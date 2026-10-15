from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + '.bak-s2-handoff-chp4-p112-citations-20261010'
)
BOOK_ID = 'cand-2962'
EXPECTED_SHA256 = 'c6005898331c3b242533bba97253551813f47e3fdf55c99e9cfb7307b811405e'

# Archive targets are selected from the literal footnote text. The old subject
# endpoint is preserved as topical context, not treated as the cited work.
TARGETS = {
    'st-chp4-sec-ii-notes-p112-fn1-passeri': {
        'old_subject': 'cand-1856',
        'old_object': 'cand-5749',
        'archive': 'cand-5749',
        'context': 'cand-1856',
        'quote': '1 Passeri, p. 187.',
        'marker': '1',
    },
    'st-chp4-sec-ii-notes-p112-fn2-passeri': {
        'old_subject': 'cand-1856',
        'old_object': 'cand-5749',
        'archive': 'cand-5749',
        'context': 'cand-1856',
        'quote': '2 ibid., p. 186.',
        'marker': '2',
    },
    'st-chp4-sec-ii-notes-p112-fn3-lumbroso': {
        'old_subject': 'cand-5626',
        'old_object': 'cand-5683',
        'archive': 'cand-5683',
        'context': 'cand-5626',
        'quote': '3 Lumbroso, p. 211.',
        'marker': '3',
    },
    'st-chp4-sec-ii-notes-p112-fn4-poussin-correspondance': {
        'old_subject': 'cand-4634',
        'old_object': 'cand-1764',
        'archive': 'cand-4634',
        'context': 'cand-1764',
        'quote': '4 Poussin: Correspondance, p. 34.',
        'marker': '4',
    },
    'st-chp4-sec-ii-notes-p112-fn5-lumbroso': {
        'old_subject': 'cand-5626',
        'old_object': 'cand-5683',
        'archive': 'cand-5683',
        'context': 'cand-5626',
        'quote': '5 Lumbroso, p. 185.',
        'marker': '5',
    },
    'st-chp4-sec-ii-notes-p112-fn7-lumbroso': {
        'old_subject': 'cand-5626',
        'old_object': 'cand-5683',
        'archive': 'cand-5683',
        'context': 'cand-5626',
        'quote': '7 Lumbroso, p. 202.',
        'marker': '7',
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare() -> tuple[bytes, bytes, dict]:
    before = STATEMENTS.read_bytes()
    before_hash = sha256(before)
    if before_hash != EXPECTED_SHA256:
        raise SystemExit(f'statement table hash changed: {before_hash}')

    lines = before.decode('utf-8').splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('duplicate statement IDs in source table')
    if set(TARGETS) - set(by_id):
        raise SystemExit(f'missing target statements: {sorted(set(TARGETS) - set(by_id))}')

    candidate_rows = {}
    with (TABLES / 'entity-candidates.csv').open(encoding='utf-8-sig', newline='') as f:
        import csv

        candidate_rows = {row['candidate_id']: row for row in csv.DictReader(f)}
    if candidate_rows.get(BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('book candidate is absent or not archive typed')

    output = []
    changed = []
    expected_segment = 'chp-4:04_CHP-4_sec_ii:l232-308'
    for row in rows:
        spec = TARGETS.get(row['statement_id'])
        if not spec:
            output.append(row)
            continue
        q = dict(row.get('qualifiers') or {})
        if (
            row.get('predicate') != 'citation_source'
            or row.get('subject_candidate_id') != spec['old_subject']
            or row.get('object_candidate_id') != spec['old_object']
            or row.get('original_quote') != spec['quote']
            or row.get('segment_id') != expected_segment
            or row.get('origin') != 'book'
            or q.get('relation_candidate') is not None
            or q.get('source_line_start') != 279 + int(spec['marker'])
            or q.get('source_line_end') != 279 + int(spec['marker'])
        ):
            raise SystemExit(f'source row changed or already classified: {row["statement_id"]}')
        archive = candidate_rows.get(spec['archive'])
        context = candidate_rows.get(spec['context'])
        if not archive or archive.get('suggested_type') != 'archive':
            raise SystemExit(f'cited target is not archive typed: {row["statement_id"]}')
        if not context:
            raise SystemExit(f'context candidate is missing: {row["statement_id"]}')

        old_claim = str(q.get('claim') or '').strip()
        if not old_claim:
            raise SystemExit(f'claim missing: {row["statement_id"]}')
        row = dict(row)
        row.update({
            'subject_candidate_id': BOOK_ID,
            'object_candidate_id': spec['archive'],
            'predicate': 'cites',
        })
        q.update({
            'claim': (
                f"Haskell’s book cites {archive['canonical_name']} in footnote "
                f"{spec['marker']}. The note’s original topical context is: {old_claim}"
            ),
            'citation_context_candidate_id': spec['context'],
            'text_layer': 'bibliographic citation',
            'relation_candidate': True,
            'relation_candidate_note': (
                'S2 cites candidate: the footnote explicitly cites this archive from '
                'Haskell’s book. The citation records a bibliographic link and does not '
                'independently validate the cited source’s claims; no formal S6 edge is created.'
            ),
        })
        row['qualifiers'] = q
        output.append(row)
        changed.append({
            'statement_id': row['statement_id'],
            'archive_target': spec['archive'],
            'preserved_context_candidate': spec['context'],
            'original_quote': spec['quote'],
        })

    if len(changed) != len(TARGETS):
        raise SystemExit(f'expected {len(TARGETS)} changes; found {len(changed)}')
    serialized = '\n'.join(
        json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output
    ) + '\n'
    after = serialized.encode('utf-8')
    true_rows = [row for row in output if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in true_rows)
    unclassified_dual = sum(
        bool(row.get('subject_candidate_id') and row.get('object_candidate_id'))
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
        for row in output
    )
    if (len(true_rows), complete, len(true_rows) - complete, unclassified_dual) != (3571, 3557, 14, 4484):
        raise SystemExit('unexpected post-state relation candidate counts')
    return before, after, {
        'changed_statements': changed,
        'total_statements': len(output),
        'relation_candidates': len(true_rows),
        'complete_endpoint_ids': complete,
        'missing_endpoint_ids': len(true_rows) - complete,
        'dual_endpoint_unclassified': unclassified_dual,
        'before_sha256': before_hash,
        'after_sha256': sha256(after),
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
    if BACKUP.exists():
        raise SystemExit(f'backup already exists: {BACKUP}')
    temporary = STATEMENTS.with_name(STATEMENTS.name + '.tmp-citation-normalization')
    if temporary.exists():
        raise SystemExit(f'temporary file already exists: {temporary}')
    shutil.copy2(STATEMENTS, BACKUP)
    temporary.write_bytes(after)
    temporary.replace(STATEMENTS)
    actual = sha256(STATEMENTS.read_bytes())
    if actual != report['after_sha256']:
        shutil.copy2(BACKUP, STATEMENTS)
        raise SystemExit(f'post-write hash mismatch; restored backup: {actual}')
    print('applied; recovery copy written; hash verified')


if __name__ == '__main__':
    main()
