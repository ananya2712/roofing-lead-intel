import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {finalizePresentation,resolvePresentationFont} from '/Users/ananyauppal/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations/container_tools/artifact_tool_utils.mjs';

const ROOT='/Users/ananyauppal/Desktop/Instalily Case Study/roofing-lead-intel';
const BUILD=path.join(ROOT,'docs/.presentation-build/full');
const SKILL='/Users/ananyauppal/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations';
const REV=process.argv[2]||'v1';
const FINAL=path.join(BUILD,`output/PROJECT_DEMO-${REV}.pptx`);
const SOURCE=JSON.parse(await fs.readFile(path.join(BUILD,'source.json'),'utf8'));
const FONT=resolvePresentationFont({fontFamily:'Arial'});
const C={navy:'#0E2A47',blue:'#2157A4',green:'#16734D',ink:'#172B42',muted:'#53667A',line:'#DCE3EC',soft:'#F5F7FA',white:'#FFFFFF'};
const deck=Presentation.create({slideSize:{width:1280,height:720}});
const owners=[];const definitions=[];

function text(s,name,value,x,y,w,h,size=26,color=C.ink,bold=false){
 const b=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 b.text=value;b.text.style={fontFamily:FONT,typeface:FONT,fontSize:size,color,bold,verticalAlignment:'top',insets:0,wrap:'word'};return b;
}
function nativeTable(s,headers,rows,{x=64,y=157,w=1152,h=452,widths,font=25,headerColor=C.soft,headerText=C.navy}={}){
 const values=[headers,...rows];
 const t=s.tables.add({rows:values.length,columns:headers.length,left:x,top:y,width:w,height:h,columnWidths:widths||headers.map(()=>w/headers.length),values});
 t.borders.assign({style:'solid',fill:C.line,width:1});
 for(let r=0;r<values.length;r++)for(let c=0;c<headers.length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?headerColor:C.white;
  cell.text.style={fontFamily:FONT,typeface:FONT,fontSize:font,color:r===0?headerText:C.ink,bold:r===0||c===0};
 }
 const headerH=Math.min(58,h/values.length);
 t.rows[0].height=headerH;
 for(let r=1;r<values.length;r++)t.rows[r].height=(h-headerH)/(values.length-1);
 return t;
}
function sourceNotes(keys){return keys.map(key=>`HTML SECTION ${key}\n`+(SOURCE.sections[key]||[]).map(t=>t.map(r=>r.join(' | ')).join('\n')).join('\n\n')).join('\n\n');}
function slide(title,keys,script,paths=[],limit=''){
 const s=deck.slides.add();s.background.fill=C.white;
 const n=deck.slides.items.length;
 text(s,'title',title,64,42,1152,83,48,C.navy,true);
 text(s,'brand','Roofing Lead Intel',64,673,1040,25,18,C.muted);
 text(s,'page',String(n).padStart(2,'0'),1160,673,56,25,18,C.muted);
 s.speakerNotes.text=`SPEAKING SCRIPT\n${script}\n\nSOURCE\n${SOURCE.htmlPath}\nHTML SHA-256: ${SOURCE.htmlSha256}\n${paths.join('\n')}\n\nDETAILS FROM THE HTML\n${sourceNotes(keys)}\n\nEVIDENCE / LIMITS\n${limit||'Source inspection explains implementation. This presentation task did not rerun the application test suite. Alternative comparisons are inferred unless a decision ID records the reason. Production additions are proposals.'}`;
 definitions.push({slide:n,title,htmlSections:keys});owners.push(n);return s;
}
function note(s,value){text(s,'note',value,64,625,1152,39,21,C.muted);}

let s=slide('Product and scope',['project'],'A roofing-materials distributor representative needs a short list of contractors to call and a way to track saved work. The MVP ranks recorded GAF listings using fixed rules and keeps lead status separate from source facts. No sales uplift or time saving has been measured.',['docs/DECISION_LOG.md','docs/BUILD_PROGRESS.md']);
nativeTable(s,['Topic','Current MVP'],[
 ['User','Distributor sales representative'],['Problem','Choose contractors to contact and track saved work'],['Data','409 recorded listings: 176 residential + 233 commercial'],['Territory','ZIP 10013, within 50 miles'],['Boundary','Notes and AI insights deferred; one shared workspace'],
],{widths:[265,887],h:450,font:28});
note(s,'Recorded GAF snapshots, not a live directory search');

s=slide('Technology choices',['stack'],'The stack is approved in repository guidance. The comparisons are engineering explanations, not proof that the author evaluated every competing framework. The cost of separate services is local setup and deployment coordination.',['AGENTS.md','backend/requirements.txt','frontend/package.json','docker-compose.yml']);
nativeTable(s,['Choice','Why it fits','Alternative','Trade-off'],[
 ['Next.js + TS','Routes and typed UI','Vite SPA','Also viable; migration adds no MVP capability'],
 ['Flask + Pydantic','Python services, validation','FastAPI','Auto OpenAPI useful; existing Flask code is sufficient'],
 ['PostgreSQL + ORM','Relations and unique constraints','SQLite / files','Separate DB process; files lack relational guarantees'],
 ['REST + typed client','Explicit resource contracts','GraphQL','No graph-query requirement; contracts can drift'],
 ['Docker Compose','Repeatable local services','Host processes / K8s','Host setup is manual; K8s adds unneeded operations'],
],{widths:[235,310,240,367],h:470,font:24});
note(s,'Alternative comparisons are inferred; original framework rejection reasons are unrecorded');

s=slide('Requirements',['requirements'],'The functional requirements are prospect discovery, explainable priority, and a saved lead workflow. Quality depends on validation and write safety, not simply on choosing TypeScript or PostgreSQL. The earlier distance-filter bug has been fixed and is covered in the recorded test report.',['backend/app/schemas.py','backend/app/models.py','backend/app/services.py','docs/TEST_RESULTS.md']);
nativeTable(s,['Need','Implementation','Boundary'],[
 ['Find prospects','Directory, search, tier, sort, pagination','Recorded source data'],
 ['Explain priority','Score breakdown and Unknown fields','No purchase-intent prediction'],
 ['Track work','Save, status and call queues','No notes or owner isolation'],
 ['Protect integrity','Validation, transactions, uniqueness','Concurrency needs ongoing regression coverage'],
 ['Handle async UI','Pending, error and latest-response guards','No production reliability guarantee'],
],{widths:[245,497,410],h:450,font:26});

s=slide('Architecture and data flow',['flow'],'The browser uses one origin. Next.js forwards /api/v1 to Flask, whose services read and write PostgreSQL. One-time JSON import is a separate CLI path. No live GAF or AI provider is called during page reads or a save.',['frontend/next.config.mjs','frontend/lib/api.ts','backend/app/api/__init__.py','backend/app/cli.py']);
const boxes=[];
for(const [i,label] of ['Browser','Next.js','Flask','PostgreSQL'].entries()){
 const b=s.shapes.add({geometry:'rect',name:`component-${i}`,position:{left:64+i*300,top:165,width:i===3?252:220,height:90},fill:C.soft,line:{fill:C.line,width:1}});
 b.text=label;b.text.style={fontFamily:FONT,typeface:FONT,fontSize:29,bold:true,color:C.navy,alignment:'center',verticalAlignment:'middle'};boxes.push(b);
}
for(let i=0;i<3;i++)s.shapes.connect(boxes[i],boxes[i+1],{kind:'straight',fromSide:'right',toSide:'left',line:{fill:C.muted,width:2},head:{type:'triangle',width:'sm',length:'sm'}});
for(const [i,label] of ['HTTP','/api/v1','SQL'].entries())text(s,`protocol-${i}`,label,287+i*300,130,90,28,21,C.muted);
nativeTable(s,['Path','Execution','Alternative / limit'],[
 ['Import','JSON → validation → upsert → stored scores','Live feed needs approved access and refresh policy'],
 ['Read','Route → service → query → response','Modular monolith avoids distributed-service failures'],
 ['Write','Validate → commit → response → refresh','UI-only checks cannot enforce saved-company identity'],
],{y:325,h:280,widths:[190,480,482],font:25});

s=slide('Opening the app: file control',['control'],'Service startup and opening a page are different events. After the initial shell hydrates, the Sales dashboard and Sidebar issue independent requests. Their completion order is not fixed. No import or rescore is triggered by opening the page. See notes for exact line-referenced HTML traces.',['backend/wsgi.py','backend/app/__init__.py','frontend/app/layout.tsx','frontend/app/page.tsx','frontend/components/ui/layout/Sidebar.tsx','backend/app/services.py']);
nativeTable(s,['Step','File / function','Control transfer'],[
 ['Startup','backend/wsgi.py → create_app()','Load config, init DB, register /api/v1'],
 ['Page','frontend/app/layout.tsx\napp/page.tsx','RootLayout → OverviewPage → OverviewView'],
 ['A: page read','app/page.tsx · load()','GET /overview with selected directory'],
 ['B: badge read','Sidebar.tsx · useEffect','Independent GET /prospects/stats'],
 ['Server','api/__init__.py → services.py\nqueries.py → PostgreSQL','Validate query; read saved leads, scores and stats'],
 ['Return','api.ts → component state','Render dashboard and badge responses independently'],
],{widths:[145,465,542],h:470,font:24});
note(s,'A and B are parallel reads. OpenAPI/type generation is not a runtime HTTP step.');

s=slide('Saving from Prospects: file control',['control'],'A row SaveButton sends the POST. The service loads the prospect, commits one lead, expires stale ORM state, rebuilds the detail response and returns 201. The Prospects callback then starts independent list and statistics refreshes. The sidebar pathname has not changed, so its badge can stay stale until navigation.',['frontend/components/leads/SaveButton.tsx','frontend/app/prospects/page.tsx','backend/app/api/__init__.py','backend/app/services.py','backend/app/models.py','frontend/lib/useLoad.ts']);
nativeTable(s,['Step','File / function','Result'],[
 ['1','SaveButton.tsx · save()','Disable button; POST prospect ID'],
 ['2','lib/api.ts + next.config.mjs','Forward /api/v1/prospects/{id}/save'],
 ['3','api/__init__.py → services.py','Load prospect, score and existing lead'],
 ['4','models.py + services.py','Insert Lead; unique indexes; commit'],
 ['5','services.py · expire_all()','Reload ORM state; return ProspectDetail / 201'],
 ['6','prospects/page.tsx · onSaved','list.reload() and loadStats() can overlap'],
],{widths:[100,490,562],h:460,font:25});
note(s,'Repeat save: 200. Same company via another listing: 409. No rescore or provider call.');

s=slide('Database model',['database'],'The model separates three ownership groups. Prospect is source data. ProspectScore is a persisted calculation with its version and effective time. Lead stores representative work. Both children are one-to-zero-or-one from Prospect, enforced through primary/unique foreign keys. The company key is unique only when non-null.',['backend/app/models.py','backend/app/collection/importer.py','backend/app/db.py']);
nativeTable(s,['prospects','Key'],[['id','PK'],['directory + source ID','UNIQUE'],['GAF facts / retrieved_at','Source']],{x:384,y:142,w:512,h:180,widths:[345,167],font:24,headerColor:C.navy,headerText:C.white});
nativeTable(s,['prospect_scores','Key'],[['prospect_id','PK + FK'],['score / breakdown','0–100 / JSONB'],['rule_version / scored_at','Stored']],{x:64,y:431,w:512,h:188,widths:[302,210],font:24,headerColor:C.blue,headerText:C.white});
nativeTable(s,['leads','Key'],[['id / prospect_id','PK / UNIQUE FK'],['company_key','Unique if present'],['status / timestamps','Rep work']],{x:704,y:431,w:512,h:188,widths:[285,227],font:24,headerColor:C.green,headerText:C.white});
function line(x,y,w,h){s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:C.muted,width:2}});}
line(500,322,1,42);line(320,364,180,1);line(320,364,1,66);
line(780,322,1,42);line(780,364,180,1);line(960,364,1,66);
text(s,'score-cardinality','1 prospect : 0..1 score',100,382,440,36,24,C.blue);
text(s,'lead-cardinality','1 prospect : 0..1 saved lead',720,382,470,36,24,C.green);
note(s,'PK = primary key. FK = foreign key to prospects.id. No note or insight table is active.');

s=slide('Scoring and business rules',['rules'],'Fixed rules produce the same result for the same source fields, rule version and effective time. Saving and changing status never add points. The example 95-point residential contractor has no specialty points. Freshness is stored during import/rescore; GET requests do not update it.',['backend/app/scoring.py','backend/app/collection/importer.py','docs/DECISION_LOG.md']);
nativeTable(s,['Signal','Maximum points'],[['Distance','35'],['Certification','20'],['Roof systems','10'],['Specialty','5'],['Phone','10'],['Website','10'],['Full address','5'],['Freshness','5']],{x:64,y:154,w:590,h:464,widths:[410,180],font:25});
nativeTable(s,['Tier','Score'],[['High','70–100'],['Medium','45–69'],['Low','0–44']],{x:706,y:154,w:510,h:220,widths:[260,250],font:27});
nativeTable(s,['Recorded-data example','Points'],[['Distance + fit','35 + 20 + 10 + 0'],['Readiness','10 + 10 + 5 + 5'],['Total','95 / 100']],{x:706,y:402,w:510,h:216,widths:[275,235],font:25});
note(s,'Missing inputs remain Unknown. Ratings/reviews do not score. Fit is not buying intent.');

s=slide('API contract: reads',['api'],'These are all six GET endpoints. Full route prefixes are visible. Health has no page caller. Sales dashboard calls overview, Prospects and Sidebar call stats, and the list/detail views call their corresponding resources. Directory is optional for overview and stats. No endpoint authenticates users.',['backend/app/api/__init__.py','backend/app/schemas.py','openapi.yaml','frontend/lib/api-types.ts']);
nativeTable(s,['Endpoint','Purpose','Result'],[
 ['GET /api/v1/health','API + DB health','status: ok'],
 ['GET /api/v1/overview','Pipeline and queues','Overview'],
 ['GET /api/v1/prospects','Search/filter/sort page','Items + total'],
 ['GET /api/v1/prospects/stats','Directory KPI counts','Counts + time'],
 ['GET /api/v1/prospects/{prospect_id}','Facts, score, Unknown','ProspectDetail'],
 ['GET /api/v1/leads','Saved-work queues','Items + counts'],
],{widths:[660,260,232],h:460,font:24});
note(s,'Queries support directory, filter and pagination contracts. Invalid inputs return 422.');

s=slide('API contract: mutations',['api'],'Save is bodyless and takes the prospect ID from the path. Status uses a JSON body. Both return a ProspectDetail response so callers can reconcile with saved server state. A network error can happen after a commit, so UI rollback alone does not establish what persisted.',['backend/app/api/__init__.py','backend/app/services.py','backend/app/models.py','frontend/lib/api.ts']);
nativeTable(s,['Endpoint','Input','Result'],[
 ['POST /api/v1/prospects/{prospect_id}/save','Path ID; no body','201 created\n200 already saved'],
 ['PATCH /api/v1/leads/{lead_id}/status','{"status":\n"contacted"}','200 updated\nProspectDetail'],
],{y:155,h:255,widths:[670,230,252],font:24});
nativeTable(s,['Error','Meaning','Recovery'],[
 ['404','Missing prospect or lead','Use an existing ID'],['409','Company saved via another listing','Open that saved prospect'],['422','Invalid query or status body','Correct the input'],
],{y:444,h:190,widths:[150,530,472],font:24});

s=slide('Frontend behavior',['frontend'],'The UI now calls Overview the Sales dashboard, while its internal component remains OverviewPage/OverviewView. Saved leads supports queues and inline status selection. The explicit Mark contacted button is on the lead detail page and dashboard Call next list, not the saved-lead table. Network errors use action-specific fallback messages.',['frontend/app/page.tsx','frontend/app/prospects/page.tsx','frontend/app/prospects/[id]/page.tsx','frontend/app/leads/page.tsx','frontend/lib/useLoad.ts','frontend/lib/api.ts']);
nativeTable(s,['Concern','Current approach','Alternative / trade-off'],[
 ['Views','Dashboard, prospects, detail, saved leads','One giant page is harder to scan'],
 ['Filter state','URL query parameters','Local-only state loses shareable views'],
 ['Async reads','Abort + request sequence guard','Uncontrolled effects can show old results'],
 ['Mutations','Pending state, safe errors, server reconciliation','Optimism alone can display unsaved work'],
 ['Narrow screens','Compact lead cards below 768px','Wide tables force horizontal scanning'],
],{widths:[230,445,477],h:450,font:26});

s=slide('Dashboard KPI semantics',['frontend'],'Metrics are current state, not a historical conversion funnel. Directory is applied before the saved-lead summary. Other table filters affect matching total, not the status/queue summary population. Contact coverage includes qualified leads. Status age is not independently recorded last-call time.',['backend/app/services.py','backend/app/queries.py','frontend/app/page.tsx','frontend/app/leads/page.tsx']);
nativeTable(s,['Metric','Calculation / scope','Interpretation'],[
 ['Active saved','New + Contacted + Qualified','Exclude Dismissed'],
 ['Needs first contact','Status New','Current status, not call history'],
 ['Follow-up due','Contacted, unchanged for 14+ days','Time since status change'],
 ['Contact coverage','(Contacted + Qualified) / active','Current coverage, not conversion'],
 ['Summary vs matching','Selected directory; then table filters','Never count only the visible page'],
],{widths:[275,490,387],h:450,font:26});

s=slide('Reliability and trade-offs',['reliability'],'Constraints and transactions provide specific protections, but not a complete production guarantee. Startup create_all has an advisory lock but cannot migrate columns. The import commits source rows before score publication, so the whole ingest is not atomic. Current directory filtering is SQL, while remaining lead filters and aggregates operate on the loaded saved set.',['backend/app/db.py','backend/app/models.py','backend/app/collection/importer.py','backend/app/services.py']);
nativeTable(s,['Boundary','Current choice','Alternative','Limit / trigger'],[
 ['Identity','Unique keys + rollback','UI existence check','UI checks race between clients'],
 ['Schema','create_all + startup lock','Alembic','Cannot upgrade existing columns'],
 ['Saved queries','SQL directory; Python remaining filters','All SQL aggregation','Move when latency/memory grows'],
 ['Ingest','Upsert, then score','Atomic/staged publication','Separate commits permit partial state'],
 ['Slow work','No job queue or cache','Durable jobs / cache','Add only for an approved workload'],
],{widths:[195,330,280,347],h:460,font:24});
note(s,'Current worker pools allow up to 20 connections in total; this is not a capacity result.');

s=slide('Production extensibility: data',['extensibility'],'These are proposals mapped to existing boundaries. A new source reader still needs a clear reader/upsert interface because import_file currently calls load_snapshot directly. Per-territory distance needs a real model, not just another global distance field. Score changes need versioned semantics and regression examples.',['docs/operations/production-extensibility.md','backend/app/collection/importer.py','backend/app/collection/snapshot.py','backend/app/scoring.py']);
nativeTable(s,['Extension','Code boundary','Data / contract change','Proof before release'],[
 ['Approved source','collection reader / importer','Validated mapping and identity','Shape, empty/failure, duplicates'],
 ['Recurring refresh','Importer + scheduler','Complete ingest and freshness policy','Retry safe; lead status preserved'],
 ['New score rule','scoring.py + score table','Version and stored breakdown','Boundary examples; compatible UI'],
 ['New territory','Source + query + score model','Distance per territory/origin','Counts and distances match territory'],
],{widths:[225,275,330,322],h:450,font:24});
note(s,'Proposed work. Add a queue, cache, or service split only when a requirement justifies it.');

s=slide('Production extensibility: workflow',['extensibility'],'Ownership can change access and uniqueness semantics and is not automatically an additive API change. Status history belongs in the same transaction as the status update. Notes and insight remain deferred. AI insight would require validated sources, durable job state, bounded retries and cost/latency monitoring, while preserving the saved lead on failure.',['docs/operations/production-extensibility.md','docs/DECISION_LOG.md','additional/insights/README.md','backend/app/services.py','backend/app/models.py']);
nativeTable(s,['Extension','Affected boundary','Required change','Compatibility / limit'],[
 ['Login + ownership','Lead / API / query / session','Owner policy + access checks','May break shared-lead semantics'],
 ['Status history','update_status + event table','Status and event commit together','One event per real transition'],
 ['Notes','Lead service + UI','Note fields or history table','Deferred; approve behavior first'],
 ['AI insight','Disconnected draft + job state','Source validation, retries, cost bounds','Deferred; preserve saved work'],
],{widths:[245,300,315,292],h:450,font:24});
note(s,'All additions on this slide are proposed, not active product features.');

s=slide('Future work and rollout priorities',['future'],'Correctness now has a recorded local regression suite, so the next task is to keep that coverage and integrate checks into a release process. External use still requires access control, secure deployment and recoverable data. Shared editing needs conflict policy. Scale changes should follow measurement rather than adding infrastructure speculatively.',['docs/operations/production-readiness.md','docs/TEST_RESULTS.md','docs/operations/production-extensibility.md']);
nativeTable(s,['When','Work','Acceptance condition'],[
 ['Before release','Contract/regression checks in CI','API, UI and persistence checks run together'],
 ['Before external users','Access control, TLS, secrets, backup, migrations','Authorized access; tested restore and upgrade'],
 ['Before shared edits','Ownership + version/conflict policy','No silent overwrite of another rep’s work'],
 ['As operations need it','Request logs, metrics, alerts, ownership','Failures are diagnosable'],
 ['After measured growth','SQL aggregates, indexes, cursors, pool sizing','Measured latency/memory/connection need'],
],{widths:[260,470,422],h:455,font:25});
note(s,'Production proposals; no traffic target, SLO, or load capacity has been measured.');

s=slide('Testing: 106 recorded passes',['verification'],'The repository test report records a final local run on 5 November 2026: 106 passed, zero failed, zero skipped, about 21 seconds. This presentation task did not rerun that suite. The tests use marker-scoped rows in the demo database under D22 and report that 409 real prospects and the same two real leads remained. The category counts on screen sum to 106.',['docs/TEST_RESULTS.md','docs/TEST_PLAN.md','backend/tests/','docs/DECISION_LOG.md'], 'Recorded evidence from docs/TEST_RESULTS.md, not a new test run by this presentation task. Browser coverage is Chromium only. No load test, full accessibility audit, CI, or production restore proof.');
nativeTable(s,['Category','Tests','Reported coverage'],[
 ['Scoring','36','Weights, tiers, distance and freshness boundaries'],
 ['API contract / validation','31','Success/error shapes and invalid inputs'],
 ['Filters / pagination','11','Combinations, ordering and saved exclusion'],
 ['Save / duplicates','5','Repeated and competing saves'],
 ['Import','4','Upsert, partial input, preserve status'],
 ['Dashboard / follow-up','8','Counts, sort and time rules'],
 ['Persistence','1','Lead/status survive backend restart'],
 ['Chromium browser','10','Flow, recovery, keyboard and narrow layouts'],
],{widths:[360,125,667],h:470,font:24});
note(s,'Recorded run: 5 Nov 2026. Not rerun for this deck. Typecheck/build are separate checks.');

s=slide('Evidence boundaries and next checks',['verification'],'A successful local test run and static presentation checks do not establish production readiness. Manual GETs during this presentation task confirmed API health, 409 total prospects, and that the fixed distance filter now returns 200. The deck is rendered and structurally checked, but it is not claimed to have been opened in native PowerPoint.',['docs/TEST_RESULTS.md','docs/CODE_WALKTHROUGH.html','docs/operations/production-readiness.md']);
nativeTable(s,['Evidence','What it supports','What remains'],[
 ['Read-only API checks','Health 200; 409 listings; distance filter 200','Not every input or mutation rerun'],
 ['Recorded 106-test run','Local API/database and Chromium behavior','Other browsers; broad outage cases'],
 ['Frontend compile checks','Types and production bundle compile','Not proof of user behavior'],
 ['Current MVP boundary','Shared local workspace','Auth, ownership, restore and load targets'],
 ['Deck verification','Editable tables/diagram; rendered slides','Native PowerPoint behavior not checked'],
],{widths:[300,440,412],h:450,font:25});

if(deck.slides.items.length!==18)throw new Error('Unexpected slide count');
await fs.mkdir(path.dirname(FINAL),{recursive:true});
try{await fs.access(path.join(BUILD,'original-two-slide.pptx'));}catch{await fs.copyFile(path.join(ROOT,'docs/PROJECT_DEMO.pptx'),path.join(BUILD,'original-two-slide.pptx'));}
const candidate=path.join(BUILD,`candidate-${REV}.pptx`);
await (await PresentationFile.exportPptx(deck)).save(candidate);
await fs.mkdir(path.join(BUILD,`previews-${REV}`),{recursive:true});
for(let i=0;i<deck.slides.items.length;i++){
 const blob=await deck.export({slide:deck.slides.items[i],format:'png',scale:1.25});
 await fs.writeFile(path.join(BUILD,`previews-${REV}`,`slide-${i+1}.png`),new Uint8Array(await blob.arrayBuffer()));
}
await fs.writeFile(path.join(BUILD,'slide-map.json'),JSON.stringify(definitions,null,2));
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:FINAL,explicitTotalSlideCount:18,requiredNativeTableOwnerSlides:owners,requiredNativeChartOwnerSlides:[],pythonExecutable:'/Users/ananyauppal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...owners.flatMap(n=>['--require-native-table-slide',String(n)])],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,`validation-${REV}.json`)});
await fs.copyFile(FINAL,path.join(ROOT,'docs/PROJECT_DEMO.pptx'));
console.log(JSON.stringify({slides:18,finalPath:path.join(ROOT,'docs/PROJECT_DEMO.pptx'),package:result.packageIntegrity.status,layoutFindings:result.presentationLayout.finding_count,receipt:result.receiptPath},null,2));
