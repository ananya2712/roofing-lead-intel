# Case Study Discovery Questions

Use these questions when a user presents a case study for a software project. The goal is to understand the user problem and the smallest useful outcome before choosing a design.

Ask one question at a time. Start with the user's goal. Ask a follow-up only when the answer can change the scope, user flow, data, or a design decision. Do not ask every question. Do not start with stack or implementation questions.

## Understand the problem

- Who will use the application?
- What task or decision should it help them complete?
- How do they handle this task today?
- What is slow, difficult, or error-prone in the current process?
- What would a useful result look like to the user?

## Define the smallest useful flow

- What action starts the flow?
- What information does the user provide?
- What should the application do with that information?
- What result should the user see?
- What action completes the flow?
- Which feature can wait until after the first version?

## Clarify data and rules

- What main records does the application need to keep?
- Which fields are required, and which can be missing?
- What rules determine the result, score, or category?
- How should the application handle missing, conflicting, or outdated information?
- Should a user be able to review or change an automated result?
- How long must the application keep the records?

## Find integrations and failure cases

- Does the flow need data from another system or service?
- What should happen if that system is slow or unavailable?
- What should the user see when the system returns no result?
- Does the application need to export data or send updates elsewhere?

## Confirm constraints and success

- What does the case study require for the demo or evaluation?
- How will you decide that the first version works?
- Are there time, hosting, privacy, or data-use constraints?
- Is there a known user count, record volume, or response-time need that could affect design?
- Which assumptions should remain open until you can check them?

## Confirm the shared understanding

Summarize the problem, user, core flow, success condition, and features that can wait. Ask the user to correct the summary before you propose the architecture.

Use a short readback:

> The application will help [user] complete [task]. The first version will [core flow] and will succeed when [observable result]. It will not include [deferred features]. Is this correct?
