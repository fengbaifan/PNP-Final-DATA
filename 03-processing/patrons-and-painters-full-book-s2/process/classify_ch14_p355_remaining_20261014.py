import argparse,csv,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];T=ROOT/'04-knowledge/tables'
P={'st':T/'book-statements.jsonl','me':T/'mentions.csv','ca':T/'entity-candidates.csv'}
EXPECTED={'st':'a8b5e35db14cb9b552fbda5ec8fbe72c5c75716bc92e4be97177e760f7b13008','me':'9fff84f0c8d2efa6bb8c1a5a6372ab7476d6722678d20534646dfc62a840cc47','ca':'fdc7e06b9273df142198f4a4715c4b77db85bfab21b6681905018b8b38c4ad93'}
TAG='.bak-s2-ch14-p355-semantic-review-20261014'
parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
def sha(b):return hashlib.sha256(b).hexdigest()
before={k:p.read_bytes() for k,p in P.items()}
for k,b in before.items():
 if sha(b)!=EXPECTED[k]:raise SystemExit(f'unexpected pre-write hash {k}')
st=[json.loads(x) for x in before['st'].decode('utf-8-sig').splitlines() if x.strip()];by={r['statement_id']:r for r in st}
if len(by)!=len(st):raise SystemExit('duplicate statement IDs')
true_notes={
'st-chp14-p355-correctness-and-dilemma':'Haskell presents Algarotti’s attempt to reconcile Tiepolo’s vision with neo-classical correctness as part of a wider interpretive dilemma; retain the source’s qualification and do not promote the period-wide interpretation to an independently verified fact.',
'st-chp14-p355-algarotti-venetian-heritage':'The source explicitly says Algarotti recognized Venetian painting’s characteristic qualities in his most gifted contemporaries; the endpoint is now an unnamed group, not Venice as a place.',
'st-chp14-p355-piazzetta-isolated-classical-phase':'Haskell says the Venice-visit period marked an important but isolated career phase for Piazzetta. The subject is the painter; the endpoint is the p.355 visit event, whose date and identity relative to other visits remain open.',
'st-chp14-p355-piazzetta-classical-works':'Haskell says the lost Algarotti commission and two further classical history paintings comprised Piazzetta’s only such works; the open group preserves those works without assigning individual locations.',
'st-chp14-p355-collection-size':'Haskell reports that Algarotti eventually built the family collection to nearly 200 paintings and many drawings; retain the approximate count and the collection identity caveat.',
'st-chp14-p355-canaletto-intensively-employed-partial':'The p.356 continuation completes the p.355 sentence: Canaletto was still intensively employed by Consul Smith. The Bonomo report about completion time is separate and is not asserted as the employment relation.',
'st-chp14-p355-note2-mucius-after-commission':'Haskell’s note reports Pallucchini’s claim that Mucius Scaevola at the Altar was painted shortly after the Algarotti commission; keep the report chain and do not infer a location.',
'st-chp14-p355-note2-darius-after-commission':'Haskell’s note reports Pallucchini’s claim that The Death of Darius was painted shortly after the Algarotti commission; keep the report chain and do not infer a location.'}
false_notes={
'st-chp14-p355-inventory-limit':'This is an explicit limit on what the surviving inventory permits Haskell to conclude, not a directed relation or proof that no other evidence exists.',
'st-chp14-p355-note1-michelessi':'Citation locator only; it attributes the preceding report and identifies a bibliographic location, with no separate entity relation.',
'st-chp14-p355-note2-two-works-and-locations':'The note lists two paintings and two Venetian locations without pairing each work to a particular site; retain the source summary but do not manufacture individual location edges.',
'st-chp14-p355-note3-collection-references':'Bibliographic locator only; it identifies the cited Selva and Levey sources, while substantive collection and painting claims are recorded in separate statements.'}
for sid,note in {**true_notes,**false_notes}.items():
 if sid not in by or by[sid].get('qualifiers',{}).get('relation_candidate') is not None:raise SystemExit(f'unexpected p355 state: {sid}')
 q=by[sid].setdefault('qualifiers',{});q['relation_candidate']=sid in true_notes;q['relation_candidate_note']=note

def readcsv(key):
 with P[key].open(encoding='utf-8-sig',newline='') as f:d=csv.DictReader(f);return d.fieldnames,list(d)
cf,ca=readcsv('ca');mf,me=readcsv('me');cids={r['candidate_id'] for r in ca};mids={r['mention_id'] for r in me}
if len(cids)!=len(ca) or len(mids)!=len(me):raise SystemExit('duplicate IDs in tables')
if max(int(x.split('-')[1]) for x in cids)!=12198:raise SystemExit('candidate ID sequence changed')
newc=[
['cand-12199','','Gifted contemporaries in whom Algarotti recognized Venetian painting’s characteristic qualities (unnamed group, p.355)','','term','open','','',"Haskell says Algarotti recognized characteristic Venetian painting qualities in the most gifted of his contemporaries. Members are not named or enumerated; do not equate this group with the separate p.350 or p.353 artist groups without alignment.",'','body-mention','chp-14:14_CHP-14_intro:l85-95#L87'],
['cand-12200','','Algarotti’s Venice visit referred to on p.355 (date unresolved)','','event','open','','',"P.355 refers to ‘this visit to Venice’ and says the period was significant for Piazzetta and Tiepolo. The date and identity relative to Algarotti’s other Venetian visits are not specified; do not merge with the p.350 1737 visit candidate.",'','body-mention','chp-14:14_CHP-14_intro:l85-95#L89'],
['cand-12201','','Piazzetta’s three classical history paintings described on p.355 (one lost commission and two further works)','','work','open','','',"Haskell groups the lost Caesar and the Corsairs of Cilicia commission with two further paintings named in p.355 note 2, Mucius Scaevola at the Altar and The Death of Darius. The source says these were the only such classical works in Piazzetta’s oeuvre; individual locations are not assigned.",'','body-mention','chp-14:14_CHP-14_intro:l85-95#L90']]
if any(r[0] in cids for r in newc):raise SystemExit('new candidate ID already exists')
ca += [dict(zip(cf,r)) for r in newc];cids.update(r[0] for r in newc)
newm=[
['m-chp14-p355-0088','chp-14:14_CHP-14_intro:l85-95','cand-12199','the most gifted of his contemporaries','428','465','Unnamed group; source does not identify or enumerate its members.'],
['m-chp14-p355-0089','chp-14:14_CHP-14_intro:l85-95','cand-12200','this visit to Venice','994','1014','Source-referred visit; date and relation to earlier visits remain unresolved.'],
['m-chp14-p355-0090','chp-14:14_CHP-14_intro:l85-95','cand-12201','only such classical works','1601','1626','Work group includes the lost commission and two later paintings; no individual locations assigned.']]
if any(r[0] in mids for r in newm):raise SystemExit('new mention ID already exists')
me += [dict(zip(mf,r)) for r in newm]
# Correct p.355 Piazzetta person mentions that had been mapped to the work-index seed.
remapped=0
for r in me:
 if r['mention_id'].startswith('m-chp14-p355-') and r['candidate_id']=='cand-1909':r['candidate_id']='cand-1902';remapped+=1
if remapped!=9:raise SystemExit(f'unexpected Piazzetta mention remap count {remapped}')
for r in st:
 if r['statement_id'].startswith('st-chp14-p355-'):
  q=r.get('qualifiers',{});ids=q.get('mentioned_candidate_ids',[])
  if 'cand-1909' in ids:q['mentioned_candidate_ids']=list(dict.fromkeys('cand-1902' if x=='cand-1909' else x for x in ids))
# Correct the person endpoints and add source-defined objects.
r=by['st-chp14-p355-algarotti-venetian-heritage'];r['object_candidate_id']='cand-12199';r['qualifiers']['mentioned_candidate_ids']=list(dict.fromkeys(r['qualifiers'].get('mentioned_candidate_ids',[])+['cand-12199']))
r=by['st-chp14-p355-piazzetta-isolated-classical-phase'];r['subject_candidate_id']='cand-1902';r['object_candidate_id']='cand-12200';r['qualifiers']['mentioned_candidate_ids']=list(dict.fromkeys(r['qualifiers'].get('mentioned_candidate_ids',[])+['cand-12200']))
r=by['st-chp14-p355-piazzetta-classical-works'];r['subject_candidate_id']='cand-1902';r['object_candidate_id']='cand-12201';r['qualifiers']['mentioned_candidate_ids']=list(dict.fromkeys(r['qualifiers'].get('mentioned_candidate_ids',[])+['cand-12201']))
# Keep the cross-page claim narrow to the employment relation.
r=by['st-chp14-p355-canaletto-intensively-employed-partial'];q=r['qualifiers']
q['claim']='Haskell says Canaletto was still intensively employed by Consul Smith at this stage.'
q['qualification']='The p.356 continuation completes the phrase “still intensively employed by Consul Smith”. The Bonomo report about completion time is separate and does not define this employment relation.'
q['mentioned_candidate_ids']=['cand-0498','cand-2440']
q['cross_reference_segments']=['chp-14:14_CHP-14_intro:l97-105']
q['cross_reference_text']='p.356 L98 completes “still intensively employed by Consul Smith”.'
# Validate all newly anchored spans.
segments={json.loads(x)['segment_id']:json.loads(x) for x in (T/'segments.jsonl').read_text(encoding='utf-8-sig').splitlines() if x.strip()};texts={}
for m in newm:
 seg=segments[m[1]]
 if m[1] not in texts:
  lines=(ROOT/seg['source_file']).read_text(encoding='utf-8-sig').splitlines();texts[m[1]]='\n'.join(lines[int(seg['line_start'])-1:int(seg['line_end'])])
 if texts[m[1]][int(m[4]):int(m[5])]!=m[3]:raise SystemExit(f'source span mismatch {m[0]}')
# All p.355 statements including notes must be classified.
page=[r for r in st if r['statement_id'].startswith('st-chp14-p355-')]
from collections import Counter
counts=Counter(r.get('qualifiers',{}).get('relation_candidate') for r in page)
if len(page)!=27 or counts[True]!=22 or counts[False]!=5 or counts[None]!=0:raise SystemExit(f'unexpected p355 counts {len(page)} {counts}')
# Nested source/entity anchors are allowed; crossing or exact duplicate spans are not.
ints={}
for m in me:ints.setdefault(m['segment_id'],[]).append((int(m['start_char']),int(m['end_char']),m['mention_id']))
for sid,spans in ints.items():
 spans.sort()
 for i,a in enumerate(spans):
  for b in spans[i+1:]:
   if b[0]>=a[1]:break
   nested=(a[0]<=b[0] and b[1]<=a[1]) or (b[0]<=a[0] and a[1]<=b[1])
   if a[:2]==b[:2] or not nested:raise SystemExit(f'crossing mention spans {sid} {a[2]} / {b[2]}')
def csvout(fields,rows):
 from io import StringIO
 b=StringIO(newline='');w=csv.DictWriter(b,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows);return b.getvalue().encode('utf-8')
outputs={P['st']:('\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in st)+'\n').encode('utf-8'),P['me']:csvout(mf,me),P['ca']:csvout(cf,ca)}
print(json.dumps({'mode':'apply' if args.apply else 'dry-run','p355_counts':{'statements':len(page),'true':counts[True],'false':counts[False],'unset':counts[None]},'new_candidates':[r[0] for r in newc],'new_mentions':len(newm),'Piazzetta_person_mentions_remapped':remapped,'repaired_endpoints':['Algarotti contemporaries group','Piazzetta person -> Venice-visit event','Piazzetta person -> classical works group'],'new_spans_validated':len(newm),'crossings':0,'after_sha256':{str(p.relative_to(ROOT)):sha(b) for p,b in outputs.items()}},ensure_ascii=False,indent=2))
if args.apply:
 temps={}
 for path,data in outputs.items():
  backup=path.with_name(path.name+TAG);key=next(k for k,v in P.items() if v==path)
  if backup.exists():
   if sha(backup.read_bytes())!=EXPECTED[key]:raise SystemExit(f'backup differs: {backup.name}')
  else:shutil.copy2(path,backup)
  with tempfile.NamedTemporaryFile('wb',delete=False,dir=path.parent) as f:f.write(data);temps[path]=Path(f.name)
 for path,tmp in temps.items():tmp.replace(path)
 print(json.dumps({'written_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in outputs}}))
