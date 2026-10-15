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
BACKUP = TABLE.with_name(TABLE.name + '.bak-s2-handoff-patronage-attribution-20261010')
EXPECTED_TABLE_SHA256 = 'db659b2681c59be5841e0c6491f6251d17451f451288e6668bcbc59be2c5aeb3'
EXPECTED_BEFORE = {
    'received-patronage-at-some-stage': 6,
    'painted_by_as_reported_in_liechtenstein_letter': 6,
    'nephew_of': 4,
    'nephew_of_reported': 4,
    'fresco_creation_reported': 3,
    'family_insignia_reported': 3,
}
PREDICATE_REWRITES = {
    'received-patronage-at-some-stage': 'patronized',
    'fresco_creation_reported': 'creator_of',
}
EXPECTED_IDS = {
    'st-chp2-seciv-l171-179-rospigliosi-patronized-camassei',
    'st-chp2-seciv-l171-179-rospigliosi-patronized-gimignani',
    'st-chp2-seciv-l171-179-rospigliosi-patronized-grimaldi',
    'st-chp2-seciv-l171-179-rospigliosi-patronized-maratta',
    'st-chp2-seciv-l171-179-rospigliosi-patronized-preti',
    'st-chp2-seciv-l181-188-rospigliosi-patronized-bernini',
    'st-chp7-p195-baccinelli-susanna',
    'st-chp7-p195-cignani-bacchanal',
    'st-chp7-p195-fumiani-christ',
    'st-chp7-p195-loth-lot-daughters',
    'st-chp7-p195-maratta-bathsheba',
    'st-chp7-p195-piola-vanita',
    'st-chp3-secii-l102-113-ludovisi-nephew',
    'st-chp3-seciv-l118-128-cardinal-ottoboni-nephew-of-alexander-viii',
    'st-chp4-sec-ii-p115-elder-camillo-nephew',
    'st-chp5-p131-camillo-nephew-of-innocent-x',
    'st-chp2-seci-l71-80-scipione-nephew',
    'st-chp2-seciv-l3-4-francesco-nephew-urban',
    'st-chp2-seciv-l3-4-taddeo-nephew-urban',
    'st-chp2-seciv-l3-4-young-antonio-nephew-urban',
    'st-chp2-seciv-l65-77-giovanni-paints-amphitrite-scene',
    'st-chp2-seciv-l65-77-giovanni-paints-europa-scene',
    'st-chp2-seciv-l65-77-giovanni-paints-proserpina-scene',
    'st-chp2-seciv-l91-94-bees-are-barberini-family-insignia',
    'st-chp2-seciv-l91-94-laurel-is-barberini-family-insignia',
    'st-chp2-seciv-l91-94-sun-is-barberini-family-insignia',
}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def prepare() -> tuple[bytes, bytes, list[tuple[str, str, str]]]:
    original = TABLE.read_bytes()
    if sha256(original) != EXPECTED_TABLE_SHA256:
        raise SystemExit(f'table changed: expected {EXPECTED_TABLE_SHA256}, got {sha256(original)}')
    lines = original.decode('utf-8').splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    current_unmarked = [row for row in rows if row.get('predicate') in EXPECTED_BEFORE and row.get('subject_candidate_id') and row.get('object_candidate_id') and 'relation_candidate' not in (row.get('qualifiers') or {})]
    observed = collections.Counter(row['predicate'] for row in current_unmarked)
    if dict(observed) != EXPECTED_BEFORE:
        raise SystemExit(f'unexpected unmarked predicate inventory: {dict(observed)}')
    selected = [row for row in rows if row.get('statement_id') in EXPECTED_IDS]
    if {row.get('statement_id') for row in selected} != EXPECTED_IDS or len(selected) != len(EXPECTED_IDS):
        raise SystemExit('expected statement IDs are missing or duplicated')
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        known_candidates = {row['candidate_id'] for row in csv.DictReader(f)}
    for row in selected:
        q = row.get('qualifiers') or {}
        if 'relation_candidate' in q or row.get('origin') != 'book':
            raise SystemExit(f'precondition mismatch: {row["statement_id"]}')
        if not row.get('original_quote') or not row.get('source_file') or not q.get('source_line_start') or not q.get('source_line_end'):
            raise SystemExit(f'missing quote or source anchor: {row["statement_id"]}')
        if not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
            raise SystemExit(f'missing endpoint: {row["statement_id"]}')
        if row['subject_candidate_id'] not in known_candidates or row['object_candidate_id'] not in known_candidates:
            raise SystemExit(f'unknown endpoint candidate: {row["statement_id"]}')
    updated_lines = []
    seen = set()
    selected_info = []
    for line in lines:
        if not line.strip():
            updated_lines.append(line)
            continue
        row = json.loads(line)
        if row.get('statement_id') in EXPECTED_IDS:
            old_predicate = row['predicate']
            row['predicate'] = PREDICATE_REWRITES.get(old_predicate, old_predicate)
            row.setdefault('qualifiers', {})['relation_candidate'] = True
            seen.add(row['statement_id'])
            selected_info.append((row['statement_id'], old_predicate, row['predicate']))
            updated_lines.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        else:
            updated_lines.append(line)
    if seen != EXPECTED_IDS:
        raise SystemExit('not all fixed statements were rewritten')
    result = ''.join(updated_lines).encode('utf-8')
    final_rows = [json.loads(line) for line in result.decode('utf-8').splitlines() if line.strip()]
    flagged = [row for row in final_rows if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in flagged)
    if (len(flagged), complete) != (3449, 3435):
        raise SystemExit(f'unexpected totals after update: {len(flagged)} flagged, {complete} complete')
    return original, result, sorted(selected_info)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    original, result, selected = prepare()
    print(json.dumps({'mode': 'apply' if args.apply else 'dry-run', 'count': len(selected), 'predicate_rewrites': [{'from': old, 'to': new} for _, old, new in selected if old != new], 'relation_candidates_after': 3449, 'complete_after': 3435, 'open_after': 14, 'changes': [{'statement_id': sid, 'from': old, 'to': new} for sid, old, new in selected], 'before_sha256': sha256(original), 'after_sha256': sha256(result), 'write': args.apply}, ensure_ascii=False, indent=2))
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
