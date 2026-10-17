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
BACKUP_SUFFIX = ".bak-s4-sasso-niello-book-1856-20261016"

KU_ID = "units/archives/sasso-osservazioni-niello-1856"
CARD_PATH = "04-knowledge/units/archives/sasso-osservazioni-niello-1856.md"
GROUP = "archive-group-sasso-osservazioni-niello-1856"
CANDIDATES = ["cand-2366", "cand-10601"]
DATE = "2026-10-16"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {"file": "16_CHP-16_intro.md", "lines": "70", "page": "373",
     "quote": "Osservazioni sopra i lavori A niello",
     "summary": "第16章印刷页373注1提及Sasso的1856年版本及其关于niello工艺的著作；OCR将题名转录为“A niello”，保留为原始转录，不据此改写标题。",
     "note": "注1；题名OCR拼写按源文件保留"},
    {"file": "21_CHP-21Bibliography.md", "lines": "1093", "page": "436",
     "quote": "Sasso, G. M.: Osservazioni sopra i lavori di niello",
     "summary": "第21章参考书目印刷页436列Sasso、题名Osservazioni sopra i lavori di niello、E. Cicogna编订及Venezia 1856；此题名的di读法区别于第16章OCR转录。",
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
        "title": "《关于 niello 工艺作品的观察》（Observations on Works in Niello）",
        "name_en": "Observations on Works in Niello",
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

**中文：** 本卡登记G. M. Sasso的《Osservazioni sopra i lavori di niello》（中文工作译名《关于 niello 工艺作品的观察》）。第21章书目列E. Cicogna编订、Venezia 1856；第16章注1称Cicogna于1856年编订出版Sasso的该书。第16章OCR将标题转录为“lavori A niello”，第21章书目则作“lavori di niello”；本卡按书目题名记录，并保留两处原始证据。原书未独立查阅。作者只按书目缩写记录，不判定其与现有人物卡G. M. Sasso的身份是否相同。

**English:** This card records G. M. Sasso’s *Osservazioni sopra i lavori di niello*, with the working English title *Observations on Works in Niello*. Chapter 21’s bibliography lists an edition arranged by E. Cicogna, Venezia, 1856; a Chapter 16 note likewise refers to Cicogna’s 1856 edition of Sasso’s work. The Chapter 16 OCR reads “lavori A niello,” while the Chapter 21 bibliography reads “lavori di niello.” The bibliographic title is used here, with both source readings preserved. The book was not independently consulted. The author is recorded as printed; this card does not decide whether the initials identify the person in the existing G. M. Sasso card.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 原题与工作译名 | *Osservazioni sopra i lavori di niello*；中文与英文名称为工作译名 | S2；[第21章 p.436](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1093） |
| 作者 | G. M. Sasso；书目缩写照录，不在本卡扩展为人物全名 | S2；[第21章 p.436](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1093） |
| 编订者 | E. Cicogna；第16章称其编订1856年版本 | S1；[第16章 p.373](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L70）；S2；[第21章 p.436](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1093） |
| 出版地与年份 | Venezia，1856；书目条未列出版者 | S2；[第21章 p.436](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L1093） |
| 原书引文范围 | 第16章注1提及该1856年版本；未列该书自身页码 | S1；[第16章 p.373](../../../02-sources/02-Markdown/16_CHP-16_intro.md)（L70） |

### 身份边界

本卡表示1856年书目版本，不确认存世本或引文页内容。`G. M. Sasso`为文献中的责任者写法；与既有人物KU的身份映射未由本S3档案组裁决，作者—文献正式关系留待S6。第16章标题的OCR转录错误不改写来源文件。

## 关系与证据

### 关系记录

尚无正式关系记录。作者与编订者的文献责任角色留待S6审查；不将书目归属写为已登记的正式边。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the 1856 Sasso niello book archive group in S4.")
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
    if len(manifest_rows) != 1312 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
                             "canonical_name": "《关于 niello 工艺作品的观察》",
                             "name_en": "Observations on Works in Niello",
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
        "S4 已登记293组、映射375条成员候选；尚待登记4,547组、4,646条映射。",
        "S4 已登记294组、映射377条成员候选；尚待登记4,546组、4,644条映射。")
    result_text = replace_once(result_text, "1,312 KU；新组登记与待登记分类型统计见下表",
                               "1,313 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| archive | 79→61 | 1,258／1,221 | 33／1,188；1,212 | 0 | 18 | 745 |",
                               "| archive | 79→61 | 1,258／1,221 | 34／1,187；1,210 | 0 | 18 | 745 |")
    follow_up = (
        "### S4 archive follow-up：Sasso《Osservazioni sopra i lavori di niello》（1856）（2026-10-16）\n\n"
        "- `cand-2366`（S.csv#54，p.373n）与 `cand-10601`（第16章p.373注1及第21章书目）同属 `archive-group-sasso-osservazioni-niello-1856`，映射至 `units/archives/sasso-osservazioni-niello-1856`。书目列G. M. Sasso、E. Cicogna、Venezia 1856；第16章OCR将标题读为“A niello”，第21章书目作“di niello”，卡片保留差异并按书目题名登记。\n"
        "- 未将作者缩写映射至既有人物卡，也未独立查阅原书。正式作者—作品关系留待S6；本轮未新增 `relations.csv`。\n"
        "- 新增1张archive卡、1条manifest映射、2条候选映射；累计S4登记294组/377条映射，待登记4,546组/4,644条映射；archive为34组已登记、1,187组/1,210条成员待登记；KU总数1,313。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 archive：Sasso《Osservazioni sopra i lavori di niello》1856年版身份组（2026-10-16）\n\n"
        "- S3组 `archive-group-sasso-osservazioni-niello-1856` 包含索引子目 `cand-2366`（S.csv#54，p.373注）和书目/引注候选 `cand-10601`。第16章p.373注1记Cicogna于1856年编订Sasso此书，OCR写作 `A niello`；第21章p.436书目列 `Sasso, G. M.: Osservazioni sopra i lavori di niello`，并列E. Cicogna及Venezia 1856，故本卡按书目题名录入并保留注释OCR原文。两处均未证明原书或被引页已独立查阅。\n"
        "- 两候选共同登记为 `units/archives/sasso-osservazioni-niello-1856`。虽有既有人物卡G. M. Sasso，本组只解决archive出版物身份，未据相同首字母建立人物 `same` 映射或正式作者边；关系端点如需确认，留待S6核对。原书未独立查阅。\n"
        "- 新增1张archive卡、`ku-manifest.csv` 1条、alignment 2条候选映射及`accepted.yml` 1条路径；字段行经 `build_field_facts.py` 预检与apply登记。S4累计294组/377条映射，待登记4,546组/4,644条映射；archive为34组已登记、1,187组/1,210条成员待登记；KU总数1,313。\n"
    )
    if "### S4 archive：Sasso《Osservazioni sopra i lavori di niello》1856年版身份组" in process_text:
        raise SystemExit("Sasso niello S4 process section already exists.")
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
    print("  group=1; candidates=2; OCR title difference preserved against bibliography spelling")
    print("  S4: 293/375 -> 294/377 groups/mappings; pending=4,546/4,644")
    print("  archive: registered 33/1,188 -> 34/1,187 groups; pending candidates=1,210")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Sasso niello S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-sasso-niello-book-1856-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied archive group registration and retained recovery copies.")


if __name__ == "__main__":
    main()
