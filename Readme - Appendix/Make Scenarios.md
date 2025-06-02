# Make (Integromat) Scenarios  

Three Make blueprints bridge **JotForm** and **Camunda**:

1. **Webhook trigger** – each scenario starts with *watchForSubmissions*, authenticated via the JotForm API key and bound to the specific form so that only submissions from that form fire the scenario. 
2. **Payload assembly** – a `json:CreateJSON` step formats the data into Camunda’s message schema:

   ```json
   {
     "tenantId": "25DIGIBP12",
     "businessKey": "<JotForm-submission-ID>",
     "messageName": "<CAMUNDA_MESSAGE>",
     "processVariables": { ... }
   }
3. **HTTP call** – the JSON is posted to /engine-rest/message, correlating either to a start event (initial submission) or to an intermediate message catch event (supplement / department measures).

The three blueprints apply this pattern as summarised below:

| Scenario (blueprint file)                                                                  | Trigger (JotForm event)                   | Action                                   | Process variables populated                               | Camunda global message reference                 |
| ------------------------------------------------------------------------------------------ | ----------------------------------------- | ---------------------------------------- | --------------------------------------------------------- | ------------------------------- |
| **Initial Feedback Submission**<br>`Make – initial submission.json`                        | Submitter sends the first feedback form   | Starts a new process instance            | `email`, `phone`, `lastName`, `firstName`, `feedbackText` | `JOTFORM_SUBMITTED`             |
| **Submission Supplementation**<br>`Make – submission supplementation.json`                 | Submitter answers a query | Correlates the waiting *Receive Task* "Wait for Stakeholder Response" | `queryAnswer`                   | `JOTFORM_SUPPLEMENTED`          |
| **Department Measure Documentation**<br>`Make – Documentation of department measures.json` | Department submits its measure documentation form   | Correlates the waiting *Receive Task* "Wait for Documentation of Measures Taken" for the department response | `measuresTaken`            | `DEPARTMENT_MEASURES_SUBMITTED` |

> **Note** – All scenarios assign `tenantId = 25DIGIBP12`.  
> *Initial Feedback Submission* uses the JotForm `submissionID` as the `businessKey`.  
> *Submission Supplementation* and *Department Measure Documentation* contain a hidden field `Feedback ID`, pre-populated by the Camunda task **Prepare Feedback Supplementation Form** with that same business key, ensuring every message correlates to the correct process instance.
