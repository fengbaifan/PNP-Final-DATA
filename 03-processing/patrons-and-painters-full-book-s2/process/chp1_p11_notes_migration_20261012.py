import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge' / 'tables'
NOTE_SEG = 'chp-1:01_CHP-1_sec_ii:l168-239'
BODY_SEG = 'chp-1:01_CHP-1_sec_ii:l48-60'
SOURCE_FULL = ROOT / '02-sources' / '02-Markdown' / '01_CHP-1.md'
OLD_ID = 'st-chp1-secii-notes-gini-lanfranco'
BACKUP_SUFFIX = '.bak-s2-chp1-secii-p11-notes-20261012'
EXPECTED = {
    'book-statements.jsonl': 'c20520548a7b0cc8bf12acc1fd97e679417da4e35f89f29522318295d0efb8df',
    'entity-candidates.csv': '3bc60e520bb6c45674b34e3d362e5312996b8997e475d74c3d9777f4635ad325',
    'mentions.csv': '34c745ef817f78841a03c5dd553ed7bd6771a7aeaa6f9d10a0adc767752b459d',
    's2-coverage.csv': 'e6b979a4341617f3bda81d9790b99b710ef8f745e31d0f11c39d6569967c8e80',
}
SOURCE_SHA = '2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb'
SEGMENT_SHA = 'b5560e20ceb3b9b531266ac26966dd0a7f76c6ce8bbc82f6664a9a95d68af258'
SOURCE_LINES = None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def normalize_with_offsets(text):
    chars, offsets = [], []
    prior_space = False
    for i, char in enumerate(text):
        if char.isspace():
            if not prior_space:
                chars.append(' ')
                offsets.append(i)
            prior_space = True
        else:
            chars.append(char)
            offsets.append(i)
            prior_space = False
    return ''.join(chars), offsets


def excerpt(lines, start, end, phrase=None):
    raw = '\n'.join(lines[start - 1:end])
    if phrase is None:
        return raw
    normalized, positions = normalize_with_offsets(raw)
    target = ' '.join(phrase.split())
    offset = normalized.find(target)
    if offset < 0:
        raise ValueError(f'quote missing from source L{start}-{end}: {phrase}')
    return raw[positions[offset]:positions[offset + len(target) - 1] + 1]


def normalized_span(text, phrase):
    normalized, positions = normalize_with_offsets(text)
    target = ' '.join(phrase.split())
    found = normalized.find(target)
    if found < 0:
        raise ValueError(f'mention phrase missing from S0 segment: {phrase}')
    start, end = positions[found], positions[found + len(target) - 1] + 1
    surface = text[start:end]
    if '\n' in surface or '\r' in surface:
        raise ValueError(f'mention surface crosses source line: {phrase}')
    return start, end, surface


def citation_row(sid, marker, start, end, quote_phrase, source_candidate,
                 publication_candidate, locator, claim, body_id, qualification,
                 mentioned, *, cited_document=None):
    q = {
        'source_line_start': start,
        'source_line_end': end,
        'printed_page': 11,
        'pdf_physical_page': 10,
        'claim': claim,
        'speaker': f'Haskell footnote {marker}',
        'text_layer': 'bibliographic citation',
        'qualification': qualification,
        'relation_candidate': True,
        'relation_candidate_note': "This records Haskell's citation path; it does not assert the cited publication's contents beyond the stated claim.",
        'mentioned_candidate_ids': list(dict.fromkeys(mentioned)),
        'footnote_marker': marker,
        'footnote_number': marker,
        'footnote_segment': NOTE_SEG,
        'footnote_refs': [{'marker': marker, 'segment_id': NOTE_SEG, 'source_line': start}],
        'related_segment': BODY_SEG,
        'related_body_statement_ids': [body_id],
        'linked_body_statement_ids': [body_id],
        'cited_material_not_independently_consulted': True,
        'footnote_link_status': 'linked',
        'footnote_text_pending': False,
        'citation_candidate_id': source_candidate,
        'citation_publication_candidate_id': publication_candidate,
        'citation_locator': locator,
        'citations': [{
            'source_candidate_id': source_candidate,
            'publication_candidate_id': publication_candidate,
            'locator': locator,
        }],
    }
    if cited_document:
        q['cited_document_candidate_id'] = cited_document
    return {
        'statement_id': sid,
        'segment_id': NOTE_SEG,
        'subject_candidate_id': 'cand-2962',
        'object_candidate_id': publication_candidate,
        'predicate': 'cites',
        'qualifiers': q,
        'original_quote': excerpt(SOURCE_LINES, start, end, quote_phrase),
        'origin': 'book',
        'source_file': '02-sources/02-Markdown/01_CHP-1.md',
    }


def main():
    global SOURCE_LINES
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after all protected checks pass; default is preview')
    args = parser.parse_args()

    for name, expected in EXPECTED.items():
        actual = digest(TABLES / name)
        if actual != expected:
            raise SystemExit(f'protected hash mismatch for {name}: {actual}')
    if digest(SOURCE_FULL) != SOURCE_SHA:
        raise SystemExit('immutable S0 full-chapter source hash changed')
    print('protected four-table hashes and immutable S0 source hash matched')

    statements = read_jsonl(TABLES / 'book-statements.jsonl')
    candidates = read_csv(TABLES / 'entity-candidates.csv')
    mentions = read_csv(TABLES / 'mentions.csv')
    coverage = read_csv(TABLES / 's2-coverage.csv')
    statement_by_id = {row['statement_id']: row for row in statements}
    candidate_by_id = {row['candidate_id']: row for row in candidates}
    mention_by_id = {row['mention_id']: row for row in mentions}
    if OLD_ID not in statement_by_id:
        raise SystemExit(f'expected combined statement missing: {OLD_ID}')
    new_ids = [
        'st-chp1-secii-p11-n1-gini-letter-authored-by',
        'st-chp1-secii-p11-n1-gini-letter-subject-cortona',
        'st-chp1-secii-p11-n1-cites-claretta-p516',
        'st-chp1-secii-p11-n2-cites-pascoli-i-p84',
        'st-chp1-secii-p11-n3-cites-costello-p278',
        'st-chp1-secii-p11-n4-cites-friedlaender-p302',
        'st-chp1-secii-p11-n5-internal-cross-reference',
        'st-chp1-secii-p11-n6-cites-pollak-p26',
        'st-chp1-secii-p11-n6-lanfranco-letter-authored-by',
        'st-chp1-secii-p11-n6-haskell-interprets-in-tela',
        'st-chp1-secii-p11-n6-cites-costello-p274',
        'st-chp1-secii-p11-n6-lanfranco-regular-practice',
    ]
    if any(sid in statement_by_id for sid in new_ids):
        raise SystemExit('one or more p.11 replacement statement IDs already exist')

    required_candidates = {
        'cand-2962', 'cand-2941', 'cand-2949', 'cand-3087', 'cand-3096', 'cand-3508', 'cand-5985',
        'cand-1842', 'cand-4834', 'cand-3509', 'cand-7017', 'cand-3506', 'cand-4375',
        'cand-3510', 'cand-4359', 'cand-2953', 'cand-3053', 'cand-3534', 'cand-3452', 'cand-3571',
    }
    if not required_candidates.issubset(candidate_by_id):
        raise SystemExit(f'required existing candidate missing: {sorted(required_candidates - candidate_by_id.keys())}')

    segment_rows = read_jsonl(TABLES / 'segments.jsonl')
    segment = next(row for row in segment_rows if row['segment_id'] == NOTE_SEG)
    segment_path = ROOT / segment['source_file']
    if segment.get('sha256') != SEGMENT_SHA or digest(segment_path) != segment.get('asset_sha256'):
        raise SystemExit('p.11 source segment or asset fingerprint changed')
    segment_lines = segment_path.read_text(encoding='utf-8-sig').splitlines()
    segment_text = '\n'.join(segment_lines[int(segment['line_start']) - 1:int(segment['line_end'])])
    source_lines = SOURCE_FULL.read_text(encoding='utf-8-sig').splitlines()
    SOURCE_LINES = source_lines
    if excerpt(source_lines, 415, 425).count('8 Pollak') != 1:
        raise SystemExit('expected S0 OCR marker 8 in p.11 note 6 was not found')

    body_links = {
        1: 'st-chp1-secii-l48-60-01',
        2: 'st-chp1-secii-l48-60-01',
        3: 'st-chp1-secii-l48-60-02',
        4: 'st-chp1-secii-l48-60-04',
        5: 'st-chp1-secii-l48-60-05',
        6: 'st-chp1-secii-l48-60-06',
    }
    for sid in set(body_links.values()):
        if sid not in statement_by_id or statement_by_id[sid]['segment_id'] != BODY_SEG:
            raise SystemExit(f'expected p.11 body statement missing: {sid}')
    if statement_by_id[OLD_ID].get('qualifiers', {}).get('source_line_start') != 415:
        raise SystemExit('combined p.11 statement no longer anchors at L415')

    by_id = {r['statement_id']: r for r in statements}

    def source_claim(sid, marker, start, end, quote_phrase, subject, obj, predicate,
                     claim, layer, qualification, mentioned, body_id, *, relation=True,
                     extra=None):
        q = {
            'source_line_start': start,
            'source_line_end': end,
            'printed_page': 11,
            'pdf_physical_page': 10,
            'claim': claim,
            'speaker': f'Haskell footnote {marker}',
            'text_layer': layer,
            'qualification': qualification,
            'relation_candidate': relation,
            'mentioned_candidate_ids': list(dict.fromkeys(mentioned)),
            'footnote_marker': marker,
            'footnote_number': marker,
            'footnote_segment': NOTE_SEG,
            'footnote_refs': [{'marker': marker, 'segment_id': NOTE_SEG, 'source_line': start}],
            'related_segment': BODY_SEG,
            'related_body_statement_ids': [body_id],
            'linked_body_statement_ids': [body_id],
            'cited_material_not_independently_consulted': True,
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
        }
        if relation:
            q['relation_candidate_note'] = 'S2 relation candidate supported by the source note; no S6 formal edge is created.'
        if extra:
            q.update(extra)
        return {
            'statement_id': sid,
            'segment_id': NOTE_SEG,
            'subject_candidate_id': subject,
            'object_candidate_id': obj,
            'predicate': predicate,
            'qualifiers': q,
            'original_quote': excerpt(source_lines, start, end, quote_phrase),
            'origin': 'book',
            'source_file': '02-sources/02-Markdown/01_CHP-1.md',
        }

    additions = []
    additions.append(source_claim(
        new_ids[0], 1, 415, 415, 'Letter from the Savoy Resident in Rome, Onorato Gini, in 1666',
        'cand-2949', 'cand-3087', 'authored_by',
        'Haskell identifies the cited 1666 letter as a letter by Onorato Gini, the Savoy Resident in Rome.',
        'document-role claim',
        'Haskell quotes the letter through Claretta; the underlying letter and Claretta article were not independently consulted in this S2 pass.',
        ['cand-2949', 'cand-3087', 'cand-3508', 'cand-5985'], body_links[1],
        extra={'time': '1666', 'role': 'Savoy Resident in Rome'},
    ))
    additions.append(source_claim(
        new_ids[1], 1, 415, 418, 'ma prima patco apposto dal Cortona era ch’egli non voleva indursi a far ver una proposta [as regards subject], allegando chc non avevane fatta alcuna in tutta la vita e che “questo sarebbe un non mai volere il quadro”',
        'cand-2949', 'cand-3096', 'has_subject',
        'The passage quoted by Haskell through Claretta reports Cortona refusing to propose the subject himself, saying he had never proposed one in his life and that doing so would amount to never wanting the picture.',
        'reported letter content',
        'Secondary summary and quotation through Claretta, not an independently consulted original. Attribute the statement to Cortona within Gini’s letter; do not treat Cortona as the letter author. The printed p.11 reads “by”, “patto” and “che”; S0 OCR remains unchanged.',
        ['cand-2949', 'cand-3096', 'cand-3508', 'cand-5985'], body_links[1],
    ))
    additions.append(citation_row(
        new_ids[2], 1, 415, 416, 'summarised bv Claretta, 1885, p. 516',
        'cand-3508', 'cand-5985', 'Claretta, 1885, p. 516',
        'Haskell cites Claretta’s 1885 article, page 516, as the source summarizing the Gini letter and its quoted statement.',
        body_links[1],
        'The printed bibliography identifies Gaudenzio Claretta’s article and page range 511–554; p.516 is within that range. The article was not independently consulted.',
        ['cand-2962', 'cand-2949', 'cand-3087', 'cand-3508', 'cand-5985', 'cand-3096'],
    ))
    additions.append(citation_row(
        new_ids[3], 2, 419, 419, 'Pascoli, I, p. 84',
        'cand-1842', 'cand-4834', 'Pascoli, I, p. 84',
        'Haskell directs readers to Pascoli, volume I, page 84, for the preceding Rosa example about seeking friends’ suggestions.',
        body_links[2],
        'The printed bibliography identifies Lione Pascoli’s volume I; page 84 was not independently consulted.',
        ['cand-2962', 'cand-1842', 'cand-4834', 'cand-2236'],
    ))
    additions.append(citation_row(
        new_ids[4], 3, 420, 420, 'Costello, p. 278',
        'cand-3509', 'cand-7017', 'Costello, p. 278',
        'Haskell cites Costello, page 278, for the preceding Valentin commission.',
        body_links[3],
        'The printed bibliography identifies Jane Costello’s 1950 article on pages 237–284; page 278 falls in that range. The article and cited page were not independently consulted; keep the passage-specific person candidate separate pending S3 identity reconciliation.',
        ['cand-2962', 'cand-3509', 'cand-7017', 'cand-3446', 'cand-3447'],
    ))
    additions.append(citation_row(
        new_ids[5], 4, 421, 421, 'Friedlaender, p. 302',
        'cand-3506', 'cand-4375', 'Friedlaender, p. 302',
        'Haskell says the 1600 contract was published by Friedlaender and cites page 302.',
        body_links[4],
        'The printed bibliography identifies Walter Friedlaender’s Caravaggio Studies (1955); the book and cited page were not independently consulted.',
        ['cand-2962', 'cand-3506', 'cand-4375', 'cand-0544', 'cand-0546', 'cand-0550'],
        cited_document='cand-2941',
    ))
    additions.append(source_claim(
        new_ids[6], 5, 422, 422, 'See later, Chapter 3, p. 70, note 2.',
        None, None, 'internal_cross_reference',
        'Haskell points forward to chapter 3, page 70, note 2.',
        'internal navigation',
        'This is an internal cross-reference, not independent evidence for the Rubens example.',
        [], body_links[5], relation=False,
        extra={'cross_reference_chapter': 3, 'cross_reference_printed_page': 70, 'cross_reference_note': 2},
    ))
    additions.append(citation_row(
        new_ids[7], 6, 423, 423, 'Pollak, 1913, p. 26',
        'cand-3510', 'cand-4359', 'Pollak, 1913, p. 26',
        'Haskell cites Pollak’s 1913 publication, page 26, for the Lanfranco letter.',
        body_links[6],
        'The printed bibliography identifies O. Pollak’s 1913 publication. Haskell’s cited page and the original letter were not independently consulted; the S0 OCR prints note marker 8, while the page image confirms printed note 6.',
        ['cand-2962', 'cand-3510', 'cand-4359', 'cand-2953', 'cand-3053'],
        cited_document='cand-2953',
    ))
    additions.append(source_claim(
        new_ids[8], 6, 423, 423, 'Letter from Lanfranco in Naples dated 14 July 1640',
        'cand-2953', 'cand-3053', 'authored_by',
        'The note identifies the cited letter as written by Giovanni Lanfranco in Naples on 14 July 1640.',
        'document-role claim',
        'The S2 note itself does not name a recipient. The reused accepted archive unit identifies Francesco Barberini from a separate DBI source; that recipient is not attributed to this footnote.',
        ['cand-2953', 'cand-3053', 'cand-3534', 'cand-3510', 'cand-4359'], body_links[6],
        extra={'time': '1640-07-14', 'place_candidate_id': 'cand-3534'},
    ))
    additions.append(source_claim(
        new_ids[9], 6, 423, 424, '‘In tela il disegno’ must certainly mean that the general composition would be sketched in on the canvas.',
        None, None, 'haskell_interprets_canvas_drawing_phrase',
        'Haskell interprets “In tela il disegno” as meaning that the general composition would be sketched onto the canvas.',
        'authorial interpretation',
        'This is Haskell’s interpretation of the Italian phrase, not a direct statement by Lanfranco about a completed drawing. The underlying letter is cited through Pollak and was not independently consulted.',
        ['cand-2953', 'cand-3053', 'cand-3452', 'cand-3571'], body_links[6], relation=False,
    ))
    additions.append(citation_row(
        new_ids[10], 6, 425, 425, 'Costello, p. 274',
        'cand-3509', 'cand-7017', 'Costello, p. 274',
        'Haskell cites Costello, page 274, for the claim that canvas composition sketches were a regular practice of Lanfranco.',
        body_links[6],
        'The printed bibliography identifies Jane Costello’s 1950 article on pages 237–284; page 274 falls in that range. The article and cited page were not independently consulted; keep the passage-specific person candidate separate pending S3 identity reconciliation.',
        ['cand-2962', 'cand-3509', 'cand-7017', 'cand-3053', 'cand-3571'],
    ))
    additions.append(source_claim(
        new_ids[11], 6, 424, 425, 'We know that this was a regular practice of Lanfranco’s—Costello, p. 274.',
        'cand-3053', 'cand-3571', 'lanfranco_regular_canvas_composition_practice',
        'Haskell says that sketching the general composition on canvas was a regular practice of Lanfranco.',
        'source-mediated authorial claim',
        'Haskell supports this claim with Costello, page 274; the article and cited page were not independently consulted. Preserve this as Haskell’s reported generalization, not direct evidence from the letter.',
        ['cand-3053', 'cand-3571', 'cand-3509', 'cand-7017'], body_links[6], relation=False,
    ))

    # Replace the broad combined note while preserving the original surrounding order.
    rebuilt = []
    for row in statements:
        if row['statement_id'] == OLD_ID:
            rebuilt.extend(additions)
        else:
            rebuilt.append(row)

    # Reuse accepted KU candidate mappings for this p.11 body/note occurrence.
    mention_remaps = {
        'm-chp1-secii-0426': 'cand-3087',
        'm-chp1-secii-0444': 'cand-3096',
        'm-chp1-secii-0427': 'cand-3096',
        'm-chp1-secii-0428': 'cand-3053',
        'm-chp1-secii-0429': 'cand-3053',
        'm-chp1-secii-0572': 'cand-2953',
        'm-chp1-secii-0069': 'cand-3096',
        'm-chp1-secii-0070': 'cand-3096',
        'm-chp1-secii-0678': 'cand-3096',
        'm-chp1-secii-0083': 'cand-3053',
    }
    for mid, cid in mention_remaps.items():
        if mid not in mention_by_id:
            raise SystemExit(f'expected existing mention missing: {mid}')
        row = mention_by_id[mid]
        row['candidate_id'] = cid
        if mid == 'm-chp1-secii-0426': row['note'] = 'Onorato Gini; mapped to the existing accepted person KU.'
        if mid in {'m-chp1-secii-0444', 'm-chp1-secii-0427', 'm-chp1-secii-0069', 'm-chp1-secii-0070', 'm-chp1-secii-0678'}:
            row['note'] = 'Pietro da Cortona; mapped to the existing accepted person KU.'
        if mid in {'m-chp1-secii-0428', 'm-chp1-secii-0429', 'm-chp1-secii-0083'}:
            row['note'] = 'Giovanni Lanfranco; mapped to the existing accepted person KU.'
        if mid == 'm-chp1-secii-0572':
            row['note'] = 'The dated Lanfranco letter; mapped to the existing accepted archive KU, whose recipient is established separately from DBI.'

    new_mentions = [
        ('m-chp1-secii-p11-n1-gini-letter', 'cand-2949', 'Letter from the Savoy Resident in Rome', 'The accepted Gini letter referred to in Haskell footnote 1.'),
        ('m-chp1-secii-p11-n1-claretta-p516', 'cand-5985', 'Claretta, 1885', 'Citation locator for the 1885 Claretta article, page 516; the article was not independently consulted.'),
        ('m-chp1-secii-p11-n2-pascoli-vol1-p84', 'cand-4834', 'Pascoli, I, p. 84', 'Exact cited volume/page locator; page 84 was not independently consulted.'),
        ('m-chp1-secii-p11-n3-costello-p278', 'cand-7017', 'Costello, p. 278', 'Exact locator within the Jane Costello 1950 article; article and page were not independently consulted.'),
        ('m-chp1-secii-p11-n4-friedlaender-p302', 'cand-4375', 'Friedlaender, p. 302', 'Exact locator within Caravaggio Studies; book and page were not independently consulted.'),
        ('m-chp1-secii-p11-n6-pollak-p26', 'cand-4359', 'Pollak, 1913, p. 26', 'Exact locator in the Pollak 1913 publication; cited page was not independently consulted.'),
        ('m-chp1-secii-p11-n6-costello-p274', 'cand-7017', 'Costello, p. 274', 'Exact locator within the Jane Costello 1950 article; article and page were not independently consulted.'),
    ]
    for mid, cid, phrase, note in new_mentions:
        if mid in mention_by_id:
            raise SystemExit(f'new mention ID already exists: {mid}')
        start, end, surface = normalized_span(segment_text, phrase)
        mentions.append({
            'mention_id': mid,
            'segment_id': NOTE_SEG,
            'candidate_id': cid,
            'surface_form': surface,
            'start_char': str(start),
            'end_char': str(end),
            'note': note,
        })

    # Add reciprocal p.11 footnote pointers to the already classified body claims.
    marker_lines = {1: 386, 2: 388, 3: 392, 4: 400, 5: 404, 6: 412}
    statements_after = {row['statement_id']: row for row in rebuilt}
    footnote_ids = {
        1: [new_ids[0], new_ids[1], new_ids[2]],
        2: [new_ids[3]],
        3: [new_ids[4]],
        4: [new_ids[5]],
        5: [new_ids[6]],
        6: [new_ids[7], new_ids[8], new_ids[9], new_ids[10], new_ids[11]],
    }
    markers_by_body = {}
    for marker, body_id in body_links.items():
        markers_by_body.setdefault(body_id, []).append(marker)
    for body_id, markers in markers_by_body.items():
        q = statements_after[body_id].setdefault('qualifiers', {})
        q['footnote_marker'] = markers[0]
        q['footnote_number'] = markers[0]
        q['footnote_markers'] = markers
        refs = q.setdefault('footnote_refs', [])
        for marker in markers:
            ref = {'marker': marker, 'segment_id': NOTE_SEG, 'source_line': marker_lines[marker]}
            if ref not in refs:
                refs.append(ref)
        linked = q.setdefault('footnote_statement_ids', [])
        for marker in markers:
            for sid in footnote_ids[marker]:
                if sid not in linked:
                    linked.append(sid)
        q['footnote_text_pending'] = False
        q['footnote_link_status'] = 'linked'

    # Keep candidate notes current without changing candidate status or identity decisions.
    detail_additions = {
        'cand-4834': ' Haskell also cites vol. I, p.84 in p.11 note 2; p.84 was not independently consulted.',
        'cand-7017': ' Haskell also cites pp.274 and 278 in p.11 notes 3 and 6; those pages and the article were not independently consulted.',
        'cand-4375': ' Haskell also cites p.302 in p.11 note 4; the cited page was not independently consulted.',
        'cand-4359': ' Haskell also cites p.26 in p.11 note 6; the cited page was not independently consulted.',
    }
    for cid, suffix in detail_additions.items():
        detail = candidate_by_id[cid].get('detail', '')
        if suffix.strip() not in detail:
            candidate_by_id[cid]['detail'] = detail + suffix
    candidate_by_id['cand-3508']['canonical_name'] = 'Gaudenzio Claretta'
    candidate_by_id['cand-3506']['canonical_name'] = 'Walter Friedlaender'
    candidate_by_id['cand-3508']['detail'] = 'The printed bibliography identifies the author of the p.11 note 1 source as Gaudenzio Claretta. The article was not independently consulted; no separate biographical authority was checked.'
    candidate_by_id['cand-3506']['detail'] = 'The printed bibliography identifies Walter Friedlaender as author of Caravaggio Studies, cited in chapter 1 notes. The book and cited pages were not independently consulted; S3 identity alignment remains pending.'
    candidate_by_id['cand-5985']['canonical_name'] = 'Gaudenzio Claretta, “Relazioni d’insigni artisti e virtuosi in Roma col Duca Carlo Emanuele II di Savoia” (1885)'
    candidate_by_id['cand-5985']['detail'] = 'Haskell cites this article at p.516 in chapter 1 note 1 and p.550 in chapter 4 note 6. The printed bibliography p.419 identifies the article and its pp.511–554 range; the article was not independently consulted.'
    candidate_by_id['cand-4375']['detail'] = 'Printed bibliography p.423 identifies Walter Friedlaender, Caravaggio Studies (Princeton, 1955); Haskell cites pp.105 and 302. The book and cited pages were not independently consulted; bibliographic identification does not verify their contents.'

    # Keep the coverage row complete and append only the newly checked p.11 details.
    cov = next((r for r in coverage if r.get('segment_id') == NOTE_SEG), None)
    if cov is None:
        raise SystemExit('p.11 note segment coverage row missing')
    addition = (' Printed p.11 (PDF physical p.10) notes 1–6 were checked against the page image. '
                'Note 6 is numbered 6 in print although S0 OCR shows 8; S0 remains unchanged. '
                'Notes 1–6 were split into atomic letter-content, citation, and internal-reference claims; '
                'Gini, Cortona, Lanfranco and the Lanfranco letter reuse accepted candidates. '
                'Claretta, Pascoli, Costello, Friedlaender and Pollak publication locators were recorded; '
                'cited pages and publications were not independently consulted. The p.11 body-note links '
                'are reciprocal. Printed readings “summarised by”, “patto”, and “che” are noted in S2 only.')
    if addition.strip() not in cov.get('note', ''):
        cov['note'] = cov.get('note', '') + addition

    # Update the already processed p.11 body claims to accepted person identities.
    for sid in ['st-chp1-secii-l48-60-01', 'st-chp1-secii-l48-60-07']:
        q = statements_after[sid].setdefault('qualifiers', {})
        ids = q.get('mentioned_candidate_ids', [])
        q['mentioned_candidate_ids'] = list(dict.fromkeys('cand-3096' if x == 'cand-0342' else x for x in ids))
    body06 = statements_after['st-chp1-secii-l48-60-06']
    body06['subject_candidate_id'] = 'cand-3053'
    q = body06.setdefault('qualifiers', {})
    q['mentioned_candidate_ids'] = list(dict.fromkeys('cand-3053' if x == 'cand-1359' else x for x in q.get('mentioned_candidate_ids', [])))

    print(f'planned: replace 1 combined p.11 statement with {len(additions)} atomic statements')
    print(f'planned: reuse/remap {len(mention_remaps)} exact mentions; add {len(new_mentions)} publication/letter mentions')
    print('planned: add reciprocal footnote metadata to 5 p.11 body statements; no candidates or KUs added')
    print(f'planned coverage disposition/status remains {cov["disposition"]}/{cov["migration_status"]}')
    if not args.apply:
        print('preview only; no files written. Use --apply after inspecting this plan.')
        return

    for name in EXPECTED:
        original = TABLES / name
        backup = original.with_name(original.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f'backup already exists; refusing to overwrite: {backup.name}')
        shutil.copy2(original, backup)
    write_jsonl(TABLES / 'book-statements.jsonl', rebuilt)
    write_csv(TABLES / 'entity-candidates.csv', candidates)
    write_csv(TABLES / 'mentions.csv', mentions)
    write_csv(TABLES / 's2-coverage.csv', coverage)
    print('applied; four pre-write recovery copies created with suffix ' + BACKUP_SUFFIX)
    for name in EXPECTED:
        print(name, digest(TABLES / name))


if __name__ == '__main__':
    main()
