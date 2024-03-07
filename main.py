import os
import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound
from dotenv import load_dotenv

from ext.config import Config
from ext.config import get_prefix

intents = discord.Intents().all()

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise "Please provide a TOKEN"

client = commands.Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)
client.remove_command("help")

config = Config(client)
first = True


@client.event
async def on_ready():
    global first

    if first:
        os.system("cls")

        for filename in os.listdir("./cogs"):
            if not filename.endswith(".py"):
                continue

            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                print(
                    f"[{(await config.get_time())}] [bAI] couldn't load `{filename}` | Error code: {e}"
                )
        first = False
    # await client.change_presence(activity=discord.Game("discord.py => discord.js"))
    on_time = await config.get_time()
    print(
        f"[{on_time}] [bAI] bot is ready | Servers = {len(client.guilds)} | User = {client.user}"
    )


@client.event
async def on_command_error(msg, error):
    if await config.blockCheck(msg):
        return

    if isinstance(error, commands.CommandNotFound):
        pass


# Run Bot
if __name__ == "__main__":
    client.run(TOKEN)
