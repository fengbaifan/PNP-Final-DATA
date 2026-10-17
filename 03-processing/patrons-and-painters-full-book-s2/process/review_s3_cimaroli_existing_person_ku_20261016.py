from __future__ import annotations

import argparse
import csv
import difflib
import json
import shutil
from io import StringIO
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
DATE = "2026-10-16"
KU_ID = "units/persons/cimaroli"
CARD_REL = "04-knowledge/units/persons/cimaroli.md"
GROUP = "sg3-ku-units-persons-cimaroli"
PRIOR_NEW_GROUP = "new-person:battista-cimaroli-giovan-5c0bd49133"
INDEX_IDS = {
    "cand-0758": "C.csv#282",
    "cand-0759": "C.csv#283",
    "cand-0760": "C.csv#284",
    "cand-0761": "C.csv#285",
    "cand-0762": "C.csv#286",
    "cand-0763": "C.csv#287",
    "cand-0764": "C.csv#288",
}
ACCEPTED_CANDIDATE = "cand-3748"
BACKUP_SUFFIX = ".bak-s3-cimaroli-reuse-20261016"


def contains(value, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(contains(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(contains(item, candidate_id) for item in value)
    return value == candidate_id


def decision_row(rows, candidate_id: str):
    matches = [
        row for row in rows
        if row.get("candidate_id") == candidate_id and not row.get("external_source")
    ]
    assert len(matches) == 1, (candidate_id, len(matches))
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-align Cimaroli index candidates to the accepted Cimaroli person KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_row = next(row for row in manifest if row.get("ku_id") == KU_ID)
    card_path = ROOT / CARD_REL
    assert manifest_row.get("card_path") == CARD_REL
    assert card_path.exists()
    card_text = card_path.read_text(encoding="utf-8-sig")
    assert "Giovanni Battista Cimaroli" in card_text
    assert "Fondazione Federico Zeri" in card_text and "URL69391" in card_text

    _, index_rows = sync.read_csv(ROOT / "02-sources/03-Index/03-2-Index-CSV/C.csv")
    for candidate_id, index_entry_id in INDEX_IDS.items():
        candidate = candidate_by_id[candidate_id]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("canonical_name") == "Cimaroli, Giovan Battista"
        assert candidate.get("index_entry_id") == index_entry_id
        index_row = index_rows[int(index_entry_id.split("#")[1])]
        assert index_row.get("Main Entry") == "Cimaroli, Giovan Battista"
    assert candidate_by_id["cand-0758"].get("index_page_range") == "266, 288, 293, 314"
    assert candidate_by_id["cand-0759"].get("sub_entry") == "share in McSwiny British Worthies"
    assert candidate_by_id["cand-0764"].get("detail") == "(possibly) Lord Stanhope"

    ch9 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    plate = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro_plates_visual-transcription.md").read_text(encoding="utf-8-sig")
    table = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro_notes_p289_visual-transcription.md").read_text(encoding="utf-8-sig")
    assert "Cimatoli" in ch9 and "Cimaroli" in ch10
    assert "Canaletto and Cimaroli painted some of the landscapes" in ch10
    assert "Cimaroli?" in ch10 and "Cimaroli?" in table
    assert "Canaletto, Cimaroli, and Pittoni" in plate

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_hits = {
        candidate_id: [row for row in statements if contains(row, candidate_id)]
        for candidate_id in INDEX_IDS
    }
    assert statement_hits["cand-0758"]
    assert not statement_hits["cand-0759"]
    assert all(statement_hits[cid] for cid in ("cand-0760", "cand-0761", "cand-0762", "cand-0763", "cand-0764"))

    accepted_alignment = decision_row(alignments, ACCEPTED_CANDIDATE)
    assert accepted_alignment.get("decision") == "same"
    assert accepted_alignment.get("ku_id") == KU_ID

    planned = [dict(row) for row in alignments]
    for candidate_id, index_entry_id in INDEX_IDS.items():
        row = decision_row(planned, candidate_id)
        previous_decision = row.get("decision", "")
        previous_note = row.get("resolution_note", "")
        assert previous_decision in {"new", "undecided"}
        assert not row.get("ku_id")
        assert not row.get("external_source")
        assert "S3 Cimaroli reuse review (2026-10-16)" not in previous_note
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = "S3-full-book-2026-10-16"
        row["resolution_note"] = (
            f"source_ref=candidate={candidate_id};index_entry={index_entry_id}; group={GROUP}; "
            f"same-person identity match to existing KU {KU_ID} / {CARD_REL}. "
            "The index gives the explicit personal name ‘Cimaroli, Giovan Battista’; the accepted card records "
            "Giovanni Battista Cimaroli, with Haskell plate 52b and Fondazione Federico Zeri record URL69391 "
            "already documented on that KU. Ch.9 p.266 OCR ‘Cimatoli’ is read against ch.10 pp.288, 293 and "
            "314’s Cimaroli mentions and the existing plate/name anchors. The p.289 note-table subentries and "
            "full artist lists are references to the same named painter. Candidate cand-0764 retains the source’s "
            "‘Cimaroli?’ / ‘possibly Lord Stanhope’ attribution uncertainty; this identity mapping does not "
            "confirm that painting attribution. Candidate cand-0759 has no mapped S2 mention or page locator; "
            "its exact full personal name and McSwiny British Worthies index context support person identity "
            "reuse only, not a new body claim or relation. "
            f"Prior S3 decision retained for audit: {previous_decision}; prior_resolution_note=({previous_note}). "
            "No new external record, KU, work attribution, or formal relation is created; relation candidates "
            "remain for S6."
        )

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_marker = "本轮新增一项身份冲突："
    assert result_text.count(result_marker) == 1
    result_insert = (
        "Cimaroli 索引候选 cand-0758–cand-0764 现统一 same → "
        "[Giovanni Battista Cimaroli 人物卡](../units/persons/cimaroli.md)。索引全名、"
        "第9章 OCR 异写、第10章多项正文／注表锚点与既有图版及 Zeri 身份依据支持同一画家；"
        "cand-0764 的 Stanhope 作品归属问号继续保留，cand-0759 只解决人物身份而无新增正文断言。"
        "此前的 6 条 new 建议组与 1 条 undecided 理由保存在对齐行中；S4 无需重复登记该人物。\n\n"
    )
    result_text = result_text.replace(result_marker, result_insert + result_marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    heading = f"### S3 person：Cimaroli 跨章候选复用既有人物 KU（{DATE}）"
    assert heading not in process_text
    registered = totals["registered_groups"]
    registered_members = totals["registered_members"]
    pending = totals["pending_groups"]
    pending_members = totals["pending_members"]
    process_note = (
        f"\n\n{heading}\n\n"
        "- 对照候选 cand-0758–cand-0764 与既有人物 KU units/persons/cimaroli。七条候选的索引主项均为 “Cimaroli, Giovan Battista”；"
        "cand-0758（C.csv#282）定位 p.266、288、293、314，其中第9章 p.266 OCR 作 Cimatoli，而第10章 p.288、293及既有 p.314／图版锚点均为 Cimaroli。"
        "cand-0760–cand-0764（C.csv#284–288）为 McSwiny British Worthies 注释下的具体主题子目；第10章 p.289 注表将 Cimaroli 与 Lord Somers、William III、Tillotson、Dorset 等行并列，"
        "与正文称 Canaletto、Cimaroli 参与部分风景绘制及既有人物卡记载的图版52b相合。既有卡已记录 Fondazione Federico Zeri URL69391 的作者身份依据；本轮复用，不新增外部行。"
        "cand-0764 的 ‘Cimaroli?’ 与 ‘(possibly) Lord Stanhope’ 只保留其作品归属不确定，不影响该姓名指向既有画家。cand-0759 虽没有映射 S2 提及或页码，但索引全名与同一 McSwiny 子目足以识别人物；不据此新增正文断言或作品关系。"
        "\n- 七条均裁为 same → units/persons/cimaroli，`sg3-ku-units-persons-cimaroli` 仅作复用映射组。cand-0758、cand-0760–cand-0764 原有的六条 new 建议组及 cand-0759 的 undecided 理由逐行保留于 alignment resolution_note；"
        "不新增人物 KU。原书的委托、作品归属及其他关系主张仍待 S6，不写入 relations.csv。"
        f"\n- S3 same 增加7条，new减少6条及1个待登记组，undecided减少1条；当前候选统计由 alignment 重新计算。S4 新组待登记 {sync.fmt(pending)}组/{sync.fmt(pending_members)}条候选；已登记新组 {sync.fmt(registered)}组/{sync.fmt(registered_members)}条成员映射；manifest 保持{len(manifest)} KU。\n"
    )
    process_text += process_note

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=alignment_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(planned)
    outputs = {
        ALIGNMENT: buffer.getvalue(),
        RESULT: result_text,
        PROCESS: process_text,
    }

    for path in outputs:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists(), path
    if args.dry_run:
        for path, updated in outputs.items():
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)),
                tofile=str(path.relative_to(ROOT)) + " (updated)",
                n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: candidates={len(INDEX_IDS)} -> same {KU_ID}; "
            f"mapped_S2_candidates={sum(bool(v) for v in statement_hits.values())}; "
            f"registered={registered}/{registered_members}; pending={pending}/{pending_members}; "
            f"manifest={len(manifest)} unchanged; no external rows or relations added"
        )
        return 0

    backups = []
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, updated in outputs.items():
            path.write_text(updated, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        raise
    print(
        f"applied: candidates={len(INDEX_IDS)} -> same {KU_ID}; "
        f"registered={registered}/{registered_members}; pending={pending}/{pending_members}; "
        f"manifest={len(manifest)} unchanged; backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
