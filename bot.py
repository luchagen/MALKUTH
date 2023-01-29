# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:11:22 2023

@author: suric
"""
import discord
import malkuth
from discord.ext import commands
import MagickEditor
malkmagic=MagickEditor.MagickEditor()
babamalk= malkuth.malkuth(1,100,0.9,3,20,True)
description = '''Malkuth has some plans to dominate the world.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    

@bot.event    
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == bot.user.id:
        return
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            reply=babamalk.generate_response(message.content,message.author.name)
            print(reply)
            await message.channel.send(reply[0])
    await bot.process_commands(message)

@bot.command(description='Send forth malkuth to the lands of youtube')
async def malkuth_on_youtube(ctx, ytvideo: str=""):
    async with ctx.channel.typing():
        await ctx.send(babamalk.youtube_video(ytvideo))
    
@bot.command(description='What s on your mind malkuth?')
async def wassup(ctx):
    async with ctx.channel.typing():
        await ctx.send(babamalk.on_my_mind())
        
@bot.command(description='use your stand malkuth')
async def heavens_gate_magick(ctx ,strength:float=0.5, image: str=""):
    async with ctx.channel.typing():
        if image=="":
            images=[str(attachment) for attachment in ctx.message.attachments if str(attachment)[-4:]=='.png' or str(attachment)[-4]=='.jpg']
            if len(images)==0:
                if babamalk.last_video !="":
                    images= [babamalk.last_video["thumbnail"][-1]["url"]]
                else:
                    images=[bot.user.avatar.url]
        else : 
            images = [image]
        files=[]
        for img in images:
            file=discord.File(malkmagic.magick(img,strength))
            files.append(file)
        await ctx.channel.send(files=files)

@bot.command(description='unconstrained interaction with the language model')
async def prompt(ctx, prompt: str):
    async with ctx.channel.typing():
        await ctx.send(babamalk.freeprompt(prompt))
bot.run('MTA2ODI2ODg5MTU4MDY4MjI5Mw.GwA5gO.jQ_DXcXZqOB3B8qH497AWEmr1k1TnKMhOhZCzs')