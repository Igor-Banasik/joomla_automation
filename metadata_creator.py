from datetime import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from openai import OpenAI


def generate_metadata(sitename):
    """
    Generates a metadata description for the given sitename using the OpenAI API.

    Args:
        sitename (str): The name of the site for which metadata is to be generated.

    Returns:
        str: The generated metadata description.
    """
    client = OpenAI()

    # Create a prompt for the metadata description
    prompt = f"Write a 140–145 character metadata description for '{sitename}', starting with its name followed by a colon or dash."

    # Call the OpenAI API
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    # Return the generated text
    return response.output_text


def metadata_description_editor(driver, menu_name):
    """Edits the metadata description for a given menu item."""
    try:
        # Navigate to the URL with the Menus
        menu_items_url = "https://bodyandsoulinternational.com/administrator/index.php?option=com_menus&view=items&menutype="
        driver.get(menu_items_url)

        # Wait for the search field to be present
        search_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "filter_search"))
        )

        # Search for the menu
        search_field.clear()  # Clear any existing text
        search_field.send_keys(menu_name)
        search_field.send_keys(Keys.RETURN)
        
        # Click on the menu
        driver.find_element(By.LINK_TEXT, menu_name).click()

        # Go to 'Page Display' tab
        button = driver.find_element(By.XPATH, "//button[@aria-controls='attrib-page-options']")
        driver.execute_script("arguments[0].click();", button)

        # Input the new Browser Page Title
        title_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "jform_params_page_title")))
        title_input.clear()  # Clear existing text if needed
        title_input.send_keys(f"{menu_name}")

        # Click the Metadata tab
        metadata_tab = driver.find_element(By.XPATH, "//button[@aria-controls='attrib-metadata']")
        driver.execute_script("arguments[0].click();", metadata_tab)

        # Wait and fill in the meta description
        meta_description = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "jform_params_menu_meta_description")))
        meta_description.clear()
        new_meta_text = generate_metadata(menu_name)  # Call the OpenAI API to generate metadata
        print(f"New metadata: {new_meta_text}")
        meta_description.send_keys(new_meta_text)

        # Click the 'Save & Close' button
        driver.find_element(By.XPATH, "//button[normalize-space()='Save & Close']").click()


        print(f"✅ Created a meta description for '{menu_name}' successfully.")
    except Exception as e:
        print(f"❌ Failed to create the meta description for '{menu_name}'")

def process_metadata_for_events_in_articles(driver, countries):
    """
    Calls the metadata_description_editor function for each country in the list.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        countries (list): A list of country names.

    Returns:
        None
    """
    for country in countries:
        menu_name = f"Events in {country}"
        print(f"Processing metadata for: {menu_name}")
        metadata_description_editor(driver, menu_name)


def process_metadata_for_activities(driver, countries):
    """
    Calls the metadata_description_editor function for each country in the list.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        countries (list): A list of country names.

    Returns:
        None
    """
    for country in countries:
        menu_name = f"Activities {country}"
        print(f"Processing metadata for: {menu_name}")
        metadata_description_editor(driver, menu_name)


def process_metadata_for_what_to_do(driver, countries):
    """
    Searches for "What to do in {country}" but uses "Activities {country}" for the page display and meta description.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        countries (list): A list of country names.

    Returns:
        None
    """
    for country in countries:
        search_menu_name = f"What to do in {country}"
        update_menu_name = f"Activities {country}"
        print(f"Processing metadata for: {search_menu_name}")

        try:
            # Navigate to the URL with the Menus
            menu_items_url = "https://bodyandsoulinternational.com/administrator/index.php?option=com_menus&view=items&menutype="
            driver.get(menu_items_url)

            # Wait for the search field to be present
            search_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "filter_search"))
            )

            # Search for the menu
            search_field.clear()
            search_field.send_keys(search_menu_name)
            search_field.send_keys(Keys.RETURN)

            # Wait for the menu item to appear and click it
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, search_menu_name))
            )
            driver.find_element(By.LINK_TEXT, search_menu_name).click()

            # Go to 'Page Display' tab
            button = driver.find_element(By.XPATH, "//button[@aria-controls='attrib-page-options']")
            driver.execute_script("arguments[0].click();", button)

            # Input the new Browser Page Title
            title_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "jform_params_page_title")))
            title_input.clear()
            title_input.send_keys(update_menu_name)  # Use "Activities {country}"

            # Click the Metadata tab
            metadata_tab = driver.find_element(By.XPATH, "//button[@aria-controls='attrib-metadata']")
            driver.execute_script("arguments[0].click();", metadata_tab)

            # Wait and fill in the meta description
            meta_description = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "jform_params_menu_meta_description")))
            meta_description.clear()
            new_meta_text = generate_metadata(update_menu_name)  # Use "Activities {country}" for metadata
            print(f"New metadata: {new_meta_text}")
            meta_description.send_keys(new_meta_text)

            # Click the 'Save & Close' button
            driver.find_element(By.XPATH, "//button[normalize-space()='Save & Close']").click()

            print(f"✅ Created a meta description for '{update_menu_name}' successfully.")
        except Exception as e:
            print(f"❌ Failed to create the meta description for '{search_menu_name}': {e}")