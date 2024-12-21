import discord
from discord.ext import commands

class SampleCog(commands.Cog):
    """A sample cog with basic commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping_command(self, ctx: commands.Context):
        """A simple ping command."""
        await ctx.send("Pong!")

    @commands.command(name="echo")
    async def echo_command(self, ctx: commands.Context, *, message: str):
        """Echoes the message back to the user."""
        await ctx.send(message)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Don't respond to the bot's own messages
        if message.author == self.bot.user:
            return
        # You could add custom logic here

def setup(bot: commands.Bot):
    bot.add_cog(SampleCog(bot))
