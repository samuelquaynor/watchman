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

# Telegram bot settings
TELEGRAM_TOKEN = "8193386528:AAHiSxCbLGxIPD1WflmL8JupSmHdqvA7USI"
CHAT_ID = "5809254524"

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
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--window-size=1920x1080")
    # chrome_options.add_argument(
    #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    # )

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

        driver.get("https://ais.usvisa-info.com/en-za/niv/schedule/64083789/payment")

        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.for-layout"))
        )

        rows = table.find_elements(By.TAG_NAME, "tr")
        appointments = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                location = cols[0].text
                date = cols[1].text
                appointments.append({"location": location, "date": date})
                
        message, should_notify = format_appointments(appointments)

        send_telegram_message(message, should_notify)
        return appointments

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)

        # Delete the cookies file
        if os.path.exists(cookies_path):
            try:
                os.remove(cookies_path)
                print("Cookies file deleted due to error.")
                send_telegram_message(
                    "Cookies file deleted. Please run the script again.",
                    False
                )
            except Exception as delete_error:
                print(f"Error deleting cookies file: {str(delete_error)}")
                print(
                    f"Error deleting cookies file: {str(delete_error)}"
                )

        raise
    # finally:
        # driver.quit()


def format_appointments(appointments):
    if not appointments:
        return "No appointments found.", False  # No notification

    formatted = "Available Appointments:\n\n"
    target_date = datetime(2024, 12, 30)
    earlier_dates = []

    for app in appointments:
        location = app["location"]
        date_str = app["date"]
        date = datetime.strptime(date_str, "%d %B, %Y")

        formatted += f"Location: {location}\n"
        if date < target_date:
            formatted += f"Date: {date_str} (EARLIER DATE FOUND!)\n\n"
            earlier_dates.append((location, date))
        else:
            formatted += f"Date: {date_str}\n\n"

    if earlier_dates:
        earliest = min(earlier_dates, key=lambda x: x[1])
        summary = f"ALERT: Earliest date found!\nLocation: {earliest[0]}\nDate: {earliest[1].strftime('%d %B, %Y')}"
        formatted = summary + "\n\n" + formatted
        return formatted.strip(), True  # Enable notification
    else:
        formatted = (
            f"No dates earlier than {target_date.strftime('%d %B, %Y')} found.\n\n"
            + formatted
        )
        return formatted.strip(), False 


import asyncio


async def main():
    email = "samwillsquaye@gmail.com"  # Replace with your actual email
    password = "Millions$9913"  # Replace with your actual password

    while True:
        try:
            print("Running appointment check...")
            await login_and_get_appointments(email, password)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        print("Waiting for 5 minutes before next check...")
        await asyncio.sleep(300)  # 300 seconds = 5 minutes


if __name__ == "__main__":
    asyncio.run(main())
