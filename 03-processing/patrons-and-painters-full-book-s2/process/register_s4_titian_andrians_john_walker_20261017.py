from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as archive_sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
WORK_SOURCE = "02-sources/02-Markdown/02_CHP-2_sec_i.md"
WORK_GROUP = "workgrp-49973a4844cb3f"
WORK_MEMBER = "cand-4249"
WORK_KU = "units/works/titian-andrians"
WORK_CARD = "04-knowledge/units/works/titian-andrians.md"
WORK_ZH = "提香《安德罗斯人》"
WORK_EN = "The Andrians (Titian)"
PERSON_GROUP = "new-person:john-walker-e3f95ea0f9"
PERSON_MEMBER = "cand-4356"
PERSON_KU = "units/persons/john-walker"
PERSON_CARD = "04-knowledge/units/persons/john-walker.md"
PERSON_ZH = "约翰·沃克"
PERSON_EN = "John Walker"
ANCHOR = "s4-work-titian-andrians-and-person-john-walker-20261017"

RELATION_IDS = {
    "st-chp2-seci-l124-157-albani-study-andrians",
    "st-chp2-seci-l124-157-darpino-copy-andrians",
    "st-chp2-seci-l124-157-rubens-version-andrians",
    "st-chp2-seci-l124-157-walker-view-andrians",
    "st-chp2-seci-l44-53-andrians-transfer",
}
WALKER_RELATION_IDS = {
    "st-chp2-seci-l124-157-walker-view-andrians",
    "st-chp2-seci-l124-157-walker-view-worship",
}
WORK_QUOTES = (
    "In particular the art treasures accumulated by the Este over the centuries were looted, and among the pictures which Cardinal Aldobrandini, the papal nephew, brought with him back to\nRome were Titian’s Worship os Venus, The Andrians and Bacchus and Ariadne.",
    "4 Though the Cavaliere d’Arpino copied them (see MS. note in Baglione, p. 372) and Albani must have studied them when he came to Rome in 1601-2. John Walker suggests that it is unlikely that Rubens made copies of the Worship of Venus and The Andrians during his visit to Rome. His versions of these pictures, now in Stockholm, date from very much later in his career and were probably made from copies by some other artist.",
)


def src(location: str, summary: str, quote: str, span: str) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": WORK_SOURCE,
            "source_span": span,
        },
    }


def card(title_zh: str, name_en: str, kind: str, sources: list[dict], body: str, sub_type: str = "") -> str:
    fm_data = {
        "title": f"{title_zh}（{name_en}）",
        "name_en": name_en,
        "type": kind,
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    if sub_type:
        fm_data["sub_type"] = sub_type
    fm = yaml.safe_dump(fm_data, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n{body.strip()}\n"


def cards() -> dict[str, str]:
    source_p25 = src(
        "第2章，印刷页25，正文行49–50；原 OCR 行含相邻题名拼写 `os`，本轮未作页图校正。",
        "Haskell叙述1598年后埃斯特家族艺术品被运往罗马，并将The Andrians列为红衣主教Aldobrandini带回罗马的提香绘画之一。原OCR在前一题名中写作`Worship os Venus`；此处按来源层保留，不据此改写题名。",
        WORK_QUOTES[0],
        "lines 49–50; print p.25",
    )
    source_p129 = src(
        "第2章，印刷页129注4，正文脚注行129；Haskell所引Baglione手稿与John Walker原文未独立查阅。",
        "Haskell称Cavaliere d’Arpino复制过相关作品，认为Albani应曾研究原作，并转述John Walker对Rubens后期版本的判断；这些复制、版本及评论均按Haskell的限定保留。",
        WORK_QUOTES[1],
        "line 129; print p.129, note 4",
    )
    work_body = f"""## 内容

### 描述

**中文：** 本卡登记哈斯克尔第2章以 *The Andrians* 称名、列为 Titian 绘画的一件作品。中文题名“安德罗斯人”为工作译名。第25页将其列入 Cardinal Aldobrandini 从 Ferrara 带回 Rome 的提香绘画；此处只记录哈斯克尔的叙述，不据此补写创作年代、原作现藏地或转移后的完整所有权链。第129页注4另述 Cavaliere d’Arpino 的复制、Albani 可能研究原作，以及 Rubens 在 Stockholm 的后期版本；它们均作为原作以外的复制／版本记录。Cavaliere d’Arpino 的身份仍待证；所引 Baglione 手稿与 John Walker 原文均未独立查阅。{source_link('第2章 p.25', 'L49–50')} {source_link('第2章 p.129 注4', 'L129')}

**English:** This unit records the work Haskell calls *The Andrians* and lists among Titian’s paintings in Chapter 2. The Chinese title is a working translation. On page 25 Haskell includes it among Titian paintings Cardinal Aldobrandini brought from Ferrara to Rome; this records Haskell’s account and does not add a creation date, present location, or complete ownership chain. Note 4 on page 129 separately discusses a copy by the Cavaliere d’Arpino, Albani’s possible study of the original, and later Rubens versions in Stockholm. These remain copies or versions distinct from the original painting. The identity behind “Cavaliere d’Arpino” remains unresolved; neither the cited Baglione manuscript nor John Walker’s original text was consulted. {source_link('Chapter 2, p.25', 'lines 49–50')} {source_link('Chapter 2, p.129 note 4', 'line 129')}

### 题名与基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 中文工作译名 | {WORK_ZH} | S1（据原文题名直译；非正式中译） |
| 原文题名 | The Andrians | S1（第2章 p.25） |
| 作品类型 | 绘画 | S1（Haskell列入Titian的pictures） |
| 创作者（按Haskell归属） | Titian | S1（第2章 p.25） |

### 本章相关记载

| 事项 | 来源表述与范围 | 证据 |
|---|---|---|
| 转移记载 | Haskell称 Cardinal Aldobrandini 从 Ferrara 带回 Rome 的提香绘画中包括本作；不扩展为完整所有权链 | S1（第2章 p.25） |
| 复制记载 | Haskell称 Cavaliere d’Arpino 复制过这些绘画；姓名所指身份仍未确认，所引 Baglione 手稿未查 | S2（第2章 p.129 注4） |
| Albani相关 | Haskell推测 Albani 来罗马时应研究过这些原作，保留为作者推断 | S2（第2章 p.129 注4） |
| Rubens版本 | Haskell称 Stockholm 有较晚的 Rubens 版本，并推测其可能依其他画家的复制品制作；不与本原作合并 | S2（第2章 p.129 注4） |
| Walker评价 | 哈斯克尔转述 John Walker 认为 Rubens 在罗马访问期间不太可能直接临摹原作；Walker 身份仅按书内姓名形式记录 | S2（第2章 p.129 注4） |

## 关系与证据

目前没有登记在 `relations.csv` 中的正式关系。五条直接 S2 关系候选 `st-chp2-seci-l124-157-albani-study-andrians`、`st-chp2-seci-l124-157-darpino-copy-andrians`、`st-chp2-seci-l124-157-rubens-version-andrians`、`st-chp2-seci-l124-157-walker-view-andrians`、`st-chp2-seci-l44-53-andrians-transfer` 均留待 S6；d’Arpino 候选 `cand-0121` 的身份仍为 undecided。"""
    work_card = card(WORK_ZH, WORK_EN, "work", [source_p25, source_p129], work_body, "painting")

    walker_body = f"""## 内容

### 描述

**中文：** 本卡只记录哈斯克尔第2章注4中的人物姓名形式 John Walker。哈斯克尔将 Rubens 在罗马访问期间是否直接临摹 *The Worship of Venus* 与 *The Andrians* 两件原作的判断归于 Walker，并以“不太可能”限定；注释未提供其著作题名、版本或进一步身份信息。本轮没有找到唯一对应的既有人物 KU，也未核对外部规范记录，因此不补写生卒、职务或生平。{source_link('第2章 p.129 注4', 'L129')}

**English:** This unit records only the name John Walker as it appears in Haskell’s Chapter 2, note 4. Haskell attributes to Walker a qualified assessment that Rubens was unlikely to have copied the originals of *The Worship of Venus* and *The Andrians* directly during his visit to Rome. The note gives no title, edition, or further identifying information. No unique existing person KU or external authority record was identified in this pass, so no dates, office, or biography are added. {source_link('Chapter 2, p.129 note 4', 'line 129')}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 书内姓名形式 | John Walker | S1（第2章 p.129 注4） |

### 本章相关内容

Haskell称 John Walker 认为 Rubens 在罗马访问期间不太可能直接依据 Titian 的原作复制 *The Worship of Venus* 与 *The Andrians*。此处只保留该观点的归属，不确认 Walker 的外部身份或所引研究文本。关联对象分别为[提香《维纳斯的崇拜》](../works/titian-worship-of-venus.md)与[提香《安德罗斯人》](../works/titian-andrians.md)；两条 S2 关系候选均留待 S6。

## 关系与证据

没有正式关系登记。`st-chp2-seci-l124-157-walker-view-worship` 与 `st-chp2-seci-l124-157-walker-view-andrians` 是来源中关于 Walker 观点与两件作品的直接关系候选，均待 S6。"""
    walker_card = card(PERSON_ZH, PERSON_EN, "person", [source_p129], walker_body)
    return {WORK_CARD: work_card, PERSON_CARD: walker_card}


def source_link(label: str, line: str) -> str:
    return f"[{label}](../../../{WORK_SOURCE})（{line}）"


def insert_accepted(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    for path in sorted(card_paths):
        if f"- {path}" in lines:
            raise AssertionError(f"accepted.yml already includes {path}")
        insert_at = next(
            (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > path),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {path}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register The Andrians and its source-local John Walker person group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_field_facts

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    groups = {
        WORK_GROUP: (WORK_MEMBER, WORK_KU, "work", WORK_EN, WORK_CARD),
        PERSON_GROUP: (PERSON_MEMBER, PERSON_KU, "person", PERSON_EN, PERSON_CARD),
    }
    for group, (member, ku_id, kind, name_en, card_rel) in groups.items():
        assert member in candidate_by_id and candidate_by_id[member]["suggested_type"] == kind
        row = alignment_by_id[member]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == group
        members = [
            r["candidate_id"] for r in alignments
            if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == group
        ]
        assert members == [member], (group, members)
        assert not (ROOT / card_rel).exists() and card_rel not in accepted
        assert not any(r.get("ku_id") == ku_id or r.get("card_path") == card_rel for r in manifest)
        assert not any(r.get("type") == kind and (r.get("name_en") or "").casefold() == name_en.casefold() for r in manifest)

    source = (ROOT / WORK_SOURCE).read_text(encoding="utf-8-sig")
    normalized = " ".join(source.split())
    for quote in WORK_QUOTES:
        assert " ".join(quote.split()) in normalized, "source quote changed"
    statements = sync.load_statements()
    direct = [
        r for r in statements
        if WORK_MEMBER in (r.get("subject_candidate_id"), r.get("object_candidate_id"))
    ]
    relations = {
        r["statement_id"] for r in direct
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert len(direct) == 5 and relations == RELATION_IDS, (len(direct), relations)
    person_direct = [
        r["statement_id"] for r in statements
        if PERSON_MEMBER in (r.get("subject_candidate_id"), r.get("object_candidate_id"))
        and (r.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert set(person_direct) == WALKER_RELATION_IDS and len(person_direct) == len(WALKER_RELATION_IDS), person_direct

    planned_cards = cards()
    assert set(planned_cards) == {WORK_CARD, PERSON_CARD}
    for card_rel, text in planned_cards.items():
        fm = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        assert fm and isinstance(yaml.safe_load(fm.group(1)), dict), f"invalid frontmatter: {card_rel}"

    planned_alignment = [dict(row) for row in alignments]
    for member, ku_id, group in ((WORK_MEMBER, WORK_KU, WORK_GROUP), (PERSON_MEMBER, PERSON_KU, PERSON_GROUP)):
        row = next(r for r in planned_alignment if r.get("candidate_id") == member and not r.get("external_source"))
        row["ku_id"] = ku_id
        row["resolution_note"] += f" S4 registration: mapped {group} to {ku_id}."
    planned_manifest = list(manifest) + [
        {"ku_id": WORK_KU, "type": "work", "canonical_name": WORK_ZH, "name_en": WORK_EN,
         "source_task": TASK, "card_path": WORK_CARD},
        {"ku_id": PERSON_KU, "type": "person", "canonical_name": PERSON_ZH, "name_en": PERSON_EN,
         "source_task": TASK, "card_path": PERSON_CARD},
    ]
    with tempfile.TemporaryDirectory(prefix="pnp-s4-andrians-preview-") as temp_dir:
        temp_root = Path(temp_dir)
        for path, text in planned_cards.items():
            p = temp_root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8-sig", newline="\n")
        original_base = build_field_facts.BASE
        build_field_facts.BASE = temp_root
        try:
            facts, source_registry, warnings, cards_with_tables = build_field_facts.extract_records(planned_manifest[-2:])
        finally:
            build_field_facts.BASE = original_base
    assert not warnings, warnings
    assert cards_with_tables == 2 and facts
    assert all(r["evidence_status"] == "source_backed" and r["source_ids"] == ["haskell-1980-rev-ed"] for r in facts)
    assert set(source_registry) <= {"haskell-1980-rev-ed"}
    build_field_facts.assign_ids(facts, TABLES / "enrichment.jsonl")
    old_facts = [
        json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assert not any(r.get("ku_id") in {WORK_KU, PERSON_KU} for r in old_facts)
    planned_facts = old_facts + facts
    assert len({r["enrichment_id"] for r in planned_facts}) == len(planned_facts)
    unverified = sum(r.get("evidence_status") == "unverified" for r in planned_facts)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, n = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_facts))}条，其中{sync.fmt(unverified)}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    process_text = archive_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### S4 work/person：The Andrians 与 John Walker 直接端点登记（{DATE}）\n\n"
        f"- work 组 `{WORK_GROUP}`（cand-4249，两处提及：第2章 p.25与p.129注4）登记为[提香《安德罗斯人》](../../../{WORK_CARD})。只按Haskell归作Titian绘画；Ferrara至Rome的转移说法归于Haskell。Rubens版本保持与原作区分；相邻 OCR 题名 `Worship os Venus` 原样注明，未作本轮OCR校正。\n"
        f"- person 组 `{PERSON_GROUP}`（cand-4356）登记为[John Walker](../../../{PERSON_CARD})，只记录Haskell的姓名形式及其对《维纳斯的崇拜》和《安德罗斯人》的限定性转述观点；无外部身份核对或传记补写。\n"
        f"- The Andrians 的五条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）及 Walker—The Worship of Venus 的观点候选 `st-chp2-seci-l124-157-walker-view-worship` 均留待 S6。cand-0121（Cavaliere d’Arpino）仍 undecided；本次不由其复制关系推断姓名或身份。没有新增正式关系或外部身份记录。\n"
        f"- S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条，KU 总数{sync.fmt(len(planned_manifest))}，结构化字段{sync.fmt(len(planned_facts))}条。"
    )
    planned_accepted = insert_accepted(accepted, [WORK_CARD, PERSON_CARD])

    if args.dry_run:
        print(
            f"dry-run passed: groups=2; new_KUs=2; candidate_mappings=2; direct_relation_candidates={len(relations)}; "
            f"new_field_rows={len(facts)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"enrichment={len(old_facts)}->{len(planned_facts)}"
        )
        for row in facts:
            print(f"  {row['ku_id']} | {row['field']} | {row['value']} | {row['evidence_status']} | {row['source_ref']}")
        return 0

    for path, text in planned_cards.items():
        (ROOT / path).write_text(text, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    build_field_facts.write_jsonl(TABLES / "enrichment.jsonl", planned_facts)
    ACCEPTED.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=2; new_KUs=2; candidate_mappings=2; direct_relation_candidates_pending={len(relations)}; "
        f"new_field_rows={len(facts)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"enrichment={len(old_facts)}->{len(planned_facts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
