from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"
BOOK_CANDIDATE = "cand-7087"
ITEM_CANDIDATE = "cand-7091"
BOOK_GROUP = "archive-group-793f3c145dfa"
ITEM_GROUP = "archive-group-fd76703203a6"
BOOK_KU = "units/archives/les-richesses-du-palais-mazarin-1885"
ITEM_KU = "units/archives/mazarin-inventory-1661-de-cosnac-item-1240"
BOOK_REL = "04-knowledge/units/archives/les-richesses-du-palais-mazarin-1885.md"
ITEM_REL = "04-knowledge/units/archives/mazarin-inventory-1661-de-cosnac-item-1240.md"
BOOK_PATH = ROOT / BOOK_REL
ITEM_PATH = ROOT / ITEM_REL
SMITHSONIAN_URL = "https://www.si.edu/object/siris_sil_278901"
PERSEE_URL = "https://www.persee.fr/authority/727409"
BACKUP_SUFFIX = ".bak-s4-cosnac-1885-mazarin-inventory-1661-20261016"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SMITHSONIAN_CITATION = f"Smithsonian Libraries and Archives, *Les richesses du Palais Mazarin*, record siris_sil_278901. {SMITHSONIAN_URL}. Accessed {DATE}."
PERSEE_CITATION = f"Persée author bibliography, Gabriel-Jules de Cosnac, authority record 727409. {PERSEE_URL}. Accessed {DATE}."


BOOK_SOURCES = [
    {
        "citation": BOOK_CITATION,
        "location": "第21章书末参考书目，印刷页420；Markdown L380",
        "sentence_summary": "Haskell将Les richesses du Palais Mazarin列于Comte Gabriel-Jules de Cosnac名下，出版项为Paris 1885。",
        "original_quotes": [{
            "source_span": "line 380; printed bibliography p. 420",
            "text": "Cosnac, Comte Gabriel-Jules de: Les richesses du Palais Mazarin, Paris 1885.",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "source_span": "line 380; printed bibliography p. 420",
        },
    },
    {
        "citation": SMITHSONIAN_CITATION,
        "url": SMITHSONIAN_URL,
        "accessed_date": DATE,
        "location": "Smithsonian Libraries and Archives, record siris_sil_278901；书名、责任者、1885年、实体描述",
        "sentence_summary": "Smithsonian目录将该书著录为1885年出版的书籍，列Comte de Cosnac为作者，并记录430页及图版信息。",
        "original_quotes": [],
    },
    {
        "citation": PERSEE_CITATION,
        "url": PERSEE_URL,
        "accessed_date": DATE,
        "location": "Persée authority record 727409；书目列题、版次、出版地及出版者",
        "sentence_summary": "Persée作者书目列出该书第二版（2ème édition），Paris: Renouard, 1885，并在副题中提及Mazarin死后1661年清单。",
        "original_quotes": [],
    },
]

ITEM_SOURCES = [
    {
        "citation": BOOK_CITATION,
        "location": "第7章，印刷页184注3；Markdown L356；PDF物理页18",
        "sentence_summary": "Haskell注3称所指为de Cosnac item 1240中的1661年清单，并报告Giovanni Andrea Podesta是编制者之一；清单和该书条目未独立查阅。",
        "original_quotes": [{
            "source_span": "line 356; print p. 184 n. 3; PDF physical p. 18",
            "text": "3 See the inventory of 1661 in de Cosnac, item 1240. Incidentally, among those who drew up this inventory was the Genoese painter and engraver Giovanni Andrea Podesta whose connection with Mazarin has not hitherto been noticed—see Blunt in Revue des Arts, 1958.",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
            "source_span": "line 356; print p. 184 n. 3; PDF physical p. 18",
        },
    },
    {
        "citation": BOOK_CITATION,
        "location": "第21章书末参考书目，印刷页420；Markdown L380",
        "sentence_summary": "Haskell书目列出de Cosnac《Les richesses du Palais Mazarin》，Paris 1885；书目用于确认注3所指的刊本线索，不代表读过书内item 1240。",
        "original_quotes": [{
            "source_span": "line 380; printed bibliography p. 420",
            "text": "Cosnac, Comte Gabriel-Jules de: Les richesses du Palais Mazarin, Paris 1885.",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "source_span": "line 380; printed bibliography p. 420",
        },
    },
    {
        "citation": PERSEE_CITATION,
        "url": PERSEE_URL,
        "accessed_date": DATE,
        "location": "Persée authority record 727409；1885年版书目及书名副题",
        "sentence_summary": "Persée列出的1885年第二版书名副题称该书含1661年Mazarin去世后所作清单；此书目描述不独立辨认de Cosnac item 1240的文献载体或内容。",
        "original_quotes": [],
    },
    {
        "citation": SMITHSONIAN_CITATION,
        "url": SMITHSONIAN_URL,
        "accessed_date": DATE,
        "location": "Smithsonian Libraries and Archives, record siris_sil_278901；书名副题及出版物描述",
        "sentence_summary": "Smithsonian目录的书名副题也称该出版物包含1661年Mazarin死后所作清单；该目录记录的是出版物，不是单独的item 1240或原件。",
        "original_quotes": [],
    },
]


def make_book_card() -> str:
    frontmatter = {
        "title": "《马萨林宫珍藏》（The Riches of the Mazarin Palace）",
        "name_en": "The Riches of the Mazarin Palace",
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": BOOK_SOURCES,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    bibliography = "[第21章书目 p.420](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L380）"
    smithsonian = f"[Smithsonian Libraries and Archives](<{SMITHSONIAN_URL}>)"
    persee = f"[Persée authority record 727409]({PERSEE_URL})"
    body = f"""## 内容

### 描述

**中文：** 本卡登记Comte Gabriel-Jules de Cosnac《Les richesses du Palais Mazarin》的1885年第二版。Haskell书目列题名、责任者和Paris 1885；Persée书目确认Renouard出版的第二版，Smithsonian目录确认1885年书籍记录及实体描述。中文题名为描述性工作译名，不是官方译名。目录副题称该书涉及1661年Mazarin死后清单；具体引文页和书中清单条目未独立查阅，人物责任关系及刊本与清单条目的正式关系留待S6。{bibliography} {smithsonian} {persee}

**English:** This card records the 1885 second edition of *Les richesses du Palais Mazarin* by the Comte Gabriel-Jules de Cosnac. Haskell’s bibliography gives the title, responsibility form, and Paris 1885; Persée identifies the second edition as published by Renouard, and the Smithsonian catalog confirms an 1885 book record and physical description. The Chinese title is a descriptive working translation, not an official title. The catalog subtitle says the book concerns an inventory made after Mazarin’s death in 1661. The cited pages and the inventory entry itself have not been independently consulted; the formal author relation and the relation between this publication and the cited inventory remain for S6 review. {bibliography} {smithsonian} {persee}

### 题名与基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 原题名 | Les richesses du Palais Mazarin | S1–S3；{bibliography}；{smithsonian}；{persee} |
| 题名性质 | 刊本原题；中文题名为描述性工作译名 | S1–S3；{bibliography}；{smithsonian}；{persee} |
| 文献类型 | 印刷书籍；第二版 | S2–S3；{smithsonian}；{persee} |
| 原文语言 | 法语 | S1–S3；{bibliography}；{smithsonian}；{persee} |
| 实体描述 | 430页，另有图版 | S2；{smithsonian} |

### 版本与出版

| 字段 | 值 | 证据 |
|---|---|---|
| 版次 | 第二版（2ème édition） | S3；{persee} |
| 出版地 | Paris | S1、S3；{bibliography}；{persee} |
| 出版者 | Renouard | S3；{persee} |
| 出版年 | 1885 | S1–S3；{bibliography}；{smithsonian}；{persee} |
| 书内责任者形式 | Comte Gabriel-Jules de Cosnac | S1–S3；{bibliography}；{smithsonian}；{persee} |

### 内容范围与核验边界

- Smithsonian与Persée目录副题将Charles I的绘画与挂毯清单、以及1661年Mazarin身后清单列入该书的题名范围；这里记录目录描述，不表示已阅读相关文本或核验其中记载。{smithsonian} {persee}
- Haskell在第7章注释引用该书p.144及pp.169 ff.，具体页未独立查阅；第7章p.184注3另指向de Cosnac item 1240。该书与1661年清单item的文本关系尚未由原书核实。{bibliography}

## 关系与证据

### 身份与外部链接

| 字段 | 值／链接 | 状态与范围 | 证据 |
|---|---|---|---|
| Smithsonian书目记录 | {smithsonian} | 支持书名、责任者、1885年及实体描述；不核验引文页内容 | S2 |
| Persée作者书目 | {persee} | 列第二版、Paris: Renouard, 1885及题名副题；非原书正文 | S3 |

### 关系记录

当前没有登记正式关系。与Gabriel-Jules de Cosnac的作者关系、以及书内1661年清单条目的刊录关系，留待S6审查。{bibliography} {smithsonian} {persee}
"""
    return f"---\n{fm}---\n\n{body}"


def make_item_card() -> str:
    frontmatter = {
        "title": "1661年马萨林身后清单（The 1661 Posthumous Inventory of Cardinal Mazarin）",
        "name_en": "The 1661 Posthumous Inventory of Cardinal Mazarin",
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": ITEM_SOURCES,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p184 = "[第7章 p.184注3](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L356）"
    bibliography = "[第21章书目 p.420](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L380）"
    persee = f"[Persée authority record 727409]({PERSEE_URL})"
    smithsonian = f"[Smithsonian Libraries and Archives](<{SMITHSONIAN_URL}>)"
    body = f"""## 内容

### 描述

**中文：** 本卡表示Haskell第7章注3所指、de Cosnac item 1240中的1661年马萨林清单身份。Haskell称Giovanni Andrea Podesta为清单编制者之一；Persée和Smithsonian的书目记录说明Cosnac 1885年第二版题名包含一项1661年Mazarin身后清单。此KU仅代表被引述的清单记录身份，不代表已查见的原始手稿，也不确定item 1240所载文本究竟是原件、抄本、刊录还是节录。原件及de Cosnac item 1240均未独立查阅。{p184} {persee} {smithsonian}

**English:** This card represents the identity of the 1661 Mazarin inventory cited by Haskell in Chapter 7 note 3 as de Cosnac item 1240. Haskell names Giovanni Andrea Podesta as one of the inventory’s compilers. Persée and Smithsonian bibliographic records describe the 1885 second edition by Cosnac as including an inventory made after Mazarin’s death in 1661. This unit records only the identity of the cited inventory; it does not represent an original manuscript inspected by us, and the form of the text at item 1240 (original, copy, printed entry, or excerpt) remains undetermined. Neither the original nor de Cosnac item 1240 has been independently consulted. {p184} {persee} {smithsonian}

### 题名与基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性题名 | 1661年马萨林身后清单 | S1–S3；{p184}；{persee}；{smithsonian} |
| 被引定位 | de Cosnac, item 1240 | S1；{p184} |
| 记载年代 | 1661 | S1、S3；{p184}；{persee}；{smithsonian} |
| 文献性质 | 清单记录；具体载体和文本形态未定 | S1–S3；{p184}；{persee}；{smithsonian} |

### 刊录与转引

- Haskell在注3写明“the inventory of 1661 in de Cosnac, item 1240”，并转述Podesta为编制者之一；该责任说法仍只是Haskell的书内陈述，清单未独立查阅。{p184}
- 1885年第二版《Les richesses du Palais Mazarin》的目录副题包含1661年Mazarin身后清单；目录描述支持清单被该刊本呈现的书目语境，但尚未确认item 1240的具体文本形态。{bibliography} {persee} {smithsonian}
- 本对象与1653年清单原件KU、1861年d’Aumale刊本KU分别登记；本卡不据日期或引文自动建立它们之间的正式关系。{p184} {bibliography}

## 关系与证据

### 身份与外部链接

目录权威记录目前识别的是引用该清单的Cosnac出版物，而非独立的item 1240或底层原件。{persee} {smithsonian}

### 关系记录

当前没有登记正式关系。Podesta作为编制者之一是Haskell转述；其与该清单、Mazarin的关系及刊本的刊录性质均留待S6审查。{p184}
"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    for card_rel in (BOOK_REL, ITEM_REL):
        if any(line.strip() == f"- {card_rel}" for line in lines):
            raise SystemExit(f"Accepted path already exists: {card_rel}")
        insert_at = next(
            (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def source_check() -> None:
    expected = {
        "02-sources/02-Markdown/07_CHP-7_sec_i.md": [
            "3 See the inventory of 1661 in de Cosnac, item 1240. Incidentally, among those who drew up this inventory was the Genoese painter and engraver Giovanni Andrea Podesta whose connection with Mazarin has not hitherto been noticed—see Blunt in Revue des Arts, 1958."
        ],
        "02-sources/02-Markdown/21_CHP-21Bibliography.md": [
            "Cosnac, Comte Gabriel-Jules de: Les richesses du Palais Mazarin, Paris 1885."
        ],
    }
    for source_file, quotes in expected.items():
        source_text = " ".join((ROOT / source_file).read_text(encoding="utf-8-sig").split())
        for quote in quotes:
            if " ".join(quote.split()) not in source_text:
                raise SystemExit(f"Source anchor changed in {source_file}: {quote}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the 1885 Cosnac publication and its cited 1661 inventory as separate archive KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidates_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignment = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    primary_by_id = {
        row["candidate_id"]: row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    expected_groups = {BOOK_CANDIDATE: BOOK_GROUP, ITEM_CANDIDATE: ITEM_GROUP}
    for cid, group in expected_groups.items():
        candidate = candidate_by_id.get(cid)
        row = primary_by_id.get(cid)
        if not candidate or not row or candidate.get("suggested_type") != "archive":
            raise SystemExit(f"Missing archive candidate/alignment row for {cid}.")
        if row.get("decision") != "new" or row.get("ku_id") or sync.get_group(row.get("resolution_note", "")) != group:
            raise SystemExit(f"{cid} is no longer an unmapped new member of {group}.")
    if len(manifest) != 1326 or any(row.get("ku_id") in {BOOK_KU, ITEM_KU} for row in manifest):
        raise SystemExit("Unexpected S4 manifest baseline or an archive target already exists.")
    if BOOK_PATH.exists() or ITEM_PATH.exists():
        raise SystemExit("An archive card path already exists; inspect before applying.")
    for url in (SMITHSONIAN_URL, PERSEE_URL):
        if any(row.get("candidate_id") == BOOK_CANDIDATE and row.get("external_id") == url for row in alignment):
            raise SystemExit(f"Publication identity row already exists: {url}")
    source_check()

    max_alignment_id = max(int(row["alignment_id"].removeprefix("aln-")) for row in alignment if row["alignment_id"].startswith("aln-") and row["alignment_id"][4:].isdigit())
    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == BOOK_CANDIDATE and not row.get("external_source"):
            row["ku_id"] = BOOK_KU
            row["resolution_note"] += f" S4 registration: mapped {BOOK_GROUP} to {BOOK_KU}; publication identity supported by Smithsonian and Persée records."
        elif row.get("candidate_id") == ITEM_CANDIDATE and not row.get("external_source"):
            row["ku_id"] = ITEM_KU
            row["resolution_note"] += f" S4 registration: mapped {ITEM_GROUP} to {ITEM_KU}; scope is the cited inventory identity, not a directly examined original or verified transcription."
    external_rows = [
        {
            "alignment_id": f"aln-{max_alignment_id + 1}", "candidate_id": BOOK_CANDIDATE, "ku_id": "",
            "external_source": "Smithsonian Libraries and Archives", "external_id": SMITHSONIAN_URL,
            "decision": "new", "accessed_date": DATE, "process_ref": "S3-full-book-2026-10-16", "legacy_ku_id": "",
            "resolution_note": "Identity only: Smithsonian Libraries and Archives record siris_sil_278901 names Les richesses du Palais Mazarin by Comte de Cosnac (Gabriel-Jules), dates it 1885, describes a book of 430 pages with plates, and includes the 1661 inventory in the title subtitle. Supports the publication identity, not the contents of item 1240 or the underlying inventory itself.",
        },
        {
            "alignment_id": f"aln-{max_alignment_id + 2}", "candidate_id": BOOK_CANDIDATE, "ku_id": "",
            "external_source": "Persée", "external_id": PERSEE_URL,
            "decision": "new", "accessed_date": DATE, "process_ref": "S3-full-book-2026-10-16", "legacy_ku_id": "",
            "resolution_note": "Identity only: Persée authority bibliography 727409 lists Les richesses du Palais Mazarin, 2ème édition, Paris: Renouard, 1885, and a subtitle naming an inventory drawn up after Mazarin’s death in 1661. Supports this publication edition and subject description; it does not verify the cited pages or identify the material form of de Cosnac item 1240.",
        },
    ]
    planned_alignment.extend(external_rows)
    planned_manifest = list(manifest)
    planned_manifest.extend([
        {"ku_id": BOOK_KU, "type": "archive", "canonical_name": "马萨林宫珍藏", "name_en": "The Riches of the Mazarin Palace", "source_task": TASK, "card_path": BOOK_REL},
        {"ku_id": ITEM_KU, "type": "archive", "canonical_name": "1661年马萨林身后清单", "name_en": "The 1661 Posthumous Inventory of Cardinal Mazarin", "source_task": TASK, "card_path": ITEM_REL},
    ])
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    book_card, item_card = make_book_card(), make_item_card()
    for card in (book_card, item_card):
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        if not match or yaml.safe_load(match.group(1)).get("type") != "archive":
            raise SystemExit("Generated archive card frontmatter failed validation.")

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    details = (
        f"### S4 archive：Cosnac《Les richesses du Palais Mazarin》1885年第二版（{DATE}）\n\n"
        f"- `{BOOK_CANDIDATE}`登记至 `{BOOK_KU}`。Haskell书目列Paris 1885；Persée确认第二版、Renouard及Paris，Smithsonian确认书籍记录、责任者和1885年。两个外部记录支持刊本书目身份；原书及Haskell所引页未独立查阅，正式作者边留待S6。\n"
        f"- 新增archive卡、manifest、1条候选映射及2条外部书目身份行；与1885刊本中所称的1661年清单分别登记。\n\n"
        f"### S4 archive：1661年马萨林身后清单（de Cosnac item 1240）（{DATE}）\n\n"
        f"- `{ITEM_CANDIDATE}`登记至 `{ITEM_KU}`，表示Haskell注3指向的1661年清单身份。Persée与Smithsonian记录说明1885年刊本副题含1661年Mazarin身后清单；它们识别的是刊本，不是独立item 1240。原件、de Cosnac条目以及item的文本形态均未核实，故不称手稿或抄本。\n"
        f"- 新增archive卡、manifest及1条候选KU映射；与1653年清单、1861年刊本和1885年书籍保持分立。Podesta编制者身份及清单—刊本关系均留待S6，不新增正式关系。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；archive为{sync.fmt(stats['archive']['registered_groups'])}组已登记、{sync.fmt(stats['archive']['pending_groups'])}组/{sync.fmt(stats['archive']['pending_members'])}条成员待登记；KU总数{len(planned_manifest)}。字段事实由 `build_field_facts.py` 预检登记。\n\n"
    )
    if result_text.count("## 未解决项与交接限制") != 1:
        raise SystemExit("Could not locate result insertion point.")
    result_text = result_text.replace("## 未解决项与交接限制", details + "## 未解决项与交接限制", 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    if f"S4 archive：Cosnac 1885" in process_text or f"S4 archive：1661年马萨林身后清单" in process_text:
        raise SystemExit("A Cosnac archive S4 process entry already exists.")
    process_text += (
        f"\n\n### S4 archive：Cosnac《Les richesses du Palais Mazarin》1885年第二版（{DATE}）\n\n"
        f"- `{BOOK_CANDIDATE}` → `{BOOK_GROUP}` → `{BOOK_KU}`。Haskell书目p.420列Comte Gabriel-Jules de Cosnac、Paris 1885；Persée authority 727409给出Renouard 1885第二版，Smithsonian record siris_sil_278901确认书名、责任者、出版年及实体描述。原书和p.144、pp.169 ff.未独立查阅；author关系待S6。\n"
        "- 该刊本与单独登记的1661年清单身份、1653年清单原件及d’Aumale 1861印本分开，不把目录副题当作对清单内容的核验。\n\n"
        f"### S4 archive：1661年马萨林身后清单（de Cosnac item 1240）（{DATE}）\n\n"
        f"- `{ITEM_CANDIDATE}` → `{ITEM_GROUP}` → `{ITEM_KU}`。Haskell p.184注3指向de Cosnac item 1240；Persée和Smithsonian书目记录显示1885刊本副题包含1661年Mazarin身后清单。清单原件与item 1240均未独立查阅；该KU仅表示来源指向的清单身份，实际载体和刊录关系未定，不标注为原件或手稿。\n"
        "- Haskell称Giovanni Andrea Podesta为编制者之一，继续作为来源归属明确的S2关系候选；不新增正式编制或刊录边。与1653年清单、1861年印本及1885年书籍保持不同KU。\n"
        f"- 两项登记后S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射；archive已登记{sync.fmt(stats['archive']['registered_groups'])}组、待登记{sync.fmt(stats['archive']['pending_groups'])}组/{sync.fmt(stats['archive']['pending_members'])}条候选。字段事实待`build_field_facts.py`预检。"
    )

    targets = [ALIGNMENT, MANIFEST, ACCEPTED, PROCESS, RESULT]
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("A Cosnac archive S4 recovery copy already exists.")
    if args.dry_run:
        print(f"dry-run passed: {BOOK_CANDIDATE}->{BOOK_KU}; {ITEM_CANDIDATE}->{ITEM_KU}; external rows={len(external_rows)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}")
        return 0

    for original, backup in zip(targets, backup_paths, strict=True):
        shutil.copy2(original, backup)
    BOOK_PATH.write_text(book_card, encoding="utf-8-sig", newline="\n")
    ITEM_PATH.write_text(item_card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST, manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_text, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {BOOK_CANDIDATE}->{BOOK_KU}; {ITEM_CANDIDATE}->{ITEM_KU}; external rows={len(external_rows)}; manifest={len(planned_manifest)}")
    print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
