from __future__ import annotations

import argparse
import csv
import difflib
import json
import shutil
from collections import Counter
from io import StringIO
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE = "cand-6051"
GROUP = "sg3-event-cand-6051"
S_GIOVANNI_SERIES = "cand-6039"
S_GIOVANNI_1675 = "cand-11768"
S_SALVATORE_1675 = "cand-11770"
S_SALVATORE_1697 = "cand-11771"
S_SALVATORE_1701 = "cand-11942"
UNRESOLVED_1708 = "cand-11783"
UNRESOLVED_CLOISTERS = "cand-6053"
ART_EXHIBITIONS_TERM = "cand-0134"
CHURCHES_PLACE = "cand-0720"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s3-salvatore-lauro-event-series-20261016"


def decision_row(rows, candidate_id: str):
    matches = [
        row for row in rows
        if row.get("candidate_id") == candidate_id and not row.get("external_source")
    ]
    assert len(matches) == 1, (candidate_id, len(matches))
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review the cross-chapter identity boundary of the S. Salvatore in Lauro exhibition series."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidates = list(csv.DictReader(stream))
    with ALIGNMENT.open(encoding="utf-8-sig", newline="") as stream:
        alignment_fields = list(csv.DictReader(stream).fieldnames or [])
        stream.seek(0)
        alignments = list(csv.DictReader(stream))
    with MANIFEST.open(encoding="utf-8-sig", newline="") as stream:
        manifest = list(csv.DictReader(stream))

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    target = decision_row(alignments, CANDIDATE)
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "event"
    assert candidate_by_id[CANDIDATE]["canonical_name"] == "Regular exhibition at S. Salvatore in Lauro, Rome"
    assert target["decision"] == "new" and not target["ku_id"]
    assert sync.get_group(target["resolution_note"]) == GROUP

    decisions = {
        cid: decision_row(alignments, cid)
        for cid in [
            S_GIOVANNI_SERIES, S_GIOVANNI_1675, S_SALVATORE_1675, S_SALVATORE_1697,
            S_SALVATORE_1701, UNRESOLVED_1708, UNRESOLVED_CLOISTERS,
            ART_EXHIBITIONS_TERM, CHURCHES_PLACE,
        ]
    }
    assert candidate_by_id[S_GIOVANNI_SERIES]["suggested_type"] == "event"
    assert decisions[S_GIOVANNI_SERIES]["decision"] == "new"
    assert decisions[S_GIOVANNI_SERIES]["ku_id"] == "units/events/annual-exhibition-s-giovanni-decollato"
    for cid in [S_SALVATORE_1675, S_SALVATORE_1697, S_SALVATORE_1701]:
        assert candidate_by_id[cid]["suggested_type"] == "event"
        assert decisions[cid]["decision"] == "new" and not decisions[cid]["ku_id"]
    assert decisions[S_GIOVANNI_1675]["decision"] == "new"
    assert decisions[S_GIOVANNI_1675]["ku_id"] == "units/events/s-giovanni-decollato-exhibition-1675"
    assert decisions[UNRESOLVED_1708]["decision"] == "undecided"
    assert decisions[UNRESOLVED_CLOISTERS]["decision"] == "undecided"
    assert candidate_by_id[ART_EXHIBITIONS_TERM]["suggested_type"] == "term"
    assert candidate_by_id[CHURCHES_PLACE]["suggested_type"] == "place"

    ch5 = (ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md").read_text(encoding="utf-8-sig")
    ch8 = (ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    assert "There was one more regular art exhibition" in ch5
    assert "the anniversary of the arrival of the Holy House in Loreto on 10 December" in ch5
    assert "the exhibitions in S. Salvatore in Lauro were organised far more professionally" in ch5
    assert "Thus in 1697 Prince Pio agreed to lend his pictures" in ch5
    assert "We find a similar situation in 1708" in ch5
    assert "among those lent to the exhibition in S. Salvatore in Lauro in 1704" in ch8

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    relation_candidates = [
        row for row in direct
        if row.get("qualifiers", {}).get("relation_candidate") is True
    ]
    chapters = sorted({
        row.get("segment_id", "").split(":")[0]
        for row in direct
        if row.get("segment_id", "").startswith("chp-")
    })
    assert len(direct) == 12 and len(relation_candidates) == 5
    assert chapters == ["chp-5", "chp-8"]

    planned = [dict(row) for row in alignments]
    planned_target = decision_row(planned, CANDIDATE)
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] += (
        " S3 cross-chapter event identity review (2026-10-16): ch.5 p.128 describes the regular picture-exhibition series at "
        "S. Salvatore in Lauro for the Marchigian community, held around 10 December for the anniversary of the Holy House's "
        "arrival in Loreto; the text says its arrangements and display practices varied across years. Ch.8 p.222 separately "
        "reports a portrait lent to an exhibition at the same venue in 1704 and links the mention to this series candidate. "
        "The identity represented by this candidate is the recurring series, not any one dated occurrence. Preserve cand-11770 "
        "(1675) and cand-11771 (1697) as distinct events within the series; cand-11942 (1701, same venue) remains a distinct new "
        "event because the source does not establish that it was an instance of the December series. The 1708 'similar situation' "
        "cand-11783 remains undecided because the continuation does not restate the venue or series. Keep the separate S. Giovanni "
        "Decollato series cand-6039 and its 1675 occurrence cand-11768 distinct. The venue/cloisters candidate cand-6053 remains "
        "undecided as a place; the general term cand-0134 and the churches place candidate cand-0720 are not aliases for the event. "
        "No same-type existing event KU represents this recurring series. Keep cand-6051 new/pending S4; do not convert the five "
        "S2 relation candidates into formal relations by this identity review."
    )

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidates)
    assert len(manifest) == 1300
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_marker = "### S4 按类型登记进度"
    assert result_text.count(result_marker) == 1
    result_note = (
        f"复核 event 候选 {CANDIDATE}：第5章将 S. Salvatore in Lauro 描述为十二月循环展览，第8章记录同一地点的1704年展览。"
        f"保留 {GROUP} 为“系列”身份；1675、1697 和 1701 年展览候选分别保持独立新事件，其中 cand-11942 未证明属于十二月系列；"
        "1708 年相似展览 cand-11783 仍待证。S. Giovanni Decollato 系列和其1675年展览不合并；修道院回廊位置 cand-6053 保持 undecided。"
        f"{len(relation_candidates)}条关系候选仍待 S6。\n\n"
    )
    assert f"复核 event 候选 {CANDIDATE}" not in result_text
    result_text = result_text.replace(result_marker, result_note + result_marker, 1)

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig").rstrip()
    heading = "### S3 event：S. Salvatore in Lauro 循环展览系列身份复核（2026-10-16）"
    assert heading not in process_text
    process_text += (
        f"\n\n{heading}\n\n"
        f"- event 候选 {CANDIDATE} 保持 {GROUP} 的独立 new 决定，KU 待 S4。第5章 p.128 以“one more regular art exhibition”引出 S. Salvatore in Lauro，"
        "说明 Marchigian 群体在12月10日庆祝 Loreto 圣屋迁来周年时举行画展，并叙述展品留置10–11日、借展安排与年度数量浮动。"
        "第8章 p.222 另记一幅 Velázquez 的 Juan de Pareja 肖像于1704年借展至同一地点。候选身份是循环系列，不与任一日期的单次展览同一化。\n"
        f"- 保留既有去向：cand-11770（1675）、cand-11771（1697）为该系列下各自独立的新 event；cand-11942（1701，同一地点）继续是独立 new event，"
        "因来源未证明它属于12月周年系列。cand-11783 的1708年“similar situation”未重述地点或系列，保持 undecided。另一系列 cand-6039（S. Giovanni Decollato）"
        "及其1675年实例 cand-11768 分别保留；place cand-6053（回廊）身份 undecided；term cand-0134 与 place cand-0720 分别保持各自类型，不并入事件。\n"
        f"- 该候选的{len(direct)}条直接 S2 陈述中{len(relation_candidates)}条为关系候选，留待 S6；本轮未新增外部身份行、KU、卡片或正式关系。"
        "S2 对1704借展的端点保持原记录，本轮不将其扩展为新的 event 候选。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=alignment_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(planned)
    updated = {
        ALIGNMENT: buffer.getvalue(),
        RESULT: result_text,
        KNOWLEDGE: process_text,
    }
    for path in updated:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists(), path

    before_decisions = [
        row for row in alignments if row.get("candidate_id") and not row.get("external_source")
    ]
    after_decisions = [
        row for row in planned if row.get("candidate_id") and not row.get("external_source")
    ]
    assert Counter(row["decision"] for row in before_decisions) == Counter(row["decision"] for row in after_decisions)
    assert decision_row(planned, CANDIDATE)["decision"] == "new"
    assert decision_row(planned, CANDIDATE)["ku_id"] == ""

    if args.dry_run:
        for path, content in updated.items():
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), content.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE} remains new/pending S4 in {GROUP}; chapters={chapters}; "
            f"direct_statements={len(direct)} relation_candidates_pending={len(relation_candidates)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']} "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged"
        )
        return 0

    backups = []
    for path in updated:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, content in updated.items():
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(path, backup)
        raise
    print(
        f"applied: {CANDIDATE} remains new/pending S4 in {GROUP}; chapters={chapters}; "
        f"relation_candidates_pending={len(relation_candidates)}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']} pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(manifest)} unchanged; recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
