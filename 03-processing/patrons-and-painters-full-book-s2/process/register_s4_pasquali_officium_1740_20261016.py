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
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
DATE = "2026-10-16"

GROUP = "archive-group-pasquali-officium-1740"
CID = "cand-1849"
KU_ID = "units/archives/beatae-mariae-virginis-officium-1740"
CARD_REL = "04-knowledge/units/archives/beatae-mariae-virginis-officium-1740.md"
BACKUP_SUFFIX = ".bak-s4-pasquali-officium-1740-20261016"
BODY_FILE = "13_CHP-13_intro.md"
INDEX_FILE = "22_CHP-22Index_intro.md"
SBN_URL = "https://opac.bibliotecauniversitaria.pi.it/bid/PUVE008510"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BODY_QUOTE = "the Beatae Mariae Virginis Officium, published in 1740"
INDEX_QUOTE = "Beatae Mariae Virginis Officium, 337 eq"
SBN_QUOTE = (
    "Titolo | Beatae Mariae Virginis officium\n"
    "Pubblicazione | Venetiis : Apud Jo. Baptistam Pasquali, 1740"
)


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), bom


def encode_csv(fields, rows, bom):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if bom else text).encode("utf-8")


def encode_text(path, text):
    bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    return ("\ufeff" + text if bom else text).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def collapse(text):
    return " ".join(text.split())


def group_of(note):
    match = re.search(r"group=([^;|\s]+)", note)
    return match.group(1) if match else ""


def make_card():
    title_zh = "《圣母玛利亚日课》1740年刊本"
    title_en = "Office of the Blessed Virgin Mary (Beatae Mariae Virginis Officium, 1740 edition)"
    body_link = f"../../../02-sources/02-Markdown/{BODY_FILE}"
    index_link = f"../../../02-sources/02-Markdown/{INDEX_FILE}"
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第13章，印刷页337；Markdown行57；Haskell称该书于1740年出版",
            "sentence_summary": (
                "Haskell以题名指称一部1740年出版的宗教插图书；同一句还叙述Pasquali与Piazzetta的插图联系，"
                "委托及艺术评价仍作为书内报告，不在此据以确认关系。"
            ),
            "original_quotes": [{"source_span": "line 57", "text": BODY_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{BODY_FILE}",
                "source_span": "line 57; print p. 337",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书末索引；Markdown行2308；Pasquali名下列出题名及p.337",
            "sentence_summary": "书末索引列出Beatae Mariae Virginis Officium及第337页定位，与正文题名相符。",
            "original_quotes": [{"source_span": "line 2308", "text": INDEX_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{INDEX_FILE}",
                "source_span": "line 2308; index locator p. 337",
            },
        },
        {
            "citation": f"OPAC SBN, Polo SBN Biblioteca Universitaria di Pisa, record PUVE008510. {SBN_URL}. Accessed {DATE}.",
            "url": SBN_URL,
            "location": "记录PUVE008510：bibliographic level、material type、title及publication fields（web lines 42–46）；publisher authority name（lines 62、74–77）",
            "accessed": DATE,
            "sentence_summary": (
                "OPAC SBN将该题名著录为印刷单行本，并记录出版地Venetiis、出版者Apud Jo. Baptistam Pasquali及1740年；"
                "该书目记录用于身份与刊本信息，不验证Haskell的委托、资助或艺术评价陈述。"
            ),
            "original_quotes": [{"source_span": "record fields, lines 45–46", "text": SBN_QUOTE}],
        },
    ]
    frontmatter = {
        "title": f"{title_zh}（{title_en}）",
        "name_en": title_en,
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** 本卡登记拉丁文题名 *Beatae Mariae Virginis Officium* 的1740年威尼斯刊本。中文题名“圣母玛利亚日课”为项目描述性暂译，不声称是原刊自题。Haskell第13章p.337以该题名指称一部1740年出版的宗教插图书；OPAC SBN记录PUVE008510将同题名著录为印刷单行本，出版项为Venetiis: Apud Jo. Baptistam Pasquali, 1740。该目录记录支持文献身份及刊本书目项，不核实Haskell关于插图委托、资助人Caime或艺术评价的叙述；本轮未独立查阅原刊。出版者入口：[Giovanni Battista Pasquali](../persons/pasquali.md)。[第13章 p.337]({body_link})（L57）[书末索引]({index_link})（L2308）

**English:** This card records the 1740 Venice edition under the Latin title *Beatae Mariae Virginis Officium*. The Chinese title “圣母玛利亚日课” is a descriptive project translation, not a claimed title of the original publication. Chapter 13, p. 337, uses the title for a religious illustrated book published in 1740; OPAC SBN record PUVE008510 catalogs the same title as a printed monograph and gives the imprint Venetiis: Apud Jo. Baptistam Pasquali, 1740. The catalog record supports the publication identity and bibliographic imprint; it does not verify Haskell’s statements about illustration commissions, the financier Caime, or artistic evaluation. The printed volume was not independently consulted. Publisher entry: [Giovanni Battista Pasquali](../persons/pasquali.md). [Chapter 13, p. 337]({body_link}) (L57) [book index]({index_link}) (L2308)

### 文献身份与书内记载

| 字段 | 内容 | 证据 |
|---|---|---|
| 原题 | *Beatae Mariae Virginis Officium*；“圣母玛利亚日课”为项目描述性暂译 | S1；S2；S3 |
| 文献类型 | 印刷单行本（OPAC SBN著录）；Haskell称其为一部小书 | S1；S3 |
| 出版信息 | 威尼斯（Venetiis），1740；OPAC SBN著录出版项“Apud Jo. Baptistam Pasquali” | S1；S3 |
| 出版者入口 | Giambattista Pasquali；链接至既有人物卡[Giovanni Battista Pasquali](../persons/pasquali.md) | S3 |

## 关系与证据

当前没有登记正式关系。Haskell关于Pasquali、Piazzetta、委托及资助的书内叙述仍须在关系阶段逐项审查；OPAC的出版者著录与本卡人物入口本身不构成已登记的正式关系。原刊未独立查阅。
"""
    return f"---\n{header}---\n\n{body}"


def main():
    parser = argparse.ArgumentParser(description="Register the 1740 Beatae Mariae Virginis Officium edition in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    _, candidates, _ = read_csv(CANDIDATES)
    _, source_rows, _ = read_csv(SOURCES)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    target_rows = [
        row for row in alignment_rows
        if row.get("candidate_id") == CID and not row.get("external_source")
    ]
    if len(manifest_rows) != 1319 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected S4 baseline or target already registered.")
    if len(target_rows) != 1 or CID not in candidate_by_id:
        raise SystemExit("Expected one candidate decision row and one S3 candidate.")
    row = target_rows[0]
    if candidate_by_id[CID].get("suggested_type") != "archive":
        raise SystemExit(f"Unexpected type for {CID}.")
    if row.get("decision") != "new" or row.get("ku_id") or group_of(row.get("resolution_note", "")) != GROUP:
        raise SystemExit(f"{CID} is no longer an unmapped member of {GROUP}.")
    group_members = {
        r["candidate_id"] for r in alignment_rows
        if r.get("candidate_id") and not r.get("external_source")
        and r.get("decision") == "new" and group_of(r.get("resolution_note", "")) == GROUP
    }
    if group_members != {CID}:
        raise SystemExit(f"Unexpected S3 group membership: {sorted(group_members)}")
    external_rows = [
        r for r in alignment_rows
        if r.get("candidate_id") == CID and r.get("external_source")
        and r.get("external_id") == "PUVE008510" and r.get("decision") == "new"
    ]
    if not external_rows:
        raise SystemExit("The S3 OPAC SBN identity row is missing.")
    if any(SBN_URL in str(r.get("url", "")) for r in source_rows):
        raise SystemExit("The OPAC SBN URL is already registered; inspect before continuing.")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")
    if not (ROOT / "04-knowledge" / "units" / "persons" / "pasquali.md").exists():
        raise SystemExit("The linked Giambattista Pasquali person card is missing.")

    body_source = collapse((ROOT / "02-sources" / "02-Markdown" / BODY_FILE).read_text(encoding="utf-8-sig"))
    index_source = collapse((ROOT / "02-sources" / "02-Markdown" / INDEX_FILE).read_text(encoding="utf-8-sig"))
    if collapse(BODY_QUOTE) not in body_source:
        raise SystemExit("The chapter quote does not match the current source file.")
    if INDEX_QUOTE not in index_source:
        raise SystemExit("The index quote does not match the current source file.")

    planned_alignment = [dict(r) for r in alignment_rows]
    planned_target = next(r for r in planned_alignment
                          if r.get("candidate_id") == CID and not r.get("external_source"))
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest_rows)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "《圣母玛利亚日课》1740年刊本",
        "name_en": "Office of the Blessed Virgin Mary (Beatae Mariae Virginis Officium, 1740 edition)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda r: r["ku_id"])

    accepted_lines = ACCEPTED.read_text(encoding="utf-8-sig").splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in accepted_lines):
        raise SystemExit("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text = replace_once(
        result_text,
        "S4 已登记300组、映射388条成员候选；尚待登记4,539组、4,633条映射。",
        "S4 已登记301组、映射389条成员候选；尚待登记4,538组、4,632条映射。",
    )
    result_text = replace_once(result_text, "1,319 KU；新组登记与待登记分类型统计见下表",
                               "1,320 KU；新组登记与待登记分类型统计见下表")
    result_text = replace_once(
        result_text,
        "| archive | 79→61 | 1,258／1,220 | 40／1,180；1,199 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 41／1,179；1,198 | 0 | 18 | 745 |",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **300／4,539；4,633** | **8** | **100** | **5,501** |",
        "| **合计** | **1,774→1,026** | **5,021／4,839** | **301／4,538；4,632** | **8** | **100** | **5,501** |",
    )
    detail = (
        "### S4 archive：*Beatae Mariae Virginis Officium* 1740年刊本（2026-10-16）\n\n"
        "- S3组 archive-group-pasquali-officium-1740 仅含索引候选 cand-1849（P.csv#49，p.337）。Haskell第13章p.337以 Beatae Mariae Virginis Officium 指称一部1740年出版的宗教插图书；索引子目同题名并列p.337。\n"
        "- OPAC SBN记录PUVE008510将同题名著录为印刷单行本，出版项为Venetiis: Apud Jo. Baptistam Pasquali, 1740；据此登记1740年刊本，中文题名《圣母玛利亚日课》为描述性暂译。SBN身份信息不核验Haskell关于插图、Caime资助、委托或艺术评价的叙述。出版者Giambattista Pasquali复用既有人物卡入口，但本轮不新增正式关系。\n"
        "- cand-1848 Dactylografa Smithiana、cand-1851 Goldoni edition及cand-12144所指Pasquali一般出版物集合均保持独立。新增1张archive卡、manifest 1条、候选映射1条及accepted路径；S4累计301组/389条映射，待登记4,538组/4,632条映射；archive为41组已登记、1,179组/1,198条成员待登记；KU总数1,320。字段行经 build_field_facts.py 预检与apply登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = "### S4 archive：*Beatae Mariae Virginis Officium* 1740年刊本"
    if heading in process_text:
        raise SystemExit("Pasquali Officium S4 process record already exists.")
    process_text += (
        f"\n\n{heading}（2026-10-16）\n\n"
        "- S3组 archive-group-pasquali-officium-1740 仅有 cand-1849（P.csv#49，索引子目 Beatae Mariae Virginis Officium，p.337）。第13章p.337正文直接给出题名与1740年刊行年份；书末索引在Pasquali名下列出题名和p.337。\n"
        "- S3外部身份行 aln-12618 记录OPAC SBN（Biblioteca Universitaria di Pisa），record PUVE008510。目录将该题名著录为printed monograph，出版项为Venetiis: Apud Jo. Baptistam Pasquali, 1740。它支持题名、出版地、出版者和年份的书目身份；本轮仅登记edition层级，不把目录的具体馆藏副本、插图者、engraver或印数资料扩展为本KU事实。\n"
        "- Haskell关于Piazzetta提供插图、商人Caime委托及资助、该书艺术评价等书内叙述仍各待关系/证据阶段核验；本轮未新增正式关系。与 cand-1848 Dactylografa Smithiana、cand-1851 Goldoni edition及 cand-12144 一般出版物集合分开。\n"
        "- 新增 units/archives/beatae-mariae-virginis-officium-1740 卡、manifest 1条、cand-1849 映射和accepted路径。S4累计301组/389条映射，待登记4,538组/4,632条映射；archive为41组已登记、1,179组/1,198条成员待登记；KU总数1,320。字段行经 build_field_facts.py 预检与apply登记；OPAC来源由字段表生成过程加入sources.csv，未重复其他已登记来源。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 3:
        raise SystemExit("Generated card frontmatter failed validation.")
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
    print(f"  group={GROUP}; candidates=1; title/year=Beatae Mariae Virginis Officium / 1740")
    print("  S4=300/388 -> 301/389; pending=4,538/4,632; KU=1,320")
    print("  archive=40/1,180 -> 41/1,179 groups; pending candidates=1,198")
    print("  OPAC SBN source will be added once by build_field_facts.py; formal relations unchanged")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Pasquali Officium S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-pasquali-officium-1740-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Pasquali Officium archive registration.")


if __name__ == "__main__":
    main()

