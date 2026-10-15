from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources/02-Markdown/07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources/01-book/CHP-7.pdf'
SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: 'b27660f58a8939602b1d42fbf0ffbf634d14842a9bba8443dfda0fcaeff1edfa',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p175-notes-20261013')
TARGETS = {
    'st-chp7-p175-n1-cite-baudson': {
        'publication_id': 'cand-7039', 'author_id': 'cand-7040',
        'locator': 'Baudson, pp. 28–33', 'marker': 1, 'line': 312,
        'body_ids': ['st-chp7-p175-i12'],
    },
    'st-chp7-p175-n1-cite-seicento': {
        'publication_id': 'cand-7041',
        'locator': 'Seicento Europeo (1956), p. 64', 'marker': 1, 'line': 312,
        'body_ids': ['st-chp7-p175-i12'],
    },
    'st-chp7-p175-n2-cite-bonnaffe': {
        'publication_id': 'cand-7042', 'author_id': 'cand-7043',
        'locator': 'Bonnaffé, p. 269', 'marker': 2, 'line': 313,
        'body_ids': ['st-chp7-p175-i22'],
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before = STATEMENTS.read_bytes()
    hashes = {
        STATEMENTS.name: sha256(before),
        CANDIDATES.name: sha256(CANDIDATES.read_bytes()),
        SOURCE.name: sha256(SOURCE.read_bytes()),
        PDF.name: sha256(PDF.read_bytes()),
    }
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        candidates = {row['candidate_id']: row for row in csv.DictReader(f)}
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell book candidate is absent or not archive typed')
    for spec in TARGETS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive missing or mistyped: {spec['publication_id']}")
        if spec.get('author_id') and candidates.get(spec['author_id'], {}).get('suggested_type') != 'person':
            raise SystemExit(f"citation author missing or mistyped: {spec['author_id']}")

    rows = [json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    required = set(TARGETS) | {sid for spec in TARGETS.values() for sid in spec['body_ids']}
    if not required.issubset(by_id):
        raise SystemExit(f'missing citation or body statement: {sorted(required - set(by_id))}')
    for sid, spec in TARGETS.items():
        row = by_id[sid]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation changed since review: {sid}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        spec = TARGETS.get(row['statement_id'])
        if not spec:
            output.append(row)
            continue
        pub_id = spec['publication_id']
        old_claim = str((row.get('qualifiers') or {}).get('claim') or '').strip()
        q = dict(row.get('qualifiers') or {})
        row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': pub_id, 'predicate': 'cites'})
        q.update({
            'claim': f"Haskell’s book cites {candidates[pub_id]['canonical_name']} at {spec['locator']} in this footnote. The prior note records: {old_claim}",
            'citation_publication_candidate_id': pub_id,
            'citation_locator': spec['locator'],
            'citations': [{'source_candidate_id': pub_id, 'publication_candidate_id': pub_id, 'locator': spec['locator']}],
            'cited_material_not_independently_consulted': True,
            'footnote_marker': spec['marker'],
            'footnote_number': spec['marker'],
            'footnote_segment': SEGMENT,
            'footnote_refs': [{'marker': spec['marker'], 'segment_id': SEGMENT, 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
            'related_body_statement_ids': spec['body_ids'],
            'linked_body_statement_ids': spec['body_ids'],
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
            'relation_candidate': True,
            'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator. This records Haskell’s bibliographic reference only; the cited material was not independently consulted and no S6 edge is created.',
        })
        if spec.get('author_id'):
            q['citation_candidate_id'] = spec['author_id']
        row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for sid, spec in TARGETS.items():
        body_id = spec['body_ids'][0]
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = list(q.get('footnote_refs') or [])
        ref = next((item for item in refs if item.get('marker') == spec['marker']), None)
        if ref is None:
            ref = {'marker': spec['marker'], 'segment_id': SEGMENT, 'source_line': spec['line']}
            refs.append(ref)
        if ref.get('segment_id') != SEGMENT or ref.get('source_line') != spec['line']:
            raise SystemExit(f'body footnote locator changed: {body_id}')
        citation_ids = [target_id for target_id, target in TARGETS.items()
                        if target['marker'] == spec['marker'] and target['line'] == spec['line']]
        ref['statement_ids'] = citation_ids
        q.update({
            'footnote_refs': refs,
            'footnote_marker': spec['marker'],
            'footnote_number': spec['marker'],
            'footnote_segment': SEGMENT,
            'footnote_statement_ids': citation_ids,
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
        })
        row['qualifiers'] = q

    text = '\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n'
    after = text.encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8435, False: 3419, 'unset': 2333}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(TARGETS),
        'linked_body_anchors': 2,
        'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
        'before_sha256': hashes,
        'after_sha256': sha256(after),
        'backup': str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    if STATEMENTS.read_bytes() != before:
        raise SystemExit('statement table changed after dry-run preparation')
    shutil.copy2(STATEMENTS, BACKUP)
    STATEMENTS.write_bytes(after)
    if sha256(STATEMENTS.read_bytes()) != report['after_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; hash verified')


if __name__ == '__main__':
    main()
