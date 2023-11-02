import discord
from discord import Color, Member
from JAS.resources.Exceptions import *
from JAS.resources.Base import commands, app_commands, CommandBase, AppCommandBase, Embeds, Views
from JAS.resources.Addons import key_gen
from math import floor
from random import choice, randrange, random
from time import strftime,localtime
from asyncio import sleep
from copy import deepcopy

class Fishing(CommandBase):
	def check_fishing_limit(self, user_id, channel):
		max_count = self.setting.max_fishing
		date = strftime('%Y-%m-%d',localtime())
		fishing_count = self.connector.get_fishing_history(user_id, channel, date)
		if fishing_count >= max_count:
			raise FishingLimit('낚시 횟수가 초과되었습니다')

	def fishing(self, fish_list, loc, user_id):
		grades = {
			"초라함": 0.5,
			"일반": 1,
			"희귀": 1.8,
			"전설": 3,
			"경이": 5
		}

		fishcode = choice(fish_list)
		fish = self.fishes[fishcode]
		print(fish)

		name = fish.name
		dice = randrange(1,101)
		print(dice)
		grade = "경이" if dice < 2 else "전설" if dice < 11 else "희귀" if dice < 31 else "일반" if dice < 91 else "초라함"
		num = 1
		length = round(randrange(fish.min, fish.max)+random(),2)
		price = floor(length/(fish.min+fish.max)*2*fish.baseprice*grades[grade])
		great = bool(length>(fish.max*0.8))
		itemcode = f'{fishcode}-{num}-{str(random())[2:]}'

		now = strftime('%Y-%m-%d %H:%M:%S',localtime())
		self.connector.set_fishing_history(now, user_id, str(loc), name, length)
		print('history logging success')
		
		desc = self.items[fishcode].desc
		code = self.user[user_id].charas
		chara_name = self.charas[code].name
		if len(self.invs[code].items) <= self.invs[code].size:
			self.connector.reg_item(itemcode, name, desc, num, price)
			self.connector.store_item(code, itemcode, num)
			title = "🎉월척이오!!!!!" if great else "🎣낚시 성공!"
			desc = f'{chara_name}님이 {name}을 낚았습니다.'
			color = Color.gold() if great or grade == "경이" else Color.green() if grade != "초라함" else Color.dark_grey()
			data = (grade, f'{length} cm', f'G {price}')
		else:
			self.connector.add_gold(code, price)
			print('set gold success')
			desc=f'가방이 꽉 차 담을 수 없었습니다...\n{chara_name}은/는 G{price}를 얻었습니다.'
			color = Color.dark_grey()
			data = (grade, f'{length} cm', f'G {price}')
		return (title, desc, color, data)
		
	@app_commands.command(name="낚시", description="낚시터에서 물고기를 낚습니다.")
	async def fishing_slash(self, interaction:discord.Interaction):
		"""
		낚시터에서 낚시를 합니다.
		"""
		loc = interaction.channel
		user_id = interaction.user.id
		await self.on_ready(interaction)
		
		try:			
			await interaction.response.send_message(embed=Embeds.general("낚시를 시작합니다.",None,Color.green()), ephemeral=True)
			print("check fishing limit")
			self.check_fishing_limit(user_id, loc)

			try:
				fish_list = self.fish_data[str(loc)]
			except:
				raise IncorrectPlace('올바른 낚시터가 아닙니다.')
			wait_time = randrange(4,10)
			print(f'대기시간: {wait_time}')
			await interaction.edit_original_response(embed=Embeds.fishing(0))
			await sleep(1)
			for i in range(wait_time+1):
				fishingview = Views.FishingView(False)
				if i == wait_time:
					fishingview = Views.FishingView(True)
					type = 9
				elif i < 2:
					type = i
				else:
					type = randrange(2,5)
				await interaction.edit_original_response(embed=Embeds.fishing(type), view=fishingview)
				await fishingview.wait()
				if fishingview.result:
					break
			
			# 낚시 버튼 클릭한 경우
			if fishingview.result:
				if fishingview.hooked:
					# 낚시에 성공한 경우
					title, desc, color, data = self.fishing(fish_list, loc, user_id)
				else:
					# 낚시에 실패한 경우
					title = "낚시 실패"
					desc = "너무 일찍 당겨버렸다..."
					color=Color.dark_grey()
					data = None
			else:
				title = "낚시 실패..."
				desc = "물고기가 미끼를 먹고 유유히 사라졌다..."
				color = Color.dark_grey()
				data = None
			embeded = Embeds.fishing_result(title, desc, color, data)
			await interaction.delete_original_response()
			await interaction.channel.send(embed=embeded, view=None)
		except FishingLimit as e:
			print(e)
			print('>> Error: exceed fishing limit')
			print(traceback.format_exc())
			title = '더이상 고기를 낚을 수 없을것 같습니다…'
			desc = None
			color = Color.brand_red()
			data = None
			embeded = Embeds.fishing_result(title, desc, color, data)
			await interaction.edit_original_response(embed=embeded, view=None)
		except SellingError as e:
			print(e)
			print('>> Error: inventory error accured')
			print(traceback.format_exc())
			title = "물고기 판매 도중 오류가 발생하였습니다."
			desc = "다시 시도해 주시기 바랍니다"
			color = Color.red()
			data = None
			embeded = Embeds.fishing_result(title, desc, color, data)
			await interaction.edit_original_response(embed=embeded, view=None)
		except FishingError as e:
			print(e)
			print('>> Error: fishing error accured')
			print(traceback.format_exc())
			title = "낚시 도중 오류가 발생하였습니다."
			desc = "다시 시도해 주시기 바랍니다"
			color = Color.red()
			data = None
			embeded = Embeds.fishing_result(title, desc, color, data)
			await interaction.edit_original_response(embed=embeded, view=None)
		except IncorrectPlace as e:
			print(e)
			print('>> Error: incorrect place')
			print(traceback.format_exc())
			title = "올바른 낚시터가 아닙니다"
			desc = "다른 곳을 찾아가 보세요"
			color = Color.yellow()
			data = None
			embeded = Embeds.fishing_result(title, desc, color, data)
			await interaction.edit_original_response(embed=embeded, view=None)
		except Exception as e:
			print(e)
			print('>> Error: Unkown Error')
			print(traceback.format_exc())
			title = '예상치 못한 오류가 발생하였습니다.'
			desc = '지속적으로 발생할 경우 관리자에게 문의 바랍니다.'
			color = Color.red()
			data = None
			embeded = Embeds.fishing_result(title, desc, color, data)
			await interaction.edit_original_response(embed=embeded, view=None)

	@app_commands.command(name="물고기목록", description="낚시터의 물고기 목록을 확인한다.")
	@app_commands.rename(loc="낚시터")
	@app_commands.describe(loc="지정된 낚시터. 입력할 경우 해당 낚시터의 물고기만 확인가능하다.")
	async def 물고기목록(self, interaction:discord.Interaction, 
		 loc:discord.TextChannel=None):
		"""
		현재 낚시 가능한 물고기 목록을 확인합니다.
		낚시터 명을 입력할 경우 해당 낚시터의 목록만 확인 가능합니다.
		"""
		await self.on_ready(interaction)
		try:
			if loc:
				try:
					data = {}
					data[loc.name] = self.fish_data[loc.name]
					title = f"{loc.name}에서 발견 가능한 물고기 입니다."
					await interaction.response.send_message(embed=Embeds.fish_data(title, data, self.fishes, True))
				except Exception as e:
					print(e)
					await interaction.response.send_message(embed=Embeds.general('해당 낚시터에는 물고기가 없습니다.',""), ephemeral=True)
			else:
				await interaction.response.send_message(embed=Embeds.fish_data("낚시터에서 발견 가능한 물고기 입니다.", self.fish_data, self.fishes, False))
		except Exception as e:
			self.bot.logger.error(e)(e)
		
	@commands.command(hidden=True)
	@commands.has_any_role('관리자')
	async def 낚시설정(self, message:commands.Context, 
		value:int=commands.parameter(displayed_name="최대 횟수",description="- 낚시가 가능한 최대 횟수")):
		"""
		최대 낚시 횟수를 변경합니다.
		횟수는 숫자로 입력해주시기 바랍니다.
		"""
		if value:
			try:
				self.connector.set_max_fishing(value)
				await message.send(embed=Embeds.setting(f'최대 낚시 횟수가 {value}회로 변경되었습니다.'))
			except Exception as e:
				print(e)
				print(traceback.format_exc())
				await message.send(embed=Embeds.error())
		else:
			await message.send(embed=Embeds.warning('변경하고자 하는 수치를 입력해 주시기 바랍니다'), delete_after=5)
	
	@commands.command(hidden=True)
	@commands.has_any_role('관리자')
	async def 낚시이력삭제(self, message:commands.Context, 
			 user:Member=commands.parameter(displayed_name="대상 유저",description="- 이력을 삭제하고자 하는 유저명. @를 통해 입력해 주세요")):
		"""
		사용자의 낚시 이력을 삭제합니다.
		@태그를 통해 입력해 주시기 바랍니다.
		"""
		if user:
			if type(user) == Member:
				self.connector.delete_fishing_history(user.id)
				name = user.nick or user.name
				await message.send(embed=Embeds.setting(f'{name}의 이력을 삭제하였습니다.'))
			else:
				await message.send(embed=Embeds.warning('@태그를 이용해 사용자를 입력 바랍니다.'), delete_after=5)
		else:
			await message.send(embed=Embeds.warning('대상 사용자를 입력해 주시기 바랍니다.'), delete_after=5)

	@commands.command(hidden=True)
	@commands.has_any_role('관리자')
	async def 물고기추가(self, message:commands.Context, 
		 name:str=commands.parameter(displayed_name="물고기 이름-",default=None, displayed_default="text",description="추가하고자 하는 물고기 이름입니다.")):
		"""
		새로운 물고기를 추가합니다.
		필요한 정보
		이름 / 설명 / 최소길이 / 최고길이 / 기본 가격 / 등장위치(채널명)
		"""
		if not name:
			await message.send(embed=Embeds.warning('물고기 이름을 입력해 주시기 바랍니다.'), delete_after=5)
			return
		infoview = Views.AddFishView()
		await message.send(embed=Embeds.setting(f"{name}을/를 추가하시겠습니까?",None),view=infoview)
		await infoview.wait()
		if infoview.cancel:return
		desc = infoview.modal.desc.value
		min = int(infoview.modal.min.value)
		max = int(infoview.modal.max.value)
		baseprice = int(infoview.modal.baseprice.value)
		loc = infoview.modal.loc.value

		try:
			self.connector.add_fish_data(name, desc, min, max, baseprice, loc)
			await message.send(embed=Embeds.add_fish(f'{name}을/를 추가했습니다.',name,desc,min,max,baseprice,loc))
		except CannotAddFish as e:
			print(e)
			print('>> Error: cannot add fish')
			print(traceback.format_exc())
			await message.send(embed=Embeds.warning('물고기를 추가하지 못하였습니다. 다시 시도해 주시기 바랍니다.'), delete_after=5)
		except Exception as e:
			print(e)
			print('>> Error: unkown error')
			print(traceback.format_exc())
			raise e

	@commands.command(name="물고기변경", hidden=True)
	@commands.has_any_role('관리자')
	async def change_fish_data(self, message:commands.Context, 
					name:str=commands.parameter(displayed_name="물고기 이름-", default=None, description="수정하고자 하는 물고기 이름")):
		"""
		낚시터의 물고기 정보를 변경합니다.
		"""
		msg = None
		try:
			if name:
				code_list = list(filter(lambda x: self.fishes[x].name==name,list(self.fishes.keys())))
				if not code_list:
					raise FishNotFOund('해당이름 물고기 없음')
				code = code_list[0]
			else:
				title = "변경하실 물고기를 선택해 주세요."
				selectview = Views.SelectFishView(self.fishes)
				msg = await message.send(embed=Embeds.setting(title,None), view=selectview)
				await selectview.wait()
				if selectview.cancel: return
				code = selectview.fish.values[0]
				name = self.items[code].name

			print(f'{name} | {code}')
			data = deepcopy(self.fishes[code])
			data.desc = self.items[code].desc
			print(data)
			infoview = Views.ChangeFishView(data)
			if msg:
				await msg.edit(embed=Embeds.setting(f"{name}을/를 변경하시겠습니까?",None),view=infoview)
			else:
				await message.send(embed=Embeds.setting(f"{name}을/를 변경하시겠습니까?",None),view=infoview)
			await infoview.wait()
			if infoview.cancel: return
			desc = infoview.modal.desc.value
			min = int(infoview.modal.min.value)
			max = int(infoview.modal.max.value)
			baseprice = int(infoview.modal.baseprice.value)
			loc = infoview.modal.loc.value

			self.connector.change_fish_data(code, desc, min, max, baseprice, loc)
			await message.send(embed=Embeds.add_fish(f'{name}을/를 변경했습니다.',name,desc,min,max,baseprice,loc))
		except CannotAddFish as e:
			print(e)
			print('>> Error: cannot add fish')
			print(traceback.format_exc())
			await message.send(embed=Embeds.warning('물고기를 변경하지 못하였습니다. 다시 시도해 주시기 바랍니다.'), delete_after=5)
		except FishNotFOund as e:
			print(e)
			print('>> Error: fish not found')
			print(traceback.format_exc())
			await message.send(embed=Embeds.warning('해당 이름의 물고기가 존재하지 않습니다. 물고기 이름을 다시 확인해 주시기 바랍니다.'), delete_after=5)
		except Exception as e:
			print(e)
			print('>> Error: unkown error')
			print(traceback.format_exc())
			raise e

	@commands.command(name="물고기삭제", hidden=True)
	@commands.has_any_role('관리자')
	async def delete_fish_data(self, message:commands.Context, 
					name:str=commands.parameter(displayed_name="물고기 이름-", default=None, description="삭제하고자 하는 물고기 이름")):
		"""
		낚시터의 물고기 정보를 삭제합니다.
		"""
		try:
			msg = None
			if name:
				code_list = list(filter(lambda x: self.fishes[x].name==name,list(self.fishes.keys())))
				if not code_list:
					raise FishNotFOund('해당이름 물고기 없음')
				code = code_list[0]
			else:
				title = "삭제하실 물고기를 선택해 주세요."
				selectview = Views.SelectFishView(self.fishes)
				msg = await message.send(embed=Embeds.setting(title,None), view=selectview)
				await selectview.wait()
				if selectview.cancel: return
				code = selectview.fish.values[0]
				name = self.items[code].name

			print(f'{name} | {code}')
			delview = Views.ConfirmFishDelete()
			if msg:
				await msg.edit(embed=Embeds.warning(f"{name}을/를 삭제하시겠습니까?"),view=delview)
			else:
				await message.send(embed=Embeds.warning(f"{name}을/를 삭제하시겠습니까?"),view=delview)
			await delview.wait()
			if delview.cancel: return
			self.connector.delete_fish(code)
			await message.send(embed=Embeds.setting(f"{name}을/를 삭제하였습니다.",None))
		except CannotAddFish as e:
			print(e)
			print('>> Error: cannot add fish')
			print(traceback.format_exc())
			await message.send(embed=Embeds.warning('물고기를 삭제하지 못하였습니다. 다시 시도해 주시기 바랍니다.'), delete_after=5)
		except FishNotFOund as e:
			print(e)
			print('>> Error: fish not found')
			print(traceback.format_exc())
			await message.send(embed=Embeds.warning('해당 이름의 물고기가 존재하지 않습니다. 물고기 이름을 다시 확인해 주시기 바랍니다.'), delete_after=5)
		except Exception as e:
			print(e)
			print('>> Error: unkown error')
			print(traceback.format_exc())
			raise e
		
async def setup(bot:commands.Bot):
	await bot.add_cog(Fishing(bot))

