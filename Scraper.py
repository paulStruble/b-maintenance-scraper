#from bs4 import beatifulsoup4
#import requests
from selenium import webdriver
from User import *

class Scraper:
    def __init__(self):
        self.current_user = None
        self.driver = webdriver.chrome

    # prompts user for calnet login
    def login_calnet(self):
        print('CALNET LOGIN:')
        self.current_user = User.login_prompt()

    def scrape_request(self):
        return None
