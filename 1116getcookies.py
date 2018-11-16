import time
import requests
from selenium import webdriver
import sys
from bs4 import BeautifulSoup
import json

# url = 'https://www.ingress.com/intel'
url = 'https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https://appengine.google.com/_ah/conflogin%3Fcontinue%3Dhttps://intel.ingress.com/intel'
driver = webdriver.Chrome()
driver.get(url)

time.sleep(40)
cookies = driver.get_cookies()

new_cookies = []
for cookie in cookies:
	if ((cookie['name'] == "SACSID") or (cookie['name'] == "csrftoken")):
		new_cookies.append(cookie)
print new_cookies
	
with open('cookies.txt', 'w') as fp:
    json.dump(new_cookies, fp)
print 'cookies documented'
