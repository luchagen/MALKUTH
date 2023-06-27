# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:06:12 2023

@author: suric
"""
import sqlite3 as sl
from discord.ext import commands
from discord import Webhook
from discord import MessageType
import parameters
from datetime import datetime
from syncmalk import studiezsync
import aiohttp
class syncog(commands.Cog):
    syncserver=parameters.sync_server
    syncchannels=parameters.sync_channels
    def __init__(self,bot):
        self.bot=bot
        self.MEMORYSYNC =  sl.connect('serversync.db', check_same_thread=False)
        testexists=self.MEMORYSYNC.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='channels'").fetchall()
        if len(testexists)<1:
            self.MEMORYSYNC.execute("""CREATE TABLE channels (
            channel_id  INTEGER  PRIMARY KEY,
            guild_id   INTEGER,
            webhook_id  INTEGER,
            webhook_token  TEXT)""")
            self.MEMORYSYNC.commit()
    
    async def get_emoj(self,emojiname):
        for emoj in self.bot.emojis:
            if emoj.name== emojiname.replace(':',''):
                return '<:'+emoj.name+':'+str(emoj.id)+'>'
        return emojiname
    async def cog_load(self):
        self.syncguild=await self.bot.fetch_guild(self.syncserver)
        self.mirrorguild = await self.bot.fetch_guild(int(studiezsync.mirror_guild_id))
        self.primaryguild = await self.bot.fetch_guild(int(studiezsync.primary_guild_id))
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
                    #if message_attributes[3]==studiezsync.mirror_guild_id:
                        print("step4")
                        
                        channelid =message_attributes[2]
                        
                        if channelid in studiezsync.completeserverdict.keys():
                            print("step5")   
                            
                            posted_message_id=""
                            
                            homechannel=self.bot.get_channel(int(channelid))
                            channel = self.bot.get_channel(studiezsync.reversedserverdict[channelid])
                            endchannel_id=studiezsync.reversedserverdict[channelid]
                            if message_attributes[5]!="0":
                                print("step6.2")
                                posteremoji= self.bot.get_emoji(studiezsync.profilepicdict[message_attributes[0]])
                            
                                to_respond= await self.get_message_instanciated(channel,message_attributes[5])
                                posted_message= await to_respond.reply("<:"+posteremoji.name+":"+str(posteremoji.id)+"> says : "+mymessage[1])
                            
                            else:
                                    mywebhook= 3    
                                    webhooks=self.MEMORYSYNC.execute("SELECT webhook_id, webhook_token FROM channels WHERE channel_id = (?)",(endchannel_id,)).fetchall()  
                                    #for webhook in webhooks :
                                        # print("zewebhook")
                                        # print(webhook.user.name)
                                        # print(webhook.channel.name)
                                        # if webhook.user == self.bot and webhook.channel_id == channel.id:
                                        #     mywebhook = webhook
                                    if len(webhooks)==0:
                                        mywebhook=await channel.create_webhook(name="malk"+channel.name) #name="malk"+channel.name,avatar=self.bot.user.avatar,reason="sync"
                                        try:
                                            self.MEMORYSYNC.execute("INSERT INTO channels (channel_id,guild_id,webhook_id,webhook_token) values (?,?,?,?) ", (endchannel_id,int(message_attributes[3]),mywebhook.id,mywebhook.token))
                                        except:
                                            self.MEMORYSYNC.rollback()
                                            raise Exception("error when trying to put channel key : "+ str(endchannel_id) + " into the database")
                                        self.MEMORYSYNC.commit()
                                        webhookid=mywebhook.id
                                        webhooktoken=mywebhook.token
                                        
                                    else:
                                        webhookid=webhooks[0][0]
                                        webhooktoken=webhooks[0][1]
                                    user = await homechannel.guild.fetch_member(int(message_attributes[0]))
                                    async with aiohttp.ClientSession() as client:
                                        try:
                                            webhook = Webhook.partial(webhookid, webhooktoken, session=client,bot_token=(parameters.discord_api_key))
                                            posted_message=await webhook.send(mymessage[1], username = user.nick or user.name, avatar_url = user.avatar.url,wait=True)
                                        except:
                                            mywebhook=await channel.create_webhook(name="malk"+channel.name) #name="malk"+channel.name,avatar=self.bot.user.avatar,reason="sync"
                                            try:
                                                self.MEMORYSYNC.execute("UPDATE channels set webhook_id = ? ,webhook_token = ? WHERE channel_id= ? ", (mywebhook.id,mywebhook.token,endchannel_id))
                                            except:
                                                self.MEMORYSYNC.rollback()
                                                raise Exception("error when trying to update channel key : "+ str(endchannel_id) + " into the database")
                                            self.MEMORYSYNC.commit()
                                            webhookid=mywebhook.id
                                            webhooktoken=mywebhook.token
                                            webhook = Webhook.partial(webhookid, webhooktoken, session=client,bot_token=(parameters.discord_api_key))
                                            posted_message=await webhook.send(mymessage[1], username = user.nick or user.name, avatar_url = user.avatar.url,wait=True)
                                        
                            posted_message_id=str(posted_message.id)
                            await self.post_to_message_dict(message_attributes[4],posted_message_id)

        
        elif message.content.count(':') == 2 and message.content[0]==':' and message.content[-1]==':' and message.type.value!=19 and message.author.id in self.syncchannels.keys():
            mywebhook= 3    
            webhooks=self.MEMORYSYNC.execute("SELECT webhook_id, webhook_token FROM channels WHERE channel_id = (?)",(message.channel.id,)).fetchall()  
            #for webhook in webhooks :
                # print("zewebhook")
                # print(webhook.user.name)
                # print(webhook.channel.name)
                # if webhook.user == self.bot and webhook.channel_id == channel.id:
                #     mywebhook = webhook
            if len(webhooks)==0:
                mywebhook=await message.channel.create_webhook(name="malk"+message.channel.name) #name="malk"+channel.name,avatar=self.bot.user.avatar,reason="sync"
                try:
                    self.MEMORYSYNC.execute("INSERT INTO channels (channel_id,guild_id,webhook_id,webhook_token) values (?,?,?,?) ", (message.channel.id,message.guild.id,mywebhook.id,mywebhook.token))
                except:
                    self.MEMORYSYNC.rollback()
                    raise Exception("error when trying to put channel key : "+ str(message.channel.id) + " into the database")
                self.MEMORYSYNC.commit()
                webhookid=mywebhook.id
                webhooktoken=mywebhook.token
                
            else:
                webhookid=webhooks[0][0]
                webhooktoken=webhooks[0][1]
            user = await message.guild.fetch_member(message.author.id)
            async with aiohttp.ClientSession() as client:
                try:
                    webhook = Webhook.partial(webhookid, webhooktoken, session=client,bot_token=(parameters.discord_api_key))
                    posted_message=await webhook.send(await self.get_emoj(message.content), username = user.nick or user.name, avatar_url = user.avatar.url,wait=True)
                except:
                    mywebhook=await message.channel.create_webhook(name="malk"+message.channel.name) #name="malk"+channel.name,avatar=self.bot.user.avatar,reason="sync"
                    try:
                        self.MEMORYSYNC.execute("UPDATE channels set webhook_id = ? ,webhook_token = ? WHERE channel_id= ? ", (mywebhook.id,mywebhook.token,message.channel.id))
                    except:
                        self.MEMORYSYNC.rollback()
                        raise Exception("error when trying to update channel key : "+ message.channel.id + " into the database")
                    self.MEMORYSYNC.commit()
                    webhookid=mywebhook.id
                    webhooktoken=mywebhook.token
                    webhook = Webhook.partial(webhookid, webhooktoken, session=client,bot_token=(parameters.discord_api_key))
                    posted_message=await webhook.send(await self.get_emoj(message.content), username = user.nick or user.name, avatar_url = user.avatar.url,wait=True)
            await message.delete()
            
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
                if thing.url[:24]!="https://media.tenor.com/":
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
            