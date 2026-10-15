import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
T = ROOT / '04-knowledge' / 'tables'
P = {'st': T/'book-statements.jsonl', 'me': T/'mentions.csv', 'ca': T/'entity-candidates.csv'}
EXPECTED = {
 'st':'7d586d6236f305948ff2ef611ec46f3c198d1475ff81f611c49412e9fa5bf988',
 'me':'49468200f15c5e32b70894ae6d06d0eae797b801e4a93786801e4376e1d8541d',
 'ca':'90039a8ead746821426cd896b9a580f07b8e3d8913f14a6a0db5d05c470953cf'}
TAG='.bak-s2-ch14-p354-reconcile-20261014'
parser=argparse.ArgumentParser(); parser.add_argument('--apply',action='store_true'); args=parser.parse_args()
def sha(b): return hashlib.sha256(b).hexdigest()
before={k:p.read_bytes() for k,p in P.items()}
for k,b in before.items():
 if sha(b)!=EXPECTED[k]: raise SystemExit(f'unexpected pre-write hash: {k}')
statements=[json.loads(x) for x in before['st'].decode('utf-8-sig').splitlines() if x.strip()]
byid={r['statement_id']:r for r in statements}
if len(byid)!=len(statements): raise SystemExit('duplicate statement ids')
true_notes={
'st-chp14-p354-banquet-classicism-and-accuracy':'Haskell attributes Algarotti’s stated classicism and accuracy priorities to the Banquet scenes; preserve this as a source-reported reception/selection relation without assigning individual scene details beyond the source.',
'st-chp14-p354-bruhl-pictures-for-patrons-in-saxony':'The source explicitly says the preceding pictures were ordered for Algarotti’s unnamed important patrons in Saxony. The endpoint is now the unnamed group; Saxony remains location context, with no one-to-one recipient mapping.',
'st-chp14-p354-bath-of-diana-boucher-style':'Haskell describes the painting as following a style Boucher had made fashionable in Paris. Record the source-attributed stylistic association; do not infer direct contact between Boucher and Tiepolo.',
'st-chp14-p354-bath-of-diana-reflects-algarotti-tastes':'Haskell explicitly interprets the painting as reflecting Algarotti’s eclectic, cosmopolitan tastes; retain the attribution and do not treat it as a documented commission instruction.',
'st-chp14-p354-algarotti-on-colourist-works':'Haskell reports Algarotti’s view that answers about colour lay in works of great colourists, naming Giorgione and Titian. The endpoint is an unidentified work group, not a specific painting.',
'st-chp14-p354-algarotti-advocated-study-of-newton-optics':'Haskell says Algarotti wanted artists to study Newton’s optical discoveries. The endpoint records those discoveries as a concept, not the duplicate Algarotti index subentry or a claim that artists adopted them.',
'st-chp14-p354-new-scientific-knowledge-justifies-practice':'Haskell attributes to Algarotti the view that new scientific knowledge chiefly justified existing artistic practice. No new departure or adoption by artists is asserted.',
'st-chp14-p354-learning-brio-fantasy':'Haskell reports Algarotti’s praise of Tiepolo as learned in the spirit of Raphael or Poussin. This is the first of two distinct responses split from the compound statement.',
'st-chp14-p354-algarotti-attracted-to-tiepolo-brio-fantasy':'Haskell says Algarotti was at least as attracted to Tiepolo’s brio and fantasy as to his learning. Keep separate from the praise of learning and preserve Haskell’s interpretation.',
'st-chp14-p354-note3-white-ground-proposal':'Haskell’s note says the 1756 letter implies the white-ground proposal had only just occurred to Algarotti. This links the letter to the proposal; it does not verify the letter or an invention date.'}
false_notes={
'st-chp14-p354-algarotti-classical-bias':'This describes an attributed characteristic of Algarotti’s taste; it remains a source claim but does not assert a separate event or directed relation.',
'st-chp14-p354-colour-influence-difficult-to-assess':'The statement records that influence is difficult to assess, not a positive relation; preserve the explicit uncertainty.',
'st-chp14-p354-early-forties-classical-phase':'This is Haskell’s time-period characterization of Tiepolo’s classical phase, not a separate directed relation; retain the periodization as a claim.',
'st-chp14-p354-note1-knox-locator':'Bibliographic locator only; it identifies the cited source and page but asserts no entity relation.',
'st-chp14-p354-note2-levey-locator':'Bibliographic locator only; the citation is linked to the body discussion elsewhere and adds no new relation here.',
'st-chp14-p354-note3-color-theory-sources':'Bibliographic locator only; it names the cited works and letter but does not itself assert a new relation.',
'st-chp14-p354-note4-rava-locator':'Bibliographic locator only; it identifies the source cited for the drawings and etchings, with no new entity relation.',
'st-chp14-p354-note5-saggio-locator':'Bibliographic locator only; it cites Algarotti’s treatise for the later summary but adds no separate relation.'}
for sid,note in {**true_notes,**false_notes}.items():
 if sid in {'st-chp14-p354-algarotti-advocated-study-of-newton-optics','st-chp14-p354-algarotti-attracted-to-tiepolo-brio-fantasy'}: continue
 if sid not in byid or byid[sid].get('qualifiers',{}).get('relation_candidate') is not None: raise SystemExit(f'unexpected statement state: {sid}')
 q=byid[sid].setdefault('qualifiers',{}); q['relation_candidate']=sid in true_notes; q['relation_candidate_note']=note

def csvread(key):
 with P[key].open(encoding='utf-8-sig',newline='') as f:
  d=csv.DictReader(f); return d.fieldnames,list(d)
cf,candidates=csvread('ca'); mf,mentions=csvread('me')
cids={r['candidate_id'] for r in candidates}; mids={r['mention_id'] for r in mentions}
if len(cids)!=len(candidates) or len(mids)!=len(mentions): raise SystemExit('duplicate ids in table')
if max(int(x.split('-')[1]) for x in cids)!=12194: raise SystemExit('candidate sequence changed')
newc=[
['cand-12195','',"Algarotti’s important patrons in Saxony (unnamed group, p.354)",'','term','open','','',"Haskell identifies only an unnamed group as Algarotti’s important patrons in Saxony and says the preceding pictures were ordered for them. Membership and individual recipient mapping are not supplied; keep distinct from Saxony as a place and from the Electorate.",'','body-mention','chp-14:14_CHP-14_intro:l73-83#L75'],
['cand-12196','',"Newton’s optical discoveries as applied to painting (p.354)",'','term','open','','',"Haskell says Algarotti propagated Newton’s optical discoveries, wanted artists to study them, and regarded new scientific knowledge as theoretical justification for existing practice. Cited writing was not independently consulted; adoption by artists is not asserted.",'','body-mention','chp-14:14_CHP-14_intro:l73-83#L79'],
['cand-12197','','Unidentified works of the great colourists named by Algarotti (p.354)','','work','open','','',"Haskell reports Algarotti locating answers about colour in works by great colourists, naming Giorgione and Titian. No individual title or version is supplied; do not assign a specific painting to either artist.",'','body-mention','chp-14:14_CHP-14_intro:l73-83#L79'],
['cand-12198','','White-ground painting proposal reported in Algarotti’s 1756 letter (p.354 n.3)','','term','open','','',"Proposal for artists to paint on white rather than usual reddish-brown grounds. Haskell says the letter implies the idea had only just occurred to Algarotti; the letter was not consulted, so this is not an independently verified invention date.",'','body-mention','chp-14:14_CHP-14_intro:l168-220#L188']]
if any(r[0] in cids for r in newc): raise SystemExit('new candidate ID already present')
candidates += [dict(zip(cf,r)) for r in newc]; cids.update(r[0] for r in newc)
newm=[
['m-chp14-p354-0072','chp-14:14_CHP-14_intro:l73-83','cand-12195','important patrons in\nSaxony','256','283','Unnamed group; no individual members or one-to-one work mapping supplied.'],
['m-chp14-p354-0073','chp-14:14_CHP-14_intro:l73-83','cand-12196','Newton’s discoveries in optics','894','924','Subject of Algarotti’s source-reported advocacy to artists.'],
['m-chp14-p354-0074','chp-14:14_CHP-14_intro:l73-83','cand-12196','newscientific knowledge','1352','1375','Preserves OCR wording; the printed page reads “new scientific knowledge”.'],
['m-chp14-p354-0075','chp-14:14_CHP-14_intro:l73-83','cand-12197','works of the great colourists such as\nGiorgione and Titian','1288','1346','Unidentified work group; named painters are examples, not specific work identities.'],
['m-chp14-p354-0076','chp-14:14_CHP-14_intro:l168-220','cand-12198','white grounds rather than on the more usual reddish brown','3082','3139','Proposal described in Haskell’s account of the letter, not directly verified from it.']]
if any(r[0] in mids for r in newm): raise SystemExit('new mention ID already present')
mentions += [dict(zip(mf,r)) for r in newm]

# Correct endpoint mappings that previously pointed to a place or a duplicate person candidate.
p=byid['st-chp14-p354-bruhl-pictures-for-patrons-in-saxony']; p['object_candidate_id']='cand-12195'
p['qualifiers']['mentioned_candidate_ids']=list(dict.fromkeys(p['qualifiers'].get('mentioned_candidate_ids',[])+['cand-12195']))
for sid in ['st-chp14-p354-algarotti-advocated-study-of-newton-optics','st-chp14-p354-new-scientific-knowledge-justifies-practice']:
 r=byid[sid];r['object_candidate_id']='cand-12196'
 r['qualifiers']['mentioned_candidate_ids']=list(dict.fromkeys('cand-12196' if x=='cand-0067' else x for x in r['qualifiers'].get('mentioned_candidate_ids',[])))
 r['qualifiers']['relation_candidate_note']=true_notes[sid]
r=byid['st-chp14-p354-algarotti-on-colourist-works'];r['object_candidate_id']='cand-12197'
r['qualifiers']['mentioned_candidate_ids']=list(dict.fromkeys(r['qualifiers'].get('mentioned_candidate_ids',[])+['cand-12197']))
r=byid['st-chp14-p354-note3-white-ground-proposal'];r['subject_candidate_id']='cand-10303';r['object_candidate_id']='cand-12198';r['predicate']='letter_reported_as_implying_recent_emergence_of_white_ground_proposal'
r['qualifiers'].update({'claim':'Haskell says the 13 May 1756 letter implies that the proposal for artists to paint on white rather than the usual reddish-brown ground had only just occurred to Algarotti.','speaker':'Haskell','text_layer':'authorial interpretation of an archival letter','qualification':'The letter itself was not consulted; retain Haskell’s implication and do not treat this as a verified invention date.','mentioned_candidate_ids':['cand-10303','cand-12198','cand-0052']})
r['qualifiers']['relation_candidate']=True;r['qualifiers']['relation_candidate_note']=true_notes[r['statement_id']]

# Split the two distinct responses in Algarotti’s p.354 reception of Tiepolo.
base=byid['st-chp14-p354-learning-brio-fantasy'];q=base['qualifiers']
q['claim']='Haskell says Algarotti attempted to praise Tiepolo as learned in the spirit of Raphael or Poussin.'
base['predicate']='praised_tiepolo_as_learned_in_spirit_of_raphael_and_poussin'
second=json.loads(json.dumps(base,ensure_ascii=False));second['statement_id']='st-chp14-p354-algarotti-attracted-to-tiepolo-brio-fantasy'
second['predicate']='attracted_to_tiepolo_brio_and_fantasy'
second['qualifiers']['claim']='Haskell says Algarotti was at least as attracted to Tiepolo’s brio and fantasy as to his learning.'
second['qualifiers']['text_layer']='authorial interpretation of Algarotti’s critical response'
second['qualifiers']['qualification']='This is the second of two distinct responses in Haskell’s sentence; it does not establish direct influence or a general doctrine.'
second['qualifiers']['mentioned_candidate_ids']=['cand-0052','cand-3781']
second['qualifiers']['relation_candidate']=True
second['qualifiers']['relation_candidate_note']=true_notes[second['statement_id']]
q['cross_reference_statement_ids']=[second['statement_id']]
second['qualifiers']['cross_reference_statement_ids']=[base['statement_id']]
if second['statement_id'] in byid: raise SystemExit('split statement ID already exists')
statements.append(second);byid[second['statement_id']]=second

# Validate new spans against the canonical S0 segment text.
segments=[json.loads(x) for x in (T/'segments.jsonl').read_text(encoding='utf-8-sig').splitlines() if x.strip()]
segby={r['segment_id']:r for r in segments};texts={}
for m in newm:
 if m[2] not in cids: raise SystemExit(f'missing mention candidate {m[0]}')
 seg=segby[m[1]]
 if m[1] not in texts:
  lines=(ROOT/seg['source_file']).read_text(encoding='utf-8-sig').splitlines();texts[m[1]]='\n'.join(lines[int(seg['line_start'])-1:int(seg['line_end'])])
 if texts[m[1]][int(m[4]):int(m[5])]!=m[3]: raise SystemExit(f'source span mismatch {m[0]}')
# Count p.354 statuses after atomization.
page=[r for r in statements if r['statement_id'].startswith('st-chp14-p354-')]
counts={'statements':len(page),'true':sum(r.get('qualifiers',{}).get('relation_candidate') is True for r in page),'false':sum(r.get('qualifiers',{}).get('relation_candidate') is False for r in page),'unset':sum(r.get('qualifiers',{}).get('relation_candidate') is None for r in page)}
if counts!={'statements':28,'true':20,'false':8,'unset':0}: raise SystemExit(f'unexpected p354 counts {counts}')
# Reject exact/crossing spans; strictly nested entity/concept anchors are permitted.
ints={}
for m in mentions:ints.setdefault(m['segment_id'],[]).append((int(m['start_char']),int(m['end_char']),m['mention_id']))
for sid,spans in ints.items():
 spans.sort()
 for i,a in enumerate(spans):
  for b in spans[i+1:]:
   if b[0]>=a[1]:break
   nested=(a[0]<=b[0] and b[1]<=a[1]) or (b[0]<=a[0] and a[1]<=b[1])
   if a[:2]==b[:2] or not nested:raise SystemExit(f'crossing mention spans {sid}: {a[2]} / {b[2]}')

def csvout(fields,rows):
 from io import StringIO
 b=StringIO(newline='');w=csv.DictWriter(b,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows);return b.getvalue().encode('utf-8')
outputs={P['st']:('\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in statements)+'\n').encode('utf-8'),P['me']:csvout(mf,mentions),P['ca']:csvout(cf,candidates)}
print(json.dumps({'mode':'apply' if args.apply else 'dry-run','new_candidates':[r[0] for r in newc],'new_mentions':len(newm),'p354_counts':counts,'repaired_endpoints':['patrons group','Newton optics concept','colourist works group','letter to white-ground proposal'],'validated_new_spans':len(newm),'crossings':0,'after_sha256':{str(k.relative_to(ROOT)):sha(v) for k,v in outputs.items()}},ensure_ascii=False,indent=2))
if args.apply:
 temps={}
 for path,data in outputs.items():
  backup=path.with_name(path.name+TAG)
  key=next(k for k,v in P.items() if v==path)
  if backup.exists():
   if sha(backup.read_bytes())!=EXPECTED[key]:raise SystemExit(f'backup differs: {backup.name}')
  else:shutil.copy2(path,backup)
  with tempfile.NamedTemporaryFile('wb',delete=False,dir=path.parent) as f:f.write(data);temps[path]=Path(f.name)
 for path,tmp in temps.items():tmp.replace(path)
 print(json.dumps({'written_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in outputs}}))
