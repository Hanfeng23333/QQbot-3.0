import os,threading,httpx

class Message_maker:
    """
    A class for making messages of the QQ bot.

    All the methods are static methods, so it's meaningless to instantiate it.

    Call the static methods only.
    """

    work_folder_name = os.path.basename(os.getcwd())

    @staticmethod
    def message_at(target:int) -> dict:
        """
        Make a message that "At" someone

        Param:

        target(int) -> The qq number of the target you want to "At"
        """
        return {"type":"At","target":target,"display":""}
    
    @staticmethod
    def message_at_all() -> dict:
        """
        Make a message that "At" everyone in the group

        No params
        """
        return {"type":"AtAll"}

    @staticmethod
    def message_text(text:str) -> dict:
        """
        Make a message that contains a string

        Param:

        text(str) -> the text you want to show
        """
        return {"type":"Plain","text":text}
    
    @staticmethod
    def message_image_path(path:str) -> dict:
        """
        Make a message that contains a image

        Param:

        path(str) -> the path of the image(Relative to the work path)(use '/')
        """
        return {"type":"Image","path":"%s/%s"%(Message_maker.work_folder_name,path)}
    
    @staticmethod
    def message_image_url(url:str) -> dict:
        """
        Make a message that contains a image

        Param:

        url(str) -> the url of the image
        """
        return {"type":"Image","url":url}
    
class Message_chain:
    """
    A class for storing the message chain.

    Sending message will use the message chain.
    """
    def __init__(self,session_key:str,target:int):
        """
        Initialize the message chain

        Params:

        session_key(str) -> the session key of the QQ bot

        target(int) -> the target where sends the message chain to(friend or group)
        """
        self.session_key = session_key
        self.target = target
        self.message_chain = []

    def push(self,message:dict) -> None:
        """
        push a message to the message chain

        Param:

        message(dict) -> the message you want to push(Use the Message_maker to create a message)
        """
        self.message_chain.append(message)

    def to_dict(self) -> dict:
        """
        Get the standard mirai message chain json

        No param
        """
        return {"sessionKey":self.session_key,"target":self.target,"messageChain":self.message_chain}
    
class Web_manager:
    """
    A class that handle the web connection

    It's used as a thread so as to get the web infomation in the background
    """
    def __init__(self,url:str):
        self.url = url
        self.header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"}
        self.thread = threading.Thread(target=self.thread_function)

    def get(self,path:str="",params:dict=None) -> httpx.Response:
        return httpx.get(self.url+path,params=params,headers=self.header)
    
    def post(self,path:str="",data=None,json:dict=None) ->httpx.Response:
        return httpx.post(self.url,data=data,json=json,headers=self.header)
    
    def thread_function(self):
        pass