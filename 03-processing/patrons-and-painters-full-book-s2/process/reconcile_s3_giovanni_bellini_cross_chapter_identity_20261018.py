from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
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
CANDIDATE = "cand-0270"
GROUP = "new-person:bellini-giovanni-b88f43a625"
ANCHOR = "s3-giovanni-bellini-index-and-cross-chapter-identity-20261018"
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
    parser = argparse.ArgumentParser(description="Resolve the two Bellini index references to Giovanni Bellini and distinguish Gentile Bellini.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    _, manifest = sync.read_csv(MANIFEST)
    candidate = next(row for row in candidates if row.get("candidate_id") == CANDIDATE)
    base_rows = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(base_rows) == 1
    row = base_rows[0]
    target_ku = "units/persons/giovanni-bellini"
    manifest_by_ku = {item.get("ku_id"): item for item in manifest}
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Bellini, Giovanni"
    assert candidate.get("index_entry_id") == "B.csv#117"
    assert candidate.get("index_page_range") == "380, 410"
    assert sync.get_group(row.get("resolution_note", "")) == GROUP
    if row.get("decision") == "new" and row.get("ku_id") == target_ku:
        assert manifest_by_ku[target_ku].get("card_path") == "04-knowledge/units/persons/giovanni-bellini.md"
        assert "S3 identity adjudication (2026-10-18)" in row.get("resolution_note", "")
        print(f"ALREADY ADJUDICATED AND REGISTERED: {CANDIDATE} -> {target_ku}; distinct from Gentile Bellini.")
        return 0
    assert row.get("decision") == "new" and not row.get("ku_id")
    assert target_ku not in manifest_by_ku
    assert not (ROOT / "04-knowledge/units/persons/giovanni-bellini.md").exists()

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_text(encoding="utf-8-sig")
    ch17 = (ROOT / "02-sources/02-Markdown/17_CHP-17_sec_i.md").read_text(encoding="utf-8-sig")
    postscript = (ROOT / "02-sources/02-Markdown/20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    gentile_card = (ROOT / "04-knowledge/units/persons/gentile-bellini.md").read_text(encoding="utf-8-sig")
    assert '"Bellini, Giovanni",,,,"380, 410"' in index_text
    assert '"Bellini, Gentile",,,,198' in index_text
    assert "The Venetian pictures began with Mantegna and Bellini" in ch17
    assert "admiration for the-‘beautiful simplicity’ of Vivarini, Carpaccio and Bellini" in postscript
    assert "Giovanni Bellini" in gentile_card

    note = row.get("resolution_note", "")
    if "S3 identity adjudication (2026-10-18)" not in note:
        row["resolution_note"] = note.rstrip() + (
            " S3 identity adjudication (2026-10-18): retain new-person group new-person:bellini-giovanni-b88f43a625 for Giovanni Bellini. "
            "The index B.csv#117 explicitly maps the two cross-chapter references on pp.380 and 410 to Giovanni Bellini; B.csv#118 separately maps Gentile Bellini to p.198. "
            "Chapter 17 p.380 and the postscript p.410 use the surname Bellini in the indexed contexts. The accepted Gentile Bellini card names Giovanni as his younger brother, further distinguishing the two people. "
            "No Giovanni Bellini KU currently exists, so the source-local new decision stands; this is not an external identity verification."
        )
    stats = sync.summarize_by_type(candidates, alignments)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    if f'<a id="{ANCHOR}"></a>' not in process_text:
        process_text = process_text.rstrip() + (
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3跨章身份裁决：Giovanni Bellini（{DATE}）\n\n"
            "cand-0270保持new，身份组为new-person:bellini-giovanni-b88f43a625。索引B.csv#117将pp.380、410两处Bellini统一列为Giovanni Bellini；同一索引的B.csv#118将Gentile Bellini另列于p.198。第17章p.380记Manfrin收藏中的Bellini，第20章后记p.410记Della Lena对Vivarini、Carpaccio与Bellini的赞赏。既有Gentile Bellini卡称Giovanni为其弟，进一步说明二者是不同人物。当前无Giovanni Bellini卡，因此该组应新建；不主张外部身份核验。"
        )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    if "S3跨章身份裁决：Giovanni Bellini" not in result_text:
        result_text = result_text.rstrip() + (
            f"\n\n### S3跨章身份裁决：Giovanni Bellini（{DATE}）\n\n"
            "cand-0270的pp.380、410索引映射共同指向Giovanni Bellini，并与另列p.198的Gentile Bellini区分；保留为独立new人物组，待S4登记。"
        )

    with tempfile.TemporaryDirectory(prefix="pnp-s3-bellini-") as tmp_name:
        staged = Path(tmp_name) / "alignment.csv"
        sync.write_csv(staged, fields, alignments)
        writes = {
            ALIGNMENT: staged.read_bytes(),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }
    if args.dry_run:
        print(f"S3 dry-run passed: {CANDIDATE} remains new as Giovanni Bellini, distinct from Gentile Bellini; pending={totals['pending_groups']}/{totals['pending_members']}; no KU created.")
        return 0

    originals = {path: path.read_bytes() for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        raise
    print(f"applied: {CANDIDATE} remains new in {GROUP}; index and cross-chapter identity rationale recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
