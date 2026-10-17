"""Reconcile the Papal States card source ID with build_field_facts citation identity."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

import yaml


BASE = Path(__file__).resolve().parents[3]
CARD = BASE / "04-knowledge/units/institutions/papal-states.md"
SOURCES = BASE / "04-knowledge/tables/sources.csv"
ALIGNMENT = BASE / "04-knowledge/tables/alignment.csv"
PROCESS = BASE / "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
OLD_ID = "src-6a9a11ba2d327062"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    card_text = read_text(CARD)
    frontmatter = card_text.split("---", 2)[1]
    metadata = yaml.safe_load(frontmatter)
    matches = [
        item for item in metadata.get("sources", [])
        if isinstance(item, dict) and "stato-pontificio" in str(item.get("citation", ""))
    ]
    if len(matches) != 1 or matches[0].get("source_id") != OLD_ID:
        raise SystemExit("Expected exactly one Treccani source with the provisional ID")
    citation = " ".join(str(matches[0]["citation"]).split())
    new_id = "src-" + hashlib.sha256(citation.encode("utf-8")).hexdigest()[:16]
    if new_id == OLD_ID:
        raise SystemExit("No source ID change is needed")

    sources_text = read_text(SOURCES)
    alignment_text = read_text(ALIGNMENT)
    process_text = read_text(PROCESS)
    if sources_text.count(OLD_ID) != 1 or alignment_text.count(OLD_ID) != 1:
        raise SystemExit("Expected one provisional ID in sources.csv and alignment.csv")
    if card_text.count(OLD_ID) != 1:
        raise SystemExit("Expected one provisional ID in the Papal States card")
    if process_text.count(OLD_ID) != 2:
        raise SystemExit("Expected the source record and prior process note to mention the provisional ID")
    if new_id in sources_text or new_id in card_text or new_id in alignment_text:
        raise SystemExit("Canonical source ID already exists; inspect for a duplicate before applying")

    source_rows = list(csv.DictReader(SOURCES.open(encoding="utf-8-sig", newline="")))
    source_rows = [row for row in source_rows if row.get("source_id") == OLD_ID]
    if len(source_rows) != 1 or source_rows[0].get("citation", "") != matches[0]["citation"]:
        raise SystemExit("The source registry row does not match the card citation")

    print(f"Treccani source ID: {OLD_ID} -> {new_id}")
    print("Files: Papal States card, sources.csv, alignment.csv, process/knowledge.md")
    print("Expected source count and all candidate/KU mappings remain unchanged.")
    if args.dry_run:
        print("dry-run passed; no files changed")
        return 0

    CARD.write_text(card_text.replace(OLD_ID, new_id), encoding="utf-8-sig", newline="\n")
    SOURCES.write_text(sources_text.replace(OLD_ID, new_id), encoding="utf-8-sig", newline="\n")
    ALIGNMENT.write_text(alignment_text.replace(OLD_ID, new_id), encoding="utf-8-sig", newline="\n")
    process_text = process_text.replace(OLD_ID, new_id)
    process_text += (
        "\n\n### S3 来源标识规范化：Treccani 条目（2026-10-17）\n\n"
        f"`{OLD_ID}` 是补录 Treccani 来源时使用的临时标识；字段表构建器按卡片引文生成规范 ID `{new_id}`，"
        "原标识会导致预检重复登记。现已将 Papal States 卡、`sources.csv` 与对应 alignment 来源注记统一到规范 ID；"
        "该改动仅规范来源标识，不改变来源、S3 身份决定或 S4 KU 映射。\n"
    )
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print("applied source ID reconciliation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
