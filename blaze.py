# NOTE FOR IAK: Embeds to edit are at lines: 42, 51, 73, 82, 90, 64, 101, 110, 118, 129, 138, 148, 156,  167, 178, 186, 197, 212, 220, 231, 241, 249, 260, 271, 279, 327, 350, 373, 394, 405, 413, 421, 447, 458, 468, 476, 494, 513, 526, 534, 547, 604, 615, 624, 637, 673, 682, 694, 708, 717, 805, 819, 827, 842, 853, 868, 884
# NOTE: Whoever is reading this code and thinks i added pretty bad debugging then you are correct
# imports
import random
import ast
import operator
import time
import asyncio
import requests
import discord
from discord.ext import commands

# cog
class blaze(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_time(self, seconds):
        weeks = seconds // 604800
        seconds %= 604800
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

    @commands.command(name="roleadd", description="add a role to a user")
    @commands.has_permissions(manage_roles=True)
    async def roleadd(self, ctx, role: discord.Role, user: discord.Member):
        try:
            if role >= ctx.guild.me.top_role:
                await ctx.send(embed=discord.Embed(
                    title="permission error",
                    description="my role is lower than the given role",
                    color=0x0b3d91
                ))
                return

            await user.add_roles(role)

            await ctx.send(embed=discord.Embed(
                title="role added",
                description=f"added {role.name} to {user.mention}",
                color=0x0b3d91
            ))
        except Exception as e:
            print("roleadd error:", e)

    @commands.command(name="roleremove", description="remove a role from a user")
    @commands.has_permissions(manage_roles=True)
    async def roleremove(self, ctx, role: discord.Role, user: discord.Member):
        try:
            if not ctx.guild.me.guild_permissions.manage_roles:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage roles permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            if role >= ctx.guild.me.top_role:
                embed = discord.Embed(
                    title="role error",
                    description="bot role must be higher than the given role",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            await user.remove_roles(role)
            embed = discord.Embed(
                title="role removed",
                description=f"removed {role.name} from {user.mention}",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("roleremove error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to remove role",
                color=0x0b3d91
            ))
            
    @commands.command(name="rolecreate", description="create a role")
    @commands.has_permissions(manage_roles=True)
    async def rolecreate(self, ctx, *, role):
        try:
            if not ctx.guild.me.guild_permissions.manage_roles:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage roles permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            await ctx.guild.create_role(name=role)
            embed = discord.Embed(
                title="role created",
                description=f"role {role} have been created",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("rolecreate error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to create role",
                color=0x0b3d91
            ))

    @commands.command(name="roledelete", description="delete a role")
    @commands.has_permissions(manage_roles=True)
    async def roledelete(self, ctx, role: discord.Role):
        try:
            if not ctx.guild.me.guild_permissions.manage_roles:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage roles permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            if role >= ctx.guild.me.top_role:
                embed = discord.Embed(
                    title="role error",
                    description="bot role must be higher than the target role",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            name = role.name
            await role.delete()
            embed = discord.Embed(
                title="role deleted",
                description=f"role {name} have been deleted",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("roledelete error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to delete role",
                color=0x0b3d91
            ))    
            
    @commands.command(name="removechannel", description="delete a channel")
    @commands.has_permissions(manage_channels=True)
    async def removechannel(self, ctx, channel: discord.TextChannel):
        try:
            if not ctx.guild.me.guild_permissions.manage_channels:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage channels permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            name = channel.name
            await channel.delete()
    
            embed = discord.Embed(
                title="channel deleted",
                description=f"channel {name} have been deleted",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("removechannel error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to delete channel",
                color=0x0b3d91
            ))

    @commands.command(name="createchannel", description="create a text or voice channel")
    @commands.has_permissions(manage_channels=True)
    async def createchannel(self, ctx, name, channeltype=None):
        try:
            if not ctx.guild.me.guild_permissions.manage_channels:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage channels permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            if channeltype == "voice":
                channel = await ctx.guild.create_voice_channel(name)
                desc = f"voice channel {channel.name} have been created"
            else:
                channel = await ctx.guild.create_text_channel(name)
                desc = f"text channel {channel.name} has been created"
    
            embed = discord.Embed(
                title="channel created",
                description=desc,
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("createchannel error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to create channel",
                color=0x0b3d91
            ))
            
    @commands.command(name="createcategory", description="create a category")
    @commands.has_permissions(manage_channels=True)
    async def createcategory(self, ctx, *, name):
        try:
            if not ctx.guild.me.guild_permissions.manage_channels:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage channels permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            category = await ctx.guild.create_category(name)
    
            embed = discord.Embed(
                title="category created",
                description=f"category {category.name} have been created",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("createcategory error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to create category",
                color=0x0b3d91
            ))
            
    @commands.command(name="removecategory", description="delete a category")
    @commands.has_permissions(manage_channels=True)
    async def removecategory(self, ctx, category: discord.CategoryChannel):
        try:
            if not ctx.guild.me.guild_permissions.manage_channels:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage channels permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            name = category.name
            await category.delete()
    
            embed = discord.Embed(
                title="category removed",
                description=f"category {name} have been deleted",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("removecategory error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to delete category",
                color=0x0b3d91
            ))
            
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
                        duration = format_time(int(time.time()) - data["time"])
    
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

                
    @commands.command(name="dm", description="send a dm to a user")
    async def dm(self, ctx, user: commands.MemberConverter, *, msg):
        try:
            if user.bot:
                embed = discord.Embed(
                    title="invalid user",
                    description="you cannot dm a bot",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            try:
                await user.send(f"message from {ctx.author.name}: {msg}")
            except discord.Forbidden:
                embed = discord.Embed(
                    title="dm failed",
                    description="user has dms disabled or blocked the bot",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            embed = discord.Embed(
                title="message sent",
                description=f"dm sent to {user.mention}",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("dm error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to send dm",
                color=0x0b3d91
            ))
                                    
    @commands.command(name="gay", description="check how gay someone is")
    async def gay(self, ctx, user: commands.MemberConverter):
        try:
            if user.id == 1238444724386533417:
                embed = discord.Embed(
                    description="blud he got girlfriend, leave em",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            percent = random.randint(0, 100)
    
            embed = discord.Embed(
                description=f"{user.mention} is {percent}% gay 🌈",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("gay error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="something went wrong",
                color=0x0b3d91
            ))
            
    @commands.command(name="slowmode", description="set slowmode for the current channel")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        try:
            if not ctx.guild.me.guild_permissions.manage_channels:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage channels permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            await ctx.channel.edit(slowmode_delay=seconds)
    
            embed = discord.Embed(
                title="slowmode updated",
                description=f"slowmode set to {seconds} seconds",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("slowmode error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to set slowmode",
                color=0x0b3d91
            ))

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
            if not ctx.guild.me.guild_permissions.manage_roles:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage roles permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
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
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to set autorole",
                color=0x0b3d91
            ))

    @commands.command(name="user", description="show user information")
    async def user(self, ctx, user: commands.MemberConverter):
        try:
            perms = user.guild_permissions
            allowed = [name.replace("_", " ") for name, value in perms if value]
            roles = [role.name for role in user.roles if role.name != "@everyone"]
    
            embed = discord.Embed(
                title="user info",
                color=0x0b3d91
            )
    
            embed.set_thumbnail(url=user.display_avatar.url)
    
            embed.add_field(
                name="display name",
                value=user.display_name,
                inline=True
            )
    
            embed.add_field(
                name="username",
                value=f"{user.name}#{user.discriminator}",
                inline=True
            )
    
            embed.add_field(
                name="user id",
                value=user.id,
                inline=False
            )
    
            embed.add_field(
                name="joined server",
                value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
    
            embed.add_field(
                name="joined discord",
                value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
    
            embed.add_field(
                name="roles",
                value=", ".join(roles) if roles else "no roles",
                inline=False
            )
    
            embed.add_field(
                name="permissions",
                value="\n".join(allowed) if allowed else "no permissions",
                inline=False
            )
    
            embed.set_author(
                name=user.name,
                icon_url=user.display_avatar.url
            )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("user command error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to fetch user information",
                color=0x0b3d91
            ))
            
    @commands.command(name="roleall", description="add roles to all members")
    @commands.has_permissions(manage_roles=True)
    async def roleall(self, ctx, *roles: discord.Role):
        try:
            if not ctx.guild.me.guild_permissions.manage_roles:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage roles permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            if not roles:
                embed = discord.Embed(
                    title="input error",
                    description="no roles provided",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            members = [m for m in ctx.guild.members if not m.bot]
            total = len(members)
            done = 0
            start = time.time()
    
            embed = discord.Embed(
                title="roleall is in progresss", 
                description=f"0/{total} users updated",
                color=0x0b3d91
            )
            msg = await ctx.send(embed=embed)
            last_edit = time.time()
    
            for member in members:
                try:
                    if all(role in member.roles for role in roles):
                        continue
            
                    await member.add_roles(*roles)
                    done += 1
                    await asyncio.sleep(0.8)
                except Exception as e:
                    print("roleall users error", e)
            
                if time.time() - last_edit >= 3:
                    elapsed = time.time() - start
                    rate = done / elapsed if elapsed > 0 else 0
                    remaining = total - done
                    eta = remaining / rate if rate > 0 else 0
            
                    if eta >= 3600:
                        eta_text = f"{int(eta // 3600)}h"
                    elif eta >= 60:
                        eta_text = f"{int(eta // 60)}m"
                    else:
                        eta_text = f"{int(eta)}s"
            
                    embed.description = f"{done}/{total} users got role\neta: {eta_text}"
                    await msg.edit(embed=embed)
                    last_edit = time.time()
            
            embed = discord.Embed(
                title="roleall completed",
                description=f"{done}/{total} users got role",
                color=0x0b3d91
            )
            await msg.edit(embed=embed)
            
        except Exception as e:
            print("roleall error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to add roles to all members",
                color=0x0b3d91
            ))

    @commands.command(name="permissions", description="show a user's permissions")
    async def permissions(self, ctx, user: commands.MemberConverter):
        try:
            perms = user.guild_permissions
            allowed = [name.replace("_", " ") for name, value in perms if value]
    
            embed = discord.Embed(
                title="user permissions",
                description="\n".join(allowed) if allowed else "no permissions",
                color=0x0b3d91
            )
    
            embed.set_author(
                name=user.name,
                icon_url=user.display_avatar.url
            )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("permissions error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to fetch permissions",
                color=0x0b3d91
            ))

    @commands.command(name="avatar", description="get user avatar")
    async def avatar(self, ctx, user: commands.MemberConverter):
        try:
            embed = discord.Embed(
                title="user avatar",
                color=0x0b3d91
            )
            embed.set_image(url=user.display_avatar.url)
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
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
            if user.id == 1238444724386533417:
                embed = discord.Embed(
                    description=f"Fuck you bitch {ctx.author.mention}",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            data = await asyncio.to_thread(
                lambda: requests.get(
                    "https://evilinsult.com/generate_insult.php?lang=en&type=json"
                ).json()
            )
    
            embed = discord.Embed(
                description=f"{user.mention} {data['insult']}",
                color=0x0b3d91
            )
    
            await ctx.send(embed=embed)
        except Exception as e:
            print("roast error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to roast user",
                color=0x0b3d91
            ))
            
    @commands.command(name="ip", description="get information about an ip address")
    async def ip(self, ctx, address):
        try:
            data = await asyncio.to_thread(
                lambda: requests.get(f"http://ip-api.com/json/{address}").json()
            )
    
            if data.get("status") != "success":
                embed = discord.Embed(
                    title="invalid ip address",
                    description="the provided ip address is not valid",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
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
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to fetch ip information",
                color=0x0b3d91
            ))

# NOTE: global handler cuz im lazy:3
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            if isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(
                    title="missing value",
                    description=f"required value: `{error.param.name}`",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            if isinstance(error, commands.BadArgument):
                received = None
                if ctx.message.content:
                    parts = ctx.message.content.split()
                    if len(parts) > 1:
                        received = " ".join(parts[1:])
    
                embed = discord.Embed(
                    title="invalid value",
                    description=(
                        f"required value: `{ctx.command.clean_params.keys()}`\n"
                        f"received value: `{received}`"
                        if received else
                        f"required value: `{ctx.command.clean_params.keys()}`"
                    ),
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            if isinstance(error, commands.CommandNotFound):
                return
    
            embed = discord.Embed(
                title="error",
                description="an unexpected error occurred",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
    
            print("unhandled command error:", error)
        except Exception as e:
            print("error handler failure:", e)
            
async def setup(bot):
    cog = blaze(bot)
    await bot.add_cog(cog)

    cmds = [command.name for command in cog.get_commands()]
    print(f"Blaze added {len(cmds)} commands: {', '.join(cmds)}") # NOTE: Specially made this part for iak :3
    print("blaze's global error handler active")
# NOTE FOR IAK: you have probably read the entire code by now, im so sorry for whatever i messed up😭🙏
