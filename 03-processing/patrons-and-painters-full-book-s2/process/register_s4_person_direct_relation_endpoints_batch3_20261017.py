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
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
ANCHOR = '<a id="s4-person-direct-relation-endpoints-batch3-20261017"></a>'

REGISTRATIONS = [
    {
        "candidate_id": "cand-0542", "group": "new-person:camillo-carandini-camillo-carandini-conte-5372eb31de",
        "ku_id": "units/persons/camillo-carandini", "canonical_name": "卡米洛·卡兰迪尼伯爵（Count Camillo Carandini）",
        "name_en": "Count Camillo Carandini", "card_path": "04-knowledge/units/persons/camillo-carandini.md",
        "statements": ["st-chp5-p137-carandini-among-most-enthusiastic-patrons", "st-chp5-p137-carandini-collected-pictures-of-described-type", "st-chp5-p137-carandini-spanish-alignment"],
    },
    {
        "candidate_id": "cand-0953", "group": "new-person:durazzo-girolamo-f6ce69a495",
        "ku_id": "units/persons/girolamo-durazzo", "canonical_name": "吉罗拉莫·杜拉佐侯爵（Marchese Girolamo Durazzo）",
        "name_en": "Marchese Girolamo Durazzo", "card_path": "04-knowledge/units/persons/girolamo-durazzo.md",
        "statements": ["st-chp8-p213-durazzo-family-membership", "st-chp8-p213-durazzo-local-collection-and-bologna-open", "st-chp8-p214-durazzo-naples-continuation"],
    },
    {
        "candidate_id": "cand-1015", "group": "new-person:andre-felibien-3106675281",
        "ku_id": "units/persons/andre-felibien", "canonical_name": "安德烈·费利比安（André Félibien）",
        "name_en": "André Félibien", "card_path": "04-knowledge/units/persons/andre-felibien.md",
        "statements": ["st-chp4-sec-ii-p114-felibien-classical-theorist", "st-chp4-sec-ii-p114-felibien-codified-enthusiasm", "st-chp4-sec-ii-p115-felibien-in-rome"],
    },
    {
        "candidate_id": "cand-1024", "group": "new-person:andrea-ferrerio-b07af1830b",
        "ku_id": "units/persons/andrea-ferrerio", "canonical_name": "安德烈亚·费雷里奥（Andrea Ferrerio）",
        "name_en": "Andrea Ferrerio", "card_path": "04-knowledge/units/persons/andrea-ferrerio.md",
        "statements": ["st-chp8-p221-ferrerio-sculptor-of-vigilance", "st-chp8-p222-ferrerio-designed-staircase-stucco", "st-chp8-p222-ferrerio-pupil"],
    },
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    import io
    old = path.read_bytes()
    newline = "\r\n" if b"\r\n" in old else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b"") + buffer.getvalue().encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    newline = "\r\n" if b"\r\n" in old else "\n"
    if newline == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    return (b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b"") + text.encode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected one exact match, found {text.count(old)}")
    return text.replace(old, new, 1)


def group_of(row: dict[str, str]) -> str:
    found = re.search(r"(?:^|[;；\s])group=([^;；\s]+)", row.get("resolution_note", ""))
    return found.group(1) if found else ""


def s4_counts(rows: list[dict[str, str]], candidate_types: dict[str, str]) -> dict[str, tuple[int, int, int, int]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        if row.get("decision") != "new" or row.get("external_source"):
            continue
        group = group_of(row)
        kind = candidate_types.get(row.get("candidate_id", ""), "")
        if not group or not kind:
            raise ValueError(f"new candidate missing group or type: {row.get('candidate_id')}")
        groups.setdefault((kind, group), []).append(row)
    counts: dict[str, list[int]] = {}
    for (kind, group), members in groups.items():
        out = counts.setdefault(kind, [0, 0, 0, 0])
        kus = {member.get("ku_id", "") for member in members}
        if kus == {""}:
            out[2] += 1
            out[3] += len(members)
        elif len(kus) == 1 and "" not in kus:
            out[0] += 1
            out[1] += len(members)
        else:
            raise ValueError(f"partially registered or split identity group {group}: {sorted(kus)}")
    return {kind: tuple(values) for kind, values in counts.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest_rows = read_csv(MANIFEST)
    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    _candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidate_types = {row["candidate_id"]: row["suggested_type"] for row in candidate_rows}
    alignment_by_candidate = {row["candidate_id"]: row for row in alignment_rows if row.get("candidate_id") and not row.get("external_source")}
    if len(manifest_rows) != 1734 or len(alignment_rows) != 12645 or len(alignment_by_candidate) != 12407 or len(candidate_types) != 12407:
        raise ValueError(f"unexpected starting counts: KU={len(manifest_rows)}, alignment={len(alignment_rows)}, candidates={len(alignment_by_candidate)}")
    before = s4_counts(alignment_rows, candidate_types)
    before_total = tuple(sum(value[i] for value in before.values()) for i in range(4))
    if before.get("person") != (320, 406, 749, 750) or before_total != (715, 879, 4066, 4087):
        raise ValueError(f"unexpected baseline S4 counts: person={before.get('person')} total={before_total}")

    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    manifest_paths = {row["card_path"] for row in manifest_rows}
    existing_names = {row["name_en"].casefold() for row in manifest_rows}
    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        statements = {row["statement_id"]: row for row in (json.loads(line) for line in handle if line.strip())}
    new_manifest_rows = []
    touched = set()
    for record in REGISTRATIONS:
        cid = record["candidate_id"]
        row = alignment_by_candidate.get(cid)
        if candidate_types.get(cid) != "person" or not row or row.get("decision") != "new" or row.get("ku_id") or group_of(row) != record["group"]:
            raise ValueError(f"unexpected S3 group decision for {cid}")
        members = [r for r in alignment_rows if r.get("decision") == "new" and group_of(r) == record["group"]]
        if [member.get("candidate_id") for member in members] != [cid]:
            raise ValueError(f"expected singleton S3 group {record['group']}")
        if record["ku_id"] in manifest_by_id or record["card_path"] in manifest_paths or record["name_en"].casefold() in existing_names:
            raise ValueError(f"identity appears already registered: {record['ku_id']}")
        if row.get("alignment_id") in touched:
            raise ValueError(f"duplicate alignment row: {row.get('alignment_id')}")
        touched.add(row["alignment_id"])
        card = ROOT / record["card_path"]
        if not card.is_file():
            raise ValueError(f"card missing: {record['card_path']}")
        fm = read_frontmatter(card.read_text(encoding="utf-8-sig"))
        if fm.get("type") != "person" or fm.get("title") != record["canonical_name"] or fm.get("name_en") != record["name_en"]:
            raise ValueError(f"card identity fields mismatch: {record['card_path']}")
        new_manifest_rows.append({"ku_id": record["ku_id"], "type": "person", "canonical_name": record["canonical_name"], "name_en": record["name_en"], "source_task": "patrons-and-painters-full-book-s2", "card_path": record["card_path"]})
        for statement_id in record["statements"]:
            statement = statements.get(statement_id)
            if not statement or not statement.get("qualifiers", {}).get("relation_candidate") or cid not in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                raise ValueError(f"expected direct relation candidate endpoint missing: {statement_id}")

    field_records, source_registry, warnings, card_count = extract_records(new_manifest_rows)
    assign_ids(field_records, ENRICHMENT)
    expected_fields = {
        "units/persons/camillo-carandini": 5,
        "units/persons/girolamo-durazzo": 4,
        "units/persons/andre-felibien": 4,
        "units/persons/andrea-ferrerio": 5,
    }
    actual_fields = {ku_id: sum(row["ku_id"] == ku_id for row in field_records) for ku_id in expected_fields}
    if card_count != 4 or len(field_records) != 18 or actual_fields != expected_fields or warnings:
        raise ValueError(f"field preflight mismatch: cards={card_count}, fields={len(field_records)}, per_KU={actual_fields}, warnings={warnings}")
    if any(row.get("evidence_status") != "source_backed" or row.get("source_ids") != ["haskell-1980-rev-ed"] for row in field_records):
        raise ValueError("all extracted fields must use existing Haskell source evidence")
    if set(source_registry) != {"haskell-1980-rev-ed"}:
        raise ValueError(f"unexpected source registry keys: {sorted(source_registry)}")
    with SOURCES.open(encoding="utf-8-sig", newline="") as handle:
        source_ids = {row["source_id"] for row in csv.DictReader(handle)}
    if not set(source_registry).issubset(source_ids):
        raise ValueError("a new source registry row would be required")
    old_enrichment = [json.loads(line) for line in ENRICHMENT.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    old_ids = {row.get("enrichment_id") for row in old_enrichment}
    old_occurrences = {row.get("occurrence_id") for row in old_enrichment}
    if any(row["enrichment_id"] in old_ids or row["occurrence_id"] in old_occurrences for row in field_records):
        raise ValueError("duplicate enrichment ID or occurrence")
    if [row["enrichment_id"] for row in field_records] != [f"enr-{i:05d}" for i in range(14455, 14473)]:
        raise ValueError("unexpected target enrichment ID range")

    for record in REGISTRATIONS:
        row = alignment_by_candidate[record["candidate_id"]]
        row["ku_id"] = record["ku_id"]
        row["process_ref"] = "S3-S4-full-book-2026-10-17"
        row["resolution_note"] += f"; S4 registration: mapped {record['group']} to {record['ku_id']}"
    after = s4_counts(alignment_rows, candidate_types)
    after_total = tuple(sum(value[i] for value in after.values()) for i in range(4))
    if after.get("person") != (324, 410, 745, 746) or after_total != (719, 883, 4062, 4083):
        raise ValueError(f"unexpected post-registration S4 counts: person={after.get('person')} total={after_total}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge, "| person | 3,464 | 1,082 | 1,069 / 1,156 | 3 | 7 | 1,216 | 320 / 406 | 749 / 750 |", "| person | 3,464 | 1,082 | 1,069 / 1,156 | 3 | 7 | 1,216 | 324 / 410 | 745 / 746 |", "knowledge person row")
    knowledge = replace_once(knowledge, "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **715 / 879** | **4,066 / 4,087** |", "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **719 / 883** | **4,062 / 4,083** |", "knowledge total row")
    if ANCHOR in knowledge or ANCHOR in RESULT.read_text(encoding="utf-8-sig"):
        raise ValueError("batch anchor already exists")
    ids = [row["enrichment_id"] for row in field_records]
    knowledge += "\n".join([
        "", ANCHOR, "", "### S4 person：四个直接关系端点新组登记（2026-10-17）", "",
        "本批按当前 S3 `new` 决定登记四个单成员 person 身份组；只据原书索引和正文记录姓名、角色与书内事实，不作外部身份补证。",
        "- cand-0542（new-person:camillo-carandini-camillo-carandini-conte-5372eb31de）登记至[Count Camillo Carandini 人物卡](../../../04-knowledge/units/persons/camillo-carandini.md)。索引列 Count Camillo Carandini；第5章 p.137 称其倾向西班牙一方且收藏 Cerquozzi 此类绘画，注2随名列出1619–1663。",
        "- cand-0953（new-person:durazzo-girolamo-f6ce69a495）登记至[Marchese Girolamo Durazzo 人物卡](../../../04-knowledge/units/persons/girolamo-durazzo.md)。第8章 p.213–214 将其置于热那亚显贵家族与跨城绘画收藏语境；Giordano、Solimena 的作品按家族归属记录。",
        "- cand-1015（new-person:andre-felibien-3106675281）登记至[André Félibien 人物卡](../../../04-knowledge/units/persons/andre-felibien.md)。索引作 Félibien, André，正文作 Felibien；保留拼写差别。Haskell 称其为法国史家／作者，p.115 关于素描的所有权仍归 Massimi。",
        "- cand-1024（new-person:andrea-ferrerio-b07af1830b）登记至[Andrea Ferrerio 人物卡](../../../04-knowledge/units/persons/andrea-ferrerio.md)。索引含 Vigilance 与 Ferrara 总主教宫子目；第8章 p.221–222 称其为雕塑家及 Giuseppe Mazza 的学生，并记述雕像与楼梯灰泥装饰。",
        f"- 四张卡共提取18条结构字段（{ids[0]}–{ids[-1]}），均 source_backed 并复用既有 `haskell-1980-rev-ed` 来源；sources.csv 未改动。",
        "- 四组各有3条直接 S2 关系候选，共12条；人物端点已映射，相关关系留待 S6；relations.csv 未新增正式边。",
        "- 登记后 person 类型为324组／410条候选映射已登记、745组／746条待登记；全书累计719组／883条已登记、4,062组／4,083条待登记；KU=1,738，enrichment=10,722。", "",
    ])

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result, "S4 已登记715组、映射879条成员候选；尚待登记4,066组、4,087条映射。", "S4 已登记719组、映射883条成员候选；尚待登记4,062组、4,083条映射。", "result S4 current totals")
    result = replace_once(result, "| [KU 登记](../tables/ku-manifest.csv) | 1,734 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,738 KU；", "result KU count")
    result = replace_once(result, "| [既有字段表](../tables/enrichment.jsonl) | 10,704条", "| [既有字段表](../tables/enrichment.jsonl) | 10,722条", "result enrichment count")
    result = replace_once(result, "2026-10-17 strict-stage 表审计通过：KU=1,734；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,704；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,087条", "2026-10-17 strict-stage 表审计通过：KU=1,738；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,722；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,083条", "result audit summary")
    result = replace_once(result, "| person | 1,082→398 | 1,156／1,069 | 320／749；750 | 3 | 7 | 1,216 |", "| person | 1,082→398 | 1,156／1,069 | 324／745；746 | 3 | 7 | 1,216 |", "result person row")
    result = replace_once(result, "| **合计** | **1,893→1,040** | **4,966／4,781** | **715／4,066；4,087** | **8** | **100** | **5,440** |", "| **合计** | **1,893→1,040** | **4,966／4,781** | **719／4,062；4,083** | **8** | **100** | **5,440** |", "result total row")
    result += "\n\n### S4 person：四个直接关系端点新组登记（2026-10-17）\n\n"
    result += (
        "cand-0542、cand-0953、cand-1015、cand-1024 分别按其 singleton S3 new 组登记为人物 KU，"
        "姓名、索引／正文差异及书内身份锚点已写入四张卡。18条字段记录（enr-14455–enr-14472）均复用既有 Haskell 来源。"
        "12条直接 S2 关系候选端点已映射，正式边仍待 S6；sources.csv 与 relations.csv 未改动。"
        "本批后 KU=1,738、enrichment=10,722；S4 已登记719组／883条成员映射，待登记4,062组／4,083条。"
    )

    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_paths = {line[2:].strip() for line in accepted_text.splitlines() if line.startswith("- ")}
    if any(record["card_path"] in accepted_paths for record in REGISTRATIONS):
        raise ValueError("a card path already exists in accepted.yml")
    lines = accepted_text.splitlines(keepends=True)
    newline = "\r\n" if any(line.endswith("\r\n") for line in lines) else "\n"
    for path in sorted(record["card_path"] for record in REGISTRATIONS):
        index = next((i for i, line in enumerate(lines) if line.startswith("- ") and line[2:].strip() > path), len(lines))
        lines.insert(index, f"- {path}{newline}")
    accepted_text = "".join(lines)
    old_bytes = ENRICHMENT.read_bytes()
    if old_bytes and not old_bytes.endswith(b"\n"):
        raise ValueError("enrichment JSONL lacks final newline")
    new_bytes = old_bytes + "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in field_records).encode("utf-8")
    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "mappings": [[r["candidate_id"], r["ku_id"]] for r in REGISTRATIONS],
        "new_kus": len(new_manifest_rows),
        "direct_relation_candidate_endpoints": sum(len(r["statements"]) for r in REGISTRATIONS),
        "field_records": len(field_records), "enrichment_ids": ids,
        "source_ids": sorted(source_registry), "warnings": warnings,
        "sources_csv_changes": 0, "relations_csv_changes": 0,
        "counts_after": {"kus": len(manifest_rows) + 4, "enrichment": len(old_enrichment) + 18, "person_s4": after["person"], "all_s4": after_total},
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return 0

    manifest_rows.extend(new_manifest_rows)
    MANIFEST.write_bytes(csv_bytes(MANIFEST, manifest_fields, manifest_rows))
    ALIGNMENT.write_bytes(csv_bytes(ALIGNMENT, alignment_fields, alignment_rows))
    ACCEPTED.write_bytes(text_bytes(ACCEPTED, accepted_text))
    KNOWLEDGE.write_bytes(text_bytes(KNOWLEDGE, knowledge))
    RESULT.write_bytes(text_bytes(RESULT, result))
    ENRICHMENT.write_bytes(new_bytes)
    print("applied: four S4 person mappings, manifest/accepted entries, 18 source-backed fields, and current process/result totals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
