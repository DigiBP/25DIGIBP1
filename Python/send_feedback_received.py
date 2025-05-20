import requests
import time
import smtplib
from email.message import EmailMessage
from art import tprint, art

from SupportFunctions import get_quote_html_mail


CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC = "send_feedback_received"
WORKER_ID = "python-worker-69"


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


def send_email(data: dict, task_id):

    # compose email
    message_header = "Wir haben Ihr Feedback erhalten"

    message_before_quote = (
        f"Guten Tag\n\n\n"
        f"Vielen Dank für das Einreichen Ihres Feedbacks. Gerne melden wir uns bei Rückfragen und Updates.\n\n"
        f"Ihr Feedback:\n\n"
    )

    quote = data["feedbackText"]

    message_after_quote = (
        f"\n\n"
        f"Freundliche Grüsse\n\n\n"
        f"Digipro Demo AG\n"
        f"Teststrasse 1\n"
        f"6000 Zürich"
    )

    # create html body
    html_body = get_quote_html_mail(message_header, message_before_quote, quote, message_after_quote)

    # create the email
    f = open("password.txt")
    password = f.readline()
    f.close()

    msg = EmailMessage()
    msg["Subject"] = "Empfangsbestätigung Ihres Feedbacks"
    msg["From"] = "digipro-demo@ikmail.com"
    msg["To"] = data["email"]

    msg.set_content(html_body, subtype="html")

    # send the email
    with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
        smtp.login("digipro-demo@ikmail.com", password)
        smtp.send_message(msg)

    print(data)


if __name__ == "__main__":
   tprint("25-DIGIBP-1", font="small")
   print("Worker started — polling Camunda...")
   print(f"{art("hugger")}\n")
   while True:
       try:
           for task in fetch_and_lock():
               task_id = task["id"]
               variables = {k: v["value"] for k, v in task["variables"].items()}
               print(art("hugger"))
               print(f"Fetched task {task_id}")
               try:
                   send_email(variables, task_id)
                   complete_task(task_id, variables)
               except Exception as exc:
                   print(f"Error in task {task_id}: {exc}")
       except Exception as exc:
           print(f"Fetch error: {exc} {art("confused scratch")}")

       time.sleep(5)