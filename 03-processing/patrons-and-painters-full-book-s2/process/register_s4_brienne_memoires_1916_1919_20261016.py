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
BACKLOG = TABLES / "candidate-backlog.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md"
BACKUP_SUFFIX = ".bak-s4-brienne-memoires-1916-1919-20261016"

KU_ID = "units/archives/brienne-memoires-1916-1919"
CARD_REL = "04-knowledge/units/archives/brienne-memoires-1916-1919.md"
GROUP = "archive-group-brienne-memoires-1916-1919"
CANDIDATES_IN_GROUP = ["cand-11265", "cand-1596", "cand-7071", "cand-7100"]
DATE = "2026-10-16"
BNF_URL = "https://catalogue.bnf.fr/ark:/12148/cb340193395"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = [
    {
        "file": "07_CHP-7_sec_i.md",
        "lines": "336",
        "page": "181, note 2",
        "quote": "2 Brienne, I, p. 315.",
        "summary": (
            "Haskell第7章第181页注2以“Brienne, I, p. 315”给出卷I页315的引文定位；"
            "这里只登记卷页定位，不表示已查阅该回忆录原卷或核实引文内容。"
        ),
        "note": "注2；卷I页315为Haskell所列locator",
    },
    {
        "file": "07_CHP-7_sec_i.md",
        "lines": "360",
        "page": "185, note 5",
        "quote": "5 Brienne, IH, pp. 88-90.",
        "summary": (
            "Haskell第7章第185页注5的OCR文本作“Brienne, IH, pp. 88-90”；S3依据同一三卷本书目及BnF身份记录"
            "将IH解释为卷III。原版引注及卷内页码未独立核对。"
        ),
        "note": "注5；OCR将卷号读作IH，保留原转录并注明S3解释",
    },
    {
        "file": "07_CHP-7_sec_i.md",
        "lines": "216-218",
        "page": "第7章，印刷页185–186",
        "quote": "Ah! mon pauvre ami, il faut quitter tout cela! Adieu, chers tableaux que j’ai tant aimés et qui m’ont tant coûté!",
        "summary": (
            "Haskell在第185–186页刊出以Brienne第一人称出现的告别藏品段落；本摘录证明的是Haskell正文所刊内容，"
            "不是对被引回忆录卷内原页的独立核验。"
        ),
        "note": "Haskell正文摘录；非回忆录原卷核验",
    },
    {
        "file": "22_CHP-22Index_intro.md",
        "lines": "2000-2001",
        "page": "书末索引；定位第185–186页",
        "quote": "Brienne’s account of farewell to his treasures, 185-6",
        "summary": (
            "书末索引在Brienne名下列出其告别藏品的叙述及第185–186页定位；该索引只提供书内定位，"
            "不代替对被引回忆录原页的查阅。"
        ),
        "note": "索引子目及页码定位",
    },
    {
        "file": "21_CHP-21Bibliography.md",
        "lines": "254-255",
        "page": "书末参考书目",
        "quote": "Brienne, Louis-Henri de Loménie Comte de: Mémoires, publiés par Paul Bonnefon, 3 vols., Paris 1916-19.",
        "summary": (
            "书末书目列Louis-Henri de Loménie Comte de Brienne的Mémoires、Paul Bonnefon编、三卷、巴黎1916–1919；"
            "用于出版物身份及书目字段。"
        ),
        "note": "书目条目；所列回忆录卷册未独立查阅",
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


def source_rows() -> list[dict[str, object]]:
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
        "citation": f"BnF Catalogue général, notice FRBNF34019339. {BNF_URL}. Accessed {DATE}.",
        "url": BNF_URL,
        "accessed_date": DATE,
        "location": "Notice FRBNF34019339；书目身份、责任者、卷数、出版地及出版时间",
        "sentence_summary": (
            "BnF Catalogue général的身份记录将该Mémoires列为Paul Bonnefon编、巴黎出版的三卷本，出版时间为1916–1919；"
            "此记录支持多卷出版物身份和书目对齐，不核验Haskell所引卷页或回忆录内容。"
        ),
        "original_quotes": [],
    })
    return rows


def make_card() -> str:
    title_en = "Memoirs of Louis-Henri de Loménie, Count of Brienne (Mémoires)"
    sources = source_rows()
    frontmatter = {
        "title": f"《布里埃纳伯爵回忆录》（{title_en}）",
        "name_en": title_en,
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    header = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = """## 内容

### 描述

**中文：** 本卡登记 *Mémoires* 的1916–1919年巴黎三卷本。第21章书目列Louis-Henri de Loménie, Comte de Brienne、Paul Bonnefon编、三卷、Paris 1916–19；BnF Catalogue général记录FRBNF34019339支持同一多卷出版物身份。布里埃纳本人已有[人物知识元](../persons/lomenie-de-brienne.md)，本卡表示其回忆录出版物，不与人物KU合并。Haskell第7章注释记录卷I第315页及卷III第88–90页的卷页定位；第二处原OCR写作“IH”，S3依据书目与目录身份解释为III。索引将“Brienne’s account of farewell to his treasures”定位在第185–186页。上述卷内原页与回忆录内容未独立查阅；目录记录不证明Haskell所引段落。中文题名为项目译名。[第7章 p.181、p.185](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L336、L360）[书末索引](../../../02-sources/02-Markdown/22_CHP-22Index_intro.md)（L2000–2001）[第21章书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L254–255）

**English:** This card records the three-volume Paris edition of *Mémoires* published in 1916–1919. Chapter 21’s bibliography lists Louis-Henri de Loménie, Comte de Brienne, Paul Bonnefon as editor, three volumes, and Paris 1916–19; BnF Catalogue général record FRBNF34019339 supports the identity of the same multivolume publication. Brienne has an existing [person knowledge unit](../persons/lomenie-de-brienne.md); this card represents the memoir publication and is not merged with that person unit. Chapter 7 notes give volume-and-page locators for volume I, p. 315, and volume III, pp. 88–90. The OCR for the latter reads “IH”; S3 interprets it as III on the basis of the bibliography and catalog identity. The book index locates “Brienne’s account of farewell to his treasures” at pp. 185–186. The cited volume pages and memoir contents were not independently consulted; the catalog record does not verify Haskell’s cited passages. The Chinese title is a project translation. [Chapter 7, pp. 181 and 185](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L336, L360) [book index](../../../02-sources/02-Markdown/22_CHP-22Index_intro.md) (L2000–2001) [Chapter 21 bibliography](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md) (L254–255)

### 书目身份

| 字段 | 内容 | 证据 |
|---|---|---|
| 原题 | *Mémoires*；题名按书目条目照录 | S5；S6 |
| 责任者 | Louis-Henri de Loménie, Comte de Brienne；链接至既有人物知识元 | S5；S6 |
| 编者 | Paul Bonnefon | S5；S6 |
| 版本范围 | 三卷本；Haskell的卷号作为同一出版物内的卷页定位 | S1；S2；S5；S6 |
| 出版信息 | Paris，1916–1919 | S5；S6 |
| 卷内引文定位 | 卷I p.315；卷III pp.88–90（Haskell OCR转录为“IH”）；未据原卷核验 | S1；S2；S6 |
| 正文摘录 | Haskell第185–186页刊出Brienne第一人称告别藏品段落；不代表核验回忆录原页 | S3；S4 |
| 索引定位 | “Brienne’s account of farewell to his treasures”，Haskell索引定位pp.185–186 | S5 |

### 身份边界

本KU对应1916–1919年三卷出版物身份，不表示手稿、原始回忆录文本或具体馆藏副本。卷号只作为出版物内部locator，不将不同实体卷册说成同一物理册。正文注释中的“IH”原OCR保留在来源中，III为S3的受限解释。责任者与编者的正式关系留待S6审查；书目记载及人物链接不构成正式关系边。

## 关系与证据

### 关系记录

尚无正式关系记录。作者和编者只按书目责任字段呈现；相关正式关系留待S6逐条审查。
"""
    return f"---\n{header}---\n\n{body}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the Brienne 1916–1919 memoirs archive group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment_rows, alignment_bom = read_csv(ALIGNMENT)
    manifest_fields, manifest_rows, manifest_bom = read_csv(MANIFEST)
    backlog_fields, backlog_rows, backlog_bom = read_csv(BACKLOG)
    _, candidate_rows, _ = read_csv(CANDIDATES)
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    candidate_alignment = {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }

    if len(manifest_rows) != 1320 or any(row.get("ku_id") == KU_ID for row in manifest_rows):
        raise SystemExit("Unexpected S4 manifest baseline or target already exists.")
    if len(backlog_rows) != 2 or any(row.get("backlog_id") == "bl-0003" for row in backlog_rows):
        raise SystemExit("Unexpected candidate-backlog baseline or Brienne editor endpoint already queued.")
    card_path = ROOT / CARD_REL
    if card_path.exists():
        raise SystemExit(f"S4 card already exists: {CARD_REL}")
    for cid in CANDIDATES_IN_GROUP:
        if cid not in candidate_by_id or cid not in candidate_alignment:
            raise SystemExit(f"Missing S3 candidate/alignment row: {cid}")
        if candidate_by_id[cid].get("suggested_type") != "archive":
            raise SystemExit(f"Unexpected type for {cid}.")
        row = candidate_alignment[cid]
        if row.get("decision") != "new" or row.get("ku_id") or group_of(row.get("resolution_note", "")) != GROUP:
            raise SystemExit(f"{cid} is no longer an unmapped member of {GROUP}.")
    actual_group_members = sorted(
        row["candidate_id"] for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    )
    if actual_group_members != sorted(CANDIDATES_IN_GROUP):
        raise SystemExit(f"Unexpected S3 group membership: {actual_group_members}")

    external_rows = [
        row for row in alignment_rows
        if row.get("alignment_id") == "aln-12622" and row.get("candidate_id") == "cand-7100"
        and row.get("external_source") == "BnF Catalogue général"
        and row.get("external_id") == BNF_URL and row.get("decision") == "new"
    ]
    if len(external_rows) != 1:
        raise SystemExit("Expected the S3 BnF identity row aln-12622.")

    for item in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        source_text = source_path.read_text(encoding="utf-8-sig")
        if collapse(item["quote"]) not in collapse(source_text):
            raise SystemExit(f"Source quote mismatch: {source_path} lines {item['lines']}")
    sources_text = collapse((ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md").read_text(encoding="utf-8-sig"))
    if "Brienne, Louis-Henri de Loménie Comte de: Mémoires, publiés par Paul Bonnefon, 3 vols., Paris 1916-19." not in sources_text:
        raise SystemExit("Brienne bibliography identity text is missing from the current source.")
    if not (ROOT / "04-knowledge" / "units" / "persons" / "lomenie-de-brienne.md").is_file():
        raise SystemExit("Expected existing Brienne person KU for a distinct identity link.")

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
        "canonical_name": "《布里埃纳伯爵回忆录》",
        "name_en": "Memoirs of Louis-Henri de Loménie, Count of Brienne (Mémoires)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_backlog = list(backlog_rows)
    planned_backlog.append({
        "backlog_id": "bl-0003",
        "canonical_name": "Paul Bonnefon",
        "suggested_type": "person",
        "status": "pending",
        "source_id": "haskell-1980-rev-ed",
        "source_ref": "chp-21:21_CHP-21Bibliography:l243-293#L254",
        "statement_id": "st-chp21-bib-l243-293-entry-07",
        "endpoint_role": f"editor of {KU_ID}",
        "candidate_id": "",
        "ku_id": "",
        "decision_note": (
            "The source bibliography names Paul Bonnefon as the editor of this three-volume Mémoires edition. "
            "No matching person KU or S3 candidate was found. Queue this named endpoint for S1→S3→S4 processing; "
            "do not infer biography or register an editor relation before identity alignment."
        ),
        "process_ref": "S3-S4-full-book-2026-10-16",
    })

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
        "S4 已登记301组、映射389条成员候选；尚待登记4,538组、4,633条映射。",
        "S4 已登记302组、映射393条成员候选；尚待登记4,537组、4,629条映射。",
    )
    result_text = replace_once(
        result_text,
        "1,320 KU；新组登记与待登记分类型统计见下表",
        "1,321 KU；新组登记与待登记分类型统计见下表",
    )
    result_text = replace_once(
        result_text,
        "| archive | 79→61 | 1,258／1,220 | 41／1,179；1,199 | 0 | 18 | 745 |",
        "| archive | 79→61 | 1,258／1,220 | 42／1,178；1,195 | 0 | 18 | 745 |",
    )
    result_text = replace_once(
        result_text,
        "| **合计** | **1,774→1,026** | **5,022／4,839** | **301／4,538；4,633** | **8** | **100** | **5,500** |",
        "| **合计** | **1,774→1,026** | **5,022／4,839** | **302／4,537；4,629** | **8** | **100** | **5,500** |",
    )
    result_detail = (
        "### S4 archive：Brienne《Mémoires》1916–1919年三卷本（2026-10-16）\n\n"
        "- S3组 `archive-group-brienne-memoires-1916-1919` 包含 `cand-11265`（第21章完整书目条目）、`cand-1596`（M.csv#135，索引告别藏品条目，pp.185–186）、"
        "`cand-7071`（第7章卷I引注定位）及 `cand-7100`（第7章卷III引注定位），统一映射至 `units/archives/brienne-memoires-1916-1919`。\n"
        "- 第21章书目列Louis-Henri de Loménie Comte de Brienne、Paul Bonnefon编、3卷、Paris 1916–19；BnF FRBNF34019339支持同一三卷本身份。"
        "Haskell脚注列卷I p.315及卷III pp.88–90，后者OCR作“IH”，按S3身份裁决解释为III；回忆录原卷页未独立查阅。"
        "已有Brienne人物KU作为独立身份入口保留，不创建作者或编者正式关系；相关关系留待S6。\n"
        "- 书目编者Paul Bonnefon尚无对应person KU；已新增待办 `bl-0003`，按S1→S3→S4处理后再审编辑关系，本轮不臆造人物身份或正式关系。\n"
        "- 新增1张archive卡、manifest 1条、4条候选映射、accepted路径和1条person端点待办；S4累计302组/393条映射，待登记4,537组/4,629条映射；"
        "archive为42组已登记、1,178组/1,195条成员待登记；KU总数1,321。字段行经 `build_field_facts.py` 预检与apply登记。\n\n"
    )
    result_text = replace_once(result_text, "## 未解决项与交接限制", result_detail + "## 未解决项与交接限制")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_heading = "### S4 archive：Brienne《Mémoires》1916–1919年三卷本"
    if process_heading in process_text:
        raise SystemExit("Brienne S4 process record already exists.")
    process_text += (
        f"\n\n{process_heading}（{DATE}）\n\n"
        "- S3身份组 `archive-group-brienne-memoires-1916-1919` 包含 `cand-11265`（第21章完整书目条目）、`cand-1596`（M.csv#135，索引子目告别藏品，pp.185–186）、"
        "`cand-7071`（第7章第181页注2，Brienne, I, p.315）和 `cand-7100`（第7章第185页注5，OCR作Brienne, IH, pp.88–90）。"
        "21章书目列Louis-Henri de Loménie Comte de Brienne、Paul Bonnefon编、3 vols.、Paris 1916–19；BnF FRBNF34019339记录同一三卷本。\n"
        "- 三条候选共同登记至 `units/archives/brienne-memoires-1916-1919`。卷I和卷III是多卷出版物内部的locator，不是同一实体卷册；索引页码是Haskell书内定位。"
        "S3以书目及BnF身份将OCR `IH` 解释为III。没有对回忆录原卷的引文页或内容作独立查验，目录记录只支持出版物身份。\n"
        "- 既有人物卡 `units/persons/lomenie-de-brienne` 仍与文献KU分立；作者与编者仅按书目责任字段列出，正式关系留待S6。没有新增relations.csv边。\n"
        "- Paul Bonnefon由第21章书目记为编者但尚无person KU，已登记候选待办`bl-0003`（status=pending），按S1→S3→S4处理；编辑关系端点补齐前保持pending。\n"
        "- 新增archive卡、manifest 1条、alignment 4条候选映射、accepted路径及1条person端点待办；字段表将由 `build_field_facts.py` 登记source-backed行及BnF来源。"
        "S4累计302组/393条映射，待登记4,537组/4,629条映射；archive为42组已登记、1,178组/1,195条成员待登记；KU总数1,321。\n"
    )

    card_text = make_card()
    frontmatter = yaml.safe_load(card_text.split("---\n", 2)[1])
    if frontmatter.get("type") != "archive" or len(frontmatter.get("sources", [])) != 6:
        raise SystemExit("Generated Brienne card frontmatter failed validation.")
    updates = {
        ALIGNMENT: encode_csv(alignment_fields, planned_alignment, alignment_bom),
        MANIFEST: encode_csv(manifest_fields, planned_manifest, manifest_bom),
        BACKLOG: encode_csv(backlog_fields, planned_backlog, backlog_bom),
        ACCEPTED: encode_text(ACCEPTED, planned_accepted),
        PROCESS: encode_text(PROCESS, process_text),
        RESULT: encode_text(RESULT, result_text),
        card_path: card_text.encode("utf-8-sig"),
    }
    print("DRY-RUN" if args.dry_run else "APPLY")
    for path, content in updates.items():
        old_hash = digest(path.read_bytes()) if path.exists() else "absent"
        print(f"  {path.relative_to(ROOT)}: {old_hash} -> {digest(content)}")
    print(f"  group={GROUP}; candidates=4; card={KU_ID}")
    print("  S4=301/389 -> 302/393; pending=4,537/4,629; KU=1,321")
    print("  archive=41/1,179 -> 42/1,178 groups; pending candidates=1,195")
    print("  BnF identity source will be added once by build_field_facts.py; formal relations unchanged")
    if args.dry_run:
        print("Dry-run passed; no files changed.")
        return

    backup_targets = [ALIGNMENT, MANIFEST, BACKLOG, ACCEPTED, PROCESS, RESULT]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in backup_targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A Brienne S4 recovery copy already exists; inspect before applying.")
    for original, backup in zip(backup_targets, backups, strict=True):
        shutil.copy2(original, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s4-brienne-memoires-1916-1919-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied Brienne Mémoires archive registration.")


if __name__ == "__main__":
    main()
