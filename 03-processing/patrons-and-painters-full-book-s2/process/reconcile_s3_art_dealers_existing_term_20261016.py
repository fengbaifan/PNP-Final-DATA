from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
TARGETS = {"cand-0125", "cand-0126"}
EXISTING_KU = "units/terms/art-dealer"
EXISTING_GROUP = "sg3-ku-units-terms-art-dealer"
OLD_GROUP = "sg3-term-artdealers"
PROCESS_REF = "S3-art-dealers-existing-term-reconciliation-2026-10-16"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def group_of(row):
    match = re.search(r"group=([^;| ]+)", row.get("resolution_note", ""))
    return match.group(1) if match else None


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def metrics(alignment_rows, candidates):
    decisions = decision_rows(alignment_rows)
    counts = Counter(row["decision"] for row in decisions)
    type_counts = Counter(
        (candidates[row["candidate_id"]].get("suggested_type") or "untyped", row["decision"])
        for row in decisions
    )
    new_groups = defaultdict(list)
    for row in decisions:
        if row["decision"] == "new":
            group = group_of(row)
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            new_groups[group].append(row)
    registered = {
        group: rows for group, rows in new_groups.items() if any(row.get("ku_id") for row in rows)
    }
    same_ku_ids = {
        row["ku_id"] for row in decisions if row["decision"] == "same" and row.get("ku_id")
    }
    return {
        "decisions": counts,
        "types": type_counts,
        "new_groups": new_groups,
        "registered_groups": registered,
        "same_ku_ids": same_ku_ids,
    }


def pending_by_type(stats, candidates):
    pending = defaultdict(lambda: [0, 0])
    for group, rows in stats["new_groups"].items():
        if group in stats["registered_groups"]:
            continue
        kind = candidates[rows[0]["candidate_id"]].get("suggested_type") or "untyped"
        pending[kind][0] += 1
        pending[kind][1] += len(rows)
    return pending


def preserve_newlines(path: Path, text: str):
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    encoded = normalized.replace("\n", newline).encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if had_bom else b"") + encoded)


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def format_table(text, stats, candidates):
    types = [
        "archive", "event", "family", "institution", "person",
        "place", "procedure", "term", "untyped", "work",
    ]
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.fullmatch(r"\| ([a-z]+) \|.*\|", line)
        if match and match.group(1) in types:
            kind = match.group(1)
            n_candidates = sum(1 for candidate in candidates.values() if (candidate.get("suggested_type") or "untyped") == kind)
            vals = [stats["types"][(kind, decision)] for decision in ("same", "new", "conflict", "excluded", "undecided")]
            lines[i] = f"| {kind} | {n_candidates:,} | " + " | ".join(f"{value:,}" for value in vals) + " |"
    total = [stats["decisions"][decision] for decision in ("same", "new", "conflict", "excluded", "undecided")]
    old_total = next(i for i, line in enumerate(lines) if line.startswith("| **合计** |"))
    n_candidates = len(candidates)
    lines[old_total] = f"| **合计** | **{n_candidates:,}** | " + " | ".join(f"**{value:,}**" for value in total) + " |"
    return "\n".join(lines)


def revised_process(text, stats, before_stats, endpoint_count, relation_count):
    before_new = before_stats["decisions"]["new"]
    after_new = stats["decisions"]["new"]
    before_groups = len(before_stats["new_groups"])
    after_groups = len(stats["new_groups"])
    after_multi = sum(len(rows) > 1 for rows in stats["new_groups"].values())
    pending_groups = len(stats["new_groups"]) - len(stats["registered_groups"])
    pending_members = after_new - sum(
        sum(bool(row.get("ku_id")) for row in rows)
        for rows in stats["registered_groups"].values()
    )
    text = format_table(text, stats, candidates_by_id)
    text = replace_once(
        text,
        "当前有 1,019 个 `same` KU 组，对应 S3 开始时 manifest 中的全部 1,019 个既有 KU；其中 278 组包含多个候选。S4 新增的 KU 不计入 `same` 组。经跨章复核，4,988 条 `new` 候选当前分为 4,819 个新身份组，其中 133 组含多个候选。",
        f"当前 `same` 候选指向 {len(stats['same_ku_ids']):,} 个既有 KU；S4 新增的 KU 不计入 `same`。经跨章复核，{after_new:,} 条 `new` 候选当前分为 {after_groups:,} 个新身份组，其中 {after_multi:,} 组含多个候选。",
        "process S3 current group summary",
    )
    text = text.replace(
        "之后 Farnese 拆分新增一条人物候选，Dolfin 索引主项由 `undecided` 转入既有家族组，当前为4,989条 `new`、4,820组。",
        "之后 Farnese 拆分新增一条人物候选，Dolfin 索引主项由 `undecided` 转入既有家族组；其后逐类型复核将跨章重复映射至既有 KU、合并同一身份组或保留待证，当前数量以本节表格及下方最新补充裁决为准。",
    )
    text = text.replace("5,615 条 `undecided`", f"{stats['decisions']['undecided']:,} 条 `undecided`")
    text = text.replace(
        "S3 的完成表示候选都已进入明确去向，不表示 5,614 个 `undecided` 的身份已查明，也不把 7 个 `conflict` 当作已解决。当前有 4,988 个 `new` 身份候选、4,819 个新身份组；",
        f"S3 的完成表示候选都已进入明确去向，不表示 {stats['decisions']['undecided']:,} 个 `undecided` 的身份已查明，也不把 {stats['decisions']['conflict']:,} 个 `conflict` 当作已解决。当前有 {after_new:,} 个 `new` 身份候选、{after_groups:,} 个新身份组；",
    )
    text = text.replace(
        "本轮按当前 S3 裁决需登记 4,988 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 4,819 个身份组。",
        f"本轮按当前 S3 裁决需登记 {after_new:,} 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 {after_groups:,} 个身份组；截至本次复核，已登记 {len(stats['registered_groups']):,} 组、{after_new - pending_members:,} 条成员映射，尚待登记 {pending_groups:,} 组、{pending_members:,} 条。",
    )
    section = (
        "\n\n### S3 补充裁决：Art dealers 候选复用既有画商术语 KU（2026-10-16）\n\n"
        f"`cand-0125`（A.csv#126；第5章 pp.120–137）与 `cand-0126`（A.csv#127；第16章 pp.377–378）原属 `new` 组 `{OLD_GROUP}`。两者共对应 {endpoint_count} 条直接 S2 端点陈述，其中 {relation_count} 条标为关系候选。第5章将专业画商作为职业／市场角色，讨论其与画家、买家、交易、税务和经营的关系；第16章以 Celotti 为具体人物并以“some of the humbler dealers so far recorded”回指先前同类画商。现有术语 KU `units/terms/art-dealer` 的范围正是买卖或中介艺术品的职业角色，且涵盖本书相应历史语境；候选没有指向独立命名的组织或边界明确的另一个术语。故两条候选由 `new` 改为 `same`，映射至 `{EXISTING_KU}` 及既有同一性组 `{EXISTING_GROUP}`。原决定与理由逐字保存在 `alignment.csv` 的 `previous_resolution_note`；原书跨章锚点与语义依据如上。本裁决不新增 KU，不改动来源断言、候选关系或正式关系。\n\n"
        f"裁决后 S3 为 same={stats['decisions']['same']:,}、new={after_new:,}（{after_groups:,}组）、undecided={stats['decisions']['undecided']:,}、conflict={stats['decisions']['conflict']:,}、excluded={stats['decisions']['excluded']:,}；S4已登记{len(stats['registered_groups']):,}组/{after_new - pending_members:,}条候选映射，待登记{pending_groups:,}组/{pending_members:,}条。脚本 `{Path(__file__).name}` 以 `--dry-run` 核对后 `--apply` 写回。"
    )
    return text + section


def revised_result(text, stats, candidates, before_stats):
    after_new = stats["decisions"]["new"]
    after_groups = len(stats["new_groups"])
    registered = stats["registered_groups"]
    reg_members = sum(sum(bool(row.get("ku_id")) for row in rows) for rows in registered.values())
    pending_groups = after_groups - len(registered)
    pending_members = after_new - reg_members
    type_pending = pending_by_type(stats, candidates)
    type_summary = "；".join(
        f"{kind} {type_pending[kind][0]:,}组/{type_pending[kind][1]:,}条"
        for kind in ("archive", "event", "family", "institution", "person", "place", "procedure", "term", "work")
    )
    # Refresh the current-state line without rewriting its dated historical narrative.
    text = replace_once(
        text,
        "same=1,715（指向1,025个既有 KU）、new=5,008（4,836个身份组）",
        f"same={stats['decisions']['same']:,}（指向{len(stats['same_ku_ids']):,}个既有 KU）、new={after_new:,}（{after_groups:,}个身份组）",
        "result current S3 status",
    )
    text = replace_once(
        text,
        "尚待登记4,671组、4,796条映射",
        f"尚待登记{pending_groups:,}组、{pending_members:,}条映射",
        "result current S4 pending status",
    )
    text = replace_once(
        text,
        "当前尚余4,657个 `new` 身份组、4,781条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,178条候选，已登记56组、94条候选，待登记1,030组、1,084条候选。",
        f"当前有{after_groups:,}个 `new` 身份组、{after_new:,}条成员候选映射；S4已登记{len(registered):,}组、{reg_members:,}条候选映射，尚待登记{pending_groups:,}组、{pending_members:,}条。按类型待登记：{type_summary}。",
        "result S4 current per-type status",
    )
    section = (
        "\n\n### S3 补充裁决：Art dealers 候选复用既有画商术语 KU（2026-10-16）\n\n"
        f"`cand-0125`（A.csv#126；第5章 pp.120–137）与 `cand-0126`（A.csv#127；第16章 pp.377–378）从新身份组改为复用 `units/terms/art-dealer`。第5章用职业角色描述画商，第16章将 Celotti 与此前记述的画商直接比较；现有术语卡的对象边界涵盖该历史职业角色，未发现独立组织或不同术语边界。两条原决定与理由保存在对齐行 `previous_resolution_note` 中。逐项比较与来源锚点见[处理记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)及[复核脚本](../../03-processing/patrons-and-painters-full-book-s2/process/{Path(__file__).name})。裁决后 same={stats['decisions']['same']:,}、new={after_new:,}（{after_groups:,}组）；S4待登记{pending_groups:,}组/{pending_members:,}条映射。未新增 KU 或正式关系。"
    )
    return text + section


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="validate and preview without writing")
    mode.add_argument("--apply", action="store_true", help="write the reviewed S3 correction")
    args = parser.parse_args()

    align_fields, alignment_rows = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(CANDIDATES_PATH)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    global candidates_by_id
    candidates_by_id = candidates
    decisions = decision_rows(alignment_rows)
    rows_by_id = {row["candidate_id"]: row for row in decisions}
    assert TARGETS <= rows_by_id.keys()
    assert all(rows_by_id[cid]["decision"] == "new" for cid in TARGETS)
    assert all(group_of(rows_by_id[cid]) == OLD_GROUP for cid in TARGETS)
    assert all(not rows_by_id[cid].get("ku_id") for cid in TARGETS)
    assert all(candidates[cid]["suggested_type"] == "term" for cid in TARGETS)

    statement_rows = [json.loads(line) for line in STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines() if line]
    direct = [
        row for row in statement_rows
        if row.get("subject_candidate_id") in TARGETS or row.get("object_candidate_id") in TARGETS
    ]
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in direct)
    assert len(direct) == 28, f"expected 28 direct S2 endpoints, found {len(direct)}"
    assert relation_count == 23, f"expected 23 relation candidates, found {relation_count}"
    assert any(row.get("statement_id") == "st-chp5-p120-dealer-growth" for row in direct)
    assert any(row.get("statement_id") == "st-chp16-p377-haskell-infers-celotti-salesmanship-and-taste" for row in direct)
    existing_row = next(
        row for row in decisions
        if row.get("ku_id") == EXISTING_KU and row.get("decision") == "same"
        and group_of(row) == EXISTING_GROUP
    )
    assert existing_row["candidate_id"] == "cand-3149"
    card_path = ROOT / "04-knowledge" / "units" / "terms" / "art-dealer.md"
    card = card_path.read_text(encoding="utf-8-sig")
    assert "type: term" in card and "画商（Art dealer）" in card

    before = metrics(alignment_rows, candidates)
    for candidate_id in TARGETS:
        row = rows_by_id[candidate_id]
        old_note = row["resolution_note"]
        row["decision"] = "same"
        row["ku_id"] = EXISTING_KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"group={EXISTING_GROUP}; source_ref=chp-5:05_CHP-5_sec_i:pp.120-137; "
            "chp-16:16_CHP-16_intro:pp.377-378; existing_ku=04-knowledge/units/terms/art-dealer.md; "
            "rationale=Both index candidates denote the same occupational/market role already expressed by the source-backed term KU; chp-16 explicitly compares Celotti with dealers recorded earlier; no separate organization or distinct term boundary is asserted; "
            f"previous_decision=new; previous_resolution_note={json.dumps(old_note, ensure_ascii=False)}"
        )
    after = metrics(alignment_rows, candidates)
    assert after["decisions"]["same"] == before["decisions"]["same"] + 2
    assert after["decisions"]["new"] == before["decisions"]["new"] - 2
    assert len(after["new_groups"]) == len(before["new_groups"]) - 1
    assert after["decisions"]["undecided"] == before["decisions"]["undecided"]
    assert after["decisions"]["conflict"] == before["decisions"]["conflict"]
    assert after["decisions"]["excluded"] == before["decisions"]["excluded"]
    assert all(rows_by_id[cid]["ku_id"] == EXISTING_KU for cid in TARGETS)

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    updated_process_text = revised_process(process_text, after, before, len(direct), relation_count)
    updated_result_text = revised_result(result_text, after, candidates, before)

    print(f"decision counts: {dict(after['decisions'])}")
    print(f"new groups: {len(after['new_groups'])}; S4 registered: {len(after['registered_groups'])}")
    print(f"S4 pending: {len(after['new_groups']) - len(after['registered_groups'])} groups / {after['decisions']['new'] - sum(sum(bool(row.get('ku_id')) for row in rows) for rows in after['registered_groups'].values())} candidates")
    print(f"direct S2 statements: {len(direct)}; relation candidates: {relation_count}")
    pending_types = pending_by_type(after, candidates)
    print("S4 pending by type:")
    for kind in ("archive", "event", "family", "institution", "person", "place", "procedure", "term", "work"):
        print(f"  {kind}: {pending_types[kind][0]} groups / {pending_types[kind][1]} candidates")
    for candidate_id in sorted(TARGETS):
        print(f"{candidate_id}: new/{OLD_GROUP} -> same/{EXISTING_KU}")
        print(f"  {rows_by_id[candidate_id]['resolution_note']}")
    if args.apply:
        # Serialize and validate the alignment payload before replacing the source table.
        output = StringIO(newline="")
        raw = ALIGNMENT_PATH.read_bytes()
        line_ending = "\r\n" if b"\r\n" in raw else "\n"
        writer = csv.DictWriter(output, fieldnames=align_fields, lineterminator=line_ending)
        writer.writeheader()
        writer.writerows(alignment_rows)
        bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        ALIGNMENT_PATH.write_bytes(bom + output.getvalue().encode("utf-8"))
        preserve_newlines(PROCESS_PATH, updated_process_text)
        preserve_newlines(RESULT_PATH, updated_result_text)
        print("applied: alignment.csv, process/knowledge.md, current results")
    else:
        print("dry-run only; no files changed")


if __name__ == "__main__":
    main()
