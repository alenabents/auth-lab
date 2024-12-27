import smtplib
from email.mime.text import MIMEText
import os

SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_email(to_email, code):
    msg = MIMEText(f"Your confirmation code is: {code}")
    msg['Subject'] = "Email Confirmation Code"
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())

