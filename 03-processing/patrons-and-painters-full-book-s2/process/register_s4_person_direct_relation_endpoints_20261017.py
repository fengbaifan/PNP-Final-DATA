from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.build_field_facts import ENRICHMENT, SOURCES, assign_ids, extract_records, write_jsonl

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST = TABLES / "ku-manifest.csv"
ALIGNMENT = TABLES / "alignment.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-relation-endpoints-20261017"
PROCESS_ANCHOR = '<a id="s4-person-direct-relation-endpoints-20261017"></a>'

REGISTRATIONS = [
    {
        "candidate_id": "cand-2531",
        "group": "new-person:benjamin-styles-96734d9ba8",
        "ku_id": "units/persons/benjamin-styles",
        "type": "person",
        "canonical_name": "本杰明·斯泰尔斯（Benjamin Styles）",
        "name_en": "Benjamin Styles",
        "card_path": "04-knowledge/units/persons/benjamin-styles.md",
        "statement_ids": [
            "st-chp10-p286-moor-park-built",
            "st-chp10-p286-moor-park-decoration-open",
            "st-chp10-p286-styles-south-sea-fortune",
        ],
    },
    {
        "candidate_id": "cand-2204",
        "group": "new-person:lazzaro-riviera-b4050e50ae",
        "ku_id": "units/persons/lazzaro-riviera",
        "type": "person",
        "canonical_name": "拉扎罗·里维埃拉（Lazzaro Riviera）",
        "name_en": "Lazzaro Riviera",
        "card_path": "04-knowledge/units/persons/lazzaro-riviera.md",
        "statement_ids": [
            "st-chp10-p326-riviera-commission",
            "st-chp10-p326-riviera-issued-explanatory-pamphlet",
            "st-chp10-p327-n03-riviera-pamphlets-attributed",
        ],
    },
    {
        "candidate_id": "cand-0805",
        "group": "new-person:anna-colonna-22071d55fd",
        "ku_id": "units/persons/anna-colonna",
        "type": "person",
        "canonical_name": "安娜·科隆纳（Anna Colonna）",
        "name_en": "Anna Colonna",
        "card_path": "04-knowledge/units/persons/anna-colonna.md",
        "statement_ids": [
            "st-chp2-sec-ii-l10-18-anna-colonna-bride-selection",
            "st-chp2-sec-ii-l10-18-anna-colonna-parentage",
            "st-chp2-sec-ii-l3-8-taddeo-fortunes",
        ],
    },
]

KNOWLEDGE_OLD_PERSON_ROW = "| person | 3,464 | 1,082 | 1,069 / 1,156 | 3 | 7 | 1,216 | 313 / 399 | 756 / 757 |"
KNOWLEDGE_NEW_PERSON_ROW = "| person | 3,464 | 1,082 | 1,069 / 1,156 | 3 | 7 | 1,216 | 316 / 402 | 753 / 754 |"
KNOWLEDGE_OLD_TOTAL_ROW = "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **708 / 872** | **4,073 / 4,094** |"
KNOWLEDGE_NEW_TOTAL_ROW = "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **711 / 875** | **4,070 / 4,091** |"

RESULT_OLD_TABLE = """| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |
|---|---:|---:|---:|---:|---:|---:|
| archive | 89→62 | 1,250／1,204 | 100／1,104；1,114 | 0 | 18 | 743 |
| event | 7→7 | 235／231 | 34／197；197 | 0 | 0 | 115 |
| family | 22→16 | 94／88 | 88／0；0 | 0 | 1 | 18 |
| institution | 180→141 | 196／193 | 20／173；173 | 0 | 0 | 121 |
| person | 1,082→398 | 1,156／1,069 | 313／756；757 | 3 | 7 | 1,216 |
| place | 225→153 | 568／560 | 40／520；520 | 0 | 0 | 316 |
| procedure | 10→10 | 31／29 | 29／0；0 | 0 | 0 | 2 |
| term | 43→35 | 940／928 | 35／893；893 | 0 | 2 | 655 |
| work | 234→218 | 497／482 | 48／434；444 | 5 | 29 | 1,632 |
| 未分类 | 0→0 | 0／0 | 0／0；0 | 0 | 43 | 622 |
| **合计** | **1,892→1,040** | **4,967／4,784** | **707／4,077；4,098** | **8** | **100** | **5,440** |"""
RESULT_NEW_TABLE = """| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |
|---|---:|---:|---:|---:|---:|---:|
| archive | 89→62 | 1,250／1,204 | 100／1,104；1,114 | 0 | 18 | 743 |
| event | 7→7 | 235／231 | 34／197；197 | 0 | 0 | 115 |
| family | 22→16 | 94／88 | 88／0；0 | 0 | 1 | 18 |
| institution | 180→141 | 196／191 | 21／170；170 | 0 | 0 | 121 |
| person | 1,082→398 | 1,156／1,069 | 316／753；754 | 3 | 7 | 1,216 |
| place | 226→153 | 567／559 | 40／519；519 | 0 | 0 | 316 |
| procedure | 10→10 | 31／29 | 29／0；0 | 0 | 0 | 2 |
| term | 43→35 | 940／928 | 35／893；893 | 0 | 2 | 655 |
| work | 234→218 | 497／482 | 48／434；444 | 5 | 29 | 1,632 |
| 未分类 | 0→0 | 0／0 | 0／0；0 | 0 | 43 | 622 |
| **合计** | **1,893→1,040** | **4,966／4,781** | **711／4,070；4,091** | **8** | **100** | **5,440** |"""


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    existing = path.read_bytes()
    has_bom = existing.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in existing else "\n"
    import io

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if has_bom else b"") + payload


def text_bytes(path: Path, text: str) -> bytes:
    existing = path.read_bytes() if path.exists() else b""
    has_bom = existing.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in existing else "\n"
    if newline == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    return (b"\xef\xbb\xbf" if has_bom else b"") + text.encode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one exact match, found {count}")
    return text.replace(old, new, 1)


def insert_accepted_paths(text: str, paths: list[str]) -> str:
    lines = text.splitlines(keepends=True)
    normalized = [line[2:].strip() for line in lines if line.startswith("- ")]
    if not any(line.strip() == "units:" for line in lines):
        raise ValueError("accepted.yml has no units root")
    additions = sorted(set(paths) - set(normalized))
    if len(additions) != len(paths):
        raise ValueError("an accepted path already exists")
    newline = "\r\n" if any(line.endswith("\r\n") for line in lines) else "\n"
    for path in additions:
        insert_at = next(
            (index for index, line in enumerate(lines) if line.startswith("- ") and line[2:].strip() > path),
            len(lines),
        )
        lines.insert(insert_at, f"- {path}{newline}")
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register reviewed person identity groups that are S2 direct relation endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest_rows = read_csv(MANIFEST)
    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    if len(manifest_rows) != 1727 or len(alignment_rows) != 12645:
        raise ValueError(f"unexpected starting counts: manifest={len(manifest_rows)} alignment={len(alignment_rows)}")
    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    alignment_by_candidate = {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    if len(alignment_by_candidate) != 12407:
        raise ValueError(f"expected 12407 candidate decisions, got {len(alignment_by_candidate)}")

    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        statements = {row["statement_id"]: row for row in (json.loads(line) for line in handle if line.strip())}
    if len({record["ku_id"] for record in REGISTRATIONS}) != len(REGISTRATIONS):
        raise ValueError("duplicate KU IDs in this batch")

    new_manifest_rows: list[dict[str, str]] = []
    touched_alignment_ids: set[str] = set()
    for record in REGISTRATIONS:
        if record["ku_id"] in manifest_by_id:
            raise ValueError(f"KU already exists: {record['ku_id']}")
        card = ROOT / record["card_path"]
        if not card.is_file():
            raise ValueError(f"reviewed card is missing: {record['card_path']}")
        if record["card_path"] in {row["card_path"] for row in manifest_rows}:
            raise ValueError(f"card path already in manifest: {record['card_path']}")
        row = alignment_by_candidate.get(record["candidate_id"])
        if not row or row.get("decision") != "new" or row.get("ku_id"):
            raise ValueError(f"candidate is not an unmapped S3 new decision: {record['candidate_id']}")
        if f"group={record['group']}" not in row.get("resolution_note", ""):
            raise ValueError(f"alignment group mismatch: {record['candidate_id']}")
        if row["alignment_id"] in touched_alignment_ids:
            raise ValueError(f"duplicate alignment row: {row['alignment_id']}")
        touched_alignment_ids.add(row["alignment_id"])
        new_manifest_rows.append({
            "ku_id": record["ku_id"],
            "type": record["type"],
            "canonical_name": record["canonical_name"],
            "name_en": record["name_en"],
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": record["card_path"],
        })
        for statement_id in record["statement_ids"]:
            statement = statements.get(statement_id)
            if (
                not statement
                or not statement.get("qualifiers", {}).get("relation_candidate")
                or record["candidate_id"] not in (
                    statement.get("subject_candidate_id"),
                    statement.get("object_candidate_id"),
                )
            ):
                raise ValueError(f"candidate is not a direct endpoint of expected S2 relation candidate: {statement_id}")

    field_records, source_registry, field_warnings, cards_with_tables = extract_records(new_manifest_rows)
    assign_ids(field_records, ENRICHMENT)
    if field_warnings or cards_with_tables != 3 or len(field_records) != 9:
        raise ValueError(
            f"field extraction mismatch: cards={cards_with_tables}, rows={len(field_records)}, warnings={field_warnings}"
        )
    if any(row.get("evidence_status") != "source_backed" for row in field_records):
        raise ValueError("all nine table rows must map to source-backed Haskell evidence")
    if set(source_registry) != {"haskell-1980-rev-ed"}:
        raise ValueError(f"unexpected field source IDs: {sorted(source_registry)}")
    with SOURCES.open(encoding="utf-8-sig", newline="") as handle:
        registered_sources = {row["source_id"] for row in csv.DictReader(handle)}
    if not set(source_registry).issubset(registered_sources):
        raise ValueError("a new source-registry entry would be required; keep it out of this targeted batch")
    old_enrichment = [
        json.loads(line)
        for line in ENRICHMENT.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    old_enrichment_ids = {row.get("enrichment_id") for row in old_enrichment}
    old_occurrences = {row.get("occurrence_id") for row in old_enrichment}
    if any(row["enrichment_id"] in old_enrichment_ids for row in field_records):
        raise ValueError("an extracted enrichment ID already exists")
    if any(row["occurrence_id"] in old_occurrences for row in field_records):
        raise ValueError("an extracted enrichment occurrence already exists")

    alignment_updates = []
    for record in REGISTRATIONS:
        row = alignment_by_candidate[record["candidate_id"]]
        row["ku_id"] = record["ku_id"]
        row["process_ref"] = "S3-S4-full-book-2026-10-17"
        row["resolution_note"] = row["resolution_note"] + f"; S4 registration: mapped {record['group']} to {record['ku_id']}"
        alignment_updates.append((record["candidate_id"], record["ku_id"]))

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge, KNOWLEDGE_OLD_PERSON_ROW, KNOWLEDGE_NEW_PERSON_ROW, "knowledge person row")
    knowledge = replace_once(knowledge, KNOWLEDGE_OLD_TOTAL_ROW, KNOWLEDGE_NEW_TOTAL_ROW, "knowledge total row")
    if PROCESS_ANCHOR in knowledge:
        raise ValueError("process anchor already exists")
    enrichment_ids = [row["enrichment_id"] for row in field_records]
    detail_lines = [
        "",
        PROCESS_ANCHOR,
        "",
        "### S4 person：三组直接关系端点身份组登记（2026-10-17）",
        "",
        "- 按 S3 已裁为 new 的身份组登记，每组一个 person KU；中文标题为编辑性音译，英文规范名保留候选与书内索引／正文形式。本批未查询外部身份来源。",
        "- new-person:benjamin-styles-96734d9ba8（cand-2531）登记至[Benjamin Styles 人物卡](../../../04-knowledge/units/persons/benjamin-styles.md)。Haskell 正文称 Mr Styles，索引列 Styles, Benjamin；卡片保留此差别，不补写外部身份。Moor Park 建造阶段未分定。",
        "- new-person:lazzaro-riviera-b4050e50ae（cand-2204）登记至[Lazzaro Riviera 人物卡](../../../04-knowledge/units/persons/lazzaro-riviera.md)。仅记录 Haskell 关于 Boscarati 四幅寓意画及 La Educazione Virile 小册子的委托／出版归属；小册子未独立查阅。",
        "- new-person:anna-colonna-22071d55fd（cand-0805）登记至[Anna Colonna 人物卡](../../../04-knowledge/units/persons/anna-colonna.md)。原书称她被选作 Don Taddeo 的新娘，不据此断言婚礼完成；Contestabile 仅为原文称谓，未识别其个人身份。",
        "- 三组各有3条直接 S2 关系候选作为端点，共9条；人物端点现已映射，但关系仍留待 S6。本批未增加 relations.csv 正式边。",
        f"- 三张卡的九条姓名、身份、委托、出版、婚姻选择及亲缘字段由 build_field_facts.extract_records 逐卡提取并写入既有 Haskell 来源字段；enrichment IDs：{', '.join(enrichment_ids)}。来源登记表未改动。",
        "- 登记后 person 类型：316组／402条候选映射已登记，753组／754条映射待登记；全书 S4 累计711组／875条候选映射已登记，4,070组／4,091条映射待登记；KU=1,730。",
        "",
    ]
    knowledge += "\n".join(detail_lines)

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(
        result,
        "S4 已登记708组、映射872条成员候选；尚待登记4,073组、4,094条映射。",
        "S4 已登记711组、映射875条成员候选；尚待登记4,070组、4,091条映射。",
        "result current S4 totals",
    )
    result = replace_once(result, "| [KU 登记](../tables/ku-manifest.csv) | 1,727 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,730 KU；", "result KU count")
    result = replace_once(result, "| [既有字段表](../tables/enrichment.jsonl) | 10,677条", "| [既有字段表](../tables/enrichment.jsonl) | 10,686条", "result enrichment count")
    result = replace_once(result, RESULT_OLD_TABLE, RESULT_NEW_TABLE, "result S4 type table")
    if PROCESS_ANCHOR in result:
        raise ValueError("result process anchor already exists")
    result += "\n\n### S4 person：三组直接关系端点身份组登记（2026-10-17）\n\n"
    result += (
        "S3 已裁为 new 的人物组 new-person:benjamin-styles-96734d9ba8（cand-2531）、"
        "new-person:lazzaro-riviera-b4050e50ae（cand-2204）和 "
        "new-person:anna-colonna-22071d55fd（cand-0805）各登记为一张 KU；"
        "对齐表已逐一写入 KU 映射，三张卡均含双语名称与等值描述、书内原文来源及姓名／类型字段。"
        f"九条字段记录为{', '.join(enrichment_ids)}，均 source_backed、复用既有 Haskell 来源。"
        "三人各自的3条直接 S2 关系候选仍待 S6，本批没有新增正式关系；sources.csv 未改动。"
        "本批后 S4 已登记711组／875条候选映射，待登记4,070组／4,091条映射；KU=1,730，字段=10,686。"
    )

    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "candidate_mappings": alignment_updates,
        "new_manifest_rows": new_manifest_rows,
        "direct_relation_candidate_endpoints": sum(len(item["statement_ids"]) for item in REGISTRATIONS),
        "field_records": len(field_records),
        "enrichment_ids": enrichment_ids,
        "field_source_ids": sorted(source_registry),
        "field_warnings": field_warnings,
        "sources_csv_changes": 0,
        "relations_csv_changes": 0,
        "post_apply": {
            "kus": len(manifest_rows) + len(new_manifest_rows),
            "registered_groups": "711",
            "registered_candidate_mappings": "875",
            "pending_groups": "4070",
            "pending_candidate_mappings": "4091",
            "enrichment_rows": len(old_enrichment) + len(field_records),
        },
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    for row in field_records:
        print(json.dumps(row, ensure_ascii=False))
    if not args.apply:
        print("preview only; pass --apply to write the reviewed person cards' registry and field mappings")
        return 0

    manifest_rows.extend(new_manifest_rows)
    MANIFEST.write_bytes(csv_bytes(MANIFEST, manifest_fields, manifest_rows))
    ALIGNMENT.write_bytes(csv_bytes(ALIGNMENT, alignment_fields, alignment_rows))
    accepted_text = insert_accepted_paths(
        ACCEPTED.read_text(encoding="utf-8-sig"),
        [record["card_path"] for record in REGISTRATIONS],
    )
    ACCEPTED.write_bytes(text_bytes(ACCEPTED, accepted_text))
    KNOWLEDGE.write_bytes(text_bytes(KNOWLEDGE, knowledge))
    RESULT.write_bytes(text_bytes(RESULT, result))
    write_jsonl(ENRICHMENT, old_enrichment + field_records)
    print("applied: manifest, accepted.yml, alignment, process/results records, and 9 target enrichment rows updated; sources.csv and relations.csv unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
