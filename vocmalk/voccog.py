import discord
import asyncio
from discord.ext import commands
from pydub import AudioSegment
import parameters
voice_client = None
class voccog(commands.Cog):
    
    # Initialize voice client variable
    def __init__(self,bot):
        self.bot = bot

    # Define user ID to audio file path dictionary
        self.user_audio_dict = parameters.audio_dict

    async def check_if_connected_to_voice(self,channel):
        if channel:
            for voiceconnection in self.bot.voice_clients:
                if  voiceconnection.guild == channel.guild:
                    return voiceconnection
        return None
    
    async def play_welcome_sound(self,member,after):
        voice_client = await self.check_if_connected_to_voice(after.channel)
        if voice_client.is_playing() == False:
                # Get user ID of member who triggered the bot
                user_id = str(member.id)
                # Check if user ID is in the dictionary and get audio file path
                if user_id in self.user_audio_dict:
                    audio_file_path =  self.user_audio_dict[user_id]
                else:
                    audio_file_path = "circus.wav"
                # Load audio file and play it
                audio_file = AudioSegment.from_file(audio_file_path, format=audio_file_path.split('.')[-1])
                audio_file.export("audio.wav", format="wav")
                audio_source = discord.FFmpegPCMAudio("audio.wav")
                audio_source = discord.PCMVolumeTransformer(audio_source,volume=0.2)
                await asyncio.sleep(1)
                voice_client.play(audio_source, after=lambda e: print('Player error: %s' % e) if e else None)
                while voice_client.is_playing():
                    await asyncio.sleep(1)
                await voice_client.disconnect()
                voice_client = None

    # Define on_voice_state_update event
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global voice_client
        
        if after.channel and str(member.id) in self.user_audio_dict and before.channel!=after.channel :
            print(str(after.channel))
            # Check if member is the bot itself
            if member == self.bot.user:
                return

        # connect to the relevant channel on member join


            voice_channel = after.channel
            voice_client = await self.check_if_connected_to_voice(after.channel)
            if voice_client is None:
                voice_client = await voice_channel.connect()
            else:
                await voice_client.move_to(after.channel) 
            await self.play_welcome_sound(member,after)

        # leave channel when member leaves
        elif before.channel and not after.channel:
                # Check if voice client is connected and disconnect if it is
                voice_client = await self.check_if_connected_to_voice(before.channel)
                if voice_client:
                    await voice_client.disconnect()
                    voice_client = None
                # Reset voice client variable
                voice_client = None

            