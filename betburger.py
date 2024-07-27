import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv

load_dotenv()

def handle_betburger():
    # Load environment variables
    email = os.getenv('BETBURGER_EMAIL')
    password = os.getenv('BETBURGER_PASSWORD')

    # Setup Chrome options
    chrome_options = Options()

    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Go to BetBurger login page
        driver.get("https://www.betburger.com/users/sign_in")

        # Find the email input element and type the email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='example@example.com']"))
        )
        email_input.click()
        email_input.send_keys(email)

        # Find the password input element and type the password
        password_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")
        password_input.click()
        password_input.send_keys(password)

        # Find the submit button and click it
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Wait until the page loads and displays the elements
        time.sleep(2)  # This can be replaced with more sophisticated waits if needed

        # Navigate to the arbs page
        driver.get('https://www.betburger.com/arbs')

        time.sleep(2)

        # Scrape the HTML and read all <li> elements with class 'wrapper arb has-2-bets'
        arb_elements = driver.find_elements(By.CSS_SELECTOR, "li.wrapper.arb.has-2-bets")
        for element in arb_elements:
            handle_arb_element(element)  # Call the function to handle each element

    finally:
        driver.quit()

def handle_arb_element(element):
    try:
        # Get the span element with class 'copy-input'
        copy_input_span = element.find_element(By.CSS_SELECTOR, "span.copy-input")

        # Get the next element inside the li element and its text
        next_element = copy_input_span.find_element(By.XPATH, "following-sibling::*[1]")
        next_element_text = next_element.text
       
        print(f"Next Element Text: {next_element_text}")


    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    handle_betburger()
