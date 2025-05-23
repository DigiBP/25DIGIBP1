from __future__ import annotations
import time
import datetime as dt
import smtplib
import html
from email.message import EmailMessage


import requests


# ── Constants ────────────────────────────────────────────────────────────────
CAMUNDA_ENGINE_URL = "https://digibp.engine.martinlab.science/engine-rest"
TOPIC      = "send_feedback_received"
WORKER_ID  = "python-worker-35"
TENANT_ID  = "25DIGIBP12"


SMTP_HOST  = "mail.infomaniak.com"
SMTP_PORT  = 465
EMAIL_ADDR = "digipro-demo@ikmail.com"
with open("password.txt") as f:
   EMAIL_PASS = f.readline().strip()



# ── Helper functions ─────────────────────────────────────────────────────────
def nl2br(text: str) -> str:
   """Escape HTML and convert LF to <br> so e-mail clients keep line breaks."""
   return html.escape(text).replace("\n", "<br>")




def fetch_and_lock():

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


   # -------- Plain-text part -------------------------------------------------
   plain = [
       "Guten Tag",
       "",
       "Vielen Dank für das Einreichen Ihres Feedbacks. Gerne melden wir uns bei Rückfragen und Updates.",
       f"\"{data['feedbackText']}\"",
       "",
   ]


   plain += [
       "Freundliche Grüsse",
       "",
       "Digipro Demo AG",
       "Teststrasse 1",
       "6000 Zürich",
   ]
   plain_text = "\n".join(plain)


   # -------- HTML part ------------------------------------------------------

   cards_html = f"""
     <tr>
       <td style="background-color:#0073b3;padding:24px 32px;">
         <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
           Vielen&nbsp;Dank&nbsp;für&nbsp;das&nbsp;Einreichen Ihres Feedbacks.
         </h1>
       </td>
     </tr>


     <tr>
       <td style="padding:32px;color:#333333;">
         <p style="margin-top:0;">Guten&nbsp;Tag,</p>


         <p>Wir&nbsp;haben&nbsp;Ihr&nbsp;Feedback&nbsp;entgegengenommen.&nbsp;Gerne&nbsp;melden&nbsp;
         wir&nbsp;uns&nbsp;bei&nbsp;Rückfragen&nbsp;oder&nbsp;Updates.</p>


         <blockquote style="margin:0;border-left:4px solid #0073b3;
                            padding:16px;background-color:#f0f8ff;">
           <em>{nl2br(data["feedbackText"])}</em>
         </blockquote>
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
   msg["Subject"] = "Empfangsbestätigung Feedback"
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
   print("Feedback recieved worker started — polling Camunda …")
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
