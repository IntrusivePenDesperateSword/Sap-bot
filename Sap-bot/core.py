from discord.ext import commands
import time


class core():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ping(self):
        """Shows how long the delay is"""
        time_1 = time.perf_counter()
        await self.bot.type()
        time_2 = time.perf_counter()
        await self.bot.say(f"{round((time_2 - time_1) * 1000)} ms")

    @commands.command(pass_context=True)
    async def save(self):
        in_serv = discord.getEmojis();
        with open("emoji.txt", "w") as f:
            f.write(str(out_serv) + "\n" + str(in_serv))
        await self.bot.say("Saved emoji.")

    @commands.command(pass_context=True)
    async def load(self):
        with open("emoji.txt", "r") as f:
            out_serv, in_serv = f.read().split("\n")

        await self.bot.say("Loaded emoji.")

    @commands.command(pass_context=True)
    async def add(self, emojiname):
        worst = ["", "", "11111111111"]
        # assert emojiname is in in_serv
        
        worstInd = 0
        for i in range(len(in_serv)):
            if in_serv[i][2] < worst[2]: # Convert to binary somehow?
                worst  = in_serv[i]
                worstInd = i

        await self.bot.say(f"Removing {worst[0]}, and adding {emojiname}...")

        new = []
        out_serv.append(in_serv.pop(in_serv.index(worst)))
        for i in out_serv:
            if i[0] == emojiname:
                new = i
    
        discord.addEmoji(new) # Not the right format but whatever


def setup(bot):
    bot.add_cog(core(bot))
