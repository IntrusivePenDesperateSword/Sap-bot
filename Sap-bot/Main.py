import discord
from discord.ext import commands
import os
import sys

token = os.environ['token']
if not token:
    print("Error. No token enviroment variable")
    sys.exit(1)

description = '''A basic bot by sapsap'''

prefix = "_"
bot = commands.Bot(command_prefix=prefix, description=description)
main_extensions = ["core", "misc", "maths", "rng"]


@bot.event
async def on_ready():
    temp = await bot.application_info()
    bot.owner = temp.owner
    await bot.change_presence(game=discord.Game(name=f"for info: {prefix}help"))
    print(f'Logged in as: \n{bot.user.name}\n{bot.user.id}\nwith {bot.owner.display_name} as owner\n------')


def is_me():
    def predicate(ctx):
        return ctx.message.author.id == bot.owner.id

    return commands.check(predicate)


@bot.command()
@is_me()
async def load(extension_name: str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say(f"```py\n{type(e).__name__}: {str(e)}\n```")
        return
    await bot.say("{} loaded.".format(extension_name))


@bot.command()
@is_me()
async def unload(extension_name: str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say(f"{extension_name} unloaded.")


@bot.command()
@is_me()
async def reload(extension_name: str):
    try:
        bot.unload_extension(extension_name)
        bot.load_extension(extension_name)
    except Exception as e:
        await bot.say(f"{e.__name__}: {e}")
    else:
        await bot.say(f"{extension_name} succsessfully reloaded")


@bot.command(hidden=True, pass_context=True)
@is_me()
async def sleep():
    """The bot goes to sleep, probably won't listen to plebs tho"""
    await bot.say("Going to sleep now")
    await bot.logout()
    print("logged out")


if __name__ == "__main__":
    for extension in main_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            print(f'Failed to load extension {extension}\n{exc}')

    bot.run(token)
