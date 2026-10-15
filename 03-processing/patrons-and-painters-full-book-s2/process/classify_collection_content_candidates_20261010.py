from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
TABLE = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
MENTIONS = TABLES / 'mentions.csv'
SOURCE = ROOT / '02-sources/02-Markdown/02_CHP-2_sec_i.md'
BACKUP = TABLE.with_name(TABLE.name + '.bak-s2-handoff-collection-group-classification-20261010')
EXPECTED_TABLE_SHA256 = 'eb9d9fd3682c6f9fbfc314e0612ebbe3cbc5d10de153c50ffaa5bf1e550fd014'

TARGETS = {
    'st-chp2-seci-l95-106-antique-sculpture-holdings': {
        'subject': 'cand-1200',
        'object': 'cand-4314',
        'mention_id': 'm-chp2-seci-l95-106-0029',
        'surface': 'antique sculpture',
        'source_fragment': 'with antique sculpture',
        'note': (
            'S2 relation candidate: the source explicitly connects Vincenzo Giustiniani to the '
            'already registered, unnamed antique-sculpture group in his palace and country house. '
            'No individual sculpture, count, ownership transfer, or formal S6 edge is asserted; '
            'the group type remains unresolved.'
        ),
    },
    'st-chp2-seci-l95-106-collection-holdings': {
        'subject': 'cand-1200',
        'object': 'cand-4313',
        'mention_id': 'm-chp2-seci-l95-106-0030',
        'surface': 'collections of paintings',
        'source_fragment': 'one of the most remarkable collections of paintings',
        'note': (
            'S2 relation candidate: the source connects Vincenzo Giustiniani to the already '
            'registered painting-collection candidate. The collection is not an individual work; '
            'its type and membership remain unresolved, and no formal S6 ownership edge is asserted.'
        ),
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode('utf-8-sig').splitlines() if line.strip()]


def prepare() -> tuple[bytes, bytes, dict]:
    original = TABLE.read_bytes()
    before_hash = sha256(original)
    if before_hash != EXPECTED_TABLE_SHA256:
        raise SystemExit(f'table changed: expected {EXPECTED_TABLE_SHA256}, got {before_hash}')

    rows = read_jsonl(original)
    by_id: dict[str, dict] = {}
    for row in rows:
        sid = row.get('statement_id')
        if sid in TARGETS:
            if sid in by_id:
                raise SystemExit(f'duplicate statement ID: {sid}')
            by_id[sid] = row
    if set(by_id) != set(TARGETS):
        raise SystemExit(f'target inventory mismatch: {sorted(by_id)}')

    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        candidates = {r['candidate_id']: r for r in csv.DictReader(f)}
    with MENTIONS.open(encoding='utf-8-sig', newline='') as f:
        mentions = {r['mention_id']: r for r in csv.DictReader(f)}
    source_lines = SOURCE.read_text(encoding='utf-8').splitlines()

    for sid, expected in TARGETS.items():
        row = by_id[sid]
        q = row.get('qualifiers') or {}
        if (row.get('predicate'), row.get('segment_id'), row.get('source_file')) != (
            'collection_contents_reported',
            'chp-2:02_CHP-2_sec_i:l95-106',
            '02-sources/02-Markdown/02_CHP-2_sec_i.md',
        ):
            raise SystemExit(f'predicate/source mismatch: {sid}')
        if (row.get('subject_candidate_id'), row.get('object_candidate_id')) != (
            expected['subject'], expected['object']
        ):
            raise SystemExit(f'endpoint mismatch: {sid}')
        if q.get('relation_candidate') is not None:
            raise SystemExit(f'relation_candidate is already classified: {sid}')
        if (q.get('source_line_start'), q.get('source_line_end')) != (100, 100):
            raise SystemExit(f'source line mismatch: {sid}')
        if expected['source_fragment'] not in row.get('original_quote', ''):
            raise SystemExit(f'quote anchor mismatch: {sid}')
        if expected['subject'] not in candidates or expected['object'] not in candidates:
            raise SystemExit(f'candidate FK missing: {sid}')
        candidate = candidates[expected['object']]
        if candidate.get('status') != 'open' or candidate.get('suggested_type'):
            raise SystemExit(f'object candidate state changed: {expected["object"]}')
        mention = mentions.get(expected['mention_id'])
        if not mention or (mention.get('segment_id'), mention.get('candidate_id'), mention.get('surface_form')) != (
            row['segment_id'], expected['object'], expected['surface']
        ):
            raise SystemExit(f'mention mapping mismatch: {sid}')
        if not source_lines[99].startswith('Genoese nobleman') or expected['source_fragment'] not in source_lines[99]:
            raise SystemExit(f'current S0 line does not support {sid}')

    output_lines = []
    seen = set()
    for line in original.decode('utf-8-sig').splitlines(keepends=True):
        if not line.strip():
            output_lines.append(line)
            continue
        row = json.loads(line)
        sid = row.get('statement_id')
        if sid in TARGETS:
            q = row.setdefault('qualifiers', {})
            q['relation_candidate'] = True
            q['relation_candidate_note'] = TARGETS[sid]['note']
            seen.add(sid)
            output_lines.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        else:
            output_lines.append(line)
    if seen != set(TARGETS):
        raise SystemExit('not all target statements were updated')

    result = ''.join(output_lines).encode('utf-8')
    final_rows = read_jsonl(result)
    flags = collections.Counter(str((r.get('qualifiers') or {}).get('relation_candidate')).lower() for r in final_rows)
    true_rows = [r for r in final_rows if (r.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(r.get('subject_candidate_id') and r.get('object_candidate_id')) for r in true_rows)
    if (flags['true'], complete, len(true_rows) - complete) != (3473, 3459, 14):
        raise SystemExit(f'unexpected post-state: true={flags["true"]}, complete={complete}, open={len(true_rows)-complete}')
    return original, result, {
        'selected_ids': sorted(TARGETS),
        'true_relation_candidates': flags['true'],
        'complete_endpoints': complete,
        'open_endpoints': len(true_rows) - complete,
        'before_sha256': before_hash,
        'after_sha256': sha256(result),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after all checks; default is dry-run')
    args = parser.parse_args()
    original, result, report = prepare()
    print(json.dumps({'mode': 'apply' if args.apply else 'dry-run', **report}, ensure_ascii=False, indent=2))
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
