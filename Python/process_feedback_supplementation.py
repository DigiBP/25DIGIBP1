#!/usr/bin/env python3
"""
Camunda External-Task Worker
Topic: append-feedback-text

Features
--------
• Polls Camunda for external tasks on the topic **append-feedback-text** and
  locks one task at a time; completes the task only after feedbackText
  has been updated.

• Reads the process variables
    – **feedbackText**   (String) – may be empty on first run
    – **query**          (String) – the newly formulated question to the stakeholder
    – **queryAnswer**    (String) – the answer just received from the stakeholder

• Appends a new conversation cycle in this exact format:

        <existing feedbackText>

        Unsere Rückfrage an Sie:
        <query>

        Rückmeldung vom <DD.MM.YYYY HH:MM:SS>:
        <queryAnswer>

  – Any trailing blank lines of the existing text are stripped first.
  – Timestamp uses Europe/Berlin; if the OS lacks tzdata it falls back to a
    fixed UTC+2 offset.

• Writes the resulting string back to the process variable **feedbackText** and
  completes the external task.

• Resilient: on network or HTTP errors the lock simply expires and Camunda will
  retry; all events are logged to stdout.

• Tunables at the top:
    POLL_INTERVAL   – seconds between polling cycles (default 5)
    LOCK_DURATION   – external-task lock in ms (default 10 000)
"""
import time
import requests
from datetime import datetime, timezone, timedelta

try:
    from zoneinfo import ZoneInfo
    TZ_BERLIN = ZoneInfo("Europe/Berlin")
except Exception:
    # Fallback if tzdata is missing (UTC+2 for summertime, adjust if needed)
    TZ_BERLIN = timezone(timedelta(hours=2))

# ── Camunda / worker settings ────────────────────────────────────────────────
CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC      = "append_feedback_text"
WORKER_ID  = "python-worker-append-45"
TENANT_ID  = "25DIGIBP12"

POLL_INTERVAL = 5         # seconds between polling cycles
LOCK_DURATION = 10_000    # ms – must exceed the worst-case handling time

# ── Camunda helper functions ─────────────────────────────────────────────────
def fetch_and_lock(max_tasks: int = 1):
    """Fetch at most `max_tasks` external tasks for our topic."""
    resp = requests.post(
        f"{CAMUNDA_ENGINE_URL}/external-task/fetchAndLock",
        json={
            "workerId": WORKER_ID,
            "maxTasks": max_tasks,
            "usePriority": False,
            "topics": [{
                "topicName":          TOPIC,
                "lockDuration":       LOCK_DURATION,
                "tenantId":           TENANT_ID,
                "includeBusinessKey": True,
            }],
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def complete_task(task_id: str, variables: dict | None = None):
    """Complete the external task and (optionally) set new variables."""
    requests.post(
        f"{CAMUNDA_ENGINE_URL}/external-task/{task_id}/complete",
        json={
            "workerId": WORKER_ID,
            "variables": variables or {},
        },
        timeout=10,
    ).raise_for_status()


# ── Business logic ──────────────────────────────────────────────────────────
def handle_task(task: dict):
    """Append query + queryAnswer to feedbackText and return it to Camunda."""
    task_id      = task["id"]
    vars_camunda = {k: v["value"] for k, v in task["variables"].items()}

    feedback_text = vars_camunda.get("feedbackText", "") or ""
    query         = vars_camunda.get("query", "") or ""
    query_answer  = vars_camunda.get("queryAnswer", "") or ""

    # Timestamp in Europe/Berlin (with fallback if tzdata missing)
    ts = datetime.now(TZ_BERLIN).strftime("%d.%m.%Y %H:%M:%S")

    updated_text = (
        f"{feedback_text.rstrip()}"          # strip trailing blank lines
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

    complete_task(task_id, camunda_vars)
    print(f"✓ Task {task_id} completed — feedbackText updated")


# ── Worker loop ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Feedback appender started — polling Camunda for tasks …")
    while True:
        try:
            for task in fetch_and_lock():
                try:
                    handle_task(task)
                except requests.HTTPError as exc:
                    # Lock expires and Camunda will retry automatically
                    print(f"HTTP error in task {task['id']}: {exc}")
                except Exception as exc:
                    print(f"Unexpected error in task {task['id']}: {exc}")
        except Exception as exc:
            print(f"Fetch error: {exc}")

        time.sleep(POLL_INTERVAL)
