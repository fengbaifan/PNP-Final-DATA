"""Controlled S2 migration for printed p.339; dry-run by default."""
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
BODY = 'chp-13:13_CHP-13_intro:l70-77'
PREVIOUS = 'chp-13:13_CHP-13_intro:l61-68'
NEXT = 'chp-13:13_CHP-13_intro:l79-88'
NOTES = 'chp-13:13_CHP-13_intro:l179-251'
SOURCE_SHA = 'c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8'
PDF_SHA = 'da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc'
BACKUP_SUFFIX = '.bak-s2-chp13-p339-20261003'

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='apply reviewed p.339 S2 migration')
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
    70: '[Page 339]',
    71: 'government1—and he himself was said by contemporaries',
    72: 'Society.2 But as a private individual',
    73: 'the vignette on one of his books, writes',
    74: 'Cacadubbj’, must clearly be an attack',
    75: 'Venetian morals.. .,3 A glance at his catalogues',
    76: 'Fontebasso and Gaetano Zompini, and the results',
    77: 'Many other publishers besides Albrizzi, Pasquali and Zatta',
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

state = (len(candidates), max(int(r['candidate_id'].split('-')[1]) for r in candidates),
         len(mentions), len(statements))
if state != (10010, 10023, 21406, 9556):
    raise SystemExit(f'unexpected table pre-state: {state}')
for segment_id in (BODY, PREVIOUS, NEXT, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f'required coverage row missing: {segment_id}')
if (coverage[BODY]['disposition'], coverage[BODY]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.339 is not queued/pending')
if (coverage[PREVIOUS]['disposition'], coverage[PREVIOUS]['migration_status']) != ('reviewed', 'partial'):
    raise SystemExit('p.338 is not reviewed/partial')
if (coverage[NEXT]['disposition'], coverage[NEXT]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.340 is not queued/pending')
if (coverage[NOTES]['disposition'], coverage[NOTES]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('chapter 13 notes are not queued/pending')
if any(row['segment_id'] == BODY for row in mentions) or any(row['segment_id'] == BODY for row in statements):
    raise SystemExit('p.339 rows already exist')

new_candidates = []
new_mentions = []
new_statements = []
new_ids = {f'cand-{n}' for n in range(10024, 10037)}
if new_ids & candidate_ids:
    raise SystemExit(f'p.339 candidate IDs already exist: {sorted(new_ids & candidate_ids)}')
if any(row['mention_id'].startswith('m-s2-ch13-p339-') for row in mentions):
    raise SystemExit('p.339 mention IDs already exist')
if any(row['statement_id'].startswith('st-chp13-p339-') for row in statements):
    raise SystemExit('p.339 statement IDs already exist')

body_lines = {n: source_lines[n - 1] for n in range(70, 78)}
segment_text = '\n'.join(body_lines[n] for n in range(70, 78))
line_offsets = {}
offset = 0
for n in range(70, 78):
    line_offsets[n] = offset
    offset += len(body_lines[n]) + 1


def add_candidate(cid, name, kind, detail, line):
    row = {field: '' for field in candidate_fields}
    row.update({'candidate_id': cid, 'canonical_name': name, 'suggested_type': kind,
                'status': 'open', 'detail': detail, 'candidate_origin': 'body-mention',
                'candidate_source_ref': f'{BODY}#L{line}'})
    new_candidates.append(row)


add_candidate('cand-10024', 'Unidentified Antonio Zatta book containing a fountain-and-dolphin vignette',
              'archive', 'Haskell does not give the book title here. Printed p.339 note 3 identifies a source at p.23, which remains to be read in source order before the document is resolved.', 73)
add_candidate('cand-10025', 'Fountain-and-dolphin vignette in an unidentified Antonio Zatta book',
              'work', 'The described decorative image is interpreted satirically in Zatta’s preface; do not treat its dolphin as proof of an intended Jesuit allegory.', 73)
add_candidate('cand-10026', 'Accademia dei Cacadubbj (satirical name in a Zatta preface)',
              'term', 'A satirical academy/name represented by the quoted secretary, not evidence of a historical institution. Preserve the source spelling and defer any external identity claim.', 73)
add_candidate('cand-10027', 'Antonio Zatta edition of Petrarch (1756)',
              'archive', 'A dated Italian-classics edition listed by Haskell; full title, format and illustration status are not specified on p.339.', 75)
add_candidate('cand-10028', 'Antonio Zatta illustrated edition of Dante (1757)',
              'archive', 'Haskell says Zatta sponsored an illustrated edition and calls it the first to appear for two centuries; title and exact edition identity remain unspecified.', 75)
add_candidate('cand-10029', 'Pietro Antonio Novelli illustrations for Metastasio works beginning in 1781',
              'work', 'A set of illustrations for multiple Metastasio works, beginning to appear in 1781. Haskell’s claim that they herald the Romantic movement is evaluative.', 76)
add_candidate('cand-10030', 'Maffeo Pinelli private library',
              '', 'A personal library/collection. Current taxonomy does not provide a dedicated collection type; retain the object without forcing it into institution or archive.', 77)
add_candidate('cand-10031', 'Maffeo Pinelli picture collection',
              '', 'A personal collection of many hundred pictures, cited for sale in 1785 in note 6. Current taxonomy does not provide a dedicated collection type; retain type undecided.', 77)
add_candidate('cand-10032', 'Unspecified Venetian State/public authority mentioned in Pinelli’s publishing activity',
              'institution', 'The passage capitalizes “State” and concerns books Pinelli produced in Venice, but does not name a constitutional body; do not equate it with the Venetian Republic without further evidence.', 77)
add_candidate('cand-10033', 'Romantic movement as a stylistic horizon for Novelli’s Metastasio illustrations',
              'term', 'Haskell says the illustrations show signs of heralding the Romantic movement; this is an art-historical interpretation, not a fixed date or causal influence claim.', 76)
add_candidate('cand-10034', 'Medieval iconography in Dante illustration',
              'term', 'The iconographic problem Haskell says was difficult for the two artists working for Zatta; retain as the stated subject of the difficulty.', 75)
add_candidate('cand-10035', 'Accommodating Venetian morals in the vignette’s satirical reading',
              'term', 'The basin of water is said in the satirical gloss to represent the accommodating nature of Venetian morals; this is a quoted parody, not a verified social fact.', 75)
add_candidate('cand-10036', 'Lower social world represented in Novelli’s later Goldoni illustrations',
              'term', 'Haskell compares the social world of the later complete Goldoni edition with Novelli’s earlier work for Pasquali and describes it as far lower; the group is not identified here.', 76)

all_candidate_ids = candidate_ids | {row['candidate_id'] for row in new_candidates}


def add_mention(surface, cid, note='', occurrence=0):
    positions, cursor = [], 0
    while True:
        at = segment_text.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f'mention text missing: {surface!r} occurrence {occurrence}')
    start = positions[occurrence]
    row = {field: '' for field in mention_fields}
    row.update({'mention_id': f'm-s2-ch13-p339-{len(new_mentions) + 1:03d}',
                'segment_id': BODY, 'candidate_id': cid, 'surface_form': surface,
                'start_char': start, 'end_char': start + len(surface), 'note': note})
    new_mentions.append(row)


def add_cross_mention(first, last, start_text, end_text, cid, note=''):
    local_text = '\n'.join(body_lines[n] for n in range(first, last + 1))
    start, last_start = local_text.find(start_text), local_text.find(end_text, local_text.find(start_text))
    if start < 0 or last_start < 0:
        raise SystemExit(f'cross-line mention boundary missing: {start_text!r}/{end_text!r}')
    surface = local_text[start:last_start + len(end_text)]
    begin = line_offsets[first] + start
    if segment_text[begin:begin + len(surface)] != surface:
        raise SystemExit(f'cross-line mention span mismatch: {surface!r}')
    row = {field: '' for field in mention_fields}
    row.update({'mention_id': f'm-s2-ch13-p339-{len(new_mentions) + 1:03d}',
                'segment_id': BODY, 'candidate_id': cid, 'surface_form': surface,
                'start_char': begin, 'end_char': begin + len(surface), 'note': note})
    new_mentions.append(row)


# Cross-page completion of the p.338 phrase, then Zatta and the satirical preface.
add_mention('government', 'cand-10015', 'Completes the p.338 phrase “the Portuguese government”; p.338 mention remains anchored to “the Portuguese”.')
add_mention('he himself', 'cand-2865', 'Anaphoric reference to Antonio Zatta named on p.338.')
add_mention('Society', 'cand-1321', 'Continues the p.338 reference to the Society of Jesus.')
add_mention('the other two men', 'cand-2068', 'Haskell means Albrizzi and Pasquali, the other two publishers in his comparison.')
add_mention('He seems', 'cand-2865')
add_mention('social Use', 'cand-2865', 'OCR reads “Use”; the print reads “life”.')
add_mention('His own prefaces', 'cand-10024', 'The possessive refers to Antonio Zatta.')
add_mention('He once mocked', 'cand-2865')
add_mention('his enemies', 'cand-2865')
add_mention('the vignette on one of his books', 'cand-10025')
add_mention('one of his books', 'cand-10024', 'Unidentified carrier book; p.339 note 3 awaits source-order reading.')
add_mention('a fountain supported by a dolphin', 'cand-10025')
add_cross_mention(73, 74, 'Segretario dell’Accademia dei', 'Cacadubbj’', 'cand-10026',
                  'The satirical secretary is a quoted persona, not an identified historical person.')
add_mention('the Jesuits', 'cand-1321', occurrence=0)
add_mention('The dolphin', 'cand-10025')
add_mention('the Jesuits', 'cand-1321', occurrence=1)
add_mention('the basin of water', 'cand-10025')
add_mention('Venetian morals', 'cand-10035')
add_mention('his catalogues', 'cand-2865', 'Haskell’s evidentiary basis; the 1790 catalogue is identified in note 4, still pending.')
add_mention('the most prolific publisher', 'cand-2865')
add_mention('eighteenth-century Venice', 'cand-2719')
add_mention('illustrated books', 'cand-2068')
add_mention('ceremonial pamphlets', 'cand-2068')
add_mention('well-established Italian classics', 'cand-2866')
add_mention('Petrarch', 'cand-1892')
add_mention('Petrarch in 1756', 'cand-10027')
add_mention('Dante', 'cand-0900', occurrence=0)
add_mention('Dante in 1757', 'cand-10028')
add_mention('Ariosto', 'cand-0116')
add_mention('Tasso', 'cand-2544')
add_mention('Metastasio', 'cand-1659', occurrence=0)
add_mention('illustrated edition that he sponsored', 'cand-10028')
add_mention('Dante', 'cand-0900', occurrence=1)
add_mention('mediaeval iconography', 'cand-10034')
add_cross_mention(75, 76, 'Francesco', 'Fontebasso', 'cand-1047')
add_mention('Gaetano Zompini', 'cand-2874')
add_mention('the poem', 'cand-10028', 'Refers to Dante’s poem in this account; exact title is not supplied.')
add_mention('Novelli’s illustrations', 'cand-10029')
add_mention('works of Metastasio', 'cand-10029')
add_mention('Metastasio', 'cand-1659', occurrence=1)
add_mention('the Romantic movement', 'cand-10033')
add_mention('the same artist', 'cand-1758', 'Anaphoric reference to Pietro Antonio Novelli.')
add_mention('a second set of drawings', 'cand-1761', 'The index identifies the Zatta Goldoni illustration set; the sentence itself does not name the publisher.')
add_mention('a complete edition of Goldoni', 'cand-1211')
add_mention('Goldoni', 'cand-1205', occurrence=0)
add_mention('the comedies', 'cand-1761')
add_mention('a far lower social world', 'cand-10036')
add_mention('Pasquali', 'cand-1844', occurrence=0)
add_mention('earlier for Pasquali', 'cand-1210')
add_mention('Albrizzi', 'cand-0025')
add_mention('Pasquali', 'cand-1844', occurrence=1)
add_mention('Zatta', 'cand-2865', occurrence=0)
add_mention('illustrated books', 'cand-2068', occurrence=1)
add_mention('artistic output', 'cand-2068', 'Haskell’s comparison of the broader publishers’ influence, not an individual work.')
add_mention('the publisher Maffeo Pinelli', 'cand-1932')
add_mention('the State', 'cand-10032')
add_mention('a private collector and patron', 'cand-1932')
add_mention('his library', 'cand-10030', 'Personal library/collection; type remains undecided.')
add_mention('many hundred pictures', 'cand-10031', 'Quantity is Haskell’s wording; printed note 6 points to the 1785 sale catalogue, pending.')

corrections = [
    {'source_line': 72, 'ocr': 'social Use', 'print': 'social life', 'basis': 'CHP-13.pdf physical page 8.'},
    {'source_line': 77, 'ocr': 'thepublisher', 'print': 'the publisher', 'basis': 'CHP-13.pdf physical page 8.'},
    {'source_line': 77, 'ocr': 'pictures.8', 'print': 'pictures.6', 'basis': 'The printed superscript footnote marker is 6, not OCR 8.'},
]


def excerpt(start, end):
    a = segment_text.find(start)
    b = segment_text.find(end, a)
    if a < 0 or b < 0:
        raise SystemExit(f'quote boundary missing: {start!r}/{end!r}')
    return segment_text[a:b + len(end)]


def note_ref(marker, lines):
    return {'footnote_marker': str(marker), 'footnote_printed_page': 339,
            'footnote_text_pending': True, 'footnote_segment': NOTES,
            'footnote_line_range': lines, 'footnote_body_link_status': 'pending'}


STATEMENT_CLAIMS = {
    'zatta-reported-lay-member-jesuits': 'Contemporaries reportedly said Antonio Zatta was a lay member of the Society of Jesus.',
    'zatta-indistinct-from-past': 'Haskell says Zatta emerges less distinctly from the past than the other two publishers.',
    'zatta-little-social-life': 'Haskell says Zatta seems to have played little part in social life.',
    'zatta-activities-untraced-in-others-writings': 'Haskell says there are no traces of Zatta’s activities in other people’s writings.',
    'zatta-prefaces-characterization': 'Haskell characterizes Zatta’s prefaces as usually vivid and presents him as enterprising, intelligent and sometimes witty.',
    'zatta-parodied-symbolic-readings': 'Haskell says Zatta mocked his enemies by parodying their heavy symbolic readings of decorative ornament.',
    'satirical-secretary-reads-vignette-as-jesuit-attack': 'The satirical secretary represented in Zatta’s preface reads the fountain-and-dolphin vignette as an attack on the Jesuits and as an allegory of Venetian morals.',
    'zatta-most-prolific-in-eighteenth-century-venice': 'Haskell says Zatta’s catalogues show him to have been the most prolific publisher in eighteenth-century Venice.',
    'zatta-range-of-illustrated-books': 'Haskell says Zatta promoted few illustrated books before the century’s second half and ranged widely thereafter.',
    'zatta-classical-editions': 'Haskell identifies elegant editions of Italian classics as Zatta’s chief contribution, naming Petrarch (1756), Dante (1757), and later Ariosto, Tasso and Metastasio.',
    'zatta-dante-support': 'Haskell says Zatta passionately supported Dante when such views were unfashionable.',
    'zatta-sponsored-first-illustrated-dante-edition-in-two-centuries': 'Haskell says Zatta sponsored an illustrated Dante edition that was the first to appear for two centuries.',
    'dante-medieval-iconography-difficult-for-artists': 'Haskell says the medieval iconography was difficult for the two artists who worked especially for Zatta, Francesco Fontebasso and Gaetano Zompini.',
    'dante-illustrations-results-engaging-limited-interpretation': 'Haskell finds the Dante illustrations often engaging but of little help in interpreting the poem.',
    'novelli-metastasio-illustrations-from-1781': 'Novelli’s illustrations for Metastasio’s works began to appear in 1781.',
    'haskell-metastasio-illustrations-herald-romantic': 'Haskell says Novelli’s Metastasio illustrations show signs of heralding the Romantic movement.',
    'novelli-second-goldoni-drawing-set': 'Seven years after the Metastasio illustrations began, Novelli produced a second drawing set for a complete Goldoni edition.',
    'novelli-goldoni-lower-social-world': 'Haskell says Novelli placed the comedies in a far lower social world in the later Goldoni edition than in his earlier work for Pasquali.',
    'other-illustrated-book-publishers-limited-artistic-influence': 'Haskell says many other publishers made fine illustrated books but had less influence on artistic output than Albrizzi, Pasquali and Zatta.',
    'pinelli-published-books-for-state': 'Haskell says Pinelli mostly produced books for the State and judges them to have had no artistic interest.',
    'pinelli-private-collector-patron': 'Haskell describes Maffeo Pinelli as a large-scale private collector and patron.',
    'pinelli-library-famous-in-europe': 'Haskell says Pinelli was best known for his library, which he calls one of Europe’s most famous.',
    'pinelli-owned-many-hundred-pictures': 'Haskell says Pinelli also owned many hundred pictures.',
}


def add_statement(suffix, subject, obj, predicate, first, last, qstart, qend, qualification,
                  mentioned, *, speaker='Haskell', layer='authorial narrative', notes=(), extra=None):
    sid = f'st-chp13-p339-{suffix}'
    if sid in statement_by_id:
        raise SystemExit(f'duplicate statement ID: {sid}')
    if suffix not in STATEMENT_CLAIMS:
        raise SystemExit(f'statement claim text missing: {suffix}')
    quote = excerpt(qstart, qend)
    if quote not in segment_text:
        raise SystemExit(f'statement quote is not anchored: {sid}')
    ids = mentioned + [x for x in (subject, obj) if x]
    if any(cid not in all_candidate_ids for cid in ids):
        raise SystemExit(f'missing candidate FK: {sid}')
    qualifiers = {'source_line_start': first, 'source_line_end': last,
                  'printed_page': 339, 'pdf_physical_page': 8, 'claim': STATEMENT_CLAIMS[suffix],
                  'speaker': speaker, 'text_layer': layer, 'qualification': qualification,
                  'mentioned_candidate_ids': mentioned,
                  'ocr_corrections': [c for c in corrections if first <= c['source_line'] <= last]}
    if notes:
        refs = [note_ref(marker, lines) for marker, lines in notes]
        qualifiers['footnote_refs'] = refs
        qualifiers['footnote_marker'] = refs[0]['footnote_marker']
        qualifiers['footnote_printed_page'] = 339
        qualifiers['footnote_text_pending'] = True
        qualifiers['footnote_segment'] = NOTES
        qualifiers['footnote_body_link_status'] = 'pending'
        qualifiers['cross_reference_segments'] = [NOTES]
    if extra:
        qualifiers.update(extra)
    new_statements.append({'statement_id': sid, 'segment_id': BODY,
                           'subject_candidate_id': subject or None,
                           'object_candidate_id': obj or None,
                           'predicate': predicate, 'qualifiers': qualifiers,
                           'original_quote': quote, 'origin': 'book',
                           'source_file': '02-sources/02-Markdown/13_CHP-13_intro.md'})


add_statement('zatta-reported-lay-member-jesuits', 'cand-2865', 'cand-1321',
              'reported_as_lay_member_of_society', 71, 72, 'he himself was said by contemporaries',
              'Society.', 'Haskell reports contemporary accounts; this is not independently verified here.',
              ['cand-2865', 'cand-1321'], speaker='Haskell reporting unnamed contemporaries',
              layer='authorial report of attributed testimony', notes=[(2, 'L213')], extra={'relation_candidate': True})
add_statement('zatta-indistinct-from-past', 'cand-2865', None,
              'emerged_less_distinctly_than_two_other_publishers', 72, 72,
              'as a private individual he emerges far more indistinctly',
              'the other two men.', 'The comparison is to Albrizzi and Pasquali in the preceding discussion.',
              ['cand-2865', 'cand-0025', 'cand-1844'])
add_statement('zatta-little-social-life', 'cand-2865', None,
              'seemed_to_play_little_part_in_social_life', 72, 72,
              'He seems to have played little part', 'social Use,',
              '“Seems” is retained; the print reads “life” where S0 OCR reads “Use”.',
              ['cand-2865'])
add_statement('zatta-activities-untraced-in-others-writings', 'cand-2865', None,
              'activities_not_traced_in_writings_of_others', 72, 72,
              'there are no traces of his activities', 'writings of others.',
              'This is Haskell’s assessment of the surviving record, not proof that no such writings exist.',
              ['cand-2865'])
add_statement('zatta-prefaces-characterization', 'cand-2865', 'cand-10024',
              'prefaces_described_as_vivid_and_witty', 72, 72,
              'His own prefaces are usually vivid', 'trenchant wit.',
              'This is Haskell’s characterization; the cited preface remains to be identified from note 3.',
              ['cand-2865', 'cand-10024'], notes=[(3, 'L214')])
add_statement('zatta-parodied-symbolic-readings', 'cand-2865', 'cand-10025',
              'mocked_enemies_by_parodying_symbolic_interpretation', 72, 72,
              'He once mocked his enemies', 'merely decorative ornament:',
              'Haskell presents this as Zatta’s parody of his enemies’ heavy symbolic readings.',
              ['cand-2865', 'cand-10024', 'cand-10025'])
add_statement('satirical-secretary-reads-vignette-as-jesuit-attack', 'cand-10025', 'cand-1321',
              'satirical_voice_interpreted_vignette_as_jesuit_attack', 73, 75,
              'the vignette on one of his books', 'Venetian morals.. .,3',
              'The quoted secretary is a satirical voice represented in Zatta’s preface, not a verified author or institution. The alleged symbolism is part of the parody.',
              ['cand-10025', 'cand-10024', 'cand-10026', 'cand-1321', 'cand-10035'],
              speaker='Satirical secretary quoted in Zatta’s preface (as presented by Haskell)',
              layer='nested quotation and authorial paraphrase',
              notes=[(3, 'L214')])
add_statement('zatta-most-prolific-in-eighteenth-century-venice', 'cand-2865', None,
              'described_as_most_prolific_publisher_in_eighteenth_century_venice', 75, 75,
              'A glance at his catalogues shows that Zatta was the most prolific publisher',
              'eighteenth-century Venice.',
              'Haskell bases this superlative on his catalogues; note 4 gives a 1790 catalogue, which has not yet been read.',
              ['cand-2865', 'cand-2719'], notes=[(4, 'L215')])
add_statement('zatta-range-of-illustrated-books', 'cand-2865', 'cand-2068',
              'range_of_illustrated_books_expanded_after_midcentury', 75, 75,
              'He did not promote illustrated books much before the second half of the century',
              'but thereafter he ranged widely.',
              'The wording distinguishes limited earlier promotion from later breadth.',
              ['cand-2865', 'cand-2068'])
add_statement('zatta-classical-editions', 'cand-2865', 'cand-2866',
              'produced_editions_of_italian_classics', 75, 75,
              'his most important contribution lay in the elegant production',
              'Ariosto, Tasso and Metastasio.',
              'The passage dates Petrarch to 1756 and Dante to 1757, then names later editions without assigning dates to them.',
              ['cand-2865', 'cand-2866', 'cand-1892', 'cand-0900', 'cand-0116', 'cand-2544', 'cand-1659',
               'cand-10027', 'cand-10028'], notes=[(4, 'L215')], extra={'relation_candidate': True})
add_statement('zatta-dante-support', 'cand-2865', 'cand-0900',
              'passionately_supported_dante_when_unfashionable', 75, 75,
              'Zatta was indeed a passionate supporter of Dante',
              'when such views were unfashionable,',
              'This is Haskell’s account of Zatta’s position.',
              ['cand-2865', 'cand-0900'])
add_statement('zatta-sponsored-first-illustrated-dante-edition-in-two-centuries', 'cand-2865', 'cand-10028',
              'sponsored_illustrated_dante_edition_first_in_two_centuries', 75, 75,
              'the illustrated edition that he sponsored was the first to appear for two centuries.',
              'for two centuries.',
              'The antecedent is the Dante edition; no full title is supplied. “First” is Haskell’s historical claim and will be checked against his cited sources only when those sources are actually consulted.',
              ['cand-2865', 'cand-0900', 'cand-10028'], notes=[(4, 'L215')], extra={'relation_candidate': True})
add_statement('dante-medieval-iconography-difficult-for-artists', 'cand-10028', 'cand-10034',
              'medieval_iconography_challenged_fontebasso_and_zompini', 75, 76,
              'The strain of coping with mediaeval iconography proved a difficult one',
              'the two artists who especially worked for him, Francesco\nFontebasso and Gaetano Zompini,',
              'This is Haskell’s evaluation of the task; both artists are named in the reviewed passage.',
              ['cand-10028', 'cand-10034', 'cand-1047', 'cand-2874'])
add_statement('dante-illustrations-results-engaging-limited-interpretation', 'cand-10028', None,
              'illustrations_engaging_but_limited_for_poem_interpretation', 76, 76,
              'the results, though often engaging, hardly contribute much',
              'an interpretation of the poem.',
              'Haskell’s aesthetic and interpretive judgment is retained as attributed evaluation.',
              ['cand-10028', 'cand-1047', 'cand-2874'])
add_statement('novelli-metastasio-illustrations-from-1781', 'cand-1758', 'cand-10029',
              'illustrations_for_metastasio_works_began_1781', 76, 76,
              'Novelli’s illustrations for the works of Metastasio',
              'began to appear in 1781,',
              'The sentence dates the beginning of their appearance; it does not date a single complete set.',
              ['cand-1758', 'cand-1659', 'cand-10029'], notes=[(5, 'L215')], extra={'relation_candidate': True})
add_statement('haskell-metastasio-illustrations-herald-romantic', 'cand-10029', 'cand-10033',
              'showed_signs_of_heralding_romantic_movement', 76, 76,
              'which show clear signs of heralding the Romantic movement.',
              'the Romantic movement.',
              'This is Haskell’s stylistic interpretation; it is not an assertion of a causal movement or exact date.',
              ['cand-10029', 'cand-10033'], notes=[(5, 'L215')])
add_statement('novelli-second-goldoni-drawing-set', 'cand-1758', 'cand-1761',
              'produced_second_drawing_set_for_complete_goldoni_edition_seven_years_later', 76, 76,
              'Seven years later the same artist produced a second set of drawings for a complete edition of Goldoni',
              'edition of Goldoni,',
              '“Seven years later” is relative to the 1781 Metastasio illustration series; the source does not give a separate year. The index identifies this as the Zatta edition, while the sentence itself does not name its publisher.',
              ['cand-1758', 'cand-1761', 'cand-1205', 'cand-1211'], notes=[(5, 'L215')], extra={'relation_candidate': True})
add_statement('novelli-goldoni-lower-social-world', 'cand-1761', 'cand-10036',
              'placed_goldoni_comedies_in_lower_social_world_than_pasquali_set', 76, 77,
              'this time he placed the comedies in a far lower social world',
              'when working earlier for Pasquali.',
              'The comparison is with Novelli’s earlier Pasquali illustrations, whose p.338 context describes rich professional classes; “far lower” remains Haskell’s characterization.',
              ['cand-1761', 'cand-10036', 'cand-1210', 'cand-1211', 'cand-10018', 'cand-1844'])
add_statement('other-illustrated-book-publishers-limited-artistic-influence', 'cand-2068', None,
              'other_publishers_illustrated_books_but_had_less_influence_on_artistic_output', 77, 77,
              'Many other publishers besides Albrizzi, Pasquali and Zatta produced fine illustrated books',
              'they cannot therefore be discussed here.',
              'Haskell’s scope decision and comparative evaluation are preserved; the passage does not name the other publishers.',
              ['cand-2068', 'cand-0025', 'cand-1844', 'cand-2865'])
add_statement('pinelli-published-books-for-state', 'cand-1932', 'cand-10032',
              'mostly_produced_books_for_state', 77, 77,
              'was mostly engaged in turning out books for the State',
              'of no artistic interest,',
              'Haskell’s evaluation of their artistic interest is not an objective property of every book; the State’s exact identity is not stated.',
              ['cand-1932', 'cand-10032'], extra={'relation_candidate': True})
add_statement('pinelli-private-collector-patron', 'cand-1932', None,
              'was_private_collector_and_patron_on_large_scale', 77, 77,
              'was a private collector and patron on a large scale.',
              'on a large scale.',
              'This is Haskell’s summary of Pinelli’s activity.',
              ['cand-1932'])
add_statement('pinelli-library-famous-in-europe', 'cand-1932', 'cand-10030',
              'known_for_library_described_as_one_of_europes_most_famous', 77, 77,
              'he is best known for his library, one of the most famous in Europe',
              'famous in Europe,',
              'The superlative is Haskell’s evaluation; the library is a private collection, not automatically an institution.',
              ['cand-1932', 'cand-10030'])
add_statement('pinelli-owned-many-hundred-pictures', 'cand-1932', 'cand-10031',
              'owned_many_hundred_pictures', 77, 77,
              'he also owned many hundred pictures.',
              'many hundred pictures.',
              'Retain Haskell’s approximate quantity. Printed note 6 identifies a sale catalogue and another reference, both pending source-order processing.',
              ['cand-1932', 'cand-10031'], notes=[(6, 'L216')], extra={'relation_candidate': True})

# Close the p.338 cross-page statement with the first word on printed p.339.
closure_id = 'st-chp13-p338-zatta-proposed-jesuit-polemical-publications'
if closure_id not in statement_by_id:
    raise SystemExit('p.338 Zatta continuation statement missing')
closure = statement_by_id[closure_id]
if closure.get('qualifiers', {}).get('continuation_status') != 'open':
    raise SystemExit('p.338 Zatta statement is not open for continuation')
closure['qualifiers'].update({
    'continuation_status': 'closed',
    'continuation_closed_by_segment_id': BODY,
    'continuation_line_start': 71,
    'continuation_line_end': 71,
    'continuation_suffix': 'government',
    'continuation_footnote_refs': [note_ref(1, 'L211-L212')],
    'continuation_closed_note': 'The phrase “the Portuguese” at p.338 closes as “the Portuguese government” at p.339 L71; p.339 printed footnote 1 remains pending in L211-L212.',
    'cross_reference_segments': [BODY, NOTES],
    'qualification': '“Two or three” is approximate. The Portuguese target is completed as “Portuguese government” at p.339 L71. Printed p.339 footnote 1 maps to consolidated L211-L212 and remains pending.'
})

candidate_by_id['cand-10015']['detail'] = 'The phrase is completed as “Portuguese government” at p.339 S0 L71. Its identity remains described at the level stated by the source.'
for row in mentions:
    if row['mention_id'] == 'm-s2-ch13-p338-048':
        row['note'] = 'Completed by the p.339 L71 mention “government”; together the two page-local anchors form “the Portuguese government”.'
        break
else:
    raise SystemExit('p.338 Portuguese mention missing')

expected_p338_coverage = 'Printed p.338 body and visible notes reviewed against CHP-13.pdf physical page 7. Goldoni’s life-scene frontispiece proposal and examples are recorded with the accepted Plate 57b link. Printed footnotes 1–2 map to consolidated L209–210 and await source-order processing. The p.338 sentence on Zatta’s proposed Jesuit attacks continues at p.339 S0 L71; keep partial until continuation and notes are linked.'
if coverage[PREVIOUS]['note'] != expected_p338_coverage:
    raise SystemExit('p.338 coverage note changed unexpectedly')
coverage[PREVIOUS]['note'] = 'Printed p.338 body and visible notes reviewed against CHP-13.pdf physical page 7. Goldoni’s life-scene frontispiece proposal and examples are recorded with the accepted Plate 57b link. The Zatta cross-page sentence is closed by p.339 L71; printed footnotes 1–2 map to consolidated L209–210 and remain pending, so coverage stays partial.'

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

new_statement_ids = {row['statement_id'] for row in new_statements}
for cid in ('cand-0025', 'cand-0116', 'cand-0900', 'cand-1047', 'cand-1205', 'cand-1321',
            'cand-1411', 'cand-1659', 'cand-1758', 'cand-1761', 'cand-1844', 'cand-1892',
            'cand-1932', 'cand-2068', 'cand-2544', 'cand-2719', 'cand-2865', 'cand-2866',
            'cand-2874', 'cand-10015', 'cand-10018', 'cand-10024', 'cand-10028', 'cand-10031'):
    if cid not in all_candidate_ids:
        raise SystemExit(f'required candidate missing: {cid}')

coverage[BODY].update({
    'disposition': 'reviewed',
    'migration_status': 'partial',
    'source_line_ranges': 'L70-77',
    'note': 'Printed p.339 body and footnotes 1–6 reviewed against CHP-13.pdf physical page 8. The p.338 Portuguese-government phrase is closed at L71. Footnotes 1–6 map to consolidated L211–216 and await source-order processing; retain partial until notes are linked. OCR corrections are recorded in S2 only.'
})
coverage_rows = [coverage[row['segment_id']] for row in coverage_rows]

print(f'p.339 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements')
print('coverage: p.338 continuation closed; p.339 -> reviewed/partial; printed notes 1–6 await L211–216')
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
