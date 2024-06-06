import shutil
import sys

import readchar


class Menu:
    @staticmethod
    def clear_lines(num_lines: int) -> None:
        """Clears the previous <num_lines> lines of text from the console/terminal.

        Args:
            num_lines (int): Number of lines to clear.
        """
        for _ in range(num_lines):
            sys.stdout.write('\033[F')  # Cursor up one line
            sys.stdout.write('\033[K')  # Clear the line
        sys.stdout.flush()


    @staticmethod
    def print_menu(options: list[str], selected_index: int, previous_lines: int = 0, title: str = None) -> int:
        """Prints a menu to the screen with a cursor '>' next to the currently-selected option.
        (Helper function for menu_prompt)

        Args:
            options: The list of options to display.
            selected_index: The index of currently-selected option.
            previous_lines: The number of lines printed for the previous menu (this many lines will be overriden).
            title: The title of the menu.
        Returns:
            The number of lines printed.
        """
        # Move the cursor up to overwrite the previous menu output
        if previous_lines > 0:
            print(f"\033[{previous_lines}A", end='')

        print()  # Padding

        # Print menu title.
        if title is not None:
            print(title, '\n')

        # Print the menu items
        for i, option in enumerate(options):
            if i == selected_index:
                print(f"| > {option}")
            else:
                print(f"|   {option}")

        print()  # Padding

        # Return the number of lines printed
        if title is not None:
            return len(options) + 4  # 4 lines of padding.
        else:
            return len(options) + 2  # 2 lines of padding.

    # TODO: if an option spans multiple lines, the menu is not fully cleared each loop
    @staticmethod
    def menu_prompt(options: list[str], title: str = None, clear: bool = True) -> int:
        """Renders a basic menu with a list of options to a terminal/command line and allows the user to navigate and
        choose from the list with the keyboard.

        Args:
            options: The list of options to render.
            title: The title of the menu.
            clear: True to clear menu from screen after complete, False to leave on screen.
        Returns:
            The index of the menu option selected by the user (0-indexed).
        """
        selected_index = 0
        previous_lines = 0

        # Menu loop
        while True:
            previous_lines = Menu.print_menu(options, selected_index, previous_lines, title)  # Render menu
            key_in = readchar.readkey()  # Get input

            if key_in == readchar.key.UP and selected_index > 0:
                selected_index -= 1  # Move cursor UP.
            elif key_in == readchar.key.DOWN and selected_index < len(options) - 1:
                selected_index += 1  # Move cursor DOWN.
            elif key_in == readchar.key.ENTER or key_in == '\n':
                if clear:
                    Menu.clear_lines(previous_lines)  # Clear menu from screen.
                return selected_index  # Select option.

    @staticmethod
    def input_prompt(label: str = "Input: ") -> str:
        """Prompt the user for input and clear the prompt from the terminal/command line after completion.

        Args:
            label: The text to display for the prompt.
        Returns:
            The string input entered by the user.
        """
        user_in = input(label)
        Menu.clear_lines(1)
        return user_in



if __name__ == '__main__':
    menu_options_1 = ["Option 1", "Option 2", "Option 3", "Option 4"]
    menu_options_2 = ["Option 5", "Option 6", "Option 7", "Option 8"]
    menu_options_3 = ["Option 9", "Option 10", "Option 11", "Option 12"]
    print(f"Selected option [{Menu.menu_prompt(menu_options_1, 'Menu 1', clear=False)}]")
    print(f"Selected option [{Menu.menu_prompt(menu_options_2)}]")
    print(f"Selected option [{Menu.menu_prompt(menu_options_3, 'Menu 3')}]")
