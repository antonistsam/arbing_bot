import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

def open_drivers_and_read_arbs():
    # Load environment variables
    email = os.getenv('BETBURGER_EMAIL')
    password = os.getenv('BETBURGER_PASSWORD')

    # Setup Chrome options
    chrome_options = Options()

    # Initialize the main Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    # # Initialize the secondary Chrome drivers
    # stoiximan_driver = webdriver.Chrome(options=chrome_options)
    # stoiximan_driver = webdriver.Chrome(options=chrome_options)

    try:
        # Go to BetBurger login page
        driver.get("https://www.betburger.com/users/sign_in")

        time.sleep(3)

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
        time.sleep(8)

        while True:
            # Navigate to the arbs page
            driver.get('https://www.betburger.com/arbs')

            # Wait for the page to load
            time.sleep(2)

            # Scrape the HTML and read all <li> elements with class 'wrapper arb has-2-bets'
            arb_elements = driver.find_elements(By.CSS_SELECTOR, "li.wrapper.arb.has-2-bets")
            for element in arb_elements:
                # Get the half period information
                period_name_span = element.find_element(By.CSS_SELECTOR, "span.period-name")
                period_spans = period_name_span.find_elements(By.CSS_SELECTOR, "span")
                half_period = period_spans[-1].text if period_spans and period_spans[-1].text.strip() else "null"
                handle_arb_element(element, half_period)
            # Wait for 15 seconds before refreshing
            time.sleep(15)

    except Exception as e:
        print(f"An error occurred: {e}")

    # Note: Do not quit the main driver as per the requirement

def handle_arb_element(element, half_period):
    try:
        # Find the Stoiximan div element within the arb element
        bet_wrappers = element.find_elements(By.CSS_SELECTOR, "div.bet-wrapper")
        for bet_wrapper in bet_wrappers:
            try:
                stoiximan_div = bet_wrapper.find_element(By.XPATH, ".//div[@title='Stoiximan']")
                handle_stoiximan_element(bet_wrapper, half_period)
                break
            except Exception as e:
                # Ignore if Stoiximan element is not found in this bet-wrapper
                continue
    except Exception as e:
        print(f"An error occurred while handling arb element: {e}")

def handle_stoiximan_element(stoiximan_element, half_period):
    try:
        # Get the event name
        copy_input_span = stoiximan_element.find_element(By.CSS_SELECTOR, "span.copy-input")
        
        # Get the next element inside the li element and its text
        event_name_element = copy_input_span.find_element(By.XPATH, "following-sibling::*[1]")
        event_name = event_name_element.text

        # Get the market information
        market_div = stoiximan_element.find_element(By.CSS_SELECTOR, "div.market.all-center")
        last_span = market_div.find_elements(By.CSS_SELECTOR, "span")[-1]
        market_text = last_span.text
        market_text_cleaned = market_text.split('(')[0]  # Exclude the parentheses part
        
        # Get the odds
        odds_span = stoiximan_element.find_element(By.CSS_SELECTOR, "span.coefficient")
        odds_text = odds_span.text


        # Print the extracted data
        print(f"Event Name: {event_name}")
        print(f"Market: {market_text_cleaned}")
        print(f"Odds: {odds_text}")
        print(f"Half Period: {half_period}")

    except Exception as e:
        print(f"An error occurred while handling Stoiximan element: {e}")

if __name__ == "__main__":
    open_drivers_and_read_arbs()
