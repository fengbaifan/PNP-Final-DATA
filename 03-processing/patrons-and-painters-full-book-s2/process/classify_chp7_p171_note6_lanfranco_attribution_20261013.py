from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
SOURCE = ROOT / '02-sources/02-Markdown/07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources/01-book/CHP-7.pdf'
TARGET = 'st-chp7-p171-n6-series-partly-lanfranco'
EXPECTED = {
    'book-statements.jsonl': '7c7ede4cf927c79b3ae37d892b06cebdde6e38fb21d53f2e273d9f24fa23e151',
    '07_CHP-7_sec_i.md': 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    'CHP-7.pdf': 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p171-note6-lanfranco-20261013')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before = STATEMENTS.read_bytes()
    actual = {
        'book-statements.jsonl': sha256(before),
        '07_CHP-7_sec_i.md': sha256(SOURCE.read_bytes()),
        'CHP-7.pdf': sha256(PDF.read_bytes()),
    }
    if actual != EXPECTED:
        raise SystemExit(f'input hashes changed: {actual}')
    rows = [json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip()]
    target = [row for row in rows if row['statement_id'] == TARGET]
    if len(target) != 1:
        raise SystemExit(f'expected exactly one target statement, found {len(target)}')
    row = dict(target[0])
    q = dict(row.get('qualifiers') or {})
    if (row.get('predicate') != 'partially_attributed_to'
            or row.get('subject_candidate_id') != 'cand-7003'
            or row.get('object_candidate_id') != 'cand-1359'
            or q.get('source_line_start') != 300
            or q.get('relation_candidate') is not None):
        raise SystemExit('target statement changed since review')
    q['relation_candidate'] = True
    q['relation_candidate_note'] = 'S2 relation candidate: the printed footnote says only some scenes in the series are by Lanfranco; this does not attribute the whole series to him.'
    row['qualifiers'] = q
    output = [row if item['statement_id'] == TARGET else item for item in rows]
    counts = {
        True: sum((item.get('qualifiers') or {}).get('relation_candidate') is True for item in output),
        False: sum((item.get('qualifiers') or {}).get('relation_candidate') is False for item in output),
        'unset': sum((item.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for item in output),
    }
    if (len(output), counts) != (14187, {True: 8420, False: 3419, 'unset': 2348}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    after = ('\n'.join(json.dumps(item, ensure_ascii=False, separators=(',', ':')) for item in output) + '\n').encode('utf-8')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'statement_id': TARGET,
        'decision': True,
        'basis': 'Printed p.171 footnote 6 states “some of which are by Lanfranco”; attribution is partial.',
        'counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
        'before_sha256': actual,
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
