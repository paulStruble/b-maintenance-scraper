# main driver class to run program from

import multiprocessing
from collections import defaultdict
from RequestDB import RequestDB
from Scraper import *
from Log import *
from Config import *


class Driver:
    def __init__(self):
        self.config = Config()
        self.log = Log()
        password_input_hidden = self.config.get("Options", "b_password_inputs_hidden")
        self.user = User.login_prompt(hidden=password_input_hidden)

        host, dbname, user, password, port = self.config.get_database_args()
        if self.config.get("Database", "b_input_database_password_at_runtime"):
            if password != password_input_hidden:
                password = pwinput(prompt="Database Password: ")
            else:
                password = input("Database Password: ")
        headless = self.config.get("Scraper", "b_primary_scraper_headless")
        self.database = RequestDB(log=self.log, calnet_user=self.user, host=host, dbname=dbname, user=user,
                                  password=password, port=port, headless=headless)

    def main_menu(self):
        options = [1, 2, 3]
        exit_value = 3
        choice = None
        while choice != exit_value:
            print('-' * (shutil.get_terminal_size().columns - 1))
            print("\nOptions:\n\n"
                  "1. Scrape a range of work order requests and write to your database\n"
                  "2. Settings\n"
                  "3. Exit\n")
            print('-' * (shutil.get_terminal_size().columns - 1))
            while choice not in options:
                choice = int(input("Input: "))

            match choice:
                case 1:
                    self.scrape_range_prompt()
                    choice = None
                case 2:
                    self.config.settings_menu()
                    choice = None
                case 3:
                    return None

    def scrape_range_prompt(self):
        start = max(int(input("start id: ")), 1)  # inputting 0 causes the program to crash
        stop = int(input("stop id: "))
        num_processes = self.config.get("Scraper", "i_parallel_process_count")

        print(f"Initializing process: scrape and write requests from ids [{start}] to [{stop}] on [{num_processes}] "
              f"processes")
        if num_processes > 1:
            headless = self.config.get("Scraper", "b_parallel_scrapers_headless")
            self.add_request_range_parallel(start, stop, num_processes, headless)
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
