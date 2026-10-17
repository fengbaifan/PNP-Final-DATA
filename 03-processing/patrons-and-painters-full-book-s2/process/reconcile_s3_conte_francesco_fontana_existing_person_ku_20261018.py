from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import register_s4_person_endpoints_assereto_barelli_baretti_bartoli_basadonna_bassi_20261017 as helper  # noqa: E402

sync = helper.base.sync
process_sync = helper.base.process_sync

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CANDIDATE = "cand-1046"
EXISTING_CANDIDATE = "cand-3036"
EXISTING_KU = "units/persons/francesco-fontana"
OLD_GROUP = "new-person:conte-fontana-francesco-f83bd27381"
GROUP = "sg3-ku-units-persons-francesco-fontana"
ANCHOR = "s3-reuse-conte-francesco-fontana-20261018"
DATE = "2026-10-18"


def atomic_write(path: Path, content: bytes) -> None:
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        handle.write(content)
    try:
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def with_bom(text: str, original: bytes) -> bytes:
    raw = text.encode("utf-8")
    return b"\xef\xbb\xbf" + raw if original.startswith(b"\xef\xbb\xbf") else raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Reuse the accepted Francesco Fontana person KU for Conte Francesco Fontana.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    _, manifest = sync.read_csv(MANIFEST)
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE)
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Fontana, Conte Francesco"
    assert candidate.get("index_entry_id") == "F.csv#61"
    assert candidate.get("index_page_range") == "17n"
    target_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    existing_rows = [row for row in alignments if row.get("candidate_id") == EXISTING_CANDIDATE and not row.get("external_source")]
    assert len(target_rows) == len(existing_rows) == 1
    target, existing = target_rows[0], existing_rows[0]
    assert existing.get("decision") == "same" and existing.get("ku_id") == EXISTING_KU
    assert f"04-knowledge/{EXISTING_KU}.md" in {row.get("card_path") for row in manifest}
    assert not any(row.get("candidate_id") == CANDIDATE and row.get("external_source") for row in alignments)

    if target.get("decision") == "same" and target.get("ku_id") == EXISTING_KU and sync.get_group(target.get("resolution_note", "")) == GROUP:
        print(f"ALREADY RECONCILED: {CANDIDATE} -> {EXISTING_KU}.")
        return 0
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == OLD_GROUP

    planned = [dict(row) for row in alignments]
    revised = next(row for row in planned if row.get("alignment_id") == target.get("alignment_id"))
    note = revised.get("resolution_note", "")
    note = note.replace(f"group={OLD_GROUP}", f"group={GROUP}; prior_group={OLD_GROUP}", 1)
    note += (
        f" S3 review ({DATE}): change new to same and reuse {EXISTING_KU}. "
        "The indexed candidate is explicitly ‘Conte Francesco Fontana’ (F.csv#61, p.17n). "
        "The accepted Francesco Fontana card preserves the same chapter 1 p.17 passage, identifies him as the Count addressed by Fulvio Testi, and records the independently documented family identity; the same 1633 letter is already represented by cand-3549 and its addressee endpoint. "
        "This exact source and recipient match supersedes the prior source-local new decision; no duplicate person KU or new external identity claim is needed."
    )
    revised.update(
        ku_id=EXISTING_KU,
        decision="same",
        accessed_date=DATE,
        process_ref=f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
        resolution_note=note,
    )

    before_stats = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(value[key] for value in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals["same_candidates"] == before_totals["same_candidates"] + 1
    assert totals["new_candidates"] == before_totals["new_candidates"] - 1
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"] - 1

    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    if f'<a id="{ANCHOR}"></a>' not in process_text:
        process_text = process_text.rstrip() + (
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物复核：Conte Francesco Fontana复用既有人物KU（{DATE}）\n\n"
            f"cand-1046（F.csv#61，Conte Francesco Fontana）由new改为same，复用[弗朗切斯科·丰塔纳人物卡]"
            f"(../../../04-knowledge/units/persons/francesco-fontana.md)（{EXISTING_KU}）。既有卡已保存第1章p.17同一段落，明确其为Fulvio Testi书信所致的Fontana伯爵；其1633年书信候选cand-3549亦已映射至既有书信卡，书信收信人端点指向此人物。既有卡同时记录家族研究对身份的独立支持。原new组号及理由作为历史保留；不重复建卡，不新增外部身份行或正式关系。该候选的直接关系仍交S6核对既有边及候选对应。"
        )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    if "Conte Francesco Fontana复用既有人物KU" not in result_text:
        result_text = result_text.rstrip() + (
            f"\n\n### S3人物复核：Conte Francesco Fontana复用既有KU（{DATE}）\n\n"
            "cand-1046由new改判same，复用[Francesco Fontana人物卡](../units/persons/francesco-fontana.md)。索引名称、Haskell第1章p.17同一书信段落及既有卡记录的书信收信人身份一致；相关1633年书信已映射至该人物端点。不新建重复KU，关系仍按S6核对。"
        )

    with tempfile.TemporaryDirectory(prefix="pnp-s3-francesco-fontana-") as tmp_name:
        tmp = Path(tmp_name)
        csv_stage = tmp / "alignment.csv"
        sync.write_csv(csv_stage, fields, planned)
        writes = {
            ALIGNMENT: csv_stage.read_bytes(),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }

    if args.dry_run:
        print(f"S3 dry-run passed: {CANDIDATE} new->same {EXISTING_KU}; person pending={totals['pending_groups']}/{totals['pending_members']}; no new KU, external row, or formal relation.")
        return 0

    originals = {path: path.read_bytes() for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        raise
    print(f"applied: {CANDIDATE}->same:{EXISTING_KU}; no new KU, external identity row, or formal relation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
