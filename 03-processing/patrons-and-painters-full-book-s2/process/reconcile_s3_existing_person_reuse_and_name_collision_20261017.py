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
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S3-full-book-2026-10-17"
ANCHOR = "s3-person-reuse-and-name-collision-20261017"

REUSE = [
    {
        "candidates": ["cand-0092", "cand-0093"],
        "group": "new-person:ameyden-dirk-dccff413fe",
        "ku": "units/persons/ameyden",
        "rationale": (
            "The existing person KU is Dirk van Ameyden, and its sources already align the book's Dirk Ameyden name "
            "and A.csv#93/#94 index entries, including the Relatione subentry, with the same author. Chapters 1 and 4 "
            "name the author/person Ameyden; the Relatione document remains a separate archive KU, not part of this person mapping."
        ),
    },
    {
        "candidates": ["cand-2624"],
        "group": "new-person:domenico-gian-tiepolo-86ddd4979f",
        "ku": "units/persons/giandomenico-tiepolo",
        "rationale": (
            "The existing person KU is Giandomenico Tiepolo, son of Giambattista. The candidate's full form Gian Domenico "
            "and chapter 9's 'his son' anchor, together with later chapter mentions, identify the same person; this is distinct "
            "from the father Giambattista Tiepolo."
        ),
    },
]

KEEP_NEW = {
    "candidate": "cand-1524",
    "group": "new-person:carlo-ferdinando-mantua-of-66e2b330e3",
    "existing_ku": "units/persons/ferdinando-duke-of-mantua",
    "rationale": (
        "Keep this candidate in its current new person group. Its indexed and body forms identify Ferdinando Carlo Gonzaga, "
        "the last Duke of Mantua, with chapter 9/10 references to 1706 and his final years. The existing KU's chapter 7 p.175 "
        "subject is Marie de Medici's nephew Ferdinando, son of Vincenzo, active as duke in 1624; these are different people "
        "within the Gonzaga succession. The shared ducal style does not merge their identities."
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-adjudicate three cross-chapter person groups against existing KUs.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {r["candidate_id"]: r for r in candidates}
    manifest_by = {r["ku_id"]: r for r in manifest}
    planned = [dict(r) for r in alignments]
    by_candidate = {
        r["candidate_id"]: r
        for r in planned
        if r.get("candidate_id") and not r.get("external_source")
    }
    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before_totals = sync.build_type_table(before_stats)

    for target in REUSE:
        ku = target["ku"]
        assert ku in manifest_by and manifest_by[ku]["type"] == "person"
        card_path = ROOT / manifest_by[ku]["card_path"]
        assert card_path.is_file()
        card_text = read_text(card_path)
        for cid in target["candidates"]:
            assert cid in candidate_by and cid in by_candidate
            c, a = candidate_by[cid], by_candidate[cid]
            assert c["suggested_type"] == "person"
            assert a["decision"] == "new" and not a.get("ku_id")
            assert sync.get_group(a.get("resolution_note", "")) == target["group"]
        group_members = [
            r["candidate_id"]
            for r in alignments
            if r.get("candidate_id")
            and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == target["group"]
        ]
        assert group_members == target["candidates"]
        if target["ku"] == "units/persons/ameyden":
            assert "Dirk van Ameyden" in card_text and "Relatione della città di Roma 1642" in card_text
            assert (ROOT / "04-knowledge/units/archives/ameyden-relazione-1642.md").is_file()
        else:
            assert "Giandomenico Tiepolo" in card_text and "Giambattista Tiepolo" in card_text
        for cid in target["candidates"]:
            a = by_candidate[cid]
            prior_note = a.get("resolution_note", "")
            a["decision"] = "same"
            a["ku_id"] = ku
            a["process_ref"] = PROCESS_REF
            a["resolution_note"] = (
                f"Supersedes prior S3 new decision; prior_resolution_note={prior_note}; "
                f"S3 re-adjudication (2026-10-17): same as existing KU {ku}. {target['rationale']} "
                f"See process record anchor {ANCHOR}."
            )

    c = KEEP_NEW["candidate"]
    assert c in candidate_by and c in by_candidate
    candidate = candidate_by[c]
    alignment = by_candidate[c]
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == KEEP_NEW["group"]
    existing = manifest_by[KEEP_NEW["existing_ku"]]
    existing_card = read_text(ROOT / existing["card_path"])
    assert "1624" in existing_card and "Ferdinando Carlo Gonzaga" not in existing_card
    alignment["process_ref"] = PROCESS_REF
    alignment["resolution_note"] += (
        f" S3 name-collision review (2026-10-17): {KEEP_NEW['rationale']} "
        f"Existing comparison KU={KEEP_NEW['existing_ku']}; current group={KEEP_NEW['group']}."
    )

    after_stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, after_totals = sync.build_type_table(after_stats)
    assert after_totals["same_candidates"] == before_totals["same_candidates"] + 3
    assert after_totals["new_candidates"] == before_totals["new_candidates"] - 3
    assert after_totals["new_groups"] == before_totals["new_groups"] - 2
    assert after_totals["pending_groups"] == before_totals["pending_groups"] - 2
    assert after_totals["pending_members"] == before_totals["pending_members"] - 3

    process = read_text(PROCESS_PATH)
    result = sync.update_result(read_text(RESULT_PATH), after_stats, after_totals, len(manifest))
    assert f'<a id="{ANCHOR}"></a>' not in process
    process += (
        "\n\n"
        + f'<a id="{ANCHOR}"></a>'
        + "\n\n### S3 person：既有人物复用与同名爵位分界（2026-10-17）\n\n"
        "本批复核3个人物身份组：2组改为复用现有KU，另1组保留new并写明同名爵位下的人物区分。原new决定及理由保存在alignment.csv的resolution_note历史段。\n\n"
        "| 候选 | 原S3组 | 当前决定 | 身份去向 |\n|---|---|---|---|\n"
        "| `cand-0092`、`cand-0093` | `new-person:ameyden-dirk-dccff413fe` | `same` | `units/persons/ameyden`；Relatione文献卡保持独立archive类型 |\n"
        "| `cand-2624` | `new-person:domenico-gian-tiepolo-86ddd4979f` | `same` | `units/persons/giandomenico-tiepolo`；与父亲Giambattista分开 |\n"
        "| `cand-1524` | `new-person:carlo-ferdinando-mantua-of-66e2b330e3` | `new` | 保持独立；与较早的`units/persons/ferdinando-duke-of-mantua`不是同一人 |\n\n"
        "同名爵位比较依据为书内姓名与时间语境：既有KU的Ferdinando是Marie de Medici的侄子、Vincenzo之子，见第7章p.175；cand-1524是Ferdinando Carlo Gonzaga，索引页码p.267、312并对应第9、10章晚期Mantua语境。该组继续待S4登记。\n"
    )
    result += (
        "\n\n### S3 person：既有人物复用与同名爵位分界（2026-10-17）\n\n"
        "- `cand-0092`、`cand-0093` → `same`，复用 [Dirk van Ameyden](../units/persons/ameyden.md)；人物候选与《Relatione della città di Roma 1642》archive对象分开。\n"
        "- `cand-2624` → `same`，复用 [Giandomenico Tiepolo](../units/persons/giandomenico-tiepolo.md)。\n"
        "- `cand-1524` 维持 `new` 身份组；与已有的Ferdinando duke KU经时代和全名复核后保持分开，待S4。\n"
    )

    if args.dry_run:
        print("DRY-RUN OK: same mappings=3 across 2 identity groups; distinct same-title Ferdinando group retained as new")
        print(
            f"same candidates: {before_totals['same_candidates']:,}->{after_totals['same_candidates']:,}; "
            f"new groups: {before_totals['new_groups']:,}->{after_totals['new_groups']:,}; "
            f"pending S4 groups: {before_totals['pending_groups']:,}->{after_totals['pending_groups']:,}; "
            f"pending mappings: {before_totals['pending_members']:,}->{after_totals['pending_members']:,}"
        )
        for target in REUSE:
            print(f"{','.join(target['candidates'])} -> same {target['ku']}; group={target['group']}")
        print(f"{c} remains new {KEEP_NEW['group']}; distinct from {KEEP_NEW['existing_ku']}")
        return

    sync.write_csv(ALIGNMENT_PATH, align_fields, planned)
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result))
    print("APPLIED: three person candidates re-adjudicated; two groups now reuse existing KUs and one remains distinct/new")


if __name__ == "__main__":
    main()
