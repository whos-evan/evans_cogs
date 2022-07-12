from .vlc import VLC

async def setup(bot):
    await bot.add_cog(VLC(bot))
