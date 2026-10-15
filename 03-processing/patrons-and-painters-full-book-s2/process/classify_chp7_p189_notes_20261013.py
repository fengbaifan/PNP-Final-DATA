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
    STATEMENTS.name: 'e23b48b3afdfa4004282e7159424294ac47e72a56a042e5a5e0387f2e0a144ac',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p189-notes-20261013')

CITATIONS = {
    'st-chp7-p189-n1-cite-soprani': {
        'publication_id': 'cand-5160', 'locator': 'Soprani/Ratti, Vite de’ Pittori, Scultori ed Architetti Genovesi, vol. I, p. 254',
        'marker': 1, 'line': 370, 'body_ids': ['st-chp7-p189-i05'],
    },
    'st-chp7-p189-n2-cite-pascoli': {
        'publication_id': 'cand-4834', 'locator': 'Pascoli, Vite de’ Pittori, Scultori ed Architetti moderni, vol. I, p. 255',
        'marker': 2, 'line': 370, 'body_ids': ['st-chp7-p189-i07'],
    },
    'st-chp7-p189-n2-cite-wittkower': {
        'publication_id': 'cand-7111', 'locator': 'Wittkower, “Domenico Guidi and French classicism” (1938)',
        'marker': 2, 'line': 370, 'body_ids': ['st-chp7-p189-i07'],
    },
    'st-chp7-p189-n3-cite-bellori': {
        'publication_id': 'cand-4831', 'locator': 'Bellori, Le Vite inedite (1942), pp. 101 and 126',
        'marker': 3, 'line': 371, 'body_ids': ['st-chp7-p189-i12', 'st-chp7-p189-i13'],
    },
    'st-chp7-p189-n3-cite-montaiglon': {
        'publication_id': 'cand-7113', 'locator': 'Montaiglon, Correspondance des Directeurs, vol. I, p. 104',
        'marker': 3, 'line': 371, 'body_ids': ['st-chp7-p189-i12', 'st-chp7-p189-i13'],
    },
    'st-chp7-p189-n4-cite-alazard': {
        'publication_id': 'cand-7099', 'locator': 'Alazard, L’Abbé Luigi Strozzi correspondant artistique de Mazarin, de Colbert, de Louvois et de La Teulière, p. 142',
        'marker': 4, 'line': 372, 'body_ids': ['st-chp7-p189-i15', 'st-chp7-p189-i16'],
    },
    'st-chp7-p189-n4-cite-montaiglon': {
        'publication_id': 'cand-7113', 'locator': 'Montaiglon, Correspondance des Directeurs, vol. I, p. 190',
        'marker': 4, 'line': 372, 'body_ids': ['st-chp7-p189-i15', 'st-chp7-p189-i16'],
    },
    'st-chp7-p189-n4-cite-zanotti': {
        'publication_id': 'cand-7115', 'locator': 'Zanotti, Storia dell’Accademia Clementina, vol. I, p. 245',
        'marker': 4, 'line': 372, 'body_ids': ['st-chp7-p189-i15', 'st-chp7-p189-i16'],
    },
    'st-chp7-p189-n5-cite-zanotti': {
        'publication_id': 'cand-7115', 'locator': 'Zanotti, Storia dell’Accademia Clementina, vol. I, pp. 155, 170, 199, and vol. II, p. 121',
        'marker': 5, 'line': 373, 'body_ids': ['st-chp7-p189-i24'],
        'ocr_corrections': [{'source_line': 373, 'ocr': '6', 'print_reading': '5', 'basis': 'CHP-7.pdf physical page 27'}],
    },
    'st-chp7-p189-n6-cite-dedominici': {
        'publication_id': 'cand-4835', 'locator': 'De Dominici, Vite dei pittori scultori ed architetti napoletani, vol. IV, p. 50',
        'marker': 6, 'line': 374, 'body_ids': ['st-chp7-p189-i27'],
    },
}

CLAIMS = {
    'st-chp7-p189-n4-claim-attempt': {
        'subject': 'cand-7117', 'predicate': 'attempted_to_persuade_artist_to_paint_for_king', 'object': 'cand-1172',
        'marker': 4, 'line': 372, 'body_ids': ['st-chp7-p189-i15', 'st-chp7-p189-i16'],
        'note': 'S2 candidate records Haskell’s report that the unidentified director of the French Academy in Rome tried in 1685 to persuade Luca Giordano to paint for the King; the painting and attempt are not further specified.',
        'open_endpoint_reason': 'The director is unnamed, the intended picture is unidentified, and no successful commission or further outcome is stated. The adjacent unnamed director associated with Cignani is kept separate.',
    },
    'st-chp7-p189-n4-claim-default': {
        'subject': 'cand-1172', 'predicate': 'defaulted_on_painting_obligation', 'object': None,
        'marker': 4, 'line': 372, 'body_ids': ['st-chp7-p189-i15', 'st-chp7-p189-i16'],
        'note': 'S2 candidate records Haskell’s statement that Luca Giordano defaulted on his obligations in the reported 1685 attempt to secure a painting for the King.',
        'open_endpoint_reason': 'The obligations, their terms, and the outcome are unspecified; no commission, payment, or particular painting is inferred.',
    },
}

SOURCE_GUARDS = {
    370: '1 Soprani, I, p. 254. 2 Pascoli, I, p. 255, and Wittkower, 1938.',
    371: '3 Montaiglon, I, p. 104, and Bellori, 1942, pp. 101 and 126.',
    372: '4 Zanotti, I, p. 245, and Montaiglon, I, p. 190. In 1685 the director',
    373: '6 Zanotti, I, pp. 155, 170, 199, and II, p. 121.',
    374: '6 De Dominici, IV, p. 50.',
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = {p: p.read_bytes() for p in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {p.name: sha256(data) for p, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    for line_no, snippet in SOURCE_GUARDS.items():
        if snippet not in source_lines[line_no - 1]:
            raise SystemExit(f'source guard failed at L{line_no}: {source_lines[line_no - 1]}')
    candidates = {r['candidate_id']: r for r in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))}
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source book candidate is missing or mistyped')
    for spec in CITATIONS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f'publication candidate missing or mistyped: {spec["publication_id"]}')
    if candidates.get('cand-7117', {}).get('suggested_type') != 'person' or candidates.get('cand-1172', {}).get('suggested_type') != 'person':
        raise SystemExit('note 4 person endpoint candidate is missing or mistyped')

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {r['statement_id']: r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    if set(CITATIONS) | set(CLAIMS) != {r['statement_id'] for r in rows if r['statement_id'].startswith('st-chp7-p189-n') and (r.get('qualifiers') or {}).get('relation_candidate') is None}:
        raise SystemExit('p.189 unset note statement set differs from reviewed set')

    for note_id, spec in {**CITATIONS, **CLAIMS}.items():
        r, q = by_id[note_id], by_id[note_id].get('qualifiers') or {}
        expected_predicate = 'footnote_citation' if note_id in CITATIONS else spec['predicate']
        if (r.get('segment_id') != NOTE_SEGMENT or r.get('predicate') != expected_predicate
                or q.get('source_line_start') != spec['line'] or q.get('relation_candidate') is not None
                or q.get('linked_body_statement_ids') != spec['body_ids']):
            raise SystemExit(f'note row changed since review: {note_id}')
        for body_id in spec['body_ids']:
            if note_id not in (by_id[body_id].get('qualifiers') or {}).get('footnote_statement_ids', []):
                raise SystemExit(f'reciprocal body link missing: {body_id} <- {note_id}')
    for note_id, spec in CLAIMS.items():
        r = by_id[note_id]
        if (r.get('subject_candidate_id'), r.get('object_candidate_id')) != (spec['subject'], spec['object']):
            raise SystemExit(f'note claim endpoints changed since review: {note_id}')

    output = []
    for src in rows:
        r = dict(src)
        note_id = r['statement_id']
        if note_id in CITATIONS:
            spec = CITATIONS[note_id]
            q = dict(r.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            publication_id = spec['publication_id']
            r.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': publication_id, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {spec['locator']} in footnote {spec['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id, 'citation_locator': spec['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': publication_id, 'locator': spec['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': spec['marker'], 'footnote_number': spec['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
                'related_body_statement_ids': spec['body_ids'], 'linked_body_statement_ids': spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_body_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; the cited publication was not independently consulted, and no S6 edge is created.',
            })
            if spec.get('ocr_corrections'):
                q['ocr_corrections'] = list(q.get('ocr_corrections') or []) + spec['ocr_corrections']
            r['qualifiers'] = q
        elif note_id in CLAIMS:
            spec = CLAIMS[note_id]
            q = dict(r.get('qualifiers') or {})
            q.update({
                'footnote_marker': spec['marker'], 'footnote_number': spec['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
                'related_body_statement_ids': spec['body_ids'], 'linked_body_statement_ids': spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_body_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True, 'relation_candidate_note': spec['note'],
                'open_endpoint_reason': spec['open_endpoint_reason'],
            })
            r['qualifiers'] = q
        output.append(r)

    out = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14187, {True: 8557, False: 3418, 'unset': 2212}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {'mode': 'apply' if args.apply else 'dry_run', 'normalized_citations': len(CITATIONS),
              'classified_note_claims': len(CLAIMS), 'reciprocal_body_links_checked': len(CITATIONS) + len(CLAIMS),
              'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
              'before_sha256': hashes, 'after_statement_sha256': sha256(out), 'backup': str(BACKUP.relative_to(ROOT))}
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
    if sha256(STATEMENTS.read_bytes()) != report['after_statement_sha256']:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
