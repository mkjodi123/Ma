import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from faker import Faker
from telegram import Bot

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("8197356432:AAHY54797qaRZen5ImUPAFkP33jXPZfDXkA")
ADMIN_ID = os.getenv("7353797869")

fake = Faker()

def send_telegram_message(message):
    """ Sends a message to Telegram admin. """
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=ADMIN_ID, text=message)

def create_cloudways_account(email):
    """ Automates Cloudways account creation and sends details via Telegram. """
    full_name = fake.name()
    password = fake.password(length=12, special_chars=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without UI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://platform.cloudways.com/signup")
        time.sleep(3)

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "name").send_keys(full_name)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Get Started')]").click()

        message = f"✅ **Cloudways Account Created!**\n📧 Email: {email}\n👤 Name: {full_name}\n🔑 Password: {password}"
        send_telegram_message(message)

        print("Account details sent to Telegram!")
        time.sleep(10)

    finally:
        driver.quit()

# Run the bot
user_email = input("Enter your Gmail: ")
create_cloudways_account(user_email)