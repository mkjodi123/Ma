import telebot
import time
import imapclient
import email
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from faker import Faker

# Telegram Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Admin Telegram ID (Replace with your Telegram ID)
ADMIN_ID = 123456789  # Replace with your Telegram user ID

bot = telebot.TeleBot(BOT_TOKEN)

# User Data Storage
user_data = {}

# Initialize Faker for random details
fake = Faker()

# Opera WebDriver Setup (Update Paths)
opera_driver_path = "C:/webdriver/operadriver.exe"
options = webdriver.ChromeOptions()
options.binary_location = "C:/Program Files/Opera/launcher.exe"

# Check if the user is admin
def is_admin(chat_id):
    return chat_id == ADMIN_ID

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, "🚫 You are not authorized to use this bot.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    send_gmail_button = telebot.types.KeyboardButton("Send Gmail")
    send_password_button = telebot.types.KeyboardButton("Send Password")
    markup.add(send_gmail_button, send_password_button)
    
    bot.send_message(chat_id, "Welcome, Admin! Use the buttons below to enter Gmail and password.", reply_markup=markup)

# Handle "Send Gmail" Button Click
@bot.message_handler(func=lambda message: message.text == "Send Gmail")
def ask_for_gmail(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, "🚫 You are not authorized to use this bot.")
        return

    bot.send_message(chat_id, "Please enter your Gmail:")
    bot.register_next_step_handler(message, get_gmail)

# Get Gmail from User
def get_gmail(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"email": message.text}
    bot.send_message(chat_id, "✅ Gmail received! Now, click 'Send Password' to enter your Gmail password.")

# Handle "Send Password" Button Click
@bot.message_handler(func=lambda message: message.text == "Send Password")
def ask_for_password(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        bot.send_message(chat_id, "🚫 You are not authorized to use this bot.")
        return

    bot.send_message(chat_id, "Please enter your Gmail password (or App Password):")
    bot.register_next_step_handler(message, get_password)

# Get Gmail Password from User and Start Registration
def get_password(message):
    chat_id = message.chat.id
    user_data[chat_id]["password"] = message.text
    bot.send_message(chat_id, "🚀 Starting Cloudways registration...")
    register_cloudways(chat_id)

# Cloudways Registration Function
def register_cloudways(chat_id):
    email_address = user_data[chat_id]["email"]
    email_password = user_data[chat_id]["password"]
    cloudways_password = "SecurePass123!"  # Default password

    # Generate random details
    first_name = fake.first_name()
    last_name = fake.last_name()
    phone = fake.phone_number()
    company = fake.company()
    website = fake.url()

    # Start Web Automation
    bot.send_message(chat_id, "⏳ Registering account... Please wait.")
    driver = webdriver.Opera(executable_path=opera_driver_path, options=options)
    driver.get("https://www.cloudways.com/en/free-trial.php")
    time.sleep(3)

    # Fill the registration form
    driver.find_element(By.NAME, "first_name").send_keys(first_name)
    driver.find_element(By.NAME, "last_name").send_keys(last_name)
    driver.find_element(By.NAME, "email").send_keys(email_address)
    driver.find_element(By.NAME, "password").send_keys(cloudways_password)
    driver.find_element(By.NAME, "phone").send_keys(phone)
    driver.find_element(By.NAME, "company").send_keys(company)
    driver.find_element(By.NAME, "website").send_keys(website)

    # Submit the form
    driver.find_element(By.NAME, "agree_terms").click()
    driver.find_element(By.NAME, "signup").click()
    time.sleep(5)
    driver.quit()

    bot.send_message(chat_id, "✅ Registration completed! Checking email for verification...")

    # Email Verification Process
    verification_link = get_verification_link(email_address, email_password)
    
    if verification_link:
        bot.send_message(chat_id, f"🔗 Verification link found: {verification_link}")
        
        # Open verification link in Opera
        driver = webdriver.Opera(executable_path=opera_driver_path, options=options)
        driver.get(verification_link)
        time.sleep(5)
        driver.quit()
        
        bot.send_message(chat_id, "✅ Cloudways account verified successfully!")
    else:
        bot.send_message(chat_id, "❌ No verification email found. Please check manually.")

# Function to Get Verification Link from Gmail
def get_verification_link(email_address, email_password):
    try:
        mail = imapclient.IMAPClient("imap.gmail.com", ssl=True)
        mail.login(email_address, email_password)
        mail.select_folder("INBOX", readonly=True)

        # Search for Cloudways email
        messages = mail.search(["FROM", "no-reply@cloudways.com"])
        for msg_id in messages[::-1]:
            msg_data = mail.fetch(msg_id, ["RFC822"])
            raw_email = msg_data[msg_id][b"RFC822"]
            msg = email.message_from_bytes(raw_email)

            # Extract email content
            email_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        email_body = part.get_payload(decode=True).decode()
            else:
                email_body = msg.get_payload(decode=True).decode()

            # Find the verification link
            match = re.search(r'href="(https://[^\s]+cloudways.com[^\s]+verify[^\s]+)"', email_body)
            if match:
                return match.group(1)
    
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Error fetching verification email: {str(e)}")
    
    return None

# Start Bot Polling
bot.polling()