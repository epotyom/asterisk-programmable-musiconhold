#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import phpserialize
import os.path

from gtts import gTTS

import config

# массиы для говорения чисел и денег
# True - male
d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19 = {3: ['tysach', 'Female'], 6: ['millionov', 'Male'], 9: ['milliardov', 'Male'], 12: ['trillionov', 'Male'], 15: ['kvadrillionov', 'Male'], 'rub': ['rubley', 'Male'], 'kop': ['kopeek', 'Female']}
d1 = {3: ['tysacha', 'Female'], 6: ['million', 'Male'], 9: ['milliard', 'Male'], 12: ['trillion', 'Male'], 15: ['kvadrillion', 'Male'], 'rub': ['rubl', 'Male'], 'kop': ['kopeyka', 'Female']}
d2_3_4 = {3: ['tysachi', 'Female'], 6: ['milliona', 'Male'], 9: ['milliarda', 'Male'], 12: ['trilliona', 'Male'], 15: ['kvadrilliona', 'Male'], 'rub': ['rublya', 'Male'], 'kop': ['kopeyki', 'Female']}
dMatch = {
	'0': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'1': d1,
	'2': d2_3_4,
	'3': d2_3_4,
	'4': d2_3_4,
	'5': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'6': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'7': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'8': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'9': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'10': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'11': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'12': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'13': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'14': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'15': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'16': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'17': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'18': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,
	'19': d0_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19,	
}

def curl(script, data):
	""" курлим с коннекта или биллинга """
	r = requests.get(config.CURL_SCRIPT[script]["url"], params=data, auth=config.CURL_SCRIPT[script]["userdata"])
	return r.text

def get_balance_info(phone):
	""" Get balance from connect API """
	result = []
	data = {
		'all_users': '1',
		'phone': "8" + phone[1:]
	}
	try:
		users = phpserialize.loads(curl('get_user', data))
	except ValueError:
		users = None
	if users:
		for uid, user in users.iteritems():
			#print user;
			res = {
				"id": user['IDUser'].encode('utf8', 'replace'),
				"balance": user['Balance'].encode('utf8', 'replace'),
				"is_locked": user['Status'] == -2,
			}

			# TODO
			# next paymant date
			#if user['Status'] == 1:
			#	date = strtotime($user['Service10000_Date']);
			#	res["paydate"] = date("Ymd", $date)."0000.00-0-000";
			#else:
			#paydate = ""			#
			# next payment summ
			#user_info =  phpserialize.loads(curl("get_user_nextpay", {"id": user['IDUser'], "get_next_pay": 1}))
			#res["paydate"] = round(user_info[0]['next_payment'])
			result.append(res)
	# Закостылим для теста
	if phone == '803':
		#for i in [[200045, 1567],[223777, -2341.23],[300000, 0],[150230, 15023007000.30]]:
		for i in [[200045, 1567]]:
			result.append({'id': str(i[0]), 'balance': str(i[1])})
	return result

def num_to_ordinalstr(num):
	""" Преобразуем число в порядковое числительное """
	dict1 = {
		1: u'первый',
		2: u'второй',
		3: u'третий',
		4: u'четвертый',
		5: u'пятый',
		6: u'шестой',
		7: u'седьмой',
		8: u'восьмой',
		9: u'девятый',
		10: u'десятый',
		11: u'одиннадцатый',
		12: u'двенадцатый',
		13: u'тринадцатый',
		14: u'четырнадцатый',
		15: u'пятнадцатый',
		16: u'шестнадцатый',
		17: u'семнадцатый',
		18: u'восемнадцатый',
		19: u'девятнадцатый',
		20: u'двадцатый',
	}
	
	if (int(num) < 21):
		return dict1[int(num)]
	else:
		return dict1[20]

def run_google_say(mode, text, fname= False):
	""" говорим номер договора или баланс через гугл
	mode = balance|account|position
	text = number (comma separated if it is balance)
	fname = имя файла в папке config.tmpSayPath, если не задано, то будет сгенерировано
	"""
	if fname:
		filename = config.tmpSayPath+fname+'.mp3'
	else:
		filename = config.tmpSayPath+mode+text+'.mp3'
	if not os.path.isfile(filename):
		if mode == 'balance':
			text = text.replace(u'.', u',')+u' руб'
		elif mode == 'position':
			text = num_to_ordinalstr(text)
		tts = gTTS(text=text, lang='ru')
		tts.save(filename)
	return 	filename

def get_num_postfix(num, pow10_or_money):
	''' Для заданного куска числа и его степени возвращается
	миллион, милллионов, тысячи, тысяч и тп
	num - число, по которому определяется склонение
	pow10_or_money - элемент элемента списка dMatch
	'''
	snum = str(num)
	inum = int(num)
	if inum > 9:
		if snum[-2:-1] == '1':
			result = dMatch[snum[-2:]][pow10_or_money][0]
		else:
			result = dMatch[snum[-1:]][pow10_or_money][0]
	else:
		result = dMatch[snum[-1:]][pow10_or_money][0]

	return result
	

def list_files_to_say_int(num, is_account=False, what_count = False):
	''' Для целого числа возвращает список файлов,
	которые надо произнести чтобы сказать это число
	is_account - если True, то говорим без тысяч и миллионов, а просто тройками
	what_count - если задано, то учитываем что говорим (рубли, копейки или другие элементы елементов массива dMatch
	'''
	result = []
	inum = abs(int(num))
	snum = str(inum)	
	# разбиваем на тройки с конца
	for i in range(0, len(snum), 3):		
		is_last_iteration = (i >= (len(snum) -3))
		subresult = []
		istripe = (inum // (10 ** i)) % (1000)
		sstripe = str(istripe)
		#print istripe
		if istripe > 0:			
			if istripe > 99:
				#print sstripe[-3:-2]
				subresult.append(sstripe[-3:-2]+'00')
			elif is_account and not is_last_iteration:
				#print istripe
				if istripe > 9:
					subresult.append('0')
				else:
					subresult.append('00')
			if istripe > 9:
				if sstripe[-2:-1] == '1':
					subresult.append(sstripe[-2:])
				else:
					if sstripe[-2:-1] != '0':
						subresult.append(sstripe[-2:-1]+'0')
					if sstripe[-1:] != '0':
						appnd = sstripe[-1:]					
						if sstripe[-1:] in ['1', '2']:
							if i > 0 and not is_account:
								appnd += dMatch[sstripe[-1:]][i][1]
							elif what_count:
								appnd += dMatch[sstripe[-1:]][what_count][1]
							else:
								appnd += 'Male'
						subresult.append(appnd)
			else:
				appnd = sstripe					
				if sstripe in ['1', '2']:
					if i > 0 and not is_account:
						appnd += dMatch[sstripe][i][1]
					elif what_count:
						appnd += dMatch[sstripe][what_count][1]
					else:
						appnd += 'Male'
				subresult.append(appnd)
			# добавляем слово - степень десятки
			if i > 0 and not is_account:
				subresult.append(get_num_postfix(istripe, i))
			result[:0] = subresult # prepend subresult to result
		elif is_account and not is_last_iteration:
			result.insert(0, '000')
		#if not is_last_iteration and result[0] != '_small_pause_':
		#	result.insert(0, '_small_pause_')

	if inum == 0:
		result.insert(0, '0')

	# добавляем что мы считаем
	if what_count:
		result.append(get_num_postfix(inum, what_count))

	if int(num) < 0:
		result.insert(0, 'minus')

	return result

def bare_num_filenames_to_pathes(flist):
	result = []
	for i in flist:
		result.append(config.numPath+i+'.wav')
	return result

def list_files_to_say_account(account):
	""" Список файлов, сгенерированных для того чтобы сказать номер договора """
	return bare_num_filenames_to_pathes(list_files_to_say_int(account, True))

def list_files_to_say_balance(balance):
	""" Список файлов, сгенерированных для того чтобы сказать баланс """
	result = []	
	lbalance = str(balance).replace(',', '.').split('.')
	if len(lbalance) > 1:
		result.extend(list_files_to_say_int(lbalance[0], False, 'rub'))
		result.extend(list_files_to_say_int(lbalance[1], False, 'kop'))
	else:
		result.extend(list_files_to_say_int(int(balance), False, 'rub'))
	return bare_num_filenames_to_pathes(result)

def list_files_to_say_position(position):
	""" Список файлов, сгенерированных для того чтобы сказать баланс """
	if int(position) > 20:
		position = '20'
	return [config.positionPath + str(position) + '.wav']
	#return [config.you, config.ordinalPath + str(position) + '.wav', config.inQueuePleaseWait]

def list_balance_files(phone):
	""" генерируем файлы и список файлов которые будут говорить баланс """
	balanceinfo = get_balance_info(phone)

	# функция включает проигрывание баланса когда изменяется значение переключателя	
	result = []

	### Составляем плэйлист
	if len(balanceinfo) == 0:
		result.append(config.phoneNotRegistered)
	elif len(balanceinfo) == 1:
		result.append(config.youAccountNumber)
		result.extend(list_files_to_say_account(balanceinfo[0]["id"]))
		result.append(config.youBalance)
		result.extend(list_files_to_say_balance(balanceinfo[0]["balance"]))
	else:
		key = 0
		result.append(config.youHaveMultipleAccounts)
		for user in balanceinfo:
			if key > 0:
				accountNumber = config.nextAccountNumber
			else:
				accountNumber = config.accountNumber			
			result.append(accountNumber)
			result.extend(list_files_to_say_account(user["id"]))
			result.append(config.balance)
			result.extend(list_files_to_say_balance(user["balance"]))
			key += 1
	
	return result

def get_liquidsoap_script(phone, socket_path, currentMusicNumber=0):
	"""
	return liquidsoap script to run radio
	======
	in liquidsoap script we use this varaiables assigment method
	iVar - interactive variable (changed via socket connection)
	sVar - source sound variable
	lVar - some local variables
	"""
	### header
	result =  """

set("log.file.path","/tmp/liquidsoap-%s.log")
set("log.level", 4)
set("server.socket",true)
set("server.socket.path","%s")
	""" % (phone, socket_path)
	
	### logic

	# list all musics
	result += """
iMusic = interactive.string("music","music%s")
	""" % currentMusicNumber
	key = 0;
	for music in config.musics:
		result += """
		sMusic%s = single("%s")
		""" % (key, music)
		key += 1

	# advices source dir
	result += """
	# By default advices randomized before play in playlist
	sFirstDaytimeAdvices = switch([
		({ 00h-10h }, playlist.once(random=false, "%(firstAdvicesMorning)s")),
		({ 10h-21h }, playlist.once(random=false, "%(firstAdvicesDay)s")),
		({ 21h-00h }, playlist.once(random=false, "%(firstAdvicesEvening)s")),
	])
	sFirstAdvices = playlist.once(random=false, "%(firstAdvices)s")
	sMiddleAdvices = playlist.once(random=true, "%(middleAdvices)s")
	sLastAdvices = playlist.once(random=false, "%(lastAdvices)s")
	sAdvices = fallback([
		sFirstAdvices,
		sFirstDaytimeAdvices,
		sMiddleAdvices,
		sLastAdvices
	])
	""" % config.advicesDir

	# balance say sequence
	#result += create_balance_files(phone)

	##### Mix all #####

	# switch music interactively
	result += """
	def crossfade(a,b)
		add(normalize=false,
		[
			sequence([ blank(duration=0.5),
			fade.initial(duration=1.,b) ]),
			fade.final(duration=1.,a)
		])
	end

	sResult = mksafe(
		switch(track_sensitive=false,
		transitions=[crossfade, crossfade, crossfade],
		[
	"""
	for key in range(0, len(config.musics)):
		result += """
				({"music%s" == iMusic()},sMusic%s),
		""" % (key, key)
	result += """
		])
	)
	"""
	
	result += """
	# delay advices
	sDelayedAdvices = delay(initial=true,20.,sAdvices)
	
	# copy of original smooth_add but fade out music before start saying
	def smooth_add_new(~delay=0.5,~p=0.2,~normal,~special)
		d = delay
		fade.final = fade.final(duration=d*2.)
		fade.initial = fade.initial(duration=d*2.)
		q = 1. - p
		c = amplify
		fallback(track_sensitive=false,
			[special,normal],
			transitions=[
				fun(normal,special)->
					add(normalize=false,
					[c(p,normal),
					c(q,fade.final(type="sin",normal)),
					sequence([blank(duration=d*2.),c(q,special)])]),
				fun(special,normal)->
					add(normalize=false,
					[c(p,normal),
					c(q,fade.initial(type="sin",normal))])
		])
	end

	# say balance or position if requested or advice if available
	sResult = smooth_add_new(delay=0.5, p=0.1, normal=sResult, special=fallback([
		merge_tracks(request.queue(id="qposition")),
		merge_tracks(request.queue(id="balance",length=200.)),
		sDelayedAdvices,		
	]))

	#sResult = normalize(gain_max=-10.,gain_min=-15.,sResult)

	##### Output wav to stdout#####
	# clock must be in sync=true so there is no output buffer
	# clock.assign_new(sync=false,[sResult])
	# flush=true makes it send data as soon as possible, not 64k every 5 sec (makes no delay before start)
	out = output.file(%wav(header=false, channels=1, samplerate=8000), "/dev/stdout", sResult, flush=true)
	"""
	return result

def get_current_music_number(phone):
	""" Обновляем в БД текущую выбраную абонентом музыку """
	config.cur.execute('SELECT music_class FROM queue_music WHERE src = %s', phone)
	res = config.cur.fetchall()
	if res:
		return int(res[0]['music_class'])
	else:
		return 0	

def update_current_music(phone, newMusicNumber):
	""" Обновляем в БД текущую выбраную абонентом музыку """
	config.cur.execute('INSERT INTO queue_music (src, music_class) values (%s, %s) ON DUPLICATE KEY UPDATE music_class = %s', (phone, newMusicNumber, newMusicNumber))
	config.con.commit();
	



