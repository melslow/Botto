import os
import discord
from discord.ext import commands

ffmpeg_options = {
    "options": "-vn",
}

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def join_voice_channel(self, ctx):
        # Join the user's voice channel
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if not voice_client:
                return await channel.connect()
            elif voice_client.channel != channel:
                await voice_client.move_to(channel)
                return voice_client
            return voice_client
        else:
            await ctx.send("You need to be in a voice channel to use this command.")
            return None

    @commands.command(name="play")
    async def play(self, ctx, *, path: str):
        """
        Play an audio file from a direct URL or local file path.
        """
        voice_client = await self.join_voice_channel(ctx)
        if voice_client is None:
            return

        if not os.path.isfile(path) and not path.startswith("http"):
            await ctx.send("Please provide a valid file path or URL.")
            return

        async with ctx.typing():
            try:
                # Play the audio file
                source = discord.FFmpegPCMAudio(path, **ffmpeg_options)
                if not voice_client.is_playing():
                    voice_client.play(
                        source,
                        after=lambda e: print(f"Finished playing: {e if e else 'No errors'}")
                    )
                    await ctx.send(f"Now playing: {os.path.basename(path) if not path.startswith('http') else path}")
                else:
                    await ctx.send("A song is already playing! Stop it first with `!stop`.")
            except Exception as e:
                await ctx.send("An error occurred while trying to play the audio.")
                print(f"Play Error: {e}")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """
        Stop playing audio.
        """
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Playback stopped.")
        else:
            await ctx.send("No audio is currently playing.")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """
        Disconnect from the voice channel.
        """
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client:
            await voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not connected to a voice channel.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
