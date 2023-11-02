import discord, os, sqlite3, traceback, shutil
from JAS.resources.Addons import DB_FOLDER_PATH, IMG_FOLDER_PATH, resource_path, filename

class Setup:
	def __init__(self):
		pass
	
	def check(self, guild_id):
		if os.path.exists(os.path.join(DB_FOLDER_PATH, f'{guild_id}.db')):
			return True
		else:
			print('creating guild folder')
			os.makedirs(os.path.join(IMG_FOLDER_PATH, str(guild_id)), exist_ok=True)
			return False

	def connect(self, guild_id):
		return sqlite3.connect(os.path.join(DB_FOLDER_PATH, f'{guild_id}.db'))
	
	def update(self, conn:sqlite3.Connection, field:dict, table):
		"""
		DB TABLE 업데이트
		"""
		conn.row_factory = sqlite3.Row
		cur = conn.cursor()
		data_cur = cur.execute(f'SELECT * FROM {table}')
		cols = [col[0] for col in data_cur.description]
		data = [dict(row) for row in data_cur.fetchall()]
		
		if list(field.keys())==cols:
			return 
		
		temp_name = f'{table}_temp'
		cur.execute(f'ALTER TABLE {table} rename to {temp_name}')
		
		try:
			script = ""
			column = list(field.keys())
			for col in column:
				script = script + f'{col} {field[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE {table}({script})")
			values = []
			script = f'INSERT INTO {table} VALUES({",".join(["?"]*len(column))})'
			for i in range(len(data)):
				row = data[i]
				temp_val = []
				for colname in column:
					value = row[colname] if colname in cols else None
					temp_val.append(value)
				values.append(temp_val)
			print(f'Script: {script}')
			print(values)
			cur.executemany(script, values)
			cur.execute(f'DROP TABLE {temp_name}')
			conn.commit()
		except Exception as e:
			cur.execute(f'ALTER TABLE {temp_name} rename to {table}')


	def setup(self, guild_id):
		self.check(guild_id)
		print('  check complete')
		self.create_DB(guild_id)
		print('  create db complete')
		return self.connect(guild_id)

	def create_DB(self,guild_id):
		conn = None
		try:
			print('start Setup Process')
			conn = sqlite3.connect(os.path.join(DB_FOLDER_PATH, f'{guild_id}.db'))
			self.creat_user(conn)
			self.create_chara(conn)
			self.create_NPC(conn, guild_id)
			self.create_store(conn)
			self.default_setting(conn)
			self.create_fishing(conn)
			self.creat_gather(conn)
			self.create_merge(conn)
			print('finish Setup Process')
		except Exception as e:
			print(e)
			print(traceback.format_exc())
		finally:
			if conn:
				conn.close()

	def creat_user(self, conn:sqlite3.Connection):
		cur = conn.cursor()
		user_list = ("id","user","loc","fish","size")
		inventory_list = ("id","gold","size","item")
		user = {
			"id":"integer primary key",
			"name":"text",
			"thread":"integer",
			"charas":"text",
		}
		check_user = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='user'").fetchone()[0]
		if check_user != 1:
			print('creat user')
			script = ""
			for col in list(user.keys()):
				script = script + f'{col} {user[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE user({script})")
			conn.commit()
		else:
			self.update(conn, user, 'user')
			
	def create_chara(self, conn:sqlite3.Connection):
		cur = conn.cursor()
		chara_list = ("id","name","keyword","desc")
		chara={
			"code":"text primary key",
			"name":"real",
			"keyword":"integer",
			"desc":"text",
			"link":"text",
			"color":"integer",
		}
		stat = {
			"code":"text primary key",
			"point":"integer",
			"statname":"text",
			"stat1":"integer",
			"stat2":"integer",
			"stat3":"integer",
			"stat4":"integer",
			"stat5":"integer",
			"stat6":"integer",
		}
		inventory={
			"code":"text primary key",
			"gold":"real",
			"size":"integer",
			"item":"text"
		}
		check_chara = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='chara'").fetchone()[0]
		check_stat = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='stat'").fetchone()[0]
		check_inventory = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='inventory'").fetchone()[0]
		if check_chara != 1:
			print('creat chara')
			script = ""
			for col in list(chara.keys()):
				script = script + f'{col} {chara[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE chara({script})")
			conn.commit()
		else:
			self.update(conn, chara, 'chara')

		if check_stat != 1:
			print('creat stat')
			script = ""
			for col in list(stat.keys()):
				script = script + f'{col} {stat[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE stat({script})")
			conn.commit()
		else:
			self.update(conn, stat, 'stat')
			
		if check_inventory != 1:
			print('creat inventory')
			script = ""
			for col in list(inventory.keys()):
				script = script + f'{col} {inventory[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE inventory({script})")
			conn.commit()
		else:
			self.update(conn, inventory, 'inventory')

	def create_NPC(self, conn:sqlite3.Connection, guils_id):
		cur = conn.cursor()
		NPC = {
			"code":"text primary key",
			"name":"text",
			"color":"integer",
		}
		NPC_vers = {
			"code":"text",
			"type":"text",
			"vers":"text"
		}
		check_NPC = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='NPC'").fetchone()[0]
		check_NPC_vers = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='NPC_vers'").fetchone()[0]
		if check_NPC != 1:
			print('creat NPC')
			script = ""
			for col in list(NPC.keys()):
				script = script + f'{col} {NPC[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE NPC({script})")

			code = "NPC_store001"
			name = "상점NPC"

			cur.execute('INSERT INTO NPC VALUES(?,?,?)',(code, name, 0))
			cases = ["환영","판매성공","구매취소","잔액부족"]

			for case in cases:
				shutil.copy(resource_path('img','sample.png'), os.path.join(IMG_FOLDER_PATH,str(guils_id),filename(f'{name}_{case}.png')))
			conn.commit()
		else:
			self.update(conn, NPC, 'NPC')

		if check_NPC_vers != 1:
			print('creat NPC')
			script = ""
			for col in list(NPC_vers.keys()):
				script = script + f'{col} {NPC_vers[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE NPC_vers({script})")
			
			code = "NPC_store001"

			cur.executescript(f'''
					INSERT INTO NPC_vers VALUES("{code}","환영","상점에 온걸 환영해!\n사고 싶은걸 골라봐~");
				 	INSERT INTO NPC_vers VALUES("{code}","판매성공","구매해 줘서 고마워!");
				 	INSERT INTO NPC_vers VALUES("{code}","구매취소","다음에 또 방문해줘");
				 	INSERT INTO NPC_vers VALUES("{code}","잔액부족","앗! 금액이 충분하지 않아!\n다음에 다시 찾아와줘~");				 	
				''')
			conn.commit()
		else:
			self.update(conn, NPC_vers, 'NPC_vers')

	def create_store(self, conn:sqlite3.Connection):
		cur = conn.cursor()
		# cur.execute('CREATE TABLE item(code text, name text, description text, number integer, price real)')
		# cur.execute('CREATE TABLE store(code text, sale text, price integer, discount real)')
			
		item_list = ("code","name","description","number","price")
		store_list = ("code","sale","price","discount")
		item = {
			"code":"text primary key",
			"name":"text",
			"description":"str",
			"number":"text",
			"price":"integer"
		}
		store={
			"code":"text primary key",
			"sale":"text",
			"price":"integer",
			"discount":"integer"
		}
		check_item = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='item'").fetchone()[0]
		check_store = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='store'").fetchone()[0]
		if check_item != 1:
			print('creat item data')
			script = ""
			for col in list(item.keys()):
				script = script + f'{col} {item[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE item({script})")
			conn.commit()
		else:
			self.update(conn, item, 'item')
			
		if check_store != 1:
			print('creat store data')
			script = ""
			for col in list(store.keys()):
				script = script + f'{col} {store[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE store({script})")

			cur.executescript('''
				INSERT INTO store values("3001", "True", 10, 1);
				INSERT INTO store values("3002", "True", 20, 1);
				INSERT INTO item values("3001", "칫솔", "빳빳한 칫솔\n양치질은 중요해!", 1, 5);
				INSERT INTO item values("3002", "보석", "아름다운 보석\n선물해 주기 딱 좋다.", 1, 10);
				''')
			conn.commit()
		else:
			self.update(conn, store, 'store')
	
	def create_fishing(self, conn:sqlite3.Connection):
		cur = conn.cursor()
		history_list = ("fishdate","user","loc","fish","size")
		data_list = ("code","name","min","max","baseprice","loc")
		fishing_history = {
			"fishdate":"text",
			"user":"integer",
			"loc":"str",
			"fish":"text",
			"size":"real"
		}
		fishing_data={
			"code":"text primary key",
			"name":"text",
			"min":"integer",
			"max":"integer",
			"baseprice":"integer",
			"loc":"text"
		}
		check_data = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='fishing_data'").fetchone()[0]
		check_history = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='fishing_history'").fetchone()[0]
		if check_data != 1:
			print('creat fishing data')
			script = ""
			for col in list(fishing_data.keys()):
				script = script + f'{col} {fishing_data[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE fishing_data({script})")

			cur.executescript('''
				INSERT INTO fishing_data values("1001", "멸치", 1, 3, 5, "기본 낚시터");
				INSERT INTO fishing_data values("1002", "고등어", 2, 10, 20, "기본 낚시터");
				INSERT INTO item values("1001", "멸치", "작은 멸치\n볶음으로 만들어 먹기에 딱 좋은 크기이다.", 1, 5);
				INSERT INTO item values("1002", "고등어", "고등어\n구워먹으면 맛있다.", 1, 20);
				''')
			conn.commit()
		else:
			self.update(conn, fishing_data, 'fishing_data')
			
		if check_history != 1:
			print('creat fishing history')
			script = ""
			for col in list(fishing_history.keys()):
				script = script + f'{col} {fishing_history[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE fishing_history({script})")
			conn.commit()
		else:
			self.update(conn, fishing_history, 'fishing_history')
	
	def creat_gather(self, conn:sqlite3.Connection):
		cur = conn.cursor()
		history_list = ("gatherdate","user","loc","item","size")
		data_list = ("code","name","min","max","baseprice","loc")
		gather_history = {
			"gatherdate":"text",
			"user":"integer",
			"loc":"str",
			"item":"text",
			"size":"real"
		}
		gather_data={
			"code":"text primary key",
			"name":"text",
			"min":"integer",
			"max":"integer",
			"baseprice":"integer",
			"loc":"text"
		}
		check_data = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gather_data'").fetchone()[0]
		if check_data != 1:
			print('creat gather data')
			script = ""
			for col in list(gather_data.keys()):
				script = script + f'{col} {gather_data[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE gather_data({script})")
			cur.executescript('''
				INSERT INTO gather_data values("2001", "사과", 1, 1, 5, "기본 채집터");
				INSERT INTO gather_data values("2002", "복숭아", 1, 1, 10, "기본 채집터");
				INSERT INTO item values("2001", "사과", "맛있어 보이는 사과\n밤에는 먹지말자.", 1, 5);
				INSERT INTO item values("2002", "복숭아", "복숭아\n털이 많다.", 1, 10);
				''')

			conn.commit()
		else:
			self.update(conn, gather_data, 'gather_data')
		
		check_history = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gather_history'").fetchone()[0]
		if check_history != 1:
			print('creat gather history')
			script = ""
			for col in list(gather_history.keys()):
				script = script + f'{col} {gather_history[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE gather_history({script})")
			conn.commit()
		else:
			self.update(conn, gather_data, 'gather_data')

	def create_merge(self, conn:sqlite3.Connection):
		cur = conn.cursor()
		store_list = ("code","sale","price","discount")
		recipe = {
			"code":"text primary key",
			"name":"text",
			"merge":"text",
			"rate":"integer"
		}
		check_recipe = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='recipe'").fetchone()[0]
		if check_recipe != 1:
			print('creat recipe data')
			script = ""
			for col in list(recipe.keys()):
				script = script + f'{col} {recipe[col]}, '
			script = script[:-2]
			cur.execute(f"CREATE TABLE recipe({script})")
			
			cur.executescript('''
				INSERT INTO recipe values("4001","물고기죽","1001,1002",100);
				INSERT INTO item values("4001", "물고기죽", "여러 물고기를 섞어 끓인 탕.\n맛은 보장할 수 없다.", 1, 10);
				''')
			conn.commit()
		else:
			self.update(conn, recipe, 'recipe')

	def default_setting(self, conn:sqlite3.Connection):
		cur = conn.cursor()
		setting = {
			"type":"text primary key",
			"value":"text"
		}

		check_history = cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='setting'").fetchone()[0]
		if check_history != 1:
			print('creat setting')
			script = ""
			for col in list(setting.keys()):
				script = script + f'{col} {setting[col]}, '
			script = script[:-2]
			
			cur.execute(f"CREATE TABLE setting({script})")
		else:
			self.update(conn, setting, 'setting')
			
		values = {
			"max_fishing":"3",
			"max_gather":"3",
			"base_inv_size":"10",
			"base_inv_gold":"10",
			"accept_user":"True",
			"random_box":"5",
			"gspread_url":"",
			"anon":"익명게시판",
			"manage":"관리",
			"join":"가입",
			"store":"상점",
			"community":"캐입역극",
			"qna":"질의응답",
			"visitor":"방문자",
			"registered":"가입자",
			"admin":"관리자",
			"stat_names":"체력,힘,지능,관찰,민첩,운",
		}
		
		for type in list(values.keys()):
			try:
				cur.execute(f'INSERT INTO setting VALUES("{type}","{values[type]}")')
			except Exception as e:
				# ignore unique error
				e

		conn.commit()

	# def get_db_list(self, conn):
	# 	tables = []
	# 	cur = conn.cursor()
	# 	cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1;")

	# 	for table in cur:
	# 		tables.append(table[0])

	# 	return tables
