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

bot.in_server = {i.id: {} for i in list(bot.servers)}
bot.out_server = {i.id: {} for i in list(bot.servers)}

bot.files = []
with open("emojiTest.json", "r") as f:
    bot.testFile = json.load(f)
    bot.files.append((bot.testFile, "emojiTest.json"))


@bot.event
async def on_ready():
    temp = await bot.application_info()
    bot.owner = temp.owner
    await bot.change_presence(game=discord.Game(name=f"For info: {prefix}help"))
    print(f'Logged in as: \n{bot.user.name}\n{bot.user.id}\nwith {bot.owner.display_name} as owner\n------')

    print(list(bot.servers))

    bot.in_server = {j.id: {i.name: {"Emoji": i.id, "URL": i.url, "Age": "0" * age_length, "Referenced": 0}
                 for i in bot.get_all_emojis() if i.server.id == j.id} for j in list(bot.servers)}

    for h in range(len(list(bot.servers))):
        for i in bot.testFile.keys():
            if i in [j.name for j in bot.get_all_emojis() if j.server.id == list(bot.servers)[h].id]:
                bot.in_server[list(bot.servers)[h].id][i] = bot.testFile[i]
            else:
                bot.out_server[list(bot.servers)[h].id][i] = bot.testFile[i]

    print((list(bot.in_server.keys()), list(bot.out_server.keys())))
    print(list(bot.in_server[bot.servers[0].id].keys()))
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
    pass


@bot.event
async def on_reaction_add(reaction, user):
    if user != bot.user and reaction.custom_emoji:
        if reaction.emoji.name not in bot.in_server.keys() :
            print("Emoji probably from outside the server used. Ignore.")
            return -2
        bot.in_server[reaction.emoji.server.id][reaction.emoji.name]["Referenced"] = 1


async def update_age():
    for key in bot.in_server.keys():
        # print(bot.in_server[key]["Referenced"])
        bot.in_server[key]["Age"] = str(bot.in_server[key]["Referenced"]) + bot.in_server[key]["Age"][:-1]
        bot.in_server[key]["Referenced"] = 0


async def scan_logs(time):
    temp = list(bot.in_server.keys())
    for server in list(bot.servers):
        for channel in server.channels:
            for message in bot.logs_from(channel, limit=200, after=time):
                for emo in temp:
                    if emo in message.content:
                        bot.in_server[emo]["Referenced"] = 1
                        temp.pop(temp.index(emo))


async def clock():
    await bot.wait_until_ready()

    while not bot.is_closed:
        await scan_logs(bot.time)
        bot.time = datetime.datetime.now()
        await update_age()
        await save()
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
    for key, value in bot.in_server[ctx.message.server.id].items():  # bot.in_server.keys()
        await bot.add_reaction(ctx.message, f'{key}:{value["Emoji"]}')
        await asyncio.sleep(0.1)


async def save():
    """Saves emojis to the testFile."""
    for i in range(len(bot.files)):
        with open(bot.files[i][1], "w") as f:
            json.dump({**bot.in_server[list(bot.servers)[i].id], **bot.out_server[list(bot.servers)[i].id]}, f, indent=4)
    print("Saved.")
    print(f"Currently in servers {[i.name for i in list(bot.servers)]}")


"""async def load():
    Gets unloaded emojis from the testFile and loaded from Discord.
    bot.in_server = {i.name: {"Emoji": i.id, "URL": i.url, "Age": "0" * age_length, "Referenced": 0}
                     for i in bot.get_all_emojis()}

    with open("emojiTest.json", "r") as f:
        bot.file = json.load(f)

    for i in bot.file.keys():
        if i in [i.name for i in bot.get_all_emojis()]:
            bot.in_server[i] = bot.file[i]
        else:
            bot.out_server[i] = bot.file[i]

    await save()"""

@bot.command(pass_context=True)
@commands.check(emoji_permission)
async def unload(ctx, *emojinames):
    """Puts an emoji in the server, out of it. For debugging."""
    for emojiname in emojinames:
        if emojiname not in bot.in_server[ctx.message.server.id].keys():
            await bot.say(f"The emoji {emojiname} didn't appear to be loaded. Maybe you misspelled?")
            continue
        if emojiname in bot.out_server[ctx.message.server.id].keys():
            await bot.say(f"{emojiname} is already unloaded.")
            continue

        bot.out_server[ctx.message.server.id][emojiname] = bot.in_server[ctx.message.server.id].pop(emojiname)

        await bot.delete_custom_emoji(discord.utils.get(ctx.message.server.emojis, name=emojiname))

        await bot.say(f"{emojiname} switched out successfully.")
    await save()


@bot.command(pass_context=True)
async def add(ctx, *emojinames):
    """Loads the requested emoji, and unloads one that hasn't been used in a while."""
    server_id = ctx.message.server.id
    for emojiname in emojinames:
        if emojiname in bot.in_server[server_id].keys():
            await bot.say(f"The emoji {emojiname} is already loaded.")
            continue
        if emojiname not in bot.out_server[server_id].keys():
            await bot.say(f"The emoji {emojiname} is not an unloaded emoji! Did you spell it correctly?")
            continue

        if len([i for i in bot.get_all_emojis() if i.server.id == server_id]) > 48:
            worst = {"worst": {"Emoji": 0, "URL": "no", "Age": "1" * age_length, "Referenced": 0}}
            for key in bot.in_server[server_id].keys():
                if bot.in_server[server_id][key]["Age"] <= worst[list(worst.keys())[0]]["Age"]:
                    worst = {key: bot.in_server[server_id][key]}
            await bot.say(f'Removing {list(worst.keys())[0]}, and adding {emojiname}...')

            bot.out_server[list(worst.keys())[0]] = bot.in_server.pop(list(worst.keys())[0])

            await bot.delete_custom_emoji(discord.utils.get(ctx.message.server.emojis, name=list(worst.keys())[0]))
        else:
            await bot.say(f'Adding {emojiname}...')

        async with aiohttp.ClientSession() as ses:
            async with ses.get(bot.out_server[emojiname]["URL"]) as r:
                img = await r.read()

        temp = await bot.create_custom_emoji(server=ctx.message.server, name=emojiname, image=img)
        prev = bot.out_server[server_id].pop(emojiname)
        bot.in_server[server_id][emojiname] = {"Emoji": temp.id, "URL": temp.url, "Age": prev["Age"], "Referenced": 0}

    await save()


@bot.command(hidden=True, pass_context=True)
@commands.check(is_owner)
async def logout(ctx):
    """The bot logs out"""
    await save()
    await bot.say("Logging out.")
    await bot.logout()
    print("Logged out")


bot.loop.create_task(clock())
bot.run(token)
