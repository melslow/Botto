import discord
from discord.ext import commands
import aiohttp
import os
from openai import OpenAI

# Riot API setup
RIOT_API_KEY = os.getenv("RIOT_API_KEY")  # Store your API key securely
BASE_URL = "https://euw1.api.riotgames.com"
REGION = "europe"  # Adjust region as needed
ACCOUNT_BASE_URL = "https://europe.api.riotgames.com"


# OpenAI API setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Store your OpenAI API key securely

class TFTStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    
        response = self.openai_client.chat.completions.create(
            messages=[{"role": "system", "content": "You are an expert at summarizing data."}, {"role": "user", "content": prompt}],
            model="gpt-4o-mini"
        )
    
        return response.choices[0].message.content

    @commands.command()
    async def tftstats(self, ctx, game_name: str, tag_line: str):
        """Fetch the latest 5 TFT matches for a given Riot ID."""
        # Step 1: Get Account Data Using Riot ID
        account_url = f"{ACCOUNT_BASE_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        account_data = await self.fetch_data(account_url)

        if not account_data:
            await ctx.send(f"Could not find account with Riot ID: {game_name}#{tag_line}")
            return

        puuid = account_data.get("puuid")

        # Step 2: Get Match History
        match_url = f"https://{REGION}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=5"
        match_ids = await self.fetch_data(match_url)

        if not match_ids:
            await ctx.send(f"Could not retrieve matches for Riot ID: {game_name}#{tag_line}")
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

            embed = discord.Embed(title=f"Latest TFT Matches for Riot ID: {game_name}#{tag_line}", color=discord.Color.blue())
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
            await ctx.send(f"No match details available for Riot ID: {game_name}#{tag_line}")

# Setup bot
async def setup(bot):
    await bot.add_cog(TFTStats(bot))
