import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l95-101'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
MENTIONS = TABLES / 'mentions.csv'
COVERAGE = TABLES / 's2-coverage.csv'
BACKUP_TAG = '.bak-s2-chp5-p139-20261013'
NEW_CANDIDATE_ID = 'cand-11935'
NEW_CANDIDATE_NAME = 'French political camp to which Cardinal Bernardino Spada was aligned (unnamed)'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: '4e577e1100bf922baf829fa7210a50ca165c22e02b2fdf59bfa6a0668741ebd4',
    CANDIDATES: 'c7f85a878fa319dce4ac3d64befc04cc2ee5d759eb6b3dfcf101acdc0146b1cd',
    MENTIONS: 'ef041eaa6a2008a9b36eb36c7cdc5cf582338069305a2278ec3085b4a649ffd7',
    COVERAGE: '810b9ac4901bf34c9b5e7a5bdfa22b7d0253038d45f2d647f2d930a9b17ec606',
}

TARGET_IDS = {
    'st-chp5-p139-chigi-identity-influence-partial',
    'st-chp5-p139-chigi-pictures',
    'st-chp5-p139-codazzi-collaboration-begins',
    'st-chp5-p139-codazzi-eyewitness-account',
    'st-chp5-p139-collaboration-style-shift',
    'st-chp5-p139-commissioner-unknown',
    'st-chp5-p139-conditional-spada-commission',
    'st-chp5-p139-folk-art-contrast',
    'st-chp5-p139-masaniello-painting',
    'st-chp5-p139-mazarin-supporters-vote',
    'st-chp5-p139-objective-1647-event',
    'st-chp5-p139-picture-neutrality',
    'st-chp5-p139-spada-assembled-collection',
    'st-chp5-p139-spada-collection-membership',
    'st-chp5-p139-spada-french-camp',
    'st-chp5-p139-spadaro-comparison',
    'st-chp5-p139-spanish-defeat-for-spada',
    'st-chp5-p139-spanish-veto',
    'st-chp5-p139-turning-point',
}
P138_CONTINUATION = 'st-chp5-p138-possible-crisis-1648-partial'

RELATION_NOTE = (
    'S2 identifies a specific source-grounded relation candidate; source '
    'qualification is retained, and no formal S6 edge is created.'
)
NONRELATION_NOTE = (
    'This is an interpretive, scalar, or contextual assertion rather than a '
    'specific entity relation.'
)

source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()
segment_text = '\n'.join(source_lines[94:101])
UNSET = object()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    return list(rows[0]), rows


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


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
    quote = text[start:end + len(end_marker)]
    if quote not in text:
        raise ValueError(f'quote is not a source substring: {quote!r}')
    return quote


def note_context(row):
    q = row.get('qualifiers', {})
    return {k: v for k, v in q.items() if k.startswith('footnote_') or k.startswith('citation_')}


def classify(row, is_relation):
    q = row.setdefault('qualifiers', {})
    q['relation_candidate'] = is_relation
    q['relation_candidate_note'] = RELATION_NOTE if is_relation else NONRELATION_NOTE


def revise(by_id, sid, *, subject=UNSET, object_=UNSET, predicate=None,
           line_start=None, line_end=None, quote=None, claim=None,
           mentioned=None, qualification=None, relation=None,
           extra_qualifiers=None, remove_qualifiers=None):
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
    if extra_qualifiers:
        q.update(extra_qualifiers)
    if relation is not None:
        classify(row, relation)
    return row


def make_statement(suffix, subject, object_, predicate, line_start, line_end,
                   quote, claim, mentioned, qualification, relation,
                   *, notes_from=None, extra_qualifiers=None):
    if quote not in '\n'.join(source_lines[line_start - 1:line_end]):
        raise ValueError(f'quote absent from source L{line_start}-L{line_end}: {quote!r}')
    q = {
        'source_line_start': line_start,
        'source_line_end': line_end,
        'printed_page': 139,
        'pdf_physical_page': 24,
        'claim': claim,
        'speaker': 'Haskell',
        'text_layer': 'authorial narration',
        'qualification': qualification,
        'mentioned_candidate_ids': mentioned,
    }
    if notes_from:
        q.update(note_context(notes_from))
    if extra_qualifiers:
        q.update(extra_qualifiers)
    row = {
        'statement_id': f'st-chp5-p139-{suffix}',
        'segment_id': SEG,
        'subject_candidate_id': subject,
        'object_candidate_id': object_,
        'predicate': predicate,
        'qualifiers': q,
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
    statement_ids = [r['statement_id'] for r in statements]
    if len(statement_ids) != len(set(statement_ids)):
        raise SystemExit('duplicate statement IDs in input')
    by_id = {r['statement_id']: r for r in statements}
    if not TARGET_IDS | {P138_CONTINUATION} <= set(by_id):
        raise SystemExit(f'missing statement targets: {sorted((TARGET_IDS | {P138_CONTINUATION}) - set(by_id))}')
    if any(by_id[sid].get('segment_id') != SEG for sid in TARGET_IDS):
        raise SystemExit('p.139 target segment mismatch')
    if by_id[P138_CONTINUATION].get('segment_id') != 'chp-5:05_CHP-5_sec_iii:l82-93':
        raise SystemExit('p.138 continuation segment mismatch')
    if any(by_id[sid].get('qualifiers', {}).get('relation_candidate') is not None for sid in TARGET_IDS | {P138_CONTINUATION}):
        raise SystemExit('a target was already relation-classified; refusing to overwrite')

    candidate_fields, candidates = load_csv(CANDIDATES)
    mention_fields, mentions = load_csv(MENTIONS)
    coverage_fields, coverage_rows = load_csv(COVERAGE)
    candidate_ids = {r['candidate_id'] for r in candidates}
    if NEW_CANDIDATE_ID in candidate_ids:
        raise SystemExit(f'{NEW_CANDIDATE_ID} already exists')
    numeric_ids = [int(cid[5:]) for cid in candidate_ids if cid.startswith('cand-') and cid[5:].isdigit()]
    if max(numeric_ids) + 1 != int(NEW_CANDIDATE_ID[5:]):
        raise SystemExit('candidate ID sequence changed')
    coverage = next((r for r in coverage_rows if r.get('segment_id') == SEG), None)
    if not coverage or coverage.get('disposition') != 'reviewed' or coverage.get('migration_status') != 'complete':
        raise SystemExit('p.139 coverage precondition failed')

    new_candidate = {
        'candidate_id': NEW_CANDIDATE_ID,
        'index_entry_id': '',
        'canonical_name': NEW_CANDIDATE_NAME,
        'index_page_range': '',
        'suggested_type': '',
        'status': 'open',
        'index_source_file': '',
        'sub_entry': '',
        'detail': (
            'Haskell says Cardinal Bernardino Spada was firmly in this French political camp. '
            'The text does not identify a formal institution or establish that this camp is the '
            'same group as the French-aligned supporters in the later conclave; keep them distinct.'
        ),
        'exclude_reason': '',
        'candidate_origin': 'body-mention',
        'candidate_source_ref': f'{SEG}#L96',
    }
    if any(r.get('canonical_name') == NEW_CANDIDATE_NAME for r in candidates):
        raise SystemExit('candidate natural-key collision')

    mention_by_id = {r['mention_id']: r for r in mentions}
    french_camp_mention = 'm-chp5-sec-iii-l95-101-007'
    neutrality_mention = 'm-chp5-sec-iii-l95-101-020'
    if french_camp_mention not in mention_by_id or mention_by_id[french_camp_mention].get('candidate_id') != 'cand-6160':
        raise SystemExit('French camp mention remap precondition failed')
    if neutrality_mention not in mention_by_id or mention_by_id[neutrality_mention].get('candidate_id') != 'cand-4060':
        raise SystemExit('Cerquozzi neutrality mention remap precondition failed')
    if mention_by_id[french_camp_mention].get('surface_form') != 'French camp':
        raise SystemExit('French camp mention surface changed')

    codazzi_note = note_context(by_id['st-chp5-p139-codazzi-eyewitness-account'])

    # Close the p.138 sentence fragment and classify its contextual claim.
    revise(
        by_id, P138_CONTINUATION,
        predicate='possible_crisis_about_1648_context',
        claim='Haskell says a crisis may have occurred about 1648, the context for his qualified dating of The Revolt of Masaniello.',
        qualification='The sentence closes at p.139 L96: Haskell says Cerquozzi probably painted The Revolt of Masaniello during this possible crisis. The crisis itself remains conjectural and is not a separately identified event.',
        relation=False,
    )

    # Split the first sentence and connect Flavio Chigi's identity across the page turn.
    revise(
        by_id, 'st-chp5-p139-chigi-identity-influence-partial',
        predicate='nephew_of', subject='cand-0671', object_='cand-0665',
        line_start=100, line_end=100,
        quote=source_quote(100, 'Flavio Chigi, nephew', 'Alexander VII'),
        claim='Haskell identifies Flavio Chigi as the nephew of Pope Alexander VII.',
        mentioned=['cand-0671', 'cand-0665'],
        qualification='The following description of Chigi as Rome’s most influential patron continues at p.140 L104 and is recorded separately.',
        relation=True,
        remove_qualifiers=['continuation_line', 'continuation_segment', 'continuation_status', 'continued_by_statement_id', 'continued_by_segment_id'],
    )
    revise(
        by_id, 'st-chp5-p139-chigi-pictures',
        predicate='painted_several_pictures_for_chigi_after_1657',
        line_start=99, line_end=100,
        claim='Haskell says Cerquozzi and Codazzi painted several pictures for Cardinal Flavio Chigi some time after 1657, about three years before Cerquozzi’s death.',
        qualification='Retain the broad date and the source’s attribution. Footnote 1 at p.140 L104 says the commission cannot be conclusively proved, despite contemporary ownership references and inventory entries; do not convert “for Chigi” into a proven commission.',
        relation=True,
    )

    # Break apart the commission context, painter biography, and witness account.
    revise(
        by_id, 'st-chp5-p139-codazzi-eyewitness-account',
        object_='cand-4490', predicate='arrived_in_rome_from_naples_towards_end_1647',
        line_start=99, line_end=99,
        quote=source_quote(99, 'who arrived in Rome', 'end of 1647'),
        claim='Haskell says Viviano Codazzi arrived in Rome from Naples towards the end of 1647.',
        mentioned=['cand-0794', 'cand-4490', 'cand-1722'],
        qualification='Retain “towards the end”. Footnote 6 discusses Codazzi’s 1636 statement about his earlier move from Bergamo to Naples and Haskell’s dating of the collaboration after 1647.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p139-codazzi-collaboration-begins',
        qualification='Retain “probably” and “main phase”; this is a likely beginning of the principal collaboration, not proof that the artists had never worked together earlier. Footnote 6 discusses the competing chronology.',
        relation=True,
        extra_qualifiers=codazzi_note,
    )
    revise(
        by_id, 'st-chp5-p139-turning-point',
        subject='cand-4131', object_=None,
        predicate='contemporary_event_records_almost_unknown_in_seventeenth_century_italian_art',
        line_start=96, line_end=96,
        quote=source_quote(96, 'for such records of contemporary events', 'particular patron.'),
        claim='Haskell says records of contemporary events were almost unknown in seventeenth-century Italian art unless associated with a particular patron.',
        mentioned=['cand-4131', 'cand-4060'],
        qualification='Retain “almost”. Footnote 1 points to Pietro Paolini’s The Death of Wallenstein as an extraordinary case; the cited example does not independently verify the generalization.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p139-collaboration-style-shift',
        predicate='collaboration_confirmed_cerquozzi_style_shift',
        line_start=99, line_end=99,
        quote=source_quote(99, 'it confirmed Cerquozzi’s move', 'even the exotic.'),
        claim='Haskell says the collaboration confirmed Cerquozzi’s move away from simpler, direct presentations of peasant life towards the grandiose and exotic.',
        mentioned=['cand-3084', 'cand-0794', 'cand-6099'],
        qualification='This is Haskell’s interpretation of stylistic development; the categories and causal link remain his framing.',
        relation=False,
    )

    # Separate the unknown commissioner, conditional Spada possibility, and political interpretation.
    revise(
        by_id, 'st-chp5-p139-commissioner-unknown',
        line_start=96, line_end=96,
        quote=source_quote(96, 'Who commissioned this remarkable picture?', 'We only know that'),
        claim='Haskell presents the commissioner of the picture as unknown in the account.',
        qualification='This describes the book’s stated knowledge, not proof that no commission record exists.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p139-conditional-spada-commission',
        predicate='conditional_painting_for_cardinal_bernardino_spada',
        line_start=96, line_end=96,
        quote=source_quote(96, 'If it was actually painted for', 'Cardinal Bernardino'),
        claim='Haskell raises the possibility that the picture was painted for Cardinal Bernardino Spada.',
        mentioned=['cand-4060', 'cand-2493'],
        qualification='The commission is explicitly conditional (“if it was actually painted”); retain it as a qualified relation candidate, not an established commission.',
        relation=True,
    )

    # Separate Spada's office and political alignment; keep the later conclave group distinct.
    revise(
        by_id, 'st-chp5-p139-spada-french-camp',
        object_=NEW_CANDIDATE_ID, predicate='aligned_with_french_political_camp',
        line_start=96, line_end=96,
        quote=source_quote(96, 'was firmly in the', 'French camp'),
        claim='Haskell says Cardinal Bernardino Spada was firmly aligned with an unnamed French political camp.',
        mentioned=['cand-2493', NEW_CANDIDATE_ID],
        qualification='The political camp is not identified as a formal institution and is kept distinct from the French-aligned supporters in the later conclave.',
        relation=True,
    )

    # Treat the revolt painting and its comparison as distinct factual and interpretive claims.
    revise(
        by_id, 'st-chp5-p139-masaniello-painting',
        predicate='cerquozzi_probably_painted_revolt_during_possible_crisis_about_1648',
        claim='Continuing the possible crisis around 1648, Haskell says Cerquozzi probably painted The Revolt of Masaniello during it.',
        qualification='Closes p.138 L93. Retain “may have occurred”, “about”, and “probably”; Plate 22b identifies the same work candidate.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p139-objective-1647-event',
        subject='cand-4060', object_='cand-1559', predicate='depicts_events_of_1647_07_07',
        line_start=97, line_end=97,
        quote=source_quote(97, 'Vividly it portrays the events of', '7 July 1647'),
        claim='Haskell says The Revolt of Masaniello vividly portrays the events of 7 July 1647.',
        mentioned=['cand-4060', 'cand-1559'],
        qualification='This records Haskell’s identification of the depicted event; the date and accuracy are not independently verified.',
        relation=True,
    )
    revise(
        by_id, 'st-chp5-p139-picture-neutrality',
        predicate='picture_described_as_inscrutable',
        line_start=97, line_end=97,
        quote=source_quote(97, 'The picture itself is', 'inscrutable;'),
        claim='Haskell calls the picture inscrutable.',
        mentioned=['cand-4060'],
        qualification='This is Haskell’s interpretive characterization.',
        relation=False,
    )
    revise(
        by_id, 'st-chp5-p139-spadaro-comparison',
        line_start=97, line_end=98,
        quote=source_quote(97, 'Compared to the almost mediaeval vision', 'the Roman seems cold and detached.' , 98),
        claim='Haskell contrasts Cerquozzi’s cold, detached picture with Micco Spadaro’s almost mediaeval vision of Masaniello.',
        mentioned=['cand-4060', 'cand-6162', 'cand-2495', 'cand-4150', 'cand-6163'],
        qualification='This is Haskell’s comparative visual interpretation, not a documented relationship between the painters or works. Footnote 5 identifies the location of Spadaro’s pictures but not this particular canvas.',
        relation=False,
    )

    # Decompose the Spanish alignment, depicted defeat, and authorial career reading.
    revise(
        by_id, 'st-chp5-p139-spanish-defeat-for-spada',
        subject='cand-3084', object_='cand-6166', predicate='committed_to_spanish_cause_in_naples_context',
        line_start=97, line_end=97,
        quote=source_quote(97, 'Cerquozzi, deeply committed to the', 'Spanish cause'),
        claim='Haskell describes Cerquozzi as deeply committed to the Spanish cause in the Naples revolt context.',
        mentioned=['cand-3084', 'cand-6166'],
        qualification='The actors represented by the Spanish cause remain unnamed; keep this Naples revolt context distinct from the Spanish conclave actors at L97.',
        relation=True,
    )

    # Keep the source-backed single claims and classify them.
    for sid in [
        'st-chp5-p139-folk-art-contrast',
        'st-chp5-p139-mazarin-supporters-vote',
        'st-chp5-p139-spada-assembled-collection',
        'st-chp5-p139-spada-collection-membership',
        'st-chp5-p139-spanish-veto',
    ]:
        classify(by_id[sid], True)
    classify(by_id['st-chp5-p139-folk-art-contrast'], False)

    new_statements = [
        make_statement(
            'chigi-pictures-codazzi-link', 'cand-0794', 'cand-6164',
            'painted_several_pictures_for_chigi_after_1657', 99, 100,
            by_id['st-chp5-p139-chigi-pictures']['original_quote'],
            'Haskell includes Viviano Codazzi with Cerquozzi among the painters of several pictures for Cardinal Flavio Chigi after 1657.',
            ['cand-0794', 'cand-3084', 'cand-6164', 'cand-0671'],
            'This is the second artist-to-work-group relation in the joint statement. Footnote 1 at p.140 L104 says commission cannot be conclusively proved; do not treat “for Chigi” as a proven commission.',
            True, notes_from=by_id['st-chp5-p139-chigi-pictures'],
        ),
        make_statement(
            'conditional-spada-political-significance', 'cand-4060', None,
            'conditional_political_significance', 96, 96,
            source_quote(96, 'it must surely have had some', 'political significance.'),
            'Haskell infers that the picture would have had political significance if it had actually been painted for Spada.',
            ['cand-4060', 'cand-2493'],
            'This consequence depends on the explicitly unproven commission possibility; record it as Haskell’s interpretation, not an established fact.',
            False,
        ),
        make_statement(
            'spada-papal-nuncio-paris', 'cand-2493', 'cand-4653',
            'served_as_papal_nuncio_in', 96, 96,
            source_quote(96, 'who had been papal nunzio in', 'Paris'),
            'Haskell says Spada had previously served as papal nuncio in Paris.',
            ['cand-2493', 'cand-4653'],
            'The office is supplied in the predicate; the source does not give dates for this post.',
            True,
        ),
        make_statement(
            'codazzi-account-supplied', 'cand-0794', 'cand-6167',
            'may_have_supplied_account_underlying_picture', 99, 99,
            source_quote(99, 'who may well have supplied the eye-witness account', 'picture is based.'),
            'Haskell says Codazzi may well have supplied the eyewitness account on which the picture was based.',
            ['cand-0794', 'cand-6167', 'cand-4060'],
            'Retain “may well”; the account is unidentified and its role as the picture’s basis remains conjectural.',
            True,
        ),
        make_statement(
            'collaboration-importance', 'cand-3084', 'cand-0794',
            'collaboration_described_as_important', 99, 99,
            source_quote(99, 'The collaboration was of', 'great importance'),
            'Haskell calls the collaboration between Cerquozzi and Codazzi of great importance.',
            ['cand-3084', 'cand-0794'],
            'This is Haskell’s assessment of the collaboration, not a distinct documented event.',
            False,
        ),
        make_statement(
            'objective-accuracy', 'cand-4060', None,
            'described_as_painted_with_scrupulous_accuracy', 97, 97,
            source_quote(97, 'with the most', 'scrupulous accuracy'),
            'Haskell says the picture depicts the revolt with the most scrupulous accuracy.',
            ['cand-4060', 'cand-1559'],
            'This is Haskell’s assessment and has not been independently verified.',
            False, notes_from=by_id['st-chp5-p139-objective-1647-event'],
        ),
        make_statement(
            'objectivity-on-contentious-subject', 'cand-4060', None,
            'objectivity_on_subject_that_stirred_european_passions', 97, 97,
            source_quote(97, 'a remarkable instance of objectivity exercised', 'passions of Europe.'),
            'Haskell calls the picture a remarkable instance of objectivity on a subject that stirred European passions.',
            ['cand-4060', 'cand-1559', 'cand-3462'],
            'This is Haskell’s interpretation of the picture; the claimed objectivity is not independently verified.',
            False, notes_from=by_id['st-chp5-p139-objective-1647-event'],
        ),
        make_statement(
            'picture-neutrality-and-antiheroic-reading', 'cand-4060', None,
            'cerquozzi_neutrality_and_antiheroic_quality_evident_in_picture', 97, 97,
            source_quote(97, 'never was Cerquozzi', 'so much in evidence.'),
            'Haskell says Cerquozzi’s interpreted neutrality and anti-heroic quality are especially evident in this picture.',
            ['cand-4060', 'cand-3084', 'cand-0626'],
            'This is Haskell’s stylistic interpretation; it does not establish the picture as politically neutral.',
            False,
        ),
        make_statement(
            'spadaro-depicts-masaniello-twice', 'cand-6162', 'cand-4150',
            'depicts_masaniello_twice', 97, 98,
            source_quote(97, 'Micco Spadaro who depicts', 'twice in the same canvas', 98),
            'Haskell says Micco Spadaro’s unidentified canvas depicts Masaniello twice.',
            ['cand-6162', 'cand-2495', 'cand-4150'],
            'The painting is not identified by title; “twice” describes its composition.',
            True,
        ),
        make_statement(
            'spadaro-background-scene', 'cand-6162', 'cand-4150',
            'depicts_masaniello_exhorting_crowd_with_crucifix_in_background', 98, 98,
            source_quote(98, 'in the background exhorting the crowd', 'with his crucifix'),
            'Haskell describes the background of Spadaro’s canvas as showing Masaniello exhorting the crowd with a crucifix.',
            ['cand-6162', 'cand-4150'],
            'This is a description of pictorial content, not evidence that the depicted episode occurred as shown.',
            True,
        ),
        make_statement(
            'spadaro-foreground-scene', 'cand-6162', 'cand-6163',
            'depicts_masaniello_on_way_to_visit_spanish_viceroy', 98, 98,
            source_quote(98, 'in the foreground at the height of his power', 'Spanish viceroy'),
            'Haskell describes the foreground as showing Masaniello at the height of his power, in velvet headdress and white plumes, on his way to visit the Spanish viceroy.',
            ['cand-6162', 'cand-4150', 'cand-6163'],
            'The viceroy is unnamed; the action is described as depicted content, not independently verified biography.',
            True,
        ),
        make_statement(
            'spanish-defeat-depicted', 'cand-4060', 'cand-6166',
            'depicts_humiliating_spanish_defeat', 97, 97,
            source_quote(97, 'painting the spectacle of their', 'most humiliating defeat'),
            'Haskell describes The Revolt of Masaniello as depicting a humiliating Spanish defeat.',
            ['cand-4060', 'cand-6166'],
            'The Spanish actors are not identified; “most humiliating” is Haskell’s characterization.',
            True,
        ),
        make_statement(
            'career-paradox-for-francophile-cardinal', 'cand-3084', 'cand-2493',
            'career_paradox_of_spanish_defeat_for_francophile_cardinal', 97, 97,
            source_quote(97, 'for the most Francophil of Cardinals', 'in his career.'),
            'Haskell treats the contrast between the Spanish defeat and its association with the most Francophile cardinal as characteristic of Cerquozzi’s career.',
            ['cand-3084', 'cand-4060', 'cand-6166', 'cand-2493'],
            'This is Haskell’s career interpretation. The preceding commission for Spada is expressly conditional and is not established here.',
            False,
        ),
        make_statement(
            'turning-point-circumstances-mysterious', 'cand-4060', None,
            'circumstances_described_as_mysterious', 96, 96,
            source_quote(96, 'The circumstances are', 'very mysterious'),
            'Haskell describes the circumstances of the picture as very mysterious.',
            ['cand-4060'],
            'This records Haskell’s characterization; it does not identify a missing commission or source.',
            False,
        ),
        make_statement(
            'turning-point-in-cerquozzi-career', 'cand-4060', None,
            'described_as_career_turning_point', 96, 96,
            source_quote(96, 'in many ways the picture marks something of a turning-point', 'in his career'),
            'Haskell says the picture marks something of a turning point in Cerquozzi’s career.',
            ['cand-4060', 'cand-3084'],
            'Retain “in many ways” and the author’s interpretive framing.',
            False,
        ),
    ]

    # Store the separately grounded fact that the collaboration itself began with this work.
    for key, value in codazzi_note.items():
        by_id['st-chp5-p139-codazzi-collaboration-begins']['qualifiers'][key] = value

    # The existing Spanish-decision sentence is a distinct relation, and the folk-art comparison is not.
    classify(by_id['st-chp5-p139-spanish-veto'], True)
    classify(by_id['st-chp5-p139-folk-art-contrast'], False)

    # Correct the two local mentions whose previous candidates conflated a broad camp or artwork with a person.
    mention_by_id[french_camp_mention]['candidate_id'] = NEW_CANDIDATE_ID
    mention_by_id[french_camp_mention]['note'] = (
        'This is Spada’s broader, unnamed French political alignment; keep it distinct from the later conclave supporters.'
    )
    mention_by_id[neutrality_mention]['candidate_id'] = 'cand-3084'
    mention_by_id[neutrality_mention]['note'] = (
        'The possessive phrase attributes neutrality to Cerquozzi; it is not a mention of the painting candidate.'
    )
    candidates_by_id = {r['candidate_id']: r for r in candidates}
    candidates_by_id['cand-6160']['detail'] = (
        'Unnamed supporters of France whom Mazarin told to vote for Spada in the conclave after Innocent X’s death. '
        'Keep distinct from the broader French political camp to which Spada was aligned.'
    )

    # Existing source statements that remain single claims.
    revise(
        by_id, 'st-chp5-p139-folk-art-contrast',
        qualification='“The fishmonger” refers to Masaniello; no particular folk-art portrait is identified. This is Haskell’s visual comparison.',
        relation=False,
    )
    for sid in [
        'st-chp5-p139-masaniello-painting',
        'st-chp5-p139-mazarin-supporters-vote',
        'st-chp5-p139-spada-assembled-collection',
        'st-chp5-p139-spada-collection-membership',
        'st-chp5-p139-spada-french-camp',
        'st-chp5-p139-spanish-veto',
        'st-chp5-p139-chigi-identity-influence-partial',
        'st-chp5-p139-chigi-pictures',
        'st-chp5-p139-codazzi-collaboration-begins',
        'st-chp5-p139-codazzi-eyewitness-account',
        'st-chp5-p139-conditional-spada-commission',
        'st-chp5-p139-objective-1647-event',
        'st-chp5-p139-spanish-defeat-for-spada',
        'st-chp5-p139-turning-point',
    ]:
        if by_id[sid].get('qualifiers', {}).get('relation_candidate') not in (True, False):
            raise SystemExit(f'target not classified: {sid}')

    new_ids = {r['statement_id'] for r in new_statements}
    if len(new_ids) != len(new_statements) or set(statement_ids) & new_ids:
        raise SystemExit('statement ID collision')
    available_candidates = candidate_ids | {NEW_CANDIDATE_ID}
    check_rows = [by_id[sid] for sid in TARGET_IDS | {P138_CONTINUATION}] + new_statements
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
    if segment_text[int(mention_by_id[french_camp_mention]['start_char']):int(mention_by_id[french_camp_mention]['end_char'])] != 'French camp':
        raise SystemExit('French camp mention span changed')
    if by_id[P138_CONTINUATION]['qualifiers'].get('relation_candidate') is not False:
        raise SystemExit('p.138 continuation was not closed as a nonrelational context claim')

    target_rows = [by_id[sid] for sid in TARGET_IDS]
    p139_rows = target_rows + new_statements
    p139_relation_count = sum(r['qualifiers']['relation_candidate'] is True for r in p139_rows)
    p139_nonrelation_count = sum(r['qualifiers']['relation_candidate'] is False for r in p139_rows)
    if p139_relation_count + p139_nonrelation_count != len(p139_rows):
        raise SystemExit('p.139 classification count mismatch')

    if args.apply:
        paths = [STATEMENTS, CANDIDATES, MENTIONS]
        backups = [p.with_name(p.name + BACKUP_TAG) for p in paths]
        if any(p.exists() for p in backups):
            raise SystemExit('backup already exists; refusing to overwrite')
        for src, backup in zip(paths, backups):
            shutil.copy2(src, backup)
        for row in new_statements:
            statements.append(row)
        candidates.append({key: new_candidate.get(key, '') for key in candidate_fields})
        mentions = [mention_by_id[r['mention_id']] for r in mentions]
        temp_paths = [p.with_name(p.name + '.tmp-s2-chp5-p139') for p in paths]
        if any(p.exists() for p in temp_paths):
            raise SystemExit('temporary output exists; refusing to overwrite')
        try:
            with temp_paths[0].open('w', encoding='utf-8-sig', newline='') as f:
                for row in statements:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
            write_csv(temp_paths[1], candidate_fields, candidates)
            write_csv(temp_paths[2], mention_fields, mentions)
            for temp, target in zip(temp_paths, paths):
                os.replace(temp, target)
        finally:
            for temp in temp_paths:
                if temp.exists():
                    temp.unlink()
        print('applied guarded p.139 S2 claim atomization and classification')
        print('backups:', ', '.join(p.name for p in backups))
    else:
        print('PREVIEW only; no table writes')

    print(f'p.139 existing statements classified: {len(TARGET_IDS)}')
    print(f'p.139 added atomic statements: {len(new_statements)}')
    print(f'p.139 relation candidates: {p139_relation_count}; non-relational claims: {p139_nonrelation_count}')
    print(f'cross-page p.138 context classified non-relational: {P138_CONTINUATION}')
    print(f'new candidate: {NEW_CANDIDATE_ID} ({NEW_CANDIDATE_NAME})')
    print('mention remaps:', f'{french_camp_mention} -> {NEW_CANDIDATE_ID}; {neutrality_mention} -> cand-3084')
    for row in sorted(p139_rows, key=lambda r: r['statement_id']):
        q = row.get('qualifiers', {})
        print(f"  {str(q['relation_candidate']).lower()} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']} | {q.get('claim', '')}")


if __name__ == '__main__':
    main()
