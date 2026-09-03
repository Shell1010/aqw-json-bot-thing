from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord import app_commands
from discord.ext import commands
from ..classes.views import ClassView, ScrollView, SearchResultsView, ConversionRateView

if TYPE_CHECKING:
    from ..bot import AQWMechanicsBot


class display(commands.Cog):
    def __init__(self, bot: AQWMechanicsBot):
        self.bot = bot

    async def class_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        classes = await self.bot.get_all_classes()
    
        current = current.lower().strip()
    
        if not current:
            return []
    
        matches = [
            class_name
            for class_name in classes.keys()
            if current in class_name.lower()
        ]
    
        matches.sort(
            key=lambda name: (
                not name.lower().startswith(current),
                name.lower(),
            )
        )
    

        return [
            discord.app_commands.Choice(
                name=name,
                value=name,
            )
            for name in matches[:25]
        ]
        
    async def scroll_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        classes = await self.bot.get_all_scrolls()
    
        current = current.lower().strip()
    
        matches = [
            class_name
            for class_name in classes.keys()
            if current in class_name.lower()
        ]
    
        matches.sort(
            key=lambda name: (
                not name.lower().startswith(current),
                name.lower(),
            )
        )
    

        return [
            discord.app_commands.Choice(
                name=name,
                value=name,
            )
            for name in matches[:25]
        ]
        
    @app_commands.command(name="scroll")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.autocomplete(name=scroll_autocomplete)
    async def scroll(self, interaction: discord.Interaction, name: str):
        data = await self.bot.get_scroll_data(name)
        view = ScrollView(data)
        await interaction.response.send_message(view=view)

    @app_commands.command(name="class")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.autocomplete(name=class_autocomplete)
    async def class_(self, interaction: discord.Interaction, name: str):
        data = await self.bot.get_class_data(name)
        view = ClassView(data, self.bot)
        await interaction.response.send_message(view=view)

    @app_commands.command(name="search")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(query="The value to search for (optional)", param="The JSON parameter to search on", source="Which data source to search")
    @app_commands.choices(source=[
        discord.app_commands.Choice(name="Classes", value="classes"),
        discord.app_commands.Choice(name="Scrolls", value="scrolls"),
        discord.app_commands.Choice(name="Both", value="both"),
    ])
    async def search(self, interaction: discord.Interaction, param: str, query: str | None = None, source: str = "both"):
        results = await self.bot.search_data(param, query, source)
        
        if not results:
            await interaction.response.send_message(f"No results found for param `{param}`" + (f" with query `{query}`" if query else ""))
            return
        
        view = SearchResultsView(results, param, self.bot)
        await interaction.response.send_message(view=view)

    async def model_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        models = await self.bot.get_all_models()
        current = current.lower().strip()
        if not current:
            return []
        matches = [m for m in models if current in m.lower()]
        matches.sort()
        return [discord.app_commands.Choice(name=m, value=m) for m in matches[:25]]

    @app_commands.command(name="lookup")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(model="The stat model to look up", level="The level (1-100)")
    @app_commands.autocomplete(model=model_autocomplete)
    async def lookup(self, interaction: discord.Interaction, model: str, level: int):
        if level < 1 or level > 100:
            await interaction.response.send_message("Level must be between 1 and 100.")
            return
        
        data = await self.bot.get_conversion_data(model, level)
        if not data:
            await interaction.response.send_message(f"No conversion data found for model `{model}` at level `{level}`.")
            return
        
        view = ConversionRateView(data)
        await interaction.response.send_message(view=view)

async def setup(bot: AQWMechanicsBot):
    await bot.add_cog(display(bot))
