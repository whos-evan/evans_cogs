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

    async def req(self, url, creds, data):
        headers = {
            "User-Agent": "Discord-Bot for Pulling Information About Video Games",
            "From": "contact@is-a.win",
            'Accept': 'application/json',
            "Client-ID": creds['client_id'],
            "Authorization": f"Bearer {creds['access_token']}"
        }
        reqtype = self.session.post
        async with reqtype(url, headers=headers, data=data) as req:
            result = await req.text()
            status = req.status
        return result, status

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
            data = f'search "{search_term}"; fields name,platforms,summary,rating,screenshots,url; limit 50;'
            response = await self.req(url='https://api.igdb.com/v4/games', creds=creds, data=data)
            raw = response[0]
            results = json.loads(raw)

            embeds = []
            options = []

            for i in range(results):
                result = results[1]
                result = json.loads(str(result))

                title = str(i) + ". " + result['name']
                name = result['name']
                url = result['url']
                summary = result['summary']
                short_summary = summary[:20] + "..."

                option = discord.SelectOption(label=title, description=short_summary)
                options.append(option)

                embed = discord.Embed(title=name, url=url, description=summary)
                embeds.append(embed)

                class Dropdown(discord.ui.Select):
                    def __init__(self):
                        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
                    async def callback(self, interaction: discord.Interaction):
                        num = self.values[0].split(' - ')[0]
                        await interaction.response.send_message(content=None, embed=embeds[int(num)], ephemeral=True)
                        

                class SelectView(discord.ui.View):
                    def __init__(self, *, timeout = 180):
                        super().__init__(timeout=timeout)
                        self.add_item(Dropdown())

                await ctx.send('Choose the game you wish to view: ', view=SelectView())
            
            