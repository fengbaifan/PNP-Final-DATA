"""Complete p.326 recovery after the staged candidate/mention replacement succeeded."""
from __future__ import annotations
import argparse,csv,hashlib,json,os,tempfile
from pathlib import Path
from io import StringIO
ROOT=Path(__file__).resolve().parents[3]; T=ROOT/'04-knowledge/tables'
CAND=T/'entity-candidates.csv'; MENT=T/'mentions.csv'; STMT=T/'book-statements.jsonl'; COV=T/'s2-coverage.csv'; STAGE=T/'tmp84a4c1jb'
EXPECT={CAND:'4e3e71204430eed09fa9dd7f829e557ccb2f0db052bdcda4e585b8f2ead67ec3',MENT:'59bab77f9aae299fa0d4479c02f4bf06009aeacaffa9747f009cb61031beaff9',STMT:'fab299fa3fcb47285639a5b7dfb5a992dc5084bfcfe43d0ad214a2408d485571',COV:'bc8265a5ef93304ab6ea6e9b501154b9d63420b1dcab79ba7055ac4896679668'}
BACKUP_SUFFIX='.bak-s2-chp10-p326-semantic-reconciliation-20261014'
for p,want in EXPECT.items():
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 if got!=want: raise SystemExit(f'current state changed: {p.relative_to(ROOT)} {got}')
 b=Path(str(p)+BACKUP_SUFFIX)
 if not b.exists(): raise SystemExit(f'missing recovery backup: {b.name}')
if not STAGE.exists(): raise SystemExit('prepared statement file is missing')
staged=[json.loads(x) for x in STAGE.read_text(encoding='utf-8').splitlines() if x.strip()]
if len(staged)!=14854 or len({r['statement_id'] for r in staged})!=14854: raise SystemExit('staged statement file failed row/ID checks')
needed={'st-chp10-p326-gozzi-authored-tribute','st-chp10-p326-pisani-received-some-support','st-chp10-p326-misunderstanding-explanation','st-chp10-p326-inquisitors-reason-for-suspicion','st-chp10-p326-montesquieu-works-controversial','st-chp10-p326-pictures-possibly-displayed-by-pisani-advisers','st-chp10-p326-riviera-issued-explanatory-pamphlet'}
if not needed.issubset({r['statement_id'] for r in staged}): raise SystemExit('staged statements missing expected splits')
with COV.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f); fields=list(reader.fieldnames); rows=list(reader)
cov=next((r for r in rows if r['segment_id']=='chp-10:10_CHP-10_sec_ii:l210-222'),None)
if not cov or '2026-10-14 semantic review against CHP-10.pdf physical p.59' in cov['note']: raise SystemExit('coverage state changed')
cov['note']+=" 2026-10-14 semantic review against CHP-10.pdf physical p.59 classified the 15 previously unset p.326 statements and split bundled claims for Gozzi's tribute, Pisani's support/surveillance, the authority episode, Montesquieu reception, Inquisitors' suspicion, display-agent alternatives, and Riviera's engravings/pamphlet. Added four source-local candidates for unnamed friends, advisers, the cited pamphlet set, and the unidentified Montesquieu writings; the source does not resolve print authorship or the display agents."
out=StringIO(); w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(rows)
with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=T,delete=False) as f: f.write(out.getvalue()); cov_stage=Path(f.name)
print(json.dumps({'candidate_rows':12094,'mention_rows':20087,'staged_statements':len(staged),'coverage_update':cov['segment_id'],'statement_stage':STAGE.name,'coverage_stage':cov_stage.name},indent=2))
parser=argparse.ArgumentParser(); parser.add_argument('--apply',action='store_true'); apply=parser.parse_args().apply
if apply:
 try:
  os.replace(STAGE,STMT)
  os.replace(cov_stage,COV)
 except Exception:
  print('APPLY INCOMPLETE; recovery backups retained; statement/coverage stages:',STAGE.exists(),cov_stage.exists())
  raise
 print('APPLIED; pre-write recovery backups retained')
