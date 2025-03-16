import time
import imapclient
import email
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from faker import Faker

# Initialize Faker for random details
fake = Faker()

# User provides only Gmail and password
email_address = input("Enter your Gmail: ")
email_password = input("Enter your Gmail Password (or App Password): ")
cloudways_password = "SecurePass123!"  # You can modify this if needed

# Generate random details for registration
first_name = fake.first_name()
last_name = fake.last_name()
phone = fake.phone_number()
company = fake.company()
website = fake.url()

# Set up Opera WebDriver
opera_driver_path = "C:/webdriver/operadriver.exe"  # Update with your path
options = webdriver.ChromeOptions()  # Opera is Chromium-based
options.binary_location = "C:/Program Files/Opera/launcher.exe"  # Update if needed
driver = webdriver.Opera(executable_path=opera_driver_path, options=options)

# Open Cloudways signup page
driver.get("https://www.cloudways.com/en/free-trial.php")
time.sleep(3)

# Fill in the registration form
driver.find_element(By.NAME, "first_name").send_keys(first_name)
driver.find_element(By.NAME, "last_name").send_keys(last_name)
driver.find_element(By.NAME, "email").send_keys(email_address)
driver.find_element(By.NAME, "password").send_keys(cloudways_password)
driver.find_element(By.NAME, "phone").send_keys(phone)
driver.find_element(By.NAME, "company").send_keys(company)
driver.find_element(By.NAME, "website").send_keys(website)

# Agree to terms and submit the form
driver.find_element(By.NAME, "agree_terms").click()
driver.find_element(By.NAME, "signup").click()

# Wait for registration to complete
time.sleep(5)
print("Registration completed! Checking email for verification link...")

# Close the browser
driver.quit()

# ---------------------------------------
# Check Gmail for Cloudways Verification Email
# ---------------------------------------
def get_verification_link():
    try:
        # Connect to Gmail via IMAP
        mail = imapclient.IMAPClient("imap.gmail.com", ssl=True)
        mail.login(email_address, email_password)
        mail.select_folder("INBOX", readonly=True)

        # Search for Cloudways email
        messages = mail.search(["FROM", "no-reply@cloudways.com"])
        for msg_id in messages[::-1]:  # Check newest emails first
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

            # Find the verification link in email body
            match = re.search(r'href="(https://[^\s]+cloudways.com[^\s]+verify[^\s]+)"', email_body)
            if match:
                return match.group(1)

    except Exception as e:
        print("Error fetching verification email:", str(e))

    return None


# Get the verification link
verification_link = get_verification_link()

if verification_link:
    print("Verification link found:", verification_link)

    # Open the verification link in Opera
    driver = webdriver.Opera(executable_path=opera_driver_path, options=options)
    driver.get(verification_link)
    time.sleep(5)
    print("Cloudways account verified successfully!")
    driver.quit()
else:
    print("No verification email found. Please check manually.")