from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KNOWLEDGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
PROCESS_REF = "S3-full-book-2026-10-16"
BACKUP_SUFFIX = ".bak-s3-mazarin-index-events-20261016"
EVENT_GROUPS = {
    "cand-1594": "sg3-event-cand-1594",
    "cand-1595": "sg3-event-cand-1595",
    "cand-1598": "sg3-event-cand-6799",
    "cand-1599": "sg3-event-cand-1599",
}
EXPECTED_BASELINE = Counter({"same": 1774, "new": 5017, "conflict": 8, "excluded": 99, "undecided": 5506})


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), had_bom


def encode_csv(headers: list[str], rows: list[dict[str, str]], had_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    text = stream.getvalue()
    return ("\ufeff" + text if had_bom else text).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one result occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def group_of(row: dict[str, str]) -> str:
    match = re.search(r"(?:^|;\s*)group=([^;\s]+)", row["resolution_note"])
    return match.group(1) if match else ""


def identity_key(row: dict[str, str]) -> str:
    if row["ku_id"]:
        return f"ku:{row['ku_id']}"
    group = group_of(row)
    if not group:
        raise SystemExit(f"New candidate {row['candidate_id']} has neither a KU target nor a group token.")
    return f"group:{group}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (ROOT / "04-knowledge" / "accepted.yml").exists():
        raise SystemExit("Run this script from the project root.")

    alignment_headers, alignment, alignment_bom = read_csv(ALIGNMENT)
    _, candidates, _ = read_csv(CANDIDATES)
    primary = [row for row in alignment if not row["external_source"]]
    external = [row for row in alignment if row["external_source"]]
    primary_by_id = {row["candidate_id"]: row for row in primary}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(primary) != 12404 or len(alignment) != 12622 or len(external) != 218:
        raise SystemExit("Unexpected alignment shape; inspect the current S3 baseline.")
    if Counter(row["decision"] for row in primary) != EXPECTED_BASELINE:
        raise SystemExit("Unexpected S3 decision counts; inspect the current baseline.")
    baseline_new = [row for row in primary if row["decision"] == "new"]
    baseline_groups = {identity_key(row) for row in baseline_new}
    baseline_pending_groups = {group_of(row) for row in baseline_new if not row["ku_id"]}
    if len(baseline_groups) != 4837 or len(baseline_pending_groups) != 4556:
        raise SystemExit("Unexpected current S4 identity-group mapping; inspect the alignment before proceeding.")
    by_type: dict[str, list[dict[str, str]]] = {}
    for row in baseline_new:
        by_type.setdefault(candidate_by_id[row["candidate_id"]]["suggested_type"], []).append(row)
    archive_groups = {identity_key(row) for row in by_type.get("archive", [])}
    archive_pending = {group_of(row) for row in by_type.get("archive", []) if not row["ku_id"]}
    if len(archive_groups) != 1221 or len(archive_pending) != 1192:
        raise SystemExit("Unexpected archive group tally; inspect the type-specific mapping before proceeding.")

    expected_candidates = {
        "cand-1594": ("event", "M.csv#133"),
        "cand-1595": ("event", "M.csv#134"),
        "cand-1598": ("event", "M.csv#137"),
        "cand-1599": ("event", "M.csv#138"),
        "cand-1600": ("term", "M.csv#139"),
    }
    for cid, (kind, index_id) in expected_candidates.items():
        if cid not in primary_by_id or cid not in candidate_by_id:
            raise SystemExit(f"Missing candidate or alignment row for {cid}.")
        candidate = candidate_by_id[cid]
        decision = primary_by_id[cid]
        if candidate["suggested_type"] != kind or candidate["index_entry_id"] != index_id:
            raise SystemExit(f"{cid} no longer matches the expected typed index entry.")
        if decision["decision"] != "undecided" or decision["ku_id"]:
            raise SystemExit(f"{cid} is no longer the expected undecided candidate.")

    sibling = primary_by_id.get("cand-6799")
    if not sibling or sibling["decision"] != "new" or group_of(sibling) != "sg3-event-cand-6799":
        raise SystemExit("The existing First Fronde event group changed; review before regrouping.")

    statement_ids = {
        "st-chp7-p176-i32",
        "st-chp7-p177-i01",
        "st-chp7-p181-i18",
        "st-chp7-p182-i20",
        "st-chp7-p182-i21",
        "st-chp7-p182-i24",
        "st-chp7-p183-i02",
        "st-chp7-p183-i13",
        "st-chp7-p183-i20",
        "st-chp7-p184-i07",
        "st-chp7-p184-i10",
        "st-chp7-p184-i11",
        "st-chp7-p184-i16",
    }
    present_statements = {
        json.loads(line)["statement_id"]
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    }
    missing_statements = statement_ids - present_statements
    if missing_statements:
        raise SystemExit(f"Missing cited S2 statements: {sorted(missing_statements)}")

    updated_alignment = [dict(row) for row in alignment]
    updated_by_id = {row["candidate_id"]: row for row in updated_alignment if not row["external_source"]}
    prior_notes = {cid: updated_by_id[cid]["resolution_note"] for cid in expected_candidates}
    notes = {
        "cand-1594": (
            "source_ref=index_candidate=cand-1594;index_locator=M.csv#133 p.176,177,181; "
            "statements=st-chp7-p176-i32,st-chp7-p177-i01,st-chp7-p181-i18; "
            f"group={EVENT_GROUPS['cand-1594']}; "
            "The index entry denotes Mazarin's early-1644 effort to persuade Bernini to settle in France, with a large salary; the following page records Urban VIII's reported intervention, and p.181 summarizes the failed early recruitment effort. No existing event KU represents this specific recruitment episode. Keep it separate from Mazarin's different proposal to have Bernini enlarge the Tubeuf palace (st-chp7-p181-i19), and from the distinct 1648 Algardi effort. "
            f"prior_resolution_note={prior_notes['cand-1594']}"
        ),
        "cand-1595": (
            "source_ref=index_candidate=cand-1595;index_locator=M.csv#134 p.182,183; "
            "statements=st-chp7-p182-i20,st-chp7-p182-i21,st-chp7-p182-i24; "
            f"group={EVENT_GROUPS['cand-1595']}; "
            "The index entry denotes the 1648 personal appeal to Algardi, with generous terms, to reverse an earlier refusal; the source continues the episode on p.183 with Algardi cancelling the French contracts after papal intervention. No existing event KU represents this specific effort. Keep it separate from the early-1644 Bernini recruitment episode; the source's approximate earlier refusal is context, not a second candidate in this index row. "
            f"prior_resolution_note={prior_notes['cand-1595']}"
        ),
        "cand-1598": (
            "source_ref=index_candidate=cand-1598;index_locator=M.csv#137 p.183; "
            "statement=st-chp7-p183-i13; identity_peers=cand-6799; "
            f"group={EVENT_GROUPS['cand-1598']}; "
            "The index subentry 'opposition of Fronde to' points to the same 1649 First Fronde episode already represented by body candidate cand-6799: the statement explicitly describes the First Fronde turning violently against Mazarin and the temporary setback to his artistic patronage. Retain a new decision for this source candidate but map both candidates to one event identity group. Preserve Haskell's event framing and do not add a standardized event span. "
            f"prior_resolution_note={prior_notes['cand-1598']}"
        ),
        "cand-1599": (
            "source_ref=index_candidate=cand-1599;index_locator=M.csv#138 p.183; "
            "statements=st-chp7-p183-i02,st-chp7-p183-i20; "
            f"group={EVENT_GROUPS['cand-1599']}; "
            "The index subentry denotes Mazarin's purchase of the Bentivoglio palace in Rome. The body states that he bought it soon after 1644; note 2 says the exact date is uncertain but the transaction preceded 1647. No existing event KU represents this purchase. Keep the transaction as a new event identity, distinct from place candidate cand-6796 for the palace itself; do not infer an exact transaction date. "
            f"prior_resolution_note={prior_notes['cand-1599']}"
        ),
    }
    for cid, group in EVENT_GROUPS.items():
        updated_by_id[cid].update(
            decision="new",
            ku_id="",
            process_ref=PROCESS_REF,
            resolution_note=notes[cid],
        )
    updated_by_id["cand-1600"].update(
        decision="excluded",
        ku_id="",
        process_ref=PROCESS_REF,
        resolution_note=(
            "source_ref=index_candidate=cand-1600;index_locator=M.csv#139 p.184,185; "
            "related_statements=st-chp7-p184-i07,st-chp7-p184-i10,st-chp7-p184-i11,st-chp7-p184-i16; "
            "Disposition=exclude from standalone term identity: the index headword 'taste' is a locator for claims about Mazarin's individual artistic preferences and Haskell's comparison with La Vrillière, not a separately named or bounded term in this evidence. Preserve the evaluative claims with the existing Mazarin person candidate cand-1588 and their S2 statement evidence; do not create a generic 'taste' KU or relation. Reopen only if later evidence independently defines a reusable concept. "
            f"prior_resolution_note={prior_notes['cand-1600']}"
        ),
    )

    result_text = RESULT.read_text(encoding="utf-8-sig")
    substitutions = [
        ("new=5,017（4,833个身份组）", "new=5,021（4,840个身份组）"),
        ("conflict=8、excluded=99、undecided=5,506。S4 已登记281组、映射352条成员候选；尚待登记4,552组、4,665条映射。", "conflict=8、excluded=100、undecided=5,501。S4 已登记281组、映射352条成员候选；尚待登记4,559组、4,669条映射。"),
        ("| new | 5,017 | 按 4,833 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,021 | 按 4,840 个当前身份组进入 S4；每组登记一个 KU |"),
        ("| excluded | 99 | 含 48 项 S1 排除及其余 S3 类型/对象边界排除 |", "| excluded | 100 | 含 48 项 S1 排除及其余 S3 类型/对象边界排除 |"),
        ("| undecided | 5,506 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |", "| undecided | 5,501 | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |"),
        ("| **合计** | **1,774→1,026** | **5,017／4,833** | **281／4,552；4,665** | **8** | **99** | **5,506** |", "| **合计** | **1,774→1,026** | **5,021／4,840** | **281／4,559；4,669** | **8** | **100** | **5,501** |"),
        ("| archive | 79→61 | 1,258／1,217 | 29／1,188；1,223 | 0 | 18 | 745 |", "| archive | 79→61 | 1,258／1,221 | 29／1,192；1,223 | 0 | 18 | 745 |"),
        ("| event | 7→7 | 231／228 | 10／218；221 | 0 | 0 | 119 |", "| event | 7→7 | 235／231 | 10／221；225 | 0 | 0 | 115 |"),
        ("| term | 40→34 | 943／930 | 4／926；936 | 0 | 1 | 656 |", "| term | 40→34 | 943／930 | 4／926；936 | 0 | 2 | 655 |"),
    ]
    for old, new in substitutions:
        result_text = replace_once(result_text, old, new)

    result_section = (
        "### S3 event / term：Mazarin 索引事件分组与“taste”去向（2026-10-16）\n\n"
        "- `cand-1594`（M.csv#133）判为 `new`，进入 `sg3-event-cand-1594`：Mazarin 1644年招揽 Bernini 定居法国的尝试，S2 statements `st-chp7-p176-i32`、`st-chp7-p177-i01` 与 `st-chp7-p181-i18` 对应索引页码。它不是 p.181 另一项请 Bernini 扩建 Tubeuf 宫殿的计划。\n"
        "- `cand-1595`（M.csv#134）判为 `new`，进入 `sg3-event-cand-1595`：1648年向 Algardi 提出优厚条件、劝其赴法的单独事件，S2 statements `st-chp7-p182-i20`、`st-chp7-p182-i21`、`st-chp7-p182-i24` 支持。因对象、年代和行动均不同，与 Bernini 事件分组。\n"
        "- `cand-1598`（M.csv#137）判为 `new`，与正文候选 `cand-6799` 共用 `sg3-event-cand-6799`。`st-chp7-p183-i13` 明确对应1649年 First Fronde 反对 Mazarin、使其艺术赞助暂时受挫的同一事件。\n"
        "- `cand-1599`（M.csv#138）判为 `new`，进入 `sg3-event-cand-1599`，表示购入 Bentivoglio 宫殿的交易；`st-chp7-p183-i02` 与 `st-chp7-p183-i20` 记载“1644年后不久”及“确切日期不定、早于1647年”。事件与宫殿 place 候选 `cand-6796` 分开，日期不擅自精确化。\n"
        "- `cand-1600`（M.csv#139）由 `undecided` 改为 `excluded`：`taste` 在该索引语境中是 Mazarin 个人审美偏好的主题定位，不是材料中独立界定的术语实体。相关断言保留在 S2 statements，并关联既有人物候选 `cand-1588`；不建立泛化术语 KU。\n"
        "- 对齐表与 KU 映射交叉核算发现旧摘要少计4个 archive 身份组：按29个已登记 KU 目标和1,192个待登记 group token 计为1,221组；全部类型合计原为4,837组、待登记4,556组。这是计数更正，不是新增语义裁决。本批将4条 event 候选转为 `new`，新增3个身份组；1条 term 候选排除。未登记 KU、卡片或关系；S4 待登记现为4,559组、4,669条成员映射。逐条 `resolution_note` 保存此前未决理由和当前证据。\n\n"
    )
    result_text = replace_once(result_text, "### S4 按类型登记进度", result_section + "### S4 按类型登记进度")

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    knowledge_text += (
        "\n\n### S3 event / term：Mazarin 索引事件分组与“taste”去向（2026-10-16）\n\n"
        "- `cand-1594`（M.csv#133，pp.176、177、181）由 `undecided` 改为 `new`，进入 `sg3-event-cand-1594`。S2 明确记载 Mazarin 于1644年初以高额薪俸劝 Bernini 定居法国；后页记录 Urban VIII 的干预，并概括早期招揽失败。该事件与第181页另一项请 Bernini 扩建 Tubeuf 宫殿的计划分开。无既有同一 event KU。\n"
        "- `cand-1595`（M.csv#134，pp.182–183）由 `undecided` 改为 `new`，进入 `sg3-event-cand-1595`。1648年 Mazarin 亲自致函 Algardi、提出优厚条件以改变其先前拒绝，随后因教宗政策干预而取消法国合同；原文 p.182–183 与 statements `st-chp7-p182-i20/i21/i24` 对应。该事件与1644年 Bernini 招揽行动相隔数年且对象不同，不合并。\n"
        "- `cand-1598`（M.csv#137，p.183）由 `undecided` 改为 `new`，与正文候选 `cand-6799` 并入 `sg3-event-cand-6799`。`st-chp7-p183-i13` 明记 First Fronde 于1649年猛烈反对 Mazarin，并导致其意大利艺术赞助暂时受挫；保留原书事件框架，不补标准化起止日期。\n"
        "- `cand-1599`（M.csv#138，p.183）由 `undecided` 改为 `new`，进入 `sg3-event-cand-1599`，作为 Mazarin 购买 Bentivoglio 宫殿的交易。正文称“soon after 1644”，注2称确切日期不定但早于1647；不据注释推定确日。事件与 place 候选 `cand-6796` 分开。\n"
        "- `cand-1600`（M.csv#139，pp.184–185，subentry `taste`）由 `undecided` 改为 `excluded`。索引词指向 Mazarin 的个人审美偏好及 Haskell 对 La Vrillière 的比较；现有 statements `st-chp7-p184-i07/i10/i11/i16` 以 claims 记录，不界定一个独立、可复用的 term identity。该内容留在 Mazarin 人物与书内断言脉络，不创建泛化的“taste” KU；未来只有出现独立概念界定时才重新立项。\n"
        "- 决定计数：same=1,774，new=5,021（4,840组），conflict=8，excluded=100，undecided=5,501；S4 待登记4,559组、4,669条候选映射。未新建 KU、卡片或正式关系。\n"
    )

    updated_counts = Counter(row["decision"] for row in updated_alignment if not row["external_source"])
    if updated_counts != Counter({"same": 1774, "new": 5021, "conflict": 8, "excluded": 100, "undecided": 5501}):
        raise SystemExit(f"Unexpected post-update decisions: {updated_counts}")
    new_groups = {identity_key(row) for row in updated_alignment if not row["external_source"] and row["decision"] == "new"}
    pending_groups = {group_of(row) for row in updated_alignment if not row["external_source"] and row["decision"] == "new" and not row["ku_id"]}
    if len(new_groups) != 4840 or len(pending_groups) != 4559:
        raise SystemExit(f"Unexpected post-update new groups: total={len(new_groups)}, pending={len(pending_groups)}")
    event_rows = [updated_by_id[cid] for cid in expected_candidates if candidate_by_id[cid]["suggested_type"] == "event"]
    event_groups = {identity_key(row) for row in updated_alignment if not row["external_source"] and row["decision"] == "new" and candidate_by_id[row["candidate_id"]]["suggested_type"] == "event"}
    if len(event_groups) != 231:
        raise SystemExit(f"Unexpected event new-group count after update: {len(event_groups)}")
    if len(event_rows) != 4 or any(row["decision"] != "new" for row in event_rows):
        raise SystemExit("The four event index candidates did not receive new decisions.")

    updates = {
        ALIGNMENT: encode_csv(alignment_headers, updated_alignment, alignment_bom),
        RESULT: ("\ufeff" + result_text).encode("utf-8"),
        KNOWLEDGE: ("\ufeff" + knowledge_text).encode("utf-8"),
    }
    print("PREVIEW" if not args.apply else "APPLY")
    for path, content in updates.items():
        print(f"  {path.relative_to(ROOT)}: {digest(path.read_bytes())} -> {digest(content)}")
    print("  Mazarin event decisions: 4 new candidates / 3 new groups; taste candidate excluded from standalone term identity")
    print("  post-update totals: new=5,021 / 4,840 groups; excluded=100; undecided=5,501; S4 pending=4,559 groups / 4,669 mappings")
    if not args.apply:
        print("Dry-run only; pass --apply to write the changes.")
        return

    for path in updates:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"Recovery copy already exists: {backup}")
        shutil.copy2(path, backup)
        print("  backup:", backup.relative_to(ROOT))
    for path, content in updates.items():
        temporary = path.with_name(path.name + ".tmp-s3-mazarin-index-events-20261016")
        temporary.write_bytes(content)
        temporary.replace(path)
    print("Applied the Mazarin index event and term candidate decisions; recovery copies retained.")


if __name__ == "__main__":
    main()
