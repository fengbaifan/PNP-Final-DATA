from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / '04-knowledge' / 'tables' / 'book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge' / 'tables' / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l140-148'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: '01afb4e6bfc0e8717a1eefea6e6fec6bed4228d5d37f2aae4e41e6af4727b44d',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p181-note-classification-links-20261013')

CITATIONS = {
    'st-chp7-p181-n1-cite-brienne': {
        'publication_id': 'cand-7071',
        'locator': 'Brienne, Mémoires, vol. I (Paris 1916–19), p. 302',
        'marker': 1,
        'line': 339,
        'body_ids': ['st-chp7-p181-i05', 'st-chp7-p181-i06'],
    },
    'st-chp7-p181-n2-cite-brienne': {
        'publication_id': 'cand-7071',
        'locator': 'Brienne, Mémoires, vol. I (Paris 1916–19), pp. 293–294',
        'marker': 2,
        'line': 340,
        'body_ids': ['st-chp7-p181-i11'],
    },
    'st-chp7-p181-n3-cite-mazarin': {
        'publication_id': 'cand-7044',
        'locator': 'Mazarin, homme d’état et collectionneur 1602–1661, p. xxxiii',
        'marker': 3,
        'line': 341,
        'body_ids': ['st-chp7-p181-i26', 'st-chp7-p181-i27'],
    },
    'st-chp7-p181-n4-cite-pollak': {
        'publication_id': 'cand-4359',
        'locator': 'Pollak, “Italienische Künstlerbriefe aus der Barockzeit” (1913), p. 52',
        'marker': 4,
        'line': 342,
        'body_ids': ['st-chp7-p181-i28'],
    },
}

CLAIMS = {
    'st-chp7-p181-n1-brienne-report': {
        'marker': 1,
        'line': 339,
        'body_ids': ['st-chp7-p181-i05'],
        'note': 'This records Haskell’s report that Brienne said Mazarin owned no Poussin; it is not independent verification of Mazarin’s holdings.',
    },
    'st-chp7-p181-n1-haskell-interpretation': {
        'marker': 1,
        'line': 339,
        'body_ids': ['st-chp7-p181-i05', 'st-chp7-p181-i06'],
        'note': 'This preserves Haskell’s explicitly qualified interpretation (“almost certainly”) of Brienne’s reference; no particular painting is identified.',
        'open_endpoint_reason': 'The note refers to one of Poussin’s later works but does not identify a painting; cand-1984 identifies the artist context, not the work endpoint.',
    },
    'st-chp7-p181-n4-letter-authored-by': {
        'marker': 4,
        'line': 342,
        'body_ids': ['st-chp7-p181-i28'],
        'note': 'Haskell’s footnote identifies Romanelli as the author of the reported letter; Pollak and the letter were not independently consulted.',
    },
}

LINKS = {
    **{key: (value['marker'], value['line'], value['body_ids']) for key, value in CITATIONS.items()},
    **{key: (value['marker'], value['line'], value['body_ids']) for key, value in CLAIMS.items()},
    'st-chp7-p181-n4-letter-addressed-to': (4, 342, ['st-chp7-p181-i28']),
}

SOURCE_GUARDS = {
    339: 'In fact Brienne says (I, p. 302)',
    340: 'Brienne, I, pp. 293-4.',
    341: 'Mazarin, p. xxxiii.',
    342: 'Letter from Romanelli to Francesco Barberini of 6 July 1646',
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

    raw = {
        STATEMENTS: STATEMENTS.read_bytes(),
        CANDIDATES: CANDIDATES.read_bytes(),
        SOURCE: SOURCE.read_bytes(),
        PDF: PDF.read_bytes(),
    }
    hashes = {path.name: sha256(content) for path, content in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')

    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    for line_no, snippet in SOURCE_GUARDS.items():
        if snippet not in source_lines[line_no - 1]:
            raise SystemExit(f'source guard failed at L{line_no}: {source_lines[line_no - 1]}')

    candidates = {}
    import csv
    import io
    for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline='')):
        candidates[row['candidate_id']] = row
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell book candidate is absent or not archive typed')
    for spec in CITATIONS.values():
        target = candidates.get(spec['publication_id'])
        if not target or target.get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive missing or mistyped: {spec['publication_id']}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_ids = set(CITATIONS) | set(CLAIMS) | {'st-chp7-p181-n4-letter-addressed-to'}
    missing = expected_ids - set(by_id)
    if missing:
        raise SystemExit(f'missing p.181 note statements: {sorted(missing)}')

    for note_id, spec in CITATIONS.items():
        row = by_id[note_id]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation row changed since review: {note_id}')
    for note_id in CLAIMS:
        row = by_id[note_id]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or q.get('source_line_start') != CLAIMS[note_id]['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'claim row changed since review: {note_id}')
    addressed = by_id['st-chp7-p181-n4-letter-addressed-to']
    if ((addressed.get('qualifiers') or {}).get('relation_candidate') is not True
            or addressed.get('subject_candidate_id') != 'cand-7073'
            or addressed.get('object_candidate_id') != 'cand-0203'):
        raise SystemExit('p.181 note 4 addressee relation changed since review')

    for note_id, (_, _, body_ids) in LINKS.items():
        for body_id in body_ids:
            if body_id not in by_id or by_id[body_id].get('segment_id') != BODY_SEGMENT:
                raise SystemExit(f'missing p.181 body link target: {body_id}')
    expected_body_link_ids = {
        'st-chp7-p181-i05': {'st-chp7-p181-n1-cite-brienne', 'st-chp7-p181-n1-brienne-report', 'st-chp7-p181-n1-haskell-interpretation'},
        'st-chp7-p181-i06': {'st-chp7-p181-n1-cite-brienne', 'st-chp7-p181-n1-haskell-interpretation'},
        'st-chp7-p181-i11': {'st-chp7-p181-n2-cite-brienne'},
        'st-chp7-p181-i26': {'st-chp7-p181-n3-cite-mazarin'},
        'st-chp7-p181-i27': {'st-chp7-p181-n3-cite-mazarin'},
        'st-chp7-p181-i28': {'st-chp7-p181-n4-cite-pollak', 'st-chp7-p181-n4-letter-authored-by', 'st-chp7-p181-n4-letter-addressed-to'},
    }
    for body_id, expected in expected_body_link_ids.items():
        q = by_id[body_id].get('qualifiers') or {}
        actual = set(q.get('footnote_statement_ids') or [])
        if actual != expected:
            raise SystemExit(f'body reciprocal links changed at {body_id}: {sorted(actual)}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        citation_spec = CITATIONS.get(row['statement_id'])
        claim_spec = CLAIMS.get(row['statement_id'])
        if citation_spec is not None:
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            publication_id = citation_spec['publication_id']
            row.update({
                'subject_candidate_id': SOURCE_BOOK_ID,
                'object_candidate_id': publication_id,
                'predicate': 'cites',
            })
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {citation_spec['locator']} in footnote {citation_spec['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id,
                'citation_locator': citation_spec['locator'],
                'citations': [{
                    'source_candidate_id': SOURCE_BOOK_ID,
                    'publication_candidate_id': publication_id,
                    'locator': citation_spec['locator'],
                }],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': citation_spec['marker'],
                'footnote_number': citation_spec['marker'],
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': citation_spec['marker'],
                    'segment_id': NOTE_SEGMENT,
                    'source_line': citation_spec['line'],
                    'statement_ids': citation_spec['body_ids'],
                }],
                'related_body_statement_ids': citation_spec['body_ids'],
                'linked_body_statement_ids': citation_spec['body_ids'],
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': (
                    'S2 citation candidate: the printed footnote identifies this source and locator. '
                    'This records Haskell’s bibliographic reference only; the cited material was not '
                    'independently consulted and no S6 edge is created.'
                ),
            })
            row['qualifiers'] = q
        elif claim_spec is not None:
            q = dict(row.get('qualifiers') or {})
            q.update({
                'relation_candidate': True,
                'relation_candidate_note': claim_spec['note'],
                'footnote_marker': claim_spec['marker'],
                'footnote_number': claim_spec['marker'],
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': claim_spec['marker'],
                    'segment_id': NOTE_SEGMENT,
                    'source_line': claim_spec['line'],
                    'statement_ids': claim_spec['body_ids'],
                }],
                'related_body_statement_ids': claim_spec['body_ids'],
                'linked_body_statement_ids': claim_spec['body_ids'],
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
            })
            if claim_spec.get('open_endpoint_reason'):
                q['open_endpoint_reason'] = claim_spec['open_endpoint_reason']
            row['qualifiers'] = q
        elif row['statement_id'] == 'st-chp7-p181-n4-letter-addressed-to':
            q = dict(row.get('qualifiers') or {})
            q.update({
                'footnote_marker': 4,
                'footnote_number': 4,
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': 4,
                    'segment_id': NOTE_SEGMENT,
                    'source_line': 342,
                    'statement_ids': ['st-chp7-p181-i28'],
                }],
                'related_body_statement_ids': ['st-chp7-p181-i28'],
                'linked_body_statement_ids': ['st-chp7-p181-i28'],
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
            })
            row['qualifiers'] = q
        output.append(row)

    output_bytes = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8483, False: 3420, 'unset': 2284}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')

    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(CITATIONS),
        'classified_note_claims': len(CLAIMS),
        'reciprocal_links_checked': sum(len(ids) for ids in expected_body_link_ids.values()),
        'post_counts': {'statements': len(output), **{str(key): value for key, value in counts.items()}},
        'before_sha256': hashes,
        'after_statement_sha256': sha256(output_bytes),
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
