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
BACKUP = TABLE.with_name(TABLE.name + '.bak-s2-handoff-creative-relational-claims-20261010')
EXPECTED_TABLE_SHA256 = '8631208328c98970352709f3110891596ede5567ef4812aebe3e78b5eb517cd9'
EXPECTED_PREDICATES = {
    'painted': 5,
    'dedicated_to': 3,
    'commission_scope_includes': 3,
    'close_friendship_reported': 3,
    'introduced_artist_to_side_chapels': 3,
    'patronage_relationship_reported': 3,
    'authored_by_reported': 2,
}
REWRITES = {'painted': 'creator_of', 'patronage_relationship_reported': 'patronized', 'authored_by_reported': 'authored_by'}
EXPECTED_IDS = {
    'st-chp3-secii-p76-note3-domenichino-allegories',
    'st-chp3-seciv-l3-6-pietro-small-sacristy-fresco',
    'st-chp3-seciv-l48-56-apse-conch-painted',
    'st-chp3-seciv-l8-14-assumption-apse',
    'st-chp3-seciv-l8-14-four-prophets-pendentives',
    'st-chp4-sec-ii-p104-footnote3-olina-dedicated-to-cassiano',
    'st-chp7-p193-n2-boschini-dedication',
    'st-fm-title-dedication',
    'st-chp3-seciv-l35-46-scope-includes-dome',
    'st-chp3-seciv-l35-46-scope-includes-main-vault',
    'st-chp3-seciv-l35-46-scope-includes-transept-vaults',
    'st-chp4-sec-ii-l10-13-cassiano-close-friend-alessandro',
    'st-chp4-sec-ii-l10-13-cassiano-close-friend-francesco',
    'st-chp4-sec-ii-l3-8-cassiano-galileo-friendship',
    'st-chp3-secii-l6-17-pious-ladies-introduced-ciampelli',
    'st-chp3-secii-l6-17-pious-ladies-introduced-pulzone',
    'st-chp3-secii-l6-17-pious-ladies-introduced-zuccari',
    'st-chp2-seci-l95-106-benedetto-caravaggio-support',
    'st-chp2-seci-l95-106-first-serious-patron',
    'st-chp2-seci-l95-106-vincenzo-caravaggio-support',
    'st-chp2-seci-l95-106-essay-authored',
    'st-chp2-seci-l95-106-hopf-authorship',
}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def prepare() -> tuple[bytes, bytes, list[tuple[str, str, str]]]:
    original = TABLE.read_bytes()
    if sha256(original) != EXPECTED_TABLE_SHA256:
        raise SystemExit(f'table changed: expected {EXPECTED_TABLE_SHA256}, got {sha256(original)}')
    lines = original.decode('utf-8').splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    pool = [row for row in rows if row.get('predicate') in EXPECTED_PREDICATES and row.get('subject_candidate_id') and row.get('object_candidate_id') and 'relation_candidate' not in (row.get('qualifiers') or {})]
    observed = collections.Counter(row['predicate'] for row in pool)
    if dict(observed) != EXPECTED_PREDICATES:
        raise SystemExit(f'unexpected unmarked predicate inventory: {dict(observed)}')
    selected = [row for row in rows if row.get('statement_id') in EXPECTED_IDS]
    if {row.get('statement_id') for row in selected} != EXPECTED_IDS or len(selected) != len(EXPECTED_IDS):
        raise SystemExit('expected statement IDs are missing or duplicated')
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        known = {row['candidate_id'] for row in csv.DictReader(f)}
    for row in selected:
        q = row.get('qualifiers') or {}
        if 'relation_candidate' in q or row.get('origin') != 'book':
            raise SystemExit(f'precondition mismatch: {row["statement_id"]}')
        if not row.get('original_quote') or not row.get('source_file') or not q.get('source_line_start') or not q.get('source_line_end'):
            raise SystemExit(f'missing source anchor: {row["statement_id"]}')
        if not row.get('subject_candidate_id') or not row.get('object_candidate_id') or row['subject_candidate_id'] not in known or row['object_candidate_id'] not in known:
            raise SystemExit(f'missing or unknown endpoint: {row["statement_id"]}')
    updated = []
    seen = set()
    changes = []
    for line in lines:
        if not line.strip():
            updated.append(line)
            continue
        row = json.loads(line)
        if row.get('statement_id') in EXPECTED_IDS:
            before = row['predicate']
            row['predicate'] = REWRITES.get(before, before)
            row.setdefault('qualifiers', {})['relation_candidate'] = True
            seen.add(row['statement_id'])
            changes.append((row['statement_id'], before, row['predicate']))
            updated.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        else:
            updated.append(line)
    if seen != EXPECTED_IDS:
        raise SystemExit('not all selected rows were rewritten')
    result = ''.join(updated).encode('utf-8')
    final = [json.loads(line) for line in result.decode('utf-8').splitlines() if line.strip()]
    flagged = [row for row in final if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in flagged)
    if (len(flagged), complete) != (3471, 3457):
        raise SystemExit(f'unexpected final counts: {len(flagged)} true, {complete} complete')
    return original, result, sorted(changes)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    original, result, changes = prepare()
    print(json.dumps({'mode': 'apply' if args.apply else 'dry-run', 'selected_count': len(changes), 'predicate_counts': EXPECTED_PREDICATES, 'normalizations': [{'from': old, 'to': new} for _, old, new in changes if old != new], 'after': {'true': 3471, 'complete': 3457, 'open': 14}, 'before_sha256': sha256(original), 'after_sha256': sha256(result), 'write': args.apply}, ensure_ascii=False, indent=2))
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
