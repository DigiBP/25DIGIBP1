# Worker Scripts Overview

This document provides an overview of the Python worker scripts used in the feedback management process. Each worker is an independent service that implements the External Task pattern with Camunda BPM. These workers subscribe to specific BPMN service task topics and handle operations such as sending emails, updating an Excel-based database, or interacting with JotForm.

Each script is responsible for one clearly defined task, making the system modular and maintainable. If a script fails, Camunda retries the task automatically. Shared logic and configuration (e.g. email settings, file paths) are encapsulated in a common helper module.

## Execution

All workers are launched concurrently using `subprocess.Popen()` in the `launch_all_workers.py` script. They remain active and poll Camunda for new tasks via the REST API.

## Structure

See the table below for a mapping of worker scripts to their BPMN service tasks and responsibilities:


| **Script Name**                         | **BPMN Service Task**                               | **Purpose** |
|----------------------------------------|-----------------------------------------------------|-------------|
| `store_feedback_in_db.py`              | Store Feedback in Database                          | Write a new feedback entry to the Excel workbook, creating or expanding the table if needed. Includes metadata such as submission date and status. |
| `send_feedback_received.py`            | Notify Stakeholder that Feedback was Received       | Compose and send an HTML-formatted confirmation email to the user acknowledging receipt of their submitted feedback. |
| `save_classification_in_db.py`         | Save Classification in Database                     | Save the classification details of a feedback entry to the Excel database, including feedback type, urgency, impact scope, and forwarding department. Also updates the status to 'open' and clears any previous query. |
| `send_information_ceo.py`              | Inform CEO                                          | Compose and send an HTML-formatted notification email to the CEO about a feedback submission marked as urgent by the Feedback Master. |
| `send_query_mail.py`                   | Send Query-Mail to Stakeholder                      | Compose and send an HTML-formatted email to request clarification from the user regarding their previously submitted feedback. |
| `prepare_supplementation_form.py`      | Prepare Feedback Supplementation Form               | Submit a pre-filled JotForm to request additional information from the user regarding their feedback. Sends the generated submission ID back to Camunda. |
| `save_query_in_db.py`                  | Save Query in DB                                    | Update the Excel feedback database by setting the status to 'clarification' and saving the clarification query for the specified feedback entry. |
| `send_query_reminder_mail.py`          | Send Reminder                                       | Compose and send an HTML-formatted reminder email to request additional information from the user for clarifying their submitted feedback. |
| `set_withdrawn_in_db.py`               | Set Status “Withdrawn” in DB                        | Update the status of a feedback entry in the Excel file to 'withdrawn' based on the provided business key. |
| `prepare_measure_documentation_form.py`| Prepare Measure Documentation Form                  | Submit a pre-filled JotForm with feedback data to request documentation from a department. Sends the resulting submission ID back to Camunda as a process variable. |
| `send_department_mail.py`              | Send Mail to Respective Department                  | Compose and send an HTML-formatted internal email to the responsible department requesting action and documentation on a received feedback item. |
| `send_department_reminder_mail.py`     | Send Reminder to Department                         | Compose and send an HTML-formatted reminder email to the responsible department, urging them to process the feedback and document actions via a linked form. |
| `save_measures_taken_in_db.py`         | Save Measures Taken in DB                           | Append or set the 'measures taken' field in the Excel database for the specified feedback entry, and update its status to 'review-board'. |
| `send_feedback_implemented.py`         | Notify Stakeholder that Feedback was Processed      | Compose and send an HTML-formatted email to inform the user that their feedback has been processed and addressed. |
| `set_review_board_in_db.py`            | Set Status “Review Board” in DB                     | Update the status of a feedback entry in the Excel file to 'review-board' based on the provided business key. |
| `send_thank_you_message.py`            | Send Thank You Message                              | Compose and send an HTML-formatted thank-you email in response to positive feedback submitted by the user. |
| `send_processed_soon.py`               | Send Mail that Feedback will be Processed Soon      | Compose and send an HTML-formatted confirmation email to inform the user that their feedback has been received and will be processed soon. |
| `send_withdrawal_message.py`           | Message that Feedback was Withdrawn                 | Compose and send an HTML-formatted email to inform the user that their feedback has been closed due to a lack of response to a clarification request. |
| `terminate_terminated_instances.py`    | *(Triggered via WebApp – not in BPMN)*              | Scan the Excel database for feedback entries marked for termination, send a termination message to the Camunda workflow engine for each, and update the status in the Excel sheet to 'cancelled' upon success. |



# Configuration Guide

To run the feedback processing system, you must first ensure the correct setup of the configuration files and external resources.

## 🔐 Secrets: Required Local Files

Two files **must be created manually** in your local repository (they are intentionally excluded from version control):

- `api_key.txt` — contains the API key for accessing the JotForm API.
- `password.txt` — contains the password for the email account used to send notifications.

📁 **Recommended location:** place both files in the `python` folder (i.e., the same directory as the worker scripts). If placed there, no changes to the config file are necessary.

## ⚙️ `config.json` Overview

This file defines all runtime settings for the workers and the web application. Below are the key fields and what you might need to adapt:

| **Key**                 | **Description** |
|-------------------------|-----------------|
| `camundaEngineUrl`      | The REST API endpoint of the Camunda engine. Adapt if you're running your own Camunda instance. |
| `excelFilePath`         | Path to the feedback database (Excel). This file is automatically generated on first feedback entry. No need to create it manually. |
| `passwordFilePath`      | Path to the `password.txt` file (see above). |
| `apiKeyPath`            | Path to the `api_key.txt` file (see above). |
| `tenantID`              | Your Camunda tenant ID. Usually fixed per deployment. |
| `documentationFormID`  | JotForm form ID used for internal documentation (departments). |
| `supplementationFormID`| JotForm form ID used for clarification requests to submitters. |
| `emailHost`             | SMTP server for sending emails (e.g., Infomaniak). |
| `emailUser`             | Sender email address used by all workers. |
| `emailPort`             | SMTP port (465 for SSL). |
| `webappHostIP`          | Host IP for the local Flask web interface (usually 127.0.0.1). |
| `webappPort`            | Port for the Flask web interface (default: 5000). |
| `ceoName`               | Name used in emails when notifying leadership. |
| `ceoEmail`              | Recipient address for urgent feedback notifications. |
| `departments`           | List of departments that can receive feedback, each with a name and email. You can add or remove departments here. |

## ✅ Example

If your repository has this structure:
your-repo/
├── python/
│ ├── api_key.txt
│ ├── password.txt
│ ├── config.json
│ └── ...

Then the following entries will work without modification:

```json
"apiKeyPath": "api_key.txt",
"passwordFilePath": "password.txt"
```
