import smtplib
from email.message import EmailMessage

def send_email(subject, body, email_cfg):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_cfg["sender"]
    msg["To"] = email_cfg["receiver"]
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_cfg["sender"], email_cfg["app_password"])
        smtp.send_message(msg)
