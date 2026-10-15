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
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_iv.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
SOURCE_BOOK_ID = 'cand-2962'
P193_BODY = 'chp-7:07_CHP-7_sec_iv:l6-21'
P193_NOTES = 'chp-7:07_CHP-7_sec_iv:l97-119'
P194_BODY = 'chp-7:07_CHP-7_sec_iv:l23-36'
EXPECTED_HASHES = {
    STATEMENTS.name: '383a0b9cf27d20fc614e75ccf807269b5b9641689b6dc8c1677f4c187c31eac2',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'd620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p193-194-20261013')

SPLIT_CITATIONS = {
    'st-chp7-p193-n3-lavagnino-heilbronner': [
        {
            'statement_id': 'st-chp7-p193-n3-cite-lavagnino', 'publication_id': 'cand-7251',
            'locator': 'Lavagnino, Gli artisti italiani in Germania, vol. III, p. 69',
            'body_ids': ['st-chp7-p193-wittelsbach-alliance'], 'marker': 3, 'line': 99,
            'context': 'in connection with Haskell’s Wittelsbach account',
        },
        {
            'statement_id': 'st-chp7-p193-n3-cite-heilbronner', 'publication_id': 'cand-7252',
            'locator': 'Heilbronner, “Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera” (1936), pp. 887–904',
            'body_ids': ['st-chp7-p193-wittelsbach-alliance'], 'marker': 3, 'line': 99,
            'context': 'in connection with Haskell’s Wittelsbach account',
        },
    ],
    'st-chp7-p194-n3-hantsch-freeden': [
        {
            'statement_id': 'st-chp7-p194-n3-cite-hantsch-scherf', 'publication_id': 'cand-6576',
            'locator': 'Hantsch and Scherf, Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn, I. Teil, erster Halbband (Augsburg, 1931)',
            'body_ids': ['st-chp7-p194-schoenborn-commission-group'], 'marker': 3, 'line': 101,
            'context': 'in connection with the Schönborn patronage account', 'keep_ocr_correction': True,
        },
        {
            'statement_id': 'st-chp7-p194-n3-cite-von-freeden', 'publication_id': 'cand-7253',
            'locator': 'von Freeden, Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn, I. Teil, zweiter Halbband (1955)',
            'body_ids': ['st-chp7-p194-schoenborn-commission-group'], 'marker': 3, 'line': 101,
            'context': 'in connection with the Schönborn patronage account',
        },
    ],
}

NOTE_CLAIMS = {
    'st-chp7-p193-n2-boschini-collection': {
        'marker': 2, 'line': 21, 'segment': P193_BODY,
        'body_ids': ['st-chp7-p193-leopold-venetian-painters'],
        'note': 'This preserves Haskell’s footnote statement about Boschini’s discussion of Leopold Wilhelm’s Venetian old-master collection; Boschini’s book and the collection scope were not independently checked.',
    },
}

TRUE_IDS = {
    'st-chp7-p193-adelaide-fails-to-attract-guarini',
    'st-chp7-p193-adelaide-surrounds-artists',
    'st-chp7-p193-barelli-nymphenburg',
    'st-chp7-p193-ferdinand-maria-marriage',
    'st-chp7-p193-leopold-bequest',
    'st-chp7-p193-leopold-commissions-stage-sets',
    'st-chp7-p193-leopold-commissions-wing',
    'st-chp7-p193-leopold-venetian-painters',
    'st-chp7-p193-munich-italian-painters',
    'st-chp7-p193-vecchia-forgeries',
    'st-chp7-p193-war-vienna',
    'st-chp7-p193-wittelsbach-recovery',
    'st-chp7-p194-arrighini-theatre-celle',
    'st-chp7-p194-cadani-employed-dresden',
    'st-chp7-p194-cross-page-renaissance',
    'st-chp7-p194-german-princely-taste-variation',
    'st-chp7-p194-italian-painters-work-for-princes',
    'st-chp7-p194-liechtenstein-enriched-by-expropriations',
    'st-chp7-p194-liechtenstein-order-franceschini',
    'st-chp7-p194-painters-new-patronal-responsibilities',
    'st-chp7-p194-princely-palace-collections',
    'st-chp7-p194-principalities-attract-painters',
}

FALSE_NOTES = {
    'st-chp7-p193-theatre-italian-influence': 'This is a broad cultural interpretation about theatre as a medium of Italian influence; the source names no identifiable performance, work, or participant to form an entity relation.',
    'st-chp7-p194-mediocre-artists-assessment': 'This is Haskell’s evaluative judgement of an unnamed group’s artistic quality, not a source-backed relation between distinct entities.',
    'st-chp7-p194-papal-cardinal-collection-limit': 'This is Haskell’s general comparison of collecting capacity. It does not identify a collection or object that can be linked without adding an unsupported endpoint.',
    'st-chp7-p194-patronage-decisive-for-painting': 'This is an emphatic authorial assessment of the importance of German patronage, not a relation between identified entities; retain it as a source claim.',
    'st-chp7-p194-roman-patronage-comparison': 'This is Haskell’s comparative evaluation of Roman patronage. The cited cities are comparators, not the agents or objects of a historical relation.',
    'st-chp7-p194-scope-of-german-patronage': 'This is a statement about the scope of Haskell’s own discussion rather than a historical relation among entities.',
}

OPEN_ENDPOINT_NOTES = {
    'st-chp7-p193-leopold-father-summoned-burnacini': 'The father is unnamed in this passage and is not identified by inference.',
    'st-chp7-p193-leopold-i-patronage': 'The predecessors and individual Italian artists are not identified; preserve Haskell’s group-level claim.',
    'st-chp7-p193-liberi-vienna': 'The individual pictures and the basis of the title are not specified; no particular work or title-granting authority is inferred.',
    'st-chp7-p193-loot-mitigated': 'The acquired pictures are not individually identified; only some are traced by Haskell to Charles I’s gallery.',
    'st-chp7-p193-prague-looting': 'The precise date, objects, and transfer sequence are not supplied; “ultimate benefit” remains Haskell’s framing.',
    'st-chp7-p193-rulers-generalization-open': 'No individual rulers, works, or commissions are named; the linked p.193–194 statements remain one source-defined generalization.',
    'st-chp7-p193-vienna-threat-limits-building': 'No particular Turkish force, ruler, or campaign is named; the statement is limited to Haskell’s account of continuing threat.',
    'st-chp7-p193-wittelsbach-alliance': 'The ruling family is unnamed. The nearby Savoy marriage does not by itself identify it.',
    'st-chp7-p193-zuccalli-schleissheim-project': 'The commissioning agent, final design, and completion are not stated; the planned project is distinct from a completed palace.',
    'st-chp7-p194-carlone-court-migration': 'The source does not enumerate Carlone family members or the courts visited.',
    'st-chp7-p194-letter-subject-suggestions': 'These are proposals in the letter, not evidence that any suggested painting was made.',
    'st-chp7-p194-liechtenstein-letter-subject-discretion': 'The passage names only a Prince of Liechtenstein. The index association with Wenzel remains unresolved pending S3.',
    'st-chp7-p194-nudes-expected': 'No individual nude painting or named patron is identified; retain the source’s broad characterization.',
    'st-chp7-p194-output-sent-north': 'No individual paintings or destinations are identified; “in some cases” limits the scope.',
    'st-chp7-p194-schoenborn-commission-group': 'The paintings are unnamed; the cities associate the listed artists and do not establish where each picture was executed.',
    'st-chp7-p194-unattributed-quote-open': 'The gallery remains unidentified. The p.195 continuation attributes the quoted description to the Prince, but the index identity is not treated as resolved here.',
}

SOURCE_GUARDS = {
    99: '3 Lavagnino, p. 69, and Heilbronner, pp. 887-904.',
    101: '8 Hantsch und Schers and von Freeden, 1955.',
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


def make_citation_row(source_row: dict, spec: dict, candidates: dict) -> dict:
    row = dict(source_row)
    q = dict(source_row.get('qualifiers') or {})
    publication_id = spec['publication_id']
    old_claim = str(q.get('claim') or '').strip()
    row['statement_id'] = spec['statement_id']
    row['subject_candidate_id'] = SOURCE_BOOK_ID
    row['object_candidate_id'] = publication_id
    row['predicate'] = 'cites'
    q.update({
        'claim': f"Haskell’s book cites {candidates[publication_id]['canonical_name']} at {spec['locator']} in footnote {spec['marker']}, {spec['context']}. The prior footnote records: {old_claim}",
        'citation_publication_candidate_id': publication_id,
        'citation_locator': spec['locator'],
        'citations': [{'source_candidate_id': SOURCE_BOOK_ID, 'publication_candidate_id': publication_id, 'locator': spec['locator']}],
        'cited_material_not_independently_consulted': True,
        'footnote_number': spec['marker'], 'footnote_segment': source_row['segment_id'],
        'footnote_refs': [{'marker': spec['marker'], 'segment_id': source_row['segment_id'], 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
        'related_body_statement_ids': spec['body_ids'], 'linked_body_statement_ids': spec['body_ids'],
        'footnote_link_status': 'linked', 'footnote_body_link_status': 'linked', 'footnote_text_pending': False,
        'relation_candidate': True,
        'relation_candidate_note': 'S2 citation candidate: the printed footnote identifies the cited source and locator; the cited work was not independently consulted, and no S6 edge is created.',
    })
    q.pop('page', None)
    q.pop('source_citation', None)
    if not spec.get('keep_ocr_correction'):
        q.pop('ocr_corrections', None)
    context_id = source_row.get('subject_candidate_id')
    q['mentioned_candidate_ids'] = [x for x in (context_id, publication_id) if x]
    row['qualifiers'] = q
    return row


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
    for specs in SPLIT_CITATIONS.values():
        for spec in specs:
            if candidates.get(spec['publication_id'], {}).get('suggested_type') != 'archive':
                raise SystemExit(f'publication candidate missing or mistyped: {spec["publication_id"]}')

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {r['statement_id']: r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_ids = set(FALSE_NOTES) | set(OPEN_ENDPOINT_NOTES) | set(NOTE_CLAIMS) | set(SPLIT_CITATIONS) | TRUE_IDS
    actual_unset = {
        r['statement_id'] for r in rows
        if r['statement_id'].startswith(('st-chp7-p193-', 'st-chp7-p194-'))
        and (r.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if actual_unset != expected_ids:
        raise SystemExit(f'p.193–194 unset set differs: {sorted(actual_unset ^ expected_ids)}')
    for old_id in SPLIT_CITATIONS:
        for spec in SPLIT_CITATIONS[old_id]:
            if spec['statement_id'] in by_id:
                raise SystemExit(f'new citation statement ID already exists: {spec["statement_id"]}')
            old = by_id[old_id]
            q = old.get('qualifiers') or {}
            if (old.get('predicate') != 'footnote_citation' or q.get('relation_candidate') is not None
                    or q.get('source_line_start') != spec['line'] or q.get('footnote_marker') != spec['marker']
                    or spec['body_ids'] != q.get('linked_body_statement_ids')):
                raise SystemExit(f'compound citation row changed since review: {old_id}')
            for body_id in spec['body_ids']:
                if body_id not in by_id:
                    raise SystemExit(f'citation body statement missing: {body_id}')
    for note_id, spec in NOTE_CLAIMS.items():
        r = by_id[note_id]
        if ((r.get('qualifiers') or {}).get('relation_candidate') is not None
                or r['segment_id'] != spec['segment'] or (r.get('qualifiers') or {}).get('source_line_start') != spec['line']
                or (r.get('qualifiers') or {}).get('linked_body_statement_ids') != spec['body_ids']):
            raise SystemExit(f'p.193 footnote claim changed since review: {note_id}')
    for note_id in FALSE_NOTES | OPEN_ENDPOINT_NOTES:
        if note_id in NOTE_CLAIMS or note_id in SPLIT_CITATIONS:
            continue
        if (by_id[note_id].get('qualifiers') or {}).get('relation_candidate') is not None:
            raise SystemExit(f'statement changed since review: {note_id}')

    output = []
    for src in rows:
        sid = src['statement_id']
        if sid in SPLIT_CITATIONS:
            for spec in SPLIT_CITATIONS[sid]:
                output.append(make_citation_row(src, spec, candidates))
            continue
        row = dict(src)
        q = dict(row.get('qualifiers') or {})
        if sid in NOTE_CLAIMS:
            spec = NOTE_CLAIMS[sid]
            q.update({
                'footnote_number': spec['marker'], 'footnote_segment': spec['segment'],
                'footnote_refs': [{'marker': spec['marker'], 'segment_id': spec['segment'], 'source_line': spec['line'], 'statement_ids': spec['body_ids']}],
                'related_body_statement_ids': spec['body_ids'], 'linked_body_statement_ids': spec['body_ids'],
                'footnote_link_status': 'linked', 'footnote_body_link_status': 'linked', 'footnote_text_pending': False,
                'relation_candidate': True, 'relation_candidate_note': spec['note'],
            })
            row['qualifiers'] = q
        elif sid in FALSE_NOTES:
            q['relation_candidate'] = False
            q['relation_candidate_note'] = FALSE_NOTES[sid]
            row['qualifiers'] = q
        elif sid in OPEN_ENDPOINT_NOTES:
            q['relation_candidate'] = True
            q['relation_candidate_note'] = 'This preserves Haskell’s source-defined relation as an S2 candidate; its scope and uncertainty remain in the qualifiers. No S6 edge is created.'
            q['open_endpoint_reason'] = OPEN_ENDPOINT_NOTES[sid]
            row['qualifiers'] = q
        elif sid in expected_ids:
            q['relation_candidate'] = True
            q['relation_candidate_note'] = 'This preserves Haskell’s stated relation as an S2 candidate, with the claim and its limits retained in the qualifiers. No S6 edge is created.'
            row['qualifiers'] = q
        output.append(row)

    # Apply body-side backlinks after all rows have been materialized.
    by_output = {r['statement_id']: r for r in output}
    for note_id, spec in NOTE_CLAIMS.items():
        for body_id in spec['body_ids']:
            body = by_output[body_id]
            bq = dict(body.get('qualifiers') or {})
            append_unique(bq.setdefault('footnote_statement_ids', []), note_id)
            append_unique(bq.setdefault('footnote_refs', []), {'marker': spec['marker'], 'segment_id': spec['segment'], 'source_line': spec['line']})
            bq['footnote_segment'] = spec['segment']
            bq['footnote_body_link_status'] = 'linked'
            bq['footnote_text_pending'] = False
            body['qualifiers'] = bq
    for old_id, specs in SPLIT_CITATIONS.items():
        for spec in specs:
            for body_id in spec['body_ids']:
                body = by_output[body_id]
                bq = dict(body.get('qualifiers') or {})
                ids = [x for x in bq.get('footnote_statement_ids', []) if x != old_id]
                append_unique(ids, spec['statement_id'])
                bq['footnote_statement_ids'] = ids
                append_unique(bq.setdefault('footnote_refs', []), {'marker': spec['marker'], 'segment_id': by_id[old_id]['segment_id'], 'source_line': spec['line']})
                bq['footnote_segment'] = by_id[old_id]['segment_id']
                bq['footnote_body_link_status'] = 'linked'
                bq['footnote_text_pending'] = False
                body['qualifiers'] = bq
    # Backlink body rows for the two citation replacements above were staged before `by_output` existed;
    # rebuild output from the final ID map to retain those mutations.
    output = [by_output[r['statement_id']] for r in output]

    post_ids = [r['statement_id'] for r in output]
    if len(post_ids) != len(set(post_ids)):
        raise SystemExit('post-state statement IDs are not unique')
    counts = {
        True: sum((r.get('qualifiers') or {}).get('relation_candidate') is True for r in output),
        False: sum((r.get('qualifiers') or {}).get('relation_candidate') is False for r in output),
        'unset': sum((r.get('qualifiers') or {}).get('relation_candidate') not in (True, False) for r in output),
    }
    if (len(output), counts) != (14189, {True: 8629, False: 3425, 'unset': 2135}):
        raise SystemExit(f'unexpected post-state: rows={len(output)}, counts={counts}')
    for old_id, specs in SPLIT_CITATIONS.items():
        for spec in specs:
            note = next(r for r in output if r['statement_id'] == spec['statement_id'])
            if note['predicate'] != 'cites' or (note.get('qualifiers') or {}).get('relation_candidate') is not True:
                raise SystemExit(f'normalized citation post-check failed: {spec["statement_id"]}')
            for body_id in spec['body_ids']:
                bq = next(r['qualifiers'] for r in output if r['statement_id'] == body_id)
                if spec['statement_id'] not in bq.get('footnote_statement_ids', []):
                    raise SystemExit(f'citation backlink missing: {body_id} <- {spec["statement_id"]}')
    out = ('\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in output) + '\n').encode('utf-8')
    report = {'mode': 'apply' if args.apply else 'dry_run', 'new_citation_statements': 4,
              'replaced_compound_citation_rows': len(SPLIT_CITATIONS), 'classified_false': len(FALSE_NOTES),
              'classified_true_existing_rows': len(actual_unset) - len(FALSE_NOTES),
              'body_side_citation_backlinks': sum(len(s) for s in SPLIT_CITATIONS.values()) + sum(len(s['body_ids']) for s in NOTE_CLAIMS.values()),
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
