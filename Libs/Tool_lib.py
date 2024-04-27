#Made by Han_feng
import os

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
    def message_image_path(path:str,is_emoji:bool=False) -> dict:
        """
        Make a message that contains a image

        Param:

        path(str) -> the path of the image(Relative to the work path)(use '/')

        is_emoji(bool) -> whether the image is a emoji
        """
        return {"type":"Image","path":"%s/%s"%(Message_maker.work_folder_name,path),"isEmoji":is_emoji}
    
    @staticmethod
    def message_image_url(url:str,is_emoji:bool=False) -> dict:
        """
        Make a message that contains a image

        Param:

        url(str) -> the url of the image

        is_emoji(bool) -> whether the image is a emoji
        """
        return {"type":"Image","url":url,"isEmoji":is_emoji}
    
    @staticmethod
    def message_image_base64(base64_str:str,is_emoji:bool=False) -> dict:
        """
        Make a message that contains a image

        Param:

        base64_str(str) -> the base64 of the image

        is_emoji(bool) -> whether the image is a emoji
        """
        return {"type":"Image","base64":base64_str,"isEmoji":is_emoji}
    
class Message:
    """
    A class for storing the message chain.

    Sending message will use the message chain.
    """
    def __init__(self,target:int):
        """
        Initialize the message chain

        Params:

        target(int) -> the target where sends the message chain to(friend or group)
        """
        self.target = target
        self.message_chain = []

    def push(self,message:dict) -> None:
        """
        push a message to the message chain

        Param:

        message(dict) -> the message you want to push(Use the Message_maker to create a message)
        """
        self.message_chain.append(message)

    def to_dict(self,session_key:str) -> dict:
        """
        Return the standard mirai message chain json

        No param
        """
        return {"sessionKey":session_key,"target":self.target,"messageChain":self.message_chain}