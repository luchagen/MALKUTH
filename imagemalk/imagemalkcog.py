# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 12:36:50 2023

@author: suric
"""
from discord.ext import commands
import discord
import parameters
from imagemalk import imagemalkuth


#generic parameters descriptions :
library_name_desc='''The library the specified picture(s) are from.
                    Libraries are usually channel names.'''
do_logging_desc='''Whether to count sent pictures into the library for this channel.
                    You can set it to 1, otherwise they won't be saved.'''

class ImageMalkCog(commands.Cog):
    '''discord bot cog for interacting with images.'''
    def __init__(self,bot):
        self.bot=bot
        self.imagemalkuth=imagemalkuth.ImageMalkuth(bot)


    @commands.Cog.listener()
    async def on_message(self,message):
        '''log images from messages into relevant libraries'''
        await self.imagemalkuth.log_message_attachments(message)


    @commands.command(description='''Magically warp a picture.
                        By default will take the last sent image in the channel.''')
    async def heavens_gate_magick(self,ctx,
            strength:float=commands.parameter(
                default=0.5,
                description='The strength of the spell, (usually) between 0 and 1.'
            ),
            image: str=commands.parameter(
                default="",
                description='(optional) Link to the image to warp.'
            )
            ):
        await self.imagemalkuth.magick_effect(ctx,strength,image)


    @commands.command(description='''Activate or deactivate the logging of pictures for this channel
                        The images will be saved in a library with the same name as the channel.''')
    async def log_attachments(self,ctx):
        await self.imagemalkuth.activate_attachment_logging(ctx)


    @commands.command(description="Check what picture libraries Malkuth has in stock")
    async def picture_libraries(self,ctx):
        await self.imagemalkuth.picture_libraries(ctx)


    @commands.command(description="Delete a picture from one of Malkuth's library")
    async def deletepicture(self,ctx,
            library_name : str=commands.parameter(
                default="",
                description=library_name_desc),
            picture_id: int=commands.parameter(
                default=1,
                description="The id of the picture you want to delete.")
        ):
        if library_name=="":
            library_name= ctx.channel.name

        await self.imagemalkuth.delete_picture(ctx,library_name,picture_id)


    @commands.command(description="Send a picture from one of Malkuth's library")
    async def picture(self,ctx,
            library_name : str=commands.parameter(
                default="",
                description=library_name_desc),
            picture_id: int=commands.parameter(
                default=1,
                description="The id of the picture you want to send."),
            do_logging: int =commands.parameter(
                default=0,
                description=do_logging_desc)
        ):
        if not library_name:
            library_name= ctx.channel.name

        await self.imagemalkuth.picture(ctx,library_name,picture_id,do_logging)


    @commands.command(
        description="Get random pictures from one of Malkuth's library (max 10)")
    async def random_pictures(self,ctx,
            library_name : str=commands.parameter(
                default="",
                description=library_name_desc
            ),
            amount : int=commands.parameter(
                default=1,
                description='''the amount of pictures to send.
                    A maximum of 10 can be sent at once.'''
            ),
            do_logging: int=commands.parameter(
                default=0,
                description=do_logging_desc
            )
        ):
        if not library_name:
            library_name= ctx.channel.name

        user_can_spam = ctx.channel.permissions_for(ctx.author).manage_channels
        if amount > 10 and not user_can_spam:
            amount= 10

        await self.imagemalkuth.send_random_pictures(ctx,library_name,amount,do_logging)


    @commands.command(description='''Completely reload one channels library.
                       Use as a last resort, some images might not register.''')
    async def reload_attachment_library(self,ctx):
        user_can_do_this = ctx.channel.permissions_for(ctx.author).manage_channels
        if user_can_do_this:
            await self.imagemalkuth.reload_attachment_library(ctx)
        else : 
            await   ctx.channel.send(parameters.wrongcommandmessage)
