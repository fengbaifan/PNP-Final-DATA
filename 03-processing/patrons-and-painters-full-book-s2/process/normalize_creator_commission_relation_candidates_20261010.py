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
BACKUP = TABLE.with_name(TABLE.name + '.bak-s2-handoff-creator-commission-relations-20261010')
EXPECTED_TABLE_SHA256 = 'a9815b9483c4d9f3dc78fd8f8a0b82cd468bd15259b6f21f461d66573616ae46'
EXPECTED_PREDICATES = {'commissioned_pictures_from': 9, 'created_by': 6}
EXPECTED_IDS = {
    'st-chp7-p194-schoenborn-commission-balestra',
    'st-chp7-p194-schoenborn-commission-cignani',
    'st-chp7-p194-schoenborn-commission-giordano',
    'st-chp7-p194-schoenborn-commission-lazzarini',
    'st-chp7-p194-schoenborn-commission-luti',
    'st-chp7-p194-schoenborn-commission-maratta',
    'st-chp7-p194-schoenborn-commission-solimena',
    'st-chp7-p194-schoenborn-commission-trevisani',
    'st-chp7-p200-n1-peterborough-commissions-dal-sole',
    'st-chp3-secii-l102-113-aurora-created',
    'st-chp3-secii-l115-123-bellori-drawings',
    'st-chp3-secii-l125-135-angels-fresco',
    'st-chp3-secii-l125-135-oratorian-fresco',
    'st-chp3-secii-l125-135-philip-fresco',
    'st-chp4-sec-ii-l46-51-bernini-bust-created',
}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def prepare() -> tuple[bytes, bytes, list[tuple[str, str]]]:
    original = TABLE.read_bytes()
    if sha256(original) != EXPECTED_TABLE_SHA256:
        raise SystemExit(f'table changed: expected {EXPECTED_TABLE_SHA256}, got {sha256(original)}')
    lines = original.decode('utf-8').splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    selected = [row for row in rows if row.get('statement_id') in EXPECTED_IDS]
    if {row.get('statement_id') for row in selected} != EXPECTED_IDS:
        raise SystemExit('the expected statement ID set is not present exactly')
    by_predicate = collections.Counter(row.get('predicate') for row in selected)
    if dict(by_predicate) != EXPECTED_PREDICATES:
        raise SystemExit(f'unexpected predicate distribution: {dict(by_predicate)}')
    known_candidates = {row['candidate_id'] for row in csv.DictReader(CANDIDATES.open(encoding='utf-8-sig', newline=''))}
    for row in selected:
        q = row.get('qualifiers') or {}
        if 'relation_candidate' in q:
            raise SystemExit(f'classification already exists: {row["statement_id"]}')
        if row.get('origin') != 'book' or not row.get('source_file') or not row.get('original_quote'):
            raise SystemExit(f'missing source attribution: {row["statement_id"]}')
        if not q.get('source_line_start') or not q.get('source_line_end'):
            raise SystemExit(f'missing source line anchor: {row["statement_id"]}')
        if not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
            raise SystemExit(f'missing relationship endpoint: {row["statement_id"]}')
        for key in ('subject_candidate_id', 'object_candidate_id'):
            if row[key] not in known_candidates:
                raise SystemExit(f'unknown candidate key {row[key]} in {row["statement_id"]}')
        claim = q.get('claim', '').casefold()
        if row['predicate'] == 'commissioned_pictures_from' and 'commission' not in claim:
            raise SystemExit(f'claim does not state commissioning: {row["statement_id"]}')
        if row['predicate'] == 'created_by' and not any(word in claim for word in ('paint', 'made', 'creator', 'commission')):
            raise SystemExit(f'claim does not state creation: {row["statement_id"]}')
    updated_lines = []
    replacements = []
    seen = set()
    for line in lines:
        if not line.strip():
            updated_lines.append(line)
            continue
        row = json.loads(line)
        if row.get('statement_id') in EXPECTED_IDS:
            row.setdefault('qualifiers', {})['relation_candidate'] = True
            seen.add(row['statement_id'])
            replacements.append((row['statement_id'], row['predicate']))
            updated_lines.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        else:
            updated_lines.append(line)
    if seen != EXPECTED_IDS:
        raise SystemExit('not all selected rows were rewritten')
    result = ''.join(updated_lines).encode('utf-8')
    final_rows = [json.loads(line) for line in result.decode('utf-8').splitlines() if line.strip()]
    flagged = [row for row in final_rows if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in flagged)
    if (len(flagged), complete) != (3394, 3380):
        raise SystemExit(f'unexpected total after classification: {len(flagged)} flagged, {complete} complete')
    return original, result, sorted(replacements)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    original, result, selected = prepare()
    print(json.dumps({'mode': 'apply' if args.apply else 'dry-run', 'selected': [{'statement_id': sid, 'predicate': pred} for sid, pred in selected], 'count': len(selected), 'predicate_counts': dict(collections.Counter(p for _, p in selected)), 'relation_candidates_after': 3394, 'complete_after': 3380, 'open_after': 14, 'before_sha256': sha256(original), 'after_sha256': sha256(result), 'write': args.apply}, ensure_ascii=False, indent=2))
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
