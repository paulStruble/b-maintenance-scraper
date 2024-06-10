import os
import shutil
import zipfile
from pathlib import Path
import requests
import platform
import sys
from Menu import Menu
from Config import Config


class SetupUtils:
    _chrome_for_testing_url = "https://googlechromelabs.github.io/chrome-for-testing/"
    _last_known_good_versions_with_downloads = "last-known-good-versions-with-downloads.json"
    _known_good_versions_with_downloads = "known-good-versions-with-downloads.json"
    _browser_path = Path.cwd() / 'Browser'
    _profiles_path = Path.cwd() / 'Profiles'

    @staticmethod
    def get_platform() -> str:
        """Automatically detect the user's current platform (operating system).

        Prompt the user to manually select platform if the detected platform is incompatible.

        Returns:
            User's current platform
        """
        system = platform.system()
        machine = platform.machine()
        is_64bits = sys.maxsize > 2 ** 32

        if system == "Windows":
            if is_64bits:
                return "win64"
            else:
                return "win32"
        elif system == "Darwin":
            if machine == "x86_64":
                return "mac-x64"
            elif machine == "arm64":
                return "mac-arm64"
        elif system == "Linux":
            if is_64bits:
                return "linux64"

        #  Unsupported/undetected: manual input
        else:
            options = ["linux64",
                       "mac-arm64",
                       "mac-x64",
                       "win32",
                       "win64"]

            selected_option = Menu.menu_prompt(options, title="Platform detection failed or platform not supported.\n"
                                                              "Please manually select a supported platform from the "
                                                              "list below:")

            return options[selected_option]

    @staticmethod
    def get_download_link(item: str, version: str, user_platform: str) -> str:
        """Fetches the download link for specified version of the given item.

        Args:
            item: The download link to fetch (e.g. 'chrome', 'chromedriver', etc.)
            version: Version number of the item to download
            user_platform: Current user platform (operating system)

        Returns:
            Download link for specified version of the given item

        Raises:
            ValueError: If the version is not supported
        """
        print(f"Fetching download link for [{item}] version [{version}] on [{user_platform}] ...")
        endpoint = SetupUtils._chrome_for_testing_url + SetupUtils._known_good_versions_with_downloads
        response = requests.get(endpoint)
        response.raise_for_status()
        versions_json = response.json()  # JSON object of all latest versions

        # Find matching version and return
        for curr_version in versions_json['versions']:
            if curr_version['version'] == version:
                for download in curr_version['downloads'][item]:
                    if download['platform'] == user_platform:
                        url = download['url']
                        print(f"Download link for [{item}] version [{version}]: {url}")
                        return url

        raise ValueError(f"Failed to find download link for [{item}] version [{version}] on [{user_platform}].")

    @staticmethod
    def get_latest_download_link(item: str, user_platform: str, channel: str = 'Stable') -> tuple[str, str]:
        """Fetch the version number and download link for the latest version of the given item.

        Args:
            item: The download link to fetch (e.g. 'chrome', 'chromedriver')
            channel: Channel to download (e.g. 'Stable', 'Beta', etc.)
            user_platform: Current user platform (operating system)

        Returns:
            Tuple of (<latest version>, <link to download>)
        """
        print(f"Fetching download link for latest [{channel}] [{user_platform}] version of [{item}] ...")
        endpoint = SetupUtils._chrome_for_testing_url + SetupUtils._last_known_good_versions_with_downloads
        response = requests.get(endpoint)
        response.raise_for_status()
        latest_json = response.json()  # JSON object of all latest versions
        version = latest_json['channels'][channel]['version']
        downloads = latest_json['channels'][channel]['downloads'][item]

        # Return link for specified platform
        for d in downloads:
            if d['platform'] == user_platform:
                url = d['url']
                print(f"Download link for [{item}] version [{version}]: {url}")
                return version, url

    @staticmethod
    def download_browser_items(version: str = None, download_dir: Path = _browser_path, channel: str = None,
                               user_platform: str = None) -> str:
        """Download and unzip latest Chrome and chromedriver versions to the specified directory.

        Args:
            version: Version of items to be downloaded (None for latest version)
            download_dir: Directory to download files to
            channel: Channel to download (e.g. 'Stable', 'Beta', etc.)
            user_platform: Current user platform (operating system)

        Returns:
            Version number of download (e.g. 125-0-6422-78)
        """
        # Download items
        for item in ('chrome', 'chromedriver'):
            if version is None:
                version, url = SetupUtils.get_latest_download_link(item, channel=channel, user_platform=user_platform)
            else:
                url = SetupUtils.get_download_link(item, version, user_platform=user_platform)

            version_dash = version.replace('.', '-')  # Rename version number for filename compatibility

            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                download_file = (download_dir / version_dash).with_suffix('.tmp')  # Construct download file

                print(f"Downloading [{item}] version [{version}] to {download_file} ...")
                # Write response content to local file
                with open(download_file, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                download_file = download_file.rename((download_dir / version_dash).with_suffix('.zip'))  # .zip extension
                print(f"[{item}] version [{version}] download complete.")

                # Unzip file and delete archive
                print(f"Extracting {download_file} ...")
                with zipfile.ZipFile(download_file, 'r') as zip_item:
                    zip_item.extractall(download_dir / version_dash)
                download_file.unlink()
                print(f"Extraction complete.")

        return version_dash

    @staticmethod
    def custom_browser_install_prompt(user_platform):
        """Prompt the user for chrome and chromedriver installation (for a user-specified version of chrome).

        Args:
            user_platform: Current user platform (operating system)
        """
        while True:
            version_in = Menu.input_prompt("Please enter the version number to download and install: ")
            try:
                SetupUtils.download_browser_items(version=version_in, user_platform=user_platform)
                return version_in  # Exit the loop if the version is valid and installation succeeds
            except (ValueError, KeyError) as e:
                print(e)
                endpoint = SetupUtils._chrome_for_testing_url + SetupUtils._known_good_versions_with_downloads
                print(f"Invalid version: {version_in} ... for a list of all supported versions visit: {endpoint}\n"
                      "Ensure version has downloads for both chrome AND chromedriver.")

                # Remove partial versions if present
                version_dash = version_in.replace('.', '-')
                version_dir = SetupUtils._browser_path / version_dash
                if version_dir.exists():
                    try:
                        shutil.rmtree(version_dir)
                        print(f"Directory {version_dir} removed successfully.")
                    except OSError as e:
                        print(f"Error removing directory {version_dir}: {e}")

    @staticmethod
    def browser_install_prompt():
        """Prompt the user for Chrome and chromedriver installation.

        Returns:
            String version number of chrome/chromedriver (e.g. "125-0-6422-78") if the user decides to install Chrome
            and chromedriver through this prompt

            None if the user decides to do a manual installation
        """
        options = ["Stable (recommended)",
                   "Beta",
                   "Dev",
                   "Canary",
                   "Specific Version",
                   "Manual Installation (see readme Section 2.5 for instructions)"]

        title = ("Setup/Install for Chrome and chromedriver:\n"
                 "If a channel is selected, the latest version for the selected channel will be installed.\n"
                 "Select a channel/version to install:")

        user_platform = SetupUtils.get_platform()
        selected_option = Menu.menu_prompt(options, title)
        match selected_option:
            case 0: return SetupUtils.download_browser_items(channel='Stable', user_platform=user_platform)
            case 1: return SetupUtils.download_browser_items(channel='Beta', user_platform=user_platform)
            case 2: return SetupUtils.download_browser_items(channel='Dev', user_platform=user_platform)
            case 3: return SetupUtils.download_browser_items(channel='Canary', user_platform=user_platform)
            case 4: return SetupUtils.custom_browser_install_prompt(user_platform)
            case 5:
                # Manual Installation
                print()  # Cosmetic padding
                print("To manually install Chrome and chromedriver, please see readme section 2.5 for instructions.\n"
                      "Once your manual installation is complete, input \"COMPLETE\" below to continue:\n")
                user_in = ''
                while user_in.lower() != 'complete':
                    user_in = Menu.input_prompt()
                Menu.clear_lines(4)

    @staticmethod
    def first_time_setup(config: Config):
        """Runs a first-time setup to install dependencies.

        Args:
            config: Config object to edit/update as settings are changed
        """
        # Stage 1: Directory Creation
        os.makedirs(SetupUtils._browser_path)  # Make .\Browser\ directory if it doesn't already exist
        os.makedirs(SetupUtils._profiles_path)  # Make .\Profiles\ directory if it doesn't already exist

        # Stage 2: Postgres Setup
        print()
        print("Please set up and connect a PostgreSQL database as explained in readme Section 2.2 before moving forward.\n"
              "Once you have set up and connected your Postgres database, input \"COMPLETE\" below to continue:\n")
        user_in = ''
        database_setup_complete = False  # Ensure b_database_setup_complete is set to 'true' in config
        while user_in.lower() != 'complete' or not database_setup_complete:
            user_in = Menu.input_prompt()
            config.reload()  # Need to reload config if a manual update was made to b_database_setup_complete
            database_setup_complete = config.get('Database', 'b_database_setup_complete')

        config.set('Program-Variables', 'b_first_time_setup_complete', 'true', save=True)
        Menu.clear_lines(4)

        # Stage 3: Install Chrome and chromedriver
        installed_version = SetupUtils.browser_install_prompt()
        user_platform = SetupUtils.get_platform()
        # Write version number and platform to config
        if installed_version is not None:
            config.set('Scraper', 's_chrome_version', installed_version, save=True)
            config.set('Scraper', 's_chrome_platform', user_platform, save=True)
        else:
            config.reload()  # Need to reload config if a manual update was made to s_chrome_version


if __name__ == '__main__':
    SetupUtils.first_time_setup(Config())
