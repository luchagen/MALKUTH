# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:11:22 2023

@author: suric
"""
import discord
from discord.ext import commands

import parameters
import imagemalk.imagemalkcog
import txtmalk.malkuthcog




description = '''Malkuth has some plans to dominate the world.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='?', description=description, intents=intents)



@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(imagemalk.imagemalkcog.imgmalkcog(bot))
    await bot.add_cog(txtmalk.malkuthcog.malkcog(bot,parameters.youtube_api_key))
    
@bot.event    
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == bot.user.id:
        return
    await bot.process_commands(message)

bot.run(parameters.discord_api_key)