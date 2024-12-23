import discord
from discord.ext import commands
import aiohttp
import os
import openai

# Riot API setup
RIOT_API_KEY = os.getenv("RIOT_API_KEY")  # Store your API key securely
BASE_URL = "https://euw1.api.riotgames.com"
REGION = "europe"  # Adjust region as needed

# OpenAI API setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Store your OpenAI API key securely
openai.api_key = OPENAI_API_KEY

class TFTStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_data(self, url):
        """Fetch data from Riot API."""
        headers = {"X-Riot-Token": RIOT_API_KEY}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

    async def generate_summary(self, results):
        """Generate a summary using OpenAI GPT model."""
        prompt = (
            """
            Generate a concise summary for the following TFT match results. Each match contains placement, traits, and the last round eliminated. Summarize the overall performance and patterns:
            {results}
            """
        ).format(results=results)

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert at summarizing data."}, {"role": "user", "content": prompt}]
        )

        return response["choices"][0]["message"]["content"]

    @commands.command()
    async def tftstats(self, ctx, summoner_name):
        """Fetch the latest 5 TFT matches for a given summoner."""
        # Step 1: Get Summoner ID
        summoner_url = f"{BASE_URL}/lol/summoner/v4/summoners/by-name/{summoner_name}"
        summoner_data = await self.fetch_data(summoner_url)

        if not summoner_data:
            await ctx.send(f"Could not find summoner: {summoner_name}")
            return

        summoner_id = summoner_data.get("id")
        puuid = summoner_data.get("puuid")

        # Step 2: Get Match History
        match_url = f"https://{REGION}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=5"
        match_ids = await self.fetch_data(match_url)

        if not match_ids:
            await ctx.send(f"Could not retrieve matches for summoner: {summoner_name}")
            return

        # Step 3: Fetch Match Details
        results = []
        for match_id in match_ids:
            match_url = f"https://{REGION}.api.riotgames.com/tft/match/v1/matches/{match_id}"
            match_data = await self.fetch_data(match_url)

            if match_data:
                # Extract data for the summoner
                participants = match_data.get("info", {}).get("participants", [])
                player_data = next((p for p in participants if p.get("puuid") == puuid), None)

                if player_data:
                    placement = player_data.get("placement")
                    traits = [trait["name"] for trait in player_data.get("traits", []) if trait.get("tier_current", 0) > 0]
                    round_eliminated = player_data.get("last_round")

                    results.append({
                        "placement": placement,
                        "traits": traits,
                        "round_eliminated": round_eliminated
                    })

        # Step 4: Generate and Send Summary
        if results:
            summary = await self.generate_summary(results)

            embed = discord.Embed(title=f"Latest TFT Matches for {summoner_name}", color=discord.Color.blue())
            embed.add_field(name="Performance Summary", value=summary, inline=False)

            for idx, result in enumerate(results, start=1):
                match_details = (
                    f"**Match {idx}**\n"
                    f"Placement: {result['placement']}\n"
                    f"Traits: {', '.join(result['traits']) if result['traits'] else 'None'}\n"
                    f"Last Round: {result['round_eliminated']}"
                )
                embed.add_field(name=f"Match {idx}", value=match_details, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No match details available for summoner: {summoner_name}")

# Setup bot
async def setup(bot):
    await bot.add_cog(TFTStats(bot))
