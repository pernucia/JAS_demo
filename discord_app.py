#run.py
import discord, traceback, os, logging, logging.handlers
from discord.ext import tasks

#get libs
from JAS.resources.Exceptions import *
from JAS.resources.Addons import read_json, prep_env

if __name__ == '__main__':
  prep_env()
  from JAS.resources.Base import JAS, logger, handler
  from JAS.mailing import Mailer
  
  #intents
  intents = discord.Intents.default()
  intents.message_content = True
  intents.members = True
  intents.guilds = True
  while True:
    data = read_json()
    SMTP_SERVER = data['SMTP_SERVER']
    SMTP_PORT = data['SMTP_PORT']
    MAIL_ID = data['MAIL_ID']
    MAIL_PW = data['MAIL_PW']
    mail_sender = Mailer(SMTP_SERVER, SMTP_PORT, MAIL_ID, MAIL_PW)

    activity = discord.CustomActivity(name="⚙️ 위이잉 치킨")
    bot = JAS(intents=intents, command_prefix='!', activity=activity, logger=logger)
    bot.TOKEN = data["TOKEN"]
    bot.PROFILE = data["PROFILE"]
    bot.TEST_SERVER_ID = int(data["TEST_SERVER_ID"])
    bot.AUTH_JSON_PATH = data["AUTH_JSON_PATH"]
    
    bot.run(bot.TOKEN, log_handler=handler)

    if bot.is_quit:
      break
    else:
      # print('error')
      mail_sender.send_email(0,'봇이 의도치 않게 중단되었습니다. 로그를 확인하여 주시기 바랍니다.')