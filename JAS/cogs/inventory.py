import discord
from JAS.resources.Exceptions import *
from JAS.resources.Base import JAS, commands, app_commands, CommandBase, AppCommandBase, Views, Embeds
from random import randrange, random
from asyncio import sleep
from copy import deepcopy

class Inventory(CommandBase):
	def __init__(self, bot: JAS) -> None:
		super().__init__(bot)
		bot.tree.add_command(app_commands.ContextMenu(
			name="송금",
			callback=self.transfer_gold_menu,
		))

	@app_commands.command(name="소지품")
	@app_commands.rename(check_gold="골드확인")
	@app_commands.describe(check_gold="소지중인 골드만 확인합니다.")
	@app_commands.choices(check_gold=[
		app_commands.Choice(name="골드만 확인", value='True'),
		app_commands.Choice(name="소지품 확인", value='False'),
	])
	async def inventory(self, interaction:discord.Interaction,
					 check_gold:app_commands.Choice[str]=None):
		"""
		현재 자신이 가지고 있는 소지품을 확인합니다.
		남은 가방공간, 아이템, 골드를 확인가능합니다.
		"""
		await self.on_ready(interaction)
		try:
			id = interaction.user.id
			code = self.user[id].charas
			if check_gold:
				if check_gold.value == 'True':
					gold = self.invs[code].gold # self.connector.get_gold(id)
					return await interaction.response.send_message(embed=Embeds.store(f'현재 G{gold}를 소지하고 있습니다.'), ephemeral=True)
			name = self.charas[code].name
			title = f'{name}님의 소지품입니다.'
			inventory = self.invs[code]
			desc = f'남은 공간: {len(inventory.items)} / {inventory.size}'
			await interaction.response.send_message(embed=Embeds.inventory(title=title, desc=desc, inventory=inventory, items=self.items), ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	def send_gold(self, id, user, gold):
		fromcode = self.user[id].charas
		tocode = self.user[user].charas
		current_gold = self.invs[fromcode].gold
		if current_gold < gold:
			raise NotEnoughGold('골드가 충분하지 않습니다.')
		self.connector.add_gold(fromcode, -gold)
		self.connector.add_gold(tocode, gold)
	
	@app_commands.command(name="송금",description="상대방에게 골드를 전달합니다.")
	@app_commands.rename(user="대상", gold="금액")
	@app_commands.describe(user="송금하고자 하는 대상", gold="송금하고자 하는 금액. 입력하지 않으면 10골드를 송금합니다.")
	async def transfer_gold(self, interaction:discord.Interaction,
			user:discord.Member,
			gold:int=10):
		"""
		골드를 다른 사람에게 전달합니다.
		골드를 입력하지 않은 경우 10골드가 전달됩니다.
		"""
		await self.on_ready(interaction)
		try:
			id = interaction.user.id
			name = interaction.user.display_name
			
			user_name = user.display_name
			user_id = user.id
			code = self.user[user_id].charas
			if not code:
				return await interaction.response.send_message(embed=Embeds.general('캐릭터가 존재하지 않는 사용자에게 송금할 수 없습니다.'), ephemeral=True)
			
			transfer_view = Views.TransferView()
			await interaction.response.send_message(embed=Embeds.store(f'{user_name}에게 송금하시겠습니까?',f'G{gold}를 전달합니다.'), view=transfer_view, ephemeral=True)
			await transfer_view.wait()
			if transfer_view.cancel: 
				return await interaction.edit_original_response(embed=Embeds.general('작업을 취소합니다.'))
			await interaction.delete_original_response()
			self.send_gold(id, user_id, gold)
			await interaction.channel.send(embed=Embeds.store(f'{name}이/가 {user_name}에게 G{gold}를 전달하였습니다.'))
		except NotEnoughGold as e:
			await interaction.edit_original_response(embed=Embeds.warning('소지한 골드가 부족합니다.'), view=None)
		except Exception as e:
			self.bot.logger.error(e)

	async def transfer_gold_menu(self, interaction:discord.Interaction, user:discord.User):
		await self.on_ready(interaction)
		try:
			id = interaction.user.id
			name = interaction.user.display_name
			gold = 10
			
			user_name = user.display_name
			user_id = user.id
			code = self.user[user_id].charas
			if not code:
				return await interaction.response.send_message(embed=Embeds.general('캐릭터가 존재하지 않는 사용자에게 송금할 수 없습니다.'), ephemeral=True)
			
			transfer_view = Views.TransferView()
			await interaction.response.send_message(embed=Embeds.store(f'{user_name}에게 송금하시겠습니까?',f'G{gold}를 전달합니다.'), view=transfer_view, ephemeral=True)
			await transfer_view.wait()
			if transfer_view.cancel: 
				return await interaction.edit_original_response(embed=Embeds.general('작업을 취소합니다.'))
			self.send_gold(id, user_id, gold)
			await interaction.delete_original_response()
			await interaction.channel.send(embed=Embeds.store(f'{name}이/가 {user_name}에게 G{gold}를 전달하였습니다.'))
		except NotEnoughGold as e:
			print(e)
			print('>> Error: not enough gold')
			print(traceback.format_exc())
			await interaction.edit_original_response(embed=Embeds.warning('소지한 골드가 부족합니다.'), view=None)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="아이템판매", description="갖고있는 아이템을 판매합니다.")
	async def item_sold(self, interaction:discord.Interaction):
		"""
		소지품을 상점에 판매합니다.
		"""
		await self.on_ready(interaction)
		try:
			user_id = interaction.user.id
			code = self.user[user_id].charas
			if len(self.invs[code].items) == 0:
				return await interaction.response.send_message(embed=Embeds.general('판매 가능한 아이템이 없습니다.'), ephemeral=True)
			item_view = Views.SoldItemView(self.invs[code].items, self.items)
			await interaction.response.send_message(embed=Embeds.store("판매할 아이템을 선택해 주세요"), view=item_view, ephemeral=True)
			await item_view.wait()
			if item_view.cancel:
				return await interaction.delete_original_response()
			sold_items = item_view.select.values
			result = 0
			for item in sold_items:
				price = self.items[item].price
				self.connector.sold_item(code, item, price)
				result = result+price
			await interaction.edit_original_response(embed=Embeds.sold_item(result), view=None)
		except Exception as e:
			self.bot.logger.error(e)

	@commands.command(name="아이템부여", hidden=True)
	async def spawn_item(self, ctx:commands.Context,
					user:discord.Member=commands.parameter(displayed_name="대상 유저",default=None,description="아이템을 부여할 유저입니다.",displayed_default="@사용자")):
		"""
		해당 유저에게 아이템을 부여합니다.
		"""
		try:
			if not user:
				return await ctx.send(embed=Embeds.warning('유저가 입력되지 않았습니다.','@로 유저를 입력해 주시기 바랍니다.'))
			else:
				try:
					user.id
				except:
					return await ctx.send(embed=Embeds.warning('유저는 @태그로 입력해야 합니다.','@로 유저를 입력해 주시기 바랍니다.'))
			select_view = Views.SpawnItem(self.items)
			await ctx.send(embed=Embeds.setting("부여할 아이템을 선택해 주세요."), view=select_view)
			await select_view.wait()
			if select_view.cancel: return
			items = []
			code = self.user[ctx.author.id].charas
			for itemcode in select_view.select.values:
				itemdata = self.items[itemcode]
				self.connector.spawn_item(code, itemcode, itemdata)
				items.append(itemdata.name)
			await ctx.send(embed=Embeds.setting(f"{user.display_name}에게 아이템을 부여하였습니다.",f"부여한 아이템: {', '.join(items)}"))
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise e

async def setup(bot:commands.Bot):
	await bot.add_cog(Inventory(bot))
