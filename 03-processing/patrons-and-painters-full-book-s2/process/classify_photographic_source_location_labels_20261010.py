from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + '.bak-s2-handoff-photo-source-location-labels-20261010'
)
BOOK_ID = 'cand-2962'
EXPECTED_SHA256 = '2409a55dae3629c0b3bb59b3db51b2ff8eaf1335517b4a6af37ed33c8e961ea0'
SOURCE_FILE = '02-sources/02-Markdown/00_05_List_of_Plates.md'
SEGMENT_ID = 'front-matter:00_05_List_of_Plates:l140-172'
TARGETS = {
    'st-fm-photo-h01-location': ('cand-3620', 'cand-3955', 164, 164),
    'st-fm-photo-h02-location': ('cand-4194', 'cand-4200', 164, 164),
    'st-fm-photo-h04-location': ('cand-3673', 'cand-2719', 164, 164),
    'st-fm-photo-h05-location': ('cand-4195', 'cand-2719', 164, 165),
    'st-fm-photo-h09-location': ('cand-4196', 'cand-3932', 166, 166),
    'st-fm-photo-h16-location': ('cand-4199', 'cand-2719', 168, 168),
    'st-fm-photo-h19-location': ('cand-3681', 'cand-3955', 169, 170),
    'st-fm-photo-h20-location': ('cand-3683', 'cand-3397', 170, 171),
    'st-fm-photo-h21-location': ('cand-3685', 'cand-3909', 171, 171),
    'st-fm-photo-h22-location': ('cand-3690', 'cand-3909', 171, 172),
    'st-fm-photo-h23-location': ('cand-3693', 'cand-3909', 172, 172),
    'st-fm-photo-h24-location': ('cand-3617', 'cand-3398', 172, 172),
    'st-fm-photo-h25-location': ('cand-3755', 'cand-3991', 172, 172),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare() -> tuple[bytes, bytes, dict]:
    before = STATEMENTS.read_bytes()
    before_hash = sha256(before)
    if before_hash != EXPECTED_SHA256:
        raise SystemExit(f'statement table hash changed: {before_hash}')

    with (TABLES / 'entity-candidates.csv').open(encoding='utf-8-sig', newline='') as f:
        import csv

        candidate_by_id = {row['candidate_id']: row for row in csv.DictReader(f)}
    if candidate_by_id.get(BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('book candidate is absent or not archive typed')

    rows = [json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip()]
    if len({row['statement_id'] for row in rows}) != len(rows):
        raise SystemExit('duplicate statement IDs in source table')
    by_id = {row['statement_id']: row for row in rows}
    if set(TARGETS) - set(by_id):
        raise SystemExit(f'missing target statements: {sorted(set(TARGETS) - set(by_id))}')

    output = []
    changes = []
    for row in rows:
        expected = TARGETS.get(row['statement_id'])
        if not expected:
            output.append(row)
            continue
        subject_id, place_id, line_start, line_end = expected
        q = dict(row.get('qualifiers') or {})
        if (
            row.get('predicate') != 'photographic_source_location_label'
            or row.get('subject_candidate_id') != subject_id
            or row.get('object_candidate_id') != place_id
            or row.get('segment_id') != SEGMENT_ID
            or row.get('source_file') != SOURCE_FILE
            or q.get('source_line_start') != line_start
            or q.get('source_line_end') != line_end
            or q.get('relation_candidate') is not None
            or not row.get('original_quote')
            or 'location label' not in str(q.get('claim') or '')
        ):
            raise SystemExit(f'source row changed or already classified: {row["statement_id"]}')
        if not candidate_by_id.get(subject_id):
            raise SystemExit(f'photographic source candidate is missing: {row["statement_id"]}')
        if candidate_by_id.get(place_id, {}).get('suggested_type') != 'place':
            raise SystemExit(f'location endpoint is not place typed: {row["statement_id"]}')

        q['relation_candidate'] = True
        q['relation_candidate_note'] = (
            'S2 relation candidate based on the explicit pair in the photographic sources list; '
            'the city is transcribed only as a source-location label. This does not establish '
            'where the particular photograph was taken or a supplier’s headquarters. Some '
            'supplier identities or types remain unresolved; no formal S6 edge is created.'
        )
        q.setdefault(
            'qualification',
            'The city appears after the photographic-source name in the list; the source does not '
            'specify whether it identifies an address, a supplier location, or a place of image production.',
        )
        row = dict(row)
        row['qualifiers'] = q
        output.append(row)
        changes.append({
            'statement_id': row['statement_id'],
            'source_candidate': subject_id,
            'location_label_place': place_id,
            'source_lines': [line_start, line_end],
            'original_quote': row['original_quote'],
        })

    if len(changes) != len(TARGETS):
        raise SystemExit(f'expected {len(TARGETS)} changes; found {len(changes)}')
    after = (
        '\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output)
        + '\n'
    ).encode('utf-8')
    true_rows = [row for row in output if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in true_rows)
    unclassified_dual = sum(
        bool(row.get('subject_candidate_id') and row.get('object_candidate_id'))
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
        for row in output
    )
    if (len(true_rows), complete, len(true_rows) - complete, unclassified_dual) != (3584, 3570, 14, 4471):
        raise SystemExit('unexpected post-state relation candidate counts')
    return before, after, {
        'classified_location_label_candidates': changes,
        'total_statements': len(output),
        'relation_candidates': len(true_rows),
        'complete_endpoint_ids': complete,
        'missing_endpoint_ids': len(true_rows) - complete,
        'dual_endpoint_unclassified': unclassified_dual,
        'before_sha256': before_hash,
        'after_sha256': sha256(after),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    _, after, report = prepare()
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    if BACKUP.exists():
        raise SystemExit(f'backup already exists: {BACKUP}')
    temporary = STATEMENTS.with_name(STATEMENTS.name + '.tmp-photo-source-classification')
    if temporary.exists():
        raise SystemExit(f'temporary file already exists: {temporary}')
    shutil.copy2(STATEMENTS, BACKUP)
    temporary.write_bytes(after)
    temporary.replace(STATEMENTS)
    actual = sha256(STATEMENTS.read_bytes())
    if actual != report['after_sha256']:
        shutil.copy2(BACKUP, STATEMENTS)
        raise SystemExit(f'post-write hash mismatch; restored backup: {actual}')
    print('applied; recovery copy written; hash verified')


if __name__ == '__main__':
    main()
