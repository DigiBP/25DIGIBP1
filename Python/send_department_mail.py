from __future__ import annotations
import time
import smtplib
import requests
import traceback
from email.message import EmailMessage
from art import tprint, art

from SupportFunctions import get_date, get_conversation_html_mail


CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC = "send_department_email"
WORKER_ID = "python-worker-23"


def fetch_and_lock():
    response = requests.post(f"{CAMUNDA_ENGINE_URL}/external-task/fetchAndLock", json={
        "workerId": WORKER_ID,
        "maxTasks": 1,
        "usePriority": False,
        "topics": [{
            "topicName": TOPIC,
            "lockDuration": 10000,
            "tenantId": "25DIGIBP12"
        }]
    })
    return response.json()


def complete_task(task_id, variables):
    requests.post(f"{CAMUNDA_ENGINE_URL}/external-task/{task_id}/complete", json={
        "workerId": WORKER_ID,
        "variables": {}
    })




def send_email(data: dict, business_key):

    # compose email
    message_header = "Aufforderung zur Umsetzung von Feedback"

    message_before_conv = (
        f"Hallo Zusammen\n\n\n"
        f"Am {get_date(int(business_key))} wurde uns folgendes Feedback übermittelt:\n\n"
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

    # create the email
    f = open("password.txt")
    password = f.readline()
    f.close()

    msg = EmailMessage()
    msg["Subject"] = "Dringendes Feedback"
    msg["From"] = "digipro-demo@ikmail.com"
    msg["To"] = "digipro-demo@ikmail.com"

    msg.set_content(html_body, subtype="html")

    # send the email
    with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
        smtp.login("digipro-demo@ikmail.com", password)
        smtp.send_message(msg)

    print(data)



if __name__ == "__main__":
   tprint("25-DIGIBP-1", font="small")
   print("Worker started — polling Camunda...")
   print(f"{art('hugger')}\n")
   while True:
       try:
           for task in fetch_and_lock():
               task_id = task["id"]
               variables = {k: v["value"] for k, v in task["variables"].items()}
               print(f"Fetched task {task_id}")
               try:
                   business_key = task.get("businessKey", "")
                   send_email(variables, business_key)
                   complete_task(task_id, variables)
               except Exception as exc:
                   print(f"Error in task {task_id}: {exc} {art('confused scratch')}")
                   traceback.print_exc()
       except Exception as exc:
           print(f"Fetch error: {exc} {art('confused scratch')}")
           traceback.print_exc()

       time.sleep(5)