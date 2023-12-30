from selenium import webdriver
# Import the ConnectionRequest class
from connection_request import ConnectionRequest
import time
import math
import random
import os
import utils
import constants
import config
import credentials
import pickle
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import colorama
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
from langdetect import detect
from googletrans import Translator
import csv
from datetime import datetime
import pyautogui


class AnotherClass:
    def __init__(self):
        self.today_date = datetime.today().strftime('%Y%m%d')
        self.driver = webdriver.Chrome(service=ChromeService(
            ChromeDriverManager().install()), options=utils.chromeBrowserOptions())

        self.driver.get(
            "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")

        try:
            try:
                self.driver.find_element(
                    "id", "username").send_keys(credentials.email)
            except:
                pass
            # time.sleep(2)
            try:
                self.driver.find_element(
                    "id", "password").send_keys(credentials.password)
            except:
                pass
            # time.sleep(2)
            try:
                self.click_using_mouse_move(self.driver.find_element(
                    "xpath", '//button[@type="submit"]'))
            except:
                pass
            time.sleep(10)
        except:
            utils.prRed(
                "                           ❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8.")

    def perform_connection_request(self):
        # Create an instance of the ConnectionRequest class
        urls_to_process = [
            'https://www.linkedin.com/in/julieta-rodriguez-conte-25914a97/',
            'https://www.linkedin.com/in/herreraecarolina/',
            'https://www.linkedin.com/in/romina-sanchez-7aa550244/',
            'https://www.linkedin.com/in/mubasher-k-l-i-o-n-96b77087/',
            'https://www.linkedin.com/in/lorena-benitez-128a3345/',
            'https://www.linkedin.com/in/natalia-arenas-838b811a7/',
            'https://www.linkedin.com/in/veroderosa/',
            'https://www.linkedin.com/in/niahblackman/',
            'https://www.linkedin.com/in/chrissykane/',
            'https://www.linkedin.com/in/nicholekanter/',
            'https://www.linkedin.com/in/treywashington/'
        ]
        connection_request_instance = ConnectionRequest(self.driver)
        for url in urls_to_process:
            self.driver.get(url)
            time.sleep(random.uniform(2, 3))
            connection_request_instance.find_follow_and_connect()

        # Optionally, you can close the webdriver when done
        self.driver.quit()


# Example usage
if __name__ == "__main__":
    another_class_instance = AnotherClass()
    another_class_instance.perform_connection_request()
