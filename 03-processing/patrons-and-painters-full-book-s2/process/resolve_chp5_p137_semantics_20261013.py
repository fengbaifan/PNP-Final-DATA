import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l70-80'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
STATEMENTS = ROOT / '04-knowledge/tables/book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge/tables/entity-candidates.csv'
MENTIONS = ROOT / '04-knowledge/tables/mentions.csv'
BACKUP_TAG = '.bak-s2-chp5-p137-20261013'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: '83a5f019ef9a7805e180e01c42731ea2966517a0be3dbbd4122fc20a96d34569',
    CANDIDATES: 'daae25e617b45bedcdaafe900bf19062aae7f230e4059ce178d034ca1b15e009',
    MENTIONS: '8d07e56fccec29a36f532859426ac67c5cef89df8551e0e19f4f265c33c7005f',
}

TARGET_IDS = {
    'st-chp5-p137-aristocratic-success-reflected-in-art',
    'st-chp5-p137-association-and-gradual-acceptance',
    'st-chp5-p137-carandini-spanish-alignment',
    'st-chp5-p137-careful-work-characterization-partial',
    'st-chp5-p137-carpegna-carandini-raggi-collectors',
    'st-chp5-p137-de-bello-farnese-campaigns',
    'st-chp5-p137-early-small-popular-pictures',
    'st-chp5-p137-families-contrast-barberini-circle',
    'st-chp5-p137-families-favored-subjects',
    'st-chp5-p137-families-stylistic-preferences',
    'st-chp5-p137-later-large-commissioned-pictures',
    'st-chp5-p137-miel-borgognone-strada-collaboration',
    'st-chp5-p137-patron-pressure-and-high-prices',
    'st-chp5-p137-patrons-spanish-sphere',
    'st-chp5-p137-private-life-dilemma-and-spanish-audience',
    'st-chp5-p137-raggi-admired-cerquozzi',
    'st-chp5-p137-raggi-genoese-spanish-cause',
    'st-chp5-p137-rapaccioli-boycotted-at-conclave',
    'st-chp5-p137-rapaccioli-death',
    'st-chp5-p137-rapaccioli-owned-cerquozzi-pictures',
}

RELATION_NOTE = (
    'Source-grounded S2 relation candidate; source qualification is retained, '
    'and no formal S6 edge is created.'
)
NONRELATION_NOTE = (
    'This is a scalar, contextual, or interpretive assertion rather than a '
    'specific entity relation.'
)
PENDING_CONTINUATION = 'st-chp5-p137-careful-work-characterization-partial'

source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()
segment_text = '\n'.join(source_lines[69:80])
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


def classify(row, is_relation):
    q = row.setdefault('qualifiers', {})
    q['relation_candidate'] = is_relation
    q['relation_candidate_note'] = RELATION_NOTE if is_relation else NONRELATION_NOTE


def revise(by_id, sid, *, subject=UNSET, object_=UNSET, predicate=None,
           claim=None, quote=None, candidates=None, qualification=None,
           line_start=None, line_end=None, relation=None):
    row = by_id[sid]
    q = row.setdefault('qualifiers', {})
    if subject is not UNSET:
        row['subject_candidate_id'] = subject
    if object_ is not UNSET:
        row['object_candidate_id'] = object_
    if predicate is not None:
        row['predicate'] = predicate
    if claim is not None:
        q['claim'] = claim
    if quote is not None:
        row['original_quote'] = quote
    if candidates is not None:
        q['mentioned_candidate_ids'] = candidates
    if qualification is not None:
        q['qualification'] = qualification
    if line_start is not None:
        q['source_line_start'] = line_start
    if line_end is not None:
        q['source_line_end'] = line_end
    if relation is not None:
        classify(row, relation)
    return row


def make_statement(suffix, subject, object_, predicate, line_start, line_end,
                   quote, claim, candidates, qualification, relation,
                   footnote_refs=None, extra_qualifiers=None):
    if quote not in '\n'.join(source_lines[line_start - 1:line_end]):
        raise ValueError(f'quote absent from source L{line_start}-L{line_end}: {quote!r}')
    q = {
        'source_line_start': line_start,
        'source_line_end': line_end,
        'printed_page': 137,
        'pdf_physical_page': 22,
        'claim': claim,
        'speaker': 'Haskell',
        'text_layer': 'authorial narration',
        'qualification': qualification,
        'mentioned_candidate_ids': candidates,
    }
    classify({'qualifiers': q}, relation)
    if footnote_refs:
        q.update({
            'footnote_target_line': 144 if any(x['marker'] == 3 for x in footnote_refs) else 143,
            'footnote_link_status': 'linked',
            'footnote_refs': footnote_refs,
        })
    if extra_qualifiers:
        q.update(extra_qualifiers)
    return {
        'statement_id': f'st-chp5-p137-{suffix}',
        'segment_id': SEG,
        'subject_candidate_id': subject,
        'object_candidate_id': object_,
        'predicate': predicate,
        'qualifiers': q,
        'original_quote': quote,
        'origin': 'book',
        'source_file': '02-sources/02-Markdown/05_CHP-5_sec_iii.md',
    }


def make_mention(number, candidate_id, surface, line_no, note):
    line = source_lines[line_no - 1]
    local_start = line.find(surface)
    if local_start < 0:
        raise ValueError(f'mention surface absent on L{line_no}: {surface!r}')
    prefix = '\n'.join(source_lines[69:line_no - 1])
    start = len(prefix) + (1 if line_no > 70 else 0) + local_start
    return {
        'mention_id': f'm-chp5-sec-iii-l70-80-{number:03d}',
        'segment_id': SEG,
        'candidate_id': candidate_id,
        'surface_form': surface,
        'start_char': str(start),
        'end_char': str(start + len(surface)),
        'note': note,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after all guarded checks pass')
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
    if not TARGET_IDS.issubset(by_id):
        raise SystemExit(f'missing targets: {sorted(TARGET_IDS - set(by_id))}')
    if any(by_id[sid].get('segment_id') != SEG for sid in TARGET_IDS):
        raise SystemExit('target segment mismatch')
    if any(by_id[sid].get('qualifiers', {}).get('relation_candidate') is not None
           for sid in TARGET_IDS):
        raise SystemExit('one or more target statements are already classified')

    candidate_fields, candidates = load_csv(CANDIDATES)
    mention_fields, mentions = load_csv(MENTIONS)
    candidate_ids = {r['candidate_id'] for r in candidates}
    new_candidate_ids = {f'cand-{n}' for n in range(11924, 11931)}
    if candidate_ids & new_candidate_ids:
        raise SystemExit('candidate ID collision')
    mention_ids = {r['mention_id'] for r in mentions}
    new_mention_ids = {f'm-chp5-sec-iii-l70-80-{n:03d}' for n in range(48, 51)}
    if mention_ids & new_mention_ids:
        raise SystemExit('mention ID collision')

    candidate_specs = [
        ('cand-11924', "Small pictures of popular life discussed in Cerquozzi's early career",
         'An unnamed work group described as small pictures with scenes from popular life; Haskell dates most of it to Cerquozzi’s early years only tentatively.', 'work', 78),
        ('cand-11925', "Larger pictures Cerquozzi increasingly painted to commission",
         'An unnamed later work group described as much larger pictures painted to commission; titles and commissioners are not supplied.', 'work', 79),
        ('cand-11926', "Picture type collected by Carpegna, Carandini, and Raggi",
         'Haskell says the three named patrons collected “this type of picture” after discussing landscape painters, artists with subjects like Cerquozzi’s, and later Bamboccianti. Keep the referent broad and distinct from Bambocciate unless further evidence resolves it.', 'term', 77),
        ('cand-11927', "Alessandro Farnese's campaigns in the Low Countries on behalf of the Spaniards",
         'The campaigns are described as the subject celebrated in volume II of De Bello Belgico; the claim follows Haskell’s wording and does not add dates or individual battles.', 'event', 72),
        ('cand-11928', 'Unspecified Spaniards in the Low Countries for whom Farnese campaigned',
         'Collective beneficiaries in Haskell’s account; individuals and institutional identity are unspecified, so taxonomy type remains unresolved.', '', 72),
        ('cand-11929', 'Noble balance between classicism and Venetian colour in history painting',
         'Aesthetic ideal that Haskell says grand history painters fostered and most of the patron families tended to ignore; preserve his evaluative phrasing.', 'term', 74),
        ('cand-11930', 'Other artists collaborating on De Bello Belgico volume II illustrations in 1647',
         'Unnamed participants in the illustration collaboration; no identities or count are supplied, and the people-group type remains unresolved.', '', 72),
    ]
    new_candidates = [{
        'candidate_id': cid,
        'index_entry_id': '',
        'canonical_name': name,
        'index_page_range': '',
        'suggested_type': kind,
        'status': 'open',
        'index_source_file': '',
        'sub_entry': '',
        'detail': detail,
        'exclude_reason': '',
        'candidate_origin': 'body-mention',
        'candidate_source_ref': f'{SEG}#L{line_no}',
    } for cid, name, detail, kind, line_no in candidate_specs]

    new_statements = []
    add = lambda *a, **kw: new_statements.append(make_statement(*a, **kw))

    # Split the page's compound claims, keeping the original IDs on the principal claim.
    revise(by_id, 'st-chp5-p137-aristocratic-success-reflected-in-art',
           subject='cand-3084', object_='cand-5260',
           predicate='success_reflected_in_art',
           claim="Haskell interprets Cerquozzi's success with Rome's aristocratic society as reflected in his art.",
           candidates=['cand-3084', 'cand-5260'],
           qualification="This is Haskell's assessment, not an independently measurable causal finding.",
           line_start=78, line_end=78, relation=False)

    revise(by_id, 'st-chp5-p137-association-and-gradual-acceptance',
           subject='cand-3084', object_='cand-6148',
           predicate='became_more_closely_associated_with',
           claim='Haskell says Cerquozzi became more closely associated with the patron families discussed.',
           quote='his closer association with them', candidates=['cand-3084', 'cand-6148'],
           qualification="'Them' refers to the families in the preceding discussion; retain this as Haskell's characterization.",
           line_start=79, line_end=79, relation=True)
    add('change-attributed-to-association', 'cand-3084', None,
        'change_seems_to_follow_closer_association', 79, 79,
        'Rather it seems to have sprung naturally from his closer association with them',
        'Haskell suggests that the change in Cerquozzi’s work arose naturally from his closer association with the patron families.',
        ['cand-3084', 'cand-6148'],
        "Preserve 'seems' and the causal interpretation; it is not an independently established explanation.", False)
    add('gradual-acceptance-of-patrons-values', 'cand-3084', 'cand-6148',
        'gradually_accepted_values_of', 79, 79,
        'from a gradual acceptance of their values',
        'Haskell says Cerquozzi gradually accepted the values of the patron families.',
        ['cand-3084', 'cand-6148'],
        "This is Haskell's interpretive account of a gradual change; the values are not independently defined.", False)
    add('acceptance-process-not-unknown-among-artists', None, None,
        'process_described_as_common_among_artists', 79, 79,
        'a process not unknown among artists of all kinds since Cerquozzi’s day',
        'Haskell generalizes that this process was not unknown among artists of all kinds since Cerquozzi’s day.',
        ['cand-3084'], 'Authorial generalization, not a claim about a named artist group.', False)

    revise(by_id, 'st-chp5-p137-carandini-spanish-alignment',
           subject='cand-0542', object_='cand-4404',
           predicate='devoted_to_spanish_cause',
           claim='Haskell places Count Camillo Carandini alongside Raggi among those devoted to the Spanish cause.',
           quote='was a Genoese and also devoted to the Spanish cause. So too was the Modenese Count Camillo Carandini',
           candidates=['cand-0542', 'cand-2091', 'cand-3416', 'cand-4404'],
           qualification='The source describes a political alignment; footnote 2 concerns Raggi’s patronage and Carandini’s identification, not independent proof of this alignment.',
           line_start=73, line_end=73, relation=True)

    # The clause at the end of p.137 is incomplete and is intentionally left for p.138.

    revise(by_id, 'st-chp5-p137-carpegna-carandini-raggi-collectors',
           subject='cand-3084', object_='cand-0567',
           predicate='had_as_enthusiastic_patron',
           claim='Haskell names the Count of Carpegna among Cerquozzi’s three most enthusiastic patrons.',
           quote='Three of Cerquozzi’s most enthusiastic patrons, the\nCounts Carpegna',
           candidates=['cand-3084', 'cand-0567'],
           qualification='The index gives only “Count Carpegna”; do not infer a personal name or identify additional family members.',
           line_start=76, line_end=77, relation=True)
    add('carandini-among-most-enthusiastic-patrons', 'cand-3084', 'cand-0542',
        'had_as_enthusiastic_patron', 76, 77,
        'Three of Cerquozzi’s most enthusiastic patrons, the\nCounts Carpegna and Carandini',
        'Haskell names Count Camillo Carandini among Cerquozzi’s three most enthusiastic patrons.',
        ['cand-3084', 'cand-0542'],
        'Footnote 2 identifies Count Camillo Carandini; it does not independently verify the political characterization.', True)
    add('raggi-among-most-enthusiastic-patrons', 'cand-3084', 'cand-2091',
        'had_as_enthusiastic_patron', 76, 77,
        'Three of Cerquozzi’s most enthusiastic patrons, the\nCounts Carpegna and Carandini and Monsignor Raggi',
        'Haskell names Monsignor Raggi among Cerquozzi’s three most enthusiastic patrons.',
        ['cand-3084', 'cand-2091'],
        'Footnote 2 discusses Raggi’s patronage; the exact identity behind the index entry remains unresolved.', True,
        footnote_refs=[{'marker': 2, 'segment_id': 'chp-5:05_CHP-5_sec_iii:l126-165', 'source_line': 143,
                        'citation_statement_ids': ['st-chp5-notes-l143-raggi-patronage-loan']}])
    for suffix, person, name, name_quote in [
        ('carpegna-collected-pictures-of-described-type', 'cand-0567', 'Count Carpegna', 'Counts Carpegna'),
        ('carandini-collected-pictures-of-described-type', 'cand-0542', 'Count Camillo Carandini', 'Carandini'),
        ('raggi-collected-pictures-of-described-type', 'cand-2091', 'Monsignor Raggi', 'Monsignor Raggi'),
    ]:
        add(suffix, person, 'cand-11926', 'collected_picture_type', 76, 77,
            'Three of Cerquozzi’s most enthusiastic patrons, the\nCounts Carpegna and Carandini and Monsignor Raggi, were all collectors of this type of picture.',
            f'Haskell says {name} collected the picture type discussed in this paragraph.',
            [person, 'cand-11926'],
            'The list is split by named patron; “this type” remains a broad reference to the preceding discussion and is not equated with Bambocciate.', True)

    revise(by_id, 'st-chp5-p137-de-bello-farnese-campaigns',
           subject='cand-2515', object_='cand-11927',
           predicate='celebrates_campaigns',
           claim='Volume II of De Bello Belgico is described as celebrating Alessandro Farnese’s campaigns.',
           quote='the second volume of Famiano Strada’s De Bello Belgico, a celebration of Alessandro Farnese’s campaigns',
           candidates=['cand-2515', 'cand-0995', 'cand-11927'],
           qualification='The campaign’s location and beneficiaries are recorded separately; the passage is Haskell’s description of the book.',
           line_start=72, line_end=72, relation=True)
    revise(by_id, 'st-chp5-p137-miel-borgognone-strada-collaboration',
           subject='cand-3084', object_='cand-2515',
           predicate='collaborated_on_illustration_of',
           claim='In 1647 Cerquozzi collaborated with Jan Miel, Giacomo Borgognone and other artists on the illustration of volume II of De Bello Belgico.',
           quote='In 1647, for instance, he was collaborating with Jan Miel, Giacomo Borgognone and others on the illustration of the second volume of Famiano Strada’s De Bello Belgico',
           candidates=['cand-3084', 'cand-1662', 'cand-0399', 'cand-11930', 'cand-2515'],
           qualification='The source names Miel and Borgognone and leaves the other collaborators unnamed; this is an illustration collaboration, not authorship of the book.',
           line_start=72, line_end=72, relation=True)
    add('miel-contributed-to-de-bello-illustrations', 'cand-1662', 'cand-2515',
        'collaborated_on_illustration_of', 72, 72,
        'collaborating with Jan Miel',
        'Haskell names Jan Miel as a collaborator on the illustration of volume II of De Bello Belgico in 1647.',
        ['cand-1662', 'cand-3084', 'cand-2515'],
        'The passage does not specify an individual plate or contribution.', True,
        extra_qualifiers={'date': '1647', 'volume': 'II'})
    add('borgognone-contributed-to-de-bello-illustrations', 'cand-0399', 'cand-2515',
        'collaborated_on_illustration_of', 72, 72,
        'Giacomo Borgognone and others on the illustration of the second volume',
        'Haskell names Giacomo Borgognone as a collaborator on the illustration of volume II of De Bello Belgico in 1647.',
        ['cand-0399', 'cand-3084', 'cand-2515'],
        'The passage does not specify an individual plate or contribution.', True,
        extra_qualifiers={'date': '1647', 'volume': 'II'})
    add('unnamed-artists-contributed-to-de-bello-illustrations', 'cand-11930', 'cand-2515',
        'collaborated_on_illustration_of', 72, 72,
        'and others on the illustration of the second volume',
        'Haskell says additional unnamed artists collaborated on the illustration of volume II of De Bello Belgico in 1647.',
        ['cand-11930', 'cand-3084', 'cand-2515'],
        'The source supplies no names or count for the other collaborators.', True,
        extra_qualifiers={'date': '1647', 'volume': 'II'})
    add('de-bello-authored-by-famiano-strada', 'cand-2515', 'cand-2514',
        'authored_by', 72, 72, 'Famiano Strada’s De Bello Belgico',
        'Haskell identifies De Bello Belgico as Famiano Strada’s work.',
        ['cand-2515', 'cand-2514'],
        'The possessive attribution is explicit in the source; the publication is not independently consulted here.', True,
        extra_qualifiers={'volume': 'II'})
    add('farnese-campaigns-were-on-behalf-of-spaniards', 'cand-11927', 'cand-11928',
        'campaigns_on_behalf_of', 72, 73,
        'campaigns on behalf of the Spaniards in the Low\nCountries',
        'Haskell says Farnese’s campaigns were on behalf of the Spaniards.',
        ['cand-11927', 'cand-11928'],
        'The Spaniards are an unspecified collective; no formal institution or individual is inferred.', True)
    add('farnese-campaigns-in-low-countries', 'cand-11927', 'cand-4342',
        'campaigns_in', 72, 73,
        'campaigns on behalf of the Spaniards in the Low\nCountries',
        'Haskell locates Farnese’s campaigns in the Low Countries.',
        ['cand-11927', 'cand-4342'],
        'The place is retained as named; no narrower boundary is inferred.', True)
    add('farnese-named-as-campaign-leader', 'cand-11927', 'cand-0995',
        'campaigns_of', 72, 72,
        'Alessandro Farnese’s campaigns',
        'Haskell identifies the campaigns as Alessandro Farnese’s.',
        ['cand-11927', 'cand-0995'],
        'The possessive identifies the campaigns with Farnese; no specific command title is inferred.', True)

    revise(by_id, 'st-chp5-p137-early-small-popular-pictures',
           subject='cand-3084', object_='cand-11924',
           predicate='small_popular_life_pictures_mostly_belong_to_early_years',
           claim='With dating uncertain, Haskell says the small popular-life pictures discussed in Cerquozzi’s career seem mostly to belong to his early years.',
           quote='As far as dating can be established at all, it seems that the small pictures with scenes from popular life belong mostly to his early years',
           candidates=['cand-3084', 'cand-11924'],
           qualification="Retain 'as far as dating can be established at all', 'it seems', and 'mostly'; this is a tentative period attribution.",
           line_start=78, line_end=79, relation=False)
    add('cerquozzi-followed-van-laer', 'cand-3084', 'cand-1351',
        'closely_followed_as_artist', 78, 79,
        'when he was closely following Van\nLaer',
        'Haskell says Cerquozzi closely followed Van Laer during the period associated with the small popular-life pictures.',
        ['cand-3084', 'cand-1351', 'cand-11924'],
        'Retain the source’s period context; “following” is not taken to mean formal apprenticeship.', True)
    add('cerquozzi-worked-for-art-dealers', 'cand-3084', 'cand-0125',
        'worked_for_dealers', 78, 79,
        'and largely working for dealers',
        'Haskell says Cerquozzi largely worked for dealers during this early period.',
        ['cand-3084', 'cand-0125', 'cand-11924'],
        'No individual dealer or particular sale is named.', True)

    revise(by_id, 'st-chp5-p137-families-contrast-barberini-circle',
           subject='cand-6148', object_='cand-5534',
           predicate='taste_contrasted_with',
           claim='Haskell says most of the families discussed showed a striking contrast in taste with the more cultivated Barberini circle.',
           candidates=['cand-6148', 'cand-5534'],
           qualification="Keep 'most' and the author's evaluative comparison; the family group is not exhaustive.",
           line_start=74, line_end=74, relation=True)

    revise(by_id, 'st-chp5-p137-families-favored-subjects',
           subject='cand-6148', object_='cand-3041',
           predicate='concentrated_on_painter',
           claim='Haskell says the families repeatedly concentrated on landscape painters such as Gaspard Dughet.',
           quote='Again and again we find them concentrating on landscape painters such as Gaspard Dughet',
           candidates=['cand-6148', 'cand-3041'],
           qualification='Dughet is an example rather than an exhaustive account of the families’ preferences.',
           line_start=74, line_end=74, relation=True)
    add('families-concentrated-on-salvator-rosa', 'cand-6148', 'cand-3099',
        'concentrated_on_painter', 74, 75,
        'landscape painters such as Gaspard Dughet or\nSalvator Rosa',
        'Haskell says the families repeatedly concentrated on landscape painters such as Salvator Rosa.',
        ['cand-6148', 'cand-3099'],
        'Rosa is an example rather than an exhaustive account of the families’ preferences.', True)
    add('families-concentrated-on-jan-miel', 'cand-6148', 'cand-1662',
        'concentrated_on_painter', 74, 76,
        'Again and again we find them concentrating on landscape painters such as Gaspard Dughet or\nSalvator Rosa as well as on other artists who specialised in subjects similar to those of\nCerquozzi—Jan Miel',
        'Haskell says the families concentrated on Jan Miel among artists whose subjects resembled Cerquozzi’s.',
        ['cand-6148', 'cand-1662', 'cand-3084'],
        'This is a statement about the families’ preferences, not proof of a specific commission.', True)
    add('families-concentrated-on-giacomo-borgognone', 'cand-6148', 'cand-0399',
        'concentrated_on_painter', 74, 76,
        'Again and again we find them concentrating on landscape painters such as Gaspard Dughet or\nSalvator Rosa as well as on other artists who specialised in subjects similar to those of\nCerquozzi—Jan Miel, for instance, or Giacomo Borgognone',
        'Haskell says the families concentrated on Giacomo Borgognone among artists whose subjects resembled Cerquozzi’s.',
        ['cand-6148', 'cand-0399', 'cand-3084'],
        'This is a statement about the families’ preferences, not proof of a specific commission.', True)
    add('miel-specialized-in-cerquozzi-like-subjects', 'cand-1662', 'cand-3084',
        'specialized_in_subjects_similar_to', 75, 76,
        'artists who specialised in subjects similar to those of\nCerquozzi—Jan Miel',
        'Haskell says Jan Miel specialized in subjects similar to Cerquozzi’s.',
        ['cand-1662', 'cand-3084'],
        'This is the author’s comparative description of subject matter.', True)
    add('borgognone-specialized-in-cerquozzi-like-subjects', 'cand-0399', 'cand-3084',
        'specialized_in_subjects_similar_to', 75, 76,
        'artists who specialised in subjects similar to those of\nCerquozzi—Jan Miel, for instance, or Giacomo Borgognone',
        'Haskell says Giacomo Borgognone specialized in subjects similar to Cerquozzi’s.',
        ['cand-0399', 'cand-3084'],
        'This is the author’s comparative description of subject matter.', True)
    add('borgognone-described-as-battle-painter', 'cand-0399', None,
        'described_as_battle_painter', 76, 76,
        'Giacomo Borgognone, the battle painter',
        'Haskell describes Giacomo Borgognone as a battle painter.',
        ['cand-0399'], 'The occupational description is Haskell’s wording.', False)
    add('families-concentrated-on-later-bamboccianti', 'cand-6148', 'cand-0173',
        'concentrated_on_artist_group', 74, 76,
        'Again and again we find them concentrating on landscape painters such as Gaspard Dughet or\nSalvator Rosa as well as on other artists who specialised in subjects similar to those of\nCerquozzi—Jan Miel, for instance, or Giacomo Borgognone, the battle painter—and bamboccianti of later generations.',
        'Haskell says the families also concentrated on Bamboccianti of later generations.',
        ['cand-6148', 'cand-0173'],
        'The source specifies later generations; it does not identify individual members.', True)
    add('later-bamboccianti-specialized-in-cerquozzi-like-subjects', 'cand-0173', 'cand-3084',
        'specialized_in_subjects_similar_to', 75, 76,
        'other artists who specialised in subjects similar to those of\nCerquozzi—Jan Miel, for instance, or Giacomo Borgognone, the battle painter—and bamboccianti of later generations',
        'Haskell includes later Bamboccianti among artists whose subjects resembled Cerquozzi’s.',
        ['cand-0173', 'cand-3084'],
        'This is Haskell’s group-level comparison; no members are inferred.', True)

    revise(by_id, 'st-chp5-p137-families-stylistic-preferences',
           subject='cand-6148', object_='cand-6144',
           predicate='tended_to_ignore_grander_history_painters',
           claim='Haskell says the families tended to ignore grander history painters.',
           quote='They tended to ignore the grander history painters',
           candidates=['cand-6148', 'cand-6144'],
           qualification="Retain 'tended to'; the claim does not apply uniformly to every family.",
           line_start=74, line_end=74, relation=True)
    add('families-ignored-classicism-venetian-colour-balance', 'cand-6148', 'cand-11929',
        'tended_to_ignore_aesthetic_ideal', 74, 74,
        'They tended to ignore the grander history painters and the noble balance between classicism and Venetian colour',
        'Haskell says the families tended to ignore the noble balance between classicism and Venetian colour.',
        ['cand-6148', 'cand-11929', 'cand-4628', 'cand-6145'],
        'Retain Haskell’s evaluative framing and the compound aesthetic ideal; component terms retain their existing separate mentions.', True)
    add('history-painters-fostered-classicism-venetian-colour-balance', 'cand-6144', 'cand-11929',
        'fostered_aesthetic_ideal', 74, 74,
        'the grander history painters and the noble balance between classicism and Venetian colour which these artists were fostering',
        'Haskell says the grander history painters were fostering the noble balance between classicism and Venetian colour.',
        ['cand-6144', 'cand-11929', 'cand-4628', 'cand-6145'],
        '“These artists” refers to the grander history painters in the sentence.', True)
    add('families-ignored-baroque-exuberance', 'cand-6148', 'cand-3993',
        'tended_to_ignore_baroque_exuberance', 74, 74,
        'They tended to ignore the grander history painters and the noble balance between classicism and Venetian colour which these artists were fostering as well as the exuberance of the Baroque',
        'Haskell says the families tended to ignore the exuberance of the Baroque.',
        ['cand-6148', 'cand-3993'],
        'Keep the source’s evaluative term “exuberance”; do not treat the statement as a universal stylistic rejection.', True)
    revise(by_id, 'st-chp5-p137-later-large-commissioned-pictures',
           subject='cand-3084', object_='cand-11925',
           predicate='increasingly_turned_to_larger_pictures',
           claim='Haskell says Cerquozzi later turned increasingly to much larger pictures.',
           quote='but that later he turned more and more to much larger pictures',
           candidates=['cand-3084', 'cand-11925'],
           qualification='The source presents a broad career pattern and gives no dates or titles for individual works.',
           line_start=79, line_end=79, relation=True)
    add('later-larger-pictures-painted-to-commission', 'cand-11925', None,
        'painted_to_commission', 79, 79,
        'which were painted to commission',
        'Haskell says the later larger pictures were painted to commission.',
        ['cand-11925'],
        'No commissioners or individual works are identified; this is a property of an unnamed work group.', False)
    add('cerquozzi-widened-subject-matter', 'cand-3084', None,
        'widened_range_of_subject_matter', 79, 79,
        'he then widened the range of his subject-matter',
        'Haskell says Cerquozzi later widened the range of his subject matter.',
        ['cand-3084', 'cand-11925'],
        'This is a broad career characterization rather than a claim about a named subject or work.', False)

    # Keep the negative causal judgment distinct from the market-price observation;
    # the printed note 3 belongs to the latter clause and is transferred with it.
    pressure = by_id['st-chp5-p137-patron-pressure-and-high-prices']
    pressure_q = pressure['qualifiers']
    marker3 = {k: pressure_q[k] for k in ('footnote_target_line', 'footnote_link_status', 'footnote_refs') if k in pressure_q}
    for key in ('footnote_marker', 'footnote_target_line', 'footnote_segment', 'footnote_link_status', 'footnote_refs'):
        pressure_q.pop(key, None)
    revise(by_id, 'st-chp5-p137-patron-pressure-and-high-prices',
           subject='cand-3084', object_='cand-6148',
           predicate='change_not_likely_directly_caused_by_specific_patron_pressure',
           claim='Haskell sees little reason to attribute Cerquozzi’s change directly to specific pressure from his patrons.',
           quote='There is not much reason for believing that this change was the direct result, of specific pressures from his patrons',
           candidates=['cand-3084', 'cand-6148'],
           qualification='Preserve the author’s caution (“not much reason”) and distinguish his causal judgment from the separate market-price observation.',
           line_start=79, line_end=79, relation=False)
    add('popular-bambocciate-continued-to-fetch-high-prices', 'cand-6099', None,
        'continued_to_fetch_high_prices', 79, 79,
        'the more authentically popular and coarse bambocciate continued to fetch very high prices',
        'Haskell says more authentically popular and coarse Bambocciate continued to fetch very high prices.',
        ['cand-6099', 'cand-2062'],
        'No price amount, individual sale, or named purchaser is given. Footnote 3 is a comparison concerning a Jan Miel painting, not direct evidence for Cerquozzi prices.',
        False, footnote_refs=[{'marker': 3, 'segment_id': 'chp-5:05_CHP-5_sec_iii:l126-165', 'source_line': 144,
                               'citation_statement_ids': ['st-chp5-notes-l144-corsini-miel']}],
        extra_qualifiers=marker3)

    revise(by_id, 'st-chp5-p137-patrons-spanish-sphere',
           subject='cand-3084', object_='cand-6148',
           predicate='had_major_patrons_within_spanish_sphere',
           claim='Until Cerquozzi’s later years, Haskell says nearly all of his more important patrons were within the Spanish sphere of influence.',
           candidates=['cand-3084', 'cand-6148', 'cand-4591'],
           qualification="The sentence continues the p.136 phrase 'and until his later years'; retain 'nearly all' and the political rather than geographic sense of Spanish sphere.",
           line_start=71, line_end=71, relation=True)

    revise(by_id, 'st-chp5-p137-private-life-dilemma-and-spanish-audience',
           subject='cand-3084', object_=None,
           predicate='possible_private_life_dilemma_reflected_in_painting',
           claim='Haskell suggests that a possible dilemma in Cerquozzi’s private life may be reflected in the way he painted.',
           candidates=['cand-3084', 'cand-6146', 'cand-6147', 'cand-4591'],
           qualification="Retain 'It may not be extravagant' as the author's interpretive qualification. S0 OCR reads 'private fife' and 'antiSpanish'; physical p.22 reads 'private life' and 'anti-Spanish'. Footnote 4 provides an attributed 1642 report and an explicit source-bias caveat, not independent verification.",
           line_start=79, line_end=79, relation=False)
    add('cerquozzi-painted-antispanish-common-people', 'cand-3084', 'cand-6146',
        'painted_subjects', 79, 79,
        'a man who painted the essentially antiSpanish common people',
        'Haskell says Cerquozzi painted common people whom he characterizes as essentially anti-Spanish.',
        ['cand-3084', 'cand-6146'],
        'This remains Haskell’s characterization of the subjects; no individual political identities are inferred.', True)
    add('cerquozzi-painted-for-sympathizers-with-spain', 'cand-3084', 'cand-6147',
        'painted_for_audience', 79, 79,
        'painted the essentially antiSpanish common people for sympathisers with Spain',
        'Haskell says Cerquozzi painted for unnamed sympathizers with Spain.',
        ['cand-3084', 'cand-6146', 'cand-6147', 'cand-4591'],
        'This is part of Haskell’s interpretive sentence; the audience’s membership and location are unspecified.', True)

    revise(by_id, 'st-chp5-p137-raggi-admired-cerquozzi',
           subject='cand-2091', object_='cand-3084', predicate='admired',
           claim='Haskell identifies Monsignor Raggi as an admirer of Cerquozzi.',
           candidates=['cand-2091', 'cand-3084'],
           qualification='The body says “admirer”; footnote 2 separately discusses Raggi’s patronage without independently verifying a specific commission.',
           line_start=73, line_end=73, relation=True)

    revise(by_id, 'st-chp5-p137-raggi-genoese-spanish-cause',
           subject='cand-2091', object_='cand-1131', predicate='described_as_genoese',
           claim='Haskell describes Monsignor Raggi as Genoese.',
           quote='was a Genoese', candidates=['cand-2091', 'cand-1131'],
           qualification='This is Haskell’s geographic-origin characterization; it does not establish a birthplace.',
           line_start=73, line_end=73, relation=True)
    add('raggi-devoted-to-spanish-cause', 'cand-2091', 'cand-4404',
        'devoted_to_spanish_cause', 73, 73,
        'also devoted to the Spanish cause',
        'Haskell says Raggi was devoted to the Spanish cause.',
        ['cand-2091', 'cand-4404'],
        'This is Haskell’s political characterization, not an independently verified affiliation.', True)

    revise(by_id, 'st-chp5-p137-rapaccioli-boycotted-at-conclave',
           subject='cand-2097', object_='cand-6143',
           predicate='boycotted_by_at_conclave',
           claim='Haskell says the French boycotted Rapaccioli at the conclave of 1655 because of his Spanish affiliations.',
           candidates=['cand-2097', 'cand-6143', 'cand-6142', 'cand-4591'],
           qualification='The French participants are unspecified; footnote 1 cites a French ambassador’s report and is retained as citation context, not independent verification.',
           line_start=73, line_end=73, relation=True)

    revise(by_id, 'st-chp5-p137-rapaccioli-death',
           subject='cand-2097', object_=None, predicate='died_in_1657',
           claim='Haskell states that Cardinal Rapaccioli died in 1657.',
           candidates=['cand-2097'],
           qualification='Book statement only; no independent death-date verification is asserted.',
           line_start=73, line_end=73, relation=False)

    revise(by_id, 'st-chp5-p137-rapaccioli-owned-cerquozzi-pictures',
           subject='cand-2097', object_='cand-6149',
           predicate='owned_pictures_by',
           claim='Haskell says Rapaccioli owned many pictures by Cerquozzi.',
           candidates=['cand-2097', 'cand-3084', 'cand-6149'],
           qualification='The artist is supplied by the antecedent “he”; no titles or count are specified.',
           line_start=73, line_end=73, relation=True)

    new_mentions = [
        make_mention(48, 'cand-11930', 'and others', 72,
                     'Unnamed additional artists collaborating on the volume II illustration; identities and count are not supplied.'),
        make_mention(49, 'cand-11927', 'Alessandro Farnese’s campaigns', 72,
                     'Campaign group described as the subject celebrated by De Bello Belgico volume II.'),
        make_mention(50, 'cand-11929', 'the noble balance between classicism and Venetian colour', 74,
                     'Composite aesthetic ideal; the component mentions remain separately mapped to their existing candidates.'),
    ]

    # Separate political entities from geography and collective populations, and
    # separate picture groups from the Bambocciate category.
    mention_remaps = {
        'm-chp5-sec-iii-l70-80-002': 'cand-4591',
        'm-chp5-sec-iii-l70-80-008': 'cand-11928',
        'm-chp5-sec-iii-l70-80-014': 'cand-4591',
        'm-chp5-sec-iii-l70-80-017': 'cand-4404',
        'm-chp5-sec-iii-l70-80-035': 'cand-11926',
        'm-chp5-sec-iii-l70-80-038': 'cand-11924',
        'm-chp5-sec-iii-l70-80-041': 'cand-11925',
        'm-chp5-sec-iii-l70-80-047': 'cand-4591',
    }
    mention_by_id = {r['mention_id']: r for r in mentions}
    if not set(mention_remaps).issubset(mention_by_id):
        raise SystemExit(f'missing mentions for remap: {sorted(set(mention_remaps) - set(mention_by_id))}')
    expected_old_candidates = {
        'm-chp5-sec-iii-l70-80-002': 'cand-5120',
        'm-chp5-sec-iii-l70-80-008': 'cand-6133',
        'm-chp5-sec-iii-l70-80-014': 'cand-5120',
        'm-chp5-sec-iii-l70-80-017': 'cand-5120',
        'm-chp5-sec-iii-l70-80-035': 'cand-6099',
        'm-chp5-sec-iii-l70-80-038': 'cand-6099',
        'm-chp5-sec-iii-l70-80-041': 'cand-6099',
        'm-chp5-sec-iii-l70-80-047': 'cand-5120',
    }
    if any(mention_by_id[mid].get('candidate_id') != old for mid, old in expected_old_candidates.items()):
        raise SystemExit('mention remap precondition failed')
    for mid, new_candidate in mention_remaps.items():
        mention_by_id[mid]['candidate_id'] = new_candidate

    # Move note 3 from the combined sentence to the high-price clause it follows.
    for row in new_statements:
        if row['statement_id'] == 'st-chp5-p137-popular-bambocciate-continued-to-fetch-high-prices':
            row['qualifiers'].update(marker3)
            row['qualifiers']['footnote_marker'] = 3
            row['qualifiers']['footnote_segment'] = 'chp-5:05_CHP-5_sec_iii:l126-165'
    # Note 2 also gives the source's patronage support for Raggi; it is citation
    # context, not a claim that the note verifies an individual commission.
    for row in new_statements:
        if row['statement_id'] == 'st-chp5-p137-raggi-among-most-enthusiastic-patrons':
            row['qualifiers']['footnote_target_line'] = 143

    new_statement_ids = {r['statement_id'] for r in new_statements}
    if len(new_statement_ids) != len(new_statements) or set(ids) & new_statement_ids:
        raise SystemExit('statement ID collision')
    if len(new_candidate_ids) != len(new_candidates):
        raise SystemExit('candidate ID collision within additions')
    existing_names = {(r.get('canonical_name'), r.get('suggested_type')) for r in candidates}
    if any((r['canonical_name'], r['suggested_type']) in existing_names for r in new_candidates):
        raise SystemExit('candidate natural key collision')

    for sid in TARGET_IDS - {PENDING_CONTINUATION}:
        row = by_id[sid]
        q = row.get('qualifiers', {})
        if q.get('relation_candidate') not in (True, False):
            raise SystemExit(f'target not classified: {sid}')
        if q.get('relation_candidate') is True and not (row.get('subject_candidate_id') and row.get('object_candidate_id')):
            raise SystemExit(f'target relation missing endpoint: {sid}')
    for row in new_statements:
        q = row['qualifiers']
        if q['relation_candidate'] and not (row['subject_candidate_id'] and row['object_candidate_id']):
            raise SystemExit(f'new relation missing endpoint: {row["statement_id"]}')
        if row['original_quote'] not in '\n'.join(source_lines[q['source_line_start'] - 1:q['source_line_end']]):
            raise SystemExit(f'quote failed source check: {row["statement_id"]}')
    for row in new_mentions:
        if segment_text[int(row['start_char']):int(row['end_char'])] != row['surface_form']:
            raise SystemExit(f'mention span failed: {row["mention_id"]}')
    for row in new_candidates:
        line_no = next(line for cid, _, _, _, line in candidate_specs if cid == row['candidate_id'])
        if row['candidate_source_ref'] != f'{SEG}#L{line_no}':
            raise SystemExit(f'candidate source ref failed: {row["candidate_id"]}')

    # Preview the full before/after classification; one sentence fragment remains
    # unclassified until the following page completes it.
    target_rows = [by_id[sid] for sid in sorted(TARGET_IDS)]
    classified = [r for r in target_rows if r['statement_id'] != PENDING_CONTINUATION]
    rel_count = sum(r['qualifiers']['relation_candidate'] is True for r in classified)
    nonrel_count = sum(r['qualifiers']['relation_candidate'] is False for r in classified)

    if args.apply:
        paths = [STATEMENTS, CANDIDATES, MENTIONS]
        backups = [p.with_name(p.name + BACKUP_TAG) for p in paths]
        if any(p.exists() for p in backups):
            raise SystemExit('backup already exists; refusing to overwrite')
        for source, backup in zip(paths, backups):
            shutil.copy2(source, backup)
        for row in new_candidates:
            candidates.append({key: row.get(key, '') for key in candidate_fields})
        for row in new_mentions:
            mentions.append({key: row.get(key, '') for key in mention_fields})
        statements.extend(new_statements)
        paths = [STATEMENTS, CANDIDATES, MENTIONS]
        temp_paths = [p.with_name(p.name + '.tmp-s2-chp5-p137') for p in paths]
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
        print('applied p.137 S2 semantic corrections')
        print('backups:', ', '.join(p.name for p in backups))
    else:
        print('PREVIEW only; no table writes')
    print(f'targets: {len(TARGET_IDS)}; classified now: {len(classified)}; pending cross-page continuation: 1')
    print(f'target classification: relation candidates {rel_count}; non-relational claims {nonrel_count}')
    print('new candidates:', ', '.join(r['candidate_id'] for r in new_candidates))
    print('new statements:', len(new_statements))
    print('new mentions:', len(new_mentions), '; remapped existing mentions:', len(mention_remaps))
    print('TARGET REVIEW:')
    for row in sorted(target_rows, key=lambda r: r['statement_id']):
        q = row.get('qualifiers', {})
        status = 'pending-continuation' if row['statement_id'] == PENDING_CONTINUATION else str(q['relation_candidate']).lower()
        print(f"  {status} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']} | {q.get('claim', '')}")
    print('ADDED CLAIM REVIEW:')
    for row in new_statements:
        q = row['qualifiers']
        print(f"  {str(q['relation_candidate']).lower()} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']} | {q['claim']}")
    print('MENTION REMAPS:')
    for mid, new_candidate in mention_remaps.items():
        print(f'  {mid}: {expected_old_candidates[mid]} -> {new_candidate}')


if __name__ == '__main__':
    main()
