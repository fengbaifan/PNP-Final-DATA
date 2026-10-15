from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / '04-knowledge' / 'tables' / 'book-statements.jsonl'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_iv.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
SEGMENT = 'chp-7:07_CHP-7_sec_iv:l89-95'

EXPECTED_HASHES = {
    STATEMENTS.name: '26a829c05f821971696a4aed3b98a80eb673e1c9b8535592947a7483c179bbad',
    SOURCE.name: 'd620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p199-20261013')

TRUE_IDS = {
    'st-chp7-p199-choice-hercules-failed-to-convey-thought',
    'st-chp7-p199-english-taste-and-patronage',
    'st-chp7-p199-picture-as-history-instructions',
    'st-chp7-p199-shaftesbury-1713-picture',
    'st-chp7-p199-shaftesbury-civilising-role-of-art',
    'st-chp7-p199-shaftesbury-died-before-order',
    'st-chp7-p199-shaftesbury-emotional-appeal',
    'st-chp7-p199-shaftesbury-satisfied-with-picture',
}

OPEN_ENDPOINT_NOTES = {
    'st-chp7-p199-choice-hercules-failed-to-convey-thought': 'This is Haskell’s assessment of the relationship between the picture and Shaftesbury’s complex ideas; retain the source judgment without asserting independent reception evidence.',
    'st-chp7-p199-english-taste-and-patronage': 'The causal contribution of Shaftesbury’s example and preaching is qualified as “in some measure”; the English audience and individual collections are not enumerated.',
    'st-chp7-p199-shaftesbury-civilising-role-of-art': 'This records Shaftesbury’s attributed theory about art and society as presented by Haskell; it is not an independently verified causal law.',
    'st-chp7-p199-shaftesbury-emotional-appeal': 'Haskell infers a position from Shaftesbury’s informal writings but does not identify a specific text or painting in this sentence.',
    'st-chp7-p199-shaftesbury-satisfied-with-picture': 'The statement preserves Haskell’s report of Shaftesbury’s satisfaction and comparative judgment about theorists and artists; no independent testimony is cited here.',
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = {p: p.read_bytes() for p in (STATEMENTS, SOURCE, PDF)}
    hashes = {p.name: sha256(data) for p, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    actual_unset = {
        row['statement_id'] for row in rows
        if row['segment_id'] == SEGMENT and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if actual_unset != TRUE_IDS:
        raise SystemExit(f'p.199 unset set differs: {sorted(actual_unset ^ TRUE_IDS)}')

    output = []
    for source_row in rows:
        sid = source_row['statement_id']
        if sid not in TRUE_IDS:
            output.append(source_row)
            continue
        row = dict(source_row)
        q = dict(row.get('qualifiers') or {})
        q['relation_candidate'] = True
        q['relation_candidate_note'] = (
            'S2 retains this source-grounded relation, project, or attributed argument as a candidate; '
            'the source’s qualification remains attached, and no formal S6 edge is created.'
        )
        if sid in OPEN_ENDPOINT_NOTES:
            q['open_endpoint_reason'] = OPEN_ENDPOINT_NOTES[sid]
        row['qualifiers'] = q
        output.append(row)

    counts = {
        'statements': len(output),
        'True': sum(row.get('qualifiers', {}).get('relation_candidate') is True for row in output),
        'False': sum(row.get('qualifiers', {}).get('relation_candidate') is False for row in output),
        'unset': sum(row.get('qualifiers', {}).get('relation_candidate') is None for row in output),
    }
    if counts != {'statements': 14189, 'True': 8719, 'False': 3431, 'unset': 2039}:
        raise SystemExit(f'unexpected post-counts: {counts}')
    after = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    after_hash = sha256(after)
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'segment': SEGMENT,
        'classified_true': len(TRUE_IDS),
        'classified_false': 0,
        'post_counts': counts,
        'before_sha256': hashes,
        'after_statement_sha256': after_hash,
        'backup': str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    BACKUP.write_bytes(raw[STATEMENTS])
    atomic_write(STATEMENTS, after)
    if sha256(STATEMENTS.read_bytes()) != after_hash:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
