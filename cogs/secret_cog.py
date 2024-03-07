import discord
import asyncio
import os
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound
from datetime import datetime


class Secret(commands.Cog):
    def __init__(self, client, config):
        self.client = client
        self.config = config

    # Add or Remove valid user
    @commands.command(aliases=["av", "add_vu"])
    async def add_valid_user(self, ctx, member: discord.Member):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "addVU", True)
        ):
            return

        if str(ctx.author.id) in self.config.valid_users:
            if str(member) not in self.config.valid_users:
                self.config.valid_users.append(str(member.id))
                self.config.save()

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Added new valid user - {member}",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} Added new valid user - {member}",
                        False,
                    )
                )
            else:
                await ctx.channel.send("This user is already valid user")
        else:
            raise CommandNotFound

        await self.config.on_checkk(ctx, "addVU", False)

    @commands.command(aliases=["rv", "rm_vu"])
    async def remove_valid_user(self, ctx, member: discord.Member):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "rmVU", True)
        ):
            return

        if str(ctx.author.id) in self.config.valid_users:
            if str(member) not in ["Bartek#4660", str(self.client.user)]:
                self.config.valid_users.remove(str(member.id))
                self.config.save()

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Removed valid user - {member}",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Config')} Removed valid user - {member}",
                        False,
                    )
                )
            else:
                await ctx.channel.send("You can't remove this valid user")
        else:
            raise CommandNotFound

        await self.config.on_checkk(ctx, "rmVU", False)

    @commands.command(aliases=["busr", "block_usr"])
    async def block_user(self, ctx, id):
        global on_check

        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "block_usr", True)
        ):
            return

        to_block = str(id)
        if str(ctx.author.id) in self.config.valid_users:
            if to_block not in self.config.blocked:
                if str(id) not in self.config.valid_users:
                    self.config.blocked.append(to_block)
                    self.config.save()
                    await ctx.channel.send(
                        embed=discord.Embed(
                            title="Message Blocking",
                            description=f"Successfully blocked {id} user everywhere",
                            colour=discord.Color.dark_blue(),
                            timestamp=datetime.utcnow(),
                        ).set_footer(
                            icon_url=ctx.author.avatar_url, text=f"Done by {ctx.author}"
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Blocking')} blocked {id} user",
                            False,
                        )
                    )
                else:
                    await ctx.channel.send("You can't block this member")
            else:
                self.config.blocked.remove(to_block)
                self.config.save()
                await ctx.channel.send(
                    embed=discord.Embed(
                        title="Message Blocking",
                        description=f"Successfully unblocked {id} user everywhere",
                        colour=discord.Color.dark_blue(),
                        timestamp=datetime.utcnow(),
                    ).set_footer(
                        icon_url=ctx.author.avatar_url, text=f"Done by {ctx.author}"
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Blocking')} unblocked {id} user",
                        False,
                    )
                )
        else:
            raise CommandNotFound

        await self.config.on_checkk(ctx, "block_usr", False)

        for checked in self.config.on_check:
            if str(id) in checked:
                del self.config.on_check[self.config.on_check.index(checked)]

    @commands.command(aliases=["bsrv", "block_srv"])
    async def block_server(self, ctx, id):
        global on_check

        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "block_srv", True)
        ):
            return

        to_block = str(f"{id}")
        if str(ctx.author.id) in self.config.valid_users:
            if to_block not in self.config.blocked_server:
                self.config.blocked_server.append(to_block)
                self.config.save()
                await ctx.channel.send(
                    embed=discord.Embed(
                        title="Server Blocking",
                        description=f"Successfully blocked {id} server",
                        colour=discord.Color.dark_blue(),
                        timestamp=datetime.utcnow(),
                    ).set_footer(
                        icon_url=ctx.author.avatar_url, text=f"Done by {ctx.author}"
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Blocking')} blocked {id} server",
                        False,
                    )
                )
            else:
                self.config.blocked_server.remove(to_block)
                self.config.save()
                await ctx.channel.send(
                    embed=discord.Embed(
                        title="Server Blocking",
                        description=f"Successfully unblocked {id} server",
                        colour=discord.Color.dark_blue(),
                        timestamp=datetime.utcnow(),
                    ).set_footer(
                        icon_url=ctx.author.avatar_url, text=f"Done by {ctx.author}"
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Blocking')} unblocked {id} server",
                        False,
                    )
                )
        else:
            raise CommandNotFound

        await self.config.on_checkk(ctx, "block_srv", False)

        for checked in self.config.on_check:
            if str(id) in checked:
                del self.config.on_check[self.config.on_check.index(checked)]

    @commands.command(aliases=["c_cons"])
    async def clear_console(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "clear_console", True)
        ):
            return

        if str(ctx.author.id) in self.config.valid_users:
            os.system("clear")
            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Successfully cleared console",
                    colour=discord.Color.dark_blue(),
                )
            )
            await asyncio.create_task(
                self.config.prnt(
                    None,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Clear')} cleared console",
                    False,
                )
            )
        else:
            raise CommandNotFound

        await self.config.on_checkk(ctx, "clear_console", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        self.config.on_check = []


# Setting up the cog
def setup(client, config):
    client.add_cog(Secret(client, config))
