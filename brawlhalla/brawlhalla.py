# other shit
import aiohttp
import asyncio
import json
import re

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS


class Brawlhalla(commands.Cog):
    """
    Brawlhalla cog.
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

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def req(self, url, get_or_url):
        headers = {
            "User-Agent": "Brawlhalla Discord-Bot for Pulling Information About Players",
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