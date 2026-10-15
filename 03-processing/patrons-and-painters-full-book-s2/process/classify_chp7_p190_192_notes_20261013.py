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
SOURCE_IV = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_iv.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
SOURCE_BOOK_ID = 'cand-2962'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_iv:l3-4'
EXPECTED_HASHES = {
    STATEMENTS.name: '8c146c0743a5e7bee1d7ed8dfea06c8e5e8a255b088c545d3d513a766073025e',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    SOURCE_IV.name: 'd620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p190-192-notes-20261013')

CITATIONS = {
    'st-chp7-p190-n1-cite-harris-1960': {
        'publication_id': 'cand-7118', 'locator': 'Harris, “La misión de Velazquez in Italia” (1960), pp. 109–136',
        'marker': 1, 'line': 375, 'body_ids': ['st-chp7-p190-i03'],
    },
    'st-chp7-p190-n1-cite-harris-1961': {
        'publication_id': 'cand-7119', 'locator': 'Harris, “Angelo Michele Colonna y la decoración de San Antonio de los Portugueses” (1961), pp. 101–105',
        'marker': 1, 'line': 375, 'body_ids': ['st-chp7-p190-i08', 'st-chp7-p190-i11'],
    },
    'st-chp7-p190-n2-cite-ghelli': {
        'publication_id': 'cand-7122', 'locator': 'Ghelli, Il viceré marchese del Carpio (1683–1687), parts I–II (1933–1934)',
        'marker': 2, 'line': 376, 'body_ids': ['st-chp7-p190-i12', 'st-chp7-p190-i14', 'st-chp7-p190-i15'],
    },
    'st-chp7-p190-n3-cite-maclaren': {
        'publication_id': 'cand-7124', 'locator': 'Maclaren, The Spanish School, p. 76',
        'marker': 3, 'line': 377, 'body_ids': ['st-chp7-p190-i17', 'st-chp7-p190-i18'],
    },
    'st-chp7-p190-n4-cite-avviso': {
        'publication_id': 'cand-7126', 'locator': 'Avviso of 12 June 1677, published in Roma, vol. XIX (1941), p. 308',
        'marker': 4, 'line': 377, 'body_ids': ['st-chp7-p190-i20'],
    },
    'st-chp7-p190-n5-cite-harris-1957': {
        'publication_id': 'cand-7127', 'locator': 'Harris, “El Marqués del Carpio y sus cuadros de Velázquez” (1957), pp. 136–139',
        'marker': 5, 'line': 378, 'body_ids': ['st-chp7-p190-i26', 'st-chp7-p190-i27'],
    },
    'st-chp7-p191-n1-cite-bellori': {
        'publication_id': 'cand-4831', 'locator': 'Bellori, Le Vite inedite (1942), pp. 117 and 121',
        'marker': 1, 'line': 379, 'body_ids': ['st-chp7-p191-i03'],
    },
    'st-chp7-p191-n2-cite-album': {
        'publication_id': 'cand-7129', 'locator': 'Introduction to the Society of Antiquaries album of antiquities drawings',
        'marker': 2, 'line': 380, 'body_ids': ['st-chp7-p191-i06'],
    },
    'st-chp7-p191-n2-cite-pacichelli': {
        'publication_id': 'cand-6973', 'locator': 'Pacichelli, Memorie de’ viaggi per l’Europa Christiana, Parte IV, vol. I, p. 39',
        'marker': 2, 'line': 380, 'body_ids': ['st-chp7-p191-i06'],
    },
    'st-chp7-p191-n3-cite-bernino': {
        'publication_id': 'cand-7130', 'locator': 'Domenico Bernino, p. 28 (cited title not supplied)',
        'marker': 3, 'line': 381, 'body_ids': ['st-chp7-p191-i07', 'st-chp7-p191-i08'],
    },
    'st-chp7-p191-n4-cite-letter': {
        'publication_id': 'cand-7131', 'locator': 'Letter from the Duc d’Estrées to Louis XIV, 27 July 1684, in Montaiglon, vol. VI, p. 388',
        'marker': 4, 'line': 382, 'body_ids': ['st-chp7-p191-i09'],
    },
    'st-chp7-p191-n6-cite-dominici': {
        'publication_id': 'cand-4835', 'locator': 'De Dominici, Vite dei pittori scultori ed architetti napoletani, vol. IV, p. 315',
        'marker': 6, 'line': 383, 'body_ids': ['st-chp7-p191-i19'],
    },
    'st-chp7-p191-n7-cite-address': {
        'publication_id': 'cand-7135', 'locator': 'Discursos leídos en la recepción pública del Duque de Berwick y de Alba (Madrid, 1924), p. 20',
        'marker': 7, 'line': 384, 'body_ids': ['st-chp7-p191-i21'],
    },
    'st-chp7-p191-n8-cite-bottari': {
        'publication_id': 'cand-6200', 'locator': 'Bottari, Raccolta di lettere sulla Pittura, Scultura ed Architettura, vol. II, p. 105',
        'marker': 8, 'line': 385, 'body_ids': ['st-chp7-p191-i22'],
    },
    'st-chp7-p191-n8-cite-orlandi': {
        'publication_id': 'cand-7137', 'locator': 'Orlandi, Abecedario Pittorico, p. 236',
        'marker': 8, 'line': 385, 'body_ids': ['st-chp7-p191-i22'],
    },
    'st-chp7-p191-n10-cite-dominici': {
        'publication_id': 'cand-4835', 'locator': 'De Dominici, Vite dei pittori scultori ed architetti napoletani, vol. IV, p. 164',
        'marker': 10, 'line': 386, 'body_ids': ['st-chp7-p191-i28', 'st-chp7-p191-i29'],
    },
    'st-chp7-p191-n10-cite-saxl': {
        'publication_id': 'cand-7138', 'locator': 'Saxl, “The battle scene without a hero—Aniello Falcone and his patrons”, p. 76',
        'marker': 10, 'line': 386, 'body_ids': ['st-chp7-p191-i30'],
    },
    'st-chp7-p191-n11-cite-list': {
        'publication_id': 'cand-7139', 'locator': 'Listas de cuadros y objetos artísticos remitidos desde Italia a España por el puerto de Nápoles, 1683–1687; MS. El Escorial &-IV-25 (photocopy at the Warburg Institute)',
        'marker': 11, 'line': 387, 'body_ids': ['st-chp7-p191-i30'],
    },
    'st-chp7-p192-n1-cite-pascoli-vol1': {
        'publication_id': 'cand-4834', 'locator': 'Pascoli, Vite de’ Pittori, Scultori ed Architetti moderni, vol. I, p. 186',
        'marker': 1, 'line': 388, 'body_ids': ['st-chp7-p192-i09'],
    },
    'st-chp7-p192-n1-cite-pascoli-vol2': {
        'publication_id': 'cand-4552', 'locator': 'Pascoli, Vite de’ Pittori, Scultori ed Architetti moderni, vol. II, p. 314',
        'marker': 1, 'line': 388, 'body_ids': ['st-chp7-p192-i09'],
    },
    'st-chp7-p192-n2-cite-griseri': {
        'publication_id': 'cand-7143', 'locator': 'Griseri, “I bozzetti di Luca Giordano per l’Escaliera dell’Escorial” (1956), pp. 33–39',
        'marker': 2, 'line': 389, 'body_ids': ['st-chp7-p192-i15'],
    },
    'st-chp7-p192-n2-cite-longhi': {
        'publication_id': 'cand-7144', 'locator': 'Longhi, “Il Goya romano e la ‘cultura di Via Condotti’” (1954), pp. 28–39',
        'marker': 2, 'line': 389, 'body_ids': ['st-chp7-p192-i15'],
    },
    'st-chp7-p192-n2-cite-zanotti': {
        'publication_id': 'cand-7115', 'locator': 'Zanotti, Storia dell’Accademia Clementina, vol. I, pp. 247–248',
        'marker': 2, 'line': 389, 'body_ids': ['st-chp7-p192-i09', 'st-chp7-p192-i12', 'st-chp7-p192-i15'],
    },
}

CLAIMS = {
    'st-chp7-p190-n4-avviso-published-in-roma': {
        'predicate': 'published_in', 'subject': 'cand-7126', 'object': 'cand-7125', 'marker': 4, 'line': 377,
        'body_ids': ['st-chp7-p190-i20'],
        'note': 'S2 candidate records Haskell’s statement that the Avviso of 12 June 1677 appeared in Roma, vol. XIX (1941), p. 308; neither the notice nor the issue was independently consulted.',
    },
    'st-chp7-p190-n5-album-belongs-to-society': {
        'predicate': 'reported_belonging_to', 'subject': 'cand-7129', 'object': 'cand-7128', 'marker': 5, 'line': 378,
        'body_ids': ['st-chp7-p190-i26', 'st-chp7-p190-i27'],
        'note': 'S2 candidate preserves Haskell’s report that the album belonged to the Society of Antiquaries; the album and ownership statement were not independently verified.',
    },
    'st-chp7-p190-n5-haskell-acknowledges-harris': {
        'predicate': 'acknowledged_information_from', 'subject': 'cand-3770', 'object': 'cand-1292', 'marker': 5, 'line': 378,
        'body_ids': ['st-chp7-p190-i26', 'st-chp7-p190-i27'],
        'note': 'Haskell’s first-person acknowledgement thanks Enriqueta Harris for information on Del Carpio’s collection; the author endpoint is mapped to the accepted Francis Haskell candidate from the book’s title-page source.',
    },
    'st-chp7-p190-n5-inscription-names-gasparo-purchaser': {
        'predicate': 'frontispiece_identifies_buyer_of_antiquities_in_rome', 'subject': 'cand-7129', 'object': 'cand-0573', 'marker': 5, 'line': 378,
        'body_ids': ['st-chp7-p190-i13', 'st-chp7-p190-i26', 'st-chp7-p190-i27'],
        'note': 'This records what the album frontispiece says, as quoted by Haskell: that Del Carpio bought antiquities in Rome. The inscription was not independently inspected.',
    },
    'st-chp7-p191-n10-neapolitan-drawings': {
        'predicate': 'drawings_referenced_by_haskell', 'subject': 'cand-0571', 'object': 'cand-7141', 'marker': 10, 'line': 386,
        'body_ids': ['st-chp7-p191-i28', 'st-chp7-p191-i30'],
        'note': 'This preserves Haskell’s direction to Saxl for Del Carpio’s Neapolitan drawings; individual drawings are unidentified and Saxl’s cited page was not independently consulted.',
    },
    'st-chp7-p192-n2-franceschini-refusal': {
        'predicate': 'invitation_followed_refusal', 'subject': 'cand-1172', 'object': 'cand-1069', 'marker': 2, 'line': 389,
        'body_ids': ['st-chp7-p192-i09', 'st-chp7-p192-i12', 'st-chp7-p192-i15'],
        'note': 'S2 records Haskell’s report through Zanotti that Luca Giordano’s invitation to go to Spain followed Marcantonio Franceschini’s refusal. The invitation issuer, date, and exact arrangement are not stated; the cited page was not independently read.',
        'open_endpoint_reason': 'The invitation issuer, date, and terms are absent. The relation is only the reported sequence between Giordano’s invitation and Franceschini’s refusal.',
    },
}

BODY_CLASSIFICATIONS = {
    'st-chp7-p192-iv01': {
        'relation_candidate': False,
        'note': 'This is Haskell’s authorial synthesis about the geographic shift of patronage successors, not a claim linking identified successor patrons to a specific institution, work, or person. Retain the sequence as an argument and do not turn the named regions into patrons.',
    },
}

SOURCE_GUARDS = {
    375: '1 Harris, in Archivo Español, i960, pp. 109-36, and 1961, pp. 101-105',
    376: '2 For the fullest account of his politics! career see Ghelli.',
    377: '3 Maclaren, p. 76. 4 Avviso of 12 June 1677 published in Roma, XIX, 1941, p. 308.',
    378: '5 Harris, 1957, pp. 136-9.',
    379: '1 Bellori, 1942, pp. 117 and 121.',
    380: '2 See the introduction to the Society of Antiquaries’ album and Pacichelli, Parte IV, Vol. I, p. 39.',
    381: '3 Domenico Bernino, p. 28.',
    382: '4 Letter from Duc d’Estrées to Louis XIV, dated 27 July 1684, in Montaiglon, VI, p. 388.',
    383: '6 De Dominici, IV, p. 315.',
    384: '7 See Discursos leídos ame la Real Academia de Bellas Artes de San Fernando en la recepción pública del Exento Sr.',
    385: '8 Bottari, Et, p. 105, and Orlandi, p. 236.',
    386: '10 De Dominici, IV, p. 164. For Del Carpio’s Neapolitan drawings see Saxl, p. 76.',
    387: '11 See Listas de cuadros y objetos artísticos remitidos desde Italia a España por el puerto da Nápoles',
    388: '1 Pascoíi, I, p. 186, and II, p. 314.',
    389: '2 Griseri, 1956, pp. 33-9, and Longhi, 1954, pp. 28-39.',
}

REQUIRED_OCR = {
    'st-chp7-p190-n1-cite-harris-1960': [(375, 'i960', '1960')],
    'st-chp7-p190-n2-cite-ghelli': [(376, 'politics!', 'political')],
    'st-chp7-p191-n6-cite-dominici': [(383, '„', '')],
    'st-chp7-p191-n7-cite-address': [(384, 'ame', 'ante'), (384, 'Exento', 'Excmo.')],
    'st-chp7-p191-n8-cite-bottari': [(385, 'Et', 'II')],
    'st-chp7-p191-n11-cite-list': [(387, 'da Nápoles', 'de Nápoles')],
    'st-chp7-p192-n1-cite-pascoli-vol1': [(388, 'Pascoíi', 'Pascoli')],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def append_unique(seq: list, item: object) -> None:
    if item not in seq:
        seq.append(item)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = {p: p.read_bytes() for p in (STATEMENTS, CANDIDATES, SOURCE, SOURCE_IV, PDF)}
    hashes = {p.name: sha256(data) for p, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')
    for path, first_line, guard in [
        (SOURCE, 375, SOURCE_GUARDS[375]), (SOURCE, 376, SOURCE_GUARDS[376]),
        (SOURCE, 377, SOURCE_GUARDS[377]), (SOURCE, 378, SOURCE_GUARDS[378]),
        (SOURCE, 379, SOURCE_GUARDS[379]), (SOURCE, 380, SOURCE_GUARDS[380]),
        (SOURCE, 381, SOURCE_GUARDS[381]), (SOURCE, 382, SOURCE_GUARDS[382]),
        (SOURCE, 383, SOURCE_GUARDS[383]), (SOURCE, 384, SOURCE_GUARDS[384]),
        (SOURCE, 385, SOURCE_GUARDS[385]), (SOURCE, 386, SOURCE_GUARDS[386]),
        (SOURCE, 387, SOURCE_GUARDS[387]), (SOURCE, 388, SOURCE_GUARDS[388]),
        (SOURCE, 389, SOURCE_GUARDS[389]),
    ]:
        lines = raw[path].decode('utf-8-sig').splitlines()
        if guard not in lines[first_line - 1]:
            raise SystemExit(f'source guard failed at L{first_line}: {lines[first_line - 1]}')
    body_lines = raw[SOURCE_IV].decode('utf-8-sig').splitlines()
    if 'Despite the considerable impact of Spain, and even of France' not in body_lines[2]:
        raise SystemExit(f'p.192 body source guard failed: {body_lines[2]}')

    candidates = {r['candidate_id']: r for r in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))}
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source book candidate is missing or mistyped')
    for spec in CITATIONS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f'publication candidate missing or mistyped: {spec["publication_id"]}')
    for cid, expected_type in [
        ('cand-3770', 'person'), ('cand-1292', 'person'), ('cand-7126', 'archive'), ('cand-7125', 'archive'),
        ('cand-7129', 'archive'), ('cand-7128', 'institution'), ('cand-0573', 'person'),
        ('cand-0571', 'person'), ('cand-7141', 'work'), ('cand-1172', 'person'), ('cand-1069', 'person'),
    ]:
        if candidates.get(cid, {}).get('suggested_type') != expected_type:
            raise SystemExit(f'claim endpoint missing or mistyped: {cid} expected {expected_type}')

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {r['statement_id']: r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_note_ids = set(CITATIONS) | set(CLAIMS)
    actual_unset_note_ids = {
        r['statement_id'] for r in rows
        if any(f'p{p}-' in r['statement_id'] for p in [190, 191, 192])
        and (r.get('qualifiers') or {}).get('relation_candidate') is None
        and 'n' in r['statement_id']
    }
    if actual_unset_note_ids != expected_note_ids:
        raise SystemExit(f'pages 190–192 unset note set differs: {sorted(actual_unset_note_ids ^ expected_note_ids)}')
    if (by_id['st-chp7-p192-iv01'].get('qualifiers') or {}).get('relation_candidate') is not None:
        raise SystemExit('p.192 synthesis row changed since review')

    body_to_notes: dict[str, list[tuple[str, int, int]]] = {}
    for note_id, spec in {**CITATIONS, **CLAIMS}.items():
        r = by_id[note_id]
        q = r.get('qualifiers') or {}
        expected_predicate = 'footnote_citation' if note_id in CITATIONS else spec['predicate']
        if (r.get('segment_id') != NOTE_SEGMENT or r.get('predicate') != expected_predicate
                or q.get('source_line_start') != spec['line'] or q.get('footnote_marker') != spec['marker']
                or q.get('relation_candidate') is not None
                or q.get('linked_body_statement_ids') != spec['body_ids']):
            raise SystemExit(f'note row changed since review: {note_id}')
        if note_id in CITATIONS and r.get('object_candidate_id') != spec['publication_id']:
            raise SystemExit(f'citation target changed since review: {note_id}')
        if note_id in CLAIMS:
            expected_before_subject = None if note_id == 'st-chp7-p190-n5-haskell-acknowledges-harris' else spec['subject']
            if (r.get('predicate'), r.get('subject_candidate_id'), r.get('object_candidate_id')) != (spec['predicate'], expected_before_subject, spec['object']):
                raise SystemExit(f'claim endpoints changed since review: {note_id}')
        for body_id in spec['body_ids']:
            body = by_id.get(body_id)
            if body is None or body.get('segment_id') not in {
                'chp-7:07_CHP-7_sec_i:l259-266', 'chp-7:07_CHP-7_sec_i:l268-280',
                'chp-7:07_CHP-7_sec_i:l282-291',
            }:
                raise SystemExit(f'linked body statement missing or outside expected chapter segment: {body_id}')
            body_q = body.get('qualifiers') or {}
            if body_q.get('footnote_segment') not in (None, NOTE_SEGMENT):
                raise SystemExit(f'body footnote segment mismatch: {body_id}')
            body_to_notes.setdefault(body_id, []).append((note_id, spec['marker'], spec['line']))
    for note_id, corrections in REQUIRED_OCR.items():
        actual = (by_id[note_id].get('qualifiers') or {}).get('ocr_corrections') or []
        for line, source_form, print_form in corrections:
            if not any(c.get('source_line') == line and c.get('source_form') == source_form and c.get('print_form') == print_form for c in actual):
                raise SystemExit(f'recorded OCR correction missing on {note_id}: {source_form} -> {print_form}')

    output = []
    for src in rows:
        r = dict(src)
        sid = r['statement_id']
        if sid in CITATIONS:
            spec = CITATIONS[sid]
            q = dict(r.get('qualifiers') or {})
            publication_id = spec['publication_id']
            old_claim = str(q.get('claim') or '').strip()
            r.update({'subject_candidate_id': SOURCE_BOOK_ID, 'object_candidate_id': publication_id, 'predicate': 'cites'})
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {spec['locator']} in footnote {spec['marker']}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id, 'citation_locator': spec['locator'],
                'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': publication_id, 'locator': spec['locator']}],
                'cited_material_not_independently_consulted': True,
                'footnote_number': spec['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
                'related_body_statement_ids': spec['body_ids'], 'linked_body_statement_ids': spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_body_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies this source and locator; the cited publication or document was not independently consulted, and no S6 edge is created.',
            })
            r['qualifiers'] = q
        elif sid in CLAIMS:
            spec = CLAIMS[sid]
            q = dict(r.get('qualifiers') or {})
            r['subject_candidate_id'] = spec['subject']
            r['object_candidate_id'] = spec['object']
            q.update({
                'footnote_number': spec['marker'], 'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': NOTE_SEGMENT, 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
                'related_body_statement_ids': spec['body_ids'], 'linked_body_statement_ids': spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_body_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True, 'relation_candidate_note': spec['note'],
            })
            if spec.get('open_endpoint_reason'):
                q['open_endpoint_reason'] = spec['open_endpoint_reason']
            if sid == 'st-chp7-p190-n5-haskell-acknowledges-harris':
                ids = q.setdefault('mentioned_candidate_ids', [])
                append_unique(ids, 'cand-3770')
            r['qualifiers'] = q
        elif sid in BODY_CLASSIFICATIONS:
            spec = BODY_CLASSIFICATIONS[sid]
            q = dict(r.get('qualifiers') or {})
            q['relation_candidate'] = spec['relation_candidate']
            q['relation_candidate_note'] = spec['note']
            r['qualifiers'] = q
        if sid in body_to_notes:
            q = dict(r.get('qualifiers') or {})
            refs = q.setdefault('footnote_refs', [])
            note_ids = q.setdefault('footnote_statement_ids', [])
            for note_id, marker, line in body_to_notes[sid]:
                append_unique(refs, {'marker': marker, 'segment_id': NOTE_SEGMENT, 'source_line': line})
                append_unique(note_ids, note_id)
            q['footnote_body_link_status'] = 'linked'
            q['footnote_segment'] = NOTE_SEGMENT
            q['footnote_text_pending'] = False
            r['qualifiers'] = q
        output.append(r)

    out = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14187, {True: 8586, False: 3419, 'unset': 2182}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    for body_id, refs in body_to_notes.items():
        q = next(r['qualifiers'] for r in output if r['statement_id'] == body_id)
        for note_id, marker, line in refs:
            if note_id not in q.get('footnote_statement_ids', []) or {'marker': marker, 'segment_id': NOTE_SEGMENT, 'source_line': line} not in q.get('footnote_refs', []):
                raise SystemExit(f'post-state reciprocal body reference failed: {body_id} <- {note_id}')
    report = {'mode': 'apply' if args.apply else 'dry_run', 'normalized_citations': len(CITATIONS),
              'classified_note_claims': len(CLAIMS), 'classified_body_statements': len(BODY_CLASSIFICATIONS),
              'body_statements_with_explicit_backlinks': len(body_to_notes),
              'reciprocal_body_statement_links': sum(len(v) for v in body_to_notes.values()),
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
