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

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
GROUP = "new-person:del-lorenzo-rosso-0ec611aff2"
ANCHOR = "s3-del-rosso-index-subentries-crosschapter-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
TARGETS = {
    "cand-2283": {
        "entry": "Q-R.csv#211",
        "subentry": "and Luca Giordano",
        "pages": "212, 213",
        "mention": "m-chp8-p212-055",
    },
    "cand-2284": {
        "entry": "Q-R.csv#212",
        "subentry": "taste",
        "pages": "213",
        "mention": "m-chp8-p212-055",
    },
}


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
    parser = argparse.ArgumentParser(description="Resolve two del Rosso index subentries to the established source-local person group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    base = helper.base
    sync = base.sync
    fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    manifest_paths = {r["card_path"] for r in manifest}
    by_candidate = {r["candidate_id"]: r for r in candidates}
    rows = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") in TARGETS and not r.get("external_source")}
    assert set(rows) == set(TARGETS)
    target_ku = "units/persons/lorenzo-del-rosso"
    if f"04-knowledge/{target_ku}.md" in manifest_paths:
        for cid in TARGETS:
            assert rows[cid].get("decision") == "new"
            assert rows[cid].get("ku_id") == target_ku
            assert sync.get_group(rows[cid].get("resolution_note", "")) == GROUP
        print(f"ALREADY RECONCILED AND REGISTERED: {GROUP}; candidates={len(TARGETS)}; KU={target_ku}.")
        return 0
    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/Q-R.csv").read_text(encoding="utf-8-sig")
    body_text = (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md").read_text(encoding="utf-8-sig")
    assert "Rosso, Lorenzo del" in index_text
    assert "Andrea and Lorenzo themselves may have started their careers in that city" in body_text
    assert "Luca Giordano was their principal artistic agent in Naples" in body_text
    for cid, data in TARGETS.items():
        candidate, row = by_candidate[cid], rows[cid]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("index_entry_id") == data["entry"]
        assert candidate.get("canonical_name") == "Rosso, Lorenzo del"
        assert candidate.get("sub_entry") == data["subentry"]
        assert row.get("decision") in {"undecided", "new"}
        if row.get("decision") == "new":
            assert sync.get_group(row.get("resolution_note", "")) == GROUP

    planned = [dict(r) for r in alignments]
    for cid, data in TARGETS.items():
        row = next(r for r in planned if r.get("candidate_id") == cid and not r.get("external_source"))
        row.update(
            decision="new",
            ku_id="",
            process_ref=PROCESS_REF,
            resolution_note=(
                f"source_ref={data['entry']};index_subentry={data['subentry']};index_pages={data['pages']};group={GROUP};"
                f"S2_cross_reference_mention={data['mention']}@02-sources/02-Markdown/08_CHP-8_sec_i.md#L98-106; "
                "S3 cross-chapter/index-subentry reconciliation 2026-10-18: the main index entry Q-R.csv#210 identifies Lorenzo del Rosso across pp.210-213. "
                f"This subentry is a locator within that same named entry ({data['subentry']}; pp.{data['pages']}), not a distinct person's name. "
                "The p.212 passage names Lorenzo among the del Rosso brothers and the connected p.212-213 discussion continues the same household and Luca Giordano context. "
                f"Group with cand-2282 as {GROUP}; distinct from brothers Andrea, Ottavio, and other family members. "
                "New relative to existing KUs; no external identity record is claimed."
            ),
        )

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(r[key] for r in stats.values()) for key in next(iter(stats.values()))}
    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    if f'<a id="{ANCHOR}"></a>' not in process_text:
        process_text += (
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3索引子项复核：Lorenzo del Rosso组（2026-10-18）\n\n"
            "cand-2283（Q-R.csv#211，and Luca Giordano，pp.212-213）与cand-2284（Q-R.csv#212，taste，p.213）从undecided改为new，并并入cand-2282的new-person:del-lorenzo-rosso-0ec611aff2组。两项是同一索引主条目下对Lorenzo del Rosso的主题／交叉定位，不是新人物。第8章p.212的S2提及m-chp8-p212-055已将Lorenzo置于同一连续段落；p.212-213延续叙述该兄弟家户与Luca Giordano的往来。该组仍与Andrea、Ottavio及其他del Rosso家族成员分开；外部身份未查验，S4将为三条候选映射同一KU。\n"
        )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    if "S3索引子项复核：Lorenzo del Rosso组" not in result_text:
        result_text += (
            f"\n\n### S3索引子项复核：Lorenzo del Rosso组（2026-10-18）\n\n"
            f"cand-2283、cand-2284已并入cand-2282的new身份组new-person:del-lorenzo-rosso-0ec611aff2；"
            "三条候选将在S4映射至同一人物KU。详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
        )
    temp_dir = Path(tempfile.mkdtemp(prefix="pnp-s3-del-rosso-"))
    try:
        stage = temp_dir / "alignment.csv"
        sync.write_csv(stage, fields, planned)
        writes = {
            ALIGNMENT_PATH: stage.read_bytes(),
            PROCESS_PATH: with_bom(process_text + "\n", PROCESS_PATH.read_bytes()),
            RESULT_PATH: with_bom(result_text + "\n", RESULT_PATH.read_bytes()),
        }
    finally:
        for p in temp_dir.glob("*"):
            p.unlink()
        temp_dir.rmdir()
    if args.dry_run:
        print("S3 dry-run passed: cand-2283 and cand-2284 join the existing Lorenzo del Rosso identity group.")
        print(f"new_group={GROUP}; group_members=3; person={stats['person']}; KU_count={len(manifest)}")
        print("No new KU, card, relation, or external identity row planned.")
        return 0
    originals = {p: p.read_bytes() for p in writes}
    try:
        for p, content in writes.items():
            atomic_write(p, content)
    except Exception:
        for p, content in originals.items():
            atomic_write(p, content)
        raise
    print(f"applied: same_new_group={GROUP}; candidates=3; KU_count={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
