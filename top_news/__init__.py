from .newsapi import NewsAPI

async def setup(bot):
    await bot.add_cog(NewsAPI(bot))
