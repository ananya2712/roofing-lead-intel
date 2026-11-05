---
name: next-react-frontend
description: Use when designing, building, or reviewing Next.js pages, React components, and Tailwind CSS interfaces in this project.
---

# Frontend Skill

Use this skill for browser UI work in this project. Read the root `AGENTS.md` first. Follow its stack and approved visual direction.

## Stack and boundaries

- Use Next.js 14 with the App Router, React, TypeScript, and Tailwind CSS.
- Use file-based routes. Check current official Next.js documentation when you set up or upgrade Next.js.
- Keep state in the closest component that needs it. Add a shared state library only when approved requirements need state across distant components or pages.
- Use existing project components and installed packages before adding a dependency.
- Do not add a component library by default. Add an accessible primitive only when an interaction needs it and the dependency is approved.
- Keep business-specific components in feature folders.

## Shared UI foundation

Keep shared app components in `frontend/components/ui/`. Create only folders that contain real components:

```text
frontend/components/ui/
  forms/
  data-display/
  feedback/
  layout/
  overlays/
  README.md
```

Build the smallest shared component set that the approved flow needs. Use native HTML with Tailwind for simple controls. Use an existing accessible primitive when an interaction needs keyboard or focus behavior. Do not mix primitive systems in one interaction. Do not wrap every library component.

Give shared components focused responsibilities, typed props, and typed callbacks. Document their purpose, states, accessibility needs, and one example in the UI README. For apps with two pages or fewer, a component gallery is optional. Add `frontend/app/dev/component-gallery/page.tsx` only when previewing shared states will help more than checking the real pages. Keep feature data and API calls out of the gallery. Keep it out of production navigation and make it unavailable in production. Show normal, loading, empty, error, disabled, and long-content states when they apply. Do not add Storybook or another component tool without an approved need.

Add design tokens after the user accepts a visual direction. Use semantic tokens for text, surfaces, fills, borders, and accents. Do not copy another site's palette or typography unless the user selects it.

For the lead dashboard, use the [Closr CRM Analytics Dashboard](https://dribbble.com/shots/27250115-CRM-Analytics-Dashboard-Contacts-Deals-Activity-Closr) selected in `AGENTS.md` for layout and information hierarchy. Use the approved neutral, multi-color palette for the working app. Apply color by purpose, with text labels for status. Show only data and actions the app implements. Keep the table, focus states, contrast, and responsive layouts clear.

## Visual direction and UI review

Use these local rules for visual work:

- Apply the user's selected reference to the real app. Follow the latest explicit design direction and match the provided brand name and capitalization.
- Use a neutral canvas, layered surfaces, purposeful color, and readable type. Make tables and status categories easy to scan. Use text labels with color.
- Check information order, spacing, alignment, labels, contrast, and visible focus. Fix the main problems on the real pages.
- For a new screen or major redesign, review desktop, tablet, and phone widths. Check loading, empty, error, and long-content states that apply.
- For interactive controls, test keyboard access, focus movement, field errors, and dismissal. Use the dialog rules below.
- Keep the approved product style and task scope. Do not add motion, assets, icons, or dependencies only for decoration. Check licenses and give required credit for third-party assets.

External UI references, including [ui-skills](https://github.com/ibelick/ui-skills) and [Taste Skill](https://github.com/Leonxlnx/taste-skill), are optional. Fetch them only when network access is permitted and they help the task. If you skip an external reference, report it. Do not install its tools without approval.

## Asynchronous data and drafts

- Associate each response with the request and record that produced it. Ignore outdated responses when the user changes a filter, opens another record, or starts a newer request. Cancel requests when supported, but also guard against responses that arrive after cancellation.
- Distinguish initial loading, refresh, partial success, empty results, and failure. Keep useful data visible during refresh when appropriate. Show stale data as stale. Prevent duplicate submissions while a mutation is pending.
- Preserve entered values and unsaved edits after validation or network failures. Do not replace a draft with a late response. Reset it after confirmed success or an explicit discard. If navigation can discard work, provide a clear recovery or discard choice. Add persistent browser storage only when approved requirements and data sensitivity permit it.
- After a mutation, reconcile the displayed record, totals, and list order with the saved result. Keep errors near the affected action and offer the supported retry action.

## Dialog focus and dismissal

Use a named dialog with an appropriate initial focus target. For a modal, keep keyboard focus inside it and make background content unavailable to interaction. Support Escape and a visible close control when dismissal is allowed. Define dismissal during pending work and for unsaved drafts. Restore focus to the opening control, or a logical fallback if that control no longer exists. Announce validation and submission errors without losing the user's place. Check opening, tab order, dismissal, and focus restoration with the keyboard.

## Collection navigation

Choose a deliberate collection strategy from expected data volume and user tasks. Use client pagination only when the full result set is bounded and safe to load. Use server pagination for larger sets. Choose page numbers or cursors to fit navigation and data changes. Infinite scrolling needs an approved browsing use case. Keep filtering and sorting consistent across the full collection. Use stable ordering with a tie-breaker. Reset or correct the current page when filters, page size, or deletions make it invalid. Show loading, empty, and failed-page states. Show totals only when known. Preserve navigation state when returning from a record when the flow needs it.

## Interface quality

Apply these rules when they fit the approved design:

- Give icon-only controls accessible names. Prefer native buttons, links, and form elements.
- Give every field a visible label. Show validation errors beside the related field and connect errors to fields with accessible markup.
- Keep paste enabled. Give disabled controls a clear reason when needed.
- Use a confirmation dialog for destructive or irreversible actions. Use an accessible primitive for focus management.
- Show visible keyboard focus. Check text contrast. Do not use color alone to show status.
- Match loading placeholders to the content they replace. Give an empty state one clear action.
- Keep motion off unless the user or approved design asks for it. When motion is needed, keep it brief, use opacity or transform, and respect reduced-motion settings.
- Use tabular numbers when alignment helps. Let long technical text wrap or scroll. Keep full values available when truncating.
- Use spacing to group content before adding divider lines. Use borders to show structure and subtle shadows only to show depth.
- Check responsive layouts and the loading, empty, error, disabled, and long-content states that apply.
