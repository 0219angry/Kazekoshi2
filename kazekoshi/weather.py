import requests
import json
import pprint
import configparser
import sys
from logging import (DEBUG, INFO, NOTSET, FileHandler, Formatter, StreamHandler, basicConfig, getLogger)

# Discord.py
import discord
from discord.ext import commands

logger = getLogger(__name__)

class Weather:
    def __init__(self) -> None:
        try:
            config = configparser.ConfigParser()
            config.read("config.ini", encoding="UTF-8")

            self.OPEN_WEATHER_MAP_TOKEN = config["DEFAULT"]["OPEN_WEATHER_MAP_TOKEN"]

        except:
            logger.exception("Not Found file : config.ini")
            sys.exit()
            
    def get_temp(self):
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": "35.02139",
                "lon": "135.75556",


                "appid": self.OPEN_WEATHER_MAP_TOKEN,
                "units": "metric",
                "lang": "ja",
            },
        )
        
        ret = json.loads(response.text)
        return ret["main"]["temp"]
    
    async def is_atsui(self, msg: discord.message):
        temp = self.get_temp()
        
        if temp > 25:
            await msg.channel.send(f"{msg.author.mention}、あついね:hot_face: :hot_face: :hot_face:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's TRUE.({temp}C)")
        else:
            await msg.channel.send(f"{msg.author.mention}、あつくないね:sweat_smile: :sweat_smile: :sweat_smile:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's FALSE.({temp}C)")
    
    async def is_atsukunai(self, msg: discord.message):
        temp = self.get_temp()
        
        if temp > 25:
            await msg.channel.send(f"{msg.author.mention}、あつくなくないね:hot_face: :hot_face: :hot_face:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's TRUE.({temp}C)")
        else:
            await msg.channel.send(f"{msg.author.mention}、あつくないね:sweat_smile: :sweat_smile: :sweat_smile:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's FALSE.({temp}C)")
    
    async def is_samui(self, msg: discord.message):
        temp = self.get_temp()
        
        if temp < 12:
            await msg.channel.send(f"{msg.author.mention}、さむいね:cold_face: :cold_face: :cold_face:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's TRUE.({temp}C)")
        else:
            await msg.channel.send(f"{msg.author.mention}、さむくないね:sweat_smile: :sweat_smile: :sweat_smile:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's FALSE.({temp}C)")
            
    async def is_samukunai(self, msg: discord.message):
        temp = self.get_temp()
        
        if temp < 12:
            await msg.channel.send(f"{msg.author.mention}、さむくなくないね:cold_face: :cold_face: :cold_face:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's TRUE.({temp}C)")
        else:
            await msg.channel.send(f"{msg.author.mention}、さむくないね:star_struck: :star_struck: :star_struck:({temp}℃)")
            logger.info(f"{msg.author.name} said HOT. It's FALSE.({temp}C)")
