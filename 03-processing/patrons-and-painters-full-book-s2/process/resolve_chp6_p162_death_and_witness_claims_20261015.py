from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_DIR = ROOT / "04-knowledge/tables"
STATEMENTS = TABLE_DIR / "book-statements.jsonl"
CANDIDATES = TABLE_DIR / "entity-candidates.csv"
MENTIONS = TABLE_DIR / "mentions.csv"
SEGMENTS = TABLE_DIR / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_v.md"
SEGMENT_ID = "chp-6:06_CHP-6_sec_v:l14-19"
CONTINUATION_SEGMENT_ID = "chp-6:06_CHP-6_sec_v:l21-26"
SOURCE_SHA256 = "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15"
SEGMENT_SHA256 = "8a9810157817ced3926abb637d945cedbb76eb0ef89b81825bd302a8775c2fae"
EXPECTED_HASHES = {
    STATEMENTS: "e69d0e42e0c1d08a3c4249321aa43bb3404ccf88e3415bec2d82d5c6abeb3819",
    CANDIDATES: "e6a1658a7ed5411e0e529d20422b39461d424b565928c2d70029589eb783b3fd",
    MENTIONS: "848b60eabead18621afe649cc78ac75e6cff35367b40f8f9d2bf8a7d1bfab3f4",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp6-p162-death-witness-20261015"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp6-p162-death-witness-20261015"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp6-p162-death-witness-20261015"),
}

NEW_CANDIDATE = {
    "candidate_id": "cand-12410",
    "index_entry_id": "",
    "canonical_name": "Death of Pope Clement IX as the temporal boundary for the abandoned S. Maria Maggiore scheme",
    "index_page_range": "",
    "suggested_type": "event",
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "Haskell says the tribune-remodelling and burial scheme was dropped after Clement IX's death. The source supplies no date here and does not say the death caused the decision.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{SEGMENT_ID}#L18",
}
NEW_MENTION = {
    "mention_id": "m-chp6-p162-clement-ix-death",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-12410",
    "surface_form": "after his death",
    "start_char": "1413",
    "end_char": "1428",
    "note": "Temporal reference to Clement IX's death; the statement asserts sequence, not causation.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open(row: dict) -> bool:
    q = row.get("qualifiers") or {}
    return q.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def csv_bytes(rows: list[dict], fields: list[str], has_bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig" if has_bom else "utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if digest(raw[path]) != expected:
            raise ValueError(f"protected table changed: {path.name} ({digest(raw[path])})")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 6 source asset changed")
    segment_rows = {
        row["segment_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLE_DIR / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    segment = segment_rows.get(SEGMENT_ID)
    continuation = segment_rows.get(CONTINUATION_SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise ValueError("reviewed p.162 source segment changed")
    if not continuation or continuation.get("asset_sha256") != SOURCE_SHA256:
        raise ValueError("p.163 continuation segment is missing or changed")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(lines[13:19])
    if digest(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("p.162 source text changed")
    scheme_quote = "A plan of Clement IX to remodel the tribune of S. Maria Maggiore, and thus provide a burial-place for himself even more imposing than those of Sixtus V and Paul V in the same church, was dropped after his death"
    if scheme_quote not in segment_text or segment_text[1413:1428] != NEW_MENTION["surface_form"]:
        raise ValueError("p.162 scheme phrase or death mention no longer matches the source")
    if not lines[21].startswith("1685?"):
        raise ValueError("expected OCR date on p.163 continuation changed")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    scheme = by_id.get("st-chp6-p162-v1-13")
    witness = by_id.get("st-chp6-p162-v1-25")
    if not scheme or scheme.get("subject_candidate_id") != "cand-6496" or scheme.get("object_candidate_id"):
        raise ValueError("reviewed Clement IX scheme statement changed")
    if not witness or witness.get("subject_candidate_id") != "cand-6510" or witness.get("object_candidate_id"):
        raise ValueError("reviewed unnamed-witness statement changed")
    if (witness.get("qualifiers") or {}).get("relation_candidate") is not True:
        raise ValueError("unnamed-witness statement is no longer a relation candidate")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_reader = csv.DictReader(handle)
        candidate_fields = candidate_reader.fieldnames
        candidates = list(candidate_reader)
    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        mention_reader = csv.DictReader(handle)
        mention_fields = mention_reader.fieldnames
        mentions = list(mention_reader)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if NEW_CANDIDATE["candidate_id"] in candidate_ids or NEW_MENTION["mention_id"] in mention_ids:
        raise ValueError("new p.162 candidate or mention ID already exists")

    open_before = sum(is_open(row) for row in statements)
    no_reason_before = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    true_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    false_before = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements)
    if (open_before, no_reason_before, true_before, false_before, len(statements)) != (375, 54, 10398, 4753, 15151):
        raise ValueError("unexpected pre-edit S2 statement counts")

    scheme["object_candidate_id"] = "cand-12410"
    scheme["original_quote"] = scheme_quote
    scheme_q = scheme["qualifiers"]
    scheme_q["pdf_physical_page"] = 17
    scheme_q["qualification"] = "The plan is not a completed burial project. Footnote 3 cites Pastor, XIV, p. 558 for the scheme; that locator is recorded separately and the cited page was not independently consulted. 'After his death' establishes sequence, not causation."
    scheme_q["mentioned_candidate_ids"] = list(dict.fromkeys(
        scheme_q.get("mentioned_candidate_ids", []) + ["cand-12410"]
    ))
    scheme_q["relation_candidate_note"] = "The source explicitly states that the proposed scheme was dropped after Clement IX's death; the death is represented only as a temporal boundary."

    witness["subject_candidate_id"] = None
    witness["object_candidate_id"] = None
    witness["predicate"] = "quote_attributed_to_unnamed_witness_in_1685"
    witness["original_quote"] = "‘La misère est déjà très grande à Rome, et le gouvernement odieux, et haï extrêmement’, wrote another witness in"
    witness_q = witness["qualifiers"]
    witness_q["relation_candidate"] = False
    witness_q["pdf_physical_page"] = 17
    witness_q["claim"] = "Haskell quotes a second, unnamed witness saying that misery in Rome was already very great and its government odious and extremely hated; the source dates the statement to 1685 on the next page."
    witness_q["qualification"] = "The speaker remains distinct from the French envoy in the Basadonna anecdote. The French quotation itself ends on p.162; only the attribution date continues across the page break. P.163 note 1 cites Michaud, vol. I, p. 68, and warns readers to account for French hostility toward the Pope; the cited page was not independently consulted."
    witness_q["continuation_segment_id"] = CONTINUATION_SEGMENT_ID
    witness_q["continuation_source_line"] = 22
    witness_q["continuation_printed_page"] = 163
    witness_q["continuation_pdf_physical_page"] = 18
    witness_q["continuation_text"] = "1685."
    witness_q["ocr_corrections"] = [{
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
        "source_line": 22,
        "ocr": "1685?",
        "print": "1685.",
        "basis": "CHP-6.pdf physical page 18, printed p.163; footnote marker 1 follows the period.",
    }]
    witness_q["relation_candidate_note"] = "This row preserves Haskell's source-attributed quotation and unnamed speaker; a quoted assertion is not an entity-to-entity relation."
    witness_q.pop("open_endpoint_reason", None)

    candidates.append(NEW_CANDIDATE)
    mentions.append(NEW_MENTION)
    outputs = {
        STATEMENTS: "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements).encode("utf-8"),
        CANDIDATES: csv_bytes(candidates, candidate_fields, raw[CANDIDATES].startswith(b"\xef\xbb\xbf")),
        MENTIONS: csv_bytes(mentions, mention_fields, raw[MENTIONS].startswith(b"\xef\xbb\xbf")),
    }
    open_after = sum(is_open(row) for row in statements)
    no_reason_after = sum(
        is_open(row) and not (row.get("qualifiers") or {}).get("open_endpoint_reason") for row in statements
    )
    true_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements)
    false_after = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements)
    if (open_after, no_reason_after, true_after, false_after, len(statements)) != (373, 52, 10397, 4754, 15151):
        raise ValueError(f"unexpected resulting S2 statement state: {(open_after, no_reason_after, true_after, false_after, len(statements))}")

    print("reviewed=chapter 6 p.162; completed the scheme-to-death sequence and reclassified the attributed quotation as a non-relation claim")
    print("changes=1 death-event candidate and exact mention; 1 missing event endpoint completed; 1 quote-attribution row reclassified; p.163 continuation and OCR date linked")
    print(f"open_endpoints={open_before}->{open_after}; open_without_reason={no_reason_before}->{no_reason_after}; relation_true={true_after}; relation_false={false_after}")
    for path, output in outputs.items():
        print(f"{path.name} sha256 {digest(raw[path])}->{digest(output)}")
    if args.preview:
        return 0

    for backup in BACKUPS.values():
        if backup.exists():
            raise FileExistsError(f"recovery copy already exists: {backup.name}")
    temps = {path: path.with_name(path.name + ".tmp-s2-chp6-p162-death-witness-20261015") for path in outputs}
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("protected temporary output already exists")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, output in outputs.items():
            temps[path].write_bytes(output)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            shutil.copy2(backup, path)
        raise
    print("backups=" + ", ".join(path.name for path in BACKUPS.values()))
    print("applied_hashes=" + ", ".join(f"{path.name}:{digest(path.read_bytes())}" for path in outputs))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
