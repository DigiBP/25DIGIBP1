# Feedback Management Process at SVK

## Overview

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

### 👤 New Role: Feedback Master

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

## 📉 Current (AS-IS) Feedback Process

The current feedback process at SVK has significant structural weaknesses:

- Feedback is collected **informally** via email, phone, or paper
- There is **no central system or responsible role**
- Processing is **inconsistent and undocumented**
- No escalation exists for unresolved or critical feedback
- Stakeholders **receive no updates or closure**
- There is **no structured categorization** or trend reporting

---
