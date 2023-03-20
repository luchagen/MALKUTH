# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:33:31 2023

@author: suric
"""
from discord.ext import commands
import malkuth
import asyncio
import http.client
import json 

class malkcog(commands.Cog):
    lastresponse=None
    
    def __init__(self,bot,api_key):
        self.bot=bot
        self.api_key=api_key

    def initialize_lm(self):
        self.babamalk= malkuth.malkuth(3,100,0.9,3,20,True)

    def babamalkreply(self,message):
        try:
            if message.content[:7]== '@MALKUTH':
                reply=self.babamalk.generate_response(message.content[8:],message.author.name)
            elif message.content[:22] == '<@1068268891580682293>':
                reply=self.babamalk.generate_response(message.content[22:],message.author.name)
            else :
                reply=self.babamalk.generate_response(message.content,message.author.name)
                
            if reply[0][-4:] == '</s>':
                reply[0] =reply[0][:-4]
            return reply
        except AttributeError:
            return ("The LM has not properly loaded. Check the state of the Petals network at health.petals.ml",1.0)

    def babamalkfreeprompt(self,prompt):
        try:
            return self.babamalk.freeprompt(prompt)
        except AttributeError:
            return ("The LM has not properly loaded. Check the state of the Petals network at health.petals.ml")

    async def cog_load(self):
        await asyncio.get_running_loop().run_in_executor(None, self.initialize_lm)
        
    @commands.Cog.listener()
    async def on_message(self,message):
        # we do not want the bot to reply to itself
        if message.author.id == self.bot.user.id:
            return
        if self.bot.user.mentioned_in(message):
            async with message.channel.typing():
                reply= await asyncio.get_running_loop().run_in_executor(None, self.babamalkreply,message)
                self.lastresponse=reply[0]
                await message.channel.send(reply[0])
                
    @commands.command(description='Send forth malkuth to the lands of youtube. Uses malkuths recent memories (see wassup) as keywords for research.')
    async def malkuth_on_youtube(self,ctx, ytvideo: str=""):
        async with ctx.channel.typing():
            await ctx.send(self.youtube_video(ytvideo))
            
    @commands.command(description='debug')
    async def debug(self,ctx , command: str=''):
        if command == 'lastmessage' or command =='':
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

    async def youtube_video(self,link=""):
        conn = http.client.HTTPSConnection("yt-api.p.rapidapi.com")
        if link=="":
            rsrch=b""
            if self.lastresponse!=None:
                rsrch+=self.lastresponse.encode("ascii","ignore")
            research=b'/search?query='+rsrch+b'&pretty=1'
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': "yt-api.p.rapidapi.com"
            }
            
            conn.request("GET", research.decode("ascii"), headers=headers)
            
            res = conn.getresponse()
            data = res.read()
            jsonised=json.loads(data)
            return("https://youtu.be/"+jsonised["data"][0]["videoId"]+self.scentgen.free_text_gen(jsonised["data"][0]["title"]))
        
            
        else:
            while link.find("/")!=-1:
                link=link[link.find("/")+1:]
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': "yt-api.p.rapidapi.com"
            }
            conn.request("GET", "/video?id="+link, headers=headers)
            res = conn.getresponse()
            data = res.read()
            jsonised=json.loads(data)
            return ("https://youtu.be/"+jsonised["id"]+self.scentgen.free_text_gen(jsonised["title"]))