import discord
from discord.ext import commands
import random


class LingoCog(commands.Cog):
    """
    A Lingo (Wordle-like) game where EVERYONE in the server shares
    the same game and the same set of turns.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Single, shared game state. If None, no game is active.
        # If a game is active, it will be a dict:
        # { "target": str, "guesses_left": int }
        self.active_game = None

        # A small list of 5-letter words you can guess from;
        # replace or expand as desired.
        self.word_list = [
            "apple", "brain", "chair", "drive", "eager",
            "flame", "grape", "house", "image", "joker",
            "knock", "light", "mouth", "night", "ocean",
            "proud", "queen", "robot", "sugar", "tiger",
            "urban", "vivid", "water", "xenon", "young", "zebra"
        ]

    def get_feedback(self, guess: str, target: str) -> str:
        """
        Returns a string of colored squares indicating
        how each letter in 'guess' matches 'target'.

        - :green_square:  = correct letter, correct position
        - :yellow_square: = correct letter, wrong position
        - :black_large_square: = letter not in the target
        """
        feedback = []
        target_chars = list(target)  # We'll mark off matched letters so they aren’t reused

        # First pass: Mark greens
        for i in range(len(guess)):
            if guess[i] == target[i]:
                feedback.append(":green_square:")
                target_chars[i] = None  # Mark as used
            else:
                feedback.append(None)  # Placeholder for now

        # Second pass: Mark yellows or black squares
        for i in range(len(guess)):
            if feedback[i] is not None:
                continue  # Already assigned green
            if guess[i] in target_chars:
                feedback[i] = ":yellow_square:"
                # Remove the matched letter so it can’t match again
                target_chars[target_chars.index(guess[i])] = None
            else:
                feedback[i] = ":black_large_square:"

        return "".join(feedback)

    @commands.group(name="lingo", invoke_without_command=True)
    async def lingo_group(self, ctx: commands.Context):
        """
        Base command group for Lingo.
        Usage: !lingo <subcommand>
        Subcommands: start, guess, end
        """
        await ctx.send(
            "**Lingo commands:**\n"
            "`!lingo start` - Start or restart a shared Lingo game.\n"
            "`!lingo guess <word>` - Make a guess (shared turns).\n"
            "`!lingo end` - End the current shared game."
        )

    @lingo_group.command(name="start")
    async def lingo_start(self, ctx: commands.Context):
        """
        Start (or restart) a new Lingo game for everyone.
        Overwrites the previous game if one was running.
        """
        target_word = random.choice(self.word_list)
        self.active_game = {
            "target": target_word,
            "guesses_left": 6
        }

        # Provide a small hint (first letter revealed, rest underscores)
        hint = f"{target_word[0].upper()} " + "_ " * (len(target_word) - 1)
        await ctx.send(
            f"**A new Lingo game has started for everyone!**\n"
            f"Guess the 5-letter word within 6 attempts.\n"
            f"First-letter hint: `{hint.strip()}`\n"
            "Type `!lingo guess <word>` to guess!"
        )

    @lingo_group.command(name="guess")
    async def lingo_guess(self, ctx: commands.Context, guess: str):
        """
        Make a guess at the target word. Everyone shares the same guesses!
        Example: !lingo guess brain
        """
        # Check if a game is active
        if self.active_game is None:
            await ctx.send("No Lingo game is currently active. Use `!lingo start` first.")
            return

        target_word = self.active_game["target"]
        guesses_left = self.active_game["guesses_left"]

        # Validation: must be 5 letters
        if len(guess) != 5:
            await ctx.send("Your guess must be exactly 5 letters!")
            return

        guess = guess.lower()

        # Generate feedback
        feedback = self.get_feedback(guess, target_word)

        # Decrement the shared guesses
        self.active_game["guesses_left"] -= 1
        guesses_left = self.active_game["guesses_left"]

        if guess == target_word:
            # Correct guess!
            await ctx.send(
                f"{feedback}\n"
                f"**{ctx.author.mention} guessed correctly!** The word was `{target_word.upper()}`.\n"
                "The game is now over."
            )
            self.active_game = None
            return
        else:
            # Wrong guess
            if guesses_left > 0:
                await ctx.send(
                    f"{feedback}\n"
                    f"**Incorrect guess** by {ctx.author.mention}. "
                    f"{guesses_left} guess(es) remain for everyone!"
                )
            else:
                # No guesses left
                await ctx.send(
                    f"{feedback}\n"
                    f"**No guesses left!** The word was `{target_word.upper()}`.\n"
                    "The game is now over."
                )
                self.active_game = None

    @lingo_group.command(name="end")
    async def lingo_end(self, ctx: commands.Context):
        """
        End the current Lingo game (forfeit) for everyone.
        """
        if self.active_game is None:
            await ctx.send("There's no active Lingo game to end.")
            return

        self.active_game = None
        await ctx.send(
            f"**{ctx.author.mention}** has ended the shared Lingo game for everyone."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(LingoCog(bot))
