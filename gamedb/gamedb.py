# other shit
from typing import List
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


class GameDB(commands.Cog):
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

    async def req(self, url, creds, data_obj: object):
        headers = {
            "User-Agent": "Discord-Bot for Pulling Information About Video Games",
            "From": "contact@is-a.win",
            "Client-ID": creds['client_id'],
            "Authorization": creds['client_secret']
        }
        reqtype = self.session.post
        async with reqtype(url, headers=headers, data=data_obj) as req:
            data = await req.text()
            status = req.status
        return data, status

    @commands.group()
    async def gamedb(self, ctx):
        """Group of commands for looking up video games."""

    @gamedb.command(name="api")
    async def gamedb_api(self, ctx):
        """Instructions for how to securely add set the api keys."""
        await ctx.send("Signup for Twitch's API then run the command ``set api twitch client_id,1234ksdjf client_secret,1234aldlfkd`` to set the keys. Make sure that you input your data.")
    
    @gamedb.command(name="search")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def gamedb_search(self, ctx, *, search_term):
        if await self.bot.get_shared_api_tokens("twitch") is None:
            await ctx.send('You need to set your api keys with ``[p]gamedb api``.')
        else:
            creds = await self.bot.get_shared_api_tokens("twitch")
            print(creds)
            response = await self.req(url='https://api.igdb.com/v4/search', creds=creds, data_obj={"name": search_term})
            print(response)