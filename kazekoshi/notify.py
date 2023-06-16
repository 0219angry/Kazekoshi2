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

class Notify:
    def __init__(self):
        # 通知するボイスチャンネルとテキストチャンネルのセット
        self.notify_dict = {}
        
        pass
    
    def load_notify_dict(self,guild:discord.guild):
        if os.path.isfile(f"./json/{guild.id}_notify.json"):
            with open(f"./json/{guild.id}_notify.json","r",encoding="UTF-8") as f:
                self.notify_dict = json.load(f)
    
    def add_notify_dict(self, voice:discord.channel, text:discord.channel):
        self.notify_dict[str(voice.id)] = str(text.id)
        with open(f"./json/{voice.guild.id}_notify.json","w",encoding="UTF-8") as f:
            f.write(json.dumps(self.notify_dict, indent=4))
        return