import discord
from JAS.resources.Exceptions import *
from JAS.resources.Base import commands, app_commands, CommandBase, AppCommandBase, Embeds, Views
from asyncio import sleep

class Stat(CommandBase):
	@app_commands.command(name="스탯", description="캐릭터의 스탯분배를 진행합니다.")
	async def stat(self, interaction:discord.Interaction):
		"""
		캐릭터의 스탯분배를 진행합니다.
		"""
		await self.on_ready(interaction)
		try:
			await interaction.response.defer(ephemeral=True)
			code = self.user[interaction.user.id].charas
			chara = self.charas[code]
			stat_names = chara.stat.stat_names or self.setting.stat_names
			point = chara.stat.point
			base_view = Views.SpendStat(interaction.user)
			stat1_view = Views.AllStat(1,chara.stat,interaction.user)
			stat2_view = Views.AllStat(2,chara.stat,interaction.user)
			base = await interaction.channel.send(embed=Embeds.setting("스탯포인트를 소모하여 스탯을 조정합니다", f"남은 포인트: {point}"), view = base_view)
			stat1 = await interaction.channel.send(view = stat1_view)
			stat2 = await interaction.channel.send(view = stat2_view)
			process=True
			while process:
				if base_view.cancel or base_view.finish:
					print("delete stat view")
					await stat1.delete()
					await stat2.delete()
					process = False
				else:
					changed = False
					if stat1_view.stat1_sub.clicked:
						print("stat1 sub")
						stat1_view.stat1_sub.clicked=False
						if stat1_view.stat1_value > stat1_view.stat1_origin:
							stat1_view.stat1_value -= 1
							stat1_view.point += 1
						stat1_view.stat1_current.label=f"{stat_names[0]}: {stat1_view.stat1_value}"
						point = stat1_view.point
						changed = True
					if stat1_view.stat1_add.clicked:
						print("stat1 add")
						stat1_view.stat1_add.clicked=False
						if stat1_view.point > 0:
							stat1_view.stat1_value += 1
							stat1_view.point -= 1
						stat1_view.stat1_current.label=f"{stat_names[0]}: {stat1_view.stat1_value}"
						point = stat1_view.point
						changed = True
					elif stat1_view.stat2_sub.clicked:
						print("stat2 sub")
						stat1_view.stat2_sub.clicked=False
						if stat1_view.stat2_value > stat1_view.stat2_origin:
							stat1_view.stat2_value -= 1
							stat1_view.point += 1
						stat1_view.stat2_current.label=f"{stat_names[1]}: {stat1_view.stat2_value}"
						point = stat1_view.point
						changed = True
					elif stat1_view.stat2_add.clicked:
						print("stat2 add")
						stat1_view.stat2_add.clicked=False
						if stat1_view.point > 0:
							stat1_view.stat2_value += 1
							stat1_view.point -= 1
						stat1_view.stat2_current.label=f"{stat_names[1]}: {stat1_view.stat2_value}"
						point = stat1_view.point
						changed = True
					elif stat1_view.stat3_sub.clicked:
						print("stat3 sub")
						stat1_view.stat3_sub.clicked=False
						if stat1_view.stat3_value > stat1_view.stat3_origin:
							stat1_view.stat3_value -= 1
							stat1_view.point += 1
						stat1_view.stat3_current.label=f"{stat_names[2]}: {stat1_view.stat3_value}"
						point = stat1_view.point
						changed = True
					elif stat1_view.stat3_add.clicked:
						print("stat3 add")
						stat1_view.stat3_add.clicked=False
						if stat1_view.point > 0:
							stat1_view.stat3_value += 1
							stat1_view.point -= 1
						stat1_view.stat3_current.label=f"{stat_names[2]}: {stat1_view.stat3_value}"
						point = stat1_view.point
						changed = True
					elif stat2_view.stat4_sub.clicked:
						print("stat4 sub")
						stat2_view.stat4_sub.clicked=False
						if stat2_view.stat4_value > stat2_view.stat4_origin:
							stat2_view.stat4_value -= 1
							stat2_view.point += 1
						stat2_view.stat4_current.label=f"{stat_names[3]}: {stat2_view.stat4_value}"
						point = stat2_view.point
						changed = True
					elif stat2_view.stat4_add.clicked:
						print("stat4 add")
						stat2_view.stat4_add.clicked=False
						if stat2_view.point > 0:
							stat2_view.stat4_value += 1
							stat2_view.point -= 1
						stat2_view.stat4_current.label=f"{stat_names[3]}: {stat2_view.stat4_value}"
						point = stat2_view.point
						changed = True
					elif stat2_view.stat5_sub.clicked:
						print("stat5 sub")
						stat2_view.stat5_sub.clicked=False
						if stat2_view.stat5_value > stat2_view.stat5_origin:
							stat2_view.stat5_value -= 1
							stat2_view.point += 1
						stat2_view.stat5_current.label=f"{stat_names[4]}: {stat2_view.stat5_value}"
						point = stat2_view.point
						changed = True
					elif stat2_view.stat5_add.clicked:
						print("stat5 add")
						stat2_view.stat5_add.clicked=False
						if stat2_view.point > 0:
							stat2_view.stat5_value += 1
							stat2_view.point -= 1
						stat2_view.stat5_current.label=f"{stat_names[4]}: {stat2_view.stat5_value}"
						point = stat2_view.point
						changed = True
					elif stat2_view.stat6_sub.clicked:
						print("stat6 sub")
						stat2_view.stat6_sub.clicked=False
						if stat2_view.stat6_value > stat2_view.stat6_origin:
							stat2_view.stat6_value -= 1
							stat2_view.point += 1
						stat2_view.stat6_current.label=f"{stat_names[5]}: {stat2_view.stat6_value}"
						point = stat2_view.point
						changed = True
					elif stat2_view.stat6_add.clicked:
						print("stat6 add")
						stat2_view.stat6_add.clicked=False
						if stat2_view.point > 0:
							stat2_view.stat6_value += 1
							stat2_view.point -= 1
						stat2_view.stat6_current.label=f"{stat_names[5]}: {stat2_view.stat6_value}"
						point = stat2_view.point
						changed = True
					if changed:
						print("value changed")
						stat1_view.point = point
						stat2_view.point = point
						# disable subtract button
						stat1_view.stat1_sub.disabled = True if stat1_view.stat1_origin == stat1_view.stat1_value else False
						stat1_view.stat2_sub.disabled = True if stat1_view.stat2_origin == stat1_view.stat2_value else False
						stat1_view.stat3_sub.disabled = True if stat1_view.stat3_origin == stat1_view.stat3_value else False
						stat2_view.stat4_sub.disabled = True if stat2_view.stat4_origin == stat2_view.stat4_value else False
						stat2_view.stat5_sub.disabled = True if stat2_view.stat5_origin == stat2_view.stat5_value else False
						stat2_view.stat6_sub.disabled = True if stat2_view.stat6_origin == stat2_view.stat6_value else False
						# disable add button
						stat1_view.stat1_add.disabled=True if point ==0 else False
						stat1_view.stat2_add.disabled=True if point ==0 else False
						stat1_view.stat3_add.disabled=True if point ==0 else False
						stat2_view.stat4_add.disabled=True if point ==0 else False
						stat2_view.stat5_add.disabled=True if point ==0 else False
						stat2_view.stat6_add.disabled=True if point ==0 else False
						await base.edit(embed=Embeds.setting("스탯", f"남은 포인트: {point}"))
						await stat1.edit(view=stat1_view)
						await stat2.edit(view=stat2_view)
					await sleep(0.1)
			await interaction.delete_original_response()
			if base_view.finish:
				point = stat1_view.point
				stat1 = stat1_view.stat1_value
				stat2 = stat1_view.stat2_value
				stat3 = stat1_view.stat3_value
				stat4 = stat2_view.stat4_value
				stat5 = stat2_view.stat5_value
				stat6 = stat2_view.stat6_value
				# stat = f'{stat1},{stat2},{stat3},{stat4},{stat5},{stat6}'
				self.connector.update_stat(code, stat_names, point, [stat1, stat2, stat3, stat4, stat5, stat6])
				await base.edit(embed=Embeds.show_stat_result(chara), view=None)
		except Exception as e:
			self.bot.logger.error(e)
	
	@commands.command(name="스탯초기화", hidden=True)
	@commands.has_any_role('관리자')
	async def clear_stat(self, ctx:commands.Context, user:discord.Member=None):
		"""
		스탯을 초기화 합니다.
		전체 스탯을 1로 만들며 이미 투자한 스탯은 포인트로 전환됩니다.
		"""
		try:
			if not user:
				return await ctx.send(embed=Embeds.general('초기화를 진행할 사용자를 입력해 주시기 바랍니다'))
			code = self.user[user.id].charas
			chara = self.charas[code]
			stat = chara.stat
			all_stat = stat.stat1+stat.stat2+stat.stat3+stat.stat4+stat.stat5+stat.stat6
			point = stat.point + all_stat-6
			stat.stat1 = 1
			stat.stat2 = 1
			stat.stat3 = 1
			stat.stat4 = 1
			stat.stat5 = 1
			stat.stat6 = 1

			self.connector.update_stat(code, stat.stat_names, point, 1,1,1,1,1,1)
			await ctx.send(embed=Embeds.setting("스탯을 초기화 하였습니다.", f"총 스탯포인트: {point}"))
		except Exception as e:
			self.bot.logger.error(e)
		
async def setup(bot:commands.Bot):
	await bot.add_cog(Stat(bot))