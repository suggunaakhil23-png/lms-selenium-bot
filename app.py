from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from main import run_lms
import pytz
from datetime import datetime

app = Flask(__name__)

def scheduled_job():
    print("Running scheduled LMS automation...")
    run_lms("2410040134", "Akhil@2006", "2410040134@klh.edu.in")
    run_lms("2410040120", "Yasar_0806", "yasarshaik0806@gmail.com")
    print("Automation finished.")

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

scheduler.add_job(
    scheduled_job,
    trigger='cron',
    hour=8,
    minute=0
)

scheduler.start()

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()