# tool to scrape work order requests from maintenance website

from Log import *
from selenium import webdriver
from WebAutomation import *
from User import *
from WORequest import *


class Scraper:
    def __init__(self, headless: bool = True):
        self.current_user = None

        self.options = webdriver.ChromeOptions()
        self.options.headless = headless
        self.driver = webdriver.Chrome(options=self.options)
        if not headless:
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
    def scrape_request(self, request_id: int) -> WORequest:
        WebAutomation.select_request_button(self.driver)
        try:
            return WebAutomation.search_request(self.driver, request_id)
        except:
            return WORequest(request_id) # return an empty request if request cannot be found

    # TODO: finds the request with the highest id
    def find_last(self):
        return None
