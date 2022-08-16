from .ytdownloader import YouTubeDownloader

async def setup(bot):
    await bot.add_cog(ytdownloader(bot))
