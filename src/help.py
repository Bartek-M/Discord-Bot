import os
from datetime import datetime

import discord
from discord.ext import commands

from . import config
from utils.config import get_prefix

NAME = os.getenv("NAME", "BOT")


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = config

        self.bot_pic = self.client.user.avatar

    # Help message
    @commands.command(aliases=["h", "help"])
    async def _help(self, ctx, command="Normal"):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "help", True)
        ):
            return

        prfx = str(get_prefix(self.client, ctx))

        if (
            str(command).lower() == "secret"
            and str(ctx.author.id) in self.config.valid_users
        ):
            desc += f"`{prfx}block_usr [user id]`\nBlock/Unblock specific user from using bot [{prfx}busr]\n\n"
            desc += f"`{prfx}block_srv [server id]`Block/Unblock specific server from using bot [{prfx}bsrv]\n\n"

            desc += f"`{prfx}add_VU [user]`\nAdd Valid User with every permission [{prfx}av]\n\n"
            desc += f"`{prfx}rm_VU [user]`\nRemove Valid User [{prfx}rv]\n\n"

            desc += f"`{prfx}clear_console`\nClear Console [{prfx}c_cons]\n\n"

            embed = discord.Embed(
                title="**Valid Users Commands Help**",
                description=desc,
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            )

        elif str(command).lower() == "moderator" or str(command).lower() == "admin":
            desc = f"`{prfx}block_msg [User]`\nBlocks/Unblock member from using commands [{prfx}bmsg]\n\n"
            desc += f"`{prfx}whoisblocked`\nCheck blocked members on current server [{prfx}whisb]\n\n"

            desc += f"`{prfx}config (name/reset)`\nShow server config or reset [{prfx}bmsg]\n\n"
            desc += f"`{prfx}regen_sc`\nRegenerates secret code\n\n"
            desc += f"`{prfx}setLogs (off)`\nSet current channel to logs\n\n"

            desc += f"`{prfx}move [User] [Channel]`\nMoves user [{prfx}mv]\n\n"
            desc += f"`{prfx}mic [User] (True/False)`\nMutes users\n\n"
            desc += f"`{prfx}deafen [User] (True/False)`\nDeafens and Mutes users [{prfx}df]\n\n"

            desc += f"`{prfx}add_role [User] [Role]`\nAdds role [{prfx}ar]\n\n"
            desc += f"`{prfx}rm_role [User] [Role]`\nRemoves role [{prfx}rr]\n\n"

            desc += f"`{prfx}kick [User] [Reason]`\nKick user\n\n"
            desc += f"`{prfx}ban [User] [Reason]`\nBans user\n\n"
            desc += f"`{prfx}unban [User]`\nUnbans user\n\n"

            desc += f"`{prfx}clear (number of messages to clear)`\nClears messager in current channel [{prfx}c]\n\n"

            embed = discord.Embed(
                title="**Moderator Commands Help**",
                description=desc,
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            )

        elif str(command).lower() == "music":
            desc = f"`{prfx}join`\Bot joins vc [{prfx}j]\n\n"
            desc += f"`{prfx}leave`\nBot leaves vc [{prfx}l]\n\n"

            desc += f"`{prfx}play [song]`\nPlays song or adds it to queue [{prfx}p]\n\n"
            desc += f"`{prfx}stop`\nStops player and leaves vc[{prfx}st]\n\n"

            desc += f"`{prfx}pause`\nPauses player [{prfx}ps]\n\n"
            desc += f"`{prfx}resume`\nResumes player [{prfx}rs]\n\n"

            desc += f"`{prfx}loop`\nLoops curent song [{prfx}lp]\n\n"

            desc += f"`{prfx}skip`\nSkips current song [{prfx}s]\n\n"
            desc += f"`{prfx}queue`\nShows queue [{prfx}qu]\n\n"
            desc += f"`{prfx}removeSong [index number of song]`\nRemoves song from queue [{prfx}rms]\n\n"

            desc += f"`{prfx}dj`\nTurns on DJ only mode\n\n"

            embed = discord.Embed(
                title="**Music Commands Help**",
                description=desc,
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            )

        elif str(command).lower() == "school":
            desc = f"`{prfx}getTest`\nShows all tests [{prfx}gt]\n\n"
            desc += f"`{prfx}newTest [name of the test]`\nAdds new test [{prfx}nt]\n\n"
            desc += f"`{prfx}rmTest [index mumber of the test]`\nRemoves test [{prfx}rt]\n\n"
            desc += f"`{prfx}editTest [index mumber of the test] [after edit]`\nEdites test [{prfx}et]\n\n"

            desc += f"`{prfx}getHW`\nShows all homeworks [{prfx}gh]\n\n"
            desc += f"`{prfx}newHW [name of the homework]`\nAdds new homework [{prfx}nh]\n\n"
            desc += f"`{prfx}rmHW [index mumber of the homework]`\nRemoves homework [{prfx}rh]\n\n"
            desc += f"`{prfx}editHW [index mumber of the homework] [after edit]`\nEdites homework [{prfx}eh]\n\n"

            embed = discord.Embed(
                title="**School Commands Help**",
                description=desc,
                colour=discord.Color.dark_blue(),
            )

        elif str(command).lower() == "reaction":
            desc = f"`{prfx}reaction_role [Role] [Emoji] [Message]`\nCreates message for auto roles [{prfx}reaction]\n\n"
            desc += f"`{prfx}add_reaction_role [Message ID] [Role] [Emoji]`\nAdds auto role conf [{prfx}add_reaction]\n\n"
            desc += f"`{prfx}remove_reaction_role [Message ID] (index number of conf (-1 for all))`\nRemoves auto role conf [{prfx}rm_reaction]\n\n"
            desc += f"`{prfx}reaction_role_list (Message ID)`\nShows auto role conf [{prfx}reaction_list]\n\n"

            embed = discord.Embed(
                title="**Auto Role Commands Help**",
                description=desc,
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            )

        elif str(command).lower() == "other" or str(command).lower() == "utilities":
            desc = "`hello`\nGreets users\n\n"

            desc += f"`{prfx}metar [Airport ICAO Code]`\nMetar report for a specific airport\n\n"
            desc += f"`{prfx}network [IP] [Subnet Mask]`\nGet information about specific network [{prfx}net]\n\n"
            desc += f"`{prfx}random_get [number of generating things] [number or some words]`\nGet something randomly [{prfx}rand]\n\n"
            desc += f"`{prfx}fetch_user [User ID]`\nShows specific user info\n\n"
            desc += f"`{prfx}ping`\nCheck bot ping\n\n"
            desc += f"`{prfx}prefix [New prefix]`\nChanges server prefix\n\n"
            desc += f"`{prfx}nick [User] [Nick]`\nChanges nick [{prfx}n]\n\n"

            desc += f"`{prfx}welcome [Channel ID] [Message] ([USER] for mention) ([MEMBERS] for number of guild members)`\nSet welcome message\n\n"
            desc += f"`{prfx}welcome_off`\nTurn off welcome message\n\n"

            desc += f"`{prfx}forward (Server ID) (Server Secret Code)`\nUse server settings in DM [{prfx}frwd]\n\n"
            desc += f"`{prfx}forward_del [User]`\nDel forwarding from specific user [{prfx}frwdel]\n\n"

            embed = discord.Embed(
                title="**Other Commands Help**",
                description=desc,
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            )

        elif str(command).lower() == "info":
            desc = f"`1` Move up {NAME} role to get every command to work\n\n`2` Every {NAME} setting is saving to config file\n\n`3` There are some limits, so don't exceed them\n\n`4` Errors doesn't crush {NAME}\n\n`5` Things in [] help command are an important parameter\n\n`6` Things in () help command aren't an important parameter\n\n`7` Mention {NAME} to see info card\n\n`8` Every command has permissions\n\n`9` {NAME} is case insensitive\n\n`10` If you've got some problems, use support command\n\n`11` Default prefix is `{NAME}.` and `.`, you can change only second one"
            embed = discord.Embed(
                title=f"**Useful info about {NAME}**",
                description=desc,
                colour=discord.Color.dark_blue(),
            )

        else:
            url = f"[**Add bot to your server**](https://discord.com/api/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=applications.commands%20bot)"

            embed = discord.Embed(
                description=url,
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            )
            embed.set_author(
                name=f"{NAME} Commands Help",
                icon_url=self.bot_pic,
            )

            embed.add_field(
                name="**Moderator**",
                value=f"`{prfx}help moderator`",
                inline=True,
            )
            embed.add_field(
                name="**Music**",
                value=f"`{prfx}help music`",
                inline=True,
            )
            embed.add_field(
                name="**School**",
                value=f"`{prfx}help school`",
                inline=True,
            )

            embed.add_field(
                name="**Reactions**",
                value=f"`{prfx}help reaction`",
                inline=True,
            )
            embed.add_field(
                name="**Other**",
                value=f"`{prfx}help other`",
                inline=True,
            )
            embed.add_field(
                name="**Info**",
                value=f"`{prfx}help info`",
                inline=True,
            )

        embed.set_thumbnail(url=self.bot_pic)
        await ctx.channel.send(embed=embed)
        await self.config.on_checkk(ctx, "help", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        self.config.on_check = []


async def setup(client):
    await client.add_cog(Help(client))
