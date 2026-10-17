from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
CANDIDATE = "cand-1727"
EXISTING_KU = "units/persons/b-nazari"
GROUP = "sg3-ku-units-persons-b-nazari"
ANCHOR = "s3-reuse-bartolommeo-nazari-existing-ku-20261017"
SOURCE = "Treccani, Dizionario Biografico degli Italiani"
SOURCE_URL = "https://www.treccani.it/enciclopedia/bartolomeo-nazari_res-1dbdf466-03ed-11e7-b5f4-00271042e8d9_(Dizionario-Biografico)/"


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile Bartolommeo Nazari to the existing Bartolomeo Nazari KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE)
    assert candidate.get("index_entry_id") == "N.csv#7"
    assert candidate.get("index_page_range") == "287, 293, 295, 312, 314, 322, 345"
    assert candidate.get("canonical_name") == "Nazari, Bartolommeo"
    base_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(base_rows) == 1
    base = base_rows[0]
    assert base.get("decision") == "new" and not base.get("ku_id")
    assert sync.get_group(base.get("resolution_note", "")) == "new-person:bartolommeo-nazari-93e34e8ef8"
    assert not any(row.get("candidate_id") == CANDIDATE and row.get("external_source") == SOURCE for row in alignments)
    existing = [row for row in alignments if row.get("candidate_id") == "cand-3728" and not row.get("external_source")]
    assert len(existing) == 1 and existing[0].get("ku_id") == EXISTING_KU and existing[0].get("decision") == "same"

    planned = [dict(row) for row in alignments]
    target = next(row for row in planned if row.get("alignment_id") == base["alignment_id"])
    mention_evidence = base.get("resolution_note", "").split("; group=", 1)[0]
    target.update({
        "ku_id": EXISTING_KU,
        "decision": "same",
        "accessed_date": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
        "resolution_note": (
            f"{mention_evidence}; group={GROUP}; S3复核（{DATE}）：原 new 改为 same，映射至既有 KU {EXISTING_KU}。"
            "本书索引 N.csv#7 的全名拼写为 Bartolommeo Nazari；第10章 p.312 明确记其为 Schulenburg 画像者。"
            "既有 KU 记名 Bartolomeo Nazari，并关联同一 Schulenburg 肖像委托；Treccani DBI 条目确认该人物与 Schulenburg 的画像委托相合。"
            "双写 m 与单写 m 为拼写差异；不新建重复人物，也不将外部传记事实复制到本书断言。"
        ),
    })
    numbers = [int(match.group(1)) for row in planned if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))]
    external_id = f"aln-{max(numbers, default=0) + 1:04d}"
    planned.append({
        "alignment_id": external_id,
        "candidate_id": CANDIDATE,
        "ku_id": EXISTING_KU,
        "external_source": SOURCE,
        "external_id": SOURCE_URL,
        "decision": "same",
        "accessed_date": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
        "legacy_ku_id": "",
        "resolution_note": "Treccani DBI, ‘NAZARI, Bartolomeo’ (Fiorenzo Fisogni, vol. 78, 2017), especially the 1733 Schulenburg portrait commission; consulted for identity comparison only.",
    })

    before_stats = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(value[key] for value in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals["same_candidates"] == before_totals["same_candidates"] + 1
    assert totals["new_candidates"] == before_totals["new_candidates"] - 1
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"] - 1

    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Bartolommeo Nazari 对齐至既有 KU（{DATE}）\n\n"
        f"cand-1727 的 S3 决定由 new 改为 same，复用[巴托洛梅奥·纳扎里（Bartolomeo Nazari）](../../../04-knowledge/units/persons/b-nazari.md)（{EXISTING_KU}）。"
        "S1 索引 N.csv#7 将第10章 p.287、293、295、312、314、322及第13章 p.345列为同一人物条目；"
        "S2 第10章 p.312 全名为 Bartolommeo Nazari，并明确称其为 Schulenburg 画像者；p.322又以完整姓名记载其绘制 Lodoli 肖像。"
        "既有 KU 的 Treccani DBI 来源记名 Bartolomeo Nazari，并记1733年 Schulenburg 委托骑马肖像；本次实际阅读该 DBI 条目（"
        f"{SOURCE_URL}，访问日期 {DATE}）用于核对姓名拼写及同一 Schulenburg 委托。判断为单写/双写 m 的拼写差异，"
        "不把 DBI 的生平或作品事实扩写进书内断言，也不新建重复 KU。外部身份记录另列于 alignment.csv。"
    )

    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(sync.read_csv(TABLES / "ku-manifest.csv")[1]))
    result_text = result_text.rstrip() + (
        f"\n\n### S3/S4 person：Bartolommeo Nazari 复用既有 KU（{DATE}）\n\n"
        f"cand-1727 的新建决定经身份复核改为 same，映射到[既有 Bartolomeo Nazari KU](../units/persons/b-nazari.md)；"
        "S2 全名与 Treccani DBI 所记 Schulenburg 肖像委托相互吻合，没有新增卡片。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} new->same {EXISTING_KU}; external_alignment={external_id}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest unchanged"
        )
        return 0

    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE}->same:{EXISTING_KU}; external_alignment={external_id}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
