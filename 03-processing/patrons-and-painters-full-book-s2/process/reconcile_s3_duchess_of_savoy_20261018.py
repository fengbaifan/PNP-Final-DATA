from __future__ import annotations

import argparse
import csv
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_person_m_index_endpoints_20261018 as common  # noqa: E402

sync = common.sync
process_sync = common.process_sync

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s3-identity-review-duchess-of-savoy-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
CANDIDATE = "cand-2383"
GROUP = "new-person:duchess-of-savoy-5fdc78ee0e"
CARD = "04-knowledge/units/persons/duchess-of-savoy.md"
S2_SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md"
INDEX_SOURCE = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "S.csv"


def csv_text(fieldnames: list[str], rows: list[dict]) -> str:
    import io

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def build_outputs():
    fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate_rows = {row["candidate_id"]: row for row in candidates}
    row = decisions[CANDIDATE]
    assert row["decision"] == "new" and not row.get("ku_id")
    assert candidate_rows[CANDIDATE]["suggested_type"] == "person"
    assert sync.get_group(row["resolution_note"]) == GROUP
    assert not (ROOT / CARD).exists()
    assert not any(item.get("candidate_id") == CANDIDATE and item.get("external_source") for item in alignments)

    index_text = INDEX_SOURCE.read_text(encoding="utf-8-sig")
    source_text = S2_SOURCE.read_text(encoding="utf-8-sig")
    assert "Savoy, Duchess of" in index_text
    assert "at the very end of the century the Duchess of Savoy" in source_text
    assert "Adelaide Enrichetta of Savoy" in (
        ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_iv.md"
    ).read_text(encoding="utf-8-sig")
    assert "Anne Marie de Savoye" in (
        ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
    ).read_text(encoding="utf-8-sig")

    updated = dict(row)
    updated["decision"] = "undecided"
    updated["ku_id"] = ""
    updated["external_source"] = ""
    updated["external_id"] = ""
    updated["accessed_date"] = ""
    updated["process_ref"] = PROCESS_REF
    updated["resolution_note"] = (
        "source_ref=candidate=cand-2383;index_entry=S.csv#71;index_pages=65;"
        "s2_mentions=m-chp3-seci-l26-33-0024@02-sources/02-Markdown/03_CHP-3_sec_i.md#L26-33[Duchess of Savoy;chars=1709-1725],"
        "m-chp3-seci-l26-33-0028@02-sources/02-Markdown/03_CHP-3_sec_i.md#L26-33[she;chars=1858-1861];"
        "prior_decision=new;prior identity group:new-person:duchess-of-savoy-5fdc78ee0e (superseded);"
        "S3复核（2026-10-18）：索引与第3章p.65均只称“Duchess of Savoy”，正文仅给出“17世纪末”及聘用Ciro Ferri赴Turin的语境，没有个人姓名或可唯一落到其他候选的书内身份锚点。"
        "cand-2380（Adelaide Enrichetta of Savoy，p.193注）与cand-2381（Anne Marie de Savoye，1736年收据，p.341注）均无原文交叉指称可与本称号合并；不按Savoy称号或姓氏推定同一人物。"
        "撤回原new身份组并改为undecided，不登记KU；如需消歧，需有据的具名书信、档案或适用权威记录。"
        "关系候选st-chp3-seci-l26-33-duchess-wanted-ciro-ferri与st-chp3-seci-l26-33-duchess-turin-not-prevented继续待S6。"
    )
    assert not sync.get_group(updated["resolution_note"])
    planned = [dict(item) for item in alignments]
    planned_row = next(item for item in planned if item.get("candidate_id") == CANDIDATE and not item.get("external_source"))
    planned_row.update(updated)

    stats = sync.summarize_by_type([dict(item) for item in candidates], planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == 611
    assert stats["person"]["registered_members"] == 704
    assert stats["person"]["pending_groups"] == 450
    assert stats["person"]["pending_members"] == 451
    assert totals["registered_groups"] == 1020 and totals["registered_members"] == 1198
    assert totals["pending_groups"] == 3749 and totals["pending_members"] == 3763

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物身份复核：Duchess of Savoy（{DATE}）\n\n"
        "- cand-2383由new改为undecided，原组new-person:duchess-of-savoy-5fdc78ee0e撤回，不登记KU。"
        "S.csv#71及第3章p.65只有“Duchess of Savoy”称号，虽有17世纪末和Turin语境，未给个人姓名，也没有书内跨章锚点能对应cand-2380或cand-2381。"
        "不因同属Savoy或头衔相近而合并；关系候选st-chp3-seci-l26-33-duchess-wanted-ciro-ferri、"
        "st-chp3-seci-l26-33-duchess-turin-not-prevented继续待S6。"
        f"\n\n复核后person类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书KU={len(sync.read_csv(TABLES / 'ku-manifest.csv')[1])}。\n"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(sync.read_csv(TABLES / "ku-manifest.csv")[1]),
    )
    summary = (
        "### S3人物身份复核：Duchess of Savoy（2026-10-18）\n\n"
        "cand-2383由new改为undecided，撤回原身份组并暂不登记KU：原书只给出头衔、世纪末语境与Turin关联，"
        "没有具名或跨章身份锚点可将其对应到cand-2380或cand-2381。两条直接关系候选继续待S6。"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, summary + "\n\n" + marker, 1)

    return {
        ALIGNMENT_PATH: csv_text(fields, planned),
        PROCESS_PATH: process_text,
        RESULT_PATH: result_text,
    }, stats, totals


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile the unnamed Duchess of Savoy person candidate.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    outputs, stats, totals = build_outputs()
    print(
        f"S3: {CANDIDATE} new -> undecided; active_person_new_groups="
        f"{stats['person']['pending_groups']}; total_new_groups={totals['pending_groups']}"
    )
    if args.dry_run:
        print("dry-run passed: title-only identity remains ungrouped; no files changed")
        return

    previous = {path: path.read_bytes() if path.exists() else None for path in outputs}
    try:
        for path, content in outputs.items():
            original = previous[path]
            encoding = "utf-8-sig" if original is not None and original.startswith(b"\xef\xbb\xbf") else "utf-8"
            temp = path.with_suffix(path.suffix + ".tmp-s3-duchess")
            temp.write_text(content, encoding=encoding, newline="\n")
        for path in outputs:
            path.with_suffix(path.suffix + ".tmp-s3-duchess").replace(path)
    except Exception:
        for path, original in previous.items():
            temp = path.with_suffix(path.suffix + ".tmp-s3-duchess")
            temp.unlink(missing_ok=True)
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        raise
    print(f"applied: updated {len(outputs)} current S3 records")


if __name__ == "__main__":
    main()
