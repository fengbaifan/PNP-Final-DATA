from __future__ import annotations

import argparse
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CANDIDATE = "cand-1935"
GROUP = "new-person:girolamo-paolo-piola-b16cf26a54"
KU_ID = "units/persons/paolo-girolamo-piola"
CARD_REL = "04-knowledge/units/persons/paolo-girolamo-piola.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile the full-book Piola candidate to its existing person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    row = next(row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    ku = [item for item in manifest if item.get("ku_id") == KU_ID]
    card_path = ROOT / CARD_REL
    card = card_path.read_text(encoding="utf-8-sig")
    ch1 = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md").read_text(encoding="utf-8-sig")
    index = (ROOT / "02-sources" / "02-Markdown" / "22_CHP-22Index.md").read_text(encoding="utf-8-sig")

    assert candidate["canonical_name"] == "Piola, Paolo Girolamo"
    assert candidate["suggested_type"] == "person"
    assert row["decision"] == "new" and not row.get("ku_id")
    assert sync.get_group(row.get("resolution_note", "")) == GROUP
    assert len(ku) == 1 and ku[0]["type"] == "person" and ku[0]["card_path"] == CARD_REL
    assert "Paolo Gerolamo Piola" in card
    assert "Paolo Girolamo Piola" in card
    assert "Piola, Paolo Girolamo, xvii, 8n, 10, 166n, 197" in index
    assert "Paolo Girolamo Piola" in ch1
    assert "when commissioning a work from the\nGenoese painter Paolo Girolamo Piola" in ch1
    assert "Paolo Girolamo Piola\n‘amante di sua libertà’" in ch1

    planned = [dict(item) for item in alignments]
    target = next(item for item in planned if item.get("candidate_id") == CANDIDATE and not item.get("external_source"))
    target["decision"] = "same"
    target["ku_id"] = KU_ID
    target["resolution_note"] += (
        " S3 review 2026-10-16: prior new group withdrawn and preserved as history; reuse existing KU because "
        "the existing card cites the same chapter 1 p. 8 and p. 10 source passages naming Paolo Girolamo Piola, "
        "and carries the same full-name index row P. G. Piola, xvii, 8n, 10, 166n, 197. "
        "The card documents Paolo Gerolamo/Girolamo as name forms; this is the same painter, not a new person. "
        f"Current S3 decision: same -> {KU_ID}."
    )
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidates)
    assert totals["same_candidates"] == 1782
    assert totals["new_candidates"] == 5018
    assert totals["new_groups"] == 4837
    assert totals["registered_groups"] == 335
    assert totals["pending_groups"] == 4502
    assert totals["pending_members"] == 4582
    result = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process += (
        "\n\n### S3 复核：Paolo Girolamo Piola 复用既有人物 KU（2026-10-16）\n\n"
        f"候选 `{CANDIDATE}` 原列为 `{GROUP}`／`new`。检查发现既有[Paolo Gerolamo Piola 人物卡]"
        "(../../../04-knowledge/units/persons/paolo-girolamo-piola.md) 已引同一书第1章 p.8 与 p.10 的同名原文，"
        "并记录同一索引行 `Piola, Paolo Girolamo, xvii, 8n, 10, 166n, 197`；旧卡明确保存 Gerolamo/Girolamo 名形。"
        f"因此将 `{CANDIDATE}` 从 `new` 改为 `same`，映射至 `{KU_ID}`；原组号、旧理由及撤回原因均保留在 alignment 行。"
        "不新增人物卡或 manifest 行，也未改关系；第1、6、7章的关系候选沿用该既有人物端点，开放端点仍待证。"
        f"更新后 S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])} KU）、"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result += (
        "\n\n### S3 复核：Piola 候选复用既有人物卡（2026-10-16）\n\n"
        f"`{CANDIDATE}` 原 S3 `new` 组经原书同章交叉核对后改为 `same`，复用"
        "[Paolo Gerolamo Piola 人物卡](../units/persons/paolo-girolamo-piola.md)。"
        "旧卡已引第1章 p.8、p.10 中本候选的全名原文，并记录相同索引行及 Gerolamo/Girolamo 名形；"
        "因此不另建人物 KU。旧组和旧理由留在 alignment 行作为历史。关系候选仍待 S6，原件或开放对象缺口未因此解除。"
        f"更新后 S3 same={sync.fmt(totals['same_candidates'])}/{sync.fmt(totals['same_kus'])} KU，"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组；"
        f"S4 待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )

    if args.dry_run:
        print(f"S3 Piola identity reconciliation dry-run passed: {CANDIDATE} -> same {KU_ID}")
        print("direct same-name evidence: chapter 1 pp. 8, 10; shared index row preserved on existing card")
        print(
            f"S4 registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest remains {sync.fmt(len(manifest))}; no files changed"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> same {KU_ID}; S4 pending="
        f"{sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest unchanged={sync.fmt(len(manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
