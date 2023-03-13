import sys
import os
from logging import (DEBUG, INFO, NOTSET, FileHandler, Formatter, StreamHandler, basicConfig, getLogger)
from datetime import datetime
import configparser
import discord
from discord.ext import commands

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
    COMMAND_PREFIX = config["DEFAULT"]["COMMAND_PREFIX"]


except:
    logger.exception("Not Found file : config.ini")
    sys.exit()


intents = discord.Intents.default() 
client = discord.Client(command_prefix=COMMAND_PREFIX, intents=intents)

@client.event
async def on_ready():
    logger.info("Kazekoshi v2.0 on ready")

@client.command()
async def help(ctx):
    logger.info("requested command : help")


@client.command()
async def r(ctx):
    logger.info("requested command : read")

    if ctx.author.voice is None:
        await ctx.channel.send("あなたはボイスチャンネルに接続していません")
        logger.info(f"{ctx.author} is not connect voicechannel")
        return
    


client.run(DISCORD_TOKEN)
