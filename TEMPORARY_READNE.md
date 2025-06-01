

| Python File                             | Description                                                                                                                                                                     |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| launch_all_workers.py                   | This module launches all workers of this project. When stopped, it also shuts all the workers down safely.                                                                      |
| prepare_feedback_supplementation_form.py | !TODO @Kevin, can you describe them better than i can?                                                                                                                          |
| prepare_measure_documentation_form.py   |                                                                                                                                                                                 |
| process_feedback_supplementation.py     |                                                                                                                                                                                 |
| save_classification_in_db.py            | After the feedback master classifies feedback, this worker updates the database. Also sets classification attributes to "NA" if not applicable in the classification.           |
| save_measures_taken_in_db.py            | Appends measures taken in the database. The text is appended and not overwritten because there could be documented measures present beforehand, that was written by the webapp. |
| save_query_in_db.py                     | Saves the query that was composed by the feedbackmaster into the database.                                                                                                      |
| send_department_mail.py                 | Sends a documentation request to another SVK department.                                                                                                                        |
| send_department_reminder_mail.py        | Same as send_department_mail.py but with reminder text.                                                                                                                         |
| send_feedback_implemented.py            | Sends an email to the feedback giver when the feedback was implemented.                                                                                                         |
| send_feedback_received.py               | Sends an email to the feedback giver that informs them that SVK received the feedback.                                                                                          |
| send_information_ceo.py                 | Sends an email to the CEO when a feedback was classified with high priority.                                                                                                    |
| send_processed_soon.py                  | Sends an email to the feedback giver that the feedback is going to be processed soon. This email is sent when the feedback receives the status "review-board".                  |
| send_query_mail.py                      | Sends an email to the feedback giver, containing the converstation history and a hyperlink to the answering jotform form.                                                       |
| send_query_reminder_mail.py             | Same as send_query_mail.py but with reminder text.                                                                                                                              |
| send_thank_you_message.py               | Sends an email to the feedback giver when the feedback was positive.                                                                                                            |
| send_withdrawal_message.py              | Sends an email to the feedback giver that informs them, that the feedback was withdrawn.                                                                                        |
| set_review_board_in_db.py               | Sets the feedback status in the database to "review-board".                                                                                                                     |
| set_withdrawn_in_db.py                  | Sets the feedback status in the database to "withdrawn".                                                                                                                        |
| store_feedback_in_db.py                 | Saves feedback in the Excel based database after new feedback is submitted. Also the worker creates a new database when there is no existing one.                               |
| terminate_terminated_instances.py       | This worker scans the database for terminated feedback periodically. When terminated feedback is found, the worker sends a terminate request to the workflow engine.            |
| SupportFunctions.py                     | This Module contains functions and constants used in different workers. See the next table for further details.                                                                 |




```powershell
docker run --rm `
  -v "${PWD}\config.json:/app/config.json" `
  -v "${PWD}\api_key.txt:/app/api_key.txt" `
  -v "${PWD}\password.txt:/app/password.txt" `
  -v "C:\Test:/host" `
  feedback-management-app
```


```json
{
  "camundaEngineUrl": "https://digibp.engine.martinlab.science/engine-rest",
  "excelFilePath": "/host/form_data.xlsm",
  "passwordFilePath": "password.txt",
  "apiKeyPath": "api_key.txt",
  "tenantID": "25DIGIBP12",
  "documentationFormID": "251324255618051",
  "supplementationFormID": "251256180381049"
}
```