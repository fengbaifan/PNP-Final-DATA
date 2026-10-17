from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "alignment.csv"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
CANDIDATE = "cand-2797"
KU_ID = "units/persons/count-of-waldstein-casanova-dux"
OLD_CLAIMS = (
    "source anchor gives a full personal name",
    "Grouped with cand-2797 by identical normalized full-name/explicit-alias anchor (of waldstein)",
)
CORRECTION = (
    " S3 correction 2026-10-17 (expanded): withdraw also the earlier claim that the candidate was "
    "grouped by an identical normalized full-name/explicit-alias anchor (‘of waldstein’). The book gives "
    "no full personal name or alias. The preserved group token `new-person:of-waldstein-9d1421b82c` is a "
    "tracking key only, not identity evidence. The current `new` decision rests solely on the source-local "
    "individual identified in p.367 as Casanova’s patron at Dux; no historical forename or external identity is asserted."
)
PROCESS_ADDENDUM = (
    "\n\n### S3 裁决理由补正：Waldstein 身份组依据（2026-10-17）\n\n"
    "在 S4 登记后复核 alignment 原备注，发现除“原书提供全名”外，旧备注中的“按 `(of waldstein)` "
    "全名／别名锚点聚组”也不成立。原书和索引都没有给出全名或别名；保留的 `new-person:of-waldstein-9d1421b82c` "
    "仅为稳定追踪键，不构成身份依据。现行 `new` 决定限于 p.367 中作为 Casanova 在 Dux 保护人的单一书内人物，" 
    "不声称其历史全名或外部身份已确认。该候选组目前只有 `cand-2797`；依据修订已追加到其 alignment 行，旧理由保留为历史记录。"
)
RESULT_REPLACEMENT = (
    "alignment 行追加更正：原书只给爵称及“Casanova 在 Dux 的保护人”语境；"
    "旧备注中按 `(of waldstein)` 全名／别名锚点聚组的说法也已撤回，组 token 仅作追踪标识。卡片未推定名字或外部身份。"
)


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
    parser = argparse.ArgumentParser(description="Correct unsupported Waldstein S3 grouping rationale while preserving the prior note.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, rows = read_csv(TABLE)
    matches = [row for row in rows if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(matches) == 1
    target = matches[0]
    assert target.get("decision") == "new" and target.get("ku_id") == KU_ID
    assert all(claim in target["resolution_note"] for claim in OLD_CLAIMS)
    assert CORRECTION not in target["resolution_note"]

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    assert "### S3 裁决理由补正：Waldstein 身份组依据（2026-10-17）" not in process_text
    assert RESULT_REPLACEMENT not in result_text
    assert "更新日期：2026-10-16。" in result_text
    assert "4,595条待登记 `decision=new` alignment 行，含4,580条候选决定映射（4,500组）和15条外部身份记录。" in result_text

    planned_rows = [dict(row) for row in rows]
    planned = next(row for row in planned_rows if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    planned["resolution_note"] += CORRECTION
    planned_process = process_text + PROCESS_ADDENDUM
    planned_result = result_text.replace(
        RESULT_REPLACEMENT.split("alignment 行追加更正：", 1)[0] + "alignment 行追加更正：原书只给爵称及“Casanova 在 Dux 的保护人”语境；卡片未推定名字或外部身份。",
        RESULT_REPLACEMENT,
        1,
    )
    planned_result = planned_result.replace("更新日期：2026-10-16。", "更新日期：2026-10-17。", 1)
    planned_result = planned_result.replace(
        "4,595条待登记 `decision=new` alignment 行，含4,580条候选决定映射（4,500组）和15条外部身份记录。",
        "4,594条待登记 `decision=new` alignment 行，含4,579条候选决定映射（4,499组）和15条外部身份记录。",
        1,
    )
    planned_result += (
        "\n\n### S4 验证：Waldstein source-local person 登记（2026-10-17）\n\n"
        "- `build_field_facts.py` 预检：cards=1,357；enrichment rows=10,476；new/changed/removed IDs 均为0；"
        "source registry changes=0；warnings=0。无字段表写回。\n"
        "- `audit_tables.py --strict-stage --summary` 退出码0：KU=1,357；`errors=[]`、`s2_missing=[]`；"
        "待登记 new alignment 共4,594条，其中4,579条候选映射（4,499组）和15条外部身份记录。"
        "既有两条来源引用警告（`enr-06678`、`enr-06937`）与S2语义审查提示继续保留。"
        "卡片/清单/映射对齐；Casanova 关系候选端点现有 KU，但两条关系候选仍待 S6，未改 `relations.csv`。\n"
    )

    if args.dry_run:
        print(f"S3 rationale correction dry-run passed: {CANDIDATE} -> {KU_ID}")
        print("both unsupported full-name and alias-group claims will remain visible as superseded history")
        print("new basis: one source-local person identified by the Dux patron role; no external identity asserted")
        print("result date and strict-stage snapshot will be updated to the observed 2026-10-17 audit")
        print("no files changed")
        return 0

    write_csv(TABLE, fields, planned_rows)
    PROCESS.write_text(planned_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(planned_result, encoding="utf-8-sig", newline="\n")
    print("applied: alignment rationale corrected; process and result records updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
