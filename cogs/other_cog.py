# Importing Modules
import discord
import random
import asyncio
from urllib.request import urlopen
from metar import Metar
from discord.ext import commands
from datetime import datetime


class Utilities(commands.Cog):
    def __init__(self, client, config):
        self.client = client
        self.config = config

    @commands.command()
    async def metar(self, ctx, station):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "metar", True)
        ):
            return

        station = str(station).upper()

        BASE_URL = "http://tgftp.nws.noaa.gov/data/observations/metar/stations"
        url = "%s/%s.TXT" % (BASE_URL, station)

        try:
            urlh = urlopen(url)
            report = ""
            for line in urlh:
                if not isinstance(line, str):
                    line = line.decode()

                if line.startswith(station):
                    report = line.strip().upper()
                    list_report = report.split()
                    obs = Metar.Metar(line)
                    report1 = "**Raw Report:**\n  ```" + str(report)
                    report1 += "```\n\n**Readable Report:**```\n"
                    for line1 in str(obs.string()).split("\n"):
                        if "METAR" not in line1:
                            if "wind" in line1:
                                for i in range(len(list_report)):
                                    if "KT" in list_report[i]:
                                        report1 += f"  Wind: {list_report[i][:3]} at {list_report[i][:-2][3:]} knots"
                                        report1 += "\n"
                                        break
                            else:
                                if len(line1) > 0:
                                    report1 += (
                                        "  " + str(line1)[0].upper() + str(line1)[1:]
                                    )
                                    report1 += "\n"

                    report1 += "```"

                    author = ctx.message.author
                    pfp = author.avatar_url

                    embed = discord.Embed(
                        title=f"**{station} Metar Report**",
                        description=report1,
                        colour=discord.Color.dark_blue(),
                    )
                    embed.set_footer(icon_url=pfp, text=f"Checked by {ctx.author}")
                    await ctx.channel.send(embed=embed)

                    break
            if not report:
                await ctx.channel.send(f"No data for {station}")
        except:
            await ctx.channel.send(f"Error retrieving {station} data")

        await asyncio.create_task(
            self.config.prnt(
                None,
                f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Metar')} checked metar for {station}",
                False,
            )
        )
        await self.config.on_checkk(ctx, "metar", False)

    # Random things
    @commands.command(aliases=["rand"])
    async def random_get(self, ctx, num, *, things=""):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "random_get", True)
        ):
            return

        if things.strip() == "":
            things = num
            num = 1
        else:
            things = things.split()
            if len(things) == 1:
                things = int(things[0])

        if int(num) >= 20:
            num = 20

        result = ""

        num = int(num) + 1

        for i in range(int(num)):
            if isinstance(things, list):
                rand = str(random.choice(things))
                if rand in result:
                    rand = str(random.choice(things))
                result += rand
                result += "\n"
            else:
                rand = str(random.randint(1, int(things)))
                if rand in result:
                    result += rand
                    result += "\n"

        await ctx.channel.send(
            embed=discord.Embed(
                description=f"**Your results:** ```{result}```",
                colour=discord.Color.dark_blue(),
            )
        )
        await asyncio.create_task(
            self.config.prnt(
                None,
                f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Random')} got something randomly",
                False,
            )
        )

        await self.config.on_checkk(ctx, "random_get", False)

    # Change Nick
    @commands.command(aliases=["n"])
    @commands.guild_only()
    async def nick(self, ctx, member: discord.Member, *, nick=""):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "nick", True)
        ):
            return

        if member == ctx.author or member == "":
            if (
                str(ctx.author.id) in self.config.valid_users
                or ctx.author.guild_permissions.change_nickname
            ):
                await ctx.author.edit(nick=nick)
                if nick != "":
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"Your nickname changed to {nick}",
                            colour=discord.Color.dark_blue(),
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Nick Change')} changed nickname to {nick}",
                        )
                    )
                else:
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"Cleared your nickname",
                            colour=discord.Color.dark_blue(),
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Nick Change')} cleared their nickname",
                        )
                    )
        else:
            if (
                str(ctx.author.id) in self.config.valid_users
                or ctx.author.guild_permissions.change_nickname
            ):
                await member.edit(nick=nick)
                if nick != "":
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"{member.mention} nicname changed to {nick}",
                            colour=discord.Color.dark_blue(),
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Nick Change')} self nickname changed to {nick}",
                        )
                    )
                else:
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"{member.mention} nickname cleared",
                            colour=discord.Color.dark_blue(),
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Nick Change')} self nickname cleared",
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
                        icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"
                    )
                )

        await self.config.on_checkk(ctx, "nick", False)

    # Ping check
    @commands.command()
    async def ping(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "ping", True)
        ):
            return

        await ctx.channel.send(
            embed=discord.Embed(
                description=f"**Pong!** Latance: {round(self.client.latency * 100)}ms",
                colour=discord.Color.dark_blue(),
            )
        )
        await self.config.on_checkk(ctx, "ping", False)

    # Fetch User or Server
    @commands.command()
    async def fetch_user(self, ctx, id):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "fetch_user", True)
        ):
            return

        member = await self.client.fetch_user(id)

        id = member.id
        pic = member.avatar_url
        bot = member.bot
        created_at = member.created_at.strftime("%d/%m/%Y")

        await ctx.channel.send(
            embed=discord.Embed(
                title="User Fetch",
                description=f"User: `{member}`\n ID: `{id}`\n Bot: `{bot}`\n Created at: `{created_at}`\n",
                colour=discord.Color.dark_blue(),
                timestamp=datetime.utcnow(),
            )
            .set_thumbnail(url=pic)
            .set_footer(icon_url=ctx.author.avatar_url, text=f"Checked by {ctx.author}")
        )

        await self.config.on_checkk(ctx, "fetch_user", False)

    # Roll through channels
    @commands.command(aliases=["rl"])
    @commands.guild_only()
    async def roll(self, ctx, member: discord.Member):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "roll", True)
        ):
            return

        valid_servers = [
            "867860377081872425",
            "788900116521680937",
            "902435317649375272",
            "801412029411885067",
            "706128112701800506",
        ]
        if str(ctx.guild.id) not in str(valid_servers):
            await self.config.on_checkk(ctx, "roll", False)
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.move_members
        ):
            if not ctx.message.author.voice:
                await ctx.channel.send(
                    ":x: You have to be in a voice channel to use this command."
                )
                await self.config.on_checkk(ctx, "roll", False)
                return

            voice_channel_list = ctx.guild.voice_channels

            if str(member) not in ["Bartek#4660", str(self.client.user)]:
                try:
                    memver_voiceChannel = member.voice.channel
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"Moving {member.mention} through the channels",
                            colour=discord.Color.dark_blue(),
                        )
                    )
                    await asyncio.create_task(
                        self.config.prnt(
                            ctx,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Voice')} is rollig {member}",
                        )
                    )

                    a = 0
                    for channel in voice_channel_list:
                        if a != 5:
                            try:
                                await member.move_to(channel)
                            except:
                                await ctx.channel.send(
                                    embed=discord.Embed(
                                        description=f"I failed to do that",
                                        colour=discord.Color.red(),
                                    )
                                )
                                break
                        else:
                            break
                        a += 1
                        await asyncio.sleep(1.5)

                    try:
                        await member.move_to(memver_voiceChannel)
                    except:
                        pass

                except:
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"This user isn't currently in the voice channel",
                            colour=discord.Color.red(),
                        )
                    )
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"You can't roll this user",
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
                    icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "roll", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        self.config.on_check = []


# Setting up the cog
def setup(client, config):
    client.add_cog(Utilities(client, config))
