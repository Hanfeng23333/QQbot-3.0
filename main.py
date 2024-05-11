#Made by Han_feng
import asyncio
from Libs.Bot_lib import *
from Libs.Tool_lib import *

print(Message_maker.work_folder_name)
qqbot = QQbot("1234567890",3644260939,3065613494,"http://localhost:8080",114514)

asyncio.run(qqbot.main())