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
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l150-158'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: 'a469680faf40e6efe57a687b637b7d695e4713a38a9b192f580c24eab3d26bdf',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p182-notes-20261013')

CITATIONS = {
    'st-chp7-p182-n1-cite-prunieres': {
        'publication_id': 'cand-4861', 'locator': 'Prunières, L’opéra italien en France avant Lulli (1913), p. 68',
        'marker': 1, 'line': 343, 'body_ids': ['st-chp7-p182-i10', 'st-chp7-p182-i11'],
    },
    'st-chp7-p182-n1-cite-bjurstrom': {
        'publication_id': 'cand-7075', 'locator': 'Bjurström, Giacomo Torelli and Baroque Stage Design (1961)',
        'marker': 1, 'line': 343, 'body_ids': ['st-chp7-p182-i10', 'st-chp7-p182-i11'],
    },
    'st-chp7-p182-n2-cite-felibien': {
        'publication_id': 'cand-7077', 'locator': 'Félibien, Entretiens, vol. III, p. 530',
        'marker': 2, 'line': 344, 'body_ids': ['st-chp7-p182-i12'],
    },
    'st-chp7-p182-n3-cite-malvasia': {
        'publication_id': 'cand-6933', 'locator': 'Malvasia, Felsina Pittrice, vol. II, p. 264',
        'marker': 3, 'line': 345, 'body_ids': ['st-chp7-p182-i14'],
    },
    'st-chp7-p182-n4-cite-malvasia': {
        'publication_id': 'cand-6933', 'locator': 'Malvasia, Felsina Pittrice, vol. II, p. 327 (ibid. to footnote 3)',
        'marker': 4, 'line': 346, 'body_ids': ['st-chp7-p182-i17'],
    },
    'st-chp7-p182-n5-cite-rothlisberger': {
        'publication_id': 'cand-4577', 'locator': 'Röthlisberger, Claude Lorrain—The Paintings (1961), vol. I, p. 274',
        'marker': 5, 'line': 347, 'body_ids': ['st-chp7-p182-i18'],
        'ocr_corrections': [{'source_line': 347, 'ocr': '8 Rothlisberger, 1961,1', 'print_reading': '5 Röthlisberger, 1961, I', 'basis': 'CHP-7.pdf physical page 16'}],
    },
}

CLAIMS = {
    'st-chp7-p182-n5-claude-recorded-parasson': {
        'subject': 'cand-0780', 'predicate': 'reported_purchaser_in_claude_record', 'object': 'cand-7074',
        'note': 'This preserves Haskell’s report through Röthlisberger that Claude recorded M. Parasson as purchaser; the record was not independently consulted.',
    },
    'st-chp7-p182-n5-mazarin-owned-by-1653': {
        'subject': 'cand-0780', 'predicate': 'reported_owner_by_date', 'object': 'cand-1588',
        'note': 'This records the source-attributed claim that the picture belonged to Mazarin by 1653; the exact acquisition date is not supplied.',
    },
    'st-chp7-p182-n5-picture-dresden': {
        'subject': 'cand-0780', 'predicate': 'reported_current_location', 'object': 'cand-0947',
        'note': 'This records the location given in Haskell’s footnote; no specific Dresden repository is named.',
    },
    'st-chp7-p182-n5-probable-agent': {
        'subject': 'cand-0780', 'predicate': 'probable_creation_for_mazarin_via_agent', 'object': 'cand-1588',
        'note': 'This preserves Röthlisberger’s probability assessment as reported by Haskell; the unnamed intermediary and possible commission remain unverified.',
        'open_endpoint_reason': 'The agent is unnamed, and the reported probability does not establish a confirmed commission or identify an intermediary.',
    },
}

LINKS = {
    **{key: (value['marker'], value['line'], value['body_ids']) for key, value in CITATIONS.items()},
    **{key: (5, 347, ['st-chp7-p182-i18']) for key in CLAIMS},
}
SOURCE_GUARDS = {
    343: 'Prunieres, 1913, p. 68; Bjurstrom, 1961.',
    344: 'Felibien, III, p. 530.',
    345: 'Malvasia, II, p. 264.',
    346: 'ibid., II, p. 327.',
    347: '8 Rothlisberger, 1961,1, p. 274',
}
EXPECTED_BODY_LINKS = {
    'st-chp7-p182-i10': {'st-chp7-p182-n1-cite-prunieres', 'st-chp7-p182-n1-cite-bjurstrom'},
    'st-chp7-p182-i11': {'st-chp7-p182-n1-cite-prunieres', 'st-chp7-p182-n1-cite-bjurstrom'},
    'st-chp7-p182-i12': {'st-chp7-p182-n2-cite-felibien'},
    'st-chp7-p182-i14': {'st-chp7-p182-n3-cite-malvasia'},
    'st-chp7-p182-i17': {'st-chp7-p182-n4-cite-malvasia'},
    'st-chp7-p182-i18': set(CLAIMS) | {'st-chp7-p182-n5-cite-rothlisberger'},
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
    raw = {path: path.read_bytes() for path in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {path.name: sha256(content) for path, content in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')

    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    for line_no, snippet in SOURCE_GUARDS.items():
        if snippet not in source_lines[line_no - 1]:
            raise SystemExit(f'source guard failed at L{line_no}: {source_lines[line_no - 1]}')
    candidates = {
        row['candidate_id']: row for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))
    }
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source-book candidate is absent or not archive typed')
    for spec in CITATIONS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive missing or mistyped: {spec['publication_id']}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_ids = set(CITATIONS) | set(CLAIMS)
    if not expected_ids.issubset(by_id):
        raise SystemExit(f'missing p.182 note statements: {sorted(expected_ids - set(by_id))}')
    for note_id, spec in CITATIONS.items():
        row, q = by_id[note_id], by_id[note_id].get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line'] or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation row changed since review: {note_id}')
    for note_id, spec in CLAIMS.items():
        row, q = by_id[note_id], by_id[note_id].get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('subject_candidate_id') != spec['subject']
                or row.get('predicate') != spec['predicate'] or row.get('object_candidate_id') != spec['object']
                or q.get('source_line_start') != 347 or q.get('relation_candidate') is not None):
            raise SystemExit(f'note fact changed since review: {note_id}')
    for body_id, expected in EXPECTED_BODY_LINKS.items():
        if body_id not in by_id or by_id[body_id].get('segment_id') != BODY_SEGMENT:
            raise SystemExit(f'missing body statement: {body_id}')
        actual = set((by_id[body_id].get('qualifiers') or {}).get('footnote_statement_ids') or [])
        if actual != expected:
            raise SystemExit(f'body reciprocal links changed at {body_id}: {sorted(actual)}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        citation_spec = CITATIONS.get(row['statement_id'])
        claim_spec = CLAIMS.get(row['statement_id'])
        if citation_spec:
            publication_id = citation_spec['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': publication_id, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {citation_spec['locator']} in footnote {citation_spec['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id,
                'citation_locator': citation_spec['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': publication_id, 'locator': citation_spec['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': citation_spec['marker'], 'footnote_number': citation_spec['marker'],
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': citation_spec['marker'], 'segment_id': NOTE_SEGMENT,
                                   'source_line': citation_spec['line'], 'statement_ids': citation_spec['body_ids']}],
                'related_body_statement_ids': citation_spec['body_ids'],
                'linked_body_statement_ids': citation_spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; the cited publication was not independently consulted, and no S6 edge is created.',
            })
            if citation_spec.get('ocr_corrections'):
                q['ocr_corrections'] = citation_spec['ocr_corrections']
            row['qualifiers'] = q
        elif claim_spec:
            q = dict(row.get('qualifiers') or {})
            q.update({
                'relation_candidate': True, 'relation_candidate_note': claim_spec['note'],
                'footnote_marker': 5, 'footnote_number': 5, 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': 5, 'segment_id': NOTE_SEGMENT, 'source_line': 347,
                                   'statement_ids': ['st-chp7-p182-i18']}],
                'related_body_statement_ids': ['st-chp7-p182-i18'],
                'linked_body_statement_ids': ['st-chp7-p182-i18'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
            })
            if claim_spec.get('open_endpoint_reason'):
                q['open_endpoint_reason'] = claim_spec['open_endpoint_reason']
            row['qualifiers'] = q
        output.append(row)

    output_bytes = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8493, False: 3420, 'unset': 2274}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(CITATIONS), 'classified_reported_facts': len(CLAIMS),
        'reciprocal_links_checked': sum(len(ids) for ids in EXPECTED_BODY_LINKS.values()),
        'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
        'before_sha256': hashes, 'after_statement_sha256': sha256(output_bytes),
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
    atomic_write(STATEMENTS, output_bytes)
    if sha256(STATEMENTS.read_bytes()) != report['after_statement_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
