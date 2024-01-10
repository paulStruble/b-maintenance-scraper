# tool to scrape work order requests from maintenance website
# TODO: load browser state with driver.get_cookies() and driver.add_cookie({'domain':''})

import hashlib
import os
import shutil

from selenium.common import exceptions
import User
from selenium import webdriver
from WebAutomation import *
from WORequest import *
from User import *


class Scraper:
    def __init__(self, user: User = None, process_id: int = 0, headless: bool = True):
        self.user = user
        self.driver = self.initialize_driver(process_id=process_id, headless=headless)
        self.login_calnet()

    # initialize a webdriver instance (chromedriver)
    def initialize_driver(self, process_id, headless):
        chrome_options = webdriver.ChromeOptions()

        # load or create a unique chrome profile for this webdriver instance
        profile_name = hashlib.sha256(self.user.username.encode('utf-8')).hexdigest()
        profile_path = os.path.dirname(os.path.realpath(__file__)) + f"\\Profiles\\{profile_name}"
        profile_instance_path = profile_path + f"\\p{process_id}"
        if not os.path.exists(profile_instance_path):
            if process_id == 0:
                os.makedirs(profile_instance_path)
            else:
                base_instance_path = profile_path + r"\p0"
                shutil.copytree(base_instance_path, profile_instance_path)

        # configure and initialize webdriver instance
        chrome_options.add_argument(f"user-data-dir={profile_instance_path}")
        chrome_options.headless = headless
        driver = webdriver.Chrome(options=chrome_options)
        if not headless:
            driver.set_window_size(1280, 720)  # TODO: set window size relative to monitor resolution, config
        return driver

    # prompts user for calnet login
    # TODO: if duo login times out, script crashes - add try statement and/or loop
    # TODO: account for incorrect login info - loop
    def login_calnet(self):
        if not self.user:
            print('CALNET LOGIN:')
            self.user = User.login_prompt()

        WebAutomation.login_calnet(self.driver, self.user)

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
