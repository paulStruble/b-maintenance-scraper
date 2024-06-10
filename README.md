# UCB Maintenance Database Scraper

## 1: Overview

This tool is used to automatically scrape maintenance data from UC Berkeley's maintenance request website 
(maintenance.housing.berkeley.edu) to a local PostgreSQL database. *The maintenance site (and consequently this tool)
are only accessible to individuals with a valid Calnet ID.*

### 1.1: The UC Berkeley Maintenance Website

UC Berkeley students or staff submit **maintenance requests** through the website. When a request is submitted, the
requester is given a unique request ID (ex. 347929) that can be used to look up the status and details of the request on
the site. Requests can be searched for and viewed by any user and are not deleted after they are complete (however the
status of the request will be updated on the site). Additionally, request IDs are simply sequential integers
(i.e. request 347929 is preceded by request 347928 and followed by request 347930). This means, by using this scraper,
any user can reconstruct the entire request database locally by scraping every request for IDs 1, 2, 3, 4, ...
The first available request ID is actually 54 (requests 1 through 53 are inaccessible or nonexistent for some reason),
and as of June 2024, the last available request ID is somewhere around 460000. These requests span back as far as 2007,
and multiple new requests are made daily.

Also accessible through the maintenance site are **work orders**. Work orders are the actual tasks distributed to
maintenance staff around campus. They contain additional information about the maintenance task they are related to.
Each maintenance request (also called a work order request) is associated with a single work order. Note however that
not all work orders have a corresponding work order request (work orders can probably be made internally through a
different system). This means that there are significantly more work orders than requests; as of June 2024 there are
about 740,000 work orders compared to about 460,000 requests. Each work order is uniquely identified by an order number
(ex. HM-546834 which corresponds to request 347929). All order numbers start with the prefix "HM-" followed by an
integer. These integers are sequential just as request IDs are. Note that the integer part of a request is not the same
as the integer part of its corresponding work order.

Orders and requests contain information including details about the location of the issue, time/date details about
when requests/orders were opened and closed, the priority of the issue, written descriptions of the "requested action"
(issue) and "corrective action" (fix), and a few other datapoints associated with the order/request.

### 1.2: bWork

bWork is written completely in Python and uses Selenium paired with the Google Chrome webdriver (chromedriver) to run
automated browser windows that search and scrape both requests and orders. psycopg2 is then used to send scraped data to
a (local) PostgreSQL database. As of June 2024, **only Windows is supported, but Mac/Linux support should be possible 
without much modification** (I had originally planned to support Mac, so most features should only require minor changes
to work on Mac and probably Linux). The webscraper is designed to scrape a range of request IDs or order numbers. The
user can specify the number of parallel processes (through settings/config) for the scraper to run over. Request IDs or
order numbers will be uniformly distributed across all parallel processes. This significantly increases the throughput 
of the scraper. Further details about bWork function, usage, and source code structure can be found throughout this 
readme.



## 2: Setup & Installation:

Program dependencies are grouped into 4 categories: Python, PostgreSQL, browser utilities (Chrome and chromedriver), 
and Python packages. Python and PostgreSQL will need to be installed and set up manually as described below. Browser 
utilities and Python packages can be installed via the first-time setup that will automatically run when Driver.py is 
run for the first time.

### 2.1: Python

The first dependency you will need to (manually) install is Python. You can download the Python installer form the
official Python website (https://www.python.org/downloads/). Because bWork was written using Python 3.12, you will want 
to download and install a version at least as recent as 3.12 (newer versions will be fine) and complete the installation 
according to instructions provided on o. Python will be used to run the scraper from the Driver.py python file once all
setup in Section 2 is complete. Once Python is installed, move on to Section 2.2.

### 2.2: PostgreSQL Setup

Next, you will need to install PostgreSQL and set up a PostgreSQL database. This database will be used to store data
scraped from the maintenance website. Follow the instructions on the official PostgreSQL website
(https://www.postgresql.org/download/) to download and install PostgreSQL.

Once installation and setup of a PostgreSQL server are complete, you will need to update the bWork's configuration file
(config.ini) so that the scraper can send data to your PostgreSQL database. Open config.ini with any text editor and
update the options in the [Database] section to the appropriate values corresponding to your PostgreSQL server. See 
Section 4 for details about editing the config. Note that if you used the default settings when setting up your 
PostgreSQL server, the config settings may already match your server's settings.

**NOTE: Once PostgreSQL setup is complete, make sure that b_database_setup_complete is set to true in the config.**

### 2.3: Database Management System (Recommended)

**NOTE: This section is recommended but not required.**

Having a database management system (DBMS) to view and work with the data in your PostgreSQL database is recommended
however this is solely for user convenience when working with data scraped from the maintenance site. Your installation
of PostgreSQL likely also installed pgAdmin which is the DBMS shipped with PostgreSQL. Any database administration tool
compatible with PostgreSQL will work fine; my personal recommendation would be dbeaver which is a free DBMS compatible
with PostgreSQL and various other SQL databases. If you are interested in using dbeaver, it can be downloaded from the
official dbeaver website (https://dbeaver.io/download/).

### 2.4: First-Run Setup

Now that Python and PostgreSQL are installed, bWork can be run for the first time to complete first-time setup. To 
launch bWork, open a command line (ex. Command Prompt) and navigate to the \bWork\ directory. Open the bWork driver with
Python by executing the command "python Driver.py" (try "python3 Driver.py" if this doesn't work). This will launch the
first-time setup.

bWork will first automatically install all Python package dependencies. Please wait while packages are installed.

Next, you will be prompted to connect a PostgreSQL database. You completed this setup already in Section 2.2. Ensure
that b_database_setup_complete is set to true in the config. Input "COMPLETE" (without quotes) to continue to the next
step.

You will first be prompted to install the necessary browser utilities: the Google Chrome for Testing web browser and the
chromedriver webdriver for use with Selenium (these will be used by the webscraper for browser automation). Chrome and
chromedriver must be the same version in order to guarantee compatibility with one another. Select a channel of Chrome/
chromedriver to install (select "Stable" if you aren't sure). The corresponding versions of Chrome and chromedriver
will be installed.

* "Stable", "Beta", "Dev", and "Canary" will each install the latest release of both Chrome and chromedriver for their 
respective channels. Selecting "Stable" is the recommended option for this step.
* "Specific Version" will prompt you to input a specific version number. A complete JSON list of all versions can be
found at the Chrome for Testing /known-good-versions-with-downloads endpoint
(https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json). When selecting a
version, ensure that there are downloads available for both "chrome" and "chromedriver". Input the version number as it
appears at the JSON endpoint (ex. "121.0.6140.0" without the quotes).
* "Manual Installation" simply skips the Chrome and chromedriver installation. This allows you to use any custom Chrome
binary and chromedriver executable. To provide bWork with your own versions of Chrome and chromedriver, follow the 
instructions in Section 2.5.

Once browser utility installation is complete, the first-time setup will be finished. You should see prompt for a
username (Calnet ID) confirming that setup is complete and that bWork is now running. Input your Calnet login 
credentials. See Section 3 for more information about navigating and using the program.

**NOTE: Try selecting "Specific Version" -> "125.0.6422.141" for browser installation if more recent versions aren't
working. This is the last version I have tested which was working as of June 2024.**

**NOTE: The bWork driver will not automatically run first-time setup again after it has been completed once. If you 
would like to run it again (such as to install new browser utilities), you can change the b_first_time_setup_complete 
option to "false" (without quotes) in the config under the [Program-Variables] section.**

### 2.5: Manual Browser Utility Installation (Optional)

If you would like to use a custom Chrome binary or custom chromedriver executable, this section will explain how. bWork 
will only be compatible with Chrome binaries and chromedriver executables that are directly compatible with Selenium.

First, navigate to the \bWork\ parent directory. Open the \bWork\Browser\ directory. Create a new directory within the 
\bWork\Browser\ directory with the name of the version of chrome you would like to use. Ensure the name does not contain 
any "." characters. Note that the name can technically be anything as you will create a reference to it in the config.
Within the version directory, create two new directories called "chrome-win64" and "chromedriver-win64" (both without
quotes, replace 64 with 32 if you are on a 32-bit operating system). These exact names are necessary. Move the Chrome
binary to \bWork\Browser\<version number>\chrome-win64\ and the chromedriver.exe executable into 
\bWork\Browser\<version number>\chromedriver-win64\. To direct bWork to use these versions, open config.ini, navigate to
the [Scraper] section, set the s_chrome_version option to the version number you used for your directory name, and set
s_chrome_platform to win64 (or win32 for a 32-bit Windows).

Ensure that chrome.exe is found at \bWork\Browser\<version number>\chrome-win64\chrome.exe

Ensure that chromedriver.xe is found at \bWork\Browser\<version number>\chromedriver-win64\chromedriver.exe

**NOTE: To see a working example of the file structure for a Chrome binary and chromedriver executable, you can use
the Driver.py first-time setup covered in Section 2.4 to automatically install some version of chrome. This will install
both the Chrome binary and chromedriver executable to the proper locations in \bWork\Browser\ which can be a useful 
reference if the instructions are unclear.**

## 3: Using bWork

### 3.1: Launching bWork

To launch the program, open a command line (ex. Command Prompt), and navigate to the \bWork\ directory. Open Driver.py
with python by running "python Driver.py" (make sure Python is in your PATH). This will launch bWork in the command line
and prompt you for your Calnet login. If your Calnet login is valid, you will be brought to the main menu. From the main
menu you can choose to scrape a range of work requests, scrape a range of work orders, change settings, or exit the
program. Menus can be navigated with the UP/DOWN arrow keys, and a menu option can be selected with the ENTER key.

Scraping a range of work requests or work orders both function effectively the same. You will be prompted to input start
and end request IDs or work order numbers, respectively. Start values are inclusive; end values are exclusive. If this
is the first time using the scraper, you will also be prompted to input how many parallel process to run. This is the
number of webscrapers that will run in parallel to scrape the entire range you input. It is recommended to choose this
number based on the number of cores and threads on your CPU to scrape large numbers of requests/orders efficiently.

Settings are discussed below in Section 4.

## 4: Settings & Config

A number of configurable program options can be viewed and edited from the settings menu (accessible from the main menu)
or directly through the config.ini file. This section will give an overview of each option. The settings menu can be
navigated with the UP/DOWN arrow keys and the ENTER key from within the program. Note that some options may require 
bWork to be restarted to take effect.

### 4.1: Structure

The config is split into sections with titles denoted in [Brackets]. Under each section are options. Each option name
begins with a single-character datatype tag followed by an underscore. This datatype tag denotes the expected datatype
of the option and affects how the option will be parsed. The value of each option is to the right of the option's name,
and option names are separated from their values by " = " (without quotes). This format must be followed in order
for options to be parsed correctly. When changing options from the settings menu, only valid values will be accepted
(which vary depending on the datatype of the option).

Datatype tags are as follows:
* b - boolean - value must be either "true" or "false" (without quotes), case-sensitive
* s - string - value can be any valid string, no quotes needed at start or finish
* i - integer - value can be any valid 32-bit integer

**NOTE: Do not edit the config.ini file while bWork is running. Either edit it while the program is closed or use 
the settings menu from within the program.**

### 4.2: Options

Database
* s_host - PostgreSQL host address
* s_name - PostgreSQL database name
* s_user - PostgreSQL database username
* s_password - PostgreSQL database password (ignored if b_input_database_password_at_runtime is true)
* i_port - PostgreSQL database port
* b_input_database_password_at_runtime - true if the PostgreSQL password should be input at runtime (instead of using
s_password)
* b_database_setup_complete - true to pass PostgreSQL step of first-time setup (Section 2.4)

Scraper
* s_chrome_version - the currently-enabled version of Chrome/chromedriver (name of the directory in \bWork\Browser\ to search 
for Chrome/chromedriver)
* s_chrome_platform - the current user platform (either "win32" or "win64" without quotes)
* b_primary_scraper_headless - false if the primary scraper that launches with bWork should be visible (true for 
hidden)
* b_parallel_scrapers_headless - false if the parallel scrapers used to scrape a range of requests/orders should be
visible (true for hidden)
* i_parallel_process_count - number of processes to run in parallel when scraping orders/requests 

Options
* b_password_inputs_hidden - true to hide all password inputs as they are being typed in the command line

Program-Variables
* b_first_time_setup_complete - true if the first-time setup (Section 2.4) is complete, false if it should run the next
time Driver.py is launched
* s_work_order_prefix - the prefix to be appended before each work order number ("HM-" by default) (see paragraph 2 of
Section 1.1 for more information)

## 5: Table Column Descriptions

Below are descriptions of the data contained in each column. Note that these descriptions are not official,
comprehensive, or guaranteed to always be correct; they are just what I could gather from quickly scanning through the
data. Most column titles are self-explanatory. Note that some columns do not contain any meaningful data (such as
columns with all NULL values or strictly duplicate data).

Also, datatypes are somewhat arbitrary. Most of the order datatypes are even just set to TEXT as I didn't feel a need to
make them much more specific (and was not sure what would be most appropriate when first deciding datatypes). Datatypes
and other table properties can of course be changed after scraping through use of SQL statements or simplpy through a
DBMS. As far as I am aware, the set datatypes should not cause any information to be omitted when scraping data.

### 5.1: request Table

* id - INT - request ID for this request (ex. 199103)
* room - VARCHAR(20) - the code corresponding to the specific room of the request
* status - VARCHAR(20) - the current status of the request (at the time of scraping): Accepted, Rejected, or Pending
* building - VARCHAR(50) - the name of building of the request
* tag - VARCHAR(50) - special tag for specific type of request
* accept_date - TIMESTAMP - date the request was accepted (if accepted) as a work order
* reject_date - TIMESTAMP - date the request was rejected (if rejected)
* reject_reason - TEXT - reason the request was rejected (if rejected)
* location - VARCHAR(50) - usually NULL (missing), sometimes duplicate of room (not NULL if and only if item_description
is not NULL)
* item_description TEXT - usually NULL (missing), sometimes the name of a specific appliance or vehicle. Used to
identify specific appliances/vehicles that need to be repaired, replaced, etc.
* work_order_num - VARCHAR(25) - the work order number of the work order created for this request (if accepted)
* area_description - VARCHAR(50) - readable text description of the room/area of the request
* requested_action - TEXT - written description of the requested maintenance action (fix) as written by the user who
made the request

### 5.2: order Table

* order_number - VARCHAR(15) - order number for this work order (ex. HM-209805)
* facility - VARCHAR(50) - always RSSP (acronym for Residential & Student Service Program)
* building - VARCHAR(50) - the name of building of the order
* location_id - VARCHAR(20) - code corresponding to the order's location
* priority - TEXT - urgency of the order, 1 to 5 scale (value is one of: 1 Routine, 2 Interest, 3 Deferred, 4 Urgent,
5 Emerg.)
* request_date - TEXT - date the original request was made
* schedule_date - TEXT - date the order was scheduled to be completed
* work_status - TEXT - usually NULL, sometimes the status of the request (canceled, Assigned not started, etc.), not
always accurate
* date_closed - TEXT - date the order was closed as completed
* main_charge_account - TEXT - NULL
* task_code - TEXT - appears to be a unique code corresponding to the specific task to be completed
* reference_number - TEXT - request id of work order request (some errors, likely manually-input by a human)
* tag_number - TEXT - usually same as tag, unique code related directly to tag
* item_description - TEXT - usually same as request item description, sometimes more specific (likely from item being
better specified after the original work request was created)
* request_time - TEXT - time the request for the order was made (may not be the same as the time the work request was
made, I am unsure)
* date_last_posted - TEXT - NULL
* trade - TEXT - category of the (work) trade assigned to this order
* contractor_name - TEXT - NULL
* est_completion_date - TEXT - usually NULL, sometimes the estimated date for the order to be completed
* task_description - TEXT - brief description of work to be completed / the thing to be fixed (ex. Bathtub/Shower, Key,
Bed Bugs, etc.)
* requested_action - TEXT - usually same as request's requested action, sometimes adds additional details
* corrective_action - TEXT - written description of the corrective action (fix) taken by maintenance as written by some
human (I assume written by the worker who completed the fix)
