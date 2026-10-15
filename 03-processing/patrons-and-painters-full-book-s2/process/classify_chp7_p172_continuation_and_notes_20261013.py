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
COMPOSITE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
EXPECTED_HASHES = {
    STATEMENTS.name: '0536c9561e55225dba27caa60f0f85e8b2c9bd8e9e5bfde8a63bf316cde6e194',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + '.bak-s2-chp7-p172-l301-notes-20261013'
)

BODY_CLASSIFICATIONS = {
    'st-chp7-p172-cont-i01': False,
    'st-chp7-p172-cont-i02': True,
    'st-chp7-p172-cont-i03': True,
    'st-chp7-p172-cont-i04': True,
    'st-chp7-p172-cont-i05': True,
    'st-chp7-p172-cont-i06': True,
    'st-chp7-p172-cont-i07': True,
    'st-chp7-p172-cont-i08': True,
    'st-chp7-p172-cont-i09': True,
    'st-chp7-p172-cont-i10': False,
    'st-chp7-p172-cont-i11': True,
    'st-chp7-p172-cont-i12': True,
    'st-chp7-p172-cont-i13': True,
    'st-chp7-p172-cont-i14': True,
    'st-chp7-p172-cont-i15': True,
    'st-chp7-p172-cont-i16': True,
    'st-chp7-p172-cont-i17': False,
}

CHILDREN = [
    {
        'statement_id': 'st-chp7-p172-cont-i07-monterey-influence-cathedral-authorities',
        'parent_statement_id': 'st-chp7-p172-cont-i07',
        'subject_candidate_id': 'cand-1693',
        'object_candidate_id': 'cand-7008',
        'predicate': 'influenced',
        'claim': 'Haskell says Monterey used his influence with the authorities of Naples Cathedral while seeking a much larger share of its decoration for Finelli.',
        'qualification': 'The authorities and original plan are unnamed; the related outcome and Fanzago opposition are recorded in the neighboring source statements.',
        'relation_candidate_note': 'Records the explicit influence relation between Monterey and the Cathedral authorities; it does not claim that the authorities accepted without opposition.',
        'mentioned_candidate_ids': ['cand-1693', 'cand-7008', 'cand-3117', 'cand-1038'],
        'footnote_marker': 1,
        'footnote_line': 302,
    },
    {
        'statement_id': 'st-chp7-p172-cont-i10-ribera-employed-by-monterey',
        'parent_statement_id': 'st-chp7-p172-cont-i10',
        'subject_candidate_id': 'cand-2140',
        'object_candidate_id': 'cand-1693',
        'predicate': 'employed_by',
        'claim': 'Haskell says Ribera was employed by the Count of Monterey in connection with a number of altarpieces for the Viceroy’s Augustinian church.',
        'qualification': 'This records the source’s employment wording; it does not supply a contract or independently establish completion of the works.',
        'relation_candidate_note': 'A direct artist–employer candidate supported by “he employed his compatriot Ribera”; the works and church remain separately represented.',
        'mentioned_candidate_ids': ['cand-2140', 'cand-1693', 'cand-7010', 'cand-7009'],
    },
    {
        'statement_id': 'st-chp7-p172-cont-i10-altarpieces-engaged-artist',
        'parent_statement_id': 'st-chp7-p172-cont-i10',
        'subject_candidate_id': 'cand-7010',
        'object_candidate_id': 'cand-2140',
        'predicate': 'engaged_artist_for',
        'claim': 'Haskell says Ribera was employed on the unidentified group of altarpieces.',
        'qualification': 'The passage records engagement on the works, not their titles or independent proof that every work was completed.',
        'relation_candidate_note': 'Preserves the explicit artist-to-work engagement without upgrading it to an unqualified authorship or ownership claim.',
        'mentioned_candidate_ids': ['cand-7010', 'cand-2140'],
    },
    {
        'statement_id': 'st-chp7-p172-cont-i10-altarpieces-intended-for-church',
        'parent_statement_id': 'st-chp7-p172-cont-i10',
        'subject_candidate_id': 'cand-7010',
        'object_candidate_id': 'cand-7009',
        'predicate': 'intended_for',
        'claim': 'Haskell says the unidentified group of Ribera altarpieces was for Monterey’s Augustinian church.',
        'qualification': 'The church is unnamed and remains distinct from the Salamanca church candidate; the passage does not establish ownership.',
        'relation_candidate_note': 'Records the expressly stated destination of the altarpiece group while preserving the unidentified church endpoint.',
        'mentioned_candidate_ids': ['cand-7010', 'cand-7009', 'cand-1693'],
    },
]

P172_CITATIONS = {
    'st-chp7-p172-n1-cite-passeri': {
        'publication_id': 'cand-4376', 'author_id': 'cand-1856',
        'locator': 'Passeri, p. 251', 'marker': 1, 'line': 302,
        'body_ids': ['st-chp7-p172-cont-i07', 'st-chp7-p172-cont-i07-monterey-influence-cathedral-authorities', 'st-chp7-p172-cont-i08'],
    },
    'st-chp7-p172-n2-cite-trapier': {
        'publication_id': 'cand-7002', 'author_id': 'cand-7015',
        'locator': 'Trapier, p. 72', 'marker': 2, 'line': 303,
        'body_ids': ['st-chp7-p172-cont-i12'],
    },
    'st-chp7-p172-n3-cite-costello': {
        'publication_id': 'cand-7017', 'author_id': 'cand-7016',
        'locator': 'Costello, p. 247', 'marker': 3, 'line': 304,
        'body_ids': ['st-chp7-p172-i04'],
    },
    'st-chp7-p172-n4-cite-blunt': {
        'publication_id': 'cand-7018', 'author_id': 'cand-0379',
        'locator': 'Blunt, 1959, pp. 389–390', 'marker': 4, 'line': 305,
        'body_ids': ['st-chp7-p172-i05'],
    },
    'st-chp7-p172-n4-cite-rothlisberger': {
        'publication_id': 'cand-4577', 'author_id': 'cand-3502',
        'locator': 'Röthlisberger, 1961, vol. I, pp. 155–160', 'marker': 4, 'line': 305,
        'body_ids': ['st-chp7-p172-i05'],
    },
}

# The already classified p.170–171 notes are linked back to the exact marked statements.
EXISTING_NOTE_LINKS = {
    294: (1, ['st-chp7-p170-i15'], ['st-chp7-p170-n1-cite']),
    295: (1, ['st-chp7-p171-i08'], ['st-chp7-p171-n1-cite']),
    296: (2, ['st-chp7-p171-i11'], ['st-chp7-p171-n2-cite']),
    297: (3, ['st-chp7-p171-i13'], ['st-chp7-p171-n3-cite']),
    298: (4, ['st-chp7-p171-i17'], ['st-chp7-p171-n4-cite']),
    299: (5, ['st-chp7-p171-i21'], ['st-chp7-p171-n5-cite']),
    300: (6, ['st-chp7-p171-i23'], [
        'st-chp7-p171-n6-cite-passeri',
        'st-chp7-p171-n6-cite-trapier',
        'st-chp7-p171-n6-series-located-prado',
        'st-chp7-p171-n6-series-painted-for-king',
        'st-chp7-p171-n6-series-partly-lanfranco',
    ]),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_candidates() -> dict[str, dict[str, str]]:
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        return {row['candidate_id']: row for row in csv.DictReader(f)}


def add_body_ref(q: dict, marker: int, line: int, statement_ids: list[str]) -> None:
    refs = list(q.get('footnote_refs') or [])
    ref = next((item for item in refs if item.get('marker') == marker), None)
    if ref is None:
        ref = {'marker': marker, 'segment_id': COMPOSITE_SEGMENT, 'source_line': line}
        refs.append(ref)
    elif ref.get('segment_id') != COMPOSITE_SEGMENT or ref.get('source_line') != line:
        raise SystemExit(f'footnote ref locator changed for marker {marker}')
    ref['statement_ids'] = statement_ids
    q['footnote_refs'] = refs
    q['footnote_marker'] = marker
    q['footnote_number'] = marker
    q['footnote_segment'] = COMPOSITE_SEGMENT
    q['footnote_statement_ids'] = statement_ids
    q['footnote_link_status'] = 'linked'
    q['footnote_text_pending'] = False


def set_note_link(row: dict, marker: int, line: int, body_ids: list[str]) -> None:
    q = dict(row.get('qualifiers') or {})
    q['footnote_marker'] = marker
    q['footnote_number'] = marker
    q['footnote_segment'] = COMPOSITE_SEGMENT
    q['footnote_refs'] = [{
        'marker': marker,
        'segment_id': COMPOSITE_SEGMENT,
        'source_line': line,
        'statement_ids': body_ids,
    }]
    q['related_body_statement_ids'] = body_ids
    q['linked_body_statement_ids'] = body_ids
    q['footnote_link_status'] = 'linked'
    q['footnote_text_pending'] = False
    row['qualifiers'] = q


def prepare() -> tuple[bytes, bytes, dict]:
    before = STATEMENTS.read_bytes()
    candidate_bytes = CANDIDATES.read_bytes()
    hashes = {
        STATEMENTS.name: digest(before),
        CANDIDATES.name: digest(candidate_bytes),
        SOURCE.name: digest(SOURCE.read_bytes()),
        PDF.name: digest(PDF.read_bytes()),
    }
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')

    candidate_by_id = load_candidates()
    for cid in ['cand-2962', 'cand-2140', 'cand-1693', 'cand-7008', 'cand-7010', 'cand-7009']:
        if cid not in candidate_by_id:
            raise SystemExit(f'required candidate is missing: {cid}')
    if candidate_by_id[SOURCE_BOOK_ID]['suggested_type'] != 'archive':
        raise SystemExit('Haskell book candidate is not archive typed')
    if candidate_by_id['cand-7008']['suggested_type'] != 'institution':
        raise SystemExit('Cathedral authorities candidate type changed')
    if candidate_by_id['cand-7010']['suggested_type'] != 'work' or candidate_by_id['cand-7009']['suggested_type'] != 'place':
        raise SystemExit('altarpiece or church candidate type changed')

    rows = [json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    required_ids = set(BODY_CLASSIFICATIONS) | set(P172_CITATIONS)
    required_ids.update(sid for _, _, note_ids in EXISTING_NOTE_LINKS.values() for sid in note_ids)
    required_ids.update(sid for _, body_ids, _ in EXISTING_NOTE_LINKS.values() for sid in body_ids)
    required_ids.update(['st-chp7-p172-i04', 'st-chp7-p172-i05'])
    required_ids.update(child['statement_id'] for child in CHILDREN)
    missing = required_ids - set(by_id)
    existing_children = {child['statement_id'] for child in CHILDREN} & set(by_id)
    if missing - {child['statement_id'] for child in CHILDREN}:
        raise SystemExit(f'required statement IDs are missing: {sorted(missing)}')
    if existing_children:
        raise SystemExit(f'new child statement IDs already exist: {sorted(existing_children)}')

    for sid in BODY_CLASSIFICATIONS:
        row = by_id[sid]
        q = row.get('qualifiers') or {}
        if row.get('segment_id') != COMPOSITE_SEGMENT or q.get('source_line_start') != 301 or q.get('relation_candidate') is not None:
            raise SystemExit(f'p.172 body statement changed since review: {sid}')
    for sid, spec in P172_CITATIONS.items():
        row = by_id[sid]
        q = row.get('qualifiers') or {}
        if (row.get('predicate') != 'footnote_citation' or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id'] or q.get('relation_candidate') is not None):
            raise SystemExit(f'p.172 citation changed since review: {sid}')

    output_by_id = {sid: dict(row) for sid, row in by_id.items()}

    for sid, is_relation in BODY_CLASSIFICATIONS.items():
        row = output_by_id[sid]
        q = dict(row.get('qualifiers') or {})
        q['relation_candidate'] = is_relation
        if sid == 'st-chp7-p172-cont-i10':
            q['relation_candidate_note'] = 'This source sentence combines an artist-employment claim, the artist’s engagement on a work group, and the group’s intended church. Keep this aggregate parent for traceability; the three binary S2 candidates are listed in related_statement_ids.'
            q['related_statement_ids'] = [
                'st-chp7-p172-cont-i10-ribera-employed-by-monterey',
                'st-chp7-p172-cont-i10-altarpieces-engaged-artist',
                'st-chp7-p172-cont-i10-altarpieces-intended-for-church',
            ]
        elif sid == 'st-chp7-p172-cont-i07':
            q['related_statement_ids'] = ['st-chp7-p172-cont-i07-monterey-influence-cathedral-authorities']
        elif sid == 'st-chp7-p172-cont-i01':
            q['relation_candidate_note'] = 'Nonrelation: this fragment only closes the already classified p.171 statement st-chp7-p171-i24 by supplying its Cathedral destination; it is retained as a continuation link, not counted as a second relation.'
        elif sid == 'st-chp7-p172-cont-i17':
            q['relation_candidate_note'] = 'Nonrelation: this is an open-ended rhetorical speculation about possible future conditions, with no identifiable event or relationship endpoint.'
        else:
            q['relation_candidate_note'] = {
                'st-chp7-p172-cont-i01': 'S2 relation candidate: completes the cross-page movement claim by naming Naples Cathedral as Finelli’s work destination.',
                'st-chp7-p172-cont-i02': 'S2 relation candidate: records Monterey taking Finelli up at the Cathedral; the phrase is Haskell’s account of patronage, not a formal appointment.',
                'st-chp7-p172-cont-i03': 'S2 relation candidate: Monterey commissioned the unidentified pair of life-size portraits.',
                'st-chp7-p172-cont-i04': 'S2 relation candidate: the source states Monterey was one sitter in the paired portraits.',
                'st-chp7-p172-cont-i05': 'S2 relation candidate: the source states Monterey’s unnamed wife was the other sitter.',
                'st-chp7-p172-cont-i06': 'S2 relation candidate: preserves the source’s explicit spousal identification without adding a personal identity.',
                'st-chp7-p172-cont-i07': 'S2 relation candidate: Monterey sought a larger share in the Cathedral decoration for Finelli; the influence on the Cathedral authorities is separately recorded below.',
                'st-chp7-p172-cont-i08': 'S2 relation candidate: records Fanzago’s opposition to the larger decoration share sought for Finelli; the outcome is unstated.',
                'st-chp7-p172-cont-i09': 'S2 relation candidate: records Haskell’s qualified patronage contrast between Monterey and the Neapolitan school.',
                'st-chp7-p172-cont-i11': 'S2 relation candidate: records Haskell’s explicitly possible stylistic concession between the altarpieces and Monterey’s stated taste; it is not direct testimony from Ribera.',
                'st-chp7-p172-cont-i12': 'S2 relation candidate: records Haskell’s claim that Ribera and other city painters owed much to Monterey’s patronage.',
                'st-chp7-p172-cont-i13': 'S2 relation candidate: links the source-defined Neapolitan group to witnessing Monterey’s departure; the mixed reaction remains Haskell’s inference.',
                'st-chp7-p172-cont-i14': 'S2 relation candidate: records Monterey’s dated departure and the reported forty shiploads without supplying a destination or inventory.',
                'st-chp7-p172-cont-i15': 'S2 relation candidate: records Haskell’s characterization of Monterey’s extraction of provincial people and money for the Spanish war effort.',
                'st-chp7-p172-cont-i16': 'S2 relation candidate: preserves Haskell’s causal evaluation of Monterey’s conduct and the arts in Naples.',
            }.get(sid, 'S2 relation candidate based on the explicit source statement; authorial scope and uncertainty are preserved in qualification.')
        row['qualifiers'] = q

    for spec in P172_CITATIONS.values():
        row = output_by_id[next(sid for sid, value in P172_CITATIONS.items() if value is spec)]
        pub_id = spec['publication_id']
        pub_name = candidate_by_id[pub_id]['canonical_name']
        q = dict(row.get('qualifiers') or {})
        old_claim = str(q.get('claim') or '').strip()
        row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': pub_id, 'predicate': 'cites'})
        q.update({
            'claim': f"Haskell’s book cites {pub_name} at {spec['locator']} in this footnote. The prior note records: {old_claim}",
            'citation_publication_candidate_id': pub_id,
            'citation_locator': spec['locator'],
            'citations': [{'source_candidate_id': pub_id, 'publication_candidate_id': pub_id, 'locator': spec['locator']}],
            'cited_material_not_independently_consulted': True,
            'relation_candidate': True,
            'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator. This records Haskell’s bibliographic reference only; the cited material was not independently consulted and no S6 edge is created.',
        })
        if spec.get('author_id'):
            q['citation_candidate_id'] = spec['author_id']
        set_note_link(row, spec['marker'], spec['line'], spec['body_ids'])
        # set_note_link updates the row qualifier, so keep the citation fields as well.
        q.update(row['qualifiers'])
        row['qualifiers'] = q

    for child in CHILDREN:
        q = {
            'source_line_start': 301,
            'source_line_end': 301,
            'print_page': 172,
            'pdf_physical_page': 6,
            'claim': child['claim'],
            'speaker': 'Haskell',
            'text_layer': 'authorial narrative',
            'qualification': child['qualification'],
            'mentioned_candidate_ids': child['mentioned_candidate_ids'],
            'parent_statement_id': child['parent_statement_id'],
            'relation_candidate': True,
            'relation_candidate_note': child['relation_candidate_note'],
        }
        if child.get('footnote_marker'):
            marker = child['footnote_marker']
            note_ids = [sid for sid, spec in P172_CITATIONS.items() if spec['marker'] == marker]
            q.update({
                'footnote_marker': marker,
                'footnote_number': marker,
                'footnote_segment': COMPOSITE_SEGMENT,
                'footnote_refs': [{'marker': marker, 'segment_id': COMPOSITE_SEGMENT, 'source_line': child['footnote_line'], 'statement_ids': note_ids}],
                'footnote_statement_ids': note_ids,
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
            })
        output_by_id[child['statement_id']] = {
            'statement_id': child['statement_id'],
            'segment_id': COMPOSITE_SEGMENT,
            'subject_candidate_id': child['subject_candidate_id'],
            'object_candidate_id': child['object_candidate_id'],
            'predicate': child['predicate'],
            'qualifiers': q,
            'original_quote': output_by_id[child['parent_statement_id']]['original_quote'],
            'origin': 'book',
            'source_file': '02-sources/02-Markdown/07_CHP-7_sec_i.md',
        }

    # Keep note records and their body anchors mutually navigable, including p.170–171 notes already classified.
    for line, (marker, body_ids, note_ids) in EXISTING_NOTE_LINKS.items():
        for sid in note_ids:
            row = output_by_id[sid]
            set_note_link(row, marker, line, body_ids)
        for body_id in body_ids:
            row = output_by_id[body_id]
            q = dict(row.get('qualifiers') or {})
            add_body_ref(q, marker, line, note_ids)
            row['qualifiers'] = q

    # Add the p.172 note references to the existing first-paragraph and later body statements.
    body_note_map = {
        'st-chp7-p172-cont-i07': (1, 302, ['st-chp7-p172-n1-cite-passeri'], ['st-chp7-p172-cont-i07', 'st-chp7-p172-cont-i07-monterey-influence-cathedral-authorities', 'st-chp7-p172-cont-i08']),
        'st-chp7-p172-cont-i08': (1, 302, ['st-chp7-p172-n1-cite-passeri'], ['st-chp7-p172-cont-i07', 'st-chp7-p172-cont-i07-monterey-influence-cathedral-authorities', 'st-chp7-p172-cont-i08']),
        'st-chp7-p172-cont-i12': (2, 303, ['st-chp7-p172-n2-cite-trapier'], ['st-chp7-p172-cont-i12']),
        'st-chp7-p172-i04': (3, 304, ['st-chp7-p172-n3-cite-costello'], ['st-chp7-p172-i04']),
        'st-chp7-p172-i05': (4, 305, ['st-chp7-p172-n4-cite-blunt', 'st-chp7-p172-n4-cite-rothlisberger'], ['st-chp7-p172-i05']),
    }
    for body_id, (marker, line, note_ids, related_body_ids) in body_note_map.items():
        row = output_by_id[body_id]
        q = dict(row.get('qualifiers') or {})
        add_body_ref(q, marker, line, note_ids)
        row['qualifiers'] = q
        for note_id in note_ids:
            set_note_link(output_by_id[note_id], marker, line, related_body_ids)

    added = [child['statement_id'] for child in CHILDREN]
    ordered = []
    for row in rows:
        ordered.append(output_by_id[row['statement_id']])
        if row['statement_id'] == 'st-chp7-p172-cont-i10':
            ordered.extend(output_by_id[sid] for sid in added if output_by_id[sid]['qualifiers'].get('parent_statement_id') == row['statement_id'])
        elif row['statement_id'] == 'st-chp7-p172-cont-i07':
            ordered.extend(output_by_id[sid] for sid in added if output_by_id[sid]['qualifiers'].get('parent_statement_id') == row['statement_id'])
    text = '\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in ordered) + '\n'
    after = text.encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in ordered),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in ordered),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in ordered),
    }
    if (len(ordered), counts) != (14187, {True: 8415, False: 3419, 'unset': 2353}):
        raise SystemExit(f'unexpected post-state: rows={len(ordered)}, counts={counts}')
    return before, after, {
        'mode': 'dry_run',
        'classified_p172_body': {'true': 14, 'false': 3, 'existing': 17},
        'normalized_p172_citations': len(P172_CITATIONS),
        'added_statements': added,
        'p170_172_note_links_closed': sum(len(v[2]) for v in EXISTING_NOTE_LINKS.values()) + len(P172_CITATIONS),
        'post_counts': {'statements': len(ordered), **{str(k): v for k, v in counts.items()}},
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
