# contains useful functions for Chrome automation using Selenium

class WebAutomation:
    def login_calnet(self, user):
        username = user.getUsername()
        password = user.getPassword()