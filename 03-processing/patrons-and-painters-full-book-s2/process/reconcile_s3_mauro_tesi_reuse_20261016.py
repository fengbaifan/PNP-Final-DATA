from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
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
DATE = "2026-10-16"

CANDIDATE = "cand-2551"
ACCEPTED_CANDIDATE = "cand-3839"
PRIOR_GROUP = "new-person:mauro-tesi-4af80fb4b8"
EXISTING_GROUP = "sg3-ku-units-persons-mauro-antonio-tesi"
KU_ID = "units/persons/mauro-antonio-tesi"
CARD_REL = "04-knowledge/units/persons/mauro-antonio-tesi.md"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/tesi-mauro-antonio-detto-maurino_(Dizionario-Biografico)/"
ICCD_URL = "https://catalogo.cultura.gov.it/Agent/62ecdfba20c98c7b07de0f22a6ea6d25"
BACKUP_SUFFIX = ".bak-s3-same-mauro-tesi-20261016"


def contains_candidate(value, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(contains_candidate(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(contains_candidate(item, candidate_id) for item in value)
    return value == candidate_id


def normalized(text: str) -> str:
    return " ".join(text.split())


def decision_row(rows, candidate_id: str):
    matches = [
        row for row in rows
        if row.get("candidate_id") == candidate_id and not row.get("external_source")
    ]
    assert len(matches) == 1, (candidate_id, len(matches))
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the cross-chapter Mauro Tesi candidate to the accepted Mauro Antonio Tesi KU."
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
    accepted_alignment = decision_row(alignments, ACCEPTED_CANDIDATE)
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[CANDIDATE]["canonical_name"] == "Tesi, Mauro"
    assert candidate_by_id[CANDIDATE]["index_entry_id"] == "T.csv#14"
    assert candidate_by_id[CANDIDATE]["index_page_range"] == "358, 359, 360, 409"
    assert target["decision"] == "new" and not target["ku_id"]
    assert sync.get_group(target["resolution_note"]) == PRIOR_GROUP
    prior_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row["decision"] == "new" and sync.get_group(row.get("resolution_note", "")) == PRIOR_GROUP
    ]
    assert prior_members == [CANDIDATE], prior_members
    assert accepted_alignment["decision"] == "same" and accepted_alignment["ku_id"] == KU_ID
    assert sync.get_group(accepted_alignment["resolution_note"]) == EXISTING_GROUP
    manifest_row = next(row for row in manifest if row.get("ku_id") == KU_ID)
    assert manifest_row["type"] == "person" and manifest_row["card_path"] == CARD_REL
    assert manifest_row["name_en"] == "Mauro Antonio Tesi"
    card = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    assert "Mauro Antonio Tesi" in card and "Mauro Tesi" in card
    assert not any(row.get("candidate_id") == CANDIDATE and row.get("external_source") for row in alignments)

    index_path = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "T.csv"
    with index_path.open(encoding="utf-8-sig", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    index_row = index_rows[int(candidate_by_id[CANDIDATE]["index_entry_id"].split("#")[1])]
    assert index_row["Main Entry"] == "Tesi, Mauro"
    assert index_row["Page Numbers"] == "358, 359, 360, 409"

    source14 = (ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md").read_text(encoding="utf-8-sig")
    source20 = (ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    for quote in (
        "In Bologna, to which he moved in 1756, he came across two artists, Prospero Pesci and Mauro Tesi",
        "with Tesi and his wife he established extremely intimate relations",
        "an essentially architectural artist as Mauro Tesi",
    ):
        assert normalized(quote) in normalized(source14), quote
    assert "painted by Mauro Tesi" in source20

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relations = [
        row for row in direct
        if row.get("qualifiers", {}).get("relation_candidate") is True
    ]
    assert len(direct) > 0

    # Retain separate, explicitly unresolved person/work/place identities around Tesi.
    expected_decisions = {
        "cand-10392": "new",       # the 1787 printed collection is an archive object
        "cand-10400": "undecided", # unidentified copies made on the central-Italy journey
        "cand-10401": "undecided", # unidentified Dietrich landscapes and copy set
        "cand-10402": "undecided", # vignettes for an edition still in preparation
        "cand-10405": "undecided", # surname-only Dietrich identity
        "cand-10406": "undecided", # unnamed wife
        "cand-10407": "undecided", # unnamed daughter
        "cand-10408": "undecided", # unidentified room in Pisa
        "cand-11522": "undecided", # unnamed admired source works, distinct from copies
    }
    for cid, expected in expected_decisions.items():
        assert decision_row(alignments, cid)["decision"] == expected, cid

    planned = [dict(row) for row in alignments]
    planned_target = decision_row(planned, CANDIDATE)
    old_note = planned_target["resolution_note"]
    assert f"; group={PRIOR_GROUP};" in old_note
    revised_note = old_note.replace(
        f"; group={PRIOR_GROUP};",
        f"; previous_group_label={PRIOR_GROUP};",
        1,
    )
    planned_target["decision"] = "same"
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] = (
        revised_note
        + f" matched_manifest={KU_ID}; matched_candidate_ids={ACCEPTED_CANDIDATE}; group={EXISTING_GROUP};"
        + " S3 cross-chapter reuse review (2026-10-16): index T.csv#14 spans pp. 358–360 and 409; "
        "chapter 14 uses the full source form Mauro Tesi in its Bologna, Algarotti, architectural-painter, and Pisa contexts, "
        "and chapter 20 p. 409 names Mauro Tesi as painter of two pictures left to Pitt. The existing accepted person KU is "
        "Mauro Antonio Tesi. Treccani DBI identifies Mauro Antonio Tesi, detto Maurino, born at Montalbano in 1730 and died "
        "in Bologna in 1766, and describes the documented intellectual relationship and commissions with Francesco Algarotti; "
        "the Italian national cultural catalogue also lists the artist authority form Tesi Mauro (1730/1766) and "
        "links his catalogued works. Full-name correspondence, period, professional context, and the shared Algarotti context "
        "support same as the existing KU. The original new-group proposal and its preliminary no-match rationale are retained "
        f"above as history under previous_group_label={PRIOR_GROUP}."
    )
    assert sync.get_group(planned_target["resolution_note"]) == EXISTING_GROUP

    used_ids = {
        int(match.group(1))
        for row in planned
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    }
    next_id = max(used_ids, default=0) + 1
    authority_rows = [
        {
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Treccani DBI",
            "external_id": TRECCANI_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: the DBI heading is 'Tesi, Mauro Antonio, detto Maurino'; it gives birth at "
                "Montalbano on 1730-01-15 and death in Bologna on 1766-07-18, identifies his artistic practice, "
                "and discusses his intellectual friendship and commissions with Francesco Algarotti."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 1:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Catalogo Generale dei Beni Culturali (ICCD)",
            "external_id": ICCD_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: the national cultural heritage catalogue authority is headed 'Tesi Mauro' and "
                "dates the artist 1730/1766; its linked work records list Tesi as artist/designer."
            ),
        },
    ]
    planned.extend(authority_rows)

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidates)
    assert totals["same_candidates"] == sum(row["decision"] == "same" for row in [decision_row(planned, cid) for cid in candidate_by_id])
    existing_external_count = sum(bool(row.get("external_source")) for row in alignments)
    external_count = sum(bool(row.get("external_source")) for row in planned)
    assert external_count == existing_external_count + len(authority_rows)

    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    external_pattern = re.compile(r"(\d+)(?=条外部身份记录单独保留)")
    next_result, external_count_updates = external_pattern.subn(str(external_count), next_result, count=1)
    assert external_count_updates == 1
    marker = "。各组来源、身份边界和映射更正见[过程记录]"
    assert next_result.count(marker) == 1
    next_result = next_result.replace(
        marker,
        f"；person 候选 {CANDIDATE}（Tesi, Mauro）复用"
        "[毛罗·安东尼奥·泰西人物卡](../units/persons/mauro-antonio-tesi.md)，"
        f"{len(direct_relations)}条关系候选留待 S6" + marker,
        1,
    )

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    heading = f"### S3 person：{CANDIDATE} 跨章复用毛罗·安东尼奥·泰西人物 KU（{DATE}）"
    assert heading not in knowledge_text
    process_note = (
        f"\n\n{heading}\n\n"
        f"- 索引候选 {CANDIDATE}（T.csv#14，pp.358–360、409）原记为 new 组 {PRIOR_GROUP}；现裁决为 same，"
        f"映射至已接收人物 KU {KU_ID}，并并入其跨任务身份组 {EXISTING_GROUP}。候选 `cand-3839` 已通过接受卡来源映射到同一 KU。"
        "第14章 pp.358–360 在 Algarotti 移居 Bologna、与建筑画家合作、Tesi 及其家人、Pisa 房间等不同语境中反复使用 Mauro Tesi；"
        "第20章后记 p.409 亦以全名称其为遗赠给 Elder Pitt 的两幅画的画家。既有人物卡规范名为 Mauro Antonio Tesi，"
        "Treccani DBI 的条目标题为“Mauro Antonio, detto Maurino”，记1730年生于 Montalbano、1766年卒于 Bologna，并记述他与 Algarotti 的交往和委托；"
        "意大利文化遗产总目录也以“Tesi Mauro (1730/1766)”列出作者规范记录，并关联作品目录。全名、年代、职业和 Algarotti 语境共同支持复用，"
        "不是仅凭姓氏或同词命中合并。原 `new` 组标签与“未匹配既有 KU”的初步说明在 alignment 行以 `previous_group_label` 留存；当前 `group` 指向既有 KU 组。"
        "本轮只裁决人物身份，不扩大为关系事实确认。\n"
        f"- 涉及该候选的{len(direct)}条直接 S2 陈述中{len(direct_relations)}条标为关系候选，留待 S6；未新增正式关系或 S5 补足。"
        "临近对象分别保留去向：`cand-10392` 是独立的1787年书目/画册 archive 新组，待 S4；`cand-10400`、`cand-10401`、`cand-10402`、"
        "`cand-11522` 为未识别作品组，继续 undecided；`cand-10405` 仅有 Dietrich 姓氏，身份 undecided；`cand-10406` 未具名妻子、"
        "`cand-10407` 未具名女儿均保持 undecided，不推测身份；`cand-10408` 为未识别的比萨房间，继续 undecided。"
        "这些对象不因 Tesi 人物身份已对齐而自动并入同一 KU。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_knowledge = knowledge_text + process_note

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=alignment_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(planned)
    updated = {
        ALIGNMENT: buffer.getvalue(),
        RESULT: next_result,
        KNOWLEDGE: next_knowledge,
    }
    for path in updated:
        assert not path.with_name(path.name + BACKUP_SUFFIX).exists(), path

    before_counts = Counter(row["decision"] for row in [decision_row(alignments, cid) for cid in candidate_by_id])
    after_counts = Counter(row["decision"] for row in [decision_row(planned, cid) for cid in candidate_by_id])
    assert after_counts["same"] == before_counts["same"] + 1
    assert after_counts["new"] == before_counts["new"] - 1
    assert after_counts["undecided"] == before_counts["undecided"]

    if args.dry_run:
        for path, content in updated.items():
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True), content.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (updated)", n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE} new->{KU_ID} same; group={EXISTING_GROUP}; "
            f"direct_statements={len(direct)} relation_candidates_pending={len(direct_relations)}; "
            f"external_records={existing_external_count}->{external_count}; "
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
            shutil.copy2(backup, path)
        raise
    print(
        f"applied: {CANDIDATE} -> same {KU_ID}; group={EXISTING_GROUP}; "
        f"relation_candidates_pending={len(direct_relations)}; external_records={external_count}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']} "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(manifest)} unchanged; recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
