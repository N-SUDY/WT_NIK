# (c) @AbirHasan2005

# Don't Forget That I Made This!
# So Give Credits!


import os
from dotenv import load_dotenv
from os.path import exists

if exists('config.env'):
  load_dotenv('config.env')


class Config(object):
    BOT_TOKEN= os.environ.get("BOT_TOKEN")
    Session_String = os.environ.get("Session_String", None)
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH")
    DOWN_PATH = os.environ.get("DOWN_PATH", "./downloads")
    PRESET = os.environ.get("PRESET", "ultrafast")
    OWNER_ID = int(os.environ.get("OWNER_ID", ''))
    GROUP_ID = int(os.environ.get("GROUP_ID", ''))
    DATABASE_URL = os.environ.get("DATABASE_URL")
    PROGRESS = """
Percentage : {0}%
Done ✅: {1}
Total 🌀: {2}
Speed 🚀: {3}/s
ETA 🕰: {4}
"""
