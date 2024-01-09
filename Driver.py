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
        options = [1, 2, 3]
        exit_value = 3
        choice = None
        while choice != exit_value:
            print("""
            ------------ Main Menu ------------
            Options:
            1. Scrape a range of work order requests and write to your database
            2. Settings
            3. Exit
            -----------------------------------
            """)
            choice = int(input())
            while choice not in options:
                choice = int(input())

            match choice:
                case 1:
                    self.scrape_range_prompt()
                case 2:
                    self.settings_menu()
                case 3:
                    return None

    def scrape_range_prompt(self):
        start = int(input("start id: "))
        stop = int(input("stop id: "))
        processes = int(input("processes: "))

        print(f"Initializing process: scrape and write requests from ids [{start}] to [{stop}] on [{processes}] processes")
        if processes > 1:
            self.database.add_request_range_parallel(start, stop, process_count=processes)
        else:
            self.database.add_request_range(start, stop, scraper=self.scraper)
        print(f"Finished scraping requests from ids [{start}] to [{stop}]")

    def settings_menu(self):
        print("Settings not yet implemented - please edit config file manually")
        # TODO: read/print config, ability to edit config from cli

    def run(self):
        self.main_menu()
        self.database.close()


if __name__ == "__main__":
    driver = Driver()
    driver.run()
