"""Controlled S2 migration for printed p.340; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge' / 'tables'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '13_CHP-13_intro.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-13.pdf'
BODY = 'chp-13:13_CHP-13_intro:l79-88'
PREVIOUS = 'chp-13:13_CHP-13_intro:l70-77'
NOTES = 'chp-13:13_CHP-13_intro:l179-251'
SOURCE_SHA = 'c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8'
PDF_SHA = 'da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc'
BODY_SHA = '661b04d02c9cbf2feda5e28e972bcb16c5375d173d775de71709151c87e2d073'
BACKUP_SUFFIX = '.bak-s2-chp13-p340-20261003'

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='apply reviewed p.340 S2 migration')
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
    79: '[Page 340]',
    80: 'He was born in 1735 and soon acquired a great reputation for learning.',
    81: 'Pinelli a series of portraits of all the Doges',
    82: 'Painting, Typography, Diplomacy and Numismatics.',
    83: 'Print sellers too were often important art patrons',
    84: '. of the firm lay in issuing separate prints.',
    85: 'They specialised in cheap romantic novels',
    86: 'Other particularly important printsellers were the German Joseph Wagner',
    87: "' was established for more than thirty years",
    88: 'Rava, 1911.',
}
for line, prefix in expected.items():
    if not source_lines[line - 1].startswith(prefix):
        raise SystemExit(f'canonical source changed at L{line}')
if hashlib.sha256(('\n'.join(source_lines[78:88])).encode('utf-8')).hexdigest() != BODY_SHA:
    raise SystemExit('p.340 source segment changed')

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

state = (len(candidates), max(int(r['candidate_id'].split('-')[1]) for r in candidates),
         len(mentions), len(statements))
if state != (10023, 10036, 21465, 9579):
    raise SystemExit(f'unexpected table pre-state: {state}')
for segment_id in (BODY, PREVIOUS, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f'required coverage row missing: {segment_id}')
if (coverage[BODY]['disposition'], coverage[BODY]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.340 is not queued/pending')
if (coverage[PREVIOUS]['disposition'], coverage[PREVIOUS]['migration_status']) != ('reviewed', 'partial'):
    raise SystemExit('p.339 is not reviewed/partial')
if (coverage[NOTES]['disposition'], coverage[NOTES]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('chapter 13 notes are not queued/pending')
if any(row['segment_id'] == BODY for row in mentions) or any(row['segment_id'] == BODY for row in statements):
    raise SystemExit('p.340 rows already exist')

new_candidates = []
new_mentions = []
new_statements = []
new_ids = {f'cand-{n}' for n in range(10037, 10059)}
if new_ids & candidate_ids:
    raise SystemExit(f'p.340 candidate IDs already exist: {sorted(new_ids & candidate_ids)}')
if any(row['mention_id'].startswith('m-s2-ch13-p340-') for row in mentions):
    raise SystemExit('p.340 mention IDs already exist')
if any(row['statement_id'].startswith('st-chp13-p340-') for row in statements):
    raise SystemExit('p.340 statement IDs already exist')

body_lines = {n: source_lines[n - 1] for n in range(79, 89)}
segment_text = '\n'.join(body_lines[n] for n in range(79, 89))
line_offsets = {}
offset = 0
for n in range(79, 89):
    line_offsets[n] = offset
    offset += len(body_lines[n]) + 1


def add_candidate(cid, name, kind, detail, line):
    row = {field: '' for field in candidate_fields}
    row.update({'candidate_id': cid, 'canonical_name': name, 'suggested_type': kind,
                'status': 'open', 'detail': detail, 'candidate_origin': 'body-mention',
                'candidate_source_ref': f'{BODY}#L{line}'})
    new_candidates.append(row)


add_candidate('cand-10037', 'Tiepolo (surname-only artist mention in Pinelli’s collection)', 'person',
              'The passage gives only the surname and says that four pictures by a Tiepolo were in Pinelli’s collection. Keep separate from Giambattista and Gian Domenico Tiepolo until S3.', 80)
add_candidate('cand-10038', 'Historical approach to art suggested by Maffeo Pinelli’s collecting', 'term',
              'Haskell infers this interest from the collection’s scholarly completeness and eclecticism and compares Pinelli to Lodoli and others. Preserve the explicitly inferential wording.', 80)
add_candidate('cand-10039', 'Sixteenth-century art as Pinelli’s principal collecting interest', 'term',
              'The source says Pinelli’s real enthusiasm seems to have been for the sixteenth century; it gives no specific preference beyond that period.', 80)
add_candidate('cand-10040', 'Unidentified pictures attributed to old masters in Pinelli’s collection', 'work',
              'Unnamed pictures attributed to Giorgione, Bassano, Veronese, Titian, Palma Giovane, Padovanino and Pietro della Vecchia. “Attributed to” is retained; no individual title or attribution is asserted as settled.', 80)
add_candidate('cand-10041', 'Four unidentified Tiepolo pictures in Pinelli’s collection', 'work',
              'Haskell gives a count of four but no titles or first name for Tiepolo. Do not identify the painter or artworks before global alignment.', 80)
add_candidate('cand-10042', 'Francesco Maggiotto’s series of portraits of all the Doges for Pinelli', 'work',
              'The passage links the series to Plate 68a. Keep its relationship to the three-portrait Plate 68a candidate cand-4190 and the other Maggiotto portrait group cand-3352 unresolved; do not merge them in S2.', 81)
add_candidate('cand-10043', 'Francesco Maggiotto’s portraits of Venetian Popes and Cardinals for Pinelli', 'work',
              'An unnamed portrait group; the source supplies no sitter names, number, titles or locations.', 81)
add_candidate('cand-10044', 'Maggiotto’s allegories of Painting, Typography, Diplomacy and Numismatics for Pinelli', 'work',
              'An unnamed group of allegories. The source does not state whether these were separate canvases or parts of one work.', 81)
add_candidate('cand-10045', 'Print sellers as art patrons', 'term',
              'Haskell generalizes that print sellers were often important art patrons before naming Remondini and other sellers.', 83)
add_candidate('cand-10046', 'Cheap romantic novels in the Remondini market', 'term',
              'A publication genre in the firm’s low-cost market; the passage gives no individual titles.', 85)
add_candidate('cand-10047', 'Remondini devotional prints for display in peasants’ houses', 'work',
              'A group of unnamed devotional prints marketed for domestic display; do not infer their subjects, producers or individual recipients.', 85)
add_candidate('cand-10048', 'Peasants as the domestic audience for Remondini devotional prints', 'term',
              'The passage identifies peasants’ houses as places where the devotional prints were to be hung; it names no individual household or precise geographic scope.', 85)
add_candidate('cand-10049', 'Remondini practice of issuing low-priced facsimiles of other publications', 'procedure',
              'Haskell says the firm produced facsimiles at much reduced prices and characterizes it as having “few scruples”; preserve that criticism as attributed evaluation.', 85)
add_candidate('cand-10050', 'Remondini’s separate-print output (unnamed group)', 'work',
              'Haskell distinguishes the firm’s separate prints from its books and says separate prints were its main activity.', 84)
add_candidate('cand-10051', 'Paintings and drawings produced for extensive reproduction by Remondini', 'work',
              'An unnamed group made by leading artists for extensive reproduction. The passage does not identify individual images or say that every named artist made both paintings and drawings.', 85)
add_candidate('cand-10052', 'Bassano (place of the Remondini firm)', 'place',
              'Named as the place where the Remondini firm was established. Do not confuse the town with the painter Jacopo Bassano.', 83)
add_candidate('cand-10053', 'Ponte de’Baretteri (Furnaletto shop location)', 'place',
              'The source locates Furnaletto’s establishment at this named site for more than thirty years; it gives no absolute opening date.', 87)
add_candidate('cand-10054', 'A. Rava, 1911 (bibliographic citation fragment in printed note 3)', 'archive',
              'S0 L88 contains only the tail “Rava, 1911.” of printed p.340 note 3; S0 L219 ends the same note with “published by A.” Full note text and cited work identity remain pending. Do not infer a title or full author name.', 88)
add_candidate('cand-10055', 'Principal Ducal ceremonies represented in Canaletto drawings for Furnaletto', 'event',
              'The ceremonies are not named individually or dated in this passage; retain only their role as the subject of the commissioned drawings.', 87)
add_candidate('cand-10056', 'International clientele of the Remondini print market', 'term',
              'Haskell says the firm began to acquire an international clientele as it expanded around the middle of the eighteenth century; no markets or clients are named.', 85)
add_candidate('cand-10057', 'Unnamed established publishing institutions competing with Remondini', 'institution',
              'The passage describes more established institutions as Remondini’s rivals and says they greeted the firm’s arrival with hostility; it names none of them.', 85)
add_candidate('cand-10058', 'Different public served by the Remondini market from the great enterprises', 'term',
              'Haskell distinguishes the audience served by Remondini from the public of larger enterprises; this audience comparison is separate from the later reference to an international clientele.', 84)

all_candidate_ids = candidate_ids | {row['candidate_id'] for row in new_candidates}


def add_mention(line, surface, cid, note='', occurrence=0):
    raw_line = body_lines[line]
    positions, cursor = [], 0
    while True:
        at = raw_line.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f'mention text missing at L{line}: {surface!r} occurrence {occurrence}')
    start = line_offsets[line] + positions[occurrence]
    row = {field: '' for field in mention_fields}
    row.update({'mention_id': f'm-s2-ch13-p340-{len(new_mentions) + 1:03d}',
                'segment_id': BODY, 'candidate_id': cid, 'surface_form': surface,
                'start_char': start, 'end_char': start + len(surface), 'note': note})
    new_mentions.append(row)


def excerpt(first, last, start_text, end_text):
    local_text = '\n'.join(body_lines[n] for n in range(first, last + 1))
    start = local_text.find(start_text)
    if start < 0:
        raise SystemExit(f'statement opening text missing: {start_text!r}')
    end = start if start_text == end_text else local_text.find(end_text, start + len(start_text))
    if end < 0:
        raise SystemExit(f'statement closing text missing after {start_text!r}: {end_text!r}')
    quote = local_text[start:end + len(end_text)]
    if quote not in segment_text:
        raise SystemExit(f'statement quote not anchored: {quote!r}')
    return quote


def note_ref(marker, lines):
    return {'footnote_marker': str(marker), 'footnote_printed_page': 340,
            'footnote_text_pending': True, 'footnote_segment': NOTES,
            'footnote_line_range': lines, 'footnote_body_link_status': 'pending'}


corrections = [
    {'source_line': 84, 'ocr': '. of the firm', 'print': '- of the firm',
     'basis': 'CHP-13.pdf physical page 9 visibly has a line-start dash; S0 OCR reads a period.'},
    {'source_line': 86, 'ocr': '.to printers', 'print': 'to printers',
     'basis': 'CHP-13.pdf physical page 9 reads “significance to printers”; S0 inserted a period.'},
    {'source_line': 87, 'ocr': "' was established", 'print': 'was established',
     'basis': 'CHP-13.pdf physical page 9 has no apostrophe before “was”; S0 OCR inserted one.'},
]


# Entity and work-group mentions. Repeated names keep their S1 candidates; unresolved surnames stay open.
mention_specs = [
    (80, 'He', 'cand-1932', 'Anaphoric reference to Maffeo Pinelli, named at p.339 L77.'),
    (80, 'his collection', 'cand-10031', 'Pinelli’s picture collection, introduced at p.339 L77.'),
    (80, 'Lodoli', 'cand-1411', 'The index candidate records Padre Carlo Lodoli; the comparison remains Haskell’s.'),
    (80, 'the historical approach to art', 'cand-10038', 'Explicitly inferential description.'),
    (80, 'the sixteenth century', 'cand-10039'),
    (80, 'Pictures attributed to Giorgione, Bassano, Veronese and Titian', 'cand-10040'),
    (80, 'Giorgione', 'cand-1188'),
    (80, 'Bassano', 'cand-0257', 'S1 index candidate includes p.340; S3 will review the surname-to-person mapping.'),
    (80, 'Veronese', 'cand-2755'),
    (80, 'Titian', 'cand-2630'),
    (80, 'others by Palma Giovane, Padovanino and Pietro della Vecchia', 'cand-10040'),
    (80, 'Palma Giovane', 'cand-1811'),
    (80, 'Padovanino', 'cand-2701', 'S1 index cross-reference says “see under Varotari, Alessandro”; the identity is not independently resolved in S2.'),
    (80, 'Pietro della Vecchia', 'cand-2707'),
    (80, 'his collection', 'cand-10031', '', 1),
    (80, 'Tiepolo', 'cand-10037', 'Surname only in the passage; retain separately from named Tiepolo index candidates pending S3.'),
    (80, 'four pictures', 'cand-10041'),
    (80, 'the painter with whom he was most in touch', 'cand-1489'),
    (80, 'Francesco Maggiotto', 'cand-1489'),
    (80, 'Piazzetta', 'cand-1901'),
    (80, 'a late and second-hand follower of Piazzetta', 'cand-1901', 'Describes the attributed artistic relationship; not a formal relation.'),
    (81, 'Pinelli', 'cand-1932'),
    (81, 'portraits of all the Doges', 'cand-10042'),
    (81, 'Plate 68a', 'cand-4190', 'The cited plate candidate is kept distinct from the broad series and cand-3352.'),
    (81, 'Venetian Popes and Cardinals', 'cand-10043'),
    (81, 'Good Inclinations leading a Youth to Knowledge', 'cand-1491', 'Reuses the p.340 S1 index subentry; title is descriptive in the source.'),
    (81, 'the Arts of', 'cand-10044'),
    (82, 'Painting', 'cand-10044'),
    (82, 'Typography', 'cand-10044'),
    (82, 'Diplomacy', 'cand-10044'),
    (82, 'Numismatics', 'cand-10044'),
    (82, 'Pinelli’s death', 'cand-1932'),
    (82, 'his library', 'cand-10030'),
    (82, 'picture collection', 'cand-10031'),
    (83, 'Print sellers', 'cand-10045'),
    (83, 'the firm of Remondini', 'cand-2123'),
    (83, 'Bassano', 'cand-10052'),
    (83, 'Venice', 'cand-2719'),
    (84, 'the firm', 'cand-2123', 'Anaphoric reference to Remondini.'),
    (84, 'separate prints', 'cand-10050'),
    (84, 'their market', 'cand-10056', 'Pronoun refers to the Remondini firm.'),
    (84, 'a very different public', 'cand-10058'),
    (85, 'They specialised', 'cand-2123', 'Anaphoric reference to the Remondini firm.'),
    (85, 'cheap romantic novels', 'cand-10046'),
    (85, 'devotional prints', 'cand-10047'),
    (85, 'peasants’ houses', 'cand-10048'),
    (85, 'they greatly expanded', 'cand-2123', 'Anaphoric reference to the Remondini firm.'),
    (85, 'an international clientèle', 'cand-10056'),
    (85, 'This brought them into rivalry', 'cand-2123', 'Anaphoric reference to the Remondini firm.'),
    (85, 'the more established institutions', 'cand-10057', 'Unnamed rival publishing institutions; no individual institution is inferred.'),
    (85, 'the Remondini', 'cand-2123'),
    (85, 'facsimiles of other publications at much reduced prices', 'cand-10049'),
    (85, 'the firm grew richer', 'cand-2123'),
    (85, 'paintings and drawings for extensive reproduction', 'cand-10051'),
    (85, 'Piazzetta', 'cand-1901'),
    (85, 'Amigoni', 'cand-0094'),
    (85, 'Guarana', 'cand-1237'),
    (85, 'Pietro Longhi', 'cand-1429'),
    (85, 'the Remondini', 'cand-2123', '', 1),
    (86, 'the German Joseph Wagner', 'cand-2796'),
    (86, 'Teodoro Viero', 'cand-2773'),
    (86, 'himself a printer', 'cand-2773', 'The phrase identifies Viero’s own occupation.'),
    (86, 'the same applies', 'cand-2773', 'Refers back to Haskell’s qualified statement about Wagner commissioning little original work.'),
    (86, 'Lodovico Furnaletto', 'cand-1092'),
    (86, 'a dealer in prints', 'cand-1092'),
    (86, 'Furnaletto', 'cand-1092', '', 1),
    (87, 'Ponte de’Baretteri', 'cand-10053'),
    (87, 'twelve drawings by Canaletto', 'cand-0503', 'Reuses the exact p.340 index subentry for drawings of Ducal ceremonies for Furnaletto.'),
    (87, 'Canaletto', 'cand-0498'),
    (87, 'the principal Ducal ceremonies', 'cand-10055'),
    (87, 'Brustolon', 'cand-0463'),
    (88, 'Rava, 1911', 'cand-10054', 'Trailing fragment of printed p.340 note 3; join to S0 L219 when that notes segment is processed.'),
]
for spec in mention_specs:
    line, surface, cid, *rest = spec
    note = rest[0] if rest else ''
    occurrence = rest[1] if len(rest) > 1 else 0
    add_mention(line, surface, cid, note, occurrence)


def add_statement(suffix, subject, obj, predicate, first, last, qfirst, qlast, claim,
                  qualification, mentioned, *, speaker='Haskell', layer='authorial narrative',
                  notes=(), relation_candidate=False, cross_refs=()):
    sid = f'st-chp13-p340-{suffix}'
    if sid in statement_by_id:
        raise SystemExit(f'duplicate statement ID: {sid}')
    quote = excerpt(first, last, qfirst, qlast)
    ids = list(dict.fromkeys(mentioned + [x for x in (subject, obj) if x]))
    if any(cid not in all_candidate_ids for cid in ids):
        raise SystemExit(f'missing candidate FK: {sid}')
    qualifiers = {'source_line_start': first, 'source_line_end': last,
                  'printed_page': 340, 'pdf_physical_page': 9, 'claim': claim,
                  'speaker': speaker, 'text_layer': layer, 'qualification': qualification,
                  'mentioned_candidate_ids': ids,
                  'ocr_corrections': [c for c in corrections if first <= c['source_line'] <= last]}
    if relation_candidate:
        qualifiers['relation_candidate'] = True
    if notes:
        refs = [note_ref(marker, lines) for marker, lines in notes]
        qualifiers['footnote_refs'] = refs
        qualifiers['footnote_marker'] = refs[0]['footnote_marker'] if len(refs) == 1 else [r['footnote_marker'] for r in refs]
        qualifiers['footnote_printed_page'] = 340
        qualifiers['footnote_text_pending'] = True
        qualifiers['footnote_body_link_status'] = 'pending'
        qualifiers['cross_reference_segments'] = [NOTES]
    if cross_refs:
        qualifiers['cross_reference_segments'] = list(dict.fromkeys(list(qualifiers.get('cross_reference_segments', [])) + list(cross_refs)))
    row = {'statement_id': sid, 'segment_id': BODY,
           'subject_candidate_id': subject, 'object_candidate_id': obj,
           'predicate': predicate, 'qualifiers': qualifiers,
           'original_quote': quote, 'origin': 'book',
           'source_file': '02-sources/02-Markdown/13_CHP-13_intro.md'}
    new_statements.append(row)


# Pinelli, his collection, and Maggiotto.
add_statement('pinelli-born-and-known-for-learning', 'cand-1932', None,
              'born_in_1735_and_gained_reputation_for_learning', 80, 80,
              'He was born in 1735', 'learning.',
              'Haskell says Maffeo Pinelli was born in 1735 and soon gained a reputation for learning.',
              '“He” refers to Pinelli, named at p.339 L77.', ['cand-1932'])
add_statement('pinelli-collection-suggested-historical-approach', 'cand-1932', 'cand-10038',
              'collection_suggested_historical_approach_to_art', 80, 80,
              'There is indeed about his collection', 'historical approach to art:',
              'Haskell infers from the collection’s scholarly completeness and eclecticism that Pinelli may have been interested in a historical approach to art.',
              'The source says “suggests” and compares Pinelli to Lodoli and others; retain the inference and analogy.',
              ['cand-10031', 'cand-1411', 'cand-10038'])
add_statement('pinelli-seems-most-interested-in-sixteenth-century-art', 'cand-1932', 'cand-10039',
              'seemed_most_enthusiastic_about_sixteenth_century_art', 80, 80,
              'but his real enthusiasm seems', 'sixteenth century.',
              'Haskell says Pinelli’s strongest enthusiasm seems to have been for the sixteenth century.',
              'The hedge “seems” is retained; the passage does not identify specific sixteenth-century works as favourites.',
              ['cand-1932', 'cand-10039'])
add_statement('pinelli-collection-attributed-old-master-pictures', 'cand-10031', 'cand-10040',
              'included_pictures_attributed_to_named_old_masters', 80, 80,
              'Pictures attributed to Giorgione', 'figure very strongly in his collection.',
              'Haskell says pictures attributed to Giorgione, Bassano, Veronese, Titian, Palma Giovane, Padovanino and Pietro della Vecchia figured strongly in Pinelli’s collection.',
              'Attribution status is explicit; no individual picture title or secure authorship is supplied.',
              ['cand-10031', 'cand-10040', 'cand-1188', 'cand-0257', 'cand-2755', 'cand-2630', 'cand-1811', 'cand-2701', 'cand-2707'])
add_statement('pinelli-collection-contemporary-artists-tiepolo-count', 'cand-10031', 'cand-10041',
              'well_represented_contemporary_artists_including_four_tiepolo_pictures', 80, 80,
              'Most of the artists of his own century', 'four pictures',
              'Haskell says most artists of Pinelli’s own century were well represented and records four pictures by a Tiepolo.',
              'The surname Tiepolo is unresolved and no picture titles are named.',
              ['cand-10031', 'cand-10037', 'cand-10041'])
add_statement('pinelli-most-in-touch-with-maggiotto', 'cand-1932', 'cand-1489',
              'was_most_in_touch_with_painter_francesco_maggiotto', 80, 80,
              'the painter with whom he was most in touch was', 'Francesco Maggiotto.',
              'Haskell identifies Francesco Maggiotto as the painter with whom Pinelli was most in touch.',
              'This comparative description does not specify a formal commission or quantify their contact.',
              ['cand-1932', 'cand-1489', 'cand-1901'], relation_candidate=True)
add_statement('maggiotto-described-as-piazzetta-follower', 'cand-1489', 'cand-1901',
              'described_as_late_second_hand_follower_of', 80, 80,
              'a late and second-hand follower of Piazzetta', 'Francesco Maggiotto.',
              'Haskell describes Maggiotto as a late and second-hand follower of Piazzetta.',
              'The characterization is attributed to Haskell and is a relation candidate, not a formal edge.',
              ['cand-1489', 'cand-1901'], relation_candidate=True)
add_statement('maggiotto-painted-doge-portrait-series-for-pinelli', 'cand-1489', 'cand-10042',
              'painted_for_pinelli_portrait_series_of_all_doges', 80, 81,
              'He painted for', 'portraits of all the Doges (Plate 68a)',
              'Maggiotto painted a series of portraits of all the Doges for Pinelli.',
              'The text links the series to Plate 68a. Keep its relation to the three-portrait plate group cand-4190 and the 168-portrait group cand-3352 unresolved.',
              ['cand-1489', 'cand-1932', 'cand-10042', 'cand-4190'], relation_candidate=True)
add_statement('maggiotto-painted-venetian-popes-cardinals', 'cand-1489', 'cand-10043',
              'painted_portraits_of_venetian_popes_and_cardinals_for_pinelli', 81, 81,
              'Venetian Popes and Cardinals', 'Venetian Popes and Cardinals',
              'The list governed by “He painted for Pinelli” includes portraits of Venetian Popes and Cardinals.',
              'The source names no sitters and the group is not counted.',
              ['cand-1489', 'cand-1932', 'cand-10043'], relation_candidate=True)
add_statement('maggiotto-painted-good-inclinations-allegory-for-pinelli', 'cand-1489', 'cand-1491',
              'painted_allegory_for_pinelli', 81, 81,
              'Good Inclinations leading a Youth to Knowledge', 'Good Inclinations leading a Youth to Knowledge',
              'The list of works Maggiotto painted for Pinelli includes the allegory indexed as Good Inclinations leading a Youth to Knowledge.',
              'The index subentry is reused; no medium, date or location is supplied here.',
              ['cand-1489', 'cand-1932', 'cand-1491'], relation_candidate=True)
add_statement('maggiotto-painted-four-arts-allegories-for-pinelli', 'cand-1489', 'cand-10044',
              'painted_allegories_of_four_arts_for_pinelli', 81, 82,
              'the Arts of', 'Numismatics.',
              'The list of works Maggiotto painted for Pinelli also includes allegories of Painting, Typography, Diplomacy and Numismatics.',
              'The source does not state whether these were four separate works or parts of a larger work.',
              ['cand-1489', 'cand-1932', 'cand-10044'], relation_candidate=True)
add_statement('pinelli-library-dispersed-after-death', 'cand-1932', 'cand-10030',
              'library_dispersed_after_pinellis_death_in_1785', 82, 82,
              'After Pinelli’s death in 1785', 'his library',
              'Haskell says Pinelli’s library was dispersed after his death in 1785.',
              'The library is kept distinct from the picture collection; note 1 is pending in the consolidated notes segment.',
              ['cand-1932', 'cand-10030'], notes=[(1, 'L217')], relation_candidate=True)
add_statement('pinelli-picture-collection-dispersed-after-death', 'cand-1932', 'cand-10031',
              'picture_collection_dispersed_after_pinellis_death_in_1785', 82, 82,
              'After Pinelli’s death in 1785', 'picture collection were dispersed',
              'Haskell says Pinelli’s picture collection was dispersed after his death in 1785.',
              'Keep the picture collection distinct from the library; note 1 is pending in the consolidated notes segment.',
              ['cand-1932', 'cand-10030', 'cand-10031'], notes=[(1, 'L217')], relation_candidate=True)
add_statement('pinelli-collection-dispersal-distressed-contemporaries', 'cand-1932', None,
              'collection_dispersal_distressed_many_contemporaries', 82, 82,
              'to the great distress', 'many contemporaries.',
              'The dispersal of the collections caused great distress among many contemporaries, according to Haskell.',
              'This is an attributed report of reaction; no contemporaries are named.',
              ['cand-1932', 'cand-10030', 'cand-10031'], notes=[(1, 'L217')])

# Remondini and the other print sellers.
add_statement('print-sellers-often-important-art-patrons', 'cand-10045', None,
              'often_important_art_patrons', 83, 83,
              'Print sellers too were often important art patrons', 'Print sellers too were often important art patrons',
              'Haskell generalizes that print sellers were often important art patrons.',
              'This is a broad authorial observation, not a claim that every seller named on the page acted as a patron.',
              ['cand-10045'])
add_statement('remondini-most-conspicuous-print-seller', 'cand-2123', None,
              'identified_as_most_conspicuous_print_seller', 83, 83,
              'the most conspicuous', 'the firm of Remondini',
              'Among print sellers, Haskell calls the Remondini firm the most conspicuous.',
              '“Most conspicuous” is Haskell’s comparative description.',
              ['cand-10045', 'cand-2123'])
add_statement('remondini-established-at-bassano', 'cand-2123', 'cand-10052',
              'firm_established_at_bassano', 83, 83,
              'the firm of Remondini which was', 'established at Bassano',
              'The Remondini firm was established at Bassano.',
              'Bassano is treated as a place in this context, distinct from Jacopo Bassano.',
              ['cand-2123', 'cand-10052'], notes=[(2, 'L218')], relation_candidate=True)
add_statement('remondini-had-venice-branch', 'cand-2123', 'cand-2719',
              'had_branch_in_venice', 83, 83,
              'but which had', 'branch in Venice.2',
              'The firm also had a branch in Venice.',
              'This is a branch location, not evidence that the firm was founded in Venice.',
              ['cand-2123', 'cand-2719'], notes=[(2, 'L218')], relation_candidate=True)
add_statement('remondini-published-books-mainly-separate-prints', 'cand-2123', 'cand-10050',
              'published_books_but_mainly_issued_separate_prints', 83, 84,
              'The Remondini also published books', 'separate prints.',
              'The firm published books but mainly issued separate prints.',
              'S0’s line-start period before “of the firm” is an OCR error recorded in S2; the original quote retains S0 text.',
              ['cand-2123', 'cand-10050'], relation_candidate=True)
add_statement('remondini-served-different-public', 'cand-2123', 'cand-10058',
              'served_a_different_public_from_great_enterprises', 84, 84,
              'On the whole their market', 'discussed so far.',
              'Haskell says the Remondini market served a very different public from the large enterprises discussed earlier.',
              'The passage does not identify or quantify that public beyond later mentioning peasants’ houses and an international clientele.',
              ['cand-2123', 'cand-10058'])
add_statement('remondini-specialised-in-cheap-romantic-novels', 'cand-2123', 'cand-10046',
              'specialised_in_cheap_romantic_novels', 85, 85,
              'They specialised in', 'cheap romantic novels',
              'The Remondini specialized in cheap romantic novels.',
              'The source gives a genre and price positioning, not individual titles.',
              ['cand-2123', 'cand-10046'])
add_statement('remondini-sold-devotional-prints-for-peasant-homes', 'cand-2123', 'cand-10047',
              'sold_devotional_prints_for_display_in_peasant_homes', 85, 85,
              'and in devotional prints', 'peasants’ houses;',
              'The firm specialized in devotional prints intended to be hung in peasants’ houses.',
              'No print subject, household, or precise geographic scope is named.',
              ['cand-2123', 'cand-10047', 'cand-10048'])
add_statement('remondini-expanded-and-acquired-international-clientele', 'cand-2123', 'cand-10056',
              'expanded_around_mid_century_and_acquired_international_clientele', 85, 85,
              'but towards the middle of the eighteenth century', 'international clientèle.',
              'Towards the middle of the eighteenth century the firm greatly expanded and began to acquire an international clientele.',
              'The source provides an approximate period, not a precise expansion date or named clients.',
              ['cand-2123', 'cand-10056'])
add_statement('remondini-rivalry-with-established-institutions', 'cand-2123', 'cand-10057',
              'entered_rivalry_with_established_publishing_institutions', 85, 85,
              'This brought them into rivalry', 'bitter hostility,',
              'The firm’s expansion brought it into rivalry with more established institutions, which greeted its arrival with bitter hostility.',
              'The institutions remain unnamed; hostility is Haskell’s characterization.',
              ['cand-2123', 'cand-10057'], relation_candidate=True)
add_statement('remondini-low-priced-facsimiles', 'cand-2123', 'cand-10049',
              'produced_facsimiles_of_other_publications_at_reduced_prices', 85, 85,
              'the more so as the Remondini had few scruples', 'much reduced prices.',
              'Haskell says the Remondini produced facsimiles of other publications at much reduced prices.',
              '“Few scruples” is Haskell’s critical evaluation, not a neutral property or a legal finding.',
              ['cand-2123', 'cand-10049'])
add_statement('remondini-employed-printers-and-artists-for-reproduction', 'cand-2123', 'cand-10051',
              'employed_printers_and_artists_to_make_images_for_reproduction', 85, 85,
              'As the firm grew richer', 'extensive reproduction.',
              'As it grew richer, the firm could employ some of the best printers and many leading artists to produce paintings and drawings for extensive reproduction.',
              'The artists are described as a group; the sentence does not state that each named artist made both paintings and drawings.',
              ['cand-2123', 'cand-10051'], relation_candidate=True)
for artist_id, artist_name, suffix in [
        ('cand-1901', 'Piazzetta', 'piazzetta'),
        ('cand-0094', 'Amigoni', 'amigoni'),
        ('cand-1237', 'Guarana', 'guarana'),
        ('cand-1429', 'Pietro Longhi', 'pietro-longhi')]:
    add_statement(f'remondini-popularised-{suffix}', artist_id, 'cand-2123',
                  'was_popularised_by_remondini_through_reproductive_prints', 85, 85,
                  'Piazzetta, Amigoni, Guarana', 'in this way.',
                  f'Haskell says {artist_name} was popularised by the Remondini through this reproductive activity.',
                  'The artists are named in a shared list; this is a relation candidate, not a documented individual commission.',
                  ['cand-2123', 'cand-1901', 'cand-0094', 'cand-1237', 'cand-1429'],
                  notes=[(3, 'L219')], relation_candidate=True)
add_statement('wagner-german-and-opened-shop-1742', 'cand-2796', None,
              'identified_as_german_and_opened_shop_in_1742', 86, 86,
              'the German Joseph Wagner', 'opened a shop in 1742',
              'Haskell identifies Joseph Wagner as German and says he opened a shop in 1742.',
              'The passage does not give the shop’s address.',
              ['cand-2796'], notes=[(4, 'L220')])
add_statement('wagner-shop-significant-to-printers', 'cand-2796', None,
              'shop_was_of_utmost_significance_to_printers', 86, 86,
              'which was of the utmost significance', 'to printers',
              'Haskell says Wagner’s shop was of the utmost significance to printers.',
              'This is an attributed evaluation; S0’s period before “to printers” is corrected in S2 only.',
              ['cand-2796'], notes=[(4, 'L220')])
add_statement('wagner-seems-to-have-commissioned-little-original-work', 'cand-2796', None,
              'seems_to_have_commissioned_little_original_work_from_artists', 86, 86,
              'though he seems to have commissioned', 'other artists4;',
              'Haskell says Wagner seems to have commissioned little original work from other artists.',
              'The hedge “seems” is retained; note 4 supplies a citation pointer still pending in the notes segment.',
              ['cand-2796'], notes=[(4, 'L220')], relation_candidate=True)
add_statement('viero-printer-opened-shop-1754', 'cand-2773', None,
              'was_printer_and_opened_shop_in_1754', 86, 86,
              'Teodoro Viero, himself a printer', 'opened a shop in 1754',
              'Teodoro Viero was a printer and opened a shop in 1754.',
              'The shop address is not supplied.',
              ['cand-2773'], notes=[(5, 'L221')])
add_statement('viero-same-limited-original-commissioning-applies', 'cand-2773', None,
              'same_qualified_claim_of_little_original_commissioning_applies', 86, 86,
              'to which the same applies', 'to which the same applies',
              'The text says the same assessment applies to Viero as to Wagner: he seems to have commissioned little original work from other artists.',
              'This is an anaphoric extension of Haskell’s qualified claim, not a statement that Viero commissioned none.',
              ['cand-2773', 'cand-2796'], notes=[(5, 'L221')], relation_candidate=True)
add_statement('furnaletto-print-dealer-not-claiming-to-practise-art', 'cand-1092', None,
              'dealt_in_prints_and_made_no_claim_to_practise_art', 86, 86,
              'Lodovico Furnaletto', 'practice the art himself.',
              'Haskell describes Lodovico Furnaletto as a print dealer who made no claim to practise art himself.',
              'This wording is preserved as the author’s description; it is not expanded into an external occupation record.',
              ['cand-1092'])
add_statement('furnaletto-established-over-thirty-years-at-ponte-de-baretteri', 'cand-1092', 'cand-10053',
              'established_at_ponte_de_baretteri_for_more_than_thirty_years', 86, 87,
              'Furnaletto', 'Ponte de’Baretteri;',
              'Furnaletto was established for more than thirty years on the Ponte de’Baretteri.',
              'The duration is approximate and no opening year is inferred. S0’s leading apostrophe at L87 is an OCR error recorded in S2.',
              ['cand-1092', 'cand-10053'])
add_statement('furnaletto-commissioned-twelve-canaletto-drawings-in-1766', 'cand-1092', 'cand-0503',
              'commissioned_twelve_canaletto_drawings_in_1766', 87, 87,
              'his most significant gesture was the commissioning in 1766 of',
              'twelve drawings by Canaletto',
              'In 1766 Furnaletto commissioned twelve drawings by Canaletto.',
              'The commission is a relation candidate; the passage supplies no payment, contract, or individual drawing titles.',
              ['cand-1092', 'cand-0503', 'cand-0498'], notes=[(6, 'L222')], relation_candidate=True)
add_statement('canaletto-drawings-depicted-principal-ducale-ceremonies', 'cand-0503', 'cand-10055',
              'depicted_principal_ducale_ceremonies', 87, 87,
              'representing the', 'principal Ducal ceremonies',
              'The twelve Canaletto drawings represented the principal Ducal ceremonies.',
              'The ceremonies are not named or individually identified.',
              ['cand-0503', 'cand-10055'], notes=[(6, 'L222')])
add_statement('canaletto-drawings-intended-for-engraving-by-brustolon', 'cand-0503', 'cand-0463',
              'were_to_be_engraved_by_brustolon', 87, 87,
              'to be engraved', 'by Brustolon.',
              'The drawings were intended to be engraved by Brustolon.',
              'The infinitive “to be engraved” records the stated plan, not proof that engraving was completed.',
              ['cand-0503', 'cand-0463'], notes=[(6, 'L222')], relation_candidate=True)
add_statement('printed-note-three-rava-citation-tail', 'cand-10054', None,
              'citation_fragment_names_rava_and_1911', 88, 88,
              'Rava, 1911.', 'Rava, 1911.',
              'The body segment carries only the terminal citation fragment “Rava, 1911.” from printed p.340 note 3.',
              'The cited work and the author’s full identity are not inferred. The rest of note 3 is in S0 L219 and remains pending.',
              ['cand-10054'], speaker='Haskell’s footnote apparatus', layer='bibliographic citation',
              notes=[(3, 'L219')], cross_refs=(BODY, NOTES))

all_candidates = sorted(candidates + new_candidates, key=lambda row: row['candidate_id'])
all_mentions = sorted(mentions + new_mentions,
                      key=lambda row: (row['segment_id'], int(row['start_char']), int(row['end_char']), row['mention_id']))
all_statements = sorted(statements + new_statements, key=lambda row: row['statement_id'])
for key, rows in [('candidate_id', all_candidates), ('mention_id', all_mentions), ('statement_id', all_statements)]:
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise SystemExit(f'duplicate {key}')
for row in new_mentions:
    start, end = int(row['start_char']), int(row['end_char'])
    if segment_text[start:end] != row['surface_form']:
        raise SystemExit(f'mention span mismatch: {row["mention_id"]}')
    if row['candidate_id'] not in all_candidate_ids:
        raise SystemExit(f'mention FK missing: {row["mention_id"]}')
for row in new_statements:
    if row['segment_id'] != BODY or row['origin'] != 'book':
        raise SystemExit(f'invalid statement metadata: {row["statement_id"]}')
    q = row['qualifiers']
    if not (79 <= q['source_line_start'] <= q['source_line_end'] <= 88):
        raise SystemExit(f'invalid source line range: {row["statement_id"]}')
    if any(cid not in all_candidate_ids for cid in q['mentioned_candidate_ids']):
        raise SystemExit(f'statement candidate FK missing: {row["statement_id"]}')

coverage[BODY].update({
    'disposition': 'reviewed',
    'migration_status': 'partial',
    'source_line_ranges': 'L79-88',
    'note': 'Printed p.340 body reviewed against CHP-13.pdf physical page 9. Printed notes 1–6 map to the consolidated notes segment L217–222 and remain pending in source order, so coverage stays partial. Note 3 is split in S0: the body segment L88 carries “Rava, 1911.” while notes L219 ends with “published by A.”; preserve both anchors and join them when the notes segment is processed. Maggiotto’s all-Doge series is kept distinct from Plate 68a candidate cand-4190 and portrait-group cand-3352 pending later global review. OCR corrections are recorded in S2 only.'
})
coverage_rows = [coverage[row['segment_id']] for row in coverage_rows]

print(f'p.340 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements')
print('candidate additions:')
for row in new_candidates:
    print(f"  {row['candidate_id']} [{row['suggested_type']}] {row['canonical_name']}")
print('statement additions:')
for row in new_statements:
    q = row['qualifiers']
    quote = row['original_quote'].replace('\n', ' ↵ ')
    print(f"  {row['statement_id']} L{q['source_line_start']}-{q['source_line_end']} {row['predicate']} [{row['subject_candidate_id']} -> {row['object_candidate_id'] or '—'}]: {quote}")
print('mention counts by candidate: ' + ', '.join(f'{cid}={count}' for cid, count in sorted(Counter(r['candidate_id'] for r in new_mentions).items())))
print('coverage: p.340 -> reviewed/partial; footnotes 1–6 await L217–222; note 3 split preserved across L88/L219')
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
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f'applied; four recovery copies created with suffix {BACKUP_SUFFIX}')
