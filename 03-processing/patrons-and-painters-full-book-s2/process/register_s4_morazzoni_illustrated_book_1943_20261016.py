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
BACKUP_SUFFIX = ".bak-s4-morazzoni-book-1943-20261016"

KU_ID = "units/archives/morazzoni-illustrated-book-venice-1943"
CARD_PATH = "04-knowledge/units/archives/morazzoni-illustrated-book-venice-1943.md"
GROUP = "archive-group-morazzoni-book-1943"
CANDIDATES = ["cand-10137", "cand-10140", "cand-10143", "cand-10162", "cand-10175"]
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {"file": "13_CHP-13_intro.md", "lines": "183", "page": "332", "quote": "4 Berengo, 1957, and Morazzoni. See also Gallo, 1948, pp. 153-214. It should be noted that Marin, Vin, p. 234, challenges the optimistic view generally given of eighteenth-century engraving in Venice.", "summary": "第13章印刷页332注4在相关讨论中引Morazzoni，但没有列出该书页码；这里只记录Haskell的书目指引。", "note": "注4；Morazzoni未附页码"},
    {"file": "13_CHP-13_intro.md", "lines": "184", "page": "332", "quote": "5 Morazzoni, p. 70.", "summary": "第13章印刷页332注5引用Morazzoni第70页；被引页未独立查阅。", "note": "注5；被引页未独立查阅"},
    {"file": "13_CHP-13_intro.md", "lines": "187", "page": "334", "quote": "2 Morazzoni, p. 131.", "summary": "第13章印刷页334注2引用Morazzoni第131页讨论Albrizzi继承的业务；被引页未独立查阅。", "note": "注2；被引页未独立查阅"},
    {"file": "13_CHP-13_intro.md", "lines": "197", "page": "336", "quote": "3 Morazzoni.", "summary": "第13章印刷页336注3只写Morazzoni，未列书名或页码；这里只记录Haskell的书目指引。", "note": "注3；未列书名或页码"},
    {"file": "13_CHP-13_intro.md", "lines": "201", "page": "336", "quote": "7 Morazzoni, p. 117.", "summary": "第13章印刷页336注7引用Morazzoni第117页；被引页未独立查阅。", "note": "注7；被引页未独立查阅"},
    {"file": "13_CHP-13_intro.md", "lines": "207", "page": "337", "quote": "Morazzoni, p. 116.", "summary": "第13章印刷页337注5引用Morazzoni第116页说明Officium段落；被引页未独立查阅。", "note": "注5；被引页未独立查阅"},
    {"file": "21_CHP-21Bibliography.md", "lines": "843", "page": "430", "quote": "Morazzoni, G.: Il libro illustrato veneziano del Settecento, Milano 1943.", "summary": "第21章参考书目印刷页430列G. Morazzoni、Il libro illustrato veneziano del Settecento、Milano与1943年；未列出版者。", "note": "参考书目条目；原书未独立查阅"},
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
        "title": "《十八世纪威尼斯插图书籍》（The Venetian Illustrated Book of the Eighteenth Century）",
        "name_en": "The Venetian Illustrated Book of the Eighteenth Century",
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

**中文：** 本卡登记G. Morazzoni的《Il libro illustrato veneziano del Settecento》，中文工作译名为《十八世纪威尼斯插图书籍》。Haskell第21章参考书目将该书列为Milano，1943年出版；第13章多处注释引Morazzoni，其中四处给出第70、131、117、116页，另两处未列页码。原书和这些被引页均未独立查阅，书目条未列出版者；本卡不补写出版者或扩展作者姓名。

**English:** This card records G. Morazzoni’s *Il libro illustrato veneziano del Settecento*, with the working English title *The Venetian Illustrated Book of the Eighteenth Century*. Haskell’s Chapter 21 bibliography lists it as published in Milano in 1943. Several Chapter 13 notes cite Morazzoni; four give pages 70, 131, 117, and 116, while two provide no page number. The book and cited pages were not independently consulted. The bibliography entry names no publisher, and none is supplied here; the author’s initial is not expanded.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 原题与工作译名 | *Il libro illustrato veneziano del Settecento*；中文及英文名称为工作译名 | S7；[第21章 p.430](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L843） |
| 作者 | G. Morazzoni；按书目照录，不扩展名字首字母 | S7；[第21章 p.430](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L843） |
| 出版地与年份 | Milano，1943；书目条未列出版者 | S7；[第21章 p.430](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L843） |
| Haskell的引文定位 | 第13章注5引第70页、注2引第131页、注7引第117页、注5引第116页；注4与第336页注3只列Morazzoni而无页码。以上页码均为被引书页码，未独立查阅 | S1–S2；[p.332](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L183–184）；S3；[p.334](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L187）；S4–S6；[pp.336–337](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L197、201、207） |

### 身份边界

本卡对应书目明确列出的1943年出版物及上述五条身份映射；不把其他未具书名的Morazzoni引文自动归入本书，不把G.擅自扩展为全名，也不据这些引注声称已验证其内容。

## 关系与证据

### 关系记录

尚无正式关系记录。Haskell的引文定位不单独构成该书与正文人物、作品或活动之间的正式关系。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the Morazzoni 1943 archive identity group in S4.")
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
    if len(manifest_rows) != 1309 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
                             "canonical_name": "《十八世纪威尼斯插图书籍》",
                             "name_en": "The Venetian Illustrated Book of the Eighteenth Century",
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
        "S4 已登记290组、映射366条成员候选；尚待登记4,550组、4,655条映射。",
        "S4 已登记291组、映射371条成员候选；尚待登记4,549组、4,650条映射。")
    result_text = replace_once(result_text, "1,309 KU；新组登记与待登记分类型统计见下表",
                               "1,310 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| archive | 79→61 | 1,258／1,221 | 30／1,191；1,221 | 0 | 18 | 745 |",
                               "| archive | 79→61 | 1,258／1,221 | 31／1,190；1,216 | 0 | 18 | 745 |")
    follow_up = (
        "### S4 archive follow-up：Morazzoni《Il libro illustrato veneziano del Settecento》（2026-10-16）\n\n"
        "- `cand-10137`、`cand-10140`、`cand-10143`、`cand-10162`、`cand-10175` 同属 `archive-group-morazzoni-book-1943`，映射至 `units/archives/morazzoni-illustrated-book-venice-1943`。第21章p.430书目给出G. Morazzoni、题名、Milano与1943年；第13章相关短引分别提供四个页码定位及两处无页码指引。\n"
        "- 原书和被引页未独立查阅；出版者未载，作者首字母未扩展。其他未具书名的Morazzoni引注不并入本组。本轮只登记书目身份，不新增 `relations.csv` 正式边。\n"
        "- 新增1张archive卡、1条manifest映射、5条候选映射；累计S4登记291组/371条映射，待登记4,549组/4,650条映射；archive为31组已登记、1,190组/1,216条成员待登记；KU总数1,310。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 archive：Morazzoni《Il libro illustrato veneziano del Settecento》跨章身份组（2026-10-16）\n\n"
        "- S3组 `archive-group-morazzoni-book-1943` 包含 `cand-10137`、`cand-10140`、`cand-10143`、`cand-10162`、`cand-10175`：`cand-10137` 为第13章无页码引注及第21章书目身份；其余四项分别是第13章p.332注5、p.334注2、p.336注7、p.337注5的pp.70、131、117、116定位。第13章p.336注3另有无标题、无页码的Morazzoni短引，对应同一候选。第21章p.430书目明确列G. Morazzoni, *Il libro illustrato veneziano del Settecento*, Milano 1943。\n"
        "- 五个候选共同登记为 `units/archives/morazzoni-illustrated-book-venice-1943`。未扩展G.的名字，未补出版者；原书及所引各页均未独立查阅。仍未具书名的其他Morazzoni引文保持独立，不并入本组。未新增 `relations.csv`。\n"
        "- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 5条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计291组/371条映射，待登记4,549组/4,650条映射；archive为31组已登记、1,190组/1,216条成员待登记；KU总数1,310。\n"
    )
    if "### S4 archive：Morazzoni《Il libro illustrato veneziano del Settecento》跨章身份组" in process_text:
        raise SystemExit("Morazzoni S4 process section already exists.")
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
    print("  group=1; candidates=5; new cards=1; original book and cited pages unconsulted")
    print("  S4: 290/366 -> 291/371 groups/mappings; pending=4,549/4,650")
    print("  archive: registered 30/1,191 -> 31/1,190 groups; pending candidates=1,216")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Morazzoni S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-morazzoni-book-1943-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied archive group registration and retained recovery copies.")


if __name__ == "__main__":
    main()
