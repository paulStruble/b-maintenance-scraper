# TODO: remove non-base chrome profiles (take up a lot of storage)
import configparser
import shutil
from pathlib import Path
from Menu import Menu


class Config:
    def __init__(self, path: Path = None):
        """An ini configuration for the current program with methods to retrieve and modify options at runtime.

        Args:
            path: Path to the config file
        """
        if path is None:
            path = Path.cwd() / 'config.ini'
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)  # Load config file

    def get(self, section: str, option: str):
        """Retrieve an option from the config.

        Args:
            section: The config section to retrieve from
            option: The name of the specific option to retrieve

        Returns:
            The value of the option in the config (cast to the correct datatype)
        """
        value = self.config[section][option]

        # Cast the value to the correct datatype
        # The first character of each option name denotes the option's datatype
        match option[0]:
            case 's':  # str
                return value
            case 'b':  # bool
                if value == 'true':
                    return True
                elif value == 'false':
                    return False
            case 'i':  # int
                return int(value)

    def get_database_args(self) -> tuple[str, str, str, str, int]:
        """Retrieve a tuple of arguments from the config to initialize a database connection (used to initialize a
        MaintenanceDatabase object). Note that initializing a MaintenanceDatabase object still requires other arguments.

        Returns:
            A tuple of arguments from the config to initialize a MaintenanceDatabase object
        """
        host = self.get('Database', 's_host')
        dbname = self.get('Database', 's_name')
        user = self.get('Database', 's_user')
        password = self.get('Database', 's_password')
        port = self.get('Database', 'i_port')
        return host, dbname, user, password, port

    def set(self, section: str, option: str, value, save=False) -> None:
        """Update an option in the config. Does not save the change by default.

        Args:
            section: The section of the option to update
            option: The specific option to update
            value: The new value to set the option to
            save: True to write the changes immediately (False waits for a call to <Config>.save() before saving)
        """
        self.config[section][option] = value
        if save:
            self.save()

    def save(self) -> None:
        """Save and write changes made to the config."""
        with open(self.path, 'w') as config_file:
            self.config.write(config_file)
        self.reload()  # Reload config to account for change

    def reload(self) -> None:
        """Reload config settings from disk.\n
        WARNING: DISCARDS ALL UNSAVED CHANGES."""
        self.config.read(self.path)

    def print_settings(self) -> None:
        """WARNING: DEPRECATED BY NEW VERSION OF settings_menu\n
        Print the current config to the console."""
        print('-' * (shutil.get_terminal_size().columns - 1))  # Horizontal line (cosmetic)
        print("\nCurrent Settings:\n")
        for section in self.config.sections():
            print(f"[{section}]")
            for key, value in self.config.items(section):
                print(f"{key} = {value}")
            print()
        print('-' * (shutil.get_terminal_size().columns - 1))

    @staticmethod
    def is_valid_option_value(option: str, value: str) -> bool:
        """Check if a value has the same datatype as a specified option.

        Args:
            option: The name of the config option to check against
            value: The new value to check for validity

        Returns:
            True if the value is valid, False otherwise
        """
        if value is None:
            return False

        type_tag = option[0]  # First character of option denotes the option's datatype
        match type_tag:
            case 'b':  # bool
                return value in ('true', 'false')
            case 's':  # str
                return True
            case 'i':  # int
                try:
                    int(value)
                    return True
                except ValueError:
                    return False
            case _:
                return False

    def update_option(self) -> None:
        """WARNING: DEPRECATED BY NEW VERSION OF settings_menu\n
        Prompt the user to update a single config option. Update the option and save.
        """
        print('-' * (shutil.get_terminal_size().columns - 1))  # Horizontal line (cosmetic)
        section, option, value = "", "", ""

        while section not in self.config.sections():
            section = input("Section: ")
        while option not in self.config[section]:
            option = input("Option Name: ")
        while not self.is_valid_option_value(option, value):
            value = input("Updated Value: ")

        self.set(section, option, value, save=True)

    def settings_menu(self) -> None:
        """Prompt the user with menus for viewing and editing the current config from the console."""
        while True:  # Section selection
            # Select from list of config sections (or exit settings menu)
            section_options = self.config.sections()
            section_options.append("[MAIN MENU]")
            selected_section_index = Menu.menu_prompt(section_options, title="SETTINGS")

            if selected_section_index == len(section_options) - 1:
                return None  # Exit settings menu
            selected_section = section_options[selected_section_index]

            while True:  # Option selection
                # Select from list of section options (or return to section selection)
                section_title = f"SETTINGS > {selected_section}"
                item_options = []
                for key, value in self.config.items(selected_section):
                    item_options.append(f"{key} = {value}")
                item_options.append('[GO BACK]')

                selected_item_index = Menu.menu_prompt(item_options, title=section_title)

                if selected_item_index == len(item_options) - 1:
                    break
                selected_item = item_options[selected_item_index].split('=')[0].strip()  # Parse option name

                # Prompt to update selected item
                item_prompt = selected_item + ' = '
                updated_item_value = None
                print()  # Cosmetic padding
                while not self.is_valid_option_value(selected_item, updated_item_value):
                    updated_item_value = Menu.input_prompt(item_prompt)
                self.set(selected_section, selected_item, updated_item_value, save=True)
                Menu.clear_lines(1)  # Clear padding
