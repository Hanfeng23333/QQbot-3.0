#Made by Han_feng
import os,functools
from enum import Flag,auto
from typing import Tuple,List

def check_command(text:str) -> Tuple[str,List[str]] | None:
    if not text or text[0] != "/":
        return None
    command_list = text.split(" ")
    return (command_list.pop(0)[1:],list(filter(None,command_list)))

class Message_type(Flag):
    BROADCAST = auto() #Send the message to all the white groups, and the target qq will be ignored
    GROUP_MESSAGE = auto()
    PERSONAL_MESSAGE = auto()

class Event_type(Flag):
    TEXT = auto()
    COMMAND = auto()
    NUDGE = auto()

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
    def __init__(self,message_type:Message_type=Message_type.GROUP_MESSAGE,target:int=0):
        """
        Initialize the message chain

        Params:

        message_type(Message_type) -> the type of the message

        target(int) -> the target where sends the message chain to(friend or group)
        """
        self.message_type = message_type
        self.target = target
        self.message_chain = []
        self.quote = 0

    def push(self,message:dict) -> None:
        """
        push a message to the message chain

        Param:

        message(dict) -> the message you want to push(Use the Message_maker to create a message)
        """
        if isinstance(message,dict):
            self.message_chain.append(message)
        else:
            raise ValueError("Invaild message!")

    def pop(self,index:int=-1) -> dict:
        """
        push a message to the message chain

        Param:

        index(int) -> the index of the message in the message chain
        """
        return self.message_chain.pop(index)
    
    def quote_message(self,message_id:int) -> None:
        """
        Make the message that quotes the certain message through the message id

        Param:

        message_id(int) -> the id of the message
        """
        if isinstance(message_id,int):
            self.quote = message_id
        else:
            raise ValueError("Invaild message id!")

    @functools.singledispatchmethod
    def to_dict(self,session_key:str) -> dict:
        return {"sessionKey":session_key,"target":self.target,"messageChain":self.message_chain,**({"quote":self.quote} if self.quote else {})}
    
    @to_dict.register
    def to_dict_by_target(self,target:int,session_key:str) -> dict:
        return {"sessionKey":session_key,"target":target,"messageChain":self.message_chain,**({"quote":self.quote} if self.quote else {})}