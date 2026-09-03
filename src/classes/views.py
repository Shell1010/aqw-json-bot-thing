from itertools import zip_longest
from typing import List

import discord

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
    "LCK": "Luck",
    "LUK": "Luck",
}

EMOJI_IDS = {
    "lvl": 1545184865937260636,
    "aqwdagger": 1545184190776090674,
    "aqwwand": 1545184189106753598,
    "aqwstaff": 1545184188020293745,
    "luck": 1545184187097809006,
    "endurance": 1545184185579474984,
    "strength": 1545184184161669170,
    "cooldown_reduction": 1545184182781612174,
    "hitchance": 1545184181674446949,
    "dodgechance": 1545184180206571571,
    "critmulti": 1545184179073847418,
    "critchancce": 1545184177895383172,
    "manaconsume": 1545184176473636924,
    "dmgboost": 1545184175387185152,
    "dmgres": 1545184174015782922,
    "range": 1545184172757356625,
    "magicres": 1545184171314643035,
    "magicboost": 1545184170219937853,
    "dotres": 1545184168500269056,
    "dotboost": 1545184166709043260,
    "healin": 1545184164721205319,
    "healout": 1545184153811550348,
    "physres": 1545184145398038558,
    "physboost": 1545184143644823572,
    "aur": 1545184141333627002,
    "skills": 1545184139173564506,
    "hp": 1545184137436991508,
    "forward": 1545184113605218314,
    "backward": 1545184111814119516,
    "dmg": 1545184109934944317,
    "aqwclass": 1545184108160884847,
    "aqwsword": 1545184106432696460,
}


def em(name: str) -> str:
    return f"<:{name}:{EMOJI_IDS[name]}>"


def bem(name: str) -> discord.PartialEmoji:
    return discord.PartialEmoji(name=name, id=EMOJI_IDS[name])


PRIMARY_EMOJI = {
    "STR": "strength",
    "INT": "aqwwand",
    "DEX": "aqwdagger",
    "END": "endurance",
    "WIS": "aqwstaff",
    "LCK": "luck",
    "LUK": "luck",
}

SECONDARY_EMOJI = {
    "AP": "aqwsword",
    "SP": "magicboost",
    "Crit chance(%)": "critchancce",
    "Mag In(%)": "magicres",
    "Mag Out(%)": "dmgboost",
    "Hit chance(%)": "hitchance",
    "Haste(%)": "cooldown_reduction",
    "Dodge(%)": "dodgechance",
    "Crit mod(%)": "critmulti",
}


def sem(secondary: str) -> str:
    if secondary == "AP/SP":
        return f"{em('aqwsword')}{em('magicboost')}"
    e = SECONDARY_EMOJI.get(secondary)
    return f"{em(e)} " if e else ""


STAT_EMOJI = {
    "Magical Intake": "magicres",
    "All Intake": "dmgres",
    "Physical Intake": "physres",
    "DoT Intake": "dotres",
    "Healing Intake": "healin",
    "All Out": "dmgboost",
    "Physical Out": "physboost",
    "DoT Out": "dotboost",
    "Magical Out": "magicboost",
    "Healing Out": "healout",
    "Dodge Chance": "dodgechance",
    "Hit Chance": "hitchance",
    "Mana Consumption": "manaconsume",
    "Haste": "cooldown_reduction",
    "Crit Chance": "critchancce",
    "Crit Multiplier": "critmulti",
    "Attack Power": "aqwsword",
    "Spell Power": "magicboost",
    "Strength": "strength",
    "Intellect": "aqwwand",
    "Endurance": "endurance",
    "Dexterity": "aqwdagger",
    "Wisdom": "aqwstaff",
    "Luck": "luck",
}


class LevelModal(discord.ui.Modal, title="Class Model"):
    level = discord.ui.TextInput(
        label="Level", placeholder="1-100", default="100", max_length=3
    )

    def __init__(self, model: str, bot, class_data: dict | None = None):
        super().__init__()
        self.model = model
        self.bot = bot
        self.class_data = class_data

    async def on_submit(self, interaction: discord.Interaction):
        try:
            level = int(str(self.level.value).strip())
        except (ValueError, TypeError):
            await interaction.response.send_message(
                "Level must be a number between 1 and 100.", ephemeral=True
            )
            return
        if level < 1 or level > 100:
            await interaction.response.send_message(
                "Level must be between 1 and 100.", ephemeral=True
            )
            return
        data = await self.bot.get_conversion_data(self.model, level)
        if not data:
            await interaction.response.send_message(
                f"No conversion data found for model `{self.model}` at level `{level}`.",
                ephemeral=True,
            )
            return
        back = ClassView(self.class_data, self.bot) if self.class_data else None
        await interaction.response.edit_message(view=ConversionRateView(data, back))


class AurasView(discord.ui.LayoutView):
    def __init__(self, data: dict, bot=None):
        super().__init__()
        self.data = data
        self.bot = bot
        self.container = discord.ui.Container()
        action_row = discord.ui.ActionRow()

        back_button = discord.ui.Button(
            emoji=bem("backward"),
            style=discord.ButtonStyle.secondary,
            custom_id="back",
        )
        back_button.callback = self.back_callback
        action_row.add_item(back_button)

        action_row.add_item(
            discord.ui.Button(
                label="#passives",
                style=discord.ButtonStyle.primary,
                custom_id="forward",
                disabled=True,
                emoji=bem("aur"),
            )
        )
        self.add_item(self.container)
        self.container.add_item(action_row)

        self.container.add_item(
            discord.ui.TextDisplay(f"# {em('aur')} Passives")
        )
        self.container.add_item(discord.ui.Separator())
        passive_data = ""
        actions_passives = self.data["actions"]["passive"]

        for item, passive in zip_longest(data["auras"], actions_passives):
            name = passive["nam"]
            passive_data += f"### {name}\n"
            passive_data += f"*{passive['desc']}*\n\n"
            if item is not None:
                for e in item.get("e", []):
                    stat = e["sta"]
                    value = e["val"]
                    type = e["typ"]
                    stat = STAT_CODES.get(stat, stat)
                    type = type.replace("*", "×")
                    e = STAT_EMOJI.get(stat or "")
                    pre = f"{em(e)} " if e else ""
                    passive_data += f"{pre}**{stat}**: {value} ({type})\n"
            self.container.add_item(discord.ui.TextDisplay(passive_data))
            passive_data = ""

    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=ClassView(self.data, self.bot))


class SkillsView(discord.ui.LayoutView):
    def __init__(self, data: dict, current: int = 0, bot=None):
        super().__init__()
        self.data = data
        self.current = current
        self.bot = bot

        self.container = discord.ui.Container()
        action_row = discord.ui.ActionRow()

        back_button = discord.ui.Button(
            emoji=discord.PartialEmoji(name="backward", id=1545184111814119516), style=discord.ButtonStyle.secondary, custom_id="back"
        )
        back_button.callback = self.back_callback
        action_row.add_item(back_button)

        action_row.add_item(
            discord.ui.Button(
                label="#skills",
                style=discord.ButtonStyle.primary,
                custom_id="forward",
                disabled=True,
                emoji=bem("skills"),
            )
        )
        self.add_item(self.container)
        self.container.add_item(action_row)
        self.container.add_item(
            discord.ui.TextDisplay(f"# {em('skills')} Skills")
        )
        self.container.add_item(discord.ui.Separator())

        current_label = self.data["actions"]["active"][self.current]["nam"]

        self.skill_select = discord.ui.Select(
            placeholder=current_label,
            options=[
                discord.SelectOption(label=skill["nam"], value=str(i))
                for i, skill in enumerate(self.data["actions"]["active"])
                if skill["nam"] != "Potions"
            ],
        )
        self.skill_select.callback = self.skill_select_callback
        skill_data_json = self.data["actions"]["active"]
        current_skill = skill_data_json[self.current]
        skill_data = ""
        name = current_skill["nam"]
        if name != "Potions":
            description = current_skill["desc"]
            skill_data += f"### {name}\n*{description}*\n\n"
            self.container.add_item(discord.ui.Separator(visible=False))
            for k, v in current_skill.items():
                if k in [
                    "nam",
                    "desc",
                    "id",
                    "fx",
                    "anim",
                    "strl",
                    "isOK",
                    "icon",
                    "tgtMin",
                    "auras",
                ]:
                    continue

                skill_data += f"**{k}**: {v}\n"
            skill_data += "\n"
            self.container.add_item(discord.ui.TextDisplay(skill_data))
            self.container.add_item(discord.ui.Separator(visible=False))
            self.container.add_item(discord.ui.ActionRow(self.skill_select))

    async def skill_select_callback(self, interaction: discord.Interaction):
        print(self.skill_select.values[0], self.current)
        await interaction.response.edit_message(
            view=SkillsView(self.data, int(self.skill_select.values[0]), self.bot)
        )

    async def back_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=ClassView(self.data, self.bot))


class ClassView(discord.ui.LayoutView):
    def __init__(self, data: dict, bot=None):
        super().__init__()
        self.data = data
        self.bot = bot
        self.class_name = data["sClassName"]
        self.description = data["sDesc"]
        self.container = discord.ui.Container()
        self.add_item(self.container)
        self.container.add_item(
            discord.ui.TextDisplay(f"# {em('aqwclass')} {self.class_name}")
        )
        self.container.add_item(discord.ui.Separator())
        self.container.add_item(discord.ui.TextDisplay(f"*{self.description}*"))
        self.container.add_item(discord.ui.Separator(visible=False))

        auras_len = data["auras"]
        class_model = CLASS_CODES.get(data["sClassCat"], "Unknown")
        self.class_model = class_model
        mrm = "\n".join(data["aMRM"])
        self.container.add_item(
            discord.ui.TextDisplay(f"{em('lvl')} **Class Model**: {class_model}")
        )
        self.container.add_item(
            discord.ui.TextDisplay(
                f"{em('manaconsume')} **Mana Regen Model**: {mrm}"
            )
        )
        self.container.add_item(discord.ui.Separator(visible=False))

        auras = discord.ui.Button(
            label="View Auras",
            style=discord.ButtonStyle.primary,
            emoji=bem("aur"),
        )
        auras.callback = self.auras_callback
        self.container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    f"{em('aur')} **Auras**: {len(auras_len)}"
                ),
                accessory=auras,
            )
        )
        self.container.add_item(discord.ui.Separator(visible=False))

        actives_len = data["actions"]["active"]
        actives = discord.ui.Button(
            label="View Skills",
            style=discord.ButtonStyle.primary,
            emoji=bem("skills"),
        )
        actives.callback = self.actives_callback
        self.container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    f"{em('skills')} **Skills**: {len(actives_len) - 1}"
                ),
                accessory=actives,
            )
        )
        self.container.add_item(discord.ui.Separator(visible=False))

        rates = discord.ui.Button(
            label="View Model Distribution",
            style=discord.ButtonStyle.primary,
            emoji=bem("lvl"),
            disabled=class_model == "Unknown" or self.bot is None,
        )
        rates.callback = self.rates_callback
        self.container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay(f"{em('lvl')} **{class_model}**"),
                accessory=rates,
            )
        )
        self.container.add_item(discord.ui.Separator(visible=False))

    async def rates_callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            LevelModal(self.class_model, self.bot, self.data)
        )

    async def auras_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=AurasView(self.data, self.bot))

    async def actives_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=SkillsView(self.data, bot=self.bot)
        )


class ScrollView(discord.ui.LayoutView):
    def __init__(self, data):
        super().__init__()
        self.data = data

        name = data["name"]
        obj = data["o"]
        self.container = discord.ui.Container()
        self.add_item(self.container)
        title = discord.ui.TextDisplay(f"# {em('aur')} {name}")
        self.container.add_item(title)
        self.container.add_item(discord.ui.Separator(visible=True))
        text = ""
        for k, v in obj.items():
            if k in [
                "name",
                "desc",
                "id",
                "fx",
                "anim",
                "strl",
                "isOK",
                "icon",
                "tgtMin",
                "auras",
            ]:
                continue
            text += f"**{k}**: {v}\n"
        self.container.add_item(discord.ui.TextDisplay(text))
        self.container.add_item(discord.ui.Separator(visible=False))


class SearchResultsView(discord.ui.LayoutView):
    MAX_RESULTS = 25
    PAGE_SIZE = 8

    def __init__(
        self, results: list[dict], param: str, bot=None, current_page: int = 0
    ):
        super().__init__()
        self.results = results[: self.MAX_RESULTS]
        self.param = param
        self.bot = bot
        self.current_page = current_page
        self.total_pages = max(
            1,
            len(self.results) // self.PAGE_SIZE
            + (1 if len(self.results) % self.PAGE_SIZE else 0),
        )

        self.container = discord.ui.Container()
        self.add_item(self.container)

        start = self.current_page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        page_results = self.results[start:end]

        self.container.add_item(
            discord.ui.TextDisplay(
                f"# Search Results ({len(self.results)}) | Page {self.current_page + 1}/{self.total_pages}"
            )
        )
        self.container.add_item(discord.ui.Separator())

        for r in page_results:
            s = r["source"]
            n = r["name"]
            d = r["data"]
            pfx = "Class" if s == "class" else "Scroll"
            icon = em("aqwclass") if s == "class" else em("aur")
            matches = self._collect_matches(d, self.param)
            shown = matches[:5]
            text = f"{icon} **{pfx}: {n}** ({len(matches)} matches)"
            if shown:
                text += "\n" + "\n".join(f"`{m}`" for m in shown)
            if len(matches) > 5:
                text += f"\n*... and {len(matches) - 5} more*"
            view_btn = discord.ui.Button(
                label="View",
                style=discord.ButtonStyle.primary,
                emoji=bem("forward"),
            )
            view_btn.callback = self._make_view_callback(r)
            self.container.add_item(
                discord.ui.Section(discord.ui.TextDisplay(text), accessory=view_btn)
            )

        if self.total_pages > 1:
            action_row = discord.ui.ActionRow()
            back_btn = discord.ui.Button(
                label="",
                style=discord.ButtonStyle.secondary,
                emoji=discord.PartialEmoji(
                    name="backward",
                    id=1545184111814119516,
                ),
                custom_id="search_back",
                disabled=self.current_page == 0,
            )
            back_btn.callback = self._back_page
            action_row.add_item(back_btn)
            page_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label=f"Page {self.current_page + 1}/{self.total_pages}",
                disabled=True,
                custom_id="page_num",
            )
            action_row.add_item(page_btn)
            fwd_btn = discord.ui.Button(
                label="",
                style=discord.ButtonStyle.secondary,
                emoji=discord.PartialEmoji(
                    name="forward",
                    id=1545184113605218314,
                ),
                custom_id="search_fwd",
                disabled=self.current_page == self.total_pages - 1,
            )
            fwd_btn.callback = self._fwd_page
            action_row.add_item(fwd_btn)
            self.container.add_item(discord.ui.Separator())
            self.container.add_item(action_row)

    def _make_view_callback(self, r: dict):
        async def _view(interaction: discord.Interaction):
            if r["source"] == "class":
                await interaction.response.edit_message(
                    view=ClassView(r["data"], self.bot)
                )
            else:
                await interaction.response.edit_message(view=ScrollView(r["data"]))

        return _view

    async def _back_page(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=SearchResultsView(
                self.results, self.param, self.bot, self.current_page - 1
            )
        )

    async def _fwd_page(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            view=SearchResultsView(
                self.results, self.param, self.bot, self.current_page + 1
            )
        )

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


class ConversionRateView(discord.ui.LayoutView):
    def __init__(self, data: dict, back=None):
        super().__init__()
        self.data = data
        self.back = back
        model = data["model"]
        level = data["level"]
        self.model_data = data["data"]
        self.headers = data.get("headers", {})
        self.base_info = data.get("base_info", {})

        self.container = discord.ui.Container()
        self.add_item(self.container)

        if self.back is not None:
            action_row = discord.ui.ActionRow()
            back_btn = discord.ui.Button(
                emoji=discord.PartialEmoji(
                    name="backward",
                    id=1545184111814119516,
                ),
                style=discord.ButtonStyle.secondary,
                custom_id="conv_class_back",
            )
            back_btn.callback = self._back_callback
            action_row.add_item(back_btn)
            action_row.add_item(
                discord.ui.Button(
                    label="#rates",
                    style=discord.ButtonStyle.primary,
                    custom_id="conv_here",
                    disabled=True,
                )
            )
            self.container.add_item(action_row)

        self.container.add_item(
            discord.ui.TextDisplay(f"# {em('lvl')} Conversion Rates: {model} | Level {level}")
        )
        self.container.add_item(discord.ui.Separator())

        info = []
        if self.base_info.get("level_cap"):
            info.append(f"{em('lvl')} **Level Cap**: {self.base_info['level_cap']}")
        if info:
            self.container.add_item(discord.ui.TextDisplay(" · ".join(info)))
            self.container.add_item(discord.ui.Separator(visible=False))

        groups: dict[str, list[str]] = {}
        for col, val in self.model_data.items():
            h = self.headers.get(str(col), {})
            primary = h.get("primary", "?")
            secondary = h.get("secondary", f"Col {col}")
            groups.setdefault(primary, []).append(
                f"{sem(secondary)}**{secondary}**: {self._format_value(val)}"
            )

        for i, (primary, rows) in enumerate(groups.items()):
            p = PRIMARY_EMOJI.get(primary)
            head = f"{em(p)} " if p else ""
            self.container.add_item(
                discord.ui.TextDisplay(f"### {head}{primary}\n" + "\n".join(rows))
            )
            if i < len(groups) - 1:
                self.container.add_item(discord.ui.Separator())

    async def _back_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=self.back)

    @staticmethod
    def _format_value(val: str):
        try:
            f = float(val)
            if f == int(f) and abs(f) < 1000:
                return str(int(f))
            return str(round(f, 4))
        except (ValueError, TypeError):
            return val
