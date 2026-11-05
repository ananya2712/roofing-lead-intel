# HTML Code Walkthrough Prompt

Use this prompt when a user asks for a detailed, source-based website that explains a complete application.

## Task

Inspect the entire codebase and generate one self-contained HTML website that explains the application in enough detail for me to understand it, demonstrate it, and answer technical interview questions.

This is a documentation task. Do not modify application code.

Base every explanation on repository evidence. Clearly distinguish implemented behavior, documented intent, inferred decisions, and proposed production improvements. Do not invent requirements or claim that checks passed without running them.

## 1. Project overview and requirements

Start with the business problem, intended users, and the main user workflows.

Then describe the functional and non-functional requirements considered in the project.

For each requirement, show:
- What the requirement means.
- Whether it is implemented, partially implemented, planned, or unverified.
- The files or functions that support your assessment.
- Relevant tests, if present.

Cover applicable non-functional concerns such as performance, reliability, security, validation, maintainability, accessibility, observability, and scalability. Distinguish measured results from design intentions.

## 2. Directory structure

Show an annotated directory tree covering the application source, configuration, migrations, fixtures, tests, and documentation.

Exclude generated folders such as node_modules, virtual environments, build output, and Git internals.

Explain each important directory’s responsibility and identify application entry points.

## 3. Architecture diagrams

Include readable diagrams showing:
- The overall system: browser, frontend, backend, database, external services, and mock services.
- The main frontend and backend modules and their dependencies.
- The data model and relationships, where applicable.

Label actual components and reference their implementation files. Explain each diagram in plain language.

Use embedded SVG or another self-contained approach so the diagrams work offline without external scripts.

## 4. Complete API inventory and request walkthroughs

Find every application API endpoint, including routes assembled through prefixes or router registration. Clearly separate framework-generated endpoints from application endpoints.

Create an inventory showing:
- HTTP method and full path.
- Purpose.
- Frontend caller, if one exists.
- Request parameters and body.
- Response structure and status codes.
- Authentication or authorization, if implemented.
- Backend handler and relevant file paths.

For every application endpoint, provide a separate end-to-end walkthrough:

User action → frontend component → API client → backend route → validation/dependencies → business logic → database or provider calls → response → frontend state and rendering.

For each step, identify the relevant file and function. Include a sequence diagram and a small, sanitized request/response example.

Explain branches such as validation failures, missing records, duplicate handling, provider failures, retries, and background processing where implemented.

If an endpoint has no frontend caller, say so. If a frontend call has no matching backend route, flag it. Document frontend calls to external services separately.

Avoid one generic diagram that hides differences between endpoints.

## 5. Where data lives

Explain what data is available in which files and storage locations.

Include:
- Synthetic datasets and fixtures.
- Database models, tables, and migrations.
- Request and response schemas.
- Frontend state and browser storage.
- Configuration and environment-variable names.
- Generated or derived values.

For each important dataset or data structure, explain:
- Its location and purpose.
- Main fields and their meanings.
- Whether it is synthetic, live, user-entered, or calculated.
- Which code reads, creates, updates, and persists it.
- Its lifecycle from collection to display.

Show small representative examples without exposing credentials, personal information, or secret values.

## 6. Deterministic rules and business logic

Locate and explain every implemented deterministic business rule, including applicable scoring, filtering, normalization, deduplication, matching, eligibility, status transitions, and tie-breaking rules.

For each rule, show:
- Inputs.
- Exact conditions, thresholds, weights, and calculation order.
- Output.
- Missing-data and boundary behavior.
- Implementation location.
- Relevant tests.

Include worked examples tracing actual fixture records through the rules. Verify that the examples agree with the implementation.

Explain whether repeated runs produce the same result and identify dependencies on time, randomness, configuration, or mutable external data. Distinguish search relevance from business-priority scoring where applicable.

## 7. Key design decisions

Explain the important choices around architecture, stack, component reuse, persistence, integration boundaries, mocks, synchronous or asynchronous work, error handling, and testing.

For each decision, describe:
- What the code does.
- Why it fits the MVP.
- A reasonable alternative and its tradeoff.
- Supporting repository evidence.

Use recorded rationale when available. Otherwise, label your explanation as an inference rather than attributing it to the developer.

## 8. Translation to production

Compare the current implementation with a realistic production version.

Cover applicable changes to:
- Replacing mock data and services with real integrations.
- Credentials, authentication, authorization, and data protection.
- Database deployment, migrations, backups, and connection management.
- API contracts, versioning, and gateway needs.
- Pagination, caching, rate limits, timeouts, retries, and idempotency.
- Background jobs and durable workflows.
- Logging, monitoring, tracing, and alerting.
- Deployment, configuration, and CI/CD.

For each proposed change, explain the current limitation, the trigger that justifies the change, and which existing modules would be affected.

Prioritize essential production work separately from improvements needed only at larger scale. Keep unimplemented capabilities explicitly labeled as proposals.

## 9. Verification and limitations

Summarize existing tests and what they actually verify.

Run relevant, non-destructive checks if practical, and report the results accurately. List missing coverage, inconsistencies, and unresolved questions.

Finish with a short code-walkthrough guide linking to the sections and files most useful for explaining the project.

## HTML requirements

- Produce one self-contained HTML file with embedded CSS and any necessary JavaScript.
- Use no external dependencies, fonts, or network requests.
- Keep the presentation plain: white background, dark text, clear headings, readable tables, and code blocks.
- Provide a table of contents with section anchors.
- Use collapsible sections for detailed endpoint walkthroughs.
- Make diagrams and tables readable on desktop and mobile.
- Include repository-relative file paths, verified function names, and line references where practical.
- Prefer precise, connected explanations over generic descriptions or large pasted code blocks.
- Inspect the rendered page if browser tooling is available and fix layout problems.

Inspect the repository first, then generate the HTML documentation. Do not build features or change application behavior.
