from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CONTl_KU = "units/works/g-m-crespi-jupiter-handed-over-by-cybele-to-the-corybantes-to-be-fed"
OLD_GROUP = "workgrp-beb5c6c0eb0cbc"
RUFFO_GROUP = "workgrp-ruffo-crespi-finding-of-moses-p222"
INDEX_CANDIDATE = "cand-0879"
RUFFO_CANDIDATE = "cand-7720"
PLATE_CANDIDATE = "cand-4040"
DATE = "2026-10-17"
S3_ANCHOR = "s3-crespi-finding-moses-same-title-split-20261017"
OLD_SECTION_REF = "same_title_crespi_work_group_reversed"
S3_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{S3_ANCHOR}"
SOURCE_CH8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE_CH20 = "02-sources/02-Markdown/20_CHP-20Postscript.md"
EXISTING_CARD_REL = f"04-knowledge/{CONTl_KU}.md"
STMT_222 = "st-chp8-p222-ruffo-commissioned-finding-of-moses"
STMT_228_SKETCH = "st-chp8-p228-crespi-chosen-subject-sketch"
STMT_228_RETITLE = "st-chp8-p228-crespi-retitles-finding-of-moses"
STMT_405 = "st-chp20-p405-conti-crespi-jupiter-commission-found"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    old = path.read_bytes() if path.exists() else b""
    bom = b"\xef\xbb\xbf" if old.startswith(b"\xef\xbb\xbf") else b""
    path.write_bytes(bom + text.encode("utf-8"))


def render_csv(fieldnames, rows) -> str:
    import csv
    import io

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def show_diff(path: str, old: str, new: str) -> None:
    diff = difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    )
    print("".join(diff), end="")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"expected one {label} marker, found {count}"
    return text.replace(old, new, 1)


def transform_jsonl(text: str, updates: dict[str, callable]) -> tuple[str, set[str]]:
    lines = text.splitlines()
    trailing_newline = text.endswith("\n")
    seen: set[str] = set()
    output: list[str] = []
    for line in lines:
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id", "")
        if statement_id in updates:
            updates[statement_id](row)
            seen.add(statement_id)
            output.append(json.dumps(row, ensure_ascii=False))
        else:
            output.append(line)
    return "\n".join(output) + ("\n" if trailing_newline else ""), seen


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct S3 for two Crespi works sharing the title The Finding of Moses.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(CANDIDATE_PATH)
    mention_fields, mentions = sync.read_csv(MENTION_PATH)
    _, manifest = sync.read_csv(ROOT / "04-knowledge" / "tables" / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert {INDEX_CANDIDATE, RUFFO_CANDIDATE, PLATE_CANDIDATE}.issubset(candidate_by_id)
    assert candidate_by_id[INDEX_CANDIDATE]["suggested_type"] == "work"
    assert candidate_by_id[RUFFO_CANDIDATE]["suggested_type"] == "work"
    assert any(row.get("ku_id") == CONTl_KU and row.get("card_path") == EXISTING_CARD_REL for row in manifest)
    assert (ROOT / EXISTING_CARD_REL).exists()
    assert alignment_by_id[PLATE_CANDIDATE]["decision"] == "same"
    assert alignment_by_id[PLATE_CANDIDATE]["ku_id"] == CONTl_KU

    current_group = {
        cid for cid, row in alignment_by_id.items()
        if row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == OLD_GROUP
    }
    already_applied = (
        alignment_by_id[INDEX_CANDIDATE]["decision"] == "same"
        and alignment_by_id[INDEX_CANDIDATE].get("ku_id") == CONTl_KU
        and alignment_by_id[RUFFO_CANDIDATE]["decision"] == "new"
        and sync.get_group(alignment_by_id[RUFFO_CANDIDATE].get("resolution_note", "")) == RUFFO_GROUP
        and f"prior_group_id={OLD_GROUP}" in alignment_by_id[RUFFO_CANDIDATE].get("resolution_note", "")
    )
    if already_applied:
        print(f"ALREADY APPLIED: {INDEX_CANDIDATE} -> same {CONTl_KU}; {RUFFO_CANDIDATE} remains new in {RUFFO_GROUP}.")
        return 0
    assert RUFFO_GROUP not in {sync.get_group(row.get("resolution_note", "")) for row in alignments}
    assert current_group == {INDEX_CANDIDATE, RUFFO_CANDIDATE}, current_group
    assert alignment_by_id[INDEX_CANDIDATE]["decision"] == "new" and not alignment_by_id[INDEX_CANDIDATE].get("ku_id")
    assert alignment_by_id[RUFFO_CANDIDATE]["decision"] == "new" and not alignment_by_id[RUFFO_CANDIDATE].get("ku_id")
    assert "same Crespi painting as candidate cand-7720" in candidate_by_id[INDEX_CANDIDATE].get("detail", "")
    assert "same Crespi painting as index candidate cand-0879" in candidate_by_id[RUFFO_CANDIDATE].get("detail", "")

    process = read_text(PROCESS_PATH)
    result = read_text(RESULT_PATH)
    assert S3_ANCHOR not in process
    assert OLD_SECTION_REF not in result
    ch8 = " ".join((ROOT / SOURCE_CH8).read_text(encoding="utf-8-sig").split())
    ch20 = " ".join((ROOT / SOURCE_CH20).read_text(encoding="utf-8-sig").split())
    assert "Crespi was represented by four works, two of which were commissioned during Russo’s legateship" in ch8
    assert "Abigail giving Presenti to David and The Finding of Moses" in ch8
    assert "The Infant Jupiter handed over by Cybele to the Corybantes to be fed" in ch8
    assert "changed the title to The Finding of Moses, as sacred pictures paid lower customs duty" in ch8
    assert "Stefano Conti’s last commission—a picture by Crespi of Jupiter among the Corybantes" in ch20
    assert "cunningly described by him as The Finding of Moses because" in ch20

    source_quote_correction = False
    statement_rows = [json.loads(line) for line in read_text(STATEMENT_PATH).splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    assert {STMT_222, STMT_228_SKETCH, STMT_228_RETITLE, STMT_405}.issubset(statement_by_id)
    for correction in (statement_by_id[STMT_222].get("qualifiers", {}).get("ocr_corrections") or []):
        if correction.get("ocr") == "Russo’s" and correction.get("print") == "Ruffo’s":
            source_quote_correction = True
    assert source_quote_correction, "the S2 page-image correction from Russo to Ruffo must be present"

    planned_alignments = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignments if row.get("candidate_id")}
    index_alignment = planned_by_id[INDEX_CANDIDATE]
    prior_index_note = index_alignment.get("resolution_note", "")
    prior_ruffo_note = planned_by_id[RUFFO_CANDIDATE].get("resolution_note", "")
    index_alignment["decision"] = "same"
    index_alignment["ku_id"] = CONTl_KU
    index_alignment["process_ref"] = "S3-crespi-distinct-same-title-works-2026-10-17"
    index_alignment["resolution_note"] = (
        "source_ref=chp-8:08_CHP-8_sec_ii:l206-214#L210; "
        "cross_chapter_source=chp-20:20_CHP-20Postscript:l137-148#L138; identity_peer=cand-4040; "
        f"prior_decision=new; prior_group_id={OLD_GROUP}; current_decision=same; "
        "p.228 and p.405 identify the Stefano Conti commission as the Jupiter/Cybele painting; its Finding of Moses wording is the customs-duty title. "
        "The subject and Plate 67 title match the existing work KU, whose Zeri record identifies Stuttgart inv.3294 and whose DBI source records the Conti commission. "
        "Do not merge with cand-7720: p.222 names a separate Crespi work in the Ruffo commission context under the same title. "
        f"Reuse {CONTl_KU}; no external identifier is assigned to this candidate."
    )

    ruffo_alignment = planned_by_id[RUFFO_CANDIDATE]
    ruffo_alignment["decision"] = "new"
    ruffo_alignment["ku_id"] = ""
    ruffo_alignment["process_ref"] = "S3-crespi-distinct-same-title-works-2026-10-17"
    ruffo_alignment["resolution_note"] = (
        "source_ref=chp-8:08_CHP-8_sec_ii:l126-138#L135; identity_peer=cand-0879; "
        f"prior_decision=new; prior_group_id={OLD_GROUP}; group={RUFFO_GROUP}; current_decision=new; "
        "The p.222 passage identifies a separate Crespi work titled The Finding of Moses among works commissioned during Ruffo’s legateship; "
        "S2 records the page-image correction from OCR Russo’s to Ruffo’s. The p.228/p.405 Conti painting has a different Jupiter/Cybele subject "
        "and uses the same title as a customs-duty label. Same title does not establish same work. No exact same-work KU exists for this p.222 object; "
        "do not infer a date, medium, or present location."
    )

    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    planned_candidate_by_id[INDEX_CANDIDATE]["detail"] = (
        "S3 correction 2026-10-17: p.228 and the p.405 postscript refer to the Stefano Conti Jupiter/Cybele painting; "
        "The Finding of Moses is its customs-duty title. Reuse the existing Plate 67 work KU. Keep distinct from the separate p.222 Ruffo work, "
        "which bears the same title."
    )
    planned_candidate_by_id[RUFFO_CANDIDATE]["detail"] = (
        "S3 correction 2026-10-17: the p.222 The Finding of Moses is a separate Crespi work in the Ruffo commission context. "
        "Do not merge with the p.228 Stefano Conti Jupiter/Cybele painting, for which the same wording was used as a customs-duty title."
    )

    mention_updates = {
        "m-chp8-p222-finding-moses-work": (
            "Named Crespi painting in the p.222 Ruffo commission context. S3 resolved: distinct from the p.228 Conti work that used the same title as a customs-duty label."
        ),
        "m-chp8-p228-finding-title": (
            "Title used for the same 1728 Conti Jupiter/Cybele commission; S3 distinguishes it from the separate p.222 Ruffo work with the same title."
        ),
        "m-chp20-p405-003": (
            "Specific Conti painting; reuse the p.228 index and Plate 67 work candidate. S3 resolves the p.222 same-title Ruffo painting as a separate work."
        ),
    }
    planned_mentions = [dict(row) for row in mentions]
    mention_by_id = {row["mention_id"]: row for row in planned_mentions}
    assert set(mention_updates).issubset(mention_by_id)
    for mention_id, note in mention_updates.items():
        assert mention_by_id[mention_id]["candidate_id"] in {INDEX_CANDIDATE, RUFFO_CANDIDATE}
        mention_by_id[mention_id]["note"] = note

    def update_statement_222(row):
        q = row.setdefault("qualifiers", {})
        q["relation_candidate_note"] = (
            "The p.222 Ruffo-commissioned Finding of Moses is distinct from the p.228 Stefano Conti Jupiter/Cybele painting, "
            "which used the same title as a customs-duty label. The S2 relation candidate remains pending S6."
        )

    def update_statement_228_sketch(row):
        q = row.setdefault("qualifiers", {})
        q["qualification"] = (
            "This is the p.228 Stefano Conti commission. Haskell identifies its Jupiter/Cybele subject and explains that The Finding of Moses "
            "was the customs-duty title; the separate p.222 Ruffo commission has the same title but is a distinct work."
        )
        q["identity_review"] = "resolved_distinct_same_title_work"

    def update_statement_228_retitle(row):
        q = row.setdefault("qualifiers", {})
        q["qualification"] = (
            "Haskell's explanation is retained as reported motive. This title belongs to the p.228 Conti Jupiter/Cybele commission; "
            "the p.222 Ruffo work with the same title is a separate painting."
        )

    def update_statement_405(row):
        q = row.setdefault("qualifiers", {})
        q["qualification"] = (
            "Map the p.405 referent to the p.228 Conti painting and Plate 67. The p.222 Ruffo commission is a separate Crespi work "
            "with the same title; the title alone does not indicate identity. The cited documentary source and present location were not independently checked."
        )
        q.pop("related_candidate_ids_pending_alignment", None)

    statement_updates = {
        STMT_222: update_statement_222,
        STMT_228_SKETCH: update_statement_228_sketch,
        STMT_228_RETITLE: update_statement_228_retitle,
        STMT_405: update_statement_405,
    }
    old_statements_text = read_text(STATEMENT_PATH)
    new_statements_text, seen_statements = transform_jsonl(old_statements_text, statement_updates)
    assert seen_statements == set(statement_updates), seen_statements

    process_addition = (
        f"\n\n<a id=\"{S3_ANCHOR}\"></a>\n\n"
        "### S3 work：Crespi 两件同名《The Finding of Moses》作品分组更正（2026-10-17）\n\n"
        "本节更正此前把 cand-0879 与 cand-7720 合并为同一幅 Crespi 画的决定。原组仅据同名题名及跨段指针判断身份，忽略了原书明确区分的委托与题材；旧判断与完整语境不符，保留在下方历史记录，不再作为当前裁决。\n\n"
        f"- cand-0879：改为 same，映射至既有 {CONTl_KU}。第8章 p.228 与第20章后记 p.405 均把 Conti 的委托识别为 Jupiter/Cybele 题材；Haskell明确说明《The Finding of Moses》是为降低关税而使用的发货题名。图版67的题名及既有 KU 的题材、Stuttgart inv.3294 与 Conti 委托信息相合。\n"
        f"- cand-7720：保持 new，单独归入 {RUFFO_GROUP}，待 S4 登记。第8章 p.222 将《The Finding of Moses》列为 Crespi 在 Ruffo 任使期间受委托的宗教题材作品之一；该画与 p.228 的 Conti Jupiter/Cybele 画是不同作品。p.222 OCR作 Russo’s，S2页图核对已校正为 Ruffo’s。未推断该画的具体年份、媒材或现藏地。\n\n"
        "两件作品共享同一英文题名，但 p.222 的委托语境与 p.228/p.405 的 Jupiter/Cybele 题材及避税改题记录形成明确区分；本次不是 unresolved conflict。cand-7720 的一条书内委托关系候选仍待 S6；本次不新增正式关系。\n\n"
        "#### 更正前 alignment 与候选说明（保留历史）\n\n"
        f"- {INDEX_CANDIDATE} 原 alignment：{prior_index_note}\n"
        f"- {RUFFO_CANDIDATE} 原 alignment：{prior_ruffo_note}\n"
        f"- {INDEX_CANDIDATE} 原 candidate detail：{candidate_by_id[INDEX_CANDIDATE].get('detail', '')}\n"
        f"- {RUFFO_CANDIDATE} 原 candidate detail：{candidate_by_id[RUFFO_CANDIDATE].get('detail', '')}\n"
    )
    old_process = process
    new_process = process.rstrip() + process_addition

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(values[key] for values in stats.values()) for key in next(iter(stats.values()))}
    new_result = sync.update_result(result, stats, totals, len(manifest)).rstrip()
    new_result += (
        "\n\n### S3 work：Crespi 两件同名《The Finding of Moses》作品分组更正（2026-10-17）\n\n"
        f"{INDEX_CANDIDATE} 改为 same，映射至既有 Jupiter/Cybele 作品卡；{RUFFO_CANDIDATE} 保持 new，另成组 {RUFFO_GROUP}。"
        "原并组只凭同名题名，忽略了 p.222 Ruffo 委托与 p.228/p.405 Conti Jupiter/Cybele 委托及避税改题的差别；现依据完整书内语境拆分。"
        "S3 当前候选去向均有决定记录；本次新增候选仍待 S4 登记。S6关系候选不在本次转正。\n\n"
        f"当前 same={sync.fmt(totals['same_candidates'])}，new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组），"
        f"conflict={sync.fmt(totals['conflict'])}，undecided={sync.fmt(totals['undecided'])}；"
        f"S4已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(manifest))}。"
    )

    if args.dry_run:
        print(f"S3 correction: {INDEX_CANDIDATE} -> same {CONTl_KU}; {RUFFO_CANDIDATE} -> new group {RUFFO_GROUP}.")
        print(f"Counts: same={totals['same_candidates']}, new={totals['new_candidates']}/{totals['new_groups']} groups, "
              f"conflict={totals['conflict']}, excluded={totals['excluded']}, undecided={totals['undecided']}; "
              f"S4 pending={totals['pending_groups']} groups/{totals['pending_members']} members.")
        print("Planned files: alignment.csv, entity-candidates.csv, mentions.csv, book-statements.jsonl, process/knowledge.md, result.")
        print("\n--- Reviewable diffs ---")
        show_diff("04-knowledge/tables/alignment.csv", render_csv(alignment_fields, alignments), render_csv(alignment_fields, planned_alignments))
        show_diff("04-knowledge/tables/entity-candidates.csv", render_csv(candidate_fields, candidates), render_csv(candidate_fields, planned_candidates))
        show_diff("04-knowledge/tables/mentions.csv", render_csv(mention_fields, mentions), render_csv(mention_fields, planned_mentions))
        show_diff("04-knowledge/tables/book-statements.jsonl", old_statements_text, new_statements_text)
        show_diff("03-processing/" + TASK + "/process/knowledge.md", old_process, new_process)
        show_diff("04-knowledge/results/" + TASK + ".md", result, new_result)
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(CANDIDATE_PATH, candidate_fields, planned_candidates)
    sync.write_csv(MENTION_PATH, mention_fields, planned_mentions)
    write_text(STATEMENT_PATH, new_statements_text)
    write_text(PROCESS_PATH, new_process)
    write_text(RESULT_PATH, new_result)
    print(f"APPLIED: {INDEX_CANDIDATE} -> same {CONTl_KU}; {RUFFO_CANDIDATE} -> new group {RUFFO_GROUP}, pending S4.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
