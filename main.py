import os

from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

load_dotenv()
from src import client, config

TOKEN = os.getenv("TOKEN")
START = True

if not TOKEN:
    raise "Please provide a TOKEN"


@client.event
async def on_ready():
    global START

    if START:
        os.system("cls")

        for filename in os.listdir("./src"):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            try:
                await client.load_extension(f"src.{filename[:-3]}")
            except Exception as e:
                print(
                    f"[{(await config.get_time())}] [bAI] couldn't load `{filename}` | Error code: {e}"
                )

        START = False

    on_time = await config.get_time()
    print(
        f"[{on_time}] [bAI] bot is ready | Servers = {len(client.guilds)} | User = {client.user}"
    )


@client.event
async def on_command_error(msg, error):
    if await config.blockCheck(msg):
        return

    if isinstance(error, CommandNotFound):
        pass


if __name__ == "__main__":
    client.run(TOKEN)
