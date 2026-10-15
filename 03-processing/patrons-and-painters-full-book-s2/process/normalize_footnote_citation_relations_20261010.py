from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
CANDIDATES = TABLES / 'entity-candidates.csv'
MENTIONS = TABLES / 'mentions.csv'
STATEMENTS = TABLES / 'book-statements.jsonl'
EXPECTED_HASHES = {
    CANDIDATES.name: 'd5ba20297135e645f045a0c38b4dc41adde9dcad9c90baacce65318f2ce267d2',
    MENTIONS.name: '9ab4a9db88fb3086b77673c7584d76bc2245a1e1e98f017db24520cd1ea72a7c',
    STATEMENTS.name: 'e4bddb40beaacad6d7baf18646e0c0db277cbe93f334f4173b386cf935b1a86f',
}
SOURCE_BOOK_ID = 'cand-2962'
HORAe_ARCHIVE_ID = 'cand-11570'
EXPECTED_TYPE_PAIRS = {
    ('person', 'archive'): 60,
    ('archive', 'person'): 6,
    ('work', 'archive'): 3,
    ('institution', 'archive'): 2,
    ('family', 'archive'): 2,
    ('person', 'person'): 2,
    ('archive', 'archive'): 2,
    ('place', 'archive'): 1,
}
ARCHIVE_ARCHIVE_TARGET_OVERRIDES = {
    'st-chp4-intro-notes-03-bottari-citation': 'object',
    'st-fm-2ed-l187-188-01-honour-review-citation': 'subject',
}
SPECIAL_ARCHIVE_TARGETS = {
    'st-chp3-intro-l7-9-horae-attribution': HORAe_ARCHIVE_ID,
    'st-chp5-seciv-note-l53-p145-marker3': 'cand-4376',
}
BACKUPS = {
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + '.bak-s2-handoff-footnote-citations-20261010'),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + '.bak-s2-handoff-footnote-citations-20261010'),
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-handoff-footnote-citations-20261010'),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def append_csv_row(original: bytes, row: dict[str, str]) -> bytes:
    fields = list(csv.DictReader(io.StringIO(original.decode('utf-8-sig'), newline='')).fieldnames or [])
    if not fields or set(fields) != set(row):
        raise SystemExit('candidate CSV schema mismatch')
    newline = '\r\n' if b'\r\n' in original else '\n'
    out = io.StringIO(newline='')
    csv.DictWriter(out, fieldnames=fields, lineterminator=newline).writerow(row)
    prefix = '' if original.endswith((b'\n', b'\r')) else newline
    return original + prefix.encode('ascii') + out.getvalue().encode('utf-8')


def prepare() -> tuple[dict[Path, bytes], dict[Path, bytes], dict]:
    before = {path: path.read_bytes() for path in (CANDIDATES, MENTIONS, STATEMENTS)}
    hashes = {path.name: sha256(data) for path, data in before.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'table hashes changed: {hashes}')
    candidate_by_id = {row['candidate_id']: row for row in load_csv(CANDIDATES)}
    source = candidate_by_id.get(SOURCE_BOOK_ID)
    if not source or source['suggested_type'] != 'archive':
        raise SystemExit('source-book candidate is absent or not archive typed')

    if max(int(row['candidate_id'][5:]) for row in candidate_by_id.values()) != 11569:
        raise SystemExit('candidate ID cursor changed')
    if HORAe_ARCHIVE_ID in candidate_by_id:
        raise SystemExit('Horae archive candidate ID already exists')
    rows = [json.loads(line) for line in before[STATEMENTS].decode('utf-8').splitlines() if line.strip()]
    target_rows = [
        row for row in rows
        if row.get('predicate') == 'footnote_citation'
        and row.get('subject_candidate_id')
        and row.get('object_candidate_id')
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
    ]
    if len(target_rows) != 78:
        raise SystemExit(f'expected 78 unclassified, dual-end footnote_citation statements; found {len(target_rows)}')
    type_pairs = collections.Counter(
        (candidate_by_id[row['subject_candidate_id']]['suggested_type'], candidate_by_id[row['object_candidate_id']]['suggested_type'])
        for row in target_rows
    )
    if dict(type_pairs) != EXPECTED_TYPE_PAIRS:
        raise SystemExit(f'footnote_citation endpoint type distribution changed: {dict(type_pairs)}')

    true_count = 0
    output = []
    classified_ids = set()
    for row in rows:
        if row not in target_rows:
            output.append(row)
            continue
        sid = row['statement_id']
        if sid in classified_ids:
            raise SystemExit(f'duplicate target statement: {sid}')
        classified_ids.add(sid)
        subject_id, object_id = row['subject_candidate_id'], row['object_candidate_id']
        subject_type = candidate_by_id[subject_id]['suggested_type']
        object_type = candidate_by_id[object_id]['suggested_type']
        q = dict(row.get('qualifiers') or {})
        special_target_id = SPECIAL_ARCHIVE_TARGETS.get(sid)
        if special_target_id:
            target_id = special_target_id
            if target_id not in candidate_by_id and target_id != HORAe_ARCHIVE_ID:
                raise SystemExit(f'special citation target does not resolve: {sid} -> {target_id}')
            choice = 'special'
        elif subject_type == 'archive' and object_type == 'archive':
            choice = ARCHIVE_ARCHIVE_TARGET_OVERRIDES.get(sid)
            if choice is None:
                raise SystemExit(f'archive/archive citation needs a specific target decision: {sid}')
        elif object_type == 'archive':
            choice = 'object'
        elif subject_type == 'archive':
            choice = 'subject'
        else:
            choice = None

        if choice:
            target_id = target_id if choice == 'special' else (object_id if choice == 'object' else subject_id)
            if target_id == HORAe_ARCHIVE_ID:
                target_type = 'archive'
                target_name = 'Horae Subsecivae (edition unspecified; pp. 386 ff. cited)'
            else:
                target_type = candidate_by_id[target_id]['suggested_type']
                target_name = candidate_by_id[target_id]['canonical_name']
            if target_type != 'archive':
                raise SystemExit(f'cites target is not archive typed: {sid}')
            old_claim = str(q.get('claim') or '').strip()
            row = dict(row)
            row.update({
                'subject_candidate_id': SOURCE_BOOK_ID,
                'object_candidate_id': target_id,
                'predicate': 'cites',
            })
            q.update({
                'claim': f'Haskell’s book cites {target_name} in this footnote. The note’s original topical context is: {old_claim}',
                'relation_candidate': True,
                'relation_candidate_note': 'S2 cites candidate: the footnote explicitly cites this archive from Haskell’s book. The citation records a bibliographic link and does not independently validate the cited source’s claims; no formal S6 edge is created.',
            })
            true_count += 1
        else:
            raise SystemExit(f'no archive target resolved for footnote citation: {sid}')
        row['qualifiers'] = q
        output.append(row)

    if classified_ids != {row['statement_id'] for row in target_rows}:
        raise SystemExit('not every selected footnote statement was classified')
    if true_count != 78:
        raise SystemExit(f'expected 78 cites statements; found {true_count}')
    horae_statement = {
        'statement_id': 'st-chp3-intro-l7-9-horae-authored-by-chandos',
        'segment_id': 'chp-3:03_CHP-3_intro:l7-9',
        'subject_candidate_id': HORAe_ARCHIVE_ID,
        'object_candidate_id': 'cand-0644',
        'predicate': 'authored_by',
        'qualifiers': {
            'source_line_start': 9,
            'source_line_end': 9,
            'claim': 'The footnote brackets Grey Brydges, 5th Lord Chandos, as the author of Horae Subsecivae.',
            'speaker': 'editorial identification in book footnote',
            'text_layer': 'bibliographic citation and attribution',
            'footnote_marker': 2,
            'page_range': '386 ff.',
            'pdf_physical_page': 1,
            'printed_page_label': 'i',
            'qualification': 'The author name is bracketed in the printed note; preserve it as the book’s attribution, not as independently verified authorship.',
            'mentioned_candidate_ids': [HORAe_ARCHIVE_ID, 'cand-0644'],
            'relation_candidate': True,
            'relation_candidate_note': 'S2 authorship candidate based on the bracketed attribution in Haskell’s footnote; no independent verification or formal S6 edge is asserted.',
        },
        'original_quote': '2 [Grey Brydges, 5th Lord Chandos]: Horae Subsecivae, pp. 386 ff.',
        'origin': 'book',
        'source_file': '02-sources/02-Markdown/03_CHP-3_intro.md',
    }
    if any(row['statement_id'] == horae_statement['statement_id'] for row in output):
        raise SystemExit('authorship statement ID already exists')
    output.append(horae_statement)

    candidate_addition = {
        'candidate_id': HORAe_ARCHIVE_ID,
        'index_entry_id': '',
        'canonical_name': 'Horae Subsecivae (edition unspecified; pp. 386 ff. cited)',
        'index_page_range': '',
        'suggested_type': 'archive',
        'status': 'open',
        'index_source_file': '',
        'sub_entry': '',
        'detail': 'Work cited in chapter 3, footnote 2 at pages 386 ff.; the note brackets Grey Brydges, 5th Lord Chandos, as author. Edition, publication details, and the cited pages have not been independently checked.',
        'exclude_reason': '',
        'candidate_origin': 'body-mention',
        'candidate_source_ref': 'chp-3:03_CHP-3_intro:l7-9#L9',
    }
    candidate_bytes = append_csv_row(before[CANDIDATES], candidate_addition)
    old_mention = b'm-chp3-intro-l7-9-0005,chp-3:03_CHP-3_intro:l7-9,cand-0646,Horae Subsecivae,289,305,Work cited in note 2; reuse its index candidate under Chandos rather than creating a duplicate.'
    new_mention = b'm-chp3-intro-l7-9-0005,chp-3:03_CHP-3_intro:l7-9,cand-11570,Horae Subsecivae,289,305,Work cited in note 2; record as an archive candidate distinct from its bracketed author.'
    if before[MENTIONS].count(old_mention) != 1:
        raise SystemExit('Horae mention natural row changed')
    mention_bytes = before[MENTIONS].replace(old_mention, new_mention)
    text = '\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n'
    after = text.encode('utf-8')
    all_true = [row for row in output if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in all_true)
    unclassified_dual = sum(
        bool(row.get('subject_candidate_id') and row.get('object_candidate_id'))
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
        for row in output
    )
    if (len(output), len(all_true), complete, len(all_true) - complete, unclassified_dual) != (12651, 3565, 3551, 14, 4490):
        raise SystemExit('unexpected post-state counts')
    candidate_by_id[HORAe_ARCHIVE_ID] = candidate_addition
    return before, {CANDIDATES: candidate_bytes, MENTIONS: mention_bytes, STATEMENTS: after}, {
        'selected_statements': len(target_rows),
        'normalized_to_cites': true_count,
        'added_authorship_candidate': HORAe_ARCHIVE_ID,
        'added_authorship_statement': horae_statement['statement_id'],
        'remapped_existing_mention': 'm-chp3-intro-l7-9-0005',
        'all_true_relation_candidates': len(all_true),
        'two_endpoint_ids': complete,
        'missing_endpoint_ids': len(all_true) - complete,
        'dual_endpoint_unclassified': unclassified_dual,
        'before_sha256': hashes,
        'after_sha256': {path.name: sha256(data) for path, data in {CANDIDATES: candidate_bytes, MENTIONS: mention_bytes, STATEMENTS: after}.items()},
        'target_type_pairs': {f'{domain}->{range_}': count for (domain, range_), count in type_pairs.items()},
        'special_archive_target_statement_ids': sorted(SPECIAL_ARCHIVE_TARGETS),
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
    for path, backup in BACKUPS.items():
        if backup.exists():
            raise SystemExit(f'backup already exists: {backup}')
        shutil.copy2(path, backup)
    for path, data in after.items():
        path.write_bytes(data)
    actual = {path.name: sha256(path.read_bytes()) for path in after}
    if actual != report['after_sha256']:
        raise SystemExit(f'post-write hashes mismatch: {actual}')
    print('applied; recovery copies written; hashes verified')


if __name__ == '__main__':
    main()
