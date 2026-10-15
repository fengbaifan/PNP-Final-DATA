import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l115-121'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
MENTIONS = TABLES / 'mentions.csv'
COVERAGE = TABLES / 's2-coverage.csv'
BACKUP_TAG = '.bak-s2-chp5-p141-20261013'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: '53947382601a77d720f1981e48a3c87309df4aaac2601bbff7c49ccf67d54b6a',
    CANDIDATES: '13b5cd81c0e9ac53050c60e17e9840b69b118a97378405c62adf1f5be563bd48',
    MENTIONS: '2742b73196ef3fe0fb88575851b676958d13a8108ac5f78d257938a9d6cdcd9d',
    COVERAGE: '810b9ac4901bf34c9b5e7a5bdfa22b7d0253038d45f2d647f2d930a9b17ec606',
}

TARGET_IDS = {
    'st-chp5-p141-1651-sacchi-albani-letter-exchange',
    'st-chp5-p141-academy-admission-no-early-hostility',
    'st-chp5-p141-albani-response-described-as-abuse',
    'st-chp5-p141-aristocratic-taste-and-relations',
    'st-chp5-p141-artists-accused-bamboccianti',
    'st-chp5-p141-attacks-peaked-with-cerquozzi-triumphs',
    'st-chp5-p141-attacks-targeted-new-ruling-class',
    'st-chp5-p141-bamboccianti-preceded-1651-letter-by-quarter-century',
    'st-chp5-p141-correspondence-significance-unclear',
    'st-chp5-p141-crowd-versus-connoisseur',
    'st-chp5-p141-financial-depression-and-cheaper-prices',
    'st-chp5-p141-financial-questions-in-success-and-opposition',
    'st-chp5-p141-hatred-developed-late-with-patronage',
    'st-chp5-p141-leading-figures-charged-more-earlier',
    'st-chp5-p141-liberal-connoisseurship-and-cerquozzi-success',
    'st-chp5-p141-malvasia-may-have-doctored-letters',
    'st-chp5-p141-old-families-power-bankruptcy-continuation',
    'st-chp5-p141-public-versus-man-of-taste-distinction',
    'st-chp5-p141-reni-and-passeri-attribution',
    'st-chp5-p141-sacchi-asks-albani-opinion',
    'st-chp5-p141-six-or-eight-scudi-claim-absurd',
    'st-chp5-p141-snobbery-as-anti-bamboccianti-appeal',
}

RELATION_NOTE = (
    'S2 identifies a specific source-grounded relation candidate; qualifications '
    'are retained, and no formal S6 edge is created.'
)
NONRELATION_NOTE = (
    'This is a scalar, chronological, contextual, or interpretive assertion rather '
    'than a specific entity relation.'
)
UNSET = object()
SOURCE_LINES = SOURCE.read_text(encoding='utf-8-sig').splitlines()
SEGMENT_TEXT = '\n'.join(SOURCE_LINES[114:121])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quote(line_start, start, end, line_end=None):
    line_end = line_end or line_start
    text = '\n'.join(SOURCE_LINES[line_start - 1:line_end])
    left = text.find(start)
    right = text.find(end, left + len(start))
    if left < 0 or right < 0:
        raise ValueError(f'quote markers absent at L{line_start}-L{line_end}: {start!r} ... {end!r}')
    return text[left:right + len(end)]


def classify(row, is_relation):
    q = row.setdefault('qualifiers', {})
    q['relation_candidate'] = is_relation
    q['relation_candidate_note'] = RELATION_NOTE if is_relation else NONRELATION_NOTE


def revise(by_id, sid, *, subject=UNSET, object_=UNSET, predicate=None,
           line_start=None, line_end=None, original_quote=None, claim=None,
           mentioned=None, qualification=None, relation=None,
           extra_qualifiers=None):
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
    if original_quote is not None:
        if original_quote not in '\n'.join(SOURCE_LINES[q['source_line_start'] - 1:q['source_line_end']]):
            raise ValueError(f'quote absent from source for {sid}: {original_quote!r}')
        row['original_quote'] = original_quote
    if claim is not None:
        q['claim'] = claim
    if mentioned is not None:
        q['mentioned_candidate_ids'] = mentioned
    if qualification is not None:
        q['qualification'] = qualification
    if extra_qualifiers:
        q.update(extra_qualifiers)
    if relation is not None:
        classify(row, relation)
    return row


def make_statement(suffix, subject, object_, predicate, line_start, line_end,
                   original_quote, claim, mentioned, qualification, relation,
                   footnote_source=None):
    source_span = '\n'.join(SOURCE_LINES[line_start - 1:line_end])
    if original_quote not in source_span:
        raise ValueError(f'quote absent from source L{line_start}-L{line_end}: {original_quote!r}')
    row = {
        'statement_id': f'st-chp5-p141-{suffix}',
        'segment_id': SEG,
        'subject_candidate_id': subject,
        'object_candidate_id': object_,
        'predicate': predicate,
        'qualifiers': {
            'source_line_start': line_start,
            'source_line_end': line_end,
            'printed_page': 141,
            'pdf_physical_page': 26,
            'claim': claim,
            'speaker': 'Haskell',
            'text_layer': 'authorial narration',
            'qualification': qualification,
            'mentioned_candidate_ids': mentioned,
        },
        'original_quote': original_quote,
        'source_file': '02-sources/02-Markdown/05_CHP-5_sec_iii.md',
        'origin': 'book',
    }
    classify(row, relation)
    if footnote_source:
        source_q = footnote_source['qualifiers']
        for key in ('footnote_target_line', 'footnote_link_status', 'citation_segment_id',
                    'citation_source_line_start', 'citation_source_line_end', 'footnote_refs'):
            if key in source_q:
                row['qualifiers'][key] = json.loads(json.dumps(source_q[key], ensure_ascii=False))
    return row


def csv_text(rows, fieldnames):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction='raise', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def make_candidate(cid, name, suggested_type, detail, source_line):
    return {
        'candidate_id': cid,
        'index_entry_id': '',
        'canonical_name': name,
        'index_page_range': '',
        'suggested_type': suggested_type,
        'status': 'open',
        'index_source_file': '',
        'sub_entry': '',
        'detail': detail,
        'exclude_reason': '',
        'candidate_origin': 'body-mention',
        'candidate_source_ref': f'{SEG}#L{source_line}',
    }


def mention(mention_id, candidate_id, surface, note):
    start = SEGMENT_TEXT.find(surface)
    if start < 0 or SEGMENT_TEXT.find(surface, start + len(surface)) >= 0:
        raise ValueError(f'mention surface is absent or ambiguous: {surface!r}')
    return {
        'mention_id': mention_id,
        'segment_id': SEG,
        'candidate_id': candidate_id,
        'surface_form': surface,
        'start_char': str(start),
        'end_char': str(start + len(surface)),
        'note': note,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write only after guarded checks pass')
    args = parser.parse_args()

    for path, expected in EXPECTED_SHA256.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f'precondition failed: {path.relative_to(ROOT)} sha256={actual}')

    statements = [json.loads(x) for x in STATEMENTS.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
    if len({r['statement_id'] for r in statements}) != len(statements):
        raise SystemExit('duplicate statement IDs in input')
    by_id = {r['statement_id']: r for r in statements}
    if not TARGET_IDS <= set(by_id):
        raise SystemExit(f'missing p.141 targets: {sorted(TARGET_IDS - set(by_id))}')
    if any(by_id[sid].get('segment_id') != SEG for sid in TARGET_IDS):
        raise SystemExit('p.141 target segment mismatch')
    if any(by_id[sid].get('qualifiers', {}).get('relation_candidate') is not None for sid in TARGET_IDS):
        raise SystemExit('a p.141 target was already classified; refusing to overwrite')
    footnote3_source = by_id['st-chp5-p141-1651-sacchi-albani-letter-exchange']
    footnote3_link = {
        key: json.loads(json.dumps(footnote3_source['qualifiers'][key], ensure_ascii=False))
        for key in ('footnote_target_line', 'footnote_link_status', 'citation_segment_id',
                    'citation_source_line_start', 'citation_source_line_end', 'footnote_refs')
        if key in footnote3_source['qualifiers']
    }

    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        candidate_reader = csv.DictReader(f)
        candidate_fields = candidate_reader.fieldnames
        candidates = list(candidate_reader)
    numeric_ids = [int(r['candidate_id'].split('-')[1]) for r in candidates]
    if max(numeric_ids) != 11935:
        raise SystemExit(f'unexpected candidate ID ceiling: {max(numeric_ids)}')
    new_candidates = [
        make_candidate('cand-11936', 'Other artists and theorists who attacked the Bamboccianti (unnamed collective)', '',
                       'The source names other artists and theorists as launching attacks on the Bamboccianti; individual members and exact boundaries remain unspecified.', 116),
        make_candidate('cand-11937', 'Grandest patrons who first took the Bamboccianti seriously (unnamed collective)', '',
                       'Haskell refers to the grandest patrons who began taking the group seriously; no patrons are identified, and this group is distinct from the private Roman connoisseurs in cand-5879.', 121),
        make_candidate('cand-11938', 'Correspondence between Andrea Sacchi and Francesco Albani (1651)', 'archive',
                       'The exchange of letters discussed by Haskell; no manuscript witness or complete text is identified here. Malvasia is said possibly to have doctored the letters.', 118),
    ]
    if {r['candidate_id'] for r in new_candidates} & {r['candidate_id'] for r in candidates}:
        raise SystemExit('candidate ID collision')

    with MENTIONS.open(encoding='utf-8-sig', newline='') as f:
        mention_reader = csv.DictReader(f)
        mention_fields = mention_reader.fieldnames
        mentions = list(mention_reader)
    mention_by_id = {r['mention_id']: r for r in mentions}
    patron_mention_id = 'm-chp5-sec-iii-l115-121-032'
    if patron_mention_id not in mention_by_id or mention_by_id[patron_mention_id]['candidate_id'] != 'cand-5879':
        raise SystemExit('expected p.141 grandest-patrons mention mapping not found')
    if mention_by_id[patron_mention_id]['surface_form'] != 'grandest patrons':
        raise SystemExit('unexpected p.141 patron mention surface')
    patron_start = SEGMENT_TEXT.find('grandest patrons')
    if (mention_by_id[patron_mention_id]['start_char'], mention_by_id[patron_mention_id]['end_char']) != (
            str(patron_start), str(patron_start + len('grandest patrons'))):
        raise SystemExit('existing p.141 patron mention offsets do not match source segment')

    # Separate the report of admission from Haskell's inference about Academy hostility.
    revise(
        by_id, 'st-chp5-p141-academy-admission-no-early-hostility',
        predicate='admitted_to_accademia_di_s_luca', line_start=117, line_end=117,
        original_quote=quote(117, 'His early admission into the ', 'Accademia di S. Luca'),
        claim='Haskell says Cerquozzi was admitted to the Accademia di S. Luca early in his career.',
        mentioned=['cand-3084', 'cand-3470'],
        qualification='The source gives no exact admission year; footnote 1 remains linked to the surrounding discussion.',
        relation=True,
    )
    # Correct the endpoint direction and retain the source-critical qualification.
    revise(
        by_id, 'st-chp5-p141-reni-and-passeri-attribution',
        subject='cand-1856', object_='cand-2127', predicate='biographer_attributed_some_own_hostility_to_subject',
        original_quote=quote(117, 'but the terms in which he expressed his hatred', 'to the master.'),
        claim='Haskell says Passeri attributed some of his own feelings about the Bamboccianti to Guido Reni.',
        mentioned=['cand-1856', 'cand-2127', 'cand-0173'],
        qualification='This is Haskell’s source-critical interpretation (“reasonably clear”, “some”); it does not establish that the hostile sentiment was Reni’s own. Footnote 2 remains linked.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p141-artists-accused-bamboccianti',
        subject='cand-11936', object_='cand-0173', predicate='accused_group_of_competing_on_low_prices',
        claim='Haskell says many artist opponents accused the Bamboccianti of competing through lower prices.',
        mentioned=['cand-11936', 'cand-0173', 'cand-0177'],
        qualification='The artists are unnamed; the accusation is reported by Haskell and is not endorsed as fact.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p141-financial-depression-and-cheaper-prices',
        object_=None, predicate='attacks_occurred_during_financial_depression',
        original_quote=quote(117, 'This was a period of ', 'acute financial depression'),
        claim='Haskell places the attacks amid a period of acute financial depression.',
        mentioned=['cand-0173'],
        qualification='Contextual dating in Haskell’s account; no precise start or end date is supplied.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p141-public-versus-man-of-taste-distinction',
        predicate='public_taste_distinction_deployed_against_movement',
        original_quote=quote(116, 'All the still embryonic distinctions', 'to discredit the movement'),
        claim='Haskell says the emerging distinction between the general public and the man of taste was used to discredit the movement.',
        mentioned=['cand-0173', 'cand-6177', 'cand-6063'],
        qualification='This is Haskell’s account of a critical strategy, not evidence of a formal institution or a documented group boundary.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p141-liberal-connoisseurship-and-cerquozzi-success',
        original_quote=quote(116, 'And inevitably the onslaught grew more fierce', 'became more widespread.'),
        claim='Haskell says attacks intensified as a more liberal form of connoisseurship became widespread.',
        qualification='This is Haskell’s causal interpretation of a broad cultural change.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p141-malvasia-may-have-doctored-letters',
        subject='cand-1501', object_='cand-11938', predicate='possibly_doctored_correspondence',
        original_quote=quote(121, 'it seems quite possible that the letters themselves', 'editor Malvasia'),
        claim='Haskell says Malvasia may have doctored the Sacchi–Albani letters.',
        mentioned=['cand-1501', 'cand-11938'],
        qualification='Retain Haskell’s “quite possible”; no manuscript witness or editorial intervention is independently verified. Footnote 3 points to L158.',
        relation=True,
        extra_qualifiers=footnote3_link,
    )
    revise(
        by_id, 'st-chp5-p141-hatred-developed-late-with-patronage',
        object_=None, predicate='intense_hostility_developed_relatively_late',
        original_quote=quote(121, 'that intense hatred for the bamboccianti', "relatively'late"),
        claim='Haskell says intense hostility toward the Bamboccianti developed relatively late.',
        mentioned=['cand-0173'],
        qualification='The apostrophe in S0 between “relatively” and “late” is an OCR artifact; printed p.141 reads “relatively late”. This preserves Haskell’s chronological interpretation.',
        relation=False,
        extra_qualifiers={'ocr_note': 'S0 reads “relatively\'late”; physical p.141 reads “relatively late”.'},
    )
    revise(
        by_id, 'st-chp5-p141-correspondence-significance-unclear',
        predicate='correspondence_treated_as_cardinal_in_history',
        original_quote=quote(119, 'though the correspondence has always been treated', 'cardinal importance in the history of the movement'),
        claim='Haskell says the Sacchi–Albani correspondence has been treated as cardinal in the movement’s history.',
        qualification='This describes how the correspondence has been treated; Haskell separately questions its significance.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p141-sacchi-asks-albani-opinion',
        predicate='asked_albani_for_opinion_on_bamboccianti',
        original_quote=quote(119, 'The Roman artist wrote to his ageing master', 'to ask for his opinion on the matter.'),
        claim='Haskell says Andrea Sacchi wrote to Francesco Albani and asked his opinion of the Bamboccianti.',
        mentioned=['cand-2318', 'cand-0021', 'cand-0173', 'cand-3398'],
        qualification='“The Roman artist” refers to Sacchi and “his ageing master” to Albani; the group spelling is corrected by the print. Footnote 3 remains linked to L158.',
        relation=True,
        extra_qualifiers=footnote3_link,
    )

    new_statements = [
        make_statement(
            'academy-no-hostility-in-1630s-inference', 'cand-3084', 'cand-3470',
            'admission_taken_as_evidence_of_no_academy_hostility', 117, 117,
            quote(117, 'shows indeed that in the', 'from that quarter.'),
            'Haskell infers from Cerquozzi’s early admission that the Academy was not hostile to him in the 1630s.',
            ['cand-3084', 'cand-3470'],
            'This is Haskell’s inference from the admission, not a separately documented institutional policy.',
            False,
        ),
        make_statement(
            'attacks-by-artists-and-theorists', 'cand-11936', 'cand-0173',
            'attacked_by_other_artists_and_theorists', 116, 116,
            quote(116, 'the attacks launched on the baniboccianti by ', 'other artists and theorists'),
            'Haskell says other artists and theorists launched attacks on the Bamboccianti.',
            ['cand-11936', 'cand-0173'],
            'The opponents are unnamed; their membership and institutional identities remain open.',
            True,
        ),
        make_statement(
            'bambocciate-described-unlike-actual-pictures', 'cand-0173', 'cand-6099',
            'critical_descriptions_often_misrepresented_pictures', 116, 116,
            quote(116, 'the bambocciate were described in terms', 'actual pictures.'),
            'Haskell says attacks often described the Bambocciate in terms that bore little resemblance to the actual pictures.',
            ['cand-0173', 'cand-6099'],
            'This is Haskell’s characterization of hostile descriptions, not an assessment of any named picture.',
            False,
        ),
        make_statement(
            'connoisseurship-cited-as-reason-for-cerquozzi-success', 'cand-3567', 'cand-3084',
            'liberal_connoisseurship_named_as_reason_for_success', 116, 116,
            quote(116, 'that more ‘liberal’ form of connoisseurship, which was one of the reasons for Cerquozzi', 'success'),
            'Haskell identifies the spread of a more liberal connoisseurship as one reason for Cerquozzi’s success.',
            ['cand-3567', 'cand-3084'],
            'Retain Haskell’s broad causal attribution; no particular collector or event is identified.',
            False,
        ),
        make_statement(
            'cheaper-prices-linked-to-group-success', 'cand-0173', 'cand-0177',
            'success_linked_to_considerably_cheaper_prices', 117, 117,
            quote(117, 'no doubt the success of the baniboccianti', 'struggle for survival.'),
            'Haskell says Bamboccianti success was linked to considerably cheaper prices during the struggle for survival.',
            ['cand-0173', 'cand-0177'],
            'This is Haskell’s account of a group-level price advantage, not a specific sale or price.',
            False,
        ),
        make_statement(
            'reni-listed-as-early-opponent-with-attribution-caveat', 'cand-2127', 'cand-0173',
            'listed_among_early_opponents_of_group', 117, 117,
            quote(117, 'Guido Reni (who died in 1642)', 'was among the first of these'),
            'Haskell lists Guido Reni among the earliest opponents of the Bamboccianti, then questions whether the hostility was Reni’s own.',
            ['cand-2127', 'cand-0173', 'cand-1856'],
            'Keep this as a qualified report: Haskell says Passeri may have projected some of his own feelings onto Reni. Footnote 2 points to L157.',
            True,
            footnote_source=by_id['st-chp5-p141-reni-and-passeri-attribution'],
        ),
        make_statement(
            'reni-death-year', 'cand-2127', None, 'died_in_1642', 117, 117,
            quote(117, 'who died in', '1642'),
            'Haskell gives Guido Reni’s death year as 1642.',
            ['cand-2127'],
            'Source-reported date; no external verification is implied.',
            False,
        ),
        make_statement(
            'sacchi-informed-albani-of-group-success', 'cand-2318', 'cand-0021',
            'informed_albani_of_bamboccianti_success', 119, 119,
            quote(119, 'to tell him of the success', 'baniboccianti'),
            'Haskell says Andrea Sacchi wrote to Albani about the Bamboccianti’s success.',
            ['cand-2318', 'cand-0021', 'cand-0173'],
            'The letter’s content is Haskell’s report; footnote 3 points to L158.',
            True,
            footnote_source=footnote3_source,
        ),
        make_statement(
            'correspondence-significance-not-altogether-clear', 'cand-2318', 'cand-0021',
            'historical_significance_of_correspondence_unclear', 119, 119,
            quote(119, 'in fact its significance is', 'not altogether clear.'),
            'Haskell says the historical significance of the Sacchi–Albani correspondence is not altogether clear.',
            ['cand-2318', 'cand-0021'],
            'Retain Haskell’s qualified assessment; footnote 3 points to L158.',
            False,
            footnote_source=footnote3_source,
        ),
        make_statement(
            'albani-held-attributed-hostile-view', 'cand-0021', 'cand-0173',
            'held_hostile_view_of_bamboccianti_as_attributed', 121, 121,
            quote(121, 'Albani and Sacchi no doubt held the hostile views ', 'attributed to them'),
            'Haskell says Albani held the hostile view of the Bamboccianti attributed to him.',
            ['cand-0021', 'cand-0173', 'cand-1501'],
            'This is Haskell’s qualified assessment of views attributed in a correspondence he says Malvasia may have doctored; footnote 3 points to L158.',
            True,
            footnote_source=footnote3_source,
        ),
        make_statement(
            'sacchi-held-attributed-hostile-view', 'cand-2318', 'cand-0173',
            'held_hostile_view_of_bamboccianti_as_attributed', 121, 121,
            quote(121, 'Albani and Sacchi no doubt held the hostile views ', 'attributed to them'),
            'Haskell says Sacchi held the hostile view of the Bamboccianti attributed to him.',
            ['cand-2318', 'cand-0173', 'cand-1501'],
            'This is Haskell’s qualified assessment of views attributed in a correspondence he says Malvasia may have doctored; footnote 3 points to L158.',
            True,
            footnote_source=footnote3_source,
        ),
        make_statement(
            'group-first-taken-seriously-by-grandest-patrons', 'cand-0173', 'cand-11937',
            'first_taken_seriously_by_grandest_patron_group', 121, 121,
            quote(121, 'when for the first time they were being taken seriously', 'grandest patrons'),
            'Haskell says the Bamboccianti were first taken seriously by the grandest patrons relatively late.',
            ['cand-0173', 'cand-11937'],
            'The patrons are unnamed; the “first” and timing remain Haskell’s characterization.',
            True,
        ),
    ]

    # The existing sentence also includes the report that Albani replied abusively.
    revise(
        by_id, 'st-chp5-p141-albani-response-described-as-abuse',
        original_quote=quote(119, 'This came quickly enough', 'stream of abuse.'),
        qualification='This is Haskell’s characterization of Albani’s reported reply to Sacchi, not a direct quotation. Footnote 3 points to L158.',
        relation=True,
        extra_qualifiers={
            'footnote_target_line': 158,
            'footnote_link_status': 'linked',
            'citation_segment_id': 'chp-5:05_CHP-5_sec_iii:l126-165',
            'citation_source_line_start': 158,
            'citation_source_line_end': 158,
            'footnote_refs': footnote3_source['qualifiers']['footnote_refs'],
        },
    )
    revise(
        by_id, 'st-chp5-p141-bamboccianti-preceded-1651-letter-by-quarter-century',
        qualification='This is Haskell’s broad chronology for the group, not a precise founding date. Footnote 3 identifies the cited letter source at L158.',
        extra_qualifiers={
            'footnote_target_line': 158,
            'footnote_link_status': 'linked',
            'citation_segment_id': 'chp-5:05_CHP-5_sec_iii:l126-165',
            'citation_source_line_start': 158,
            'citation_source_line_end': 158,
            'footnote_refs': footnote3_source['qualifiers']['footnote_refs'],
        },
    )
    revise(
        by_id, 'st-chp5-p141-1651-sacchi-albani-letter-exchange',
        subject='cand-2318', object_='cand-0021', predicate='exchanged_letters_about_bamboccianti_in_1651',
        mentioned=['cand-2318', 'cand-0021', 'cand-11938'],
        qualification='The exchange is Haskell’s report, citing Malvasia at L158; the letter text and its transmission are not independently verified. Albani’s identity remains for S3 alignment.',
        relation=True,
    )

    classifications = {
        'st-chp5-p141-1651-sacchi-albani-letter-exchange': True,
        'st-chp5-p141-academy-admission-no-early-hostility': True,
        'st-chp5-p141-albani-response-described-as-abuse': True,
        'st-chp5-p141-aristocratic-taste-and-relations': False,
        'st-chp5-p141-artists-accused-bamboccianti': True,
        'st-chp5-p141-attacks-peaked-with-cerquozzi-triumphs': False,
        'st-chp5-p141-attacks-targeted-new-ruling-class': False,
        'st-chp5-p141-bamboccianti-preceded-1651-letter-by-quarter-century': False,
        'st-chp5-p141-correspondence-significance-unclear': False,
        'st-chp5-p141-crowd-versus-connoisseur': False,
        'st-chp5-p141-financial-depression-and-cheaper-prices': False,
        'st-chp5-p141-financial-questions-in-success-and-opposition': False,
        'st-chp5-p141-hatred-developed-late-with-patronage': False,
        'st-chp5-p141-leading-figures-charged-more-earlier': False,
        'st-chp5-p141-liberal-connoisseurship-and-cerquozzi-success': False,
        'st-chp5-p141-malvasia-may-have-doctored-letters': True,
        'st-chp5-p141-old-families-power-bankruptcy-continuation': False,
        'st-chp5-p141-public-versus-man-of-taste-distinction': False,
        'st-chp5-p141-reni-and-passeri-attribution': True,
        'st-chp5-p141-sacchi-asks-albani-opinion': True,
        'st-chp5-p141-six-or-eight-scudi-claim-absurd': False,
        'st-chp5-p141-snobbery-as-anti-bamboccianti-appeal': False,
    }
    for sid, is_relation in classifications.items():
        classify(by_id[sid], is_relation)

    new_mentions = [
        mention('m-chp5-sec-iii-l115-121-033', 'cand-11936', 'other artists and theorists', 'Unnamed group identified by Haskell as attacking the Bamboccianti; exact membership remains open.'),
        mention('m-chp5-sec-iii-l115-121-034', 'cand-11936', 'many artists', 'Subset described as among the group’s fiercest enemies; do not infer named individuals.'),
        mention('m-chp5-sec-iii-l115-121-035', 'cand-11938', 'letters themselves', 'Coreference to the 1651 Sacchi–Albani correspondence; Haskell says Malvasia may have doctored it.'),
    ]
    mention_by_id[patron_mention_id]['candidate_id'] = 'cand-11937'
    mention_by_id[patron_mention_id]['note'] = 'Unnamed grandest patron group in Haskell’s p.141 account; distinct from private connoisseurs in cand-5879.'
    if any(m['mention_id'] in mention_by_id for m in new_mentions):
        raise SystemExit('mention ID collision')
    mentions.extend(new_mentions)

    segment_row = None
    with COVERAGE.open(encoding='utf-8-sig', newline='') as f:
        coverage_reader = csv.DictReader(f)
        coverage_fields = coverage_reader.fieldnames
        coverage_rows = list(coverage_reader)
    for row in coverage_rows:
        if row.get('segment_id') == SEG:
            segment_row = row
            break
    if not segment_row or segment_row.get('disposition') != 'reviewed' or segment_row.get('migration_status') != 'complete':
        raise SystemExit('p.141 coverage precondition failed')
    segment_row['note'] = '正文逐条完成S2语义分类；与注释1–4的来源回链保留。第140页L113残句由本段L116闭合。印本OCR校勘仅记于S2，不改S0。'

    new_ids = {r['statement_id'] for r in new_statements}
    if len(new_ids) != len(new_statements) or set(by_id) & new_ids:
        raise SystemExit('statement ID collision')
    candidate_ids = {r['candidate_id'] for r in candidates + new_candidates}
    mention_ids = {r['mention_id'] for r in mentions}
    if len(mention_ids) != len(mentions):
        raise SystemExit('duplicate mention IDs')
    for row in new_statements:
        q = row['qualifiers']
        if row['original_quote'] not in '\n'.join(SOURCE_LINES[q['source_line_start'] - 1:q['source_line_end']]):
            raise SystemExit(f'source quote mismatch: {row["statement_id"]}')
    for row in [by_id[sid] for sid in TARGET_IDS] + new_statements:
        q = row.get('qualifiers', {})
        if q.get('relation_candidate') is True:
            if not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
                raise SystemExit(f'relation candidate missing endpoint: {row["statement_id"]}')
            if row['subject_candidate_id'] not in candidate_ids or row['object_candidate_id'] not in candidate_ids:
                raise SystemExit(f'relation candidate endpoint missing: {row["statement_id"]}')
        for cid in q.get('mentioned_candidate_ids', []) or []:
            if cid and cid not in candidate_ids:
                raise SystemExit(f'mentioned candidate missing in {row["statement_id"]}: {cid}')
    all_rows = statements + new_statements
    relation_count = sum(r.get('qualifiers', {}).get('relation_candidate') is True for r in [by_id[sid] for sid in TARGET_IDS] + new_statements)
    nonrelation_count = sum(r.get('qualifiers', {}).get('relation_candidate') is False for r in [by_id[sid] for sid in TARGET_IDS] + new_statements)
    if relation_count + nonrelation_count != len(TARGET_IDS) + len(new_statements):
        raise SystemExit('p.141 classification count mismatch')

    candidate_output = csv_text(candidates + new_candidates, candidate_fields)
    mention_output = csv_text(mentions, mention_fields)
    coverage_output = csv_text(coverage_rows, coverage_fields)
    statement_output = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in all_rows)

    if args.apply:
        targets = [STATEMENTS, CANDIDATES, MENTIONS, COVERAGE]
        for path in targets:
            backup = path.with_name(path.name + BACKUP_TAG)
            if backup.exists():
                raise SystemExit(f'backup already exists; refusing to overwrite: {backup.name}')
        temp_paths = []
        for path, content in ((STATEMENTS, statement_output), (CANDIDATES, candidate_output),
                              (MENTIONS, mention_output), (COVERAGE, coverage_output)):
            temp = path.with_name(path.name + '.tmp-s2-chp5-p141')
            if temp.exists():
                raise SystemExit(f'temporary output exists; refusing to overwrite: {temp.name}')
            temp.write_bytes(('\ufeff' + content).encode('utf-8'))
            temp_paths.append((path, temp))
        for path in targets:
            shutil.copy2(path, path.with_name(path.name + BACKUP_TAG))
        for path, temp in temp_paths:
            os.replace(temp, path)
        print('applied guarded p.141 S2 claim atomization, candidate and mention repairs')
        print('backups:', ', '.join(path.name + BACKUP_TAG for path in targets))
    else:
        print('PREVIEW only; no table writes')

    print(f'p.141 existing statements classified: {len(TARGET_IDS)}')
    print(f'p.141 added atomic statements: {len(new_statements)}')
    print(f'p.141 relation candidates: {relation_count}; non-relational claims: {nonrelation_count}')
    print('new candidates:', ', '.join(r['candidate_id'] for r in new_candidates))
    print('new mentions:', ', '.join(r['mention_id'] for r in new_mentions))
    for row in sorted([by_id[sid] for sid in TARGET_IDS] + new_statements, key=lambda r: r['statement_id']):
        q = row.get('qualifiers', {})
        print(f"  {str(q['relation_candidate']).lower()} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']} | {q.get('claim', '')}")


if __name__ == '__main__':
    main()
