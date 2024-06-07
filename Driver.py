import multiprocessing
from collections import defaultdict
from MaintenanceDatabase import MaintenanceDatabase
from Scraper import *
from Log import *
from Config import *
from User import login_prompt
from SetupUtils import SetupUtils
from pathlib import Path
from Menu import Menu


class Driver:
    def __init__(self):
        """A driver used to run the program from. Includes calls to menus, provides a cli, and navigates the program
        when run with <driver>.run()"""
        self.config = Config()  # Config object to load the program's settings
        self.log = Log()  # Log object to track progress and error codes

        # First-time setup
        if not self.config.get('Program-Variables', 'b_first_time_setup_complete'):
            SetupUtils.first_time_setup(self.config)

        self.password_input_hidden = self.config.get("Options", "b_password_inputs_hidden")
        self.user = login_prompt(hidden=self.password_input_hidden)  # Log into the user's Calnet profile

        self.database = self.connect_primary_database()

    def connect_primary_database(self) -> MaintenanceDatabase:
        """Connect to the database (database connection information and credentials are stored in the config).
        Note:
            This function should only be used to connect to the DRIVER'S database (NOT for parallel processes).

        Returns:
            The primary database object.
        """
        host, dbname, user, password, port = self.config.get_database_args()

        # Prompt for database password input if configured to do so
        if self.config.get("Database", "b_input_database_password_at_runtime"):
            if self.password_input_hidden:
                password = Menu.input_prompt(prompt="Database Password: ", hidden=True)
            else:
                password = Menu.input_prompt("Database Password: ")

        headless = self.config.get("Scraper", "b_primary_scraper_headless")  # For primary scraper only
        database = MaintenanceDatabase(log=self.log, chrome_path=self.get_chrome_dir(),
                                       chromedriver_path=self.get_chromedriver_dir(), calnet_user=self.user,
                                       host=host, dbname=dbname, user=user, password=password, port=port,
                                       headless=headless)
        return database

    def main_menu(self) -> None:
        """Run the main menu loop with options to navigate the program."""
        title = "MAIN MENU"
        options = ["Scrape a range of work order requests and write to your database",
                   "Scrape a range of work orders and write to your database",
                   "Settings",
                   "Exit"]

        while True:
            selected_option = Menu.menu_prompt(options, title=title)
            match selected_option:
                case 0:
                    self.scrape_range_prompt(item_type='request')
                case 1:
                    order_prefix = self.config.get('Program-Variables', 's_work_order_prefix')
                    self.scrape_range_prompt(item_type='order', prefix=order_prefix)
                case 2:
                    self.config.settings_menu()
                case 3:
                    return None

    def scrape_range_prompt(self, item_type: str, prefix: str = "") -> None:
        """Prompt the user to scrape a range of work order requests or work orders and add them to the database.

        Args:
            item_type: Type of item to be scraped (either 'request' or 'order').
            prefix: Prefix to append to work order numbers ("" for requests).
        """
        start = int(Menu.input_prompt(f"start id: {prefix}"))
        stop = int(Menu.input_prompt(f"stop id: {prefix}"))

        if item_type == "request":
            start = max(1, start)  # Inputting 0 causes program to crash

        num_processes = self.config.get("Scraper", "i_parallel_process_count")  # Parallel process count

        print(f"Initializing process: scrape and write orders from ids [{prefix}{start}] to [{prefix}{stop}] on "
              f"[{num_processes}] processes")

        if num_processes > 1:  # Parallel processing
            headless = self.config.get("Scraper", "b_parallel_scrapers_headless")
            self.add_item_range_parallel(item_type, start, stop, num_processes, headless=headless, prefix=prefix)
        else:  # Sequential processing
            if item_type == "request":
                self.database.add_request_range(start, stop)
            elif item_type == "order":
                self.database.add_order_range(start, stop, prefix)

        print('-' * (shutil.get_terminal_size().columns - 1))  # Horizontal line (cosmetic)
        print(f"Finished scraping requests from ids [{prefix}{start}] to [{prefix}{stop}]")

    @staticmethod
    def add_item_range_parallel_helper(item_type: str, item_ids: list, prefix: str, log: Log, chrome_path: Path,
                                       chromedriver_path: Path, calnet_user: User, process_id: int, headless: bool,
                                       db_args: tuple) -> None:
        """Initialize and run a single process for scraping work order requests and adding them to a database.

        A new database object is created for every process to establish a unique connection and scraper as psycopg2
        connections and selenium webdrivers cannot be shared between processes.

        Args:
            item_type: Type of item to be scraped (either 'request' or 'order').
            item_ids: List of work order item ids to be scraped/added by this process.
            prefix: Prefix to append to work order numbers ("" for requests).
            log: Log object for recording progress and error messages.
            chrome_path: Path pointing to the chrome directory to be used for Scrapers.
            chromedriver_path: Path pointing to the chromedriver directory to be used for Scrapers.
            calnet_user: Calnet user used to log into maintenance.housing.berkeley.edu.
            process_id: Unique integer id assigned to this specific process.
            headless: Whether this process should be run in a headless or headful browser.
            db_args: Tuple of arguments to connect to the database.
        """
        host, dbname, user, password, port = db_args
        database = MaintenanceDatabase(log=log, chrome_path=chrome_path, chromedriver_path=chromedriver_path,
                                       calnet_user=calnet_user, process_id=process_id, headless=headless, host=host,
                                       dbname=dbname, user=user, password=password, port=port)

        try:
            if item_type == 'request':
                database.add_requests(item_ids)
            elif item_type == 'order':
                database.add_orders(item_ids)
            database.close()
        except KeyboardInterrupt:  # Allows user to exit program to interrupt scraping a large range of items
            database.close()

    def add_item_range_parallel(self, item_type: str, start: int, stop: int, num_processes: int, headless=False,
                                prefix: str = "") -> None:
        """Scrape and add a range of work order requests or work orders to the database (in parallel).

        Args:
            item_type: Type of item to be scraped (either 'request' or 'order').
            start: First item id to scrape/add (inclusive).
            stop: Last item id to scrape/add (exclusive).
            num_processes: number of parallel processes to use.
            headless: Whether processes should be run in a headless or headful browsers.
            prefix: Prefix to append to work order numbers (leave empty for requests).
        """
        log = self.log
        chrome_path = self.get_chrome_dir()
        chromedriver_path = self.get_chromedriver_dir()
        calnet_user = self.user
        db_args = self.database.db_args

        # Uniformly assign item ids to different processes
        # An item id is assigned to a process with: <process id> = <item id> (mod <number of processes>)
        id_dict = defaultdict(list)
        for item_id in range(start, stop):
            process_num = item_id % num_processes
            if item_type == 'request':
                id_dict[process_num].append(item_id)
            elif item_type == 'order':
                id_dict[process_num].append(prefix + str(item_id))

        # Generate a list of argument tuples
        # Each tuple will be passed to add_item_range_parallel to create a new process
        args = []
        for process_id in range(num_processes):
            item_ids = id_dict[process_id]
            args.append((item_type, item_ids, prefix, log, chrome_path, chromedriver_path, calnet_user,
                         process_id + 1, headless, db_args))

        self.database.close()  # Main scraper needs to be closed to allow for its Chrome profile to be cloned for
        # each parallel process
        del self.database
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.starmap(Driver.add_item_range_parallel_helper, args)
        self.database = self.connect_primary_database()

    def get_chrome_dir(self) -> Path:
        """Get the path to the director of the currently-enabled Chrome version (e.g. chrome-win64).

            Returns: Path object pointing to the Chrome directory.
        """
        chrome_version = self.config.get('Scraper', 's_chrome_version')
        chrome_platform = self.config.get('Scraper', 's_chrome_platform')
        return Path.cwd() / 'Browser' / chrome_version / ('chrome-' + chrome_platform)

    def get_chromedriver_dir(self) -> Path:
        """Get the path to the directory of the currently-enabled chromedriver version (e.g. chromedriver-win64).

            Returns: Path object pointing to the chromedriver directory.
        """
        chrome_version = self.config.get('Scraper', 's_chrome_version')
        chrome_platform = self.config.get('Scraper', 's_chrome_platform')
        return Path.cwd() / 'Browser' / chrome_version / ('chromedriver-' + chrome_platform)

    def run(self):
        """Run this driver. Load and display the main menu."""
        self.main_menu()


# Main program run point
if __name__ == "__main__":
    driver = Driver()
    driver.run()
