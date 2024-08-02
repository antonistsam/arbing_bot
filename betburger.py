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
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    # Initialize the main Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

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
                handle_arb_element(element, half_period, driver)
            # Wait for 15 seconds before refreshing
            time.sleep(15)

    except Exception as e:
        print(f"An error occurred: {e}")

    # Note: Do not quit the main driver as per the requirement

def handle_arb_element(element, half_period, driver):
    try:
        # Find the Stoiximan div element within the arb element
        bet_wrappers = element.find_elements(By.CSS_SELECTOR, "div.bet-wrapper")
        for bet_wrapper in bet_wrappers:
            try:
                stoiximan_div = bet_wrapper.find_element(By.XPATH, ".//div[@title='Stoiximan']")
                handle_stoiximan_element(bet_wrapper, half_period, driver)
                break
            except Exception as e:
                # Ignore if Stoiximan element is not found in this bet-wrapper
                continue
    except Exception as e:
        print(f"An error occurred while handling arb element: {e}")

def handle_stoiximan_element(stoiximan_element, half_period, driver):
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
        
        # Enhanced parsing
        market_text_cleaned = market_text.split('(')[0].strip() + " - " + market_text.split(')')[-1].strip() if '(' in market_text and ')' in market_text else market_text.strip()
        line = market_text.split('(')[1].split(')')[0] if '(' in market_text and ')' in market_text else ""
        
        # Get the odds
        odds_span = stoiximan_element.find_element(By.CSS_SELECTOR, "span.coefficient")
        odds_text = odds_span.text

        # Print the extracted data
        print(f"Event Name: {event_name}")
        print(f"Market: {market_text_cleaned}")
        print(f"Odds: {odds_text}")
        print(f"Half Period: {half_period}")
        print(f"Line: {line}")

        # Perform actions on Stoiximan
        bookmaker = 'stoiximan'
        time.sleep(1)
        perform_stoiximan_actions(driver, event_name, market_text_cleaned, line, half_period, bookmaker)

    except Exception as e:
        print(f"An error occurred while handling Stoiximan element: {e}")


def perform_stoiximan_actions(driver, event_name, market_text_cleaned, line, half_period, bookmaker):
    try:
        # Open the Stoiximan website
        driver.get('https://en.stoiximan.gr/')

        # Wait for the page to load
        time.sleep(5)

        # Click the close icon if it exists
        try:
            div_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'tw-flex tw-gap-n tw-relative')]"))
            )

            # Find all SVG elements within this div
            svg_elements = div_element.find_elements(By.TAG_NAME, 'svg')

            # Check if there are at least two SVG elements
            if len(svg_elements) >= 2:
                # Click on the second SVG element
                svg_elements[1].click()

                # Wait for a short period
                time.sleep(1)
                driver.execute_script(f"document.activeElement.value += '{event_name}';")
        except Exception as e:
            print(f"Error occurred: {e}")

        # Wait for the search results to appear and click on the first result
        first_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-result__info__name"))
        )
        first_result.click()

        # Click on the last div with the specific class
        last_div = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tw-py-n.tw-px-[12px].tw-leading-s.tw-text-[12px].tw-rounded-m.tw-font-medium"))
        )
        last_div[-1].click()

        # Map and interact with the specific odds
        time.sleep(1)
        map_and_place_stoiximan_bet(driver, market_text_cleaned, line, half_period)

    except Exception as e:
        print(f"An error occurred while performing actions on Stoiximan: {e}")

def map_and_place_stoiximan_bet(driver, market_text_cleaned, odds, line, half_period):
    try:
        # Click on the last div with the specific class
        last_div = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.tw-py-n.tw-px-[12px].tw-leading-s.tw-text-[12px].tw-rounded-m.tw-font-medium"))
        )
        last_div[-1].click()

        mapping_dict = {
            ('AH1', '+0.5', None): 'Asian Handicap (Current Score 0 - 0)', 
            ('AH1', '-0.5', None): 'Asian Handicap (Current Score 0 - 0)',
            # Add more mappings as required
        }

        market_type = 'even' if line.isdigit() and int(line) % 2 == 0 in market_text_cleaned else 'odd' if 'O' in market_text_cleaned else None
        key = (market_text_cleaned.split(' ')[0], market_type)

        if key in mapping_dict:
            mapped_value = mapping_dict[key]

            # Search for the lines_tab
            lines_tab = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".tw-text-s.tw-leading-s.tw-tracking-s.tw-flex-1.tw-flex.tw-flex-row.tw-justify-start.tw-items-start.tw-min-h-[20px].tw-text-n-13-steel.dark:tw-text-n-silver-mist"))
            )
            lines_tab.click()

            # Find the correct column based on mapping
            columns = lines_tab.find_elements(By.CSS_SELECTOR, ".selections__selection.selection-horizontal-button.tw-flex.tw-flex-row.tw-items-center.tw-justify-center.tw-h-[36px].tw-flex-1.tw-cursor-pointer.tw-py-[10px].tw-px-n.tw-rounded-s.tw-border-n.tw-border-solid.dark:tw-bg-n-22-licorice.dark:tw-border-n-28-cloud-burst.tw-bg-n-97-porcelain.tw-border-n-90-dark-snow.dark:tw-text-white-snow.tw-text-n-13-steel.tw-relative.tw-overflow-hidden.tw-outline-none.tw-select-none.tw-break-words.tw-text-center.selections__selection--columns-2.hover:tw-bg-n-94-dirty-snow.hover:tw-border-n-silver-mist.dark:hover:tw-border-n-36-east-bay.dark:hover:tw-bg-n-28-cloud-burst")

            for column in columns:
                if mapped_value in column.text:
                    column.click()
                    break

            # Find the correct odd element based on market type
            for column in columns:
                if market_type == 'even' and 'U' in column.text:
                    odds_element = column.find_element(By.CSS_SELECTOR, ".tw-text-s.tw-leading-s.tw-font-bold.tw-text-tertiary.dark:tw-text-quartary")
                    if odds_element:
                        odds_element.click()
                        break
                elif market_type == 'odd' and 'O' in column.text:
                    odds_element = column.find_element(By.CSS_SELECTOR, ".tw-text-s.tw-leading-s.tw-font-bold.tw-text-tertiary.dark:tw-text-quartary")
                    if odds_element:
                        odds_element.click()
                        break

    except Exception as e:
        print(f"An error occurred while mapping and placing bet: {e}")


if __name__ == "__main__":
    open_drivers_and_read_arbs()
