from __future__ import annotations
import argparse, csv, hashlib, json, shutil
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge' / 'tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
MENTIONS = TABLES / 'mentions.csv'
CANDIDATES = TABLES / 'entity-candidates.csv'
COVERAGE = TABLES / 's2-coverage.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '10_CHP-10_sec_ii.md'
SEGMENT = 'chp-10:10_CHP-10_sec_ii:l248-256'
P328_SEGMENT = 'chp-10:10_CHP-10_sec_ii:l241-246'
NOTE_SEGMENT = 'chp-10:10_CHP-10_sec_ii:l273-349'
SOURCE_FILE = '02-sources/02-Markdown/10_CHP-10_sec_ii.md'
BACKUP_SUFFIX = '.bak-s2-chp10-p329-semantic-reconciliation-20261014'
EXPECTED = {
    STATEMENTS.name: 'd4601e579916f3f4d1fc6bda05af474ba860aaf39b7a8c22ea67691a2088a6e1',
    MENTIONS.name: '5d32019321b31e4a000decbbb58ba5b4331a6c81799e367b73fe85bb7658012a',
    CANDIDATES.name: '4e3e71204430eed09fa9dd7f829e557ccb2f0db052bdcda4e585b8f2ead67ec3',
    COVERAGE.name: '93f51e35cc5b6ffd5f24a0ece9b15be7b74b45974260fbe65ca193481cb2519d',
    SOURCE.name: '25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ('\n'.join(json.dumps(row, ensure_ascii=False) for row in rows) + '\n').encode('utf-8')


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def dump_csv(fields: list[str], rows: list[dict]) -> bytes:
    stream = StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def source_quote(lines: list[str], first: int, last: int, start: str, end: str) -> str:
    block = '\n'.join(lines[first - 1:last])
    a = block.find(start)
    if a < 0:
        raise ValueError(f'quote start missing at {first}-{last}: {start!r}')
    b = block.find(end, a if start == end else a + len(start))
    if b < 0:
        raise ValueError(f'quote end missing at {first}-{last}: {end!r}')
    return block[a:b + len(end)]


def new_statement(sid: str, subject: str | None, obj: str | None, predicate: str,
                  quote: str, start: int, end: int, claim: str, qualification: str,
                  mentions: list[str], relation: bool, **extra: object) -> dict:
    qualifiers: dict[str, object] = {
        'source_line_start': start, 'source_line_end': end,
        'printed_page': 329, 'pdf_physical_page': 62,
        'claim': claim, 'speaker': 'Haskell', 'text_layer': 'authorial narrative',
        'qualification': qualification, 'mentioned_candidate_ids': mentions,
        'relation_candidate': relation,
    }
    qualifiers.update(extra)
    return {
        'statement_id': sid, 'segment_id': SEGMENT,
        'subject_candidate_id': subject, 'object_candidate_id': obj,
        'predicate': predicate, 'qualifiers': qualifiers,
        'original_quote': quote, 'origin': 'book', 'source_file': SOURCE_FILE,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after exact-hash and row preflight')
    args = parser.parse_args()
    paths = [STATEMENTS, MENTIONS, CANDIDATES, COVERAGE, SOURCE]
    hashes = {path.name: sha(path) for path in paths}
    if hashes != EXPECTED:
        raise SystemExit(f'preflight hash mismatch; no writes made: {hashes}')

    source_lines = SOURCE.read_text(encoding='utf-8').splitlines()
    source_text = '\n'.join(source_lines)
    segment_text = '\n'.join(source_lines[247:256])
    statements = load_jsonl(STATEMENTS)
    by_id = {row['statement_id']: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit('duplicate statement_id in current table')
    p329_ids = {
        'st-chp10-p329-academy-1724-plan',
        'st-chp10-p329-academy-established-1756',
        'st-chp10-p329-academy-hierarchy-chronology',
        'st-chp10-p329-academy-subject-hierarchy',
        'st-chp10-p329-artist-status-debate-open',
        'st-chp10-p329-artists-graded-by-subject',
        'st-chp10-p329-committee-report-economic-argument',
        'st-chp10-p329-didactic-function',
        'st-chp10-p329-diletto-ed-utile',
        'st-chp10-p329-foreign-market-chain',
        'st-chp10-p329-gozzi-political-economists',
        'st-chp10-p329-gozzi-social-value',
        'st-chp10-p329-painting-teaches-and-relaxes',
        'st-chp10-p329-princely-commissions-and-trade',
        'st-chp10-p329-senate-commercial-benefit',
        'st-chp10-p329-utilitarian-patronage-defense',
        'st-chp10-p329-venetian-economic-caveat',
        'st-chp10-p329-zanetti-useful-arts',
    }
    current_p329 = {row['statement_id'] for row in statements if row.get('segment_id') == SEGMENT}
    if current_p329 != p329_ids:
        raise SystemExit(f'p.329 statement set mismatch: {sorted(current_p329 ^ p329_ids)}')
    if any('relation_candidate' in by_id[sid].get('qualifiers', {}) for sid in p329_ids):
        raise SystemExit('p.329 expected all baseline rows to be unset')
    p328_fragment = by_id.get('st-chp10-p328-gozzi-traditional-reply-open')
    p329_social = by_id['st-chp10-p329-gozzi-social-value']
    if not p328_fragment or p328_fragment['qualifiers'].get('continuation_to_statement_id') != p329_social['statement_id']:
        raise SystemExit('p.328/p.329 Gozzi continuation preflight mismatch')

    candidate_fields, candidates = load_csv(CANDIDATES)
    candidate_ids = {row['candidate_id'] for row in candidates}
    numeric_ids = [int(row['candidate_id'].split('-', 1)[1]) for row in candidates
                   if row['candidate_id'].startswith('cand-') and row['candidate_id'].split('-', 1)[1].isdigit()]
    if max(numeric_ids) != 12116 or 'cand-12117' in candidate_ids:
        raise SystemExit(f'candidate sequence changed; max={max(numeric_ids)}, cand-12117 exists={"cand-12117" in candidate_ids}')

    mention_fields, mentions = load_csv(MENTIONS)
    if any(row.get('mention_id') == 'm-s2-ch10-p329-0043' for row in mentions):
        raise SystemExit('new p.329 mention ID already exists')
    expected_mentions = {'m-s2-ch10-p329-0015': 'cand-4439', 'm-s2-ch10-p329-0016': 'cand-4591'}
    mention_by_id = {row['mention_id']: row for row in mentions}
    for mid, old_candidate in expected_mentions.items():
        if mention_by_id.get(mid, {}).get('candidate_id') != old_candidate:
            raise SystemExit(f'mention mapping preflight mismatch for {mid}')

    def update(sid: str, *, predicate: str | None = None, subject: str | None = None,
               obj: str | None = None, set_subject: bool = False, set_obj: bool = False,
               quote: str | None = None, claim: str | None = None,
               qualification: str | None = None, mention_ids: list[str] | None = None,
               relation: bool | None = None, start: int | None = None, end: int | None = None,
               remove: tuple[str, ...] = (), **extra: object) -> None:
        row = by_id[sid]
        q = row.setdefault('qualifiers', {})
        if predicate is not None: row['predicate'] = predicate
        if set_subject: row['subject_candidate_id'] = subject
        if set_obj: row['object_candidate_id'] = obj
        if quote is not None: row['original_quote'] = quote
        if claim is not None: q['claim'] = claim
        if qualification is not None: q['qualification'] = qualification
        if mention_ids is not None: q['mentioned_candidate_ids'] = mention_ids
        if relation is not None: q['relation_candidate'] = relation
        if start is not None: q['source_line_start'] = start
        if end is not None: q['source_line_end'] = end
        for key in remove: q.pop(key, None)
        q.update(extra)

    # The p.328 open clause closes first with Gozzi's traditional glory argument, not the later social-value argument.
    glory_id = 'st-chp10-p329-gozzi-traditional-glory-reply'
    p328q = p328_fragment['qualifiers']
    p328q['continuation_to_statement_id'] = glory_id
    p328q['continuation_status'] = 'closed'
    p328q['continuation_closed_by_segment_id'] = SEGMENT
    p328q['continuation_closed_by_statement_id'] = glory_id
    update('st-chp10-p329-gozzi-social-value',
        predicate='advanced_tentative_social_value_argument_for',
        quote=source_quote(source_lines, 249, 249, 'he refers almost tentatively to their social value.', 'families are kept alive.'),
        claim='Haskell says Gozzi tentatively turned from the traditional national-glory reply to the arts’ social value: they employ people, circulate money and keep families alive.',
        qualification='Reported by Haskell as Gozzi’s argument. The fragment at p.328 is closed by the separate traditional-reply statement immediately before this claim.',
        mention_ids=['cand-1222', 'cand-1805'], relation=True,
        start=249, end=249,
        remove=('continuation_from_segment_id','continuation_from_statement_id','continuation_prefix','continuation_status'))

    update('st-chp10-p329-academy-1724-plan',
        predicate='academy_planned_to_attract_foreign_travellers_to_venetian_territory',
        set_subject=True, subject='cand-0005', set_obj=True, obj='cand-3678',
        quote=source_quote(source_lines, 255, 255, 'As early as 1724 it had been planned', 'Florence, Bologna and Rome’.3'),
        claim='Haskell says a plan existed by 1724 to found the Academy of Painting and Sculpture in order to attract foreigners travelling through Venetian territory toward Florence, Bologna and Rome.',
        qualification='The planner is not named, and the plan is not said to have been implemented in 1724; the intended destination is Venetian territory.',
        mention_ids=['cand-0005','cand-3678','cand-1041','cand-3398','cand-4490'], relation=True,
        start=255, end=255,
        relation_candidate_note='Source-supported institutional purpose; the planner remains unspecified. S2 candidate only.',
        footnote_marker=3, footnote_segment=NOTE_SEGMENT,
        footnote_refs=[{'marker':3,'segment_id':NOTE_SEGMENT,'source_line':345}],
        footnote_statement_ids=['st-chp10-p329-n03-bassi-academy-study','st-chp10-p329-n03-fogolari-academy-study'],
        footnote_body_link_status='linked')

    update('st-chp10-p329-academy-established-1756',
        predicate='academy_established_in_1756',
        quote=source_quote(source_lines, 255, 255, 'When in 1756 the Academy was finally established', 'When in 1756 the Academy was finally established'),
        claim='Haskell dates the Academy’s establishment to 1756.',
        qualification='The passage does not name the establishing agent; the comparison with earlier academies in other towns is recorded separately.',
        mention_ids=['cand-0005'], relation=False, start=255, end=255)
    update('st-chp10-p329-academy-hierarchy-chronology',
        predicate='academy_curriculum_looked_back_rather_than_anticipating_neoclassicist_opinions',
        quote=source_quote(source_lines, 255, 255, 'looked back to a much earlier period', 'opinions of the neo-classicists.'),
        claim='Haskell characterizes the Academy’s curriculum as looking back to an earlier period rather than anticipating neo-classicist opinions.',
        qualification='This is Haskell’s interpretive comparison of intellectual chronology, not a direct influence claim.',
        mention_ids=['cand-0005','cand-6439'], relation=False, start=255, end=255)
    update('st-chp10-p329-academy-subject-hierarchy',
        predicate='academy_subordinated_view_painting',
        quote=source_quote(source_lines, 255, 255, 'complete subordination of such inferior branches as view painting', 'complete subordination of such inferior branches as view painting'),
        claim='Haskell says the Academy’s subject hierarchy completely subordinated view painting.',
        qualification='This is Haskell’s account of the curriculum; the statement is separated from the separate supremacy accorded to history painting.',
        mention_ids=['cand-0005','cand-9848'], relation=True, start=255, end=255,
        relation_candidate_note='Curricular hierarchy described by Haskell; S2 candidate only, not a formal S6 relation.')
    update('st-chp10-p329-artist-status-debate-open', relation=False,
        qualification='The sentence is completed on p.330 and says the discussion occurred shortly after the Academy was instituted. The Academy is temporal context here; Haskell does not say it caused the debate.',
        mention_ids=['cand-0140','cand-0005'])
    update('st-chp10-p329-artists-graded-by-subject',
        predicate='artists_graded_by_subjects_they_painted', set_subject=True, subject=None,
        set_obj=True, obj=None, relation=False,
        claim='Haskell says artists were firmly graded in a hierarchy according to the subjects they painted.',
        qualification='The agent imposing this hierarchy is not identified; the adjacent Academy discussion does not establish that the institution formally graded the artists.',
        mention_ids=[], start=255, end=255)
    update('st-chp10-p329-committee-report-economic-argument',
        predicate='committee_reported_liberal_arts_benefit_to_venice',
        quote=source_quote(source_lines, 253, 254, 'the liberal arts, it concluded,', 'come here.2'),
        claim='Haskell reports that the 1772 committee concluded that the liberal arts attract foreigners and provide pleasure and reputation to the State.',
        qualification='The report is cited through Haskell’s footnote 2; the committee report was not independently consulted. Its initiating authority is not named.',
        mention_ids=['cand-9849','cand-9850','cand-3678'], relation=True,
        start=253, end=254,
        relation_candidate_note='Source-reported institutional argument about benefit to the State; S2 candidate only.',
        speaker='Official committee (as reported by Haskell)', text_layer='committee conclusion reported in authorial narrative',
        footnote_marker=2, footnote_segment=NOTE_SEGMENT,
        footnote_refs=[{'marker':2,'segment_id':NOTE_SEGMENT,'source_line':344}],
        footnote_statement_ids=['st-chp10-p329-n02-relazione-in-sagredo'], footnote_body_link_status='linked')
    update('st-chp10-p329-didactic-function', relation=True,
        qualification='Haskell reports Zanetti’s use of an older theory; the quoted maxim is not independently checked against Zanetti’s publication.',
        relation_candidate_note='Zanetti’s reported appeal to the didactic theory; S2 candidate only.')
    update('st-chp10-p329-diletto-ed-utile', relation=True,
        qualification='This is Haskell’s characterization of the relation between the teaching/relaxation claim and the older theory, not an independently verified history of the phrase.',
        relation_candidate_note='Conceptual relation as characterized by Haskell; S2 candidate only.')
    update('st-chp10-p329-foreign-market-chain', relation=False,
        qualification='This is a generalized economic mechanism in Zanetti’s reported argument; the artists, visitors, works and buyers are not individually identified as endpoints.',
        mention_ids=['cand-9846'])
    update('st-chp10-p329-gozzi-political-economists',
        predicate='implicitly_answered_charges_by', set_subject=True, subject='cand-1222',
        set_obj=True, obj='cand-12117',
        claim='Haskell infers that Gozzi’s argument implicitly answered charges by the unnamed “new political economists”.',
        qualification='This is Haskell’s interpretation, not an explicit statement by Gozzi. The source names a plural intellectual category but no individuals, organization or specific doctrine.',
        mention_ids=['cand-1222','cand-12117'], relation=True,
        relation_candidate_note='Source-derived, unnamed intellectual category; candidate type term preserves the phrase without inventing membership.')
    update('st-chp10-p329-painting-teaches-and-relaxes', relation=True,
        qualification='Haskell reports this as Zanetti’s concession about painting; it is not an independent empirical claim about every viewer.',
        relation_candidate_note='Zanetti’s reported argument about painting’s functions; S2 candidate only.')
    update('st-chp10-p329-princely-commissions-and-trade', relation=True,
        qualification='This is Zanetti’s reported economic argument, not proof that each foreign commission returned a particular sum to Italy.',
        relation_candidate_note='Qualified economic relation in Zanetti’s argument; S2 candidate only.')
    update('st-chp10-p329-senate-commercial-benefit',
        predicate='senate_expected_commercial_benefit_from_academy',
        set_subject=True, subject='cand-8129', set_obj=True, obj='cand-0005',
        claim='Haskell says the Senate hoped the Academy arrangement would yield commercial benefit, while describing the calculation as characteristically shrewd yet naïve.',
        qualification='The source reports the Senate’s expectation and Haskell’s evaluation; it does not establish that the expected benefit occurred.',
        mention_ids=['cand-8129','cand-0005','cand-3678'], relation=True,
        relation_candidate_note='The “arrangement” refers to the Academy; this is an expectation, not a realized benefit.')
    update('st-chp10-p329-utilitarian-patronage-defense', relation=True,
        qualification='Haskell describes Zanetti’s argument for painting, more precisely its patronage, on utilitarian grounds.',
        relation_candidate_note='Reported intellectual position of Zanetti; S2 candidate only.')
    update('st-chp10-p329-venetian-economic-caveat', relation=False,
        mention_ids=['cand-3678','cand-3461','cand-8983','cand-5120','cand-5529','cand-9161'],
        qualification='Haskell’s qualified economic caveat. The named countries are geographic origins/destinations in this sentence, not political actors; the claim does not identify individual artists or quantify the sums.')
    update('st-chp10-p329-zanetti-useful-arts', relation=True,
        qualification='Haskell reports the view Zanetti developed eleven years after Gozzi’s 1760 argument; Zanetti’s underlying text is not independently consulted.',
        relation_candidate_note='Reported argument from Zanetti to the useful-arts concept; S2 candidate only.')

    new_rows = [
        new_statement('st-chp10-p329-state-academy-single-venture', 'cand-3678', 'cand-0005',
            'made_single_important_venture_into_art_patronage',
            source_quote(source_lines, 255, 255, 'It was ideas of this kind that persuaded the State', 'realm of art patronage.'),
            255, 255, 'Haskell says these ideas persuaded the Venetian State to make its single important venture into art patronage, identified in the next sentence as the Academy.',
            '“Single important” is Haskell’s characterization. The Academy identification follows directly in context; this does not claim that the planned 1724 foundation was immediately realized.',
            ['cand-3678','cand-0005'], True,
            relation_candidate_note='State-to-Academy patronage relation as described by Haskell; S2 candidate only.'),
        new_statement(glory_id, 'cand-1222', 'cand-1805',
            'answered_criticism_with_national_glory_argument',
            source_quote(source_lines, 249, 249, 'the finest claim to glory of the country that produces them,', 'the finest claim to glory of the country that produces them,'),
            249, 249, 'Haskell says Gozzi’s traditional reply was that the buildings, altars and pictures represented the producing country’s finest claim to glory.',
            'This completes the unfinished p.328 clause. “These” refers to buildings, altars and pictures mentioned with the criticism on p.328; the claim is attributed to Gozzi through Haskell.',
            ['cand-1222','cand-1805'], True,
            continuation_from_segment_id=P328_SEGMENT,
            continuation_from_statement_id='st-chp10-p328-gozzi-traditional-reply-open',
            continuation_prefix='After making the traditional reply that these represent', continuation_status='closed',
            relation_candidate_note='Source-reported argument in Gozzi’s reply; S2 candidate only.'),
        new_statement('st-chp10-p329-academy-history-painting-supremacy', 'cand-0005', 'cand-6179',
            'accorded_absolute_supremacy_to_history_painting',
            source_quote(source_lines, 255, 255, 'absolute supremacy of history painting', 'absolute supremacy of history painting'),
            255, 255, 'Haskell says the Academy’s subject hierarchy gave history painting absolute supremacy.',
            'This is a separate curricular judgment from the subordination of view painting.',
            ['cand-0005','cand-6179'], True,
            relation_candidate_note='Curricular hierarchy described by Haskell; S2 candidate only, not a formal S6 relation.'),
        new_statement('st-chp10-p329-committee-1772-established', 'cand-9849', None,
            'committee_set_up_in_1772_to_consider_economic_situation',
            source_quote(source_lines, 252, 253, '1772 by an official committee set up', 'general economic situation:'),
            253, 253, 'Haskell says an official committee was set up in 1772 to consider the general economic situation.',
            'The committee’s establishing authority and formal name are not supplied.',
            ['cand-9849'], False),
        new_statement('st-chp10-p329-academy-established-after-similar-institutions', 'cand-0005', None,
            'established_after_similar_institutions_in_italy_and_europe',
            source_quote(source_lines, 255, 255, '(after a number of similar institutions', 'other towns of Italy and Europe)'),
            255, 255, 'Haskell says the Venetian Academy was established after similar institutions had appeared in other Italian and European towns.',
            'The other academies are not named; this is comparative chronology, not evidence of a direct institutional relationship.',
            ['cand-0005','cand-3461','cand-3462'], False),
        new_statement('st-chp10-p329-academy-organization-new-theories', 'cand-0005', 'cand-9846',
            'organization_did_not_reflect_new_theories_about_painting_value',
            source_quote(source_lines, 255, 255, 'The actual organisation of the body, however, reflected none of the new theories', 'had been attracting attention'),
            255, 255, 'Haskell says the Academy’s organization reflected none of the newer theories about painting’s value then attracting attention.',
            'This is Haskell’s assessment of the Academy’s organization; the particular theories are not exhaustively identified in this clause.',
            ['cand-0005','cand-9846'], False),
    ]
    for row in new_rows:
        if row['original_quote'] not in source_text:
            raise SystemExit(f"new quote not in S0 source: {row['statement_id']}")
        if row['statement_id'] in by_id:
            raise SystemExit(f"new statement ID exists: {row['statement_id']}")
        statements.append(row)
        by_id[row['statement_id']] = row

    # A source-defined term records the otherwise unnamed intellectual group without inventing people or an institution.
    candidates.append({
        'candidate_id':'cand-12117', 'index_entry_id':'',
        'canonical_name':'Unnamed “new political economists” referred to at p.329',
        'index_page_range':'', 'suggested_type':'term', 'status':'open',
        'index_source_file':'', 'sub_entry':'',
        'detail':'Haskell says Gozzi implicitly answered charges by this unnamed plural intellectual category. No individuals, organized institution, or precise doctrine are identified; retain only the source-defined category.',
        'exclude_reason':'', 'candidate_origin':'body-mention',
        'candidate_source_ref':f'{SEGMENT}#L249',
    })
    phrase = 'the new political economists'
    start = segment_text.find(phrase)
    if start < 0:
        raise SystemExit('political economists mention not found in p.329 source segment')
    mentions.append({
        'mention_id':'m-s2-ch10-p329-0043', 'segment_id':SEGMENT,
        'candidate_id':'cand-12117', 'surface_form':phrase,
        'start_char':str(start), 'end_char':str(start+len(phrase)),
        'note':'Haskell’s unnamed plural category; no individual economists or organized institution are identified.'
    })

    # Re-type the two country mentions by their geographic role in the sentence about artists returning to Italy.
    mention_by_id['m-s2-ch10-p329-0015']['candidate_id'] = 'cand-8983'
    mention_by_id['m-s2-ch10-p329-0015']['note'] = 'England as geographic origin in Haskell’s economic caveat; use the place candidate rather than the separate polity candidate.'
    mention_by_id['m-s2-ch10-p329-0016']['candidate_id'] = 'cand-5120'
    mention_by_id['m-s2-ch10-p329-0016']['note'] = 'Spain as geographic origin in Haskell’s economic caveat; use the place candidate rather than a polity candidate from another passage.'

    coverage_fields, coverage_rows = load_csv(COVERAGE)
    coverage_match = [row for row in coverage_rows if row.get('segment_id') == SEGMENT]
    if len(coverage_match) != 1:
        raise SystemExit(f'expected one coverage row, got {len(coverage_match)}')
    coverage_match[0]['note'] = 'p.329 body semantically reviewed against the page scan; Gozzi’s p.328 fragment is closed by the separate national-glory reply before the social-value argument. Academy chronology, state planning, committee report, curriculum claims and p.330 artist-status continuation are distinguished; country mentions use geographic candidates.'

    p329_count = sum(row.get('segment_id') == SEGMENT for row in statements)
    p329_true = sum(row.get('segment_id') == SEGMENT and row.get('qualifiers',{}).get('relation_candidate') is True for row in statements)
    p329_false = sum(row.get('segment_id') == SEGMENT and row.get('qualifiers',{}).get('relation_candidate') is False for row in statements)
    p329_unset = sum(row.get('segment_id') == SEGMENT and 'relation_candidate' not in row.get('qualifiers',{}) for row in statements)
    if p329_unset != 0 or p329_count != len(p329_ids) + len(new_rows):
        raise SystemExit(f'p.329 classification result invalid: rows={p329_count} unset={p329_unset}')
    if p328q.get('continuation_to_statement_id') != glory_id or p329_social['qualifiers'].get('continuation_from_segment_id'):
        raise SystemExit('Gozzi continuation links are inconsistent')

    output_paths = [STATEMENTS, MENTIONS, CANDIDATES, COVERAGE]
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in output_paths]
    for backup in backup_paths:
        if backup.exists():
            raise SystemExit(f'backup already exists; refusing overwrite: {backup.name}')
    output_data = {
        STATEMENTS: dump_jsonl(statements), MENTIONS: dump_csv(mention_fields, mentions),
        CANDIDATES: dump_csv(candidate_fields, candidates), COVERAGE: dump_csv(coverage_fields, coverage_rows),
    }
    print('MODE', 'APPLY' if args.apply else 'PREVIEW')
    print('P329_STATEMENTS', p329_count, 'TRUE', p329_true, 'FALSE', p329_false, 'UNSET', p329_unset)
    print('ADDED_STATEMENTS',len(new_rows),'ADDED_CANDIDATES',1,'ADDED_MENTIONS',1)
    for row in new_rows: print('ADD',row['statement_id'],row['qualifiers']['relation_candidate'])
    print('REMAP', 'm-s2-ch10-p329-0015 cand-4439->cand-8983', 'm-s2-ch10-p329-0016 cand-4591->cand-5120')
    if not args.apply:
        return 0
    for backup, path in zip(backup_paths, output_paths): shutil.copy2(path, backup)
    temps=[]
    try:
        for path,data in output_data.items():
            temp=path.with_name(path.name+'.tmp-p329-semantic-reconciliation')
            temp.write_bytes(data); temps.append(temp)
        for temp,path in zip(temps,output_data.keys()): temp.replace(path)
    except Exception:
        for temp in temps:
            if temp.exists(): temp.unlink()
        raise
    print('BACKUPS',*(p.name for p in backup_paths))
    print('POST_HASHES',*(f'{p.name}={sha(p)}' for p in output_paths))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
