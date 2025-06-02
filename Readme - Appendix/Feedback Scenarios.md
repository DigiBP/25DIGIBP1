# Feedback Handling Scenarios

Different Handling Scenarios for different types of feedback have been defined. As soon as the token arrives at the Business Rule Task, one of the following scenarios is defined by using the input of the Feedback Masters classification output:

  ---- SCREENSHOT OF DMN TABLE (pictures/dmnTable.png)

- **Scenario 1**: Low-urgency suggestions or negative feedback that the feedback master can not resolve directly are added to the Review Board backlog for periodic review.

- **Scenario 2**: High-impact or urgent feedback/suggestions is forwarded to the appropriate department. The Feedback Master identifies and assigns the responsible team during classification.

- **Scenario 3**: Feedback or Suggestions that the Feedback Master can/must resolve directly are implemented immediately. 

- **Scenario 4**: Positive feedback (e.g., praise or kudos) is stored in the Review Board backlog for potential sharing and celebration during regular review meetings.

Say that the project team has also created guardrails which support the feedback master on classifying a feedback (Classification Guardrails.md)

Explain the follow up logic with the review board. 
The review board approves every feedback by using the Feedback Manager (web app). 
Thereby, it is ensured that the same persons keep track of the feedback over time and it is ensured that issues and patterns can be detected directly and feedback is generally recognized.


