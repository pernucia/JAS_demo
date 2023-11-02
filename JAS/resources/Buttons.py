from typing import Optional, Union
from discord.emoji import Emoji
from discord.partial_emoji import PartialEmoji
from discord.ui import Button
from discord.ext import commands
from discord import ButtonStyle, Interaction

class TransferButton(Button):
    def __init__(self):
        super().__init__(label="송금", style=ButtonStyle.primary, row=1)

class cancel(Button):
    def __init__(self, row=None):
        super().__init__(label="취소", style=ButtonStyle.secondary, row=row)

    async def callback(self, Interaction):
        await Interaction.response.send_message('작업을 취소합니다.')

class sub_stat(Button):
    def __init__(self, row, user):
        self.clicked=False
        self.user_id = user.id
        super().__init__(label="-", style=ButtonStyle.red, row=row)

    async def callback(self, interaction:Interaction):
        if self.user_id != interaction.user.id:
            return await interaction.response.send_message('스탯은 본인만 조정할 수 있습니다', ephemeral=True)
        print("sub button click")
        await interaction.response.defer()
        self.clicked=True

class add_stat(Button):
    def __init__(self, row, user):
        self.clicked=False
        self.user_id = user.id
        super().__init__(label="+", style=ButtonStyle.green, row=row)

    async def callback(self, interaction:Interaction):
        if self.user_id != interaction.user.id:
            return await interaction.response.send_message('스탯은 본인만 조정할 수 있습니다', ephemeral=True)
        print("add button click")
        await interaction.response.defer()
        self.clicked=True

class current_stat(Button):
    def __init__(self, name, stat, row=0):
        super().__init__(label=f'{name} : {stat}', style=ButtonStyle.secondary, row=row, disabled=True)

    async def callback(self, interaction:Interaction): ...
