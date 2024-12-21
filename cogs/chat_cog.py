import os
import openai
from discord.ext import commands
from dotenv import load_dotenv

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = openai.OpenAI(api_key=bot.config["OPENAI_API_KEY"])

    @commands.command(name="chat")
    async def chat(self, ctx, *, prompt: str):
        """
        Send a prompt to ChatGPT and return the response using the updated OpenAI API.
        """
        try:
            # Call the OpenAI ChatCompletion endpoint
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

            # Extract the assistant's reply
            reply = response.choices[0].message.content.strip()

            # Send the reply back to the Discord channel
            await ctx.send(reply)

        except Exception as e:
            await ctx.send("An unexpected error occurred.")
            print(f"Unexpected Error: {e}")

async def setup(bot):
    await bot.add_cog(ChatCog(bot))