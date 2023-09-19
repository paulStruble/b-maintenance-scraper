# an independent driver class solely for testing and debugging purposes

from Scraper import *

scraper = Scraper()
scraper.login_calnet()
for request_number in range(100000, 200001, 10000):
    try:
        print(scraper.scrape_request(request_number).to_csv())
    except:
        print(f"failed to print request #{request_number}")
input()