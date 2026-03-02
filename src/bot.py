from typing import List, Optional
from discord.ext import commands
import discord
import aiohttp
import os
import json

class AQWMechanicsBot(commands.Bot):
    def __init__(self, token: str, admins: dict[str, int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admins = admins
        self.token = token

    async def load_all_cogs(self):
        
        print("Loading cogs...")
        for file in os.listdir("./src/cogs"):
            if file.endswith(".py") and "__init__" not in file:
                try:
                    await self.load_extension(f"src.cogs.{file[:-3]}")
                except Exception as e:
                    print(f"Failed to load cog\n{e}")
        
        print("Cogs loaded.")

    def get_all_classes(self) -> dict:
        with open("./classes.json", "r") as f:
            data = json.load(f)
    
        data = {k.lower(): v for k, v in data.items()}

        return data

    def get_class_data(self, class_name: str) -> dict:
        with open("./classes.json", "r") as f:
            data = json.load(f)
    
        data = {k.lower(): v for k, v in data.items()}
        return data.get(class_name.lower(), {})

    def start_bot(self):
        self.run(self.token)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online!")
        await self.tree.sync()


    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.load_all_cogs()
        return await super().setup_hook()
