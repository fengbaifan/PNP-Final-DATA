from __future__ import annotations

import argparse
import csv
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
OLD_GROUP = "sg3-place-colonnapalace"
CHIGI_GROUP = "sg3-place-chigi-palace-ss-apostoli"
CANDIDATES = ("cand-0815", "cand-0816")


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Split the conflated Colonna and former-Colonna/Chigi palace S3 groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    _, manifest = read_csv(MANIFEST_PATH)
    by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    first = by_id[CANDIDATES[0]]
    second = by_id[CANDIDATES[1]]
    assert all(by_id[cid]["decision"] == "new" and not by_id[cid].get("ku_id") for cid in CANDIDATES)
    assert all(sync.get_group(by_id[cid].get("resolution_note", "")) == OLD_GROUP for cid in CANDIDATES)
    assert not any(row.get("ku_id") in {"units/places/colonna-palace-rome", "units/places/flavio-chigi-palace-ss-apostoli"} for row in manifest)

    chapter = (ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Cardinal Flavio was fond of painting and he naturally employed Bernini to build, or rather rebuild, the palace in piazza SS. Apostoli which he bought from a branch of the Colonna family in 1662." in chapter
    assert "Their palace, situated near the one sold to the Chigi, had been largely rebuilt and decorated by Filippo and his son, Cardinal Girolamo" in chapter
    assert "m-chp6-p155-012" in (ROOT / "04-knowledge" / "tables" / "mentions.csv").read_text(encoding="utf-8-sig")
    assert "m-chp6-p155-013" in (ROOT / "04-knowledge" / "tables" / "mentions.csv").read_text(encoding="utf-8-sig")

    planned = [dict(row) for row in alignments]
    target = next(row for row in planned if row.get("candidate_id") == CANDIDATES[1] and not row.get("external_source"))
    target["resolution_note"] = target["resolution_note"].replace(
        f"group={OLD_GROUP};",
        f"prior_s3_group_token={OLD_GROUP}; group={CHIGI_GROUP};",
        1,
    )
    target["resolution_note"] += (
        " S3 correction 2026-10-17: split from the prior shared group with cand-0815. The p.155 text explicitly distinguishes "
        "‘Their palace’ (the Colonna family palace, candidate cand-0815) from ‘the one sold to the Chigi’ (candidate cand-0816); "
        "p.154 identifies the latter as the palace in Piazza SS. Apostoli purchased by Cardinal Flavio Chigi from a Colonna branch in 1662. "
        "These are separate, nearby buildings; cand-0816 remains new as its own source-local place. The old group token is retained above as history, not identity evidence."
    )
    source_sibling = next(row for row in planned if row.get("candidate_id") == CANDIDATES[0] and not row.get("external_source"))
    source_sibling["resolution_note"] += (
        " S3 group-boundary correction 2026-10-17: after splitting cand-0816 to a separate Chigi palace group, "
        "this Colonna family palace group contains cand-0815 only; p.155 describes it as nearby the palace sold to Chigi."
    )
    assert sync.get_group(target["resolution_note"]) == CHIGI_GROUP
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    old_audit = "4,589条待登记 `decision=new` alignment 行，含4,574条候选决定映射（4,497组）和15条外部身份记录。"
    new_audit = "4,589条待登记 `decision=new` alignment 行，含4,574条候选决定映射（4,498组）和15条外部身份记录。"
    assert old_audit in result_text
    result_text = result_text.replace(old_audit, new_audit, 1)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3 复核：Colonna palace 与售予 Chigi 的宫殿拆分（2026-10-17）\n\n"
        f"原共享组 `{OLD_GROUP}` 包含 `cand-0815` 与 `cand-0816`；现拆分为两个 `new` place 组：`{OLD_GROUP}`（仅 cand-0815）和 `{CHIGI_GROUP}`（cand-0816）。"
        "第6章 p.154 称 Flavio Chigi 于1662年从 Colonna 家族一支购入 Piazza SS. Apostoli 的宫殿；p.155 随后称 Colonna 家族的另一座宫殿位于“the one sold to the Chigi”附近，并由 Filippo 与 Cardinal Girolamo Colonna 重建和装饰。"
        "邻近关系及两个不同所有者/建筑上下文直接排除同一建筑。cand-0816 的旧 S3 组 token 与理由保留在其 alignment 行的 prior 字段；现行分组依据和边界更正追加于两行。两个对象均无同名 place KU，继续作为 source-local new 对象交 S4。"
        f"修正后 S3 new 仍为{sync.fmt(totals['new_candidates'])}条候选、{sync.fmt(totals['new_groups'])}组；"
        f"S4 待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text += (
        "\n\n### S3 复核：Colonna palace 与售予 Chigi 的宫殿（2026-10-17）\n\n"
        f"旧组 `{OLD_GROUP}` 拆分为两个 place 身份组：`cand-0815` 保留 Colonna family palace；`cand-0816` 改入 `{CHIGI_GROUP}`，指向1662年由 Colonna 家族一支售给 Cardinal Flavio Chigi、位于 Piazza SS. Apostoli 的另一座宫殿。"
        "第6章 p.155 明确称两座宫殿相邻而非同一座；原理由保留在 alignment 历史字段。"
        f"S3 new 共{sync.fmt(totals['new_candidates'])}条候选/{sync.fmt(totals['new_groups'])}组；S4 待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射。"
    )

    if args.dry_run:
        print("S3 palace-group split dry-run passed: cand-0815 remains Colonna palace; cand-0816 becomes distinct Chigi palace")
        print("p.154 identifies the Chigi palace by Piazza SS. Apostoli and purchase in 1662")
        print("p.155 calls the Colonna palace nearby the one sold to Chigi; separate buildings confirmed")
        print(f"S3 new groups={sync.fmt(totals['new_groups'])}; S4 pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
        print("historical token and rationale preserved; no files changed")
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: S3 group split; new groups={sync.fmt(totals['new_groups'])}; "
        f"S4 pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
