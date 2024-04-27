#Made by Han_feng
import httpx
from Plugins.Plugin_template import Base_plugin
from Tool_lib import *
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,Future
from concurrent.futures import TimeoutError,CancelledError
from typing import List

class QQbot:
    def __init__(self,verify_key:str,qq:int,master_qq:int,url:str):
        self.verify_key = verify_key
        self.qq = qq
        self.master_qq = master_qq
        self.url = url
        self.session_key = ""
        self.plugins:List[Base_plugin] = []
        self.update_futures:List[Future] = []
        self.whitegroups:List[int] = []
        self.send_message_queue:List[Message] = []

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
            self.plugins.append(plugin)
            print("%s plugin is loaded successfully!"%type(plugin).__name__)
        else:
            print("%s plugin is loaded failed!"%type(plugin).__name__)

    def update(self):
        #Update all the plugins

        #Try to cancel the futures left
        for future in self.update_futures:
            future.cancel()

        #Create the futures
        executor = ThreadPoolExecutor(max_workers=5)
        self.update_futures = [executor.submit(plugin.update) for plugin in self.plugins]
        executor.shutdown(False)

    def update_check(self):
        #Catch the errors
        for plugin,future in zip(self.plugins,self.update_futures):
            if future.running():
                continue

            try:
                exception = future.exception()
                if exception:
                    #The update function of the plugin raises an error, so we will remove the plugin...
                    error_text = Message_maker.message_text("%s plugin updates failed!\n%s:%s"%(type(plugin).__name__,type(exception).__name__,str(exception)))
                    for target in self.whitegroups:
                        error_message = Message(target)
                        error_message.push(error_text)
                        self.send_message_queue.append(error_message)
                    self.plugins.remove(plugin)
                else:
                    self.send_message_queue.extend(future.result())
            except TimeoutError:
                pass
            except CancelledError:
                pass
            finally:
                self.update_futures.remove(future)

    def fetch_messages(self):
        pass