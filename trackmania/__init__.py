from .trackmania import Trackmania

async def setup(bot):
    bot.add_cog(Trackmania(bot))
