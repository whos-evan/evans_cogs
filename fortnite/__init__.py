from .trackmania import Trackmania

async def setup(bot):
    await bot.add_cog(Trackmania(bot))
