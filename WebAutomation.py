# contains useful functions for Chrome automation using Selenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebAutomation:
    # logs in to CalNet using credentials from prompt
    @staticmethod
    def login_calnet(driver, user):
        url = "https://auth.berkeley.edu/cas/login?service=https://maintenance.housing.berkeley.edu/cas2/login.aspx"

        # prompt for CalNet login credentials
        driver.get(url)
        driver.find_element(By.ID, "username").send_keys(user.username)
        driver.find_element(By.ID, "password").send_keys(user.password)

        # click signin button
        driver.find_element(By.ID, "submit").click()

        # wait for DUO Mobile confirmation
        print('---CONFIRM LOGIN ON DUO MOBILE---')
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "dont-trust-browser-button")))
        print('---LOGIN CONFIRMED---')
