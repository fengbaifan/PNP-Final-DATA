from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

import yaml

PROCESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE_ID = "cand-0929"
GROUP = "new-person:dionisio-dolfin-b1fe9e909e"
KU_ID = "units/persons/dionisio-dolfin"
CARD_REL = "04-knowledge/units/persons/dionisio-dolfin.md"
CARD_PATH = ROOT / CARD_REL
EXTERNAL_ALIGNMENT_ID = "aln-12631"
DBF_URL = "https://www.dizionariobiograficodeifriulani.it/dolfin-dionisio"
ARCHIVE_URL = "https://www.archiviodiocesano.it/storia/"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s4-dionisio-dolfin-20261016"

BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
DBF_CITATION = (
    "Cristina Moro, ‘Dolfin Dionisio,’ *Dizionario Biografico dei Friulani Nuovo Liruti*. "
    f"{DBF_URL} Accessed {DATE}."
)
ARCHIVE_CITATION = (
    f"Archivio Storico Diocesano di Udine, ‘Storia.’ {ARCHIVE_URL} Accessed {DATE}."
)


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv_text(fieldnames, rows) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if any(line.strip() == f"- {CARD_REL}" for line in lines):
        raise ValueError("Accepted path already exists.")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "全书索引 D.csv#31；索引转录行33",
            "sentence_summary": "索引主项以Dolfin, Dionisio为名，定位第9章pp.252–253。",
            "original_quotes": [{"source_span": "D.csv#31", "text": "Dolfin, Dionisio; 252, 253"}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-2-Index-CSV/D.csv",
                "source_span": "D.csv#31",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 p.252；OCR L116–122",
            "sentence_summary": "Haskell以Dionisio称该人物，记其1698年获任并迁居Udine；外部传记把1698年解释为获任coadjutor、1699年正式接掌宗主教职位。本卡保留两种来源各自的时间表述。",
            "original_quotes": [
                {"source_span": "lines 120–122; print p. 252", "text": "was given the post and went to live in Udine"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "lines 116–122; print p. 252",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章 p.253；OCR L124–132",
            "sentence_summary": "Haskell在正文中给出Dionisio Dolfin全名，并描述其Udine宗主教宫殿及Tiepolo壁画语境；这些作品、亲属及委托陈述不在本卡登记为正式关系。",
            "original_quotes": [
                {"source_span": "line 127; print p. 253", "text": "Dionisio Dolfin"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "lines 124–132; print p. 253",
            },
        },
        {
            "citation": DBF_CITATION,
            "url": DBF_URL,
            "accessed_date": DATE,
            "location": "Dizionario Biografico dei Friulani Nuovo Liruti, ‘Dolfin Dionisio’；lines 8–24, 41",
            "sentence_summary": "Cristina Moro以Dionisio Dolfin为条目名，记录其1663年生于威尼斯、1734年8月3日卒于San Vito al Tagliamento；1698年获任其叔Giovanni的coadjutor，1699年正式接掌阿奎莱亚宗主教职位。",
            "original_quotes": [
                {"source_span": "entry lines 8, 15–16", "text": "(1663-1734); 1663 - Venezia; 3 agosto 1734 - San Vito al Tagliamento"},
                {"source_span": "entry lines 18–19", "text": "nel 1698 il D. fu nominato coadiutore"},
            ],
            "evidence_ref": {"source_url": DBF_URL, "source_span": "lines 8–24, 41"},
        },
        {
            "citation": ARCHIVE_CITATION,
            "url": ARCHIVE_URL,
            "accessed_date": DATE,
            "location": "Archivio Storico Diocesano di Udine, ‘Storia,’ lines 37–39",
            "sentence_summary": "乌迪内教区档案馆将Dionisio Delfino列为阿奎莱亚宗主教（1699–1734），并记其更新宗主教驻地、委托Tiepolo装饰。该页面只作机构历史旁证。",
            "original_quotes": [],
            "evidence_ref": {"source_url": ARCHIVE_URL, "source_span": "lines 37–39"},
        },
    ]
    frontmatter = {
        "title": "迪奥尼西奥·多尔芬（Dionisio Dolfin）",
        "name_en": "Dionisio Dolfin",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 D.csv#31](../../../02-sources/03-Index/03-2-Index-CSV/D.csv)"
    p252 = "[第9章 p.252](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L116–122）"
    p253 = "[第9章 p.253](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L124–132）"
    dbf = f"[《弗留利人传记辞典》条目]({DBF_URL})"
    archive = f"[乌迪内教区档案馆历史页]({ARCHIVE_URL})"
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 第9章所称的 Dionisio Dolfin。索引以“Dolfin, Dionisio”定位第9章第252–253页，正文第253页给出全名；《弗留利人传记辞典》将其识别为阿奎莱亚宗主教 Dionisio Dolfin（1663–1734）。Haskell称其1698年“获任”该职位，传记辞典进一步区分：1698年获任叔父 Giovanni 的继任辅佐主教，1699年正式接掌宗主教职位。中文名为项目工作音译。{idx} {p252} {p253} {dbf} {archive}

**English:** This unit records the Dionisio Dolfin named in Chapter 9 of Haskell’s book. The index entry “Dolfin, Dionisio” points to pp. 252–253, and the text on p. 253 gives his full name. The *Dizionario Biografico dei Friulani* identifies him as Dionisio Dolfin, patriarch of Aquileia (1663–1734). Haskell says he was given the office in 1698; the biographical entry distinguishes his 1698 appointment as coadjutor with right of succession from his formal assumption of the patriarchate in 1699. The Chinese display name is a project working transliteration. {idx} {p252} {p253} {dbf} {archive}

### 姓名与身份

| 字段 | 值 | 证据 |
|---|---|---|
| 规范姓名 | Dionisio Dolfin | S3，DBF；S2，{p253} |
| 本书索引形式 | Dolfin, Dionisio | S1，D.csv#31 |
| 本书正文全名 | Dionisio Dolfin | S2，{p253} |
| 身份 | 阿奎莱亚宗主教（1699–1734） | S3，DBF；乌迪内教区档案馆 |

### 生平信息

| 字段 | 值 | 证据 |
|---|---|---|
| 出生年份 | 1663年 | S3，DBF |
| 出生地 | 威尼斯 | S3，DBF |
| 去世日期 | 1734年8月3日 | S3，DBF |
| 去世地 | San Vito al Tagliamento | S3，DBF |
| 宗主教任职 | 1699–1734年；1698年受任为有继任权的coadjutor，1699年正式接掌宗主教职位 | S3，DBF；乌迪内教区档案馆 |

### 本章相关内容

Haskell第9章p.252将任职起点表述为1698年；外部传记把该年对应为coadjutor任命，并记正式接掌为1699年。这里保留来源各自的时间含义。Haskell关于其与Daniele人物的亲属关系、居住与宫殿项目，以及Tiepolo受召和具体作品的说法仍由原始 statement 承载，未在本次登记为正式关系或独立核实事实。{p252} {p253}

## 关系与证据

### 身份与外部链接

| 字段 | 值／链接 | 状态与范围 | 证据 |
|---|---|---|---|
| 《弗留利人传记辞典》人物条目 | {dbf} | 支持姓名、出生／去世信息及宗主教身份；不验证Haskell提出的亲属、居住和艺术关系 | S3 |
| 乌迪内教区档案馆历史页 | {archive} | 旁证阿奎莱亚宗主教任期和驻地项目 | S3 |

### 关系记录

本卡未新增正式关系。与Daniele Dolfin等人的亲属关系、Tiepolo委托及作品地点主张仍待S6逐条审查。

### 关系候选入口

[全书关系候选与端点记录](../../../03-processing/{TASK}/process/knowledge.md)
"""
    return f"---\n{fm}---\n\n{body}"


def update_external_alignment_counts(result: str, alignment_count: int) -> str:
    pattern = re.compile(
        r"(?m)^(\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \| )"
        r"[\d,]+ 条：[\d,]+ 条候选决定记录及 [\d,]+ 条外部身份记录；候选决定数见下表 \|$"
    )
    replacement = (
        f"| [全书对齐](../tables/alignment.csv) | {alignment_count:,} 条：12,405 条候选决定记录及 226 条外部身份记录；候选决定数见下表 |"
    )
    updated, n = pattern.subn(replacement, result, count=1)
    if n != 1:
        raise ValueError("Could not refresh alignment artifact counts in the result.")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Dionisio Dolfin in S4 after S3 identity alignment.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    manifest_fields, manifest = read_csv(MANIFEST)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id[CANDIDATE_ID]
    primary_matches = [row for row in alignment if row.get("candidate_id") == CANDIDATE_ID and not row.get("external_source")]
    assert len(primary_matches) == 1
    primary = primary_matches[0]
    assert candidate.get("canonical_name") == "Dolfin, Dionisio"
    assert candidate.get("index_entry_id") == "D.csv#31"
    assert candidate.get("suggested_type") == "person"
    assert primary.get("decision") == "new" and not primary.get("ku_id")
    assert GROUP in primary.get("resolution_note", "")
    assert "No external identity source was accessed" in primary.get("resolution_note", "")
    group_rows = [
        row for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and GROUP in row.get("resolution_note", "")
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE_ID]
    assert not any(row.get("alignment_id") == EXTERNAL_ALIGNMENT_ID for row in alignment)
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not CARD_PATH.exists()
    assert not any(line.strip() == f"- {CARD_REL}" for line in ACCEPTED.read_text(encoding="utf-8-sig").splitlines())
    assert any(row.get("type") == "family" and row.get("name_en") == "Dolfin family" for row in manifest)
    assert not any(row.get("type") == "person" and "Dionisio Dolfin" in (row.get("canonical_name", "") + row.get("name_en", "")) for row in manifest)

    source_252 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    assert "Dionisio Dolfin" in source_252
    assert "Dionisio, younger brother of the two Danieles" in source_252

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    relation_candidates = [
        row for row in statements
        if row.get("qualifiers", {}).get("relation_candidate")
        and CANDIDATE_ID in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    ]
    contextual_mentions = [
        row for row in statements
        if row.get("qualifiers", {}).get("relation_candidate")
        and CANDIDATE_ID in row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
        and row not in relation_candidates
    ]
    assert len(relation_candidates) == 9 and len(contextual_mentions) == 3

    planned_alignment = [dict(row) for row in alignment]
    planned_primary = next(row for row in planned_alignment if row.get("alignment_id") == primary["alignment_id"])
    planned_primary["resolution_note"] += (
        f" S3 external identity checked {DATE}: Cristina Moro, Dizionario Biografico dei Friulani Nuovo Liruti, "
        f"‘Dolfin Dionisio’ ({DBF_URL}), identifies the person as Dionisio Dolfin (1663–1734), patriarch of Aquileia; "
        "the record dates his appointment as coadjutor to 1698 and formal assumption of the patriarchate to 1699. "
        "This reconciles Haskell's 1698 wording without changing his source statement."
    )
    planned_alignment.append({
        "alignment_id": EXTERNAL_ALIGNMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "ku_id": "",
        "external_source": "Dizionario Biografico dei Friulani (Nuovo Liruti)",
        "external_id": DBF_URL,
        "decision": "new",
        "accessed_date": DATE,
        "process_ref": "S3-full-book-2026-10-16",
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity only: Cristina Moro's ‘Dolfin Dionisio’ record identifies the index and Chapter 9 full-name anchors "
            "as Dionisio Dolfin (1663–1734), patriarch of Aquileia. It records a 1698 appointment as coadjutor with right of succession "
            "and formal possession in 1699; this distinguishes appointment from accession and does not validate Haskell's other claims."
        ),
    })
    planned_primary["ku_id"] = KU_ID
    planned_primary["resolution_note"] += f" S4 registration ({DATE}): new identity group {GROUP} maps to one person KU {KU_ID}."
    planned_external = next(row for row in planned_alignment if row.get("alignment_id") == EXTERNAL_ALIGNMENT_ID)
    planned_external["ku_id"] = KU_ID
    planned_external["resolution_note"] += " S4 registration maps this identity authority row to the same KU."

    planned_manifest = [dict(row) for row in manifest] + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "迪奥尼西奥·多尔芬",
        "name_en": "Dionisio Dolfin",
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_text = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))
    card_text = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card_text, re.DOTALL)
    assert frontmatter_match
    card_frontmatter = yaml.safe_load(frontmatter_match.group(1))
    assert card_frontmatter["type"] == "person" and len(card_frontmatter["sources"]) == 5

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text = update_external_alignment_counts(result_text, len(planned_alignment))
    s3_insert = (
        f"### S3 person：Dionisio Dolfin 跨页身份与外部对齐（{DATE}）\n\n"
        f"- {CANDIDATE_ID}（D.csv#31，pp.252–253）由索引主项、p.252人物名和p.253正文全名锚定同一人物。Dizionario Biografico dei Friulani Nuovo Liruti（Cristina Moro，{DBF_URL}）确认Dionisio Dolfin为1663–1734年的阿奎莱亚宗主教，并区分1698年coadjutor任命与1699年正式接掌；因此与Haskell的1698年说法不冲突。新增外部身份行 {EXTERNAL_ALIGNMENT_ID}，不把外证扩展为亲属或艺术关系判断。\n"
        f"- 保留 `new-person:dionisio-dolfin-b1fe9e909e`；现有Dolfin family KU为family类型，不与人物合并。9条以Dionisio为主／客体端点的S2关系候选仍待S6；另3条只在statement限定中提及他，不计作直接关系端点。\n\n"
    )
    s3_marker = "### S3 institution：Papal States 跨章身份组裁决（2026-10-16）"
    assert result_text.count(s3_marker) == 1
    result_text = result_text.replace(s3_marker, s3_insert + s3_marker, 1)
    result_insert = (
        f"### S4 person：Dionisio Dolfin 人物组登记（{DATE}）\n\n"
        f"- {CANDIDATE_ID} → {GROUP} → {KU_ID}。新增双语person卡、manifest、accepted路径及候选／外部身份映射；卡片只录姓名、书内锚点、DBF支持的生卒和任职信息。\n"
        f"- 9条以Dionisio为主／客体端点的S2关系候选继续待S6，未写入 `relations.csv`；另3条statement只在语境限定中提及他。书内关于Daniele亲属、宫殿/作品、Tiepolo委托的说法保留原statement及限定；不因端点登记认定为正式关系。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；KU总数{len(planned_manifest)}。字段事实待 `build_field_facts.py` 预检登记。\n\n"
    )
    result_marker = "## 未解决项与交接限制"
    assert result_text.count(result_marker) == 1
    result_text = result_text.replace(result_marker, result_insert + result_marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    s3_heading = f"### S3 person：Dionisio Dolfin 跨页身份与外部对齐（{DATE}）"
    s4_heading = f"### S4 person：Dionisio Dolfin 人物组登记（{DATE}）"
    assert s3_heading not in process_text and s4_heading not in process_text
    process_text += (
        f"\n\n{s3_heading}\n\n"
        f"- `cand-0929`（D.csv#31，pp.252–253）为person候选。第9章p.252先以Dionisio称该人物，p.253给出Dionisio Dolfin全名；两处正文锚点与索引页码相互对应。此前decision为new-person:dionisio-dolfin-b1fe9e909e，且无既有人物KU命中；Dolfin family KU不因同姓而合并。\n"
        f"- Cristina Moro, ‘Dolfin Dionisio,’ *Dizionario Biografico dei Friulani Nuovo Liruti*（{DBF_URL}，访问于{DATE}）记录1663年生于威尼斯、1734年8月3日卒于San Vito al Tagliamento；1698年获任其叔Giovanni Dolfin的coadjutor，1699年正式接掌阿奎莱亚宗主教职位。乌迪内教区档案馆历史页（{ARCHIVE_URL}）旁证其1699–1734年任期与驻地项目。\n"
        "- 外部传记与Haskell p.252的1698年表述不构成冲突：前者区分任命和正式接掌。本轮只增强身份与该任职的时间语境，不把Haskell关于Daniele亲属、宫殿修建、召请Tiepolo或具体作品的陈述改写为外部确认事实。新增身份行 `aln-12631`；9条直接关系端点候选保留待S6，另3条仅在限定中提及该人物。\n\n"
        f"{s4_heading}\n\n"
        f"- `cand-0929` → `{GROUP}` → `{KU_ID}`。新增双语人物卡 `[{CARD_REL}]({CARD_REL})`、manifest一条及accepted路径；候选决定行和外部身份行 `aln-12631` 共同指向该KU。\n"
        "- 卡片将Haskell与DBF的时间表述并列，记录其姓名、出生/去世信息、coadjutor任命及正式宗主教任期；没有新增relations.csv边。9条以该人物为直接端点的关系候选逐项留待S6，另3条仅为语境提及。\n"
        f"- S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；person已登记{sync.fmt(stats['person']['registered_groups'])}组，待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条成员；manifest={len(planned_manifest)}。字段表待 `build_field_facts.py` dry-run/apply。\n"
    )

    outputs = {
        ALIGNMENT: write_csv_text(alignment_fields, planned_alignment),
        MANIFEST: write_csv_text(manifest_fields, planned_manifest),
        ACCEPTED: accepted_text,
        CARD_PATH: card_text,
        PROCESS: process_text,
        RESULT: result_text,
    }
    for path in outputs:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists()

    if args.dry_run:
        for path, updated in outputs.items():
            current = path.read_text(encoding="utf-8-sig") if path.exists() else ""
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE_ID}->{GROUP}->{KU_ID}; external={EXTERNAL_ALIGNMENT_ID}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"relation_candidates={len(relation_candidates)} contextual_mentions={len(contextual_mentions)}"
        )
        return 0

    backups = []
    try:
        for path in outputs:
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if path.exists():
                shutil.copy2(path, backup)
            else:
                backup.write_text("NEW FILE: created by S4 Dionisio Dolfin registration\n", encoding="utf-8")
            backups.append((path, backup))
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8", newline="\n")
    except Exception:
        for path, backup in backups:
            if backup.read_text(encoding="utf-8-sig").startswith("NEW FILE:"):
                if path.exists():
                    path.unlink()
            else:
                shutil.copy2(backup, path)
        raise

    print(
        f"applied: {CANDIDATE_ID}->{GROUP}->{KU_ID}; external={EXTERNAL_ALIGNMENT_ID}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"relation_candidates={len(relation_candidates)}; backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
