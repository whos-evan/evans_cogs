# other shit
import asyncio
import datetime
import argparse
from logging import exception

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
    async def upload(self, ctx):
            if ctx.message.attachments:
                video  = await ctx.message.attachments[0].read()

                def check(m: discord.Message):  # m = discord.Message.
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

                try:
                    await ctx.send('Please type the title of the video.')
                    title_message = await self.client.wait_for(event = 'message', check = check, timeout = 60.0)
                    title = title_message.content
                except asyncio.TimeoutError:
                    await ctx.send('Timed out.')
                else:
                    try:
                        await ctx.send('Please type the description of the video.')
                        description_message = await self.client.wait_for(event = 'message', check = check, timeout = 60.0)
                        description = description_message.content
                    except asyncio.TimeoutError:
                        await ctx.send('Timed out.')
                    else:
                        try:
                            await ctx.send('Please type the tags of the video.')
                            tags_message = await self.client.wait_for(event = 'message', check = check, timeout = 60.0)
                            tags = tags_message.content
                            tags = tags.split(', ')
                        except asyncio.TimeoutError:
                            await ctx.send('Timed out.')
                        else:
                            try:
                                await ctx.send('Please select the category number.\n20 - Gaming\n21 - Videoblogging\n23 - Comedy\n24 - Entertainment\n25 - News & Politics\n27 - Education\n28 - Science & Technology\n42 - Shorts')
                                category_message = await self.client.wait_for(event = 'message', check = check, timeout = 60.0)
                                category = category_message.content
                            except asyncio.TimeoutError:
                                await ctx.send('Timed out.')
                            else:
                                try:
                                    await ctx.send('Please select the privacy status of the video:\npublic\nunlisted\nprivate')
                                    privacy_message = await self.client.wait_for(event = 'message', check = check, timeout = 60.0)
                                    privacy = privacy_message.content
                                except asyncio.TimeoutError:
                                    await ctx.send('Timed out.')
                                else:
                                    try:
                                        await ctx.send('Please upload the thumbnail of the video.')
                                        thumbnail_message = await self.client.wait_for(event = 'message', check = check, timeout = 60.0)
                                        thumbnail = thumbnail_message.attachments[0].url
                                    except asyncio.TimeoutError:
                                        await ctx.send('Timed out.')
                await ctx.send(f'Title: {title} | Description: {description} | Tags: {tags} | Category: {category} | Privacy: {privacy} | Thumbnail: {thumbnail}')

            else:
                await ctx.send("You didn't attach a video that I can upload to YouTube.")