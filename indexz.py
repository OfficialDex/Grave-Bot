# imports
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
# functions
def get_prefix(bot, msg):
    return ","

    
async def blaze_part():
    await bot.load_extension("blaze")

# variables / bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# hook assignment
bot.setup_hook = blaze_part

# run
token = os.getenv("TOKEN")
bot.run(token)
