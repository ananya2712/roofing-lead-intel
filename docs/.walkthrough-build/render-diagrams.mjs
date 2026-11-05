import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const req=createRequire('/Users/ananyauppal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/__runtime__.cjs');
const sharp=req('sharp');
const html=await fs.readFile(new URL('../CODE_WALKTHROUGH.html',import.meta.url),'utf8');
const svgs=[...html.matchAll(/<svg\b[\s\S]*?<\/svg>/g)].map(m=>m[0]);
const out=new URL('./diagrams/',import.meta.url);
await fs.mkdir(out,{recursive:true});
for(let i=0;i<svgs.length;i++){
  const svg=svgs[i].replace('<svg ','<svg style="font-family:Arial;fill:#172b42" ');
  await sharp(Buffer.from(svg)).flatten({background:'#fff'}).png().toFile(fileURLToPath(new URL(`diagram-${i+1}.png`,out)));
}
console.log(`Rendered ${svgs.length} embedded diagrams for document review.`);
