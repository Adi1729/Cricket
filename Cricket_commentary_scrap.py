''' Uses Selenium to interact with Firefox .
Challenge : Link used does not load all html at once. It needs to be scrolled down. Selenium makes it easier.'''


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

#launch url
url = r'http://www.espncricinfo.com/series/19185/commentary/1179274?innings=1'

driver = webdriver.Firefox()
driver.implicitly_wait(30)
driver.get(url)

python_button = driver.find_element_by_class_name('body') #FHSU
python_button.click() #click fhsu link

for i in range(14):
    
    python_button = driver.find_element_by_tag_name("body")
    python_button.send_keys(Keys.PAGE_DOWN)
    time.sleep(3)
    soup_level1=BeautifulSoup(driver.page_source, 'lxml')
    a_container = soup_level1.find_all('div',{'class':'commentary-item'})
    
match = []
idx =1

for idx,comm in enumerate(a_container):
    temp_data = OrderedDict()        
    try:
        temp_data['over_comp'] =a_container[idx].find('div',{'class':'over'}).text
        temp_data['over'] =a_container[idx].find('div',{'class':'time-stamp'}).text
        temp_data['comm'] = a_container[idx].find('div',{'class':'description'}).text
        
        match.append(temp_data)
        
    except:
        print(idx)
        pass
    
df = pd.DataFrame(match)

import re

df['over_act'] = df['over'].apply(lambda x: re.findall('\d+\.\d',x)[0]) 
df['over_act'] = df['over'].apply(lambda x: re.findall('^\d',x)) 
df['action'] = df['over_comp'].apply(lambda x:re.findall('[a-zA-Z]+',x)[0] if(re.findall('[a-zA-Z]+',x)) else None)
     
print(driver.title)
driver.quit()
