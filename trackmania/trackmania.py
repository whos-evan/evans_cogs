# other shit
import aiohttp
import asyncio
import re
import datetime
from attr import has

import discord
from discord.ext import commands
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS


class Trackmania(commands.Cog):
    """
    Trackmania cog.
    """

    __version__ = "0.0.1 beta"
    __author__ = "evan"

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    async def cog_unload(self):
        await self.client.close()

    async def req(self, url, get_or_url):
        headers = {
            "User-Agent": "Trackmania Discord-Bot for Pulling Information About Maps",
            "From": "contact@is-a.win",  # This is another valid field
        }
        reqtype = self.session.get
        if get_or_url == "url":
            async with reqtype(url, headers=headers) as req:
                data = req.url
                status = req.status
        else:
            async with reqtype(url, headers=headers) as req:
                data = await req.text()
                status = req.status
        return data, status

    async def track_embed(self, map_info: str, number: int = 0, return_important: bool = False):
        try:
            track_id = re.findall('(?<="TrackID":).*(?=,"UserID":)', map_info)
            track_id = track_id[number]

            url = f"https://trackmania.exchange/maps/{track_id}"

            author_name = re.findall('(?<="Username":").*?(?=","GbxMapName")', map_info)
            author_time = re.findall('(?<="AuthorTime":).*?(?=,"ParserVersion")', map_info)

            author_time = int(author_time[number])
            author_time = author_time / 1000
            author_time = datetime.timedelta(seconds=author_time)
            author_time = str(author_time)
            author_time = author_time[:-3]

            name = re.findall('(?<="Name":").*?(?=","Tags")', map_info)
            length = re.findall('(?<="LengthName":").*?(?=","DifficultyName")', map_info)
            difficulty = re.findall('(?<="DifficultyName":").*?(?=","Laps")', map_info)
            award_count = re.findall('(?<="AwardCount":).*?(?=,"CommentCount")', map_info)
            track_photo = str("https://trackmania.exchange/tracks/screenshot/normal/" + track_id)
            track_desc = str("Map ID: " + track_id)

            track_uid = re.findall('(?<="TrackUID":").*(?=","Mood":)', map_info)

            track_io_request_url = (
                "https://trackmania.io/api/leaderboard/map/"
                + track_uid[number]
                + "?offset=0&length="
                + "1"
            )
            wr_info = await self.req(track_io_request_url, get_or_url="get")
            wr_info = wr_info[0]

            record_names = []
            record_times = []

            async def findrecord(record_num):
                name = re.findall('(?<={"player":{"name":").*?(?=","tag"|","id":")', wr_info)
                try:
                    name = name[record_num]
                    record_names.append(name)
                except:
                    name = "No Record"
                    record_names.append(name)

                time = re.findall('(?<="time":).*?(?=,"filename")', wr_info)
                try:
                    time = int(time[record_num])
                    time = time / 1000
                    time = datetime.timedelta(seconds=time)
                    time = str(time)
                    time = time[:-3]
                    record_times.append(time)
                except:
                    time = "No Record"
                    record_times.append(time)

            await findrecord(0)
            wr_time = (
                "``"
                + record_names[0]
                + "`` set a time of ``"
                + str(record_times[0])
                + "``"
            )

            embed = discord.Embed(title=name[number], url=url, description=track_desc)
            embed.add_field(name="Author's Username", value=author_name[number], inline=True)
            embed.add_field(name="Author's Time", value=author_time, inline=True)
            embed.add_field(name="WR Time", value=wr_time, inline=True)
            embed.add_field(name="Track Length", value=length[number], inline=True)
            embed.add_field(name="Track's Difficulty", value=difficulty[0], inline=True)
            embed.add_field(name="Awards", value=award_count[number], inline=True)
            embed.set_image(url=track_photo)
            if return_important is False:
                return embed
            else:
                return embed, name[0], author_name[0], author_time
        except Exception as e:
            print(f"Error: {e}")
            return None


    @commands.group()
    async def trackmania(self, ctx):
        """Group for Trackmania track info."""

    @trackmania.command(name="search")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def tracksearch(self, ctx, *, search: str):
        """Search for a track on Trackmania.exchange."""
        await ctx.trigger_typing()
        full_search = await self.req("https://trackmania.exchange/tracksearch2/search?api=on&format=json&trackname=" + search, get_or_url="get")
        full_search = full_search[0]
        try:
            track_ids = re.findall('(?<={"TrackID":).*?(?=,"UserID")', full_search)
            embeds = []
            options = []
            for i in range(len(track_ids)):
                result = await self.track_embed(map_info=full_search, number=i, return_important=True)

                embed = result[0]
                name = str(len(embeds)) + ' - ' + result[1]
                name2 = result[1]
                author_name = result[2]
                author_time = result[3]

                description = name2 + " by: " + author_name + " - " + author_time

                option = discord.SelectOption(label=name, description=description)
                options.append(option)

                embeds.append(embed)

            class Dropdown(discord.ui.Select):
                def __init__(self):
                    super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
                async def callback(self, interaction: discord.Interaction):
                    num = self.values[0].split(' - ')[0]
                    await interaction.response.send_message(content=None, embed=embeds[int(num)], ephemeral=True)
                    

            class SelectView(discord.ui.View):
                def __init__(self, *, timeout = 180):
                    super().__init__(timeout=timeout)
                    self.add_item(Dropdown())

            await ctx.send('Choose the track you wish to view: ', view=SelectView())
        except:
            await ctx.send(content="No results found.")

    @trackmania.command(name="info")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def trackinfo(self, ctx, track):
        """Grab a Trackmania.Exchange's track information."""

        await ctx.trigger_typing()
        try:
            async def if_integer(string):
                try:
                    int(string)
                    return True
                except ValueError:
                    return False

            if await if_integer(track) is True:
                track_id = str(track)
            elif "https://trackmania.exchange/maps/" in track:
                track_id = track.partition("/maps/")[2]
            else:
                track_id = "-1"

            track_exc_request_url = (
                "https://trackmania.exchange/api/maps/get_map_info/multi/" + track_id
            )

            map_info = await self.req(track_exc_request_url, get_or_url="get")
            map_info = map_info[0]

            embed = await self.track_embed(map_info)
            await ctx.send(embed=embed)
        except:
            await ctx.send("No results found.")

    @trackmania.command(name="records")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def worldrecords(self, ctx, track, num: int):
        """Grab a Trackmania.Exchange/Trackmania.Io WR information."""

        async def if_integer(string):
            try:
                int(string)
                return True
            except ValueError:
                return False

        if await if_integer(track) is True:
            track_id = str(track)
        elif "https://trackmania.exchange/maps/" in track:
            track_id = track.partition("/maps/")[2]
        else:
            track_id = "-1"

        if num > 23:
            num = 23
        elif num < 0:
            num = 5 # this is so that people don't put a stupid number that the bot can't parse

        url = "https://trackmania.exchange/maps/" + track_id

        track_exc_request_url = (
            "https://trackmania.exchange/api/maps/get_map_info/multi/" + track_id
        )

        map_info = await self.req(track_exc_request_url, get_or_url="get")
        map_info = map_info[0]

        if map_info == "[]":
            await ctx.send(
                "You did something wrong or the bot did something wrong. It's very likely that it is your fault however."
            )
        else:
            await ctx.trigger_typing()
            author_name = re.findall('(?<="Username":").*(?=","GbxMapName")', map_info)
            author_time = re.findall('(?<="AuthorTime":).*(?=,"ParserVersion")', map_info)

            track_photo = str("https://trackmania.exchange/tracks/screenshot/normal/" + track_id)

            author_time = int(author_time[0])
            author_time = author_time / 1000
            author_time = str(author_time)

            name = re.findall('(?<="Name":").*(?=","Tags")', map_info)

            track_uid = re.findall('(?<="TrackUID":").*(?=","Mood":)', map_info)

            track_io_request_url = (
                "https://trackmania.io/api/leaderboard/map/"
                + track_uid[0]
                + "?offset=0&length="
                + str(num)
            )
            wr_info = await self.req(track_io_request_url, get_or_url="get")
            wr_info = wr_info[0]

            record_names = []
            record_times = []

            async def findrecord(record_num):
                name = re.findall(
                    '(?<={"player":{"name":").*?(?=","tag"|","id":")', wr_info
                )
                try:
                    name = name[record_num]
                    record_names.append(name)
                except:
                    name = "No Record"
                    record_names.append(name)

                time = re.findall('(?<="time":).*?(?=,"filename")', wr_info)
                try:
                    time = int(time[record_num])
                    time = time / 1000
                    record_times.append(time)
                except:
                    time = "No Record"
                    record_times.append(time)

            embed = discord.Embed(title=name[0], url=url)
            embed.add_field(name="Author's Username", value=author_name[0], inline=True)
            embed.add_field(name="Author's Time", value=author_time, inline=True)

            for x in range(0, num):
                await findrecord(x)
                wr_time = (
                    "``"
                    + record_names[x]
                    + "`` set a time of ``"
                    + str(record_times[x])
                    + "``"
                )
                y = x + 1
                if y == 1:
                    extra = "🥇"
                elif y == 2:
                    extra = "🥈"
                elif y == 3:
                    extra = "🥉"
                else:
                    extra = ""
                ordinial = lambda y: "%d%s" % (
                    y,
                    "tsnrhtdd"[(y // 10 % 10 != 1) * (y % 10 < 4) * y % 10 :: 4],
                )
                place = ordinial(y) + " Place" + extra
                embed.add_field(name=place, value=wr_time, inline=True)

            embed.set_image(url=track_photo)

            await ctx.send(embed=embed)

    @trackmania.command(name="randomtrack")
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def randomtrack(self, ctx, number: int):
        """Grab random Trackmania.Exchange's tracks."""
        if number > 25:
            await ctx.send("Don't crash the bot please.")
        elif number < 1:
            await ctx.send("https://www.youtube.com/watch?v=xxhNCY21-xs")
        else:
            await ctx.trigger_typing()
            embeds = []
            options = []

            track_ids = []

            for i in range(number):
                random_url = await self.req(
                    "https://trackmania.exchange/mapsearch2/search?random=1",
                    get_or_url="url",
                )
                random_url = str(random_url[0])

                track_id = random_url.partition("/maps/")[2]
                track_ids.append(track_id)
            
            track_ids = ",".join(track_ids)

            full_search = await self.req('https://trackmania.exchange/api/maps/get_map_info/multi/' + track_ids, get_or_url="get")

            for i in range(number):
                result = await self.track_embed(map_info=full_search, number=i, return_important=True)

                embed = result[0]
                name = str(len(embeds)) + ' - ' + result[1]
                name2 = result[1]
                author_name = result[2]
                author_time = result[3]

                description = name2 + " by: " + author_name + " - " + author_time

                option = discord.SelectOption(label=name, description=description)
                options.append(option)

                embeds.append(embed)

            class Dropdown(discord.ui.Select):
                def __init__(self):
                    super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
                async def callback(self, interaction: discord.Interaction):
                    num = self.values[0].split(' - ')[0]
                    await interaction.response.send_message(content=None, embed=embeds[int(num)], ephemeral=True)
                    

            class SelectView(discord.ui.View):
                def __init__(self, *, timeout = 180):
                    super().__init__(timeout=timeout)
                    self.add_item(Dropdown())

            await ctx.send('Choose the track you wish to view: ', view=SelectView())

    @trackmania.command(name="totd")
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def totd(self, ctx):
        """Grab Trackmania's current TOTD."""
        await ctx.trigger_typing()

        totd_info = await self.req('https://trackmania.io/api/totd/0', get_or_url='get')
        totd_info = totd_info[0]

        name = re.findall('(?<=,"name":").*?(?=","mapType":)', totd_info)
        thumbnail = re.findall('(?<=,"thumbnailUrl":").*?(?=","authorplayer":)', totd_info)
        author_name = re.findall('(?<=,"authorplayer":{"name":").*?(?=","tag":"|","id":)', totd_info)

        author_time = re.findall('(?<="authorScore":).*?(?=,"goldScore":)', totd_info)
        author_time = int(author_time[-1])
        author_time = author_time / 1000
        author_time = datetime.timedelta(seconds=author_time)
        author_time = str(author_time)
        author_time = author_time[:-3]

        embed = discord.Embed(title=name[-1], url="https://trackmania.io/totd", description="Trackmania's Track Of The Day")
        embed.add_field(name="Author's Username", value=author_name[-1], inline=True)
        embed.add_field(name="Author's Time", value=author_time, inline=True)
        embed.set_image(url=thumbnail[-1])

        await ctx.send(embed=embed)

