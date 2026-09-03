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
        self.class_url = "https://raw.githubusercontent.com/Shell1010/aqw-json-stuff/refs/heads/main/classes.json"
        self.scroll_url = "https://raw.githubusercontent.com/Shell1010/aqw-json-stuff/refs/heads/main/scrolls.json"

    async def load_all_cogs(self):
        
        print("Loading cogs...")
        for file in os.listdir("./src/cogs"):
            if file.endswith(".py") and "__init__" not in file:
                try:
                    await self.load_extension(f"src.cogs.{file[:-3]}")
                except Exception as e:
                    print(f"Failed to load cog\n{e}")
        
        print("Cogs loaded.")
        
    async def get_class_data(self, class_name: str) -> dict:
       
        data = await self.get_all_classes()
        
        return data.get(class_name.lower(), {})
        
    async def get_scroll_data(self, scroll_name: str) -> dict:
        data = await self.get_all_scrolls()
        
        return data.get(scroll_name.lower(), {})
        
    def _find_key_recursive(self, data, key: str, path: str = "") -> list[str]:
        results = []
        if isinstance(data, dict):
            for k, v in data.items():
                current_path = f"{path}.{k}" if path else k
                if k == key:
                    results.append((current_path, v))
                results.extend(self._find_key_recursive(v, key, current_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                results.extend(self._find_key_recursive(item, key, current_path))
        return results

    def _key_exists_recursive(self, data, key: str) -> bool:
        if isinstance(data, dict):
            if key in data:
                return True
            return any(self._key_exists_recursive(v, key) for v in data.values())
        elif isinstance(data, list):
            return any(self._key_exists_recursive(item, key) for item in data)
        return False

    async def search_data(self, param: str, query: str | None = None, source: str = "both") -> list[dict]:
        results = []

        if source in ("classes", "both"):
            classes = await self.get_all_classes()
            for name, data in classes.items():
                if not self._key_exists_recursive(data, param):
                    continue
                if query is not None:
                    matches = self._find_key_recursive(data, param)
                    found = False
                    for _, val in matches:
                        if query.lower() in str(val).lower():
                            found = True
                            break
                    if not found:
                        continue
                results.append({"source": "class", "name": name, "data": data})

        if source in ("scrolls", "both"):
            scrolls = await self.get_all_scrolls()
            for name, data in scrolls.items():
                if not self._key_exists_recursive(data, param):
                    continue
                if query is not None:
                    matches = self._find_key_recursive(data, param)
                    found = False
                    for _, val in matches:
                        if query.lower() in str(val).lower():
                            found = True
                            break
                    if not found:
                        continue
                results.append({"source": "scroll", "name": name, "data": data})

        return results

    async def get_all_scrolls(self) -> dict:
        async with self.session.get(self.scroll_url) as response:
            data = json.loads((await response.text()))
        
        data = {k.lower(): v for k, v in data.items()}

        return data
        

    async def get_all_classes(self) -> dict:
        async with self.session.get(self.class_url) as response:
            data = json.loads((await response.text()))
        
        data = {k.lower(): v for k, v in data.items()}

        return data

    def start_bot(self):
        self.run(self.token)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online!")
        await self.tree.sync()


    async def get_conversion_data(self, model: str, level: int) -> dict | None:
        levels = self.conversion_rates.get("levels", {})
        level_data = levels.get(str(level))
        if not level_data:
            return None
        data = level_data.get(model.lower().title())
        if not data:
            return None
        headers = self.conversion_rates.get("headers", {})
        cols = {k: headers.get(k, {}) for k in data}
        return {"model": model, "level": level, "data": data, "headers": cols, "base_info": {
            "hp-1": self.conversion_rates.get("hp-1"),
            "hp-2": self.conversion_rates.get("hp-2"),
            "level_cap": self.conversion_rates.get("level_cap"),
        }}

    async def get_all_models(self) -> list[str]:
        return list(self.conversion_rates.get("class_ranges", {}).keys())

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.load_all_cogs()
        with open("conversion_rates.json") as f:
            self.conversion_rates = json.load(f)
        return await super().setup_hook()
