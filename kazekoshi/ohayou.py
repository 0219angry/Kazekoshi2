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

class Ohayou:
    def __init__(self):
        self.ohayou_member = {}
    
    def load_ohayou(self,guild: discord.guild):
        if os.path.isfile(f"./json/{guild.id}_ohayou.json"):
            with open(f"./json/{guild.id}_ohayou.json","r",encoding="UTF-8") as f:
                self.ohayou_member = json.load(f)

    async def add_ohayou(self, ctx: commands.Context, user: discord.Member):
        self.ohayou_member[str(user.id)] = ctx.channel.id
        with open(f"./json/{ctx.guild.id}_ohayou.json","w",encoding="UTF-8") as f:
            f.write(json.dumps(self.ohayou_member,indent=4))
        await ctx.channel.send(f"{ctx.author.mention} {user.display_name}に{ctx.channel.name}であいさつするよ")

    async def send_ohayou(self, before: discord.Member, after: discord.Member):
        self.load_ohayou(before.guild)
        if str(before.id) in self.ohayou_member.keys():
            if before.status == discord.Status.offline and after.status == discord.Status.online:
                await self.ohayou_member[str(before.id)].send(f"{before.mention}おはよう")
    