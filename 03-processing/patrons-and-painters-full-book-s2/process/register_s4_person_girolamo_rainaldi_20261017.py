from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE_ID = "cand-2093"
GROUP = "new-person:girolamo-rainaldi-cfd3000d9f"
KU_ID = "units/persons/girolamo-rainaldi"
CARD_REL = "04-knowledge/units/persons/girolamo-rainaldi.md"
NAME_ZH = "吉罗拉莫·拉伊纳尔迪"
NAME_EN = "Girolamo Rainaldi"
ANCHOR = "s4-person-girolamo-rainaldi-20261017"
S3_ANCHOR = "s3-person-girolamo-rainaldi-treccani-20261017"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/girolamo-rainaldi_%28Dizionario-Biografico%29/"
TRECCANI_SOURCE = "Treccani, Dizionario Biografico degli Italiani"
TRECCANI_ID = TRECCANI_URL
QUOTES = (
    {
        "location": "第6章；印刷页147；OCR L22–23",
        "source_span": "lines 22–23; print p. 147",
        "quote": "Girolamo Rainaldi, a totally unfashionable figure nearly thirty years older than himself",
        "summary_cn": "Haskell称 Girolamo Rainaldi 接替Bernini成为首席建筑师之一；此处年龄比较是作者估计。",
    },
    {
        "location": "第6章；印刷页147；OCR L22–23",
        "source_span": "lines 22–23; print p. 147",
        "quote": "Rainaldi planned the vast palace on the Piazza Navona where Innocent had lived as a cardinal",
        "summary_cn": "Haskell将Piazza Navona上的大宅规划归于Rainaldi；Treccani DBI也把palazzo Pamphilj列为Girolamo Rainaldi的作品，构成姓名、职业和建筑对象的对应。",
    },
)
EXPECTED_RELATION_IDS = {
    "st-chp6-p147-bernini-replaced-as-leading-architect",
    "st-chp6-p147-rainaldi-characterized",
    "st-chp6-p147-rainaldi-plans-pamfili-palace",
    "st-chp6-p148-pamfili-palace-rainaldi-limitations",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第6章；印刷页147–148；OCR L22–27",
            "sentence_summary": "第6章称Girolamo Rainaldi是Innocent X时期接替Bernini的建筑师之一，并将Piazza Navona上的大宅规划归于他；第148页对宅邸的限制性评价保留为Haskell判断。",
            "original_quotes": [
                {"source_span": item["source_span"], "text": item["quote"]}
                for item in QUOTES
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "lines 22–27; print pp. 147–148",
            },
        }],
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第6章书内来源](../../../{SOURCE_FILE})"
    relation_lines = "\n".join(f"- `{sid}`" for sid in sorted(EXPECTED_RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** Haskell在第6章把 Girolamo Rainaldi 列为Innocent X时期接替Bernini、担任首席建筑师的两人之一，并称他规划了Piazza Navona上的家族大宅。第148页将该宅的某些限制归因于Rainaldi的年龄与能力，这是Haskell的评价，不作为独立事实。Treccani《意大利人传记辞典》所载Girolamo Rainaldi（Geronimo）为建筑师，且将Piazza Navona的Palazzo Pamphilj归于他；姓名、职业与建筑对象相合。中文名为工作音译。{source_link}

**English:** In Chapter 6 Haskell names Girolamo Rainaldi as one of two architects who replaced Bernini as leading architects under Innocent X, and says Rainaldi planned the family palace on Piazza Navona. On page 148 Haskell attributes limitations of the palace to Rainaldi’s age and limitations; this remains the author’s assessment. Treccani’s *Dizionario Biografico degli Italiani* identifies Girolamo Rainaldi (Geronimo) as an architect and also attributes the Palazzo Pamphilj on Piazza Navona to him, matching the name, profession, and building. The Chinese display name is a working transliteration. {source_link}

### 姓名与身份范围

- 书中全名：Girolamo Rainaldi。{source_link}
- 外文异名：Treccani DBI列作 Girolamo Rainaldi (Geronimo)。
- 中文显示名：“吉罗拉莫·拉伊纳尔迪”为工作音译，不声明为已核定通行译名。
- 身份边界：Girolamo与第7章另见的Carlo Rainaldi为不同人物；Treccani DBI记Carlo为Girolamo之子，两组不合并。

## 关系与证据

### 身份与外部链接

- Treccani《意大利人传记辞典》第86卷（2016）：[Rainaldi, Girolamo (Geronimo)]({TRECCANI_URL})。该记录用于核对建筑师身份及Piazza Navona的Palazzo Pamphilj；同条将Carlo记为其子。它不验证Haskell的年龄估计或建筑评价。

### 关系记录

当前没有新增正式关系。以下4条直接S2关系候选仍待S6逐条核对端点、语境与作者限定：

{relation_lines}
"""
    return f"---\n{fm}---\n\n{body}"


def next_alignment_id(rows) -> str:
    numbers = [int(row["alignment_id"].split("-", 1)[1]) for row in rows if row.get("alignment_id", "").startswith("aln-")]
    return f"aln-{max(numbers, default=0) + 1:04d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register and externally corroborate Girolamo Rainaldi's S4 person identity.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignments = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate = candidate_by_id[CANDIDATE_ID]
    alignment = candidate_alignments[CANDIDATE_ID]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Rainaldi, Girolamo"
    assert candidate.get("index_entry_id") == "Q-R.csv#20"
    assert alignment.get("decision") == "new" and sync.get_group(alignment.get("resolution_note", "")) == GROUP

    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_paths = {
        line[2:] for line in accepted.splitlines()
        if line.startswith("- 04-knowledge/units/")
    }
    manifest_targets = [row for row in manifest if row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL]
    external_rows = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE_ID and row.get("external_source") == TRECCANI_SOURCE
    ]
    assert len(manifest_targets) <= 1 and len(external_rows) <= 1
    registered = bool(manifest_targets) and alignment.get("ku_id") == KU_ID and CARD_REL in accepted_paths and card_path.exists() and bool(external_rows)
    if registered:
        assert len(manifest_targets) == 1 and external_rows[0].get("external_id") == TRECCANI_ID
        if card_path.read_text(encoding="utf-8-sig") != make_card():
            if args.dry_run:
                print(f"REGISTERED CARD UPDATE REQUIRED: {GROUP} -> {KU_ID}; identity link formatting changed; no files changed")
                return 0
            card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
            print(f"updated registered card formatting: {GROUP} -> {KU_ID}")
            return 0
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; Treccani DBI identity row present; 4 relation candidates remain non-formal.")
        return 0
    assert not manifest_targets and not alignment.get("ku_id") and not card_path.exists() and CARD_REL not in accepted_paths and not external_rows
    assert not any(
        row.get("type") == "person" and (row.get("name_en") or "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "Girolamo Rainaldi already exists as a person KU"

    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == {CANDIDATE_ID}, group_members
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == EXPECTED_RELATION_IDS, (direct_relations, EXPECTED_RELATION_IDS)
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for item in QUOTES:
        assert " ".join(item["quote"].split()) in source_text, item["source_span"]

    planned_alignment = [dict(row) for row in alignments]
    planned_candidate_alignments = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    target_alignment = planned_candidate_alignments[CANDIDATE_ID]
    target_alignment["ku_id"] = KU_ID
    target_alignment["resolution_note"] = target_alignment["resolution_note"].replace(
        "No external identity source was accessed; KU assignment remains for S4.",
        "At the initial S3 decision no external source was accessed; Treccani DBI later corroborated the identity and is recorded below.",
    )
    target_alignment["resolution_note"] += f" S4 registration applied: mapped {GROUP} to {KU_ID}."
    treccani_row = {
        "alignment_id": next_alignment_id(planned_alignment),
        "candidate_id": CANDIDATE_ID,
        "ku_id": KU_ID,
        "external_source": TRECCANI_SOURCE,
        "external_id": TRECCANI_ID,
        "decision": "same",
        "accessed_date": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{S3_ANCHOR}",
        "legacy_ku_id": "",
        "resolution_note": "Identity corroboration: Treccani DBI, vol. 86 (2016), article by Cristiano Marchegiani identifies Girolamo Rainaldi (Geronimo) as an architect and attributes Palazzo Pamphilj on Piazza Navona to him; name, role, and building match Haskell ch. 6 pp. 147–148. The same entry distinguishes Carlo as his son. Supports identity only, not Haskell's age estimate or evaluative statements.",
    }
    planned_alignment.append(treccani_row)
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{S3_ANCHOR}\"></a>\n\n"
        "### S3/S4 person：Girolamo Rainaldi 身份核对与登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（`{GROUP}`；索引Q-R.csv#20）登记为[Girolamo Rainaldi人物卡](../../../{CARD_REL})。"
        "原书第6章第147页将Girolamo Rainaldi列为Innocent X时期接替Bernini的建筑师之一，并把Piazza Navona上的家族大宅规划归于他；第148页的年龄与能力评价仍属Haskell判断。"
        f"外部身份对照：Cristiano Marchegiani, ‘Rainaldi, Girolamo (Geronimo),’ Treccani, *Dizionario Biografico degli Italiani*, vol. 86 (2016), {TRECCANI_URL}（访问日期2026-10-17）。该条确认为建筑师，并将Piazza Navona的Palazzo Pamphilj归于Girolamo，名称、职业和具体建筑与书内锚点相合；条目还记Carlo Rainaldi为Girolamo之子。因此第7章候选`cand-2092`（Carlo）保留独立`new-person:carlo-rainaldi-7ecc91cf92`身份组，不并入本组；该外部来源未验证Carlo候选所涉Louvre设计。"
        "Treccani身份记录已写入`alignment.csv`；4条直接书内关系候选仍待S6，不新增正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### person：Girolamo Rainaldi 跨候选身份组 S4 登记（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}` → [人物卡](../units/persons/girolamo-rainaldi.md)。Treccani DBI的Girolamo条目与原书的Piazza Navona宫殿规划锚点相合；Carlo Rainaldi为其子，仍保留为另一个S3人物组。4条直接S2关系候选待S6，未新增正式关系。\n\n"
        f"全书S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。"
    )
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    planned_accepted = "\n".join(accepted_lines[:insert_at] + [f"- {CARD_REL}"] + accepted_lines[insert_at:]) + "\n"

    if args.dry_run:
        print(f"S4 person dry-run passed: {GROUP} -> {KU_ID}")
        print(f"identity source=Treccani DBI vol.86; direct relation candidates={len(direct_relations)}; separate Carlo Rainaldi group preserved")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; external rows={sum(bool(row.get('external_source')) for row in alignments):,}->{sum(bool(row.get('external_source')) for row in planned_alignment):,}"
        )
        print("no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; Treccani DBI identity corroboration recorded; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
