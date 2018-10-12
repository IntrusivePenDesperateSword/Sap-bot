from discord.ext import commands
import random


class rng():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", aliases=["dice"])
    async def roll(self, dice: str):
        """Rolls a dice,uses NdN setup."""
        message = await self.bot.say("Rolling..")
        try:
            rolls, limit = map(int, dice.split('d'))
            if rolls > 99999 or rolls < 0 or limit > 99999 or limit < 0:
                await self.bot.edit_message(message, "Those aren't valid rolls, sorry")
        except Exception:
            await self.bot.edit_message(message, 'Needs to be written as NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        await self.bot.edit_message(message, result)

    @commands.command(description='Makes a choice based on the options you gave it')
    async def choose(self, *choices: str):
        """Chooses a random choice."""
        if len(choices) == 0:
            await self.bot.say("That's easy, i choose \" \"")
        else:
            await self.bot.say(random.choice(choices))


def setup(bot):
    bot.add_cog(rng(bot))
