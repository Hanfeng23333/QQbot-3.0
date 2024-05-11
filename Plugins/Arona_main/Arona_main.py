from threading import Event
from Plugins.Plugin_template import Base_plugin
from Libs.Tool_lib import *

class Arona_main(Base_plugin):
    def __init__(self):
        Base_plugin.__init__(self)
        self.event_types = ["command","nudge"]
        self.key_words = []
        self.update_internal = 0

    async def reply(self, event_type: str, key_word: str = "", *args, **info) -> None:
        pass

    def update(self, stop_event: Event) -> None:
        pass

    def help(self) -> dict:
        pass