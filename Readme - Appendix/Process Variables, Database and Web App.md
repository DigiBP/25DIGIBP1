# Process Variables



# Database

- Camunda Engine Persistence: The solution did not introduce a separate relational database for process data. All feedback case information (submitted fields, process variables, task assignments, etc.) is stored in Camunda’s internal database as part of the workflow state. This built-in persistence guarantees that process context is saved reliably (with transaction support) and can be queried via Camunda’s history if needed. It sufficed for ensuring data durability and auditability within the scope of this project.

- Volume and Complexity: The expected volume of feedback cases and associated data is moderate, and the querying requirements are relatively simple (mostly tracking the status of a case or reviewing its details). Given this scope, using a full-fledged external database for application data was not strictly necessary. Camunda’s history service and task list already provide insights into each case’s progress and outcome, which covers the fundamental needs.

- Excel as Output Log: To facilitate easy access for stakeholders and to have a consolidated report of all feedback, an Excel file is used as a lightweight data store for output. At process completion, key information (such as feedback ID, submitter name, summary of feedback, department measures, dates, and outcome) is written to an Excel spreadsheet. This approach was chosen instead of a custom database or UI for reporting because stakeholders are comfortable with Excel for reviewing and filtering data. It provides a quick way to share results (e.g., the Feedback Master can email the Excel log periodically) without additional software.

- Justification: Using Camunda’s persistence plus an Excel report strikes a balance between complexity and functionality. A traditional database and custom reporting UI were beyond the project’s time constraints and were not required to meet the core requirements. By avoiding unnecessary infrastructure, we reduced maintenance overhead. If the process expands in the future (e.g., a much higher volume of feedback or more complex analytics needs), the data export to a proper database can be revisited. For now, the combination of Camunda’s internal storage (for operational needs) and an Excel-based log (for managerial reporting) meets all requirements with minimal complexity.


## Status Coventions

| Status value | Meaning in lifecycle          | 
| ------------ | ----------------------------- | 
| `open`       | Initial, still running        | 
| `withdrawn`  | User withdrew feedback        | 
| `terminate`  | **Marker**: request full stop | 
| `cancelled`  | Instance already killed       | 


# Web App

