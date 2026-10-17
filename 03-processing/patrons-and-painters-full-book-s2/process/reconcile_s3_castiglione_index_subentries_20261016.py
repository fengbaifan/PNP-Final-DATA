from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
GROUP = "new-person:benedetto-castiglione-giovanni-c3cfd274af"
MAIN = "cand-0602"
PROCESS_REF = "S3-Castiglione-subentry-evidence-2026-10-16"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s3-castiglione-subentries-20261016"

TARGETS = {
    "cand-0603": {
        "index_entry": "C.csv#127",
        "sub_entry": "drawings in Sagredo collection",
        "pages": "266",
        "mention": "m-chp9-p266-castiglione",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "quote": "his magnificent set of drawings, the finest in existence, by the Genoese artist Giovanni Benedetto Castiglione",
        "rationale": (
            "The p. 266 prose names Giovanni Benedetto Castiglione while describing Sagredo's magnificent set of drawings; "
            "this directly anchors the subentry 'drawings in Sagredo collection' to the main person candidate."
        ),
    },
    "cand-0604": {
        "index_entry": "C.csv#128",
        "sub_entry": "importance of for 18th century",
        "pages": "266, 267",
        "mention": "m-chp9-p266-castiglione",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "quote": "of very much greater importance for the future of",
        "rationale": (
            "The p. 266-267 account of Castiglione's prints and drawings explicitly connects their later reception "
            "with Venetian eighteenth-century taste; this anchors the index subentry to the same named artist."
        ),
    },
    "cand-0605": {
        "index_entry": "C.csv#129",
        "sub_entry": "print of Diogenes",
        "pages": "124n",
        "mention": "m-chp5-p124-0011",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "quote": "the suggestion that his outlook on the world was not wholly conformist comes from Castiglione’s print of Diogenes",
        "rationale": (
            "The p. 124 paragraph names Castiglione as the artist whose publisher dedicated a print of Diogenes to Simonelli, "
            "and its note identifies the same object as 'Castiglione's print of Diogenes'; this anchors the subentry to the same person."
        ),
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve Castiglione's evidence-anchored index subentries into the existing source-local person group."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    ]
    alignment_by_id = {row["candidate_id"]: row for row in decision_rows}

    main_candidate = candidate_by_id[MAIN]
    main_alignment = alignment_by_id[MAIN]
    assert main_candidate["suggested_type"] == "person"
    assert main_candidate["canonical_name"] == "Castiglione, Giovanni Benedetto"
    assert main_candidate["index_entry_id"] == "C.csv#126"
    assert main_alignment["decision"] == "new" and not main_alignment.get("ku_id")
    assert sync.get_group(main_alignment["resolution_note"]) == GROUP
    group_rows = [
        row for row in decision_rows
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [MAIN]

    for cid, spec in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == main_candidate["canonical_name"]
        assert candidate["index_entry_id"] == spec["index_entry"]
        assert candidate["sub_entry"] == spec["sub_entry"]
        assert candidate["index_page_range"] == spec["pages"]
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "no mapped S2 mention/body source_ref" in alignment["resolution_note"]
        source = ROOT / spec["source_file"]
        normalized = " ".join(source.read_text(encoding="utf-8-sig").casefold().split())
        quote = " ".join(spec["quote"].casefold().split())
        assert quote in normalized, (cid, spec["quote"])

    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "C.csv")
    expected_index_rows = {
        "C.csv#126": ("", "114, 124, 207, 267, 309, 312, 341, 343, 350, 354"),
        "C.csv#127": ("drawings in Sagredo collection", "266"),
        "C.csv#128": ("importance of for 18th century", "266, 267"),
        "C.csv#129": ("print of Diogenes", "124n"),
    }
    for entry, (subentry, pages) in expected_index_rows.items():
        row = index_rows[int(entry.split("#")[1])]
        assert row["Main Entry"] == main_candidate["canonical_name"]
        assert row["Sub-entry"] == subentry and row["Page Numbers"] == pages

    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid, spec in TARGETS.items():
        row = planned_by_id[cid]
        old_note = row["resolution_note"]
        row["decision"] = "new"
        row["ku_id"] = ""
        row["accessed_date"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref=candidate={cid};index_entry={spec['index_entry']};index_pages={spec['pages']};"
            f"sub_entry={spec['sub_entry']};body_group_anchor={MAIN};body_anchor_mention={spec['mention']}@"
            f"{spec['source_file']};group={GROUP}; New: {spec['rationale']} "
            "The full personal name is stated in the indexed person entry and directly in the book's p. 266 prose; "
            "the page-specific subentry describes the same person, not a second person or a work. "
            f"Prior S3 decision and rationale retained: {old_note}"
        )

    planned_decisions = [
        row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    ]
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["new_candidates"] == 5008, totals
    assert totals["new_groups"] == 4835, totals
    assert totals["undecided"] == 5528, totals
    assert totals["pending_groups"] == 4567 and totals["pending_members"] == 4674, totals
    assert len(manifest) == 1287

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S3 re-review: Castiglione index subentries (2026-10-16)"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {MAIN} 是人物身份组 {GROUP} 的主项候选。复核 {TARGETS['cand-0603']['index_entry']}、"
        f"{TARGETS['cand-0604']['index_entry']}、{TARGETS['cand-0605']['index_entry']}：三者均与主项同为 "
        "Castiglione, Giovanni Benedetto，分别为“drawings in Sagredo collection”“importance of for 18th century”"
        "和“print of Diogenes”子项。原始待决理由是没有映射 S2 正文锚点；本次逐页回查解除该缺口。\n"
        "- 第9章 p.266 L309 明称 “the Genoese artist Giovanni Benedetto Castiglione”，并在同段讲述 "
        "Sagredo 的 Castiglione 素描；p.266-267 L309–316 直接对应素描集及其对十八世纪威尼斯趣味的影响，"
        "支撑 cand-0603 与 cand-0604 并入主项。第5章 p.124 L38–39 写 Castiglione 的出版者为 Simonelli 献上 Diogenes 版画，"
        "脚注 p.124n L47–49 又明确称 “Castiglione's print of Diogenes”，支撑 cand-0605 并入同一画家。"
        "cand-0602 已有对应 S2 mention / statement 锚点；这里只把索引子项映射到该同一来源人物，不新造 S2 事实或正式关系。\n"
        f"- 将 cand-0603、cand-0604、cand-0605 从 undecided 改为 new，统一并入 {GROUP}；原决定和理由保存在各自 "
        "alignment resolution_note 中。S3 new 候选增加3，身份组数不变；undecided 减少3。没有外部身份源、KU 登记或 S6 关系裁决。\n\n"
        f"S3 same={sync.fmt(totals['same_candidates'])}/{sync.fmt(totals['same_kus'])}; "
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}; "
        f"undecided={sync.fmt(totals['undecided'])}. S4 registered="
        f"{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending="
        f"{sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}.\n"
    )
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )

    targets = [ALIGNMENT, KNOWLEDGE, RESULT]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in targets)
    if args.dry_run:
        print(
            "dry-run passed: cand-0603/0604/0605 undecided->new in Castiglione person group; "
            "all three body anchors verified; prior reasons retained; "
            f"S3 new={totals['new_candidates']}/{totals['new_groups']} undecided={totals['undecided']}; "
            f"S4 pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}"
        )
        return 0

    shutil.copy2(ALIGNMENT, ALIGNMENT.with_name(ALIGNMENT.name + BACKUP_SUFFIX))
    shutil.copy2(KNOWLEDGE, KNOWLEDGE.with_name(KNOWLEDGE.name + BACKUP_SUFFIX))
    shutil.copy2(RESULT, RESULT.with_name(RESULT.name + BACKUP_SUFFIX))
    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    KNOWLEDGE.write_text(next_knowledge, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        "applied: cand-0603/0604/0605 -> new-person:benedetto-castiglione-giovanni-c3cfd274af; "
        f"new={totals['new_candidates']}/{totals['new_groups']} undecided={totals['undecided']}; "
        "S4 remains pending for this group"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
