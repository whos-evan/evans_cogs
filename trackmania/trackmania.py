from typing import Literal

# other shit
import aiohttp
import json
import re

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

class Trackmania(commands.Cog):
    """
    Trackmania cog.
    """

    __version__ = "0.0.1 beta"
    __author__ = "evan"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())


    async def req(self, url, get_or_url):
        headers = {
            'User-Agent': 'Trackmania Discord-Bot for Pulling Information About Maps',
            'From': 'contact@is-a.win'  # This is another valid field
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
    
    @commands.group()
    async def trackmania(self, ctx):
        """Group for Trackmania track info."""


    @trackmania.command(name="trackinfo")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def trackinfo(self, ctx, track):
        """Grab a Trackmania.Exchange's track information."""

        message = await ctx.send('This may take a second.')

        async def if_integer(string):
            try: 
                int(string)
                return True
            except ValueError:
                return False

        if await if_integer(track) is True:
            track_id = str(track)
        elif 'https://trackmania.exchange/maps/' in track:
            track_id = track.partition('/maps/')[2]
        else:
            track_id = '-1'
        
        url = 'https://trackmania.exchange/maps/' + track_id
        
        track_exc_request_url = 'https://trackmania.exchange/api/maps/get_map_info/multi/' + track_id
        
        map_info = await self.req(track_exc_request_url, get_or_url="get")
        map_info = map_info[0]

        if map_info == '[]':
            await message.delete()
            await ctx.send("Bruv the thing that you put in the thingy doesn't have a track.")
        else:
            author_name = re.findall('(?<="Username":").*(?=","GbxMapName")', map_info)
            author_time = re.findall('(?<="AuthorTime":).*(?=,"ParserVersion")', map_info)

            author_time = int(author_time[0])
            author_time = author_time / 1000
            author_time = str(author_time)

            name = re.findall('(?<="Name":").*(?=","Tags")', map_info)
            length = re.findall('(?<="LengthName":").*(?=","DifficultyName")', map_info)
            difficulty = re.findall('(?<="DifficultyName":").*(?=","Laps")', map_info)
            rating = re.findall('(?<="RatingVoteAverage":).*(?=,"HasScreenshot")', map_info)
            track_photo = str('https://trackmania.exchange/tracks/screenshot/normal/' + track_id)
            track_desc = str("Rating: " + rating[0])

            track_uid = re.findall('(?<="TrackUID":").*(?=","Mood":)', map_info)

            track_io_request_url = 'https://trackmania.io/api/leaderboard/map/' + track_uid[0] + '?offset=0&length=' + '1'
            wr_info = await self.req(track_io_request_url, get_or_url="get")
            wr_info = wr_info[0]

            record_names = []
            record_times = []

            async def findrecord(record_num):
                name = re.findall('(?<={"player":{"name":").*?(?=","tag"|","id":")', wr_info)
                name = name[record_num]
                record_names.append(name)

                time = re.findall('(?<="time":).*?(?=,"filename")', wr_info)
                time = int(time[record_num])
                time = time / 1000
                record_times.append(time)

            await findrecord(0)
            wr_time = '``' + record_names[0] + '`` set a time of ``' + str(record_times[0]) + '``'

            embed=discord.Embed(title=name[0], url=url, description=track_desc)
            embed.add_field(name="Author's Username", value=author_name[0], inline=True)
            embed.add_field(name="Author's Time", value=author_time, inline=True)
            embed.add_field(name="WR Time", value=wr_time, inline=True)
            embed.add_field(name="Track Length", value=length[0], inline=True)
            embed.add_field(name="Track's Difficulty", value=difficulty[0], inline=True)
            embed.add_field(name="Track's Rating", value=rating[0], inline=True)
            embed.set_thumbnail(url=track_photo)

            await message.delete()
            await ctx.send(embed=embed)
