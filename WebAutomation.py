from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from User import User
from WorkOrder import WorkOrder
from WorkOrderRequest import WorkOrderRequest


class WebAutomation:
    """Contains utility functions for Chrome automation using Selenium."""

    @staticmethod
    def login_calnet(driver: WebDriver, user: User, duo_wait_time: int = 5) -> None:
        """Complete the Calnet login and Duo Mobile confirmation for UC Berkeley's maintenance site.

        Args:
            driver: Selenium webdriver instance for automated login.
            user: Calnet user for login.
            duo_wait_time: Time (in seconds) to wait for the Duo Mobile confirmation screen to load after logging in.
        """
        url = "https://auth.berkeley.edu/cas/login?service=https://maintenance.housing.berkeley.edu/cas2/login.aspx"
        driver.get(url)

        if driver.title == "CAS - Central Authentication Service":
            # Prompt user for Calnet login credentials
            driver.find_element(By.ID, "username").send_keys(user.username)
            driver.find_element(By.ID, "password").send_keys(user.password)

            # Click signin button
            driver.find_element(By.ID, "submit").click()

        try:  # Duo Mobile confirmation is bypassed (already completed in a previous session)
            WebDriverWait(driver, duo_wait_time).until(EC.title_is("TMA iServiceDesk - University of "
                                                                   "California-Berkeley"))
        except:  # Wait for user to confirm login on the Duo Mobile app
            if driver.title == "Duo Security":
                print('---CONFIRM LOGIN ON DUO MOBILE---')
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "trust-browser-button"))).click()
                print('---LOGIN CONFIRMED---')

    @staticmethod
    def select_request_button(driver: WebDriver) -> None:
        """Select "Work Request" from the maintenance tracking dropdown menu.

        Args:
            driver: Selenium webdriver instance for automated selection.
        """
        try:  # Wait for the sidebar to load # TODO: move into login_calnet if redundant
            driver.switch_to.default_content()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "botleft")))
        except:
            print("frame 'botleft' could not be found or switched to")

        # Select "Work Request" button
        dropdown_select = Select(driver.find_element(By.XPATH, "//select[@name='Search']"))
        dropdown_select.select_by_value("WR")

    @staticmethod
    def search_request(driver: WebDriver, request_id: int) -> WORequest:
        """Submit a search for a single work order request.

        Args:
            driver: Selenium webdriver to automate search for.
            request_id: id of the request to search for.

        Returns:
            WORequest object containing data about the work request.
        """
        search_box = driver.find_element(By.NAME, "WorkOrderNumber")
        search_box.clear()
        search_box.send_keys(str(request_id))

        submit_button = driver.find_element(By.XPATH, "//input[@src='images/arrowbutton.gif']")
        submit_button.click()

        driver.switch_to.default_content()
        driver.switch_to.frame("botright")

        def find(xpath):
            try:
                return driver.find_element(By.XPATH, xpath).text.strip(", ")
            except:
                print(f"failed to find element at XPATH: '{xpath}'")
                return None

        request = WORequest(request_id)

        # Scrape data
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
