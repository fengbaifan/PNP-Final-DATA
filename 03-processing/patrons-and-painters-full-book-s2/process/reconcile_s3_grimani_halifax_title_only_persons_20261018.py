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
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s3-grimani-halifax-title-only-persons-20261018"
REVIEWS = {
    "cand-1234": {
        "index": "G.csv#144",
        "canonical": "Grimani, Doge",
        "group": "new-person:doge-grimani-ee5c26c638",
        "old_anchor": "normalized full-name/explicit-alias anchor (doge grimani), not surname-only similarity.",
        "new_anchor": "normalized source-title anchor ('Doge Grimani'); it identifies the person only by title and surname, not by a full personal name.",
    },
    "cand-1286": {
        "index": "H.csv#1",
        "canonical": "Halifax, Earl of",
        "group": "new-person:halifax-of-d914fc61b9",
        "old_anchor": "normalized full-name/explicit-alias anchor (halifax of), not surname-only similarity.",
        "new_anchor": "normalized source-title anchor ('Earl of Halifax'); it identifies a source-local titleholder, not a full personal name.",
    },
}


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
    parser = argparse.ArgumentParser(description="Correct title-only S3 person rationales without changing their source-local new groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    revised_rows = [dict(row) for row in alignments]
    for candidate_id, review in REVIEWS.items():
        candidate = candidate_by_id[candidate_id]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("index_entry_id") == review["index"]
        assert candidate.get("canonical_name") == review["canonical"]
        target = next(row for row in revised_rows if row.get("candidate_id") == candidate_id and not row.get("external_source"))
        assert target.get("decision") == "new" and not target.get("ku_id")
        assert sync.get_group(target.get("resolution_note", "")) == review["group"]
        assert not any(row.get("candidate_id") == candidate_id and row.get("external_source") for row in alignments)
        if "S3 title-only identity review" in target.get("resolution_note", ""):
            continue
        note = target["resolution_note"]
        note = note.replace("source anchor gives a full personal name.", "source anchor identifies a particular person by title but does not provide a full personal name.", 1)
        assert review["old_anchor"] in note
        note = note.replace(review["old_anchor"], review["new_anchor"], 1)
        if candidate_id == "cand-1234":
            note += (
                " S3 title-only identity review (2026-10-18): retain this as a source-local Doge Grimani person group, without resolving a given name. "
                "The 1745 rebuilding context identifies the officeholder in this account; it is distinct from the generic Doge of Venice institution candidate cand-8728 and from the earlier Cardinal Grimani candidate cand-1233, which remains undecided."
            )
        else:
            note += (
                " S3 title-only identity review (2026-10-18): retain this as a source-local Earl of Halifax person group, without mapping it to a named hereditary titleholder. "
                "Chapter 10 p.286 identifies the speaker in the Queen's Bed Chamber commission account but supplies no given name; no external identity was consulted."
            )
        target.update(
            process_ref=f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
            accessed_date=DATE,
            resolution_note=note,
        )

    for row in revised_rows:
        if row.get("candidate_id") in REVIEWS and not row.get("external_source"):
            assert "S3 title-only identity review" in row.get("resolution_note", "")

    stats = sync.summarize_by_type(candidates, revised_rows)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    before_stats = sync.summarize_by_type(candidates, alignments)
    before_totals = {key: sum(value[key] for value in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert totals == before_totals

    process_text = process_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    if f'<a id="{ANCHOR}"></a>' not in process_text:
        process_text = process_text.rstrip() + (
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物复核：Doge Grimani与Earl of Halifax保留职衔型书内身份（{DATE}）\n\n"
            "- cand-1234（G.csv#144，Doge Grimani）保留原new组，但撤回“完整个人姓名”的判断。第9章p.272将其置于1745年决定重建Pietà教堂的具体情境；卡片只登记书内称谓，不推定其名字。它与通称职务机构cand-8728及较早的Cardinal Grimani候选cand-1233分开；cand-1233仍为undecided。\n"
            "- cand-1286（H.csv#1，Earl of Halifax）保留原new组，但撤回“完整个人姓名”的判断。第10章p.286明确其在Queen’s Bed Chamber委托叙述中的行动角色，未给出名字；不映射至任何外部命名的伯爵。威胁拒付按Haskell报告保留，不写成实际拒付。\n"
            "- 两组均为来源限定的person/titleholder记录，不添加外部身份行或正式关系；各自直接S2关系候选仍待S6。"
        )
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(sync.read_csv(TABLES / "ku-manifest.csv")[1]))
    if "Doge Grimani与Earl of Halifax保留职衔型书内身份" not in result_text:
        result_text = result_text.rstrip() + (
            f"\n\n### S3人物复核：Doge Grimani与Earl of Halifax保留职衔型书内身份（{DATE}）\n\n"
            "cand-1234与cand-1286仍为source-local new组，但裁决理由更正为来源只提供职衔／称谓，不提供完整个人姓名。Doge Grimani只按1745年重建语境登记，且与通称Doge职务候选及Cardinal Grimani候选分开；Earl of Halifax不映射至外部命名的继承人。两项无新KU、外部身份行或正式关系；cand-1233仍待S3。"
        )

    with tempfile.TemporaryDirectory(prefix="pnp-s3-title-only-persons-") as temp_name:
        stage = Path(temp_name) / "alignment.csv"
        sync.write_csv(stage, fields, revised_rows)
        writes = {
            ALIGNMENT: stage.read_bytes(),
            PROCESS: with_bom(process_text + "\n", PROCESS.read_bytes()),
            RESULT: with_bom(result_text + "\n", RESULT.read_bytes()),
        }
    if args.dry_run:
        print("S3 dry-run passed: cand-1234 and cand-1286 remain source-local new person groups; no given name, KU, external identity, or relation is added.")
        return 0
    originals = {path: path.read_bytes() for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        raise
    print("applied: two title-only S3 rationales corrected; decisions and groups unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
