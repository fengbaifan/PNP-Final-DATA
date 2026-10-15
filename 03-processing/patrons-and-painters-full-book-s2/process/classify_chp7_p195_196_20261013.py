from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / '04-knowledge' / 'tables' / 'book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge' / 'tables' / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '07_CHP-7_sec_iv.md'
PDF = ROOT / '02-sources' / '01-book' / 'CHP-7.pdf'
SOURCE_BOOK_ID = 'cand-2962'
P195_BODY = 'chp-7:07_CHP-7_sec_iv:l38-46'
P196_BODY = 'chp-7:07_CHP-7_sec_iv:l48-61'
NOTES = 'chp-7:07_CHP-7_sec_iv:l97-119'
WIND_NOTE_ID = 'st-chp7-p196-footnote2-wind'
WIND_BODY_ID = 'st-chp7-p196-hampton_fresco_subject'
P195_NOTE_ID = 'st-chp7-p195-n1-prince-taste-comment'
P195_BODY_ID = 'st-chp7-p195-liechtenstein-gallery-worldly'

EXPECTED_HASHES = {
    STATEMENTS.name: '8bd2f5d2a3f29c6dfd4b0a331273f221e6c89049d4503191b4ae962f073332ad',
    CANDIDATES.name: '9ae98db4017b0e7bf61331c07b286792458b2eadbe09c2bd2903a6593d74275d',
    SOURCE.name: 'd620659a2f3567ea9a1d91b7657390e9824768c320c3cf534bd30069d6c72077',
    PDF.name: 'eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212',
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + '.bak-s2-chp7-p195-196-20261013')

TRUE_IDS = {
    'st-chp7-p195-arlington-introduced-verrio',
    'st-chp7-p195-cagnacci-cleopatra-lucretia-output',
    'st-chp7-p195-cagnacci-from-romagna-to-venice',
    'st-chp7-p195-cagnacci-summoned-vienna',
    'st-chp7-p195-charlesii-motive',
    'st-chp7-p195-charlesii-no-contemporary-italian-interest',
    'st-chp7-p195-charlesii-recovers-pictures',
    'st-chp7-p195-cignani-testimony',
    'st-chp7-p195-england-impact-comparison',
    'st-chp7-p195-english-patronage-next-century',
    'st-chp7-p195-female-nude-historical-role',
    'st-chp7-p195-german-patron-generalization',
    'st-chp7-p195-lazzarini-output-germany',
    'st-chp7-p195-lazzarini-testimony',
    'st-chp7-p195-liechtenstein-gallery-worldly',
    'st-chp7-p195-lothar-schonborn-letter',
    P195_NOTE_ID,
    'st-chp7-p195-plate28a-cagnacci-work',
    'st-chp7-p195-price-of-german-orders',
    'st-chp7-p195-verrio-lebrun-versailles',
    'st-chp7-p195-verrio-origin-and-self-description',
    WIND_NOTE_ID,
    'st-chp7-p196-gennari-arrival_and_kinship',
    'st-chp7-p196-gennari-mythological_pictures',
    'st-chp7-p196-gennari-paris_success',
    'st-chp7-p196-gennari_ancient_guise_practice',
    'st-chp7-p196-gennari_departure_1688',
    'st-chp7-p196-gennari_new_style',
    'st-chp7-p196-gennari_salary_and_commissions',
    'st-chp7-p196-gennari_subject_shift',
    'st-chp7-p196-jamesii-demand_for_italian_artists',
    'st-chp7-p196-verrio-brings-baroque-decoration',
    'st-chp7-p196-verrio-illusionistic-effects',
    'st-chp7-p196-verrio-style_evaluation',
    'st-chp7-p196-verrio_conflicting_programmes',
    'st-chp7-p196-verrio_leaves_court',
    'st-chp7-p196-verrio_pension_open',
    'st-chp7-p196-verrio_shaftesbury_roles',
    'st-chp7-p196-whitehall_programme',
    'st-chp7-p196-windsor-frescoes-absolutism',
}

FALSE_NOTES = {
    'st-chp7-p196-windsor-charles-rubens-comparison': (
        'The sentence uses an analogy between the Windsor frescoes and Charles I’s claims, '
        'then between Verrio’s art and Rubens; it does not assert direct historical relations '
        'between those pairs. Preserve it as Haskell’s comparative source claim.'
    ),
}

OPEN_ENDPOINT_NOTES = {
    'st-chp7-p195-cagnacci-cleopatra-lucretia-output': 'The paintings are described as a collective output; no individual Cleopatra or Lucretia work is identified.',
    'st-chp7-p195-charlesii-no-contemporary-italian-interest': 'This is Haskell’s broad negative characterization; no particular encounter, artist, or work is identified.',
    'st-chp7-p195-cignani-testimony': 'The testimony is reported second-hand and the youthful paintings are unnamed; preserve the attribution and cited-source boundary.',
    'st-chp7-p195-england-impact-comparison': 'This is a macro-level comparison of English impact and German/Austrian commissions before 1700; no individual patron, commission, or work is specified.',
    'st-chp7-p195-english-patronage-next-century': 'The “next century” is relative to the narrative period; no individual English patron or commission is identified in this framing statement.',
    'st-chp7-p195-female-nude-historical-role': 'The claim is Haskell’s broad causal interpretation of German patronage; no individual patron or painting is identified.',
    'st-chp7-p195-german-patron-generalization': 'The other patrons are unnamed and their agreement is Haskell’s inference from one letter, not individually attested testimony.',
    'st-chp7-p195-lazzarini-testimony': 'The testimony is reported indirectly; the “best amateurs” and the paintings are not individually identified.',
    'st-chp7-p195-liechtenstein-gallery-worldly': 'The Prince is identified only by title, and neither the gallery nor the pictures are individually identified; do not resolve the title to an indexed person here.',
    'st-chp7-p195-lothar-schonborn-letter': 'The letter expresses a preference and view of Strudel’s strengths; it does not establish that the suggested subjects were commissioned or painted.',
    'st-chp7-p195-price-of-german-orders': '“A small price to pay” is Haskell’s metaphorical account of subject demands and continuing German commissions, not evidence of a literal transaction or named commission.',
    'st-chp7-p196-gennari-mythological_pictures': 'The surviving mythological paintings are not individually identified in this passage.',
    'st-chp7-p196-gennari_ancient_guise_practice': 'The sitters and paintings are unnamed; retain this as Haskell’s claim about Gennari’s practice and its contemporary French context.',
    'st-chp7-p196-gennari_new_style': 'The reported style concerns royal sitters collectively; no specific portrait or commission is identified here.',
    'st-chp7-p196-gennari_salary_and_commissions': 'The Queen and other patrons are unnamed, and the currency for the annual salary is not specified in the passage.',
    'st-chp7-p196-jamesii-demand_for_italian_artists': 'This is a short-lived group-level causal claim; no individual commission or artist beyond the preceding group is assigned.',
    'st-chp7-p196-verrio-illusionistic-effects': 'The ceilings and walls are described as features of the decorative mode; no individual room or building is specified in this sentence.',
    'st-chp7-p196-verrio-style_evaluation': '“The work” refers to Verrio’s decorative production collectively; no single work is identified for the stylistic evaluation.',
    'st-chp7-p196-verrio_conflicting_programmes': 'The Catholic and anti-Catholic programmes are characterized collectively; the sentence does not identify each programme as a separate work.',
    'st-chp7-p196-verrio_leaves_court': 'The country houses and individual commissions are unnamed; the passage records only a period of work after Verrio left court.',
    'st-chp7-p196-windsor-frescoes-absolutism': 'The frescoes are treated as a series; individual paintings and their exact intended viewers are not specified.',
}

WIND_SOURCE_GUARD = 'a Wind, 1939-40, pp. 127-37.'
P195_NOTE_GUARD = '1 ibid., pp. 89 and 92.'


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


def add_note_link(note_row: dict, body_row: dict, *, marker: int, source_line: int,
                  body_id: str, note_segment: str) -> None:
    nq = dict(note_row.get('qualifiers') or {})
    bq = dict(body_row.get('qualifiers') or {})
    ref = {'marker': marker, 'segment_id': note_segment, 'source_line': source_line,
           'statement_ids': [body_id]}
    nq.update({
        'footnote_number': marker,
        'footnote_segment': note_segment,
        'footnote_refs': [ref],
        'related_body_statement_ids': [body_id],
        'linked_body_statement_ids': [body_id],
        'footnote_link_status': 'linked',
        'footnote_body_link_status': 'linked',
        'footnote_text_pending': False,
    })
    bref = {'marker': marker, 'segment_id': body_row['segment_id'], 'source_line': source_line}
    # The body reference points to the note segment, not its own body segment.
    bref['segment_id'] = note_segment
    refs = list(bq.get('footnote_refs') or [])
    if bref not in refs:
        refs.append(bref)
    ids = list(bq.get('footnote_statement_ids') or [])
    append_unique(ids, note_row['statement_id'])
    bq.update({
        'footnote_refs': refs,
        'footnote_statement_ids': ids,
        'footnote_body_link_status': 'linked',
    })
    note_row['qualifiers'] = nq
    body_row['qualifiers'] = bq


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    raw = {p: p.read_bytes() for p in (STATEMENTS, CANDIDATES, SOURCE, PDF)}
    hashes = {p.name: sha256(data) for p, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f'input hashes changed: {hashes}')

    source_lines = raw[SOURCE].decode('utf-8-sig').splitlines()
    if WIND_SOURCE_GUARD not in source_lines[60] or P195_NOTE_GUARD not in source_lines[102]:
        raise SystemExit('footnote source guard failed')
    candidates = {
        row['candidate_id']: row
        for row in csv.DictReader(io.StringIO(raw[CANDIDATES].decode('utf-8-sig'), newline=''))
    }
    for candidate_id, expected_type in ((SOURCE_BOOK_ID, 'archive'), ('cand-7229', 'person'), ('cand-7230', 'archive')):
        if candidates.get(candidate_id, {}).get('suggested_type') != expected_type:
            raise SystemExit(f'citation candidate missing or mistyped: {candidate_id}')

    rows = [json.loads(line) for line in raw[STATEMENTS].decode('utf-8-sig').splitlines() if line.strip()]
    by_id = {row['statement_id']: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit('statement IDs are not unique')
    expected_ids = TRUE_IDS | set(FALSE_NOTES)
    actual_unset = {
        row['statement_id'] for row in rows
        if row['statement_id'].startswith(('st-chp7-p195-', 'st-chp7-p196-'))
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
    }
    if actual_unset != expected_ids:
        raise SystemExit(f'p.195–196 unset set differs: {sorted(actual_unset ^ expected_ids)}')

    note = by_id[P195_NOTE_ID]
    body = by_id[P195_BODY_ID]
    if (note['segment_id'] != NOTES or body['segment_id'] != P195_BODY
            or note['qualifiers'].get('source_line_start') != 103
            or note['qualifiers'].get('footnote_marker') != 1
            or note['qualifiers'].get('linked_body_statement_ids') != [P195_BODY_ID]
            or body['qualifiers'].get('footnote_marker') != 1):
        raise SystemExit('p.195 note 1 linkage changed since review')

    wind = by_id[WIND_NOTE_ID]
    wind_body = by_id[WIND_BODY_ID]
    wq = wind.get('qualifiers') or {}
    if (wind['segment_id'] != P196_BODY or wind['predicate'] != 'footnote_citation'
            or wind.get('subject_candidate_id') is not None
            or wind.get('object_candidate_id') != 'cand-7230'
            or wq.get('source_line_start') != 61 or wq.get('footnote_marker') != 2
            or wq.get('linked_body_statement_ids') != [WIND_BODY_ID]
            or wind_body.get('qualifiers', {}).get('footnote_marker') != 2):
        raise SystemExit('p.196 note 2 citation or body link changed since review')

    output = []
    for source_row in rows:
        sid = source_row['statement_id']
        row = dict(source_row)
        q = dict(row.get('qualifiers') or {})
        if sid in TRUE_IDS:
            q['relation_candidate'] = True
            q['relation_candidate_note'] = (
                'S2 preserves this source-grounded historical or authorial claim as a relation candidate; '
                'its attribution and limits remain attached, and no formal S6 edge is created.'
            )
            if sid in OPEN_ENDPOINT_NOTES:
                q['open_endpoint_reason'] = OPEN_ENDPOINT_NOTES[sid]
            row['qualifiers'] = q
        elif sid in FALSE_NOTES:
            q['relation_candidate'] = False
            q['relation_candidate_note'] = FALSE_NOTES[sid]
            row['qualifiers'] = q

        if sid == P195_NOTE_ID:
            add_note_link(row, by_id[P195_BODY_ID], marker=1, source_line=103,
                          body_id=P195_BODY_ID, note_segment=NOTES)
            row['qualifiers']['relation_candidate'] = True
            row['qualifiers']['relation_candidate_note'] = (
                'This records Haskell’s source-attributed interpretation of the Prince’s preference; '
                'it does not independently confirm the Prince’s intention or identify individual sacred works.'
            )
        elif sid == WIND_NOTE_ID:
            add_note_link(row, by_id[WIND_BODY_ID], marker=2, source_line=61,
                          body_id=WIND_BODY_ID, note_segment=P196_BODY)
            q = row['qualifiers']
            q.update({
                'citation_publication_candidate_id': 'cand-7230',
                'citation_locator': 'Wind, 1939–40, pp. 127–137',
                'citations': [{
                    'source_candidate_id': SOURCE_BOOK_ID,
                    'publication_candidate_id': 'cand-7230',
                    'locator': 'Wind, 1939–40, pp. 127–137',
                }],
                'cited_material_not_independently_consulted': True,
                'relation_candidate': True,
                'relation_candidate_note': (
                    'S2 citation candidate: Haskell’s printed footnote cites E. Wind’s study at the stated locator; '
                    'the cited work was not independently consulted, and no formal S6 edge is created.'
                ),
            })
            row['subject_candidate_id'] = SOURCE_BOOK_ID
            row['predicate'] = 'cites'
            row['object_candidate_id'] = 'cand-7230'
            mentioned = list(q.get('mentioned_candidate_ids') or [])
            for candidate_id in (SOURCE_BOOK_ID, 'cand-7229', 'cand-7230'):
                append_unique(mentioned, candidate_id)
            q['mentioned_candidate_ids'] = mentioned
            q.pop('page', None)
            q.pop('source_citation', None)
            row['qualifiers'] = q
        output.append(row)

    by_output = {row['statement_id']: row for row in output}
    for sid in (P195_BODY_ID, WIND_BODY_ID):
        target = by_output[sid]
        target_q = dict(target.get('qualifiers') or {})
        backlink_q = by_id[sid].get('qualifiers') or {}
        for key in ('footnote_refs', 'footnote_statement_ids', 'footnote_body_link_status'):
            if key in backlink_q:
                target_q[key] = backlink_q[key]
        target['qualifiers'] = target_q

    decisions = [row.get('qualifiers', {}).get('relation_candidate') for row in output]
    counts = {
        'statements': len(output),
        'True': sum(value is True for value in decisions),
        'False': sum(value is False for value in decisions),
        'unset': sum(value is None for value in decisions),
    }
    if counts != {'statements': 14189, 'True': 8669, 'False': 3426, 'unset': 2094}:
        raise SystemExit(f'unexpected post-counts: {counts}')
    for note_id, body_id in ((P195_NOTE_ID, P195_BODY_ID), (WIND_NOTE_ID, WIND_BODY_ID)):
        nq = by_output[note_id]['qualifiers']
        bq = by_output[body_id]['qualifiers']
        if body_id not in nq.get('linked_body_statement_ids', []) or note_id not in bq.get('footnote_statement_ids', []):
            raise SystemExit(f'footnote backlink validation failed: {note_id}')
    if (by_output[WIND_NOTE_ID]['predicate'] != 'cites'
            or by_output[WIND_NOTE_ID]['subject_candidate_id'] != SOURCE_BOOK_ID
            or by_output[WIND_NOTE_ID]['object_candidate_id'] != 'cand-7230'):
        raise SystemExit('Wind citation normalization failed')

    encoded = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    backup_label = str(BACKUP.relative_to(ROOT))
    after_hash = sha256(encoded)
    report = {
        'mode': 'apply' if args.apply else 'dry_run',
        'classified_true': len(TRUE_IDS),
        'classified_false': len(FALSE_NOTES),
        'citation_rows_normalized': 1,
        'body_side_footnote_backlinks': 2,
        'post_counts': counts,
        'before_sha256': hashes,
        'after_statement_sha256': after_hash,
        'backup': backup_label,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print('dry-run only; no files changed')
        return
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    BACKUP.write_bytes(raw[STATEMENTS])
    atomic_write(STATEMENTS, encoded)
    if sha256(STATEMENTS.read_bytes()) != after_hash:
        raise SystemExit('post-write statement hash mismatch')
    print('applied; recovery copy written; statement hash verified')


if __name__ == '__main__':
    main()
