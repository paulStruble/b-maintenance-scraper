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
from typing import Iterable


class RequestDB:
    def __init__(self, log: Log, calnet_user: User, process_id: int = 0, headless=True, host="localhost",
                 dbname="postgres", user="postgres", password="postgres", port=5432):
        self.scraper = Scraper(user=calnet_user, process_id=process_id, headless=headless)
        self.log = log
        self.db_name = dbname
        self.db_args = (host, dbname, user, password, port)

        self.all_columns = ["id", "room", "status", "building", "tag", "accept_date", "reject_date", "reject_reason",
                            "location", "item_description", "work_order_num", "area_description", "requested_action"]

        self.connection = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
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
    def add_request(self, request_id: int):
        # noinspection PyBroadException
        try:
            # skip this request if an entry with the same id already exists
            select_query = f"SELECT * FROM requests WHERE id = {request_id}"
            self.cursor.execute(select_query)
            if self.cursor.fetchone():
                self.log.add(f"entry with id [{request_id}] already exists ... skipping this insert request")
                return None

            # scrape request
            request = self.scraper.scrape_request(request_id)

            # filter out all null values and their corresponding columns
            columns = [c for c in self.all_columns if getattr(request, c)]
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

    # scraper and insert work requests for an iterable
    def add_requests(self, request_ids: Iterable[int]):
        for request_id in request_ids:
            self.add_request(request_id)

    # scrape and insert a range of work requests into the database
    def add_request_range(self, start: int, stop: int):
        for request_id in range(start, stop):
            self.add_request(request_id)

    # close the connection to the database
    def close(self):
        self.cursor.close()
        self.connection.close()
