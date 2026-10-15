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
    STATEMENTS.name: 'cc1129080fe32053fe0f3b11e0337989d5e58f6554c42f60cdd5d24e10f6c8fc',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p186-note-20261013')
NOTE_ID = 'st-chp7-p186-n1-cite-wittkower'
BODY_IDS = ['st-chp7-p186-i11', 'st-chp7-p186-i12', 'st-chp7-p186-i13', 'st-chp7-p186-i14']
LOCATOR = 'Wittkower, Art and Architecture in Italy 1600 to 1750 (1958), p. 269'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as f:
        f.write(data)
        temp = Path(f.name)
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = {p: p.read_bytes() for p in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {p.name: digest(data) for p, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    if '1 Wittkower, 1958, p. 269.' not in lines[360]:
        raise SystemExit(f'source guard failed at L361: {lines[360]}')
    candidates = {r['candidate_id']: r for r in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))}
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive' or candidates.get('cand-4557', {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source book or Wittkower publication candidate is missing/mistyped')
    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {r['statement_id']: r for r in rows}
    row = by_id.get(NOTE_ID)
    if (not row or row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
            or row.get('object_candidate_id') != 'cand-4557' or row.get('subject_candidate_id') is not None
            or row.get('qualifiers', {}).get('source_line_start') != 361
            or row.get('qualifiers', {}).get('relation_candidate') is not None
            or row.get('qualifiers', {}).get('linked_body_statement_ids') != BODY_IDS):
        raise SystemExit('p.186 citation row changed since review')
    for body_id in BODY_IDS:
        if NOTE_ID not in (by_id.get(body_id, {}).get('qualifiers') or {}).get('footnote_statement_ids', []):
            raise SystemExit(f'reciprocal body link missing: {body_id}')

    output = []
    for source_row in rows:
        r = dict(source_row)
        if r['statement_id'] == NOTE_ID:
            q = dict(r.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            r.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': 'cand-4557', 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates['cand-4557']['canonical_name']} at {LOCATOR} in footnote 1. The prior note records: {old_claim}",
                'citation_publication_candidate_id': 'cand-4557', 'citation_locator': LOCATOR,
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': 'cand-4557', 'locator': LOCATOR}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': 1, 'footnote_number': 1, 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': 1, 'segment_id': NOTE_SEGMENT, 'source_line': 361, 'statement_ids': BODY_IDS}],
                'related_body_statement_ids': BODY_IDS, 'linked_body_statement_ids': BODY_IDS,
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; the cited publication was not independently consulted, and no S6 edge is created.',
            })
            r['qualifiers'] = q
        output.append(r)
    out = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14187, {True: 8524, False: 3418, 'unset': 2245}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {'mode': 'apply' if args.apply else 'dry_run', 'normalized_citations': 1,
              'reciprocal_body_links_checked': len(BODY_IDS), 'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
              'before_sha256': hashes, 'after_statement_sha256': digest(out), 'backup': str(BACKUP.relative_to(ROOT))}
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
    if digest(STATEMENTS.read_bytes()) != report['after_statement_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
