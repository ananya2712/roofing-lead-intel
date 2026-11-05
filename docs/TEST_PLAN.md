# Test Plan

Status: **Done on 2026-11-05.** 107 tests pass. Results, failures and fixes: [TEST_RESULTS.md](TEST_RESULTS.md).

## Test types

- **pytest API and database integration tests** with the Flask test client and the CLI runner.
- **Playwright browser tests** (Python pytest plugin) for the user flow.
- Frontend compile checks support these tests but do not prove behavior:

  ```bash
  docker compose exec frontend npm run typecheck
  docker compose exec frontend npm run build
  ```

  Note: the production frontend image contains only the build output. These two commands need the full source and dev dependencies, so run them in `frontend/` on the host (`npm run typecheck`, `npm run build`) or in a dev image.

## Database rule (approved, D22)

Tests run against the demo database. Each test creates its own rows (`gaf_source_id` starts `TEST-`, name starts `ZZTEST`) and deletes them at the end. No test changes rows it did not create.

## Priority order (from the user)

1. Saving and duplicates
2. Scoring
3. Filters and pagination
4. Complete browser workflow

## Test areas

| Area | Tests | Expected result |
| --- | --- | --- |
| Filters and pagination | Combine search, priority, distance, directory and state. Change sort and page. | Every result matches the filters. Order is stable. Pages do not repeat records. |
| API validation | Valid requests; invalid status, tier, scope and sort; page 0; page size over 100; malformed JSON; missing IDs | Valid inputs succeed. Invalid inputs return the standard error shape and change no data. Responses match `openapi.yaml`. |
| Scoring | Calculate expected scores independently. Check distance cutoffs (10, 25, 50 mi), tiers at 45 and 70, freshness at 30 days, and missing fields. | Totals and breakdowns are correct. Unknown stays separate from zero. Saving or a status change does not change the score. |
| Saving and duplicates | Save once, save again, parallel saves, same company through both directories | First save makes one lead. Repeats make no duplicates. Cross-directory saves return 409 with the existing lead. |
| Snapshot import | Import twice; import changed source facts; include invalid records | No duplicate prospects. Saved leads and statuses survive. Invalid records are reported correctly. |
| Dashboard calculations | Compare Overview and Saved-lead counts with database rows. Test every status and an empty pipeline. | Counts agree. Dismissed leads follow the documented rules. No division-by-zero error. |
| Follow-up timing | Contacted leads just before and at 14 days; repeat the same status update | The lead becomes due at 14 days. A repeated status does not reset the timestamp. |
| Browser workflow | Filter → open details → read score → save → change status → Overview → reload | UI and saved data agree at each step. |
| Failures and recovery | Delay or fail requests; change filters fast; double-click Save; retry | Old responses do not replace new results. Errors stay visible. Retry works. Saved work stays. |
| Persistence and usability | Restart without deleting volumes; keyboard navigation; narrow screens | Leads and statuses stay. Controls and tables stay usable. |

Notes and AI insights are deferred, so they are not in this suite.

## Manual checks already done (not automated tests)

See `docs/BUILD_PROGRESS.md` for the full table: repeated import (0 new rows), validation errors, 404, save/repeat/409 on a real cross-directory pair, the 14-day boundary, same-status update, and restart persistence.
