from discord.ext import commands
import time
from main import is_me


class core():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ping(self):
        """Shows how long the delay is"""
        time_1 = time.perf_counter()
        await self.bot.type()
        time_2 = time.perf_counter()
        await self.bot.say(f"pong\n{round((time_2 - time_1) * 1000)} ms")

    @commands.command()
    async def echo(self, *, message: str):
        """Repeats what you just said"""
        await self.bot.say(f"{message}")


def setup(bot):
    bot.add_cog(core(bot))
