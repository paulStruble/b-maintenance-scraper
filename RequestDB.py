# utilities to communicate with request database
# TODO: acquire default values from config/profile

import math
from selenium import webdriver
import psycopg2
from Scraper import *
from Log import *
import multiprocessing
import traceback
from User import *


class RequestDB:
    def __init__(self, log: Log, calnet_user: User, driver_cookies: list[dict] = None, host="localhost", dbname="postgres", user="postgres", password="postgres", port=5432):
        self.log = log
        self.calnet_user = calnet_user
        self.driver_cookies = driver_cookies
        self.dbname = dbname
        self.all_columns = ["id", "room", "status", "building", "tag", "accept_date", "reject_date", "reject_reason",
                            "location", "item_description", "work_order_num", "area_description", "requested_action"]

        self.connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=5432)
        self.cursor = self.connection.cursor()

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

        self.connection.commit()

    # scrape and insert a work request into the database
    def add_request(self, request_id: int, scraper: Scraper):
        try:
            # skip this request if an entry with the same id already exists
            select_query = f"SELECT * FROM requests WHERE id = {request_id}"
            self.cursor.execute(select_query)
            if self.cursor.fetchone():
                self.log.add(f"entry with id [{request_id}] already exists ... skipping this insert request")
                return None

            # scrape request
            request = scraper.scrape_request(request_id)

            # filter out all null values and their corresponding columns
            columns = [c for c in self.all_columns if getattr(request, c)]
            values = [str(getattr(request, c)).replace("'", "") for c in columns]
            columns = ', '.join(columns)
            values = ', '.join([f"'{v}'" for v in values])
            insert_query = f"INSERT INTO requests ({columns}) VALUES ({values});"

            self.cursor.execute(insert_query)
            self.connection.commit()
            self.log.add(f"successfully inserted request [{request_id}] to database [{self.dbname}]")
        except Exception as e:
            self.log.add(f"failed to insert request [{request_id}]")
            self.log.add_quiet(f"{traceback.format_exc()}\n")

    # TODO: run parallel directly from add_request_range using boolean parallel argument
    # scrape and insert a range of work requests into the database (sequential)
    def add_request_range(self, start: int, stop: int, scraper: Scraper):
        for request_id in range(start, stop):
            self.add_request(request_id, scraper)

    # TODO: add headless option to config
    # generate a list of argument tuples for each process (unique scrapers and id ranges)
    def generate_args_add_request_range_parallel(self, start: int, stop: int, process_count=4) -> list[tuple[int, int, Scraper]]:
        process_args = []
        process_stop = start
        remaining_tasks = stop - start

        for remaining_processes in range(process_count, 0, -1):
            scraper = Scraper(user=self.calnet_user, cookies=self.driver_cookies, headless=False)  # pass info from a logged-in browser
            # prevents the need to log in again for every process

            process_task_count = math.ceil(remaining_tasks / remaining_processes)
            remaining_tasks -= process_task_count
            process_start = process_stop
            process_stop = process_start + process_task_count

            args = (process_start, process_stop, scraper)
            process_args.append(args)

        return process_args

    # TODO: implement config for process count
    # TODO: corner cases for small ranges
    # scrape and insert a range of work requests into the database (parallel)
    def add_request_range_parallel(self, start: int, stop: int, process_count=4):
        process_args = self.generate_args_add_request_range_parallel(start, stop, process_count)

        # run processes in parallel
        with multiprocessing.Pool(processes=process_count) as pool:
            pool.starmap(self.add_request_range, process_args)

    # close the connection to the database
    def close(self):
        self.cursor.close()
        self.connection.close()
