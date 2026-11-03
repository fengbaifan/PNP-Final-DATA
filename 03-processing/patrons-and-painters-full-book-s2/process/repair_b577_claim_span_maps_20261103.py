#!/usr/bin/env python3
"""Dry-run/apply claim-span mapping repairs within the B577 review stage."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROCESS = ROOT / '03-processing/patrons-and-painters-full-book-s2/process'
TABLES = ROOT / '04-knowledge/tables'
RECOVERY = ROOT / '06-runtime/recovery/s2-b577-order-2060-2159'
PLAN_PATH = RECOVERY / 'claim-span-repair-plan.json'
sys.path.insert(0, str(PROCESS))
from adjudicate_s2_current_review_b576_order_1960_2059_20261103 import (  # noqa: E402
    atomic_write, canonical_hash, csv_bytes, jsonl_bytes, read_csv, read_jsonl,
    read_text, sha, text_bytes,
)

STATEMENTS = TABLES / 'book-statements.jsonl'
ROSTER = PROCESS / 's2-current-review-roster.csv'
MENTIONS = TABLES / 'mentions.csv'
STAGES = PROCESS / 'stages.md'
KNOWLEDGE = PROCESS / 'knowledge.md'
RESULT_STAGES = PROCESS.parent / 'results/stages.md'
CURRENT_RESULT = ROOT / '04-knowledge/results/patrons-and-painters-full-book-s2.md'
MAIN_SCRIPT = PROCESS / 'adjudicate_s2_current_review_b577_order_2060_2159_20261103.py'


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def prepare():
    applied_path = RECOVERY / 'applied.json'
    applied = json.loads(applied_path.read_text(encoding='utf-8'))
    require(applied['summary']['batch'] == 'S2-B577-CH2-2060-2159', 'Wrong recovery package')
    statements, st_raw, _, _ = read_jsonl(STATEMENTS)
    roster, rf, rr_raw, reol, rbom = read_csv(ROSTER)
    mentions, mf, mr_raw, meol, mbom = read_csv(MENTIONS)
    sb = {s['statement_id']: s for s in statements}
    rb = {r['statement_id']: r for r in roster}
    window = {int(r['current_order']): r for r in roster if 2060 <= int(r['current_order']) <= 2159}
    require(len(window) == 100 and len(statements) == 15518 and len(mentions) == 27359,
            'Unexpected current batch baseline')

    before_hashes = {
        p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
        for p in [STATEMENTS, ROSTER, MENTIONS, STAGES, KNOWLEDGE, RESULT_STAGES,
                  CURRENT_RESULT, MAIN_SCRIPT]
    }
    for rel, expected in applied['applied_outputs'].items():
        if rel in before_hashes and rel not in {
            STAGES.relative_to(ROOT).as_posix(), KNOWLEDGE.relative_to(ROOT).as_posix(),
            CURRENT_RESULT.relative_to(ROOT).as_posix(),
        }:
            require(before_hashes[rel] == expected, f'B577 output changed before repair: {rel}')
    final = applied['final_card_and_document_sha256']
    for p in [STAGES, KNOWLEDGE, CURRENT_RESULT]:
        rel = p.relative_to(ROOT).as_posix()
        require(before_hashes[rel] == final[rel], f'B577 final record changed before repair: {rel}')

    # Missing context mentions stay source anchored; unrelated names from the
    # adjacent clause are removed from the family-papal-patronage claim.
    target_maps = {
        2069: ['cand-0290', 'cand-4654', 'cand-1017', 'cand-4223'],
        2073: ['cand-0291', 'cand-4654', 'cand-1017', 'cand-4223'],
        2083: ['cand-0290', 'cand-4656', 'cand-12303', 'cand-1017', 'cand-4490'],
        2108: ['cand-4651', 'cand-12304', 'cand-4288'],
    }
    changed = {}
    for order, mapped in target_maps.items():
        sid = window[order]['statement_id']
        st = sb[sid]
        q = dict(st.get('qualifiers') or {})
        if q.get('mentioned_candidate_ids') != mapped:
            q['mentioned_candidate_ids'] = mapped
            st['qualifiers'] = q
            changed[sid] = st

    sid_2093 = window[2093]['statement_id']
    st_2093 = sb[sid_2093]
    q = dict(st_2093.get('qualifiers') or {})
    require(q.get('source_line_start') == 67 and st_2093.get('original_quote') ==
            'decorated by Guido Reni, Tassi, Gentileschi and others', '2093 source baseline changed')
    q['source_line_start'] = 66
    st_2093['qualifiers'] = q
    st_2093['original_quote'] = (
        'the great Borghese palace on the Quirinal, decorated by Guido Reni, Tassi, Gentileschi and others'
    )
    changed[sid_2093] = st_2093

    sid_2143 = window[2143]['statement_id']
    q_2143 = sb[sid_2143]['qualifiers']
    require('cand-4003' in q_2143.get('mentioned_candidate_ids', []), '2143 work-context mapping changed')
    segid = sb[sid_2143]['segment_id']
    segments, _, _, _ = read_jsonl(TABLES / 'segments.jsonl')
    seg = next(s for s in segments if s['segment_id'] == segid)
    source_lines = (ROOT / '02-sources/02-Markdown/02_CHP-2_sec_iv.md').read_text(encoding='utf-8-sig').splitlines()
    seg_text = '\n'.join(source_lines[int(seg['line_start']) - 1:int(seg['line_end'])])
    surface = 'the fresco'
    require(seg_text.count(surface) == 1, '2143 exact work-context phrase is not unique')
    start = seg_text.index(surface)
    mention_id = 'm-s2-b577-advisers-fresco-context'
    require(not any(m['mention_id'] == mention_id for m in mentions), 'Repair mention ID already exists')
    mentions.append({
        'mention_id': mention_id, 'segment_id': segid, 'candidate_id': 'cand-4003',
        'surface_form': surface, 'start_char': str(start), 'end_char': str(start + len(surface)),
        'note': 'B577 claim-span repair: the fresco named in the biblical-text sentence is the work context for the advisers’ interpretation; not an additional relation claim.',
    })
    mentions_by_segment = {}
    for m in mentions:
        mentions_by_segment.setdefault(m['segment_id'], []).append(m)
    for key in mentions_by_segment:
        mentions_by_segment[key].sort(key=lambda m: m['mention_id'])

    for sid, st in changed.items():
        row = rb[sid]
        row['current_statement_sha256'] = canonical_hash(st)
        if int(row.get('history_9622_event_count') or 0) > 0:
            row['history_9622_current_statement_match'] = (
                'exact' if row['history_9622_latest_statement_sha256'] == row['current_statement_sha256'] else 'changed'
            )
            row['prior_review_match'] = (
                'exact_object_and_source_segment'
                if row['history_9622_current_statement_match'] == 'exact' and row['history_9622_source_match'] == 'true'
                else 'historical_object_or_source_differs'
            )
    for row in roster:
        if row['segment_id'] == segid:
            mm = mentions_by_segment[segid]
            row['current_segment_mention_count'] = str(len(mm))
            row['current_segment_mentions_sha256'] = canonical_hash(mm)

    main_script_text, main_eol, main_bom, _ = read_text(MAIN_SCRIPT)
    replacements = {
        '2069:[290,4654]': '2069:[290,4654,1017,4223]',
        '2073:[291,4654]': '2073:[291,4654,1017,4223]',
        '2083:[290,4656,12303]': '2083:[290,4656,12303,1017,4490]',
        '2108:[290,291,4651,12304,4288]': '2108:[4651,12304,4288]',
        "for mid,candidate,surface in [('m-s2-b577-divine-sanction',11888,'the divine sanction given to the sovereigns of this world'),('m-s2-b577-larger-scheme',11889,'the much larger scheme of decoration that was to follow')]:":
        "for mid,candidate,surface in [('m-s2-b577-divine-sanction',11888,'the divine sanction given to the sovereigns of this world'),('m-s2-b577-larger-scheme',11889,'the much larger scheme of decoration that was to follow'),('m-s2-b577-advisers-fresco-context',4003,'the fresco')]:",
        "require(len(statements)==15518 and len(mentions)==27359 and len(backlog)==101,'Post counts inconsistent')":
        "require(len(statements)==15518 and len(mentions)==27360 and len(backlog)==101,'Post counts inconsistent')",
        "'mentions_added':2": "'mentions_added':3",
        'mention新增2条并修正2条': 'mention新增3条并修正2条',
        '新增divine sanction和later larger scheme两个精确span': '新增divine sanction、later larger scheme及adviser句中的fresco上下文精确span',
    }
    for old, new in replacements.items():
        require(main_script_text.count(old) == 1, f'Batch script anchor mismatch: {old[:80]}')
        main_script_text = main_script_text.replace(old, new, 1)
    # Make the source excerpt and line span for the unnamed additional decorators explicit.
    anchor = "    at(2094)['qualifiers']['seller_candidate_id'] = cid(4651)"
    source_fix = "    at(2093)['qualifiers']['source_line_start'] = 66\n    at(2093)['original_quote'] = 'the great Borghese palace on the Quirinal, decorated by Guido Reni, Tassi, Gentileschi and others'\n"
    require(main_script_text.count(anchor) == 1, 'Batch script source-span insertion point changed')
    main_script_text = main_script_text.replace(anchor, source_fix + anchor, 1)

    # Keep the visible per-ID audit table aligned with the corrected claim mappings.
    stages_text, stages_eol, stages_bom, _ = read_text(STAGES)
    table_maps = {n: ', '.join(f'`{x}`' for x in mapped) for n, mapped in target_maps.items()}
    updated_table_orders = set()
    lines = stages_text.splitlines()
    for i, line in enumerate(lines):
        parts = line.split('|')
        if len(parts) < 7 or not parts[1].strip().isdigit():
            continue
        order = int(parts[1].strip())
        if order in table_maps and parts[2].strip() == f"`{window[order]['statement_id']}`":
            parts[4] = ' ' + table_maps[order] + ' '
            lines[i] = '|'.join(parts)
            updated_table_orders.add(order)
    require(updated_table_orders == set(target_maps), f'Stage mapping rows mismatch: {updated_table_orders}')
    stages_text = '\n'.join(lines) + '\n'
    stages_text, n = re.subn(r'(?m)^连续100条：17条既有PASS核对当前statement／来源资产／S0段／mention-set指纹后复用；83条pending逐条对照印刷p\.48–51与原页，本次71条转PASS、12条保留pending。statement修订80条；未新增statement；mention新增2条并修正2条，现有提及逐项按segment切片断言surface form。$',
        '连续100条：17条既有PASS核对当前statement／来源资产／S0段／mention-set指纹后复用；83条pending逐条对照印刷p.48–51与原页，本次71条转PASS、12条保留pending。statement修订82条；未新增statement；mention新增3条并修正2条，现有提及逐项按segment切片断言surface form。2069、2073保留Ferrara与Papacy语境，2083补齐Ferrara→Rome职位端点；2108移除相邻句的Enzo、Guido误映射。2093扩展引文至明确的宫殿先行词；2143补入原文“the fresco”精确span。',
        stages_text, count=1)
    require(n == 1, 'Stage summary paragraph not found')

    knowledge_text, keol, kbom, _ = read_text(KNOWLEDGE)
    knowledge_text, n = knowledge_text.replace(
        'his ancestors缩为his的教皇指代，祖先群体不冒充Urban VIII；subject从Contracts子项改映Wisdom题材；新增divine sanction和later larger scheme两个精确span。',
        'his ancestors缩为his的教皇指代，祖先群体不冒充Urban VIII；subject从Contracts子项改映Wisdom题材；新增divine sanction、later larger scheme和adviser句中the fresco三个精确span。', 1), 1
    require(n == 1, 'Knowledge record S2 summary anchor changed')

    result_text, reol, rbom_text, _ = read_text(RESULT_STAGES)
    result_text, n = result_text.replace('2条新增mention及2条span／指代修正', '3条新增mention及2条span／指代修正', 1), 1
    require('B577当前结果' in result_text and '3条新增mention及2条span／指代修正' in result_text,
            'Result stages B577 summary mismatch')
    current_text, ceol, cbom_text, _ = read_text(CURRENT_RESULT)
    # Update only the current top-line S2 total and the B577 batch summary.
    current_text, n = current_text.replace('15,518条statement、27,359条mention', '15,518条statement、27,360条mention', 1), 1
    require(n == 1, 'Current result statement/mention total anchor changed')
    current_text, n = current_text.replace('B577连续2060–2159共100条：17条既有PASS复用、71条pending转PASS、12条保留pending。',
        'B577连续2060–2159共100条：17条既有PASS复用、71条pending转PASS、12条保留pending；原文span核平后全书mention为27,360。', 1), 1
    require(n == 1, 'Current result B577 summary anchor changed')

    # Verify the corrected pending candidates overlap their recorded source lines.
    source = (ROOT / '02-sources/02-Markdown/02_CHP-2_sec_iv.md').read_text(encoding='utf-8-sig').splitlines()
    pending_span_errors = []
    for order, row in window.items():
        if row['current_review_status'] != 'reviewed_current_pending':
            continue
        st = sb[row['statement_id']]
        seg = next(s for s in segments if s['segment_id'] == st['segment_id'])
        seg_lines = source[int(seg['line_start']) - 1:int(seg['line_end'])]
        offsets = [0]
        for line in seg_lines:
            offsets.append(offsets[-1] + len(line) + 1)
        q = st['qualifiers']
        lo_line, hi_line = int(q['source_line_start']), int(q['source_line_end'])
        lo = offsets[lo_line - int(seg['line_start'])]
        hi = offsets[hi_line - int(seg['line_start']) + 1]
        for candidate in q.get('mentioned_candidate_ids', []):
            if not any(m['segment_id'] == st['segment_id'] and m['candidate_id'] == candidate
                       and int(m['start_char']) < hi and int(m['end_char']) > lo for m in mentions):
                pending_span_errors.append((order, candidate))
    require(not pending_span_errors, f'Pending claim-span mapping errors: {pending_span_errors}')

    outputs = {
        STATEMENTS: jsonl_bytes(st_raw, changed),
        ROSTER: csv_bytes(roster, rf, reol, rbom),
        MENTIONS: csv_bytes(mentions, mf, meol, mbom),
        MAIN_SCRIPT: text_bytes(main_script_text, main_eol, main_bom),
        STAGES: text_bytes(stages_text, stages_eol, stages_bom),
        KNOWLEDGE: text_bytes(knowledge_text, keol, kbom),
        RESULT_STAGES: text_bytes(result_text, reol, rbom_text),
        CURRENT_RESULT: text_bytes(current_text, ceol, cbom_text),
    }
    before_hashes = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in outputs}
    after_hashes = {p.relative_to(ROOT).as_posix(): sha(raw) for p, raw in outputs.items()}
    summary = {
        'batch': 'S2-B577-CH2-2060-2159', 'changed_statements': sorted(changed),
        'updated_claim_mappings': target_maps, 'corrected_source_span_order': 2093,
        'added_mention': mention_id, 'pending_claim_span_errors': pending_span_errors,
        'mentions_before': len(mentions) - 1, 'mentions_after': len(mentions),
    }
    return outputs, {'before_hashes': before_hashes, 'after_hashes': after_hashes, 'summary': summary}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    RECOVERY.mkdir(parents=True, exist_ok=True)
    outputs, plan = prepare()
    if not args.apply:
        PLAN_PATH.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'mode': 'dry-run', **plan['summary'], 'plan': str(PLAN_PATH)}, ensure_ascii=False))
        return
    require(PLAN_PATH.exists(), 'Run dry-run first')
    require(json.loads(PLAN_PATH.read_text(encoding='utf-8')) == json.loads(json.dumps(plan, ensure_ascii=False)),
            'Repair plan changed; rerun dry-run and inspect')
    for p, raw in outputs.items():
        require(sha(p.read_bytes()) == plan['before_hashes'][p.relative_to(ROOT).as_posix()],
                f'Input changed before apply: {p}')
    backup = RECOVERY / 'before-claim-span-repair'
    for p in outputs:
        dest = backup / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        require(not dest.exists(), f'Repair backup already exists: {dest}')
        dest.write_bytes(p.read_bytes())
    written = []
    try:
        for p, raw in outputs.items():
            atomic_write(p, raw)
            written.append(p)
        for p, raw in outputs.items():
            require(p.read_bytes() == raw, f'Write verification failed: {p}')
    except Exception:
        for p in reversed(written):
            atomic_write(p, (backup / p.relative_to(ROOT)).read_bytes())
        raise

    applied = json.loads((RECOVERY / 'applied.json').read_text(encoding='utf-8'))
    applied['post_apply_claim_span_repairs'] = {
        **plan['summary'], 'final_hashes': plan['after_hashes'],
        'backup': str(backup.relative_to(ROOT)).replace('\\', '/'),
    }
    (RECOVERY / 'applied.json').write_text(json.dumps(applied, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    verification = json.loads((RECOVERY / 'verification.json').read_text(encoding='utf-8'))
    verification['mentions'] = 27360
    verification['claim_line_span_mismatches'] = []
    verification['post_apply_repairs'] = plan['summary']
    (RECOVERY / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'mode': 'applied', **plan['summary']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
