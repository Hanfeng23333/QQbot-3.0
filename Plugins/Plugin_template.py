#Made by Han_feng
#All the plugins must be derived from the Base_plugin class, or the plugins that don't meet the requirement will be not allowed to be loaded!
#Only the update, the reply functions will be called in main thread, but you can make up other functions... Use them in those two functions!!!
from Libs.Tool_lib import *
import asyncio,httpx

class Base_plugin:
    def __init__(self):
        self.name = type(self).__name__
        self.data_path = "Plugins/Plugins_data/%s/"%self.name #You must use this data path to store your data or file, or they won't save correctly
        self.plugin_lock = False
        self.event_types = [] #choose which kinds of event to receive
        self.key_words = [] #Fill the list of the key words, as only the matched functions will call the reply function when the event type is "command"
        self.push_message:function[Message] = None
        self.get_plugin:function[str] = None
        self.async_client:httpx.AsyncClient = None

    async def reply(self,event_type:str,key_word:str="",*args,**info) -> None:
        """
        Overwrite this reply function for calling your functions to reply the users.

        Use the push_massage function to push the message into the message queue

        Use the get_plugin function to interact with other plugins

        DON'T MODIFY THE PARAMS, OR YOUR PLUGIN WILL BE UNABLE TO USE!!!

        Params:

        event_type(str) -> the type of the event

        key_word(str) -> the key word that calls this plugin

        args(list) -> the parameters that follow the key word

        info(dict) -> the information of the message {"sender":qq(int),"group":qq(int)}
        """

    def update(self) -> None:
        """
        Overwrite this update function for updating some data.

        The update function will be called at the start of the main loop and every 30 minutes after that, so you can implement a timer(a multiple of 0.5 hours) to update

        The plugin will be removed if it can't finish its update until the next update(I don't believe that the plugin can't finish the update in 30min, so there must be some errors)

        Use the push_massage function to push the message into the message queue

        Use the get_plugin function to interact with other plugins

        Set the plugin_lock to prevent some strange error if necessary

        DON'T MODIFY THE PARAMS, OR YOUR PLUGIN WILL BE UNABLE TO USE!!!
        """

    def help(self) -> dict:
        """
        Return the help documentation for your plugin

        Format(keys must be str and values can either be str or nested dict(keys must be str,too)):
        {function_name:introduction,function_name:{arg1:introduction,arg2:introduction...}...}
        """
        return {}

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self,other) -> bool:
        if isinstance(other,str):
            return self.name == other
        elif isinstance(other,Base_plugin):
            return self.name == other.name
        return False