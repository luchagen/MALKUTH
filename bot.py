# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:11:22 2023

@author: suric
"""
import discord
from discord.ext import commands
from discord import PCMVolumeTransformer
from discord.utils import get
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import parameters
import imagemalk.imagemalkcog as imagemalkcog
import txtmalk.malkuthcog as malkuthcog
import syncmalk.syncmalkcog as syncmalkcog
import vocmalk.voccog as vocmalkcog
import asyncio




description = '''Malkuth has some plans to dominate the world.'''

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(imagemalkcog.imgmalkcog(bot))
    await bot.add_cog(malkuthcog.malkcog(bot,parameters.youtube_api_key))
    await bot.add_cog(syncmalkcog.syncog(bot))
    await bot.add_cog(vocmalkcog.voccog(bot))
    
@bot.event    
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == bot.user.id:
        return
    await bot.process_commands(message)

bot.run(parameters.discord_api_key)
