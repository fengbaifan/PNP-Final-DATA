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
ANCHOR = "s3-s4-person-medici-endpoints-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
INDEX_PATH = "02-sources/03-Index/03-2-Index-CSV/M.csv"

TARGETS = [
    {
        "candidate": "cand-1606",
        "group": "new-person:anna-de-ludovica-maria-medici-4e4e0c1fff",
        "ku": "units/persons/anna-maria-ludovica-de-medici",
        "card": "04-knowledge/units/persons/anna-maria-ludovica-de-medici.md",
        "name_zh": "安娜·玛丽亚·卢多维卡·德·美第奇",
        "name_en": "Anna Maria Ludovica de' Medici",
        "index_entry": "M.csv#146",
        "index_label": "Medici, Anna Maria Ludovica de' (wife of Johann Wilhelm, Elector Palatinate)",
        "index_name": "Medici, Anna Maria Ludovica de'",
        "index_pages": "282",
        "chapter": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章，印刷页282；OCR L143",
        "summary": "Haskell称Johann Wilhelm与Anna Maria Ludovica的婚姻可能推动其收藏与赞助；将她称为美第奇家族最后一人。",
        "quotes": [
            ("line 143; print p. 282", "Johann Wilhelm’s marriage to Anna Maria Ludovica, the last of the Medici"),
        ],
        "name_rows": [
            ("索引姓名", "Medici, Anna Maria Ludovica de'", "S1"),
            ("正文称名", "Anna Maria Ludovica", "S2"),
            ("展示姓名", "Anna Maria Ludovica de' Medici", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#146的Anna Maria Ludovica de' Medici，以及第10章p.282称为“Anna Maria Ludovica”的人物。Haskell称她为美第奇家族最后一人，并认为她与Johann Wilhelm的婚姻可能推动了他的收藏与赞助；这项因果判断保留为原书观点，不扩展为独立验证的生平事实。中文名依本书称名作工作音译。",
        "description_en": "This card records the person indexed as Anna Maria Ludovica de' Medici at M.csv#146 and called “Anna Maria Ludovica” on p. 282. Haskell describes her as the last of the Medici and suggests that her marriage to Johann Wilhelm may have encouraged his collecting and patronage. That causal interpretation remains Haskell's account, not an independently verified biographical fact. The Chinese name is a working transliteration of the book form.",
        "context_zh": "第10章p.282将Johann Wilhelm的婚姻与其收藏、赞助联系起来。该关系候选st-chp10-p282-marriage-patronage留待S6审查。",
        "context_en": "Chapter 10, p. 282, connects Johann Wilhelm's marriage with his collecting and patronage. The relation candidate st-chp10-p282-marriage-patronage remains for S6 review.",
        "relations": ["st-chp10-p282-marriage-patronage"],
        "note": "索引与第10章p.282均使用Anna Maria Ludovica形式；无匹配的既有person KU。保留现有new身份组，不将未见于本书的姓名异体补入。",
    },
    {
        "candidate": "cand-1626",
        "group": "new-person:de-francesco-maria-medici-d2f7719ab0",
        "ku": "units/persons/francesco-maria-de-medici",
        "card": "04-knowledge/units/persons/francesco-maria-de-medici.md",
        "name_zh": "弗朗切斯科·玛丽亚·德·美第奇",
        "name_en": "Francesco Maria de' Medici",
        "index_entry": "M.csv#166",
        "index_label": "Medici, Francesco Maria de'",
        "index_name": "Medici, Francesco Maria de'",
        "index_pages": "229",
        "chapter": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章，印刷页229；OCR L220",
        "summary": "Haskell称Ferdinand与叔父Francesco Maria共同反对Cosimo III。",
        "quotes": [
            ("line 220; print p. 229", "With his uncle Francesco Maria, only three years older than himself, he led the opposition"),
        ],
        "name_rows": [
            ("索引姓名", "Medici, Francesco Maria de'", "S1"),
            ("正文称名", "Francesco Maria", "S2"),
            ("展示姓名", "Francesco Maria de' Medici", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#166的Francesco Maria de' Medici，以及第8章p.229称为“Francesco Maria”的人物。Haskell将其称为Ferdinand的叔父，并称二人共同反对Cosimo III；该关系表述保留为本书陈述，候选边留待S6审查。中文名为项目工作音译。",
        "description_en": "This card records the person indexed as Francesco Maria de' Medici at M.csv#166 and called “Francesco Maria” on p. 229. Haskell identifies him as Ferdinand's uncle and says that the two led opposition to Cosimo III; this remains the book's account, with the candidate edge pending S6 review. The Chinese name is a project working transliteration.",
        "context_zh": "第8章p.229称Francesco Maria与Ferdinand共同反对Cosimo III。相关关系候选st-chp8-p229-ferdinand-francesco-opposition留待S6审查。",
        "context_en": "Chapter 8, p. 229, says Francesco Maria and Ferdinand jointly opposed Cosimo III. The relation candidate st-chp8-p229-ferdinand-francesco-opposition remains for S6 review.",
        "relations": ["st-chp8-p229-ferdinand-francesco-opposition"],
        "note": "索引提供Medici姓氏，第8章p.229提供正文称名及叔侄语境；无匹配的既有person KU。该关系候选不在S4写为正式边。",
    },
    {
        "candidate": "cand-1627",
        "group": "new-person:de-gastone-gian-medici-6164ea1b9e",
        "ku": "units/persons/gian-gastone-de-medici",
        "card": "04-knowledge/units/persons/gian-gastone-de-medici.md",
        "name_zh": "吉安·加斯托内·德·美第奇",
        "name_en": "Gian Gastone de' Medici",
        "index_entry": "M.csv#167",
        "index_label": "Medici, Grand Duke Gian Gastone de'",
        "index_name": "Medici, Gian Gastone de'",
        "index_pages": "229",
        "chapter": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章，印刷页229；OCR L218",
        "summary": "Haskell称Gian Gastone为美第奇家族最后一位亲王，并在同段将Ferdinand与Gian Gastone称为Cosimo III和Marguerite d'Orléans的两个儿子。",
        "quotes": [
            ("line 218; print p. 229", "the two sons of the marriage: Ferdinand, who died at 50 before ruling, and Gian Gastone, the last of the Medici princes"),
        ],
        "name_rows": [
            ("索引姓名", "Medici, Gian Gastone de'", "S1"),
            ("正文称名", "Gian Gastone", "S2"),
            ("展示姓名", "Gian Gastone de' Medici", "S1"),
            ("索引头衔", "Grand Duke", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#167的Gian Gastone de' Medici，以及第8章p.229称为“Gian Gastone”的人物。Haskell称他为美第奇家族最后一位亲王，并将其与Ferdinand并列为Cosimo III与Marguerite d'Orléans的两个儿子。原文的出生年份语句指向前文的Ferdinand，本卡不将该日期转记给Gian Gastone。相关关系候选留待S6审查。",
        "description_en": "This card records the person indexed as Gian Gastone de' Medici at M.csv#167 and called “Gian Gastone” on p. 229. Haskell calls him the last Medici prince and names him alongside Ferdinand as one of the two sons of Cosimo III and Marguerite d'Orléans. The birth-year sentence in the passage refers to the preceding discussion of Ferdinand; this card does not transfer that date to Gian Gastone. The related candidate edges remain for S6 review.",
        "context_zh": "第8章p.229关于“美第奇家族最后一位亲王”及与Ferdinand的兄弟关系分别保留为S2关系候选，留待S6；没有新增正式边。",
        "context_en": "The p. 229 statements identifying him as the last Medici prince and as Ferdinand's brother remain separate S2 relation candidates for S6; no formal edge is added.",
        "relations": [
            "st-chp8-p229-gian-gastone-last-medici-prince",
            "st-chp8-p229-ferdinand-gian-gastone-siblings",
        ],
        "note": "索引列Grand Duke Gian Gastone de'，第8章p.229有两处正文提及。保留与Ferdinand相区分的候选映射；不把相邻句中关于Ferdinand的1663年出生日期转移给Gian Gastone。",
    },
    {
        "candidate": "cand-1628",
        "group": "new-person:de-isabella-medici-6acace310c",
        "ku": "units/persons/isabella-de-medici",
        "card": "04-knowledge/units/persons/isabella-de-medici.md",
        "name_zh": "伊莎贝拉·德·美第奇",
        "name_en": "Isabella de' Medici",
        "index_entry": "M.csv#168",
        "index_label": "Medici, Isabella de' (Duchess of Bracciano)",
        "index_name": "Medici, Isabella de'",
        "index_pages": "98n",
        "chapter": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
        "location": "第4章，印刷页98，注3；OCR L66",
        "summary": "Haskell脚注称Paolo Giordano I曾令其妻Isabella de' Medici被勒死；该事件陈述保留为原书归述。",
        "quotes": [
            ("line 66; print p. 98 n. 3", "His grandfather Paolo Giordano I had had his wife Isabella de’ Medici strangled"),
        ],
        "name_rows": [
            ("索引姓名", "Medici, Isabella de'", "S1"),
            ("正文称名", "Isabella de’ Medici", "S2"),
            ("展示姓名", "Isabella de' Medici", "S1"),
            ("索引头衔", "Duchess of Bracciano", "S1"),
        ],
        "description_zh": "本卡记录索引M.csv#168的Isabella de' Medici（Duchess of Bracciano）以及第4章p.98注3称为“Isabella de’ Medici”的人物。该脚注将她指为Paolo Giordano I的妻子，并归述其被勒死的事件；这是Haskell的来源陈述，不代表独立核验。她与另一候选cand-5550所指身份未明的Paolo Giordano II之妻Isabella保持区分。",
        "description_en": "This card records the Isabella de' Medici indexed at M.csv#168 with the title Duchess of Bracciano and called “Isabella de’ Medici” in ch. 4, p. 98 n. 3. The footnote identifies her as Paolo Giordano I's wife and reports that she was strangled; this is Haskell's account, not an independent verification. She remains distinct from cand-5550, the unresolved Isabella identified as Paolo Giordano II's wife.",
        "context_zh": "第4章p.98注3的事件陈述st-chp4-sec-i-l42-67-fn98-strangling-event留待S6审查；不把原书归述登记为已核实的正式关系。",
        "context_en": "The event statement in ch. 4, p. 98 n. 3, st-chp4-sec-i-l42-67-fn98-strangling-event remains for S6 review; Haskell's report is not entered as a verified formal relation.",
        "relations": ["st-chp4-sec-i-l42-67-fn98-strangling-event"],
        "note": "索引姓名及Bracciano头衔与第4章p.98注3的Isabella de' Medici相合。保持与cand-5550（Paolo Giordano II之身份未明妻子）分开；不以同名推定同一人物。",
    },
]


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
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in target["name_rows"])
    relations = "；".join(target["relations"])
    body = f"""## 内容

### 描述

**中文：** {target['description_zh']}

**English:** {target['description_en']}

### 姓名与称号

| 字段 | 值 | 证据 |
|---|---|---|
{rows}

### 本书相关内容

**中文：** {target['context_zh']} 相关statement：{relations}。

**English:** {target['context_en']} Related statements: {relations}.

## 关系与证据

### 身份与外部链接

本卡身份依据限于原书索引与正文；本轮未登记外部身份链接。

### 关系记录

当前没有登记在relations.csv中的正式关系。直接S2关系候选 {relations} 留待S6审查；本次S4登记不创建正式边。
"""
    return f"---\n{fm}---\n\n{body}"


def csv_text(fieldnames: list[str], rows: list[dict]) -> str:
    stream = tempfile.SpooledTemporaryFile(mode="w+", encoding="utf-8", newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    stream.seek(0)
    return stream.read()


def build_outputs():
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidates_by_id = {r["candidate_id"]: r for r in candidates}
    decisions = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert len(decisions) == len(candidates)
    assert len({t["ku"] for t in TARGETS}) == len(TARGETS)
    assert len({t["card"] for t in TARGETS}) == len(TARGETS)

    manifest_ids = {r["ku_id"] for r in manifest}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    for target in TARGETS:
        candidate = target["candidate"]
        assert candidates_by_id[candidate]["suggested_type"] == "person"
        row = decisions[candidate]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row["resolution_note"]) == target["group"]
        assert target["ku"] not in manifest_ids
        assert not (ROOT / target["card"]).exists()
        assert f"- {target['card']}" not in accepted_text.splitlines()
        assert len([r for r in alignments if r.get("candidate_id") == candidate]) == 1
        assert not any(r.get("candidate_id") == candidate and r.get("external_source") for r in alignments)
        assert len(common.primary_group_rows(alignments, target["group"])) == 1
    unresolved_isabella = decisions["cand-5550"]
    assert unresolved_isabella["decision"] == "undecided" and not unresolved_isabella.get("ku_id")

    index_text = (ROOT / INDEX_PATH).read_text(encoding="utf-8-sig")
    for target in TARGETS:
        assert target["index_label"] in index_text
    source_checks = {
        "02-sources/02-Markdown/10_CHP-10_intro.md": ["marriage to Anna Maria Ludovica, the last of the Medici"],
        "02-sources/02-Markdown/08_CHP-8_sec_ii.md": ["uncle Francesco Maria", "Gian Gastone, the last of the Medici princes"],
        "02-sources/02-Markdown/04_CHP-4_sec_i.md": ["wife Isabella de’ Medici strangled"],
    }
    for source_file, fragments in source_checks.items():
        content = (ROOT / source_file).read_text(encoding="utf-8-sig")
        assert all(fragment in content for fragment in fragments), source_file

    planned_alignments = [dict(r) for r in alignments]
    planned_decisions = {r["candidate_id"]: r for r in planned_alignments if r.get("candidate_id") and not r.get("external_source")}
    for target in TARGETS:
        row = planned_decisions[target["candidate"]]
        row["ku_id"] = target["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] += f" S4登记（{DATE}）：保留S3身份组{target['group']}，映射至{target['ku']}。"

    planned_manifest = list(manifest)
    accepted_new = accepted_text
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
        accepted_new = common.insert_accepted(accepted_new, target["card"])
        cards[target["card"]] = make_card(target)
    planned_manifest.sort(key=lambda r: r["ku_id"])

    statements = sync.load_statements()
    member_ids = {t["candidate"] for t in TARGETS}
    direct = [
        r for r in statements
        if any(r.get(field) in member_ids for field in ("subject_candidate_id", "object_candidate_id"))
    ]
    direct_relation = [r for r in direct if (r.get("qualifiers") or {}).get("relation_candidate") is True]
    expected_direct = {
        "st-chp10-p282-marriage-patronage",
        "st-chp4-sec-i-l42-67-fn98-strangling-event",
        "st-chp8-p229-brothers-personalities",
        "st-chp8-p229-ferdinand-francesco-opposition",
        "st-chp8-p229-gian-gastone-last-medici-prince",
        "st-chp8-p229-ferdinand-gian-gastone-siblings",
        "st-chp8-p229-gian-gastone-instability-debauchery",
        "st-chp8-p229-francesco-opposition-behavior",
    }
    expected_relations = {
        "st-chp10-p282-marriage-patronage",
        "st-chp4-sec-i-l42-67-fn98-strangling-event",
        "st-chp8-p229-ferdinand-francesco-opposition",
        "st-chp8-p229-gian-gastone-last-medici-prince",
        "st-chp8-p229-ferdinand-gian-gastone-siblings",
    }
    assert {r["statement_id"] for r in direct} == expected_direct
    assert {r["statement_id"] for r in direct_relation} == expected_relations

    stats = sync.summarize_by_type([dict(r) for r in candidates], planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == 603, stats["person"]
    assert stats["person"]["registered_members"] == 696
    assert stats["person"]["pending_groups"] == 459
    assert stats["person"]["pending_members"] == 460
    assert totals["registered_groups"] == 1012 and totals["registered_members"] == 1190
    assert totals["pending_groups"] == 3758 and totals["pending_members"] == 3772
    assert len(planned_manifest) == len(manifest) + 4

    with tempfile.TemporaryDirectory(prefix="pnp-s4-medici-") as temp_dir:
        selected_manifest = []
        for target in TARGETS:
            temp_card = Path(temp_dir) / f"{target['ku'].split('/')[-1]}.md"
            temp_card.write_text(cards[target["card"]], encoding="utf-8")
            selected_manifest.append({"ku_id": target["ku"], "card_path": str(temp_card)})
        additions, source_registry, warnings, cards_with_tables = extract_records(selected_manifest)
    assert cards_with_tables == 4 and not warnings, warnings
    expected_name_rows = sum(len(t["name_rows"]) for t in TARGETS)
    assert len(additions) == expected_name_rows == 14
    assert all(r["evidence_status"] == "source_backed" and r["source_ids"] for r in additions)

    current_enrichment = [
        json.loads(line)
        for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assign_ids(additions, ENRICHMENT_PATH)
    existing_ids = {r.get("enrichment_id") for r in current_enrichment}
    existing_keys = {
        (r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id"))
        for r in current_enrichment
    }
    for row in additions:
        assert row["enrichment_id"] not in existing_ids
        key = (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id"))
        assert key not in existing_keys
        existing_ids.add(row["enrichment_id"])
        existing_keys.add(key)
    planned_enrichment = current_enrichment + additions

    current_source_rows = sync.read_csv(SOURCES_PATH)[1]
    current_source_ids = {r["source_id"] for r in current_source_rows}
    assert set(source_registry) <= current_source_ids
    assert len(current_source_rows) == 1724

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_lines = []
    for target in TARGETS:
        process_lines.append(
            f"- {target['candidate']}（原组{target['group']}）→ {target['group']} → "
            f"[{target['name_zh']}（{target['name_en']}）](../../../{target['card']})；{target['note']}"
        )
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份组登记与S4人物端点：Medici索引候选（{DATE}）\n\n"
        + "\n".join(process_lines)
        + f"\n\n本批沿用4个既有S3 new人物组，登记4张KU卡、4条候选映射和{len(additions)}条source_backed名称／头衔字段；身份依据为既有书内索引与正文来源，未新增外部身份对齐行或sources.csv记录。8条直接S2 statement中5条relation_candidate继续待S6，3条非关系叙述不转为关系；未新增formal relation。cand-1628与仍为undecided的cand-5550保持区分。"
        + f"\n\n登记后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    if not process_text.endswith("\n"):
        process_text += "\n"

    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    alignment_total = len(planned_alignments)
    external_total = sum(bool(r.get("external_source")) for r in planned_alignments)
    result_text, n = re.subn(
        r"^\| \[全书对齐\].*$",
        f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(alignment_total)} 条：{sync.fmt(len(candidates))} 条候选决定记录及 {sync.fmt(external_total)} 条外部身份记录；候选决定数见下表 |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    unverified = sum(row.get("evidence_status") == "unverified" for row in current_enrichment)
    result_text, n = re.subn(
        r"^\| \[既有字段表\].*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_enrichment))}条，其中{sync.fmt(unverified)}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    batch_result = (
        f"### S4人物端点：Medici索引候选组（{DATE}）\n\n"
        + "；\n".join(
            f"{target['candidate']} → ../units/persons/{target['ku'].split('/')[-1]}.md（{target['group']}）"
            for target in TARGETS
        )
        + f"。本批5条直接关系候选继续待S6；cand-1628与未决的cand-5550未合并。S4累计{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射已登记，{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记；KU={len(planned_manifest)}。"
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
    return outputs, stats, totals, additions, direct_relation, planned_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Register four already-decided Medici person groups in S4.")
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
        print("dry-run passed: S3 groups, direct endpoints, source anchors, identity separation, and enrichment keys; no files changed")
        return

    previous = {path: path.read_bytes() if path.exists() else None for path in outputs}
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            original = previous[path]
            encoding = "utf-8-sig" if original is not None and original.startswith(b"\xef\xbb\xbf") else "utf-8"
            temp = path.with_suffix(path.suffix + ".tmp-s4-medici")
            temp.write_text(content, encoding=encoding, newline="\n")
        for path in outputs:
            temp = path.with_suffix(path.suffix + ".tmp-s4-medici")
            temp.replace(path)
    except Exception:
        for path, original in previous.items():
            temp = path.with_suffix(path.suffix + ".tmp-s4-medici")
            temp.unlink(missing_ok=True)
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        raise
    print(f"applied: wrote {len(outputs)} artifacts; enrichment_rows={len(additions)}; source_registry_rows_added=0")


if __name__ == "__main__":
    main()
