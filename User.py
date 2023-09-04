# a user with attached login info

from getpass import getpass


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # prompts the user for login credentials and returns a new User object with the same credentials
    @staticmethod
    def login_prompt():
        print('Username: ')
        new_username = input()
        new_password = getpass()
        return User(new_username, new_password)