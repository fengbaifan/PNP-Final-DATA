"""Controlled S2 migration for printed p.334; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge' / 'tables'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '13_CHP-13_intro.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-13.pdf'
BODY = 'chp-13:13_CHP-13_intro:l21-30'
PREVIOUS = 'chp-13:13_CHP-13_intro:l14-19'
NEXT = 'chp-13:13_CHP-13_intro:l32-39'
NOTES = 'chp-13:13_CHP-13_intro:l179-251'
SOURCE_SHA = 'c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8'
PDF_SHA = 'da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc'
BACKUP_SUFFIX = '.bak-s2-chp13-p334-20261003'

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='apply the reviewed p.334 S2 migration')
args = parser.parse_args()

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)

def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        temporary = Path(stream.name)
    temporary.replace(path)

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit('canonical chapter 13 Markdown source changed')
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit('registered CHP-13 PDF asset changed')
source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()
expected_prefixes = {
    21: '[Page 334]',
    22: 'I suspect that she insists on it in the marriage contract',
    23: '‘I have never seen a scientific or important book',
    24: 'Horace or psalm of David.’ But despite',
    25: 'Three publishers stand out above all the others',
    26: 'Albrizzi was a notable collector of contemporary pictures',
    27: 'Repubblica delle Lettere, which commented',
    28: 'Pisani. He figured prominently among the members',
    29: 'In 1736 he began to bring out a complete edition',
    30: '‘the reputation of Venetian prints',
}
for line_no, prefix in expected_prefixes.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f'canonical source changed at L{line_no}')

candidate_path = TABLES / 'entity-candidates.csv'
mention_path = TABLES / 'mentions.csv'
statement_path = TABLES / 'book-statements.jsonl'
coverage_path = TABLES / 's2-coverage.csv'
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row['candidate_id']: row for row in candidates}
candidate_ids = set(candidate_by_id)
mention_ids = {row['mention_id'] for row in mentions}
statement_by_id = {row['statement_id']: row for row in statements}
statement_ids = set(statement_by_id)
coverage = {row['segment_id']: row for row in coverage_rows}

state = (len(candidates), max(int(row['candidate_id'].split('-')[1]) for row in candidates), len(mentions), len(statements))
if state != (9972, 9985, 21203, 9428):
    raise SystemExit(f'unexpected table pre-state: {state}')
for segment in (BODY, PREVIOUS, NEXT, NOTES):
    if segment not in coverage:
        raise SystemExit(f'required coverage row missing: {segment}')
if (coverage[BODY]['disposition'], coverage[BODY]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.334 body is not queued/pending')
if (coverage[PREVIOUS]['disposition'], coverage[PREVIOUS]['migration_status']) != ('reviewed', 'partial'):
    raise SystemExit('p.333 is not reviewed/partial')
if (coverage[NEXT]['disposition'], coverage[NEXT]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.335 continuation is not queued/pending')
if any(row['segment_id'] == BODY for row in mentions) or any(row['segment_id'] == BODY for row in statements):
    raise SystemExit('p.334 rows already exist')
planned_ids = {f'cand-{n}' for n in range(9986, 9990)}
if candidate_ids & planned_ids:
    raise SystemExit('one or more p.334 candidate IDs already exist')
if any(row['mention_id'].startswith('m-s2-ch13-p334-') for row in mentions):
    raise SystemExit('p.334 mention IDs already exist')
if any(row['statement_id'].startswith('st-chp13-p334-') for row in statements):
    raise SystemExit('p.334 statement IDs already exist')
required_candidates = {
    'cand-0001', 'cand-0024', 'cand-0025', 'cand-0028', 'cand-0369', 'cand-0415',
    'cand-1844', 'cand-1907', 'cand-2351', 'cand-2719', 'cand-2772', 'cand-2865',
    'cand-3462', 'cand-5317', 'cand-5529', 'cand-7201', 'cand-9985',
}
missing = required_candidates - candidate_ids
if missing:
    raise SystemExit(f'expected S1/body candidates missing: {sorted(missing)}')
if 'st-chp13-p333-anonymous-quotation-on-poem-collections' not in statement_by_id:
    raise SystemExit('p.333 cross-page quote statement missing')
if 'st-chp13-p333-two-categories-of-illustrated-books' not in statement_by_id:
    raise SystemExit('p.333 book-category statement missing')

body_lines = {line_no: source_lines[line_no - 1] for line_no in range(21, 31)}
segment_text = '\n'.join(body_lines[n] for n in range(21, 31))
new_candidates = []

def add_candidate(cid, name, kind, detail, line_no):
    if cid in candidate_ids or any(row['candidate_id'] == cid for row in new_candidates):
        raise SystemExit(f'candidate ID already exists: {cid}')
    row = {field: '' for field in candidate_fields}
    row.update({'candidate_id': cid, 'canonical_name': name, 'suggested_type': kind, 'status': 'open',
                'detail': detail, 'candidate_origin': 'body-mention', 'candidate_source_ref': f'{BODY}#L{line_no}'})
    new_candidates.append(row)

add_candidate('cand-9986', 'Fine editions of modern and especially ancient authors (second illustrated-book category)', 'term',
              'Haskell’s second broad category of Venetian illustrated books, distinguished from the commemorative poem/eulogy collections. It is a category, not a single publication.', 24)
add_candidate('cand-9987', 'Complete French edition of Jacques-Bénigne Bossuet’s works issued by Giambattista Albrizzi from 1736', 'archive',
              'A multi-volume French-language edition begun in 1736; each volume was dedicated to a member of the Austrian royal family. No exact edition title, volume count, or full imprint is supplied in this passage.', 29)
add_candidate('cand-9988', 'Novelle della Repubblica delle Lettere (weekly literary bulletin)', 'archive',
              'A weekly bulletin edited by Giambattista Albrizzi and described as commenting on and reviewing recent books from across Europe. Publication start date is deferred to the printed footnote and consolidated note migration.', 26)
add_candidate('cand-9989', 'Pisani aristocratic family (branch unspecified in the p.334 account)', 'family',
              'The family is named as especially prominent among aristocratic families in touch with Albrizzi. No individual or branch is specified; do not merge with other Pisani family candidates before S3.', 28)
all_candidate_ids = candidate_ids | {row['candidate_id'] for row in new_candidates}
new_mentions = []

def add_mention(line_no, surface, cid, note='', occurrence=0):
    if cid not in all_candidate_ids:
        raise SystemExit(f'unknown candidate for mention: {surface!r} {cid}')
    line = body_lines[line_no]
    starts, cursor = [], 0
    while True:
        at = line.find(surface, cursor)
        if at < 0: break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f'mention text missing at L{line_no}: {surface!r} occurrence {occurrence}')
    start = sum(len(body_lines[n]) + 1 for n in range(21, line_no)) + starts[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f'mention span mismatch at L{line_no}: {surface!r}')
    row = {field: '' for field in mention_fields}
    row.update({'mention_id': f'm-s2-ch13-p334-{len(new_mentions)+1:03d}', 'segment_id': BODY,
                'candidate_id': cid, 'surface_form': surface, 'start_char': start, 'end_char': end, 'note': note})
    new_mentions.append(row)

add_mention(22, 'Saverio Bettinelli', 'cand-0369', 'Named as the author of the following outburst; p.334 note 1 also identifies Bettinelli as the source cited for the preceding cross-page quotation.')
add_mention(24, 'second class of illustrated books', 'cand-9986')
add_mention(25, 'Giambattista Albrizzi', 'cand-0025')
add_mention(25, 'Giambattista Pasquali', 'cand-1844')
add_mention(25, 'Antonio Zatta', 'cand-2865', 'S1 index page range begins at p.335; the person is named in the p.334 text.')
add_mention(26, 'Albrizzi', 'cand-0025')
add_mention(26, 'Germany', 'cand-5529')
add_mention(26, 'Austria', 'cand-7201')
add_mention(26, 'Vienna', 'cand-2772')
add_mention(26, 'II Forestiere Illuminate', 'cand-0028', 'S0 OCR form; the page image reads Il Forestiere Illuminato.')
add_mention(26, 'Albrizzi', 'cand-0025', occurrence=1)
add_mention(26, 'Almord', 'cand-0024', 'S0 OCR form; the page image reads Almorò.')
add_mention(26, 'Accademia Albrizziana', 'cand-0001')
add_mention(26, 'Novelle della', 'cand-9988', 'First part of the periodical title, continued across the S0 line break at L27.')
add_mention(27, 'Repubblica delle Lettere', 'cand-9988', 'Second part of the periodical title begun at S0 L26.')
add_mention(27, 'Europe', 'cand-3462')
add_mention(28, 'Pisani', 'cand-9989')
add_mention(28, 'Scuola di S. Rocco', 'cand-2351')
add_mention(29, 'Albrizzi', 'cand-0025', 'Anaphoric subject of the 1736 edition and stated aim to reach an international public.')
add_mention(29, 'Albrizzi', 'cand-0027', 'S1 index subentry specifically concerns Albrizzi’s employment of Piazzetta.', occurrence=1)
add_mention(29, 'complete edition in French of the works of Bossuet', 'cand-9987')
add_mention(29, 'Bossuet', 'cand-0415', 'Nested within the mention of the edition of his works.')
add_mention(29, 'Europe', 'cand-3462')
add_mention(29, 'Austrian', 'cand-7201', 'Geographic adjective within “Austrian royal family”; no specific dedicatee is identified.')
add_mention(29, 'Piazzetta', 'cand-1907')
add_mention(30, 'Venetian', 'cand-2719', 'Geographic adjective in the unfinished quotation about Venetian prints.')

new_statements = []
OCR_CORRECTIONS = [
    {'source_line': 22, 'ocr': 'cornplains', 'print': 'complains', 'basis': 'CHP-13.pdf physical page 3.'},
    {'source_line': 26, 'ocr': 'welT', 'print': 'well', 'basis': 'CHP-13.pdf physical page 3.'},
    {'source_line': 26, 'ocr': 'II Forestiere Illuminate', 'print': 'Il Forestiere Illuminato', 'basis': 'CHP-13.pdf physical page 3.'},
    {'source_line': 26, 'ocr': 'Almord', 'print': 'Almorò', 'basis': 'CHP-13.pdf physical page 3.'},
    {'source_line': 27, 'ocr': 'famflies', 'print': 'families', 'basis': 'CHP-13.pdf physical page 3.'},
]

def excerpt(line_no, start_text, end_text):
    line = body_lines[line_no]
    start = line.find(start_text)
    end = line.find(end_text, start)
    if start < 0 or end < 0:
        raise SystemExit(f'quote boundary missing at L{line_no}: {start_text!r} / {end_text!r}')
    return line[start:end+len(end_text)]

def cross_excerpt(first_line, last_line, start_text, end_text):
    text = '\n'.join(body_lines[n] for n in range(first_line, last_line+1))
    start = text.find(start_text)
    end = text.find(end_text, start)
    if start < 0 or end < 0:
        raise SystemExit(f'cross-line quote boundary missing: {start_text!r} / {end_text!r}')
    return text[start:end+len(end_text)]

def pending_note(marker):
    return {'footnote_marker': marker, 'footnote_printed_page': 334, 'footnote_text_pending': True,
            'footnote_segment': NOTES, 'footnote_body_link_status': 'pending', 'cross_reference_segments': [NOTES]}

def add_statement(suffix, subject, obj, predicate, line_start, line_end, claim, quote, qualification, mentioned,
                  *, speaker='Haskell', layer='authorial narrative', extra=None):
    sid = f'st-chp13-p334-{suffix}'
    if sid in statement_ids or any(r['statement_id'] == sid for r in new_statements):
        raise SystemExit(f'statement ID already exists: {sid}')
    if quote not in segment_text:
        raise SystemExit(f'statement quote is not anchored in S0: {sid}')
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f'mentioned-candidate FK missing: {sid}')
    for cid in (subject, obj):
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f'statement endpoint FK missing: {sid}: {cid}')
    q = {'source_line_start': line_start, 'source_line_end': line_end, 'printed_page': 334, 'pdf_physical_page': 3,
         'claim': claim, 'speaker': speaker, 'text_layer': layer, 'qualification': qualification,
         'mentioned_candidate_ids': mentioned,
         'ocr_corrections': [x for x in OCR_CORRECTIONS if line_start <= x['source_line'] <= line_end]}
    if extra: q.update(extra)
    new_statements.append({'statement_id': sid, 'segment_id': BODY, 'subject_candidate_id': subject or None,
                           'object_candidate_id': obj or None, 'predicate': predicate, 'qualifiers': q,
                           'original_quote': quote, 'origin': 'book',
                           'source_file': '02-sources/02-Markdown/13_CHP-13_intro.md'})

# Close the p.333 quotation only after reading its p.334 continuation and printed citation.
prior_quote = statement_by_id['st-chp13-p333-anonymous-quotation-on-poem-collections']
prior_q = prior_quote['qualifiers']
continuation = excerpt(22, 'I suspect that she insists', 'everyone wants it.’')
prior_q.update({
    'claim': 'A quotation attributed by the p.334 printed note to Saverio Bettinelli describes the commemorative verse collections as gifts that were handled roughly, rarely read, yet expected in a bride’s trousseau; the closing lines add that a bride was expected to insist on them in the marriage contract.',
    'speaker': 'Saverio Bettinelli (identified by p.334 printed note 1)',
    'text_layer': 'quotation cited by Haskell; printed note names Bettinelli',
    'qualification': 'The cross-page quotation closes at p.334 S0 L22. The printed note reads “Bettinelli: Lettere inglesi—lettera seconda”; its consolidated endnote record and precise link remain pending. Preserve this as the quoted author’s characterization, not a verified universal practice.',
    'mentioned_candidate_ids': list(dict.fromkeys(prior_q.get('mentioned_candidate_ids', []) + ['cand-0369'])),
    'continuation_status': 'closed_on_p334',
    'continuation_quote_pending': False,
    'continuation_quote': continuation,
    'continuation_quote_segment_id': BODY,
    'continuation_quote_source_line_start': 22,
    'continuation_quote_source_line_end': 22,
    'continuation_footnote_marker': 1,
    'continuation_footnote_printed_page': 334,
    'continuation_footnote_text_pending': True,
    'continuation_footnote_segment': NOTES,
    'speaker_identity_status': 'named_by_printed_footnote',
    'cross_reference_segments': [BODY, NOTES],
})
if prior_quote.get('object_candidate_id') != 'cand-9985':
    raise SystemExit('p.333 collection quote endpoint changed')

prior_categories = statement_by_id['st-chp13-p333-two-categories-of-illustrated-books']
prior_cat_q = prior_categories['qualifiers']
prior_cat_q['claim'] = 'Haskell divides eighteenth-century Venetian illustrated books into two broad categories: commemorative poem/eulogy collections and fine editions of modern, especially ancient, authors.'
prior_cat_q['qualification'] = 'The p.333 passage states the first category; p.334 defines the second as fine editions of modern and especially ancient authors. The passage does not establish that these are exhaustive beyond Haskell’s framing.'
prior_cat_q['mentioned_candidate_ids'] = list(dict.fromkeys(prior_cat_q.get('mentioned_candidate_ids', []) + ['cand-9986']))
prior_cat_q['cross_segment_completion'] = {'segment_id': BODY, 'source_line_start': 24, 'source_line_end': 24}
prior_cat_q['cross_reference_segments'] = [BODY]

add_statement('named-publisher-triad', None, None, 'named_three_publishers_as_leaders_in_enterprise_and_patronage_quality', 25, 25,
              'Haskell singles out Giambattista Albrizzi, Giambattista Pasquali, and Antonio Zatta for enterprise and the quality of their patronage.',
              excerpt(25, 'Three publishers stand out', 'Antonio Zatta.'),
              'This is Haskell’s comparative assessment, not an exhaustive ranking of Venetian publishers.',
              ['cand-0025','cand-1844','cand-2865'])
add_statement('albrizzi-collector-and-publisher', 'cand-0025', None, 'collected_contemporary_pictures_and_published_finely_produced_books', 26, 26,
              'Haskell describes Albrizzi as a notable collector of contemporary pictures and publisher of some of the century’s most finely produced books.',
              excerpt(26, 'Albrizzi was a notable collector', 'books of the century.'),
              'The evaluative terms are Haskell’s; no individual collection or title is identified in this sentence.',
              ['cand-0025'])
add_statement('albrizzi-birth-and-inherited-business', 'cand-0025', None, 'born_1699_and_inherited_fathers_flourishing_publishing_concern', 26, 26,
              'Haskell states that Albrizzi was born in 1699 and inherited a flourishing business from his father.',
              excerpt(26, 'He was born in 1699', 'from his father.'),
              'The father is unnamed; the date and business history are reported by Haskell and the cited note remains pending.',
              ['cand-0025'], extra=pending_note(2))
add_statement('albrizzi-travel-and-vienna-education', 'cand-0025', 'cand-2772', 'travelled_in_germany_and_austria_and_sent_son_to_vienna_for_education', 26, 26,
              'In his youth Albrizzi travelled widely, especially in Germany and Austria, maintained close links there, and sent his son to be educated in Vienna.',
              excerpt(26, 'In his youth he travelled widely', 'educated in Vienna.'),
              'The son is unnamed; “close links” is not converted into a formal relation. The printed note and underlying source require later note processing.',
              ['cand-0025','cand-5529','cand-7201','cand-2772'], extra=pending_note(3))
add_statement('albrizzi-guidebook-1737', 'cand-0025', 'cand-0028', 'published_venice_guide_with_dedication_to_elector_of_saxony_in_1737', 26, 26,
              'Albrizzi first issued the Venice guide Il Forestiere Illuminato in 1737 with a dedication to the Elector of Saxony.',
              excerpt(26, 'one of his most popular books was a guide to Venice', 'Elector of Saxony.'),
              'S0 OCR title “II Forestiere Illuminate” is corrected against the page image. The dedicatee is not individually identified from the title alone.',
              ['cand-0025','cand-0028','cand-2719'], extra={'relation_candidate': True})
add_statement('almoro-organized-academy', 'cand-0024', 'cand-0001', 'organized_literary_and_scientific_society', 26, 26,
              'Albrizzi’s brother Almorò organized the Accademia Albrizziana, which concerned itself with literary and scientific phenomena.',
              excerpt(26, 'His brother Almord organised a society', 'literary and scientific phenomena,'),
              'The OCR name “Almord” is corrected to printed Almorò. The statement records Haskell’s account and does not expand the academy’s membership or institutional history.',
              ['cand-0024','cand-0001'], extra={**pending_note(4), 'relation_candidate': True})
add_statement('albrizzi-edited-weekly-bulletin', 'cand-0025', 'cand-9988', 'edited_weekly_bulletin_reviewing_books_across_europe', 26, 27,
              'Albrizzi edited the weekly Novelle della Repubblica delle Lettere, which commented on and reviewed recent books published across Europe.',
              cross_excerpt(26, 27, 'and he himself edited a weekly bulletin', 'published all over Europe.'),
              'The title is split by the S0 line break. The printed note says publication began in 1729, but that detail is deferred to consolidated-note processing.',
              ['cand-0025','cand-9988','cand-3462'], extra={**pending_note(5), 'relation_candidate': True})
add_statement('albrizzi-catholic-and-aristocratic-connections-inference', 'cand-0025', 'cand-9989', 'inferred_clerical_and_aristocratic_connections_including_pisani', 27, 28,
              'From journal advertisements and dedications, Haskell infers that Albrizzi was a devout and militant Catholic in close contact with clerical circles and leading aristocratic families, especially the Pisani.',
              cross_excerpt(27, 28, 'From the advertisements and dedications', 'Pisani.'),
              'This is explicitly Haskell’s inference from paratexts, not an independently established religious identity or formal relation to a specified Pisani branch.',
              ['cand-0025','cand-9988','cand-9989'], extra={'relation_candidate': True, 'inference_status': 'authorial_inference'})
add_statement('albrizzi-member-and-guardiano-at-san-rocco', 'cand-0025', 'cand-2351', 'member_and_later_guardiano_of_scuola_di_san_rocco', 28, 28,
              'Albrizzi was prominent among members of the Scuola di S. Rocco and became its Guardiano in old age.',
              excerpt(28, 'He figured prominently among the members', 'in his old age.'),
              'The office title and timing are preserved as stated; exact years are not supplied.',
              ['cand-0025','cand-2351'], extra={'relation_candidate': True})
add_statement('publications-reflected-connections', 'cand-0025', None, 'connections_stressed_in_choice_and_style_of_publications', 28, 28,
              'Haskell says these connections are stressed in the selection and style of Albrizzi’s publications.',
              excerpt(28, 'All these connections are stressed', 'style of his publications.'),
              'This is Haskell’s interpretive summary; the specific causal contribution of each connection is not separately demonstrated here.',
              ['cand-0025','cand-9989','cand-2351'])
add_statement('bossuet-french-edition-started-1736', 'cand-0025', 'cand-9987', 'began_complete_french_edition_of_bossuet_works_in_1736', 29, 29,
              'In 1736 Albrizzi began issuing a complete French edition of Bossuet’s works, with each volume dedicated to a member of the Austrian royal family.',
              excerpt(29, 'In 1736 he began to bring out', 'member of the Austrian royal family.'),
              'The edition has no exact title or total volume count in this passage; no particular dedicatee is named. Citation details require note processing.',
              ['cand-0025','cand-9987','cand-0415','cand-7201'], extra={'relation_candidate': True})
add_statement('bossuet-interest-and-heresy-context', 'cand-0415', None, 'renewed_interest_linked_to_spread_of_heresy_across_europe', 29, 29,
              'Haskell links renewed interest in Bossuet at this time to the spread of heretical opinions throughout Europe.',
              excerpt(29, 'The revived interest in Bossuet', 'throughout Europe,'),
              'This is Haskell’s historical interpretation; the supporting Hazard citation is not independently checked and remains pending in the note workflow.',
              ['cand-0415','cand-3462'], extra=pending_note(6))
add_statement('albrizzi-international-audience-goal', 'cand-0025', 'cand-3462', 'aimed_to_reach_wide_international_public_through_original_french', 29, 29,
              'By printing the works in the original French, Albrizzi was clearly hoping to reach a wide international public.',
              excerpt(29, 'by printing the works in the original French', 'wide international public.'),
              'The intention is Haskell’s stated interpretation; it is not direct evidence of sales or readership.',
              ['cand-0025','cand-9987','cand-3462'])
add_statement('piazzetta-first-bossuet-illustrator', 'cand-0025', 'cand-1907', 'employed_piazzetta_as_illustrator_for_first_time_in_this_edition', 29, 29,
              'Haskell identifies the Bossuet edition as the first publication in which Albrizzi employed Piazzetta as an illustrator.',
              excerpt(29, 'the main interest of this splendid publication', 'Piazzetta as his illustrator.'),
              'This is a publisher–artist collaboration candidate tied to the edition; it is not yet a formal S6 relation.',
              ['cand-0025','cand-9987','cand-1907'], extra={'relation_candidate': True})
add_statement('albrizzi-plan-revive-venetian-prints-open', 'cand-0027', None, 'planned_to_revive_reputation_of_venetian_prints', 29, 30,
              'Haskell says Albrizzi had long planned to revive the reputation of Venetian prints, quoting the phrase that continues on p.335.',
              cross_excerpt(29, 30, 'He had for some years been planning to revive', 'fallen in the'),
              'The quoted sentence breaks mid-phrase at p.334 and continues at p.335 S0 L32 onward; do not treat this passage as complete until that segment is read.',
              ['cand-0027','cand-2719'], extra={'continuation_status': 'open', 'continuation_to_segment_id': NEXT,
              'continuation_quote_pending': True, 'cross_reference_segments': [NEXT], 'relation_candidate': True})

# A source named without a specific person remains an unlinked claim, not an invented endpoint.
add_statement('noble-reported-thousand-ducats', None, 'cand-9985', 'unnamed_noble_reported_spending_thousand_ducats_on_collection', 22, 22,
              'Haskell reports that an unnamed noble said he had spent a thousand ducats on a commemorative collection.',
              excerpt(22, 'One noble said that he had spent a thousand ducats', 'on such a collection,'),
              'The noble and the specific collection are not identified; the amount is a reported statement, not independently verified expenditure.',
              ['cand-9985'], speaker='Haskell reporting an unnamed noble', layer='reported speech')
add_statement('bettinelli-criticized-opulent-poem-collection', 'cand-0369', 'cand-9985', 'criticized_luxurious_production_of_ceremonial_verse_publication', 22, 24,
              'Bettinelli’s quoted outburst describes an important or scientific book produced with exceptionally fine paper, engravings, and elaborate frames, and compares its production with classical poetry and scripture.',
              cross_excerpt(23, 24, '‘I have never seen a scientific or important book', 'Horace or psalm of David.’'),
              'Haskell directly names Bettinelli as speaker. Preserve the quotation as his evaluative comparison, not an objective quality ranking.',
              ['cand-0369','cand-9985'], speaker='Saverio Bettinelli as quoted by Haskell', layer='direct quotation')
add_statement('fine-edition-category-produced-striking-designs', 'cand-9986', None, 'fine_editions_generated_many_striking_illustration_designs', 24, 24,
              'Haskell says many striking designs were produced for fine editions of modern and especially ancient authors, the second broad category of illustrated books.',
              excerpt(24, 'it was for the second class of illustrated books', 'many of the most striking designs were produced.'),
              'This is Haskell’s classification and comparative emphasis, not a complete inventory of editions or designs.',
              ['cand-9986'])

# Verify non-overlapping new mention spans within this source segment.
new_mentions.sort(key=lambda row: (int(row['start_char']), int(row['end_char']), row['mention_id']))
for i, left in enumerate(new_mentions):
    a, b = int(left['start_char']), int(left['end_char'])
    for right in new_mentions[i+1:]:
        c, d = int(right['start_char']), int(right['end_char'])
        if c >= b: break
        nested = (a <= c and d <= b and (a,b)!=(c,d)) or (c <= a and b <= d and (a,b)!=(c,d))
        if not nested: raise SystemExit(f'crossing or duplicate mention spans: {left["mention_id"]} / {right["mention_id"]}')

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
if len({r['candidate_id'] for r in all_candidates}) != len(all_candidates): raise SystemExit('duplicate candidate IDs')
if len({r['mention_id'] for r in all_mentions}) != len(all_mentions): raise SystemExit('duplicate mention IDs')
if len({r['statement_id'] for r in all_statements}) != len(all_statements): raise SystemExit('duplicate statement IDs')

coverage[BODY].update({'disposition':'reviewed','migration_status':'partial','source_line_ranges':'L21-30',
    'note':'Printed p.334 body reviewed against CHP-13.pdf physical page 3. The cross-page quotation begun on p.333 closes here and p.334 printed note 1 names Bettinelli; its consolidated note link is pending. Footnotes 1–6 remain to be mapped to consolidated notes L179–251. The final quotation about Albrizzi’s plan to restore Venetian prints continues onto p.335 S0 L32 onward; retain partial until that continuation and notes are processed.'})
coverage[PREVIOUS]['note'] = 'Printed p.333 body reviewed against CHP-13.pdf physical page 2. The “Bundles of them” quotation now closes on p.334; the p.334 printed note 1 identifies Saverio Bettinelli as its cited source. Caterina Barbarigo’s instructions still have p.333 footnote marker 1 pending consolidated notes L179–251. Keep partial until the citation record is processed and linked.'

candidate_rows = sorted(all_candidates, key=lambda r:r['candidate_id'])
mention_rows = sorted(all_mentions, key=lambda r:(r['segment_id'],int(r['start_char']),int(r['end_char']),r['mention_id']))
all_statements.sort(key=lambda r:r['statement_id'])
coverage_rows = [coverage[r['segment_id']] for r in coverage_rows]
print(f'p.334 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; updated 2 p.333 statements')
print('coverage: p.334 body -> reviewed/partial; p.333 quotation closes with Bettinelli source citation; final p.334 sentence continues to p.335; printed notes remain pending')
print(f'totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(all_statements)} statements')
if not args.apply:
    print('dry-run only; no files written')
    raise SystemExit(0)
paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists(): raise SystemExit(f'recovery copy already exists: {backup.name}')
for path in paths: shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path,candidate_fields,candidate_rows)
write_csv(mention_path,mention_fields,mention_rows)
write_jsonl(statement_path,all_statements)
write_csv(coverage_path,coverage_fields,coverage_rows)
print(f'applied; four recovery copies created with suffix {BACKUP_SUFFIX}')
