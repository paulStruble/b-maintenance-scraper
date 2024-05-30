import psycopg2
from Scraper import *
from Log import *
import traceback
from User import *
from typing import Iterable


class MaintenanceDatabase:
    def __init__(self, log: Log, calnet_user: User, host: str, dbname: str, user: str, password: str, port: int,
                 process_id: int = 0, headless=True):
        """A connection to a PostgreSQL database with utilities to add work order request data.

        Args:
            log: Log object to record progress and errors to.
            calnet_user: User for Calnet login/authorization.
            host: Hostname of the database.
            dbname: Name of the database.
            user: Username for the database.
            password: Password for the database.
            port: Port for the database.
            process_id: Unique process id for this database connection (for parallel processing).
            headless: Whether to run the scraper's webdriver in headless or headful mode.
        """
        self.scraper = Scraper(user=calnet_user, process_id=process_id, headless=headless)
        self.log = log
        self.db_name = dbname
        self.db_args = (host, dbname, user, password, port)

        self.all_columns_requests = ["id", "room", "status", "building", "tag", "accept_date", "reject_date",
                                     "reject_reason", "location", "item_description", "work_order_num",
                                     "area_description", "requested_action"]
        self.all_columns_orders = ["order_number", "facility", "building", "location_id", "priority", "request_date",
                                   "schedule_date", "work_status", "date_closed", "main_charge_account", "task_code",
                                   "reference_number", "tag_number", "item_description", "request_time",
                                   "date_last_posted", "trade", "contractor_name", "est_completion_date",
                                   "task_description", "requested_action", "corrective_action"]

        self.connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
        self.cursor = self.connection.cursor()

        self.initialize_requests_table()
        self.initialize_orders_table()

        self.connection.commit()

    def initialize_requests_table(self) -> None:
        """Create database table for work requests if none exists yet."""
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INT,
            room VARCHAR(20),
            status VARCHAR(20),
            building VARCHAR(50),
            tag VARCHAR(50),
            accept_date TIMESTAMP,
            reject_date TIMESTAMP,
            reject_reason TEXT,
            location VARCHAR(50),
            item_description TEXT,
            work_order_num VARCHAR(25),
            area_description VARCHAR(50),
            requested_action TEXT
            )
            """)

    # TODO: change "TEXT" to proper types
    def initialize_orders_table(self) -> None:
        """Create database table for work orders if none exists yet."""
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
            order_number VARCHAR(15),
            facility VARCHAR(50),
            building VARCHAR(50),
            location_id VARCHAR(20),
            priority TEXT,
            request_date TEXT,
            schedule_date TEXT,
            work_status TEXT,
            date_closed TEXT,
            main_charge_account TEXT,
            task_code TEXT,
            reference_number TEXT,
            tag_number TEXT,
            item_description TEXT,
            request_time TEXT,
            date_last_posted TEXT,
            trade TEXT,
            contractor_name TEXT,
            est_completion_date TEXT,
            task_description TEXT,
            requested_action TEXT,
            corrective_action TEXT
            )
            """)

    def add_request(self, request_id: int) -> None:
        """Scrape and insert a work request into the database.

        Args:
            request_id: id of the work request.
        """
        try:
            # Skip this request if an entry with the same id already exists
            select_query = f"SELECT 1 FROM requests WHERE id = {request_id}"
            self.cursor.execute(select_query)
            if self.cursor.fetchone():
                self.log.add(f"entry with id [{request_id}] already exists ... skipping this insert request")
                return None

            # Scrape request
            request = self.scraper.scrape_request(request_id)

            # Filter out all null values and their corresponding columns
            columns = [c for c in self.all_columns_requests if getattr(request, c)]
            values = [str(getattr(request, c)).replace("'", "") for c in columns]
            columns = ', '.join(columns)
            values = ', '.join([f"'{v}'" for v in values])
            insert_query = f"INSERT INTO requests ({columns}) VALUES ({values});"

            self.cursor.execute(insert_query)
            self.connection.commit()
            self.log.add(f"successfully inserted request [{request_id}] to database [{self.db_name}]")
        except Exception as e:
            self.log.add(f"failed to insert request [{request_id}]")
            self.log.add_quiet(f"{traceback.format_exc()}\n")

    def add_requests(self, request_ids: Iterable[int]) -> None:
        """Scrape and insert work requests for an iterable of request ids.

        Args:
            request_ids: Iterable of request ids.
        """
        for request_id in request_ids:
            self.add_request(request_id)

    def add_request_range(self, start: int, stop: int) -> None:
        """Scrape and insert a range of work requests into the database.

        Args:
            start: First request id to scrape and insert (inclusive).
            stop: Last request id to scrape and insert (exclusive).
        """
        for request_id in range(start, stop):
            self.add_request(request_id)

    def add_order(self, order_number: str) -> None:
        """Scrape and insert a work order into the database.

        Args:
            order_number: Order number of the order.
        """
        try:
            # Skip this request if an entry with the same id already exists
            select_query = f"SELECT 1 FROM orders WHERE order_number = {order_number}"
            self.cursor.execute(select_query)
            if self.cursor.fetchone():
                self.log.add(f"entry with order number [{order_number}] already exists ... skipping this insert "
                             f"request")
                return None

            # Scrape order
            order = self.scraper.scrape_order(order_number)

            # Filter out all null values and their corresponding columns
            columns = [c for c in self.all_columns_orders if getattr(order, c)]
            values = [str(getattr(order, c)).replace("'", "") for c in columns]
            columns = ', '.join(columns)
            values = ', '.join([f"'{v}'" for v in values])
            insert_query = f"INSERT INTO orders ({columns}) VALUES ({values});"

            self.cursor.execute(insert_query)
            self.connection.commit()
            self.log.add(f"successfully inserted order [{order_number}] to database [{self.db_name}]")
        except Exception as e:
            self.log.add(f"failed to insert order [{order_number}]")
            self.log.add_quiet(f"{traceback.format_exc()}\n")

    def add_orders(self, order_numbers: Iterable[str]) -> None:
        """Scrape and insert work orders for an iterable of order numbers.

        Args:
            order_numbers: Iterable of order numbers.
        """
        for order_number in order_numbers:
            self.add_order(order_number)

    def add_order_range(self, start: int, stop: int, prefix: str = "HM-") -> None:
        """Scrape and insert a range of work orders into the database.

        Args:
            start: First order number to scrape and insert (inclusive).
            stop: Last order number to scrape and insert (exclusive).
            prefix: String to append the beginning of each integer work order number (default is "HM-").
        """
        for int_order_number in range(start, stop):
            order_number = prefix + str(int_order_number)
            self.add_order(order_number)

    def close(self) -> None:
        """Close the connection to the database."""
        self.cursor.close()
        self.connection.close()
