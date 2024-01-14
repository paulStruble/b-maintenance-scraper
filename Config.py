# configurable settings for various program features
# TODO: comments + standardize comments
# TODO: remove non-base chrome profiles (take up a lot of storage)
# TODO: first-time setup
import configparser
import os
import shutil


class Config:
    def __init__(self, path=None):
        if path is None:
            path = os.path.dirname(os.path.realpath(__file__)) + f"\\config.ini"
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def get(self, section: str, option: str):
        """Retrieve an option from the config.

        Args:
            section: The config section to retrieve from.
            option: the name of the specific option to retrieve.

        Returns:
            The value of the option in the config.
        """
        value = self.config[section][option]

        match option[0]:
            case 's':
                return value
            case 'b':
                if value == 'true':
                    return True
                elif value == 'false':
                    return False
            case 'i':
                return int(value)

    def get_database_args(self) -> tuple[str, str, str, str, int]:
        """Retrieve a tuple of arguments from the config to initialize a database connection (used to initialize a
        RequestDB object).

        Returns:
            A tuple of arguments from the config to initialize a RequestDB object.
        """
        host = self.config.get('Database', 's_host')
        dbname = self.config.get('Database', 's_name')
        user = self.config.get('Database', 's_user')
        password = self.config.get('Database', 's_password')
        port = self.config.get('Database', 'i_port')
        return host, dbname, user, password, port

    def set(self, section, option, value) -> None:
        """Update an option in the config.

        Args:
            section: The section of the option to update.
            option: The specific option to update.
            value: The new value to set the option to.
        """
        self.config[section][option] = value

    def save(self) -> None:
        """Save and write changes made to the config."""
        with open(self.path, 'w') as config_file:
            self.config.write(config_file)
        self.config.read(self.path)

    def revert(self) -> None:
        """Cancel changes made to the config (before they have been saved/written)."""
        self.config.read(self.path)

    def print_settings(self) -> None:
        """Print the current config to the console."""
        print('-' * (shutil.get_terminal_size().columns - 1))
        print("\nCurrent Settings:\n")
        for section in self.config.sections():
            print(f"[{section}]")
            for key, value in self.config.items(section):
                print(f"{key} = {value}")
            print()
        print('-' * (shutil.get_terminal_size().columns - 1))

    def valid_value_input(self, option: str, value: str) -> bool:
        """Check if a value has the same type as a specified option.

        Args:
            option: The config option to check against.
            value: The new value to check for validity.

        Returns:
            True if the value is valid, False otherwise.
        """
        type_tag = option[0]
        match type_tag:
            case 'b':  # boolean
                return value in ('true', 'false')
            case 's':  # string
                return True
            case 'i':  # integer
                try:
                    int(value)
                    return True
                except ValueError:
                    return False
            case _:
                return False

    def update_option(self) -> None:
        """Prompt the user to update a single config option. Update the option and save."""
        print('-' * (shutil.get_terminal_size().columns - 1))
        section, option, value = "", "", ""

        while section not in self.config.sections():
            section = input("Section: ")
        while option not in self.config[section]:
            option = input("Option Name: ")
        while not self.valid_value_input(option, value):
            value = input("Updated Value: ")

        self.set(section, option, value)
        self.save()

    def settings_menu(self) -> None:
        """Prompt the user with a menu for viewing and editing the current config from the console."""
        choice = None
        exit_value = 2
        options = [1, 2]

        while choice != exit_value:
            self.print_settings()
            print("\nOptions:\n\n"
                  "1. Update settings\n"
                  "2. Return to main menu\n\n"
                  "NOTE: Some settings require the program to be restarted in order to take full effect\n")
            print('-' * (shutil.get_terminal_size().columns - 1))

            while choice not in options:
                choice = int(input("Input: "))

            match choice:
                case 1:
                    self.update_option()
                    choice = None
                case 2:
                    return None
