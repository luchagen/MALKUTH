# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:06:12 2023

@author: suric
"""
import re
import sqlite3 as sl
from syncmalk import studiezsync
from discord.ext import commands
from discord import Webhook
from discord import Thread
import parameters
from datetime import datetime
from syncmalk import studiezsync
from imagemalk  import attachmentutils
import aiohttp
class syncog(commands.Cog):
    syncserver=parameters.sync_server
    syncchannels=parameters.sync_channels
    def __init__(self,bot):
        self.bot=bot

        #initialize channels table (for webhooks)
        self.MEMORYSYNC =  sl.connect('serversync.db', check_same_thread=False)
        testexists=self.MEMORYSYNC.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='channels'").fetchall()
        if len(testexists)<1:
            self.MEMORYSYNC.execute("""CREATE TABLE channels (
            channel_id  INTEGER  PRIMARY KEY,
            guild_id   INTEGER,
            webhook_id  INTEGER,
            webhook_token  TEXT)""")
            self.MEMORYSYNC.commit()
        
        #initialize mirrors table (for synchronization)
        testexists=self.MEMORYSYNC.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mirrors'").fetchall()
        if len(testexists)<1:
            self.MEMORYSYNC.execute("""CREATE TABLE mirrors (
            mirror_id  INTEGER  PRIMARY KEY,  
            channel_id  INTEGER,
            mirror_channel_id  INTEGER)""")
            
            self.MEMORYSYNC.executemany("""INSERT INTO mirrors(channel_id,mirror_channel_id) 
            values (?,?) """, [item for item in studiezsync.completeserverdict.items()])
            self.MEMORYSYNC.commit()

        self.emojipattern=re.compile(";[A-Za-z0-9]+;")
    
    def get_emoj(self,emojimatch: re.Match):
        """
        searches though all emojis the bot has access to for one that satisfies the input name
        """
        emojiname=emojimatch.group(0)
        for emoj in self.bot.emojis:
            if emoj.name== emojiname.replace(';',''):
                return '<:'+emoj.name+':'+str(emoj.id)+'>'
        return emojiname
    
    def get_listened_channels(self):
        qresults=self.MEMORYSYNC.execute("SELECT channel_id FROM mirrors").fetchall()
        results=[result[0] for result in qresults]
        return results
    
    def get_channel_mirrors(self,channel_id):
        qresults=self.MEMORYSYNC.execute("SELECT mirror_channel_id FROM mirrors WHERE channel_id=?",[channel_id]).fetchall()
        results = [result[0] for result in qresults]
        return results
    
    #def replaceEmojisInMessage(self,message:str):
        #replacing= True
        
        #while replacing:
        #    emojmatch = self.emojipattern.search(message)  
        #    emoj=emojmatch.group(0)
            


    async def cog_load(self):
        """
        Is called when this cog is loaded, cog equivalent to on_ready() 
        """
        self.syncguild=await self.bot.fetch_guild(self.syncserver)
        self.mirrorguild = await self.bot.fetch_guild(int(studiezsync.mirror_guild_id))
        self.primaryguild = await self.bot.fetch_guild(int(studiezsync.primary_guild_id))
    
    async def getOrCreateWebhookForChannel(self,channel):
        """
        Used to get a webhook's credential from memory for a given channel, or create a new webhook and then insert it into the sqlite db used for that purpose.
        This was found to be more reliable than getting the credentials back from discord api each time.
        """
        thread=None
        if isinstance(channel,Thread):
            thread=channel
            channel = channel.parent #if thread or forum post, we get the parent channel
        webhooks=self.MEMORYSYNC.execute("SELECT webhook_id, webhook_token FROM channels WHERE channel_id = (?)",(channel.id,)).fetchall() 
        if len(webhooks)==0:
                mywebhook=await channel.create_webhook(name="malk"+channel.name) #name="malk"+channel.name,avatar=self.bot.user.avatar,reason="sync"
                try:
                    self.MEMORYSYNC.execute("INSERT INTO channels (channel_id,guild_id,webhook_id,webhook_token) values (?,?,?,?) ", (channel.id,channel.guild.id,mywebhook.id,mywebhook.token))
                except:
                    self.MEMORYSYNC.rollback()
                    raise Exception("error when trying to put channel key : "+ str(channel.id) + " into the database")
                self.MEMORYSYNC.commit()

                return(mywebhook.id,mywebhook.token)
        else:
                return(webhooks[0][0],webhooks[0][1])

    def UpdateDBForWebhook(self,webhookid: int,webhooktoken: str,channelid: int):
        """
        Used to update a webhook's credential on the sqlite db used for that purpose.
        """
        try:
            self.MEMORYSYNC.execute("UPDATE channels set webhook_id = ? ,webhook_token = ? WHERE channel_id= ? ", (webhookid,webhooktoken,channelid))
        except:
            self.MEMORYSYNC.rollback()
            raise Exception("error when trying to update channel key : "+ str(channelid) + " into the database")
        self.MEMORYSYNC.commit()

    async def PostMessageToWebHook(self,channel,webhookid: int, webhooktoken: str, message : str, user):
        """
        Used to push a message to a discord channel's webhook, create back if it is not reachable/doesn't exist anymore.
        """
        thread=None
        if isinstance(channel,Thread):
            thread=channel
            channel = channel.parent #if thread or forum post, we get the parent channel
        avatar_url=user.avatar.url
        try:
            username = user.nick or user.name
        except:
            username = user.name
        async with aiohttp.ClientSession() as client:
            try:
                webhook = Webhook.partial(webhookid, webhooktoken, session=client,bot_token=(parameters.discord_api_key))
                if not thread:
                    posted_message=await webhook.send(message, username=username , avatar_url=avatar_url,wait=True)
                else : # if the target is a thread / forum post , specify it in the send request
                    posted_message=await webhook.send(message, username=username , avatar_url=avatar_url,wait=True,thread=thread)
            except: #we assume sending the message failed because the old webhook was faulty / did not exist anymore
                mywebhook=await channel.create_webhook(name="malk"+channel.name) #name="malk"+channel.name,avatar=self.bot.user.avatar,reason="sync"
                self.UpdateDBForWebhook(mywebhook.id,mywebhook.token,channel.id)
                webhookid=mywebhook.id
                webhooktoken=mywebhook.token
                webhook = Webhook.partial(webhookid, webhooktoken, session=client,bot_token=(parameters.discord_api_key))
                if not thread:
                    posted_message=await webhook.send(message, username=username , avatar_url=avatar_url,wait=True)
                else : # if the target is a thread / forum post , specify it in the send request
                    posted_message=await webhook.send(message, username=username , avatar_url=avatar_url,wait=True,thread=thread)
            return posted_message

    @commands.Cog.listener()
    async def on_message(self,message):

        if message.webhook_id!=None: #we do not want to modify or sync messages that were already sent by a webhook
            return

        print(message.channel.id in self.get_listened_channels())
        if message.channel.id in self.get_listened_channels():
            
            """If the message is sent in a channel meant to be synced, publish that message in the linked mirror channel"""
            mirror_channels = self.get_channel_mirrors(message.channel.id)
            
            
            #edit the message content
            if self.emojipattern.search(message.clean_content): #replace emojis in message
                syncmessage = self.emojipattern.sub(self.get_emoj,message.clean_content)
            else :
                syncmessage= message.clean_content
            
            attachments=attachmentutils.getMessageAttachments(message)
            embeds=attachmentutils.getMessageEmbeds(message)
            if attachments :
                syncmessage+= " \n " + str(attachments)
            #elif embeds :
            #    syncmessage+= " \n " + str(embeds)
            
            
            for mirror_channel_id in mirror_channels:
                mirror_channel = self.bot.get_channel(mirror_channel_id)
                replymessage=""

                if message.reference != None: #message is a reply, add reply elements
                    to_respond= await self.get_message_instanciated(mirror_channel,str(message.reference.message_id))
                    replymessage += to_respond.jump_url + " \n"
                    replymessage += "<@"+str(to_respond.author.id)+">"
                (webhookid, webhooktoken) = await self.getOrCreateWebhookForChannel(mirror_channel)    
            
                user = message.author

                if replymessage:
                    await self.PostMessageToWebHook(mirror_channel,webhookid, webhooktoken, replymessage, user)
                if syncmessage:
                    posted_message=await self.PostMessageToWebHook(mirror_channel,webhookid, webhooktoken, syncmessage, user)
                    posted_message_id=str(posted_message.id)
                    await self.post_to_message_dict(str(message.id),str(posted_message_id))

        
        if self.emojipattern.search(message.content) : #replace emojis in message if it contains ;emojiname; words
            if len(message.attachments)!=0: return
                
            print(str(message.attachments))
            syncmessage = self.emojipattern.sub(self.get_emoj,message.content)
            if syncmessage ==  message.content: return
            replymessage=""
            if message.reference != None: #message is a reply, add reply elements
                to_respond= message.reference
                replymessage += to_respond.jump_url + " \n"
                if to_respond.resolved!=None:
                    replymessage += "<@"+str(to_respond.resolved.author.id)+">"

            (webhookid, webhooktoken) = await self.getOrCreateWebhookForChannel(message.channel)    
            
            user = message.author

            if replymessage !="":
                await self.PostMessageToWebHook(message.channel,webhookid, webhooktoken, replymessage, user)
            newmessage=await self.PostMessageToWebHook(message.channel,webhookid, webhooktoken, syncmessage, user)
            
            #if the message has a reference in the message reference dictionary, update it.
            if message.channel.id in self.get_listened_channels():
                await self.modify_message_dict(str(message.id), str(newmessage.id))
            
            await message.delete()

    @commands.command(description="Create a mirror channel, every (non webhook) message from input channel id will be mirrored to this channel")
    async def synchronize_mirror(self,ctx,channel_id):
        try:
            self.MEMORYSYNC.execute("""INSERT INTO mirrors(channel_id,mirror_channel_id) VALUES (?,?)""", [channel_id,ctx.channel.id])
        except Exception as e:
            print(e)
            await ctx.channel.send(e)
        else:
            self.MEMORYSYNC.commit()
            original_channel = self.bot.get_channel(int(channel_id))
            await original_channel.send("channel "+str(ctx.channel.id)+" from guild "+
                                        ctx.guild.name+" will now mirror messages from "+str(channel_id))

    @commands.command(description="Delete a mirror synchronizing from this channel")
    async def delete_mirror(self,ctx,channel_id):
        try:
            self.MEMORYSYNC.execute("""DELETE FROM mirrors WHERE channel_id=? and mirror_channel_id=?""",[ctx.channel.id,channel_id])
        except Exception as e:
            print(e)
            await ctx.channel.send(e)
        else:
            self.MEMORYSYNC.commit()
            mirror_channel = self.bot.get_channel(int(channel_id))
            await mirror_channel.send("This channel ("+mirror_channel.name +':'+str(mirror_channel.id)+
                                      ") will stop mirroring messages from "+ctx.channel.name)
            await ctx.channel.send("Stopped " + mirror_channel.name +" ("+ 
                                   str(mirror_channel.id) + 
                                   ") from mirroring messages from this channel ("+
                                   ctx.channel.name+ ':' +str(ctx.channel.id) +")" )


    @commands.command(description="completely reload one channels library. Use as a last resort, some images might not register.")
    async def reposteverything(self,ctx , areyousureaboutwhatyouredoing:str=""):
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
        else : 
            await   ctx.channel.send(parameters.wrongcommandmessage)
    
    async def get_message_instanciated(self,channel,message_id: str):
        """
        Get the instance of the message on the other side of the mirror from the one we already have an id for
        can be used to then keep the same message relationships (eg. message/response) on the mirror channel
        """
        serverdictchannel = self.bot.get_channel(studiezsync.message_dict_channel)
        async for message in serverdictchannel.history(limit=None):
            if message_id in message.content:
                if message_id== message.content.split("|")[0]:
                    to_return_message_id=message.content.split("|")[1]
                else:
                    to_return_message_id=message.content.split("|")[0]
                to_return_message=await channel.fetch_message(int(to_return_message_id))
                return to_return_message

    async def modify_message_dict(self,original_message_id:str, new_message_id:str):
        """
        Edit the entry in the message dictionary when we change a message
        """
        serverdictchannel = self.bot.get_channel(studiezsync.message_dict_channel)
        async for message in serverdictchannel.history(limit=None):
            if original_message_id in message.content:
                if original_message_id== message.content.split("|")[0]:
                    linked_message_id=message.content.split("|")[1]
                    edited_message = new_message_id + "|"+linked_message_id 
                else:
                    linked_message_id=message.content.split("|")[0]
                    edited_message = linked_message_id + "|"+ new_message_id 
                await message.edit(content=edited_message)
                return
                

    async def post_to_message_dict(self,original_message_id : str , instanciated_message_id: str):
        """
        post to a dedicated message dictionary discord channel.
        message ids are linked to the message ids of their synchronized message"""
        serverdictchannel = self.bot.get_channel(studiezsync.message_dict_channel)
        await serverdictchannel.send(original_message_id+"|"+instanciated_message_id)
            