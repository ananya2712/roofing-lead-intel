// Shared content for the editable PowerPoint diagram and offline SVG.
export const nodes = [
  ['1 · React', 'Open / filter\nor save'],
  ['2 · Client', 'Typed GET\nor POST'],
  ['3 · Proxy', 'Next.js\n/api/v1 rewrite'],
  ['4 · Route', 'Path / query /\nbody checks'],
  ['5 · Rules', 'Read / save\nbusiness logic'],
  ['6 · ORM', 'Select / join\nor add Lead'],
  ['7 · DB', 'SQL / commit\nconstraints'],
  ['8 · Reload', 'Save only:\nexpire_all()'],
  ['9 · Model', 'Pydantic\nresponse'],
  ['10 · JSON', '_json() +\njsonify()'],
  ['11 · Client', 'unwrap() /\nsafe errors'],
  ['12 · UI', 'Save: refetch\nlist + stats'],
];
export const importHeaders = ['A · Snapshot', 'B · CLI', 'C · Validate', 'D · Upsert', 'E · Score', 'F · Persist'];
export const importValues = ['GAF JSON', 'CLI import', 'Normalize', 'Source facts', 'Imported IDs', 'Score version'];
const xFor = i => 64 + (i < 6 ? i : 11-i) * 196;
const yFor = i => i < 6 ? 167 : 350;

export function drawArchitecture(slide,{text,nativeTable,FONT,C}){
  text(slide,'request-lane','REQUEST · Browser / Next.js / Flask',64,126,1152,31,24,C.blue,true);
  text(slide,'response-lane','RESPONSE · Database state back to the UI',64,307,1000,31,24,C.green,true);
  const boxes=nodes.map(([title,body],i)=>{
    const x=xFor(i),y=yFor(i),db=i===6;
    const b=slide.shapes.add({geometry:'rect',name:`architecture-step-${i+1}`,position:{left:x,top:y,width:172,height:116},fill:db?'#EAF5EF':C.soft,line:{fill:db?C.green:C.line,width:1}});
    text(slide,`architecture-title-${i+1}`,title,x+10,y+12,152,33,26,db?C.green:C.navy,true);
    text(slide,`architecture-detail-${i+1}`,body,x+10,y+54,152,58,24,C.ink);
    return b;
  });
  for(let i=0;i<11;i++)slide.shapes.connect(boxes[i],boxes[i+1],{
    kind:'straight',fromSide:i===5?'bottom':i<5?'right':'left',toSide:i===5?'top':i<5?'left':'right',
    line:{fill:i<6?C.blue:C.green,width:2},tail:{type:'triangle',width:'sm',length:'sm'},
  });
  text(slide,'setup-lane','SETUP ONLY · Explicit CLI, separate from page and save requests',64,490,1152,32,24,C.muted,true);
  nativeTable(slide,importHeaders,[importValues],{y:532,h:88,widths:[192,192,192,192,192,192],font:24});
  text(slide,'architecture-errors','Errors: 422 input · 404 missing · commit conflict: rollback, then 200 or 409. No live GAF/AI call.',64,638,1152,28,21,C.muted);
}

const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
export function architectureSvg(){
  const labels=(str,x,y,size,color,bold=false)=>str.split('\n').map((v,j)=>`<text x="${x}" y="${y+j*28}" font-size="${size}" fill="${color}"${bold?' font-weight="700"':''}>${esc(v)}</text>`).join('');
  const n=nodes.map(([title,body],i)=>{const x=xFor(i),y=yFor(i);return `<g id="step-${i+1}"><rect x="${x}" y="${y}" width="172" height="116" fill="${i===6?'#EAF5EF':'#F5F7FA'}" stroke="${i===6?'#16734D':'#DCE3EC'}"/>${labels(title,x+10,y+36,26,'#0E2A47',true)}${labels(body,x+10,y+77,24,'#172B42')}</g>`;}).join('');
  const arrows=nodes.slice(0,-1).map((_,i)=>{
    const x=xFor(i),y=yFor(i),right=i<5,down=i===5,color=i<6?'#2157A4':'#16734D';
    const ex=down?x+86:right?x+196:x-24,ey=down?350:y+58;
    const head=down?`${ex},${ey} ${ex-5},${ey-9} ${ex+5},${ey-9}`:right?`${ex},${ey} ${ex-9},${ey-5} ${ex-9},${ey+5}`:`${ex},${ey} ${ex+9},${ey-5} ${ex+9},${ey+5}`;
    return `<path d="M ${down?x+86:right?x+172:x} ${down?y+116:y+58} L ${ex} ${ey}" fill="none" stroke="${color}" stroke-width="2"/><polygon points="${head}" fill="${color}"/>`;
  }).join('');
  const table=importHeaders.map((v,i)=>`<rect x="${64+i*192}" y="532" width="192" height="44" fill="#F5F7FA" stroke="#DCE3EC"/><rect x="${64+i*192}" y="576" width="192" height="44" fill="#FFFFFF" stroke="#DCE3EC"/>${labels(v,74+i*192,562,24,'#0E2A47',true)}${labels(importValues[i],74+i*192,606,24,'#172B42')}`).join('');
  return `<svg id="request-flow" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 690" role="img" aria-labelledby="request-title request-desc"><title id="request-title">Architecture and detailed request flow</title><desc id="request-desc">Twelve ordered runtime steps through UI, typed client, Next.js proxy, route validation, service logic, ORM, PostgreSQL, saved-state reload, response model, JSON, error handling and UI refresh. Six separate setup steps import and score recorded snapshots.</desc><defs><marker id="blue" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#2157A4"/></marker><marker id="green" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#16734D"/></marker></defs><rect width="1280" height="690" fill="#FFFFFF"/><g font-family="Arial, sans-serif">${labels('Architecture and data flow',64,90,48,'#0E2A47',true)}${labels('REQUEST · Browser / Next.js / Flask',64,150,24,'#2157A4',true)}${labels('RESPONSE · Database state back to the UI',64,331,24,'#16734D',true)}${arrows}${n}${labels('SETUP ONLY · Explicit CLI, separate from page and save requests',64,514,24,'#53667A',true)}${table}${labels('Errors: 422 input · 404 missing · commit conflict: rollback, then 200 or 409. No live GAF/AI call.',64,660,21,'#53667A')}</g></svg>`;
}
