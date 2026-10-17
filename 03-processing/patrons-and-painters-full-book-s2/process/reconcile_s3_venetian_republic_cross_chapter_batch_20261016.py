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

SAME_TARGETS = (
    "cand-6255",
    "cand-8105",
    "cand-8572",
    "cand-8838",
    "cand-9789",
    "cand-9874",
)
PENDING_TARGET = "cand-8668"
EXISTING_CANDIDATE = "cand-3678"
EXISTING_KU = "units/institutions/republic-of-venice"
EXISTING_GROUP = "sg3-ku-units-institutions-republic-of-venice"
PROCESS_REF = "S3-Venetian-Republic-cross-chapter-reconciliation-2026-10-16"

SOURCE_ANCHORS = {
    "cand-6255": ("06_CHP-6_sec_i.md", "France, Tuscany, Venice and Modena banded together"),
    "cand-8105": ("09_CHP-9_intro.md", "the government did everything possible to promote"),
    "cand-8572": ("09_CHP-9_intro.md", "they gave to the Republic one of its most impressive Doges"),
    "cand-8668": ("09_CHP-9_sec_ii.md", "Within the State itself, however, the government insisted on a policy"),
    "cand-8838": ("10_CHP-10_intro.md", "he quarrelled with the Republic"),
    "cand-9789": ("10_CHP-10_sec_ii.md", "which caused the government so much trouble during the eighteenth century"),
    "cand-9874": ("10_CHP-10_sec_ii.md", "Thus ended State interference in the arts"),
}


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
        "截至 Chiesa Nuova S3 复用裁决后，4,843 个当前 `new` 身份组中完成163组，余4,680组；5,015条成员候选中映射208条，余4,807条。",
        "截至威尼斯共和国跨章身份复核后，4,836 个当前 `new` 身份组中完成163组，余4,673组；5,008条成员候选中映射208条，余4,800条。",
        "current S4 totals after Republic reconciliation",
    )
    batch = """### S3 跨章复核：威尼斯共和国候选复用与政府机构待证（2026-10-16）

对照既有 `units/institutions/republic-of-venice` 及其 accepted KU，将6条书内候选复用至同一政治实体；`cand-3678` 是既有全书锚点，所有新决定均追加保留原 `new` 组和理由：

| 候选 | 来源锚点 | S3 去向 |
|---|---|---|
| `cand-6255` | 第6章 p.146，Venice 与 France、Tuscany、Modena 联合反对 Barberini 扩张 | `same` → Republic of Venice；“Venice”在此是政治行动者，不是城市。 |
| `cand-8105` | 第9章 p.245，政府推动旅游同时限制外来影响 | `same` → Republic of Venice；Haskell以 government / State 叙述同一主权政治实体及其治理行为，没有另指独立命名的机关。39条直接 S2 关系候选继续保留原词。 |
| `cand-8572` | 第9章 p.263，Sagredo 家族向共和国贡献 Doge Niccolò | `same` → Republic of Venice；正文直接称 Republic。 |
| `cand-8838` | 第10章 p.276，Lord Manchester 与共和国发生争执后离开 | `same` → Republic of Venice；正文直接称 Republic。 |
| `cand-9789` | 第10章 p.325，Barnabotti 与政府、全邦公共利益及改革语境 | `same` → Republic of Venice；这里是威尼斯政治实体的治理语境，未具名另一机关。 |
| `cand-9874` | 第10章 p.331，State interference in the arts | `same` → Republic of Venice；`State`为政治权力指称，没有指名独立部门。 |

`cand-8668`（第9章 p.267）暂改为 `undecided`：Haskell 明说 “Within the State itself ... the government”，区分国家与政府，但未命名该政府机构，也未说明其与 Republic KU 的实体边界。不能把该政府强并为共和国，也不凭一个泛称先创建新机关卡。后续须有来源识别具体机构或足以确定其治理实体边界；在此之前保持待证并阻断相关关系端点。

脚本 dry-run 核对7条原 `new` 决定、各自书内原文、6条 existing-KU 复用映射、1条待证去向及候选组唯一性。应用后候选决定为 `same=1,715`、`new=5,008`、`undecided=5,576`、`conflict=7`、`excluded=98`；same 的唯一既有 KU 仍为1,025。S4 已登记163组/208条映射，待登记4,673组/4,800条；manifest、accepted.yml 与 formal relations 未变。

"""
    return text + "\n" + batch


def update_result(text):
    text = replace_once(
        text,
        "same=1,709（指向1,025个既有 KU）、new=5,015（4,843个身份组）、conflict=7、excluded=98、undecided=5,575",
        "same=1,715（指向1,025个既有 KU）、new=5,008（4,836个身份组）、conflict=7、excluded=98、undecided=5,576",
        "result S3 decision totals",
    )
    text = replace_once(
        text,
        "S4 已登记163组、映射208条成员候选；尚待登记4,680组、4,807条映射。S3 将 `cand-0710` 复用到既有 Chiesa Nuova 地点 KU。",
        "S4 已登记163组、映射208条成员候选；尚待登记4,673组、4,800条映射。S3 已将 `cand-0710` 复用到既有 Chiesa Nuova 地点 KU，并将6条威尼斯共和国政治实体候选复用到既有 KU；`cand-8668` 因政府／国家边界未明保留待证。",
        "result current S4 totals",
    )
    followup = """### S3 跨章复核：威尼斯共和国候选复用与政府机构待证（2026-10-16）

将 `cand-6255`、`cand-8105`、`cand-8572`、`cand-8838`、`cand-9789`、`cand-9874` 映射至[既有威尼斯共和国 KU](../../04-knowledge/units/institutions/republic-of-venice.md)。证据分别为第6章 p.146 的政治联盟、第9章 pp.245、263 的治理与共和国指称，以及第10章 pp.276、325、331 的共和国、政治改革和 State 语境。它们均指同一历史政治实体，不是 Venice 城市；对 government、State 等原文措辞的差异保留在各候选说明中。`cand-8105` 对应39条直接 S2 关系候选，映射没有把候选谓词提升为正式关系。

`cand-8668` 从 `new` 改为 `undecided`：第9章 p.267 明确区分 State 与 government，但没有说明 government 是既有 Republic KU 的治理行为还是独立组织。暂不合并或建立未具名政府卡，等待能界定其组织身份的来源；相关端点在此之前保持待证。原决定、组号和理由均留在对齐行历史注释中。

当前 S3 为 `same=1,715`（映射至1,025个既有 KU）、`new=5,008`（4,836组）、`undecided=5,576`、`conflict=7`、`excluded=98`。S4 已登记163组/208条候选映射，尚待4,673组/4,800条。没有新增 KU、manifest/accepted 条目或正式关系。依据、候选去向与逐项证据见[处理记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)和[复核脚本](../../03-processing/patrons-and-painters-full-book-s2/process/reconcile_s3_venetian_republic_cross_chapter_batch_20261016.py)。

"""
    return replace_once(
        text,
        "### person：Simon Vouet 双候选 S4 登记（2026-10-16）",
        followup + "### person：Simon Vouet 双候选 S4 登记（2026-10-16）",
        "result Republic S3 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Align cross-chapter Venetian polity candidates with the accepted Republic of Venice KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(CANDIDATE_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in decisions}
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    existing_manifest = manifest_by_id[EXISTING_KU]
    assert existing_manifest["type"] == "institution"
    assert existing_manifest["card_path"] == "04-knowledge/units/institutions/republic-of-venice.md"
    assert existing_manifest["card_path"] in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    existing_card = (ROOT / existing_manifest["card_path"]).read_text(encoding="utf-8-sig")
    assert "title: 威尼斯共和国（Republic of Venice）" in existing_card
    assert "历史政治实体" in existing_card
    assert alignment_by_id[EXISTING_CANDIDATE]["decision"] == "same"
    assert alignment_by_id[EXISTING_CANDIDATE]["ku_id"] == EXISTING_KU
    existing_same = [row for row in decisions if row["decision"] == "same" and get_group(row.get("resolution_note")) == EXISTING_GROUP]
    assert {row["candidate_id"] for row in existing_same} == {EXISTING_CANDIDATE}

    targets = set(SAME_TARGETS) | {PENDING_TARGET}
    assert targets <= set(candidate_by_id) and targets <= set(alignment_by_id)
    for cid in targets:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == "institution" and candidate["status"] == "open"
        assert row["decision"] == "new" and not row.get("ku_id"), cid
        assert get_group(row.get("resolution_note")) == f"sg3-institution-{cid}"
        filename, quote = SOURCE_ANCHORS[cid]
        source = (ROOT / "02-sources" / "02-Markdown" / filename).read_text(encoding="utf-8-sig")
        assert quote in source, (cid, filename, quote)

    before = Counter(row["decision"] for row in decisions)
    assert before == Counter({"same": 1709, "new": 5015, "undecided": 5575, "excluded": 98, "conflict": 7}), before
    same_kus_before = {row["ku_id"] for row in decisions if row["decision"] == "same" and row.get("ku_id")}
    assert len(same_kus_before) == 1025
    old_groups = defaultdict(list)
    for row in decisions:
        if row["decision"] == "new":
            old_groups[get_group(row.get("resolution_note"))].append(row)
    assert len(old_groups) == 4843
    for cid in targets:
        assert {row["candidate_id"] for row in old_groups[get_group(alignment_by_id[cid]["resolution_note"])]} == {cid}, cid

    with STATEMENTS_PATH.open(encoding="utf-8-sig") as stream:
        statements = [json.loads(line) for line in stream if line.strip()]
    direct_relation_counts = {}
    for cid in targets:
        direct_relation_counts[cid] = sum(
            1
            for statement in statements
            if cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
            and statement.get("qualifiers", {}).get("relation_candidate") is True
        )
    assert direct_relation_counts["cand-8105"] == 39, direct_relation_counts

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned if row.get("candidate_id") and not row.get("external_source")}
    for cid in SAME_TARGETS:
        old_note = planned_by_id[cid]["resolution_note"]
        filename, _ = SOURCE_ANCHORS[cid]
        candidate = candidate_by_id[cid]
        planned_by_id[cid]["decision"] = "same"
        planned_by_id[cid]["ku_id"] = EXISTING_KU
        planned_by_id[cid]["process_ref"] = PROCESS_REF
        planned_by_id[cid]["resolution_note"] = (
            f"matched_manifest={EXISTING_KU}; matched_candidate_ids={EXISTING_CANDIDATE}; group={EXISTING_GROUP}; "
            f"source_ref={candidate['candidate_source_ref']}@02-sources/02-Markdown/{filename}; Same: "
            "the source identifies Venice, the Republic, Venetian government or State as the historical polity acting in context. "
            "The accepted KU represents the Republic of Venice as a historical political entity; the city of Venice remains a separate type. "
            "These passages do not name a separate governmental organ. Preserve each passage's original wording and scope; do not infer a formal "
            "relationship from this identity mapping. No new external identity source was consulted. Historical S3 decision and rationale retained: "
            f"{old_note}"
        )

    old_note = planned_by_id[PENDING_TARGET]["resolution_note"]
    planned_by_id[PENDING_TARGET]["decision"] = "undecided"
    planned_by_id[PENDING_TARGET]["ku_id"] = ""
    planned_by_id[PENDING_TARGET]["process_ref"] = PROCESS_REF
    planned_by_id[PENDING_TARGET]["resolution_note"] = (
        f"source_ref={candidate_by_id[PENDING_TARGET]['candidate_source_ref']}@02-sources/02-Markdown/09_CHP-9_sec_ii.md#L3; "
        f"group=sg3-institution-{PENDING_TARGET}; Undecided: Haskell explicitly distinguishes government from the State in this passage, "
        "but names no independent government institution and does not establish whether the referent is the existing Republic of Venice KU or a distinct "
        "organization. Do not force a same mapping or create an unnamed government KU. Next evidence route: require a source identifying the government body "
        "or establishing its entity boundary; until then keep this candidate undecided and its relation endpoints pending. Historical new-group decision and "
        f"rationale retained: {old_note}"
    )

    after_rows = [row for row in planned if row.get("candidate_id") and not row.get("external_source")]
    after = Counter(row["decision"] for row in after_rows)
    assert after == Counter({"same": 1715, "new": 5008, "undecided": 5576, "excluded": 98, "conflict": 7}), after
    same_kus_after = {row["ku_id"] for row in after_rows if row["decision"] == "same" and row.get("ku_id")}
    assert same_kus_after == same_kus_before
    new_groups_after = defaultdict(list)
    for row in after_rows:
        if row["decision"] == "new":
            new_groups_after[get_group(row.get("resolution_note"))].append(row)
    assert len(new_groups_after) == 4836
    registered_groups = defaultdict(list)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_groups[get_group(row.get("resolution_note"))].append(row)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (163, 208)
    assert len(new_groups_after) - len(registered_groups) == 4673
    assert sum(len(rows) for rows in new_groups_after.values()) - 208 == 4800

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))

    if args.dry_run:
        print(
            "dry-run passed: six Republic/polity candidates new->same existing KU; cand-8668 new->undecided; "
            "same=1709->1715 new=5015->5008 undecided=5575->5576 groups=4843->4836 "
            "cand-8105_direct_relation_candidates=39 registered_new_groups=163 mapped_candidates=208 "
            "pending_groups=4673 pending_candidates=4800; manifest/accepted/cards unchanged"
        )
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: six candidates -> units/institutions/republic-of-venice; cand-8668 -> undecided; "
        "S3 same=1715 new=5008 undecided=5576 groups=4836; S4 pending_groups=4673 pending_candidates=4800; "
        "manifest/accepted/cards unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
