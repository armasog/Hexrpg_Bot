from robobrowser import RoboBrowser
import pandas as pd
import time
from random import randint
import re; re._pattern_type = re.Pattern  # Workaround for a bug in robobrowser and Python 3.7
import numpy as np

browser = RoboBrowser(history=True)
pd.set_option("display.max_columns", 101)

# Step 1: Enter Log In Details
user = 'enter your username'
password = 'enter your password'

# Step 2: Set fair price algorithm parameters
years = [18]  # Years of price history to consider. Entered as two digit integer format i.e 2018 is entered as 18
months = ['Sep', 'Oct', 'Nov']  # Months of price history to consider. Entered in 3 letter format

#Step 3: Run!

def log_in():
    global browser, user, password
    browser.open('https://www.hexrpg.com/login.php')
    forms = browser.get_forms()
    form = forms[0]
    form['username'] = user
    form['password'] = password
    browser.submit_form(form)

    return None


def place_bid(galleon, item_name):
    global browser
    browser.open('https://www.hexrpg.com/auctions')
    item_link = browser.get_link(item_name)
    browser.follow_link(item_link)
    forms = browser.get_forms()
    bid_entry = forms[0]
    bid_entry['galleon'] = str(galleon)  # Bids need to be submitted as strings
    bid_entry['sickle'] = '0'
    bid_entry['knut'] = '0'
    browser.submit_form(bid_entry)

    # TODO implement some type of feedback/log
    return None


def auction_history(item_name, month, year):
    # Gets the auction history for items currently up for auction
    # The item_name must be complete and exactly correct
    global browser
    browser.open('https://www.hexrpg.com/item_search.php?type=1&phrase=1&search=' + item_name)
    link = browser.get_link('Yes')
    browser.follow_link(link)
    html = str(browser.parsed)
    data = pd.read_html(html)[1]
    price_history = data[[5, 6]]  # Grabs final price and date
    price_history = price_history.drop(0).reset_index(drop=True)  # Removes top row with labels
    galleon_history = {}
    target_year = []
    for i in year:
        target_year.append('\'' + str(i))
    for i in range(len(price_history.index)):
        # Creates dictionary for final prices and months in the target year
        if price_history.iloc[i, 1].split(' ')[2] in target_year:
            galleon_history[int(price_history.iloc[i, 0].split('/')[0])] = price_history.iloc[i, 1].split(' ')[0]

    output = []
    for key in galleon_history:
        # Returns only the prices from the target months
        if galleon_history[key] in month:
            output.append(key)
    return output


def fair_price(item_name, month, year):
    data = auction_history(item_name, month, year)
    return [int(np.mean(data)), int(np.std(data)), int(len(data))]


def current_bid(item_name):
    # Figures out the current bid (last bid + minimum increment) by navigating to the auction page
    # This should only be used once a potential opportunity has been identified to minimize number of pings to server
    browser.open('https://www.hexrpg.com/auctions')
    item_link = browser.get_link(item_name)
    browser.follow_link(item_link)
    html = str(browser.parsed)
    bid_string = re.search('<input class="mainInput" name="galleon" size="9" type="textbox" value="[0-9]*"',
                           html).group(0)
    bid_string = bid_string.split(' ')[5]
    bid = int(bid_string.split('"')[1])

    return bid


def open_auctions():
    # Returns first page of open options as dictionary with name of the item and current price
    # This price is used to first identify the opportunity and later confirmed with current_bid to account for
    # min increment while minimizing pings to server
    browser.open('https://www.hexrpg.com/auctions')
    html = str(browser.parsed)
    auctions = pd.read_html(html)[0]
    auctions = auctions.drop([0, 1]).reset_index(drop=True)
    item_names = auctions[1].tolist()
    for i in range(len(item_names)):
        # Add 6 digit random number to item names to create unique keys when they are zipped into a dictionary
        item_names[i] = item_names[i] + str(randint(100000, 999999))
    item_prices = auctions[5].tolist()
    for i in range(len(item_prices)):
        clean_price = item_prices[i].split('/')[0]
        clean_price = clean_price.replace(',', '')
        item_prices[i] = clean_price

    open_auctions = dict(zip(item_names, item_prices))
    print(open_auctions)
    return open_auctions


def identify_opportunities(open_auctions):
    global years, months
    for item in open_auctions:
        clean_item = item[:-6]  # Removes 6 random digits from item keys used to handle duplicates
        item_no_spaces = clean_item.replace(' ', '+')  # URL convention
        try:
            fair = fair_price(item_no_spaces, months, years)
            current = int(open_auctions[item])
            if current < fair[0]:
                current_actual = current_bid(clean_item)  # Accounts for min increment
                print('{} \nCurrent Price: {} \nFair Price: {} \nStd: {} \nSample Size {}'.format(clean_item,
                                                                                                  current_actual,
                                                                                                  fair[0], fair[1],
                                                                                                  fair[2]))
                action = input('Type BID to bid or anything else to skip: ')
                if action == 'BID':
                    place_bid(current_actual + 5, clean_item)
                    print('Bid successful.')
        except ValueError:
            pass


log_in()
identify_opportunities(open_auctions())
