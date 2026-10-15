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
TABLES = ROOT / '04-knowledge' / 'tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_i.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l102-111'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: 'd13f7e75ca4201f9f240093aa7ca1c6356e027924483d68823c6adfa3a22cf55',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p178-notes-20261013')

TARGETS = {
    'st-chp7-p178-n1-cite-mahon': {
        'publication_id': 'cand-7057', 'locator': 'Mahon, “Guercino’s paintings of Semiramis” (1949), p. 222',
        'marker': 1, 'line': 324, 'body_ids': ['st-chp7-p178-i02'],
    },
    'st-chp7-p178-n1-cite-malvasia': {
        'publication_id': 'cand-6933', 'locator': 'Malvasia, Felsina Pittrice, vol. II, p. 261',
        'marker': 1, 'line': 324, 'body_ids': ['st-chp7-p178-i02'],
    },
    'st-chp7-p178-n2-cite-walpole': {
        'publication_id': 'cand-7058', 'locator': 'Walpole, Anecdotes of Painting in England, vol. II (1762), p. 51',
        'marker': 2, 'line': 325, 'body_ids': ['st-chp7-p178-i03'],
        'bibliography_note': 'The footnote prints 1762, vol. II, p. 51; the bibliography entry on p. 440 prints 1726 for the five-volume set. The discrepancy remains unresolved.',
    },
    'st-chp7-p178-n3-cite-baldinucci': {
        'publication_id': 'cand-7059', 'locator': 'Baldinucci, vol. V (1702), p. 361; exact title/edition unresolved',
        'marker': 3, 'line': 326, 'body_ids': ['st-chp7-p178-i05'],
    },
    'st-chp7-p178-n4-cite-crino': {
        'publication_id': 'cand-7060', 'locator': 'Crinò, “Due lettere autografe inedite di Orazio e di Artemisia Gentileschi,” p. 203',
        'marker': 4, 'line': 327, 'body_ids': ['st-chp7-p178-i08'],
    },
    'st-chp7-p178-n4-cite-hess': {
        'publication_id': 'cand-7062', 'locator': 'Hess, “Die Gemälde des Orazio Gentileschi für das Haus der Königin in Greenwich” (1952), pp. 159–187',
        'marker': 4, 'line': 327, 'body_ids': ['st-chp7-p178-i08'],
    },
    'st-chp7-p178-n6-cite-pope-hennessy': {
        'publication_id': 'cand-7064', 'locator': 'Pope-Hennessy (1953), pp. 157–162',
        'marker': 6, 'line': 329, 'body_ids': ['st-chp7-p178-i17'],
        'ocr_correction': {'source_line': 329, 'ocr_footnote_marker': 8, 'printed_footnote_marker': 6, 'basis': 'CHP-7.pdf physical page 12'},
    },
    'st-chp7-p178-n6-cite-whinney-millar': {
        'publication_id': 'cand-7066', 'locator': 'Whinney and Millar, English Art, 1625–1714, pp. 121–122',
        'marker': 6, 'line': 329, 'body_ids': ['st-chp7-p178-i17'],
        'ocr_correction': {'source_line': 329, 'ocr_footnote_marker': 8, 'printed_footnote_marker': 6, 'basis': 'CHP-7.pdf physical page 12'},
    },
}

FACTS = {
    'st-chp7-p178-n1-mahon-interpretation': {
        'relation_candidate': True,
        'note': 'This preserves Mahon’s attributed negative interpretation about whether the Semiramis picture was connected to Charles I’s invitation to Guercino; it is not treated as a settled historical conclusion.',
        'body_ids': ['st-chp7-p178-i02'], 'marker': 1, 'line': 324,
        'cited_material_not_independently_consulted': True,
    },
    'st-chp7-p178-n2-walpole-assessment': {
        'relation_candidate': True,
        'note': 'This records Haskell’s assessment of the cited Walpole account as evidence; it does not independently verify the account’s substantial truth.',
        'body_ids': ['st-chp7-p178-i03'], 'marker': 2, 'line': 325,
        'subject_candidate_id': 'cand-2962', 'object_candidate_id': 'cand-7058',
        'cited_material_not_independently_consulted': True,
    },
    'st-chp7-p178-n5-artemisia-daughter': {
        'relation_candidate': True,
        'note': 'This records Haskell’s explicit statement that Artemisia Gentileschi was Orazio Gentileschi’s daughter; it is not independently verified here.',
        'body_ids': ['st-chp7-p178-i16'], 'marker': 5, 'line': 328,
        'ocr_correction': {'source_line': 328, 'ocr_footnote_marker': 6, 'printed_footnote_marker': 5, 'basis': 'CHP-7.pdf physical page 12'},
    },
    'st-chp7-p178-n5-artemisia-england': {
        'relation_candidate': True,
        'note': 'This records Haskell’s claim that Artemisia came to England for about one or two years around 1638; preserve the approximate date and duration.',
        'body_ids': ['st-chp7-p178-i16'], 'marker': 5, 'line': 328,
        'ocr_correction': {'source_line': 328, 'ocr_footnote_marker': 6, 'printed_footnote_marker': 5, 'basis': 'CHP-7.pdf physical page 12'},
    },
}

SOURCE_GUARDS = {
    324: ('1 Malvasia, II, p. 261, and Mahon, 1949, p. 222',),
    325: ('2 Walpole, 1762, II, p. 51.', 'no reason to doubt its substantial truth.'),
    326: ('3 Baldinucci, V, 1702, p. 361.',),
    327: ('4 Crinò, p. 203; Hess, 1952, pp. 159-87.',),
    328: ('6 Orazio’s daughter, the painter Artemisia Gentileschi', 'about 1638.'),
    329: ('8 Pope-Hennessy, 1953, pp. 157-62; Whinney and Millar, pp. 121-2.'),
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
    for line_no, snippets in SOURCE_GUARDS.items():
        source_line = source_lines[line_no - 1]
        if any(snippet not in source_line for snippet in snippets):
            raise SystemExit(f'source guard failed at L{line_no}: {source_line}')

    candidates = {
        row['candidate_id']: row
        for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))
    }
    if candidates.get(SOURCE_BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell source-book candidate is absent or not archive typed')
    for spec in TARGETS.values():
        if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
            raise SystemExit(f"citation archive missing or mistyped: {spec['publication_id']}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    body_to_note_ids: dict[str, list[str]] = {}
    body_expected_refs: dict[str, tuple[int, int]] = {}
    for note_id, spec in TARGETS.items():
        for body_id in spec['body_ids']:
            body_to_note_ids.setdefault(body_id, []).append(note_id)
            body_expected_refs[body_id] = (spec['marker'], spec['line'])
    for note_id, spec in FACTS.items():
        for body_id in spec['body_ids']:
            body_to_note_ids.setdefault(body_id, []).append(note_id)
            body_expected_refs[body_id] = (spec['marker'], spec['line'])

    required = set(TARGETS) | set(FACTS) | set(body_to_note_ids)
    if not required.issubset(by_id):
        raise SystemExit(f'missing note/body statement: {sorted(required - set(by_id))}')
    unset_targets = {
        row['statement_id'] for row in rows
        if row.get('segment_id') == NOTE_SEGMENT
        and 324 <= (row.get('qualifiers') or {}).get('source_line_start', 0) <= 329
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if unset_targets != set(TARGETS) | set(FACTS):
        raise SystemExit(f'p.178 unset target set changed: {sorted(unset_targets ^ (set(TARGETS) | set(FACTS)))}')
    for note_id, spec in TARGETS.items():
        row = by_id[note_id]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation changed since review: {note_id}')
    for note_id, spec in FACTS.items():
        row = by_id[note_id]
        if row.get('segment_id') != NOTE_SEGMENT or row.get('qualifiers', {}).get('source_line_start') != spec['line']:
            raise SystemExit(f'footnote fact anchor changed: {note_id}')
    for body_id, (marker, line_no) in body_expected_refs.items():
        q = by_id[body_id].get('qualifiers') or {}
        if not any(ref.get('marker') == marker and ref.get('segment_id') == NOTE_SEGMENT
                   and ref.get('source_line') == line_no for ref in (q.get('footnote_refs') or [])):
            raise SystemExit(f'body footnote locator changed: {body_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        spec = TARGETS.get(row['statement_id'])
        fact_spec = FACTS.get(row['statement_id'])
        if spec is not None:
            publication_id = spec['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            body_ids = spec['body_ids']
            marker, line_no = spec['marker'], spec['line']
            locator = spec['locator']
            row.update({
                'subject_candidate_id': SOURCE_BOOK_ID,
                'object_candidate_id': publication_id,
                'predicate': 'cites',
            })
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {locator} in footnote {marker}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id,
                'citation_locator': locator,
                'citations': [{
                    'source_candidate_id': SOURCE_BOOK_ID,
                    'publication_candidate_id': publication_id,
                    'locator': locator,
                }],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': marker,
                'footnote_number': marker,
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': marker,
                    'segment_id': NOTE_SEGMENT,
                    'source_line': line_no,
                    'statement_ids': body_ids,
                }],
                'related_body_statement_ids': body_ids,
                'linked_body_statement_ids': body_ids,
                'footnote_link_status': 'linked',
                'footnote_text_pending': False,
                'relation_candidate': True,
                'relation_candidate_note': (
                    'S2 citation candidate: the printed footnote identifies this source and locator. '
                    'This records Haskell’s bibliographic reference only; the cited material was not '
                    'independently consulted and no S6 edge is created.'
                ),
            })
            if spec.get('bibliography_note'):
                q['bibliography_locator_discrepancy'] = spec['bibliography_note']
            if spec.get('ocr_correction'):
                q['ocr_corrections'] = [spec['ocr_correction']]
            row['qualifiers'] = q
        elif fact_spec is not None:
            q = dict(row.get('qualifiers') or {})
            q['relation_candidate'] = fact_spec['relation_candidate']
            q['relation_candidate_note'] = fact_spec['note']
            q['footnote_marker'] = fact_spec['marker']
            q['footnote_number'] = fact_spec['marker']
            q['footnote_segment'] = NOTE_SEGMENT
            q['footnote_refs'] = [{
                'marker': fact_spec['marker'],
                'segment_id': NOTE_SEGMENT,
                'source_line': fact_spec['line'],
                'statement_ids': fact_spec['body_ids'],
            }]
            q['related_body_statement_ids'] = fact_spec['body_ids']
            q['linked_body_statement_ids'] = fact_spec['body_ids']
            q['footnote_link_status'] = 'linked'
            q['footnote_text_pending'] = False
            if fact_spec.get('cited_material_not_independently_consulted'):
                q['cited_material_not_independently_consulted'] = True
            if fact_spec.get('ocr_correction'):
                q['ocr_corrections'] = [fact_spec['ocr_correction']]
            if fact_spec.get('subject_candidate_id'):
                if row.get('subject_candidate_id') != 'cand-7058' or row.get('object_candidate_id') is not None:
                    raise SystemExit(f'unexpected Haskell assessment endpoints: {row["statement_id"]}')
                row['subject_candidate_id'] = fact_spec['subject_candidate_id']
                row['object_candidate_id'] = fact_spec['object_candidate_id']
            row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for body_id, note_ids in body_to_note_ids.items():
        marker, line_no = body_expected_refs[body_id]
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = [dict(ref) for ref in (q.get('footnote_refs') or [])]
        ref = next(item for item in refs
                   if item.get('marker') == marker and item.get('segment_id') == NOTE_SEGMENT
                   and item.get('source_line') == line_no)
        ref['statement_ids'] = note_ids
        q.update({
            'footnote_refs': refs,
            'footnote_marker': marker,
            'footnote_number': marker,
            'footnote_segment': NOTE_SEGMENT,
            'footnote_statement_ids': note_ids,
            'footnote_link_status': 'linked',
            'footnote_text_pending': False,
        })
        row['qualifiers'] = q

    output_bytes = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    counts = {
        True: sum((row.get('qualifiers') or {}).get('relation_candidate') is True for row in output),
        False: sum((row.get('qualifiers') or {}).get('relation_candidate') is False for row in output),
        'unset': sum((row.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for row in output),
    }
    if (len(output), counts) != (14187, {True: 8465, False: 3420, 'unset': 2302}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(TARGETS),
        'classified_footnote_claims': len(FACTS),
        'linked_body_statements': len(body_to_note_ids),
        'printed_footnote_markers_corrected': 2,
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
