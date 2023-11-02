import discord
from JAS.resources.Exceptions import *
from JAS.resources.Base import commands, app_commands, CommandBase, AppCommandBase, Embeds, Views
from random import random, randrange, choice
from asyncio import sleep

class Store(CommandBase):
	@app_commands.command(name="랜덤박스", description="일정 금액을 소비하여 랜덤뽑기를 진행합니다.")
	async def random_box(self, interaction:discord.Interaction):
		"""
		일정 금액을 소비하여 뽑기를 진행합니다.
		"""
		await self.on_ready(interaction)
		result_text = [
			"잭팟!\n넣은 금액의 네배를 얻습니다.",
			"2등상!\n넣은 금액의 두배가 나왔습니다.",
			"3등상\n본전은 찾았습니다.",
			"참가상\n사용한 금액의 반을 돌려 받습니다.",
			"꽝!\n랜덤박스는 잠잠합니다...",
		]
		try:
			price = self.setting.random_box
			code = self.user[interaction.user.id].charas
			gold = self.invs[code].gold
			if price > gold:
				return await interaction.response.send_message(embed=Embeds.general('금액이 부족합니다',f'현재 소지금은 {gold}입니다.'), ephemeral=True)
			else:
				self.connector.add_gold(code, -price)
				dice = randrange(0,100)
				if dice < 1:
					result_title = "만세!"
					result = result_text[0]
					result_color = discord.Color.gold()
					self.connector.add_gold(code, price*4)
				elif dice < 5:
					result_title = "야호!"
					result = result_text[1]
					result_color = discord.Color.green()
					self.connector.add_gold(code, price*2)
				elif dice < 20:
					result_title = "괜찮아!"
					result = result_text[2]
					result_color = discord.Color.green()
					self.connector.add_gold(code, price)
				elif dice < 60:
					result_title = "이런..."
					result = result_text[3]
					result_color = discord.Color.light_grey()
					self.connector.add_gold(code, int(price/2))
				else:
					result_title = "..."
					result = result_text[4]
					result_color = discord.Color(0)
			
			title_list = [
				"힘차게 돌아갑니다!",
				"덜컹덜컹 돌아갑니다",
				"힘없이 돌아갑니다...",
				"수상한 소음을 내며 돌아갑니다...?",
			]
			title = f"랜덤박스가 {choice(title_list)}"
			embed_msg = Embeds.random_box(title, 0)
			await interaction.response.send_message(embed=embed_msg)
			for i in range(1,8):
				embed_msg = Embeds.random_box(title, i)
				await interaction.edit_original_response(embed=embed_msg)
				await sleep(0.5)
			await interaction.edit_original_response(embed=Embeds.general(result_title, result, result_color))
		except Exception as e:
			self.bot.logger.error(e)

async def setup(bot:commands.Bot):
	await bot.add_cog(Store(bot))


