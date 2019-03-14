from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
url_login = 'https://accounts.google.com/'
chrome_options = webdriver.ChromeOptions()
# chrome_options.set_headless()
chrome_options.add_argument('--no-sandbox') 
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
	
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
driver.get(url_login)

#get the username textbox
login_field = driver.find_element_by_id("Email")
login_button = driver.find_element_by_id('next')

login_field.clear()
login_field.send_keys(u'ingress6526')
login_button.click()
print "email sended"
time.sleep(2)

#get the password textbox
password_field = driver.find_element_by_id("Passwd")
password_button = driver.find_element_by_id("signIn")

password_field.send_keys(u'shihao1992!G')
# password_button.click
password_button.send_keys(Keys.ENTER)
# js = 'document.getElementById("signIn").click();'
# driver.execute_script(js)
print "password sended"
time.sleep(10)
f = open('0314.html', 'w')
f.write(driver.page_source.encode('utf-8'))
f.close
cookies = driver.get_cookies()
print "cookies got"

for cookie in cookies:
	if ((cookie['name'] == "SACSID") or (cookie['name'] == "csrftoken")):
		print cookie['value']
		


driver.quit()
	
	