# other shit
import aiohttp

import discord
from discord.ext import commands
from redbot.core import commands


class NewsAPI(commands.Cog):
    """
    NewsAPI cog.
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

    async def req(self, url):
        headers = {
            "User-Agent": "Trackmania Discord-Bot for Pulling Information About Maps",
            "From": "contact@is-a.win",  # This is another valid field
        }
        reqtype = self.session.get
        async with reqtype(url, headers=headers) as req:
            data = await req.json()
            status = req.status
        return data, status
    
    async def news_embed(article):
        embed = discord.Embed(
            title=f"{article['source']['name']} - {article['title']}",
            description=f"{article['author']}\n{article['description']}",
            url=article['url'],
            color=discord.Color.red()
        )
        embed.set_footer(text=article['publishedAt'])
        return embed
    
    @commands.group()
    async def news(self, ctx):
        """Group for news."""

    @news.command(name="top")
    @commands.cooldown(rate=1, per=25, type=commands.BucketType.user)
    async def topnews(self, ctx, country: str):
        newsapikey = await self.bot.get_shared_api_tokens("newsapi")
        url = "https://newsapi.org/v2/top-headlines?country=" + country + "&apiKey=" + newsapikey['apiKey']
        data, status = await self.req(url)
        if status != 200:
            return await ctx.send("Error: " + str(status))
        if data["status"] != "ok":
            return await ctx.send("Error.")
        if data["totalResults"] == 0:
            return await ctx.send("No results.")
        for i in range(4):
            article = data["articles"][i]
            embed = discord.Embed(
                title=f"{article['source']['name']} - {article['title']}",
                description=f"{article['author']}\n{article['description']}",
                url=article['url'],
                color=discord.Color.red()
            )
            embed.set_footer(text=article['publishedAt'])
            await ctx.send(embed=embed)