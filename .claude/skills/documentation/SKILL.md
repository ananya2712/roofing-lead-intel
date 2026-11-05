---
name: project-documentation
description: Use when creating or updating project records, visual architecture and data-flow diagrams, demo guides, or production handoff documents.
---

# Documentation Skill

Use this skill during an approved project implementation. Do not create project records for a planning-only chat or an instruction-file update. Read the root `AGENTS.md` and the writing skill. Apply ASD-STE100 to every project-authored document.

## Project records

Create these files after design approval and before implementation begins:

- `docs/BUILD_PROGRESS.md` records the goal, approved scope, current status, milestones, and file-by-file changes.
- `docs/DECISION_LOG.md` records durable, cross-cutting decisions and their trade-offs.
- `docs/DEMO_GUIDE.md` explains the implemented project from a demo user's point of view.

Update `BUILD_PROGRESS.md` at each milestone and before a pause. Record status, changed files, reasons, and evidence. Keep the history chronological.

Update `DECISION_LOG.md` when the user approves a durable choice or when an architecture or scope decision changes. Keep file-level implementation details in `BUILD_PROGRESS.md`. Link progress rows to relevant decisions.

Start `DEMO_GUIDE.md` with the intended user flow. Keep it current. Give setup commands, actions, expected results, recovery steps, and limits. Link relevant files to each step, including files the user cannot see. Verify the guide against the final app.

Create `docs/ARCHITECTURE_AND_DESIGN.md` after the approved application flow is implemented. Use `architecture/PROMPT.md` for its content. Mermaid diagrams are permitted inside this Markdown guide. Update the guide in the same change whenever completed code alters a documented API, workflow, business rule, data model, integration, UI state, or deployment behavior. Check affected claims against code before calling the code change finished. Remove stale claims and preserve accurate sections. Refresh verification results only after rerunning the relevant checks. If the code change does not affect the guide, leave it as it is.

Create `docs/DIAGRAMS.md` only when the user requests a separate diagram guide. Then use `architecture/DIAGRAMS_PROMPT.md` and update affected diagrams with completed code changes to flows, dependencies, stored entities, or rules. Verify each arrow and label against code. Follow the diagram format the user requested for that document.

## Evidence, failures, and open policies

Distinguish implemented behavior, observed verification, assumptions, and proposed work. For each verification claim, record the date, command or manual action, environment, input source, expected result, and observed result. Label live, fixture, simulated, and recorded provider data. State whether a check passed, failed, was blocked, or was not run. Static inspection and builds do not prove runtime behavior. Link to existing evidence where useful; do not create new records or store sensitive payloads only to support a claim.

Use this table for each verification summary. Put the date, environment, input source, and expected result in the relevant cell or a short note linked from the row. Put observed evidence in **Result**. Use **Not checked** for a skipped or blocked check and give the reason; otherwise use `—`.

| Check | Command or action | Result | Not checked |
| --- | --- | --- | --- |
| [specific check] | [command or manual action] | [observed result] | [— or reason] |

In the demo guide and relevant data-flow diagrams, explain applicable partial failures and recovery paths. State what remains saved, what the user sees, how retry works, and how duplicate effects are prevented. Record unresolved business policies in the decision log as pending, with their impact and the decision needed. Do not present a proposed default as an approved policy.

For freshness claims, state the source timestamp, retrieval time when known, and freshness rule. For performance results, record the measured operation, data volume, concurrency, environment, cache state when relevant, measurement method, and run count. Distinguish measured results from targets and estimates. Do not generalize a local or simulated result into a production guarantee.

## Architecture visuals

Create visual diagrams as image files in `docs/architecture/`. Use SVG, PNG, or another viewable image format. Keep an editable source for each diagram. Mermaid in `docs/ARCHITECTURE_AND_DESIGN.md` does not replace these images. Do not use Mermaid as the source for these image files unless the user explicitly requests it. Choose the smallest set of views that explains the implemented system:

- **System boundary:** Show the user, frontend, backend, data stores, external sources, and trust boundaries. Mark simulated sources as simulated.
- **Main data flow:** Follow one complete user action from input to response. Show validation, business rules, external calls, reads, writes, and visible results. Label each arrow with the data or request it carries. Number steps when order matters.
- **Failure and recovery:** Show where a call can fail, what data remains saved, what the user sees, and where a retry resumes. Put this in the main flow or a separate view if the main diagram becomes crowded.
- **Additional views:** Add a module or data-model view only when ownership, dependencies, identity, or stored fields need a separate explanation.

Use consistent names for records and modules. Mark the source of truth for key fields. Distinguish stored, derived, and external data. Show synchronous and background steps differently when both exist. Mark current behavior and proposed production changes in separate diagrams or clearly separate panels. Do not draw an unimplemented component as current behavior.

Write `docs/architecture/README.md` as a short guide. For each diagram, give its purpose, image link, editable source, key files or API routes, and a brief text path through the flow. Define any symbols and labels that are not clear from the image. Record important assumptions and unresolved decisions near the affected diagram. Link to the decision log and production handoff instead of repeating them.

Draft from the approved design. Update diagrams when a route, data store, provider, or business flow changes. Before handoff, trace each arrow against the UI, routes, services, models, and provider adapters. Check the saved state and failure path against observed behavior. Open or render every image. Inspect text size, arrow direction, contrast, and legibility at normal reading size. Record what was checked and what remains unverified.

## Production handoff

At project completion, create `docs/operations/production-readiness.md`. Separate observed facts, assumptions, recommendations, and remaining work. Include:

- The deployed or proposed system shape and current readiness status.
- Expected traffic, data volume, and reliability targets. State when these are unknown.
- Scaling options and the evidence or thresholds that would justify them.
- Failure modes, timeouts, retry and idempotency needs, and recovery steps.
- Health checks, logs, metrics, alerts, and incident ownership.
- Database backup, restore, and connection-capacity needs.
- Security and secret-management gaps.
- Known limits, open decisions, and prioritized work before launch.

Also create `docs/operations/production-extensibility.md`. Map likely additions to the current module or interface that would change. Cover new data sources, business rules, UI flows, and higher data volume only when relevant. For each addition, state the trigger, proposed boundary, data or API change, compatibility needs, and verification needed. Name what is already extensible and what needs refactoring. Keep proposals separate from implemented extension points. Do not add speculative infrastructure.

Do not invent load targets, SLOs, recovery objectives, or guarantees. Do not claim production readiness from code review alone. Do not deploy infrastructure or expand approved scope to address a recommendation. Record that work as a recommendation until the user approves it.
