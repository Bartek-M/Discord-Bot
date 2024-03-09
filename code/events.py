import os
import random
import asyncio

import discord
from discord.utils import get
from discord.ext import commands

from . import config
from utils.config import get_prefix

NAME = os.getenv("NAME", "BOT")


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = config

        self.listening = []
        self.xyz1 = ""
        self.brb_nick = []
        self.h = ["Hello", "Hi", "Hello, how can I help you?"]
        self.bot_avatar = self.client.user.avatar

    # Bot events
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            id = member.guild.id

            wlcm = self.config.get_server(str(id))
            wlcm = wlcm["welcomeMsg"]

            if len(wlcm) != 2:
                return

            msg = f"{str(wlcm[1])}"
            msg = msg.replace("[USER]", member.mention)
            msg = msg.replace("[MEMBERS]", str(member.guild.member_count))

            for channel in member.guild.channels:
                if str(channel.id) == wlcm[0]:
                    await channel.send(
                        embed=discord.Embed(
                            description=msg, colour=discord.Color.dark_blue()
                        )
                    )
                    break
        except:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.member

        try:
            guild = member.guild
            id = str(guild.id)
        except:
            return

        msgID = payload.message_id

        spcificSrvr = self.config.get_server(id)
        autoRole = spcificSrvr["Reactions"]

        try:
            ar_msg = autoRole[str(msgID)]
        except:
            return

        if str(member) != str(self.client.user):
            emoji = payload.emoji

            check_ = False
            role = ""

            for i in range(len(ar_msg)):
                atr = ar_msg[i]
                role1 = atr[0]
                emoji1 = atr[1]

                if str(emoji1) == str(emoji):
                    check_ = True
                    role = role1
                    break

            if check_:
                role = get(guild.roles, id=int(role))
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        try:
            guild = await self.client.fetch_guild(payload.guild_id)
            id = str(guild.id)
        except:
            return

        member = await guild.fetch_member(payload.user_id)
        msgID = payload.message_id

        spcificSrvr = self.config.get_server(id)
        autoRole = spcificSrvr["Reactions"]

        try:
            ar_msg = autoRole[str(msgID)]
        except:
            return

        if str(member) != str(self.client.user):
            emoji = payload.emoji

            check_ = False
            role = ""

            for i in range(len(ar_msg)):
                atr = ar_msg[i]
                role1 = atr[0]
                emoji1 = atr[1]

                if str(emoji1) == str(emoji):
                    check_ = True
                    role = role1
                    break

            if check_:
                role = get(guild.roles, id=int(role))
                await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send("Hey there!")

                desc = f"[**Add bot to your server**](https://discord.com/api/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=applications.commands%20bot)\n\n"

                desc += f"**My prefix:** `.`\n\n"
                desc += f"**If you need some help, type** `.help`\n\n"
                desc += f"**If you want to see this info card, mention me**\n\n"

                embed = discord.Embed(
                    description=desc, colour=discord.Color.dark_blue()
                )
                embed.set_author(
                    name=f"Hello, I'm {NAME}",
                    icon_url=self.bot_avatar,
                )

                embed.set_thumbnail(url=self.bot_avatar)
                await channel.send(embed=embed)

                break

        id = guild.id
        self.config.servers.append(str(id))
        new_category = self.config.category
        new_category["name"] = str(id)
        new_category["secret_code"] = self.config.gen_sc()
        self.config.settings.append(new_category)

        self.config.save()
        await asyncio.create_task(
            self.config.prnt(
                None,
                f"[{(await self.config.get_time())}] [{NAME}] Added to {guild.name} ({guild.id})",
                False,
            )
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        id = guild.id
        spcificSrvr = self.config.servers.index(str(id))
        self.config.servers.remove(str(id))
        del self.config.settings[spcificSrvr]
        self.config.save()
        await asyncio.create_task(
            self.config.prnt(
                None,
                f"[{(await self.config.get_time())}] [{NAME}] Removed from {guild.name} ({guild.id})",
                False,
            )
        )

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await msg.channel.send(
                embed=discord.Embed(
                    description=f"Please pass in all required arguments",
                    colour=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.MissingPermissions):
            await msg.channel.send(
                embed=discord.Embed(
                    description=f"Missing permission", colour=discord.Color.red()
                )
            )
        elif isinstance(error, commands.ArgumentParsingError):
            await msg.channel.send(
                embed=discord.Embed(
                    description=f"You passed wrong arguments",
                    colour=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await msg.channel.send(
                embed=discord.Embed(description=error, colour=discord.Color.red())
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await msg.channel.send(
                embed=discord.Embed(
                    description=f"This command doesn't work in direct messages",
                    colour=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await msg.channel.send(
                embed=discord.Embed(
                    description=f"I don't have sufficient permissions for this",
                    colour=discord.Color.red(),
                )
            )
        elif isinstance(error, discord.errors.Forbidden):
            await msg.channel.send(
                embed=discord.Embed(
                    description=f"Message: `{error}`\n\n [Contact support for help - use `{get_prefix(self.client, msg)}support`]",
                    colour=discord.Color.red(),
                )
            )
        elif isinstance(error, discord.errors.NotFound):
            try:
                error_lst = error.split()
                error_num = error_lst.index("Unknown")

                unknown = error_lst[int(error_num + 1)]

                await msg.channel.send(
                    embed=discord.Embed(
                        description=f"{str(unknown).capitalize()} not found",
                        colour=discord.Color.red(),
                    )
                )
            except:
                await msg.channel.send(
                    embed=discord.Embed(
                        description=f"Message: `{error}`\n\n [Contact support for help - use `{get_prefix(self.client, msg)}support`]",
                        colour=discord.Color.red(),
                    )
                )
        else:
            if "missing permission" in str(error).lower():
                required_perrmisions = [
                    "View Channels",
                    "Manage Roles",
                    "Change Nickname",
                    "Manage Nicknames",
                    "Kick Members",
                    "Ban Members",
                    "Send Messages",
                    "Send Messages in Threads",
                    "Embed Links",
                    "Add Reactionss",
                    "Mention @everyone, @here, and All Roles",
                    "Manage Messages",
                    "Read Message History",
                    "Connect",
                    "Speak",
                    "Use Voice Activity",
                    "Piority Speaker",
                    "Mute Members",
                    "Deafen Members",
                    "Move Members",
                ]
                await msg.channel.send(
                    embed=discord.Embed(
                        title="I don't have sufficient permissions for this",
                        description=f"Check up my **required** permissions or just make me **Administrator**:\n```{required_perrmisions}```\nI also can't do anything to someone who is higher, in the roles, than me - take my role to the highest point in the roles. Some commands doesn't work on server owners\n\n [Contact support for help - use `{get_prefix(self.client, msg)}support`]",
                        colour=discord.Color.red(),
                    )
                )
            elif "not found" in str(error).lower():
                await msg.channel.send(
                    embed=discord.Embed(
                        description=f"{error}", colour=discord.Color.red()
                    )
                )
            else:
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(msg, 'Error')} Message = `{error}` | Invoked with: `{msg.invoked_with}`",
                        False,
                    )
                )
                await msg.channel.send(
                    embed=discord.Embed(
                        description=f"Message: `{error}`\n\n [Contact support for help - use `{get_prefix(self.client, msg)}support`]",
                        colour=discord.Color.red(),
                    )
                )

        self.config.on_check = []

    # Getting Messages
    @commands.Cog.listener()
    async def on_message(self, msg):
        if str(self.config.getID(msg)) in self.config.config["msgs"]:
            if str(msg.content).strip() != "":
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(msg, 'Chat')} -> {msg.content}",
                        False,
                    )
                )
            else:
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(msg, 'Chat')} -> Unkown Content",
                        False,
                    )
                )

        if not msg.author.bot:
            channels1 = ["calc"]
            msgs1 = ["hello", f"<@!{self.client.user.id}>", f"<@{self.client.user.id}>"]

            if (
                str(msg.channel) in channels1
                or str(msg.content.lower()) in msgs1
                or "calc" in str(msg.channel)
            ):
                if not (await self.config.blockCheck(msg)):
                    if "calc" in str(msg.channel):
                        try:
                            calculation = msg.content.strip()
                            calculation = (
                                calculation.replace("^", "**")
                                .replace(":", "/")
                                .replace("=", "")
                            )
                            calculation1 = calculation.replace(" ", "")
                            await msg.channel.send(
                                embed=discord.Embed(
                                    description=f"{calculation} = {eval(calculation1)}",
                                    colour=discord.Color.dark_blue(),
                                )
                            )

                        except:
                            if (
                                msg.content.find(f"{(get_prefix(self.client, msg))}c")
                                != -1
                            ):
                                pass
                            else:
                                await msg.channel.send(
                                    embed=discord.Embed(
                                        description="ERROR :/",
                                        colour=discord.Color.red(),
                                    )
                                )
                    else:
                        if str(msg.content).lower() == "hello":
                            await msg.channel.send(
                                embed=discord.Embed(
                                    description=f"{random.choice(self.h)} {msg.author.mention}",
                                    colour=discord.Color.dark_blue(),
                                )
                            )

                        elif (
                            str(msg.content.strip()) == f"<@!{self.client.user.id}>"
                            or str(msg.content.strip()) == f"<@{self.client.user.id}>"
                        ):
                            desc = f"[**Add bot to your server**](https://discord.com/api/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=applications.commands%20bot)\n\n"

                            desc += (
                                f"**My prefix:** `{(get_prefix(self.client, msg))}`\n\n"
                            )
                            desc += f"**If you need some help, type** `{get_prefix(self.client, msg)}help`\n\n"
                            desc += (
                                f"**If you want to see this info card, mention me**\n\n"
                            )

                            embed = discord.Embed(
                                description=desc, colour=discord.Color.dark_blue()
                            )
                            embed.set_author(
                                name=f"Hello, I'm {NAME}", icon_url=self.bot_avatar
                            )
                            embed.set_thumbnail(url=self.bot_avatar)

                            await msg.channel.send(embed=embed)


# Setting up the cog
async def setup(client):
    await client.add_cog(Events(client))
