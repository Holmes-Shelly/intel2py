#-*- coding:utf-8 -*-
import requests
import sys
import json
import re
import time

url = 'https://www.ingress.com/intel'
req = requests.Session()

# 从本地文件中获取cookies并加入session和header中去
header_cookie = ''
with open('cookies.txt', 'r') as fp:
	intel_cookies = json.load(fp)
	for cookie in intel_cookies:
		req.cookies.set(cookie['name'],cookie['value'])
		header_cookie = header_cookie + cookie['name'] + '=' + cookie['value'] + ';'

# 从网页中获取version
content_test = req.get(url).content
version = re.findall(r'gen_dashboard_(\w*)\.js', content_test)[0]

# header和data
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
headers['cookie'] = header_cookie
for cookie in intel_cookies:
	if(cookie['name'] == 'csrftoken'):
		headers['x-csrftoken'] = cookie['value']
		break

data = {'guid': "47297cb5f5db4a12a0b91284d8f13352.16"}
data['v'] = version

portal_guid_list = [
"b7fb26b8fb7f4dce9636fdaf270c41f1.16","499dee356bab4b9dba1dfa6ae2fc6979.16","b61f808294844cf1b70d39989b263b32.16","3372f163343e4cfe99dbcad160033160.16","d69a9ae6733e4c9487808cde64564be9.16","a0a1a02678c44d26bac39bd7c97b1a10.16","ac6f5912651948038996f3e488dea71a.16","5b355df9569d42bda75a24bb53faae64.16","c6ac5bd1f7344d9fb02ae0ea180dcb4e.16","3c76246d83034a2f93d7e0dae956e451.16","01cfc7fbd3d94050ae978ded4b3b301b.16","47297cb5f5db4a12a0b91284d8f13352.16","5da3a810471f470aa4c822f45fc032fb.11","5aad6ed3536a4966b28d044769c45819.16","7ba489836ff747d8aa28f4b375b2185f.16","f73abaa7f6d8418c958892b51472edc7.16","99f2cf56f74b4f64abaa04ea55b0503b.16","145074d91d264ddc964a26128f5d509c.16","5960a0b2b5c74181885d4265cc56a1f3.16","2ba92ce1157343e78a5796a5c1679d40.16","f32499a941c246899fa76981e58a1d74.16"
]

res_power = (0, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000)
query_history = ()

# portal名字输出函数
def portal_name_output():
	f = open('prtlmsg.txt', 'a')
	for portal_index in range(len(portal_guid_list)):
		# 获取portal信息
		data['guid'] = portal_guid_list[portal_index]
		post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
		portal_detail = post_content.json()['result']
		# 规定输出格式
		f.write('[')
		f.write('{:0>2d}'.format(portal_index + 1))
		f.write(']')
		f.write(portal_detail[8].encode('utf-8'))
		f.write(' ')
		f.write(portal_link(portal_detail[2], portal_detail[3]))
		f.write('\n')
	f.close
	return

# 电量查询函数
def portal_power_query():
	global query_history
	wrong_time = 0
	portal_power_list = []
	# 对列表里的portal进行循环
	for portal_index in range(len(portal_guid_list)):
		# 获取一个的portal信息
		data['guid'] = portal_guid_list[portal_index]
		try:
			post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
			portal_detail = post_content.json()['result']
		except:
			#网络不畅，电量维持不变
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			print str(portal_index + 1), "has been ignored, maybe network wrong."
			portal_power_list.append(query_history[-1][portal_index])
			wrong_time += 1
			if(wrong_time > 10):
				send_email((),false)
			time.sleep(2)
			continue
		# 计算这个portal的电量总和
		portal_full_power = 0
		portal_decay_power = 0
		for res in portal_detail[15]:
			portal_decay_power += res[2]
			portal_full_power += res_power[res[1]]
		# 根据portal阵营输出power_percentage
		if(portal_detail[1] == "R"):
			power_percentage = round(float(portal_decay_power)/float(portal_full_power), 4)
		elif(portal_detail[1] == "N"):
			power_percentage = 0
		else:
			power_percentage = -round(float(portal_decay_power)/float(portal_full_power), 4)
		# 将每个portal的power_percentage列入电量列表
		portal_power_list.append(power_percentage)
		# 歇一歇再查询下一个portal
		time.sleep(2)
	# 信息储存
	query_history += (tuple(portal_power_list),)
	query_output()
	# 查询变化
	any_change()
	return 

# 无限循环查询电量	
def query_cycle():
	while(1):
		portal_power_query()
		time.sleep(1200)
	return

# 输出到txt
def query_output():
	f = open('prtlmsg.txt', 'a')
	f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
	f.write('\n')
	for portal_index in range(len(query_history[-1])):
		f.write('[')
		f.write('{:0>2d}'.format(portal_index + 1))
		f.write(']')
		if(query_history[-1][portal_index] > 0):
			f.write('R')
		elif(query_history[-1][portal_index] == 0):
			f.write('N')
		else:
			f.write('E')
		f.write('-')
		f.write('{:.2f}'.format(abs(query_history[-1][portal_index]) * 100))
		f.write('%')
		f.write(' ')
	f.write('\n')
	return
	
# 每次查询结束后，根据上次查询结果进行比对
def any_change():
	charged_list = []
	if(len(query_history) > 1):
		for portal_index in range(len(portal_guid_list)):
			if(abs(query_history[-1][portal_index]) > abs(query_history[-2][portal_index])):
				charged_list.append(str(portal_index + 1))	
		if(len(charged_list)):
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			print ', '.join(charged_list), "has been charged"
			send_email(tuple(charged_list),true)
		# 这个地方应该写一个变化列表，把每次循环变化的情况归类（以后量大了再加进去，自动分析判断？）
	return	

# 根据经纬度生成portal的链接
def portal_link(lat, lon):
	latitude = '{:.6f}'.format(lat / 1000000.0)
	longitude = '{:.6f}'.format(lon / 1000000.0)
	return 'https://www.ingress.com/intel?ll=' + latitude + ',' + longitude + '&z=17&pll=' + latitude + ',' + longitude

def send_email(msg_tuple, net_sign):
	# 第三方 SMTP 服务
	mail_host="smtp.163.com"  #设置服务器
	mail_user="shihao1024@163.com"   #用户名
	mail_pass="shihao1992"   #口令

	sender = 'shihao1024@163.com'
	receivers = ['shihao1024@163.com']  # 接收邮件
	message = MIMEText(','.join(msg_tuple), 'plain', 'utf-8')
	
	if(net_sign):
		subject = str(len(msg_tuple))+" portals are recharged"
	else:
		subject = "Network wrong, please check."
		
	message['Subject'] = Header(subject)
	message['From'] = "shihao<shihao1024@163.com>"
	message['To'] =  "shihao<shihao1024@163.com>"
	try:
		smtpObj = smtplib.SMTP()
		smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
		smtpObj.login(mail_user,mail_pass)
		smtpObj.sendmail(sender, receivers, message.as_string())
		print "send successfully"
	except smtplib.SMTPException:
		print "send unsuccessfully"
	return
	
# 根据guid列表输出portal名字和链接 	
portal_name_output()

# 开始查询	
query_cycle()