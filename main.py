import discord
from src.bot import AQWMechanicsBot
from dotenv import load_dotenv
import os

load_dotenv()

try:
    bot = AQWMechanicsBot(token=os.getenv("TOKEN"), admins={"admin": 1143657502941122580}, command_prefix="!", intents=discord.Intents.all())
    bot.start_bot()
except Exception as e:
    raise Exception(e)