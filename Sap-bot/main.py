import discord
from discord.ext import commands
import sys, time, json, asyncio


with open("Secret.txt", "r") as f:
    token = f.read()

if not token:
    print("Error. No token file called Secret.txt")
    sys.exit(1)

description = '''A bot for automatic emote replacement, mimicking virtual memory. Somewhat by IntrusivePenDesperateSword#7881.'''

in_server, out_server = {}, {}
prefix = "!"
clock_hours = 12
age_length = 16
bot = commands.Bot(command_prefix=prefix, description=description)


@bot.event
async def on_ready():
    temp = await bot.application_info()
    bot.owner = temp.owner
    await bot.change_presence(game=discord.Game(name=f"for info: {prefix}help"))
    print(f'Logged in as: \n{bot.user.name}\n{bot.user.id}\nwith {bot.owner.display_name} as owner\n------')

    in_server = bot.get_all_emojis()
    with open("emoji.json", "r") as f:
        out_server = json.load(f)


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == bot.owner.id

    return commands.check(predicate)


@bot.event
async def on_reaction_add(reaction, user):
    in_server[reaction.emoji.name]["Referenced"] = 1


def update_age():
    for key, value in in_server:
        value[1] = str(value[2]) + value[1][:-1]
        value[2] = 0


async def clock():
    await bot.wait_until_ready()

    while not bot.is_closed:
        update_age()
        await asyncio.sleep(3600*clock_hours)


@commands.command()
async def ping():
    """Shows how long the delay is"""
    time_1 = time.perf_counter()
    await bot.type()
    time_2 = time.perf_counter()
    await bot.say(f"{round((time_2 - time_1) * 1000)} ms")


"""@commands.command(pass_context=True)
async def test():"""


@commands.command(pass_context=True)
async def save():
    in_server = await bot.get_all_emojis()
    with open("emoji.json", "w") as f:
        json.dump(str(out_server), f)
    #await bot.say("Saved emoji.")


@commands.command(pass_context=True)
async def load():
    with open("emoji.json", "r") as f:
        out_server = json.load(f)

    await bot.say("Loaded emoji.")


@commands.command(pass_context=True)
async def add(emojiname):
    worst = {"emoji":None, "Age":"1"*age_length, "Referenced":0}
    # assert emojiname is in in_server

    worstInd = 0
    for i in range(len(bot.in_server)):
        if in_server[i][1] < worst[1]:
            worst = in_server[i]
            worstInd = i
    await bot.say(f"Removing {worst[0]}, and adding {emojiname}...")
    new = []
    out_server.append(bot.in_server.pop(worstInd))
    await save()

    for i in out_server:
        if i[0] == emojiname:
            new = i

    #discord.addEmoji(new)  # Not the right format but whatever


@bot.command(hidden=True)
@is_me()
async def logout():
    """The bot logs out"""
    await bot.say("Logging out.")
    await bot.logout()
    print("logged out")
    sys.exit(0)

bot.loop.create_task(clock())
bot.run(token)
