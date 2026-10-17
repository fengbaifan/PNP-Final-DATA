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
CARD_PATH = "04-knowledge/units/archives/zatta-letter-to-unnamed-duke-1761.md"
CARD = ROOT / CARD_PATH
ANCHOR = '<a id="s4-archive-zatta-letter-1761-20261017"></a>'
KU_ID = "units/archives/zatta-letter-to-unnamed-duke-1761"
CANONICAL_NAME = "Zatta 致未具名公爵书信（1761年）（Zatta’s Letter to an Unnamed Duke, 1761）"
NAME_EN = "Zatta’s Letter to an Unnamed Duke, 1761"
GROUP = "archive-group-zatta-letter-1761"
CANDIDATE_IDS = ["cand-10024", "cand-10178"]
DIRECT_STATEMENTS = [
    "st-chp13-p338-note2-zatta-authored-letter",
    "st-chp13-p338-note2-zatta-letter-to-unnamed-duke",
]
SOURCE_QUOTES = {
    "02-sources/02-Markdown/13_CHP-13_intro.md": [
        "Lettera del Magnifico Signor Antonio Zatta a Sua Eccellenza il Signor Duca di... . In Fiorenza [in fact, Venice], 1761",
        "3 Lettera del Magnifico Signor Antonio Zatta (see p. 338, note 2), p. 23.",
    ]
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
    parser = argparse.ArgumentParser(description="Register the reviewed Zatta 1761 archive identity group as one S4 KU.")
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
    if (len(manifest_rows), len(alignment_rows), len(candidate_by_id), len(alignment_by_candidate)) != (1739, 12645, 12407, 12407):
        raise ValueError("unexpected baseline counts")
    before = s4_counts(alignment_rows, candidate_types)
    if before.get("archive") != (101, 138, 1103, 1112) or total_counts(before) != (720, 885, 4061, 4081):
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
    for sid in DIRECT_STATEMENTS:
        statement = statements.get(sid)
        endpoints = {statement.get("subject_candidate_id"), statement.get("object_candidate_id")} if statement else set()
        if not statement or not statement.get("qualifiers", {}).get("relation_candidate") or "cand-10178" not in endpoints:
            raise ValueError(f"direct S2 relation candidate changed: {sid}")
    page_statement = statements.get("st-chp13-p339-note3-zatta-letter-page23")
    if not page_statement or page_statement.get("qualifiers", {}).get("relation_candidate") is not False or page_statement.get("object_candidate_id") != "cand-10178":
        raise ValueError("p.339 note 3 citation locator no longer points to the reviewed letter candidate")

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
    if cards_with_tables != 1 or len(field_records) != 8 or field_warnings:
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
    candidate_by_id["cand-10024"]["canonical_name"] = "Lettera del Magnifico Signor Antonio Zatta (1761; p. 23 citation for the fountain-and-dolphin vignette)"
    candidate_by_id["cand-10024"]["detail"] = (
        "S2 initially recorded this as an unidentified carrier book and left its relation to cand-10178 for S3. "
        "S3 aligned it with cand-10178: p.339 note 3 cites page 23 of the same 1761 Lettera and explicitly cross-references p.338 note 2. "
        "The Duke remains unnamed and Haskell's printed Fiorenza/[in fact, Venice] wording is preserved. The letter and original imprint were not independently consulted."
    )
    after = s4_counts(alignment_rows, candidate_types)
    after_total = total_counts(after)
    if after.get("archive") != (102, 140, 1102, 1110) or after_total != (721, 887, 4060, 4079):
        raise ValueError(f"unexpected post-registration counts: archive={after.get('archive')}; total={after_total}")

    knowledge = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge = replace_once(knowledge,
        "| archive | 2,100 | 89 | 1,204 / 1,250 | 0 | 18 | 743 | 101 / 138 | 1,103 / 1,112 |",
        "| archive | 2,100 | 89 | 1,204 / 1,250 | 0 | 18 | 743 | 102 / 140 | 1,102 / 1,110 |", "process archive row")
    knowledge = replace_once(knowledge,
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **720 / 885** | **4,061 / 4,081** |",
        "| **合计** | **12,407** | **1,893** | **4,781 / 4,966** | **8** | **100** | **5,440** | **721 / 887** | **4,060 / 4,079** |", "process total row")
    if ANCHOR in knowledge:
        raise ValueError("process anchor already exists")
    enrichment_ids = [row["enrichment_id"] for row in field_records]
    process_section = [
        "", ANCHOR, "", "### S4 archive：Zatta 致未具名公爵书信（1761）双候选组登记（2026-10-17）", "",
        "- S3 身份组 `archive-group-zatta-letter-1761` 含正文候选 `cand-10024` 与书信题名候选 `cand-10178`。p.339 注3明示该段所说的小图像见 Zatta 1761 年书信第23页，并交叉引用第338页注2；两候选由此对齐到同一被引书信，共映射至一个 archive KU。",
        "- 卡片保留 Haskell 所引不完整题名、1761 年、未具名公爵，以及原注 Fiorenza 后附的 Venice 更正；原信、完整题名和刊地未独立核实。第338页注2另列的 `Lettera Giustificativa di Antonio Zatta` 是另一书目对象，未并入本组。",
        f"- 八条字段记录（{enrichment_ids[0]}–{enrichment_ids[-1]}）均为 source_backed，复用既有 `haskell-1980-rev-ed`；未改 `sources.csv`。",
        "- `st-chp13-p338-note2-zatta-authored-letter` 与 `st-chp13-p338-note2-zatta-letter-to-unnamed-duke` 两条直接 S2 关系候选保留待 S6；收信人没有具名端点。`relations.csv` 未改动。",
        "- 登记后 archive 类型为102组／140条候选映射已登记、1,102组／1,110条待登记；全书累计721组／887条已登记、4,060组／4,079条待登记；KU=1,740，enrichment=10,737。",
    ]
    knowledge += "\n".join(process_section) + "\n"

    result = RESULT.read_text(encoding="utf-8-sig")
    result = replace_once(result,
        "S4 已登记720组、映射885条成员候选；尚待登记4,061组、4,081条映射。",
        "S4 已登记721组、映射887条成员候选；尚待登记4,060组、4,079条映射。", "result S4 totals")
    result = replace_once(result, "| [KU 登记](../tables/ku-manifest.csv) | 1,739 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,740 KU；", "result KU count")
    result = replace_once(result, "| [既有字段表](../tables/enrichment.jsonl) | 10,729条", "| [既有字段表](../tables/enrichment.jsonl) | 10,737条", "result field count")
    result = replace_once(result, "| archive | 89→62 | 1,250／1,204 | 101／1,103；1,112 | 0 | 18 | 743 |", "| archive | 89→62 | 1,250／1,204 | 102／1,102；1,110 | 0 | 18 | 743 |", "result archive row")
    result = replace_once(result, "| **合计** | **1,893→1,040** | **4,966／4,781** | **720／4,061；4,081** | **8** | **100** | **5,440** |", "| **合计** | **1,893→1,040** | **4,966／4,781** | **721／4,060；4,079** | **8** | **100** | **5,440** |", "result total row")
    result += (
        "\n\n### S4 archive：Zatta 致未具名公爵书信（1761）（2026-10-17）\n\n"
        "S3 组 `archive-group-zatta-letter-1761` 的 `cand-10024` 与 `cand-10178` 已共同映射至一个 archive KU。"
        "第339页注3通过第23页与第338页注2的交叉引用识别同一书信；八条 source_backed 字段复用 Haskell 来源。"
        "原信与刊地未独立核实；两条直接关系候选留待 S6，未新增正式关系。"
        "本批后 KU=1,740、enrichment=10,737；S4 已登记721组／887条成员映射，待登记4,060组／4,079条。"
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
        "source_candidate_name_updated": "cand-10024",
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
    print("applied: one archive KU for both S3 group members; eight source-backed fields; current S4 totals updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
