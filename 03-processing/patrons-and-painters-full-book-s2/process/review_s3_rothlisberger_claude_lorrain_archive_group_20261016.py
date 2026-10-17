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

CANDIDATE = "cand-4577"
GROUP = "archive-group-4f5f75670a57"
CLAUDE_PERSON_KU = "units/persons/claude-lorrain"
INHA_URL = "https://agorha.inha.fr/ark:/54721/6ca774b1-afc0-47eb-ac34-561be13db605"
FOLGER_URL = "https://catalog.folger.edu/record/11636"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s3-rothlisberger-archive-20261016"


def decision_row(rows, candidate_id: str):
    matches = [
        row for row in rows
        if row.get("candidate_id") == candidate_id and not row.get("external_source")
    ]
    assert len(matches) == 1, (candidate_id, len(matches))
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review the cross-chapter archive identity for Röthlisberger's Claude Lorrain catalogue."
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
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "archive"
    assert candidate_by_id[CANDIDATE]["canonical_name"] == "Claude Lorrain—The Paintings (M. Röthlisberger, 1961), vol. I"
    assert candidate_by_id[CANDIDATE]["detail"].find("two-volume") >= 0
    assert target["decision"] == "new" and not target["ku_id"]
    assert sync.get_group(target["resolution_note"]) == GROUP
    group_members = [
        row["candidate_id"]
        for row in alignments
        if row.get("candidate_id")
        and not row.get("external_source")
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert group_members == [CANDIDATE]
    assert not any(
        row.get("type") == "archive"
        and "claude lorrain" in (row.get("canonical_name", "") + row.get("name_en", "")).lower()
        for row in manifest
    )
    assert any(row.get("ku_id") == CLAUDE_PERSON_KU and row.get("type") == "person" for row in manifest)
    assert not any(
        row.get("candidate_id") == CANDIDATE and row.get("external_source")
        for row in alignments
    )

    bibliography = (ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md").read_text(encoding="utf-8-sig")
    ch2 = (ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md").read_text(encoding="utf-8-sig")
    ch4 = (ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md").read_text(encoding="utf-8-sig")
    ch6 = (ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md").read_text(encoding="utf-8-sig")
    ch7 = (ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Claude Lorrain" in bibliography and "2 vols." in bibliography and "1961" in bibliography
    assert "Rothlisberger, 1961, p. 153" in ch2
    assert "Rothlisberger, 1961, pp. 428 and 433" in ch4
    assert "Rothlisberger, 1961, p. 374" in ch6
    assert "pp. 15 5-60" in ch7 and "1, p. 274" in ch7

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
    assert len(direct) == 10 and len(relation_candidates) == 4
    assert chapters == ["chp-2", "chp-21", "chp-4", "chp-6", "chp-7"]

    planned = [dict(row) for row in alignments]
    planned_target = decision_row(planned, CANDIDATE)
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] += (
        " S3 cross-chapter archive identity review (2026-10-16): the same 1961 Claude Lorrain catalogue is cited in ch.2, ch.4, "
        "ch.6, and ch.7, and its complete bibliographic record appears in ch.21. The source bibliography explicitly lists "
        "Claude Lorrain—The Paintings, two volumes, Yale and London, 1961; its citations include p.153, pp.121/67/127, "
        "pp.428/433, p.374, p.369, pp.155–160, and p.274 (the latter explicitly volume I). INHA AGORHA records Marcel "
        "Röthlisberger as author of the two-volume publication, New Haven, 1961. The Folger catalog distinguishes vol.1 as "
        "the critical catalogue and vol.2 as illustrations, and gives the vol.1 bibliography at pp.551–558; the cited numbered "
        "pages therefore fit the vol.1 critical-catalogue locator retained in this candidate. Keep one new archive group for "
        "the cited 1961 publication/vol.1 locator; do not merge it with the distinct 1968 Claude Lorrain drawings work or with "
        "the person Claude Lorrain. No same-type archive KU is present; this group remains new and pending S4. Bibliographic "
        "identity does not verify any cited page content or the claims supported by those citations."
    )

    external_rows = [
        {
            "external_source": "INHA AGORHA",
            "external_id": INHA_URL,
            "note": (
                "Identity only: AGORHA record names Marcel Röthlisberger as author of Claude Lorrain. The paintings; "
                "full citation states two volumes, New Haven, 1961. Supports the full name and publication identity."
            ),
        },
        {
            "external_source": "Folger Shakespeare Library catalog",
            "external_id": FOLGER_URL,
            "note": (
                "Identity only: catalog record names Marcel Röthlisberger, New Haven: Yale University Press, 1961, two volumes; "
                "vol.1 is the critical catalogue and vol.2 the illustrations. Does not verify cited page contents."
            ),
        },
    ]
    used_ids = {
        int(match.group(1))
        for row in planned
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    }
    next_id = max(used_ids, default=0) + 1
    for record in external_rows:
        planned.append({
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": "",
            "external_source": record["external_source"],
            "external_id": record["external_id"],
            "decision": "new",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": record["note"],
        })
        next_id += 1

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidates)
    external_before = sum(bool(row.get("external_source")) for row in alignments)
    external_after = sum(bool(row.get("external_source")) for row in planned)
    assert external_after == external_before + len(external_rows)
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text, alignment_count = re.subn(
        r"(\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \| )[\d,]+(?= 条：)",
        f"\\g<1>{len(planned):,}",
        result_text,
        count=1,
    )
    assert alignment_count == 1
    result_text, row_external_count = re.subn(
        r"(\| \[全书对齐\]\(\.\./tables/alignment\.csv\) \| [\d,]+ 条：[\d,]+ 条候选决定记录及 )[\d,]+(?= 条外部身份记录)",
        f"\\g<1>{external_after:,}",
        result_text,
        count=1,
    )
    assert row_external_count == 1
    result_text, external_count = re.subn(
        r"(?<=统计；)[\d,]+(?=条外部身份记录单独保留)",
        f"{external_after:,}",
        result_text,
        count=1,
    )
    assert external_count == 1
    result_marker = "### S4 按类型登记进度"
    assert result_text.count(result_marker) == 1
    result_note = (
        f"复核 archive 候选 {CANDIDATE}（Claude Lorrain—The Paintings，1961）：第2、4、6、7章的引文及第21章书目项指向同一两卷本出版物；"
        f"INHA 与 Folger 目录将作者全名定为 Marcel Röthlisberger，并区分 vol.1 critical catalogue 与 vol.2 illustrations。保留 "
        f"{GROUP} 为 new archive 组，待 S4。候选标题中的 vol. I 是所引页码定位；不与 Claude Lorrain 人物 KU 或其1968年绘画作品集混合。"
        f"{len(relation_candidates)}条关系候选仍待 S6；书目身份不验证具体引文内容。\n\n"
    )
    assert f"复核 archive 候选 {CANDIDATE}" not in result_text
    result_text = result_text.replace(result_marker, result_note + result_marker, 1)

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig").rstrip()
    heading = "### S3 archive：Röthlisberger《Claude Lorrain—The Paintings》跨章身份组复核（2026-10-16）"
    assert heading not in process_text
    process_text += (
        f"\n\n{heading}\n\n"
        f"- archive 候选 {CANDIDATE} 保持 {GROUP} 的独立 new 决定，KU 待 S4。第2章引文引用1961年 p.153、p.121、p.67、p.127；"
        "第4章 p.118 注5引用 pp.428、433；第6章引用 p.374、p.369；第7章引用 vol.I pp.155–160 与 p.274；第21章书目列 "
        "Claude Lorrain—The Paintings, 2 vols., Yale and London 1961。候选实体为这部文献的书目/卷册身份，不是 Claude Lorrain 本人或其绘画作品。\n"
        f"- INHA AGORHA（{INHA_URL}）以 Marcel Röthlisberger 为作者，列两卷本、New Haven、1961。Folger Shakespeare Library 目录"
        f"（{FOLGER_URL}）区分 vol.1 “Critical catalogue” 与 vol.2 “Illustrations”，并将 vol.1 书目页标为551–558。书内所引页码均符合 vol.1"
        "的分页范围，且 p.274 明标卷I；因此当前候选的“vol. I locator”与同一两卷本出版物身份相容。未发现同类型 archive KU；"
        "已存在 units/persons/claude-lorrain 是艺术家人物卡，类型和对象均不同。未将其他 editions 或《Claude Lorrain: The Drawings》(1968) 并入。\n"
        f"- 涉及该候选的{len(direct)}条直接 S2 陈述中{len(relation_candidates)}条被标为关系候选，留待 S6；身份裁决不验证各引文页内容或相关作品断言。"
        "本轮只新增两条外部书目身份记录，无 KU、卡片、manifest 或正式关系变更。\n\n"
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
    assert len(manifest) == 1300

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
            f"external_records={external_before}->{external_after}; alignment_rows={len(alignments)}->{len(planned)}; "
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
        f"relation_candidates_pending={len(relation_candidates)}; external_records={external_after}; "
        f"alignment_rows={len(planned)}; registered={totals['registered_groups']}/{totals['registered_members']} "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
