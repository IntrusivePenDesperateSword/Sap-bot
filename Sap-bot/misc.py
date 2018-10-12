from discord.ext import commands
import words2num as w2n
import num2words as n2w
import random
import asyncio


class misc():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wordify", aliases=["Wordify", "word", "Word"])
    async def wordify(self, *, number: int):
        """Turns a number into words, almost as magic as it sounds"""
        await self.bot.say(n2w.num2words(number))

    @commands.command(name="numbify", aliases=["Numbify", "numb", "Numb"])
    async def numbify(self, *, string: str):
        """Turns words into a number, not as magic as it sounds"""
        await self.bot.say(w2n.words2num(string))

    @commands.command(pass_context=True, name="reminder", aliases=["Reminder", "remind", "Remind"])
    async def reminder(self, ctx, time: int, *, message: str):
        """takes a time in minutes and a string and then pings you with the string after that amount of time"""
        if len(message) < 1:
            message = "reminder"
        if time < 1:
            time = 1
        await self.bot.say(f"okay, i'll remind you in {time} minute{'s' * (time > 1)}")
        await asyncio.sleep(time * 60)
        await self.bot.say(f"Hey {ctx.message.author.mention}, {message}")

    @commands.command(pass_context=True)
    async def love(self, ctx):
        """tells the people you mentioned that you love them"""
        message = ctx.message
        server = message.server
        await self.bot.delete_message(ctx.message)
        if len(message.mentions) < 1:
            await self.bot.say("you need to love someone")
        else:
            sender = server.get_member(message.author.id)
            for i in message.mentions:
                interest = server.get_member(i.id)
                await self.bot.say(f"{interest.nick}, {sender.nick} loves you :3")

    @commands.command(pass_context=True)
    async def inspire(self, ctx):
        """Gets you a picture from inspirobot"""
        await self.bot.delete_message(ctx.message)
        numberA = str(random.randint(1, 30))
        numberB = random.randint(0, 9999)
        response = f"http://generated.inspirobot.me/0{'0' * (len(numberA) < 2)}{numberA}/aXm{numberB}xjU.jpg"
        await self.bot.say(f"{response}")


def setup(bot):
    bot.add_cog(misc(bot))
