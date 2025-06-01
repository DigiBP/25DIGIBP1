## Team Members
| Name          | Email                  |
|---------------|------------------------|
| Julie Klingelschmitt | julie.klingelschmitt@students.fhnw.ch |
| Kevin Maier  | kevin.maier@students.fhnw.ch |
| Loris Mariño | loris.marino@students.fhnw.ch |
| Ramona Stadler | ramona.stadler@students.fhnw.ch |


## Coaches
| Name          | Email                  |
|---------------|------------------------|
| Andreas Martin | andreas.martin@fhnw.ch |
| Charuta Pande | charuta.pande@fhnw.ch |
| Devid Montecchiari  | devid.montecchiari@fhnw.ch |


# Description of the Project

This project aims to implement a standardized and digitized customer feedback management process for the **Schweizerische Verband für Gemeinschaftsaufgaben der Krankenversicherer (SVK)**. 
It complies with the continuous improvement requirements of **ISO 9001:2015**, specifically **clauses 9.1.2 (Customer Satisfaction)** and **9.1.3 (Analysis and Evaluation)**.



---

## Motivation

During an **ISO 9001:2015 audit in 2018**, SVK was advised to improve its feedback management procedures. In response, a PDF-based feedback form was introduced. However, due to lack of integration, clarity, and ownership, usage remained sporadic.

---- DESCRIBE HOW OUR PROJECT TEAM CAME INTO PLAY 

This has lead to the Project Teams mission.


## Project Goal

The project teams mission is to ensure **audit readiness by August 2025** by introducing a **centralized and executable business process**.

The overarching goal is to **digitally transform SVK’s feedback management** by introducing:

- A **central role (Feedback Master)** responsible for classification, routing, and process monitoring
- A **Review Board** that evaluates feedback outcomes biweekly to promote continuous improvement
- Structured, scenario-based process logic that ensures consistency
- Full audit-traceability through Camunda’s workflow engine
- Transparency and responsiveness for internal and external stakeholders

---


## Current (AS-IS) Feedback Process

---- DESCRIBE PROCESS TEXTUALLY (USE TEXT FROM BPM PROJECT)

  - Feedback is collected **informally** via email, phone, or paper
  - There is **no central system or responsible role**
  - Processing is **inconsistent and undocumented**
  - No escalation exists for unresolved or critical feedback
  - Stakeholders **receive no updates or closure**
  - There is **no structured categorization** or trend reporting

Below is an example of how feedback might have been handled:

---- SCREENSHOT OF AS IS PROCESS MODEL ----

Historically, stakeholders submitted feedback by e-mail, phone or paper. Each unit handled its own inbox, resulting in **fragmented ownership**. Issues were forwarded informally, follow-up dates were tracked in personal calendars, and once a matter was ‘handled’ no structured record remained. Consequently SVK could not demonstrate:

* **Traceability** – who did what, when, and with what outcome
* **Timeliness** – whether response times met internal or ISO targets
* **Trend analysis** – aggregated data for management review


---- CONCLUSIVE TEXT WHICH TRANSITIONS SEAMLESSSLY TO TO-BE CHAPTER
  In summary, the legacy workflow lacks both governance and measurable performance indicators. These deficits defined the mandatory requirements for the redesigned (TO-BE) process presented in the next chapter.


## Requirements for To-Be Process

---- DESCRIPTION OF THE REQUIREMENTS

- Clear process ownership and traceability
- Automated follow-ups and stakeholder communication
- Compliance with ISO and internal quality goals
- Alignment with best practices in business process management (BPM)



# To-Be Process

## Description of the To-Be Process  

The future-state workflow is orchestrated end-to-end by a **Camunda 7** BPMN engine. A new case begins when a stakeholder submits feedback via a **JotForm** which is going to be embedded on the SVK website. The submission payload is forwarded through a **Make** scenario (**LINK TO SCENARIO EXPORT**) which instantiates a Camunda process instance; the JotForm *submission ID* (created by Jotform on submission) serves as the **business key**.

![Initial data flow](<Readme - Appendix/DataFlow_initialSubmission.png>)

Immediately after instantiation, the feedback is persisted in SVK’s central data store - an Excel workbook on SVK's local server - and assigned the status **`open`**. A confirmation e-mail is dispatched to the submitter.

![Database save + confirmation](25DIGIBP1/Readme - Appendix/Dataflow_initialSubmissionSaveConfirm.png)

The case is then routed to the newly created role **Feedback Master** (**see Section _XX_ for a full role profile**). The Feedback Master works exclusively in **Camunda Tasklist**, where a Camunda form displays all submission details.

![Classification task](25DIGIBP1/Readme - Appendix/Dataflow_classification.png)

During classification the Feedback Master records three attributes:  

* `feedbackType` – semantic category (positive, negative, suggestion)  
* `urgency` – low, medium, or high  
* `impactScope` – specific, small, large

Please see **"25DIGIBP1/Readme - Appendix/Classification Guardrails.md"** for additional information.

If essential information is missing, the Feedback Master sets the Boolean `needsClarification`.  
She or he also indicates - via `immediateAction` - whether the feedback can be resolved immediately; otherwise the responsible department is selected from a drop-down menu which contains SVKs department names.

After these entries, the record is re-written to the database. An **inclusive gateway** checks `urgency`; if the value is *high*, an escalation e-mail is sent to the CEO.  
An **exclusive gateway** then directs the token either to a *Clarification* sub-flow or to scenario determination, depending on `needsClarification`.

![Save → CEO alert → decision](25DIGIBP1/Readme - Appendix/DataFlow_saveCEOqueryDecision.png)

### Clarification sub-flow  
If clarification is required, Camunda generates a new task for the Feedback Master to phrase a query to the submitter.  
The query text is added to the database and the status changes to **`clarification`**.  
A pre-filled JotForm - including the original submission and the query - is generated, and the submitter receives an e-mail with the link.

![Querying the submitter](25DIGIBP1/Readme - Appendix/DataFlow_querying.png)

Camunda then waits at a *Receive Task* for the supplementary submission. A reminder is e-mailed after **7 days**; if no response arrives within **14 days**, the case is marked **`withdrawn`** and the process instance is terminated.

![Receive supplementary data](25DIGIBP1/Readme - Appendix/DataFlow_ReceiveQueryAnswer.png)

When the submitter answers, another Make scenario correlates the message to Camunda.

![Supplementary form submission](25DIGIBP1/Readme - Appendix/DataFlow_supplementarySubmission.png)

The query and the reply are appended - timestamped - to the process variable `feedbackText`. Control returns to the **Classify Feedback** user task; the sub-flow may loop until all clarifications are complete. The final classification is submitted when  `needsClarification` is cleared, allowing the main flow to continue to define the appropriate scenario for the feedback.

### Scenario selection  
A **Business Rule Task** evaluates the classified variables and outputs one of four predefined handling scenarios (**see *FeedbackScenarios.md***). An exclusive gateway routes accordingly:

*Scenario 1 and 4 – Non-critical items*  
Status is set to **`review-board`**; the submitter receives an acknowledgement e-mail (gratitude in Scenario 4, processing notice in Scenario 1). The item is placed on the agenda of the bi-weekly **Feedback Review Board**.

![Scenario 1 & 4 path](25DIGIBP1/Readme - Appendix/Dataflow_scenario1Scenario4.png)

*Scenario 2 – Department measure required*  
A **Department Measure Documentation** JotForm is pre-populated with `feedbackText` and the submitters contact data (provided with the initial submission form). An e-mail with the form link is sent to the department selected earlier.  
If no response is received within **3 days**, Camunda sends cyclic reminders (3-day interval) until submission arrives. If the department does not respond, feedback review board will get aware of the case.

![Scenario 2 & 3 path](25DIGIBP1/Readme - Appendix/Dataflow_scenario2Scenario3.png)  
![Receive department measure](25DIGIBP1/Readme - Appendix/DataFlow_ReceiveDepartmentMeasureForm.png)

*Scenario 3 – Immediate action by Feedback Master*  
A follow-up user task prompts the Feedback Master to document the actions taken directly.

For Scenarios 2 and 3 the documented measures are persisted to the database, and the submitter is informed that the feedback has been resolved.

### Review Board approval and lifecycle management  
Throughout the lifecycle the Feedback Master (Camunda Tasklist) and Review Board members (dedicated **Feedback Manager Web-App**) can monitor the case.  
The web-app provides dashboards, allows the Review Board to approve a case (**status `complete`**) or terminate it (**status `terminate` and `cancelled`**), and supports ad-hoc data entry if resolution occurred via another channel (e.g., phone).

![Feedback Manager web-app](25DIGIBP1/Readme - Appendix/webapp.png)





# Deployment


- Jotforms will be provided
- MAKE will be provided


- **Decide**:
  - if we host python workers
    - then share excel via onedrive
    - then share config file via onedrive (they can then adapt the TenantID in the config file)
      - say that they could deploy the BPMN files on their TenantID and change the TenantID in the config file
    - say that they can also (easily) login with tenantID 12 (argue why we only have one profile for deployment and feedback MAster)
  
  - if they host python workers 
    - send them password and api key file
    - tell them how to open excel
    - tell them how they could use the config file
    - tell them how to run docker (see below)







If an error arises when trying to open the excel for the first time:
https://support.microsoft.com/de-de/topic/ein-potenziell-gef%C3%A4hrliches-makro-wurde-blockiert-0952faa0-37e7-4316-b61d-5b5ed6024216






## Docker
docker run \
  -v "$(pwd)/api_key.txt:/app/api_key.txt" \
  -v "$(pwd)/password.txt:/app/password.txt" \
  -v "$(pwd)/config.json:/app/config.json" \
  my-python-app

Yes — exactly! 🎯

Here’s a step-by-step summary of what to do on a **new computer**:

---

## ✅ What You Need on the New Computer

1. **Docker installed**
2. **Your Docker image**, either:

   * Built locally again (with your project files), **or**
   * Pulled from a registry (e.g., Docker Hub)
3. A folder with:

   * `api_key.txt`
   * `password.txt`
   * `config.json`

---

## 📁 Example Folder Layout on New Computer

```
my_run_folder/
├── api_key.txt
├── password.txt
├── config.json
```

Assume the image is already available locally (e.g., `my-python-app`).

---

## 🖥️ PowerShell: How to Run It

Open PowerShell, go into the folder:

```powershell
cd path\to\my_run_folder
```

Then run:

```powershell
docker run --rm `
  -v "${PWD}\config.json:/app/config.json" `
  -v "${PWD}\api_key.txt:/app/api_key.txt" `
  -v "${PWD}\password.txt:/app/password.txt" `
  -v "C:\Test:/host" `
  feedback-management-app
```

> ✅ `${PWD}` in PowerShell is equivalent to `$(pwd)` in Bash.

---

## 🧼 Clean, Secure, Portable

* Secrets stay outside the image 🔐
* You don’t need to modify the image on each computer 💻
* Works in production, staging, or testing just by changing the mounted files 🧪

---

Let me know if you also want to package the image for transfer (`docker save`) or push it to Docker Hub.

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



To **export your Docker image** so it can be moved to another computer (e.g., via USB or file transfer), you'll use the `docker save` command.

---

## ✅ Step-by-Step: Export the Image to a `.tar` File

### 1. Save the image as a tarball

```powershell
docker save -o feedback-management-app.tar feedback-management-app
```

* `-o feedback-management-app.tar`: output file
* `feedback-management-app`: name of your image (no `:tag` defaults to `latest`)

This creates a portable `.tar` file you can transfer.





---

## ✅ To Import It on Another Computer

After transferring the `.tar` file:

```powershell
docker load -i feedback-management-app.tar
```

This will load the image into Docker’s local image registry on the new machine.

---

## ✅ Verify It’s There

```powershell
docker images
```

You should see:

```
REPOSITORY               TAG       IMAGE ID       CREATED         SIZE
feedback-management-app  latest    abc123456789   ...             ...
```

Then you can run it like before.

---
