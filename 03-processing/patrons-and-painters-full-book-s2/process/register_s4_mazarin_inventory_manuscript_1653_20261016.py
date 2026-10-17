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
SOURCES = TABLES / "sources.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-mazarin-inventory-1653-20261016"

KU_ID = "units/archives/mazarin-inventory-manuscript-1653"
CARD_REL = "04-knowledge/units/archives/mazarin-inventory-manuscript-1653.md"
GROUP = "archive-group-mazarin-inventory-1653"
CANDIDATES_IN_GROUP = ["cand-1597", "cand-6814"]
DATE = "2026-10-16"
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb30039849q"
BNF_CITATION = f"BnF Catalogue général, notice FRBNF30039849. {BNF_URL}. Accessed {DATE}."
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES_FOR_CARD = [
    {
        "file": "07_CHP-7_sec_i.md",
        "lines": "172",
        "page": "第7章，印刷页184，正文",
        "quote": "An inventory was at once drawn up and from it we can gauge the extent ofhis collecting and patronage during the previous twenty years.2",
        "summary": "Haskell称1653年马萨林恢复权力后立即编制清单，并以此估量此前二十年的收藏与赞助范围；这是Haskell的叙述，不是本卡对原件的独立核验。",
        "note": "正文叙述；OCR原样保留",
    },
    {
        "file": "07_CHP-7_sec_i.md",
        "lines": "355",
        "page": "第7章，印刷页184，注2",
        "quote": "2 d’Aumale, pp. 293 ff. -",
        "summary": "注2将正文清单定位到d’Aumale刊本pp.293 ff.；所引刊本页面未独立查阅。",
        "note": "书内引注；引文页未独立查阅",
    },
    {
        "file": "21_CHP-21Bibliography.md",
        "lines": "82",
        "page": "第21章书目",
        "quote": "d’Aumale, duc: Inventaire de tous les tneubles du Cardinal Mazarin dressé en 1653 d’après l’original, conservé dans les archives de Condé, Londres 1861.",
        "summary": "书目将清单描述为1653年编制、据Condé原件刊行并于伦敦出版的1861年刊本；OCR将meubles转录为tneubles，本卡保留异文。",
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


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def group_of(note: str) -> str:
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def collapse(text: str) -> str:
    return " ".join(text.split())


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def make_sources() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in SOURCES_FOR_CARD:
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
        "citation": BNF_CITATION,
        "url": BNF_URL,
        "accessed_date": DATE,
        "location": "FRBNF30039849；题名、1653年日期及刊本据Condé原件刊行的书目说明",
        "sentence_summary": (
            "BnF书目记录确认《Inventaire de tous les meubles du Cardinal Mazarin》的1861年刊本，并将其说明为据Condé保存的原件刊行。"
            "本记录只用于支持刊本与其所据原件的身份区分，不据此声称已经查阅手稿或所引页。"
        ),
        "original_quotes": [],
    })
    return rows


def make_card() -> str:
    title_en = "Inventory of All the Movable Property of Cardinal Mazarin (1653 original manuscript)"
    frontmatter = {
        "title": f"《马萨林枢机主教全部动产清单》（1653年原件）（{title_en}）",
        "name_en": title_en,
        "type": "archive",
        "sub_type": "manuscript",
        "evidence_status": "source_backed",
        "sources": make_sources(),
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记Haskell第7章p.184所称、并由第21章书目及BnF书目记录指认为1861年刊本所据原件的1653年清单。书目OCR题名作 *tneubles*，此处保留原转录；工作题名据规范拼写 *meubles*。Haskell称清单用于估量马萨林此前二十年的收藏与赞助范围；这是原书叙述，未由本卡独立核验。注2引d’Aumale刊本pp.293 ff.，对应页面与手稿均未独立查阅。本KU表示清单原件，不是[1861年刊本](daumale-inventaire-mazarin-1861.md)，也不与注3另引的1661年清单合并。正式书目关系留待S6审查。

**English:** This unit records the 1653 inventory named on p. 184 of Haskell’s Chapter 7 and identified by Chapter 21’s bibliography and the BnF bibliographic record as the original used for the 1861 edition. The bibliography OCR reads *tneubles*; that transcription is retained, while the working title follows the normalized spelling *meubles*. Haskell says the inventory was used to gauge Mazarin’s collecting and patronage over the preceding twenty years; this remains Haskell’s account and has not been independently verified here. Note 2 cites pp. 293 ff. of d’Aumale’s edition; neither those pages nor the manuscript were independently consulted. This KU denotes the inventory original, not the [1861 printed edition](daumale-inventaire-mazarin-1861.md), and not the separate 1661 inventory cited in note 3. The formal bibliographic relationship awaits S6 review.

### 文献身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 文献类型 | 1653年清单原件；此身份由Haskell书内叙述、书目以及1861年刊本的目录说明共同定位，原件未直接查阅 | S1；S3；S4 |
| 题名 | *Inventaire de tous les meubles du Cardinal Mazarin*；Haskell书目OCR作 *tneubles*，规范拼写据BnF书目记录 | S3；S4 |
| 日期 | 1653年；Haskell正文将编制时间置于马萨林当年恢复权力之后，刊本题名亦称清单于1653年编制 | S1；S3；S4 |
| 书内引注 | 第7章p.184注2引d’Aumale刊本pp.293 ff.；引文页未独立查阅 | S2 |
| 原书所述用途 | Haskell称该清单可用于估量马萨林此前二十年的收藏与赞助范围；保留为Haskell的陈述 | S1 |
| 版本边界 | 与1861年印刷刊本分立；BnF目录称刊本据Condé原件刊行；正式版本关系待关系阶段审查 | S2；S3；S4 |

### 身份边界

本卡的对象身份限于被书目与目录记录指称的1653年原件。现有来源足以将它与1861年刊本、1661年另一清单分开，但不足以证明手稿内容、完整形成过程或其后续保管沿革。S2关系候选保留在原书断言表，正式关系未在S6审查前登记。

## 关系与证据

### 关系记录

尚无正式关系边。Haskell的原书断言 `st-chp7-p184-i04` 保留该清单与其收藏／赞助叙述的语境；它不单独证明原件编制者或所有权关系。1861年刊本为独立KU，原件与刊本的正式关系待S6审查。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the 1653 Mazarin inventory manuscript group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    _, candidate_rows, _ = read_csv(CANDIDATES)
    _, source_rows, _ = read_csv(SOURCES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }
    if len(manifest_rows) != 1323 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
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
    if not any(
        row.get("alignment_id") == "aln-12621" and row.get("candidate_id") == "cand-6814"
        and row.get("external_source") == "BnF Catalogue général" and row.get("external_id") == BNF_URL
        and row.get("decision") == "new"
        for row in alignment_rows
    ):
        raise SystemExit("Expected the S3 BnF identity row aln-12621 for the manuscript group.")
    person_alignment = [row for row in alignment_rows if row.get("candidate_id") == "cand-7090" and not row.get("external_source")]
    person_ku = "units/persons/henri-dorleans-duc-aumale"
    if len(person_alignment) != 1 or person_alignment[0].get("ku_id") != person_ku:
        raise SystemExit("The separate d’Aumale person KU mapping is missing.")

    source_texts = {
        item["file"]: (ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig")
        for item in SOURCES_FOR_CARD
    }
    for item in SOURCES_FOR_CARD:
        if collapse(item["quote"]) not in collapse(source_texts[item["file"]]):
            raise SystemExit(f"Source quote mismatch: {item['file']} lines {item['lines']}")
    if not any(row.get("url") == BNF_URL for row in source_rows):
        raise SystemExit("The BnF publication record is not registered in sources.csv.")

    planned_alignment = [dict(row) for row in alignment_rows]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES_IN_GROUP:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "《马萨林枢机主教全部动产清单》（1653年原件）",
        "name_en": "Inventory of All the Movable Property of Cardinal Mazarin (1653 original manuscript)",
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
        "S4 已登记304组、映射396条成员候选；尚待登记4,536组、4,627条映射。",
        "S4 已登记305组、映射398条成员候选；尚待登记4,535组、4,625条映射。")
    result_text = replace_once(result_text, "1,323 KU；新组登记与待登记分类型统计见下表", "1,324 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(result_text,
        "| archive | 79→61 | 1,258／1,220 | 43／1,177；1,193 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 44／1,176；1,191 | 0 | 18 | 745 |")
    result_text = replace_once(result_text,
        "| **合计** | **1,774→1,026** | **5,023／4,840** | **304／4,536；4,627** | **8** | **100** | **5,499** |",
        "| **合计** | **1,774→1,026** | **5,023／4,840** | **305／4,535；4,625** | **8** | **100** | **5,499** |")
    detail = (
        "### S4 archive：马萨林1653年清单原件（2026-10-16）\n\n"
        "- S3组 `archive-group-mazarin-inventory-1653` 的 `cand-6814`（第7章p.184正文候选）与 `cand-1597`（M.csv#136，p.184索引子目）"
        "共同映射至 `units/archives/mazarin-inventory-manuscript-1653`。第21章书目和BnF FRBNF30039849将其与据Condé原件刊行的1861年印本联系起来；原件未直接查阅。\n"
        "- 1861年刊本保持独立KU `units/archives/daumale-inventaire-mazarin-1861`；第7章注3所引1661年清单候选 `cand-7091` 仍为另一对象。注2所引刊本pp.293 ff.未独立核读，正式版本关系留待S6。\n"
        "- 新增1张archive卡、manifest 1条、2条候选映射及accepted路径；S4累计305组/398条映射，待登记4,535组/4,625条映射；archive为44组已登记、1,176组/1,191条成员待登记；KU总数1,324。字段事实由 `build_field_facts.py` 预检与apply登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = "### S4 archive：马萨林1653年清单原件"
    if heading in process_text:
        raise SystemExit("1653 manuscript S4 process record already exists.")
    process_text += (
        f"\n\n{heading}（{DATE}）\n\n"
        "- S3组 `archive-group-mazarin-inventory-1653` 包含正文候选 `cand-6814` 与索引定位候选 `cand-1597`。正文statement `st-chp7-p184-i04` 锚定“An inventory was at once drawn up”；索引子目 `M.csv#136` 的 `inventory of collection` 指向同页。注2与第21章书目指向d’Aumale 1861年刊本，BnF FRBNF30039849说明该刊本据Condé原件刊行；S3外部身份行 `aln-12621` 记录目录身份比较。\n"
        "- 两候选共同登记为1653年原件KU `units/archives/mazarin-inventory-manuscript-1653`，与1861年印刷刊本 `units/archives/daumale-inventaire-mazarin-1861` 分开。第7章注3另引1661年清单 `cand-7091`，不与本组合并。Haskell所引pp.293 ff.及原件均未独立查阅；“用于估量收藏与赞助”保留为Haskell叙述，不写成独立核实的历史事实。\n"
        "- 卡片不创建正式作者、所有权或版本关系；原书关系候选继续留在S2断言表，1861年刊本与原件的正式关系留待S6。新增archive卡、manifest 1条、2条候选映射和accepted路径。`build_field_facts.py`将按预检结果登记字段行；BnF来源已在sources.csv登记。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 4:
        raise SystemExit("Generated manuscript card frontmatter failed validation.")
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
    print("  S4=304/396 -> 305/398; pending=4,535/4,625; KU=1,324")
    print("  archive=43/1,177 -> 44/1,176 groups; pending candidates=1,191")
    print("  field facts will be extracted in the next preview/apply step; formal relations unchanged")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT, TABLES / "enrichment.jsonl", SOURCES]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A recovery copy for this S4 registration already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-mazarin-inventory-1653-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied 1653 Mazarin inventory manuscript archive registration.")


if __name__ == "__main__":
    main()
