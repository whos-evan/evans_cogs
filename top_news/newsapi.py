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
    @commands.cooldown(rate=1, per=150, type=commands.BucketType.user)
    async def topnews(self, ctx, country: str, number: int = 1):
        if number > 10:
            await ctx.send("Number must be less than 10.")
            return

        newsapikey = await self.bot.get_shared_api_tokens("newsapi")
        url = "https://newsapi.org/v2/top-headlines?country=" + country + "&apiKey=" + newsapikey['apiKey']

        data, status = await self.req(url)

        if status != 200:
            return await ctx.send("Error: " + str(status))

        if data["status"] != "ok":
            return await ctx.send("Error.")

        if data["totalResults"] == 0:
            return await ctx.send("No results.")

        options = []
        embeds = []
        for i in range(len(data["articles"])):
            # generates the options
            label = f"{str(i)} - {data['articles'][i]['title']}"
            if len(data['articles'][i]['description']) > 95:
                description = data['articles'][i]['description'][:95] + "..."
            else:
                description = data['articles'][i]['description']
            default = False
            option = discord.SelectOption(label=label, description=description, default=default)
            options.append(option)
            
            # generates the embeds
            article = data['articles'][i]
            embed = discord.Embed(
                title=f"{article['source']['name']} - {article['title']}",
                description=f"{article['author']}\n{article['description']}",
                url=article['url'],
                color=discord.Color.red()
            )
            embed.set_footer(text=article['publishedAt'])
            embeds.append(embed)
        
        class Dropdown(discord.ui.Select):
            def __init__(self):
                super().__init__(placeholder="Choose the news story to hear more about...",max_values=1,min_values=1,options=options)
            async def callback(self, interaction: discord.Interaction):
                num = self.values[0].split(' - ')[0]
                await interaction.response.send_message(content=None, embed=embeds[int(num)], ephemeral=True)

        class SelectView(discord.ui.View):
            def __init__(self, *, timeout = 86400):
                super().__init__(timeout=timeout)
                self.add_item(Dropdown())
        
        await ctx.send(f"Top {number} news from {country}.", view=SelectView())
