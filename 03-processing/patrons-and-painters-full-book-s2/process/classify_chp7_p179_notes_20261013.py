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
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l113-126'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: '6e60e4eede511c523fb20bbf2eb4b8cd5f72f6671a0af3434d2d2fe6a95fb60b',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p179-notes-20261013')

TARGETS = {
    'st-chp7-p179-n1-cite-wittkower': {
        'publication_id': 'cand-4383', 'locator': 'Wittkower, The Sculptures of Gian Lorenzo Bernini (1955), p. 201',
        'marker': 1, 'line': 126, 'segment': BODY_SEGMENT, 'body_ids': ['st-chp7-p179-i07'],
        'already_classified': True,
    },
    'st-chp7-p179-n2-cite-wittkower-ibid': {
        'publication_id': 'cand-4383', 'locator': 'Wittkower, The Sculptures of Gian Lorenzo Bernini (1955), p. 201; ibid., with bibliography',
        'marker': 2, 'line': 330, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p179-i08', 'st-chp7-p179-i09', 'st-chp7-p179-i10'],
    },
    'st-chp7-p179-n3-cite-hervey': {
        'publication_id': 'cand-5615', 'locator': 'Hervey, The life, correspondence and collections of Thomas Howard, Earl of Arundel (1921), p. 391',
        'marker': 3, 'line': 331, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p179-i11', 'st-chp7-p179-i12', 'st-chp7-p179-i13'],
    },
    'st-chp7-p179-n4-cite-passeri': {
        'publication_id': 'cand-4376', 'locator': 'Passeri, p. 191',
        'marker': 4, 'line': 332, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p179-i16'],
    },
    'st-chp7-p179-n5-cite-albion': {
        'publication_id': 'cand-7055', 'locator': 'Albion, Charles I and the Court of Rome (1935), p. 395',
        'marker': 5, 'line': 333, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p179-i17', 'st-chp7-p179-i18'],
    },
    'st-chp7-p179-n6-cite-guido-reni': {
        'publication_id': 'cand-7069', 'locator': 'Guido Reni exhibition catalog (1954), p. 109',
        'marker': 6, 'line': 334, 'segment': NOTE_SEGMENT, 'body_ids': ['st-chp7-p179-i19'],
    },
}

SOURCE_GUARDS = {
    126: ('- 1 Wittkower, 1955, p. 201.',),
    330: ('2 ibid., with bibliography.',),
    331: ('3 Hervey, p. 391.',),
    332: ('4 Passeri, p. 191.',),
    333: ('5 Albion, p. 395.',),
    334: ('6 Guido Reni, p. 109.',),
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
    body_to_notes: dict[str, list[str]] = {}
    body_refs: dict[str, tuple[int, int, str]] = {}
    for note_id, spec in TARGETS.items():
        for body_id in spec['body_ids']:
            body_to_notes.setdefault(body_id, []).append(note_id)
            body_refs[body_id] = (spec['marker'], spec['line'], spec['segment'])
    required = set(TARGETS) | set(body_to_notes)
    if not required.issubset(by_id):
        raise SystemExit(f'missing citation/body statement: {sorted(required - set(by_id))}')

    unset_targets = {
        row['statement_id'] for row in rows
        if row.get('segment_id') == NOTE_SEGMENT
        and 330 <= (row.get('qualifiers') or {}).get('source_line_start', 0) <= 334
        and row.get('predicate') == 'footnote_citation'
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    expected_unset = {sid for sid, spec in TARGETS.items() if not spec.get('already_classified')}
    if unset_targets != expected_unset:
        raise SystemExit(f'p.179 unset citation target set changed: {sorted(unset_targets ^ expected_unset)}')
    for note_id, spec in TARGETS.items():
        row = by_id[note_id]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != spec['segment'] or row.get('predicate') != 'footnote_citation'
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or (spec.get('already_classified') and q.get('relation_candidate') is not True)
                or (not spec.get('already_classified') and q.get('relation_candidate') is not None)):
            raise SystemExit(f'citation changed since review: {note_id}')
    for body_id, (marker, line_no, segment_id) in body_refs.items():
        q = by_id[body_id].get('qualifiers') or {}
        if not any(ref.get('marker') == marker and ref.get('segment_id') == segment_id
                   and ref.get('source_line') == line_no for ref in (q.get('footnote_refs') or [])):
            raise SystemExit(f'body footnote locator changed: {body_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        spec = TARGETS.get(row['statement_id'])
        if spec is not None:
            publication_id = spec['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            marker, line_no, source_segment = spec['marker'], spec['line'], spec['segment']
            body_ids = spec['body_ids']
            row.update({
                'subject_candidate_id': SOURCE_BOOK_ID,
                'object_candidate_id': publication_id,
                'predicate': 'cites',
            })
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {spec['locator']} in footnote {marker}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id,
                'citation_locator': spec['locator'],
                'citations': [{
                    'source_candidate_id': SOURCE_BOOK_ID,
                    'publication_candidate_id': publication_id,
                    'locator': spec['locator'],
                }],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': marker,
                'footnote_number': marker,
                'footnote_segment': source_segment,
                'footnote_refs': [{
                    'marker': marker,
                    'segment_id': source_segment,
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
            q.pop('open_endpoint_reason', None)
            row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for body_id, note_ids in body_to_notes.items():
        marker, line_no, segment_id = body_refs[body_id]
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = [dict(ref) for ref in (q.get('footnote_refs') or [])]
        ref = next(item for item in refs if item.get('marker') == marker
                   and item.get('segment_id') == segment_id and item.get('source_line') == line_no)
        ref['statement_ids'] = note_ids
        q.update({
            'footnote_refs': refs,
            'footnote_marker': marker,
            'footnote_number': marker,
            'footnote_segment': segment_id,
            'footnote_statement_ids': note_ids,
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
    if (len(output), counts) != (14187, {True: 8470, False: 3420, 'unset': 2297}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(TARGETS),
        'newly_classified_citations': len(expected_unset),
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
