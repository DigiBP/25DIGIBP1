# Feedback Management Process at SVK


This project aims to implement a standardized and digitized customer feedback management process for the **Schweizerische Verband für Gemeinschaftsaufgaben der Krankenversicherer (SVK)**. It complies with the continuous improvement requirements of **ISO 9001:2015**, specifically **clauses 9.1.2 (Customer Satisfaction)** and **9.1.3 (Analysis and Evaluation)**.

The new system leverages **Camunda 7** for workflow orchestration and **BPMN 2.0 / DMN** for structured process and decision modeling. The goal is to systematically **collect**, **classify**, **process**, and **analyze** customer feedback while improving transparency, accountability, and responsiveness across departments.

---

## Motivation

During an **ISO 9001:2015 audit in 2018**, SVK was advised to improve its feedback management procedures. In response, a PDF-based feedback form was introduced. However, due to lack of integration, clarity, and ownership, usage remained sporadic.

To ensure **audit readiness by August 2025**, SVK now introduces a **centralized and executable business process**, ensuring:

- Clear process ownership and traceability
- Automated follow-ups and stakeholder communication
- Compliance with ISO and internal quality goals
- Alignment with best practices in business process management (BPM)

---

## Project Goal

The overarching goal is to **digitally transform SVK’s feedback management** by introducing:

- A **central role (Feedback Master)** responsible for classification, routing, and process monitoring
- A **Review Board** that evaluates feedback outcomes biweekly to promote continuous improvement
- Structured, scenario-based process logic that ensures consistency
- Full audit-traceability through Camunda’s workflow engine
- Transparency and responsiveness for internal and external stakeholders

---

## Technologies Used

| Component       | Purpose                                   |
|----------------|-------------------------------------------|
| **Camunda 7**   | Workflow automation and BPM execution     |
| **BPMN 2.0**     | Process modeling language                 |
| **DMN**         | Business rule modeling for routing/classification |
| **JotForm**     | Frontend for stakeholder feedback capture |
| **REST APIs**   | TBD |

---

## Organizational Enhancements

### New Role: Feedback Master

A dedicated employee (or team) who is responsible for:

- Receiving and classifying all feedback
- Routing feedback to the appropriate department
- Managing SLA deadlines, follow-ups, and escalations
- Ensuring communication with stakeholders
- Maintaining data quality and traceability

### New Entity: Review Board

A cross-functional board that:

- Meets **biweekly** to review all feedback (processed and open)
- Identifies trends, recurring issues, or systemic opportunities
- Oversees feedback categories like praise and complaints
- Ensures the ISO 9001:2015 cycle of improvement is embedded

---

## Current (AS-IS) Feedback Process

The current feedback process at SVK has significant structural weaknesses:

- Feedback is collected **informally** via email, phone, or paper
- There is **no central system or responsible role**
- Processing is **inconsistent and undocumented**
- No escalation exists for unresolved or critical feedback
- Stakeholders **receive no updates or closure**
- There is **no structured categorization** or trend reporting

---

## Proposed (To-Be) Process

CURRENTLY IN DEVELOPMENT PHASE. 

As a first step, different Handling Scenarios for different types of feedback have been defined.

## Handling Scenarios

- **Scenario 1**: Low-urgency suggestions or negative feedback are added to the Review Board backlog for periodic review. They might still be handled operationally but are tracked to identify recurring themes.

- **Scenario 2**: High-impact or complex feedback is forwarded to the appropriate department. The Feedback Master identifies and assigns the responsible team during classification.

- **Scenario 3**: Routine issues that the Feedback Master can resolve directly are implemented immediately. The stakeholder is notified, and the resolution is logged.

- **Scenario 4**: Positive feedback (e.g., praise or kudos) is stored in the Review Board backlog for potential sharing and celebration during regular review meetings.


## Scripts

| Script Name  | Explanation                   | ......                                 | ...............                        |
| ------------ | ----------------------------- | -------------------------------------- | -------------------------------------- |
|              |                               |                                        | —                                      |




## Status Coventions

| Status value | Meaning in lifecycle          | Set by                                 | Picked up by                           |
| ------------ | ----------------------------- | -------------------------------------- | -------------------------------------- |
| `open`       | Initial, still running        | `store_feedback_in_db.py`              | —                                      |
| `withdrawn`  | User withdrew feedback        | `set_withdrawn_in_db.py`               | —                                      |
| `terminate`  | **Marker**: request full stop | Any script / UI that decides to cancel | **`terminate_cancelled_instances.py`** |
| `cancelled`  | Instance already killed       | `terminate_cancelled_instances.py`     | —                                      |



---

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



## Deployment

If an error arises when trying to open the excel for the first time:
https://support.microsoft.com/de-de/topic/ein-potenziell-gef%C3%A4hrliches-makro-wurde-blockiert-0952faa0-37e7-4316-b61d-5b5ed6024216
