import discord
import asyncio

from discord.ext import commands
from discord.ext.commands import BucketType
from datetime import datetime

from . import config


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = config

    # Settings
    @commands.command(aliases=["conf", "config"])
    async def config_(self, ctx, state="test"):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "conf", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            id = self.config.getID(ctx)
            conf1 = self.config.get_server(str(id))

            if str(state) != "reset" and str(state) != "test":
                try:
                    conf1[state]
                except:
                    state = "test"

            if str(state) == "reset":
                if "DM" in str(id):
                    new_category = self.config.categoryDM

                    new_category["name"] = str(id)
                    new_category["secret_code"] = self.config.gen_sc()

                    spcificSrvr = self.config.dm.index(str(id))
                    self.config.dm_settings[int(spcificSrvr)] = new_category
                else:
                    new_category = self.config.category

                    new_category["name"] = str(id)
                    new_category["secret_code"] = self.config.gen_sc()

                    spcificSrvr = self.config.servers.index(str(id))
                    self.config.settings[int(spcificSrvr)] = new_category

                self.config.save()

                await ctx.channel.send(
                    embed=discord.Embed(
                        description="Config file has been reset",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} reset config file",
                    )
                )
            elif str(state) != "test":
                await ctx.channel.send(
                    embed=discord.Embed(
                        title="Config File",
                        description=f"  {state} - `{conf1[state]}`",
                        colour=discord.Color.dark_blue(),
                        timestamp=datetime.utcnow(),
                    ).set_footer(
                        icon_url=ctx.author.avatar, text=f"Checked by {ctx.author}"
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} showed config file [{state}]",
                    )
                )
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        title="Config File",
                        description=f"```{str(self.config.category)}```",
                        colour=discord.Color.dark_blue(),
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "conf", False)

    # Secret code
    @commands.command(aliases=["regen_sc"])
    async def regenerate_secret_code(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "regen_sc", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            id = self.config.getID(ctx)
            sc = self.config.get_server(str(id))
            sc["secret_code"] = self.config.gen_sc()
            self.config.save()

            await ctx.channel.send(
                embed=discord.Embed(
                    description="Secret code has been regenerated",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} regenerated secret code",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "regen_sc", False)

    # Logs
    @commands.command(aliases=["logs", "setlogs"])
    @commands.guild_only()
    async def set_logs(self, ctx, state="test"):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "setLogs", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            id = self.config.getID(ctx)
            log = self.config.get_server(str(id))
            if str(state) == "off":
                log["LogChannel"] = ""
                self.config.save()

                await ctx.channel.send(
                    embed=discord.Embed(
                        description="Turned off logs channel",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} turned off logs channel'",
                    )
                )
            else:
                log["LogChannel"] = str(ctx.channel.id)
                self.config.save()

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Log channel set to `{ctx.channel.name}`",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} set log channel to '{ctx.channel.name}'",
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "setLogs", False)

    # Welcome message change
    @commands.command()
    async def welcome(self, ctx, channel: discord.TextChannel, *, msg):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "welcome", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            welcome1 = [str(channel.id), msg]

            id = self.config.getID(ctx)
            wlcm = self.config.get_server(str(id))
            wlcm["welcomeMsg"] = welcome1
            self.config.save()

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Welcome message has been changed to:\n{msg}",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} changed welcome message to '{msg}'",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "welcome", False)

    @commands.command()
    async def welcome_off(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "welcome_off", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            id = self.config.getID(ctx)
            wlcm = self.config.get_server(str(id))
            wlcm["welcomeMsg"] = []
            self.config.save()

            await ctx.channel.send(
                embed=discord.Embed(
                    description="Welcome message has been turned off",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} turned off welcome message",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "welcome_off", False)

    # Change prefix
    @commands.command()
    async def prefix(self, ctx, prefix):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "prefix", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            if len(prefix) <= 5:
                id = self.config.getID(ctx)
                prfx = self.config.get_server(str(id))
                prfx["Prefix"] = prefix
                self.config.save()

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Prefix has been changed to: `{prefix}`",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} changed prefix to '{prefix}'",
                    )
                )
            else:
                await ctx.channel.send("This prefix is too long, try with shorter one")
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "prefix", False)

    @commands.command(aliases=["frwd"])
    async def forward(self, ctx, serverID="False", sc="False"):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "forward", True)
        ):
            return

        id = self.config.getID(ctx)
        if "[DM]" in str(id):
            if serverID == "False":
                forw = self.config.get_server(str(id), "True")

                forw["forwarding"] = ""
                self.config.save()

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Forwarding has been disabled",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} disabled forwarding",
                    )
                )
            else:
                if sc != "False":
                    sc1 = self.config.get_server(str(serverID))
                    sc1 = sc1["secret_code"]

                    if str(sc1) == str(sc):
                        forw = self.config.get_server(str(id), "True")

                        forw["forwarding"] = str(serverID)
                        self.config.save()

                        await ctx.channel.send(
                            embed=discord.Embed(
                                description=f"Forwarding to {serverID} has been enabled",
                                colour=discord.Color.dark_blue(),
                            )
                        )
                        await asyncio.create_task(
                            self.config.prnt(
                                ctx,
                                f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} enabled forwarding to {serverID}",
                            )
                        )
                    else:
                        await ctx.channel.send(
                            embed=discord.Embed(
                                description=f"You don't have correct secret code",
                                colour=discord.Color.red(),
                            )
                        )
                else:
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"You have to give me secret code from that server",
                            colour=discord.Color.red(),
                        )
                    )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    description="It's only for direct messages",
                    colour=discord.Color.red(),
                )
            )
        await self.config.on_checkk(ctx, "forward", False)

    @commands.command(aliases=["frwdel"])
    async def forward_del(self, ctx, user):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "forward_del", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            id = self.config.getID(ctx)
            user = user.replace(" ", "")
            user = f"[DM] {user}"

            forw = self.config.get_server(str(user), "True")
            forw1 = forw["forwarding"]

            if str(forw1) != "" or str(forw1) == str(id):
                forw["forwarding"] = ""
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Forwarding from {user} has been disabled; Regenerate secret code to stop next forwarding",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} disabled forwarding from {user}",
                    )
                )
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"This user doesn't have forwarding to your server",
                        colour=discord.Color.red(),
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "forward_del", False)

    # Block Messages
    @commands.command(aliases=["bmsg", "block_msg"])
    @commands.guild_only()
    async def block_message(self, ctx, member: discord.Member):
        global on_check

        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "block_msg", True)
        ):
            return

        to_block = str(f"{ctx.message.guild.id}-{member.id}")
        usr_block = str(member.id)

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            if (
                to_block not in self.config.blocked
                and usr_block not in self.config.blocked
            ):
                if str(member) not in [
                    "Bartek#4660",
                    str(self.client.user),
                    str(ctx.author),
                ]:
                    to_block = str(f"{ctx.message.guild.id}-{member.id}")
                    self.config.blocked.append(to_block)
                    self.config.save()
                    await ctx.channel.send(
                        embed=discord.Embed(
                            title="Message Blocking",
                            description=f"Successfully blocked <@{member.id}> on this server",
                            colour=discord.Color.dark_blue(),
                            timestamp=datetime.utcnow(),
                        ).set_footer(
                            icon_url=ctx.author.avatar, text=f"Done by {ctx.author}"
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Blocking')} blocked {member} from using bAI",
                        )
                    )
                else:
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"You can't block this member",
                            colour=discord.Color.red(),
                        )
                    )
            else:
                if to_block in self.config.blocked:
                    self.config.blocked.remove(to_block)
                    self.config.save()

                    await ctx.channel.send(
                        embed=discord.Embed(
                            title="Message Blocking",
                            description=f"Successfully unblocked <@{member.id}> on this server",
                            colour=discord.Color.dark_blue(),
                            timestamp=datetime.utcnow(),
                        ).set_footer(
                            icon_url=ctx.author.avatar, text=f"Done by {ctx.author}"
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Blocking')} unblocked {member}",
                        )
                    )
                elif usr_block in self.config.blocked:
                    await ctx.channel.send(
                        embed=discord.Embed(
                            title="ERROR",
                            description="You dont have permition to do that",
                            colour=discord.Color.red(),
                            timestamp=datetime.utcnow(),
                        ).set_footer(
                            icon_url=ctx.author.avatar,
                            text=f"Created by {ctx.author}",
                        )
                    )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "block_msg", False)

        for checked in self.config.on_check:
            if str(member.id) in checked:
                del self.config.on_check[int(self.config.on_check.index(checked))]

    @commands.command(aliases=["whisb", "whoisblocked"])
    async def who_is_blocked(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "whoisblocked", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            blocked_yours = ""
            for item in self.config.blocked:
                if str(ctx.guild.id) in item:
                    blocked_yours += f"  {item}\n"

            if blocked_yours != "":
                await ctx.channel.send(
                    embed=discord.Embed(
                        title="Message Blocking",
                        description=f"Blocked user in this server:\n{blocked_yours}",
                        colour=discord.Color.dark_blue(),
                    )
                )
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"There are no blocked users in this server",
                        colour=discord.Color.dark_blue(),
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "whoisblocked", False)

    # Move someone to another channel
    @commands.command(aliases=["mv"])
    @commands.guild_only()
    @commands.cooldown(per=10, rate=1, type=BucketType.user)
    async def move(self, ctx, member: discord.Member, channel2: discord.VoiceChannel):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "move", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.move_members
        ):
            if str(member) in str(self.client.user):
                channel1 = ctx.author.voice.channel
                members = channel1.members
                for m in range(len(members)):
                    await members[m].move_to(channel2)
                    await asyncio.sleep(0.2)

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"{len(members)} users from channel {channel1.mention} moved to {channel2.mention}",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Voice')} {len(members)} users moved to {channel2}",
                    )
                )
            else:
                await member.move_to(channel2)

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"{member.mention} moved to {channel2.mention}",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Voice')} {member} moved to {channel2}",
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "move", False)

    # Mute & Deafen
    @commands.command()
    @commands.guild_only()
    async def mic(self, ctx, member: discord.Member, booL=False):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "mute", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.mute_members
        ):
            await member.edit(mute=booL)

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"{member.mention} muted state = {booL}",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Voice')} {member} muted state = {booL}",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "mute", False)

    @commands.command(aliases=["df"])
    @commands.guild_only()
    async def deafen(self, ctx, member: discord.Member, booL=False):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "deafen", True)
        ):
            return

        if str(ctx.author.id) in self.config.valid_users or (
            ctx.author.guild_permissions.deafen_members
            and ctx.author.guild_permissions.mute_members
        ):
            await member.edit(mute=booL, deafen=booL)

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"{member.mention} muted and deafen state = {booL}",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Voice')} {member} muted and deafen state = {booL}",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "deafen", False)

    # Roles
    @commands.command(aliases=["ar"])
    @commands.guild_only()
    async def add_role(self, ctx, member: discord.Member, role: discord.Role):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "addr", True)
        ):
            return

        pos = False
        if len(ctx.author.roles) != 0:
            if (
                ctx.author.roles[int(len(ctx.author.roles) - 1)].position
                > role.position
            ):
                pos = True

        if ctx.author.guild_permissions.manage_roles and (
            ctx.author == ctx.guild.owner or pos
        ):
            await member.add_roles(role)

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Added role {role.mention} to user {member.mention}",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Roles')} Added role '{role}' to user {member}",
                )
            )
        elif str(ctx.author.id) in self.config.valid_users:
            await member.add_roles(role)

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Added role {role.mention} to user {member.mention}",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Roles')} Added role '{role}' to user {member}",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "addr", False)

    @commands.command(aliases=["rr", "rm_role"])
    @commands.guild_only()
    async def remove_role(self, ctx, member: discord.Member, role: discord.Role):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "rmr", True)
        ):
            return

        pos = False
        if len(ctx.author.roles) != 0:
            if (
                ctx.author.roles[int(len(ctx.author.roles) - 1)].position
                > role.position
            ):
                pos = True

        if ctx.author.guild_permissions.manage_roles and (
            ctx.author == ctx.guild.owner or pos
        ):
            await member.remove_roles(role)

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Removed role {role.mention} from user {member.mention}",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Roles')} Removed role '{role}' from user {member}",
                )
            )
        elif str(ctx.author.id) in self.config.valid_users:
            await member.remove_roles(role)

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Removed role {role.mention} from user {member.mention}",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Roles')} Removed role '{role}' from user {member}",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "rmr", False)

    # Kick & Ban
    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason="Not provided"):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "kick", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.kick_members
        ):
            if str(member) not in [
                "Bartek#4660",
                str(self.client.user),
                str(ctx.author),
            ]:
                await ctx.guild.kick(member, reason=reason)

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Kicked: `{member}`\nReason: `{reason}`",
                        colour=discord.Color.dark_blue(),
                        timestamp=datetime.utcnow(),
                    ).set_footer(
                        icon_url=ctx.author.avatar, text=f"Done by {ctx.author}"
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Get Out')} kicked {member}, reason = {reason}",
                    )
                )
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"You can't kick this member",
                        colour=discord.Color.red(),
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "kick", False)

    @commands.command()
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason="Not provided"):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "ban", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.ban_members
        ):
            if str(member) not in [
                "Bartek#4660",
                str(self.client.user),
                str(ctx.author),
            ]:
                await ctx.guild.ban(member, reason=reason)

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Banned: `{member}`\nResone: `{reason}`",
                        colour=discord.Color.dark_blue(),
                        timestamp=datetime.utcnow(),
                    ).set_footer(
                        icon_url=ctx.author.avatar, text=f"Done by {ctx.author}"
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Get Out')} baned {member}, reason = {reason}",
                    )
                )
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"You can't ban this member",
                        colour=discord.Color.red(),
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "ban", False)

    @commands.command()
    @commands.guild_only()
    async def unban(self, ctx, member):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "unban", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.ban_members
        ):
            test = None
            bans = await ctx.guild.bans()
            for ban in bans:
                if str(ban.user) == member:
                    await ctx.guild.unban(ban.user)

                    test = await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"Unbaned `{member}`",
                            colour=discord.Color.dark_blue(),
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Get Out')} ubaned {member}",
                        )
                    )
                    break

            if test == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"This member isn't baned",
                        colour=discord.Color.dark_blue(),
                    )
                )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "unban", False)

    # Clear
    @commands.command(name="clear", aliases=["c", "cls", "cl"])
    @commands.guild_only()
    async def clear(self, ctx, amount=1):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "clear", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.manage_messages
        ):
            try:
                if int(amount) > 100:
                    amount = 1
            except:
                amount = 1

            delated_msgs = await ctx.channel.purge(limit=int(amount) + 1)
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Clear')} delated {len(delated_msgs) - 1} messages from channel {ctx.channel.id}",
                    True,
                )
            )

            await self.config.on_checkk(ctx, "clear", False)

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Successfully cleared `{len(delated_msgs) - 1}` messages",
                    colour=discord.Color.dark_blue(),
                ),
                delete_after=5,
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="ERROR",
                    description="You dont have permition to do that",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(
                    icon_url=ctx.author.avatar, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "clear", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        self.config.on_check = []


# Setting up the cog
async def setup(client):
    await client.add_cog(Admin(client))
