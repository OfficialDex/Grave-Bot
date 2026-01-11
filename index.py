import asyncio
import discord
from discord.ext import commands
from pytimeparse.timeparse import timeparse
from easy_pil import *
from dotenv import load_dotenv
from detoxify import Detoxify
from datetime import datetime
import requests
import random
import os
import time
import threading
import json

# NOTE: This is my part file, DO NOT MESS with it
async def blaze_part():
    await bot.load_extension("blaze")
    
def get_server_info(serverId: str):
    if serverId not in servers_temp:
        add_server(serverId)
    return servers_temp[serverId]

def add_server(serverId: str):
    servers_temp[serverId] = {
        "prefix": ",",
        "welcomeMessage": {
            "channelId": "",
            "lastVideo": "",
            "image": {
                "enabled": False,
                "background": "",
                "description": ""
            },
            "embed": {
                "enabled": False,
                "color": "",
                "title": "Welcome to the server!",
                "description": "Welcome {user} to {server}!"
            }
        },
        "youtubeMessage": {
            "channelId": "",
            "enabled": False,
            "ytChannelId": "",
            "lastvid": "",
            "embed": {
                "color": "",
                "title": "",
                "description": ""
            }
        },
        "moderation": {
            "linksAllowed": True,
            "swearingAllowed": True,
            "disabledCmdsChannels": []
        },
        "voiceMaster": {
            "enabled": False,
            "channelId": "",
            "channels": {}
        },
        "logs": {
            "channelId": "",
            "moderation": False
        },
        "robloxVerification": {
            "enabled": True,
            "roleId": "",
            "data": {}
        },
        "boosterMessage": {
            "enabled": False,
            "title": "",
            "description": "",
            "channelId": ""
        },
        "gwInfo": {
            "channelId": ""
        },
        "warns": {},
        "snipes": {},
        "levels": {
            "enabled": False,
            "users": {}
        }
    }

def get_vm_owned_channel(ctx):
    server_info = get_server_info(ctx.guild.id)
    vm = server_info["voiceMaster"]
    channel_id = vm["channels"].get(ctx.author.id)
    if not channel_id:
        return None
    return ctx.guild.get_channel(channel_id)

def get_prefix(bot, msg):
        if not msg.guild:
            return ","
        
        return get_server_info(msg.guild.id)["prefix"]

class TrackedDict(dict):
    def __init__(self, *args, file_name="serverdata.json", **kwargs):
        super().__init__(*args, **kwargs)
        self.file_name = file_name
        self._lock = threading.Lock()

    def _save(self):
        with self._lock:
            with open(self.file_name, "w", encoding="utf-8") as f:
                json.dump(self, f, indent=4)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._save()

    def clear(self):
        super().clear()
        self._save()


load_dotenv()

model = None
servers_temp = TrackedDict()
bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all(), help_command=None)
token = os.getenv("TOKEN")
model = Detoxify("original")
bot.setup_hook = blaze_part # NOTE: DO NOT edit this part

def resolve_color(value: str) -> discord.Color:
    if not value:
        return discord.Color.blue()

    value = value.lower().strip()

    if value == "random":
        return discord.Color.random()

    if value.startswith("#"):
        value = value[1:]

    if len(value) == 6:
        try:
            return discord.Color(int(value, 16))
        except ValueError:
            pass

    NAMED_COLORS = {
        "red": discord.Color.red(),
        "blue": discord.Color.blue(), 
        "green": discord.Color.green(), 
        "purple": discord.Color.purple(), 
        "gold": discord.Color.gold(),
        "orange": discord.Color.orange(),
        "teal": discord.Color.teal(),
        "pink": discord.Color.magenta(),
        "dark_red": discord.Color.dark_red(),
        "dark_blue": discord.Color.dark_blue(),
        "dark_purple": discord.Color.dark_purple(),
    }

    return NAMED_COLORS.get(value, discord.Color.blue())

async def log_moderation(user, interaction, serverId, extraData):
    serverInfo = get_server_info(serverId)
    moderation = serverInfo

    if moderation["logs"]["moderation"]:
        channel = bot.get_channel(moderation["logs"]["channelId"])

        if channel:
            embed = discord.Embed(
                title="Moderation Logging.",
                description=f"At **{datetime.now()}**, User: **{user}** **{interaction}**. **{extraData}**",
                color=discord.Colour.blue()
            )

            await channel.send(embed=embed) # type: ignore Must be a text channel.

@bot.event
async def on_ready():
    print("-- Grave Is Ready --")
    print(f"Username Check: {bot.user}")

@bot.event
async def on_message(message):
    if message.guild is None:
        return

    serverInfo = get_server_info(message.guild.id)
    moderation = serverInfo["moderation"]

    if not moderation["linksAllowed"]:
        if message.content.startswith("https://") or message.content.startswith("http://"):
            await log_moderation(message.author.id, "Shared a link", message.guild.id, f"Link was: {message.content}")
            await message.delete()
    
    scores = model.predict(message.content) # type: ignore it will become a model after startup

    if not moderation["swearingAllowed"]:
        if scores["toxicity"] > 0.5:
            await log_moderation(message.author.id, "Sweared", message.guild.id, f"Message was: {message.content}")
            await message.delete()
    
    if message.type == discord.MessageType.premium_guild_subscription:
        booster_person = message.author.name

        if serverInfo["boosterMessage"]["enabled"]:
            embed = discord.Embed(
                title=serverInfo["boosterMessage"]["title"],
                description=serverInfo["boosterMessage"]["description"].replace("{user}", f"<#{booster_person.id}>"),
                color=discord.Color.purple()
            )

            await bot.get_channel(serverInfo["boosterMessage"]["channelId"]).send(embed=embed) # type: ignore its required to be a textchannel
    
    if serverInfo["levels"]["enabled"]:
        if not message.author.id in serverInfo["levels"]:
            serverInfo["levels"][message.author.id] = {
                "level": 1,
                "xp": 0
            }
        
        if message.author.id == bot.id: # type: ignore
            return
        
        serverInfo["levels"][message.author.id]["xp"] += 2

        if serverInfo["levels"][message.author.id]["level"] * 100 >= serverInfo["levels"][message.author.id]["xp"]:
            embed = discord.Embed(
                title="Level Up!",
                description=f'You leveled up to level {serverInfo["levels"][message.author.id]["level"]}',
                color=discord.Colour.blue()
            )

            serverInfo["levels"][message.author.id]["level"] += 1
            serverInfo["levels"][message.author.id]["xp"] = 0

            await message.author.send(embed=embed)

    if not message.channel.id in moderation["disabledCmdsChannels"]:
        await bot.process_commands(message)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    customId = interaction.data.get("custom_id") # type: ignore it does work!!
    server_info = get_server_info(interaction.guild.id) # type: ignore

    if customId == "RBX_verify_start":

        if server_info["robloxVerification"]["enabled"]:
            modal = discord.ui.Modal(
                title="Verify Your Roblox Account"
            )
            text_input = discord.ui.TextInput(
                label="Roblox Username"
            )

            async def verifyRBX(interaction: discord.Interaction):
                request = requests.post("https://users.roblox.com/v1/usernames/users", json={
                    "usernames": [text_input.value],
                    "excludeBannedUsers": True
                }).json()
                embed = discord.Embed(
                    title="Is this you?",
                    color=discord.Color.blue()
                )

                embed.add_field(name="ID", value=request["data"][0]["id"])
                embed.add_field(name="Name", value=request["data"][0]["name"])
                embed.add_field(name="Display Name", value=request["data"][0]["displayName"])
                avatarId = str(request["data"][0]["id"])
                avatarReq = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={avatarId}&size=150x150&format=Png&isCircular=true").json()["data"][0]["imageUrl"]

                button = discord.ui.Button(
                    label="Yes",
                    style=discord.ButtonStyle.green,
                    custom_id=f"RBX_yes_{avatarId}"
                )

                button2 = discord.ui.Button(
                    label="No",
                    style=discord.ButtonStyle.red,
                    custom_id="RBX_no"
                )

                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)

                embed.set_thumbnail(url=avatarReq)

                await interaction.response.send_message(embed=embed, ephemeral=True, view=view)

            modal.on_submit = verifyRBX
            modal.add_item(text_input)

            await interaction.response.send_modal(modal)
    elif customId == "RBX_no":
        await interaction.response.send_message(f"Please go to your account and get the username again (The one which starts with @)", ephemeral=True)
    elif customId.startswith("RBX_yes"): # type: ignore
        list_of_words = requests.get("https://www.mit.edu/~ecprice/wordlist.10000").text
        final_string = ""
        button2 = discord.ui.Button(
            label="Change String",
            style=discord.ButtonStyle.blurple,
            custom_id="RBX_yes"
        )
        button = discord.ui.Button(
            label="I'm done",
            style=discord.ButtonStyle.green,
            custom_id="RBX_done"
        )

        view = discord.ui.View()
        view.add_item(button)
        view.add_item(button2)

        for i in range(1, random.randint(1, 10)):
            final_string = f"{final_string} {random.choice(list_of_words.splitlines())}"
        
        server_info["robloxVerification"]["data"][interaction.user.id] = {
            "user_id": interaction.user.id,
            "rbx_id": customId.split("_")[2], # type: ignore
            "str": final_string
        }

        embed = discord.Embed(
            title="Please prove that this is your account.",
            description="Please prove that this account is your by changing the description of your account to:"
        )

        embed.add_field(name="Change your description to:", value=final_string)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    elif customId == "RBX_done":
        userData = server_info["robloxVerification"]["data"][interaction.user.id]
        if userData:
            userInfo = requests.get(f"https://users.roblox.com/v1/users/{userData['rbx_id']}").json()

            if userInfo["description"] == userData["str"]:
                embed = discord.Embed(
                    title="Verification Complete!",
                    description="You will be awarded your role in 5 seconds. Thank you for verifying!",
                    color=discord.Color.green()
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)

                time.sleep(5)
                
                await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id=server_info["robloxVerification"]["roleId"])) # type: ignore HOPE.
            else:
                embed = discord.Embed(
                    title="Verification Failed",
                    description="We could not verify that this was your account. Please try again.",
                    color=discord.Color.red()
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"<:Error:1453258237423124520> There was an error processing your request: {error}")

@bot.event
async def on_voice_state_update(member, before, after):
    server_info = get_server_info(member.guild.id)
    vm = server_info["voiceMaster"]

    if not vm["enabled"]:
        return

    if before.channel is None and after.channel:
        if after.channel.id == vm["channelId"]:
            category = after.channel.category
            channel = await category.create_voice_channel(
                f"{member.name}'s Channel",
                user_limit=vm["settings"]["default_limit"]
            )

            vm["channels"][member.id] = channel.id
            await member.move_to(channel)

    if before.channel and member.id in vm["channels"]:
        if before.channel.id == vm["channels"][member.id]:
            if len(before.channel.members) == 0:
                await before.channel.delete()
                vm["channels"].pop(member.id, None)

@bot.event
async def on_message_delete(message):
    serverInfo = get_server_info(message.guild.id)

    serverInfo["snipes"][message.channel.id] = {
        "message": message.content,
        "author": message.author.id,
        "time": datetime.now()
    }

@bot.event
async def on_member_join(member):
    server_info = get_server_info(str(member.guild.id))

    if server_info["welcomeMessage"]["image"]["enabled"]:
        channel = bot.get_channel(int(server_info["welcomeMessage"]["channelId"]))
        embed = discord.Embed(
            color=discord.Color.blue()
        )

        embed.set_image(url=f"https://api.popcat.xyz/v2/welcomecard?background={server_info['welcomeMessage']['image']['background']}&text1={member.name}&text2={server_info['welcomeMessage']['image']['description'].replace('{user}', member.name)}&text3=Member+{len(member.guild.members)}&avatar={member.avatar.url}")
        await channel.send(embed=embed) # type: ignore It's required to be a Text Channel.
    else:
        channel = bot.get_channel(int(server_info["welcomeMessage"]["channelId"]))
        embed = discord.Embed(
            title=server_info["welcomeMessage"]["embed"]["title"].replace("{user}", member.name),
            description=server_info["welcomeMessage"]["embed"]["description"].replace("{user}", member.name),
            color=resolve_color(server_info["welcomeMessage"]["embed"]["color"])
        )

        await channel.send(embed=embed) # type: ignore Required to be a Text channel.

@bot.event
async def on_guild_join(guild):
    channels = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
    if not channels:
        return
    
    chosen = random.choice(channels)

    if chosen.permissions_for(guild.me).send_messages:
        embed = discord.Embed(
            title="Thanks for inviting Grave!",
            description="Thanks for inviting me to your server! We really appreciate it!",
            color=discord.Colour.purple()
        )

        await chosen.send(embed=embed)

@bot.command(
        name="ping",
        description="Get the latency."
)
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latency is: {round(bot.latency * 1000)}ms")

@bot.command(
        name="serverInfo",
        description="Get info about the server you're in."
)
async def serverinfo(ctx):
    embedInfo = discord.Embed(
        title=f"{ctx.guild.name}'s Information",
        description=f"Information about this server ({ctx.guild.name})",
        color=discord.Colour.dark_purple()
    )
    embedInfo.add_field( name = "Server ID:", value = ctx.guild.id)
    embedInfo.add_field( name = "Created On:", value = ctx.guild.created_at )
    embedInfo.add_field( name = "Owner", value = ctx.guild.owner )
    embedInfo.add_field( name = "Member Count: ", value = ctx.guild.member_count )

    await ctx.send(embed=embedInfo)

@bot.command()
async def help(ctx):
    description = "# Here are all of my commands!",

    for command in bot.commands:
        description = f"{description}\n**{command.name}**: {command.description}"
    
    embed = discord.Embed(
        title="Help",
        description=description,
        color=discord.Colour.blue()
    )
    
    await ctx.send(embed=embed)

@bot.command(
    name="ban",
    description="Ban a member."
)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, reason = None):
    try:
        if member == bot.user:
            await ctx.send(f"wow... just no. WOW. after all this time... this is what i get?")
            return
        
        await member.ban(reason=reason)
        await log_moderation(member, "Ban", ctx.guild.id, f"User got banned for reason {reason}")

        await ctx.send(f"✅ Banned user <@{member.id}> {reason: reason if reason else 'no reason'}")
    except Exception as e:
        await ctx.send(f":x: **Error**: {e}")

@bot.command(
    name="kick",
    description="Kick a member."
)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, reason = None):
    try:
        if member == bot.user:
            await ctx.send(f"wow... just no. WOW. after all this time... this is what i get?")
            return
        
        await member.kick(reason=reason)
        await log_moderation(member, "Kick", ctx.guild.id, f"User got kicked for reason {reason}")

        await ctx.send(f"✅ Kicked user <@{member.id}> for {reason: reason if reason else 'no reason'}")
    except Exception as e:
        await ctx.send(f":x: **Error**: {e}")

@bot.command(
        name="rizz",
        description="Get W rizz from this command frfr"
)
async def rizz(ctx):
    reply = requests.get("https://api.popcat.xyz/v2/pickuplines").json()
    embed = discord.Embed(
        title="Rizz",
        description=f"**Rizz Line**: {reply['message']['pickupline']}",
        color=discord.Colour.red()
    )

    await ctx.send(embed=embed)

@bot.command(
        name="unforgivable",
        description="Something unforgivable"
)
async def unforgivable(ctx, *, message):
    embed = discord.Embed(
        color=discord.Color.blue()
    )

    embed.set_image(url=f"https://api.popcat.xyz/v2/unforgivable?text={message.replace(' ', '+')}")

    await ctx.send(embed=embed)

@bot.command(
        name="wanted",
        description="Make someone wanted!"
)
async def wanted(ctx, user: discord.Member):
    embed = discord.Embed(
        color=discord.Color.blue()
    )

    embed.set_image(url=f"https://api.popcat.xyz/v2/wanted?image={user.avatar.url}") # type: ignore it does exist

    await ctx.send(embed=embed)



@bot.command(
        name="immitate",
        description="Make a discord message / image of a user saying whatever you want!"
)
async def immitate(ctx, user: discord.Member, *, message):
    embed = discord.Embed(
        color=discord.Colour.blue()
    )

    embed.set_image(url=f"https://api.popcat.xyz/v2/discord-message?username={user.name}&content={message.replace(' ', '+')}&avatar={user.avatar.url}&color=%23ffcc99&timestamp=2025-09-02T18%3A30%3A00Z") # type: ignore Avatar URL Exists

    await ctx.send(embed=embed)

@bot.command(
        name="drip",
        description="Make anyone look drippy."
)
async def drip(ctx, user: discord.Member):
    if user == bot.user:
        await ctx.send(f"No need to drip me, I'm already drippy as is.")

        return

    embed = discord.Embed(
        color=discord.Colour.blue()
    )
    embed.set_image(url=f"https://api.popcat.xyz/v2/drip?image={user.avatar.url}") # type: ignore Avatar URL Exists

    await ctx.send(embed=embed)

@bot.command(
        name="sswebs",
        description="ScreenShot a website!"
)
async def sswebs(ctx, webs):
    embed = discord.Embed(
        color=discord.Color.blue()
    )

    embed.set_image(url=f"https://api.popcat.xyz/v2/screenshot?url={webs}")

    await ctx.send(embed=embed)

@bot.command(
        name="alert",
        description="ALERTTT!!"
)
async def alert(ctx, *, message):
    embed = discord.Embed(
        color=discord.Color.blue()
    )

    embed.set_image(url=f"https://api.popcat.xyz/v2/alert?text={message.replace(' ', '+')}")

    await ctx.send(embed=embed)

@bot.command(
        name="biden",
        description="Make biden tweet anything!"
)
async def biden(ctx, *, message):
    embed = discord.Embed(
        color=discord.Color.blue()
    )

    embed.set_image(url=f"https://api.popcat.xyz/v2/biden?text={message.replace(' ', '+')}")

    await ctx.send(embed=embed)

@bot.command(
        name="randomcar",
        description="Get a random car!"
)
async def randomcar(ctx):
    req = requests.get("https://api.popcat.xyz/v2/car").json()
    embed = discord.Embed(
        title=req["message"]["title"],
        color=discord.Color.blue()
    ) 
    
    embed.set_image(url=req["message"]["image"])

    await ctx.send(embed=embed)

@bot.command(
        name="threaten",
        description="Threaten a person!"
)
async def threaten(ctx, *, message):
    embed = discord.Embed(
        color=discord.Color.blue()
    )

    embed.set_image(url=f"https://api.popcat.xyz/v2/gun?image={ctx.author.avatar.url}&text={message.replace(' ', '+')}")

    await ctx.send(embed=embed)

@bot.command(
    name="welcomeImage",
    description="Shows an image on join"
)
@commands.has_permissions(administrator=True)
async def welcomeImage(ctx, backgroundUrl, description, channelId: discord.TextChannel):
    serverInfo = get_server_info(str(ctx.guild.id))
    await log_moderation(ctx.author, "Welcome Image Changed", ctx.guild.id, "")

    serverInfo["welcomeMessage"]["channelId"] = channelId.id

    if not serverInfo["welcomeMessage"]["image"]["enabled"]:
        serverInfo["welcomeMessage"]["image"]["enabled"] = True
        serverInfo["welcomeMessage"]["embed"]["enabled"] = False
    
    serverInfo["welcomeMessage"]["image"]["background"] = backgroundUrl
    serverInfo["welcomeMessage"]["image"]["description"] = description

    await ctx.send(f" (+ will be used as a space)")

@bot.command(
    name="welcomeEmbed",
    description="Set the Welcome Embed. {user} for user."
)
@commands.has_permissions(administrator=True)
async def welcomeEmbed(ctx, embedColor, title, description, channelId: discord.TextChannel):
    serverInfo = get_server_info(str(ctx.guild.id))
    await log_moderation(ctx.author, "Welcome Embed Change", ctx.guild.id, "User changed the welcome embed.")

    serverInfo["welcomeMessage"]["channelId"] = channelId.id

    if not serverInfo["welcomeMessage"]["embed"]["enabled"]:
        serverInfo["welcomeMessage"]["embed"]["enabled"] = True
        serverInfo["welcomeMessage"]["image"]["enabled"] = False
    
    serverInfo["welcomeMessage"]["embed"]["color"] = embedColor
    serverInfo["welcomeMessage"]["embed"]["description"] = description.replace("+", " ")
    serverInfo["welcomeMessage"]["embed"]["title"] = title.replace("+", " ")

    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue. (+ will be used as a space!)")

@bot.command(
    name="linkstoggle",
    description="Allows / Disables Links"
)
@commands.has_permissions(administrator=True)
async def linkstoggle(ctx):
    await log_moderation(ctx.author, "Changed Links Toggle", ctx.guild.id, f"User changed Links Toggle")
    servers_temp[ctx.guild.id]["moderation"]["linksAllowed"] = not servers_temp[ctx.guild.id]["moderation"]["linksAllowed"]

    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
    name="swearingtoggle",
    description="Toggle Swearing filter on / off"
)
@commands.has_permissions(administrator=True)
async def swearingtoggle(ctx):
    serverinfo = get_server_info(ctx.guild.id)
    await log_moderation(ctx.author, "Changed Swearing Toggle", ctx.guild.id, f"User changed Swearing Toggle")

    serverinfo["moderation"]["swearingAllowed"] = not serverinfo["moderation"]["swearingAllowed"]

    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
    name="moderationlogging",
    description="Toggle on moderation logging."
)
@commands.has_permissions(administrator=True)
async def moderationlogging(ctx, channel: discord.TextChannel):
    serverinfo = get_server_info(ctx.guild.id)
    moderation = serverinfo

    moderation["logs"]["moderation"] = True
    moderation["logs"]["channelId"] = channel.id

    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
    name="disablecmdsin",
    description="Disable Commands in a channel."
)
@commands.has_permissions(administrator=True)
async def disablecmdsin(ctx, channel: discord.TextChannel):
    await log_moderation(ctx.author, "User disabled commands in a channel.", ctx.guild.id, f"User disabled commands in {channel}")
    server_info = get_server_info(ctx.guild.id)
    moderation = server_info["moderation"]

    if not channel.id in moderation["disabledCmdsChannels"]:
        moderation["disabledCmdsChannels"].append(channel.id)
    
    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
    name="removechannelfromcmdsin",
    description="SORRY FOR LONG NAME! Remove a channel from disabled commands channels."
)
@commands.has_permissions(administrator=True)
async def removechannelfromcmdsin(ctx, channel: discord.TextChannel):
    await log_moderation(ctx.author, "User undisabled commands in a channel.", ctx.guild.id, f"User undisabled commands in {channel}")
    server_info = get_server_info(ctx.guild.id)
    moderation = server_info["moderation"]

    if channel.id in moderation["disabledCmdsChannels"]:
        moderation["disabledCmdsChannels"].remove(channel.id)
    
    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
    name="snipe",
    description="Snipe any message from the given channel. (Gives last deleted message)"
)
@commands.has_permissions(administrator=True)
async def snipe(ctx):
    server_info = get_server_info(ctx.guild.id)
    snipes = server_info["snipes"]

    if snipes[ctx.channel.id]:
        user = bot.get_user(snipes[ctx.channel.id]["author"])
        embed = discord.Embed(
            title="Sniped",
            description=f"**User**: {user.name}\n**Message**: {snipes[ctx.channel.id]['message']}", # type: ignore it works.
            color=discord.Colour.red()
        )
        embed.set_thumbnail(url=user.avatar.url) # type: ignore it works.
        embed.set_footer(text=f"At: {snipes[ctx.channel.id]['time']}")

        await ctx.send(embed=embed)

@bot.command(
    name="prefixchange",
    descripton="Change the prefix for the server."
)
@commands.has_permissions(administrator=True)
async def prefixchange(ctx, prefix):
    serverInfo = get_server_info(ctx.guild.id)

    await log_moderation(ctx.author, "User changed prefix.", ctx.guild.id, f"User changed prefix to: **{prefix}**")

    serverInfo["prefix"] = prefix

    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")


@bot.command(
    name="changepfp",
    description="Change the profile picture of the bot."
)
@commands.has_permissions(administrator=True)
async def changepfp(ctx, url):
    try:
        data = requests.get(url)
        contents = data.content
        
        
        await bot.user.edit(avatar=contents) # type: ignore it does exist.

        await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")
    except Exception as e:
        await ctx.send(f":x: {e}")

@bot.command(
    name="purge",
    descriptions="Purge messages."
)
@commands.has_permissions(administrator=True)
async def purge(ctx, amount):
    await ctx.channel.purge(limit=int(amount))

    msg = await ctx.send(f"✅ Purged {amount} messages")

    time.sleep(1)

    await msg.delete()

@bot.command(name="vmsetup", description="Setup VoiceMaster")
@commands.has_permissions(administrator=True)
async def vmsetup(ctx):
    server_info = get_server_info(ctx.guild.id)
    vm = server_info["voiceMaster"]

    category = await ctx.guild.create_category("Voice Master")
    channel = await category.create_voice_channel("Join to Create")

    vm["enabled"] = True
    vm["channelId"] = channel.id
    vm["channels"] = {}
    vm.setdefault("settings", {})["default_limit"] = 5

    await ctx.send("✅ VoiceMaster setup completed.")


@bot.command(name="vmlock", description="Lock your VoiceMaster channel")
async def vmlock(ctx):
    channel = get_vm_owned_channel(ctx)
    if not channel:
        return await ctx.send("❌ You do not own a VoiceMaster channel.")

    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.connect = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔒 Channel locked.")


@bot.command(name="vmunlock", description="Unlock your VoiceMaster channel")
async def vmunlock(ctx):
    channel = get_vm_owned_channel(ctx)
    if not channel:
        return await ctx.send("❌ You do not own a VoiceMaster channel.")

    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.connect = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    await ctx.send("🔓 Channel unlocked.")


@bot.command(name="vmkick", description="Kick a member from your VoiceMaster channel")
async def vmkick(ctx, member: discord.Member):
    channel = get_vm_owned_channel(ctx)
    if not channel or member not in channel.members:
        return await ctx.send("❌ Member is not in your channel.")

    await member.move_to(None)
    await ctx.send(f"👢 Kicked {member.display_name}.")


@bot.command(name="vmban", description="Ban a member from your VoiceMaster channel")
async def vmban(ctx, member: discord.Member):
    channel = get_vm_owned_channel(ctx)
    if not channel:
        return await ctx.send("❌ You do not own a VoiceMaster channel.")

    overwrite = channel.overwrites_for(member)
    overwrite.connect = False
    await channel.set_permissions(member, overwrite=overwrite)

    if member in channel.members:
        await member.move_to(None)

    await ctx.send(f"⛔ Banned {member.display_name}.")


@bot.command(name="vmlimit", description="Set user limit for your VoiceMaster channel")
async def vmlimit(ctx, limit: int):
    channel = get_vm_owned_channel(ctx)
    if not channel:
        return await ctx.send("❌ You do not own a VoiceMaster channel.")

    if limit < 0 or limit > 99:
        return await ctx.send("❌ Limit must be between 0 and 99.")

    await channel.edit(user_limit=limit)
    await ctx.send(f"🔢 User limit set to {limit}.")


@bot.command(name="vmrename", description="Rename your VoiceMaster channel")
async def vmrename(ctx, *, name):
    channel = get_vm_owned_channel(ctx)
    if not channel:
        return await ctx.send("❌ You do not own a VoiceMaster channel.")

    await channel.edit(name=name)
    await ctx.send("✏ Channel renamed.")


@bot.command(name="vmdefaultlimit", description="Set default VoiceMaster limit")
@commands.has_permissions(administrator=True)
async def vmdefaultlimit(ctx, limit: int):
    if limit < 0 or limit > 99:
        return await ctx.send("❌ Limit must be between 0 and 99.")

    server_info = get_server_info(ctx.guild.id)
    server_info["voiceMaster"].setdefault("settings", {})["default_limit"] = limit

    await ctx.send(f"✅ Default VoiceMaster limit set to {limit}.")


@bot.command(name="vmdisable", description="Disable VoiceMaster")
@commands.has_permissions(administrator=True)
async def vmdisable(ctx):
    server_info = get_server_info(ctx.guild.id)
    vm = server_info["voiceMaster"]

    for ch_id in list(vm["channels"].values()):
        channel = ctx.guild.get_channel(ch_id)
        if channel:
            await channel.delete()

    vm["channels"].clear()
    vm["enabled"] = False

    await ctx.send("🛑 VoiceMaster disabled and cleaned up.")

@bot.command()
async def warn(ctx, user: discord.Member, *, reason):
    server_info = get_server_info(ctx.guild.id)

    await log_moderation(ctx.author.id, f"Warned <@{user.id}>", ctx.guild.id, "")

    if user.id not in server_info["warns"]:
        server_info["warns"][user.id] = [
            {
                "date": datetime.now(),
                "by": ctx.author.id,
                "reason": reason
            }
        ]
    else:
        server_info["warns"][user.id].append({
                "date": datetime.now(),
                "by": ctx.author.id,
                "reason": reason
            })
    
    embed = discord.Embed(
        description=f"<:PlusLogo:1453259324674539661> A warn was added to <@{user.id}> for {reason}. The user now has {len(server_info['warns'][user.id])} warns.",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def clearwarns(ctx, user: discord.Member):
    server_info = get_server_info(ctx.guild.id)

    if user.id in server_info["warns"]:
        server_info["warns"][user.id] = []

        embed = discord.Embed(
            description="<:Tick:1453257219545108632> Your updates were applied without issue.",
            color=discord.Colour.blue()
        )

        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=":x: The user has no warns.",
            color=discord.Colour.blue()
        )

        await ctx.send(embed=embed)

@bot.command()
async def checkwarns(ctx, user: discord.Member):
    server_info = get_server_info(ctx.guild.id)

    if user.id in server_info["warns"]:
        embed = discord.Embed(
            description=f"## The user <@{user.id}> has {len(server_info['warns'][user.id])} warns.",
            color=discord.Color.blue()
        )

        for i, warn in enumerate(server_info["warns"][user.id], start=1):
            embed.add_field(name=warn['reason'], value=f"By {bot.get_user(int(warn['by'])).id} on {warn['date']}") # type: ignore im pretty sure it does exist ;) -- iamiak
        
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"The user <@{user.id}> has no warns.",
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

@bot.command()
async def roleadd(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(discord.utils.get(ctx.guild.roles, id=role.id))

    embed = discord.Embed(
        description=f"<:PlusLogo:1453259324674539661> Role <@&{role.id}> was added to <@{user.id}>",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def roleremove(ctx, user: discord.Member, role: discord.Role):
    await user.remove_roles(discord.utils.get(ctx.guild.roles, id=role.id))

    embed = discord.Embed(
        description=f"<:PlusLogo:1453259324674539661> Role <@&{role.id}> was removed from <@{user.id}>",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def levelsystemtoggle(ctx):
    server_info = get_server_info(ctx.guild.id)

    embed = discord.Embed(
        description="<:Tick:1453257219545108632> Your updates were applied without issue.",
        color=discord.Colour.blue()
    )

    server_info["levels"]["enabled"] = not server_info["levels"]["enabled"]

    await ctx.send(embed=embed)

@bot.command()
async def level(ctx):
    server_info = get_server_info(ctx.guild.id)

    background = Editor(Canvas((900, 300), color="#141414"))
    user_image = await load_image_async(str(ctx.author.avatar.url))
    profile = Editor(user_image).resize((150, 150)).circle_image()

    poppins = Font.poppins(size=40)
    poppins_sml = Font.poppins(size=30)

    background.polygon([(600,0),(750,300),(900,300),(900,0)], color="#FFFFFF")
    background.paste(profile, (30, 30))

    background.rectangle((30, 220), width=650, height=40, color="#FFFFFF", radius=20)

    background.rectangle((200, 100), width=350, height=2, fill="#FFFFFF")
    background.bar((30, 220), max_width=650, height=40, percentage=server_info["levels"][ctx.author.id]["xp"], color="#14bed8", radius=20,)

    background.text((200, 40), ctx.author.name, font=poppins, color="#FFFFFF")

    background.rectangle((200, 100), width=350, height=2, fill="#FFFFFF")
    background.text(
        (200,130),
        f'Level - {server_info["levels"][ctx.author.id]["level"]} | XP - {server_info["levels"][ctx.author.id]["xp"]}/100',
        font=poppins_sml,
        color="#FFFFFF",
    )

    file = discord.File(fp=background.image_bytes, filename="DCard.png")

    await ctx.send(file=file)

@bot.command()
async def setBoosterMessage(ctx, title, description, channel: discord.TextChannel):
    server_info = get_server_info(ctx.guild.id)
    description = description.replace("+", " ")
    title = title.replace("+", " ")

    server_info["boosterMessage"] = True 
    server_info["boosterMessage"]["title"] = title
    server_info["boosterMessage"]["description"] = description
    server_info["boosterMessage"]["channelId"] = channel.id

    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
        name="rbxauthorization",
        description="Add roblox authentication to your server!"
)
async def rbxauthorization(ctx, role: discord.Role):
    server_info = get_server_info(ctx.guild.id)

    embed = discord.Embed(
        title="Verification",
        description="This server uses Grave Bots Roblox linker authentication.",
        color=discord.Color.purple()
    )
    button = discord.ui.Button(
        label="Open Input",
        style=discord.ButtonStyle.blurple,
        custom_id="RBX_verify_start"
    )

    view = discord.ui.View()
    view.add_item(button)

    server_info["robloxVerification"]["enabled"] = True
    server_info["robloxVerification"]["roleId"] = role.id

    newCategory = await ctx.guild.create_category("Verify Here")
    newChannel = await newCategory.create_text_channel("Verify Here")

    await newChannel.send(embed=embed, view=view)
    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
    name="setgwchannel",
    description="Set the GiveAway Channel."
)
async def setgwchannel(ctx, channel: discord.TextChannel):
    server_info = get_server_info(ctx.guild.id)

    server_info["gwInfo"]["channelId"] = channel.id

    await ctx.send(f"<:Tick:1453257219545108632> Your updates were applied without issue.")

@bot.command(
    name="gw",
    description="Start a giveaway!"
)
async def gw(ctx, prize, time, winners):
    server_info = get_server_info(ctx.guild.id)
    prize = prize.replace("+", " ")

    time = timeparse(time)

    embed = discord.Embed(
        title="🎉 New Giveaway!",
        description=f"**Prize**: {prize}\n**Time**: {time}\n\n **Winners**: {winners}",
        color=discord.Color.blue()
    )
    
    msg = await bot.get_channel(server_info["gwInfo"]["channelId"]).send(embed=embed) # type: ignore

    await msg.add_reaction('\U0001F44D')
    
    await asyncio.sleep(time) # type: ignore

    message = await ctx.fetch_message(msg.id)
    users = [user async for user in message.reactions[0].users() if not user.bot]


    winners_list = random.sample(users, k=min(int(winners), len(users)))
    winners_mentions = ", ".join([winner.mention for winner in winners_list])

    await bot.get_channel(server_info["gwInfo"]["channelId"]).send(f"Congratulations {winners_mentions}! You won **{prize}**!") # type: ignore


bot.run(token)  # type: ignore It works.
