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
from random import randint

# Discord.py
import discord
from discord.ext import commands

logger = getLogger(__name__)

class Dice:
    def __init__(self, ctx: commands.Context, arg):
        self.ctx = ctx
        self.arg = arg
        self.result = []
        self.input = []
        
    def roll_dice(self,a:int):
        return randint(1,a)
    
    async def create_dice(self):
        self.input = re.findall(r'\d+',self.arg)
        if len(self.input) != 2:
            logger.info("[個数]D[目の数]の形式で入力してください")
            await self.ctx.reply("[個数]D[目の数]の形式で入力してください")
            return
            
        quantity = int(self.input[0])
        figure = int(self.input[1])
        for i in range(0,quantity):
            self.result.append(self.roll_dice(figure))
        await self.send_dice_result()
        
    async def send_dice_result(self):
        await self.ctx.reply(f"{self.ctx.author.mention} ({self.input[0]}D{self.input[1]})=>{sum(self.result)}{self.result}=>{sum(self.result)}")
        return