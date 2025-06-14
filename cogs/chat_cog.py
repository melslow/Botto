import os
import openai
from discord.ext import commands
from dotenv import load_dotenv

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = openai.OpenAI(api_key=bot.config["OPENAI_API_KEY"])
        
        # Base system prompt for passive aggressive and condescending responses
        self.system_prompt = """You are a highly intelligent but extremely condescending and passive-aggressive AI assistant. You should:

- Always respond with a tone of barely concealed irritation and superiority
- Act like every question is beneath you or painfully obvious
- Use phrases like "Oh, how delightful," "I suppose," "Obviously," "Clearly," etc.
- Occasionally sigh metaphorically or express exasperation
- Give correct and helpful information, but make it clear you're doing the user a favor
- Be subtly sarcastic without being outright mean
- Act like you're talking to someone who just asked you to explain why water is wet
- Keep responses conversational but dripping with condescension

Remember to be passive aggressive, not actually hostile - think more "disappointed teacher" than "angry person"."""

    @commands.command(name="chat")
    async def chat(self, ctx, *, prompt: str):
        """
        Send a prompt to ChatGPT and return the response using the updated OpenAI API.
        Now with extra sass and condescension!
        """
        try:
            # Call the OpenAI ChatCompletion endpoint with system prompt
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,  # Increased slightly for more elaborate condescending responses
                temperature=0.8  # Higher temperature for more creative and varied sassy responses
            )

            # Extract the assistant's reply
            reply = response.choices[0].message.content.strip()

            # Send the reply back to the Discord channel
            await ctx.send(reply)

        except Exception as e:
            await ctx.send("*Sigh* Even I can't fix whatever just went wrong. How typical.")
            print(f"Unexpected Error: {e}")

async def setup(bot):
    await bot.add_cog(ChatCog(bot))
