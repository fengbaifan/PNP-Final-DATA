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
SEGMENT = 'chp-7:07_CHP-7_sec_iv:l63-75'
RETURN_ID = 'st-chp7-p197-exeter-return-verrio-open'
RESOLUTION_ID = 'st-chp7-p198-exeter-employs-verrio-burghley'

EXPECTED_HASHES = {
    STATEMENTS.name: '45e21ebdf8d811db88d41dd6c5ca58f52a58b08a7911530a37679cf5a815f693',
    SOURCE.name: 'd620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p197-20261013')

TRUE_IDS = {
    'st-chp7-p197-business-visitors-more-enterprising',
    'st-chp7-p197-dolci-giordano-contrast',
    'st-chp7-p197-exeter-commissioned-across-visited-cities',
    'st-chp7-p197-exeter-italian-visits',
    'st-chp7-p197-exeter-larger-patronage-scale',
    'st-chp7-p197-exeter-ordered-fifteen-giordano',
    'st-chp7-p197-exeter-ordered-nine-dolci',
    'st-chp7-p197-exeter-unique-commission-scale',
    'st-chp7-p197-finch-commissioned-dolci',
    'st-chp7-p197-finch-gifted-royal-family',
    'st-chp7-p197-finch-resident-florence',
    'st-chp7-p197-giordano-frescoes-riccardi',
    'st-chp7-p197-isham-commissions-in-rome',
    'st-chp7-p197-isham-copies-after-famous-works',
    'st-chp7-p197-isham-italian-tour',
    'st-chp7-p197-isham-mythological-pictures',
    'st-chp7-p197-isham-portrait-maratta',
    'st-chp7-p197-monnot-tomb',
    'st-chp7-p197-queen-anne-employs-cassana',
    'st-chp7-p197-tourist-patronage-comparison',
    'st-chp7-p197-tourist-portrait-examples',
    'st-chp7-p197-tourists-seek-portraits',
    'st-chp7-p197-verrio-doubtless-greeted-cassana',
}

FALSE_NOTES = {
    'st-chp7-p197-england-lacks-italian-painting': (
        'This is Haskell’s broad characterization of the national art context, without an identified '
        'collection, work, or acquisition relation. Preserve it as a source claim; do not turn it '
        'into a country-to-art edge.'
    ),
    'st-chp7-p197-exeter-aesthetic-experience': (
        '“A glutton for every kind of aesthetic experience” is Haskell’s figurative characterization '
        'of Exeter, not a distinct relation among identified entities.'
    ),
    'st-chp7-p197-exeter-taste-breadth': (
        'This is Haskell’s inference about the breadth or inconsistency of Exeter’s taste, drawn from '
        'the preceding artist contrast; retain the interpretation without creating a separate relation.'
    ),
    'st-chp7-p197-isham-love-affairs-and-debt': (
        'The passage gives biographical characterization but identifies no partner, creditor, or '
        'specific transaction that forms a relation candidate.'
    ),
    RETURN_ID: (
        'This row is the p.197 opening fragment of the cross-page sentence. The complete Exeter–Verrio '
        'employment relation is represented by the p.198 continuation statement; classifying this '
        'bridge row separately would duplicate that relation.'
    ),
}

OPEN_ENDPOINT_NOTES = {
    'st-chp7-p197-business-visitors-more-enterprising': '“More enterprising” is Haskell’s comparison of an unnamed subset of business visitors with the portrait-focused tourist majority; the specific actions are separately recorded in the following statements.',
    'st-chp7-p197-dolci-giordano-contrast': 'Haskell says the two artists “seem” to have been Exeter’s favourites; preserve the inference and do not convert it into independently verified preference.',
    'st-chp7-p197-exeter-commissioned-across-visited-cities': 'The statement generalizes across the cities Exeter visited; the city-specific artist associations are recorded separately, and this row does not identify every commission.',
    'st-chp7-p197-exeter-ordered-fifteen-giordano': 'The number and artist are stated, but the fifteen individual paintings are not titled or otherwise identified here.',
    'st-chp7-p197-exeter-ordered-nine-dolci': 'The number and artist are stated, but the nine individual paintings are not titled or otherwise identified here.',
    'st-chp7-p197-exeter-unique-commission-scale': 'The “no Englishman” and “few ever” quantifiers are Haskell’s broad comparison; no complete comparison set is provided in this passage.',
    'st-chp7-p197-finch-commissioned-dolci': 'The religious pictures and individual commission dates are not specified.',
    'st-chp7-p197-finch-gifted-royal-family': 'The recipients are described only as the royal family and the gifted pictures are not individually identified.',
    'st-chp7-p197-isham-copies-after-famous-works': 'The copied works are described by artist names and category; no individual original or copy is identified.',
    'st-chp7-p197-isham-mythological-pictures': 'The subject type and named painters are supplied, but the individual pictures are not titled in this passage.',
    'st-chp7-p197-isham-italian-tour': 'The tutor and most visited towns remain unnamed in this statement; the relative duration and 1676 departure are preserved as stated.',
    'st-chp7-p197-tourist-portrait-examples': 'The three tourists are named, but the leading artists are not; the Rome/Naples/Florence assignments are not made individually in the sentence.',
    'st-chp7-p197-tourists-seek-portraits': 'This is Haskell’s group-level statement about the majority of tourists; it does not identify each visitor or portrait.',
    'st-chp7-p197-verrio-doubtless-greeted-cassana': 'Haskell marks the greeting as “doubtless”; preserve this as his inference, not a directly documented meeting.',
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
    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    if source_lines[74].strip() != 'Calandrucci. No Englishman had ever commissioned contemporary Italian painting on such a scale before; few were ever to do so again. He also persuaded the FrancoItalian sculptor Pierre Monnot to make a tomb for him6 and when back again at':
        raise SystemExit('p.197 source line guard failed')

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_ids = TRUE_IDS | set(FALSE_NOTES)
    actual_unset = {
        row['statement_id'] for row in rows
        if row['segment_id'] == SEGMENT and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if actual_unset != expected_ids:
        raise SystemExit(f'p.197 unset set differs: {sorted(actual_unset ^ expected_ids)}')
    bridge = by_id[RETURN_ID]
    resolved = by_id.get(RESOLUTION_ID)
    if (bridge['segment_id'] != SEGMENT
            or (bridge.get('qualifiers') or {}).get('continuation_status') != 'completed'
            or (bridge.get('qualifiers') or {}).get('continuation_to_segment_id') != 'chp-7:07_CHP-7_sec_iv:l77-87'
            or resolved is None
            or (resolved.get('qualifiers') or {}).get('continuation_of_statement_id') != RETURN_ID
            or (resolved.get('qualifiers') or {}).get('relation_candidate') is not True):
        raise SystemExit('p.197–198 continuation relation changed since review')

    output = []
    for source_row in rows:
        sid = source_row['statement_id']
        if sid not in expected_ids:
            output.append(source_row)
            continue
        row = dict(source_row)
        q = dict(row.get('qualifiers') or {})
        if sid in TRUE_IDS:
            q['relation_candidate'] = True
            q['relation_candidate_note'] = (
                'S2 retains the source-grounded historical relation or group-level claim as a candidate; '
                'the source attribution and uncertainty remain attached, and no formal S6 edge is created.'
            )
            if sid in OPEN_ENDPOINT_NOTES:
                q['open_endpoint_reason'] = OPEN_ENDPOINT_NOTES[sid]
        else:
            q['relation_candidate'] = False
            q['relation_candidate_note'] = FALSE_NOTES[sid]
            if sid == RETURN_ID:
                q['continuation_resolved_by_statement_id'] = RESOLUTION_ID
        row['qualifiers'] = q
        output.append(row)

    counts = {
        'statements': len(output),
        'True': sum(row.get('qualifiers', {}).get('relation_candidate') is True for row in output),
        'False': sum(row.get('qualifiers', {}).get('relation_candidate') is False for row in output),
        'unset': sum(row.get('qualifiers', {}).get('relation_candidate') is None for row in output),
    }
    if counts != {'statements': 14189, 'True': 8692, 'False': 3431, 'unset': 2066}:
        raise SystemExit(f'unexpected post-counts: {counts}')
    after = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    after_hash = sha256(after)
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'segment': SEGMENT,
        'classified_true': len(TRUE_IDS),
        'classified_false': len(FALSE_NOTES),
        'cross_page_duplicate_linked_to': RESOLUTION_ID,
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
