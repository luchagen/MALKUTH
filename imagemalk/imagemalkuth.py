# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 12:36:50 2023

@author: suric
"""
from discord.ext import commands
import discord
from imagemalk import MagickEditor,image_libraries,discord_message_images

class ImageMalkuth():
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


    async def log_message_attachments(self,message):
        '''log images from messages into relevant libraries'''
        if message.author.id == self.bot.user.id:
            return
        if self.library_handler.check_logging(str(message.channel.guild.id), message.channel.name):
            image_urls = self.message_images.get_images_from_message(message)
            for img_url in image_urls:
                self.library_handler.store_picture(img_url,message.channel.name)


    async def magick_effect(self,ctx ,strength:float, image: str):
        '''
        Uses the seam carving algorithm to produce funny effects on an image. 
        By default will just pick the last sent image in the channel
        '''
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
                file=discord.File(self.malkmagic.magick(img,1-strength))
                files.append(file)
            await ctx.channel.send(files=files)


    async def activate_attachment_logging(self,ctx):
        '''
        decide for each channel if we should log the image attachments (images, embeds)
        The attachments will be saved into a library named after the channel name.
        '''
        async with ctx.channel.typing():
            self.library_handler.change_logging(str(ctx.channel.guild.id), ctx.channel.name)
            if self.library_handler.check_logging(str(ctx.channel.guild.id), ctx.channel.name):
                await ctx.send(''' :question:
                    Malkuth will now log all attachments posted in this channel.''')
            else:
                await ctx.send(''' :question:
                    Malkuth will no longer record all attachments posted in this channel.''')


    async def picture_libraries(self,ctx):
        '''Send all picture libraries from malkuth.
            For now there is no coniditon for accessing libraries.'''
        await ctx.send(str(self.library_handler.get_all_tables()))


    async def delete_picture(self,ctx, library_name : str,pictureid: int):
        '''Delete a picture from one of the libraries.'''
        if library_name=="":
            library_name= ctx.channel.name
        async with ctx.channel.typing():
            self.library_handler.delete_one_picture(library_name,pictureid)


    async def picture(self,context,library_name : str,pictureid: int,do_logging: int):
        '''Send a picture from a specific library'''
        async with context.channel.typing():
            img = self.library_handler.get_one_picture(library_name,pictureid)
            if isinstance(img[0],str):
                await context.send(img[0])
                if do_logging==1:
                    self.library_handler.store_picture(img[0],context.channel.name)
            else:
                await context.send(img[0][0])
                if do_logging==1:
                    self.library_handler.store_picture(img[0][0],context.channel.name)


    async def send_random_pictures(self,context, library_name : str,amount, do_logging: int):
        '''send random pictures from a specific library
            to a discord channel identified by the context variable.
            we may send more than 10 images at once if the user can anyway manage the channel.'''
        images = self.library_handler.get_random_pictures(library_name,amount)
        for img in images:
            async with context.channel.typing():
                if isinstance(img,str):
                    await context.send(img)
                    if do_logging==1:
                        self.library_handler.store_picture(img,context.channel.name)
                else:
                    await context.send(img[0])
                    if do_logging==1:
                        self.library_handler.store_picture(img[0],context.channel.name)


    async def reload_attachment_library(self,ctx):
        '''reload attachment library completely for a channel'''
        async with ctx.channel.typing():
            self.library_handler.drop_library(ctx.channel.name)
            async for message in ctx.channel.history(limit=None):
                images=self.message_images.get_images_from_message(message)
                for image in images :
                    self.library_handler.store_picture(image,message.channel.name)
            await ctx.send(''' :question: Malkuth has successfully rebuilt message history.''')
