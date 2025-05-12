from __future__ import annotations
import re
import time
import datetime as dt
import smtplib
import html
from email.message import EmailMessage

import requests

from SupportFunctions import get_date

# ── Constants ────────────────────────────────────────────────────────────────
CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC      = "send-query-email"
WORKER_ID  = "python-worker-2"
TENANT_ID  = "25DIGIBP12"

SMTP_HOST  = "mail.infomaniak.com"
SMTP_PORT  = 465
EMAIL_ADDR = "digipro-demo@ikmail.com"
with open("password.txt") as f:
    EMAIL_PASS = f.readline().strip()

# Marker regexes
RE_QUERY_HEAD   = re.compile(r"\n{0,2}Unsere Rückfrage an Sie:\n", re.MULTILINE)
RE_RESPONSE_HEAD = re.compile(
    r"\n{0,2}Rückmeldung vom (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}):\n",
    re.MULTILINE,
)

# ── Helper functions ─────────────────────────────────────────────────────────
def nl2br(text: str) -> str:
    """Escape HTML and convert LF to <br> so e-mail clients keep line breaks."""
    return html.escape(text).replace("\n", "<br>")

def split_conversation(full_text: str):
    """
    Returns:
        initial     – text before first query
        conversations – list of (query, timestamp, answer) in chronological order
                       (only pairs that already have an answer).
    Leaves the final, unanswered query out (that will be sent separately).
    """
    initial_end = None
    conversations: list[tuple[str, str, str]] = []

    pos = 0
    first_query_match = RE_QUERY_HEAD.search(full_text)
    if first_query_match:
        initial_end = first_query_match.start()
    else:
        # No query marker at all
        return full_text.strip(), []

    initial = full_text[:initial_end].strip()

    while True:
        q_match = RE_QUERY_HEAD.search(full_text, pos)
        if not q_match:
            break
        q_start = q_match.end()
        r_match = RE_RESPONSE_HEAD.search(full_text, q_start)
        if not r_match:
            # No response for this query → unanswered → stop parsing pairs
            break
        # Extract query text (up to response marker)
        query_text = full_text[q_start : r_match.start()].strip()
        ts = r_match.group(1)
        # Find start of next query to slice the answer properly
        next_q_match = RE_QUERY_HEAD.search(full_text, r_match.end())
        if next_q_match:
            answer_text = full_text[r_match.end() : next_q_match.start()].strip()
            pos = next_q_match.start()
        else:
            answer_text = full_text[r_match.end() :].strip()
            pos = len(full_text)
        conversations.append((query_text, ts, answer_text))

    return initial, conversations

def fetch_and_lock():
    """Fetch at most one External Task for our topic and tenant."""
    resp = requests.post(
        f"{CAMUNDA_ENGINE_URL}/external-task/fetchAndLock",
        json={
            "workerId": WORKER_ID,
            "maxTasks": 1,
            "usePriority": False,
            "topics": [{
                "topicName":          TOPIC,
                "lockDuration":       10_000,  # ms
                "tenantId":           TENANT_ID,
                "includeBusinessKey": True,
            }],
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()

def complete_task(task_id: str):
    """Complete the External Task without adding variables."""
    requests.post(
        f"{CAMUNDA_ENGINE_URL}/external-task/{task_id}/complete",
        json={"workerId": WORKER_ID, "variables": {}},
        timeout=10,
    ).raise_for_status()

# ── Mail composition ─────────────────────────────────────────────────────────
def build_mail(data: dict) -> EmailMessage:
    """
    Create a multipart e-mail with:
      • initial feedback
      • every answered query/response pair (chronological)
      • the current query (data['query'])
      • CTA link
    """
    link = f"https://eu.jotform.com/edit/{data['jotformSubmissionId']}"
    initial, convs = split_conversation(data["feedbackText"])

    # -------- Plain-text part -------------------------------------------------
    plain = [
        "Guten Tag",
        "",
        f"Am {get_date(task_id)} haben Sie uns folgendes Feedback übermittelt:",
        f"\"{initial}\"",
        "",
    ]
    for query_text, ts, answer in convs:
        plain += [
            "Unsere Rückfrage an Sie:",
            query_text,
            "",
            f"--- Rückmeldung vom {ts} ---",
            answer,
            "",
        ]

    plain += [
        "Um Ihr Feedback bearbeiten zu können, bitten wir Sie um folgende zusätzliche Informationen:",
        data["query"],
        "",
        f"Rückmeldung geben: {link}",
        "",
        "Vielen Dank, dass Sie sich dafür kurz Zeit nehmen.",
        "",
        "Freundliche Grüsse",
        "",
        "Digipro Demo AG",
        "Teststrasse 1",
        "6000 Zürich",
    ]
    plain_text = "\n".join(plain)

    # -------- HTML part ------------------------------------------------------
    conv_html = ""
    for query_text, ts, answer in convs:
        conv_html += f"""
            <h3 style="margin:24px 0 8px;color:#0073b3;font-weight:normal;">
              Unsere&nbsp;Rückfrage&nbsp;an&nbsp;Sie
            </h3>
            <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                               padding:16px;background-color:#f0f8ff;">
              {nl2br(query_text)}
            </blockquote>

            <h3 style="margin:0 0 8px;color:#0073b3;font-weight:normal;">
              Rückmeldung&nbsp;vom&nbsp;{ts}
            </h3>
            <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                               padding:16px;background-color:#f0f8ff;">
              {nl2br(answer)}
            </blockquote>
        """

    cards_html = f"""
      <tr>
        <td style="background-color:#0073b3;padding:24px 32px;">
          <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
            Nachfrage&nbsp;zu&nbsp;Ihrem&nbsp;Feedback
          </h1>
        </td>
      </tr>

      <tr>
        <td style="padding:32px;color:#333333;">
          <p style="margin-top:0;">Guten&nbsp;Tag,</p>

          <p>am&nbsp;{get_date(task_id)}&nbsp;haben&nbsp;Sie&nbsp;uns folgendes Feedback übermittelt:</p>

          <blockquote style="margin:0;border-left:4px solid #0073b3;
                             padding:16px;background-color:#f0f8ff;">
            <em>{nl2br(initial)}</em>
          </blockquote>

          {conv_html}   <!-- past conversations inserted here -->

          <p>Um&nbsp;Ihr&nbsp;Feedback&nbsp;bearbeiten&nbsp;zu&nbsp;können, bitten&nbsp;wir&nbsp;Sie&nbsp;um&nbsp;folgende&nbsp;zusätzliche&nbsp;Informationen:</p>

          <p style="font-weight:bold;margin-bottom:24px;">{nl2br(data['query'])}</p>

          <p style="text-align:center;margin:32px 0;">
            <a href="{link}"
               style="background-color:#0073b3;color:#ffffff;text-decoration:none;
                      padding:12px 24px;border-radius:4px;font-weight:bold;display:inline-block;">
               Rückmeldung&nbsp;geben
            </a>
          </p>
        </td>
      </tr>
    """

    year = dt.datetime.now().year
    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">
                {cards_html}
                <!-- Footer -->
                <tr>
                  <td style="background-color:#f0f2f4;padding:16px;text-align:center;
                             font-size:12px;color:#666666;">
                    © {year}&nbsp;Digipro&nbsp;Demo&nbsp;AG&nbsp;• Alle&nbsp;Rechte&nbsp;vorbehalten
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = "Nachfrage zu Ihrem Feedback"
    msg["From"]    = EMAIL_ADDR
    msg["To"]      = data["email"]

    msg.set_content(plain_text)
    msg.add_alternative(html_body, subtype="html")
    return msg

def send_email(data: dict):
    """Send the composed e-mail via SMTP."""
    msg = build_mail(data)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.login(EMAIL_ADDR, EMAIL_PASS)
        smtp.send_message(msg)
    print("E-mail sent to", data["email"])

# ── Worker loop ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Query-mail worker started — polling Camunda …")
    while True:
        try:
            for task in fetch_and_lock():
                task_id = task["id"]
                vars_   = {k: v["value"] for k, v in task["variables"].items()}
                print(f"Fetched task {task_id}")
                try:
                    send_email(vars_)
                    complete_task(task_id)
                except Exception as exc:
                    # Let the lock expire so Camunda retries
                    print(f"Error in task {task_id}: {exc}")
        except Exception as exc:
            print(f"Fetch error: {exc}")

        time.sleep(5)
