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
SOURCE_2_PATH = "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
SOURCE_6_PATH = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-clement-ix-accession-20261016"

KU_ID = "units/events/giulio-rospigliosi-accession-clement-ix-1667"
CARD_PATH = "04-knowledge/units/events/giulio-rospigliosi-accession-clement-ix-1667.md"
GROUP = "sg3-event-clement-ix-accession-1667"
CANDIDATES = ["cand-4813", "cand-6482"]
QUOTE_2 = (
    "And when in 1667 Rospigliosi became Pope Clement IX, he managed to give striking proof "
    "of his love of art though he only survived for two years."
)
QUOTE_6 = "The deeply cultivated Giulio Rospigliosi, who became Pope Clement IXin 1667, reigned for only two years"


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


def make_card() -> str:
    frontmatter = {
        "title": "朱利奥·罗斯皮廖西即位为教皇克勉九世（1667）（Giulio Rospigliosi's Accession as Pope Clement IX (1667)）",
        "name_en": "Giulio Rospigliosi's Accession as Pope Clement IX (1667)",
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第2章；印刷页58；OCR L182",
                "sentence_summary": "Haskell称 Rospigliosi 于1667年成为教皇克勉九世，并将其短暂在位与艺术赞助并述。",
                "original_quotes": [{"source_span": "lines 182", "text": QUOTE_2}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_2_PATH,
                    "source_span": "lines 182; print p. 58",
                },
            },
            {
                "citation": BOOK_CITATION,
                "location": "第6章；印刷页161；OCR L3；原文将 Clement IX 与后续词连写，摘录保留原貌",
                "sentence_summary": "Haskell重述 Rospigliosi 于1667年成为克勉九世，并称其在位仅两年；原OCR将 IX 与 in 连写。",
                "original_quotes": [{"source_span": "lines 3", "text": QUOTE_6}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_6_PATH,
                    "source_span": "lines 3; print p. 161",
                },
            },
        ],
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** 本卡记录朱利奥·罗斯皮廖西于1667年即位为教皇克勉九世这一事件。第2章与第6章均将其即位年份记为1667年，并称其在位仅两年；原文没有给出精确的终止日期。本卡保留 Haskell 对短暂在位的概述，不推算具体卒年。

**English:** This unit records Giulio Rospigliosi's accession as Pope Clement IX in 1667. Chapters 2 and 6 both date the accession to 1667 and describe his reign as lasting only two years; neither passage supplies an exact end date. The duration remains Haskell's summary, and no precise death year is inferred.

### 事件信息

| 项目 | 内容 | 证据 |
|---|---|---|
| 事件性质 | 罗丝皮廖西即位为教皇克勉九世 | S1、S2；[第2章 p.58](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L182）；[第6章 p.161](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L3） |
| 时间 | 1667年；原文未给具体日期 | S1、S2；[第2章 p.58](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L182）；[第6章 p.161](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L3） |
| 即位者 | [朱利奥·罗斯皮廖西（Giulio Rospigliosi）](../persons/cardinal-rospigliosi-gimignani.md) | S1、S2；[第2章 p.58](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L182）；[第6章 p.161](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L3） |
| 即位后称号 | 教皇克勉九世（Pope Clement IX） | S1、S2；[第2章 p.58](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L182）；[第6章 p.161](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L3） |
| 在位时长 | Haskell称仅两年；未据此补定具体终止日期 | S1、S2；[第2章 p.58](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L182）；[第6章 p.161](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L3） |

## 关系与证据

### 关系记录

尚无正式关系记录。人物与即位事件的正式参与关系留待 S6 审查；本卡不把两年概述转换为精确的在位起止日期。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Clement IX accession group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    source2 = (ROOT / SOURCE_2_PATH).read_text(encoding="utf-8-sig")
    source6 = (ROOT / SOURCE_6_PATH).read_text(encoding="utf-8-sig")
    if QUOTE_2 not in source2 or QUOTE_6 not in source6:
        raise SystemExit("A quoted passage does not match the chapter source files.")

    alignment_fields, alignments, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    candidate_rows = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing S3 candidate or alignment row: {cid}")
        if candidate_by_id[cid].get("suggested_type") != "event":
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
    if len(manifest_rows) != 1306 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
        "type": "event",
        "canonical_name": "朱利奥·罗斯皮廖西即位为教皇克勉九世（1667）",
        "name_en": "Giulio Rospigliosi's Accession as Pope Clement IX (1667)",
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
    result_text = replace_once(result_text, "S4 已登记287组、映射360条成员候选；尚待登记4,553组、4,661条映射。",
                               "S4 已登记288组、映射362条成员候选；尚待登记4,552组、4,659条映射。")
    result_text = replace_once(result_text, "1,306 KU；新组登记与待登记分类型统计见下表",
                               "1,307 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| event | 7→7 | 235／231 | 15／216；218 | 0 | 0 | 115 |",
                               "| event | 7→7 | 235／231 | 16／215；216 | 0 | 0 | 115 |")
    follow_up = (
        "### S4 event follow-up：跨章 Rospigliosi 1667 年即位组（2026-10-16）\n\n"
        "- `cand-4813`（第2章 p.58）与 `cand-6482`（第6章 p.161）属于同一组 `sg3-event-clement-ix-accession-1667`，登记为 `units/events/giulio-rospigliosi-accession-clement-ix-1667`；两个来源锚点映射到同一事件 KU。\n"
        "- 两章均将即位年份记为1667，并称在位仅两年；不据此补定终止日期。第6章原OCR将 `Clement IX` 与 `in` 连写为 `Clement IXin`，原始摘录保留该转录，摘要按语义表达。人物入口复用既有 Giulio Rospigliosi KU；与人物的正式参与关系仍待 S6。\n"
        "- 新增1张 event 卡、1条 manifest 映射、2条候选映射；累计S4登记288组/362条映射，待登记4,552组/4,659条映射；event 为16组已登记、215组/216条成员待登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 event follow-up：跨章 Rospigliosi 1667 年即位组（2026-10-16）\n\n"
        "- S3 组 `sg3-event-clement-ix-accession-1667` 由 `cand-4813`（ch.2:02_CHP-2_sec_iv:L181–188）与 `cand-6482`（ch.6:06_CHP-6_sec_v:L3–12）组成；同一人物、即位称号及1667年均相符，登记为单一 event KU `units/events/giulio-rospigliosi-accession-clement-ix-1667`。\n"
        "- 第2章 p.58 L182 称 Rospigliosi 于1667年成为 Pope Clement IX；第6章 p.161 L3 重述1667年即位并称仅在位两年。第6章 OCR 将 `Clement IX` 与后词 `in` 连写为 `Clement IXin`；卡片原始摘录保留原貌，转述不照搬该 OCR 拼接。两段均不支持确定终止日期。\n"
        "- 复用既有 Giulio Rospigliosi 人物 KU，不新建同名人物。新卡登记两个候选成员，未新增 `relations.csv`；即位者与事件的正式参与边留待 S6。\n"
        "- 新增1张 event 卡、`ku-manifest.csv` 1条、alignment 2条成员映射及 `accepted.yml` 1条路径；字段行随后通过 `build_field_facts.py` 预检与 apply 登记。S4 累计288组/362条映射，待登记4,552组/4,659条映射；event 为16组已登记、215组/216条成员待登记；KU 总数1,307。\n"
    )
    if "### S4 event follow-up：跨章 Rospigliosi 1667 年即位组" in process_text:
        raise SystemExit("S4 Rospigliosi process section already exists.")
    process_text += process_section

    card_text = make_card()
    card_bytes = card_text.encode("utf-8-sig")
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "event" or len(frontmatter.get("sources", [])) != 2:
        raise SystemExit("Generated card frontmatter failed validation.")

    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        ACCEPTED: text_bytes(ACCEPTED, planned_accepted),
        RESULT: text_bytes(RESULT, result_text),
        KNOWLEDGE: text_bytes(KNOWLEDGE, process_text),
        card_path: card_bytes,
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print("  group=1; candidates=2; new cards=1; both chapter quotes checked")
    print("  S4: 287/360 -> 288/362 groups/mappings; pending=4,552/4,659")
    print("  event: registered 15 -> 16 groups; manifest=1,306 -> 1,307")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Clement IX S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-clement-ix-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied cross-chapter Clement IX accession registration and retained recovery copies.")


if __name__ == "__main__":
    main()
