import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l82-93'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
STATEMENTS = ROOT / '04-knowledge/tables/book-statements.jsonl'
CANDIDATES = ROOT / '04-knowledge/tables/entity-candidates.csv'
MENTIONS = ROOT / '04-knowledge/tables/mentions.csv'
BACKUP_TAG = '.bak-s2-chp5-p138-20261013'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: '5ddeb58b3a6ceefe25c1f8ae6391596189b1e9759751f8c7f7c1dd6b167bcba1',
    CANDIDATES: '821998592b7b01097dd97f0b6c595e41776665688f609512358e58243b326fab',
    MENTIONS: '52f3ec079683c0b786738cdc2c013cdffc6c6036a8a30fe5075ca3e27e2e088b',
}

TARGET_IDS = {
    'st-chp5-p138-aristocratic-limit',
    'st-chp5-p138-battle-scene-motifs',
    'st-chp5-p138-battle-specialization',
    'st-chp5-p138-deathbed-artichoke-return',
    'st-chp5-p138-funeral-academy-idealism',
    'st-chp5-p138-imaginative-capacity',
    'st-chp5-p138-large-still-lifes',
    'st-chp5-p138-massimi-appeal-and-collection',
    'st-chp5-p138-observation-contrast',
    'st-chp5-p138-paint-and-colour',
    'st-chp5-p138-patronage-political-shift',
    'st-chp5-p138-possible-crisis-1648-partial',
    'st-chp5-p138-realism-waterloo-comparison',
    'st-chp5-p138-saxl-battle-analysis',
    'st-chp5-p138-vicarious-participation',
    'st-chp5-p138-work-characterization',
}
P137_CONTINUATION = 'st-chp5-p137-careful-work-characterization-partial'
PENDING_CONTINUATION = 'st-chp5-p138-possible-crisis-1648-partial'
RELATION_NOTE = (
    'Source-grounded S2 relation candidate; source qualification is retained, '
    'and no formal S6 edge is created.'
)
NONRELATION_NOTE = (
    'This is a scalar, contextual, or interpretive assertion rather than a '
    'specific entity relation.'
)

source_lines = SOURCE.read_text(encoding='utf-8-sig').splitlines()
segment_text = '\n'.join(source_lines[81:93])
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
           line_start=None, line_end=None, relation=None, extra_qualifiers=None,
           remove_qualifiers=None):
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
    if remove_qualifiers:
        for key in remove_qualifiers:
            q.pop(key, None)
    if extra_qualifiers:
        q.update(extra_qualifiers)
    if relation is not None:
        classify(row, relation)
    return row


def note_context(row):
    q = row.get('qualifiers', {})
    return {k: v for k, v in q.items() if k.startswith('footnote_') or k.startswith('citation_')}


def make_statement(suffix, subject, object_, predicate, line_start, line_end,
                   quote, claim, candidates, qualification, relation,
                   extra_qualifiers=None):
    if quote not in '\n'.join(source_lines[line_start - 1:line_end]):
        raise ValueError(f'quote absent from source L{line_start}-L{line_end}: {quote!r}')
    q = {
        'source_line_start': line_start,
        'source_line_end': line_end,
        'printed_page': 138,
        'pdf_physical_page': 23,
        'claim': claim,
        'speaker': 'Haskell',
        'text_layer': 'authorial narration',
        'qualification': qualification,
        'mentioned_candidate_ids': candidates,
    }
    classify({'qualifiers': q}, relation)
    if extra_qualifiers:
        q.update(extra_qualifiers)
    return {
        'statement_id': f'st-chp5-p138-{suffix}',
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
    prefix = '\n'.join(source_lines[81:line_no - 1])
    start = len(prefix) + (1 if line_no > 82 else 0) + local_start
    return {
        'mention_id': f'm-chp5-sec-iii-l82-93-{number:03d}',
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
    required = TARGET_IDS | {P137_CONTINUATION}
    if not required.issubset(by_id):
        raise SystemExit(f'missing targets: {sorted(required - set(by_id))}')
    if any(by_id[sid].get('segment_id') != SEG for sid in TARGET_IDS):
        raise SystemExit('p.138 target segment mismatch')
    if by_id[P137_CONTINUATION].get('segment_id') != 'chp-5:05_CHP-5_sec_iii:l70-80':
        raise SystemExit('p.137 continuation segment mismatch')
    if any(by_id[sid].get('qualifiers', {}).get('relation_candidate') is not None for sid in TARGET_IDS | {P137_CONTINUATION}):
        raise SystemExit('one or more target statements are already classified')

    candidate_fields, candidates = load_csv(CANDIDATES)
    mention_fields, mentions = load_csv(MENTIONS)
    candidate_ids = {r['candidate_id'] for r in candidates}
    new_candidate_ids = {f'cand-{n}' for n in range(11931, 11935)}
    if candidate_ids & new_candidate_ids:
        raise SystemExit('candidate ID collision')
    mention_ids = {r['mention_id'] for r in mentions}
    new_mention_ids = {f'm-chp5-sec-iii-l82-93-{n:03d}' for n in range(32, 35)}
    if mention_ids & new_mention_ids:
        raise SystemExit('mention ID collision')

    candidate_specs = [
        ('cand-11931', 'Unspecified princes and prelates described as Cerquozzi’s friends',
         'Unnamed social group in Haskell’s characterization of Cerquozzi; no members or formal organization are identified.', '', 83),
        ('cand-11932', 'Death of Pope Urban VIII in Haskell’s account of Cerquozzi’s position',
         'Historical event that Haskell says affected Cerquozzi’s position; the passage supplies no date.', 'event', 93),
        ('cand-11933', 'European wars of the seventeenth century in Haskell’s battle-painting discussion',
         'Collective wars described as changing Europe; no particular conflict is identified in this passage.', 'event', 89),
        ('cand-11934', 'Popular life depicted by Cerquozzi (source description)',
         'Subject matter Haskell says Cerquozzi often depicted. Keep this broad expression distinct from the Bambocciate category and from individual work groups.', 'term', 83),
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

    # Close the p.137 fragment through its existing cross-page continuation link.
    p137 = by_id[P137_CONTINUATION]
    p137_q = p137['qualifiers']
    if p137_q.get('continued_by_statement_id') != 'st-chp5-p138-work-characterization':
        raise SystemExit('unexpected p.137 continuation link')
    revise(by_id, P137_CONTINUATION,
           predicate='careful_and_conscientious_in_work',
           claim='Haskell characterizes Cerquozzi as careful and conscientious in his work; the phrase continues across the page break.',
           qualification='The fragment at p.137 L79 is completed by the word “work” at p.138 L83; keep this as a work-practice characterization rather than a general personality judgment.',
           candidates=['cand-3084'], relation=False)
    p137_q['continued_by_statement_id'] = 'st-chp5-p138-cerquozzi-careful-in-work'

    revise(by_id, 'st-chp5-p138-aristocratic-limit',
           subject='cand-3084', object_='cand-5260',
           predicate='aristocratic_patronage_limited_sympathetic_painting_of_the_very_poor',
           claim='Haskell argues that after the Roman aristocracy took Cerquozzi up, it became almost impossible for him to paint the lives of the very poor with sympathy and understanding.',
           candidates=['cand-3084', 'cand-5260'],
           qualification='Retain “almost impossible”; this is Haskell’s social interpretation, not an independently established causal fact.',
           line_start=83, line_end=83, relation=False)

    revise(by_id, 'st-chp5-p138-battle-scene-motifs',
           subject='cand-3084', object_='cand-6152',
           predicate='battle_pictures_depicted_combat_aftermath',
           claim='Haskell describes battle pictures with charging cavaliers, collapsing horses, trampled soldiers, gunfire smoke, plundered dead, treated wounded and couriers announcing victory.',
           candidates=['cand-3084', 'cand-6152'],
           qualification='These are generalized scene motifs in the author’s description; no individual painting or battle is identified. The print reads “lit up” where S0 OCR reads “fit up”; S0 is unchanged.',
           line_start=90, line_end=90, relation=False)

    revise(by_id, 'st-chp5-p138-battle-specialization',
           subject='cand-3084', object_='cand-6152',
           predicate='specialized_in_battle_painting',
           claim='Haskell says Cerquozzi specialized in battle pictures.',
           quote='Above all he specialised in battle pictures',
           candidates=['cand-3084', 'cand-6152'],
           qualification='This records the specialization separately from Haskell’s genre comparison and the reported nickname.',
           line_start=88, line_end=88, relation=True)
    add('battle-genre-described-as-more-respectable-than-bambocciate', 'cand-6152', 'cand-6099',
        'described_as_more_respectable_than', 88, 88,
        'a more respectable genre than bambocciate',
        'Haskell describes battle painting as a more respectable genre than Bambocciate.',
        ['cand-6152', 'cand-6099'],
        'This is the author’s evaluative genre comparison, not a universal hierarchy.', True)
    add('cerquozzi-nickname-michelangelo-delle-battaglie', 'cand-3084', None,
        'success_in_battle_painting_attested_by_nickname', 88, 88,
        'his success is testified by the nicknameof‘Michelangelo delle Battaglie’',
        'Haskell says Cerquozzi’s success in battle painting was testified by the nickname “Michelangelo delle Battaglie”.',
        ['cand-3084', 'cand-6152'],
        'The nickname is reported by the book; the scan separates “nickname of”, while S0 OCR joins the words. No separate identity is inferred.', False)

    deathbed = by_id['st-chp5-p138-deathbed-artichoke-return']
    deathbed_notes = note_context(deathbed)
    revise(by_id, 'st-chp5-p138-deathbed-artichoke-return',
           subject='cand-3084', object_=None,
           predicate='ordered_artichokes_on_deathbed',
           claim='Haskell reports that Cerquozzi ordered a couple of artichokes on his deathbed.',
           quote='ordering a couple of artichokes on his deathbed ‘che io mi voglio saziare a mio modo’',
           candidates=['cand-3084'],
           qualification='The Italian words are reported speech; footnote 1 cites Passeri p.289. The following symbolic reading is recorded separately.',
           line_start=83, line_end=83, relation=False)
    add('deathbed-artichokes-as-symbolic-return-to-popular-life', 'cand-3084', 'cand-11934',
        'interpreted_as_symbolic_return_to_subject_matter', 83, 83,
        'in an almost symbolic last minute return to the popular Use he had so often depicted',
        'Haskell presents the reported deathbed order as an almost symbolic return to the popular life Cerquozzi had often depicted.',
        ['cand-3084', 'cand-11934'],
        'Retain “almost symbolic”; the scan reads “life” where S0 OCR reads “Use”. The subject-matter term is not equated with Bambocciate.', False,
        extra_qualifiers=deathbed_notes)

    funeral = by_id['st-chp5-p138-funeral-academy-idealism']
    funeral_notes = note_context(funeral)
    revise(by_id, 'st-chp5-p138-funeral-academy-idealism',
           subject='cand-3084', object_='cand-3470',
           predicate='buried_with_full_pomp_by',
           claim='Haskell says Cerquozzi was buried with full pomp by the Accademia di S. Luca.',
           quote='buried with full pomp by the Accademia di S. Luca',
           candidates=['cand-3084', 'cand-3470'],
           qualification='This records the Academy’s role in the funeral, not a burial location. Footnote 1 cites Passeri p.289.',
           line_start=83, line_end=83, relation=True)
    add('accademia-stronghold-of-classical-idealism', 'cand-3470', 'cand-6156',
        'described_as_stronghold_of', 83, 83,
        'by now the very stronghold of that classical idealism',
        'Haskell describes the Accademia di S. Luca as the stronghold of classical idealism.',
        ['cand-3470', 'cand-6156'],
        'This is Haskell’s characterization of the Academy; footnote 1 remains citation context.', True,
        extra_qualifiers=funeral_notes)
    add('cerquozzi-seemed-to-thwart-classical-idealism', 'cand-3084', 'cand-6156',
        'seemed_to_thwart', 83, 83,
        'which he had seemed to thwart',
        'Haskell says Cerquozzi seemed to thwart the classical idealism associated with the Academy.',
        ['cand-3084', 'cand-6156'],
        'Preserve “seemed”; this is Haskell’s interpretive characterization. Footnote 1 remains citation context.', True,
        extra_qualifiers=funeral_notes)
    add('classical-idealism-may-have-thwarted-cerquozzi', 'cand-6156', 'cand-3084',
        'may_have_thwarted', 83, 83,
        'but which had perhaps thwarted him',
        'Haskell suggests that classical idealism may in turn have thwarted Cerquozzi.',
        ['cand-6156', 'cand-3084'],
        'Preserve “perhaps”; this is an interpretive reversal, not an independently established causal fact. Footnote 1 remains citation context.', True,
        extra_qualifiers=funeral_notes)

    revise(by_id, 'st-chp5-p138-imaginative-capacity',
           subject='cand-3084', object_=None,
           predicate='reputation_based_partly_on_imaginative_unwitnessed_scenes',
           claim='Haskell says Cerquozzi’s reputation rested in part on his imaginative ability to paint scenes he had never witnessed.',
           candidates=['cand-3084'],
           qualification='Retain “to some extent”; this is the author’s account of the artist’s reputation and talent.',
           line_start=85, line_end=85, relation=False)

    still_life = by_id['st-chp5-p138-large-still-lifes']
    still_life_notes = note_context(still_life)
    revise(by_id, 'st-chp5-p138-large-still-lifes',
           subject='cand-3084', object_='cand-6150',
           predicate='painted_large_still_lifes_with_figures',
           claim='Haskell identifies large still lifes with figures as part of Cerquozzi’s work.',
           quote='his large still lifes with figures',
           candidates=['cand-3084', 'cand-6150'],
           qualification='The work group is unnamed; note 2 and the detailed description are retained below.',
           line_start=84, line_end=84, relation=True)
    add('large-still-lifes-grapes-and-figures-described', 'cand-6150', None,
        'described_with_grapes_and_sentimentally_or_erotically_posed_figures', 84, 84,
        'lush clusters of grapes cascading down over prettified boys and girls, somewhat sentimentally or erotically posed',
        'Haskell describes the still lifes as showing lush grape clusters over prettified boys and girls posed somewhat sentimentally or erotically.',
        ['cand-6150'],
        'The people are unnamed; “prettified”, “sentimentally” and “erotically” are Haskell’s characterizations. Footnote 2 cites Briganti 1954.',
        False, extra_qualifiers=still_life_notes)

    revise(by_id, 'st-chp5-p138-massimi-appeal-and-collection',
           subject='cand-1564', object_='cand-6151',
           predicate='owned_four_country_life_scenes_by',
           claim='Haskell says Cardinal Camillo Massimi owned four country-life scenes by Cerquozzi.',
           quote='the owner of four scenes of country life by\nCerquozzi.',
           candidates=['cand-1564', 'cand-6151', 'cand-3084'],
           qualification='The four scenes are an unnamed work group; no titles or individual identities are supplied.',
           line_start=86, line_end=87, relation=True)
    for suffix, artist_id, artist_name, quote in [
        ('massimi-admired-claude', 'cand-0767', 'Claude', 'the admirer of\nClaude'),
        ('massimi-admired-poussin', 'cand-1984', 'Poussin', 'Claude, Poussin'),
        ('massimi-admired-velasquez', 'cand-2709', 'Velasquez', 'Poussin and Velasquez'),
    ]:
        add(suffix, 'cand-1564', artist_id, 'admired', 85, 86, quote,
            f'Haskell identifies Cardinal Massimi as an admirer of {artist_name}.',
            ['cand-1564', artist_id],
            'These names are split from the source’s list of artists Massimi admired.', True)
    add('cerquozzi-paint-quality-presumably-appealed-to-massimi', 'cand-3084', 'cand-1564',
        'presumably_appealed_to', 85, 86,
        'This, presumably, was the appeal of his work to a cultivated connoisseur such as Cardinal Massimi',
        'Haskell presumes that the paint and colour qualities just described appealed to Cardinal Camillo Massimi.',
        ['cand-3084', 'cand-1564'],
        'Retain “presumably”; “This” refers to the aesthetic qualities in the preceding sentence, not a separately identified work.', True)

    revise(by_id, 'st-chp5-p138-observation-contrast',
           subject='cand-3084', object_='cand-1351',
           predicate='contrasted_with_passeri_claim_about_van_laer',
           claim='Haskell contrasts Cerquozzi’s ability to move beyond direct observation with Passeri’s claim about Van Laer’s unaltered observation of life.',
           candidates=['cand-3084', 'cand-1351', 'cand-1856', 'cand-11934'],
           qualification='The quoted “without any kind of alteration” is Passeri’s claim about Van Laer, not a direct claim that Cerquozzi followed the same practice. The scan reads “life” where S0 OCR reads “Use”; S0 remains unchanged.',
           line_start=84, line_end=85, relation=True)

    revise(by_id, 'st-chp5-p138-paint-and-colour',
           subject='cand-3084', object_=None,
           predicate='paint_and_colour_admired_as_crushed_jewels',
           claim='Haskell says contemporaries could admire the exquisite quality of Cerquozzi’s paint and colour, which appeared like crushed jewels.',
           candidates=['cand-3084'],
           qualification='This is a contemporary aesthetic judgment attributed through Haskell; S0 reads “Eke” where the scan reads “like”. Footnote 3 cites Passeri p.288; S0 is unchanged.',
           line_start=85, line_end=85, relation=False,
           extra_qualifiers={'reported_source': 'Passeri, p.288 (via footnote 3)'})

    revise(by_id, 'st-chp5-p138-patronage-political-shift',
           subject='cand-3084', object_='cand-11932',
           predicate='position_affected_by_death_of',
           claim='Haskell says Cerquozzi’s position was naturally affected by the death of Urban VIII.',
           quote='Cerquozzi’s position was naturally affected by the death of Urban VIII',
           candidates=['cand-3084', 'cand-0209', 'cand-11932'],
           qualification='This is Haskell’s causal framing; no date for the event is added.',
           line_start=93, line_end=93, relation=True)
    add('exclusive-french-influence-came-to-an-end', 'cand-6157', None,
        'came_to_an_end', 93, 93,
        'when exclusive French influence came to an end',
        'Haskell says exclusive French influence came to an end after Urban VIII’s death.',
        ['cand-6157', 'cand-0209', 'cand-11932'],
        'This is the author’s political-periodization; no individual French actors are named.', False)
    add('spanish-party-began-to-occupy-centre-stage', 'cand-6158', None,
        'began_to_occupy_centre_stage', 93, 93,
        'the Spanish party, began to occupy the centre of the stage',
        'Haskell says the Spanish party began to occupy the centre of the stage.',
        ['cand-6158'],
        'The group remains unnamed and its membership is not inferred.', False)
    add('cerquozzi-natural-patrons-were-spanish-party', 'cand-3084', 'cand-6158',
        'had_natural_patrons_in', 93, 93,
        'his natural patrons, the Spanish party',
        'Haskell identifies the Spanish party as Cerquozzi’s natural patrons.',
        ['cand-3084', 'cand-6158'],
        'This is Haskell’s characterization; it does not establish a formal organization or identify members.', True)

    revise(by_id, 'st-chp5-p138-realism-waterloo-comparison',
           subject='cand-6152', object_='cand-6159',
           predicate='detachment_helped_stress_realism',
           claim='Haskell says detachment in these battle scenes helped stress their “realism”.',
           quote='Such detachment also played its part in stressing the\n‘realism’ of the scene.',
           candidates=['cand-3084', 'cand-6152', 'cand-6159'],
           qualification='This is Haskell’s interpretation of the scenes; “realism” remains a quoted characterization.',
           line_start=90, line_end=91, relation=True)
    add('battle-imagery-foreshadowed-stendhals-view-of-waterloo', 'cand-6152', 'cand-6155',
        'almost_seemed_to_foreshadow_view_of', 91, 92,
        'The anti-heroic confusion, the smoke rising from distant battle\u00ad\n- fields—at times these almost seem to foreshadow Stendhal’s equally incoherent, though far more subtle, view of Waterloo',
        'Haskell says the battle scene’s anti-heroic confusion and smoke at times almost seem to foreshadow Stendhal’s view of Waterloo.',
        ['cand-6152', 'cand-6154', 'cand-2509', 'cand-6155'],
        'Retain “at times almost seem” and the comparative evaluation. The scan breaks “battle-fields” across a line and ends at “Waterloo.”; S0 OCR tail marks remain unaltered.', True)

    revise(by_id, 'st-chp5-p138-saxl-battle-analysis',
           subject='cand-3084', object_='cand-6154',
           predicate='work_exemplified_analysis_of',
           claim='Haskell says Cerquozzi’s battle work demonstrates the truth of Fritz Saxl’s “battle scene without a hero” analysis.',
           quote='His work in this field demonstrates the truth of Fritz Saxl’s subtle analysis of the ‘battle scene without a hero’',
           candidates=['cand-3084', 'cand-6152', 'cand-6153', 'cand-6154'],
           qualification='Keep the interpretation attributed to Saxl through Haskell. Footnote 4 cites Saxl.',
           line_start=89, line_end=89, relation=True)
    sax_context = note_context(by_id['st-chp5-p138-saxl-battle-analysis'])
    add('battle-pictures-for-society-indirectly-affected-by-wars', 'cand-6152', None,
        'painted_for_society_indirectly_affected_by_wars', 89, 89,
        'pictures painted for a society that was only indirectly affected by the wars that raged throughout Europe during most of the seventeenth century',
        'Haskell, applying Saxl’s analysis, describes the battle pictures as painted for a society only indirectly affected by the wars that raged across Europe during most of the seventeenth century.',
        ['cand-6152', 'cand-11933', 'cand-3462'],
        'This is a broad social-context claim in Haskell’s presentation of Saxl, not a named audience or a specific war.', False,
        extra_qualifiers=sax_context)

    revise(by_id, 'st-chp5-p138-vicarious-participation',
           subject='cand-6152', object_='cand-11933',
           predicate='offered_vicarious_participation_in',
           claim='Haskell says battle pictures offered viewers an opportunity for vicarious participation in wars changing Europe.',
           quote='the attraction of these pictures lay in the opportunity that they offered for vicarious participation in battles that were changing the shape of Europe',
           candidates=['cand-6152', 'cand-11933', 'cand-3462'],
           qualification='This describes the pictures’ appeal, not actual participation in war; Haskell says a particular victory hardly mattered.',
           line_start=90, line_end=90, relation=True)
    add('victory-for-whom-hardly-mattered', 'cand-6152', None,
        'victory_side_described_as_immaterial_to_appeal', 90, 90,
        'Victory for whom? That hardly mattered',
        'Haskell says it hardly mattered to the pictures’ appeal which side won.',
        ['cand-6152'], 'Retain the rhetorical question and authorial interpretation.', False)
    add('italy-described-as-a-backwater', 'cand-3461', None,
        'described_as_backwater', 90, 90,
        'far outside the backwater into which Italy had now sunk',
        'Haskell characterizes Italy as a backwater in relation to the European wars discussed.',
        ['cand-3461', 'cand-3462'], 'This is Haskell’s evaluative framing, not a neutral geographic description.', False)

    revise(by_id, 'st-chp5-p138-work-characterization',
           subject='cand-3084', object_='cand-11931',
           predicate='was_friend_of',
           claim='Haskell describes Cerquozzi as a friend of princes and prelates.',
           quote='the friend of princes and prelates',
           candidates=['cand-3084', 'cand-11931'],
           qualification='The social group is unnamed; no individual members or organization are inferred.',
           line_start=83, line_end=83, relation=True)
    add('cerquozzi-speech-described-as-coarse-and-vulgar', 'cand-3084', None,
        'speech_described_as_coarse_and_vulgar', 83, 83,
        'yet coarse and vulgar in his speech',
        'Haskell describes Cerquozzi’s speech as coarse and vulgar.',
        ['cand-3084'],
        'Retain the contrast with the preceding descriptions of his work and social friendships; this is Haskell’s characterization.', False)
    add('cerquozzi-careful-and-conscientious-in-work', 'cand-3084', None,
        'careful_and_conscientious_in_work', 83, 83,
        'work',
        'Haskell characterizes Cerquozzi as careful and conscientious in his work.',
        ['cand-3084'],
        'Completes the p.137 L79 fragment “careful and conscientious in his”; see the linked statement in the preceding segment.', False,
        extra_qualifiers={'continued_from_statement_id': P137_CONTINUATION})

    new_mentions = [
        make_mention(32, 'cand-11931', 'princes and prelates', 83,
                     'Unnamed social group described as Cerquozzi’s friends; no members are identified.'),
        make_mention(33, 'cand-11932', 'death of Urban VIII', 93,
                     'Event said by Haskell to have affected Cerquozzi’s position; no date is added.'),
        make_mention(34, 'cand-11933', 'the wars that raged throughout Europe', 89,
                     'Collective war reference in Haskell’s presentation of Saxl; no individual conflict is identified.'),
    ]

    mention_remaps = {
        'm-chp5-sec-iii-l82-93-002': 'cand-11934',
        'm-chp5-sec-iii-l82-93-007': 'cand-11934',
    }
    mention_by_id = {r['mention_id']: r for r in mentions}
    if not set(mention_remaps).issubset(mention_by_id):
        raise SystemExit(f'missing mentions for remap: {sorted(set(mention_remaps) - set(mention_by_id))}')
    expected_old_candidates = {
        'm-chp5-sec-iii-l82-93-002': 'cand-6099',
        'm-chp5-sec-iii-l82-93-007': 'cand-6099',
    }
    if any(mention_by_id[mid].get('candidate_id') != old for mid, old in expected_old_candidates.items()):
        raise SystemExit('mention remap precondition failed')
    for mid, new_candidate in mention_remaps.items():
        mention_by_id[mid]['candidate_id'] = new_candidate
    mention_by_id['m-chp5-sec-iii-l82-93-002']['note'] = 'S0 OCR reads “Use”; the print reads “life”. This broad subject-matter expression is kept distinct from the Bambocciate category.'
    mention_by_id['m-chp5-sec-iii-l82-93-007']['note'] = 'S0 OCR reads “Use”; the print reads “life”. This phrase concerns surrounding life, not the Bambocciate category.'

    # Move the p.137 note-3 backlink from the market-pressure sentence to the
    # high-price clause, which is where marker 3 appears in print.
    pressure = by_id['st-chp5-p137-patron-pressure-and-high-prices']
    high_prices = by_id['st-chp5-p137-popular-bambocciate-continued-to-fetch-high-prices']
    citation_keys = ('citation_segment_id', 'citation_source_line_start', 'citation_source_line_end')
    if pressure['qualifiers'].get('citation_source_line_start') != 144:
        raise SystemExit('p.137 note-3 citation precondition failed')
    for key in citation_keys:
        if key in pressure['qualifiers']:
            high_prices['qualifiers'][key] = pressure['qualifiers'].pop(key)

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
    if by_id[PENDING_CONTINUATION]['qualifiers'].get('relation_candidate') is not None:
        raise SystemExit('p.138 continuation should remain unset until p.139 is read')
    if by_id[P137_CONTINUATION]['qualifiers'].get('relation_candidate') is not False:
        raise SystemExit('p.137 continuation was not classified')

    available_candidates = candidate_ids | new_candidate_ids
    rows_to_check = [by_id[sid] for sid in TARGET_IDS | {P137_CONTINUATION}] + new_statements
    for row in rows_to_check:
        q = row.get('qualifiers', {})
        for cid in q.get('mentioned_candidate_ids', []) or []:
            if cid and cid not in available_candidates:
                raise SystemExit(f'candidate reference missing: {row["statement_id"]} -> {cid}')
        if q.get('relation_candidate') is True:
            if not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
                raise SystemExit(f'relation candidate missing endpoint: {row["statement_id"]}')
            if row['subject_candidate_id'] not in available_candidates or row['object_candidate_id'] not in available_candidates:
                raise SystemExit(f'relation candidate endpoint missing: {row["statement_id"]}')
        if row['statement_id'] in new_statement_ids:
            if row['original_quote'] not in '\n'.join(source_lines[q['source_line_start'] - 1:q['source_line_end']]):
                raise SystemExit(f'quote failed source check: {row["statement_id"]}')
    for row in new_mentions:
        if segment_text[int(row['start_char']):int(row['end_char'])] != row['surface_form']:
            raise SystemExit(f'mention span failed: {row["mention_id"]}')

    pending_rows = [by_id[sid] for sid in sorted(TARGET_IDS)]
    classified = [r for r in pending_rows if r['statement_id'] != PENDING_CONTINUATION]
    target_relations = sum(r['qualifiers']['relation_candidate'] is True for r in classified)
    target_nonrelations = sum(r['qualifiers']['relation_candidate'] is False for r in classified)
    new_relation_count = sum(r['qualifiers']['relation_candidate'] is True for r in new_statements)

    if args.apply:
        paths = [STATEMENTS, CANDIDATES, MENTIONS]
        backups = [p.with_name(p.name + BACKUP_TAG) for p in paths]
        if any(p.exists() for p in backups):
            raise SystemExit('backup already exists; refusing to overwrite')
        for src, backup in zip(paths, backups):
            shutil.copy2(src, backup)
        for row in new_candidates:
            candidates.append({key: row.get(key, '') for key in candidate_fields})
        for row in new_mentions:
            mentions.append({key: row.get(key, '') for key in mention_fields})
        statements.extend(new_statements)
        temp_paths = [p.with_name(p.name + '.tmp-s2-chp5-p138') for p in paths]
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
        print('applied p.138 S2 semantic corrections and p.137 continuation closure')
        print('backups:', ', '.join(p.name for p in backups))
    else:
        print('PREVIEW only; no table writes')
    print(f'p.138 targets: {len(TARGET_IDS)}; classified now: {len(classified)}; pending p.139 continuation: 1')
    print(f'p.138 target classification: relation candidates {target_relations}; non-relational claims {target_nonrelations}')
    print(f'new candidates: {len(new_candidates)}; new statements: {len(new_statements)} ({new_relation_count} relations); new mentions: {len(new_mentions)}')
    print('p.137 continuation: classified non-relational; linked to p.138 careful-work completion')
    print('TARGET REVIEW:')
    for row in sorted(pending_rows, key=lambda r: r['statement_id']):
        q = row.get('qualifiers', {})
        status = 'pending-continuation' if row['statement_id'] == PENDING_CONTINUATION else str(q['relation_candidate']).lower()
        print(f"  {status} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']} | {q.get('claim', '')}")
    print('ADDED CLAIM REVIEW:')
    for row in new_statements:
        q = row['qualifiers']
        print(f"  {str(q['relation_candidate']).lower()} | {row['subject_candidate_id']} -> {row['object_candidate_id']} | {row['predicate']} | {q['claim']}")
    print('MENTION REMAPS:', ', '.join(f'{mid}: {expected_old_candidates[mid]} -> {new}' for mid, new in mention_remaps.items()))


if __name__ == '__main__':
    main()
