import discord
from discord.ext import commands
import sys
import time
import json
import asyncio

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
        await asyncio.sleep(3600 * clock_hours)


@bot.command()
async def ping():
    """Shows how long the delay is"""
    time_1 = time.perf_counter()
    await bot.type()
    time_2 = time.perf_counter()
    await bot.say(f"{round((time_2 - time_1) * 1000)} ms")


@bot.command(pass_context=True)
async def test(ctx):
    """Reacts with all emoji in the server"""
    for key, value in in_server:  # in_server.keys()
        await bot.add_reaction(ctx.message, value["Emoji"])
        await asyncio.sleep(0.2)


@bot.command(pass_context=True)
async def save():
    """Reloads all emoji in the server, and saves the ones out of it to the file."""
    global in_server
    in_server = await bot.get_all_emojis()
    with open("emoji.json", "w") as f:
        json.dump(str(out_server), f)
    # await bot.say("Saved emoji.")


@bot.command(pass_context=True)
async def load():
    """Gets unloaded emojis from the file."""
    global out_server
    with open("emoji.json", "r") as f:
        out_server = json.load(f)

    await bot.say("Loaded emoji.")


@bot.command(pass_context=True)
async def add(emojiname):
    worst = {"worst": {"emoji": None, "Age": "1" * age_length, "Referenced": 0}}
    if emojiname not in out_server.keys():
        await bot.say(f"The emoji {emojiname} is not an unloaded emoji! Did you spell it correctly?")
        return emojiname

    if emojiname in in_server.keys():
        await bot.say(f"The emoji {emojiname} is already loaded.")
        return emojiname

    for key, value in in_server:
        if value["Age"] < worst["Age"]:
            worst = {value["Name"]: value}
    await bot.say(f'Removing {worst["Name"]}, and adding {emojiname}...')

    in_server[emojiname] = out_server.pop(emojiname)
    out_server[worst["Name"]] = in_server.pop(worst["Name"])
    await save()

    # discord.addEmoji(in_server[emojiname])  # Not the right format but whatever


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
