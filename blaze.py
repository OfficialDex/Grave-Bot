# NOTE FOR IAK: Embeds to edit are at lines:  201, 210, 229, 238, 248, 267, 278, 297, 312, 331, 341, 360, 371, 427, 450, 473, 494, 557, 565, 574, 593, 601, 610, 622, 644, 659, 679, 698, 719, 737, 757, 779, 794, 805, 823, 864, 875, 887, 897, 907, 944, 988, 999, 1014, 1024, 1034, 1092, 1104, 1115, 1133, 1142, 1159, 1167, 1175, 1184, 1201, 1209, 1217, 1226, 1282, 1294, 1310, 1319, 1328, 1339, 1348, 1370, 1391, 1403, 1414, 1426, 1438, 1454, 1659, 1667, 1724, 1766, 1862, 1872, 1907, 1917, 1935, 1949, 1958, 1964, 1977, 1989, 2002, 2023, 2091, 2100, 2113, 2149, 2170, 2189, 2204, 2235, 2253, 2275, 2297, 2353, 2361, 2389, 2404, 2420: updated:)
# NOTE: Whoever is reading this code and thinks i added pretty bad debugging then you are correct
# imports
import random
import os
import subprocess 
import importlib.util
import traceback
import uuid
import json
import base64
from io import BytesIO
import ast
import operator
import time
import asyncio
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

# helpers
def loadleaderboard():
    try:
        if not os.path.exists("leaderboard.json"):
            return {"messages": {}, "invites": {}}

        with open("leaderboard.json", "r") as f:
            data = json.load(f)

        if "messages" not in data or "invites" not in data:
            return {"messages": {}, "invites": {}}

        return data

    except Exception as e:
        print("leaderboard load error:", e)
        return {"messages": {}, "invites": {}}

def saveleaderboard(data):
    try:
        with open("leaderboard.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("leaderboard save error:", e)

def loadaliases():
    try:
        if not os.path.exists("aliases.json"):
            return {}
        with open("aliases.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print("alias load error:", e)
        return {}

def savealiases(data):
    try:
        with open("aliases.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("alias save error:", e)

def loadjson(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print("json load error:", e)
        return default


def savejson(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("json save error:", e)

def testextension(filepath):
    try:
        with open(filepath, "r") as f:
            compile(f.read(), filepath, "exec")
        return True, None
    except Exception as e:
        return False, str(e)

def extensionfail(name, reason):
    print(f"({name}) {reason}")
    return discord.Embed(
        title="installation failed",
        description="due to broken extension, we cannot install this",
        color=0x0b3d91
    )

async def githubpull():
    while True:
        try:
            fetch = subprocess.run(
                ["git", "fetch", "origin"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if fetch.returncode != 0:
                print("ssh fetch failed, trying token fallback")

                token = os.getenv("github_token")
                if not token:
                    print("github token not set, cannot fallback")
                    await asyncio.sleep(3600)
                    continue

                repo = "github.com/imiakk/GraveBot.git"
                tokenurl = f"https://{token}@{repo}"

                seturl = subprocess.run(
                    ["git", "remote", "set-url", "origin", tokenurl],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if seturl.returncode != 0:
                    print("failed to set token remote:", seturl.stderr.strip())
                    await asyncio.sleep(3600)
                    continue

                fetch = subprocess.run(
                    ["git", "fetch", "origin"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if fetch.returncode != 0:
                    print("token fetch failed:", fetch.stderr.strip())
                    await asyncio.sleep(3600)
                    continue

            checkout = subprocess.run(
                ["git", "checkout", "origin/main", "--", "extensions", "extensions.json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if checkout.returncode != 0:
                print("checkout error:", checkout.stderr.strip())

            subprocess.run(
                ["git", "remote", "set-url", "origin", "git@github.com:imiakk/GraveBot.git"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        except Exception as e:
            print("github pull exception:", e)

        await asyncio.sleep(3600)

# cog
class blaze(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memory = {}
        self.invites = {}
        if not hasattr(bot, "githubtask"):
            bot.githubtask = bot.loop.create_task(githubpull())

        # NOTE: made it a seperate function just in case iak needs them >.<
    def format_time(seconds):# type: ignore
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

                
    @commands.command(name="dm", description="send a dm to a user")
    async def dm(self, ctx, user: commands.MemberConverter, *, msg):
        try:
            await user.send(
                embed=discord.Embed(
                    title="new message",
                    description=f"from {ctx.author.name}:\n{msg}",
                    color=0x0b3d91
                )
            )

            await ctx.send(embed=discord.Embed(
                title="success",
                description="message sent successfully",
                color=0x0b3d91
            ))

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="error",
                description="i cannot dm this user",
                color=0x0b3d91
            ))

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
                await ctx.send(embed=discord.Embed(
                    description="blud he got girlfriend, leave em",
                    color=0x0b3d91
                ))
                return

            await ctx.send(embed=discord.Embed(
                description=f"<@{user.id}> is {random.randint(0, 100)}% gay 🌈",
                color=0x0b3d91
            ))

        except Exception as e:
            print("gay command error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="something went wrong",
                color=0x0b3d91
            ))

    @commands.command(name="encode", description="encode text into base formats")
    async def encode(self, ctx, base, *, text):
        try:
            base = base.lower()

            if base == "base64":
                result = base64.b64encode(text.encode()).decode()
            elif base == "base32":
                result = base64.b32encode(text.encode()).decode()
            elif base == "base16":
                result = base64.b16encode(text.encode()).decode()
            else:
                embed = discord.Embed(
                        title="invalid base",
                        description="supported bases: base16, base32, base64",
                        color=0x0b3d91
                        )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                    title="encoded",
                    description=f"```\n{result}\n```",
                    color=0x0b3d91
                    )
            await ctx.send(embed=embed)

        except Exception as e:
            print("encode error:", e)
            embed = discord.Embed(
                    title="error",
                    description="failed to encode text",
                    color=0x0b3d91
                    )
            await ctx.send(embed=embed)

    @commands.command(name="decode", description="decode text from base formats")
    async def decode(self, ctx, base, *, text):
        try:
            base = base.lower()

            if base == "base64":
                result = base64.b64decode(text).decode()
            elif base == "base32":
                result = base64.b32decode(text).decode()
            elif base == "base16":
                result = base64.b16decode(text).decode()
            else:
                embed = discord.Embed(
                        title="invalid base",
                        description="supported bases: base16, base32, base64",
                        color=0x0b3d91
                        )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                    title="decoded",
                    description=f"```\n{result}\n```",
                    color=0x0b3d91
                    )
            await ctx.send(embed=embed)

        except Exception as e:
            print("decode error:", e)
            embed = discord.Embed(
                    title="error",
                    description="invalid encoded text or wrong base selected",
                    color=0x0b3d91
                    )
            await ctx.send(embed=embed)

    @commands.command(name="createemoji", description="create emoji from image")
    @commands.has_permissions(manage_emojis=True)
    async def createemoji(self, ctx, name=None):
        try:
            if not ctx.guild.me.guild_permissions.manage_emojis:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage emojis permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            images = []

            if ctx.message.attachments:
                images = ctx.message.attachments
            elif ctx.message.reference:
                ref = ctx.message.reference.resolved
                if ref and ref.attachments:
                    images = ref.attachments
            elif ctx.message.content and ctx.message.raw_mentions == []:
                for e in ctx.message.emojis:
                    emoji = await e.read()
                    images.append(type("obj", (), {"read": lambda: emoji}))

            if not images:
                embed = discord.Embed(
                    title="missing image",
                    description="attach or reply to an image or emoji",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            created = []
            for img in images:
                data = await img.read()
                ename = name or f"emoji_{uuid.uuid4().hex[:6]}"
                emoji = await ctx.guild.create_custom_emoji(name=ename, image=data)
                created.append(emoji.name)

            embed = discord.Embed(
                title="emoji created",
                description=", ".join(created),
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print("createemoji error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to create emoji",
                color=0x0b3d91
            ))

    @commands.command(name="removeemoji", description="remove emoji")
    @commands.has_permissions(manage_emojis=True)
    async def removeemoji(self, ctx, emoji: discord.Emoji):
        try:
            await emoji.delete()
            embed = discord.Embed(
                title="emoji removed",
                description=emoji.name,
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("removeemoji error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to remove emoji",
                color=0x0b3d91
            ))

    @commands.command(name="createsticker", description="create sticker from image")
    @commands.has_permissions(manage_emojis=True)
    async def createsticker(self, ctx, name=None):
        try:
            if not ctx.guild.me.guild_permissions.manage_emojis:
                embed = discord.Embed(
                    title="permission error",
                    description="bot does not have manage emojis permission",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            image = None

            if ctx.message.attachments:
                image = ctx.message.attachments[0]
            elif ctx.message.reference:
                ref = ctx.message.reference.resolved
                if ref and ref.attachments:
                    image = ref.attachments[0]
            elif ctx.message.stickers:
                sticker = ctx.message.stickers[0]
                image = await sticker.read()

            if not image:
                embed = discord.Embed(
                    title="missing image",
                    description="attach or reply to an image or sticker",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            data = await image.read() if hasattr(image, "read") else image
            sname = name or f"sticker_{uuid.uuid4().hex[:6]}"

            sticker = await ctx.guild.create_sticker(
                name=sname,
                description="created by grave",
                emoji="🔥",
                file=discord.File(fp=BytesIO(data), filename="sticker.png")
            )

            embed = discord.Embed(
                title="sticker created",
                description=sticker.name,
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print("createsticker error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to create sticker",
                color=0x0b3d91
            ))

    @commands.command(name="removesticker", description="remove sticker")
    @commands.has_permissions(manage_emojis=True)
    async def removesticker(self, ctx, sticker: discord.GuildSticker):
        try:
            await sticker.delete()
            embed = discord.Embed(
                title="sticker removed",
                description=sticker.name,
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("removesticker error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to remove sticker",
                color=0x0b3d91
            ))

    @commands.command(name="servericon", description="change server icon")
    @commands.has_permissions(manage_guild=True)
    async def servericon(self, ctx):
        try:
            image = None

            if ctx.message.attachments:
                if len(ctx.message.attachments) != 1:
                    embed = discord.Embed(
                        title="invalid input",
                        description="attach only one image",
                        color=0x0b3d91
                    )
                    await ctx.send(embed=embed)
                    return
                image = ctx.message.attachments[0]

            elif ctx.message.reference:
                ref = ctx.message.reference.resolved
                if ref and ref.attachments and len(ref.attachments) == 1:
                    image = ref.attachments[0]

            if not image:
                embed = discord.Embed(
                    title="missing image",
                    description="attach or reply to a single image",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            data = await image.read()
            await ctx.guild.edit(icon=data)

            embed = discord.Embed(
                title="server icon updated",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print("servericon error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to update server icon",
                color=0x0b3d91
            ))
                
    @commands.command(name="ai", description="chat with ai")
    async def ai(self, ctx, *, prompt):
        try:
            if not os.getenv("secret_key"):
                embed = discord.Embed(
                    title="configuration error",
                    description="api key isnt configured yet (it was iak's job btw)",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            userid = ctx.author.id
    
            if userid not in self.memory:
                self.memory[userid] = []
    
            self.memory[userid].append({"role": "user", "content": prompt})
            self.memory[userid] = self.memory[userid][-45:]
    
            messages = [
                {
                    "role": "system",
                    "content": "you are a helpful and friendly assistant"
                }
            ] + self.memory[userid]
            
            async with ctx.typing():
                response = await asyncio.to_thread(
                    lambda: requests.post(
                        "https://text.pollinations.ai/openai",
                        headers={
                            "content-type": "application/json",
                            "authorization": f"Bearer {os.getenv('secret_key')}"
                        },
                        json={
                            "model": "openai-fast",
                            "messages": messages,
                            "temperature": 0.7
                        },
                        timeout=30
                    )
                )
            
            if response.status_code != 200:
                embed = discord.Embed(
                    title="ai error",
                    description="api is not responding",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
            
            data = response.json()
    
            if "choices" not in data or not data["choices"]:
                embed = discord.Embed(
                    title="ai error",
                    description="api did not return an valid json",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return
    
            reply = data["choices"][0]["message"]["content"]
            self.memory[userid].append({"role": "assistant", "content": reply})
            self.memory[userid] = self.memory[userid][-45:]
    
            embed = discord.Embed(
                title="ai response",
                description=f"\u200b{reply}",
                color=0x0b3d91
            )
            embed.set_footer(text=f"requested by {ctx.author.name}")
    
            await ctx.send(embed=embed)
    
        except requests.exceptions.Timeout:
            embed = discord.Embed(
                title="timeout",
                description="ai took too long to respond, try again later",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
            print("ai timeout error")
    
        except Exception as e:
            print("ai error:", e)
            embed = discord.Embed(
                title="unexpected error",
                description="something went wrong while processing your request",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)



    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return
    
            if not message.reference:
                return
    
            replied = message.reference.resolved
            if not replied:
                return
    
            if replied.author.id != self.bot.user.id:
                return
            
            if not replied.embeds:
                return
            
            embed = replied.embeds[0]
            if not embed.description or not embed.description.startswith("\u200b"):
                return
    
            ctx = await self.bot.get_context(message)
            if ctx.valid:
                return
    
            if not os.getenv("secret_key"):
                embed = discord.Embed(
                    title="configuration error",
                    description="api key isnt configured yet (it was iak's job btw)",
                    color=0x0b3d91
                )
                await message.channel.send(embed=embed)
                return
    
            userid = message.author.id
    
            if userid not in self.memory:
                self.memory[userid] = []
    
            self.memory[userid].append({
                "role": "user",
                "content": message.content
            })
            self.memory[userid] = self.memory[userid][-45:]
    
            messages = [
                {
                    "role": "system",
                    "content": "you are a helpful and friendly assistant"
                }
            ] + self.memory[userid]
            
            async with message.channel.typing():
                response = await asyncio.to_thread(
                    lambda: requests.post(
                        "https://text.pollinations.ai/openai",
                        headers={
                            "content-type": "application/json",
                            "authorization": f"Bearer {os.getenv('secret_key')}"
                        },
                        json={
                            "model": "openai-fast",
                            "messages": messages,
                            "temperature": 0.7
                        },
                        timeout=30
                    )
                )
            
            if response.status_code != 200:
                embed = discord.Embed(
                    title="ai error",
                    description="api is not responding",
                    color=0x0b3d91
                )
                await message.channel.send(embed=embed)
                return
            
            data = response.json()
    
            if "choices" not in data or not data["choices"]:
                embed = discord.Embed(
                    title="ai error",
                    description="api did not return an valid json",
                    color=0x0b3d91
                )
                await message.channel.send(embed=embed)
                return
    
            reply = data["choices"][0]["message"]["content"]
            self.memory[userid].append({
                "role": "assistant",
                "content": reply
            })
            self.memory[userid] = self.memory[userid][-45:]
    
            embed = discord.Embed(
                title="ai response",
                description=f"\u200b{reply}",
                color=0x0b3d91
            )
            embed.set_footer(text=f"requested by {message.author.name}")
    
            await message.reply(embed=embed)
    
        except requests.exceptions.Timeout:
            embed = discord.Embed(
                title="timeout",
                description="ai took too long to respond, try again later",
                color=0x0b3d91
            )
            await message.channel.send(embed=embed)
            print("ai reply timeout")
    
        except Exception as e:
            print("ai reply error:", e)
            embed = discord.Embed(
                title="unexpected error",
                description="something went wrong while processing your request",
                color=0x0b3d91
            )
            await message.channel.send(embed=embed)
            
            await self.bot.process_commands(message)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot or not message.guild:
                return

            data = loadleaderboard()
            userid = str(message.author.id)
            data["messages"][userid] = data["messages"].get(userid, 0) + 1
            saveleaderboard(data)

        except Exception as e:
            print("leaderboard tracking error:", e)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            for guild in self.bot.guilds:
                self.invites[guild.id] = await guild.invites()
        except Exception as e:
            print("invite cache error:", e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            oldinvites = self.invites.get(member.guild.id)
            if oldinvites is None:
                self.invites[member.guild.id] = await member.guild.invites()
                return

            newinvites = await member.guild.invites()
            self.invites[member.guild.id] = newinvites

            for new in newinvites:
                for old in oldinvites:
                    if new.code == old.code and new.uses > old.uses:
                        data = loadleaderboard()
                        inviter = str(new.inviter.id)
                        data["invites"][inviter] = data["invites"].get(inviter, 0) + 1
                        saveleaderboard(data)
                        return

        except Exception as e:
            print("invite tracking error:", e)

    @commands.command(name="leaderboard", aliases=["ldboard", "ldb"], description="show leaderboard stats")
    async def leaderboard(self, ctx, mode=None):
        try:
            if not mode:
                embed = discord.Embed(
                    title="missing option",
                    description="use `leaderboard message` or `leaderboard invite`",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            mode = mode.lower()
            data = loadleaderboard()

            if mode not in ["message", "invite"]:
                embed = discord.Embed(
                    title="invalid option",
                    description="valid options are `message` or `invite`",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            stats = data["messages"] if mode == "message" else data["invites"]

            if not stats:
                embed = discord.Embed(
                    title="no data",
                    description=f"no {mode} data has been recorded yet",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            sortedstats = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]

            lines = []
            index = 1
            for userid, value in sortedstats:
                member = ctx.guild.get_member(int(userid))
                name = member.mention if member else f"<@{userid}>"
                lines.append(f"#{index} {name} — {value}")
                index += 1

            embed = discord.Embed(
                title=f"{mode} leaderboard",
                description="\n".join(lines),
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print("leaderboard command error:", e)
            embed = discord.Embed(
                title="error",
                description="failed to fetch leaderboard data",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

    @commands.command(name="messages", description="check message count")
    async def messages(self, ctx, user: discord.Member = None):
        try:
            target = user or ctx.author
            data = loadleaderboard()

            userid = str(target.id)
            count = data["messages"].get(userid)

            if count is None:
                embed = discord.Embed(
                    title="no data",
                    description=f"{target.mention} has no recorded messages yet",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title="message count",
                description=f"{target.mention} has sent **{count}** messages",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except commands.BadArgument:
            embed = discord.Embed(
                title="invalid user",
                description="please mention a valid user",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print("messages command error:", e)
            embed = discord.Embed(
                title="error",
                description="failed to fetch message data",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

    @commands.command(name="invites", description="check invite count")
    async def invites(self, ctx, user: discord.Member = None):
        try:
            target = user or ctx.author
            data = loadleaderboard()

            userid = str(target.id)
            count = data["invites"].get(userid)

            if count is None:
                embed = discord.Embed(
                    title="no data",
                    description=f"{target.mention} has no recorded invites yet",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title="invite count",
                description=f"{target.mention} has invited **{count}** members",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except commands.BadArgument:
            embed = discord.Embed(
                title="invalid user",
                description="please mention a valid user",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print("invites command error:", e)
            embed = discord.Embed(
                title="error",
                description="failed to fetch invite data",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot or not message.guild:
                return

            data = loadaliases()
            guildid = str(message.guild.id)

            if guildid not in data:
                return

            content = message.content.strip()
            if not content:
                return

            ctx = await self.bot.get_context(message)
            if ctx.valid:
                return

            parts = content.split()
            alias = parts[0].lstrip(ctx.prefix or "")
            if alias not in data[guildid]:
                return

            real = data[guildid][alias]
            newcontent = (ctx.prefix or "") + real
            if len(parts) > 1:
                newcontent += " " + " ".join(parts[1:])

            fake = message
            fake.content = newcontent

            newctx = await self.bot.get_context(fake)
            if newctx.command:
                await self.bot.invoke(newctx)

        except Exception as e:
            print("alias resolve error:", e)

    @commands.command(name="alias", description="manage command aliases")
    @commands.has_permissions(administrator=True)
    async def alias(self, ctx, mode=None, command=None, *aliases):
        try:
            data = loadaliases()
            guildid = str(ctx.guild.id)
            data.setdefault(guildid, {})

            if not mode:
                embed = discord.Embed(
                    title="missing mode",
                    description="use `add`, `remove`, or `list`",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            mode = mode.lower()

            if mode == "list":
                if not data[guildid]:
                    embed = discord.Embed(
                        title="no aliases",
                        description="no aliases configured for this server",
                        color=0x0b3d91
                    )
                    await ctx.send(embed=embed)
                    return

                lines = []
                grouped = {}
                for a, c in data[guildid].items():
                    grouped.setdefault(c, []).append(a)

                for c, als in grouped.items():
                    lines.append(f"`{c}` → {', '.join(als)}")

                embed = discord.Embed(
                    title="aliases",
                    description="\n".join(lines),
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            if mode not in ["add", "remove"]:
                embed = discord.Embed(
                    title="invalid mode",
                    description="use `add`, `remove`, or `list`",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            if not command:
                embed = discord.Embed(
                    title="missing command",
                    description="specify a command name",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            realcmd = self.bot.get_command(command)
            if not realcmd:
                cmds = sorted([c.name for c in self.bot.commands])
                embed = discord.Embed(
                    title="invalid command",
                    description="available commands:\n" + ", ".join(cmds),
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            if not aliases:
                embed = discord.Embed(
                    title="missing aliases",
                    description="provide at least one alias",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            added = []
            removed = []
            skipped = []

            if mode == "add":
                for a in aliases:
                    if a in data[guildid]:
                        skipped.append(a)
                    else:
                        data[guildid][a] = realcmd.name
                        added.append(a)

                savealiases(data)

                embed = discord.Embed(
                    title="aliases added",
                    description=(
                        (f"added: {', '.join(added)}\n" if added else "") +
                        (f"skipped (already exists): {', '.join(skipped)}" if skipped else "")
                    ),
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            if mode == "remove":
                for a in aliases:
                    if data[guildid].get(a) == realcmd.name:
                        del data[guildid][a]
                        removed.append(a)
                    else:
                        skipped.append(a)

                savealiases(data)

                embed = discord.Embed(
                    title="aliases removed",
                    description=(
                        (f"removed: {', '.join(removed)}\n" if removed else "") +
                        (f"not found: {', '.join(skipped)}" if skipped else "")
                    ),
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)

        except Exception as e:
            print("alias command error:", e)
            embed = discord.Embed(
                title="error",
                description="failed to manage aliases",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

    @commands.command(name="man", description="show command manual") # inspired from linux command;)
    async def man(self, ctx, commandname=None):
        try:
            if not commandname:
                embed = discord.Embed(
                    title="missing command",
                    description="usage: man {command}",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            cmd = self.bot.get_command(commandname)

            if not cmd:
                names = sorted([c.name for c in self.bot.commands])
                embed = discord.Embed(
                    title="unknown command",
                    description="available commands:\n" + ", ".join(names),
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            aliases = ", ".join(cmd.aliases) if cmd.aliases else "none"
            params = cmd.signature if cmd.signature else "none"
            desc = cmd.description if cmd.description else "no description provided"

            embed = discord.Embed(
                title=f"manual: {cmd.name}",
                description=desc,
                color=0x0b3d91
            )

            embed.add_field(name="usage", value=f"`{ctx.prefix}{cmd.name} {params}`", inline=False)
            embed.add_field(name="aliases", value=aliases, inline=False)

            if cmd.cog:
                embed.set_footer(text=f"module: {cmd.cog.qualified_name}")

            await ctx.send(embed=embed)

        except Exception as e:
            print("man command error:", e)
            embed = discord.Embed(
                title="error",
                description="failed to fetch command manual",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

    @commands.command(name="extension", description="manage extensions")
    @commands.has_permissions(administrator=True)
    async def extension(self, ctx, action=None, name=None, option=None):
        try:
            data = loadjson("extensions.json", {})
            installed = loadjson("installed_extensions.json", {})
            guildid = str(ctx.guild.id)
            installed.setdefault(guildid, {})
            installed.setdefault("autoupdate", {})
            installed["autoupdate"].setdefault(guildid, False)

            if action not in ["install", "update", "downgrade", "uninstall", "autoupdate"]:
                await ctx.send(embed=discord.Embed(
                    title="invalid action",
                    description="use install, update, downgrade, uninstall or autoupdate",
                    color=0x0b3d91
                ))
                return

            if action == "autoupdate":
                if name not in ["enable", "disable"]:
                    await ctx.send(embed=discord.Embed(
                        title="invalid option",
                        description="use extension autoupdate enable or extension autoupdate disable",
                        color=0x0b3d91
                    ))
                    return

                installed["autoupdate"][guildid] = name == "enable"
                savejson("installed_extensions.json", installed)

                await ctx.send(embed=discord.Embed(
                    title="autoupdate",
                    description=f"autoupdate {name}d",
                    color=0x0b3d91
                ))
                return
                savejson("installed_extensions.json", installed)

                await ctx.send(embed=discord.Embed(
                    title="autoupdate",
                    description=f"autoupdate {option}d",
                    color=0x0b3d91
                ))
                return

            if not name:
                await ctx.send(embed=discord.Embed(
                    title="missing extension",
                    description="specify extension id",
                    color=0x0b3d91
                ))
                return

            if action == "update" and name == "*":
                updated = []
                for extid in installed[guildid]:
                    latest = sorted(data[extid]["versions"].keys())[-1]
                    if installed[guildid][extid] != latest:
                        installed[guildid][extid] = latest
                        updated.append(extid)

                savejson("installed_extensions.json", installed)

                await ctx.send(embed=discord.Embed(
                    title="update complete",
                    description="updated: " + ", ".join(updated) if updated else "everything is already up to date",
                    color=0x0b3d91
                ))
                return

            wantedversion = None
            if "==" in name:
                name, wantedversion = name.split("==", 1)

            if name not in data:
                await ctx.send(embed=discord.Embed(
                    title="unknown extension",
                    description="extension id not found",
                    color=0x0b3d91
                ))
                return

            ext = data[name]
            versions = sorted(ext["versions"].keys())

            if action == "update":
                if name not in installed[guildid]:
                    await ctx.send(embed=discord.Embed(
                        title="not installed",
                        description="extension is not installed",
                        color=0x0b3d91
                    ))
                    return

                current = installed[guildid][name]
                latest = versions[-1]

                if current == latest:
                    await ctx.send(embed=discord.Embed(
                        title="no update",
                        description="extension is already up to date",
                        color=0x0b3d91
                    ))
                    return

                wantedversion = latest

            if action == "downgrade":
                if name not in installed[guildid]:
                    await ctx.send(embed=discord.Embed(
                        title="not installed",
                        description="extension is not installed",
                        color=0x0b3d91
                    ))
                    return

                current = installed[guildid][name]
                older = [v for v in versions if v < current]

                if not older:
                    await ctx.send(embed=discord.Embed(
                        title="no older version",
                        description="no older version available to downgrade",
                        color=0x0b3d91
                    ))
                    return

                wantedversion = wantedversion or older[-1]

                if wantedversion not in older:
                    await ctx.send(embed=discord.Embed(
                        title="invalid version",
                        description="available versions: " + ", ".join(older),
                        color=0x0b3d91
                    ))
                    return

            if action == "install" and wantedversion and wantedversion not in versions:
                await ctx.send(embed=discord.Embed(
                    title="invalid version",
                    description="available versions: " + ", ".join(versions),
                    color=0x0b3d91
                ))
                return

            if action == "uninstall":
                if name not in installed[guildid]:
                    await ctx.send(embed=discord.Embed(
                        title="not installed",
                        description="extension is not installed",
                        color=0x0b3d91
                    ))
                    return

                installed[guildid].pop(name)
                savejson("installed_extensions.json", installed)

                await ctx.send(embed=discord.Embed(
                    title="uninstalled",
                    description=f"{ext['title']} removed",
                    color=0x0b3d91
                ))
                return

            target = wantedversion or versions[-1]
            filepath = os.path.join("extensions", ext["versions"][target])

            msg = await ctx.send(embed=discord.Embed(
                title="safety check",
                description="running tests to ensure no breakage",
                color=0x0b3d91
            ))

            await asyncio.sleep(0.8)

            ok, err = testextension(filepath)
            if not ok:
                await msg.edit(embed=extensionfail(name, err))
                return

            spec = importlib.util.spec_from_file_location(f"{name}_{target}", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            await asyncio.sleep(0.4)

            if hasattr(module, "setup"):
                await module.setup(self.bot)

            installed[guildid][name] = target
            savejson("installed_extensions.json", installed)

            added = [
                c.name for c in self.bot.commands
                if c.cog and c.cog.__module__ == module.__name__
            ] or ["no commands"]

            await msg.edit(embed=discord.Embed(
                title="installing",
                description="installing " + ", ".join(added) + "...",
                color=0x0b3d91
            ))

            await asyncio.sleep(2.5)

            await msg.edit(embed=discord.Embed(
                title="success",
                description=f"{ext['title']} {target} installed successfully",
                color=0x0b3d91
            ))

        except Exception:
            print("extension command error:\n", traceback.format_exc())
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to manage extension",
                color=0x0b3d91
            ))

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            installed = loadjson("installed_extensions.json", {})
            extensions = loadjson("extensions.json", {})
            guildid = str(ctx.guild.id)

            for extid, version in installed.get(guildid, {}).items():
                if ctx.command.cog and ctx.command.cog.__module__.startswith(extid):
                    latest = sorted(extensions[extid]["versions"].keys())[-1]
                    if latest != version:
                        await ctx.send(
                            f"update available for **{extensions[extid]['title']}** → `{latest}`"
                        )
        except Exception as e:
            print("extension update notify error:", e)

    @commands.command(name="extensions", description="manage installed extensions")
    @commands.has_permissions(administrator=True)
    async def extensions(self, ctx, mode=None):
        try:
            extensionsdata = loadjson("extensions.json", {})
            installeddata = loadjson("installed_extensions.json", {})
            guildid = str(ctx.guild.id)
            installed = installeddata.get(guildid, {})

            if mode not in ["list", "library"]:
                await ctx.send(embed=discord.Embed(
                    title="invalid option",
                    description="use extensions list or extensions library",
                    color=0x0b3d91
                ))
                return

            if mode == "list":
                if not installed:
                    await ctx.send(embed=discord.Embed(
                        title="no extensions installed",
                        description="this server has no installed extensions",
                        color=0x0b3d91
                    ))
                    return

                embed = discord.Embed(title="installed extensions", color=0x0b3d91)

                for extid, version in installed.items():
                    ext = extensionsdata.get(extid)
                    if not ext:
                        continue

                    commandsadded = ext.get("commands", [])

                    embed.add_field(
                        name=f"{ext['title']} ({extid})",
                        value=(
                            f"creator: {ext['creator']}\n"
                            f"version: {version}\n"
                            f"commands: {', '.join(commandsadded) if commandsadded else 'no commands found'}"
                        ),
                        inline=False
                    )

                await ctx.send(embed=embed)
                return

            if mode == "library":
                if not extensionsdata:
                    await ctx.send(embed=discord.Embed(
                        title="no extensions",
                        description="no extensions available",
                        color=0x0b3d91
                    ))
                    return

                keys = list(extensionsdata.keys())
                index = 0

                def makeembed(i):
                    extid = keys[i]
                    ext = extensionsdata[extid]
                    versions = list(ext["versions"].keys())
                    latest = versions[-1]

                    commandsadded = ext.get("commands", [])

                    embed = discord.Embed(
                        title=extid,
                        description=ext.get("description", "no description"),
                        color=0x0b3d91
                    )

                    embed.set_thumbnail(url=ext["image"])

                    embed.add_field(name="title", value=ext["title"], inline=False)
                    embed.add_field(name="creator", value=ext["creator"], inline=False)

                    versiontext = []
                    for v in reversed(versions):
                        versiontext.append(f"{v} (latest)" if v == latest else v)

                    embed.add_field(
                        name="versions",
                        value=", ".join(versiontext),
                        inline=False
                    )

                    embed.add_field(
                        name="commands",
                        value=", ".join(commandsadded) if commandsadded else "no commands found",
                        inline=False
                    )

                    usage = (
                        f"use `extension install {extid}`\n"
                        "or\n"
                        f"use `extension install {extid}=={latest}`"
                    )

                    embed.add_field(name="usage", value=usage, inline=False)

                    if extid in installed:
                        embed.add_field(name="status", value="installed", inline=False)

                    embed.set_footer(text=f"{i + 1}/{len(keys)}")

                    return embed

                class navview(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=120)

                    async def interaction_check(self, interaction):
                        return interaction.user.id == ctx.author.id

                    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary)
                    async def back(self, interaction, button):
                        nonlocal index
                        if index > 0:
                            index -= 1

                        self.children[0].disabled = index == 0
                        self.children[1].disabled = index == len(keys) - 1

                        await interaction.response.edit_message(
                            embed=makeembed(index),
                            view=self
                        )

                    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary)
                    async def next(self, interaction, button):
                        nonlocal index
                        if index < len(keys) - 1:
                            index += 1

                        self.children[0].disabled = index == 0
                        self.children[1].disabled = index == len(keys) - 1

                        await interaction.response.edit_message(
                            embed=makeembed(index),
                            view=self
                        )

                view = navview()
                view.children[0].disabled = True
                view.children[1].disabled = len(keys) == 1

                await ctx.send(embed=makeembed(index), view=view)

        except Exception as e:
            print("extensions command error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to fetch extensions",
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
            headers = {
                "user-agent": "grave/1.0 (discord bot)"
            }

            search = requests.get(
                "https://en.wikipedia.org/w/api.php",
                headers=headers,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json"
                },
                timeout=10
            )

            if search.status_code != 200:
                print("wiki search status:", search.status_code)
                embed = discord.Embed(
                    title="wiki error",
                    description="failed to contact wikipedia",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            results = search.json().get("query", {}).get("search", [])
            if not results:
                embed = discord.Embed(
                    title="no results",
                    description="no wikipedia page found for that query",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            title = results[0]["title"]

            summary = requests.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + title.replace(" ", "%20"),
                headers=headers,
                timeout=10
            )

            if summary.status_code != 200:
                print("wiki summary status:", summary.status_code)
                embed = discord.Embed(
                    title="wiki error",
                    description="failed to fetch wikipedia summary",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            data = summary.json()

            text = data.get("extract")
            link = data.get("content_urls", {}).get("desktop", {}).get("page")

            if not text:
                embed = discord.Embed(
                    title="no summary",
                    description="wikipedia page has no readable summary",
                    color=0x0b3d91
                )
                await ctx.send(embed=embed)
                return

            if len(text) > 4096:
                embed = discord.Embed(
                    title=data.get("title", title),
                    description=f"summary is too long to display\n[read full article]({link})",
                    color=0x0b3d91
                )
            else:
                embed = discord.Embed(
                    title=data.get("title", title),
                    description=text,
                    color=0x0b3d91
                )

            if "thumbnail" in data and "source" in data["thumbnail"]:
                embed.set_thumbnail(url=data["thumbnail"]["source"])

            await ctx.send(embed=embed)

        except Exception as e:
            print("wiki error:", e)
            embed = discord.Embed(
                title="error",
                description="failed to fetch wikipedia information",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)

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
            perms = user.guild_permissions # type: ignore
            allowed = [name.replace("_", " ") for name, value in perms if value]
            roles = [role.name for role in user.roles if role.name != "@everyone"] # type: ignore
    
            embed = discord.Embed(
                title="user info",
                color=0x0b3d91
            )
    
            embed.set_thumbnail(url=user.display_avatar.url) # type: ignore
    
            embed.add_field(
                name="display name",
                value=user.display_name, # type: ignore
                inline=True
            )
    
            embed.add_field(
                name="username",
                value=f"{user.name}#{user.discriminator}", # type: ignore
                inline=True
            )
    
            embed.add_field(
                name="user id",
                value=user.id, # type: ignore
                inline=False
            )
    
            embed.add_field(
                name="joined server",
                value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), # type: ignore
                inline=True
            )
    
            embed.add_field(
                name="joined discord",
                value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), # type: ignore
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
                name=user.name, # type: ignore
                icon_url=user.display_avatar.url # type: ignore
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
            embed.set_image(url=user.display_avatar.url) # type: ignore
            embed.set_author(name=user.name, icon_url=user.display_avatar.url) # type: ignore
            await ctx.send(embed=embed)
        except Exception as e:
            print("avatar error:", e)
            await ctx.send("failed to fetch avatar")
            
    @commands.command(name="meme", description="send a random meme")
    async def meme(self, ctx):
        try:
            data = await asyncio.to_thread(lambda: requests.get("https://meme-api.com/gimme", timeout=10).json())
            embed = discord.Embed(
                title="meme",
                color=0x0b3d91
            )
            embed.set_image(url=data["url"])
            await ctx.send(embed=embed)
        except Exception as e:
            print("meme error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to fetch meme",
                color=0x0b3d91
            ))


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
                    },
                    timeout=10
                ).json()
            )
            embed = discord.Embed(
                title="translation",
                description=data[0][0][0],
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("translate error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to translate text",
                color=0x0b3d91
            ))


    @commands.command(name="dice", description="roll a dice")
    async def dice(self, ctx):
        try:
            embed = discord.Embed(
                title="dice roll",
                description=f"🎲 rolled: {random.randint(1, 6)}",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("dice error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to roll dice",
                color=0x0b3d91
            ))


    @commands.command(name="joke", description="send a random joke")
    async def joke(self, ctx):
        try:
            data = await asyncio.to_thread(lambda: requests.get(
                "https://official-joke-api.appspot.com/random_joke",
                timeout=10
            ).json())
            embed = discord.Embed(
                title="joke",
                description=f"{data['setup']}\n\n{data['punchline']}",
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("joke error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to fetch joke",
                color=0x0b3d91
            ))


    @commands.command(name="fact", description="get a random fact")
    async def fact(self, ctx):
        try:
            data = await asyncio.to_thread(lambda: requests.get(
                "https://api.popcat.xyz/v2/fact",
                timeout=10
            ).json())
            embed = discord.Embed(
                title="fact",
                description=data["message"]["fact"],
                color=0x0b3d91
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("fact error:", e)
            await ctx.send(embed=discord.Embed(
                title="error",
                description="failed to fetch fact",
                color=0x0b3d91
            ))

    @commands.command(name="roast", description="roast a user")
    async def roast(self, ctx, user: commands.MemberConverter):
        try:
            if user.id == 1238444724386533417:
                await ctx.send(embed=discord.Embed(
                    description=f"fuck you bitch {ctx.author.mention}",
                    color=0x0b3d91
                ))
                return

            data = await asyncio.to_thread(
                lambda: requests.get(
                    "https://evilinsult.com/generate_insult.php",
                    params={
                        "lang": "en",
                        "type": "json"
                    },
                    timeout=10
                ).json()
            )

            await ctx.send(embed=discord.Embed(
                description=f"{user.mention} {data.get('insult', 'no insult found')}",
                color=0x0b3d91
            ))

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
# TO BLAZE: yes i, iamiak did this i didnt wanna ruin your progress if i did anything wrong so i just commented every line.
# TO IAK: thanks buddy
    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     try:
    #         if isinstance(error, commands.MissingRequiredArgument):
    #             embed = discord.Embed(
    #                 title="missing value",
    #                 description=f"required value: `{error.param.name}`",
    #                 color=0x0b3d91
    #             )
    #             await ctx.send(embed=embed)
    #             return
    
    #         if isinstance(error, commands.BadArgument):
    #             received = None
    #             if ctx.message.content:
    #                 parts = ctx.message.content.split()
    #                 if len(parts) > 1:
    #                     received = " ".join(parts[1:])
    
    #             embed = discord.Embed(
    #                 title="invalid value",
    #                 description=(
    #                     f"required value: `{ctx.command.clean_params.keys()}`\n"
    #                     f"received value: `{received}`"
    #                     if received else
    #                     f"required value: `{ctx.command.clean_params.keys()}`"
    #                 ),
    #                 color=0x0b3d91
    #             )
    #             await ctx.send(embed=embed)
    #             return
    
    #         if isinstance(error, commands.CommandNotFound):
    #             return
    
    #         embed = discord.Embed(
    #             title="error",
    #             description="an unexpected error occurred",
    #             color=0x0b3d91
    #         )
    #         await ctx.send(embed=embed)
    
    #         print("unhandled command error:", error)
    #     except Exception as e:
    #         print("error handler failure:", e)
            
async def setup(bot):
    cog = blaze(bot)
    await bot.add_cog(cog)

    cmds = [command.name for command in cog.get_commands()]
    print(f"Blaze added {len(cmds)} commands: {', '.join(cmds)}") # NOTE: Specially made this part for iak :3
#    print("blaze's global error handler active")
# NOTE FOR IAK: you have probably read the entire code by now, im so sorry for whatever i messed up😭🙏
