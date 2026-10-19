from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATE = "cand-7664"
GROUP = "workgrp-26c7ec57931fff"
KU_ID = "units/works/the-flood-canvas-liberi-bergamo"
CARD_REL = "04-knowledge/units/works/the-flood-canvas-liberi-bergamo.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "《洪水》画布"
NAME_EN = "The Flood canvas"
SOURCE_FILE = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 8, p. 217."
)
DIRECT_IDS = {
    "st-chp8-p217-flood-rejected",
    "st-chp8-p217-flood-repainted-placed",
    "st-chp8-p217-flood-arrives-after-seven-months",
    "st-chp8-p217-committee-rejects-flood",
    "st-chp8-p217-letter-demands-repaint-and-suspension",
    "st-chp8-p217-flood-repainted",
    "st-chp8-p217-flood-placed-south-door",
}
RELATION_IDS = {
    "st-chp8-p217-flood-arrives-after-seven-months",
    "st-chp8-p217-committee-rejects-flood",
    "st-chp8-p217-letter-demands-repaint-and-suspension",
    "st-chp8-p217-flood-repainted",
    "st-chp8-p217-flood-placed-south-door",
}
QUOTES = (
    ("lines 71–72; print p. 217", "his first canvas—The Flood—arrived in Bergamo."),
    ("line 72; print p. 217", "it was placed above the South door"),
)


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [{
            "citation": BOOK_CITATION,
            "location": "第8章，印刷页217，来源转录第71–72行",
            "sentence_summary": (
                "Haskell称1660年签订了为贝加莫 Santa Maria Maggiore 绘制16幅画的合同；"
                "七个月后 Pietro Liberi 的首幅画布《The Flood》抵达，委员会拒绝后要求重绘。"
                "Haskell称 Liberi 后来完成重绘，作品被安置在南门上方；“仍在那里”仅对应作者成书时的说法。"
            ),
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in QUOTES
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": "lines 71–72; print p. 217",
            },
        }],
        "created": "2026-10-20",
        "updated": "2026-10-20",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p217 = "[第8章 p.217](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L71–72）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 所称 Pietro Liberi 为贝加莫 Santa Maria Maggiore 绘制的首幅画布《The Flood》。原书称作品抵达后遭委员会拒绝，Liberi 按要求重绘，随后被安置在教堂南门上方。中文显示名是对 Haskell 英文称谓的描述性译名；原题、现代馆藏身份及当前存放状态未在本卡核实。{p217}

**English:** This unit records the first canvas Haskell calls *The Flood*, painted by Pietro Liberi for Santa Maria Maggiore in Bergamo. The account says that the committee rejected the canvas after its arrival; Liberi repainted it as requested, and it was then placed above the church’s south door. The Chinese display name is descriptive. The original title, present-day object identity, and current location have not been independently established here. {p217}

### 身份范围与书内记录

- **作品识别：** Haskell identifies this as Liberi’s first canvas in the church commission and names it *The Flood*. This descriptive unit does not assert a verified original title or an externally confirmed surviving painting. {p217}
- **委托语境：** The 1660 contract covered sixteen pictures for the church. Its total price and advance payment apply to the whole commission, not solely to this canvas. {p217}
- **拒绝与重绘：** Haskell reports that the committee rejected the canvas and demanded a satisfactory repainting. The letter is known here through Haskell’s quotation, not an independent inspection of the document. {p217}
- **安置报告：** Haskell says that after repainting, the work was placed above the south door and “still” was there at the time of his account. The passage supplies no exact installation date and does not establish the present location. {p217}
- **相关知识元：** 创作者候选见[Pietro Liberi 人物卡](../persons/pietro-liberi.md)；地点候选见[贝加莫圣母玛利亚教堂地点卡](../places/santa-maria-maggiore-bergamo.md)。两端均不因本卡登记而自动形成正式关系。

## 关系与证据

### 正式关系

本批未新增 formal 关系。五条以该作品为直接端点的 S2 关系候选仍待 S6 逐条裁决。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register Pietro Liberi's Flood canvas as an S4 work endpoint."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_had_bom = MANIFEST_PATH.read_bytes().startswith(b"\xef\xbb\xbf")
    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_rows = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(candidate_rows) == 1
    target = candidate_rows[0]
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "work"
    assert target["decision"] == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(
        row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL
        for row in manifest
    )
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "work"
        and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same-title work already exists in the manifest"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for _, quote in QUOTES:
        assert " ".join(quote.split()) in source_text, quote

    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE
        or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_ids = {row["statement_id"] for row in direct}
    relation_ids = {
        row["statement_id"] for row in direct
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert direct_ids == DIRECT_IDS, (direct_ids - DIRECT_IDS, DIRECT_IDS - direct_ids)
    assert relation_ids == RELATION_IDS, (relation_ids - RELATION_IDS, RELATION_IDS - relation_ids)

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
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {
        key: sum(item[key] for item in stats.values())
        for key in next(iter(stats.values()))
    }
    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(planned_manifest),
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4 work：Pietro Liberi《洪水》画布直接端点登记（2026-10-20）\n\n"
        f"{CANDIDATE} 沿用 S3 new 组 {GROUP}，登记至"
        f"[《洪水》画布知识卡](../../../{CARD_REL})。"
        "第8章 p.217 将其识别为 Liberi 在贝加莫 Santa Maria Maggiore 委托中的首幅画布；"
        "七个月后抵达、委员会拒绝及要求重绘、随后重绘并安置于南门上方均归于 Haskell 的叙述。"
        "合同的总价与预付款适用于16幅画，不分摊到本画；“仍在那里”限定为 Haskell 成书时的报告。"
        "该组仅含1个候选，来源为单章描述性识别；无外部身份核验。"
        f"7条直接 S2 statement 中5条关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；"
        "本批未改动 S2 statements/mentions，未新增 formal 关系或 S5 外部补足。"
        f"S4 已登记{result_sync.fmt(totals['registered_groups'])}组/"
        f"{result_sync.fmt(totals['registered_members'])}条映射，待登记"
        f"{result_sync.fmt(totals['pending_groups'])}组/"
        f"{result_sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text += (
        "\n\n### S4 work：Liberi《洪水》画布（2026-10-20）\n\n"
        f"{CANDIDATE} 映射至[《洪水》画布知识卡](../units/works/the-flood-canvas-liberi-bergamo.md)。"
        "作品边界限于 Haskell 所称 Liberi 为贝加莫 Santa Maria Maggiore 委托绘制的首幅画布；"
        "原题及当代实物身份未核实，成书时“仍在南门上方”的报告不表示当前状态。"
        "7条直接 S2 statement 中5条关系候选仍待 S6；无 formal 关系及外部补足。"
        f"当前 S4 为{result_sync.fmt(totals['registered_groups'])}组/"
        f"{result_sync.fmt(totals['registered_members'])}条已登记映射，"
        f"{result_sync.fmt(totals['pending_groups'])}组/"
        f"{result_sync.fmt(totals['pending_members'])}条映射待登记。"
    )

    if args.dry_run:
        print(f"S4 work dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members={len(group_rows)}; direct statements={len(direct)}; relation candidates={len(relation_ids)}")
        print("source quotes and page 217 location checked; the 16-work contract is not assigned solely to this canvas")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(
            f"registered={result_sync.fmt(totals['registered_groups'])}/"
            f"{result_sync.fmt(totals['registered_members'])}; pending="
            f"{result_sync.fmt(totals['pending_groups'])}/"
            f"{result_sync.fmt(totals['pending_members'])}"
        )
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8", newline="\n")
    result_sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    if not manifest_had_bom:
        manifest_bytes = MANIFEST_PATH.read_bytes()
        if manifest_bytes.startswith(b"\xef\xbb\xbf"):
            MANIFEST_PATH.write_bytes(manifest_bytes[3:])
    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (
            i for i, line in enumerate(accepted_lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text(
        "\n".join(accepted_lines) + "\n",
        encoding="utf-8-sig",
        newline="\n",
    )
    PROCESS_PATH.write_text((process_text + process_note).rstrip() + "\n", encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={result_sync.fmt(totals['registered_groups'])}/"
        f"{result_sync.fmt(totals['registered_members'])}; pending="
        f"{result_sync.fmt(totals['pending_groups'])}/"
        f"{result_sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
