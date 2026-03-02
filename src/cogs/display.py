from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord import app_commands
from discord.ext import commands
from ..classes.views import ClassView

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
        classes = self.bot.get_all_classes()
    
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
    
        # 4️⃣ Return top 25
        return [
            discord.app_commands.Choice(
                name=name,
                value=name,
            )
            for name in matches[:25]
        ]

    @app_commands.command(name="class")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.autocomplete(current_class=class_autocomplete)
    async def class_(self, interaction: discord.Interaction, current_class: str):
        data = self.bot.get_class_data(current_class)
        view = ClassView(data)
        await interaction.response.send_message(view=view)

async def setup(bot: AQWMechanicsBot):
    await bot.add_cog(display(bot))
