import subprocess
import sys


def check_and_install_dependencies(path='requirements.txt') -> None:
    """ Automatically install all required packages from the specified requirements file if they are not already
    installed.

    Args:
        path: path to requirements.txt file (optional)
    """
    try:
        import multiprocessing
        from collections import defaultdict
        from MaintenanceDatabase import MaintenanceDatabase
        from Scraper import Scraper
        from Log import Log
        from Config import Config
        from User import User
        from SetupUtils import SetupUtils
        from pathlib import Path
        from Menu import Menu
    except ImportError:
        install_dependencies(path)


def install_dependencies(path='requirements.txt') -> None:
    """ Automatically install all required packages from the specified requirements file.

    Args:
        path: path to requirements.txt file (optional)
    """
    print(f'\nInstalling required packages from {path}:\n')
    try:
        # Open requirements file
        with open(path, 'r') as requirements_file:
            # Read list of required packages.
            packages = requirements_file.read().splitlines()

        # Iterate over each package and install it
        for package in packages:
            print(f"Installing [{package}] ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])  # Install
            print(f"[{package}] installation complete")
        print("All packages installed successfully.")
    except Exception as e:
        print(f"An error occurred while trying to install packages: {e}")
