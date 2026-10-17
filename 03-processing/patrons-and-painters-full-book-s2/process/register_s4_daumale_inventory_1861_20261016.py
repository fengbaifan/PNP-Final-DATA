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
CANDIDATES = TABLES / "entity-candidates.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-daumale-inventaire-1861-20261016"

KU_ID = "units/archives/daumale-inventaire-mazarin-1861"
CARD_REL = "04-knowledge/units/archives/daumale-inventaire-mazarin-1861.md"
GROUP = "archive-group-daumale-inventaire-1653-1861"
CANDIDATES_IN_GROUP = ["cand-6807", "cand-11231"]
DATE = "2026-10-16"
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb30039849q"
BNF_PERSON_URL = "https://catalogue.bnf.fr/ark:/12148/cb12375307v"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {
        "file": "07_CHP-7_sec_i.md",
        "lines": "168",
        "page": "第7章，印刷页183，注2",
        "quote": "d’Aumale, p. 8.",
        "summary": "Haskell第7章p.183注2引用d’Aumale第8页，作为交易日期定位；这里只记录出版物引注，不核验被引页内容。",
        "note": "注2；引文页未独立查阅",
    },
    {
        "file": "07_CHP-7_sec_i.md",
        "lines": "355",
        "page": "第7章，印刷页184，注2",
        "quote": "2 d’Aumale, pp. 293 ff.",
        "summary": "Haskell第7章p.184注2再次引用d’Aumale刊本pp.293 ff.；未独立查阅刊本对应页面。",
        "note": "注2；卷册页码为Haskell引用定位",
    },
    {
        "file": "21_CHP-21Bibliography.md",
        "lines": "82",
        "page": "书末参考书目",
        "quote": "d’Aumale, duc: Inventaire de tous les tneubles du Cardinal Mazarin dressé en 1653 d’après l’original, conservé dans les archives de Condé, Londres 1861.",
        "summary": (
            "Haskell的书目条目列d’Aumale, duc、题名转录、称该清单于1653年编制且据Condé档案原件刊行，并列Londres 1861。"
            "OCR题名作‘tneubles’，本卡保留原转录并依BnF目录记录采用规范拼写meubles。"
        ),
        "note": "书目条目；OCR题名异文按来源保留",
    },
]


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), bom


def encode_csv(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if bom else text).encode("utf-8")


def encode_text(path: Path, text: str) -> bytes:
    bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if bom else text).encode("utf-8")


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


def collapse(text: str) -> str:
    return " ".join(text.split())


def make_sources() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in SOURCES:
        rows.append({
            "citation": BOOK_CITATION,
            "location": f"{item['page']}；Markdown行{item['lines']}；{item['note']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; {item['page']}",
            },
        })
    rows.append({
        "citation": f"BnF Catalogue général, notice FRBNF30039849. {BNF_URL}. Accessed {DATE}.",
        "url": BNF_URL,
        "accessed_date": DATE,
        "location": "Notice FRBNF30039849；题名、责任者、出版项及刊行年份",
        "sentence_summary": (
            "BnF Catalogue général记录FRBNF30039849确认《Inventaire de tous les meubles du Cardinal Mazarin》题名及Londres: "
            "Whittingham et Wilkins, 1861出版项；用于识别1861年刊本，不等同或核验其依据的1653年清单原件。"
        ),
        "original_quotes": [],
    })
    rows.append({
        "citation": f"BnF Catalogue général, notice de personne FRBNF12375307. {BNF_PERSON_URL}. Accessed {DATE}.",
        "url": BNF_PERSON_URL,
        "accessed_date": DATE,
        "location": "Notice de personne FRBNF12375307；responsibility name on the 1861 edition linked to Henri d’Orléans",
        "sentence_summary": (
            "BnF人物权威记录将书目责任者Henri d’Orléans, duc d’Aumale与书目形式d’Aumale, duc相对应；"
            "用于刊本责任者身份映射，不扩展传记，也不代替正式关系审查。"
        ),
        "original_quotes": [],
    })
    return rows


def make_card() -> str:
    title_en = "Inventory of All the Movable Property of Cardinal Mazarin (Inventaire de tous les meubles du Cardinal Mazarin, 1861 edition)"
    frontmatter = {
        "title": f"《马萨林枢机主教全部动产清单》1861年刊本（{title_en}）",
        "name_en": title_en,
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": make_sources(),
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记《Inventaire de tous les meubles du Cardinal Mazarin》的1861年伦敦刊本。第21章书目将其列为“d’Aumale, duc”名下，称该清单于1653年编制、依据Condé档案所藏原件刊行，并记录Londres 1861；书目OCR把 *meubles* 转录为 *tneubles*，此处保留原转录而按BnF Catalogue général的FRBNF30039849规范题名。BnF记录的出版项为Londres: Whittingham et Wilkins, 1861。第7章p.183注2与p.184注2分别引用该刊本p.8及pp.293 ff.，这些页面未独立查阅。此KU是1861年印刷刊本，不是其所据1653年清单原件；原件身份单列在S3组 `archive-group-mazarin-inventory-1653`。作者形式“d’Aumale, duc”由BnF人物权威记录FRBNF12375307识别为[Henri d’Orléans, duc d’Aumale](../persons/henri-dorleans-duc-aumale.md)，人物知识元保持独立；正式作者关系留待S6审查。中文题名为项目工作译名。

**English:** This card records the 1861 London edition of *Inventaire de tous les meubles du Cardinal Mazarin*. Chapter 21’s bibliography lists it under “d’Aumale, duc,” describes the inventory as drawn up in 1653 from an original held in the Condé archives, and gives London, 1861. The bibliography OCR reads *tneubles*; that reading is preserved here, while the normalized title follows BnF Catalogue général record FRBNF30039849. The BnF imprint is Londres: Whittingham et Wilkins, 1861. Chapter 7, p. 183, note 2, and p. 184, note 2, cite pp. 8 and 293 ff. of this edition; those cited pages were not independently consulted. This KU is the 1861 printed edition, not the underlying 1653 inventory, whose identity remains in the separate S3 group `archive-group-mazarin-inventory-1653`. BnF person authority FRBNF12375307 identifies the responsibility form “d’Aumale, duc” as [Henri d’Orléans, duc d’Aumale](../persons/henri-dorleans-duc-aumale.md); the person KU remains separate, and the formal authorship relation awaits S6. The Chinese title is a project working translation.

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 规范题名 | *Inventaire de tous les meubles du Cardinal Mazarin*；书目OCR作“tneubles” | S3；S4 |
| 责任者形式 | “d’Aumale, duc”；据BnF人物权威记录映射至Henri d’Orléans人物KU | S3；S4；S5 |
| 刊本身份 | 1861年伦敦印刷刊本；与1653年所据清单原件分立 | S3；S4 |
| 出版信息 | Londres: Whittingham et Wilkins, 1861 | S4 |
| 书内引注定位 | Haskell分别引用p.8及pp.293 ff.；未独立查阅刊本对应页 | S1；S2 |
| 所据原件说明 | Haskell书目称该清单编于1653年、据Condé档案原件刊行；此说法未独立核验 | S4 |

### 身份边界

本KU表示1861年出版物，不把刊本与其所据的1653年清单原件合并。BnF书目记录支持刊本身份与出版项，不核验Haskell关于原件编制、保管沿革或所引页内容的陈述。作者形式已映射至独立人物KU；正式作者关系保持pending。

## 关系与证据

### 关系记录

尚无正式关系记录。第21章书目与BnF记录支持该责任者身份，但相应正式作者关系仍待S6审查。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the 1861 d'Aumale inventory edition archive group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    _, candidate_rows, _ = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_id = {row["candidate_id"]: row for row in alignment_rows if row.get("candidate_id") and not row.get("external_source")}
    if len(manifest_rows) != 1322 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected S4 manifest baseline or target already exists.")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")
    for cid in CANDIDATES_IN_GROUP:
        if cid not in candidate_by_id or cid not in alignment_by_id:
            raise SystemExit(f"Missing S3 candidate/alignment row: {cid}")
        if candidate_by_id[cid].get("suggested_type") != "archive":
            raise SystemExit(f"Unexpected type for {cid}.")
        row = alignment_by_id[cid]
        if row.get("decision") != "new" or row.get("ku_id") or group_of(row.get("resolution_note", "")) != GROUP:
            raise SystemExit(f"{cid} is no longer an unmapped member of {GROUP}.")
    members = sorted(
        row["candidate_id"] for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and group_of(row.get("resolution_note", "")) == GROUP
    )
    if members != sorted(CANDIDATES_IN_GROUP):
        raise SystemExit(f"Unexpected S3 group membership: {members}")
    external_rows = [
        row for row in alignment_rows
        if row.get("alignment_id") == "aln-12620" and row.get("candidate_id") == "cand-6807"
        and row.get("external_source") == "BnF Catalogue général" and row.get("external_id") == BNF_URL
        and row.get("decision") == "new"
    ]
    if len(external_rows) != 1:
        raise SystemExit("Expected the S3 BnF identity row aln-12620 for the 1861 edition.")
    person_alignment = [row for row in alignment_rows if row.get("candidate_id") == "cand-7090" and not row.get("external_source")]
    person_ku = "units/persons/henri-dorleans-duc-aumale"
    if len(person_alignment) != 1 or person_alignment[0].get("decision") != "new" or person_alignment[0].get("ku_id") != person_ku:
        raise SystemExit("cand-7090 is not mapped to the resolved Henri d’Orléans person KU.")
    if not (ROOT / "04-knowledge" / "units" / "persons" / "henri-dorleans-duc-aumale.md").is_file():
        raise SystemExit("The resolved Henri d’Orléans person card is missing.")

    for item in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        if collapse(item["quote"]) not in collapse(source_path.read_text(encoding="utf-8-sig")):
            raise SystemExit(f"Source quote mismatch: {source_path} lines {item['lines']}")
    if not (ROOT / "04-knowledge" / "tables" / "candidate-backlog.csv").is_file():
        raise SystemExit("Missing candidate backlog; preserve pending person identities there or in S3 alignment.")

    source_rows_now, source_rows_raw, _ = read_csv(TABLES / "sources.csv")
    if any(BNF_URL in (row.get("url", "") or "") for row in source_rows_raw):
        raise SystemExit("The BnF 1861-edition source is already in sources.csv; inspect before applying.")
    if not any(BNF_PERSON_URL in (row.get("url", "") or "") for row in source_rows_raw):
        raise SystemExit("The BnF person authority source was not registered with the S4 person card.")

    planned_alignment = [dict(row) for row in alignment_rows]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for cid in CANDIDATES_IN_GROUP:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "《马萨林枢机主教全部动产清单》1861年刊本",
        "name_en": "Inventory of All the Movable Property of Cardinal Mazarin (Inventaire de tous les meubles du Cardinal Mazarin, 1861 edition)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(result_text,
        "S4 已登记303组、映射394条成员候选；尚待登记4,537组、4,629条映射。",
        "S4 已登记304组、映射396条成员候选；尚待登记4,536组、4,627条映射。")
    result_text = replace_once(result_text, "1,322 KU；新组登记与待登记分类型统计见下表", "1,323 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text,
        "| archive | 79→61 | 1,258／1,220 | 42／1,178；1,195 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 43／1,177；1,193 | 0 | 18 | 745 |")
    result_text = replace_once(result_text,
        "| **合计** | **1,774→1,026** | **5,023／4,840** | **303／4,537；4,629** | **8** | **100** | **5,499** |",
        "| **合计** | **1,774→1,026** | **5,023／4,840** | **304／4,536；4,627** | **8** | **100** | **5,499** |")
    detail = (
        "### S4 archive：d’Aumale《Inventaire de tous les meubles du Cardinal Mazarin》1861年刊本（2026-10-16）\n\n"
        "- S3组 `archive-group-daumale-inventaire-1653-1861` 的 `cand-6807`（第7章注释出版物候选）与 `cand-11231`（第21章完整书目候选）"
        "共同映射至 `units/archives/daumale-inventaire-mazarin-1861`。Haskell书目OCR将 *meubles* 转录为 *tneubles*；BnF FRBNF30039849确认规范题名及Londres: Whittingham et Wilkins, 1861。\n"
        "- 本KU是1861年刊本，不与其据称依据的1653年清单原件（独立S3组 `archive-group-mazarin-inventory-1653`）合并。作者形式d’Aumale, duc已映射至独立Henri d’Orléans人物KU；正式作者关系留待S6。\n"
        "- 新增1张archive卡、manifest 1条、2条候选映射及accepted路径；S4累计304组/396条映射，待登记4,536组/4,627条映射；archive为43组已登记、1,177组/1,193条成员待登记；KU总数1,323。字段行经 `build_field_facts.py` 预检与apply登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = "### S4 archive：d’Aumale《Inventaire de tous les meubles du Cardinal Mazarin》1861年刊本"
    if heading in process_text:
        raise SystemExit("d’Aumale 1861 S4 process record already exists.")
    process_text += (
        f"\n\n{heading}（{DATE}）\n\n"
        "- S3组 `archive-group-daumale-inventaire-1653-1861` 包含 `cand-6807`（第7章第183页注2及第184页注2引文候选）和 `cand-11231`（第21章书目候选）。"
        "二者指向同一1861年刊本；BnF身份行 `aln-12620` / FRBNF30039849支持规范题名与Londres: Whittingham et Wilkins, 1861。\n"
        "- 第21章书目OCR题名作 `tneubles`，照录于source quote；卡片按BnF规范题名 *meubles* 登记并保留OCR异文。Haskell还称该刊本为1653年编制、据Condé档案原件刊行；原件未独立查阅，刊本与原件分立。\n"
        "- `cand-7090` 已在独立person组映射至 `units/persons/henri-dorleans-duc-aumale`；BnF FRBNF12375307将d’Aumale, duc识别为Henri d’Orléans（1822–1897）。作者关系仍待S6，不新增正式边。\n"
        "- 新增archive卡、manifest 1条、alignment 2条候选映射和accepted路径。S4累计304组/396条映射，待登记4,536组/4,627条映射；archive为43组已登记、1,177组/1,193条成员待登记；KU总数1,323。字段事实由 `build_field_facts.py` 登记；BnF刊本来源将由同一过程加入sources.csv。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 5:
        raise SystemExit("Generated d’Aumale card frontmatter failed validation.")
    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        ACCEPTED: encode_text(ACCEPTED, planned_accepted),
        PROCESS: encode_text(PROCESS, process_text),
        RESULT: encode_text(RESULT, result_text),
        card_path: card_text.encode("utf-8-sig"),
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print(f"  group={GROUP}; candidates=2; card={KU_ID}")
    print("  S4=303/394 -> 304/396; pending=4,536/4,627; KU=1,323")
    print("  archive=42/1,178 -> 43/1,177 groups; pending candidates=1,193")
    print("  BnF edition source will be added once by build_field_facts.py; cand-7090 is mapped to the person KU; formal relations unchanged")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A d’Aumale S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-daumale-inventaire-1861-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied d’Aumale inventory edition archive registration.")


if __name__ == "__main__":
    main()
