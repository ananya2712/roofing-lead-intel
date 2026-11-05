# AI insight (additional functionality, not part of the MVP)

The user removed the AI insight from the MVP on 2026-11-05 and kept it as additional functionality.

This folder holds the draft code that was written before that decision. The app does not import it. It was never run or tested.

## Draft design

- Trigger: a representative saves a prospect. The save is recorded first. A background job generates the insight.
- Inputs: GAF facts, up to 4 pages of the contractor website (`robots.txt` respected, 8-second timeout), and Perplexity citation URLs only when the website names no decision-maker.
- Model: OpenAI with Structured Outputs. The server keeps a claim only when its source URL is in the input. It keeps a contact name only when the fetched page contains that name.
- Output: why the contractor fits, 2–3 conversation topics, a contact (a sourced name or a suggested role), a next action, and source links.
- States: missing, generating, ready, failed (with retry), stale.
- Storage: a `lead_insights` table with one row for each lead.

## Files

| File | Purpose |
| --- | --- |
| `service.py` | Background job, states, retry |
| `generator.py` | Prompt, OpenAI call, validation, template mode |
| `website.py` | Website page fetch |
| `perplexity.py` | Source discovery |

To add the feature, follow `docs/operations/production-extensibility.md`.
