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
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp9-p260-20261015")
EXPECTED_TABLE_HASH = "1ecf31288a47dcc1b169becfc6e59e4852523e75e63946bd48fb6bda4d1533bf"
SEGMENT_HASHES = {
    "chp-9:09_CHP-9_intro:l202-210": "ffbd53ac783c55a991bc4629b6bde3328e0708acce1819a1412f55607387ce6d",
    "chp-9:09_CHP-9_intro:l323-445": "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
    "chp-9:09_CHP-9_intro_notes_p260_visual-transcription:l1-1": "88f6aedbfcbc999f20c7b4965c2ed50c3507df155b810b589ac921b1a3ebbfa0",
}
REVIEWED_IDS = {
    "st-chp9-p260-contemporary-rooms-description",
    "st-chp9-p260-first-half-patronage-moschini",
    "st-chp9-p260-household-employment-general",
    "st-chp9-p260-note8-miani-baglione-list",
    "st-chp9-p260-note7-moschini-volume-iii-page-49",
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


def new_moschini_statement() -> dict[str, object]:
    return {
        "statement_id": "st-chp9-p260-moschini-no-lack-of-support-claim",
        "segment_id": "chp-9:09_CHP-9_intro:l202-210",
        "subject_candidate_id": None,
        "object_candidate_id": None,
        "predicate": "moschini_claimed_no_lack_of_support_for_the_arts",
        "qualifiers": {
            "source_line_start": 208,
            "source_line_end": 208,
            "printed_page": 260,
            "pdf_physical_page": 22,
            "claim": "Haskell reports that Moschini claimed the arts had suffered from no lack of support.",
            "speaker": "Haskell, reporting Abate G. A. Moschini",
            "text_layer": "authorial narrative reporting an attributed proposition",
            "qualification": "Haskell attributes the position to Moschini; note 7 cites volume III, page 49. The citation and underlying proposition are not independently verified here.",
            "mentioned_candidate_ids": ["cand-1709", "cand-8511"],
            "cross_reference_segments": [
                {
                    "segment_id": "chp-9:09_CHP-9_intro:l323-445",
                    "source_line_start": 401,
                    "source_line_end": 401,
                }
            ],
            "footnote_marker": 7,
            "relation_candidate": False,
            "relation_candidate_note": "This is an attributed historiographic proposition about general support for the arts; neither specific patrons nor recipient artists are named, so it is retained as a claim rather than converted into an entity edge. The cited Moschini locator is recorded separately.",
        },
        "original_quote": "the Abate Moschini specifically claimed that the arts had suffered from no lack of support",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }


def new_baglione_statement() -> dict[str, object]:
    return {
        "statement_id": "st-chp9-p260-note8-baglione-household-example",
        "segment_id": "chp-9:09_CHP-9_intro_notes_p260_visual-transcription:l1-1",
        "subject_candidate_id": "cand-8502",
        "object_candidate_id": None,
        "predicate": "baglione_family_listed_as_household_artist_employment_example",
        "qualifiers": {
            "source_line_start": 1,
            "source_line_end": 1,
            "printed_page": 260,
            "pdf_physical_page": 22,
            "claim": "Haskell's note 8 lists the Baglione of Polazzo among household-employment examples, citing Alessandro Longhi parenthetically.",
            "speaker": "Haskell's footnote",
            "text_layer": "footnote claim",
            "qualification": "The note does not identify an individual family member or assign a particular artist to this family. Alessandro Longhi appears as a citation, not an established employment target.",
            "mentioned_candidate_ids": ["cand-8502", "cand-1424"],
            "cross_reference_segments": [
                {
                    "segment_id": "chp-9:09_CHP-9_intro:l323-445",
                    "source_line_start": 402,
                    "source_line_end": 402,
                }
            ],
            "footnote_marker": 8,
            "relation_candidate": True,
            "relation_candidate_note": "The family group is explicitly named, but the artist endpoint is not. Do not treat the parenthetical source citation as an artist-family pairing.",
            "open_endpoint_reason": "The note places the Baglione of Polazzo among household-employment examples but names no particular artist for this family. Alessandro Longhi appears parenthetically as a source citation and is not a proven target; retain the family endpoint and leave the artist unresolved.",
        },
        "original_quote": "the Baglione of Polazzo (Alessandro Longhi)",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro_notes_p260_visual-transcription.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_HASH:
        raise ValueError("book-statements.jsonl changed since the p.260 review was prepared")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_index = {row["segment_id"]: row for row in segments}
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        segment = segment_index.get(segment_id)
        if segment is None or segment.get("sha256") != expected_hash:
            raise ValueError(f"Reviewed p.260 source segment changed: {segment_id}")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    index = {row["statement_id"]: row for row in rows}
    if not REVIEWED_IDS.issubset(index):
        raise ValueError("One or more p.260 reviewed statements are missing")
    if endpoint_counts(rows) != (402, 249, 50, 103):
        raise ValueError(f"Unexpected global open-endpoint counts: {endpoint_counts(rows)}")
    for statement_id in ("st-chp9-p260-contemporary-rooms-description", "st-chp9-p260-first-half-patronage-moschini", "st-chp9-p260-household-employment-general", "st-chp9-p260-note8-miani-baglione-list"):
        if not is_open(index[statement_id]):
            raise ValueError(f"Reviewed p.260 statement is no longer open: {statement_id}")
    if "st-chp9-p260-moschini-no-lack-of-support-claim" in index or "st-chp9-p260-note8-baglione-household-example" in index:
        raise ValueError("A p.260 split statement ID already exists")

    contemporary = index["st-chp9-p260-contemporary-rooms-description"]
    contemporary["subject_candidate_id"] = "cand-8509"
    contemporary["object_candidate_id"] = "cand-8519"
    contemporary["predicate"] = "sebastiano_molino_described_foscarini_rooms_as_venerable_sanctuary"
    contemporary["qualifiers"]["mentioned_candidate_ids"] = ["cand-1053", "cand-8519", "cand-8491", "cand-8499", "cand-8509", "cand-8510"]
    contemporary["qualifiers"]["cross_reference_segments"] = [
        {
            "segment_id": "chp-9:09_CHP-9_intro:l323-445",
            "source_line_start": 400,
            "source_line_end": 400,
        }
    ]
    contemporary["qualifiers"]["relation_candidate_note"] = "Note 6 identifies the contemporary associated with this quotation as Sebastiano Molino and cites his oration; the oration is used as Haskell's source attribution only and was not independently consulted. The described rooms are in Foscarini's palace."
    contemporary["qualifiers"].pop("open_endpoint_reason", None)

    patronage = index["st-chp9-p260-first-half-patronage-moschini"]
    patronage["predicate"] = "certain_artists_received_considerable_patronage_in_first_half_18c"
    patronage["qualifiers"]["claim"] = "Haskell says certain artists at least received considerable patronage during the first half of the eighteenth century."
    patronage["qualifiers"]["qualification"] = "This is Haskell's broad historical summary; the artists and patrons are not individually identified. Moschini's attributed position is recorded separately."
    patronage["qualifiers"]["mentioned_candidate_ids"] = []
    patronage["qualifiers"]["relation_candidate"] = False
    patronage["qualifiers"]["relation_candidate_note"] = "A generalized historical proposition with no identified artist group or patron endpoint; preserve it as a claim without inventing collective entities or formal edges."
    patronage["qualifiers"].pop("open_endpoint_reason", None)

    household = index["st-chp9-p260-household-employment-general"]
    household["qualifiers"]["relation_candidate"] = False
    household["qualifiers"]["relation_candidate_note"] = "This is Haskell's generalized transition to examples rather than a specific family-artist pairing. The Pisani academy and the separately retained note 8 family examples carry the source-level particulars."
    household["qualifiers"].pop("open_endpoint_reason", None)

    miani = index["st-chp9-p260-note8-miani-baglione-list"]
    miani["subject_candidate_id"] = "cand-8501"
    miani["object_candidate_id"] = None
    miani["predicate"] = "miani_family_listed_as_household_artist_employment_example"
    miani["qualifiers"]["claim"] = "Haskell's note 8 lists the Miani of Camerata among household-employment examples, citing Alessandro Longhi parenthetically."
    miani["qualifiers"]["qualification"] = "The note does not identify an individual family member or assign a particular artist to this family. Alessandro Longhi appears as a citation, not an established employment target."
    miani["qualifiers"]["mentioned_candidate_ids"] = ["cand-8501", "cand-1424"]
    miani["qualifiers"]["relation_candidate_note"] = "The family group is explicitly named, but the artist endpoint is not. Do not treat the parenthetical source citation as an artist-family pairing."
    miani["qualifiers"]["open_endpoint_reason"] = "The note places the Miani of Camerata among household-employment examples but names no particular artist for this family. Alessandro Longhi appears parenthetically as a source citation and is not a proven target; retain the family endpoint and leave the artist unresolved."
    miani["original_quote"] = "the Miani of Camerata and"

    rows.extend([new_moschini_statement(), new_baglione_statement()])
    after = endpoint_counts(rows)
    if after != (400, 251, 49, 100):
        raise ValueError(f"Unexpected post-review global open-endpoint counts: {after}")
    statement_after = ("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)).encode("utf-8")

    print("reviewed=p.260 contemporary-room quotation; general patronage claims; household-employment summary and note 8")
    print("resolved=source attribution for the contemporary quotation; split Moschini claim; reclassified general summaries; atomized Miani/Baglione examples")
    print("open=p.260 Miani and Baglione artist-family pairings (artists not identified in note 8)")
    print(f"statements={len(rows)-2}->{len(rows)}; open_endpoints={endpoint_counts([json.loads(line) for line in raw.decode('utf-8-sig').splitlines() if line.strip()])}->{after}")
    print(f"book-statements.jsonl sha256 {digest(raw)}->{digest(statement_after)}")
    if args.preview:
        return 0
    if BACKUP.exists():
        raise FileExistsError(f"Recovery copy already exists: {BACKUP.name}")
    temporary = TABLE.with_name("book-statements.jsonl.tmp-s2-chp9-p260-20261015")
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
