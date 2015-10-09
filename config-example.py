#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

socketPath = "/var/run/asterisk/"

# backgroun music
musicPath = "/usr/scripts/asterisk-moh/music/background/"
musics = [
	musicPath + "dj_street_style_vanessa_mae_eiforia_full_version.wav",
	musicPath + "nickelback_far_Away.wav",
	musicPath + "poets_of_the_fall_brighter_than_the_sun_jealous_gods_2014.wav",
	musicPath + "vanessa_mae_step_up.wav",
	musicPath + "Akh-Point_-_2_-_Foundin__Faith.wav",
	musicPath + "Dzynek_-_Accelerate.wav",
	musicPath + "The.madpix.project_-_Wish_You_Were_Here.wav",
]

# phrases
phrasesPath = "/usr/scripts/asterisk-moh/music/phrases/"
phoneNotRegistered = phrasesPath + "phoneNotRegistered.wav"
youHaveMultipleAccounts = phrasesPath + "youHaveMultipleAccounts.wav"
youAccountNumber = phrasesPath + "youAccountNumber.wav"
accountNumber = phrasesPath + "accountNumber.wav"
nextAccountNumber = phrasesPath + "nextAccountNumber.wav"
youBalance = phrasesPath + "youBalance.wav"
balance = phrasesPath + "balance.wav"
#you = phrasesPath + "you.wav"
#inQueuePleaseWait = phrasesPath + "inQueuePleaseWait.wav"

# advices folders
advicesDir = {
	"firstAdvicesMorning": "/usr/scripts/asterisk-moh/music/advices/firstMorning/",
	"firstAdvicesDay": "/usr/scripts/asterisk-moh/music/advices/firstDay/",
	"firstAdvicesEvening": "/usr/scripts/asterisk-moh/music/advices/firstEvening/",
	"firstAdvices": "/usr/scripts/asterisk-moh/music/advices/first/",
	"middleAdvices": "/usr/scripts/asterisk-moh/music/advices/middle/",
	"lastAdvices": "/usr/scripts/asterisk-moh/music/advices/last/",
}

# dir with position sounds
positionPath = "/usr/scripts/asterisk-moh/music/position/"

# dir for money and number saying
numPath = "/usr/scripts/asterisk-moh/music/num/"

# path where to place google said phrases
tmpSayPath = "/usr/scripts/asterisk-moh/music/num/"

# delay after DTMF press before handle next DTMF
# it's to prevent DTMF DDoS atack:)
digitPressDelay = {
	'2': 15,
	'3': 3,
	'4': 8,
}

# web api configuration
CURL_SCRIPT = {
	# to retrive current balance
        "get_user": {
                "url": "http://billing.example/get_user",
                "userdata": ("user", "pass")
        },
	# to retrive data how much user should pay next time
        'get_user_nextpay': {
                "url" : "http://billing.example/get_users_nextpay",
                "userdata": ("user", "pass")
        }
}

# DB connect to asterisk database
# to save and get music that was choosen by user last time
con = MySQLdb.connect(host='127.0.0.1',user="moh_advenced",passwd="pass",db="asterisk",use_unicode=True, charset='utf8')
cur = con.cursor(MySQLdb.cursors.DictCursor)

