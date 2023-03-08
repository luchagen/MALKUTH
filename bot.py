# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:11:22 2023

@author: suric
"""
import discord
import malkuth
from discord.ext import commands
import MagickEditor
import parameters
import attachmentutils
from time import sleep

malkmagic=MagickEditor.MagickEditor()
babamalk= malkuth.malkuth(1,100,0.9,3,2,True)
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
            if message.content[:7]== '@MALKUTH':
                reply=babamalk.generate_response(message.content[8:],message.author.name)
            elif message.content[:22] == '<@1068268891580682293>':
                reply=babamalk.generate_response(message.content[22:],message.author.name)
            else :
                reply=babamalk.generate_response(message.content,message.author.name)
            print(reply)
            if reply[-4:] == '</s>':
                reply =reply[:-4]
            await message.channel.send(reply[0])
    #attachmentlogging
    if attachmentutils.checklogging(message.channel.guild.name, message.channel.name):
        for thing in message.embeds:
            if thing.url[:18]!='https://tenor.com/' :
                attachmentutils.storepicture(thing.url,message.channel.name)
        for thing in message.attachments :
            if thing.url[:18]!='https://tenor.com/' :
                attachmentutils.storepicture(thing.url,message.channel.name)
                
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
            images=[str(attachment) for attachment in ctx.message.attachments]
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

@bot.command(description='debug')
async def debug(ctx , command: str=''):
    if command == 'lastmemory':
        await ctx.channel.send(babamalk.last_activated)
    if command == 'lastmessage':
        await ctx.channel.send(babamalk.lastresponse)

@bot.command(description='unconstrained interaction with the language model')
async def prompt(ctx, prompt: str):
    async with ctx.channel.typing():
        await ctx.send(babamalk.freeprompt(prompt))

@bot.command(description='program (kinda) the response Malkuth would say to a (or a string of) question(s)')
async def program(ctx, questions: str, answer: str):
    async with ctx.channel.typing():
        babamalk.program(questions,answer)
        await ctx.send(" :question: Malkuth will remember that.")

@bot.command(description="activate or deactivate logging attachments into Malkuth's memory for this channel")
async def attachmentlog(ctx):
    async with ctx.channel.typing():
        logging_activated=attachmentutils.changelogging(ctx.channel.guild.name, ctx.channel.name)
        if attachmentutils.checklogging(ctx.channel.guild.name, ctx.channel.name):
            await ctx.send(" :question: Malkuth will now log all attachments posted in this channel.")
        else:
            await ctx.send(" :question: Malkuth will now stop logging all attachments posted in this channel.")

@bot.command(description="check what Malkuth has in stock in her library of pictures")
async def picturetypes(ctx):
        await ctx.send(str(attachmentutils.getalltables()))
        
@bot.command(description="send a random picture from one of Malkuth's library")
async def randompicture(ctx, what : str, do_logging: int =0 ):
    async with ctx.channel.typing():
        img = attachmentutils.getrandompicture(what)
        if isinstance(img[0],str):
            await ctx.send(img[0])
            if do_logging==1:
                attachmentutils.storepicture(img[0],ctx.channel.name)
        else:
            await ctx.send(img[0][0])
            if do_logging==1:
                attachmentutils.storepicture(img[0][0],ctx.channel.name)
                        
@bot.command(description="send a picture from one of Malkuth's library")
async def picture(ctx, what : str, pictureid: int, do_logging: int =0 ):
    async with ctx.channel.typing():
        img = attachmentutils.getonepicture(what,pictureid)
        if isinstance(img[0],str):
            await ctx.send(img[0])
            if do_logging==1:
                attachmentutils.storepicture(img[0],ctx.channel.name)
        else:
            await ctx.send(img[0][0])
            if do_logging==1:
                attachmentutils.storepicture(img[0][0],ctx.channel.name)
        
@bot.command(description="send every picture from one of Malkuth's library")
async def everypicture(ctx, what : str, areyousureaboutwhatyouredoing: str, do_logging: int =0 ):
    if areyousureaboutwhatyouredoing=='I am sure about what I am doing' :
        images = attachmentutils.getallpictures(what)
        for img in images:
            async with ctx.channel.typing():
                if isinstance(img,str):
                    await ctx.send(img)
                    if do_logging==1:
                        attachmentutils.storepicture(img,ctx.channel.name)
                else:
                    await ctx.send(img[0])
                    if do_logging==1:
                        attachmentutils.storepicture(img[0],ctx.channel.name)
                    

bot.run(parameters.discord_api_key)