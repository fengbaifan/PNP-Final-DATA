from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_person_relation_endpoints_allegrini_bouchardon_20261018 as person_sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s4-person-sagredo-family-endpoints-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index, S.csv."

DIA_URL = "https://dia.org/collection/madonna-and-child-adoring-figure/57076"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/niccolo-sagredo_(Enciclopedia-Italiana)/"
PRINCETON_URL = "https://artmuseum.princeton.edu/art/collections/objects/8051"

TARGETS = [
    {
        "candidate": "cand-2326",
        "group": "new-person:gherardo-sagredo-6252819bc6",
        "ku": "units/persons/gherardo-sagredo",
        "card": "04-knowledge/units/persons/gherardo-sagredo.md",
        "name_zh": "杰拉尔多·萨格雷多",
        "name_en": "Gherardo Sagredo",
        "index_file": "S.csv",
        "index_entry": "S.csv#14",
        "index_name": "Sagredo, Gherardo",
        "page": "263",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "location": "第9章，印刷页263–264；OCR L236、241、246",
        "quotes": [
            ("line 236; print p. 263", "leaving it to his nephew Gherardo"),
            ("line 241; print p. 264", "but after his death aged 49 in 1738"),
            ("line 246; print p. 264", "Girardo P.O Sagredio mio Amatissimo Nipote"),
        ],
        "summary": "Haskell称Gherardo为Zaccaria Sagredo的侄子和遗嘱中的受遗赠人，并说Gherardo去世后收藏开始面临散佚；引述遗嘱时拼作“Girardo P.O Sagredio”。",
        "description_zh": "本卡登记书后索引“Sagredo, Gherardo”所指人物。第9章称Gherardo是Zaccaria Sagredo的侄子，并引述遗嘱将其列为受遗赠人；同章称Zaccaria死后Gherardo继承收藏。遗嘱转录作“Girardo P.O Sagredio”，保留该原文异写。底特律艺术博物馆的一件绘画馆藏记录也将Gherardo Sagredo列在Zaccaria之后的收藏沿革中，该记录用于身份比对。中文显示名为项目工作音译。",
        "description_en": "This card records the person indexed as “Sagredo, Gherardo.” Chapter 9 calls Gherardo a nephew of Zaccaria Sagredo and quotes Zaccaria's will naming him as an heir; the chapter also describes the collection passing to Gherardo after Zaccaria's death. The will transcription reads “Girardo P.O Sagredio,” which is retained as a source variant. A Detroit Institute of Arts painting record also places Gherardo Sagredo after Zaccaria in the collection provenance and is used for identity comparison. The Chinese display name is a working transliteration.",
        "name_rows": [
            ("索引姓名", "Sagredo, Gherardo", "S1（索引 S.csv#14）"),
            ("遗嘱原文姓名异写", "Girardo P.O Sagredio", "S2（第9章，印刷页264，OCR L246）"),
        ],
        "relation_context_zh": "第9章叙述Gherardo为Zaccaria的侄子、继承其遗嘱安排，并在Zaccaria死后接掌收藏；这些关系候选留待S6，当前不登记正式关系。",
        "relation_context_en": "Chapter 9 describes Gherardo as Zaccaria's nephew and heir under the will, and says he succeeded to the collection after Zaccaria's death. These relation candidates remain for S6; no formal relation is registered here.",
        "relation_ids": [
            "st-chp9-p263264-gherardo-death-and-dispersal",
            "st-chp9-p263264-sagredo-death-gherardo",
            "st-chp9-p263264-will-arrangements-summary",
        ],
        "external_source": "Detroit Institute of Arts collection record",
        "external_id": DIA_URL,
        "external_decision": "same",
        "external_ku": "units/persons/gherardo-sagredo",
        "external_note": "Identity comparison only: the DIA record for accession 38.56 lists Zaccaria Sagredo followed by Gherardo Sagredo (d. 1738) in the provenance. Compared with Haskell's index S.csv#14 and ch. 9 pp. 263–264 naming Gherardo as Zaccaria's nephew and heir. The linked painting record supports the identity comparison; it does not independently validate the book's will account or collection history.",
        "identity_links": [
            (
                "Detroit Institute of Arts",
                "[collection record 38.56](" + DIA_URL + ")",
                "The provenance lists Gherardo Sagredo after Zaccaria; used for identity comparison.",
            )
        ],
        "s3_followup": "S3续核（2026-10-18）：DIA馆藏号38.56的沿革记录将Gherardo Sagredo列在Zaccaria之后，姓名及卒年与第9章对应；该作品沿革只支持身份比对，不把收藏转移叙述转成新关系事实。另查Princeton object x1948-601列Gherardo生卒年1691–1738，而Haskell p.264称其1738年去世时49岁；年龄差异留待后续事实核验，不改变本次身份分组。",
    },
    {
        "candidate": "cand-2327",
        "group": "new-person:niccolo-sagredo-52f2c679cd",
        "ku": "units/persons/niccolo-sagredo",
        "card": "04-knowledge/units/persons/niccolo-sagredo.md",
        "name_zh": "尼科洛·萨格雷多",
        "name_en": "Niccolò Sagredo",
        "index_file": "S.csv",
        "index_entry": "S.csv#15",
        "index_name": "Sagredo, Niccolò",
        "page": "152, 263, 264",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "location": "第9章，印刷页263–264；OCR L234、243；另见第6章第I节，印刷页152、OCR L70",
        "quotes": [
            ("line 234; print p. 263", "his nephew the young Zaccaria"),
            ("line 234; print p. 263", "Doges, Niccolò"),
            ("line 243; print p. 264", "painted for Doge Niccolò"),
        ],
        "additional_source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
        "additional_location": "第6章第I节，印刷页152；OCR L70",
        "additional_quote": ("line 70; print p. 152", "wrote Niccolò Sagredo in 1661"),
        "summary": "第6章以全名“Niccolò Sagredo”标识1661年的引文发言者；第9章称Niccolò为Doge并为Zaccaria的叔父，第9章另称一组Borgognone战景为Doge Niccolò绘制。Treccani人物条目记载Niccolò Sagredo于1675年当选威尼斯总督。",
        "description_zh": "本卡登记书后索引“Sagredo, Niccolò”所指人物。第6章以全名Niccolò Sagredo标识一段1661年的引文；第9章称同名人物为Doge，并称其是年轻Zaccaria的叔父，另将一组Borgognone战景归于Doge Niccolò。Treccani人物条目中的Niccolò Sagredo也于1675年当选威尼斯总督，与书中姓名、职位和年份相合。中文显示名为项目工作音译。",
        "description_en": "This card records the person indexed as “Sagredo, Niccolò.” Chapter 6 identifies the speaker of a 1661 quotation as Niccolò Sagredo. Chapter 9 calls a Niccolò a Doge and uncle of the young Zaccaria, and separately attributes a group of Borgognone battle scenes to Doge Niccolò. Treccani's biographical entry for Niccolò Sagredo also records his election as Doge of Venice in 1675, matching the book's name, office, and year. The Chinese display name is a working transliteration.",
        "name_rows": [
            ("索引姓名", "Sagredo, Niccolò", "S1（索引 S.csv#15）"),
            ("正文全名", "Niccolò Sagredo", "S2（第6章第I节，印刷页152，OCR L70）"),
        ],
        "relation_context_zh": "第9章将Niccolò与年轻Zaccaria描述为叔父和侄子，并将Borgognone的战景与Doge Niccolò相连；亲缘与作品关系候选均留待S6。",
        "relation_context_en": "Chapter 9 describes Niccolò as uncle to the young Zaccaria and associates Doge Niccolò with Borgognone's battle scenes. The kinship and artwork relation candidates remain for S6.",
        "relation_ids": ["st-chp9-p263264-niccolo-and-zaccaria-kinship"],
        "external_source": "Treccani, Enciclopedia Italiana",
        "external_id": TRECCANI_URL,
        "external_decision": "same",
        "external_ku": "units/persons/niccolo-sagredo",
        "external_note": "Identity comparison only: Mario Brunetti's Treccani entry “SAGREDO, Niccolò” identifies a Venetian Doge, born in 1606 and elected on 6 February 1675. The name, office, and election year match Haskell's index S.csv#15 and ch. 9 p. 263. The entry supports identification of the person, not the separate kinship or artwork claims in Haskell.",
        "identity_links": [
            (
                "Treccani, Enciclopedia Italiana",
                "[SAGREDO, Niccolò](" + TRECCANI_URL + ")",
                "Biographical identity and Doge election in 1675; not used to validate Haskell's kinship or artwork claims.",
            )
        ],
        "s3_followup": "S3续核（2026-10-18）：Treccani《Enciclopedia Italiana》Mario Brunetti撰“SAGREDO, Niccolò”记其为威尼斯总督并于1675年当选；书中第6章p.152的全名和第9章p.263的总督称谓、当选年份与之相合。cand-2327与既有Zaccaria Sagredo及其父Stefano保持分立。",
    },
    {
        "candidate": "cand-2328",
        "group": "new-person:sagredo-stefano-fce8efdd59",
        "ku": "units/persons/stefano-sagredo",
        "card": "04-knowledge/units/persons/stefano-sagredo.md",
        "name_zh": "斯特法诺·萨格雷多",
        "name_en": "Stefano Sagredo",
        "index_file": "S.csv",
        "index_entry": "S.csv#16",
        "index_name": "Sagredo, Stefano",
        "page": "263n",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "location": "第9章，印刷页263注1；OCR L414",
        "quotes": [("line 414; print p. 263, n. 1", "the son of Stessano Sagredo and Vienna Foscarini")],
        "summary": "Haskell转述Barbaro称Zaccaria Sagredo于1653年出生，是Stessano Sagredo与Vienna Foscarini之子；S2页图校读将姓名记作“Steffano Sagredo”，书后索引写作“Stefano”。",
        "description_zh": "本卡登记书后索引“Sagredo, Stefano”所指人物。第9章注1转述Barbaro称Zaccaria Sagredo是Stessano Sagredo与Vienna Foscarini之子；S2记录原文OCR作“Stessano”，页图校读作“Steffano”。本卡保留索引主名与脚注异写，不以一种拼法覆盖另一种。中文显示名为项目工作音译。",
        "description_en": "This card records the person indexed as “Sagredo, Stefano.” Chapter 9 note 1 quotes Barbaro as naming Stessano Sagredo and Vienna Foscarini as Zaccaria Sagredo's parents. S2 records the OCR form “Stessano” and the page-image reading “Steffano.” This card preserves the index name and note variants without replacing one spelling with another. The Chinese display name is a working transliteration.",
        "name_rows": [
            ("索引姓名", "Sagredo, Stefano", "S1（索引 S.csv#16）"),
            ("脚注OCR姓名异写", "Stessano Sagredo", "S2（第9章，印刷页263注1，OCR L414）"),
            ("页图校读姓名异写", "Steffano Sagredo", "S2（第9章，印刷页263注1；页图校读，详见过程记录）"),
        ],
        "relation_context_zh": "脚注转述Barbaro对Zaccaria父母的记载，正文又称Zaccaria在父亲去世后继承家族支系首领位置；与Stefano相关的关系候选留待S6。",
        "relation_context_en": "The footnote reports Barbaro's account of Zaccaria's parents, and the chapter says Zaccaria became head of his family branch after his father's death. The relation candidate involving Stefano remains for S6.",
        "relation_ids": ["st-chp9-p263264-zaccaria-head-of-branch-and-late-passion"],
        "external_source": "Princeton University Art Museum",
        "external_id": PRINCETON_URL,
        "external_decision": "undecided",
        "external_ku": "",
        "external_note": "External identity comparison remains undecided: the museum's provenance record describes a possible chain involving Nicolò Sagredo, his brother Stefano, and Stefano's son Zaccaria, but marks the descent as possible and gives Zaccaria's dates as 1633–1729, whereas Haskell's cited Barbaro note says he was born in 1653. The page is retained as a comparison lead, not accepted as a match or used to overwrite the book's name forms or dates. The source-local S3 new-person group remains supported by index S.csv#16 and the p. 263 note's father reference.",
        "identity_links": [],
        "s3_followup": "S3续核（2026-10-18）：索引S.csv#16给出“Sagredo, Stefano”；第9章p.263注1转述Barbaro称Zaccaria为Stessano Sagredo之子，既有S2页图校读记该姓名为“Steffano”。三种拼写按索引名、OCR与页图读法保留，指向同一书内父辈人物。对照Princeton University Art Museum object x1948-601时，其来源链虽列Niccolò之弟Stefano及Zaccaria之父，但以“possibly”限定沿承，且将Zaccaria生年列为1633，与书中转引的1653不合；该外部对应记为undecided，不据此改动书内身份或生年。",
    },
]


def source_record(citation: str, location: str, summary: str, file: str, span: str, quotes: list[tuple[str, str]]) -> dict:
    return {
        "citation": citation,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": qspan, "text": quote} for qspan, quote in quotes],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": file,
            "source_span": "; ".join(qspan for qspan, _ in quotes),
        },
    }


def make_card(t: dict) -> str:
    sources = [
        source_record(
            INDEX_CITATION,
            f"书后索引 {t['index_entry']}；所列页码{t['page']}",
            f"索引主项为“{t['index_name']}”，页码指向{t['page']}。",
            f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}",
            t["index_entry"],
            [(t["index_entry"], t["index_name"])],
        )
    ]
    if t["candidate"] == "cand-2327":
        sources.append(
            source_record(
                BOOK,
                t["additional_location"],
                "第6章以全名标识Niccolò Sagredo为1661年引文的发言者。",
                t["additional_source_file"],
                t["additional_quote"][0],
                [t["additional_quote"]],
            )
        )
    sources.append(source_record(BOOK, t["location"], t["summary"], t["source_file"], "; ".join(q[0] for q in t["quotes"]), t["quotes"]))
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    index_link = f"../../../02-sources/03-Index/03-2-Index-CSV/{t['index_file']}"
    book_link = f"../../../{t['source_file']}"
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in t["name_rows"])
    identity = ""
    if t["identity_links"]:
        identity_items = "\n".join(f"- **{name}：** {link}；{scope}" for name, link, scope in t["identity_links"])
        identity = f"\n### 身份与外部链接\n\n{identity_items}\n"
    relation_list = "、".join(f"`{sid}`" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']} [索引 {t['index_entry']}]({index_link}) [书内语境]({book_link})

**English:** {t['description_en']} [index {t['index_entry']}]({index_link}) [book passage]({book_link})

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{name_rows}

### 本书相关内容

**中文：** {t['relation_context_zh']} [书内语境]({book_link})

**English:** {t['relation_context_en']} [book passage]({book_link})

## 关系与证据
{identity}
### 关系记录

当前没有登记在 `relations.csv` 中的正式关系。直接S2关系候选 {relation_list} 留待S6审查；本次S4登记不创建正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three distinct Sagredo person groups as S4 relation endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = sync.load_statements()

    for t in TARGETS:
        cid = t["candidate"]
        candidate = candidate_by_id[cid]
        base = [row for row in alignments if row.get("candidate_id") == cid and not row.get("external_source")]
        assert len(base) == 1, (cid, len(base))
        assert candidate.get("suggested_type") == "person"
        assert base[0].get("decision") == "new" and not base[0].get("ku_id")
        assert sync.get_group(base[0].get("resolution_note", "")) == t["group"]
        group_members = [row["candidate_id"] for row in alignments if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]]
        assert group_members == [cid], (t["group"], group_members)
        assert candidate.get("index_entry_id") == t["index_entry"]
        assert candidate.get("canonical_name") == t["index_name"]
        assert candidate.get("index_page_range", "") == t["page"]
        index = person_sync.read_index_rows(t["index_file"])[int(t["index_entry"].split("#")[1])]
        assert index.get("Main Entry") == t["index_name"] and index.get("Page Numbers", "") == t["page"]
        index_row = person_sync.read_index_rows(t["index_file"])[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"]
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold() for row in manifest)
        assert not any(row.get("candidate_id") == cid and row.get("external_source") == t["external_source"] for row in alignments)
        source_text = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        assert all(quote in source_text for _, quote in t["quotes"])
        if t["candidate"] == "cand-2327":
            assert t["additional_quote"][1] in (ROOT / t["additional_source_file"]).read_text(encoding="utf-8-sig")
        direct = {row["statement_id"] for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))}
        assert direct == set(t["relation_ids"]), (cid, direct)

    stefano_mention = next(row for row in sync.read_csv(TABLES / "mentions.csv")[1] if row.get("mention_id") == "m-chp9-p263264-stessano-sagredo")
    assert "scan reads Steffano Sagredo" in stefano_mention.get("note", "")

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    planned_accepted = list(accepted_lines)
    max_alignment_id = max((int(match.group(1)) for row in alignments if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))), default=0)
    external_rows = []
    for t in TARGETS:
        base = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        base["ku_id"] = t["ku"]
        base["process_ref"] = PROCESS_REF
        base["resolution_note"] = base.get("resolution_note", "").rstrip() + " " + t["s3_followup"] + f" S4登记（{DATE}）：该source-local身份组映射至{t['ku']}。"
        max_alignment_id += 1
        ext = {
            "alignment_id": f"aln-{max_alignment_id}",
            "candidate_id": t["candidate"],
            "ku_id": t["external_ku"],
            "external_source": t["external_source"],
            "external_id": t["external_id"],
            "decision": t["external_decision"],
            "accessed_date": DATE,
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": t["external_note"],
        }
        external_rows.append(ext)
        planned_alignments.append(ext)
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
        planned_accepted = person_sync.insert_accepted(planned_accepted, t["card"])
    planned_manifest.sort(key=lambda row: row["ku_id"])

    baseline = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == baseline["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == baseline["person"]["registered_members"] + len(TARGETS)
    assert stats["person"]["pending_groups"] == baseline["person"]["pending_groups"] - len(TARGETS)
    assert stats["person"]["pending_members"] == baseline["person"]["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    external_outcomes = "；".join(f"{t['candidate']} → {t['external_decision']}（{t['external_source']}）" for t in TARGETS)
    endpoint_lines = [f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；索引{t['index_entry']}、{t['location']}；{t['s3_followup']}" for t in TARGETS]
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份复核与S4人物直接端点登记：Sagredo三位人物（{DATE}）\n\n"
        + "\n".join(endpoint_lines)
        + "\n\n外部记录结论：" + external_outcomes + "。Niccolò、Stefano、Gherardo分别对应不同身份组；Stefano的Princeton馆藏沿革仅作未决比对，保留其对Zaccaria生年的冲突，不改写书内原名和日期。五条直接S2关系候选留待S6审查，未新增formal relation。"
        + f"\n\n登记脚本 `{Path(__file__).name}` 与姓名字段脚本 `register_s4_person_name_fields_sagredo_family_20261018.py` 均先dry-run后apply。"
        + f"\n\n登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        + f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        + f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S3复核与S4人物登记：Sagredo三位人物（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。三位均为各自独立的S3 new身份组，各登记一张KU；Niccolò与Gherardo的外部身份对应已记录，Stefano的Princeton馆藏沿革映射仍为undecided，书内索引、注释及页图拼写差异保留。Princeton记录与Haskell对Zaccaria生年（1633／1653）的记载不一，且Princeton对Gherardo列1691–1738，Haskell称其1738年去世时49岁；这些日期与年龄差异留待S5事实核验，不作为身份冲突裁决。五条关系候选留待S6，不新增正式关系。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: distinct_person_groups=3; candidate_mappings=3; external_rows=3 "
            f"(same=2, undecided=1); index/source/variant checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
            f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
            f"KU={len(planned_manifest)}; relation_candidates=5; relation_rows_added=0; no files changed"
        )
        return 0

    for path, card in cards.items():
        (ROOT / path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=3; candidate_mappings=3; external_rows=3 (same=2, undecided=1); "
        f"KU={len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
        "relation_candidates=5; relation_rows_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
