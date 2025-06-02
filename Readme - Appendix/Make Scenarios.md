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

All three blueprints apply this pattern as summarised below:

| Scenario (blueprint file)                                                                  | Trigger (JotForm event)                   | Action                                   | Process variables populated                               | Camunda global message reference                 |
| ------------------------------------------------------------------------------------------ | ----------------------------------------- | ---------------------------------------- | --------------------------------------------------------- | ------------------------------- |
| **Initial Feedback Submission**<br>`Make – initial submission.json`                        | Submitter sends the first feedback form   | Starts a new process instance            | `email`, `phone`, `lastName`, `firstName`, `feedbackText` | `JOTFORM_SUBMITTED`             |
| **Submission Supplementation**<br>`Make – submission supplementation.json`                 | Submitter answers a query | Correlates the waiting *Receive Task* "Wait for Stakeholder Response" | `queryAnswer`                   | `JOTFORM_SUPPLEMENTED`          |
| **Department Measure Documentation**<br>`Make – Documentation of department measures.json` | Department submits its measure documentation form   | Correlates the waiting *Receive Task* "Wait for Documentation of Measures Taken" for the department response | `measuresTaken`            | `DEPARTMENT_MEASURES_SUBMITTED` |

> **Note** – All scenarios assign `tenantId = 25DIGIBP12`.  
> *Initial Feedback Submission* uses the JotForm `submissionID` as the `businessKey`.  
> *Submission Supplementation* and *Department Measure Documentation* contain a hidden field `Feedback ID`, pre-populated by the Camunda task **Prepare Feedback Supplementation Form** with that same business key, ensuring every message correlates to the correct process instance.

---

## Deployment  

To reuse these blueprints in another Make (Integromat) workspace:

1. **Import the JSON blueprint**  
   * In Make, click **Scenarios → Create a new scenario → Import Blueprint** and upload the corresponding `.json` file.  

2. **Configure the Webhook module** (`jotform:watchForSubmissions`)  
   * **API key** – paste the JotForm API key for the target account(see [*Jotform Documentation on how to create an API key*](https://www.jotform.com/help/253-how-to-create-a-jotform-api-key/)).  
   * **Form** – select the exact form (see [*JotForm Specifications*](Readme%20-%20Appendix/Jotform.md)).  

3. **Adjust the HTTP Request module** (`http:ActionSendData`)  
   * **URL** – set to the Camunda REST endpoint, e.g. `https://<YOUR-HOST>/engine-rest/message`.  
   * **tenantId** – replace `25DIGIBP12` with the tenant ID used by the Feedback Master in Camunda.  

4. **Save and enable** the scenario. Use the *Run once* button to verify that a test submission from JotForm reaches the correct Camunda process instance. Finally, activate the switch *Immediately as data arrives*.

> **Tip:** Field mappings inside `json:CreateJSON` rely on the JotForm *Unique Names*.  
> If you change form fields, update the corresponding variable names in the mapper to avoid message-correlation errors.
