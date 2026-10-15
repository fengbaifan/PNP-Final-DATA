import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l36-43'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
STATEMENTS = ROOT / '04-knowledge/tables/book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge/tables/entity-candidates.csv'
MENTIONS = ROOT / '04-knowledge/tables/mentions.csv'
BACKUP_TAG = '.bak-s2-chp5-p136-20261013'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: 'de605c80d57fae5c849bd19ae654f2397b3c9775c46cb1520f3e84ff3a76c978',
    CANDIDATES: '689a93e80a8cd183a3906fdc0eb1d4d4e7979cbab8cdfe6f58b7d5e407d62b2f',
    MENTIONS: '052888ed7b2c147069a10b393ed8b7775dcc875cabda585da0e5f0918c065c04',
}

TARGET_IDS = {
    'st-chp5-p136-cerquozzi-admired-by-fellow-artists-and-close-friends',
    'st-chp5-p136-cerquozzi-among-artists-exploiting-demand-and-roman-born',
    'st-chp5-p136-cerquozzi-and-velasquez-painted-for-colonna',
    'st-chp5-p136-cerquozzi-career-linked-to-spain-and-supporters',
    'st-chp5-p136-cerquozzi-encouraged-potential-rival-borgognone',
    'st-chp5-p136-cerquozzi-first-successes-for-spanish-embassy-official',
    'st-chp5-p136-cerquozzi-illustrates-limits-on-realistic-painting',
    'st-chp5-p136-cerquozzi-important-admirers-from-professional-classes',
    'st-chp5-p136-cerquozzi-may-have-been-employed-at-embassy-with-velasquez-stay',
    'st-chp5-p136-cerquozzi-nationality-eased-patron-contact',
    'st-chp5-p136-cerquozzi-on-excellent-terms-with-cortona',
    'st-chp5-p136-cerquozzi-probably-sold-cheaply-before-connoisseur-attention',
    'st-chp5-p136-cerquozzi-taken-up-by-leading-aristocratic-families',
    'st-chp5-p136-cerquozzi-wore-spanish-dress',
    'st-chp5-p136-complete-don-ferdinando-identification',
    'st-chp5-p136-marchesi-lawyer-and-beneficiary-of-cerquozzi-bequest',
    'st-chp5-p136-neri-and-friends-immortalised-in-plate-22a',
    'st-chp5-p136-spaniards-associated-with-bamboccianti-success',
    'st-chp5-p136-van-laer-clientele-was-anonymous-middle-status-group',
    'st-chp5-p136-van-laer-demand-large-and-rewarding-by-departure',
    'st-chp5-p136-van-laer-impact-on-rome-and-european-painting',
    'st-chp5-p136-van-laer-remained-on-social-fringes',
    'st-chp5-p136-velasquez-guest-of-monterey-in-1630',
}

RELATION_NOTE = (
    'Source-grounded S2 relation candidate; source qualification is retained, '
    'and no formal S6 edge is created.'
)
NONRELATION_NOTE = (
    'This is a scalar, contextual, or interpretive assertion rather than a '
    'specific entity relation.'
)

source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()


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


def classify(row, is_relation):
    q = row.setdefault('qualifiers', {})
    q['relation_candidate'] = is_relation
    q['relation_candidate_note'] = RELATION_NOTE if is_relation else NONRELATION_NOTE


def segment_span(line_no, surface):
    line = source_lines[line_no - 1]
    start = line.find(surface)
    if start < 0:
        raise ValueError(f'missing surface on L{line_no}: {surface!r}')
    base = len('\n'.join(source_lines[35:line_no - 1]))
    if line_no > 36:
        base += 1
    return base + start, base + start + len(surface)


def add_statement(suffix, subject, obj, predicate, line_no, claim, quote,
                  candidate_ids, qualification, is_relation, marker=None,
                  speaker='Haskell', layer='authorial narration', extra=None):
    if quote not in source_lines[line_no - 1]:
        raise ValueError(f'quote absent from source L{line_no}: {quote!r}')
    q = {
        'source_line_start': line_no,
        'source_line_end': line_no,
        'printed_page': 136,
        'pdf_physical_page': 17,
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
            'footnote_target_line': {1: 139, 2: 139, 3: 140, 4: 141}[marker],
            'footnote_segment': 'chp-5:05_CHP-5_sec_iii:l126-165',
            'footnote_link_status': 'pending_source_migration',
        })
    if extra:
        q.update(extra)
    return {
        'statement_id': f'st-chp5-p136-{suffix}',
        'segment_id': SEG,
        'subject_candidate_id': subject,
        'object_candidate_id': obj,
        'predicate': predicate,
        'qualifiers': q,
        'original_quote': quote,
        'origin': 'book',
        'source_file': '02-sources/02-Markdown/05_CHP-5_sec_iii.md',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after all guarded checks pass')
    args = parser.parse_args()
    for path, expected in EXPECTED_SHA256.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f'precondition failed: {path.relative_to(ROOT)} sha256={actual}')

    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    ids = [r['statement_id'] for r in statements]
    if len(ids) != len(set(ids)):
        raise SystemExit('duplicate statement IDs in input')
    by_id = {r['statement_id']: r for r in statements}
    if not TARGET_IDS.issubset(by_id):
        raise SystemExit(f'missing targets: {sorted(TARGET_IDS - set(by_id))}')
    targets = [by_id[sid] for sid in sorted(TARGET_IDS)]
    if any(r.get('segment_id') != SEG for r in targets):
        raise SystemExit('target segment mismatch')
    if any(r.get('qualifiers', {}).get('relation_candidate') is not None for r in targets):
        raise SystemExit('one or more target statements are already classified')

    candidate_fields, candidates = load_csv(CANDIDATES)
    mention_fields, mentions = load_csv(MENTIONS)
    new_candidate_ids = {f'cand-{n}' for n in range(11919, 11924)}
    if {r['candidate_id'] for r in candidates} & new_candidate_ids:
        raise SystemExit('candidate ID collision')
    new_mention_ids = {f'm-chp5-sec-iii-l36-43-{n:03d}' for n in range(42, 47)}
    if {r['mention_id'] for r in mentions} & new_mention_ids:
        raise SystemExit('mention ID collision')

    candidate_specs = [
        ('cand-11919', "Painters ready to exploit demand for small genre paintings (unnamed group)",
         'A group Haskell says was ready to exploit the demand proven by Van Laer; Cerquozzi is then named as one of them.', 38),
        ('cand-11920', "Fellow artists who admired Michelangelo Cerquozzi (unnamed group)",
         'The fellow artists are not named in the admiration clause; Viola and Brandi are separately identified as his closest friends.', 40),
        ('cand-11921', "Leading aristocratic families who took up Michelangelo Cerquozzi (unnamed group)",
         'Haskell contrasts these families with those around the Barberini court. Do not equate the group automatically with the later Hispanophil clans or Colonna.', 42),
        ('cand-11922', "Connoisseurs who noticed Michelangelo Cerquozzi's pictures (unnamed group)",
         'Unspecified connoisseurs whom Haskell says Cerquozzi probably attracted after beginning to sell paintings cheaply to dealers.', 39),
        ('cand-11923', "People around the Barberini court who helped spread artists’ fame (unnamed group)",
         'Haskell contrasts this circle with the aristocratic families who took up Cerquozzi and says it helped spread the fame of Romanelli, Poussin, and Testa.', 42),
    ]
    new_candidates = [{
        'candidate_id': cid,
        'index_entry_id': '',
        'canonical_name': name,
        'index_page_range': '',
        'suggested_type': 'term',
        'status': 'open',
        'index_source_file': '',
        'sub_entry': '',
        'detail': detail,
        'exclude_reason': '',
        'candidate_origin': 'body-mention',
        'candidate_source_ref': f'{SEG}#L{line_no}',
    } for cid, name, detail, line_no in candidate_specs]

    # Correct compound claims and endpoints in the 23 existing records.
    def revise(sid, *, subject='__keep__', obj='__keep__', predicate=None,
               claim=None, quote=None, candidate_ids=None, qualification=None,
               line=None, marker='__keep__', is_relation):
        row = by_id[sid]
        q = row['qualifiers']
        if subject != '__keep__':
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
                q['footnote_target_line'] = {1: 139, 2: 139, 3: 140, 4: 141}[marker]
                q['footnote_segment'] = 'chp-5:05_CHP-5_sec_iii:l126-165'
                q['footnote_link_status'] = 'pending_source_migration'
        classify(row, is_relation)

    revise('st-chp5-p136-cerquozzi-admired-by-fellow-artists-and-close-friends',
           obj='cand-11920', predicate='admired_by_fellow_artists',
           claim='Haskell says Cerquozzi was much admired by fellow artists.',
           quote='He too was much admired by his fellow-artists',
           candidate_ids=['cand-0625', 'cand-11920'],
           qualification='The pronoun continues the Cerquozzi narrative; his two closest friends are recorded separately.', line=40, is_relation=True)
    revise('st-chp5-p136-cerquozzi-among-artists-exploiting-demand-and-roman-born',
           obj='cand-11919', predicate='member_of_demand_exploiting_group',
           claim='Haskell names Cerquozzi as one of the painters ready to exploit demand for Van Laer’s genre paintings.',
           quote='Among these was Michelangelo Cerquozzi',
           candidate_ids=['cand-0625', 'cand-11919', 'cand-1351'],
           qualification='“These” refers to the unnamed painters ready to exploit the demand. Roman birth is recorded separately.', marker=None, is_relation=True)
    revise('st-chp5-p136-cerquozzi-and-velasquez-painted-for-colonna',
           subject='cand-0625', obj='cand-4638', predicate='painted_bambocciate_for',
           claim='Haskell says there is some evidence that Cerquozzi painted Bambocciate for the Colonna, more likely during Velasquez’s second visit.',
           quote='Cerquozzi and Velasquez painted bambocciate for the most important of the Hispanophil clans in Rome, the Colonna',
           candidate_ids=['cand-0625', 'cand-2709', 'cand-6099', 'cand-6141', 'cand-4638'],
           qualification='“Some evidence” and “more likely” are retained; the work titles and exact visit are not established.', marker=4, line=43, is_relation=True)
    revise('st-chp5-p136-cerquozzi-career-linked-to-spain-and-supporters',
           subject='cand-0625', obj='cand-5120', predicate='career_closely_linked_to_spain',
           claim='Haskell says Cerquozzi’s career was closely linked to Spain.',
           quote='career was closely linked to Spain', candidate_ids=['cand-0625', 'cand-5120'],
           qualification='This is Haskell’s broad characterization. S0 punctuation around the following phrase is an OCR artifact; the print reads “her supporters in Rome,” recorded separately.', line=43, is_relation=True)
    revise('st-chp5-p136-cerquozzi-encouraged-potential-rival-borgognone',
           predicate='encouraged_potential_rival',
           claim='Haskell says Cerquozzi went out of his way to encourage his potential rival Giacomo Borgognone.',
           quote='went out of his way to encourage his potential rival Giacomo Borgognone',
           candidate_ids=['cand-0625', 'cand-0399'],
           qualification='“Potential rival” is Haskell’s characterization; the general statement about generosity to younger men is recorded separately.', is_relation=True)
    revise('st-chp5-p136-cerquozzi-first-successes-for-spanish-embassy-official',
           subject='cand-6139', obj='cand-6134', predicate='apparently_painted_for',
           claim='Haskell says Cerquozzi’s first great successes were apparently painted for an unnamed official at the Spanish Embassy.',
           quote='His first great successes were apparently painted for an official at the Spanish Embassy',
           candidate_ids=['cand-0625', 'cand-6139', 'cand-6134', 'cand-6135'],
           qualification='“Apparently” is retained; the works, official, and precise commission remain unidentified.', is_relation=True)
    revise('st-chp5-p136-cerquozzi-illustrates-limits-on-realistic-painting', is_relation=False)
    revise('st-chp5-p136-cerquozzi-important-admirers-from-professional-classes',
           predicate='admired_by_professional_classes',
           claim='Haskell says some of Cerquozzi’s most important admirers came from the professional classes.',
           quote='some of his most important admirers and patrons came from the professional classes',
           candidate_ids=['cand-0625', 'cand-6136'],
           qualification='The group is not enumerated; Raffaele Marchesi and Vincenzo Neri follow as examples. Patronage is recorded separately.', is_relation=True)
    revise('st-chp5-p136-cerquozzi-may-have-been-employed-at-embassy-with-velasquez-stay',
           predicate='may_have_been_employed_at_embassy_during_velasquez_visit',
           claim='Haskell considers it possible that Cerquozzi was employed at the Spanish Embassy when Velasquez stayed with Ambassador Monterey in 1630.',
           qualification='Both “possible” and “may” are retained; the employment and timing are unconfirmed.', marker=None, is_relation=True)
    revise('st-chp5-p136-cerquozzi-nationality-eased-patron-contact',
           obj=None, predicate='nationality_and_social_position_made_circumstances_easier',
           claim='Haskell says Cerquozzi’s nationality and social circumstances made his position much easier.',
           quote='his nationality, if nothing else, made his situation much easier',
           candidate_ids=['cand-0625'],
           qualification='This is Haskell’s causal interpretation; the comparative patron-contact claim is recorded separately.', line=39, is_relation=False)
    revise('st-chp5-p136-cerquozzi-on-excellent-terms-with-cortona', is_relation=True)
    revise('st-chp5-p136-cerquozzi-probably-sold-cheaply-before-connoisseur-attention',
           obj='cand-0125', predicate='probably_sold_pictures_cheaply_to_dealers',
           claim='Haskell says Cerquozzi probably began by selling his pictures cheaply to dealers.',
           quote='probably began by selling his pictures cheaply to dealers',
           candidate_ids=['cand-0625', 'cand-0125', 'cand-11922'],
           qualification='“Probably” is retained; attracting connoisseurs is recorded as a separate qualified relation.', line=39, marker=None, is_relation=True)
    revise('st-chp5-p136-cerquozzi-taken-up-by-leading-aristocratic-families',
           obj='cand-11921', predicate='taken_up_by_aristocratic_families',
           claim='Haskell says some leading aristocratic families took up Cerquozzi.',
           quote='taken up by some of the leading aristocratic families',
           candidate_ids=['cand-0625', 'cand-11921', 'cand-11923', 'cand-4970'],
           qualification='The source distinguishes this group from those around the Barberini court; do not equate it automatically with the Colonna or Hispanophil clans.', line=42, is_relation=True)
    revise('st-chp5-p136-cerquozzi-wore-spanish-dress', is_relation=False)
    revise('st-chp5-p136-complete-don-ferdinando-identification',
           claim='Page 136 completes the dedicatee introduced at p.135 L34: the source identifies Don Ferdinando as Afan de Ribera, Viceroy of Naples.',
           qualification='This is a source identity claim retained for S3 alignment; it is not a relationship edge.', is_relation=False)
    revise('st-chp5-p136-marchesi-lawyer-and-beneficiary-of-cerquozzi-bequest',
           subject='cand-0625', obj='cand-1538', predicate='bequeathed_unspecified_works_to',
           claim='Haskell identifies Raffaele Marchesi as a distinguished lawyer to whom Cerquozzi bequeathed some of his works.',
           candidate_ids=['cand-0625', 'cand-1538'],
           qualification='The bequest is attributed to Haskell; note 1 cites a published will but it has not been independently consulted.', is_relation=True)
    revise('st-chp5-p136-neri-and-friends-immortalised-in-plate-22a',
           subject='cand-6137', obj='cand-1735', predicate='depicts',
           claim='Haskell says Cerquozzi immortalised the doctor Vincenzo Neri in one of his finest paintings, Plate 22a.',
           quote='the doctor Vincenzo Neri whom with a group of other friends he immortalised',
           candidate_ids=['cand-0625', 'cand-1735', 'cand-6137'],
           qualification='The unnamed friends are represented as a separate group; this row identifies Neri as a sitter.', marker=2, line=41, is_relation=True)
    revise('st-chp5-p136-spaniards-associated-with-bamboccianti-success', is_relation=True)
    revise('st-chp5-p136-van-laer-clientele-was-anonymous-middle-status-group',
           predicate='clientele_mostly_from_middling_or_lower_status_group',
           qualification='“We must assume” marks Haskell’s inference; the passage contrasts this clientele with great princes and learned patrons.', is_relation=True)
    revise('st-chp5-p136-van-laer-demand-large-and-rewarding-by-departure',
           claim='By the time Van Laer left Rome, Haskell says demand for his small genre paintings had proved large and rewarding.',
           quote='he had proved that the demand for his little genre paintings was large and rewarding',
           candidate_ids=['cand-1351', 'cand-4490'],
           qualification='The departure date is approximately 1639; the general claim about many painters ready to exploit the demand is recorded separately.', is_relation=False)
    revise('st-chp5-p136-van-laer-impact-on-rome-and-european-painting', is_relation=False)
    revise('st-chp5-p136-van-laer-remained-on-social-fringes', is_relation=False)
    revise('st-chp5-p136-velasquez-guest-of-monterey-in-1630',
           predicate='stayed_as_guest_of_ambassador_monterey_in_1630',
           qualification='The print confirms 1630 followed by footnote 3; the event is separately linked to its named host.',
           marker=3, is_relation=True)

    new_statements = [
        add_statement('cerquozzi-born-in-rome', 'cand-0625', 'cand-4490', 'born_in', 39,
                      'Haskell identifies Michelangelo Cerquozzi as Roman by birth.', 'a Roman by birth',
                      ['cand-0625', 'cand-4490'], 'Direct biographical statement; footnote 1 points to biographical sources.', True, marker=1),
        add_statement('many-painters-ready-to-exploit-demand', 'cand-11919', None, 'many_ready_to_exploit_painting_demand', 38,
                      'Haskell says many painters were ready to exploit the demand for Van Laer’s small genre paintings.',
                      'There were many ready to exploit it', ['cand-11919', 'cand-1351'],
                      'The group is unnamed; this records the author’s general statement without inventing members.', False),
        add_statement('van-laer-left-rome-about-1639', 'cand-1351', 'cand-4490', 'left_rome_around_1639', 38,
                      'Haskell says Van Laer left Rome at about 1639.', 'By the time he left Rome in about 1639',
                      ['cand-1351', 'cand-4490'], 'The year is approximate, as stated in the source.', True, extra={'time': 'about 1639'}),
        add_statement('cerquozzi-closer-patron-contact-than-van-laer', 'cand-0625', None, 'comparatively_closer_contact_with_patrons_than_foreigner', 39,
                      'Haskell says Cerquozzi had closer contact with his patrons than had been possible for a foreigner such as Van Laer.',
                      'brought him into far closer contact with his patrons than had been possible for a foreigner such as Van Laer',
                      ['cand-0625', 'cand-1351'], 'This is Haskell’s comparative explanation, not a specific relation to an identified patron.', False),
        add_statement('cerquozzi-first-successes-created-by-artist', 'cand-6139', 'cand-0625', 'created_by', 42,
                      'The unidentified first successful paintings are Cerquozzi’s works.', 'His first great successes',
                      ['cand-6139', 'cand-0625'], 'The possessive reference identifies Cerquozzi as the artist.', True),
        add_statement('embassy-official-affiliated-with-embassy', 'cand-6134', 'cand-6135', 'official_at', 42,
                      'The unnamed official for whom Cerquozzi’s first great successes were apparently painted was at the Spanish Embassy.',
                      'an official at the Spanish Embassy', ['cand-6134', 'cand-6135'],
                      'The official’s identity is unknown; “at” is retained without inferring a specific office.', True),
        add_statement('cerquozzi-attracted-connoisseur-attention', 'cand-0625', 'cand-11922', 'attracted_attention_of_connoisseurs', 39,
                      'Haskell says Cerquozzi probably attracted the attention of connoisseurs after selling pictures cheaply to dealers.',
                      'before attracting the attention of connoisseurs', ['cand-0625', 'cand-11922', 'cand-0125'],
                      'The sequence and attention remain qualified by “probably” in the source sentence.', True),
        add_statement('cerquozzi-generous-to-younger-men', 'cand-0625', None, 'characterized_as_generous_to_younger_men', 41,
                      'Haskell characterizes Cerquozzi as always generous with younger men.',
                      'He was always generous with younger men', ['cand-0625'],
                      'This is a general authorial characterization; the specific encouragement of Borgognone is a separate relation.', False),
        add_statement('cerquozzi-close-friend-domenico-viola', 'cand-0625', 'cand-2776', 'close_friend_of', 40,
                      'Haskell identifies painter Domenico Viola as one of Cerquozzi’s two closest friends.',
                      'Domenico Viola', ['cand-0625', 'cand-2776'],
                      'The source names the relationship but does not provide dates or further context.', True),
        add_statement('cerquozzi-close-friend-giacinto-brandi', 'cand-0625', 'cand-0446', 'close_friend_of', 40,
                      'Haskell identifies painter Giacinto Brandi as one of Cerquozzi’s two closest friends.',
                      'Giacinto Brandi', ['cand-0625', 'cand-0446'],
                      'The source names the relationship but does not provide dates or further context.', True),
        add_statement('cerquozzi-patronized-by-professional-classes', 'cand-0625', 'cand-6136', 'patronized_by_professional_classes', 41,
                      'Haskell says some of Cerquozzi’s most important patrons came from the professional classes.',
                      'admirers and patrons came from the professional classes', ['cand-0625', 'cand-6136'],
                      'The class group is not enumerated; Marchesi and Neri follow as examples.', True),
        add_statement('leading-families-distinct-from-barberini-circle', 'cand-11921', 'cand-11923', 'distinct_from', 42,
                      'Haskell distinguishes the families who took up Cerquozzi from those who circled around the Barberini court.',
                      'of a kind rather different from those who circled round the Barberini court', ['cand-11921', 'cand-11923', 'cand-4970'],
                      'This preserves Haskell’s stated contrast without inferring that the later Colonna group exhausts the families.', True),
        add_statement('velasquez-painted-bambocciate-for-colonna', 'cand-2709', 'cand-4638', 'painted_bambocciate_for', 43,
                      'Haskell says there is some evidence that Velasquez painted Bambocciate for the Colonna, more likely during his second visit.',
                      'Cerquozzi and Velasquez painted bambocciate for the most important of the Hispanophil clans in Rome, the Colonna',
                      ['cand-2709', 'cand-0625', 'cand-6099', 'cand-6141', 'cand-4638'],
                      '“Some evidence” and “more likely” remain; retain the source spelling Velasquez and defer identity resolution to S3.', True, marker=4),
        add_statement('colonna-among-hispanophil-clans', 'cand-4638', 'cand-6141', 'member_of_hispanophil_clans', 43,
                      'Haskell names the Colonna as the most important of the Hispanophil clans in Rome.',
                      'the most important of the Hispanophil clans in Rome, the Colonna', ['cand-4638', 'cand-6141', 'cand-4490'],
                      'This is the source’s explicit group classification; it does not establish that the Colonna are the entire group.', True),
        add_statement('cerquozzi-career-linked-to-rome-supporters-of-spain', 'cand-0625', 'cand-6133', 'career_closely_linked_to_supporters_in_rome', 43,
                      'Haskell says Cerquozzi’s career was closely linked to Spain’s supporters in Rome.',
                      'her.supporters, in . Rome', ['cand-0625', 'cand-6133', 'cand-5120', 'cand-4490'],
                      'S0 punctuation is an OCR artifact; the print reads “her supporters in Rome.” The group remains unnamed and is not equated with the Spanish Embassy community.', True),
        add_statement('neri-was-a-doctor', 'cand-1735', None, 'identified_as_doctor', 41,
                      'Haskell identifies Vincenzo Neri as a doctor.', 'the doctor Vincenzo Neri', ['cand-1735'],
                      'Biographical role only; no institution is named.', False),
        add_statement('plate22a-painting-created-by-cerquozzi', 'cand-6137', 'cand-0625', 'created_by', 41,
                      'The painting referred to as Plate 22a is one of Cerquozzi’s paintings.',
                      'he immortalised in one of his finest paintings', ['cand-0625', 'cand-6137'],
                      'The source explicitly attributes the painting to Cerquozzi.', True, marker=2),
        add_statement('plate22a-depicts-unnamed-friends', 'cand-6137', 'cand-6138', 'depicts_group', 41,
                      'Cerquozzi’s Plate 22a painting also depicts an unnamed group of Neri’s friends.',
                      'a group of other friends', ['cand-6137', 'cand-1735', 'cand-6138'],
                      '“Other” distinguishes the unnamed friends from Vincenzo Neri, recorded separately.', True, marker=2),
        add_statement('velasquez-stay-hosted-by-monterey', 'cand-6140', 'cand-1693', 'hosted_by', 42,
                      'The 1630 stay described in the text was as a guest of Ambassador Monterey.',
                      'the Ambassador Monterey in 1630', ['cand-6140', 'cand-2709', 'cand-1693'],
                      'The source says Velasquez stayed as Monterey’s guest; no address is inferred.', True, marker=3, extra={'time': '1630'}),
        add_statement('barberini-circle-helped-spread-romanelli-fame', 'cand-11923', 'cand-2208', 'helped_spread_fame_of', 42,
                      'Haskell says people around the Barberini court helped spread the fame of Romanelli.',
                      'helped to spread the fame of artists such as Romanelli', ['cand-11923', 'cand-4970', 'cand-2208'],
                      'This is Haskell’s account of the circle’s role; membership remains unspecified.', True),
        add_statement('barberini-circle-helped-spread-poussin-fame', 'cand-11923', 'cand-1984', 'helped_spread_fame_of', 42,
                      'Haskell says people around the Barberini court helped spread the fame of Poussin.',
                      'helped to spread the fame of artists such as Romanelli, Poussin', ['cand-11923', 'cand-4970', 'cand-1984'],
                      'This is Haskell’s account of the circle’s role; membership remains unspecified.', True),
        add_statement('barberini-circle-helped-spread-testa-fame', 'cand-11923', 'cand-2556', 'helped_spread_fame_of', 42,
                      'Haskell says people around the Barberini court helped spread the fame of Testa.',
                      'helped to spread the fame of artists such as Romanelli, Poussin and Testa', ['cand-11923', 'cand-4970', 'cand-2556'],
                      'This is Haskell’s account of the circle’s role; membership remains unspecified.', True),
    ]

    # Add explicit continuation pointers across the p.135/p.136 page break.
    p135_id = 'st-chp5-p135-van-laer-dedicated-eight-animal-engravings'
    p136_id = 'st-chp5-p136-complete-don-ferdinando-identification'
    by_id[p135_id]['qualifiers']['continued_by'] = p136_id
    by_id[p136_id]['qualifiers']['continuation_of'] = p135_id

    # Tighten the friends group candidate and route index-subentry mentions to the person.
    candidate_by_id = {r['candidate_id']: r for r in candidates}
    friends = candidate_by_id['cand-6138']
    friends['canonical_name'] = "Unnamed friends represented with Vincenzo Neri in Cerquozzi’s Plate 22a painting"
    friends['detail'] = 'The depicted group consists of unnamed friends accompanying the separately identified doctor Vincenzo Neri; no additional member is named.'
    mention_by_id = {r['mention_id']: r for r in mentions}
    for mention_id in ('m-chp5-sec-iii-l36-43-033', 'm-chp5-sec-iii-l36-43-038'):
        if mention_by_id[mention_id]['candidate_id'] != 'cand-0634':
            raise SystemExit(f'unexpected candidate on {mention_id}')
        mention_by_id[mention_id]['candidate_id'] = 'cand-0625'
    mention_specs = [
        ('cand-11919', 38, 'many ready to exploit it', 'The unnamed painters ready to exploit the demonstrated demand.'),
        ('cand-11920', 40, 'his fellow-artists', 'Unnamed fellow artists described as admiring Cerquozzi.'),
        ('cand-11922', 39, 'connoisseurs', 'Unnamed connoisseurs whose attention Cerquozzi probably attracted.'),
        ('cand-11921', 42, 'some of the leading aristocratic families', 'Unnamed aristocratic families said to have taken up Cerquozzi.'),
        ('cand-11923', 42, 'those who circled round the Barberini court', 'Unnamed people in the court circle, distinguished from the families who took up Cerquozzi.'),
    ]
    new_mentions = []
    for idx, (candidate_id, line_no, surface, note) in enumerate(mention_specs, 42):
        start, end = segment_span(line_no, surface)
        new_mentions.append({
            'mention_id': f'm-chp5-sec-iii-l36-43-{idx:03d}',
            'segment_id': SEG,
            'candidate_id': candidate_id,
            'surface_form': surface,
            'start_char': str(start),
            'end_char': str(end),
            'note': note,
        })

    # Update existing note backlinks to the precise child claims created by the split.
    note_by_id = {r['statement_id']: r for r in statements
                  if r.get('segment_id') == 'chp-5:05_CHP-5_sec_iii:l126-165'}
    def replace_link(note_id, old, new):
        q = note_by_id[note_id].setdefault('qualifiers', {})
        links = q.setdefault('linked_body_statement_ids', [])
        links[:] = [new if value == old else value for value in links]
        if new not in links:
            links.append(new)
    def append_link(note_id, body_id):
        q = note_by_id[note_id].setdefault('qualifiers', {})
        links = q.setdefault('linked_body_statement_ids', [])
        if body_id not in links:
            links.append(body_id)
    replace_link('st-chp5-notes-l139-biographies',
                 'st-chp5-p136-cerquozzi-among-artists-exploiting-demand-and-roman-born',
                 'st-chp5-p136-cerquozzi-born-in-rome')
    replace_link('st-chp5-notes-l139-cerquozzi-will',
                 'st-chp5-p136-cerquozzi-among-artists-exploiting-demand-and-roman-born',
                 'st-chp5-p136-cerquozzi-born-in-rome')
    append_link('st-chp5-notes-l139-cerquozzi-will',
                'st-chp5-p136-marchesi-lawyer-and-beneficiary-of-cerquozzi-bequest')
    replace_link('st-chp5-notes-l141-ghezzi-velasco-pictures',
                 'st-chp5-p136-cerquozzi-and-velasquez-painted-for-colonna',
                 'st-chp5-p136-velasquez-painted-bambocciate-for-colonna')

    new_ids = {r['statement_id'] for r in new_statements}
    if len(new_ids) != len(new_statements) or set(ids) & new_ids:
        raise SystemExit('statement ID collision')
    if len(new_candidates) != len({r['candidate_id'] for r in new_candidates}):
        raise SystemExit('candidate ID collision within additions')
    existing_names = {(r.get('canonical_name'), r.get('suggested_type')) for r in candidates}
    if any((r['canonical_name'], r['suggested_type']) in existing_names for r in new_candidates):
        raise SystemExit('candidate natural key collision')

    for row in new_statements:
        q = row['qualifiers']
        if q['relation_candidate'] and not (row['subject_candidate_id'] and row['object_candidate_id']):
            raise SystemExit(f'relation candidate missing endpoint: {row["statement_id"]}')
        if row['original_quote'] not in source_lines[q['source_line_start'] - 1]:
            raise SystemExit(f'quote failed source check: {row["statement_id"]}')
    text = '\n'.join(source_lines[35:43])
    for row in new_mentions:
        if text[int(row['start_char']):int(row['end_char'])] != row['surface_form']:
            raise SystemExit(f'mention span failed: {row["mention_id"]}')
    for row in new_candidates:
        line_no = next(line for cid, _, _, line in candidate_specs if cid == row['candidate_id'])
        if row['candidate_source_ref'] != f'{SEG}#L{line_no}':
            raise SystemExit(f'candidate source ref failed: {row["candidate_id"]}')

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
        temp_paths = [p.with_name(p.name + '.tmp-s2-chp5-p136') for p in paths]
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
        print('applied p.136 S2 semantic corrections')
        print('backups:', ', '.join(p.name for p in backups))
    else:
        print('PREVIEW only; no table writes')
    print(f'targets classified: {len(TARGET_IDS)}')
    print('new candidates:', ', '.join(r['candidate_id'] for r in new_candidates))
    print('new statements:', len(new_statements))
    print('new mentions:', len(new_mentions), '; remapped existing mentions: 2')
    print('footnote/backlink corrections: 4')


if __name__ == '__main__':
    main()
