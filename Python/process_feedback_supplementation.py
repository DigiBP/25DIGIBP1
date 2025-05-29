import time
import traceback
from datetime import  timezone, timedelta
from pathlib import Path
from art import art

from SupportFunctions import *


# read config file
with open("config.json", "r") as f:
    config = json.load(f)
f.close()


TOPIC      = "append_feedback_text"
WORKER_ID  = "python-worker-3"
TENANT_ID  = config["tenantID"]



def handle_task(task: dict):

    task_id = task["id"]
    vars_camunda = {k: v["value"] for k, v in task["variables"].items()}

    feedback_text = vars_camunda.get("feedbackText", "") or ""
    query = vars_camunda.get("query", "") or ""
    query_answer = vars_camunda.get("queryAnswer", "") or ""



    try:
        from zoneinfo import ZoneInfo
        time_zone_berlin = ZoneInfo("Europe/Berlin")
    except Exception:
        # Fallback if tzdata is missing (UTC+2 for summertime, adjust if needed)
        time_zone_berlin = timezone(timedelta(hours=2))
    
    ts = datetime.now(time_zone_berlin).strftime("%d.%m.%Y %H:%M:%S")

    updated_text = (
        f"{feedback_text.rstrip()}" # strip trailing blank lines
        f"\n\nUnsere Rückfrage an Sie:\n"
        f"{query}"
        f"\n\nRückmeldung vom {ts}:\n"
        f"{query_answer}"
    )

    camunda_vars = {
        "feedbackText": {
            "value": updated_text,
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