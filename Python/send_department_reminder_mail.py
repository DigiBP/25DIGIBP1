from __future__ import annotations
import time
import smtplib
import traceback
from pathlib import Path
from email.message import EmailMessage
from art import art

from SupportFunctions import *



TOPIC = "send_department_reminder_email"
WORKER_ID = "python-worker-7"



def send_email(data: dict, business_key):

    # compose email
    message_header = "Aufforderung zur Umsetzung von Feedback"

    message_before_conv = (
        f"Hallo Zusammen\n\n\n"
        f"Am {get_date(int(business_key))} wurde uns Feedback übermittelt:\n\n"
    )

    message_after_conv = (
        f"\n\n"
        f"Kontaktdaten Feedbackgeber:in\n"
        f"{data["firstName"]} {data["lastName"]}\n"
        f"{data["email"]}\n"
        f"{data["phone"]}\n\n"
        f"Bitte bearbeitet dieses Feedback umgehend und dokumentiert die getroffenen Massnahmen in folgendem Formular:\n"
    )

    # create html body
    link = f"https://eu.jotform.com/edit/{data['documentationJotformSubmissionId']}"
    html_body = get_conversation_html_mail(message_header=message_header,
                                           message_before_conv=message_before_conv,
                                           conversation=data["feedbackText"],
                                           message_after_conv=message_after_conv,
                                           button_text="Feedback dokumentieren",
                                           link=link)


    msg = EmailMessage()
    msg["Subject"] = "Dringendes Feedback"
    msg["From"] = "digipro-demo@ikmail.com"
    msg["To"] = "digipro-demo@ikmail.com"

    msg.set_content(html_body, subtype="html")

    # send the email
    with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
        smtp.login("digipro-demo@ikmail.com", PASSWORD)
        smtp.send_message(msg)

    print(data)



if __name__ == "__main__":
    print(f"Worker \"{Path(__file__).name}\" started — polling Camunda...")
    try:
        while True:
            try:
                for task in fetch_and_lock(worker_id=WORKER_ID, topic=TOPIC):
                    business_key = task.get("businessKey", "")
                    task_id = task["id"]
                    variables = {k: v["value"] for k, v in task["variables"].items()}
                    print(f"Worker \"{Path(__file__).name} fetched task {task_id} with business key {business_key}")
                    try:
                        send_email(data=variables, business_key=business_key)
                        complete_task(task_id=task_id, variables=variables, worker_id=WORKER_ID)
                        print(f"Worker \"{Path(__file__).name} completed task {task_id} with business key {business_key}")
                    except Exception as exc:
                        print(f"Error in task {task_id}: {exc} {art('confused scratch')}")
                        traceback.print_exc()

            except Exception as exc:
                print(f"Fetch error: {exc} {art('table flip2')}")
                traceback.print_exc()

            time.sleep(5)

    except KeyboardInterrupt:
        time.sleep(0.7)
        print(f"Worker \"{Path(__file__).name}\" stopped")