import re
import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from . import config


class School(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = config

    # Remove test
    @commands.command(aliases=["rt", "rmtest"])
    async def remove_test(self, ctx, rmtest1: int):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "rmTest", True)
        ):
            return

        id = self.config.getID(ctx)
        spcificSrvr = self.config.get_server(str(id))
        f = spcificSrvr["Tests"]
        removedTest = f[rmtest1 - 1].capitalize().replace("\n", " ")
        f.remove(f[rmtest1 - 1])
        self.config.save()

        await ctx.channel.send(
            embed=discord.Embed(
                title="Test Management",
                description=f"Successfully removed test: `{removedTest}`",
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
        )
        await asyncio.create_task(
            self.config.prnt(
                ctx,
                f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Test Management')} removed test: {removedTest}",
            )
        )
        await self.config.on_checkk(ctx, "rmTest", False)

    # Check all tests
    @commands.command(aliases=["gt", "gettest"])
    async def get_test(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "getTest", True)
        ):
            return

        id = self.config.getID(ctx)
        spcificSrvr = self.config.get_server(str(id))
        tests = spcificSrvr["Tests"]

        sorted_Tests = {}
        a = 0

        for test in tests:
            try:
                temp_test = test.replace("-", ".").strip()
                match = re.search(r"\d{2}.\d{2}.\d{4}", temp_test)
                if match == None:
                    match2 = re.search(r"\d{2}.\d{2}.\d{2}", temp_test)
                    match2 = str(match2.group())

                    year = str(datetime.now().year)[:-2]
                    match = match2[:-2] + year + match2[-2:]
                else:
                    match = str(match.group())

                date = datetime.strptime(match, "%d.%m.%Y").date()

                try:
                    sorted_Tests[str(date)]
                    sorted_Tests[str(f"{date}|{a}")] = test
                except:
                    sorted_Tests[str(date)] = test
            except:
                sorted_Tests[str(a)] = test

            a += 1

        srtd = sorted(sorted_Tests)
        sorted_Tests2 = []
        for item in srtd:
            sorted_Tests2.append(sorted_Tests[item])

        spcificSrvr["Tests"] = sorted_Tests2
        self.config.save()

        num = 1
        b = ""
        for line in sorted_Tests2:
            if line != "":
                b += str(f"`[{num}]` {line}\n")
                num += 1
        if num != 1:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Test Management",
                    description=b,
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Test Management",
                    description=f"You don't have any tests",
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
        await self.config.on_checkk(ctx, "getTest", False)

        await asyncio.sleep(5)
        try:
            await ctx.message.delete()
        except:
            pass

    # Add new test
    @commands.command(aliases=["nt", "newtest"])
    async def new_test(self, ctx, *, newtest):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "newTest", True)
        ):
            return

        if len(newtest) <= 160:
            newtest1 = newtest
            id = self.config.getID(ctx)
            spcificSrvr = self.config.get_server(str(id))
            tests = spcificSrvr["Tests"]
            tests.append(newtest1)
            self.config.save()

            await ctx.channel.send(
                embed=discord.Embed(
                    title="Test Management",
                    description=f"Successfully added new test: `{newtest}`",
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Test Management')} added new test: {newtest1}",
                )
            )

        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Test Management",
                    description=f"Error to add new test - Subject is too long! (Max 160 Characters)",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )

        await self.config.on_checkk(ctx, "newTest", False)

    # Edit test
    @commands.command(aliases=["et", "edittest"])
    async def edit_test(self, ctx, num: int, *, edittest):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "editTest", True)
        ):
            return

        if len(edittest) <= 160:
            id = self.config.getID(ctx)
            spcificSrvr = self.config.get_server(str(id))
            tests = spcificSrvr["Tests"]
            tests[num - 1] = str(edittest)
            self.config.save()

            await ctx.channel.send(
                embed=discord.Embed(
                    title="Test Management",
                    description=f"Successfully edited test `[{num}]`:` {edittest}`",
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Test Management')} edited test [{num}]: {edittest}",
                )
            )

        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Test Management",
                    description=f"Error to add edited test - Subject is too long! (Max 160 Characters)",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )

        await self.config.on_checkk(ctx, "editTest", False)

    # Remove homework
    @commands.command(aliases=["rh", "rmhw"])
    async def remove_homework(self, ctx, rmHW1: int):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "rmHW", True)
        ):
            return

        id = self.config.getID(ctx)
        spcificSrvr = self.config.get_server(str(id))
        f = spcificSrvr["Homeworks"]
        removedHW = f[rmHW1 - 1].capitalize().replace("\n", " ")
        f.remove(f[rmHW1 - 1])
        self.config.save()

        await ctx.channel.send(
            embed=discord.Embed(
                title="Homework Management",
                description=f"Successfully removed homework: `{removedHW}`",
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
        )
        await asyncio.create_task(
            self.config.prnt(
                ctx,
                f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Homework Management')} removed homework: {removedHW}",
            )
        )
        await self.config.on_checkk(ctx, "rmHW", False)

    # Check all homeworks
    @commands.command(aliases=["gh", "gethw"])
    async def get_homework(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "getHW", True)
        ):
            return

        id = self.config.getID(ctx)
        spcificSrvr = self.config.get_server(str(id))
        homeW = spcificSrvr["Homeworks"]

        sorted_HW = {}
        a = 0

        for hw in homeW:
            try:
                temp_hw = hw.replace("-", ".").strip()
                match = re.search(r"\d{2}.\d{2}.\d{4}", temp_hw)
                if match == None:
                    match2 = re.search(r"\d{2}.\d{2}.\d{2}", temp_hw)
                    match2 = str(match2.group())

                    year = str(datetime.now().year)[:-2]
                    match = match2[:-2] + year + match2[-2:]
                else:
                    match = str(match.group())

                date = datetime.strptime(match, "%d.%m.%Y").date()

                try:
                    sorted_HW[str(date)]
                    sorted_HW[str(f"{date}|{a}")] = hw
                except:
                    sorted_HW[str(date)] = hw
            except:
                sorted_HW[str(a)] = hw

            a += 1

        srtd = sorted(sorted_HW)
        sorted_HW2 = []
        for item in srtd:
            sorted_HW2.append(sorted_HW[item])

        spcificSrvr["Homeworks"] = sorted_HW2
        self.config.save()

        num = 1
        a = ""
        for line in sorted_HW2:
            if line != "":
                a += str(f"`[{num}]` {line}\n")
                num += 1
        if num != 1:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Homework Management",
                    description=a,
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Homework Management",
                    description=f"You don't have any homework",
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
        await self.config.on_checkk(ctx, "getHW", False)

        await asyncio.sleep(5)
        try:
            await ctx.message.delete()
        except:
            pass

    # Add new homework
    @commands.command(aliases=["nh", "newhw"])
    async def new_homework(self, ctx, *, newhw):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "newHW", True)
        ):
            return
        if len(newhw) <= 160:
            newHW1 = newhw
            id = self.config.getID(ctx)
            spcificSrvr = self.config.get_server(str(id))
            homeW = spcificSrvr["Homeworks"]
            homeW.append(newHW1)
            self.config.save()

            await ctx.channel.send(
                embed=discord.Embed(
                    title="Homework Management",
                    description=f"Successfully added new homework: `{newhw}`",
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Homework Management')} added new homework: {newHW1}",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Homework Management",
                    description=f"Error to add Homework - Subject is too long! (Max 160 Characters)",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )

        await self.config.on_checkk(ctx, "newHW", False)

    # Edit homework
    @commands.command(aliases=["eh", "edithw"])
    async def edit_homework(self, ctx, num: int, *, edithw):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "edithw", True)
        ):
            return
        if len(edithw) <= 160:
            id = self.config.getID(ctx)
            spcificSrvr = self.config.get_server(str(id))
            homeW = spcificSrvr["Homeworks"]
            homeW[num - 1] = str(edithw)
            self.config.save()

            await ctx.channel.send(
                embed=discord.Embed(
                    title="Homework Management",
                    description=f"Successfully edited homework `[{num}]`:` {edithw}`",
                    colour=discord.Color.dark_blue(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )
            await asyncio.create_task(
                self.config.prnt(
                    ctx,
                    f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Homework Management')} edited homework [{num}]: {edithw}",
                )
            )
        else:
            await ctx.channel.send(
                embed=discord.Embed(
                    title="Homework Management",
                    description=f"Error to add edited Homework - Subject is too long! (Max 160 Characters)",
                    colour=discord.Color.red(),
                    timestamp=datetime.utcnow(),
                ).set_footer(icon_url=ctx.author.avatar, text=f"Done by {ctx.author}")
            )

        await self.config.on_checkk(ctx, "edithw", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        self.config.on_check = []


async def setup(client):
    await client.add_cog(School(client))
