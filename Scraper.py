# tool to scrape work order requests from maintenance website

#from bs4 import beatifulsoup4
#import requests
from selenium import webdriver

from WebAutomation import *
from User import *
import WORequest

class Scraper:
    def __init__(self):
        self.current_user = None

        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1905, 1025) #TODO: set window size relative to monitor resolution

    # prompts user for calnet login
    def login_calnet(self):
        print('CALNET LOGIN:')
        self.current_user = User.login_prompt()

        WebAutomation.login_calnet(self.driver, self.current_user)

    # scrapes a work order request with the specified request number
    # returns a WORequest
    def scrape_request(self, request_number: int) -> WORequest:
        WebAutomation.select_request_button(self.driver)
        return WebAutomation.search_request(self.driver, request_number)
