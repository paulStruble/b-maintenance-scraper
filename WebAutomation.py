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
    def select_item(driver: WebDriver, item_value: str) -> None:
        """Select "Work Request" from the maintenance tracking dropdown menu.

        Args:
            driver: Selenium webdriver instance for automated selection.
            item_value: Value of item to be selected from dropdown menu ('WR' for Work Request, 'WO' for Work Order).
        """
        try:  # Wait for the sidebar to load # TODO: move into login_calnet if redundant
            driver.switch_to.default_content()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "botleft")))
        except:
            print("frame 'botleft' could not be found or switched to")

        # Select "Work Request" button
        dropdown_select = Select(driver.find_element(By.XPATH, "//select[@name='Search']"))
        dropdown_select.select_by_value(item_value)

    @staticmethod
    def search_item(driver: WebDriver, query: str) -> None:
        """Search for a work order or work order request in the search box.

        Args:
            driver: Selenium webdriver instance for automated search.
            query: Work order number or work request id.
        """
        search_box = driver.find_element(By.NAME, "WorkOrderNumber")
        search_box.clear()
        search_box.send_keys(query)

        submit_button = driver.find_element(By.XPATH, "//input[@src='images/arrowbutton.gif']")
        submit_button.click()

        driver.switch_to.default_content()
        driver.switch_to.frame("botright")

    @staticmethod
    def find_xpath_helper(driver: WebDriver, xpath: str, wait_time: float = 3.0) -> str | None:
        """Find an element by xpath, convert to string, strip spaces commas.
        NOT intended for use outside WebAutomation.scrape_request()!

        Args:
            driver: Selenium webdriver to find element in.
            xpath: XPath to find element with.
            wait_time: Time to wait (in seconds) for element to load if initial search fails.

        Returns:
            String value of element (commas and spaces are stripped)
        """
        try:
            return WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath))).text.strip(", ")
        except Exception as e:
            print(f"failed to find element at XPATH: '{xpath}':")
            print(e)


    @staticmethod
    def scrape_request(driver: WebDriver, request_id: int) -> WorkOrderRequest:
        """Submit a search for a single work order request.

        Args:
            driver: Selenium webdriver to automate search for.
            request_id: id of the request to search for.

        Returns:
            WorkOrderRequest object containing data about the work request.
        """
        WebAutomation.search_item(driver, str(request_id))

        request = WorkOrderRequest(request_id)

        # Scrape data
        request_room = driver.find_element(By.XPATH, "//tr[3]/td[1]/p/font/b").text
        if request_room.startswith("for "):
            request_room = request_room[4:]
        request.room = request_room
        request.status = WebAutomation.find_xpath_helper(driver, "//tr[3]/td[2]/strong/font")
        request.building = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[2]/td[2]")
        request.tag = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[3]/td[2]")
        request.accept_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[4]/td[2]")
        request.reject_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[5]/td[2]")
        request.reject_reason = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[6]/td[2]")
        request.location = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[2]/td[4]")
        request.item_description = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[3]/td[4]")
        request.work_order_num = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[4]/td[4]")
        request.area_description = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[5]/td[4]")
        request.requested_action = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[8]/td[2]")

        return request

    @staticmethod
    def get_page_layout(driver: WebDriver, order_number: str) -> int:
        """Determine the page layout type of the current work order.
        Work order pages can have one of two different layouts.

        Args:
            driver: Selenium webdriver instance to search with.
            order_number: Work order number to search for.
        Returns:
            1 if the page layout corresponds to the first scrape_order clause
        Raises:
            Exception if the page layout cannot be determined.
        """
        try:
            if WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[6]/td[1]") == 'Facility:':
                return 1
            elif WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[4]/td[1]") == 'Facility:':
                return 2
            else:
                raise Exception(f"Failed to determine page layout for work order [{order_number}]")
        except Exception as e1:
            try:
                if WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[4]/td[1]") == 'Facility:':
                    return 2
                else:
                    raise Exception(f"Failed to determine page layout for work order [{order_number}]")
            except Exception as e2:
                print(f"Failed to determine page layout for work order [{order_number}]:")
                print(e2)

    # TODO: complete implementation
    @staticmethod
    def scrape_order(driver: WebDriver, order_number: str) -> WorkOrder:
        """Submit a search for a single work order.

        Args:
            driver: Selenium webdriver to automate search for.
            order_number: id of the request to search for.

        Returns:
            WorkOrder object containing data about the work order.
        """
        WebAutomation.search_item(driver, order_number)
        order = WorkOrder(order_number)
        order.order_number = order_number

        page_layout = WebAutomation.get_page_layout(driver, order_number)
        # Scrape data
        if page_layout == 1:
            order.facility = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[6]/td[2]")
            order.building = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[7]/td[2]")
            order.location_id = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[8]/td[2]")
            order.priority = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[9]/td[2]")
            order.request_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[10]/td[2]")
            order.schedule_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[11]/td[2]")
            order.work_status = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[12]/td[2]")
            order.date_closed = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[13]/td[2]")
            order.main_charge_account = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[14]/td[2]")
            order.task_code = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[15]/td[2]/font")
            order.reference_number = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[6]/td[4]")
            order.tag_number = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[8]/td[4]")
            order.item_description = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[9]/td[4]")
            order.request_time = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[10]/td[4]")
            order.date_last_posted = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[11]/td[4]")
            order.trade = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[12]/td[4]")
            order.contractor_name = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[13]/td[4]")
            order.est_completion_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[14]/td[4]")
            order.task_description = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[15]/td[4]")
            order.requested_action = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[17]/td[2]")
            order.corrective_action = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[18]/td[2]")
        elif page_layout == 2:
            order.facility = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[4]/td[2]")
            order.building = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[5]/td[2]")
            order.location_id = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[6]/td[2]")
            order.priority = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[7]/td[2]")
            order.request_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[8]/td[2]")
            order.schedule_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[9]/td[2]")
            order.work_status = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[10]/td[2]")
            order.date_closed = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[11]/td[2]")
            order.main_charge_account = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[12]/td[2]")
            order.task_code = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[13]/td[2]")
            order.reference_number = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[4]/td[4]/p")
            order.tag_number = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[6]/td[4]")
            order.item_description = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[7]/td[4]")
            order.request_time = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[8]/td[4]")
            order.date_last_posted = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[9]/td[4]")
            order.trade = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[10]/td[4]")
            order.contractor_name = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[11]/td[4]")
            order.est_completion_date = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[12]/td[4]")
            order.task_description = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[13]/td[4]")
            order.requested_action = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[15]/td[2]")
            order.corrective_action = WebAutomation.find_xpath_helper(driver, "/html/body/table/tbody/tr[16]/td[2]")

        return order
