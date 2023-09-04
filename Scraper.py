from bs4 import beatifulsoup4
import requests
from selenium import webdriver

class Scraper:
    ucb_maintenance_url = 'https://maintenance.housing.berkeley.edu'

    driver = webdriver.Chrome()

    driver.get(ucb_maintenance_url)
