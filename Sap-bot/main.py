import discord
from discord.ext import commands
import sys
import json

with open("Secret.txt", "r") as f:
    token = f.read()

if not token:
    print("Error. No token file called Secret.txt")
    sys.exit(1)

description = '''A bot for automatic emote replacement, mimicking virtual memory. Somewhat by IntrusivePenDesperateSword#7881.'''

prefix = "!"
bot = commands.Bot(command_prefix=prefix, description=description)


@bot.event
async def on_ready():
    temp = await bot.application_info()
    bot.owner = temp.owner
    await bot.change_presence(game=discord.Game(name=f"for info: {prefix}help"))
    print(f'Logged in as: \n{bot.user.name}\n{bot.user.id}\nwith {bot.owner.display_name} as owner\n------')
    
    in_serv = [i for i in bot.get_all_emojis()]
    with open("emojis.json", "r") as f:
        out_serv = f.read().split("\n")[0]


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == bot.owner.id

    return commands.check(predicate)


@commands.command(pass_context=True)
async def ping():
    """Shows how long the delay is"""
    time_1 = time.perf_counter()
    await bot.type()
    time_2 = time.perf_counter()
    await bot.say(f"{round((time_2 - time_1) * 1000)} ms")

    
@commands.command(pass_context=True)
async def save():
    bot.in_server = bot.get_all_emojis()
    with open("emoji.json", "w") as f:
        f.write(str(out_serv) + "\n" + str(bot.in_server))
    await bot.say("Saved emoji.")

    
@commands.command(pass_context=True)
async def load():
    with open("emoji.json", "r") as f:
        out_serv, in_serv = f.read().split("\n")

    await bot.say("Loaded emoji.")

@commands.command(pass_context=True)
async def add(emojiname):
    worst = ["", "", "11111111111"]
    # assert emojiname is in in_serv
        
    worstInd = 0
    for i in range(len(in_serv)):
        if in_serv[i][2] < worst[2]: # Convert to binary somehow?
            worst  = in_serv[i]
            worstInd = i
    await bot.say(f"Removing {worst[0]}, and adding {emojiname}...")
    new = []
    out_serv.append(in_serv.pop(worstInd))
    for i in out_serv:
        if i[0] == emojiname:
            new = i

    discord.addEmoji(new) # Not the right format but whatever


@bot.command(hidden=True)
@is_me()
async def logout():
    """The bot logs out"""
    await bot.say("Logging out.")
    await bot.logout()
    print("logged out")
    sys.exit(0)



bot.run(token)
