# other shit
import aiohttp
import xml.etree.ElementTree as ET

import discord
from discord.ext import commands
from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS


class VLC(commands.Cog):
    """
    VLC cog.
    """

    __version__ = "0.0.1 beta"
    __author__ = "evan"

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.config = Config.get_conf(
            self,
            identifier=929150000791965787,
            force_registration=True
        )

        default_guild = {
            "url": "http://localhost:8080",
            "password": "test"
        }

        self.config.register_guild(**default_guild)
        self.config.init_custom("VLCGroup", 1)
        self.config.register_custom("VLCGroup", **default_guild)

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    async def cog_unload(self):
        await self.client.close()

    @commands.group()
    async def vlc(self, ctx):
        """Group for VLC."""

    @vlc.command(name="seturl")
    @commands.admin_or_permissions(manage_guild=True)
    async def seturl(self, ctx, url: str = None):
        """
        Set the url.
        """
        if url is None:
            await self.config.custom("VLCGroup", ctx.guild.id).url.set(None)
            await ctx.send("Url has been cleared.")
        else:
            await self.config.custom("VLCGroup", ctx.guild.id).url.set(url)
            await ctx.send("Url set to {}".format(url))

    @vlc.command(name="setpassword")
    @commands.admin_or_permissions(manage_guild=True)
    async def setpassword(self, ctx, password = None):
        """
        Set the password.
        """
        if password is None:
            await self.config.custom("VLCGroup", ctx.guild.id).password.set(None)
            await ctx.send("Password has been cleared.")
        else:
            await self.config.custom("VLCGroup", ctx.guild.id).password.set(password)
            await ctx.send("Password set to {}".format(password))

    @vlc.command(name="search")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def search(self, ctx, *, search: str):
        """Search for stuff in VLC"""
        url = await self.config.custom("VLCGroup", ctx.guild.id).url()
        password = await self.config.custom("VLCGroup", ctx.guild.id).password()
        full_search = await self.session.get(f'{url}/requests/playlist_jstree.xml', auth=aiohttp.BasicAuth('', password=password))
        print(await full_search.text())
        full_search = await full_search.text()
        root = ET.fromstring(full_search)

        items = []
        searched_items = []
        times = 0
        for elem in root.iter('item'):
            
            items.append(elem.attrib)
        
        for item in items:
            times += 1
            if search in str(item):
                searched_items.append(str(times) + ' - ' + item['name'])
                searched_list = '\n'.join(searched_items)
        
        await ctx.send(f"{len(searched_items)} results found.\n{searched_list}")
        message = await ctx.guild.wait_for('message', check=lambda m: m.author == ctx.author)
        number = int(message.content)
        item_id = items[number]['id']
        item_id = item_id.replace('plid', '')

        self.session.get(f'{url}/requests/status.xml?command=pl_play&id={item_id}', auth=aiohttp.BasicAuth('', password=password))
