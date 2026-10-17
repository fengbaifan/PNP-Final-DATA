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
BACKUP_SUFFIX = ".bak-s4-vianello-carriera-journal-1793-20261016"

KU_ID = "units/archives/carriera-journal-vianello-1793"
CARD_PATH = "04-knowledge/units/archives/carriera-journal-vianello-1793.md"
GROUP = "archive-group-vianello-carriera-journal-1793"
CANDIDATES = ["cand-2766", "cand-10631"]
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCE = {
    "file": "16_CHP-16_intro.md",
    "lines": "41",
    "page": "376",
    "quote": "in the edition he brought out in 1793 of Rosalba’s journal.",
}


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


def make_card() -> str:
    frontmatter = {
        "title": "《卡丽埃拉日记的1793年刊本（题名未载）》（1793 Edition of Rosalba Carriera’s Journal (title unspecified)）",
        "name_en": "1793 Edition of Rosalba Carriera’s Journal (title unspecified)",
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第16章；印刷页376；Markdown行41；题名、版本形式及出版地点未载",
            "sentence_summary": "Haskell称Dr Giovanni Vianello于1793年刊行Rosalba的journal；没有给出题名、格式、出版地点、出版者或所指版本。",
            "original_quotes": [{"source_span": "lines 41", "text": SOURCE["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{SOURCE['file']}",
                "source_span": f"lines {SOURCE['lines']}; print p. {SOURCE['page']}",
            },
        }],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记Haskell所述Dr Giovanni Vianello于1793年刊行的Rosalba Carriera日记版本。原书未提供出版物题名、出版地、出版者、版式或馆藏本信息；卡片标题仅为标明对象及当前缺口的描述性工作名。原刊及其与日记原稿的版本关系未独立查阅。

**English:** This card records the edition of Rosalba Carriera’s journal that Haskell says Dr Giovanni Vianello brought out in 1793. The source gives no publication title, place, publisher, format, or surviving-copy information. The card title is a descriptive working title that marks the object and the missing title. The edition and its relation to any manuscript journal were not independently consulted.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 对象描述 | Rosalba的journal之1793年刊本；出版物题名未载 | S1；[第16章 p.376](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L41） |
| 刊行者与年份 | Haskell称Dr Giovanni Vianello于1793年刊行；不据此推定具体编辑角色 | S1；[第16章 p.376](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L41） |
| 未载信息 | 原刊题名、出版地、出版者、格式、馆藏本及被引页均未给出 | S1；[第16章 p.376](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L41） |

### 身份边界

本卡只表示Haskell报告的1793年刊本，不构成原始日记手稿的知识元，也不推定存世版本或刊行者的具体出版责任。Rosalba与Vianello相关身份／关系不在本archive组内作额外判断。

## 关系与证据

### 关系记录

尚无正式关系记录。刊行者、日记作者与潜在手稿之间的正式关系留待S6审查；本轮不补造标题或版本边。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Vianello's 1793 Carriera journal edition group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")
    source_path = ROOT / "02-sources" / "02-Markdown" / SOURCE["file"]
    if SOURCE["quote"] not in source_path.read_text(encoding="utf-8-sig"):
        raise SystemExit(f"Source quote mismatch: {source_path} line {SOURCE['lines']}")

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
    if len(manifest_rows) != 1314 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
                             "canonical_name": "《卡丽埃拉日记的1793年刊本（题名未载）》",
                             "name_en": "1793 Edition of Rosalba Carriera’s Journal (title unspecified)",
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
        "S4 已登记295组、映射379条成员候选；尚待登记4,545组、4,642条映射。",
        "S4 已登记296组、映射381条成员候选；尚待登记4,544组、4,640条映射。")
    result_text = replace_once(result_text, "1,314 KU；新组登记与待登记分类型统计见下表",
                               "1,315 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| archive | 79→61 | 1,258／1,221 | 35／1,186；1,208 | 0 | 18 | 745 |",
                               "| archive | 79→61 | 1,258／1,221 | 36／1,185；1,206 | 0 | 18 | 745 |")
    follow_up = (
        "### S4 archive follow-up：Vianello 1793年刊行的Carriera日记版本（题名未载）（2026-10-16）\n\n"
        "- `cand-2766`（UVWXYZ.csv#102，p.376）与正文候选 `cand-10631`（第16章p.376）同属 `archive-group-vianello-carriera-journal-1793`，映射至 `units/archives/carriera-journal-vianello-1793`。Haskell称Dr Giovanni Vianello于1793年刊行Rosalba的journal，但未给出版物题名、出版地、载体或版本信息。\n"
        "- 卡片使用明确标注“题名未载”的工作名，不把它升级为原作题名，也不新建或合并手稿对象；未独立查阅原刊。本轮未新增 `relations.csv` 正式边。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记296组/381条映射，待登记4,544组/4,640条映射；archive为36组已登记、1,185组/1,206条成员待登记；KU总数1,315。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 archive：Vianello 1793年刊行的Carriera日记版本身份组（2026-10-16）\n\n"
        "- S3组 `archive-group-vianello-carriera-journal-1793` 包含索引候选 `cand-2766`（UVWXYZ.csv#102，p.376）与正文候选 `cand-10631`。第16章p.376称Vianello于1793年刊行Rosalba的journal。原文限定了年份与刊行行为，但没有题名、出版地、出版者、格式或具体存世版本。\n"
        "- 两个候选共同登记为 `units/archives/carriera-journal-vianello-1793`，卡片题名为标明缺口的描述性工作名。没有补造原刊题名、手稿身份或edition关系；相关关系留待S6。原刊未独立查阅。\n"
        "- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计296组/381条映射，待登记4,544组/4,640条映射；archive为36组已登记、1,185组/1,206条成员待登记；KU总数1,315。\n"
    )
    if "### S4 archive：Vianello 1793年刊行的Carriera日记版本身份组" in process_text:
        raise SystemExit("Vianello S4 process section already exists.")
    process_text += process_section

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 1:
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
    print("  group=1; candidates=2; title remains unspecified in the source")
    print("  S4: 295/379 -> 296/381 groups/mappings; pending=4,544/4,640")
    print("  archive: registered 35/1,186 -> 36/1,185 groups; pending candidates=1,206")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Vianello S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-vianello-carriera-journal-1793-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied archive group registration and retained recovery copies.")


if __name__ == "__main__":
    main()
