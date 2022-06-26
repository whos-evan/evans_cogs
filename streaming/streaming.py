from typing import Literal

import aiohttp

from datetime import timedelta

import discord
from discord import utils
from discord.ext import tasks

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.config import Config


class Streaming(commands.Cog):
    """
    Performs actions when a streamer goes live.
    """

    __version__ = "0.0.1 beta"
    __author__ = "evan"

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=929150000791965787,
            force_registration=True,
        )

        self.session = aiohttp.ClientSession()

        self.config.register_guild(**default_guild)
        self.config.init_custom("StreamingGroup", 1)
        self.config.register_custom("StreamingGroup", **default_guild)

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    @commands.group()
    async def streaming(self, ctx):
        """Group for streaming info."""
    
    @streaming.command(name="setchannel")
    @commands.admin_or_permissions(manage_guild=True)
    async def streaming_setchannel(self, ctx, channel: str):
        """
        Set the channel to check for live streams.
        """

        if channel is None:
            await self.config.custom("StreamingGroup", ctx.guild.id).channel.set(None)
            await ctx.send("Channel has been cleared.")
        else:
            await self.config.custom("StreamingGroup", ctx.guild.id).channel.set(channel)
            await ctx.send("Channel set to {}".format(channel))

    @streaming.command(name="setvoicechat")
    @commands.admin_or_permissions(manage_guild=True)
    async def streaming_setchannel(self, ctx, vc: int):
        """
        Set the voice channel to set for the event creation.
        """

        if vc is None:
            await self.config.custom("StreamingGroup", ctx.guild.id).vc.set(None)
            await ctx.send("Voice chat has been cleared.")
        else:
            if await ctx.get_channel(vc) is None:
                await ctx.send("Voice chat does not exist.")
            else:
                await self.config.custom("StreamingGroup", ctx.guild.id).vc.set(vc)
                await ctx.send("Voice chat set to {}".format(vc))
    
    # check if a youtube channel is live using youtube api
    async def is_live(self, ctx):
        channel = await self.config.custom("StreamingGroup", ctx.guild.id).channel()
        youtube_api = await self.bot.get_shared_api_tokens("youtube")

        if channel or youtube_api is None:
            return False
        else:
            url = f'https://youtube.com/channel/{channel}/live'
            async with self.session.get(url) as resp:
                data = await resp.text
            if '{"text":" watching now"}' in data:
                return True
            else:
                return False
    
    async def create_streaming_event(self, ctx):
        channel = await self.config.custom("StreamingGroup", ctx.guild.id).channel()

        vc = await self.config.custom("StreamingGroup", ctx.guild.id).vc()
        vc = ctx.get_channel(vc)

        await ctx.guild.create_scheduled_event(name='Kazwire is live!', description=f'Kazwire is currently live on YouTube! Link: https://youtube.com/channel/{channel}/live', channel=vc, entity_type=discord.EntityType.voice, start_time=utils.utcnow() + timedelta(minutes=1)) # don't hard code this (channel name)
        await ctx.start(reason='Streamer is live!')


    @tasks.loop(seconds=60)
    async def check_streams(self):
        if await self.is_live() is True:
            await self.create_streaming_event()