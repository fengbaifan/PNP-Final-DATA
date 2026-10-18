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
INDEX_PATH = "02-sources/03-Index/03-2-Index-CSV/S.csv"
ANCHOR = "s3-s4-person-s-index-endpoints-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

TARGETS = [
    {
        "candidate": "cand-2347",
        "group": "new-person:nicola-salvi-4ff08e1bab",
        "ku": "units/persons/nicola-salvi",
        "card": "04-knowledge/units/persons/nicola-salvi.md",
        "name_zh": "尼古拉·萨尔维",
        "name_en": "Nicola Salvi",
        "index_entry": "S.csv#35",
        "index_label": "Salvi, Nicola",
        "index_pages": "223",
        "chapters": [
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "location": "第8章，印刷页223；OCR L144–145",
                "summary": "Haskell称Nicola Salvi为Ruffo在S. Lorenzo in Damaso的富丽礼拜堂的建造者；该空间为教堂内部礼拜堂。",
                "quotes": [
                    ("lines 144–145; print p. 223", "The rich chapel which Nicola Salvi built for him in S. Lorenzo in Damaso"),
                ],
            }
        ],
        "name_rows": [
            ("索引姓名", "Salvi, Nicola", "S1"),
            ("正文姓名", "Nicola Salvi", "S2"),
            ("展示姓名", "Nicola Salvi", "S1"),
        ],
        "description_zh": "本卡记录索引S.csv#35的Nicola Salvi。第8章p.223称他为Ruffo在S. Lorenzo in Damaso所建富丽礼拜堂的建造者。S2将该礼拜堂作为教堂内部空间单独记录；本卡不把礼拜堂与所在教堂合并。该建造陈述仍待S6审查，未作独立核验。中文名为项目工作音译。",
        "description_en": "This card records Nicola Salvi, indexed at S.csv#35. Chapter 8, p. 223, names him as the builder of the rich chapel for Ruffo at S. Lorenzo in Damaso. S2 records the chapel as an interior space distinct from its host church; this card does not merge those objects. The building statement remains for S6 review and has not been independently verified. The Chinese display name is a project working transliteration.",
        "context_zh": "第8章p.223称Nicola Salvi为Ruffo礼拜堂的建造者；人物与礼拜堂的关系候选st-chp8-p223-salvi-built-chapel留待S6。",
        "context_en": "Chapter 8, p. 223, names Nicola Salvi as the builder of Ruffo's chapel; the person-to-chapel candidate st-chp8-p223-salvi-built-chapel remains for S6.",
        "relations": ["st-chp8-p223-salvi-built-chapel"],
        "statements": ["st-chp8-p223-salvi-built-chapel"],
        "note": "S.csv#35与第8章p.223均给出Nicola Salvi全名；礼拜堂作为教堂内部空间保持独立，建造关系待S6。",
    },
    {
        "candidate": "cand-2357",
        "group": "new-person:de-santi-tommaso-ed5fd73fba",
        "ku": "units/persons/tommaso-de-santi",
        "card": "04-knowledge/units/persons/tommaso-de-santi.md",
        "name_zh": "托马索·德·桑蒂",
        "name_en": "Tommaso de Santi",
        "index_entry": "S.csv#45",
        "index_label": "Santi, Tommaso de'",
        "index_pages": "263",
        "chapters": [
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "location": "第9章，印刷页263–264；OCR L236、L245–246",
                "summary": "Haskell称Zaccaria Sagredo将收藏交由仆人Tommaso de’ Santi照料，并在书中引述遗嘱条款；正文写作Gherardo，遗嘱引文写作Girardo，原始遗嘱未独立查阅。",
                "quotes": [
                    ("line 236; print p. 263", "his favourite servant Tommaso de’ Santi"),
                    ("lines 245–246; print p. 264", "ellego Tomaso de Santi mio cameriere"),
                    ("line 246; print p. 264", "Nobil Homo M. Girardo P.O Sagredio mio Amatissimo Nipote"),
                ],
            }
        ],
        "name_rows": [
            ("索引姓名", "Santi, Tommaso de'", "S1"),
            ("正文称名", "Tommaso de’ Santi", "S2"),
            ("遗嘱引文拼写", "Tomaso de Santi", "S2"),
            ("展示姓名", "Tommaso de Santi", "S1"),
        ],
        "description_zh": "本卡记录索引S.csv#45的Tommaso de’ Santi。第9章p.263称他为Zaccaria Sagredo的仆人并受托照料收藏；p.264引述的遗嘱写作“Tomaso de Santi”。这段遗嘱文字由Haskell转引，原始公证文书未在本项目中独立查阅。正文称遗产受益侄子为Gherardo，遗嘱引文则拼作Girardo；两种形式的身份对应仍待S3处理，本卡不替其合并。中文名为项目工作音译。",
        "description_en": "This card records Tommaso de’ Santi, indexed at S.csv#45. Chapter 9, p. 263, identifies him as Zaccaria Sagredo's servant and says he was entrusted with the collection; the quoted will on p. 264 spells his name “Tomaso de Santi.” Haskell reproduces the will passage, and the notarial original has not been independently consulted in this project. The narrative names the nephew Gherardo, while the quoted will spells the name Girardo; their identity correspondence remains for S3 review and is not merged here. The Chinese display name is a project working transliteration.",
        "context_zh": "第9章p.263–264记述Sagredo遗嘱安排及Tommaso的保管职责。摘要与遗嘱引文对应的两条关系候选均留待S6；Gherardo／Girardo身份差异仍待S3核对。",
        "context_en": "Chapter 9, pp. 263–264, describes Sagredo's will arrangements and Tommaso's custodial role. Both the summary and quoted-will relation candidates remain for S6; the Gherardo/Girardo identity difference remains for S3 review.",
        "relations": [
            "st-chp9-p263264-will-arrangements-summary",
            "st-chp9-p263264-will-quoted-provisions",
        ],
        "statements": [
            "st-chp9-p263264-will-arrangements-summary",
            "st-chp9-p263264-will-quoted-provisions",
        ],
        "note": "索引与正文称名为Tommaso de’ Santi，遗嘱引文拼作Tomaso；原始遗嘱未独立查阅。Gherardo／Girardo身份对应仍待S3，不通过登记Tommaso KU替代该裁决。",
    },
    {
        "candidate": "cand-2358",
        "group": "new-person:carlo-saraceni-d6fa6d7fe0",
        "ku": "units/persons/carlo-saraceni",
        "card": "04-knowledge/units/persons/carlo-saraceni.md",
        "name_zh": "卡洛·萨拉切尼",
        "name_en": "Carlo Saraceni",
        "index_entry": "S.csv#46",
        "index_label": "Saraceni, Carlo",
        "index_pages": "206",
        "chapters": [
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "location": "第8章第I节，印刷页205–206；OCR L28、L31",
                "summary": "Haskell称Gaspar Roomer拥有三幅Carlo Saraceni的绘画；姓氏在p.205–206换页处续接，索引S.csv#46列出全名。",
                "quotes": [
                    ("line 28; print p. 205", "three paintings each by Caracciolo, the young Massimo Stanzione and Carlo"),
                    ("line 31; print p. 206", "Saraceni"),
                ],
            }
        ],
        "name_rows": [
            ("索引姓名", "Saraceni, Carlo", "S1"),
            ("正文姓名（跨页续接）", "Carlo Saraceni", "S2"),
            ("展示姓名", "Carlo Saraceni", "S1"),
        ],
        "description_zh": "本卡记录索引S.csv#46的Carlo Saraceni。第8章p.205句末出现“Carlo”，p.206续行为“Saraceni”；两条S2记录标记同一句跨页续接，索引也列出完整姓名。Haskell称Gaspar Roomer拥有三幅其作品，本卡不据此补写具体作品题名或独立核验归属。中文名采用通行工作音译。",
        "description_en": "This card records Carlo Saraceni, indexed at S.csv#46. Chapter 8 ends the p. 205 sentence with “Carlo” and continues it as “Saraceni” on p. 206; the two S2 records mark one sentence across a page break, and the index gives the full name. Haskell says Gaspar Roomer owned three of his paintings. This card adds no individual work titles and does not independently verify the attribution. The Chinese display name uses a conventional project transliteration.",
        "context_zh": "第8章p.205–206称Roomer拥有三幅Carlo Saraceni绘画；跨页的open／continuation两条关系候选指向同一陈述，均保留待S6。",
        "context_en": "Chapter 8, pp. 205–206, says Roomer owned three paintings by Carlo Saraceni; the open/continuation relation records refer to the same statement and remain for S6.",
        "relations": [
            "st-chp8-p205-roomer-owned-three-saraceni-paintings-open",
            "st-chp8-p206-saraceni-closes-three-paintings-continuation",
        ],
        "statements": [
            "st-chp8-p205-roomer-owned-three-saraceni-paintings-open",
            "st-chp8-p206-saraceni-closes-three-paintings-continuation",
        ],
        "note": "索引S.csv#46确认完整姓名；p.205句末与p.206续行构成同一条Roomer藏画陈述，保留两条S2记录但不当作两项作品事实。",
    },
    {
        "candidate": "cand-2360",
        "group": "new-person:giuseppe-sardi-d9fb8f5ac8",
        "ku": "units/persons/giuseppe-sardi",
        "card": "04-knowledge/units/persons/giuseppe-sardi.md",
        "name_zh": "朱塞佩·萨尔迪",
        "name_en": "Giuseppe Sardi",
        "index_entry": "S.csv#48",
        "index_label": "Sardi, Giuseppe",
        "index_pages": "248, 269",
        "chapters": [
            {
                "file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "location": "第9章，印刷页248；OCR L42–45",
                "summary": "Haskell称S. Maria del Giglio立面由Antonio Barbaro设计、由Giuseppe Sardi于1675至1683年间建造。",
                "quotes": [
                    ("lines 42–45; print p. 248", "erected by Giuseppe Sardi between 1675 and 1683"),
                ],
            },
            {
                "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                "location": "第9章，印刷页269；OCR L21–22",
                "summary": "Haskell称Longhena与Sardi受聘建造Scalzi的新教堂；本句没有进一步拆分二人的具体职责。",
                "quotes": [
                    ("lines 21–22; print p. 269", "Longhena and Sardi were employed to build a new one"),
                ],
            },
        ],
        "name_rows": [
            ("索引姓名", "Sardi, Giuseppe", "S1"),
            ("正文全名", "Giuseppe Sardi", "S2"),
            ("正文简称", "Sardi", "S2"),
            ("展示姓名", "Giuseppe Sardi", "S1"),
        ],
        "description_zh": "本卡记录索引S.csv#48的Giuseppe Sardi。第9章p.248称S. Maria del Giglio立面由Antonio Barbaro设计、由Sardi于1675至1683年间建造；p.269另称Longhena与Sardi受聘建造Scalzi新教堂，但没有拆分二人的职责。本卡不把建造角色改写为设计，也不推定具体共同分工。两条直接关系候选均留待S6。中文名为项目工作音译。",
        "description_en": "This card records Giuseppe Sardi, indexed at S.csv#48. Chapter 9, p. 248, distinguishes Antonio Barbaro as the designer of the S. Maria del Giglio façade and Sardi as its builder between 1675 and 1683. On p. 269, Haskell also says Longhena and Sardi were employed to build the new Scalzi church, without dividing their roles. This card does not recast the builder as designer or infer a more specific division of work. Both direct relation candidates remain for S6. The Chinese display name is a project working transliteration.",
        "context_zh": "第9章p.248的立面建造陈述与p.269的Scalzi教堂受聘陈述各保留为独立关系候选，均待S6；设计者、建造者及共同受聘语境不混写。",
        "context_en": "The p. 248 façade-building statement and p. 269 Scalzi church employment statement remain separate relation candidates for S6; designer, builder, and joint employment roles are kept distinct.",
        "relations": [
            "st-chp9-p248-facade-erected-by-sardi",
            "st-chp9-p269-scalzi-original-church-too-small",
        ],
        "statements": [
            "st-chp9-p248-facade-erected-by-sardi",
            "st-chp9-p269-scalzi-original-church-too-small",
        ],
        "note": "索引列p.248、269；p.248明确区分Antonio Barbaro为设计者、Sardi为建造者，p.269只称Longhena与Sardi受聘建造新教堂，不推定具体分工。",
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
        )
    ]
    for chapter in target["chapters"]:
        sources.append(
            common.book_source(
                chapter["location"],
                chapter["summary"],
                chapter["file"],
                "; ".join(span for span, _ in chapter["quotes"]),
                chapter["quotes"],
            )
        )
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
    statement_text = "；".join(target["statements"])
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
        "02-sources/02-Markdown/08_CHP-8_sec_ii.md": [
            "The rich chapel which Nicola Salvi built",
        ],
        "02-sources/02-Markdown/09_CHP-9_intro.md": [
            "his favourite servant Tommaso de’ Santi",
            "ellego Tomaso de Santi mio cameriere",
            "mio Amatissimo Nipote",
            "erected by Giuseppe Sardi between 1675 and 1683",
        ],
        "02-sources/02-Markdown/08_CHP-8_sec_i.md": [
            "three paintings each by Caracciolo",
            "and Carlo",
            "Saraceni;",
        ],
        "02-sources/02-Markdown/09_CHP-9_sec_ii.md": [
            "Longhena and\nSardi were employed to build a new one",
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
    direct = []
    for row in statements:
        qualifiers = row.get("qualifiers") or {}
        if (
            row.get("subject_candidate_id") in member_ids
            or row.get("object_candidate_id") in member_ids
            or member_ids.intersection(qualifiers.get("mentioned_candidate_ids") or [])
        ):
            direct.append(row)
    expected_direct = {
        statement_id
        for target in TARGETS
        for statement_id in target["statements"]
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
    assert len(direct_relations) == 7

    stats = sync.summarize_by_type([dict(row) for row in candidates], planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == 611
    assert stats["person"]["registered_members"] == 704
    assert stats["person"]["pending_groups"] == 451
    assert stats["person"]["pending_members"] == 452
    assert totals["registered_groups"] == 1020 and totals["registered_members"] == 1198
    assert totals["pending_groups"] == 3750 and totals["pending_members"] == 3764
    assert len(planned_manifest) == len(manifest) + 4

    with tempfile.TemporaryDirectory(prefix="pnp-s4-s-index-") as temp_dir:
        selected_manifest = []
        for target in TARGETS:
            temp_card = Path(temp_dir) / f"{target['ku'].split('/')[-1]}.md"
            temp_card.write_text(cards[target["card"]], encoding="utf-8")
            selected_manifest.append({"ku_id": target["ku"], "card_path": str(temp_card)})
        additions, source_registry, warnings, cards_with_tables = extract_records(selected_manifest)
    assert cards_with_tables == 4 and not warnings, warnings
    assert len(additions) == sum(len(target["name_rows"]) for target in TARGETS) == 14
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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份组登记与S4人物端点：S索引候选（{DATE}）\n\n"
        + "\n".join(process_lines)
        + f"\n\n本批沿用4个既有S3 new人物组，登记4张KU卡、4条候选映射和{len(additions)}条source_backed名称字段；身份依据为书内索引与正文，未新增外部身份对齐行或sources.csv记录。7条relation_candidate记录继续待S6，其中Saraceni跨页续句、Tommaso遗嘱摘要与引文保留来源层差异；Gherardo／Girardo身份对应仍待S3，不合并。未新增formal relation。"
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
        f"### S4人物端点：S索引候选组（{DATE}）\n\n"
        + "；".join(
            f"{target['candidate']} → ../units/persons/{target['ku'].split('/')[-1]}.md（{target['group']}）"
            for target in TARGETS
        )
        + f"。7条relation_candidate记录继续待S6；Gherardo／Girardo身份对应未并入Tommaso裁决。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射已登记，{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记；KU={len(planned_manifest)}。"
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
    parser = argparse.ArgumentParser(description="Register four already-decided S-index person groups.")
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
        print("dry-run passed: S3 groups, source anchors, mentioned and endpoint statements, enrichment keys; no files changed")
        return

    previous = {path: path.read_bytes() if path.exists() else None for path in outputs}
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            original = previous[path]
            encoding = "utf-8-sig" if original is not None and original.startswith(b"\xef\xbb\xbf") else "utf-8"
            temp = path.with_suffix(path.suffix + ".tmp-s4-s-index")
            temp.write_text(content, encoding=encoding, newline="\n")
        for path in outputs:
            path.with_suffix(path.suffix + ".tmp-s4-s-index").replace(path)
    except Exception:
        for path, original in previous.items():
            temp = path.with_suffix(path.suffix + ".tmp-s4-s-index")
            temp.unlink(missing_ok=True)
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        raise
    print(f"applied: wrote {len(outputs)} artifacts; enrichment_rows={len(additions)}; source_registry_rows_added=0")


if __name__ == "__main__":
    main()
