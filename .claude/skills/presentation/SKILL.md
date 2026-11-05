---
name: project-presentation
description: Use when creating, editing, or reviewing the final PowerPoint presentation for a completed project in this workspace.
---

# Project Presentation Skill

Create a technical project presentation for a Software Engineer L1/L2 audience. Explain the business problem, implemented system, and engineering decisions clearly enough for an interviewer to assess the work.

The deck must help the presenter answer:
- What problem does the application solve, and for whom?
- What requirements shaped the implementation?
- How are the data and system organized?
- How does the application expose its functionality?
- Why were these design choices appropriate?
- What would change after the MVP?

## Prerequisites and sources

Create the final deck after approved implementation, agreed tests, and final verification are complete.

For an existing deck, make the requested edits without rebuilding the application or repeating unrelated work.

Before authoring:
1. Read `AGENTS.md`.
2. Read the project documentation and writing skills.
3. Use the relevant presentation authoring skill available in the session.
4. Inspect the implemented routes, schemas, database models, database setup, configuration, and important business logic.
5. Read the architecture document, decision log, demo guide, verification results, and HTML code walkthrough when available.
6. Review the [Google Slides reference deck](https://docs.google.com/presentation/d/1RWY1xEEjRpM93radP9uHwpHtNai9NjFcjR3e8hwHaUI/edit?slide=id.p1#slide=id.p1) for topics the presentation should cover. Map relevant topics to the seven core slides or a justified appendix. Check each project-specific claim against the implementation.

Treat code as evidence of implementation. Treat the decision log as evidence of recorded rationale. Verify documentation claims against the code.

The HTML walkthrough and reference deck supply supporting material. They do not override the mandatory slide order below. If either source is unavailable, report that limit. Do not infer its contents.

Distinguish:
- **Implemented:** Present in the application.
- **Verified:** Supported by an observed check under stated conditions.
- **Proposed:** A future capability or production improvement.

If required verification is incomplete, report the gap and label the deck as a draft. Do not describe the project as fully verified.

## Mandatory deck structure

Use seven core slides in this exact order. Do not add a separate title slide before Slide 1.

Use project-specific titles and content. Keep the purpose of each slide recognizable.

### Slide 1 — Problem and target user

**Purpose:** Establish why the application exists.

Include:
- Project name and a one-sentence description.
- The primary user and their responsibility.
- The current workflow and its main difficulty.
- The outcome the application enables.
- A short core workflow, such as:
  `Find prospects → Enrich → Prioritize → Record follow-up`

Describe the problem in business terms before naming technologies.

Do not invent time savings, revenue impact, conversion improvements, or user research.

**Speaker notes:**
- One realistic user scenario.
- What is inside and outside the MVP.
- Which problem details are supplied requirements versus assumptions.

### Slide 2 — Functional and non-functional requirements

**Purpose:** Show what the system must do and the quality constraints it must satisfy.

Use two clearly separated groups.

**Functional requirements**
Select the principal user capabilities. State them as observable behavior, such as:
- Search and import leads.
- Prevent duplicate records.
- Enrich saved information.
- Explain priority scores.
- Persist notes and follow-up status.

**Non-functional requirements**
Include only concerns relevant to this implementation, such as:
- Correct and repeatable calculations.
- Input validation and data integrity.
- Recovery from integration failures.
- Usable loading, empty, and error states.
- Maintainable module boundaries.
- Protection of configuration and secrets.

Show implementation status where a requirement is partial or absent. Distinguish a quality goal from a measured result.

Do not claim that “uses PostgreSQL” proves reliability or that “uses TypeScript” proves correctness.

**Speaker notes:**
- Acceptance conditions for each requirement.
- Supporting code or tests.
- Performance targets and results, if measured.
- Important deferred requirements.

### Slide 3 — Database data model

**Purpose:** Explain how persistent data represents the business workflow.

Make the main visual an entity-relationship diagram.

Include:
- Actual table names.
- Primary and foreign keys.
- Relationship cardinalities.
- Important business fields.
- Constraints that enforce significant rules.

Show enough fields to explain the model. Put full column details in notes rather than shrinking the diagram.

Clearly distinguish:
- Persisted records.
- Source files or Excel enrichment data.
- Derived values calculated at request time.
- Temporary frontend state.

Do not represent mock files as database tables. Do not show proposed history, audit, or provenance tables as implemented.

**Speaker notes:**
- Model and database setup file paths.
- Why each entity exists.
- Duplicate-prevention strategy.
- Nullable fields and missing-data behavior.
- Whether enrichment replaces existing values.
- Whether scores are stored or recalculated.

### Slide 4 — System architecture and request flow

**Purpose:** Explain component responsibilities and how they work together.

Show:
- Browser and frontend.
- Backend API.
- Business logic and integration boundaries.
- Database.
- Actual external providers, simulated APIs, and file-based sources.

Label arrows with their purpose, such as:
- REST JSON.
- SQL reads and writes.
- Mock search request.
- Excel lookup.

Use the approved project stack only when it matches the implementation. Clearly label deviations.

Trace one representative request through the same diagram with numbered steps:
1. User action.
2. Frontend API call.
3. Route validation.
4. Business logic.
5. Database or enrichment access.
6. Response and UI update.

Show one important failure branch, such as an enrichment failure that preserves the saved lead.

Use native PowerPoint shapes and connectors. Do not use Mermaid.

**Speaker notes:**
- Actual files and functions for the trace.
- Synchronous versus background behavior.
- Error handling and retry behavior.
- What runs locally and what requires network access.

### Slide 5 — Complete API endpoint inventory

**Purpose:** Show the full application API surface.

Include every implemented application endpoint in a readable table:

| Method | Full path | Purpose | Main input → result |
| --- | --- | --- | --- |

Use full route prefixes, such as `/api/v1`. Verify the inventory against route registration, schemas, and `openapi.yaml`.

Include important health or configuration endpoints. Identify endpoints without frontend callers when relevant.

Do not count framework-generated `OPTIONS`, static assets, or page routes as business API endpoints.

Highlight one representative endpoint and its principal success or failure behavior.

Keep the complete inventory visible when it fits. If it cannot fit at readable size, show a grouped overview on Slide 5 and place the complete inventory on clearly labeled appendix slides. Never silently omit endpoints or move the entire inventory into notes.

**Speaker notes:**
- Request and response examples.
- Validation rules and status codes.
- Runtime behavior versus OpenAPI discrepancies.
- Frontend caller and backend handler paths.
- Whether HTTP success can contain a failed enrichment state.

### Slide 6 — Key design decisions and alternatives

**Purpose:** Demonstrate engineering judgment.

Use a comparison table with three or four significant choices:

| Decision | Chosen approach and reason | Alternative and tradeoff |
| --- | --- | --- |

Select decisions that shaped the application, such as:
- Deterministic rules versus LLM-based ranking.
- Structured database records versus file-only storage.
- Synchronous enrichment versus a background queue.
- Modular monolith versus separate services.
- Simulated integrations versus live providers.
- Calculated scores versus stored score snapshots.

Include at least one important business-rule decision.

Explain choices in relation to the MVP requirements and time limit. Alternatives may be reasonable at a different scale.

Distinguish recorded rationale from your inference. Do not claim the team evaluated an alternative unless evidence supports that claim.

**Speaker notes:**
- Benefits and limitations.
- Relevant modules.
- Evidence supporting the choice.
- Conditions that would justify changing it.
- One brief deterministic-scoring example, when applicable.

### Slide 7 — Future capabilities and production evolution

**Purpose:** Explain how the MVP can grow through justified next steps.

Separate:
- **Production essentials:** Changes needed before real users or live data.
- **Product extensions:** Additional user capabilities.
- **Scale-driven improvements:** Changes justified by observed volume or latency.

Select three to five concrete improvements. For each, explain:
- The current limitation.
- The proposed capability.
- The user or operational benefit.
- The prerequisite or trigger.

Examples may include real provider integration, authentication, CRM synchronization, durable enrichment jobs, or representative assignment. Include only proposals relevant to this project.

Do not present queues, caches, microservices, or Kubernetes as automatic upgrades.

**Speaker notes:**
- Suggested implementation order.
- Modules affected.
- New data or integration requirements.
- Known verification gaps.
- How success would be measured.

## Supporting material

Keep the seven core slides intact.

Add appendix slides only when needed for:
- API inventory overflow.
- Detailed scoring rules and a worked example.
- Directory structure and code entry points.
- Verification results.
- A demo sequence and implemented recovery case.

Do not add generic filler slides.

Include the recorded verification summary in notes and, when useful, an appendix. Clearly identify simulated behavior. If a recovery path is absent, describe it as a gap rather than demonstrating invented behavior.

## Visual and writing requirements

- Use a clean 16:9 layout.
- An external slide template is optional. If a Slidesgo or other template needs a login or cannot be downloaded, use native PowerPoint shapes in the approved project style. Report the skipped template. Keep the required seven-slide structure.
- Follow the approved application style and project writing skill.
- Use short, concrete sentences suitable for an L1/L2 technical walkthrough.
- Use one main message per slide.
- Prefer diagrams and comparison tables over dense paragraphs.
- Use approximately 28–36 pt titles and 20–24 pt body text.
- Keep table and diagram labels at least 18 pt. Split content when necessary.
- Use consistent entity, module, and endpoint names.
- Explain acronyms on first use.
- Label mocks, synthetic data, and proposed components visibly.
- Keep diagrams editable with native shapes and connectors when practical.
- Do not use Mermaid.
- Do not use screenshots of code as substitutes for diagrams.
- Place commands, file references, detailed examples, and evidence conditions in speaker notes.

Each slide’s notes should contain:
1. A short speaking script.
2. Supporting repository paths.
3. Relevant limitations or assumptions.
4. Verification evidence when a claim depends on a check.

## Review and delivery

Save the final deck as `docs/PROJECT_DEMO.pptx`.

Before delivery:
- Confirm the seven required slides exist in the specified order.
- Cross-check entities against models and the initialized database schema when available.
- Cross-check endpoints against actual routes and the API contract.
- Check diagram arrows against real dependencies and data flow.
- Check that stated alternatives and rationale are accurately attributed.
- Confirm future capabilities are labeled as proposals.
- Render and inspect every slide.
- Fix clipping, overlap, small text, low contrast, and unreadable diagrams.
- Confirm that speaker notes are present.
- Report checks that could not be completed.

For an approved implementation, update:
- `docs/BUILD_PROGRESS.md` with deck completion and observed checks.
- `docs/DEMO_GUIDE.md` with the deck path and presentation/demo order.
- `docs/DECISION_LOG.md` only when a new durable format decision needs recording.

Do not create project progress records for planning-only conversations or instruction-file revisions.

Deliver the final deck with a concise report stating its path, slide count, checks completed, and any remaining limitations. Keep temporary files out of the delivery.
