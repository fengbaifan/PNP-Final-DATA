"""Controlled S2 migration for printed p.335; dry-run by default."""
import argparse, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TABLES=ROOT/'04-knowledge'/'tables'
SOURCE=ROOT/'02-sources'/'02-Markdown'/'13_CHP-13_intro.md'
PDF=ROOT/'02-sources'/'01-book'/'CHP-13.pdf'
BODY='chp-13:13_CHP-13_intro:l32-39'
PREVIOUS='chp-13:13_CHP-13_intro:l21-30'
PREVIOUS_QUOTE='chp-13:13_CHP-13_intro:l21-30'
NEXT='chp-13:13_CHP-13_intro:l41-50'
NOTES='chp-13:13_CHP-13_intro:l179-251'
SOURCE_SHA='c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8'
PDF_SHA='da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc'
BACKUP_SUFFIX='.bak-s2-chp13-p335-20261003'
parser=argparse.ArgumentParser()
parser.add_argument('--apply',action='store_true',help='apply the reviewed p.335 S2 migration')
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
 32:'[Page 335]',
 33:'eyes not only of our own writers, but in those of foreigners also’.1 This book gave him',
 34:'Europe. The book set a pattern for their future ventures',
 35:'Albrizzi’s patronage of Piazzetta reached its climax',
 36:'Venetian eighteenth-century books—the Gerusalemme Liberata',
 37:'Consul Smith, Rosalba Camera and Pellegrini.',
 38:'For Albrizzi’s relations with Recurti',
 39:'Richard, H, p. 492—quoted by Morazzoni, p. 125.',
}
for n,prefix in expected.items():
    if not source_lines[n-1].startswith(prefix):raise SystemExit(f'canonical source changed at L{n}')

candidate_path=TABLES/'entity-candidates.csv';mention_path=TABLES/'mentions.csv';statement_path=TABLES/'book-statements.jsonl';coverage_path=TABLES/'s2-coverage.csv'
candidate_fields,candidates=read_csv(candidate_path)
mention_fields,mentions=read_csv(mention_path)
coverage_fields,coverage_rows=read_csv(coverage_path)
statements=read_jsonl(statement_path)
candidate_by_id={r['candidate_id']:r for r in candidates}; candidate_ids=set(candidate_by_id)
mention_ids={r['mention_id'] for r in mentions};statement_by_id={r['statement_id']:r for r in statements};statement_ids=set(statement_by_id)
coverage={r['segment_id']:r for r in coverage_rows}
state=(len(candidates),max(int(r['candidate_id'].split('-')[1]) for r in candidates),len(mentions),len(statements))
if state!=(9976,9989,21229,9446):raise SystemExit(f'unexpected table pre-state: {state}')
for sid in (BODY,PREVIOUS,NEXT,NOTES):
    if sid not in coverage:raise SystemExit(f'required coverage row missing: {sid}')
if (coverage[BODY]['disposition'],coverage[BODY]['migration_status'])!=('queued','pending'):raise SystemExit('p.335 is not queued/pending')
if (coverage[PREVIOUS]['disposition'],coverage[PREVIOUS]['migration_status'])!=('reviewed','partial'):raise SystemExit('p.334 is not reviewed/partial')
if (coverage[NEXT]['disposition'],coverage[NEXT]['migration_status'])!=('queued','pending'):raise SystemExit('p.336 continuation is not queued/pending')
if any(r['segment_id']==BODY for r in mentions) or any(r['segment_id']==BODY for r in statements):raise SystemExit('p.335 rows already exist')
planned={f'cand-{n}' for n in range(9990,9997)}
if planned & candidate_ids:raise SystemExit(f'p.335 candidate IDs already exist: {sorted(planned & candidate_ids)}')
if any(r['mention_id'].startswith('m-s2-ch13-p335-') for r in mentions):raise SystemExit('p.335 mention IDs already exist')
if any(r['statement_id'].startswith('st-chp13-p335-') for r in statements):raise SystemExit('p.335 statement IDs already exist')
required={'cand-0025','cand-0027','cand-0415','cand-0421','cand-0581','cand-1545','cand-1862','cand-1907','cand-1913','cand-2068','cand-2111','cand-2188','cand-2401','cand-2440','cand-2545','cand-2719','cand-3462','cand-5317','cand-9987','cand-9988'}
if required-candidate_ids:raise SystemExit(f'required candidates missing: {sorted(required-candidate_ids)}')
prior_id='st-chp13-p334-albrizzi-plan-revive-venetian-prints-open'
if prior_id not in statement_by_id:raise SystemExit('p.334 open statement missing')
body_lines={n:source_lines[n-1] for n in range(32,40)}
segment_text='\n'.join(body_lines[n] for n in range(32,40))
new_candidates=[]
def add_candidate(cid,name,kind,detail,line):
    if cid in candidate_ids or any(x['candidate_id']==cid for x in new_candidates):raise SystemExit(f'candidate ID already exists: {cid}')
    row={f:'' for f in candidate_fields};row.update({'candidate_id':cid,'canonical_name':name,'suggested_type':kind,'status':'open','detail':detail,'candidate_origin':'body-mention','candidate_source_ref':f'{BODY}#L{line}'})
    new_candidates.append(row)
add_candidate('cand-9990','Albrizzi’s illustrated edition of Torquato Tasso’s Gerusalemme Liberata (1745)','archive','Published by Giambattista Albrizzi in 1745 and illustrated by Piazzetta; dedicated to Empress Maria Teresa. Record as this edition, distinct from Tasso’s literary work and later Guardi paintings.',36)
add_candidate('cand-9991','Approximately seventy Piazzetta drawings for Albrizzi’s 1745 Gerusalemme Liberata','work','A group of about seventy drawings prepared for the 1745 edition. Individual drawings are not named in this passage; ownership/provenance awaits p.335 printed note 3 and consolidated note L194.',37)
add_candidate('cand-9992','Schönbrunn Palace','place','Named as the site of luxurious decorations carried out during Maria Teresa’s rule; the source gives no particular room or decorative work in this passage.',36)
add_candidate('cand-9993','Unspecified devotional book published by Recurti with a Piazzetta frontispiece','archive','Piazzetta had already made a frontispiece for this book twelve years before his first enterprise with Albrizzi. Printed note 2 and consolidated note L193 give further bibliographic and artwork details.',33)
add_candidate('cand-9994','Chinoiserie in Piazzetta’s book illustrations','term','A decorative motif/style named among illustrations in the Bossuet volumes; source calls it frankly irrelevant to the text, preserving Haskell’s characterization.',33)
add_candidate('cand-9995','Arcadian Rococo pictures in Piazzetta’s early career','term','Haskell’s stylistic phrase for Piazzetta’s first tentative pictures, contrasted chronologically with his religious altarpieces. Do not collapse with broader Arcadian landscape concepts before S3.',33)
add_candidate('cand-9996','Richard, volume II, page 492 (quoted through Morazzoni, page 125)','archive','Short-form citation attached to Haskell’s statement that the Gerusalemme edition was admired by Abbé Richard. The page image reads “II”; S0 OCR reads “H”. Neither the cited work nor Morazzoni was independently consulted here.',39)
all_candidate_ids=candidate_ids|{r['candidate_id'] for r in new_candidates}
new_mentions=[]
def add_mention(line,surface,cid,note='',occurrence=0):
    if cid not in all_candidate_ids:raise SystemExit(f'unknown candidate for mention {surface!r}: {cid}')
    raw=body_lines[line];positions=[];cursor=0
    while True:
        at=raw.find(surface,cursor)
        if at<0:break
        positions.append(at);cursor=at+1
    if occurrence>=len(positions):raise SystemExit(f'mention text missing at L{line}: {surface!r} occurrence {occurrence}')
    start=sum(len(body_lines[n])+1 for n in range(32,line))+positions[occurrence];end=start+len(surface)
    if segment_text[start:end]!=surface:raise SystemExit(f'mention span mismatch at L{line}: {surface!r}')
    row={f:'' for f in mention_fields};row.update({'mention_id':f'm-s2-ch13-p335-{len(new_mentions)+1:03d}','segment_id':BODY,'candidate_id':cid,'surface_form':surface,'start_char':start,'end_char':end,'note':note});new_mentions.append(row)

add_mention(33,'This book','cand-9987','Anaphoric reference to the Bossuet edition described on p.334.')
add_mention(33,'Albrizzi','cand-0025',occurrence=0)
add_mention(33,'the artist','cand-1907','Anaphoric reference to Piazzetta.')
add_mention(33,'the artist','cand-1907','Anaphoric reference to Piazzetta in the frontispiece sentence.',occurrence=1)
add_mention(33,'Albrizzi','cand-0025',occurrence=1)
add_mention(33,'Piazzetta','cand-1907')
add_mention(33,'a devotional book','cand-9993')
add_mention(33,'Recurti','cand-2111')
add_mention(33,'Albrizzi','cand-0025',occurrence=2)
add_mention(33,'Piazzetta’s','cand-1907','Possessive reference to the artist’s illustration work.')
add_mention(33,'the rest of his work','cand-1907','Anaphoric reference to Piazzetta’s artistic work.')
add_mention(33,'arcadian rococo pictures','cand-9995')
add_mention(33,'Piazzetta','cand-1907',occurrence=2)
add_mention(33,'Albrizzi’s Bossuet','cand-9987')
add_mention(33,'Bossuet','cand-0415','Nested mention within the edition title/reference.')
add_mention(33,'Chinoiserie','cand-9994')
add_mention(35,'Albrizzi’s','cand-0027','S1 subentry concerns his employment of Piazzetta.')
add_mention(35,'Piazzetta','cand-1913')
add_mention(36,'Gerusalemme Liberata','cand-9990')
add_mention(36,'Empress Maria Teresa','cand-1545')
add_mention(36,'Schonbrunn','cand-9992','S0 OCR omits the umlaut; the page image reads Schönbrunn.')
add_mention(36,'Europe','cand-3462')
add_mention(36,'Venice','cand-2719')
add_mention(36,'Marshal Schulenburg','cand-2401')
add_mention(37,'Consul Smith','cand-2440')
add_mention(37,'Rosalba Camera','cand-0581','S0 OCR form; the printed page reads Rosalba Carriera.')
add_mention(37,'Pellegrini','cand-1862','Surname only in the text; mapped to the p.335 index candidate, identity still for S3.')
add_mention(37,'Piazzetta','cand-1913')
add_mention(37,'seventy drawings','cand-9991')
add_mention(37,'Boucher','cand-0421')
add_mention(37,'France','cand-5317')
add_mention(37,'Abbé Richard','cand-2188')
add_mention(38,'Albrizzi','cand-0025')
add_mention(38,'Recurti','cand-2111')
add_mention(38,'Novelle','cand-9988')
add_mention(39,'Richard, H, p. 492','cand-9996','S0 OCR form; the printed page reads Richard, II, p. 492.')
add_mention(39,'Morazzoni, p. 125','cand-9996')

new_statements=[]
OCR=[
 {'source_line':36,'ocr':'Schonbrunn','print':'Schönbrunn','basis':'CHP-13.pdf physical page 4.'},
 {'source_line':37,'ocr':'Rosalba Camera','print':'Rosalba Carriera','basis':'CHP-13.pdf physical page 4.'},
 {'source_line':37,'ocr':'drawings?;','print':'drawings³;','basis':'CHP-13.pdf physical page 4; superscript 3 is a footnote marker.'},
 {'source_line':37,'ocr':'a" success','print':'a success','basis':'CHP-13.pdf physical page 4.'},
 {'source_line':39,'ocr':'Richard, H, p. 492','print':'Richard, II, p. 492','basis':'CHP-13.pdf physical page 4.'},
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
    return {'footnote_marker':marker,'footnote_printed_page':335,'footnote_text_pending':True,'footnote_segment':NOTES,'footnote_body_link_status':'pending','cross_reference_segments':[NOTES]}
def add_statement(suffix,subj,obj,predicate,lstart,lend,claim,quote,qualification,mentioned,*,speaker='Haskell',layer='authorial narrative',extra=None):
    sid=f'st-chp13-p335-{suffix}'
    if sid in statement_ids or any(r['statement_id']==sid for r in new_statements):raise SystemExit(f'statement ID already exists: {sid}')
    if quote not in segment_text:raise SystemExit(f'statement quote is not anchored in S0: {sid}')
    if any(c not in all_candidate_ids for c in mentioned):raise SystemExit(f'mentioned-candidate FK missing: {sid}')
    for c in (subj,obj):
        if c and c not in all_candidate_ids:raise SystemExit(f'statement endpoint FK missing: {sid}: {c}')
    q={'source_line_start':lstart,'source_line_end':lend,'printed_page':335,'pdf_physical_page':4,'claim':claim,'speaker':speaker,'text_layer':layer,'qualification':qualification,'mentioned_candidate_ids':mentioned,'ocr_corrections':[x for x in OCR if lstart<=x['source_line']<=lend]}
    if extra:q.update(extra)
    new_statements.append({'statement_id':sid,'segment_id':BODY,'subject_candidate_id':subj or None,'object_candidate_id':obj or None,'predicate':predicate,'qualifiers':q,'original_quote':quote,'origin':'book','source_file':'02-sources/02-Markdown/13_CHP-13_intro.md'})

# Close the p.334 quotation with its p.335 continuation; defer the consolidated citation record to L192.
prior=statement_by_id[prior_id];q=prior['qualifiers']
continuation=excerpt(33,'eyes not only of our own writers','foreigners also’')
q.update({'claim':'Haskell says Albrizzi intended to restore the reputation of Venetian prints and quotes the closing words of an advertisement in Novelle dated 19 March 1730. The note identifies the advertisement as promoting a proposed edition of St Augustine’s works.',
 'speaker':'Advertisement in Novelle, 19 March 1730 (identified by p.335 printed note 1; individual author unnamed)',
 'text_layer':'Haskell’s report quoting a printed advertisement',
 'qualification':'The quoted sentence closes on p.335. The cited edition is described as proposed, not as published. The full endnote and the identity of its proposed editor/source remain pending consolidated-note processing at L192.',
 'mentioned_candidate_ids':list(dict.fromkeys(q.get('mentioned_candidate_ids',[])+['cand-9988'])),
 'continuation_status':'closed_on_p335','continuation_quote_pending':False,'continuation_quote':continuation,
 'continuation_quote_segment_id':BODY,'continuation_quote_source_line_start':33,'continuation_quote_source_line_end':33,
 'continuation_footnote_marker':1,'continuation_footnote_printed_page':335,'continuation_footnote_text_pending':True,
 'continuation_footnote_segment':NOTES,'speaker_identity_status':'source_named_by_printed_footnote',
 'cross_reference_segments':[BODY,NOTES]})

add_statement('friendship-and-business-partnership', 'cand-0025','cand-1907','formed_friendship_and_business_partnership_after_bossuet_book',33,33,
 'After the Bossuet book, Haskell says Albrizzi and Piazzetta became closely linked in friendship and business partnership.',
 excerpt(33,'Thereafter the two men were so intimately linked','business partnership'),
 'The stated sequence is “thereafter”; do not extend the partnership date or scope beyond Haskell’s account.',
 ['cand-0025','cand-1907'],extra={'relation_candidate':True})
add_statement('artist-buried-in-albrizzi-family-vault', 'cand-0025','cand-1907','artist_buried_in_publisher_family_vault',33,33,
 'Haskell says Albrizzi eventually had Piazzetta buried in his own family vault.',
 excerpt(33,'Albrizzi eventually had the artist buried','family vault.'),
 'The vault and its location are not named; this wording does not establish legal ownership or a separate place endpoint.',
 ['cand-0025','cand-1907'])
add_statement('piazzetta-frontispiece-before-albrizzi-enterprise', 'cand-9993','cand-1907','frontispiece_drawn_by_piazzetta_for_recurti_book',33,33,
 'Twelve years before Piazzetta and Albrizzi’s first enterprise together, Piazzetta had already produced a frontispiece for a devotional book.',
 excerpt(33,'twelve years before their first enterprise together','published by Recurti'),
 'The interval is stated relative to their first enterprise; do not calculate a date until the referent is resolved. The printed note identifies the devotional book and image, but consolidated note L193 remains pending.',
 ['cand-9993','cand-1907','cand-2111'],extra={**pending_note(2),'relation_candidate':True})
add_statement('recurti-published-devotional-book', 'cand-9993','cand-2111','published_devotional_book',33,33,
 'Haskell identifies Recurti as the publisher of the devotional book for which Piazzetta had made a frontispiece.',
 excerpt(33,'a devotional book published by Recurti','published by Recurti'),
 'This is the publisher relation stated in the passage; exact title and imprint details remain pending the printed note and consolidated note L193.',
 ['cand-9993','cand-2111'],extra={**pending_note(2),'relation_candidate':True})
add_statement('albrizzi-close-relations-with-recurti', 'cand-0025','cand-2111','maintained_close_relations_with_recurti',33,33,
 'Haskell says Albrizzi maintained close relations with Recurti, another religiously minded publisher.',
 excerpt(33,'published by Recurti with whom Albrizzi maintained close relations','relations2'),
 'The S0 phrase ends with footnote marker 2. p.335 L38 continues that note by directing readers to Novelle; the full note at consolidated L193 is pending.',
 ['cand-0025','cand-2111','cand-9988'],extra={**pending_note(2),'page_note_continuation':excerpt(38,'For Albrizzi’s relations with Recurti','(passim).'),'relation_candidate':True})
add_statement('piazzetta-monopoly-and-cooperation', 'cand-0025','cand-1907','held_near_monopoly_of_piazzetta_illustration_work_and_cooperated',33,33,
 'For many years Albrizzi enjoyed what Haskell calls an almost complete monopoly of Piazzetta’s work as a book illustrator, and their cooperation shaped Albrizzi’s finest editions.',
 excerpt(33,'but for many years he enjoyed an almost complete monopoly','editions.'),
 'Haskell limits the claim to Piazzetta’s illustration work in this field and qualifies the monopoly as “almost complete.”',
 ['cand-0025','cand-1907'],extra={'relation_candidate':True})
add_statement('piazzetta-bossuet-illustration-series', 'cand-9987','cand-1907','illustrated_bossuet_edition_with_series_of_drawings',33,33,
 'Piazzetta began drawing for Albrizzi’s Bossuet edition a series of vignettes and illustrations unlike his prior work and new to Venetian books.',
 excerpt(33,'Piazzetta began drawing for Albrizzi’s Bossuet','as they were to him.'),
 'This describes the illustrated edition and a series, not individually identified drawings; their approximate count and provenance are separately stated later.',
 ['cand-9987','cand-0415','cand-1907'],extra={'relation_candidate':True})
add_statement('piazzetta-illustration-style-contrast', 'cand-1907',None,'illustration_series_differed_from_painters_other_work',33,33,
 'Haskell characterizes Piazzetta’s illustrations for the worldly publisher as unlike the rest of the artist’s work.',
 excerpt(33,'For the worldly publisher with his wide international contacts','unlike the rest of his work.'),
 'This is Haskell’s stylistic interpretation; it does not define a separate commission or attribute every illustrated motif to a particular volume.',
 ['cand-0025','cand-1907'])
add_statement('piazzetta-style-and-career-sequence', 'cand-1907',None,'drawing_for_bossuet_preceded_arcadian_rococo_pictures_and_coincided_with_religious_altarpieces',33,33,
 'Haskell places Piazzetta’s work on the Bossuet illustrations before his first tentative Arcadian Rococo pictures and during a period when he mainly produced exalted religious altarpieces.',
 excerpt(33,'Long before he painted his first tentative arcadian rococo pictures','exalted religious altarpieces,'),
 'Relative sequence and Haskell’s emphasis are preserved; the text supplies no exact start or end dates for these phases.',
 ['cand-1907','cand-9995'])
add_statement('piazzetta-bossuet-illustration-repertoire', 'cand-9987',None,'illustrations_included_multiple_visual_motifs',33,33,
 'The Bossuet volumes included views, landscapes, small genre scenes, Chinoiserie, putti, religious imagery, and hieratic portraits.',
 excerpt(33,'Views, landscapes, small genre scenes','hieratic portraits,'),
 'Haskell calls some motifs “frankly irrelevant”; preserve that critical description as his judgment, not a factual classification of each image.',
 ['cand-9987','cand-9994'])
add_statement('illustrations-for-central-european-readers', 'cand-9987',None,'illustrations_made_bossuet_volumes_more_digestible_for_archbishops_and_monasteries',33,34,
 'Haskell says the illustrations helped make Bossuet’s extensive volumes more digestible for archbishops and wealthy monasteries in Central Europe.',
 cross_excerpt(33,34,'helped to make digestible the thundering tomes of Bossuet','Europe.'),
 'This is Haskell’s account of readership and effect; no specific monastery or reader is identified.',
 ['cand-9987','cand-0415'])
add_statement('bossuet-edition-set-pattern-and-aesthetic', 'cand-9987','cand-0025','set_pattern_for_future_editions_with_distinctive_style',34,34,
 'Haskell says the Bossuet book set a pattern for later ventures and characterizes Albrizzi’s editions as opulent, aristocratic, often melancholy, and weighty even when frivolous.',
 excerpt(34,'The book set a pattern for their future ventures','other publications.'),
 'These are Haskell’s evaluative generalizations about the editions, not attributes measured across every publication.',
 ['cand-9987','cand-0025'])
add_statement('gerusalemme-1745-edition-and-patronage-climax', 'cand-0025','cand-9990','published_piazzetta_illustrated_gerusalemme_liberata_1745',35,36,
 'Haskell identifies Albrizzi’s 1745 Gerusalemme Liberata as the climax of his patronage of Piazzetta and the most famous Venetian eighteenth-century book.',
 cross_excerpt(35,36,'Albrizzi’s patronage of Piazzetta reached its climax','(Plate 57a).'),
 'The candidate is the 1745 illustrated edition, distinct from Tasso’s literary work and later painted scenes based on the poem.',
 ['cand-0025','cand-1907','cand-1913','cand-2545','cand-9990'],extra={'relation_candidate':True})
add_statement('gerusalemme-dedicated-to-maria-teresa', 'cand-9990','cand-1545','dedicated_to_empress_maria_teresa',36,36,
 'The 1745 edition was dedicated to Empress Maria Teresa.',
 excerpt(36,'It was dedicated to the Empress Maria Teresa','rule at Schonbrunn,'),
 'The dedication is distinguished from sponsorship or commissioning; no specific dedicatory wording is quoted here.',
 ['cand-9990','cand-1545','cand-9992'],extra={'relation_candidate':True})
add_statement('maria-teresa-luxury-associated-with-schonbrunn', 'cand-1545','cand-9992','luxurious_decorations_at_schonbrunn_during_her_rule',36,36,
 'Haskell says Maria Teresa’s taste for luxury is well attested by decorations carried out at Schönbrunn during her rule.',
 excerpt(36,'whose taste for the luxurious is well attested','at Schonbrunn,'),
 'This is Haskell’s characterization and example; no particular room, decorative program, or causal link to the book is asserted.',
 ['cand-1545','cand-9992'])
add_statement('gerusalemme-subscriber-network', 'cand-9990',None,'subscriber_list_included_named_european_and_venetian_figures',36,37,
 'Haskell describes the subscriber list as including people from across Europe and names Marshal Schulenburg, Consul Smith, Rosalba Carriera, and Pellegrini among Venetian connoisseurs and artists.',
 cross_excerpt(36,37,'the list of subscribers provides a glittering series of names','Pellegrini.'),
 'The passage calls these named figures subscribers; Rosalba’s OCR surname is corrected against the page image. Pellegrini is surname-only here and remains subject to S3 identity review.',
 ['cand-9990','cand-2401','cand-2440','cand-0581','cand-1862'],extra={'relation_candidate':True})
add_statement('piazzetta-seventy-drawings-for-gerusalemme', 'cand-9990','cand-9991','illustrated_edition_with_approximately_seventy_drawings',37,37,
 'Piazzetta produced about seventy drawings for the Gerusalemme Liberata edition.',
 excerpt(37,'For this book Piazzetta produced some seventy drawings','dramatic ones'),
 'The footnote marker 3 gives ownership and later location information; consolidated note L194 remains pending. No individual drawing is identified.',
 ['cand-9990','cand-9991','cand-1913'],extra={**pending_note(3),'relation_candidate':True})
add_statement('piazzetta-dramatic-and-pastoral-compositions', 'cand-1913','cand-0421','contrasted_dramatic_and_pastoral_illustration_qualities',37,37,
 'Haskell says Piazzetta’s dramatic drawings reveal difficulty narrating heroic action, while the pastoral scenes resemble Boucher in some qualities but make a less artificial world.',
 excerpt(37,'the dramatic ones show','though Piazzetta’s world is much less artificial.'),
 'This is Haskell’s art-critical judgment and comparison, not a documented opinion by Boucher or a measured influence claim.',
 ['cand-1913','cand-0421'])
add_statement('gerusalemme-success-in-france', 'cand-9990',None,'successful_in_france',37,37,
 'Haskell says the Gerusalemme Liberata edition was a success in France.',
 excerpt(37,'The book was in fact a','success in France.'),
 'The OCR has an extraneous quotation mark before “success”; the page image confirms the reading recorded in ocr_corrections.',
 ['cand-9990','cand-5317'])
add_statement('gerusalemme-admired-by-richard', 'cand-2188','cand-9990','admired_gerusalemme_liberata_edition',37,37,
 'Haskell reports that the edition was much admired by Abbé Richard.',
 excerpt(37,'It was much admired by the Abbé Richard','Richard,4'),
 'The citation in p.335 note 4 is visible locally as Richard, volume II, p.492, quoted through Morazzoni, p.125; those cited works were not independently consulted.',
 ['cand-9990','cand-2188','cand-9996'],extra={'footnote_marker':4,'footnote_printed_page':335,'footnote_text_pending':False,'footnote_segment':BODY,'footnote_body_link_status':'linked_local_segment','citation_locator_candidate_id':'cand-9996','cross_reference_segments':[BODY],'relation_candidate':True})
add_statement('gerusalemme-inspired-next-project-open', 'cand-9990',None,'inspired_subsequent_project_described_on_p336',37,37,
 'Haskell says the book inspired a further project, whose recipient and outcome continue on p.336.',
 excerpt(37,'and it inspired','and it inspired'),
 'The object of “inspired” is not present in this segment; close only after reading p.336 S0 L41–50.',
 ['cand-9990'],extra={'continuation_status':'open','continuation_to_segment_id':NEXT,'continuation_quote_pending':True,'cross_reference_segments':[NEXT]})

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

coverage[BODY].update({'disposition':'reviewed','migration_status':'partial','source_line_ranges':'L32-39',
 'note':'Printed p.335 body and visible notes reviewed against CHP-13.pdf physical page 4. The p.334 quotation closes here; printed note 1 attributes it to a Novelle advertisement, with its consolidated record pending at L192. p.335 markers 1–3 map to consolidated notes L192–194 and remain pending; local footnote 2 continues at L38 and note 4 is transcribed at L39. The statement ending “it inspired” continues on p.336 S0 L41–50. Keep partial until continuation and footnote links are closed.'})
coverage[PREVIOUS]['note']='Printed p.334 body reviewed against CHP-13.pdf physical page 3. Its final quotation now closes on p.335 and p.335 printed note 1 identifies a Novelle advertisement dated 19 March 1730 as source; the consolidated citation at L192 remains pending. p.334 footnotes 1–6 still require note migration; keep partial until those links are applied.'
prior_categories=statement_by_id['st-chp13-p334-albrizzi-plan-revive-venetian-prints-open']

candidate_rows=sorted(all_candidates,key=lambda r:r['candidate_id'])
mention_rows=sorted(all_mentions,key=lambda r:(r['segment_id'],int(r['start_char']),int(r['end_char']),r['mention_id']))
all_statements.sort(key=lambda r:r['statement_id'])
coverage_rows=[coverage[r['segment_id']] for r in coverage_rows]
print(f'p.335 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; updated 1 p.334 statement')
print('coverage: p.335 -> reviewed/partial; p.334 quote closes, notes 1–3 await L192–194; p.335 “it inspired” continues to p.336')
print(f'totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(all_statements)} statements')
if not args.apply:print('dry-run only; no files written');raise SystemExit(0)
paths=[candidate_path,mention_path,statement_path,coverage_path]
for path in paths:
    backup=path.with_name(path.name+BACKUP_SUFFIX)
    if backup.exists():raise SystemExit(f'recovery copy already exists: {backup.name}')
for path in paths:shutil.copy2(path,path.with_name(path.name+BACKUP_SUFFIX))
write_csv(candidate_path,candidate_fields,candidate_rows);write_csv(mention_path,mention_fields,mention_rows);write_jsonl(statement_path,all_statements);write_csv(coverage_path,coverage_fields,coverage_rows)
print(f'applied; four recovery copies created with suffix {BACKUP_SUFFIX}')
