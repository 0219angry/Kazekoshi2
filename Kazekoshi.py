import sys
import os
import glob
import wave
import asyncio
from collections import defaultdict, deque
from logging import (DEBUG, INFO, NOTSET, FileHandler, Formatter, StreamHandler, basicConfig, getLogger)
from datetime import datetime
import configparser

# Discord.py
import discord
from discord.ext import commands


# VOICEVOX
from pathlib import Path
from voicevox_core import VoicevoxCore

# my module
import kazekoshi.global_val as g
from kazekoshi import voicevox

MAX_LOG_FILE = 5
MAX_WAV_FILE = 10

# create dir
if not os.path.exists("log"):
    os.makedirs("log")

if not os.path.exists("temp"):
    os.makedirs("temp")


loglist = glob.glob("./log/*.log")

loglist.sort(reverse=False)
if len(loglist) > MAX_LOG_FILE:
    for i in range(len(loglist)-MAX_LOG_FILE):
        os.remove(loglist[i])

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
    SPEAKER_ID = int(config["DEFAULT"]["SPEAKER_ID"])
    OPEN_JTALK_DICT_DIR = config["DEFAULT"]["OPEN_JTALK_DICT_DIR"]

except:
    logger.exception("Not Found file : config.ini")
    sys.exit()

intents = discord.Intents.all() 
client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)
connected_channel = {}
core = VoicevoxCore(open_jtalk_dict_dir=Path(OPEN_JTALK_DICT_DIR))
queue_dict = defaultdict(deque)

vv = voicevox.VoiceVox()


@client.event
async def on_ready():
    logger.info("Kazekoshi v2.0 on ready")

@client.command()
async def help(ctx: commands.Context):
    logger.info("requested command : help")


@client.command()
async def c(ctx: commands.Context, *args):
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

        connected_channel[ctx.guild] = ctx.channel

        logger.info(f"Start reading {ctx.channel.name} at {ctx.author.voice.channel.name}")
    
    if ctx.guild.voice_client is not None:
        await ctx.guild.voice_client.disconnect()
    
    await connect(ctx)
    return

@client.command()
async def dc(ctx: commands.Context):
    logger.info("requested command : disconnect")
    await ctx.guild.voice_client.disconnect()
    discon_embed = discord.Embed(title="読み上げ終了")
    await ctx.channel.send(embed=discon_embed)
    connected_channel.pop(ctx.guild)
    return
    
@client.event
async def on_message(message: discord.Message):
    # COMMAND_PREFIXで始まるMessageはコマンドとして扱う
    if message.content.startswith(COMMAND_PREFIX):
        await client.process_commands(message)
        return
    
    if message.author.bot:
        return
    
    if message.channel in connected_channel.values() and message.guild.voice_client is not None:
        vv.create_voice(message, SPEAKER_ID, message.guild.voice_client)


    return

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    
    # 読み上げ中に対象ボイスチャンネルから人がいなくなった時読み上げ終了する
    if (member.guild.voice_client is not None and member.id != client.user.id and member.guild.voice_client.channel is before.channel and len(member.guild.voice_client.channel.members) == 1):
        await member.guild.voice_client.disconnect()
        discon_embed = discord.Embed(title="読み上げ終了", description="誰もいなくなったので読み上げを終了しました")
        await connected_channel[member.guild].send(embed=discon_embed)
        logger.info(f"auto disconnected from {before.channel}")
        connected_channel.pop(member.guild)
    return
    
try:
    client.run(DISCORD_TOKEN)
except:
    logger.exception("Discord API key error")
    sys.exit()