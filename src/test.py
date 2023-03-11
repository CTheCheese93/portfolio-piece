from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.options import Options

from dotenv import load_dotenv

import csv
import sqlite3
import os

load_dotenv()

### Implementation

def get_selenium_driver():
    options = Options()
    options.binary_location = r'/usr/bin/firefox'
    driver = webdriver.Firefox(executable_path=os.environ['gecko_location'], options=options)
    driver.implicitly_wait(3)
    return driver

driver = get_selenium_driver()
driver.get('https://google.com/')

print(os.environ['gecko_location'])