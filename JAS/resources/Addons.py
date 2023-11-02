import math, discord, re, json
import os, sys, shutil
from PIL import Image
from io import BytesIO
from random import randrange
from traceback import format_exc

PRJ_NAME = 'JAS'
if sys.platform.startswith('win'):
	MAIN_PATH = os.path.join(os.getenv('APPDATA'), PRJ_NAME)
else:
	MAIN_PATH = os.path.join(os.getcwd(), '..', 'DATA')
CONFIG_PATH = os.path.join(MAIN_PATH, 'config.json')
DB_FOLDER_PATH = os.path.join(MAIN_PATH, 'DB')
IMG_FOLDER_PATH = os.path.join(MAIN_PATH, 'IMG')

def resource_path(*path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, *path)

def prep_env():
	for path in [MAIN_PATH, DB_FOLDER_PATH, IMG_FOLDER_PATH]:
		if not os.path.exists(path):
			os.makedirs(path, exist_ok=True)
			if path == MAIN_PATH:
				data = {
					"TOKEN":"",
					"PROFILE":"가동",
					"TEST_SERVER_ID":"",
					"AUTH_JSON_PATH":"",
					"SMTP_SERVER":"smtp.gmail.com",
					"SMTP_PORT":587,
					"MAIL_ID":"",
					"MAIL_PW":"",
				}
				write_json(data)
			if path == IMG_FOLDER_PATH:
				for filename in ['img/sample.png']:
					shutil.copy(resource_path(filename), os.path.join(IMG_FOLDER_PATH,filename.split('/')[-1]))
	
def read_json():
	with open(CONFIG_PATH, 'r', encoding='UTF8') as f:
		json_data:dict[str, str] = json.load(f)
		f.close()
	return json_data

def write_json(data):
	with open(CONFIG_PATH, 'w', encoding='UTF8') as f:
		json_data = json.dumps(data, indent=2)
		f.writelines(json_data)
		f.close()
	
def currency(type, gold):
		content = f"G {gold}"
		return content

def filename(str:str) -> str:
	filterlist = ['?','/','\\',':','*','"','<','>']
	replaceist = ['|']*len(filterlist)
	result = str.translate(str.maketrans(''.join(filterlist), ''.join(replaceist))).replace('|', '')
	return result

async def resize_img(attachment:discord.Attachment, path):
	size = (300,300)
	image = await attachment.read(use_cached=True)
	
	with Image.open(BytesIO(image)) as img:
		img.thumbnail(size)
		img.save(path)
		
def key_gen(key_len=8):
	"""
	8자의 랜덤한 키를 생성합니다.

	Args:
		length: 키의 길이 (기본값: 8)

	Returns:
		8자의 랜덤한 키
	"""
	chars = "abcdefghijklmnopqrstuvwxyz0123456789"

	key = ''
	for _ in range(key_len):
		key = key + chars[randrange(len(chars))]
	return key

def dice(count:int, num:int) -> list[int]:
	"""
	주사위를 굴려 결괏값을 리스트로 반환받습니다.
	
	Args:
		count: 주사위의 개수
		num: 주사위의 눈수
	
		Returns:
			각각의 주사위 결과가 담긴 리스트
	"""
	result = randrange(num)+1
	return [result] + dice(count-1, num) if count != 1 else [result]

def desc_converter(str:str):
	result = str
	match_bold = re.compile('\[[^]]*]')
	match_dice = re.compile('\[[0-9]+d[0-9]+\]')
	# print(re.findall(match_dice, result))
	for text in re.findall(match_dice, result):
		# print(text)
		if text:
			dice_count = int(text[1:-1].split('d')[0])
			dice_num = int(text[1:-1].split('d')[1])
			dice_result = sum(dice(dice_count, dice_num))
			dice_result = f'[{dice_result}]'
			result = result.replace(text, dice_result, 1)
	# print(result)
	for text in re.findall(match_bold, result):
		if text:
			bold_result = f'[**`{text[1:-1]}`**]'
			result = result.replace(text, bold_result)
	# print(result)
	return result

def open_image(path) -> Image.Image:
	img = Image.open(path)
	return img

def merge_image(base:Image.Image, input:Image.Image, x, y) -> Image.Image:
	base.paste(input, (x, y), input)
	return base
	
def crop_icon(base:Image.Image, x, y, width) -> Image.Image:
	icon = base.crop((x, y, x+width, y+width))
	return icon