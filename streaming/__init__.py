from .streaming import Streaming

async def setup(bot) -> None:
    await bot.add_cog(Streaming(bot))
