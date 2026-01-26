from discord.ext import commands


class testext(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hi", description="say hello from test extension")
    async def hi(self, ctx):
        await ctx.send("hello")


async def setup(bot):
    await bot.add_cog(testext(bot))
