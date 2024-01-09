# main driver class to run program from

from RequestDB import RequestDB
from Scraper import *
import traceback
from Log import *

class Driver:
    def __init__(self):
        self.log = Log()
        self.scraper = Scraper(headless=True)   # TODO: config
        user = self.scraper.user
        self.database = RequestDB(self.log, user)

    def main_menu(self):
        options = [1, 2]
        exit = 2
        choice = None
        while choice != exit:
            print("""
            ------------ Main Menu ------------
            Options:
            1. Scrape a range of work order requests and write to your database
            2. Exit
            -----------------------------------
            """)
            choice = int(input())
            while choice not in options:
                choice = int(input())

            match choice:
                case 1:
                    self.scrape_range_prompt()
                case 2:
                    return None

    def scrape_range_prompt(self):
        start = int(input("start id: "))
        end = int(input("end id: "))

        print(f"Initializing process: scrape and write requests from ids [{start}] to [{end}]")
        self.database.add_request_range(start, end, self.scraper)
        print(f"Finished scraping requests from ids [{start}] to [{end}]")

    def run(self):
        self.main_menu()
        self.database.close()


if __name__ == "__main__":
    driver = Driver()
    driver.run()
