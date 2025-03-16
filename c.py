import telebot
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from faker import Faker

# Replace with your actual Telegram Bot Token & Admin ID
BOT_TOKEN = "8197356432:AAEr4OsAoVSa87jzmU_7-QEfWiuFY_50KdQ"
ADMIN_ID = 7353797869

# Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Generate Fake Data
fake = Faker()

# Configure Chrome for Headless Mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without opening a browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Start Chrome WebDriver (Without Installing Chrome Manually)
def get_driver():
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to Register on Cloudways
def register_cloudways(chat_id, email, password):
    driver = get_driver()
    driver.get("https://www.cloudways.com/en/signup")

    # Auto-fill Registration Form
    driver.find_element("name", "email").send_keys(email)
    driver.find_element("name", "password").send_keys(password)
    driver.find_element("name", "first_name").send_keys(fake.first_name())
    driver.find_element("name", "last_name").send_keys(fake.last_name())
    driver.find_element("name", "phone").send_keys(fake.phone_number())
    driver.find_element("name", "company").send_keys(fake.company())
    
    time.sleep(2)  # Wait for form validation
    driver.find_element("xpath", "//button[contains(text(),'Start Free')]").click()

    time.sleep(5)  # Wait for submission
    driver.quit()

    bot.send_message(chat_id, "✅ Cloudways Account Created Successfully!")

# Handle "/start" Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome! Send your Gmail & Password to create an account.")

# Handle User Input
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if "@" in message.text and "." in message.text:
        email = message.text
        bot.send_message(message.chat.id, "✅ Email received! Now send your password.")
        bot.register_next_step_handler(message, lambda msg: register_cloudways(message.chat.id, email, msg.text))
    else:
        bot.send_message(message.chat.id, "❌ Invalid email. Please enter a valid Gmail.")

# Run the Bot
bot.polling()