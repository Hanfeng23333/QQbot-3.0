#Made by Han_feng
import importlib.util
import httpx,asyncio,threading,os,importlib,functools
from Plugins.Plugin_template import Base_plugin
from .Tool_lib import *
from typing import Self

class QQbot:
    def __init__(self,verify_key:str,qq:int,master_qq:int,url:str,manager_password:int):
        #Base attributes
        self.verify_key = verify_key
        self.qq = qq
        self.master_qq = master_qq
        self.url = url
        self.manager_password = manager_password
        self.session_key = ""
        self.white_groups:list[int] = list()

        #Plugins management
        self.plugins:list[Base_plugin] = list()
        self.plugin_client = httpx.AsyncClient()
        self.update_plugin_tasks:dict[Base_plugin,list[asyncio.Task,asyncio.Task,threading.Event]] = dict()

        #Event management
        self.receive_event_queue:list[dict] = list()

        #Message management
        self.send_message_queue:list[Message] = list()
        self.send_message_tasks = set()
        self.message_client = httpx.AsyncClient()

    async def login(self) -> None:
        #Verify the identity
        verify_result = await self.message_client.post(self.url+"/verify",json={"verifyKey":self.verify_key})
        verify_result_json = verify_result.json()
        if verify_result_json["code"] != 0:
            raise ValueError("Verify failed! Please check the verify key!")
        self.session_key = verify_result_json["session"]

        #Bind the qq number of the bot
        bind_result = await self.message_client.post(self.url+"/bind",json={"sessionKey":self.session_key,"qq":self.qq})
        bind_result_json = bind_result.json()
        if bind_result_json["code"] != 0:
            raise ConnectionError("Bind failed! Please check the session key!")
        
        print("QQ bot has been signed in!")

    def find_plugin(self,plugin_name:str) -> type[Base_plugin] | None:
        if spec := importlib.util.find_spec("."+plugin_name,"Plugins."+plugin_name):
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            return getattr(plugin_module,plugin_name,None)
        return None

    def load_plugin(self,plugin:Base_plugin) -> bool:
        if isinstance(plugin,Base_plugin): #Check the plugin whether is deride the Base_plugin
            #Closure function
            def push_message(message:Message):
                if isinstance(message,Message):
                    message.push("\n—— by %s Plugin"%plugin)
                    self.send_message_queue.append(message)
            
            plugin.push_message = push_message
            plugin.get_plugin = self.get_plugin
            plugin.async_client = self.plugin_client

            self.plugins.append(plugin)
            if plugin.update_internal > 0:
                self.update_plugin(plugin)
            elif plugin.update_internal == 0:
                self.update_once_plugin(plugin)
            print("%s plugin is loaded successfully!"%plugin)
            return True
        print("%s plugin is loaded failed!"%plugin)
        return False

    def update_plugin(self,plugin:Base_plugin) -> None:
        #set the timer task
        timer_task = asyncio.create_task(asyncio.sleep(plugin.update_internal))
        timer_task.set_name(plugin)
        timer_task.add_done_callback(self.check_timer)
        self.update_plugin_tasks[plugin][0] = timer_task

        #set the update task
        stop_event = threading.Event()
        update_task = asyncio.create_task(asyncio.to_thread(plugin.update,stop_event))
        update_task.set_name(plugin)
        update_task.add_done_callback(self.check_update)
        self.update_plugin_tasks[plugin][1] = update_task
        self.update_plugin_tasks[plugin][2] = stop_event

    def update_once_plugin(self,plugin:Base_plugin) -> None:
        #Only the update task
        update_once_task = asyncio.create_task(asyncio.to_thread(plugin.update))
        update_once_task.set_name(plugin)
        update_once_task.add_done_callback(self.check_once_update)
        self.update_plugin_tasks[plugin] = update_once_task

    def remove_plugin(self,plugin:Base_plugin|str,message:str="",exception:Exception=None) -> None:
        if plugin in self.plugins:
            error_message = Message(Message_type.BROADCAST)
            error_message.push(Message_maker.message_text(message))
            error_message.push(Message_maker.message_text("%s: %s\n"%(exception.__class__.__name__,exception) if exception else ""))
            error_message.push(Message_maker.message_text("%s Plugin has been removed!"%plugin))
            self.send_message_queue.append(error_message)
            self.plugins.remove(plugin)

    @functools.singledispatchmethod
    def get_plugin(self,plugin_name) -> None:
        #Callback function for plugins
        return None
    
    @get_plugin.register
    def get_plugin_by_name(self,plugin_name:str) -> Base_plugin | None:
        #get the plugin by name
        try:
            return self.plugins[self.plugins.index(plugin_name)]
        except ValueError:
            return None
        
    @get_plugin.register 
    def get_self(self,manager_password:int) -> Self | None:
        #get the plugin list if it's the manager plugin
        return self if manager_password == self.manager_password else None

    def check_timer(self,task:asyncio.Task) -> None:
        plugin_name = task.get_name()
        match task.exception():
            case None:
                if self.update_plugin_tasks[plugin_name][1].done():
                    self.update_plugin(self.get_plugin(plugin_name))
                else:
                    self.remove_plugin(plugin_name,exception=TimeoutError("The update of %s plugin timed out!"))
                    self.update_plugin_tasks[plugin_name][1].cancel()
                    self.update_plugin_tasks.pop(plugin_name)
            case asyncio.CancelledError():
                if not self.update_plugin_tasks[plugin_name][1].done():
                    self.update_plugin_tasks[plugin_name][1].cancel()
                    self.update_plugin_tasks[plugin_name][2].set()
                self.update_plugin(self.get_plugin(plugin_name))
            
    def check_update(self,task:asyncio.Task) -> None:
        match task.exception():
            case None | asyncio.CancelledError():
                pass
            case TimeoutError():
                timeout_message = Message(Message_type.BROADCAST)
                timeout_message.push(Message_maker.message_text("%s plugin failed to update!"%task.get_name()))
                self.send_message_queue.append(timeout_message)
            case exception:
                plugin_name = task.get_name()
                self.remove_plugin(plugin_name,exception=exception)
                self.update_plugin_tasks[plugin_name][0].remove_done_callback(self.check_timer)
                self.update_plugin_tasks[plugin_name][0].cancel()
                self.update_plugin_tasks.pop(plugin_name)

    def check_once_update(self,task:asyncio.Task) -> None:
        exception,plugin_name = task.exception(),task.get_name()
        if exception:
            self.remove_plugin(plugin_name,exception=exception)
        self.update_plugin_tasks.pop(plugin_name)

    async def fetch_events(self) -> None:
        received_events_result = await self.message_client.get(self.url+"/fetchMessage",params={"sessionKey":self.session_key,"count":20})
        for event in received_events_result.json()["data"]:
            event_dict:dict = {"event_type":"","key_word":"","args":[],"info":{"sender":0,"group":0}}
            is_valid:bool = False

            #handle the event
            match event["type"]:
                case "GroupMessage" if event["sender"]["group"] in self.white_groups:
                    #Group message
                    event_dict["info"]["sender"] = event["sender"]["id"]
                    event_dict["info"]["group"] = event["sender"]["group"]["id"]
                    is_valid = True

                    match event["messageChain"]:
                        case [dict() as text_dict] if text_dict["type"] == "Plain":
                            if command_tuple:= check_command(text_dict["text"].strip()):
                                event_dict["event_type"] = Event_type.COMMAND
                                event_dict["key_word"],event_dict["args"] = command_tuple
                            else:
                                event_dict["event_type"] = Event_type.TEXT
                                event_dict["key_word"] = text_dict["text"]
                        case [dict() as at_dict,dict() as text_dict] if at_dict["type"] == "At" and at_dict["target"] == self.qq and text_dict["type"] == "Plain":
                            event_dict["event_type"] = Event_type.COMMAND
                            text_segments:list[str] = list(filter(None,text_dict["text"].strip()))
                            is_valid = bool(text_segments)
                            if is_valid:
                                text_segments[0] = text_segments[0][1:] if text_segments[0].startswith("/") else text_segments[0]
                                event_dict["key_word"],event_dict["args"] = text_segments.pop(0),text_segments
                        case [*args]:
                            event_dict["event_type"] = Event_type.COMMAND
                            event_dict["args"] = list(map(lambda d:d["text"],filter(lambda d:d["type"]=="Plain",args)))
                
                case "NudgeEvent" if event["target"] == self.qq:
                    #Nudge event
                    event_dict["event_type"] == Event_type.NUDGE
                    event_dict["info"]["sender"] = event["fromID"]
                    if event["subject"]["kind"] == "Group":
                        event_dict["info"]["group"] = event["subject"]["id"]
                        is_valid = event["subject"]["id"] in self.white_groups
            
            #push the event to the queue
            if is_valid:
                self.receive_event_queue.append(event_dict)

    def handle_events(self) -> None:
        while self.receive_event_queue:
            event_dict = self.receive_event_queue.pop(0)
            for plugin in self.plugins:
                is_valid = False
                if event_dict["event_type"] in plugin.event_types:
                    match event_dict["event_type"]:
                        case Event_type.COMMAND:
                            is_valid = event_dict["key_word"] in plugin.key_words
                        case Event_type.TEXT | Event_type.NUDGE:
                            is_valid = True
                
                if is_valid:
                    reply_task = asyncio.create_task(plugin.reply(event_dict["event_type"],event_dict["key_word"],*event_dict["args"],**event_dict["info"]))
                    reply_task.add_done_callback(self.send_message_tasks.discard)
                    self.send_message_tasks.add(reply_task)

    async def send_single_message(self,message:Message) -> None:
        match message.message_type:
            case Message_type.BROADCAST:
                await asyncio.gather(*map(lambda group:self.message_client.post(self.url+"/sendGroupMessage",json=message.to_dict(group,self.session_key)),self.white_groups))
            case Message_type.GROUP_MESSAGE:
                await self.message_client.post(self.url+"/sendGroupMessage",json=message.to_dict(self.session_key))

    def send_messages(self):
        while self.send_message_queue:
            send_task = asyncio.create_task(self.send_single_message(self.send_message_queue.pop(0)))
            send_task.add_done_callback(self.send_message_tasks.discard)
            self.send_message_tasks.add(send_task)
    
    async def main(self) -> None:
        await self.login()
        
        plugin_list = os.listdir("Plugins")
        plugin_list.remove("Plugins_data")
        plugin_list.remove("Plugin_template.py")
        plugin_list.remove("__pycache__")
        plugin_list.remove("__init__.py")

        for plugin_class in filter(None,map(self.find_plugin,plugin_list)):
            #print(plugin_class())
            self.load_plugin(plugin_class())

        while True:
            await self.fetch_events()
            self.handle_events()
            self.send_messages()
            await asyncio.sleep(0.1)