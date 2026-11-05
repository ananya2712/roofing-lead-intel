# Production Extensibility

This file maps likely additions to the code that would change. Everything here is a **proposal**, not implemented.

## What is already easy to extend

- **New data source:** `backend/app/collection/` separates file validation (`snapshot.py`) from storage (`importer.py`). A new source needs a reader that returns `SnapshotRecord` objects. `import_file` and `rescore_all` stay the same.
- **New score rule version:** `scoring.py` is pure functions with a `RULE_VERSION`. `prospect_scores` stores the version and the breakdown, so the UI shows any new category without code changes.
- **New API fields:** add the field to `schemas.py` and `openapi.yaml`, then run `npm run gen:api`. TypeScript then shows every frontend place that must change.

## What needs refactoring first

- `services.list_leads` and `services.overview` filter in Python. Move these filters into `queries.py` before the lead count grows.
- `db.init_db` creates tables with `create_all()`. Add Alembic before the first schema change with real data.

## Planned additions

| Addition | Trigger | Boundary | Data or API change | Compatibility | Verification |
| --- | --- | --- | --- | --- | --- |
| Notes (deferred, D10) | User asks for notes | `services.update_note`, new `PUT /leads/{id}/note` | `note`, `note_updated_at` on `leads`, or a `lead_notes` table for history | Additive fields in `/api/v1` | Note survives reload and restart; empty note rejected |
| AI insights (deferred, D11) | User approves the design in `additional/insights/README.md` | Move `additional/insights/` into `backend/app/`; run jobs from a durable queue, not threads | `lead_insights` table; `insight` object on `LeadInfo` | Additive | Claims cite only fetched URLs; failures show Retry; cost and latency logged |
| Login and ownership | Production launch | Auth middleware; `owner_id` on `leads` | All lead endpoints filter by owner | Breaking for clients that expect shared leads; version the change | Users see only their leads |
| Status history | Managers need trends or an audit | `services.update_status` writes a history row in the same transaction | New `lead_status_events` table | Additive | Every change has one event |
| Scheduled data refresh | Data older than the 30-day freshness limit | Job that runs the importer, then `rescore_all` | None | None | Import report is complete; leads unchanged |
| Other territories | Representatives outside ZIP 10013 | Snapshot header already stores ZIP and radius | Add `search_zip` to `prospects`; distance becomes per territory | Additive | Distances match each territory |
