from discord import Embed, Color, File
from JAS.resources.Addons import os, currency, desc_converter, IMG_FOLDER_PATH, filename
import JAS.resources.Connector as Conn

# 공용
def general(title, desc=None, color=Color.dark_grey(), footer=None):
	embed = Embed(title=title, description=desc, color=color)
	if footer: embed.set_footer(text=footer)
	return embed

def warning(title, desc=None):
	return Embed(title=title, description=desc, color=Color.dark_red())

def error(errorcode=None):
	title = "예상치 못한 오류가 발생하였습니다."
	desc = "지속적으로 발생하는 경우 관리자에게 문의 바랍니다."
	if errorcode:
		desc = desc+f'\n오류 내용: {errorcode}'
	return Embed(title=title, description=desc, color=Color.red())

def store(title, desc=None):
	return Embed(title=title, description=desc, color=Color.teal())

# 관리
def setting(title, desc=None, footer=None):
	embed = Embed(title=title, description=desc, color=Color.gold())
	if footer:
		embed.set_footer(text=footer)
	return embed

def show_user(manage:Conn.Connector, id):
	user_name = manage.data.user.data[id].name
	code = manage.data.user.data[id].charas
	chara_data = manage.data.chara.data[code]
	chara_name = chara_data.name
	title = f'{user_name}의 정보입니다.'
	desc = f'id: {id}'
	embed = Embed(title=title, description=desc, color=Color.gold())
	embed.add_field(name="캐릭터",value=f'{chara_name}\n==========\n{str(chara_data)}')
	return embed

def show_system(title, manage:Conn.Vars, footer):
	embed = Embed(title=title, color=Color.gold())
	data = {
		"회원가입 가능여부": "허용" if manage.accept_user else "차단",
		"최대 낚시 횟수": manage.max_fishing,
		"최대 채집 횟수": manage.max_gather,
		"기본 가방 크기": manage.base_inv_size,
		"최초 소지 골드": manage.base_inv_gold,
		"랜덤 박스 가격": manage.random_box,
		"구글 연동 링크": manage.gspread_url or '_',
		"스탯명": str(manage.stat_names),
	}
	for key in list(data.keys()):
		embed.add_field(name=key, value=f'`{data[key]}`', inline=True)
	embed.set_footer(text=footer)
	return embed

def user_accept(manage:Conn.Connector, footer):
	title = "회원가입 가능여부를 설정"
	desc = "회원가입을 허용하시겠습니까?"
	embed = Embed(title=title, description=desc, color=Color.gold())
	value="허용" if manage.data.setting.data.accept_user else "차단"
	embed.add_field(name="현재 설정", value=value)
	embed.set_footer(text=footer)
	return embed

def guide_user(name):
	title = f"{name}님 환영합니다."
	desc = "해당 익명 스레드의 사용법을 설명드리겠습니다."
	embed = Embed(title=title, description=desc, color=Color.gold())
	guide_list={
		"익명 게시판 작성":"해당 스레드에 메세지를 보내시면 해당 메세지는 익명게시판에 작성됩니다.",
		"익명 문의":"/문의 명령어를 이용하시면 비공개 문의를 진행할 수 있습니다.",
		"명령어 사용":"다른 게시판에서와 마찬가지로 명령어의 사용이 가능합니다."
	}
	for name in list(guide_list.keys()):
		value = guide_list[name]
		embed.add_field(name=name, value=value, inline=False)

	return embed

# 낚시
def fishing(type:int):
	types = {
		0:["자리를 준비하는 중...",Color.dark_grey()],
		1:["낚싯대를 드리우는 중...", Color.green()],
		2:["흐르는 물을 바라보는 중...", Color.blue()],
		3:["스쳐 지나가는 물고기 그림자를 바라보는 중...", Color.teal()],
		4:["월척의 꿈을 꾸는 중...",Color.green()],
		9:["앗 느낌이?!",Color.gold()]
	}
	title = types[type][0]
	color = types[type][1]
	embed = Embed(title=title, description=None, color=color)
	return embed

def fishing_result(title, desc, color, result=None):
	image = None
	embed = Embed(title=title, description=desc, color=color)
	context = ""
	if result:
		for item in result:
			context = context + ' / ' + str(item) if context else "🐟 "+str(item)
		embed.set_footer(text = context)
		# embed.add_field(name='크기', value=result["length"], inline=True)
		# embed.add_field(name='가격', value=result["price"], inline=True)
	# file = File(f'resources/img/{image}')
	return embed

def fish_data(title, data:dict[str, list['fishcode':str]], fishinfo:dict[str, Conn.Fish], isOnePlace):
	embed = Embed(title=title, description=None, color=Color.green())
	for place in list(data.keys()):
		context = ""
		name = "물고기 목록" if isOnePlace else place
		for fish in data[place]:
			context = context+','+ fishinfo[fish].name if context else fishinfo[fish].name
		embed.add_field(name=name, value=context, inline=False)
	return embed

def add_fish(title, name, desc, min, max, baseprice, loc):
	embed = Embed(title=title,color=Color.yellow())
	embed.add_field(name="이름",value=name, inline=False)
	embed.add_field(name="설명",value=desc, inline=False)
	embed.add_field(name="최소 길이",value=min, inline=False)
	embed.add_field(name="최고 길이",value=max, inline=False)
	embed.add_field(name="기본 가격",value=baseprice, inline=False)
	embed.add_field(name="등장위치",value=loc, inline=False)
	return embed

# 인텐토리
def inventory(title, desc, inventory:Conn.Backpack, items:dict[str, Conn.Item]):
	embed = Embed(title=title, description=desc, color=Color.teal())
	# index = 0
	gold = inventory.gold
	if inventory.items:
		for item in inventory.items:
			itemcode = item.split('_')[0]
			name = items[itemcode].name
			price = '가격: '+currency(0, str(items[itemcode].price)) if items[itemcode].price else ""
			embed.add_field(name=name, value=price, inline=False)
	else:
		name = ""
		value = ""
		# embed.add_field(name=name, value=value)
	embed.set_footer(text=f"{currency(0, gold)}")
	return embed

def sold_item(gold):
	title="아이템을 판매하였습니다."
	desc=f"총 가격: {gold}"
	color = Color.teal()
	return Embed(title=title, description=desc, color=color)

def random_box(title, count:int):
	spin = [
		"/","―","\\","|"
	]
	desc = spin[count%4]
	embed = Embed(title=title, description=desc, color=Color.brand_red()) 
	return embed

# 캐릭터
def chara_talk(data:Conn.Chara, iconpath, content, color):
	name = data.name
	# embed = Embed(title=name, description=desc_converter(content), color=color)
	embed = Embed(title=None, description=desc_converter(content), color=color)
	icon = 'icon.png'
	try:
		file = File(iconpath, filename=icon)
	except:
		file = File(os.path.join(IMG_FOLDER_PATH, 'sample.png'), filename=icon)
	embed.set_thumbnail(url=f"attachment://{icon}")
	return embed, file

def show_chara(data:Conn.Chara, imgpath="img/sample.png"):
	name = data.name
	keyword = data.keyword.replace(',',' / ')
	desc = data.desc
	link = f'[신청서 링크]({data.link})'
	color = data.color or Color.light_grey().value
	embed = Embed(title=name, color=Color(color))
	icon = 'icon.png'
	try:
		file = File(imgpath, filename=icon)
	except:
		file = File("img/sample.png", filename=icon)
	embed.set_image(url=f"attachment://{icon}")
	embed.add_field(name="키워드", value=keyword, inline=False)
	embed.add_field(name="소개", value=desc, inline=False)
	if data.stat:
		stat_names = data.stat.stat_names
		embed.add_field(name=stat_names[0], value=data.stat.stat1, inline=True)
		embed.add_field(name=stat_names[1], value=data.stat.stat2, inline=True)
		embed.add_field(name=stat_names[2], value=data.stat.stat3, inline=True)
		embed.add_field(name=stat_names[3], value=data.stat.stat4, inline=True)
		embed.add_field(name=stat_names[4], value=data.stat.stat5, inline=True)
		embed.add_field(name=stat_names[5], value=data.stat.stat6, inline=True)
		embed.add_field(name="스탯포인트", value=data.stat.point, inline=False)
	embed.add_field(name="신청서", value=link, inline=False)
	return embed, file

def show_npc(data:Conn.NPC):
	name = data.name
	number = data.number
	cases = data.case.split(',')
	vers = data.vers
	color = data.color or Color.light_grey().value
	desc = '총 대사 수: ' + str(number)
	embed = Embed(title=name, description=desc, color=Color(color))
	for case in cases:
		embed.add_field(name=case, value=vers[cases.index(case)], inline=False)
	return embed

def show_stat_result(data:Conn.Chara):
	title = f"{data.name}의 스탯적용을 완료하였습니다."
	desc = f"남은 포인트: {data.stat.point}"
	embed = Embed(title=title, description=desc, color=Color.brand_green())
	embed.add_field(name='체력', value=data.stat.stat1)
	embed.add_field(name='힘', value=data.stat.stat2)
	embed.add_field(name='지능', value=data.stat.stat3)
	embed.add_field(name='관찰', value=data.stat.stat4)
	embed.add_field(name='민첩', value=data.stat.stat5)
	embed.add_field(name='운', value=data.stat.stat6)
	return embed

def anon_qna(question, answer):
	title = "익명문의"
	embed = Embed(title=title, description=question, color=Color.dark_gold())
	embed.add_field(name="답변", value=answer)
	return embed

# 투표
def vote(timeout:int, op1:str, op2:str, op3:str, op4:str, op5:str):
	embed = Embed(title='투표', color=Color.brand_green())
	if '/' in op1:
		embed.add_field(name='1. '+op1.split('/')[0], value=op1.split('/')[1], inline=False)
	else:
		embed.add_field(name='1. '+op1.split('/')[0], value='', inline=False)
	if '/' in op2:
		embed.add_field(name='2. '+op2.split('/')[0], value=op2.split('/')[1], inline=False)
	else:
		embed.add_field(name='2. '+op2.split('/')[0], value='', inline=False)
	if op3: 
		if '/' in op3:
			embed.add_field(name='3. '+op3.split('/')[0], value=op3.split('/')[1], inline=False)
		else:
			embed.add_field(name='3. '+op3.split('/')[0], value='', inline=False)
	if op4:
		if '/' in op4:
			embed.add_field(name='4. '+op4.split('/')[0], value=op4.split('/')[1], inline=False)
		else:
			embed.add_field(name='4. '+op4.split('/')[0], value='', inline=False)
	if op5:
		if '/' in op5:
			embed.add_field(name='5. '+op5.split('/')[0], value=op5.split('/')[1], inline=False)
		else:
			embed.add_field(name='5. '+op5.split('/')[0], value='', inline=False)
	time = '{0}시간 {1}분'.format(*divmod(timeout,60)) if timeout >= 60 else f'{timeout}분'
	embed.set_footer(text=f'진행시간: {time}')
	return embed

def vote_result(total:int, data:dict[str, list[int, int]]):
	embed = Embed(title="투표 결과 입니다", description=f"총 투표수: {total}", color=Color.light_grey())
	for key in list(data.keys()):
		embed.add_field(name=f'{key} ({data[key][0]}%)', value='`'+'■'*(data[key][0]//10)+'□'*(10-data[key][0]//10)+' '+str(data[key][1])+'`', inline=False)
	return embed
