# utilities to communicate with request database

import psycopg2

import Scraper
from WORequest import WORequest


class RequestDB:
    def __init__(self):
        self.all_columns = ["id", "room", "status", "building", "tag", "accept_date", "reject_date", "reject_reason",
                            "location", "item_description", "work_order_num", "area_description", "requested_action"]

        self.connection = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="postgres",
                                      port=5432)
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

    # a
    # TODO: clean data, escape coding characters, null entries, add audio
    def add_request(self, request_id: int, scraper: Scraper):
        # skip this request if an entry with the same id already exists
        select_query = f"SELECT * FROM requests WHERE id = {request_id}"
        self.cursor.execute(select_query)
        if self.cursor.fetchone():
            print(f"entry with id [{request_id}] already exists ... skipping this insert request")
            return None

        # scrape request
        try:
            request = scraper.scrape_request(request_id)
        except:
            print(f"failed to scrape request with id [{request_id}]")
            return None

        # filter out all null values and their corresponding columns
        columns = [c for c in self.all_columns if getattr(request, c)]
        values = [str(getattr(request, c)).replace("'", "") for c in columns]
        columns = ', '.join(columns)
        values = ', '.join([f"'{v}'" for v in values])
        insert_query = f"INSERT INTO requests ({columns}) VALUES ({values});"

        self.cursor.execute(insert_query)
        self.connection.commit()

    # close the connection to the database
    def close(self):
        self.cursor.close()
        self.connection.close()
