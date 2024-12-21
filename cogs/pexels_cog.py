import discord
from discord.ext import commands
import aiohttp
import random

class PexelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = bot.config["PEXELS_API_KEY"]  # Replace with your Pexels API key
        self.search_url = "https://api.pexels.com/v1/search"

    async def fetch_image(self, prompt):
        """
        Fetches a random image URL from Pexels based on a search prompt.
        """
        headers = {"Authorization": self.api_key}
        params = {"query": prompt, "per_page": 15}  # Limit to 15 results per query
        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    photos = data.get("photos", [])
                    if photos:
                        return random.choice(photos).get("src", {}).get("large")  # Get a random image
                return None

    @commands.command(name="image")
    async def get_image(self, ctx, *, prompt):
        """
        Fetches a random image from Pexels based on the user's prompt.
        """
        await ctx.send("Searching for an image, please wait...")
        image_url = await self.fetch_image(prompt)
        if image_url:
            embed = discord.Embed(title=f"Here's a random image for '{prompt}':")
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Sorry, I couldn't find any images for '{prompt}'.")

async def setup(bot):
    await bot.add_cog(PexelsCog(bot))
