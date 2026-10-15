import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l28-34'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
STATEMENTS = ROOT / '04-knowledge/tables/book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge/tables/entity-candidates.csv'
MENTIONS = ROOT / '04-knowledge/tables/mentions.csv'
BACKUP_TAG = '.bak-s2-chp5-p135-20261013'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: '812c65d9d55128317036e4f4360c8ba2b305b5e1fd35185a546d50681f879c8b',
    CANDIDATES: '8ad570a955eb9eab2cd23c98ca19600c3ca91d65bfd6f999362f2b31fe81296a',
    MENTIONS: '82fbb006f33977bff593272a08506179512611387e93f7017deb14641fd1dfb9',
}

TARGET_IDS = {
    'st-chp5-p135-carracci-works-incidental-to-orthodox-career',
    'st-chp5-p135-cassiano-may-have-owned-van-laer-picture',
    'st-chp5-p135-giustiniani-acquired-two-uncharacteristic-van-laer-pictures',
    'st-chp5-p135-giustiniani-protected-caravaggios-northern-followers',
    'st-chp5-p135-influential-roman-patrons-took-cautious-interest',
    'st-chp5-p135-no-real-forerunners-and-difficulty-of-breaking-categories',
    'st-chp5-p135-northern-compatriots-among-van-laer-admirers',
    'st-chp5-p135-painters-admired-van-laer-as-model-of-reality',
    'st-chp5-p135-simonelli-temporarily-owned-and-exchanged-two-pictures',
    'st-chp5-p135-swanevelt-owned-two-van-laer-pictures',
    'st-chp5-p135-testa-connected-to-early-bamboccianti-and-may-have-owned-work',
    'st-chp5-p135-van-laer-arrived-in-rome-1625',
    'st-chp5-p135-van-laer-associated-with-schildersbent',
    'st-chp5-p135-van-laer-buyers-hard-to-identify',
    'st-chp5-p135-van-laer-cut-off-from-official-patronage',
    'st-chp5-p135-van-laer-dedicated-eight-animal-engravings',
    'st-chp5-p135-van-laer-expensive-reputation',
    'st-chp5-p135-van-laer-grew-up-in-haarlem',
    'st-chp5-p135-van-laer-picture-price',
    'st-chp5-p135-van-laer-sold-small-scenes-through-fairs-and-dealers',
}

RELATION_NOTE = (
    'Source-grounded S2 relation candidate; source qualification is retained, '
    'and no formal S6 edge is created.'
)
NONRELATION_NOTE = (
    'This is a scalar, contextual, or interpretive assertion rather than a '
    'specific entity relation.'
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0])
    return fields, rows


def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def relation(row, is_relation):
    q = row.setdefault('qualifiers', {})
    q['relation_candidate'] = is_relation
    q['relation_candidate_note'] = RELATION_NOTE if is_relation else NONRELATION_NOTE


def add_statement(suffix, subject, obj, predicate, line_no, claim, quote,
                  candidate_ids, qualification, is_relation, marker=None,
                  speaker='Haskell', layer='authorial narration'):
    line = source_lines[line_no - 1]
    if quote not in line:
        raise ValueError(f'quote absent from source L{line_no}: {quote!r}')
    q = {
        'source_line_start': line_no,
        'source_line_end': line_no,
        'printed_page': 135,
        'pdf_physical_page': 16,
        'claim': claim,
        'speaker': speaker,
        'text_layer': layer,
        'qualification': qualification,
        'mentioned_candidate_ids': candidate_ids,
        'relation_candidate': is_relation,
        'relation_candidate_note': RELATION_NOTE if is_relation else NONRELATION_NOTE,
    }
    if marker is not None:
        q.update({
            'footnote_marker': marker,
            'footnote_target_line': {1: 134, 2: 135, 3: 136, 4: 137, 5: 138}[marker],
            'footnote_segment': 'chp-5:05_CHP-5_sec_iii:l126-165',
            'footnote_link_status': 'pending_source_migration',
        })
    return {
        'statement_id': f'st-chp5-p135-{suffix}',
        'segment_id': SEG,
        'subject_candidate_id': subject,
        'object_candidate_id': obj,
        'predicate': predicate,
        'qualifiers': q,
        'original_quote': quote,
        'origin': 'book',
        'source_file': '02-sources/02-Markdown/05_CHP-5_sec_iii.md',
    }


source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()


def segment_span(line_no, surface, occurrence=0):
    line = source_lines[line_no - 1]
    start = -1
    for _ in range(occurrence + 1):
        start = line.find(surface, start + 1)
        if start < 0:
            raise ValueError(f'missing surface on L{line_no}: {surface!r}')
    base = len('\n'.join(source_lines[27:line_no - 1]))
    if line_no > 28:
        base += 1
    return base + start, base + start + len(surface)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after all guarded checks pass')
    args = parser.parse_args()

    for path, expected in EXPECTED_SHA256.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f'precondition failed: {path.relative_to(ROOT)} sha256={actual}')

    statement_lines = STATEMENTS.read_text(encoding='utf-8-sig').splitlines()
    statements = [json.loads(line) for line in statement_lines if line.strip()]
    statement_fields = None
    ids = [r['statement_id'] for r in statements]
    if len(ids) != len(set(ids)):
        raise SystemExit('duplicate statement ids in source table')
    by_id = {r['statement_id']: r for r in statements}
    if not TARGET_IDS.issubset(by_id):
        raise SystemExit(f'missing target statements: {sorted(TARGET_IDS - set(by_id))}')
    target_rows = [by_id[sid] for sid in sorted(TARGET_IDS)]
    if any(r.get('segment_id') != SEG for r in target_rows):
        raise SystemExit('target statement segment mismatch')
    if any(r.get('qualifiers', {}).get('relation_candidate') is not None for r in target_rows):
        raise SystemExit('one or more target statements are no longer unclassified')

    candidate_fields, candidates = load_csv(CANDIDATES)
    mention_fields, mentions = load_csv(MENTIONS)
    existing_candidate_ids = {r['candidate_id'] for r in candidates}
    new_candidate_ids = {f'cand-{i}' for i in range(11914, 11919)}
    if existing_candidate_ids & new_candidate_ids:
        raise SystemExit('one or more new candidate IDs already exist')
    existing_mention_ids = {r['mention_id'] for r in mentions}
    new_mention_ids = {f'm-chp5-sec-iii-l28-34-{i:03d}' for i in range(30, 38)}
    if existing_mention_ids & new_mention_ids:
        raise SystemExit('one or more new mention IDs already exist')

    candidate_specs = [
        ('cand-11914', "Unidentified Pieter Van Laer paintings admired and sought by painters", 'work',
         'Unnamed works whose realism painters reportedly admired and sought as examples; no individual title is given.', 32),
        ('cand-11915', "Two unidentified Pieter Van Laer paintings owned by Hermann Swanevelt", 'work',
         'A pair of pictures reported as owned by Swanevelt; neither is identified by title in the body.', 32),
        ('cand-11916', "Unidentified early Bamboccianti works possibly owned by Pietro Testa", 'work',
         'Unspecified examples of early Bamboccianti work; Testa’s possible ownership remains Haskell’s qualified inference.', 32),
        ('cand-11917', "Small peasant and animal scenes by Pieter Van Laer", 'work',
         'Unidentified small scenes which Haskell says Van Laer evidently sold; Corpus Domini fairs are only a possible channel, dealers a stated channel.', 30),
        ('cand-11918', "Pieter Van Laer’s Northern compatriots (unnamed group)", 'term',
         'Unnamed compatriots whom Haskell infers must have been prominent among the painters who admired Van Laer’s works.', 32),
    ]
    new_candidates = []
    for cid, name, typ, detail, line_no in candidate_specs:
        new_candidates.append({
            'candidate_id': cid,
            'index_entry_id': '',
            'canonical_name': name,
            'index_page_range': '',
            'suggested_type': typ,
            'status': 'open',
            'index_source_file': '',
            'sub_entry': '',
            'detail': detail,
            'exclude_reason': '',
            'candidate_origin': 'body-mention',
            'candidate_source_ref': f'{SEG}#L{line_no}',
        })

    for row in candidates:
        if row.get('candidate_source_ref', '').startswith(SEG + '#L'):
            ref = row['candidate_source_ref'].split('#L', 1)[1]
            if not ref.isdigit():
                raise SystemExit(f'invalid existing source ref: {row}')
    existing_natural = {(r.get('canonical_name'), r.get('suggested_type')) for r in candidates}
    for row in new_candidates:
        if (row['canonical_name'], row['suggested_type']) in existing_natural:
            raise SystemExit(f'duplicate candidate natural key: {row["candidate_id"]}')

    # Correct mixed claims and relation endpoints while preserving existing identifiers.
    def revise(sid, *, subject=None, obj='__keep__', predicate=None, claim=None,
               quote=None, candidate_ids=None, qualification=None, line=None,
               marker='__keep__', speaker=None, layer=None, is_relation):
        row = by_id[sid]
        q = row['qualifiers']
        if subject is not None:
            row['subject_candidate_id'] = subject
        if obj != '__keep__':
            row['object_candidate_id'] = obj
        if predicate is not None:
            row['predicate'] = predicate
        if claim is not None:
            q['claim'] = claim
        if quote is not None:
            row['original_quote'] = quote
        if candidate_ids is not None:
            q['mentioned_candidate_ids'] = candidate_ids
        if qualification is not None:
            q['qualification'] = qualification
        if line is not None:
            q['source_line_start'] = line
            q['source_line_end'] = line
        if marker != '__keep__':
            if marker is None:
                for key in ('footnote_marker', 'footnote_target_line', 'footnote_segment', 'footnote_link_status'):
                    q.pop(key, None)
            else:
                q['footnote_marker'] = marker
                q['footnote_target_line'] = {1: 134, 2: 135, 3: 136, 4: 137, 5: 138}[marker]
                q['footnote_segment'] = 'chp-5:05_CHP-5_sec_iii:l126-165'
                q['footnote_link_status'] = 'pending_source_migration'
        if speaker is not None:
            q['speaker'] = speaker
        if layer is not None:
            q['text_layer'] = layer
        relation(row, is_relation)

    revise('st-chp5-p135-carracci-works-incidental-to-orthodox-career', is_relation=False)
    revise('st-chp5-p135-cassiano-may-have-owned-van-laer-picture', is_relation=True)
    revise('st-chp5-p135-giustiniani-acquired-two-uncharacteristic-van-laer-pictures',
           obj='cand-1352', predicate='acquired_work',
           claim='Haskell says Giustiniani acquired the Landscape with figures and animals, one of two rather uncharacteristic Van Laer examples.',
           quote='a Landscape with figures and animals', candidate_ids=['cand-1200', 'cand-1351', 'cand-1352'],
           qualification='This statement records the first named work; the second acquisition is recorded separately. “Uncharacteristic” is Haskell’s description.', line=33, is_relation=True)
    revise('st-chp5-p135-giustiniani-protected-caravaggios-northern-followers', is_relation=True)
    revise('st-chp5-p135-influential-roman-patrons-took-cautious-interest', is_relation=True)
    revise('st-chp5-p135-no-real-forerunners-and-difficulty-of-breaking-categories', is_relation=False)
    revise('st-chp5-p135-northern-compatriots-among-van-laer-admirers',
           subject='cand-11918', obj='cand-6128', predicate='likely_leading_members_of_admirer_group',
           claim='Haskell infers that Van Laer’s Northern compatriots must have been prominent among the painters who admired his work.',
           candidate_ids=['cand-11918', 'cand-6128', 'cand-1351'],
           qualification='“Must have been” marks Haskell’s inference; the unnamed group and likely membership are not independently established.', is_relation=True)
    revise('st-chp5-p135-painters-admired-van-laer-as-model-of-reality',
           obj='cand-11914', predicate='admired_van_laer_paintings',
           claim='Haskell reports through Passeri that painters, including some of reputation, looked with delight at Van Laer’s pictures.',
           quote='even those of some reputation looked at his pictures with great delight',
           candidate_ids=['cand-6128', 'cand-11914', 'cand-1351'],
           qualification='Nested testimony reported by Haskell and cited to Passeri; the painters and pictures remain unidentified.',
           speaker='Other painters, as reported by Haskell', layer='quoted testimony reported by Haskell', is_relation=True)
    revise('st-chp5-p135-simonelli-temporarily-owned-and-exchanged-two-pictures',
           obj='cand-6130', predicate='temporarily_owned_and_exchanged_work',
           claim='Haskell says Simonelli briefly owned Van Laer’s painting showing a peasant with a lamb and a dog, then exchanged the pair of pictures for something else.',
           quote='owned two for a short time—one showing a peasant with a lamb and a dog',
           candidate_ids=['cand-2434', 'cand-1351', 'cand-6130', 'cand-6131'],
           qualification='This row identifies the first of the two works; the second work is recorded separately. The exchange counterpart is unspecified.',
           marker=5, is_relation=True)
    revise('st-chp5-p135-swanevelt-owned-two-van-laer-pictures',
           obj='cand-11915', predicate='owned_two_pictures_by_van_laer',
           claim='Haskell reports that Hermann Swanevelt owned two unidentified pictures by Van Laer.',
           quote='Hermann Swanevelt, the Dutch landscape painter, owned two',
           candidate_ids=['cand-2535', 'cand-11915', 'cand-1351'],
           qualification='The pictures are not individually identified; footnote 3 refers to Swanevelt’s testimony in a case and reports an accusation, not an adjudicated finding.',
           marker=3, is_relation=True)
    revise('st-chp5-p135-testa-connected-to-early-bamboccianti-and-may-have-owned-work',
           obj='cand-0173', predicate='in_touch_with_early_bamboccianti',
           claim='Haskell says Pietro Testa was in touch with the world of the early Bamboccianti.',
           quote='was in touch with the world of the early bamboccianti',
           candidate_ids=['cand-2556', 'cand-0173'],
           qualification='The source states this connection directly; Testa’s possible ownership of works is recorded separately.',
           marker=4, is_relation=True)
    revise('st-chp5-p135-van-laer-arrived-in-rome-1625', is_relation=True)
    revise('st-chp5-p135-van-laer-associated-with-schildersbent',
           predicate='associated_with',
           claim='Haskell says Van Laer associated in Rome with the newly formed schildersbent.',
           quote='associated with the newly formed schildersbent',
           candidate_ids=['cand-1351', 'cand-4490', 'cand-6127'],
           qualification='Do not assume identity with the Bentvueghels group from another chapter before S3.', is_relation=True)
    revise('st-chp5-p135-van-laer-buyers-hard-to-identify', is_relation=False)
    revise('st-chp5-p135-van-laer-cut-off-from-official-patronage', is_relation=False)
    revise('st-chp5-p135-van-laer-dedicated-eight-animal-engravings',
           subject='cand-6132', obj='cand-2139', predicate='dedicated_to',
           claim='Haskell says Van Laer dedicated his series of eight animal engravings to Don Ferdinando.',
           quote='the artist dedicated a series of eight engravings of animals to Don Ferdinando',
           candidate_ids=['cand-1351', 'cand-4490', 'cand-6132', 'cand-2139'],
           qualification='The dedicatee’s full name and office continue at p.136 L37; identity alignment remains an S3 task.', line=34, is_relation=True)
    revise('st-chp5-p135-van-laer-expensive-reputation', is_relation=False)
    revise('st-chp5-p135-van-laer-grew-up-in-haarlem',
           claim='Haskell says Van Laer grew up in the Protestant town of Haarlem.',
           quote='He had grown up in the Protestant town of Haarlem',
           candidate_ids=['cand-1351', 'cand-6125'],
           qualification='Haskell’s characterization of Haarlem’s painting tradition is recorded as a separate scalar claim.', line=30, is_relation=True)
    revise('st-chp5-p135-van-laer-picture-price', is_relation=False)
    revise('st-chp5-p135-van-laer-sold-small-scenes-through-fairs-and-dealers',
           obj='cand-11917', predicate='sold_work',
           claim='Haskell says Van Laer evidently sold his small scenes of peasant and animal life through whatever channels were available.',
           quote='he evidently sold his little scenes of peasant and animal life',
           candidate_ids=['cand-1351', 'cand-11917'],
           qualification='“Evidently” is retained. The possible Corpus Domini fair channel and stated dealer channel are split into separate claims.',
           line=30, is_relation=True)

    new_statements = [
        add_statement('giustiniani-acquired-st-eustace-hunting', 'cand-1200', 'cand-1354', 'acquired_work', 33,
                      'Haskell says Giustiniani acquired a small scene of St Eustace hunting, the second of two rather uncharacteristic Van Laer examples.',
                      'a small scene of St Eustace hunting', ['cand-1200', 'cand-1351', 'cand-1354'],
                      'This is the second named work in the pair; “uncharacteristic” is Haskell’s description.', True),
        add_statement('giustiniani-left-pictures-unframed', 'cand-1200', None, 'left_acquired_pictures_unframed', 33,
                      'Haskell says Giustiniani did not bother to frame the two pictures.',
                      'though he did not bother to frame them', ['cand-1200', 'cand-1352', 'cand-1354'],
                      '“Them” refers to the Landscape with figures and animals and the St Eustace hunting scene.', False),
        add_statement('painters-tried-to-possess-van-laer-works', 'cand-6128', 'cand-11914', 'sought_to_acquire_work_as_example', 32,
                      'Haskell reports through Passeri that painters tried to possess some of Van Laer’s pictures as examples of realistic expression.',
                      'tried to possess some for themselves as examples of how to express reality so well', ['cand-6128', 'cand-11914', 'cand-1351'],
                      'Nested testimony reported by Haskell and cited to Passeri; “some” does not identify particular works.', True, marker=2,
                      speaker='Other painters, as reported by Haskell', layer='quoted testimony reported by Haskell'),
        add_statement('simonelli-owned-and-exchanged-night-scene', 'cand-2434', 'cand-6131', 'temporarily_owned_and_exchanged_work', 32,
                      'Haskell says Simonelli briefly owned Van Laer’s night scene, then exchanged the pair of pictures for something else.',
                      'the other a night scene', ['cand-2434', 'cand-1351', 'cand-6130', 'cand-6131'],
                      'This row identifies the second of the two works; the exchange counterpart is unspecified.', True, marker=5),
        add_statement('testa-may-have-owned-bamboccianti-works', 'cand-2556', 'cand-11916', 'may_have_owned_work', 32,
                      'Haskell says Pietro Testa may have owned examples of early Bamboccianti work.',
                      'may therefore have owned examples of their work', ['cand-2556', 'cand-11916', 'cand-0173'],
                      '“May” preserves Haskell’s inference; the works are not identified.', True, marker=4),
        add_statement('van-laer-bohemian-lifestyle', 'cand-1351', None, 'lived_typically_bohemian_existence', 30,
                      'Haskell characterizes Van Laer’s way of life in Rome as the typically bohemian existence of schildersbent members.',
                      'lived the typically ‘bohemian’ existence of its members', ['cand-1351', 'cand-6127'],
                      'This is Haskell’s characterization of lifestyle; the group association is recorded separately.', False),
        add_statement('haarlem-realistic-painting-tradition', 'cand-6126', None, 'firmly_established_local_painting_tradition', 30,
                      'Haskell says a tradition of realistic painting was firmly established in Haarlem and characterizes it as free from aristocratic or idealistic prejudice.',
                      'a tradition of‘realistic’ painting was firmly established', ['cand-6125', 'cand-6126'],
                      'This records Haskell’s contextual description of Haarlem, not an independently established generalization.', False),
        add_statement('van-laer-may-have-sold-scenes-at-corpus-domini', 'cand-1351', 'cand-6024', 'possibly_sold_at_fairs_of', 30,
                      'Haskell says Van Laer may have sold his small scenes at the fairs of Corpus Domini.',
                      'at the fairs of Corpus Domini, perhaps', ['cand-1351', 'cand-11917', 'cand-6024'],
                      '“Perhaps” is retained; this is a possible sales channel, not a confirmed transaction.', True),
        add_statement('van-laer-sold-scenes-to-art-dealers', 'cand-1351', 'cand-0125', 'sold_work_to_dealers', 30,
                      'Haskell says Van Laer certainly sold his small scenes of peasant and animal life to dealers.',
                      'certainly to dealers', ['cand-1351', 'cand-11917', 'cand-0125'],
                      'The source states this channel more firmly than the possible Corpus Domini fairs; it names no dealer or individual transaction.', True),
        add_statement('admired-works-created-by-van-laer', 'cand-11914', 'cand-1351', 'created_by', 32,
                      'The pictures admired and sought by the painters are identified in the passage as Van Laer’s works.',
                      'his pictures', ['cand-11914', 'cand-1351'],
                      'The possessive reference is resolved to Pieter Van Laer from the immediately preceding paragraph.', True),
        add_statement('swanevelt-pictures-by-van-laer', 'cand-11915', 'cand-1351', 'created_by', 32,
                      'The two pictures in Swanevelt’s ownership are identified in context as works by Van Laer.',
                      'Hermann Swanevelt, the Dutch landscape painter, owned two', ['cand-11915', 'cand-2535', 'cand-1351'],
                      'The owner statement is explicit; the attribution depends on the paragraph context and is corroborated by note 3, pending its S2 processing.', True, marker=3),
        add_statement('testa-works-are-early-bamboccianti', 'cand-11916', 'cand-0173', 'work_of_group', 32,
                      'The works Testa may have owned are described as examples of the early Bamboccianti’s work.',
                      'examples of their work', ['cand-11916', 'cand-0173', 'cand-2556'],
                      '“Their” refers to the early Bamboccianti; Testa’s ownership remains qualified in a separate statement.', True, marker=4),
        add_statement('simonelli-peasant-scene-by-van-laer', 'cand-6130', 'cand-1351', 'created_by', 32,
                      'The peasant scene in Simonelli’s temporary possession is identified as one of Van Laer’s pictures.',
                      'one showing a peasant with a lamb and a dog', ['cand-6130', 'cand-2434', 'cand-1351'],
                      'Attribution is resolved from the surrounding discussion of Van Laer’s pictures.', True, marker=5),
        add_statement('simonelli-night-scene-by-van-laer', 'cand-6131', 'cand-1351', 'created_by', 32,
                      'The night scene in Simonelli’s temporary possession is identified as one of Van Laer’s pictures.',
                      'the other a night scene', ['cand-6131', 'cand-2434', 'cand-1351'],
                      'Attribution is resolved from the surrounding discussion of Van Laer’s pictures.', True, marker=5),
        add_statement('giustiniani-landscape-by-van-laer', 'cand-1352', 'cand-1351', 'created_by', 33,
                      'The Landscape with figures and animals acquired by Giustiniani is identified as a Van Laer example.',
                      'a Landscape with figures and animals', ['cand-1352', 'cand-1351', 'cand-1200'],
                      'The attribution follows the paragraph’s explicit referent, two examples by Van Laer.', True),
        add_statement('giustiniani-st-eustace-by-van-laer', 'cand-1354', 'cand-1351', 'created_by', 33,
                      'The St Eustace hunting scene acquired by Giustiniani is identified as a Van Laer example.',
                      'a small scene of St Eustace hunting', ['cand-1354', 'cand-1351', 'cand-1200'],
                      'The attribution follows the paragraph’s explicit referent, two examples by Van Laer.', True),
        add_statement('small-scenes-created-by-van-laer', 'cand-11917', 'cand-1351', 'created_by', 30,
                      'The small scenes of peasant and animal life sold by the artist are Van Laer’s works.',
                      'his little scenes of peasant and animal life', ['cand-11917', 'cand-1351'],
                      'The possessive reference is explicit in the sentence about Van Laer.', True),
    ]

    new_statement_ids = {r['statement_id'] for r in new_statements}
    if len(new_statement_ids) != len(new_statements) or set(by_id) & new_statement_ids:
        raise SystemExit('new statement ID collision')
    if set(new_statement_ids) & TARGET_IDS:
        raise SystemExit('new statement ID collides with target')

    # Redirect the source mention for the inferred compatriot group and append exact spans.
    mention_by_id = {r['mention_id']: r for r in mentions}
    compatriot_mention = mention_by_id['m-chp5-sec-iii-l28-34-012']
    if compatriot_mention['candidate_id'] != 'cand-6128':
        raise SystemExit('unexpected existing Northern compatriots mention target')
    compatriot_mention['candidate_id'] = 'cand-11918'
    mention_specs = [
        ('cand-11914', 32, 'his pictures', 'The Van Laer pictures admired in the reported testimony.'),
        ('cand-11914', 32, 'some for themselves', 'Unspecified works the painters tried to possess.'),
        ('cand-11915', 32, 'owned two', 'The number of unidentified Van Laer pictures in Swanevelt’s ownership.'),
        ('cand-11916', 32, 'examples of their work', 'Unidentified works of the early Bamboccianti.'),
        ('cand-6128', 32, 'these admirers', 'Anaphoric reference to the painters who admired Van Laer’s pictures.'),
        ('cand-11917', 30, 'his little scenes of peasant and animal life', 'Small works attributed to Van Laer.'),
        ('cand-0125', 30, 'dealers', 'Unspecified art dealers named as a sales channel.'),
    ]
    new_mentions = []
    for i, (candidate_id, line_no, surface, note) in enumerate(mention_specs, 30):
        start, end = segment_span(line_no, surface)
        new_mentions.append({
            'mention_id': f'm-chp5-sec-iii-l28-34-{i:03d}',
            'segment_id': SEG,
            'candidate_id': candidate_id,
            'surface_form': surface,
            'start_char': str(start),
            'end_char': str(end),
            'note': note,
        })

    # Carry the precise body split into the existing note-to-body links.
    note_ids = {r['statement_id']: r for r in statements
                if r.get('segment_id') == 'chp-5:05_CHP-5_sec_iii:l126-165'}
    note_links = {
        'st-chp5-notes-l135-passeri-p74': 'st-chp5-p135-painters-tried-to-possess-van-laer-works',
        'st-chp5-notes-l137-ibid-page134': 'st-chp5-p135-testa-may-have-owned-bamboccianti-works',
        'st-chp5-notes-l138-ibid-page133': 'st-chp5-p135-simonelli-owned-and-exchanged-night-scene',
    }
    for note_id, body_id in note_links.items():
        if note_id not in note_ids:
            raise SystemExit(f'missing footnote statement: {note_id}')
        q = note_ids[note_id].setdefault('qualifiers', {})
        links = q.setdefault('linked_body_statement_ids', [])
        if body_id not in links:
            links.append(body_id)

    # Validate every new quote, span, endpoint, and source reference before preview/write.
    for row in new_statements:
        q = row['qualifiers']
        ln = q['source_line_start']
        if row['original_quote'] not in source_lines[ln - 1]:
            raise SystemExit(f'new quote failed source check: {row["statement_id"]}')
        if q['relation_candidate'] and (not row['subject_candidate_id'] or not row['object_candidate_id']):
            raise SystemExit(f'relation candidate missing endpoint: {row["statement_id"]}')
    for row in new_mentions:
        start, end = int(row['start_char']), int(row['end_char'])
        segment_text = '\n'.join(source_lines[27:34])
        if segment_text[start:end] != row['surface_form']:
            raise SystemExit(f'mention span mismatch: {row["mention_id"]}')
    for row in new_candidates:
        if not row['candidate_source_ref'].endswith(f'#L{next(l for c,n,t,d,l in candidate_specs if c == row["candidate_id"])}'):
            raise SystemExit(f'candidate source reference mismatch: {row["candidate_id"]}')

    if args.apply:
        paths = [STATEMENTS, CANDIDATES, MENTIONS]
        backups = [p.with_name(p.name + BACKUP_TAG) for p in paths]
        if any(p.exists() for p in backups):
            raise SystemExit('backup already exists; refusing to overwrite')
        for source, backup in zip(paths, backups):
            shutil.copy2(source, backup)
        candidates.extend({key: row.get(key, '') for key in candidate_fields} for row in new_candidates)
        mentions.extend({key: row.get(key, '') for key in mention_fields} for row in new_mentions)
        statements.extend(new_statements)
        temp_paths = [p.with_name(p.name + '.tmp-s2-chp5-p135') for p in paths]
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
        print('applied p.135 S2 semantic corrections')
        print('backups:', ', '.join(p.name for p in backups))
    else:
        print('PREVIEW only; no table writes')
    print(f'targets classified: {len(TARGET_IDS)}')
    print('new candidates:', ', '.join(r['candidate_id'] for r in new_candidates))
    print('new statements:', len(new_statements))
    print('new mentions:', len(new_mentions), '; remapped existing mentions: 1')
    print('footnote body-link additions:', len(note_links))


if __name__ == '__main__':
    main()
