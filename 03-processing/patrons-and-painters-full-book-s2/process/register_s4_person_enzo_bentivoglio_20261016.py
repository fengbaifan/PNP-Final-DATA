from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
STAGES = PROCESS_DIR / "stages.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"

CANDIDATE = "cand-0290"
GROUP = "new-person:bentivoglio-enzo-62e0406c74"
KU_ID = "units/persons/enzo-bentivoglio"
CARD_REL = "04-knowledge/units/persons/enzo-bentivoglio.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "恩佐·本蒂沃利奥"
NAME_EN = "Enzo Bentivoglio"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/B.csv"
PALACE_STATEMENT = "st-chp2-seciv-l65-77-enzo-buys-borghese-palace-1619"
PALACE_QUOTE = "his brother Enzo bought in 1619"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-enzo-bentivoglio-20261016"


BODY_QUOTES = (
    (
        "line 57",
        "The Bentivoglio came from Ferrara, where they had for centuries been one of the most distinguished families.",
    ),
    (
        "line 58",
        "His younger brothers Guido and Enzo saw their duty in a different light.",
    ),
    (
        "lines 60–62",
        "Enzo served for a time as ‘ambassador’ from Ferrara to\n"
        "Rome—a post specially created by the Pope to satisfy local sensibilities.\n"
        "Both men were extremely fond of art, and showed a fine and adventurous taste.",
    ),
)
INDEX_QUOTE = "Bentivoglio, Enzo"


def source_row(location: str, summary: str, quotes: list[tuple[str, str]], source_file: str, source_span: str):
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [
            {"source_span": span, "text": quote}
            for span, quote in quotes
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": source_span,
        },
    }


def make_card() -> str:
    sources = [
        source_row(
            "第2章，印刷页48–49；OCR L57–62",
            "正文将 Enzo 与 Guido 记为 Ippolito 的弟弟，并称 Enzo 曾一度担任从 Ferrara 到 Rome 的“ambassador”；作者也称两人热爱艺术。索引姓名形式由另一条索引证据给出。",
            list(BODY_QUOTES),
            SOURCE_FILE,
            "lines 57–62; print pp. 48–49; PDF physical pp. 33–34",
        ),
        source_row(
            "全书索引，B.csv#137；索引页码48、49、50、55、182；CSV记录行139",
            "索引以 Bentivoglio, Enzo 为姓名主项，并指向书内五个页码。",
            [("B.csv#137; CSV line 139", INDEX_QUOTE)],
            INDEX_FILE,
            "B.csv#137; CSV line 139; indexed pages 48, 49, 50, 55, 182",
        ),
    ]
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
    p48 = "[第2章 p.48](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md)（L57–62）"
    idx = "[全书索引 B.csv#137](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)（CSV记录行139）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 哈斯克尔书中索引列名“Bentivoglio, Enzo”。第2章将 Enzo 列为 Ippolito 的弟弟之一，称他曾一度担任从费拉拉到罗马的“使节”，并将他与 Guido 一并描述为热爱艺术。本卡登记书内所指人物，不补入全名、生卒或未经本书支持的传记。{idx} {p48}

**English:** The index of Haskell’s book lists the name “Bentivoglio, Enzo.” Chapter 2 identifies Enzo as one of Ippolito’s younger brothers, says that he served for a time as an “ambassador” from Ferrara to Rome, and describes him and Guido as strongly interested in art. This card records the person identified within the book and adds no fuller personal name, dates, or biography unsupported by the source. {idx} {p48}

### 名称与书内身份

- **索引姓名：** Bentivoglio, Enzo；正文顺序显示为 Enzo Bentivoglio。中文显示名“恩佐·本蒂沃利奥”为项目工作译名。{idx}
- **书内身份语境：** 第2章称 Enzo 是 Ippolito 的弟弟之一，并称其曾一度担任 Ferrara 至 Rome 的“ambassador”；原文用引号标出该职务称谓且未给出任职日期。此处为书内叙述，不构成已登记的正式关系。{p48}
- **身份边界：** 本卡不与 Guido Bentivoglio 人物或 Bentivoglio 家族 KU 合并；未使用外部身份源，不推定 Enzo 的全名、生卒或其他履历。{idx} {p48}

## 关系与证据

当前没有登记正式关系。涉及 Enzo 的 11 条 S2 关系候选保留待 S6 逐条裁决；其中正文关于1619年 Borghese 宫购买者的引句定位已在过程记录中更正，脚注归属差异仍按原记录保留。{p48}
"""


def insert_accepted(accepted_text: str) -> str:
    lines = accepted_text.splitlines()
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Enzo Bentivoglio person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert CANDIDATE in candidate_by_id
    candidate = candidate_by_id[CANDIDATE]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Bentivoglio, Enzo"
    assert candidate.get("index_entry_id") == "B.csv#137"
    alignment = decision_by_id[CANDIDATE]
    assert alignment.get("decision") == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP

    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-identity person KU already exists in manifest"
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    for _, quote in BODY_QUOTES:
        assert quote in source_text, quote
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert '"Bentivoglio, Enzo"' in index_text

    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = []
    for row in statements:
        q = row.get("qualifiers", {})
        candidate_refs = {
            row.get("subject_candidate_id"),
            row.get("object_candidate_id"),
            *q.get("mentioned_candidate_ids", []),
        }
        if CANDIDATE in candidate_refs or CANDIDATE in q.values():
            related.append(row)
    palace = next(row for row in statements if row.get("statement_id") == PALACE_STATEMENT)
    assert palace.get("qualifiers", {}).get("source_line_start") == 67
    assert palace.get("qualifiers", {}).get("source_line_end") == 67
    assert palace.get("qualifiers", {}).get("footnote_refs") == [
        {"marker": 1, "segment_id": "chp-2:02_CHP-2_sec_iv:l190-245", "source_line": 214}
    ]
    assert palace.get("qualifiers", {}).get("relation_candidate") is True
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    assert len(related) == 12, f"unexpected S2 statement count involving Enzo: {len(related)}"
    assert relation_count == 11, f"unexpected relation-candidate count involving Enzo: {relation_count}"

    planned_statements = [dict(row) for row in statements]
    planned_palace = next(row for row in planned_statements if row.get("statement_id") == PALACE_STATEMENT)
    planned_palace["original_quote"] = PALACE_QUOTE
    planned_palace["qualifiers"] = dict(planned_palace["qualifiers"])
    planned_palace["qualifiers"]["source_line_end"] = 68
    planned_palace["qualifiers"]["qualification"] += (
        " Evidence locator correction (2026-10-16): original_quote now quotes the buyer clause at L67–68; "
        "the claim, subject, object, date, and footnote reference are unchanged."
    )
    assert " ".join(PALACE_QUOTE.split()) in " ".join(source_text.split())

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

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
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_recent = (
        "。各组来源、身份边界和映射更正见[过程记录]"
    )
    new_recent = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[恩佐·本蒂沃利奥人物卡]"
        f"(../units/persons/enzo-bentivoglio.md)，11条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_recent) == 1
    next_result = next_result.replace(old_recent, new_recent, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    stages_text = STAGES.read_text(encoding="utf-8-sig")
    assert f"S4 person: {GROUP}" not in knowledge_text
    assert f"Evidence locator correction for {PALACE_STATEMENT}" not in stages_text
    next_knowledge = knowledge_text + (
        f"\n\n### S4 person：Enzo Bentivoglio 跨章身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；当前 S3 组仅含此候选。候选索引 B.csv#137 明列 "
        f"“Bentivoglio, Enzo”，索引页码为48、49、50、55、182；正文第2章 p.48 将 Enzo 列为 "
        "Ippolito 的弟弟之一，并称其曾一度担任从 Ferrara 至 Rome 的“ambassador”，作者并称 Enzo 与 "
        "Guido 热爱艺术。卡片以索引和正文为依据，不补全个人姓名或传记，不与 Guido 人物或 Bentivoglio "
        "家族合并；未使用外部身份源。\n"
        f"- 涉及 Enzo 的12条 S2 陈述中，11条为关系候选，全部留待 S6；本次不登记正式关系或 S5 补足。\n"
        f"- 修正 {PALACE_STATEMENT} 的原文引句与行范围：原存引句止于买方姓名前，现据 p.49 L67–68 "
        f"保存“{PALACE_QUOTE}”，source_line_end 由67改为68。断言、端点、1619日期及脚注 L214 的"
        "Bentivoglio 家族表述均未改；主文与脚注的归属表述继续并列，不作静默消解。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_stages = stages_text + (
        f"\n\n### Evidence locator correction for {PALACE_STATEMENT}（{DATE}）\n\n"
        "复核第2章 p.49 L67–68 后，将原 statement 引句由不完整的前置短语校正为 "
        "“his brother Enzo bought in 1619”，并将 source_line_end 从67改为68。断言内容、人物与宫殿"
        "端点、1619日期及注1定位不变；注1 L214 另称 Bentivoglio 从 Altemps 家族购得宫殿，"
        "两处措辞均保留，不据此静默确定归属。"
    )
    next_accepted = insert_accepted(accepted)

    target_files = [
        TABLES / "alignment.csv", statements_path, TABLES / "ku-manifest.csv",
        ACCEPTED, KNOWLEDGE, STAGES, RESULT,
    ]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in target_files)

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; "
            f"identity_sources=2; related_statements={len(related)}; "
            f"relation_candidates_pending={relation_count}; palace_quote_corrected=True; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    write_targets = {
        TABLES / "alignment.csv": None,
        statements_path: None,
        TABLES / "ku-manifest.csv": None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        STAGES: next_stages,
        RESULT: next_result,
    }
    for path in write_targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    statements_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in planned_statements) + "\n",
        encoding="utf-8-sig",
        newline="\n",
    )
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    for path, content in write_targets.items():
        if content is not None:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; relation_candidates_pending={relation_count}; "
        f"palace_quote_corrected=True; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; recovery_backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
