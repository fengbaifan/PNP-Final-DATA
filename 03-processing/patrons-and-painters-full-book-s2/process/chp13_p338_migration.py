"""Controlled S2 migration for printed p.338; dry-run by default."""
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
BODY = 'chp-13:13_CHP-13_intro:l61-68'
PREVIOUS = 'chp-13:13_CHP-13_intro:l52-59'
NEXT = 'chp-13:13_CHP-13_intro:l70-77'
NOTES = 'chp-13:13_CHP-13_intro:l179-251'
PLATES = 'front-matter:00_05_List_of_Plates:l123-138'
SOURCE_SHA = 'c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8'
PDF_SHA = 'da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc'
BACKUP_SUFFIX = '.bak-s2-chp13-p338-20261003'

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='apply reviewed p.338 S2 migration')
args = parser.parse_args()

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        tmp = Path(f.name)
    tmp.replace(path)

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit('canonical chapter 13 Markdown source changed')
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit('registered CHP-13 PDF asset changed')
source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()
expected = {
    61: '[Page 338]',
    62: 'There was no list of subscribers',
    63: 'For the illustrations Pasquali employed the young Pietro Antonio Novelli',
    64: 'Goldoni himself explained the novelty of the undertaking.',
    65: '57b); acting his first rôle in the theatre',
    66: 'Baroque architecture. Among the publishers of sumptuous books',
    67: 'The third of the greater Venetian publishers, Antonio Zatta',
    68: 'Jesuits, whose side he strongly supported.',
}
for line, prefix in expected.items():
    if not source_lines[line - 1].startswith(prefix):
        raise SystemExit(f'canonical source changed at L{line}')

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
statement_by_id = {row['statement_id']: row for row in statements}
coverage = {row['segment_id']: row for row in coverage_rows}
state = (len(candidates), max(int(r['candidate_id'].split('-')[1]) for r in candidates), len(mentions), len(statements))
if state != (9999, 10012, 21358, 9533):
    raise SystemExit(f'unexpected table pre-state: {state}')
for segment_id in (BODY, PREVIOUS, NEXT, NOTES, PLATES):
    if segment_id not in coverage:
        raise SystemExit(f'required coverage row missing: {segment_id}')
if (coverage[BODY]['disposition'], coverage[BODY]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.338 is not queued/pending')
if (coverage[PREVIOUS]['disposition'], coverage[PREVIOUS]['migration_status']) != ('reviewed', 'partial'):
    raise SystemExit('p.337 is not reviewed/partial')
if (coverage[NEXT]['disposition'], coverage[NEXT]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.339 continuation is not queued/pending')
if any(row['segment_id'] == BODY for row in mentions) or any(row['segment_id'] == BODY for row in statements):
    raise SystemExit('p.338 rows already exist')
new_ids = {f'cand-{n}' for n in range(10013, 10024)}
if new_ids & candidate_ids:
    raise SystemExit(f'p.338 candidate IDs already exist: {sorted(new_ids & candidate_ids)}')
if any(row['mention_id'].startswith('m-s2-ch13-p338-') for row in mentions):
    raise SystemExit('p.338 mention IDs already exist')
if any(row['statement_id'].startswith('st-chp13-p338-') for row in statements):
    raise SystemExit('p.338 statement IDs already exist')

body_lines = {n: source_lines[n - 1] for n in range(61, 69)}
segment_text = '\n'.join(body_lines[n] for n in range(61, 69))
new_candidates = []
def add_candidate(cid, name, kind, detail, line):
    row = {field: '' for field in candidate_fields}
    row.update({'candidate_id': cid, 'canonical_name': name, 'suggested_type': kind, 'status': 'open',
                'detail': detail, 'candidate_origin': 'body-mention', 'candidate_source_ref': f'{BODY}#L{line}'})
    new_candidates.append(row)

add_candidate('cand-10013', 'Novelli illustration program for Pasquali’s Goldoni edition',
              'work', 'A group of over one hundred drawings reproduced by engravers, including Goldoni-life frontispieces and illustrations for the plays. The passage does not identify every drawing or engraver; keep separate from the specific accepted volume-2 frontispiece.', 63)
add_candidate('cand-10014', 'Pasquali’s edition of Vignola dedicated to Carlo Lodoli (title unspecified)',
              'archive', 'The passage names an edition of Vignola and quotes its Italian dedication to Lodoli, but supplies no full title or publication date.', 65)
add_candidate('cand-10015', 'Portuguese government (named as a target of Jesuit polemical attacks)',
              'institution', 'The object is completed as “government” at p.339 S0 L71; retain this reviewed-page anchor at the word “Portuguese” and keep the cross-page claim partial until the continuation is reviewed.', 68)
add_candidate('cand-10016', 'Unidentified Jesuit polemical works proposed for publication by Antonio Zatta',
              'archive', 'Haskell says Zatta proposed publishing attacks by Jesuits on their enemies; titles and actual publication status are not given in the reviewed passage.', 68)
add_candidate('cand-10017', 'Unidentified Venetian authorities involved in disputes over Jesuit affairs',
              'institution', 'Haskell refers generally to authorities hostile to the Society of Jesus; the specific bodies or officials are not identified in this passage.', 68)
add_candidate('cand-10018', 'Rich professional classes represented in the Goldoni edition illustrations',
              'term', 'A social group depicted in the illustrated scenes as the prosperous but relatively simple mid-eighteenth-century Venetian world; do not equate automatically with other bourgeoisie candidates.', 65)
add_candidate('cand-10019', 'Enlightened bourgeoisie in Haskell’s account of Pasquali’s ideals',
              'term', 'A pan-European social-cultural ideal invoked by Haskell in describing Pasquali; keep distinct pending comparison with other bourgeoisie concepts.', 65)
add_candidate('cand-10020', 'Baroque architecture as the target of Visentini’s attack supported by Pasquali',
              'term', 'The architectural style named as the target of Visentini’s criticism; do not merge with Lodoli’s distinct account of late Baroque architecture without S3 review.', 66)
add_candidate('cand-10021', 'Experimental science popularized for Pasquali’s readers',
              'term', 'The field Haskell says Pasquali brought within reach through illustrated translations; no specific title or scientific claim is supplied here.', 65)
add_candidate('cand-10022', 'Unidentified first comedy written by Goldoni at age nine (as reported by Haskell)',
              'archive', 'The passage mentions Goldoni writing his first comedy at nine as an autobiographical illustration; no title or evidence of a surviving work is given.', 64)
add_candidate('cand-10023', 'Unspecified publications by Giambattista Albrizzi contrasted with Pasquali’s books',
              'archive', 'A comparative group of Albrizzi publications characterized by Haskell as more pompous; no individual title is identified in this sentence.', 65)
all_candidate_ids = candidate_ids | {row['candidate_id'] for row in new_candidates}

new_mentions = []
def line_offset(line):
    return sum(len(body_lines[n]) + 1 for n in range(61, line))

def add_mention(line, surface, cid, note='', occurrence=0):
    raw = body_lines[line]
    positions, cursor = [], 0
    while True:
        at = raw.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f'mention text missing at L{line}: {surface!r} occurrence {occurrence}')
    start = line_offset(line) + positions[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f'mention span mismatch: {surface!r}')
    row = {field: '' for field in mention_fields}
    row.update({'mention_id': f'm-s2-ch13-p338-{len(new_mentions) + 1:03d}', 'segment_id': BODY,
                'candidate_id': cid, 'surface_form': surface, 'start_char': start,
                'end_char': start + len(surface), 'note': note})
    new_mentions.append(row)

def add_cross_mention(first, last, start_text, end_text, cid, note=''):
    text = '\n'.join(body_lines[n] for n in range(first, last + 1))
    start, end = text.find(start_text), text.find(end_text, text.find(start_text))
    if start < 0 or end < 0:
        raise SystemExit(f'cross-line mention boundary missing: {start_text!r}/{end_text!r}')
    surface = text[start:end + len(end_text)]
    begin = line_offset(first) + start
    if segment_text[begin:begin + len(surface)] != surface:
        raise SystemExit(f'cross-line mention span mismatch: {surface!r}')
    row = {field: '' for field in mention_fields}
    row.update({'mention_id': f'm-s2-ch13-p338-{len(new_mentions) + 1:03d}', 'segment_id': BODY,
                'candidate_id': cid, 'surface_form': surface, 'start_char': begin,
                'end_char': begin + len(surface), 'note': note})
    new_mentions.append(row)

# Goldoni edition and its designed illustrations.
add_mention(62, 'the volumes', 'cand-1851')
add_mention(63, 'Pasquali', 'cand-1844')
add_mention(63, 'Pietro Antonio Novelli', 'cand-1760')
add_mention(63, 'Over a hundred drawings', 'cand-10013')
add_mention(64, 'Goldoni', 'cand-1205')
add_mention(64, 'frontispieces', 'cand-0390')
add_mention(64, 'Muses, Apollos, Masks, Satyrs, Apes', 'cand-0390', 'Listed as conventionalized frontispiece imagery, not as separate people or works.')
add_mention(64, 'the frontispiece to each volume', 'cand-10013')
add_mention(64, 'his own life', 'cand-1205')
add_mention(64, 'a young boy of nine', 'cand-1205')
add_mention(64, 'his first comedy', 'cand-10022', 'The work is unnamed and is reported as part of Goldoni’s autobiographical scene.')
add_mention(64, 'his Latin exams', 'cand-1205')
add_mention(64, 'Perugia', 'cand-3532')
add_cross_mention(64, 65, '(Plate', '57b)', 'cand-4079', 'Cross-reference crosses the S0 line break; it points to the accepted volume-2 Goldoni frontispiece.')
add_mention(65, 'acting his first rôle in the theatre', 'cand-1205')
add_mention(65, 'a whole sequence of illustrated biography', 'cand-10013')
add_mention(65, 'these drawings', 'cand-10013')
add_mention(65, 'Novelli', 'cand-1760')
add_mention(65, 'the plays themselves', 'cand-1851')
add_mention(65, 'the rich professional classes', 'cand-10018')
add_mention(65, 'Venice', 'cand-2719')
add_mention(65, 'Pietro Longhi', 'cand-1429')
add_mention(65, 'Goldoni’s enthusiasm', 'cand-1205')
add_mention(65, 'Pasquah’s books', 'cand-1844', 'S0 OCR surname correction is registered below; anchor preserves source spelling.')
add_mention(65, 'Novelli’s drawings', 'cand-10013')
add_mention(65, 'Albrizzi’s pubheations', 'cand-10023', 'S0 OCR reads “pubheations”; the scan reads “publications”.')
add_mention(65, 'Albrizzi', 'cand-0025', occurrence=0)
add_mention(65, 'that enlightened bourgeoisie', 'cand-10019')
add_mention(65, 'experimental science', 'cand-10021')
add_mention(65, 'the Abbé Nollet', 'cand-1748')
add_mention(65, 'Paris', 'cand-4653')
add_mention(65, 'his edition of Vignola', 'cand-10014')
add_mention(65, 'Padre Carlo Lodoli', 'cand-1411')
add_mention(65, 'Visentini', 'cand-2783')
add_mention(66, 'Baroque architecture', 'cand-10020')
add_mention(66, 'the publishers of sumptuous books', 'cand-2068')
add_mention(66, 'Venice', 'cand-2719')
# Zatta and the Jesuit controversy; the sentence continues onto p.339.
add_mention(67, 'The third of the greater Venetian publishers', 'cand-2068')
add_mention(67, 'Antonio Zatta', 'cand-2865')
add_mention(68, 'Zatta', 'cand-2865')
add_mention(68, 'the Jesuits', 'cand-1321')
add_mention(68, 'whose side', 'cand-1321', 'Anaphoric reference to the Jesuits.')
add_mention(68, 'the Society', 'cand-1321', 'Anaphoric reference to the Society of Jesus.')
add_mention(68, 'the authorities', 'cand-10017')
add_mention(68, 'the Inquisitori', 'cand-9739')
add_mention(68, 'attacks by the Jesuits', 'cand-10016')
add_mention(68, 'the local-Dominicans', 'cand-0941')
add_mention(68, 'the Portuguese', 'cand-10015', 'This noun phrase continues as “Portuguese government” at p.339 L71; continuation is not yet reviewed.')

new_statements = []
ocr_corrections = [
    {'source_line': 64, 'ocr': 'général run', 'print': 'general run', 'basis': 'CHP-13.pdf physical page 7.'},
    {'source_line': 65, 'ocr': 'Pasquah’s', 'print': 'Pasquali’s', 'basis': 'CHP-13.pdf physical page 7.'},
    {'source_line': 65, 'ocr': 'pubheations', 'print': 'publications', 'basis': 'CHP-13.pdf physical page 7.'},
    {'source_line': 65, 'ocr': 'suture', 'print': 'future', 'basis': 'CHP-13.pdf physical page 7.'},
]

def excerpt(line, start, end):
    text = body_lines[line]
    a = text.find(start)
    b = text.find(end, a)
    if a < 0 or b < 0:
        raise SystemExit(f'quote boundary missing at L{line}: {start!r}/{end!r}')
    return text[a:b + len(end)]

def cross_excerpt(first, last, start, end):
    text = '\n'.join(body_lines[n] for n in range(first, last + 1))
    a = text.find(start)
    b = text.find(end, a)
    if a < 0 or b < 0:
        raise SystemExit(f'cross-line quote boundary missing: {start!r}/{end!r}')
    return text[a:b + len(end)]

def pending_note(marker):
    return {'footnote_marker': marker, 'footnote_printed_page': 338, 'footnote_text_pending': True,
            'footnote_segment': NOTES, 'footnote_body_link_status': 'pending',
            'cross_reference_segments': [NOTES]}

def add_statement(suffix, subject, obj, predicate, start_line, end_line, claim, quote,
                  qualification, mentioned, *, speaker='Haskell', layer='authorial narrative', extra=None):
    sid = f'st-chp13-p338-{suffix}'
    if sid in statement_by_id or any(row['statement_id'] == sid for row in new_statements):
        raise SystemExit(f'duplicate statement ID: {sid}')
    if quote not in segment_text:
        raise SystemExit(f'statement quote not anchored in S0: {sid}')
    ids = mentioned + [x for x in (subject, obj) if x]
    if any(cid not in all_candidate_ids for cid in ids):
        raise SystemExit(f'missing candidate FK: {sid}')
    qualifiers = {'source_line_start': start_line, 'source_line_end': end_line,
                  'printed_page': 338, 'pdf_physical_page': 7, 'claim': claim,
                  'speaker': speaker, 'text_layer': layer, 'qualification': qualification,
                  'mentioned_candidate_ids': mentioned,
                  'ocr_corrections': [item for item in ocr_corrections
                                      if start_line <= item['source_line'] <= end_line]}
    if extra:
        qualifiers.update(extra)
    new_statements.append({'statement_id': sid, 'segment_id': BODY,
                           'subject_candidate_id': subject or None, 'object_candidate_id': obj or None,
                           'predicate': predicate, 'qualifiers': qualifiers,
                           'original_quote': quote, 'origin': 'book',
                           'source_file': '02-sources/02-Markdown/13_CHP-13_intro.md'})

add_statement('no-subscribers-wide-public', 'cand-1851', None, 'aimed_at_wide_general_public', 62, 62,
              'The Goldoni edition had no list of subscribers and its volumes were aimed at a wide general public.',
              excerpt(62, 'There was no list of subscribers', 'a wide general public.'),
              'The absence of a subscriber list and intended broad audience are both stated on p.338.',
              ['cand-1851'])
add_statement('novelli-employed-for-goldoni-illustrations', 'cand-1844', 'cand-1760',
              'employed_young_novelli_for_illustrations', 63, 63,
              'Pasquali employed the young Pietro Antonio Novelli for the Goldoni edition illustrations while Novelli was beginning to acquire a reputation.',
              excerpt(63, 'Pasquali employed the young Pietro Antonio Novelli', 'beginning to acquire a reputation.'),
              'This records Haskell’s account of Novelli’s career at that time.',
              ['cand-1844', 'cand-1760', 'cand-1851'], extra={'relation_candidate': True})
add_statement('novelli-over-hundred-drawings-reproduced', 'cand-10013', 'cand-1851',
              'required_over_one_hundred_drawings_reproduced_by_engravers', 63, 63,
              'The edition required over one hundred drawings, which were reproduced by various engravers.',
              excerpt(63, 'Over a hundred drawings were required', 'various engravers.'),
              'The source gives an approximate lower-bound quantity and does not name the engravers.',
              ['cand-10013', 'cand-1760', 'cand-1851'], extra={'relation_candidate': True})
add_statement('goldoni-explained-illustration-novelty', 'cand-1205', 'cand-1851',
              'explained_novelty_of_illustration_program', 64, 64,
              'Goldoni explained the novelty of the illustration undertaking for the edition.',
              excerpt(64, 'Goldoni himself explained the novelty', 'the undertaking.'),
              'The following account is Haskell’s presentation of Goldoni’s explanation.',
              ['cand-1205', 'cand-1851'], speaker='Haskell reporting Goldoni')
add_statement('goldoni-criticised-conventional-frontispieces', 'cand-1205', 'cand-0390',
              'criticised_common_frontispiece_repertory_as_exhausted', 64, 64,
              'Goldoni was tired of common frontispieces using Muses, Apollos, Masks, Satyrs, Apes and similar motifs, which artists could no longer treat in a new way.',
              excerpt(64, 'He was tired of the général run of frontispieces', 'any new way of treating them.'),
              'This is Goldoni’s criticism as reported by Haskell; the examples are not separate historical actors or works.',
              ['cand-1205', 'cand-0390'], speaker='Carlo Goldoni (reported by Haskell)',
              layer='author quoted or paraphrased in Haskell')
add_statement('goldoni-general-symbols-no-longer-attracted-public', 'cand-1205', 'cand-0390',
              'said_generalised_symbols_no_longer_attracted_public', 64, 64,
              'Goldoni said generalized frontispiece symbols no longer attracted public interest.',
              excerpt(64, 'such generalised symbols no longer attracted', 'interest of the public.'),
              'This is Goldoni’s assessment of public taste, not a measured audience study.',
              ['cand-1205', 'cand-0390'], speaker='Carlo Goldoni (reported by Haskell)',
              layer='author quoted or paraphrased in Haskell')
add_statement('goldoni-proposed-life-scenes-on-frontispieces', 'cand-1205', 'cand-10013',
              'proposed_frontispiece_scene_from_his_life_for_each_volume', 64, 64,
              'Goldoni proposed that each volume’s frontispiece show a scene from his own life.',
              excerpt(64, 'from that love of novelty', 'represent a scene from his own life.'),
              'The proposal is directly attributed to Goldoni; no claim is made here about every volume’s completed frontispiece.',
              ['cand-1205', 'cand-10013'], speaker='Carlo Goldoni (quoted by Haskell)',
              layer='author quoted in Haskell', extra={**pending_note(1), 'relation_candidate': True})
add_statement('goldoni-biographical-episodes-in-illustrations', 'cand-10013', 'cand-1205',
              'illustrated_autobiographical_episodes', 64, 65,
              'The illustrated life sequence showed Goldoni at nine writing his first comedy, passing Latin examinations in Perugia, and acting his first theatrical role dressed as an old woman.',
              cross_excerpt(64, 65, 'Thus we come across him as a young boy of nine', 'a whole sequence of illustrated biography.'),
              'Goldoni’s first comedy is unnamed; Plate 57b is separately identified with the volume-2 frontispiece. The printed note 1 awaits consolidated L209.',
              ['cand-10013', 'cand-10022', 'cand-1205', 'cand-3532', 'cand-4079'],
              extra={**pending_note(1), 'cross_reference_segments': [NOTES, PLATES]})
add_statement('illustrated-intimacy-affected-play-plates', 'cand-10013', 'cand-1851',
              'intimacy_and_public_confidence_affected_play_illustrations', 65, 65,
              'Haskell says the intimacy of the autobiographical drawings and the invitation to public confidence affected Novelli’s illustrations for Goldoni’s plays.',
              excerpt(65, 'The intimacy of these drawings', 'to illustrate the plays themselves.'),
              'This is Haskell’s account of an effect on the play illustrations, not proof of Goldoni’s private intentions beyond the passage.',
              ['cand-10013', 'cand-1760', 'cand-1205', 'cand-1851'])
add_statement('novelli-scenes-depict-venetian-professional-world', 'cand-10013', None,
              'depicted_prosperous_modest_venetian_professional_classes_mid_eighteenth_century', 65, 65,
              'Haskell says the plays’ illustrated scenes show the prosperous but relatively simple world of mid-eighteenth-century Venice’s rich professional classes.',
              excerpt(65, 'The scene is set in the prosperous', 'mid-eighteenth-century Venice,'),
              'This is Haskell’s social-historical interpretation of the represented scenes.',
              ['cand-10013', 'cand-10018', 'cand-2719'])
add_statement('haskell-longhi-comparison-and-vivid-period-impression', 'cand-10013', 'cand-1429',
              'claimed_no_other_source_as_vivid_as_these_illustrations', 65, 65,
              'Haskell says no other source, certainly not Pietro Longhi’s pictures, gives as vivid an impression of the period.',
              excerpt(65, 'from no other source', 'such a vivid impression of the period.'),
              'This is Haskell’s comparative evaluation, not an objective exclusion of other evidence.',
              ['cand-10013', 'cand-1429', 'cand-1205'])
add_statement('haskell-praised-drawings-quality', 'cand-10013', None,
              'drawings_delicate_and_refined_justified_goldoni_enthusiasm', 65, 65,
              'Haskell describes the drawings as delicate and refined and says their quality justified Goldoni’s enthusiasm.',
              excerpt(65, 'The quality of the drawings', 'justify Goldoni’s enthusiasm.'),
              'This is an aesthetic evaluation attributed to Haskell.',
              ['cand-10013', 'cand-1205'])
add_statement('pasquali-books-shared-audience-and-lacked-pomp', 'cand-1844', 'cand-0025',
              'books_shared_audience_but_lacked_albrizzi_pomp', 65, 65,
              'Haskell says most Pasquali books targeted the same public represented in Novelli’s drawings and lacked the pomp of Albrizzi’s publications.',
              excerpt(65, 'As in most of Pasquah’s books', 'characterises Albrizzi’s pubheations.'),
              'The OCR surname and publications spelling are corrected against the page image; “most” remains a qualifier.',
              ['cand-1844', 'cand-10013', 'cand-10023', 'cand-0025'])
add_statement('pasquali-ideals-enlightened-bourgeoisie', 'cand-1844', 'cand-8131',
              'represented_ideals_of_enlightened_bourgeoisie', 65, 65,
              'Haskell associates Pasquali’s ideals with the enlightened bourgeoisie in whose future hopes were placed across Europe.',
              excerpt(65, 'His were the ideals of that enlightened bourgeoisie', 'all over Europe.'),
              'This is Haskell’s broad social interpretation, not a claim that all European hopes were uniform.',
              ['cand-1844', 'cand-10019'])
add_statement('pasquali-brought-experimental-science-within-reach', 'cand-1844', 'cand-1852',
              'popularised_experimental_science_through_illustrated_translations', 65, 65,
              'Haskell says Pasquali brought experimental science within reach through witty illustrated translations of the Abbé Nollet’s latest works in Paris.',
              excerpt(65, 'He brought experimental science within its reach', 'the Abbé Nollet in Paris;'),
              'The translation titles are not supplied in this passage; retain the S1 works-of-scientific-popularization candidate.',
              ['cand-1844', 'cand-1852', 'cand-10021', 'cand-1748', 'cand-4653'], extra={'relation_candidate': True})
add_statement('pasquali-dedicated-vignola-edition-to-lodoli', 'cand-1844', 'cand-10014',
              'dedicated_vignola_edition_to_carlo_lodoli', 65, 65,
              'Pasquali dedicated his edition of Vignola to Padre Carlo Lodoli with an Italian honorific dedication.',
              excerpt(65, 'he dedicated his edition of Vignola', 'Arti e Scienze’,'),
              'The exact edition title and publication date are not given. Printed note 1 and consolidated L209 remain pending.',
              ['cand-1844', 'cand-10014', 'cand-2775', 'cand-1411'],
              speaker='Haskell quoting Pasquali’s dedication', layer='authorial narrative and quoted dedication',
              extra={**pending_note(1), 'relation_candidate': True})
add_statement('pasquali-supported-visentini-attack-on-baroque', 'cand-1844', 'cand-2783',
              'supported_visentini_attack_on_baroque_architecture', 65, 66,
              'Haskell says Pasquali later supported Visentini’s attack on Baroque architecture.',
              cross_excerpt(65, 66, 'later we find him supporting Visentini’s attack on', 'Baroque architecture.'),
              'The passage does not identify the specific publication or form of support.',
              ['cand-1844', 'cand-2783', 'cand-10020'], extra={'relation_candidate': True})
add_statement('haskell-called-pasquali-most-enlightened-venetian-publisher', 'cand-1844', None,
              'called_most_enlightened_voice_among_sumptuous_book_publishers_in_venice', 66, 66,
              'Haskell calls Pasquali the most “enlightened” voice among Venice’s publishers of sumptuous books.',
              excerpt(66, 'Among the publishers of sumptuous books', 'the most ‘enlightened’ voice in Venice.'),
              'This is Haskell’s evaluative ranking within the stated group.',
              ['cand-1844', 'cand-2068', 'cand-2719'])
add_statement('zatta-third-greater-venetian-publisher', 'cand-2865', 'cand-2068',
              'identified_as_third_greater_venetian_publisher', 67, 67,
              'Haskell introduces Antonio Zatta as the third of the greater Venetian publishers and says he was controversial in politics.',
              excerpt(67, 'The third of the greater Venetian publishers', 'in the political field.'),
              '“Third” follows Haskell’s presentation of Albrizzi and Pasquali; it is not a complete census of publishers.',
              ['cand-2865', 'cand-2068'])
add_statement('zatta-combatively-supported-jesuits', 'cand-2865', 'cand-1321',
              'combatively_supported_jesuits_during_political_controversies', 67, 68,
              'Haskell says Zatta took a combative part in controversies around the Jesuits and strongly supported their side.',
              cross_excerpt(67, 68, 'He took a combative part', 'whose side he strongly supported.'),
              'This summarizes Haskell’s account; printed note 2 cites Zatta letters, pending consolidated L210.',
              ['cand-2865', 'cand-1321', 'cand-2867'], extra={**pending_note(2), 'relation_candidate': True})
add_statement('authorities-opposed-jesuits-and-suppressed-disputes', 'cand-9739', 'cand-1321',
              'authorities_often_opposed_society_and_sought_to_suppress_religious_disputes', 68, 68,
              'Haskell says authorities were often antagonistic to the Society of Jesus and anxious to damp down religious disputes.',
              excerpt(68, 'the authorities, who were often antagonistic', 'religious disputes.'),
              'The source describes authorities generally and does not identify every body or official.',
              ['cand-10017', 'cand-1321'])
add_statement('zatta-unpopular-with-authorities', 'cand-2865', 'cand-10017',
              'became_unpopular_with_authorities_due_to_jesuit_support', 68, 68,
              'Haskell says Zatta’s support for the Jesuits made him unpopular with the authorities.',
              excerpt(68, 'This made him unpopular with the authorities', 'the authorities,'),
              'This is Haskell’s stated causal characterization; the specific officials are not individually identified.',
              ['cand-2865', 'cand-1321', 'cand-10017'], extra={'relation_candidate': True})
add_statement('zatta-proposed-jesuit-polemical-publications', 'cand-2865', 'cand-10016',
              'proposed_to_publish_jesuit_attacks_on_enemies', 68, 68,
              'On two or three occasions Zatta got into trouble with the Inquisitori for proposing to publish Jesuit attacks on enemies at home and abroad, including local Dominicans and the Portuguese government.',
              excerpt(68, 'On two or three occasions Zatta actually ran into trouble', 'the Portuguese'),
              '“Two or three” is approximate. The last target continues at p.339 L71, and note 2 maps to L210; keep the statement open and this segment partial.',
              ['cand-2865', 'cand-9739', 'cand-1321', 'cand-0941', 'cand-10015', 'cand-10016'],
              extra={**pending_note(2), 'relation_candidate': True, 'continuation_status': 'open',
                     'continuation_to_segment_id': NEXT, 'cross_reference_segments': [NEXT, NOTES]})

new_mentions.sort(key=lambda row: (int(row['start_char']), int(row['end_char']), row['mention_id']))
for i, left in enumerate(new_mentions):
    a, b = int(left['start_char']), int(left['end_char'])
    for right in new_mentions[i + 1:]:
        c, d = int(right['start_char']), int(right['end_char'])
        if c >= b:
            break
        nested = (a <= c and d <= b and (a, b) != (c, d)) or (c <= a and b <= d and (a, b) != (c, d))
        if not nested:
            raise SystemExit(f'crossing or duplicate mention spans: {left["mention_id"]}/{right["mention_id"]}')

required = {'cand-0025', 'cand-0390', 'cand-0941', 'cand-1205', 'cand-1321', 'cand-1411',
            'cand-1429', 'cand-1748', 'cand-1760', 'cand-1844', 'cand-1851', 'cand-1852',
            'cand-2068', 'cand-2719', 'cand-2775', 'cand-2783', 'cand-2865', 'cand-2867',
            'cand-3532', 'cand-4079', 'cand-4653', 'cand-9739'}
if required - candidate_ids:
    raise SystemExit(f'required S1/accepted candidates missing: {sorted(required - candidate_ids)}')
all_candidates = sorted(candidates + new_candidates, key=lambda row: row['candidate_id'])
all_mentions = sorted(mentions + new_mentions, key=lambda row: (row['segment_id'], int(row['start_char']), int(row['end_char']), row['mention_id']))
all_statements = sorted(statements + new_statements, key=lambda row: row['statement_id'])
for key, rows in [('candidate_id', all_candidates), ('mention_id', all_mentions), ('statement_id', all_statements)]:
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise SystemExit(f'duplicate {key}')

coverage[BODY].update({'disposition': 'reviewed', 'migration_status': 'partial',
                       'source_line_ranges': 'L61-68',
                       'note': 'Printed p.338 body and visible notes reviewed against CHP-13.pdf physical page 7. Goldoni’s life-scene frontispiece proposal and examples are recorded with the accepted Plate 57b link. Printed footnotes 1–2 map to consolidated L209–210 and await source-order processing. The p.338 sentence on Zatta’s proposed Jesuit attacks continues at p.339 S0 L71; keep partial until continuation and notes are linked.'})

print(f'p.338 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements')
print('coverage: p.338 -> reviewed/partial; notes 1–2 await L209–210; Zatta sentence continues to p.339')
print(f'totals: {len(all_candidates)} candidates, {len(all_mentions)} mentions, {len(all_statements)} statements')
if not args.apply:
    print('dry-run only; no files written')
    raise SystemExit(0)
paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f'recovery copy already exists: {backup.name}')
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, all_candidates)
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, all_statements)
coverage_rows = [coverage[row['segment_id']] for row in coverage_rows]
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f'applied; four recovery copies created with suffix {BACKUP_SUFFIX}')
