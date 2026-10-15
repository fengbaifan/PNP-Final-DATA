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
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
EXPECTED_HASHES = {
    STATEMENTS.name: 'ef485f8ef95045ac87f2b6a896884b548af2a2c6e5c4df6410b1e9c3cf6862d3',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p188-notes-20261013')
CITATIONS = {
    'st-chp7-p188-n1-cite-wittkower': {
        'locator': 'Wittkower, The Sculptures of Gian Lorenzo Bernini (1955), pp. 230–231',
        'line': 368, 'marker': 1, 'body': 'st-chp7-p188-i17',
    },
    'st-chp7-p188-n2-cite-ibid-wittkower': {
        'locator': 'Wittkower, The Sculptures of Gian Lorenzo Bernini (1955), pp. 234–236 (ibid. to footnote 1)',
        'line': 369, 'marker': 2, 'body': 'st-chp7-p188-i21',
    },
}
SOURCE_GUARDS = {368: 'Wittkower, 1955, pp. 230-1, with bibliography.', 369: 'ibid., pp. 234-6.'}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = {p: p.read_bytes() for p in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {p.name: sha256(data) for p, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    for line_no, snippet in SOURCE_GUARDS.items():
        if snippet not in source_lines[line_no - 1]:
            raise SystemExit(f'source guard failed at L{line_no}: {source_lines[line_no - 1]}')
    candidates = {r['candidate_id']: r for r in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))}
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive' or candidates.get('cand-4383', {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source book or Wittkower publication candidate is missing/mistyped')
    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {r['statement_id']: r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    for note_id, spec in CITATIONS.items():
        r, q = by_id[note_id], by_id[note_id].get('qualifiers') or {}
        if (r.get('segment_id') != NOTE_SEGMENT or r.get('predicate') != 'footnote_citation'
                or r.get('subject_candidate_id') is not None or r.get('object_candidate_id') != 'cand-4383'
                or q.get('source_line_start') != spec['line'] or q.get('relation_candidate') is not None
                or q.get('linked_body_statement_ids') != [spec['body']]):
            raise SystemExit(f'citation row changed since review: {note_id}')
        if note_id not in (by_id[spec['body']].get('qualifiers') or {}).get('footnote_statement_ids', []):
            raise SystemExit(f'reciprocal body link missing: {spec["body"]}')

    output = []
    for src in rows:
        r = dict(src)
        spec = CITATIONS.get(r['statement_id'])
        if spec:
            q = dict(r.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            r.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': 'cand-4383', 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates['cand-4383']['canonical_name']} at {spec['locator']} in footnote {spec['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': 'cand-4383', 'citation_locator': spec['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': 'cand-4383', 'locator': spec['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': spec['marker'], 'footnote_number': spec['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': spec['line'], 'statement_ids': [spec['body']]}],
                'related_body_statement_ids': [spec['body']], 'linked_body_statement_ids': [spec['body']],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; the cited publication was not independently consulted, and no S6 edge is created.',
            })
            r['qualifiers'] = q
        output.append(r)
    out = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14187, {True: 8545, False: 3418, 'unset': 2224}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {'mode': 'apply' if args.apply else 'dry_run', 'normalized_citations': len(CITATIONS),
              'reciprocal_body_links_checked': len(CITATIONS), 'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
              'before_sha256': hashes, 'after_statement_sha256': sha256(out), 'backup': str(BACKUP.relative_to(ROOT))}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    if STATEMENTS.read_bytes() != raw[STATEMENTS]:
        raise SystemExit('statement table changed after dry-run preparation')
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, out)
    if sha256(STATEMENTS.read_bytes()) != report['after_statement_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
