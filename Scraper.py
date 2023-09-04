# tool to scrape work order requests from maintenance website

#from bs4 import beatifulsoup4
#import requests
from selenium import webdriver

from WebAutomation import *
from User import *

class Scraper:
    def __init__(self):
        self.current_user = None
        self.driver = webdriver.Chrome()

    # prompts user for calnet login
    def login_calnet(self):
        print('CALNET LOGIN:')
        self.current_user = User.login_prompt()

        WebAutomation.login_calnet(self.driver, self.current_user)

    # TODO: scrapes a work order request with the number [request_number]
    def scrape_request(self, request_number):
        WebAutomation.select_request_button(self.driver)
