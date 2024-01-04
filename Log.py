# Utilities for logging runtime information

import logging
from datetime import datetime


class Log:
    def __init__(self):
        # create and name log
        self.filepath = f"./Logs/Log {datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(self.filepath, 'w') as log:
            log.write(f"log created at time: {datetime.now()}\n\n")

    # add a timestamped message to the log and log in console
    def add(self, message: str):
        print(self.add_quiet(message))

    # add a timestamped message to the log (no log in console)
    def add_quiet(self, message: str) -> str:
        output = f"[{datetime.now()}] " + message

        with open(self.filepath, 'a') as log:
            log.write(output + "\n")

        return output
