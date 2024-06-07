from datetime import datetime
from pathlib import Path


class Log:
    def __init__(self):
        """A log to capture certain events/errors throughout the program's execution (bound to a specific .log file)."""
        filename = f"Log {datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.filepath = Path.cwd() / 'Logs' / filename
        with open(self.filepath, 'w') as log:
            log.write(f"log created at time: {datetime.now()}\n\n")

    def add(self, message: str) -> None:
        """Add a timestamped message to the log and print it to the console.

        Args:
            message: The message to add to the log and print (excluding timestamp)
        """
        print(self.add_quiet(message))

    def add_quiet(self, message: str) -> str:
        """Add a timestamped message to the log (without printing it to the console).

        Args:
            message: The message to add to the log (excluding timestamp)

        Returns:
            The timestamped log message
        """
        output = f"[{datetime.now()}] " + message

        with open(self.filepath, 'a') as log:
            log.write(output + "\n")

        return output
