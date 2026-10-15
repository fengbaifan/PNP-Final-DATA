"""Reconcile p.325 statements and link Memmo's cross-referenced plan."""
from __future__ import annotations
import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
from io import StringIO
ROOT=Path(__file__).resolve().parents[3]
T=ROOT/'04-knowledge/tables'
SOURCE=ROOT/'02-sources/02-Markdown/10_CHP-10_sec_ii.md'
STATEMENTS=T/'book-statements.jsonl'; MENTIONS=T/'mentions.csv'; COVERAGE=T/'s2-coverage.csv'
SEGMENT='chp-10:10_CHP-10_sec_ii:l203-208'
EXPECTED={STATEMENTS:'48781aa4d355f55eed6aaf4a7ceeae4c7a39313eb8b19372c8b53597404053ef',MENTIONS:'a728398c57654683f42c929a233de9fe3cda2c1c670e09f1e53a4d82524af53f',COVERAGE:'80c9d12a54981eb72bc315b0ef423fe7f44da7c3c7541da295e5e5aecd262f03'}
SUFFIX='.bak-s2-chp10-p325-semantic-reconciliation-20261014'
for p,want in EXPECTED.items():
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 if got!=want: raise SystemExit(f'input changed: {p.relative_to(ROOT)} {got}')
rows=[json.loads(x) for x in STATEMENTS.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
with MENTIONS.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f); mention_fields=list(rd.fieldnames); mentions=list(rd)
with COVERAGE.open(encoding='utf-8-sig',newline='') as f:
 rd=csv.DictReader(f); coverage_fields=list(rd.fieldnames); coverage=list(rd)
byid={r['statement_id']:r for r in rows}
open_rows=[r for r in rows if r.get('segment_id')==SEGMENT and (r.get('qualifiers') or {}).get('relation_candidate') is None]
expected_open={
'st-chp10-p325-gian-domenico-most-influenced-by-social-ideas',
'st-chp10-p325-jibe-and-pictures-anticipate-millet',
'st-chp10-p325-valmarana-scenes-do-not-match-fable-programme',
'st-chp10-p325-valmarana-scenes-realistic-and-sympathetic',
'st-chp10-p325-gozzi-letter-advocates-public-virtue-images',
'st-chp10-p325-gozzi-public-display-idea-described-as-new',
'st-chp10-p325-gozzi-returned-to-didactic-painting',
'st-chp10-p325-haskell-says-memmo-implemented-similar-padua-scheme',
'st-chp10-p325-maggiotto-flemish-mockery-undermines-labor-dignity',
'st-chp10-p325-maggiotto-oscillates-between-longhi-and-zompini',
'st-chp10-p325-pisani-proposes-return-to-sacred-laws',
'st-chp10-p325-pisani-querini-opposition-sentence-continues',
'st-chp10-p325-pisani-reforms-favor-self-and-friends',
'st-chp10-p325-pisani-seen-as-temporary-advanced-figure'}
if {r['statement_id'] for r in open_rows}!=expected_open: raise SystemExit('p.325 unclassified set changed')
for r in open_rows: r['qualifiers']['relation_candidate']=False
memmo=byid['st-chp10-p325-haskell-says-memmo-implemented-similar-padua-scheme']
memmo['object_candidate_id']='cand-1650'
q=memmo['qualifiers']; q['relation_candidate']=True
q['claim']="Haskell says Andrea Memmo was putting a similar scheme into effect in Padua in 1782; note 3 directs readers to Chapter 15, where the related Prà della Valle plan is described."
q['qualification']="The p.325 cross-reference supports mapping the scheme to candidate cand-1650, Memmo's Prà della Valle plan. The 1782 implementation date is preserved as Haskell states it; Chapter 15 describes the plan's earlier conception and continuing execution. Haskell's 'must have been aware' remains an inference, not independent corroboration."
q['mentioned_candidate_ids']=list(dict.fromkeys(q.get('mentioned_candidate_ids',[])+['cand-1650']))
mag=byid['st-chp10-p325-maggiotto-flemish-mockery-undermines-labor-dignity']
mag['qualifiers']['relation_candidate']=True
mag['qualifiers']['qualification']="Haskell explicitly says Maggiotto's peasant scenes revert to the Flemish tradition of mockery; this supports a source-level association with the named tradition, without identifying specific model works or artists. The assessment of labour dignity remains Haskell's evaluation."
# Add the previously unrecorded p.325 mention of the work candidate cand-1650.
source_lines=SOURCE.read_text(encoding='utf-8').splitlines()
segment_text='\n'.join(source_lines[202:208])
surface='scheme very similar to the one he was calling for'
start=segment_text.index(surface); end=start+len(surface)
if start!=2136: raise SystemExit(f'unexpected mention offset {start}')
if any(m['segment_id']==SEGMENT and m['candidate_id']=='cand-1650' for m in mentions): raise SystemExit('candidate mention already exists')
mention={'mention_id':'m-s2-ch10-p325-0033','segment_id':SEGMENT,'candidate_id':'cand-1650','surface_form':surface,'start_char':str(start),'end_char':str(end),'note':'The p.325 note 3 points to Chapter 15, which describes the related Prà della Valle plan; this identifies the contextual referent without altering the source wording.'}
mentions.append(mention)
cov=next((r for r in coverage if r['segment_id']==SEGMENT),None)
if not cov or (cov['disposition'],cov['migration_status'])!=('reviewed','complete'): raise SystemExit('coverage state changed')
review_note=" 2026-10-14 semantic reconciliation against CHP-10.pdf physical p.58 classified 14 previously unset claims: 2 relation candidates (Maggiotto's return to Flemish mockery tradition; Memmo's Padua scheme linked by note 3 to the Prà della Valle plan cand-1650) and 12 non-relational claims. Preserved p.325's 1782 implementation statement and Chapter 15's account of earlier planning."
cov['note']+=review_note
print(json.dumps({'segment':SEGMENT,'classified':len(open_rows),'relation_candidates':[memmo['statement_id'],mag['statement_id']],'non_relational_count':12,'added_mention':mention},ensure_ascii=True,indent=2))
def replace(path,text):
 with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=path.parent,delete=False) as f:
  f.write(text); tmp=Path(f.name)
 tmp.replace(path)
def apply():
 files=[STATEMENTS,MENTIONS,COVERAGE]; backups=[Path(str(p)+SUFFIX) for p in files]
 if any(b.exists() for b in backups): raise SystemExit('recovery backup exists; inspect before retrying')
 for p,b in zip(files,backups): shutil.copy2(p,b)
 try:
  replace(STATEMENTS,''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows))
  out=StringIO(); w=csv.DictWriter(out,fieldnames=mention_fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(mentions); replace(MENTIONS,out.getvalue())
  out=StringIO(); w=csv.DictWriter(out,fieldnames=coverage_fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(coverage); replace(COVERAGE,out.getvalue())
 except Exception:
  for p,b in zip(files,backups): shutil.copy2(b,p)
  raise
 print('APPLIED; backups='+', '.join(str(b.relative_to(ROOT)) for b in backups))
parser=argparse.ArgumentParser(); parser.add_argument('--apply',action='store_true'); args=parser.parse_args()
if args.apply: apply()
