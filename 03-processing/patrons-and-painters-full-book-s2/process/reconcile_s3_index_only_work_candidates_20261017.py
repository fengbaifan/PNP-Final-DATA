from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S3-full-book-2026-10-17"
ANCHOR = "s3-index-only-work-crosscandidate-20261017"

TARGETS = [
    {
        "index_candidate": "cand-1238",
        "body_candidate": "cand-9154",
        "expected_group": "workgrp-d20da8ada884b0",
        "title": "Sacrifice of Iphigenia",
        "index_entry": "G.csv#148",
        "index_page": "297",
        "body_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "body_lines": (341, 342),
        "statement_id": "st-chp10-p297-guarana-iphigenia",
        "rationale": (
            "G.csv#148 is an index subentry under Giacomo Guarana and names Sacrifice of Iphigenia on p. 297. "
            "The same printed page's S2 statement names that painting, its artist, Moscow destination, and 1762 date. "
            "The index-only candidate therefore joins the existing S2 work identity group; it does not create a second work group."
        ),
    },
    {
        "index_candidate": "cand-1840",
        "body_candidate": "cand-7885",
        "expected_group": "workgrp-ec542d23614466",
        "title": "Madonna del Collo Lungo",
        "index_entry": "P.csv#40",
        "index_page": "222",
        "body_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "body_lines": (255, 255),
        "statement_id": "",
        "rationale": (
            "P.csv#40 is an index subentry under Parmigianino, Francesco and names the Madonna del Collo Lungo. "
            "S2 independently anchors the same full title, attributed to Parmigianino, in the body candidate cand-7885. "
            "The printed index locator is p. 222 while the body anchor is p. 232; the locator discrepancy is retained and not silently corrected. "
            "The exact title and creator identify one source-local work, so the index candidate joins the existing work group."
        ),
    },
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile index-only work candidates to exact S2 work anchors.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    _, mentions = sync.read_csv(MENTIONS_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    alignment_by = {
        r["candidate_id"]: r
        for r in alignments
        if r.get("candidate_id") and not r.get("external_source")
    }
    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }

    planned = [dict(r) for r in alignments]
    planned_by = {
        r["candidate_id"]: r
        for r in planned
        if r.get("candidate_id") and not r.get("external_source")
    }
    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)
    updates = []

    for target in TARGETS:
        index_id = target["index_candidate"]
        body_id = target["body_candidate"]
        assert index_id in candidate_by and body_id in candidate_by
        index_candidate = candidate_by[index_id]
        body_candidate = candidate_by[body_id]
        index_alignment = planned_by[index_id]
        body_alignment = planned_by[body_id]
        assert index_candidate["suggested_type"] == "work"
        assert body_candidate["suggested_type"] == "work"
        assert index_candidate["sub_entry"] == target["title"]
        assert index_candidate["index_entry_id"] == target["index_entry"]
        assert index_alignment["decision"] == "undecided"
        assert body_alignment["decision"] == "new"
        assert not body_alignment.get("ku_id")
        assert sync.get_group(body_alignment.get("resolution_note", "")) == target["expected_group"]
        assert target["title"].casefold() in (
            body_candidate["canonical_name"] + " " + body_candidate.get("detail", "")
        ).casefold()
        source_text = (ROOT / target["body_file"]).read_text(encoding="utf-8-sig")
        start, end = target["body_lines"]
        lines = source_text.splitlines()
        quote = "\n".join(lines[start - 1 : end])
        assert target["title"].casefold() in quote.casefold()
        assert target["statement_id"] in statements if target["statement_id"] else True
        if target["statement_id"]:
            statement = statements[target["statement_id"]]
            assert body_id in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
            assert target["title"].casefold() in statement.get("original_quote", "").casefold()
        else:
            assert any(
                m.get("candidate_id") == body_id and target["title"].casefold() in m.get("surface_form", "").casefold()
                for m in mentions
            )
        group_members = [
            r["candidate_id"]
            for r in planned
            if r.get("candidate_id")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == target["expected_group"]
        ]
        assert body_id in group_members
        assert index_id not in group_members
        index_alignment["decision"] = "new"
        index_alignment["process_ref"] = PROCESS_REF
        old_note = index_alignment.get("resolution_note", "")
        index_alignment["resolution_note"] = (
            f"Supersedes prior S3 undecided rationale: {old_note}; group={target['expected_group']}; "
            f"S3 cross-candidate identity decision (2026-10-17): {target['rationale']} "
            f"The candidate remains an index-derived mapping to the group's future single S4 KU; no KU is created by this decision."
        )
        updates.append((index_id, body_id, target["expected_group"], target["rationale"]))

    after_stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, after_totals = sync.build_type_table(after_stats)
    result = sync.update_result(read_text(RESULT_PATH), after_stats, after_totals, len(manifest))
    process = read_text(PROCESS_PATH)
    assert f'<a id="{ANCHOR}"></a>' not in process
    section = [
        "",
        "",
        f'<a id="{ANCHOR}"></a>',
        "",
        "### S3 work：索引子目与正文候选跨来源合组（2026-10-17）",
        "",
        "两条原为 `undecided` 的索引-only work 候选，现与已有正文锚点的候选合入同一新身份组。裁决依赖精确题名、创作者或索引层级以及原书正文锚点；不重复建组，也不因合组提前登记正式关系。",
        "",
        "| 索引候选 | 正文候选／身份组 | S3 去向 | 证据与保留项 |",
        "|---|---|---|---|",
    ]
    for index_id, body_id, group, rationale in updates:
        target = next(t for t in TARGETS if t["index_candidate"] == index_id)
        retained = "；索引页码与正文页码差异保留" if index_id == "cand-1840" else "；索引和正文均定位 p. 297"
        section.append(f"| {index_id} | {body_id} / `{group}` | `new`，同组单一未来 KU | {rationale}{retained} |")
    process += "\n".join(section) + "\n"
    result += (
        "\n\n### S3 work：索引子目与正文候选跨来源合组（2026-10-17）\n\n"
        "- `cand-1238` 与正文候选 `cand-9154` 合入 `workgrp-d20da8ada884b0`；G.csv#148 与第10章 p.297 的作品题名和定位一致。\n"
        "- `cand-1840` 与正文候选 `cand-7885` 合入 `workgrp-ec542d23614466`；题名和创作者一致，索引 p.222 与正文 p.232 的页码差异继续保留待核。\n"
        "- 两组均仍待 S4 登记；合组只确定来源内作品身份，不确认作者归属之外的事实或关系。\n"
    )

    assert len(updates) == 2
    assert after_totals["new_groups"] == before_totals["new_groups"]
    assert after_totals["pending_groups"] == before_totals["pending_groups"]
    assert after_totals["pending_members"] == before_totals["pending_members"] + len(updates)

    if args.dry_run:
        print(f"DRY-RUN OK: S3 candidates={len(updates)}; no KU files or manifest rows created")
        print(
            f"new groups: {before_totals.get('new_groups', 'n/a')}->{after_totals.get('new_groups', 'n/a')}; "
            f"pending S4 groups: {before_totals['pending_groups']:,}->{after_totals['pending_groups']:,}; "
            f"pending S4 mappings: {before_totals['pending_members']:,}->{after_totals['pending_members']:,}"
        )
        for index_id, body_id, group, rationale in updates:
            print(f"{index_id} -> {body_id}; group={group}; {rationale}")
        return

    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result))
    print("APPLIED: two index-only work candidates now share their exact S2 work groups; KU registration remains pending S4")


if __name__ == "__main__":
    main()
