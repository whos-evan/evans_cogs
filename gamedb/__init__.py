from .gamedb import GameDB

async def setup(bot):
    await bot.add_cog(GameDB(bot))
