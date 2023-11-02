import discord, shutil, os
from discord import Color, File
from JAS.resources.Base import commands, app_commands, CommandBase, AppCommandBase, Views, Embeds
from JAS.resources.Addons import resize_img, key_gen, filename, IMG_FOLDER_PATH, resource_path
from JAS.resources.Exceptions import *
from asyncio import sleep

class Community(CommandBase):
	async def anon_message(self, message:discord.Message):
		print(f'{message.author.display_name} | {message.author.id} | {message.content}')
		content = message.content
		
		channel_id = list(filter(lambda x: x.name == self.channel.anon, message.guild.text_channels))[0].id
		channel = message.guild.get_channel(channel_id)
		await channel.send(embed=Embeds.general(content))

	async def chara_talk(self, message:discord.Message):
		id = message.author.id
		code = self.user[id].charas # self.connector.get_user_chara(id)[0]
		chara = self.charas[code]
		content = message.content
		color = chara.color or Color.brand_green()
		path = os.path.join(IMG_FOLDER_PATH, str(message.guild.id), f'{filename(chara.name)}.png')
		embedmsg, icon = Embeds.chara_talk(self.charas[code], path, content, color)
		print(icon.filename)
		files = [icon]
		if message.attachments:
			for attachment in message.attachments:
				file = await attachment.to_file(use_cached=True)
				files.append(file)
		channel_name = message.channel.name
		webhook = list(filter(lambda x:x.name == f"{channel_name} Chat", await message.guild.webhooks()))
		print(webhook)
		if not webhook: 
			webhook = await message.channel.create_webhook(name=f"{channel_name} Chat")
		else: 
			webhook = webhook[0]
		# if message.reference:
		# 	print(message.reference)
		# 	# msg = await message.channel.fetch_message(message.reference.message_id)
		# 	# await msg.reply(embed=embedmsg, files=files)
		# 	print(await webhook.fetch())
		# 	msg = await webhook.fetch_message(message.reference.message_id)
		# 	await msg.reply(embed=embedmsg, files=files)
		# else:
		# 	await webhook.send(embed=embedmsg, files=files, username=chara.name, avatar_url=message.author.display_avatar.url, wait=True)
		await webhook.send(content=message.reference.jump_url if message.reference else None,
										 embed=embedmsg, files=files, 
										 username=chara.name, 
										 avatar_url=message.author.display_avatar.url, 
										 wait=True)
		# await webhook.delete()

	@app_commands.command(name="스레드명", description="현재 속해있는 스레드의 이름을 변경합니다")
	@app_commands.rename(title="이름")
	@app_commands.describe(title="변경하고자 하는 이름")
	async def change_thread_name(self, inter:discord.Interaction, title:str):
		await self.on_ready(inter)
		try:
			if inter.channel.type==discord.ChannelType.text:
				return await inter.response.send_message(embed=Embeds.general('해당 채널은 스레드가 아닙니다','스레드에 접속된 상태에서 다시 시도해 보세요.'), ephemeral=True)
			else:
				before_title = inter.channel.name
				await inter.channel.edit(name=title)
				await inter.response.send_message(embed=Embeds.general('스레드 명이 변경되었습니다',f'{before_title} > {title}'), ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="투표", description="투표를 생성합니다. 항목은 최대 5개까지 설정 가능합니다. 기한을 설정하지 않을 시 10분으로 설정됩니다.")
	@app_commands.rename(timeout="기한",
											op1="항목1",
											op2="항목2",
											op3="항목3",
											op4="항목4",
											op5="항목5")
	@app_commands.describe(timeout="투표 마감 기한을 설정해 주세요. 기준은 분입니다. 예) 10",
											op1="투표 항목. /로 설명을 기입할 수 있습니다. 예) 투표한다/당신은 투표를 해야한다.",
											op2="투표 항목. /로 설명을 기입할 수 있습니다. 예) 투표한다/당신은 투표를 해야한다.",
											op3="투표 항목. /로 설명을 기입할 수 있습니다. 예) 투표한다/당신은 투표를 해야한다.",
											op4="투표 항목. /로 설명을 기입할 수 있습니다. 예) 투표한다/당신은 투표를 해야한다.",
											op5="투표 항목. /로 설명을 기입할 수 있습니다. 예) 투표한다/당신은 투표를 해야한다.")
	async def vote(self, inter:discord.Interaction, 
								op1:str, op2:str, op3:str="", op4:str="", op5:str="",
								timeout:int=10):
		await self.on_ready(inter, check_user=False, check_chara=False)
		embedmsg = Embeds.vote(timeout, op1, op2, op3, op4, op5)
		await inter.response.send_message(embed=embedmsg, allowed_mentions=discord.AllowedMentions.none())
		msg = await inter.edit_original_response()
		await msg.add_reaction('1️⃣')
		await msg.add_reaction('2️⃣')
		if op3: await msg.add_reaction(discord.Reaction('3️⃣'))
		if op4:	await msg.add_reaction(discord.Reaction('4️⃣'))
		if op5:	await msg.add_reaction(discord.Reaction('5️⃣'))
		# print(msg)
		
		await sleep(timeout*60)

		msg = await inter.channel.fetch_message(msg.id)
		# print(msg)
		result = {}
		total = sum([reaction.count-1 for reaction in msg.reactions])
		# print(msg.reactions)
		for reaction in msg.reactions:
			# print(reaction)
			if reaction.emoji == '1️⃣':
				key = op1.split('/')[0]
			if reaction.emoji == '2️⃣':
				key = op2.split('/')[0]
			if reaction.emoji == '3️⃣':
				key = op3.split('/')[0]
			if reaction.emoji == '4️⃣':
				key = op4.split('/')[0]
			if reaction.emoji == '5️⃣':
				key = op5.split('/')[0]
			count = reaction.count-1
			percent = int(count/total*100)
			result[key] = [percent, count]
		resultmsg = Embeds.vote_result(total, result)
		
		await inter.channel.send(content=msg.jump_url, embed=resultmsg)

	@commands.command(name="캐릭터등록", hidden=True)
	@commands.has_any_role('관리자')
	async def add_chara(self, ctx:commands.Context, 
					 user:discord.Member=commands.parameter(displayed_name="추가 대상 사용자",description="캐릭터 추가를 진행할 사용자",displayed_default="@사용자")):
		"""
		대상자의 캐릭터를 등록합니다.
		이름, 키워드(옵션), 설명을 등록합니다.
		이미지를 첨부할 시 해당 이미지를 아이콘으로 사용합니다. 첨부되지 않은 경우 기본 아이콘이 사용됩니다.
		이미지 사이즈 100x100
		"""
		try:
			chara_codes = list(self.charas.keys())
			id = user.id
			code = self.user[id].charas
			if code in chara_codes:
				return await ctx.send(embed=Embeds.setting('이미 캐릭터가 등록되어 있습니다.','정보 변경을 원하신다면 `!캐릭터변경`을 사용해 주시기 바랍니다.'))
			infoview=Views.AddChara()
			await ctx.send(embed=Embeds.setting("캐릭터를 등록하시겠습니까?"), view=infoview)
			await infoview.info.wait()
			name = infoview.info.name.value
			keyword = infoview.info.keyword.value
			desc = infoview.info.desc.value
			link = infoview.info.link.value
			if 'https://' not in link:
				link = 'https://'+ link
			self.connector.set_charactor_data(id, code, name, keyword, desc, link)
			path = os.path.join(IMG_FOLDER_PATH, str(ctx.guild.id), f'{filename(name)}.png')
			if ctx.message.attachments:
				icon=ctx.message.attachments[0]
				if icon.height > 300 or icon.width > 300:
					await resize_img(icon, path)
				else:
					await icon.save(path)	
				chara_embed, icon = Embeds.show_chara(self.charas[code], path)
				await ctx.send(embeds=[Embeds.setting(f"{name}을/를 등록하였습니다."),chara_embed], file=icon)
			else:
				shutil.copy(resource_path(IMG_FOLDER_PATH,'sample.png'), path)
				chara_embed, icon = Embeds.show_chara(self.charas[code], path)
				await ctx.send(embeds=[Embeds.setting(f"{name}을/를 등록하였습니다.","기본 이미지가 등록 되었습니다.\n`!캐릭터변경`으로 인장을 등록해 주시기 바랍니다."),chara_embed], file=icon)
		except Exception as e:
			self.bot.logger.error(e)

	@commands.command(name="캐릭터변경", hidden=True)
	@commands.has_any_role('관리자')
	async def change_chara(self, ctx:commands.Context, 
					 user:discord.Member=commands.parameter(displayed_name="추가 대상 사용자",description="캐릭터 변경을 진행할 사용자",displayed_default="@사용자")):
		"""
		대상자의 캐릭터를 변경합니다.
		이름, 키워드(옵션), 설명을 등록합니다.
		이미지를 첨부할 시 해당 이미지를 아이콘으로 사용합니다. 첨부되지 않은 경우 기본 아이콘이 사용됩니다.
		이미지 사이즈 100x100
		"""
		try:
			id = user.id
			code = self.user[id].charas
			before_name = self.charas[code].name
			infoview=Views.ChangeChara(before_name, self.charas[code])
			await ctx.send(embed=Embeds.setting(f'{before_name}을/를 수정하시겠습니까?'), view=infoview)
			await infoview.info.wait()
			if infoview.cancel: return
			name = infoview.info.name.value
			keyword = infoview.info.keyword.value
			desc = infoview.info.desc.value
			link = infoview.info.link.value
			if 'https://' not in link:
				link = 'https://'+ link
			path = os.path.join(IMG_FOLDER_PATH, str(ctx.guild.id), f'{filename(name)}.png')
			if ctx.message.attachments:
				icon=ctx.message.attachments[0]
				if icon.height > 300 or icon.width > 300:
					await resize_img(icon, path)
				else:
					await icon.save(path)
			self.connector.update_charactor_data(code, name, keyword, desc, link)
			chara_embed, icon = Embeds.show_chara(self.charas[code], path)
			await ctx.send(embeds=[Embeds.setting(f"{name}의 정보가 변경되었습니다."),chara_embed], file=icon)
		except Exception as e:
			self.bot.logger.error(e)
		
	@commands.command(name="캐릭터삭제", hidden=True)
	@commands.has_any_role('관리자')
	async def delete_chara(self, ctx:commands.Context, 
					 user:discord.Member=commands.parameter(displayed_name="추가 대상 사용자",description="캐릭터 삭제를 진행할 사용자",displayed_default="@사용자")):
		"""
		대상의 캐릭터를 삭제합니다.
		"""
		try:
			id = user.id
			code = self.user[id].charas
			name = self.charas[code].name
			remove_view = Views.RemoveChara(name)
			await ctx.send(embed=Embeds.warning(f"캐릭터 {name}을/를 삭제하시겠습니까?"),view=remove_view)
			await remove_view.wait()
			if remove_view.cancel: return
			self.connector.delete_charactor_data(code, id)
			path = os.path.join(IMG_FOLDER_PATH, str(ctx.guild.id), f'{filename(name)}.png')
			os.remove(path)
		except Exception as e:
			self.bot.logger.error(e)

class CharaGroup(AppCommandBase):
	def __init__(self, bot, name, description):
		super().__init__(bot, name, description)
		self.bot.tree.add_command(app_commands.ContextMenu(
			name="캐릭터 정보",
			callback=self.view_chara,
		))

	@app_commands.command(name="등록", description="커뮤에서 사용할 캐릭터를 등록합니다.")
	@app_commands.rename(icon="아이콘")
	@app_commands.describe(icon="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.")
	async def add_chara_slash(self, interaction:discord.Interaction, icon:discord.Attachment=None):
		"""
		자신의 캐릭터를 등록합니다.
		이름, 키워드(옵션), 설명을 등록합니다.
		이미지를 첨부할 시 해당 이미지를 아이콘으로 사용합니다. 첨부되지 않은 경우 기본 아이콘이 사용됩니다.
		이미지 사이즈 300x300
		"""
		await self.on_ready(interaction, check_chara=False)
		try:
			chara_codes = list(self.charas.keys())
			id = interaction.user.id
			code = key_gen()
			if code in chara_codes:
				return await interaction.response.send_message(embed=Embeds.setting('이미 캐릭터가 등록되어 있습니다.','정보 변경을 원하신다면 `!캐릭터변경`을 사용해 주시기 바랍니다.'), ephemeral=True, delete_after=10)
			modal=Views.CharaInfo("캐릭터정보")
			await interaction.response.send_modal(modal)
			await modal.wait()
			if not modal.finish: return
			name = modal.name.value
			keyword = modal.keyword.value
			desc = modal.desc.value
			link = modal.link.value
			if 'https://' not in link:
				link = 'https://'+ link
			self.connector.set_charactor_data(id, code, name, keyword, desc, link)
			path = os.path.join(IMG_FOLDER_PATH, str(interaction.guild_id), f'{filename(name)}.png')
			if icon:
				if icon.height > 300 or icon.width > 300:
					await resize_img(icon, path)
				else:
					await icon.save(path)	
				chara_embed, icon = Embeds.show_chara(self.charas[code], path)
				await interaction.followup.send(embeds=[Embeds.setting(f"{name}을/를 등록하였습니다."),chara_embed], file=icon, ephemeral=True)
			else:
				shutil.copy(resource_path(IMG_FOLDER_PATH,'sample.png'), path)
				chara_embed, icon = Embeds.show_chara(self.charas[code], path)
				await interaction.followup.send(embeds=[Embeds.setting(f"{name}을/를 등록하였습니다.","기본 이미지가 등록 되었습니다.\n`!캐릭터변경`으로 인장을 등록해 주시기 바랍니다."),chara_embed], file=icon, ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="변경", description="커뮤에서 사용할 캐릭터 정보를 변경합니다.")
	@app_commands.rename(icon="아이콘")
	@app_commands.describe(icon="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.")
	async def update_chara_slash(self, interaction:discord.Interaction, icon:discord.Attachment=None):
		"""
		자신의 캐릭터를 변경합니다.
		이름, 키워드(옵션), 설명을 등록합니다.
		이미지를 첨부할 시 해당 이미지를 아이콘으로 사용합니다. 첨부되지 않은 경우 기본 아이콘이 사용됩니다.
		이미지 사이즈 300x300
		"""
		await self.on_ready(interaction)
		try:
			id = interaction.user.id
			code = self.user[id].charas
			before_name = self.charas[code].name
			modal=Views.CharaInfo(f"{before_name} 정보", self.charas[code])
			await interaction.response.send_modal(modal)
			await modal.wait()
			if not modal.finish: return
			name = modal.name.value
			keyword = modal.keyword.value
			desc = modal.desc.value
			link = modal.link.value
			if 'https://' not in link:
				link = 'https://'+ link
			path = os.path.join(IMG_FOLDER_PATH, str(interaction.guild_id), f'{filename(name)}.png')
			if icon:
				if icon.height > 300 or icon.width > 300:
					await resize_img(icon, path)
				else:
					await icon.save(path)
			self.connector.update_charactor_data(code, name, keyword, desc, link)
			chara_embed, icon = Embeds.show_chara(self.charas[code], path)
			await interaction.followup.send(embeds=[Embeds.setting(f"{name}의 정보가 변경되었습니다."),chara_embed], file=icon, ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="삭제", description="자신의 캐릭터를 삭제합니다.")
	async def delete_chara_slash(self, interaction:discord.Interaction):
		"""
		자신의 캐릭터를 삭제합니다.
		"""
		await self.on_ready(interaction)
		try:
			id = interaction.user.id
			code = self.user[id].charas
			name = self.charas[code].name
			remove_view = Views.RemoveChara(name)
			await interaction.response.send_message(embed=Embeds.warning(f"캐릭터 {name}을/를 삭제하시겠습니까?"),view=remove_view, ephemeral=True)
			await remove_view.wait()
			if remove_view.cancel: return
			self.connector.delete_charactor_data(code, id)
			path = os.path.join(IMG_FOLDER_PATH, str(interaction.guild_id), f'{filename(name)}.png')
			os.remove(path)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="확인", description="자신 혹은 타인의 캐릭터를 확인합니다.")
	@app_commands.rename(user="사용자명")
	@app_commands.describe(user="확인하고 싶은 캐릭터의 대상자명. 입력하지 않으면 자신의 캐릭터를 확인합니다.")
	async def show_user_chara(self, interaction:discord.Interaction, 
					user:discord.Member=None):
		"""
		타인의 캐릭터를 확인합니다.
		유저명은 필수도 입력해 주시기 바랍니다.
		"""
		await self.on_ready(interaction, check_chara=False)
		try:
			if user:
				code = self.user[user.id].charas
			else:
				code = self.user[interaction.user.id].charas
			chara = self.charas[code]
			path = os.path.join(IMG_FOLDER_PATH, str(interaction.guild_id), f'{filename(chara.name)}.png')
			msg, icon = Embeds.show_chara(chara, path)
			await interaction.response.send_message(embed=msg, file=icon, ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	async def view_chara(self, interaction:discord.Interaction, user:discord.User):
		await self.on_ready(interaction)
		try:
			code = self.user[user.id].charas
			chara = self.charas[code]
			path = os.path.join(IMG_FOLDER_PATH, str(interaction.guild_id), f'{filename(chara.name)}.png')
			msg, icon = Embeds.show_chara(chara, path)
			await interaction.response.send_message(embed=msg, file=icon, ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="색상", description="자신의 캐릭터 대화창의 색상을 변경합니다.")
	@app_commands.rename(input_color='색상코드')
	@app_commands.describe(input_color="원하는 색상코드를 입력해 주세요. 예) #1E45D2")
	async def change_chara_color(self, interaction:discord.Interaction, input_color:str=''):
		"""
		캐릭터 대화창의 색상을 변경합니다.
		"""
		await self.on_ready(interaction)
		try:
			code = self.user[interaction.user.id].charas
			if input_color:
				try:
					color = int(input_color, 16)
					Color(color)
					print('direct',color)
				except:
					color_code = input_color.replace('#','0x') if input_color.startswith('#') else f'0x{input_color}'
					color = int(color_code, 16)
					print('convert',color)
			else:
				color_view = Views.CharaColor()
				await interaction.response.send_message(embed=Embeds.general('원하시는 색상을 선택해 주세요'),view=color_view, ephemeral=True)
				await color_view.wait()
				if not color_view.finish: 
					return await interaction.delete_original_response()
				color = int(color_view.select.values[0])
			self.connector.update_charactor_color(code, color)
			msg = Embeds.general(title="캐릭터 색상이 변경되었습니다",color=Color(color))
			if input_color:
				await interaction.response.send_message(embed=msg, ephemeral=True)
			else:
				await interaction.edit_original_response(embed=msg, view=None)
		except ValueError as e:
			print('input_color error')
			await interaction.response.send_message(embed=Embeds.warning('올바른 색상코드가 아닙니다', f'입력된 값: {input_color}'), ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_role('관리자')
class NPCGroup(AppCommandBase): 
	@app_commands.command(name="등록", description="커뮤에서 사용할 NPC를 등록합니다.")
	@app_commands.rename(color="캐릭터색상", icon1="아이콘1",icon2="아이콘2",icon3="아이콘3",icon4="아이콘4")
	@app_commands.describe(
		color="캐릭터의 채팅창 색상 예) #4F231E",
		icon1="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.",
		icon2="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.",
		icon3="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.",
		icon4="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.")
	async def add_NPC_slash(self, interaction:discord.Interaction, 
						color:str='',
						icon1:discord.Attachment=None,
						icon2:discord.Attachment=None,
						icon3:discord.Attachment=None,
						icon4:discord.Attachment=None,):
		"""
		새로운 NPC 정보를 등록합니다.
		필요사항
		이름 / 상황
		"""
		await self.on_ready(interaction, check_user=False, check_chara=False)
		try:
			guild_id = interaction.guild_id
			code = 'NPC_'+ key_gen()
			modal=Views.NPCInfo()
			await interaction.response.send_modal(modal)
			await modal.wait()
			if not modal.finish: return
			name = modal.name.value
			vers1 = modal.vers1.value
			vers2 = modal.vers2.value
			vers3 = modal.vers3.value
			vers4 = modal.vers4.value
			vers_list = [
				[vers1.split('/')[0], '/'.join(vers1.split('/')[1:])],
				[vers2.split('/')[0], '/'.join(vers2.split('/')[1:])],
				[vers3.split('/')[0], '/'.join(vers3.split('/')[1:])],
				[vers4.split('/')[0], '/'.join(vers4.split('/')[1:])],
			]
			title = f"NPC {name}을/를 등록하였습니다."
			
			# NPC 색상
			if color:
				try:
					color = int(color, 16)
					Color(color)
					print('direct',color)
				except:
					color_code = color.replace('#','0x') if color.startswith('#') else f'0x{color}'
					color = int(color_code, 16)
					print('convert',color)

			self.connector.set_NPC_info(code, name, color)
			for vers_data in vers_list:
				case, vers = vers_data
				if vers:
					path = os.path.join(IMG_FOLDER_PATH, str(interaction.guild_id), filename(f'{name}_{case}.png'))
					
					if vers_list.index(vers_data) == 0:
						icon = icon1
					elif vers_list.index(vers_data) == 1:
						icon = icon2
					elif vers_list.index(vers_data) == 2:
						icon = icon3
					elif vers_list.index(vers_data) == 3:
						icon = icon4
					
					if icon:
						if icon.height > 300 or icon.width > 300:
							await resize_img(icon, path)
						else:
							await icon.save(path)
					else:
						shutil.copy(resource_path(IMG_FOLDER_PATH,'sample.png'), path)
					
					self.connector.set_NPC_vers(code, case, vers)
			chara_embed = Embeds.show_npc(self.npc[code])
			files = []
			for case in self.npc[code].case:
				file = File(os.path.join(IMG_FOLDER_PATH, str(guild_id), filename(f'{name}_{case}.png')))
				files.append(file)
			await interaction.followup.send(embeds=[Embeds.setting(title),chara_embed], files=files)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="변경", description="커뮤에서 사용할 NPC 정보를 변경합니다.")
	@app_commands.rename(color="캐릭터색상", icon1="아이콘1",icon2="아이콘2",icon3="아이콘3",icon4="아이콘4")
	@app_commands.describe(
		color="캐릭터의 채팅창 색상 예) #4F231E",
		icon1="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.",
		icon2="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.",
		icon3="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.",
		icon4="캐릭터를 표시하는 아이콘. 정사각형 형태의 그림을 넣어주세요.")
	async def update_NPC_slash(self, interaction:discord.Interaction, 
						color:str='',
						icon1:discord.Attachment=None,
						icon2:discord.Attachment=None,
						icon3:discord.Attachment=None,
						icon4:discord.Attachment=None,):
		"""
		NPC를 변경합니다.
		이름, 키워드(옵션), 설명을 등록합니다.
		이미지를 첨부할 시 해당 이미지를 아이콘으로 사용합니다. 첨부되지 않은 경우 기본 아이콘이 사용됩니다.
		이미지 사이즈 300x300
		"""
		await self.on_ready(interaction, check_user=False, check_chara=False)
		try:
			guild_id = interaction.guild_id

			data = [[self.npc[code].name, code] for code in self.npc.keys()]
			select_view = Views.UpdateNPC(data, self.npc)
			await interaction.response.send_message(embed=Embeds.setting('변경할 NPC를 선택해 주세요'), view=select_view)
			await select_view.wait()
			if select_view.cancel: return
			code = select_view.select.values[0]

			# NPC 색상
			if color:
				try:
					color = int(color, 16)
					Color(color)
					print('direct',color)
				except:
					color_code = color.replace('#','0x') if color.startswith('#') else f'0x{color}'
					color = int(color_code, 16)
					print('convert',color)

			name = select_view.modal.name.value
			vers1 = select_view.modal.vers1.value
			vers2 = select_view.modal.vers2.value
			vers3 = select_view.modal.vers3.value
			vers4 = select_view.modal.vers4.value
			vers_list = [
				[vers1.split('/')[0], '/'.join(vers1.split('/')[1:])],
				[vers2.split('/')[0], '/'.join(vers2.split('/')[1:])],
				[vers3.split('/')[0], '/'.join(vers3.split('/')[1:])],
				[vers4.split('/')[0], '/'.join(vers4.split('/')[1:])],
			]
			title = f"NPC {name}을/를 등록하였습니다."
			self.connector.update_NPC_info(code, name, Color)

			self.npc[code].number = 0
			self.npc[code].case = []
			self.npc[code].vers = []

			for vers_data in vers_list:
				case, vers = vers_data
				if vers:
					path = os.path.join(IMG_FOLDER_PATH, str(guild_id), filename(f'{name}_{case}.png'))
					
					if vers_list.index(vers_data) == 0:
						icon = icon1
					elif vers_list.index(vers_data) == 1:
						icon = icon2
					elif vers_list.index(vers_data) == 2:
						icon = icon3
					elif vers_list.index(vers_data) == 3:
						icon = icon4
					
					if icon:
						if icon.height > 300 or icon.width > 300:
							await resize_img(icon, path)
						else:
							await icon.save(path)
					else:
						shutil.copy(resource_path(IMG_FOLDER_PATH,'sample.png'), path)
					
					self.connector.set_NPC_vers(code, case, vers)
			chara_embed = Embeds.show_npc(self.npc[code])
			files = []
			for case in self.npc[code].case:
				file = File(os.path.join(IMG_FOLDER_PATH, str(guild_id), filename(f'{name}_{case}.png')))
				files.append(file)
			await interaction.followup.send(embeds=[Embeds.setting(title),chara_embed], files=files, ephemeral=True)
			# id = interaction.user.id
			# code = self.user[id].charas
			# before_name = self.charas[code].name
			# modal=Views.NPCInfo(f"{before_name} 정보", self.npc[code])
			# await interaction.response.send_modal(modal)
			# await modal.wait()
			# if not modal.finish: return
			# name = modal.name.value
			# if icon:
			# 	if icon.height > 300 or icon.width > 300:
			# 		await resize_img(icon, path)
			# 	else:
			# 		await icon.save(path)
			# self.connector.update_charactor_data(code, name, keyword, desc, link)
			# chara_embed, icon = Embeds.show_chara(self.charas[code], path)
			# await interaction.followup.send(embeds=[Embeds.setting(f"NPC {name}의 정보가 변경되었습니다."),chara_embed], file=icon, ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	@app_commands.command(name="삭제", description="NPC를 삭제합니다.")
	async def delete_NPC_slash(self, interaction:discord.Interaction):
		"""
		자신의 캐릭터를 삭제합니다.
		"""
		await self.on_ready(interaction, check_user=False, check_chara=False)
		try:
			guild_id = interaction.guild_id
			data = [[self.npc[code].name, code] for code in self.npc.keys()]
			select_view = Views.RemoveNPC(data)
			await interaction.response.send_message(embed=Embeds.setting('삭제할 NPC를 선택해 주세요'), view=select_view)
			await select_view.wait()
			if select_view.cancel: return
			code = select_view.select.values[0]
			name = self.npc[code].name
			cases = self.npc[code].case

			self.connector.delete_NPC_data(code)

			for case in cases:
				path = os.path.join(IMG_FOLDER_PATH, str(guild_id), filename(f'{name}_{case}.png'))
				os.remove(path)
		except Exception as e:
			self.bot.logger.error(e)

	class NPC_Vers_Num(discord.enums.Enum):
		대사1 = 0
		대사2 = 1
		대사3 = 2
		대사4 = 3

	async def NPC_talk(self, inter:discord.Interaction, code, vers):
		npc = self.npc[code]
		content = vers
		color = npc.color or Color.brand_green()
		target_case = npc.case[npc.vers.index(vers)]
		path = os.path.join(IMG_FOLDER_PATH, str(inter.guild_id), filename(f'{npc.name}_{target_case}.png'))
		embedmsg, icon = Embeds.chara_talk(self.npc[code], path, content, color)
		# print(icon.filename)
		files = [icon]
		channel_name = inter.channel.name
		webhook = list(filter(lambda x:x.name == f"{channel_name} Chat", await inter.guild.webhooks()))
		# print(webhook)
		if not webhook: 
			webhook = await inter.channel.create_webhook(name=f"{channel_name} Chat")
		else: 
			webhook = webhook[0]
		# if message.reference:
		# 	print(message.reference)
		# 	# msg = await message.channel.fetch_message(message.reference.message_id)
		# 	# await msg.reply(embed=embedmsg, files=files)
		# 	print(await webhook.fetch())
		# 	msg = await webhook.fetch_message(message.reference.message_id)
		# 	await msg.reply(embed=embedmsg, files=files)
		# else:
		# 	await webhook.send(embed=embedmsg, files=files, username=chara.name, avatar_url=message.author.display_avatar.url, wait=True)
		await webhook.send(embed=embedmsg, files=files, 
										 username=npc.name, 
										 avatar_url=inter.user.display_avatar, 
										 wait=True)
		# await webhook.delete()

	@app_commands.command(name="대사", description="NPC의 대사를 출력합니다.")
	@app_commands.rename(number="출력대사")
	@app_commands.describe(number="출력할 대사를 선택합니다. 대사의 번호를 선택해 주세요")
	async def NPC_chat_slash(self, interaction:discord.Interaction,
													number:NPC_Vers_Num):
		"""
		NPC의 대사를 사용합니다.

		"""
		await self.on_ready(interaction, check_user=False, check_chara=False)
		try:
			data = [[self.npc[code].name, code] for code in self.npc.keys()]
			select_view = Views.SelectNPC(data)

			await interaction.response.send_message(embed=Embeds.setting('변경할 NPC를 선택해 주세요'), view=select_view)
			await select_view.wait()
			if select_view.cancel: return
			code = select_view.select.values[0]

			npc = self.npc[code]
			if number.value >= npc.number:
				total_vers = [npc.case[npc.vers.index(vers)]+' / '+vers for vers in npc.vers]
				return await interaction.channel.send(embed=Embeds.general(f'현재 {npc.name}의 대사는 {npc.number}개 등록되어 있습니다', f'사용 가능한 대사:\n{total_vers}'))
			target_vers = npc.vers[number.value]
			await self.NPC_talk(interaction, code, target_vers)
		except Exception as e:
			self.bot.logger.error(e)

async def setup(bot:commands.Bot):
	await bot.add_cog(Community(bot))
	bot.tree.add_command(CharaGroup(bot=bot, name="캐릭터", description="커뮤 캐릭터를 등록하거나 관리합니다."))
	bot.tree.add_command(NPCGroup(bot=bot, name="npc", description="커뮤 NPC를 등록하거나 관리합니다."))

	
