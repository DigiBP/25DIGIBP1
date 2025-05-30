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



# Executive Summary

---- TBD


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

---- SCREENSHOT OF AS IS PROCESS MODEL ----

The current feedback process at SVK has significant structural weaknesses:

- Feedback is collected **informally** via email, phone, or paper
- There is **no central system or responsible role**
- Processing is **inconsistent and undocumented**
- No escalation exists for unresolved or critical feedback
- Stakeholders **receive no updates or closure**
- There is **no structured categorization** or trend reporting

---- CONCLUSIVE TEXT WHICH TRANSITIONS SEAMLESSSLY TO TO-BE CHAPTER


## Requirements for To-Be Process

---- DESCRIPTION OF THE REQUIREMENTS

- Clear process ownership and traceability
- Automated follow-ups and stakeholder communication
- Compliance with ISO and internal quality goals
- Alignment with best practices in business process management (BPM)



# To-Be Process

---- INTRO

The new system leverages **Camunda 7** for workflow orchestration and **BPMN 2.0 / DMN** for structured process and decision modeling. The goal is to systematically **collect**, **classify**, **process**, and **analyze** customer feedback while improving transparency, accountability, and responsiveness across departments.


---- SCREENSHOT OF STRATEGIC MODEL (Here it is not clearly defined how specific feedbacktypes are processed) ----


---- DESCRIBE THE IDEA IN DETAIL -> WHO DOES WHAT (INCLUDING THE DESCRIPTION OF THE NEW ROLE AND ENTITY)

              -- New Role: Feedback Master

              A dedicated employee (or team) who is responsible for:

              - Receiving and classifying all feedback
              - Routing feedback to the appropriate department
              - Managing SLA deadlines, follow-ups, and escalations
              - Ensuring communication with stakeholders
              - Maintaining data quality and traceability

              -- New Entity: Review Board

              A cross-functional board that:

              - Meets **biweekly** to review all feedback (processed and open)
              - Identifies trends, recurring issues, or systemic opportunities
              - Oversees feedback categories like praise and complaints
              - Ensures the ISO 9001:2015 cycle of improvement is embedded
  


              Handling Scenarios
              As a first step, different Handling Scenarios for different types of feedback have been defined.

              - **Scenario 1**: Low-urgency suggestions or negative feedback are added to the Review Board backlog for periodic review. They might still be handled operationally but are tracked to identify recurring themes.

              - **Scenario 2**: High-impact or complex feedback is forwarded to the appropriate department. The Feedback Master identifies and assigns the responsible team during classification.

              - **Scenario 3**: Routine issues that the Feedback Master can resolve directly are implemented immediately. The stakeholder is notified, and the resolution is logged.

              - **Scenario 4**: Positive feedback (e.g., praise or kudos) is stored in the Review Board backlog for potential sharing and celebration during regular review meetings.



---- SCREENSHOT OF OPERATIONAL PROCESS MODEL


---- TRANSITION TO "TECHNICAL IMPLEMENTATION



## Technical Implementation

----  DESCRIBE THE TECHNOLOGICAL FRAMEWORK AND WHY WE USE WHICH TECHNOLOGY AND FOR WHAT WE USE IT (PURPOSE)



| Component       | Purpose                                   |
|-----------------|-------------------------------------------|
| **Camunda 7**   | Workflow automation and BPM execution     |
| **BPMN 2.0**    | Process modeling language                 |
| **DMN**         | Business rule modeling for routing/classification |
| **JotForm**     | Frontend for stakeholder feedback capture |
| **MAKE**        | Bridge between JotForm and Workflow Engine|
| **Python Scripts** | Implement Service Tasks                |



----  INSERT A SCREENSHOT OF THE OPERATIONAL PROCESS MODEL AND INSERT SOME ICONS OF THE COMPONENTS ON THE PLACE WHERE THEY BELONG




### MAKE Scenarios


### Database

Database is excel file -> argue why

is created automatically with first submission


#### Status Coventions

| Status value | Meaning in lifecycle          | Set by                                 | Picked up by                           |
| ------------ | ----------------------------- | -------------------------------------- | -------------------------------------- |
| `open`       | Initial, still running        | `store_feedback_in_db.py`              | —                                      |
| `withdrawn`  | User withdrew feedback        | `set_withdrawn_in_db.py`               | —                                      |
| `terminate`  | **Marker**: request full stop | Any script / UI that decides to cancel | **`terminate_cancelled_instances.py`** |
| `cancelled`  | Instance already killed       | `terminate_cancelled_instances.py`     | —                                      |




### Service Tasks

| Script Name  | Explanation                   | Connected Camunda Element (s)          | ...............                        |
| ------------ | ----------------------------- | -------------------------------------- | -------------------------------------- |
|              |                               |                                        | —                                      |








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
