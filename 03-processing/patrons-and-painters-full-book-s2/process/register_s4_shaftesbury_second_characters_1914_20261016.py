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
BACKUP_SUFFIX = ".bak-s4-shaftesbury-second-characters-1914-20261016"

KU_ID = "units/archives/shaftesbury-second-characters-rand-1914"
CARD_PATH = "04-knowledge/units/archives/shaftesbury-second-characters-rand-1914.md"
GROUP = "archive-group-shaftesbury-second-characters-1914"
CANDIDATES = ["cand-2431", "cand-11434"]
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {"file": "05_CHP-5_sec_iii.md", "lines": "165", "page": "142",
     "quote": "Shaftesbury, Second Characters, p. 15.",
     "summary": "第5章印刷页142注6引用Shaftesbury的Second Characters第15页；该页为被引书页码，被引书页未独立查阅。",
     "note": "注6；被引书p.15未独立查阅"},
    {"file": "21_CHP-21Bibliography.md", "lines": "1110-1111", "page": "437",
     "quote": "Shaftesbury, Third Earl of: Second Characters or The Language of Forms—edited by Benjamin\nRand, Cambridge 1914.",
     "summary": "第21章参考书目印刷页437列Shaftesbury, Third Earl of、Second Characters or The Language of Forms、Benjamin Rand编、Cambridge与1914年。OCR末尾多出撇号，S2按页图记录为非印刷内容。",
     "note": "参考书目条目；S2据页图排除OCR末尾多出的撇号；原书未独立查阅"},
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
        "title": "《第二性格论，或形式的语言》（Second Characters or The Language of Forms）",
        "name_en": "Second Characters or The Language of Forms",
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

**中文：** 本卡登记Shaftesbury第三伯爵的《Second Characters or The Language of Forms》1914年编订版，中文名为描述性工作译名。第21章参考书目列Benjamin Rand编、Cambridge 1914；第5章注6引用该书第15页。该版本及被引页未独立查阅；S2依据页图判断书目OCR末尾多出的撇号不属于印刷内容。

**English:** This card records the 1914 edited edition of *Second Characters or The Language of Forms* by the Third Earl of Shaftesbury, with a descriptive working Chinese title. Haskell’s Chapter 21 bibliography lists Benjamin Rand as editor and Cambridge, 1914; a Chapter 5 note cites page 15. The edition and cited page were not independently consulted. S2 records that a stray apostrophe at the end of the OCR bibliography entry is not present in the page image.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 题名 | *Second Characters or The Language of Forms* | S2；[第21章 p.437](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1110–1111） |
| 作者 | Shaftesbury, Third Earl of；按书目照录 | S2；[第21章 p.437](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1110） |
| 编者 | Benjamin Rand | S2；[第21章 p.437](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1110–1111） |
| 出版地与年份 | Cambridge，1914 | S2；[第21章 p.437](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1111） |
| Haskell所引页码 | 第5章注6引用被引书第15页；该页未独立查阅 | S1；[第5章 p.142](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md)（L165） |

### 身份边界

本卡对应Benjamin Rand编订的1914年出版版本。S2另有 work 类型候选 `cand-6220` 表示题名作品本身；本archive卡不与该 work 候选合并，也不据 edition 身份推定其文本版本关系。原著、手稿和被引页均未独立查阅。

## 关系与证据

### 关系记录

尚无正式关系记录。编者与出版版次之间的文献责任以及版本与抽象作品的关系留待S6审查。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Shaftesbury's 1914 Second Characters archive group in S4.")
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
    if len(manifest_rows) != 1313 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
                             "canonical_name": "《第二性格论，或形式的语言》",
                             "name_en": "Second Characters or The Language of Forms",
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
        "S4 已登记294组、映射377条成员候选；尚待登记4,546组、4,644条映射。",
        "S4 已登记295组、映射379条成员候选；尚待登记4,545组、4,642条映射。")
    result_text = replace_once(result_text, "1,313 KU；新组登记与待登记分类型统计见下表",
                               "1,314 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| archive | 79→61 | 1,258／1,221 | 34／1,187；1,210 | 0 | 18 | 745 |",
                               "| archive | 79→61 | 1,258／1,221 | 35／1,186；1,208 | 0 | 18 | 745 |")
    follow_up = (
        "### S4 archive follow-up：Shaftesbury《Second Characters》1914年编订版（2026-10-16）\n\n"
        "- `cand-2431`（S.csv#119，p.142n）与 `cand-11434`（第21章p.437书目）同属 `archive-group-shaftesbury-second-characters-1914`，映射至 `units/archives/shaftesbury-second-characters-rand-1914`。第5章注6引该书p.15；书目给出完整副题、Benjamin Rand编、Cambridge 1914。\n"
        "- 本卡表示1914年编订版，与work候选 `cand-6220` 保持类型及粒度区分；未独立查阅版本或被引页。S2据页图排除了OCR末尾多出的撇号，未新增 `relations.csv` 正式边。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记295组/379条映射，待登记4,545组/4,642条映射；archive为35组已登记、1,186组/1,208条成员待登记；KU总数1,314。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 archive：Shaftesbury《Second Characters》Rand编1914年版身份组（2026-10-16）\n\n"
        "- S3组 `archive-group-shaftesbury-second-characters-1914` 包含索引候选 `cand-2431`（S.csv#119，p.142n）和书目候选 `cand-11434`。第5章p.142注6引 *Second Characters*, p.15；第21章p.437书目列 *Second Characters or The Language of Forms*、Shaftesbury第三伯爵、Benjamin Rand编、Cambridge 1914。S2依据图像核对记录OCR末尾多出的撇号并非印刷内容。\n"
        "- 两个archive候选共同登记为 `units/archives/shaftesbury-second-characters-rand-1914`。正文S2另有work类型候选 `cand-6220`，表示作品身份而非1914年编订出版版；本轮不合并，也不推定该 edition 与 work 的具体版本关系。原著、版本及被引页未独立查阅。\n"
        "- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计295组/379条映射，待登记4,545组/4,642条映射；archive为35组已登记、1,186组/1,208条成员待登记；KU总数1,314。\n"
    )
    if "### S4 archive：Shaftesbury《Second Characters》Rand编1914年版身份组" in process_text:
        raise SystemExit("Shaftesbury S4 process section already exists.")
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
    print("  group=1; candidates=2; 1914 edition kept separate from the work candidate cand-6220")
    print("  S4: 294/377 -> 295/379 groups/mappings; pending=4,545/4,642")
    print("  archive: registered 34/1,187 -> 35/1,186 groups; pending candidates=1,208")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Shaftesbury S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-shaftesbury-second-characters-1914-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied archive group registration and retained recovery copies.")


if __name__ == "__main__":
    main()
