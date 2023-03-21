# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 12:36:50 2023

@author: suric
"""
import imagemalk.MagickEditor as MagickEditor
from discord.ext import commands
import discord
import imagemalk.attachmentutils as attachmentutils

class imgmalkcog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.malkmagic=MagickEditor.MagickEditor()
        
    async def lastpicture(self,channel):
        lastpics=[]
        async for message in channel.history(limit=1):
            for thing in message.embeds:
                imgurl="notfound"
                if thing.url !=None:
                    if thing.url[:18]!='https://tenor.com/' :
                        imgurl=thing.url
                if thing.thumbnail !=None and thing.thumbnail.proxy_url!=None:
                    if thing.thumbnail.proxy_url[:18]!='https://tenor.com/' :
                        imgurl=thing.thumbnail.proxy_url
                if thing.image != None and thing.image.proxy_url!=None :
                    if thing.image.proxy_url[:18]!='https://tenor.com/'  :
                        imgurl=thing.image.proxy_url
                if thing.image != None and thing.image.url!=None :
                    if thing.image.url[:18]!='https://tenor.com/'  :
                        imgurl=thing.image.url
                if thing.thumbnail !=None and thing.thumbnail.url!=None :
                    if thing.thumbnail.url[:18]!='https://tenor.com/' :
                        imgurl=thing.thumbnail.url
                lastpics.append(imgurl)
            for thing in message.attachments :
                if thing.url[:18]!='https://tenor.com/' :
                    lastpics.append(thing.url)
        return lastpics
    
    @commands.Cog.listener()
    async def on_message(self,message):
        # we do not want the bot to reply to itself
        if message.author.id == self.bot.user.id:
            return
        #attachmentlogging
        if attachmentutils.checklogging(str(message.channel.guild.id), message.channel.name):
            for thing in message.embeds:
                    imgurl="notfound"
                    if thing.url!=None:
                        if thing.url[:18]!='https://tenor.com/' :
                            imgurl=thing.url
                    if thing.thumbnail !=None and thing.thumbnail.proxy_url!=None:
                        if thing.thumbnail.proxy_url[:18]!='https://tenor.com/' :
                            imgurl=thing.thumbnail.proxy_url
                    if thing.image != None and thing.image.proxy_url!=None :
                        if thing.image.proxy_url[:18]!='https://tenor.com/'  :
                            imgurl=thing.image.proxy_url
                    if thing.image != None and thing.image.url!=None :
                        if thing.image.url[:18]!='https://tenor.com/'  :
                            imgurl=thing.image.url
                    if thing.thumbnail !=None and thing.thumbnail.url!=None :
                        if thing.thumbnail.url[:18]!='https://tenor.com/' :
                            imgurl=thing.thumbnail.url
                    attachmentutils.storepicture(imgurl,message.channel.name)
            for thing in message.attachments :
                if thing.url[:18]!='https://tenor.com/' :
                    attachmentutils.storepicture(thing.url,message.channel.name)
    
    @commands.command(description='use your stand malkuth')
    async def heavens_gate_magick(self,ctx ,strength:float=0.5, image: str=""):
        async with ctx.channel.typing():
            if image=="":
                images=[str(attachment) for attachment in ctx.message.attachments]
                if len(images)==0:
                    lastpics=self.lastpicture(ctx.channel)
                    if lastpics !=[]:
                        images= lastpics
                    else:
                        images=[self.bot.user.avatar.url]
            else : 
                images = [image]
            files=[]
            for img in images:
                file=discord.File(self.malkmagic.magick(img,strength))
                files.append(file)
            await ctx.channel.send(files=files)


    @commands.command(description="activate or deactivate logging attachments into Malkuth's memory for this channel")
    async def attachmentlog(self,ctx):
        async with ctx.channel.typing():
            logging_activated=attachmentutils.changelogging(str(ctx.channel.guild.id), ctx.channel.name)
            if attachmentutils.checklogging(str(ctx.channel.guild.id), ctx.channel.name):
                await ctx.send(" :question: Malkuth will now log all attachments posted in this channel.")
            else:
                await ctx.send(" :question: Malkuth will now stop logging all attachments posted in this channel.")

    @commands.command(description="check what Malkuth has in stock in her library of pictures")
    async def picturetypes(self,ctx):
            await ctx.send(str(attachmentutils.getalltables()))
            
    @commands.command(description="send a random picture from one of Malkuth's library")
    async def randompicture(self,ctx, what : str=commands.parameter(default="", description="The library you want a picture from, empty for the current channel") , do_logging: int =commands.parameter(default=0, description="Set to 1 to log the result into this channel's library") ):
        if what=="":
            what= ctx.channel.name
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

    @commands.command(description="delete a picture from one of Malkuth's library")
    async def deletepicture(self,ctx, what : str=commands.parameter(default="", description="The library you want to delete a picture from, empty for the current channel"), pictureid: int=0 ):
        if what=="":
               what= ctx.channel.name
        async with ctx.channel.typing():
            img = attachmentutils.deleteonepicture(what,pictureid)
                    
    @commands.command(description="send a picture from one of Malkuth's library")
    async def picture(self,ctx, what : str=commands.parameter(default="", description="The library you want a picture from, empty for the current channel") , pictureid: int=commands.parameter(default=1, description="The id of the picture you want.") , do_logging: int =commands.parameter(default=0, description="Set to 1 to log the result into this channel's library")   ):
        if what=="":
            what= ctx.channel.name
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
            
    @commands.command(description="send every picture from one of Malkuth's library")
    async def everypicture(self,ctx, what : str, areyousureaboutwhatyouredoing: str, do_logging: int =0 ):
        print(ctx.channel.name)
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
                        
    @commands.command(description="completely reload one channels library. Use as a last resort, some images might not register.")
    async def reloadattachmentlibrary(self,ctx , areyousureaboutwhatyouredoing:str):
        if areyousureaboutwhatyouredoing=='I am sure about what I am doing' :
            async with ctx.channel.typing():
                attachmentutils.droplibrary(ctx.channel.name)
                async for message in ctx.channel.history(limit=None):
                    for thing in message.embeds:
                        imgurl="notfound"
                        if thing.url !=None:
                            if thing.url[:18]!='https://tenor.com/' :
                                imgurl=thing.url
                        if thing.thumbnail !=None and thing.thumbnail.proxy_url!=None:
                            if thing.thumbnail.proxy_url[:18]!='https://tenor.com/' :
                                imgurl=thing.thumbnail.proxy_url
                        if thing.image != None and thing.image.proxy_url!=None :
                            if thing.image.proxy_url[:18]!='https://tenor.com/'  :
                                imgurl=thing.image.proxy_url
                        if thing.image != None and thing.image.url!=None :
                            if thing.image.url[:18]!='https://tenor.com/'  :
                                imgurl=thing.image.url
                        if thing.thumbnail !=None and thing.thumbnail.url!=None :
                            if thing.thumbnail.url[:18]!='https://tenor.com/' :
                                imgurl=thing.thumbnail.url
                        attachmentutils.storepicture(imgurl,message.channel.name)
                    for thing in message.attachments :
                        if thing.url[:18]!='https://tenor.com/' :
                            attachmentutils.storepicture(thing.url,message.channel.name)
                await ctx.send(" :question: Malkuth has successfully reregistered the library associated with this channel and saved all pictures in message history.")
