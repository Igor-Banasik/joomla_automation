from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from setup_utils import auto_create_driver
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Defined funcitons:

def login_to_imex(driver):
    """
    Logs into the IMEX website using the provided driver.
    
    Args:
        driver (webdriver): The Selenium WebDriver instance.
    
    Returns:
        None
    """
    # 1. Open website
    driver.get("https://imex-frankfurt.com/newfront/page/sign-in")

    time.sleep(2)  # Let page load

    # 2. Click on "Accept all cookies"
    try:
        driver.find_element(By.CSS_SELECTOR, ".wscrOk2").click()
    except Exception as e:
        print("Cookie accept button not found or already accepted.", e)

    time.sleep(1)

    # 3. Scroll down
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)

    time.sleep(1)

    # 4. Click on "Access your IMEX account"
    driver.find_element(By.CSS_SELECTOR, "span[title='Access your IMEX account']").click()

    time.sleep(2)

    # 5. Enter email
    email_input = driver.find_element(By.CSS_SELECTOR, "#email")
    email_input.clear()
    email_input.send_keys(os.getenv("IMEX_EMAIL"))

    # 6. Enter password
    password_input = driver.find_element(By.CSS_SELECTOR, "#password")
    password_input.clear()
    password_input.send_keys(os.getenv("IMEX_PASSWORD"))

    # 7. Click on "Sign in"
    driver.find_element(By.CSS_SELECTOR, "#next").click()

    time.sleep(5)  # Wait for dashboard to load

    # 8. Click on "Accept all cookies" (again)
    try:
        driver.find_element(By.CSS_SELECTOR, ".wscrOk2").click()
    except Exception as e:
        print("Second cookie accept button not found or already accepted.", e)


# Function to message all attendees
def message_all_attendees():
    global MESSAGED_ATTENDEES_COUNT  # Use the global counter
    attendee_index = 1

    while True:
        try:
            # Build the dynamic selector for each attendee
            attendee_selector = f"#__next > div.MuiBox-root.css-g9qx4c > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-sm-7.MuiGrid-grid-md-9.css-1fz58g7 > div.MuiPaper-root.MuiPaper-outlined.MuiPaper-rounded.css-17bpyl9 > div.MuiGrid-root.MuiGrid-container.MuiGrid-spacing-xs-2.css-isbt42 > div:nth-child({attendee_index})"
            
            attendee_container = driver.find_element(By.CSS_SELECTOR, attendee_selector)

            # Scroll to the attendee
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", attendee_container)

            favorite_button = attendee_container.find_element(By.CSS_SELECTOR, "button[data-testid='favor']")
            favorite_class = favorite_button.get_attribute('class')
            if 'css-6ck4wa' in favorite_class:
                print(f"Attendee #{attendee_index} already favorited. Skipping.")
                attendee_index += 1
                continue

            # Find and click the message button inside this attendee container
            attendee_button = attendee_container.find_element(By.CSS_SELECTOR, "div > div.MuiBox-root.css-1h1kiqf > button")
            attendee_button.click()

            # Wait until the message textarea is present
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.MuiInputBase-inputMultiline"))
            )

            # Type the message into the textarea
            textarea = driver.find_element(By.CSS_SELECTOR, "textarea.MuiInputBase-inputMultiline")
            textarea.click()
            textarea.send_keys(MESSAGE_TEXT)
            
            # Locate and click the send message button
            send_button = driver.find_element(By.CSS_SELECTOR, "button.MuiButton-containedPrimary[aria-label='send message']")
            send_button.click()

            time.sleep(0.2)  # Wait for the message to send

            # Close the message window
            close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-controls='chat-close']")
            close_button.click()

            # Re-find the attendee container AFTER closing the message window
            # attendee_container = driver.find_element(By.CSS_SELECTOR, attendee_selector)

            # Then find the favorite button FRESH again and click it
            favorite_button = attendee_container.find_element(By.CSS_SELECTOR, "button[data-testid='favor']")
            favorite_button.click()

            # Increment the counter for successfully messaged attendees
            MESSAGED_ATTENDEES_COUNT += 1

            print(f"Successfully messaged and favorited attendee #{attendee_index}.")
            attendee_index += 1

        except Exception as e:
            print(f"No more attendees or error at attendee #{attendee_index}: {e}")
            break


MESSAGE_TEXT = "Your Appointment for Morocco. Hi! I'm excited to connect and tell you more about what we can offer in Morocco. I’d love to hear what you’re looking for and see how we can help bring your plans to life. Looking forward to our chat, Hind"

# Actual code to run:
if __name__ == "__main__":
    # Create a new driver instance
    driver = auto_create_driver()

    # Maximize the window
    driver.maximize_window()

    # Log into IMEX
    login_to_imex(driver)

    # Navigate to the dashboard page
    driver.get("https://imex-frankfurt.com/newfront/profile/dashboard")

    print("Now, choose the DMC in Profile (Karma, Vas Events etc.) and navigate to the Attendee list")
    input("Press Enter when you're on the attendee list...")

    # Initialize the global counter
    MESSAGED_ATTENDEES_COUNT = 0

    while True:
        message_all_attendees()
        print(f"Total attendees messaged so far: {MESSAGED_ATTENDEES_COUNT}")
        user_input = input("Press Enter to run the function again, or type 'exit' to quit: ")
        if user_input.lower() == 'exit':
            break

    # Close the driver after use
    input("Press Enter to close the driver...")
    driver.quit()