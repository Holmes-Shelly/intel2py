#-*- coding:utf-8 -*-
import requests
import re
import json
import time

req = requests.Session()
guid_pattern = r'\w{32}\.\d{2}'
#receive new portal link
def get_updates():
	TOKEN = "33637785666:AAHRW-gz-CeKkSGbP_xKubcau0dO28ffBYc"
	url = "https://api.telegram.org/bot{}/".format(TOKEN[2:])
	cmd = requests.get(url + "getUpdates").json()["result"]

	new_guid = cmd[-1]["message"]["text"]

	if re.match(guid_pattern, new_guid):
		print 'true'
	if re.match(guid_pattern, "42d026ec3e6747f08f489a1d90623c711.16"):
		print 'false'
	
	
	# f = open('0319.txt', 'a')
	# f.write(cmd)
	# f.close
	return

get_updates()
