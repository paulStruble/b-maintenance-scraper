# a user with attached login info
import getpass


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # prompts the user for login credentials and returns a new User object with the same credentials
    @staticmethod
    def login_prompt():
        new_username = input("Username: ")
        new_password = getpass.getpass("Password: ")
        return User(new_username, new_password)