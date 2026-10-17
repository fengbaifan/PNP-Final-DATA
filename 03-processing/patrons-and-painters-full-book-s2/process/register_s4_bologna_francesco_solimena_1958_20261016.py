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
BACKUP_SUFFIX = ".bak-s4-bologna-francesco-solimena-20261016"

KU_ID = "units/archives/ferdinando-bologna-francesco-solimena-1958"
CARD_PATH = "04-knowledge/units/archives/ferdinando-bologna-francesco-solimena-1958.md"
GROUP = "archive-group-bologna-francesco-solimena-1958"
CANDIDATES = ["cand-7348", "cand-7759"]
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {
        "file": "07_CHP-7_sec_v.md",
        "lines": "66",
        "page": "200",
        "quote": "Bologna, p. 191",
        "summary": "第7章印刷页200注4引Bologna第191页，作为Solimena于1715年受邀赴巴黎的书目定位；被引页未独立查阅。",
        "location_note": "注4；被引页未独立查阅",
    },
    {
        "file": "08_CHP-8_sec_i.md",
        "lines": "141",
        "page": "208",
        "quote": "For the influence of this picture see Bologna, p. 20.",
        "summary": "第8章印刷页208注4称关于前文《希律的宴席》影响问题参见Bologna第20页；被引页未独立查阅。",
        "location_note": "注4；被引页未独立查阅",
    },
    {
        "file": "08_CHP-8_sec_ii.md",
        "lines": "161",
        "page": "224",
        "quote": "Bologna (Plate 209) publishes a replica in the Scholz-Forni collection, Hamburg.",
        "summary": "第8章印刷页224称Bologna（图版209）刊载一件位于汉堡Scholz-Forni collection的复制品；这是Haskell的转述，相关书籍及实物未独立查阅。",
        "location_note": "注释／图版引注；仅记录Haskell转述",
    },
    {
        "file": "21_CHP-21Bibliography.md",
        "lines": "217",
        "page": "416",
        "quote": "Bologna, Ferdinando: Francesco Solimena, Napoli 1958.",
        "summary": "第21章参考书目印刷页416列Ferdinando Bologna、Francesco Solimena、Napoli与1958年；该条未列出版者。",
        "location_note": "参考书目条目；书本身未独立查阅",
    },
    {
        "file": "00_05_List_of_Plates.md",
        "lines": "94",
        "page": "",
        "quote": "33 a Solimena: Dido and Aeneas (formerly Palazzo Buonaccorsi, Macerata) 216",
        "summary": "Haskell本书图版目录将Solimena的Dido and Aeneas列为Plate 33a；用于区分本书自身图版号与第8章p.224所引Bologna Plate 209。",
        "location_note": "Plate 33a条目",
    },
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
        raise SystemExit(f"Expected one result occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def make_source_rows() -> list[dict[str, object]]:
    rows = []
    for item in SOURCES:
        if item["page"]:
            location = f"第{item['page']}页；Markdown行{item['lines']}；{item['location_note']}"
            source_span = f"lines {item['lines']}; print p. {item['page']}"
        else:
            location = f"图版目录；Plate 33a；Markdown行{item['lines']}"
            source_span = f"lines {item['lines']}; plate list 33a"
        rows.append({
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": source_span,
            },
        })
    return rows


def make_card() -> str:
    frontmatter = {
        "title": "《弗朗切斯科·索利梅纳》（Francesco Solimena）",
        "name_en": "Francesco Solimena",
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": make_source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记第21章参考书目所列Ferdinando Bologna著《Francesco Solimena》（Napoli，1958）。第7章与第8章注释分别以Bologna短引形式指向该书的第191页和第20页；第8章第224页写作“Bologna (Plate 209)”，并转述该书刊载一件在汉堡Scholz-Forni collection的复制品。Haskell本书图版目录将其自身的《Dido and Aeneas》列为Plate 33a，因此第224页的Plate 209指向被引书内图版。以上判断只依据Haskell本书的书目、注释和图版目录；Bologna原书、被引页及所述复制品均未在本轮独立查阅。书目条未列出版者，本卡不补写。

**English:** This card records *Francesco Solimena* by Ferdinando Bologna, listed in Chapter 21’s bibliography as Napoli, 1958. Notes in Chapters 7 and 8 cite the book in abbreviated form at pages 191 and 20; Chapter 8, page 224, refers to “Bologna (Plate 209)” and reports a replica in the Scholz-Forni collection in Hamburg. Haskell’s own plate list identifies its *Dido and Aeneas* as Plate 33a, so Plate 209 on page 224 refers to a plate in the cited book. This conclusion uses the bibliography, notes, and plate list in Haskell’s book; Bologna’s book, the cited pages, and the reported replica were not independently consulted in this pass. The bibliography entry gives no publisher, which is not supplied here.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 题名 | *Francesco Solimena*；按书目照录 | S4；[第21章 p.416](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L217） |
| 作者 | Ferdinando Bologna；按书目责任者照录 | S4；[第21章 p.416](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L217） |
| 出版地与年份 | Napoli，1958；书目条未列出版者 | S4；[第21章 p.416](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L217） |
| Haskell所引页码 | 第7章注4引第191页；第8章注4引第20页；两处被引页均未独立查阅 | S1；[第7章 p.200](../../../02-sources/02-Markdown/07_CHP-7_sec_v.md)（L66）；S2；[第8章 p.208](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L141） |
| 图版引述 | 第8章称“Bologna (Plate 209)”刊载一件复制品；Haskell本书的《Dido and Aeneas》列为Plate 33a，据此区分被引书的图版号；Bologna原书未独立查阅 | S3；[第8章 p.224](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L161）；S5；[本书图版目录](../../../02-sources/02-Markdown/00_05_List_of_Plates.md)（L94） |

### 身份边界

本卡表示书目中的1958年出版物，不代表对该书版本、出版者或内容的外部核验。第224页所述复制品没有足以独立识别实物的进一步信息，不与该作品候选或Scholz-Forni collection合并；与Solimena及复制品相关的正式关系留待S6审查。

## 关系与证据

### 关系记录

尚无正式关系记录。第224页的作品与收藏叙述保留为Haskell的转述，不据此新增作品或收藏关系边。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the Bologna Francesco Solimena archive group in S4.")
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
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing S3 candidate or alignment row: {cid}")
        if candidate_by_id[cid].get("suggested_type") != "archive":
            raise SystemExit(f"Unexpected type for {cid}: {candidate_by_id[cid].get('suggested_type')}")
        row = alignment_by_id[cid]
        if row.get("decision") != "new" or row.get("ku_id") or group_of(row.get("resolution_note", "")) != GROUP:
            raise SystemExit(f"{cid} is no longer an unmapped member of {GROUP}.")
    members = sorted(
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and group_of(row.get("resolution_note", "")) == GROUP
    )
    if members != sorted(CANDIDATES):
        raise SystemExit(f"Unexpected S3 membership for {GROUP}: {members}")
    if len(manifest_rows) != 1308 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected manifest baseline or the S4 target already exists.")
    card_path = ROOT / CARD_PATH
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_PATH}")

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "《弗朗切斯科·索利梅纳》",
        "name_en": "Francesco Solimena",
        "source_task": TASK,
        "card_path": CARD_PATH,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    if any(line == f"- {CARD_PATH}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(
        result_text,
        "S4 已登记289组、映射364条成员候选；尚待登记4,551组、4,657条映射。",
        "S4 已登记290组、映射366条成员候选；尚待登记4,550组、4,655条映射。",
    )
    result_text = replace_once(result_text, "1,308 KU；新组登记与待登记分类型统计见下表",
                               "1,309 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| archive | 79→61 | 1,258／1,221 | 29／1,192；1,223 | 0 | 18 | 745 |",
                               "| archive | 79→61 | 1,258／1,221 | 30／1,191；1,221 | 0 | 18 | 745 |")
    follow_up = (
        "### S4 archive follow-up：Bologna《Francesco Solimena》（2026-10-16）\n\n"
        "- `cand-7348`（第7、8章注释及第21章书目）与 `cand-7759`（第8章 p.224“Bologna (Plate 209)”）同属 `archive-group-bologna-francesco-solimena-1958`，映射至 `units/archives/ferdinando-bologna-francesco-solimena-1958`。书目p.416列Ferdinando Bologna、题名 *Francesco Solimena*、Napoli 1958；没有出版者信息。\n"
        "- 第7章p.200注4引该书p.191，第8章p.208注4引p.20；被引页未独立查阅。第8章p.224称该书图版209刊载一件在汉堡Scholz-Forni collection的复制品；此处只保存Haskell的转述，不据此识别复制品、确认原书内容或建立关系。未新增 `relations.csv` 正式边。\n"
        "- 新增1张 archive 卡、1条 manifest 映射及2条候选映射；累计S4登记290组/366条映射，待登记4,550组/4,655条映射；archive 为30组已登记、1,191组/1,221条成员待登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 archive：Bologna《Francesco Solimena》跨章身份组（2026-10-16）\n\n"
        "- S3组 `archive-group-bologna-francesco-solimena-1958` 包含 `cand-7348` 与 `cand-7759`。前者由第7章p.200注4、第8章p.204/p.208/p.212–214引注及第21章p.416书目锚定；后者是第8章p.224的“Bologna (Plate 209)”。p.416书目列Ferdinando Bologna、*Francesco Solimena*、Napoli 1958；Haskell本书的图版目录把Dido图像列为Plate 33a，p.224的209因此指被引书图版号。该身份决定和映射见alignment对应行。\n"
        "- 两个候选共同登记为 `units/archives/ferdinando-bologna-francesco-solimena-1958`。正文注释所引Bologna pp.191、20均未独立查阅，Bologna原书、其版本/出版者和p.224所述复制品均未外核；书目条未列出版者。`cand-7760`复制品work、`cand-7761` Scholz-Forni collection（类型仍待决）保持独立，不由此新增KU或正式关系。\n"
        "- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行随后经 `build_field_facts.py` 预检与apply登记。S4累计290组/366条映射，待登记4,550组/4,655条映射；archive为30组已登记、1,191组/1,221条成员待登记；KU总数1,309。\n"
    )
    if "### S4 archive：Bologna《Francesco Solimena》跨章身份组" in process_text:
        raise SystemExit("Bologna S4 process section already exists.")
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
    print("  group=1; candidates=2; new cards=1; original Bologna book and cited pages remain unconsulted")
    print("  S4: 289/364 -> 290/366 groups/mappings; pending=4,550/4,655")
    print("  archive: registered 29/1,192 -> 30/1,191 groups; pending candidates=1,221")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Bologna S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-bologna-francesco-solimena-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied archive group registration and retained recovery copies.")


if __name__ == "__main__":
    main()
