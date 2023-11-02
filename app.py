import os, shutil, sys, json
import sqlite3
import logging, logging.handlers, multiprocessing
from io import BytesIO
from PIL import Image
from random import choice, randrange, random
from math import floor
from asyncio import sleep
from copy import deepcopy
from time import strftime,localtime, sleep
from traceback import format_exc

from discord import CustomActivity, Intents
from JAS.resources.Addons import read_json

def run_discord(receive_queue:multiprocessing.Queue, send_queue:multiprocessing.Queue):
	from JAS.resources.Base import JAS, logger, handler
	while True:
		if not receive_queue.empty():
			queuedata = receive_queue.get()
			print('from main discord process >>',queuedata)
			if 'stop process' == queuedata:
				print('  stop process')
				break
			elif 'start bot' == queuedata: 
				try:
					print('startup process')
					data = read_json()
					
					intents = Intents.default()
					intents.message_content = True
					intents.members = True
					intents.guilds = True
	
					activity = CustomActivity(name="Running DEMO...")
					bot = JAS(intents=intents, command_prefix='!', activity=activity, logger=logger)

					bot.rec_queue = receive_queue
					bot.send_queue = send_queue
					bot.TOKEN = data["TOKEN"]
					bot.PROFILE = data["PROFILE"]
					bot.TEST_SERVER_ID = int(data["TEST_SERVER_ID"])
					bot.AUTH_JSON_PATH = data["AUTH_JSON_PATH"]
					print(bot.TOKEN, bot.PROFILE, bot.TEST_SERVER_ID, bot.AUTH_JSON_PATH)
					print('launching discord bot')
					bot.run(bot.TOKEN, log_handler=handler)
					send_queue.put_nowait('bot terminated')
					print('bot terminated')
				except Exception as e:
					send_queue.put('error')
					send_queue.put(str(e))
			else:
				if queuedata != 'stop bot':
					receive_queue.put(queuedata)
		else:
			sleep(1)
	print('end discord process')
	pass

def run_GUI(receive_queue:multiprocessing.Queue, send_queue:multiprocessing.Queue):
	from JAS.UI import QApplication, ComuBotAPP
	app = QApplication(sys.argv)
	main_window = ComuBotAPP()
	main_window.rec_queue = receive_queue
	main_window.send_queue = send_queue
	main_window.show()

	app.exec()
	send_queue.close()
	receive_queue.close()
	print('end GUI process')
	pass


if __name__ == '__main__':
	multiprocessing.freeze_support()
	
	# construct env
	from JAS.resources.Addons import prep_env
	prep_env()

	queue1 = multiprocessing.Queue()
	queue2 = multiprocessing.Queue()
	discord_process = multiprocessing.Process(target=run_discord, args=(queue1,queue2))
	pyGUI_process = multiprocessing.Process(target=run_GUI, args=(queue2,queue1))

	pyGUI_process.start()
	discord_process.start()
	discord_process.join()
	pyGUI_process.join()
