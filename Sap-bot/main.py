import discord
from discord.ext import commands
import sys
import time
import json
import asyncio
import aiohttp
import aiofiles

with open("Secret.txt", "r") as f:
    token = f.read()

if not token:
    print("Error. No token file called Secret.txt")
    sys.exit(1)

description = '''A bot for automatic emote replacement, mimicking virtual memory. Somewhat by IntrusivePenDesperateSword#7881.'''

in_server, out_server = {}, {}
prefix = "!"
clock_hours = 1/60  # Low amount of time for debugging
age_length = 16
bot = commands.Bot(command_prefix=prefix, description=description)


@bot.event
async def on_ready():
    global in_server
    global out_server

    temp = await bot.application_info()
    bot.owner = temp.owner
    await bot.change_presence(game=discord.Game(name=f"For info: {prefix}help"))
    print(f'Logged in as: \n{bot.user.name}\n{bot.user.id}\nwith {bot.owner.display_name} as owner\n------')

    in_server = {i.name:{"Emoji": i.id, "URL": i.url, "Age": "0" * age_length, "Referenced": 0}
                 for i in bot.get_all_emojis()}

    with open("emoji.json", "r") as j:
        file = json.load(j)
    print(file.keys())

    online_keys = bot.get_all_emojis()
    for i in file.keys():
        if i in [k.name for k in online_keys]:
            in_server[i] = file[i]
        else:
            out_server[i] = file[i]

    print(out_server)
    print(in_server)  # Do note these are also equal, for some reason.

    await save()
    print(in_server)


async def emoji_permission(ctx):
    channel = ctx.channel
    user = ctx.message.author
    permissions = await channel.permissions_for(user)
    if not permissions.manage_emojis:
        bot.send_message(channel, f"sorry {user.display_name}, you can't manage emojis")
    return permissions.manage_emojis


def is_owner(ctx):
    user = ctx.message.author
    if not user.id == bot.owner.id:
        bot.send_message(ctx.message.channel,
                         f"sorry {user.display_name}, but this command is only for {bot.owner.display_name}")
    return user.id == bot.owner.id


@bot.event
async def on_reaction_add(reaction, user):
    if user != bot.user and reaction.custom_emoji:
        if reaction.emoji.name not in in_server.keys() :
            print("Emoji supposedly not in in_server used in reaction. Hecc")
            return -2
        in_server[reaction.emoji.name]["Referenced"] = 1


async def update_age():
    for key in in_server.keys():
        # print(in_server[key]["Referenced"])
        in_server[key]["Age"] = str(in_server[key]["Referenced"]) + in_server[key]["Age"][:-1]
        in_server[key]["Referenced"] = 0


async def clock():
    await bot.wait_until_ready()

    while not bot.is_closed:
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
    for key, value in in_server.items():  # in_server.keys()
        await bot.add_reaction(ctx.message, f'{key}:{value["Emoji"]}')
        await asyncio.sleep(0.1)


async def save():
    """Saves emojis to the file."""
    global out_server
    global in_server
    with open("emoji.json", "w") as f:
        json.dump({**in_server, **out_server}, f, indent=4)
    print("Saved.")


@bot.command()
async def load():
    """Gets unloaded emojis from the file and loaded from Discord."""
    global out_server
    global in_server

    in_server = {i.name:{"Emoji": i.id, "URL": i.url, "Age": "0" * age_length, "Referenced": 0}
                 for i in bot.get_all_emojis()}

    with open("emoji.json", "r") as f:
        file = json.load(f)
    for i in file.keys():
        if i in [i.name for i in bot.get_all_emojis()]:
            in_server[i] = file[i]
        else:
            out_server[i] = file[i]

    await save()
    await bot.say("Loaded emoji.")


@bot.command(pass_context=True)
@commands.check(emoji_permission)
async def unload(ctx, *emojinames):
    """Puts an emoji in the server, out of it. For debugging."""
    global out_server
    global in_server
    for emojiname in emojinames:
        if emojiname not in in_server.keys():
            await bot.say(f"The emoji {emojiname} didn't appear to be loaded. Maybe you misspelled?")
            continue
        if emojiname in out_server.keys():
            await bot.say(f"{emojiname} is already unloaded.")
            continue

        out_server[emojiname] = in_server.pop(emojiname)

        await bot.delete_custom_emoji(discord.utils.get(ctx.message.server.emojis, name=emojiname))

        await bot.say(f"{emojiname} switched out successfully.")
    await save()


@bot.command(pass_context=True)
async def add(ctx, *emojinames):
    """Loads the requested emoji, and unloads one that hasn't been used in a while."""
    for emojiname in emojinames:
        worst = {"worst": {"Emoji": 0, "URL": "no", "Age": "1" * age_length, "Referenced": 0}}
        if emojiname in in_server.keys():
            await bot.say(f"The emoji {emojiname} is already loaded.")
            continue

        if emojiname not in out_server.keys():
            await bot.say(f"The emoji {emojiname} is not an unloaded emoji! Did you spell it correctly?")
            continue

        if len([i for i in bot.get_all_emojis()]) < 49:
            for key in in_server.keys():
                if in_server[key]["Age"] <= worst[list(worst.keys())[0]]["Age"]:
                    worst = {key: in_server[key]}
            await bot.say(f'Removing {list(worst.keys())[0]}, and adding {emojiname}...')

            in_server[emojiname] = out_server.pop(emojiname)
            out_server[list(worst.keys())[0]] = in_server.pop(list(worst.keys())[0])

            await bot.delete_custom_emoji(discord.utils.get(ctx.message.server.emojis, name=list(worst.keys())[0]))

        async with aiohttp.ClientSession() as ses:
            async with ses.get(in_server[emojiname]["URL"]) as r:
                img = await r.read()

        await bot.create_custom_emoji(server=ctx.message.server, name=emojiname, image=img)

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
