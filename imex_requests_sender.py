from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from setup_utils import auto_create_driver
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import datetime

# Defined funcitons:

def login_to_imex(driver):
    """
    Logs into the IMEX website using the provided driver.
    
    Args:
        driver (webdriver): The Selenium WebDriver instance.
    
    Returns:
        None
    """
    # 0. Maximize the window
    driver.maximize_window()

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

    time.sleep(1)

    # 6. Enter password
    password_input = driver.find_element(By.CSS_SELECTOR, "#password")
    password_input.clear()
    password_input.send_keys(os.getenv("IMEX_PASSWORD"))

    time.sleep(1)

    # 7. Click on "Sign in"
    driver.find_element(By.CSS_SELECTOR, "#next").click()

    time.sleep(5)  # Wait for dashboard to load

    # 8. Click on "Accept all cookies" (again)
    try:
        driver.find_element(By.CSS_SELECTOR, ".wscrOk2").click()
    except Exception as e:
        print("Second cookie accept button not found or already accepted.", e)


# Function to message all attendees
def message_all_attendees(current_dmc):
    global MESSAGED_ATTENDEES_COUNT  # Use the global counter
    attendee_index = 1

    while MESSAGED_ATTENDEES_COUNT < 220:
        try:
            # If attendee index reaches 59, go the next page
            if attendee_index > 59:
                # Find the current page number
                current_page_button = driver.find_element(By.CSS_SELECTOR, "button.MuiButtonBase-root.MuiPaginationItem-root.MuiPaginationItem-sizeMedium.MuiPaginationItem-text.MuiPaginationItem-rounded.MuiPaginationItem-page.css-1tuw226[aria-current='true']")
                current_page_number = int(current_page_button.get_attribute("aria-label").split()[-1])

                # Go to the next page
                next_page_button = driver.find_element(By.CSS_SELECTOR, f"button.MuiButtonBase-root.MuiPaginationItem-root.MuiPaginationItem-sizeMedium.MuiPaginationItem-text.MuiPaginationItem-rounded.MuiPaginationItem-page.css-1tuw226[aria-label='Go to page {current_page_number + 1}']")
                next_page_button.click()

                # Wait for the next page to load

                # Wait until the attendee container is present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, attendee_selector))
                )

                time.sleep(3)

                # Reset attendee index for the new page
                attendee_index = 1

                print(f"Total attendees messaged so far: {MESSAGED_ATTENDEES_COUNT}")
                print(f"Moving on to page {current_page_number + 1}")
                continue

            # Build the dynamic selector for each attendee
            attendee_selector = f"#__next > div.MuiBox-root.css-g9qx4c > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-sm-7.MuiGrid-grid-md-9.css-1fz58g7 > div.MuiPaper-root.MuiPaper-outlined.MuiPaper-rounded.css-17bpyl9 > div.MuiGrid-root.MuiGrid-container.MuiGrid-spacing-xs-2.css-isbt42 > div:nth-child({attendee_index})"
            
            attendee_container = driver.find_element(By.CSS_SELECTOR, attendee_selector)

            # Scroll to the attendee
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", attendee_container)

            # Check if the attendee's from a company we don't want
            try:
                title_element = attendee_container.find_element(By.CSS_SELECTOR, "div[data-testid='teamMemberPosition'][data-styleid='team-member-company']")
                title_text = title_element.get_attribute("title").lower()
                if any(keyword in title_text for keyword in ["helms", "cwt"]):
                    print(f"Skipping attendee #{attendee_index} due to them being from a company: {title_text}")
                    attendee_index += 1
                    continue
            except Exception as e:
                print(f"Error checking the company for attendee #{attendee_index}: {e}")

            favorite_button = attendee_container.find_element(By.CSS_SELECTOR, "button[data-testid='favor']")
            favorite_class = favorite_button.get_attribute('class')

            # Check if the attendee has already been favorited
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

            # Wait until the previous messages are displayed (if they exist)
            time.sleep(0.5)

            # Check if the attendee has been messaged, but not favorited
            try:
                if len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='message-car-wrapper'] p[data-testid='message-text']")) > 0:
                    print(f"Attendee #{attendee_index} already been messaged. Skipping.")

                    # Close the message window
                    close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-controls='chat-close']")
                    close_button.click()

                    # Favorite the attendee
                    favorite_button = attendee_container.find_element(By.CSS_SELECTOR, "button[data-testid='favor']")
                    favorite_button.click()

                    attendee_index += 1
                    continue
            except Exception as e:
                print("Problem when checking if the attendee's been messaged:", e)

            # Type the message into the textarea
            textarea = driver.find_element(By.CSS_SELECTOR, "textarea.MuiInputBase-inputMultiline")
            textarea.click()
            textarea.send_keys(MESSAGE_TEXTS[current_dmc])
            
            # Locate and click the send message button
            send_button = driver.find_element(By.CSS_SELECTOR, "button.MuiButton-containedPrimary[aria-label='send message']")
            send_button.click()

            time.sleep(1)  # Wait for the message to send

            # Close the message window
            close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-controls='chat-close']")
            close_button.click()

            # Re-find the attendee container AFTER closing the message window (not necessary i think)
            # attendee_container = driver.find_element(By.CSS_SELECTOR, attendee_selector)

            # Then find the favorite button FRESH again and click it
            favorite_button = attendee_container.find_element(By.CSS_SELECTOR, "button[data-testid='favor']")
            favorite_button.click()

            # Increment the counter for successfully messaged attendees
            MESSAGED_ATTENDEES_COUNT += 1

            print(f"Successfully messaged and favorited attendee {MESSAGED_ATTENDEES_COUNT}✅ (#{attendee_index}).")
            attendee_index += 1

        except Exception as e:
            print(f"No more attendees or error at attendee #{attendee_index}: {e}")
            break

def navigate_to_dmc(dmc_profile):

    # Navigate to the dashboard page
    driver.get("https://imex-frankfurt.com/newfront/profile/dashboard")

    # Wait until the profile menu button is present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiBox-root.css-cii0a7[data-button-role='profile_menu']"))
    )

    # Locate and click the profile menu button
    profile_menu_button = driver.find_element(By.CSS_SELECTOR, "div.MuiBox-root.css-cii0a7[data-button-role='profile_menu']")
    profile_menu_button.click()

    # Locate the scrollable container
    scroll_container = driver.find_element(By.CSS_SELECTOR, "div.MuiBox-root.css-1g3rt2y")

    # Find all elements with the class "MuiBox-root css-1mvuziv" inside the scrollable container
    dmc_elements = scroll_container.find_elements(By.CSS_SELECTOR, "div.MuiBox-root.css-1mvuziv")

    for dmc_element in dmc_elements:
        # Scroll to the current DMC element
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dmc_element)

        # Find the title element within the current DMC element
        title_element = dmc_element.find_element(By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body2.css-11tolnh")

        # Check if the title matches the desired DMC
        if title_element.get_attribute("title") == dmc_profile:
            # Click the matching DMC element
            dmc_element.click()
            print(f"Entered DMC profile for: {dmc_profile}")
            break

    time.sleep(6)

    # Navigate to the specified URL
    driver.get("https://imex-frankfurt.com/newfront/participants?page=delegates&hash=f0452762f7ed11ad9aa7fbf9c86c2330&pageNumber=1&authorId=26793")

    time.sleep(6)

    # Locate the dropdown menu for selecting the number of attendees per page
    dropdown_menu = driver.find_element(By.CSS_SELECTOR, "div[data-styleid='uiselect-12'] div[role='combobox']")

    # Click the dropdown menu to open it
    dropdown_menu.click()

    time.sleep(0.5)

    # Locate the specific option for "60" attendees per page
    option_60 = driver.find_element(By.CSS_SELECTOR, "li.MuiButtonBase-root.MuiMenuItem-root[title='60']")

    # Click the option to select it
    option_60.click()

    # Wait for the page to reload with the new attendee count
    time.sleep(8)

    # Define the dimensions of the left half of the screen
    screen_width = 1920  # Adjust if necessary
    screen_height = 1080
    one_third_screen_width = screen_width // 2.6

    # Move and resize the window to the left side
    driver.set_window_position(0, 0)
    driver.set_window_size(one_third_screen_width, screen_height)

def go_back_to_main_profile():

    # Maximize the browser window
    driver.maximize_window()

    # Navigate to the dashboard page
    driver.get("https://imex-frankfurt.com/newfront/profile/dashboard")

    # Wait until the profile menu button is present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiBox-root.css-cii0a7[data-button-role='profile_menu']"))
    )

    # Locate and click the profile menu button
    profile_menu_button = driver.find_element(By.CSS_SELECTOR, "div.MuiBox-root.css-cii0a7[data-button-role='profile_menu']")
    profile_menu_button.click()

    # Locate the scrollable container
    scroll_container = driver.find_element(By.CSS_SELECTOR, "div.MuiBox-root.css-1g3rt2y")

    # Find all elements with the class "MuiBox-root css-1mvuziv" inside the scrollable container
    dmc_elements = scroll_container.find_elements(By.CSS_SELECTOR, "div.MuiBox-root.css-1mvuziv")

    for dmc_element in dmc_elements:
        # Scroll to the current DMC element
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dmc_element)

        # Find the title element within the current DMC element
        title_element = dmc_element.find_element(By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body2.css-11tolnh")

        # Check if the title matches the desired DMC
        if title_element.get_attribute("title") == "Jaapjan Fenijn":
            # Click the matching DMC element
            dmc_element.click()
            print(f"Back to the main profile")
            break
        
    time.sleep(6)

MESSAGE_TEXTS = {
    "MidFar": "Your Appointment for Morocco. Hi! I'm excited to connect and tell you more about what we can offer in Morocco. I’d love to hear what you’re looking for and see how we can help bring your plans to life. Looking forward to our chat, Hind",
    "DT Slovenia": "Your Appointment for Slovenia. Hi! I'm excited to meet and tell you more about what we can offer in Slovenia. I’d really like to hear what you have in mind and see how we can collaborate to bring it to life. Looking forward to our conversation, Taja",
    "Brook Green UK": "Your Appointment for the United Kingdom. Hi! I'm looking forward to our meeting and sharing more about what we offer in the UK. I’d love to hear about your interests and explore how we can work together to create something great. Looking forward to speaking soon, Elena",
    "Grosvenor Tours": "Your Appointment for South Africa. Hi! I'm excited to connect and tell you more about what we can offer in South Africa. I’d love to hear what you’re looking for and see how we can help bring your plans to life. Looking forward to our chat, Peter-John",
    "DZK Travel": "Your Appointment for Central Europe with DZK. Hi! I’m looking forward to our chat about Central Europe. With local offices in Prague, Budapest, Vienna, Bucharest, and Bratislava, we’re well set up to help you with whatever you need in the region. Let’s connect and see how we can work together! Speak soon, Nicolas",
    "On Site Malta": "Your appointment for Malta. Hi! I’m excited to catch up and talk about Malta! I’d love to hear more about your needs and see how we can support you and your clients. Hope to see you soon, Chris"
}

stop_flag = False

def check_for_stop():
    global stop_flag
    while not stop_flag:
        user_input = input("Type 'stop' to quit: ")
        if user_input.lower() == 'stop':
            stop_flag = True

def keep_running_message_all_attendees(dmc):
    # global stop_flag
    global MESSAGED_ATTENDEES_COUNT

    # Start a thread to listen for the "stop" command
    # stop_thread = threading.Thread(target=check_for_stop)
    # stop_thread.start()

    while MESSAGED_ATTENDEES_COUNT < 220:
        message_all_attendees(dmc)
    
    # stop_thread.join()
        
    # Set stop_flag back to False after the function has been stopped
    # stop_flag = False

def navigate_to_last_logged_page(driver, log_directory="imex_logs"):
    """
    Reads the last page number from the most recent log file and navigates to that page.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        log_directory (str): The directory where log files are stored.

    Returns:
        None
    """
    # Find the most recent log file
    if not os.path.exists(log_directory) or not os.listdir(log_directory):
        print("No log files found. Starting from the first page.")
        return

    log_files = sorted(os.listdir(log_directory), reverse=True)
    latest_log_file = os.path.join(log_directory, log_files[0])

    # Read the last page number from the log file
    last_page_number = 1  # Default to the first page if not found
    try:
        with open(latest_log_file, "r") as file:
            for line in file:
                if "Last Page Number:" in line:
                    last_page_number = int(line.split(":")[-1].strip())
                    break
    except Exception as e:
        print(f"Error reading the log file: {e}")
        return

    print(f"Resuming from page {last_page_number}...")

    # Navigate to the last logged page
    while True:
        try:
            # Find the current page number
            current_page_button = driver.find_element(By.CSS_SELECTOR, "button.MuiButtonBase-root.MuiPaginationItem-root.MuiPaginationItem-sizeMedium.MuiPaginationItem-text.MuiPaginationItem-rounded.MuiPaginationItem-page.css-1tuw226[aria-current='true']")
            current_page_number = int(current_page_button.get_attribute("aria-label").split()[-1])

            if current_page_number >= last_page_number:
                print(f"Reached page {current_page_number}.")
                break

            if current_page_number + 4 <= last_page_number:
                # Go 5 pages forward
                next_page_button = driver.find_element(By.CSS_SELECTOR, f"button.MuiButtonBase-root.MuiPaginationItem-root.MuiPaginationItem-sizeMedium.MuiPaginationItem-text.MuiPaginationItem-rounded.MuiPaginationItem-page.css-1tuw226[aria-label='Go to page {current_page_number + 4}']")
                next_page_button.click()
            else:
                # Go to the next page
                next_page_button = driver.find_element(By.CSS_SELECTOR, f"button.MuiButtonBase-root.MuiPaginationItem-root.MuiPaginationItem-sizeMedium.MuiPaginationItem-text.MuiPaginationItem-rounded.MuiPaginationItem-page.css-1tuw226[aria-label='Go to page {current_page_number + 1}']")
                next_page_button.click()

            # Wait for the next page to load
            time.sleep(0.5)
            # Wait until the current page button is present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.MuiButtonBase-root.MuiPaginationItem-root.MuiPaginationItem-sizeMedium.MuiPaginationItem-text.MuiPaginationItem-rounded.MuiPaginationItem-page.css-1tuw226[aria-current='true']"))
            )

        except Exception as e:
            print(f"Error navigating to the next page: {e}")
            break


# Actual code to run:
if __name__ == "__main__":
    # Create a new driver instance
    driver = auto_create_driver()

    # Log into IMEX
    login_to_imex(driver)

    # Get the current timestamp for unique log file entries
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for dmc in MESSAGE_TEXTS:
        # Navigate to the chosen DMC
        navigate_to_dmc(dmc)

        # Initialize the global counter
        MESSAGED_ATTENDEES_COUNT = 0

        # Start runtime counter
        start_time = datetime.datetime.now()

        navigate_to_last_logged_page(driver)

        # Message all attendees
        keep_running_message_all_attendees(dmc)

        # Calculate the time it took
        end_time = datetime.datetime.now()
        time_taken = end_time - start_time

        # Get the last current_page_number from message_all_attendees
        try:
            current_page_button = driver.find_element(By.CSS_SELECTOR, "button.MuiButtonBase-root.MuiPaginationItem-root.MuiPaginationItem-sizeMedium.MuiPaginationItem-text.MuiPaginationItem-rounded.MuiPaginationItem-page.css-1tuw226[aria-current='true']")
            current_page_number = int(current_page_button.get_attribute("aria-label").split()[-1])
        except Exception as e:
            current_page_number = "Unknown (Error retrieving page number)"

        # Write the summary to a log file with a unique timestamp
        # Ensure the "imex_logs" directory exists
        log_directory = "imex_logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # Write the summary to a log file with a unique timestamp
        log_file_path = os.path.join(log_directory, f"imex_log_{timestamp}.txt")
        with open(log_file_path, "w") as file:
            file.write(f"DMC: {dmc}\n")
            file.write(f"Messaged Attendees: {MESSAGED_ATTENDEES_COUNT}\n")
            file.write(f"Time Taken: {time_taken}\n")
            file.write(f"Last Page Number: {current_page_number}\n")
            file.write("\n")

        # Go back to the main profile
        go_back_to_main_profile()

    # Close the driver after use
    input("Press Enter to close the driver...")
    driver.quit()