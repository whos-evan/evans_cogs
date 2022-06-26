# other shit
import aiohttp
import asyncio
import re
import datetime

import discord
from discord.ext import commands
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS


class Fortnite(commands.Cog):
    """
    Fortnite cog.
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

    async def req(self, url, auth):
        headers = {
            "User-Agent": "Fortnite Discord-Bot for Pulling Information About Maps",
            "From": "contact@is-a.win",
            "TRN-Api-Key": auth
        }
        reqtype = self.session.get
        async with reqtype(url, headers=headers) as req:
            data = await req.text()
            status = req.status
        return data, status


    @commands.group()
    async def fortnite(self, ctx):
        """Group for Fortnite track info."""

    @fortnite.command(name="user")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def fortnite_user(self, ctx, *, user):
        """
        Get the stats of a user.
        """
        if await self.bot.get_shared_api_tokens("trackergg") is None:
            await ctx.send('You need to set your api keys with ``[p]set api trackergg [api_key]``.')
        else:
            creds = await self.bot.get_shared_api_tokens("fortnite")
            url = f"https://api.fortnitetracker.com/v1/profile/{creds['platform']}/{user}"
            data, status = await self.req(url, "url")
            if status == 200:
                data = json.loads(data)
                embed = discord.Embed(title=f"{data['epicUserHandle']}", color=0x00ff00)
                embed.set_thumbnail(url=data['avatar'])
                embed.add_field(name="Level", value=data['level'], inline=True)
                embed.add_field(name="Kills", value=data['lifeTimeStats'][0]['value'], inline=True)
                embed.add_field(name="K/D", value=data['lifeTimeStats'][1]['value'], inline=True)
                embed.add_field(name="Wins", value=data['lifeTimeStats'][2]['value'], inline=True)
                embed.add_field(name="Losses", value=data['lifeTimeStats'][3]['value'], inline=True)
                embed.add_field(name="Win %", value=data['lifeTimeStats'][4]['value'], inline=True)
                embed.add_field(name="Matches Played", value=data['lifeTimeStats'][5]['value'], inline=True)
                embed.add_field(name="Kills/Match", value=data['lifeTimeStats'][6]['value'], inline=True)
                embed.add_field(name="K/D/Match", value=data['lifeTimeStats'][7]['value'], inline=True)
                await ctx.send(embed=embed)
