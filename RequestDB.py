# utilities to communicate with request database

import psycopg2
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

    # TODO: clean data, escape coding characters, null entries, try statement for duplicate requests (prevent crash), add audio
    # TODO: scrape request inside this function
    def add_request(self, request: WORequest):
        # skip this request if an entry with the same id already exists
        select_query = f"SELECT * FROM requests WHERE id = {request.id}"
        self.cursor.execute(select_query)
        if self.cursor.fetchone():
            print(f"entry with id [{request.id}] already exists ... skipping this insert request")
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
