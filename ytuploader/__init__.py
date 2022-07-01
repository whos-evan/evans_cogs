from .ytuploader import YTUploader

async def setup(bot):
    await bot.add_cog(YTUploader(bot))
