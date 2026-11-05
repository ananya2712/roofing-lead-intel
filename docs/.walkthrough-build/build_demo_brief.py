from pathlib import Path
from datetime import datetime
from html import escape
import json

root=Path(__file__).resolve().parents[2]
out=root/'docs/CODE_WALKTHROUGH.html'
archive=root/'docs/.walkthrough-build/archive'
archive.mkdir(parents=True,exist_ok=True)
if out.exists():
    backup=archive/'walkthrough-before-demo-brief.html'
    if not backup.exists():backup.write_bytes(out.read_bytes())

db='''<svg id="db-model" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 730" role="img" aria-labelledby="db-title db-desc" font-family="Arial, sans-serif">
<title id="db-title">Database model: source facts, calculated priority, and saved work</title>
<desc id="db-desc">Prospects is the parent table. Each prospect can have zero or one score row and zero or one saved lead. Both child tables reference prospects.id. The lead's prospect_id is unique, and company_key is unique when present.</desc>
<rect width="1200" height="730" fill="#ffffff"/>
<g stroke="#ccd6e1" fill="#ffffff" stroke-width="1.5">
<rect x="360" y="20" width="480" height="270" rx="8"/>
<rect x="20" y="418" width="530" height="275" rx="8"/>
<rect x="650" y="418" width="530" height="300" rx="8"/>
</g>
<path d="M368 20 H832 Q840 20 840 28 V78 H360 V28 Q360 20 368 20" fill="#0e2a47"/>
<path d="M28 418 H542 Q550 418 550 426 V476 H20 V426 Q20 418 28 418" fill="#2157a4"/>
<path d="M658 418 H1172 Q1180 418 1180 426 V476 H650 V426 Q650 418 658 418" fill="#16734d"/>
<g fill="#ffffff" font-size="25" font-weight="700">
<text x="384" y="59">prospects</text><text x="44" y="457">prospect_scores</text><text x="674" y="457">leads</text>
</g>
<g fill="#53667a" font-size="17"><text x="384" y="107">GAF SOURCE FACTS</text><text x="44" y="507">CALCULATED PRIORITY</text><text x="674" y="507">REPRESENTATIVE WORK</text></g>
<g fill="#172b42" font-size="20">
<text x="384" y="145" font-weight="700">id</text><text x="793" y="145" text-anchor="end" font-size="16" fill="#53667a">PK</text>
<text x="384" y="180">directory + gaf_source_id</text><text x="816" y="180" text-anchor="end" font-size="15" fill="#53667a">UNIQUE</text>
<text x="384" y="215">name, phone_digits, location</text><text x="384" y="250">distance, certifications, retrieved_at</text>
<text x="44" y="548" font-weight="700">prospect_id</text><text x="526" y="548" text-anchor="end" font-size="16" fill="#2157a4">PK + FK</text>
<text x="44" y="587">score</text><text x="526" y="587" text-anchor="end" font-size="16" fill="#53667a">CHECK 0–100</text>
<text x="44" y="626">breakdown (JSONB)</text><text x="44" y="665">rule_version, scored_at</text>
<text x="674" y="548" font-weight="700">id</text><text x="1156" y="548" text-anchor="end" font-size="16" fill="#53667a">PK</text>
<text x="674" y="587" font-weight="700">prospect_id</text><text x="1156" y="587" text-anchor="end" font-size="16" fill="#16734d">FK + UNIQUE</text>
<text x="674" y="626">company_key</text><text x="1156" y="626" text-anchor="end" font-size="15" fill="#53667a">UNIQUE if present</text>
<text x="674" y="665">status</text><text x="674" y="698" font-size="18">saved_at, status_changed_at</text>
</g>
<g fill="none" stroke="#596f86" stroke-width="2.2">
<path d="M475 290 V335 H285 V418"/><path d="M725 290 V335 H915 V418"/>
<path d="M467 301 H483 M717 301 H733"/>
<circle cx="285" cy="398" r="5" fill="#ffffff"/><path d="M277 412 H293"/>
<circle cx="915" cy="398" r="5" fill="#ffffff"/><path d="M907 412 H923"/>
</g>
<g fill="#ffffff"><rect x="95" y="354" width="380" height="30"/><rect x="715" y="354" width="400" height="30"/></g>
<g fill="#324b65" font-size="18" text-anchor="middle"><text x="285" y="376">One prospect → zero or one score</text><text x="915" y="376">One prospect → zero or one saved lead</text></g>
</svg>'''

flow='''<svg id="request-flow" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 220" role="img" aria-labelledby="flow-title" font-family="Arial, sans-serif">
<title id="flow-title">A browser request reaches Next.js, Flask, and PostgreSQL</title>
<defs><marker id="flow-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#62788e"/></marker></defs>
<rect width="1120" height="220" fill="#ffffff"/>
<g fill="#f5f7fa" stroke="#ccd6e1"><rect x="10" y="62" width="205" height="100" rx="6"/><rect x="302" y="62" width="205" height="100" rx="6"/><rect x="594" y="62" width="205" height="100" rx="6"/><rect x="886" y="62" width="220" height="100" rx="6"/></g>
<g text-anchor="middle" fill="#172b42" font-size="23" font-weight="700"><text x="112" y="104">Browser</text><text x="404" y="104">Next.js</text><text x="696" y="104">Flask</text><text x="996" y="104">PostgreSQL</text></g>
<g text-anchor="middle" fill="#53667a" font-size="16"><text x="112" y="135">User action</text><text x="404" y="135">UI + API forwarding</text><text x="696" y="135">Validate + services</text><text x="996" y="135">Read / write rows</text></g>
<g fill="none" stroke="#62788e" stroke-width="2" marker-end="url(#flow-arrow)"><path d="M215 112 H298"/><path d="M507 112 H590"/><path d="M799 112 H882"/></g>
<g text-anchor="middle" fill="#53667a" font-size="15"><text x="258" y="91">HTTP</text><text x="550" y="91">/api/v1</text><text x="842" y="91">SQL</text><text x="560" y="202">JSON response returns to the page; the UI refreshes its data</text></g>
</svg>'''

css='''
:root{--ink:#172b42;--muted:#53667a;--line:#dce3ec;--blue:#2157a4;--soft:#f5f7fa}*{box-sizing:border-box}body{margin:0;background:#fff;color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}main{max-width:1120px;margin:auto;padding:34px 26px 64px}h1{font-size:clamp(2rem,4.5vw,3.1rem);line-height:1.15;margin:0 0 10px;letter-spacing:-.03em}h2{font-size:1.45rem;margin:0 0 13px}h3{font-size:1rem;margin:0 0 8px;color:var(--blue)}section{border-top:1px solid var(--line);margin-top:28px;padding-top:24px}ul{padding-left:22px;margin:8px 0 12px}li{margin:7px 0}a{color:var(--blue);text-underline-offset:3px}a:focus-visible,summary:focus-visible,.scroll:focus-visible{outline:3px solid var(--blue);outline-offset:4px}nav{display:flex;flex-wrap:wrap;gap:8px 17px;padding:18px 0 6px;font-size:.9rem}code{font:0.87em/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.meta{font-size:.85rem;color:var(--muted)}.cols{display:grid;grid-template-columns:1fr 1fr;gap:30px}.diagram{overflow-x:auto;border:1px solid var(--line);border-radius:6px;margin:16px 0;background:#fff}.diagram svg{width:100%;height:auto;display:block;min-width:760px}.scroll{overflow-x:auto;margin:14px 0}table{width:100%;border-collapse:collapse;text-align:left;font-size:.92rem}th{background:var(--soft)}th,td{padding:10px 12px;vertical-align:top;border:1px solid var(--line)}td:first-child{white-space:nowrap}details{margin-top:22px;padding-top:15px;border-top:1px solid var(--line)}summary{cursor:pointer;font-weight:600}.num{color:var(--blue);font-size:.9em;margin-right:8px}header{padding-bottom:6px}.callout{border-left:3px solid var(--blue);padding-left:17px}footer{margin-top:28px;color:var(--muted);font-size:.85rem}@media(max-width:650px){main{padding:24px 16px 40px}.cols{grid-template-columns:1fr;gap:12px}h2{font-size:1.25rem}th,td{padding:8px}.diagram svg{min-width:740px}}@media print{nav{display:none}main{max-width:none;padding:0}.diagram svg{min-width:0}section{break-inside:avoid}a{color:inherit}}
'''
items=[('project','Project'),('demo','Demo'),('stack','Stack'),('requirements','Requirements'),('flow','Data flow'),('database','DB model'),('api','API'),('frontend','Frontend'),('decisions','Decisions'),('testing','Testing')]
def bullets(items):return '<ul>'+''.join('<li>'+x+'</li>' for x in items)+'</ul>'
def sec(i,key,title,body):return f'<section id="{key}"><h2><span class="num">{i:02}</span>{title}</h2>{body}</section>'
sections=[]
sections.append(sec(1,'project','Project and problem',bullets([
 '<strong>User:</strong> a roofing-materials distributor’s sales representative.',
 '<strong>Problem:</strong> decide which contractors to contact and keep track of saved leads.',
 '<strong>Data:</strong> 409 recorded GAF listings near ZIP 10013, within 50 miles: 176 residential + 233 commercial.',
 '<strong>Scope:</strong> explain priority, save leads, update status. Notes and AI insights are deferred.',
])))
sections.append(sec(2,'demo','Demo sequence',bullets([
 '<strong>1. Overview:</strong> show the pipeline and switch All / Residential / Commercial.',
 '<strong>2. Prospects:</strong> search, sort, and open a contractor.',
 '<strong>3. Details:</strong> explain the score and point out unknown information.',
 '<strong>4. Save as lead:</strong> show the saved row in Saved leads.',
 '<strong>5. Take action:</strong> mark Contacted; show updated counts and the follow-up queue.',
 '<strong>Open:</strong> <code>http://localhost:3000</code>. Follow-up means Contacted with no status change for 14+ days.',
])))
sections.append(sec(3,'stack','Tech stack and why',bullets([
 '<strong>Next.js + React + TypeScript:</strong> four views, shared controls, typed API calls.',
 '<strong>Flask + Pydantic:</strong> Python business logic with validated API inputs and responses.',
 '<strong>PostgreSQL + SQLAlchemy:</strong> related records, persistent status, database-enforced uniqueness.',
 '<strong>Docker Compose:</strong> runs the UI, API, and database together.',
 '<strong>Trade-off:</strong> separate UI/API services need more setup than one framework; business logic stays in Python.',
])))
sections.append(sec(4,'requirements','Functional and non-functional requirements','<div class="cols"><div><h3>Functional</h3>'+bullets([
 'Search/filter contractors and explain their priority.',
 'Save a company once; change its lead status.',
 'Show first-contact and follow-up work queues.',
])+'</div><div><h3>Quality</h3>'+bullets([
 'Repeatable scoring; missing information stays Unknown.',
 'Validate requests; prevent duplicate saved records.',
 'Show loading/errors and preserve saved work.',
])+'</div></div>'))
sections.append(sec(5,'flow','Data flow','<div class="diagram">'+flow+'</div>'+bullets([
 '<strong>Setup:</strong> GAF browser collection → JSON snapshots → <code>flask import-snapshot</code> → validated prospects + stored scores.',
 '<strong>Save:</strong> button → POST → insert lead → commit → return updated details. No live GAF or AI request runs.',
])))
sections.append(sec(6,'database','Database model','<div class="diagram">'+db+'</div>'+bullets([
 '<strong>Separate ownership:</strong> source facts, calculated priority, and representative work.',
 '<strong>PK</strong> = primary key. <strong>FK</strong> = foreign key to <code>prospects.id</code>. Each prospect has at most one score and one saved lead.',
 '<strong>Duplicate protection:</strong> unique listing ID per directory; unique saved prospect; unique non-null company phone key.',
])))
api_rows=[
 ('GET','/health','API/database connectivity','<code>{status: "ok"}</code>'),
 ('GET','/overview','Pipeline counts and call lists','Overview summary'),
 ('GET','/prospects','Filtered, sorted prospect page','Items + matching total'),
 ('GET','/prospects/stats','Prospect KPI/chart counts','Counts + retrieval time'),
 ('GET','/prospects/{prospect_id}','Source facts, score, unknowns','Prospect details'),
 ('POST','/prospects/{prospect_id}/save','Save as lead','201 new / 200 already saved'),
 ('GET','/leads','Saved leads and work queues','Items + counts + matching total'),
 ('PATCH','/leads/{lead_id}/status','Change status','Updated prospect details'),
]
api_table='<div class="scroll" tabindex="0"><table><thead><tr><th scope="col">Endpoint</th><th scope="col">Purpose</th><th scope="col">Result</th></tr></thead><tbody>'+''.join('<tr><td><strong>'+m+'</strong> <code>/api/v1'+p+'</code></td><td>'+purpose+'</td><td>'+result+'</td></tr>' for m,p,purpose,result in api_rows)+'</tbody></table></div>'
sections.append(sec(7,'api','API endpoints',api_table+bullets([
 '<strong>Prospect inputs:</strong> search, directory, priority, distance, certification, sort, page.',
 '<strong>Lead inputs:</strong> directory, active/all/dismissed scope, status, first-contact/follow-up queue, sort, page.',
 '<strong>Status body:</strong> <code>{"status":"contacted"}</code>; allowed: New, Contacted, Qualified, Dismissed.',
 '<strong>Errors:</strong> 422 invalid input; 404 missing record; 409 company already saved through another listing.',
 '<strong>Directory counts:</strong> follow the selected directory; saved-lead totals precede other table filters. No authentication is implemented.',
])))
sections.append(sec(8,'frontend','Frontend behavior',bullets([
 '<strong>Views:</strong> Overview, Prospects, Prospect details, Saved leads.',
 '<strong>Saved leads:</strong> first-contact/follow-up queues, status cards, matching count, reasons, distance, and contact actions.',
 '<strong>State:</strong> filters live in the URL; <code>useLoad</code> guards older responses; save/status controls show pending and error states.',
 '<strong>Small screens:</strong> compact saved-lead cards replace the desktop table.',
])))
sections.append(sec(9,'decisions','Key decisions and challenges',bullets([
 '<strong>Fixed scoring over AI:</strong> distance 35 + product fit 35 + data readiness 30. High ≥70; Medium 45–69. Ratings/reviews do not score.',
 '<strong>Example:</strong> 35 distance + 20 certification + 10 systems + 0 specialty + 30 readiness = 95. This measures fit under rules, not buying intent.',
 '<strong>Snapshots over live scraping:</strong> recorded GAF data avoids runtime scraping; refreshing data requires another import.',
 '<strong>Phone-based company matching:</strong> prevents known duplicates across directories; missing/shared numbers remain a limit.',
 '<strong>Database constraints over UI-only checks:</strong> enforce uniqueness during competing saves. Repeating a save returns the existing lead.',
 '<strong>After the MVP:</strong> authentication, safe schema upgrades, and backups before shared production use.',
])))
sections.append(sec(10,'testing','Testing and demo limits',bullets([
 '<strong>Observed in this review:</strong> stats API returned 409 listings: 176 residential + 233 commercial.',
 '<strong>Known issue:</strong> <code>max_distance=10</code> still returns 422. Avoid promising that filter works.',
 '<strong>Automated tests:</strong> planned, not run here. Priorities: save/deduplication, score boundaries, filter/API contracts, and the browser workflow.',
 '<strong>Manual evidence:</strong> import, save, conflict, and restart checks are recorded in <a href="BUILD_PROGRESS.md">BUILD_PROGRESS.md</a>; they were not repeated here.',
 '<strong>Visual review:</strong> diagrams checked separately; browser page rendering unavailable in this session.',
])))
refs=[('backend/app/models.py','Tables and constraints'),('backend/app/scoring.py','Priority rules'),('backend/app/services.py','Saving, statuses, queues, counts'),('backend/app/api/__init__.py','Eight route handlers'),('backend/app/schemas.py','Request/response shapes'),('openapi.yaml','API contract'),('frontend/app/leads/page.tsx','Saved leads UI'),('docs/DECISION_LOG.md','Recorded choices and deferred scope')]
reference='<details><summary>Code references</summary>'+bullets([f'<a href="../{p}"><code>{p}</code></a> — {label}' for p,label in refs])+'</details>'
date=datetime.now().astimezone().strftime('%d %B %Y, %H:%M %Z')
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Roofing Lead Intel · Demo guide</title><style>'+css+'</style></head><body><main><header><h1>Roofing Lead Intel</h1><ul class="meta"><li>Demo guide · '+date+' · Recorded GAF data</li></ul></header><nav aria-label="Contents">'+''.join(f'<a href="#{key}">{label}</a>' for key,label in items)+'</nav>'+''.join(sections)+reference+'<footer><ul><li>Offline HTML. No application code or saved data changed.</li></ul></footer></main></body></html>'
out.write_text(html,encoding='utf-8')
svg_path=root/'docs/architecture/demo-data-model.svg'
svg_path.write_text(db,encoding='utf-8')
print('Created concise guide:',out)
print('Editable DB diagram:',svg_path)
print('HTML bytes:',len(html.encode()))
