import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l103-113'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
MENTIONS = TABLES / 'mentions.csv'
COVERAGE = TABLES / 's2-coverage.csv'
BACKUP_TAG = '.bak-s2-chp5-p140-20261013'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: 'd7a0ebe51d6581292f4782eecd0a5bf26beef8a25671b633b16cad8cb794fcef',
    CANDIDATES: '13b5cd81c0e9ac53050c60e17e9840b69b118a97378405c62adf1f5be563bd48',
    MENTIONS: '2742b73196ef3fe0fb88575851b676958d13a8108ac5f78d257938a9d6cdcd9d',
    COVERAGE: '810b9ac4901bf34c9b5e7a5bdfa22b7d0253038d45f2d647f2d930a9b17ec606',
}

TARGET_IDS = {
    'st-chp5-p140-aristocratic-patronage-obstacle',
    'st-chp5-p140-arrival-fantastic-setting',
    'st-chp5-p140-arrival-figures-and-peasants',
    'st-chp5-p140-bamboccianti-inferior-position',
    'st-chp5-p140-bath-allusion-stufe-or-east',
    'st-chp5-p140-bath-scene-figures',
    'st-chp5-p140-cerquozzi-history-painter',
    'st-chp5-p140-chigi-habits-reported',
    'st-chp5-p140-chigi-patron-continuation',
    'st-chp5-p140-democratization-and-public',
    'st-chp5-p140-miel-career-tension',
    'st-chp5-p140-moved-from-inspiration',
    'st-chp5-p140-new-rich-marriage',
    'st-chp5-p140-old-families-description-partial',
    'st-chp5-p140-patrons-outside-theoretical-reach',
    'st-chp5-p140-subjects-not-seen-in-italy',
    'st-chp5-p140-theoretical-antagonism',
    'st-chp5-p140-two-chigi-works',
    'st-chp5-p140-womens-bath-plausibility',
}

RELATION_NOTE = (
    'S2 identifies a specific source-grounded relation candidate; qualifications '
    'are retained, and no formal S6 edge is created.'
)
NONRELATION_NOTE = (
    'This is a visual, scalar, contextual, or interpretive assertion rather than '
    'a specific entity relation.'
)

source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()
UNSET = object()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_quote(line_start, start_marker, end_marker, line_end=None):
    line_end = line_end or line_start
    text = '\n'.join(source_lines[line_start - 1:line_end])
    start = text.find(start_marker)
    end = text.find(end_marker, start + len(start_marker))
    if start < 0 or end < 0:
        raise ValueError(
            f'quote markers not found in source L{line_start}-L{line_end}: '
            f'{start_marker!r} ... {end_marker!r}'
        )
    return text[start:end + len(end_marker)]


def classify(row, is_relation):
    q = row.setdefault('qualifiers', {})
    q['relation_candidate'] = is_relation
    q['relation_candidate_note'] = RELATION_NOTE if is_relation else NONRELATION_NOTE


def revise(by_id, sid, *, subject=UNSET, object_=UNSET, predicate=None,
           line_start=None, line_end=None, quote=None, claim=None,
           mentioned=None, qualification=None, relation=None,
           remove_qualifiers=None):
    row = by_id[sid]
    q = row.setdefault('qualifiers', {})
    if subject is not UNSET:
        row['subject_candidate_id'] = subject
    if object_ is not UNSET:
        row['object_candidate_id'] = object_
    if predicate is not None:
        row['predicate'] = predicate
    if line_start is not None:
        q['source_line_start'] = line_start
    if line_end is not None:
        q['source_line_end'] = line_end
    if quote is not None:
        if quote not in '\n'.join(source_lines[q['source_line_start'] - 1:q['source_line_end']]):
            raise ValueError(f'quote absent from source for {sid}: {quote!r}')
        row['original_quote'] = quote
    if claim is not None:
        q['claim'] = claim
    if mentioned is not None:
        q['mentioned_candidate_ids'] = mentioned
    if qualification is not None:
        q['qualification'] = qualification
    if remove_qualifiers:
        for key in remove_qualifiers:
            q.pop(key, None)
    if relation is not None:
        classify(row, relation)
    return row


def make_statement(suffix, subject, object_, predicate, line_start, line_end,
                   quote, claim, mentioned, qualification, relation):
    if quote not in '\n'.join(source_lines[line_start - 1:line_end]):
        raise ValueError(f'quote absent from source L{line_start}-L{line_end}: {quote!r}')
    row = {
        'statement_id': f'st-chp5-p140-{suffix}',
        'segment_id': SEG,
        'subject_candidate_id': subject,
        'object_candidate_id': object_,
        'predicate': predicate,
        'qualifiers': {
            'source_line_start': line_start,
            'source_line_end': line_end,
            'printed_page': 140,
            'pdf_physical_page': 25,
            'claim': claim,
            'speaker': 'Haskell',
            'text_layer': 'authorial narration',
            'qualification': qualification,
            'mentioned_candidate_ids': mentioned,
        },
        'original_quote': quote,
        'origin': 'book',
        'source_file': '02-sources/02-Markdown/05_CHP-5_sec_iii.md',
    }
    classify(row, relation)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after guarded preview checks pass')
    args = parser.parse_args()

    for path, expected in EXPECTED_SHA256.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f'precondition failed: {path.relative_to(ROOT)} sha256={actual}')

    statements = [json.loads(x) for x in STATEMENTS.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
    ids = [r['statement_id'] for r in statements]
    if len(ids) != len(set(ids)):
        raise SystemExit('duplicate statement IDs in input')
    by_id = {r['statement_id']: r for r in statements}
    if not (TARGET_IDS <= set(by_id)):
        raise SystemExit(f'missing p.140 targets: {sorted(TARGET_IDS - set(by_id))}')
    if any(by_id[sid].get('segment_id') != SEG for sid in TARGET_IDS):
        raise SystemExit('p.140 target segment mismatch')
    if any(by_id[sid].get('qualifiers', {}).get('relation_candidate') is not None for sid in TARGET_IDS):
        raise SystemExit('a p.140 target was already classified; refusing to overwrite')

    coverage = next((r for r in __import__('csv').DictReader(COVERAGE.open(encoding='utf-8-sig', newline='')) if r.get('segment_id') == SEG), None)
    if not coverage or coverage.get('disposition') != 'reviewed' or coverage.get('migration_status') != 'complete':
        raise SystemExit('p.140 coverage precondition failed')

    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        import csv
        candidate_ids = {r['candidate_id'] for r in csv.DictReader(f)}
    if not {'cand-0794', 'cand-6168', 'cand-0671', 'cand-4490', 'cand-1662', 'cand-6175', 'cand-6179', 'cand-6176', 'cand-6178'} <= candidate_ids:
        raise SystemExit('required candidate endpoint missing')

    # Link Codazzi's imagined architecture to the named work and keep absence of a real site separate.
    revise(
        by_id, 'st-chp5-p140-arrival-fantastic-setting',
        subject='cand-0794', object_='cand-6168',
        predicate='envisaged_fantastic_architectural_setting_for',
        line_start=105, line_end=107,
        quote=source_quote(105, 'Codazzi envisaged as the setting', 'The Arrival at the\nPalace', 107),
        claim='Haskell says Codazzi envisaged the vast, fantastic structure as the setting for the princely family in The Arrival at the Palace.',
        mentioned=['cand-0794', 'cand-6168', 'cand-3084'],
        qualification='The structure is imagined pictorial content, not an identified real villa or palace; this claim does not say Codazzi painted the work.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p140-arrival-figures-and-peasants',
        predicate='princely_family_retinue_acute_against_grandeur',
        line_start=107, line_end=107,
        quote=source_quote(107, 'these figures, with coach and horses, retinue and dogs', 'acutely realised'),
        claim='Haskell says the princely family, coach, horses, retinue and dogs are acutely realised in The Arrival at the Palace.',
        mentioned=['cand-6168', 'cand-3084'],
        qualification='This is Haskell’s visual assessment; the family and attendants are not identified as historical individuals.',
        relation=False,
    )

    # Separate Chigi's reported habits from the bath picture's visual content and allusions.
    revise(
        by_id, 'st-chp5-p140-bath-allusion-stufe-or-east',
        line_start=108, line_end=108,
        quote=source_quote(108, 'events described must surely refer obliquely', 'notorious stufe of Renaissance Rome'),
        claim='Haskell says the Women’s Bath events must surely refer obliquely to the notorious stufe of Renaissance Rome.',
        mentioned=['cand-4061', 'cand-6169', 'cand-4490'],
        qualification='Retain “must surely”; no particular bathhouse is identified. This is an interpretation of the pictured events.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p140-bath-scene-figures',
        line_start=108, line_end=108,
        quote=source_quote(108, 'A turbaned Oriental wistfully surveys the scene', 'while elegant young dandies'),
        claim='Haskell describes a turbaned Oriental figure wistfully surveying the Women’s Bath scene.',
        mentioned=['cand-4061'],
        qualification='The figure is described as pictorial content; no real person or specific region is identified.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p140-theoretical-antagonism',
        predicate='theoretical_antagonism_to_realistic_painting',
        line_start=110, line_end=111,
        quote=source_quote(110, 'there was also the antagonism to such painting', 'on theoretical grounds'),
        claim='Haskell says there was theoretical antagonism to this kind of painting.',
        mentioned=['cand-6173', 'cand-6172'],
        qualification='The antagonism is a broad intellectual condition; its advocates are not identified as a group or institution.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p140-bamboccianti-inferior-position',
        line_start=112, line_end=112,
        quote=source_quote(112, 'But it did serve to keep the bamboccianti', 'inferior position'),
        claim='Haskell says theoretical objections helped keep the Bamboccianti in an inferior position.',
        mentioned=['cand-0173', 'cand-6173'],
        qualification='This is Haskell’s group-level account of their social standing.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p140-miel-career-tension',
        predicate='veered_toward_history_painting',
        line_start=112, line_end=112,
        quote=source_quote(112, 'the more acceptable branch of', 'far less suited to his talents.'),
        claim='Haskell says Jan Miel veered toward the more socially acceptable branch of history painting, which was far less suited to his talents.',
        mentioned=['cand-1662', 'cand-6179'],
        qualification='This is a tendency in Haskell’s account, not a claim that Miel adopted history painting exclusively or in a dated career phase.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p140-old-families-description-partial',
        predicate='old_patrician_families_described_as_powerless_and_bankrupt',
        claim='Haskell describes Rome’s old patrician families as bereft of power and bankrupt.',
        qualification='The phrase begun at p.140 L113 closes at p.141 L116 with “power and bankrupt”; this remains Haskell’s broad social characterization.',
        relation=False,
    )

    # Classify the remaining claims while retaining their source qualifications.
    classifications = {
        'st-chp5-p140-aristocratic-patronage-obstacle': False,
        'st-chp5-p140-cerquozzi-history-painter': True,
        'st-chp5-p140-chigi-habits-reported': False,
        'st-chp5-p140-chigi-patron-continuation': True,
        'st-chp5-p140-democratization-and-public': False,
        'st-chp5-p140-moved-from-inspiration': False,
        'st-chp5-p140-new-rich-marriage': True,
        'st-chp5-p140-patrons-outside-theoretical-reach': False,
        'st-chp5-p140-subjects-not-seen-in-italy': False,
        'st-chp5-p140-two-chigi-works': True,
        'st-chp5-p140-womens-bath-plausibility': False,
    }
    for sid, is_relation in classifications.items():
        classify(by_id[sid], is_relation)

    revise(
        by_id, 'st-chp5-p140-chigi-patron-continuation',
        qualification='Completes the p.139 L100 phrase. This records Chigi’s role as a patron in Rome; “most influential” remains Haskell’s characterization.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p140-two-chigi-works',
        predicate='two_cerquozzi_works_associated_with_chigi',
        qualification='Retain Haskell’s “painted for him” wording as a relation candidate. Footnote 1 at L154 says commission cannot be conclusively proved, while contemporary sources and inventories indicate ownership; a prior Colonna commission is described as possible but unlikely.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p140-moved-from-inspiration',
        qualification='This is Haskell’s interpretive assessment of Cerquozzi’s development, not a discrete event or formal relation.',
        relation=False,
    )

    new_statements = [
        make_statement(
            'arrival-no-real-villa', 'cand-6168', None,
            'imagined_structure_matches_no_actual_villa_or_palace', 105, 105,
            source_quote(105, 'Indeed no actual villa or palace', 'fantastic structure'),
            'Haskell says no actual villa or palace corresponded to the vast structure imagined for The Arrival at the Palace.',
            ['cand-6168'],
            'The pictured structure is fantastic and is not identified with any real architectural site.',
            False,
        ),
        make_statement(
            'arrival-peasants', 'cand-6168', None,
            'peasants_selling_watermelons_or_lounging_rendered_acutely', 107, 107,
            source_quote(107, 'as, still more, are the peasants', 'general grandeur.'),
            'Haskell says the peasants selling water melons or lounging on the ground are even more acutely realised and remain unperturbed by the grandeur.',
            ['cand-6168'],
            'This is Haskell’s visual description; the peasants are not identified as historical individuals.',
            False,
        ),
        make_statement(
            'bath-east-traveller-tales', 'cand-4061', None,
            'may_evokes_travellers_tales_from_east', 108, 108,
            source_quote(108, 'or perhaps evoke some traveller', 'East.'),
            'Haskell suggests that the Women’s Bath may evoke travellers’ tales from the East.',
            ['cand-4061', 'cand-6170'],
            'Retain “perhaps”; neither a particular journey nor travel text is identified.',
            False,
        ),
        make_statement(
            'bath-young-dandies', 'cand-4061', None,
            'young_dandies_prepare_to_use_scene_opportunities', 108, 108,
            source_quote(108, 'while elegant young dandies', 'await them.'),
            'Haskell describes elegant young dandies as preparing to make use of the opportunities in the Women’s Bath scene.',
            ['cand-4061'],
            'The dandies are pictorial figures, not identified individuals.',
            False,
        ),
        make_statement(
            'artists-tempted-to-leave-inferior-position', 'cand-0173', None,
            'artists_tempted_to_leave_inferior_position_after_success', 112, 112,
            source_quote(112, 'from which they were always tempted', 'once they had achieved any success.'),
            'Haskell says Bamboccianti artists were tempted to leave their inferior position after achieving success.',
            ['cand-0173'],
            'This is a general claim about the group; no individual artist or career change is identified.',
            False,
        ),
        make_statement(
            'theoretical-opposition-chronology', 'cand-6173', None,
            'opposition_preceded_van_laer_and_later_widely_held', 110, 111,
            source_quote(110, 'in some circles even before the arrival of Van Laer', 'widely held dogma.', 111),
            'Haskell says opposition existed in some circles before Van Laer arrived and later became a widely held dogma.',
            ['cand-6173', 'cand-1351'],
            'Retain Haskell’s limited initial scope (“in some circles”) and broad chronology.',
            False,
        ),
        make_statement(
            'miel-bambocciante-manner', 'cand-1662', 'cand-6175',
            'veered_between_styles_including_bambocciante_manner', 112, 112,
            source_quote(112, 'Jan Miel also found himself veering between', 'to which he aspired'),
            'Haskell says Jan Miel veered toward a profitable bambocciante manner that earned him discredit in the social circles to which he aspired.',
            ['cand-1662', 'cand-6175'],
            'This is a career tendency in Haskell’s account; do not treat the manner as exclusive or date a period of use.',
            True,
        ),
    ]

    new_ids = {r['statement_id'] for r in new_statements}
    if len(new_ids) != len(new_statements) or set(ids) & new_ids:
        raise SystemExit('statement ID collision')
    available_candidates = candidate_ids
    check_rows = [by_id[sid] for sid in TARGET_IDS] + new_statements
    for row in check_rows:
        q = row.get('qualifiers', {})
        for cid in q.get('mentioned_candidate_ids', []) or []:
            if cid and cid not in available_candidates:
                raise SystemExit(f'missing mentioned candidate {cid} in {row["statement_id"]}')
        if q.get('relation_candidate') is True:
            if not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
                raise SystemExit(f'relation candidate missing endpoint: {row["statement_id"]}')
            if row['subject_candidate_id'] not in available_candidates or row['object_candidate_id'] not in available_candidates:
                raise SystemExit(f'relation candidate endpoint not found: {row["statement_id"]}')
    for row in new_statements:
        q = row['qualifiers']
        if row['original_quote'] not in '\n'.join(source_lines[q['source_line_start'] - 1:q['source_line_end']]):
            raise SystemExit(f'quote/source-line check failed: {row["statement_id"]}')

    target_rows = [by_id[sid] for sid in TARGET_IDS]
    p140_rows = target_rows + new_statements
    relation_count = sum(r['qualifiers']['relation_candidate'] is True for r in p140_rows)
    nonrelation_count = sum(r['qualifiers']['relation_candidate'] is False for r in p140_rows)
    if relation_count + nonrelation_count != len(p140_rows):
        raise SystemExit('p.140 classification count mismatch')

    if args.apply:
        backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_TAG)
        if backup.exists():
            raise SystemExit('backup already exists; refusing to overwrite')
        shutil.copy2(STATEMENTS, backup)
        statements.extend(new_statements)
        temp = STATEMENTS.with_name(STATEMENTS.name + '.tmp-s2-chp5-p140')
        if temp.exists():
            raise SystemExit('temporary output exists; refusing to overwrite')
        try:
            with temp.open('w', encoding='utf-8-sig', newline='') as f:
                for row in statements:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
            os.replace(temp, STATEMENTS)
        finally:
            if temp.exists():
                temp.unlink()
        print('applied guarded p.140 S2 claim atomization and classification')
        print('backup:', backup.name)
    else:
        print('PREVIEW only; no table writes')

    print(f'p.140 existing statements classified: {len(TARGET_IDS)}')
    print(f'p.140 added atomic statements: {len(new_statements)}')
    print(f'p.140 relation candidates: {relation_count}; non-relational claims: {nonrelation_count}')
    for row in sorted(p140_rows, key=lambda r: r['statement_id']):
        q = row.get('qualifiers', {})
        print(f"  {str(q['relation_candidate']).lower()} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']} | {q.get('claim', '')}")


if __name__ == '__main__':
    main()
