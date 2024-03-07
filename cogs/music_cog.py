# Importing Modules
import discord
import yt_dlp
import asyncio
import re
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands.errors import CommandNotFound
from discord import FFmpegPCMAudio
from ext.config import get_prefix

# TODO: add spotify player and youtube live


# Music Class
class Music(commands.Cog):
    def __init__(self, client, config):
        self.client = client
        self.config = config  # Config(client)

        self.regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

        self.xyz1 = 0
        self.queue_ = {}
        self.listening = []

        self.loopList = {}
        self.loop_songs = {}

        self.YDL_OPTIONS = {
            "format": "bestaudio/best",
            "extractaudio": True,
            "cachedir": False,
            "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "noplaylist": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "print": False,
            ""
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredquality": "192",
                }
            ],
            "keepvideo": False,
            "source_address": "0.0.0.0",
        }

        self.FFMPEG_OPTIONS = {
            "options": "-vn -nostats -loglevel 0",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        }

        self.ydl = yt_dlp.YoutubeDL(self.YDL_OPTIONS)

    # Create player object
    async def search(self, queue1, num):
        queue2 = queue1[num]

        URL = queue2[0]
        title = queue2[1]
        url = queue2[2]
        author = queue2[3]
        duration = queue2[4]

        stuff = ["Empty", URL, title, url, author, duration]
        return stuff

    # Create play message
    async def playMsg(self, ctx, tag, title, url, author, duration):
        ending = url.replace("https://www.youtube.com/watch?v=", "")
        img = f"https://img.youtube.com/vi/{ending}/0.jpg"

        url = f"[{title}]({url}) | `{duration}`"

        pfp = author.avatar_url

        id = self.config.getID(ctx)
        try:
            loopState = self.loopList[str(id)]
        except:
            loopState = False

        embed = discord.Embed(
            title=f"**{tag}**,  Loop={loopState}",
            description=url,
            colour=discord.Color.dark_blue(),
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=img)
        embed.set_footer(icon_url=pfp, text=f"Added by {author}")

        return embed

    # Play next song
    async def play_next(self, ctx):
        id = self.config.getID(ctx)
        queue1 = self.queue_[str(id)]
        voice = get(self.client.voice_clients, guild=ctx.guild)

        if voice != None and not voice.is_playing() and len(queue1) > 0:
            voice.stop()
            try:
                loopState = self.loopList[str(id)]
            except:
                loopState = False

            if loopState or len(queue1) > 1:
                if loopState:
                    var1 = await self.search(queue1, 0)
                else:
                    var1 = await self.search(queue1, 1)
                    del queue1[0]

                voice.play(
                    FFmpegPCMAudio(var1[1], **self.FFMPEG_OPTIONS),
                    after=lambda e: (
                        asyncio.run_coroutine_threadsafe(
                            self.play_next(ctx), self.client.loop
                        )
                    ),
                )

                try:
                    self.loop_songs[str(id)]
                except:
                    self.loop_songs[str(id)] = ""

                if not loopState or var1[1] != self.loop_songs[str(id)]:
                    tag = "Now Playing"
                    playMsg1 = await self.playMsg(
                        ctx, tag, var1[2], var1[3], var1[4], var1[5]
                    )
                    await ctx.channel.send(embed=playMsg1)

                self.loop_songs[str(id)] = var1[1]

            elif len(queue1) == 1:
                del queue1[0]

    # Check if dj role is requaried
    async def dj_check(self, ctx):
        id = self.config.getID(ctx)
        dj_ = self.config.specifSRVR(str(id))

        if dj_["DJ"] == "True":
            usr_roles = ctx.author.roles
            for i in range(len(usr_roles)):
                c_role = usr_roles[i]
                role_name = c_role.name
                if str(role_name.lower()) == "dj":
                    return True
            return False
        return True

    # Join voice channel
    @commands.command(aliases=["j"])
    @commands.guild_only()
    async def join(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "join", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "join", False)
                return
            else:
                voice = get(self.client.voice_clients, guild=ctx.guild)

            voice = ctx.message.guild.voice_client
            channel = ctx.author.voice.channel

            if voice or (voice and voice.is_connected()):
                await voice.move_to(channel)
            else:
                voice = await channel.connect()
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

        await self.config.on_checkk(ctx, "join", False)

    # Leave voice channel
    @commands.command(aliases=["l", "quit"])
    @commands.guild_only()
    async def leave(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "leave", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "leave", False)
                return

            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "leave", False)
                return

            await voice_client.disconnect()
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

        await self.config.on_checkk(ctx, "leave", False)

    # Start player or add something to queue
    @commands.command(aliases=["p"])
    @commands.guild_only()
    async def play(self, ctx, *, url):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "play", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            id = self.config.getID(ctx)
            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "play", False)
                return
            else:
                voice = get(self.client.voice_clients, guild=ctx.guild)

            voice1 = ctx.message.guild.voice_client
            channel1 = ctx.author.voice.channel

            if voice1 or (voice1 and voice1.is_connected()):
                if channel1 != voice1.channel:
                    await voice1.move_to(channel1)
            else:
                voice = await channel1.connect()

            if not voice.is_playing():
                try:
                    self.queue_[str(id)]
                except:
                    self.queue_[str(id)] = []

            if int(len(self.queue_[str(id)]) + 1) <= 18:
                try:
                    url1 = url.strip()
                    url_check = re.match(self.regex, url1)
                except:
                    url_check = False

                duration = None

                if url_check and "open.spotify" in url:
                    url_test = requests.get(url)
                    soup = BeautifulSoup(url_test.content, "html.parser")

                    url = soup.title.get_text()
                    url = url.replace(" song by", "").replace(" | Spotify", "")

                    url_check = False

                if url_check:
                    try:
                        youtube = self.ydl.extract_info(url, download=False)
                    except Exception as e:
                        if "unsupported url" in str(e).lower():
                            await ctx.channel.send(
                                embed=discord.Embed(
                                    description=f"Unsupported URL {ctx.author.mention}",
                                    colour=discord.Color.red(),
                                )
                            )
                        else:
                            await ctx.channel.send(
                                embed=discord.Embed(
                                    description=f"Message: `{e}`\n\n [Contact support for help - use `{get_prefix(self.client, ctx)}support`]",
                                    colour=discord.Color.red(),
                                )
                            )
                        await self.config.on_checkk(ctx, "play", False)
                        return

                    URL = ""
                    if len(youtube["formats"]) == 0:
                        await ctx.channel.send(
                            embed=discord.Embed(
                                description=f"Couldn't find any link to play, sorry",
                                colour=discord.Color.red(),
                            )
                        )
                        await self.config.on_checkk(ctx, "play", False)
                        return

                    for format in youtube["formats"]:
                        if "asr" in format:
                            URL = format["url"]
                            break

                    if URL == "":
                        await ctx.channel.send(
                            embed=discord.Embed(
                                description=f"Couldn't find any link to play {ctx.author.mention}",
                                colour=discord.Color.red(),
                            )
                        )

                        await self.config.on_checkk(ctx, "play", False)
                        return

                    title = youtube["title"]
                    url = f'https://www.youtube.com/watch?v={youtube["id"]}'

                    try:
                        duration = youtube["duration_string"]
                        if ":" not in duration:
                            duration = f"0:{duration}"
                    except:
                        duration = "None"
                else:
                    try:
                        youtube = self.ydl.extract_info(
                            f"ytsearch:{url}", download=False
                        )
                    except Exception as e:
                        if "unsupported url" in str(e).lower():
                            await ctx.channel.send(
                                embed=discord.Embed(
                                    description=f"Unsupported URL {ctx.author.mention}",
                                    colour=discord.Color.red(),
                                )
                            )
                        else:
                            await ctx.channel.send(
                                embed=discord.Embed(
                                    description=f"Message: `{e}`\n\n [Contact support for help - use `{get_prefix(self.client, ctx)}support`]",
                                    colour=discord.Color.red(),
                                )
                            )
                        await self.config.on_checkk(ctx, "play", False)
                        return

                    URL = ""
                    if len(youtube["entries"]) == 0:
                        await ctx.channel.send(
                            embed=discord.Embed(
                                description=f"Couldn't find any link to play, sorry",
                                colour=discord.Color.red(),
                            )
                        )
                        await self.config.on_checkk(ctx, "play", False)
                        return

                    for format in youtube["entries"][0]["formats"]:
                        if "asr" in format:
                            URL = format["url"]
                            break

                    if URL == "":
                        await ctx.channel.send(
                            embed=discord.Embed(
                                description=f"Couldn't find any link to play {ctx.author.mention}",
                                colour=discord.Color.red(),
                            )
                        )

                        await self.config.on_checkk(ctx, "play", False)
                        return

                    title = youtube["entries"][0]["title"]

                    url = youtube["entries"][0]["id"]
                    url = f"https://www.youtube.com/watch?v={url}"

                    try:
                        duration = youtube["entries"][0]["duration_string"]
                        if ":" not in duration:
                            duration = f"0:{duration}"
                    except:
                        duration = "None"

                youtube = [str(URL), str(title), str(url), ctx.message.author, duration]

                try:
                    self.queue_[str(id)].append(youtube)
                except:
                    self.queue_[str(id)] = [youtube]

                if not voice.is_playing() and int(len(self.queue_[str(id)])) == 1:
                    voice.play(
                        FFmpegPCMAudio(URL, **self.FFMPEG_OPTIONS),
                        after=lambda e: (
                            asyncio.run_coroutine_threadsafe(
                                self.play_next(ctx), self.client.loop
                            )
                        ),
                    )

                    tag = "Now Playing"
                    playMsg1 = await self.playMsg(
                        ctx, tag, title, url, ctx.message.author, duration
                    )
                    await ctx.channel.send(embed=playMsg1)
                else:
                    tag = "Added To Queue"
                    playMsg1 = await self.playMsg(
                        ctx, tag, title, url, ctx.message.author, duration
                    )
                    await ctx.channel.send(embed=playMsg1)
            else:
                await ctx.channel.send(
                    "```You've reached queue limit. To add new songs make your queue smaller```"
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

        await self.config.on_checkk(ctx, "play", False)

    # Change loop state
    @commands.command(aliases=["lp"])
    @commands.guild_only()
    async def loop(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "loop", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "loop", False)
                return

            id = self.config.getID(ctx)
            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "loop", False)
                return

            try:
                loopState = self.loopList[str(id)]

                if loopState == True:
                    self.loopList[str(id)] = False
                else:
                    self.loopList[str(id)] = True
            except:
                self.loopList[str(id)] = True

            loopState = self.loopList[str(id)]

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"Music loop state: `{loopState}`",
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
                    icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "loop", False)

    # Pasue player
    @commands.command(aliases=["ps"])
    @commands.guild_only()
    async def pause(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "pause", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "pause", False)
                return

            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "pause", False)
                return

            server = ctx.message.guild
            voice_channel = server.voice_client

            voice_channel.pause()

            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"⏸ **Player paused.** Type `{get_prefix(self.client, ctx)}resume` to resume",
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
                    icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "pause", False)

    # Resume player
    @commands.command(aliases=["rs"])
    @commands.guild_only()
    async def resume(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "resume", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "resume", False)
                return

            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "resume", False)
                return

            server = ctx.message.guild
            voice_channel = server.voice_client

            voice_channel.resume()
            await ctx.channel.send(
                embed=discord.Embed(
                    description=f"⏯ **Resuming player**",
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
                    icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "resume", False)

    # Stop player
    @commands.command(aliases=["st"])
    @commands.guild_only()
    async def stop(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "stop", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "stop", False)
                return

            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "stop", False)
                return

            server = ctx.message.guild
            voice_channel = server.voice_client

            voice_channel.stop()

            voice_client = ctx.message.guild.voice_client
            await voice_client.disconnect()
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

        await self.config.on_checkk(ctx, "stop", False)

    # Check queue
    @commands.command(aliases=["qu"])
    @commands.guild_only()
    async def queue(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "queue", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "queue", False)
                return

            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "queue", False)
                return

            id = self.config.getID(ctx)

            try:
                loopState = self.loopList[str(id)]
            except:
                loopState = False

            try:
                queue1 = self.queue_[str(id)]
            except:
                self.queue_[str(id)] = []
                queue1 = self.queue_[str(id)]

            if len(queue1) > 1:
                var1 = await self.search(queue1, 0)
                url = f"[{var1[2]}]({var1[3]})"

                queued = f"**Now Playing**\n{url} | `{var1[5]}`\n\n"

                for i in range(len(queue1)):
                    if i != 0:
                        var2 = await self.search(queue1, i)

                        url = f"[{var2[2]}]({var2[3]})"
                        queued += f"`{i}` {url} | `{var2[5]}`\n"
                embed = discord.Embed(
                    title=f"**Music Queue ({len(queue1) - 1} tracks)**,  Loop={str(loopState)}",
                    description=queued,
                    colour=discord.Color.dark_blue(),
                )
            elif len(queue1) == 1:
                var1 = await self.search(queue1, 0)
                title = var1[2]
                url = var1[3]
                author = var1[4]
                duration = var1[5]

                tag = "Now Playing"
                embed = await self.playMsg(ctx, tag, title, url, author, duration)
            else:
                embed = discord.Embed(
                    title=f"**Music Queue (0 tracks)**,  Loop={str(loopState)}",
                    description="`There's no song in the queue`",
                    colour=discord.Color.dark_blue(),
                )
                embed.set_footer(
                    text=f"Type {get_prefix(self.client, ctx)}play <song> to add one"
                )

            await ctx.channel.send(embed=embed)
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

        await self.config.on_checkk(ctx, "queue", False)

    # Skip to the next song
    @commands.command(aliases=["sk", "s"])
    @commands.guild_only()
    async def skip(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "skip", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "skip", False)
                return

            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "skip", False)
                return
            else:
                voice = get(self.client.voice_clients, guild=ctx.guild)

            voice.stop()

            id = self.config.getID(ctx)
            try:
                queue1 = self.queue_[str(id)]
            except:
                self.queue_[str(id)] = []
                queue1 = self.queue_[str(id)]

            try:
                loopState = self.loopList[str(id)]
            except:
                loopState = False

            if loopState:
                del queue1[0]

            await asyncio.sleep(1)

            if len(queue1) != 0:
                await self.play_next(ctx)
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description="No more songs in your queue",
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
                    icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "skip", False)

    # Remove song from queue
    @commands.command(aliases=["rms"])
    @commands.guild_only()
    async def removeSong(self, ctx, num: int):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "removeSong", True)
        ):
            return

        dj_check1 = await self.dj_check(ctx)
        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
            or dj_check1
        ):
            voice_client = ctx.message.guild.voice_client
            if voice_client == None:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"I'm not connected to the voice channel",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "removeSong", False)
                return

            if not ctx.message.author.voice:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f":x: You must be in the voice channel to use this command.",
                        colour=discord.Color.red(),
                    )
                )
                await self.config.on_checkk(ctx, "removeSong", False)
                return

            id = self.config.getID(ctx)

            try:
                queue1 = self.queue_[str(id)]
            except:
                self.queue_[str(id)] = []
                queue1 = self.queue_[str(id)]

            if len(queue1) > 1:
                del queue1[num]

                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Successfully removed queue {num}",
                        colour=discord.Color.dark_blue(),
                    )
                )
            else:
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"Your queue is empty",
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
                    icon_url=ctx.author.avatar_url, text=f"Created by {ctx.author}"
                )
            )

        await self.config.on_checkk(ctx, "removeSong", False)

    # Change dj only mode
    @commands.command()
    @commands.guild_only()
    async def dj(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "dj", True)
        ):
            return

        if (
            str(ctx.author.id) in self.config.valid_users
            or ctx.author.guild_permissions.administrator
        ):
            id = self.config.getID(ctx)
            dj_ = self.config.specifSRVR(str(id))
            if dj_["DJ"] == "True":
                dj_["DJ"] = "False"
                self.config.save()
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"DJ only is disabled",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Audio')} disabled DJ only",
                    )
                )
            else:
                dj_["DJ"] = "True"
                self.config.save()
                await ctx.channel.send(
                    embed=discord.Embed(
                        description=f"DJ only is enabled",
                        colour=discord.Color.dark_blue(),
                    )
                )
                await asyncio.create_task(
                    self.config.prnt(
                        ctx,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(ctx, 'Audio')} enabled DJ only",
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

        await self.config.on_checkk(ctx, "dj", False)

    # Auto channels leave
    @tasks.loop(minutes=5)
    async def checkLeave(self):
        vc = self.client.voice_clients

        for i in range(len(vc)):
            vc1 = vc[i]
            chnlID = vc1.channel.id
            VC = get(vc1.guild.channels, id=chnlID)

            voice = get(vc, guild=vc1.guild)
            id = vc1.guild.id

            try:
                queue1 = self.queue_[str(id)]
            except:
                queue1 = []

            if len(VC.members) == 1:
                await vc1.disconnect()
            elif not voice.is_playing() and len(queue1) == 0:
                await vc1.disconnect()

    # Getting vc changes
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if str(member) in str(self.client.user):
            if not before.channel:
                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(member, 'Voice')} joined {after.channel.id}",
                        False,
                    )
                )
                try:
                    await member.edit(deafen=True)
                except:
                    pass

                self.listening.append(
                    f"{member.guild.name} | {after.channel.name}   [{member.guild.id} | {after.channel.id}]"
                )

                if self.xyz1 == 0:
                    self.checkLeave.start()
                    self.xyz1 = 1
            if before.channel and not after.channel:
                id = member.guild.id
                self.queue_[str(id)] = []
                self.loopList[str(id)] = False
                os.system("yt-dlp --rm-cache-dir > /dev/null 2>&1")

                try:
                    num = self.listening.index(
                        f"{member.guild.name} | {before.channel.name}   [{member.guild.id} | {before.channel.id}]"
                    )
                    del self.listening[num]
                except:
                    pass

                await asyncio.create_task(
                    self.config.prnt(
                        None,
                        f"[{(await self.config.get_time())}] {self.config.getNAME(member, 'Voice')} left {before.channel.id}",
                        False,
                    )
                )
            if before.channel and after.channel:
                if before.channel.id != after.channel.id:
                    try:
                        num = self.listening.index(
                            f"{member.guild.name} | {before.channel.name}   [{member.guild.id} | {before.channel.id}]"
                        )
                        del self.listening[num]
                    except:
                        pass

                    self.listening.append(
                        f"{member.guild.name} | {after.channel.name}   [{member.guild.id} | {after.channel.id}]"
                    )

                    await asyncio.create_task(
                        self.config.prnt(
                            None,
                            f"[{(await self.config.get_time())}] {self.config.getNAME(member, 'Voice')} switched from {before.channel.id} to {after.channel.id}",
                            False,
                        )
                    )

    # Check if someone is using bot on voice channel
    @commands.command(aliases=["srv_listening", "srv_listen"])
    async def server_listening(self, ctx):
        if (await self.config.blockCheck(ctx)) or not (
            await self.config.on_checkk(ctx, "srv_music", True)
        ):
            return

        if str(ctx.author.id) in self.config.valid_users:
            are_listening = "```"
            if len(self.listening) == 0:
                are_listening += "No one is using bot"
            else:
                for item in self.listening:
                    id = str(item.split()[4]).replace("[", "")
                    try:
                        queue1 = self.queue_[str(id)]
                    except:
                        self.queue_[str(id)] = []
                        queue1 = self.queue_[str(id)]

                    are_listening += f"{item} | Queue: {len(queue1)}\n\n"
            are_listening += "```"

            await ctx.channel.send(
                embed=discord.Embed(
                    title="Servers that are listening",
                    description=are_listening,
                    colour=discord.Color.dark_blue(),
                )
            )
        else:
            raise CommandNotFound

        await self.config.on_checkk(ctx, "srv_music", False)

    # Errors
    @commands.Cog.listener()
    async def on_command_error(self, msg, error):
        if await self.config.blockCheck(msg):
            return

        self.config.on_check = []


# Setting up the cog
def setup(client, config):
    client.add_cog(Music(client, config))
