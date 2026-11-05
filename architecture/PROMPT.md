# Architecture and design guide prompt

Inspect this codebase and create or update `docs/ARCHITECTURE_AND_DESIGN.md` for a Software Engineer L1/L2 who needs to understand, maintain, and explain the application.

Generate the first version after the approved application flow is implemented. Update the existing file whenever completed code changes an API, workflow, rule, data model, integration, UI state, or deployment behavior. Do this as part of the same change, before calling the work finished. Recheck affected sections against code and remove stale claims; preserve accurate sections. Update verification claims only when checks were run again. Do not rewrite the file for a code change that has no effect on its contents.

Document the actual implementation. Use plain language, define unfamiliar terms briefly, and connect architectural choices to the problem they solve. Do not modify application code.

Mermaid is permitted inside `docs/ARCHITECTURE_AND_DESIGN.md` for the architecture and sequence diagrams below. Also create or update the required viewable image files in `docs/architecture/` under `skills/documentation/SKILL.md`. The Markdown diagrams do not replace those images. Do not create `docs/DIAGRAMS.md` unless the user requests a separate diagram guide.

Include:

1. **Purpose and scope**
   - Business problem, intended users, and main workflows.
   - Implemented functional and non-functional requirements in short bullet points.
   - MVP boundaries and known limitations.
2. **Technology stack**
   - Main frameworks, libraries, database, and development tools.
   - Each tool's responsibility in this application.
3. **Directory structure**
   - An annotated tree of important source, configuration, test, database setup, and data files.
   - Application entry points.
   - Exclude generated files and dependency folders.
4. **Architecture**
   - A Mermaid diagram showing the frontend, backend, database, and integrations.
   - Responsibilities of major modules and how they communicate.
   - Clearly distinguish real services, simulated APIs, and local data sources.
5. **Request and data flows**
   - Inventory every application API endpoint: method, path, purpose, inputs, outputs, and errors.
   - Trace each endpoint from its frontend caller through validation, business logic, persistence or integrations, and back to the UI.
   - Reference actual files and functions. Identify endpoints without frontend callers.
   - Include sequence diagrams for the main workflows and explain meaningful differences between endpoints.
6. **Data design**
   - Main entities, relationships, identifiers, and database constraints.
   - Where source data, enrichment data, and calculated values live.
   - How Excel files, fixtures, or simulated APIs are used, if present.
   - What persists and what exists only in browser memory.
7. **Business rules**
   - Scoring formulas, thresholds, normalization, deduplication, matching, and status rules.
   - Missing-data and failure behavior.
   - One worked example showing how inputs produce an output.
   - Separate deterministic calculations from any AI-generated output.
8. **Key design decisions**
   - Explain the most important choices, their benefits, limitations, and one reasonable alternative.
   - Use documented rationale when available. Label inferred rationale explicitly.
   - Keep explanations appropriate to the application's size.
9. **Reliability, security, and testing**
   - Validation, error handling, retries, duplicate prevention, and credential handling actually implemented.
   - Existing tests and the behavior they cover.
   - Important gaps and risks. Do not claim tests passed unless you ran them.
10. **Production evolution**
    - Explain which MVP choices would need to change for real users and live integrations.
    - Prioritize changes and state what would justify them.
    - Cover relevant database, security, API, deployment, monitoring, and background-processing concerns without assuming microservices are necessary.

Finish with a short reading order: which files a new engineer should open first and why.

Accuracy requirements:

- Treat repository documentation as context; verify claims against code.
- Distinguish implemented behavior, documented intent, inference, and recommendations.
- Flag contradictions and unknowns instead of guessing.
- Use repository-relative paths and verified function names.
- Never include secret values.
- Prefer concise explanations and small examples over pasted source code.
- Scale the document to the codebase; avoid generic textbook material.

Create or update the Markdown file and report its location along with any significant uncertainties.
