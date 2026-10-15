from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources/02-Markdown/07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources/01-book/CHP-7.pdf'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: '1b8e65fae5a9b408f7cdaf8183ed93d86f8f12fc4f4289516387f1594da02963',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + '.bak-s2-chp7-p170-171-note-citations-20261013'
)
TARGETS = {
    'st-chp7-p170-n1-cite': {
        'publication_id': 'cand-6997',
        'author_id': 'cand-6386',
        'locator': 'Vaes, 1931, p. 202',
    },
    'st-chp7-p171-n1-cite': {
        'publication_id': 'cand-6998',
        'locator': 'Colapietra, p. 30',
    },
    'st-chp7-p171-n2-cite': {
        'publication_id': 'cand-6999',
        'locator': 'Capecelatro, p. 94',
    },
    'st-chp7-p171-n3-cite': {
        'publication_id': 'cand-7000',
        'locator': 'Bouchard—Marcheix, p. 61',
    },
    'st-chp7-p171-n4-cite': {
        'publication_id': 'cand-7001',
        'locator': 'J. Walker, p. 78',
    },
    'st-chp7-p171-n5-cite': {
        'publication_id': 'cand-4376',
        'author_id': 'cand-1856',
        'locator': 'Passeri, pp. 61 and 64, note 3',
    },
    'st-chp7-p171-n6-cite-passeri': {
        'publication_id': 'cand-4376',
        'author_id': 'cand-1856',
        'locator': 'Passeri (ibid.), p. 157',
    },
    'st-chp7-p171-n6-cite-trapier': {
        'publication_id': 'cand-7002',
        'locator': 'Trapier, p. 109',
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_candidates() -> dict[str, dict[str, str]]:
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        return {row['candidate_id']: row for row in csv.DictReader(f)}


def prepare() -> tuple[bytes, bytes, dict]:
    before = STATEMENTS.read_bytes()
    candidate_bytes = CANDIDATES.read_bytes()
    source_bytes = SOURCE.read_bytes()
    pdf_bytes = PDF.read_bytes()
    hashes = {
        STATEMENTS.name: digest(before),
        CANDIDATES.name: digest(candidate_bytes),
        SOURCE.name: digest(source_bytes),
        PDF.name: digest(pdf_bytes),
    }
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')

    candidate_by_id = read_candidates()
    if candidate_by_id.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source-book candidate is absent or not archive typed')
    for spec in TARGETS.values():
        publication = candidate_by_id.get(spec['publication_id'])
        if not publication or publication.get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive is missing or mistyped: {spec['publication_id']}")
        author_id = spec.get('author_id')
        if author_id and candidate_by_id.get(author_id, {}).get('suggested_type') != 'person':
            raise SystemExit(f'citation author candidate is missing or mistyped: {author_id}')

    rows = [json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    if not set(TARGETS).issubset(by_id):
        raise SystemExit('one or more expected p.170–171 citation statements are missing')

    for sid, spec in TARGETS.items():
        row = by_id[sid]
        q = row.get('qualifiers') or {}
        if (
            row.get('segment_id') != 'chp-7:07_CHP-7_sec_i:l293-389'
            or row.get('predicate') != 'footnote_citation'
            or row.get('subject_candidate_id') is not None
            or row.get('object_candidate_id') != spec['publication_id']
            or q.get('relation_candidate') is not None
            or q.get('text_layer') != 'footnote citation'
        ):
            raise SystemExit(f'target statement changed since review: {sid}')

    output = []
    for row in rows:
        spec = TARGETS.get(row['statement_id'])
        if not spec:
            output.append(row)
            continue
        q = dict(row.get('qualifiers') or {})
        publication_id = spec['publication_id']
        publication_name = candidate_by_id[publication_id]['canonical_name']
        old_claim = str(q.get('claim') or '').strip()
        row = dict(row)
        row.update({
            'subject_candidate_id': SOURCE_BOOK_ID,
            'object_candidate_id': publication_id,
            'predicate': 'cites',
        })
        q.update({
            'claim': f"Haskell’s book cites {publication_name} at {spec['locator']} in this footnote. The prior locator note records: {old_claim}",
            'citation_publication_candidate_id': publication_id,
            'citation_locator': spec['locator'],
            'citations': [{
                'source_candidate_id': publication_id,
                'publication_candidate_id': publication_id,
                'locator': spec['locator'],
            }],
            'cited_material_not_independently_consulted': True,
            'relation_candidate': True,
            'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator. This records Haskell’s bibliographic reference only; the cited material was not independently consulted and no S6 edge is created.',
        })
        if spec.get('author_id'):
            q['citation_candidate_id'] = spec['author_id']
        row['qualifiers'] = q
        output.append(row)

    after = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    status = {
        value: sum((row.get('qualifiers') or {}).get('relation_candidate') is value for row in output)
        for value in (True, False)
    }
    status['unset'] = sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output)
    if (len(output), status) != (14183, {True: 8392, False: 3416, 'unset': 2375}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, statuses={status}')
    if digest(after) == digest(before):
        raise SystemExit('no statement-table changes were prepared')
    return before, after, {
        'mode': 'dry_run',
        'target_count': len(TARGETS),
        'target_ids': list(TARGETS),
        'target_endpoints': {
            sid: {'subject': SOURCE_BOOK_ID, 'object': spec['publication_id'], 'predicate': 'cites'}
            for sid, spec in TARGETS.items()
        },
        'post_counts': {'statements': len(output), **{str(k): v for k, v in status.items()}},
        'before_sha256': hashes,
        'after_sha256': digest(after),
        'backup': str(BACKUP.relative_to(ROOT)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before, after, report = prepare()
    if args.apply:
        report['mode'] = 'apply'
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
    if digest(STATEMENTS.read_bytes()) != report['after_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; hash verified')


if __name__ == '__main__':
    main()
