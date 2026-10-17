from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CESI_CARD_PATH = ROOT / "04-knowledge" / "units" / "persons" / "cardinal-pier-donato-cesi.md"

TARGET = "cand-0710"
EXISTING_CANDIDATE = "cand-3110"
EXISTING_KU = "units/places/chiesa-nuova"
TARGET_GROUP = "sg3-place-cand-0710"
PROCESS_REF = "S3-Chiesa-Nuova-existing-place-reuse-2026-10-16"
CESI_PENDING_ZH = (
    "11 条直接 S2 断言均标为关系候选；其中8条的对端已映射至 Farnese 枢机或 Oratorians 机构 KU，"
    "另3条的 Chiesa Nuova 对端 `cand-0710` 尚未登记。本批不建立正式关系，待端点完成后按 S6 审查。"
)
CESI_MAPPED_ZH = (
    "11 条直接 S2 断言均标为关系候选；其对端均已有 KU：4条指 Cardinal Alessandro Farnese，4条指 Oratorians 机构，"
    "3条指已复用的 Chiesa Nuova 地点 KU（`cand-0710`）。本批不建立正式关系；这些断言仍待 S6 按端点、关系类型、语境与证据审查。"
)
CESI_PENDING_EN = (
    "All 11 direct S2 statements are marked as relation candidates: eight counterpart endpoints map to the Farnese cardinal or "
    "the Oratorians institution KU, while the three Chiesa Nuova counterparts (`cand-0710`) remain unregistered. This batch creates no formal relation; "
    "the statements remain for S6 after the endpoint is registered."
)
CESI_MAPPED_EN = (
    "All 11 direct S2 statements are marked as relation candidates and each counterpart now maps to a KU: four to Cardinal Alessandro Farnese, "
    "four to the Oratorians institution, and three to the reused Chiesa Nuova place KU (`cand-0710`). This batch creates no formal relation; "
    "the statements remain for S6 review of endpoints, relation types, context, and evidence."
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


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def update_process(text):
    text = replace_once(
        text,
        "截至 Cardinal Pier Donato Cesi 批次，4,844 个当前 `new` 身份组中完成163组，余4,681组；5,016条成员候选中映射208条，余4,808条。",
        "截至 Chiesa Nuova S3 复用裁决后，4,843 个当前 `new` 身份组中完成163组，余4,680组；5,015条成员候选中映射208条，余4,807条。",
        "current S4 totals after S3 reuse",
    )
    text = replace_once(
        text,
        "11条直接 S2 断言全部带 `relation_candidate`；其中8条对端已映射到 Cardinal Alessandro Farnese 或 Oratorians KU，3条对端为尚未登记的 Chiesa Nuova 候选 `cand-0710`。关系候选不写入正式关系表，留待端点登记后 S6 审查；本批不做外部身份核验或 S5 补足。书内将其兄弟 Angelo Cesi 与 Pier Donato 区分，未合并 Cesi 家族卡或 Farnese 枢机卡。",
        "11条直接 S2 断言全部带 `relation_candidate`；登记时其中8条对端已映射到 Cardinal Alessandro Farnese 或 Oratorians KU，3条对端为当时尚未登记的 Chiesa Nuova 候选 `cand-0710`。后续 S3 将 `cand-0710` 复用至既有 `units/places/chiesa-nuova`，故 Cesi 的11条关系候选现均有已登记对端；关系本身仍留待 S6 审查。本批不做外部身份核验或 S5 补足。书内将其兄弟 Angelo Cesi 与 Pier Donato 区分，未合并 Cesi 家族卡或 Farnese 枢机卡。",
        "Cesi process endpoint status",
    )
    followup = """### S3 更正：Chiesa Nuova 索引候选复用既有地点 KU（2026-10-16）

`cand-0710`（C.csv#234，Rome 下 “S. Maria della Vallicella (Chiesa Nuova)” 子目）原裁为 `new`，组 `sg3-place-cand-0710`。复核发现该索引名称与已接受的 `units/places/chiesa-nuova` 完全对应：既有 KU 类型为 place，标题为“罗马新教堂（Chiesa Nuova, Rome）”，其卡片保留 Rome、Santa Maria in Vallicella 与 Chiesa Nuova 的身份依据；全书 S2 也把三者置于同一替换教堂及其建造语境。故将 `cand-0710` 更正为 `same` 并映射至该既有 KU，不另建卡。原 `new` 组号和裁决理由保存在对齐行历史注释中。

该候选是 Pier Donato Cesi 的3条直接关系候选对端。复用后，Cesi 的11条直接关系候选对端全部映射到既有 KU；正式关系仍待 S6，不因端点齐备自动成立。S4 新组总量减少1组、1条候选，已登记数和 manifest 不变：`same=1,709`、`new=5,015`（4,843组）、`undecided=5,575`、`conflict=7`、`excluded=98`；S4 已登记163组/208条，待登记4,680组/4,807条。现有 same KU 去重数仍为1,025。本批未修改 manifest、accepted.yml、既有 Chiesa Nuova 卡或正式关系表。

"""
    return text + "\n" + followup


def update_result(text):
    text = replace_once(
        text,
        "same=1,708（指向1,025个既有 KU）、new=5,016（4,844个身份组）",
        "same=1,709（指向1,025个既有 KU）、new=5,015（4,843个身份组）",
        "result S3 decision totals",
    )
    text = replace_once(
        text,
        "S4 已登记163组、映射208条成员候选；尚待登记4,681组、4,808条映射。",
        "S4 已登记163组、映射208条成员候选；尚待登记4,680组、4,807条映射。S3 将 `cand-0710` 复用到既有 Chiesa Nuova 地点 KU。",
        "result current S4 totals",
    )
    text = replace_once(
        text,
        "11条直接 S2 断言均为关系候选，8条对端已有 Farnese 枢机或 Oratorians KU，3条对端 `cand-0710`（Chiesa Nuova）仍待登记；本批不新增正式关系、外部身份核验或 S5 补足。",
        "11条直接 S2 断言均为关系候选；登记时3条 Chiesa Nuova 对端 `cand-0710` 尚待处理，随后 S3 将其复用至既有 `units/places/chiesa-nuova`。当前11条断言的另一端均已有 KU，但正式关系仍留待 S6；本批不新增外部身份核验或 S5 补足。",
        "result Cesi endpoint status",
    )
    followup = """### S3 更正：Chiesa Nuova 索引候选复用既有地点 KU（2026-10-16）

`cand-0710`（C.csv#234，Rome 下 “S. Maria della Vallicella (Chiesa Nuova)” 子目）已从 `new` 更正为 `same`，映射至[既有罗马新教堂地点 KU](../../04-knowledge/units/places/chiesa-nuova.md)。索引子目明确给出 Santa Maria della Vallicella / Chiesa Nuova 名称，既有 place KU 标题及已接受身份依据相符；不另建重复地点卡。历史 `new` 组号和理由保留在对齐行。

这是 Pier Donato Cesi 的3条直接关系候选对端；更正后，他的11条直接关系候选均已有已登记的另一端 KU，但这些候选关系仍须 S6 审查。全局 S3 现为 `same=1,709`、`new=5,015`（4,843组）、`undecided=5,575`、`conflict=7`、`excluded=98`；S4 已登记163组/208条映射，尚待4,680组/4,807条。same 映射的唯一既有 KU 数仍为1,025；manifest、accepted.yml、既有地点卡和正式关系表未变。裁决和写回依据见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)与[复核脚本](../../03-processing/patrons-and-painters-full-book-s2/process/reconcile_s3_chiesa_nuova_existing_place_20261016.py)。

"""
    return replace_once(
        text,
        "### person：Simon Vouet 双候选 S4 登记（2026-10-16）",
        followup + "### person：Simon Vouet 双候选 S4 登记（2026-10-16）",
        "result S3 follow-up insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Reuse the accepted Chiesa Nuova place KU for its full-book index candidate")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(CANDIDATE_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_rows = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in decision_rows}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    target = candidate_by_id[TARGET]
    current = alignment_by_id[TARGET]
    assert target["suggested_type"] == "place" and target["status"] == "open"
    assert target["index_entry_id"] == "C.csv#234"
    assert target["sub_entry"] == "S. Maria della Vallicella (Chiesa Nuova)"
    assert current["decision"] == "new" and not current.get("ku_id")
    assert get_group(current["resolution_note"]) == TARGET_GROUP

    index_path = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "C.csv"
    _, index_rows = read_csv(index_path)
    assert any(
        row.get("Main Entry") == "Churches"
        and row.get("Location") == "Rome"
        and row.get("Sub-entry") == "S. Maria della Vallicella (Chiesa Nuova)"
        for row in index_rows
    ), "source index row changed"

    existing_manifest = manifest_by_id[EXISTING_KU]
    assert existing_manifest["type"] == "place"
    assert existing_manifest["card_path"] == "04-knowledge/units/places/chiesa-nuova.md"
    assert existing_manifest["card_path"] in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    existing_card = (ROOT / existing_manifest["card_path"]).read_text(encoding="utf-8-sig")
    assert 'title: "罗马新教堂（Chiesa Nuova, Rome）"' in existing_card
    assert "Santa Maria in Vallicella" in existing_card and "Chiesa Nuova, Rome" in existing_card
    known = alignment_by_id[EXISTING_CANDIDATE]
    assert known["decision"] == "same" and known["ku_id"] == EXISTING_KU

    decisions_before = Counter(row["decision"] for row in decision_rows)
    assert decisions_before == Counter({"same": 1708, "new": 5016, "undecided": 5575, "excluded": 98, "conflict": 7})
    same_kus_before = {row["ku_id"] for row in decision_rows if row["decision"] == "same" and row.get("ku_id")}
    assert len(same_kus_before) == 1025
    new_groups = defaultdict(list)
    for row in decision_rows:
        if row["decision"] == "new":
            group = get_group(row.get("resolution_note", ""))
            assert group
            new_groups[group].append(row)
    assert len(new_groups) == 4844
    registered_groups = defaultdict(list)
    for row in decision_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_groups[get_group(row["resolution_note"])].append(row)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (163, 208)

    statements = []
    with STATEMENTS_PATH.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if TARGET in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                statements.append(statement)
    cesi_ids = {
        "st-chp3-secii-l40-52-cesi-fund-chiesa-nuova",
        "st-chp3-secii-l40-52-cesi-little-building-interference",
        "st-chp3-secii-l40-52-cesi-terms-arms-privileges",
    }
    cesi_endpoints = {
        statement["statement_id"]
        for statement in statements
        if "cand-0640" in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
        and statement.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert cesi_endpoints & cesi_ids == cesi_ids
    assert all(statement.get("qualifiers", {}).get("relation_candidate") is True for statement in statements if statement["statement_id"] in cesi_ids)

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned if row.get("candidate_id") and not row.get("external_source")}
    old_note = planned_by_id[TARGET]["resolution_note"]
    planned_by_id[TARGET]["decision"] = "same"
    planned_by_id[TARGET]["ku_id"] = EXISTING_KU
    planned_by_id[TARGET]["process_ref"] = PROCESS_REF
    planned_by_id[TARGET]["resolution_note"] = (
        f"matched_manifest={EXISTING_KU}; matched_candidate_ids={EXISTING_CANDIDATE}; "
        "source_ref=02-sources/03-Index/03-2-Index-CSV/C.csv#236; Same: the index subentry explicitly reads "
        "‘S. Maria della Vallicella (Chiesa Nuova)’ under Churches, Rome. The accepted manifest already contains a "
        "place KU titled ‘Chiesa Nuova, Rome’, and its card identifies Rome and Santa Maria in Vallicella as the same "
        "church; full-book candidate cand-3110 already maps to that KU. Chapter 3 describes the successor church as "
        "a larger building of the same name, often called the Chiesa Nuova. This is the same source-local place, not "
        "a separate church or an institution. Reuse the accepted KU; no new card or external identity claim. "
        f"Historical S3 decision and rationale retained: {old_note}"
    )

    planned_decisions = [row for row in planned if row.get("candidate_id") and not row.get("external_source")]
    decisions_after = Counter(row["decision"] for row in planned_decisions)
    assert decisions_after == Counter({"same": 1709, "new": 5015, "undecided": 5575, "excluded": 98, "conflict": 7})
    same_kus_after = {row["ku_id"] for row in planned_decisions if row["decision"] == "same" and row.get("ku_id")}
    assert same_kus_after == same_kus_before
    groups_after = defaultdict(list)
    for row in planned_decisions:
        if row["decision"] == "new":
            groups_after[get_group(row["resolution_note"])].append(row)
    assert len(groups_after) == 4843 and TARGET_GROUP not in groups_after
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (163, 208)

    planned_by_id = {row["candidate_id"]: row for row in planned_decisions}
    for statement_id in cesi_ids:
        statement = next(row for row in statements if row["statement_id"] == statement_id)
        other = statement.get("object_candidate_id") if statement.get("subject_candidate_id") == "cand-0640" else statement.get("subject_candidate_id")
        assert planned_by_id[other].get("ku_id")

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    cesi_card = CESI_CARD_PATH.read_text(encoding="utf-8-sig")
    cesi_card = replace_once(cesi_card, CESI_PENDING_ZH, CESI_MAPPED_ZH, "Cesi Chinese endpoint mapping")
    cesi_card = replace_once(cesi_card, CESI_PENDING_EN, CESI_MAPPED_EN, "Cesi English endpoint mapping")

    if args.dry_run:
        print(
            "dry-run passed: cand-0710 new->same units/places/chiesa-nuova; "
            "same=1708->1709 new=5016->5015 groups=4844->4843 "
            "registered_new_groups=163 mapped_candidates=208 pending_groups=4680 pending_candidates=4807 "
            "Cesi_counterparts=11/11_mapped; manifest/accepted/existing_place_card unchanged"
        )
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    CESI_CARD_PATH.write_text(cesi_card, encoding="utf-8-sig", newline="\n")
    print(
        "applied: cand-0710 -> units/places/chiesa-nuova; S3 same=1709 new=5015 groups=4843; "
        "S4 registered_groups=163 mapped_candidates=208 pending_groups=4680 pending_candidates=4807; "
        "Cesi_counterparts=11/11_mapped; manifest/accepted unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
