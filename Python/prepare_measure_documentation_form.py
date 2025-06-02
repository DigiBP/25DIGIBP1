import time
import traceback
from urllib.parse import quote_plus
from pathlib import Path
from art import art

from SupportFunctions import *


# read config file
with open("config.json", "r") as f:
    config = json.load(f)
f.close()


TOPIC      = "prepare_measure_documentation_form"
WORKER_ID  = "python-worker-2"
TENANT_ID  = config['tenantID']
FORM_ID = config["documentationFormID"]

JOTFORM_URL = f"https://eu-api.jotform.com/form/{FORM_ID}/submissions?apiKey={quote_plus(API_KEY)}"



def handle_task(task: dict):
    """
    Submit a pre-filled JotForm with feedback data to request documentation from a department.
    Sends the resulting submission ID back to Camunda as a process variable.

    Args:
        task: Dictionary containing Camunda task data and feedback-related variables.
    """

    task_id = task["id"]
    business_key = task.get("businessKey", "")
    vars_ = {k: v["value"] for k, v in task["variables"].items()}

    payload = {
        "submission[15]": business_key,
        "submission[5]": vars_.get("email", ""),
        "submission[3][first]": vars_.get("firstName", ""),
        "submission[3][last]": vars_.get("lastName", ""),
        "submission[4]": vars_.get("phone", ""),
        "submission[6]": vars_.get("feedbackText", ""),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    print(f"→ Submitting to Jotform: {payload}")

    resp = requests.post(JOTFORM_URL, headers=headers, data=payload, timeout=15)
    resp.raise_for_status()

    submission_id = resp.json()["content"]["submissionID"]
    print(f"✓ Jotform submission {submission_id} created")

    camunda_vars = {
        "documentationJotformSubmissionId": {
            "value": submission_id,
            "type":  "String",
        }
    }

    complete_task(task_id=task_id, variables=camunda_vars, worker_id=WORKER_ID, send_variables="yes")
    print(f"Worker \"{Path(__file__).name} completed task {task_id} with business key {business_key}")



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
                        handle_task(task)
                    except Exception as exc:
                        print(f"Error in task {task_id}: {exc} {art('confused scratch')}")
                        traceback.print_exc()

            except Exception as exc:
                print(f"Fetch error: {exc} {art('table flip2')}")
                traceback.print_exc()

            time.sleep(5)

    except KeyboardInterrupt:
        pass