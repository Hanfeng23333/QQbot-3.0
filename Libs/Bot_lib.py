#Made by Han_feng
import httpx,asyncio
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
        self.whitegroups:list[int] = []

        #Plugins management
        self.plugins:list[Base_plugin] = []
        self.plugin_client = httpx.AsyncClient()

        #Event management
        self.receive_event_queue:list[dict] = []

        #Message management
        self.send_message_queue:list[Message] = []
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

    def load_plugin(self,plugin:Base_plugin) -> None:
        if(isinstance(plugin,Base_plugin)): #Check the plugin whether is deride the Base_plugin
            #Closure function
            def push_message(message:Message):
                if isinstance(message,Message):
                    message.push("\n—— by %s Plugin"%plugin.name)
                    self.send_message_queue.append(message)
            
            plugin.push_message = push_message
            plugin.get_plugin = self.get_plugin
            plugin.async_client = self.plugin_client

            self.plugins.append(plugin)
            print("%s plugin is loaded successfully!"%plugin.name)
        else:
            print("%s plugin is loaded failed!"%plugin.name)

    def remove_plugin(self,plugin:Base_plugin,message:str="",exception:BaseException=None) -> None:
        message_text = Message_maker.message_text(message)
        exception_text = Message_maker.message_text("%s: %s\n"%(type(exception).__name__,str(exception)) if exception else "")
        remove_text = Message_maker.message_text("%s Plugin has been removed!",plugin.name)
        for target in self.whitegroups:
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

    async def fetch_events(self):
        received_events_result = await self.massage_client.get(self.url+"/fetchMessage",params={"sessionKey":self.session_key,"count":20})
        self.receive_event_queue.extend(received_events_result.json()["data"])

    async def update_plugins(self):
        while True:
            update_tasks:dict[Base_plugin,asyncio.Task] = dict(map(lambda plugin:(plugin,asyncio.create_task(asyncio.to_thread(plugin.update))),self.plugins))
            await asyncio.sleep(1800)

            for plugin in update_tasks:
                if update_tasks[plugin].done():
                    exception = update_tasks[plugin].exception()
                    if exception:
                        self.remove_plugin(plugin,exception)
                else:
                    self.remove_plugin(plugin,TimeoutError("update timed out!"))
    
    async def main(self):
        pass