from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S3-gesu-and-santandrea-place-reconciliation-2026-10-16"
CASES = {
    "cand-4252": {
        "ku": "units/places/barberini-chapel-sant-andrea-valle",
        "group": "sg3-place-cand-4252",
        "quote": "He was now in a position to have a rich family chapel built for himself",
        "file": "02_CHP-2_sec_i.md",
        "why": "Chapter 2 states that Maffeo chose the S. Andrea della Valle site and had a family chapel built; the accepted place KU is the Barberini Chapel in that same church, named in the plate list as ‘Barberini Chapel in S. Andrea della Valle, Rome’. This is one internal architectural space, not the church itself.",
    },
    "cand-5200": {
        "ku": "units/places/gesu-rome",
        "group": "sg3-place-cand-5200",
        "quote": "the Gesù still looked essentially the same as it had done in 1589",
        "file": "03_CHP-3_sec_iv.md",
        "why": "Chapter 3 names the church whose appearance is compared; the accepted place KU is Gesù, Rome and already records this church building. The candidate is not a chapel, fresco, vault, or Jesuit institution.",
    },
}
OLD_CHAPEL_GROUP = "sg3-place-cand-5237"
KEEP_CHAPEL_GROUP = "sg3-place-cand-5300"
CHAPEL_MEMBERS = {"cand-5237", "cand-5300"}


def get_group(note):
    m = re.search(r"group=([^;| ]+)", note or "")
    return m.group(1) if m else ""


def main():
    parser = argparse.ArgumentParser(description="Correct Gesu/Sant'Andrea place identity alignments against accepted units.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    decisions = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert len(decisions) == len(candidate_by_id) == 12404
    manifest_by_id = {r["ku_id"]: r for r in manifest}
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")

    for cid, case in CASES.items():
        c, a, m = candidate_by_id[cid], decisions[cid], manifest_by_id[case["ku"]]
        assert c["suggested_type"] == "place" and a["decision"] == "new" and not a.get("ku_id")
        assert get_group(a["resolution_note"]) == case["group"]
        assert m["type"] == "place" and Path(m["card_path"]).exists() and m["card_path"] in accepted_text
        src = ROOT / "02-sources" / "02-Markdown" / case["file"]
        assert case["quote"] in src.read_text(encoding="utf-8-sig"), cid
        assert not any(r.get("type") == "place" and r.get("canonical_name") == c["canonical_name"] for r in manifest)

    chapel_groups = defaultdict(list)
    for row in decisions.values():
        if row.get("decision") == "new":
            chapel_groups[get_group(row["resolution_note"])].append(row["candidate_id"])
    assert sorted(chapel_groups[OLD_CHAPEL_GROUP]) == ["cand-5237"]
    assert sorted(chapel_groups[KEEP_CHAPEL_GROUP]) == ["cand-5300"]
    for cid in CHAPEL_MEMBERS:
        assert candidate_by_id[cid]["suggested_type"] == "place"
        src = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
        assert "chapels of St Ignatius and St Francis Xavier" in " ".join(src.read_text(encoding="utf-8-sig").split())
    chapel_source = " ".join((ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md").read_text(encoding="utf-8-sig").split())
    assert "The chapel, in the right transept was one of the only ones that long remained exclusively under Jesuit patronage." in chapel_source
    assert "On his canonisation in 1623 the chapel was dedicated to St Francis Xavier" in chapel_source

    planned = [dict(r) for r in alignments]
    by_id = {r["candidate_id"]: r for r in planned if r.get("candidate_id") and not r.get("external_source")}
    prior_notes = {}
    for cid, case in CASES.items():
        row = by_id[cid]
        prior_notes[cid] = row["resolution_note"]
        row["decision"] = "same"
        row["ku_id"] = case["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"matched_manifest={case['ku']}; matched_existing_card={manifest_by_id[case['ku']]['card_path']}; "
            f"source_ref={candidate_by_id[cid].get('candidate_source_ref','')}; Same: {case['why']} "
            f"Prior S3 new group id {case['group']} and its former rationale superseded: {prior_notes[cid]}"
        )

    old_note = by_id["cand-5237"]["resolution_note"]
    row5300 = by_id["cand-5300"]
    note5300 = row5300["resolution_note"]
    assert note5300.startswith(f"group={KEEP_CHAPEL_GROUP};")
    by_id["cand-5237"]["resolution_note"] = re.sub(
        rf"^group={re.escape(OLD_CHAPEL_GROUP)};",
        f"group={KEEP_CHAPEL_GROUP};",
        old_note,
        count=1,
    ) + (
        f" S3 identity correction: same physical right-transept chapel as cand-5300, whose dedication changed over time; "
        f"the former separate group id {OLD_CHAPEL_GROUP} is superseded. Prior rationale retained: {old_note}"
    )
    assert get_group(by_id["cand-5237"]["resolution_note"]) == KEEP_CHAPEL_GROUP
    by_id["cand-5237"]["process_ref"] = PROCESS_REF
    by_id["cand-5300"]["resolution_note"] += (
        " S3 cross-candidate identity review: cand-5237 names this same chapel as St Francis Xavier in the earlier Gaulli commission; "
        "the later passage identifies it as the right-transept chapel and records its successive dedications."
    )
    by_id["cand-5300"]["process_ref"] = PROCESS_REF

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(v[key] for v in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1759 and totals["new_candidates"] == 5007
    assert totals["new_groups"] == 4837
    assert totals["registered_groups"] == 231 and totals["registered_members"] == 289
    assert totals["pending_groups"] == 4606 and totals["pending_members"] == 4718
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    note = (
        "\n\n### S3 地点身份复核：复用 Gesù 与 Barberini Chapel，并合并 Gesù 圣方济各礼拜堂候选（2026-10-16）\n\n"
        "`cand-4252` 与既有 `units/places/barberini-chapel-sant-andrea-valle` 指同一谷地圣安德烈堂内部的 Barberini Chapel：第2章记 Maffeo 选择该教堂并为自己建造家族礼拜堂，图版目录以 ‘Barberini Chapel in S. Andrea della Valle, Rome’ 明名。现从 new 改为 same，保留旧组号及理由，不另建地点卡。"
        "`cand-5200` 指全书既有 `units/places/gesu-rome` 教堂建筑；第3章 p.82 的建筑外观比较与既有 KU 身份一致，故从 new 改为 same。该决定不把教堂与内部礼拜堂、拱顶绘画或修会合并。两条复用均经现有 manifest、accepted.yml 与卡片核对。\n\n"
        "另将 `cand-5237`（Gaulli 合约中的 Chapel of St Francis Xavier）与 `cand-5300`（同教堂右横翼、经历连续更名／改奉的礼拜堂）并入 `sg3-place-cand-5300`。第3章 p.80 列 Gaulli 合约范围中的 St Francis Xavier 礼拜堂；p.84 将右横翼礼拜堂的历次奉献对象及1623年改奉圣方济各·沙勿略记为同一空间。故这两行保持 new、共用一个新组；原独立组号在 `cand-5237` 注释中保留。`cand-5236` 的 St Ignatius 礼拜堂继续独立，且不与圣依纳爵堂 S. Ignazio 或教堂中的祭坛和绘画合并。\n\n"
        f"更正后 S3：same={sync.fmt(totals['same_candidates'])}、new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组）、conflict={sync.fmt(totals['conflict'])}、excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。未改既有 KU、manifest 或正式关系。"
    )
    process_text += note
    result_text += note

    if args.dry_run:
        print("S3 place reconciliation dry-run passed")
        print("reuse: cand-4252 -> units/places/barberini-chapel-sant-andrea-valle; cand-5200 -> units/places/gesu-rome")
        print("merge: cand-5237 + cand-5300 -> sg3-place-cand-5300; distinct: cand-5236 remains its own group")
        print(f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']} groups; S4 registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
        print("No files changed.")
        return 0

    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("S3 place reconciliation applied: two same mappings and one two-candidate new identity group")


if __name__ == "__main__":
    raise SystemExit(main())
