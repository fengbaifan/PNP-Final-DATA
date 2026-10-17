from __future__ import annotations

import argparse
import re
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
DATE = "2026-10-18"
ANCHOR = "s3-dolfin-and-devonshire-identity-boundaries-20261018"
DEVONSHIRE = "cand-0918"
DEVONSHIRE_CONFLICT = "person-conflict-devonshire-titleholders-20261018"
DOLFIN = "cand-0926"
DOLFIN_GROUP = "new-person:a-daniele-dolfin-new-patriarch-daniele-dol-463e05f412"
DOLFIN_KU = "units/persons/daniele-dolfin-archbishop-of-udine"


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
    parser = argparse.ArgumentParser(description="Keep Daniele Dolfin distinct from Daniele III/IV and hold the Devonshire title conflict pending disaggregation.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    _, manifest = sync.read_csv(MANIFEST)
    by_candidate = {row["candidate_id"]: row for row in candidates}
    rows = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") in {DEVONSHIRE, DOLFIN} and not row.get("external_source")}
    assert set(rows) == {DEVONSHIRE, DOLFIN}
    dev, dolfin = rows[DEVONSHIRE], rows[DOLFIN]
    assert by_candidate[DEVONSHIRE].get("index_entry_id") == "D.csv#20"
    assert by_candidate[DEVONSHIRE].get("index_page_range") == "343n"
    assert by_candidate[DOLFIN].get("index_entry_id") == "D.csv#28"
    assert by_candidate[DOLFIN].get("canonical_name") == "Dolfin, Daniele (Archbishop of Udine)"
    if (
        dev.get("decision") == "conflict"
        and sync.get_group(dev.get("resolution_note", "")) == DEVONSHIRE_CONFLICT
        and "S3 conflict" in dev.get("resolution_note", "")
        and dolfin.get("decision") == "new"
        and sync.get_group(dolfin.get("resolution_note", "")) == DOLFIN_GROUP
        and "S3 distinction adjudication (2026-10-18)" in dolfin.get("resolution_note", "")
        and (not dolfin.get("ku_id") or dolfin.get("ku_id") == DOLFIN_KU)
    ):
        print(f"ALREADY RECONCILED: {DEVONSHIRE}=conflict-pending; {DOLFIN}=distinct new identity group.")
        return 0
    assert dev.get("decision") == "new" and not dev.get("ku_id")
    assert sync.get_group(dev.get("resolution_note", "")) == "new-person:d-devonshire-of-devonshire-of-6ef9026fdd"
    assert dolfin.get("decision") == "new" and not dolfin.get("ku_id")
    assert sync.get_group(dolfin.get("resolution_note", "")) == DOLFIN_GROUP

    index_d = (ROOT / "02-sources/03-Index/03-2-Index-CSV/D.csv").read_text(encoding="utf-8-sig")
    ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    ch10_table = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro_notes_p289_visual-transcription.md").read_text(encoding="utf-8-sig")
    ch13 = (ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md").read_text(encoding="utf-8-sig")
    ch9 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    index_row_28 = next(line for line in index_d.splitlines() if '"Dolfin, Daniele (Archbishop of Udine)"' in line)
    assert "Duke of Devonshire" in ch10 and "late D. of Devonshire" in ch10
    assert "Duke of Devonshire" in ch10_table and "the Duke of Devonshire" in ch13
    assert "His brother, Daniele IV, who died in the same year" in ch9
    assert "In 1759 Tiepolo and his son Gian Domenico were recalled to Udine by a new patriarch, Daniele Dolfin, nephew of Dionisio" in ch9
    assert "343n" in index_row_28 or "D.csv#20" in dev.get("resolution_note", "")

    planned = [dict(row) for row in alignments]
    planned_dev = next(row for row in planned if row.get("alignment_id") == dev.get("alignment_id"))
    original_group = sync.get_group(dev.get("resolution_note", ""))
    planned_dev.update(
        decision="conflict",
        ku_id="",
        process_ref=f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
        resolution_note=(
            "source_ref=entity-candidates.csv#cand-0918;index_entry=D.csv#20;index_pages=343n;"
            "conflict_side_A=chapter10-p289-p290-Duke-of-Devonshire;conflict_side_B=chapter13-p343n-Duke-of-Devonshire;"
            f"original_group_label={original_group};group={DEVONSHIRE_CONFLICT}; "
            "S3 conflict: p.289-290 identifies a Duke of Devonshire as monument subject and as the late Duke in a 1729 client letter; p.343 n.3 lists a Duke of Devonshire among names in the preface to the 1760 Varie Pitture. "
            "The shared hereditary title does not establish one individual across these contexts, and the S1 index candidate D.csv#20 points only to p.343 n. The source-local identity cannot be safely registered as one person. "
            "Keep this candidate in conflict-pending status with no KU; the three p.289-290 direct S2 relation candidates remain pending until the titleholder references are disaggregated. "
            "Next action: identify the period-specific Duke in p.343 n.3 from an authoritative or primary record; if a distinct endpoint is established, create a separate candidate through the backlog and return affected S2 endpoints for remapping. No external identity source was consulted in this decision."
        ),
    )
    planned_dolfin = next(row for row in planned if row.get("alignment_id") == dolfin.get("alignment_id"))
    planned_dolfin["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_dolfin["resolution_note"] = dolfin.get("resolution_note", "").rstrip() + (
        " S3 distinction adjudication (2026-10-18): retain new-person group " + DOLFIN_GROUP + ". "
        "S1 index D.csv#28 labels Daniele Dolfin (Archbishop of Udine), p.253 n.; D.csv#29 and #30 separately identify Daniele III and Daniele IV on pp.252-253 and p.252. "
        "Haskell says Daniele III and IV died in 1729, while the p.253 n.1 subject is a new patriarch acting in 1759 and identified as Dionisio's nephew; this is a distinct source-local person, not either deceased brother. "
        "No external identity claim is added; retain the existing new group for S4 registration."
    )

    before_stats = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(value[key] for value in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals["conflict"] == before_totals["conflict"] + 1
    assert totals["new_candidates"] == before_totals["new_candidates"] - 1
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"] - 1

    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    if f'<a id="{ANCHOR}"></a>' not in process_text:
        process_text = process_text.rstrip() + (
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3身份边界：Daniele Dolfin与Devonshire公爵头衔（{DATE}）\n\n"
            f"- {DOLFIN}保留new组{DOLFIN_GROUP}：索引D.csv#28的Daniele Dolfin（Archbishop of Udine）对应第9章p.253注1所述1759年新任宗主教；既有D.csv#29、#30的Daniele III、Daniele IV均据第9章p.252于1729年去世，不能复用其KU。该新组可进入S4，身份限于书内。\n"
            f"- {DEVONSHIRE}由new改为conflict，组{DEVONSHIRE_CONFLICT}。第10章pp.289-290的Duke of Devonshire与第13章p.343注3、1760年序言语境中的同头衔，未证明是同一世代。无KU；p.289-290的三条直接关系端点保留待证。下一步先以权威或原始记录识别p.343注的公爵；确认不同后再经backlog新增候选并回到S2重映射。未使用外部身份源。\n"
        )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    if "S3身份边界：Daniele Dolfin与Devonshire公爵头衔" not in result_text:
        result_text = result_text.rstrip() + (
            f"\n\n### S3身份边界：Daniele Dolfin与Devonshire公爵头衔（{DATE}）\n\n"
            "cand-0926确认为新身份组，与1729年去世的Daniele III、IV分开；cand-0918改列conflict，保留为未拆分头衔候选，暂不登记KU。"
        )

    with tempfile.TemporaryDirectory(prefix="pnp-s3-dolfin-devonshire-") as temp_name:
        staged = Path(temp_name) / "alignment.csv"
        sync.write_csv(staged, fields, planned)
        writes = {
            ALIGNMENT: staged.read_bytes(),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }
    if args.dry_run:
        print(f"S3 dry-run passed: {DOLFIN} remains new/distinct; {DEVONSHIRE} new->conflict pending disaggregation; conflict={totals['conflict']}; pending={totals['pending_groups']}/{totals['pending_members']}.")
        print("No KU, external identity row, source registry change, or formal relation planned.")
        return 0

    originals = {path: path.read_bytes() for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        raise
    print(f"applied: {DOLFIN} remains new; {DEVONSHIRE}=conflict-pending; no KU or external identity row added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
