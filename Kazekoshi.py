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

except:
    logger.exception("Not Found file : config.ini")
    sys.exit()

intents = discord.Intents.all() 
client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)
connected_channel = {}
core = VoicevoxCore(open_jtalk_dict_dir=Path("../open_jtalk_dic_utf_8-1.11"))
queue_dict = defaultdict(deque)

# VOICEVOX function difinition
def create_voice(msg: discord.Message, speaker_id: int, voice_client: discord.VoiceClient):
    msg_text = msg.content
    wavfilename = f"./temp/{datetime.now():%Y-%m-%d_%H%M%S}.wav"
    if not core.is_model_loaded(speaker_id):
        core.load_model(speaker_id)
    wave_bytes = core.tts(msg_text, speaker_id)
    
    with open(wavfilename,"wb") as f:
        f.write(wave_bytes)
    
    enqueue(voice_client, msg.guild, discord.FFmpegPCMAudio(wavfilename))
    logger.info(f"メッセージ[{msg_text}]の読み上げ完了")
    
    wavlist = glob.glob("./temp/*.wav")
    wavlist.sort(reverse=False)
    if len(wavlist) > MAX_WAV_FILE:
        for i in range(len(wavlist)-MAX_WAV_FILE):
            os.remove(wavlist[i])
    return


def enqueue(voice_client: discord.VoiceClient, guild: discord.Guild, source: discord.FFmpegPCMAudio):
    queue = queue_dict[guild.id]
    queue.append(source)
    if not voice_client.is_playing():
        play(voice_client, queue)

def play(voice_client, queue):
    if not queue or voice_client.is_playing():
      return
    source = queue.popleft()
    voice_client.play(source, after=lambda e:play(voice_client, queue))



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
        create_voice(message, SPEAKER_ID, message.guild.voice_client)


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