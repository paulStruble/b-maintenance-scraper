# contains useful functions for Chrome automation using Selenium
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from WORequest import WORequest


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
            driver.switch_to.default_content()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "botleft")))
        except:
            print("frame 'botleft' could not be found or switched to")

        # select "Work Request"
        dropdown_select = Select(driver.find_element(By.XPATH, "//select[@name='Search']"))
        dropdown_select.select_by_value("WR")

    # searches for a work order request by request number
    # returns a WORequest object
    @staticmethod
    def search_request(driver, request_number: int) -> WORequest:
        # search for request by number
        search_box = driver.find_element(By.NAME, "WorkOrderNumber")
        search_box.clear()
        search_box.send_keys(str(request_number))

        submit_button = driver.find_element(By.XPATH, "//input[@src='images/arrowbutton.gif']")
        submit_button.click()

        # scrape data and create request
        driver.switch_to.default_content()
        driver.switch_to.frame("botright")

        def find(xpath) -> str:
            try:
                return driver.find_element(By.XPATH, xpath).text.strip(", ")
            except:
                print(f"failed to find element at XPATH: '{xpath}'")
                return None

        request = WORequest(request_number)

        request_room = driver.find_element(By.XPATH, "//tr[3]/td[1]/p/font/b").text
        if request_room.startswith("for "):
            request_room = request_room[4:]
        request.room = request_room
        request.status = find("//tr[3]/td[2]/strong/font")
        request.building = find("/html/body/table/tbody/tr[2]/td[2]")
        request.tag = find("/html/body/table/tbody/tr[3]/td[2]")
        request.accept_date = find("/html/body/table/tbody/tr[4]/td[2]")
        request.reject_date = find("/html/body/table/tbody/tr[5]/td[2]")
        request.reject_reason = find("/html/body/table/tbody/tr[6]/td[2]")
        request.location = find("/html/body/table/tbody/tr[2]/td[4]")
        request.item_description = find("/html/body/table/tbody/tr[3]/td[4]")
        request.work_order_num = find("/html/body/table/tbody/tr[4]/td[4]")
        request.area_description = find("/html/body/table/tbody/tr[5]/td[4]")
        request.requested_action = find("/html/body/table/tbody/tr[8]/td[2]")

        return request

        # TODO: complete implementation
