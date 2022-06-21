# other shit
from typing import List
import aiohttp
import json

import discord
from discord.ext import commands
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

from igdb.wrapper import IGDBWrapper


class GameDB(commands.Cog):
    """
    GameDB cog.
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

    @commands.group()
    async def gamedb(self, ctx):
        """Group of commands for looking up video games."""

    @gamedb.command(name="api")
    async def gamedb_api(self, ctx):
        """Instructions for how to securely add set the api keys."""
        await ctx.send("Signup for Twitch's API then run the command ``set api twitch client_id,1234ksdjf access_token,1234aldlfkd`` to set the keys. Make sure that you input your data.")

    @gamedb.command(name="search")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def gamedb_search(self, ctx, *, search_term):
        if await self.bot.get_shared_api_tokens("twitch") is None:
            await ctx.send('You need to set your api keys with ``[p]gamedb api``.')
        else:
            creds = await self.bot.get_shared_api_tokens("twitch")
            wrapper = IGDBWrapper(creds['client_id'], creds['access_token'])
            byte_array = wrapper.api_request(
            'games',
            f'fields name, summary, cover; offset 0; where name="{search_term}"*;',
            
          )
            print(byte_array)
            games = json.loads(byte_array)
            print(games)
            for game in games:
                name = game['name']
                summary = game['summary']
                url = game['url']
                await ctx.send(f'{url}\n{name} - {summary}')