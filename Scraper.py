# tool to scrape work order requests from maintenance website

#from bs4 import beatifulsoup4
#import requests
from selenium import webdriver

from WebAutomation import *
from User import *
from WORequest import *

class Scraper:
    def __init__(self, headless=True):
        self.current_user = None

        self.options = webdriver.ChromeOptions()
        self.options.headless = headless
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_window_size(1905, 1025) #TODO: set window size relative to monitor resolution

    # prompts user for calnet login
    # TODO: if duo login times out, script crashes - add try statement and/or loop
    # TODO: account for incorrect login info - loop
    def login_calnet(self):
        print('CALNET LOGIN:')
        self.current_user = User.login_prompt()

        WebAutomation.login_calnet(self.driver, self.current_user)

    # scrapes a work order request with the specified request number
    # returns a WORequest
    def scrape_request(self, request_number: int) -> WORequest:
        WebAutomation.select_request_button(self.driver)
        try:
            return WebAutomation.search_request(self.driver, request_number)
        except:
            print(f"failed to retrieve request #{request_number}")
            return WORequest(request_number)

    # TODO: finds the maintenance request with the lowest ID value
    def find_start(self):
        return None

    # TODO: finds the maintenance request with the highest ID value
    def find_end(self):
        return None
