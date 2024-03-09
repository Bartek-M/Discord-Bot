# Importing Modules
import random
import asyncio
from urllib.request import urlopen
from datetime import datetime

import discord
from discord.ext import commands
from metar import Metar

from . import config


class Utilities(commands.Cog):
    def __init__(self, client):
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
                    pfp = author.avatar

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

    @commands.command(aliases=["ip", "net"])
    async def network(self, ctx, ip, mask="0"):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "network", True)
        ):
            return

        # Check if valid
        example_ip, example_mask = "192.168.1.0", "255.255.255.0"
        test_ip, test_mask = ip.split("."), mask.split(".")

        if mask == "0":
            test_mask = ["0", "0", "0", "0"]

        if (
            ip.count(".") != 3
            or len(test_ip) != 4
            or ((len(test_mask) != 4 or mask.count(".") != 3) and mask != "0")
        ):
            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Wrong IP or mask format. Example: `{example_ip} and {example_mask}`",
                    colour=discord.Color.red(),
                )
            )
            await self.config.on_checkk(ctx, "network", False)
            return

        for i in range(len(test_ip)):
            try:
                isinstance(test_ip[i], int)
                isinstance(test_mask[i], int)

                if int(test_ip[i]) > 255 or (int(test_mask[i]) > 255 and mask != "0"):
                    await ctx.channel.send(
                        embed=discord.Embed(
                            description=f"Max value of IP or mask is 255. Example: `{example_ip} and {example_mask}`",
                            colour=discord.Color.red(),
                        )
                    )
                    await self.config.on_checkk(ctx, "network", False)
                    return

            except ValueError:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"IP or mask must be a number. Example: `{example_ip} and {example_mask}`",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "network", False)
                return

        # Converting to ip to binary
        ip = {"bin": [], "deci": ip.split(".")}
        ip["bin"] = convert_binary(ip["deci"], 8)

        # Getting network class
        first_num = int(ip["deci"][0])

        network_classes = {
            "A": [0, 126, 8, "255.0.0.0"],
            "B": [128, 191, 16, "255.255.0.0"],
            "C": [192, 223, 24, "255.255.255.0"],
            "D": [224, 239, 0],
            "E": [240, 254, 0],
            "LOCAL": [127, 127, 8, "255.0.0.0"],
        }
        current_class = ""

        for key in network_classes:
            if key == "LOCAL" and (first_num == network_classes[key][0]):
                current_class = key
                mask = network_classes[key][3]
                break

            if network_classes[key][0] <= first_num <= network_classes[key][1]:
                current_class = key
                if mask == "0":
                    if key == "D" or key == "E":
                        await ctx.channel.send(
                            embed=discord.Embed(
                                description=f"You have to specify mask for this IP",
                                colour=discord.Color.red(),
                            )
                        )
                        await self.config.on_checkk(ctx, "network", False)
                        return
                    mask = network_classes[key][3]
                break

        # Converting to mask to binary
        mask = {"bin": [], "deci": mask.split(".")}
        mask["bin"] = convert_binary(mask["deci"], 8)

        # Getting network adres
        network_adress = {"bin": [], "deci": []}

        for i in range(len(ip["bin"])):
            number = ""
            for j in range(len(ip["bin"][i])):
                if int(list(mask["bin"][i])[j]) == 1:
                    number += list(ip["bin"][i])[j]
                else:
                    number += "0"

            network_adress["bin"].append(number)

        network_adress["deci"] = convert_decimal(network_adress["bin"])

        # Getting broadcast
        broadcast = {"bin": [], "deci": []}

        for i in range(len(ip["bin"])):
            number = ""
            for j in range(len(ip["bin"][i])):
                if int(list(mask["bin"][i])[j]) == 1:
                    number += list(ip["bin"][i])[j]
                else:
                    number += "1"

            broadcast["bin"].append(number)

        broadcast["deci"] = convert_decimal(broadcast["bin"])

        # Getting number of hosts and subnets
        min_host = [
            network_adress["deci"][0],
            network_adress["deci"][1],
            network_adress["deci"][2],
            str(int(network_adress["deci"][3]) + 1),
        ]
        max_host = [
            broadcast["deci"][0],
            broadcast["deci"][1],
            broadcast["deci"][2],
            str(int(broadcast["deci"][3]) - 1),
        ]

        num_host = 2 ** ".".join(mask["bin"]).count("0") - 2
        num_subnet = 2 ** int(
            "".join(mask["bin"]).count("1") - network_classes[current_class][2]
        )

        total_hosts = ""
        if num_subnet != 1:
            total_hosts = f"\nNumber of all usable hosts = {num_host * num_subnet}"

        # Output information
        desc = f"""
```
IP = {'.'.join(ip['deci'])}  ||  {'.'.join(ip['bin'])}
Mask = {'.'.join(mask['deci'])} (/{str(''.join(mask['bin'])).count('1')})  ||  {'.'.join(mask['bin'])}

Class = {current_class}  ||  Range: {network_classes[current_class][0]} - {network_classes[current_class][1]}; Default Mask: /{network_classes[current_class][2]}

Network adress = {'.'.join(network_adress['deci'])}  ||  {'.'.join(network_adress['bin'])}

Broadcast = {'.'.join(broadcast['deci'])}  ||  {'.'.join(broadcast['bin'])}

Min host = {'.'.join(min_host)}
Max host = {'.'.join(max_host)}

Number of usable hosts per subnet = {num_host}{total_hosts}
Number of subnets = {num_subnet}


128  |  64  |  32  |  16  |  8  |  4  |  2  |  1
```
        """
        await ctx.channel.send(
            embed=discord.Embed(
                title="IPv4 Calculator",
                description=desc,
                colour=discord.Color.dark_blue(),
            )
        )

        await self.config.on_checkk(ctx, "network", False)

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

    @commands.command()
    async def fetch_user(self, ctx, id):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "fetch_user", True)
        ):
            return

        member = await self.client.fetch_user(id)

        id = member.id
        pic = member.avatar
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
            .set_footer(icon_url=ctx.author.avatar, text=f"Checked by {ctx.author}")
        )

        await self.config.on_checkk(ctx, "fetch_user", False)

    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        self.config.on_check = []


def convert_decimal(to_convert):
    deci_output = []

    for i in range(len(to_convert)):
        num = 0
        decimal = 0
        converting = to_convert[i][::-1]

        for item in list(converting):
            if item == "1":
                decimal += 2**num
            num += 1
        deci_output.append(str(decimal))

    return deci_output


def convert_binary(to_convert, bit=0):
    bin_output = []

    for i in range(len(to_convert)):
        number = list(str(bin(int(to_convert[i]))).replace("0b", ""))
        for _ in range(bit - len(number)):
            number.insert(0, "0")

        number = "".join(number)
        bin_output.append(number)

    return bin_output


async def setup(client):
    await client.add_cog(Utilities(client))