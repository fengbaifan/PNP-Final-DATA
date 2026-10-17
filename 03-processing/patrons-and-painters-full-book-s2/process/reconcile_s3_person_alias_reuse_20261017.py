from __future__ import annotations

import argparse
import re
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PROCESS_REF = "S3-full-book-2026-10-17"
SLAM_SOURCE = "Saint Louis Art Museum"
SLAM_ID = "https://www.slam.org/collection/constituents/851/"
TARGETS = {
    "cand-2140": {
        "ku": "units/persons/ribera",
        "group": "sg3-ku-units-persons-ribera",
        "old_group": "new-person:giuseppe-ribera-e4beaa06d5",
        "comparison": (
            "The book index entry is Ribera, Giuseppe, and chapter 5 calls him the Spaniard Giuseppe Ribera "
            "while describing his work as a painter. The existing accepted person card is Jusepe de Ribera, "
            "with the book's plate-list artist entry Ribera. The Saint Louis Art Museum record names Jusepe "
            "de Ribera and explicitly lists Giuseppe de Ribera and lo Spagnoletto as alternate names; it "
            "describes him as Spanish (active Italy), c.1590–1652, and links to Getty ULAN and the Library "
            "of Congress Name Authority File. Together these support identity equivalence for S3 only; no "
            "external biographical facts are copied into the KU."
        ),
    },
    "cand-1066": {
        "ku": "units/persons/baldassare-franceschini",
        "group": "sg3-ku-units-persons-baldassare-franceschini",
        "old_group": "new-person:baldassare-franceschini-baldassare-frances-a60fbefa71",
        "comparison": (
            "The index and chapter 20 name Baldassare Franceschini and chapter 20 supplies the alias il "
            "Volterrano. The existing accepted person card is Baldassarre Franceschini, explicitly records "
            "Baldassare Franceschini as the original-book name form, and already records il Volterrano. "
            "These are the same full personal name and alias in this source context; no external identity "
            "source was needed."
        ),
    },
}


def keep_bom_bytes(path: Path, text: str) -> bytes:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    return bom + text.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-adjudicate two full-book person candidates as same as accepted person KUs."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by = {row["candidate_id"]: row for row in candidates}
    manifest_by = {row["ku_id"]: row for row in manifest}
    primary_by = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned = [dict(row) for row in alignments]
    planned_primary = {
        row["candidate_id"]: row
        for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }

    before_stats = sync.summarize_by_type(candidate_by.values(), alignments)
    _, before = sync.build_type_table(before_stats)
    external_source_name = SLAM_SOURCE
    assert not any(
        row.get("candidate_id") == "cand-2140" and row.get("external_source") == external_source_name
        for row in alignments
    ), "the Saint Louis Art Museum record is already linked for cand-2140"

    primary_group_ids = {
        row["alignment_id"] for row in alignments if row.get("alignment_id")
    }
    numeric_ids = [
        int(match.group(1))
        for row in alignments
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    ]
    external_alignment_id = f"aln-{max(numeric_ids, default=0) + 1:04d}"
    assert external_alignment_id not in primary_group_ids

    for cid, target in TARGETS.items():
        assert cid in candidate_by and candidate_by[cid].get("suggested_type") == "person"
        row = planned_primary[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == target["old_group"]
        assert target["ku"] in manifest_by
        existing_card = ROOT / manifest_by[target["ku"]]["card_path"]
        assert existing_card.exists()
        members = [
            item
            for item in alignments
            if item.get("candidate_id")
            and not item.get("external_source")
            and item.get("decision") == "same"
            and item.get("ku_id") == target["ku"]
        ]
        assert members, f"target KU has no existing same decision: {target['ku']}"
        original_note = row.get("resolution_note", "")
        prior_group = sync.get_group(original_note)
        archived_note = original_note.replace(
            f"group={prior_group}", f"superseded_identity_token:{prior_group}", 1
        )
        assert "group=" not in archived_note
        row["decision"] = "same"
        row["ku_id"] = target["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"Supersedes prior S3 new decision; prior_resolution_note={archived_note}; "
            f"S3 re-adjudication ({DATE}): same as existing KU {target['ku']}. "
            f"{target['comparison']} See process record anchor s3-person-alias-reuse-20261017; "
            f"current identity group={target['group']};"
        )
        assert sync.get_group(row["resolution_note"]) == target["group"]

    external_row = {field: "" for field in alignment_fields}
    external_row.update(
        {
            "alignment_id": external_alignment_id,
            "candidate_id": "cand-2140",
            "ku_id": TARGETS["cand-2140"]["ku"],
            "external_source": SLAM_SOURCE,
            "external_id": SLAM_ID,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": PROCESS_REF,
            "resolution_note": (
                "Identity comparison only: Saint Louis Art Museum, Jusepe de Ribera, alternate names "
                "Giuseppe de Ribera and lo Spagnoletto. See process record anchor "
                "s3-person-alias-reuse-20261017. This record does not verify the other statements in the KU."
            ),
        }
    )
    planned.append(external_row)

    after_stats = sync.summarize_by_type(candidate_by.values(), planned)
    _, after = sync.build_type_table(after_stats)
    assert after["same_candidates"] == before["same_candidates"] + 2
    assert after["same_kus"] == before["same_kus"]
    assert after["new_candidates"] == before["new_candidates"] - 2
    assert after["new_groups"] == before["new_groups"] - 2
    assert after["pending_groups"] == before["pending_groups"] - 2
    assert after["pending_members"] == before["pending_members"] - 2
    assert after["registered_groups"] == before["registered_groups"]

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    anchor = '<a id="s3-person-alias-reuse-20261017"></a>'
    assert anchor not in process_text
    process_text += (
        "\n\n"
        + anchor
        + "\n\n### S3 person：Ribera 与 Baldassare Franceschini 的既有身份复用（2026-10-17）\n\n"
        "复核 S3 的两个 person new 决定时发现已登记人物卡中的姓名变体。两项均改判为 same 并指向原 KU；"
        "原 new 决定及组 token 保留在 alignment resolution_note 的 superseded 历史中，当前身份组改并入既有 same 组。"
        "此处理只裁决身份，不确认相关关系候选，也不把外部来源内容写入人物卡。\n\n"
        "| 候选 | 先前决定 | 当前决定 / KU | 身份比较与依据 |\n|---|---|---|---|\n"
        "| cand-2140 / Q-R.csv#67 | new | same / units/persons/ribera | Haskell第5章 p.120称“the Spaniard Giuseppe Ribera”，并以画家语境叙述；既有KU题名为Jusepe de Ribera，且承接同书图版目录Ribera条目。Saint Louis Art Museum 记录将 Giuseppe de Ribera 列为 Jusepe de Ribera 的异名，身份层面支持复用；其记录亦列 lo Spagnoletto、Spanish (active Italy)、约1590–1652，并链接Getty ULAN与美国国会图书馆规范档。访问日期2026-10-17；记录ID为 https://www.slam.org/collection/constituents/851/。|\n"
        "| cand-1066 / F.csv#81 | new | same / units/persons/baldassare-franceschini | 本书索引和第20章使用Baldassare Franceschini，并将其与il Volterrano并称；既有KU明确以Baldassarre Franceschini为规范名，同时在名称表记录原书形式Baldassare Franceschini及别名il Volterrano。复用既有KU，不需外部来源。|\n\n"
        f"主 S3 决策统计：same {before['same_candidates']:,}→{after['same_candidates']:,}；"
        f"new groups {before['new_groups']:,}→{after['new_groups']:,}；"
        f"S4 待登记组 {before['pending_groups']:,}→{after['pending_groups']:,}。"
        "Ribera 外部身份链接作为独立 alignment 行保存；不向 sources.csv 或 enrichment.jsonl 复制身份链接。\n"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        after_stats,
        after,
        len(manifest),
    )
    result_text += (
        "\n\n### S3 person：Ribera 与 Baldassare Franceschini 复用既有 KU（2026-10-17）\n\n"
        "- cand-2140：new 改为 same，映射至 [Jusepe de Ribera](../units/persons/ribera.md)。"
        " Saint Louis Art Museum 将 Giuseppe de Ribera 列为其异名；只用于身份比较，未补入外部传记事实。\n"
        "- cand-1066：new 改为 same，映射至 [Baldassarre Franceschini](../units/persons/baldassare-franceschini.md)。"
        " 既有卡已记录本书原拼 Baldassare Franceschini 及别名 il Volterrano。\n"
        "- 两项均不新增 KU；原 S3 决定与组 token 保留为可追溯历史。Ribera 外部身份记录见 alignment.csv 和过程记录。\n"
    )

    if args.dry_run:
        print(
            f"DRY-RUN OK: re-adjudicated={len(TARGETS)}; added external identity rows=1; "
            f"manifest remains={len(manifest):,}"
        )
        print(
            f"same candidates: {before['same_candidates']:,}->{after['same_candidates']:,}; "
            f"new groups: {before['new_groups']:,}->{after['new_groups']:,}; "
            f"pending groups: {before['pending_groups']:,}->{after['pending_groups']:,}; "
            f"pending mappings: {before['pending_members']:,}->{after['pending_members']:,}"
        )
        return

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_bytes(keep_bom_bytes(PROCESS_PATH, process_text))
    RESULT_PATH.write_bytes(keep_bom_bytes(RESULT_PATH, result_text))
    print(
        f"APPLIED: re-adjudicated={len(TARGETS)}; added external identity rows=1; "
        f"same candidates={after['same_candidates']:,}; pending groups={after['pending_groups']:,}"
    )


if __name__ == "__main__":
    main()
