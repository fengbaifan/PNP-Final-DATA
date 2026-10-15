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
SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: 'd4645085d3ad09d63872c269382140435368aae7a1d1c40b034de56677df0b72',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p174-notes-20261013')

CITATIONS = {
    'st-chp7-p174-n1-cite-baldinucci': {
        'publication_id': 'cand-7027', 'author_id': 'cand-0166',
        'locator': 'Baldinucci, IV, 1688, pp. 206–207', 'marker': 1, 'line': 309,
        'body_ids': ['st-chp7-p174-i10'],
    },
    'st-chp7-p174-n1-cite-desjardins': {
        'publication_id': 'cand-7028', 'author_id': 'cand-7031',
        'locator': 'Desjardins, p. 49', 'marker': 1, 'line': 309,
        'body_ids': ['st-chp7-p174-i10'],
    },
    'st-chp7-p174-n1-cite-dhanens': {
        'publication_id': 'cand-7029', 'author_id': 'cand-7032',
        'locator': 'Dhanens (no page specified)', 'marker': 1, 'line': 309,
        'body_ids': ['st-chp7-p174-i10'],
    },
    'st-chp7-p174-n2-cite-desjardins': {
        'publication_id': 'cand-7028', 'author_id': 'cand-7031',
        'locator': 'Desjardins, p. 50', 'marker': 2, 'line': 310,
        'body_ids': ['st-chp7-p174-i18'],
    },
    'st-chp7-p174-n3-cite-batiffol': {
        'publication_id': 'cand-7021', 'author_id': 'cand-7022',
        'locator': 'Batiffol, p. 430', 'marker': 3, 'line': 311,
        'body_ids': ['st-chp7-p174-i25'],
    },
    'st-chp7-p174-n4-cite-sterling': {
        'publication_id': 'cand-7030', 'author_id': 'cand-7033',
        'locator': 'Sterling, pp. 112–120', 'marker': 4, 'line': 311,
        'body_ids': ['st-chp7-p174-i32'],
    },
}

FACTS = {
    'st-chp7-p174-n2-catherine-commission': 'The note reports Catherine de’ Medici’s 1559 commission for the proposed equestrian statue of Henri II; the work was not executed.',
    'st-chp7-p174-n2-commissioned-from-michelangelo': 'The note identifies Michelangelo as the artist from whom the unexecuted statue was commissioned.',
    'st-chp7-p174-n2-monument-destroyed': 'The note says the previously discussed Henri IV equestrian monument was destroyed in 1792; this is distinct from the unexecuted Henri II proposal.',
    'st-chp7-p174-n2-monument-for-philip-iii': 'The note says Pietro Tacca later made a similar but distinct equestrian monument for Philip III of Spain.',
    'st-chp7-p174-n2-statue-not-executed': 'The note explicitly says the proposed Henri II statue was never executed.',
    'st-chp7-p174-n2-tacca-made-monument': 'The note attributes the later similar equestrian monument to Pietro Tacca.',
}
BODY_LINKS = {
    'st-chp7-p174-i10': (1, 309, list(CITATIONS)[:3]),
    'st-chp7-p174-i18': (2, 310, [
        'st-chp7-p174-n2-cite-desjardins',
        'st-chp7-p174-n2-catherine-commission',
        'st-chp7-p174-n2-commissioned-from-michelangelo',
        'st-chp7-p174-n2-monument-destroyed',
        'st-chp7-p174-n2-monument-for-philip-iii',
        'st-chp7-p174-n2-statue-not-executed',
        'st-chp7-p174-n2-tacca-made-monument',
    ]),
    'st-chp7-p174-i25': (3, 311, ['st-chp7-p174-n3-cite-batiffol']),
    'st-chp7-p174-i32': (4, 311, ['st-chp7-p174-n4-cite-sterling']),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def set_note_link(row: dict, marker: int, line: int, body_ids: list[str]) -> None:
    q = dict(row.get('qualifiers') or {})
    q.update({
        'footnote_marker': marker,
        'footnote_number': marker,
        'footnote_segment': SEGMENT,
        'footnote_refs': [{'marker': marker, 'segment_id': SEGMENT, 'source_line': line, 'statement_ids': body_ids}],
        'related_body_statement_ids': body_ids,
        'linked_body_statement_ids': body_ids,
        'footnote_link_status': 'linked',
        'footnote_text_pending': False,
    })
    row['qualifiers'] = q


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before = STATEMENTS.read_bytes()
    hashes = {
        STATEMENTS.name: sha256(before),
        CANDIDATES.name: sha256(CANDIDATES.read_bytes()),
        SOURCE.name: sha256(SOURCE.read_bytes()),
        PDF.name: sha256(PDF.read_bytes()),
    }
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        candidates = {row['candidate_id']: row for row in csv.DictReader(f)}
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell book candidate is absent or not archive typed')
    for spec in CITATIONS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f"citation publication is absent or mistyped: {spec['publication_id']}")
        if candidates.get(spec['author_id'], {}).get('suggested_type') != 'person':
            raise SystemExit(f"citation author is absent or mistyped: {spec['author_id']}")

    rows = [json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    required = set(CITATIONS) | set(FACTS) | set(BODY_LINKS)
    if not required.issubset(by_id):
        raise SystemExit(f'missing target statement or body anchor: {sorted(required - set(by_id))}')
    for sid, spec in CITATIONS.items():
        row = by_id[sid]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation changed since review: {sid}')
    for sid in FACTS:
        q = by_id[sid].get('qualifiers') or {}
        if q.get('source_line_start') != 310 or q.get('relation_candidate') is not None:
            raise SystemExit(f'note fact changed since review: {sid}')
    if by_id['st-chp7-p174-n2-commissioned-from-michelangelo'].get('object_candidate_id') != 'cand-1660':
        raise SystemExit('Michelangelo endpoint changed since review')

    output = []
    for source_row in rows:
        row = dict(source_row)
        sid = row['statement_id']
        if sid in CITATIONS:
            spec = CITATIONS[sid]
            pub_id = spec['publication_id']
            old_claim = str((row.get('qualifiers') or {}).get('claim') or '').strip()
            q = dict(row.get('qualifiers') or {})
            row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': pub_id, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[pub_id]['canonical_name']} at {spec['locator']} in this footnote. The prior note records: {old_claim}",
                'citation_candidate_id': spec['author_id'],
                'citation_publication_candidate_id': pub_id,
                'citation_locator': spec['locator'],
                'citations': [{'source_candidate_id': pub_id, 'publication_candidate_id': pub_id, 'locator': spec['locator']}],
                'cited_material_not_independently_consulted': True,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator. This records Haskell’s bibliographic reference only; the cited material was not independently consulted and no S6 edge is created.',
            })
            row['qualifiers'] = q
        elif sid in FACTS:
            q = dict(row.get('qualifiers') or {})
            q['relation_candidate'] = True
            q['relation_candidate_note'] = 'S2 relation candidate: explicit historical claim in Haskell’s note; preserve the distinct work, person, and outcome endpoints recorded in the statement.'
            if sid == 'st-chp7-p174-n2-monument-destroyed':
                q['date'] = '1792'
            elif sid == 'st-chp7-p174-n2-statue-not-executed':
                q['relation_candidate_note'] = 'S2 relation candidate: the note explicitly reports non-execution of the proposed Henri II statue; it remains distinct from the completed Henri IV and Philip III monuments.'
            row['qualifiers'] = q
        if sid == 'st-chp7-p174-n2-commissioned-from-michelangelo':
            q = dict(row.get('qualifiers') or {})
            q['qualification'] = 'The project is described as commissioned, not executed; Michelangelo is mapped to person candidate cand-1660, whose identity remains for global S3 review. Candidate cand-1661 is a work and is not the artist endpoint.'
            row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for body_id, (marker, line, note_ids) in BODY_LINKS.items():
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = list(q.get('footnote_refs') or [])
        ref = next((item for item in refs if item.get('marker') == marker), None)
        if ref is None:
            ref = {'marker': marker, 'segment_id': SEGMENT, 'source_line': line}
            refs.append(ref)
        if ref.get('segment_id') != SEGMENT or ref.get('source_line') != line:
            raise SystemExit(f'body footnote locator changed: {body_id}')
        ref['statement_ids'] = note_ids
        q.update({
            'footnote_refs': refs,
            'footnote_marker': marker,
            'footnote_number': marker,
            'footnote_segment': SEGMENT,
            'footnote_statement_ids': note_ids,
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
        })
        row['qualifiers'] = q
        for note_id in note_ids:
            set_note_link(by_out[note_id], marker, line, [body_id])

    text = '\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n'
    after = text.encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8432, False: 3419, 'unset': 2336}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(CITATIONS),
        'classified_note_claims': len(FACTS),
        'linked_body_anchors': len(BODY_LINKS),
        'endpoint_correction': 'Michelangelo person cand-1660; cand-1661 is a work',
        'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
        'before_sha256': hashes,
        'after_sha256': sha256(after),
        'backup': str(BACKUP.relative_to(ROOT)),
    }
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
    if sha256(STATEMENTS.read_bytes()) != report['after_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; hash verified')


if __name__ == '__main__':
    main()
