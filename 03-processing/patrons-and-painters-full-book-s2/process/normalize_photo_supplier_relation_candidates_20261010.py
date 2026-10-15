from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / '04-knowledge/tables/book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge/tables/entity-candidates.csv'
BACKUP = TABLE.with_name(TABLE.name + '.bak-s2-handoff-photo-supplier-relations-20261010')
EXPECTED_TABLE_SHA256 = 'c7e50fe0a1907cb3a668c48ca95f1f71de25394d9dd4fe2154c4f82d20a486db'
SOURCE_FILE = '02-sources/02-Markdown/00_05_List_of_Plates.md'
PREDICATE = 'photograph_supplied_by'
EXPECTED_COUNT = 79

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def prepare() -> tuple[bytes, bytes, list[str]]:
    original = TABLE.read_bytes()
    actual_hash = sha256(original)
    if actual_hash != EXPECTED_TABLE_SHA256:
        raise SystemExit(f'table hash changed: expected {EXPECTED_TABLE_SHA256}, got {actual_hash}')
    lines = original.decode('utf-8').splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    selected = [row for row in rows if row.get('predicate') == PREDICATE]
    if len(selected) != EXPECTED_COUNT:
        raise SystemExit(f'expected {EXPECTED_COUNT} {PREDICATE} statements, got {len(selected)}')
    candidate_ids = set()
    for row in selected:
        q = row.get('qualifiers') or {}
        if q.get('relation_candidate') is not None:
            raise SystemExit(f'existing relation classification on {row["statement_id"]}')
        if row.get('origin') != 'book' or row.get('source_file') != SOURCE_FILE:
            raise SystemExit(f'unexpected source or origin: {row["statement_id"]}')
        if not row.get('original_quote') or not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
            raise SystemExit(f'missing quote or endpoint: {row["statement_id"]}')
        if q.get('photographic_source_role') != 'reproduction image supplier':
            raise SystemExit(f'unexpected photographic role: {row["statement_id"]}')
        if 'supplying the photograph' not in q.get('claim', ''):
            raise SystemExit(f'claim does not establish supplier relation: {row["statement_id"]}')
        if not q.get('source_line_start') or not q.get('source_line_end'):
            raise SystemExit(f'missing source line anchor: {row["statement_id"]}')
        candidate_ids.update((row['subject_candidate_id'], row['object_candidate_id']))
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        known_candidates = {row['candidate_id'] for row in csv.DictReader(f)}
    missing = sorted(candidate_ids - known_candidates)
    if missing:
        raise SystemExit(f'unresolved candidate keys: {missing}')
    selected_ids = {row['statement_id'] for row in selected}
    if len(selected_ids) != EXPECTED_COUNT:
        raise SystemExit('selected statement IDs are not unique')
    updated_lines = []
    replaced = set()
    for line in lines:
        if not line.strip():
            updated_lines.append(line)
            continue
        row = json.loads(line)
        if row.get('statement_id') in selected_ids:
            row.setdefault('qualifiers', {})['relation_candidate'] = True
            replaced.add(row['statement_id'])
            updated_lines.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        else:
            updated_lines.append(line)
    if replaced != selected_ids:
        raise SystemExit('not all selected statements were replaced exactly once')
    result = ''.join(updated_lines).encode('utf-8')
    final_rows = [json.loads(line) for line in result.decode('utf-8').splitlines() if line.strip()]
    flagged = [row for row in final_rows if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in flagged)
    if (len(flagged), complete) != (3379, 3365):
        raise SystemExit(f'unexpected final candidate counts: total={len(flagged)}, complete={complete}')
    return original, result, sorted(selected_ids)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    original, result, selected_ids = prepare()
    print(json.dumps({'mode': 'apply' if args.apply else 'dry-run', 'predicate': PREDICATE, 'selected_statement_count': len(selected_ids), 'expected_relation_candidate_total_after': 3379, 'expected_complete_relation_candidates_after': 3365, 'expected_open_relation_candidates_after': 14, 'before_sha256': sha256(original), 'after_sha256': sha256(result), 'write': args.apply}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    shutil.copy2(TABLE, BACKUP)
    if sha256(BACKUP.read_bytes()) != sha256(original):
        raise SystemExit('recovery copy does not match the preimage')
    TABLE.write_bytes(result)
    if sha256(TABLE.read_bytes()) != sha256(result):
        TABLE.write_bytes(original)
        raise SystemExit('post-write hash mismatch; original bytes restored')
    print(f'backup={BACKUP}')
    print(f'applied_sha256={sha256(result)}')

if __name__ == '__main__':
    main()
