from pathlib import Path
from datetime import datetime
from html import escape
import ast
import re

root=Path(__file__).resolve().parents[2]
target=root/'docs/CODE_WALKTHROUGH.html'
old=target.read_text()
archive=root/'docs/.walkthrough-build/archive/walkthrough-before-technical-tables.html'
if not archive.exists():archive.write_text(old)
svgs=re.findall(r'<svg\b.*?</svg>',old,re.S)
flow=next(s for s in svgs if 'id="request-flow"' in s)
db=next(s for s in svgs if 'id="db-model"' in s)

def c(value):return '<code>'+escape(value)+'</code>'
def link(path,label=None):return f'<a href="../{path}">{label or c(path)}</a>'
def table(caption,headers,rows):
    return '<div class="scroll" tabindex="0"><table><caption>'+caption+'</caption><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def ref(path,symbol=None,needle=None):
    text=(root/path).read_text();line=None
    if symbol:
        if path.endswith('.py'):
            line=next((n.lineno for n in ast.walk(ast.parse(text)) if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==symbol),None)
        else:
            line=next((i for i,s in enumerate(text.splitlines(),1) if re.search(r'\b(?:function|const)\s+'+re.escape(symbol)+r'\b',s)),None)
    elif needle:
        line=next((i for i,s in enumerate(text.splitlines(),1) if needle in s),None)
    if (symbol or needle) and line is None:raise ValueError(f'Missing source reference: {path}, {symbol or needle}')
    label=path+(f':{line}' if line else '')+(f' · {symbol}()' if symbol else '')
    return link(path,c(label))
def diagram_table(caption,svg):
    return '<div class="scroll"><table class="figure-table"><caption>'+caption+'</caption><thead><tr><th scope="col">Diagram</th></tr></thead><tbody><tr><td><div class="diagram">'+svg+'</div></td></tr></tbody></table></div>'
def subsection(key,title,content):return f'<h3 id="{key}">{title}</h3>'+content
parts=[];nav=[]
def section(key,title,body):
    n=len(parts)+1;nav.append((key,title))
    parts.append(f'<section id="{key}"><h2><span class="num">{n:02}</span>{title}</h2>{body}</section>')

section('project','Product and scope',table('Current MVP',['Item','Essential information'],[
 ('User / problem','Distributor sales representative selecting roofing contractors to contact and tracking saved work.'),
 ('Dataset','409 recorded GAF listings: 176 residential + 233 commercial. ZIP 10013, radius 50 miles. Snapshot data, not live search.'),
 ('Implemented','Search/filter/sort, explain priority, save a company, update status, first-contact and follow-up queues.'),
 ('Deferred','Notes and AI insights. No login, CRM sync, outreach automation, or per-representative ownership.'),
 ('Evidence labels','<strong>Recorded:</strong> rationale in the decision log. <strong>Inferred:</strong> technical comparison, not a claim that the author evaluated it. <strong>Proposed:</strong> future work, not implemented.'),
] ))

section('stack','Technology choices',table('Approved stack; rationale and alternative comparisons below are inferred unless a decision ID is cited',['Current choice','Why it fits','Current cost / limitation','Alternative','Why the alternative is not used here'],[
 ('Next.js + React + TypeScript','File-based routes, shared components, typed REST callers.','Separate frontend build; generated types do not validate HTTP at runtime.','Vite React SPA','Reason for the original selection is unrecorded. A SPA could work; changing frameworks adds migration work without a new MVP capability.'),
 ('Flask + Pydantic','Python services with explicit input/output schemas; thin blueprint handlers.','OpenAPI must be maintained separately.','FastAPI','Original rejection is unrecorded. Automatic OpenAPI is useful, but moving the existing Flask services/routes is not required for this MVP.'),
 ('PostgreSQL + SQLAlchemy 2','Foreign keys, transactions, JSONB breakdowns, partial unique indexes.','Requires a database service; PostgreSQL-specific types reduce portability.','SQLite / file-only storage','SQLite could suit one local user; the chosen SQL/constraint model supports concurrent writes. Files alone do not provide these relational guarantees.'),
 ('REST + OpenAPI + generated TS client','Explicit resource contracts and compile-time caller checks.','Routes, schemas, YAML, and generated types must stay aligned.','GraphQL / handwritten fetch types','No requirement for client-selected graph traversal. Handwritten types add another manual contract that can drift.'),
 ('Docker Compose','One local service definition; named database volume and service DNS.','Three containers and image builds add local overhead.','Host-installed processes / Kubernetes','Host processes require manual runtime/database setup. Kubernetes adds orchestration concerns without measured availability or scale requirements.'),
]))

section('requirements','Requirements',table('Observable behavior; implementation is not the same as test verification',['Type','Requirement','Current mechanism','Limit'],[
 ('Functional','Find relevant prospects','Directory/search/tier filters, SQL sorting, offset pagination.','The former distance-query coercion bug is fixed; regression coverage is recorded in TEST_RESULTS.md.'),
 ('Functional','Understand priority','Stored breakdown, rule version, Unknown fields.','No purchase-intent or revenue prediction.'),
 ('Functional','Track saved companies','Lead status, company-key uniqueness, work queues.','No contact log, notes, or owner isolation.'),
 ('Quality','Consistent results and safe writes','Deterministic rules, Pydantic validation, database constraints, commit/rollback.','Concurrency behavior needs automated coverage.'),
 ('Quality','Usable async interface','Pending states, error messages, sequence-guarded requests, responsive lead cards.','Browser accessibility and failure-path checks remain separate.'),
]))

section('flow','Architecture and data flow',diagram_table('System request path',flow)+table('Current execution paths; comparisons are inferred except snapshot choice D1',['Path','Implementation','Why this boundary','Alternative / trade-off'],[
 ('Data ingestion','GAF browser collection → JSON → CLI validation/upsert → stored scores.','D1: one-time collection avoids a runtime dependency on blocked GAF scraping.','Live API/feed: better freshness, but approved access and refresh policy are not available in the current implementation.'),
 ('Browser request','Typed client → same-origin /api/v1 → Next.js rewrite → Flask route → service/query → PostgreSQL.','D15: one browser origin avoids separate cross-origin configuration.','Direct browser-to-Flask calls: workable, but require explicit CORS and deployment-origin management.'),
 ('Save/status mutation','Validate → service write → commit → response → reconcile UI.','Commit defines persisted truth; UI pending/error state is not persistence.','Optimistic UI alone cannot enforce identity or recover an ambiguous commit.'),
 ('Service layout','Modular monolith: routes, services, queries, models.','Keeps HTTP, policy, and persistence responsibilities separate.','Microservices introduce distributed failures and deployment boundaries without a measured need.'),
]))

startup=table('Source-traced control flow, not an instrumented browser trace. Startup occurs when services launch, not every time a page opens.',['Phase','File / function','Control and result'],[
 ('Backend worker start',ref('backend/wsgi.py',needle='app = create_app()')+' → '+ref('backend/app/__init__.py','create_app'),'Gunicorn imports wsgi:app. create_app calls load_config, init_db, then registers session cleanup, JSON error handlers, /api/v1 blueprint, and CLI commands.'),
 ('Configuration / database',ref('backend/app/config.py','load_config')+' → '+ref('backend/app/db.py','init_db'),'Read environment configuration; create engine/session factory; acquire PostgreSQL advisory transaction lock; create missing tables. No snapshot import runs here.'),
 ('Initial app route',ref('frontend/app/layout.tsx','RootLayout')+' → '+ref('frontend/app/page.tsx','OverviewPage'),'Assume services already run. GET / selects the Overview page, not a redirect to Prospects. The shared layout includes Sidebar and page content.'),
])
first_open=table('A = Overview request; B = Sidebar badge request. A and B start independently after hydration. Rows describe dependencies within each branch, not one global network order.',['Step','File / function','Action / next call','Visible or database effect'],[
 ('1',ref('frontend/app/layout.tsx','RootLayout')+'; '+ref('frontend/app/page.tsx','OverviewPage'),'Next.js serves the page shell. React hydrates the client components; OverviewPage renders OverviewView inside Suspense.','Shared navigation and initial loading placeholders.'),
 ('2A',ref('frontend/app/page.tsx','OverviewView')+' → '+ref('frontend/app/page.tsx','load'),'useEffect calls load. Read optional directory from URL; api.GET("/overview", {directory}) is wrapped with unwrap.','Starts the main overview read; no writes.'),
 ('2B',ref('frontend/components/ui/layout/Sidebar.tsx','Sidebar'),'Its pathname-dependent useEffect independently calls api.GET("/prospects/stats") without a directory filter.','Starts an all-directory badge read; completion order relative to A is unspecified.'),
 ('3A / 3B',ref('frontend/lib/api.ts',needle='export const api')+' → '+ref('frontend/next.config.mjs',needle='async rewrites()'),'openapi-fetch requests /api/v1/overview or /api/v1/prospects/stats. Next.js forwards the URL to Flask.','Runtime HTTP boundary. The rewrite configuration is loaded by Next.js, compiled build/startup routing configuration, not a per-request application function.'),
 ('4A',ref('backend/app/api/__init__.py','overview')+' → '+ref('backend/app/schemas.py','DirectoryQuery')+'; '+ref('backend/app/db.py','get_session'),'Validate optional directory, obtain request-scoped session, call services.overview(session, directory).','Invalid query can return 422; valid input enters service logic.'),
 ('5A',ref('backend/app/services.py','overview')+' → '+ref('backend/app/queries.py','all_leads'),'Load saved leads with related prospects/scores; _lead_summary computes display fields and follow_up_due. Count statuses and build call/follow-up lists.','Reads PostgreSQL; computes current-state metrics.'),
 ('6A',ref('backend/app/queries.py','top_unsaved')+' → '+ref('backend/app/services.py','summarize_prospects')+' → '+ref('backend/app/queries.py','stats'),'Select high-priority unsaved prospects; summarize using twins then saved_leads_by_key. Read stats last for the overview retrieval timestamp.','Stored scores are read and formatted; no rescore or snapshot lookup.'),
 ('4B / 5B',ref('backend/app/api/__init__.py','prospect_stats')+' → '+ref('backend/app/services.py','prospect_stats'),'Validate DirectoryQuery; get_session; queries.stats → queries.all_leads → queries.count_high_unsaved.','Build ProspectStats. Sidebar will use only total and saved.'),
 ('7A / 7B',ref('backend/app/api/__init__.py','_json')+'; '+ref('backend/app/db.py','close_session'),'Pydantic model_dump(mode="json") → Flask jsonify → HTTP response through Next.js. Request teardown closes the database session.','Two independent JSON responses; no mutation.'),
 ('8A / 8B',ref('frontend/lib/api.ts','unwrap')+'; '+ref('frontend/app/page.tsx','load')+'; '+ref('frontend/components/ui/layout/Sidebar.tsx','Sidebar'),'A: unwrap returns Overview; load sets page data. B: Sidebar reads returned data directly and sets badge counts.','React renders KPIs/call lists and navigation badges independently. The initial Overview request does not use useLoad.'),
])
save_flow=table('Starts on an already-loaded Prospects list; the onSaved callback is the one attached to each list-row SaveButton.',['Step','File / function','Action / next call','State / persistence'],[
 ('0',ref('frontend/app/prospects/page.tsx','ProspectsView')+'; '+ref('frontend/lib/useLoad.ts','useLoad'),'Earlier GET /prospects supplied list.data.items. Each row renders SaveButton with prospectId, savedLeadId, savedVia, and an onSaved callback.','An existing savedLeadId renders Saved; savedVia renders a link rather than an active save button.'),
 ('1',ref('frontend/components/leads/SaveButton.tsx','save'),'Click invokes save(): setPending(true), clear the error, call api.POST("/prospects/{prospect_id}/save").','Button disables and shows Saving. No request body is needed.'),
 ('2',ref('frontend/lib/api.ts',needle='export const api')+' → '+ref('frontend/next.config.mjs',needle='async rewrites()'),'The typed client sends POST /api/v1/prospects/{id}/save; Next.js forwards it to Flask.','unwrap awaits the request; api-types.ts is not a runtime network step.'),
 ('3',ref('backend/app/api/__init__.py','save_prospect')+' → '+ref('backend/app/db.py','get_session'),'Flask integer path converter supplies prospect_id. Route calls services.save_prospect(session, prospect_id).','No Pydantic request-body model is involved in this bodyless endpoint.'),
 ('4',ref('backend/app/services.py','save_prospect')+' → '+ref('backend/app/queries.py','prospect_with_everything'),'Read prospect with joined score and lead. Missing prospect raises 404; existing lead returns existing detail with created=False.','No insert on missing/already-saved paths.'),
 ('5',ref('backend/app/services.py','save_prospect')+' → '+ref('backend/app/models.py','Lead'),'For an unsaved prospect, session.add(Lead(prospect_id=p.id, company_key=p.phone_digits, status="new")).','Pending ORM insert; not persisted until commit.'),
 ('6',ref('backend/app/services.py','save_prospect')+'; '+ref('backend/app/models.py','Lead'),'session.commit flushes INSERT. Unique prospect_id and the partial company_key unique index enforce identity.','Successful transaction persists one lead with New status and saved/status timestamps.'),
 ('7',ref('backend/app/services.py','save_prospect')+' → '+ref('backend/app/services.py','prospect_detail'),'After a successful new insert, session.expire_all invalidates loaded ORM state. prospect_detail reloads the prospect and new lead.','Important because expire_on_commit=False can otherwise retain the old lead=None relationship.'),
 ('8',ref('backend/app/services.py','prospect_detail')+' → '+ref('backend/app/queries.py','prospect_with_everything'),'Read joined row; twins → saved_leads_by_key; construct ProspectDetail with stored score, unknown fields, and LeadInfo.','No new score computation, provider call, note, or insight generation.'),
 ('9',ref('backend/app/api/__init__.py','save_prospect')+' → '+ref('backend/app/api/__init__.py','_json'),'created=True gives 201; created=False gives 200. Serialize ProspectDetail and return through Next.js.','Response identifies confirmed saved state.'),
 ('10',ref('frontend/lib/api.ts','unwrap')+' → '+ref('frontend/components/leads/SaveButton.tsx','save'),'unwrap returns detail; SaveButton calls onSaved(detail). finally resets pending.','On an error, catch sets the row-local error and finally re-enables the button.'),
 ('11',ref('frontend/app/prospects/page.tsx',needle='onSaved={() => { setMsg('),'The row callback sets the success message, calls list.reload(), and starts loadStats().','List and summary GETs can overlap; one response does not wait for the other.'),
 ('12A',ref('frontend/lib/useLoad.ts','run')+' → '+ref('backend/app/api/__init__.py','list_prospects')+' → '+ref('backend/app/services.py','list_prospects'),'GET /prospects keeps current filters. ProspectQuery → queries.prospect_page → summarize_prospects; useLoad accepts the latest result.','Row now shows Saved, or leaves the list when hide_saved=true.'),
 ('12B',ref('frontend/app/prospects/page.tsx','loadStats')+' → '+ref('backend/app/api/__init__.py','prospect_stats')+' → '+ref('backend/app/services.py','prospect_stats'),'GET /prospects/stats keeps selected directory; returned counts update page stats.','Prospects summary refreshes. No automatic navigation occurs.'),
])
branches=table('Branches and ordering limits are source-derived, not newly reproduced by a browser test.',['Case','File / control branch','Result'],[
 ('Competing / duplicate save',ref('backend/app/services.py','save_prospect'),'On IntegrityError: rollback → saved_leads_by_key. Different listing for the saved company returns 409 with alternate prospect/directory; same-prospect race can return existing detail/200.'),
 ('Server / network failure',ref('backend/app/errors.py','register_error_handlers')+'; '+ref('frontend/components/leads/SaveButton.tsx','save'),'Safe error JSON or failed fetch reaches unwrap/catch. UI error does not prove no commit occurred; retrying the same prospect is intended to recover the existing row.'),
 ('Sidebar after same-page save',ref('frontend/components/ui/layout/Sidebar.tsx','Sidebar'),'Sidebar effect depends on pathname. The Prospects save callback does not change pathname or invalidate sidebar state, so the sidebar badge can remain stale until navigation/remount.'),
 ('Not part of either runtime path',link('openapi.yaml')+'; '+link('frontend/lib/api-types.ts')+'; '+link('backend/app/cli.py'),'OpenAPI/type generation is build-time tooling. Import/rescore are explicit CLI operations. Opening the app or saving from Prospects does not read JSON snapshots, run scoring, or call GAF/AI providers.'),
])
control_index=table('Read each path in order; independent HTTP branches can complete in either order.',['Path','Entry point','Reading order'],[
    ('<a href="#startup-control">Service startup</a>','Gunicorn imports wsgi:app.','Configuration and database initialization occur before the browser paths below.'),
    ('<a href="#first-open-control">Initial opening</a>','GET / → RootLayout → OverviewPage.','Overview read (A) and Sidebar statistics read (B) run independently.'),
    ('<a href="#prospect-save-control">Save from Prospects</a>','List-row SaveButton → save().','Write transaction and response, then independent list/statistics refreshes.'),
])
section('control','File-by-file control flow',control_index+
    subsection('startup-control','Service startup and entry point',startup)+
    subsection('first-open-control','When the app first opens at /',first_open)+
    subsection('prospect-save-control','When Save as lead is clicked in Prospects',save_flow)+
    subsection('control-branches','Branches, refreshes, and excluded work',branches))

section('database','Database model',diagram_table('Database relationships and key constraints',db)+table('PK = primary key; FK = foreign key. Each child references prospects.id. D4 records the three-table ownership split.',['Table / relationship','Why chosen','Alternative','Why not / current limitation'],[
 (c('prospects')+' · source facts','Unique (directory, gaf_source_id) supports repeat-import upserts.','One wide source/score/work table','Mixes source refresh ownership with representative edits; user selected field-group separation (D4).'),
 (c('prospect_scores')+' · 0..1 per prospect','PK/FK prospect_id stores score, JSONB breakdown, rule_version, scored_at.','Calculate on every GET','Adds request work and can change visible scores with time. Stored scores need explicit rescore to refresh freshness points; this trade-off is inferred.'),
 (c('leads')+' · 0..1 per prospect','Unique prospect_id; status and timestamps remain independent of source updates.','saved flag directly on prospect','Less schema overhead, but source facts and user workflow share one row; D4 selected separate ownership.'),
 ('Company uniqueness','D8: unique non-null company_key uses normalized ten-digit phone.','Separate company table / authoritative company ID','No stable external company ID is available. Shared phones can merge distinct companies; missing keys permit separate saves.'),
]))

section('rules','Scoring and business rules',table('D7–D9/D12; comparisons are inferred where not explicitly recorded',['Rule / implementation','Why chosen','Alternative','Why not / limitation'],[
 ('Score /100: distance 35; certification 20; systems 10; specialty 5; phone 10; website 10; address 5; freshness 5.','D7: explainable, repeatable ranking from GAF facts.','LLM ranking / learned sales model','LLM score is harder to reproduce; no labelled sales outcomes justify a learned model. Ratings/reviews do not score.'),
 ('High ≥70; Medium 45–69; Low <45. Missing inputs score zero with an Unknown flag.','Preserves missing-data meaning while keeping one deterministic total.','Impute missing values or treat them as known negatives','Can imply unsupported facts. Thresholds are business rules, not validated conversion probabilities.'),
 ('Freshness ≤30 days; stored during import/rescore.','Makes effective time explicit in calculation.','Recompute every request / scheduled rescore','No scheduler is implemented. Stored freshness can age until rescore; future timestamps also need stricter validation.'),
 ('New / Contacted / Qualified / Dismissed; any transition allowed.','D13: representatives can correct status mistakes.','Finite-state workflow with restricted transitions','No required stage-gating policy. Current last-writer-wins edits have no version check or audit history.'),
 ('Follow-up: Contacted and unchanged for ≥14 days.','D12: uses the approved interval and existing timestamp.','Reminder date / last-contact event','Requires additional workflow/data. Current timestamp measures status age, not verified call history.'),
 ('No unsave; Dismissed removes work from active lists.','D9: retain saved work.','Delete/unsave endpoint','Would discard the saved-work boundary. UI/API currently expose no such action.'),
]))

api=[
 ('GET','/health','None','Database connectivity','200 '+c('{"status":"ok"}')),
 ('GET','/overview','Optional directory','Pipeline counts + call lists','200 Overview'),
 ('GET','/prospects','Search, directory, tier, distance, certification, sort, page','Filtered prospect list','200 items/total/page; 422 invalid query'),
 ('GET','/prospects/stats','Optional directory','KPI/chart aggregates','200 counts + retrieval time'),
 ('GET','/prospects/{prospect_id}','Path ID','Source facts, score, Unknown fields','200 ProspectDetail; 404 missing'),
 ('POST','/prospects/{prospect_id}/save','Path ID; no body','Insert a saved lead','201 created; 200 existing; 404 missing; 409 company conflict'),
 ('GET','/leads','Directory, scope, status, queue, sort, page, search, tier','Saved lead work queues','200 items + counts + matching total; 422 invalid query'),
 ('POST','/leads/{lead_id}/status','Path ID + '+c('{"status":"contacted"}'),'Change lead status','200 ProspectDetail; 404 missing; 422 invalid body'),
]
section('api','API contract',table('All eight application endpoints; no authentication. Shared unexpected failures use a safe 500 JSON error.',['Endpoint','Input','Responsibility','Result'],[(f'<strong>{m}</strong> '+c('/api/v1'+p),i,why,res) for m,p,i,why,res in api])+table('API design comparisons are inferred; implementation sources are linked below',['Choice','Why','Alternative','Why not / limit'],[
 ('Thin handlers + Pydantic','Validate the trust boundary; services own business behavior.','Validation and business logic inside page/route code','Duplicates rules across entry points and couples persistence to HTTP.'),
 ('Resource-oriented JSON /api/v1','Stable URLs and explicit errors for four UI views.','RPC-only actions or GraphQL','No current consumer needs the additional protocol or query machinery.'),
 ('Idempotent repeated save + unique constraints','A retry after a lost response can recover the existing lead.','Check-then-insert in UI only','Cannot prevent races between clients. A durable request-id ledger is not implemented.'),
]))

section('frontend','Frontend and KPI semantics',table('Current UI implementation; alternative comparisons are inferred',['Concern','Current approach / why','Alternative','Why not / trade-off'],[
 ('Navigation','Sales dashboard, Prospects, Prospect details, Saved leads; directory toggle controls the population.','One large dashboard containing every detail','Makes each task harder to scan; existing routes isolate list/detail work.'),
 ('Filter state','URL parameters; links preserve directory, queue, sort, page.','Redux/global store or local-only state','No distant-state requirement justifies another store; local-only filters are not shareable in a URL.'),
 ('Async reads','useLoad AbortSignal + sequence guard; retain prior results during refresh.','Uncontrolled fetch effects / query library','Uncontrolled effects risk stale responses. A query library could help caching, but adds a dependency beyond the current needs.'),
 ('Mutations','Disable pending actions; reconcile from saved response; row-level errors.','Optimistic updates without server reconciliation','Can display an unsaved status or stale counts after errors.'),
 ('Responsive leads','Desktop table; compact cards below 768px.','Force the wide table onto phones / Kanban','Wide tables need horizontal scanning; no drag-and-drop stage workflow is required.'),
])+table('Counts are current-state metrics, not a historical funnel',['KPI','Calculation / scope','Interpretation limit'],[
 ('Active saved','New + Contacted + Qualified in selected directory.','Excludes Dismissed.'),
 ('Needs first contact','Status New in selected directory.','No independent call history.'),
 ('Follow-up due','Contacted with unchanged status for ≥14 days.','Not a scheduled task date.'),
 ('Contact coverage','(Contacted + Qualified) / active ×100; zero when no active leads.','Current coverage, not a conversion rate.'),
 ('Saved-lead summary vs matching total','Status/queue counts cover the selected directory before remaining table filters; total covers matching rows.','Do not calculate counts from the current page.'),
]))

section('reliability','Reliability and current limitations',table('Recorded choices plus source-derived limits; no new guarantees',['Choice','Why chosen','Alternative','Why deferred / production consequence'],[
 ('create_all + PostgreSQL startup lock','D5: migrations excluded; advisory transaction lock serializes worker table creation.','Alembic schema migrations','Explicitly excluded from MVP. create_all cannot upgrade existing columns; introduce migrations before data-preserving schema changes.'),
 ('Directory filter in SQL; remaining saved-lead filtering/sorting in Python','D19: database limits the directory; bounded saved set keeps queue logic small.','All filtering/counting/pagination in SQL','More query work for the MVP; move it when measured row count/memory/latency justifies it.'),
 ('Snapshot upsert, then rescore','Reimports update source columns and preserve representative work.','Single atomic ingest-and-score transaction / staged publication','Current helpers commit separately. A rescore failure can leave rows without scores; atomicity/recovery remains work.'),
 ('Database uniqueness + rollback','Enforces one saved prospect and one non-null company key under competing writes.','Application-only existence check','A check can race. Shared/missing phone cases and unexpected IntegrityError handling still need coverage.'),
 ('No queue, cache, or status history','No active slow provider path; no measured need or approved audit requirement.','Durable jobs, cache, event history','Adds recovery/invalidation/schema complexity. Introduce each only for a defined requirement.'),
]))

section('extensibility','Production extensibility — proposed',table('Extension map; these modules exist, but the additions below are not implemented',['Addition / trigger','Affected boundary','Data / contract change','Compatibility / proof needed'],[
 ('Approved new data source','collection/snapshot.py, importer.py, cli.py','Map provider data to validated records; extract reader/upsert boundary because import_file currently calls load_snapshot directly.','Keep listing identity explicit; validate fields, provenance, empty/failure states, and duplicate handling.'),
 ('Periodic refresh / stale data','Importer + rescore command; future scheduler','Define source access, refresh interval, complete-ingest publication, freshness policy.','Preserve lead status; prove retry/reimport safety and consistent score coverage.'),
 ('New score version','scoring.py + prospect_scores + detail response','New rule version/weights; rescore stored results.','Version score meaning; check breakdown compatibility and boundary examples. Do not silently change historical interpretation.'),
 ('Login / representative ownership','Lead model, API access checks, queries, UI session','owner_id/territory policy; revise global company-key uniqueness as needed.','Potentially breaking access semantics; prove isolation and define who can save the same company.'),
 ('Additional territories','Snapshot reader, prospect/territory queries, scoring','Model per-territory distance and search origin rather than assuming one fixed ZIP.','Identity remains company/listing based; validate distance, counts, and scores per territory.'),
 ('Status history / trends','update_status + new status-event table','Write event and status in the same transaction.','Additive response fields; prove one event per real transition before reporting historical conversion.'),
 ('Notes / AI insight, only after approval','Lead services/UI; disconnected additional/insights draft','Note schema/history or insight table + durable job state; provider timeouts/retries.','Additive APIs where possible; preserve saved leads on failure; validate sources/claims and bound cost.'),
]))

section('future','Future work and rollout priorities',table('Suggested order; proposals do not change the approved application scope',['When','Work','Why / acceptance condition','Why not build it all now'],[
 ('First: correctness','Retain regression coverage for distance coercion, API contracts, uniqueness, time boundaries, and mutation refresh; add CI.','Allowed filters work; contract success/null/error shapes agree; repeat/concurrent saves preserve identity.','Tests have run under D22. CI, broader browser coverage, and production verification remain separate work.'),
 ('Before external users','Authentication/authorization, TLS, deployment secret management, backups/restore, schema migration procedure.','Authorized access and recoverable saved work; checked restore and upgrade path.','Local Compose and a named volume are not production access control or a backup plan.'),
 ('Before shared editing','Ownership policy, optimistic concurrency/version checks, status audit if required.','No silent overwrite; conflict response identifies a stale edit.','Current app has one shared workspace and no version/history model.'),
 ('As operations need it','Structured request logs, metrics/alerts, CI checks, documented incident ownership.','Failures are diagnosable; release checks exercise the actual API and browser flow.','No measured SLOs or operational targets have been established.'),
 ('After measured growth','SQL saved-lead aggregates, query-plan-driven indexes, cursor pagination, pool sizing; selective stats cache.','Measure latency/memory/connections; retain directory semantics and invalidate cache after ingest.','Cursor/cache/pooler complexity is not justified solely by possible future scale.'),
]))

section('verification','Testing and evidence',table('This revision changes documentation only; it does not rerun application tests',['Check / test','Purpose','Current evidence / status'],[
 ('Source inventory','Compare route decorators, schemas, models, decision log.','Eight endpoints and three tables inspected. Notes/AI remain deferred.'),
 ('Last manual data check','Confirm imported data and a known filter issue.','Prior review: stats 200 with 409 prospects. The former max_distance=10 failure is fixed by an integer parser/allowed-band validator; TEST_RESULTS.md records the regression passing.'),
 ('API/database integration tests','Save/repeat/race/conflict, reimport preservation, scoring boundaries, API validation.','TEST_RESULTS.md records 106 passes across API/database/browser coverage on 2026-11-05. D22 authorizes isolated marker-scoped rows in the demo database; not rerun for this presentation.'),
 ('Playwright browser tests','Filter/detail/save/status/counts/reload; keyboard, narrow layout, network errors.','Recorded: 10 Chromium browser tests pass, including recovery, keyboard save, directory navigation and narrow layouts. Other browsers and a full accessibility audit remain uncovered.'),
 ('Build/type checks','Catch TypeScript/build regressions.','The test report records typecheck/build passing. Compilation is supporting evidence, not proof of persistence or the full user flow.'),
 ('HTML review','Unique anchors, local links, well-formed embedded SVGs, complete route inventory.','Checked at handoff. Browser rendering remains unverified because the browser host was unavailable.'),
]))

references=[
 ('backend/app/models.py','Tables, constraints, relationships'),('backend/app/scoring.py','Priority rules'),
 ('backend/app/services.py','Workflow and queue logic'),('backend/app/queries.py','SQL filtering and aggregates'),
 ('backend/app/api/__init__.py','Route handlers'),('backend/app/schemas.py','Validation / response types'),
 ('openapi.yaml','API contract'),('frontend/app/leads/page.tsx','Saved-lead UI'),
 ('docs/DECISION_LOG.md','Recorded choices'),('docs/TEST_PLAN.md','Coverage plan and execution status'),('docs/TEST_RESULTS.md','Recorded 106-pass run, fixes, and limits'),
 ('docs/operations/production-extensibility.md','Extension proposals'),('docs/operations/production-readiness.md','Production handoff'),
]
refs='<details><summary>Source references</summary>'+table('Repository sources',['File','Responsibility'],[(link(p),label) for p,label in references])+'</details>'
css='''
:root{--ink:#172b42;--muted:#53667a;--line:#dce3ec;--blue:#2157a4;--soft:#f5f7fa}*{box-sizing:border-box}body{margin:0;background:#fff;color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}main{max-width:1280px;margin:auto;padding:32px 26px 60px}h1{font-size:clamp(2rem,4.5vw,3rem);line-height:1.15;margin:0 0 14px;letter-spacing:-.03em}h2{font-size:1.4rem;margin:0 0 12px}h3{font-size:1.07rem;color:var(--blue);margin:23px 0 10px}.figure-table{min-width:0}.figure-table td{padding:0;font-weight:400}.figure-table .diagram{border:0;margin:0}section{border-top:1px solid var(--line);margin-top:25px;padding-top:22px}nav{display:flex;flex-wrap:wrap;gap:8px 17px;padding:15px 0 4px;font-size:.9rem}a{color:var(--blue);text-underline-offset:3px}a:focus-visible,summary:focus-visible,.scroll:focus-visible{outline:3px solid var(--blue);outline-offset:4px}code{font:0.88em/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.scroll{overflow:auto;margin:13px 0 20px}table{border-collapse:collapse;width:100%;min-width:760px;table-layout:auto}caption{text-align:left;color:var(--muted);font-size:.85rem;padding:0 0 9px;max-width:100ch}th,td{border:1px solid var(--line);padding:11px 12px;text-align:left;vertical-align:top;overflow-wrap:break-word}th{background:var(--soft);font-weight:650}td:first-child{font-weight:550;min-width:135px}table:has(th:nth-child(5)){min-width:1050px}th:nth-child(n+2){min-width:150px}.meta table{min-width:0}.meta td:first-child{width:130px}.meta td{font-size:.86rem;padding:7px 10px}.diagram{overflow:auto;border:1px solid var(--line);border-radius:5px;margin:16px 0}.diagram svg{width:100%;height:auto;min-width:760px;display:block}details{border-top:1px solid var(--line);margin-top:26px;padding-top:16px}summary{font-weight:600;cursor:pointer}.num{color:var(--blue);font-size:.9em;margin-right:8px}@media(max-width:650px){main{padding:22px 14px 40px}th,td{padding:9px}h2{font-size:1.2rem}}@media print{nav{display:none}main{padding:0;max-width:none}table{min-width:0!important;font-size:10px}th,td{padding:5px;min-width:0!important}.diagram svg{min-width:0}tr{break-inside:avoid}a{color:inherit}}
'''
date=datetime.now().astimezone().strftime('%d %B %Y, %H:%M %Z')
metadata='<div class="meta">'+table('',['Reference','Status'],[('Updated',date),('Format','Technical tables, embedded diagrams; one offline HTML file.'),('Decision evidence','Recorded choices are attributed by ID. Unrecorded alternative comparisons are explicitly inferred. Future additions are proposals.')])+'</div>'
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Roofing Lead Intel · Technical overview</title><style>'+css+'</style></head><body><main><header><h1>Roofing Lead Intel</h1>'+metadata+'</header><nav aria-label="Contents">'+''.join(f'<a href="#{k}">{t}</a>' for k,t in nav)+'</nav>'+''.join(parts)+refs+'</main></body></html>'
target.write_text(html)
print('Updated:',target)
print('Sections:',len(parts),'Tables:',html.count('<table>'),'Bytes:',len(html.encode()))
