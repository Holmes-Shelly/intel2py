#-*- coding:utf-8 -*-
import requests
import sys
import json
import re
import time
from selenium import webdriver

url = 'https://www.ingress.com/intel'
url_login = 'https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps://intel.ingress.com/intel'
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

portal_guid_list = [
"d7ef946e2a874f9cb6c95b6121d20a4b.16","7d445f84239d48a786eaf7a6b0868232.16"
# "d7ef946e2a874f9cb6c95b6121d20a4b.16","01cf9462bb224b6997cd11d8fd99b4ab.16","e9f89a6608a646aab112cfd3cb63cd17.16","7d445f84239d48a786eaf7a6b0868232.16","8c439807c2fc41b3a7e89df60b6617c7.16","9b262cc432a24ab3aaf076c0e20d4014.16","c0a27a1badee4fdc94bd1180776e945d.16","7ef47a0afc904b43a7f6c71062f0dae4.16","6729c68ebaee40c78af4c1481ec46016.16", "499dee356bab4b9dba1dfa6ae2fc6979.16","b61f808294844cf1b70d39989b263b32.16","d69a9ae6733e4c9487808cde64564be9.16","a0a1a02678c44d26bac39bd7c97b1a10.16","5b355df9569d42bda75a24bb53faae64.16","c6ac5bd1f7344d9fb02ae0ea180dcb4e.16","3c76246d83034a2f93d7e0dae956e451.16","5aad6ed3536a4966b28d044769c45819.16","99f2cf56f74b4f64abaa04ea55b0503b.16",
]
portal_name_list = []

res_power = (0, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000)
query_history = ()

# portal名字输出函数
def portal_name_output():
	for portal_index in range(len(portal_guid_list)):
		data['guid'] = portal_guid_list[portal_index]
		post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
		portal_detail = post_content.json()['result']
		portal_name_list.append(portal_detail)
		time.sleep(2)
	return

# 电量查询函数
def portal_power_query():
	global query_history
	wrong_time = 0
	portal_power_list = []

	for portal_index in range(len(portal_guid_list)):
		data['guid'] = portal_guid_list[portal_index]
		try:
			post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
			portal_detail = post_content.json()['result']
		except Exception, e:
			#网络不畅，电量维持不变
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), str(portal_index + 1), "has been ignored, ", Exception, e
			portal_power_list.append(query_history[-1][portal_index])
			wrong_time += 1
			if(wrong_time > len(portal_guid_list)-1):
				send_tg((),0)
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
		
	query_history += (tuple(portal_power_list),)
	any_change()
	return 
	
# 每次查询结束后，根据上次查询结果进行比对
def any_change():
	charged_list = []
	if(len(query_history) > 1):
		for portal_index in range(len(portal_guid_list)):
			if(abs(query_history[-1][portal_index]) > abs(query_history[-2][portal_index])):
				charged_list.append(portal_index + 1)
		if(len(charged_list)):
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), charged_list, "has been charged"
			send_tg(tuple(charged_list),1)
		# 这个地方应该写一个变化列表，把每次循环变化的情况归类（以后量大了再加进去，自动分析判断？）
	return	

def get_cookies():
	chrome_options = webdriver.ChromeOptions()
	chrome_options.set_headless()
	chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors. 
	driver = webdriver.Chrome(chrome_options=chrome_options)
	# options.add_argument('-headless')
	# chrome_options.add_argument('--headless')
	# chrome_options.add_argument('--disable-gpu')
		
	# driver = webdriver.Chrome(chrome_options=chrome_options)
	# driver = webdriver.Chrome()
	driver.get(url_login)
	
	#get the username textbox
	login_field = driver.find_element_by_id("identifierId")
	login_button = driver.find_element_by_id('identifierNext')

	login_field.clear()
	login_field.send_keys(u'ingress6526')
	login_button.click()
	time.sleep(2)

	#get the password textbox
	password_field = driver.find_element_by_name("password")
	password_button = driver.find_element_by_id("passwordNext")

	password_field.send_keys(u'shihao1992!G')
	password_button.click()
	time.sleep(10)
	
	cookies = driver.get_cookies()
	driver.quit()
	headers['cookie'] = ''
	for cookie in cookies:
		if ((cookie['name'] == "SACSID") or (cookie['name'] == "csrftoken")):
			req.cookies.set(cookie['name'],cookie['value'])
			headers['cookie'] = headers['cookie'] + cookie['name'] + '=' + cookie['value'] + ';'
			if(cookie['name'] == 'csrftoken'):
				headers['x-csrftoken'] = cookie['value']
	data['v'] = re.findall(r'gen_dashboard_(\w*)\.js', req.get(url).content)[0]# 获取version
	return
	
def send_tg(msg_tuple, net_sign):
	TOKEN = "637785666:AAHRW-gz-CeKkSGbP_xKubcau0dO28ffBYc"
	url = "https://api.telegram.org/bot{}/".format(TOKEN)
	content = ''
	for index in msg_tuple:
		content = content + str(index) + '. ' + portal_name_list[index - 1][16] + ' ' + portal_name_list[index - 1][8] + '\n'

	if not (net_sign):
		requests.get(url + "sendMessage?chat_id=-1001366507371&text={}".format("Network wrong, please check."))
	else:
		try:
			requests.get(url + "sendMessage?chat_id=-1001366507371&text={}".format(content.encode('utf-8')))
			print "send successfully"
		except:
			print "send unsuccessfully"
	return

# 无限循环查询电量	
def query_cycle():
	cycle_time = 0
	while(1):
		portal_power_query()
		cycle_time += 1
		print cycle_time
		time.sleep(10)
	return
	
# 浏览器初始化
get_cookies()
	
# 根据guid列表输出portal名字和链接 	
portal_name_output()

# 开始查询	
query_cycle()
