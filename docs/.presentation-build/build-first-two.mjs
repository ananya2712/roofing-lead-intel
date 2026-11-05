import fs from 'node:fs/promises';
import path from 'node:path';
import { Presentation, PresentationFile } from '@oai/artifact-tool';
import { finalizePresentation, resolvePresentationFont } from '/Users/ananyauppal/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations/container_tools/artifact_tool_utils.mjs';

const workspaceDir = '/Users/ananyauppal/Desktop/Instalily Case Study/roofing-lead-intel';
const buildDir = path.join(workspaceDir, 'docs/.presentation-build');
const skillDir = '/Users/ananyauppal/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations';
const finalPath = path.join(buildDir, 'output/PROJECT_DEMO.pptx');
const FONT = resolvePresentationFont({fontFamily: 'Arial'});
const C = {navy:'#0E2A47', blue:'#2563EB', ink:'#19283B', muted:'#53657A', pale:'#EEF3F8', line:'#DCE3EB', white:'#FFFFFF'};
const deck = Presentation.create({slideSize:{width:1280,height:720}});

function text(slide, name, value, x,y,w,h,size=28,color=C.ink,bold=false) {
  const box = slide.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  box.text=value;
  box.text.style={fontFamily:FONT,typeface:FONT,fontSize:size,color,bold,verticalAlignment:'top',alignment:'left',insets:0,wrap:'word'};
  return box;
}

const s1=deck.slides.add();
s1.background.fill=C.white;
text(s1,'slide-1-title','Roofing Lead Intelligence',64,48,1152,78,56,C.navy,true);
text(s1,'slide-1-subtitle','Contractor prioritization for a roofing-materials distributor',66,134,1120,48,28,C.muted);
text(s1,'user-label','THE USER',66,230,650,26,18,C.blue,true);
text(s1,'user-description','A sales representative deciding which\ncontractors to contact next',66,268,710,85,30,C.ink);
text(s1,'problem-label','THE PROBLEM',66,383,650,26,18,C.blue,true);
text(s1,'problem-description','Directory listings provide facts.\nThe rep needs a prioritized call list.',66,421,710,85,30,C.ink);
text(s1,'outcome','Explain the priority. Save a lead. Track its status.',66,563,1130,54,29,C.navy,true);
text(s1,'prospect-count','176',858,237,350,142,112,C.blue,true);
text(s1,'prospect-count-label','residential prospects',863,389,330,45,27,C.navy,true);
text(s1,'territory','ZIP 10013\nWithin 50 miles',863,444,320,82,26,C.muted);
text(s1,'source','GAF residential snapshot, 5 November 2026',66,663,1110,28,18,C.muted);
text(s1,'page-number','01',1162,663,54,28,18,C.muted);
s1.speakerNotes.text=`SPEAKING SCRIPT
This project supports a sales representative at a roofing-materials distributor. The rep needs to decide which nearby roofing contractors to call. GAF provides listing facts, but the representative still needs to interpret those facts and keep track of saved prospects. The MVP turns that directory data into an explainable priority list and a small lead-status workflow.

SCENARIO
Imagine a rep starting work in the ZIP 10013 territory. They filter nearby prospects, inspect a contractor's score and missing fields, save the contractor, and track the status after contact. This is an illustrative scenario, not an observed customer interview. No time savings or sales uplift were measured.

SCOPE AND CURRENT EVIDENCE
The running API returned 176 residential prospects on 2026-11-05. The territory is ZIP 10013 within 50 miles. Commercial collection remains in progress, so 409 is not the imported count. The source is a recorded GAF snapshot, not a live GAF query on each user request. Retrieved timestamp returned by the API: 2026-11-05T19:07:47.766000Z.
The active MVP has Overview, Prospects, Saved leads, and Prospect details. Notes and AI insights are deferred. Login, outreach, CRM sync, and queues are outside the current scope.

SOURCES
docs/BUILD_PROGRESS.md: Goal, Current scope, M1-M4.
docs/DECISION_LOG.md: D1-D4, D7-D11, D17.
backend/app/scoring.py: score_prospect and tier_for.
frontend/app/prospects/page.tsx: ProspectsView.
frontend/app/page.tsx: OverviewPage.
additional/insights/README.md: deferred feature, disconnected draft.

VERIFICATION BOUNDARY
Read-only manual requests: GET http://localhost:5001/api/v1/health returned status ok. GET /api/v1/prospects/stats returned total 176, residential 176, high 130, medium 46. docker compose ps showed backend/frontend up and PostgreSQL healthy. This review did not run automated application tests, change lead data, restart services, or rehearse the browser flow. Browser tooling reported that its access host was unavailable. The existing progress record reports another contributor's browser save/status check. Do not present that as an independent check by this review.`;

const s2=deck.slides.add();
s2.background.fill=C.white;
text(s2,'slide-2-title','Demo: prioritize and save a lead',64,48,1152,76,50,C.navy,true);
text(s2,'slide-2-subtitle','A representative’s path through the MVP',66,133,1120,45,28,C.muted);
const steps=[
  ['01','Filter nearby prospects','Priority, distance and directory'],
  ['02','Explain the score','Source facts and missing data'],
  ['03','Save a contractor as a lead','One saved lead per company'],
  ['04','Track the next action','Update status and review Overview'],
];
steps.forEach(([n,title,body],i)=>{
  const y=220+i*95;
  text(s2,`step-${n}`,n,66,y,52,42,27,C.blue,true);
  text(s2,`step-${n}-title`,title,130,y,560,43,28,C.navy,true);
  text(s2,`step-${n}-detail`,body,130,y+43,560,35,23,C.muted);
});
text(s2,'example-label','EXAMPLE FROM THE LOCAL API',766,219,450,30,18,C.blue,true);
text(s2,'example-company','American Siding\nConstruction Corp',766,261,450,96,32,C.navy,true);
const vals=[['Location','Newark, NJ'],['Distance','6.5 mi'],['Priority','High, 95 / 100'],['Directory','Residential']];
const table=s2.tables.add({rows:4,columns:2,left:766,top:370,width:450,height:190,columnWidths:[175,275],values:vals});
table.borders.assign({style:'solid',fill:C.line,width:1});
for(let r=0;r<4;r++)for(let c=0;c<2;c++){
  const cell=table.getCell(r,c);
  cell.fill=C.white;
  cell.text.style={fontFamily:FONT,typeface:FONT,fontSize:25,color:c===0?C.muted:C.ink,bold:c===1};
}
text(s2,'score-limit','Priority follows fixed rules.\nIt does not prove buying intent.',766,580,450,66,22,C.muted);
const link=text(s2,'demo-link','Open the local app: localhost:3000/prospects',66,649,1040,38,23,C.blue);
link.text=[[{run:'Open the local app: localhost:3000/prospects',style:{underline:'sng'},link:{uri:'http://localhost:3000/prospects',isExternal:true}}]];
text(s2,'slide-2-number','02',1162,663,54,28,18,C.muted);
s2.speakerNotes.text=`DEMO SCRIPT
1. Open http://localhost:3000/prospects. Explain that these are recorded GAF facts. Filter by priority and distance. The score is a ranking under selected rules, not a probability of purchase.
2. Open a prospect and show Source facts, Why this priority, and What we don't know. The API example in this slide is American Siding Construction Corp, prospect 145, Newark NJ, 6.5 miles, score 95. The example already had a saved lead when read. Choose an unsaved prospect for a fresh-save demonstration rather than resetting this row.
3. Save the selected prospect. The intended result is one saved company with status New. Show the Saved leads view. Company identity uses normalized ten-digit phone numbers when available. The database enforces unique non-null company keys; missing company keys require care and do not establish global company uniqueness.
4. Change its status to Contacted. Return to Overview and show Call next and Follow up. Follow up means Contacted with no status change for at least 14 days. Do not manufacture an aged record for this deck.

SCORING CONTEXT
backend/app/scoring.py defines distance 35, certification 20, roof systems 10, specialty 5, phone 10, website 10, address 5, and freshness 5. High starts at 70. Missing data receives zero points and an unknown flag. Ratings and reviews do not contribute. Saving does not add score points. The score is not evidence of purchase intent, revenue, business size, or a known decision-maker.

CURRENT SCOPE
Notes and AI insight are deferred. Do not demonstrate them or promise a retry-insight workflow. Commercial import is incomplete. This slide is a demo agenda supported by inspected code and API data, not a recording of a browser walkthrough.

SOURCES
GET http://localhost:5001/api/v1/prospects?page_size=1, manually read 2026-11-05: id 145, name American Siding Construction Corp, city Newark, state NJ, distance_mi 6.5, score 95, tier high, directory residential, saved_lead_id 1.
frontend/app/prospects/page.tsx: ProspectsView, filters and SaveButton.
frontend/app/prospects/[id]/page.tsx: ProspectPage, score/source/unknown sections.
frontend/components/leads/SaveButton.tsx.
frontend/components/leads/StatusSelect.tsx.
frontend/app/leads/page.tsx: LeadsView.
frontend/app/page.tsx: OverviewPage.
backend/app/api/__init__.py: list_prospects, get_prospect, save_prospect, update_status.
backend/app/services.py: save_prospect, update_status, overview.
backend/app/models.py: Lead uniqueness constraints.
docs/DECISION_LOG.md and additional/insights/README.md: deferred scope.

PRESENTATION LIMITS
The supplied notebook specifies Project/problem followed by Demo. These two draft slides follow that order instead of the repository skill's default seven-slide order. The external Google Slides reference could not be accessed. Browser tooling was unavailable, so no product screenshot or independent browser rehearsal is included. The link targets a running local app and requires Docker services to remain available. Automated application tests were not run, consistent with D17.`;

await fs.mkdir(buildDir,{recursive:true});
await fs.mkdir(path.dirname(finalPath),{recursive:true});
const candidatePath=path.join(buildDir,'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
for(let i=0;i<deck.slides.items.length;i++){
  const slide=deck.slides.items[i];
  const png=await deck.export({slide,format:'png',scale:1.5});
  await fs.writeFile(path.join(buildDir,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const report=await finalizePresentation({
  workspaceDir,candidatePath,finalPath,
  explicitTotalSlideCount:2,
  requiredNativeTableOwnerSlides:[2],requiredNativeChartOwnerSlides:[],
  pythonExecutable:'/Users/ananyauppal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
  integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','2'],
  fontPolicy:{basis:'design',families:[FONT]},
  verifyArtifactToolImport:true,
  receiptPath:path.join(buildDir,'PROJECT_DEMO.validation.json'),
});
console.log(JSON.stringify(report,null,2));
await fs.copyFile(finalPath,path.join(workspaceDir,'docs/PROJECT_DEMO.pptx'));
