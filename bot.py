import asyncio
import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv  # Only needed if you use .env

# 1. Load environment variables (if using .env)
load_dotenv()  # Reads .env if it exists
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# 2. Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s"
)

# 3. Configure intents
intents = discord.Intents.default()
intents.message_content = True

# 4. Initialize bot with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)
bot.config = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "PEXELS_API_KEY": PEXELS_API_KEY,
}


# 5. Define which cogs to load on startup
COGS = ["lingo_cog",'chat_cog','music_cog','pexels_cog', "tts_cog"]

@bot.event
async def on_ready():
    logging.info(f"Bot is online! Logged in as: {bot.user} (ID: {bot.user.id})")
    logging.info("------")
    for guild in bot.guilds:
        logging.info("Joined: {}, Guild_id: {}".format(guild,guild.id))
        await bot.tree.sync(guild=discord.Object(id=guild.id))

async def main():
    # Load cogs
    for cog in COGS:
        try:
            await bot.load_extension(f"cogs.{cog}")
            logging.info(f"Loaded cog: {cog}")
        except Exception as e:
            logging.error(f"Failed to load cog {cog}: {e}")

    # Run the bot
    if not TOKEN:
        logging.error("DISCORD_BOT_TOKEN environment variable not set.")
        return
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())