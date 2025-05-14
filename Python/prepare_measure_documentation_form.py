#!/usr/bin/env python3
"""
Camunda 7 external-task worker
──────────────────────────────
Creates a Jotform submission for form 251103903332039 and writes the returned
`submissionID` back to the process as variable `jotformSubmissionId`.

Field mapping (Camunda → Jotform):
  businessKey            → submission[15]
  email                  → submission[5]
  firstName              → submission[3][first]
  lastName               → submission[3][last]
  phone                  → submission[4]
  feedbackText variable  → submission[6]
"""

import os
import time
import requests
from urllib.parse import quote_plus

# ─── Configuration ────────────────────────────────────────────────────────────
CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC      = "prepare_measure_documentation_form"
WORKER_ID  = "python-worker-2"
TENANT_ID  = "25DIGIBP12"

FORM_ID = "251324255618051"
API_KEY = os.getenv(                 # < set JOTFORM_API_KEY env-var in prod!
    "JOTFORM_API_KEY",
    "75f1f0b302477cad1fb52837c2f427db",
)

JOTFORM_URL = (
    f"https://eu-api.jotform.com/form/{FORM_ID}/submissions?apiKey={quote_plus(API_KEY)}"
)

POLL_INTERVAL = 5      # seconds between polling cycles
LOCK_DURATION = 10_000 # ms – must exceed worst-case handling time
# ──────────────────────────────────────────────────────────────────────────────


# ─── Camunda helpers ──────────────────────────────────────────────────────────
def fetch_and_lock(max_tasks: int = 1):
    """Fetch at most `max_tasks` external tasks for our topic."""
    resp = requests.post(
        f"{CAMUNDA_ENGINE_URL}/external-task/fetchAndLock",
        json={
            "workerId": WORKER_ID,
            "maxTasks": max_tasks,
            "usePriority": False,
            "topics": [
                {
                    "topicName": TOPIC,
                    "lockDuration": LOCK_DURATION,
                    "tenantId": TENANT_ID,
                    "includeBusinessKey": True,
                }
            ],
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def complete_task(task_id: str, variables: dict | None = None):
    """Complete the external task and (optionally) store new variables."""
    requests.post(
        f"{CAMUNDA_ENGINE_URL}/external-task/{task_id}/complete",
        json={
            "workerId": WORKER_ID,
            "variables": variables or {},
        },
        timeout=10,
    ).raise_for_status()


# ─── Business logic ───────────────────────────────────────────────────────────
def handle_task(task: dict):
    """Create Jotform submission, return submissionID to Camunda."""
    task_id      = task["id"]
    business_key = task.get("businessKey", "")
    vars_        = {k: v["value"] for k, v in task["variables"].items()}

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

    complete_task(task_id, camunda_vars)
    print(f"✓ Completed Camunda task {task_id} (saved jotformSubmissionId)")


# ─── Main loop ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Jotform worker started — polling Camunda for tasks …")
    while True:
        try:
            for t in fetch_and_lock():
                try:
                    handle_task(t)
                except requests.HTTPError as exc:
                    # The lock will expire, Camunda will retry.
                    print(f"HTTP error in task {t['id']}: {exc}")
                except Exception as exc:
                    print(f"Unexpected error in task {t['id']}: {exc}")
        except Exception as exc:
            print(f"Fetch error: {exc}")

        time.sleep(POLL_INTERVAL)
