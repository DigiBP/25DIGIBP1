# Abstract

With this project, a digital feedback management process was designed and implemented for a service provider in the health insurance sector. The aim was to standardize, digitalize, and align the previously ad-hoc handling of feedback with ISO requirements. The new process enables efficient, traceable, and situation-adaptive processing of feedback from all relevant stakeholder groups.



# People Involved 

## Project Team / Authors
| Name          | Email                  |
|---------------|------------------------|
| Julie Klingelschmitt | julie.klingelschmitt@students.fhnw.ch |
| Kevin Maier  | kevin.maier@students.fhnw.ch |
| Loris Mariño | loris.marino@students.fhnw.ch |
| Ramona Stadler | ramona.stadler@students.fhnw.ch |

## Supervisors
| Name          | Email                  |
|---------------|------------------------|
| Andreas Martin | andreas.martin@fhnw.ch |
| Charuta Pande  | charuta.pande@fhnw.ch |
| Devid Montecchiari | devid.montecchiari@fhnw.ch |



# Description of the Project

This project aims to implement a standardized and digitized customer feedback management process for the **Schweizerische Verband für Gemeinschaftsaufgaben der Krankenversicherer (SVK)**. 
It complies with the continuous improvement requirements of **ISO 9001:2015**, specifically **clauses 9.1.2 (Customer Satisfaction)** and **9.1.3 (Analysis and Evaluation)**.


## Motivation

During an ISO 9001:2015 audit in 2018, SVK was advised to improve its feedback management procedures. In response, a PDF-based feedback form was introduced. However, due to a lack of integration, clarity, and defined responsibilities, the solution remained largely unused.

In the BPM course led by Maja Spahic in the fall semester of 2024, the authors of this project were tasked by SVK with designing an ISO-compliant feedback management process. Based on the highly positive feedback from both the course instructor and SVK, it was decided to continue with the implementation as part of the Digitalization of Business Processes course in the spring semester of 2025.

![image](https://github.com/user-attachments/assets/d546845f-91d6-41a4-9faa-466a607c3a4a)

One of the project team members works as a project and process manager at SVK, which allowed for a well-informed assessment of the organization’s practical needs.

The proposed solution introduces technologies that are new to SVK, specifically Camunda and Make, showcasing modern tools that not only support this specific support process but further hold potential for improving core operational processes.

With only minor adjustments, the developed process is ready for deployment within the organization.


## Project Goal

The project teams mission is to ensure **audit readiness by August 2025** by introducing a **centralized and executable business process**.

The overarching goal is to **digitally transform SVK’s feedback management** by introducing:

- A **central role (Feedback Master)** responsible for classification, routing, and process monitoring
- A **Review Board** that evaluates feedback outcomes biweekly to promote continuous improvement
- Structured, scenario-based process logic that ensures consistency
- Full audit-traceability through Camunda’s workflow engine
- Transparency and responsiveness for internal and external stakeholders


## Current (AS-IS) Feedback Process

At SVK, although a standardized feedback process exists, it is not actively followed in day-to-day operations. Instead, spontaneous feedback from their varios stakeholders is typically handled ad hoc by individual employees. When feedback is received (most often via email) the employee reviews it to determine whether the content is clear or requires additional information. If clarification is needed, the stakeholder is contacted directly. In the absence of a response, some employees may follow up with a reminder after several days, but there is no consistent handling timeline.

Once enough information has been gathered, employees usually send a confirmation message to acknowledge the input. They then decide on their own whether any follow-up action is necessary. If not, the feedback may be documented informally or simply noted for awareness. If action is required, the steps are defined and tracked individually, without alignment to a central system or predefined process.

In cases where the feedback falls outside the employee’s area of responsibility, it should be forwarded to a colleague. However, because there is no enforced routing procedure, identifying the right contact person often requires extra effort. As a result, the actual handling of feedback varies depending on the person involved.

---- SCREENSHOT OF AS IS PROCESS MODEL ----

At SVK, stakeholders typically submit feedback via e-mail, phone or even paper. Each unit manages its own inbox, resulting in fragmented ownership. Issues are forwarded informally, follow-up dates are tracked in personal calendars, and once a matter is considered ‘handled’, no structured record remains. As a result, SVK cannot demonstrate:
  - **Traceability** – who did what, when, and with what outcome
  - **Timeliness** – whether response times met internal or ISO targets
  - **Trend analysis** – aggregated data for management review

## Challenges and Requirements to be adressed with the To-Be Process
| Challenge          | Requirement                  |
|---------------|------------------------|
| Feedback is collected **informally** via email, phone, or paper | Standardizing how feedback is analyzed and handled internally |
| Processing is **inconsistent and undocumented** | Documentation of feedback and Compliance with ISO-Standards |
| There is **no central system or responsible role**  | Clear process ownership and traceability |
| There is **no structured categorization** or trend reporting| Standardized categorization |
| **No standardized escalation** exists for unresolved or critical feedback | Ensuring every feedback is recognized, proceed and answered |
| **Updates or Closure is not guaranteed** for the Feedback Givers  | Automated follow-ups and stakeholder communication |

In summary, the current feedback handling process at SVK is characterized by a lack of governance, transparency, and process reliability. Without clearly assigned responsibilities, centralized documentation, or standard workflows, the organization is unable to ensure traceability, timely responses, or data-driven insights. These deficiencies served as the basis for defining the mandatory requirements of the redesigned TO-BE process, which aims to standardize, digitize, and control feedback management. The following chapter presents this target-state process and the implementation with state-f-the-art tools in detail.

# To-Be Process

bla bla...

![To-Be Process Model](Readme%20-%20Appendix/Pictures/To-Be%20Process%20Model.png)

## Description of the To-Be Process

The future-state workflow is orchestrated end-to-end by a **Camunda 7** BPMN engine. A new case begins when a stakeholder submits feedback via a **Jotform** which is going to be embedded on the SVK website. The submission payload is forwarded through a **Make** scenario  ([Make - initial Submission](Make/)) which instantiates a Camunda process instance; the Jotform *submission ID* (created by Jotform on submission) serves as the **business key**.

![Initial data flow](Readme%20-%20Appendix/Pictures/DataFlow_initialSubmission.png)

Immediately after instantiation, the feedback is persisted in SVK’s central data store - an Excel workbook on SVK's local server - and assigned the status **`open`** (see [Database & web App](Readme%20-%20Appendix/Database%20and%20Web%20App.md) for further details to statuses). A confirmation e-mail is dispatched to the submitter.

![Database save + confirmation](Readme%20-%20Appendix/Pictures/Dataflow_initialSubmissionSaveConfirm.png)

The case is then routed to the newly created role **Feedback Master** (see [Role Definitions.md](Readme%20-%20Appendix/Role%20Definitions.md)). The Feedback Master works exclusively in the **Camunda Tasklist**, where a Camunda form displays all submission details.

![Classification task](Readme%20-%20Appendix/Pictures/Dataflow_classification.png)

During classification the Feedback Master records three attributes:  

* `feedbackType` – semantic category (positive, negative, suggestion)  
* `urgency` – low, medium, or high  
* `impactScope` – specific, small, large

Please see ([Classification Guardrails.md](Readme%20-%20Appendix/Classification%20Guardrails.md)) for additional information.

If essential information is missing, the Feedback Master sets the Boolean `needsClarification`.  
She or he also indicates - via `immediateAction` - whether the feedback can be resolved immediately; otherwise the responsible department is selected from a drop-down menu which contains SVKs department names.

After these entries, the record is re-written to the database. An **inclusive gateway** checks `urgency`; if the value is *high*, an escalation e-mail is sent to the CEO.  
An **exclusive gateway** then directs the token either to a *Clarification* sub-flow or to scenario determination, depending on `needsClarification`.

![Save → CEO alert → decision](Readme%20-%20Appendix/Pictures/DataFlow_saveCEOqueryDecision.png)

### Clarification sub-flow  
If clarification is required, Camunda generates a new task for the Feedback Master to phrase a query to the submitter.  
The query text is added to the database and the status changes to **`clarification`**.  
A pre-filled Jotform - including the original submission and the query - is generated, and the submitter receives an e-mail with the link.

![Querying the submitter](Readme%20-%20Appendix/Pictures/DataFlow_querying.png)

Camunda then waits at a *Receive Task* for the supplementary submission. A reminder is e-mailed after **7 days**; if no response arrives within **14 days**, the case is marked **`withdrawn`** and the process instance is terminated.

![Receive supplementary data](Readme%20-%20Appendix/Pictures/DataFlow_ReceiveQueryAnswer.png)

When the submitter answers, another Make scenario ([Make - submission supplementation](Make/)) correlates the message to Camunda.

![Supplementary form submission](Readme%20-%20Appendix/Pictures/DataFlow_supplementarySubmission.png)

The query and the reply are appended - timestamped - to the process variable `feedbackText`. Control returns to the **Classify Feedback** user task; the sub-flow may loop until all clarifications are complete. The final classification is submitted when  `needsClarification` is cleared, allowing the main flow to continue to define the appropriate scenario for the feedback.

### Scenario selection  
A **Business Rule Task** evaluates the classified variables and outputs one of four predefined handling scenarios (see [Handling Scenarios.md](Readme%20-%20Appendix/Handling%20Scenarios.md) for further details). An exclusive gateway routes accordingly:

*Scenario 1 and 4 – Non-critical items*  
Status is set to **`review-board`**; the submitter receives an acknowledgement e-mail (gratitude in Scenario 4, processing notice in Scenario 1). The item is placed on the agenda of the bi-weekly **Feedback Review Board**.

![Scenario 1 & 4 path](Readme%20-%20Appendix/Pictures/Dataflow_scenario1Scenario4.png)

*Scenario 2 – Department measure required*  
A **Department Measure Documentation** Jotform is pre-populated with `feedbackText` and the submitters contact data (provided with the initial submission form). An e-mail with the form link is sent to the department selected earlier.  
If no response is received within **3 days**, Camunda sends cyclic reminders (3-day interval) until submission arrives. If the department does not respond, feedback review board will get aware of the case.

![Receive department measure](Readme%20-%20Appendix/Pictures/DataFlow_ReceiveDepartmentMeasureForm.png)

As soon as the departments responsible person submits the form, the form values will again be posted to the camunda workflow engine with the measure documentation by another Make scenario ([Make - Documentation of department measures](Make/)).

![Scenario 2 & 3 path](Readme%20-%20Appendix/Pictures/Dataflow_scenario2Scenario3.png)

*Scenario 3 – Immediate action by Feedback Master*  
A follow-up user task prompts the Feedback Master to document the actions taken directly.

For Scenarios 2 and 3 the documented measures are persisted to the database, and the submitter is informed that the feedback has been resolved.

### Feedback termination and lifecycle management  
Throughout the lifecycle the Feedback Master and Review Board members can monitor the case in the dedicated **Feedback Manager Web-App**.  

The landing page provides a dashboard and lists all feedback items, grouped by their status.

![Feedback-Manager dashboard](Readme%20-%20Appendix/Pictures/webapp.png)

Selecting a row opens a detailed view of the chosen feedback.

![Detailed feedback view](Readme%20-%20Appendix/Pictures/webappDetail.png)

In this view the Feedback Master can set a case to **`terminate`** (e.g., when the submitter withdraws the issue).  
The web-app then correlates a terminate message to Camunda; the workflow instance ends and the database status becomes **`cancelled`**.

![Event Sub Process: Termination](Readme%20-%20Appendix/Pictures/DataFlow_Termination.png)

The detailed view also allows to record measures taken and grant final approval, which updates the status to **`complete`**.







# READ UNTIL HERE Deployment


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
