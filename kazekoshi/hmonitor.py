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

class HMonitor:
    def __init__(self):
        pass
    
    def create_record()