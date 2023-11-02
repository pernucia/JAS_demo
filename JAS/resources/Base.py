import discord, os
import logging, logging.handlers, multiprocessing
from traceback import format_exc
from discord import app_commands
from discord.ext import commands, tasks
from JAS.resources import Embeds, Views
from JAS.resources.Connector import Connector
import JAS.resources.Connector as Conn
from JAS.resources.Addons import MAIN_PATH, resource_path
from asyncio import sleep

class Logger:
	PROFILE = ''
	
	def __init__(self, logger:logging.Logger) -> None:
		self.logger = logger
		# self.bot.logger.info('=====bot.Logger======')

	def info(self, message):
		self.logger.info(message)
		if self.PROFILE != '테스트':
			print(message)

	def debug(self, message):
		self.logger.debug(message)
		if self.PROFILE != '테스트':
			print(message)

	def warn(self, exception, status='Unkown Error Occured'):
		self.logger.warn(status)
		self.logger.warn(str(exception))
		self.logger.warn(format_exc())
		if self.PROFILE != '테스트':
			print('>> ',status)
			print(exception)
			print(format_exc())

	def error(self, exception, status='Unkown Error Occured'):
		self.logger.error(status)
		self.logger.error(str(exception))
		self.logger.error(format_exc())
		if self.PROFILE != '테스트':
			print('>> ',status)
			print(exception)
			print(format_exc())
		raise exception
	
logger_tmp = logging.getLogger('discord')
logger_tmp.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(
		filename=os.path.join(MAIN_PATH, 'discord.log'),
		encoding='utf-8',
		maxBytes=32 * 1024 * 1024,  # 32 MiB
		backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger_tmp.addHandler(handler)

logger = Logger(logger_tmp)


class JAS(commands.Bot):
	rec_queue:multiprocessing.Queue=None
	send_queue:multiprocessing.Queue=None
	TOKEN:str = ''
	AUTH_JSON_PATH:str = ''
	PROFILE:str = ''
	TEST_SERVER_ID:int = 0
	_version = 'demo'
	is_quit = False

	def __init__(self, *, intents: discord.Intents, command_prefix:str, activity:discord.CustomActivity, logger):
		self.var_manage:dict['server_id':int, Connector] = {}
		self.var_registered:bool = False
		self.var_proceed:bool = False
		self.ver_cog_commands:dict['cog_name':str,list['command_name':str]] = {}
		self.ver_admin_commands:list['command_name':str] = []	
		super().__init__(intents=intents, command_prefix=command_prefix, activity=activity)
		self.logger:Logger = logger
		self.tree.error(coro=self.on_app_command_error)
	
	# 확장코드 등재
	async def load_extensions(self, bot:commands.Bot):
		for filename in os.listdir(resource_path('JAS','cogs')):
			if filename.startswith('setup') or filename.startswith("_"):
				continue
			if filename.endswith('.py'):
				await bot.load_extension(f'JAS.cogs.{filename[:-3]}')
				self.logger.info(f'load complete: {filename[:-3]}')

	# 확장코드 등재
	async def reload_extensions(self, bot:commands.Bot):
		for filename in os.listdir(resource_path('JAS','cogs')):
			if filename.startswith('setup') or filename.startswith("_"):
				continue
			if filename.endswith('.py'):
				await bot.load_extension(f'JAS.cogs.{filename[:-3]}')
				self.logger.info(f'reload complete: {filename[:-3]}')

	# 시작시 서버 ID 확보 및 DB 설정 
	async def setup_hook(self):
		self.logger.info('-'*30)
		await self.load_extensions(self)
		self.logger.info('base install complete')
		self.logger.info('-'*30)
		await sleep(1)
		
		for command in self.commands:
			command_name = command.name
			if command.checks:
				self.ver_admin_commands.append(command_name)
			if command.cog:
				cog_name = command.cog_name
				if cog_name not in list(self.ver_cog_commands.keys()):
					self.ver_cog_commands[cog_name] = []
				self.ver_cog_commands[cog_name].append(command_name)

		self.logger.info('admin commands')
		self.logger.info('-'*20)
		self.logger.info(self.ver_admin_commands)
		self.logger.info('-'*30)
		await sleep(1)
		self.logger.info('cog commands')
		self.logger.info('-'*20)
		for cog in self.ver_cog_commands:
			self.logger.info(cog)
			self.logger.info(self.ver_cog_commands[cog])
		self.logger.info('-'*30)
		await sleep(1)
		self.logger.info('app commands')
		self.logger.info('-'*20)
		self.logger.info(list(map(lambda x: x.name, await self.tree.fetch_commands(guild=None))))
		self.logger.info(f'load {len(self.commands)} commands')
		self.logger.info('-'*30)
		
	async def on_ready(self):
		self.check_close.start()
		self.logger.info(f'We have logged in as {self.user}')
		self.logger.info('-'*30)
		self.logger.info(f'ID: {self.user.id}')
		self.logger.info(f'Discord version: {discord.__version__}')
		self.logger.info('-'*30)
		self.logger.info(f'PROFILE : {self.PROFILE}')
		self.logger.info(f'TEST_SERVER_ID : {self.TEST_SERVER_ID}')
		self.logger.info('-'*30)

		self.var_manage[self.TEST_SERVER_ID] = Connector(self.TEST_SERVER_ID)

		self.logger.info('get DB data complete')
		self.logger.info('-'*20)
		self.logger.info(self.var_manage)
		self.logger.info('='*30)
		if self.send_queue:
			self.send_queue.put('started')
		self.logger.info('>> bot on to go')

	async def on_message(self, message:discord.Message):
		if message.author.bot:
			return

		if message.guild.id != self.TEST_SERVER_ID:
			print('This is only for test server')
			return

		self.var_proceed = False
		self.var_registered = False
		
		self.logger.debug(message.content)

		try:
			self.var_manage[message.guild.id]
		except:
			try:
				self.logger.info(f'Connect {message.guild.name}|{message.guild.id} DB')
				self.var_manage[message.guild.id]=Connector(message.guild.id)
			except Exception as e:
				self.logger.error(e, 'DB  error occured')
				await message.channel.send(embed=Embeds.error(e))
				return	
			
		connector:Connector = self.var_manage[message.guild.id]
		command = message.content[1:].split(' ')[0]
		
		if not message.content.startswith('!'):
			self.logger.info('-'*10)
			if message.channel.parent.name == connector.data.setting.channel.anon:
				self.var_proceed = True
				self.var_registered = True
				self.logger.debug('anon message')
				return
			elif message.channel.category.name in connector.data.setting.channel.community:
				self.var_proceed = True
				self.var_registered = True
				self.logger.debug("chara message")
				return
			self.logger.debug('not a command')
			return
		
		if not message.author.guild_permissions.administrator:
			self.logger.debug('not a admin')
			if command in self.ver_admin_commands:
				await message.delete()
				await message.channel.send(embed=Embeds.general('관리자 전용 명령어입니다.'), delete_after=5)
				self.var_proceed = False
				return
		else:
			if message.content.startswith('!서버구축'):
				self.var_proceed = True
				self.var_registered = True
				return
							
			if command in self.ver_admin_commands:
				if message.channel.name != connector.data.setting.channel.manage:
					self.var_proceed = False
					await message.delete()
					await message.channel.send(embed=Embeds.general('관리자 전용 명령어는 관리채널에서 사용할 수 있습니다.'), delete_after=3)
					return
				else:
					self.logger.debug('admin command')
					self.var_proceed = True
					self.var_registered = True
					return
			
		if not connector.check_user(message.author.id) and not message.content.startswith("!회원가입"):
			await message.channel.send(embed=Embeds.setting('아직 회원가입이 되지 않은 유저입니다.','`/가입`을 먼저 진행해 주시기 바랍니다.'), delete_after=5)
			if not message.author.top_role.permissions.administrator:
				await message.delete()
				self.var_registered = False
				return
		elif connector.check_chara(message.author.id) == 0 and not message.content.startswith("!캐릭터등록"):
			await message.channel.send(embed=Embeds.setting('아직 캐릭터 등록이 되지 않은 유저입니다.','`/캐릭터등록`을 먼저 진행해 주시기 바랍니다.'), delete_after=5)
			if not message.author.top_role.permissions.administrator:
				await message.delete()
				self.var_registered = False
				return
			
		self.var_proceed = True
		self.var_registered = True

		if command == "help":
			await message.delete()
			if message.content == '!help':
				return await self.process_commands(message)
			
			if message.content.split(' ')[1] in self.ver_admin_commands:
				if message.author.top_role.permissions.administrator:
					if not message.channel.name == connector.data.setting.channel.manage:
						await message.channel.send(embed=Embeds.setting('해당 명령어는 관리 채널에서만 사용 가능합니다.'), delete_after=3)
					else:
						await self.process_commands(message)
				else:
					await message.channel.send(embed=Embeds.general('해당 내용은 관리자만 확인 가능합니다.'), delete_after=5)
			else:
				await self.process_commands(message)
			return

		if command not in list(map(lambda x: x.name, self.commands)):
			self.logger.debug("no match command")
			await message.delete()
			await self.process_commands(message)
			return

	async def on_command_error(self, message:commands.Context, error):
		self.logger.warn(error, 'command error occured')
		if self.send_queue:
			self.send_queue.put('warn')
			self.send_queue.put(str(error))
		if isinstance(error, commands.CommandNotFound):
			return await message.send(embed=Embeds.general("잘못된 명령어 입니다", "명령어 목록을 확인하고 싶으시다면 `!help`를 이용해 주세요"), delete_after=30)
		elif isinstance(error, commands.MissingRole):
			return await message.send(embed=Embeds.general("역할이 충분하지 않습니다", "역할을 확인해 주세요"), delete_after=30)
		elif isinstance(error, commands.MissingRequiredArgument):
			return await message.send(embed=Embeds.general("입력되지 않은 변수가 있습니다", f"`{error.args[0].replace('is a required argument that is missing', '`가 입력되지 않았습니다')}"), delete_after=30)
		else:
			return await message.send(embed=Embeds.error(error))

	async def on_app_command_error(self, interaction:discord.Interaction, error:app_commands.AppCommandError):
		self.logger.warn(error, 'app command error occured')
		if self.send_queue:
			self.send_queue.put('warn')
			self.send_queue.put(str(error))
		if isinstance(error, app_commands.MissingAnyRole):
			await interaction.response.send_message(embed=Embeds.general("사용할 수 없는 명령어 입니다", "관리자 전용 명령어입니다"), ephemeral=True, delete_after=30)
		elif isinstance(error, app_commands.AppCommandError):
			if 'NoUser' in error.args:
				await interaction.response.send_message(embed=Embeds.setting('아직 회원가입이 되지 않은 유저입니다.','`/가입`을 먼저 진행해 주시기 바랍니다.'), ephemeral=True, delete_after=30)
			elif 'NoChara' in error.args:
				await interaction.response.send_message(embed=Embeds.setting('아직 캐릭터 등록이 되지 않은 유저입니다.','`/캐릭터등록`을 먼저 진행해 주시기 바랍니다.'), ephemeral=True, delete_after=30)
			else:
				await interaction.response.send_message(embed=Embeds.error(error))
		else:
			await interaction.response.send_message(embed=Embeds.error(error))

	@tasks.loop(seconds=5)
	async def check_close(self):
		queue_data = ''
		
		if self.rec_queue:
			if not self.rec_queue.empty():
				queue_data = self.rec_queue.get()
		
		if 'stop bot' == queue_data:
			if self.send_queue:
				self.send_queue.put('closed')
			print('>> stop bot')
			self.is_quit = True
			await self.close()
			exit(0)

class Data:
	connector:Connector
	setting:Conn.Vars
	channel:Conn.Channel
	role:Conn.Roles
	user:dict[int, Conn.User]
	charas:dict[str, Conn.Chara]
	npc:dict[str, Conn.NPC]
	invs:dict[str, Conn.Backpack]
	items:dict[str, Conn.Item]
	fish_data:dict[str, list[str]]
	fishes:dict[str, Conn.Fish]

def __connection__(self, guild_id):
	# connection
	self.connector = self.bot.var_manage[guild_id]
	# server infos
	self.setting = self.connector.data.setting.data
	self.channel = self.connector.data.setting.channel
	self.role = self.connector.data.setting.role
	self.user = self.connector.data.user.data
	# chara data
	self.charas = self.connector.data.chara.data
	self.npc = self.connector.data.npc.data
	self.invs = self.connector.data.inventory.data
	self.items = self.connector.data.items.data
	# fishing data
	self.fish_data = self.connector.data.fishing.data
	self.fishes = self.connector.data.fishing.fish
	# print('connection complete')

async def __on_ready__(self, interaction:discord.Interaction, check_user=True, check_chara=True):
	self.bot.logger.debug('-'*10)
	try:
		command_name = f'{interaction.command.parent.name} {interaction.command.name}'
	except:
		command_name = interaction.command.name
	self.bot.logger.debug(command_name)
	await self.__get_connection__(interaction.guild_id)
	user_id = interaction.user.id

	if not check_user or not check_chara:
		return

	if user_id not in list(self.user.keys()):
		raise app_commands.AppCommandError('NoUser','회원가입이 진행되지 않은 유저입니다.')
	
	if not self.user[user_id].charas:
		raise app_commands.AppCommandError('NoChara','캐릭터등록이 진행되지 않은 유저입니다.')


class CommandBase(commands.Cog, Data):
	def __init__(self, bot:JAS) -> None:
		self.bot:JAS = bot
		super().__init__()

	async def __get_connection__(self, guild_id):
		__connection__(self, guild_id)
	
	async def on_ready(self, interaction:discord.Interaction, check_user=True, check_chara=True):
		await __on_ready__(self, interaction, check_user, check_chara)

	@commands.Cog.listener()
	async def on_message(self, message:discord.Message):
		if message.author.bot:
			return
		
		if not (self.bot.var_registered and self.bot.var_proceed):
			return
		
		command_list = self.bot.ver_cog_commands[self.__cog_name__]
		
		await self.__get_connection__(message.guild.id)
		command = message.content[1:].split(' ')[0]
		if command in command_list:
			self.bot.logger.debug('-'*10)
			await message.delete()
			await self.bot.process_commands(message)
			return
		
		if self.__cog_name__ == "Community" and not message.content.startswith('!'):
			if message.channel.category.name in self.channel.community and message.channel.type.value == 0 :
				self.bot.logger.debug('send chara message')
				await message.delete()
				self.bot.logger.debug('-'*10)
				await self.chara_talk(message)
				return
			
			if message.channel.parent.name == self.channel.anon:
				prefix = self.bot.command_prefix
				if not message.content.startswith(prefix) and '전용 익명방' not in message.content:
					self.bot.logger.debug('send anon message')
					self.bot.logger.debug('-'*10)
					await self.anon_message(message)
				return
			
@app_commands.default_permissions(send_messages=True)
class AppCommandBase(app_commands.Group, Data):
	def __init__(self, bot, name, description):
		super().__init__(name=name, description=description)
		self.bot:JAS = bot

	async def __get_connection__(self, guild_id):
		__connection__(self, guild_id)
	
	async def on_ready(self, interaction:discord.Interaction, check_user=True, check_chara=True):
		await __on_ready__(self, interaction, check_user, check_chara)
	