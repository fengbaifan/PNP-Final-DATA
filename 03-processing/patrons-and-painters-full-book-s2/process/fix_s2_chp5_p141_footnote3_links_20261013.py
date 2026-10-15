import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / '04-knowledge/tables/book-statements.jsonl'
EXPECTED_SHA256 = 'e4869aec58ffd375d4277e9cff2c18198e57eb913ab075e90116c60489fdcb18'
BACKUP_TAG = '.bak-s2-chp5-p141-footnote3-20261013'
TARGETS = {
    'st-chp5-p141-malvasia-may-have-doctored-letters',
    'st-chp5-p141-sacchi-asks-albani-opinion',
}
SOURCE_ID = 'st-chp5-p141-1651-sacchi-albani-letter-exchange'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    actual = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    if actual != EXPECTED_SHA256:
        raise SystemExit(f'precondition failed: statements sha256={actual}')
    rows = [json.loads(s) for s in TABLE.read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    by_id = {r['statement_id']: r for r in rows}
    if not (TARGETS | {SOURCE_ID}).issubset(by_id):
        raise SystemExit('missing p.141 statement or footnote source')
    source_q = by_id[SOURCE_ID].get('qualifiers', {})
    if source_q.get('footnote_target_line') != 158 or source_q.get('footnote_link_status') != 'linked':
        raise SystemExit('footnote 3 source link is not resolved to L158')
    keys = ('footnote_target_line', 'footnote_link_status', 'citation_segment_id',
            'citation_source_line_start', 'citation_source_line_end', 'footnote_refs')
    fields = {key: json.loads(json.dumps(source_q[key], ensure_ascii=False)) for key in keys}
    for sid in TARGETS:
        q = by_id[sid].setdefault('qualifiers', {})
        if q.get('footnote_target_line') is not None:
            raise SystemExit(f'{sid} already has a footnote link; refusing to overwrite')
        q.update(fields)
    if args.apply:
        backup = TABLE.with_name(TABLE.name + BACKUP_TAG)
        if backup.exists():
            raise SystemExit(f'backup already exists: {backup.name}')
        temp = TABLE.with_name(TABLE.name + '.tmp-s2-chp5-p141-footnote3')
        if temp.exists():
            raise SystemExit(f'temporary output already exists: {temp.name}')
        shutil.copy2(TABLE, backup)
        try:
            temp.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8-sig')
            os.replace(temp, TABLE)
        finally:
            if temp.exists():
                temp.unlink()
        print('applied missing footnote 3 links to two p.141 claims')
        print('backup:', backup.name)
    else:
        print('PREVIEW only; no table writes')
    for sid in sorted(TARGETS):
        print(sid, fields)


if __name__ == '__main__':
    main()
