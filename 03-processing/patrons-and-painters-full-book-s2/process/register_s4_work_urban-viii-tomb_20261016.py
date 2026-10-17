from __future__ import annotations

import argparse
import csv
import json
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

CANDIDATE = "cand-4512"
GROUP = "workgrp-aa9759b87aa39d"
KU_ID = "units/works/tomb-of-urban-viii-st-peters"
CARD_REL = "04-knowledge/units/works/tomb-of-urban-viii-st-peters.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "乌尔班八世墓葬纪念碑"
NAME_EN = "Tomb of Urban VIII at St Peter’s Basilica"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "location": "第2章；印刷页41；OCR L125",
        "summary": "第2章称 Urban VIII 于1627年下令建造自己的墓葬纪念碑，原计划在其生前完成并显著安置于圣彼得大殿；Bernini 受托，早期工程包括在后殿一侧建壁龛。",
        "quotes": (
            ("lines 125", "Urban VIII’s greatest commission to record his own glory was that for his tomb which he ordered in 1627 after only three years on the throne."),
            ("lines 125", "It was to be built in his own lifetime and prominently placed in St Peter’s."),
            ("lines 125", "Bernini was, of course, entrusted with the work"),
            ("lines 125", "The work began quickly; a niche was built On the right of the apse"),
        ),
        "span": "lines 125; print p. 41",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    },
    {
        "location": "第2章；印刷页42；OCR L128–130",
        "summary": "第2章记载青铜教宗像铸成后工程停滞八年、1639年复工，随后制作 Charity 与 Death；1644年 Urban VIII 最后尝试赶在生前完工未成，Justice 于1647年完成。1647年是 Justice 的完成时间，不是整座墓葬的完成日期。",
        "quotes": (
            ("lines 128", "Soon afterwards the gigantic bronze figure of the blessing Pope was cast."),
            ("lines 128–129", "There for eight years the tomb rested while Urban VIII overwhelmed Bernini with commissions designed to satisfy his more immediate ambitions. In 1639 work was resumed."),
            ("lines 129", "The suave and attractive marble Charity accompanied by two putti was carved, followed by the grim, skeletal Death emerging from the sarcophagus"),
            ("lines 129–130", "in May 1644 the now dying Pope, who carefully examined all these projects, made a final attempt to get the tomb finished in time. It was too late, and Justice was only completed in 1647"),
        ),
        "span": "lines 128–130; print p. 42",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    },
    {
        "location": "第2章；印刷页59；OCR L13–14",
        "summary": "第2章后文称 Bernini 最终完成了 Urban VIII 生前希望看到完成的墓葬纪念碑；未给出完工日期。",
        "quotes": (
            ("lines 13–14", "Bernini at last completed the tomb that Urban VIII had so wished to see during his lifetime, and Angelo Giori, who was in charge, wrote to the exiled Cardinals and suggested that they should congratulate the artist."),
        ),
        "span": "lines 13–14; print p. 59",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
    },
)


def make_card():
    sources = []
    for item in SOURCES:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p41 = "[第2章 p.41](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L125）"
    p42 = "[第2章 p.42](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L128–130）"
    p59 = "[第2章 p.59](../../../02-sources/02-Markdown/02_CHP-2_sec_vii.md)（L13–14）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录位于圣彼得大殿的教宗 Urban VIII 墓葬纪念碑。哈斯克尔称 Urban VIII 于1627年下令建造，原计划在其生前完成并显著安置于大殿；工程经历多次停顿，后由 Bernini 完成。原书称 Justice 雕像于1647年完成，但没有把这一部件日期作为整座墓葬的完工日期；后文称 Bernini 最终完成了 Urban VIII 生前希望看到完成的纪念碑，却未标具体完工年。中文题名为描述性工作译名。{p41} {p42} {p59}

**English:** This unit records the funerary monument to Urban VIII at St Peter’s Basilica. Haskell says Urban ordered it in 1627 and intended it to be completed during his lifetime and prominently placed in the church; construction was interrupted several times before Bernini completed it. The book dates the completion of the Justice sculpture to 1647, but does not use that component date as the completion date of the whole tomb. A later passage says Bernini eventually completed the monument Urban had wished to see in his lifetime, without giving a calendar date. The Chinese title is descriptive. {p41} {p42} {p59}

### 委托与建造进程

- 下令：1627年，Urban VIII 下令建造自己的墓葬纪念碑。哈斯克尔称其为记录教宗自身荣耀的重要委托；该评价及动机归于作者。{p41}
- 原定安排：墓葬原计划在 Urban VIII 生前建成，并显著安置于圣彼得大殿；这是原计划，不是其生前完成的证明。{p41}
- 早期工程：Bernini 受托；工程迅速开始，在后殿右侧建造壁龛；随后铸成祝福姿态的巨型青铜教宗像。{p41} {p42}
- 停工与复工：墓葬停滞八年，1639年复工。复工后雕成大理石 Charity 与两个 putti，并制作从石棺出现的 Death 雕像。{p42}
- 1644年：Urban VIII 临终前检查各项工程并最后尝试在生前完成墓葬；Haskell称未能赶上。{p42}
- 1647年：Justice 雕像在该年完成；该日期仅指此组成部分。{p42}
- 整体完成：哈斯克尔后文称 Bernini 最终完成整座墓葬；所引段落没有给出具体完工日期。{p59}
- 地点：圣彼得大殿（地点实体另见[圣彼得大殿地点卡](../places/st-peters-basilica.md)）。墓葬纪念碑是 work，不与建筑地点合并。{p41}

## 关系与证据

### 关系记录

当前没有已登记的正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main():
    parser = argparse.ArgumentParser(description="Register Urban VIII's tomb monument as a work in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE].get("suggested_type") == "work"
    target = decisions[CANDIDATE]
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
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "work"
        and "urban viii" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
        and "tomb" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
        for row in manifest
    ), "same-object Urban VIII tomb work already exists in manifest"

    for item in SOURCES:
        source_text = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        for span, quote in item["quotes"]:
            assert " ".join(quote.split()) in source_text, (item["location"], span, quote)

    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 14 and len(direct_relations) == 12
    assert any(x.get("statement_id") == "st-chp2-secii-l127-139-urban-tomb-justice-completed" for x in direct)
    assert any(x.get("statement_id") == "st-chp2-secvii-l5-19-bernini-completes-urban-tomb" for x in direct)

    planned_alignment = [dict(row) for row in alignments]
    mapped = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4 work：Urban VIII 墓葬纪念碑跨章登记（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）映射至[乌尔班八世墓葬纪念碑作品卡](../../../04-knowledge/units/works/tomb-of-urban-viii-st-peters.md)。"
        "第2章 p.41 记1627年下令、Bernini受托、原定生前完成及显著安置；p.42记录早期青铜教宗像、停工八年、1639年复工、1644年未能赶上生前完工及 Justice 于1647年完成。"
        "p.59 后文称 Bernini 最终完成整座墓葬，但没有具体日期。Justice 的1647年仅为部件完成日期，不推作全墓完工年；原计划亦不写成 Urban 生前已经完成。"
        "14条直接 S2 陈述中12条关系候选留待 S6；未新增正式关系或 S5 补足。"
        f"S4 累计登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### work：乌尔班八世墓葬纪念碑 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[乌尔班八世墓葬纪念碑作品卡](../units/works/tomb-of-urban-viii-st-peters.md)。"
        "卡片区分1627年委托、1639年复工、1644年最后但未成功的生前完工尝试、Justice 于1647年完成，以及原书后文所述 Bernini 最终完成整座墓葬但未注明日期。"
        "14条直接 S2 陈述中12条关系候选留待 S6；本轮未新增正式关系或 S5 补足。"
        f"全书 S4 当前登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 work dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members={len(group_rows)}; direct statements={len(direct)}; relation candidates={len(direct_relations)}")
        print("cross-chapter p.41/p.42/p.59 quotations checked; Justice date kept separate from whole-tomb completion")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    result_sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; "
        f"pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
