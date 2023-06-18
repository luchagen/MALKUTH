# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:06:12 2023

@author: suric
"""

from discord.ext import commands
import parameters
from datetime import datetime
from syncmalk import studiezsync
class syncog(commands.Cog):
    syncserver=parameters.sync_server
    syncchannels=parameters.sync_channels
    def __init__(self,bot):
        self.bot=bot
    
    async def cog_load(self):
        self.syncguild=await self.bot.fetch_guild(self.syncserver)
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author.id == self.bot.user.id:
            print("step1")
            mymessage=message.content.split(";>")
            
            if len(mymessage)==2:
                print("step2")
                if len(mymessage[0].split("|"))>=6:
                    print("step3")
                    message_attributes=mymessage[0].split("|")
                    print(message_attributes[3])
                    if message_attributes[3]==studiezsync.mirror_guild_id:
                        print("step4")
                        
                        channelid =message_attributes[2]
                        
                        if channelid in studiezsync.reversedserverdict.keys():
                            print("step5")   
                            
                            posted_message_id=""
                            
                            channel = self.bot.get_channel(studiezsync.reversedserverdict[channelid])
                            
                            posteremoji= self.bot.get_emoji(studiezsync.profilepicdict[message_attributes[0]])
                            
                            if message_attributes[5]!="0":
                                print("step6.2")
                                to_respond= await self.get_message_instanciated(channel,message_attributes[5])
                                posted_message= await to_respond.reply("<:"+posteremoji.name+":"+str(posteremoji.id)+"> says : "+mymessage[1])
                            else:  
                                print("step6.1")
                                posted_message= await channel.send("<:"+posteremoji.name+":"+str(posteremoji.id)+"> says : "+mymessage[1])
                            
                            posted_message_id=str(posted_message.id)
                            
                            await self.post_to_message_dict(message_attributes[4],posted_message_id)

            
        if message.author.id in self.syncchannels.keys():
            
            channel = self.bot.get_channel(self.syncchannels[message.author.id])
            
            ref="0"
            if message.reference != None:
                ref=message.reference.message_id
            
            syncmessage=str(message.author.id)+"|"+datetime.strftime(message.created_at,"%d/%m/%y %H:%M:%S")+"|"+str(message.channel.id)+"|"+str(message.guild.id)+"|"+str(message.id)+"|"+str(ref)+";>"+message.clean_content

            for thing in message.embeds:
                imgurl=""
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
                
                syncmessage += " " + imgurl
            for thing in message.attachments :
                syncmessage+= " " + thing.url
            await channel.send(syncmessage)
            
    @commands.command(description="completely reload one channels library. Use as a last resort, some images might not register.")
    async def reposteverything(self,ctx , areyousureaboutwhatyouredoing:str):
        if areyousureaboutwhatyouredoing=='I am not sure about what I am doing' :
            async for message in ctx.channel.history(limit=None):
                if message.author.id in self.syncchannels.keys():
                    channel = self.bot.get_channel(self.syncchannels[message.author.id])
                
                    syncmessage=str(message.author.id)+"|"+datetime.strftime(message.created_at,"%d/%m/%y %H:%M:%S")+"|"+str(message.channel.id)+"|"+str(message.guild.id)+";>"+message.content

                    for thing in message.embeds:
                        imgurl=""
                        if thing.url!=None:
                            imgurl=thing.url
                        if thing.thumbnail !=None and thing.thumbnail.proxy_url!=None:
                            imgurl=thing.thumbnail.proxy_url
                        if thing.image != None and thing.image.proxy_url!=None :
                                imgurl=thing.image.proxy_url
                        if thing.image != None and thing.image.url!=None :
                                imgurl=thing.image.url
                        if thing.thumbnail !=None and thing.thumbnail.url!=None :
                                imgurl=thing.thumbnail.url
                        syncmessage += " " + imgurl
                    for thing in message.attachments :
                        syncmessage+= " " + thing.url
                    await channel.send(syncmessage)
    
    async def get_message_instanciated(self,channel,message_id: str):
        serverdictchannel = self.bot.get_channel(studiezsync.message_dict_channel)
        async for message in serverdictchannel.history(limit=None):
            if message_id in message.content:
                if message_id== message.content.split("|")[0]:
                    to_return_message_id=message.content.split("|")[1]
                else:
                    to_return_message_id=message.content.split("|")[0]
                to_return_message=await channel.fetch_message(int(to_return_message_id))
                return to_return_message
        
    async def post_to_message_dict(self,original_message_id : str , instanciated_message_id: str):
        serverdictchannel = self.bot.get_channel(studiezsync.message_dict_channel)
        await serverdictchannel.send(original_message_id+"|"+instanciated_message_id)
            