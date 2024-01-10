# main driver class to run program from

import multiprocessing
from collections import defaultdict
from RequestDB import RequestDB
from Scraper import *
from Log import *


class Driver:
    def __init__(self):
        self.log = Log()
        self.user = User.login_prompt(hidden=False)
        self.database = RequestDB(log=self.log, calnet_user=self.user, headless=False)  # TODO: config

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
        num_processes = int(input("process count: "))

        print(f"Initializing process: scrape and write requests from ids [{start}] to [{stop}] on [{num_processes}] "
              f"processes")
        if num_processes > 1:
            self.add_request_range_parallel(start, stop, num_processes)
        else:
            self.database.add_request_range(start, stop)
        print(f"Finished scraping requests from ids [{start}] to [{stop}]")

    def settings_menu(self):
        print("Settings not yet implemented - please edit config file manually")
        # TODO: read/print config, ability to edit config from cli

    @staticmethod
    def add_request_range_parallel_helper(request_ids, log, calnet_user, process_id, headless, db_args):
        host, dbname, user, password, port = db_args
        database = RequestDB(log=log, calnet_user=calnet_user, process_id=process_id, headless=headless, host=host,
                             dbname=dbname, user=user, password=password, port=port)

        database.add_requests(request_ids)
        database.close()

    def add_request_range_parallel(self, start, stop, num_processes, headless=False):
        log = self.log
        calnet_user = self.user
        db_args = self.database.db_args

        id_dict = defaultdict(list)
        for request_id in range(start, stop):
            process_num = request_id % num_processes
            id_dict[process_num].append(request_id)

        args = []
        for process_id in range(num_processes):
            request_ids = id_dict[process_id]
            args.append((request_ids, log, calnet_user, process_id + 1, headless, db_args))

        self.database.close()
        del self.database
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.starmap(Driver.add_request_range_parallel_helper, args)
        self.database = RequestDB(log=self.log, calnet_user=self.user, headless=False)  # TODO: config

    def run(self):
        self.main_menu()


if __name__ == "__main__":
    driver = Driver()
    driver.run()
