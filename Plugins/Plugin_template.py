#Made by Han_feng
#All the plugins must be derived from the Base_plugin class, or the plugins that don't meet the requirement will be not allowed to be loaded!
#Only the update and the reply functions will be called in main thread, and you can make up other functions... Use them in those two functions!!!
from Libs.Tool_lib import *
from typing import List,Dict

class Base_plugin:
    def __init__(self):
        self.key_words = [] #Fill the list of the key words, as only the matched functions will call the reply function
        self.name = type(self).__name__
        self.data_path = "Plugins/Plugins_data/"+self.name+"/" #You must use this data path to store your data or file, or they won't save correctly

    def reply(self,key_word:str,*args,**kwargs) -> List[Message]:
        """
        Overwrite this reply function for calling your functions to reply the users.

        If there's no reply, then just return a empty list

        DON'T MODIFY THE PARAMS, OR YOUR PLUGIN WILL BE UNABLE TO USE!!!

        Params:

        key_word(str) -> the key word that calls this plugin

        args(list) -> the parameters that follow the key word

        kwargs(dict) -> the information of the message
        """
        return []

    def update(self) -> List[Message]:
        """
        Overwrite this update function for updating some data and sending messages proactively.

        If there's no message or just you don't need this function, then just return a empty list

        DON'T MODIFY THE PARAMS, OR YOUR PLUGIN WILL BE UNABLE TO USE!!!
        """
        return []