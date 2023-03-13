import sys
import os
from logging import (DEBUG, INFO, NOTSET, FileHandler, Formatter, StreamHandler, basicConfig, getLogger)
from datetime import datetime
import configparser
import discord

# bot token
TOKEN = ""

# create dir
if not os.path.exists("log"):
    os.makedirs("log")

if not os.path.exits("temp"):
    os.makedirs("temp")

# log
format = "[%(asctime)s] %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s"

sh = StreamHandler()
sh.setLevel(INFO)
sh.setFormatter(Formatter(format))

fh = FileHandler(f"./log/{datetime.now():%Y-%m-%d_%H%M%S}.log")
fh.setLevel(DEBUG)
fh.setFormatter(Formatter(format))

basicConfig(level=NOTSET, handlers=[sh, fh])
logger = getLogger(__name__)


# read config.ini
try:
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="UTF-8")
    DISCORD_TOKEN = config["DEFAULT"]["DISCORD_TOKEN"]


except:
    logger.exception("Not Found file : config.ini")
    sys.exit()


intents = discord.Intents.default() 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info("Kazekoshi v2.0 on ready")


client.run(DISCORD_TOKEN)
