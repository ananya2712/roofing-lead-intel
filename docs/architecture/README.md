# Architecture diagrams

The SVG files are both the image and the editable source. Edit them in a text editor or a vector editor.

| Diagram | Purpose | Key files and routes |
| --- | --- | --- |
| [demo-data-model.svg](demo-data-model.svg) ([PNG preview](demo-data-model.png)) | Shows the three current tables, ownership, PK/FK fields, uniqueness, and one-to-zero-or-one relationships. SVG is the editable source. Embedded directly in the concise HTML demo guide. | `backend/app/models.py` |
| [system-boundary.svg](system-boundary.svg) | Shows the user, the three Compose services, the snapshot files and the external GAF site | `docker-compose.yml`, `frontend/next.config.mjs`, `backend/app/cli.py` |
| [save-flow.svg](save-flow.svg) | Follows one Save as lead action, with the duplicate and failure paths | `frontend/components/leads/SaveButton.tsx`, `POST /api/v1/prospects/{id}/save`, `backend/app/services.py` (`save_prospect`), `backend/app/models.py` (`uq_leads_company_key`) |

## Text path: system boundary

The representative's browser calls the Next.js frontend on port 3000. The frontend forwards `/api/v1` calls to Flask. Flask reads and writes PostgreSQL. The snapshot files enter only through `flask import-snapshot`. The app never calls gaf.com. The dashed arrow from GAF is the one-time manual collection on 2026-11-05.

## Text path: save flow

1. The button sends a POST and is disabled while the request runs.
2. Next.js forwards the request.
3. Flask loads the prospect and any existing lead.
4. If a lead exists for this prospect, Flask returns 200 and inserts nothing.
5. Otherwise Flask inserts a lead with `company_key` set to the phone digits.
6. The commit succeeds (201), or a unique index rejects it. On rejection, nothing is saved and Flask returns 409 with the other listing's ID.

## Symbols

- Solid arrow: a step the app performs.
- Dashed gray arrow: a manual step outside the app.
- Red box and arrow: the failure path.
- Dashed purple box: the local Compose boundary. There is no login inside it.

## Checks

On 2026-11-05 each arrow was compared with `docker-compose.yml`, `next.config.mjs`, `api/__init__.py` and `services.save_prospect`. Both SVG files were opened in Chrome (through a temporary local HTML wrapper) and inspected at normal size. Text, arrows and colors were readable. The 409 path was also triggered manually: saving residential prospect 1 (Perry's Roofing LLC) returned 201, a repeat returned 200, and saving its commercial listing 418 returned 409 `company_already_saved`.

Related: [decision log](../DECISION_LOG.md), [production readiness](../operations/production-readiness.md).
