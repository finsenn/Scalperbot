from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
import time

# Configuration
BASE_URL = "http://127.0.0.1:6969"  # Update with the actual URL where this app is hosted
EMAIL = "finsen@gmail.com"  # Replace with your login email
PASSWORD = "finsen"  # Replace with your login password
TARGET_MOVIE = "Batman"  # Replace with the movie name
TARGET_TIME = "14:30"  # Replace with desired showtime
TARGET_SEAT = "A"  # Replace with desired seat
NUMBER_OF_TICKETS = 1  # Number of tickets to purchase
TARGET_LOCATION = "BeeNema"  # Replace with the location you're targeting

# Initialize WebDriver
driver = webdriver.Chrome()
driver.maximize_window()

# Initialize data collection variables
transaction_start_time = time.time()  # Start timer for overall transaction
transaction_speed = []  # List to collect transaction times for individual steps
request_frequency = 0  # Counter to count the number of requests made (browser behavior)

def login():
    """Login to the website using email and track the transaction speed."""
    start_time = time.time()  # Start time for login
    driver.get(BASE_URL)
    time.sleep(0.1)  # Wait for the page to load

    # Find and click the Login button
    login_button = driver.find_element(By.LINK_TEXT, "Login")
    login_button.click()
    time.sleep(0.1)

    # Fill in the login credentials
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")

    email_field.send_keys(EMAIL)
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)  # Submit the login form
    time.sleep(0.1)

    transaction_speed.append({"step": "Login", "time": time.time() - start_time})

def click_with_retry(element, retries=3):
    """Click an element with retries to handle timing or obstruction issues."""
    global request_frequency
    for attempt in range(retries):
        try:
            element.click()
            request_frequency += 1  # Increment request frequency for each click
            return
        except (ElementNotInteractableException, ElementClickInterceptedException) as e:
            print(f"Retrying click ({attempt + 1}/{retries}): {e}")
            time.sleep(1)
    raise Exception("Failed to interact with the element after multiple attempts.")

def see_screenings():
    """Click the 'See Screenings' button after login and track speed."""
    start_time = time.time()  # Start time for see_screenings action
    try:
        # Wait for the "See Screenings" button to be clickable
        screenings_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "See Screenings"))
        )
        click_with_retry(screenings_button)
        print("Clicked 'See Screenings' button.")

    except Exception as e:
        print("Error clicking 'See Screenings' button:", e)
        driver.quit()
    
    transaction_speed.append({"step": "See Screenings", "time": time.time() - start_time})

def select_location_and_show_screenings():
    """Select location, show screenings, and click 'Select Seats'."""
    start_time = time.time()  # Start time for location selection
    try:
        # Wait for the location dropdown to appear and select the location
        location_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "location_id"))
        )
        select = Select(location_dropdown)
        select.select_by_visible_text(TARGET_LOCATION)
        print(f"Selected location: {TARGET_LOCATION}")

        # Click the 'Show Screenings' button
        show_screenings_button = driver.find_element(By.XPATH, "//button[text()='Show Screenings']")
        click_with_retry(show_screenings_button)
        print("Clicked 'Show Screenings' button.")

        # Wait for the page to reload and display the screenings
        select_seats_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Select Seats"))
        )
        click_with_retry(select_seats_button)
        print("Clicked 'Select Seats' button.")

    except Exception as e:
        print("Error selecting location or clicking buttons:", e)
        driver.quit()

    transaction_speed.append({"step": "Select Location and Show Screenings", "time": time.time() - start_time})

def select_seat_and_confirm():
    """Select seats and confirm the selection."""
    start_time = time.time()  # Start time for seat selection
    try:
        # Wait for the seat options to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "seat"))
        )

        # Find all seats
        seats = driver.find_elements(By.CLASS_NAME, "seat")
        selected_seats = 0
        for seat in seats:
            # Check if the seat is available and matches the target
            if 'unavailable' not in seat.get_attribute('class') and TARGET_SEAT in seat.get_attribute('data-seat-number'):
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", seat)  # Scroll to the seat
                click_with_retry(seat)  # Click on the seat
                print(f"Selected seat: {seat.get_attribute('data-seat-number')}")
                selected_seats += 1
                if selected_seats == NUMBER_OF_TICKETS:
                    break

        if selected_seats < NUMBER_OF_TICKETS:
            print("Not enough seats available.")
            return False

        # Confirm the selection
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn"))
        )
        click_with_retry(confirm_button)
        print("Seat selection confirmed.")

        return True

    except Exception as e:
        print("Error selecting seats or confirming:", e)
        return False

    transaction_speed.append({"step": "Select Seat and Confirm", "time": time.time() - start_time})

def main():
    try:
        login()  # Login to the site
        see_screenings()  # Click "See Screenings" first
        select_location_and_show_screenings()  # Select the location and show screenings, then click "Select Seats"
        if not select_seat_and_confirm():  # Select seat and confirm the selection
            print("Failed to complete the booking.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the browser if it was opened

    # Final output of the collected data
    transaction_end_time = time.time()
    total_transaction_time = transaction_end_time - transaction_start_time
    print("\n--- Transaction Data ---")
    print(f"Total Transaction Time: {total_transaction_time:.2f} seconds")
    print("Transaction Speed (Time per Step):")
    for record in transaction_speed:
        print(f"{record['step']}: {record['time']:.2f} seconds")
    print(f"Total Requests Made (Request Frequency): {request_frequency}")
    print(f"Transaction Frequency: {1}")  # Frequency would depend on how often this script is run, for now, assume it's 1 per run.
    print("Transaction Volume: 1 (based on the number of bookings made)")
    print("Geographic Data: Not collected in this script (requires external tools like IP geolocation APIs)")
    print("Browser Behavior: Not specifically tracked but can be inferred from request frequency and timing")
    print("Order Timing: Not captured in this code, but you can log when the order is placed")

if __name__ == "__main__":
    main()
