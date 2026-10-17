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

base = helper.base
sync = base.sync
process_sync = base.process_sync

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CANDIDATE = "cand-0167"
EXISTING_KU = "units/persons/gio-gasparo-baldoini"
EXISTING_CANDIDATE = "cand-3048"
GROUP = "sg3-ku-units-persons-gio-gasparo-baldoini"
ANCHOR = "s3-reuse-baldoini-existing-person-ku-20261018"
DATE = "2026-10-18"


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    parser = argparse.ArgumentParser(description="Reuse the accepted Giovanni Gaspare Baldoino KU for the indexed Baldoini candidate.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    _, manifest = sync.read_csv(MANIFEST)
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE)
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Baldoini, Giovanni Gasparo"
    assert candidate.get("index_entry_id") == "B.csv#14"
    assert candidate.get("index_page_range") == "6n"
    base_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    existing_rows = [row for row in alignments if row.get("candidate_id") == EXISTING_CANDIDATE and not row.get("external_source")]
    assert len(base_rows) == len(existing_rows) == 1
    base, existing = base_rows[0], existing_rows[0]
    manifest_paths = {row.get("card_path") for row in manifest}
    assert f"04-knowledge/{EXISTING_KU}.md" in manifest_paths
    assert existing.get("decision") == "same" and existing.get("ku_id") == EXISTING_KU
    assert not any(row.get("candidate_id") == CANDIDATE and row.get("external_source") for row in alignments)
    if base.get("decision") == "same" and base.get("ku_id") == EXISTING_KU and sync.get_group(base.get("resolution_note", "")) == GROUP:
        print(f"ALREADY RECONCILED: {CANDIDATE} -> {EXISTING_KU}.")
        return 0
    assert base.get("decision") == "new" and not base.get("ku_id")
    assert sync.get_group(base.get("resolution_note", "")) == "new-person:baldoini-gasparo-giovanni-5f338a89ac"

    planned = [dict(row) for row in alignments]
    target = next(row for row in planned if row.get("alignment_id") == base.get("alignment_id"))
    target.update(
        ku_id=EXISTING_KU,
        decision="same",
        accessed_date=DATE,
        process_ref=f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
        resolution_note=(
            "source_ref=candidate=cand-0167;index_entry=B.csv#14;index_pages=6n;"
            "s2_mentions=m-chp1-seci-0105@02-sources/02-Markdown/01_CHP-1_sec_i.md#L38-47[Gio. Gasparo Baldoini]; "
            f"group={GROUP}; S3 review ({DATE}): change new to same and reuse {EXISTING_KU}. "
            "The chapter 1 note identifies Gio. Gasparo Baldoini as appointed by Cardinal Maurizio di Savoia as 'per nostro pittore'. "
            "The accepted Baldoino card records this exact source passage and aligns the abbreviated chapter form with Giovanni Gaspare Baldoino/Baudoin using separately documented name variants and patronage context. "
            "The indexed form Baldoini is therefore the same painter already represented by the accepted KU; no duplicate person card or new external identity claim is added."
        ),
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
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物复核：Baldoini候选复用既有人物KU（{DATE}）\n\n"
            f"cand-0167（B.csv#14，Gio. Gasparo Baldoini）由new改为same，复用[乔瓦尼·加斯帕雷·巴尔多伊诺（Giovanni Gaspare Baldoino）]"
            f"(../../../04-knowledge/units/persons/gio-gasparo-baldoini.md)（{EXISTING_KU}）。第1章注释记其由Maurizio di Savoia任命为“per nostro pittore”；"
            "既有卡已保存这条原文，并以独立记录核对Gio. Gasparo Baldoini与Giovanni Gaspare Baldoino/Baudoin的名字变体及赞助语境。"
            "故索引形式Baldoini归入同一人物；不新建重复KU，不新增外部身份行或正式关系。"
        )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    if "Baldoini候选复用既有人物KU" not in result_text:
        result_text = result_text.rstrip() + (
            f"\n\n### S3人物复核：Baldoini候选复用既有KU（{DATE}）\n\n"
            f"cand-0167改判same并映射至既有[Giovanni Gaspare Baldoino KU](../units/persons/gio-gasparo-baldoini.md)；"
            "第1章任命注释与该卡已保存的同段来源及姓名变体核对相符，没有新增卡片。"
        )

    with tempfile.TemporaryDirectory(prefix="pnp-s3-baldoini-") as tmp_name:
        tmp = Path(tmp_name)
        csv_stage = tmp / "alignment.csv"
        sync.write_csv(csv_stage, fields, planned)
        writes = {
            ALIGNMENT: csv_stage.read_bytes(),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }

    if args.dry_run:
        print(f"S3 dry-run passed: {CANDIDATE} new->same {EXISTING_KU}; person pending={totals['pending_groups']}/{totals['pending_members']}; no external row or KU added.")
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
