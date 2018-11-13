import discord
from discord.ext import commands
import sys

with open("Secret.txt", "r") as f:
    token = f.read()

if not token:
    print("Error. No token file called Secret.txt")
    sys.exit(1)

description = '''A bot for automatic emote replacement, mimicking virtual memory. Somewhat by IntrusivePenDesperateSword#7881.'''

prefix = "!"
bot = commands.Bot(command_prefix=prefix, description=description)
main_extensions = ["core"]


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


@bot.command(hidden=True)
@is_me()
async def logout():
    """The bot logs out"""
    await bot.say("Logging out.")
    await bot.logout()
    print("logged out")
    sys.exit(0)


if __name__ == "__main__":
    for extension in main_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            print(f'Failed to load extension {extension}\n{exc}')

    bot.run(token)
