# imports
import discord
import requests
from discord.ext import commands


# functions
def fetchimage(action):
    try:
        res = requests.get(f"https://api.waifu.pics/sfw/{action}", timeout=10)
        data = res.json()
        return data.get("url")
    except Exception as e:
        print("love_sfw api error:", e)
        return None


async def sendimage(ctx, action, user=None):
    try:
        url = fetchimage(action)
        if not url:
            await ctx.send(
                embed=discord.Embed(
                    title="error", description="failed to fetch image", color=0x0B3D91
                )
            )
            return

        desc = f"{ctx.author.mention} {action}s"
        if user:
            desc += f" {user.mention}"

        embed = discord.Embed(description=desc, color=0x0B3D91)
        embed.set_image(url=url)

        await ctx.send(embed=embed)

    except Exception as e:
        print("love_sfw send error:", e)
        await ctx.send(
            embed=discord.Embed(
                title="error", description="failed to send action", color=0x0B3D91
            )
        )


# cog
class love_sfw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kiss", description="kiss someone")
    async def kiss(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "kiss", user)

    @commands.command(name="hug", description="hug someone")
    async def hug(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "hug", user)

    @commands.command(name="slap", description="slap someone")
    async def slap(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "slap", user)

    @commands.command(name="cuddle", description="cuddle someone")
    async def cuddle(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "cuddle", user)

    @commands.command(name="waifu", description="random waifu")
    async def waifu(self, ctx):
        await sendimage(ctx, "waifu")

    @commands.command(name="cry", description="cry")
    async def cry(self, ctx):
        await sendimage(ctx, "cry")

    @commands.command(name="lick", description="lick someone")
    async def lick(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "lick", user)

    @commands.command(name="pat", description="pat someone")
    async def pat(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "pat", user)

    @commands.command(name="bonk", description="bonk someone")
    async def bonk(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "bonk", user)

    @commands.command(name="yeet", description="yeet someone")
    async def yeet(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "yeet", user)

    @commands.command(name="blush", description="blush")
    async def blush(self, ctx):
        await sendimage(ctx, "blush")

    @commands.command(name="smile", description="smile")
    async def smile(self, ctx):
        await sendimage(ctx, "smile")

    @commands.command(name="wave", description="wave")
    async def wave(self, ctx):
        await sendimage(ctx, "wave")

    @commands.command(name="highfive", description="high five someone")
    async def highfive(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "highfive", user)

    @commands.command(name="handhold", description="hold hands")
    async def handhold(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "handhold", user)

    @commands.command(name="bite", description="bite someone")
    async def bite(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "bite", user)

    @commands.command(name="glomp", description="glomp someone")
    async def glomp(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "glomp", user)

    @commands.command(name="kill", description="anime kill")
    async def kill(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "kill", user)

    @commands.command(name="kickk", description="kick someone")
    async def kick(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "kick", user)

    @commands.command(name="happy", description="be happy")
    async def happy(self, ctx):
        await sendimage(ctx, "happy")

    @commands.command(name="wink", description="wink")
    async def wink(self, ctx):
        await sendimage(ctx, "wink")

    @commands.command(name="poke", description="poke someone")
    async def poke(self, ctx, user: discord.Member = None):
        await sendimage(ctx, "poke", user)

    @commands.command(name="dance", description="dance")
    async def dance(self, ctx):
        await sendimage(ctx, "dance")

    @commands.command(name="cringe", description="cringe")
    async def cringe(self, ctx):
        await sendimage(ctx, "cringe")


# setup
async def setup(bot):
    await bot.add_cog(love_sfw(bot))
