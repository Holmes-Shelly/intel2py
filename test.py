#-*- coding:utf-8 -*-
import requests
import sys
import json
import re
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header

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

portal_name_list = []


# portal名字输出函数
def portal_name_output():
	
	post_content = req.post('https://intel.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
	portal_detail = post_content.json()['result']
	portal_name_list.append(portal_detail)
	send_email((1,),1)
	return




def send_email(msg_tuple, net_sign):
	# 第三方 SMTP 服务
	mail_host="smtp.163.com"  #设置服务器
	mail_user="shihao1024@163.com"   #用户名
	mail_pass="shihao1992"   #口令

	sender = 'shihao1024@163.com'
	receivers = ['shihao1024@163.com']  # 接收邮件
	content = ''
	for index in msg_tuple:
		content = content + str(index) + ' ' + portal_name_list[index - 1][16] + ' ' + portal_name_list[index - 1][8] + '\n'
	message = MIMEText(content, 'plain', 'utf-8')
	
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
	
portal_name_output()