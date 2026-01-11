# NOTE: Whoever is reading this code and thinks i added pretty bad debugging then you are correct
# imports
import random
import ast
import urllib.parse
import operator
import os
import time
import asyncio
import requests
import discord
from discord.ext import commands

# functions
class blaze(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # NOTE: made it a seperate function just in case iak needs them >.<
    def format_time(seconds): # type: ignore
        weeks = seconds // 604800 # type: ignore
        seconds %= 604800 # type: ignore
        days = seconds // 86400
        seconds %= 86400
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60    
        parts = []
        if weeks:
            parts.append(f"{weeks}w")
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
    
        return " ".join(parts) if parts else "just now"
        


    @commands.command(name="rolecreate", description="create a role")
    @commands.has_permissions(manage_roles=True)
    async def rolecreate(self, ctx, *, role):
        try:
            await ctx.guild.create_role(name=role)
            await ctx.send(f"role {role} created")
        except Exception as e:
            print("rolecreate error:", e)
            await ctx.send("failed to create role")

    @commands.command(name="roledelete", description="delete a role")
    @commands.has_permissions(manage_roles=True)
    async def roledelete(self, ctx, role: discord.Role):
        try:
            await role.delete()
            await ctx.send(f"role {role.name} deleted")
        except Exception as e:
            print("roledelete error:", e)
            await ctx.send("failed to delete role")

    @commands.command(name="createchannel", description="create a text or voice channel")
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx, name, channeltype=None):
        try:
            if channeltype == "voice":
                channel = await ctx.guild.create_voice_channel(name)
                embed = discord.Embed(
                    title="channel created",
                    description=f"voice channel {channel.name} created",
                    color=0x0b3d91
                )
            else:
                channel = await ctx.guild.create_text_channel(name)
                embed = discord.Embed(
                    title="channel created",
                    description=f"text channel {channel.name} created",
                    color=0x0b3d91
                )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("createchannel error:", e)
            await ctx.send("failed to create channel")
            
    @commands.command(name="removechannel", description="delete a channel")
    @commands.has_permissions(manage_channels=True)
    async def removechannel(self, ctx, channel: discord.TextChannel):
        try:
            name = channel.name
            await channel.delete()
    
            embed = discord.Embed(
                title="channel deleted",
                description=f"channel {name} deleted",
                color=0x0b3d91
            )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("removechannel error:", e)
            await ctx.send("failed to delete channel")
            
    @commands.command(name="createcatagory", description="creates a category")
    @commands.has_permissions(manage_channels=True)
    async def createcatagory(self, ctx, *, name):
        try:
            category = await ctx.guild.create_category(name)
            embed = discord.Embed(
                title="category created",
                description=f"category {category.name} created",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("createcatagory error:", e)
            await ctx.send("failed to create category")

    @commands.command(name="removecatagory", description="deletes a category")
    @commands.has_permissions(manage_channels=True)
    async def removecatagory(self, ctx, category: discord.CategoryChannel):
        try:
            name = category.name
            await category.delete()
            embed = discord.Embed(
                title="category removed",
                description=f"category {name} deleted",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("removecatagory error:", e)
            await ctx.send("failed to delete category")
            
    @commands.command(name="calc", description="calculate a math expression")
    async def calc(self, ctx, *, expr):
        try:
            print("calc input:", expr)
    
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.USub: operator.neg
            }
    
            def evalnode(node):
                if isinstance(node, ast.Num):
                    return node.n
                if isinstance(node, ast.BinOp):
                    return ops[type(node.op)](evalnode(node.left), evalnode(node.right))
                if isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](evalnode(node.operand))
                raise ValueError("invalid expression")
    
            result = evalnode(ast.parse(expr, mode="eval").body)
            await ctx.send(result)
        except Exception as e:
            print("calc error:", e)
            await ctx.send("invalid expression")
            
    @commands.command(name="afk", description="set yourself as afk")
    async def afk(self, ctx, *, reason=None):
        try:
            if not hasattr(self.bot, "afk_data"):
                self.bot.afk_data = {}
    
            self.bot.afk_data[ctx.author.id] = {
                "time": int(time.time()),
                "reason": reason,
                "pings": []
            }
    
            embed = discord.Embed(
                title="afk enabled",
                description=f"reason: {reason}" if reason else "no reason provided",
                color=0x0b3d91
            )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("afk error:", e)
            await ctx.send("failed to set afk")
     
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return
            ctx = await self.bot.get_context(message)
            if ctx.valid and ctx.command and ctx.command.name == "afk":
                return
            if hasattr(self.bot, "afk_data") and message.author.id in self.bot.afk_data:
                data = self.bot.afk_data.pop(message.author.id)
                count = len(data["pings"])
    
                embed = discord.Embed(
                    title="afk removed",
                    description=f"{count} people pinged you while you were away",
                    color=0x0b3d91
                )
    
                await message.channel.send(embed=embed)
    
                if count > 0:
                    lines = []
                    for entry in data["pings"]:
                        lines.append(f"{entry['user']}: {entry['content']} link")
    
                    await message.author.send(
                        f"{count} users pinged you:\n" + "\n".join(lines)
                    )
    
            if hasattr(self.bot, "afk_data"):
                for user in message.mentions:
                    if user.id in self.bot.afk_data:
                        data = self.bot.afk_data[user.id]
                        duration = format_time(int(time.time()) - data["time"]) # type: ignore
    
                        embed = discord.Embed(
                            title="user is afk",
                            description=f"reason: {data['reason']}" if data["reason"] else "no reason provided",
                            color=0x0b3d91
                        )
                        embed.add_field(name="away for", value=duration)
    
                        await message.channel.send(embed=embed)
    
                        data["pings"].append({
                            "user": message.author,
                            "content": message.content
                        })
        except Exception as e:
            print("afk listener error:", e)

            
    @commands.command(name="dm", description="send dm to user via bot")
    async def dm(self, ctx, user: commands.MemberConverter, *, msg):
        try:
            print("sender:", ctx.author)
            print("receiver:", user)
            await user.send(f"message from {ctx.author.name}: {msg}") # type: ignore
            await ctx.send("message sent")
        except Exception as e:
            print("dm command error:", e)
            await ctx.send("failed to send message")

    @commands.command(name="gay", description="check how gay someone is")
    async def gay(self, ctx, user: commands.MemberConverter):
        try:
            print("target:", user)
            percent = random.randint(0, 100)
            await ctx.send(f"{user.mention} is {percent}% gay 🌈") # type: ignore
        except Exception as e:
            print("gay command error:", e)
            await ctx.send("something went wrong")

    @commands.command(name="userinfo", description="get information about a user")
    async def userinfo(self, ctx, user: commands.MemberConverter):
        try:
            embed = discord.Embed(
                title="user information",
                color=0x0b3d91
            )
    
            embed.set_thumbnail(url=user.display_avatar.url) # type: ignore
            embed.add_field(name="username", value=f"{user.name}#{user.discriminator}", inline=True) # type: ignore
            embed.add_field(name="user id", value=user.id, inline=True) # type: ignore
            embed.add_field(name="joined server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False) # type: ignore
            embed.add_field(name="account created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False) # type: ignore
            embed.add_field(name="roles", value=", ".join([role.name for role in user.roles if role.name != "@everyone"]), inline=False) # type: ignore
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("userinfo error:", e)
            await ctx.send("failed to fetch user info")

    @commands.command(name="slowmode", description="set slowmode for the current channel")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
            embed = discord.Embed(
                title="slowmode updated",
                description=f"slowmode set to {seconds} seconds",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("slowmode error:", e)
            await ctx.send("failed to set slowmode")

    @commands.command(name="wiki", description="search wikipedia")
    async def wiki(self, ctx, *, query):
        try:
            data = await asyncio.to_thread(
                lambda: requests.get(
                    "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "%20")
                ).json()
            )
            if "extract" not in data:
                await ctx.send("no results found")
                return
    
            embed = discord.Embed(
                title=data.get("title"),
                description=data.get("extract"),
                color=0x0b3d91
            )
    
            if "thumbnail" in data:
                embed.set_thumbnail(url=data["thumbnail"]["source"])
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("wiki error:", e)
            await ctx.send("failed to fetch wiki info")

    @commands.command(name="autorole", description="set autoroles for new members")
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx, *roles: discord.Role):
        try:
            if not roles:
                await ctx.send("no roles provided")
                return
    
            if not hasattr(self.bot, "autoroles"):
                self.bot.autoroles = {}
    
            self.bot.autoroles[ctx.guild.id] = [role.id for role in roles]
    
            embed = discord.Embed(
                title="autorole updated",
                description=", ".join(role.name for role in roles),
                color=0x0b3d91
            )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("autorole error:", e)
            await ctx.send("failed to set autorole")

    @commands.command(name="roleall", description="add one or more roles to all members")
    @commands.has_permissions(manage_roles=True)
    async def roleall(self, ctx, *roles: discord.Role):
        try:
            if not roles:
                await ctx.send("no roles provided")
                return
    
            count = 0
            for member in ctx.guild.members:
                if member.bot:
                    continue
                await member.add_roles(*roles)
                count += 1
    
            embed = discord.Embed(
                title="roles added to all members",
                description=f"roles: {', '.join(role.name for role in roles)}\nmembers affected: {count}",
                color=0x0b3d91
            )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("roleall error:", e)
            await ctx.send("failed to add roles to all members")

    @commands.command(name="permissions", description="show a user's permissions")
    async def permissions(self, ctx, user: commands.MemberConverter):
        try:
            perms = user.guild_permissions # type: ignore
            allowed = [name.replace("_", " ") for name, value in perms if value]
    
            embed = discord.Embed(
                title="user permissions",
                description="\n".join(allowed) if allowed else "no permissions",
                color=0x0b3d91
            )
    
            embed.set_author(name=user.name, icon_url=user.display_avatar.url) # type: ignore
            await ctx.send(embed=embed)
        except Exception as e:
            print("permissions error:", e)
            await ctx.send("failed to fetch permissions")

    @commands.command(name="avatar", description="get user avatar")
    async def avatar(self, ctx, user: commands.MemberConverter):
        try:
            embed = discord.Embed(
                title="user avatar",
                color=0x0b3d91
            )
            embed.set_image(url=user.display_avatar.url) # type: ignore
            embed.set_author(name=user.name, icon_url=user.display_avatar.url) # type: ignore
            await ctx.send(embed=embed)
        except Exception as e:
            print("avatar error:", e)
            await ctx.send("failed to fetch avatar")
            
    @commands.command(name="meme", description="send a random meme")
    async def meme(self, ctx):
        try:
            data = await asyncio.to_thread(lambda: requests.get("https://meme-api.com/gimme").json())
            await ctx.send(data["url"])
        except Exception as e:
            print("meme error:", e)
            await ctx.send("failed to fetch meme")

    @commands.command(name="translate", description="translate text to english")
    async def translate(self, ctx, *, text):
        try:
            data = await asyncio.to_thread(
                lambda: requests.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={
                        "client": "gtx",
                        "sl": "auto",
                        "tl": "en",
                        "dt": "t",
                        "q": text
                    }
                ).json()
            )
            await ctx.send(data[0][0][0])
        except Exception as e:
            print("translate error:", e)
            await ctx.send("failed to translate")

    @commands.command(name="dice", description="roll a dice")
    async def dice(self, ctx):
        try:
            result = random.randint(1, 6)
            await ctx.send(f"🎲 rolled: {result}")
        except Exception as e:
            print("dice error:", e)
            await ctx.send("failed to roll dice")
            
    @commands.command(name="joke", description="sends a random joke")
    async def joke(self, ctx):
        data = await asyncio.to_thread(lambda: requests.get("https://official-joke-api.appspot.com/random_joke").json())
        await ctx.send(f"{data['setup']}\n{data['punchline']}")

    @commands.command(name="fact", description="get a random fact")
    async def fact(self, ctx):
        try:
            data = await asyncio.to_thread(lambda: requests.get("https://api.popcat.xyz/v2/fact").json())
            await ctx.send(data["message"]["fact"])
        except Exception as e:
            print("fact error:", e)
            await ctx.send("failed to fetch fact")

    @commands.command(name="roast", description="roast a user")
    async def roast(self, ctx, user: commands.MemberConverter):
        try:
            data = await asyncio.to_thread(
                lambda: requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json").json()
            )
            await ctx.send(f"{user.mention} {data['insult']}") # type: ignore
        except Exception as e:
            print("roast error:", e)
            await ctx.send("failed to roast user")
            
    @commands.command(name="ip", description="get information about an ipv4 address")
    async def ip(self, ctx, address):
        try:
            data = await asyncio.to_thread(lambda: requests.get(f"http://ip-api.com/json/{address}").json())
            if data.get("status") != "success":
                await ctx.send("invalid ip address")
                return
    
            embed = discord.Embed(
                title="ip information",
                color=0x0b3d91
            )
    
            embed.add_field(name="ip", value=data.get("query"), inline=False)
            embed.add_field(name="country", value=data.get("country"), inline=True)
            embed.add_field(name="region", value=data.get("regionName"), inline=True)
            embed.add_field(name="city", value=data.get("city"), inline=True)
            embed.add_field(name="isp", value=data.get("isp"), inline=False)
            embed.add_field(name="timezone", value=data.get("timezone"), inline=True)
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("ip error:", e)
            await ctx.send("failed to fetch ip information")

            
async def setup(bot):
    cog = blaze(bot)
    await bot.add_cog(cog)

    cmds = [command.name for command in cog.get_commands()]
    print(f"Blaze added {len(cmds)} commands: {', '.join(cmds)}") # NOTE: Specially made this part for iak :3

# NOTE FOR IAK: you have probably read the entire code by now, im so sorry for whatever i messed up😭🙏
