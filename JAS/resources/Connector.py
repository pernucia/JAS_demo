import sqlite3, gspread
from JAS.setup import Setup
from JAS.resources.Exceptions import *
from copy import deepcopy
from random import random

def return_string(string):
	result = []
	result.append('='*30)
	result.extend(string)
	result.append('='*30)
	return '\n'.join(result)
	
class Connector:
	def __init__(self, guild_id):
		self.id = guild_id
		self.conn = None
		self.cur = None
		self.__connect__()
		self.data:Data = self.__get_data__()
		
	def __str__(self):
		return str(self.data)

	def __connect__(self, update:bool=False, isDict:bool=False):
		if not self.conn or update:
			self.conn = Setup().setup(self.id)
		else:
			self.conn = Setup().connect(self.id)
		self.conn.row_factory = sqlite3.Row if isDict else None
		self.cur = self.conn.cursor()

	def __commit__(self):
		self.conn.commit()

	def close(self):
		self.cur.close()
		self.conn.close()

	def __get_data__(self):
		return Data(self, self.id)

	# General
	# getter
	def get_table_list(self):
		self.__connect__()
		tables = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
		self.close()
		return tables
	
	# setter
	def __reset_table_data__(self, tablename, data):
		self.__connect__()
		self.cur.execute(f'DELETE FROM {tablename}')
		script = f'INSERT INTO {tablename} VALUES({",".join(["?"]*len(data[0]))})'
		self.cur.executemany(script, data)
		self.__commit__()
		self.close()

	# 관리
	# getter
	# 유저존재 확인
	def check_user(self, id):
		self.__connect__()
		user = self.cur.execute(f'SELECT count(*) FROM user WHERE id ={id} ').fetchone()[0]
		self.close()
		if user != 0:
			return True
		else:
			return False
		
	def get_user_info(self):
		self.__connect__()
		userdata = self.cur.execute(f'SELECT * from user').fetchall()
		self.close()
		return userdata
		
	# 유저 목록
	def get_user_list(self):
		self.__connect__()
		userdata = self.cur.execute('SELECT * FROM user').fetchall()
		self.close()
		return userdata
	
	# 회원가입 가능여부
	def check_register_available(self):
		self.__connect__()
		result = self.cur.execute('SELECT value from setting WHERE type="accept_user"').fetchone()[0]
		self.close()
		return True if result == "True" else False
	
	# 설정정보
	def get_setting_info(self):
		self.__connect__()
		result = self.cur.execute('SELECT * FROM setting').fetchall()
		self.close()
		return result
	
	def __get_setting_value__(self, name):
		self.__connect__()
		value = self.cur.execute('SELECT value FROM setting WHERE type = (?)',(name,)).fetchone()[0]
		self.close()
		return value
	
	# 서버 관련 정보 가져오기
	def get_server_info(self):
		self.__connect__()
		self.close()

	# setter
	# 설정
	def __set_setting_value__(self, name, value):
		print('setting value set')
		try:
			self.__connect__()
			self.cur.execute('UPDATE setting SET value=(?) WHERE type = (?)',(value, name))
			self.__commit__()
			self.close()

			self.data.setting.__data__[name] = value
			print('setting complete')
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			print('error occured')
			raise ConnectionError('설정 변경 실패', name)

	# 유저정보 등록/갱신
	def set_user(self, id, name, private_thread_id):
		self.__connect__()
		self.cur.execute(f'INSERT INTO user VALUES(?,?,?,?)',(id, name, private_thread_id, ""))
		self.__commit__()
		self.close()

		self.data.user.data[id] = User((id, name, private_thread_id, ''))

	def update_user(self, id, name):
		self.__connect__()
		self.cur.execute(f'UPDATE user SET name={name} WHERE id = {id}')
		
		self.__commit__()
		self.close()

		self.data.user.data[id].name = name

	# 유저정보 삭제
	def delete_user(self, id):
		if self.check_user(id):
			self.__connect__()
			self.cur.execute(f'DELETE FROM user WHERE id = {id}')
			self.__commit__()
			self.close()
		
			if self.data.user.data[id].charas:
				self.delete_charactor_data(self.data.user.data[id].charas, id)
			del self.data.user.data[id] 

	# 낚시 관련
	# getter
	# 물고기 정보 가져오기
	def get_fish_data(self):
		self.__connect__()
		fish_data = self.cur.execute('SELECT * FROM fishing_data').fetchall()
		self.close()
		return fish_data
	
	# 최대 낚시 횟수 확인
	def get_max_fishing(self):
		self.__connect__()
		max_count = int(self.cur.execute('SELECT value FROM setting WHERE type = "max_fishing"').fetchone()[0])
		self.close()
		return max_count
	
	# 낚시 이력 확인
	def get_fishing_history(self, id, channel, date):
		try:
			self.__connect__()
			count = self.cur.execute(f"SELECT COUNT(*) FROM fishing_history WHERE user = {id} and fishdate LIKE '{date}%'").fetchone()[0]
			self.close()
			return count
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise ConnectionError('낚시 이력 조회 실패')
	
	# 물고기 존재 확인
	def check_fish(self, name):
		self.__connect__()
		result = self.cur.execute('SELECT count(*) FROM fishign_data WHERE name=(?)',(name)).fetchone()[0]
		self.close()
		return True if result > 0 else False

	# setter
	# 낚시 결과 기록
	def set_fishing_history(self, now, user_id, loc, name, length):
		try:
			self.__connect__()
			print('connect DB')
			self.cur.execute('INSERT INTO fishing_history VALUES(?, ?, ?, ?, ?)', (now, user_id, loc, name, length))
			self.__commit__()
			self.close()
			print('connection closed')
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise FishingError('낚시 이력 등록 실패')
		
	# 최대 낚시 횟수 설정
	def set_max_fishing(self, value):
		try:
			self.__set_setting_value__("max_fishing", value)
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise ConnectionError('최대 낚시 횟수 등록 실패')
		
	# 물고기 추가
	def add_fish_data(self, name, desc, min, max, baseprice, loc):
		try:
			self.__connect__()
			count = self.cur.execute('SELECT count(*) FROM fishing_data').fetchone()[0]
		
			code = str(count+1001)
			code_list = self.cur.execute(f'SELECT code FROM fishing_data ORDER BY code').fetchall()
			if code in code_list:
				recent_code = code_list.pop()[0]
				code = str(int(recent_code)+1)

			self.cur.execute('INSERT INTO fishing_data VALUES(?,?,?,?,?,?)',(code, name, min, max, baseprice, loc))
			self.cur.execute('INSERT INTO item VALUES(?,?,?,?,?)', (code, name, desc, 1, baseprice))
			self.__commit__()
			self.close()
			self.reg_item(code, name, desc, 1, baseprice)

			locs = list(self.data.fishing.data.keys())
			for location in loc.split(','):
				if location in locs:
					self.data.fishing.data[location] = []
				self.data.fishing.data[location].append(code)
			self.data.fishing.fish[code] = Fish((code, name, min, max, baseprice, loc))
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise CannotAddFish('물고기 추가 실패')
	
	# 물고기 변경
	def change_fish_data(self, code, desc, min, max, baseprice, loc):
		try:
			self.__connect__()
			self.cur.execute('UPDATE fishing_data SET min=(?), max=(?), baseprice=(?), loc=(?) WHERE code = (?)',(min, max, baseprice, loc, code))
			self.cur.execute('UPDATE item SET description=(?), price=(?) WHERE code=(?)', (desc, baseprice, code))
			self.__commit__()
			self.close()
			locs = list(self.data.fishing.data.keys())
			for location in loc.split(','):
				if location in locs :
					if code not in self.data.fishing.data[location]:
						self.data.fishing.data[location].append(code)
				else:
					self.data.fishing.data[location] = []
					self.data.fishing.data[location].append(code)
			fish = self.data.fishing.fish[code]
			fish.desc = desc
			fish.min = min
			fish.max = max
			fish.baseprice = baseprice
			item = self.data.items.data[code]
			item.desc = desc
			item.baseprice = baseprice
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise CannotAddFish('물고기 변경 실패')
		
	# 물고기 삭제
	def delete_fish(self, code):
		self.__connect__()
		self.cur.execute(f'DELETE FROM fishing_data WHERE code={code}')
		self.cur.execute(f'DELETE FROM item WHERE code={code}')
		self.__commit__()
		self.close()
		self.delete_item_from_inventory(code)
		
		for loc in list(self.data.fishing.data.keys()):
			if code in self.data.fishing.data[loc]:
				self.data.fishing.data[loc].remove(code)
		del self.data.fishing.fish[code]

	# 낚시 이력 삭제
	def delete_fishing_history(self, id):
		try:
			self.__connect__()
			self.cur.execute(f"DELETE FROM fishing_history WHERE user={id}")
			self.__commit__()
			self.close()
			return True
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise ConnectionError('낚시 이력 삭제 실패')
		
	# 낚시터 변경
	def change_fishing_channel(self, before, after):
		self.__connect__()
		list = self.cur.execute("SELECT code, loc FROM fishing_data WHERE loc LIKE '(?)'",(f'%{before}%',)).fetchall()
		for item in list:
			code = item[0]
			loc = item[1]
			after_loc = loc.replace(before, after)
			self.cur.execute("UPDATE fishing_data SET loc=(?) WHERE code=(?)",(after_loc, code))
		self.__commit__()
		self.close()

		self.data.fishing.data[after] = deepcopy(self.data.fishing.data[before])
		del self.data.fishing.data[before]
		
	# 아이템 관련
	# getter
	# 아이템 정보 수집
	def get_items_info(self):
		self.__connect__()
		item = self.cur.execute(f'SELECT * FROM item').fetchall()
		self.close()
		return item

	# 아이템 정보 확인
	def get_item_info(self, code):
		self.__connect__()
		item = self.cur.execute(f'SELECT * FROM item WHERE code={code}').fetchone()
		self.close()
		return item

	# setter
	# 아이템 등록
	def reg_item(self, code, name, desc, number, price):
		self.__connect__()
		self.cur.execute('INSERT INTO item VALUES(?,?,?,?,?)',(code, name, desc, number, price))
		self.__commit__()
		self.close()

		self.data.items.data[code] = Item((code, name, desc, number, price))

	# 아이템 수정
	def update_item(self, code, name, desc, number, price):
		self.__connect__()
		self.cur.execute('UPDATE item SET name=(?), description=(?), price=(?) WHERE code=(?)',(name, desc, price, code))
		self.__commit__()
		self.close()

		self.data.items.data[code].name = name
		self.data.items.data[code].desc = desc
		self.data.items.data[code].number = number
		self.data.items.data[code].price = price

	# 인벤토리 관련
	# getter
	# 인벤토리 정보 확인
	def get_inventory_data(self):
		try:
			self.__connect__()
			result = self.cur.execute('SELECT * FROM inventory').fetchall()
			self.close()
			return result
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise ConnectionError('인벤토리 정보 확인 실패')
	
	# setter
	# 아이템 보관
	def store_item(self, code, itemcode, num):
		inventory = self.data.inventory.data[code]
		before_items = ','.join(inventory.items)
		items = f'{before_items},{itemcode}' if before_items else f'{itemcode}'
		self.__connect__()
		self.cur.execute(f'UPDATE inventory SET item=? WHERE code=?',(items, code))
		self.__commit__()
		self.close()

		self.data.inventory.data[code].items.append(itemcode)

	# 아이템사용
	def use_item(self, code, itemcode):
		self.__connect__()
		item = self.cur.execute(f'SELECT item from inventory WHERE code=?',(code,)).fetchone()
		items = item[0].split(',')
		items.remove(itemcode)
		item_after = ','.join(items)
		self.cur.execute(f"UPDATE inventory SET item=(?) WHERE code=(?)",(item_after, code))
		self.cur.execute(f"DELETE FROM item WHERE code=(?)",(itemcode,))
		self.__commit__()
		self.close()

		self.data.inventory.data[code].items.remove(itemcode)

	# 아이템 부여
	def spawn_item(self, code, itemcode, item):
		itemcode = f'{itemcode}-1-{str(random())[2:]}'
		name = item.name
		desc = item.desc
		price = item.price
		self.reg_item(itemcode, name, desc, 1, price)
		self.store_item(code, itemcode, 1)

	# 아이템판매
	def sold_item(self, code, itemcode, gold):
		self.use_item(code, itemcode)
		self.add_gold(code, gold)
	
	# 골드 추가
	def add_gold(self, code, gold):
		try:	
			before_gold = self.data.inventory.data[code].gold
			print(before_gold)
			after_gold = before_gold + float(gold)
			self.__connect__()
			self.cur.execute('UPDATE inventory SET gold = (?) WHERE code = (?)', (after_gold, code))
			self.__commit__()
			self.close()
			
			self.data.inventory.data[code].gold = after_gold
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise SellingError('골드 추가 실패')
		
	# 인벤토리 업데이트
	def update_chara_inv_size(self, code, size):
		try:
			self.__connect__()
			before_size = self.data.inventory.data[code].size
			after_size = before_size+size
			self.cur.execute(f'UPDATE inventory SET size=(?) WHERE code=(?)',(after_size, code))
			self.__commit__()
			self.close()

			self.data.inventory.data[code].size = after_size
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			raise SellingError('인벤토리 업데이트 실패')
	
	# 인벤토리에서 아이템 삭제
	def delete_item_from_inventory(self, code):
		self.__connect__()
		self.cur.execute(f"DELETE FROM item WHERE code LIKE '{'%-'+code+'-%'}'")
		self.__commit__()
		inventory = self.cur.execute(f"SELECT code, item FROM inventory WHERE items LIKE '{'%-'+code+'-%'}'").fetchall()
		
		for inv in inventory:
			items = inv[1].split(',')
			mod_items = []
			for item in items:
				if f'-{code}-' not in item:
					mod_items.append(item)
			self.cur.execute(f'UPDATE inventory SET item={",".join(mod_items)} WHERE code={inv[0]}')	
		self.__commit__()
		self.close()

		for code in list(self.data.inventory.data.keys()):
			itemcodes = list(filter(lambda x: code.split('_')[0] == code,list(self.data.inventory.data[code].keys()))) 
			if len(itemcodes) > 0:
				for itemcode in itemcodes:
					del self.data.inventory[code][itemcode]

	# 캐릭터 관련
	# getter
	# NPC존재 확인
	def check_NPC(self, type):
		self.__connect__()
		result = self.cur.execute("SELECT count(*) FROM chara WHERE code LIKE '(?)'",(f'%{type}%',)).fetchall()[0]
		self.close()
		return True if result > 0 else False
	
	# 캐릭터 존재 확인
	def check_chara(self, id):
		self.__connect__()
		code = self.cur.execute('SELECT charas FROM user WHERE id=(?)',(id,)).fetchone()[0]
		result = self.cur.execute(f"SELECT count(*) FROM chara WHERE code=?",(code,)).fetchone()[0]
		self.close()
		return result

	# NPC정보 가져오기
	def get_NPC_info(self):
		self.__connect__()
		info = self.cur.execute("SELECT * FROM NPC").fetchall()
		vers = self.cur.execute("SELECT * FROM NPC_vers").fetchall()
		self.close()
		return info, vers

	# 캐릭터 정보 가져오기
	def get_charactor_data(self):
		self.__connect__()
		data = self.cur.execute("SELECT * FROM chara").fetchall()
		self.close()
		return data

	# 유저 캐릭터 가져오기
	def get_user_chara(self, id):
		self.__connect__()
		data = self.cur.execute("SELECT code FROM chara WHERE code LIKE '(?)'",(f'{id}%',)).fetchall()[0]
		self.close()
		return data
		
	# setter
	# NPC정보 입력
	def set_NPC_info(self, code, name, color=0):
		self.__connect__()
		self.cur.execute("INSERT INTO NPC VALUES(?,?,?)",(code, name, color))
		self.__commit__()
		self.close()

		self.data.npc.data[code] = NPC((code, name, color), [])
	
	# NPC대사 입력
	def set_NPC_vers(self, code, keyword, vers):
		self.__connect__()
		self.cur.execute("INSERT INTO NPC_vers VALUES(?,?,?)",(code, keyword, vers))
		self.__commit__()
		self.close()

		self.data.npc.data[code].number += 1 
		self.data.npc.data[code].case = self.data.npc.data[code].case + f',{keyword}' if self.data.npc.data[code].case else keyword
		self.data.npc.data[code].vers.append(vers)
	
	# NPC정보 수정
	def update_NPC_info(self, code, name, color):
		self.__connect__()
		self.cur.execute("UPDATE NPC SET name=(?), color=(?) WHERE code=(?)",(name, color, code))
		self.__commit__()
		self.close()
		
		self.data.npc.data[code].name = name
		self.data.npc.data[code].color = color

	# NPC대사 입력
	def update_NPC_vers(self, code, before_keyword, after_keyword, vers):
		self.__connect__()
		self.cur.execute("UPDATE NPC_vers SET keyword=(?), vers=(?) WHERE code=(?) and keyword=(?)",(after_keyword, vers, code, before_keyword))
		self.__commit__()
		self.close()

		self.data.npc.data[code].case = ','.join([after_keyword if case == before_keyword else case for case in self.data.npc.data[code].case.split(',')])
		self.data.npc.data[code].vers[self.data.npc.data[code].case.split(',').index(after_keyword)] = vers

	# NPC 정보 삭제
	def delete_NPC_data(self, code):
		self.__connect__()
		self.cur.execute("DELETE FROM NPC WHERE code=(?)",(code,))
		self.cur.execute(f'DELETE FROM NPC_vers WHERE code=(?)',(code,))
		self.__commit__()
		self.close()

		del self.data.npc.data[code]
	
	# 캐릭터 정보 입력
	def set_charactor_data(self, id, code, name, keyword, desc, link):
		stat = [1,1,1,1,1,1]
		point = 4
		gold = self.data.setting.data.base_inv_gold
		size = self.data.setting.data.base_inv_size
		self.__connect__()
		self.cur.execute("INSERT INTO chara VALUES(?,?,?,?,?,?)",(code, name, keyword, desc, link, None))
		self.cur.execute("INSERT INTO stat VALUES(?,?,?,?,?,?,?,?,?)",(code, point, None, *stat))
		self.cur.execute(f'INSERT INTO inventory VALUES(?,?,?,?)',(code, gold, size, ""))
		self.cur.execute("UPDATE user SET charas=(?) WHERE id=(?)",(code, id))
		self.__commit__()
		self.close()

		self.data.user.data[id].charas = code
		self.data.chara.data[code] = Chara((code, name, keyword, desc, link, None),(code, point, None, *stat),','.join(self.data.setting.data.stat_names))
		self.data.inventory.data[code] = Backpack((code, gold, size, ""))

	# 캐릭터 정보 갱신
	def update_charactor_data(self, code, name, keyword, desc, link):
		self.__connect__()
		self.cur.execute("UPDATE chara SET name=(?), keyword=(?), desc=(?), link=(?) WHERE code=(?)",(name, keyword, desc, link, code))
		self.__commit__()
		self.close()

		self.data.chara.data[code].name = name
		self.data.chara.data[code].keyword = keyword
		self.data.chara.data[code].desc = desc
		self.data.chara.data[code].link = link

	# 캐릭터 색상 갱신
	def update_charactor_color(self, code, color):
		self.__connect__()
		self.cur.execute("UPDATE chara SET color=(?) WHERE code=(?)",(color, code))
		self.__commit__()
		self.close()

		self.data.chara.data[code].color = color
		
	# 캐릭터 인벤토리 갱신
	def update_charactor_inventory(self, code, gold=0, size=0):
		self.__connect__()
		basegold, basesize = self.cur.execute('SELECT gold, size FROM inventory WHERE code = (?)',(code,)).fetchone()
		result_gold = basegold+gold
		result_size = basesize+size
		self.cur.execute('UPDATE inventory SET gold=(?), size=(?) WHERE code=(?)',(result_gold, result_size, code))
		self.__commit__()
		self.close()

		self.data.inventory.data[code].gold = result_gold
		self.data.inventory.data[code].size = result_size

	# 캐릭터 정보 삭제
	def delete_charactor_data(self, code, id):
		self.__connect__()
		self.cur.execute("DELETE FROM chara WHERE code=(?)",(code,))
		self.cur.execute(f'DELETE FROM inventory WHERE code = {code}')
		self.cur.execute('UPDATE user SET charas=(?) WHERE id=(?)',(code, id))
		self.__commit__()
		self.close()

		del self.data.inventory.data[id]
		del self.data.chara.data[code]
		self.data.user.data[id].charas = ''

	# 스탯 관련
	# getter
	def get_stat_data(self):
		self.__connect__()
		result = self.cur.execute('SELECT * FROM stat').fetchall()
		self.close()
		return result

	def get_base_stat_names(self):
		self.__connect__()
		result = self.cur.execute("SELECT value FROM setting WHERE id LIKE 'stat%'").fetchall()
		self.close()
		return result
		
	# setter
	def update_stat(self, code, names:list[str], point, stat:list[int]):
		self.__connect__()
		self.cur.execute('UPDATE stat SET stat1=(?), stat2=(?), stat3=(?), stat4=(?), stat5=(?), stat6=(?), point=(?), statname=(?) WHERE code=(?)', (*stat, point, ','.join(names), code))
		self.__commit__()
		self.close()

		self.data.chara.data[code].stat.point = point
		self.data.chara.data[code].stat.stat_names = names
		self.data.chara.data[code].stat.stat1 = stat[0]
		self.data.chara.data[code].stat.stat2 = stat[1]
		self.data.chara.data[code].stat.stat3 = stat[2]
		self.data.chara.data[code].stat.stat4 = stat[3]
		self.data.chara.data[code].stat.stat5 = stat[4]
		self.data.chara.data[code].stat.stat6 = stat[5]

	# 스탯명 변경
	def update_stat_name(self, statname):
		if not statname:
			for chara in list(self.data.chara.data.keys()):
				self.data.chara.data[chara].stat=None
		else:
			if not self.data.setting.data.stat_names[0]:
				for stat_data in self.get_stat_data():
					chara = stat_data[0]
					self.data.chara.data[chara].stat = Stat(stat_data, statname)
		self.__set_setting_value__('stat_names', statname)

# Data Object
class Data():
	def __init__(self, conn:Connector, guild_id) -> None:
		self.guild_id = guild_id
		self.setting=Setting(conn.get_setting_info())
		self.user=Users(conn.get_user_info())
		self.fishing=Fishing(conn.get_fish_data())
		self.items=Items(conn.get_items_info())
		self.inventory=Inventory(conn.get_inventory_data())
		self.chara=Charas(conn.get_charactor_data(), conn.get_stat_data(), conn.__get_setting_value__('stat_names'))
		self.npc=NPCs(conn.get_NPC_info())
	def __str__(self) -> str:
		content = []
		content.append(str(self.setting))
		content.append(str(self.user))
		content.append(str(self.fishing))
		content.append(str(self.items))
		content.append(str(self.inventory))
		content.append(str(self.chara))
		content.append(str(self.npc))
		return '\n'.join(content)
	def showDB(self)->list:
		content = []
		content.append(str(self.setting))
		content.append(str(self.user))
		content.append(str(self.fishing))
		content.append(str(self.items))
		content.append(str(self.inventory))
		content.append(str(self.chara))
		content.append(str(self.npc))
		return content
		
# User data
class Users():
	def __init__(self, data) -> None:
		self.data : dict[int, User] = {}
		for user in data:
			code = user[0]
			self.data[code] = User(user)
	def __str__(self) -> str:
		content = []
		content.append('User data')
		for code in list(self.data.keys()):
			content.append('-'*30)
			content.append(str(self.data[code]))
		return return_string(content)
			
class User():
	def __init__(self, data) -> None:
		self.id:int = data[0]
		self.name:str = data[1]
		self.thread:int = data[2]
		self.charas:str = data[3]
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('id', self.id))
		content.append('{0:<20} : {1}'.format('name', self.name))
		content.append('{0:<20} : {1}'.format('thread', self.thread))
		content.append('{0:<20} : {1}'.format('charas', self.charas))
		return '\n'.join(content)

# setting		
class Setting():
	def __init__(self, data) -> None:
		self.__data__:dict[str, str] = {}

		for item in data:
			key, value = item
			self.__data__[key] = value

		self.data=Vars(self.__data__)
		self.channel=Channel(self.__data__)
		self.role=Roles(self.__data__)
	def __str__(self) -> str:
		content = []
		content.append('Current Setting')
		content.append('-'*30)
		content.append(str(self.data))
		content.append('-'*30)
		content.append(str(self.channel))
		content.append('-'*30)
		content.append(str(self.role))
		return return_string(content)
		
class Vars:
	def __init__(self, data) -> None:
		self.__data__:dict[str, str] = data
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('max_fishing', self.max_fishing))
		content.append('{0:<20} : {1}'.format('max_gather', self.max_gather))
		content.append('{0:<20} : {1}'.format('base_inv_size', self.base_inv_size))
		content.append('{0:<20} : {1}'.format('base_inv_gold', self.base_inv_gold))
		content.append('{0:<20} : {1}'.format('accept_user', self.accept_user))
		content.append('{0:<20} : {1}'.format('random_box', self.random_box))
		content.append('{0:<20} : {1}'.format('gspread_url', self.gspread_url))
		content.append('{0:<20} : {1}'.format('stat_names', self.stat_names))
		return '\n'.join(content)

	@property
	def max_fishing(self) -> int:
		return int(self.__data__["max_fishing"])
	@property
	def max_gather(self) -> int:
		return int(self.__data__["max_gather"])
	@property
	def base_inv_size(self) -> int:
		return int(self.__data__["base_inv_size"])
	@property
	def base_inv_gold(self) -> int:
		return int(self.__data__["base_inv_gold"])
	@property
	def accept_user(self) -> bool:
		return  True if self.__data__["accept_user"]=="True" else False
	@property
	def random_box(self) -> int:
		return int(self.__data__["random_box"])
	@property
	def gspread_url(self) -> str:
		return self.__data__["gspread_url"]
	@property
	def stat_names(self) -> list[str]:
		return self.__data__["stat_names"].split(',')
	
class Channel:
	def __init__(self, data) -> None:
		self.__data__:dict[str, str] = data
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('anon channel', self.anon))
		content.append('{0:<20} : {1}'.format('manage channel', self.manage))
		content.append('{0:<20} : {1}'.format('join channel', self.join))
		content.append('{0:<20} : {1}'.format('store channel', self.store))
		content.append('{0:<20} : {1}'.format('community channel', self.community))
		content.append('{0:<20} : {1}'.format('qna channel', self.qna))
		return '\n'.join(content)
	
	@property
	def anon(self) -> str:
		return self.__data__["anon"]
	@property
	def manage(self) -> str:
		return self.__data__["manage"]
	@property
	def join(self) -> str:
		return self.__data__["join"]
	@property
	def store(self) -> str:
		return self.__data__["store"]
	@property
	def community(self) -> str:
		return self.__data__["community"]
	@property
	def qna(self) -> str:
		return self.__data__["qna"]
	
class Roles:
	def __init__(self, data) -> None:
		self.__data__:dict[str, str] = data
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('visitor role', self.visitor))
		content.append('{0:<20} : {1}'.format('registered role', self.registered))
		content.append('{0:<20} : {1}'.format('admin role', self.admin))
		return '\n'.join(content)

	@property
	def visitor(self) -> str:
		return self.__data__["visitor"]
	@property
	def registered(self) -> str:
		return self.__data__["registered"]
	@property
	def admin(self) -> str:
		return self.__data__["admin"]
	
# fishing data
class Fishing():
	def __init__(self, data) -> None:
		self.data:dict[str, list[str]] = {}
		self.fish:dict[str, Fish] = {}
		for fish in data:
			code = fish[0]
			fishdata = Fish(fish)
			locs = fish[5].split(',')
			for loc in locs:
				try:
					self.data[loc].append(code)
				except:
					self.data[loc]=[]
					self.data[loc].append(code)
			self.fish[code] = fishdata
		self.data = self.data
	def __str__(self) -> str:
		content = []
		content.append('Fish data')
		for loc in list(self.data.keys()):
			content.append('-'*30)
			content.append(f'place: {loc}')
			for fish in self.data[loc]:
				content.append('-'*20)
				content.append(f'[{fish}]')
				content.append(str(self.fish[fish]))
		return return_string(content)
		
class Fish():
	def __init__(self, fish) -> None:
		self.name:str = fish[1]
		self.min:int = fish[2]
		self.max:int = fish[3]
		self.baseprice:int = fish[4]
		self.loc:str = fish[5]
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('name', self.name))
		content.append('{0:<20} : {1}'.format('min', self.min))
		content.append('{0:<20} : {1}'.format('max', self.max))
		content.append('{0:<20} : {1}'.format('baseprice', self.baseprice))
		content.append('{0:<20} : {1}'.format('loc', self.loc))
		return '\n'.join(content)
	
# Item data
class Items():
	def __init__(self, data) -> None:
		self.data:dict[str,Item] = {}
		for item in data:
			code = item[0]
			itemdata = Item(item)
			self.data[code] = itemdata
	def __str__(self) -> str:
		content = []
		content.append('Item data')
		for code in list(self.data.keys()):
			content.append('-'*30)
			content.append(f'[{code}]')
			content.append(str(self.data[code]))
		return return_string(content)
				
class Item():
	def __init__(self, data) -> None:
		self.name:str = data[1]
		self.desc:str = data[2]
		self.number:int = data[3]
		self.price:int = data[4]
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('name', self.name))
		content.append('{0:<20} : {1}'.format('desc', self.desc))
		content.append('{0:<20} : {1}'.format('number', self.number))
		content.append('{0:<20} : {1}'.format('price', self.price))
		return '\n'.join(content)

# Inventory data
class Inventory():
	def __init__(self, data) -> None:
		self.data:dict[str, Backpack] = {}
		for invdata in data:
			id = invdata[0]
			self.data[id] = Backpack(invdata)
	def __str__(self) -> str:
		content = []
		content.append('Inventory data')
		for user in list(self.data.keys()):
			content.append('-'*30)
			content.append(f'User: {user}')
			content.append('-'*20)
			content.append(str(self.data[user]))
		return return_string(content)
		
class Backpack():
	def __init__(self, inv_data) -> None:
		self.gold:int = inv_data[1]
		self.size:int = inv_data[2]
		self.items:list[str] = []
		if inv_data[3] != '':
			for itemcode in inv_data[3].split(','):
				code = itemcode.strip()
				self.items.append(code)
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('gold', self.gold))
		content.append('{0:<20} : {1}'.format('max size', self.size))
		content.append('{0:<20} :'.format('items'))
		content.append('-'*15)
		for item in self.items:
			content.append('{0:<15} : {1}'.format('code', item))
		return '\n'.join(content)

# Store data
class Store():
	def __init__(self, data, iteminfo) -> None:
		self.data:dict[str, StoreItem] = {}
		for item in data:
			code = item[0]
			self.data[code] = StoreItem(item, iteminfo)
	def __str__(self) -> str:
		content = []
		content.append('Store data')
		for code in list(self.data.keys()):
			content.append('-'*30)
			content.append(f'[{code}]')
			content.append(str(self.data[code]))
		return return_string(content)
		
class StoreItem():
	def __init__(self, data, iteminfo) -> None:
		code = data[0]
		self.name:str = iteminfo[code].name
		self.sale:bool = True if data[1]=='True' else False
		self.desc:str = iteminfo[code].desc
		self.price:int = data[2]
		self.discount:int = data[3]
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('name', self.name))
		content.append('{0:<20} : {1}'.format('sale', self.sale))
		content.append('{0:<20} : \n{1}'.format('desc', self.desc))
		content.append('{0:<20} : {1}'.format('price', self.price))
		content.append('{0:<20} : {1}'.format('discount', self.discount))
		return '\n'.join(content)

# NPC data
class NPCs():
	def __init__(self, data) -> None:
		self.data:dict[str,NPC] = {}
		info = data[0]
		vers = data[1]
		for chara in info:
			code = chara[0]
			npc_vers = list(filter(lambda x: x[0]==code,vers))
			self.data[code] = NPC(chara, npc_vers)
	def __str__(self) -> str:
		content = []
		content.append('NPC data')
		for code in list(self.data.keys()):
			content.append('-'*30)
			content.append(f'[{code}]')
			content.append(str(self.data[code]))
		return return_string(content)
	
class NPC():
	def __init__(self, data, vers:list) -> None:
		self.name:str = data[1]
		self.color:int = data[2]
		self.number:int = len(vers)
		self.case:list[str] = []
		self.vers:list[str] = []
		if vers:
			for item in vers:
				self.case.append(item[1])
				self.vers.append(item[2])
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('name', self.name))
		content.append('-'*15)
		content.append('{0:<15} : {1}'.format('number', self.number))
		content.append('{0:<15} :'.format('vers'))
		for i in range(len(self.vers)):
			content.append(self.case[i] + '-'*10)
			for vers in self.vers[i].split('\n'):
				content.append(f'  {vers}')
		return '\n'.join(content)

# Chara data
class Charas():
	def __init__(self, data, stat, stat_default) -> None:
		self.data:dict[str,Chara] = {}
		for chara in data:
			code = chara[0]
			stat_data = list(filter(lambda x: x[0]==code ,stat))[0]
			self.data[code] = Chara(chara, stat_data, stat_default)
	def __str__(self) -> str:
		content = []
		content.append('Chara data')
		for code in list(self.data.keys()):
			content.append('-'*30)
			content.append(f'[{code}]')
			content.append(str(self.data[code]))
		return return_string(content)
			
class Stat():
	def __init__(self, data, default) -> None:
		self.stat1:int = int(data[3])
		self.stat2:int = int(data[4])
		self.stat3:int = int(data[5])
		self.stat4:int = int(data[6])
		self.stat5:int = int(data[7])
		self.stat6:int = int(data[8])
		self.point:int = data[1]
		self.stat_names = data[2].split(',') if data[2] else default.split(',')
	def __str__(self) -> str:
		content = []
		content.append('{0:<15} : {1}'.format(self.stat_names[0], self.stat1))
		content.append('{0:<15} : {1}'.format(self.stat_names[1], self.stat2))
		content.append('{0:<15} : {1}'.format(self.stat_names[2], self.stat3))
		content.append('{0:<15} : {1}'.format(self.stat_names[3], self.stat4))
		content.append('{0:<15} : {1}'.format(self.stat_names[4], self.stat5))
		content.append('{0:<15} : {1}'.format(self.stat_names[5], self.stat6))
		content.append('='*5)
		content.append('{0:<15} : {1}'.format('point', self.point))
		return '\n'.join(content)
	
class Chara():
	def __init__(self, data, stat, stat_default) -> None:
		self.name:str = data[1]
		self.keyword:str = data[2]
		self.desc:str = data[3]
		self.link:str = data[4]
		self.color:int = data[5]
		self.stat:Stat = Stat(stat, stat_default) if stat_default else None
	def __str__(self) -> str:
		content = []
		content.append('{0:<20} : {1}'.format('name', self.name))
		content.append('{0:<20} : {1}'.format('keyword', self.keyword))
		content.append('{0:<20} : \n{1}'.format('desc', self.desc))
		content.append('{0:<20} : {1}'.format('link', self.link))
		if self.stat:
			content.append('-'*15)
			content.append(str(self.stat))
		return '\n'.join(content)
	