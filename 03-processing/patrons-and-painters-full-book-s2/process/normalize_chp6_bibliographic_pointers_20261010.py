from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / '04-knowledge/tables'
STATEMENTS = TABLES / 'book-statements.jsonl'
CANDIDATES = TABLES / 'entity-candidates.csv'
SOURCE = ROOT / '02-sources/02-Markdown/06_CHP-6_sec_iv.md'
BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + '.bak-s2-handoff-chp6-bibliographic-pointers-20261010'
)
EXPECTED_STATEMENTS_SHA256 = (
    '38cd056fcd07de138fb81cc223dc28c5cdff279530640e5326b3c7f4cbd9daea'
)
EXPECTED_SOURCE_SHA256 = (
    '65de7b08cd2bad4cbf783d807160ef15e80cb031a47e1f28a6cb6c0f2b29e775'
)
BOOK_ID = 'cand-2962'
SOURCE_FILE = '02-sources/02-Markdown/06_CHP-6_sec_iv.md'
SEGMENT_ID = 'chp-6:06_CHP-6_sec_iv:l55-72'
NEW_MISSON_ID = 'st-chp6-p160-note3-misson-citation'

# The citation target and topical context were checked against each note and
# its linked body statement. Footnotes 160.1 and 160.2 name a publication
# locator for a separately represented source; footnote 160.3 contains two
# independent citations and is split below.
TARGETS = {
    'st-chp6-p158-notes-p158-n1-biagi-mare-magnum': {
        'old_subject': 'cand-1554', 'old_object': 'cand-6412',
        'archive': 'cand-6412', 'context': 'cand-1554',
        'line': 59, 'page': '158', 'marker': 1,
        'locator': 'Guido Biagi, introduction to Mare Magnum',
    },
    'st-chp6-p158-notes-p158-n4-donahue-1946': {
        'old_subject': 'cand-0272', 'old_object': 'cand-6422',
        'archive': 'cand-6422', 'context': 'cand-0272',
        'line': 62, 'page': '158', 'marker': 4,
        'locator': 'Donahue, 1946',
    },
    'st-chp6-p159-note1-schlosser-magnino': {
        'old_subject': 'cand-0272', 'old_object': 'cand-6440',
        'archive': 'cand-6440', 'context': 'cand-0272',
        'line': 63, 'page': '159', 'marker': 1,
        'locator': 'Schlosser Magnino',
    },
    'st-chp6-p159-note2-bellori-1942-p99': {
        'old_subject': 'cand-0272', 'old_object': 'cand-6338',
        'archive': 'cand-6338', 'context': 'cand-1526',
        'line': 64, 'page': '159', 'marker': 2,
        'locator': 'Bellori, 1942, p. 99',
    },
    'st-chp6-p159-note3-bellori-pascoli': {
        'old_subject': 'cand-0272', 'old_object': 'cand-6338',
        'archive': 'cand-6338', 'context': 'cand-1526',
        'line': 65, 'page': '159', 'marker': 3,
        'locator': 'Bellori, 1942, p. 92',
    },
    'st-chp6-p159-note3-pascoli-I': {
        'old_subject': 'cand-0272', 'old_object': 'cand-4834',
        'archive': 'cand-4834', 'context': 'cand-1526',
        'line': 65, 'page': '159', 'marker': 3,
        'locator': 'Pascoli, vol. I, p. 211',
    },
    'st-chp6-p159-note4-bellori-1942-p115': {
        'old_subject': 'cand-0272', 'old_object': 'cand-6338',
        'archive': 'cand-6338', 'context': 'cand-0272',
        'line': 65, 'page': '159', 'marker': 4,
        'locator': 'Bellori, 1942, p. 115',
    },
    'st-chp6-p160-note1-avvisi-roma-1941': {
        'old_subject': 'cand-6451', 'old_object': 'cand-6452',
        'archive': 'cand-6451', 'context': 'cand-6445',
        'line': 66, 'page': '160', 'marker': 1,
        'locator': 'Roma, vol. XIX (1941), p. 392',
        'publication_candidate_id': 'cand-6452',
    },
    'st-chp6-p160-note2-jacomo-letter-ruffo': {
        'old_subject': 'cand-6453', 'old_object': 'cand-6454',
        'archive': 'cand-6453', 'context': 'cand-0606',
        'line': 67, 'page': '160', 'marker': 2,
        'locator': 'Letter of 20 September 1670; V. Ruffo, 1916, p. 290',
        'publication_candidate_id': 'cand-6454',
    },
    'st-chp6-p160-note3-skippon-misson': {
        'old_subject': 'cand-6455', 'old_object': 'cand-6457',
        'archive': 'cand-6455', 'context': 'cand-0675',
        'line': 68, 'page': '160', 'marker': 3,
        'locator': 'Skippon, p. 676',
        'split': True,
    },
    'st-chp6-p160-note4-bildt-1904': {
        'old_subject': 'cand-6459', 'old_object': 'cand-6458',
        'archive': 'cand-6458', 'context': 'cand-5565',
        'line': 69, 'page': '160', 'marker': 4,
        'locator': 'Bildt, 1904, pp. 989-1003',
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_candidates() -> dict[str, dict[str, str]]:
    with CANDIDATES.open(encoding='utf-8-sig', newline='') as f:
        return {row['candidate_id']: row for row in csv.DictReader(f)}


def citation_row(source_id: str, locator: str, publication_id: str | None = None) -> dict:
    result = {'source_candidate_id': source_id, 'locator': locator}
    if publication_id:
        result['publication_candidate_id'] = publication_id
    return result


def set_citation(
    row: dict,
    spec: dict,
    candidates: dict[str, dict[str, str]],
    *,
    claim_override: str | None = None,
) -> dict:
    archive_id = spec['archive']
    archive = candidates.get(archive_id)
    context = candidates.get(spec['context'])
    if not archive or archive.get('suggested_type') != 'archive':
        raise SystemExit(f'citation target is absent or not archive typed: {row["statement_id"]}')
    if not context:
        raise SystemExit(f'citation context candidate is absent: {row["statement_id"]}')

    q = dict(row.get('qualifiers') or {})
    old_claim = str(q.get('claim') or '').strip()
    if not old_claim:
        raise SystemExit(f'original topical claim is missing: {row["statement_id"]}')
    row = dict(row)
    row.update({
        'subject_candidate_id': BOOK_ID,
        'object_candidate_id': archive_id,
        'predicate': 'cites',
    })
    q.update({
        'claim': claim_override or (
            f'Haskell’s book cites {archive["canonical_name"]} in footnote '
            f'{spec["marker"]}. The note’s topical context from the prior S2 record is: '
            f'{old_claim}'
        ),
        'citation_context_candidate_id': spec['context'],
        'text_layer': 'bibliographic citation',
        'citations': [citation_row(
            archive_id, spec['locator'], spec.get('publication_candidate_id')
        )],
        'relation_candidate': True,
        'relation_candidate_note': (
            'S2 cites candidate: the footnote explicitly points from Haskell’s book '
            'to this cited source. This records a bibliographic link only; it does not '
            'independently verify the cited material or create a formal S6 edge.'
        ),
        'cited_material_not_independently_consulted': True,
    })
    row['qualifiers'] = q
    return row


def prepare() -> tuple[bytes, bytes, dict]:
    before = STATEMENTS.read_bytes()
    if digest(before) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit(f'statement table changed: {digest(before)}')
    source_bytes = SOURCE.read_bytes()
    if digest(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f'source file changed: {digest(source_bytes)}')

    candidates = read_candidates()
    if candidates.get(BOOK_ID, {}).get('suggested_type') != 'archive':
        raise SystemExit('Haskell book candidate is absent or not archive typed')
    if set(TARGETS) - set(candidates_by_statement := {
        r['statement_id']: r
        for r in (json.loads(line) for line in before.decode('utf-8').splitlines() if line.strip())
    }):
        raise SystemExit('one or more fixed target statement IDs are missing')
    if NEW_MISSON_ID in candidates_by_statement:
        raise SystemExit(f'new split statement ID already exists: {NEW_MISSON_ID}')

    source_lines = source_bytes.decode('utf-8-sig').splitlines()
    rows = list(candidates_by_statement.values())
    targets = []
    for sid, spec in TARGETS.items():
        row = candidates_by_statement[sid]
        q = row.get('qualifiers') or {}
        if (
            row.get('segment_id') != SEGMENT_ID
            or row.get('source_file') != SOURCE_FILE
            or row.get('origin') != 'book'
            or row.get('predicate') != 'footnote_bibliographic_pointer'
            or row.get('subject_candidate_id') != spec['old_subject']
            or row.get('object_candidate_id') != spec['old_object']
            or q.get('relation_candidate') is not None
            or q.get('source_line_start') != spec['line']
            or q.get('source_line_end') != spec['line']
            or str(q.get('printed_page')) != spec['page']
            or q.get('footnote_marker') != spec['marker']
        ):
            raise SystemExit(f'fixed source contract changed: {sid}')
        if spec['line'] > len(source_lines) or row['original_quote'] not in source_lines[spec['line'] - 1]:
            raise SystemExit(f'quote no longer matches its source line: {sid}')
        for candidate_id in (spec['archive'], spec['context']):
            if candidate_id not in candidates:
                raise SystemExit(f'candidate endpoint missing: {sid} -> {candidate_id}')
        targets.append(row)

    output = []
    changed = []
    body_backlinks_updated = 0
    for original in rows:
        sid = original['statement_id']
        if sid not in TARGETS:
            row = dict(original)
            q = dict(row.get('qualifiers') or {})
            ids = q.get('footnote_statement_ids')
            if sid == 'st-chp6-p160-christina-quoted-appearance':
                if not isinstance(ids, list):
                    raise SystemExit('Christina footnote backlink is missing or malformed')
                if 'st-chp6-p160-note3-skippon-misson' not in ids:
                    raise SystemExit('existing Christina footnote backlink changed')
                if NEW_MISSON_ID not in ids:
                    q['footnote_statement_ids'] = [*ids, NEW_MISSON_ID]
                    row['qualifiers'] = q
                    body_backlinks_updated += 1
            output.append(row)
            continue

        spec = TARGETS[sid]
        if spec.get('split'):
            q = dict(original.get('qualifiers') or {})
            source_mentions = q.get('mentioned_candidate_ids')
            if not isinstance(source_mentions, list):
                raise SystemExit('compound citation mention list is missing')
            q['mentioned_candidate_ids'] = [
                candidate_id for candidate_id in source_mentions
                if candidate_id in {'cand-2438', 'cand-6455', 'cand-0675'}
            ]
            original = dict(original)
            original['qualifiers'] = q
            skippon_claim = (
                'Haskell’s book cites Skippon, p. 676, in footnote 3 for the quoted '
                'physical description of Christina. The note does not map the source '
                'to any individual phrase.'
            )
            output.append(set_citation(original, spec, candidates, claim_override=skippon_claim))
            changed.append({'statement_id': sid, 'archive': spec['archive'], 'locator': spec['locator']})

            misson_spec = dict(spec)
            misson_spec.update({'archive': 'cand-6457', 'locator': 'Misson, 1717, vol. II, p. 167'})
            misson = dict(original)
            misson['statement_id'] = NEW_MISSON_ID
            misson['qualifiers'] = dict(original['qualifiers'])
            misson['qualifiers']['mentioned_candidate_ids'] = [
                candidate_id for candidate_id in source_mentions
                if candidate_id in {'cand-6456', 'cand-6457', 'cand-0675'}
            ]
            misson_claim = (
                'Haskell’s book cites Misson, 1717, vol. II, p. 167, in footnote 3 '
                'for the quoted physical description of Christina. The note does not '
                'map the source to any individual phrase.'
            )
            output.append(set_citation(misson, misson_spec, candidates, claim_override=misson_claim))
            changed.append({'statement_id': NEW_MISSON_ID, 'archive': 'cand-6457', 'locator': misson_spec['locator']})
            continue

        output.append(set_citation(original, spec, candidates))
        changed.append({'statement_id': sid, 'archive': spec['archive'], 'locator': spec['locator']})

    if body_backlinks_updated != 1:
        raise SystemExit(f'expected one backlink update, found {body_backlinks_updated}')
    if len({row['statement_id'] for row in output}) != len(output):
        raise SystemExit('duplicate statement IDs after split')

    after = ('\n'.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) for row in output) + '\n').encode('utf-8')
    true_rows = [row for row in output if (row.get('qualifiers') or {}).get('relation_candidate') is True]
    complete = sum(bool(row.get('subject_candidate_id') and row.get('object_candidate_id')) for row in true_rows)
    dual_unclassified = sum(
        bool(row.get('subject_candidate_id') and row.get('object_candidate_id'))
        and (row.get('qualifiers') or {}).get('relation_candidate') is None
        for row in output
    )
    if (len(output), len(true_rows), complete, len(true_rows) - complete, dual_unclassified) != (12664, 3625, 3611, 14, 4443):
        raise SystemExit('unexpected post-state counts')
    return before, after, {
        'changed_citations': changed,
        'source_statements_reviewed': len(TARGETS),
        'citation_statements_after_split': len(changed),
        'new_statement_id': NEW_MISSON_ID,
        'body_backlinks_updated': body_backlinks_updated,
        'statement_rows': len(output),
        'relation_candidates': len(true_rows),
        'complete_endpoints': complete,
        'open_endpoints': len(true_rows) - complete,
        'dual_endpoint_unclassified': dual_unclassified,
        'before_sha256': digest(before),
        'after_sha256': digest(after),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before, after, report = prepare()
    if not args.apply:
        print(json.dumps({'mode': 'dry-run', **report}, ensure_ascii=False, indent=2))
        return 0
    if BACKUP.exists():
        raise SystemExit(f'recovery copy already exists: {BACKUP}')
    if STATEMENTS.read_bytes() != before:
        raise SystemExit('statement table changed after dry-run')
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + '.tmp-chp6-bibliographic-pointers')
    try:
        temporary.write_bytes(after)
        os.replace(temporary, STATEMENTS)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(json.dumps({'mode': 'applied', 'backup': str(BACKUP.relative_to(ROOT)), **report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
