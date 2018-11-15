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
clock_hours = 1/180
age_length = 16
bot = commands.Bot(command_prefix=prefix, description=description)


@bot.event
async def on_ready():
    global in_server
    global out_server

    temp = await bot.application_info()
    bot.owner = temp.owner
    await bot.change_presence(game=discord.Game(name=f"for info: {prefix}help"))
    print(f'Logged in as: \n{bot.user.name}\n{bot.user.id}\nwith {bot.owner.display_name} as owner\n------')

    in_server = {i.name:{"Emoji": i.id, "Age": "0" * age_length, "Referenced": 0}
                 for i in bot.get_all_emojis()}


    with open("emoji.json", "r") as f:
        out_server = json.load(f)


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == bot.owner.id

    return commands.check(predicate)


@bot.event
async def on_reaction_add(reaction, user):
    if user != bot.user:
        in_server[reaction.emoji.name]["Referenced"] = 1


async def update_age():
    for key, value in in_server:
        value["Age"] = str(value["Referenced"]) + value["Age"][:-1]
        value["Referenced"] = 0


async def clock():
    await bot.wait_until_ready()

    while not bot.is_closed:
        await update_age()
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
    """Reacts with all emojis in the server"""
    for key, value in in_server.items():  # in_server.keys()
        await bot.add_reaction(ctx.message, f'{key}:{value["Emoji"]}')
        await asyncio.sleep(0.1)


async def save():
    """Saves unloaded emojis to the file."""
    global out_server
    with open("emoji.json", "w") as f:
        json.dump(out_server, f)
    await bot.say("Saved emoji.")


@bot.command()
async def load():
    """Gets unloaded emojis from the file and loaded from Discord."""
    global out_server
    global in_server
    in_server = {i.name:{"Emoji": i.id, "Age": "0" * age_length, "Referenced": 0}
                 for i in bot.get_all_emojis()}

    with open("emoji.json", "r") as f:
        out_server = json.load(f)

    await bot.say("Loaded emoji.")


@bot.command()
async def unload(emojiname):
    """Puts an emoji in the server, out of it. For debugging."""
    global out_server
    global in_server

    if emojiname not in in_server.keys():
        await bot.say("The emoji didn't appear to be loaded. Misspelled?")
        return -1

    out_server[emojiname] = in_server.pop(emojiname)

    # await bot.delete_custom_emoji(bot.utils.get(bot.Server.emojis, name==emojiname))

    await bot.say(f"{emojiname} switched out successfully.")
    await save()


@bot.command()
async def add(emojiname):
    """Loads the requested emoji, and unloads one that hasn't been used in a while."""
    worst = {"worst": {"Emoji": 0, "Age": "1" * age_length, "Referenced": 0}}
    if emojiname in in_server.keys():
        await bot.say(f"The emoji {emojiname} is already loaded.")
        return emojiname

    if emojiname not in out_server.keys():
        await bot.say(f"The emoji {emojiname} is not an unloaded emoji! Did you spell it correctly?")
        return emojiname

    for key, value in in_server:
        if value["Age"] < worst["Age"]:
            worst = {key: value}
    await bot.say(f'Removing {worst.keys()[0]}, and adding {emojiname}...')

    in_server[emojiname] = out_server.pop(emojiname)
    out_server[list(worst.keys())[0]] = in_server.pop(list(worst.keys())[0])
    await save()

    # await bot.delete_custom_emoji(bot.utils.get(bot.Server.emojis, name==list(worst.keys())[0]))
    # await bot.create_custom_emoji(server, emojiname, image)  # Not the right format but whatever


@bot.command(hidden=True)
@is_me()
async def logout():
    """The bot logs out"""
    await bot.say("Logging out.")
    await bot.logout()
    print("Logged out")


bot.loop.create_task(clock())
bot.run(token)
