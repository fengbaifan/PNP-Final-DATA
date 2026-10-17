from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
BACKLOG_PATH = TABLES / "candidate-backlog.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

PERSON_CANDIDATES = ("cand-0482", "cand-0483")
PERSON_GROUP = "new-person:callot-jacques-b8b6e13e5f"
PERSON_KU = "units/persons/jacques-callot"
PERSON_CARD = "04-knowledge/units/persons/jacques-callot.md"
PERSON_NAME_ZH = "雅克·卡洛"
PERSON_NAME_EN = "Jacques Callot"

WORK_CANDIDATE = "cand-12429"
WORK_ALIGNMENT = "aln-12634"
WORK_GROUP = "new-work:callot-la-fiera-dell-impruneta-20261017"
WORK_KU = "units/works/jacques-callot-la-fiera-dell-impruneta-print"
WORK_CARD = "04-knowledge/units/works/jacques-callot-la-fiera-dell-impruneta-print.md"
WORK_NAME_ZH = "雅克·卡洛《因普鲁内塔集市》版画"
WORK_NAME_EN = "Jacques Callot's print of La Fiera dell'Impruneta"

BACKLOG_ID = "bl-0005"
STATEMENT_ID = "st-chp8-p213-callot-print-and-original-plate"
MENTION_PRINT = "m-chp8-p213-040"
MENTION_TITLE = "m-chp8-p213-041"
MENTION_PERSON = "m-chp8-p213-086"
SOURCE_DIR = ROOT / "02-sources" / "02-Markdown"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#s3-s4-callot-cross-chapter-group"


def make_source(file: str, location: str, summary: str, span: str, quote: str) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{file}",
            "source_span": f"{span}; {location}",
        },
    }


PERSON_SOURCES = [
    make_source(
        "04_CHP-4_sec_i.md",
        "第4章；印刷页95；OCR L13–14",
        "Haskell names Jacques Callot among a group of artists and musicians associated with the Medici court's social circle.",
        "lines 13–14",
        "a dazzling group of artists and musicians, including\nGiulio Parigi, Jacques Callot, Giovanni da San Giovanni, Filippo Napoletano and\nGerolamo Frescobaldi.",
    ),
    make_source(
        "05_CHP-5_sec_iii.md",
        "第5章；印刷页133；OCR L16–17",
        "Haskell contrasts the Bamboccianti's works with what he calls the distortions of Georges de la Tour and the brutality of Jacques Callot.",
        "lines 16–17",
        "We do not find in their works the distortions of Georges de la Tour or the brutality of Jacques\nCallot;",
    ),
    make_source(
        "08_CHP-8_sec_i.md",
        "第8章；印刷页213；OCR L112",
        "Haskell refers to Callot's print La Fiera dell'Impruneta while separately describing what was apparently its original plate.",
        "line 112",
        "Callot’s print of La Fiera dellTmpruneta.",
    ),
    make_source(
        "13_CHP-13_intro.md",
        "第13章；印刷页343；OCR L111",
        "Haskell names Callot in a passage about prints acquired during foreign travel; the OCR merges spaces in this line.",
        "line 111",
        "Rembrandtand Callot whomhe bought on his foreign travels;",
    ),
]

WORK_SOURCES = [
    make_source(
        "08_CHP-8_sec_i.md",
        "第8章；印刷页213；OCR L111–112",
        "Haskell distinguishes the brothers' possession of what was apparently an original plate from the print by Jacques Callot that the plate was for. S2's visual comparison reads the title as La Fiera dell'Impruneta; the OCR source is left unchanged.",
        "lines 111–112",
        "what was apparently the original plate for\nCallot’s print of La Fiera dellTmpruneta.",
    )
]

PERSON_BODY = """### 描述

**中文：** 本卡记录《赞助人与画家》第4、5、8、13章提及的 Jacques Callot。第4章以全名将他列入一组艺术家与音乐家；第5章在评价 Bamboccianti 绘画时以 Callot 作比较；第8章称一件版画为 Callot 所作；第13章也在版画收藏语境中提及 Callot。中文显示名“雅克·卡洛”为项目工作音译，不构成外部身份核验或完整生平。〔[第4章 p.95](../../../02-sources/02-Markdown/04_CHP-4_sec_i.md)（L13–14）；[第5章 p.133](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md)（L16–17）；[第8章 p.213](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L112）；[第13章 p.343](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L111）〕

**English:** This unit records Jacques Callot as mentioned in Chapters 4, 5, 8, and 13 of *Patrons and Painters*. Chapter 4 names him among a group of artists and musicians; Chapter 5 invokes him in a comparison of Bamboccianti painting; Chapter 8 refers to a print by Callot; and Chapter 13 mentions him in a discussion of print collecting. The Chinese display name is a project working transliteration; this card does not claim external identity verification or provide a full biography. ([Chapter 4, p. 95](../../../02-sources/02-Markdown/04_CHP-4_sec_i.md) (lines 13–14); [Chapter 5, p. 133](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md) (lines 16–17); [Chapter 8, p. 213](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md) (line 112); [Chapter 13, p. 343](../../../02-sources/02-Markdown/13_CHP-13_intro.md) (line 111).)

### 名称与身份边界

- 本卡合并 S3 人物候选 `cand-0482`（C.csv#6，索引页95、133、343）与 `cand-0483`（C.csv#7，索引页213）。两条索引候选规范名均为 Callot, Jacques；第4章的全名与其他章节的姓氏提及相互支持同一书内人物身份。
- C.csv#7 的 “Fiera dell'Impruneta” 是作品定位子项，不是第二个人名。第8章相应版画作品另登记为[《La Fiera dell'Impruneta》版画](../works/jacques-callot-la-fiera-dell-impruneta-print.md)。
- 第8章将兄弟所持对象称为“apparently the original plate”；该原版模具候选 `cand-7570` 与本人物及版画作品均保持分开，类型仍待证。
- 本卡只记录原书指称，不补充生卒、国籍、创作日期或版画版本。

## 关系与证据

当前没有登记为 S6 正式关系的记录。书中提及的艺术圈、风格比较、版画及收藏关系仍按原有 S2 陈述保留；本次未新增正式关系。"""

WORK_BODY = """### 描述

**中文：** 本卡记录哈斯克尔所称 Jacques Callot 的《La Fiera dell'Impruneta》版画。第8章将它与兄弟所持、被称为“apparently the original plate”的原版模具区分；本卡代表版画作品，不代表原版模具，也不指某一已识别的现存印张。S0 OCR 将题名转录为 “La Fiera dellTmpruneta”；S2 对照印刷页读作 “La Fiera dell'Impruneta”，OCR 来源文本保持不变。中文显示名为描述性工作译名；不补作品年代、版次、媒材或现存地点。〔[第8章 p.213](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L111–112）〕

**English:** This unit records the print that Haskell attributes to Jacques Callot as *La Fiera dell'Impruneta*. Chapter 8 distinguishes it from an object the brothers possessed that was described as “apparently the original plate.” This unit represents the print as a named work; it does not represent the plate or identify a surviving impression. The S0 OCR transcribes the title as “La Fiera dellTmpruneta”; S2's comparison with the printed page reads “La Fiera dell'Impruneta,” and the OCR source text remains unchanged. The Chinese display name is descriptive; no date, edition, medium, or present location is added. ([Chapter 8, p. 213](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md) (lines 111–112).)

### 名称与对象边界

- 书中题名：La Fiera dell'Impruneta；中文显示名为描述性工作译名。
- 作品类型：哈斯克尔称为 Jacques Callot 的 print；原书未在此处说明媒材、版次或制作日期。
- 对象边界：版画与被称为“apparently the original plate”的 cand-7570 分开。cand-7570 的对象类型仍待证，本卡不将其并入 work KU。

## 关系与证据

当前没有登记为 S6 正式关系的记录。第8章关于原版模具与版画的 S2 陈述仍留待 S6 审查；本次未新增正式关系。"""


def make_card(title: str, name_en: str, kind: str, sources: list[dict], body: str) -> str:
    frontmatter = {
        "title": f"{title}（{name_en}）",
        "name_en": name_en,
        "type": kind,
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n## 内容\n\n{body.strip()}\n"


def insert_cards(accepted: str, card_rels: tuple[str, ...]) -> str:
    lines = accepted.splitlines()
    for card_rel in card_rels:
        insert_at = next(
            (i for i, line in enumerate(lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def replace_artifact_line(text: str, prefix: str, replacement: str) -> str:
    text, count = re.subn(rf"(?m)^{re.escape(prefix)}.*$", replacement, text, count=1)
    assert count == 1, f"artifact line not found: {prefix}"
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile the Callot cross-chapter person group and register its distinct print work.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_fields, candidates = sync.read_csv(CANDIDATES_PATH)
    mention_fields, mentions = sync.read_csv(MENTIONS_PATH)
    backlog_fields, backlog = sync.read_csv(BACKLOG_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_ids = {row["ku_id"] for row in manifest}
    manifest_paths = {row["card_path"] for row in manifest}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert all(cid in candidate_by_id for cid in PERSON_CANDIDATES)
    assert [candidate_by_id[cid]["canonical_name"] for cid in PERSON_CANDIDATES] == ["Callot, Jacques"] * 2
    assert [candidate_by_id[cid]["suggested_type"] for cid in PERSON_CANDIDATES] == ["person"] * 2
    assert candidate_by_id["cand-0482"]["index_entry_id"] == "C.csv#6"
    assert candidate_by_id["cand-0482"]["index_page_range"] == "95, 133, 343"
    assert candidate_by_id["cand-0483"]["index_entry_id"] == "C.csv#7"
    assert candidate_by_id["cand-0483"]["sub_entry"] == "Fiera dell' Impruneta"
    for cid in PERSON_CANDIDATES:
        row = alignment_by_id[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == PERSON_GROUP
    person_group_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == PERSON_GROUP
    ]
    assert set(person_group_members) == set(PERSON_CANDIDATES)

    assert MENTION_PRINT in mention_by_id and MENTION_TITLE in mention_by_id
    assert mention_by_id[MENTION_PRINT]["candidate_id"] == "cand-0483"
    assert mention_by_id[MENTION_PRINT]["surface_form"] == "Callot’s print"
    assert mention_by_id[MENTION_PRINT]["start_char"] == "1260" and mention_by_id[MENTION_PRINT]["end_char"] == "1274"
    assert mention_by_id[MENTION_TITLE]["candidate_id"] == "cand-0483"
    assert mention_by_id[MENTION_TITLE]["surface_form"] == "La Fiera dellTmpruneta"
    assert MENTION_PERSON not in mention_by_id

    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}
    assert STATEMENT_ID in statement_by_id
    statement = statement_by_id[STATEMENT_ID]
    assert statement["subject_candidate_id"] == "cand-7489"
    assert statement["object_candidate_id"] == "cand-7570"
    assert statement["qualifiers"].get("relation_candidate") is True
    assert "cand-0483" in statement["qualifiers"].get("mentioned_candidate_ids", [])
    assert "cand-7570" in statement["qualifiers"].get("mentioned_candidate_ids", [])

    existing_candidate_max = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
    existing_alignment_max = max(int(row["alignment_id"].split("-")[1]) for row in alignments if row["alignment_id"].startswith("aln-"))
    assert WORK_CANDIDATE == f"cand-{existing_candidate_max + 1:04d}" and WORK_CANDIDATE not in candidate_by_id
    assert WORK_ALIGNMENT == f"aln-{existing_alignment_max + 1:04d}"
    assert BACKLOG_ID == f"bl-{len(backlog) + 1:04d}"
    assert all(row["status"] == "completed" for row in backlog)
    assert all(BACKLOG_ID != row["backlog_id"] for row in backlog)

    assert PERSON_KU not in manifest_ids and WORK_KU not in manifest_ids
    assert PERSON_CARD not in manifest_paths and WORK_CARD not in manifest_paths
    assert not (ROOT / PERSON_CARD).exists() and not (ROOT / WORK_CARD).exists()
    assert not any(row["type"] == "person" and row["name_en"] == PERSON_NAME_EN for row in manifest)
    assert not any(row["type"] == "work" and "La Fiera dell'Impruneta" in row["name_en"] for row in manifest)
    assert f"- {PERSON_CARD}" not in accepted and f"- {WORK_CARD}" not in accepted

    quoted_sources = [
        ("04_CHP-4_sec_i.md", PERSON_SOURCES[0]["original_quotes"][0]["text"]),
        ("05_CHP-5_sec_iii.md", PERSON_SOURCES[1]["original_quotes"][0]["text"]),
        ("08_CHP-8_sec_i.md", WORK_SOURCES[0]["original_quotes"][0]["text"]),
        ("13_CHP-13_intro.md", PERSON_SOURCES[3]["original_quotes"][0]["text"]),
    ]
    for file, quote in quoted_sources:
        content = " ".join((SOURCE_DIR / file).read_text(encoding="utf-8-sig").split())
        assert " ".join(quote.split()) in content, (file, quote)

    planned_candidates = list(candidates)
    planned_candidates.append({
        "candidate_id": WORK_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": "La Fiera dell'Impruneta, print by Jacques Callot",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell identifies a print by Jacques Callot titled in the S0 OCR as La Fiera dellTmpruneta. The passage distinguishes it from an object the brothers possessed, described as apparently the original plate. S2's visual comparison reads the printed title as La Fiera dell'Impruneta; keep the OCR source unchanged. The print is distinct from candidate cand-7570, whose type remains unresolved.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-8:08_CHP-8_sec_i:l108-118#L112",
    })

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    old_0483_note = planned_by_id["cand-0483"]["resolution_note"]
    planned_by_id["cand-0482"]["resolution_note"] += (
        " S3 cross-chapter identity review 2026-10-17: C.csv#6 (pages 95, 133, 343) and C.csv#7 (page 213, Fiera dell'Impruneta work subentry) "
        "share the same normalized full name Callot, Jacques. The full name appears on p.95; p.133 and p.343 give cross-chapter surname anchors, and p.213 attributes the named print to Callot. "
        "No external identity source was accessed; the print is separately represented by cand-12429."
    )
    planned_by_id["cand-0483"]["resolution_note"] = (
        f"source_ref=candidate=cand-0483;index_entry=C.csv#7;index_pages=213;s2_mentions={MENTION_PERSON}@02-sources/02-Markdown/08_CHP-8_sec_i.md#L112[Callot;chars=1260-1266]; "
        f"group={PERSON_GROUP}; S3 cross-chapter reconciliation 2026-10-17: the normalized full name matches C.csv#6 and the p.95 full-name anchor. "
        f"The index subentry Fiera dell'Impruneta is a work locator, not a second person. The p.213 work-phrase mentions {MENTION_PRINT} and {MENTION_TITLE} are reassigned to the separate work candidate {WORK_CANDIDATE}; {MENTION_PERSON} retains Callot as the person mention. "
        f"Prior S3 rationale preserved: {old_0483_note}"
    )
    for cid in PERSON_CANDIDATES:
        planned_by_id[cid]["ku_id"] = PERSON_KU
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {PERSON_GROUP} to {PERSON_KU}."
    planned_alignment.append({
        "alignment_id": WORK_ALIGNMENT,
        "candidate_id": WORK_CANDIDATE,
        "ku_id": WORK_KU,
        "external_source": "",
        "external_id": "",
        "decision": "new",
        "accessed_date": "",
        "process_ref": "S1-S4-full-book-2026-10-17",
        "legacy_ku_id": "",
        "resolution_note": (
            f"source_ref=candidate={WORK_CANDIDATE};candidate_source_ref=chp-8:08_CHP-8_sec_i:l108-118#L112;index_clue=C.csv#7 subentry Fiera dell'Impruneta; "
            f"statement={STATEMENT_ID};group={WORK_GROUP}; S3 source-local work identity: Haskell refers to a print by Jacques Callot and distinguishes it from the brothers' apparently original plate (cand-7570). "
            "No same-type work KU matched. The title remains source-limited; no date, medium, edition, or surviving impression is inferred. "
            f"S4 registration: mapped {WORK_GROUP} to {WORK_KU}."
        ),
    })

    planned_mentions = [dict(row) for row in mentions]
    planned_mention_by_id = {row["mention_id"]: row for row in planned_mentions}
    planned_mention_by_id[MENTION_PRINT]["candidate_id"] = WORK_CANDIDATE
    planned_mention_by_id[MENTION_PRINT]["note"] = "Mention of Callot's print; mapped to the separately identified work, not to the person or the original-plate candidate cand-7570."
    planned_mention_by_id[MENTION_TITLE]["candidate_id"] = WORK_CANDIDATE
    planned_mention_by_id[MENTION_TITLE]["note"] = "Title of Callot's print. S0 OCR reads La Fiera dellTmpruneta; S2 visual comparison reads La Fiera dell'Impruneta. S0 remains unchanged."
    planned_mentions.append({
        "mention_id": MENTION_PERSON,
        "segment_id": "chp-8:08_CHP-8_sec_i:l108-118",
        "candidate_id": "cand-0483",
        "surface_form": "Callot",
        "start_char": "1260",
        "end_char": "1266",
        "note": "Person mention inside the possessive phrase Callot's print; the full phrase and title are mapped separately to work candidate cand-12429.",
    })

    planned_statements = list(statements)
    target_statement = next(row for row in planned_statements if row["statement_id"] == STATEMENT_ID)
    mention_ids = list(target_statement["qualifiers"].get("mentioned_candidate_ids", []))
    if WORK_CANDIDATE not in mention_ids:
        mention_ids.append(WORK_CANDIDATE)
    target_statement["qualifiers"]["mentioned_candidate_ids"] = mention_ids

    planned_manifest = list(manifest) + [
        {"ku_id": PERSON_KU, "type": "person", "canonical_name": PERSON_NAME_ZH, "name_en": PERSON_NAME_EN, "source_task": TASK, "card_path": PERSON_CARD},
        {"ku_id": WORK_KU, "type": "work", "canonical_name": WORK_NAME_ZH, "name_en": WORK_NAME_EN, "source_task": TASK, "card_path": WORK_CARD},
    ]

    planned_backlog = list(backlog) + [{
        "backlog_id": BACKLOG_ID,
        "canonical_name": "La Fiera dell'Impruneta, print by Jacques Callot",
        "suggested_type": "work",
        "status": "completed",
        "source_id": "haskell-1980-rev-ed",
        "source_ref": "chp-8:08_CHP-8_sec_i:l108-118#L112",
        "statement_id": STATEMENT_ID,
        "endpoint_role": "named print distinguished from the brothers' apparently original-plate object",
        "candidate_id": WORK_CANDIDATE,
        "ku_id": WORK_KU,
        "decision_note": (
            "S1/S3/S4 completed 2026-10-17 after S2 separated the creator, the named print, and the apparently original plate. "
            "The source-local print is candidate cand-12429 / new-work group new-work:callot-la-fiera-dell-impruneta-20261017 and is registered in units/works/jacques-callot-la-fiera-dell-impruneta-print. "
            "Candidate cand-7570 remains a distinct type-unresolved original-plate object. The source does not establish a date, medium, edition, or surviving impression; the relation statement remains for S6 review."
        ),
        "process_ref": "S1-S4-full-book-2026-10-17",
    }]

    planned_accepted = insert_cards(accepted, (PERSON_CARD, WORK_CARD))
    stats = sync.summarize_by_type(planned_candidates, planned_alignment)
    totals = {key: sum(section[key] for section in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    candidate_count = len(planned_candidates)
    alignment_count = len(planned_alignment)
    external_count = sum(bool(row.get("external_source")) for row in planned_alignment)
    result_text = replace_artifact_line(
        result_text,
        "| [实体候选](../tables/entity-candidates.csv)",
        f"| [实体候选](../tables/entity-candidates.csv) | {candidate_count:,} candidates（新增 Callot《La Fiera dell'Impruneta》版画 work 候选；含直接关系端点候选 Luigi Pavini、Alessandro Farnese 公爵与 Paul Bonnefon） |",
    )
    result_text = replace_artifact_line(
        result_text,
        "| [全书对齐](../tables/alignment.csv)",
        f"| [全书对齐](../tables/alignment.csv) | {alignment_count:,} 条：{candidate_count:,} 条候选决定记录及 {external_count:,} 条外部身份记录；候选决定数见下表 |",
    )
    result_text = replace_artifact_line(
        result_text,
        "| [提及账本](../tables/mentions.csv)",
        f"| [提及账本](../tables/mentions.csv) | {len(planned_mentions):,} mentions |",
    )
    result_text = replace_artifact_line(
        result_text,
        "| [候选待办](../tables/candidate-backlog.csv)",
        f"| [候选待办](../tables/candidate-backlog.csv) | {len(planned_backlog)}条记录均已登记到KU，状态均为 completed；新增 Callot《La Fiera dell'Impruneta》work 对象；Paul Bonnefon编辑端点正式关系仍待S6 |",
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s3-s4-callot-cross-chapter-group\"></a>\n\n"
        "### S3–S4 person／work：Jacques Callot 跨章人物组与《La Fiera dell'Impruneta》作品边界（2026-10-17）\n\n"
        f"S3 复核 `cand-0482`（C.csv#6，索引页95、133、343）与 `cand-0483`（C.csv#7，p.213 子项 Fiera dell'Impruneta）：两条人物候选的规范全名均为 Callot, Jacques。第4章 p.95 给出 Jacques Callot 全名；第5章 p.133、第8章 p.213 与第13章 p.343 形成跨章姓氏/归属锚点。故保留 `{PERSON_GROUP}` 为同一人物 new 组，不映射到任何已有 person KU；未访问外部身份源。\n\n"
        f"检查第8章 p.213 后发现 `{MENTION_PRINT}`（Callot’s print）和 `{MENTION_TITLE}`（La Fiera dellTmpruneta）被挂在人物候选下。现将两条作品提及改映射至新 work 候选 `{WORK_CANDIDATE}`，新增 `{MENTION_PERSON}` 将其中人名 Callot 单独映射回 `cand-0483`。原断言 `{STATEMENT_ID}` 的 subject/object 保持不变：Del Rosso 兄弟与被称为“apparently the original plate”的 `cand-7570`；只将版画 work 候选补入 mentioned_candidate_ids。\n\n"
        f"新 work 候选 `{WORK_CANDIDATE}` 以 `{WORK_GROUP}` 裁为 source-local `new`，和 `{PERSON_GROUP}` 的人物组分开，经 backlog `{BACKLOG_ID}` 按 S1→S3→S4 登记为[《La Fiera dell'Impruneta》版画](../../../{WORK_CARD})。印刷页对照读作 La Fiera dell'Impruneta；S0 OCR 保持不变。版画与原版模具分开；cand-7570 的类型继续待证，不新增推定关系。\n\n"
        "Callot 相关艺术圈、收藏及版画陈述仍留在 S2；未写 `relations.csv` 或新增正式关系。\n"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S3–S4 跨章复核：Jacques Callot 人物组与《La Fiera dell'Impruneta》版画分型（2026-10-17）\n\n"
        f"`cand-0482`、`cand-0483` 按 C.csv#6/#7 与第4、5、8、13章的人名锚点归为同一人物组，登记为[Jacques Callot 人物卡](../units/persons/jacques-callot.md)。C.csv#7 的 Fiera 子项另指向作品；第8章 p.213 的版画名称提及现拆映至新 work 候选 `{WORK_CANDIDATE}`，与原版模具候选 `cand-7570` 分开。版画候选经 backlog `{BACKLOG_ID}` 完成 S1→S3→S4，登记为[《La Fiera dell'Impruneta》版画](../units/works/jacques-callot-la-fiera-dell-impruneta-print.md)。\n"
        "`cand-7570` 类型仍待证；相关关系继续留待 S6。未新增正式关系或外部身份断言。\n"
        f"S3 new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}；S4 已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    person_card = make_card(PERSON_NAME_ZH, PERSON_NAME_EN, "person", PERSON_SOURCES, PERSON_BODY)
    work_card = make_card(WORK_NAME_ZH, WORK_NAME_EN, "work", WORK_SOURCES, WORK_BODY)
    for card_text, expected_type in ((person_card, "person"), (work_card, "work")):
        parts = card_text.split("---", 2)
        assert len(parts) == 3 and yaml.safe_load(parts[1])["type"] == expected_type

    if args.dry_run:
        print("Callot cross-chapter person/work boundary dry-run passed")
        print(f"{PERSON_CANDIDATES} -> one person KU; {WORK_CANDIDATE} -> separate print work KU")
        print(f"{MENTION_PRINT} and {MENTION_TITLE} -> work; {MENTION_PERSON} -> person")
        print(f"{STATEMENT_ID}: original-plate object remains cand-7570; work added only as a mention")
        print(f"candidates={len(candidates):,}->{len(planned_candidates):,}; alignments={len(alignments):,}->{len(planned_alignment):,}; manifest={len(manifest):,}->{len(planned_manifest):,}")
        print(f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("source quotations, identity group, S1 backlog route, S2 mentions, statement boundaries, and card frontmatter checked; no files changed")
        return 0

    for card_rel, content in ((PERSON_CARD, person_card), (WORK_CARD, work_card)):
        (ROOT / card_rel).write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(CANDIDATES_PATH, candidate_fields, planned_candidates)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(MENTIONS_PATH, mention_fields, planned_mentions)
    sync.write_csv(BACKLOG_PATH, backlog_fields, planned_backlog)
    STATEMENTS_PATH.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in planned_statements) + "\n",
        encoding="utf-8-sig",
        newline="\n",
    )
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: Callot person candidates={len(PERSON_CANDIDATES)}; work={WORK_CANDIDATE}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={len(planned_manifest):,}; candidates={candidate_count:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
