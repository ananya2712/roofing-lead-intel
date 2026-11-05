from pathlib import Path
from html.parser import HTMLParser
import json,hashlib

root=Path(__file__).resolve().parents[3]
path=root/'docs/CODE_WALKTHROUGH.html'
class Source(HTMLParser):
    def __init__(self):super().__init__();self.sections={};self.section=None;self.cell=None;self.row=None;self.table=None;self.skip=0
    def handle_starttag(self,t,a):
        a=dict(a)
        if t=='section':self.section=a.get('id');self.sections[self.section]=[]
        if t=='svg':self.skip+=1
        if self.skip:return
        if t=='table' and self.section:self.table=[]
        if t=='tr' and self.table is not None:self.row=[]
        if t in ('td','th') and self.row is not None:self.cell=[]
    def handle_endtag(self,t):
        if t=='svg':self.skip-=1;return
        if self.skip:return
        if t in ('td','th') and self.cell is not None:self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        if t=='tr' and self.row is not None:self.table.append(self.row);self.row=None
        if t=='table' and self.table is not None:self.sections[self.section].append(self.table);self.table=None
        if t=='section':self.section=None
    def handle_data(self,d):
        if not self.skip and self.cell is not None:self.cell.append(d)
p=Source();p.feed(path.read_text())
out=Path(__file__).parent/'source.json'
out.write_text(json.dumps({'htmlPath':str(path),'htmlSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sections':p.sections},indent=2))
print('Extracted HTML tables:',len(p.sections),'sections')
