# imports
import discord
import requests
from discord.ext import commands


# functions
def fetchimage(action):
    try:
        res = requests.get(f"https://api.waifu.pics/nsfw/{action}", timeout=10)
        data = res.json()
        return data.get("url")
    except Exception as e:
        print("love_nsfw api error:", e)
        return None


async def sendimage(ctx, action, user=None):
    try:
        if not ctx.channel.is_nsfw():
            await ctx.send(
                embed=discord.Embed(
                    title="nsfw only",
                    description="this command can only be used in nsfw channels",
                    color=0x0B3D91,
                )
            )
            return

        url = fetchimage(action)
        if not url:
            await ctx.send(
                embed=discord.Embed(
                    title="error", description="failed to fetch image", color=0x0B3D91
                )
            )
            return

        desc = f"{ctx.author.mention} {action}"
        if user:
            desc += f" {user.mention}"

        embed = discord.Embed(description=desc, color=0x0B3D91)
        embed.set_image(url=url)

        await ctx.send(embed=embed)

    except Exception as e:
        print("love_nsfw send error:", e)
        await ctx.send(
            embed=discord.Embed(
                title="error", description="failed to send action", color=0x0B3D91
            )
        )


# cog
class love_nsfw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="waifu18+", description="nsfw waifu")
    async def waifu18(self, ctx):
        await sendimage(ctx, "waifu")

    @commands.command(name="neko", description="nsfw neko")
    async def neko(self, ctx):
        await sendimage(ctx, "neko")

    @commands.command(name="blowjob", description="nsfw blowjob")
    async def blowjob(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "blowjob", user)

    @commands.command(name="trap", description="nsfw trap")
    async def trap(self, ctx):
        await sendimage(ctx, "trap")


# setup
async def setup(bot):
    await bot.add_cog(love_nsfw(bot))
