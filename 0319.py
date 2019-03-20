#-*- coding:utf-8 -*-
import requests
import sys
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url = 'https://www.ingress.com/intel'
url_login = 'https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps://intel.ingress.com/intel'
guid_pattern = r'\w{32}\.\d{2}'
TOKEN = "33637785666:AAHRW-gz-CeKkSGbP_xKubcau0dO28ffBYc"
url_tg = "https://api.telegram.org/bot{}/".format(TOKEN[2:])
req = requests.Session()

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

# "d7ef946e2a874f9cb6c95b6121d20a4b.16","7d445f84239d48a786eaf7a6b0868232.16"
portal_guid_list = [
"d7ef946e2a874f9cb6c95b6121d20a4b.16","01cf9462bb224b6997cd11d8fd99b4ab.16","e9f89a6608a646aab112cfd3cb63cd17.16","7d445f84239d48a786eaf7a6b0868232.16","8c439807c2fc41b3a7e89df60b6617c7.16","9b262cc432a24ab3aaf076c0e20d4014.16","c0a27a1badee4fdc94bd1180776e945d.16","7ef47a0afc904b43a7f6c71062f0dae4.16","6729c68ebaee40c78af4c1481ec46016.16","499dee356bab4b9dba1dfa6ae2fc6979.16","b61f808294844cf1b70d39989b263b32.16","d69a9ae6733e4c9487808cde64564be9.16","5b355df9569d42bda75a24bb53faae64.16","c6ac5bd1f7344d9fb02ae0ea180dcb4e.16","3c76246d83034a2f93d7e0dae956e451.16","99f2cf56f74b4f64abaa04ea55b0503b.16","c20365d801534dbc8ca53734d79e85a4.16","ee11c1511d004f4ebcee1c5e314079f3.16","ca09681350fb46509c59a8b7268a5ab3.16","42d026ec3e6747f08f489a1d90623c71.16",
]
portal_name_list = []

res_power = (0, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000)
last_query = ()

#update portals' details
def query_initialize():
	global last_query, portal_name_list
	portal_name_list = []
	portal_power_list = []
	for portal_index in range(len(portal_guid_list)):
		data['guid'] = portal_guid_list[portal_index]
		post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
		portal_detail = post_content.json()['result']
		portal_name_list.append(portal_detail)
		
		#last_query initialize
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
			
		portal_power_list.append(power_percentage)
		time.sleep(2)
	
	last_query = tuple(portal_power_list)
	
	send_tg(tuple(range(len(portal_guid_list)+1)[1:]), 'portal list update:')
	return

#update portal list
def portal_list_update(new_guid):
	#find new portal in getentity, and attach it to portal_guid_list
	#add and delete
	if new_guid not in portal_guid_list:
		portal_guid_list.append(new_guid)
		send_tg((), 'Congratulations, your portal has been accepted.')
		query_initialize()
	return

#receive new portal link
def get_updates():
	try:
		cmd = requests.get(url_tg + "getUpdates").content
	except:
		tg_send((),'update failed, please try again.')
	# print json.loads(cmd)["result"][-1]["message"]["date"] - time.time()
	if((json.loads(cmd)["result"][-1]["message"]["date"] - time.time()) < 1260):
		new_guid = json.loads(cmd)["result"][-1]["message"]["text"]
		if re.match(guid_pattern, new_guid):
			portal_list_update(new_guid)
	return
	
# power query
def portal_power_query():
	wrong_time = 0
	portal_power_list = []
	for portal_index in range(len(portal_guid_list)):
		data['guid'] = portal_guid_list[portal_index]
		try:
			post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
			portal_detail = post_content.json()['result']
		except Exception, e:
			#cookies maybe expired, let the data remain unchanged
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), str(portal_index + 1), "has been ignored, ", Exception, e
			portal_power_list.append(last_query[portal_index])
			wrong_time += 1
			if(wrong_time > 2):
				get_cookies()
			time.sleep(2)
			continue

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
			
		portal_power_list.append(power_percentage)
		time.sleep(2)

	any_change(tuple(portal_power_list))
	return 
	
# find power changes
def any_change(this_query):
	global last_query
	charged_list = []
	neutral_find = 0
	
	for portal_index in range(len(portal_guid_list)):
		if(abs(this_query[portal_index]) > abs(last_query[portal_index])):
			charged_list.append(portal_index + 1)
		if not((this_query[portal_index] * last_query[portal_index]) > 0):
			neutral_find = 1
			send_tg((portal_index + 1,), 'This portal has been neutralized:')

	if(neutral_find):
		query_initialize() #update portal details
	
	#send changes
	if(len(charged_list)):
		last_query = this_query
		print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), charged_list, "has been charged"
		send_tg(tuple(charged_list),'Portals charged:')
	# data analyze, later work
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
	cycle_time = 0
	while(1):
		time.sleep(1200)
		portal_power_query()
		cycle_time += 1
		if not (cycle_time % 3):
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), cycle_time, "times finished."
		get_updates()
	
	return
	
get_cookies()
	
# portal list initialize 	
query_initialize()

# begin the cycle		
query_cycle()
