# Utilities for logging runtime information

import logging
from datetime import datetime


class Log:
    def __init__(self):
        """An object linked to a unique .log file that captures events and errors throughout the program."""
        self.filepath = f"./Logs/Log {datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(self.filepath, 'w') as log:
            log.write(f"log created at time: {datetime.now()}\n\n")

    def add(self, message: str):
        """Add a timestamped message to the log and print it to the console."""
        print(self.add_quiet(message))

    def add_quiet(self, message: str) -> str:
        """Add a timestamped message to the log (without printing it to the console)."""
        output = f"[{datetime.now()}] " + message

        with open(self.filepath, 'a') as log:
            log.write(output + "\n")

        return output
