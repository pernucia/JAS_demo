import discord
from discord import Interaction
from discord.components import SelectOption
from discord.interactions import Interaction
from discord.ui import Select

class UserSelect(Select):
    def __init__(self, data):
        options = self.options(data)
        super().__init__(placeholder="대상을 선택해 주세요", options=options, row=0)
    
    def options(self, data):
        options = []
        for user in data:
            label = user[1]
            value = user[0]
            option = discord.SelectOption(label=label, value=value)
            options.append(option)
        return options

    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()
    
class UserManageSelect(Select):
    def __init__(self):
        menus = {"유저 정보":"유저정보 확인"}
        options = []
        for i in menus.keys():
            label = menus[i]
            option = SelectOption(label=label, value=i)
            options.append(option)

        super().__init__(options=options)
        
    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()
        
class InventoryManageSelect(Select):
    def __init__(self):
        menus = {"인벤토리 골드":"유저 골드 추가", "인벤토리 크기":"인벤토리 크기 조정"}
        options = []
        for i in menus.keys():
            label = menus[i]
            option = SelectOption(label=label, value=i)
            options.append(option)

        super().__init__(options=options)
        
    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()
        
class InventoryGoldSelect(Select):
    def __init__(self):
        placeholder = "지급할 금액을 선택해 주세요"

        options = []
        for i in range(20,-21, -5):
            if i != 0:
              label = str(i)
              option = SelectOption(label=label, value=i)
              options.append(option)

        super().__init__(options=options, placeholder=placeholder, row=1)
        
    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()

class InventorySizeSelect(Select):
    def __init__(self):
        placeholder = "변경할 인벤토리 크기를 선택해 주세요"

        options = []
        for i in range(5,-6, -1):
            if i != 0:
              label = str(i)
              option = SelectOption(label=label, value=i)
              options.append(option)

        super().__init__(options=options, placeholder=placeholder, row=1)
        
    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()

class StatManageSelect(Select):
    def __init__(self):
        menus = {"스탯 변경":"스탯명 변경", }
        options = []
        for i in menus.keys():
            label = menus[i]
            option = SelectOption(label=label, value=i)
            options.append(option)

        super().__init__(options=options)
        
    async def callback(self, interaction:Interaction):
        print(self.values)
        await interaction.response.defer()
        
class SystemManageSelect(Select):
    def __init__(self):
        menus = {"시스템 확인":"설정확인", "시스템 회원가입":"화원가입 허용 여부 변경", "시스템 변경":"기본수치 변경"}
        options = []
        for i in menus.keys():
            label = menus[i]
            option = SelectOption(label=label, value=i)
            options.append(option)

        super().__init__(options=options)
        
    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()

class ValueChange(Select):
    def __init__(self, type, manage):
        if type == 1:
            placeholder = "최대 낚시 횟수"
            base=manage.max_fishing
            valuerange = range(1,11)
        elif type == 2:
            placeholder = "최대 수집 횟수"
            base=manage.max_gather
            valuerange = range(1,11)
        elif type == 3:
            placeholder = "기본 가방 크기"
            base=manage.base_inv_size
            valuerange = range(5,21,5)
        elif type == 4:
            placeholder = "최초 소지 골드"
            base=manage.base_inv_gold
            valuerange = range(5,31,5)

        options = []
        for i in valuerange:
            label = str(i)
            default = True if i == base else False
            option = SelectOption(label=label, default=default)
            options.append(option)

        super().__init__(options=options, placeholder=placeholder)
        
    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()

class SettingValueSelect(Select):
    def __init__(self):
        placeholder = '변경하고자 하는 항목을 선택해 주세요.'
        options = self.options()
        super().__init__(placeholder=placeholder, options=options, row=0)

    def options(self):
        data = [
            ['구글 연동 링크','gspread_key','DB 데이터가 연동될 구글 스프레드 시트 링크'],
            ['최대 낚시 횟수','max_fishing','하루에 최대로 낚시 가능한 기본 횟수'],
            ['최대 채집 횟수','max_gather','하루에 최대로 채집 가능한 기본 횟수'],
            ['기본 가방 크기','base_inv_size','캐릭터 생성시 부여받게되는 기본 인벤토리 크기'],
            ['최초 소지 골드','base_inv_gold','캐릭터 생성시 부여받게되는 기본 골드'],
            ['랜덤 박스 가격','random_box','랜덤 박스 가격'],
        ]

        options = []
        for item in data:
          options.append(SelectOption(label=item[0], value=item[1], description=item[2]))
        return options

    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()

# NPC 선택
class NPCSelect(Select):
    def __init__(self, data) -> None:
        placeholder = 'NPC를 선택해 주세요'
        options = self.options(data)
        super().__init__(placeholder=placeholder, options=options, row=0)

    def options(self, data):
        options = []
        for item in data:
          options.append(SelectOption(label=item[0], value=item[1]))
        return options

    async def callback(self, interaction:Interaction):
        print(self.values)
        await interaction.response.defer()
    
# 물고기 선택
class FishSelect(Select):
    def __init__(self, manage) -> None:
        self.manage = manage
        placeholder = "물고기를 선택해 주세요."
        options = self.get_options()
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, row=0)

    def get_options(self):
        options = []
        for fish in list(self.manage.keys()):
            label = self.manage[fish].name
            code = fish
            options.append(SelectOption(label=label, value=code))
        return options
    
    async def callback(self, interaction):
        print(self.values)
        await interaction.response.defer()

# 인벤토리 아이템 선택
class InventoryItemSelect(Select):
    def __init__(self, data, items, count=None) -> None:
        placeholder = "아이템을 선택해 주세요"
        options = self.options(data, items)
        max_values = count or len(data)
        super().__init__(placeholder=placeholder, min_values=1, max_values=max_values, options=options, row=0)
    
    def options(self, data:dict, items):
        options = []
        for item in data:
            label = items[item].name
            value = item
            desc = f'{items[item].price} {items[item].desc}'
            option = SelectOption(label=label,value=value,description=desc)
            options.append(option)
        return options

    async def callback(self, interaction: Interaction) -> any:
        print(self.values)
        await interaction.response.defer()

# 전체 아이템 선택
class ItemSelect(Select):
    def __init__(self, items) -> None:
        placeholder = "아이템을 선택해 주세요"
        options = self.options(items)
        max_values = 5
        super().__init__(placeholder=placeholder, min_values=1, max_values=max_values, options=options, row=0)
    
    def options(self, items):
        options = []
        print(items)
        for item in items:
            if "_" in item:
                continue
            label = items[item].name
            value = item
            desc = f'{items[item].price} {items[item].desc}'
            option = SelectOption(label=label,value=value,description=desc)
            options.append(option)
        return options

    async def callback(self, interaction: Interaction) -> any:
        print(self.values)
        await interaction.response.defer()

# 색상 선택
class ColorSelect(Select):
    def __init__(self):
        placeholder = "원하는 색상을 선택해 주세요"
        options = self.options()
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, row=0)
    
    def options(self):
        return [
            SelectOption(label="teal",value=discord.Color.teal().value),
            SelectOption(label="dark_teal",value=discord.Color.dark_teal().value),
            SelectOption(label="brand_green",value=discord.Color.brand_green().value),
            SelectOption(label="green",value=discord.Color.green().value),
            SelectOption(label="dark_green",value=discord.Color.dark_green().value),
            SelectOption(label="blue",value=discord.Color.blue().value),
            SelectOption(label="purple",value=discord.Color.purple().value),
            SelectOption(label="dark_purple",value=discord.Color.dark_purple().value),
            SelectOption(label="magenta",value=discord.Color.magenta().value),
            SelectOption(label="dark_magenta",value=discord.Color.dark_magenta().value),
            SelectOption(label="gold",value=discord.Color.gold().value),
            SelectOption(label="dark_gold",value=discord.Color.dark_gold().value),
            SelectOption(label="orange",value=discord.Color.orange().value),
            SelectOption(label="dark_orange",value=discord.Color.dark_orange().value),
            SelectOption(label="brand_red",value=discord.Color.brand_red().value),
            SelectOption(label="lighter_grey",value=discord.Color.lighter_grey().value),
            SelectOption(label="dark_grey",value=discord.Color.dark_grey().value),
            SelectOption(label="light_grey",value=discord.Color.light_grey().value),
            SelectOption(label="darker_grey",value=discord.Color.darker_grey().value),
            SelectOption(label="og_blurple",value=discord.Color.og_blurple().value),
            SelectOption(label="blurple",value=discord.Color.blurple().value),
            SelectOption(label="greyple",value=discord.Color.greyple().value),
            SelectOption(label="fuchsia",value=discord.Color.fuchsia().value),
            SelectOption(label="yellow",value=discord.Color.yellow().value),
            SelectOption(label="pink",value=discord.Color.pink().value),
        ]

    async def callback(self, interaction: Interaction) -> any:
        print(self.values[0])
        await interaction.response.defer()
        # color = discord.Color(int(self.values[0]))
        # emb = discord.Embed(title='원하시는 색상을 선택해 주세요',color=color)
        # await interaction.edit_original_response(embed=emb)
