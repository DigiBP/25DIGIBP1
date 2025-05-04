import requests
import time, datetime
import smtplib
from email.message import EmailMessage
from urllib.parse import quote_plus

CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC = "send-query-email"
WORKER_ID = "python-worker-2"




def fetch_and_lock():
    response = requests.post(f"{CAMUNDA_ENGINE_URL}/external-task/fetchAndLock", json={
        "workerId": WORKER_ID,
        "maxTasks": 1,
        "usePriority": False,
        "topics": [{
            "topicName": TOPIC,
            "lockDuration": 10000,
            "tenantId": "25DIGIBP12",
            "includeBusinessKey": True
        }]
    })
    return response.json()


def complete_task(task_id, variables):
    requests.post(f"{CAMUNDA_ENGINE_URL}/external-task/{task_id}/complete", json={
        "workerId": WORKER_ID,
        "variables": {}
    })


def send_email(data: dict, task_id, business_key):

    # E-Mail-Zugangsdaten
    email_address = "digipro-demo@ikmail.com"
    with open("password.txt") as f:
        password = f.readline().strip()


    base_url = "https://www.jotform.com/251103903332039"
    query_string = (
        f"feedbackId={quote_plus(str(business_key))}"
        f"&feedbackText={quote_plus(data['feedbackText'])}"
        f"&query={quote_plus(data['query'])}"
    )
    link = f"{base_url}?{query_string}"


    message_text = (
        "Guten Tag\n\n"
        f"Am TBD haben Sie uns folgendes Feedback übermittelt:\n"
        f"\"{data['feedbackText']}\"\n\n"
        "Um Ihr Feedback bearbeiten zu können, bitten wir Sie um folgende "
        "zusätzliche Informationen:\n"
        f"{data['query']}\n\n"
        f"Rückmeldung geben: {link}\n\n"
        "Vielen Dank, dass Sie sich dafür kurz Zeit nehmen.\n\n"
        "Freundliche Grüsse\n\n"
        "Digipro Demo AG\n"
        "Teststrasse 1\n"
        "6000 Zürich"
    )

    message_html = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif; line-height:1.4;">
        <p>Guten&nbsp;Tag<br><br>
           Am&nbsp;TBD&nbsp;haben&nbsp;Sie&nbsp;uns folgendes Feedback übermittelt:<br>
           „{data['feedbackText']}“<br><br>
           Um&nbsp;Ihr&nbsp;Feedback&nbsp;bearbeiten&nbsp;zu&nbsp;können, bitten&nbsp;wir&nbsp;Sie&nbsp;um&nbsp;folgende&nbsp;zusätzliche&nbsp;Informationen:<br>
           {data['query']}<br><br>
           <a href="{link}">Klicken&nbsp;Sie&nbsp;hier, um&nbsp;Rückmeldung&nbsp;zu&nbsp;geben</a><br><br>
           Vielen&nbsp;Dank, dass&nbsp;Sie&nbsp;sich&nbsp;dafür&nbsp;kurz&nbsp;Zeit&nbsp;nehmen.<br><br>
           Freundliche&nbsp;Grüsse<br><br>
           Digipro&nbsp;Demo&nbsp;AG<br>
           Teststrasse&nbsp;1<br>
           6000&nbsp;Zürich
        </p>
      </body>
    </html>
    """

    # E-Mail zusammensetzen
    msg = EmailMessage()
    msg["Subject"] = "Nachfrage zu Ihrem Feedback"
    msg["From"]    = email_address
    msg["To"]      = data["email"]

    # Plain-Text und HTML in einer Multipart-Alternative-Mail
    msg.set_content(message_text)
    msg.add_alternative(message_html, subtype="html")

    with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
        smtp.login(email_address, password)
        smtp.send_message(msg)

    print(data)


while True:
    tasks = fetch_and_lock()
    for task in tasks:
        task_id = task['id']
        business_key = task.get('businessKey')
        variables = {k: v['value'] for k, v in task['variables'].items()}
        print(f"Fetched task {task_id} with variables {variables}")

        send_email(variables, task_id, business_key)
        complete_task(task_id, variables)
    time.sleep(5)