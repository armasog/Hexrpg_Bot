from robobrowser import RoboBrowser
import time
import re; re._pattern_type = re.Pattern  # Workaround for a bug in robobrowser and Python 3.7
from config import *

browser = RoboBrowser(history=True)

def log_in():
    global browser, user, password
    browser.open('https://www.hexrpg.com/login.php')
    forms = browser.get_forms()
    form = forms[0]
    form['username'] = user
    form['password'] = password
    browser.submit_form(form)

    return None

def buy(item):
    browser.open(item)
    forms = browser.get_forms()
    form = forms[0]
    browser.submit_form(form)

    return None

def bulk_buy(item, quantity):
    i = 1
    while i <= quantity:
        buy(item)
        if i % 3 == 0:  # Prevent pinging the server too quickly and allow the store to restock
            time.sleep(2)
            browser.open('https://www.hexrpg.com')
        i += 1

log_in()
bulk_buy()