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
SEGMENT = 'chp-7:07_CHP-7_sec_iv:l77-87'
RETURN_ID = 'st-chp7-p197-exeter-return-verrio-open'
RESOLUTION_ID = 'st-chp7-p198-exeter-employs-verrio-burghley'

EXPECTED_HASHES = {
    STATEMENTS.name: 'd4b876a21e5fb06629ac9a61a9b928ae84158df29a382148c117ce84696b142e',
    SOURCE.name: 'd620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p198-20261013')

TRUE_IDS = {
    'st-chp7-p198-closterman-instructions-advice',
    'st-chp7-p198-closterman-search-sculptor',
    'st-chp7-p198-closterman-shaftesbury-portrait',
    'st-chp7-p198-english-tourist-collecting',
    'st-chp7-p198-enthusiasm-and-shaftesbury-theory',
    'st-chp7-p198-exeter-collecting-role',
    'st-chp7-p198-exeter-introduced-maratta',
    'st-chp7-p198-guidi-drawings-project-failed',
    'st-chp7-p198-haskell-on-shaftesbury-executant',
    'st-chp7-p198-shaftesbury-buys-pictures-for-friends',
    'st-chp7-p198-shaftesbury-de-matteis-choice-hercules',
    'st-chp7-p198-shaftesbury-endorsed-letter-inference',
    'st-chp7-p198-shaftesbury-italy-visit',
    'st-chp7-p198-shaftesbury-political-sympathies',
    'st-chp7-p198-shaftesbury-quoted-aesthetic-instruction',
    'st-chp7-p198-shaftesbury-retires-naples',
    'st-chp7-p198-shaftesbury-verrio-programme',
    'st-chp7-p198-shaftesbury-welcomed-patronage',
    'st-chp7-p198-virtues-subject-choice',
}

OPEN_ENDPOINT_NOTES = {
    'st-chp7-p198-closterman-instructions-advice': 'The artists Shaftesbury might later employ are not identified; the statement records Closterman’s advice, not a commission.',
    'st-chp7-p198-english-tourist-collecting': 'This summarizes accounts in Italian biographies about an unnamed group of English visitors; individuals and specific studio invitations are not assigned here.',
    'st-chp7-p198-enthusiasm-and-shaftesbury-theory': 'The causal link between indiscriminate collecting enthusiasm and Shaftesbury’s theorizing is Haskell’s interpretation; preserve that attribution.',
    'st-chp7-p198-exeter-collecting-role': 'Haskell’s significance assessment is a summary of Exeter’s role; the specific acts are recorded in adjacent statements, and no single institution or collecting object is named here.',
    'st-chp7-p198-exeter-introduced-maratta': 'The members of the nobility are not individually identified.',
    'st-chp7-p198-haskell-on-shaftesbury-executant': 'This is Haskell’s interpretation of Shaftesbury’s conception as applied to an actual creation; retain the source judgment and do not treat it as an independently verified statement by the artist.',
    'st-chp7-p198-shaftesbury-buys-pictures-for-friends': 'The pictures and Shaftesbury’s English friends are not individually identified.',
    'st-chp7-p198-shaftesbury-endorsed-letter-inference': '“Must have endorsed” is Haskell’s inference from the failed project; no direct endorsement or response is cited.',
    'st-chp7-p198-shaftesbury-verrio-programme': 'Haskell qualifies Shaftesbury’s participation as probable; no independent documentary evidence is supplied in this passage.',
    'st-chp7-p198-virtues-subject-choice': 'The proposed series of Virtues was not made; preserve the choice as a project intention and Haskell’s characterization, not as a completed sculpture.',
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
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_ids = TRUE_IDS
    actual_unset = {
        row['statement_id'] for row in rows
        if row['segment_id'] == SEGMENT and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if actual_unset != expected_ids:
        raise SystemExit(f'p.198 unset set differs: {sorted(actual_unset ^ expected_ids)}')
    bridge = by_id[RETURN_ID]
    resolution = by_id[RESOLUTION_ID]
    if ((bridge.get('qualifiers') or {}).get('relation_candidate') is not False
            or (bridge.get('qualifiers') or {}).get('continuation_resolved_by_statement_id') != RESOLUTION_ID
            or (resolution.get('qualifiers') or {}).get('continuation_of_statement_id') != RETURN_ID):
        raise SystemExit('p.197–198 continuation deduplication link changed')

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
            'S2 retains this source-grounded historical, intellectual, or author-attributed claim as a candidate; '
            'its scope and uncertainty remain attached, and no formal S6 edge is created.'
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
    if counts != {'statements': 14189, 'True': 8711, 'False': 3431, 'unset': 2047}:
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
