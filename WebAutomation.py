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
        driver.find_element(By.ID, "submit").click()

        # wait for DUO Mobile confirmation
        print('---CONFIRM LOGIN ON DUO MOBILE---')
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "dont-trust-browser-button"))).click()
        print('---LOGIN CONFIRMED---')

    # selects "Work Request" from the maintenance tracking dropdown menu
    @staticmethod
    def select_request_button(driver):
        # wait for sidebar to load #TODO: move into login_calnet if redundant
        try:
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "botleft")))
        except:
            print("frame 'botleft' could not be found or switched to")

        # select "Work Request"
        dropdown_select = Select(driver.find_element(By.XPATH, "//select[@name='Search']"))
        dropdown_select.select_by_value("WR")

    # searches for a work order request by request number
    @staticmethod
    def search_request(driver, request_number: int):
        return None #TODO: implement
