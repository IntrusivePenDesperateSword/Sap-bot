from discord.ext import commands


class maths():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def add(self, ctx, *, numbers):
        """sums numbers separated by spaces"""
        await self.bot.delete_message(ctx.message)
        numbers = " + ".join(numbers.split(" "))
        result = sum(list(map(int, numbers.split(" + "))))
        await self.bot.say(f"{numbers} = {result}")
        # await self.bot.say(sum(list(map(int, numbers))))

    @commands.command()
    async def multiply(self, *, numbers):
        """multiplies numbers"""
        temp_str = " * ".join(numbers.split(" "))
        numbers = list(map(int, numbers.split(" ")))
        output = 1
        for i in numbers:
            output *= i
        await self.bot.say(f"{temp_str} = {output}")

    @commands.command(pass_context=True)
    async def divide(self, ctx, left: int, right: int):
        """Divide a number by another number"""
        if right == 0:
            await self.bot.say(
                "you think it's funny to divide by zero?? you disgust me.")
        else:
            try:
                await self.bot.say(f"{left} / {right} = {left/right}")
            except Exception:
                print(f"something went wrong with {ctx.message.author}'s math")


def setup(bot):
    bot.add_cog(maths(bot))
