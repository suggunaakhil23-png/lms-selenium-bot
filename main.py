from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

students = [
    {
        "username": "2410040134",
        "password": "Akhil@2006",
        "email": "2410040134@klh.edu.in"
    },
    {
        "username": "2410040120",
        "password": "Yasar_0806",
        "email": "yasarshaik0806@gmail.com"
    }
]

sender_email = "suggunaakhil@gmail.com"
app_password = "nvgbvitrypngzkyu"

for student in students:

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 40)

    driver.get("https://lms.klh.edu.in/my/")

    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(student["username"])
    driver.find_element(By.NAME, "password").send_keys(student["password"])
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
            try:
                container = item.find_element(By.XPATH, "ancestor::*[self::li or self::div][1]")
                if "overdue" not in container.text.lower():
                    continue
            except:
                continue

            try:
                title = container.find_element(
                    By.XPATH,
                    ".//small[contains(@class,'mb-0')]"
                ).text.strip()
            except:
                title = item.text.strip()

            announcements.append({
                "title": title,
                "date": current_date if current_date else "N/A",
                "status": "Overdue",
                "link": item.get_attribute("href")
            })

    driver.quit()

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = student["email"]
    message["Subject"] = "LMS Overdue Assignments"

    body = ""

    for item in announcements:
        body += f"Title: {item['title']}\n"
        body += f"Date: {item['date']}\n"
        body += f"Status: {item['status']}\n"
        body += f"Submission Link: {item['link']}\n"
        body += "-" * 60 + "\n"

    if not announcements:
        body = "No overdue assignments found."

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(message)
    server.quit()

print("Emails Sent Successfully")