# an independent driver class solely for testing and debugging purposes
# TODO: test class - write JUnit tests - test features on a series of random work requests
# TODO: input validation (all inputs)
# TODO: chrome, chromedriver installations and refactor to relative paths
# TODO: setup - required libraries, chrome install, chromedriver install, postgres
# TODO: better typechecking, remove inappropriate default args
# TODO: documentation cleanup - consistency in comment formatting, comments where appropriate
# TODO: remove classes where necessary (maybe for utils) - convert class modules to just function modules
# TODO: cleanup - "final variables"
# TODO: move module/class variables to config
# TODO: include in docs: custom chrome/chromedriver version install (manual install to filepath)
# TODO: option to update chrome version
# TODO: readme/documentation instructions for manual chrome/chromedriver install (install + s_chrome_version + s_chrome_platform)
# TODO: readme/documentation instructions for postgres setup (MUST MANUALLY CHANGE b_database_setup_complete)
# TODO: ensure config path works for windows AND unix
# TODO: update SetupUtils instructions for postgres/chrome installs with relevant readme sections/references
# TODO: catch WAAAAYYYY more errors
# TODO: manual first time setup - parallel process count (and go through all other config options)
# TODO: logging (maybe automatically log all console output/input (except login info)
# TODO: may need to include empty Browser and Profiles directories with releases - maybe add if missing (or just ship with)
# TODO: Scraper scrape_order and scrape_request exceptions too broad
# TODO: Include start/end info in readme
# TODO: assert statements to ensure proper args and inputs
# TODO: keyboard interrupt to exit (readme)
# TODO: logging info - also for debugging failed database inserts (readme)
# TODO: readme - login credentials not checked for validity - ensure correct when inputting
# TODO: profiler for optimization

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