from pytube import YouTube # yt downloader
import aiohttp
import os

import discord
from discord.ext import commands, tasks
from redbot.core import commands
from redbot.core.data_manager import cog_data_path


class YouTubeDownloader(commands.Cog):
    """
    YouTube Downloader cog.
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

    @commands.group('ytdownloader')
    async def ytdownloader(self, ctx):
        """Group for ytdownloader."""

    async def upload(file_path):
        """Upload the file to tmpfiles."""
        async with aiohttp.ClientSession() as session:
            async with session.post('https://tmpfiles.org/', data={'file': open(file_path, 'rb')}) as resp:
                return await resp.text()
    
    @ytdownloader.command('download')
    async def download(self, ctx, url: str = None):
        """
        Download a youtube video, must start with ``https://www.youtube.com``
        """
        if url is None:
            await ctx.send("Please provide a url.")
        elif url.startswith('https://www.youtube.com') is True:
            yt = YouTube(url)
            directory = str(cog_data_path(self)) + '/tmp/'
            full_directory = directory + "/" + str(yt.streams.first().default_filename)
            download = yt.streams.first().download(output_path=directory)
            upload = await self.upload(file_path=full_directory)
            # delete the file
            os.remove(full_directory)
            await ctx.send("Download complete. Link to file: {}".format(upload))
        else:
            await ctx.send("Please provide a valid youtube url that start's with ``https://www.youtube.com``")