import smtplib
from email.message import EmailMessage
from SupportFunctions import get_simple_html_mail

# email credentials
email_address = "digipro-demo@ikmail.com"

f = open("password.txt")
password = f.readline()
f.close()



# create the email
msg = EmailMessage()
msg["Subject"] = "Test Email from Python"
msg["From"] = email_address
msg["To"] = email_address



msg.set_content(get_simple_html_mail(submission_id=12,
                                           message_header="Thank you for your feedback",
                                           message="Hello There\n\n\nThe Tesla Cybertruck is an all-electric, battery-powered light-duty truck unveiled by Tesla, Inc. Here's a comprehensive overview of its key features and specifications"), subtype="html")

# send the email
with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
    smtp.login(email_address, password)
    smtp.send_message(msg)