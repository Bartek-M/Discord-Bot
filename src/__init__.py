import discord
from discord.ext import commands

from utils.config import Config, get_prefix

intents = discord.Intents().all()

client = commands.Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)
client.remove_command("help")

config = Config(client)
