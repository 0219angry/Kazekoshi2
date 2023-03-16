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
import pprint

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
        self.queue_dict_text = defaultdict(deque)
        self.queue_dict_speaker = defaultdict(deque)
        # userとspeakerの辞書 {userid:speakerid}
        self.user_speaker_dict = {}
        # 読み上げる文章
        self.msg_text = ""


    # VOICEVOX function difinition
    async def create_voice(self, msg: discord.Message, speaker_id: int, voice_client: discord.VoiceClient):
        self.msg_text = msg.content

        # 読み上げ用処理
        self.replace_URL()
        self.replace_mention(msg)
        self.replace_channel(msg)

        self.replace_dictionary(msg)

        if str(msg.author.id) not in list(self.user_speaker_dict.keys()):
            self.add_user_speaker(msg.author, 3)
        
        speaker_id = int(self.user_speaker_dict[str(msg.author.id)])

        self.enqueue(voice_client, msg.guild, self.msg_text, speaker_id)
        
        logger.info(f"メッセージ[{self.msg_text}]の読み上げ完了")
        
        wavlist = glob.glob("./temp/*.wav")
        wavlist.sort(reverse=False)
        if len(wavlist) > self.MAX_WAV_FILE:
            for i in range(len(wavlist)-self.MAX_WAV_FILE):
                os.remove(wavlist[i])
        return

    def synthesize_voice(self, speaker_id: int):
        wave_bytes = self.core.tts(self.msg_text, speaker_id)
        return wave_bytes


    def enqueue(self, voice_client: discord.VoiceClient, guild: discord.Guild, msg_text: str, speaker_id: int):
        queue_text = self.queue_dict_text[guild.id]
        queue_speaker = self.queue_dict_speaker[guild.id]
        queue_text.append(msg_text)
        queue_speaker.append(speaker_id)
        if not voice_client.is_playing():
            self.synthesize_play(voice_client, queue_text, queue_speaker)

    def synthesize_play(self, voice_client: discord.VoiceClient, queue_text: deque, queue_speaker: deque):
        if not queue_text or voice_client.is_playing():
          return
        text = queue_text.popleft()
        speaker = queue_speaker.popleft()
        
        wavfilename = f"./temp/{datetime.now():%Y-%m-%d_%H%M%S}.wav"
        if not self.core.is_model_loaded(speaker):
            self.core.load_model(speaker)
        wave_bytes = self.synthesize_voice(speaker)
        
        with open(wavfilename,"wb") as f:
            f.write(wave_bytes)

        source = discord.FFmpegPCMAudio(wavfilename)
        voice_client.play(source, after=lambda e:self.synthesize_play(voice_client, queue_text, queue_speaker))

    def add_user_speaker(self, member: discord.Member, id: int):
        self.user_speaker_dict[str(member.id)] = str(id)
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
    
    async def print_dictionary(self, ctx: commands.Context):
        dict_str = "```"
        for from_word, to_word in self.word_dict.items():
            dict_str += f"{from_word} => {to_word}\n"
            if len(dict_str) > 2000:
                dict_str += "```"
                dict_embed = discord.Embed(title=f"サーバー {ctx.guild.name} の辞書",description=dict_str)
                await ctx.channel.send(embed=dict_embed)
                dict_str = "```"
        dict_str += "```"
        dict_embed = discord.Embed(title=f"サーバー {ctx.guild.name} の辞書",description=dict_str)

        await ctx.channel.send(embed=dict_embed)
        


    # 読み上げ用の処理
    def replace_URL(self):
        self.msg_text = re.sub(r"https?://.*?\s|https?://.*?$", "URL", self.msg_text)

    def replace_mention(self, msg:discord.Message):
        if "<@" and ">" in self.msg_text:
            Temp = re.findall("<@!?([0-9]+)>", self.msg_text)
            for i in range(len(Temp)):
                Temp[i] = int(Temp[i])
                user = msg.guild.get_member(Temp[i])
                self.msg_text = re.sub(f"<@!?{Temp[i]}>", "アット" + user.display_name, self.msg_text)

    def replace_dictionary(self, msg: discord.Message):
        self.load_dictionary(msg.guild)
        read_list=[]
        for i, one_dic in enumerate(self.word_dict.items()):
            self.msg_text = self.msg_text.replace(one_dic[0], '{'+str(i)+'}')
            read_list.append(one_dic[1])
        self.msg_text = self.msg_text.format(*read_list)
        
    def replace_channel(self, msg:discord.Message):
            if "<#" and ">" in self.msg_text:
                Temp = re.findall("<#!?([0-9]+)>", self.msg_text)
            for i in range(len(Temp)):
                Temp[i] = int(Temp[i])
                channel = msg.guild.get_channel_or_thread(Temp[i])
                self.msg_text = re.sub(f"<#!?{Temp[i]}>", "チャンネル" + channel.name, self.msg_text)

class Dropdown(discord.ui.Select):
    def __init__(self, vv: VoiceVox):
        self.vv = vv
        options = []
        for i in range(0,len(METAS)):
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