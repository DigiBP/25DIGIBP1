import smtplib
from email.message import EmailMessage

# email credentials
email_address = "digipro-demo@ikmail.com"
password = "4t!RKvZYwRFtAJY"  # replace with your actual password

# create the email
msg = EmailMessage()
msg["Subject"] = "Test Email from Python"
msg["From"] = email_address
msg["To"] = "loris.marino@students.fhnw.ch"
msg.set_content("This is a test email sent via Infomaniak SMTP.")

# send the email
with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
    smtp.login(email_address, password)
    smtp.send_message(msg)