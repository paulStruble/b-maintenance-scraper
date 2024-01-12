# main driver class to run program from

import multiprocessing
from collections import defaultdict
from RequestDB import RequestDB
from Scraper import *
from Log import *
from Config import *


class Driver:
    def __init__(self):
        """A driver used to run the program from. Includes calls to menus, provides a cli, and navigates the program
        when run with <driver>.run()"""
        self.config = Config()  # Config object to load the program's settings
        self.log = Log()  # Log object to track progress and error codes
        self.password_input_hidden = self.config.get("Options", "b_password_inputs_hidden")
        self.user = User.login_prompt(hidden=self.password_input_hidden)  # Log into the user's Calnet profile

        self.database = self.connect_primary_database()

    def connect_primary_database(self) -> RequestDB:
        """Connect to the database (database connection information and credentials are stored in the config).
        Note:
            This function should only be used to connect to the DRIVER'S database (NOT for parallel processes).

        Returns:
            The primary database object
        """
        host, dbname, user, password, port = self.config.get_database_args()

        # prompt for database password input if configured to do so
        if self.config.get("Database", "b_input_database_password_at_runtime"):
            if self.password_input_hidden:
                password = pwinput(prompt="Database Password: ")
            else:
                password = input("Database Password: ")

        headless = self.config.get("Scraper", "b_primary_scraper_headless")  # for primary scraper only
        database = RequestDB(log=self.log, calnet_user=self.user, host=host, dbname=dbname, user=user,
                             password=password, port=port, headless=headless)
        return database

    def main_menu(self) -> None:
        """Run the main menu loop with options to navigate the program."""
        options = [1, 2, 3]
        exit_value = 3
        choice = None

        # main menu loop
        while choice != exit_value:
            print('-' * (shutil.get_terminal_size().columns - 1))  # horizontal line (cosmetic)
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

    def scrape_range_prompt(self) -> None:
        """Prompt the user to scrape a range of work order requests and add them to the database."""
        start = max(int(input("start id: ")), 1)  # inputting 0 causes the program to crash
        stop = int(input("stop id: "))
        num_processes = self.config.get("Scraper", "i_parallel_process_count")  # parallel process count

        print(f"Initializing process: scrape and write requests from ids [{start}] to [{stop}] on [{num_processes}] "
              f"processes")
        if num_processes > 1:  # parallel processing
            headless = self.config.get("Scraper", "b_parallel_scrapers_headless")
            self.add_request_range_parallel(start, stop, num_processes, headless)
        else:  # sequential processing
            self.database.add_request_range(start, stop)
        print(f"Finished scraping requests from ids [{start}] to [{stop}]")

    @staticmethod
    def add_request_range_parallel_helper(request_ids: list, log: Log, calnet_user: User, process_id: int,
                                          headless: bool, db_args: tuple) -> None:
        """Initialize and run a single process for scraping work order requests and adding them to a database.

        A new database object is created for every process to establish a unique connection and scraper as psycopg2
        connections and selenium webdrivers cannot be shared between processes.

        Args:
            request_ids: List of work order request ids to be scraped/added by this process.
            log: Log object for recording progress and error messages.
            calnet_user: Calnet user used to log into maintenance.housing.berkeley.edu.
            process_id: Unique integer id used assigned to this specific process.
            headless: Whether this process should be run in a headless or headful browser.
            db_args: Tuple of arguments to connect to the database.
        """
        host, dbname, user, password, port = db_args
        database = RequestDB(log=log, calnet_user=calnet_user, process_id=process_id, headless=headless, host=host,
                             dbname=dbname, user=user, password=password, port=port)

        database.add_requests(request_ids)
        database.close()

    def add_request_range_parallel(self, start, stop, num_processes, headless=False) -> None:
        """Scrape and add a range of work order requests to the database (in parallel).

        Args:
            start: First work order request id to scrape/add (inclusive)
            stop: Last work order request id to scrape/add (exclusive)
            num_processes: number of parallel processes to use
            headless: Whether processes should be run in a headless or headful browsers
        """
        log = self.log
        calnet_user = self.user
        db_args = self.database.db_args

        # Uniformly assign requests ids to different processes
        # A request id is assigned to a process with: <process id> = <request id> (mod <number of processes>)
        id_dict = defaultdict(list)
        for request_id in range(start, stop):
            process_num = request_id % num_processes
            id_dict[process_num].append(request_id)

        # Generate a list of argument tuples
        # Each tuple will be passed to add_request_range_parallel to create a new process
        args = []
        for process_id in range(num_processes):
            request_ids = id_dict[process_id]
            args.append((request_ids, log, calnet_user, process_id + 1, headless, db_args))

        self.database.close()  # main scraper needs to be closed to allow for its Chrome profile to be cloned for
        # each parallel process
        del self.database
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.starmap(Driver.add_request_range_parallel_helper, args)
        self.database = self.connect_primary_database()

    def run(self):
        """Run this driver. Load and display the main menu."""
        self.main_menu()


# main program run point
if __name__ == "__main__":
    driver = Driver()
    driver.run()
