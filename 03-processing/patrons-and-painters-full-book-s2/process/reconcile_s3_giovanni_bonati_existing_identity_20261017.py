from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
CANDIDATE = "cand-0385"
GROUP = "new-person:bonati-giovanni-d0cc94b9b1"
KU_ID = "units/persons/giovanni-bonati"
CARD_REL = f"04-knowledge/{KU_ID}.md"
ANCHOR = "s3-giovanni-bonati-existing-identity-20261017"
RELATION_IDS = {"st-chp1-l186-187-pio-travel"}
DBI_URL = "https://www.treccani.it/enciclopedia/bonatti-giovanni-detto-giovannino-del-pio-o-il-ferraresino_(Dizionario-Biografico)/"


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile the Bonati/Bonatti spelling variant to its accepted person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    decision = next(row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    card = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate["suggested_type"] == "person"
    assert candidate["canonical_name"] == "Bonati, Giovanni"
    assert candidate["index_entry_id"] == "B.csv#232"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    manifest_row = next(row for row in manifest if row.get("ku_id") == KU_ID)
    assert manifest_row["type"] == "person" and manifest_row["name_en"] == "Giovanni Bonatti"
    assert CARD_REL in accepted
    assert 'name_en: "Giovanni Bonatti"' in card
    assert "OCR Bonari 经本章 PDF 印刷页 6 目视核对为 Bonati" in card
    assert "BONATTI, Giovanni" in card and DBI_URL in card

    source = (ROOT / "02-sources/02-Markdown/01_CHP-1_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Cardinal Pio sent his protégé Giovanni Bonari to Florence, Bologna, Modena, Parma, Milan and Venice" in source
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == RELATION_IDS
    statement = next(row for row in statements if row["statement_id"] in direct)
    assert statement["object_candidate_id"] == CANDIDATE
    assert "PDF-reviewed reading is Bonati" in statement["qualifiers"]["claim"]

    planned_alignments = [dict(row) for row in alignments]
    changed = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    changed["decision"] = "same"
    changed["ku_id"] = KU_ID
    changed["process_ref"] = f"{TASK}#s3-giovanni-bonati-existing-identity-20261017"
    changed["resolution_note"] += (
        f" S3复核（{DATE}）：撤回 new 组 {GROUP}，改为 same → {KU_ID}。书后索引 B.csv#232 的 Bonati, Giovanni "
        "与第1章 p.6 注同一旅行叙述相连；本章 PDF 校读为 Bonati，现有卡已记录该页并指出 OCR Bonari 的差异。"
        "Treccani《Dizionario Biografico degli Italiani》词条标题为“BONATTI (Bonati), Giovanni”，并将其与 Cardinal "
        "Carlo Pio junior 的保护及同一组城市旅行相连，直接支持 Bonati/Bonatti 为同一人物。既有卡在 accepted.yml、"
        "ku-manifest.csv 中均为有效 person KU；故复用而不重复登记。原 new 组和旧理由保留在本行作历史记录。"
        "直接 S2 关系候选仍按原状态留待 S6。"
    )

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4967
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 666
    assert totals["registered_members"] == 822
    assert totals["pending_groups"] == 4119
    assert totals["pending_members"] == 4145

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Giovanni Bonati／Bonatti 既有身份复核（{DATE}）\n\n"
        f"- {CANDIDATE}（B.csv#232，Bonati, Giovanni）原属 {GROUP}；复核后改为 same → "
        f"[{KU_ID}](../../../{CARD_REL})。第1章 p.6 注记的对象正是该人物：Haskell/OCR 作 Bonari，印刷页目视校读为 Bonati；"
        "既有 Bonatti 卡已收录同一页及拼写校正。Treccani DBI 词条明列“BONATTI (Bonati), Giovanni”，并记录 Cardinal "
        f"Carlo Pio junior 的保护及 Florence、Bologna、Modena、Parma、Milan、Venice 的旅行（[词条]({DBI_URL})）。"
        "这一独立书目身份依据与本书同页人名、保护人及旅行内容吻合，支持复用现有人物 KU，不按一字拼写差异新建。\n"
        f"- 直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6；本次未改写关系表或既有卡。\n"
        f"- S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个 KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组；S4 已登记"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条，待登记"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S3 person：Giovanni Bonati／Bonatti 既有身份复核（{DATE}）\n\n"
        f"{CANDIDATE} 原 new 组改为 same → [{KU_ID}](../units/persons/giovanni-bonati.md)。印刷页姓名校读、既有卡同页记录、"
        "保护人与旅行语境及 Treccani DBI 的“BONATTI (Bonati), Giovanni”相互印证；未重复登记 KU。关系候选留待 S6。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} new/{GROUP}->same/{KU_ID}; direct_relation_candidates={len(direct)}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; new={totals['new_candidates']}/{totals['new_groups']}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE} same->{KU_ID}; manifest unchanged at {len(manifest)} KU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
