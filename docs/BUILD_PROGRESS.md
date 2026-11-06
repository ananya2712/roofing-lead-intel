# Build Progress

## Goal

Give sales representatives of a roofing-materials distributor one place to find roofing contractors near ZIP 10013, see why each contractor may fit, save leads and track their status.

## Current scope (minimal version)

- GAF residential and commercial directories, ZIP 10013, 50 mi, full profiles, collected one time (D1–D3).
- Tables: `prospects`, `prospect_scores`, `leads` (D4). No Alembic (D5). No fixtures and no test database (D6).
- Deterministic score v1 (D7). One saved lead for each company (D8).
- Views: Sales dashboard, Prospects, Saved leads, Prospect details.
- Deferred: notes (D10), AI insights (D11). Tests authorized under D22; 106 passes recorded in `docs/TEST_RESULTS.md`.
- Out of scope: login, outreach, CRM sync, segmentation, multi-agent orchestration, queues.

## Milestones

| # | Milestone | Status |
| --- | --- | --- |
| M0 | Project folder, guidance files, records | Done |
| M1 | GAF snapshot collection | Done: residential 176 of 176, commercial 233 of 233 |
| M2 | Backend: tables, import, scoring, API, OpenAPI | Done |
| M3 | Frontend: four views | Done (first version) |
| M4 | Docker Compose run and manual checks | Done (manual checks below) |
| M5 | Tests | Done: 106 passed (see `docs/TEST_RESULTS.md`) |
| M6 | Architecture guide, diagrams, handoff, walkthrough, presentation | Done: 18-slide editable deck based on the current HTML, with tables, diagrams and speaker notes. |

## History

### 2026-11-05 — M0

| File | Change | Reason |
| --- | --- | --- |
| `AGENTS.md`, `skills/`, `.claude/`, `.agents/`, `architecture/` | Copied from `essential-skills/` | Project guidance |
| `.gitignore`, `.env.example`, `.env` (not in git) | Added | Keep secrets out of git |
| `docs/*.md` | Added | Project records |

### 2026-11-05 — M1 (residential)

| Item | Result |
| --- | --- |
| Method | Claude in Chrome read 18 result pages and 176 profile pages in the user's Chrome, about 1.5 s apart. The user saved the JSON file. |
| File | `data/snapshot/gaf_residential_10013_50mi.json` (183,305 bytes) |
| Result | 176 records for 176 shown by GAF. 0 failed profile requests. 81 have no website on GAF. 24 have no Google rating. |

### 2026-11-05 — M2 and M3

| File | Responsibility |
| --- | --- |
| `backend/app/models.py` | Three tables, constraints and indexes |
| `backend/app/collection/snapshot.py`, `importer.py` | Validate, normalize, upsert by (`directory`, `gaf_source_id`), then score |
| `backend/app/scoring.py` | Score v1 (D7) |
| `backend/app/queries.py`, `services.py`, `api/__init__.py` | Reads, business rules, routes |
| `backend/app/cli.py` | `flask import-snapshot`, `flask rescore` |
| `openapi.yaml`, `frontend/lib/api-types.ts` | API contract and generated types |
| `frontend/app/*` | Overview, Prospects, Saved leads, Prospect details |
| `frontend/components/*` | Shared UI and lead components |
| `additional/insights/` | Deferred AI insight draft (not connected) |

### Manual checks so far

| Check | Command or action | Result | Not checked |
| --- | --- | --- | --- |
| Import is complete | `docker compose exec backend flask import-snapshot` | "176 valid of 176 shown by GAF (complete); 176 new" | — |
| Repeated import makes no duplicates | Same command again | "0 new, 176 updated" | — |
| Validation error shape | `GET /api/v1/prospects?tier=bad` | HTTP 422 with `validation_error` and the field message | — |
| Save, status change, views | Browser at `http://localhost:3000` | Saved a prospect, changed status to Contacted; Overview and Saved leads showed the new counts | — |

### 2026-11-05 — First two presentation slides

- Created `docs/PROJECT_DEMO.pptx` with two editable slides: project/problem and demo, following the user's notebook order. Added source-based speaker notes.
- Used read-only local API evidence: health `ok`, 176 residential prospects, and prospect 145 with score 95 and distance 6.5 mi. This presentation review made no lead-data changes and ran no application tests.
- PowerPoint package, slide-count, geometry, font, native-table, and import checks passed. Both slides were rendered and inspected. Native PowerPoint execution and the browser demo were not verified. The browser access host was unavailable.
- Updated the demo guide to remove deferred notes and AI insights. Linked the deck from the running HTML record.

### 2026-11-05 — Single-page repository walkthrough

- Added `docs/CODE_WALKTHROUGH.html` from the documentation HTML prompt and writing skill. It is self-contained and includes eight endpoint traces, embedded SVGs, data ownership, exact rules, a recorded-data score example, decisions, production proposals, and verification limits.
- Rechecked the updated saved-lead scope/queue/sort implementation. Read-only local GET requests returned the current data and validation/missing-record errors. `max_distance=10` returned 422 despite being an allowed filter in the contract; the walkthrough records this discrepancy. No application code was changed.
- HTML anchors/source links, embedded SVG XML, and route/OpenAPI operation inventory passed static document checks. Embedded diagrams were rasterized for inspection. Browser access was unavailable. No automated application tests, writes, imports, rescores, or restarts were performed in this documentation task.
- Linked the new current reference from `PRODUCT_EVOLUTION.html` and this guide from `DEMO_GUIDE.md`. Older dated history remains preserved.

### 2026-11-05 — Concise HTML demo guide

- Replaced the long `CODE_WALKTHROUGH.html` with short bullets in the user's notebook order. Kept all eight API endpoints in one table.
- Added `docs/architecture/demo-data-model.svg` and its PNG preview. The HTML embeds the SVG and remains self-contained.
- Rechecked snapshot counts and read-only API stats: 409 total (176 residential, 233 commercial). `max_distance=10` still returned 422. No application writes or automated tests were run.
- Preserved the previous HTML privately before rewriting. Updated the repository guidance to keep this page concise.

### 2026-11-05 — Technical tables and production extensions

- Removed the demo sequence from `CODE_WALKTHROUGH.html`. Converted explanations to tables while retaining the embedded database and request-flow diagrams and all eight API endpoints.
- Added technical rationale, limitations, alternatives, and reasons for deferring alternatives. Marked unrecorded comparisons as inferred rather than attributing them to earlier developer decisions.
- Added production extension boundaries, compatibility/verification requirements, and a prioritized future-work table. Additions remain proposals; no application behavior changed.
- Updated the persistent formatting rule in `AGENTS.md`. Checked table structure, anchors/links, embedded SVG XML, and route-inventory coverage. No application tests or writes were performed; browser layout remains unverified.

### 2026-11-05 — File/function control-flow tables

- Added source-linked tables to `CODE_WALKTHROUGH.html` for backend startup, initial `/` opening, and Save as lead from the Prospects list. All subsection explanations and both diagrams are presented in table structures.
- Traced the independent Overview and Sidebar GET requests. Traced the save transaction, `session.expire_all()`, response construction, and parallel list/statistics refreshes. Documented the Sidebar's pathname-only refresh behavior and excluded import/rescore/provider work.
- Checked referenced symbols/line locations, table structure, heading/table coverage, links/anchors, embedded SVG XML, and the eight-route inventory. This is source inspection, not a new runtime or browser test. No application code or business data changed.

### 2026-11-05 — Commercial data, Saved leads update, directory filter, docs

| File | Change | Reason |
| --- | --- | --- |
| `data/snapshot/gaf_commercial_10013_50mi.json` | Added (171,566 bytes, 233 records). 0 failed profile requests. All have a phone; 209 have no website on GAF. | D3 |
| `backend/app/schemas.py`, `services.py`, `openapi.yaml` | Lead `scope`, `queue`, `sort`; row `distance_mi`, `top_reason`, `follow_up_due`; `queue_counts`, `total_saved` | D18 |
| `backend/app/queries.py`, `api/__init__.py` | SQL directory filter for leads, stats, overview | D19 |
| `backend/app/schemas.py` | `QueryModel` drops empty query values | D20 |
| `frontend/app/leads/page.tsx` | Call lists, labeled totals, sort, row reasons, Mark contacted with row feedback, phone layout | D18 |
| `frontend/components/leads/DirectoryToggle.tsx` and three pages | Directory toggle | D19 |
| Pastel redesign (`tailwind.config.ts`, shared components, all pages) | Pastel tokens, 4–6 px corners, icons, clickable KPIs and charts, filter chips, sortable columns | User direction |
| `backend/app/insights/generator.py` | Deleted: a stray copy of `additional/insights/generator.py` that nothing imported | Keep insights out of the MVP (D11) |
| `README.md`, `docs/ARCHITECTURE_AND_DESIGN.md`, `docs/architecture/*`, `docs/operations/*`, `docs/TEST_PLAN.md`, `docs/CODE_WALKTHROUGH.html` | Added or updated | Handoff |

### Manual checks on 2026-11-05 (local Docker Compose, real snapshot data)

| Check | Command or action | Result | Not checked |
| --- | --- | --- | --- |
| Commercial import complete | `flask import-snapshot` | "233 valid of 233 shown by GAF (complete); 233 new"; total 409 prospects | — |
| Repeated import of both files | Same command again | "0 new, 233 updated" and "0 new, 176 updated" | — |
| Companies in both directories | SQL join on `phone_digits` | 36 pairs | — |
| Save, repeat, other listing | POST save on prospect 1, again, then on prospect 418 (same company) | 201, 200, 409 `company_already_saved` with `prospect_id` 1; 2 leads in total | — |
| UI for the other listing | Browser: `/prospects/418` | "Saved via Residential listing" | — |
| 404 | `GET /prospects/999999` | 404 | — |
| Invalid values | `scope=bogus`, `sort=oops`, `status=dismissed`, `status=won`, `directory=bad` | 422 `validation_error` with the field message | — |
| Empty value | `?directory=` | 200, no filter | — |
| Follow-up boundary | Set lead 1 `status_changed_at` to 13 d 23 h ago, then 14 d 1 min ago (restored afterwards) | Due count 0, then 1 | — |
| Same-status update | PATCH Contacted on a Contacted lead | `status_changed_at` unchanged | — |
| Directory filter | `stats`, `leads`, `overview` with each directory | Residential 176 / Commercial 233; leads and top prospects only from the chosen directory | — |
| Restart persistence | `docker compose restart` | Saved lead and status unchanged | Restart after the latest code changes not repeated |
| Frontend types | `npx tsc --noEmit` in `frontend/` | No errors | — |
| Diagrams | Opened both SVG files in Chrome | Readable | — |
| Automated tests | — | — | Not written at this point; see the next entry |

### 2026-11-05 — M5 tests, fixes found by the tests, user UI changes

| File | Change | Reason |
| --- | --- | --- |
| `backend/tests/` (`conftest.py`, 7 test files, `e2e/test_browser.py`), `backend/pytest.ini`, `backend/requirements-test.txt` | Added 96 API/database tests and 10 Playwright tests | User approved the test plan (D22) |
| `backend/app/schemas.py` | `max_distance` accepted as a number from the query string (F1) | Distance filter returned 422 |
| `backend/app/services.py` | `session.expire_all()` after a save (F2) | Save response had `lead: null` |
| `frontend/lib/api.ts` | Network failures show the clear fallback message (F5, D24) | Raw "Failed to fetch" text |
| `frontend/components/ui/layout/Sidebar.tsx`, `components/leads/DirectoryToggle.tsx`, `app/prospects/page.tsx` | Wrap on narrow screens; table scroll area `relative` (F7) | Pages wider than a phone |
| `backend/app/collection/importer.py`, `cli.py` | Import rescores only imported rows (D21) | Isolation of test rows; less work |
| `Sidebar.tsx`, `app/page.tsx` | "Overview" renamed "Sales dashboard" (D23) | User request |
| `app/leads/page.tsx`, `app/prospects/[id]/page.tsx` | Mark contacted moved from the table to the lead page (D23) | User request |
| `docs/TEST_RESULTS.md`, `docs/DEMO_GUIDE.md`, `docs/TEST_PLAN.md`, `docs/DECISION_LOG.md`, `docs/ARCHITECTURE_AND_DESIGN.md`, `README.md` | Updated | Records |

| Check | Command or action | Result | Not checked |
| --- | --- | --- | --- |
| Full test suite | `cd backend && .venv/bin/pytest tests --browser chromium` | 106 passed in about 21 s | — |
| Frontend type check | `npm run typecheck` in `frontend/` | No errors | — |
| Frontend build | `npm run build` in `frontend/` | Compiled successfully; 5 routes | — |
| Test rows removed | SQL count after the run | 0 `TEST-` rows; 409 prospects; the 2 real leads unchanged | — |
| `CODE_WALKTHROUGH.html`, `PRODUCT_EVOLUTION.html` | Rewrote the walkthrough (table-based, per `AGENTS.md`); added Entry 005 to the running record; opened both in Chrome | Both parse as HTML and render; past record entries kept | — |

### 2026-11-05 — Complete HTML-based presentation

| Change | Result / reason | Verification boundary |
| --- | --- | --- |
| `PROJECT_DEMO.pptx` | Expanded the old two-slide draft to 18 editable slides in current HTML order. Tables throughout; native architecture/data-model diagrams; first-open/save file flow; eight endpoints; alternatives, production extensions and future work. No cover or demo-sequence slide. | Package integrity passed; 18 slides imported; native table ownership and layout checks passed with zero findings. Slides rendered and visually inspected. Native PowerPoint execution not checked. |
| `CODE_WALKTHROUGH.html` and build source | Refreshed obsolete distance-filter, test-status and dashboard-name text against current source and `TEST_RESULTS.md`. | Read-only local API checks: health 200, 409 prospects, `max_distance=10` 200. No app writes or test-suite rerun. |
| `PRESENTATION_CONTEXT.md`, `DEMO_GUIDE.md`, `PRODUCT_EVOLUTION.html` | Added compact working context, replaced stale current slide-count statements and retained earlier history. | Current deck cites the recorded 106-test run instead of claiming a new run. |

### 2026-11-05 — More detailed architecture diagram

| Change | Result / reason | Verification boundary |
| --- | --- | --- |
| Deck slide 4; embedded HTML; `architecture/request-flow.svg` and PNG | Expanded four boxes to 12 runtime steps and six setup stages. Show request/response direction, validation, service, ORM, commit constraints, save-only reload, serialization, errors and UI refetch. | Compared arrows with current UI/client, routes/schemas, services, queries/models, DB and CLI/importer source. Save and reads have different branches; independent GETs can overlap. |
| Shared diagram module | `.presentation-build/full/architecture_flow.mjs` supplies native PPT elements and SVG labels. Preserved the 18-slide structure and table formatting. | Rendered slide/image inspection; package integrity and layout checks. Native PowerPoint not checked. |
| Status-route label | Corrected stale PATCH to POST in the deck and HTML from current Flask/OpenAPI/frontend evidence. | No application code or business data changed; no application suite rerun. |
| Supporting records | Updated diagram README, compact context, demo guide and running HTML. | Unrelated slides compared against prior rendered output. |

### 2026-11-05 — PATCH removed; deck: scraping pipeline, ICP, tests

| File | Change | Reason |
| --- | --- | --- |
| `backend/app/api/__init__.py`, `openapi.yaml`, `frontend/lib/api-types.ts` (generated) | Status route changed from PATCH to POST | D25 |
| `frontend/components/leads/StatusSelect.tsx`, `frontend/app/page.tsx`, `frontend/app/prospects/[id]/page.tsx` | Call `api.POST` for status changes | D25 |
| `backend/tests/*.py` | Status calls use POST; new test: PATCH returns 405 and changes nothing | D25 |
| `docs/.presentation-build/full/build.mjs`, `docs/PROJECT_DEMO.pptx` | Removed slides "Opening the app: file control" and "Saving from Prospects: file control". Added 6 scraping-pipeline slides, an ideal-customer-profile slide and a test-failures slide. Test slide shows 107. 405 row on the API slide. 24 slides. | User request |
| `docs/CODE_WALKTHROUGH.html`, `docs/.presentation-build/full/source.json` | POST in the API table; 107 tests | D25 |

| Check | Command or action | Result | Not checked |
| --- | --- | --- | --- |
| Full test suite | `cd backend && .venv/bin/pytest tests --browser chromium` | 107 passed in about 21 s | — |
| Live API | `PATCH /api/v1/leads/1/status` on port 5001 | 405 | — |
| Test rows removed | SQL count after the run | 0 `TEST-` rows; 409 prospects; 2 real leads unchanged | — |
| Deck build | `RUNTIME_NODE_MODULES=… node build.mjs v7` | 24 slides; package check pass; 0 layout findings; 24 notes | Native PowerPoint not opened |
| Slide review | Read rendered previews 4–10, 13, 15, 22, 23 | Readable; no clipping or overlap | Other slides unchanged from v6 and not reinspected |

### 2026-11-05 — Dark HTML walkthrough and production extensions

| Change | Result / reason | Verification boundary |
| --- | --- | --- |
| `CODE_WALKTHROUGH.html`; `.walkthrough-build/build_technical_tables.py` | Dark theme and headings; dark embedded architecture and database SVGs; current collection, ideal customer profile, 107-test evidence and failure summary; production tables for collection, PostgreSQL and LLM jobs. | Chromium desktop and 390 px screenshots; no page-level horizontal overflow. SVGs parsed and rendered. No application logic or business data changed. |
| `PRODUCT_EVOLUTION.html` | Entry 008 records this documentation update while retaining earlier entries. | Application suite not rerun for a documentation change. |

### 2026-11-05 — Pastel deck (28 slides)

| File | Change | Reason |
| --- | --- | --- |
| `docs/.presentation-build/full/build_pastel.mjs` (local, not in git) | New deck builder: pastel theme, smaller text, more content from the docs | User request |
| `docs/PROJECT_DEMO.pptx` | 28 slides: non-table overview; functional / non-functional requirements; high-level architecture; save-flow line diagram; tech choices without REST and Docker Compose; Flask vs FastAPI + REST; scraping pipeline and production pipeline diagrams; scoring fields; ideal residential and commercial profiles; three-stage roadmap; scheduled collection options; append-only lead_events proposal; more capabilities; test strategy by type | User request |

| Check | Command or action | Result | Not checked |
| --- | --- | --- | --- |
| Deck build | `node build_pastel.mjs p2` | 28 slides; package check pass; 0 layout findings | Native PowerPoint not opened |
| Speaker notes | Read notes in the PPTX | 28 of 28 slides have notes | — |
| Slide review | Read rendered previews 1–7, 9, 13–16, 21–23, 25–27 | Readable; no clipping or overlap | Slides 8, 10–12, 17–20, 24, 28 checked by the layout validator only |

### 2026-11-05 — Deck restyle: white boxes, mixed visuals

| File | Change | Reason |
| --- | --- | --- |
| `docs/.presentation-build/full/build_clean.mjs` (local, not in git) | New builder: white boxes with thin accents; tables on 13 slides; diagrams, checklists, cards, timeline, matrix and 3 native charts elsewhere | User request |
| `docs/PROJECT_DEMO.pptx` | 28 slides rebuilt from `build_clean.mjs` | User request |

| Check | Command or action | Result | Not checked |
| --- | --- | --- | --- |
| Deck build | `node build_clean.mjs c2` | 28 slides; package check pass; 0 layout findings; charts have embedded data sheets | Native PowerPoint not opened |
| Speaker notes | Read notes in the PPTX | 28 of 28 | — |
| Slide review | Read rendered previews 1, 2, 6, 8, 12, 14, 15, 18, 20–22, 24, 26, 27 | Readable; chart labels and colors fixed on 12 and 26 | Other slides checked by the layout validator only |


### 2026-11-05 — Code comments and docstrings

| Area | Change |
| --- | --- |
| `backend/app/models.py` | A comment for each column: meaning, source and the rule that uses it |
| `backend/app/scoring.py` | Module docstring explains the additive points model: 8 categories, points, tiers, unknown data, fields not scored |
| Backend (`app/`, `tests/conftest.py`) | One-line docstring on every function and class |
| Frontend | One-line header per page or multi-export file; `/** */` comment on every top-level function. Time-zone comment fixed (D14, not D15) |

| Check | Result |
| --- | --- |
| Diff review | Only comments and docstrings changed; one `pass` became a docstring |
| `pytest tests --ignore=tests/e2e` | 97 passed |
| `npx tsc --noEmit`, `npm run build` | Pass |
| Browser tests | Not rerun (no behavior change) |

### 2026-11-05 — Company key changed from phone to GAF ID (D26)

| File or system | Change | Reason |
| --- | --- | --- |
| `backend/app/services.py` | `save_prospect` sets `company_key` to the GAF ID; saved-via lookups use the GAF ID | User approved D26 |
| `backend/app/queries.py` | `twins`, Hide saved and "top prospects not saved" match on the GAF ID | Same rule everywhere |
| `backend/app/models.py` | `company_key` is `String(32)` (the width of `gaf_source_id`); comments updated. `phone_digits` and its index stay, but nothing matches on them now | No migrations in the MVP (D5) |
| `backend/tests/conftest.py` | Twin test records share `TEST-TWIN`; the fixture maps records by label | Twins now share a GAF ID |
| Demo database (one-time SQL) | `ALTER TABLE leads ALTER COLUMN company_key TYPE varchar(32)`; `company_key` = GAF ID for the 3 existing leads | Existing rows match the new rule; statuses and status times did not change |
| Docs | `DECISION_LOG.md` (D26), `ARCHITECTURE_AND_DESIGN.md`, `architecture/README.md`, `architecture/save-flow.svg` | Describe the new rule |

| Check | Result |
| --- | --- |
| `pytest tests --browser chromium` after `docker compose up -d --build backend` | 107 passed |
| SQL: listings with one GAF ID in both directories | 36 (same as the phone rule) |
| `GET /prospects/418` | `also_listed_in` and `saved_via` = prospect 1 (unchanged) |
| `GET /prospects/548`, `/559` | No link between them (the phone rule joined them) |
| Not updated | `PROJECT_DEMO.pptx`, `CODE_WALKTHROUGH.html`, `PRODUCT_EVOLUTION.html` still describe the phone rule |
