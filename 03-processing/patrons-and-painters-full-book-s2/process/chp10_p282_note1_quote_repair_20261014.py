"""Preserve OCR source quote while keeping scan correction in structured evidence."""
from __future__ import annotations
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TABLES=ROOT/'04-knowledge/tables'
SOURCE=ROOT/'02-sources/02-Markdown/10_CHP-10_intro.md'
STATEMENTS=TABLES/'book-statements.jsonl'
COVERAGE=TABLES/'s2-coverage.csv'
TARGET='st-chp10-notes-p282n1-portrait-patronage-account'
SEGMENT='chp-10:10_CHP-10_intro:l491-634'
EXPECTED={STATEMENTS:'156273c88cbdff04d1ab60f446a7b1635ee42a898b6d9f79e9611f1f83968a74',COVERAGE:'5bb0cb4e31b8235f8af69d66c8d4fab21067e7cf4a2e625a3b70563d63e8d166'}
SUFFIX='.bak-s2-chp10-p282-note1-quote-repair-20261014'
for path,want in EXPECTED.items():
 got=hashlib.sha256(path.read_bytes()).hexdigest()
 if got!=want: raise SystemExit(f'input changed: {path.relative_to(ROOT)} {got}')
rows=[json.loads(x) for x in STATEMENTS.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
with COVERAGE.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f); fields=list(reader.fieldnames); coverage=list(reader)
row=next((x for x in rows if x['statement_id']==TARGET),None)
if not row or row['segment_id']!=SEGMENT or row['qualifiers'].get('relation_candidate') is not False: raise SystemExit('target state changed')
source_lines=SOURCE.read_text(encoding='utf-8').splitlines()
source_line=source_lines[519]
start=source_line.index('Le Portrait du Vrai ')
end=source_line.index(' of Johann Wilhelm’s patronage')+len(' of Johann Wilhelm’s patronage')
quote=source_line[start:end]
if 'hill account' not in quote: raise SystemExit('OCR quote anchor not found')
row['original_quote']=quote
q=row['qualifiers']
if not any(x.get('ocr')=='hill' and x.get('print')=='full' for x in q.get('ocr_corrections',[])): raise SystemExit('structured OCR correction missing')
cov=next((x for x in coverage if x['segment_id']==SEGMENT),None)
old="Corrected the quoted OCR 'hill' to printed 'full'."
new="Recorded OCR 'hill' as printed 'full' in ocr_corrections; original_quote preserves the source transcription."
if not cov or old not in cov['note']: raise SystemExit('expected coverage note not found')
cov['note']=cov['note'].replace(old,new)
print(json.dumps({'target':TARGET,'original_quote':quote,'coverage_note_correction':new},ensure_ascii=True,indent=2))
def write(path, content):
 with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=path.parent,delete=False) as f:
  f.write(content); tmp=Path(f.name)
 tmp.replace(path)
args=argparse.ArgumentParser(); args.add_argument('--apply',action='store_true'); apply=args.parse_args().apply
if apply:
 paths=[STATEMENTS,COVERAGE]; backups=[Path(str(x)+SUFFIX) for x in paths]
 if any(x.exists() for x in backups): raise SystemExit('backup exists; inspect before retrying')
 for x,b in zip(paths,backups): shutil.copy2(x,b)
 try:
  write(STATEMENTS,''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in rows))
  from io import StringIO
  out=StringIO(); writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore',lineterminator='\n'); writer.writeheader(); writer.writerows(coverage); write(COVERAGE,out.getvalue())
 except Exception:
  for x,b in zip(paths,backups): shutil.copy2(b,x)
  raise
 print('APPLIED; backups='+', '.join(str(x.relative_to(ROOT)) for x in backups))
