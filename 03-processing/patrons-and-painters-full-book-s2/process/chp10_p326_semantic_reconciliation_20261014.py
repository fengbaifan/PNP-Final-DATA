"""Reconcile p.326 semantic statements, split bundled claims, and register missing local groups."""
from __future__ import annotations
import argparse,csv,copy,hashlib,json,shutil,tempfile
from pathlib import Path
from io import StringIO
ROOT=Path(__file__).resolve().parents[3]
T=ROOT/'04-knowledge/tables'
SOURCE=ROOT/'02-sources/02-Markdown/10_CHP-10_sec_ii.md'
CAND=T/'entity-candidates.csv'; MENT=T/'mentions.csv'; STMT=T/'book-statements.jsonl'; COV=T/'s2-coverage.csv'
SEG='chp-10:10_CHP-10_sec_ii:l210-222'
EXPECTED={CAND:'ec3f112c6d0bec748ca78fd9c749cc9aaa73bcdddae2d5b11bf0394eaabaa875',MENT:'d929f309ce2e8876f47a6c4cd06c6a192f605c48d75f7074fabf1f91d2dc9f7d',STMT:'fab299fa3fcb47285639a5b7dfb5a992dc5084bfcfe43d0ad214a2408d485571',COV:'bc8265a5ef93304ab6ea6e9b501154b9d63420b1dcab79ba7055ac4896679668'}
SUFFIX='.bak-s2-chp10-p326-semantic-reconciliation-20261014'
for p,want in EXPECTED.items():
 got=hashlib.sha256(p.read_bytes()).hexdigest()
 if got!=want: raise SystemExit(f'input changed: {p.relative_to(ROOT)} {got}')
with CAND.open(encoding='utf-8-sig',newline='') as f:
 cr=csv.DictReader(f); cand_fields=list(cr.fieldnames); candidates=list(cr)
with MENT.open(encoding='utf-8-sig',newline='') as f:
 mr=csv.DictReader(f); mention_fields=list(mr.fieldnames); mentions=list(mr)
with COV.open(encoding='utf-8-sig',newline='') as f:
 vr=csv.DictReader(f); cov_fields=list(vr.fieldnames); coverage=list(vr)
statements=[json.loads(x) for x in STMT.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
byid={r['statement_id']:r for r in statements}
open_rows=[r for r in statements if r.get('segment_id')==SEG and (r.get('qualifiers') or {}).get('relation_candidate') is None]
expected_open={
'st-chp10-p326-appointment-enthusiasm','st-chp10-p326-authorities-misunderstanding','st-chp10-p326-il-patriotismo-title','st-chp10-p326-inquisitori-opposition','st-chp10-p326-inquisitors-interpret-allegories','st-chp10-p326-justice-temple-frontispiece','st-chp10-p326-montesquieu-frontispiece','st-chp10-p326-n01-marciana-set','st-chp10-p326-n01-montesquieu-reference','st-chp10-p326-pamphlet-prints-hostility','st-chp10-p326-picture-display-agency-alternatives','st-chp10-p326-procurator-procession-picture-custom','st-chp10-p326-riviera-engravings-and-pamphlet','st-chp10-p326-support-and-state-surveillance','st-chp10-p326-visiting-card-iconography'}
if {r['statement_id'] for r in open_rows}!=expected_open: raise SystemExit('p.326 unclassified statement set changed')
# Reuse these existing local source lines to anchor additional entity mentions.
source_lines=SOURCE.read_text(encoding='utf-8').splitlines()
segment_text='\n'.join(source_lines[209:222])
new_candidates=[
 {'candidate_id':'cand-12113','index_entry_id':'','canonical_name':'Unidentified advisers of Giorgio Pisani in the procession-picture episode','index_page_range':'','suggested_type':'term','status':'open','index_source_file':'','sub_entry':'','detail':'Haskell says Pisani\'s advisers may have displayed the political allegories because they liked abstruse symbolism. Their names and membership are not supplied; preserve this as one alternative agent, not an established display decision.','exclude_reason':'','candidate_origin':'body-mention','candidate_source_ref':f'{SEG}#L217'},
 {'candidate_id':'cand-12114','index_entry_id':'','canonical_name':'Unidentified friends of Giorgio Pisani in the p.326 political episode','index_page_range':'','suggested_type':'term','status':'open','index_source_file':'','sub_entry':'','detail':'Haskell says Pisani and his friends offended the authorities. Their names and membership are not supplied; keep this local group distinct from Pisani\'s advisers and from his unnamed supporters.','exclude_reason':'','candidate_origin':'body-mention','candidate_source_ref':f'{SEG}#L216'},
 {'candidate_id':'cand-12115','index_entry_id':'','canonical_name':'Collective set of pamphlets issued in honour of Giorgio Pisani\'s 1780 entry','index_page_range':'','suggested_type':'archive','status':'open','index_source_file':'','sub_entry':'','detail':'Haskell refers collectively to pamphlets printed for Pisani\'s entry; note 1 names three publications and says a set at Biblioteca Marciana carries marginal comments. Do not infer that every pamphlet contains each frontispiece or merge the set with the election event.','exclude_reason':'','candidate_origin':'body-mention','candidate_source_ref':f'{SEG}#L213'},
 {'candidate_id':'cand-12116','index_entry_id':'','canonical_name':'Unidentified works of Montesquieu represented in a Pisani-entry pamphlet frontispiece','index_page_range':'','suggested_type':'archive','status':'open','index_source_file':'','sub_entry':'','detail':'A putto is shown carrying works of Montesquieu in one frontispiece. No titles, editions, or individual volumes are identified; the source is not independently consulted.','exclude_reason':'','candidate_origin':'body-mention','candidate_source_ref':f'{SEG}#L213'},
]
existing_cids={r['candidate_id'] for r in candidates}
if any(r['candidate_id'] in existing_cids for r in new_candidates): raise SystemExit('candidate ID already exists')
# Verify exact source spans before recording offsets or splitting claims.
phrases=[('a tribute','cand-9793'),('pamphlets that were printed in his honour','cand-12115'),('the works of Montesquieu','cand-12116'),('his friends','cand-12114'),('Pisani’s advisers','cand-12113'),('these pamphlets','cand-12115')]
for phrase,_ in phrases:
 if segment_text.count(phrase)!=1: raise SystemExit(f'source phrase not unique: {phrase!r}')
new_mentions=[]
first_mention_number=max((int(m['mention_id'].rsplit('-',1)[1]) for m in mentions if m['mention_id'].startswith('m-s2-ch10-p326-327-') and m['mention_id'].rsplit('-',1)[1].isdigit()),default=0)+1
for number,(surface,cid) in enumerate(phrases,first_mention_number):
 start=segment_text.index(surface)
 new_mentions.append({'mention_id':f'm-s2-ch10-p326-327-{number:04d}','segment_id':SEG,'candidate_id':cid,'surface_form':surface,'start_char':str(start),'end_char':str(start+len(surface)),'note':{
 'cand-9793':'The tribute is the unidentified work Gozzi wrote in response to Pisani\'s appointment.','cand-12115':'Collective referent; the footnote names three individual pamphlets and identifies a set held at Biblioteca Marciana.','cand-12116':'The printed frontispiece refers to Montesquieu\'s writings collectively; no individual title is named.','cand-12114':'Possessive refers to Giorgio Pisani; members are unnamed.','cand-12113':'Haskell offers this unnamed group as one possible agent; it is not merged with Pisani\'s friends.','cand-12115':'Anaphoric reference to the same collective pamphlet set.'}[cid]})
if any(m['mention_id'] in {r['mention_id'] for r in mentions} for m in new_mentions): raise SystemExit('mention ID conflict')
for r in open_rows: r['qualifiers']['relation_candidate']=False
# Reception of Pisani's appointment and Gozzi's authored tribute are separate claims.
appointment=byid['st-chp10-p326-appointment-enthusiasm']
appointment['subject_candidate_id']='cand-9792'; appointment['object_candidate_id']=''
appointment['qualifiers'].update({'claim':'Haskell says Pisani\'s 1780 appointment was greeted with great enthusiasm and congratulations poured in.','qualification':'This records reception of the appointment; it does not establish an organized ceremony or identify the congratulators. Gozzi\'s separate tribute is recorded as its own work and authorship claim.','mentioned_candidate_ids':['cand-1942','cand-9792'],'relation_candidate':False})
appointment['original_quote']='The appointment was greeted with great enthusiasm.\nCongratulations poured in'
# The line explicitly attributes the tribute to Gozzi; reuse its local archive candidate.
tribute=copy.deepcopy(appointment)
tribute.update({'statement_id':'st-chp10-p326-gozzi-authored-tribute','subject_candidate_id':'cand-9793','object_candidate_id':'cand-1223','predicate':'authored_by','original_quote':'Gozzi wrote a tribute'})
tribute['qualifiers'].update({'claim':'Haskell says Gasparo Gozzi wrote a tribute for Giorgio Pisani after his 1780 appointment.','qualification':'The tribute is unidentified by title. Its creator and recipient are stated through this passage; candidate identity remains for S3.','mentioned_candidate_ids':['cand-9793','cand-1223','cand-1942'],'relation_candidate':True})
# Separate the unnamed support from surveillance by a singular government spy.
surveillance=byid['st-chp10-p326-support-and-state-surveillance']
surveillance['predicate']='received_attention_from_government_spy'
surveillance['qualifiers'].update({'claim':'Haskell says Pisani\'s preceding political stance drew the attention of a government spy.','qualification':'\'This\' refers to Pisani\'s political stance. The source names one spy here; do not identify this person with the plural spies in the later celebration.','mentioned_candidate_ids':['cand-1942','cand-9790','cand-9789'],'relation_candidate':True})
surveillance['original_quote']='as well as the attentions of a government spy.'
support=copy.deepcopy(surveillance)
support.update({'statement_id':'st-chp10-p326-pisani-received-some-support','subject_candidate_id':'cand-1942','object_candidate_id':'','predicate':'received_some_support','original_quote':'And this won him some support'})
support['qualifiers'].update({'claim':'Haskell says Pisani\'s preceding political stance won him some support.','qualification':'The supporters are not identified as a person or a stable group; do not equate them with the later celebration guests.','mentioned_candidate_ids':['cand-1942'],'relation_candidate':False})
# Preserve the direct offense claim and isolate Haskell's qualified causal explanation.
authorities=byid['st-chp10-p326-authorities-misunderstanding']
authorities['qualifiers'].update({'claim':'Haskell says Pisani and his friends offended the authorities.','qualification':'The episode involves Pisani and an unnamed group of friends in relation to Venetian authorities; Haskell does not name the officials or claim a formal prosecution.','mentioned_candidate_ids':['cand-1942','cand-12114','cand-9789','cand-9807'],'relation_candidate':True})
authorities['original_quote']='Here too Pisani and his friends offended the authorities'
misunderstanding=copy.deepcopy(authorities)
misunderstanding.update({'statement_id':'st-chp10-p326-misunderstanding-explanation','subject_candidate_id':'cand-1942','object_candidate_id':'','predicate':'trouble_attributed_to_possible_misunderstanding','original_quote':'though the trouble seems to have been caused by a misunderstanding natural enough in the prevailing tension.'})
misunderstanding['qualifiers'].update({'claim':'Haskell says the trouble seems to have been caused by a misunderstanding amid the prevailing tension.','qualification':'This is Haskell\'s qualified causal explanation, not an established finding that the allegories had no political meaning.','mentioned_candidate_ids':['cand-1942','cand-9789','cand-9807'],'relation_candidate':False})
# A pamphlet title is an identification, not a relationship candidate.
byid['st-chp10-p326-il-patriotismo-title']['qualifiers']['relation_candidate']=False
# Explicit political and institutional relations.
byid['st-chp10-p326-inquisitori-opposition']['qualifiers']['relation_candidate']=True
inquisitors=byid['st-chp10-p326-inquisitors-interpret-allegories']
inquisitors['qualifiers'].update({'claim':'Haskell says the Inquisitors decided that the political allegories were intended as subversive propaganda.','qualification':'This records the Inquisitors\' interpretation, not the artist\'s or Pisani\'s actual intent. The cited note later qualifies the attribution and dating of related images.','relation_candidate':True})
inquisitors['original_quote']='they decided that the allegories were intended as subversive propaganda.'
suspicion=copy.deepcopy(inquisitors)
suspicion.update({'statement_id':'st-chp10-p326-inquisitors-reason-for-suspicion','object_candidate_id':'','predicate':'haskell_assesses_suspicion_as_reasonable','original_quote':'They had some reason to be suspicious'})
suspicion['qualifiers'].update({'claim':'Haskell says the Inquisitors had some reason to be suspicious.','qualification':'This is Haskell\'s assessment, not an independently established basis for suspicion.','relation_candidate':False})
byid['st-chp10-p326-justice-temple-frontispiece']['qualifiers']['relation_candidate']=True
montes=byid['st-chp10-p326-montesquieu-frontispiece']
montes['object_candidate_id']='cand-12116'
montes['qualifiers'].update({'claim':'One frontispiece shows a nude youth and a putto carrying an unidentified group of Montesquieu\'s works.','qualification':'The image and its contents are Haskell\'s description; no individual work is named or independently consulted. The candidate denotes the writings represented, not a portrait of Montesquieu.','mentioned_candidate_ids':['cand-9794','cand-12116','cand-1696'],'relation_candidate':True})
montes['original_quote']='in one frontispiece a nude youth reclined while a putto carried aloft the works of Montesquieu'
controversy=copy.deepcopy(montes)
controversy.update({'statement_id':'st-chp10-p326-montesquieu-works-controversial','subject_candidate_id':'cand-12116','object_candidate_id':'','predicate':'described_as_controversial_in_venetian_society','original_quote':'which were highly controversial in Venetian society'})
controversy['qualifiers'].update({'claim':'Haskell says the represented works of Montesquieu were highly controversial in Venetian society.','qualification':'This is Haskell\'s broad reception assessment; the specific works and scope of the society are not identified.','mentioned_candidate_ids':['cand-12116','cand-1696','cand-2719'],'relation_candidate':False})
# The collectively cited pamphlet set is the referent for hostility and the Marciana copy.
pamphlet_group='cand-12115'
hostility=byid['st-chp10-p326-pamphlet-prints-hostility']
hostility['subject_candidate_id']=pamphlet_group
hostility['qualifiers'].update({'mentioned_candidate_ids':[pamphlet_group,'cand-9792','cand-9791','cand-9794','cand-9795','cand-9796'],'relation_candidate':True,'qualification':'Haskell reports hostility to allegorical prints in the collectively described entry pamphlets. Note 1 identifies three titles, but neither the exact pamphlet containing each image nor the hostile individuals are identified.'})
marciana=byid['st-chp10-p326-n01-marciana-set']
marciana['subject_candidate_id']=pamphlet_group; marciana['object_candidate_id']='cand-9448'
marciana['predicate']='pamphlet_set_held_at_and_marked_in_repository'
marciana['qualifiers'].update({'mentioned_candidate_ids':[pamphlet_group,'cand-9448','cand-2719','cand-9794','cand-9795','cand-9796'],'relation_candidate':True})
byid['st-chp10-p326-n01-montesquieu-reference']['qualifiers']['relation_candidate']=False
# The route custom is relational; preserve it separately from the specific uncertain display agency.
custom=byid['st-chp10-p326-procurator-procession-picture-custom']
custom['subject_candidate_id']='cand-9807'; custom['object_candidate_id']='cand-9792'
custom['predicate']='displayed_for_procurator_entry_procession'
custom['qualifiers'].update({'mentioned_candidate_ids':['cand-9807','cand-9792','cand-8449'],'relation_candidate':True})
# Split the two possible display agents into separate candidate relations without resolving which occurred.
agency=byid['st-chp10-p326-picture-display-agency-alternatives']
agency['subject_candidate_id']='cand-9807'; agency['object_candidate_id']='cand-0411'
agency['predicate']='possibly_displayed_by_boscarati'
agency['qualifiers'].update({'claim':'Haskell offers Boscarati himself as one possible agent who displayed the pictures to take advantage of his position.','qualification':'This is one of two alternatives, not a resolved attribution; the source does not establish that Boscarati commissioned the pictures.','mentioned_candidate_ids':['cand-9807','cand-0411','cand-1942'],'relation_candidate':True})
agency['original_quote']='either by the artist himself in order to take advantage of his situation'
advisers=copy.deepcopy(agency)
advisers.update({'statement_id':'st-chp10-p326-pictures-possibly-displayed-by-pisani-advisers','object_candidate_id':'cand-12113','predicate':'possibly_displayed_by_pisani_advisers','original_quote':'or by Pisani’s advisers who rather liked abstruse symbolism for its own sake.'})
advisers['qualifiers'].update({'claim':'Haskell offers Pisani\'s advisers as an alternative possible group who displayed the pictures because they liked abstruse symbolism.','qualification':'This is the alternative to Boscarati as display agent; the advisers are unnamed and the source does not establish that they commissioned the pictures.','mentioned_candidate_ids':['cand-9807','cand-12113','cand-1942'],'relation_candidate':True})
# Separate copying of paintings into engravings from Riviera's issuing of the explanatory pamphlet.
riviera=byid['st-chp10-p326-riviera-engravings-and-pamphlet']
riviera['subject_candidate_id']='cand-9805'; riviera['object_candidate_id']='cand-9803'; riviera['predicate']='derived_from'
riviera['qualifiers'].update({'claim':'Haskell says the four allegorical paintings were copied into large engravings with garbled Latin text beneath.','qualification':'The antecedent of “he” is locally Lazzaro Riviera. The source does not identify the engraver or surviving impressions; the pamphlet is recorded separately.','mentioned_candidate_ids':['cand-2204','cand-9803','cand-9805'],'relation_candidate':True})
riviera['original_quote']='he had them copied in large engravings with a text in garbled Latin underneath'
pamphlet=copy.deepcopy(riviera)
pamphlet.update({'statement_id':'st-chp10-p326-riviera-issued-explanatory-pamphlet','subject_candidate_id':'cand-9806','object_candidate_id':'cand-2204','predicate':'issued_by','original_quote':'and issued an equally incomprehensible pamphlet to explain them.'})
pamphlet['qualifiers'].update({'claim':'Haskell says Riviera issued an explanatory pamphlet for the engravings.','qualification':'The pamphlet is identified as La Educazione Virile in p.327 note 3; neither version was independently consulted.','mentioned_candidate_ids':['cand-9806','cand-2204','cand-9803','cand-9805'],'relation_candidate':True})
# The card's motifs are preserved as content; the source does not identify a portrait or a formal relation.
byid['st-chp10-p326-visiting-card-iconography']['qualifiers']['relation_candidate']=False
new_statements=[tribute,support,misunderstanding,suspicion,controversy,advisers,pamphlet]
if any(r['statement_id'] in byid for r in new_statements): raise SystemExit('new statement ID already exists')
statements.extend(new_statements)
candidates.extend(new_candidates); mentions.extend(new_mentions)
# Append a source- and page-specific review note once.
cov=next((r for r in coverage if r['segment_id']==SEG),None)
if not cov or (cov['disposition'],cov['migration_status'])!=('reviewed','complete'): raise SystemExit('coverage state changed')
review=' 2026-10-14 semantic review against CHP-10.pdf physical p.59 classified the 15 previously unset p.326 statements and split bundled claims for Gozzi\'s tribute, Pisani\'s support/surveillance, the authority episode, Montesquieu reception, Inquisitors\' suspicion, display-agent alternatives, and Riviera\'s engravings/pamphlet. Added four source-local candidates for unnamed friends, advisers, the cited pamphlet set, and the unidentified Montesquieu writings; the source does not resolve print authorship or the display agents.'
if '2026-10-14 semantic review against CHP-10.pdf physical p.59' in cov['note']: raise SystemExit('coverage review note already present')
cov['note']+=review
print(json.dumps({'segment':SEG,'previously_unclassified':len(open_rows),'new_statements':len(new_statements),'new_candidates':[r['candidate_id'] for r in new_candidates],'new_mentions':[r['mention_id'] for r in new_mentions],'relation_candidate_counts':{'true':sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in statements if r.get('segment_id')==SEG),'false':sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in statements if r.get('segment_id')==SEG)}},ensure_ascii=True,indent=2))
def replace(path,text):
 with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=path.parent,delete=False) as f: f.write(text); tmp=Path(f.name)
 tmp.replace(path)
args=argparse.ArgumentParser(); args.add_argument('--apply',action='store_true'); apply=args.parse_args().apply
if apply:
 files=[CAND,MENT,STMT,COV]; backups=[Path(str(p)+SUFFIX) for p in files]
 if any(b.exists() for b in backups): raise SystemExit('recovery backup exists; inspect before retrying')
 for p,b in zip(files,backups): shutil.copy2(p,b)
 try:
  out=StringIO(); w=csv.DictWriter(out,fieldnames=cand_fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(candidates); replace(CAND,out.getvalue())
  out=StringIO(); w=csv.DictWriter(out,fieldnames=mention_fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(mentions); replace(MENT,out.getvalue())
  replace(STMT,''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in statements))
  out=StringIO(); w=csv.DictWriter(out,fieldnames=cov_fields,extrasaction='ignore',lineterminator='\n'); w.writeheader(); w.writerows(coverage); replace(COV,out.getvalue())
 except Exception:
  for p,b in zip(files,backups): shutil.copy2(b,p)
  raise
 print('APPLIED; backups='+', '.join(str(b.relative_to(ROOT)) for b in backups))
parser=argparse.ArgumentParser(); parser.add_argument('--apply',action='store_true'); args=parser.parse_args()
if args.apply: apply()
