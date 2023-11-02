import discord
from discord.enums import ButtonStyle
from discord.interactions import Interaction
from discord.ui import View, TextInput, Modal, Button
from discord.ext.commands import Cog
from discord import ButtonStyle, TextStyle, ui
from JAS.resources import Buttons, Embeds, Selects
from JAS.resources.Exceptions import *
import JAS.resources.Connector as Conn

async def cancel_message(interaction:Interaction):
	await interaction.message.delete()
	# return await interaction.response.send_message(embed=Embeds.general('작업을 취소합니다.'), delete_after=5, ephemeral=True)

async def delete_message(interaction:Interaction):
	await interaction.response.defer()
	await interaction.message.delete()

timeout = 300

class templateView(View):
	def __init__(self):
		super().__init__(timeout=timeout)
		
	@ui.button(label="선택", style=ButtonStyle.primary, row=1)
	async def add_callback(self, interaction:Interaction, button):
		self.finish = True
		await delete_message(interaction)
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction:Interaction, button):
		self.stop()

class templateModal(Modal):
	def __init__(self):
		title = "제목"
		super().__init__(title=title, timeout=timeout)
		
		self.item = TextInput(
			label="제목", 
			placeholder="설명",
			max_length=100,
			required=True,
			)
		self.add_item(self.item)

	async def on_submit(self, interaction:Interaction) -> None:
		await interaction.response.defer()
		self.stop()

# 송금 뷰
class TransferView(View):
	def __init__(self):
		super().__init__(timeout=timeout)
		self.cancel = False
		# self.select = select.UserSelect(data)
		# self.add_item(self.select)

	@ui.button(label="송금",row=1)
	async def button_callback(self, interaction=discord.Interaction, button=Buttons):
		self.stop()
	
	@ui.button(label="취소", style=ButtonStyle.secondary,row=1)
	async def select_callback(self, interaction=Interaction, button=Buttons):
		self.cancel = True
		# await interaction.edit_original_response(embed=embed.general('작업을 취소합니다.'), delete_after=5)
		self.stop()

class ManageView(View):
	def __init__(self):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
	
	@ui.button(label="유저 관리", custom_id="User Management", row=0)
	async def user_manage_callback(self, interaction:Interaction, button):
		await interaction.response.defer()
		self.result="유저"
		self.stop()

	@ui.button(label="인벤토리 관리", custom_id="Inventory Management", row=1)
	async def inventory_manage_callback(self, interaction:Interaction, button):
		await interaction.response.defer()
		self.result="인벤토리"
		self.stop()

	@ui.button(label="스탯 관리", custom_id="Stat Management", row=1)
	async def inventory_manage_callback(self, interaction:Interaction, button):
		await interaction.response.defer()
		self.result="스탯"
		self.stop()
	
	# @ui.button(label="이벤트 관리", custom_id="Event Management", row=2)
	# async def event_manage_callback(self, interaction:Interaction, button):
	# 	await interaction.response.defer()
	# 	self.result="이벤트"
	# 	self.stop()
	
	@ui.button(label="시스템 관리", custom_id="System Management", row=3)
	async def system_manage_callback(self, interaction:Interaction, button):
		await interaction.response.defer()
		self.result="시스템"
		self.stop()
	
	@ui.button(label="취소", custom_id="cancel", row=4)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()

# sub Views
# 유저 관리 뷰
class UserManageView(View):
	def __init__(self):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.select = Selects.UserManageSelect()
		self.add_item(self.select)

	@ui.button(label="확인", style=ButtonStyle.primary, row=1)
	async def confirm_callback(self, interaction:Interaction, button):
		self.result = self.select.values[0]
		await interaction.response.defer()
		self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=1)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()
	
class UserInfo(View):
	def __init__(self, manage:Conn.Connector, data):
		self.result = None
		self.cancel = None
		self.manage = manage
		super().__init__(timeout=timeout)
		self.select_user = Selects.UserSelect(data)
		self.add_item(self.select_user)

	@ui.button(label="선택", style=ButtonStyle.primary, row=1)
	async def select_callback(self, interaction:Interaction, button):
		selected_user=self.select_user.values[0]
		id = int(selected_user.split(',')[0])
		await interaction.response.edit_message(embed=Embeds.show_user(self.manage, id), view=None)
		self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=1)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()

# 인벤토리 관리 뷰
class InventoryManageView(View):
	def __init__(self, manage:Conn.Connector):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.manage = manage
		self.select = Selects.InventoryManageSelect()
		self.add_item(self.select)

	@ui.button(label="확인", style=ButtonStyle.primary, row=1)
	async def confirm_callback(self, interaction:discord.Interaction, button):
		self.result =  self.select.values[0]
		await interaction.response.defer()
		self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=1)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()
		
class InventoryGoldChange(View):
	def __init__(self, manage:Conn.Connector, data):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.manage = manage
		self.data = data
		self.user = Selects.UserSelect(data)
		self.gold = Selects.InventoryGoldSelect()
		self.add_item(self.user)
		self.add_item(self.gold)

	@ui.button(label="확인", style=ButtonStyle.primary, row=2)
	async def confirm_callback(self, interaction:discord.Interaction, button):
		user = int(self.user.values[0])
		# name = list(filter(lambda x:x[0]==user, self.data))[0][1]
		code = self.manage.data.user.data[user].charas
		chara = self.manage.data.chara.data[code]
		name = chara.name
		gold = int(self.gold.values[0])
		self.manage.update_charactor_inventory(code=code, gold=gold)
		after_gold = self.manage.data.inventory.data[code].gold
		await interaction.response.edit_message(embed=Embeds.setting(f'{name}에게 G {gold}를 전달하였습니다', f'소지금액: {after_gold}'), view=None)
		self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=2)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()
		
class InventorySizeChange(View):
	def __init__(self, manage:Conn.Connector, data):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.manage = manage
		self.data = data
		self.user = Selects.UserSelect(data)
		self.size = Selects.InventorySizeSelect()
		self.add_item(self.user)
		self.add_item(self.size)

	@ui.button(label="확인", style=ButtonStyle.primary, row=2)
	async def confirm_callback(self, interaction:discord.Interaction, button):
		user = int(self.user.values[0])
		# name = list(filter(lambda x:x[0]==user, self.data))[0][1]
		code = self.manage.data.user.data[user].charas
		chara = self.manage.data.chara.data[code]
		name = chara.name
		size = int(self.size.values[0])
		self.manage.update_charactor_inventory(code=code, size=size)
		after_size = self.manage.data.inventory.data[code].size
		await interaction.response.edit_message(embed=Embeds.setting(f'{name}의 가방 공간이 {size} 변경 되었습니다.', f'가방크기: {after_size}'), view=None)
		self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=2)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()

# 스탯 관리 뷰
class StatManageView(View):
	def __init__(self, manage:Conn.Connector):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.manage = manage
		self.select = Selects.StatManageSelect()
		self.add_item(self.select)

	@ui.button(label="확인", style=ButtonStyle.primary, row=1)
	async def confirm_callback(self, interaction:Interaction, button):
		self.result = self.select.values[0]
		await interaction.response.defer()
		self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=1)
	async def cancel_callback(self, interaction, button):
		self.cancel=True
		await cancel_message(interaction)
		self.stop()

class StatNameChange(View):
	def __init__(self, manage:Conn.Connector):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.manage = manage

	@ui.button(label="확인", style=ButtonStyle.primary, row=1)
	async def confirm_callback(self, interaction:Interaction, button):
		modal = ChangeStatName(','.join(self.manage.data.setting.data.stat_names))
		await interaction.response.send_modal(modal)
		await modal.wait()
		if modal.finish:
			values = [name.strip() for name in modal.setting.value.split(',')]
			if len(values) != 6 and not (len(values) == 1 and not values[0]):
				for _ in range(len(values),6):
					values.append('-')
			value = ','.join(values)
			self.manage.update_stat_name(value)
			await interaction.followup.edit_message(interaction.message.id, embed=Embeds.setting('스탯 변경완료',f'변경된 스탯이 적용되었습니다.\n{value}'), view=None)
			self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=1)
	async def cancel_callback(self, interaction, button):
		self.cancel=True
		await cancel_message(interaction)
		self.stop()
		
class ChangeStatName(Modal):
	def __init__(self, default) -> None:
		self.finish = False
		super().__init__(title="스탯명 변경", timeout=timeout)

		self.setting = TextInput(
			label='스탯명\n쉼표로 구분하여 기입해 주세요',
			required=False,
			max_length=300,
			default=default
		)
		self.add_item(self.setting)
	
	async def on_submit(self, interaction:Interaction):
		self.finish = True
		await interaction.response.defer()
		

# 시스템 관리 뷰
class SystemManageView(View):
	def __init__(self):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.add_item(Selects.SystemManageSelect())

	@ui.button(label="확인", style=ButtonStyle.primary, row=1)
	async def confirm_callback(self, interaction:Interaction, button):
		self.result = self.children[2].values[0]
		await interaction.response.defer()
		self.stop()

	@ui.button(label="취소", style=ButtonStyle.secondary, row=1)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()

class RegView(View):
	def __init__(self, manage:Conn.Connector):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.manage = manage

	@ui.button(label="O")
	async def open_callback(self, interaction:Interaction, button):
		self.manage.__set_setting_value__("accept_user", "True")
		await interaction.response.edit_message(embed=Embeds.setting('회원가입을 허용합니다.'),view=None)
		self.stop()
	
	@ui.button(label="X")
	async def close_callback(self, interaction:Interaction, button):
		self.manage.__set_setting_value__("accept_user", "False")
		await interaction.response.edit_message(embed=Embeds.setting('회원가입을 차단합니다.'),view=None)
		self.stop()

class ChangeSettingView(View):
	def __init__(self, manage:Conn.Connector):
		self.result = None
		self.cancel = None
		super().__init__(timeout=timeout)
		self.manage = manage
		self.select = Selects.SettingValueSelect()
		self.add_item(self.select)

	@ui.button(label="확인", row=1)
	async def open_callback(self, interaction:Interaction, button):
		key = self.select.values[0]
		values = {
			"gspread_key":[self.manage.data.setting.data.gspread_key,'구글 연동 링크',2000],
			"max_fishing":[self.manage.data.setting.data.max_fishing,'최대 낚시 횟수',2],
			"max_gather":[self.manage.data.setting.data.max_gather,'최대 채집 횟수',2],
			"base_inv_size":[self.manage.data.setting.data.base_inv_size,'기본 인벤토리 크기',2],
			"base_inv_gold":[self.manage.data.setting.data.base_inv_gold,'기본 인벤토리 골드',2],
			"random_box":[self.manage.data.setting.data.random_box,'랜덤박스 비용',2],
		}
		default, label, max_length = values[key]
		modal = ChangeSetting(default, label, max_length)
		await interaction.response.send_modal(modal)
		await modal.wait()
		if modal.finish:
			await interaction.message.delete()
			# if key == 'gspread_key':
			# 	result = modal.setting.value
			# else:
			# 	result = int(modal.setting.value)
			self.manage.__set_setting_value__(key, modal.setting.value)
			await interaction.channel.send(embed=Embeds.show_system('설정 적용이 완료되었습니다.', self.manage.data.setting.data, '[관리 ▶ 시스템 ▶ 변경]'))
			self.stop()
	
	@ui.button(label="취소", row=1)
	async def close_callback(self, interaction:Interaction, button):
		self.cancel = True
		await interaction.response.defer()
		self.stop()

class ChangeSetting(Modal):
	def __init__(self, default, label, max_length) -> None:
		self.finish = False
		super().__init__(title="설정 변경", timeout=timeout)

		self.setting = TextInput(
			label=label,
			required=True,
			max_length=max_length,
			default=default
		)
		self.add_item(self.setting)
	
	async def on_submit(self, interaction:Interaction):
		self.finish = True
		await interaction.response.defer()

# 낚시
class FishingView(View):
	label = "label"
	style = ButtonStyle.secondary

	def __init__(self, hooked):
		super().__init__(timeout=1.5)
		self.hooked=hooked
		self.result = False
		if self.hooked:
			self.children[0].label = "지금이야!"
			self.children[0].style = ButtonStyle.primary
	
	@ui.button(label = "대기중...")
	async def callback(self, interaction, button):
		self.stop()
		self.result = True

class GetFishInfo(Modal):
	def __init__(self, data=None) -> None:
		title = "물고기 정보"
		super().__init__(title=title, timeout=timeout)

		self.desc = TextInput(
			label="물고기 설명", 
			placeholder="물고기에 대한 설명을 입력해 주세요",
			default=data.desc if data else None,
			style=TextStyle.paragraph,
			max_length=100,
			required=True,
			)
		self.min = TextInput(
			label="최소 길이", 
			placeholder="물고기의 최소 길이를 입력해 주세요",
			default=data.min if data else None,
			max_length=3,
			required=True,
			)
		self.max = TextInput(
			label="최대 길이", 
			placeholder="물고기의 최대 길이를 입력해 주세요",
			default=data.max if data else None,
			max_length=3,
			required=True
			)
		self.baseprice = TextInput(
			label="기본 가격", 
			placeholder="물고기가 팔릴 가격을 입력해 주세요",
			default=data.baseprice if data else None,
			max_length=20,
			min_length=1,
			required=True
			)
		self.loc = TextInput(
			label="등장위치(쉼표로 구분)", 
			placeholder="물고기가 등장할 낚시터 채널명을 입력해 주세요.",
			default=data.loc if data else None,
			required=True,
			max_length=20
			)
		self.add_item(self.desc)
		self.add_item(self.min)
		self.add_item(self.max)
		self.add_item(self.baseprice)
		self.add_item(self.loc)

	async def on_submit(self, interaction) -> None:
		await interaction.response.defer()
		self.stop()

class AddFishView(View):
	def __init__(self):
		super().__init__(timeout=timeout)
		self.cancel = False
		self.modal = GetFishInfo()

	@ui.button(label="추가", style=ButtonStyle.primary)
	async def add_callback(self, interaction, button):
		await interaction.message.delete()
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		self.stop()

	@ui.button(label="취소")
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class SelectFishView(View):
	def __init__(self, manage):
		super().__init__(timeout=timeout)
		self.fish = Selects.FishSelect(manage)
		self.add_item(self.fish)
		self.cancel = False
		
	@ui.button(label="선택", style=ButtonStyle.primary, row=1)
	async def add_callback(self, interaction:Interaction, button):
		await delete_message(interaction)
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()
	

class ChangeFishView(View):
	def __init__(self, data):
		super().__init__(timeout=timeout)
		self.modal = GetFishInfo(data)
		self.data = data
		self.cancel = False

	@ui.button(label="변경", style=ButtonStyle.primary)
	async def change_callback(self, interaction, button):
		await interaction.message.delete()
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		self.stop()

	@ui.button(label="취소")
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class ConfirmFishDelete(View):
	def __init__(self):
		self.cancel = False
		super().__init__(timeout=timeout)

	@ui.button(label="삭제", style=ButtonStyle.danger)
	async def delete_callback(self, interaction, button):
		await delete_message(interaction)
		self.stop()

	@ui.button(label="취소")
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

# 캐릭터
class CharaInfo(Modal):
	def __init__(self, title, data=None) -> None:
		self.finish = False
		super().__init__(title=title, timeout=timeout)

		self.name = TextInput(
			label="이름", 
			placeholder="캐릭터의 이름",
			default=data.name if data else None,
			required=True,
			max_length=20
			)
		self.keyword = TextInput(
			label="키워드(쉼표로 구분)", 
			placeholder="캐릭터를 나타내는 키워드를 입력해 주세요",
			default=data.keyword if data else None,
			style=TextStyle.paragraph,
			required=False,
			max_length=100
			)
		self.desc = TextInput(
			label="간단설명", 
			placeholder="캐릭터에 대한 간단한 설명 및 소개말",
			default=data.desc if data else None,
			style=TextStyle.paragraph,
			required=False,
			max_length=1000
			)
		self.link = TextInput(
			label="신청서 링크", 
			placeholder="신청서 링크",
			default=data.link if data else None,
			required=True,
			max_length=1000
			)
		self.add_item(self.name)
		self.add_item(self.keyword)
		self.add_item(self.desc)
		self.add_item(self.link)

	async def on_submit(self, interaction) -> None:
		self.finish = True
		await interaction.response.defer()
		self.stop()
	

class AddChara(View):
	def __init__(self):
		title = f'캐릭터 정보'
		self.info = CharaInfo(title)
		self.cancel = False
		super().__init__(timeout=timeout)

	@ui.button(label="등록", style=ButtonStyle.primary)
	async def add_callback(self, interaction:discord.Interaction, button):
		await interaction.message.delete()
		await interaction.response.send_modal(self.info)

	@ui.button(label="취소")
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class ChangeChara(View):
	def __init__(self, name, data):
		self.cancel = False
		title = f'{name}를 변경합니다.'
		self.info = CharaInfo(title, data)
		super().__init__(timeout=timeout)

	@ui.button(label="변경", style=ButtonStyle.primary)
	async def add_callback(self, interaction:discord.Interaction, button):
		await interaction.message.delete()
		await interaction.response.send_modal(self.info)	
		await self.info.wait()
		self.stop()

	@ui.button(label="취소")
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class RemoveChara(View):
	def __init__(self, name):
		self.name = name
		self.delete = False
		self.cancel = False
		super().__init__(timeout=timeout)

	@ui.button(label="삭제", style=ButtonStyle.danger)
	async def add_callback(self, interaction:discord.Interaction, button):
		self.delete = True
		await interaction.response.edit_message(embed=Embeds.setting(f"{self.name}을/를 삭제하였습니다."), view=None)
		self.stop()

	@ui.button(label="취소")
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class NPCInfo(Modal):
	def __init__(self, data:Conn.NPC=None) -> None:
		title = "NPC 정보"
		self.finish=False
		self.data = data
		vers_placeholder = '(상황)/(대사) 와 같은 형식으로 기입해 주세요'
		super().__init__(title=title, timeout=timeout)

		self.name = TextInput(
			label="NPC 이름",
			default=data.name if data else '',
			required=True,
			max_length=20
		)
		self.vers1 = TextInput(
			label="캐릭터의 대사1",
			style=TextStyle.paragraph,
			default='' if not data else data.case.split(',')[0]+'/'+data.vers[0] if data.number>=0 else '',
			placeholder=vers_placeholder,
			max_length=500
		)
		self.vers2 = TextInput(
			label="캐릭터의 대사2",
			style=TextStyle.paragraph,
			default='' if not data else data.case.split(',')[1]+'/'+data.vers[1] if data.number>=1 else '',
			placeholder=vers_placeholder,
			required=False,
			max_length=500
		)
		self.vers3 = TextInput(
			label="캐릭터의 대사3",
			style=TextStyle.paragraph,
			default='' if not data else data.case.split(',')[2]+'/'+data.vers[2] if data.number>=2 else '',
			placeholder=vers_placeholder,
			required=False,
			max_length=500
		)
		self.vers4 = TextInput(
			label="캐릭터의 대사4",
			style=TextStyle.paragraph,
			default='' if not data else data.case.split(',')[3]+'/'+data.vers[3] if data.number>=3 else '',
			placeholder=vers_placeholder,
			required=False,
			max_length=500
		)
		self.add_item(self.name)
		self.add_item(self.vers1)
		self.add_item(self.vers2)
		self.add_item(self.vers3)
		self.add_item(self.vers4)
	
	async def on_submit(self, interaction:Interaction):
		self.finish = True
		await interaction.response.defer()
		self.stop()

class AddNPC(View):
	def __init__(self):
		title = f'캐릭터 정보'
		self.info = CharaInfo(title)
		self.cancel = False
		super().__init__(timeout=timeout)

	@ui.button(label="등록", style=ButtonStyle.primary)
	async def add_callback(self, interaction:discord.Interaction, button):
		await interaction.message.delete()
		await interaction.response.send_modal(self.info)
		await self.info.wait()
		self.stop()

	@ui.button(label="취소")
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class UpdateNPC(View):
	def __init__(self, npc_list, npc_data):
		self.cancel = False
		self.data = npc_data
		self.select = Selects.NPCSelect(npc_list)
		super().__init__(timeout=timeout)
		self.add_item(self.select)

	@ui.button(label="선택", style=ButtonStyle.primary, row=1)
	async def add_callback(self, interaction:discord.Interaction, button):
		await interaction.message.delete()
		self.modal = NPCInfo(self.data[self.select.values[0]])
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		if not self.modal.finish:
			self.cancel = True
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction:discord.Interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class RemoveNPC(View):
	def __init__(self, npc_list):
		self.cancel = False
		self.select = Selects.NPCSelect(npc_list)
		super().__init__(timeout=timeout)
		self.add_item(self.select)

	@ui.button(label="삭제", style=ButtonStyle.danger, row=1)
	async def add_callback(self, interaction:discord.Interaction, button):
		await interaction.message.delete()
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction:discord.Interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class SelectNPC(View):
	def __init__(self, npc_list):
		self.cancel = False
		self.select = Selects.NPCSelect(npc_list)
		super().__init__(timeout=timeout)
		self.add_item(self.select)

	@ui.button(label="선택", style=ButtonStyle.primary, row=1)
	async def add_callback(self, interaction:discord.Interaction, button):
		await interaction.message.delete()
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction:discord.Interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class CharaColor(View):
	def __init__(self):
		self.finish = False
		super().__init__(timeout=300)
		self.select = Selects.ColorSelect()
		self.add_item(self.select)
		
	@ui.button(label="선택", style=ButtonStyle.primary, row=1)
	async def finish_callback(self, interaction:Interaction, button):
		self.finish = True
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction, button):
		self.stop()

# 인벤토리
class SpawnItem(View):
	def __init__(self, items):
		self.cancel = False
		super().__init__(timeout=timeout)
		self.select = Selects.ItemSelect(items)
		self.add_item(self.select)

	@ui.button(label="부여", style=ButtonStyle.primary, row=1)
	async def confirm_callback(self, interaction:Interaction, button):
		await delete_message(interaction)
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

class SoldItemView(View):
	def __init__(self, data, items):
		self.cancel = False
		super().__init__(timeout=timeout)
		self.select = Selects.InventoryItemSelect(data, items)
		self.add_item(self.select)
	
	@ui.button(label="판매", style=ButtonStyle.primary, row=1)
	async def buy_callback(self, interaction:Interaction, button:Button):
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction:Interaction, button):
		self.cancel = True
		self.stop()

# 스탯
class SpendStat(View):
	def __init__(self, user:discord.Member):
		self.cancel = False
		self.finish = False
		self.user_id = user.id
		super().__init__(timeout=timeout)

	@ui.button(label="적용", style=ButtonStyle.primary, row=1)
	async def add_callback(self, interaction:discord.Interaction, button):
		if self.user_id != interaction.user.id:
			return await interaction.response.send_message('스탯은 본인만 조정할 수 있습니다', ephemeral=True)
		self.finish = True
		await interaction.response.defer()
		self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction:discord.Interaction, button):
		if self.user_id != interaction.user.id:
			return await interaction.response.send_message('스탯은 본인만 조정할 수 있습니다', ephemeral=True)
		self.cancel = True
		await cancel_message(interaction)
		self.stop()
			
class AllStat(View):
	def __init__(self, type, data:Conn.Stat, user:discord.Member):
		super().__init__(timeout=timeout)
		self.user_id = user.id
		self.point = data.point
		if type == 1:
			self.stat1_origin = data.stat1
			self.stat1_value = data.stat1
			self.stat2_origin = data.stat2
			self.stat2_value = data.stat2
			self.stat3_origin = data.stat3
			self.stat3_value = data.stat3
			self.stat1_sub = Buttons.sub_stat(0, user)
			self.stat1_current = Buttons.current_stat(data.stat_names[0], self.stat1_value,0)
			self.stat1_add = Buttons.add_stat(0, user)
			self.stat2_sub = Buttons.sub_stat(1, user)
			self.stat2_current = Buttons.current_stat(data.stat_names[1],self.stat2_value,1)
			self.stat2_add = Buttons.add_stat(1, user)
			self.stat3_sub = Buttons.sub_stat(2, user)
			self.stat3_current = Buttons.current_stat(data.stat_names[2],self.stat3_value,2)
			self.stat3_add = Buttons.add_stat(2, user)
			if self.stat1_origin==self.stat1_value:
				self.stat1_sub.disabled=True
			if self.stat2_origin==self.stat2_value:
				self.stat2_sub.disabled=True
			if self.stat3_origin==self.stat3_value:
				self.stat3_sub.disabled=True
			if self.point==0:
				self.stat1_add.disabled=True
				self.stat2_add.disabled=True
				self.stat3_add.disabled=True
			self.add_item(self.stat1_sub)
			self.add_item(self.stat1_current)
			self.add_item(self.stat1_add)
			self.add_item(self.stat2_sub)
			self.add_item(self.stat2_current)
			self.add_item(self.stat2_add)
			self.add_item(self.stat3_sub)
			self.add_item(self.stat3_current)
			self.add_item(self.stat3_add)
		elif type == 2:
			self.stat4_origin = data.stat4
			self.stat4_value = data.stat4
			self.stat5_origin = data.stat5
			self.stat5_value = data.stat5
			self.stat6_origin = data.stat6
			self.stat6_value = data.stat6
			self.stat4_sub = Buttons.sub_stat(0, user)
			self.stat4_current = Buttons.current_stat(data.stat_names[3], self.stat4_value,0)
			self.stat4_add = Buttons.add_stat(0, user)
			self.stat5_sub = Buttons.sub_stat(1, user)
			self.stat5_current = Buttons.current_stat(data.stat_names[4],self.stat5_value,1)
			self.stat5_add = Buttons.add_stat(1, user)
			self.stat6_sub = Buttons.sub_stat(2, user)
			self.stat6_current = Buttons.current_stat(data.stat_names[5],self.stat6_value,2)
			self.stat6_add = Buttons.add_stat(2, user)
			if self.stat4_origin==self.stat4_value:
				self.stat4_sub.disabled=True
			if self.stat5_origin==self.stat5_value:
				self.stat5_sub.disabled=True
			if self.stat6_origin==self.stat6_value:
				self.stat6_sub.disabled=True
			if self.point==0:
				self.stat4_add.disabled=True
				self.stat5_add.disabled=True
				self.stat6_add.disabled=True
			self.add_item(self.stat4_sub)
			self.add_item(self.stat4_current)
			self.add_item(self.stat4_add)
			self.add_item(self.stat5_sub)
			self.add_item(self.stat5_current)
			self.add_item(self.stat5_add)
			self.add_item(self.stat6_sub)
			self.add_item(self.stat6_current)
			self.add_item(self.stat6_add)
		elif type == 3:
			self.stat1_origin = data.stat1
			self.stat1_value = data.stat1
			self.stat2_origin = data.stat2
			self.stat2_value = data.stat2
			self.stat3_origin = data.stat3
			self.stat3_value = data.stat3
			self.stat4_origin = data.stat4
			self.stat4_value = data.stat4
			self.stat5_origin = data.stat5
			self.stat5_value = data.stat5
			self.stat1_sub = Buttons.sub_stat(0, user)
			self.stat1_current = Buttons.current_stat(data.stat_names[0], self.stat1_value,0)
			self.stat1_add = Buttons.add_stat(0, user)
			self.stat2_sub = Buttons.sub_stat(1, user)
			self.stat2_current = Buttons.current_stat(data.stat_names[1],self.stat2_value,1)
			self.stat2_add = Buttons.add_stat(1, user)
			self.stat3_sub = Buttons.sub_stat(2, user)
			self.stat3_current = Buttons.current_stat(data.stat_names[2],self.stat3_value,2)
			self.stat3_add = Buttons.add_stat(2, user)
			self.stat4_sub = Buttons.sub_stat(0, user)
			self.stat4_current = Buttons.current_stat(data.stat_names[3], self.stat4_value,0)
			self.stat4_add = Buttons.add_stat(0, user)
			self.stat5_sub = Buttons.sub_stat(1, user)
			self.stat5_current = Buttons.current_stat(data.stat_names[4],self.stat5_value,1)
			self.stat5_add = Buttons.add_stat(1, user)
			if self.stat1_origin==self.stat1_value:
				self.stat1_sub.disabled=True
			if self.stat2_origin==self.stat2_value:
				self.stat2_sub.disabled=True
			if self.stat3_origin==self.stat3_value:
				self.stat3_sub.disabled=True
			if self.stat4_origin==self.stat4_value:
				self.stat4_sub.disabled=True
			if self.stat5_origin==self.stat5_value:
				self.stat5_sub.disabled=True
			if self.point==0:
				self.stat1_add.disabled=True
				self.stat2_add.disabled=True
				self.stat3_add.disabled=True
				self.stat4_add.disabled=True
				self.stat5_add.disabled=True
			self.add_item(self.stat1_sub)
			self.add_item(self.stat1_current)
			self.add_item(self.stat1_add)
			self.add_item(self.stat2_sub)
			self.add_item(self.stat2_current)
			self.add_item(self.stat2_add)
			self.add_item(self.stat3_sub)
			self.add_item(self.stat3_current)
			self.add_item(self.stat3_add)
			self.add_item(self.stat4_sub)
			self.add_item(self.stat4_current)
			self.add_item(self.stat4_add)
			self.add_item(self.stat5_sub)
			self.add_item(self.stat5_current)
			self.add_item(self.stat5_add)

class Ticket(View):
	def __init__(self, data):
		self.cancel = False
		super().__init__(timeout=timeout)
		self.modal = self.Response(data)

	@ui.button(label="답변", style=ButtonStyle.primary, row=1)
	async def add_callback(self, interaction:discord.Interaction, button):
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		if self.modal.finish:
			await interaction.message.edit(view = None)
			self.stop()

	@ui.button(label="취소", row=1)
	async def cancel_callback(self, interaction, button):
		self.cancel = True
		await cancel_message(interaction)
		self.stop()

	class Response(Modal):
		def __init__(self, data=None) -> None:
			self.finish = False
			title = "답변 작성"
			super().__init__(title=title, timeout=timeout)

			self.question = TextInput(
				label="질문내용",
				default=data,
				style=TextStyle.paragraph,
			)
			self.content = TextInput(
				label="답변", 
				placeholder="질문에 대한 답변",
				style=TextStyle.paragraph,
				required=True,
				max_length=1000
				)
			self.add_item(self.question)
			self.add_item(self.content)

		async def on_submit(self, interaction:Interaction) -> None:
			await interaction.response.defer()
			self.finish = True
			self.stop()