#Made by Han_feng
#All the plugins must be derived from the Base_plugin class, or the plugins that don't meet the requirement will be not allowed to be loaded!
#Only the update, the reply functions will be called in main thread, but you can make up other functions... Use them in those two functions!!!
from Libs.Tool_lib import *

class Base_plugin:
    def __init__(self):
        self.key_words = [] #Fill the list of the key words, as only the matched functions will call the reply function
        self.name = type(self).__name__
        self.data_path = "Plugins/Plugins_data/"+self.name+"/" #You must use this data path to store your data or file, or they won't save correctly
        self.is_update = False
        self.push_message:function[Message] = None
        self.get_plugin:function[Base_plugin] = None

    def reply(self,key_word:str,*args,**info) -> None:
        """
        Overwrite this reply function for calling your functions to reply the users.

        Use the push_massage function to push the message into the message queue

        Use the get_plugin function to interact with other plugins

        DON'T MODIFY THE PARAMS, OR YOUR PLUGIN WILL BE UNABLE TO USE!!!

        Params:

        key_word(str) -> the key word that calls this plugin

        args(list) -> the parameters that follow the key word

        info(dict) -> the information of the message
        """

    def update(self) -> None:
        """
        Overwrite this update function for updating some data.

        The update function will be called at the start of the main loop and every 30 minutes after that, so you can implement a timer(a multiple of 0.5 hours) to update

        The plugin will be removed if it can't finish its update until the next update(I don't believe that the plugin can't finish the update in 30min, so there must be some errors)

        Use the push_massage function to push the message into the message queue

        Use the get_plugin function to interact with other plugins

        DON'T MODIFY THE PARAMS, OR YOUR PLUGIN WILL BE UNABLE TO USE!!!
        """

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self,other):
        return isinstance(other,Base_plugin) and self.name == other.name