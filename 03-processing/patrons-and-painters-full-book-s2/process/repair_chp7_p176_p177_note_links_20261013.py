from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / '04-knowledge' / 'tables' / 'book-statements.jsonl'
EXPECTED_SHA256 = '4da489c6e5767ce0884f3fbdff7abd9be1c912ca0dbe9bd485dff5c02b8cbcd8'
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p176-p177-note-links-20261013')
SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'

CITATION_BODY_LINKS = {
    'st-chp7-p176-n1-cite-mazarin': ['st-chp7-p176-i01', 'st-chp7-p176-i02'],
    'st-chp7-p176-n2-cite-correspondance': ['st-chp7-p176-i06', 'st-chp7-p176-i07', 'st-chp7-p176-i08'],
    'st-chp7-p176-n3-cite-correspondance': ['st-chp7-p176-i15'],
    'st-chp7-p176-n4-cite-correspondance': ['st-chp7-p176-i16'],
    'st-chp7-p176-n4-cite-briganti': ['st-chp7-p176-i16'],
    'st-chp7-p176-n5-cite-malvasia': ['st-chp7-p176-i16b'],
    'st-chp7-p176-n6-cite-blunt': ['st-chp7-p176-i22'],
    'st-chp7-p176-n7-cite-wittkower': ['st-chp7-p176-i23', 'st-chp7-p176-i24', 'st-chp7-p176-i25', 'st-chp7-p176-i26'],
    'st-chp7-p176-n8-cite-poussin-correspondance': ['st-chp7-p176-i29'],
    'st-chp7-p176-n9-cite-passeri': ['st-chp7-p176-i30'],
    'st-chp7-p177-n1-cite-baldinucci': ['st-chp7-p177-i01', 'st-chp7-p177-i03'],
    'st-chp7-p177-n2-cite-stone': ['st-chp7-p177-i06'],
    'st-chp7-p177-n2-cite-betcherman': ['st-chp7-p177-i06'],
    'st-chp7-p177-n3-cite-luzio': ['st-chp7-p177-i07', 'st-chp7-p177-i08'],
    'st-chp7-p177-n4-cite-lumbroso': ['st-chp7-p177-i09'],
    'st-chp7-p177-n4-cite-venturi': ['st-chp7-p177-i09'],
    'st-chp7-p177-n5-cite-albion': ['st-chp7-p177-i14'],
}

P177_NOTE4_STATEMENTS = [
    'st-chp7-p177-n4-cite-lumbroso',
    'st-chp7-p177-n4-cite-venturi',
    'st-chp7-p177-n4-letter-addressed-to',
    'st-chp7-p177-n4-letter-authored-by',
    'st-chp7-p177-n4-letter-quoted-content',
]
P177_NOTE4_BODY = 'st-chp7-p177-i09'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before = STATEMENTS.read_bytes()
    actual = sha256(before)
    if actual != EXPECTED_SHA256:
        raise SystemExit(f'statement table hash changed: {actual}')

    rows = [json.loads(line) for line in before.decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    note4_ids = P177_NOTE4_STATEMENTS
    required = set(CITATION_BODY_LINKS) | {sid for ids in CITATION_BODY_LINKS.values() for sid in ids} | set(note4_ids) | {P177_NOTE4_BODY}
    if not required.issubset(by_id):
        raise SystemExit(f'missing link endpoint: {sorted(required - set(by_id))}')

    for citation_id, body_ids in CITATION_BODY_LINKS.items():
        row = by_id[citation_id]
        q = row.get('qualifiers') or {}
        refs = q.get('footnote_refs') or []
        if row.get('predicate') != 'cites' or q.get('relation_candidate') is not True:
            raise SystemExit(f'citation status changed: {citation_id}')
        if not any(ref.get('segment_id') == SEGMENT and ref.get('statement_ids') for ref in refs):
            raise SystemExit(f'citation footnote locator missing: {citation_id}')
        if q.get('linked_body_statement_ids') != body_ids:
            raise SystemExit(f'citation body link changed: {citation_id}')

    for fact_id in note4_ids[2:]:
        row = by_id[fact_id]
        q = row.get('qualifiers') or {}
        if row.get('segment_id') != SEGMENT or q.get('source_line_start') != 322:
            raise SystemExit(f'p.177 note 4 fact anchor changed: {fact_id}')
    body = by_id[P177_NOTE4_BODY]
    body_q = body.get('qualifiers') or {}
    if not any(ref.get('marker') == 4 and ref.get('segment_id') == SEGMENT and ref.get('source_line') == 322
               for ref in (body_q.get('footnote_refs') or [])):
        raise SystemExit('p.177 note 4 body anchor changed')

    output = []
    for source_row in rows:
        row = dict(source_row)
        citation_body_ids = CITATION_BODY_LINKS.get(row['statement_id'])
        if citation_body_ids is not None:
            q = dict(row.get('qualifiers') or {})
            refs = [dict(ref) for ref in (q.get('footnote_refs') or [])]
            ref = refs[0]
            ref['statement_ids'] = citation_body_ids
            q['footnote_refs'] = refs
            row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for fact_id in note4_ids[2:]:
        row = by_out[fact_id]
        q = dict(row.get('qualifiers') or {})
        q.update({
            'footnote_marker': 4,
            'footnote_number': 4,
            'footnote_segment': SEGMENT,
            'footnote_refs': [{
                'marker': 4,
                'segment_id': SEGMENT,
                'source_line': 322,
                'statement_ids': [P177_NOTE4_BODY],
            }],
            'related_body_statement_ids': [P177_NOTE4_BODY],
            'linked_body_statement_ids': [P177_NOTE4_BODY],
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
        })
        row['qualifiers'] = q

    body = by_out[P177_NOTE4_BODY]
    q = dict(body.get('qualifiers') or {})
    refs = [dict(ref) for ref in (q.get('footnote_refs') or [])]
    ref = next(item for item in refs if item.get('marker') == 4 and item.get('segment_id') == SEGMENT and item.get('source_line') == 322)
    ref['statement_ids'] = P177_NOTE4_STATEMENTS
    q.update({
        'footnote_refs': refs,
        'footnote_statement_ids': P177_NOTE4_STATEMENTS,
        'footnote_link_status': 'linked',
        'footnote_text_pending': False,
    })
    body['qualifiers'] = q

    output_bytes = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8453, False: 3420, 'unset': 2314}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'citation_ref_rows_repaired': len(CITATION_BODY_LINKS),
        'p177_note4_fact_statements_linked': len(note4_ids) - 2,
        'body_reciprocal_links_completed': 1,
        'classification_counts_unchanged': counts,
        'before_sha256': actual,
        'after_sha256': sha256(output_bytes),
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
    atomic_write(STATEMENTS, output_bytes)
    if sha256(STATEMENTS.read_bytes()) != report['after_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
