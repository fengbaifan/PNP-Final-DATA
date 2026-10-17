from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
COZZA_CARD_PATH = ROOT / "04-knowledge" / "units" / "persons" / "francesco-cozza.md"

MEMBERS = ("cand-2369", "cand-2372")
KU_ID = "units/persons/sassoferrato"
GROUP = "sg3-ku-units-persons-sassoferrato"
ANCHOR = "s3-sassoferrato-person-crosschapter-20261017"
DATE = "2026-10-17"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/salvi-giovanni-battista-detto-il-sassoferrato_(Dizionario-Biografico)/"
EXTERNAL_SOURCE = "Treccani, Dizionario Biografico degli Italiani"
TYPE_ORDER = ("archive", "event", "family", "institution", "person", "place", "procedure", "term", "work", "untyped")
BT = chr(96)


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
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label}; found {count}")
    return text.replace(old, new, 1)


def candidates_only(rows):
    return [row for row in rows if not row.get("external_source")]


def compute_stats(alignments, candidates):
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_rows = candidates_only(alignments)
    groups = defaultdict(list)
    status = defaultdict(lambda: defaultdict(int))
    for row in candidate_rows:
        typ = candidate_by_id[row["candidate_id"]].get("suggested_type") or "untyped"
        status[typ][row["decision"]] += 1
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            groups[(typ, group)].append(row)
    stats = {}
    for typ in TYPE_ORDER:
        same = [row for row in candidate_rows if (candidate_by_id[row["candidate_id"]].get("suggested_type") or "untyped") == typ and row["decision"] == "same"]
        new = [row for row in candidate_rows if (candidate_by_id[row["candidate_id"]].get("suggested_type") or "untyped") == typ and row["decision"] == "new"]
        new_groups = {get_group(row["resolution_note"]) for row in new}
        registered = {group for group in new_groups if all(row.get("ku_id") for row in groups[(typ, group)])}
        stats[typ] = {
            "same_candidates": len(same),
            "same_kus": len({row["ku_id"] for row in same if row.get("ku_id")}),
            "new_candidates": len(new),
            "new_groups": len(new_groups),
            "registered_groups": len(registered),
            "pending_groups": len(new_groups - registered),
            "pending_candidates": sum(1 for row in new if not row.get("ku_id")),
            "conflict": status[typ]["conflict"],
            "excluded": status[typ]["excluded"],
            "undecided": status[typ]["undecided"],
        }
    return stats


def fmt(value):
    return f"{value:,}"


def type_table(stats, candidate_rows):
    headers = [
        "| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    totals = defaultdict(int)
    for typ in TYPE_ORDER:
        s = stats[typ]
        for key in ("same_candidates", "new_candidates", "new_groups", "registered_groups", "pending_groups", "pending_candidates", "conflict", "excluded", "undecided"):
            totals[key] += s[key]
        headers.append(
            f"| {typ} | {fmt(s['same_candidates'])}→{fmt(s['same_kus'])} | "
            f"{fmt(s['new_candidates'])}／{fmt(s['new_groups'])} | "
            f"{fmt(s['registered_groups'])}／{fmt(s['pending_groups'])}；{fmt(s['pending_candidates'])} | "
            f"{fmt(s['conflict'])} | {fmt(s['excluded'])} | {fmt(s['undecided'])} |"
        )
    same_kus = len({row["ku_id"] for row in candidate_rows if row["decision"] == "same" and row.get("ku_id")})
    headers.append(
        f"| **合计** | **{fmt(totals['same_candidates'])}→{fmt(same_kus)}** | "
        f"**{fmt(totals['new_candidates'])}／{fmt(totals['new_groups'])}** | "
        f"**{fmt(totals['registered_groups'])}／{fmt(totals['pending_groups'])}；{fmt(totals['pending_candidates'])}** | "
        f"**{fmt(totals['conflict'])}** | **{fmt(totals['excluded'])}** | **{fmt(totals['undecided'])}** |"
    )
    return "\n".join(headers)


def resolution_note(candidate_id, old_note):
    if candidate_id == "cand-2369":
        evidence = (
            "Index main entry S.csv#57 gives ‘Sassoferrato (Giovan Battista Salvi)’ at pp.130–131; "
            "the mapped ch.5 p.130–131 mentions and anaphoric references resolve to the painter, including the 1641 commission and Cozza passage. "
        )
    else:
        evidence = (
            "Index sub-entry S.csv#60 is ‘style’ at p.131 beneath the same full person heading ‘Sassoferrato (Giovan Battista Salvi)’. "
            "It locates discussion of this painter’s style; it is not a second person or a separately named style entity, and no unlinked S2 fact is inferred. "
        )
    return (
        f"source_ref=candidate={candidate_id}; group={GROUP}; existing_KU={KU_ID}; {evidence}"
        f"S3 identity correction 2026-10-17: map to the existing person KU. The accepted card gives Giovanni Battista Salvi and Sassoferrato as his usual name; "
        f"Treccani DBI, Silvia Blasio, vol. 90 (2017), heading ‘SALVI, Giovanni Battista, detto il Sassoferrato’ "
        f"({TRECCANI_URL}; accessed {DATE}) directly matches the indexed full-name/epithet form. Identity only; no S2 relation is validated or formalized. "
        f"prior_decision=undecided;prior_resolution_note={old_note}"
    )


def update_process(text, stats):
    if f'<a id="{ANCHOR}"></a>' in text:
        return text
    same_count = sum(row["same_candidates"] for row in stats.values())
    undecided_count = sum(row["undecided"] for row in stats.values())
    entry = f"""

<a id="{ANCHOR}"></a>

### S3 person：Sassoferrato 索引主项与 style 子项复用既有人物（{DATE}）

{BT}cand-2369{BT}（S.csv#57，主项“ Sassoferrato (Giovan Battista Salvi) ”，pp.130–131）由 undecided 改为 same → {KU_ID}。S2 正文 p.130–131 有12条映射到该候选的人名、画家称谓与指代；本次仅决定人物身份，不据此接受全部传记或关系陈述。

{BT}cand-2372{BT}（S.csv#60，子项 style，p.131）也由 undecided 改为 same → {KU_ID}。子项重复同一完整人物主项，只定位其风格讨论；它不是另一人物，也不在没有独立概念锚点时新建风格术语 KU。原 alignment 理由认为缺少全名，现补入索引主项全名及既有别名证据，旧理由作为 prior_resolution_note 保留。

权威身份比对：Treccani DBI，Silvia Blasio，vol. 90（2017），条目标题“ SALVI, Giovanni Battista, detto il Sassoferrato ”（[条目链接]({TRECCANI_URL})，访问：{DATE}）。标题将 Giovanni Battista Salvi 与 Sassoferrato 直接并列，匹配本书索引的 “Giovan Battista Salvi” 及既有人物卡的全名／惯用名。这里只记录身份比对，不导入生平或作品字段；原书人物关系命题仍须按 S6 逐条审查。

两候选并入既有 {BT}{GROUP}{BT} 身份组，与已登记的图版候选 cand-3880 共用同一 KU。cand-2373、cand-2374 是作品候选，未随人物身份合并；Cozza 组中的4条 S2 关系候选仍待 S6，本次未新增正式关系。

S3 现行决定计数：same={fmt(same_count)}（1,031个既有KU）；undecided={fmt(undecided_count)}。S4 登记数不变。
"""
    return text.rstrip() + entry


def update_result(text, stats, candidate_rows, alignment_count, external_count):
    same_count = sum(row["same_candidates"] for row in stats.values())
    same_kus = len({row["ku_id"] for row in candidate_rows if row["decision"] == "same" and row.get("ku_id")})
    undecided_count = sum(row["undecided"] for row in stats.values())
    old_top = re.compile(r"same=[\d,]+（指向[\d,]+个既有 KU）、new=[\d,]+（[\d,]+个身份组）、conflict=[\d,]+、excluded=[\d,]+、undecided=[\d,]+")
    text, n = old_top.subn(
        f"same={fmt(same_count)}（指向{fmt(same_kus)}个既有 KU）、new=4,978（4,804个身份组）、conflict=8、excluded=100、undecided={fmt(undecided_count)}",
        text,
        count=1,
    )
    if n != 1:
        raise AssertionError(f"could not update current S3 totals: {n}")
    align_pattern = re.compile(r"(\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \| )[\d,]+ 条：12,407 条候选决定记录及 [\d,]+ 条外部身份记录；候选决定数见下表 \|")
    text, n = align_pattern.subn(
        lambda match: match.group(1) + f"{fmt(alignment_count)} 条：12,407 条候选决定记录及 {fmt(external_count)} 条外部身份记录；候选决定数见下表 |",
        text,
        count=1,
    )
    if n != 1:
        raise AssertionError(f"could not update alignment count: {n}")
    start = text.find("| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |")
    end = text.find("\n\n本轮新增的 archive 身份组包括：", start)
    if start < 0 or end < 0:
        raise AssertionError("current S3/S4 type summary table not found")
    text = text[:start] + type_table(stats, candidate_rows) + text[end:]
    old_cozza_status = "Sassoferrato " + BT + "cand-2369" + BT + " 仍待证，Domenichino " + BT + "cand-0932" + BT + " 已复用既有 KU。"
    new_cozza_status = "Sassoferrato " + BT + "cand-2369" + BT + " 现复用既有人物 KU，Domenichino " + BT + "cand-0932" + BT + " 已复用既有 KU。"
    text = replace_once(text, old_cozza_status, new_cozza_status, "Cozza current endpoint status")
    section = f"""

### S3 person：Sassoferrato 主项与 style 子项复用既有人物（{DATE}）

{BT}cand-2369{BT}（S.csv#57，pp.130–131）与 {BT}cand-2372{BT}（S.csv#60，style 子项）均在同一人物主项“Giovan Battista Salvi／Sassoferrato”下，现改为 same → [Sassoferrato 人物卡](../units/persons/sassoferrato.md)，并并入 {BT}{GROUP}{BT}。Treccani DBI（Silvia Blasio，vol. 90，2017）条目标题直接列为“Salvi, Giovanni Battista, detto il Sassoferrato”，与索引及既有人物卡的全名、惯用名相合。cand-2372 的 style 是人物主项的主题定位，不另建人物或术语 KU；其无 S2 独立提及的限制保留，未据此抽取风格事实。原 undecided 理由保存在 alignment 行的 prior_resolution_note 中。

本次只解决人物身份；相关 S2 关系候选仍待 S6。作品候选 cand-2373、cand-2374 未并入人物 KU，也未在本次重判。

S3 现行决定计数更新为 same={fmt(same_count)}（指向{fmt(same_kus)}个既有 KU）、undecided={fmt(undecided_count)}；S4 登记进度不变。
"""
    return text.rstrip() + section


def main():
    parser = argparse.ArgumentParser(description="Map Sassoferrato person candidates to the existing person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    _, manifest = read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_rows = {
        cid: [row for row in alignments if row.get("candidate_id") == cid and not row.get("external_source")]
        for cid in MEMBERS
    }
    authority_rows = {
        cid: [row for row in alignments if row.get("candidate_id") == cid and row.get("external_source") == EXTERNAL_SOURCE and row.get("external_id") == TRECCANI_URL]
        for cid in MEMBERS
    }
    if all(len(decision_rows[cid]) == 1 and decision_rows[cid][0].get("decision") == "same" and decision_rows[cid][0].get("ku_id") == KU_ID for cid in MEMBERS):
        assert all(len(authority_rows[cid]) == 1 for cid in MEMBERS)
        print(f"ALREADY APPLIED: {MEMBERS} -> {KU_ID}")
        return 0

    assert len(manifest) == 1542
    assert any(row["ku_id"] == KU_ID and row["card_path"] == "04-knowledge/units/persons/sassoferrato.md" for row in manifest)
    assert candidate_by_id["cand-2369"]["canonical_name"] == "Sassoferrato (Giovan Battista Salvi)"
    assert candidate_by_id["cand-2369"]["index_entry_id"] == "S.csv#57"
    assert candidate_by_id["cand-2372"]["sub_entry"] == "style"
    assert candidate_by_id["cand-2372"]["index_entry_id"] == "S.csv#60"
    assert all(candidate_by_id[cid]["suggested_type"] == "person" for cid in MEMBERS)
    assert all(len(decision_rows[cid]) == 1 and decision_rows[cid][0]["decision"] == "undecided" and not decision_rows[cid][0].get("ku_id") for cid in MEMBERS)
    assert all(not authority_rows[cid] for cid in MEMBERS)

    before = compute_stats(alignments, candidates)
    assert sum(row["same_candidates"] for row in before.values()) == 1849
    assert sum(row["undecided"] for row in before.values()) == 5472
    assert sum(row["registered_groups"] for row in before.values()) == 523
    assert sum(row["pending_groups"] for row in before.values()) == 4281
    assert sum(row["pending_candidates"] for row in before.values()) == 4325

    planned = [dict(row) for row in alignments]
    max_id = max(int(row["alignment_id"].removeprefix("aln-")) for row in planned if row["alignment_id"].removeprefix("aln-").isdigit())
    next_id = max_id
    for cid in MEMBERS:
        decision = next(row for row in planned if row["alignment_id"] == decision_rows[cid][0]["alignment_id"])
        old_note = decision["resolution_note"]
        decision["decision"] = "same"
        decision["ku_id"] = KU_ID
        decision["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        decision["resolution_note"] = resolution_note(cid, old_note)
        next_id += 1
        planned.append({
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": cid,
            "ku_id": KU_ID,
            "external_source": EXTERNAL_SOURCE,
            "external_id": TRECCANI_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: Silvia Blasio, Dizionario Biografico degli Italiani, vol. 90 (2017), heading "
                "‘SALVI, Giovanni Battista, detto il Sassoferrato’ directly identifies the indexed name and epithet as the existing Giovanni Battista Salvi / Sassoferrato KU. "
                "No biographical facts are imported; the style locator does not by itself support a style claim or formal relation."
            ),
        })

    after = compute_stats(planned, candidates)
    candidate_rows = candidates_only(planned)
    assert sum(row["same_candidates"] for row in after.values()) == 1851
    assert sum(row["same_kus"] for row in after.values()) == 1031
    assert sum(row["undecided"] for row in after.values()) == 5470
    assert sum(row["registered_groups"] for row in after.values()) == 523
    assert sum(row["pending_groups"] for row in after.values()) == 4281
    assert sum(row["pending_candidates"] for row in after.values()) == 4325
    assert len(planned) == 12641
    external_count = sum(1 for row in planned if row.get("external_source"))
    assert external_count == 234
    assert sum(1 for row in planned if row["decision"] == "new" and not row.get("ku_id")) == 4340

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    planned_process = update_process(process_text, after)
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    planned_result = update_result(result_text, after, candidate_rows, len(planned), external_count)
    card_text = COZZA_CARD_PATH.read_text(encoding="utf-8-sig")
    old_card_status = "Sassoferrato 身份候选 " + BT + "cand-2369" + BT + " 仍为 " + BT + "undecided" + BT
    new_card_status = "Sassoferrato 身份候选 " + BT + "cand-2369" + BT + " 现复用既有人物卡（" + BT + KU_ID + BT + "）"
    planned_card = replace_once(card_text, old_card_status, new_card_status, "Cozza card endpoint status")

    if args.dry_run:
        print(
            f"dry-run passed: candidates={MEMBERS}; same_after=1851; undecided_after=5470; "
            f"alignment_after={len(planned)}; external_records_after={external_count}; "
            "S4 new registration counts unchanged=523 groups/653 candidates registered, 4281 groups/4325 candidates pending"
        )
        return 0

    write_csv(ALIGNMENT_PATH, fields, planned)
    PROCESS_PATH.write_text(planned_process, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(planned_result, encoding="utf-8-sig", newline="")
    COZZA_CARD_PATH.write_text(planned_card, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: candidates={MEMBERS} same->{KU_ID}; same=1851; undecided=5470; "
        f"alignment={len(planned)}; external_records={external_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
