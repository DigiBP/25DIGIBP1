import time
import smtplib
import traceback
from pathlib import Path
from email.message import EmailMessage
from art import art

from SupportFunctions import *



TOPIC = "send_thank_you_message"
WORKER_ID = "python-worker-13"



def send_email(data: dict, business_key):

    # compose email
    message_header = "Vielen Dank für Ihr Feedback"

    message = (
        f"Guten Tag\n\n\n"
        f"Am {get_date(int(business_key))} haben Sie uns ein positives Feedback übermittelt.\n\n"
        f"Vielen Dank, dass Sie sich die Zeit genommen haben, uns eine Rückmeldung zu geben. "
        f"Gerne wachsen wir sowohl an Lob als auch Kritik!.\n\n"
        f"Freundliche Grüsse\n\n"
        f"Digipro Demo AG\n"
    )

    # create html body
    html_body = get_simple_html_mail(message_header, message)


    msg = EmailMessage()
    msg["Subject"] = "Ihr Feedback"
    msg["From"] = "digipro-demo@ikmail.com"
    msg["To"] = data["email"]

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
        time.sleep(1.3)
        print(f"Worker \"{Path(__file__).name}\" stopped")