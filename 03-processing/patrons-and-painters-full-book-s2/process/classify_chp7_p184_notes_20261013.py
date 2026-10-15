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
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l170-176'
NEXT_BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l205-213'
EXPECTED_HASHES = {
    STATEMENTS.name: 'b3ab8e07944b023a50f3751271174b04f9fd6e4286ea9a56ccc4480abc1e17f6',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p184-notes-20261013')

CITATIONS = {
    'st-chp7-p184-n1-cite-cosnac': {
        'publication_id': 'cand-7087', 'locator': 'de Cosnac, Les richesses du Palais Mazarin (1885), p. 144',
        'marker': 1, 'line': 354, 'body_ids': ['st-chp7-p184-i02'],
        'ocr_corrections': [{'source_line': 354, 'ocr': 'de Còrnac', 'print_reading': 'de Cosnac', 'basis': 'CHP-7.pdf physical page 18'}],
    },
    'st-chp7-p184-n1-cite-taylor': {
        'publication_id': 'cand-7089', 'locator': 'Taylor, The Taste of Angels (1948), p. 332',
        'marker': 1, 'line': 354, 'body_ids': ['st-chp7-p184-i02'],
        'ocr_corrections': [{'source_line': 354, 'ocr': 'p, 332', 'print_reading': 'p. 332', 'basis': 'CHP-7.pdf physical page 18'}],
    },
    'st-chp7-p184-n2-cite-daumale': {
        'publication_id': 'cand-6807', 'locator': 'd’Aumale, pp. 293 ff.',
        'marker': 2, 'line': 355, 'body_ids': ['st-chp7-p184-i04'],
        'ocr_corrections': [{'source_line': 355, 'ocr': 'pp. 293 ff. -', 'print_reading': 'pp. 293 ff.', 'basis': 'CHP-7.pdf physical page 18'}],
    },
    'st-chp7-p184-n3-cite-blunt': {
        'publication_id': 'cand-5618', 'locator': 'Blunt, “Poussin dans les Musées de province,” Revue des Arts (Jan.–Feb. 1958)',
        'marker': 3, 'line': 356, 'body_ids': ['st-chp7-p184-i09'],
    },
    'st-chp7-p184-n3-cite-inventory-cosnac': {
        'publication_id': 'cand-7091', 'locator': 'de Cosnac, item 1240 (inventory of 1661)',
        'marker': 3, 'line': 356, 'body_ids': ['st-chp7-p184-i09'],
    },
    'st-chp7-p184-n4-cite-bonnaffe': {
        'publication_id': 'cand-7042', 'locator': 'Bonnaffé, Dictionnaire des amateurs français au XVII siècle, pp. 168–170',
        'marker': 4, 'line': 357, 'body_ids': ['st-chp7-p184-i13', 'st-chp7-p184-i14'],
    },
    'st-chp7-p184-n4-cite-briganti': {
        'publication_id': 'cand-4473', 'locator': 'Briganti (1962), p. 230',
        'marker': 4, 'line': 357, 'body_ids': ['st-chp7-p184-i13', 'st-chp7-p184-i14'],
    },
    'st-chp7-p184-n4-cite-hoog': {
        'publication_id': 'cand-7095', 'locator': 'Hoog, Attributions anciennes à Valentin (1960), pp. 270 ff.',
        'marker': 4, 'line': 357, 'body_ids': ['st-chp7-p185-i01'],
        'related_statement_ids': ['st-chp7-p184-n4-guercino-cato-location'],
    },
}

CLAIMS = {
    'st-chp7-p184-n3-podesta-inventory': {
        'subject': 'cand-5558', 'predicate': 'named_among_compilers_of_inventory', 'object': 'cand-7091',
        'marker': 3, 'line': 356, 'body_ids': ['st-chp7-p184-i09'],
        'note': 'This records Haskell’s statement that Giovanni Andrea Podesta was among the compilers of the 1661 inventory; the inventory was not independently examined.',
    },
    'st-chp7-p184-n3-podesta-mazarin-connection': {
        'subject': 'cand-5558', 'predicate': 'connection_with_mazarin_reported_as_previously_unnoticed', 'object': 'cand-1588',
        'marker': 3, 'line': 356, 'body_ids': ['st-chp7-p184-i09'],
        'note': 'This preserves Haskell’s statement that Podesta’s connection with Mazarin had not previously been noticed; the passage does not specify the connection’s nature, so it remains only an S2 candidate.',
        'open_endpoint_reason': 'The person endpoints are named, but Haskell does not identify the type, direction, or circumstances of their connection.',
    },
    'st-chp7-p184-n4-guercino-cato-location': {
        'subject': 'cand-7092', 'predicate': 'reported_currently_located_at', 'object': 'cand-7093',
        'marker': 4, 'line': 357, 'body_ids': ['st-chp7-p185-i01'],
        'note': 'This records Haskell’s report that Guercino’s Cato is at Marseilles; the current location and work identity are not independently verified.',
    },
}

SOURCE_GUARDS = {
    354: '1 de Còrnac, p. 144, and Taylor, p, 332.',
    355: '2 d’Aumale, pp. 293 ff. -',
    356: '3 See the inventory of 1661 in de Cosnac, item 1240.',
    357: '4 Bonnaffé, pp. 168-70, and Briganti, 1962, p. 230.',
}
BODY_LINKS = {
    'st-chp7-p184-i02': (1, 354, BODY_SEGMENT, 171, {'st-chp7-p184-n1-cite-cosnac', 'st-chp7-p184-n1-cite-taylor'}),
    'st-chp7-p184-i04': (2, 355, BODY_SEGMENT, 172, {'st-chp7-p184-n2-cite-daumale'}),
    'st-chp7-p184-i09': (3, 356, BODY_SEGMENT, 172, {
        'st-chp7-p184-n3-cite-blunt', 'st-chp7-p184-n3-cite-inventory-cosnac',
        'st-chp7-p184-n3-podesta-inventory', 'st-chp7-p184-n3-podesta-mazarin-connection',
    }),
    'st-chp7-p184-i13': (4, 357, BODY_SEGMENT, 173, {'st-chp7-p184-n4-cite-bonnaffe', 'st-chp7-p184-n4-cite-briganti'}),
    'st-chp7-p184-i14': (4, 357, BODY_SEGMENT, 173, {'st-chp7-p184-n4-cite-bonnaffe', 'st-chp7-p184-n4-cite-briganti'}),
    'st-chp7-p185-i01': (4, 357, NEXT_BODY_SEGMENT, 206, {'st-chp7-p184-n4-cite-hoog', 'st-chp7-p184-n4-guercino-cato-location'}),
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
                or q.get('source_line_start') != spec['line'] or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation row changed since review: {note_id}')
    for note_id, spec in CLAIMS.items():
        row, q = by_id[note_id], by_id[note_id].get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('subject_candidate_id') != spec['subject']
                or row.get('predicate') != spec['predicate'] or row.get('object_candidate_id') != spec['object']
                or q.get('source_line_start') != spec['line'] or q.get('relation_candidate') is not None):
            raise SystemExit(f'claim row changed since review: {note_id}')
    for body_id, (_, _, body_segment, body_line, _) in BODY_LINKS.items():
        if body_id not in by_id or by_id[body_id].get('segment_id') != body_segment:
            raise SystemExit(f'missing or moved body link target: {body_id}')
        q = by_id[body_id].get('qualifiers') or {}
        if q.get('source_line_start') != body_line or q.get('footnote_statement_ids'):
            raise SystemExit(f'body source anchor or prior links changed: {body_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        note_id = row['statement_id']
        c = CITATIONS.get(note_id)
        fact = CLAIMS.get(note_id)
        if c:
            publication_id = c['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': publication_id, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {c['locator']} in footnote {c['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id, 'citation_locator': c['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': publication_id, 'locator': c['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': c['marker'], 'footnote_number': c['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': c['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': c['line'], 'statement_ids': c['body_ids']}],
                'related_body_statement_ids': c['body_ids'], 'linked_body_statement_ids': c['body_ids'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; cited material was not independently consulted, and no S6 edge is created.',
            })
            if c.get('related_statement_ids'):
                q['related_statement_ids'] = c['related_statement_ids']
            if c.get('ocr_corrections'):
                q['ocr_corrections'] = c['ocr_corrections']
            row['qualifiers'] = q
        elif fact:
            q = dict(row.get('qualifiers') or {})
            q.update({
                'relation_candidate': True, 'relation_candidate_note': fact['note'],
                'footnote_marker': fact['marker'], 'footnote_number': fact['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': fact['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': fact['line'], 'statement_ids': fact['body_ids']}],
                'related_body_statement_ids': fact['body_ids'], 'linked_body_statement_ids': fact['body_ids'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
            })
            if fact.get('open_endpoint_reason'):
                q['open_endpoint_reason'] = fact['open_endpoint_reason']
            row['qualifiers'] = q
        output.append(row)

    by_out = {r['statement_id']: r for r in output}
    for body_id, (marker, line, body_segment, body_line, note_ids) in BODY_LINKS.items():
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        q.update({
            'footnote_marker': marker, 'footnote_number': marker, 'footnote_segment': NOTE_SEGMENT,
            'footnote_refs': [{
                'marker': marker, 'segment_id': NOTE_SEGMENT, 'source_line': line,
                'citation_segment_id': body_segment, 'citation_source_line': body_line,
                'statement_ids': sorted(note_ids),
            }],
            'footnote_statement_ids': sorted(note_ids),
            'footnote_link_status': 'linked', 'footnote_text_pending': False,
        })
        row['qualifiers'] = q

    output_bytes = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14187, {True: 8518, False: 3418, 'unset': 2251}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run', 'normalized_citations': len(CITATIONS),
        'classified_note_claims': len(CLAIMS), 'reciprocal_body_links': len(BODY_LINKS),
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
