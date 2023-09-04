# an independent driver class solely for testing and debugging purposes

from Scraper import *

scraper = Scraper()
scraper.login_calnet()
scraper.scrape_request(220149)
input()