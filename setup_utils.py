from datetime import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time


def create_driver():
    """Creates and returns a Selenium WebDriver instance."""

    chrome_driver_path = "C:\Program Files (x86)\ChromeDriver\chromedriver-win64\chromedriver.exe"

    driver = webdriver.Chrome(service=Service(chrome_driver_path))
    return driver

def login_to_joomla(driver):
    """Logs into the Joomla site using the provided driver."""

    username = os.getenv('JOOMLA_USER')
    password = os.getenv('JOOMLA_PASS')
    joomla_url = "https://bodyandsoulinternational.com/administrator/"
    driver.get(joomla_url)

    try:
        # Wait for the login form
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "mod-login-username")))

        # Enter username
        user_input = driver.find_element(By.ID, "mod-login-username")
        user_input.send_keys(username)

        # Enter password
        pass_input = driver.find_element(By.ID, "mod-login-password")
        pass_input.send_keys(password)

        # Submit the login form
        pass_input.send_keys(Keys.RETURN)

        # Optional: wait and check that the login was successful
        WebDriverWait(driver, 10).until(lambda d: "index.php" in d.current_url)

        print("✅ Logged in successfully.")

    except Exception as e:
        print("❌ Login failed:", e)






