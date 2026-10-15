"""Assign the new p.325 mention the next free source-local identifier."""
import argparse,csv,hashlib,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'04-knowledge/tables/mentions.csv'
EXPECTED='4a0f28933bd4b45f73709b53d04ae37ead1b52418847ed0e54053ed6901e38e1'
OLD='m-s2-ch10-p325-0033'; NEW='m-s2-ch10-p325-0054'
SUFFIX='.bak-s2-chp10-p325-mention-id-repair-20261014'
actual=hashlib.sha256(P.read_bytes()).hexdigest()
if actual!=EXPECTED: raise SystemExit(f'input changed: {actual}')
with P.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f); fields=list(rd.fieldnames); rows=list(rd)
target=[r for r in rows if r.get('mention_id')==OLD and r.get('segment_id')=='chp-10:10_CHP-10_sec_ii:l203-208' and r.get('candidate_id')=='cand-1650']
if len(target)!=1 or any(r.get('mention_id')==NEW for r in rows): raise SystemExit('mention id state changed')
target[0]['mention_id']=NEW
print(f'{OLD} -> {NEW}; target_count={len(target)}')
args=argparse.ArgumentParser(); args.add_argument('--apply',action='store_true'); apply=args.parse_args().apply
if apply:
 b=Path(str(P)+SUFFIX)
 if b.exists(): raise SystemExit('backup exists; inspect before retrying')
 shutil.copy2(P,b)
 with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=P.parent,delete=False) as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(rows); tmp=Path(f.name)
 tmp.replace(P)
 print('APPLIED; backup='+str(b.relative_to(ROOT)))
