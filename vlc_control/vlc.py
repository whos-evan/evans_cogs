# other shit
import aiohttp
import xml.etree.ElementTree as ET

import asyncio

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
            "password": "test",
            "modonly": 'False'
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

    @vlc.command(name="modonly")
    @commands.admin_or_permissions(manage_guild=True)
    async def modonly(self, ctx):
        """
        Set the modonly setting.
        """
        settings = await self.config.custom("VLCGroup", ctx.guild.id).modonly()
        if 'True' in settings:
            await self.config.custom("VLCGroup", ctx.guild.id).modonly.set('False')
            await ctx.send("Modonly has been disabled.")
        else:
            await self.config.custom("VLCGroup", ctx.guild.id).modonly.set('True')
            await ctx.send("Modonly has been enabled.")

    @vlc.command(name="search")
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def search(self, ctx, *, search: str):
        """Search for stuff in VLC"""
        modonly = await self.config.custom("VLCGroup", ctx.guild.id).modonly()
        if 'True' in modonly and not ctx.author.guild_permissions.administrator:
            return
        else:
            url = await self.config.custom("VLCGroup", ctx.guild.id).url()
            password = await self.config.custom("VLCGroup", ctx.guild.id).password()
            full_search = await self.session.get(f'{url}/requests/playlist_jstree.xml', auth=aiohttp.BasicAuth('', password=password))
            full_search = await full_search.text()
            root = ET.fromstring(full_search)

            searched_items = []
            
            for item in root.findall('.//item/*'):
                if search.lower() in str(item.attrib).lower():
                    searched_items.append(item.attrib['id'].replace('plid_', '') + ' - ' + item.attrib['name'])
                    searched = item.findall('.//item')
                    for item in searched:
                        searched_items.append(item.attrib['id'].replace('plid_', '') + ' - ' + item.attrib['name'].replace('RARBG', ''))

            searched_items = list( dict.fromkeys(searched_items) )
            searched_list = '\n'.join(searched_items)

            def check(m: discord.Message):  # m = discord.Message.
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 
            
            if len(searched_items) == 0:
                await ctx.send("No results found.")
            else:
                await ctx.send(f"{len(searched_items)} results found. Please type the number next to the item you wish to play.\n{searched_list}")
                try:
                    message = await self.bot.wait_for('message', check=check, timeout=60.0)
                    if message.content.isdigit():
                        number = int(message.content)
                        if number > 200000:
                            await ctx.send("Number invalid.")
                        elif number < 0:
                            await ctx.send("Number invalid.")
                        else:
                            for item in searched_items:
                                if str(number) in item.split(' - ')[0]:
                                    requested = item
                            request = await self.session.get(f'{url}/requests/status.xml?command=pl_play&id={number}', auth=aiohttp.BasicAuth('', password=password))
                            if request.status == 200:
                                await ctx.send(f"Playing: {requested}")
                            else:
                                await ctx.send("Error while searching for that item number. Please try again.")
                    else:
                        await ctx.send("You didn't provide a number.")
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")
                except:
                    await ctx.send("Error while searching for that item number. Please try again.")
