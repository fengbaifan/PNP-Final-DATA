from __future__ import annotations

import argparse
import csv
import io
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
import register_s4_person_m_index_endpoints_20261018 as common  # noqa: E402
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

sync = common.sync
process_sync = common.process_sync

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
SOURCES_PATH = TABLES / "sources.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
INDEX_PATH = "02-sources/03-Index/03-2-Index-CSV/M.csv"
ANCHOR = "s3-s4-person-montage-endpoints-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

TARGETS = [
    {
        "candidate": "cand-1673",
        "group": "new-person:alvise-doge-mocenigo-112023801c",
        "ku": "units/persons/alvise-mocenigo",
        "card": "04-knowledge/units/persons/alvise-mocenigo.md",
        "name_zh": "阿尔维塞·莫切尼戈",
        "name_en": "Alvise Mocenigo",
        "index_entry": "M.csv#213",
        "index_label": "Mocenigo, Doge Alvise",
        "index_name": "Mocenigo, Doge Alvise",
        "index_pages": "269n",
        "chapter": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页269，注1；OCR L91",
        "summary": "Haskell称圣斯泰教堂于1709年以Doge Alvise Mocenigo的遗赠款修建外立面；书内没有提供进一步的在任序号。",
        "quotes": [
            ("line 91; print p. 269 n. 1", "a legacy of Doge Alvise Mocenigo"),
        ],
        "name_rows": [
            ("索引姓名与头衔", "Mocenigo, Doge Alvise", "S1"),
            ("正文称名与头衔", "Doge Alvise Mocenigo", "S2"),
            ("展示姓名", "Alvise Mocenigo", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#213所列的Doge Alvise Mocenigo。第9章p.269注1称圣斯泰教堂于1709年以其遗赠款修建外立面。原书未提供在任序号或更具体的身份信息，因此本卡限于书内人物指称，不补入未经本书支持的身份数据。中文名为项目工作音译。",
        "description_en": "This card records the Doge Alvise Mocenigo indexed at M.csv#213. Chapter 9, p. 269 n. 1, says that a legacy of his funded the façade of S. Stae in 1709. The book gives no regnal ordinal or further identifying detail, so this card stays with the source-local person reference and adds no unsupported identity data. The Chinese display name is a project working transliteration.",
        "context_zh": "第9章p.269注1将S. Stae于1709年修建外立面与Doge Alvise Mocenigo的遗赠款相连；关系候选留待S6审查。",
        "context_en": "Chapter 9, p. 269 n. 1, links the 1709 façade of S. Stae to a legacy of Doge Alvise Mocenigo; the relation candidate remains for S6 review.",
        "relations": ["st-chp9-p269-n01-stae-facade-mocenigo-legacy"],
        "all_statements": ["st-chp9-p269-n01-stae-facade-mocenigo-legacy"],
        "note": "索引与第9章p.269注1均使用Doge Alvise Mocenigo；书内未给出在任序号。本卡保留源内指称，不作外部人物消歧。",
    },
    {
        "candidate": "cand-1689",
        "group": "new-person:de-michel-montaigne-49e9b48a8a",
        "ku": "units/persons/michel-de-montaigne",
        "card": "04-knowledge/units/persons/michel-de-montaigne.md",
        "name_zh": "米歇尔·德·蒙田",
        "name_en": "Michel de Montaigne",
        "index_entry": "M.csv#230",
        "index_label": "Montaigne, Michel de",
        "index_name": "Montaigne, Michel de",
        "index_pages": "370",
        "chapter": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "location": "第15章，印刷页370；OCR L67",
        "summary": "Haskell称Querini花园中“cabane de la folie”的门上刻有Montaigne的一句格言。",
        "quotes": [
            ("line 67; print p. 370", "Montaigne’s dictum"),
        ],
        "name_rows": [
            ("索引姓名", "Montaigne, Michel de", "S1"),
            ("正文称名", "Montaigne", "S2"),
            ("展示姓名", "Michel de Montaigne", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#230的Michel de Montaigne，以及第15章p.370所称的Montaigne。Haskell称Querini花园中“cabane de la folie”的门上刻有Montaigne的一句格言；本卡仅记录书内归属陈述，不表示独立核验其文本或作者身份。中文名采用通行工作音译。",
        "description_en": "This card records Michel de Montaigne, indexed at M.csv#230 and referred to as Montaigne on p. 370. Haskell says that a dictum of Montaigne was inscribed on the door of the “cabane de la folie” in Querini's garden. This records the book's attribution and does not independently verify the wording or authorship. The Chinese display name uses a conventional project transliteration.",
        "context_zh": "第15章p.370将Querini花园门上的格言归于Montaigne；作者归属关系候选留待S6审查。",
        "context_en": "Chapter 15, p. 370, attributes the dictum on the garden hut to Montaigne; the authorship relation candidate remains for S6 review.",
        "relations": ["st-chp15-p370-montaigne-dictum-text-authored-by-montaigne"],
        "all_statements": ["st-chp15-p370-montaigne-dictum-text-authored-by-montaigne"],
        "note": "索引列出Michel de Montaigne，第15章p.370以Montaigne称呼门上格言的作者；本卡保留书内归属，不声称独立核验。",
    },
    {
        "candidate": "cand-1692",
        "group": "new-person:da-federigo-montefeltre-7c480bf440",
        "ku": "units/persons/federigo-da-montefeltre",
        "card": "04-knowledge/units/persons/federigo-da-montefeltre.md",
        "name_zh": "费代里戈·达·蒙特费尔特罗",
        "name_en": "Federigo da Montefeltre",
        "index_entry": "M.csv#233",
        "index_label": "Montefeltre, Federigo da",
        "index_name": "Montefeltre, Federigo da",
        "index_pages": "54",
        "chapter": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "location": "第2章第IV节，印刷页54；OCR L123",
        "summary": "Haskell称Federigo da Montefeltre曾建造并改造乌尔比诺宫，将其作为文艺复兴文化的象征。",
        "quotes": [
            ("line 123; print p. 54", "Federigo da Montefeltre had built and turned into a symbol of Renaissance culture"),
        ],
        "name_rows": [
            ("索引姓名", "Montefeltre, Federigo da", "S1"),
            ("正文姓名", "Federigo da Montefeltre", "S2"),
            ("展示姓名", "Federigo da Montefeltre", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#233的Federigo da Montefeltre。第2章p.54称乌尔比诺宫由其建造并被改造为文艺复兴文化的象征；原书未在该段指明宫殿的正式名称。本卡只登记人物身份与书内称名，不将其与候选cand-4746的未定宫殿对象合并。中文名为项目工作音译。",
        "description_en": "This card records Federigo da Montefeltre, indexed at M.csv#233. Chapter 2, p. 54, says that he built the palace at Urbino and turned it into a symbol of Renaissance culture; the passage does not give the palace's formal name. This card records the person and the book's form of the name without merging him with the unidentified palace candidate cand-4746. The Chinese display name is a project working transliteration.",
        "context_zh": "第2章p.54将Federigo da Montefeltre与乌尔比诺宫的建造联系起来；该人物—建筑关系候选留待S6审查，宫殿对象仍按独立候选处理。",
        "context_en": "Chapter 2, p. 54, links Federigo da Montefeltre to the building of the Urbino palace; this person-to-building relation candidate remains for S6 review, and the palace stays a separate candidate.",
        "relations": ["st-chp2-seciv-l114-125-palace-built-by-federigo"],
        "all_statements": ["st-chp2-seciv-l114-125-palace-built-by-federigo"],
        "note": "索引与第2章p.54均给出Federigo da Montefeltre全名；与未命名宫殿候选cand-4746分开，关系留待S6。",
    },
    {
        "candidate": "cand-1697",
        "group": "new-person:claudio-monteverdi-306c7d79d5",
        "ku": "units/persons/claudio-monteverdi",
        "card": "04-knowledge/units/persons/claudio-monteverdi.md",
        "name_zh": "克劳迪奥·蒙特威尔第",
        "name_en": "Claudio Monteverdi",
        "index_entry": "M.csv#238",
        "index_label": "Monteverdi, Claudio",
        "index_name": "Monteverdi, Claudio",
        "index_pages": "96",
        "chapter": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
        "location": "第4章，印刷页96；OCR L20–21、L46注2",
        "summary": "Haskell称Paolo Giordano II结交了包括Monteverdi在内的音乐家；脚注2仅列Prunières (1926)，未在本项目中独立查阅该书。",
        "quotes": [
            ("line 21; print p. 96", "He befriended musicians of all kinds, including Monteverdi"),
            ("line 46; print p. 96 n. 2", "2 Prunieres, 1926."),
        ],
        "name_rows": [
            ("索引姓名", "Monteverdi, Claudio", "S1"),
            ("正文称名", "Monteverdi", "S2"),
            ("展示姓名", "Claudio Monteverdi", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#238的Claudio Monteverdi，以及第4章p.96所称的Monteverdi。Haskell称Paolo Giordano II结交了包括Monteverdi在内的音乐家，并在脚注2列Prunières (1926)作为参考；该书未在本项目中独立查阅，因此引用不构成额外核验。中文名采用通行音译。",
        "description_en": "This card records Claudio Monteverdi, indexed at M.csv#238 and referred to as Monteverdi on p. 96. Haskell says Paolo Giordano II befriended musicians including Monteverdi and cites Prunières (1926) in footnote 2. That cited book has not been independently consulted in this project, so the citation does not provide additional verification. The Chinese display name uses a conventional transliteration.",
        "context_zh": "第4章p.96称Paolo Giordano II结交包括Monteverdi在内的音乐家，相关关系候选留待S6；脚注2的Prunières (1926)仅作书目定位，非独立证据。",
        "context_en": "Chapter 4, p. 96, says Paolo Giordano II befriended musicians including Monteverdi; the relation candidate remains for S6. Footnote 2's Prunières (1926) is a bibliographic locator, not independently consulted evidence.",
        "relations": ["st-chp4-sec-i-l20-24-befriended-monteverdi"],
        "all_statements": [
            "st-chp4-sec-i-l20-24-befriended-monteverdi",
            "st-chp4-sec-i-l42-67-fn96-monteverdi-citation",
        ],
        "note": "索引列出Claudio Monteverdi，第4章p.96称Monteverdi；脚注2仅指向Prunières (1926)，作为书目定位而非关系或独立查证。",
    },
]


def csv_text(fieldnames: list[str], rows: list[dict]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def make_card(target: dict) -> str:
    sources = [
        common.book_source(
            f"书后索引 {target['index_entry']}；所列页码{target['index_pages']}",
            f"索引条目为‘{target['index_label']}’，页码指向{target['index_pages']}。",
            INDEX_PATH,
            target["index_entry"],
            [(target["index_entry"], target["index_label"])],
        ),
        common.book_source(
            target["location"],
            target["summary"],
            target["chapter"],
            "; ".join(span for span, _ in target["quotes"]),
            target["quotes"],
        ),
    ]
    frontmatter = {
        "title": f"{target['name_zh']}（{target['name_en']}）",
        "name_en": target["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    rows = "\n".join(
        f"| {field} | {value} | {evidence} |"
        for field, value, evidence in target["name_rows"]
    )
    relation_text = "；".join(target["relations"])
    statement_text = "；".join(target["all_statements"])
    body = f"""## 内容

### 描述

**中文：** {target['description_zh']}

**English:** {target['description_en']}

### 姓名与称号

| 字段 | 值 | 证据 |
|---|---|---|
{rows}

### 本书相关内容

**中文：** {target['context_zh']} 相关statement：{statement_text}。

**English:** {target['context_en']} Related statements: {statement_text}.

## 关系与证据

### 身份与外部链接

本卡身份依据限于原书索引与正文；本轮未登记外部身份链接。

### 关系记录

当前没有登记在relations.csv中的正式关系。直接S2关系候选 {relation_text} 留待S6审查；本次S4登记不创建正式边。
"""
    return f"---\n{fm}---\n\n{body}"


def build_outputs():
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidates_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidates)
    assert len({target["ku"] for target in TARGETS}) == len(TARGETS)
    assert len({target["card"] for target in TARGETS}) == len(TARGETS)

    manifest_ids = {row["ku_id"] for row in manifest}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_PATH).read_text(encoding="utf-8-sig")
    for target in TARGETS:
        candidate = target["candidate"]
        assert candidates_by_id[candidate]["suggested_type"] == "person"
        row = decisions[candidate]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row["resolution_note"]) == target["group"]
        assert target["ku"] not in manifest_ids
        assert not (ROOT / target["card"]).exists()
        assert f"- {target['card']}" not in accepted_text.splitlines()
        assert target["index_label"] in index_text
        assert len([item for item in alignments if item.get("candidate_id") == candidate]) == 1
        assert not any(
            item.get("candidate_id") == candidate and item.get("external_source")
            for item in alignments
        )
        assert len(common.primary_group_rows(alignments, target["group"])) == 1

    source_checks = {
        "02-sources/02-Markdown/09_CHP-9_sec_ii.md": ["legacy of Doge Alvise Mocenigo"],
        "02-sources/02-Markdown/15_CHP-15_sec_ii.md": ["Montaigne’s dictum"],
        "02-sources/02-Markdown/02_CHP-2_sec_iv.md": ["Federigo da Montefeltre had built"],
        "02-sources/02-Markdown/04_CHP-4_sec_i.md": [
            "He befriended musicians of all kinds, including Monteverdi",
            "2 Prunieres, 1926.",
        ],
    }
    for source_file, fragments in source_checks.items():
        content = (ROOT / source_file).read_text(encoding="utf-8-sig")
        assert all(fragment in content for fragment in fragments), source_file

    planned_alignments = [dict(row) for row in alignments]
    planned_decisions = {
        row["candidate_id"]: row
        for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    for target in TARGETS:
        row = planned_decisions[target["candidate"]]
        row["ku_id"] = target["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += (
            f" S4登记（{DATE}）：保留S3身份组{target['group']}，映射至{target['ku']}。"
        )

    planned_manifest = list(manifest)
    cards = {}
    for target in TARGETS:
        planned_manifest.append(
            {
                "ku_id": target["ku"],
                "type": "person",
                "canonical_name": target["name_zh"],
                "name_en": target["name_en"],
                "source_task": TASK,
                "card_path": target["card"],
            }
        )
        cards[target["card"]] = make_card(target)
    planned_manifest.sort(key=lambda row: row["ku_id"])
    accepted_new = accepted_text
    for target in TARGETS:
        accepted_new = common.insert_accepted(accepted_new, target["card"])

    statements = sync.load_statements()
    member_ids = {target["candidate"] for target in TARGETS}
    direct = [
        row for row in statements
        if any(row.get(field) in member_ids for field in ("subject_candidate_id", "object_candidate_id"))
    ]
    expected_direct = {
        statement_id
        for target in TARGETS
        for statement_id in target["all_statements"]
    }
    direct_relations = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    expected_relations = {
        statement_id
        for target in TARGETS
        for statement_id in target["relations"]
    }
    assert {row["statement_id"] for row in direct} == expected_direct
    assert {row["statement_id"] for row in direct_relations} == expected_relations

    stats = sync.summarize_by_type([dict(row) for row in candidates], planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == 607
    assert stats["person"]["registered_members"] == 700
    assert stats["person"]["pending_groups"] == 455
    assert stats["person"]["pending_members"] == 456
    assert totals["registered_groups"] == 1016 and totals["registered_members"] == 1194
    assert totals["pending_groups"] == 3754 and totals["pending_members"] == 3768
    assert len(planned_manifest) == len(manifest) + 4

    with tempfile.TemporaryDirectory(prefix="pnp-s4-montage-") as temp_dir:
        selected_manifest = []
        for target in TARGETS:
            temp_card = Path(temp_dir) / f"{target['ku'].split('/')[-1]}.md"
            temp_card.write_text(cards[target["card"]], encoding="utf-8")
            selected_manifest.append({"ku_id": target["ku"], "card_path": str(temp_card)})
        additions, source_registry, warnings, cards_with_tables = extract_records(selected_manifest)
    assert cards_with_tables == 4 and not warnings, warnings
    assert len(additions) == sum(len(target["name_rows"]) for target in TARGETS) == 12
    assert all(row["evidence_status"] == "source_backed" and row["source_ids"] for row in additions)

    current_enrichment = [
        json.loads(line)
        for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assign_ids(additions, ENRICHMENT_PATH)
    existing_ids = {row.get("enrichment_id") for row in current_enrichment}
    existing_keys = {
        (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id"))
        for row in current_enrichment
    }
    for row in additions:
        assert row["enrichment_id"] not in existing_ids
        key = (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id"))
        assert key not in existing_keys
        existing_ids.add(row["enrichment_id"])
        existing_keys.add(key)
    planned_enrichment = current_enrichment + additions
    current_sources = sync.read_csv(SOURCES_PATH)[1]
    current_source_ids = {row["source_id"] for row in current_sources}
    assert set(source_registry) <= current_source_ids
    assert len(current_sources) == 1724

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_lines = [
        f"- {target['candidate']}（原组{target['group']}）→ {target['group']} → "
        f"[{target['name_zh']}（{target['name_en']}）](../../../{target['card']})；{target['note']}"
        for target in TARGETS
    ]
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份组登记与S4人物端点：M索引候选（{DATE}）\n\n"
        + "\n".join(process_lines)
        + f"\n\n本批沿用4个既有S3 new人物组，登记4张KU卡、4条候选映射和{len(additions)}条source_backed名称字段；身份依据为书内索引与正文，未新增外部身份对齐行或sources.csv记录。5条直接S2 statement中4条relation_candidate继续待S6，Monteverdi的Prunières (1926)脚注仅为书目定位；未新增formal relation。"
        + f"\n\n登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    if not process_text.endswith("\n"):
        process_text += "\n"

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    external_total = sum(bool(row.get("external_source")) for row in planned_alignments)
    result_text, count = re.subn(
        r"^\| \[全书对齐\].*$",
        f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(len(planned_alignments))} 条：{sync.fmt(len(candidates))} 条候选决定记录及 {sync.fmt(external_total)} 条外部身份记录；候选决定数见下表 |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert count == 1
    unverified = sum(row.get("evidence_status") == "unverified" for row in current_enrichment)
    result_text, count = re.subn(
        r"^\| \[既有字段表\].*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_enrichment))}条，其中{sync.fmt(unverified)}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert count == 1
    batch_result = (
        f"### S4人物端点：M索引候选组（{DATE}）\n\n"
        + "；".join(
            f"{target['candidate']} → ../units/persons/{target['ku'].split('/')[-1]}.md（{target['group']}）"
            for target in TARGETS
        )
        + f"。4条直接关系候选继续待S6；Monteverdi脚注仅保留书目定位。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射已登记，{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记；KU={len(planned_manifest)}。"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, batch_result + "\n\n" + marker, 1)

    enrichment_text = "\n".join(json.dumps(row, ensure_ascii=False) for row in planned_enrichment) + "\n"
    outputs = {
        ALIGNMENT_PATH: csv_text(alignment_fields, planned_alignments),
        MANIFEST_PATH: csv_text(manifest_fields, planned_manifest),
        ACCEPTED_PATH: accepted_new,
        PROCESS_PATH: process_text,
        RESULT_PATH: result_text,
        ENRICHMENT_PATH: enrichment_text,
        **{ROOT / path: content for path, content in cards.items()},
    }
    return outputs, stats, totals, additions, direct_relations, planned_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Register four already-decided M-index person groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    outputs, stats, totals, additions, relations, planned_manifest = build_outputs()
    print(
        f"S4: groups={len(TARGETS)}; candidate_mappings={len(TARGETS)}; cards={len(TARGETS)}; "
        f"name_rows={len(additions)}; relation_candidates_pending={len(relations)}; formal_relations_added=0; "
        f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
        f"S4_total={totals['registered_groups']}/{totals['registered_members']} registered, "
        f"{totals['pending_groups']}/{totals['pending_members']} pending; KU={len(planned_manifest)}"
    )
    if args.dry_run:
        print("dry-run passed: S3 groups, source anchors, direct statements, enrichment keys; no files changed")
        return

    previous = {path: path.read_bytes() if path.exists() else None for path in outputs}
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            original = previous[path]
            encoding = "utf-8-sig" if original is not None and original.startswith(b"\xef\xbb\xbf") else "utf-8"
            temp = path.with_suffix(path.suffix + ".tmp-s4-montage")
            temp.write_text(content, encoding=encoding, newline="\n")
        for path in outputs:
            path.with_suffix(path.suffix + ".tmp-s4-montage").replace(path)
    except Exception:
        for path, original in previous.items():
            temp = path.with_suffix(path.suffix + ".tmp-s4-montage")
            temp.unlink(missing_ok=True)
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        raise
    print(f"applied: wrote {len(outputs)} artifacts; enrichment_rows={len(additions)}; source_registry_rows_added=0")


if __name__ == "__main__":
    main()
