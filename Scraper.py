# tool to scrape work order requests from maintenance website
# TODO: load browser state with driver.get_cookies() and driver.add_cookie({'domain':''})
from selenium.common import exceptions

from selenium import webdriver
from WebAutomation import *
from WORequest import *
from User import *


class Scraper:
    def __init__(self, user: User = None, cookies: list[dict] = None, headless: bool = True):
        # initialize driver
        self.options = webdriver.ChromeOptions()
        self.options.headless = headless
        self.driver = webdriver.Chrome(options=self.options)
        if not headless:
            self.driver.set_window_size(1280, 720) #TODO: set window size relative to monitor resolution, config

        # calnet login
        self.user = user
        self.login_calnet(cookies)

    # prompts user for calnet login
    # TODO: if duo login times out, script crashes - add try statement and/or loop
    # TODO: account for incorrect login info - loop
    def login_calnet(self, cookies: list[dict]):
        if not self.user:
            print('CALNET LOGIN:')
            self.user = User.login_prompt()

        WebAutomation.login_calnet(self.driver, self.user)

        # if cookies:
        #     WebAutomation.login_calnet(self.driver, self.user, duo=False)
        #     self.add_cookies(cookies)
        # else:
        #     WebAutomation.login_calnet(self.driver, self.user, duo=True)

    # scrapes a work order request with the specified request number
    # returns a WORequest
    def scrape_request(self, request_id: int) -> WORequest:
        WebAutomation.select_request_button(self.driver)
        try:
            return WebAutomation.search_request(self.driver, request_id)
        except:
            return WORequest(request_id)  # return an empty request if request cannot be found

    # return a list of dictionaries containing the driver's current cookies
    def get_cookies(self) -> list[dict]:
        return self.driver.get_cookies()

    # add a list of cookies to the driver
    def add_cookies(self, cookies: list[dict], lax: bool = True):
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except exceptions.InvalidCookieDomainException as e:
                print(f"failed to add cookie with name [{cookie.get('name')}] (wrong domain)")

    # close this scraper instance
    def close(self):
        self.driver.close()

    # TODO: finds the request with the highest id
    def find_last(self):
        return None
