import discord
import asyncio
from datetime import datetime
from discord.ext import commands
#from ext.config import Config

# TODO: add poll system and auto roles

# Auto Roles Class
class Auto_Roles(commands.Cog):
    def __init__(self, client, config):
        self.client = client
        self.config = config #Config(client)

    # Create reaction role message
    @commands.command(aliases=["reaction"])
    @commands.guild_only()
    async def reaction_role(self, ctx, *, msg):
        if (await self.config.blockCheck(ctx)) or not (await self.config.on_checkk(ctx, "autoR", True)):
            return

        if str(ctx.author.id) in self.config.valid_users or ctx.author.guild_permissions.manage_roles:
            embed = discord.Embed(description=msg, colour=discord.Color.dark_blue(),)

            id = self.config.getID(ctx)
            spcificSrvr = self.config.specifSRVR(id)
            autoRole = spcificSrvr["Reactions"]

            if int(len(autoRole) + 1) > 10:
                await ctx.channel.send(embed=discord.Embed(description="You've reached reaction role limit. To add reaction roles remove some", colour=discord.Color.red()))
                self.config.on_checkk(ctx, "autoR", False)
                return

            sent = await ctx.channel.send(embed=embed)
            sent = sent.id

            autoRole[sent] = []
            self.config.save()

            msg = await ctx.fetch_message(sent)
            await ctx.channel.send(embed=discord.Embed(description=f"Message sent, now add some configurations for it", colour=discord.Color.dark_blue()), delete_after=20)
            await asyncio.create_task(self.config.prnt(ctx,f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Auto Role')} added new auto role message",))
        else:
            await ctx.channel.send(embed=discord.Embed(title="ERROR", description="You dont have permition to do that", colour=discord.Color.red(), timestamp=datetime.utcnow()).set_footer(icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"))

        await self.config.on_checkk(ctx, "autoR", False)

    # Add reaction role config
    @commands.command(aliases=["add_reaction"])
    @commands.guild_only()
    async def add_reaction_role(self, ctx, messageID, role: discord.Role, emoji):
        if (await self.config.blockCheck(ctx)) or not (await self.config.on_checkk(ctx, "add_autoR", True)):
            return

        if str(ctx.author.id) in self.config.valid_users or ctx.author.guild_permissions.manage_roles:
            try:
                msg = await ctx.fetch_message(messageID)
            except:
                await ctx.channel.send(embed=discord.Embed(description="Couldn't find that message", colour=discord.Color.red()))
                await self.config.on_checkk(ctx, "add_autoR", False)
                return

            id = self.config.getID(ctx)
            spcificSrvr = self.config.specifSRVR(id)
            autoRole = spcificSrvr["Reactions"]

            if int(len(autoRole) + 1) > 10:
                await ctx.channel.send(embed=discord.Embed(description="You've reached reaction role limit. To add reaction roles remove some", colour=discord.Color.red()))
                await self.config.on_checkk(ctx, "add_autoR", False)
                return

            try:
                autoRole = autoRole[messageID]

                if int(len(autoRole) + 1) > 8:
                    await ctx.channel.send(embed=discord.Embed(description="You've reached reaction role limit. To add reactoin roles remove some", colour=discord.Color.red()))
                    await self.config.on_checkk(ctx, "add_autoR", False)
                    return

                check_ = False
                for i in range(len(autoRole)):
                    atr = autoRole[i]
                    role1 = atr[0]
                    emoji1 = atr[1]

                    if role1 == str(role.id):
                        check_ = True
                    if emoji1 == emoji:
                        check_ = True

                if check_:
                    await ctx.channel.send(embed=discord.Embed(description="This role or emoji is already configured", colour=discord.Color.red()))
                    await self.config.on_checkk(ctx, "add_autoR", False)
                    return

                autoRole.append([str(role.id), emoji])
            except:
                autoRole[messageID] = [[str(role.id), emoji]]

            self.config.save()

            await msg.add_reaction(emoji)
            await ctx.channel.send(embed=discord.Embed(description=f"React {emoji} to get {role.mention} ", colour=discord.Color.dark_blue()), delete_after=10)
            await asyncio.create_task(self.config.prnt(ctx, f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Auto Role')} added new auto role"))
        else:
            await ctx.channel.send(embed=discord.Embed(title="ERROR", description="You dont have permition to do that", colour=discord.Color.red(), timestamp=datetime.utcnow()).set_footer(icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"))

        await self.config.on_checkk(ctx, "add_autoR", False)

    # Remove reaction role config
    @commands.command(aliases=["rm_reaction"])
    @commands.guild_only()
    async def remove_reaction_role(self, ctx, messageID, num=0):
        if (await self.config.blockCheck(ctx)) or not (await self.config.on_checkk(ctx, "rm_autoR", True)):
            return

        if str(ctx.author.id) in self.config.valid_users or ctx.author.guild_permissions.manage_roles:
            id = self.config.getID(ctx)
            spcificSrvr = self.config.specifSRVR(id)
            autoRole = spcificSrvr["Reactions"]

            try:
                msg = autoRole[messageID]
            except:
                await ctx.channel.send(embed=discord.Embed(description="Couldn't find that messsage in config file", colour=discord.Color.red()))
                await self.config.on_checkk(ctx, "rm_autoR", False)
                return

            if int(num) == -1:
                del autoRole[messageID]
            else:
                num -= 1
                length = len(autoRole[messageID])

                if int(num) > int(length):
                    await ctx.channel.send(embed=discord.Embed(description="Out of range", colour=discord.Color.red()))
                    await self.config.on_checkk(ctx, "rm_autoR", False)
                    return

                if int(length) == 1:
                    del autoRole[messageID]
                else:
                    del msg[num]

            self.config.save()
            await ctx.channel.send(embed=discord.Embed(description="Succcessfully remove reaction role config", colour=discord.Color.dark_blue()))
            await asyncio.create_task(self.config.prnt(ctx, f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Auto Role')} removed auto role"))

        else:
            await ctx.channel.send(embed=discord.Embed(title="ERROR", description="You dont have permition to do that", colour=discord.Color.red(), timestamp=datetime.utcnow()).set_footer(icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"))

        await self.config.on_checkk(ctx, "rm_autoR", False)

    # Check reaction role configuration
    @commands.command(aliases=["reaction_list"])
    @commands.guild_only()
    async def reaction_role_list(self, ctx, messageID="None"):
        if (await self.config.blockCheck(ctx)) or not (await self.config.on_checkk(ctx, "autoR_list", True)):
            return

        if str(ctx.author.id) in self.config.valid_users or ctx.author.guild_permissions.manage_roles:
            id = self.config.getID(ctx)
            spcificSrvr = self.config.specifSRVR(id)
            autoRole = spcificSrvr["Reactions"]

            if len(autoRole) < 1:
                await ctx.channel.send(embed=discord.Embed(description="You don't have any reaction role configured", colour=discord.Color.red()))
                await self.config.on_checkk(ctx, "autoR_list", False)
                return

            if str(messageID) == "None":
                arL = list(autoRole)
                autorls = ""

                for j in range(len(autoRole)):
                    autorls += f"**Message ID:** {arL[j]}\n"
                    msgID = str(arL[j])
                    atr = autoRole[msgID]

                    for i in range(len(atr)):
                        atr1 = atr[i]
                        role1 = atr1[0]
                        emoji1 = atr1[1]

                        autorls += f"`{i+1}` {emoji1} - {role1}\n"
                    autorls += "\n"

                embed = discord.Embed(title="Reaction Roles", description=autorls, colour=discord.Color.dark_blue())
            else:
                try:
                    autoRole = autoRole[messageID]
                except:
                    await ctx.channel.send(embed=discord.Embed(description="Couldn't find that message in config file", colour=discord.Color.red()))
                    await self.config.on_checkk(ctx, "autoR_list", False)
                    return

                autorls = f"**Message ID:** {messageID}\n\n"

                for i in range(len(autoRole)):
                    atr = autoRole[i]
                    role1 = atr[0]
                    emoji1 = atr[1]

                    autorls += f"`{i+1}` {emoji1} - {role1}\n"

                embed = discord.Embed(title=f"Reaction Roles", description=autorls, colour=discord.Color.dark_blue())

            await ctx.channel.send(embed=embed)
            await asyncio.create_task(self.config.prnt(ctx, f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Auto Role')} checked auto roles"))

        else:
            await ctx.channel.send(embed=discord.Embed(title="ERROR", description="You dont have permition to do that", colour=discord.Color.red(), timestamp=datetime.utcnow()).set_footer(icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"))

        await self.config.on_checkk(ctx, "autoR_list", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return
            
        self.config.on_check = []

# Setting up the cog
def setup(client, config):
    client.add_cog(Auto_Roles(client, config))
