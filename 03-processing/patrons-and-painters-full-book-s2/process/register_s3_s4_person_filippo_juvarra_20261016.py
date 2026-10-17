from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
from collections import defaultdict
from io import StringIO
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge/tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge/results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge/accepted.yml"
DATE = "2026-10-16"

MAIN_CANDIDATE = "cand-1339"
SUBENTRY_CANDIDATE = "cand-1340"
GROUP = "new-person:filippo-juvarra-61d1b03394"
KU_ID = "units/persons/filippo-juvarra"
CARD_REL = "04-knowledge/units/persons/filippo-juvarra.md"
CARD = ROOT / CARD_REL
NAME_ZH = "菲利波·尤瓦拉"
NAME_EN = "Filippo Juvarra"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/filippo-juvarra_(Dizionario-Biografico)/"
NATIONALMUSEUM_URL = "https://collection.nationalmuseum.se/en/artists/artist/10591/"
NGA_URL = "https://www.nga.gov/artists/2585-filippo-juvarra"
BACKUP_SUFFIX = ".bak-s3-s4-filippo-juvarra-20261016"

BOOK_SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
        "location": "第6章 pp.164–165；OCR L30、36–38",
        "span": "lines 30, 36–38; print pp. 164–165",
        "summary": "正文以 Filippo Juvarra 全名记其管理 Pietro Ottoboni 剧场布景；下一页续述其建筑风格与为 Cancelleria 剧场制作布景。",
        "quotes": (
            ("line 30", "whose scenery was managed by Filippo Juvarra"),
            ("line 37", "Only Juvarra"),
            ("lines 37–38", "But that was confined to his marvellous stage sets for the theatre in the Cancelleria"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        "location": "第7章 p.202；OCR L59–60",
        "span": "lines 59–60; print p. 202",
        "summary": "正文以全名 Filippo Juvarra 称其为 Savoy 统治者推动绘画赞助时的艺术决策者。",
        "quotes": (("lines 59–60", "with the help of his artistic dictator Filippo Juvarra"),),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章 pp.296–297；OCR L330–335、343",
        "span": "lines 330–335, 343; print pp. 296–297",
        "summary": "正文以全名记载建筑师 Filippo Juvarra 在都灵担任城市艺术总监，并叙述其受西班牙国王委托为马德里王宫规划装饰及绘画征集。",
        "quotes": (
            ("lines 330–331", "the architect Filippo Juvarra was artistic director of the city"),
            ("line 330", "on his authority a vast number of commissions was given"),
            ("lines 334–335", "he devised a scheme for decorating the Royal Palace in Madrid"),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/J，K.csv",
        "location": "全书索引 J，K.csv#23；页码 164、165、202、296、297",
        "span": "J，K.csv#23",
        "summary": "人物主项 Juvarra, Filippo 汇集第6、7、10章的对应页码。",
        "quotes": (("J，K.csv#23", "Juvarra, Filippo"),),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/J，K.csv",
        "location": "全书索引 J，K.csv#24；子项 as artistic director in Turin；页码 296、297",
        "span": "J，K.csv#24",
        "summary": "索引子项将 Juvarra, Filippo 的都灵艺术总监语境定位到 p.296–297；该页正文直接以同一全名、同一职能锚定候选。",
        "quotes": (
            ("J，K.csv#24", "Juvarra, Filippo"),
            ("J，K.csv#24", "as artistic director in Turin"),
        ),
    },
)


def source_row(item: dict) -> dict:
    return {
        "citation": (
            BOOK_CITATION
            if item["source_file"].startswith("02-sources/02-Markdown/")
            else "Francis Haskell, *Patrons and Painters*, index"
        ),
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": span, "text": quote}
            for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["source_file"],
            "source_span": item["span"],
        },
    }


def make_card() -> str:
    sources = [source_row(item) for item in BOOK_SOURCES]
    sources.extend(
        [
            {
                "citation": f"Tommaso Manfredi, “JUVARRA, Filippo,” *Dizionario Biografico degli Italiani*, vol. 62 (2004). {TRECCANI_URL} Accessed {DATE}.",
                "location": "Entry heading; birth, Turin career, Madrid commission, and death passages",
                "sentence_summary": (
                    "The DBI identifies Filippo Juvarra, born in Messina on 27 March 1678 and deceased in Madrid on 31 January 1736, "
                    "as an architect whose career included major work in Turin and a final Royal Palace project in Madrid."
                ),
            },
            {
                "citation": f"Nationalmuseum, artist record 10591: Filippo Juvarra. {NATIONALMUSEUM_URL} Accessed {DATE}.",
                "location": "Person authority record",
                "sentence_summary": (
                    "The museum authority record identifies the Italian architect Filippo Juvarra, gives Messina and Madrid as birth and death places, "
                    "dates 1678–1736, and lists spelling variants Filippo Juvara, Filippo Juarra, and Filippo Ivara."
                ),
            },
            {
                "citation": f"National Gallery of Art, artist record: Filippo Juvarra, artist 2585. {NGA_URL} Accessed {DATE}.",
                "location": "Artist heading, name variants, role, and date line",
                "sentence_summary": (
                    "The NGA identifies Filippo Juvarra as Sicilian, 1678–1736, and lists Juvara, Filippo and Ivara, Filippo as name variants."
                ),
            },
        ]
    )
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch6 = "[第6章 pp.164–165](../../../02-sources/02-Markdown/06_CHP-6_sec_v.md)（L30、36–38）"
    ch7 = "[第7章 p.202](../../../02-sources/02-Markdown/07_CHP-7_sec_v.md)（L59–60）"
    ch10 = "[第10章 pp.296–297](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L330–335、343）"
    main_index = "[人物主项 J，K.csv#23](../../../02-sources/03-Index/03-2-Index-CSV/J，K.csv)"
    sub_index = "[索引子项 J，K.csv#24](../../../02-sources/03-Index/03-2-Index-CSV/J，K.csv)"
    treccani = f"[Treccani DBI]({TRECCANI_URL})"
    nationalmuseum = f"[瑞典国家博物馆人物记录]({NATIONALMUSEUM_URL})"
    nga = f"[美国国家美术馆]({NGA_URL})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引人物主项“Juvarra, Filippo”列出第6、7、10章页码；另有子项“as artistic director in Turin”，定位到第10章 pp.296–297。该页正文以全名称他为建筑师，并称其在都灵担任城市艺术总监，随后叙述他为马德里王宫构思装饰方案。第6章以全名记其管理 Pietro Ottoboni 剧场布景，第7章又以全名称其为 Savoy 绘画赞助的艺术决策者。Treccani DBI、瑞典国家博物馆和美国国家美术馆记录在姓名、建筑师身份及1678–1736年日期上相符；后两者列出 Juvara、Ivara 等拼写异形。{main_index} {sub_index} {ch6} {ch7} {ch10} {treccani} {nationalmuseum} {nga}

**English:** The book’s main index entry “Juvarra, Filippo” cites Chapters 6, 7, and 10; a subentry, “as artistic director in Turin,” points to pages 296–297 of Chapter 10. The text on those pages names the architect Filippo Juvarra and describes him as the city’s artistic director in Turin before recounting his scheme for the Royal Palace in Madrid. Chapter 6 names him in connection with Pietro Ottoboni’s theatre scenery, and Chapter 7 again names him as the artistic decision-maker in Savoy’s policy for painting patronage. Treccani’s DBI, the Nationalmuseum, and the National Gallery of Art agree on the identity, architect role, and dates 1678–1736; the latter two list spelling variants including Juvara and Ivara. {main_index} {sub_index} {ch6} {ch7} {ch10} {treccani} {nationalmuseum} {nga}

### 名称与身份比对

- **规范展示名：** Filippo Juvarra，依本书正文与索引主项。{main_index} {ch6} {ch7} {ch10}
- **姓名异形：** Filippo Juvara、Filippo Juarra、Filippo Ivara，见瑞典国家博物馆；美国国家美术馆另列 Juvara, Filippo、Ivara, Filippo。{nationalmuseum} {nga}
- **身份：** 意大利建筑师。Treccani DBI 记其于1714年赴都灵任萨伏依王室建筑职务，后长期从事都灵建筑项目；本书跨第6、7、10章的建筑与赞助语境与该人物身份相合。{treccani} {ch6} {ch7} {ch10}
- **生卒：** 1678年生于 Messina，1736年1月31日卒于 Madrid；Treccani DBI 记出生日期为3月27日，国家博物馆与 NGA 给出1678–1736年。{treccani} {nationalmuseum} {nga}
- **索引子项裁决：** cand-1340 的“as artistic director in Turin”页码296、297与 cand-1339 人物主项重叠；同页正文明确写“the architect Filippo Juvarra”并说明其为都灵城市艺术总监。因此两个候选归入同一人物组，不单独建立子项人物。{main_index} {sub_index} {ch10}

### 跨章语境

第6章记其为 Pietro Ottoboni 管理剧场布景及其风格；第7章记其在 Savoy 赞助政策中的角色；第10章将都灵艺术总监与马德里宫廷建筑方案联系起来。三个章节的全名或同页明确指代，与索引主项及都灵艺术总监子项共同支持跨章归并。{ch6} {ch7} {ch10} {main_index} {sub_index}

## 关系与证据

### 外部身份记录

- **Treccani DBI：** {treccani}；以 Filippo Juvarra 立目，记 Messina 出生、Madrid 去世、建筑师身份与职业经历。
- **瑞典国家博物馆：** {nationalmuseum}；记录规范姓名、建筑师角色、Messina / Madrid 地点、1678–1736年及 Juvara、Ivara 等姓名异形。
- **美国国家美术馆：** {nga}；记录 Filippo Juvarra，Sicilian，1678–1736，并列 Juvara 与 Ivara 两种姓名形式。

### 关系记录

当前没有登记正式关系。涉及 cand-1339 的12条 S2 关系候选留待 S6 逐条审查；cand-1340 原为索引子项候选，没有独立 S2 statement，本次依据第10章 pp.296–297 的全名与职能锚点将其并入人物主项身份组。未开展 S5 补足。
"""


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    assert CARD_REL not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def contains_candidate(value, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(contains_candidate(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(contains_candidate(item, candidate_id) for item in value)
    return value == candidate_id


def normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Review the Filippo Juvarra S3 group and register it in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    main_candidate = candidate_by_id[MAIN_CANDIDATE]
    subentry_candidate = candidate_by_id[SUBENTRY_CANDIDATE]
    main_row = next(
        row for row in alignments
        if row.get("candidate_id") == MAIN_CANDIDATE and not row.get("external_source")
    )
    subentry_row = next(
        row for row in alignments
        if row.get("candidate_id") == SUBENTRY_CANDIDATE and not row.get("external_source")
    )
    assert main_candidate.get("suggested_type") == subentry_candidate.get("suggested_type") == "person"
    assert main_candidate.get("canonical_name") == subentry_candidate.get("canonical_name") == "Juvarra, Filippo"
    assert main_candidate.get("index_entry_id") == "J，K.csv#23"
    assert subentry_candidate.get("index_entry_id") == "J，K.csv#24"
    assert subentry_candidate.get("sub_entry") == "as artistic director in Turin"
    assert main_row.get("decision") == "new" and not main_row.get("ku_id")
    assert sync.get_group(main_row.get("resolution_note", "")) == GROUP
    assert subentry_row.get("decision") == "undecided" and not subentry_row.get("ku_id")
    assert "index locator/page range is only a locator" in subentry_row.get("resolution_note", "")
    current_group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in current_group_rows] == [MAIN_CANDIDATE]
    assert not CARD.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    aliases = {"filippo juvarra", "juvarra, filippo", "filippo juvara", "filippo ivara"}
    assert not any(
        row.get("type") == "person"
        and (
            row.get("canonical_name", "").casefold() in aliases
            or row.get("name_en", "").casefold() in aliases
        )
        for row in manifest
    ), "same-identity person KU already exists in manifest"
    assert not any(
        row.get("candidate_id") in {MAIN_CANDIDATE, SUBENTRY_CANDIDATE} and row.get("external_source")
        for row in alignments
    ), "external identity record already exists for this group"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in BOOK_SOURCES:
        normalized_source = normalize((ROOT / item["source_file"]).read_text(encoding="utf-8-sig"))
        for _, quote in item["quotes"]:
            assert normalize(quote) in normalized_source, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources/03-Index/03-2-Index-CSV/J，K.csv")
    main_index = index_rows[int(main_candidate["index_entry_id"].split("#")[1])]
    subentry_index = index_rows[int(subentry_candidate["index_entry_id"].split("#")[1])]
    assert main_index.get("Main Entry") == "Juvarra, Filippo"
    assert main_index.get("Page Numbers") == "164, 165, 202, 296, 297"
    assert subentry_index.get("Main Entry") == "Juvarra, Filippo"
    assert subentry_index.get("Sub-entry") == "as artistic director in Turin"
    assert subentry_index.get("Page Numbers") == "296, 297"

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [row for row in statements if contains_candidate(row, MAIN_CANDIDATE)]
    relation_count = sum(
        row.get("qualifiers", {}).get("relation_candidate") is True
        for row in related
    )
    assert len(related) == 13 and relation_count == 12, (len(related), relation_count)
    assert not any(contains_candidate(row, SUBENTRY_CANDIDATE) for row in statements)

    planned_alignment = [dict(row) for row in alignments]
    target_main = next(
        row for row in planned_alignment
        if row.get("candidate_id") == MAIN_CANDIDATE and not row.get("external_source")
    )
    target_sub = next(
        row for row in planned_alignment
        if row.get("candidate_id") == SUBENTRY_CANDIDATE and not row.get("external_source")
    )
    main_s3_addition = (
        " S3 cross-chapter review (2026-10-16): cand-1340, index subentry "
        "'as artistic director in Turin' (J，K.csv#24, pp.296–297), is anchored by the same printed "
        "pages as the full-name statement 'the architect Filippo Juvarra was artistic director of the city' "
        "in ch.10. The main entry J，K.csv#23 and subentry #24 share the exact canonical name, and the "
        "subentry page range is contained in the main entry range. Grouped with cand-1340 under the same "
        "new-person identity group; this decision is supported by the body text, not the index locator alone."
    )
    assert "S3 cross-chapter review (2026-10-16)" not in target_main.get("resolution_note", "")
    target_main["resolution_note"] += main_s3_addition
    target_main["ku_id"] = KU_ID
    target_main["process_ref"] = "S3-full-book-2026-10-16"

    prior_undecided = target_sub.get("resolution_note", "")
    target_sub["decision"] = "new"
    target_sub["ku_id"] = KU_ID
    target_sub["process_ref"] = "S3-full-book-2026-10-16"
    target_sub["resolution_note"] = (
        "Prior S3 record (2026-10-15): " + prior_undecided
        + f" S3 cross-chapter review (2026-10-16): direct body evidence at "
        "02-sources/02-Markdown/10_CHP-10_intro.md#L330-331 (printed pp.296–297) explicitly names "
        "architect Filippo Juvarra as the artistic director of Turin; this is the exact role and page "
        "range named by index subentry J，K.csv#24. The main entry J，K.csv#23 has the same canonical "
        "name and includes pp.296–297 along with the ch.6 and ch.7 locations. Therefore the former "
        "index-only undecided candidate is now adjudicated as the same new source-local person group "
        f"as {MAIN_CANDIDATE}, not a separate person and not a forced index-only match. "
        f"group={GROUP}; S4 registration: mapped this group to {KU_ID}."
    )
    group_rows = [
        row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [MAIN_CANDIDATE, SUBENTRY_CANDIDATE]
    assert all(row.get("ku_id") == KU_ID for row in group_rows)

    used_alignment_ids = {
        int(match.group(1))
        for row in planned_alignment
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    }
    next_id = max(used_alignment_ids, default=0) + 1
    authority_rows = [
        {
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": MAIN_CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Treccani DBI",
            "external_id": TRECCANI_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: Tommaso Manfredi's DBI entry names Filippo Juvarra, born in Messina "
                "on 1678-03-27 and deceased in Madrid on 1736-01-31, and identifies his architectural career."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 1:04d}",
            "candidate_id": MAIN_CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Nationalmuseum",
            "external_id": NATIONALMUSEUM_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: the museum authority record identifies Filippo Juvarra as an Italian "
                "architect, gives Messina and Madrid as birth/death places and 1678–1736 as dates, "
                "and lists Juvara, Juarra, and Ivara variants."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 2:04d}",
            "candidate_id": MAIN_CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "National Gallery of Art",
            "external_id": NGA_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: the NGA identifies Filippo Juvarra as Sicilian, 1678–1736, and lists "
                "Juvara, Filippo and Ivara, Filippo as name variants."
            ),
        },
    ]
    planned_alignment.extend(authority_rows)

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    external_count = sum(bool(row.get("external_source")) for row in planned_alignment)
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(planned_manifest),
    )
    next_result, count_updates = re.subn(
        r"\d+(?=条外部身份记录单独保留)",
        str(external_count),
        next_result,
        count=1,
    )
    assert count_updates == 1, "could not refresh external identity record count"
    marker = "。各组来源、身份边界和映射更正见[过程记录]"
    assert next_result.count(marker) == 1
    result_insert = (
        f"；person 身份组 {GROUP}（{MAIN_CANDIDATE}、{SUBENTRY_CANDIDATE}）映射至"
        "[菲利波·尤瓦拉人物卡](../units/persons/filippo-juvarra.md)，12条关系候选留待 S6" + marker
    )
    next_result = next_result.replace(marker, result_insert, 1)

    note = (
        f"\n### S3-S4 person：{NAME_EN} 跨章身份组与索引子项裁决（{DATE}）\n\n"
        f"- {MAIN_CANDIDATE} 与 {SUBENTRY_CANDIDATE} → {GROUP} → {KU_ID}；主项 J，K.csv#23 列第6章 pp.164–165、"
        "第7章 p.202、第10章 pp.296–297；子项 J，K.csv#24 为“as artistic director in Turin”，页码仅296–297。"
        "第10章 p.296–297 正文直接称建筑师 Filippo Juvarra 为都灵城市艺术总监，职能与子项完全对应，且该页全名锚点也属于主项的页码范围。"
        "据同名、重叠页码和直接正文职能锚点，将 cand-1340 从上一轮的 index-only undecided 改判为与 cand-1339 同属一个 new-person 组；"
        "原未决理由保留在对齐记录中，当前理由说明正文锚点如何解除缺口。"
        f"Treccani DBI（Tommaso Manfredi, vol. 62, 2004; {TRECCANI_URL}）记 Filippo Juvarra 1678年生于 Messina、"
        "1736年1月31日卒于 Madrid，并记录其建筑师生涯。瑞典国家博物馆人物权威记录给出意大利建筑师、Messina / Madrid、1678–1736及 Juvara、Juarra、Ivara 异形；"
        "NGA 记 Sicilian、1678–1736，并列 Juvara、Ivara。姓名、日期、建筑师身份和跨章语境支持此单一人物组。"
        "未发现同身份既有 person KU；中文名为项目工作音译。\n"
        f"- cand-1339 涉及13条 S2 陈述，其中12条标为关系候选；均留待 S6 逐条审查。cand-1340 原为索引子项，没有独立 S2 statement；"
        "没有登记正式关系，也未开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"### S3-S4 person：{NAME_EN} 跨章身份组与索引子项裁决（{DATE}）" not in knowledge_text
    next_knowledge = knowledge_text + note
    next_accepted = insert_accepted(accepted)

    output = {
        ALIGNMENT: None,
        MANIFEST: None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
        CARD: card,
    }
    for path, headers, rows in (
        (ALIGNMENT, alignment_fields, planned_alignment),
        (MANIFEST, manifest_fields, planned_manifest),
    ):
        buffer = StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        output[path] = buffer.getvalue()

    protected_paths = [path for path in output if path != CARD]
    assert all(
        not path.with_name(path.name + BACKUP_SUFFIX).exists()
        for path in protected_paths
    )
    if args.dry_run:
        for path, updated in output.items():
            if path == CARD:
                print(f"--- create {CARD_REL} ({len(updated)} characters)")
                print("\n".join(updated.splitlines()[:22]))
                continue
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)),
                tofile=str(path.relative_to(ROOT)) + " (updated)",
                n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: group={GROUP}; members={','.join(row['candidate_id'] for row in group_rows)}; "
            f"main_statements={len(related)}; relation_candidates_pending={relation_count}; "
            f"external_records={external_count}; registered={totals['registered_groups']}/"
            f"{totals['registered_members']}; pending={totals['pending_groups']}/"
            f"{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    backups: list[tuple[Path, Path]] = []
    for path in protected_paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, updated in output.items():
            path.write_text(updated, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        if CARD.exists():
            CARD.unlink()
        raise
    print(
        f"applied: group={GROUP}; members={','.join(row['candidate_id'] for row in group_rows)}; "
        f"relation_candidates_pending={relation_count}; external_records={external_count}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
