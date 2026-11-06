# Demo Guide

Status: **Verified on 2026-11-05.** 107 automated tests pass against the local Docker Compose app with the real GAF snapshot (409 prospects). See [TEST_RESULTS.md](TEST_RESULTS.md).

## 1. Setup (before the demo)

```bash
cp .env.example .env              # set POSTGRES_PASSWORD
docker compose up -d --build
docker compose exec backend flask import-snapshot
```

Expected: "176 valid of 176 shown by GAF (complete)" and "233 valid of 233 shown by GAF (complete)". Open http://localhost:3000.

## 2. The story in one minute

- **Problem:** representatives research roofing contractors by hand.
- **Data:** the GAF directory blocks automated clients (HTTP 403), and its URL ignores the ZIP code without `countryCode=us`. We collected the real results for ZIP 10013 within 50 mi one time from a browser: 176 residential and 233 commercial listings, each equal to the total GAF showed.
- **Product:** a deterministic, explainable priority score; one place to save leads and track status; call lists that answer "Who should I contact next?"

## 3. Demo steps

| # | Action | What to point out | Proof |
| --- | --- | --- | --- |
| 1 | Open **Sales dashboard**. | KPI cards, pipeline bar, Call next, Follow up, Top prospects not saved. | Counts equal database counts (`test_dashboard.py`) |
| 2 | Click **Commercial** in the directory toggle. | Every number changes to commercial only. The filter runs in SQL. | `test_directory_toggle...`; dashboard count tests for each directory |
| 3 | Open **Prospects**. Click the **High** bar, then **≤ 10 mi**. | Filter chips; "X prospects"; reason chips in each row. | `test_filters.py`: every row matches, pages never repeat |
| 4 | Click the **Distance** column header. | Nearest first, stable order. | `test_distance_and_name_sorts` |
| 5 | Open Redline Enterprises LLC (prospect 20). | Source facts with "Unknown"; breakdown 10 + 20 + 10 + 5 + 10 + 0 + 5 + 5 = 65 → Medium; "What we don't know". | `test_scoring.py`: 25 hand-calculated records, cutoffs, tier boundaries |
| 6 | Click **Save as lead**. | The status control and **Mark contacted** appear at once. | `test_full_workflow...` (this was bug F2) |
| 7 | Click **Mark contacted** on the lead page. | Status changes to Contacted; the button disappears. It is not in the Saved-leads table. | `test_mark_contacted_is_on_the_lead_page...` |
| 8 | Open Perry's Roofing LLC's commercial listing (prospect 418). | "Saved via Residential listing". Saving it is blocked. | `test_same_company_in_both_directories_returns_409...` |
| 9 | Open **Saved leads** → **Needs first contact**, then **Follow-up due**. | Two call lists; cards say "All saved leads"; the table says "X matching leads". | `test_first_contact_queue...`, `test_follow_up_starts_at_exactly_14_days...` |
| 10 | Reload, run `docker compose restart backend`, reload again. | Leads and statuses are unchanged. | `test_lead_and_status_survive_backend_restart` |

Follow-up due is empty in a fresh demo, because a lead becomes due 14 days after its status changes to Contacted. A test proves the boundary with a test lead.

## 4. Failure and recovery to show

| Show | How | Expected |
| --- | --- | --- |
| Duplicate company | Step 8 | Nothing new is saved; link to the saved listing |
| Invalid request | Open http://localhost:5001/api/v1/leads?sort=oops | 422 with `validation_error` and the field message |
| Failed status update | Chrome DevTools → Network → Offline, then change a status in Saved leads | "The status could not be saved. Try again." and the old value comes back. Go online and change it again: it saves. (Browser test; this was bug F5.) |
| Double click | Double-click **Save as lead** | One lead only |

## 5. What the tests found (talking point)

| Bug | User impact before the fix | Fix |
| --- | --- | --- |
| F1 Distance filter returned 422 | The Distance filter and distance chart never worked | Accept the value as a number and check that it is 10, 25 or 50 |
| F2 Save response had no lead | After Save on the lead page, the Save button stayed | Refresh the database session after the save |
| F5 Raw "Failed to fetch" text | A network error showed browser jargon | Show the action's clear message |
| F7 Page wider than a phone | Sideways scrolling on phones (Prospects 522 px too wide) | Wrapping navigation and toggle; contain a hidden table label |

Full table, including two test bugs and one environment problem: [TEST_RESULTS.md](TEST_RESULTS.md).

## 6. Run the tests live (optional, about 21 seconds)

```bash
cd backend && .venv/bin/pytest tests --browser chromium -q
```

Tests create only `ZZTEST` rows and delete them at the end. The demo data does not change.

## 7. Limits to state

- The data is a one-time GAF snapshot from 2026-11-05. The app does not call GAF.
- There is no login, so all users share the same leads.
- Notes and AI insights are deferred.
- Only Chromium was tested. There is no CI pipeline.

## Presentation

[PROJECT_DEMO.pptx](PROJECT_DEMO.pptx) contains 28 editable slides with speaker notes on every slide. Boxes are white with thin colored accents. About half the slides use tables; the rest use diagrams, checklists, card grids, a comparison layout, a positioning matrix, a timeline and three native charts (tier split, residential vs commercial signals, tests by area). Order: overview (not a table); functional and non-functional requirements; high-level architecture; a line diagram of how a lead is saved; technology choices (REST and Docker Compose removed); Flask vs FastAPI with the REST design; scraping pipeline diagram, parameters and production pipeline diagram; traffic; storage policies; all prospects vs high scores; database model; scoring fields used and not used; ideal residential and commercial profiles; API inventory; frontend; dashboard metrics; reliability; future: three-stage production roadmap, scheduled collection options (cron and others), an append-only lead_events table for rep and AI insights, more capabilities, rollout order; verification: test strategy by test type, results by area (107), failures fixed, evidence limits. Detailed explanations are in speaker notes. There is no demo-sequence slide.

The deck uses the current 409-listing snapshot. The 107-test suite ran on 5 November 2026 before this deck version was built. Slides were rendered and inspected, with package/layout checks. Native PowerPoint behavior remains unverified. The compact handoff is [PRESENTATION_CONTEXT.md](PRESENTATION_CONTEXT.md).

Slide 4 now shows 12 runtime steps and six separate import/scoring steps. It distinguishes commit, save-only ORM expiration, response serialization, error handling and parallel post-save refreshes. The offline version is [request-flow.svg](architecture/request-flow.svg), also embedded in the HTML. The API table uses the current POST status-update route.
