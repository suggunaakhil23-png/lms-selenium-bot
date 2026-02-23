import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


sender_email = os.environ["GMAIL_USER"]
app_password = os.environ["GMAIL_APP_PASS"]


def run_lms(username, password, receiver_email):

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 40)

    driver.get("https://lms.klh.edu.in/my/")

    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.ID, "loginbtn").click()

    wait.until(EC.url_contains("/my/"))

    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    items = driver.find_elements(
        By.XPATH,
        "//h5[contains(@class,'font-weight-bold')] | //a[contains(@href,'mod/assign/view.php')]"
    )

    announcements = []
    current_date = None

    for item in items:
        tag = item.tag_name.lower()

        if tag == "h5":
            current_date = item.text.strip()
            continue

        if tag == "a":
            container = item.find_element(By.XPATH, "ancestor::*[self::li or self::div][1]")

            if "overdue" not in container.text.lower():
                continue

            announcements.append({
                "title": item.text.strip(),
                "date": current_date if current_date else "N/A",
                "link": item.get_attribute("href")
            })

    driver.quit()
    return announcements


if __name__ == "__main__":

    students = [
        {
            "username": os.environ["LMS_USER_1"],
            "password": os.environ["LMS_PASS_1"],
            "email": os.environ["LMS_EMAIL_1"]
        },
        {
            "username": os.environ["LMS_USER_2"],
            "password": os.environ["LMS_PASS_2"],
            "email": os.environ["LMS_EMAIL_2"]
        }
    ]

    for student in students:

        print(f"Running for {student['username']}")

        results = run_lms(
            student["username"],
            student["password"],
            student["email"]
        )

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = student["email"]
        message["Subject"] = "LMS Overdue Assignments"

        body = ""

        if not results:
            body = "No overdue assignments found."
        else:
            for item in results:
                body += f"Title: {item['title']}\n"
                body += f"Date: {item['date']}\n"
                body += f"Link: {item['link']}\n"
                body += "-" * 40 + "\n"

        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)
        server.quit()

        print(f"Email sent to {student['email']}")