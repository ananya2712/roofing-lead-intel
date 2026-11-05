# Project Guidance

This file records project-wide defaults and user decisions. The project skill source is in `skills/`. Discovery copies are in `.agents/skills/` for Codex and `.claude/skills/` for Claude Code. Both tools can discover the skills when this repository is the project root. Read the relevant skill when its task applies.

These project rules have priority over plugin or personal skills, including TDD and brainstorming. If a skill conflicts with the test timing, approval, or scope rules here, follow this file.

For full-stack application work, read [the consolidated workflow](skills/full-stack-project/SKILL.md). It routes to the backend, frontend, documentation, writing, and presentation skills. For a focused task, read the relevant skill directly. Keep this file as the source for project decisions. Keep detailed workflows in the skill files.

## Approved stack

- Backend and database: Flask, PostgreSQL, and SQLAlchemy 2. Do not add Alembic or schema-versioning tooling for the MVP.
- API: REST JSON endpoints under `/api/v1`, Flask app factories and blueprints, and Pydantic request and response schemas. Keep `openapi.yaml` aligned with the routes and schemas. Generate the TypeScript client with `openapi-typescript` and `openapi-fetch` when the API contract changes.
- Frontend: Next.js 14 App Router, React, TypeScript, and Tailwind CSS. Check current official Next.js documentation when you set up or upgrade the stack.
- Local development: Docker Compose with the frontend, backend, and PostgreSQL. The frontend image installs its own packages. Use the Compose port mapping to report the local URL.
- Tests: pytest for API and database integration tests. Use the Playwright Python pytest plugin for browser end-to-end tests. Add tests after all approved functionality is implemented. Do not add unit or smoke tests unless the user changes this decision.

Keep route handlers, business logic, and feature-specific database queries in separate modules. Do not add a generic repository base class by default. Do not add login or account features unless the user asks for them or requirements need them. Store main records in structured tables. Add optional fields only when a project requirement needs them. Do not add enrichment history, provider payload storage, or provenance tables by default. Add queues, caches, microservices, or deployment infrastructure only when approved requirements need them.

Load configuration from environment variables. Keep placeholder values in `.env.example`. Do not store secrets in source control. Define consistent API errors and database constraints for important data rules.

## Project decisions

- Use Docker Compose for local runs.
- Keep the first release useful and within the scope the user approves.
- Use [Closr CRM Analytics Dashboard](https://dribbble.com/shots/27250115-CRM-Analytics-Dashboard-Contacts-Deals-Activity-Closr) as the primary layout reference for the lead dashboard. Put important summary information first, supporting views next, and a readable detail table below. Use a neutral canvas and separated surfaces. Use deep navy for navigation and primary actions, blue for information, emerald for success, amber for caution, and coral for errors. Keep spacing compact, filters visible, and IBM Plex Sans as the font unless the user selects another. Show only data and actions the app supports.
- Use ASD-STE100 as the writing guide for all project-authored files. See [the writing skill](skills/writing/SKILL.md).
- Do not use subagent-driven implementation by default. Use it only when the user asks for it or a task requirement or applicable instruction makes delegation necessary.

## Running HTML record

The user requested a running explanation of repository changes, product design decisions, and architecture. Maintain `docs/PRODUCT_EVOLUTION.html` as one self-contained, offline HTML file. This requested record can start before application implementation. Update it in the same change when code or an approved decision changes its contents. Keep a dated change history with changed files, before/after behavior, reasons, affected components, and observed verification. Explain decisions with their evidence, alternatives, production limits, and conditions for revisiting them. Label inferred rationale and distinguish documented intent, implemented code, observed results, and proposed work. Keep the current architecture view accurate, preserve past entries, and never include secret values. This is a maintained document, not an automatic repository watcher.

Keep `docs/CODE_WALKTHROUGH.html` concise and table-based. Do not include a demo sequence. Retain the database relationship diagram and complete API inventory. Explain technical choices with their reasons, limitations, alternatives, and why an alternative was not selected. Label unrecorded comparisons as inferred. Include proposed production extensibility and prioritized future work with affected code, compatibility needs, and verification. Keep detailed history in `PRODUCT_EVOLUTION.html`.

Every subsection in the HTML must present its explanation in a table. Keep file/function control-flow tables for initial application opening and saving a lead from Prospects. Distinguish service startup from page requests, parallel requests from sequential calls, build-time artifacts from runtime code, and committed database state from UI refreshes.

## Skill routing

| Task | Read |
| --- | --- |
| Full-stack design, implementation, and handoff | [Full-stack project](skills/full-stack-project/SKILL.md) |
| Flask API, PostgreSQL, or SQLAlchemy | [Backend](skills/backend/SKILL.md) |
| Next.js pages, React components, or UI design | [Frontend](skills/frontend/SKILL.md) |
| Build progress, decisions, demo guide, diagrams, or production handoff | [Documentation](skills/documentation/SKILL.md) |
| Project prose, UI copy, comments, docstrings, or slide text | [Writing](skills/writing/SKILL.md) |
| Final project presentation | [Presentation](skills/presentation/SKILL.md) |

Create and maintain project records only after design approval, when work enters an approved implementation. Do not create them for planning-only chats or instruction-file updates. Follow the documentation skill when these records apply.

Use the requested design and implementation process. Get approval before application code, project scaffolding, or dependency installation. Do not write or run automated application tests before approved functionality is complete. Do not use test-driven development. Manual checks are allowed; report them as manual checks. Do not claim success without observing the required result. Report any check that you could not run.
