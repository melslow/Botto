import discord
from discord.ext import commands
from gtts import gTTS
import os

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_cache = "tts_audio.mp3"  # Temporary file for TTS audio

    @commands.command(name="tts")
    async def tts(self, ctx, *, text: str):
        """
        Converts text to speech and plays it in the user's voice channel.
        """
        # Check if the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use TTS!")
            return
        
        # Convert text to speech
        try:
            tts = gTTS(text=text, lang="en")
            tts.save(self.audio_cache)
        except Exception as e:
            await ctx.send("Failed to generate TTS audio.")
            return

        # Connect to the user's voice channel
        voice_channel = ctx.author.voice.channel
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        
        try:
            if vc and vc.is_connected():
                await vc.move_to(voice_channel)
            else:
                vc = await voice_channel.connect()
        except Exception as e:
            await ctx.send("Failed to connect to the voice channel.")
            return

        # Play the audio file
        try:
            vc.play(discord.FFmpegPCMAudio(self.audio_cache), after=lambda e: os.remove(self.audio_cache))
            vc.source = discord.PCMVolumeTransformer(vc.source, volume=1.0)
            await ctx.send(f"Playing TTS audio: '{text}'")
        except Exception as e:
            await ctx.send("Failed to play the TTS audio.")
            if os.path.exists(self.audio_cache):
                os.remove(self.audio_cache)

async def setup(bot):
    await bot.add_cog(TTSCog(bot))
