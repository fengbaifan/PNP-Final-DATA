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

CANDIDATE = "cand-1013"
FILIPPO_KU = "units/persons/filippo-farsetti"
FAMILY_KU = "units/families/farsetti-family"
FAMILY_HISTORY_CANDIDATE = "cand-10443"
FAMILY_HISTORY_GROUP = "archive-group-ca70d9ac8f95"
GROUP = "new-person:farsetti-giuseppe-tommaso-339a4db213"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/tommaso-giuseppe-farsetti_(Dizionario-Biografico)/"
DATE = "2026-10-16"
BACKUP_SUFFIX = ".bak-s3-tommaso-giuseppe-farsetti-20261016"


def decision_row(rows, candidate_id: str):
    matches = [
        row for row in rows
        if row.get("candidate_id") == candidate_id and not row.get("external_source")
    ]
    assert len(matches) == 1, (candidate_id, len(matches))
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review the cross-chapter identity group for Tommaso Giuseppe Farsetti."
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
    family_history = decision_row(alignments, FAMILY_HISTORY_CANDIDATE)
    filippo_manifest = next(row for row in manifest if row.get("ku_id") == FILIPPO_KU)
    family_manifest = next(row for row in manifest if row.get("ku_id") == FAMILY_KU)
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[CANDIDATE]["canonical_name"] == "Farsetti, Tommaso Giuseppe"
    assert candidate_by_id[CANDIDATE]["index_entry_id"] == "F.csv#28"
    assert candidate_by_id[CANDIDATE]["index_page_range"] == "235n, 362n, 364"
    assert target["decision"] == "new" and not target["ku_id"]
    assert sync.get_group(target["resolution_note"]) == GROUP
    assert family_history["decision"] == "new" and not family_history["ku_id"]
    assert sync.get_group(family_history["resolution_note"]) == FAMILY_HISTORY_GROUP
    assert candidate_by_id[FAMILY_HISTORY_CANDIDATE]["suggested_type"] == "archive"
    assert filippo_manifest["type"] == "person"
    assert family_manifest["type"] == "family"
    assert not any(
        row.get("type") == "person"
        and row.get("ku_id") != FILIPPO_KU
        and "Tommaso Giuseppe" in (row.get("canonical_name", "") + row.get("name_en", ""))
        for row in manifest
    )
    assert not any(
        row.get("candidate_id") == CANDIDATE and row.get("external_source")
        for row in alignments
    )

    ch8 = (ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    ch14 = (ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md").read_text(encoding="utf-8-sig")
    ch15 = (ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_i.md").read_text(encoding="utf-8-sig")
    assert "T. G. Farsetti referred to the ceiling" in ch8
    assert "the quotation is a nested source report" not in ch8
    assert "short and rare Latin life by T. G. Farsetti" in ch14
    assert "Daniele’s brother, Tommaso Giuseppe (1720-91)" in ch15
    assert "cousin Daniele" in ch15
    assert "Filippo Farsetti.1 He was born in 1703" in ch15
    assert "the family history published by his cousin Tommaso Giuseppe in 1778" in ch15

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
    assert len(direct) == 11 and len(relation_candidates) == 9

    planned = [dict(row) for row in alignments]
    planned_target = decision_row(planned, CANDIDATE)
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] += (
        " S3 cross-chapter identity review (2026-10-16): F.csv#28 indexes this candidate at pp.235n, 362n, and 364. "
        "Chapter 8 p.235n attributes a late-eighteenth-century ceiling description to ‘T. G. Farsetti’ through Fogolari (1937), p.186; "
        "this is Haskell's nested citation and is not treated as independently verified evidence for the ceiling or its attribution. "
        "Chapter 14 p.347n refers to a short Latin life by ‘T. G. Farsetti’ dedicated to Bonomo. Chapter 15 p.362n cites the 1778 "
        "family history, and p.364 names Tommaso Giuseppe, gives 1720–91, identifies him as Daniele's brother, and discusses his "
        "account of Filippo's collecting and his nephew Anton Francesco. Treccani DBI (Paolo Preto, vol.45, 1995) identifies "
        "Tommaso Giuseppe Farsetti, born in Venice on 16 April 1720 and deceased in Padua on 30 October 1791, and lists "
        "Notizie della famiglia Farsetti (1778) among his works. The cross-chapter initial form and full name therefore belong "
        "to one new person group; no existing person KU represents Tommaso Giuseppe. Keep him distinct from the existing "
        "units/persons/filippo-farsetti (Haskell separately dates Filippo to 1703 and calls Daniele his cousin) and from the "
        "Farsetti family KU. Candidate cand-10443 is the separate 1778 archive/work object in archive-group-ca70d9ac8f95; "
        "this person identity decision does not merge author and work or resolve all claims about the work. Keep this candidate "
        "new with KU registration pending S4. Identity evidence does not establish formal family, authorship, commission, or "
        "other relations beyond the source-bound S2 claims."
    )

    used_ids = {
        int(match.group(1))
        for row in planned
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    }
    next_id = max(used_ids, default=0) + 1
    planned.append({
        "alignment_id": f"aln-{next_id:04d}",
        "candidate_id": CANDIDATE,
        "ku_id": "",
        "external_source": "Treccani DBI",
        "external_id": TRECCANI_URL,
        "decision": "new",
        "accessed_date": DATE,
        "process_ref": "S3-full-book-2026-10-16",
        "legacy_ku_id": "",
        "resolution_note": (
            "Identity only: FARSETTI, Tommaso Giuseppe (Paolo Preto, Dizionario Biografico degli Italiani, vol.45, 1995); "
            "born 16 April 1720 in Venice, died 30 October 1791 in Padua. The entry names his cousin Filippo Vincenzo and "
            "lists Notizie della famiglia Farsetti (1778) among his works. This authority record supports the person's full-name "
            "identity and the connection between the source's initials and full form; it does not verify Haskell's nested quotation "
            "through Fogolari, the specific Latin-life attribution, or the S2 relation candidates."
        ),
    })

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidates)
    external_before = sum(bool(row.get("external_source")) for row in alignments)
    external_after = sum(bool(row.get("external_source")) for row in planned)
    assert external_after == external_before + 1
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
        f"复核人物候选 {CANDIDATE}（Farsetti, Tommaso Giuseppe）：第8章 p.235n 的 T. G. Farsetti、第14章 p.347n 的 T. G. Farsetti "
        f"与第15章 pp.362n、364 的全名及1720–91相互对应；Treccani DBI 支持该身份，并列出其1778年家族史。该候选保留 "
        f"{GROUP} 的独立 new 决定，待 S4 登记。现有 Filippo Farsetti 人物 KU 与 Farsetti family KU 分别是不同人物和集体对象；"
        f"cand-10443 是独立 archive 新组 {FAMILY_HISTORY_GROUP}，不与作者人物合并。{len(relation_candidates)}条关系候选仍待 S6；"
        "第8章转引不作为独立核验的天花描述。\n\n"
    )
    assert f"复核人物候选 {CANDIDATE}" not in result_text
    result_text = result_text.replace(result_marker, result_note + result_marker, 1)

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig").rstrip()
    heading = "### S3 person：Tommaso Giuseppe Farsetti 跨章身份组复核（2026-10-16）"
    assert heading not in process_text
    process_text += (
        f"\n\n{heading}\n\n"
        f"- 索引候选 {CANDIDATE}（F.csv#28，pp.235n、362n、364）保持 {GROUP} 的独立 new 决定，KU 尚未登记。第8章 p.235n 署名缩写“T. G. Farsetti”，"
        "经 Fogolari (1937), p.186 转引一段18世纪末对 Poggio 天花的描述；这是嵌套引文，未经独立核实，不据此确认天花身份、作者原文或引文内容。"
        "第14章 p.347n 称“T. G. Farsetti”写过献给 Bonomo 的短篇拉丁文 Algarotti 生平；这是书内归属，本轮不将其扩大为外部核验。"
        "第15章 p.362n 引用 Tommaso Giuseppe 1778年刊行的家族史，p.364 明载 Daniele 的兄弟 Tommaso Giuseppe (1720–91)，并提到其关于 Filippo 收藏的叙述。"
        f"Treccani DBI（Paolo Preto, vol.45, 1995; {TRECCANI_URL}）以“FARSETTI, Tommaso Giuseppe”立目，记其1720年4月16日生于威尼斯、"
        "1791年10月30日卒于帕多瓦，并列出《Notizie della famiglia Farsetti》(1778)为其著作；同条还称其堂亲 Filippo Vincenzo。全名、初始形式、"
        "年代和家族史著作共同支持这些跨章指称属于同一人物组。未发现同身份既有 person KU。既有 units/persons/filippo-farsetti 对应书中另一个"
        "Filippo Farsetti（第15章 p.302 记生于1703年；p.363称 Daniele 为 Filippo 的堂亲，p.364 则称 Tommaso 为 Daniele 的兄弟）；"
        "units/families/farsetti-family 是不同类型的家族对象。cand-10443 是独立 archive 新组 archive-group-ca70d9ac8f95，指向1778年家族史作品，"
        "待 S4；不把作品并入作者人物，也不借身份裁决解决作品内容或其他 claims。\n"
        f"- 该候选的{len(direct)}条直接 S2 陈述中{len(relation_candidates)}条为关系候选，留待 S6；未新增正式关系或 S5 补足。"
        "涉及亲属、赞助、著述、委托的语句仍按各自 S2 证据和类型保留，不由身份匹配自动升级为正式关系。\n\n"
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
            f"dry-run passed: {CANDIDATE} remains new/pending S4 in {GROUP}; distinct_from={FILIPPO_KU}; "
            f"separate_work={FAMILY_HISTORY_CANDIDATE}/{FAMILY_HISTORY_GROUP}; "
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
            shutil.copy2(backup, path)
        raise
    print(
        f"applied: {CANDIDATE} remains new/pending S4 in {GROUP}; distinct_from={FILIPPO_KU}; "
        f"separate_work={FAMILY_HISTORY_CANDIDATE}/{FAMILY_HISTORY_GROUP}; "
        f"relation_candidates_pending={len(relation_candidates)}; external_records={external_after}; "
        f"alignment_rows={len(planned)}; registered={totals['registered_groups']}/{totals['registered_members']} "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
