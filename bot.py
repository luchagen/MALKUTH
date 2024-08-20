# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:11:22 2023

@author: suric
"""
import logging
import discord
from discord.ext import commands
import parameters
import vocmalk.voccog as vocmalkcog
from imagemalk import imagemalkcog
from txtmalk import malkuthcog
from syncmalk import syncmalkcog
from setup.SQL import pictures



DESCRIPTION = '''Malkuth has some plans to dominate the world.'''

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.voice_states = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
help_command = commands.help.DefaultHelpCommand(width=160) #change parameter description length
bot = commands.Bot(command_prefix='?',
                   description=DESCRIPTION,
                   intents=intents,
                   help_command=help_command)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(imagemalkcog.ImageMalkCog(bot))
    await bot.add_cog(malkuthcog.malkcog(bot,parameters.youtube_api_key))
    await bot.add_cog(syncmalkcog.syncog(bot))
    await bot.add_cog(vocmalkcog.voccog(bot))
    
@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == bot.user.id:
        return
    await bot.process_commands(message)

bot.run(parameters.discord_api_key,log_handler=handler)
