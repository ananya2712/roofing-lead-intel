# Presentation context

| Topic | Current contract |
| --- | --- |
| Source and output | `CODE_WALKTHROUGH.html` → `PROJECT_DEMO.pptx`, 24 editable slides with speaker notes. Slides 5–10: scraping pipeline (method, parameters, production, traffic, storage, all prospects kept). Slide 13: ideal customer profile and scoring rationale. Slides 22–23: tests and failures fixed. File-control flow slides removed (user request). |
| Format | Follow HTML section order. Concise technical tables; native diagrams. No cover or demo sequence. |
| Decisions | Include rationale, alternatives, limitations and production path. Label inferred comparisons and proposed work. |
| Stack | Next.js/TypeScript → same-origin rewrite → Flask/Pydantic → PostgreSQL/SQLAlchemy. Eight endpoints; three tables. |
| Architecture visual | Slide 4 and embedded HTML diagram: 12 runtime steps, plus six explicit import/scoring steps. Source: `architecture/request-flow.svg` and `.presentation-build/full/architecture_flow.mjs`. |
| Model | `prospects` owns source facts; `prospect_scores` owns versioned scores; `leads` owns rep status. Each prospect has at most one score and saved lead. |
| Initial open | Page and Sidebar issue independent overview/statistics GETs after hydration. No import, rescore or provider call. |
| Save | SaveButton → client/rewrite → route/service → Lead commit → `expire_all()` → detail response → parallel list/statistics refresh. |
| Current product | Sales dashboard, Prospects, detail, Saved leads. 409 recorded listings: 176 residential, 233 commercial. Notes and AI deferred. |
| Evidence | 107 passes (5 Nov 2026, after PATCH → POST, D25). Read-only GETs confirmed health, counts and fixed distance filtering. |
| Presentation boundary | Rendered and inspected; package/layout checks passed. Native PowerPoint not checked. |

Build source and receipts: `docs/.presentation-build/full/`.
