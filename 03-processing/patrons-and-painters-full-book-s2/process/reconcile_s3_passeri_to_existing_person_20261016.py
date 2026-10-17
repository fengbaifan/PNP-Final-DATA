from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-16"

CANDIDATE = "cand-1856"
GROUP = "new-person:giambattista-passeri-110a86b546"
SAME_KU = "units/persons/giambattista-passeri"
CARD_REL = "04-knowledge/units/persons/giambattista-passeri.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/P.csv"
CH1_SOURCE = "02-sources/02-Markdown/01_CHP-1.md"
FULLBOOK_SOURCE = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
NEW_PROCESS_REF = "S3-S4-follow-up-2026-10-16-passeri-reuse"
BACKUP_SUFFIX = ".bak-s3-passeri-reuse-20261016"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the full-book Giambattista Passeri candidate to the existing Passeri person KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate = candidate_by_id[CANDIDATE]
    current = decisions[CANDIDATE]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Passeri, Giambattista"
    assert candidate.get("index_entry_id") == "P.csv#56"
    assert current.get("decision") == "new" and not current.get("ku_id")
    assert sync.get_group(current.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]

    manifest_row = next(
        (row for row in manifest if row.get("ku_id") == SAME_KU),
        None,
    )
    assert manifest_row is not None
    assert manifest_row.get("card_path") == CARD_REL
    assert manifest_row.get("type") == "person"
    card = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    assert "Giovanni Battista Passeri" in card
    assert "Giambattista Passeri" in card
    assert "常用名／本章名形 | Giambattista Passeri" in card

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert '"Passeri, Giambattista"' in index_text
    chapter1 = (ROOT / CH1_SOURCE).read_text(encoding="utf-8-sig")
    fullbook = (ROOT / FULLBOOK_SOURCE).read_text(encoding="utf-8-sig")
    assert "art-chronicler Giambattista Passeri" in chapter1
    assert "critic Giambattista Passeri" in fullbook

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert "S3 re-review: Passeri reuse" not in knowledge_text
    note = current.get("resolution_note", "")
    old_group_token = f"group={GROUP}"
    assert note.count(old_group_token) == 1

    planned_alignment = [dict(row) for row in alignments]
    target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    target["decision"] = "same"
    target["ku_id"] = SAME_KU
    target["process_ref"] = NEW_PROCESS_REF
    target["resolution_note"] = (
        note.replace(old_group_token, f"previous_group_label={GROUP}", 1)
        + " S3 re-review (2026-10-16): same as existing person KU "
        f"{SAME_KU}; the existing card explicitly records both Giovanni Battista Passeri and the source-name "
        "form Giambattista Passeri, and the full-book index P.csv#56 plus p.132 L8 identify the same named "
        "person. Prior new decision/group label is retained in previous_group_label for traceability; no new KU."
    )
    assert sync.get_group(target["resolution_note"]) == ""
    assert target["ku_id"] == SAME_KU

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(manifest),
    )
    next_knowledge = knowledge_text + (
        f"\n\n### S3 re-review: Passeri reuse existing person KU（{DATE}）\n\n"
        f"- {CANDIDATE} 原按新人物组 {GROUP} 待登记。回查发现 manifest 已有 {SAME_KU}，其卡片以 "
        "Giovanni Battista Passeri 为规范名，并明确将 Giambattista Passeri 列为原书常用名／本章名形；"
        "卡片第1章 p.3 L15–18 又引 Haskell 称 art-chronicler Giambattista Passeri。全书索引 P.csv#56 "
        "以 Passeri, Giambattista 为主项并指向 p.3，完整书候选在第5章 p.132 L8 再称 critic "
        "Giambattista Passeri。名字、来源锚点和人物角色共同支持复用同一人物 KU，无须外部身份裁定。\n"
        f"- 将 {CANDIDATE} 的决定由 new 改为 same，映射至 {SAME_KU}；原 new 身份组标签保留在 alignment "
        "的 previous_group_label 与本记录中。未创建重复卡片，未改动 S2 陈述或既有 KU 正式关系。\n\n"
        f"S3 same={sync.fmt(totals['same_candidates'])} candidates / {sync.fmt(totals['same_kus'])} existing KUs; "
        f"new={sync.fmt(totals['new_candidates'])} candidates / {sync.fmt(totals['new_groups'])} groups. "
        f"S4 registered={sync.fmt(totals['registered_groups'])} groups/{sync.fmt(totals['registered_members'])} mappings; "
        f"pending={sync.fmt(totals['pending_groups'])} groups/{sync.fmt(totals['pending_members'])} candidate mappings.\n"
    )

    target_files = [
        TABLES / "alignment.csv",
        KNOWLEDGE,
        RESULT,
    ]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in target_files)

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} new->{SAME_KU} same; prior_group={GROUP}; "
            f"manifest_reuse=True; same={totals['same_candidates']}/{totals['same_kus']}; "
            f"new={totals['new_candidates']}/{totals['new_groups']}; "
            f"S4_registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"S4_pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}"
        )
        return 0

    write_targets = {
        TABLES / "alignment.csv": None,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
    }
    for path in write_targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    for path, content in write_targets.items():
        if content is not None:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> existing {SAME_KU}; prior new group retained in note; "
        f"same={totals['same_candidates']}/{totals['same_kus']}; "
        f"new={totals['new_candidates']}/{totals['new_groups']}; "
        f"S4_registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"S4_pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(manifest)}; recovery_backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
