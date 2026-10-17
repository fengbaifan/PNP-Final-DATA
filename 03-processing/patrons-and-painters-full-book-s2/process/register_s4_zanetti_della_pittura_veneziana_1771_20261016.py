from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import shutil
from pathlib import Path

import yaml


ROOT = Path.cwd()
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
KNOWLEDGE = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-zanetti-della-pittura-1771-20261016"

KU_ID = "units/archives/zanetti-della-pittura-veneziana-1771"
CARD_PATH = "04-knowledge/units/archives/zanetti-della-pittura-veneziana-1771.md"
GROUP = "archive-group-zanetti-della-pittura-veneziana-1771"
CANDIDATES = ["cand-2855", "cand-9837"]
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {"file": "10_CHP-10_sec_ii.md", "lines": "343", "page": "329",
     "quote": "1 In the preface to Della Pittura Veneziana, 1771, p. xiii.",
     "summary": "第10章印刷页329注1引用Della Pittura Veneziana 1771年版序言第xiii页；被引序言未独立查阅。",
     "note": "注1；被引序言页未独立查阅"},
    {"file": "13_CHP-13_intro.md", "lines": "164", "page": "345",
     "quote": "his own Della Pittura Veneziana of 1771",
     "summary": "第13章印刷页345称A. M. Zanetti the Younger自己的Della Pittura Veneziana于1771年出版；记录为Haskell的书内表述。",
     "note": "正文对作品及作者语境的说明"},
    {"file": "21_CHP-21Bibliography.md", "lines": "1285", "page": "441",
     "quote": "Zanetti, AM.: Della Pittura Veneziana, Venezia 1771.",
     "summary": "第21章参考书目印刷页441列Zanetti, AM.、Della Pittura Veneziana、Venezia与1771年；该条未列出版者。",
     "note": "参考书目条目；原书未独立查阅"},
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict[str, str]], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def text_bytes(path: Path, text: str) -> bytes:
    has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if has_bom else text).encode("utf-8")


def group_of(note: str) -> str:
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def source_rows() -> list[dict[str, object]]:
    return [{
        "citation": BOOK_CITATION,
        "location": f"第{item['page']}页；Markdown行{item['lines']}；{item['note']}",
        "sentence_summary": item["summary"],
        "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{item['file']}",
            "source_span": f"lines {item['lines']}; print p. {item['page']}",
        },
    } for item in SOURCES]


def make_card() -> str:
    frontmatter = {
        "title": "《威尼斯绘画论》（On Venetian Painting）",
        "name_en": "On Venetian Painting",
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记A. M. Zanetti the Younger的著作《Della Pittura Veneziana》（中文工作译名《威尼斯绘画论》）。Haskell第21章书目列Zanetti, AM.、Venezia与1771年；第13章正文称这是 younger Zanetti 自己的1771年著作。第10章注释引用其序言第xiii页，但该书及被引页未独立查阅。书目条未列出版者；作者姓名不扩展，且不与既有人物卡A. M. Zanetti the Elder合并。

**English:** This card records *Della Pittura Veneziana* by A. M. Zanetti the Younger, with the working English title *On Venetian Painting*. Haskell’s Chapter 21 bibliography lists Zanetti, AM., Venezia, and 1771; Chapter 13 describes it as the younger Zanetti’s own work of 1771. A Chapter 10 note cites page xiii of its preface, but the book and cited page were not independently consulted. The bibliography entry gives no publisher. The author’s name is not expanded, and this book is kept distinct from the existing person card for A. M. Zanetti the Elder.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 原题与工作译名 | *Della Pittura Veneziana*；中文与英文名称为工作译名 | S2；[第13章 p.345](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L164）；S3；[第21章 p.441](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1285） |
| 作者 | A. M. Zanetti the Younger；第13章称为其本人著作，名字首字母不扩展 | S2；[第13章 p.345](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L164） |
| 出版地与年份 | Venezia，1771；书目条未列出版者 | S3；[第21章 p.441](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1285） |
| Haskell所引位置 | 第10章注1引该书序言第xiii页；被引书页未独立查阅 | S1；[第10章 p.329](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L343） |

### 身份边界

本卡对应1771年书目出版物，不等于A. M. Zanetti the Younger的人物卡。Haskell书内所引序言未查阅，出版者及首字母所指全名仍未确认。

## 关系与证据

### 关系记录

尚无正式关系记录。作者与著作的书目责任事实留待S6关系审查；本卡不将作者身份边界或书目引文直接转为正式关系边。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the Zanetti 1771 archive identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    for item in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        if item["quote"] not in source_path.read_text(encoding="utf-8-sig"):
            raise SystemExit(f"Source quote mismatch: {source_path} line {item['lines']}")

    alignment_fields, alignments, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as stream:
        candidate_rows = list(csv.DictReader(stream))
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_id = {row["candidate_id"]: row for row in alignments
                       if row.get("candidate_id") and not row.get("external_source")}
    for cid in CANDIDATES:
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing S3 candidate or alignment row: {cid}")
        if candidate_by_id[cid].get("suggested_type") != "archive":
            raise SystemExit(f"Unexpected type for {cid}: {candidate_by_id[cid].get('suggested_type')}")
        row = alignment_by_id[cid]
        if row.get("decision") != "new" or row.get("ku_id") or group_of(row.get("resolution_note", "")) != GROUP:
            raise SystemExit(f"{cid} is no longer an unmapped member of {GROUP}.")
    members = sorted(row["candidate_id"] for row in alignments
                     if row.get("candidate_id") and not row.get("external_source")
                     and row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP)
    if members != sorted(CANDIDATES):
        raise SystemExit(f"Unexpected S3 membership for {GROUP}: {members}")
    if len(manifest_rows) != 1310 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected manifest baseline or S4 target already exists.")
    card_path = ROOT / CARD_PATH
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_PATH}")

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment
                     if row.get("candidate_id") and not row.get("external_source")}
    for cid in CANDIDATES:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest_rows)
    planned_manifest.append({"ku_id": KU_ID, "type": "archive",
                             "canonical_name": "《威尼斯绘画论》", "name_en": "On Venetian Painting",
                             "source_task": TASK, "card_path": CARD_PATH})
    planned_manifest.sort(key=lambda row: row["ku_id"])

    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    if any(line == f"- {CARD_PATH}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next((i for i, line in enumerate(accepted_lines)
                      if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
                     next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)))
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(result_text,
        "S4 已登记291组、映射371条成员候选；尚待登记4,549组、4,650条映射。",
        "S4 已登记292组、映射373条成员候选；尚待登记4,548组、4,648条映射。")
    result_text = replace_once(result_text, "1,310 KU；新组登记与待登记分类型统计见下表",
                               "1,311 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| archive | 79→61 | 1,258／1,221 | 31／1,190；1,216 | 0 | 18 | 745 |",
                               "| archive | 79→61 | 1,258／1,221 | 32／1,189；1,214 | 0 | 18 | 745 |")
    follow_up = (
        "### S4 archive follow-up：Zanetti《Della Pittura Veneziana》（1771）（2026-10-16）\n\n"
        "- `cand-2855`（UVWXYZ.csv#192，p.345）与 `cand-9837`（第10章注1、第13章正文及第21章书目）同属 `archive-group-zanetti-della-pittura-veneziana-1771`，映射至 `units/archives/zanetti-della-pittura-veneziana-1771`。书目列Della Pittura Veneziana、Venezia 1771；第13章称其为A. M. Zanetti the Younger自己的著作。\n"
        "- 第10章注1引该书序言p.xiii，未独立查阅。作者首字母不扩展；与既有人物卡A. M. Zanetti the Elder分开。出版者未载，未新增 `relations.csv` 正式边。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记292组/373条映射，待登记4,548组/4,648条映射；archive为32组已登记、1,189组/1,214条成员待登记；KU总数1,311。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 archive：Zanetti《Della Pittura Veneziana》1771年版身份组（2026-10-16）\n\n"
        "- S3组 `archive-group-zanetti-della-pittura-veneziana-1771` 包含索引候选 `cand-2855`（UVWXYZ.csv#192，p.345）与正文／书目候选 `cand-9837`。第10章p.329注1引该书序言p.xiii；第13章p.345称这是A. M. Zanetti the Younger自己的1771年著作；第21章p.441书目列 `Zanetti, AM.: Della Pittura Veneziana, Venezia 1771.`。\n"
        "- 两候选共同登记为 `units/archives/zanetti-della-pittura-veneziana-1771`。正文语境将该书归于younger Zanetti；既有人物卡 `a-m-zanetti-the-elder` 明确对应长者，不把二人合并。作者全名未展开，出版者未载，序言及原书未独立查阅。\n"
        "- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计292组/373条映射，待登记4,548组/4,648条映射；archive为32组已登记、1,189组/1,214条成员待登记；KU总数1,311。\n"
    )
    if "### S4 archive：Zanetti《Della Pittura Veneziana》1771年版身份组" in process_text:
        raise SystemExit("Zanetti S4 process section already exists.")
    process_text += process_section

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != len(SOURCES):
        raise SystemExit("Generated card frontmatter failed validation.")
    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        ACCEPTED: text_bytes(ACCEPTED, planned_accepted),
        RESULT: text_bytes(RESULT, result_text),
        KNOWLEDGE: text_bytes(KNOWLEDGE, process_text),
        card_path: card_text.encode("utf-8-sig"),
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print("  group=1; candidates=2; new cards=1; author remains distinct from the elder Zanetti KU")
    print("  S4: 291/371 -> 292/373 groups/mappings; pending=4,548/4,648")
    print("  archive: registered 31/1,190 -> 32/1,189 groups; pending candidates=1,214")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Zanetti S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-zanetti-della-pittura-1771-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied archive group registration and retained recovery copies.")


if __name__ == "__main__":
    main()
