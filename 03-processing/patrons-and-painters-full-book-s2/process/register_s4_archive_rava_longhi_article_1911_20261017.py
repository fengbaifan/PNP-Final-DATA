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
CARD_PATH = "04-knowledge/units/archives/rava-contributo-alla-biografia-di-pietro-longhi-1911.md"
CARD = ROOT / CARD_PATH
ANCHOR = '<a id="s4-archive-rava-longhi-1911-20261017"></a>'
KU_ID = "units/archives/rava-contributo-alla-biografia-di-pietro-longhi-1911"
CANONICAL_NAME = "《关于皮埃特罗·隆基传记的补充》（Contributo alla biografia di Pietro Longhi）"
NAME_EN = "Contributo alla biografia di Pietro Longhi"
GROUP = "archive-group-84f06577c903"
CANDIDATE_ID = "cand-10054"
DIRECT_STATEMENT = "st-chp13-p340-note3-longhi-letters-rava-publication"
BIBLIOGRAPHY_STATEMENT = "st-chp21-bib-l1022-1057-entry-05"
SOURCE_QUOTES = {
    "02-sources/02-Markdown/13_CHP-13_intro.md": [
        "3 See the seven letters from Pietro Longhi to Remondini between 1748 and 1752 published by A.",
        "Rava, 1911.",
    ],
    "02-sources/02-Markdown/21_CHP-21Bibliography.md": [
        "Rava, A.: ‘Contributo alla biografia di Pietro Longhi’ in Rassegna Contemporanea, IV, 1911, pp. 297-307."
    ],
}


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
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + output.getvalue().encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    newline = "\r\n" if b"\r\n" in old else "\n"
    if newline == "\r\n":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


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
        kind = candidate_types.get(row.get("candidate_id", ""), "")
        group = group_of(row)
        if not kind or not group:
            raise ValueError(f"new decision lacks type/group: {row.get('candidate_id')}")
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
    parser = argparse.ArgumentParser(description="Register the 1911 Rava article as one archive KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not CARD.is_file():
        raise ValueError(f"target card is missing: {CARD_PATH}")
    card_text = CARD.read_text(encoding="utf-8-sig")
    frontmatter = read_frontmatter(card_text)
    if frontmatter.get("type") != "archive" or frontmatter.get("title") != CANONICAL_NAME or frontmatter.get("name_en") != NAME_EN:
        raise ValueError("target card type/name does not match registration")
    for source, quotes in SOURCE_QUOTES.items():
        source_text = (ROOT / source).read_text(encoding="utf-8-sig")
        if any(quote not in source_text for quote in quotes):
            raise ValueError(f"source quote mismatch: {source}")

    manifest_fields, manifest_rows = read_csv(MANIFEST)
    alignment_fields, alignment_rows = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    candidate_types = {row["candidate_id"]: row["suggested_type"] for row in candidate_rows}
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    if (len(manifest_rows), len(alignment_rows), len(candidate_by_id), len(alignment_by_candidate)) != (1748, 12645, 12407, 12407):
        raise ValueError("unexpected table baseline")
    before = s4_counts(alignment_rows, candidate_types)
    if before.get("archive") != (108, 150, 1096, 1100) or total_counts(before) != (729, 900, 4049, 4063):
        raise ValueError(f"unexpected S4 baseline: archive={before.get('archive')}, total={total_counts(before)}")
    if candidate_types.get(CANDIDATE_ID) != "archive":
        raise ValueError("Rava article candidate type changed")
    row = alignment_by_candidate[CANDIDATE_ID]
    if row.get("decision") != "new" or row.get("ku_id") or group_of(row) != GROUP:
        raise ValueError("S3 new identity group changed or is already mapped")
    group_members = [r for r in alignment_rows if r.get("decision") == "new" and group_of(r) == GROUP]
    if [r.get("candidate_id") for r in group_members] != [CANDIDATE_ID]:
        raise ValueError(f"S3 identity group membership changed: {[r.get('candidate_id') for r in group_members]}")
    for distinct_id, expected_group in {
        "cand-10190": "archive-group-24b596c875b8",
        "cand-10305": "archive-group-83cfc3278d12",
        "cand-6579": "archive-group-6dca896a39ba",
    }.items():
        distinct = alignment_by_candidate.get(distinct_id)
        if not distinct or distinct.get("decision") != "new" or group_of(distinct) != expected_group:
            raise ValueError(f"distinct letters/article group changed: {distinct_id}")
        if expected_group == GROUP:
            raise ValueError(f"distinct archive object was merged into Rava article: {distinct_id}")

    if KU_ID in {r["ku_id"] for r in manifest_rows} or CARD_PATH in {r["card_path"] for r in manifest_rows}:
        raise ValueError("target KU or card path already exists in manifest")
    if not CARD_PATH or any(r.get("ku_id") == KU_ID for r in alignment_rows):
        raise ValueError("target KU already appears in an alignment")

    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        statements = {item["statement_id"]: item for item in (json.loads(line) for line in handle if line.strip())}
    direct = statements.get(DIRECT_STATEMENT)
    if not direct or direct.get("qualifiers", {}).get("relation_candidate") is not True or CANDIDATE_ID not in (direct.get("qualifiers", {}).get("mentioned_candidate_ids") or []):
        raise ValueError("S2 publication citation candidate changed")
    bibliography = statements.get(BIBLIOGRAPHY_STATEMENT)
    bib_record = (bibliography or {}).get("qualifiers", {}).get("bibliographic_record") or {}
    if (
        not bibliography
        or bibliography.get("qualifiers", {}).get("relation_candidate") is not False
        or bibliography.get("object_candidate_id") != CANDIDATE_ID
        or bib_record.get("author_as_printed") != "Rava, A."
        or bib_record.get("title_as_printed") != "‘Contributo alla biografia di Pietro Longhi’"
        or bib_record.get("publication_details_as_printed") != "Rassegna Contemporanea, IV, 1911, pp. 297–307"
    ):
        raise ValueError("S2 bibliography identity record changed")

    new_manifest = {
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": CANONICAL_NAME,
        "name_en": NAME_EN,
        "source_task": "patrons-and-painters-full-book-s2",
        "card_path": CARD_PATH,
    }
    field_records, source_registry, field_warnings, cards_with_tables = extract_records([new_manifest])
    assign_ids(field_records, ENRICHMENT)
    if cards_with_tables != 1 or len(field_records) != 7 or field_warnings:
        raise ValueError(f"field extraction mismatch: cards={cards_with_tables}, rows={len(field_records)}, warnings={field_warnings}")
    if any(r.get("evidence_status") != "source_backed" or r.get("source_ids") != ["haskell-1980-rev-ed"] for r in field_records):
        raise ValueError("all target fields must be source-backed by Haskell")
    if set(source_registry) != {"haskell-1980-rev-ed"}:
        raise ValueError(f"unexpected source registry IDs: {sorted(source_registry)}")
    with SOURCES.open(encoding="utf-8-sig", newline="") as handle:
        existing_sources = {r["source_id"] for r in csv.DictReader(handle)}
    if not set(source_registry).issubset(existing_sources):
        raise ValueError("target fields require a new source registry entry")
    old_enrichment = [json.loads(line) for line in ENRICHMENT.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    old_ids = {r.get("enrichment_id") for r in old_enrichment}
    old_occurrences = {r.get("occurrence_id") for r in old_enrichment}
    if any(r["enrichment_id"] in old_ids or r["occurrence_id"] in old_occurrences for r in field_records):
        raise ValueError("target enrichment ID or occurrence already exists")

    new_alignment = alignment_by_candidate[CANDIDATE_ID]
    new_alignment["ku_id"] = KU_ID
    new_alignment["process_ref"] = "S3-S4-full-book-2026-10-17"
    new_alignment["resolution_note"] += f"; S4 登记：{GROUP} → {KU_ID}。作者署名按书目保留为 Rava, A.，未据此创建或合并人物身份。"
    after = s4_counts(alignment_rows, candidate_types)
    after_total = total_counts(after)
    if after.get("archive") != (109, 151, 1095, 1099) or after_total != (730, 901, 4048, 4062):
        raise ValueError(f"unexpected post-registration S4 counts: archive={after.get('archive')}; total={after_total}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge,
        "| archive | 2,100 | 89 | 1,204 / 1,250 | 0 | 18 | 743 | 108 / 150 | 1,096 / 1,100 |",
        "| archive | 2,100 | 89 | 1,204 / 1,250 | 0 | 18 | 743 | 109 / 151 | 1,095 / 1,099 |", "process archive row")
    knowledge = replace_once(knowledge,
        "| **合计** | **12,407** | **1,896** | **4,778 / 4,963** | **8** | **100** | **5,440** | **729 / 900** | **4,049 / 4,063** |",
        "| **合计** | **12,407** | **1,896** | **4,778 / 4,963** | **8** | **100** | **5,440** | **730 / 901** | **4,048 / 4,062** |", "process S3/S4 total row")
    if ANCHOR in knowledge:
        raise ValueError("process anchor already exists")
    enrichment_ids = [r["enrichment_id"] for r in field_records]
    process_section = [
        "", ANCHOR, "", "### S4 archive：Rava《Contributo alla biografia di Pietro Longhi》（1911）登记（2026-10-17）", "",
        "- 单成员 S3 组 `archive-group-84f06577c903`（`cand-10054`）由第13章 p.340 注3的分段引用（L219、L88）与第21章书目 p.435 L1029 对应至同一篇期刊文章；登记一个 archive KU。书目给出的刊名、卷、年份和页码均按原记载分字段录入。",
        "- 作者仅保存书目署名 `Rava, A.`，不扩写全名，也不凭相同署名合并人物。七封 Longhi 致 Remondini 信件 `cand-10190` 是独立 archive 候选；另两篇 Rava 书目文章 `cand-10305`、`cand-6579` 保持各自 S3 身份组。文章和信件未独立查阅。",
        f"- 七条字段记录（{enrichment_ids[0]}–{enrichment_ids[-1]}）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。",
        f"- S2 候选 `{DIRECT_STATEMENT}` 保留待 S6；书目记录本身不是关系断言。`relations.csv` 未改动。",
        "- 登记后 archive 类型为109组／151条候选映射已登记、1,095组／1,099条待登记；全书累计730组／901条已登记、4,048组／4,062条待登记；KU=1,749，enrichment=10,789。",
    ]
    knowledge += "\n".join(process_section) + "\n"

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result,
        "S4 已登记729组、映射900条成员候选；尚待登记4,049组、4,063条映射。",
        "S4 已登记730组、映射901条成员候选；尚待登记4,048组、4,062条映射。", "result current S4 totals")
    result = replace_once(result, "| [KU 登记](../tables/ku-manifest.csv) | 1,748 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,749 KU；", "result KU count")
    result = replace_once(result, "| [既有字段表](../tables/enrichment.jsonl) | 10,782条", "| [既有字段表](../tables/enrichment.jsonl) | 10,789条", "result enrichment count")
    result = replace_once(result,
        "2026-10-17 strict-stage 表审计通过：KU=1,748；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,782；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,063条",
        "2026-10-17 strict-stage 表审计通过：KU=1,749；candidates=12,407；alignments=12,645、unlinked=0；enrichment=10,789；errors=[]、s2_missing=[]。当前待登记 S4 的 new 候选映射为4,062条", "result current audit line")
    result = replace_once(result,
        "| archive | 89→62 | 1,250／1,204 | 108／1,096；1,100 | 0 | 18 | 743 |",
        "| archive | 89→62 | 1,250／1,204 | 109／1,095；1,099 | 0 | 18 | 743 |", "result archive row")
    result = replace_once(result,
        "| work | 235→218 | 496／481 | 50／431；440 | 5 | 29 | 1,632 |",
        "| work | 237→218 | 494／479 | 50／429；438 | 5 | 29 | 1,632 |", "result work row")
    result = replace_once(result,
        "| **合计** | **1,894→1,040** | **4,965／4,780** | **729／4,051；4,065** | **8** | **100** | **5,440** |",
        "| **合计** | **1,896→1,040** | **4,963／4,778** | **730／4,048；4,062** | **8** | **100** | **5,440** |", "result total S3/S4 row")
    result += (
        "\n\n### S4 archive：Rava《Contributo alla biografia di Pietro Longhi》（1911）（2026-10-17）\n\n"
        "`cand-10054` 已登记为 archive KU，七条 source_backed 字段记录书目题名、署名、期刊、卷、年份与页码。作者只按书目署名 `Rava, A.` 记录；七封 Longhi 致 Remondini 信件是独立 archive 候选，另外两篇 Rava 文章也保持各自身份组。本文与信件未独立查阅；S2 引用关系候选留待 S6。"
        "本批后 KU=1,749、enrichment=10,789；S4 已登记730组／901条，待登记4,048组／4,062条。"
    )

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    if CARD_PATH in {line[2:].strip() for line in accepted.splitlines() if line.startswith("- ")}:
        raise ValueError("target card is already in accepted.yml")
    accepted_lines = accepted.splitlines(keepends=True)
    accepted_newline = "\r\n" if any(line.endswith("\r\n") for line in accepted_lines) else "\n"
    insert_at = next((i for i, line in enumerate(accepted_lines) if line.startswith("- ") and line[2:].strip() > CARD_PATH), len(accepted_lines))
    accepted_lines.insert(insert_at, f"- {CARD_PATH}{accepted_newline}")
    accepted = "".join(accepted_lines)

    old_jsonl = ENRICHMENT.read_bytes()
    if old_jsonl and not old_jsonl.endswith(b"\n"):
        raise ValueError("enrichment JSONL lacks final newline")
    new_jsonl = old_jsonl + "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in field_records).encode("utf-8")
    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "identity_group": GROUP,
        "candidate_mappings": {CANDIDATE_ID: KU_ID},
        "separate_groups_preserved": {
            "letters": "cand-10190",
            "Rava_1913_article": "cand-10305",
            "Rava_1942_article": "cand-6579",
        },
        "new_kus": 1,
        "field_records": len(field_records),
        "enrichment_ids": enrichment_ids,
        "source_ids": sorted(source_registry),
        "field_warnings": field_warnings,
        "sources_csv_changes": 0,
        "relations_csv_changes": 0,
        "counts_after": {"kus": len(manifest_rows) + 1, "enrichment": len(old_enrichment) + len(field_records), "archive_s4": after["archive"], "all_s4": after_total},
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    manifest_rows.append(new_manifest)
    MANIFEST.write_bytes(csv_bytes(MANIFEST, manifest_fields, manifest_rows))
    ALIGNMENT.write_bytes(csv_bytes(ALIGNMENT, alignment_fields, alignment_rows))
    ACCEPTED.write_bytes(text_bytes(ACCEPTED, accepted))
    KNOWLEDGE.write_bytes(text_bytes(KNOWLEDGE, knowledge))
    RESULT.write_bytes(text_bytes(RESULT, result))
    ENRICHMENT.write_bytes(new_jsonl)
    print("applied: one archive KU with seven Haskell-backed fields; other Rava publications and the seven letters remain distinct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
