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
- Full audit-traceability
- Transparency and responsiveness for internal and external stakeholders


## Current (AS-IS) Feedback Process

At SVK, although a standardized feedback process exists, it is not actively followed in day-to-day operations. Instead, spontaneous feedback from their varios stakeholders is typically handled ad hoc by individual employees. When feedback is received (most often via email) the employee reviews it to determine whether the content is clear or requires additional information. If clarification is needed, the stakeholder is contacted directly. In the absence of a response, some employees may follow up with a reminder after several days, but there is no consistent handling timeline.

Once enough information has been gathered, employees usually send a confirmation message to acknowledge the input. They then decide on their own whether any follow-up action is necessary. If not, the feedback may be documented informally or simply noted for awareness. If action is required, the steps are defined and tracked individually, without alignment to a central system or predefined process.

In cases where the feedback falls outside the employee’s area of responsibility, it should be forwarded to a colleague. However, because there is no enforced routing procedure, identifying the right contact person often requires extra effort. As a result, the actual handling of feedback varies depending on the person involved.

![As-Is-Process](https://github.com/user-attachments/assets/5a498502-e5b0-42ee-900f-ded90232ac1a)

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

--- 

# To-Be Process
The **To-Be process** operationalises SVK’s feedback management as an executable BPMN 2.0 model. The whole workflow is orchestrated end-to-end by a **Camunda 7** BPMN engine. Its logic can be summarised in five stages:

1. [**Intake**](#intake) – A stakeholder submits feedback via Jotform; a Make scenario starts a Camunda instance and stores the record with status `open`.  
2. [**Classification**](#classification) – The Feedback Master reviews the submission, assigns type, urgency, and impact scope, and decides whether clarification or departmental involvement is required.  
3. [**Clarification (conditional)**](#Clarification) – If additional information is needed, the process launches an asynchronous query–response loop with the submitter; status switches to `clarification` until the loop is closed or withdrawn.  
4. [**Scenario handling**](#scenario-handling--closure) – A DMN decision returns one of four scenarios which result in:  
   * feedback forwarded to the bi-weekly Review Board (`review-board`), 
   * feedback forwarded to applicable department for resolution, or  
   * immediate resolution by the Feedback Master   
5. [**Closure**](#scenario-handling--closure) – Where applicable (Scenarios 2 and 3) the documented measures are captured; in every path the workflow writes the closing entry to the Excel log, notifies the submitter, and transfers the case to the newly developed Feedback-Manager web app, where it awaits final Review Board approval.
6. [**Feedback termination and lifecycle management**](#Feedback-termination-and-lifecycle-management) Throughout the process, the Feedback Master and Review Board track the case in the Web-App. As the last step, feedback is completed in the app.

The following operational process model provides the holistic visual representation of these stages.

![To-Be Process Model](Readme%20-%20Appendix/Pictures/To-Be%20Process%20Model.png)

## Demovideo
The video demonstrates the process using a happy path scenario. Please note that not all functionalities – such as clarification steps – are included.

https://github.com/user-attachments/assets/c1368ce6-763b-48c5-84a6-0831ab784a37


## Intake
A new case begins when a stakeholder submits feedback via a **Jotform** which is going to be embedded on the SVK website. The submission payload is forwarded through a **Make** scenario  ([see further details](Readme%20-%20Appendix/Make%20Scenarios.md)) which instantiates a Camunda process instance; the Jotform *submission ID* (created by Jotform on submission) serves as the **business key**.

![Initial data flow](Readme%20-%20Appendix/Pictures/DataFlow_initialSubmission.png)

Immediately after instantiation, the feedback is persisted in SVK’s central data store - an Excel workbook on SVK's local server - and assigned the status **`open`** (see [Process Variables and Database](Readme%20-%20Appendix/Process%20Variables%20and%20Database.md) for further details to statuses). A confirmation e-mail is dispatched to the submitter.

![Database save + confirmation](Readme%20-%20Appendix/Pictures/Dataflow_initialSubmissionSaveConfirm.png)

## Classification
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

## Clarification
If clarification is required, Camunda generates a new task for the Feedback Master to phrase a query to the submitter.  
The query text is added to the database and the status changes to **`clarification`**.  
A pre-filled Jotform - including the original submission and the query - is generated, and the submitter receives an e-mail with the link.

![Querying the submitter](Readme%20-%20Appendix/Pictures/DataFlow_querying.png)

Camunda then waits at a *Receive Task* for the supplementary submission. A reminder is e-mailed after **7 days**; if no response arrives within **14 days**, the case is marked **`withdrawn`** and the process instance is terminated.

![Receive supplementary data](Readme%20-%20Appendix/Pictures/DataFlow_ReceiveQueryAnswer.png)

When the submitter answers, another Make scenario ([see further details](Readme%20-%20Appendix/Make%20Scenarios.md)) correlates the message to Camunda.

![Supplementary form submission](Readme%20-%20Appendix/Pictures/DataFlow_supplementarySubmission.png)

The query and the reply are appended - timestamped - to the process variable `feedbackText`. Control returns to the **Classify Feedback** user task; the sub-flow may loop until all clarifications are complete. The final classification is submitted when  `needsClarification` is cleared, allowing the main flow to continue to define the appropriate scenario for the feedback.

## Scenario Handling & Closure
A **Business Rule Task** evaluates the classified variables and outputs one of four predefined handling scenarios (see [Feedback Scenarios.md](Readme%20-%20Appendix/Feedback%20Scenarios.md) for further details). An exclusive gateway routes accordingly:

*Scenario 1 and 4 – Non-critical items*  
Status is set to **`review-board`**; the submitter receives an acknowledgement e-mail (gratitude in Scenario 4, processing notice in Scenario 1). The item is placed on the agenda of the bi-weekly **Feedback Review Board**.

![Scenario 1 & 4 path](Readme%20-%20Appendix/Pictures/Dataflow_scenario1Scenario4.png)

*Scenario 2 – Department measure required*  
A **Department Measure Documentation** Jotform is pre-populated with `feedbackText` and the submitters contact data (provided with the initial submission form). An e-mail with the form link is sent to the department selected earlier.  
If no response is received within **3 days**, Camunda sends cyclic reminders (3-day interval) until submission arrives. If the department does not respond, feedback review board will get aware of the case.

![Receive department measure](Readme%20-%20Appendix/Pictures/DataFlow_ReceiveDepartmentMeasureForm.png)

As soon as the departments responsible person submits the form, the form values will again be posted to the camunda workflow engine with the measure documentation by another Make scenario ([see further details](Readme%20-%20Appendix/Make%20Scenarios.md)).

![Scenario 2 & 3 path](Readme%20-%20Appendix/Pictures/Dataflow_scenario2Scenario3.png)

*Scenario 3 – Immediate action by Feedback Master*  
A follow-up user task prompts the Feedback Master to document the actions taken directly.

For Scenarios 2 and 3 the documented measures are persisted to the database, and the submitter is informed that the feedback has been resolved.

## Feedback Termination and Lifecycle Management
Throughout the lifecycle the Feedback Master and Review Board members can monitor the case in the dedicated **Feedback Manager Web-App**.  

The landing page provides a dashboard and lists all feedback items, grouped by their status.

![Feedback-Manager dashboard](Readme%20-%20Appendix/Pictures/webapp.png)

Selecting a row opens a detailed view of the chosen feedback.

![Detailed feedback view](Readme%20-%20Appendix/Pictures/webappDetail.png)

In this view the Feedback Master can set a case to **`terminate`** (e.g., when the submitter withdraws the issue) by clicking the red button.
The web-app then correlates a terminate message to Camunda; the workflow instance ends and the database status becomes **`cancelled`**.

![Event Sub Process: Termination](Readme%20-%20Appendix/Pictures/DataFlow_Termination.png)

The detailed view also allows to record measures taken and grant final approval, which updates the status to **`complete`**.


## Further Documentation  

For implementation details that exceed the scope of this overview, consult the companion documents listed below. Each file resides in *25DIGIBP1/Readme – Appendix/* and expands a specific aspect of the solution.
Use the links below to open each file directly:

| File Name | Scope |
|------------|-------|
| [**Classification Guardrails.md**](Readme%20-%20Appendix/Classification%20Guardrails.md) | Decision criteria for `feedbackType`, `urgency`, and `impactScope`. |
| [**Feedback Scenarios.md**](Readme%20-%20Appendix/Feedback%20Scenarios.md) | Rationale and routing logic of the DMN *Define Scenario* table. |
| [**Jotform.md**](Readme%20-%20Appendix/Jotform.md) | Public URLs, and cloning instructions. |
| [**Make Scenarios.md**](Readme%20-%20Appendix/Make%20Scenarios.md) | Description of the Make blueprints and cloning instructions. |
| [**Process Variables and Database.md**](Readme%20-%20Appendix/Process%20Variables%20and%20Database.md) | Complete list of process variables, database schema, and status semantics. |
| [**Python (Service Workers and Web App).md**](Readme%20-%20Appendix/Python%20(Service%20Workers%20and%20Web%20App).md) | Mapping of each external-task topic to its Python script with a functional summary and description of the web app. |
| [**Role Definitions.md**](Readme%20-%20Appendix/Role%20Definitions.md) | Formal responsibilities and authority boundaries for Feedback Master and Review Board. |
| [**Docker.md**](Readme%20-%20Appendix/Docker.md) | Guide on how to perform the local deployment. |

These sub-documents provide further insights required to replicate, maintain, or extend this solution.




# Deployment  

The solution can be installed in three logical layers - Camunda, integration artefacts (JotForm + Make), and Python workers.  
Wherever further detail is required, links point to the dedicated README Appendices in *Readme – Appendix/*.

---

## 1 Camunda Engine  

1. **Provision Camunda 7** on an on-premise server and confirm that `/engine-rest` is reachable.  
2. **Deploy Camunda artefacts** (`TOBE_Technical_Model.bpmn`, `DMN.dmn`, and the three embedded Camunda forms  
   (`classificationForm.form`, `queryForm.form`, `feedbackMasterMeasureDocumentationForm.form`). .  
3. **Tenant ID**  
   * All external messages reference the Feedback Master’s tenant (default `25DIGIBP12`).  
   * If Camunda administrators and the Feedback Master use separate tenants, open each user task in the *Feedback Master* lane and set the **User Assignment → Tenant ID** property accordingly.  
4. **Classification form dropdown** — add every department name in the `forwardToDepartment`.

---

## 2 Integration Artefacts  

| Step | Action | Reference |
|------|--------|-----------|
| **Clone JotForms** | Import the three public forms into SVK’s JotForm workspace; do **not** alter field names. | [Jotform.md](Readme%20-%20Appendix/Jotform.md) |
| **Import Make blueprints** | Upload the three JSON files, insert the JotForm API key in each *watchForSubmissions* module, select the cloned form, and configure the Camunda REST URL plus `tenantId` (Feedback Master) in the HTTP request module. | [Make Scenarios.md](Readme%20-%20Appendix/Make%20Scenarios.md) |

---

## 3 Python Workers (SVK on-premise)  

SVK operates a pre-built Docker image containing all Python external-task workers.

1. **Pull or load the image** (command in *Docker.md*).  
2. **Mount configuration**  
   * Edit `config.json` (Camunda URL, tenant ID, Excel path).  
   * Provide `api_key.txt` and `password.txt` (supplied separately).  
3. **Run the container** — the `docker run` statement mounts `config.json`, the secrets files, and a host directory that holds `form_data.xlsx`.

Full image and configuration details:  
[Docker.md](Readme%20-%20Appendix/Docker.md) · [Python (Service Workers and Web App).md](Readme%20-%20Appendix/Python%20(Service%20Workers%20and%20Web%20App).md)

---

# Testing (University / Coaches)  

A test environment is hosted in a DeepNote project so reviewers can evaluate the full workflow without installing local infrastructure.  
Camunda artefacts already run on the provided Camunda Enginge on Tenant **`25DIGIBP12`**, JotForms are available and Make scenarios are running; your only task is to execute the Python workers (and later the web app) from DeepNote.

## 1 Testing-Environment Setup  

| Step | Action |
|------|--------|
| 1 | <a href="https://deepnote.com/workspace/maierk-73504f8c-d324-4df7-a9e9-437921c573fe/project/SVK-Feedback-Management-System-695b966e-0260-420f-9d51-bf90028ebc3a/notebook/Launcher-b9aa3c2eb3864129a944f40ad0bac8cb?utm_source=share-modal&utm_medium=product-shared-content&utm_campaign=notebook&utm_content=695b966e-0260-420f-9d51-bf90028ebc3a">**Open Deepnote project**</a> provided by the team; you should have received an invitation via email. |
| 2 | In the sidebar, select **`Launcher`** and run the first script (import script).<br>Then run the worker script to launch all Python external-task workers. |
| 3 | Keep this kernel running while you execute the functional test below. |

> **Deepnote limitation:** only **one** kernel can run at a time. You will later stop the workers and start the web-app script.

## 2 Functional Test Walk-Through  

1. **Submit feedback** — open the public JotForm <a href="https://form.jotform.com/251255809932058">“Initial Feedback”</a>, fill in your own e-mail, and press *Submit*.  
2. **Classify** — log into Camunda Cockpit (tenant `25DIGIBP12`), open the new task, and complete the classification form.  
   * Optionally tick **needsClarification** and author a query to see the clarification loop.  
3. **Clarification loop** (conditional) — check your mailbox, follow the Supplementation link, answer the query, and submit.  
4. **Scenario branching**  
   * *Scenario 3* → in Camunda Tasklist finish **Document Measures**.  
   * *Scenario 2* → log in with test account **digipro-demo@ikmail.com** (password can be found in DeepNote (password.txt)) on <a href="https://login.infomaniak.com/de/login">Infomaniak/login</a>, find the mail and submit the Department Measures form.  
5. **Stop the worker notebook**  
6. **Launch web app** — Run the single cell for the web app, and click the displayed URL below.  
7. **Approve or terminate** — locate your feedback in the web app:  
   * Click **Approve** to set status `complete`, **or**  
   * Click **Terminate** to set status `terminate`; then re-run the worker notebook so Camunda processes the termination message.

For variable definitions and Excel column mapping see [Process Variables, Database and Web App.md](Readme%20-%20Appendix/Process%20Variables%2C%20Database%20and%20Web%20App.md).


