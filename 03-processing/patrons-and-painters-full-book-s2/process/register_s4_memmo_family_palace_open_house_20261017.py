from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

import register_s4_archive_memmo_query_sheet_20261017 as archive_sync
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

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

CANDIDATE = "cand-11534"
GROUP = "sg3-event-cand-11534"
KU_ID = "units/events/memmo-family-palace-open-house"
CARD = "04-knowledge/units/events/memmo-family-palace-open-house.md"
NAME_ZH = "安德烈亚·梅莫家族宫邸开放聚会"
NAME_EN = "Open-house gatherings at Andrea Memmo's family palace"
SOURCE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
ANCHOR = "s4-event-memmo-family-palace-open-house-20261017"

RELATION_IDS = {
    "st-chp15-p368-memmo-open-house-until-death",
    "st-chp15-p368-memmo-open-house-hosted-by",
    "st-chp15-p368-memmo-open-house-at-family-palace",
    "st-chp15-p368-memmo-open-house-with-brothers",
    "st-chp15-p368-memmo-open-house-for-advanced-spirits",
}
QUOTE = "In this palace, in the company of his brothers, he would hold open house to the more advanced spirits of the day until his death in 1792."


def make_card() -> str:
    source = {
        "citation": BOOK_CITATION,
        "location": "第15章，印刷页368，正文行41",
        "sentence_summary": "Haskell称 Andrea Memmo 在家族宫邸与兄弟们一起接待当时更为进步的知识界人士，持续至其1792年去世。原文未识别宫邸、兄弟或来客身份。",
        "original_quotes": [{"source_span": "line 41; print p.368", "text": QUOTE}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SOURCE,
            "source_span": "line 41; print p.368",
        },
    }
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [source],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    evidence = f"[S1：第15章 p.368](../../../{SOURCE})（L41）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记 Haskell 所述 Andrea Memmo 在家族宫邸举行的反复开放聚会。原文称他与兄弟们一起接待当时“更为进步的知识界人士”（the more advanced spirits of the day），直至 Memmo 于1792年去世。原文未提供聚会的具体日期或频率、宫邸的可识别名称、兄弟姓名或来客名单；不据此推定。该 KU 表示反复发生的社会活动，不代表单次聚会。{evidence}

**English:** This unit records Haskell’s account of recurring open-house gatherings held by Andrea Memmo in his family palace. The text says he would receive his brothers and “the more advanced spirits of the day” until his death in 1792. It gives no specific dates or frequency, identifiable palace name, brothers’ names, or guest list; none are inferred here. The KU represents a recurring social activity, not one individual gathering. {evidence}

### 来源记载

| 记载（中文） | Account (English) | 证据 / Evidence |
|---|---|---|
| Memmo 与兄弟在家族宫邸接待当时更为进步的知识界人士，直至1792年；地点和来客均未进一步识别。 | Memmo held open house with his brothers for the more advanced spirits of the day in the family palace until 1792; neither the place nor guests are further identified. | {evidence}（S1） |

## 关系与证据

未登记正式关系。五条直接 S2 关系候选（{', '.join(f'`{sid}`' for sid in sorted(RELATION_IDS))}）留待 S6。Andrea Memmo 已复用 `units/persons/andrea-memmo`；宫邸候选 `cand-10517`、兄弟候选 `cand-11532` 与来客类别候选 `cand-11533` 仍为 `undecided`，故不建立或扩写相应关系边。未使用外部来源。"""
    return f"---\n{fm}---\n\n{body.strip()}\n"


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if f"- {CARD}" in lines:
        raise AssertionError(f"accepted.yml already includes {CARD}")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Memmo's recurring open-house event group in S4")
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
    candidate = next((r for r in candidates if r.get("candidate_id") == CANDIDATE), None)
    assert candidate and candidate.get("suggested_type") == "event"
    row = next(r for r in alignments if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    assert row.get("decision") == "new" and not row.get("ku_id")
    assert sync.get_group(row.get("resolution_note", "")) == GROUP
    members = [
        r["candidate_id"] for r in alignments
        if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new"
        and sync.get_group(r.get("resolution_note", "")) == GROUP
    ]
    assert members == [CANDIDATE], members
    assert not (ROOT / CARD).exists() and CARD not in accepted
    assert not any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD for r in manifest)
    assert not any(r.get("type") == "event" and (r.get("name_en") or "").casefold() == NAME_EN.casefold() for r in manifest)

    endpoint_rows = {
        r.get("candidate_id"): r for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    assert endpoint_rows["cand-1642"].get("ku_id") == "units/persons/andrea-memmo"
    assert endpoint_rows["cand-1642"].get("decision") == "same"
    for unresolved in ("cand-10517", "cand-11532", "cand-11533"):
        assert endpoint_rows[unresolved].get("decision") == "undecided" and not endpoint_rows[unresolved].get("ku_id")

    statements = sync.load_statements()
    direct = [
        r for r in statements
        if CANDIDATE in (r.get("subject_candidate_id"), r.get("object_candidate_id"))
    ]
    relation_ids = {
        r["statement_id"] for r in direct
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert len(direct) == 5 and relation_ids == RELATION_IDS, (len(direct), relation_ids)
    source_text = " ".join((ROOT / SOURCE).read_text(encoding="utf-8-sig").split())
    assert " ".join(QUOTE.split()) in source_text

    planned_card = make_card()
    fm = re.match(r"\A---\n(.*?)\n---\n", planned_card, re.DOTALL)
    assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
    planned_alignment = [dict(r) for r in alignments]
    planned_row = next(r for r in planned_alignment if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    planned_row["ku_id"] = KU_ID
    planned_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD,
    }]

    with tempfile.TemporaryDirectory(prefix="pnp-s4-memmo-open-house-preview-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_card = temp_root / CARD
        temp_card.parent.mkdir(parents=True, exist_ok=True)
        temp_card.write_text(planned_card, encoding="utf-8-sig", newline="\n")
        original_base = build_field_facts.BASE
        build_field_facts.BASE = temp_root
        try:
            facts, source_registry, warnings, cards_with_tables = build_field_facts.extract_records([planned_manifest[-1]])
        finally:
            build_field_facts.BASE = original_base
    assert not warnings, warnings
    assert cards_with_tables == 1 and len(facts) == 1
    assert facts[0]["evidence_status"] == "source_backed" and facts[0]["source_ids"] == ["haskell-1980-rev-ed"]
    assert set(source_registry) == {"haskell-1980-rev-ed"}
    build_field_facts.assign_ids(facts, TABLES / "enrichment.jsonl")
    old_facts = [
        json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assert not any(r.get("ku_id") == KU_ID for r in old_facts)
    planned_facts = old_facts + facts
    assert len({r["enrichment_id"] for r in planned_facts}) == len(planned_facts)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, n = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_facts))}条，其中{sync.fmt(sum(r.get('evidence_status') == 'unverified' for r in planned_facts))}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    process_text = archive_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### S4 event：Memmo 家族宫邸开放聚会组登记（{DATE}）\n\n"
        f"- `{CANDIDATE}`（`{GROUP}`）登记为[Memmo 宫邸开放聚会事件卡](../../../{CARD})。按第15章 p.368，识别为反复活动而非单次事件；原文未识别具体宫邸、兄弟姓名、来客名单或具体场次。\n"
        f"- Andrea Memmo 复用 `units/persons/andrea-memmo`；宫邸 `cand-10517` 与两类未具名参与者 `cand-11532`、`cand-11533` 均仍 undecided。五条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；未新增正式关系或外部身份来源。\n"
        f"- S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU={sync.fmt(len(planned_manifest))}，字段={sync.fmt(len(planned_facts))}。"
    )
    planned_accepted = insert_accepted(accepted)

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP}; candidate={CANDIDATE}; new_KU={KU_ID}; "
            f"direct_statements={len(direct)}; relation_candidates={len(relation_ids)}; new_field_rows={len(facts)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"enrichment={len(old_facts)}->{len(planned_facts)}"
        )
        for fact in facts:
            print(f"  {fact['field']} | {fact['source_ref']} | {fact['evidence_status']}")
        return 0

    (ROOT / CARD).write_text(planned_card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    build_field_facts.write_jsonl(TABLES / "enrichment.jsonl", planned_facts)
    ACCEPTED.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: group={GROUP}; candidate={CANDIDATE}; new_KU={KU_ID}; field_rows={len(facts)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"enrichment={len(old_facts)}->{len(planned_facts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
