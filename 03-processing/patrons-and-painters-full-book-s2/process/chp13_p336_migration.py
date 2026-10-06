"""Controlled S2 migration for printed p.336; dry-run by default."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TABLES=ROOT/'04-knowledge'/'tables'
SOURCE=ROOT/'02-sources'/'02-Markdown'/'13_CHP-13_intro.md'
PDF=ROOT/'02-sources'/'01-book'/'CHP-13.pdf'
BODY='chp-13:13_CHP-13_intro:l41-50'
PREVIOUS='chp-13:13_CHP-13_intro:l32-39'
NEXT='chp-13:13_CHP-13_intro:l52-59'
NOTES='chp-13:13_CHP-13_intro:l179-251'
SOURCE_SHA='c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8'
PDF_SHA='da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc'
BACKUP_SUFFIX='.bak-s2-chp13-p336-20261003'
parser=argparse.ArgumentParser()
parser.add_argument('--apply',action='store_true',help='apply the reviewed p.336 S2 migration')
args=parser.parse_args()

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); return r.fieldnames,list(r)
def read_jsonl(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8-sig').splitlines() if s.strip()]
def write_csv(path,fields,rows):
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=path.parent,delete=False) as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows);tmp=Path(f.name)
    tmp.replace(path)
def write_jsonl(path,rows):
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='',dir=path.parent,delete=False) as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
        tmp=Path(f.name)
    tmp.replace(path)

if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise SystemExit('canonical chapter 13 Markdown source changed')
if hashlib.sha256(PDF.read_bytes()).hexdigest()!=PDF_SHA:raise SystemExit('registered CHP-13 PDF asset changed')
source_lines=SOURCE.read_text(encoding='utf-8-sig').splitlines()
expected={
 41:'[Page 336]',
 42:'Francesco Gerbault, Louis XV’s interpreter of Spanish and Italian',
 43:'Chirurgicae. Meanwhile in Venice the Guardi brothers',
 44:'Gerusalemme Liberata in a series of large decorative canvases',
 45:'Albrizzi was well aware of the debt that he owed to his friend.',
 46:'But he also employed a number of other illustrators on his books.',
 47:'Novelli, Giuseppe Zais and Alessandro Longhi',
 48:'Robert Adam realised when he passed through in 1761',
 49:'Besides employing artists for commercial purposes Albrizzi',
 50:'Pilati and Francesco Albergati-Capacelli.',
}
for n,prefix in expected.items():
    if not source_lines[n-1].startswith(prefix):raise SystemExit(f'canonical source changed at L{n}')

candidate_path=TABLES/'entity-candidates.csv';mention_path=TABLES/'mentions.csv';statement_path=TABLES/'book-statements.jsonl';coverage_path=TABLES/'s2-coverage.csv'
candidate_fields,candidates=read_csv(candidate_path)
mention_fields,mentions=read_csv(mention_path)
coverage_fields,coverage_rows=read_csv(coverage_path)
statements=read_jsonl(statement_path)
candidate_by_id={r['candidate_id']:r for r in candidates};candidate_ids=set(candidate_by_id)
mention_ids={r['mention_id'] for r in mentions};statement_by_id={r['statement_id']:r for r in statements};statement_ids=set(statement_by_id)
coverage={r['segment_id']:r for r in coverage_rows}
state=(len(candidates),max(int(r['candidate_id'].split('-')[1]) for r in candidates),len(mentions),len(statements))
if state!=(9983,9996,21266,9467):raise SystemExit(f'unexpected table pre-state: {state}')
for sid in (BODY,PREVIOUS,NEXT,NOTES):
    if sid not in coverage:raise SystemExit(f'required coverage row missing: {sid}')
if (coverage[BODY]['disposition'],coverage[BODY]['migration_status'])!=('queued','pending'):raise SystemExit('p.336 is not queued/pending')
if (coverage[PREVIOUS]['disposition'],coverage[PREVIOUS]['migration_status'])!=('reviewed','partial'):raise SystemExit('p.335 is not reviewed/partial')
if (coverage[NEXT]['disposition'],coverage[NEXT]['migration_status'])!=('queued','pending'):raise SystemExit('p.337 continuation is not queued/pending')
if any(r['segment_id']==BODY for r in mentions) or any(r['segment_id']==BODY for r in statements):raise SystemExit('p.336 rows already exist')
planned={f'cand-{n}' for n in range(9997,10010)}
if planned & candidate_ids:raise SystemExit(f'p.336 candidate IDs already exist: {sorted(planned & candidate_ids)}')
if any(r['mention_id'].startswith('m-s2-ch13-p336-') for r in mentions):raise SystemExit('p.336 mention IDs already exist')
if any(r['statement_id'].startswith('st-chp13-p336-') for r in statements):raise SystemExit('p.336 statement IDs already exist')
required={'cand-0013','cand-0025','cand-0029','cand-0023','cand-0117','cand-0581','cand-1142','cand-1155','cand-1242','cand-1250','cand-1424','cand-1448','cand-1717','cand-1758','cand-1844','cand-1901','cand-1907','cand-1913','cand-1921','cand-1930','cand-1961','cand-2075','cand-2351','cand-2545','cand-2719','cand-2830','cand-2879','cand-5719','cand-9172','cand-9498','cand-9799','cand-9990'}
if required-candidate_ids:raise SystemExit(f'required candidates missing: {sorted(required-candidate_ids)}')
prior_id='st-chp13-p335-gerusalemme-inspired-next-project-open'
if prior_id not in statement_by_id:raise SystemExit('p.335 open continuation statement missing')
body_lines={n:source_lines[n-1] for n in range(41,51)}
segment_text='\n'.join(body_lines[n] for n in range(41,51))

new_candidates=[]
def add_candidate(cid,name,kind,detail,line,refsegment=BODY):
    if cid in candidate_ids or any(x['candidate_id']==cid for x in new_candidates):raise SystemExit(f'candidate ID already exists: {cid}')
    row={f:'' for f in candidate_fields};row.update({'candidate_id':cid,'canonical_name':name,'suggested_type':kind,'status':'open','detail':detail,'candidate_origin':'body-mention','candidate_source_ref':f'{refsegment}#L{line}'})
    new_candidates.append(row)
add_candidate('cand-9997','Unpublished sumptuous Orlando Furioso edition proposed through a subscription invitation','archive','Francesco Gerbault invited subscriptions for this projected edition after the 1745 Gerusalemme Liberata inspired him. Haskell says the project came to nothing; do not describe it as a published edition.',42)
add_candidate('cand-9998','Guardi brothers’ large decorative canvases after the Gerusalemme Liberata illustrations','work','A series of canvases depicting scenes from the poem, described by Haskell as plagiarising Piazzetta’s illustrations. The passage does not attribute individual canvases to either brother.',44)
add_candidate('cand-9999','The Guardi brothers (collective reference to Francesco and Gian Antonio Guardi)','family','The source explicitly calls them brothers; the individual attribution of the cited canvases is not specified. Keep the collective candidate distinct from the two index candidates pending S3.',43)
add_candidate('cand-10000','Collection of Giovanni Battista Piazzetta’s academic drawings','work','A collection of drawings prefaced by Giambattista Albrizzi’s account of Piazzetta’s life. The collection title and format are not given in this passage.',45)
add_candidate('cand-10001','Giambattista Albrizzi’s account of Giovanni Battista Piazzetta’s life','archive','Haskell says it was published as the preface to a collection of Piazzetta’s academic drawings after the artist’s death in 1754. The exact title and publication date are not given here.',45)
add_candidate('cand-10002','Robert Adam’s book on Diocletian’s palace','archive','The book that Adam entrusted to Albrizzi for sale when he passed through Venice in 1761. The title and the palace’s exact identity are not specified in this passage.',48)
add_candidate('cand-10003','Diocletian’s palace (named as the subject of Robert Adam’s book)','place','A palace named as the subject of Adam’s book; the passage does not give its location or independently establish the exact monument identity.',48)
add_candidate('cand-10004','Giovanni Battista Piazzetta’s 1747 frontispiece for Institutiones Chirurgicae','work','A frontispiece designed for Platnerus’ book. Preserve Haskell’s judgment that the book was “the most unpromising”; no image or full imprint is supplied here.',42)
add_candidate('cand-10005','Scuola di S. Rocco exhibition of 16 August 1770','event','The exhibition to which Albrizzi took two pictures by Zais while serving as Guardiano in 1770. Exact event title and venue details are not further specified; relate cautiously to the recurring exhibition candidate cand-8587.',49)
add_candidate('cand-10006','Two unidentified Giuseppe Zais pictures taken to the 16 August exhibition','work','The source identifies two paintings by Zais but gives no titles. Keep this group distinct from the event and from named works.',49)
add_candidate('cand-10007','Giambattista Albrizzi’s private collection of drawings and paintings by Piazzetta','work','Haskell estimates several hundred drawings and many paintings; the group includes the Sacrifice of Iphigenia. Do not infer an exact inventory or merge it with the published academic-drawing collection.',49)
add_candidate('cand-10008','Letter from P. E. Gherardi to L. A. Muratori, 12 July 1749 (Biblioteca Estense, Modena)','archive','Printed p.336 note 8 identifies this as the source of the comparison between Albrizzi and Pasquali. The archival letter is cited by Haskell but was not independently consulted; the corresponding consolidated citation at L202 remains pending.',50)
add_candidate('cand-10009','Platnerus’ Institutiones Chirurgicae','archive','Book for which Piazzetta designed a frontispiece in 1747. The title is split across S0 lines 42–43; the printed page confirms the wording.',42)
all_candidate_ids=candidate_ids|{r['candidate_id'] for r in new_candidates}

new_mentions=[]
def line_offset(line):return sum(len(body_lines[n])+1 for n in range(41,line))
def add_span(start,end,surface,cid,note=''):
    if cid not in all_candidate_ids:raise SystemExit(f'unknown candidate for mention {surface!r}: {cid}')
    if start<0 or end>len(segment_text) or segment_text[start:end]!=surface:raise SystemExit(f'mention span mismatch: {surface!r}')
    row={f:'' for f in mention_fields};row.update({'mention_id':f'm-s2-ch13-p336-{len(new_mentions)+1:03d}','segment_id':BODY,'candidate_id':cid,'surface_form':surface,'start_char':start,'end_char':end,'note':note});new_mentions.append(row)
def add_mention(line,surface,cid,note='',occurrence=0):
    raw=body_lines[line];positions=[];cursor=0
    while True:
        at=raw.find(surface,cursor)
        if at<0:break
        positions.append(at);cursor=at+1
    if occurrence>=len(positions):raise SystemExit(f'mention text missing at L{line}: {surface!r} occurrence {occurrence}')
    start=line_offset(line)+positions[occurrence];add_span(start,start+len(surface),surface,cid,note)
def add_cross_mention(first,last,start_text,end_text,cid,note=''):
    text='\n'.join(body_lines[n] for n in range(first,last+1));a=text.find(start_text);b=text.find(end_text,a)
    if a<0 or b<0:raise SystemExit(f'cross-line mention boundary missing: {start_text!r}/{end_text!r}')
    surface=text[a:b+len(end_text)];add_span(line_offset(first)+a,line_offset(first)+b+len(end_text),surface,cid,note)

add_mention(42,'Francesco Gerbault','cand-1142')
add_mention(42,'Louis XV','cand-1448')
add_mention(42,'Albrizzi','cand-0025')
add_mention(42,'Piazzetta','cand-1907')
add_mention(42,'an invitation for subscriptions','cand-9997')
add_mention(42,'edition of the Orlando Furioso','cand-9997','Proposed edition, not a published book.')
add_mention(42,'Orlando Furioso','cand-5719','Nested mention of Ariosto’s poem within the projected edition title.')
add_mention(42,'a frontispiece','cand-10004')
add_mention(42,'Platnerus’','cand-1961')
add_cross_mention(42,43,'Institutiones','Chirurgicae','cand-10009','The book title continues across an S0 line break.')
add_mention(43,'Venice','cand-2719')
add_mention(43,'Guardi brothers','cand-9999')
add_mention(43,'his illustrations','cand-1913','Anaphoric reference to Piazzetta’s Gerusalemme Liberata illustrations.')
add_mention(44,'Gerusalemme Liberata','cand-9990','Reference to the 1745 illustrated edition discussed on p.335.')
add_mention(44,'large decorative canvases','cand-9998')
add_mention(44,'the poem','cand-2545','Anaphoric reference to Tasso’s poem.')
add_mention(45,'Albrizzi','cand-0025')
add_mention(45,'Piazzetta’s','cand-1901')
add_mention(45,'an account of his Use','cand-10001','S0 OCR reads “Use”; the page image reads “life.”')
add_mention(45,'a collection of the artist’s academic drawings','cand-10000')
add_mention(46,'Pietro Antonio','cand-1758','Name continues on the following S0 line.')
add_mention(47,'Novelli','cand-1758')
add_mention(47,'Giuseppe Zais','cand-2830')
add_mention(47,'Alessandro Longhi','cand-1424')
add_mention(47,'the firm','cand-9799','Refers to Albrizzi’s publishing establishment; scope awaits identity alignment.')
add_mention(47,'his shop','cand-9799','Refers to Albrizzi’s publishing establishment.')
add_mention(47,'Venice','cand-2719')
add_mention(48,'Robert Adam','cand-0013')
add_mention(48,'Albrizzi','cand-0025')
add_mention(48,'his book on Diocletian’s palace','cand-10002')
add_mention(48,'Diocletian’s palace','cand-10003','Nested mention within the book description; precise place identity awaits S3.')
add_mention(49,'Albrizzi','cand-0029','S1 subentry concerns his private collection.')
add_mention(49,'Piazzetta','cand-1901')
add_mention(49,'a Sacrifice of Iphigenia','cand-1921')
add_mention(49,'Rosalba Carriera','cand-0581')
add_mention(49,'Francesco Zuccarelli','cand-2879')
add_mention(49,'Zais','cand-2830')
add_mention(49,'Scuola di S. Rocco','cand-2351')
add_mention(49,'two of that artist’s pictures','cand-10006','The artist is Giuseppe Zais; titles are not supplied.')
add_mention(49,'the exhibition on 16 August','cand-10005')
add_mention(49,'Giambattista Pasquali','cand-1844')
add_mention(49,'Albrizzi','cand-0025',occurrence=1)
add_mention(49,'Angelo Querini','cand-2075')
add_cross_mention(49,50,'Carlo Antonio','Pilati','cand-1930','The name continues across the S0 line break.')
add_mention(50,'Francesco Albergati-Capacelli','cand-0023')
add_mention(50,'a forthright friend of both men','cand-1155','Printed p.336 note 8 identifies P. E. Gherardi; identity and note link are pending S3/L202 review.')
add_mention(50,'Albrizzi','cand-0025',occurrence=0)
add_mention(50,'Pasquali','cand-1844',occurrence=0)

new_statements=[]
OCR=[
 {'source_line':45,'ocr':'his Use','print':'his life','basis':'CHP-13.pdf physical page 5.'},
 {'source_line':49,'ocr':'die strangely neglected','print':'the strangely neglected','basis':'CHP-13.pdf physical page 5.'},
 {'source_line':49,'ocr':'povertystricken','print':'poverty-stricken','basis':'CHP-13.pdf physical page 5.'},
 {'source_line':49,'ocr':'successful Use','print':'successful life','basis':'CHP-13.pdf physical page 5.'},
]
def excerpt(line,start,end):
    text=body_lines[line];a=text.find(start);b=text.find(end,a)
    if a<0 or b<0:raise SystemExit(f'quote boundary missing at L{line}: {start!r}/{end!r}')
    return text[a:b+len(end)]
def cross_excerpt(first,last,start,end):
    text='\n'.join(body_lines[n] for n in range(first,last+1));a=text.find(start);b=text.find(end,a)
    if a<0 or b<0:raise SystemExit(f'cross-line quote boundary missing: {start!r}/{end!r}')
    return text[a:b+len(end)]
def pending_note(marker):
    return {'footnote_marker':marker,'footnote_printed_page':336,'footnote_text_pending':True,'footnote_segment':NOTES,'footnote_body_link_status':'pending','cross_reference_segments':[NOTES]}
def add_statement(suffix,subj,obj,predicate,lstart,lend,claim,quote,qualification,mentioned,*,speaker='Haskell',layer='authorial narrative',extra=None):
    sid=f'st-chp13-p336-{suffix}'
    if sid in statement_ids or any(r['statement_id']==sid for r in new_statements):raise SystemExit(f'statement ID already exists: {sid}')
    if quote not in segment_text:raise SystemExit(f'statement quote is not anchored in S0: {sid}')
    if any(c not in all_candidate_ids for c in mentioned):raise SystemExit(f'mentioned-candidate FK missing: {sid}')
    for c in (subj,obj):
        if c and c not in all_candidate_ids:raise SystemExit(f'statement endpoint FK missing: {sid}: {c}')
    q={'source_line_start':lstart,'source_line_end':lend,'printed_page':336,'pdf_physical_page':5,'claim':claim,'speaker':speaker,'text_layer':layer,'qualification':qualification,'mentioned_candidate_ids':mentioned,'ocr_corrections':[x for x in OCR if lstart<=x['source_line']<=lend]}
    if extra:q.update(extra)
    new_statements.append({'statement_id':sid,'segment_id':BODY,'subject_candidate_id':subj or None,'object_candidate_id':obj or None,'predicate':predicate,'qualifiers':q,'original_quote':quote,'origin':'book','source_file':'02-sources/02-Markdown/13_CHP-13_intro.md'})

# Close p.335’s sentence without claiming that Gerbault’s projected edition was published.
prior=statement_by_id[prior_id];prior['object_candidate_id']='cand-9997';prior['predicate']='inspired_subscription_plan_for_orlando_furioso_edition'
q=prior['qualifiers'];q.update({'claim':'Haskell says the 1745 Gerusalemme Liberata inspired Francesco Gerbault, Louis XV’s interpreter of Spanish and Italian, to invite subscriptions for an equally sumptuous Orlando Furioso edition.',
 'qualification':'The p.336 printed note 1 cites Hofer, p.37; the consolidated note at L195 remains pending. The projected edition did not come to fruition, as a separate statement records; do not present it as published.',
 'mentioned_candidate_ids':list(dict.fromkeys(q.get('mentioned_candidate_ids',[])+['cand-1142','cand-1448','cand-9997','cand-5719'])),
 'continuation_status':'closed_on_p336','continuation_quote_pending':False,
 'continuation_quote':excerpt(42,'Francesco Gerbault','Orlando Furioso'),
 'continuation_quote_segment_id':BODY,'continuation_quote_source_line_start':42,'continuation_quote_source_line_end':42,
 'continuation_footnote_marker':1,'continuation_footnote_printed_page':336,'continuation_footnote_text_pending':True,'continuation_footnote_segment':NOTES,
 'cross_reference_segments':[PREVIOUS,BODY,NOTES]})

add_statement('gerbault-invited-orlando-subscriptions','cand-1142','cand-9997','issued_subscription_invitation_for_projected_edition',42,42,
 'Gerbault issued an invitation for subscriptions to an equally sumptuous edition of the Orlando Furioso.',
 excerpt(42,'Francesco Gerbault','Orlando Furioso'),
 'The source calls this a project; its failure is recorded separately. Hofer p.37 is cited in printed note 1, pending consolidated note L195.',
 ['cand-1142','cand-1448','cand-9997','cand-5719'],extra={**pending_note(1),'relation_candidate':True})
add_statement('orlando-subscription-project-failed','cand-9997',None,'project_came_to_nothing',42,42,
 'Haskell says the projected Orlando Furioso edition came to nothing.',
 excerpt(42,'a project that came to nothing','a project that came to nothing'),
 'This is an unrealized publication project, not evidence that an edition was issued.',
 ['cand-9997','cand-0117','cand-5719'],extra=pending_note(1))
add_statement('piazzetta-french-sophistication','cand-1907',None,'achieved_french_sophistication_in_book_illustration',42,42,
 'Haskell says Piazzetta could achieve an entirely French sophistication in work for Albrizzi.',
 excerpt(42,'Indeed, on other occasions when working for Albrizzi','entirely French sophistication'),
 'This is Haskell’s stylistic assessment, illustrated by the 1747 frontispiece described separately.',
 ['cand-1907','cand-0025'])
add_statement('piazzetta-designed-platnerus-frontispiece','cand-1907','cand-10004','designed_frontispiece_for_institutiones_chirurgicae_in_1747',42,43,
 'In 1747 Piazzetta designed a frontispiece for Platnerus’ Institutiones Chirurgicae.',
 cross_excerpt(42,43,'as he showed in 1747 when designing a frontispiece','Chirurgicae.'),
 'The book title continues at S0 line 43. Haskell calls the book “the most unpromising”; this evaluative phrase is not treated as a bibliographic fact.',
 ['cand-1907','cand-10004','cand-10009','cand-1961'],extra={**pending_note(1),'relation_candidate':True})
add_statement('guardi-brothers-plagiarised-gerusalemme-illustrations','cand-9999','cand-9998','plagiarised_piazzetta_illustrations_in_canvas_series',43,44,
 'Haskell says the Guardi brothers plagiarised Piazzetta’s Gerusalemme Liberata illustrations in a series of large decorative canvases depicting scenes from the poem.',
 '\n'.join([excerpt(43,'Meanwhile in Venice the Guardi brothers','illustrations for the'),excerpt(44,'Gerusalemme Liberata','the poem.2')]),
 'This is Haskell’s attribution. The passage does not identify which brother made individual canvases; note 2’s collection locations await L196.',
 ['cand-9999','cand-1242','cand-1250','cand-9998','cand-1913','cand-9990','cand-2545'],extra={**pending_note(2),'relation_candidate':True})
add_statement('albrizzi-felt-debt-to-piazzetta','cand-0025','cand-1901','felt_debt_to_artist_friend',45,45,
 'Haskell says Albrizzi was aware of the debt he owed to his friend Piazzetta.',
 excerpt(45,'Albrizzi was well aware of the debt','his friend.'),
 'This reports Haskell’s characterization of their friendship and debt; it does not specify a monetary amount or legal obligation.',
 ['cand-0025','cand-1901'])
add_statement('piazzetta-died-in-1754','cand-1901',None,'died_in_1754',45,45,
 'Haskell dates Piazzetta’s death to 1754.',
 excerpt(45,'Piazzetta’s death in 1754','in 1754'),
 'The passage gives the year only; it supplies no day or month.',
 ['cand-1901'])
add_statement('albrizzi-published-piazzetta-life-account','cand-0025','cand-10001','published_account_of_piazzetta_life',45,45,
 'After Piazzetta’s death in 1754, Albrizzi published an account of Piazzetta’s life.',
 excerpt(45,'After Piazzetta’s death in 1754 he published an account','his Use'),
 'The wording gives a sequence after the 1754 death, not an exact publication year. The account’s title and full bibliographic record remain unresolved.',
 ['cand-0025','cand-1901','cand-10001'],extra={'relation_candidate':True})
add_statement('piazzetta-life-account-prefaced-drawings','cand-10001','cand-10000','prefaced_collection_of_academic_drawings',45,45,
 'Albrizzi’s account of Piazzetta’s life served as the preface to a collection of the artist’s academic drawings.',
 excerpt(45,'an account of his Use as the preface','academic drawings'),
 'The collection format and title are not supplied here; the nearby printed note 5 citation to “Memorie” is not assumed to identify this preface without checking L199.',
 ['cand-10001','cand-10000','cand-1901'],extra={'relation_candidate':True})
add_statement('albrizzi-kept-piazzetta-memory-alive','cand-0025','cand-1901','worked_to_preserve_piazzetta_memory',45,45,
 'Haskell says Albrizzi did everything he could to keep Piazzetta’s memory alive.',
 excerpt(45,'he did everything he could','keep his memory alive.'),
 'This is Haskell’s characterization of Albrizzi’s memorial efforts.',
 ['cand-0025','cand-1901'])
for suffix,artist,cid in [('novelli','Pietro Antonio Novelli','cand-1758'),('zais','Giuseppe Zais','cand-2830'),('longhi','Alessandro Longhi','cand-1424')]:
    add_statement(f'{suffix}-provided-drawings-for-albrizzi-firm',cid,'cand-9799','provided_occasional_drawings_for_publishing_firm',46,47,
     f'Haskell says {artist} provided occasional drawings for Albrizzi’s firm.',
     '\n'.join([excerpt(46,'Pietro Antonio','Pietro Antonio'),excerpt(47,'Novelli, Giuseppe Zais and Alessandro Longhi','the firm,3')]),
     'The preceding sentence says Albrizzi employed other illustrators; “firm” is mapped provisionally to the indexed Stamperia Albrizziana pending S3 alignment.',
     [cid,'cand-0025','cand-9799'],extra={**pending_note(3),'relation_candidate':True})
add_statement('albrizzi-shop-flourishing-artistic-centre','cand-9799','cand-2719','shop_became_flourishing_artistic_centre_in_venice',47,47,
 'Haskell says Albrizzi’s shop became one of Venice’s most flourishing artistic centres.',
 excerpt(47,'his shop became one of the most flourishing','artistic centres in Venice,'),
 'This is Haskell’s characterization; “shop” is retained as the publishing establishment, not asserted to be a separate institution from the firm.',
 ['cand-9799','cand-0025','cand-2719'])
add_statement('adam-authored-diocletian-palace-book','cand-0013','cand-10002','authored_book_on_diocletian_palace',48,48,
 'Robert Adam had a book on Diocletian’s palace.',
 excerpt(48,'his book on Diocletian’s palace','his book on Diocletian’s palace'),
 'The passage does not supply the book’s title or establish the palace’s exact identity.',
 ['cand-0013','cand-10002','cand-10003'],extra={'relation_candidate':True})
add_statement('adam-entrusted-book-sale-to-albrizzi','cand-0013','cand-0025','entrusted_albrizzi_with_book_sale_in_1761',48,48,
 'When Robert Adam passed through Venice in 1761, he entrusted Albrizzi with the sale of his book on Diocletian’s palace.',
 excerpt(48,'Robert Adam realised when he passed through in 1761','palace.4'),
 'The source says Albrizzi was entrusted with sale; it does not state that he printed or published Adam’s book. Printed note 4 is pending L198.',
 ['cand-0013','cand-0025','cand-10002','cand-10003','cand-2719'],extra={**pending_note(4),'relation_candidate':True})
add_statement('albrizzi-owned-piazzetta-private-collection','cand-0029','cand-10007','owned_several_hundred_drawings_and_many_paintings_by_piazzetta',49,49,
 'Haskell says Albrizzi owned several hundred drawings and many paintings by Piazzetta.',
 excerpt(49,'He owned several hundred drawings','many paintings by Piazzetta,'),
 'The quantities are approximate (“several hundred” and “many”); the passage gives no inventory. The group is distinct from the published academic-drawing collection.',
 ['cand-0029','cand-10007','cand-1901'],extra={'relation_candidate':True})
add_statement('albrizzi-proud-of-sacrifice-of-iphigenia','cand-0029','cand-1921','particularly_proud_of_piazzetta_sacrifice_of_iphigenia',49,49,
 'Haskell says the Sacrifice of Iphigenia was among Albrizzi’s Piazzetta paintings and that Albrizzi was particularly proud of it.',
 excerpt(49,'including a Sacrifice of Iphigenia','particularly proud,5'),
 'The printed note 5 cites “[G. B. Albrizzi]: Memorie”; its full note record at L199 remains pending.',
 ['cand-0029','cand-1921','cand-1901'],extra={**pending_note(5),'relation_candidate':True})
add_statement('albrizzi-admired-carriera','cand-0025','cand-0581','was_special_admirer_of_rosalba_carriera',49,49,
 'Haskell calls Albrizzi a special admirer of Rosalba Carriera.',
 excerpt(49,'he was a special admirer of','Rosalba Carriera.'),
 'The statement records Haskell’s description and does not infer a personal friendship or commission.',
 ['cand-0025','cand-0581'])
add_statement('albrizzi-patronised-zuccarelli','cand-0025','cand-2879','patronised_landscape_artist',49,49,
 'Haskell says Albrizzi patronised the landscape artist Francesco Zuccarelli.',
 excerpt(49,'he patronised the landscape artists Francesco Zuccarelli','Zuccarelli'),
 'The statement records the named patronage claim without inferring individual commissions.',
 ['cand-0025','cand-2879'],extra={'relation_candidate':True})
add_statement('albrizzi-patronised-zais','cand-0025','cand-2830','patronised_landscape_artist',49,49,
 'Haskell says Albrizzi patronised the landscape artist Zais.',
 excerpt(49,'and die strangely neglected Zais','for whom he had a high regard.'),
 'Haskell’s patronage statement does not specify each commission; surname/given-name alignment remains for S3.',
 ['cand-0025','cand-2830'],extra={**pending_note(6),'relation_candidate':True})
add_statement('albrizzi-held-high-regard-for-zais','cand-0025','cand-2830','held_high_regard_for_zais',49,49,
 'Haskell says Albrizzi had high regard for Zais.',
 excerpt(49,'for whom he had a high regard','high regard.6'),
 'This is Haskell’s assessment of the patron’s regard; note 6 remains to be migrated at L200.',
 ['cand-0025','cand-2830'],extra={**pending_note(6),'relation_candidate':True})
add_statement('albrizzi-guardiano-of-scuola-in-1770','cand-0025','cand-2351','held_guardiano_office_in_1770',49,49,
 'Haskell says Albrizzi was Guardiano of the Scuola di S. Rocco in 1770.',
 excerpt(49,'When in 1770 he was Guardiano','Scuola di S. Rocco,'),
 'The source supplies the role and year; no start or end date for the office is inferred.',
 ['cand-0025','cand-2351'],extra={'relation_candidate':True})
add_statement('albrizzi-took-zais-pictures-to-august-exhibition','cand-0025','cand-10005','took_two_zais_pictures_to_16_august_exhibition',49,49,
 'While Guardiano in 1770, Albrizzi took two pictures by Zais to the exhibition on 16 August.',
 excerpt(49,'he took two of that artist’s pictures','exhibition on 16 August,'),
 'The picture titles and exact venue are not given. The event is kept distinct from the recurring exhibition series candidate cand-8587.',
 ['cand-0025','cand-2830','cand-10005','cand-10006','cand-8587'],extra={**pending_note(6),'relation_candidate':True})
add_statement('zais-pictures-shown-at-1770-exhibition','cand-10006','cand-10005','shown_at_16_august_1770_exhibition',49,49,
 'Two unidentified Zais pictures were taken to the 16 August 1770 exhibition.',
 excerpt(49,'two of that artist’s pictures','exhibition on 16 August,'),
 'The two paintings are not individually identified; note 6 is pending at L200.',
 ['cand-10006','cand-2830','cand-10005'],extra={**pending_note(6),'relation_candidate':True})
add_statement('albrizzi-attempted-to-help-zais','cand-0025','cand-2830','attempted_to_help_poverty_stricken_painter_with_little_response',49,49,
 'Haskell says Albrizzi tried to help the poverty-stricken Zais, but met with little response.',
 excerpt(49,'his attempts to help','met with little response.'),
 'The page image confirms “the” and “poverty-stricken”; no specific aid or recipient response is identified.',
 ['cand-0025','cand-2830'])
add_statement('albrizzi-died-in-1777-aged-85','cand-0025',None,'died_in_1777_at_age_85',49,49,
 'Haskell says Albrizzi died in 1777 at the age of 85.',
 excerpt(49,'In 1777 this generous publisher died','age of 85'),
 'This conflicts with p.334’s statement that Albrizzi was born in 1699, which would not yield age 85 in 1777. Preserve both source claims without calculating a replacement birth year; resolve at S3/S5.',
 ['cand-0025'],extra={'internal_source_conflict':{'other_statement_id':'st-chp13-p334-albrizzi-birth-and-inherited-business','reason':'p.334 states birth in 1699; p.336 states age 85 at death in 1777. Preserve both source claims pending adjudication.'},'cross_reference_segments':['chp-13:13_CHP-13_intro:l21-30']})
add_statement('albrizzi-influential-patron-evaluation','cand-0025',None,'described_as_one_of_century_most_influential_patrons',49,49,
 'Haskell characterizes Albrizzi as one of the century’s most influential patrons.',
 excerpt(49,'one of the most influential patrons','the century.'),
 'This is Haskell’s evaluative conclusion, not a quantitative ranking.',
 ['cand-0025'])
add_statement('pasquali-produced-luxurious-books','cand-1844',None,'produced_many_fine_and_luxurious_books',49,49,
 'Haskell says Giambattista Pasquali produced many fine and luxurious books.',
 excerpt(49,'Giambattista Pasquali also produced','luxurious books,'),
 'The passage does not identify the books in this general statement; specific works are treated where named.',
 ['cand-1844','cand-9172'])
add_statement('pasquali-outlook-differed-from-albrizzi','cand-1844','cand-0025','had_very_different_outlook_from_albrizzi',49,49,
 'Haskell says Pasquali’s outlook was very different from Albrizzi’s.',
 excerpt(49,'but his outlook was very different','that of Albrizzi.'),
 'This is Haskell’s comparison of the publishers’ outlooks, not a complete contrast of their practices.',
 ['cand-1844','cand-0025'])
add_statement('pasquali-independent-and-vigorous','cand-1844',None,'characterised_as_vigorous_and_independent',49,49,
 'Haskell characterizes Pasquali as vigorous and independent in his opinions.',
 excerpt(49,'He was a vigorous man','independent opinions,'),
 'This is Haskell’s descriptive characterization.',
 ['cand-1844'])
for suffix,friend,cid in [('querini','Angelo Querini','cand-2075'),('pilati','Carlo Antonio Pilati','cand-1930'),('albergati-capacelli','Francesco Albergati-Capacelli','cand-0023')]:
    add_statement(f'pasquali-friend-of-{suffix}','cand-1844',cid,'friend_of_nonconforming_spirit',49,50,
     f'Haskell names {friend} as one of Pasquali’s non-conforming friends.',
     cross_excerpt(49,50,'the friend of non-conforming spirits','Francesco Albergati-Capacelli.'),
     'The source gives these people as examples of Pasquali’s friends; it does not specify the duration or context of each friendship.',
     ['cand-1844',cid],extra=pending_note(7))
speaker='P. E. Gherardi, letter to L. A. Muratori, 12 July 1749 (identified by printed p.336 note 8; consolidated note L202 pending)'
add_statement('gherardi-described-publishers-as-opposites','cand-1844','cand-0025','described_as_complete_opposites_by_gherardi',50,50,
 'Gherardi described Pasquali and Albrizzi as complete opposites.',
 excerpt(50,'They are complete opposites','both men in 1749,8'),
 'The printed note 8 identifies the archival letter and correspondent; the exact archival source has not been independently consulted.',
 ['cand-1844','cand-0025','cand-1155','cand-1717','cand-10008'],speaker=speaker,layer='Haskell quoting an archival letter',extra={**pending_note(8),'relation_candidate':True})
add_statement('gherardi-characterisation-of-publishers-open','cand-1155',None,'contrasted_albrizzi_and_pasquali_character',50,50,
 'In the cited letter, Gherardi characterizes Albrizzi as excessively cautious and poorly supported, and Pasquali as shrewd, well supported, and likely to succeed in his affairs.',
 excerpt(50,'Albrizzi is incapable','gives the impression of'),
 'The quotation is incomplete at p.336 and continues to p.337 S0 L52–59. Printed note 8 identifies P. E. Gherardi; the quoted archival letter is not independently consulted.',
 ['cand-1155','cand-1717','cand-0025','cand-1844','cand-10008'],speaker=speaker,layer='Haskell quoting an archival letter',extra={**pending_note(8),'continuation_status':'open','continuation_to_segment_id':NEXT,'continuation_quote_pending':True,'cross_reference_segments':[NEXT]})

new_mentions.sort(key=lambda r:(int(r['start_char']),int(r['end_char']),r['mention_id']))
for i,left in enumerate(new_mentions):
    a,b=int(left['start_char']),int(left['end_char'])
    for right in new_mentions[i+1:]:
        c,d=int(right['start_char']),int(right['end_char'])
        if c>=b:break
        nested=(a<=c and d<=b and (a,b)!=(c,d)) or (c<=a and b<=d and (a,b)!=(c,d))
        if not nested:raise SystemExit(f'crossing or duplicate mention spans: {left["mention_id"]}/{right["mention_id"]}')

all_candidates=candidates+new_candidates;all_mentions=mentions+new_mentions;all_statements=statements+new_statements
for key in ('candidate_id','mention_id','statement_id'):
    collection={'candidate_id':all_candidates,'mention_id':all_mentions,'statement_id':all_statements}[key]
    vals=[x[key] for x in collection]
    if len(vals)!=len(set(vals)):raise SystemExit(f'duplicate {key}')

coverage[BODY].update({'disposition':'reviewed','migration_status':'partial','source_line_ranges':'L41-50',
 'note':'Printed p.336 body and visible notes reviewed against CHP-13.pdf physical page 5. p.335’s open Gerusalemme sentence closes at L42: Francesco Gerbault’s subscription proposal for an Orlando Furioso edition failed. Printed footnotes 1–8 map to consolidated notes L195–202 and await source-order processing. The Gherardi/Muratori letter named in note 8 is the reported speaker for the opening comparison; its quotation continues to p.337 S0 L52–59. Keep partial until the continuation and notes are linked.'})
coverage[PREVIOUS]['note']='Printed p.335 body reviewed against CHP-13.pdf physical page 4. The p.334 quotation closes at p.335 L33; the p.335 “it inspired” sentence now closes at p.336 L42 with Gerbault’s unsuccessful subscription project. Printed notes 1–3 still await consolidated L192–194; keep partial until those links are applied.'

candidate_rows=sorted(all_candidates,key=lambda r:r['candidate_id'])
mention_rows=sorted(all_mentions,key=lambda r:(r['segment_id'],int(r['start_char']),int(r['end_char']),r['mention_id']))
all_statements.sort(key=lambda r:r['statement_id'])
coverage_rows=[coverage[r['segment_id']] for r in coverage_rows]
print(f'p.336 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; closed 1 p.335 continuation')
print('coverage: p.336 -> reviewed/partial; p.335 sentence closes; notes 1–8 await L195–202; Gherardi quote continues to p.337')
print(f'totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(all_statements)} statements')
if not args.apply:print('dry-run only; no files written');raise SystemExit(0)
paths=[candidate_path,mention_path,statement_path,coverage_path]
for path in paths:
    backup=path.with_name(path.name+BACKUP_SUFFIX)
    if backup.exists():raise SystemExit(f'recovery copy already exists: {backup.name}')
for path in paths:shutil.copy2(path,path.with_name(path.name+BACKUP_SUFFIX))
write_csv(candidate_path,candidate_fields,candidate_rows);write_csv(mention_path,mention_fields,mention_rows);write_jsonl(statement_path,all_statements);write_csv(coverage_path,coverage_fields,coverage_rows)
print(f'applied; four recovery copies created with suffix {BACKUP_SUFFIX}')
