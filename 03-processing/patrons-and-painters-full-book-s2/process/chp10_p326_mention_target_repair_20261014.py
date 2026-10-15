"""Repair duplicate p.326 adviser mention by correcting its existing semantic target."""
import argparse,csv,hashlib,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'04-knowledge/tables/mentions.csv'
EXPECTED='59bab77f9aae299fa0d4479c02f4bf06009aeacaffa9747f009cb61031beaff9'
SUFFIX='.bak-s2-chp10-p326-mention-target-repair-20261014'
if hashlib.sha256(P.read_bytes()).hexdigest()!=EXPECTED: raise SystemExit('mentions table changed')
with P.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f); fields=list(rd.fieldnames); rows=list(rd)
old=next((r for r in rows if r['mention_id']=='m-s2-ch10-p326-327-0020'),None)
dup=[r for r in rows if r['mention_id']=='m-s2-ch10-p326-327-0084']
if not old or old['candidate_id']!='cand-1942' or len(dup)!=1 or dup[0]['candidate_id']!='cand-12113': raise SystemExit('expected duplicate mention state not found')
old['candidate_id']='cand-12113'; old['note']='Haskell names Pisani\'s advisers as an unnamed alternative group that may have displayed the pictures; do not map this phrase to Pisani himself.'
rows=[r for r in rows if r['mention_id']!='m-s2-ch10-p326-327-0084']
print('Reassigned existing adviser mention to cand-12113; removed duplicate mention row.')
args=argparse.ArgumentParser(); args.add_argument('--apply',action='store_true'); apply=args.parse_args().apply
if apply:
 b=Path(str(P)+SUFFIX)
 if b.exists(): raise SystemExit('repair backup exists')
 shutil.copy2(P,b)
 with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=P.parent,delete=False) as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(rows); tmp=Path(f.name)
 tmp.replace(P)
 print('APPLIED; backup='+str(b.relative_to(ROOT)))
