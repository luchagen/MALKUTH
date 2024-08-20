# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:33:31 2023

@author: suric
"""
from discord.ext import commands
import txtmalk.malkuth as malkuth
import asyncio
import traceback

from threading import Semaphore

class malkcog(commands.Cog):
    lastresponse=None
    lastactivated=None
    sem=Semaphore(1)
    
    def __init__(self,bot,api_key):
        self.bot=bot
        self.api_key=api_key

    def initialize_lm(self):
        self.babamalk= malkuth.malkuth(3,100,0.9,3,20,True)
        
    def babamalkreply(self,message):
        self.sem.acquire()
        try:
            if message.clean_content[:7]== '@MALKUTH':
                reply=self.babamalk.generate_response(message.content[8:],
                                                      message.author.name,
                                                      message.guild.name,
                                                      message.channel.name)
            else :
                reply=self.babamalk.generate_response(message.content,
                                                      message.author.name,
                                                      message.guild.name,
                                                      message.channel.name)
                
            if reply[-4:] == '</s>':
                reply =reply[:-4]
            self.sem.release()
            return reply
        except AttributeError as e:
            self.sem.release()
            return (f''' Exception : {e}
                    The LM has not properly loaded. Check the state of the Petals network at health.petals.ml''',1.0,"no")
        except Exception as e :
            traceback.print_exc()
            return (f''' Exception : {e}
                    ''',1.0,"no")
            
    def babamalkfreeprompt(self,prompt):
        try:
            return self.babamalk.freeprompt(prompt)
        except AttributeError:
            return ("The LM has not properly loaded. Check the state of the Petals network at health.petals.ml")

    async def cog_load(self):
        await asyncio.get_running_loop().run_in_executor(None, self.initialize_lm)
        

    def wipeshorttermmemory(self):
        self.sem.acquire()
        self.babamalk.wipeshorttermmemory()
        self.sem.release() 


    @commands.Cog.listener()
    async def on_message(self,message):
        # we do not want the bot to reply to itself
        if message.author.id == self.bot.user.id:
            return

        if self.bot.user.mentioned_in(message):
            reply= await asyncio.get_running_loop().run_in_executor(None, self.babamalkreply,message)
            self.lastresponse=reply[0]
            self.lastactivated=reply[2]
            async with message.channel.typing():
                await message.reply(reply[0])


    @commands.command(description='Send forth malkuth to the lands of youtube. Uses malkuths recent memories (see wassup) as keywords for research.')
    async def malkuth_on_youtube(self,ctx, ytvideo: str=""):
        async with ctx.channel.typing():
            await ctx.send(self.babamalk.youtube_video(ytvideo))

    @commands.command(description='''Tell Malkuth how she must behave in this channel.
                    e.g. : You are Malkuth. your job is to answer question on a discord channel.''')
    async def system_prompt(self,ctx, prompt: str=""):
        self.babamalk.new_system_prompt(
            ctx.guild.name,
            ctx.channel.name,
            prompt)

        hello= await asyncio.get_running_loop().run_in_executor(
                None, self.babamalk.generate_response,
                        prompt,
                        ctx.author.name,
                        ctx.guild.name,
                        ctx.channel.name
                )
        async with ctx.channel.typing():
            await ctx.channel.send(prompt + '  ' + str(hello[0]))
            
    @commands.command(description='wipe malkuths short term memory')
    async def wipemalkuth(self,ctx):
        await asyncio.get_running_loop().run_in_executor(None, self.wipeshorttermmemory)
    
    
    @commands.command(description='debug')
    async def debug(self,ctx , command: str=''):
        if command == 'lastmemory':
            if self.lastactivated !=None:
                await ctx.channel.send(self.lastactivated)
        if command == 'lastmessage':
            if self.lastresponse!=None:
                await ctx.channel.send(self.lastresponse)

    @commands.command(description='unconstrained interaction with the language model')
    async def prompt(self,ctx, prompt: str):
        async with ctx.channel.typing():
            reply= await asyncio.get_running_loop().run_in_executor(None, self.babamalkfreeprompt,prompt)
            await ctx.send(reply)

    @commands.command(description='program (kinda) the response Malkuth would say to a (or a string of) question(s)')
    async def program(self,ctx, questions: str, answer: str):
        async with ctx.channel.typing():
            self.babamalk.program(questions,answer)
            await ctx.send(" :question: Malkuth will remember that.")
