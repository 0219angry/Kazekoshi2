import sys
import os
import glob
import wave
import asyncio
from collections import defaultdict, deque
from logging import (DEBUG, INFO, NOTSET, FileHandler, Formatter, StreamHandler, basicConfig, getLogger)
from datetime import datetime
import configparser
import json
import re

# Discord.py
import discord
from discord.ext import commands


# VOICEVOX
from pathlib import Path
from voicevox_core import VoicevoxCore, METAS

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
        
        # voicevox_core
        self.core = VoicevoxCore(open_jtalk_dict_dir=Path(self.OPEN_JTALK_DICT_DIR)) 
        # 読み上げ中queue
        self.queue_dict = defaultdict(deque)
        # userとspeakerの辞書 {userid:speakerid}
        self.user_speaker_dict = {}
        # dictionaryの辞書
        self.word_dict = {}


    # VOICEVOX function difinition
    def create_voice(self, msg: discord.Message, speaker_id: int, voice_client: discord.VoiceClient):
        msg_text = msg.content

        self.replace_dictionary(msg)

        if str(msg.author.id) not in list(self.user_speaker_dict.keys()):
            self.add_user_speaker(msg.author, 3)
        
        speaker_id = int(self.user_speaker_dict[str(msg.author.id)])

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

    def add_user_speaker(self, member: discord.Member, id: int):
        self.user_speaker_dict[member.id] = str(id)
        with open(f"./json/{member.guild.id}_speakerid.json","w",encoding="UTF-8") as f:
            f.write(json.dumps(self.user_speaker_dict, indent=4))
        return
    
    def load_user_speaker_id(self, ctx: commands.Context):
        if len(self.user_speaker_dict) == 0:
            if os.path.isfile(f"./json/{ctx.guild.id}_speakerid.json"):
                with open(f"./json/{ctx.guild.id}_speakerid.json","r",encoding="UTF-8") as f:
                    self.user_speaker_dict = json.load(f)
        logger.debug(self.user_speaker_dict)

    def load_dictionary(self, guild: discord.guild):
        if os.path.isfile(f"./json/{guild.id}_dictionary.json"):
            with open(f"./json/{guild.id}_dictionary.json","r",encoding="UTF-8") as f:
                self.word_dict = json.load(f)

    async def add_dictionary(self,ctx: commands.Context, from_word: str, to_word: str):
        self.word_dict[from_word] = to_word
        with open(f"./json/{ctx.guild.id}_dictionary.json","w",encoding="UTF-8") as f:
            f.write(json.dumps(self.word_dict,indent=4))
        await ctx.channel.send(f"{ctx.author.mention} {from_word}の読みを{to_word}として登録しました")
        return

    async def del_dictionary(self, ctx: commands.Context, del_word: str):
        del self.word_dict[del_word]
        with open(f"./json/{ctx.guild.id}_dictionary.json","w",encoding="UTF-8") as f:
            f.write(json.dumps(self.word_dict,indent=4))
        await ctx.channel.send(f"{ctx.author.mention} {del_word}の読みを削除しました")
        return
    
    def replace_dictionary(self, msg: discord.Message):
        self.load_dictionary(msg.guild)
        read_list=[]
        for i, one_dic in enumerate(self.word_dict.items()):
            self.msg_text = self.msg_text.replace(one_dic[0], '{'+str(i)+'}')
            read_list.append(one_dic[1])
        msg_text = msg_text.format(*read_list)




class Dropdown(discord.ui.Select):
    def __init__(self, vv: VoiceVox):
        self.vv = vv
        options = []
        for i in range(1,len(METAS)):
            filtered = list(filter(lambda x: x.name=="ノーマル",METAS[i].styles))
            if len(filtered) == 1:
                options.append(discord.SelectOption(label=f"{METAS[i].name} : {filtered[0].id}"))
        super().__init__(placeholder="初期設定はずんだもんです",min_values=1,max_values=1,options=options)


    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f"{interaction.user.name}の読み上げは{self.values}です")
        logger.info(f"{interaction.user.name}の読み上げは{self.values[0]}です")
        speaker_id = re.findall(r"\d+",self.values[0])
        self.vv.add_user_speaker(interaction.user,int(speaker_id[len(speaker_id)-1]))

class DropdownView(discord.ui.View):
    def __init__(self, vv: VoiceVox):
        super().__init__()
        self.add_item(Dropdown(vv))