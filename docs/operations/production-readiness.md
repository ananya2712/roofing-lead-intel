# Production Readiness

Status on 2026-11-05: **local MVP, not production-ready.** The app runs in Docker Compose on one computer, with one shared workspace and no login.

Labels in this file: **Observed** (checked), **Assumption**, **Recommendation** (not implemented).

## 1. Current system shape (observed)

| Part | Current state |
| --- | --- |
| Frontend | Next.js 14 production build in a container, port 3000. Forwards `/api/v1` to the backend. |
| Backend | Flask under gunicorn, 2 workers × 4 threads, port 5001 → 5000. |
| Database | PostgreSQL 16 in a container with the named volume `pgdata`. |
| Data | 409 prospects from two GAF snapshot files collected on 2026-11-05. |
| Writes | Save as lead and status change only. |

## 2. Traffic, data volume and targets

- **Unknown:** the number of representatives, requests per second, and availability or latency targets. No targets were set, and no load test was run.
- **Observed data volume:** 409 prospects. The saved-lead count depends on use.
- **Recommendation:** agree on targets (for example, the number of representatives and the acceptable page-load time) before choosing infrastructure.

## 3. Work needed before a production launch (essential)

| Priority | Work | Reason | Affected code |
| --- | --- | --- | --- |
| 1 | Authentication (company single sign-on) | Anyone who can reach the app can change leads | New middleware; frontend layout |
| 2 | Per-representative and territory ownership | Each representative needs their own leads; shared GAF data stays shared | Add `owner_id` and `territory` to `leads`; filter in `services.list_leads` and `overview`; change `uq_leads_company_key` to a per-owner or per-territory rule |
| 3 | Database migrations (Alembic) | `create_all()` cannot change an existing table | `backend/app/db.py`, new `migrations/` |
| 4 | Managed PostgreSQL with backups and a tested restore | A local volume has no backup | Deployment configuration |
| 5 | Secret management | `.env` on disk is not suitable for servers; two unused AI keys are in the local `.env` and should be rotated | Deployment configuration, `.env` |
| 6 | Status history table | Audit trail and trends ("contacted this week") need history | New table written by `services.update_status` |
| 7 | Health checks, logs and alerts | Detect failures before users report them | `/api/v1/health` exists; add request IDs and structured logs |
| 8 | CI pipeline | Run type checks, build and tests on each change | New CI configuration |

## 4. Scaling to hundreds or thousands of representatives (recommendations)

Make these changes only when measurements show a need.

| Concern | Current | Change when needed |
| --- | --- | --- |
| Shared ingestion and deduplication | One-time manual snapshot; upsert on (`directory`, `gaf_source_id`) | One scheduled import job for all representatives; keep the same upsert key; rescore after each import. Representatives never trigger collection. |
| Query cost | `list_leads` and `overview` filter all saved leads in Python | Move filters, counts and sorting to SQL with indexes on `leads(owner_id, status, status_changed_at)` |
| Pagination | Offset pagination with a stable tie-breaker | Keyset (cursor) pagination if lists become large |
| Connections | Each worker pool: 5 + 5 overflow | Calculate pool size × worker count against the database limit; add PgBouncer if the limit is reached |
| Caching | None | Cache `prospects/stats` and the prospect list for a short time, and clear the cache after an import |
| Rate limiting | None | Per-user limits at the gateway |
| API versioning | `/api/v1` and `openapi.yaml` | Add `/api/v2` only for breaking changes; check the contract in CI |
| Stale UI responses | Handled in `lib/useLoad.ts` (abort and ignore late responses) | No change |
| Concurrent edits | Last write wins on status | Add a version column and return 409 on a conflict when several people share a lead |
| Background work | None (all requests are short) | A durable queue (for example a PostgreSQL-backed job table or a managed queue) with timeouts, bounded retries and idempotent jobs, when a slow step is added (for example AI insights or a live data source) |
| Deployment | Docker Compose | Containers on a managed platform; frontend and backend scale on their own |

## 5. Failure modes and recovery (observed behavior)

| Failure | What the user sees | What stays saved | Recovery |
| --- | --- | --- | --- |
| Invalid request | 422 with field messages | Nothing changes | Fix the input |
| Save of a company already saved through its other listing | Message next to the button and a link to the saved listing | The first lead | Open the saved listing |
| Two saves at the same time | One 201, the other 200 or 409 | One lead | None needed |
| Status update fails | Message in the row; the dropdown returns to the old value | The old status | Try again |
| Backend down | Red error banner with **Try again** | All saved data in PostgreSQL | Restart the backend |
| Invalid record in a snapshot file | Import output lists the record and the reason | Valid records import | Fix the file and import again |

## 6. Security gaps

- No authentication or authorization.
- No HTTPS (local only).
- No CSRF protection. Not needed without cookies, but required after a cookie-based login is added.
- The database port 5433 is open on the local computer for development.

## 7. Open decisions

- Who owns a lead when two representatives want the same company?
- How often must GAF data refresh, and from which approved source?
- Which AI insight design (see `additional/insights/README.md`) is approved, if any?
