import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv  # Only needed if you use .env

# 1. Load environment variables (if using .env)
load_dotenv()  # Reads .env if it exists
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

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

# 5. Define which cogs to load on startup
COGS = ["sample_cog"]

@bot.event
async def on_ready():
    logging.info(f"Bot is online! Logged in as: {bot.user} (ID: {bot.user.id})")
    logging.info("------")

def main():
    # Load cogs
    for cog in COGS:
        try:
            bot.load_extension(f"cogs.{cog}")
            logging.info(f"Loaded cog: {cog}")
        except Exception as e:
            logging.error(f"Failed to load cog {cog}: {e}")

    # Run the bot
    if not TOKEN:
        logging.error("DISCORD_BOT_TOKEN environment variable not set.")
        return
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
