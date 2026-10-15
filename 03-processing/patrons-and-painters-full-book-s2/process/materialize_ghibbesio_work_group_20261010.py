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
SOURCE = ROOT / '02-sources/02-Markdown/04_CHP-4_intro.md'
SEGMENTS = TABLES / 'segments.jsonl'

EXPECTED_HASHES = {
    CANDIDATES.name: 'd3548313f75bfaad0a6457229cbd2e59e265cd238704bbd5df922dfbdac3d92b',
    MENTIONS.name: 'b19c0b8e0f973afd21ad2f4ab78206b547c0203d4e068ab6aa64065d442ca29b',
    STATEMENTS.name: 'bffcf6aa304af0af2a4968d9fd0eb75522456ab671fba891609d95fc6a535061',
}
SEGMENT_ID = 'chp-4:04_CHP-4_intro:l3-8'
SOURCE_LINE = 7
SOURCE_PHRASE = 'many paintings and drawings by Pietro da Cortona'
GROUP_START = 818
GROUP_END = 866
GROUP_CANDIDATE_ID = 'cand-11566'
GROUP_MENTION_ID = 'm-chp4-intro-0027'
OWNERSHIP_STATEMENT_ID = 'st-chp4-intro-l3-8-ghibbesio-collection-contents'
CREATOR_STATEMENT_ID = 'st-chp4-intro-l3-8-ghibbesio-works-creator'
GROUP_NAME = "Unidentified paintings and drawings by Pietro da Cortona owned by Jacopo Ghibbesio"

BACKUPS = {
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + '.bak-s2-handoff-ghibbesio-work-group-20261010'),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + '.bak-s2-handoff-ghibbesio-work-group-20261010'),
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-handoff-ghibbesio-work-group-20261010'),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_rows(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = data.decode('utf-8-sig')
    rows = list(csv.DictReader(io.StringIO(text, newline='')))
    if not rows:
        raise SystemExit('CSV unexpectedly empty')
    return list(rows[0]), rows


def append_csv_row(original: bytes, row: dict[str, str]) -> bytes:
    fields, _ = csv_rows(original)
    if set(row) != set(fields):
        raise SystemExit(f'CSV field mismatch for new row: {set(row) ^ set(fields)}')
    newline = '\r\n' if b'\r\n' in original else '\n'
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=newline)
    writer.writerow(row)
    prefix = b'' if original.endswith((b'\n', b'\r')) else newline.encode('ascii')
    return original + prefix + buf.getvalue().encode('utf-8')


def load_jsonl(data: bytes) -> tuple[str, list[dict]]:
    text = data.decode('utf-8')
    return text, [json.loads(line) for line in text.splitlines() if line.strip()]


def prepare() -> tuple[dict[Path, bytes], dict[Path, bytes], dict]:
    originals = {path: path.read_bytes() for path in (CANDIDATES, MENTIONS, STATEMENTS)}
    hashes = {path.name: sha256(data) for path, data in originals.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'table hashes changed: {hashes}')

    candidate_fields, candidate_rows = csv_rows(originals[CANDIDATES])
    mention_fields, mention_rows = csv_rows(originals[MENTIONS])
    statement_text, statement_rows = load_jsonl(originals[STATEMENTS])
    candidate_by_id = {row['candidate_id']: row for row in candidate_rows}
    mention_by_id = {row['mention_id']: row for row in mention_rows}
    statement_by_id: dict[str, dict] = {}
    for row in statement_rows:
        sid = row.get('statement_id')
        if sid in statement_by_id:
            raise SystemExit(f'duplicate statement ID: {sid}')
        statement_by_id[sid] = row

    if GROUP_CANDIDATE_ID in candidate_by_id or GROUP_MENTION_ID in mention_by_id or CREATOR_STATEMENT_ID in statement_by_id:
        raise SystemExit('new IDs already exist')
    if OWNERSHIP_STATEMENT_ID not in statement_by_id:
        raise SystemExit('ownership statement is missing')

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get('segment_id') == SEGMENT_ID), None)
    if not segment or segment.get('sha256') != '3bf389f549c498902ecc1b876c57a93141d7872f7aa372b873daf8718ea14ee8':
        raise SystemExit('source segment or segment hash changed')
    source_lines = SOURCE.read_text(encoding='utf-8').splitlines()
    if SOURCE_PHRASE not in source_lines[SOURCE_LINE - 1]:
        raise SystemExit('source phrase not present on expected S0 line')
    segment_text = '\n'.join(source_lines[segment['line_start'] - 1:segment['line_end']])
    if segment_text[GROUP_START:GROUP_END] != SOURCE_PHRASE:
        raise SystemExit('group mention offsets do not match the source segment')

    artist_mention = mention_by_id.get('m-chp4-intro-0014')
    if not artist_mention or (artist_mention['segment_id'], artist_mention['candidate_id'], artist_mention['surface_form'], int(artist_mention['start_char']), int(artist_mention['end_char'])) != (
        SEGMENT_ID, 'cand-0342', 'Pietro da Cortona', 849, 866
    ):
        raise SystemExit('nested artist mention changed')
    for mention in mention_rows:
        if mention.get('segment_id') != SEGMENT_ID:
            continue
        start, end = int(mention['start_char']), int(mention['end_char'])
        if start < GROUP_END and GROUP_START < end and not (GROUP_START <= start and end <= GROUP_END):
            raise SystemExit(f'new group span would cross mention {mention["mention_id"]}')
        if start == GROUP_START and end == GROUP_END:
            raise SystemExit('duplicate mention natural key')

    old = statement_by_id[OWNERSHIP_STATEMENT_ID]
    old_q = old.get('qualifiers') or {}
    if (old.get('segment_id'), old.get('predicate'), old.get('subject_candidate_id'), old.get('object_candidate_id'), old.get('source_file')) != (
        SEGMENT_ID, 'collection_contents_reported', 'cand-1158', 'cand-0342', '02-sources/02-Markdown/04_CHP-4_intro.md'
    ) or old_q.get('relation_candidate') is not None or (old_q.get('source_line_start'), old_q.get('source_line_end')) != (SOURCE_LINE, SOURCE_LINE):
        raise SystemExit('original statement no longer matches the reviewed assertion')

    candidate = {
        'candidate_id': GROUP_CANDIDATE_ID,
        'index_entry_id': '',
        'canonical_name': GROUP_NAME,
        'index_page_range': '',
        'suggested_type': 'work',
        'status': 'open',
        'index_source_file': '',
        'sub_entry': '',
        'detail': 'Source-defined group of many paintings and drawings attributed to Pietro da Cortona and owned by Jacopo Ghibbesio. Individual works, titles, dates, and exact count are not supplied; do not split into named works or infer a complete inventory.',
        'exclude_reason': '',
        'candidate_origin': 'body-mention',
        'candidate_source_ref': f'{SEGMENT_ID}#L{SOURCE_LINE}',
    }
    mention = {
        'mention_id': GROUP_MENTION_ID,
        'segment_id': SEGMENT_ID,
        'candidate_id': GROUP_CANDIDATE_ID,
        'surface_form': SOURCE_PHRASE,
        'start_char': str(GROUP_START),
        'end_char': str(GROUP_END),
        'note': 'Source-bounded work group; no individual titles or count. Strictly contains the separate artist mention m-chp4-intro-0014.',
    }
    if set(candidate) != set(candidate_fields) or set(mention) != set(mention_fields):
        raise SystemExit('new CSV row schema mismatch')

    updated_rows = []
    for row in statement_rows:
        if row.get('statement_id') != OWNERSHIP_STATEMENT_ID:
            updated_rows.append(row)
            continue
        row = dict(row)
        q = dict(row.get('qualifiers') or {})
        row.update({
            'subject_candidate_id': GROUP_CANDIDATE_ID,
            'object_candidate_id': 'cand-1158',
            'predicate': 'owned_by',
        })
        q.update({
            'claim': 'Haskell reports that Jacopo Ghibbesio owned many paintings and drawings by Pietro da Cortona.',
            'qualification': 'The source directly identifies Ghibbesio as owner of the source-defined work group. Individual works, titles, dates, and exact count are not specified.',
            'mentioned_candidate_ids': ['cand-1158', GROUP_CANDIDATE_ID, 'cand-0342'],
            'relation_candidate': True,
            'relation_candidate_note': 'S2 candidate for ownership of the source-bounded work group; the original says “enthusiastic owner”. No formal S6 edge is created.',
        })
        q.pop('object_role', None)
        row['qualifiers'] = q
        updated_rows.append(row)

    old_quote = old.get('original_quote')
    creator = {
        'statement_id': CREATOR_STATEMENT_ID,
        'segment_id': SEGMENT_ID,
        'subject_candidate_id': 'cand-0342',
        'object_candidate_id': GROUP_CANDIDATE_ID,
        'predicate': 'creator_of',
        'qualifiers': {
            'source_line_start': SOURCE_LINE,
            'source_line_end': SOURCE_LINE,
            'claim': 'Haskell attributes the source-defined group of paintings and drawings owned by Ghibbesio to Pietro da Cortona.',
            'speaker': 'Haskell',
            'text_layer': 'authorial report',
            'pdf_physical_page': 1,
            'qualification': 'The phrase “by Pietro da Cortona” supports the group-level attribution; individual works, titles, and exact count remain unknown. This is a source-reported claim, not independent verification.',
            'mentioned_candidate_ids': ['cand-1158', GROUP_CANDIDATE_ID, 'cand-0342'],
            'parent_body_statement_ids': [OWNERSHIP_STATEMENT_ID],
            'relation_candidate': True,
            'relation_candidate_note': 'S2 creator-of candidate for an explicitly source-defined group; no individual work or formal S6 edge is asserted.',
        },
        'original_quote': old_quote,
        'origin': 'book',
        'source_file': '02-sources/02-Markdown/04_CHP-4_intro.md',
    }
    updated_rows.append(creator)

    output_text = '\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in updated_rows) + '\n'
    new_files = {
        CANDIDATES: append_csv_row(originals[CANDIDATES], candidate),
        MENTIONS: append_csv_row(originals[MENTIONS], mention),
        STATEMENTS: output_text.encode('utf-8'),
    }
    flags = collections.Counter(str((row.get('qualifiers') or {}).get('relation_candidate')).lower() for row in updated_rows)
    true_rows = [row for row in updated_rows if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in true_rows)
    if (len(candidate_rows) + 1, len(mention_rows) + 1, len(updated_rows), flags['true'], complete, len(true_rows) - complete) != (11544, 27477, 12647, 3475, 3461, 14):
        raise SystemExit('unexpected post-state counts')
    return originals, new_files, {
        'candidate_id': GROUP_CANDIDATE_ID,
        'mention_id': GROUP_MENTION_ID,
        'statement_ids': [OWNERSHIP_STATEMENT_ID, CREATOR_STATEMENT_ID],
        'candidate_count': len(candidate_rows) + 1,
        'mention_count': len(mention_rows) + 1,
        'statement_count': len(updated_rows),
        'relation_candidate_true': flags['true'],
        'complete_endpoints': complete,
        'open_endpoints': len(true_rows) - complete,
        'before_sha256': hashes,
        'after_sha256': {path.name: sha256(data) for path, data in new_files.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after all checks; default is dry-run')
    args = parser.parse_args()
    originals, new_files, report = prepare()
    print(json.dumps({'mode': 'apply' if args.apply else 'dry-run', **report}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit(f'one or more recovery copies already exist: {list(BACKUPS.values())}')
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
        if sha256(backup.read_bytes()) != sha256(originals[path]):
            raise SystemExit(f'recovery copy failed verification: {backup}')
    for path, data in new_files.items():
        path.write_bytes(data)
    mismatches = [str(path) for path, data in new_files.items() if sha256(path.read_bytes()) != sha256(data)]
    if mismatches:
        for path, data in originals.items():
            path.write_bytes(data)
        raise SystemExit(f'post-write hash mismatch; original bytes restored for {mismatches}')
    print('backups=' + json.dumps({path.name: str(backup) for path, backup in BACKUPS.items()}, ensure_ascii=False))
    print('applied_sha256=' + json.dumps({path.name: sha256(path.read_bytes()) for path in new_files}, ensure_ascii=False))


if __name__ == '__main__':
    main()
