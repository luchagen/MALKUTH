# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 12:36:50 2023

@author: suric
"""
from discord.ext import commands
import discord
from imagemalk import MagickEditor,image_libraries,discord_message_images

class ImageMalkCog(commands.Cog):
    '''discord bot cog for interacting with images.'''
    def __init__(self,bot):
        self.bot=bot
        self.malkmagic=MagickEditor.MagickEditor()
        self.library_handler=image_libraries.ImageLibraryHandler()
        self.message_images =discord_message_images.MessageImageFetcher()

    async def lastpicture(self,channel):
        '''Returns images from last message that had at least an image.'''
        async for message in channel.history(limit=100):
            images=self.message_images.get_images_from_message(message)
            if images:
                break
        return images

    @commands.Cog.listener()
    async def on_message(self,message):
        '''log images from messages into relevant libraries'''
        if message.author.id == self.bot.user.id:
            return
        if self.library_handler.check_logging(str(message.channel.guild.id), message.channel.name):
            image_urls = self.get_images_from_message(message)
            for img_url in image_urls:
                self.library_handler.store_picture(img_url,message.channel.name)

    @commands.command(description='use your stand malkuth')
    async def heavens_gate_magick(self,ctx ,strength:float=0.5, image: str=""):
        ''' Uses the seam carving algorithm to produce funny effects. '''
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
            self.library_handler.change_logging(str(ctx.channel.guild.id), ctx.channel.name)
            if self.library_handler.check_logging(str(ctx.channel.guild.id), ctx.channel.name):
                await ctx.send(" :question: Malkuth will now log all attachments posted in this channel.")
            else:
                await ctx.send(" :question: Malkuth will now stop logging all attachments posted in this channel.")

    @commands.command(description="check what Malkuth has in stock in her library of pictures")
    async def picturetypes(self,ctx):
        await ctx.send(str(self.library_handler.get_all_tables()))
            
    @commands.command(description="send a random picture from one of Malkuth's library")
    async def randompicture(self,ctx, what : str=commands.parameter(default="", description="The library you want a picture from, empty for the current channel") , do_logging: int =commands.parameter(default=0, description="Set to 1 to log the result into this channel's library") ):
        if what=="":
            what= ctx.channel.name
        async with ctx.channel.typing():
            img = self.library_handler.get_random_picture(what)
            if isinstance(img[0],str):
                await ctx.send(img[0])
                if do_logging==1:
                    self.library_handler.store_picture(img[0],ctx.channel.name)
            else:
                await ctx.send(img[0][0])
                if do_logging==1:
                    self.library_handler.store_picture(img[0][0],ctx.channel.name)

    @commands.command(description="delete a picture from one of Malkuth's library")
    async def deletepicture(self,ctx, what : str=commands.parameter(default="", description="The library you want to delete a picture from, empty for the current channel"), pictureid: int=0 ):
        if what=="":
            what= ctx.channel.name
        async with ctx.channel.typing():
            self.library_handler.delete_one_picture(what,pictureid)
                    
    @commands.command(description="send a picture from one of Malkuth's library")
    async def picture(self,ctx, what : str=commands.parameter(default="", description="The library you want a picture from, empty for the current channel") , pictureid: int=commands.parameter(default=1, description="The id of the picture you want.") , do_logging: int =commands.parameter(default=0, description="Set to 1 to log the result into this channel's library")   ):
        if what=="":
            what= ctx.channel.name
        async with ctx.channel.typing():
            img = self.library_handler.get_one_picture(what,pictureid)
            if isinstance(img[0],str):
                await ctx.send(img[0])
                if do_logging==1:
                    self.library_handler.store_picture(img[0],ctx.channel.name)
            else:
                await ctx.send(img[0][0])
                if do_logging==1:
                    self.library_handler.store_picture(img[0][0],ctx.channel.name)

    @commands.command(description="send every picture from one of Malkuth's library")
    async def everypicture(self,ctx, what : str, do_logging: int =0 ):
        print(ctx.channel.name)
        images = self.library_handler.get_all_pictures(what)
        for img in images:
            async with ctx.channel.typing():
                if isinstance(img,str):
                    await ctx.send(img)
                    if do_logging==1:
                        self.library_handler.store_picture(img,ctx.channel.name)
                else:
                    await ctx.send(img[0])
                    if do_logging==1:
                        self.library_handler.store_picture(img[0],ctx.channel.name)

    @commands.command(description='''completely reload one channels library.
                       Use as a last resort, some images might not register.''')
    async def reloadattachmentlibrary(self,ctx):
        async with ctx.channel.typing():
            self.library_handler.drop_library(ctx.channel.name)
            async for message in ctx.channel.history(limit=None):
                images=self.message_images.get_images_from_message(message)
                for image in images :
                    self.library_handler.store_picture(image,message.channel.name)
            await ctx.send(''' :question: Malkuth has successfully rebuilt message history.''')
