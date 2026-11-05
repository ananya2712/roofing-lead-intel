# Test Results

**Final run on 2026-11-05: 107 passed, 0 failed, 0 skipped (about 21 seconds).** The suite ran again after the status route changed from PATCH to POST (D25); one test was added to prove that PATCH now returns 405.

The tests found 4 application bugs and 2 test bugs, and hit 1 environment problem. Each one is fixed and rerun below.

## 1. How the tests run

| Item | Value |
| --- | --- |
| Environment | Local Docker Compose (`db`, `backend`, `frontend`) on macOS. Tests run on the host in `backend/.venv` (Python 3.13). |
| Database | The demo database (user decision: no separate test database). |
| Isolation rule | Every test row has a `gaf_source_id` that starts with `TEST-` and a name that starts with `ZZTEST`. Tests create and delete only these rows. Real prospects and leads are read only. |
| Proof of isolation | After the run: 0 `TEST-` rows, 409 prospects, and the same 2 real leads (prospect 145 Contacted, prospect 1 New). |
| Test data | 25 `ZZTEST` records, imported through the real importer. Each has a score that was calculated by hand (`backend/tests/conftest.py`). |
| API tests | pytest with the Flask test client and CLI runner (in-process), plus `requests` against the running backend for parallel saves and a restart. |
| Browser tests | Playwright (Chromium) against http://localhost:3000. |

Run the tests:

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements-test.txt
.venv/bin/python -m playwright install chromium
.venv/bin/pytest tests --browser chromium        # needs docker compose up
```

## 2. Results by category

| # | Category | File | Tests | What the tests prove | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | Scoring | `test_scoring.py` | 36 | Total and tier match hand calculations for 25 records. Distance cutoffs at 10.0 / 10.1 / 25.0 / 25.1 / 50.0 mi and unknown. Tiers at 70 / 69 / 45 / 44. Freshness: 5 points at exactly 30 days, 0 points one second later. Unknown is separate from zero (rating 0 vs no rating). Commercial needs technologies for roof-system points. Saving and status changes never change the score. | Pass |
| 2 | API validation and contract | `test_api_validation.py` | 32 | 8 valid GET requests and 3 mutations match `openapi.yaml`. 13 invalid query values return 422 with the standard error shape. Invalid, malformed or non-JSON bodies return 422 and change nothing. Missing IDs return 404. Empty query values mean "no filter". | Pass |
| 3 | Filters and pagination | `test_filters.py` | 11 | 5 filter combinations on the real 409 prospects: every row matches, pages never repeat, the total equals the database count. Default order (score, distance, name), distance sort and name sort. Page beyond the end is empty, not an error. Certification filter. Hide saved also hides the other listing of a saved company. | Pass |
| 4 | Saving and duplicates | `test_saving.py` | 5 | First save: 201 and one lead with status New. Repeat save: 200 and no new row. 8 parallel saves of one prospect: one 201, one row. Same company in both directories: 409 `company_already_saved` with the existing lead. 8 parallel saves across both listings: one lead. | Pass |
| 5 | Snapshot import | `test_import.py` | 4 | CLI import twice: "2 new", then "0 new, 2 updated". Re-import with changed facts updates the facts and the score but keeps the lead, its status and its status time. 3 invalid records are named in the output and the valid record imports ("partial"). Import does not touch the scores of real prospects. | Pass |
| 6 | Dashboard and Saved-lead counts | `test_dashboard.py` | 8 | Dashboard and Saved-lead counts equal database counts for all, residential and commercial, with leads in all 4 statuses. Dismissed is excluded from "saved". Empty pipeline (commercial): 0%, no division error. First-contact call list. Lead sorts never repeat rows across pages. | Pass |
| 7 | Follow-up timing | `test_dashboard.py` | (in 6) | Not due at 14 days minus 1 minute; due at 14 days plus 1 minute. The same status again does not reset the clock; a real change does. | Pass |
| 8 | Persistence | `test_persistence.py` | 1 | A saved lead and its Qualified status survive `docker compose restart backend`. | Pass |
| 9 | Browser workflow and recovery | `e2e/test_browser.py` | 10 | Search → details → score → save → change status → Saved leads → Sales dashboard → reload. Double-click Save makes one lead. A failed status update shows a clear message, restores the old value, and a retry works. A late response does not replace newer results. Save with the keyboard only. No page-level horizontal scroll at 390 px wide on 3 pages. Directory toggle keeps the filter in links. Mark contacted is on the lead page and not in the Saved-leads table. | Pass |
| 10 | Frontend compile checks | `npm run typecheck`, `npm run build` (in `frontend/`) | 2 | Types and production build compile. These checks do not prove behavior. | Pass |

## 3. Failures found, cause and fix

| # | Category | Test that failed | What was observed | Root cause | Fix | Kind | After the fix |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | API validation, filters | `test_valid_get_requests_match_contract[...max_distance=25...]` | `GET /prospects?max_distance=25` returned **422**. | `max_distance` was declared as `Literal[10, 25, 50]`. A query string arrives as text (`"25"`), and Pydantic does not convert text for a `Literal`. **Impact: the Distance filter and the distance chart in the UI never worked.** | `backend/app/schemas.py`: declare `int` and check the allowed values (10, 25, 50) in a validator. | App bug | Pass |
| F2 | Saving (and 15 dependent tests) | `test_first_save_creates_one_lead_with_status_new` and others | `POST /prospects/{id}/save` returned **201 with `"lead": null`**. | The database session still held the prospect loaded with `lead = None`, and `expire_on_commit` is off, so the response used the old object. **Impact: on the lead page, Save showed "Saved", but the Save button stayed and no status control appeared until a reload.** | `backend/app/services.py` `save_prospect`: call `session.expire_all()` after the commit, so the response reads the new lead. | App bug | Pass |
| F3 | Follow-up timing | `test_follow_up_starts_at_exactly_14_days...` | `ResourceClosedError: This result object does not return rows`. | The test helper `sql()` called `.all()` on an `UPDATE`. | `backend/tests/conftest.py`: return rows only when the statement returns rows. | Test bug | Pass |
| F4 | Persistence | `test_lead_and_status_survive_backend_restart` | Save through the running API returned `lead: null`. | This test calls the running container. The container still ran the code from before fix F2. | Rebuilt the backend container (`docker compose up -d --build backend`). | Environment | Pass |
| F5 | Browser recovery | `test_failed_status_update_shows_error_reverts_and_retry_works` | On a network failure, the row showed the raw browser text **"Failed to fetch"**. The old value was restored correctly. | `frontend/lib/api.ts` `unwrap` passed the browser's network exception to the UI. | `unwrap` now changes a network failure into the action's clear message ("The status could not be saved. Try again."). Cancelled requests still pass through, so `useLoad` can ignore them. | App bug | Pass |
| F6 | Browser late response | `test_late_response_does_not_replace_newer_results` | Playwright "strict mode violation": `get_by_label("Search")` found 2 elements. | The filter chip button "Remove filter Search: …" also matches the label "Search". | Test now uses `get_by_role("searchbox", name="Search")`. | Test bug | Pass |
| F7 | Browser narrow screen | `test_narrow_screen_has_no_page_level_horizontal_scroll` (3 pages) | At 390 px: Sales dashboard and Saved leads were 11–12 px too wide; Prospects was 522 px too wide. | (a) The three sidebar links stayed in one row. (b) The directory toggle did not wrap. (c) The hidden "Actions" table header label (`sr-only`, absolutely positioned) escaped the table's scroll area, so the whole page became 912 px wide. | `Sidebar.tsx`: links wrap. `DirectoryToggle.tsx`: buttons wrap. `app/prospects/page.tsx`: the table scroll area is `relative`, so the hidden label stays inside it. | App bug | Pass |

**Change after the run (not a failure):** the user moved Mark contacted out of the Saved-leads table and onto the lead page, and renamed Overview to Sales dashboard. Two browser tests were updated and one test was added for this. The full suite then passed again (106). After the PATCH-to-POST change (D25) it passed with 107 tests.

## 4. Not covered

| Gap | Reason |
| --- | --- |
| Browsers other than Chromium | Only Chromium was installed. |
| Automated accessibility audit (for example axe) | Not in the approved test types. Keyboard save and labels are covered. |
| Slow or failing backend for list pages | One late-response case and one failed-mutation case are covered; long outages are not. |
| Restart with deleted volumes, backup and restore | Out of MVP scope (see `docs/operations/production-readiness.md`). |
| Performance and load | No targets were set. |
| CI | There is no CI pipeline yet. |
