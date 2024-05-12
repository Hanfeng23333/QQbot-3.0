from threading import Event
from Plugins.Plugin_template import Base_plugin
from Libs.Tool_lib import *
from Libs.Bot_lib import *
import ujson,copy

class Arona_main(Base_plugin):
    def __init__(self):
        Base_plugin.__init__(self)
        self.event_types = [Event_type.COMMAND,Event_type.NUDGE]
        self.key_words = ["帮助","插件"]
        self.update_internal = 600

        self.bot:QQbot = None
        self.empty_user = {"credit":0,"stone":0}
        self.users = {}

    async def reply(self, event_type: Event_type, key_word: str = "", *args, **info) -> None:
        if not info["sender"] in self.users:
            self.users[info["sender"]] = copy.deepcopy(self.empty_user)
        match event_type:
            case Event_type.COMMAND:
                match key_word:
                    case "帮助":
                        message = Message(target=info["group"])
                        match args:
                            case []:
                                message.push(Message_maker.message_text("\n".join(map(lambda plugin:"%s Plugin:\n%s"%(plugin,self.formatted_nested_dict(plugin.help())),self.bot.plugins))))
                            case [str() as plugin_name]:
                                plugin = self.get_plugin(plugin_name)
                                message.push(Message_maker.message_text("%s Plugin:\n%s"%(plugin,self.formatted_nested_dict(plugin.help())) if plugin else "老师,什庭之匣未安装%s插件..."%plugin_name))
                            case [*attrs]:
                                message.push("老师,你传入了无效的参数:%s"%attrs)
                        self.push_message(message)
                    case "插件":
                        message = Message(target=info["group"])
                        match args:
                            case []:
                                message.push(Message_maker.message_text("老师,目前什庭之匣已安装的插件有:\n"+"\n".join(map(lambda plugin:str(plugin),self.bot.plugins))))
                            case [*attrs]:
                                message.push("老师,你传入了无效的参数:%s"%attrs)
                        self.push_message(message)
                            

    def update(self, stop_event: Event) -> None:
        if not self.bot:
            self.bot = self.get_plugin(114514)
        if self.users:
            with open(self.data_path+"users.json","w",encoding="UTF-8") as file:
                ujson.dump(self.users,file)
        else:
            try:
                with open(self.data_path+"users.json","r",encoding="UTF-8") as file:
                    data = ujson.load(file)
                    for key in data:
                        self.users[key] = copy.deepcopy(self.empty_user)
                        self.users[key].update(data[key])
            except FileNotFoundError:
                with open(self.data_path+"users.json","w",encoding="UTF-8") as file:
                    ujson.dump(self.users,file)

    def help(self) -> dict:
        return {
            "帮助":{
                "<无参数>":"查询所有插件的帮助文档",
                "[插件名称]":"查询特定插件的帮助文档"
            },
            "插件":"查询目前已安装的插件"
        }
    
    def formatted_nested_dict(self,dictionary:dict,indent=0) -> str:
        lines = []
        for key,value in dictionary.items():
            key_string = " "*2*indent + str(key) + ":"
            if isinstance(value,dict):
                lines.append(key_string)
                lines.append(self.formatted_nested_dict(value,indent+1))
            else:
                lines.append(key_string + " " + str(value))
        return "\n".join(lines)