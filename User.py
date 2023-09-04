# a user with attached login info


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # prompts the user for login credentials and returns a new User object with the same credentials
    @staticmethod
    def login_prompt():
        print('Username:', end=" ")
        new_username = input()
        print('Password:', end=" ")
        new_password = input()
        return User(new_username, new_password)