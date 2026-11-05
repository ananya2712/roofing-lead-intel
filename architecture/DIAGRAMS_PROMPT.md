# Diagram guide prompt

Use this prompt only when the user requests a separate `docs/DIAGRAMS.md`. Otherwise, put the required Mermaid diagrams in `docs/ARCHITECTURE_AND_DESIGN.md` using `architecture/PROMPT.md`, and maintain viewable image files in `docs/architecture/` using `skills/documentation/SKILL.md`.

When requested, inspect this codebase and create or update `docs/DIAGRAMS.md` for a Software Engineer L1/L2. Generate it after the approved application flow is implemented. Update affected diagrams whenever completed code changes a workflow, module dependency, persisted entity, integration, or business rule. Check each change against code before calling the code change finished. Keep accurate diagrams; remove stale ones. Do not modify application code. This separate guide does not replace the image files in `docs/architecture/`.

Include focused Mermaid diagrams for:

1. System architecture: frontend, backend, database, real services, and mocks. Label connections by purpose or protocol.
2. Module structure: important modules, responsibilities, and actual dependency directions. Group related components with subgraphs.
3. Request flows: sequence diagrams for the main user workflows, from UI action through the API client, route, validation, service, database or provider, and response. Use `alt` for meaningful failures.
4. Data model: an entity-relationship diagram with persisted entities, primary and foreign keys, and cardinalities.
5. Business logic: a top-to-bottom flowchart for scoring or decisions, including missing data and rule order.

Use plain language. Define unfamiliar terms briefly. Use actual function names where helpful. Keep current behavior distinct from mocks and proposals. Place a short explanation and source-file list below each diagram. Flag unknowns and conflicts between code and other documentation. Use left-to-right architecture views, consistent names, simple Mermaid syntax, unique node IDs, and quoted labels when needed. Avoid crossing arrows and decorative styling.

Render with an available Mermaid renderer. If none is available, review syntax and state clearly that the diagrams were not rendered. Report the file path and significant uncertainties. Never include secret values.
