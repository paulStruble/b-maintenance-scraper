import shutil
from pwinput import pwinput


class User:
    def __init__(self, username, password):
        """A single user with login credentials (username and password).

        Args:
            username: The username of the user.
            password: The password of the user.
        """
        self.username = username
        self.password = password


def login_prompt(hidden: bool = True) -> User:
    """Prompt the user for login credentials.

    Args:
        hidden: Whether to hide the password in the cli as it is being typed.

    Returns:
        A User object with the input credentials.
    """
    print('-' * (shutil.get_terminal_size().columns - 1))  # Horizontal line (cosmetic)
    new_username = input("Username: ")
    if hidden:
        new_password = pwinput(prompt="Password: ")
    else:
        new_password = input("Password: ")
    print('-' * (shutil.get_terminal_size().columns - 1))

    return User(new_username, new_password)
