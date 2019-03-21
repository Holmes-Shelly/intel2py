#-*- coding:utf-8 -*-
import requests
import re
import json
import time

req = requests.Session()
add_pattern = r'\/add\s\w{32}\.\d{2}'
del_pattern = r'\/del\s\d'
cmd_pattern = r'\/.*'
#receive new portal link
def get_updates():
	TOKEN = "33637785666:AAHRW-gz-CeKkSGbP_xKubcau0dO28ffBYc"
	url = "https://api.telegram.org/bot{}/".format(TOKEN[2:])
	rece_cmd = requests.get(url + "getUpdates").json()["result"]
	
	cmd_text = rece_cmd[-1]["message"]["text"]
	cmd_time = rece_cmd[-1]["message"]["date"]

	if ((cmd_time - time.time()) < 1260) and re.match(cmd_pattern, cmd_text):
		print "This is a command."
	# if re.match(add_pattern, cmd_text):
		# print cmd_text[5:]
	
	
	# f = open('0319.txt', 'a')
	# f.write(cmd)
	# f.close
	return

get_updates()
