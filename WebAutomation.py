# contains useful functions for Chrome automation using Selenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class WebAutomation:
    # logs in to CalNet with the given [driver] as [user]
    @staticmethod
    def login_calnet(driver, user):
        url = "https://auth.berkeley.edu/cas/login?service=https://maintenance.housing.berkeley.edu/cas2/login.aspx"

        # prompt for CalNet login credentials
        driver.get(url)
        driver.find_element(By.ID, "username").send_keys(user.username)
        driver.find_element(By.ID, "password").send_keys(user.password)

        # click signin button
        driver.find_element(By. ID, "submit").click()

        # wait for DUO Mobile confirmation
        print('---CONFIRM LOGIN ON DUO MOBILE---')
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "dont-trust-browser-button"))).click()
        print('---LOGIN CONFIRMED---')

    # selects "Work Request" from the maintenance tracking dropdown menu
    @staticmethod
    def select_request_button(driver):
        driver.switch_to.frame(1)

        dropdown_select = Select(driver.find_element(By.XPATH, "//select[@name='Search']"))
        dropdown_select.select_by_value("WR")
