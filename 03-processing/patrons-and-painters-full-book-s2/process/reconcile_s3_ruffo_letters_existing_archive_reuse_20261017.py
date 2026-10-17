from __future__ import annotations

import argparse
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

ITEMS = (
    {
        "candidate_id": "cand-3550",
        "group": "archive-group-f35a1e15e21c",
        "ku_id": "units/archives/novetti-ruffo-letter-1670",
        "card_rel": "04-knowledge/units/archives/novetti-ruffo-letter-1670.md",
        "candidate_name": "Letter from Francesco Novetti to Don Antonio Ruffo (1670)",
        "source_ref": "chp-1:01_CHP-1_sec_ii:l168-239#L753",
        "statement_ids": {
            "st-chp1-secii-p18-n5-novetti-letter-authored-by",
            "st-chp1-secii-p18-n5-novetti-letter-addressed-to",
        },
        "anchor": "s3-existing-novetti-ruffo-letter-1670-reuse-20261017",
        "print_locator": "print p. 18, note 5",
        "quote": "See letter from Francesco Novetti to Don Antonio Ruffo, dated 22 March 1670",
        "card_quote": "Letter from Francesco Novetti to Antonio Ruffo (1670-03-22)",
        "why": (
            "the same Chapter 1 note identifies the letter from Francesco Novetti to Don Antonio Ruffo dated "
            "22 March 1670 and cites V. Russo, p. 290; the existing archive card records these same correspondents, "
            "exact date, and citation"
        ),
        "result_name": "Novetti–Ruffo 1670年书信",
    },
    {
        "candidate_id": "cand-3552",
        "group": "archive-group-82845893d285",
        "ku_id": "units/archives/de-rosis-ruffo-letter-1663",
        "card_rel": "04-knowledge/units/archives/de-rosis-ruffo-letter-1663.md",
        "candidate_name": "Letter from Giuseppe de Rosis to Don Antonio Ruffo (1663)",
        "source_ref": "chp-1:01_CHP-1_sec_ii:l168-239#L971",
        "statement_ids": {
            "st-chp1-secii-l971-n1-derosis-letter-authored-by",
            "st-chp1-secii-l971-n1-derosis-letter-addressed-to",
        },
        "anchor": "s3-existing-de-rosis-ruffo-letter-1663-09-22-reuse-20261017",
        "print_locator": "print p. 23, note 1",
        "quote": "Letter from Giuseppe de Rosis to Don. Antonio Ruffo, dated 22 September 1663",
        "card_quote": "Letter from Giuseppe de Rosis to Antonio Ruffo (1663-09-22)",
        "why": (
            "the same Chapter 1 note identifies the letter from Giuseppe de Rosis to Don Antonio Ruffo dated "
            "22 September 1663 and cites V. Ruffo, p. 172; the existing September archive card records that exact "
            "date and citation, while the distinct 2 June 1663 letter remains a separate KU"
        ),
        "result_name": "de Rosis–Ruffo 1663年9月22日书信",
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reuse two existing archive KUs for exact full-book letter citations.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest = sync.read_csv(ROOT / "04-knowledge" / "tables" / "ku-manifest.csv")[1]
    statements = sync.load_statements()

    for item in ITEMS:
        cid = item["candidate_id"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "archive"
        assert candidate.get("canonical_name") == item["candidate_name"]
        assert candidate.get("candidate_source_ref") == item["source_ref"]
        assert sync.get_group(alignment.get("resolution_note", "")) == item["group"]
        matches = [row for row in manifest if row.get("ku_id") == item["ku_id"]]
        assert len(matches) == 1 and matches[0].get("card_path") == item["card_rel"]
        assert matches[0].get("type") == "archive"
        card = (ROOT / item["card_rel"]).read_text(encoding="utf-8-sig")
        assert item["card_quote"] in card
        actual_statements = {
            row["statement_id"] for row in statements
            if (row.get("subject_candidate_id") == cid or row.get("object_candidate_id") == cid)
            and (row.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert actual_statements == item["statement_ids"], actual_statements
        if alignment.get("decision") == "same" and alignment.get("ku_id") == item["ku_id"]:
            continue
        assert alignment.get("decision") == "new" and not alignment.get("ku_id"), alignment

        group_members = {
            row["candidate_id"]
            for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        source_full = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md").read_text(encoding="utf-8-sig")
        source_section = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md").read_text(encoding="utf-8-sig")
        assert item["quote"] in source_full and item["quote"] in source_section

    if all(alignment_by_id[item["candidate_id"]].get("decision") == "same" for item in ITEMS):
        print("ALREADY ALIGNED: both candidates reuse their date-matched existing archive KUs; 4 S2 relation candidates unchanged.")
        return 0

    planned_alignment = [dict(row) for row in alignments]
    for item in ITEMS:
        target = next(
            row for row in planned_alignment
            if row.get("candidate_id") == item["candidate_id"] and not row.get("external_source")
        )
        target["decision"] = "same"
        target["ku_id"] = item["ku_id"]
        target["resolution_note"] = (
            f"source_ref=candidate_ref={item['source_ref']}; statements={','.join(sorted(item['statement_ids']))}; "
            f"group={item['group']}; S3 reuse adjudication: same -> {item['ku_id']}. {item['why']}. "
            "Internal source/card comparison; no external correspondence content or manuscript consultation is inferred."
        )
        target["process_ref"] = f"S3-full-book-2026-10-17#{item['anchor']}"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3 archive：Ruffo 通信组既有书信复用裁决（2026-10-17）\n\n"
        + "\n".join(
            f"<a id=\"{item['anchor']}\"></a>\n- `{item['candidate_id']}`（{item['source_ref']}）"
            f"由`new`改判`same`，映射到既有[{item['ku_id']}](../../../{item['card_rel']})；"
            f"{item['why']}。书内书信关系候选原ID保留待S6，未新增正式关系。"
            for item in ITEMS
        )
        + "\n\n"
        + f"当前 S3：same={sync.fmt(totals['same_candidates'])}候选/{sync.fmt(totals['same_kus'])} KU；"
        + f"new={sync.fmt(totals['new_candidates'])}候选/{sync.fmt(totals['new_groups'])}组；"
        + f"conflict={sync.fmt(totals['conflict'])}；excluded={sync.fmt(totals['excluded'])}；"
        + f"undecided={sync.fmt(totals['undecided'])}。S4已登记{sync.fmt(totals['registered_groups'])}组，"
        + f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )
    result_text += (
        "\n\n### S3 archive：Ruffo 通信既有身份复用（2026-10-17）\n\n"
        + "\n".join(
            f"- `{item['candidate_id']}` → [既有书信卡](../units/archives/{Path(item['card_rel']).name})；"
            f"{item['result_name']}的寄件人、收件人、精确日期与书内刊引相合。"
            for item in ITEMS
        )
        + "\n原书4条关系候选保持待S6，未新增KU或正式关系。"
    )

    if args.dry_run:
        print("S3 existing archive reuse dry-run passed")
        for item in ITEMS:
            print(f"  {item['candidate_id']} new -> same -> {item['ku_id']}")
        print(f"new_groups={totals['new_groups']:,}; same_candidates={totals['same_candidates']:,}; relation_candidates=4")
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: candidates=2; new -> same; existing archive KUs reused; 4 relation candidates unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
