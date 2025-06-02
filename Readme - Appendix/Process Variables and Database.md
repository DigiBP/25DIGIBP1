# Process Variables  

The Camunda workflow uses a concise set of process variables.  
Table 1 lists every variable, its data type, the moment of creation, and its main purpose.

| Variable | Type | Created / updated by | Purpose |
|----------|------|----------------------|---------|
| `businessKey` | `String` | **Make – initial submission** (set to JotForm `submissionID`) | Unique identifier for correlating all subsequent messages. |
| `email` | `String` | Make – initial submission | Submitter contact information. |
| `phone` | `String` | Make – initial submission | Optional contact channel for clarifications. |
| `firstName` | `String` | Make – initial submission | Submitter contact information. |
| `lastName` | `String` | Make – initial submission | Submitter contact information. |
| `feedbackText` | `String` | Make – initial submission → appended by Clarification loop | Holds the original feedback plus any query/answer history (timestamped). |
| `feedbackType` | `String` | **Classification Form** (Camunda user task) | Categorical label: `ftPositive`, `ftNegative`, `ftSuggestion`. |
| `urgency` | `String` | Classification Form | `uHigh`, `uMedium`, `uLow`; drives CEO escalation timer. |
| `impactScope` | `String` | Classification Form | `isLarge`, `isSmall`, `isSpecific`; input to DMN decision. |
| `needsClarification` | `Boolean` | Classification Form | Governs entry to the Clarification sub-flow. |
| `immediateAction` | `Boolean` | Classification Form | Indicates whether the Feedback Master can resolve directly (Scenario 3). |
| `forwardToDepartment` | `String` | Classification Form | Department selected when immediate action is **No** in the Classification Form(Scenario 2). |
| `query` | `String` | **Query Form** | Clarification question authored by the Feedback Master and shown to the submitter in the supplementary form. |
| `queryAnswer` | `String` | **Make – submission supplementation** | Submitter’s response to a clarification request. |
| `measuresTaken` | `String` | **Make – documentation of department measures** | Measures taken provided by the department. |
| `scenario` | `String` | **DMN “Define Scenario”** task | `scenario1` … `scenario4`; selects the downstream path. |
| `status` | `String` | Python workers & Web-App | Lifecycle marker: `open`, `clarification`, `review-board`, `complete`, `withdrawn`, `terminate`, `cancelled`. |
| `tenantId` | `String` | - | - |

---

# Database (Excel Workbook)  

SVK required that feedback data remain accessible to non-technical staff without introducing additional database infrastructure.  
Excel was therefore selected because:

* **User familiarity** – employees already analyse data in Excel; no training is needed.  
* **Low volume** – annual feedback volume (currently) is below 100 entries, so concurrency and transaction hazards are negligible.  
* **Cost efficiency** – the organisation’s MS 365 licence covers Excel, avoiding extra DB licences or hosting fees.   

## Worksheet Structure  

| Column name in Excel | Source variable / task | Comment |
|----------------------|------------------------|---------|
| `businessKey` | `businessKey` (Make – initial submission) | Primary key; equals the initial JotForms `submissionID`. |
| `feedbackDate` | Auto-timestamp in **store_feedback_in_db.py** | Date-time of first submission. |
| `feedbackType` | `feedbackType` (Classification Form) | Codes: `ftPositive`, `ftNegative`, `ftSuggestion`. |
| `query` | `query` (Classification Form → Query Form) | Clarification question drafted by the Feedback Master. |
| `email` | `email` (Make – initial submission) | Submitter’s e-mail address. |
| `phone` | `phone` (Make – initial submission) | Optional contact number. |
| `firstName` / `lastName` | `firstName`, `lastName` | Personal details of the submitter. |
| `feedbackText` | `feedbackText` (initial + appended) | Original feedback plus any Q&A history. |
| `needsClarification` | `needsClarification` (Classification Form) | Boolean flag that triggers the clarification sub-flow. |
| `urgency` | `urgency` (Classification Form) | Codes: `uHigh`, `uMedium`, `uLow`. |
| `impactScope` | `impactScope` (Classification Form) | Codes: `isLarge`, `isSmall`, `isSpecific`. |
| `forwardToDepartment` | Dropdown value in Classification Form | Filled only for Scenario 2. |
| `status` | `status` (scripts & web-app) | Lifecycle marker (`open`, `clarification`, …). |
| `measuresTaken` | `measuresTaken` (Make – department measures / Scenario 3 user task) | Corrective actions documented by the department or Feedback Master. |
| `feedbackTypeDE` | Derived in **store_feedback_in_db.py** | German label for reporting (e.g., *Positiv*, *Negativ*). |
| `urgencyDE` | Derived in **store_feedback_in_db.py** | German label for urgency (e.g., *Hoch*, *Mittel*, *Tief*). |
| `impactScopeDE` | Derived in **store_feedback_in_db.py** | German label for scope (e.g., *Gross*, *Klein*, *Spezifisch*). |

*(Column names match the header row in **form_data.xlsx**; any header change must be mirrored in the associated Python scripts.)*

---

## Status Values  

| Status | Meaning in lifecycle |
|--------|----------------------|
| `open` | Feedback received, initial record saved; awaiting classification. |
| `clarification` | Feedback Master has requested additional information from the submitter; process is paused. |
| `review-board` | Case is on the agenda for the bi-weekly Review Board meeting (Scenarios 1 & 4, or after departmental measures). |
| `complete` | Review Board approved the outcome; case closed. |
| `withdrawn` | Submitter does not responst; indicated the feedback is no longer relevant; case closed without further action. |
| `terminate` | Feedback Master (or Review Board) requested termination of the feedbacks process isntance via the web app. |
| `cancelled` | Feedback in status `review-board` was terminated or workflow instance terminated was programmatically ended after a `terminate` request (final status for termianted feedback). |
