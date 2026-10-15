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
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l224-230'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
EXPECTED_HASHES = {
    STATEMENTS.name: '0cbbb812bd63691860f94cde18795ffb7321bb869d7b44bb434a03fdb321f7d4',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p187-notes-20261013')

CITATIONS = {
    'st-chp7-p187-n1-cite-alazard': {
        'publication_id': 'cand-7099', 'locator': 'Alazard, L’Abbé Luigi Strozzi correspondant artistique de Mazarin, de Colbert, de Louvois et de La Teulière, passim',
        'marker': 1, 'line': 362, 'body_ids': ['st-chp7-p187-i01', 'st-chp7-p187-i02'],
    },
    'st-chp7-p187-n1-cite-bonnaffe': {
        'publication_id': 'cand-7042', 'locator': 'Bonnaffé, Dictionnaire des amateurs français au XVII siècle, pp. 68–69 and 113–115',
        'marker': 1, 'line': 362, 'body_ids': ['st-chp7-p187-i01', 'st-chp7-p187-i02'],
    },
    'st-chp7-p187-n2-cite-alazard': {
        'publication_id': 'cand-7099', 'locator': 'Alazard, L’Abbé Luigi Strozzi correspondant artistique de Mazarin, de Colbert, de Louvois et de La Teulière, p. 110',
        'marker': 2, 'line': 363, 'body_ids': ['st-chp7-p187-i04'],
        'ocr_corrections': [{'source_line': 363, 'ocr': 'p. no.', 'print_reading': 'p. 110', 'basis': 'CHP-7.pdf physical page 25'}],
    },
    'st-chp7-p187-n3-cite-ruffo': {
        'publication_id': 'cand-3555', 'locator': 'Ruffo, p. 298',
        'marker': 3, 'line': 364, 'body_ids': ['st-chp7-p187-i05'],
        'ocr_corrections': [{'source_line': 364, 'ocr': 'RufFo', 'print_reading': 'Ruffo', 'basis': 'CHP-7.pdf physical page 25'}],
    },
    'st-chp7-p187-n4-cite-pascoli-i': {
        'publication_id': 'cand-4834', 'locator': 'Pascoli, Vite de’ Pittori, Scultori ed Architetti moderni, vol. I, p. 127',
        'marker': 4, 'line': 365, 'body_ids': ['st-chp7-p187-i06'],
    },
    'st-chp7-p187-n4-cite-pascoli-ii': {
        'publication_id': 'cand-4552', 'locator': 'Pascoli, Vite de’ Pittori, Scultori ed Architetti moderni, vol. II, p. 124',
        'marker': 4, 'line': 365, 'body_ids': ['st-chp7-p187-i06'],
        'related_statement_ids': ['st-chp7-p187-n4-canini-accompanied-cardinal-chigi', 'st-chp7-p187-n4-canini-employed-french-court'],
    },
    'st-chp7-p187-n5-cite-limentani': {
        'publication_id': 'cand-6239', 'locator': 'Limentani, “Poesie e lettere inedite di Salvator Rosa” (1950), p. 21',
        'marker': 5, 'line': 366, 'body_ids': ['st-chp7-p187-i07', 'st-chp7-p187-i08'],
        'related_statement_ids': ['st-chp7-p187-n5-louis-xiv-attitude-to-rosa-changed'],
    },
    'st-chp7-p187-n5-cite-de-rinaldis': {
        'publication_id': 'cand-6605', 'locator': 'De Rinaldis, Lettere inedite di Salvator Rosa a G. B. Ricciardi (1939), p. 193',
        'marker': 5, 'line': 366, 'body_ids': ['st-chp7-p187-i07', 'st-chp7-p187-i08'],
        'related_statement_ids': ['st-chp7-p187-n5-louis-xiv-attitude-to-rosa-changed'],
    },
    'st-chp7-p187-n5-cite-bailly': {
        'publication_id': 'cand-7110', 'locator': 'Bailly, Inventaire des tableaux du Roy rédigé en 1709 et 1710 (1899), p. 50',
        'marker': 5, 'line': 366, 'body_ids': ['st-chp7-p187-i07', 'st-chp7-p187-i08'],
        'related_statement_ids': [
            'st-chp7-p187-n5-papal-nunzio-presented-battle-to-louis-xiv',
            'st-chp7-p187-n5-rosa-battle-sent-from-versailles-to-paris',
            'st-chp7-p187-n5-note-accompanies-1697-transfer-and-quotes-royal-refusal',
        ],
    },
    'st-chp7-p187-n6-cite-blunt': {
        'publication_id': 'cand-7101', 'locator': 'Blunt, Art and Architecture in France 1500–1700 (1953)',
        'marker': 6, 'line': 367, 'body_ids': ['st-chp7-p187-i16'],
    },
    'st-chp7-p187-n6-cite-wittkower': {
        'publication_id': 'cand-4557', 'locator': 'Wittkower, Art and Architecture in Italy 1600 to 1750 (1958)',
        'marker': 6, 'line': 367, 'body_ids': ['st-chp7-p187-i16'],
        'ocr_corrections': [{'source_line': 367, 'ocr': 'Wittkower, 1938', 'print_reading': 'Wittkower, 1958', 'basis': 'CHP-7.pdf physical page 25'}],
    },
    'st-chp7-p187-n6-cite-hautecoeur': {
        'publication_id': 'cand-7097', 'locator': 'Hautecœur, L’Histoire des Châteaux du Louvre et des Tuileries (1927)',
        'marker': 6, 'line': 367, 'body_ids': ['st-chp7-p187-i16'],
    },
    'st-chp7-p187-n6-cite-chantelou': {
        'publication_id': 'cand-7102', 'locator': 'Chantelou, Journal du voyage du chevalier Bernin en France',
        'marker': 6, 'line': 367, 'body_ids': ['st-chp7-p187-i16'],
    },
}

CLAIMS = {
    'st-chp7-p187-n4-canini-accompanied-cardinal-chigi': {
        'subject': 'cand-7103', 'predicate': 'canini_accompanied_cardinal_chigi_on_1664_paris_visit', 'object': 'cand-7104',
        'marker': 4, 'line': 365, 'body_ids': ['st-chp7-p187-i06'],
        'note': 'This records Haskell’s footnote report that Canini accompanied Cardinal Chigi to Paris in 1664; both identities remain unresolved and Pascoli was not independently consulted.',
        'open_endpoint_reason': 'No first names are given for Canini or the Cardinal; the candidate identities remain unresolved.',
    },
    'st-chp7-p187-n4-canini-employed-french-court': {
        'subject': 'cand-7103', 'predicate': 'canini_employed_at_french_court', 'object': 'cand-6699',
        'marker': 4, 'line': 365, 'body_ids': ['st-chp7-p187-i06'],
        'note': 'This preserves Haskell’s statement that Canini was employed at the French court; the period and terms are not supplied, and Pascoli was not independently read.',
        'open_endpoint_reason': 'Canini is not identified by full name and no dates, office, or employment instrument are given.',
    },
    'st-chp7-p187-n5-louis-xiv-attitude-to-rosa-changed': {
        'subject': 'cand-1447', 'predicate': 'louis_xiv_attitude_toward_salvator_rosa_later_changed', 'object': 'cand-2246',
        'marker': 5, 'line': 366, 'body_ids': ['st-chp7-p187-i07', 'st-chp7-p187-i08'],
        'note': 'This records Haskell’s statement that Louis XIV’s attitude toward Rosa changed later; no exact date or full chronology is supplied.',
    },
    'st-chp7-p187-n5-note-accompanies-1697-transfer-and-quotes-royal-refusal': {
        'subject': 'cand-7107', 'predicate': 'note_accompanied_1697_transfer_and_quoted_royal_refusal', 'object': 'cand-7106',
        'marker': 5, 'line': 366, 'body_ids': ['st-chp7-p187-i07', 'st-chp7-p187-i08'],
        'note': 'This records Haskell’s report that a note accompanied the 1697 transfer and quoted the King’s refusal; the note’s author and addressee are unknown, and Bailly was not independently read.',
        'open_endpoint_reason': 'The note is not identified by author, recipient, archival location, or document title.',
    },
    'st-chp7-p187-n5-papal-nunzio-presented-battle-to-louis-xiv': {
        'subject': 'cand-7105', 'predicate': 'papal_nunzio_presented_rosa_battle_to_louis_xiv', 'object': 'cand-1447',
        'marker': 5, 'line': 366, 'body_ids': ['st-chp7-p187-i07', 'st-chp7-p187-i08'],
        'note': 'This preserves Haskell’s report that an unnamed Papal Nuncio had presented the Battle to Louis XIV; its presentation date is unspecified and 1697 refers only to the later dispatch.',
        'open_endpoint_reason': 'The Nuncio is unnamed, the painting version is unidentified, and the presentation date is not given.',
    },
    'st-chp7-p187-n5-rosa-battle-sent-from-versailles-to-paris': {
        'subject': 'cand-7106', 'predicate': 'rosa_battle_sent_from_versailles_to_paris_in_1697', 'object': 'cand-4653',
        'marker': 5, 'line': 366, 'body_ids': ['st-chp7-p187-i07', 'st-chp7-p187-i08'],
        'note': 'This records Haskell’s report that the Rosa Battle was sent from Versailles to Paris in 1697; it is a transfer date, not the date of the Nuncio’s earlier presentation.',
        'open_endpoint_reason': 'The source does not name the sending authority, destination building or collection, or the painting version.',
    },
}

SOURCE_GUARDS = {
    362: '1 Alazard, passim, and Bonnaffé, pp. 68-9 and 113-15.',
    363: '2 Alazard, p. no.',
    364: '3 RufFo, p. 298.',
    365: '4 Pascoli, I, p. 127. Canini, who accompanied Cardinal Chigi on his visit to Paris in 1664',
    366: '5 Limentani, 1950, p. 21, and De Rinaldis, 1939, p. 193.',
    367: '6 For this section see, apart from Blunt, 1953, and Wittkower, 1938, Hautecœur and Chantelou.',
}
BODY_LINKS = {
    'st-chp7-p187-i01': {'st-chp7-p187-n1-cite-alazard', 'st-chp7-p187-n1-cite-bonnaffe'},
    'st-chp7-p187-i02': {'st-chp7-p187-n1-cite-alazard', 'st-chp7-p187-n1-cite-bonnaffe'},
    'st-chp7-p187-i04': {'st-chp7-p187-n2-cite-alazard'},
    'st-chp7-p187-i05': {'st-chp7-p187-n3-cite-ruffo'},
    'st-chp7-p187-i06': {
        'st-chp7-p187-n4-cite-pascoli-i', 'st-chp7-p187-n4-cite-pascoli-ii',
        'st-chp7-p187-n4-canini-accompanied-cardinal-chigi', 'st-chp7-p187-n4-canini-employed-french-court',
    },
    'st-chp7-p187-i07': {
        'st-chp7-p187-n5-cite-limentani', 'st-chp7-p187-n5-cite-de-rinaldis', 'st-chp7-p187-n5-cite-bailly',
        'st-chp7-p187-n5-louis-xiv-attitude-to-rosa-changed', 'st-chp7-p187-n5-papal-nunzio-presented-battle-to-louis-xiv',
        'st-chp7-p187-n5-rosa-battle-sent-from-versailles-to-paris', 'st-chp7-p187-n5-note-accompanies-1697-transfer-and-quotes-royal-refusal',
    },
    'st-chp7-p187-i08': {
        'st-chp7-p187-n5-cite-limentani', 'st-chp7-p187-n5-cite-de-rinaldis', 'st-chp7-p187-n5-cite-bailly',
        'st-chp7-p187-n5-louis-xiv-attitude-to-rosa-changed', 'st-chp7-p187-n5-papal-nunzio-presented-battle-to-louis-xiv',
        'st-chp7-p187-n5-rosa-battle-sent-from-versailles-to-paris', 'st-chp7-p187-n5-note-accompanies-1697-transfer-and-quotes-royal-refusal',
    },
    'st-chp7-p187-i16': {
        'st-chp7-p187-n6-cite-blunt', 'st-chp7-p187-n6-cite-wittkower',
        'st-chp7-p187-n6-cite-hautecoeur', 'st-chp7-p187-n6-cite-chantelou',
    },
}
BODY_MARKERS = {
    'st-chp7-p187-i01': 1, 'st-chp7-p187-i02': 1, 'st-chp7-p187-i04': 2,
    'st-chp7-p187-i05': 3, 'st-chp7-p187-i06': 4, 'st-chp7-p187-i07': 5,
    'st-chp7-p187-i08': 5, 'st-chp7-p187-i16': 6,
}
BODY_NOTE_LINES = {
    'st-chp7-p187-i01': 362, 'st-chp7-p187-i02': 362, 'st-chp7-p187-i04': 363,
    'st-chp7-p187-i05': 364, 'st-chp7-p187-i06': 365, 'st-chp7-p187-i07': 366,
    'st-chp7-p187-i08': 366, 'st-chp7-p187-i16': 367,
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
        if (row.get('subject_candidate_id') != spec['subject'] or row.get('predicate') != spec['predicate']
                or row.get('object_candidate_id') != spec['object'] or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'claim row changed since review: {note_id}')
    all_links = {**{k: v['body_ids'] for k, v in CITATIONS.items()}, **{k: v['body_ids'] for k, v in CLAIMS.items()}}
    for body_id, expected in BODY_LINKS.items():
        q = (by_id.get(body_id) or {}).get('qualifiers') or {}
        if set(q.get('footnote_statement_ids') or []) != expected:
            raise SystemExit(f'body reciprocal links changed at {body_id}')
    for note_id, body_ids in all_links.items():
        if any(body_id not in by_id for body_id in body_ids):
            raise SystemExit(f'missing p.187 body link target for {note_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        note_id = row['statement_id']
        c = CITATIONS.get(note_id)
        fact = CLAIMS.get(note_id)
        if c:
            pub = c['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            row.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': pub, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[pub]['canonical_name']} at {c['locator']} in footnote {c['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': pub, 'citation_locator': c['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': pub, 'locator': c['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': c['marker'], 'footnote_number': c['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': c['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': c['line'], 'statement_ids': c['body_ids']}],
                'related_body_statement_ids': c['body_ids'], 'linked_body_statement_ids': c['body_ids'],
                'footnote_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; the cited publication was not independently consulted, and no S6 edge is created.',
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
    for body_id, note_ids in BODY_LINKS.items():
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = [dict(ref) for ref in q.get('footnote_refs') or []]
        note_line = BODY_NOTE_LINES[body_id]
        marker = BODY_MARKERS[body_id]
        ref = next((x for x in refs if x.get('marker') == marker and x.get('segment_id') == NOTE_SEGMENT and x.get('source_line') == note_line), None)
        if ref is None:
            ref = {'marker': marker, 'segment_id': NOTE_SEGMENT, 'source_line': note_line}
            refs.append(ref)
        ref['statement_ids'] = sorted(note_ids)
        q['footnote_refs'] = refs
        q['footnote_statement_ids'] = sorted(note_ids)
        q['footnote_link_status'] = 'linked'
        q['footnote_text_pending'] = False
        q['footnote_marker'], q['footnote_number'], q['footnote_segment'] = marker, marker, NOTE_SEGMENT
        row['qualifiers'] = q

    output_bytes = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14187, {True: 8543, False: 3418, 'unset': 2226}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {'mode': 'apply' if args.apply else 'dry_run', 'normalized_citations': len(CITATIONS),
              'classified_note_claims': len(CLAIMS), 'body_links_checked': len(BODY_LINKS),
              'post_counts': {'statements': len(output), **{str(k): v for k, v in counts.items()}},
              'before_sha256': hashes, 'after_statement_sha256': sha256(output_bytes),
              'backup': str(BACKUP.relative_to(ROOT))}
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
