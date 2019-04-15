#-*- coding:utf-8 -*-
import requests
import sys
import json
import re
import time
import numpy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def query_initialize():
	#delete all contents in list
	for power_index in range(len(portal_name_list)):
		portal_name_list.pop(-1)
		portal_power_list.pop(-1)
	
	for portal_index in range(len(portal_guid_list)):
		data['guid'] = portal_guid_list[portal_index]
		post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
		portal_detail = post_content.json()['result']
		
		#fill up the list again
		portal_name_list.append(portal_detail)	
		portal_power_list.append(get_power(tuple(portal_detail)))
		time.sleep(2)
	
	send_tg(tuple(range(len(portal_guid_list)+1)[1:]), 'portal list update:')
	return

def save_guid():
	numpy.save('guid_list.npy', portal_guid_list)
	return
	
#update portal list
def portal_list_add(new_guid):
	#find new portal in getentity, and attach it to portal_guid_list
	if new_guid not in portal_guid_list:
		portal_guid_list.append(new_guid)
		save_guid()
		query_initialize()
	return

def portal_list_del(portal_index):
	portal_guid_list.pop(portal_index-1)
	save_guid()
	portal_name_list.pop(portal_index-1)
	portal_power_list.pop(portal_index-1)
	return

def get_power(portal_detail):
	portal_full_power = 0
	portal_decay_power = 0

	for res in portal_detail[15]:
		portal_decay_power += res[2]
		portal_full_power += res_power[res[1]]

	if(portal_detail[1] == "R"):
		power_percentage = round(float(portal_decay_power)/float(portal_full_power), 4)
	elif(portal_detail[1] == "N"):
		power_percentage = 0
	else:
		power_percentage = -round(float(portal_decay_power)/float(portal_full_power), 4)

	return power_percentage
	
#receive new portal link
def get_updates():
	global last_id
	try:
		rece_cmd = requests.get(url_tg + "getUpdates").json()["result"]
	except:
		send_tg((),'Update failed, please try it later.')
		return
		
	#non text message
	if not("text" in rece_cmd[-1]["message"]):
		return
	
	cmd_text = rece_cmd[-1]["message"]["text"]
	cmd_id = rece_cmd[-1]["message"]["message_id"]
		
	if((re.match(cmd_pattern, cmd_text)) and (cmd_id != last_id)):
		last_id = cmd_id
		if re.match(add_pattern, cmd_text):
			send_tg((), 'Congratulations, your portal has been accepted.')
			portal_list_add(cmd_text[5:])
		elif re.match(del_pattern, cmd_text):
			send_tg((int(cmd_text[5:]), ), 'Congratulations, this portal has been deleted:')
			portal_list_del(int(cmd_text[5:]))
		elif re.match(help_pattern, cmd_text):
			send_tg((), "I'm your father.")
		elif re.match(att_pattern, cmd_text):
			send_tg((), "Maybe I'm not SelfHelp's father, but I still love her.@selfhelp233")
		else:
			send_tg((), 'Sorry, your application has been rejected.')
	return
	
# power query
def portal_power_query():
	wrong_time = 0
	portal_power_list_new = []
	for portal_index in range(len(portal_guid_list)):
		data['guid'] = portal_guid_list[portal_index]
		try:
			post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
			portal_detail = post_content.json()['result']
		except Exception, e:
			#cookies maybe expired, let the data remain unchanged
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), str(portal_index + 1), "has been ignored, ", Exception, e
			portal_power_list_new.append(portal_power_list[portal_index])
			wrong_time += 1
			if(wrong_time > 2):
				get_cookies()
			time.sleep(2)
			continue
			
		portal_power_list_new.append(get_power(tuple(portal_detail)))
		time.sleep(2)

	any_change(tuple(portal_power_list_new))
	return 
	
# find power changes
def any_change(portal_power_list_new):
	charged_list = []
	change_find = 0
	
	for portal_index in range(len(portal_guid_list)):
		if(abs(portal_power_list_new[portal_index]) > abs(portal_power_list[portal_index])):
			charged_list.append(portal_index + 1)
		if((portal_power_list_new[portal_index] * portal_power_list[portal_index]) < 0):
			change_find = 1
			send_tg((portal_index + 1,), 'This portal has been attacked:')
		if (portal_power_list_new[portal_index] == 0) and (portal_power_list[portal_index] != 0):
			change_find = 1
			send_tg((portal_index + 1,), 'This portal has been neutralized:')
	
	if(len(charged_list)):
		print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), charged_list, "has been charged"
		send_tg(tuple(charged_list),'Portals charged:')
	
	if(change_find):
		query_initialize()
	
	#just like "last_tuple = this_tuple"
	for power_index in range(len(portal_power_list)):
		portal_power_list[power_index] = portal_power_list_new[power_index]

	return	

def get_cookies():
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--no-sandbox') 
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
		
	driver = webdriver.Chrome(options=chrome_options)
	driver.get(url_login)
	
	#get the username textbox
	login_field = driver.find_element_by_id("Email")
	login_button = driver.find_element_by_id('next')

	login_field.clear()
	login_field.send_keys(u'ingress6526')
	login_button.click()
	# print "Email sended"
	time.sleep(2)
	
	#get the password textbox
	password_field = driver.find_element_by_id("Passwd")
	password_button = driver.find_element_by_id("signIn")

	password_field.send_keys(u'shihao1992!G')
	password_button.send_keys(Keys.ENTER)
	# print "password sended"
	time.sleep(10)
	
	cookies = driver.get_cookies()
	driver.quit()
	# print "cookies got"
	
	headers['cookie'] = ''
	for cookie in cookies:
		if ((cookie['name'] == "SACSID") or (cookie['name'] == "csrftoken")):
			req.cookies.set(cookie['name'],cookie['value'])
			headers['cookie'] = headers['cookie'] + cookie['name'] + '=' + cookie['value'] + ';'
			if(cookie['name'] == 'csrftoken'):
				headers['x-csrftoken'] = cookie['value']
				print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), "csrftoken:", cookie['value']

	data['v'] = re.findall(r'gen_dashboard_(\w*)\.js', req.get(url).content)[0]# get version
	
	send_tg((), "Cookies updated.")
	return
	
def send_tg(portal_tuple, attention):
	content = ''
	for index in portal_tuple:
		content = content + str(index) + '. ' + portal_name_list[index - 1][1] + ' ' + portal_name_list[index - 1][16] + ' ' + portal_name_list[index - 1][8] + ' ' + '\n'
	try:
		if(len(attention)):
			requests.get(url_tg + "sendMessage?chat_id=-393700256&text={}".format(attention))
		requests.get(url_tg + "sendMessage?chat_id=-393700256&text={}".format(content.encode('utf-8')))
	except:
		print "send unsuccessfully"
	return

def query_cycle():
	cycle_time = 1
	begin_time = time.time()
	while(1):
		get_updates()
		time.sleep(6)
		if((((time.time() - begin_time)) / 1200) > cycle_time):
			portal_power_query()
			cycle_time += 1
			if not (cycle_time % 3):
				print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), cycle_time, "times finished."
		
	
	return

req = requests.Session()	
url = 'https://www.ingress.com/intel'
url_login = 'https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps://intel.ingress.com/intel'

cmd_pattern = r'\/.*'
help_pattern = r'\/help'
add_pattern = r'\/add\s\w{32}\.\d{2}'
del_pattern = r'\/del\s\d'
att_pattern = r'\/attack'

TOKEN = "33637785666:AAHRW-gz-CeKkSGbP_xKubcau0dO28ffBYc"
url_tg = "https://api.telegram.org/bot{}/".format(TOKEN[2:])
last_id = 0

headers = {
	'accept':'application/json, text/javascript, */*; q=0.01',
	'accept-encoding':'gzip, deflate, br',
	'accept-language':'en,zh;q=0.9,zh-CN;q=0.8,lb;q=0.7',
	'content-length':'93',
	'content-type':'application/json; charset=UTF-8',
	'origin':'https://intel.ingress.com',
	'referer':'https://intel.ingress.com/intel',
	'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
	'x-requested-with':'XMLHttpRequest',
	}
data = {}
get_cookies()

res_power = (0, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000)
portal_name_list = []
portal_power_list = []
# portal list initialize 
portal_guid_list = numpy.load('guid_list.npy').tolist()
#update portal_name_list and portal_power_list
query_initialize()

# begin the cycle		
query_cycle()
# portal_power_query()
