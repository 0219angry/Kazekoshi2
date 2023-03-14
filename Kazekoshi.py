import sys
import os
from logging import (DEBUG, INFO, NOTSET, FileHandler, Formatter, StreamHandler, basicConfig, getLogger)
from datetime import datetime
import configparser
import discord
from discord.ext import commands



# create dir
if not os.path.exists("log"):
    os.makedirs("log")

if not os.path.exists("temp"):
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


intents = discord.Intents.all() 
client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

@client.event
async def on_ready():
    logger.info("Kazekoshi v2.0 on ready")

@client.command()
async def help(ctx: commands.Context):
    logger.info("requested command : help")


@client.command()
async def c(ctx: commands.Context):
    logger.info("requested command : connect")

    if ctx.author.voice is None:
        await ctx.channel.send("あなたはボイスチャンネルに接続していません")
        logger.info(f"{ctx.author} is not connected voice channel")
        return
    
    global connected_channel

    async def connect(ctx: commands.Context):
        con_embed = discord.Embed(title="読み上げ開始")
        con_embed.add_field(name="読み上げテキストチャンネル", value=f"{ctx.channel.name}", inline="false")
        con_embed.add_field(name="読み上げボイスチャンネル", value=f"{ctx.author.voice.channel.name}",inline="false")
        await ctx.channel.send(embed=con_embed)

        await ctx.author.voice.channel.connect()

        connected_channel = ctx.author.voice.channel

        logger.info(f"Start reading {ctx.channel.name} at {ctx.author.voice.channel.name}")
    
    if ctx.guild.voice_client is not None:
        await ctx.guild.voice_client.disconnect()
    
    await connect(ctx)
    return



client.run(DISCORD_TOKEN)
