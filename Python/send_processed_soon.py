import time
import smtplib
import traceback
from pathlib import Path
from email.message import EmailMessage
from art import art

from SupportFunctions import *



TOPIC = "send_processed_soon"
WORKER_ID = "python-worker-10"



def send_email(data: dict, business_key):
    """
    Compose and send an HTML-formatted confirmation email to inform the user
    that their feedback has been received and will be processed soon.

    Args:
        data: Dictionary containing user details and feedback content.
        business_key: Unique identifier used to retrieve the original feedback date.
    """

    # compose email
    message_header = "Wir haben Ihr Feedback erhalten"

    message_before_conv = (
        f"Guten Tag {data['firstName']} {data['lastName']}\n\n\n"
        f"Am {get_date(int(business_key))} haben Sie uns ein Feedback übermittelt. "
        f"Wir haben Ihr Anliegen aufgenommen und werden dies in naher Zukunft bearbeiten.\n\n"
        f"Ihr Feedback:"
    )

    message_after_conv = ""

    # create html body
    html_body = get_conversation_html_mail(message_header=message_header,
                                           message_before_conv=message_before_conv,
                                           conversation=data["feedbackText"],
                                           message_after_conv=message_after_conv,
                                           only_show_initial=True)



    msg = EmailMessage()
    msg["Subject"] = "Empfangsbestätigung Ihres Feedbacks"
    msg["From"] = EMAIL_USER
    msg["To"] = data["email"]

    msg.set_content(html_body, subtype="html")

    # send the email
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print(data)


if __name__ == "__main__":
    print(f"Worker \"{Path(__file__).name}\" started — polling Camunda...")
    try:
        time.sleep(2)
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
                    except PermissionError:
                        print("Excel in use, try again later")
                        time.sleep(30)
                    except Exception as exc:
                        print(f"Error in task {task_id}: {exc} {art('confused scratch')}")
                        traceback.print_exc()

            except Exception as exc:
                print(f"Fetch error: {exc} {art('table flip2')}")
                traceback.print_exc()

            time.sleep(5)

    except KeyboardInterrupt:
        pass