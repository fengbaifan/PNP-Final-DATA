from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_s5_s6_archive_citations_20261020 as endpoint_queue  # noqa: E402
from scripts.build_field_facts import extract_records  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
STAGES_PATH = PROCESS_DIR / "stages.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
AGENTS_PATH = ROOT / "AGENTS.md"

CANDIDATE = "cand-5556"
GROUP = "workgrp-8b74eec6fd2029"
KU_ID = "units/works/a-storm-at-sea-claude-orsini"
CARD_REL = "04-knowledge/units/works/a-storm-at-sea-claude-orsini.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "《海上风暴》"
NAME_EN = "A Storm at Sea"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/04_CHP-4_sec_i.md"
ANCHOR = "s4-s5-s6-storm-at-sea-20261021"
S2_REPAIR_ANCHOR = "s2-repair-storm-at-sea-footnote-anchor-20261021"

DIRECT_STATEMENT_IDS = {
    "st-chp4-sec-i-l26-33-claude-seascape",
    "st-chp4-sec-i-l26-33-claude-authored-picture",
    "st-chp4-sec-i-l26-33-storm-motto-connection",
    "st-chp4-sec-i-l42-67-fn97-claude-picture-record",
    "st-chp4-sec-i-l42-67-claude-picture-recorded-in-liber-veritatis",
}
RELATION_STATEMENT_IDS = DIRECT_STATEMENT_IDS - {
    "st-chp4-sec-i-l42-67-fn97-claude-picture-record"
}
PARENT_STATEMENT_ID = "st-chp4-sec-i-l42-67-fn97-claude-picture-record"
RECORD_RELATION_STATEMENT_ID = "st-chp4-sec-i-l42-67-claude-picture-recorded-in-liber-veritatis"


def fmt(value: int) -> str:
    return f"{value:,}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def encode_text_like(path: Path, text: str) -> bytes:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    payload = text.encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + payload


def csv_bytes_like(path: Path, fieldnames: list[str], rows: list[dict]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    payload = output.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if path.read_bytes().startswith(b"\xef\xbb\xbf") else b"") + payload


def jsonl_patch_bytes(path: Path, replacements: dict[str, dict] | None = None, additions: list[dict] | None = None) -> bytes:
    """Patch JSONL records without reformatting unrelated source lines."""
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    pending = dict(replacements or {})
    output = []
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if content:
            record = json.loads(content)
            key = record.get("statement_id") or record.get("enrichment_id")
            if key in pending:
                newline = line[len(content):]
                compact = not re.match(r'^\s*\{\s*"[^"]+":\s', content)
                rendered = json.dumps(
                    pending.pop(key),
                    ensure_ascii=False,
                    **({"separators": (",", ":")} if compact else {}),
                )
                line = rendered + newline
        output.append(line)
    assert not pending, f"JSONL replacement targets not found: {sorted(pending)}"
    if additions:
        if output and not output[-1].endswith(("\n", "\r")):
            output[-1] += "\n"
        output.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in additions)
    return bom + "".join(output).encode("utf-8")


def atomic_write(path: Path, payload: bytes) -> None:
    temp = path.with_name(path.name + ".codex-tmp")
    temp.write_bytes(payload)
    os.replace(temp, path)


def current_group(note: str) -> str:
    return sync.get_group(note or "")


def replace_one(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.M)
    assert count == 1, f"expected one {label}; found {count}"
    return updated


def insert_accepted(text: str) -> str:
    assert CARD_REL not in text
    lines = text.splitlines()
    insert_at = next(
        (
            index for index, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((index for index, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def add_alignment_mapping(alignment_rows: list[dict]) -> list[dict]:
    updated = [dict(row) for row in alignment_rows]
    target = [row for row in updated if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(target) == 1
    target[0]["ku_id"] = KU_ID
    target[0]["resolution_note"] = (
        (target[0].get("resolution_note", "") or "").rstrip()
        + f" S4 registration: mapped {GROUP} to {KU_ID}."
    )
    return updated


def add_statement_repairs(statements: list[dict]) -> list[dict]:
    updated = [dict(row) for row in statements]
    by_id = {row["statement_id"]: row for row in updated}
    parent = by_id[PARENT_STATEMENT_ID]
    parent_q = parent.setdefault("qualifiers", {})
    corrections = parent_q.setdefault("ocr_corrections", [])
    correction = {
        "source_line": 58,
        "source_form": "Rdthlisberger",
        "print_reading": "Röthlisberger",
        "locator": "CHP-4.pdf physical page 4 / print p.97",
    }
    if correction not in corrections:
        corrections.append(correction)

    relation = by_id[RECORD_RELATION_STATEMENT_ID]
    relation_q = relation.setdefault("qualifiers", {})
    relation_q["printed_page_locator"] = "p.97"
    relation_q["pdf_physical_page"] = 4
    relation_q["related_statement_ids"] = [PARENT_STATEMENT_ID]
    return updated


def build() -> tuple[dict[str, bytes], dict]:
    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    relations_path = TABLES / "relations.csv"
    enrichment_path = TABLES / "enrichment.jsonl"
    statements_path = TABLES / "book-statements.jsonl"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"

    manifest_fields, manifest = sync.read_csv(manifest_path)
    alignment_fields, alignments = sync.read_csv(alignment_path)
    relation_fields, relations = sync.read_csv(relations_path)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}

    assert candidate_by_id[CANDIDATE]["suggested_type"] == "work"
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_PATH.is_file(), f"prepare the reviewable card first: {CARD_REL}"
    card_text = read_text(CARD_PATH)
    assert f'name_en: "{NAME_EN}"' in card_text
    assert not any(row.get("type") == "work" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    candidate_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(candidate_rows) == 1
    target_alignment = candidate_rows[0]
    assert target_alignment["decision"] == "new" and not target_alignment.get("ku_id")
    assert current_group(target_alignment.get("resolution_note", "")) == GROUP
    group_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and current_group(row.get("resolution_note", "")) == GROUP
    ]
    assert group_members == [CANDIDATE], group_members

    statements = sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_ids = {row["statement_id"] for row in direct}
    relation_ids = {
        row["statement_id"] for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_ids == DIRECT_STATEMENT_IDS, (direct_ids, DIRECT_STATEMENT_IDS)
    assert relation_ids == RELATION_STATEMENT_IDS, (relation_ids, RELATION_STATEMENT_IDS)

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for quote in [
        "He commissioned a picture from Claude (a notoriously expensive artist) of A storm at sea, designed perhaps to illustrate his motto of contra ventos et undas",
        "The picture has been lost, but it is recorded in the Liber Veritatis, No. 33. It probably dates from 1638-9.",
    ]:
        assert " ".join(quote.split()) in source_text, quote

    statements_by_id = {row["statement_id"]: row for row in statements}
    parent_before = statements_by_id[PARENT_STATEMENT_ID]["qualifiers"]
    record_before = statements_by_id[RECORD_RELATION_STATEMENT_ID]["qualifiers"]
    assert not any(item.get("source_form") == "Rdthlisberger" for item in parent_before.get("ocr_corrections", []))
    assert not record_before.get("printed_page_locator") and not record_before.get("pdf_physical_page")
    assert not record_before.get("related_statement_ids")

    source_rows = [row for row in sync.read_csv(TABLES / "sources.csv")[1] if row.get("source_id") == SOURCE_ID]
    assert len(source_rows) == 1

    existing_enrichment = [
        json.loads(line)
        for line in read_text(enrichment_path).splitlines()
        if line.strip()
    ]
    assert not any(row.get("ku_id") == KU_ID for row in existing_enrichment)
    additions, source_registry, warnings, cards_with_tables = extract_records([{
        "ku_id": KU_ID,
        "card_path": CARD_REL,
    }])
    assert cards_with_tables == 1
    assert len(additions) == 4, len(additions)
    assert not warnings, warnings
    assert set(source_registry) == {SOURCE_ID}
    assert all(row.get("evidence_status") == "source_backed" and row.get("origin") == "book" for row in additions)
    assert all(row.get("source_ids") == [SOURCE_ID] for row in additions)

    existing_enrichment_ids = {row.get("enrichment_id", "") for row in existing_enrichment}
    existing_occurrences = {row.get("occurrence_id", "") for row in existing_enrichment}
    numeric_enrichment_ids = [
        int(match.group(1))
        for value in existing_enrichment_ids
        if (match := re.fullmatch(r"enr-(\d+)", value))
    ]
    next_enrichment_id = max(numeric_enrichment_ids, default=0) + 1
    for offset, row in enumerate(additions):
        row["enrichment_id"] = f"enr-{next_enrichment_id + offset:05d}"
        assert row["enrichment_id"] not in existing_enrichment_ids
        assert row["occurrence_id"] not in existing_occurrences
        existing_enrichment_ids.add(row["enrichment_id"])
        existing_occurrences.add(row["occurrence_id"])

    planned_alignment = add_alignment_mapping(alignments)
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_statements = add_statement_repairs(statements)

    source_types = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    manifest_by_id = {row["ku_id"]: row for row in planned_manifest}
    candidate_by_alignment = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    endpoints = {
        "cand-0428": "units/persons/paolo-giordano-ii-orsini",
        "cand-0767": "units/persons/claude-lorrain",
    }
    for candidate_id, ku_id in endpoints.items():
        alignment = candidate_by_alignment[candidate_id]
        assert alignment.get("ku_id") == ku_id and ku_id in manifest_by_id
    for candidate_id in ["cand-5557", "cand-5617"]:
        alignment = candidate_by_alignment[candidate_id]
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")

    relation_rows = list(relations)
    next_relation_id = max(
        (int(match.group(1)) for row in relations if (match := re.fullmatch(r"rel-(\d+)", row.get("relation_id", "")))),
        default=0,
    ) + 1
    new_relations = [
        {
            "relation_id": f"rel-{next_relation_id:04d}",
            "subject_ku_id": KU_ID,
            "object_ku_id": "units/persons/paolo-giordano-ii-orsini",
            "predicate": "commissioned_by",
            "time": "",
            "role": "委托人",
            "scope": "仅指 Haskell 所称的 A Storm at Sea；格言寓意另保留为待证候选。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "lines 29–30; print p.97",
            "source_file": SOURCE_FILE,
            "note": "Haskell 明言 Paolo 委托该画；不据此确认格言寓意或其他作品身份。",
        },
        {
            "relation_id": f"rel-{next_relation_id + 1:04d}",
            "subject_ku_id": KU_ID,
            "object_ku_id": "units/persons/claude-lorrain",
            "predicate": "created_by",
            "time": "",
            "role": "画家",
            "scope": "仅指 Haskell 所称的 A Storm at Sea；格言寓意另保留为待证候选。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "lines 29–30; print p.97",
            "source_file": SOURCE_FILE,
            "note": "Haskell 称 Paolo 委托 Claude 绘制该画；不把委托语境扩写为其他作者责任。",
        },
    ]
    allowed_predicates = set(source_types)
    natural_keys = {
        (row.get("subject_ku_id"), row.get("predicate"), row.get("object_ku_id"), row.get("time"), row.get("scope"))
        for row in relations
    }
    for row in new_relations:
        assert row["predicate"] in allowed_predicates
        spec = source_types[row["predicate"]]
        assert manifest_by_id[row["subject_ku_id"]]["type"] in spec["domain"]
        assert manifest_by_id[row["object_ku_id"]]["type"] in spec["range"]
        assert (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["scope"]) not in natural_keys
        natural_keys.add((row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["scope"]))
        assert row["source_id"] and row["source_span"] and row["source_file"]
    relation_rows.extend(new_relations)

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_text = insert_accepted(read_text(accepted_path))
    accepted_units_count = sum(1 for line in accepted_text.splitlines() if line.startswith("- 04-knowledge/units/"))

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {
        key: sum(item[key] for item in stats.values())
        for key in next(iter(stats.values()))
    }
    total_endpoint_groups, endpoint_candidates, endpoint_members, _ = endpoint_queue.summarize_relation_endpoint_queue(
        candidates, planned_alignment, planned_manifest, planned_statements
    )

    old_decisions = re.search(
        r"逐条裁决([\d,]+)/([\d,]+)条S2关系候选（([\d,]+) formal、([\d,]+) pending、([\d,]+) rejected）",
        read_text(RESULT_PATH),
    )
    assert old_decisions, "current S6 decision snapshot not found"
    base_decisions, total_decisions, base_formal, base_pending, base_rejected = [
        int(value.replace(",", "")) for value in old_decisions.groups()
    ]
    assert (base_decisions, total_decisions, base_formal, base_pending, base_rejected) == (203, 10402, 141, 53, 9)
    decisions_after = base_decisions + 4
    formal_after = base_formal + 2
    pending_after = base_pending + 2

    s2_count = sum(1 for row in statements if row.get("statement_id"))
    s3_counts = {
        "same": sum(item["same_candidates"] for item in stats.values()),
        "new": sum(item["new_candidates"] for item in stats.values()),
        "conflict": sum(item["conflict"] for item in stats.values()),
        "excluded": sum(item["excluded"] for item in stats.values()),
        "undecided": sum(item["undecided"] for item in stats.values()),
    }
    current_enrichment_count = len(existing_enrichment)
    current_unverified = sum(1 for row in existing_enrichment if row.get("evidence_status") == "unverified")
    planned_enrichment_count = current_enrichment_count + len(additions)
    relation_status_counts = {
        status: sum(1 for row in relation_rows if row.get("status") == status)
        for status in ["formal", "pending"]
    }

    # The shared helper expects a legacy "current status paragraph" that this
    # result document no longer contains. Refresh only the authoritative S4/S5/S6
    # bullets below, preserving the document's current structure and history.
    result_text = read_text(RESULT_PATH)
    snapshot_heading = result_text.index("## 当前全书阶段总览")
    snapshot_end = result_text.find("\n### ", snapshot_heading)
    if snapshot_end < 0:
        snapshot_end = len(result_text)
    snapshot = result_text[snapshot_heading:snapshot_end]
    direct_members = endpoint_members
    non_direct_groups = totals["pending_groups"] - total_endpoint_groups
    non_direct_members = totals["pending_members"] - direct_members
    s4_line = (
        f"- **S4：** 已登记{fmt(totals['registered_groups'])}/{fmt(totals['new_groups'])}组、"
        f"{fmt(totals['registered_members'])}/{fmt(totals['new_candidates'])}条候选映射；"
        f"待登记{fmt(totals['pending_groups'])}组／{fmt(totals['pending_members'])}条映射，"
        f"直接关系端点{fmt(total_endpoint_groups)}组／{fmt(direct_members)}条组成员映射，"
        f"非直接{fmt(non_direct_groups)}组／{fmt(non_direct_members)}条。"
    )
    s5_line = f"- **S5：** 字段表{fmt(planned_enrichment_count)}条，其中{fmt(current_unverified)}条为 `unverified`；未核字段按证据逐项处理。"
    s6_line = (
        f"- **S6：** 关系表{fmt(len(relation_rows))}条（{fmt(relation_status_counts['formal'])} formal、"
        f"{fmt(relation_status_counts['pending'])} pending）；过程记录累计逐条裁决"
        f"{fmt(decisions_after)}/{fmt(total_decisions)}条S2关系候选（{fmt(formal_after)} formal、"
        f"{fmt(pending_after)} pending、{fmt(base_rejected)} rejected），其余"
        f"{fmt(total_decisions - decisions_after)}条待逐项裁决。"
    )
    snapshot = replace_one(snapshot, r"^- \*\*S4：\*\*.*$", s4_line, "S4 current snapshot")
    snapshot = replace_one(snapshot, r"^- \*\*S5：\*\*.*$", s5_line, "S5 current snapshot")
    snapshot = replace_one(snapshot, r"^- \*\*S6：\*\*.*$", s6_line, "S6 current snapshot")
    result_text = result_text[:snapshot_heading] + snapshot + result_text[snapshot_end:]

    process_note = f"""
<a id="{ANCHOR}"></a>

### S4/S5/S6 work：Claude《A Storm at Sea》直接端点（2026-10-21）

沿用 S3 `new` 身份组 `{GROUP}`，将 `{CANDIDATE}` 登记为单成员 work KU [`{KU_ID}`](../../../{CARD_REL})。身份范围限于 Haskell 称 Paolo Giordano II 委托 Claude 绘制的《A Storm at Sea》；“或许”旨在说明格言、失佚、*Liber Veritatis* 第33号记录及1638–39可能年代均按 Haskell／其引文归属保留，未独立查阅该研究或图册。S5 从卡片提取4条书内 `source_backed` 字段（原文名称、作者转述的状态、可能年代、图册记录）；来源表无变化。

| S2 statement | S6 决定 | 关系／去向 |
|---|---|---|
| `st-chp4-sec-i-l26-33-claude-seascape` | formal | `{new_relations[0]['relation_id']}`：作品 `commissioned_by` Paolo Giordano II，证据限第4章 p.97 L29–30。 |
| `st-chp4-sec-i-l26-33-claude-authored-picture` | formal | `{new_relations[1]['relation_id']}`：作品 `created_by` Claude，证据限第4章 p.97 L29–30。 |
| `st-chp4-sec-i-l26-33-storm-motto-connection` | pending | Haskell 使用 “perhaps”，且格言 term 端点 `{candidate_by_alignment['cand-5557'].get('ku_id') or 'cand-5557 尚未 S4 登记'}`；保留来源推测，不建立正式边。 |
| `{RECORD_RELATION_STATEMENT_ID}` | pending | Haskell 注7转述该记录，但 `{candidate_by_alignment['cand-5617'].get('ku_id') or 'cand-5617 尚未 S4 登记'}`；具体图册条目未核，暂不建立正式边。 |

本批同时按第4章独立复核记录修复 S2 注7 `recorded_in` statement 的印刷页／PDF物理页锚及其与父statement的链接；父statement新增扫描校读 `Rdthlisberger` → `Röthlisberger`，保留原始转录。该修复不增加statement数或独立复核覆盖，也不表示第4章已接收。

批后 S4 已登记{fmt(totals['registered_groups'])}/{fmt(totals['new_groups'])}组、{fmt(totals['registered_members'])}/{fmt(totals['new_candidates'])}条映射；待登记{fmt(totals['pending_groups'])}组／{fmt(totals['pending_members'])}条，其中直接关系端点{fmt(total_endpoint_groups)}组／{fmt(direct_members)}条组成员映射。S5字段{fmt(planned_enrichment_count)}条（{fmt(current_unverified)}条 `unverified`）；S6累计逐条裁决{fmt(decisions_after)}/{fmt(total_decisions)}条（{fmt(formal_after)} formal、{fmt(pending_after)} pending、{fmt(base_rejected)} rejected），关系表{fmt(len(relation_rows))}条（{fmt(relation_status_counts['formal'])} formal、{fmt(relation_status_counts['pending'])} pending）。S2独立复核分子不变；S3决定不变。
""".strip()
    process_text = read_text(PROCESS_PATH)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.replace("# 全书 S3 身份对齐过程\n\n", "# 全书 S3 身份对齐过程\n\n" + process_note + "\n\n", 1)

    stages_note = f"""
<a id="{S2_REPAIR_ANCHOR}"></a>

### S2定向修复：A Storm at Sea 注7定位与校读（2026-10-21）

依第4章独立复核批次六、八的既有问题记录，修复 `{RECORD_RELATION_STATEMENT_ID}`：补印刷页 `p.97`、PDF物理页4，并关联复合父statement `{PARENT_STATEMENT_ID}`。父statement保留S0／original_quote原转录 `Rdthlisberger`，在 `ocr_corrections` 记录扫描页印作 `Röthlisberger`。本修订只补证据定位、statement关联与校读；statement/candidate/mention行数及S2独立复核覆盖不变，第4章仍未接收。
""".strip()
    stages_text = read_text(STAGES_PATH)
    assert f'<a id="{S2_REPAIR_ANCHOR}"></a>' not in stages_text
    stages_text = stages_text.rstrip() + "\n\n" + stages_note + "\n"

    batch_block = f"""### S4/S5/S6 work：Claude《A Storm at Sea》直接端点（2026-10-21）

登记既有 S3 新组 `{GROUP}` 的作品候选 `{CANDIDATE}`，新增4条 Haskell 书内 `source_backed` 字段。四条直接关系候选逐条裁决为2 formal、2 pending：正式边为作品 `commissioned_by` Paolo Giordano II 与 `created_by` Claude；格言关系因原文仅为“perhaps”且 term 端点未登记而待证；*Liber Veritatis* 第33号记录关系因端点未登记且图册未核而待证。第4章注7 `recorded_in` statement 的页锚、父statement链接及 Röthlisberger OCR校读一并修复；不增加S2覆盖计数，不表示第4章接收。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。批后 S4 {fmt(totals['registered_groups'])}/{fmt(totals['new_groups'])}组、{fmt(totals['registered_members'])}/{fmt(totals['new_candidates'])}条映射；S5 {fmt(planned_enrichment_count)}条（{fmt(current_unverified)}条 `unverified`）；S6 {fmt(decisions_after)}/{fmt(total_decisions)}条（{fmt(formal_after)} formal、{fmt(pending_after)} pending、{fmt(base_rejected)} rejected），关系表 {fmt(len(relation_rows))}条（{fmt(relation_status_counts['formal'])} formal、{fmt(relation_status_counts['pending'])} pending）。

"""
    result_text = result_text.replace("更新日期：2026-10-21。\n\n", "更新日期：2026-10-21。\n\n" + batch_block, 1)

    agents_text = read_text(AGENTS_PATH)
    s4_agents = (
        f"S4已登记{fmt(totals['registered_groups'])}/{fmt(totals['new_groups'])}组、"
        f"{fmt(totals['registered_members'])}/{fmt(totals['new_candidates'])}条候选映射；"
        f"待登记{fmt(totals['pending_groups'])}组／{fmt(totals['pending_members'])}条映射，其中直接关系端点"
        f"{fmt(total_endpoint_groups)}组／{fmt(direct_members)}条组成员映射，非直接映射"
        f"{fmt(non_direct_groups)}组／{fmt(non_direct_members)}条。"
    )
    agents_text = replace_one(
        agents_text,
        r"S4已\s*登记[\d,]+/[\d,]+组、[\d,]+/[\d,]+条候选映射；待登记[\d,]+组／[\d,]+条映射，其中直接关系端点[\d,]+组／[\d,]+条组成员映射，非直接映射[\d,]+组／[\d,]+条。",
        s4_agents,
        "S4 snapshot in AGENTS.md",
    )
    agents_text = replace_one(
        agents_text,
        r"S5字段表[\d,]+条、其中[\d,]+条unverified",
        f"S5字段表{fmt(planned_enrichment_count)}条、其中{fmt(current_unverified)}条unverified",
        "S5 snapshot in AGENTS.md",
    )
    s6_agents = (
        f"S6关系表{fmt(len(relation_rows))}条（{fmt(relation_status_counts['formal'])} formal、"
        f"{fmt(relation_status_counts['pending'])} pending），过程记录累计逐条裁决"
        f"{fmt(decisions_after)}/{fmt(total_decisions)}条S2关系候选（{fmt(formal_after)} formal、"
        f"{fmt(pending_after)} pending、{fmt(base_rejected)} rejected）；其余"
        f"{fmt(total_decisions - decisions_after)}条待逐项裁决"
    )
    agents_text = replace_one(
        agents_text,
        r"S6关系表[\d,]+条（[\d,]+ formal、[\d,]+ pending），过程记录累计逐条裁决[\d,]+/[\d,]+条S2关系候选（[\d,]+ formal、[\d,]+ pending、[\d,]+ rejected）；其余[\d,]+条待逐项裁决",
        s6_agents,
        "S6 snapshot in AGENTS.md",
    )

    planned_enrichment = existing_enrichment + additions
    planned_bytes = {
        manifest_path: csv_bytes_like(manifest_path, manifest_fields, planned_manifest),
        alignment_path: csv_bytes_like(alignment_path, alignment_fields, planned_alignment),
        relations_path: csv_bytes_like(relations_path, relation_fields, relation_rows),
        enrichment_path: jsonl_patch_bytes(enrichment_path, additions=additions),
        statements_path: jsonl_patch_bytes(
            statements_path,
            replacements={
                row["statement_id"]: row
                for row in planned_statements
                if row["statement_id"] in {PARENT_STATEMENT_ID, RECORD_RELATION_STATEMENT_ID}
            },
        ),
        accepted_path: encode_text_like(accepted_path, accepted_text),
        PROCESS_PATH: encode_text_like(PROCESS_PATH, process_text),
        STAGES_PATH: encode_text_like(STAGES_PATH, stages_text),
        RESULT_PATH: encode_text_like(RESULT_PATH, result_text),
        AGENTS_PATH: encode_text_like(AGENTS_PATH, agents_text),
    }
    summary = {
        "candidate": CANDIDATE,
        "ku_id": KU_ID,
        "relations_added": [row["relation_id"] for row in new_relations],
        "enrichment_added": len(additions),
        "enrichment_total": planned_enrichment_count,
        "enrichment_unverified": current_unverified,
        "s4_registered_groups": totals["registered_groups"],
        "s4_registered_members": totals["registered_members"],
        "s4_pending_groups": totals["pending_groups"],
        "s4_pending_members": totals["pending_members"],
        "direct_endpoint_groups": total_endpoint_groups,
        "direct_endpoint_candidates": endpoint_candidates,
        "direct_endpoint_members": direct_members,
        "s6_decisions": decisions_after,
        "s6_total": total_decisions,
        "s6_formal": formal_after,
        "s6_pending": pending_after,
        "s6_rejected": base_rejected,
        "relation_table_rows": len(relation_rows),
        "relation_table_formal": relation_status_counts["formal"],
        "relation_table_pending": relation_status_counts["pending"],
        "accepted_units": accepted_units_count,
        "s2_statements": s2_count,
        "s3_counts": s3_counts,
        "files": [str(path.relative_to(ROOT)) for path in planned_bytes],
        "bytes": planned_bytes,
    }
    return planned_bytes, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Register and adjudicate the A Storm at Sea direct S4/S6 endpoint batch.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    planned, summary = build()
    print("preflight passed")
    print(json.dumps({key: value for key, value in summary.items() if key not in {"bytes", "files"}}, ensure_ascii=False, indent=2))
    print("files:")
    for path in summary["files"]:
        print(f"- {path}")
    if args.dry_run:
        return 0

    for path, payload in planned.items():
        atomic_write(path, payload)
    print("applied atomically per file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
