# JotForm Specifications  

Below, each section presents one of the three forms used in the feedback process.  
For every form you will find a screenshot of the form, the public URL, and the purpose of the form.

---

## 1&nbsp;· Initial Feedback Submission  

![Initial Submission Form](Readme%20-%20Appendix/Pictures/Jotform_InitialSubmission.png)  

**Form URL:** <https://form.jotform.com/251255809932058>  

**Purpose:** Captures the stakeholder’s original feedback together with basic contact details; the submission ID becomes the Camunda `businessKey`.  

---

## 2&nbsp;· Feedback Supplementation  

![Supplementation Form](Readme%20-%20Appendix/Pictures/Jotform_Supplementation.png)  

**Form URL:** <https://form.jotform.com/251256180381049>  

**Purpose:** Allows the stakeholder to provide additional information requested by the Feedback Master; pre-filled with the initial feedback and the clarification question.  

---

## 3&nbsp;· Department Measure Documentation  

![Department Measures Form](Readme%20-%20Appendix/Pictures/Jotform_DepartmentMeasures.png)  

**Form URL:** <https://form.jotform.com/251324255618051>  

**Purpose:** Enables department representatives to document the corrective or improvement actions they will take in response to the feedback.  

---

## Deployment  

To clone these forms into another JotForm workspace, follow the official *Import / Clone* steps[^1]:

1. **Open My Forms › Create Form › Import**  
   ![Clone Step 1](Readme%20-%20Appendix/Pictures/Jotform_CloneStep1.png)  

2. **Choose “From a Webpage”, paste the Form URL, and confirm**  
   ![Clone Step 2](Readme%20-%20Appendix/Pictures/Jotform_CloneStep2.png)  

3. The form appears in *My Forms* with a new ID; open it and check that *all field properties* (especially **Unique Name / Field ID**) match the originals.  

> **Important:** Do **not** rename or delete fields. Any change to a field’s *Unique Name* alters its ID, breaking the mappings in Python scripts and Make scenarios. If you must modify a field, update the corresponding variable names in:
> * Python external-task scripts  
> * `json:CreateJSON` mappers inside the three Make blueprints

[^1]: JotForm help article “Export and Import Forms” <https://www.jotform.com/answers/1459343-export-and-import-forms>
