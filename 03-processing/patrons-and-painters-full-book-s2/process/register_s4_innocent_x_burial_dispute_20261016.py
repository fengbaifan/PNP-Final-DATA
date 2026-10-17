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
SOURCE_PATH = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-innocent-x-burial-dispute-20261016"

KU_ID = "units/events/innocent-x-burial-expense-dispute-1655"
CARD_PATH = "04-knowledge/units/events/innocent-x-burial-expense-dispute-1655.md"
GROUP = "sg3-event-cand-6297"
CANDIDATES = ["cand-1821", "cand-6297"]
QUOTE = (
    "As a final economy measure; and one which in its squalid avarice-and feuds symbolises much of Innocent X’s reign, "
    "Donna Olimpia and Prince Camillo Pamfili refused to pay for a coffin for the Pope when he died in January 1655. "
    "While the corpse lay rotting in a cellar, mother and son quarrelled over who should be charged for the burial."
)


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
        "title": "教皇英诺森十世葬礼费用争议（1655）（Dispute over the Funeral Expenses of Pope Innocent X (1655)）",
        "name_en": "Dispute over the Funeral Expenses of Pope Innocent X (1655)",
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第6章；印刷页150；OCR L56；注5所引 Pastor XIV p.37 未独立查阅",
            "sentence_summary": "Haskell记述 Donna Olimpia 与 Prince Camillo Pamfili 在英诺森十世1655年1月去世后拒付棺木费用，并争论安葬费用由谁承担；最终支付情况未载。",
            "original_quotes": [{"source_span": "lines 56", "text": QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_PATH,
                "source_span": "lines 56; print p. 150; footnote 5 cites Pastor, XIV, p. 37",
            },
        }],
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 所述英诺森十世于1655年1月去世后的葬礼费用争议：Donna Olimpia 与 Prince Camillo Pamfili 被称拒绝支付棺木费用，母子二人又争论应由谁承担安葬费用。Haskell称遗体一度停放在地窖；这保留为原书报告。注5引 Pastor, XIV, p.37，本轮未独立查阅；原文没有说明最终由谁支付。

**English:** This unit records Haskell's account of a dispute over funeral expenses after Pope Innocent X died in January 1655. Donna Olimpia and Prince Camillo Pamfili are said to have refused to pay for a coffin, and the mother and son quarrelled over who should bear the burial costs. Haskell says the corpse lay in a cellar; this remains attributed to his account. Footnote 5 cites Pastor, XIV, p.37, which was not independently consulted. Haskell does not say who ultimately paid.

### 事件信息

| 项目 | 内容 | 证据 |
|---|---|---|
| 事件性质 | 英诺森十世葬礼棺木与安葬费用争议 | S1；[第6章 p.150](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L56） |
| 时间 | 1655年1月；英诺森十世去世时；原文未给具体日期 | S1；[第6章 p.150](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L56） |
| 逝者 | [教皇英诺森十世（Pope Innocent X）](../persons/innocent-x.md) | S1；[第6章 p.150](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L56） |
| 争议参与者 | [Donna Olimpia（Olimpia Maidalchini）](../persons/olimpia-maidalchini.md)；Haskell称她拒绝支付棺木费用，并与其子争议安葬费用承担者 | S1；[第6章 p.150](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L56） |
| 争议参与者 | [Prince Camillo Pamfili（Camillo Pamfili）](../persons/camillo-pamfili.md)；Haskell称其拒绝支付棺木费用，并与母亲争议安葬费用承担者 | S1；[第6章 p.150](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L56） |
| 结果 | Haskell 未说明最终由谁支付或争议如何解决；其叙述由注5所引 Pastor 支持，但该页未独立查阅 | S1；[第6章 p.150](../../../02-sources/02-Markdown/06_CHP-6_sec_i.md)（L56） |

## 关系与证据

### 关系记录

尚无正式关系记录。逝者与两名争议参与者的正式事件关系留待 S6 审查；本卡不补写最终付款或争议解决结果。
"""
    return f"---\n{header}---\n\n{body.strip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the Innocent X funeral-expense dispute group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")
    source = (ROOT / SOURCE_PATH).read_text(encoding="utf-8-sig")
    if QUOTE not in source:
        raise SystemExit("The quoted passage does not match the chapter source file.")

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
    if len(manifest_rows) != 1307 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
        "canonical_name": "教皇英诺森十世葬礼费用争议（1655）",
        "name_en": "Dispute over the Funeral Expenses of Pope Innocent X (1655)",
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
    result_text = replace_once(result_text, "S4 已登记288组、映射362条成员候选；尚待登记4,552组、4,659条映射。",
                               "S4 已登记289组、映射364条成员候选；尚待登记4,551组、4,657条映射。")
    result_text = replace_once(result_text, "1,307 KU；新组登记与待登记分类型统计见下表",
                               "1,308 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text, "| event | 7→7 | 235／231 | 16／215；216 | 0 | 0 | 115 |",
                               "| event | 7→7 | 235／231 | 17／214；214 | 0 | 0 | 115 |")
    follow_up = (
        "### S4 event follow-up：Innocent X 葬礼费用争议组（2026-10-16）\n\n"
        "- `cand-1821` 是 `P.csv#20`（Pamfili, Gianbattista / Innocent X）之“dispute over burial of”子目；该父级索引名虽指人物，子目实际指事件。它与第6章正文候选 `cand-6297` 同属 `sg3-event-cand-6297`，现映射至 `units/events/innocent-x-burial-expense-dispute-1655`。未把索引子目并入 Innocent X 人物 KU。\n"
        "- p.150 L56 称 Donna Olimpia 与 Prince Camillo Pamfili 在 Innocent X 于1655年1月去世时拒绝支付棺木费用，并争议安葬费用承担者。注5引 Pastor, XIV, p.37，本轮未独立查阅；原文没有交代最终付款者或解决方式。三个人物端点复用既有 KU；正式事件关系仍待 S6。\n"
        "- 新增1张 event 卡、1条 manifest 映射、2条候选映射；累计S4登记289组/364条映射，待登记4,551组/4,657条映射；event 为17组已登记、214组/214条成员待登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", follow_up + "## 未解决项与交接限制")

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    process_section = (
        "\n\n### S4 event follow-up：Innocent X 葬礼费用争议组（2026-10-16）\n\n"
        "- S3 将索引候选 `cand-1821`（P.csv#20，父项 Pamfili, Gianbattista / Pope Innocent X；子目 `dispute over burial of`，p.150）与正文候选 `cand-6297`（ch.6:06_CHP-6_sec_i:L48–57）并入 `sg3-event-cand-6297`。子目指向事件而非父项人物；两候选共同登记为 `units/events/innocent-x-burial-expense-dispute-1655`。\n"
        "- p.150 L56 记 Donna Olimpia 与 Prince Camillo Pamfili 拒付 Innocent X 的棺木费用，并争论安葬费用应由谁承担；原文还以地窖中的遗体作叙述。卡片将此保留为 Haskell 的报告。注5引 Pastor, XIV, p.37，该页未独立查阅；不推断最终付款者或事件解决结果。人物端点复用既有 KU，未新增 `relations.csv`。\n"
        "- 新增1张 event 卡、`ku-manifest.csv` 1条、alignment 2条成员映射及 `accepted.yml` 1条路径；字段行随后通过 `build_field_facts.py` 预检与 apply 登记。S4 累计289组/364条映射，待登记4,551组/4,657条映射；event 为17组已登记、214组/214条成员待登记；KU 总数1,308。\n"
    )
    if "### S4 event follow-up：Innocent X 葬礼费用争议组" in process_text:
        raise SystemExit("S4 Innocent X process section already exists.")
    process_text += process_section

    card_text = make_card()
    card_bytes = card_text.encode("utf-8-sig")
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "event" or len(frontmatter.get("sources", [])) != 1:
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
    print("  group=1; candidates=2; new cards=1; indexed event subentry and body event checked")
    print("  S4: 288/362 -> 289/364 groups/mappings; pending=4,551/4,657")
    print("  event: registered 16 -> 17 groups; manifest=1,307 -> 1,308")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, RESULT, KNOWLEDGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("An Innocent X S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-innocent-x-burial-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied cross-source event subentry registration and retained recovery copies.")


if __name__ == "__main__":
    main()
