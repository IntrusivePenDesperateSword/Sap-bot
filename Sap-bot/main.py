import discord
from discord.ext import commands
import sys
import time
import json
import asyncio
import aiohttp
import datetime

with open("Secret.txt", "r") as f:
    token = f.read()

if not token:
    print("Error. No token file called Secret.txt")
    sys.exit(1)

description = '''A bot for automatic emote replacement, mimicking virtual memory. Somewhat by IntrusivePenDesperateSword#7881.'''

prefix = "!"
clock_hours = 1/60  # Low amount of time for debugging
age_length = 16
bot = commands.Bot(command_prefix=prefix, description=description)

bot.time = datetime.datetime.now()

bot.in_server = {}
bot.out_server = {}

with open("emojiTest.json", "r") as f:
    bot.testFile = json.load(f)

@bot.event
async def on_ready():
    temp = await bot.application_info()
    bot.owner = temp.owner
    await bot.change_presence(game=discord.Game(name=f"For info: {prefix}help"))
    print(f'Logged in as: \n{bot.user.name}\n{bot.user.id}\nwith {bot.owner.display_name} as owner\n------')

    bot.in_server = {i.name: {"Emoji": i.id, "URL": i.url, "Age": "0" * age_length, "Referenced": 0}
                 for i in bot.get_all_emojis()}

    for i in bot.testFile.keys():
        if i in [j.name for j in bot.get_all_emojis()]:
            bot.in_server[i] = bot.testFile[i]
        else:
            bot.out_server[i] = bot.testFile[i]

    print(list(bot.in_server.keys()), list(bot.out_server.keys()))
    await save()


def emoji_permission(ctx):
    channel = ctx.message.channel
    user = ctx.message.author
    permissions = user.permissions_in(channel)
    # if not permissions.manage_emojis:
    #     bot.send_message(channel, f"Sorry {user.display_name}, you can't manage emojis")
    return permissions.manage_emojis


def is_owner(ctx):
    user = ctx.message.author
    # if not user.id == bot.owner.id:
    #     bot.send_message(ctx.message.channel,
    #                      f"sorry {user.display_name}, but this command is only for {bot.owner.display_name}")
    return user.id == bot.owner.id


@bot.event
async def on_server_emojis_update(before, after):
    new = ""
    for emoji in after:
        if emoji not in before and emoji.name not in list(bot.in_server.keys()):
            new = emoji
            bot.in_server[new.name] = {"Emoji": new.id, "URL": new.url, "Age": "0" * age_length, "Referenced": 0}
            print(f"Added the new emoji {new.name}.")
            break
    else:
        gone = ""
        for emoji in before:
            if emoji not in after and emoji not in list(bot.out_server.keys()):
                gone = emoji
                print(f"Emoji {gone.name} is gone forever.")
                break


    if len([i for i in bot.get_all_emojis()]) > 48:
        worst = {"worst": {"Emoji": 0, "URL": "no", "Age": "1" * age_length, "Referenced": 0}}
        for key in bot.in_server.keys():
            if bot.in_server[key]["Age"] <= worst[list(worst.keys())[0]]["Age"]:
                worst = {key: bot.in_server[key]}
        await bot.say(f'Removing {list(worst.keys())[0]}, since {new.name} was added...')

        bot.out_server[list(worst.keys())[0]] = bot.in_server.pop(list(worst.keys())[0])

        await bot.delete_custom_emoji(discord.utils.get(new.server.emojis, name=list(worst.keys())[0]))

@bot.event
async def on_reaction_add(reaction, user):
    if user != bot.user and reaction.custom_emoji:
        if reaction.emoji.name not in bot.in_server.keys() :
            print("Emoji probably from outside the server used. Ignore.")
            return -2
        bot.in_server[reaction.emoji.name]["Referenced"] = 1


async def update_age():
    for key in bot.in_server.keys():
        bot.in_server[key]["Age"] = str(bot.in_server[key]["Referenced"]) + bot.in_server[key]["Age"][:-1]
        bot.in_server[key]["Referenced"] = 0


async def scan_logs(time):
    temp = list(bot.in_server.keys())
    for channel in list(bot.servers)[0].channels:
        logs = bot.logs_from(channel, limit=200, after=time)
        print(logs)
        for message in logs:
            for emo in temp:
                if emo in message.content:
                    bot.in_server[emo]["Referenced"] = 1
                    temp.pop(temp.index(emo))


async def clock():
    await bot.wait_until_ready()

    while not bot.is_closed:
        #await scan_logs(bot.time)
        bot.time = datetime.datetime.now()
        await update_age()
        await save()
        await asyncio.sleep(3600 * clock_hours)


@bot.command(pass_context=True)
async def add(ctx, *emojinames):
    """Loads the requested emojis and unloads unused ones."""
    server_id = ctx.message.server.id
    for emojiname in emojinames:
        if emojiname in bot.in_server.keys():
            await bot.say(f"The emoji {emojiname} is already loaded.")
            continue
        if emojiname not in bot.out_server.keys():
            await bot.say(f"The emoji {emojiname} is not an unloaded emoji! Did you spell it correctly?")
            continue

        if len([i for i in bot.get_all_emojis()]) > 48:
            worst = {"worst": {"Emoji": 0, "URL": "no", "Age": "1" * age_length, "Referenced": 0}}
            for key in bot.in_server.keys():
                if bot.in_server[key]["Age"] <= worst[list(worst.keys())[0]]["Age"]:
                    worst = {key: bot.in_server[key]}
            await bot.say(f'Removing {list(worst.keys())[0]}, and adding {emojiname}...')

            bot.out_server[list(worst.keys())[0]] = bot.in_server.pop(list(worst.keys())[0])

            await bot.delete_custom_emoji(discord.utils.get(ctx.message.server.emojis, name=list(worst.keys())[0]))
        else:
            await bot.say(f'Adding {emojiname}...')

        async with aiohttp.ClientSession() as ses:
            async with ses.get(bot.out_server[emojiname]["URL"]) as r:
                img = await r.read()

        temp = await bot.create_custom_emoji(server=ctx.message.server, name=emojiname, image=img)
        prev = bot.out_server.pop(emojiname)
        bot.in_server[emojiname] = {"Emoji": temp.id, "URL": temp.url, "Age": prev["Age"], "Referenced": 0}

    await save()


@bot.command(pass_context=True)
async def emojilist(ctx):
    """Lists the emojis not in the server, available for loading."""
    message = f"```{', '.join(list(bot.out_server.keys()))}```" if len(bot.out_server) > 0 else "There are no emojis not in the server!"
    if len(message) > 2000:
        message = f"{message[:1995]}...```"
    await bot.say(message)


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
    for key, value in bot.in_server.items():  # bot.in_server.keys()
        await bot.add_reaction(ctx.message, f'{key}:{value["Emoji"]}')
        await asyncio.sleep(0.1)


async def save():
    """Saves emojis to the testFile."""
    with open("emojiTest.json", "w") as f:
        json.dump({**bot.in_server, **bot.out_server}, f, indent=4)
    print("Saved.")


@bot.command(pass_context=True, hidden=True)
@commands.check(emoji_permission)
async def unload(ctx, *emojinames):
    """Puts an emoji in the server, out of it. For debugging."""
    for emojiname in emojinames:
        if emojiname not in bot.in_server.keys():
            await bot.say(f"The emoji {emojiname} didn't appear to be loaded. Maybe you misspelled?")
            continue
        if emojiname in bot.out_server.keys():
            await bot.say(f"{emojiname} is already unloaded.")
            continue

        bot.out_server[emojiname] = bot.in_server.pop(emojiname)

        await bot.delete_custom_emoji(discord.utils.get(ctx.message.server.emojis, name=emojiname))

        await bot.say(f"{emojiname} switched out successfully.")
    await save()


@bot.command(hidden=True, pass_context=True)
@commands.check(is_owner)
async def logout(ctx):
    """The bot logs out"""
    await save()
    #await bot.say("Logging out.")
    await bot.send_message(ctx.message.channel, "Logging out.")
    await bot.logout()
    print("Logged out")


bot.loop.create_task(clock())
bot.run(token)
