from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_person_relation_endpoints_allegrini_bouchardon_20261018 as person_sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
SOURCES_PATH = TABLES / "sources.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s4-schut-segala-serlio-skala-person-endpoints-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BATCH_TITLE = "Schut、Segala、Serlio、Skala四组直接端点登记"
BATCH_PROCESS_NOTE = (
    "四组均为S3 new单候选身份组，登记4张KU卡、4条候选映射和8条source_backed姓名字段。"
    "Skala的雕像对象建议与Padua学生描述保留perhaps和问句限定；Schut的数百件作品数量保留为多人集合总量。"
    "本批不新增外部来源、正式关系或backlog项目。"
)
BATCH_RESULT_NOTE = "。五条S2关系候选继续待S6；Skala相关两条保留原文的试探语气。"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def book_source(source_file: str, location: str, span: str, quote: str, summary: str) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    }


def index_source(t: dict) -> dict:
    index_file = t["index_entry"].split("#", 1)[0]
    page = t.get("index_page", "")
    if page:
        location = f"书后索引，{t['index_entry']}；指向印刷页{page}"
        summary = f"索引以“{t['index_name']}”为主条并指向印刷页{page}。"
    else:
        location = f"书后索引，{t['index_entry']}；该索引行未列页码"
        summary = f"索引以“{t['index_name']}”为主条；该索引行未列页码。"
    return {
        "citation": f"Francis Haskell, *Patrons and Painters*, index, {index_file}.",
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/03-Index/03-2-Index-CSV/{index_file}",
            "source_span": t["index_entry"],
        },
    }


TARGETS = [
    {
        "candidate": "cand-2415",
        "group": "new-person:corneille-schut-c477be65d5",
        "ku": "units/persons/corneille-schut",
        "card": "04-knowledge/units/persons/corneille-schut.md",
        "name_zh": "科内利斯·舒特",
        "name_en": "Corneille Schut",
        "index_entry": "S.csv#103",
        "index_name": "Schut, Corneille",
        "index_page": "206",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "book_source": book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_i.md",
            "第8章第1节，印刷页206，行34–36",
            "lines 34–36; print p. 206",
            "and he owned several hundreds by Paul Brill,\n"
            "Peter de Witte, Velvet Breughel, Leonard Bramer, Jacques Duyvelant, Cornelius\n"
            "Poelenburgh, Corneille Schut, Gioffredo Wals, Gerard van dor Bos and many others.",
            "Haskell列举Roomer所藏作品的作者，其中包括Corneille Schut；“数百件”指该段列举的多人作品总量。",
        ),
        "name_rows": [
            ("索引姓名", "Schut, Corneille", "S1，S.csv#103"),
            ("正文姓名", "Corneille Schut", "S2，第8章，p.206，L36"),
        ],
        "relation_ids": ["st-chp8-p206-roomer-owned-hundreds-by-flemish-artists"],
        "description_zh": (
            "本卡登记书后索引作“Schut, Corneille”、第8章具名的Corneille Schut。"
            "Haskell在叙述Roomer藏画时将他列入作品作者名单，并称Roomer藏有数百件由包括Schut在内诸人创作的作品；"
            "该数量是多人作品总量，不表示Schut个人作品数量。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Corneille Schut, indexed as “Schut, Corneille” and named in Chapter 8. "
            "In discussing Roomer's collection, Haskell lists Schut among the makers of works owned by Roomer and says the collection included several hundred works by the named artists. "
            "That number describes the works collectively and is not a count of Schut's individual works. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "关系候选将Schut列入Roomer所藏画作的多人作者名单；作品数量和归属范围保持原书的集合表述，候选留待S6。"
        ),
        "context_en": (
            "The relation candidate includes Schut in a group of makers whose pictures Roomer owned. "
            "The number and ownership scope remain the book's collective statement; the candidate remains for S6 review."
        ),
    },
    {
        "candidate": "cand-2417",
        "group": "new-person:giovanni-segala-c9998cedb7",
        "ku": "units/persons/giovanni-segala",
        "card": "04-knowledge/units/persons/giovanni-segala.md",
        "name_zh": "乔瓦尼·塞加拉",
        "name_en": "Giovanni Segala",
        "index_entry": "S.csv#105",
        "index_name": "Segala, Giovanni",
        "index_page": "227",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "book_source": book_source(
            "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
            "第8章第2节，印刷页227，行195–196",
            "lines 195–196; print p. 227",
            "The artists he had chosen—Marchesini himself, Lazzarini,\n"
            "Balestra, Fumiani, Bellucci, Angiolo Trevisani, Segala, Dal Sole and Franceschini—",
            "Haskell列出Conti为画廊挑选的画家，名单中包括Segala。",
        ),
        "name_rows": [
            ("索引姓名", "Segala, Giovanni", "S1，S.csv#105"),
            ("正文姓名形式", "Segala", "S2，第8章，p.227，L196"),
        ],
        "relation_ids": ["st-chp8-p227-gallery-academic-style"],
        "description_zh": (
            "本卡登记书后索引作“Segala, Giovanni”、第8章具名的Giovanni Segala。"
            "Haskell将Segala列入Conti为画廊挑选的画家，并称该组画家属于同一代，多数遵循“correct”素描与浅金色调。"
            "此处只记录书内名单与评价，不据此补充个人生平。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Giovanni Segala, indexed as “Segala, Giovanni” and named in Chapter 8. "
            "Haskell includes Segala among the painters Conti selected for a gallery and says the group belonged to the same generation, "
            "with most adhering to “correct” drawing and blond tonality. The card adds no individual biography from this passage. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "关系候选将Segala列入Conti为画廊挑选的画家名单；关于同代与风格的评价仍按原文集体限定，候选待S6。"
        ),
        "context_en": (
            "The relation candidate places Segala in the group of painters Conti selected for a gallery. "
            "The generation and style comments retain their collective qualification; the candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2419",
        "group": "new-person:sebastiano-serlio-9c5888fd05",
        "ku": "units/persons/sebastiano-serlio",
        "card": "04-knowledge/units/persons/sebastiano-serlio.md",
        "name_zh": "塞巴斯蒂亚诺·塞尔里奥",
        "name_en": "Sebastiano Serlio",
        "index_entry": "S.csv#107",
        "index_name": "Serlio, Sebastiano",
        "index_page": "103",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "book_source": book_source(
            "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
            "第4章第2节，印刷页103，行50–51",
            "lines 50–51; print p. 103",
            "Brunelleschi, Buonarotti,\n"
            "Bramante, Serlio, Palladio, Vignola and the other restorers of this great art, who took the true proportions of those perfectly regular orders from Roman buildings.",
            "Haskell引述Cassiano，将Serlio列在一组从罗马建筑获取规则建筑式样比例的建筑艺术复兴者之中。",
        ),
        "name_rows": [
            ("索引姓名", "Serlio, Sebastiano", "S1，S.csv#107"),
            ("正文姓名形式", "Serlio", "S2，第4章，p.103，L50–51"),
        ],
        "relation_ids": ["st-chp4-sec-ii-l46-51-restorers-took-proportions-from-roman-buildings"],
        "description_zh": (
            "本卡登记书后索引作“Serlio, Sebastiano”、第4章引文提及的Sebastiano Serlio。"
            "Haskell引述Cassiano，把Serlio与Brunelleschi、Buonarotti、Bramante、Palladio和Vignola等并列，"
            "称这组建筑艺术复兴者从罗马建筑取得规则式样的比例。该表述保留为引文中的集合主张，不拆作已核实的个人经历。"
            "中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Sebastiano Serlio, indexed as “Serlio, Sebastiano” and named in a Chapter 4 quotation. "
            "Haskell quotes Cassiano, who lists Serlio with Brunelleschi, Buonarotti, Bramante, Palladio, and Vignola, "
            "saying that this group of restorers of the art took the proportions of regular orders from Roman buildings. "
            "The statement remains a collective claim within the quotation, not a separately verified personal biography. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "Cassiano引文中的集合关系候选把Serlio列在建筑艺术复兴者名单中；不补造其个人作品或具体建筑对应，候选待S6。"
        ),
        "context_en": (
            "The collective relation candidate lists Serlio among restorers of architectural art. "
            "No individual work or building attribution is added; the candidate remains for S6."
        ),
    },
    {
        "candidate": "cand-2436",
        "group": "new-person:dubravio-giovanni-skala-b564631145",
        "ku": "units/persons/giovanni-dubravio-skala",
        "card": "04-knowledge/units/persons/giovanni-dubravio-skala.md",
        "name_zh": "乔瓦尼·杜布拉维奥·斯卡拉",
        "name_en": "Giovanni Dubravio Skala",
        "index_entry": "S.csv#125",
        "index_name": "Skala, Giovanni Dubravio",
        "index_page": "367",
        "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "book_source": book_source(
            "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
            "第15章第2节，印刷页367，行34",
            "line 34; print p. 367",
            "Giovanni Dubravio Skala, perhaps, from Pilsen, the first German student to study at Padua after the League of Cambrai?",
            "Haskell以perhaps提出Skala可能是Waldstein雕像的对象之一；同一带问号的句子称其来自Pilsen，并询问他是否为坎布雷同盟之后首位在Padua学习的德国学生。",
        ),
        "name_rows": [
            ("索引姓名", "Skala, Giovanni Dubravio", "S1，S.csv#125"),
            ("正文姓名", "Giovanni Dubravio Skala", "S2，第15章，p.367，L34"),
        ],
        "relation_ids": [
            "st-chp15-p367-skala-possible-statue-subject",
            "st-chp15-p367-skala-student-description",
        ],
        "description_zh": (
            "本卡登记书后索引作“Skala, Giovanni Dubravio”、第15章具名的Giovanni Dubravio Skala。"
            "Haskell在讨论Waldstein雕像可能对象时写作“Giovanni Dubravio Skala, perhaps”；"
            "同一问句称其来自Pilsen，并提出他是否为坎布雷同盟之后首位在Padua学习的德国学生。"
            "雕像对象与学生身份均保留原文的试探语气。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records Giovanni Dubravio Skala, indexed as “Skala, Giovanni Dubravio” and named in Chapter 15. "
            "When discussing a possible subject for a Waldstein statue, Haskell writes “Giovanni Dubravio Skala, perhaps”; "
            "the same question says he was from Pilsen and asks whether he was the first German student to study at Padua after the League of Cambrai. "
            "Both the statue identification and the student description retain the source's tentative wording. "
            "The Chinese display name is a project working transliteration."
        ),
        "context_zh": (
            "两条候选分别涉及可能的雕像对象和带问号的Padua学生描述；均不改写为确定身份或经历，留待S6裁决。"
        ),
        "context_en": (
            "The two candidates concern a possible statue subject and a question-marked description of study at Padua. "
            "Neither is turned into a definite identification or life fact; both remain for S6."
        ),
    },
]


def make_card(t: dict) -> str:
    sources = [index_source(t), *t.get("book_sources", [t.get("book_source")])]
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
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in t["name_rows"])
    relation_ids = "、".join(t["relation_ids"])
    if relation_ids:
        relation_record = (
            f"当前没有登记在 relations.csv 中的正式关系。S2关系候选 {relation_ids} 保留原书归因和限制，"
            "留待S6逐条裁决；本次S4身份登记不将其转为正式关系。"
        )
    else:
        relation_record = (
            "当前没有登记在 relations.csv 中的正式关系。本卡未关联到可归于该身份组的S2关系候选；"
            "不从同段共现或索引提及生成正式关系。"
        )
    type_sections = t.get("type_sections", "")
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}

**English:** {t['description_en']}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{rows}

{type_sections}
### 本书相关内容

**中文：** {t['context_zh']}

**English:** {t['context_en']}

## 关系与证据

### 关系记录

{relation_record}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four S-index person endpoint groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(candidate_by_id) == len(alignment_by_id)
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(manifest_by_ku) == len(manifest)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = sync.load_statements()

    for t in TARGETS:
        cid = t["candidate"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        assert candidate.get("index_entry_id") == t["index_entry"]
        assert candidate.get("canonical_name") == t.get("candidate_name", t["index_name"])
        assert candidate.get("index_page_range") == t["index_page"]
        index_file = t["index_entry"].split("#", 1)[0]
        index_rows = person_sync.read_index_rows(index_file)
        index_row = index_rows[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        for book_source_record in t.get("book_sources", [t.get("book_source")]):
            evidence_file = book_source_record.get("evidence_ref", {}).get("source_file", t["source_file"])
            source_body = (ROOT / evidence_file).read_text(encoding="utf-8-sig")
            assert book_source_record["original_quotes"][0]["text"] in source_body
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths
        assert not (ROOT / t["card"]).exists()
        assert not any(
            row.get("type") == "person"
            and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
            for row in manifest
        )
        related = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (
                cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
                or cid in (row.get("qualifiers") or {}).get("mentioned_candidate_ids", [])
            )
        }
        # `mentioned_candidate_ids` may cover every entity in a whole segment,
        # even when a relation candidate concerns only one sentence or another
        # person in that segment. `relation_ids` is the semantically selected
        # list for this identity; require each selected statement to be present
        # without treating every co-mentioned candidate as a relation endpoint.
        assert set(t["relation_ids"]) <= related, (cid, related, set(t["relation_ids"]))

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(
            row for row in planned_alignments
            if row.get("candidate_id") == t["candidate"] and not row.get("external_source")
        )
        row["ku_id"] = t["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + (
            f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；"
            "新增一张书内来源支持的人物KU，相关S2关系候选仍待S6。"
        )
        planned_manifest.append({
            "ku_id": t["ku"],
            "type": "person",
            "canonical_name": t["name_zh"],
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": t["card"],
        })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = person_sync.insert_accepted(planned_accepted, t["card"])
    assert len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}) == len(accepted_paths) + len(TARGETS)

    baseline = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == baseline["person"]["registered_groups"] + 4
    assert stats["person"]["registered_members"] == baseline["person"]["registered_members"] + 4
    assert stats["person"]["pending_groups"] == baseline["person"]["pending_groups"] - 4
    assert stats["person"]["pending_members"] == baseline["person"]["pending_members"] - 4
    assert len(planned_manifest) == len(manifest) + 4
    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    with tempfile.TemporaryDirectory(prefix="pnp-s4-s-index-persons-") as temp_dir:
        selected_manifest = []
        for t in TARGETS:
            temp_card = Path(temp_dir) / f"{t['ku'].split('/')[-1]}.md"
            temp_card.write_text(cards[t["card"]], encoding="utf-8")
            selected_manifest.append({"ku_id": t["ku"], "card_path": str(temp_card)})
        additions, source_registry, warnings, cards_with_tables = extract_records(selected_manifest)
    assert cards_with_tables == 4 and not warnings, warnings
    expected_name_rows = sum(len(t["name_rows"]) for t in TARGETS)
    expected_additional_rows = sum(t.get("additional_field_rows", 0) for t in TARGETS)
    assert len(additions) == expected_name_rows + expected_additional_rows
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert all(row.get("source_ids") == ["haskell-1980-rev-ed"] and row.get("source_ref") for row in additions)

    current_enrichment = [
        json.loads(line) for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()
    ]
    assert not any(row.get("ku_id") in {t["ku"] for t in TARGETS} for row in current_enrichment)
    assign_ids(additions, ENRICHMENT_PATH)
    current_ids = {row.get("enrichment_id") for row in current_enrichment}
    current_occurrences = {row.get("occurrence_id") for row in current_enrichment}
    for row in additions:
        assert row.get("enrichment_id") not in current_ids
        assert row.get("occurrence_id") not in current_occurrences
        current_ids.add(row.get("enrichment_id"))
        current_occurrences.add(row.get("occurrence_id"))
    planned_enrichment = current_enrichment + additions
    source_rows = sync.read_csv(SOURCES_PATH)[1]
    source_ids = {row["source_id"] for row in source_rows}
    assert set(source_registry) == {"haskell-1980-rev-ed"}
    assert set(source_registry) <= source_ids

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_lines = []
    for t in TARGETS:
        relation_note = (
            f"S2关系候选{'、'.join(t['relation_ids'])}留待S6。"
            if t["relation_ids"]
            else "无可归属于本身份组的S2关系候选；不从同段共现或索引提及生成正式关系。"
        )
        process_lines.append(
            f"- {t['candidate']}（{t['group']}）→ [{t['name_zh']}（{t['name_en']}）]"
            f"(../../../{t['card']})；{relation_note}{t['context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：{BATCH_TITLE}（{DATE}）\n\n"
        + "\n".join(process_lines)
        + f"\n\n{BATCH_PROCESS_NOTE}\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    external_total = sum(bool(row.get("external_source")) for row in planned_alignments)
    result_text, count = re.subn(
        r"^\| \[全书对齐\].*$",
        f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(len(planned_alignments))} 条："
        f"{sync.fmt(len(candidates))} 条候选决定记录及 {sync.fmt(external_total)} 条外部身份记录；候选决定数见下表 |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert count == 1
    unverified = sum(row.get("evidence_status") == "unverified" for row in planned_enrichment)
    result_text, count = re.subn(
        r"^\| \[既有字段表\].*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_enrichment))}条，其中"
        f"{sync.fmt(unverified)}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert count == 1
    batch_result = (
        f"### S4 人物身份组登记：{BATCH_TITLE}（{DATE}）\n\n"
        + "；".join(f"{t['candidate']} → ../units/persons/{t['ku'].split('/')[-1]}.md" for t in TARGETS)
        + BATCH_RESULT_NOTE
        + f"S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射已登记，"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记；KU={len(planned_manifest)}。"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, batch_result + "\n\n" + marker, 1)

    enrichment_text = "\n".join(json.dumps(row, ensure_ascii=False) for row in planned_enrichment) + "\n"
    outputs = {
        ACCEPTED_PATH: "\n".join(planned_accepted) + "\n",
        PROCESS_PATH: process_text,
        RESULT_PATH: result_text,
        ENRICHMENT_PATH: enrichment_text,
        **{ROOT / path: content for path, content in cards.items()},
    }

    if args.dry_run:
        print(
            f"dry-run passed: groups=4; cards=4; candidate_mappings=4; name_rows={expected_name_rows}; "
            f"additional_fields={expected_additional_rows}; enrichment_rows={len(additions)}; "
            f"relation_candidates={sum(len(t['relation_ids']) for t in TARGETS)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; "
            f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
            f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
            f"enrichment={len(current_enrichment)}->{len(planned_enrichment)}; KU={len(planned_manifest)}; "
            "external_sources_added=0; formal_relations_added=0; no files changed"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    for path, content in outputs.items():
        if path == ACCEPTED_PATH:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
        elif path in {PROCESS_PATH, RESULT_PATH}:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print(
        f"applied: groups=4; candidate_mappings=4; name_rows={expected_name_rows}; "
        f"additional_fields={expected_additional_rows}; enrichment_rows={len(additions)}; "
        f"relation_candidates={sum(len(t['relation_ids']) for t in TARGETS)}; "
        f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
        f"enrichment={len(current_enrichment)}->{len(planned_enrichment)}; KU={len(planned_manifest)}; "
        "external_sources_added=0; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
