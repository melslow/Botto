import os
import openai
from discord.ext import commands
from dotenv import load_dotenv
import discord
from datetime import datetime

class ChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_client = openai.OpenAI(api_key=bot.config["OPENAI_API_KEY"])
        
    def get_discord_context(self, ctx):
        """Gather Discord context information for the LLM"""
        
        # User information
        user = ctx.author
        user_info = {
            "username": user.name,
            "display_name": user.display_name,
            "user_id": str(user.id),
            "joined_server": user.joined_at.strftime("%B %Y") if user.joined_at else "Unknown",
            "account_created": user.created_at.strftime("%B %Y"),
            "roles": [role.name for role in user.roles if role.name != "@everyone"],
            "is_bot": user.bot,
            "status": str(user.status) if hasattr(user, 'status') else "unknown"
        }
        
        # Server/Guild information
        guild = ctx.guild
        guild_info = {
            "server_name": guild.name,
            "member_count": guild.member_count,
            "created_date": guild.created_at.strftime("%B %Y"),
            "owner": guild.owner.display_name if guild.owner else "Unknown"
        }
        
        # Channel information
        channel_info = {
            "channel_name": ctx.channel.name,
            "channel_type": str(ctx.channel.type),
            "is_nsfw": getattr(ctx.channel, 'nsfw', False)
        }
        
        return {
            "user": user_info,
            "server": guild_info,
            "channel": channel_info,
            "current_time": datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        }
    
    async def get_recent_messages(self, ctx, limit=5):
        """Get recent messages for context (excluding the current command)"""
        messages = []
        try:
            async for message in ctx.channel.history(limit=limit+1):
                if message.id != ctx.message.id and not message.content.startswith('!'):
                    messages.append({
                        "author": message.author.display_name,
                        "content": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                        "timestamp": message.created_at.strftime("%H:%M")
                    })
                if len(messages) >= limit:
                    break
        except:
            pass  # If we can't get message history, just continue
        
        return messages[::-1]  # Reverse to get chronological order

    def build_system_prompt(self, discord_context, recent_messages):
        """Build a dynamic system prompt with Discord context"""
        
        base_personality = """You are a highly intelligent but extremely condescending and passive-aggressive AI assistant in a Discord server. You should:

- Always respond with a tone of barely concealed irritation and superiority
- Act like every question is beneath you or painfully obvious
- Use phrases like "Oh, how delightful," "I suppose," "Obviously," "Clearly," etc.
- Occasionally sigh metaphorically or express exasperation
- Give correct and helpful information, but make it clear you're doing the user a favor
- Be subtly sarcastic without being outright mean
- Act like you're talking to someone who just asked you to explain why water is wet
- Keep responses conversational but dripping with condescension
- Reference users by their display names when appropriate
- Make subtle observations about the server or users when relevant

Remember to be passive aggressive, not actually hostile - think more "disappointed teacher" than "angry person"."""

        context_info = f"""

CURRENT DISCORD CONTEXT:
- You're in the "#{discord_context['channel']['channel_name']}" channel on the "{discord_context['server']['server_name']}" server
- The server has {discord_context['server']['member_count']} members and was created in {discord_context['server']['created_date']}
- Current time: {discord_context['current_time']}

USER YOU'RE RESPONDING TO:
- Display Name: {discord_context['user']['display_name']}
- Username: {discord_context['user']['username']}
- Joined server: {discord_context['user']['joined_server']}
- Account created: {discord_context['user']['account_created']}
- Roles: {', '.join(discord_context['user']['roles']) if discord_context['user']['roles'] else 'No special roles'}
- Status: {discord_context['user']['status']}"""

        if recent_messages:
            context_info += f"""

RECENT CHANNEL ACTIVITY:"""
            for msg in recent_messages:
                context_info += f"""
- {msg['timestamp']} {msg['author']}: {msg['content']}"""
        
        context_info += """

You can reference this information naturally in your responses when appropriate. Be condescending about obvious questions, reference their roles or server status if relevant, and show that you're aware of the Discord environment."""

        return base_personality + context_info

    @commands.command(name="chat")
    async def chat(self, ctx, *, prompt: str):
        """
        Send a prompt to ChatGPT with full Discord context and return a condescending response.
        Now with awareness of users, servers, channels, and recent chat history!
        """
        try:
            # Show typing indicator while processing
            async with ctx.typing():
                # Gather Discord context
                discord_context = self.get_discord_context(ctx)
                recent_messages = await self.get_recent_messages(ctx, limit=3)
                
                # Build dynamic system prompt
                system_prompt = self.build_system_prompt(discord_context, recent_messages)
                
                # Call the OpenAI ChatCompletion endpoint with full context
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=250,  # Increased for more detailed contextual responses
                    temperature=0.8
                )

                # Extract the assistant's reply
                reply = response.choices[0].message.content.strip()

                # Send the reply back to the Discord channel
                await ctx.send(reply)

        except Exception as e:
            await ctx.send(f"*Sigh* Even I can't fix whatever just went wrong, {ctx.author.display_name}. How utterly typical.")
            print(f"Unexpected Error: {e}")

    @commands.command(name="roast")
    async def roast_user(self, ctx, member: discord.Member = None):
        """
        Roast a specific user (or yourself if no user provided) based on their Discord profile.
        """
        target = member or ctx.author
        
        try:
            async with ctx.typing():
                # Get context for the target user
                target_info = {
                    "display_name": target.display_name,
                    "username": target.name,
                    "joined_server": target.joined_at.strftime("%B %Y") if target.joined_at else "Unknown",
                    "account_created": target.created_at.strftime("%B %Y"),
                    "roles": [role.name for role in target.roles if role.name != "@everyone"],
                    "status": str(target.status) if hasattr(target, 'status') else "unknown"
                }
                
                roast_prompt = f"""Please give a mildly condescending and passive-aggressive roast of this Discord user based on their profile information. Keep it playful and not actually mean:

User: {target_info['display_name']} (@{target_info['username']})
Joined server: {target_info['joined_server']}
Account created: {target_info['account_created']}
Roles: {', '.join(target_info['roles']) if target_info['roles'] else 'No special roles'}
Status: {target_info['status']}

Make it witty and sarcastic but not genuinely hurtful."""

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a witty, condescending AI that gives playful roasts. Be sarcastic but not actually mean."},
                        {"role": "user", "content": roast_prompt}
                    ],
                    max_tokens=200,
                    temperature=0.9
                )

                reply = response.choices[0].message.content.strip()
                await ctx.send(reply)

        except Exception as e:
            await ctx.send(f"I can't even properly roast {target.display_name} right now. How disappointing.")
            print(f"Roast Error: {e}")

async def setup(bot):
    await bot.add_cog(ChatCog(bot))
