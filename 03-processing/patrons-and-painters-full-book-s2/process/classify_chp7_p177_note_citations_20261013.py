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
BODY_SEGMENT = 'chp-7:07_CHP-7_sec_i:l91-100'
NOTE_SEGMENT = 'chp-7:07_CHP-7_sec_i:l293-389'
SOURCE_BOOK_ID = 'cand-2962'
EXPECTED_HASHES = {
    STATEMENTS.name: '4aa02729efd4c90faf0a08f8d700bd20f32902a1693a6d01f1e39ca3b3213e87',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p177-notes-20261013')

TARGETS = {
    'st-chp7-p177-n1-cite-baldinucci': {
        'publication_id': 'cand-4548', 'locator': 'Baldinucci, Vita del Cavaliere Gio. Lorenzo Bernini (1948), p. 92',
        'marker': 1, 'line': 319, 'body_ids': ['st-chp7-p177-i01', 'st-chp7-p177-i03'],
    },
    'st-chp7-p177-n2-cite-stone': {
        'publication_id': 'cand-7048', 'locator': 'Stone, “The market for Italian art” (1959), p. 92',
        'marker': 2, 'line': 320, 'body_ids': ['st-chp7-p177-i06'],
    },
    'st-chp7-p177-n2-cite-betcherman': {
        'publication_id': 'cand-7050', 'locator': 'Betcherman, “Balthazar Gerbier in seventeenth century Italy” (1961), pp. 325–331',
        'marker': 2, 'line': 320, 'body_ids': ['st-chp7-p177-i06'],
    },
    'st-chp7-p177-n3-cite-luzio': {
        'publication_id': 'cand-7052', 'locator': 'Luzio, La galleria dei Gonzaga venduta all’Inghilterra nel 1627–38 (1913), pp. 63–167',
        'marker': 3, 'line': 321, 'body_ids': ['st-chp7-p177-i07', 'st-chp7-p177-i08'],
    },
    'st-chp7-p177-n4-cite-lumbroso': {
        'publication_id': 'cand-5683', 'locator': 'Lumbroso, Notizie sulla vita di Cassiano dal Pozzo (1874), p. 369',
        'marker': 4, 'line': 322, 'body_ids': ['st-chp7-p177-i09'],
    },
    'st-chp7-p177-n4-cite-venturi': {
        'publication_id': 'cand-4354', 'locator': 'Venturi, La R. Galleria Estense in Modena (1883), p. 252',
        'marker': 4, 'line': 322, 'body_ids': ['st-chp7-p177-i09'],
    },
    'st-chp7-p177-n5-cite-albion': {
        'publication_id': 'cand-7055', 'locator': 'Albion, Charles I and the Court of Rome (1935), passim',
        'marker': 5, 'line': 323, 'body_ids': ['st-chp7-p177-i14'],
    },
}

FACTS = {
    'st-chp7-p177-n4-letter-authored-by': {
        'relation_candidate': True,
        'note': 'This records the footnote’s explicit attribution of the 1645 letter to Gabriele Balestrieri; it does not imply that the letter was independently consulted.',
    },
    'st-chp7-p177-n4-letter-quoted-content': {
        'relation_candidate': False,
        'note': 'This preserves the content Haskell attributes to the quoted 1645 letter. It is an attributed statement about what the letter says; the letter’s author and addressee are recorded separately.',
    },
}

SOURCE_GUARDS = {
    319: ('1 Baldinucci, 1948, p. 92.',),
    320: ('2 Stone, p. 92, and also Betcherman, pp. 325-31.',),
    321: ('3 Luzio, pp. 63-167.',),
    322: ('4 Lumbroso, p. 369, and in 1645 Gabriele Balestrieri wrote to the Duke of Modena',),
    323: ('5 Albion, passim.',),
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
    body_to_citations: dict[str, list[str]] = {}
    body_expected_refs: dict[str, tuple[int, int]] = {}
    for citation_id, spec in TARGETS.items():
        for body_id in spec['body_ids']:
            body_to_citations.setdefault(body_id, []).append(citation_id)
            body_expected_refs[body_id] = (spec['marker'], spec['line'])

    required = set(TARGETS) | set(FACTS) | set(body_to_citations) | {'st-chp7-p177-n4-letter-addressed-to'}
    if not required.issubset(by_id):
        raise SystemExit(f'missing citation/fact/body statement: {sorted(required - set(by_id))}')
    unset_citations = {
        row['statement_id'] for row in rows
        if row.get('segment_id') == NOTE_SEGMENT
        and 319 <= (row.get('qualifiers') or {}).get('source_line_start', 0) <= 323
        and row.get('predicate') == 'footnote_citation'
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if unset_citations != set(TARGETS):
        raise SystemExit(f'p.177 unset citation target set changed: {sorted(unset_citations ^ set(TARGETS))}')
    for citation_id, spec in TARGETS.items():
        row = by_id[citation_id]
        q = row.get('qualifiers') or {}
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('predicate') != 'footnote_citation'
                or row.get('subject_candidate_id') is not None
                or row.get('object_candidate_id') != spec['publication_id']
                or q.get('source_line_start') != spec['line']
                or q.get('relation_candidate') is not None):
            raise SystemExit(f'citation changed since review: {citation_id}')
    for fact_id in FACTS:
        row = by_id[fact_id]
        if (row.get('segment_id') != NOTE_SEGMENT or row.get('qualifiers', {}).get('relation_candidate') is not None
                or row.get('qualifiers', {}).get('source_line_start') != 322):
            raise SystemExit(f'letter fact changed since review: {fact_id}')
    address = by_id['st-chp7-p177-n4-letter-addressed-to']
    if (address.get('subject_candidate_id') != 'cand-7053' or address.get('object_candidate_id') != 'cand-1675'
            or address.get('qualifiers', {}).get('relation_candidate') is not True):
        raise SystemExit('letter addressee statement changed since review')
    for body_id, (marker, line_no) in body_expected_refs.items():
        q = by_id[body_id].get('qualifiers') or {}
        if not any(ref.get('marker') == marker and ref.get('segment_id') == NOTE_SEGMENT
                   and ref.get('source_line') == line_no for ref in (q.get('footnote_refs') or [])):
            raise SystemExit(f'body footnote locator changed: {body_id}')

    output = []
    for source_row in rows:
        row = dict(source_row)
        citation_spec = TARGETS.get(row['statement_id'])
        fact_spec = FACTS.get(row['statement_id'])
        if citation_spec is not None:
            publication_id = citation_spec['publication_id']
            q = dict(row.get('qualifiers') or {})
            old_claim = str(q.get('claim') or '').strip()
            marker, line_no = citation_spec['marker'], citation_spec['line']
            linked_citations = [
                sid for sid, spec in TARGETS.items()
                if spec['marker'] == marker and spec['line'] == line_no
            ]
            row.update({
                'subject_candidate_id': SOURCE_BOOK_ID,
                'object_candidate_id': publication_id,
                'predicate': 'cites',
            })
            q.update({
                'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {citation_spec['locator']} in footnote {marker}. The prior note records: {old_claim}",
                'citation_publication_candidate_id': publication_id,
                'citation_locator': citation_spec['locator'],
                'citations': [{
                    'source_candidate_id': SOURCE_BOOK_ID,
                    'publication_candidate_id': publication_id,
                    'locator': citation_spec['locator'],
                }],
                'cited_material_not_independently_consulted': True,
                'footnote_marker': marker,
                'footnote_number': marker,
                'footnote_segment': NOTE_SEGMENT,
                'footnote_refs': [{
                    'marker': marker,
                    'segment_id': NOTE_SEGMENT,
                    'source_line': line_no,
                    'statement_ids': linked_citations,
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
        elif fact_spec is not None:
            q = dict(row.get('qualifiers') or {})
            q['relation_candidate'] = fact_spec['relation_candidate']
            q['relation_candidate_note'] = fact_spec['note']
            if row['statement_id'] == 'st-chp7-p177-n4-letter-authored-by':
                q['qualification'] = 'The letter is identified in Haskell’s footnote and quoted through Venturi; neither the letter nor the cited page was independently consulted.'
            if row['statement_id'] == 'st-chp7-p177-n4-letter-quoted-content':
                q['qualification'] = 'Attributed by Haskell to the 1645 letter and quoted through A. Venturi, p. 252; preserve as a source claim, not as an independently verified report about all English buyers.'
                q['ocr_corrections'] = [{
                    'source_line': 322,
                    'ocr': 'the quotation and Venturi locator are truncated after “gli Inglesi...”',
                    'print_reading': '… non hanno guardato a spesa per haver pitture di qual si voglia sorte — A. Venturi, p. 252.',
                    'basis': 'CHP-7.pdf physical page 11',
                }]
            row['qualifiers'] = q
        output.append(row)

    by_out = {row['statement_id']: row for row in output}
    for body_id, citation_ids in body_to_citations.items():
        marker, line_no = body_expected_refs[body_id]
        row = by_out[body_id]
        q = dict(row.get('qualifiers') or {})
        refs = [dict(ref) for ref in (q.get('footnote_refs') or [])]
        ref = next(item for item in refs
                   if item.get('marker') == marker and item.get('segment_id') == NOTE_SEGMENT
                   and item.get('source_line') == line_no)
        ref['statement_ids'] = citation_ids
        q.update({
            'footnote_refs': refs,
            'footnote_marker': marker,
            'footnote_number': marker,
            'footnote_segment': NOTE_SEGMENT,
            'footnote_statement_ids': citation_ids,
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
    if (len(output), counts) != (14187, {True: 8453, False: 3420, 'unset': 2314}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'normalized_citations': len(TARGETS),
        'classified_footnote_facts': len(FACTS),
        'linked_body_statements': len(body_to_citations),
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
