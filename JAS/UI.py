import sys, logging, os, multiprocessing
import logging, logging.handlers
from time import sleep
import uuid, clipboard

#Pyside6
from PySide6.QtCore import QRunnable, Slot, QThreadPool, QObject, Signal, QThread
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout
from PySide6.QtWidgets import QPlainTextEdit, QLabel, QLineEdit, QComboBox, QStatusBar
from PySide6.QtGui import QIcon, QScreen, QAction, QFont

#get libs
from JAS.resources.Addons import read_json, write_json, MAIN_PATH, IMG_FOLDER_PATH, resource_path
from JAS.resources.Exceptions import *

class QueueMsg():
	msg_dict = {
		"가동 실패":'봇 가동에 실패하였습니다.',
		"봇 운영중":"봇 가동이 성공적으로 진행되었습니다.",
		"봇 정지":"봇이 중지되었습니다.",
		"경고":"봇 가동 중 경고 사항이 발견되었습니다.",
		"오류 발생":'봇 가동 중 오류가 발생하였습니다.',
	}
	
	@property
	def run_failed(self) -> str: return "가동 실패"
	@property
	def started(self) -> str: return "봇 운영중"
	@property
	def closed(self) -> str: return "봇 정지"
	@property
	def warn(self) -> str: return "경고"
	@property
	def error(self) -> str: return "오류 발생"
	

class PySideHdr(logging.handlers.RotatingFileHandler):
	def __init__(self, logbox, filepath) -> None:
		super().__init__(filename=filepath, encoding='utf-8', maxBytes=32 * 1024 * 1024, backupCount=5)
		self.logbox:QPlainTextEdit = logbox

	def emit(self, record):
		self.logbox.appendPlainText(self.format(record))


class WorkerSignals(QObject):
	started = Signal(str)
	closed = Signal(str)
	run_fail = Signal(str)
	error = Signal(str)
	warning = Signal(str)
	terminate = Signal()

	queue_check_in = Signal(object)
	queue_check_out = Signal()


class Worker(QRunnable):
	signals = WorkerSignals()

	def __init__(self) -> None:
		super().__init__()
		self.is_stop = False
		self.queue_empty = True
		self.queue_msg = ''
		self.signals.terminate.connect(self.stop)
		self.signals.queue_check_in.connect(self.check_in)
	
	@Slot()
	def run(self):
		wait_count = 0
		connected = False
		while True:
			if self.is_stop:
				return
			
			if not connected:
				if wait_count == 100:
					print('===launch failed===')
					self.signals.run_fail.emit(QueueMsg().run_failed)
					break
				else:
					wait_count += 1
					sleep(1)

			self.check_out()
			if self.queue_empty:
				wait_time = 5 if connected else 1
				sleep(wait_time)
			else:
				if 'started' == self.queue_msg:		# 봇 가동 확인
					print('===bot connected===')
					connected = True
					self.signals.started.emit(QueueMsg().started)
				elif 'warn' == self.queue_msg:
					print('===warning===')
					self.signals.warning.emit(QueueMsg().warn)
					sleep(1)
				elif 'closed' == self.queue_msg:
					print('===closed===')
					self.signals.closed.emit(QueueMsg().closed)
					self.is_stop = True
					break
				elif 'error' == self.queue_msg:
					print('===error===')
					self.signals.error.emit(QueueMsg().error)
					break
				self.queue_empty = True
				self.queue_msg = ''
		pass

	@Slot()
	def stop(self):
		print('stop msg send')
		self.is_stop = True

	@Slot()
	def check_out(self) -> None:
		# print('checkout')
		self.signals.queue_check_out.emit()
		sleep(1)
		return 

	@Slot()
	def check_in(self, result):
		if type(result) == bool:
			self.queue_empty = result
		else:
			self.queue_msg = result

# Main Window
class ComuBotAPP(QMainWindow):
	rec_queue:multiprocessing.Queue
	send_queue:multiprocessing.Queue
	data = {
		"TOKEN":"",
		"PROFILE":"",
		"TEST_SERVER_ID":"",
		"AUTH_JSON_PATH":"",
		"AUTH_KEY":"",
	}
	is_stoped = True

	def __init__(self) -> None:
		super().__init__()
		self.get_vars()
		self.define_btns()
		self.set_logger()
		self.threadpool:QThreadPool = QThreadPool()
		self.initUI()

	def initUI(self):
		self.cwidget = self.center_widget_init()
		self.setCentralWidget(self.cwidget)

		self.setWindowTitle(f'JAS [DEMO]')
		self.setWindowIcon(QIcon(resource_path('img/UI/icon.png')))
		self.setGeometry(300,300,600,500)

		self.setStatusBar(QStatusBar())

		self.toolbar = self.toolbar_init()
		self.logger.info('===안녕하세요 여러분의 도우미 J.A.S.입니다===')
		self.center()

	# cWidget
	def center_widget_init(self):
		cwidget = QWidget()

		grid = QGridLayout()
		grid.addWidget(self.tokenLabel, 0, 0)
		grid.addWidget(self.serverLabel, 1, 0)
		grid.addWidget(self.statusLabel, 2, 0)

		grid.addWidget(self.tokenLine, 0, 1)
		grid.addWidget(self.serverLine, 1, 1)
		grid.addWidget(self.statusLine, 2, 1)
		grid.addWidget(self.logText, 3, 0, 1, 2)
		
		cwidget.setLayout(grid)
		return cwidget

	# toolbar
	def toolbar_init(self):
		toolbar = self.addToolBar('main toolbar')
		toolbar.setMovable(False)
		toolbar.addAction(self.runbtn)
		toolbar.addAction(self.stopbtn)
		toolbar.addSeparator()
		toolbar.addAction(self.savebtn)
		toolbar.addAction(self.openbtn)
		toolbar.addSeparator()
		toolbar.addAction(self.exitbtn)
		return toolbar

	def center(self):
		center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
		geo = self.frameGeometry()
		geo.moveCenter(center)
		self.move(geo.topLeft())

	def define_btns(self):
		runAction = QAction(QIcon(resource_path('img/UI/play.png')), '실행', self)
		runAction.setShortcut('Ctrl+R')
		runAction.setStatusTip('봇 구동')
		runAction.triggered.connect(self.run)
		self.runbtn =  runAction

		stopAction = QAction(QIcon(resource_path('img/UI/stop.png')), '정지', self)
		stopAction.setShortcut('Ctrl+E')
		stopAction.setStatusTip('봇 정지')
		stopAction.triggered.connect(self.stop)
		stopAction.setEnabled(False)
		self.stopbtn = stopAction

		saveAction = QAction(QIcon(resource_path('img/UI/disk.png')), '설정 저장', self)
		saveAction.setShortcut('Ctrl+S')
		saveAction.setStatusTip('설정 저장')
		saveAction.triggered.connect(self.save_setting)
		self.savebtn =  saveAction

		openAction = QAction(QIcon(resource_path('img/UI/folder.png')), '데이터 위치 열기', self)
		openAction.setShortcut('Ctrl+O')
		openAction.setStatusTip('데이터 위치 열기')
		openAction.triggered.connect(self.open_btn)
		self.openbtn =  openAction

		exitAction = QAction(QIcon(resource_path('img/UI/exit.png')), '종료', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('종료')
		exitAction.triggered.connect(self.close_btn)
		self.exitbtn =  exitAction

		self.tokenLabel = QLabel('봇 Token')
		self.serverLabel = QLabel('테스트 서버 ID')
		self.statusLabel = QLabel('상태')

		self.tokenLine = QLineEdit(self.data["TOKEN"])
		self.tokenLine.setEchoMode(QLineEdit.Password)
		self.serverLine = QLineEdit(str(self.data["TEST_SERVER_ID"]))
		self.statusLine = QLabel()
		self.logText = QPlainTextEdit()
		self.logText.setReadOnly(True)
		self.logText.setFont(QFont("Courier New", 10))

	def set_logger(self):
		logger = logging.getLogger('PySide6')
		logger.setLevel(logging.INFO)

		filepath = os.path.join(MAIN_PATH, 'UI.log')
		pyside_handler = PySideHdr(self.logText, filepath)
		dt_fmt = '%m-%d %H:%M:%S'
		formatter = logging.Formatter('[{asctime}][{levelname:<8}] {message}', dt_fmt, style='{')
		pyside_handler.setFormatter(formatter)
		logger.addHandler(pyside_handler)

		self.logger = logger

	def get_vars(self):
		self.data = read_json()

	def set_vars(self):
		self.data['TOKEN'] = self.tokenLine.text()
		self.data['PROFILE'] = '테스트'
		self.data['TEST_SERVER_ID'] = int(self.serverLine.text())

		write_json(self.data)

	# signals
	def check_queue(self):
		is_empty = self.rec_queue.empty()
		if is_empty:
			self.worker.signals.queue_check_in.emit(True)
		else:
			self.worker.signals.queue_check_in.emit(False)
			self.worker.signals.queue_check_in.emit(self.rec_queue.get())

	def started(self, string):
		print('started', string)
		self.statusLine.setText(string)
		self.logger.info(QueueMsg.msg_dict[string])

	def closed(self, string):
		print('closed', string)
		self.logger.info(QueueMsg.msg_dict[string])
		self.statusLine.setText('봇 정지')
		self.is_stoped = True
		self.available_on_stop()

	def run_failed(self, string):
		print('run fail', string)
		self.is_stoped = True
		self.statusLine.setText(string)
		self.logger.error(QueueMsg.msg_dict[string])

	def warning(self, string):
		print('warning', string)
		self.logger.warn(QueueMsg.msg_dict[string])
		self.logger.warn(self.rec_queue.get(timeout=10))

	def error_occured(self, string):
		print('error_occured', string)
		self.is_stoped = True
		self.statusLine.setText(string)
		self.logger.error(QueueMsg.msg_dict[string])
		self.logger.warn(self.rec_queue.get(timeout=10))

	def disable_on_start(self):
		self.runbtn.setEnabled(False)
		self.savebtn.setEnabled(False)
		self.openbtn.setEnabled(False)
		self.exitbtn.setEnabled(False)

		self.stopbtn.setEnabled(True)
		
		self.tokenLine.setEnabled(False)
		self.serverLine.setEnabled(False)

	def available_on_stop(self):
		self.runbtn.setEnabled(True)
		self.savebtn.setEnabled(True)
		self.openbtn.setEnabled(True)
		self.exitbtn.setEnabled(True)

		self.stopbtn.setEnabled(False)
		
		self.tokenLine.setEnabled(True)
		self.serverLine.setEnabled(True)


	@Slot()
	def run(self):
		print('===run bot===')
		try:
			self.send_queue.put('start bot')
			self.statusLine.setText('봇 가동')
			self.logger.info('봇을 가동합니다.')
			
			worker = Worker()
			worker.signals.queue_check_out.connect(self.check_queue)
			worker.signals.started.connect(self.started)
			worker.signals.run_fail.connect(self.run_failed)
			worker.signals.closed.connect(self.closed)
			worker.signals.warning.connect(self.warning)
			worker.signals.error.connect(self.error_occured)
			self.threadpool.start(worker)
			self.worker = worker
			self.is_stoped = False
			self.disable_on_start()
		except Exception as e:
			print(traceback.format_exc())
			self.statusLine.setText('봇 실행 중 오류 발생')
			self.logger.error(str(e))
			self.available_on_stop()

	@Slot()
	def stop(self):
		print('===stop bot===')
		self.send_queue.put('stop bot')
		self.logger.info('봇을 정지합니다.')
		# self.worker.signals.terminate.emit()
	
	@Slot()
	def save_setting(self):
		print('===save setting===')
		self.set_vars()
		self.statusLine.setText('설정 저장')
		self.logger.info('설정이 저장되었습니다.')

	@Slot()
	def open_btn(self):
		print('=====open folder=====')
		os.startfile(MAIN_PATH)

	@Slot()
	def close_btn(self):
		print('===exit app===')
		if self.is_stoped:
			self.send_queue.put_nowait('stop process')
			self.close()
		else:
			self.logger.warn('봇이 가동중입니다.')
			self.logger.info('봇을 정지 시킨 후 앱을 종료 해 주시기 바랍니다.')


