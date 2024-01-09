# a user with attached login info

from pwinput import pwinput


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # prompts the user for login credentials and returns a new User object with the same credentials
    @staticmethod
    def login_prompt():
        new_username = input("Username: ")
        new_password = pwinput(prompt="Password: ")
        return User(new_username, new_password)

    if __name__ == "__main__":
        login = login_prompt()
        print(f"Username: {login.username}")
        print(f"Password: {login.password}")