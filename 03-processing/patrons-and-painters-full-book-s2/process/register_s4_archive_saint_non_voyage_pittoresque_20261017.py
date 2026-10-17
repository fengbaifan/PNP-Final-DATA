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
CARD_PATH = "04-knowledge/units/archives/voyage-pittoresque-greece-sicily.md"
CARD = ROOT / CARD_PATH
ANCHOR = '<a id="s4-archive-saint-non-voyage-pittoresque-20261017"></a>'
KU_ID = "units/archives/voyage-pittoresque-greece-sicily"
CANONICAL_NAME = "《希腊与西西里风景游记》（Picturesque Voyage through Greece and Sicily）"
NAME_EN = "Picturesque Voyage through Greece and Sicily (working translation)"
GROUP = "archive-group-saint-non-voyage-pittoresque-text"
CANDIDATE_IDS = ["cand-10583", "cand-2342"]
DIRECT_STATEMENTS = ["st-chp15-p371-de-non-saint-non-travel-book-work"]
SOURCE_QUOTES = {
    "02-sources/02-Markdown/15_CHP-15_sec_ii.md": [
        "Abbé de Saint-Non’s Voyage Pittoresque de la Grèce et de la Sicile"
    ],
    "02-sources/03-Index/03-1-Index-MD/S.md": [
        "| Saint-Non, Abbé de |  | Voyage Pittoresque de la Grèce et de la Sicile |  | 371 |"
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
    parser = argparse.ArgumentParser(description="Register the Saint-Non Voyage Pittoresque identity group as one archive KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not CARD.is_file():
        raise ValueError(f"target card is missing: {CARD_PATH}")
    frontmatter = read_frontmatter(CARD.read_text(encoding="utf-8-sig"))
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
    if (len(manifest_rows), len(alignment_rows), len(candidate_by_id), len(alignment_by_candidate)) != (1744, 12645, 12407, 12407):
        raise ValueError("unexpected baseline counts")
    before = s4_counts(alignment_rows, candidate_types)
    if before.get("archive") != (106, 147, 1098, 1103) or total_counts(before) != (725, 894, 4056, 4072):
        raise ValueError(f"unexpected S4 baseline: archive={before.get('archive')}, total={total_counts(before)}")
    if any(cid not in candidate_by_id or candidate_types.get(cid) != "archive" for cid in CANDIDATE_IDS):
        raise ValueError("both group members must be present archive candidates")
    group_members = [row for row in alignment_rows if row.get("decision") == "new" and group_of(row) == GROUP]
    if sorted(row.get("candidate_id", "") for row in group_members) != sorted(CANDIDATE_IDS):
        raise ValueError(f"S3 group membership changed: {[row.get('candidate_id') for row in group_members]}")
    if any(row.get("ku_id") for row in group_members):
        raise ValueError("S3 group is already wholly or partially mapped")
    if KU_ID in {row["ku_id"] for row in manifest_rows} or CARD_PATH in {row["card_path"] for row in manifest_rows}:
        raise ValueError("target KU or card path already exists in manifest")

    with STATEMENTS.open(encoding="utf-8-sig") as handle:
        statements = {row["statement_id"]: row for row in (json.loads(line) for line in handle if line.strip())}
    statement = statements.get(DIRECT_STATEMENTS[0])
    if (not statement or not statement.get("qualifiers", {}).get("relation_candidate")
            or statement.get("subject_candidate_id") != "cand-1752"
            or statement.get("object_candidate_id") != "cand-10583"):
        raise ValueError("direct S2 relation candidate endpoints changed")

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
    if cards_with_tables != 1 or len(field_records) != 5 or field_warnings:
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
    candidate_by_id["cand-2342"]["canonical_name"] = "Voyage Pittoresque de la Grèce et de la Sicile"
    candidate_by_id["cand-2342"]["detail"] = (
        "S2 index entry S.csv#30 lists this title under Saint-Non, Abbé de. S3 aligns it with body candidate cand-10583 on the exact title at ch.15 p.371. "
        "Keep distinct from Dominique De Non, who Haskell reports worked on the book in Naples; the nature of that work and any edition remain unspecified."
    )
    candidate_by_id["cand-10583"]["detail"] = (
        "S3 aligns this Haskell body reference with index subentry cand-2342 as the same Voyage Pittoresque title. "
        "Haskell says Dominique De Non worked on it in Naples, without specifying the contribution, edition, or publication details."
    )
    after = s4_counts(alignment_rows, candidate_types)
    after_total = total_counts(after)
    if after.get("archive") != (107, 149, 1097, 1101) or after_total != (726, 896, 4055, 4070):
        raise ValueError(f"unexpected post-registration counts: archive={after.get('archive')}; total={after_total}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge,
        "| archive | 2,100 | 89 | 1,204 / 1,250 | 0 | 18 | 743 | 106 / 147 | 1,098 / 1,103 |",
        "| archive | 2,100 | 89 | 1,204 / 1,250 | 0 | 18 | 743 | 107 / 149 | 1,097 / 1,101 |", "process archive row")
    knowledge = replace_once(knowledge,
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **725 / 894** | **4,056 / 4,072** |",
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **726 / 896** | **4,055 / 4,070** |", "process total row")
    if ANCHOR in knowledge:
        raise ValueError("process anchor already exists")
    enrichment_ids = [row["enrichment_id"] for row in field_records]
    process_section = [
        "", ANCHOR, "", "### S4 archive：Saint-Non《Voyage Pittoresque》身份组登记（2026-10-17）", "",
        "- S3 身份组 `archive-group-saint-non-voyage-pittoresque-text` 含正文候选 `cand-10583`（第15章 p.371 L80）与索引子目候选 `cand-2342`（S.csv#30，页371）。题名完全对应，两候选映射至一个 archive KU。",
        "- Haskell 说 Dominique De Non 曾在那不勒斯为 Abbé de Saint-Non 的出版物工作，但没有说明具体贡献。二者保持为不同人物角色；本卡不推定作者、编者或版本信息。",
        f"- 五条字段记录（{enrichment_ids[0]}–{enrichment_ids[-1]}）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。",
        f"- 直接关系候选 `{DIRECT_STATEMENTS[0]}` 保留待 S6；`relations.csv` 未改动。",
        "- 登记后 archive 类型为107组／149条候选映射已登记、1,097组／1,101条待登记；全书累计726组／896条已登记、4,055组／4,070条待登记；KU=1,745，enrichment=10,763。",
    ]
    knowledge += "\n".join(process_section) + "\n"

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result,
        "S4 已登记725组、映射894条成员候选；尚待登记4,056组、4,072条映射。",
        "S4 已登记726组、映射896条成员候选；尚待登记4,055组、4,070条映射。", "result S4 totals")
    result = replace_once(result, "| [KU 登记](../tables/ku-manifest.csv) | 1,744 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,745 KU；", "result KU count")
    result = replace_once(result, "| [既有字段表](../tables/enrichment.jsonl) | 10,758条", "| [既有字段表](../tables/enrichment.jsonl) | 10,763条", "result field count")
    result = replace_once(result, "| archive | 89→62 | 1,250／1,204 | 106／1,098；1,103 | 0 | 18 | 743 |", "| archive | 89→62 | 1,250／1,204 | 107／1,097；1,101 | 0 | 18 | 743 |", "result archive row")
    result = replace_once(result, "| **合计** | **1,893→1,040** | **4,966／4,781** | **725／4,056；4,072** | **8** | **100** | **5,440** |", "| **合计** | **1,893→1,040** | **4,966／4,781** | **726／4,055；4,070** | **8** | **100** | **5,440** |", "result total row")
    result += (
        "\n\n### S4 archive：Saint-Non《Voyage Pittoresque》文本身份组（2026-10-17）\n\n"
        "S3 组 `archive-group-saint-non-voyage-pittoresque-text` 的正文候选 `cand-10583` 与索引子目候选 `cand-2342` 已映射至一个 archive KU。"
        "五条 source_backed 字段复用 Haskell 来源；Dominique De Non 的参与范围及出版版本未确定，直接关系候选留待 S6。"
        "本批后 KU=1,745、enrichment=10,763；S4 已登记726组／896条，待登记4,055组／4,070条。"
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
        "counts_after": {"kus": len(manifest_rows) + 1, "enrichment": len(old_enrichment) + len(field_records), "archive_s4": after["archive"], "all_s4": after_total},
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return 0

    manifest_rows.append(new_manifest)
    MANIFEST.write_bytes(csv_bytes(MANIFEST, manifest_fields, manifest_rows))
    ALIGNMENT.write_bytes(csv_bytes(ALIGNMENT, alignment_fields, alignment_rows))
    CANDIDATES.write_bytes(csv_bytes(CANDIDATES, candidate_fields, candidate_rows))
    ACCEPTED.write_bytes(text_bytes(ACCEPTED, accepted))
    KNOWLEDGE.write_bytes(text_bytes(KNOWLEDGE, knowledge))
    RESULT.write_bytes(text_bytes(RESULT, result))
    ENRICHMENT.write_bytes(new_jsonl)
    print("applied: one archive KU for both S3 group members; five source-backed fields; current S4 totals updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
