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

    # build the link from the submission ID
    link = f"https://eu.jotform.com/edit/{data['jotformSubmissionId']}"

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
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <!-- Karten-Container -->
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">
                <!-- Kopfbereich -->
                <tr>
                  <td style="background-color:#0073b3;padding:24px 32px;">
                    <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
                      Nachfrage&nbsp;zu&nbsp;Ihrem&nbsp;Feedback
                    </h1>
                  </td>
                </tr>
    
                <!-- Nachricht -->
                <tr>
                  <td style="padding:32px;color:#333333;">
                    <p style="margin-top:0;">Guten&nbsp;Tag,</p>
    
                    <p>am&nbsp;TBD&nbsp;haben&nbsp;Sie&nbsp;uns folgendes Feedback übermittelt:</p>
    
                    <!-- Zitat -->
                    <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                                       padding:16px;background-color:#f0f8ff;">
                      <em>{data['feedbackText']}</em>
                    </blockquote>
    
                    <p>Um&nbsp;Ihr&nbsp;Feedback&nbsp;bearbeiten&nbsp;zu&nbsp;können, bitten&nbsp;wir&nbsp;Sie&nbsp;um&nbsp;folgende&nbsp;zusätzliche&nbsp;Informationen:</p>
    
                    <p style="font-weight:bold;margin-bottom:24px;">{data['query']}</p>
    
                    <!-- Call to Action -->
                    <p style="text-align:center;margin:32px 0;">
                      <a href="{link}"
                         style="background-color:#0073b3;color:#ffffff;text-decoration:none;
                                padding:12px 24px;border-radius:4px;font-weight:bold;display:inline-block;">
                         Rückmeldung&nbsp;geben
                      </a>
                    </p>
    
                    <p>Vielen&nbsp;Dank, dass&nbsp;Sie&nbsp;sich&nbsp;dafür&nbsp;kurz&nbsp;Zeit&nbsp;nehmen.</p>
    
                    <p style="margin-bottom:0;">
                      Freundliche&nbsp;Grüsse<br><br>
                      Digipro&nbsp;Demo&nbsp;AG<br>
                      Teststrasse&nbsp;1<br>
                      6000&nbsp;Zürich
                    </p>
                  </td>
                </tr>
    
                <!-- Fusszeile -->
                <tr>
                  <td style="background-color:#f0f2f4;padding:16px;text-align:center;
                             font-size:12px;color:#666666;">
                    © {datetime.datetime.now().year}&nbsp;Digipro&nbsp;Demo&nbsp;AG&nbsp;• Alle&nbsp;Rechte&nbsp;vorbehalten
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
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