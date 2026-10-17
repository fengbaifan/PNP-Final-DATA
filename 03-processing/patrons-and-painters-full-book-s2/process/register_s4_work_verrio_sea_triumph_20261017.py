from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.build_field_facts import ENRICHMENT, SOURCES, assign_ids, extract_records, read_frontmatter

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST = TABLES / "ku-manifest.csv"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
CARD_PATH = "04-knowledge/units/works/verrio-earliest-royal-picture-a-sea-triumph.md"
CARD = ROOT / CARD_PATH
ANCHOR = '<a id="s4-work-verrio-sea-triumph-20261017"></a>'
KU_ID = "units/works/verrio-earliest-royal-picture-a-sea-triumph"
CANONICAL_NAME = "《海上凯旋》（A Sea triumph; exact object unidentified）"
NAME_EN = "A Sea triumph; exact object unidentified"
GROUP = "workgrp-b43402f3260265"
CANDIDATE_IDS = ["cand-2762", "cand-7206"]
DIRECT_STATEMENTS = [
    "st-chp7-p195-sea-triumph-open",
    "st-chp7-p196-sea-triumph-description",
]
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
SOURCE_QUOTES = [
    "His earliest royal picture—A Sea triumph, being",
    "a large piece with King Charles II in it—was flattering if hardly very relevant to Charles’s rule so far",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    import io

    old = path.read_bytes()
    newline = "\r\n" if b"\r\n" in old else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b"") + output.getvalue().encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    newline = "\r\n" if b"\r\n" in old else "\n"
    if newline == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    return (b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b"") + text.encode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one exact match, found {count}")
    return text.replace(old, new, 1)


def group_of(row: dict[str, str]) -> str:
    match = re.search(r"(?:^|[;；\s])group=([^;；\s]+)", row.get("resolution_note", ""))
    return match.group(1) if match else ""


def s4_counts(rows: list[dict[str, str]], candidate_types: dict[str, str]) -> dict[str, tuple[int, int, int, int]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        if row.get("decision") != "new" or row.get("external_source"):
            continue
        group = group_of(row)
        kind = candidate_types.get(row.get("candidate_id", ""), "")
        if not group or not kind:
            raise ValueError(f"new decision lacks group or type: {row.get('candidate_id')}")
        groups.setdefault((kind, group), []).append(row)
    out: dict[str, list[int]] = {}
    for (kind, group), members in groups.items():
        counts = out.setdefault(kind, [0, 0, 0, 0])
        mapped = {member.get("ku_id", "") for member in members}
        if mapped == {""}:
            counts[2] += 1
            counts[3] += len(members)
        elif len(mapped) == 1 and "" not in mapped:
            counts[0] += 1
            counts[1] += len(members)
        else:
            raise ValueError(f"partial or split S4 identity group {group}: {sorted(mapped)}")
    return {kind: tuple(counts) for kind, counts in out.items()}


def total_counts(counts: dict[str, tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    return tuple(sum(row[index] for row in counts.values()) for index in range(4))


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the two-candidate S3 identity group for Verrio's A Sea triumph.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not CARD.is_file():
        raise ValueError(f"target card is missing: {CARD_PATH}")
    frontmatter = read_frontmatter(CARD.read_text(encoding="utf-8-sig"))
    if frontmatter.get("type") != "work" or frontmatter.get("title") != CANONICAL_NAME or frontmatter.get("name_en") != NAME_EN:
        raise ValueError("target card type/name does not match registration")
    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    if any(quote not in source_text for quote in SOURCE_QUOTES):
        raise ValueError("source quote mismatch")

    manifest_fields, manifest_rows = read_csv(MANIFEST)
    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    _, candidate_rows = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    candidate_types = {row["candidate_id"]: row["suggested_type"] for row in candidate_rows}
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    if (len(manifest_rows), len(alignment_rows), len(candidate_by_id), len(alignment_by_candidate)) != (1746, 12645, 12407, 12407):
        raise ValueError("unexpected baseline counts")
    before = s4_counts(alignment_rows, candidate_types)
    if before.get("work") != (48, 53, 434, 444) or total_counts(before) != (727, 897, 4054, 4069):
        raise ValueError(f"unexpected S4 baseline: work={before.get('work')}, total={total_counts(before)}")
    if any(candidate_types.get(cid) != "work" for cid in CANDIDATE_IDS):
        raise ValueError("target candidates are no longer both work candidates")
    group_members = [row for row in alignment_rows if row.get("decision") == "new" and not row.get("external_source") and group_of(row) == GROUP]
    if sorted(row.get("candidate_id", "") for row in group_members) != sorted(CANDIDATE_IDS):
        raise ValueError(f"S3 group membership changed: {[row.get('candidate_id') for row in group_members]}")
    if any(row.get("ku_id") for row in group_members):
        raise ValueError("S3 group is already wholly or partially mapped")
    if KU_ID in {row["ku_id"] for row in manifest_rows} or CARD_PATH in {row["card_path"] for row in manifest_rows}:
        raise ValueError("target KU or card path already exists in manifest")
    if not all(cid in alignment_by_candidate for cid in CANDIDATE_IDS):
        raise ValueError("a candidate mapping row is missing")
    if any(alignment_by_candidate[cid].get("decision") != "new" for cid in CANDIDATE_IDS):
        raise ValueError("a target candidate is no longer S3 new")

    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        statements = {row["statement_id"]: row for row in (json.loads(line) for line in handle if line.strip())}
    first, second = [statements.get(sid) for sid in DIRECT_STATEMENTS]
    if (not first or first.get("qualifiers", {}).get("relation_candidate") is not True
            or first.get("object_candidate_id") != "cand-7206"):
        raise ValueError(f"work identity statement changed: {DIRECT_STATEMENTS[0]}")
    if (not second or second.get("qualifiers", {}).get("relation_candidate") is not True
            or second.get("subject_candidate_id") != "cand-7206"):
        raise ValueError(f"work depiction statement changed: {DIRECT_STATEMENTS[1]}")
    for endpoint in ("cand-2759", "cand-0656"):
        row = alignment_by_candidate.get(endpoint)
        if not row or not row.get("ku_id"):
            raise ValueError(f"expected existing endpoint KU missing: {endpoint}")

    new_manifest = {
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": CANONICAL_NAME,
        "name_en": NAME_EN,
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_PATH,
    }
    field_records, source_registry, field_warnings, cards_with_tables = extract_records([new_manifest])
    assign_ids(field_records, ENRICHMENT)
    if cards_with_tables != 1 or len(field_records) != 6 or field_warnings:
        raise ValueError(f"field extraction mismatch: cards={cards_with_tables}, rows={len(field_records)}, warnings={field_warnings}")
    if any(row.get("evidence_status") != "source_backed" or row.get("source_ids") != ["haskell-1980-rev-ed"] for row in field_records):
        raise ValueError("all target fields must be source-backed by Haskell")
    if set(source_registry) != {"haskell-1980-rev-ed"}:
        raise ValueError(f"unexpected source registry IDs: {sorted(source_registry)}")
    with SOURCES.open(encoding="utf-8-sig", newline="") as handle:
        existing_sources = {row["source_id"] for row in csv.DictReader(handle)}
    if not set(source_registry).issubset(existing_sources):
        raise ValueError("target fields require a new source registry entry")
    old_enrichment = [json.loads(line) for line in ENRICHMENT.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    old_ids = {row.get("enrichment_id") for row in old_enrichment}
    old_occurrences = {row.get("occurrence_id") for row in old_enrichment}
    if any(row["enrichment_id"] in old_ids or row["occurrence_id"] in old_occurrences for row in field_records):
        raise ValueError("target enrichment ID or occurrence already exists")

    for cid in CANDIDATE_IDS:
        row = alignment_by_candidate[cid]
        row["ku_id"] = KU_ID
        row["process_ref"] = "S3-S4-full-book-2026-10-17"
        row["resolution_note"] += f"; S4 registration: mapped {GROUP} to {KU_ID}"
    after = s4_counts(alignment_rows, candidate_types)
    after_total = total_counts(after)
    if after.get("work") != (49, 55, 433, 442) or after_total != (728, 899, 4053, 4067):
        raise ValueError(f"unexpected post-registration counts: work={after.get('work')}; total={after_total}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge,
        "| work | 2,397 | 234 | 482 / 497 | 5 | 29 | 1,632 | 48 / 53 | 434 / 444 |",
        "| work | 2,397 | 234 | 482 / 497 | 5 | 29 | 1,632 | 49 / 55 | 433 / 442 |", "process work row")
    knowledge = replace_once(knowledge,
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **727 / 897** | **4,054 / 4,069** |",
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **728 / 899** | **4,053 / 4,067** |", "process total row")
    if ANCHOR in knowledge:
        raise ValueError("process anchor already exists")
    enrichment_ids = [row["enrichment_id"] for row in field_records]
    knowledge += "\n".join([
        "", ANCHOR, "", "### S4 work：Verrio《A Sea triumph》描述性身份组登记（2026-10-17）", "",
        "- S3 身份组 `workgrp-b43402f3260265` 将索引简称候选 `cand-2762` 与正文候选 `cand-7206` 合并为一个 work KU。索引子目指向 pp.195–196 的 Verrio 王室绘画；正文称其为最早的王室绘画、“A Sea triumph”。此名称作为描述性工作题名，原文没有确认正式题名或具体作品身份。",
        "- 第195页句子在第196页续完；Haskell 称画中有 Charles II，并评价该画奉承国王但与其统治实际关联有限。该评价保留为 Haskell 的判断；媒介、尺寸、地点、委托与存世情况未由此处确定。Antonio Verrio 与 Charles II 已各有对应人物 KU。",
        f"- 六条字段记录（{enrichment_ids[0]}–{enrichment_ids[-1]}）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。",
        f"- `st-chp7-p195-sea-triumph-open` 与 `st-chp7-p196-sea-triumph-description` 两条关系候选保留待 S6；不在本轮登记正式创作者或描绘对象关系。`relations.csv` 未改动。",
        "- 登记后 work 类型为49组／55条候选映射已登记、433组／442条待登记；全书累计728组／899条已登记、4,053组／4,067条待登记；KU=1,747，enrichment=10,775。",
    ]) + "\n"

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result,
        "S4 已登记727组、映射897条成员候选；尚待登记4,054组、4,069条映射。",
        "S4 已登记728组、映射899条成员候选；尚待登记4,053组、4,067条映射。", "result S4 totals")
    result = replace_once(result, "| [KU 登记](../tables/ku-manifest.csv) | 1,746 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,747 KU；", "result KU count")
    result = replace_once(result, "| [既有字段表](../tables/enrichment.jsonl) | 10,769条", "| [既有字段表](../tables/enrichment.jsonl) | 10,775条", "result field count")
    result = replace_once(result, "| work | 234→218 | 497／482 | 48／434；444 | 5 | 29 | 1,632 |", "| work | 234→218 | 497／482 | 49／433；442 | 5 | 29 | 1,632 |", "result work row")
    result = replace_once(result, "| **合计** | **1,893→1,040** | **4,966／4,781** | **727／4,054；4,069** | **8** | **100** | **5,440** |", "| **合计** | **1,893→1,040** | **4,966／4,781** | **728／4,053；4,067** | **8** | **100** | **5,440** |", "result total row")
    result += (
        "\n\n### S4 work：Verrio《A Sea triumph》描述性身份组（2026-10-17）\n\n"
        "索引候选 `cand-2762` 与正文候选 `cand-7206` 已映射至一个 work KU；“A Sea triumph”仅作为描述性工作题名，具体作品身份及正式题名未确认。"
        "六条 source_backed 字段记录 Haskell 第7章 pp.195–196 的称谓与画面描述。两条直接关系候选留待 S6，未新增正式关系。"
        "本批后 KU=1,747、enrichment=10,775；S4 已登记728组／899条，待登记4,053组／4,067条。"
    )

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    if CARD_PATH in {line[2:].strip() for line in accepted.splitlines() if line.startswith("- ")}:
        raise ValueError("card is already in accepted.yml")
    accepted_lines = accepted.splitlines(keepends=True)
    accepted_newline = "\r\n" if any(line.endswith("\r\n") for line in accepted_lines) else "\n"
    insert_at = next((i for i, line in enumerate(accepted_lines) if line.startswith("- ") and line[2:].strip() > CARD_PATH), len(accepted_lines))
    accepted_lines.insert(insert_at, f"- {CARD_PATH}{accepted_newline}")
    accepted = "".join(accepted_lines)

    old_jsonl = ENRICHMENT.read_bytes()
    if old_jsonl and not old_jsonl.endswith(b"\n"):
        raise ValueError("enrichment JSONL lacks final newline")
    new_jsonl = old_jsonl + "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in field_records).encode("utf-8")
    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "identity_group": GROUP,
        "candidate_mappings": {cid: KU_ID for cid in CANDIDATE_IDS},
        "new_kus": 1,
        "direct_s2_relation_candidates_pending_s6": DIRECT_STATEMENTS,
        "field_records": len(field_records),
        "enrichment_ids": enrichment_ids,
        "source_ids": sorted(source_registry),
        "field_warnings": field_warnings,
        "sources_csv_changes": 0,
        "relations_csv_changes": 0,
        "counts_after": {"kus": len(manifest_rows) + 1, "enrichment": len(old_enrichment) + len(field_records), "work_s4": after["work"], "all_s4": after_total},
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return 0

    manifest_rows.append(new_manifest)
    MANIFEST.write_bytes(csv_bytes(MANIFEST, manifest_fields, manifest_rows))
    ALIGNMENT.write_bytes(csv_bytes(ALIGNMENT, alignment_fields, alignment_rows))
    ACCEPTED.write_bytes(text_bytes(ACCEPTED, accepted))
    KNOWLEDGE.write_bytes(text_bytes(KNOWLEDGE, knowledge))
    RESULT.write_bytes(text_bytes(RESULT, result))
    ENRICHMENT.write_bytes(new_jsonl)
    print("applied: one work KU for the two-member S3 group; both direct relation candidates remain pending S6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
