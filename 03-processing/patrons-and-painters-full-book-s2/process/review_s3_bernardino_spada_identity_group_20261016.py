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

CANDIDATE = "cand-2493"
VIRGILIO_CANDIDATE = "cand-2494"
VIRGILIO_ACCEPTED_CANDIDATE = "cand-3895"
GROUP = "new-person:bernardino-spada-810d88ac92"
VIRGILIO_KU = "units/persons/virgilio-spada"
TRECCANI_URL = "https://www.treccani.it/enciclopedia/bernardino-spada_(Dizionario-Biografico)/"
BACKUP_SUFFIX = ".bak-s3-bernardino-spada-20261016"


def decision_row(rows, candidate_id: str):
    matches = [
        row for row in rows
        if row.get("candidate_id") == candidate_id and not row.get("external_source")
    ]
    assert len(matches) == 1, (candidate_id, len(matches))
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review the cross-chapter Cardinal Bernardino Spada identity separately from Virgilio Spada."
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
    virgil_candidate = decision_row(alignments, VIRGILIO_CANDIDATE)
    accepted_virgil = decision_row(alignments, VIRGILIO_ACCEPTED_CANDIDATE)
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[CANDIDATE]["canonical_name"] == "Spada, Cardinal Bernardino"
    assert candidate_by_id[CANDIDATE]["index_entry_id"] == "S.csv#182"
    assert candidate_by_id[CANDIDATE]["index_page_range"] == "75, 139"
    assert target["decision"] == "new" and not target["ku_id"]
    assert sync.get_group(target["resolution_note"]) == GROUP
    assert virgil_candidate["decision"] == "same" and virgil_candidate["ku_id"] == VIRGILIO_KU
    assert accepted_virgil["decision"] == "same" and accepted_virgil["ku_id"] == VIRGILIO_KU
    assert any(row.get("ku_id") == VIRGILIO_KU and row.get("type") == "person" for row in manifest)
    assert not any(
        row.get("type") == "person"
        and "Bernardino Spada" in (row.get("name_en", "") + row.get("canonical_name", ""))
        for row in manifest
    )
    assert not any(row.get("candidate_id") == CANDIDATE and row.get("external_source") for row in alignments)

    source3 = (ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md").read_text(encoding="utf-8-sig")
    source5 = (ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iii.md").read_text(encoding="utf-8-sig")
    assert "He and his brother Cardinal Bernardino were both protégés of Urban VIII and enthusiastic connoisseurs." in source3
    assert "where the Cardinal had served as legate between 1627 and 1631" in source3
    assert "If it was actually painted for Cardinal Bernardino" in source5
    assert "Spada who had been papal nunzio in Paris was firmly in the French camp" in source5

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
        " S3 cross-chapter identity review (2026-10-16): ch.3 p.75 identifies the full form ‘Cardinal Bernardino’ and "
        "explicitly says ‘He and his brother Cardinal Bernardino’ when naming Virgilio Spada; it describes Bernardino as "
        "the collector who acquired the palace and says he had served as legate in Bologna 1627–1631. Ch.5 p.139 names "
        "Cardinal Bernardino again in the possible commission context, while preserving the conditional ‘If it was actually painted’; "
        "the same passage identifies the cardinal as former papal nuncio in Paris and as aligned with the French camp. Treccani DBI "
        "(Benedetta Borello, vol. 93, 2018) identifies Bernardino Spada, born in 1594, appointed cardinal in 1626, legate of Bologna "
        "until 1631, and deceased in 1661; it separately names his brother Virgilio. These full-name, title, career, and cross-chapter "
        "anchors support this one new person group and distinguish it from the existing Virgilio Spada KU. Do not merge the two men; "
        "the book's co-connoisseur statement does not by itself create a formal family or patronage relation. The candidate remains new "
        "with KU registration pending S4."
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
            "Identity only: ‘SPADA, Bernardino’ (Benedetta Borello, DBI vol. 93, 2018), born 1594 and died 1661; "
            "appointed cardinal in 1626, served as papal nuncio in Paris and legate of Bologna, and had a brother named Virgilio."
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
    result_text, count_updates = re.subn(
        r"\d+(?=条外部身份记录单独保留)", str(external_after), result_text, count=1
    )
    assert count_updates == 1
    result_marker = "### S4 按类型登记进度"
    assert result_text.count(result_marker) == 1
    result_note = (
        f"本轮复核人物候选 `{CANDIDATE}`（Cardinal Bernardino Spada），其跨第3、5章锚点与 Treccani DBI 身份记录相符，"
        f"保持独立 new 组 `{GROUP}`，KU 待 S4。现有 `{VIRGILIO_KU}` 对应 Virgilio Spada；第3章明说 Virgilio 与 Cardinal Bernardino 为兄弟，"
        f"故不把两人合并。{len(relation_candidates)}条关系候选仍待 S6。\n\n"
    )
    assert f"本轮复核人物候选 `{CANDIDATE}`" not in result_text
    result_text = result_text.replace(result_marker, result_note + result_marker, 1)

    process_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    heading = f"### S3 person：Cardinal Bernardino Spada 跨章身份组复核（{DATE}）"
    assert heading not in process_text
    process_text += (
        f"\n\n{heading}\n\n"
        f"- 索引候选 `{CANDIDATE}`（S.csv#182，pp.75、139）保持 `{GROUP}` 的独立 `new` 决定，KU 尚未登记。第3章 p.75 先以 Virgilio Spada 为主语，"
        "接着明确写“his brother Cardinal Bernardino”，并记 Bernardino 从 Mignanelli 手中购得 Farnese 宫附近的宫殿、曾于1627–1631年任博洛尼亚使节；"
        "第5章 p.139 再以 Cardinal Bernardino 指称曾任驻巴黎教廷使节、与法国阵营相关的红衣主教。该页关于《Masaniello 起义》的委托语气为“If it was actually painted”，"
        "不将可能委托写成确定事实。Treccani DBI（Benedetta Borello，vol.93，2018）以“SPADA, Bernardino”为标题，记其1594年出生、1626年获任枢机、"
        "曾任巴黎教廷使节及博洛尼亚使节（至1631年）、1661年去世，并明确记其兄弟 Virgilio。故本书 candidate `cand-2493` 对应 Cardinal Bernardino，"
        f"与已存在的 `{VIRGILIO_KU}`（Virgilio Spada）是两个人；同姓和兄弟关系不构成合并理由。外部记录只附到 Bernardino 候选，不借用 Virgilio 的身份标识。\n"
        f"- 涉及该候选的{len(direct)}条直接 S2 陈述中{len(relation_candidates)}条为关系候选，留待 S6；未新增正式关系或 S5 补足。\n\n"
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
            f"dry-run passed: {CANDIDATE} remains new/pending S4 in {GROUP}; distinct_from={VIRGILIO_KU}; "
            f"direct_statements={len(direct)} relation_candidates_pending={len(relation_candidates)}; "
            f"external_records={external_before}->{external_after}; registered={totals['registered_groups']}/"
            f"{totals['registered_members']} pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged"
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
        f"applied: {CANDIDATE} remains new/pending S4 in {GROUP}; distinct_from={VIRGILIO_KU}; "
        f"relation_candidates_pending={len(relation_candidates)}; external_records={external_after}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']} "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
