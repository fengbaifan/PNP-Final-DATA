from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
CANDIDATES = TABLES / 'entity-candidates.csv'
STATEMENTS = TABLES / 'book-statements.jsonl'
EXPECTED = {
    CANDIDATES.name: '1f95394640eb6971cce023a23633596bf28f44d2a79df839dbed1e3a88ad8451',
    STATEMENTS.name: '464f6c1a216bd42a38c10710238765d6a0139f76b36a57de431606be2f74b065',
}
REQUOTE_IDS = {
    'st-chp2-seci-l95-106-cambiaso-collection',
    'st-chp2-seci-l95-106-carracci-collection',
    'st-chp2-seci-l95-106-venetian-collection',
    'st-chp2-seci-l95-106-other-paintings-location',
}
BACKUPS = {
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + '.bak-s2-handoff-collection-group-anchor-fix-20261010'),
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-handoff-collection-group-anchor-fix-20261010'),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare() -> tuple[dict[Path, bytes], dict[Path, bytes], dict]:
    before = {path: path.read_bytes() for path in (CANDIDATES, STATEMENTS)}
    hashes = {path.name: digest(data) for path, data in before.items()}
    if hashes != EXPECTED:
        raise SystemExit(f'table hash changed: {hashes}')

    old_ref = b'chp-2:02_CHP-2_sec_i:l108-119#L113-L114'
    if before[CANDIDATES].count(old_ref) != 1:
        raise SystemExit('unexpected candidate source ref count')
    candidate_bytes = before[CANDIDATES].replace(old_ref, b'chp-2:02_CHP-2_sec_i:l108-119#L113')

    output_lines = []
    seen = set()
    for raw in before[STATEMENTS].decode('utf-8').splitlines():
        row = json.loads(raw)
        sid = row.get('statement_id')
        if sid in REQUOTE_IDS:
            q = dict(row.get('qualifiers') or {})
            if q.get('source_line_start') != 102 or q.get('source_line_end') != 102:
                raise SystemExit(f'unexpected prior source line values: {sid}')
            q['source_line_start'] = 101
            q['source_line_end'] = 102
            row['qualifiers'] = q
            seen.add(sid)
        output_lines.append(json.dumps(row, ensure_ascii=False, separators=(',', ':')))
    if seen != REQUOTE_IDS:
        raise SystemExit(f'missing rewritten statements: {REQUOTE_IDS - seen}')
    statement_bytes = ('\n'.join(output_lines) + '\n').encode('utf-8')
    after = {CANDIDATES: candidate_bytes, STATEMENTS: statement_bytes}
    return before, after, {
        'corrected_statement_ids': sorted(REQUOTE_IDS),
        'candidate_source_ref': 'chp-2:02_CHP-2_sec_i:l108-119#L113',
        'before_sha256': hashes,
        'after_sha256': {path.name: digest(data) for path, data in after.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before, after, report = prepare()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    for path, backup in BACKUPS.items():
        if backup.exists():
            raise SystemExit(f'backup already exists: {backup}')
        shutil.copy2(path, backup)
    for path, data in after.items():
        path.write_bytes(data)
    actual = {path.name: digest(path.read_bytes()) for path in after}
    expected = {path.name: digest(data) for path, data in after.items()}
    if actual != expected:
        raise SystemExit(f'write verification failed: {actual}')
    print('applied; recovery copies written; hashes verified')


if __name__ == '__main__':
    main()
