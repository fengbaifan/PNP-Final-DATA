from __future__ import annotations
import argparse, csv, hashlib, json, shutil
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge' / 'tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
MENTIONS = TABLES / 'mentions.csv'
COVERAGE = TABLES / 's2-coverage.csv'
SOURCE = ROOT / '02-sources' / '02-Markdown' / '10_CHP-10_sec_ii.md'
SEGMENT = 'chp-10:10_CHP-10_sec_ii:l241-246'
NOTE_SEGMENT = 'chp-10:10_CHP-10_sec_ii:l273-349'
SOURCE_FILE = '02-sources/02-Markdown/10_CHP-10_sec_ii.md'
BACKUP_SUFFIX = '.bak-s2-chp10-p328-semantic-reconciliation-20261014'
EXPECTED = {
    STATEMENTS.name: '9b4b785c009ec014e949c0327505ddf1d668e15f8e44e17127659868863c5439',
    MENTIONS.name: '08292dd34deed827c2e02d2ca12edabf3e391920c9bf41abc91cb0b791523688',
    COVERAGE.name: 'ee02ae7bbefa5ecffd9805174269dd44a949744e29cdf2681ad3ae7fad3f589d',
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


def quote(lines: list[str], start_line: int, end_line: int, start: str, end: str) -> str:
    block = '\n'.join(lines[start_line - 1:end_line])
    a = block.find(start)
    if a < 0:
        raise ValueError(f'quote start missing at {start_line}-{end_line}: {start!r}')
    b = block.find(end, a if start == end else a + len(start))
    if b < 0:
        raise ValueError(f'quote end missing at {start_line}-{end_line}: {end!r}')
    return block[a:b + len(end)]


def make_statement(sid: str, subject: str | None, obj: str | None, predicate: str,
                   source_quote: str, start: int, end: int, claim: str,
                   qualification: str, mentioned: list[str], relation: bool,
                   **extra: object) -> dict:
    qualifiers: dict[str, object] = {
        'source_line_start': start,
        'source_line_end': end,
        'printed_page': 328,
        'pdf_physical_page': 61,
        'claim': claim,
        'speaker': 'Haskell',
        'text_layer': 'authorial narrative',
        'qualification': qualification,
        'mentioned_candidate_ids': mentioned,
        'relation_candidate': relation,
    }
    qualifiers.update(extra)
    return {
        'statement_id': sid,
        'segment_id': SEGMENT,
        'subject_candidate_id': subject,
        'object_candidate_id': obj,
        'predicate': predicate,
        'qualifiers': qualifiers,
        'original_quote': source_quote,
        'origin': 'book',
        'source_file': SOURCE_FILE,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='write after exact-hash and row preflight')
    args = parser.parse_args()
    paths = [STATEMENTS, MENTIONS, COVERAGE, SOURCE]
    hashes = {path.name: sha(path) for path in paths}
    if hashes != EXPECTED:
        raise SystemExit(f'preflight hash mismatch; no writes made: {hashes}')

    lines = SOURCE.read_text(encoding='utf-8').splitlines()
    full_source = '\n'.join(lines)
    statement_rows = load_jsonl(STATEMENTS)
    by_id = {row['statement_id']: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit('duplicate statement_id in table')
    expected_ids = {
        'st-chp10-p328-arcadia-not-necessary-cause',
        'st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli',
        'st-chp10-p328-biffi-diary-on-rousseau',
        'st-chp10-p328-biffi-friendship-with-beccaria',
        'st-chp10-p328-biffi-friendship-with-verri',
        'st-chp10-p328-biffi-praised-zuccarelli-in-letter',
        'st-chp10-p328-english-landscape-market',
        'st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany',
        'st-chp10-p328-filosofo-poem-identified',
        'st-chp10-p328-gozzi-criticism-for-journal-space',
        'st-chp10-p328-midcentury-painting-social-question',
        'st-chp10-p328-ode-rousseau-influence',
        'st-chp10-p328-smith-employed-zuccarelli',
        'st-chp10-p328-zais-neglected',
        'st-chp10-p328-zanetti-praised-zuccarelli',
        'st-chp10-p328-zuccarelli-praised-by-patrons',
    }
    current_segment_ids = {row['statement_id'] for row in statement_rows if row.get('segment_id') == SEGMENT}
    if current_segment_ids != expected_ids:
        raise SystemExit(f'p.328 statement set mismatch: {sorted(current_segment_ids ^ expected_ids)}')
    if any(by_id[sid].get('qualifiers', {}).get('relation_candidate') is not None
           for sid in expected_ids if by_id[sid]['statement_id'] not in {
               'st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli',
               'st-chp10-p328-biffi-friendship-with-beccaria',
               'st-chp10-p328-biffi-friendship-with-verri',
               'st-chp10-p328-biffi-praised-zuccarelli-in-letter',
               'st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany',
               'st-chp10-p328-filosofo-poem-identified',
               'st-chp10-p328-ode-rousseau-influence',
               'st-chp10-p328-smith-employed-zuccarelli',
               'st-chp10-p328-zanetti-praised-zuccarelli',
           }):
        raise SystemExit('unexpected p.328 classification on an item expected to be unset')

    added_ids = {
        'st-chp10-p328-biffi-follower-of-rousseau-inferred',
        'st-chp10-p328-biffi-diary-entry-after-rousseau-death',
        'st-chp10-p328-arcadias-convincing',
        'st-chp10-p328-zais-authentic-robust',
        'st-chp10-p328-gozzi-criticized-for-journal-space',
        'st-chp10-p328-gozzi-traditional-reply-open',
        'st-chp10-p328-ode-spirit-partly-responsible-for-success',
    }
    if added_ids & by_id.keys():
        raise SystemExit(f'new statement IDs already exist: {sorted(added_ids & by_id.keys())}')

    def set_claim(sid: str, *, predicate: str | None = None, subject: str | None = None,
                  obj: str | None = None, source_quote: str | None = None,
                  claim: str | None = None, qualification: str | None = None,
                  mentioned: list[str] | None = None, relation: bool | None = None,
                  start: int | None = None, end: int | None = None,
                  remove_qualifiers: tuple[str, ...] = (), **extra: object) -> None:
        row = by_id[sid]
        q = row.setdefault('qualifiers', {})
        for key in remove_qualifiers:
            q.pop(key, None)
        if predicate is not None: row['predicate'] = predicate
        if subject is not None: row['subject_candidate_id'] = subject
        if obj is not None or sid == 'st-chp10-p328-english-landscape-market': row['object_candidate_id'] = obj
        if source_quote is not None: row['original_quote'] = source_quote
        if claim is not None: q['claim'] = claim
        if qualification is not None: q['qualification'] = qualification
        if mentioned is not None: q['mentioned_candidate_ids'] = mentioned
        if relation is not None: q['relation_candidate'] = relation
        if start is not None: q['source_line_start'] = start
        if end is not None: q['source_line_end'] = end
        q.update(extra)

    # Keep claims atomic and preserve quotations as they occur in the S0 OCR layer.
    set_claim('st-chp10-p328-arcadia-not-necessary-cause', relation=False)
    set_claim('st-chp10-p328-biffi-diary-on-rousseau',
        predicate='diary_entry_describes_rousseau_as_genius_guide_and_master',
        source_quote=quote(lines, 243, 243, '‘The greatest genius', 'my idol... . .’'),
        claim='Haskell quotes Biffi’s diary describing Rousseau as the century’s greatest genius and as his father, guide, master and idol.',
        qualification='This is a diary passage reported through Haskell and cited to Venturi, 1957, p.45; neither the diary nor Venturi was independently consulted. The quoted metaphor records Biffi’s expressed reverence, not proof of a specific causal influence.',
        mentioned=['cand-0373', 'cand-2289', 'cand-9833', 'cand-2751'], relation=True,
        source_line_start=243, source_line_end=243,
        speaker='Giambattista Biffi (as quoted by Haskell)',
        text_layer='quoted diaristic text reported in authorial narrative',
        footnote_marker=6, footnote_segment=NOTE_SEGMENT,
        footnote_refs=[{'marker': 6, 'segment_id': NOTE_SEGMENT, 'source_line': 342}],
        footnote_statement_ids=['st-chp10-p328-n06-venturi-locator'], footnote_body_link_status='linked',
        relation_candidate_note='Source-reported first-person tribute; S2 candidate only, not a formal relation.')
    set_claim('st-chp10-p328-english-landscape-market', relation=False,
        obj=None, mentioned=['cand-2879', 'cand-3575'],
        qualification='This is Haskell’s explanation of reception through a broad, unnamed English audience and its supposed taste, not a claim about Consul Smith or every English patron. The OCR reads “Use”; the p.328 scan reads “life”.',
        ocr_corrections=[{'source_line': 242, 'ocr': 'country house Use', 'print': 'country house life'}])
    set_claim('st-chp10-p328-gozzi-criticism-for-journal-space',
        predicate='among_first_to_address_painting_social_importance_in_venice',
        source_quote=quote(lines, 246, 246, 'Gasparo Gozzi was among the first', 'in Venice.'),
        claim='Haskell says Gozzi was among the first in Venice to address painting’s importance in modern life.',
        qualification='This is Haskell’s characterization of Gozzi’s place in the discussion; it is separated from the following 1760 report about criticism of his journalism.',
        mentioned=['cand-1222', 'cand-1805'], relation=True,
        source_line_start=246, source_line_end=246,
        relation_candidate_note='The passage links Gozzi to the debate on painting’s social importance; S2 candidate, not a formal edge.',
        remove_qualifiers=('footnote_marker','footnote_segment','footnote_refs','footnote_statement_ids','footnote_body_link_status'))
    set_claim('st-chp10-p328-midcentury-painting-social-question', relation=False)
    set_claim('st-chp10-p328-ode-rousseau-influence',
        source_quote=quote(lines, 242, 242, 'was strongly influenced by Rousseau', 'was strongly influenced by Rousseau'),
        claim='Haskell describes Il Filosofo dell’Alpi as strongly influenced by Rousseau.',
        qualification='This is Haskell’s literary interpretation; it does not make Rousseau the poem’s sole source.',
        mentioned=['cand-9829', 'cand-2289'], relation=True)
    set_claim('st-chp10-p328-zais-neglected',
        predicate='described_as_wholly_neglected',
        source_quote=quote(lines, 244, 244, 'was wholly neglected.', 'was wholly neglected.'),
        claim='Haskell says Giuseppe Zais was wholly neglected.',
        qualification='This is Haskell’s comparative statement about reception, not a measured account of every patron or Zais’s whole career.',
        mentioned=['cand-2830'], relation=False, source_line_start=244, source_line_end=244)
    set_claim('st-chp10-p328-zuccarelli-praised-by-patrons', relation=False)

    note6 = {
        'speaker': 'Giambattista Biffi (as reported by Haskell)',
        'text_layer': 'authorial narrative reporting a diaristic act',
        'footnote_marker': 6,
        'footnote_segment': NOTE_SEGMENT,
        'footnote_refs': [{'marker': 6, 'segment_id': NOTE_SEGMENT, 'source_line': 342}],
        'footnote_statement_ids': ['st-chp10-p328-n06-venturi-locator'],
        'footnote_body_link_status': 'linked',
    }
    rows_to_add = [
        make_statement('st-chp10-p328-biffi-follower-of-rousseau-inferred', 'cand-0373', 'cand-2289',
            'inferred_follower_of', quote(lines, 243, 243, 'The language alone would betray a follower of Rousseau', 'The language alone would betray a follower of Rousseau'),
            243, 243, 'Haskell infers from the language of Biffi’s letter that Biffi was a follower of Rousseau.',
            'This is Haskell’s inference from the wording of a letter, not Biffi’s own self-identification; keep it distinct from the poem’s influence and the later diary tribute.',
            ['cand-0373', 'cand-2289'], True,
            relation_candidate_note='Authorial inference about Biffi and Rousseau; S2 candidate only, not an independently verified relation.'),
        make_statement('st-chp10-p328-biffi-diary-entry-after-rousseau-death', 'cand-0373', 'cand-2289',
            'wrote_diary_entry_after_hearing_of_death', quote(lines, 243, 243, 'when Biffi heard later of that philosopher’s death, he wrote in his diary6:', 'when Biffi heard later of that philosopher’s death, he wrote in his diary6:'),
            243, 243, 'Haskell says Biffi later heard of Rousseau’s death and wrote in his diary.',
            'The entry is reported by Haskell and cited to Venturi, 1957, p.45; neither source was independently consulted. The diary’s quoted praise is recorded separately.',
            ['cand-0373', 'cand-2289', 'cand-9833', 'cand-2751'], False, **note6),
        make_statement('st-chp10-p328-arcadias-convincing', 'cand-9834', None,
            'described_as_convincing_for_believers_in_natural_life', quote(lines, 243, 244, 'Purely artificial', 'natural life:'),
            243, 244, 'Haskell says golden-misted, artificial Arcadias could still convince people strongly drawn to the idea of natural life.',
            'This is Haskell’s aesthetic and reception judgment; “believers” is not identified as a bounded group.',
            ['cand-9834'], False),
        make_statement('st-chp10-p328-zais-authentic-robust', 'cand-2830', None,
            'described_as_authentic_robust_interpreter_of_countryside', quote(lines, 244, 244, 'a more authentic and robust interpreter of the countryside', 'a more authentic and robust interpreter of the countryside'),
            244, 244, 'Haskell characterizes Zais as a more authentic and robust interpreter of the countryside.',
            'This is Haskell’s aesthetic comparison, separated from the distinct claim that Zais was neglected.',
            ['cand-2830'], False),
        make_statement('st-chp10-p328-gozzi-criticized-for-journal-space', 'cand-1222', None,
            'reported_attacked_for_journal_space_on_buildings_altars_and_pictures', quote(lines, 246, 246, 'Writing in 1760 he admitted', 'pictures.7'),
            246, 246, 'Haskell says Gozzi admitted in 1760 that he had been attacked for devoting too much journal space to buildings, altars and pictures.',
            'The attackers are unnamed, and the report is cited through the Gazzetta Veneta note; the issue was not independently consulted.',
            ['cand-1222', 'cand-1805', 'cand-8729'], False,
            footnote_marker=7, footnote_segment=NOTE_SEGMENT,
            footnote_refs=[{'marker': 7, 'segment_id': NOTE_SEGMENT, 'source_line': 342}],
            footnote_statement_ids=['st-chp10-p328-n07-gazzetta-citation'], footnote_body_link_status='linked'),
        make_statement('st-chp10-p328-gozzi-traditional-reply-open', 'cand-1222', 'cand-1805',
            'began_traditional_reply_about_cultural_objects_open_fragment', quote(lines, 246, 246, 'After making the traditional reply that these represent', 'After making the traditional reply that these represent'),
            246, 246, 'Haskell begins the account of Gozzi’s traditional reply but the clause is unfinished at the page break.',
            'The referent of “these” and the claim’s completion continue on p.329; do not read this fragment as a complete independent proposition.',
            ['cand-1222', 'cand-1805'], False,
            continuation_to_segment_id='chp-10:10_CHP-10_sec_ii:l248-256',
            continuation_to_statement_id='st-chp10-p329-gozzi-social-value', continuation_status='open'),
        make_statement('st-chp10-p328-ode-spirit-partly-responsible-for-success', 'cand-9829', 'cand-2879',
            'poem_spirit_partly_contributed_to_artist_success', quote(lines, 242, 242, 'and the spirit that informed it was partly responsible', 'almost the only Venetian artist of the eighteenth century who won unqualified praise from every different kind of patron.'),
            242, 242, 'Haskell says the spirit of the ode was partly responsible for Zuccarelli’s success.',
            'This is Haskell’s qualified causal interpretation, not a claim that the poem was the sole cause; the praise itself is recorded separately.',
            ['cand-9829', 'cand-2879'], True,
            relation_candidate_note='Qualified causal claim from Haskell; S2 candidate only, not a formal edge.'),
    ]
    for row in rows_to_add:
        if row['original_quote'] not in full_source:
            raise SystemExit(f"new quote not in S0 OCR source: {row['statement_id']}")
        if row['statement_id'] in by_id:
            raise SystemExit(f"new statement ID exists: {row['statement_id']}")
        statement_rows.append(row)
        by_id[row['statement_id']] = row

    # Add the exact mention of landscape painting; avoid mapping the broad English audience to Consul Smith.
    mention_fields, mention_rows = load_csv(MENTIONS)
    if not mention_fields:
        raise SystemExit('mentions table has no header')
    mention_id = 'm-s2-ch10-p328-0042'
    if any(row.get('mention_id') == mention_id for row in mention_rows):
        raise SystemExit(f'mention ID already exists: {mention_id}')
    source_segment = '\n'.join(lines[240:246])
    needle = 'landscape painting'
    start = source_segment.find(needle)
    if start < 0:
        raise SystemExit('landscape painting mention not found in p.328 segment')
    mention_rows.append({
        'mention_id': mention_id, 'segment_id': SEGMENT, 'candidate_id': 'cand-3575',
        'surface_form': needle, 'start_char': str(start), 'end_char': str(start + len(needle)),
        'note': 'Landscape genre mentioned in Haskell’s explanation of Zuccarelli’s English reception; “country house Use” is OCR for printed “life”.'
    })

    coverage_fields, coverage_rows = load_csv(COVERAGE)
    matches = [row for row in coverage_rows if row.get('segment_id') == SEGMENT]
    if len(matches) != 1:
        raise SystemExit(f'expected one coverage row, found {len(matches)}')
    matches[0]['note'] = 'p.328 body semantically reviewed against the page scan; atomic claims separated, OCR “Use” corrected to printed “life” in S2 qualifiers, and the unfinished Gozzi reply linked to its p.329 continuation. Page notes are linked.'

    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in [STATEMENTS, MENTIONS, COVERAGE]]
    for backup, source in zip(backup_paths, [STATEMENTS, MENTIONS, COVERAGE]):
        if backup.exists():
            raise SystemExit(f'backup already exists; refusing overwrite: {backup.name}')
    outputs = {
        STATEMENTS: dump_jsonl(statement_rows),
        MENTIONS: dump_csv(mention_fields, mention_rows),
        COVERAGE: dump_csv(coverage_fields, coverage_rows),
    }
    print('MODE', 'APPLY' if args.apply else 'PREVIEW')
    print('P328_STATEMENTS', sum(row.get('segment_id') == SEGMENT for row in statement_rows),
          'TRUE', sum(row.get('segment_id') == SEGMENT and row.get('qualifiers', {}).get('relation_candidate') is True for row in statement_rows),
          'FALSE', sum(row.get('segment_id') == SEGMENT and row.get('qualifiers', {}).get('relation_candidate') is False for row in statement_rows),
          'UNSET', sum(row.get('segment_id') == SEGMENT and 'relation_candidate' not in row.get('qualifiers', {}) for row in statement_rows))
    print('ADDED_STATEMENTS', len(rows_to_add), 'ADDED_MENTIONS', 1, 'P328_MENTION_ID', mention_id)
    for row in rows_to_add: print('ADD', row['statement_id'], row['qualifiers']['relation_candidate'])
    if not args.apply:
        return 0
    for backup, source in zip(backup_paths, [STATEMENTS, MENTIONS, COVERAGE]):
        shutil.copy2(source, backup)
    temp_paths: list[Path] = []
    try:
        for path, data in outputs.items():
            tmp = path.with_name(path.name + '.tmp-p328-semantic-reconciliation')
            tmp.write_bytes(data)
            temp_paths.append(tmp)
        for tmp, path in zip(temp_paths, outputs.keys()):
            tmp.replace(path)
    except Exception:
        for tmp in temp_paths:
            if tmp.exists(): tmp.unlink()
        raise
    print('BACKUPS', *(p.name for p in backup_paths))
    print('POST_HASHES', *(f'{p.name}={sha(p)}' for p in [STATEMENTS, MENTIONS, COVERAGE]))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
