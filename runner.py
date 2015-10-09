#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asterisk.manager
import sys
import os
import time
import logging
import threading
import subprocess
import socket
import datetime


from random import randint
from pprint import pformat

import config
from functions import *

__author__ = "Egor Potiomkin"

# info from asterisk
callId = os.environ['UNIQUEID']
channel = os.environ['CHANNEL']
phone = os.environ['PHONE']

### communication with liquidsoap
#socketPath = '/tmp/testliq.sock'
socketPath = config.socketPath + phone + '.sock'
client = None
popen = None
# interactive variables
#switchSayBalance = False # change when you want to say balance
#switchSayPosition = False
position = "0"
currentMusicNumber = get_current_music_number(phone)
lastPressTime = {}
positionLastSay = 0 # Количество итераций после поледнего говорения позиции

currentActionId = 'LiquidsoapID'; # to checkthat we handle event for our request
logger = logging.getLogger(__name__)
filelog = logging.FileHandler("/var/log/asterisk/moh_liquidsoap.log")
formatter = logging.Formatter('%(asctime)s callid %(callid)s : %(message)s')
filelog.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(filelog)
logger = logging.LoggerAdapter(logger, {"callid": callId})

def on_dtmf(event, manager):
	#global switchSayBalance
	global phone
	global currentMusicNumber
	global callid
	global positionLastSay
	if (event.headers['Channel'] == channel):
		logger.debug('DTMF: ' + str(event.headers))
		# не обрабатываем слишком частые нажатия клавиш
		if event.headers['Digit'] in lastPressTime and event.headers['Digit'] in config.digitPressDelay and (datetime.datetime.now()-lastPressTime[event.headers['Digit']]).total_seconds() < config.digitPressDelay[event.headers['Digit']]:
			return
		lastPressTime[event.headers['Digit']] = datetime.datetime.now()
		if (event.headers['Digit'] == '2'):
			# Говорим баланс
			logger.debug('Say balance: %s' % str(list_balance_files(phone)))
			socket_queue_push_list('balance', list_balance_files(phone))
		if (event.headers['Digit'] == '3'):
			# Меняем музыку случайно
			currentMusicNumber = (currentMusicNumber + 1) % len(config.musics)
			logger.debug('Change music to: ' + config.musics[currentMusicNumber])						
			socket_var_set('music', 'music%s' % currentMusicNumber)
			update_current_music(phone, currentMusicNumber)
		if (event.headers['Digit'] == '4'):
			# Говорим номер в очереди
			logger.debug('Say position: %s' % position)
			positionLastSay = 0
			socket_queue_push_list('qposition', list_files_to_say_position(position))

def on_queueentry(event, manager):
	global position
	global switchSayPosition
	global positionLastSay
	if (event.headers['Channel'] == channel):
		if position != event.headers['Position']:
			logger.debug('Position changed, old: %s, new: %s' % (position, event.headers['Position']))
			position = event.headers['Position']
			positionLastSay = 0
			socket_queue_push_list('qposition', list_files_to_say_position(position))
	# also say position every 120 sec
	if (positionLastSay > 119):
		socket_queue_push_list('qposition', list_files_to_say_position(position))
		positionLastSay = 0	

def socket_connect():
	global client
	if os.path.exists(socketPath):
		client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )	
		client.connect(socketPath)
	else:
		raise Exception("Socket %s is not exists" % socketPath)

def socket_cmd_run(cmd):
	global client
	try:	
		client.send(cmd + "\n")
	except:
		client.close()
		socket_connect()
		client.send(cmd + "\n")

	datagram = client.recv( 2048 )
	logger.debug("socket cmd <%s>, answer: %s" % (cmd, datagram))

def socket_var_set(variable, value):
	if type(value) is str:
		value = '"%s"' % value
	elif type(value) is bool:
		value = str(value).lower()
	
	socket_cmd_run("var.set " + variable + "=" +  value )
	
def socket_queue_push_list(queue, filelist):
	client.close() # reopen socket before push list to have enough time
	for f in filelist:
		socket_cmd_run("%s.push %s" % (queue, f))

def get_queue_status_periodic():
	global positionLastSay
	while True:
		cdict = {"Action": "QueueStatus"}
		response = manager.send_action(cdict)
		positionLastSay += 10;
		time.sleep(10)

def cleanup():
	"""
	clean before exit
	TODO: it doesnot work because asterisk probably kill -9 process 
	"""
	global liquidsoapfile
	global liquidsoap_process
	global client
	global socketPath
	raise Exception("test except")
	try:
		client.close()
	except:
		pass
	liquidsoap_process.terminate()
	try:
		os.remove(liquidsoapfile)
	except OSError:
		pass
	try:
		os.remove(socketPath)
	except OSError:
		pass
	
manager = asterisk.manager.Manager()

try:
	FNULL = open(os.devnull, 'w')	
	# При передаче скрипта liquidsoap как параметра или на стандартынй вывод не работает логирование,
	# Поэтому мы сначала формируем файл, а потом запускаем с ним в качестве параметра
	# popen = subprocess.Popen("/usr/bin/liquidsoap '%s'" % get_liquidsoap_script(phone, socketPath), shell=True, stderr=FNULL)
	#
	liquidsoapfile = config.socketPath + 'liquidsoap.liq'
	try:
		with open(liquidsoapfile, "w") as text_file:
			text_file.write(get_liquidsoap_script(phone, socketPath, currentMusicNumber))
	except Exception as e:
		logger.error("Cannot rewrite liquidsoap.liq script file, error: %s" % str(e))
	cmd = "/usr/bin/liquidsoap %s" % (liquidsoapfile)
	liquidsoap_process = subprocess.Popen(cmd.split(), stderr=FNULL)
	#atexit.register(cleanup) TODO doesn work yet
	logger.debug('New call to queue, phone: %s, callid: %s, channel: %s' % (phone, callId, channel))
	time.sleep(1) # let liquidsoap open socket
	socket_connect()
	manager.connect('127.0.0.1') 
	manager.login('admin', 'admin')
	manager.register_event('DTMF', on_dtmf)
	manager.register_event('QueueEntry', on_queueentry)
	get_queue_status_periodic()
	
except asterisk.manager.ManagerSocketException as err:
	errno, reason = err
	logger.error("Error connecting to the manager: %s" % reason)
	sys.exit(1)
except asterisk.manager.ManagerAuthException as reason:
	logger.error("Error login in to the manager: %s" % reason)
	sys.exit(1)
except asterisk.manager.ManagerException as reason:
	logger.error("Error: %s" % reason)
	sys.exit(1)

