from selenium import webdriver
from selenium.common import exceptions as seleex
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from random import randint
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pickle as pk
import random, string
import pyperclip
import csv
import sys

url = "https://presearch.org/"
refUrl = 'https://presearch.org/signup?rid=1602392'
search_xpath = '//*[@id="search"]'
search_click_xpath = '//*[@id="search-input"]/div/span/button'
sign_up_click_xpath = '//*[@id="main"]/div[1]/div[2]/div/a[1]'
project_path = '/home/sam/Documents/Portfolios/preGenerator'
chromedriver_path = project_path+'/browser/chromedriver'
presearch_cookie = 'presearch_session'
pre_accounts_file = "pre_accounts.csv"
pre_accounts_log_file = "log"
pre_reg_accounts_file = "pre_reg_accounts.csv"
dict_file = "dict"

class CsvReader:
    def __init__(self):
        pass

    def get_accounts(self):
        accounts = []

        with open(pre_accounts_file, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                accounts.append(row)
        
        return accounts
    
    def get_unregistered_accounts(self):
        accounts = []

        with open(pre_reg_accounts_file, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                accounts.append(row[0])
        
        return accounts

    def get_dictionary(self):
        dictionary = []

        with open(dict_file, 'r', encoding="ISO-8859-1") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                dictionary.append(row[0])
        
        return dictionary

class CsvWriter:
    def __init__(self):
        pass

    def remove_first_row(self, filename = pre_reg_accounts_file):
        with open(filename,'r') as f:
            with open(filename,'w') as f1:
                next(f)
                for line in f:
                    f1.write(line)

    def add_registered_account(self, csv_row : list, filename = pre_reg_accounts_file):
        strings = ",".join(csv_row)
        with open(filename, 'a') as fd:
            fd.write(strings+'\n')

class Logger:
    def __init__(self):
        self._csv_reader = CsvReader()
        self._csv_writer = CsvWriter()
    
    def write_log(self):
        pass

class IdGenerator:
    def __init__(self):
        pass

    def generate_id(self, size=6, chars = string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

class CookiesManager:
    def get_pickle(self):
        raise NotImplementedError

class CookiesSaver(CookiesManager):
    def __init__(self):
        self.pickle = pk

    def get_pickle(self):
        return self.pickle
    
    def save_cookies(self, cookies, cookiesname):
        self.pickle.dump(cookies, open(cookiesname, "wb"))
    
class CookiesLoader(CookiesManager):
    def __init__(self):
        self.pickle = pk

    def get_pickle(self):
        return self.pickle
    
    def load_cookies(self, cookiesname):
        return self.pickle.load(open(cookiesname, "rb"))

class WebBrowser:
    def __init__(self):
        pass

    def get_driver(self, account : str):    
        chrome_options = self.get_options(account)
        driver = webdriver.Chrome(chromedriver_path, options=chrome_options)
        return driver
    
    def get_options(self, account, headless = False):
        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={account}")
        if headless:
            chrome_options.add_argument('headless')     
        return chrome_options

class AccountMaker:
    def __init__(self):
        self._csv_reader = CsvReader()
        self._csv_writer = CsvWriter()
        self._unregistered_accounts = self._csv_reader.get_unregistered_accounts()
        self._accounts = self._csv_reader.get_accounts()
        self._driver = WebBrowser()
    
    def register_accounts(self):
        for account in self._unregistered_accounts:
            self.register_account(account)
        
        print("Done registering All Account")

    def register_account(self, account : str):
        print(f"Currently Registering : {account}")
        driver = self._driver.get_driver(account)
        driver.get(refUrl)
        print("Acount Email Copied to clipboard!")
        pyperclip.copy(account)
        self.click_sign_up(driver)
        # self.add_registered_account(account)

    def do_login(self, driver):
        print("Not logged in! Please log in with current email provided Above! (MAX : 120 seconds)")
        self.wait_until_register_complete(driver)
    
    def wait_until_register_complete(self, driver):
        wait = WebDriverWait(driver, 120)
        wait.until(lambda driver: driver.current_url == url)
    
    def add_registered_account(self, account : str):
        self._csv_writer.add_registered_account(account)
        self._csv_writer.remove_first_row()

    def click_sign_up(self, driver):
        try:
            elem = driver.find_element_by_xpath(sign_up_click_xpath)
            elem.click()
            self.do_login(driver)
        except Exception as e:
            print(f"Error has occured : \n {e}")

    
class AutoSearcher:
    def __init__(self):
        self.words = CsvReader().get_dictionary()
        self._accounts = CsvReader().get_accounts()
        self._dict_length = len(self.words)
        self._csv_writer = CsvWriter()
        self._driver = WebBrowser()

    def do_login(self):
        print("Not logged in! Please log in with current email provided Above! (MAX : 120 seconds)")
        sleep(120)

    def _input_element(self, keyword : str, driver):
        try:
            elem = driver.find_element_by_xpath(search_xpath)
            elem.send_keys(self.words[randint(0, self._dict_length)])
            elem = driver.find_element_by_xpath(search_click_xpath)
            elem.click()
        except seleex.ElementClickInterceptedException as e:
            self.do_login()
        except Exception as e:
            print(f"Error has occured : \n {e}")

    def _get_token_ammount(self):
        pass

    def do_accounts_search(self):
        for account in self._accounts:
            self.do_search(account[0])
        print("Done")

    def put_done_search_account_to_the_last(self, account):
        self._csv_writer.add_registered_account(account, pre_accounts_file)
        self._csv_writer.remove_first_row(pre_accounts_file)

    def do_search(self, account : str = None):        
        if account is None:
            account = self._accounts[0][0]
        
        print(f"Current Account : {account}")
        
        driver = self._driver.get_driver(account)

        number_of_search = self.get_rand_time(16, 18)

        for i in range(0,number_of_search):
            driver.get(url)
            self._input_element(search_xpath, driver)
            print(f"Search Loop through : {account} {i+1} times")
            sleep(self.get_rand_time(10, 30))

        sleep(self.get_rand_time(20, 40))
        print(f"Done Searching on : {account}")

        # self.put_done_search_account_to_the_last(account)

        driver.close()
    
    def get_rand_time(self, min_time : int = 0, max_time : int = 60):
        return randint(min_time, max_time)

class AccountSyncer:
    def __init__(self):
        self.words = CsvReader().get_dictionary()
        self._accounts = CsvReader().get_accounts()
        self._csv_writer = CsvWriter()
        self._driver = WebBrowser()
    
    def sync_accounts(self):
        pass

    def sync_account(self, account : str):
        pass

def startBot(argument : str = 'search'):
    if argument == "search":
        autoSearcher = AutoSearcher()
        autoSearcher.do_accounts_search()
    elif argument == "sync":
        pass
    elif argument == "register":
        autoReg = AccountMaker()
        autoReg.register_accounts()
    else:
        print("Wrong Command")

argument = sys.argv[1]

startBot(argument)