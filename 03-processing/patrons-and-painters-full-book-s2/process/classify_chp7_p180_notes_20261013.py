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
TABLES = ROOT / '04-knowledge' / 'tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l128-138'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: '15f298cac19cacf5edd558dc9989d8fc6905ca5fae30898062491a689e08a390',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p180-notes-20261013')

CITATIONS = {
    'st-chp7-p180-n1-cite-prunieres': {
        'publication_id': 'cand-4861', 'locator': 'Prunières, L’opéra italien en France avant Lulli (1913), p. 41',
        'marker': 1, 'line': 335, 'body_ids': ['st-chp7-p180-i22'],
        'ocr_corrections': [{'source_line': 335, 'ocr': 'Prunidres', 'print_reading': 'Prunières', 'basis': 'CHP-7.pdf physical page 14'}],
    },
    'st-chp7-p180-n2-cite-brienne': {
        'publication_id': 'cand-7071', 'locator': 'Brienne, Mémoires, vol. I (1916–1919), p. 315',
        'marker': 2, 'line': 336, 'body_ids': ['st-chp7-p180-i27'],
    },
    'st-chp7-p180-n3-cite-mahon': {
        'publication_id': 'cand-7070', 'locator': 'Mahon, “Mazarin and Poussin” (1960), pp. 352–354',
        'marker': 3, 'line': 337, 'body_ids': ['st-chp7-p180-i30', 'st-chp7-p180-i34'],
        'ocr_corrections': [{'source_line': 337, 'ocr': 'i960', 'print_reading': '1960', 'basis': 'CHP-7.pdf physical page 14'}],
    },
    'st-chp7-p180-n4-cite-poussin-catalog': {
        'publication_id': 'cand-4633', 'locator': 'Nicolas Poussin exhibition catalog (1960), pp. 46 and 65',
        'marker': 4, 'line': 338, 'body_ids': ['st-chp7-p180-i34'],
    },
}

FOOTNOTE_CLAIMS = {
    'st-chp7-p180-n3-commission-before-1632': {
        'relation_candidate': True,
        'note': 'This records Haskell’s qualified chronology assessment of Mazarin’s commissioning activity; it does not establish that no earlier commission occurred.',
        'marker': 3, 'line': 337, 'body_ids': ['st-chp7-p180-i30', 'st-chp7-p180-i34'],
        'open_endpoint_reason': 'The note names no particular work or commission for this general assessment; the specific purchase-date report about two Poussin paintings is recorded separately.',
        'ocr_correction': {'source_line': 337, 'ocr': 'i960', 'print_reading': '1960', 'basis': 'CHP-7.pdf physical page 14'},
    },
    'st-chp7-p180-n3-mahon-purchase-date': {
        'relation_candidate': True,
        'note': 'This records Haskell’s report of Mahon’s suggested date for Mazarin’s purchase of a pair of Poussin paintings; it is a source-attributed chronology, not an independently verified purchase.',
        'marker': 3, 'line': 337, 'body_ids': ['st-chp7-p180-i30', 'st-chp7-p180-i34'],
        'open_endpoint_reason': 'Haskell’s note says “the two Poussins” and likely refers to the two works named in p.180 L138; retain the pair-level reference without asserting a separate purchase event for each individual work.',
        'cited_material_not_independently_consulted': True,
        'ocr_correction': {'source_line': 337, 'ocr': 'i960', 'print_reading': '1960', 'basis': 'CHP-7.pdf physical page 14'},
    },
}

NOTE4_FACTS = {
    'st-chp7-p180-n4-pair-location': False,
    'st-chp7-p180-n4-inspiration-louvre-location': True,
    'st-chp7-p180-n4-diana-detroit-location': True,
}

SOURCE_GUARDS = {
    335: ('1 Prunidres, 1913, p. 41.',),
    336: ('2 Brienne, I, p. 315.',),
    337: ('3 It is most unlikely that Mazarin could have commissioned anything serious before 1632', 'Mahon (i960, pp. 352-4)'),
    338: ('4 In the Louvre and Institute of Arts, Detroit—see Nicolas Poussin, pp. 46 and 65.',),
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
    raw = {
        STATEMENTS: STATEMENTS.read_bytes(),
        CANDIDATES: CANDIDATES.read_bytes(),
        SOURCE: SOURCE.read_bytes(),
        PDF: PDF.read_bytes(),
    }
    hashes = {path.name: sha256(content) for path, content in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')

    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    for line_no, snippets in SOURCE_GUARDS.items():
        source_line = source_lines[line_no - 1]
        if any(snippet not in source_line for snippet in snippets):
            raise SystemExit(f'source guard failed at L{line_no}: {source_line}')

    candidates = {
        row['candidate_id']: row
        for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))
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
    body_to_notes: dict[str, list[str]] = {}
    body_refs: dict[str, list[tuple[int, int]]] = {}
    for note_id, spec in CITATIONS.items():
        for body_id in spec['body_ids']:
            body_to_notes.setdefault(body_id, []).append(note_id)
            body_refs.setdefault(body_id, []).append((spec['marker'], spec['line']))
    for note_id, spec in FOOTNOTE_CLAIMS.items():
        for body_id in spec['body_ids']:
            body_to_notes.setdefault(body_id, []).append(note_id)
            body_refs.setdefault(body_id, []).append((spec['marker'], spec['line']))
    for note_id in NOTE4_FACTS:
        body_id = 'st-chp7-p180-i34'
        body_to_notes.setdefault(body_id, []).append(note_id)
        body_refs.setdefault(body_id, []).append((4, 338))

    required = set(CITATIONS) | set(FOOTNOTE_CLAIMS) | set(NOTE4_FACTS) | set(body_to_notes)
    if not required.issubset(by_id):
        raise SystemExit(f'missing note/body statement: {sorted(required - set(by_id))}')
    unset_targets = {
        row['statement_id'] for row in rows
        if row.get('segment_id') == NOTE_SEGMENT
        and 335 <= (row.get('qualifiers') or {}).get('source_line_start', 0) <= 338
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if unset_targets != set(CITATIONS) | set(FOOTNOTE_CLAIMS):
        raise SystemExit(f'p.180 unset target set changed: {sorted(unset_targets ^ (set(CITATIONS) | set(FOOTNOTE_CLAIMS)))}')
    for note_id, spec in CITATIONS.items():
        row = by_id[note_id]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation changed since review: {note_id}')
    for note_id, spec in FOOTNOTE_CLAIMS.items():
        row = by_id[note_id]
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('qualifiers', {}).get('source_line_start') != 337
                or row.get('qualifiers', {}).get('relation_candidate') is not None):
            raise SystemExit(f'footnote claim changed since review: {note_id}')
    for note_id, expected_status in NOTE4_FACTS.items():
        if by_id[note_id].get('qualifiers', {}).get('relation_candidate') is not expected_status:
            raise SystemExit(f'p.180 note 4 classification changed: {note_id}')
    for body_id in body_to_notes:
        q = by_id[body_id].get('qualifiers') or {}
        expected_lines = {line_no for _, line_no in body_refs[body_id]}
        if q.get('source_line_start') is None or not expected_lines:
            raise SystemExit(f'p.180 body anchor missing: {body_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        citation_spec = CITATIONS.get(row['statement_id'])
        fact_spec = FOOTNOTE_CLAIMS.get(row['statement_id'])
        if citation_spec is not None:
            publication_id = citation_spec['publication_id']
            marker, line_no = citation_spec['marker'], citation_spec['line']
            body_ids = citation_spec['body_ids']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            row.update({
                'subject_candidate_id': SOURCE_BOOK_ID,
                'object_candidate_id': publication_id,
                'predicate': 'cites',
            })
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {citation_spec['locator']} in footnote {marker}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id,
                'citation_locator': citation_spec['locator'],
                'citations': [{
                    'source_candidate_id': SOURCE_BOOK_ID,
                    'publication_candidate_id': publication_id,
                    'locator': citation_spec['locator'],
                }],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': marker,
                'footnote_number': marker,
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': marker,
                    'segment_id': NOTE_SEGMENT,
                    'source_line': line_no,
                    'statement_ids': body_ids,
                }],
                'related_body_statement_ids': body_ids,
                'linked_body_statement_ids': body_ids,
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': (
                    'S2 citation candidate: the printed footnote identifies this source and locator. '
                    'This records Haskell’s bibliographic reference only; the cited material was not '
                    'independently consulted and no S6 edge is created.'
                ),
            })
            if citation_spec.get('ocr_corrections'):
                q['ocr_corrections'] = citation_spec['ocr_corrections']
            row['qualifiers'] = q
        elif fact_spec is not None:
            q = dict(row.get('qualifiers') or {})
            q.update({
                'relation_candidate': fact_spec['relation_candidate'],
                'relation_candidate_note': fact_spec['note'],
                'footnote_marker': fact_spec['marker'],
                'footnote_number': fact_spec['marker'],
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': fact_spec['marker'],
                    'segment_id': NOTE_SEGMENT,
                    'source_line': fact_spec['line'],
                    'statement_ids': fact_spec['body_ids'],
                }],
                'related_body_statement_ids': fact_spec['body_ids'],
                'linked_body_statement_ids': fact_spec['body_ids'],
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
            })
            if fact_spec.get('open_endpoint_reason'):
                q['open_endpoint_reason'] = fact_spec['open_endpoint_reason']
            if fact_spec.get('cited_material_not_independently_consulted'):
                q['cited_material_not_independently_consulted'] = True
            if fact_spec.get('ocr_correction'):
                q['ocr_corrections'] = [fact_spec['ocr_correction']]
            row['qualifiers'] = q
        elif row['statement_id'] in NOTE4_FACTS:
            q = dict(row.get('qualifiers') or {})
            marker, line_no, body_id = 4, 338, 'st-chp7-p180-i34'
            q.update({
                'footnote_marker': marker,
                'footnote_number': marker,
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': marker,
                    'segment_id': NOTE_SEGMENT,
                    'source_line': line_no,
                    'statement_ids': [body_id],
                }],
                'related_body_statement_ids': [body_id],
                'linked_body_statement_ids': [body_id],
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
            })
            row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for body_id, note_ids in body_to_notes.items():
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = [dict(ref) for ref in (q.get('footnote_refs') or [])]
        for marker, line_no in body_refs[body_id]:
            ref = next((item for item in refs if item.get('marker') == marker
                        and item.get('segment_id') == NOTE_SEGMENT and item.get('source_line') == line_no), None)
            if ref is None:
                ref = {
                    'marker': marker,
                    'segment_id': NOTE_SEGMENT,
                    'source_line': line_no,
                    'citation_segment_id': BODY_SEGMENT,
                    'citation_source_line': q.get('source_line_start'),
                }
                refs.append(ref)
            marker_note_ids = [note_id for note_id in note_ids
                               if (CITATIONS.get(note_id) or FOOTNOTE_CLAIMS.get(note_id) or {}).get('marker') == marker
                               or note_id in NOTE4_FACTS and marker == 4]
            ref['statement_ids'] = marker_note_ids
        q['footnote_refs'] = refs
        q['footnote_statement_ids'] = note_ids
        q['footnote_link_status'] = 'linked'
        q['footnote_text_pending'] = False
        if len(body_refs[body_id]) == 1:
            marker = body_refs[body_id][0][0]
            q['footnote_marker'] = marker
            q['footnote_number'] = marker
            q['footnote_segment'] = NOTE_SEGMENT
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
    if (len(output), counts) != (14187, {True: 8476, False: 3420, 'unset': 2291}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(CITATIONS),
        'classified_footnote_claims': len(FOOTNOTE_CLAIMS),
        'note4_location_statements_linked': len(NOTE4_FACTS),
        'linked_body_statements': len(body_to_notes),
        'post_counts': {'statements': len(output), **{str(key): value for key, value in counts.items()}},
        'before_sha256': hashes,
        'after_statement_sha256': sha256(output_bytes),
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
