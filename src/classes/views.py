
from itertools import zip_longest
from typing import List
import discord
from discord.ext.commands.parameters import CurrentChannel


CLASS_CODES = {
    "M1": "Tank Melee",
    "M2": "Dodge Melee",
    "M3": "Hybrid",
    "M4": "Power Melee",
    "C1": "Offensive Caster",
    "C2": "Defensive Caster",
    "C3": "Power Caster",
    "S1": "Luck Hybrid",
}

STAT_CODES = {
    "cmi": "Magical Intake",
    "cai": "All Intake",
    "cpi": "Physical Intake",
    "cdi": "DoT Intake",
    "chi": "Healing Intake",

    "cao": "All Out",
    "cpo": "Physical Out",
    "cdo": "DoT Out",
    "cmo": "Magical Out",
    "cho": "Healing Out",

    "tdo": "Dodge Chance",
    "thi": "Hit Chance",
    "cmc": "Mana Consumption",
    "tha": "Haste",
    "tcr": "Crit Chance",
    "scm": "Crit Multiplier",

    "ap": "Attack Power",
    "sp": "Spell Power",

    "STR": "Strength",
    "INT": "Intellect",
    "END": "Endurance",
    "DEX": "Dexterity",
    "WIS": "Wisdom",

    # Both map to the same stat
    "LCK": "Luck",
    "LUK": "Luck",
}


class AurasView(discord.ui.LayoutView):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.container = discord.ui.Container()
        action_row = discord.ui.ActionRow()
        
        back_button = discord.ui.Button(label="←", style=discord.ButtonStyle.secondary, custom_id="back")
        back_button.callback = self.back_callback
        action_row.add_item(back_button)
        
        action_row.add_item(discord.ui.Button(label="#passives", style=discord.ButtonStyle.primary, custom_id="forward", disabled=True))
        self.add_item(self.container)
        self.container.add_item(action_row)
        
        
        self.container.add_item(discord.ui.TextDisplay("# Passives"))
        self.container.add_item(discord.ui.Separator())
        passive_data = ""
        actions_passives = self.data['actions']['passive']
        
        for item, passive in zip_longest(data['auras'], actions_passives):
            name = passive['nam']
            passive_data += f"### {name}\n"
            passive_data += f"*{passive['desc']}*\n\n"
            if item is not None:
                for e in item.get("e", []):
                    stat = e['sta']
                    value = e['val']
                    type = e['typ']
                    stat = STAT_CODES.get(stat, stat)
                    type = type.replace("*", "×")
                    passive_data += f"**{stat}**: {value} ({type})\n"
            self.container.add_item(discord.ui.TextDisplay(passive_data))
            passive_data = ""
            
    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=ClassView(self.data))
    
        
class SkillsView(discord.ui.LayoutView):
    def __init__(self, data: dict, current: int = 0):
        super().__init__()
        self.data = data
        self.current = current
        
        self.container = discord.ui.Container()
        action_row = discord.ui.ActionRow()
        
        back_button = discord.ui.Button(label="←", style=discord.ButtonStyle.secondary, custom_id="back")
        back_button.callback = self.back_callback
        action_row.add_item(back_button)
        
        action_row.add_item(discord.ui.Button(label="#skills", style=discord.ButtonStyle.primary, custom_id="forward", disabled=True))
        self.add_item(self.container)
        self.container.add_item(action_row)
        self.container.add_item(discord.ui.TextDisplay("# Skills"))
        self.container.add_item(discord.ui.Separator())
        
        current_label = self.data['actions']['active'][self.current]['nam']
        
        self.skill_select = discord.ui.Select(
            placeholder=current_label,
            options=[
                discord.SelectOption(label=skill['nam'], value=str(i))
                for i, skill in enumerate(self.data['actions']['active'])
                if skill['nam'] != "Potions"
            ]
        )
        self.skill_select.callback = self.skill_select_callback
        skill_data_json = self.data['actions']['active']
        current_skill = skill_data_json[self.current]
        skill_data = ""
        name = current_skill['nam']
        if name != "Potions":
            
            description = current_skill['desc']
            skill_data += f"### {name}\n*{description}*\n\n"
            self.container.add_item(discord.ui.Separator(visible=False))
            for k,v in current_skill.items():
                if k in ['nam', 'desc', 'id', 'fx', 'anim', 'strl', 'isOK', 'icon', 'tgtMin', 'auras']:
                    continue
    
                skill_data += f"**{k}**: {v}\n"
            skill_data += "\n"
            self.container.add_item(discord.ui.TextDisplay(skill_data))
            self.container.add_item(discord.ui.Separator(visible=False))
            self.container.add_item(discord.ui.ActionRow(self.skill_select))
            
        
        
    async def skill_select_callback(self, interaction: discord.Interaction):
        print(self.skill_select.values[0], self.current)
        await interaction.response.edit_message(view=SkillsView(self.data, int(self.skill_select.values[0])))
        

    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=ClassView(self.data))
        


class ClassView(discord.ui.LayoutView):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.class_name = data['sClassName']
        self.description = data['sDesc']
        self.container = discord.ui.Container()
        self.add_item(self.container)
        self.container.add_item(discord.ui.TextDisplay(f"# {self.class_name}"))
        self.container.add_item(discord.ui.Separator())
        self.container.add_item(discord.ui.TextDisplay(f"*{self.description}*"))
        self.container.add_item(discord.ui.Separator(visible=False))
        
        auras_len = data['auras']
        class_model = CLASS_CODES.get(data['sClassCat'], "Unknown")
        mrm = '\n'.join(data['aMRM'])
        self.container.add_item(discord.ui.TextDisplay(f"**Class Model**: {class_model}"))
        self.container.add_item(discord.ui.TextDisplay(f"**Mana Regen Model**: {mrm}"))
        self.container.add_item(discord.ui.Separator(visible=False))
        
        auras = discord.ui.Button(label="View Auras", style=discord.ButtonStyle.primary)
        auras.callback = self.auras_callback
        self.container.add_item(
            discord.ui.Section(discord.ui.TextDisplay(f"**Auras**: {len(auras_len)}"), accessory=auras)
            )
        self.container.add_item(discord.ui.Separator(visible=False))
        
        actives_len = data['actions']['active']
        actives = discord.ui.Button(label="View Skills", style=discord.ButtonStyle.primary)
        actives.callback = self.actives_callback
        self.container.add_item(
            discord.ui.Section(discord.ui.TextDisplay(f"**Skills**: {len(actives_len) - 1}"), accessory=actives)
            )
        self.container.add_item(discord.ui.Separator(visible=False))
        
    async def auras_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=AurasView(self.data))
        
    async def actives_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=SkillsView(self.data))

class ScrollView(discord.ui.LayoutView):
    def __init__(self, data):
        super().__init__()
        self.data = data
        
        name = data['name']
        obj = data['o']
        self.container = discord.ui.Container()
        self.add_item(self.container)
        title = discord.ui.TextDisplay(f"# {name}")
        self.container.add_item(title)
        self.container.add_item(discord.ui.Separator(visible=True))
        text = ""
        for k,v in obj.items():
            if k in ['name', 'desc', 'id', 'fx', 'anim', 'strl', 'isOK', 'icon', 'tgtMin', 'auras']:
                continue
            text += f"**{k}**: {v}\n"
        self.container.add_item(discord.ui.TextDisplay(text))
        self.container.add_item(discord.ui.Separator(visible=False))


class SearchResultsView(discord.ui.LayoutView):
    MAX_RESULTS = 25
    PAGE_SIZE = 10

    def __init__(self, results: list[dict], param: str, current_page: int = 0):
        super().__init__()
        self.results = results[:self.MAX_RESULTS]
        self.param = param
        self.current_page = current_page
        self.total_pages = max(1, len(self.results) // self.PAGE_SIZE + (1 if len(self.results) % self.PAGE_SIZE else 0))

        self.container = discord.ui.Container()
        self.add_item(self.container)

        start = self.current_page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        page_results = self.results[start:end]

        lines = [f"# Search Results ({len(self.results)}) | Page {self.current_page + 1}/{self.total_pages}"]
        lines.append("")

        for r in page_results:
            s = r["source"]
            n = r["name"]
            d = r["data"]
            pfx = "Class" if s == "class" else "Scroll"
            matches = self._collect_matches(d, self.param)
            lines.append(f"**{pfx}: {n}**")
            for m in matches[:10]:
                lines.append(m)
            if len(matches) > 10:
                lines.append(f"*... and {len(matches) - 10} more matches*")
            lines.append("")

        content = "\n".join(lines)
        if len(content) > 4000:
            content = content[:3997] + "..."

        self.container.add_item(discord.ui.TextDisplay(content))
        self.container.add_item(discord.ui.Separator(visible=False))

        if self.total_pages > 1:
            action_row = discord.ui.ActionRow()
            back_btn = discord.ui.Button(label="<-", style=discord.ButtonStyle.secondary, custom_id="search_back", disabled=self.current_page == 0)
            back_btn.callback = self._back_page
            action_row.add_item(back_btn)
            fwd_btn = discord.ui.Button(label="->", style=discord.ButtonStyle.secondary, custom_id="search_fwd", disabled=self.current_page == self.total_pages - 1)
            fwd_btn.callback = self._fwd_page
            action_row.add_item(fwd_btn)
            self.container.add_item(action_row)

    async def _back_page(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=SearchResultsView(self.results, self.param, self.current_page - 1))

    async def _fwd_page(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=SearchResultsView(self.results, self.param, self.current_page + 1))

    @staticmethod
    def _collect_matches(data, key: str) -> list[str]:
        matches = []
        def _walk(d, path=""):
            if isinstance(d, dict):
                for k, v in d.items():
                    current_path = f"{path}.{k}" if path else k
                    if k == key and not isinstance(v, (dict, list)):
                        matches.append(f"{current_path}: {v}")
                    if isinstance(v, (dict, list)):
                        _walk(v, current_path)
            elif isinstance(d, list):
                for i, item in enumerate(d):
                    _walk(item, f"{path}[{i}]")
        _walk(data)
        return matches
        

