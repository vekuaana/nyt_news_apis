# coding:utf-8

import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


if __name__ == "__main__":

    url = "https://www.nytimes.com/2024/04/30/us/police-shooting-charlotte-what-happened.html"
    clean_url = re.sub(r'https://www.nytimes.com(.*$)', 'https://www-nytimes-com.translate.goog\\1', url)
    trans_url = clean_url + "?_x_tr_sl=es&_x_tr_tl=en&_x_tr_hl=fr&_x_tr_pto=wapp"
    driver = webdriver.Chrome()
    driver.get(trans_url)
    time.sleep(3)
    elements = driver.find_elements(By.TAG_NAME, 'p')
    with open("webscrappingexample.txt", 'w', encoding='utf-8') as f:
        for e in elements:
            f.write(e.text + '\n')
