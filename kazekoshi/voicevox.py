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

logger = getLogger(__name__)

class VoiceVox:
    def __init__(self):
        self.MAX_WAV_FILE = 10
        try:
            config = configparser.ConfigParser()
            config.read("config.ini", encoding="UTF-8")


            self.SPEAKER_ID = int(config["DEFAULT"]["SPEAKER_ID"])
            self.OPEN_JTALK_DICT_DIR = config["DEFAULT"]["OPEN_JTALK_DICT_DIR"]

        except:
            logger.exception("Not Found file : config.ini")
            sys.exit()
        
        self.core = VoicevoxCore(open_jtalk_dict_dir=Path(self.OPEN_JTALK_DICT_DIR))
        self.queue_dict = defaultdict(deque)


    # VOICEVOX function difinition
    def create_voice(self, msg: discord.Message, speaker_id: int, voice_client: discord.VoiceClient):
        msg_text = msg.content
        wavfilename = f"./temp/{datetime.now():%Y-%m-%d_%H%M%S}.wav"
        if not self.core.is_model_loaded(speaker_id):
            self.core.load_model(speaker_id)
        wave_bytes = self.core.tts(msg_text, speaker_id)
        
        with open(wavfilename,"wb") as f:
            f.write(wave_bytes)
        
        self.enqueue(voice_client, msg.guild, discord.FFmpegPCMAudio(wavfilename))
        logger.info(f"メッセージ[{msg_text}]の読み上げ完了")
        
        wavlist = glob.glob("./temp/*.wav")
        wavlist.sort(reverse=False)
        if len(wavlist) > self.MAX_WAV_FILE:
            for i in range(len(wavlist)-self.MAX_WAV_FILE):
                os.remove(wavlist[i])
        return


    def enqueue(self, voice_client: discord.VoiceClient, guild: discord.Guild, source: discord.FFmpegPCMAudio):
        queue = self.queue_dict[guild.id]
        queue.append(source)
        if not voice_client.is_playing():
            self.play(voice_client, queue)

    def play(self, voice_client: discord.VoiceClient, queue: defaultdict):
        if not queue or voice_client.is_playing():
          return
        source = queue.popleft()
        voice_client.play(source, after=lambda e:self.play(voice_client, queue))
