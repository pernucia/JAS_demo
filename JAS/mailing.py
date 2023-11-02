import smtplib, ssl, os
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

if __name__ != '__main__':
  from COMUBOT.resources.Addons import MAIN_PATH
else:
  from resources.Addons import MAIN_PATH

class Mailer():
  def __init__(self, host, port,mail_ID, mail_PW) -> None:
    smtp = smtplib.SMTP(host=host, port=port)
    smtp.starttls()
    self.sender = smtp
    self.ID = mail_ID
    self.PW = mail_PW

  def login(self):
    self.sender.login(self.ID, self.PW)

  def exit(self):
    self.sender.quit()

  def send_email(self, body_type, mail_body, mail_subject="[NOTICE] 디코봇으로 부터 발송된 메일입니다."):
    self.login()
    if body_type == 0:
      body = MIMEText(mail_body, 'plain', 'utf-8')
    elif body_type == 1:
      body = MIMEText(mail_body, 'html', 'utf-8')
    else:
      raise 
    
    message = MIMEMultipart()
    message["subject"] = Header(s=mail_subject, charset='utf-8')
    message["FROM"] = self.ID
    message["TO"] = self.ID
    message.attach(body)
    self.get_log(message)

    self.sender.sendmail(self.ID, self.ID, message.as_string())
    self.exit()
  
  def get_log(self, message:MIMEMultipart):
    files = [os.path.join(MAIN_PATH, 'discord.log'), os.path.join(MAIN_PATH, 'discord_debug.log')]

    for file in files:
      if os.path.exists(file):
        attachment = MIMEApplication(open(file, 'rb').read())
        attachment.add_header('Content-Disposition', 'attachment', filename=file.split('\\')[-1])
        message.attach(attachment)


if __name__ == '__main__':
  from resources.Addons import read_json
  json_data = read_json()
  SMTP_SERVER = json_data['SMTP_SERVER']
  SMTP_PORT = json_data['SMTP_PORT']
  MAIL_ID = json_data['MAIL_ID']
  MAIL_PW = json_data['MAIL_PW']
  mail = Mailer(SMTP_SERVER, SMTP_PORT, MAIL_ID, MAIL_PW)
  mail.send_email(0,'test')
