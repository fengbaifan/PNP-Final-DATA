from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp9-p265-endpoints-20261015")
EXPECTED_TABLE_HASH = "21a25559c723aec0096f24922c5eb6a22a5d8941517d58e94d17b3a375d0f446"
SEGMENT_HASHES = {
    "chp-9:09_CHP-9_intro:l291-301": "3820d49b66ee86388bfe238d2257d81f282963238c24fbf01a771e396f41cc83",
    "chp-9:09_CHP-9_intro:l323-445": "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
REVIEWED_IDS = {
    "st-chp9-p265-sagredo-collected-until-end-of-life",
    "st-chp9-p265-tiepolo-works-recorded-in-1743",
    "st-chp9-p265-tiepolo-ceiling-possibly-posthumous",
    "st-chp9-p265-tiepolo-drawings-probably-acquired-by-sagredo",
    "st-chp9-p265-note8-assessment-and-collection-dispersal",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict[str, object]) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open(row)]
    object_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opens)
    subject_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opens)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opens)
    return len(opens), object_only, subject_only, both


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_HASH:
        raise ValueError("book-statements.jsonl changed since the p.265 review was prepared")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_index = {row["segment_id"]: row for row in segments}
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        segment = segment_index.get(segment_id)
        if segment is None or segment.get("sha256") != expected_hash:
            raise ValueError(f"Reviewed p.265 source segment changed: {segment_id}")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    index = {row["statement_id"]: row for row in rows}
    if not REVIEWED_IDS.issubset(index):
        raise ValueError("One or more p.265 reviewed statements are missing")
    if endpoint_counts(rows) != (393, 247, 46, 100):
        raise ValueError(f"Unexpected global open-endpoint counts: {endpoint_counts(rows)}")
    for statement_id in ("st-chp9-p265-sagredo-collected-until-end-of-life", "st-chp9-p265-tiepolo-works-recorded-in-1743"):
        if not is_open(index[statement_id]):
            raise ValueError(f"Reviewed p.265 statement is no longer open: {statement_id}")
    if "st-chp9-p265-tiepolo-drawings-recorded-in-1743" in index:
        raise ValueError("Atomic p.265 Tiepolo-drawings statement already exists")
    if index["st-chp9-p265-tiepolo-works-recorded-in-1743"].get("subject_candidate_id") != "cand-8618":
        raise ValueError("The p.265 combined Tiepolo-record statement changed")

    collecting = index["st-chp9-p265-sagredo-collected-until-end-of-life"]
    collecting["qualifiers"]["relation_candidate"] = False
    collecting["qualifiers"]["relation_candidate_note"] = "This is an attributed biographical summary of Zaccaria Sagredo's continuing collecting activity, not a transaction or a relation to one identifiable work. Preserve the statement without inventing an endpoint or final acquisition date."
    collecting["qualifiers"].pop("open_endpoint_reason", None)

    recorded = index["st-chp9-p265-tiepolo-works-recorded-in-1743"]
    recorded["subject_candidate_id"] = "cand-8606"
    recorded["object_candidate_id"] = "cand-8618"
    recorded["predicate"] = "unidentified_tiepolo_ceiling_recorded_in_sagredo_inventory_1743"
    recorded["qualifiers"]["claim"] = "Haskell says an unidentified ceiling by Tiepolo was recorded in the 1743 Sagredo inventory."
    recorded["qualifiers"]["qualification"] = "The ceiling is unidentified and may have been commissioned after Zaccaria's death; do not infer that he commissioned or acquired it. The exact inventory record and repository are not supplied."
    recorded["qualifiers"]["mentioned_candidate_ids"] = ["cand-2569", "cand-8606", "cand-8618"]
    recorded["qualifiers"]["relation_candidate_note"] = "The work candidate is the identified source-level ceiling group; the object is the 1743 first-inventory locator named by Haskell later on the same page. The repository and exact record remain unidentified."
    recorded["qualifiers"].pop("open_endpoint_reason", None)
    recorded["original_quote"] = "an unidentified ceiling by him and several drawings were recorded in 1743"

    drawings = json.loads(json.dumps(recorded, ensure_ascii=False))
    drawings["statement_id"] = "st-chp9-p265-tiepolo-drawings-recorded-in-1743"
    drawings["subject_candidate_id"] = "cand-8607"
    drawings["predicate"] = "tiepolo_drawings_recorded_in_sagredo_inventory_1743"
    drawings["qualifiers"]["claim"] = "Haskell says several unidentified drawings by Tiepolo were recorded in the 1743 Sagredo inventory."
    drawings["qualifiers"]["qualification"] = "The drawings are almost certainly acquired by Zaccaria according to Haskell, but no individual sheet or acquisition date is identified. The exact inventory record and repository are not supplied."
    drawings["qualifiers"]["mentioned_candidate_ids"] = ["cand-2569", "cand-8607", "cand-8618"]
    drawings["qualifiers"]["relation_candidate_note"] = "This row records the drawing group separately from the unidentified ceiling; the object is the 1743 first-inventory locator named by Haskell later on the same page. The repository and exact record remain unidentified."
    drawings["original_quote"] = "an unidentified ceiling by him and several drawings were recorded in 1743"
    rows.append(drawings)

    after = endpoint_counts(rows)
    if after != (391, 245, 46, 100):
        raise ValueError(f"Unexpected post-review global open-endpoint counts: {after}")
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")

    print("reviewed=p.265 Sagredo's collecting summary and Tiepolo works recorded in 1743")
    print("resolved=kept the biographical collecting statement nonrelational; split ceiling and drawings and linked each to the source-identified 1743 inventory")
    print("open=p.265 none")
    print(f"statements={len(rows)-1}->{len(rows)}; open_endpoints={endpoint_counts([json.loads(line) for line in raw.decode('utf-8-sig').splitlines() if line.strip()])}->{after}")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(statement_after)}")
    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"Recovery copy already exists: {BACKUP.name}")
    temporary = TABLE.with_name("book-statements.jsonl.tmp-s2-chp9-p265-endpoints-20261015")
    if temporary.exists():
        raise FileExistsError(f"Temporary file already exists: {temporary.name}")
    shutil.copy2(TABLE, BACKUP)
    try:
        temporary.write_bytes(statement_after)
        temporary.replace(TABLE)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={digest(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
