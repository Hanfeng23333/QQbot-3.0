#Made by Han_feng
import httpx,asyncio,functools
from Plugins.Plugin_template import Base_plugin
from Tool_lib import *

class QQbot:
    def __init__(self,verify_key:str,qq:int,master_qq:int,url:str):
        #Base attributes
        self.verify_key = verify_key
        self.qq = qq
        self.master_qq = master_qq
        self.url = url
        self.session_key = ""
        self.white_groups:list[int] = []

        #Plugins management
        self.plugins:list[Base_plugin] = []
        self.plugin_client = httpx.AsyncClient()
        self.update_plugin_tasks:dict[Base_plugin,list[asyncio.Task,asyncio.Task]] = {}

        #Event management
        self.receive_event_queue:list[dict] = []

        #Message management
        self.send_message_queue:list[Message] = []
        self.send_message_tasks = set()
        self.massage_client = httpx.AsyncClient()

    async def login(self) -> None:
        #Verify the identity
        verify_result = await self.massage_client.post(self.url+"/verify",json={"verifyKey":self.verify_key})
        verify_result_json = verify_result.json()
        if(verify_result_json["code"] != 0):
            raise ValueError("Verify failed! Please check the verify key!")
        self.session_key = verify_result_json["session"]

        #Bind the qq number of the bot
        bind_result = await self.massage_client.post(self.url+"/bind",json={"sessionKey":self.session_key,"qq":self.qq})
        bind_result_json = bind_result.json()
        if(bind_result_json["code"] != 0):
            raise ConnectionError("Bind failed! Please check the session key!")
        
        print("QQ bot has been signed in!")

    async def load_plugin(self,plugin:Base_plugin) -> None:
        if(isinstance(plugin,Base_plugin)): #Check the plugin whether is deride the Base_plugin
            #Closure function
            def push_message(message:Message):
                if isinstance(message,Message):
                    message.push("\n—— by %s Plugin"%plugin)
                    self.send_message_queue.append(message)
            
            plugin.push_message = push_message
            plugin.get_plugin = self.get_plugin
            plugin.async_client = self.plugin_client

            self.plugins.append(plugin)
            await self.update_plugin(plugin)
            print("%s plugin is loaded successfully!"%plugin)
        else:
            print("%s plugin is loaded failed!"%plugin)

    async def update_plugin(self,plugin:Base_plugin):
        #set the timer
        self.update_plugin_tasks[plugin][1] = asyncio.create_task(asyncio.sleep(1800))

        #set the update task
        update_task = asyncio.create_task(asyncio.to_thread(plugin.update))
        update_task.set_name(plugin)
        update_task.add_done_callback(functools.partial(self.check_error,functools.partial(self.update_plugin_tasks.pop,plugin)))
        self.update_plugin_tasks[plugin][0] = update_task

    def remove_plugin(self,plugin:Base_plugin|str,message:str="",exception:Exception=None) -> None:
        if plugin in self.plugins:
            message_text = Message_maker.message_text(message)
            exception_text = Message_maker.message_text("%s: %s\n"%(exception.__class__.__name__,exception) if exception else "")
            remove_text = Message_maker.message_text("%s Plugin has been removed!"%plugin)
            for target in self.white_groups:
                error_message = Message(target)
                error_message.push(message_text)
                error_message.push(exception_text)
                error_message.push(remove_text)
                self.send_message_queue.append(error_message)
            self.plugins.remove(plugin)

    def get_plugin(self,plugin_name:str) -> Base_plugin | None:
        #Callback function for plugins
        try:
            return self.plugins[self.plugins.index(plugin_name)]
        except ValueError:
            return None
        
    def check_error(self,delete_function:function,task:asyncio.Task) -> None:
        match task.exception():
            case None:
                pass
            case asyncio.CancelledError():
                pass
            case exception:
                self.remove_plugin(task.get_name(),exception=exception)
            
        delete_function()

    async def fetch_events(self) -> None:
        received_events_result = await self.massage_client.get(self.url+"/fetchMessage",params={"sessionKey":self.session_key,"count":20})
        for event in received_events_result.json()["data"]:
            event_dict:dict = {"event_type":"","key_word":"","args":[],"info":{"sender":0,"group":0}}
            is_valid:bool = False

            #handle the event
            match event["type"]:
                case "GroupMessage" if event["sender"]["group"] in self.white_groups:
                    #Group message
                    event_dict["event_type"] = "command"
                    event_dict["info"]["sender"] = event["sender"]["id"]
                    event_dict["info"]["group"] = event["sender"]["group"]

                    #search the command
                    command_symbol_count = 0 #handle the exception
                    for message in event["messageChain"]:
                        match message["type"]:
                            case "At" if message["target"] == self.qq:
                                is_valid = True
                            case "Plain":
                                text_segments = list(filter(None,message["text"]))
                                if text_segments and text_segments[0][0] == "/":
                                    command_symbol_count += 1
                                    event_dict["key_word"] = text_segments.pop(0)[1:]
                                event_dict["args"].extend(text_segments)
                    
                    #Let's see whether the command is vdlid
                    is_valid = is_valid or command_symbol_count and command_symbol_count <= 1
                
                case "NudgeEvent" if event["target"] == self.qq:
                    event_dict["info"]["sender"] = event["fromID"]
                    is_valid = True
                    if event["subject"]["kind"] == "Group":
                        event_dict["info"]["group"] = event["subject"]["id"]
                        is_valid = event["subject"]["id"] in self.white_groups
            
            #push the event to the queue
            if is_valid:
                self.receive_event_queue.append(event_dict)
    
    async def main(self) -> None:
        pass