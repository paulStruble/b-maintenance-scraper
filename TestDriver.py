# an independent driver class solely for testing and debugging purposes
# TODO: test class - write JUnit tests - test features on a series of random work requests
# TODO: input validation (all inputs)
# TODO: chrome, chromedriver installations and refactor to relative paths
# TODO: setup - required libraries, chrome install, chromedriver install, postgres
# TODO: better typechecking, remove inappropriate default args
# TODO: documentation cleanup - consistency in comment formatting, comments where appropriate
# TODO: remove classes where necessary (maybe for utils) - convert class modules to just function modules
# TODO: move module/class variables to config
# TODO: include in docs: custom chrome/chromedriver version install (manual install to filepath)
# TODO: option to update chrome version
import multiprocessing
from MaintenanceDatabase import MaintenanceDatabase
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

from Log import *
import traceback

# log = Log()
# scraper = Scraper(headless=False)
# # cookies = scraper.get_cookies()
# user = scraper.user
#
# database = RequestDB(log, user)
# try:
#     database.add_request_range(0, 100001)
# except Exception as e:
#     log.add(f"exited with error traceback:\n{traceback.format_exc()}\n")
#
# database.close()

# args = database.generate_args_add_request_range_parallel(3, 26, 5)
# input()

# from Log import *
#
# my_log = Log()
# my_log.add("this is a call to Log.add!")
# my_log.add_quiet("this is a call to Log.add_quiet!")

scraper = Scraper()