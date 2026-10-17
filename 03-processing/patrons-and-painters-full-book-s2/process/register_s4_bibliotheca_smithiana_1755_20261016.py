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
BACKUP_SUFFIX = ".bak-s4-bibliotheca-smithiana-1755-20261016"

KU_ID = "units/archives/bibliotheca-smithiana-1755"
CARD_PATH = "04-knowledge/units/archives/bibliotheca-smithiana-1755.md"
GROUP = "archive-group-bibliotheca-smithiana-1755"
CANDIDATES = ["cand-2450", "cand-9274"]
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {"file": "10_CHP-10_intro.md", "lines": "484", "page": "310",
     "quote": "In 1755 he published an inventory of his books, grandly but slightly absurdly called the Bibliotheca Smithiana, almost certainly designed as an elaborate sale catalogue",
     "summary": "第10章印刷页310称Smith于1755年出版藏书目录Bibliotheca Smithiana；Haskell认为它“几乎可以肯定”是精心制作的售书目录，此为作者推断。",
     "note": "正文；售书目录性质为Haskell推断"},
    {"file": "19_CHP-19Appendix.md", "lines": "158", "page": "394",
     "quote": "the library catalogued in the Bibliotheca Smithiana (published by Pasquali in 1755) to George III",
     "summary": "第19章附录5印刷页394称1762年售予George III的藏书曾编入Bibliotheca Smithiana，并记该目录由Pasquali于1755年出版。",
     "note": "附录5；记录Haskell转述"},
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
        "title": "《史密斯藏书目录》（The Smith Library Catalogue）",
        "name_en": "The Smith Library Catalogue",
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

**中文：** 本卡登记Haskell所称Joseph Smith藏书目录《Bibliotheca Smithiana》，中文与英文名为描述性工作译名。第10章称Smith于1755年出版了该目录，并认为它“几乎可以肯定”是精心制作的售书目录；第19章附录5称Smith于1762年售予George III的藏书曾编入此目录，并记其由Pasquali于1755年出版。售书目录性质保留为Haskell推断；原目录及具体存世版本未独立查阅。

**English:** This card records the catalogue of Joseph Smith’s library referred to by Haskell as *Bibliotheca Smithiana*; the Chinese and English names are descriptive working titles. Chapter 10 says Smith published the catalogue in 1755 and says it was “almost certainly” designed as an elaborate sale catalogue. Chapter 19, Appendix 5, says the library sold to George III in 1762 had been catalogued in it and records publication by Pasquali in 1755. The proposed sale-catalogue purpose remains Haskell’s inference; neither the catalogue nor a surviving edition was independently consulted.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 原称与工作译名 | *Bibliotheca Smithiana*；中文与英文名称为描述性工作译名 | S1；[第10章 p.310](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L484） |
| 文献类型 | 1755年出版的Joseph Smith藏书目录；Haskell称其可能为售书目录，保留为作者推断 | S1；[第10章 p.310](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L484） |
| 出版信息 | 1755年由Pasquali出版；地点及出版者全名未在所引处给出 | S2；[第19章附录5 p.394](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)（L158） |
| 所涉藏书 | Joseph Smith的图书藏品；Haskell称其中编入该目录的藏书于1762年售予George III | S1；[第10章 p.310](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L484）；S2；[第19章附录5 p.394](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)（L158） |

### 身份边界

本卡仅对应1755年《Bibliotheca Smithiana》藏书目录。Haskell在第19章另提1771年 *Catalogo di Libri Raccolti...* 与1773年 *Bibliotheca Smithiana, pars altera*，二者均为不同目录，不并入本卡。第10章所说“几乎可以肯定是售书目录”不是经原件核实的出版目的。

## 关系与证据

### 关系记录

尚无正式关系记录。Joseph Smith、George III与目录所涉藏书的具体关系留待S6审查；本卡记载Haskell的报告，不将其直接转换为正式关系边。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the 1755 Bibliotheca Smithiana archive group in S4.")
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
    if len(manifest_rows) != 1311 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
                             "canonical_name": "《史密斯藏书目录》", "name_en": "The Smith Library Catalogue",
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
        "S4 已登记292组、映射373条成员候选；尚待登记4,548组、4,648条映射。",
        "S4 已登记293组、映射375条成员候选；尚待登记4,547组、4,646条映射。")
    result_text = replace_once(result_text, "1,311 KU；新组登记与待登记分类型统计见下表",
                               "1,312 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| archive | 79→61 | 1,258／1,221 | 32／1,189；1,214 | 0 | 18 | 745 |",
                               "| archive | 79→61 | 1,258／1,221 | 33／1,188；1,212 | 0 | 18 | 745 |")
    follow_up = (
        "### S4 archive follow-up：Bibliotheca Smithiana（1755）（2026-10-16）\n\n"
        "- `cand-2450`（S.csv#139，pp.310、394）与 `cand-9274`（第10章p.310正文及第19章附录5 p.394）同属 `archive-group-bibliotheca-smithiana-1755`，映射至 `units/archives/bibliotheca-smithiana-1755`。Haskell称该目录1755年出版；第19章记由Pasquali出版。\n"
        "- 第10章称它“几乎可以肯定”是精心设计的售书目录，这是Haskell推断；第19章称目录所列藏书于1762年售给George III。1771年 *Catalogo di Libri Raccolti...* 与1773年 *Bibliotheca Smithiana, pars altera* 保持独立。未独立查阅目录原件或版本，未新增 `relations.csv` 正式边。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记293组/375条映射，待登记4,547组/4,646条映射；archive为33组已登记、1,188组/1,212条成员待登记；KU总数1,312。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 archive：Bibliotheca Smithiana 1755年藏书目录身份组（2026-10-16）\n\n"
        "- S3组 `archive-group-bibliotheca-smithiana-1755` 包含索引子目 `cand-2450`（S.csv#139，pp.310、394）和正文候选 `cand-9274`。第10章p.310称Joseph Smith于1755年出版其藏书目录，题为 *Bibliotheca Smithiana*；Haskell认为它“几乎可以肯定”被设计为精心制作的售书目录，此性质保留为作者推断。第19章附录5 p.394记该目录所列藏书于1762年出售给George III，并称目录由Pasquali于1755年出版。\n"
        "- 两候选共同登记为 `units/archives/bibliotheca-smithiana-1755`。与1771年 *Catalogo di Libri Raccolti...*（`cand-2452`/`cand-10832`）及1773年 *Bibliotheca Smithiana, pars altera*（`cand-2451`/`cand-10833`）严格区分；它们均保留各自S3组。原目录及其存世本未独立查阅。Joseph Smith与George III之间关于目录所涉藏书的正式关系留待S6，本轮未新增 `relations.csv`。\n"
        "- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计293组/375条映射，待登记4,547组/4,646条映射；archive为33组已登记、1,188组/1,212条成员待登记；KU总数1,312。\n"
    )
    if "### S4 archive：Bibliotheca Smithiana 1755年藏书目录身份组" in process_text:
        raise SystemExit("Bibliotheca Smithiana S4 process section already exists.")
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
    print("  group=1; candidates=2; 1755 catalogue kept separate from 1771 and 1773 catalogues")
    print("  S4: 292/373 -> 293/375 groups/mappings; pending=4,547/4,646")
    print("  archive: registered 32/1,189 -> 33/1,188 groups; pending candidates=1,212")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Bibliotheca Smithiana S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-bibliotheca-smithiana-1755-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied archive group registration and retained recovery copies.")


if __name__ == "__main__":
    main()
