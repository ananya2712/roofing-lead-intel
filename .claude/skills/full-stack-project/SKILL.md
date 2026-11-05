---
name: full-stack-project-workflow
description: Use when taking an approved full-stack application from design through implementation, verification, and handoff in this project.
---

# Full-Stack Project Workflow

Use this skill for end-to-end application work in this project. Read the root `AGENTS.md` first. It contains the approved stack and user decisions. Read the focused skill files listed below when their work begins.

## Load the focused skills

- Read [`../backend/SKILL.md`](../backend/SKILL.md) for Flask, API, database, and integration work.
- Read [`../frontend/SKILL.md`](../frontend/SKILL.md) for Next.js, React, TypeScript, Tailwind, and UI work.
- Read [`../documentation/SKILL.md`](../documentation/SKILL.md) when creating or updating project records, diagrams, or the production handoff.
- Read [`../writing/SKILL.md`](../writing/SKILL.md) when writing project prose, interface text, comments, docstrings, or slide text.
- Read [`../presentation/SKILL.md`](../presentation/SKILL.md) at project completion when creating the final deck.

Load only the focused skills that apply to the current task. For full-stack implementation, use the backend and frontend skills together. Do not repeat their detailed rules here. Follow `AGENTS.md` when it sets a project-specific choice.

## Workflow

1. When the user presents a case study without asking for a design directly, ask only scope-changing discovery questions, one at a time. Then inspect the repository and current stack. Learn the users, problem, inputs, outputs, constraints, and features that must wait. Read affected code. Trace its callers, data flow, configuration, and UI. Check for broken behavior, data loss, and data exposure.
2. Discuss the architecture, API, data model, frontend flow, reusable UI foundation, local run method, documentation, production handoff, and test scope. For each durable design decision, explain why it fits the requirements, why a reasonable alternative was not selected, which code and architecture parts it affects, and what would justify changing it in production. Mark unapproved choices as recommendations.
3. Present the proposed design in a concise summary. Include scope, exclusions, user flow, architecture, API, data, frontend, UI, local run, documentation, tests, and open questions. Use the design checklist below and define observable acceptance criteria before implementation. If the user asks for a design directly, give the design with open questions. Do not start with discovery questions.
4. Get user approval before writing application code, creating project scaffolding, or installing dependencies. If the user changes the design, revise the summary and get approval again.
5. After approval, create the progress and decision records, the initial demo guide, and the initial architecture visuals. Follow the documentation skill.
6. Write a short milestone plan. Build the smallest complete user flow first. Reuse project code, platform features, and installed dependencies. Do not add options, abstractions, or dependencies for unapproved future needs.
   If implementation shows that an approved business rule must change, stop work that depends on the change and ask the user to approve it. Until then, record the proposed change as **Pending** in `docs/DECISION_LOG.md`, with its reason and impact. Do not implement the changed rule before approval.
7. At each milestone, update the project records and demo guide. Once the approved flow is implemented, create or update `docs/ARCHITECTURE_AND_DESIGN.md` when completed code changes its contents. State the user-visible result, architecture impact, file responsibilities, and connections between changed files. Review connected callers. Preserve required validation and error handling. Report progress in plain language and link implementation details to the decisions that caused them.
8. Do not write or run automated application tests until all approved functionality is complete. Do not use test-driven development. Then run only the agreed test types from `AGENTS.md`. Use a separate test database. Do not use production data or live provider accounts.
9. Verify the agreed behavior. Check that Docker Compose starts the local app, the main user flow works, and saved data remains after restart. Compare architecture visuals with the implementation. Inspect the affected code path, not only the diff. Report commands, observed results, unchecked items, and known risks.
10. Verify the demo guide against the final implementation. Create the production readiness and extensibility handoff. Mark the demo guide complete only when all approved requirements are complete and the guide matches the observed project.
11. After implementation and final verification, create `docs/PROJECT_DEMO.pptx` with the presentation skill. Structure it from the HTML walkthrough when available. Use observed project evidence. Add speaker notes. Inspect every slide. Record the deck in the project records and demo guide.

## Design checklist and acceptance criteria

Include a short assumptions table in the design:

| Assumption | Status | Evidence or decision needed |
| --- | --- | --- |
| [specific assumption] | Approved or Recommended | [user decision or open question] |

Use **Approved** only for a choice the user confirmed. Use **Recommended** for an unapproved proposal. Keep open questions visible and get approval before implementing a recommendation that changes scope or behavior.

Resolve these points for the approved flow. Mark items that do not apply. Keep unresolved business policies visible and get a decision before implementing behavior that depends on them.

- Record identity: define how the app recognizes the same record across imports, edits, and retries. State how it handles duplicates and conflicting values.
- Source of truth: define which source controls each important value and when user edits take precedence.
- Missing or stale data: distinguish unknown, empty, zero, and outdated values. Define freshness limits and the action available when data is stale.
- Partial failure: define what succeeds, what is saved, and what the user sees when only part of an operation completes.
- Retry behavior: define what can be retried, how duplicate effects are prevented, and when retry attempts stop.
- Time-dependent rules: define the relevant timestamp, time zone, cutoff, and recalculation trigger when time can change a result.

For each complete user flow, state the starting data, user actions, visible result, and required saved state. Include applicable missing-data, failure, retry, and reload cases. Make each criterion observable, such as a visible status or a saved value after restart. Define performance limits only when required and state the measurement conditions. These criteria guide later verification; do not write or run automated application tests before approved functionality is complete.

## Small and complete changes

Choose the smallest complete solution that meets approved requirements. Reuse existing code and dependencies. Keep the current module structure. Do not add generic wrappers or speculative setup. When moving code, preserve validation and error handling. Complete all required caller, configuration, documentation, and UI updates.

Never cut trust-boundary validation, security, accessibility, or error handling that protects data. Keep comments short and explain why the code needs a non-obvious choice. Report checks that you did not run and known limits. Do not claim that the app works unless you observed the required result.

## Testing rules

- Add pytest API and database integration tests after approved functionality is implemented.
- Use the Playwright Python pytest plugin for browser end-to-end tests.
- Do not add unit or smoke tests unless the user changes this decision.
- Do not use test-driven development.
- If another test type appears necessary, explain why and ask before adding it.
- Before reporting that Docker is unavailable, run `docker compose ps` from the project root. If Docker works, report the Compose service status.

Do not use subagent-driven implementation by default. Use it only when the user asks or a task requirement or applicable instruction makes delegation necessary.
