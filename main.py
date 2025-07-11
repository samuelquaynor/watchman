import requests
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import telegram
import asyncio
from datetime import datetime
import json
import os
import json

# Telegram bot settings
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def save_cookies(driver, path):
    with open(path, "w") as filehandler:
        json.dump(driver.get_cookies(), filehandler)


def load_cookies(driver, path):
    with open(path, "r") as cookiesfile:
        cookies = json.load(cookiesfile)
    for cookie in cookies:
        driver.add_cookie(cookie)


def send_telegram_message(message, notify):
    bot.send_message(chat_id=CHAT_ID, text=message, disable_notification=(not notify))


async def login_and_get_appointments(email, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    cookies_path = "cookies.json"
    need_login = True

    try:
        if os.path.exists(cookies_path):
            driver.get("https://ais.usvisa-info.com/en-za/niv")
            load_cookies(driver, cookies_path)
            driver.get("https://ais.usvisa-info.com/en-za/niv/groups")

            if "niv/groups" in driver.current_url:
                need_login = False
                print("Logged in successfully using cookies!")

        if need_login:
            driver.get("https://ais.usvisa-info.com/en-za/niv/users/sign_in")

            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "user_email"))
            )
            email_field.send_keys(email)

            password_field = driver.find_element(By.ID, "user_password")
            password_field.send_keys(password)

            policy_confirmed = driver.find_element(By.ID, "policy_confirmed")
            driver.execute_script("arguments[0].click();", policy_confirmed)

            submit_button = driver.find_element(By.NAME, "commit")
            submit_button.click()

            WebDriverWait(driver, 10).until(EC.url_contains("/niv/groups"))

            save_cookies(driver, cookies_path)
            print("Logged in successfully!")

        # Enable network interception
        driver.execute_script(
            """
            window.networkRequests = [];
            var originalFetch = window.fetch;
            window.fetch = function() {
                return originalFetch.apply(this, arguments).then(function(response) {
                    var clone = response.clone();
                    clone.text().then(function(body) {
                        window.networkRequests.push({
                            url: response.url,
                            body: body
                        });
                    });
                    return response;
                });
            };
        """
        )

        # Trigger the appointment data request
        driver.execute_script(
            """
            fetch("https://ais.usvisa-info.com/en-za/niv/schedule/68662830/appointment/days/101.json?appointments[expedite]=false", {
                headers: {
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                    "x-requested-with": "XMLHttpRequest"
                },
                method: "GET",
                credentials: "include"
            });
        """
        )

        # Wait for the request to complete
        import time

        time.sleep(5)

        # Retrieve the intercepted requests
        requests = driver.execute_script("return window.networkRequests;")

        # Find the appointment data request
        appointment_data = next(
            (req for req in requests if "/appointment/days/101.json" in req["url"]),
            None,
        )

        if appointment_data:
            print("Appointment data retrieved successfully")
            appointment_json = json.loads(appointment_data["body"])
            print("Response Body:", appointment_json)
            # Process the appointment data as needed
            # For example, you can pass this data to format_appointments function
            formatted_appointments, notify = format_appointments(appointment_json)
            send_telegram_message(formatted_appointments, notify)
        else:
            print("Failed to retrieve appointment data")
            send_telegram_message(
                "Failed to retrieve appointment data. Please check the system.", True
            )

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        send_telegram_message(error_message, True)

        # Delete the cookies file
        if os.path.exists(cookies_path):
            try:
                os.remove(cookies_path)
                print("Cookies file deleted due to error.")
                send_telegram_message(
                    "Cookies file deleted. Please check the system.", True
                )
            except Exception as delete_error:
                print(f"Error deleting cookies file: {str(delete_error)}")
                print(f"Error deleting cookies file: {str(delete_error)}")

        raise

    finally:
        driver.quit()


def format_appointments(appointments):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not appointments:
        message = f"Appointment Check ({current_time}):\nNo appointments found."
        return message, False  # No notification for no appointments

    formatted = f"Appointment Check ({current_time}):\n\n"
    target_date = datetime(2025, 8, 8)
    earlier_dates = []

    # Sort appointments by date
    sorted_appointments = sorted(appointments, key=lambda x: x["date"])

    # Take only the first three appointments
    for app in sorted_appointments[:1]:
        date_str = app["date"]
        date = datetime.strptime(date_str, "%Y-%m-%d")
        is_business_day = app["business_day"]

        formatted += f"Date: {date.strftime('%d %B, %Y')}\n"
        formatted += f"Business Day: {'Yes' if is_business_day else 'No'}\n\n"

        if date < target_date:
            earlier_dates.append(date)

    if earlier_dates:
        earliest = min(earlier_dates)
        summary = f"ALERT: Earliest date found!\nDate: {earliest.strftime('%d %B, %Y')}"
        formatted = summary + "\n\n" + formatted
        return formatted.strip(), True  # Enable notification
    else:
        formatted = (
            f"No dates earlier than {target_date.strftime('%d %B, %Y')} found.\n\n"
            + formatted
        )
        return formatted.strip(), False


async def main():
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")

    if not all([email, password, TELEGRAM_TOKEN, CHAT_ID]):
        raise ValueError(
            "Missing required environment variables. Please set EMAIL, PASSWORD, TELEGRAM_TOKEN, and CHAT_ID."
        )

    try:
        print("Running appointment check...")
        await login_and_get_appointments(email, password)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise  # Re-raise the exception to ensure GitHub Actions marks the run as failed


if __name__ == "__main__":
    asyncio.run(main())
