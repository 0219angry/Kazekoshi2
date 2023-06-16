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
from random import random

# Discord.py
import discord
from discord.ext import commands

logger = getLogger(__name__)

class WordWolfFrame:
    def __init__(self):
        self.wordwolf_instance = {}
        pass

    def newgame(self, channel: discord.channel):
        self.wordwolf_instance[channel.id] = WordWolf()
        



class WordWolf:
    def __init__(self):
        self.theme_dict = {} # ワードウルフお題辞書
        self.genre = "" # お題のジャンル
        self.villager = "" # お題(正解)
        self.werewolf = "" # お題(間違い)
        self.player_list = WordWolfPlayerList()
        self.watching_message
        self.game_state = ""
        
    def load_theme_dict(self):
        if os.path.isfile(f"./games/wordwolf_theme.json"):
            with open(f"./games/wordwolf_theme.json","r", encoding="UTF-8") as f:
                self.theme_dict = json.load(f)
    
    def regist_watching_message(self, message:discord.Message):
        self.watching_message = message

    async def add_player(self, member:discord.Member):
        self.player_list.add_player(member)
        await self.watching_message.channel.send(f"{member.mention} 参加登録完了！")

    async def remove_player(self, member:discord.Member):
        self.player_list.remove_player(member)
        await self.watching_message.channel.send(f"{member.mention} 参加登録を取り消しました")

    async def look_for_member(self):
        embed = discord.Embed(title="W O R D W O L F")
        embed.add_field(name="参加方法", value="リアクションをクリック")
        embed.add_field(name="プレイ方法",value="会話から違うお題を渡されたプレイヤー<人狼>を見つけ出せ！")
        embed.add_field(name="",value="30秒後に開始します")
        self.looking_message = await self.channel.send(embed=embed)
        await self.looking_message.add_reaction("👍")


    def create_theme(self):
        if os.path.isfile(f"./games/wordwolf_theme.json"):
            with open(f"./games/wordwolf_theme.json","r", encoding="UTF-8") as f:
                theme_dict = json.load(f)

        self.genre = random.choice(list(theme_dict.keys()))
        theme = random.sample(theme_dict[self.genre],2)
        # お題をお題辞書から選択する
        self.villager = theme[0]
        self.werewolf = theme[1]
        logger.info(f"ジャンル：{self.genre}多数派：{self.villager} 少数派：{self.werewolf}")
    


class WordWolfPlayer:
    def __init__(self, member):
        self.discord = member
        self.role = "villager"
        pass


class WordWolfPlayerList:
    def __init__(self) -> None:
        self.player_list = []
    
    def add_player(self, member=0):
        newplayer = WordWolfPlayer(random.random())
        self.player_list.append(newplayer)
        pass
    
    def remove_player(self, member):
        for player in self.player_list:
            if player.discord == member:
                self.player_list.remove(player)

    def set_roles(self, number=1):
        werewolf_player = random.choice(self.player_list)
        werewolf_player.role = "werewolf"
        return werewolf_player

class DiscordWordWolf:
    def __init__(self,ctx: commands.Context=None):
        self.channel = ctx.channel
        self.looking_message


    def load_theme_dict(self,ctx: commands.Context):
        pass
    
    async def look_for_member(self):
        embed = discord.Embed(title="W O R D W O L F")
        embed.add_field(name="参加方法", value="リアクションをクリック")
        embed.add_field(name="プレイ方法",value="会話から違うお題を渡されたプレイヤー<人狼>を見つけ出せ！")
        embed.add_field(name="",value="30秒後に開始します")
        self.looking_message = await self.channel.send(embed=embed)
        await self.looking_message.add_reaction("👍")

    async def add_player(self, player: discord.Member):
        
        pass

    
    async def start_wordwolf(self):
        self.create_theme()


        startgame_embed = discord.Embed(title="ゲーム開始！")
        # self.werewolf_player = max(self.player.items(), key = lambda x:x[1])[0]
        
        # startgame_embed.add_field(name="人狼",value=f"{self.werewolf_player.name}")
        startgame_embed.add_field(name="人狼",value="[||じんろうのなまえ||]")
        startgame_embed.add_field(name="多数派のお題",value=f"[||{self.villager}||]")
        startgame_embed.add_field(name="少数派のお題",value=f"[||{self.werewolf}||]")

        await self.channel.send(embed=startgame_embed)
