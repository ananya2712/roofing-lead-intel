"""Build docs/CODE_WALKTHROUGH.html as a page-by-page walkthrough.

Pages follow docs/PROJECT_DEMO.pptx slide by slide (same order, group labels and
titles). Each page holds the slide's facts as tables, plus the detailed code
references that the walkthrough must keep (AGENTS.md). ref() fails the build when
a cited function, class or text is missing from the source, and link() fails when
a cited path is missing.

Run: python3 docs/.walkthrough-build/build_walkthrough_pages.py
"""
from pathlib import Path
from datetime import datetime
from html import escape
import ast
import re

root = Path(__file__).resolve().parents[2]
target = root / 'docs/CODE_WALKTHROUGH.html'
DECK = 'docs/PROJECT_DEMO.pptx'

# Embedded copies use dark colors. The standalone diagram sources remain editable.
flow = (root / 'docs/architecture/request-flow.svg').read_text()
db = (root / 'docs/architecture/demo-data-model.svg').read_text()
for old, new in {
    '#FFFFFF': '#0B1220', '#F5F7FA': '#142238', '#EAF5EF': '#12362F',
    '#DCE3EC': '#35485F', '#0E2A47': '#E9F2FF', '#172B42': '#DFE9F6',
    '#53667A': '#A9BBD0', '#2157A4': '#78B7FF', '#16734D': '#65D8AA',
}.items():
    flow = flow.replace(old, new)
db = db.replace('<g fill="#ffffff" font-size="25"', '<g fill="#f6f9ff" font-size="25"')
for old, new in {
    '#ffffff': '#0B1220', '#ccd6e1': '#35485F', '#172b42': '#DFE9F6',
    '#53667a': '#A9BBD0', '#324b65': '#C7D9EE', '#596f86': '#8CA3BD',
    '#2157a4': '#78B7FF', '#16734d': '#65D8AA',
}.items():
    db = db.replace(old, new)
# Keep the colored table headers high-contrast; their labels stay white.
db = (db.replace('fill="#0e2a47"', 'fill="#173B64"', 1)
        .replace('fill="#78B7FF"', 'fill="#2157A4"', 1)
        .replace('fill="#65D8AA"', 'fill="#16734D"', 1))


def c(value):
    return '<code>' + escape(value) + '</code>'


def link(path, label=None):
    if not (root / path).exists():
        raise ValueError(f'Missing linked path: {path}')
    return f'<a href="../{path}">{label or c(path)}</a>'


def ref(path, symbol=None, needle=None):
    text = (root / path).read_text()
    line = None
    if symbol:
        if path.endswith('.py'):
            line = next((n.lineno for n in ast.walk(ast.parse(text))
                         if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == symbol), None)
        else:
            line = next((i for i, s in enumerate(text.splitlines(), 1)
                         if re.search(r'\b(?:function|const)\s+' + re.escape(symbol) + r'\b', s)), None)
    elif needle:
        line = next((i for i, s in enumerate(text.splitlines(), 1) if needle in s), None)
    if (symbol or needle) and line is None:
        raise ValueError(f'Missing source reference: {path}, {symbol or needle}')
    label = path + (f':{line}' if line else '') + (f' · {symbol}()' if symbol else '')
    return link(path, c(label))


def table(caption, headers, rows):
    return ('<div class="scroll" tabindex="0"><table><caption>' + caption + '</caption><thead><tr>'
            + ''.join('<th scope="col">' + h + '</th>' for h in headers) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join('<td>' + v + '</td>' for v in r) + '</tr>' for r in rows)
            + '</tbody></table></div>')


def diagram_table(caption, svg):
    return ('<div class="scroll"><table class="figure-table"><caption>' + caption
            + '</caption><thead><tr><th scope="col">Diagram</th></tr></thead><tbody><tr><td><div class="diagram">'
            + svg + '</div></td></tr></tbody></table></div>')


def sub(key, title, content):
    return f'<h3 id="{key}" tabindex="-1">{title}</h3>' + content


def sources(items, evidence):
    return sub(None, 'Sources and evidence', table(
        'Sources cited in the speaker notes of this slide, plus the code this page references.',
        ['Sources', 'Evidence and limits'], [('<br>'.join(items), evidence)])).replace(' id="None"', '')


STD = ('Facts come from the repository and the observed 107-test run on 5 November 2026. '
       'Comparisons with alternatives are inferred unless a decision ID is cited. Production items are proposals.')
pages = []


def page(key, group, title, *blocks):
    pages.append({'key': key, 'group': group, 'title': title, 'body': ''.join(blocks)})


# 01 ─────────────────────────────────────────────────────────────────────────────
page('project', 'Case study', 'Roofing Lead Intel',
    table('Find, rank and track roofing contractors near ZIP 10013, so a sales representative knows whom to call next and why.',
          ['Measure', 'Value', 'Meaning'], [
        ('GAF listings collected', '409 = 176 residential + 233 commercial', 'All listings that GAF showed for the search; snapshot data, not live search.'),
        ('Territory', '50 miles around ZIP 10013', 'Search radius chosen during collection (see page 8).'),
        ('Tests passing', '107', 'Observed run on 5 November 2026 (see page 26).'),
        ('Stack', 'Next.js · Flask · PostgreSQL', 'Approved stack in ' + link('AGENTS.md') + '.'),
        ('Scoring', 'Fixed, explainable rules', 'Rule v1, 0–100, with a reason for each point (D7).'),
    ]),
    sub('workflow', 'How a representative uses it', table('Product workflow. Steps 1–2 run once by command; steps 3–5 are page actions.',
          ['Step', 'What happens', 'Main code'], [
        ('1 · Collect', 'One-time GAF snapshot, 409 listings.', link('data/snapshot/') + '; ' + ref('backend/app/collection/importer.py', 'import_file')),
        ('2 · Score', 'Fixed rules, 0–100, with reasons.', ref('backend/app/scoring.py')),
        ('3 · Review', 'Filter by distance, tier and directory.', ref('frontend/app/prospects/page.tsx', 'ProspectsView')),
        ('4 · Save', 'One lead per company.', ref('backend/app/services.py', 'save_prospect')),
        ('5 · Follow up', 'New → Contacted → Qualified.', ref('backend/app/services.py', 'update_status')),
    ])),
    sub('scope', 'Who, problem and MVP boundary', table('The brief supplied the user, the territory and the data source.',
          ['Item', 'Essential information'], [
        ('Who', 'Sales representatives of a roofing-materials distributor. They plan accounts and call roofing contractors.'),
        ('Problem', 'Research is manual. There is no single list of nearby contractors with a reason to call, and saved work is hard to track.'),
        ('MVP boundary', 'One shared workspace. Data is a GAF snapshot from 5 November 2026. Notes, AI insights and login are deferred (D10, D11). No CRM sync, outreach automation or per-representative ownership.'),
        ('Evidence labels', '<strong>Recorded:</strong> rationale in the decision log. <strong>Inferred:</strong> technical comparison, not a claim that the author evaluated it. <strong>Proposed:</strong> future work, not implemented.'),
    ])),
    sources([link('README.md'), link('docs/DECISION_LOG.md', c('docs/DECISION_LOG.md') + ' (D1–D3, D7)'), link('docs/TEST_RESULTS.md')],
            'No time saving or sales uplift was measured.'))

# 02 ─────────────────────────────────────────────────────────────────────────────
page('requirements', 'Requirements', 'Functional and non-functional requirements',
    table('Functional requirements: what a representative can do. Status: implemented and tested, except the deferred row.',
          ['Functional requirement', 'Implementation / evidence'], [
        ('Collect GAF contractors, ZIP 10013, 50 mi', '409 listings; 176 + 233 = GAF totals'),
        ('No duplicates on re-import', 'Upsert on directory + GAF ID; second import reports "0 new"'),
        ('Find prospects', 'Search, directory, tier, distance, state, certification, sort'),
        ('Explain priority', 'Score 0–100, breakdown, Unknown fields'),
        ('Save leads', 'One lead per company; 409 for the twin listing'),
        ('Track status', 'New → Contacted → Qualified / Dismissed'),
        ('Know whom to call', 'Needs first contact; Follow-up due (14 days)'),
        ('Separate segments', 'Residential / Commercial toggle; SQL directory filter'),
        ('Deferred', 'Notes, AI insights, login'),
    ]),
    table('Non-functional requirements: how well the system must do it.', ['Non-functional requirement', 'Implementation / evidence'], [
        ('Repeatable scoring', 'Rule v1 with an explicit effective time; 36 scoring tests'),
        ('Data integrity', 'Unique keys, transactions, rollback'),
        ('Input validation', 'Pydantic; 422 with field messages; PATCH on the status route returns 405'),
        ('Consistent API', c('/api/v1') + ', one error shape, OpenAPI'),
        ('Usable UI', 'Loading, empty and error states; checked at 390 px'),
        ('Accessible controls', 'Labels, keyboard save, text plus color'),
        ('Resilient UI', 'Late responses ignored; clear retry'),
        ('Maintainable code', 'Routes → services → queries'),
        ('Verified', '107 tests: pytest + Playwright'),
    ]),
    sub('requirement-limits', 'Known limits', table('Implementation is not the same as proof for every case.', ['Area', 'Limit'], [
        ('Priority', 'No purchase-intent or revenue prediction. Weights are not calibrated against sales results.'),
        ('Saved work', 'No contact log, notes, status history or owner isolation.'),
        ('Concurrency', 'Parallel saves are tested. Concurrent status edits are not tested and have no version check.'),
        ('Browser coverage', 'Chromium only. No full accessibility audit. List-page outages are not tested.'),
    ])),
    sources([ref('backend/app/services.py'), ref('backend/app/schemas.py'), ref('backend/app/models.py'), link('frontend/app/', c('frontend/app/*')), link('docs/TEST_RESULTS.md')],
            STD))

# 03 ─────────────────────────────────────────────────────────────────────────────
startup = table('Source-traced control flow, not an instrumented browser trace. Startup occurs when services launch, not every time a page opens.', ['Phase', 'File / function', 'Control and result'], [
    ('Backend worker start', ref('backend/wsgi.py', needle='app = create_app()') + ' → ' + ref('backend/app/__init__.py', 'create_app'), 'Gunicorn imports wsgi:app. create_app calls load_config, init_db, then registers session cleanup, JSON error handlers, /api/v1 blueprint, and CLI commands.'),
    ('Configuration / database', ref('backend/app/config.py', 'load_config') + ' → ' + ref('backend/app/db.py', 'init_db'), 'Read environment configuration; create engine/session factory; acquire PostgreSQL advisory transaction lock; create missing tables. No snapshot import runs here.'),
    ('Initial app route', ref('frontend/app/layout.tsx', 'RootLayout') + ' → ' + ref('frontend/app/page.tsx', 'OverviewPage'), 'Assume services already run. GET / selects the Sales dashboard (OverviewPage component; renamed by D23), not a redirect to Prospects. The shared layout includes Sidebar and page content.'),
])
first_open = table('A = Overview request; B = Sidebar badge request. A and B start independently after hydration. Rows describe dependencies within each branch, not one global network order.', ['Step', 'File / function', 'Action / next call', 'Visible or database effect'], [
    ('1', ref('frontend/app/layout.tsx', 'RootLayout') + '; ' + ref('frontend/app/page.tsx', 'OverviewPage'), 'Next.js serves the page shell. React hydrates the client components; OverviewPage renders OverviewView inside Suspense.', 'Shared navigation and initial loading placeholders.'),
    ('2A', ref('frontend/app/page.tsx', 'OverviewView') + ' → ' + ref('frontend/app/page.tsx', 'load'), 'useEffect calls load. Read optional directory from URL; api.GET("/overview", {directory}) is wrapped with unwrap.', 'Starts the main overview read; no writes.'),
    ('2B', ref('frontend/components/ui/layout/Sidebar.tsx', 'Sidebar'), 'Its pathname-dependent useEffect independently calls api.GET("/prospects/stats") without a directory filter.', 'Starts an all-directory badge read; completion order relative to A is unspecified.'),
    ('3A / 3B', ref('frontend/lib/api.ts', needle='export const api') + ' → ' + ref('frontend/next.config.mjs', needle='async rewrites()'), 'openapi-fetch requests /api/v1/overview or /api/v1/prospects/stats. Next.js forwards the URL to Flask.', 'Runtime HTTP boundary. The rewrite configuration is loaded by Next.js, compiled build/startup routing configuration, not a per-request application function.'),
    ('4A', ref('backend/app/api/__init__.py', 'overview') + ' → ' + ref('backend/app/schemas.py', 'DirectoryQuery') + '; ' + ref('backend/app/db.py', 'get_session'), 'Validate optional directory, obtain request-scoped session, call services.overview(session, directory).', 'Invalid query can return 422; valid input enters service logic.'),
    ('5A', ref('backend/app/services.py', 'overview') + ' → ' + ref('backend/app/queries.py', 'all_leads'), 'Load saved leads with related prospects/scores; _lead_summary computes display fields and follow_up_due. Count statuses and build call/follow-up lists.', 'Reads PostgreSQL; computes current-state metrics.'),
    ('6A', ref('backend/app/queries.py', 'top_unsaved') + ' → ' + ref('backend/app/services.py', 'summarize_prospects') + ' → ' + ref('backend/app/queries.py', 'stats'), 'Select high-priority unsaved prospects; summarize using twins then saved_leads_by_key. Read stats last for the overview retrieval timestamp.', 'Stored scores are read and formatted; no rescore or snapshot lookup.'),
    ('4B / 5B', ref('backend/app/api/__init__.py', 'prospect_stats') + ' → ' + ref('backend/app/services.py', 'prospect_stats'), 'Validate DirectoryQuery; get_session; queries.stats → queries.all_leads → queries.count_high_unsaved.', 'Build ProspectStats. Sidebar will use only total and saved.'),
    ('7A / 7B', ref('backend/app/api/__init__.py', '_json') + '; ' + ref('backend/app/db.py', 'close_session'), 'Pydantic model_dump(mode="json") → Flask jsonify → HTTP response through Next.js. Request teardown closes the database session.', 'Two independent JSON responses; no mutation.'),
    ('8A / 8B', ref('frontend/lib/api.ts', 'unwrap') + '; ' + ref('frontend/app/page.tsx', 'load') + '; ' + ref('frontend/components/ui/layout/Sidebar.tsx', 'Sidebar'), 'A: unwrap returns Overview; load sets page data. B: Sidebar reads returned data directly and sets badge counts.', 'React renders KPIs/call lists and navigation badges independently. The initial Overview request does not use useLoad.'),
])
page('flow', 'Architecture', 'High-level architecture',
    diagram_table('System request path. The setup path (snapshot import) runs by command, outside page requests.', flow),
    table('Two paths: page requests at run time, and a one-time setup by command.', ['Path', 'Parts', 'Boundary'], [
        ('Request path · every page view and save', 'Sales rep → browser → Next.js frontend (4 pages, typed API client, ' + c('/api/v1') + ' proxy) → Flask API (validation, services, scoring rules) → PostgreSQL (prospects, prospect_scores, leads)',
         'Pages call the typed client. Next.js forwards /api/v1 to Flask on the same origin. Flask validates input, runs services and queries, and returns JSON. A save commits one lead row; the page then reloads the list and counts. Late responses are ignored.'),
        ('Setup path · one time, by command', 'GAF directory (external; blocks servers with 403) → browser, once → 2 snapshot JSON files (409 records, retrieved_at) → ' + c('flask import-snapshot') + ' (validate, upsert, score)',
         'Validate each record, normalize phones and addresses, upsert by directory + GAF ID, then rescore only the imported rows. Leads are never changed. Invalid records are listed and skipped.'),
        ('Excluded at run time', 'No live GAF or AI call; no background jobs or cache; one shared workspace, no login',
         'All writes are short transactions in PostgreSQL. Runs as three containers locally (Docker Compose).'),
    ]),
    table('Current execution paths; comparisons are inferred except snapshot choice D1 and proxy choice D15.', ['Path', 'Implementation', 'Why this boundary', 'Alternative / trade-off'], [
        ('Data ingestion', 'GAF browser collection → JSON → CLI validation/upsert → stored scores.', 'D1: one-time collection avoids a runtime dependency on blocked GAF scraping.', 'Live API/feed: better freshness, but approved access and refresh policy are not available in the current implementation.'),
        ('Browser request', 'Typed client → same-origin /api/v1 → Next.js rewrite → Flask route → service/query → PostgreSQL.', 'D15: one browser origin avoids separate cross-origin configuration.', 'Direct browser-to-Flask calls: workable, but require explicit CORS and deployment-origin management.'),
        ('Save/status mutation', 'Validate → service write → commit → response → reconcile UI.', 'Commit defines persisted truth; UI pending/error state is not persistence.', 'Optimistic UI alone cannot enforce identity or recover an ambiguous commit.'),
        ('Service layout', 'Modular monolith: routes, services, queries, models.', 'Keeps HTTP, policy, and persistence responsibilities separate.', 'Microservices introduce distributed failures and deployment boundaries without a measured need.'),
    ]),
    sub('control', 'File-by-file control flow: reading order', table('Read each path in order; independent HTTP branches can complete in either order.', ['Path', 'Entry point', 'Reading order'], [
        ('<a href="#startup-control">Service startup</a>', 'Gunicorn imports wsgi:app.', 'Configuration and database initialization occur before the browser paths.'),
        ('<a href="#first-open-control">Initial opening</a>', 'GET / → RootLayout → OverviewPage.', 'Overview read (A) and Sidebar statistics read (B) run independently.'),
        ('<a href="#prospect-save-control">Save from Prospects</a> (page 4)', 'List-row SaveButton → save().', 'Write transaction and response, then independent list/statistics refreshes.'),
    ])),
    sub('startup-control', 'Service startup and entry point', startup),
    sub('first-open-control', 'When the app first opens at /', first_open),
    sources([link('frontend/next.config.mjs'), link('frontend/lib/api.ts'), link('backend/app/api/__init__.py'), link('backend/app/services.py'), link('backend/app/cli.py'), link('backend/app/models.py')], STD))

# 04 ─────────────────────────────────────────────────────────────────────────────
save_flow = table('Starts on an already-loaded Prospects list; the onSaved callback is the one attached to each list-row SaveButton.', ['Step', 'File / function', 'Action / next call', 'State / persistence'], [
    ('0', ref('frontend/app/prospects/page.tsx', 'ProspectsView') + '; ' + ref('frontend/lib/useLoad.ts', 'useLoad'), 'Earlier GET /prospects supplied list.data.items. Each row renders SaveButton with prospectId, savedLeadId, savedVia, and an onSaved callback.', 'An existing savedLeadId renders Saved; savedVia renders a link rather than an active save button.'),
    ('1', ref('frontend/components/leads/SaveButton.tsx', 'save'), 'Click invokes save(): setPending(true), clear the error, call api.POST("/prospects/{prospect_id}/save").', 'Button disables and shows Saving. A double click sends one request. No request body is needed.'),
    ('2', ref('frontend/lib/api.ts', needle='export const api') + ' → ' + ref('frontend/next.config.mjs', needle='async rewrites()'), 'The typed client sends POST /api/v1/prospects/{id}/save; Next.js forwards it to Flask.', 'unwrap awaits the request; api-types.ts is not a runtime network step.'),
    ('3', ref('backend/app/api/__init__.py', 'save_prospect') + ' → ' + ref('backend/app/db.py', 'get_session'), 'Flask integer path converter supplies prospect_id. Route calls services.save_prospect(session, prospect_id).', 'No Pydantic request-body model is involved in this bodyless endpoint.'),
    ('4', ref('backend/app/services.py', 'save_prospect') + ' → ' + ref('backend/app/queries.py', 'prospect_with_everything'), 'Read prospect with joined score and lead. Missing prospect raises 404; existing lead returns existing detail with created=False.', 'No insert on missing/already-saved paths.'),
    ('5', ref('backend/app/services.py', 'save_prospect') + ' → ' + ref('backend/app/models.py', 'Lead'), 'For an unsaved prospect, session.add(Lead(prospect_id=p.id, company_key=p.phone_digits, status="new")).', 'Pending ORM insert; not persisted until commit.'),
    ('6', ref('backend/app/services.py', 'save_prospect') + '; ' + ref('backend/app/models.py', needle='uq_leads_company_key'), 'session.commit flushes INSERT. Unique prospect_id and the partial company_key unique index enforce identity.', 'Successful transaction persists one lead with New status and saved/status timestamps.'),
    ('7', ref('backend/app/services.py', 'save_prospect') + ' → ' + ref('backend/app/services.py', 'prospect_detail'), 'After a successful new insert, session.expire_all invalidates loaded ORM state. prospect_detail reloads the prospect and new lead.', 'Important because expire_on_commit=False can otherwise retain the old lead=None relationship (bug F2).'),
    ('8', ref('backend/app/services.py', 'prospect_detail') + ' → ' + ref('backend/app/queries.py', 'prospect_with_everything'), 'Read joined row; twins → saved_leads_by_key; construct ProspectDetail with stored score, unknown fields, and LeadInfo.', 'No new score computation, provider call, note, or insight generation.'),
    ('9', ref('backend/app/api/__init__.py', 'save_prospect') + ' → ' + ref('backend/app/api/__init__.py', '_json'), 'created=True gives 201; created=False gives 200. Serialize ProspectDetail and return through Next.js.', 'Response identifies confirmed saved state.'),
    ('10', ref('frontend/lib/api.ts', 'unwrap') + ' → ' + ref('frontend/components/leads/SaveButton.tsx', 'save'), 'unwrap returns detail; SaveButton calls onSaved(detail). finally resets pending.', 'On an error, catch sets the row-local error and finally re-enables the button.'),
    ('11', ref('frontend/app/prospects/page.tsx', needle='onSaved={() => { setMsg('), 'The row callback sets the success message, calls list.reload(), and starts loadStats().', 'List and summary GETs can overlap; one response does not wait for the other.'),
    ('12A', ref('frontend/lib/useLoad.ts', 'run') + ' → ' + ref('backend/app/api/__init__.py', 'list_prospects') + ' → ' + ref('backend/app/services.py', 'list_prospects'), 'GET /prospects keeps current filters. ProspectQuery → queries.prospect_page → summarize_prospects; useLoad accepts the latest result.', 'Row now shows Saved, or leaves the list when hide_saved=true.'),
    ('12B', ref('frontend/app/prospects/page.tsx', 'loadStats') + ' → ' + ref('backend/app/api/__init__.py', 'prospect_stats') + ' → ' + ref('backend/app/services.py', 'prospect_stats'), 'GET /prospects/stats keeps selected directory; returned counts update page stats.', 'Prospects summary refreshes. No automatic navigation occurs.'),
])
page('save-flow', 'Architecture', 'How a lead is saved',
    table('Slide summary: request, then database and response. Committed database state comes first; the UI refreshes from the server response.', ['Step', 'Action', 'Detail'], [
        ('1 · Click Save', 'SaveButton', 'Button disabled while pending'),
        ('2 · Typed client', c('POST /api/v1/prospects/{id}/save'), 'openapi-fetch client'),
        ('3 · Proxy + route', 'Next.js rewrite → Flask ' + c('save_prospect()'), 'Same origin'),
        ('4 · Load', 'Prospect + score + existing lead', 'Existing lead → 200, no new row'),
        ('5 · Insert lead', 'Status New; company_key = phone digits', 'Pending until commit'),
        ('6 · Commit', 'Unique: prospect_id, company_key', 'Races are decided here'),
        ('7 · Respond', c('expire_all()') + ' → ProspectDetail, 201', 'Response includes the new lead'),
        ('8 · UI refresh', '"✓ Saved"; reload list + counts', 'The two reloads run in parallel'),
    ]),
    sub('prospect-save-control', 'File-by-file control flow: Save as lead in Prospects', save_flow),
    sub('control-branches', 'Other outcomes, refreshes and excluded work', table('Branches and ordering limits are source-derived; the save races are also covered by tests (page 26).', ['Case', 'File / control branch', 'Result'], [
        ('Lead already exists', ref('backend/app/services.py', 'save_prospect'), 'Step 4 finds a lead: return 200 with the detail. No new row.'),
        ('Other listing of the company saved', ref('backend/app/services.py', 'save_prospect') + '; ' + ref('backend/app/models.py', needle='uq_leads_company_key'), 'Commit fails on company_key: rollback, then 409 ' + c('company_already_saved') + ' with the other prospect and directory.'),
        ('Parallel save of the same prospect', ref('backend/app/services.py', 'save_prospect'), 'Commit fails on prospect_id: rollback, then 200 with the existing detail. 8 parallel saves → 1 lead.'),
        ('Server / network failure', ref('backend/app/errors.py', 'register_error_handlers') + '; ' + ref('frontend/components/leads/SaveButton.tsx', 'save'), 'Safe error JSON or failed fetch reaches unwrap/catch. A UI error does not prove that no commit occurred; retrying the same prospect recovers the existing row.'),
        ('Sidebar after same-page save', ref('frontend/components/ui/layout/Sidebar.tsx', 'Sidebar'), 'Sidebar effect depends on pathname. The Prospects save callback does not change pathname, so the sidebar badge can stay stale until navigation/remount.'),
        ('Then: change status', ref('backend/app/api/__init__.py', 'update_status') + ' → ' + ref('backend/app/services.py', 'update_status'), c('POST /api/v1/leads/{id}/status') + '. status_changed_at changes only on a real change.'),
        ('Not part of either runtime path', link('openapi.yaml') + '; ' + link('frontend/lib/api-types.ts') + '; ' + link('backend/app/cli.py'), 'OpenAPI/type generation is build-time tooling. Import/rescore are explicit CLI operations. Opening the app or saving does not read JSON snapshots, run scoring, or call GAF/AI providers.'),
    ])),
    sources([link('frontend/components/leads/SaveButton.tsx'), link('frontend/lib/api.ts'), link('frontend/next.config.mjs'), ref('backend/app/api/__init__.py', 'save_prospect'), ref('backend/app/services.py', 'prospect_detail'), ref('backend/app/models.py', needle='uq_leads_company_key'), ref('frontend/app/prospects/page.tsx', needle='onSaved')], STD))

# 05 ─────────────────────────────────────────────────────────────────────────────
page('stack', 'Design decisions', 'Technology choices',
    table('Approved stack (AGENTS.md). Rationale and alternative comparisons are inferred unless a decision ID is cited.',
          ['Choice', 'Why it fits this MVP', 'Cost / limitation', 'Alternative', 'Why the alternative is not used here'], [
        ('Next.js 14 + React + TypeScript + Tailwind', 'File routes, typed pages, shared pastel tokens, same-origin API proxy.', 'Separate frontend build; generated types do not validate HTTP at run time.', 'Vite + React SPA', 'Also viable; a proxy and routing must be added by hand. Changing frameworks adds migration work without a new MVP capability.'),
        ('Flask + Pydantic', 'Small Python API; explicit validation at the boundary; Flask CLI for the import.', 'OpenAPI must be maintained by hand.', 'FastAPI', 'Compared on page 6. Moving the existing Flask services/routes is not required for this MVP.'),
        ('PostgreSQL + SQLAlchemy 2', 'Relations, unique and check constraints, JSONB score breakdown, safe parallel writes.', 'Requires a database service; PostgreSQL-specific types reduce portability.', 'SQLite or JSON files', 'Files have no constraints; SQLite is weaker for parallel writes.'),
        ('Scores stored in their own table', 'Fast sorting and filtering; rescore never touches leads (D4).', 'Freshness points age until an explicit rescore.', 'Calculate on every request', 'Always fresh, but more work per request, and visible scores can change with time.'),
        ('Fixed scoring rules, no AI', 'Explainable, repeatable, testable; same input gives the same score (D7).', 'Weights are not calibrated against sales results.', 'LLM ranking', 'Hard to explain, costs money, can vary between runs.'),
        ('REST + OpenAPI + generated TypeScript client', 'Explicit resource contracts and compile-time caller checks.', 'Routes, schemas, YAML and generated types must stay aligned.', 'GraphQL / handwritten fetch types', 'No requirement for client-selected graph traversal. Handwritten types add another manual contract that can drift.'),
        ('Docker Compose', 'One local service definition; named database volume and service DNS.', 'Three containers and image builds add local overhead.', 'Host-installed processes / Kubernetes', 'Host processes require manual setup. Kubernetes adds orchestration without measured availability or scale requirements.'),
        ('pytest + Playwright', 'Real API, database and browser checks; found 4 application bugs.', 'Tests use the demo database with marker rows (D22).', 'Unit tests only', 'Would miss integration bugs such as F1 and F2.'),
    ]),
    sources([link('AGENTS.md'), link('backend/requirements.txt'), link('frontend/package.json'), link('docs/DECISION_LOG.md')], STD))

# 06 ─────────────────────────────────────────────────────────────────────────────
api_style = [
    ('Resources', c('/prospects') + ', ' + c('/prospects/{id}') + ', ' + c('/prospects/stats') + ', ' + c('/leads') + ', ' + c('/leads/{id}/status') + ', ' + c('/overview') + ', ' + c('/health')),
    ('Methods', 'GET for reads (6). POST for save and status change (2). PATCH returns 405 (D25).'),
    ('Status codes', '200, 201, 404, 405, 409, 422; unexpected failures return a safe 500.'),
    ('Versioned prefix', c('/api/v1')),
    ('One error shape', c('{"error": {"code", "message", "details"}}')),
    ('Stateless requests', 'Filters and pages in the query string.'),
    ('Safe repeat', 'Saving again returns 200 and adds no row.'),
    ('Contract', link('openapi.yaml') + ' → generated TypeScript client (openapi-typescript, openapi-fetch).'),
]
page('flask-fastapi', 'Design decisions', 'Flask vs FastAPI, and the REST design',
    table('Verdict: FastAPI would remove contract upkeep; Flask stays for the approved stack and the small API. Comparison inferred.', ['Criterion', 'Flask (chosen)', 'FastAPI'], [
        ('Validation', 'Pydantic models called in each route', 'Pydantic built into function signatures'),
        ('API contract', c('openapi.yaml') + ' by hand; 11 contract tests catch drift', 'OpenAPI generated from code'),
        ('Async', 'Sync WSGI, gunicorn 2 workers × 4 threads; short database calls', 'Native async; helps many slow I/O calls'),
        ('CLI and setup', 'Flask CLI: ' + c('import-snapshot') + ', ' + c('rescore'), 'Needs Typer or separate scripts'),
        ('Errors', 'One handler set: ApiError, 404, 405, 422, 500', 'Similar, with a built-in 422 shape'),
        ('Fit', 'Approved stack; 8 endpoints', 'Stack change; little gain at this size'),
    ]),
    sub('rest-design', 'REST rules in this API', table('How the eight endpoints follow REST conventions.', ['Rule', 'In this API'], api_style)),
    sub('rest-example', 'Example', table('A save of the second listing of an already-saved company.', ['Request', 'Response'], [
        (c('POST /api/v1/prospects/418/save'), '409 ' + c('{"error": {"code": "company_already_saved", "details": {"prospect_id": 1}}}')),
    ])),
    sub('api-design', 'API design choices', table('API design comparisons are inferred.', ['Choice', 'Why', 'Alternative', 'Why not / limit'], [
        ('Thin handlers + Pydantic', 'Validate the trust boundary; services own business behavior.', 'Validation and business logic inside page/route code', 'Duplicates rules across entry points and couples persistence to HTTP.'),
        ('Resource-oriented JSON /api/v1', 'Stable URLs and explicit errors for four UI views.', 'RPC-only actions or GraphQL', 'No current consumer needs the additional protocol or query machinery.'),
        ('Idempotent repeated save + unique constraints', 'A retry after a lost response can recover the existing lead.', 'Check-then-insert in UI only', 'Cannot prevent races between clients. A durable request-id ledger is not implemented.'),
    ])),
    sources([link('backend/app/api/__init__.py'), link('backend/app/schemas.py'), link('backend/app/errors.py'), link('openapi.yaml'), link('frontend/lib/api.ts'), link('backend/tests/test_api_validation.py'), link('AGENTS.md'), link('backend/Dockerfile', c('backend/Dockerfile') + ' (gunicorn -w 2 --threads 4)')], STD))

# 07 ─────────────────────────────────────────────────────────────────────────────
page('collection', 'Data collection', 'Scraping pipeline: how the data was collected',
    table('One-time collection on 5 November 2026 in the user\'s Chrome, then a local import. Not a live in-app scraper.', ['Stage', 'Step', 'Detail', 'Code / data'], [
        ('Collect', '1 · Search URL', c('postalCode=10013, distance=50, countryCode=us'), '—'),
        ('Collect', '2 · Result pages', '42 pages × 10 cards; click Next (GAF search service)', '—'),
        ('Collect', '3 · Profile pages', '409 requests, one at a time, about 1.5 s apart', '—'),
        ('Collect', '4 · Parse', 'JSON-LD address, website link, details, certifications', '—'),
        ('Import', '5 · Snapshot JSON', '2 files; retrieved_at on every record', link('data/snapshot/')),
        ('Import', '6 · Normalize + upsert', 'Phone digits, address; key = directory + GAF ID', ref('backend/app/collection/snapshot.py') + '; ' + ref('backend/app/collection/importer.py', 'import_file')),
        ('Import', '7 · Score', 'Rule v1 on imported rows only (D21); ' + c('flask rescore') + ' recalculates all', ref('backend/app/scoring.py')),
        ('Import', '8 · PostgreSQL', '409 prospects + 409 scores', ref('backend/app/models.py')),
    ]),
    table('Checks made during collection and import.', ['Topic', 'Observed result'], [
        ('Blocked path', 'Plain HTTP from a server got 403 (Akamai bot protection), also for robots.txt. A headless scraper would work against GAF\'s block, so none was built.'),
        ('Checks', 'The URL ignores postalCode unless countryCode=us is present (tested with ZIP 90210). Unique GAF IDs equal the GAF totals: 176 of 176 and 233 of 233. 0 failed profile requests.'),
        ('Result', '409 prospects. A second import adds 0 rows. 36 companies appear in both directories (same phone). Invalid records are reported and skipped.'),
    ]),
    sources([link('data/snapshot/', c('data/snapshot/*.json')), link('backend/app/collection/snapshot.py'), link('backend/app/collection/importer.py'), link('backend/app/cli.py'), link('docs/DECISION_LOG.md', c('docs/DECISION_LOG.md') + ' (D1–D3)')],
            'One-time manual collection on 5 November 2026 with the user. GAF terms were not reviewed for production use. Raw HTML was not stored.'))

# 08 ─────────────────────────────────────────────────────────────────────────────
page('collection-parameters', 'Data collection', 'Scraping parameters and captured fields',
    table('Exact search parameters. Key finding: without countryCode=us, GAF silently uses the visitor\'s IP location.', ['Parameter', 'Value', 'Reason / evidence'], [
        ('Directories', 'residential, commercial', 'Both roof segments (D3)'),
        ('postalCode', '10013', 'Territory in the brief'),
        ('distance', '50 mi (GAF offers 25 / 50 / 100)', '409 listings vs 238 at 25 mi; residential 370 at 100 mi'),
        ('countryCode', 'us', 'Without it GAF uses IP location (ZIP 90210 test)'),
        ('Paging', '10 cards per page; 18 + 24 pages', '176 + 233 = totals shown by GAF'),
        ('Pacing', '1 profile request at a time, about 1.5 s apart', 'Low load on GAF; 0 failed requests'),
        ('Fields captured', 'GAF ID, profile URL, name, phone, website, address, about, years in business, distance, rating, reviews, distinctions, specialties / technologies', 'Business facts only; no raw HTML'),
        ('Timestamps', 'retrieved_at on each record; collected_at on each file', '30-day freshness rule'),
        ('Gaps found', '81 residential + 209 commercial without website; 24 without rating', 'Shown as Unknown; 0 points'),
    ]),
    sources([link('data/snapshot/', c('data/snapshot/*.json') + ' (header: search_url, expected_total, collected_at)'), link('docs/DECISION_LOG.md', c('docs/DECISION_LOG.md') + ' (D2, D3)')], STD))

# 09 ─────────────────────────────────────────────────────────────────────────────
page('production-pipeline', 'Data collection', 'Extending the pipeline to production',
    table('Proposed design; not implemented. "Exists today" parts are current code.', ['Component', 'Role', 'Status'], [
        ('Scheduler', 'One job per territory, before 30 days', 'New for production'),
        ('Job queue', 'Durable; one job per ZIP + radius', 'New for production'),
        ('Collector workers', 'Licensed feed or partner API; rate limit, backoff, bounded retries', 'New for production'),
        ('Validate + normalize', 'Same Pydantic and normalize code', 'Exists today'),
        ('Upsert prospects', 'Key: directory + GAF ID; leads untouched', 'Exists today'),
        ('Rescore', 'Versioned rules; imported rows', 'Exists today'),
        ('collection_runs table', 'Parameters, counts, status, errors', 'New for production'),
        ('Monitoring + alerts', 'Partial run, count drop, 403 / 429', 'New for production'),
    ]),
    table('Build order.', ['Order', 'Step', 'Why first'], [
        ('1', 'Approved data access + legal review', 'Scraping a site that blocks bots is not a production basis'),
        ('2', 'Scheduler + collection_runs table', 'Repeatable runs with a record of each one'),
        ('3', 'Completeness alerts', 'A silent partial run would hide prospects'),
        ('4', 'Queue + workers', 'Only when territories or volume grow'),
    ]),
    sub('production-collection', 'Code boundaries for the change', table('The current importer reads local JSON. Live collection requires approved source access.', ['Change', 'Code boundary', 'Why / proof needed'], [
        ('Approved source reader', ref('backend/app/collection/snapshot.py') + ', ' + ref('backend/app/collection/importer.py', 'import_file') + ', ' + ref('backend/app/cli.py'), 'Extract a reader interface: import_file currently calls load_snapshot directly. Preserve directory + source ID and reject invalid or duplicate records.'),
        ('Scheduled refresh', 'CLI + future job runner', 'Run one refresh per source with run ID, completeness checks, bounded retry, alerts, and source timestamps. Verify that repeat imports preserve lead status.'),
        ('Publish scores with facts', ref('backend/app/collection/importer.py') + ', ' + ref('backend/app/scoring.py') + ', ' + c('prospect_scores'), 'Current source and score writes commit separately. Stage or publish a complete run so a scoring failure cannot expose mismatched facts and scores.'),
    ])),
    sources([link('backend/app/collection/importer.py'), link('backend/app/scoring.py'), link('docs/operations/production-readiness.md'), link('docs/operations/production-extensibility.md')],
            'Proposed design; not implemented.'))

# 10 ─────────────────────────────────────────────────────────────────────────────
page('traffic', 'Operations', 'Handling traffic changes',
    table('Scraping never runs on a page view. All representatives share one stored copy. These are triggers, not load-test results.', ['Change', 'Effect', 'Response', 'Trigger to act'], [
        ('More reps / page views', 'More API reads', 'Scale Flask and Next.js out; size database pools; cache counts', 'Measured latency or CPU'),
        ('More saved leads', 'Python filters slow down', 'Move lead filters and counts to SQL with indexes', 'List time grows with leads'),
        ('Large prospect lists', 'Offset paging slows', 'Keyset (cursor) pagination', 'Deep pages slow'),
        ('More territories', 'More collection work', 'One queued job per territory; scale workers', 'Runs overlap or miss the 30-day limit'),
        ('Source rate limits / 403', 'Collection blocked', 'Back off, slow pacing, alert; never retry fast', '429 / 403 in run records'),
        ('Daytime peaks', 'Burst reads', 'Collect off-peak; reps read shared data', 'Peak latency'),
        ('Connection limits', 'Database refuses connections', 'Pool size × workers ≤ database limit; add PgBouncer', 'Connection errors'),
    ]),
    sources([ref('backend/app/db.py', needle='pool_size=5') + ' (pool 5 + 5 per worker)', link('backend/app/services.py'), link('backend/app/queries.py'), link('docs/operations/production-readiness.md')],
            'No load test was run and no traffic targets were set.'))

# 11 ─────────────────────────────────────────────────────────────────────────────
page('storage', 'Operations', 'Data storage policies',
    table('Public business contact data only, as GAF publishes it.', ['Policy', 'Rule', 'Status'], [
        ('What is stored', 'Business facts + retrieved_at; no raw HTML, no review text', 'Current'),
        ('What is not stored', 'Search rank, employee range, license number', 'Current'),
        ('Freshness', 'Data older than 30 days loses 5 points; refresh before then', 'Current rule'),
        ('Re-import', 'Updates GAF fields only; leads and statuses never change', 'Current'),
        ('Deletion', 'Nothing is deleted; Dismissed hides a lead', 'Current'),
        ('Removed listings', 'Mark inactive; keep the lead and its history', 'Proposed'),
        ('Secrets', 'Keys only in .env, outside git; none in the browser', 'Current'),
        ('Access', 'Login, lead ownership, territory access', 'Proposed'),
        ('Backups', 'Daily backups and a tested restore', 'Proposed'),
    ]),
    sources([link('backend/app/models.py'), ref('backend/app/collection/importer.py', needle='GAF_COLUMNS'), ref('backend/app/scoring.py', needle='FRESHNESS_DAYS'), link('.gitignore'), link('.env.example')],
            'The snapshot files are in the GitHub repository; check its visibility before sharing.'))

# 12 ─────────────────────────────────────────────────────────────────────────────
page('keep-all', 'Operations', 'Do we keep all leads or only high scores?',
    table('The score explains priority; it does not decide what is stored. Counts observed on 5 November 2026.', ['Table', 'What is kept', 'Detail'], [
        ('Prospects', 'All 409', 'Every GAF listing is stored, at every tier. Reps can still find any company by search or filter.'),
        ('Scores', 'All 409', 'High 197 · Medium 212 · Low 0. Low is empty because most listings are GAF certified.'),
        ('Leads', 'Rep\'s choice', 'Only prospects a rep saves, at any tier. One lead per company (36 companies are listed twice).'),
    ]),
    table('Policy questions.', ['Question', 'Answer'], [
        ('Why not drop low scores?', 'A low score often comes from Unknown fields (no website), not from a poor fit.'),
        ('Why not auto-save high scores?', '197 High prospects is too many to call; the rep decides.'),
        ('How is the list kept short?', 'Filters: tier, distance, directory, Hide saved; Dismissed status.'),
        ('Is anything deleted?', 'No. Filters and statuses hide rows; data stays for later review.'),
    ]),
    sources([link('backend/app/collection/importer.py'), ref('backend/app/services.py', 'save_prospect'), ref('backend/app/models.py', needle='uq_leads_company_key')], 'Counts observed on 5 November 2026.'))

# 13 ─────────────────────────────────────────────────────────────────────────────
page('database', 'Data model', 'Database model: three tables',
    diagram_table('Database relationships and key constraints. Each prospect has at most one score and at most one lead.', db),
    table('Columns and rules. PK = primary key. FK = foreign key to prospects.id. No notes, history or insight table is active.', ['Table', 'Column', 'Rule'], [
        (c('prospects'), 'id', 'PK'),
        (c('prospects'), 'directory + gaf_source_id', 'UNIQUE'),
        (c('prospects'), 'name, phone, phone_digits', 'phone_digits links directories'),
        (c('prospects'), 'website_url, address, city, state', 'May be Unknown'),
        (c('prospects'), 'distance_mi, rating, review_count', 'Numbers or Unknown'),
        (c('prospects'), 'distinctions[], specialties[]', 'Text arrays'),
        (c('prospects'), 'about_text, years_in_business', 'Shown, not scored'),
        (c('prospects'), 'retrieved_at', 'Freshness'),
        (c('prospect_scores'), 'prospect_id', 'PK + FK (1 : 0..1)'),
        (c('prospect_scores'), 'score', 'CHECK 0–100'),
        (c('prospect_scores'), 'breakdown', 'JSONB, 8 items'),
        (c('prospect_scores'), 'rule_version, scored_at', 'v1, effective time'),
        (c('leads'), 'id', 'PK'),
        (c('leads'), 'prospect_id', 'UNIQUE FK (1 : 0..1, saved as)'),
        (c('leads'), 'company_key', 'UNIQUE when present'),
        (c('leads'), 'status', 'CHECK 4 values'),
        (c('leads'), 'saved_at, status_changed_at', 'Follow-up clock'),
    ]),
    table('Why this split. D4 records the three-table ownership split.', ['Table / relationship', 'Why chosen', 'Alternative', 'Why not / current limitation'], [
        (c('prospects') + ' · source facts', 'Unique (directory, gaf_source_id) supports repeat-import upserts.', 'One wide source/score/work table', 'Mixes source refresh ownership with representative edits; user selected field-group separation (D4).'),
        (c('prospect_scores') + ' · 0..1 per prospect', 'PK/FK prospect_id stores score, JSONB breakdown, rule_version, scored_at.', 'Calculate on every GET', 'Adds request work and can change visible scores with time. Stored scores need explicit rescore to refresh freshness points; this trade-off is inferred.'),
        (c('leads') + ' · 0..1 per prospect', 'Unique prospect_id; status and timestamps remain independent of source updates.', 'saved flag directly on prospect', 'Less schema overhead, but source facts and user workflow share one row; D4 selected separate ownership.'),
        ('Company uniqueness', 'D8: unique non-null company_key uses normalized ten-digit phone.', 'Separate company table / authoritative company ID', 'No stable external company ID is available. Shared phones can merge distinct companies; missing keys permit separate saves.'),
    ]),
    sources([link('backend/app/models.py'), link('backend/app/db.py'), link('backend/app/collection/importer.py')], STD))

# 14 ─────────────────────────────────────────────────────────────────────────────
page('rules', 'Scoring', 'Scoring fields: what is used and why',
    table('Each point comes from one GAF field. Missing data gets 0 points and shows as Unknown. Saving or a status change never changes the score.', ['Field (column)', 'Rule', 'Points', 'Why'], [
        ('distance_mi', '≤10 mi 35 · ≤25 22 · ≤50 10 · unknown 0', '35', 'Delivery cost and rep travel'),
        ('distinctions', 'Top tier 20 · certified 12 · none 0', '20', 'Manufacturer program standing'),
        ('directory + specialties', 'Residential, or commercial technologies listed', '10', 'Matches our product lines'),
        ('specialties / distinctions', 'FORTIFIED, metal, solar or coatings', '5', 'Higher-value product topics'),
        ('phone', 'Listed', '10', 'Rep can call today'),
        ('website_url', 'Listed', '10', 'Rep can research the company'),
        ('address + city + state', 'All present', '5', 'Visit or deliver'),
        ('retrieved_at', '≤30 days old', '5', 'Facts are current'),
    ]),
    table('Shown or stored, but deliberately not scored.', ['Not scored', 'Why not'], [
        ('rating, review_count', 'Reputation; favors big review counts'),
        ('search rank', 'GAF\'s relevance, not our priority'),
        ('employee range', 'Self-stated, broad; not stored'),
        ('years_in_business', 'Sources conflict (1984 vs 1995)'),
        ('about_text', 'Free text; not verified'),
    ]),
    sub('business-rules', 'Tiers and business rules', table('D7–D9, D12, D13; comparisons are inferred where not explicitly recorded.', ['Rule / implementation', 'Why chosen', 'Alternative', 'Why not / limitation'], [
        ('Tiers: High ≥70; Medium 45–69; Low <45. Tie-break: score, distance, name, id.', 'Preserves missing-data meaning while keeping one deterministic total.', 'Impute missing values or treat them as known negatives', 'Can imply unsupported facts. Thresholds are business rules, not validated conversion probabilities.'),
        ('Fixed weights /100 (D7)', 'Explainable, repeatable ranking from GAF facts.', 'LLM ranking / learned sales model', 'LLM score is harder to reproduce; no labelled sales outcomes justify a learned model.'),
        ('Freshness ≤30 days; stored during import/rescore.', 'Makes effective time explicit in calculation.', 'Recompute every request / scheduled rescore', 'No scheduler is implemented. Stored freshness can age until rescore.'),
        ('New / Contacted / Qualified / Dismissed; any transition allowed.', 'D13: representatives can correct status mistakes.', 'Finite-state workflow with restricted transitions', 'No required stage-gating policy. Last-writer-wins edits have no version check or audit history.'),
        ('Follow-up: Contacted and unchanged for ≥14 days.', 'D12: uses the approved interval and existing timestamp.', 'Reminder date / last-contact event', 'Requires additional workflow/data. The timestamp measures status age, not verified call history.'),
        ('No unsave; Dismissed removes work from active lists.', 'D9: retain saved work.', 'Delete/unsave endpoint', 'Would discard the saved-work boundary. UI/API expose no such action.'),
    ])),
    sources([link('backend/app/scoring.py'), link('docs/DECISION_LOG.md', c('docs/DECISION_LOG.md') + ' (D7)'), link('docs/ARCHITECTURE_AND_DESIGN.md', c('docs/ARCHITECTURE_AND_DESIGN.md') + ' (section 7)')],
            'Weights were proposed in the design and approved by the user (D7). They are not calibrated against sales results.'))

# 15 ─────────────────────────────────────────────────────────────────────────────
page('ideal-customer-profile', 'Scoring', 'Ideal residential and commercial profiles',
    table('The same idea for both segments, with different signals. No prospect reaches 100 today.', ['Trait', 'Ideal residential contractor (100 pts)', 'Ideal commercial contractor (100 pts)'], [
        ('Territory', 'Within 10 mi of ZIP 10013', 'Within 10 mi of ZIP 10013'),
        ('Certification', 'GAF Master Elite® or President\'s Club', 'GAF PlatinumElite™ or Chairman\'s Circle'),
        ('Roof systems', 'Residential (steep-slope) directory', 'Technologies listed: single-ply, asphaltic'),
        ('Specialty', 'FORTIFIED Roof™, metal or solar specialty', 'Coatings &amp; Liquid Applied specialty'),
        ('Contact', 'Phone, website and full street address', 'Phone, website and full street address'),
        ('Freshness', 'Data read in the last 30 days', 'Data read in the last 30 days'),
        ('Best today', 'American Siding Construction Corp, Newark NJ, 6.5 mi, Master Elite: 95 (no specialty)', 'Tecta America Metro NY LLC, Belleville NJ, 8.8 mi, GoldElite + CoatingsPro: 92'),
    ]),
    table('Signals in the data, observed on 5 November 2026.', ['Signal', 'Residential (176)', 'Commercial (233)'], [
        ('Within 10 mi', '12', '50'),
        ('Top certification tier', '176', '16'),
        ('Specialty points', '14', '66'),
        ('No website on GAF', '81', '209'),
        ('High / Medium tier', '130 / 46', '67 / 166'),
        ('Average score · best score', '73 · 95', '66 · 92'),
    ]),
    table('Ideal profile by trait. D7 uses public GAF signals, not measured purchase intent.', ['Trait', 'Signal and points', 'Reason'], [
        ('Territory fit', 'Distance: 35', 'Delivery cost and representative travel.'),
        ('Product fit', 'Certification: 20; roof systems: 10; specialty: 5', 'Manufacturer standing and roof segment match.'),
        ('Contact readiness', 'Phone: 10; website: 10; address: 5; freshness: 5', 'A representative can act on reachable, recent information.'),
        ('Excluded', 'Ratings, reviews, search rank, size: 0', 'These do not establish buying need.'),
    ]),
    sources([link('backend/app/scoring.py'), 'SQL on ' + c('prospects') + ' and ' + c('prospect_scores') + ', 5 November 2026'], 'Counts and examples observed in the database on 5 November 2026.'))

# 16 ─────────────────────────────────────────────────────────────────────────────
api = [
    ('GET', '/health', 'API + database check', '—', '200 ' + c('{"status":"ok"}'), '500', 'Manual', 'health'),
    ('GET', '/overview', 'Pipeline counts, call lists', 'directory', '200 Overview', '422', 'Sales dashboard', 'overview'),
    ('GET', '/prospects', 'Search, filter, sort, page', 'q, directory, tier, max_distance, state, cert_tier, hide_saved, sort, page, page_size', '200 items/total/page', '422', 'Prospects', 'list_prospects'),
    ('GET', '/prospects/stats', 'KPI and chart counts', 'directory', '200 counts + retrieval time', '422', 'Prospects, sidebar', 'prospect_stats'),
    ('GET', '/prospects/{prospect_id}', 'Facts, score, Unknown fields', 'path id', '200 ProspectDetail', '404', 'Lead page', 'get_prospect'),
    ('POST', '/prospects/{prospect_id}/save', 'Save as lead', 'path id; no body', '201 created / 200 existing', '404, 409 company conflict', 'Save button', 'save_prospect'),
    ('GET', '/leads', 'Saved leads, work queues', 'scope, status, queue, directory, tier, sort, page, page_size, search','200 items + counts + matching total', '422', 'Saved leads', 'list_leads'),
    ('POST', '/leads/{lead_id}/status', 'Change status', c('{"status": "contacted"}'), '200 ProspectDetail', '404, 405 (PATCH), 422', 'Status control', 'update_status'),
]
page('api', 'API', 'API inventory: 8 endpoints under /api/v1',
    table('All eight application endpoints; no authentication. Six reads, two writes. Error shape: ' + c('{"error": {"code", "message", "details"}}') + '. 409 = company saved through its other listing. An empty query value, such as ' + c('?directory=') + ', means no filter (D20).',
          ['Endpoint', 'Purpose', 'Main input', 'Success', 'Errors', 'Caller', 'Handler'],
          [(f'<strong>{m}</strong> ' + c('/api/v1' + p), why, i, ok, err, caller, ref('backend/app/api/__init__.py', fn)) for m, p, why, i, ok, err, caller, fn in api]),
    sources([link('backend/app/api/__init__.py'), link('backend/app/schemas.py'), link('openapi.yaml'), link('frontend/lib/api-types.ts')],
            'PATCH on the status route returns 405 since decision D25. Health has no page caller. ' + STD))

# 17 ─────────────────────────────────────────────────────────────────────────────
page('frontend', 'Frontend', 'Frontend behavior',
    table('Current UI implementation; alternative comparisons are inferred.', ['Concern', 'Current approach / why', 'Alternative', 'Why not / trade-off'], [
        ('Views', 'Sales dashboard, Prospects, Prospect details, Saved leads.', 'One large dashboard containing every detail', 'Harder to scan; separate routes isolate list and detail work.'),
        ('Filter state', 'Filters, sort and page live in the URL query, so the Back button and shared links keep them. Sales dashboard links carry the directory.', 'Redux/global store or local-only state', 'No distant-state need justifies another store; local-only filters are not shareable.'),
        ('Async reads', 'useLoad: abort the old request + sequence guard; keep prior results during refresh.', 'Uncontrolled fetch effects / query library', 'Old answers could replace new results. A query library adds a dependency beyond current needs.'),
        ('Writes', 'Save button disabled while pending. The status control shows the new value at once and restores the old value if the save fails. Pages reload from the server after a write.', 'Optimistic updates without server reconciliation', 'Can show unsaved work or stale counts after errors.'),
        ('Mark contacted', 'One-click status change on the Sales dashboard Call next list and on the lead page for New leads; not in the Saved leads table (D23).', 'A button on every table row', 'The user removed it from the table (D23).'),
        ('Errors', 'Clear action messages; network failure text replaced (F5).', 'Show the raw browser error', 'Raw "Failed to fetch" confuses users.'),
        ('Directory toggle', 'All / Residential / Commercial on three views.', 'Separate pages per segment', 'Duplicates views and navigation.'),
        ('Narrow screens', 'Lead cards below 768 px; wrapping navigation (F7).', 'Force the wide table onto phones / Kanban', 'Sideways scrolling on phones; no drag-and-drop stage workflow is required.'),
        ('Accessibility', 'Labels, aria-pressed, aria-sort, focus rings, text plus color.', 'Color-only status', 'Fails users who cannot tell colors apart.'),
    ]),
    sources([link('frontend/app/page.tsx'), link('frontend/app/prospects/page.tsx'), link('frontend/app/prospects/[id]/page.tsx'), link('frontend/app/leads/page.tsx'), link('frontend/lib/useLoad.ts'), link('frontend/lib/api.ts')], STD))

# 18 ─────────────────────────────────────────────────────────────────────────────
page('dashboard-metrics', 'Frontend', 'Sales dashboard: what each number means',
    table('Counts are current-state metrics, not a historical funnel. The directory toggle applies first. No status history is kept, so trends over time are not available.', ['Metric', 'Calculation', 'Meaning / limit'], [
        ('Saved leads', 'New + Contacted + Qualified', 'Dismissed not counted.'),
        ('Not contacted yet', 'Status New', 'Call these first. No independent call history.'),
        ('Contacted (%)', '(Contacted + Qualified) ÷ saved leads, rounded to a whole percent; zero when there are no saved leads', 'Coverage now, not a conversion rate.'),
        ('Qualified', 'Status Qualified', 'Worth an account plan.'),
        ('Follow-up due', 'Contacted and no change for ≥14 days', 'Setting the same status again does not reset it. Not a scheduled task date.'),
        ('Top prospects not saved', 'High score, no lead for the company', 'Next companies to review.'),
        ('Matching leads', 'After table filters', 'Status cards show all saved leads in the directory; do not calculate counts from the current page.'),
        ('"Saved leads" outside the dashboard', 'Sidebar badge and Prospects card: all leads, including Dismissed (' + ref('backend/app/services.py', 'prospect_stats') + ')', 'The same label means two counts: the dashboard card excludes Dismissed; these include it.'),
    ]),
    sources([link('backend/app/services.py'), link('backend/app/queries.py'), link('frontend/app/page.tsx'), link('frontend/app/leads/page.tsx')], STD))

# 19 ─────────────────────────────────────────────────────────────────────────────
page('reliability', 'Quality', 'Reliability: what is protected and where the limits are',
    table('Constraints and transactions give specific protections, not a full production guarantee.', ['Area', 'Current choice / why', 'Alternative', 'Limit / trigger'], [
        ('Duplicate leads', 'Unique keys + rollback; 8 parallel saves → 1 lead.', 'Check in the UI', 'UI checks race between clients. Shared or missing phones still need policy.'),
        ('Duplicate prospects', 'Upsert on directory + GAF ID; reimports keep representative work.', 'Delete and reload', 'Reload would lose links to leads.'),
        ('Schema', 'create_all with a PostgreSQL advisory lock (D5: migrations excluded from the MVP).', 'Alembic', 'Cannot change existing columns; add migrations before data-preserving schema changes.'),
        ('Saved-lead queries', 'D19: directory filter in SQL. Other filters and sorting run in Python, because the saved set is small (code comment in ' + ref('backend/app/queries.py') + ').', 'All in SQL', 'Move when measured row count, memory or latency grows.'),
        ('Import', 'Upsert, then score, in separate commits.', 'One staged publish', 'Partial state is possible: a rescore failure can leave rows without scores.'),
        ('Slow work', 'No jobs, no cache, no status history.', 'Durable jobs, cache, event history', 'Add each only for a real workload or approved audit need.'),
        ('Connections', 'Pool 5 + 5 per worker (2 workers).', 'PgBouncer', 'Not a measured capacity.'),
    ]),
    sources([link('backend/app/db.py'), link('backend/app/models.py'), link('backend/app/collection/importer.py'), link('backend/app/services.py')], STD))

# 20 ─────────────────────────────────────────────────────────────────────────────
page('extensibility', 'Future', 'Production roadmap in three stages',
    table('Stages: 1 · Reliable data refresh. 2 · Safe database changes. 3 · AI insights as a separate workflow. Proposed work.', ['Area', 'Current code', 'Production extension'], [
        ('Collection pipeline', ref('backend/app/collection/importer.py', 'import_file') + ' reads the two recorded GAF JSON files. No live collection job.', 'Approved feed or access method; a source reader that produces validated records. import_file() calls load_snapshot() directly, so it needs a reader interface first.'),
        ('Refresh and recovery', 'CLI imports source rows, then scores imported prospects, in separate commits.', 'Scheduled refresh with a run ID, completion checks, retry rules and alerts. Stage and publish a complete run together, so new facts never pair with old scores. Keep lead status on every refresh.'),
        ('Database', 'Three tables: source facts, stored scores, saved work. ' + ref('backend/app/db.py', 'init_db') + ' uses create_all().', 'Versioned migrations (Alembic) before changing live tables; backups and a tested restore; move saved-lead filters and counts to SQL when volume needs it.'),
        ('AI insights', link('additional/insights/') + ' is a disconnected, untested draft with a process-local thread pool.', 'Save the lead first, enqueue an idempotent insight job, and store generating / ready / failed / stale in a lead_insights table. A durable worker retries after a restart without duplicate work.'),
    ]),
    sub('production-database', 'Database and query path', table('Change the schema before real data needs upgrading; scale queries only after measuring them.', ['Change', 'Code boundary', 'Why / proof needed'], [
        ('Versioned migrations + recovery', 'db.py, models.py, new migration files', 'create_all creates missing tables but cannot upgrade existing columns. Test an upgrade and a backup restore before production use.'),
        ('Ownership and uniqueness', 'leads, services.py, queries.py', 'Define whether company uniqueness applies per representative or territory; then migrate the unique key and prove users cannot read or edit each other\'s leads.'),
        ('SQL filtering and indexes', 'services.list_leads, services.overview, queries.py', 'Move Python filtering/counting to SQL after measured row, memory or latency growth. Keep total counts distinct from visible-page counts.'),
    ])),
    sub('production-llm', 'LLM research and insight jobs', table('The disconnected additional/insights draft has not run or been tested. It must stay separate from deterministic scoring.', ['Change', 'Code boundary', 'Why / proof needed'], [
        ('Durable insight job', 'additional/insights/service.py; proposed lead_insights table', 'Save the lead first. Enqueue an idempotent job with generating, ready, failed and stale states. A process-local thread pool cannot recover work after a worker restart.'),
        ('Safe page fetch', 'additional/insights/website.py', 'Check resolved addresses and each redirect, restrict domains/response size, and respect robots and approved data access. Redirects currently follow without destination checks.'),
        ('Grounded output', 'additional/insights/generator.py', 'Validate each claim against a source passage. A URL in the input alone does not prove the claim. Treat page text as untrusted and review generated advice before use.'),
        ('Control cost and change', 'proposed job records and monitoring', 'Version model/prompt/schema, bound tokens and retries, record cost, latency and failures. AI never changes the rule-based priority score.'),
    ])),
    sources([ref('backend/app/collection/importer.py', 'import_file'), ref('backend/app/db.py', 'init_db'), link('additional/insights/README.md'), link('docs/operations/production-readiness.md')],
            'Proposed work. Alembic supports ordered schema upgrades; create_all() does not.'))

# 21 ─────────────────────────────────────────────────────────────────────────────
page('scheduled-collection', 'Future', 'From JSON snapshots to scheduled collection',
    table('Path from today to production. In every option, the run is recorded and alerts fire on partial runs.', ['Stage', 'State'], [
        ('Today', '2 JSON files in data/snapshot, collected once. ' + c('flask import-snapshot') + ' loads them.'),
        ('Next', 'A collector job writes the same record shape; importer and scoring stay the same.'),
        ('Then', 'Every run recorded (collection_runs); alert on partial runs or count drops.'),
    ]),
    table('Scheduling options. Proposed; none is implemented. The choice depends on the hosting platform and the number of territories.', ['Option', 'How it runs', 'Good for', 'Limits'], [
        ('Host cron', 'cron runs the collector, then flask import-snapshot', 'One server; simplest start', 'No retries or run history unless added'),
        ('Container schedule', 'Kubernetes CronJob or ECS scheduled task', 'Teams already on Kubernetes or AWS', 'Needs the platform; same run-record work'),
        ('Managed scheduler', 'EventBridge / Cloud Scheduler → Lambda or Cloud Run job', 'Low operations', 'Run-time limits; cold starts'),
        ('Queue + workers', 'Celery beat / RQ enqueue one job per territory; workers retry', 'Many territories; retries; pacing', 'Needs a broker (Redis) and monitoring'),
        ('Orchestrator', 'Airflow / Dagster / Prefect: collect → validate → upsert → score → alert', 'Multi-step pipelines, backfills, lineage', 'Heavy for a single job'),
        ('CI schedule', 'GitHub Actions on a cron trigger', 'Demos and prototypes', 'Not for production data or secrets'),
    ]),
    sources([link('data/snapshot/', c('data/snapshot/*.json')), link('backend/app/cli.py'), link('backend/app/collection/importer.py'), link('docs/operations/production-extensibility.md')],
            'Proposed options; none is implemented.'))

# 22 ─────────────────────────────────────────────────────────────────────────────
page('lead-events', 'Future', 'Tracking rep and AI insights: an append-only table',
    table('Proposed ' + c('lead_events') + ' table; not implemented. Notes and AI insights are deferred (D10, D11).', ['Column', 'Type', 'Meaning'], [
        ('id', 'bigint PK', 'Event identity'),
        ('lead_id', 'FK → leads.id', 'Which lead'),
        ('event_type', 'status_change · rep_note · call · ai_insight', 'What happened'),
        ('actor_type, actor_id', 'rep · system · model; rep id or model + version', 'Who wrote it'),
        ('payload', 'JSONB', 'Status from/to, note text, insight + source URLs'),
        ('supersedes_id', 'FK → lead_events.id, nullable', 'Correction of an earlier row'),
        ('created_at', 'timestamptz, default now()', 'Time order'),
    ]),
    table('Append-only rules and what they enable.', ['Append-only rule', 'What it enables'], [
        ('App role has INSERT and SELECT only, no UPDATE or DELETE', 'Full history: who changed what, and when'),
        ('A trigger rejects UPDATE and DELETE as a second guard', 'Trends: contacts per week, time to qualify'),
        ('Index (lead_id, created_at) for the lead timeline', 'Compare AI insights with rep notes'),
        ('Latest insight per lead = newest ai_insight row', 'Safe retries: an insight job adds a row once (idempotency key)'),
        ('Corrections are new rows with supersedes_id', 'Audit trail for disputes and manager reviews'),
        ('Status change: event row + leads.status in one transaction', 'Training data to calibrate the score later'),
    ]),
    table('Illustrative example timeline for one lead, from the slide. Not real data.', ['Date', 'event_type', 'Payload', 'Actor'], [
        ('Nov 5', 'status_change', 'New → Contacted', 'rep 12'),
        ('Nov 5', 'call', '"Uses GAF Timberline; buys from a competitor"', 'rep 12'),
        ('Nov 6', 'ai_insight', 'Brief with 3 cited sources', 'model + version'),
        ('Nov 6', 'rep_note (supersedes)', 'Correction: "buys monthly, not weekly"', 'rep 12'),
        ('Nov 20', 'status_change', 'Contacted → Qualified', 'rep 12'),
    ]),
    table('Costs of the design.', ['Trade-off', 'Needed control'], [
        ('The table grows forever', 'A retention rule'),
        ('Notes may hold personal data', 'Access control'),
    ]),
    sources([link('backend/app/models.py'), ref('backend/app/services.py', 'update_status'), link('additional/insights/README.md'), link('docs/operations/production-extensibility.md')],
            'Proposed design; not implemented.'))

# 23 ─────────────────────────────────────────────────────────────────────────────
page('capabilities', 'Future', 'More future capabilities',
    table('Each capability builds on the same data model and needs a prerequisite before it is safe to build.', ['Capability', 'Value for a representative', 'Needs first'], [
        ('Notes and call log', 'Remember every conversation', 'lead_events append-only table'),
        ('AI account brief', 'Faster call preparation, with cited sources', 'Durable jobs, source checks, cost limits'),
        ('Follow-up reminders', 'No missed follow-ups (email or Slack)', 'Rep identity, notification service'),
        ('CRM sync (Salesforce, HubSpot)', 'One system of record', 'Ownership mapping, duplicate rules'),
        ('Territory assignment', 'Fair split of prospects between reps', 'Login, territory table'),
        ('Website enrichment', 'Fill 290 missing websites, find contacts', 'Approved enrichment source'),
        ('Map and route view', 'Plan visits by area', 'Geocoding of addresses'),
        ('Score calibration', 'Ranking that matches won accounts', 'Outcome data; new rule version'),
        ('CSV export', 'Share a filtered list with a manager', 'Access control, export audit'),
    ]),
    sources([link('docs/operations/production-extensibility.md'), link('docs/DECISION_LOG.md')], 'Proposals for discussion; none is implemented or approved.'))

# 24 ─────────────────────────────────────────────────────────────────────────────
page('future', 'Future', 'Rollout order',
    table('Suggested order, steps 1–6; proposals do not change the approved application scope. No traffic target, SLO or load capacity has been measured.', ['When', 'Work', 'Done when', 'Why not build it now'], [
        ('1 · Before release', 'Run the 107 tests in CI with a throwaway database', 'Every change runs API, UI and persistence checks', 'Tests run locally under D22; CI is separate work.'),
        ('2 · Before external users', 'Login, TLS, secret manager, backups, Alembic migrations', 'Authorized access; tested restore and upgrade', 'Local Compose and a named volume are not production access control or a backup plan.'),
        ('3 · Before shared editing', 'Lead ownership; version check on status updates', 'No silent overwrite of another rep\'s work', 'The app has one shared workspace and no version/history model.'),
        ('4 · With the data team', 'Approved data source; scheduled refresh; run alerts', 'Fresh data without a person\'s browser', 'Needs approved access first (page 9).'),
        ('5 · With sales results', 'Calibrate score weights (new rule version)', 'Scores separate won accounts better', 'No outcome data exists yet.'),
        ('6 · After measured growth', 'SQL aggregates, indexes, cursor paging, pool sizing', 'Measured latency and connection need met', 'Complexity is not justified by possible future scale alone.'),
    ]),
    sources([link('docs/operations/production-readiness.md'), link('docs/TEST_RESULTS.md')], STD))

# 25 ─────────────────────────────────────────────────────────────────────────────
page('test-strategy', 'Verification', 'Test strategy: what kinds of tests were run',
    table('The 107 tests grouped by the kind of risk they cover. Tests run against the demo database but create and delete only marker rows (D22).', ['Test type', 'What it checks', 'Examples from the suite'], [
        ('Happy path', 'Normal use works end to end', '8 valid GETs match openapi.yaml; save → 201; status change; full browser flow'),
        ('Negative / validation', 'Bad input fails safely and changes nothing', '13 invalid queries → 422; malformed JSON; missing IDs → 404; PATCH → 405'),
        ('Boundary', 'Exact cut-off values', '10.0 / 10.1 / 25.0 / 25.1 / 50.0 mi; tiers 70 / 69 / 45 / 44; 30 days; 14 days ± 1 min'),
        ('Concurrency', 'Races between clients', '8 parallel saves → 1 lead; parallel saves across both listings → 1 lead'),
        ('Idempotency / import', 'Repeats do no harm', 'Re-import "0 new"; repeat save 200; invalid rows reported; status kept'),
        ('Consistency', 'Numbers equal the database', 'Dashboard and lead counts per directory; filter totals = SQL count'),
        ('Persistence', 'Data survives restarts', 'Lead and status after ' + c('docker compose restart backend')),
        ('Browser end-to-end', 'Real UI in Chromium', 'Search → details → save → status → dashboard → reload; directory toggle'),
        ('Failure and recovery', 'Errors are clear; retry works', 'Offline status change: message, old value back, retry saves; late response ignored'),
        ('Responsive / accessibility', 'Usable on phones and by keyboard', 'No sideways scroll at 390 px on 3 pages; keyboard-only save; labels'),
    ]),
    sources([link('docs/TEST_PLAN.md'), link('docs/TEST_RESULTS.md'), link('backend/tests/conftest.py'), link('backend/tests/e2e/test_browser.py')],
            'Tool split: pytest with the Flask test client, the CLI runner and requests to the running backend; Playwright with Chromium for the browser.'))

# 26 ─────────────────────────────────────────────────────────────────────────────
page('test-results', 'Verification', 'Test results by area: 107 passing',
    table('Full suite on 5 November 2026, after PATCH was replaced by POST: 107 passed, 0 failed, about 21 s.', ['Category', 'Tests', 'What it proves'], [
        ('Scoring', '36', 'Hand-calculated totals; cutoffs 10/25/50 mi; tiers 70/69/45/44; 30-day freshness'),
        ('API contract / validation', '32', 'Responses match openapi.yaml; 422 shapes; 404; PATCH → 405'),
        ('Filters / pagination', '11', 'Every row matches; no repeats across pages; stable order'),
        ('Save / duplicates', '5', 'Repeat save 200; 8 parallel saves → 1 lead; twin listing 409'),
        ('Import', '4', 'Re-import 0 new; facts update, status kept; invalid rows reported'),
        ('Dashboard / follow-up', '8', 'Counts = database; 14-day boundary; no reset on same status'),
        ('Persistence', '1', 'Lead and status survive a backend restart'),
        ('Browser (Chromium)', '10', 'Full flow, double click, offline retry, keyboard, 390 px, toggle'),
        ('<strong>Total</strong>', '<strong>107</strong>', '0 failed. Afterwards 409 real prospects and the same two real leads remained.'),
    ]),
    sources([link('docs/TEST_RESULTS.md'), link('docs/TEST_PLAN.md'), link('backend/tests/'), link('docs/DECISION_LOG.md', c('docs/DECISION_LOG.md') + ' (D22)')],
            'Observed run: ' + c('cd backend && .venv/bin/pytest tests --browser chromium') + '. Chromium only. No load test, accessibility audit or CI. Not rerun for this documentation change.'))

# 27 ─────────────────────────────────────────────────────────────────────────────
page('test-findings', 'Verification', 'Testing: failures found and fixed',
    table('4 application bugs, 2 test bugs, 1 environment problem. All fixed; the full suite then passed: 106 tests, and 107 after D25 added the PATCH test.', ['#', 'Failure', 'Root cause', 'User impact', 'Fix', 'Kind'], [
        ('F1', 'max_distance=25 returned 422', 'Literal[10,25,50] did not convert query text', 'Distance filter never worked', 'Integer + allowed-value check', 'App'),
        ('F2', 'Save returned lead: null', 'Session kept the old prospect object', 'Save button stayed on the lead page', c('expire_all()') + ' after commit', 'App'),
        ('F3', 'ResourceClosedError', 'Test helper read rows from an UPDATE', 'None', 'Fixed helper', 'Test'),
        ('F4', 'Restart test failed', 'Container ran code from before F2', 'None', 'Rebuilt container', 'Setup'),
        ('F5', '"Failed to fetch" shown', 'Network error passed to the UI', 'Browser jargon on errors', 'Clear fallback message', 'App'),
        ('F6', 'Two "Search" elements', 'Filter chip label also said Search', 'None', 'Searchbox role locator', 'Test'),
        ('F7', 'Page wider than 390 px', 'Nav/toggle did not wrap; hidden label escaped', 'Sideways scrolling (522 px)', 'Wrap; contain label', 'App'),
    ]),
    sources([link('docs/TEST_RESULTS.md', c('docs/TEST_RESULTS.md') + ' (section 3)'), link('backend/app/schemas.py'), link('backend/app/services.py'), link('frontend/lib/api.ts'), link('frontend/components/ui/layout/Sidebar.tsx')], STD))

# 28 ─────────────────────────────────────────────────────────────────────────────
references = [
    ('backend/app/models.py', 'Tables, constraints, relationships'), ('backend/app/scoring.py', 'Priority rules'),
    ('backend/app/services.py', 'Workflow and queue logic'), ('backend/app/queries.py', 'SQL filtering and aggregates'),
    ('backend/app/api/__init__.py', 'Route handlers'), ('backend/app/schemas.py', 'Validation / response types'),
    ('openapi.yaml', 'API contract'), ('frontend/app/leads/page.tsx', 'Saved-lead UI'),
    ('docs/DECISION_LOG.md', 'Recorded choices'), ('docs/TEST_PLAN.md', 'Coverage plan and execution status'), ('docs/TEST_RESULTS.md', 'Recorded 107-pass run, fixes, and limits'),
    ('docs/operations/production-extensibility.md', 'Extension proposals'), ('docs/operations/production-readiness.md', 'Production handoff'), ('additional/insights/README.md', 'Disconnected LLM draft'),
    (DECK, 'Slide deck that sets the page order'), ('docs/PRODUCT_EVOLUTION.html', 'Detailed change history'),
]
page('verification', 'Verification', 'What the evidence supports',
    table('A local test run and document checks do not prove production readiness.', ['Evidence', 'Supports', 'Still open'], [
        ('107-test run (5 November 2026)', 'API, database and Chromium behavior on real data', 'Other browsers; long outages'),
        ('Import reports', '176 / 176 and 233 / 233 complete; re-import 0 new', 'Data freshness after 30 days'),
        ('Manual checks', 'Restart persistence, 405 for PATCH, directory counts', 'Backups and restore'),
        ('Frontend compile checks', 'Types and production bundle compile', 'Not proof of behavior'),
        ('MVP boundary', 'One shared local workspace', 'Login, ownership, load targets'),
        ('Deck checks', 'Rendered slides; package and layout checks', 'Not opened in PowerPoint'),
        ('This walkthrough', 'Build-time check that each cited function, class, text and path exists; HTML integrity and Chromium render checks at desktop and 390 px', 'Not a test of application behavior'),
    ]),
    sub('source-references', 'Source references', table('Main repository sources.', ['File', 'Responsibility'], [(link(p), label) for p, label in references])),
    sources([link('docs/TEST_RESULTS.md'), link('docs/operations/production-readiness.md'), link('docs/BUILD_PROGRESS.md')], STD))

# ── Assemble ────────────────────────────────────────────────────────────────────
N = len(pages)
groups = []
for i, p in enumerate(pages, 1):
    p['n'] = i
    if not groups or groups[-1][0] != p['group']:
        groups.append((p['group'], []))
    groups[-1][1].append(p)


def label(p):
    return f"{p['n']:02} · {escape(p['title'])}"


options = ''.join(f'<optgroup label="{escape(g)}">' + ''.join(f'<option value="{p["key"]}">{label(p)}</option>' for p in ps) + '</optgroup>' for g, ps in groups)
contents = ''.join(f'<li><span class="group">{escape(g)}</span><ol>' + ''.join(f'<li value="{p["n"]}"><a href="#{p["key"]}">{escape(p["title"])}</a></li>' for p in ps) + '</ol></li>' for g, ps in groups)

body = []
for i, p in enumerate(pages):
    prev_p = pages[i - 1] if i else None
    next_p = pages[i + 1] if i + 1 < N else None
    pager = ('<nav class="pager" aria-label="Page ' + str(p['n']) + ' navigation">'
             + (f'<a class="prev" href="#{prev_p["key"]}" rel="prev"><span>← Previous</span>{label(prev_p)}</a>' if prev_p else '<span></span>')
             + (f'<a class="next" href="#{next_p["key"]}" rel="next"><span>Next →</span>{label(next_p)}</a>' if next_p else '<span></span>')
             + '</nav>')
    body.append(f'<section class="page" id="{p["key"]}" aria-labelledby="{p["key"]}-title">'
                f'<p class="eyebrow">{escape(p["group"])} · Page {p["n"]} of {N} · Slide {p["n"]}</p>'
                f'<h2 id="{p["key"]}-title" tabindex="-1"><span class="num">{p["n"]:02}</span>{escape(p["title"])}</h2>'
                + p['body'] + pager + '</section>')

css = '''
:root{color-scheme:dark;--bg:#0B1220;--panel:#101C2D;--soft:#17263B;--ink:#E4EDF8;--muted:#A9BBD0;--line:#31445A;--blue:#80BFFF;--green:#70DBB0}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:radial-gradient(ellipse 900px 420px at 15% -5%,#19345C 0%,transparent 70%),var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1280px;margin:auto;padding:34px 26px 68px}
header{padding:20px 0 22px;border-bottom:1px solid var(--line)}
h1{font-size:clamp(2.2rem,4.7vw,3.5rem);line-height:1.1;margin:0 0 20px;letter-spacing:-.035em;color:#F2F7FF}
h2{font-size:1.55rem;line-height:1.2;margin:0 0 15px;color:#F2F7FF}
h3{font-size:1.15rem;color:var(--blue);margin:28px 0 10px}
h2:focus,h3:focus{outline:none}
.page{border-top:1px solid var(--line);margin-top:30px;padding-top:27px;scroll-margin-top:84px}
.page h3{scroll-margin-top:84px}
.eyebrow{margin:0 0 6px;color:var(--green);font-size:.78rem;font-weight:700;letter-spacing:.11em;text-transform:uppercase}
a{color:var(--blue);text-underline-offset:3px}a:hover{color:#B8DDFF}
a:focus-visible,summary:focus-visible,.scroll:focus-visible,button:focus-visible,select:focus-visible{outline:3px solid var(--blue);outline-offset:3px}
code{font:0.88em/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere;color:#B5DBFF}
.scroll{overflow:auto;margin:13px 0 20px;border-radius:8px}
table{border-collapse:collapse;width:100%;min-width:760px;table-layout:auto;background:var(--panel)}
caption{text-align:left;color:var(--muted);font-size:.87rem;padding:0 0 10px;max-width:min(105ch,calc(100vw - 28px));background:var(--bg)}
th,td{border:1px solid var(--line);padding:12px 13px;text-align:left;vertical-align:top;overflow-wrap:break-word}
th{background:var(--soft);color:#F2F7FF;font-weight:650}
tbody tr:nth-child(even){background:#0E192A}
.meta table{min-width:0}.meta td:first-child{width:130px}.meta td{font-size:.86rem;padding:8px 10px}
.figure-table{min-width:0}.figure-table td{padding:0;font-weight:400}.figure-table .diagram{border:0;margin:0}
.diagram{overflow:auto;border:1px solid var(--line);border-radius:7px;margin:16px 0;background:var(--bg)}
.diagram svg{width:100%;height:auto;min-width:760px;display:block}
.num{color:var(--green);font-size:.76em;margin-right:12px;font-variant-numeric:tabular-nums}
.toolbar{display:none}
.js .toolbar{display:flex;position:sticky;top:0;z-index:5;flex-wrap:wrap;align-items:center;gap:8px 10px;margin:18px -10px 0;padding:10px;background:rgba(11,18,32,.94);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.toolbar button,.toolbar select{font:inherit;color:var(--ink);background:var(--soft);border:1px solid var(--line);border-radius:7px;padding:7px 12px;min-height:38px}
.toolbar button{cursor:pointer}.toolbar button:hover{border-color:var(--blue)}
.toolbar button:disabled{opacity:.45;cursor:default}
.toolbar select{flex:1 1 260px;max-width:520px;min-width:0;text-overflow:ellipsis}
.toolbar .count{color:var(--muted);font-size:.88rem;font-variant-numeric:tabular-nums}
.toolbar #all{margin-left:auto}
.toolbar #all[aria-pressed="true"]{background:#173B64;border-color:var(--blue)}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.contents{margin-top:20px}.contents summary{font-weight:650;cursor:pointer}
.contents>ol{columns:3 260px;column-gap:28px;padding-left:0;list-style:none;margin:14px 0 0}
.contents>ol>li{break-inside:avoid;margin:0 0 12px}
.contents .group{display:block;color:var(--green);font-size:.76rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase}
.contents ol ol{margin:4px 0 0;padding-left:30px}.contents ol ol li{margin:2px 0;font-size:.92rem}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:30px}
.pager a{display:block;padding:12px 14px;border:1px solid var(--line);border-radius:8px;background:var(--panel);text-decoration:none;font-size:.92rem}
.pager a span{display:block;color:var(--muted);font-size:.8rem;margin-bottom:2px}
.pager .next{text-align:right;grid-column:2}
@media(max-width:650px){main{padding:20px 14px 42px}th,td{padding:9px}h2{font-size:1.25rem}h3{font-size:1.06rem}.toolbar select{flex-basis:100%;max-width:none;order:-1}.toolbar .count{display:none}.page,.page h3{scroll-margin-top:118px}.pager{grid-template-columns:1fr}.pager .next{grid-column:1}}
@media print{body{background:#fff;color:#111}.toolbar,.pager,.contents{display:none!important}.page{display:block!important;break-before:page;border-color:#888}main{padding:0;max-width:none}table{min-width:0!important;font-size:10px;background:#fff}th,td{padding:5px;min-width:0!important;border-color:#999;color:#111}th{background:#eee}tbody tr:nth-child(even){background:#fafafa}.diagram svg{min-width:0}tr{break-inside:avoid}a,code,h1,h2,h3,.eyebrow{color:#111}}
'''

# Progressive enhancement: without JavaScript every page shows in order; with it, one page shows at a time.
js = '''
(function(){
var d=document,root=d.documentElement;root.classList.add('js');
var pages=[].slice.call(d.querySelectorAll('.page')),jump=d.getElementById('jump'),prev=d.getElementById('prev'),next=d.getElementById('next'),all=d.getElementById('all'),count=d.getElementById('count'),cur=0;
function find(hash){if(!hash||hash.length<2)return null;var el=d.getElementById(decodeURIComponent(hash.slice(1)));if(!el)return null;var p=el.closest('.page');return p?{i:pages.indexOf(p),el:el}:null;}
function render(){var showAll=root.classList.contains('all');pages.forEach(function(p,k){p.hidden=!showAll&&k!==cur;});jump.value=pages[cur].id;count.textContent='Page '+(cur+1)+' of '+pages.length;prev.disabled=cur===0;next.disabled=cur===pages.length-1;all.setAttribute('aria-pressed',showAll?'true':'false');all.textContent=showAll?'Show one page':'Show all pages';}
function open(hash,focus){var t=find(hash);if(!t)return false;cur=t.i;render();var el=t.el.classList.contains('page')?t.el.querySelector('h2'):t.el;if(focus){el.focus({preventScroll:true});}toTop(t.el);return true;}
function toTop(el){var bar=d.querySelector('.toolbar'),y=el.getBoundingClientRect().top+window.pageYOffset-(bar?bar.offsetHeight:0)-12;window.scrollTo({top:Math.max(0,y),behavior:'instant'});}
function go(i){i=Math.max(0,Math.min(pages.length-1,i));if(location.hash==='#'+pages[i].id){open(location.hash,true);}else{location.hash=pages[i].id;}}
window.addEventListener('hashchange',function(){open(location.hash,true);});
prev.addEventListener('click',function(){go(cur-1);});
next.addEventListener('click',function(){go(cur+1);});
jump.addEventListener('change',function(){go(pages.map(function(p){return p.id;}).indexOf(jump.value));});
all.addEventListener('click',function(){root.classList.toggle('all');render();toTop(pages[cur]);});
d.addEventListener('keydown',function(e){if(e.altKey||e.ctrlKey||e.metaKey||e.shiftKey||root.classList.contains('all'))return;var t=e.target.tagName;if(t==='INPUT'||t==='SELECT'||t==='TEXTAREA'||e.target.isContentEditable)return;if(e.key==='ArrowRight'&&cur<pages.length-1){e.preventDefault();go(cur+1);}else if(e.key==='ArrowLeft'&&cur>0){e.preventDefault();go(cur-1);}});
if(!open(location.hash,false)){render();}
})();
'''

date = datetime.now().astimezone().strftime('%d %B %Y, %H:%M %Z')
metadata = '<div class="meta">' + table('', ['Reference', 'Status'], [
    ('Updated', date),
    ('Format', f'{N} pages in the order of the {N}-slide deck ' + link(DECK) + '. One page shows at a time; use Previous / Next, the page list or the arrow keys. "Show all pages" restores one long page for search and print.'),
    ('Decision evidence', 'Recorded choices are attributed by ID. Unrecorded alternative comparisons are explicitly inferred. Future additions are proposals.'),
]) + '</div>'
toolbar = ('<div class="toolbar" role="toolbar" aria-label="Page controls">'
           '<button type="button" id="prev" aria-label="Previous page">← Previous</button>'
           '<label class="sr-only" for="jump">Go to page</label><select id="jump">' + options + '</select>'
           '<button type="button" id="next" aria-label="Next page">Next →</button>'
           '<span class="count" id="count" aria-live="polite"></span>'
           '<button type="button" id="all" aria-pressed="false">Show all pages</button></div>')
contents_html = f'<details class="contents"><summary>All {N} pages</summary><ol>{contents}</ol></details>'
html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Roofing Lead Intel · Technical walkthrough</title><style>' + css + '</style></head><body><main>'
        '<header><h1>Roofing Lead Intel</h1>' + metadata + contents_html + '</header>' + toolbar
        + ''.join(body) + '</main><script>' + js + '</script></body></html>')
target.write_text(html)
print('Updated:', target)
print('Pages:', N, 'Tables:', html.count('<table>'), 'Bytes:', len(html.encode()))
