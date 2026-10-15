from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / '04-knowledge' / 'tables' / 'book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge' / 'tables' / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
SOURCE_BOOK_ID = 'cand-2962'
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l160-168'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
EXPECTED_HASHES = {
    STATEMENTS.name: '3e62b8662050d50dc808b47690ebe1fa74fbede79b642e5acbea9c40efc039cf',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p183-notes-20261013')

CITATIONS = {
    'st-chp7-p183-n2-cite-daumale': {
        'publication_id': 'cand-6807', 'locator': 'd’Aumale, Histoire des princes de Condé, p. 8',
        'marker': 2, 'line': 168, 'segment': BODY_SEGMENT,
        'body_ids': ['st-chp7-p183-i02', 'st-chp7-p183-i20'],
        'ocr_corrections': [{'source_line': 168, 'source_form': 'exact-date', 'print_form': 'exact date'}],
    },
    'st-chp7-p183-n2-cite-callari': {
        'publication_id': 'cand-4845', 'locator': 'Callari, p. 298',
        'marker': 2, 'line': 168, 'segment': BODY_SEGMENT,
        'body_ids': ['st-chp7-p183-i02', 'st-chp7-p183-i20'],
        'ocr_corrections': [{'source_line': 168, 'source_form': 'exact-date', 'print_form': 'exact date'}],
    },
    'st-chp7-p183-n1-cite-passeri': {
        'publication_id': 'cand-4376', 'locator': 'Passeri, p. 210',
        'marker': 1, 'line': 348, 'segment': NOTE_SEGMENT,
        'body_ids': ['st-chp7-p182-i24', 'st-chp7-p183-q01'],
    },
    'st-chp7-p183-n3-cite-avviso': {
        'publication_id': 'cand-7079', 'locator': 'avviso published in Roma (1938), p. 477',
        'marker': 3, 'line': 350, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i08'],
        'ocr_corrections': [{'source_line': 350, 'ocr': '19 3 8', 'print_reading': '1938', 'basis': 'CHP-7.pdf physical page 17'}],
    },
    'st-chp7-p183-n3-cite-benedetti': {
        'publication_id': 'cand-7081', 'locator': 'Elpidio Benedetti, funeral publication on Mazarin (1661), p. 5',
        'marker': 3, 'line': 350, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i08'],
    },
    'st-chp7-p183-n3-cite-epistolario': {
        'publication_id': 'cand-7082', 'locator': 'Mazarin, Epistolario inedito, p. 119 (letter to Maccarani, 3 June 1650)',
        'marker': 3, 'line': 350, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i08'],
        'related_statement_ids': ['st-chp7-p183-n3-letter-1650-to-maccarani'],
    },
    'st-chp7-p183-n3-cite-lettres': {
        'publication_id': 'cand-7083', 'locator': 'Mazarin, Lettres pendant son ministère, vol. IX, p. 693 (letter to Maccarani, 6 March 1661)',
        'marker': 3, 'line': 350, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i11'],
        'ocr_corrections': [{'source_line': 350, 'ocr': 'fletter osò March 1661', 'print_reading': 'letter of 6 March 1661', 'basis': 'CHP-7.pdf physical page 17'}],
    },
    'st-chp7-p183-n3-cite-spon-wheler': {
        'publication_id': 'cand-6395', 'locator': 'Spon and Wheler, vol. I, p. 236',
        'marker': 3, 'line': 350, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i08'],
        'related_statement_ids': ['st-chp7-p183-n3-maccarani-gallery-1675'],
        'ocr_corrections': [{'source_line': 350, 'ocr': 'Span', 'print_reading': 'Spon', 'basis': 'CHP-7.pdf physical page 17'}],
    },
    'st-chp7-p183-n4-cite-prunieres': {
        'publication_id': 'cand-4861', 'locator': 'Prunières, L’opéra italien en France avant Lulli (1913), p. 149',
        'marker': 4, 'line': 351, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i16'],
    },
    'st-chp7-p183-n5-cite-baldinucci': {
        'publication_id': 'cand-4846', 'locator': 'Baldinucci, Notizie, vol. VI (1728), p. 245',
        'marker': 5, 'line': 352, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i17'],
    },
    'st-chp7-p183-n6-cite-pascoli': {
        'publication_id': 'cand-4834', 'locator': 'Pascoli, Vite, vol. I, p. 47',
        'marker': 6, 'line': 353, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p183-i18'],
        'ocr_corrections': [{'source_line': 353, 'ocr': '8 Pascoli', 'print_reading': '6 Pascoli', 'basis': 'CHP-7.pdf physical page 17'}],
    },
}

CLAIMS = {
    'st-chp7-p183-n2-lante-transfer-chain': {
        'subject': 'cand-4659', 'predicate': 'lante_family_acquired_palace_from_bentivoglio', 'object': 'cand-6796',
        'marker': 2, 'line': 349, 'body_ids': ['st-chp7-p183-i02', 'st-chp7-p183-i20'],
        'note': 'This preserves Haskell’s reported transfer chain: the Lante family had acquired the palace from the Bentivoglio before Mazarin bought it; the dates remain qualified.',
    },
    'st-chp7-p183-n3-facade-inscription': {
        'subject': 'cand-6797', 'predicate': 'facade_inscription_reports_jubilee_1650_and_mazarin', 'object': 'cand-1588',
        'marker': 3, 'line': 350, 'body_ids': ['st-chp7-p183-i08'],
        'note': 'This records Haskell’s transcription/report of the façade inscription naming Mazarin and invoking the 1650 Jubilee; the inscription was not independently examined.',
    },
    'st-chp7-p183-n3-maccarani-gallery-1675': {
        'subject': 'cand-1463', 'predicate': 'reported_owned_gallery_in_1675', 'object': 'cand-7085',
        'marker': 3, 'line': 350, 'body_ids': ['st-chp7-p183-i08'],
        'note': 'This records Haskell’s report that Maccarani owned a gallery of statues and paintings in 1675; Spon and Wheler are the cited locator, not independently consulted evidence.',
    },
}
ALREADY_CLASSIFIED_CLAIM = 'st-chp7-p183-n3-letter-1650-to-maccarani'

SOURCE_GUARDS = {
    168: 'The exact-date of the transaction is not certain, but it must have been before 1647',
    348: '1 Passeri, p. 210.',
    349: '2 Mazarin bought the palace from the Lante family which had acquired it from the Bentivoglio.',
    350: '3 In 1646',
    351: '4 Prunières, 1913, p. 149.',
    352: '5 Baldinucci, VI, 1728. p. 245.',
    353: '8 Pascoli, I, p. 47.',
}
BODY_EXPECTED_LINKS = {
    'st-chp7-p183-i02': {'st-chp7-p183-n2-cite-daumale', 'st-chp7-p183-n2-cite-callari', 'st-chp7-p183-n2-lante-transfer-chain'},
    'st-chp7-p183-i20': {'st-chp7-p183-n2-cite-daumale', 'st-chp7-p183-n2-cite-callari', 'st-chp7-p183-n2-lante-transfer-chain'},
    'st-chp7-p182-i24': {'st-chp7-p183-n1-cite-passeri'},
    'st-chp7-p183-q01': {'st-chp7-p183-n1-cite-passeri'},
    'st-chp7-p183-i08': {
        'st-chp7-p183-n3-cite-avviso', 'st-chp7-p183-n3-cite-benedetti',
        'st-chp7-p183-n3-cite-epistolario', ALREADY_CLASSIFIED_CLAIM,
        'st-chp7-p183-n3-facade-inscription', 'st-chp7-p183-n3-cite-spon-wheler',
        'st-chp7-p183-n3-maccarani-gallery-1675',
    },
    'st-chp7-p183-i11': {'st-chp7-p183-n3-cite-lettres'},
    'st-chp7-p183-i16': {'st-chp7-p183-n4-cite-prunieres'},
    'st-chp7-p183-i17': {'st-chp7-p183-n5-cite-baldinucci'},
    'st-chp7-p183-i18': {'st-chp7-p183-n6-cite-pascoli'},
}
CURRENT_BODY_LINKS = {
    **{key: value for key, value in BODY_EXPECTED_LINKS.items() if key != 'st-chp7-p183-i08'},
    'st-chp7-p183-i08': {
        'st-chp7-p183-n3-cite-avviso', 'st-chp7-p183-n3-cite-benedetti',
        'st-chp7-p183-n3-cite-epistolario', ALREADY_CLASSIFIED_CLAIM,
        'st-chp7-p183-n3-facade-inscription',
    },
}
LINES = {
    'st-chp7-p183-n2-cite-daumale': (2, 168, BODY_SEGMENT),
    'st-chp7-p183-n2-cite-callari': (2, 168, BODY_SEGMENT),
    **{key: (spec['marker'], spec['line'], spec['segment']) for key, spec in CITATIONS.items() if key not in {'st-chp7-p183-n2-cite-daumale', 'st-chp7-p183-n2-cite-callari'}},
    **{key: (spec['marker'], spec['line'], NOTE_SEGMENT) for key, spec in CLAIMS.items()},
    ALREADY_CLASSIFIED_CLAIM: (3, 350, NOTE_SEGMENT),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = {path: path.read_bytes() for path in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {path.name: sha256(content) for path, content in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    for line_no, snippet in SOURCE_GUARDS.items():
        if snippet not in source_lines[line_no - 1]:
            raise SystemExit(f'source guard failed at L{line_no}: {source_lines[line_no - 1]}')
    candidates = {
        row['candidate_id']: row for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))
    }
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source-book candidate is absent or not archive typed')
    for spec in CITATIONS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive missing or mistyped: {spec['publication_id']}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_note_ids = set(CITATIONS) | set(CLAIMS) | {ALREADY_CLASSIFIED_CLAIM}
    if not expected_note_ids.issubset(by_id):
        raise SystemExit(f'missing p.183 note statements: {sorted(expected_note_ids - set(by_id))}')
    for note_id, spec in CITATIONS.items():
        row = by_id[note_id]
        q = row.get('qualifiers') or {}
        expected_status = False if note_id in {'st-chp7-p183-n2-cite-daumale', 'st-chp7-p183-n2-cite-callari'} else None
        if (row.get('object_candidate_id') != spec['publication_id'] or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not expected_status):
            raise SystemExit(f'citation row changed since review: {note_id}')
    for note_id, spec in CLAIMS.items():
        row = by_id[note_id]
        q = row.get('qualifiers') or {}
        if (row.get('subject_candidate_id') != spec['subject'] or row.get('predicate') != spec['predicate']
                or row.get('object_candidate_id') != spec['object'] or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'note fact changed since review: {note_id}')
    letter = by_id[ALREADY_CLASSIFIED_CLAIM]
    if (letter.get('qualifiers', {}).get('relation_candidate') is not True
            or letter.get('predicate') != 'letter_addressed_to'):
        raise SystemExit('already classified 1650 letter statement changed')
    for body_id, expected in CURRENT_BODY_LINKS.items():
        if body_id not in by_id:
            raise SystemExit(f'missing linked body statement: {body_id}')
        actual = set((by_id[body_id].get('qualifiers') or {}).get('footnote_statement_ids') or [])
        if actual != expected:
            raise SystemExit(f'body links changed at {body_id}: {sorted(actual)}')
    for note_id, spec in CITATIONS.items():
        for body_id in spec['body_ids']:
            if body_id not in by_id:
                raise SystemExit(f'missing source body target: {body_id}')
    for note_id, spec in CLAIMS.items():
        for body_id in spec['body_ids']:
            if body_id not in by_id:
                raise SystemExit(f'missing source body target: {body_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        note_id = row['statement_id']
        citation_spec = CITATIONS.get(note_id)
        claim_spec = CLAIMS.get(note_id)
        if citation_spec:
            pub_id = citation_spec['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': pub_id, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[pub_id]['canonical_name']} at {citation_spec['locator']} in footnote {citation_spec['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': pub_id, 'citation_locator': citation_spec['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': pub_id, 'locator': citation_spec['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': citation_spec['marker'], 'footnote_number': citation_spec['marker'],
                'footnote_segment': citation_spec['segment'],
                'footnote_refs': [{'marker': citation_spec['marker'], 'segment_id': citation_spec['segment'],
                                   'source_line': citation_spec['line'], 'statement_ids': citation_spec['body_ids']}],
                'related_body_statement_ids': citation_spec['body_ids'],
                'linked_body_statement_ids': citation_spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; cited material was not independently consulted, and no S6 edge is created.',
            })
            related = citation_spec.get('related_statement_ids')
            if related:
                q['related_statement_ids'] = related
            if citation_spec.get('ocr_corrections'):
                q['ocr_corrections'] = citation_spec['ocr_corrections']
            row['qualifiers'] = q
        elif claim_spec or note_id == ALREADY_CLASSIFIED_CLAIM:
            spec = claim_spec or {'marker': 3, 'line': 350, 'body_ids': ['st-chp7-p183-i08']}
            q = dict(row.get('qualifiers') or {})
            if claim_spec:
                q['relation_candidate'] = True
                q['relation_candidate_note'] = claim_spec['note']
            q.update({
                'footnote_marker': spec['marker'], 'footnote_number': spec['marker'],
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': NOTE_SEGMENT,
                                   'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
                'related_body_statement_ids': spec['body_ids'],
                'linked_body_statement_ids': spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
            })
            if claim_spec and claim_spec.get('open_endpoint_reason'):
                q['open_endpoint_reason'] = claim_spec['open_endpoint_reason']
            row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    body_notes: dict[str, list[str]] = {}
    body_refs: dict[str, list[tuple[int, int, str]]] = {}
    for note_id, (marker, line, segment) in LINES.items():
        for body_id in by_out[note_id].get('qualifiers', {}).get('linked_body_statement_ids', []):
            body_notes.setdefault(body_id, []).append(note_id)
            body_refs.setdefault(body_id, []).append((marker, line, segment))
    for body_id, note_ids in body_notes.items():
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = [dict(ref) for ref in q.get('footnote_refs') or []]
        for marker, line, segment in body_refs[body_id]:
            ref = next((item for item in refs if item.get('marker') == marker and item.get('source_line') == line and item.get('segment_id') == segment), None)
            if ref is None:
                ref = {'marker': marker, 'segment_id': segment, 'source_line': line}
                refs.append(ref)
            ref['statement_ids'] = [nid for nid in note_ids if LINES[nid][0:3] == (marker, line, segment)]
        q['footnote_refs'] = refs
        q['footnote_statement_ids'] = list(dict.fromkeys(note_ids))
        q['footnote_link_status'] = 'linked'
        q['footnote_text_pending'] = False
        unique_body_refs = list(dict.fromkeys(body_refs[body_id]))
        if len(unique_body_refs) == 1:
            q['footnote_marker'], q['footnote_number'], q['footnote_segment'] = unique_body_refs[0][0], unique_body_refs[0][0], unique_body_refs[0][2]
        else:
            q.pop('footnote_marker', None)
            q.pop('footnote_number', None)
            q.pop('footnote_segment', None)
        row['qualifiers'] = q

    output_bytes = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8507, False: 3418, 'unset': 2262}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(CITATIONS), 'classified_note_claims': len(CLAIMS),
        'linked_already_classified_claims': 1, 'reciprocal_body_links': len(body_notes),
        'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
        'before_sha256': hashes, 'after_statement_sha256': sha256(output_bytes),
        'backup': str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    if STATEMENTS.read_bytes() != raw[STATEMENTS]:
        raise SystemExit('statement table changed after dry-run preparation')
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, output_bytes)
    if sha256(STATEMENTS.read_bytes()) != report['after_statement_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
