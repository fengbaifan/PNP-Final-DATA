import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEG = 'chp-5:05_CHP-5_sec_iii:l126-165'
BODY_PREV = 'chp-5:05_CHP-5_sec_iii:l95-101'
BODY_NEXT = 'chp-5:05_CHP-5_sec_iii:l103-113'
SOURCE = ROOT / '02-sources/02-Markdown/05_CHP-5_sec_iii.md'
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
MENTIONS = TABLES / 'mentions.csv'
COVERAGE = TABLES / 's2-coverage.csv'
BACKUP_TAG = '.bak-s2-chp5-notes-l126-165-20261013'

EXPECTED_SHA256 = {
    SOURCE: '9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a',
    STATEMENTS: 'dab99cfede698769bea412a776bd8bef52b4fb14e8f656480d5941b36a3f68a9',
    CANDIDATES: '553056eac88450a9ebfbc84102eb4847edaca8d7b8d43ffdb83042b7e55ac706',
    MENTIONS: '6be2d87d2905ce3bef8b29c39bc7e004111c8002c8d22452d1d6e771b2f07272',
    COVERAGE: 'd66d29451e2770644d5cf73fb749019279e371a083a5bf48cb7fbf467236e805',
}

RELATION_NOTE = (
    'S2 preserves a source-grounded relation candidate with its attribution, '
    'time, uncertainty, and evidence scope; this does not create an S6 formal edge.'
)
NONRELATION_NOTE = (
    'This records a scalar, chronological, source-critical, or interpretive claim, '
    'not a specific entity-to-entity relation.'
)
SOURCE_LINES = SOURCE.read_text(encoding='utf-8-sig').splitlines()
SEGMENT_LINES = SOURCE_LINES[125:165]
SEGMENT_TEXT = '\n'.join(SEGMENT_LINES)
LINE_OFFSETS = {}
offset = 0
for line_number, text in enumerate(SEGMENT_LINES, 126):
    LINE_OFFSETS[line_number] = (offset, offset + len(text), text)
    offset += len(text) + 1


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_quote(line_number, phrase, occurrence=0):
    text = SOURCE_LINES[line_number - 1]
    positions = []
    start = 0
    while True:
        pos = text.find(phrase, start)
        if pos < 0:
            break
        positions.append(pos)
        start = pos + max(1, len(phrase))
    if occurrence >= len(positions):
        raise ValueError(f'quote absent at L{line_number}: {phrase!r}')
    return text[positions[occurrence]:positions[occurrence] + len(phrase)]


def quote_between(line_number, start_marker, end_marker, occurrence=0):
    text = SOURCE_LINES[line_number - 1]
    starts = []
    cursor = 0
    while True:
        pos = text.find(start_marker, cursor)
        if pos < 0:
            break
        starts.append(pos)
        cursor = pos + len(start_marker)
    if occurrence >= len(starts):
        raise ValueError(f'start marker absent at L{line_number}: {start_marker!r}')
    start = starts[occurrence]
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise ValueError(f'end marker absent at L{line_number}: {end_marker!r}')
    return text[start:end + len(end_marker)]


def classify(row, is_relation):
    q = row.setdefault('qualifiers', {})
    q['relation_candidate'] = bool(is_relation)
    q['relation_candidate_note'] = RELATION_NOTE if is_relation else NONRELATION_NOTE


def revise(by_id, sid, *, subject=None, object_=None, predicate=None, claim=None,
           quote_text=None, qualification=None, mentioned=None, relation=None,
           extra=None):
    row = by_id[sid]
    q = row.setdefault('qualifiers', {})
    if subject is not None:
        row['subject_candidate_id'] = subject
    if object_ is not None:
        row['object_candidate_id'] = object_
    if predicate is not None:
        row['predicate'] = predicate
    if claim is not None:
        q['claim'] = claim
    if quote_text is not None:
        if quote_text not in '\n'.join(SOURCE_LINES[q['source_line_start'] - 1:q['source_line_end']]):
            raise ValueError(f'quote absent from source for {sid}: {quote_text!r}')
        row['original_quote'] = quote_text
    if qualification is not None:
        q['qualification'] = qualification
    if mentioned is not None:
        q['mentioned_candidate_ids'] = list(dict.fromkeys(mentioned))
    if extra:
        q.update(extra)
    if relation is not None:
        classify(row, relation)
    return row


def new_candidate(cid, name, suggested_type, detail, source_line):
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


def add_mention(mention_id, candidate_id, line_number, surface=None,
                start_marker=None, end_marker=None, note=''):
    line_start, line_end, line_text = LINE_OFFSETS[line_number]
    if surface is None:
        if start_marker is None or end_marker is None:
            raise ValueError('mention needs an exact surface or start/end markers')
        local_start = line_text.find(start_marker)
        if local_start < 0:
            raise ValueError(f'mention start absent at L{line_number}: {start_marker!r}')
        local_end = line_text.find(end_marker, local_start + len(start_marker))
        if local_end < 0:
            raise ValueError(f'mention end absent at L{line_number}: {end_marker!r}')
        local_end += len(end_marker)
        surface = line_text[local_start:local_end]
    else:
        positions = []
        cursor = 0
        while True:
            pos = line_text.find(surface, cursor)
            if pos < 0:
                break
            positions.append(pos)
            cursor = pos + max(1, len(surface))
        if len(positions) != 1:
            raise ValueError(f'mention surface not unique at L{line_number}: {surface!r}')
        local_start = positions[0]
        local_end = local_start + len(surface)
    return {
        'mention_id': mention_id,
        'segment_id': SEG,
        'candidate_id': candidate_id,
        'surface_form': surface,
        'start_char': str(line_start + local_start),
        'end_char': str(line_start + local_end),
        'note': note,
    }


def line_page_meta(line_number, target_rows):
    for row in target_rows:
        q = row.get('qualifiers', {})
        if q.get('source_line_start') == line_number:
            return {
                'printed_page': q.get('printed_page', q.get('print_page')),
                'pdf_physical_page': q.get('pdf_physical_page'),
            }
    raise ValueError(f'no existing page metadata for source L{line_number}')


def add_statement(suffix, subject, object_, predicate, line_number, quote_text,
                  claim, is_relation, target_rows, *, qualification=None,
                  mentioned=None, speaker='Haskell', text_layer='authorial footnote',
                  footnote_marker=None, extra=None):
    if quote_text not in SOURCE_LINES[line_number - 1]:
        raise ValueError(f'new statement quote absent at L{line_number}: {quote_text!r}')
    q = {
        'source_line_start': line_number,
        'source_line_end': line_number,
        **line_page_meta(line_number, target_rows),
        'claim': claim,
        'speaker': speaker,
        'text_layer': text_layer,
        'mentioned_candidate_ids': list(dict.fromkeys(mentioned or [])),
    }
    if qualification:
        q['qualification'] = qualification
    if footnote_marker is not None:
        q['footnote_marker'] = footnote_marker
        q['footnote_number'] = footnote_marker
        q['footnote_segment'] = SEG
    if extra:
        q.update(extra)
    row = {
        'statement_id': f'st-chp5-notes-l126-165-{suffix}',
        'segment_id': SEG,
        'subject_candidate_id': subject,
        'object_candidate_id': object_,
        'predicate': predicate,
        'qualifiers': q,
        'original_quote': quote_text,
        'source_file': '02-sources/02-Markdown/05_CHP-5_sec_iii.md',
        'origin': 'book',
    }
    classify(row, is_relation)
    return row


def add_citation(suffix, line_number, quote_text, archive_id, claim,
                 marker, target_rows, *, mentioned=None, qualification=None):
    return add_statement(
        suffix, 'cand-2962', archive_id, 'cites', line_number, quote_text,
        claim, True, target_rows,
        qualification=qualification or 'The cited source/page is identified from Haskell’s note and local bibliography; it was not independently consulted in this S2 pass.',
        mentioned=[archive_id, *(mentioned or [])],
        text_layer='bibliographic citation', footnote_marker=marker,
    )


def set_note_link(row, marker, line_number, statement_ids):
    q = row.setdefault('qualifiers', {})
    q.update({
        'footnote_marker': marker,
        'footnote_link_status': 'linked',
        'footnote_target_line': line_number,
        'citation_segment_id': SEG,
        'citation_source_line_start': line_number,
        'citation_source_line_end': line_number,
        'footnote_refs': [{
            'marker': marker,
            'segment_id': SEG,
            'source_line': line_number,
            'citation_statement_ids': statement_ids,
        }],
    })


def csv_text(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='raise', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after guarded dry-run checks')
    args = parser.parse_args()

    for path, expected in EXPECTED_SHA256.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f'precondition failed: {path.relative_to(ROOT)} sha256={actual}')

    statements = [json.loads(x) for x in STATEMENTS.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
    if len({r['statement_id'] for r in statements}) != len(statements):
        raise SystemExit('duplicate statement IDs in input')
    by_id = {r['statement_id']: r for r in statements}
    target_rows = [r for r in statements if r.get('segment_id') == SEG]
    unset_rows = [r for r in target_rows if r.get('qualifiers', {}).get('relation_candidate') is None]
    if len(target_rows) != 66 or len(unset_rows) != 52:
        raise SystemExit(f'unexpected note segment state: {len(target_rows)} statements, {len(unset_rows)} unset')
    if any(r.get('origin') != 'book' for r in target_rows):
        raise SystemExit('unexpected non-book row in target segment')

    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        cr = csv.DictReader(f)
        candidate_fields = cr.fieldnames
        candidates = list(cr)
    candidate_by_id = {r['candidate_id']: r for r in candidates}
    numeric_ids = [int(r['candidate_id'].split('-')[1]) for r in candidates]
    if len(candidates) != 11916 or max(numeric_ids) != 11938:
        raise SystemExit(f'unexpected candidate count/ceiling: {len(candidates)}/{max(numeric_ids)}')

    with MENTIONS.open(encoding='utf-8-sig', newline='') as f:
        mr = csv.DictReader(f)
        mention_fields = mr.fieldnames
        mentions = list(mr)
    mention_by_id = {r['mention_id']: r for r in mentions}

    with COVERAGE.open(encoding='utf-8-sig', newline='') as f:
        cov_reader = csv.DictReader(f)
        coverage_fields = cov_reader.fieldnames
        coverage_rows = list(cov_reader)
    coverage = next((r for r in coverage_rows if r.get('segment_id') == SEG), None)
    if not coverage or coverage.get('disposition') != 'reviewed' or coverage.get('migration_status') != 'complete':
        raise SystemExit('target coverage precondition failed')

    new_candidates = [
        new_candidate('cand-11939', 'Bamboots (artist name form in the 1943 catalogue; identity unresolved)', 'person',
                      'The 1943 Burlington Magazine sale-catalogue is reported to attribute genre scenes to “Bamboots”. Keep this source form separate from Bamboccianti (cand-0173); identity and whether it denotes an individual remain unresolved.', 135),
        new_candidate('cand-11940', 'Will of Michelangelo Cerquozzi (published 1886)', 'archive',
                      'Cerquozzi’s will, which Haskell says Bertolotti published in Arte e Storia, volume V (1886), p. 22. The will and publication were not independently consulted.', 139),
        new_candidate('cand-11941', 'Five unidentified Cerquozzi paintings lent by Raggi in 1701', 'work',
                      'A group of five oblong paintings by Cerquozzi, all of one size, lent by Marchese Raggi to an exhibition at S. Salvatore in Lauro in 1701. Titles and individual identities are not given.', 143),
        new_candidate('cand-11942', '1701 exhibition at S. Salvatore in Lauro', 'event',
                      'The exhibition to which Marchese Raggi lent five Cerquozzi paintings in 1701. The source does not identify the event title or establish that it was a particular edition of the recurring December series.', 143),
        new_candidate('cand-11943', 'Unidentified Jan Miel painting owned by Filippo Corsini', 'work',
                      'A painting described in Baldinucci as depicting a barone seated and wiping a child. The title, date, medium, and present location are not supplied.', 144),
        new_candidate('cand-11944', 'Unidentified paintings by Micco Spadaro at Museo di San Martino', 'work',
                      'Plural pictures by Micco Spadaro reported by Haskell to be at Museo di San Martino, Naples. Keep this source-bounded group distinct from the single double-scene Masaniello picture cand-6162.', 152),
        new_candidate('cand-11945', 'Unidentified 1651 letter first mentioning Rosa’s Satire on Painting', 'archive',
                      'A letter dated only to 1651 which Haskell says first mentions Salvator Rosa’s Satire on Painting. Sender, recipient, and manuscript or edition are not identified.', 162),
        new_candidate('cand-11946', 'Saxl, cited publication (title, date, and page unspecified)', 'archive',
                      'Haskell gives only “Saxl” as a citation. The source work and bibliographic identity remain unresolved; no specific publication is inferred.', 149),
        new_candidate('cand-11947', 'Ruffo, cited source, p. 189 (title unspecified)', 'archive',
                      'A source cited as “Ruffo, p. 189” for the 1671 valuation of a four-palmi Van Laer picture. The title, edition, and relation to other Ruffo publications remain unresolved.', 159),
    ]
    if {r['candidate_id'] for r in new_candidates} & set(candidate_by_id):
        raise SystemExit('new candidate ID collision')
    candidate_ids = set(candidate_by_id) | {r['candidate_id'] for r in new_candidates}

    added_statements = []
    def add(*args, **kwargs):
        row = add_statement(*args, target_rows=target_rows, **kwargs)
        if row['statement_id'] in by_id or any(r['statement_id'] == row['statement_id'] for r in added_statements):
            raise SystemExit(f'statement ID collision: {row["statement_id"]}')
        added_statements.append(row)
        return row

    def cite(*args, **kwargs):
        return add_citation(*args, target_rows=target_rows, **kwargs)

    # Classify and normalize all 52 previously unset note statements.
    classify(by_id['st-chp5-notes-l134-vanlaer-valuation'], False)
    revise(by_id, 'st-chp5-notes-l135-baldinucci-reactions', subject='cand-2962', object_='cand-4846',
           predicate='cites', claim='Haskell cites Baldinucci, volume VI (1728), pages 602–604, for painters’ reactions to the Bamboccianti.',
           mentioned=['cand-2962', 'cand-4846'], relation=True)
    revise(by_id, 'st-chp5-notes-l135-bamboots-catalogue', object_='cand-11939',
           predicate='reported_catalogue_attribution',
           claim='The 1943 Burlington Magazine sale catalogue is reported to attribute various genre scenes to the name-form Bamboots.',
           quote_text=quote_between(135, 'various genre scenes', 'Bamboots'),
           mentioned=['cand-6215', 'cand-11939'],
           qualification='Keep “Bamboots” distinct from the collective Bamboccianti; the catalogue attribution is reported by Haskell and the artist identity is unresolved.',
           relation=True)
    classify(by_id['st-chp5-notes-l135-lely-admiration'], True)
    revise(by_id, 'st-chp5-notes-l135-passeri-p74', subject='cand-2962', object_='cand-4376', predicate='cites',
           claim='Haskell cites Passeri, page 74, in this note.', mentioned=['cand-2962', 'cand-4376'], relation=True)
    classify(by_id['st-chp5-notes-l136-swanevelt-catalano-case'], True)
    revise(by_id, 'st-chp5-notes-l136-swanevelt-catalano-case',
           qualification='This is an accusation reported in a legal case, not an adjudicated finding that Catalano stole the paintings.',
           mentioned=['cand-2535', 'cand-0608', 'cand-1351', 'cand-6182'])
    classify(by_id['st-chp5-notes-l136-testimony-value'], False)
    revise(by_id, 'st-chp5-notes-l137-ibid-page134', subject='cand-2962', object_='cand-6182', predicate='cites',
           claim='Haskell’s “ibid.” continues the Bertolotti citation at page 134.', mentioned=['cand-2962', 'cand-6182'], relation=True)
    revise(by_id, 'st-chp5-notes-l138-ibid-page133', subject='cand-2962', object_='cand-6182', predicate='cites',
           claim='Haskell’s “ibid.” continues the Bertolotti citation at page 133.', mentioned=['cand-2962', 'cand-6182'], relation=True)
    classify(by_id['st-chp5-notes-l138-lorca-friend'], True)
    revise(by_id, 'st-chp5-notes-l139-biographies', subject='cand-2962', object_='cand-4376', predicate='cites',
           claim='Haskell points readers to Passeri’s life of Cerquozzi.', mentioned=['cand-2962', 'cand-0625', 'cand-1856', 'cand-4376'], relation=True)
    revise(by_id, 'st-chp5-notes-l139-cerquozzi-will', subject='cand-11940', object_='cand-6183', predicate='published_in',
           claim='Haskell says Bertolotti published Cerquozzi’s will in Arte e Storia, volume V (1886), page 22.',
           mentioned=['cand-11940', 'cand-0625', 'cand-6183'],
           qualification='The will and cited publication are known here through Haskell’s note; neither was independently consulted.', relation=True)
    revise(by_id, 'st-chp5-notes-l139-ibid', subject='cand-2962', object_='cand-6183', predicate='cites',
           claim='Haskell’s second note says “ibid.”, referring to the preceding Bertolotti citation in Arte e Storia, volume V.',
           mentioned=['cand-2962', 'cand-6183'], relation=True)
    classify(by_id['st-chp5-notes-l140-1615-age-doubt'], False)
    revise(by_id, 'st-chp5-notes-l140-baldinucci-p190', subject='cand-2962', object_='cand-4846', predicate='cites',
           claim='Haskell cites Baldinucci, volume VI (1728), page 190.', mentioned=['cand-2962', 'cand-4846'], relation=True)
    classify(by_id['st-chp5-notes-l140-embassy-meeting'], True)
    revise(by_id, 'st-chp5-notes-l140-longhi-significance', relation=False,
           qualification='This is Haskell’s historiographical assessment of Longhi’s observation, not a biographical or artistic relation between Cerquozzi and Velasquez.')
    classify(by_id['st-chp5-notes-l140-vanlaer-rome-arrival'], True)
    revise(by_id, 'st-chp5-notes-l140-velasquez-attribution', subject='cand-5505', object_='cand-6209',
           predicate='reported_attribution',
           claim='Haskell reports that Longhi attributed Rissa all’ambasciata di Spagna to Velasquez, but says the attribution is not altogether convincing.',
           mentioned=['cand-5505', 'cand-2709', 'cand-6209'],
           qualification='The attributed maker is Velasquez; Haskell explicitly questions Longhi’s attribution. Longhi is the claimant, not the artist endpoint.', relation=True)
    classify(by_id['st-chp5-notes-l141-cerquozzi-colonna-work'], True)
    classify(by_id['st-chp5-notes-l141-ghezzi-velasco-pictures'], True)
    revise(by_id, 'st-chp5-notes-l142-rapaccioli-report', object_='cand-4404',
           predicate='reported_alignment_with',
           claim='A French ambassador reported in 1654–1655 that Rapaccioli was “as Spanish as Cardinal”, an attributed alignment with the Spanish cause in Rome.',
           mentioned=['cand-2097', 'cand-4404', 'cand-6214'],
           qualification='This is a report by the French ambassador as relayed by Haskell; it does not identify a formal political membership.', relation=True)
    classify(by_id['st-chp5-notes-l143-carandini-reference'], False)
    revise(by_id, 'st-chp5-notes-l143-raggi-patronage-loan', object_='cand-0625',
           predicate='patron_of',
           claim='Haskell says Baldinucci mentions Ferdinando Raggi’s patronage of Cerquozzi.',
           quote_text=quote_between(143, 'Raggi', 'by Baldinucci'),
           mentioned=['cand-2090', 'cand-0625', 'cand-0166', 'cand-4846'],
           qualification='The patronage is reported through Baldinucci; the note separately documents a five-picture loan in 1701.', relation=True)
    revise(by_id, 'st-chp5-notes-l144-corsini-miel', subject='cand-11943', object_='cand-0861', predicate='owned_by',
           claim='Haskell reports that Marchese Filippo Corsini in Florence owned a painting by Jan Miel depicting a seated barone wiping a child.',
           quote_text=quote_between(144, 'Even in Florence', 'Baldinucci, VI'),
           mentioned=['cand-0861', 'cand-3397', 'cand-1662', 'cand-11943', 'cand-4846'],
           qualification='The report is attributed to Haskell, who cites Baldinucci, volume VI (1728), page 368; the cited page was not independently consulted.', relation=True)
    classify(by_id['st-chp5-notes-l145-amayden-report'], False)
    revise(by_id, 'st-chp5-notes-l145-amayden-report',
           qualification='This preserves Amayden’s source-attributed description of social groups on the two sides; it does not assert that the named social categories formed formal political organizations.',
           mentioned=['cand-0093', 'cand-3408', 'cand-3409', 'cand-4490'])
    classify(by_id['st-chp5-notes-l145-amayden-source-caveat'], False)
    for sid in ('st-chp5-notes-l146-passeri-p289', 'st-chp5-notes-l147-briganti-1954', 'st-chp5-notes-l148-passeri-p288'):
        row = by_id[sid]
        q = row['qualifiers']
        target = {'st-chp5-notes-l146-passeri-p289': 'cand-4376',
                  'st-chp5-notes-l147-briganti-1954': 'cand-6187',
                  'st-chp5-notes-l148-passeri-p288': 'cand-4376'}[sid]
        revise(by_id, sid, subject='cand-2962', object_=target, predicate='cites',
               mentioned=['cand-2962', target], relation=True)
    revise(by_id, 'st-chp5-notes-l149-saxl', subject='cand-2962', object_='cand-11946', predicate='cites',
           claim='Haskell cites a work by Saxl without giving its title, date, or page.',
           mentioned=['cand-2962', 'cand-11946', 'cand-6153'], relation=True)
    revise(by_id, 'st-chp5-notes-l150-wallenstein-painting', relation=False,
           claim='Haskell characterizes The Death of Wallenstein as the most extraordinary example of such a painting.',
           quote_text=quote_between(150, 'The most extraordinary case', 'Pietro Paolini'),
           qualification='“Most extraordinary” is Haskell’s evaluative description; the note also identifies Paolini as the painter and cites Marabottini separately.')
    revise(by_id, 'st-chp5-notes-l151-spada-location', subject='cand-4060', object_='cand-3953', predicate='reported_location',
           claim='Haskell says Baldinucci’s account reports that the work was seen in Palazzo del Bali Spada.',
           quote_text=exact_quote(151, 'si vede nel Palazzo del Bali Spada'),
           mentioned=['cand-4060', 'cand-3953', 'cand-4846'],
           qualification='This is Baldinucci’s reported location in the cited account, not a claim of the work’s present location.', relation=True)
    revise(by_id, 'st-chp5-notes-l152-filomarino-dispatches', subject='cand-2962', object_='cand-6192', predicate='cites',
           claim='Haskell directs readers to Cardinal Filomarino’s dispatches published in Archivio Storico Italiano, volume IX (1846), pages 379–393, for the immediate impact of Masaniello’s revolt in Rome.',
           quote_text=quote_between(152, 'for the immediate impact', '393'),
           mentioned=['cand-2962', 'cand-1036', 'cand-6192', 'cand-1559', 'cand-4490'],
           qualification='This is a bibliographic pointer, not independent verification of the dispatches or their contents.', relation=True)
    revise(by_id, 'st-chp5-notes-l152-spadaro-pictures', subject='cand-11944', object_='cand-6201', predicate='reported_location',
           claim='Haskell reports that a group of Micco Spadaro’s pictures is at Museo di San Martino, Naples.',
           quote_text=quote_between(152, 'Micco Spadaro', 'Naples'),
           mentioned=['cand-11944', 'cand-2495', 'cand-6201', 'cand-1722'], relation=True)
    classify(by_id['st-chp5-notes-l153-brunetti-evidence-assessment'], False)
    revise(by_id, 'st-chp5-notes-l153-codazzi-testimony', object_='cand-1722', predicate='reported_arrival_in',
           claim='In words quoted by Haskell from 1636, Codazzi says he came to Naples from Bergamo about fifteen years earlier.',
           quote_text=quote_between(153, 'Io venni dalla predetta', 'venni in Napoli'),
           mentioned=['cand-0794', 'cand-6208', 'cand-1722', 'cand-6202', 'cand-6195'],
           qualification='Codazzi’s first-person statement is reproduced through Prota-Giurleo and Haskell; “about fifteen years” is not converted to an exact arrival date.', relation=True)
    revise(by_id, 'st-chp5-notes-l153-collaboration-after1647', relation=True,
           qualification='Haskell presents this as a reasonable assumption, not as a dated documentary record; retain the after-1647 limit and the Rome context.')
    revise(by_id, 'st-chp5-notes-l153-longhi-brunetti-claim', subject='cand-0794', object_='cand-0625',
           predicate='reported_collaboration_claim_for_1625_1635',
           claim='Haskell reports that Longhi and Estella Brunetti claimed Codazzi painted with Cerquozzi and others in Rome between 1625 and 1635, then rejects that chronology against Codazzi’s 1636 words.',
           mentioned=['cand-5505', 'cand-6193', 'cand-0794', 'cand-0625', 'cand-4490', 'cand-6194'],
           qualification='This is a contested historiographical claim attributed to Longhi and Brunetti; Haskell explicitly rejects its 1625–1635 chronology.', relation=True)
    revise(by_id, 'st-chp5-notes-l154-chigi-commission-unproven', subject='cand-6164', object_='cand-0671',
           quote_text=quote_between(154, 'cannot be conclusively proved', 'Cardinal Chigi'),
           mentioned=['cand-6164', 'cand-0671', 'cand-0625'], relation=False)
    revise(by_id, 'st-chp5-notes-l154-colonna-acquisition-alternative', subject='cand-6164', object_='cand-4638',
           predicate='qualified_possible_commission_by',
           claim='Haskell says it is just conceivable, though most unlikely, that the pictures were painted for the Colonna.',
           quote_text=quote_between(154, 'just conceivable', 'for the Colonna'),
           mentioned=['cand-6164', 'cand-4638', 'cand-0671', 'cand-6211', 'cand-6212'],
           qualification='This is explicitly a low-confidence alternative offered by Haskell, not an established commission.', relation=True)
    revise(by_id, 'st-chp5-notes-l154-no-payment-document', subject='cand-6164', object_='cand-0625',
           quote_text=quote_between(154, 'There is, however, no document', 'to Cerquozzi'),
           mentioned=['cand-6164', 'cand-0625'], relation=False)
    revise(by_id, 'st-chp5-notes-l156-hoogewerff-1913', subject='cand-2962', object_='cand-6199', predicate='cites',
           mentioned=['cand-2962', 'cand-6199'], relation=True)
    revise(by_id, 'st-chp5-notes-l157-passeri-p96', subject='cand-2962', object_='cand-4376', predicate='cites',
           mentioned=['cand-2962', 'cand-4376'], relation=True)
    revise(by_id, 'st-chp5-notes-l158-malvasia-volume2', subject='cand-2962', object_='cand-4578', predicate='cites',
           mentioned=['cand-2962', 'cand-4578'], relation=True)
    classify(by_id['st-chp5-notes-l159-vanlaer-valuation'], False)
    classify(by_id['st-chp5-notes-l159-ruffo-cerquozzi-purchase'], True)
    revise(by_id, 'st-chp5-notes-l160-simonelli-tityus-exhibition', relation=True,
           claim='Haskell says Simonelli arranged for Rosa’s Tityus to be exhibited at the Pantheon in 1638.',
           qualification='The arrangement is attributed to Haskell, who cites Passeri, page 388; the cited page was not independently consulted.')
    revise(by_id, 'st-chp5-notes-l161-baldinucci-p191', subject='cand-2962', object_='cand-4846', predicate='cites',
           mentioned=['cand-2962', 'cand-4846'], relation=True)
    revise(by_id, 'st-chp5-notes-l162-rosa-satire-date', relation=False,
           claim='Haskell says the date of Rosa’s Satire on Painting is uncertain.',
           qualification='The uncertainty about the work’s date is a source-critical claim. Its first mention in a 1651 letter, possible Florentine composition, and Limentani citation are recorded separately.')
    revise(by_id, 'st-chp5-notes-l164-rosa-biographies', subject='cand-2962', object_='cand-4376', predicate='cites',
           claim='Haskell directs readers to Passeri’s life of Salvator Rosa.', mentioned=['cand-2962', 'cand-2236', 'cand-1856', 'cand-4376'], relation=True)
    revise(by_id, 'st-chp5-notes-l165-shaftesbury-second-characters', subject='cand-2426', object_='cand-6220',
           predicate='reported_literature_gap',
           claim='Haskell says that, to his knowledge, art historians had not noticed the cited passage.',
           mentioned=['cand-2426', 'cand-6220'], relation=False)

    # Bibliographic links that were missing from the note statements.
    cite('l127-passeri-citation', 127, exact_quote(127, 'Passeri, p. 72'), 'cand-4376',
         'Haskell cites Passeri, page 72, for the quotation about Van Laer.', 1, mentioned=['cand-1856'])
    cite('l136-bertolotti-citation', 136, exact_quote(136, 'Bertolotti: Artisti belgi c olandesi, pp. 127 If.'), 'cand-6182',
         'Haskell cites Bertolotti’s Artisti belgi e olandesi for the reported legal case.', 3, mentioned=['cand-3504'])
    cite('l139-baldinucci-biography-citation', 139, exact_quote(139, 'Baldinucci'), 'cand-4846',
         'Haskell points readers to Baldinucci’s life of Cerquozzi.', 1, mentioned=['cand-0625', 'cand-0166'])
    add('l139-will-of-cerquozzi', 'cand-11940', 'cand-0625', 'will_of', 139,
        exact_quote(139, 'his will'), 'The will published in the cited note is Cerquozzi’s will.', True,
        qualification='The possessive is resolved to Cerquozzi from the immediately preceding phrase “lives of Cerquozzi”; the will itself is not independently consulted.',
        mentioned=['cand-11940', 'cand-0625'], text_layer='document identity')
    add('l141-velasco-work-attribution', 'cand-6189', 'cand-6190', 'attributed_to', 141,
        exact_quote(141, 'Due bambocciate di Velasco'),
        'Ghezzi’s note records a pair of bambocciate under the source name Velasco.', True,
        qualification='Keep Velasco distinct from Velasquez; the identity of this named maker remains unresolved.',
        mentioned=['cand-1157', 'cand-6189', 'cand-6190'], text_layer='attributed title')
    cite('l142-valfrey-citation', 142, exact_quote(142, 'Valsrey, p. 220'), 'cand-6214',
         'Haskell cites Valfrey, page 220, for the French ambassador’s report about Rapaccioli.', 1,
         mentioned=['cand-2097', 'cand-6214'], qualification='The print reads Valfrey; S0 OCR reads Valsrey. The cited page was not independently consulted.')
    cite('l143-baldinucci-citation', 143, exact_quote(143, 'Baldinucci'), 'cand-4846',
         'Haskell cites Baldinucci as a source mentioning Raggi’s patronage of Cerquozzi.', 2,
         mentioned=['cand-2090', 'cand-0625', 'cand-0166'])
    cite('l143-ghezzi-papers-citation', 143, exact_quote(143, 'Ghezzi papers in the Museo di Roma'), 'cand-6029',
         'Haskell identifies Giuseppe Ghezzi’s papers as the source documenting Raggi’s 1701 loan.', 2,
         mentioned=['cand-2090', 'cand-0625', 'cand-6030'])
    add('l143-raggi-loaned-five-pictures', 'cand-11941', 'cand-2090', 'lent_by', 143,
        quote_between(143, 'cinque quadri bellissimi bislunghi', 'misura'),
        'Five unidentified Cerquozzi paintings were lent by Marchese Ferdinando Raggi in 1701.', True,
        qualification='The source supplies the number, artist, lender, year, and shape/size sameness but no individual titles or current locations.',
        mentioned=['cand-11941', 'cand-2090', 'cand-0625'], footnote_marker=2)
    add('l143-five-pictures-exhibited', 'cand-11941', 'cand-11942', 'shown_at_exhibition', 143,
        exact_quote(143, 'to the exhibition'),
        'The five paintings lent by Raggi were sent to the 1701 exhibition at S. Salvatore in Lauro.', True,
        qualification='The event is kept distinct from the recurring exhibition series cand-6051; the note does not explicitly identify the series.',
        mentioned=['cand-11941', 'cand-11942', 'cand-6052'], footnote_marker=2)
    add('l143-exhibition-at-san-salvatore', 'cand-11942', 'cand-6052', 'occurred_at', 143,
        exact_quote(143, 'S. Salvatore in Lauro'),
        'The 1701 exhibition took place at the Church of S. Salvatore in Lauro.', True,
        qualification='The event and venue are distinct; venue identity is taken from the source wording.',
        mentioned=['cand-11942', 'cand-6052'], footnote_marker=2)
    add('l143-five-pictures-by-cerquozzi', 'cand-11941', 'cand-0625', 'created_by', 143,
        exact_quote(143, 'by the artist'),
        'The five paintings lent by Raggi are identified as paintings by Cerquozzi.', True,
        qualification='This is the artist attribution stated in Haskell’s footnote.', mentioned=['cand-11941', 'cand-0625'], footnote_marker=2)
    cite('l144-baldinucci-citation', 144, exact_quote(144, 'Baldinucci, VI, 1728, p. 368'), 'cand-4846',
         'Haskell cites Baldinucci, volume VI (1728), page 368, for the Miel painting owned by Filippo Corsini.', 3,
         mentioned=['cand-0861', 'cand-1662', 'cand-11943'])
    add('l144-miel-painting-by-miel', 'cand-11943', 'cand-1662', 'created_by', 144,
        exact_quote(144, 'a painting by Jan Miel'),
        'The painting owned by Filippo Corsini is identified as a work by Jan Miel.', True,
        qualification='This is the work attribution in Haskell’s report, which cites Baldinucci.',
        mentioned=['cand-11943', 'cand-0861', 'cand-1662'], footnote_marker=3)
    cite('l145-relazione-casanatense-citation', 145, exact_quote(145, 'Relazione della Citti di Roma'), 'cand-3408',
         'Haskell cites the 1642 Relatione della città di Roma, manuscript 5001 at Biblioteca Casanatense, for Amayden’s account.', 4,
         mentioned=['cand-0093', 'cand-3408', 'cand-3409'],
         qualification='The manuscript is identified as cited in Haskell’s note; it was not independently consulted.')
    cite('l150-marabottini-citation', 150, exact_quote(150, 'Marabottini, 1963'), 'cand-6191',
         'Haskell cites Marabottini (1963) for The Death of Wallenstein.', 1,
         mentioned=['cand-1830', 'cand-1829', 'cand-5897'])
    add('l150-wallenstein-authorship', 'cand-1830', 'cand-1829', 'created_by', 150,
        exact_quote(150, 'The Death of Wallenstein by Pietro Paolini'),
        'The Death of Wallenstein is identified as a work by Pietro Paolini.', True,
        qualification='The note’s named artist candidate cand-1829 is kept distinct from the indexed work entry cand-1830.',
        mentioned=['cand-1830', 'cand-1829'], footnote_marker=1)
    cite('l151-baldinucci-citation', 151, exact_quote(151, 'Baldinucci, VI, 1728, p. 192'), 'cand-4846',
         'Haskell cites Baldinucci, volume VI (1728), page 192, for the reported location of the work.', 2,
         mentioned=['cand-4060', 'cand-3953'])
    add('l152-spadaro-workgroup-authorship', 'cand-11944', 'cand-2495', 'created_by', 152,
        exact_quote(152, 'Micco Spadaro’s pictures'),
        'The reported group of pictures at Museo di San Martino is attributed to Micco Spadaro.', True,
        qualification='This group remains distinct from the single double-scene Masaniello picture cand-6162.',
        mentioned=['cand-11944', 'cand-2495', 'cand-6201'], footnote_marker=5)
    cite('l153-brunetti-1958-citation', 153, exact_quote(153, 'Estella Brunetti (1958, p. 311)'), 'cand-6194',
         'Haskell cites Estella Brunetti (1958), page 311, for the disputed early collaboration chronology.', 6,
         mentioned=['cand-6193', 'cand-5505', 'cand-0794', 'cand-0625'])
    add('l153-codazzi-left-bergamo', 'cand-0794', 'cand-6208', 'reported_departure_from', 153,
        exact_quote(153, 'dalla predetta mia patria [Bergamo] da quindici anni'),
        'Codazzi’s quoted 1636 words place his departure from his homeland Bergamo about fifteen years earlier.', True,
        qualification='This is a first-person statement quoted by Haskell through Prota-Giurleo; no exact departure date is inferred.',
        mentioned=['cand-0794', 'cand-6208', 'cand-6195'], footnote_marker=6, speaker='Viviano Codazzi, quoted by Haskell', text_layer='quoted testimony')
    add('l153-codazzi-resided-at-baglivo', 'cand-0794', 'cand-6202', 'reported_residence_at', 153,
        exact_quote(153, 'sempre ho abitato in Napoli al Baglivo'),
        'Codazzi’s quoted 1636 words say that he had always lived at Baglivo in Naples.', True,
        qualification='This is Codazzi’s first-person statement reproduced by Haskell; the exact identity of Baglivo remains unresolved.',
        mentioned=['cand-0794', 'cand-1722', 'cand-6202', 'cand-6195'], footnote_marker=6, speaker='Viviano Codazzi, quoted by Haskell', text_layer='quoted testimony')
    cite('l153-prota-giurleo-citation', 153, exact_quote(153, 'Prota-Giurleo, p. 77'), 'cand-6195',
         'Haskell cites Prota-Giurleo, page 77, as the source of Codazzi’s 1636 words.', 6,
         mentioned=['cand-0794', 'cand-6208', 'cand-1722', 'cand-6202'],
         qualification='The cited page and publication were not independently consulted.')
    add('l154-contemporary-ownership-reports', 'cand-6164', 'cand-0671', 'reported_owned_by', 154,
        exact_quote(154, 'all writers of the time refer to his owning them'),
        'Haskell reports that contemporary writers refer to Cardinal Flavio Chigi owning the two pictures.', True,
        qualification='Reported ownership is evidence distinct from an original commission; the “them” refers to the two works discussed on p. 140.',
        mentioned=['cand-6164', 'cand-0671', 'cand-0625'], footnote_marker=1)
    add('l154-pictures-listed-in-chigi-inventories', 'cand-6164', 'cand-0671', 'listed_in_inventories_of', 154,
        exact_quote(154, 'they are listed in his inventories'),
        'Haskell says the two pictures are listed in Cardinal Flavio Chigi’s inventories.', True,
        qualification='The inventory entries are reported by Haskell; the underlying inventories were not independently consulted.',
        mentioned=['cand-6164', 'cand-0671'], footnote_marker=1)
    add('l154-acquisition-by-chigi-1661', 'cand-6164', 'cand-0671', 'qualified_possible_acquisition_by', 154,
        exact_quote(154, 'acquired with many others by the Chigi in 1661'),
        'Haskell says the pictures may have been acquired by the Chigi with other contents in 1661.', True,
        qualification='This belongs to Haskell’s explicitly unlikely Colonna-origin alternative; it is not asserted as established provenance.',
        mentioned=['cand-6164', 'cand-0671', 'cand-4638', 'cand-6211', 'cand-6212'], footnote_marker=1)
    add('l154-chigi-bought-palazzo-odescalchi', 'cand-0671', 'cand-6211', 'reported_purchase_of', 154,
        exact_quote(154, 'when they bought the palace'),
        'Haskell reports that Chigi bought the palace later called Palazzo Odescalchi at SS. Apostoli from the Colonna in 1661.', True,
        qualification='The palace’s later name and location are preserved as phrased; this purchase is stated within Haskell’s qualified alternative-provenance explanation.',
        mentioned=['cand-0671', 'cand-6211', 'cand-6212', 'cand-4638'], footnote_marker=1)
    cite('l154-golzio-citation', 154, exact_quote(154, 'Golzio, 1939, p. 3'), 'cand-6196',
         'Haskell cites V. Golzio, Documenti artistici sul Seicento nell’Archivio Chigi (Rome, 1939), page 3, for the alternative provenance.', 1,
         mentioned=['cand-6164', 'cand-4638', 'cand-0671'])
    add('l155-raggi-report-quoted-in-neri', 'cand-6210', 'cand-6198', 'quoted_in', 155,
        exact_quote(155, 'quoted by Achille Neri, 1883'),
        'Ferdinando Raggi’s report is identified as quoted by Achille Neri in 1883.', True,
        qualification='The report and Neri publication are known here through Haskell’s citation; neither was independently consulted.',
        mentioned=['cand-6210', 'cand-2090', 'cand-6197', 'cand-6198'], footnote_marker=2)
    add('l155-neri-citation', 'cand-2962', 'cand-6198', 'cites', 155,
        exact_quote(155, 'Achille Neri, 1883'),
        'Haskell cites Achille Neri’s 1883 publication as the intermediary for Raggi’s report.', True,
        qualification='Bibliographic pointer only; the cited publication was not independently consulted.',
        mentioned=['cand-2962', 'cand-6197', 'cand-6198'], footnote_marker=2, text_layer='bibliographic citation')
    add('l159-vanlaer-picture-authorship', 'cand-6204', 'cand-1351', 'created_by', 159,
        exact_quote(159, 'a Van Laer, size 4 palmi'),
        'The four-palmi picture valued in 1671 is identified as a work by Pieter van Laer.', True,
        qualification='This is the artist attribution in Haskell’s note; the work remains unidentified by title or location.',
        mentioned=['cand-6204', 'cand-1351'], footnote_marker=4)
    cite('l159-ruffo-source-citation', 159, exact_quote(159, 'Ruffo, p. 189'), 'cand-11947',
         'Haskell cites Ruffo, page 189, for the 1671 valuation of Van Laer’s picture.', 4,
         mentioned=['cand-2297', 'cand-6204'])
    cite('l160-passeri-p388-citation', 160, exact_quote(160, 'Passeri, p. 388'), 'cand-4376',
         'Haskell cites Passeri, page 388, for Simonelli’s arrangement of Rosa’s Tityus exhibition.', 1,
         mentioned=['cand-2434', 'cand-2236', 'cand-2257'])
    add('l162-satire-first-mentioned-in-letter', 'cand-2255', 'cand-11945', 'first_mentioned_in', 162,
        exact_quote(162, 'mentioned for the first time in a letter of 1651'),
        'Haskell says Rosa’s Satire on Painting was first mentioned in a letter of 1651.', True,
        qualification='This dates the first mention reported by Haskell, not the composition of the work.',
        mentioned=['cand-2255', 'cand-11945', 'cand-2236'], footnote_marker=3)
    add('l162-satire-possibly-written-in-florence', 'cand-2255', 'cand-3397', 'qualified_possible_composition_place', 162,
        exact_quote(162, 'may have been written in Florence'),
        'Haskell says Rosa’s Satire on Painting may have been written in Florence.', True,
        qualification='This is explicitly a possibility, not an established composition location.',
        mentioned=['cand-2255', 'cand-3397', 'cand-2236'], footnote_marker=3)
    cite('l162-limentani-citation', 162, exact_quote(162, 'Limentani, 1961, pp. 163-79'), 'cand-6206',
         'Haskell cites Limentani’s 1961 study, pages 163–179, for an analysis of Rosa’s satire.', 3,
         mentioned=['cand-2236', 'cand-2255', 'cand-6376'])
    cite('l163-de-rinaldis-citation', 163, exact_quote(163, 'de R...Jdis, 1939, p. 109'), 'cand-6205',
         'Haskell cites the 1939 de Rinaldis publication, page 109, for the Rosa–Ricciardi letter.', 4,
         mentioned=['cand-11571', 'cand-2236', 'cand-2187'],
         qualification='The print scan reads “de R...ndis”; retain the unresolved form in S0 and do not expand the surname beyond the existing candidate.')
    add('l163-letter-published-in-de-rinaldis', 'cand-11571', 'cand-6205', 'published_in', 163,
        exact_quote(163, 'Letter from Salvator Rosa to G. B. Ricciardi dated 2 April 1660'),
        'The Rosa–Ricciardi letter dated 2 April 1660 is cited through the 1939 de Rinaldis publication.', True,
        qualification='The letter and cited publication are referenced through Haskell; the original letter and publication were not independently consulted.',
        mentioned=['cand-11571', 'cand-2236', 'cand-2187', 'cand-6205'], footnote_marker=4)
    cite('l164-baldinucci-biography-citation', 164, exact_quote(164, 'Baldinucci'), 'cand-4846',
         'Haskell also directs readers to Baldinucci’s life of Salvator Rosa.', 5,
         mentioned=['cand-2236', 'cand-0166'])
    cite('l165-shaftesbury-citation', 165, exact_quote(165, 'Shaftesbury, Second Characters, p. 15'), 'cand-6220',
         'Haskell cites Shaftesbury’s Second Characters, page 15.', 6,
         mentioned=['cand-2426', 'cand-6220'])

    # Add row-level references that preserve the distinction between cited author and cited work.
    add('l139-bibliography-cited-source', 'cand-2962', 'cand-6183', 'cites', 139,
        exact_quote(139, 'Bertolotti in Arte e Storia, V, 1886, p. 22'),
        'Haskell cites the publication of Cerquozzi’s will in Arte e Storia, volume V (1886), page 22.', True,
        qualification='The volume is represented by the existing archive candidate; the cited page was not independently consulted.',
        mentioned=['cand-2962', 'cand-11940', 'cand-6183'], footnote_marker=1, text_layer='bibliographic citation')

    # Correct the two earlier source-layer citation classifications in this note segment.
    revise(by_id, 'st-chp5-notes-l128-briganti-survey', subject='cand-2962', object_='cand-6181', predicate='cites',
           claim='Haskell directs readers to the introduction by Giulio Briganti to the 1950 I Bamboccianti exhibition as a general survey.',
           mentioned=['cand-2962', 'cand-6180', 'cand-6181'],
           qualification='This is a bibliographic recommendation to the exhibition-catalogue introduction; it is separate from Briganti’s authorship relation.',
           relation=True)

    # Atomic statements for the remaining parts of already-classified composite notes.

    # Exact source mentions newly represented by the added candidates.
    new_mentions = [
        add_mention('m-chp5-note-139-will-11940', 'cand-11940', 139, surface='his will',
                    note='Coreference to Cerquozzi’s will, published in the cited source.'),
        add_mention('m-chp5-note-143-five-pictures-11941', 'cand-11941', 143,
                    start_marker='cinque quadri bellissimi bislunghi', end_marker='misura',
                    note='The five unidentified Cerquozzi paintings lent by Raggi in 1701.'),
        add_mention('m-chp5-note-143-exhibition-11942', 'cand-11942', 143, surface='the exhibition',
                    note='The specific 1701 exhibition at S. Salvatore in Lauro.'),
        add_mention('m-chp5-note-144-painting-11943', 'cand-11943', 144, surface='a painting',
                    note='The unidentified painting by Jan Miel owned by Filippo Corsini.'),
        add_mention('m-chp5-note-152-pictures-11944', 'cand-11944', 152, surface='pictures',
                    note='Plural Spadaro paintings reported at Museo di San Martino, separate from the single p.139 work.'),
        add_mention('m-chp5-note-154-two-pictures-6164', 'cand-6164', 154, surface='the two pictures',
                    note='The two works identified on p.140; commission and provenance remain qualified.'),
        add_mention('m-chp5-note-154-these-pictures-6164', 'cand-6164', 154, surface='these pictures',
                    note='Coreference to the two pictures in Haskell’s alternative provenance sentence.'),
        add_mention('m-chp5-note-162-letter-11945', 'cand-11945', 162, surface='a letter of 1651',
                    note='Unidentified letter said to contain the first mention of Rosa’s Satire on Painting.'),
        add_mention('m-chp5-note-159-ruffo-source-11947', 'cand-11947', 159, surface='Ruffo, p. 189',
                    note='Unidentified source cited for the 1671 Van Laer valuation.'),
    ]
    if any(m['mention_id'] in mention_by_id for m in new_mentions):
        raise SystemExit('mention ID collision')
    mentions.extend(new_mentions)
    mention_by_id.update({m['mention_id']: m for m in new_mentions})

    # Repair the source-form names and candidate mappings without changing S0.
    mention_updates = {
        'm-chp5-note-135-015': ('cand-11939', 'Bamboots attribution; distinct from Bamboccianti.'),
        'm-chp5-note-142-051': ('cand-6214', 'S0 OCR reads Valsrey; the printed note reads Valfrey.'),
        'm-chp5-note-154-099': ('cand-0671', 'Context identifies this Cardinal Chigi as Flavio Chigi.'),
        'm-chp5-note-154-103': ('cand-0671', 'Context identifies “the Chigi” as Cardinal Flavio Chigi.'),
        'm-chp5-note-154-104': ('cand-0671', 'Context identifies “the Chigi” as Cardinal Flavio Chigi.'),
        'm-chp5-note-150-076': ('cand-6191', 'Surname citation mapped to the cited 1963 publication candidate.'),
        'm-chp5-note-149-073': ('cand-11946', 'Surname-only citation retained as an unresolved archive candidate.'),
    }
    for mid, (cid, note) in mention_updates.items():
        if mid not in mention_by_id:
            raise SystemExit(f'expected mention missing: {mid}')
        mention_by_id[mid]['candidate_id'] = cid
        mention_by_id[mid]['note'] = note

    # Source quotation row is a print-only p.139 note absent from S0; do not invent a source line.
    for row in statements:
        if row['statement_id'] == 'st-chp5-p139-spanish-veto':
            q = row['qualifiers']
            for key in ('footnote_target_line', 'citation_segment_id', 'citation_source_line_start',
                        'citation_source_line_end', 'footnote_refs'):
                q.pop(key, None)
            q.update({
                'footnote_marker': 3,
                'footnote_link_status': 'print-only-omitted-from-s0',
                'print_only_footnote_text': 'Leman, pp. 13 ff., and Hanotaux, p. 9.',
                'print_only_source': 'CHP-5.pdf, physical page 24 (printed page 139)',
                'print_only_reference_status': 'Bibliographic locator recorded from print; cited works were not independently consulted.',
                'qualification': 'The printed p.139 note 3 is absent from the S0 transcription. Preserve it as a print-only source difference; do not manufacture an S0 statement or mention offset.',
            })

    # Correct body-to-footnote mapping across p.139–140 and populate statement IDs after atomization.
    note_150_ids = ['st-chp5-notes-l150-wallenstein-painting',
                    'st-chp5-notes-l126-165-l150-marabottini-citation',
                    'st-chp5-notes-l126-165-l150-wallenstein-authorship']
    note_154_ids = ['st-chp5-notes-l154-chigi-commission-unproven',
                    'st-chp5-notes-l154-no-payment-document',
                    'st-chp5-notes-l154-colonna-acquisition-alternative',
                    'st-chp5-notes-l126-165-l154-contemporary-ownership-reports',
                    'st-chp5-notes-l126-165-l154-pictures-listed-in-chigi-inventories',
                    'st-chp5-notes-l126-165-l154-acquisition-by-chigi-1661',
                    'st-chp5-notes-l126-165-l154-chigi-bought-palazzo-odescalchi',
                    'st-chp5-notes-l126-165-l154-golzio-citation']
    for sid in ('st-chp5-p139-turning-point',):
        if sid in by_id:
            set_note_link(by_id[sid], 1, 150, note_150_ids)
    for sid in ('st-chp5-p139-chigi-pictures', 'st-chp5-p139-chigi-pictures-codazzi-link',
                'st-chp5-p140-chigi-patron-continuation', 'st-chp5-p140-two-chigi-works'):
        if sid not in by_id:
            raise SystemExit(f'body link target missing: {sid}')
        set_note_link(by_id[sid], 1, 154, note_154_ids)
        q = by_id[sid]['qualifiers']
        q['qualification'] = (q.get('qualification', '') + ' Footnote 1 is on printed p.140 L154; p.139 note 1 at L150 belongs to the contemporary-event discussion.').strip()

    marker_by_line = {
        127: 1, 128: 2, 129: 1, 130: 1, 131: 2, 132: 3, 133: 4,
        134: 1, 135: 2, 136: 3, 137: 4, 138: 5,
        140: 3, 141: 4, 142: 1, 143: 2, 144: 3, 145: 4,
        146: 1, 147: 2, 148: 3, 149: 4, 150: 1, 151: 2,
        153: 6, 154: 1, 155: 2, 156: 1, 157: 2, 158: 3,
        159: 4, 160: 1, 161: 2, 162: 3, 163: 4, 164: 5, 165: 6,
    }
    for row in target_rows + added_statements:
        q = row.get('qualifiers', {})
        line = q.get('source_line_start')
        marker = marker_by_line.get(line)
        if line == 139:
            marker = 2 if row['statement_id'] == 'st-chp5-notes-l139-ibid' else 1
        elif line == 152:
            marker = 4 if row['statement_id'].endswith('filomarino-dispatches') else 5
        if marker is not None:
            q['footnote_marker'] = marker
            q['footnote_number'] = marker
            q['footnote_segment'] = SEG

    # Refresh body back-links to the note statements after atomic splitting.
    for body_row in statements:
        if body_row.get('segment_id') not in (BODY_PREV, BODY_NEXT):
            continue
        if body_row['statement_id'] == 'st-chp5-p139-spanish-veto':
            continue
        q = body_row.get('qualifiers', {})
        ref_line = q.get('citation_source_line_start', q.get('footnote_target_line'))
        existing_refs = q.get('footnote_refs') or []
        marker = existing_refs[0].get('marker') if existing_refs else q.get('footnote_marker')
        if body_row['statement_id'] in ('st-chp5-p139-chigi-pictures',
                                        'st-chp5-p139-chigi-pictures-codazzi-link',
                                        'st-chp5-p140-chigi-patron-continuation',
                                        'st-chp5-p140-two-chigi-works'):
            ref_line, marker = 154, 1
        elif body_row['statement_id'] == 'st-chp5-p139-turning-point':
            ref_line, marker = 150, 1
        if ref_line is None or marker is None:
            continue
        linked_ids = [r['statement_id'] for r in target_rows + added_statements
                      if r.get('qualifiers', {}).get('source_line_start') == ref_line
                      and r.get('qualifiers', {}).get('footnote_marker') == marker]
        if linked_ids:
            set_note_link(body_row, marker, ref_line, linked_ids)

    # Preserve the unresolved surname form while recording what the printed page shows.
    candidate_by_id['cand-6214']['canonical_name'] = 'Valfrey, cited publication, p. 220 (S0 OCR: Valsrey)'
    candidate_by_id['cand-6214']['detail'] = 'Cited intermediary source for the French ambassador’s description of Rapaccioli; the print reads Valfrey while S0 OCR reads Valsrey. Author and title remain unresolved; page 220 was not independently consulted.'

    # Update coverage only after all note lines and their print-layer exception are reviewed.
    coverage['note'] = (
        '脚注段L126–165及印刷p.142注1–6已逐条完成S2语义处理；补全出处引用、作品/文书/事件端点和原子断言，'
        '正文p.139–140的注1回链改接L154，p.139讨论当代事件的注1保留L150。印本p.139注3“Leman, pp.13 ff., and Hanotaux, p.9”未见于S0，'
        '仅在正文statement登记print-only缺注，不伪造S0行或mention。L142的印本拼写Valfrey与S0 OCR Valsrey之差记于候选/过程，不改S0。'
    )

    # Repair the existing note-1 recommendation to a proper book-to-source citation candidate.
    if by_id['st-chp5-notes-l128-briganti-survey']['qualifiers']['relation_candidate'] is not True:
        raise SystemExit('p.128 bibliography normalization failed')

    new_ids = {r['statement_id'] for r in added_statements}
    if len(new_ids) != len(added_statements) or set(by_id) & new_ids:
        raise SystemExit('new statement collision')
    all_statements = statements + added_statements
    all_by_id = {r['statement_id']: r for r in all_statements}
    if len(all_by_id) != len(all_statements):
        raise SystemExit('duplicate statement IDs after append')
    final_target_rows = [r for r in all_statements if r.get('segment_id') == SEG]
    if any(r.get('qualifiers', {}).get('relation_candidate') is None for r in final_target_rows):
        raise SystemExit('target segment still has unclassified statements')
    if any(r['qualifiers'].get('relation_candidate') is None for r in added_statements):
        raise SystemExit('new statement lacks relation classification')

    all_candidate_rows = candidates + new_candidates
    all_candidate_ids = {r['candidate_id'] for r in all_candidate_rows}
    for row in added_statements + final_target_rows:
        q = row.get('qualifiers', {})
        if q.get('relation_candidate') is True:
            if not row.get('subject_candidate_id') or not row.get('object_candidate_id'):
                raise SystemExit(f'missing relation endpoint: {row["statement_id"]}')
            if row['subject_candidate_id'] not in all_candidate_ids or row['object_candidate_id'] not in all_candidate_ids:
                raise SystemExit(f'unknown endpoint: {row["statement_id"]}')
        for cid in q.get('mentioned_candidate_ids', []) or []:
            if cid and cid not in all_candidate_ids:
                raise SystemExit(f'unknown mentioned candidate {cid}: {row["statement_id"]}')
        if row.get('segment_id') == SEG:
            line_start = q['source_line_start']
            line_end = q['source_line_end']
            source_span = '\n'.join(SOURCE_LINES[line_start - 1:line_end])
            if row.get('original_quote') and row['original_quote'] not in source_span:
                raise SystemExit(f'quote does not match S0 for {row["statement_id"]}')

    existing_ids = {r['mention_id'] for r in mentions}
    if len(existing_ids) != len(mentions):
        raise SystemExit('duplicate mention IDs')
    for m in new_mentions:
        if m['candidate_id'] not in all_candidate_ids:
            raise SystemExit(f'unknown candidate in mention {m["mention_id"]}')
        s, e = int(m['start_char']), int(m['end_char'])
        if SEGMENT_TEXT[s:e] != m['surface_form']:
            raise SystemExit(f'mention span does not match S0: {m["mention_id"]}')
        for prior in mentions:
            if prior['mention_id'] == m['mention_id'] or prior['segment_id'] != SEG:
                continue
            ps, pe = int(prior['start_char']), int(prior['end_char'])
            if max(s, ps) < min(e, pe):
                raise SystemExit(f'new mention overlaps existing mention {prior["mention_id"]}: {m["mention_id"]}')

    # Make the no-op/dry-run inspectable before any write.
    all_target_rows = [r for r in all_statements if r.get('segment_id') == SEG]
    relation_count = sum(r['qualifiers']['relation_candidate'] is True for r in all_target_rows)
    nonrelation_count = sum(r['qualifiers']['relation_candidate'] is False for r in all_target_rows)
    if relation_count + nonrelation_count != len(all_target_rows):
        raise SystemExit('classification count mismatch')
    new_candidate_ids = [r['candidate_id'] for r in new_candidates]
    new_mention_ids = [r['mention_id'] for r in new_mentions]

    statements_text = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in all_statements)
    candidates_text = csv_text(all_candidate_rows, candidate_fields)
    mentions_text = csv_text(mentions, mention_fields)
    coverage_text = csv_text(coverage_rows, coverage_fields)

    if args.apply:
        targets = [STATEMENTS, CANDIDATES, MENTIONS, COVERAGE]
        for path in targets:
            backup = path.with_name(path.name + BACKUP_TAG)
            if backup.exists():
                raise SystemExit(f'backup already exists; refusing to overwrite: {backup.name}')
        payloads = ((STATEMENTS, statements_text), (CANDIDATES, candidates_text),
                    (MENTIONS, mentions_text), (COVERAGE, coverage_text))
        temp_paths = []
        for path, content in payloads:
            temp = path.with_name(path.name + '.tmp-s2-chp5-notes-l126-165')
            if temp.exists():
                raise SystemExit(f'temporary output exists; refusing to overwrite: {temp.name}')
            temp.write_bytes(('\ufeff' + content).encode('utf-8'))
            temp_paths.append((path, temp))
        for path in targets:
            shutil.copy2(path, path.with_name(path.name + BACKUP_TAG))
        for path, temp in temp_paths:
            os.replace(temp, path)
        print('applied guarded p.132–142 note-segment semantic resolution')
        print('backups:', ', '.join(path.name + BACKUP_TAG for path in targets))
    else:
        print('PREVIEW only; no table writes')

    print(f'existing note statements classified: {len(unset_rows)}')
    print(f'atomic statements added: {len(added_statements)}')
    print(f'final note segment statements: {len(all_target_rows)}; relations={relation_count}; nonrelations={nonrelation_count}')
    print('new candidates:', ', '.join(new_candidate_ids))
    print('new mentions:', ', '.join(new_mention_ids))
    for row in added_statements:
        q = row['qualifiers']
        print(f"  added | {q['relation_candidate']} | L{q['source_line_start']} | {row['subject_candidate_id']} -> {row['predicate']} -> {row['object_candidate_id']} | {q.get('claim', '')}")
    for row in sorted(all_target_rows, key=lambda r: (r['qualifiers'].get('source_line_start', 0), r['statement_id'])):
        q = row['qualifiers']
        if q.get('relation_candidate') is None:
            raise SystemExit(f'unclassified final row {row["statement_id"]}')
    print('p.139–140 footnote targets corrected: p.139 event note -> L150; Chigi note 1 -> L154; p.139 printed note 3 recorded as print-only')


if __name__ == '__main__':
    main()
