import requests
import time, datetime
import smtplib
from email.message import EmailMessage

CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC = "send-reminder"
WORKER_ID = "python-worker-3"




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

    # email credentials
    email_address = "digipro-demo@ikmail.com"

    f = open("password.txt")
    password = f.readline()
    f.close()

    # compose email
    message = (
        f"Guten Tag\n\n"
        f"Am TBD haben Sie uns folgendes Feedback übermittelt:\n"
        f"\"{data['feedbackText']}\"\n\n"
        f"Um Ihr Feedback bearbeiten zu können, bitten wir Sie um folgende zusätzlichen Informationen:\n"
        f"\"{data['query']}\"\n\n"
        f"Für Ihre Antwort in den nächsten 7 Tagen sind wir dankbar.\n\n"
        f"Freundliche Grüsse\n\n\n"
        f"Digipro Demo AG\n"
        f"Teststrasse 1\n"
        f"6000 Zürich"
    )

    # create the email
    msg = EmailMessage()
    msg["Subject"] = "Reminder: Nachfrage zu Ihrem Feedback "
    msg["From"] = email_address
    msg["To"] = data["email"]
    msg.set_content(message)

    # send the email
    with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
        smtp.login(email_address, password)
        smtp.send_message(msg)

    print(data)


while True:
    tasks = fetch_and_lock()
    for task in tasks:
        task_id = task['id']
        variables = {k: v['value'] for k, v in task['variables'].items()}
        print(f"Fetched task {task_id} with variables {variables}")

        send_email(variables, task_id)
        complete_task(task_id, variables)
    time.sleep(5)