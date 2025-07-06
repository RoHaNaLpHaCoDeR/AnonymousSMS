import time
import sys
import requests
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# URL of the website
URL = "https://anonymsms.com/"  # Replace with the actual website URL
token = os.environ.get("token")
chat_id = os.environ.get("chat_id")

# Setup Selenium WebDriver to use Brave with automatic download settings
def setup_chrome_selenium():

    Chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Update this path with your Brave installation path
    options = webdriver.ChromeOptions()
    options.binary_location = Chrome_path
    
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_experimental_option("useAutomationExtension", False) 
    driver = webdriver.Chrome(options=options)
    driver.get(URL)  # Open the website
    return driver

# Setup Selenium WebDriver to use chrome with automatic download settings
def setup_selenium():

    chrome_options = Options()
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print("driver = ",driver)
    print("[LOG] Selenium WebDriver setup complete.")
    driver.get(URL)  # Open the website
    return driver

# Function to fetch the latest number
def fetch_latest_number(driver):
    # Find the latest added number
    try:
        # latest_number_tag = driver.find_element(By.CSS_SELECTOR, "p.latest-added__title a")
        latest_number_tag = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.latest-added__title a"))
        )
        latest_number = latest_number_tag.text.strip()
        return latest_number
    except Exception as e:
        print(f"Error fetching latest number: {e}")
        return None

# Function to send a desktop notification
def send_notification(new_number):
    print (f"[LOG] Sending notification for new number: {new_number}")
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': new_number}
    requests.post(url, data=data)

# Main function
def monitor_website():
    driver = setup_selenium()
    previous_number = None

    while True:
        print("Checking for the latest added number...")
        try:
            latest_number = fetch_latest_number(driver)
            print(latest_number)
            if latest_number:
                if previous_number is None:  # First run
                    print(f"Baseline number set to: {latest_number}")
                    previous_number = latest_number
                elif latest_number != previous_number:
                    print(f"New number detected: {latest_number}")
                    send_notification(latest_number)
                    previous_number = latest_number
                else:
                    send_notification(latest_number)
                    print("No new number detected.")
        except Exception as e:
            print(f"Error: {e}")
        driver.refresh()
        # Refresh the page every 1 minutes
        time.sleep(10)  # Wait for 1 minutes before checking again

# Run the script
if __name__ == "__main__":
    monitor_website()