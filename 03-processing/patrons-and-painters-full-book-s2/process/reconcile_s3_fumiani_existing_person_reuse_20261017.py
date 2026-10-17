from __future__ import annotations

import argparse
import re
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
KU = "units/persons/giannantonio-fumiani"
CARD = "04-knowledge/units/persons/giannantonio-fumiani.md"
URL = "https://www.treccani.it/enciclopedia/giovanni-antonio-fumiani_(Dizionario-Biografico)/"
SOURCE = "Treccani, Dizionario Biografico degli Italiani"
DATE = "2026-10-17"
ANCHOR = "s3-reuse-fumiani-existing-identity-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
TARGETS = {
    "cand-1087": {
        "old_decision": "new",
        "old_group": "new-person:fumiani-giannantonio-09eeb0cf67",
        "note": (
            "source_ref=F.csv#104;S2_mentions=m-chp8-p227-fumiani,m-chp8-p232-fumiani,m-chp8-p233-fumiani-contextual,m-chp8-p234-fumiani-name,m-chp8-p234-fumiani-1,m-chp8-p234-fumiani-3; "
            "S3 cross-chapter identity correction 2026-10-17: index F.csv#104 gives Fumiani, Giannantonio for pp.227,232; p.234 supplies the same artist in the Grand Prince Ferdinand context. "
            "Reuse existing units/persons/giannantonio-fumiani: its front-matter Plate 40b source reads GiannAntonio Fumiani, and the existing card's Treccani DBI entry is headed Giovanni Antonio Fumiani and discusses his commission of La lapidazione di Zaccaria by Ferdinando. "
            "These name forms and artist-patron context support one identity. Supersedes prior S3 new group new-person:fumiani-giannantonio-09eeb0cf67; p.234 OCR form Giannaritonio is preserved and not silently corrected. "
            "Reuse the existing KU; do not create a duplicate person card. The three p.232-234 relation candidates remain for S6."
        ),
    },
    "cand-1088": {
        "old_decision": "undecided",
        "old_group": "",
        "note": (
            "source_ref=F.csv#105;index_subentry=and Grand Prince Ferdinand;index_page=234; "
            "S3 cross-chapter identity resolution 2026-10-17: the index subentry points to the p.234 passage whose mapped body mention m-chp8-p234-fumiani-name identifies Giannaritonio Fumiani in relation to the Grand Prince. "
            "This is an index locator for the same person as cand-1087, not a separate person; the existing units/persons/giannantonio-fumiani card records the related plate-name form GiannAntonio Fumiani, and Treccani DBI identifies Giovanni Antonio Fumiani in the same Grand Prince commission context. "
            "Set same to the existing KU. OCR form Giannaritonio is retained without correction. This resolves the former missing-body-anchor undecided state without asserting that the p.234 work identification is certain."
        ),
    },
}


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(content)
    try:
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def with_bom(text: str, original: bytes | None = None) -> bytes:
    encoded = text.encode("utf-8")
    if original is None or original.startswith(b"\xef\xbb\xbf"):
        return b"\xef\xbb\xbf" + encoded
    return encoded


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve full-book Fumiani person candidates to the existing accepted KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base = helper.base
    sync = base.sync
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert KU in manifest_by_ku and manifest_by_ku[KU]["card_path"] == CARD
    assert (ROOT / CARD).exists()
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_alignment = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") in TARGETS and not row.get("external_source")
    }
    assert set(candidate_alignment) == set(TARGETS)
    for cid, data in TARGETS.items():
        row = candidate_alignment[cid]
        assert row["decision"] == data["old_decision"] or (
            row["decision"] == "same" and row.get("ku_id") == KU
        ), (cid, row["decision"], row.get("ku_id"))
        if row["decision"] == data["old_decision"] and data["old_decision"] == "new":
            assert base.sync.get_group(row.get("resolution_note", "")) == data["old_group"]
        assert candidate_by_id[cid]["suggested_type"] == "person"
    existing_external = [
        row for row in alignments
        if row.get("candidate_id") == "cand-1087" and row.get("external_source") == SOURCE and row.get("external_id") == URL
    ]
    assert len(existing_external) <= 1

    planned = [dict(row) for row in alignments]
    for cid, data in TARGETS.items():
        row = next(r for r in planned if r.get("candidate_id") == cid and not r.get("external_source"))
        row["decision"] = "same"
        row["ku_id"] = KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = data["note"]

    if not existing_external:
        max_id = max(
            (int(m.group(1)) for row in alignments if (m := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))),
            default=0,
        )
        planned.append({
            "alignment_id": f"aln-{max_id + 1:05d}",
            "candidate_id": "cand-1087",
            "ku_id": KU,
            "external_source": SOURCE,
            "external_id": URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": PROCESS_REF,
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity comparison only: Laura Mocci, ‘FUMIANI, Giovanni Antonio,’ Dizionario Biografico degli Italiani, vol. 50 (1998), "
                "heading identifies the person as Giovanni Antonio Fumiani; biography reports his work for Ferdinando and his late-century commission of La lapidazione di Zaccaria. "
                "Compared with Haskell index F.csv#104 and #105, ch.8 pp.232-234, and the existing card's front-matter Plate 40b form GiannAntonio Fumiani. "
                "This supports person identity; it does not settle the identity or completion history of the separate p.234 work candidate."
            ),
        })

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    if f'<a id="{ANCHOR}"></a>' not in process_text:
        process_text += (
            f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3跨章复核：Fumiani候选复用既有人物KU（{DATE}）\n\n"
            "- cand-1087（原S3 new组 new-person:fumiani-giannantonio-09eeb0cf67）改判same至units/persons/giannantonio-fumiani。索引F.csv#104列Giannantonio Fumiani及pp.227、232；第8章p.234的姓名和Grand Prince Ferdinand语境与既有卡图版40b的GiannAntonio Fumiani相连。Treccani DBI《意大利人传记辞典》第50卷（1998）条目以Giovanni Antonio Fumiani为题，并记其受Ferdinando委托创作《撒迦利亚被石击》。姓名变体与画家—赞助人语境支持复用同一人物KU；旧new判断已由本条更正，不另建重复人物卡。\n"
            "- cand-1088（索引F.csv#105，子项and Grand Prince Ferdinand，p.234）改判same至同一KU。该索引子项定位到已映射在cand-1087下的p.234人物提及，不作为第二个人物；OCR形式Giannaritonio保留，不据此静默校正。\n"
            "- 外部身份比较行登记Treccani DBI URL及访问日期2026-10-17，只支持人物身份。p.234具体作品识别仍保留原有不确定性；cand-1090及cand-7939的作品身份裁决不在本次变更内。直接关系候选st-chp8-p232-fumiani-david-instruction、st-chp8-p233-loth-and-responsive-artist、st-chp8-p234-fumiani-option-to-paint-david继续待S6。\n"
        )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    if "S3跨章复核：Fumiani候选复用既有人物KU" not in result_text:
        result_text += (
            f"\n\n### S3跨章复核：Fumiani候选复用既有人物KU（{DATE}）\n\n"
            "cand-1087与索引子项候选cand-1088均映射至既有人物KU units/persons/giannantonio-fumiani；"
            "Treccani DBI身份对照和Haskell索引、p.234语境支持同一人物。cand-1087旧S3 new组判断已更正，未新增KU。"
            "Giannaritonio OCR形式保留；p.234作品识别仍待证，3条直接关系候选待S6。"
            f"详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
        )

    temp_dir = Path(tempfile.mkdtemp(prefix="pnp-s3-fumiani-"))
    try:
        staged = temp_dir / "alignment.csv"
        sync.write_csv(staged, alignment_fields, planned)
        writes = {
            ALIGNMENT_PATH: staged.read_bytes(),
            PROCESS_PATH: with_bom(process_text + "\n", PROCESS_PATH.read_bytes()),
            RESULT_PATH: with_bom(result_text + "\n", RESULT_PATH.read_bytes()),
        }
    finally:
        for path in temp_dir.glob("*"):
            path.unlink()
        temp_dir.rmdir()

    if args.dry_run:
        print("S3 dry-run passed: cand-1087 and cand-1088 resolve to the existing Fumiani person KU.")
        print(f"external_identity_rows_added={0 if existing_external else 1}; person_groups={stats['person']}; KU={len(manifest)}")
        print("No KU, card, relation, work-decision, or source-registry changes planned.")
        return 0

    originals = {path: path.read_bytes() for path in writes}
    try:
        for path, content in writes.items():
            atomic_write(path, content)
    except Exception:
        for path, content in originals.items():
            atomic_write(path, content)
        raise
    print(
        f"applied: same_mappings=2; reused={KU}; external_identity_rows_added={0 if existing_external else 1}; "
        f"KU={len(manifest)}; works_and_relations_unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
