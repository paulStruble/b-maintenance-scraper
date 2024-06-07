from pwinput import pwinput

from Menu import Menu


class User:
    def __init__(self, username: str, password: str):
        """A single user with login credentials (username and password).

        Args:
            username: The username of the user
            password: The password of the user
        """
        self.username = username
        self.password = password


def login_prompt(hidden: bool = True) -> User:
    """Prompt the user to input login credentials.

    Args:
        hidden: True to hide the password in the cli as it is being typed

    Returns:
        A User object with the input credentials
    """
    new_username = input("Username: ")
    if hidden:
        new_password = pwinput(prompt="Password: ")
    else:
        new_password = input("Password: ")
    Menu.clear_lines(2)

    return User(new_username, new_password)
