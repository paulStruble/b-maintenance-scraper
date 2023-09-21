# an independent driver class solely for testing and debugging purposes

from Scraper import *

scraper = Scraper()
scraper.login_calnet()
for request_number in range(100000, 200001, 5000):
    try:
        print(scraper.scrape_request(request_number).to_csv())
    except:
        print(f"failed to print request #{request_number}")
input()

"""current_request = scraper.scrape_request(1)
if current_request:
    print(current_request.to_csv())

print("execution complete")"""

print(scraper.scrape_request(0).to_csv())