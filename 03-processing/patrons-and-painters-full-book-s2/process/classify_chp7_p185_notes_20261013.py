from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / '04-knowledge' / 'tables' / 'book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge' / 'tables' / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
SOURCE_BOOK_ID = 'cand-2962'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
EXPECTED_HASHES = {
    STATEMENTS.name: '03ba5859ff4c41936863f9d5a93130f17ac09c40f265d990c5a11653dd73aa7d',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p185-notes-20261013')
CITATIONS = {
    'st-chp7-p185-n1-cite-cosnac': {
        'publication_id': 'cand-7087', 'locator': 'de Cosnac, Les richesses du Palais Mazarin (1885), pp. 169 ff.',
        'marker': 1, 'line': 358, 'body_ids': ['st-chp7-p185-i20', 'st-chp7-p185-i21', 'st-chp7-p185-i22'],
    },
    'st-chp7-p185-n2-cite-hautecoeur': {
        'publication_id': 'cand-7097', 'locator': 'Hautecœur, Rome et la Renaissance de la peinture française (1943), pp. 39–49',
        'marker': 2, 'line': 358, 'body_ids': ['st-chp7-p185-i25'],
    },
    'st-chp7-p185-n3-cite-hautecoeur': {
        'publication_id': 'cand-7097', 'locator': 'Hautecœur, Rome et la Renaissance de la peinture française (1943), pp. 84–89 (ibid. to footnote 2)',
        'marker': 3, 'line': 359, 'body_ids': ['st-chp7-p185-i26'],
    },
    'st-chp7-p185-n4-cite-alazard': {
        'publication_id': 'cand-7099', 'locator': 'Alazard, La Vie artistique au temps de Mazarin (1931), pp. 18–28 and 55–86',
        'marker': 4, 'line': 359, 'body_ids': ['st-chp7-p185-i29'],
    },
    'st-chp7-p185-n5-cite-brienne': {
        'publication_id': 'cand-7100', 'locator': 'Brienne, Mémoires, vol. III, pp. 88–90',
        'marker': 5, 'line': 360, 'body_ids': ['st-chp7-p185-i30'],
        'ocr_corrections': [{'source_line': 360, 'ocr': 'IH', 'print_reading': 'III', 'basis': 'CHP-7.pdf physical page 23'}],
    },
}
SOURCE_GUARDS = {
    358: '1 de Cosnac, pp. 169 ff. 2 Hautecoeur, pp. 39-49.',
    359: '3 ibid., pp. 84-9. 4 Alazard, pp. 18-28 and 55-86.',
    360: '5 Brienne, IH, pp. 88-90.',
}


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
    raw = {p: p.read_bytes() for p in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {p.name: sha256(data) for p, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    for line_no, snippet in SOURCE_GUARDS.items():
        if snippet not in source_lines[line_no - 1]:
            raise SystemExit(f'source guard failed at L{line_no}: {source_lines[line_no - 1]}')
    candidates = {r['candidate_id']: r for r in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))}
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source-book candidate is absent or not archive typed')
    for spec in CITATIONS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive missing or mistyped: {spec['publication_id']}")
    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {r['statement_id']: r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    for note_id, spec in CITATIONS.items():
        row, q = by_id[note_id], by_id[note_id].get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line'] or q.get('relation_candidate') is not None
                or q.get('linked_body_statement_ids') != spec['body_ids']):
            raise SystemExit(f'citation row changed since review: {note_id}')
        for body_id in spec['body_ids']:
            body = by_id.get(body_id)
            if not body or note_id not in (body.get('qualifiers') or {}).get('footnote_statement_ids', []):
                raise SystemExit(f'reciprocal body link missing: {body_id} <- {note_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        spec = CITATIONS.get(row['statement_id'])
        if spec:
            pub = spec['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': pub, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[pub]['canonical_name']} at {spec['locator']} in footnote {spec['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': pub, 'citation_locator': spec['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': pub, 'locator': spec['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': spec['marker'], 'footnote_number': spec['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
                'related_body_statement_ids': spec['body_ids'], 'linked_body_statement_ids': spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; the cited publication was not independently consulted, and no S6 edge is created.',
            })
            if spec.get('ocr_corrections'):
                q['ocr_corrections'] = spec['ocr_corrections']
            row['qualifiers'] = q
        output.append(row)
    out = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14187, {True: 8523, False: 3418, 'unset': 2246}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run', 'normalized_citations': len(CITATIONS),
        'reciprocal_links_checked': sum(len(spec['body_ids']) for spec in CITATIONS.values()),
        'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
        'before_sha256': hashes, 'after_statement_sha256': sha256(out),
        'backup': str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    if STATEMENTS.read_bytes() != raw[STATEMENTS]:
        raise SystemExit('statement table changed after dry-run preparation')
    shutil.copy2(STATEMENTS, BACKUP)
    atomic_write(STATEMENTS, out)
    if sha256(STATEMENTS.read_bytes()) != report['after_statement_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
