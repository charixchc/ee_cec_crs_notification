import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from bs4 import BeautifulSoup
import os

# Gmail SMTP Setup
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "charishccheung@gmail.com"
EMAIL_PASSWORD = "ystr eypo brcz jare"
EMAIL_RECIPIENT = "charishccheung@gmail.com"

# Log file path
LOG_FILE_PATH = "test_cron_log.txt"

# Function to send email
def send_email(subject, message):
    try:
        msg = MIMEText(message, "html")
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
    try:
        with open(LOG_FILE_PATH, "a") as log_file:
            log_file.write(f"[{datetime.now()}] {message}\n")
    except Exception as e:
        print(f"⚠️ Failed to write log: {e}")

def extract_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    link = soup.find('a')
    if link and 'href' in link.attrs:
        return link['href']
    return ""

def ee_cec_crs_notification():
    url = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_en.json"
    domain = "https://www.canada.ca/"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        log_message("Fetched data successfully")

        if "rounds" in data and isinstance(data["rounds"], list) and len(data["rounds"]) > 0:
            latest_draw = data["rounds"][0]
            latest_draw_date = latest_draw.get("drawDate", "N/A")
            today_date = datetime.today().strftime("%Y-%m-%d")
            latest_draw_crs = latest_draw.get("drawCRS", "N/A")  # Get CRS score safely
            latest_draw_name = latest_draw.get("drawName", "N/A")
            latest_draw_tie_breaking_rule = latest_draw.get("drawCutOff", "N/A")
            latest_draw_number = latest_draw.get("drawNumber", "N/A")
            draw_url_html = latest_draw.get("drawNumberURL", "")
            draw_url = extract_url(draw_url_html)
            full_url = domain + draw_url
            log_message(f"Extracted URL: {full_url}")
            message = f"""
                <html>
                <body>
                    <h1>{latest_draw_name} on {latest_draw_date}</h1>
                    <ul>
                        <li><b>CRS score of lowest-ranked candidate invited: </b>{latest_draw_crs}</li>
                        <li><b>Tie-breaking rule: </b>{latest_draw_tie_breaking_rule}</li>
                    </ul>
                    <p>More details: <a href='{full_url}'>{latest_draw_number}</a></p>
                </body>
                </html>
            """


        else:
            message = "Cannot read response"
            log_message("No rounds data found")

        # Send email
        if latest_draw_date >= today_date and latest_draw_name == "Canadian Experience Class":
            send_email(f"🇨🇦 Express Entry Draw Alert! {latest_draw_name} (CRS: {latest_draw_crs})", message)
            log_message(f"✅ Sent email: {message}")

        else:
            log_message(f"🥲 No new draw today. Latest Draw on {latest_draw_date} for {latest_draw_name} with the lowest CRS of {latest_draw_crs}")

    except requests.RequestException as e:
        log_message(f"⚠️ Error fetching data: {e}")
        send_email("[ERR]", "Cannot read response")

# Run once
ee_cec_crs_notification()
