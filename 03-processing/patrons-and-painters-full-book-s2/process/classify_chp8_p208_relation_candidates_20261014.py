"""Classify and refine S2 statements for the p.208 Roomer passage."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l53-60"
BACKUP_SUFFIX = ".bak-s2-chp8-p208-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "784fc7d4d352d01cc3a071033eaea2e8bd2280d1a2f32e095425a1f57a943733",
    CANDIDATES: "7e64470430b563b90b7c2fe9e271e11fde520b1a1459b1aa385f4289d8e2d3af",
    MENTIONS: "fbc69bd9a1710e5bb73bd85ad38fc0d345b08b5fae9c82a271daa2bf6b33ca21",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "c2128dd7a6a12db5624d7199227a7bcd95737d4987bf660bd05e2ef58f171d8f"

UNSET_IDS = {
    "st-chp8-p208-flemish-still-life-influenced-neapolitans",
    "st-chp8-p208-haskell-asks-if-manner-loose-brushstrokes-tonality",
    "st-chp8-p208-jan-flemish-origin",
    "st-chp8-p208-many-painters-studied-feast",
    "st-chp8-p208-neapolitan-painters-repaid-debt",
    "st-chp8-p208-roomer-gallery-crystallized-north-south",
    "st-chp8-p208-roomer-naturalism-longstanding-love",
}
NEW_STATEMENT_IDS = {
    "st-chp8-p208-giordano-manner-offended-other-connoisseurs",
}
CANDIDATE_SPECS = [
    (
        "cand-12033",
        "Unspecified Neapolitan painters working in still life",
        "term",
        "Unnamed painters in the still-life genre whom Haskell says had little chance to see Flemish examples before the pictures in Roomer's gallery; members are not identified.",
        56,
    ),
    (
        "cand-12034",
        "Unspecified painters who studied Rubens's Feast of Herod",
        "term",
        "Haskell says many other painters studied the picture but names none; do not equate this group with artists breaking away from Caravaggism unless later evidence supports it.",
        56,
    ),
    (
        "cand-12035",
        "Unidentified connoisseurs offended by Luca Giordano's new manner",
        "term",
        "Haskell says Giordano's loose brushwork and lighter tonality offended other connoisseurs; no members are named, and whether these features explain Roomer's rebuke remains a question.",
        54,
    ),
    (
        "cand-12036",
        "Naturalism as Gaspar Roomer's long-standing artistic preference in Haskell's p.208 account",
        "term",
        "Source-local concept described as Roomer's greatest love from early to late life; not aligned with other naturalism candidates until S3.",
        55,
    ),
    (
        "cand-12037",
        "Long-standing relationship between the cultures of North and South Europe in Haskell's p.208 account",
        "term",
        "Abstract cultural relationship that Haskell says Roomer's gallery crystallised; preserve it as the author's interpretation, not a newly verified historical mechanism.",
        56,
    ),
]
MENTION_SPECS = [
    (
        "m-s2-chp8-p208-painters-who-studied-feast",
        "cand-12034",
        "many other painters",
        "Unspecified group said by Haskell to have studied Rubens's Feast of Herod.",
    ),
    (
        "m-s2-chp8-p208-other-connoisseurs-offended",
        "cand-12035",
        "other connoisseurs",
        "Unnamed connoisseurs whom Haskell says Giordano's new manner offended.",
    ),
]
UNCHANGED = object()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after every guard passes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    hashes = {path: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit("one or more tables or source files changed since this reviewed baseline")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("a recovery copy already exists; inspect it before applying this script")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segments = read_jsonl(SEGMENTS)
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    segment_text = "\n".join(source_lines[52:60])
    if not segment or (segment["line_start"], segment["line_end"]) != (53, 60):
        raise SystemExit("p.208 segment metadata changed")
    if segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE] or segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.208 source asset or segment fingerprint changed")
    if sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.208 segment text changed since review")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(by_id) != len(statements) or len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("statement, candidate, or mention IDs are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if actual_unset != UNSET_IDS or len(page_rows) != 24:
        raise SystemExit(f"unexpected p.208 statement inventory: unset delta={sorted(actual_unset ^ UNSET_IDS)}, total={len(page_rows)}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")
    if {row[0] for row in CANDIDATE_SPECS} & set(candidate_by_id) or {row[0] for row in MENTION_SPECS} & set(mention_by_id):
        raise SystemExit("a planned candidate or mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12032:
        raise SystemExit("candidate sequence changed since the p.208 review")

    new_candidates = []
    for candidate_id, name, kind, detail, line in CANDIDATE_SPECS:
        new_candidates.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": kind, "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": detail, "exclude_reason": "",
            "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    for mention_id, candidate_id, surface, note in MENTION_SPECS:
        starts = [i for i in range(len(segment_text)) if segment_text.startswith(surface, i)]
        if len(starts) != 1:
            raise SystemExit(f"expected one exact surface for {mention_id}, got {len(starts)}")
        start = starts[0]
        mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)),
            "note": note,
        })

    def require_mention(mention_id: str, candidate_id: str, surface: str) -> dict:
        row = mention_by_id.get(mention_id)
        if not row or row["candidate_id"] != candidate_id or row["surface_form"] != surface:
            raise SystemExit(f"mention {mention_id} no longer matches expected prestate")
        return row

    painter_group_mention = require_mention("m-chp8-p208-019", "cand-7459", "many of the Neapolitan painters in this genre")
    painter_group_mention["candidate_id"] = "cand-12033"
    painter_group_mention["note"] = "Unnamed Neapolitan painter group in the still-life genre; the paintings they create are separately mapped to cand-7459."
    naturalism_mention = require_mention("m-chp8-p208-007", "cand-2231", "naturalism")
    naturalism_mention["candidate_id"] = "cand-12036"
    naturalism_mention["note"] = "Source-local artistic concept, distinct from the indexed person candidate cand-2231 (Gaspar Roomer)."
    culture_mention = require_mention("m-chp8-p208-017", "cand-2233", "the cultures of the South and North of Europe")
    culture_mention["candidate_id"] = "cand-12037"
    culture_mention["note"] = "Haskell's abstract north-south cultural relationship, not the indexed person Gaspar Roomer."
    require_mention("m-chp8-p208-001", "cand-2056", "Prcti")["note"] = "S0 OCR reads Prcti; print reads Preti (CHP-8.pdf physical page 6). Preserve the source span and record the correction in S2."
    require_mention("m-chp8-p208-004", "cand-7451", "loose brushstrokes and lighter tonahty")["note"] = "S0 OCR reads tonahty; print reads tonality (CHP-8.pdf physical page 6). Preserve the source span and record the correction in S2."
    require_mention("m-chp8-p208-012", "cand-7456", "a set of prints showing scenes from peasant Use")["note"] = "S0 OCR reads Use; print reads life (CHP-8.pdf physical page 6). Candidate identity preserves the printed phrase."
    require_mention("m-chp8-p208-018", "cand-7458", "The Flemish still Eves")["note"] = "S0 OCR reads Eves; print reads lives (CHP-8.pdf physical page 6). Preserve the source span and record the correction in S2."
    require_mention("m-chp8-p208-025", "cand-0613", "Bernardo CavaUino")["note"] = "S0 OCR reads CavaUino; print reads Cavallino (CHP-8.pdf physical page 6)."

    def excerpt(start_line: int, end_line: int, first: str, last: str) -> str:
        source = "\n".join(source_lines[start_line - 1:end_line])
        start, end = source.find(first), source.rfind(last)
        if start < 0 or end < start:
            raise SystemExit(f"expected source phrase missing at L{start_line}-L{end_line}: {first!r} ... {last!r}")
        return source[start:end + len(last)]

    def update(statement_id: str, relation: bool, note: str, *,
               predicate: str | None = None, subject=UNCHANGED, object_id=UNCHANGED,
               claim: str | None = None, qualification: str | None = None,
               quote_text: str | None = None, start_line: int | None = None,
               end_line: int | None = None, mentioned: list[str] | None = None,
               extra: dict | None = None) -> None:
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        if claim is not None:
            q["claim"] = claim
        if qualification is not None:
            q["qualification"] = qualification
        if start_line is not None:
            q["source_line_start"] = start_line
        if end_line is not None:
            q["source_line_end"] = end_line
        if mentioned is not None:
            q["mentioned_candidate_ids"] = list(dict.fromkeys(mentioned))
        if predicate is not None:
            row["predicate"] = predicate
        if subject is not UNCHANGED:
            row["subject_candidate_id"] = subject
        if object_id is not UNCHANGED:
            row["object_candidate_id"] = object_id
        if quote_text is not None:
            row["original_quote"] = quote_text
        if extra:
            q.update(extra)
        row["qualifiers"] = q

    update(
        "st-chp8-p208-flemish-still-life-influenced-neapolitans", True,
        "Haskell says the Flemish still-life pictures must have excited many Neapolitan painters; this is an explicitly qualified influence claim.",
        subject="cand-7458", object_id="cand-12033",
        predicate="flemish_still_life_pictures_must_have_excited_neapolitan_still_life_painters",
        claim="Haskell says Flemish still-life pictures in Roomer's gallery must have excited many Neapolitan painters working in the genre, who otherwise had little chance to see such work.",
        qualification="The source says 'must have'; no individual painters or works are named, and the causal influence remains Haskell's inference.",
        mentioned=["cand-7458", "cand-12033"],
    )
    update(
        "st-chp8-p208-haskell-asks-if-manner-loose-brushstrokes-tonality", False,
        "This is Haskell's open question about which stylistic features constituted Giordano's new manner; the separately stated effect on other connoisseurs is captured below.",
        predicate="haskell_questioned_whether_giordano_rebuke_concerned_loose_brushwork_and_light_tonality",
        claim="Haskell asks whether the new manner for which Roomer rebuked Giordano lay in loose brushstrokes and lighter tonality.",
        qualification="The question leaves open whether these features explain Roomer's rebuke; it does not establish a fact about the patron's reason.",
        mentioned=["cand-1172", "cand-7451"],
        extra={"ocr_corrections": [
            {"source_line": 54, "ocr": "He", "print": "lie", "basis": "CHP-8.pdf physical page 6."},
            {"source_line": 54, "ocr": "tonahty", "print": "tonality", "basis": "CHP-8.pdf physical page 6."},
        ]},
    )
    update(
        "st-chp8-p208-jan-flemish-origin", False,
        "Flemish origin and seemingly low social origins are attributed descriptors of Jan, not relations between distinct entities.",
        predicate="haskell_described_jan_van_den_einden_as_flemish_with_seemingly_low_origins",
        object_id=None,
        qualification="The comparison with Roomer is retained as Haskell's wording; 'seem' remains a source qualification.",
    )
    update(
        "st-chp8-p208-many-painters-studied-feast", True,
        "Haskell explicitly says many other painters studied Rubens's Feast of Herod; the unnamed painter group is retained as an open candidate.",
        subject="cand-4092", object_id="cand-12034",
        predicate="many_other_painters_studied_rubens_feast_of_herod",
        mentioned=["cand-4092", "cand-12034"],
    )
    update(
        "st-chp8-p208-neapolitan-painters-repaid-debt", True,
        "Haskell says Neapolitan still-life painters repaid their debt to the Flemish examples with pictures; the source's metaphor and quality assessment are preserved.",
        subject="cand-12033", object_id="cand-7459",
        predicate="neapolitan_still_life_painters_created_pictures_in_response_to_flemish_examples",
        claim="Haskell says Neapolitan painters in this genre repaid their debt to the Flemish still-life examples with pictures of superb quality.",
        qualification="The 'debt' is Haskell's metaphor for artistic influence. No individual makers or works are named.",
        mentioned=["cand-12033", "cand-7458", "cand-7459"],
    )
    update(
        "st-chp8-p208-roomer-gallery-crystallized-north-south", False,
        "This is Haskell's interpretation of what Roomer's gallery symbolised about long-standing cultural exchange, not a direct historical relation among the cultures.",
        predicate="haskell_interpreted_roomers_gallery_as_crystallising_north_south_cultural_exchange",
        subject="cand-7407", object_id="cand-12037",
        claim="Haskell interprets Roomer's gallery as crystallising a long-standing relationship between the cultures of Southern and Northern Europe.",
        qualification="The claim is an authorial cultural interpretation; the relationship concept is kept source-local pending S3.",
        mentioned=["cand-7407", "cand-12037"],
        extra={"ocr_corrections": [{"source_line": 56, "ocr": "crystafosed", "print": "crystallised", "basis": "CHP-8.pdf physical page 6."}]},
    )
    update(
        "st-chp8-p208-roomer-naturalism-longstanding-love", False,
        "This is a broad account of Roomer's artistic preference across his life, not a relation to a distinct identified work or artist.",
        predicate="haskell_described_naturalism_as_roomers_longstanding_preference",
        subject="cand-2223", object_id="cand-12036",
        claim="Haskell says naturalism seems to have been Roomer's greatest artistic preference from his early gallery to the end of his life.",
        qualification="The preference is Haskell's characterization, and the naturalism concept remains source-local pending S3.",
        mentioned=["cand-2223", "cand-12036"],
        extra={"ocr_corrections": [{"source_line": 55, "ocr": "Use", "print": "life", "basis": "CHP-8.pdf physical page 6."}]},
    )

    update(
        "st-chp8-p208-flemish-still-life-influenced-neapolitans", True,
        "Haskell states a qualified influence from Flemish still-life pictures to the unnamed Neapolitan painter group.",
        mentioned=["cand-7458", "cand-12033"],
    )
    update(
        "st-chp8-p208-roomer-gallery-crystallized-north-south", False,
        "This is Haskell's interpretation of the gallery as a cultural symbol, not a formal relation.",
        subject="cand-7407", object_id="cand-12037",
        mentioned=["cand-7407", "cand-12037"],
    )

    # The index row is Gaspar Roomer; its descriptive subentry is not the entity itself.
    candidate_by_id["cand-2233"]["suggested_type"] = "person"
    candidate_by_id["cand-2233"]["detail"] = "The Q-R index entry identifies Gaspar Roomer; its subentry refers to a cultural relationship in his collection discussion, represented separately by cand-12037."

    new_statement = {
        "statement_id": "st-chp8-p208-giordano-manner-offended-other-connoisseurs",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-7451",
        "object_candidate_id": "cand-12035",
        "predicate": "giordano_new_manner_offended_other_connoisseurs",
        "qualifiers": {
            "source_line_start": 54, "source_line_end": 54,
            "printed_page": 208, "pdf_physical_page": 6,
            "claim": "Haskell says the loose brushstrokes and lighter tonality associated with Giordano's new manner had offended other connoisseurs too.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "Haskell leaves open whether these same stylistic features explain Roomer's rebuke; the statement about other connoisseurs is in a subordinate clause.",
            "mentioned_candidate_ids": ["cand-7451", "cand-12035"],
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly connects Giordano's manner with other connoisseurs' offense; the exact critics remain unnamed.",
            "ocr_corrections": [
                {"source_line": 54, "ocr": "He", "print": "lie", "basis": "CHP-8.pdf physical page 6."},
                {"source_line": 54, "ocr": "tonahty", "print": "tonality", "basis": "CHP-8.pdf physical page 6."},
            ],
        },
        "original_quote": excerpt(54, 54, "Did this new manner He", "which offended other connoisseurs also?"),
        "origin": "book", "source_file": SOURCE_REL,
    }
    if normalize(new_statement["original_quote"]) not in normalize(source_lines[53]):
        raise SystemExit("new statement quote does not match the p.208 source line")
    by_id[new_statement["statement_id"]] = new_statement
    statements = list(by_id.values())

    for row in statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        q = row.get("qualifiers") or {}
        if "relation_candidate" not in q:
            raise SystemExit(f"p.208 statement remains unset: {row['statement_id']}")
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])):
            if candidate_id and candidate_id not in candidate_by_id:
                raise SystemExit(f"p.208 statement has unresolved candidate: {row['statement_id']} -> {candidate_id}")
        if q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"true p.208 relation candidate has an unexplained open endpoint: {row['statement_id']}")
    final_p208 = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(final_p208) != 25 or sum(row["qualifiers"].get("relation_candidate") is True for row in final_p208) != 21 or sum(row["qualifiers"].get("relation_candidate") is False for row in final_p208) != 4:
        raise SystemExit("unexpected p.208 final classification counts")

    expected_counts = {"statements": 14232, "candidates": 12015, "mentions": 28075, "true": 8925, "false": 3471, "unset": 1836}
    actual_counts = {
        "statements": len(statements), "candidates": len(candidates), "mentions": len(mentions),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements),
        "unset": sum("relation_candidate" not in (row.get("qualifiers") or {}) for row in statements),
    }
    if actual_counts != expected_counts:
        raise SystemExit(f"unexpected post-write counts: {actual_counts}")

    outputs = {
        STATEMENTS: jsonl_bytes(statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
    }
    result = {
        "mode": "apply" if args.apply else "dry_run",
        "segment_id": SEGMENT_ID,
        "unclassified_statement_rows_reviewed": len(UNSET_IDS),
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [row[0] for row in MENTION_SPECS],
        "reassigned_existing_mentions": {
            "m-chp8-p208-019": "cand-7459 -> cand-12033",
            "m-chp8-p208-007": "cand-2231 -> cand-12036",
            "m-chp8-p208-017": "cand-2233 -> cand-12037",
        },
        "corrected_index_candidate_type": {"cand-2233": "term -> person"},
        "ocr_corrections": ["Prcti -> Preti", "tonahty -> tonality", "Use -> life", "Eves -> lives", "CavaUino -> Cavallino", "He -> lie", "crystafosed -> crystallised"],
        "post_counts": actual_counts,
        "input_sha256": {path.name: hashes[path] for path in EXPECTED_HASHES},
        "output_sha256": {path.name: sha(data) for path, data in outputs.items()},
        "recovery_copies": [path.name + BACKUP_SUFFIX for path in (STATEMENTS, CANDIDATES, MENTIONS)],
    }
    if args.apply:
        for path in (STATEMENTS, CANDIDATES, MENTIONS):
            backups[path].write_bytes(raw[path])
        for path, data in outputs.items():
            atomic_write(path, data)
        actual_hashes = {path: sha(path.read_bytes()) for path in outputs}
        expected_hashes = {path: sha(data) for path, data in outputs.items()}
        if actual_hashes != expected_hashes:
            raise SystemExit("post-write hash verification failed")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("applied; recovery copies written and post-write hashes verified" if args.apply else "dry-run only; no files changed")


if __name__ == "__main__":
    main()
