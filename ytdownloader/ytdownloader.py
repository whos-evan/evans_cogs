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

            mp4files = yt.streams.filter(progressive=True, file_extension='mp4')
            mp4files.get_lowest_resolution().download(output_path=directory)

            full_directory = directory + "/" + str(mp4files.get_lowest_resolution().default_filename)
            
            async with aiohttp.ClientSession() as session:
                async with session.post('https://tmpfiles.org/api/v1/upload', data={'file': open(full_directory, 'rb')}) as resp:
                    response_json = await resp.json()
                    if response_json['status'] == 'success':
                        await ctx.send(f"Download complete. Link to file: {response_json['data']['url']}")
                    else:
                        await ctx.send(f"Error, possible that the file was just too big.")
            # delete the file
            os.remove(full_directory)
            
        else:
            await ctx.send("Please provide a valid youtube url that start's with ``https://www.youtube.com``")