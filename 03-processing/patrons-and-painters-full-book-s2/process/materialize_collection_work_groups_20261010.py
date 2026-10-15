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
SEGMENTS = TABLES / 'segments.jsonl'
SOURCE = ROOT / '02-sources/02-Markdown/02_CHP-2_sec_i.md'

EXPECTED_HASHES = {
    CANDIDATES.name: '6bc5d72187540e92da313330b6a092167b75eef93416bc4bc400405fe076ba37',
    MENTIONS.name: '275ace24d31c3186b0bdb7744c4cc9647e66be47060b0bf85507f1d7e1bab6e6',
    STATEMENTS.name: '4f4115b4ffd461015abeac5518bcb0b3cf977cdee075223c4a5623417c9af1f2',
}

CHP2_SEGMENT = 'chp-2:02_CHP-2_sec_i:l95-106'
CHP2_SEGMENT_SHA = '165eaffa3127c4d1978a6d3bddf30c96e2b139803117cdefc6d8c02d0c04df8a'
CHP2_GROUP_PHRASE = 'along with others by the\nCarracci, the great masters of the Venetian High Renaissance and by Luca Cambiaso'
CHP2_GROUP_SPAN = (1607, 1713)
VENETIAN_MASTERS_PHRASE = 'the great masters of the Venetian High Renaissance'
VENETIAN_MASTERS_SPAN = (1642, 1692)
CHP2_ARTIST_IDS = {
    'st-chp2-seci-l95-106-carracci-collection': ('cand-4318', 'the Carracci'),
    'st-chp2-seci-l95-106-venetian-collection': ('cand-11569', 'the Venetian High Renaissance masters'),
    'st-chp2-seci-l95-106-cambiaso-collection': ('cand-0488', 'Luca Cambiaso'),
}

CHP2_PALACE_SEGMENT = 'chp-2:02_CHP-2_sec_i:l108-119'
CHP2_PALACE_SEGMENT_SHA = 'eb79505a43436aa4d7a141a2314a8bf34fd450b0ac108511cda8880d292f65f3'
PALACE_GROUP_PHRASE = 'paintings—by old masters such as Raphael, Correggio, Andrea del Sarto,\nGiulio Romano, Parmigianino and others'
PALACE_GROUP_SPAN = (1487, 1596)
PALACE_ARTIST_IDS = {
    'st-chp2-seci-l108-119-palace-paintings-by-raphael': 'cand-2098',
    'st-chp2-seci-l108-119-palace-paintings-by-correggio': 'cand-0852',
    'st-chp2-seci-l108-119-palace-paintings-by-andrea-del-sarto': 'cand-2361',
    'st-chp2-seci-l108-119-palace-paintings-by-giulio-romano': 'cand-1194',
    'st-chp2-seci-l108-119-palace-paintings-by-parmigianino': 'cand-1839',
}

NEW_CANDIDATES = {
    'cand-11567': {
        'canonical_name': 'Unidentified old-master paintings listed among the decorations in Maffeo Barberini’s palace',
        'suggested_type': 'work',
        'detail': 'Source-bounded group introduced as paintings by old masters decorating Maffeo Barberini’s palace. Haskell names Raphael, Correggio, Andrea del Sarto, Giulio Romano, Parmigianino, and others; no individual title, count, date, or complete membership is supplied. “Such as” and “and others” make the list non-exhaustive.',
        'candidate_source_ref': f'{CHP2_PALACE_SEGMENT}#L113',
    },
    'cand-11568': {
        'canonical_name': 'Unidentified additional paintings attributed to artists named in Vincenzo Giustiniani’s large room',
        'suggested_type': 'work',
        'detail': 'Source-bounded group introduced as “others by” the Carracci, the great masters of the Venetian High Renaissance, and Luca Cambiaso, hung with the thirteen Caravaggio paintings in Giustiniani’s large room. Individual titles, counts, and complete membership are not supplied; this group is distinct from the thirteen Caravaggio paintings candidate cand-4316.',
        'candidate_source_ref': f'{CHP2_SEGMENT}#L102',
    },
    'cand-11569': {
        'canonical_name': 'Unnamed collective of Venetian High Renaissance masters cited as painters in Giustiniani’s collection',
        'suggested_type': '',
        'detail': 'The source says “the great masters of the Venetian High Renaissance” as creators of paintings. No individuals or membership are named. Keep this creator collective distinct from the artistic-tradition term cand-4319; the current taxonomy has no established type for an unnamed artist collective, so type remains open.',
        'candidate_source_ref': f'{CHP2_SEGMENT}#L102',
    },
}

NEW_MENTIONS = [
    {
        'mention_id': 'm-chp2-seci-l108-119-0071',
        'segment_id': CHP2_PALACE_SEGMENT,
        'candidate_id': 'cand-11567',
        'surface_form': PALACE_GROUP_PHRASE,
        'start_char': str(PALACE_GROUP_SPAN[0]),
        'end_char': str(PALACE_GROUP_SPAN[1]),
        'note': 'Source-bounded group of paintings; strictly contains the five separate old-master mentions. No individual work titles or count are supplied.',
    },
    {
        'mention_id': 'm-chp2-seci-l95-106-0085',
        'segment_id': CHP2_SEGMENT,
        'candidate_id': 'cand-11568',
        'surface_form': CHP2_GROUP_PHRASE,
        'start_char': str(CHP2_GROUP_SPAN[0]),
        'end_char': str(CHP2_GROUP_SPAN[1]),
        'note': 'Source-bounded group of additional paintings; strictly contains the Carracci, Venetian tradition, and Cambiaso mentions. No individual titles or complete count are supplied.',
    },
    {
        'mention_id': 'm-chp2-seci-l95-106-0086',
        'segment_id': CHP2_SEGMENT,
        'candidate_id': 'cand-11569',
        'surface_form': VENETIAN_MASTERS_PHRASE,
        'start_char': str(VENETIAN_MASTERS_SPAN[0]),
        'end_char': str(VENETIAN_MASTERS_SPAN[1]),
        'note': 'Unnamed creator collective, strictly nested within the additional-paintings group and containing the separate artistic-tradition term mention cand-4319. Individual masters and membership remain unknown.',
    },
]

NEW_STATEMENT_IDS = {
    'st-chp2-seci-l95-106-other-paintings-location',
    'st-chp2-seci-l95-106-other-paintings-part-of-collection',
    'st-chp2-seci-l108-119-old-master-paintings-location',
}

BACKUPS = {
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + '.bak-s2-handoff-collection-work-groups-20261010'),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + '.bak-s2-handoff-collection-work-groups-20261010'),
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-handoff-collection-work-groups-20261010'),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_rows(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    rows = list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'), newline='')))
    if not rows:
        raise SystemExit('CSV unexpectedly empty')
    return list(rows[0]), rows


def append_csv_rows(original: bytes, additions: list[dict[str, str]]) -> bytes:
    fields, _ = csv_rows(original)
    if any(set(row) != set(fields) for row in additions):
        raise SystemExit('CSV field mismatch for added rows')
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=newline.decode('ascii'))
    writer.writerows(additions)
    prefix = b'' if original.endswith((b'\n', b'\r')) else newline
    return original + prefix + buf.getvalue().encode('utf-8')


def load_jsonl(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode('utf-8').splitlines() if line.strip()]


def make_statement(
    statement_id: str,
    segment_id: str,
    source_file: str,
    line_start: int,
    line_end: int,
    subject: str,
    obj: str,
    predicate: str,
    claim: str,
    quote: str,
    mentioned: list[str],
    qualification: str,
    note: str,
    print_page: str,
    pdf_page: int,
) -> dict:
    return {
        'statement_id': statement_id,
        'segment_id': segment_id,
        'subject_candidate_id': subject,
        'object_candidate_id': obj,
        'predicate': predicate,
        'qualifiers': {
            'source_line_start': line_start,
            'source_line_end': line_end,
            'claim': claim,
            'speaker': 'Haskell',
            'text_layer': 'authorial narrative',
            'print_page': print_page,
            'pdf_page': pdf_page,
            'qualification': qualification,
            'mentioned_candidate_ids': mentioned,
            'relation_candidate': True,
            'relation_candidate_note': note,
        },
        'original_quote': quote,
        'origin': 'book',
        'source_file': source_file,
    }


def prepare() -> tuple[dict[Path, bytes], dict[Path, bytes], dict]:
    originals = {path: path.read_bytes() for path in (CANDIDATES, MENTIONS, STATEMENTS)}
    hashes = {path.name: sha256(data) for path, data in originals.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'table hashes changed: {hashes}')

    candidate_fields, candidate_rows = csv_rows(originals[CANDIDATES])
    mention_fields, mention_rows = csv_rows(originals[MENTIONS])
    statement_rows = load_jsonl(originals[STATEMENTS])
    candidate_by_id = {row['candidate_id']: row for row in candidate_rows}
    mention_by_id = {row['mention_id']: row for row in mention_rows}
    statement_by_id = {row['statement_id']: row for row in statement_rows}
    if len(statement_by_id) != len(statement_rows):
        raise SystemExit('duplicate statement ID already exists')
    if max(int(row['candidate_id'][5:]) for row in candidate_rows) != 11566:
        raise SystemExit('candidate ID cursor changed')
    if any(cid in candidate_by_id for cid in NEW_CANDIDATES):
        raise SystemExit('new candidate ID already exists')
    if any(row['mention_id'] in mention_by_id for row in NEW_MENTIONS):
        raise SystemExit('new mention ID already exists')
    if any(sid in statement_by_id for sid in NEW_STATEMENT_IDS):
        raise SystemExit('new statement ID already exists')

    segment_rows = load_jsonl(SEGMENTS.read_bytes())
    segment_by_id = {row['segment_id']: row for row in segment_rows}
    source_lines = SOURCE.read_text(encoding='utf-8').splitlines()
    segment_texts = {}
    for segment_id, expected_sha in ((CHP2_SEGMENT, CHP2_SEGMENT_SHA), (CHP2_PALACE_SEGMENT, CHP2_PALACE_SEGMENT_SHA)):
        segment = segment_by_id.get(segment_id)
        if not segment or segment.get('sha256') != expected_sha:
            raise SystemExit(f'source segment changed: {segment_id}')
        segment_texts[segment_id] = '\n'.join(source_lines[segment['line_start'] - 1:segment['line_end']])

    def verify_span(segment_id: str, span: tuple[int, int], phrase: str) -> None:
        if segment_texts[segment_id][span[0]:span[1]] != phrase:
            raise SystemExit(f'phrase/offset mismatch in {segment_id}: {phrase!r}')

    verify_span(CHP2_SEGMENT, CHP2_GROUP_SPAN, CHP2_GROUP_PHRASE)
    verify_span(CHP2_SEGMENT, VENETIAN_MASTERS_SPAN, VENETIAN_MASTERS_PHRASE)
    verify_span(CHP2_PALACE_SEGMENT, PALACE_GROUP_SPAN, PALACE_GROUP_PHRASE)

    expected_nested = {
        'm-chp2-seci-l95-106-0044': CHP2_GROUP_SPAN,
        'm-chp2-seci-l95-106-0045': CHP2_GROUP_SPAN,
        'm-chp2-seci-l95-106-0046': CHP2_GROUP_SPAN,
        'm-chp2-seci-l108-119-0032': PALACE_GROUP_SPAN,
        'm-chp2-seci-l108-119-0033': PALACE_GROUP_SPAN,
        'm-chp2-seci-l108-119-0034': PALACE_GROUP_SPAN,
        'm-chp2-seci-l108-119-0035': PALACE_GROUP_SPAN,
        'm-chp2-seci-l108-119-0036': PALACE_GROUP_SPAN,
    }
    for mention_id, outer in expected_nested.items():
        row = mention_by_id.get(mention_id)
        if not row:
            raise SystemExit(f'nested source mention missing: {mention_id}')
        start, end = int(row['start_char']), int(row['end_char'])
        if not (outer[0] <= start < end <= outer[1]):
            raise SystemExit(f'nested span changed: {mention_id}')
    venetian_term = mention_by_id.get('m-chp2-seci-l95-106-0045')
    if not venetian_term or not (VENETIAN_MASTERS_SPAN[0] <= int(venetian_term['start_char']) < int(venetian_term['end_char']) <= VENETIAN_MASTERS_SPAN[1]):
        raise SystemExit('Venetian art-tradition mention is not nested in the unnamed masters phrase')

    expected_old_rows = {
        **{sid: ('palace_paintings_by_artist_reported', 'cand-4343', artist) for sid, artist in PALACE_ARTIST_IDS.items()},
        **{sid: ('collection_contents_reported', 'cand-1200', artist[0] if sid != 'st-chp2-seci-l95-106-venetian-collection' else 'cand-4319') for sid, artist in CHP2_ARTIST_IDS.items()},
    }
    for sid, expected in expected_old_rows.items():
        row = statement_by_id.get(sid)
        if not row or (row.get('predicate'), row.get('subject_candidate_id'), row.get('object_candidate_id')) != expected:
            raise SystemExit(f'statement changed before review: {sid}')
        if (row.get('qualifiers') or {}).get('relation_candidate') is not None:
            raise SystemExit(f'statement was already classified: {sid}')

    existing_mentions_by_segment = collections.defaultdict(list)
    for row in mention_rows:
        existing_mentions_by_segment[row['segment_id']].append(row)
    for group in NEW_MENTIONS:
        start, end = int(group['start_char']), int(group['end_char'])
        for row in existing_mentions_by_segment[group['segment_id']]:
            other_start, other_end = int(row['start_char']), int(row['end_char'])
            overlap = other_start < end and start < other_end
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if overlap and not nested:
                raise SystemExit(f'new mention crosses existing span: {group["mention_id"]} / {row["mention_id"]}')
    if not (VENETIAN_MASTERS_SPAN[0] > CHP2_GROUP_SPAN[0] and VENETIAN_MASTERS_SPAN[1] < CHP2_GROUP_SPAN[1]):
        raise SystemExit('unnamed-master mention must be nested in the additional-paintings group')

    candidate_additions = []
    for candidate_id, info in NEW_CANDIDATES.items():
        candidate_additions.append({
            'candidate_id': candidate_id,
            'index_entry_id': '',
            'canonical_name': info['canonical_name'],
            'index_page_range': '',
            'suggested_type': info['suggested_type'],
            'status': 'open',
            'index_source_file': '',
            'sub_entry': '',
            'detail': info['detail'],
            'exclude_reason': '',
            'candidate_origin': 'body-mention',
            'candidate_source_ref': info['candidate_source_ref'],
        })
    for row in candidate_additions:
        if set(row) != set(candidate_fields):
            raise SystemExit('candidate CSV schema mismatch')
    for row in NEW_MENTIONS:
        if set(row) != set(mention_fields):
            raise SystemExit('mention CSV schema mismatch')

    updated = []
    for old in statement_rows:
        sid = old['statement_id']
        if sid not in expected_old_rows:
            updated.append(old)
            continue
        row = dict(old)
        q = dict(row.get('qualifiers') or {})
        if sid in PALACE_ARTIST_IDS:
            artist = PALACE_ARTIST_IDS[sid]
            row.update({'subject_candidate_id': artist, 'object_candidate_id': 'cand-11567', 'predicate': 'creator_of'})
            q.update({
                'claim': f'Haskell attributes paintings in the source-defined Maffeo Barberini palace group at least in part to {candidate_by_id[artist]["canonical_name"]}.',
                'qualification': 'The aggregate phrase includes this named artist among old masters whose paintings decorated the palace. “Such as” and “and others” make the artist list non-exhaustive; individual works, titles, counts, and dates are unknown. The group-level statement does not mean every member was made by this artist.',
                'mentioned_candidate_ids': ['cand-4343', artist, 'cand-11567'],
                'relation_candidate': True,
                'relation_candidate_note': 'S2 creator_of candidate for an explicitly source-bounded aggregate. The artist is attributed some member(s) of the group; no individual work or formal S6 edge is asserted.',
            })
        else:
            subject, label = CHP2_ARTIST_IDS[sid]
            row.update({'subject_candidate_id': subject, 'object_candidate_id': 'cand-11568', 'predicate': 'creator_of'})
            if sid == 'st-chp2-seci-l95-106-carracci-collection':
                qualification = 'The source attributes some of the additional paintings to “the Carracci” collectively; no individual member is assigned a work. The group candidate cand-4318 has no established type, so any formal S6 edge remains pending type review.'
                note = 'S2 creator_of candidate for a source-bounded group; the collective creator endpoint remains untyped pending later type review. No formal S6 edge is asserted.'
                mentioned = ['cand-4318', 'cand-11568']
            elif sid == 'st-chp2-seci-l95-106-venetian-collection':
                qualification = 'The source names “the great masters of the Venetian High Renaissance” as an unnamed creator collective. The term candidate cand-4319 describes the artistic tradition and remains distinct; no individuals or group membership are identified. The creator candidate remains untyped, pending type review.'
                note = 'S2 creator_of candidate for the source-named but individually unidentified masters; keep distinct from term cand-4319. The collective creator endpoint remains untyped, so no formal S6 edge is asserted.'
                mentioned = ['cand-11569', 'cand-4319', 'cand-11568']
            else:
                qualification = 'The source attributes some additional paintings to Luca Cambiaso. Individual works, titles, counts, and dates are not supplied; the group is not an inventory.'
                note = 'S2 creator_of candidate for some members of the source-bounded aggregate; no individual work or formal S6 edge is asserted.'
                mentioned = [subject, 'cand-11568']
            q.update({
                'source_line_start': 101,
                'source_line_end': 102,
                'claim': f'Haskell attributes some of the source-defined additional paintings in Giustiniani’s large room to {label}.',
                'qualification': qualification,
                'mentioned_candidate_ids': mentioned,
                'relation_candidate': True,
                'relation_candidate_note': note,
            })
            row['original_quote'] = CHP2_GROUP_PHRASE
        row['qualifiers'] = q
        updated.append(row)

    palace_text = segment_texts[CHP2_PALACE_SEGMENT]
    palace_quote_start = palace_text.index('He decorated his palace with ')
    palace_quote = palace_text[palace_quote_start:PALACE_GROUP_SPAN[1]]
    group_text = segment_texts[CHP2_SEGMENT]
    room_quote_start = group_text.index('In the ‘large room with old pictures’')
    room_quote = group_text[room_quote_start:CHP2_GROUP_SPAN[1]]
    new_statements = [
        make_statement(
            'st-chp2-seci-l108-119-old-master-paintings-location', CHP2_PALACE_SEGMENT,
            '02-sources/02-Markdown/02_CHP-2_sec_i.md', 113, 114,
            'cand-4343', 'cand-11567', 'location_of',
            'Haskell says Maffeo Barberini decorated his palace with the source-defined group of old-master paintings.',
            palace_quote, ['cand-4343', 'cand-11567'],
            'The source gives the group a palace setting but no inventory, individual titles, exact count, or installation dates.',
            'S2 location candidate for the source-defined paintings in the palace; this does not assert ownership or identify the building. No formal S6 edge is created.',
            '30', 11,
        ),
        make_statement(
            'st-chp2-seci-l95-106-other-paintings-location', CHP2_SEGMENT,
            '02-sources/02-Markdown/02_CHP-2_sec_i.md', 101, 102,
            'cand-4315', 'cand-11568', 'location_of',
            'Haskell says the source-defined additional paintings hung in Giustiniani’s large room.',
            room_quote, ['cand-4315', 'cand-11568'],
            'The source says the thirteen Caravaggio paintings hung in the room “along with” these additional paintings; individual titles and complete membership are unknown.',
            'S2 location candidate based on the explicit display context; no ownership of any individual work or formal S6 edge is asserted.',
            '29', 10,
        ),
        make_statement(
            'st-chp2-seci-l95-106-other-paintings-part-of-collection', CHP2_SEGMENT,
            '02-sources/02-Markdown/02_CHP-2_sec_i.md', 98, 102,
            'cand-11568', 'cand-4313', 'part_of',
            'Haskell places the source-defined additional paintings within Vincenzo Giustiniani’s painting collection described in the same passage.',
            group_text[group_text.index('The Marchese Vincenzo Giustiniani'):CHP2_GROUP_SPAN[1]],
            ['cand-11568', 'cand-4313'],
            'This collection membership is resolved from the paragraph’s continuous account: Giustiniani is filling his palace with a remarkable collection of paintings, followed by the works hung in a room of that palace. It does not establish a complete inventory or ownership of individually unidentified works.',
            'S2 contextual part_of candidate linking the described group to the painting-collection candidate. The collection candidate has no established type, so S6 type validation remains pending.',
            '29', 10,
        ),
    ]
    updated.extend(new_statements)

    def add_candidate_defaults(candidate_id: str, info: dict) -> dict[str, str]:
        return {
            'candidate_id': candidate_id,
            'index_entry_id': '',
            'canonical_name': info['canonical_name'],
            'index_page_range': '',
            'suggested_type': info['suggested_type'],
            'status': 'open',
            'index_source_file': '',
            'sub_entry': '',
            'detail': info['detail'],
            'exclude_reason': '',
            'candidate_origin': 'body-mention',
            'candidate_source_ref': info['candidate_source_ref'],
        }

    # Candidate rows were assembled above for schema validation; use the same exact data.
    updated_candidate_rows = [add_candidate_defaults(cid, info) for cid, info in NEW_CANDIDATES.items()]
    output_text = '\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in updated) + '\n'
    new_files = {
        CANDIDATES: append_csv_rows(originals[CANDIDATES], updated_candidate_rows),
        MENTIONS: append_csv_rows(originals[MENTIONS], NEW_MENTIONS),
        STATEMENTS: output_text.encode('utf-8'),
    }
    true_rows = [row for row in updated if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in true_rows)
    counts = (len(candidate_rows) + 3, len(mention_rows) + 3, len(updated), len(true_rows), complete, len(true_rows) - complete)
    if counts != (11547, 27480, 12650, 3486, 3472, 14):
        raise SystemExit(f'unexpected post-state counts: {counts}')

    return originals, new_files, {
        'candidate_ids': list(NEW_CANDIDATES),
        'mention_ids': [row['mention_id'] for row in NEW_MENTIONS],
        'rewritten_statement_ids': sorted(expected_old_rows),
        'added_statement_ids': sorted(NEW_STATEMENT_IDS),
        'counts': {'candidates': counts[0], 'mentions': counts[1], 'statements': counts[2], 'relation_candidates': counts[3], 'complete_endpoints': counts[4], 'open_endpoints': counts[5]},
        'before_sha256': hashes,
        'after_sha256': {path.name: sha256(data) for path, data in new_files.items()},
        'group_mentions': [
            {'mention_id': row['mention_id'], 'span': [int(row['start_char']), int(row['end_char'])], 'surface_form': row['surface_form']}
            for row in NEW_MENTIONS
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    originals, new_files, report = prepare()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    for path, backup in BACKUPS.items():
        if backup.exists():
            raise SystemExit(f'backup already exists: {backup}')
        shutil.copy2(path, backup)
    for path, data in new_files.items():
        path.write_bytes(data)
    final_hashes = {path.name: sha256(path.read_bytes()) for path in new_files}
    expected_after = {path.name: sha256(data) for path, data in new_files.items()}
    if final_hashes != expected_after:
        raise SystemExit(f'write verification failed: {final_hashes}')
    print('applied; recovery copies written; hashes verified')


if __name__ == '__main__':
    main()
