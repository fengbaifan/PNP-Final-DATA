from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / '04-knowledge/tables/book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge/tables/entity-candidates.csv'
BACKUP = TABLE.with_name(TABLE.name + '.bak-s2-handoff-predicate-family-relations-20261010')
EXPECTED_TABLE_SHA256 = 'c3fcfcbf8d8ea1549963fcb84bf8a86cf5fc48dd4b9094953ebc9105df316a39'
EXPECTED_PREDICATES = {'located_at': 6, 'pupil_of': 4, 'commissioned_by': 4, 'owned_by': 3, 'authored_by': 3, 'acquired_from': 3, 'patronized': 3, 'painted_for': 3}
EXPECTED_IDS = {
    'st-chp3-secii-l102-113-aurora-location',
    'st-chp3-secii-l125-135-church-site',
    'st-chp3-secii-l125-135-construction-site',
    'st-chp6-p166-n1-confession',
    'st-chp6-p166-n1-sacraments',
    'st-chp7-p171-n6-series-located-prado',
    'st-chp6-p161-gherardi-pupil-of-mola',
    'st-chp6-p165-v1-01',
    'st-chp6-p165-v1-22',
    'st-chp7-p191-i13',
    'st-chp3-secii-l125-135-alterations-for-spada',
    'st-chp3-secii-l125-135-colonnade-for-spada',
    'st-chp3-secii-l125-135-fresco-commission',
    'st-chp3-secii-l125-135-oratorio-commissioned-by',
    'st-chp4-sec-ii-l46-51-cassiano-owned-allegory-coral-fishing',
    'st-chp4-sec-ii-l46-51-cassiano-owned-bernini-drawings',
    'st-chp4-sec-ii-l46-51-cassiano-owned-madonna-child',
    'st-chp4-sec-ii-p102-footnote2-vouet-letters-authored-by',
    'st-chp4-sec-ii-p103-footnote2-pietro-letters-authored-by',
    'st-fm-title-authored-by',
    'st-chp3-secii-l102-113-casino-purchase',
    'st-chp3-secii-l125-135-palace-acquisition',
    'st-chp7-p191-i07',
    'st-chp3-secii-l102-113-ludovisi-emilia-patronage',
    'st-chp3-secii-p70-note3-serra-guercino-patronage',
    'st-chp7-p193-leopold-patronizes-vecchia',
    'st-chp3-seciv-l26-33-courtois-paints-for-oliva',
    'st-chp3-seciv-l26-33-guglielmo-paints-for-oliva',
    'st-chp7-p171-n6-series-painted-for-king',
}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def prepare() -> tuple[bytes, bytes, list[tuple[str, str]]]:
    original = TABLE.read_bytes()
    actual_hash = sha256(original)
    if actual_hash != EXPECTED_TABLE_SHA256:
        raise SystemExit(f'table changed: expected {EXPECTED_TABLE_SHA256}, got {actual_hash}')
    lines = original.decode('utf-8').splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    selected = [row for row in rows if row.get('statement_id') in EXPECTED_IDS]
    if {row.get('statement_id') for row in selected} != EXPECTED_IDS:
        raise SystemExit('expected statement ID set is not present exactly')
    by_predicate = collections.Counter(row.get('predicate') for row in selected)
    if dict(by_predicate) != EXPECTED_PREDICATES:
        raise SystemExit(f'unexpected predicate distribution: {dict(by_predicate)}')
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        known_candidates = {row['candidate_id'] for row in csv.DictReader(f)}
    for row in selected:
        q = row.get('qualifiers') or {}
        if 'relation_candidate' in q:
            raise SystemExit(f'already classified: {row["statement_id"]}')
        if row.get('origin') != 'book' or not row.get('source_file') or not row.get('original_quote'):
            raise SystemExit(f'missing source attribution: {row["statement_id"]}')
        if not q.get('source_line_start') or not q.get('source_line_end'):
            raise SystemExit(f'missing source line anchor: {row["statement_id"]}')
        if not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
            raise SystemExit(f'missing endpoint: {row["statement_id"]}')
        if row['subject_candidate_id'] not in known_candidates or row['object_candidate_id'] not in known_candidates:
            raise SystemExit(f'unknown candidate endpoint: {row["statement_id"]}')
    updated_lines = []
    seen = set()
    selected_info = []
    for line in lines:
        if not line.strip():
            updated_lines.append(line)
            continue
        row = json.loads(line)
        if row.get('statement_id') in EXPECTED_IDS:
            row.setdefault('qualifiers', {})['relation_candidate'] = True
            seen.add(row['statement_id'])
            selected_info.append((row['statement_id'], row['predicate']))
            updated_lines.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        else:
            updated_lines.append(line)
    if seen != EXPECTED_IDS:
        raise SystemExit('not all fixed records were replaced exactly once')
    result = ''.join(updated_lines).encode('utf-8')
    final_rows = [json.loads(line) for line in result.decode('utf-8').splitlines() if line.strip()]
    flagged = [row for row in final_rows if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in flagged)
    if (len(flagged), complete) != (3423, 3409):
        raise SystemExit(f'unexpected totals after update: {len(flagged)} flagged, {complete} complete')
    return original, result, sorted(selected_info)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    original, result, selected = prepare()
    print(json.dumps({'mode': 'apply' if args.apply else 'dry-run', 'count': len(selected), 'predicate_counts': dict(collections.Counter(p for _, p in selected)), 'relation_candidates_after': 3423, 'complete_after': 3409, 'open_after': 14, 'selected_statement_ids': [sid for sid, _ in selected], 'before_sha256': sha256(original), 'after_sha256': sha256(result), 'write': args.apply}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy exists: {BACKUP}')
    shutil.copy2(TABLE, BACKUP)
    if sha256(BACKUP.read_bytes()) != sha256(original):
        raise SystemExit('recovery copy does not match preimage')
    TABLE.write_bytes(result)
    if sha256(TABLE.read_bytes()) != sha256(result):
        TABLE.write_bytes(original)
        raise SystemExit('post-write hash mismatch; original bytes restored')
    print(f'backup={BACKUP}')
    print(f'applied_sha256={sha256(result)}')

if __name__ == '__main__':
    main()
