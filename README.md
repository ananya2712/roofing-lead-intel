# Roofing Lead Intel

A sales workspace for representatives of a roofing-materials distributor. It shows roofing contractors from the GAF contractor directory near ZIP 10013, gives each one a rule-based priority score, and lets a representative save leads and track their status.

## What it does

- **Prospects:** all collected GAF listings with filters, a score from 0 to 100, and the reasons for the score.
- **Prospect details:** GAF facts, the score breakdown, and the information that is not known.
- **Saved leads:** prospects that a representative saved, with a status (New, Contacted, Qualified, Dismissed), and two call lists: Needs first contact and Follow-up due.
- **Sales dashboard:** saved and contacted counts, leads to call next, leads to follow up, and top prospects that are not saved.

Not in this version: notes, AI insights (draft code in `additional/insights/`) and login.

## Requirements

- Docker Desktop with Docker Compose v2.
- Free ports 3000 (frontend), 5001 (backend) and 5433 (PostgreSQL).

## Set up and run

1. Copy the environment template, then set a database password:

   ```bash
   cp .env.example .env
   ```

2. Build and start the three services:

   ```bash
   docker compose up -d --build
   ```

3. Import the GAF snapshot files one time. The command also calculates the scores:

   ```bash
   docker compose exec backend flask import-snapshot
   ```

   Expected output for the residential file:

   ```text
   gaf_residential_10013_50mi.json: 176 valid of 176 shown by GAF (complete); 176 new, 0 updated, 0 invalid.
   ```

4. Open http://localhost:3000.

To check the API, open http://localhost:5001/api/v1/health. It returns `{"status": "ok"}`.

## Useful commands

| Task | Command |
| --- | --- |
| Recalculate all scores with the current time | `docker compose exec backend flask rescore` |
| Stop the app and keep the data | `docker compose down` |
| Stop the app and delete the data | `docker compose down -v` |
| Regenerate frontend API types after an `openapi.yaml` change | `cd frontend && npm run gen:api` |
| Run all tests (app must be running) | `cd backend && .venv/bin/pytest tests --browser chromium` (setup in `docs/TEST_RESULTS.md`) |

## Data

The two files in `data/snapshot/` are the only data source. They were collected one time on 2026-11-05 from the GAF directory in a browser (see `docs/DECISION_LOG.md`, D1 and D2). The app makes no live calls to GAF.

| File | Directory | Records |
| --- | --- | --- |
| `gaf_residential_10013_50mi.json` | Residential | 176 of 176 shown by GAF |
| `gaf_commercial_10013_50mi.json` | Commercial | 233 of 233 shown by GAF |

## Documentation

| Document | Content |
| --- | --- |
| `docs/ARCHITECTURE_AND_DESIGN.md` | How the code works: modules, API, data, rules |
| `docs/CODE_WALKTHROUGH.html` | Self-contained code walkthrough for a demo or an interview |
| `docs/architecture/` | System and data-flow diagrams |
| `docs/DEMO_GUIDE.md` | Demo steps, test evidence for each step, and talking points |
| `docs/TEST_RESULTS.md` | Test categories, failures, causes and fixes |
| `docs/DECISION_LOG.md` | Design decisions and their reasons |
| `docs/BUILD_PROGRESS.md` | Build history and manual checks |
| `docs/operations/` | Production readiness and extension plans |
| `openapi.yaml` | API contract |
