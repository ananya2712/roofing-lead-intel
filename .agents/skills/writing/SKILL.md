---
name: project-writing
description: Use when writing or editing project documentation, interface copy, comments, docstrings, or presentation text in this workspace.
---

# Writing Skill

Use this skill for all project-authored prose. Read the root `AGENTS.md` first. Write in clear English guided by ASD-STE100.

## ASD-STE100 style

- Use short sentences and active voice.
- Use familiar words and one main action in each instruction.
- Keep one main point in each paragraph.
- Use consistent names for the same feature, data, and action.
- Define a technical term when readers may not know it.
- Keep required syntax, identifiers, API names, and standard technical terms unchanged.
- Apply these rules to Markdown, interface text, HTML, comments, docstrings, slide text, and speaker notes.

Treat ASD-STE100 as a writing guide. Do not claim formal compliance unless the current specification and controlled dictionary have been checked.

## Humanizer resource

Use [Humanizer](https://github.com/blader/humanizer) as a supplementary review when project prose needs editing. Remove filler, staged lead-ins, repeated points, unsupported claims, decorative formatting, and stock closers. Keep the writer's meaning, factual details, and neutral tone.

Edit prose only. Preserve code, data, frontmatter, and link targets. Do not optimize text to pass AI detectors. Do not invent names, numbers, dates, quotes, or claims. If a required fact is missing, mark it as unknown or ask for it.

## Evidence and recommendation language

- Match claims to evidence. Use “implemented” for behavior present in code and “verified” only for an observed check. Name the check and its limits. Use “proposed” for work that remains unapproved or unbuilt.
- Keep unknown, unavailable, empty, zero, and failed distinct. Do not call a record verified because one field was checked. Name the checked fields and source when that distinction affects the user.
- State when data was obtained or last updated when freshness matters. Use “current” or “fresh” only with a stated freshness rule and supporting timestamp. Mark an unknown timestamp as unknown.
- Label sample, fixture, simulated, and recorded results where readers encounter them. Do not describe a simulated provider response as a live integration result.
- Describe rule-based scores, rankings, and recommendations by their inputs, criteria, and limits. Use “highest under these rules” rather than an unsupported claim such as “best.” Do not imply a prediction, probability, or independent validation unless evidence supports it. Label generated advice and keep it distinct from calculated results.
- State the failure and available recovery action in user-facing errors. Do not promise that a retry will succeed or that work was saved unless that state is confirmed.

## Comments and technical writing

Make comments explain why the code needs a non-obvious choice. Do not use comments to repeat what the code already says. Keep technical and reference prose neutral and direct. Preserve exact commands, paths, and identifiers when editing surrounding prose.
