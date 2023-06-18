# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:11:22 2023

@author: suric
"""
import discord
from discord.ext import commands
from discord import PCMVolumeTransformer
from discord.utils import get
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import parameters
import imagemalk.imagemalkcog as imagemalkcog
import txtmalk.malkuthcog as malkuthcog
import syncmalk.syncmalkcog as syncmalkcog
import asyncio




description = '''Malkuth has some plans to dominate the world.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='?', description=description, intents=intents)

# Initialize voice client variable
voice_client = None

# Define user ID to audio file path dictionary
user_audio_dict = {
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.add_cog(imagemalkcog.imgmalkcog(bot))
    await bot.add_cog(malkuthcog.malkcog(bot,parameters.youtube_api_key))
    await bot.add_cog(syncmalkcog.syncog(bot))
    
@bot.event    
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == bot.user.id:
        return
    await bot.process_commands(message)



# Define on_voice_state_update event
@bot.event
async def on_voice_state_update(member, before, after):
    global voice_client

    # Check to see if connecting to an after channel that is not the AFK channel
    if after.channel is not None and after.channel.id != 385892420660756480:
        # Check if member is the bot itself
        if member == bot.user:
            return

        # If bot is not already in a voice channel and member has joined a channel, connect to the channel
        if before.channel is None and after.channel is not None:
            voice_channel = after.channel
            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()

        # If bot is already in a voice channel and member has moved to a different channel, move the bot to the new channel
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            if voice_client is None:
                voice_client = await after.channel.connect()
            else:
                await voice_client.move_to(after.channel)

        # If bot is already in a voice channel and member has left the channel, disconnect the bot from the channel
        elif before.channel is not None and after.channel is None:
            # Check if voice client is connected and disconnect if it is
            if voice_client is not None and voice_client.is_connected():
                await voice_client.disconnect()
                voice_client = None
            # Reset voice client variable
            voice_client = None

        # Check if bot is connected to a voice channel and not already playing audio, and play audio if conditions are met
        if voice_client is not None and voice_client.is_connected() and voice_client.is_playing() == False:
            # Get user ID of member who triggered the bot
            user_id = str(member.id)
            # Check if user ID is in the dictionary and get audio file path
            if user_id in user_audio_dict:
                audio_file_path =  user_audio_dict[user_id]
            else:
                audio_file_path = "circus.wav"
            # Load audio file and play it
            audio_file = AudioSegment.from_file(audio_file_path, format=audio_file_path.split('.')[-1])
            audio_file.export("audio.wav", format="wav")
            audio_source = discord.FFmpegPCMAudio("audio.wav")
            await asyncio.sleep(1)
            voice_client.play(audio_source, after=lambda e: print('Player error: %s' % e) if e else None)
            while voice_client.is_playing():
                await asyncio.sleep(1)
            await voice_client.disconnect()
            voice_client = None

bot.run(parameters.discord_api_key)