# an independent driver class solely for testing and debugging purposes
# TODO: test class - write JUnit tests - test features on a series of random work requests
from RequestDB import RequestDB
from Scraper import *
#
# scraper = Scraper()
# scraper.login_calnet()
# for request_number in range(100000, 200001, 5000):
#     try:
#         print(scraper.scrape_request(request_number).to_csv())
#     except:
#         print(f"failed to print request #{request_number}")
# input()
#
# """current_request = scraper.scrape_request(1)
# if current_request:
#     print(current_request.to_csv())
#
# print("execution complete")"""
#
# print(scraper.scrape_request(0).to_csv())

scraper = Scraper()
database = RequestDB()

scraper.login_calnet()
for request_id in range(200000, 400001, 201):
    try:
        database.add_request(scraper.scrape_request(request_id)) # TODO: log
    except:
        print(f"Error inserting with Request ID: {request_id}")

database.close()
input()
