from robobrowser import RoboBrowser
import pandas as pd
import time
import re; re._pattern_type = re.Pattern  # Workaround for a bug in robobrowser and Python 3.7
from config import *

browser = RoboBrowser(history=True)
bets = []  # Log of bet results to be exported to csv


def log_in():
    global browser, user, password
    browser.open('https://www.hexrpg.com/login.php')
    forms = browser.get_forms()
    form = forms[0]
    form['username'] = user
    form['password'] = password
    browser.submit_form(form)

    return None


def place_bet(bet, bet_type):
    global browser
    browser.open(bet_type)
    forms = browser.get_forms()
    form = forms[0]
    form['galleon'] = str(bet)
    browser.submit_form(form)

    confirmation_form = browser.get_forms()
    confirmation_button = confirmation_form[0]
    browser.submit_form(confirmation_button)

    return None


def galleons_on_hand():
    browser.open('https://www.hexrpg.com')  # Refresh the page before calculating to avoid errors
    html = str(browser.parsed)
    raw_galleons = re.search('<font color="#FFCC00" size="2">[0-9,]*', html).group(0)
    galleons = raw_galleons[31:]  # Select only the numeric portion of the regex
    galleons = int(galleons.replace(',', ''))

    return galleons


def evaluate_bet(bet):
    global results, bets
    starting_galleons = galleons_on_hand()
    time.sleep(300)
    ending_galleons = galleons_on_hand()
    outcome = - bet + (ending_galleons - starting_galleons)
    bets.append(outcome)
    log_bet()


    return outcome


def log_bet():
    global bets
    log = pd.DataFrame(data=bets, columns=['result'])
    log.to_csv('results.csv')


def strategy(amt, iterations=1):
    i = 1
    while i <= iterations:
        place_bet(amt, circle_bet)
        place_bet(amt * 2, color_bet)
        evaluate_bet(amt * 3)
        i += 1


log_in()
strategy(50, iterations=2)
