import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Gmail SMTP Setup
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "charishccheung@gmail.com"
EMAIL_PASSWORD = "ystr eypo brcz jare"
EMAIL_RECIPIENT = "charishccheung@gmail.com"

# Function to send email
def send_email(subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

        log_message("📧 Email sent successfully!")

    except Exception as e:
        log_message(f"⚠️ Email sending failed: {e}")

def log_message(message):
    with open("test_cron_log.txt", "a") as log_file:
        log_file.write(f"[{datetime.now()}] {message}\n")

def test_cron_job():
    url = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_en.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "rounds" in data and isinstance(data["rounds"], list) and len(data["rounds"]) > 0:
            latest_draw = data["rounds"][0].get("drawCRS", "N/A")  # Get CRS score safely
            latest_draw_name = data["rounds"][0].get("drawName", "N/A")
            message = f"Latest CRS Score for {latest_draw_name}: {latest_draw}"
        else:
            message = "Cannot read response"

        # Send email
        send_email("🇨🇦 [TEST-Phase-2][Github] Express Entry Draw Alert!", message)
        log_message(f"✅ Sent email: {message}")

    except requests.RequestException as e:
        log_message(f"⚠️ Error fetching data: {e}")
        send_email("🇨🇦 [TEST] Express Entry Draw Alert!", "Cannot read response")

# Run once
test_cron_job()
