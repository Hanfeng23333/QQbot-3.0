#Made by Han_feng
import httpx
from Plugins.Plugin_template import Base_plugin
from Tool_lib import *
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,Future
from concurrent.futures import TimeoutError,CancelledError

class QQbot:
    def __init__(self,verify_key:str,qq:int,master_qq:int,url:str):
        #Base attributes
        self.verify_key = verify_key
        self.qq = qq
        self.master_qq = master_qq
        self.url = url
        self.session_key = ""
        self.whitegroups:list[int] = []

        #Plugins managements
        self.plugins:list[Base_plugin] = []
        self.update_futures:dict[Base_plugin,Future] = {}
        self.update_thread_pool = ThreadPoolExecutor(max_workers=5)

        #Event managements
        self.receive_event_queue:list[dict] = []
        self.handle_event_process_pool = ProcessPoolExecutor(max_workers=3)

        #Sending messages managements
        self.send_message_queue:list[Message] = []
        self.send_thread_pool = ThreadPoolExecutor(max_workers=5)

    def login(self) -> None:
        #Verify the identity
        verify_result = httpx.post(self.url+"/verify",json={"verifyKey":self.verify_key})
        verify_result_json = verify_result.json()
        if(verify_result_json["code"] != 0):
            raise ValueError("Verify failed! Please check the verify key!")
        self.session_key = verify_result_json["session"]

        #Bind the qq number of the bot
        bind_result = httpx.post(self.url+"/bind",json={"sessionKey":self.session_key,"qq":self.qq})
        bind_result_json = bind_result.json()
        if(bind_result_json["code"] != 0):
            raise ConnectionError("Bind failed! Please check the Internet or the session key!")
        
        print("QQ bot has been signed in!")

    def load_plugin(self,plugin:Base_plugin) -> None:
        if(isinstance(plugin,Base_plugin)): #Check the plugin whether is deride the Base_plugin
            #Closure function
            def push_message(message:Message):
                message.push("\n—— by %s Plugin"%type(plugin).__name__)
                self.send_message_queue.append(message)
            
            plugin.push_message = push_message
            self.plugins.append(plugin)
            print("%s plugin is loaded successfully!"%type(plugin).__name__)
        else:
            print("%s plugin is loaded failed!"%type(plugin).__name__)

    def remove_plugin(self,plugin:Base_plugin,message:str=""):
        error_text = Message_maker.message_text(message)
        remove_text = Message_maker.message_text("%s Plugin has been removed!",type(plugin).__name__)
        for target in self.whitegroups:
            error_message = Message(target)
            error_message.push(error_text)
            error_message.push(remove_text)
            self.send_message_queue.append(error_message)
        self.plugins.remove(plugin)

    def update(self):
        #Update all the plugins

        #Remove those plugins that update timeout
        for plugin in tuple(self.update_futures.keys()):
            if not self.update_futures[plugin].done():
                self.update_futures.pop(plugin)
                self.remove_plugin(plugin,"%s plugin updates timed out!\n"%type(plugin).__name__)

        #Make a clousure function
        def plugin_update(plugin:Base_plugin):
            plugin.is_update = True
            plugin.update()
            plugin.is_update = False

        #Create the futures
        for plugin in self.plugins:
            self.update_futures[plugin] = self.update_thread_pool.submit(plugin_update,plugin)

        
    def update_check(self):
        #Catch the errors
        for plugin in self.update_futures:
            if self.update_futures[plugin].running():
                continue
            try:
                exception = self.update_futures[plugin].exception()
                if exception:
                    #The update function of the plugin raises an error, so we will remove the plugin...
                    self.remove_plugin(plugin,"%s plugin failed to update!\n%s:%s\n"%(type(plugin).__name__,type(exception).__name__,str(exception)))
            except TimeoutError:
                pass
            except CancelledError:
                pass
            finally:
                self.update_futures.pop(plugin)

    def fetch_events(self):
        received_events_result = httpx.get(self.url+"/fetchMessage",params={"sessionKey":self.session_key,"count":20})
        self.receive_event_queue.extend(received_events_result.json()["data"])