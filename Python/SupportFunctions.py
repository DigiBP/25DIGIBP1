"""


SupportFunctions.py

Shared constants and utility functions used by worker scripts in the project.
Handles:
- Configuration loading
- Email content generation
- Camunda engine communication
- HTML formatting helpers


"""

import pandas as pd
import html
import re
import requests
import json
from datetime import datetime


# read config file
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
f.close()


# get constants that are imported by worker python files
with open(config["passwordFilePath"]) as f:
    EMAIL_PASSWORD = f.readline()
f.close()


with open(config["apiKeyPath"]) as f:
    API_KEY = f.readline()
f.close()

EXCEL_FILE = config["excelFilePath"]
EMAIL_USER = config["emailUser"]
EMAIL_HOST = config["emailHost"]
EMAIL_PORT = config["emailPort"]

CEO_NAME = config["ceoName"]
CEO_EMAIL = config["ceoEmail"]




def get_date(business_key):
    """
    Retrieve the feedback date for a given business key from the Excel file.

    Args:
        business_key (str): Unique identifier for the business case.

    Returns:
        str: The date string associated with the feedback.
    """

    data = pd.read_excel("form_data.xlsx", sheet_name="feedbackData")
    data = data.set_index("businessKey")

    return data.loc[business_key, "feedbackDate"]



def get_department_email(department_name):
    """
    Get the department email address from config by department name.

    Args:
        department_name (str): Name of the department.

    Returns:
        str: Department email address.

    Raises:
        ValueError: If department not found in config.
    """

    for department in config.get("departments", []):
        if department.get("departmentName") == department_name:
            return department.get("departmentEmail")

    raise ValueError(f"Department '{department_name}' not found in config.")



def fetch_and_lock(worker_id, topic):
    """
    Fetch and lock one external task from Camunda for a specific topic.

    Args:
        worker_id (str): ID of the worker requesting the task.
        topic (str): The topic to subscribe to.

    Returns:
        dict: JSON response from Camunda containing the task.
    """

    response = requests.post(url=f"{config['camundaEngineUrl']}/external-task/fetchAndLock",
                             json={
                                   "workerId": worker_id,
                                   "maxTasks": 1,
                                   "usePriority": False,
                                   "topics": [{
                                        "topicName": topic,
                                        "lockDuration": 10000,
                                        "tenantId": config["tenantID"]
                                        }]
                                   })
    #print(response.json())
    return response.json()




def complete_task(task_id, variables, worker_id, send_variables = "none"):
    """
    Complete a Camunda task and optionally send process variables.

    Args:
        task_id (str): ID of the task to complete.
        variables (dict): Variable dictionary to send.
        worker_id (str): ID of the completing worker.
        send_variables (str): "none", "yes", or "new" to determine variable behavior.
    """

    if send_variables == "new":
        new_variables = {
                        "feedbackText": {
                            "type": "String",
                            "value": variables["feedbackText"],
                            "valueInfo": {}
                        },
                        "firstName": {
                            "type": "String",
                            "value": variables["firstName"],
                            "valueInfo": {}
                        },
                        "lastName": {
                            "type": "String",
                            "value": variables["lastName"],
                            "valueInfo": {}
                        },
                        "needsClarification": {
                            "type": "Boolean",
                            "value": variables["needsClarification"],
                            "valueInfo": {}
                        },
                        "phone": {
                            "type": "String",
                            "value": variables["phone"],
                            "valueInfo": {}
                        },
                        "feedbackType": {
                            "type": "String",
                            "value": variables["feedbackType"],
                            "valueInfo": {}
                        },
                        "email": {
                            "type": "String",
                            "value": variables["email"],
                            "valueInfo": {}
                        }
                    }

        if "urgency" in variables:
            new_variables["urgency"] = {
                            "type": "String",
                            "value": variables["urgency"],
                            "valueInfo": {}
                        }
        else:
            new_variables["urgency"] = {
                "type": "String",
                "value": "NA",
                "valueInfo": {}
            }

        if "impactScope" in variables:
            new_variables["impactScope"] = {
                            "type": "String",
                            "value": variables["impactScope"],
                            "valueInfo": {}
                        }
        else:
            new_variables["impactScope"] = {
                "type": "String",
                "value": "NA",
                "valueInfo": {}
            }

        if "immediateAction" in variables:
            new_variables["immediateAction"] = {
                "type": "String",
                "value": variables["immediateAction"],
                "valueInfo": {}
            }
        else:
            new_variables["immediateAction"] = {
                "type": "String",
                "value": "NA",
                "valueInfo": {}
            }


    elif send_variables == "yes":
        new_variables = variables

    else:
        new_variables = {}


    payload = {
               "workerId": worker_id,
               "variables": new_variables
               }
    response = requests.post(url=f"{config['camundaEngineUrl']}/external-task/{task_id}/complete",
                             json=payload)
    print(response.text)
    #print(json.dumps(payload, indent=2))




# Marker regexes for split_conversation
RE_QUERY_HEAD = re.compile(r"\n{0,2}Unsere Rückfrage an Sie:\n", re.MULTILINE)
RE_RESPONSE_HEAD = re.compile(r"\n{0,2}Rückmeldung vom (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}):\n", re.MULTILINE)

def split_conversation(full_text: str):
   """
   Split conversation text into individual feedback-reply pairs.

   Args:
        full_text (str): The complete conversation string.

   Returns:
        tuple: Initial feedback and a list of (query, timestamp, answer) tuples.
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





def newline_to_br(text: str):
    return html.escape(text).replace("\n", "<br>")





def space_to_nbsp(text: str):
    return html.escape(text).replace("\n", "<br>")





def get_simple_html_mail(message_header, message):
    """
    Create a basic HTML mail with a header and message body.

    Args:
        message_header (str): Header title for the mail.
        message (str): Message body content.

    Returns:
        str: Complete HTML email string.
    """

    year = datetime.now().year

    content_card = f"""
      <tr>
        <td style="background-color:#0073b3;padding:24px 32px;">
          <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
            {space_to_nbsp(message_header)}
          </h1>
        </td>
      </tr>

      <tr>
        <td style="padding:32px;color:#333333;">
          <p>{newline_to_br(message)}</p>
        </td>
      </tr>
    """


    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">
                            
                {content_card}

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

    return html_body




def get_quote_html_mail(message_header, message_before_quote, quote, message_after_quote):
    """
    Create an HTML mail with a quoted block between two text sections.

    Args:
        message_header (str)
        message_before_quote (str)
        quote (str)
        message_after_quote (str)

    Returns:
        str: HTML mail body
    """

    year = datetime.now().year

    content_card = f"""
      <tr>
        <td style="background-color:#0073b3;padding:24px 32px;">
          <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
            {space_to_nbsp(message_header)}
          </h1>
        </td>
      </tr>

      <tr>
        <td style="padding:32px;color:#333333;">
          <p>{newline_to_br(message_before_quote)}</p>
            <blockquote style="margin:0;border-left:4px solid #0073b3; padding:16px;background-color:#f0f8ff;">
                <em>{newline_to_br(quote)}</em>
            </blockquote>
          <p>{newline_to_br(message_after_quote)}</p>
        </td>
      </tr>
    """

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">

                {content_card}

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

    return html_body





def get_conversation_html_mail(message_header, message_before_conv, conversation, message_after_conv,
                               button_text="", link="", only_show_initial=False, internal=False):
    """
    Generate HTML email content showing a threaded feedback conversation.

    Args:
        message_header (str): Title header of the email.
        message_before_conv (str): Intro text before the conversation thread.
        conversation (str): Raw text containing conversation history (feedbackText).
        message_after_conv (str): Text appended after the conversation.
        button_text (str, optional): Call-to-action button text.
        link (str, optional): URL for the CTA button.
        only_show_initial (bool, optional): If True, show only the initial feedback.
        internal (bool, optional): If True, render email in an internal format.

    Returns:
        str: Complete HTML email string.
    """

    year = datetime.now().year

    initial, convs = split_conversation(conversation)

    conv_html = ""

    if not only_show_initial:
        if not internal:
            conv_html += f"""
                <h3 style="margin:24px 0 8px;color:#0073b3;font-weight:normal;">
                    {space_to_nbsp("Ihr initiales Feedback:")}
                </h3>
                <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                padding:16px;background-color:#f0f8ff;">
                    {newline_to_br(initial)}
                </blockquote>
                """
            for query_text, ts, answer in convs:
                conv_html += f"""
                    <h3 style="margin:24px 0 8px;color:#0073b3;font-weight:normal;">
                        {space_to_nbsp("Unsere Rückfrage an Sie")}
                    </h3>
                    <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                    padding:16px;background-color:#f0f8ff;">
                        {newline_to_br(query_text)}
                    </blockquote>
                    <h3 style="margin:0 0 8px;color:#0073b3;font-weight:normal;">
                        {space_to_nbsp("Rückmeldung vom ")}{ts}
                    </h3>
                    <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                                       padding:16px;background-color:#f0f8ff;">
                        {newline_to_br(answer)}
                    </blockquote>
                """
        else:
            conv_html += f"""
                            <h3 style="margin:24px 0 8px;color:#0073b3;font-weight:normal;">
                                {space_to_nbsp("Initiales Feedback:")}
                            </h3>
                            <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                            padding:16px;background-color:#f0f8ff;">
                                {newline_to_br(initial)}
                            </blockquote>
                            """
            for query_text, ts, answer in convs:
                conv_html += f"""
                                <h3 style="margin:24px 0 8px;color:#0073b3;font-weight:normal;">
                                    {space_to_nbsp("Unsere Rückfrage")}
                                </h3>
                                <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                                padding:16px;background-color:#f0f8ff;">
                                    {newline_to_br(query_text)}
                                </blockquote>
                                <h3 style="margin:0 0 8px;color:#0073b3;font-weight:normal;">
                                    {space_to_nbsp("Rückmeldung vom ")}{ts}
                                </h3>
                                <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                                                   padding:16px;background-color:#f0f8ff;">
                                    {newline_to_br(answer)}
                                </blockquote>
                            """

    else:
        conv_html += f"""
                    <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                    padding:16px;background-color:#f0f8ff;">
                        {newline_to_br(initial)}
                    </blockquote>
                    """

    link_html = ""

    if link:
        link_html = f"""<p style="text-align:center;margin:32px 0;">
                            <a href="{link}" style="background-color:#0073b3;color:#ffffff;text-decoration:none;
        padding:12px 24px;border-radius:4px;font-weight:bold;display:inline-block;">{space_to_nbsp(button_text)}</a>
                        </p>"""

    content_card = f"""
      <tr>
        <td style="background-color:#0073b3;padding:24px 32px;">
          <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
            {space_to_nbsp(message_header)}
          </h1>
        </td>
      </tr>

      <tr>
        <td style="padding:32px;color:#333333;">
          <p>{newline_to_br(message_before_conv)}</p>

            {conv_html}

          <p>{newline_to_br(message_after_conv)}</p>

          {link_html}

        </td>
      </tr>
    """

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">

                {content_card}

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

    return html_body