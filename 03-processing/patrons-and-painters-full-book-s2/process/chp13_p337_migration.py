"""Controlled S2 migration for printed p.337; dry-run by default."""
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
BODY = 'chp-13:13_CHP-13_intro:l52-59'
PREVIOUS = 'chp-13:13_CHP-13_intro:l41-50'
NEXT = 'chp-13:13_CHP-13_intro:l61-68'
NOTES = 'chp-13:13_CHP-13_intro:l179-251'
SOURCE_SHA = 'c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8'
PDF_SHA = 'da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc'
BACKUP_SUFFIX = '.bak-s2-chp13-p337-20261003'

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='apply reviewed p.337 S2 migration')
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
    52: '[Page 337]',
    53: 'succeeding in the affairs that interest him',
    54: 'Smithiana. This contained 100 plates engraved by Brustolon',
    55: 'Albrizzi’s publication a few years earlier of the gems',
    56: 'The only concession to the more painterly.',
    57: 'On one occasion Pasquali too employed Piazzetta',
    58: 'Much more attention was to be paid to paper',
    59: '- too like an elegant, clean and well adorned page',
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
if state != (9996, 10009, 21314, 9503):
    raise SystemExit(f'unexpected table pre-state: {state}')
for segment_id in (BODY, PREVIOUS, NEXT, NOTES):
    if segment_id not in coverage:
        raise SystemExit(f'required coverage row missing: {segment_id}')
if (coverage[BODY]['disposition'], coverage[BODY]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.337 is not queued/pending')
if (coverage[PREVIOUS]['disposition'], coverage[PREVIOUS]['migration_status']) != ('reviewed', 'partial'):
    raise SystemExit('p.336 is not reviewed/partial')
if (coverage[NEXT]['disposition'], coverage[NEXT]['migration_status']) != ('queued', 'pending'):
    raise SystemExit('p.338 continuation is not queued/pending')
if any(row['segment_id'] == BODY for row in mentions) or any(row['segment_id'] == BODY for row in statements):
    raise SystemExit('p.337 rows already exist')
new_ids = {f'cand-{n}' for n in range(10010, 10013)}
if new_ids & candidate_ids:
    raise SystemExit(f'p.337 candidate IDs already exist: {sorted(new_ids & candidate_ids)}')
if any(row['mention_id'].startswith('m-s2-ch13-p337-') for row in mentions):
    raise SystemExit('p.337 mention IDs already exist')
if any(row['statement_id'].startswith('st-chp13-p337-') for row in statements):
    raise SystemExit('p.337 statement IDs already exist')

body_lines = {n: source_lines[n - 1] for n in range(52, 60)}
segment_text = '\n'.join(body_lines[n] for n in range(52, 60))
new_candidates = []
def add_candidate(cid, name, kind, detail, line):
    row = {field: '' for field in candidate_fields}
    row.update({'candidate_id': cid, 'canonical_name': name, 'suggested_type': kind, 'status': 'open',
                'detail': detail, 'candidate_origin': 'body-mention', 'candidate_source_ref': f'{BODY}#L{line}'})
    new_candidates.append(row)

add_candidate('cand-10010', 'Unidentified English grammar among Giambattista Pasquali’s early books', 'archive',
              'Haskell says one of Pasquali’s first books was an English grammar, but supplies no title or author. Keep it as a descriptive unidentified work.', 53)
add_candidate('cand-10011', 'Perseus and the Head of Medusa endplate in Dactylografa Smithiana', 'work',
              'An endplate engraved by Andrea Brustolon after a drawing by Pietro Antonio Novelli. The image title is transcribed as printed; no separate impression or collection location is given.', 56)
add_candidate('cand-10012', 'Unspecified Albrizzi publication of gems in A. M. Zanetti’s collection', 'archive',
              'Haskell compares the later Dactylografa Smithiana with Albrizzi’s earlier publication of gems in Zanetti’s collection. This descriptive candidate is not automatically merged with the indexed Dactyliotheca Ant. M. Zanetti.', 55)
all_candidate_ids = candidate_ids | {row['candidate_id'] for row in new_candidates}

new_mentions = []
def line_offset(line):
    return sum(len(body_lines[n]) + 1 for n in range(52, line))

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
    row.update({'mention_id': f'm-s2-ch13-p337-{len(new_mentions) + 1:03d}', 'segment_id': BODY,
                'candidate_id': cid, 'surface_form': surface, 'start_char': start,
                'end_char': start + len(surface), 'note': note})
    new_mentions.append(row)

def add_cross_mention(first, last, start_text, end_text, cid, note=''):
    text = '\n'.join(body_lines[n] for n in range(first, last + 1))
    start = text.find(start_text)
    end = text.find(end_text, start)
    if start < 0 or end < 0:
        raise SystemExit(f'cross-line mention boundary missing: {start_text!r}/{end_text!r}')
    surface = text[start:end + len(end_text)]
    begin = line_offset(first) + start
    if segment_text[begin:begin + len(surface)] != surface:
        raise SystemExit(f'cross-line mention span mismatch: {surface!r}')
    row = {field: '' for field in mention_fields}
    row.update({'mention_id': f'm-s2-ch13-p337-{len(new_mentions) + 1:03d}', 'segment_id': BODY,
                'candidate_id': cid, 'surface_form': surface, 'start_char': begin,
                'end_char': begin + len(surface), 'note': note})
    new_mentions.append(row)

# The opening words close the archival-letter quotation begun on p.336.
add_mention(53, 'Pasquali', 'cand-1844')
add_mention(53, 'Carlo Lodoli', 'cand-1411')
add_mention(53, 'the censorship', 'cand-1850')
add_mention(53, 'a letter to a bookseller in Prato', 'cand-1850', 'Printed note 2 identifies the correspondent and publication; consolidated note L204 remains pending.')
add_mention(53, 'Inquisitori di Stato', 'cand-9739')
add_mention(53, 'Beccaria', 'cand-0265')
add_mention(53, 'Dei delitti e delle pene', 'cand-9707')
add_mention(53, 'all the clients', 'cand-1850')
add_mention(53, 'elegant pamphlets for aristocratic ceremonies', 'cand-1844')
add_mention(53, 'his patron Joseph Smith', 'cand-2440')
add_mention(53, 'the firm', 'cand-9799')
add_mention(53, 'an English grammar', 'cand-10010')
add_mention(53, 'Pasquali', 'cand-1847', occurrence=1)
add_mention(53, 'Smith’s collection', 'cand-9626')
add_mention(53, 'paintings by Cignani and Ricci in 1749', 'cand-1847')
add_mention(53, 'Cignani', 'cand-0748')
add_mention(53, 'Ricci', 'cand-2154')
add_cross_mention(53, 54, 'the Dactylografa', 'Smithiana', 'cand-1848', 'Title continues at S0 L54; index also has a Dactylografia spelling variant.')
add_mention(54, '100 plates', 'cand-1848')
add_mention(54, 'Brustolon', 'cand-0463')
add_mention(54, 'Smith’s medals and gems', 'cand-9556')
add_mention(55, 'Albrizzi’s publication a few years earlier of the gems in A. M. Zanetti’s collection', 'cand-10012')
add_mention(55, 'that book', 'cand-1848', 'Anaphoric reference to Dactylografa Smithiana.')
add_mention(56, 'an endplate of Perseus and the Head of Medusa', 'cand-10011')
add_mention(56, 'Brustolon', 'cand-0463')
add_mention(56, 'Pietro Antonio Novelli', 'cand-1758')
add_mention(56, 'Pasquali', 'cand-1844')
add_mention(56, 'Piazzetta', 'cand-1901')
add_mention(56, 'Albrizzi', 'cand-0025')
add_mention(57, 'Pasquali', 'cand-1844')
add_mention(57, 'Piazzetta', 'cand-1901')
add_mention(57, 'the Beatae Mariae Virginis Officium', 'cand-1849')
add_mention(57, 'in 1740', 'cand-1849')
add_mention(57, 'à rich merchant called Caime', 'cand-0480', 'S0 OCR reads “à”; the scan reads “a”.')
add_mention(57, 'the seventeen-volume edition of the works of Goldoni', 'cand-1851')
add_mention(57, 'Goldoni', 'cand-1205')
add_mention(57, 'the author', 'cand-1205')
add_mention(57, 'book illustration', 'cand-1851')
add_mention(57, 'Goldoni', 'cand-1205', occurrence=1)
add_mention(58, 'paper', 'cand-1851')
add_mention(58, 'printing', 'cand-1851')
add_mention(58, 'illustration', 'cand-1851')
add_mention(59, 'an elegant, clean and well adorned page', 'cand-1851')
add_mention(59, 'Pasquali’s edition of Goldoni', 'cand-1851')

new_statements = []
ocr_corrections = [
    {'source_line': 53, 'ocr': 'chased under the censorship', 'print': 'chafed under the censorship', 'basis': 'CHP-13.pdf physical page 6.'},
    {'source_line': 53, 'ocr': 'Dei delitti e delle pene\',', 'print': 'Dei delitti e delle pene;', 'basis': 'CHP-13.pdf physical page 6.'},
    {'source_line': 56, 'ocr': 'painterly. Baroque', 'print': 'painterly Baroque', 'basis': 'CHP-13.pdf physical page 6.'},
    {'source_line': 57, 'ocr': 'à rich merchant', 'print': 'a rich merchant', 'basis': 'CHP-13.pdf physical page 6.'},
    {'source_line': 57, 'ocr': 'pubUcations', 'print': 'publications', 'basis': 'CHP-13.pdf physical page 6.'},
    {'source_line': 58, 'ocr': 'général run', 'print': 'general run', 'basis': 'CHP-13.pdf physical page 6.'},
    {'source_line': 59, 'ocr': '- too like', 'print': 'too like', 'basis': 'CHP-13.pdf physical page 6; line-break hyphen removed.'},
]

def excerpt(line, start, end):
    text = body_lines[line]
    a, b = text.find(start), text.find(end, text.find(start))
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
    return {'footnote_marker': marker, 'footnote_printed_page': 337, 'footnote_text_pending': True,
            'footnote_segment': NOTES, 'footnote_body_link_status': 'pending',
            'cross_reference_segments': [NOTES]}

def add_statement(suffix, subject, obj, predicate, start_line, end_line, claim, quote, qualification,
                  mentioned, *, speaker='Haskell', layer='authorial narrative', extra=None):
    sid = f'st-chp13-p337-{suffix}'
    if sid in statement_by_id or any(row['statement_id'] == sid for row in new_statements):
        raise SystemExit(f'duplicate statement ID: {sid}')
    if quote not in segment_text:
        raise SystemExit(f'statement quote not anchored in S0: {sid}')
    if any(cid not in all_candidate_ids for cid in mentioned + [x for x in (subject, obj) if x]):
        raise SystemExit(f'missing candidate FK: {sid}')
    q = {'source_line_start': start_line, 'source_line_end': end_line, 'printed_page': 337,
         'pdf_physical_page': 6, 'claim': claim, 'speaker': speaker, 'text_layer': layer,
         'qualification': qualification, 'mentioned_candidate_ids': mentioned,
         'ocr_corrections': [item for item in ocr_corrections if start_line <= item['source_line'] <= end_line]}
    if extra:
        q.update(extra)
    new_statements.append({'statement_id': sid, 'segment_id': BODY, 'subject_candidate_id': subject or None,
                           'object_candidate_id': obj or None, 'predicate': predicate, 'qualifiers': q,
                           'original_quote': quote, 'origin': 'book',
                           'source_file': '02-sources/02-Markdown/13_CHP-13_intro.md'})

# Close the archival quotation opened on p.336; printed note 8 is still pending.
prior = statement_by_id['st-chp13-p336-gherardi-characterisation-of-publishers-open']
pq = prior['qualifiers']
pq.update({'continuation_status': 'closed_on_p337', 'continuation_quote_pending': False,
           'continuation_quote': excerpt(53, 'succeeding in the affairs that interest him', 'succeeding in the affairs that interest him'),
           'continuation_quote_segment_id': BODY, 'continuation_quote_source_line_start': 53,
           'continuation_quote_source_line_end': 53, 'cross_reference_segments': [PREVIOUS, BODY, NOTES]})
pq['qualification'] = 'Printed p.336 note 8 identifies the Gherardi–Muratori letter; consolidated note L202 remains pending. The quotation closes at the start of p.337 L53.'

add_statement('pasquali-admired-lodoli', 'cand-1844', 'cand-1411', 'admired_carolo_lodoli', 53, 53,
              'Haskell says Pasquali worshipped Carlo Lodoli.', excerpt(53, 'Pasquali worshipped Carlo Lodoli', 'Carlo Lodoli'),
              'This is Haskell’s characterization of Pasquali’s admiration; printed note 1 and consolidated L203 await linkage.',
              ['cand-1844', 'cand-1411'], extra=pending_note(1))
add_statement('pasquali-chafed-under-censorship', 'cand-1844', None, 'chafed_under_censorship', 53, 53,
              'Haskell says Pasquali chafed under censorship that he implied prevented him from publishing what he wanted.',
              excerpt(53, 'he chased under the censorship', 'what he wanted'),
              'The letter is reported by Haskell; do not treat this as independently verified censorship correspondence.',
              ['cand-1844', 'cand-1850'], extra={**pending_note(2), 'relation_candidate': True})
add_statement('pasquali-secretly-distributed-beccaria-1764', 'cand-1844', 'cand-9707', 'secretly_distributed_copies_in_1764', 53, 53,
              'In 1764 Pasquali got into trouble with the Inquisitori di Stato for secretly distributing copies of Beccaria’s forbidden Dei delitti e delle pene.',
              excerpt(53, 'in 1764 he got into trouble', 'for secretly distributing copies of Beccaria’s forbidden Dei delitti e delle pene'),
              'Haskell reports the incident and calls the book forbidden; printed note 3 cites a Venetian state archive record, pending L205.',
              ['cand-1844', 'cand-9739', 'cand-0265', 'cand-9707'], extra={**pending_note(3), 'relation_candidate': True})
add_statement('pasquali-revealed-book-clients-under-pressure', 'cand-1844', None, 'revealed_clients_after_pressure', 53, 53,
              'Under pressure, Pasquali revealed the names of all clients to whom he had sold the book.',
              excerpt(53, 'under pressure he revealed the names', 'to whom he had sold the book'),
              'Haskell says Pasquali was “no martyr”; this is the author’s characterization, not a claim about motive.',
              ['cand-1844', 'cand-9707'], extra={**pending_note(3), 'relation_candidate': True})
add_statement('pasquali-limited-ceremonial-pamphlets', 'cand-1844', None, 'showed_little_interest_in_aristocratic_ceremonial_pamphlets', 53, 53,
              'Haskell says Pasquali showed little interest in producing elegant pamphlets for aristocratic ceremonies.',
              excerpt(53, 'He showed little interest', 'aristocratic ceremonies,'),
              'A qualified statement (“little interest”), not a claim that he never produced such pamphlets.',
              ['cand-1844'])
add_statement('smith-controlled-interest-in-pasquali-firm', 'cand-2440', 'cand-9799', 'retained_controlling_interest_in_publishing_firm', 53, 53,
              'Haskell says Joseph Smith retained a controlling interest in Pasquali’s publishing firm.',
              excerpt(53, 'his patron Joseph Smith', 'controlling interest in the firm'),
              'The source establishes Smith as patron and a controlling interest, without specifying its legal or financial form.',
              ['cand-2440', 'cand-2474', 'cand-1844', 'cand-9799'], extra={**pending_note(4), 'relation_candidate': True})
add_statement('english-grammar-among-pasquali-early-books', 'cand-1844', 'cand-10010', 'one_of_first_books_produced_by', 53, 53,
              'Haskell says one of the first books produced by Pasquali was an English grammar.',
              excerpt(53, 'one of the first books produced by Pasquali', 'an English grammar.'),
              'The grammar is unidentified; printed note 4 provides a book citation, pending L206.',
              ['cand-1844', 'cand-10010'], extra={**pending_note(4), 'relation_candidate': True})
add_statement('pasquali-books-recorded-smith-collection', 'cand-1844', 'cand-1847', 'published_illustrated_books_recording_smith_collection', 53, 53,
              'Pasquali published finely illustrated books recording some treasures in Smith’s collection, including paintings by Cignani and Ricci in 1749.',
              excerpt(53, 'It was naturally Pasquali who published', 'and Ricci in 1749,'),
              'The source names the artists and year but not the paintings or an exact title for this book group.',
              ['cand-1844', 'cand-2440', 'cand-9626', 'cand-1847', 'cand-0748', 'cand-2154'], extra={'relation_candidate': True})
add_statement('pasquali-published-dactylografa-smithiana', 'cand-1844', 'cand-1848', 'published_dactylografa_smithiana_1767', 53, 54,
              'Eighteen years after 1749, Pasquali published Dactylografa Smithiana.',
              cross_excerpt(53, 54, 'eighteen years later the Dactylografa', 'Smithiana.'),
              'The relative date places the work in 1767; preserve the printed title spelling and the index spelling variant for S3.',
              ['cand-1844', 'cand-2440', 'cand-1848', 'cand-2458'], extra={'relation_candidate': True})
add_statement('dactylografa-contained-100-brustolon-plates', 'cand-1848', None, 'contained_100_plates_engraved_by_brustolon', 54, 54,
              'Dactylografa Smithiana contained 100 plates engraved by Brustolon.',
              excerpt(54, 'This contained 100 plates', 'engraved by Brustolon,'),
              'The printed passage says 100 plates; it does not identify individual plates beyond the endplate described below.',
              ['cand-1848', 'cand-0463'], extra={'relation_candidate': True})
add_statement('dactylografa-illustrated-smith-medals-gems', 'cand-1848', 'cand-9556', 'illustrated_smiths_medals_and_gems', 54, 54,
              'The plates illustrated Smith’s medals and gems.', excerpt(54, 'illustrating Smith’s medals and gems', 'Smith’s medals and gems'),
              'The collection is described generally; do not infer a complete catalogue or current holdings.',
              ['cand-1848', 'cand-2440', 'cand-9556'], extra={'relation_candidate': True})
add_statement('dactylografa-neoclassical-style', 'cand-1848', None, 'mostly_severely_neoclassical_style', 54, 54,
              'Haskell says most of the plates were in a severely Neoclassical style.',
              excerpt(54, 'mostly in a severely neoclassical style', 'neoclassical style'),
              'This stylistic characterization applies to most, not all, plates.', ['cand-1848'])
add_statement('dactylografa-influenced-by-albrizzi-zanetti-publication', 'cand-1848', 'cand-10012', 'clearly_influenced_by_earlier_gem_publication', 54, 55,
              'Haskell says Dactylografa Smithiana was clearly influenced by Albrizzi’s earlier publication of gems in A. M. Zanetti’s collection.',
              cross_excerpt(54, 55, 'it was clearly influenced by', 'collection.'),
              'This is Haskell’s influence claim. The earlier publication’s identity is not supplied here and is kept separate from the indexed Dactyliotheca candidate.',
              ['cand-1848', 'cand-0025', 'cand-10012', 'cand-2838'], extra={'relation_candidate': True})
add_statement('dactylografa-simpler-presentation-than-albrizzi-book', 'cand-1848', 'cand-10012', 'presentation_simpler_than_comparator', 55, 55,
              'Haskell says Dactylografa Smithiana had a far simpler presentation and lacked the rich, elaborate decoration of the earlier Albrizzi book.',
              excerpt(55, 'But the general presentation is far simpler', 'decoration of that book,'),
              'This is a comparison of presentation, not a claim that the books had identical content.', ['cand-1848', 'cand-10012'])
add_statement('dactylografa-latin-only-scholarly-audience', 'cand-1848', None, 'printed_in_latin_only_for_scholarly_public', 55, 55,
              'The text was printed only in Latin and aimed at a more scholarly public.',
              excerpt(55, 'the text—printed in Latin only—is aimed', 'a more scholarly public.'),
              'The audience is Haskell’s description of the intended public.', ['cand-1848'])
add_statement('dactylografa-medusa-endplate-engraved-after-novelli', 'cand-0463', 'cand-10011', 'engraved_endplate_after_novelli_drawing', 56, 56,
              'The endplate showing Perseus and the Head of Medusa was engraved by Brustolon from a drawing by Pietro Antonio Novelli.',
              excerpt(56, 'an endplate of Perseus and the Head of Medusa', 'from a drawing by Pietro Antonio Novelli'),
              'The printed page calls this the only concession to the more painterly Baroque style; keep the image distinct from the book as a whole.',
              ['cand-10011', 'cand-0463', 'cand-1758', 'cand-1848'], extra={'relation_candidate': True})
add_statement('novelli-associated-with-pasquali', 'cand-1758', 'cand-1844', 'closely_associated_with_publisher', 56, 56,
              'Haskell says Novelli was almost as closely associated with Pasquali as Piazzetta was with Albrizzi.',
              excerpt(56, 'an artist almost as closely associated with Pasquali', 'Piazzetta was with Albrizzi.'),
              'This is Haskell’s comparative characterization; it does not specify a formal contract or exclusive relationship.',
              ['cand-1758', 'cand-1844', 'cand-1901', 'cand-0025'], extra={'relation_candidate': True})
add_statement('pasquali-employed-piazzetta-for-officium', 'cand-1844', 'cand-1849', 'employed_piazzetta_to_illustrate_religious_work', 57, 57,
              'In 1740 Pasquali employed Piazzetta to provide illustrations for Beatae Mariae Virginis Officium.',
              excerpt(57, 'Pasquali too employed Piazzetta', 'published in 1740'),
              'Printed note 5 cites Morazzoni p.116; the consolidated note L207 remains pending.',
              ['cand-1844', 'cand-1901', 'cand-1849'], extra={**pending_note(5), 'relation_candidate': True})
add_statement('officium-plates-religious-intimacy', 'cand-1849', None, 'plates_described_as_religiously_intimate', 57, 57,
              'Haskell describes the Officium’s plates as having great religious intimacy.',
              excerpt(57, 'with plates of great religious intimacy', 'great religious intimacy.'),
              'This is Haskell’s stylistic evaluation.', ['cand-1849'], extra=pending_note(5))
add_statement('officium-commissioned-and-financed-by-caime', 'cand-0480', 'cand-1849', 'commissioned_and_financed_religious_book', 57, 57,
              'The Officium was specially commissioned and financed by a rich merchant called Caime.',
              excerpt(57, 'especially commissioned and financed', 'called Caime'),
              'The source gives only the surname Caime and no individual commission terms; note 5 remains pending.',
              ['cand-0480', 'cand-1849'], extra={**pending_note(5), 'relation_candidate': True})
add_statement('officium-distinct-from-pasquali-general-output', 'cand-1849', 'cand-1844', 'stood_out_from_general_publishing_output', 57, 57,
              'Haskell says the specially commissioned Officium stood out from the general run of Pasquali’s publications.',
              excerpt(57, 'it stands out from the general run', 'pubUcations.'),
              'The comparison does not imply that the whole publishing programme was religious.', ['cand-1849', 'cand-1844'])
add_statement('pasquali-goldoni-seventeen-volume-edition-started-1761', 'cand-1844', 'cand-1851', 'began_seventeen_volume_goldoni_edition_in_1761', 57, 57,
              'Pasquali’s seventeen-volume edition of Goldoni’s works began to appear in 1761.',
              excerpt(57, 'His most enterprising venture was the seventeen-volume edition', 'began to appear in 1761.'),
              'The edition began in 1761; the passage does not claim all volumes appeared that year.',
              ['cand-1844', 'cand-1851', 'cand-1205', 'cand-1210'], extra={'relation_candidate': True})
add_statement('goldoni-edition-close-author-collaboration', 'cand-1851', 'cand-1205', 'produced_in_closest_collaboration_with_author', 57, 57,
              'The edition was produced in the closest collaboration with Goldoni.',
              excerpt(57, 'This was produced in the closest collaboration', 'with the author,'),
              'The author is Carlo Goldoni in the immediate context; preserve Haskell’s description of the collaboration.',
              ['cand-1851', 'cand-1205'], extra={'relation_candidate': True})
add_statement('goldoni-edition-designed-as-new-departure', 'cand-1851', None, 'designed_to_mark_new_departure_in_book_illustration', 57, 57,
              'The edition was designed to mark a new departure in book illustration.',
              excerpt(57, 'was designed to mark a new departure', 'in book illustration.'),
              'This describes its design ambition; whether the volume set achieved it remains the author’s assessment.', ['cand-1851'])
add_statement('goldoni-criticised-earlier-commercial-production', 'cand-1205', 'cand-1851', 'criticised_earlier_commercial_production_style', 57, 57,
              'Goldoni complained that until then his works had been produced in a style he called “commercial”.',
              excerpt(57, 'Until now, complained Goldoni', 'commercial’.'),
              'This is Goldoni’s reported criticism of earlier editions, not a general market classification.',
              ['cand-1205', 'cand-1851'], speaker='Carlo Goldoni (quoted by Haskell)', layer='author quoted in Haskell', extra={**pending_note(6), 'relation_candidate': True})
add_statement('goldoni-said-paper-and-printing-economised', 'cand-1205', 'cand-1851', 'reported_economy_in_paper_and_printing', 57, 57,
              'Goldoni said paper and printing had been economised to a degree that would discredit the best book in the world.',
              excerpt(57, 'Paper and printing had been economised', 'the best book in the world.'),
              'This is Goldoni’s quoted complaint; the source gives no quantitative production data.',
              ['cand-1205', 'cand-1851'], speaker='Carlo Goldoni (quoted by Haskell)', layer='author quoted in Haskell', extra={**pending_note(6), 'relation_candidate': True})
add_statement('goldoni-promised-increased-production-attention', 'cand-1205', 'cand-1851', 'announced_more_attention_to_paper_printing_illustration', 57, 58,
              'Goldoni says that now much more attention would be paid to paper, printing, and illustration.',
              cross_excerpt(57, 58, 'Now all this was to change.', 'illustration.'),
              'This is Goldoni’s reported statement about the edition’s production intentions; note 6 is pending L208.',
              ['cand-1205', 'cand-1851'], speaker='Carlo Goldoni (quoted by Haskell)', layer='author quoted in Haskell', extra={**pending_note(6), 'relation_candidate': True})
add_statement('goldoni-acknowledged-higher-cost', 'cand-1205', 'cand-1851', 'acknowledged_higher_book_cost', 58, 58,
              'Goldoni acknowledged that improved paper, printing, and illustration would make the book more expensive.',
              excerpt(58, 'this would mean a more expensive book', 'more expensive book,'),
              'The statement records the anticipated higher cost, not a specific price.',
              ['cand-1205', 'cand-1851'], speaker='Carlo Goldoni (quoted by Haskell)', layer='author quoted in Haskell', extra=pending_note(6))
add_statement('goldoni-favoured-elegant-clean-page', 'cand-1205', 'cand-1851', 'expressed_preference_for_elegant_clean_page', 58, 59,
              'Goldoni said he preferred an elegant, clean, well-adorned page.',
              cross_excerpt(58, 59, 'My dear friend, I reply, surely you', 'adorned page’.'),
              'The page-break hyphen in S0 is an OCR artifact confirmed against the scan. Goldoni is the speaker identified in the preceding sentence.',
              ['cand-1205', 'cand-1851'], speaker='Carlo Goldoni (quoted by Haskell)', layer='author quoted in Haskell', extra=pending_note(6))
add_statement('haskell-goldoni-edition-not-luxury-enterprise', 'cand-1844', 'cand-1851', 'not_designed_as_luxurious_enterprise', 59, 59,
              'Despite the tone of Goldoni’s remarks, Haskell says Pasquali’s edition of Goldoni was not designed as a luxurious enterprise.',
              excerpt(59, 'despite the tone of these remarks', 'not designed as a luxurious enterprise.'),
              'This is Haskell’s distinction between Goldoni’s rhetoric and the edition’s design; p.338 continues with its intended audience.',
              ['cand-1844', 'cand-1851', 'cand-1205'])

# Ensure no partial overlap or duplicate character spans among mentions.
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

for cid in ['cand-1844', 'cand-1411', 'cand-1850', 'cand-9739', 'cand-0265', 'cand-9707', 'cand-2440',
            'cand-9799', 'cand-9626', 'cand-1847', 'cand-0748', 'cand-2154', 'cand-1848', 'cand-0463',
            'cand-9556', 'cand-0025', 'cand-2838', 'cand-1849', 'cand-0480', 'cand-1851', 'cand-1205',
            'cand-1210', 'cand-1758']:
    if cid not in candidate_ids:
        raise SystemExit(f'required S1/body candidate missing: {cid}')

all_candidates = sorted(candidates + new_candidates, key=lambda row: row['candidate_id'])
all_mentions = sorted(mentions + new_mentions, key=lambda row: (row['segment_id'], int(row['start_char']), int(row['end_char']), row['mention_id']))
all_statements = sorted(statements + new_statements, key=lambda row: row['statement_id'])
if len({row['candidate_id'] for row in all_candidates}) != len(all_candidates):
    raise SystemExit('duplicate candidate id')
if len({row['mention_id'] for row in all_mentions}) != len(all_mentions):
    raise SystemExit('duplicate mention id')
if len({row['statement_id'] for row in all_statements}) != len(all_statements):
    raise SystemExit('duplicate statement id')

coverage[BODY].update({'disposition': 'reviewed', 'migration_status': 'partial', 'source_line_ranges': 'L52-59',
    'note': 'Printed p.337 body and visible notes reviewed against CHP-13.pdf physical page 6. The Gherardi/Muratori quotation begun on p.336 closes in the first words of L53. Footnotes 1–6 map to consolidated notes L203–208 and await source-order processing. The p.337 Goldoni quotation closes on this page; p.338 continues Haskell’s discussion of the edition.'})
coverage[PREVIOUS]['note'] = 'Printed p.336 body and visible notes reviewed against CHP-13.pdf physical page 5. The p.335 Gerbault subscription sentence closes at L42. The opening Gherardi/Muratori quotation continues into p.337 L53 and is now closed there. Printed notes 1–8 still await consolidated L195–202.'

print(f'p.337 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements; closed p.336 quotation')
print('coverage: p.337 -> reviewed/partial; notes 1–6 await L203–208; page-end Goldoni quotation closes')
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
