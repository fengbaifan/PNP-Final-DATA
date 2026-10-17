from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.build_field_facts import ENRICHMENT, SOURCES, assign_ids, extract_records

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST = TABLES / "ku-manifest.csv"
ALIGNMENT = TABLES / "alignment.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
ANCHOR = '<a id="s4-person-direct-relation-endpoints-batch2-20261017"></a>'
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-person-direct-relation-endpoints-batch2-20261017"

REGISTRATIONS = [
    {
        "candidate_id": "cand-2671",
        "group": "new-person:della-francesco-maria-of-rovere-urbino-a2e180b241",
        "ku_id": "units/persons/francesco-maria-della-rovere-urbino",
        "canonical_name": "弗朗切斯科·马里亚·德拉·罗韦雷（Francesco Maria della Rovere）",
        "name_en": "Francesco Maria della Rovere",
        "card_path": "04-knowledge/units/persons/francesco-maria-della-rovere-urbino.md",
        "statements": [
            "st-chp2-seciv-l114-125-duke-death-and-possession-1631",
            "st-chp2-seciv-l114-125-duke-heirless-son",
            "st-chp2-seciv-l114-125-private-possession-inheritance",
        ],
    },
    {
        "candidate_id": "cand-1687",
        "group": "new-person:jennifer-montagu-52540a5df8",
        "ku_id": "units/persons/jennifer-montagu",
        "canonical_name": "詹妮弗·蒙塔古（Jennifer Montagu）",
        "name_en": "Jennifer Montagu",
        "card_path": "04-knowledge/units/persons/jennifer-montagu.md",
        "statements": [
            "st-chp2-seciv-l96-104-montagu-reports-four-ages",
            "st-chp2-seciv-l96-104-montagu-reports-rosichino-teti",
            "st-chp2-seciv-l139-152-montagu-points-author-to-tessin-account",
        ],
    },
    {
        "candidate_id": "cand-0293",
        "group": "new-person:bentivoglio-ippotilo-0720feb34a",
        "ku_id": "units/persons/ippolito-bentivoglio",
        "canonical_name": "伊波利托·本蒂沃利奥（Ippolito Bentivoglio）",
        "name_en": "Ippolito Bentivoglio",
        "card_path": "04-knowledge/units/persons/ippolito-bentivoglio.md",
        "statements": [
            "st-chp2-seciv-l54-63-ippolito-supports-cesare-deste-succession-claim",
            "st-chp2-seciv-l54-63-guido-younger-brother-of-ippolito",
            "st-chp2-seciv-l54-63-enzo-younger-brother-of-ippolito",
        ],
    },
    {
        "candidate_id": "cand-2826",
        "group": "new-person:francis-xavier-914536af47",
        "ku_id": "units/persons/francis-xavier",
        "canonical_name": "圣方济各·沙勿略（Francis Xavier）",
        "name_en": "Francis Xavier",
        "card_path": "04-knowledge/units/persons/francis-xavier.md",
        "statements": [
            "st-chp3-seci-l16-24-gregory-canonisation-xavier",
            "st-chp3-seciv-l75-81-xavier-dedication-and-picture",
            "st-chp3-seciv-notes-l205-243-p85-n4-xavier-relic",
        ],
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
    found = re.search(r"(?:^|[;；\s])group=([^;；\s]+)", row.get("resolution_note", ""))
    return found.group(1) if found else ""


def s4_counts(rows: list[dict[str, str]], candidate_types: dict[str, str]) -> dict[str, tuple[int, int, int, int]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        if row.get("decision") != "new" or row.get("external_source"):
            continue
        group = group_of(row)
        if not group:
            raise ValueError(f"new candidate lacks group token: {row.get('candidate_id')}")
        kind = candidate_types.get(row.get("candidate_id", ""), "")
        if not kind:
            raise ValueError(f"candidate type missing: {row.get('candidate_id')}")
        grouped.setdefault((kind, group), []).append(row)
    counts: dict[str, list[int]] = {}
    for (kind, _group), members in grouped.items():
        target = counts.setdefault(kind, [0, 0, 0, 0])
        kus = {member.get("ku_id", "") for member in members}
        if kus == {""}:
            target[2] += 1
            target[3] += len(members)
        elif len(kus) == 1 and "" not in kus:
            target[0] += 1
            target[1] += len(members)
        else:
            raise ValueError(f"partial or split S4 group: {kind}/{_group}: {sorted(kus)}")
    return {kind: tuple(values) for kind, values in counts.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest_rows = read_csv(MANIFEST)
    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    if len(manifest_rows) != 1730 or len(alignment_rows) != 12645 or len(alignment_fields) < 10:
        raise ValueError(f"unexpected starting tables: manifest={len(manifest_rows)} alignments={len(alignment_rows)}")
    candidate_types = {row["candidate_id"]: row["suggested_type"] for row in candidate_rows}
    if len(candidate_types) != 12407:
        raise ValueError(f"expected 12407 unique candidate records, got {len(candidate_types)}")
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    if len(alignment_by_candidate) != 12407:
        raise ValueError(f"expected one current alignment per candidate, got {len(alignment_by_candidate)}")
    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    manifest_paths = {row["card_path"] for row in manifest_rows}
    expected_before = s4_counts(alignment_rows, candidate_types)
    if expected_before.get("person") != (316, 402, 753, 754):
        raise ValueError(f"unexpected current person S4 counts: {expected_before.get('person')}")
    if (sum(v[0] for v in expected_before.values()), sum(v[1] for v in expected_before.values()),
            sum(v[2] for v in expected_before.values()), sum(v[3] for v in expected_before.values())) != (711, 875, 4070, 4091):
        raise ValueError("unexpected current total S4 counts")

    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        statements = {row["statement_id"]: row for row in (json.loads(line) for line in handle if line.strip())}
    touched = set()
    new_manifest_rows = []
    for record in REGISTRATIONS:
        candidate_id, group, ku_id = record["candidate_id"], record["group"], record["ku_id"]
        if candidate_types.get(candidate_id) != "person":
            raise ValueError(f"candidate is not typed person: {candidate_id}")
        row = alignment_by_candidate.get(candidate_id)
        if not row or row.get("decision") != "new" or row.get("ku_id"):
            raise ValueError(f"candidate is not an unmapped S3 new decision: {candidate_id}")
        if group_of(row) != group:
            raise ValueError(f"S3 identity group mismatch: {candidate_id}")
        members = [r for r in alignment_rows if r.get("decision") == "new" and group_of(r) == group]
        if [r.get("candidate_id") for r in members] != [candidate_id]:
            raise ValueError(f"expected singleton S3 group {group}, got {[r.get('candidate_id') for r in members]}")
        if row.get("alignment_id") in touched:
            raise ValueError(f"duplicate alignment row: {row.get('alignment_id')}")
        touched.add(row["alignment_id"])
        if ku_id in manifest_by_id or record["card_path"] in manifest_paths:
            raise ValueError(f"KU or card path already registered: {ku_id}")
        if not (ROOT / record["card_path"]).is_file():
            raise ValueError(f"reviewed card is missing: {record['card_path']}")
        new_manifest_rows.append({
            "ku_id": ku_id,
            "type": "person",
            "canonical_name": record["canonical_name"],
            "name_en": record["name_en"],
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": record["card_path"],
        })
        for statement_id in record["statements"]:
            statement = statements.get(statement_id)
            if not statement or not statement.get("qualifiers", {}).get("relation_candidate"):
                raise ValueError(f"expected direct S2 relation candidate missing: {statement_id}")
            if candidate_id not in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                raise ValueError(f"candidate is not an endpoint of {statement_id}")

    field_records, source_registry, field_warnings, cards_with_tables = extract_records(new_manifest_rows)
    assign_ids(field_records, ENRICHMENT)
    expected_per_ku = {
        "units/persons/francesco-maria-della-rovere-urbino": 6,
        "units/persons/jennifer-montagu": 3,
        "units/persons/ippolito-bentivoglio": 5,
        "units/persons/francis-xavier": 4,
    }
    actual_per_ku = {ku_id: sum(row["ku_id"] == ku_id for row in field_records) for ku_id in expected_per_ku}
    if cards_with_tables != 4 or len(field_records) != 18 or actual_per_ku != expected_per_ku or field_warnings:
        raise ValueError(f"field preflight mismatch: cards={cards_with_tables}, rows={len(field_records)}, per_ku={actual_per_ku}, warnings={field_warnings}")
    if any(row.get("evidence_status") != "source_backed" or row.get("source_ids") != ["haskell-1980-rev-ed"] for row in field_records):
        raise ValueError("all target field rows must be source-backed by the existing Haskell source")
    if set(source_registry) != {"haskell-1980-rev-ed"}:
        raise ValueError(f"unexpected target source IDs: {sorted(source_registry)}")
    with SOURCES.open(encoding="utf-8-sig", newline="") as handle:
        registered_sources = {row["source_id"] for row in csv.DictReader(handle)}
    if not set(source_registry).issubset(registered_sources):
        raise ValueError("target cards require a new source registry entry")
    old_enrichment = [json.loads(line) for line in ENRICHMENT.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    old_ids = {row.get("enrichment_id") for row in old_enrichment}
    old_occurrences = {row.get("occurrence_id") for row in old_enrichment}
    if any(row["enrichment_id"] in old_ids or row["occurrence_id"] in old_occurrences for row in field_records):
        raise ValueError("target enrichment ID or occurrence already exists")
    if [row["enrichment_id"] for row in field_records] != [f"enr-{n:05d}" for n in range(14437, 14455)]:
        raise ValueError("unexpected target enrichment ID range")

    for record in REGISTRATIONS:
        row = alignment_by_candidate[record["candidate_id"]]
        row["ku_id"] = record["ku_id"]
        row["process_ref"] = "S3-S4-full-book-2026-10-17"
        row["resolution_note"] += f"; S4 registration: mapped {record['group']} to {record['ku_id']}"
    expected_after = s4_counts(alignment_rows, candidate_types)
    totals_after = (
        sum(v[0] for v in expected_after.values()), sum(v[1] for v in expected_after.values()),
        sum(v[2] for v in expected_after.values()), sum(v[3] for v in expected_after.values()),
    )
    if expected_after.get("person") != (320, 406, 749, 750) or totals_after != (715, 879, 4066, 4087):
        raise ValueError(f"unexpected post-registration S4 counts: person={expected_after.get('person')}, total={totals_after}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge,
        "| person | 3,464 | 1,082 | 1,069 / 1,156 | 3 | 7 | 1,216 | 316 / 402 | 753 / 754 |",
        "| person | 3,464 | 1,082 | 1,069 / 1,156 | 3 | 7 | 1,216 | 320 / 406 | 749 / 750 |", "knowledge person row")
    knowledge = replace_once(knowledge,
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **711 / 875** | **4,070 / 4,091** |",
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **715 / 879** | **4,066 / 4,087** |", "knowledge total row")
    if ANCHOR in knowledge or ANCHOR in RESULT.read_text(encoding="utf-8-sig"):
        raise ValueError("batch process anchor already exists")
    field_ids = [row["enrichment_id"] for row in field_records]
    process_detail = [
        "", ANCHOR, "", "### S4 person：四个直接关系端点新组登记（2026-10-17）", "",
        "本批按当前 S3 `new` 决定逐组登记，每个单成员组登记一个 person KU；身份判断依据限于书内姓名、索引定位与正文锚点，不作无证据的跨人合并。",
        "- cand-2671（new-person:della-francesco-maria-of-rovere-urbino-a2e180b241）登记至[Francesco Maria della Rovere 人物卡](../../../04-knowledge/units/persons/francesco-maria-della-rovere-urbino.md)。书末索引给出姓名与 Duke of Urbino 头衔，第2章 p.54 正文同名；未将未具名的占有行动者或全部公爵收藏继承写成已识别事实。",
        "- cand-1687（new-person:jennifer-montagu-52540a5df8）登记至[Jennifer Montagu 人物卡](../../../04-knowledge/units/persons/jennifer-montagu.md)。索引列 p.52、56 注；正文分别提到其 Barberini 天顶画文章及其向作者提供 Tessin 记载的线索。本轮未独立查阅该文章。",
        "- cand-0293（new-person:bentivoglio-ippotilo-0720feb34a）登记至[Ippolito Bentivoglio 人物卡](../../../04-knowledge/units/persons/ippolito-bentivoglio.md)。正文拼写 Ippolito，索引拼作 Ippotilo；以正文拼写作标题并保留索引异写，书内政治行动及 Guido、Enzo 亲缘字段各按原书表述。",
        "- cand-2826（new-person:francis-xavier-914536af47）登记至[Francis Xavier 人物卡](../../../04-knowledge/units/persons/francis-xavier.md)。第3章 p.64、84、85 注4 的 Francis/St Francis Xavier 指向同一具名圣人；圣髑内容仅记录 Haskell 注释，未作独立核验。",
        "- 四张卡共提取18条双语卡片结构字段，均 source_backed 并复用既有 `haskell-1980-rev-ed` 来源；enrichment IDs：enr-14437–enr-14454。sources.csv 未改动。",
        "- 四组各含3条直接 S2 关系候选，共12条；本次只完成端点身份映射，相关关系留待 S6，relations.csv 未新增正式边。",
        "- 登记后 person 类型为320组／406条候选映射已登记、749组／750条待登记；全书累计715组／879条已登记、4,066组／4,087条待登记；KU=1,734，enrichment=10,704。",
        "",
    ]
    knowledge += "\n".join(process_detail)

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result,
        "S4 已登记711组、映射875条成员候选；尚待登记4,070组、4,091条映射。",
        "S4 已登记715组、映射879条成员候选；尚待登记4,066组、4,087条映射。", "result current S4 totals")
    result = replace_once(result, "| [KU 登记](../tables/ku-manifest.csv) | 1,730 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,734 KU；", "result KU count")
    result = replace_once(result, "| [既有字段表](../tables/enrichment.jsonl) | 10,686条", "| [既有字段表](../tables/enrichment.jsonl) | 10,704条", "result enrichment count")
    result = replace_once(result,
        "2026-10-17 strict-stage 表审计通过：KU=1,730；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,686；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,091条",
        "2026-10-17 strict-stage 表审计通过：KU=1,734；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,704；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,087条", "result strict-stage summary")
    result = replace_once(result,
        "| person | 1,082→398 | 1,156／1,069 | 316／753；754 | 3 | 7 | 1,216 |",
        "| person | 1,082→398 | 1,156／1,069 | 320／749；750 | 3 | 7 | 1,216 |", "result person row")
    result = replace_once(result,
        "| **合计** | **1,893→1,040** | **4,966／4,781** | **711／4,070；4,091** | **8** | **100** | **5,440** |",
        "| **合计** | **1,893→1,040** | **4,966／4,781** | **715／4,066；4,087** | **8** | **100** | **5,440** |", "result total row")
    result += "\n\n### S4 person：四个直接关系端点新组登记（2026-10-17）\n\n"
    result += (
        "cand-2671、cand-1687、cand-0293、cand-2826 分别按其 singleton S3 new 组登记至四张人物 KU；"
        "卡片保留原书姓名／索引拼写差异、来源页码和语境限定。18条字段记录（enr-14437–enr-14454）均有既有 Haskell 来源。"
        "12条直接 S2 关系候选的人物端点现已映射，正式关系仍待 S6；sources.csv 与 relations.csv 未改动。"
        "本批后 KU=1,734、enrichment=10,704；S4 已登记715组／879条成员映射，待登记4,066组／4,087条。"
    )

    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    existing_accepted = {line[2:].strip() for line in accepted_text.splitlines() if line.startswith("- ")}
    if any(record["card_path"] in existing_accepted for record in REGISTRATIONS):
        raise ValueError("one or more cards already appear in accepted.yml")
    lines = accepted_text.splitlines(keepends=True)
    if not any(line.strip() == "units:" for line in lines):
        raise ValueError("accepted.yml has no units root")
    newline = "\r\n" if any(line.endswith("\r\n") for line in lines) else "\n"
    for path in sorted(record["card_path"] for record in REGISTRATIONS):
        insert_at = next((i for i, line in enumerate(lines) if line.startswith("- ") and line[2:].strip() > path), len(lines))
        lines.insert(insert_at, f"- {path}{newline}")
    accepted_text = "".join(lines)
    old_enrichment_bytes = ENRICHMENT.read_bytes()
    if old_enrichment_bytes and not old_enrichment_bytes.endswith(b"\n"):
        raise ValueError("enrichment JSONL does not end with a newline")
    new_enrichment_bytes = old_enrichment_bytes + "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in field_records).encode("utf-8")

    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "candidate_mappings": [[row["candidate_id"], row["ku_id"]] for row in REGISTRATIONS],
        "new_ku_rows": len(new_manifest_rows),
        "direct_relation_candidate_endpoints": sum(len(row["statements"]) for row in REGISTRATIONS),
        "field_records": len(field_records),
        "enrichment_ids": field_ids,
        "source_ids": sorted(source_registry),
        "field_warnings": field_warnings,
        "sources_csv_changes": 0,
        "relations_csv_changes": 0,
        "counts_after": {"kus": len(manifest_rows) + 4, "enrichment": len(old_enrichment) + 18, "person_s4": expected_after["person"], "all_s4": totals_after},
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
    ENRICHMENT.write_bytes(new_enrichment_bytes)
    print("applied: four S4 person mappings, four KU manifest/accepted entries, 18 target enrichment rows, and current process/result summaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
