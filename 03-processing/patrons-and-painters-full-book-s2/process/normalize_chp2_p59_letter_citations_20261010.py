from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources/02-Markdown/02_CHP-2_sec_vii.md'
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + '.bak-s2-handoff-chp2-p59-letter-citations-20261010'
)
EXPECTED_STATEMENTS_SHA256 = (
    '833231ad660ba838647794e44480c04a381aa5695ca8d5d7383b4c8a1e8e1901'
)
EXPECTED_SOURCE_SHA256 = (
    '5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c'
)
BOOK_ID = 'cand-2962'
SOURCE_FILE = '02-sources/02-Markdown/02_CHP-2_sec_vii.md'
SEGMENT_ID = 'chp-2:02_CHP-2_sec_vii:l38-54'

TARGETS = {
    'st-chp2-secvii-l38-54-fn-p59-1-letters-of-unnamed-wife': {
        'old_subject': 'cand-4907', 'archive': 'cand-4942',
        'old_object': 'cand-4942', 'context': 'cand-4907',
        'publication': 'cand-4575', 'author_candidate': 'cand-4238',
        'line': 39, 'page': 59, 'marker': 1,
        'locator': 'Pecchiai, 1959, pp. 182 ff.',
        'body_statement': 'st-chp2-secvii-l5-19-rome-properties-and-taddeo-wife',
    },
    'st-chp2-secvii-l38-54-fn-p59-2-letter-1646-01-21': {
        'old_subject': 'cand-4943', 'archive': 'cand-4943',
        'old_object': 'cand-4359', 'context': 'cand-2208',
        'publication': 'cand-4359', 'author_candidate': None,
        'line': 40, 'page': 59, 'marker': 2,
        'locator': 'Pollak, 1913, p. 50',
        'body_statement': 'st-chp2-secvii-l5-19-romanelli-letter-and-exile',
    },
    'st-chp2-secvii-l38-54-fn-p59-3-letter-1646-03-09': {
        'old_subject': 'cand-4944', 'archive': 'cand-4944',
        'old_object': 'cand-4946', 'context': 'cand-0199',
        'publication': 'cand-4946', 'author_candidate': 'cand-0199',
        'line': 41, 'page': 59, 'marker': 3,
        'locator': 'Lumbroso, p. 312',
        'body_statement': 'st-chp2-secvii-l5-19-francesco-praises-vouet',
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_candidates() -> dict[str, dict[str, str]]:
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        return {row['candidate_id']: row for row in csv.DictReader(f)}


def prepare() -> tuple[bytes, bytes, dict]:
    before = STATEMENTS.read_bytes()
    if sha256(before) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit(f'statement table changed: {sha256(before)}')
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f'source file changed: {sha256(source_bytes)}')

    candidate_by_id = load_candidates()
    if candidate_by_id.get(BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('book candidate is absent or not archive typed')
    rows = [json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('duplicate statement IDs in source table')
    if set(TARGETS) - set(by_id):
        raise SystemExit('one or more fixed target statement IDs are missing')

    source_lines = source_bytes.decode('utf-8-sig').splitlines()
    for sid, spec in TARGETS.items():
        row = by_id[sid]
        q = row.get('qualifiers') or {}
        if (
            row.get('segment_id') != SEGMENT_ID
            or row.get('source_file') != SOURCE_FILE
            or row.get('origin') != 'book'
            or row.get('predicate') != 'footnote-claim'
            or row.get('subject_candidate_id') != spec['old_subject']
            or row.get('object_candidate_id') != spec['old_object']
            or q.get('relation_candidate') is not None
            or q.get('source_line_start') != spec['line']
            or q.get('source_line_end') != spec['line']
            or q.get('print_page') != spec['page']
            or q.get('footnote_marker') != spec['marker']
        ):
            raise SystemExit(f'fixed source contract changed: {sid}')
        if spec['line'] > len(source_lines) or row['original_quote'] not in source_lines[spec['line'] - 1]:
            raise SystemExit(f'original quote no longer matches source line: {sid}')
        for candidate_id in (spec['archive'], spec['context'], spec['publication']):
            candidate = candidate_by_id.get(candidate_id)
            if not candidate:
                raise SystemExit(f'citation candidate is absent: {sid} -> {candidate_id}')
        if candidate_by_id[spec['archive']]['suggested_type'] != 'archive':
            raise SystemExit(f'cited letter is not archive typed: {sid}')
        if candidate_by_id[spec['publication']]['suggested_type'] != 'archive':
            raise SystemExit(f'publication locator is not archive typed: {sid}')
        if spec['author_candidate'] and spec['author_candidate'] not in candidate_by_id:
            raise SystemExit(f'author/context candidate is absent: {sid}')
        if spec['body_statement'] not in by_id:
            raise SystemExit(f'linked body statement is absent: {sid}')

    output = []
    changed = []
    for row in rows:
        spec = TARGETS.get(row['statement_id'])
        if not spec:
            output.append(row)
            continue
        sid = row['statement_id']
        q = dict(row.get('qualifiers') or {})
        prior_claim = str(q.get('claim') or '').strip()
        if not prior_claim:
            raise SystemExit(f'prior source-bounded claim is missing: {sid}')
        archive = candidate_by_id[spec['archive']]['canonical_name']
        publication = candidate_by_id[spec['publication']]['canonical_name']
        row = dict(row)
        row.update({
            'subject_candidate_id': BOOK_ID,
            'object_candidate_id': spec['archive'],
            'predicate': 'cites',
        })
        q.update({
            'claim': (
                f'Haskell’s book cites {archive} in footnote {spec["marker"]}; '
                f'the printed locator is {spec["locator"]}. Prior S2 context: {prior_claim}'
            ),
            'citation_context_candidate_id': spec['context'],
            'related_body_statement_ids': [spec['body_statement']],
            'text_layer': 'bibliographic citation to correspondence',
            'citation_publication_candidate_id': spec['publication'],
            'citations': [{
                'source_candidate_id': spec['archive'],
                'publication_candidate_id': spec['publication'],
                'locator': spec['locator'],
            }],
            'relation_candidate': True,
            'relation_candidate_note': (
                'S2 cites candidate: the note points to the identified letter as cited '
                'through its printed publication locator. The author/title details remain '
                'only as stated in the note; the cited letter and publication pages were '
                'not independently consulted. No formal S6 edge is created.'
            ),
            'cited_material_not_independently_consulted': True,
        })
        row['qualifiers'] = q
        output.append(row)
        changed.append({
            'statement_id': sid,
            'letter_archive': spec['archive'],
            'publication_archive': spec['publication'],
            'body_context': spec['body_statement'],
        })

    after = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    true_rows = [row for row in output if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in true_rows)
    dual_unclassified = sum(
        bool(row.get('subject_candidate_id') and row.get('object_candidate_id'))
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
        for row in output
    )
    if (len(output), len(changed), len(true_rows), complete, len(true_rows) - complete, dual_unclassified) != (12664, 3, 3628, 3614, 14, 4440):
        raise SystemExit('unexpected post-state counts')
    return before, after, {
        'mode': 'dry-run',
        'changed_citations': changed,
        'statement_rows': len(output),
        'relation_candidates': len(true_rows),
        'complete_endpoints': complete,
        'open_endpoints': len(true_rows) - complete,
        'dual_endpoint_unclassified': dual_unclassified,
        'before_sha256': sha256(before),
        'after_sha256': sha256(after),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before, after, report = prepare()
    if not args.apply:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    if STATEMENTS.read_bytes() != before:
        raise SystemExit('statement table changed after dry-run')
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + '.tmp-chp2-p59-letter-citations')
    try:
        temporary.write_bytes(after)
        os.replace(temporary, STATEMENTS)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps({
        **report,
        'mode': 'applied',
        'backup': str(BACKUP.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
