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
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l76-89'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: '0608ebce6cb9235a22e0829313fa6fe9f672d67aa348b78e313ac67d6fb50908',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p176-notes-20261013')

TARGETS = {
    'st-chp7-p176-n1-cite-mazarin': {
        'publication_id': 'cand-7044', 'locator': 'Mazarin exhibition catalogue (Paris, 1961)',
        'marker': 1, 'line': 314, 'body_ids': ['st-chp7-p176-i01', 'st-chp7-p176-i02'],
    },
    'st-chp7-p176-n2-cite-correspondance': {
        'publication_id': 'cand-4634', 'locator': 'Poussin, Correspondance, p. 15',
        'marker': 2, 'line': 314, 'body_ids': ['st-chp7-p176-i06', 'st-chp7-p176-i07', 'st-chp7-p176-i08'],
    },
    'st-chp7-p176-n3-cite-correspondance': {
        'publication_id': 'cand-4634', 'locator': 'Poussin, Correspondance, p. 31, n. 2',
        'marker': 3, 'line': 315, 'body_ids': ['st-chp7-p176-i15'],
    },
    'st-chp7-p176-n4-cite-correspondance': {
        'publication_id': 'cand-4634', 'locator': 'Poussin, Correspondance, pp. 36–37',
        'marker': 4, 'line': 315, 'body_ids': ['st-chp7-p176-i16'],
    },
    'st-chp7-p176-n4-cite-briganti': {
        'publication_id': 'cand-4473', 'locator': 'Briganti, Pietro da Cortona (Florence, 1962), p. 142',
        'marker': 4, 'line': 315, 'body_ids': ['st-chp7-p176-i16'],
        'transcription_note': 'The printed note reads Briganti; the S0 OCR transcribes Brigand.',
    },
    'st-chp7-p176-n5-cite-malvasia': {
        'publication_id': 'cand-6933', 'locator': 'Malvasia, Felsina Pittrice, vol. II, p. 264',
        'marker': 5, 'line': 316, 'body_ids': ['st-chp7-p176-i16b'],
    },
    'st-chp7-p176-n6-cite-blunt': {
        'publication_id': 'cand-7045', 'locator': 'Blunt (1954), p. 89; title unresolved',
        'marker': 6, 'line': 316, 'body_ids': ['st-chp7-p176-i22'],
    },
    'st-chp7-p176-n7-cite-wittkower': {
        'publication_id': 'cand-4383', 'locator': 'Wittkower, The Sculptures of Gian Lorenzo Bernini (1955), p. 202',
        'marker': 7, 'line': 317, 'body_ids': ['st-chp7-p176-i23', 'st-chp7-p176-i24', 'st-chp7-p176-i25', 'st-chp7-p176-i26'],
    },
    'st-chp7-p176-n8-cite-poussin-correspondance': {
        'publication_id': 'cand-4634', 'locator': 'Poussin, Correspondance, p. 188',
        'marker': 8, 'line': 317, 'body_ids': ['st-chp7-p176-i29'],
    },
    'st-chp7-p176-n9-cite-passeri': {
        'publication_id': 'cand-4376', 'locator': 'Passeri, p. 115',
        'marker': 9, 'line': 318, 'body_ids': ['st-chp7-p176-i30'],
        'transcription_note': 'The printed note reads p. 115; the S0 OCR transcribes p. 11$.',
    },
}

SOURCE_GUARDS = {
    314: ('1 Mazarin, 1961.', '2 Correspondance, p. 15.'),
    315: ('3 ibid., p. 31, note 2.', '4 ibid., pp. 36 and 37; Brigand, 1962, p. 142.'),
    316: ('5 Malvasia, II, p. 264.', '6 Blunt, 1954, p. 89.'),
    317: ('7 Wittkower, 1955, p. 202.', '8 Poussin: Correspondance, p. 188.'),
    318: ('9 Passeri, p. 11$.',),
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
    for spec in TARGETS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive missing or mistyped: {spec['publication_id']}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    body_to_citations: dict[str, list[str]] = {}
    body_expected_refs: dict[str, tuple[int, int]] = {}
    for citation_id, spec in TARGETS.items():
        for body_id in spec['body_ids']:
            body_to_citations.setdefault(body_id, []).append(citation_id)
            body_expected_refs[body_id] = (spec['marker'], spec['line'])

    required = set(TARGETS) | set(body_to_citations)
    if not required.issubset(by_id):
        raise SystemExit(f'missing citation/body statements: {sorted(required - set(by_id))}')
    note_targets = {
        sid for sid, row in by_id.items()
        if row.get('segment_id') == NOTE_SEGMENT
        and 314 <= (row.get('qualifiers') or {}).get('source_line_start', 0) <= 318
        and (row.get('qualifiers') or {}).get('predicate', row.get('predicate')) == 'footnote_citation'
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if note_targets != set(TARGETS):
        raise SystemExit(f'p.176 unset citation target set changed: {sorted(note_targets ^ set(TARGETS))}')

    for citation_id, spec in TARGETS.items():
        row = by_id[citation_id]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation changed since review: {citation_id}')
    for body_id, (marker, line_no) in body_expected_refs.items():
        q = by_id[body_id].get('qualifiers') or {}
        refs = q.get('footnote_refs') or []
        if not any(ref.get('marker') == marker and ref.get('segment_id') == NOTE_SEGMENT
                   and ref.get('source_line') == line_no for ref in refs):
            raise SystemExit(f'body footnote locator changed: {body_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        spec = TARGETS.get(row['statement_id'])
        if spec is None:
            output.append(row)
            continue
        publication_id = spec['publication_id']
        old_claim = str((row.get('qualifiers') or {}).get('claim') or '').strip()
        q = dict(row.get('qualifiers') or {})
        claim = (f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {spec['locator']} "
                 f"in footnote {spec['marker']}. The prior note records: {old_claim}")
        if spec.get('transcription_note'):
            claim += ' ' + spec['transcription_note']
        row.update({
            'subject_candidate_id': SOURCE_BOOK_ID,
            'object_candidate_id': publication_id,
            'predicate': 'cites',
        })
        q.update({
            'claim': claim,
            'citation_publication_candidate_id': publication_id,
            'citation_locator': spec['locator'],
            'citations': [{
                'source_candidate_id': SOURCE_BOOK_ID,
                'publication_candidate_id': publication_id,
                'locator': spec['locator'],
            }],
            'cited_material_not_independently_consulted': True,
            'footnote_marker': spec['marker'],
            'footnote_number': spec['marker'],
            'footnote_segment': NOTE_SEGMENT,
            'footnote_refs': [{
                'marker': spec['marker'],
                'segment_id': NOTE_SEGMENT,
                'source_line': spec['line'],
                'statement_ids': body_to_citations[next(iter(spec['body_ids']))]
                if len(spec['body_ids']) == 1 else [
                    item for item, item_spec in TARGETS.items()
                    if item_spec['marker'] == spec['marker'] and item_spec['line'] == spec['line']
                ],
            }],
            'related_body_statement_ids': spec['body_ids'],
            'linked_body_statement_ids': spec['body_ids'],
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
            'relation_candidate': True,
            'relation_candidate_note': (
                'S2 citation candidate: the printed footnote identifies this source and locator. '
                'This records Haskell’s bibliographic reference only; the cited material was not '
                'independently consulted and no S6 edge is created.'
            ),
        })
        row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for body_id, citation_ids in body_to_citations.items():
        marker, line_no = body_expected_refs[body_id]
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = [dict(ref) for ref in (q.get('footnote_refs') or [])]
        ref = next(item for item in refs
                   if item.get('marker') == marker and item.get('segment_id') == NOTE_SEGMENT
                   and item.get('source_line') == line_no)
        ref['statement_ids'] = citation_ids
        q.update({
            'footnote_refs': refs,
            'footnote_marker': marker,
            'footnote_number': marker,
            'footnote_segment': NOTE_SEGMENT,
            'footnote_statement_ids': citation_ids,
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
        })
        row['qualifiers'] = q

    output_bytes = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8445, False: 3419, 'unset': 2323}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(TARGETS),
        'linked_body_statements': len(body_to_citations),
        'footnote_numbers': len({spec['marker'] for spec in TARGETS.values()}),
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
