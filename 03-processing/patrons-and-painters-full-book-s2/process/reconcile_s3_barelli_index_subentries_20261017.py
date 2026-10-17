from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import register_s4_person_endpoints_ciarpi_castello_conduitt_corelli_corradini_coypel_20261017 as base  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-reassessment-barelli-index-subentries-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
TARGET_GROUP = "new-person:agostino-barelli-5bf161332b"


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile two Barelli index subentries to one source-local person group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    _, candidates = base.sync.read_csv(ENTITY_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    main_candidate = candidate_by_id["cand-0243"]
    subentry_candidate = candidate_by_id["cand-0244"]
    assert main_candidate.get("canonical_name") == subentry_candidate.get("canonical_name") == "Barelli, Agostino"
    assert main_candidate.get("index_entry_id") == "B.csv#90"
    assert main_candidate.get("sub_entry") == "palace at Nymphenburg"
    assert subentry_candidate.get("index_entry_id") == "B.csv#91"
    assert subentry_candidate.get("sub_entry") == "Theatine church in Munich"
    source_text = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md").read_text(encoding="utf-8-sig")
    assert "the Bolognese architect Agostino Barelli came to" in source_text
    assert "built a church for the Theatines" in source_text and "central block of the royal palace at Nymphenburg" in source_text

    primary = alignment_by_id["cand-0243"]
    target = alignment_by_id["cand-0244"]
    assert primary.get("decision") == "new" and not primary.get("ku_id")
    assert base.sync.get_group(primary.get("resolution_note", "")) == TARGET_GROUP
    assert target.get("decision") == "undecided" and not target.get("ku_id")
    assert not base.sync.get_group(target.get("resolution_note", ""))
    assert f'<a id="{ANCHOR}"></a>' not in PROCESS_PATH.read_text(encoding="utf-8-sig")

    planned = [dict(row) for row in alignments]
    revised = next(row for row in planned if row.get("candidate_id") == "cand-0244" and not row.get("external_source"))
    revised["decision"] = "new"
    revised["process_ref"] = PROCESS_REF
    revised["resolution_note"] += (
        f" S3复核（{DATE}）：原undecided理由已由新增的同页正文锚点补足；本行索引主项与cand-0243完全相同，"
        "两条索引子项分别指向正文同句中Agostino Barelli建造的Theatine教堂与Nymphenburg宫中央建筑，"
        f"故与cand-0243归入同一source-local人物身份组。仅按共名和同一正文人物锚点合组，不据此扩展建筑事实。group={TARGET_GROUP};"
    )
    stats_before = base.sync.summarize_by_type(candidates, alignments)
    stats_after = base.sync.summarize_by_type(candidates, planned)
    total_before = sum(row["pending_members"] for row in stats_before.values())
    total_after = sum(row["pending_members"] for row in stats_after.values())
    assert total_after == total_before + 1
    assert stats_after["person"]["pending_groups"] == stats_before["person"]["pending_groups"]
    assert stats_after["person"]["pending_members"] == stats_before["person"]["pending_members"] + 1
    assert base.sync.get_group(revised["resolution_note"]) == TARGET_GROUP

    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats_after)
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3复核：Agostino Barelli 的两个索引子项并入同一人物组（{DATE}）\n\n"
        "`cand-0244`（B.csv#91，Theatine church in Munich）原为undecided；现与`cand-0243`（B.csv#90，palace at Nymphenburg）"
        f"归入同一new组`{TARGET_GROUP}`。依据是两行索引的规范主项均为“Barelli, Agostino”，页码均为193，且第7章p.193同一句"
        "明确点名Agostino Barelli，并分别叙述Theatines教堂与Nymphenburg宫中央建筑。两个子项是同一人物的索引定位，不是两个新人物；"
        "旧undecided状态及理由保留在alignment行并由本裁决覆盖。待登记组数不变，待登记候选映射增加1条。\n"
    )

    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    result_text, n_new = re.subn(r"new=4,961（4,776个身份组）", "new=4,962（4,776个身份组）", result_text, count=1)
    result_text, n_undecided = re.subn(r"undecided=5,440", "undecided=5,439", result_text, count=1)
    result_text, n_pending = re.subn(
        r"尚待登记([\d,]+)组、([\d,]+)条映射", "尚待登记3,995组、4,010条映射", result_text, count=1
    )
    result_lines = result_text.splitlines()
    enrichment_indexes = [i for i, line in enumerate(result_lines) if line.startswith("| [既有字段表]")]
    assert (n_new, n_undecided, n_pending, len(enrichment_indexes)) == (1, 1, 1, 1)
    result_lines[enrichment_indexes[0]] = "| [既有字段表](../tables/enrichment.jsonl) | 10,831条，其中1,615条 unverified |"
    result_text = "\n".join(result_lines)

    if args.dry_run:
        print(
            f"dry-run passed: cand-0244 undecided->new in existing group; pending_groups="
            f"{stats_after['person']['pending_groups']}; pending_members={total_before}->{total_after}; no files changed"
        )
        return 0

    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: cand-0244 now joins {TARGET_GROUP}; new candidates=4,962; undecided=5,439; pending mappings={total_after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
