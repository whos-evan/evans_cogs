# other shit
import asyncio
import datetime
import argparse

import discord
from discord.ext import commands
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS


class YTUploader(commands.Cog):
    """
    YoutubeUploader cog.
    """

    __version__ = "0.0.1 beta"
    __author__ = "evan"

    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    async def cog_unload(self):
        await self.client.close()

    @commands.group()
    @commands.is_owner()
    async def yt(self, ctx):
        """Group for uploading videos to YouTube."""

    @yt.command(name="upload")
    @commands.is_owner()
    async def upload(self, ctx, *, args):
            if ctx.message.attachments:
                video  = await ctx.message.attachments[0].read()

                parser = argparse.ArgumentParser()
                parser.add_argument("--title")
                parser.add_argument("--description")
                parser.add_argument("--tags")
                parser.add_argument("--category")
                parser.add_argument("--privacy_status")

                args = parser.parse_args(args.split())
                await ctx.send(f'Title: {args.title} | Description: {args.description} | Tags: {args.tags} | Category: {args.category} | Privacy Status: {args.privacy_status}')