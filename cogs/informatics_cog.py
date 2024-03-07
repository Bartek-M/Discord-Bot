# Importing Modules
import discord
from discord.ext import commands

# Informatics Class
class Informatics(commands.Cog):
    def __init__(self, client, config):
        self.client = client
        self.config = config

    # Converting to decimal
    def convert_decimal(self, to_convert):
        deci_output = []

        for i in range(len(to_convert)):
            num = 0
            decimal = 0
            converting = to_convert[i][::-1]

            for item in list(converting):
                if item == "1":
                    decimal += 2 ** num
                num += 1
            deci_output.append(str(decimal))

        return deci_output

    # Converting to binary
    def convert_binary(self, to_convert, bit=0):
        bin_output = []

        for i in range(len(to_convert)):
            number = list(str(bin(int(to_convert[i]))).replace("0b", ""))
            for j in range(bit - len(number)):
                number.insert(0, "0")
            number = "".join(number)
            bin_output.append(number)

        return bin_output

    # Get network data
    @commands.command(aliases=["ip", "net"])
    async def network(self, ctx, ip, mask="0"):
        if (await self.config.blockCheck(ctx)) or not (await self.config.on_checkk(ctx, "network", True)):
            return

        # Check if valid
        example_ip, example_mask = "192.168.1.0", "255.255.255.0"
        test_ip, test_mask = ip.split("."), mask.split(".")

        if mask == "0":
            test_mask = ["0", "0", "0", "0"]

        if ip.count(".") != 3 or len(test_ip) != 4 or ((len(test_mask) != 4 or mask.count(".") != 3) and mask != "0"):
            await ctx.channel.send(embed=discord.Embed(description=f"Wrong IP or mask format. Example: `{example_ip} and {example_mask}`", colour=discord.Color.red()))
            await self.config.on_checkk(ctx, "network", False)
            return
        
        for i in range(len(test_ip)):
            try:
                isinstance(test_ip[i], int) 
                isinstance(test_mask[i], int)

                if int(test_ip[i]) > 255 or (int(test_mask[i]) > 255 and mask != "0"):
                    await ctx.channel.send(embed=discord.Embed(description=f"Max value of IP or mask is 255. Example: `{example_ip} and {example_mask}`", colour=discord.Color.red()))
                    await self.config.on_checkk(ctx, "network", False)
                    return

            except ValueError:
                await ctx.channel.send(embed=discord.Embed(description=f"IP or mask must be a number. Example: `{example_ip} and {example_mask}`", colour=discord.Color.red()))
                await self.config.on_checkk(ctx, "network", False)
                return

        # Converting to ip to binary
        ip = {"bin":[], "deci":ip.split(".")}
        ip["bin"] = self.convert_binary(ip["deci"], 8)


        # Getting network class
        first_num = int(ip["deci"][0])

        network_classes = {"A":[0, 126, 8, "255.0.0.0"], "B":[128, 191, 16, "255.255.0.0"], "C":[192, 223, 24, "255.255.255.0"], "D":[224, 239, 0], "E":[240, 254, 0], "LOCAL":[127, 127, 8, "255.0.0.0"]}
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
                        await ctx.channel.send(embed=discord.Embed(description=f"You have to specify mask for this IP", colour=discord.Color.red()))
                        await self.config.on_checkk(ctx, "network", False)
                        return
                    mask = network_classes[key][3]
                break
        

        # Converting to mask to binary
        mask = {"bin":[], "deci":mask.split(".")}
        mask["bin"] = self.convert_binary(mask["deci"], 8)

        # Getting network adres
        network_adress = {"bin":[], "deci":[]}

        for i in range(len(ip["bin"])):
            number = ""
            for j in range(len(ip["bin"][i])):
                if int(list(mask["bin"][i])[j]) == 1:
                    number += list(ip["bin"][i])[j]
                else:
                    number += "0"

            network_adress["bin"].append(number)

        network_adress["deci"] = self.convert_decimal(network_adress["bin"])


        # Getting broadcast
        broadcast = {"bin":[], "deci":[]}

        for i in range(len(ip["bin"])):
            number = ""
            for j in range(len(ip["bin"][i])):
                if int(list(mask["bin"][i])[j]) == 1:
                    number += list(ip["bin"][i])[j]
                else:
                    number += "1"

            broadcast["bin"].append(number)

        broadcast["deci"] = self.convert_decimal(broadcast["bin"])


        # Getting number of hosts and subnets
        min_host = [network_adress["deci"][0], network_adress["deci"][1], network_adress["deci"][2], str(int(network_adress["deci"][3]) + 1)]
        max_host = [broadcast["deci"][0], broadcast["deci"][1], broadcast["deci"][2], str(int(broadcast["deci"][3]) - 1)]

        num_host = 2 ** ".".join(mask["bin"]).count("0") - 2
        num_subnet = 2 ** int("".join(mask["bin"]).count("1") - network_classes[current_class][2])

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
        await ctx.channel.send(embed=discord.Embed(title="IPv4 Calculator", description=desc, colour=discord.Color.dark_blue()))

        await self.config.on_checkk(ctx, "network", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return
            
        self.config.on_check = []