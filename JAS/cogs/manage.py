import discord, os
from discord import Permissions, Color, PermissionOverwrite
from discord.abc import GuildChannel
from JAS.resources.Exceptions import *
from JAS.resources.Base import commands, app_commands, CommandBase, AppCommandBase, Embeds, Views
from JAS.resources.Addons import resource_path

class Manage(CommandBase):
	@commands.Cog.listener()
	async def on_member_join(self, member:discord.Member):
		guild_id = member.guild.id
		await self.__get_connection__(guild_id)
		role = list(filter(lambda x:x.name==self.role.visitor, member.guild.roles))[0]
		await member.add_roles(role)
	
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction:discord.Reaction, user:discord.Member):
		if not user.bot and reaction.message.type == discord.MessageType.chat_input_command:
			poll_msg = discord.utils.get(self.bot.cached_messages, id=reaction.message.id)
			for reac in poll_msg.reactions:
				async for reac_user in reac.users():
					if user == reac_user:
						if str(reac.emoji) != str(reaction.emoji):
							await poll_msg.remove_reaction(reac.emoji, user)

	@commands.command(hidden=True)
	@commands.has_any_role('관리자')
	async def sync(self, ctx:commands.Context):
		try:
			print('start sync')
			waitmsg = await ctx.send(embed=Embeds.setting('/명령어 동기화를 시작합니다','잠시만 기다려 주세요'))
			self.bot.tree.copy_global_to(guild=discord.Object(id=ctx.guild.id))
			comm_list = await self.bot.tree.sync(guild=ctx.guild)
			print(comm_list)
			print(f'sync complete on {ctx.guild.name}')
			await waitmsg.edit(embed=Embeds.setting('/명령어가 동기화 되었습니다','지금부터 /명령어를 사용할 수 있습니다.'))
		except Exception as e:
			self.bot.logger.error(e)
			
	@commands.command(hidden=True)
	@commands.has_any_role('관리자')
	async def total_reset(self, ctx:commands.Context):
		msg:discord.Message = await ctx.send(embed=Embeds.setting('/명령어 초기화를 시작합니다','잠시만 기다려 주세요'))
		self.bot.tree.clear_commands(guild=None)
		await self.bot.tree.sync(guild=None)
		for guild in self.bot.guilds:
			self.bot.tree.clear_commands(guild=guild)
			await self.bot.tree.sync(guild=guild)
		await self.bot.reload_extensions(self)
		print(list(map(lambda x: x.name, self.bot.commands)))
		print(list(map(lambda x: x.name, await self.bot.tree.fetch_commands(guild=None))))
		await msg.edit(embed=Embeds.setting('/명령어가 초기화 되었습니다'))
					
	@commands.command(hidden=True)
	@commands.has_any_role('관리자')
	async def showDB(self, message:commands.Context,
			category:str=None):
		categories = [
			"setting",
			"user",
			"fishing",
			"gather",
			"items",
			"merge",
			"inventory",
			"store",
			"chara",
			"npc",
		]
		if category and category not in categories:
			return await message.send(embed=Embeds.setting(f'사용 가능한 목록은 다음과 같습니다.{", ".join(categories)}'))
		DB_data = self.connector.data
		print(DB_data)
		if category:
			index = categories.index(category)
			contents = [DB_data.showDB()[index]]
		else:
			contents = DB_data.showDB()				
				
		for content in contents:
			if len(content) > 1990:
				rowmsg = ''
				for row in content.split('\n'):
					if len(rowmsg) + len(row) > 1980:
						await message.send(f'```{rowmsg}```')
						rowmsg = ''
					rowmsg = rowmsg + row + '\n'
				if rowmsg:
					await message.send(f'```{rowmsg}```')
			else:
				await message.send(f'```{content}```')

	@commands.command(name="업데이트", hidden=True)
	@commands.has_any_role('관리자')
	async def update_data(self, ctx:commands.Context):
		try:
			guild_id = ctx.guild.id

			self.bot.var_manage[guild_id].data = self.bot.var_manage[guild_id].__get_data__()
			await ctx.send(embed=Embeds.general('','업데이트가 완료되었습니다'))
		except Exception as e:
			self.bot.logger.error(e)

	@commands.command(hidden=True)
	@commands.has_any_role('관리자')
	async def 서버정보(self, ctx:commands.Context):
		"""
		현재 서버 정보를 표시합니다.
		표시되는 정보: 서버 ID
		"""
		await ctx.send(f'현재 서버 ID는 `{ctx.guild.id}`입니다.')

	async def get_user_list(self, data:list[discord.Member]):
		result = []
		async for user in data:
			if not user.bot:
				name = user.display_name
				id = user.id
				result.append([id, name])
		return result

	#회원가입
	@app_commands.command(name="가입", description="커뮤에서 활동하기 위해 회원가입을 진행합니다. 가입 혀용 상태에서만 가능합니다.")
	async def register_slash(self, interaction:discord.Interaction):
		"""
		회원가입을 진행합니다.
		회원가입은 가입허용 상태에서만 진행 가능합니다.
		"""
		await self.on_ready(interaction, check_user=False, check_chara=False)
		try:
			if self.setting.accept_user:
				username = interaction.user.display_name
				user_id = interaction.user.id

				if self.connector.check_user(user_id):
					await interaction.response.send_message(embed=Embeds.setting('이미 등록된 사용자입니다.'), ephemeral=True)
				else:
					reg_role = list(filter(lambda x:x.name==self.role.registered, interaction.guild.roles))[0]
					visit_role = list(filter(lambda x:x.name==self.role.visitor, interaction.guild.roles))[0]
					await interaction.user.remove_roles(visit_role)
					await interaction.user.add_roles(reg_role)
					id = list(filter(lambda x: x.name == self.channel.anon, interaction.guild.text_channels))[0].id
					private = await interaction.guild.get_channel(id).create_thread(
						name=f'{interaction.user.display_name} 전용 익명방',
						type=discord.ChannelType.private_thread,
						message=None,
						invitable=False)
					await private.send(embed=Embeds.guide_user(username))
					private.id
					self.connector.set_user(user_id, username, private.id)
					await private.add_user(interaction.user)
					await interaction.response.send_message(embed=Embeds.setting(f'회원가입이 완료되었습니다. 환영합니다 {username}님!'))
			else:
				await interaction.delete_original_response()
				await interaction.channel.send(embed=Embeds.warning('현재는 회원가입을 할 수 없습니다','허용이 되기 전까지 기다려 주시기 바랍니다.'))
		except ConnectionError as e:
			self.bot.logger.warn(e,'Error: register failed')
			await interaction.response.send_message(embed=Embeds.warning('등록 중 오류가 발생하였습니다. 잠시 후 다시 시도해 주시기 바랍니다.'))
		except Exception as e:
			self.bot.logger.error(e)

	# 회원탈퇴
	@app_commands.command(name="탈퇴", description="탈퇴하여 회원정보를 삭제합니다. 해당 명령어는 복구할 수 없습니다.")
	async def delete_user_slash(self, interaction:discord.Interaction):
		"""
		탈퇴를 진행합니다.
		회원정보가 모두 삭제됩니다.
		"""
		await self.on_ready(interaction, check_chara=False)
		try:
			name = interaction.user.display_name
			# thread = list(filter(lambda x: x.name == f"{name} 전용 익명방", interaction.guild.threads))
			thread = self.user[interaction.user.id].thread
			for role in interaction.user.roles:
				if role.name != '@everyone' and role.name != self.role.admin:
					await interaction.user.remove_roles(role)
			visitor = discord.utils.get(interaction.guild.roles, name=self.role.visitor)
			await interaction.user.add_roles(visitor)
			if thread:
				await interaction.guild.get_channel_or_thread(thread).delete()
			else:
				print('thread not found')
			self.connector.delete_user(interaction.user.id)
			await interaction.response.send_message(embed=Embeds.setting(f"{name}의 탈퇴절차가 완료되었습니다."), ephemeral=True)
		except Exception as e:
			self.bot.logger.error(e)

	# 회원목록
	@commands.command()
	async def 회원목록(self, ctx:commands.Context):
		"""
		현재 서버 내의 유저 목록을 보여줍니다.
		"""
		user_list = self.connector.get_user_list()
		result = ''
		for user in user_list:
			result = result+'\n'+user[1]
		print(result)
		await ctx.send(embed=Embeds.general('현재 등록된 사용자 입니다.',result))

	@app_commands.command(name="공지", description="임베드된 공지를 작성합니다.")
	@app_commands.rename(title="제목",body="내용", pin="고정여부")
	@app_commands.choices(pin=[
		app_commands.Choice(name='등록',value='Y'),
		app_commands.Choice(name='미등록',value='N'),
	])
	@app_commands.checks.has_role('관리자')
	async def notice(self, inter:discord.Interaction, title:str, body:str, pin:str='Y'):
		"""
		임베드된 공지를 작성합니다.
		"""
		msg = await inter.channel.send(embed=Embeds.general(title, body))
		if pin == 'Y': await msg.pin()
		await inter.response.send_message('공지를 게시하였습니다.',delete_after=3,ephemeral=True)

	@app_commands.command(name="문의", description="익명 문의를 남깁니다. 해당 문의에 대한 답변은 QnA에 등재됩니다.")
	@app_commands.rename(args="문의내용", attachment="첨부파일")
	@app_commands.describe(args="문의하고자 하는 내용", attachment="문의 내용과 관련된 첨부파일")
	async def submit_ticket(self, interaction: discord.Interaction, args:app_commands.Range[str,1,2000], attachment:discord.Attachment=None):
		"""
		익명문의를 진행합니다.
		관리자에게 문의하고픈 내용을 작성하여 전송한다.
		"""
		await self.on_ready(interaction, check_chara=False, check_user=False)
		try:
			comment = args
			if attachment:
				file = await attachment.to_file()
			else:
				file = None
			channel = discord.utils.get(interaction.guild.text_channels, name=self.channel.manage)
			await interaction.response.send_message(embed=Embeds.setting("접수가 완료되었습니다."),ephemeral=True, delete_after=5)
			response_view = Views.Ticket(comment)
			await channel.send(embed=Embeds.setting('익명문의가 접수되었습니다',comment), file=file, view=response_view)
			await response_view.wait()
			if response_view.cancel: return
			answer = response_view.modal.content
			qna_channel = discord.utils.get(interaction.guild.text_channels, name=self.channel.qna)
			await qna_channel.send(embed=Embeds.anon_qna(comment, answer))
		except Exception as e:
			self.bot.logger.error(e)
		
	@commands.command(name="봇이름", hidden=True)
	@commands.has_any_role('관리자')
	@commands.has_permissions(change_nickname=True)
	async def change_bot_nick(self, ctx:commands.Context,
													 nick=commands.parameter(displayed_name="닉네임", description="표시할 봇의 이름")):
		"""
		봇의 이름을 변경합니다.
		실제 이름이 아닌 표시되는 이름이 변경됩니다.
		"""
		if not nick:
			return await ctx.send(embed=Embeds.general('닉네임이 입력되지 않았습니다','봇이 사용할 닉네임을 입력해 주시기 바랍니다.'), delete_after=10)
		else:
			await ctx.guild.me.edit(nick=nick)
			await ctx.send(embed=Embeds.setting('봇의 이름이 변경되었습니다', f'이제부터 저를 {nick}이라고 불러주세요.'))

	async def set_channel_permission(self, channel:discord.TextChannel, overite:dict[discord.Role, discord.PermissionOverwrite]):
		for role in list(overite.keys()):
			await channel.set_permissions(role, overwrite=overite[role])


	@commands.command(name="관리", hidden=True)
	@commands.has_any_role('관리자')
	async def manage(self, ctx:commands.Context, *,
				args:str=commands.parameter(displayed_name="메뉴명-",default=None, description="각 관리 카테고리. 바로 해당 카테고리로 이동 가능하다.")):
		"""
		!관리자 전용
		서버 내 혹은 커뮤 봇의 각종 설정을 관리합니다.
		
		사용법
		!관리 (메뉴명)
		"""
		try:
			selectembeds={
				None : Embeds.setting('관리자 설정을 시작합니다','원하시는 대상을 선택해 주세요.'),
				"유저" : Embeds.setting('유저 관리','각 유저에 대한 관리를 진행합니다.','[관리 ▶ 유저]'),
				"유저 정보" : Embeds.setting('유저 정보 확인','확인하고자 하는 사용자를 선택해 주세요','[관리 ▶ 유저 ▶ 정보]'),
				"인벤토리" : Embeds.setting('인벤토리 관리', '각 유저의 인벤토리를 확인하고 내용을 수정랍니다.','[관리 ▶ 인벤토리]'),
				"인벤토리 골드" : Embeds.setting('유저 골드 추가', '골드를 지급할 유저와 금액을 선택해 주세요.','[관리 ▶ 인벤토리 ▶ 골드]'),
				"인벤토리 크기" : Embeds.setting('유저 인벤토리 추가', '인벤토리 크기를 조정할 유저를 선택해 주세요','[관리 ▶ 인벤토리 ▶ 크기]'),
				"스탯" : Embeds.setting('스탯 관리', '스탯과 관련된 관리를 진행합니다.','[관리 ▶ 스탯]'),
				"스탯 변경" : Embeds.setting('스탯 변경', '스탯 명을 변경하시겠습니까?\n`입력방법:(스탯명),(스탯명),...`\n스탯을 사용하지 않는다면 공란으로 비워주시기 바랍니다.','[관리 ▶ 스탯 ▶ 변경]'),
				"시스템" : Embeds.setting('시스템 관리', '봇의 각종 수치를 변경하고 확인합니다.','[관리 ▶ 시스템]'),
				"시스템 확인" : Embeds.show_system("현재 설정을 표시합니다.", self.setting,'[관리 ▶ 시스템 ▶ 확인]'),
				"시스템 회원가입" : Embeds.user_accept(self.connector,'[관리 ▶ 시스템 ▶ 회원가입]'),
				"시스템 변경" : Embeds.setting('시스템 기본수치 변경', '변경할 설정 값을 선택해 주세요.','[관리 ▶ 시스템 ▶ 변경]'),
			}
			selectviews={
				None : Views.ManageView(),
				"유저" : Views.UserManageView(),
				"유저 정보": Views.UserInfo(self.connector, await self.get_user_list(ctx.guild.fetch_members(limit=None))),
				"인벤토리" : Views.InventoryManageView(self.connector),
				"인벤토리 골드" : Views.InventoryGoldChange(self.connector, await self.get_user_list(ctx.guild.fetch_members(limit=None))),
				"인벤토리 크기" : Views.InventorySizeChange(self.connector, await self.get_user_list(ctx.guild.fetch_members(limit=None))),
				"스탯" : Views.StatManageView(self.connector),
				"스탯 변경" : Views.StatNameChange(self.connector),
				"시스템" : Views.SystemManageView(),
				"시스템 확인" : None,
				"시스템 회원가입" : Views.RegView(self.connector),
				"시스템 변경" : Views.ChangeSettingView(self.connector),
			}
			embeded=selectembeds[args] #or discord.Embed()
			messageview=selectviews[args] #or view.ManageView()
			
			msg = await ctx.send(embed=embeded, view=messageview)
			while True:
				await msg.edit(embed=embeded, view=messageview)
				if messageview:
					await messageview.wait()
					print(f'result: {messageview.result} | cancel: {messageview.cancel}')
					if messageview.cancel:
						await msg.delete()
						break
					if not messageview.result:
						break
				else:
					break
				key = messageview.result
				embeded = selectembeds[key]
				messageview = selectviews[key]
		except KeyError as e:
			return await ctx.send(embed=Embeds.warning('존재하지 않는 메뉴명입니다', f'사용 가능한 메뉴명은 다음과 같습니다.\n{", ".join(list(filter(lambda x: x ,selectembeds.keys())))}'))
		except Exception as e:
			self.bot.logger.error(e)

	# 커뮤 구축
	@commands.command(name="서버구축", hidden=True)
	@commands.has_permissions(manage_channels=True, manage_guild=True, manage_messages=True, manage_roles=True)
	@commands.bot_has_guild_permissions(manage_channels=True, manage_guild=True, manage_messages=True, manage_roles=True)
	async def setup_guild(self, ctx:commands.Context, 
					 arg=commands.parameter(displayed_name="재구축:", default=None, description="서버 재구축시 사용.")):
		"""
		최초 서버 설정시 사용.
		"""
		print('start')
		main_msg = await ctx.send(embed=Embeds.setting("서버구축을 시작합니다","대략 2~3분 정도의 시간이 소요되오니 잠시만 기다려 주세요."))
		guild = ctx.guild
		cog_list = list(self.bot.cogs.keys())
		try:
			channels = list(map(lambda x: x.name , guild.text_channels))
			categories = list(map(lambda x: x.name , guild.categories))
			forums = list(map(lambda x: x.name , guild.forums))
			roles = list(map(lambda x: x.name , guild.roles))
			print(f'''
{channels}
{categories}
{forums}
{roles}
			''')

			# 역할 설정
			everyone_permission = Permissions(view_channel=True, read_message_history=False)

			await guild.default_role.edit(permissions=everyone_permission)

			if "관리자" not in roles:
				admin = await guild.create_role(
					name="관리자",
					color=Color.gold(),
					permissions=Permissions.all(),
					hoist=True,
					mentionable=True)
				ctx.author.add_roles(admin)
			else:
				admin = list(filter(lambda x: x.name=="관리자", guild.roles))[0]
				await admin.edit(permissions=Permissions.all())
			
			await ctx.author.add_roles(admin)

			if "가입자" not in roles:
				user = await guild.create_role(
					name="가입자",color=Color.green(),
					permissions=Permissions(448891571264),
					hoist=True)
			else:
				user = list(filter(lambda x: x.name=="가입자", guild.roles))[0]
				await user.edit(permissions=Permissions(448891571264))

			if "방문자" not in roles:
				visitor = await guild.create_role(
					name="방문자",
					color=Color.greyple(),
					permissions=Permissions.none())
			else:
				visitor = list(filter(lambda x: x.name=="방문자", guild.roles))[0]
				await visitor.edit(permissions=Permissions.none())

			bot_role = discord.utils.get(guild.roles, name='JAS')

			# 권한 설정
			admin_overwrites = {
				bot_role:PermissionOverwrite(administrator=True),
				visitor:PermissionOverwrite(view_channel=False),
				user:PermissionOverwrite(view_channel=False),
				guild.default_role:PermissionOverwrite(view_channel=False),
			}
			announce_overwrite={
				visitor:PermissionOverwrite(view_channel=True,
																read_message_history=True),
				user:PermissionOverwrite(view_channel=True,
														 read_message_history=True,
														 send_messages=False),
			}
			general_overwrites={
				visitor:PermissionOverwrite(view_channel=False),
				user:PermissionOverwrite(view_channel=True,
														 read_messages=True,
														 send_messages=True,
														 use_application_commands=True,
														 read_message_history=True,
														 embed_links=True,
														 attach_files=True,
														 add_reactions=True,
														 send_messages_in_threads=True),
			}
			join_overites={
				user:PermissionOverwrite(view_channel=False),
				visitor:PermissionOverwrite(view_channel=True,
																send_messages=True,
																use_application_commands=True),
			}
			anon_overwrites={
				visitor:PermissionOverwrite(view_channel=False),
				user:PermissionOverwrite(view_channel=True,
														 send_messages=False,
														 read_message_history=True,
														 use_application_commands=True,
														 attach_files=True,
														 send_messages_in_threads=True),
			}
			community_overwrites={
				visitor:PermissionOverwrite(view_channel=False),
				user:PermissionOverwrite(view_channel=True,
														 send_messages=False, 
														 read_message_history=True,
														 use_application_commands=True,
														 create_public_threads=True,
														 embed_links=True,
														 attach_files=True,
														 add_reactions=True,
														 send_messages_in_threads=True),
			}

			# 카테고리 확인
			if "일반 채팅" not in categories:
				chat_cat = await guild.create_category(name="일반 채팅", position=1, overwrites=general_overwrites)
			else:
				chat_cat = discord.utils.get(guild.categories, name="일반 채팅")
				await self.set_channel_permission(chat_cat, general_overwrites)
			if "공지사항" not in categories:
				notice_cat = await guild.create_category(name="공지사항", position=0, overwrites=announce_overwrite)
			else:
				notice_cat = discord.utils.get(guild.categories, name="공지사항")
				await self.set_channel_permission(notice_cat, announce_overwrite)
			if self.channel.community not in categories and 'Community' in cog_list:
				comm_cat = await guild.create_category(name=self.channel.community, position=2, overwrites=community_overwrites)
			else:
				comm_cat = discord.utils.get(guild.categories, name=self.channel.community)
				await self.set_channel_permission(comm_cat, community_overwrites)
			if 'Fishing' in cog_list:
				if "낚시터" not in categories:
					fishing_cat = await guild.create_category(name="낚시터", position=3)
				else:
					fishing_cat = discord.utils.get(guild.categories, name="낚시터")
				await fishing_cat.edit(overwrites=general_overwrites)
			if 'Gather' in cog_list:
				if "채집터" not in categories:
					gather_cat = await guild.create_category(name="채집터", position=4)
				else:
					gather_cat = discord.utils.get(guild.categories, name="채집터")
				await gather_cat.edit(overwrites=general_overwrites)
			if "관리자" not in categories:
				admin_cat = await guild.create_category(name="관리자", position=5, overwrites=admin_overwrites)
			else:
				admin_cat = discord.utils.get(guild.categories, name="관리자")
				await admin_cat.edit(overwrites=admin_overwrites)

			# 관리 생성
			if self.channel.manage not in channels:
				administor = await guild.create_text_channel(name=self.channel.manage, category=admin_cat)
			else:
				administor = discord.utils.get(guild.text_channels, name=self.channel.manage)
				# id = list(filter(lambda x: x.name == self.channel.manage, guild.text_channels))[0].id
				# administor = guild.get_channel(id)

			# 공지 생성
			if "공지" not in channels:	
				public = await guild.create_text_channel(position=0, name="공지", category=notice_cat)
			else:
				public = discord.utils.get(guild.text_channels, name="공지")
				await public.move(category=notice_cat, beginning=True)
			# 규칙 생성
			if "규칙" not in channels:
				rules = await guild.create_text_channel(position=1, name="규칙", category=notice_cat)
			else:
				rules = discord.utils.get(guild.text_channels, name="규칙")
				await rules.move(category=notice_cat, beginning=True, offset=1)
			# 세계관 생성
			if "세계관" not in channels:
				world = await guild.create_text_channel(position=2, name="세계관", category=notice_cat)
			else:
				world = discord.utils.get(guild.text_channels, name="세계관")
				await world.move(category=notice_cat, beginning=True, offset=2)
			# 가입 생성
			if "가입" not in channels:
				join = await guild.create_text_channel(position=3, name=self.channel.join, category=notice_cat, reason="/가입을 진행해 주세요", overwrites=join_overites)
			else:
				join = discord.utils.get(guild.text_channels, name=self.channel.join)
				await join.edit(overwrites=join_overites)
				await join.move(category=notice_cat, beginning=True, offset=3)
			# QnA 생성
			if "질의응답" not in channels:
				qna = await guild.create_text_channel(position=4,name="질의응답", category=notice_cat)
			else:
				qna = discord.utils.get(guild.text_channels, name="질의응답")
				await qna.move(category=notice_cat, beginning=True, offset=4)
			# 익명
			if "오너게시판" not in channels:
				author = await guild.create_text_channel(name="오너게시판", category=chat_cat, 
										reason="개인 스레드에서 보낸 익명 메세지가 모이는 곳입니다.\n개인 스레드가 보이지 않는다면 우측 상단의 스레드를 통해 확인 바랍니다.")
				msg = await author.send("""> ## 오너게시판
> 
> 자유롭게 대화할 수 있는 게시판 입니다. 텍관모집, 이벤트 조율 등등의 내용을 진핼할 때 이용 가능합니다.
""")
				await msg.pin()
			else:
				author = discord.utils.get(guild.text_channels, name="오너게시판")
				await author.move(category=chat_cat, beginning=True)
			# 익명
			if "익명게시판" not in channels:
				anon = await guild.create_text_channel(name="익명게시판", category=chat_cat, 
										reason="개인 스레드에서 보낸 익명 메세지가 모이는 곳입니다.\n개인 스레드가 보이지 않는다면 우측 상단의 스레드를 통해 확인 바랍니다.",
										overwrites=anon_overwrites)
			else:
				anon = discord.utils.get(guild.text_channels, name=self.channel.anon)
				await anon.edit(overwrites=anon_overwrites)
				await anon.move(category=chat_cat, beginning=True, offset=1)
			# 한역
			if "캐입역극" not in channels:
				comm = await guild.create_text_channel(name="캐입역극", category=chat_cat, 
										reason="캐입역극을 진행 가능합니다.(=탐라대화)\n개인 간의 한역을 위한 스레드 생성 시 원하는 대화에 답글을 작성한 뒤 해당 답글을 바탕으로 스레드를 생성하시길 바랍니다.",)
			else:
				comm = discord.utils.get(guild.text_channels, name="캐입역극")
				await comm.move(category=comm_cat, beginning=True)
			# 상점
			if 'Store' in cog_list:
				if "상점" not in channels:
					store = await guild.create_text_channel(name="상점", category=chat_cat)
				else:
					store = discord.utils.get(guild.text_channels, name="상점")
					await store.move(category=chat_cat, beginning=True, offset=2)
			# 낚시터
			if 'Fishing' in cog_list:
				if "기본-낚시터" not in channels:
					fishing = await guild.create_text_channel(name="기본-낚시터", category=fishing_cat, reason="낚시 채널입니다. /낚시로 낚시를 시작해 보세요!")
					msg = await fishing.send(content='''> ## 낚시
	> 
	> `/낚시` 명령어를 통해 낚시를 진행할 수 있습니다.
	> `/물고기목록` 명령어를 통해 낚을 수 있는 물고기를 확인해 보세요!
	''')
					await msg.pin()
				else:
					fishing = discord.utils.get(guild.text_channels, name="기본-낚시터")
					await fishing.move(category=fishing_cat, beginning=True)
			# 채집터
			if 'Gather' in cog_list:
				if "기본-채집터" not in channels:
					gather = await guild.create_text_channel(name="기본-채집터", category=gather_cat, reason="채집용 채널입니다! /채집을 진행해 보세요!")
					msg = await gather.send(content='''> ## 채집
	> 
	> `/채집` 명령어를 통해 채집을 진행할 수 있습니다.
	> `/채집목록` 명령어를 통해 수집 가능한 아이템을 확인해 보세요!
	''')
					await msg.pin()
				else:
					gather = discord.utils.get(guild.text_channels, name="기본-채집터")
					await gather.move(category=gather_cat, beginning=True)
			
			try:
				# 조사게시판?
				# 가입 가이드라인 출력
				await guild.edit(
					community = True,
					rules_channel=rules,
					public_updates_channel=administor,
					preferred_locale=discord.Locale.korean)
				# 한역 생성
				if "토론" not in forums:
					tags = (
						discord.ForumTag(name="마감"),
						discord.ForumTag(name="이어가요"),
						discord.ForumTag(name="중단해요")
					)
					topic = """
					토론을 진행할 수 있는 공간입니다.
					"""
					talk = await guild.create_forum(name="토론", topic=topic, category=chat_cat, available_tags=tags)
				else:
					id = list(filter(lambda x: x.name == "토론", guild.forums))[0].id
					talk = guild.get_channel(id)

				await main_msg.edit(embed=Embeds.setting("서버구축이 완료되었습니다"))
			except:
				await main_msg.edit(embed=Embeds.setting("서버구축이 일부 완료되었습니다",'커뮤니티 설정이 완료되지 않았습니다.\n커뮤니티 기능을 사용하길 원하신다면 커뮤니티를 활성화 한 후 `!서버구축`을 실행해 주시기 바랍니다.'))
		except Exception as e:
			self.bot.logger.error(e)

async def setup(bot:commands.Bot):
	await bot.add_cog(Manage(bot))