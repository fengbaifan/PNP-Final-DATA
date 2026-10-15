"""Classify and refine S2 statements for the p.207 Roomer passage."""
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
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l43-51"
CONTINUATION_ID = "st-chp8-p208-p207-preti-question-continued"
BACKUP_SUFFIX = ".bak-s2-chp8-p207-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "47517b2ed4f5a2fd945376422148d76b29821bed7bbfdf4f66fcf39d02fc0252",
    CANDIDATES: "76cbd424188bc60aed414cd11ab2422edcfc48b3d08e28436f5f64948ba92c9b",
    MENTIONS: "53d2491b373b0f4204a1dcafe75eac9ae4177922d5905baa7d5895d96b632dd9",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "a0b6b741d348cd7ce0cf4f45791d6fdce3dd97b3b35622f0bd7b8d24380c1c6b"

UNSET_IDS = {
    "st-chp8-p207-de-dominici-praised-preti-maniera-grande",
    "st-chp8-p207-giordano-pictures-for-roomer-unknown-two-styles-proposed",
    "st-chp8-p207-haskell-questioned-roomer-reaction-to-preti-venetian-picture-open",
    "st-chp8-p207-preti-cana-picture-recalls-veronese",
    "st-chp8-p207-roomer-held-richest-and-largest-collection-permanent",
    "st-chp8-p207-roomer-patronage-scantily-known-but-important",
    "st-chp8-p207-rubens-feast-may-have-shifted-roomer-taste",
}
NEW_STATEMENT_IDS = {
    "st-chp8-p207-giordano-painted-unidentified-pictures-for-roomer",
    "st-chp8-p207-roomer-rivalled-spanish-viceroys-for-patronage",
}
CANDIDATE_SPECS = [
    (
        "cand-12032",
        "Unidentified pictures Luca Giordano painted for Gaspar Roomer",
        "work",
        "Haskell says Giordano painted pictures for Roomer but that it is impossible to identify them; keep this group distinct from the old-master pictures he apparently forged to tease Roomer.",
        48,
    ),
]
MENTION_SPECS = [
    (
        "m-s2-chp8-p207-giordano-painted-pictures-for-roomer",
        "cand-12032",
        "pictures Giordano painted for him",
        "Unnamed work group painted by Luca Giordano for Roomer; its members and style are unknown and it is distinct from the forged-old-master group.",
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
    segment_text = "\n".join(source_lines[42:51])
    if not segment or (segment["line_start"], segment["line_end"]) != (43, 51):
        raise SystemExit("p.207 segment metadata changed")
    if segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE] or segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.207 source asset or segment fingerprint changed")
    if sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.207 segment text changed since review")

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
    if actual_unset != UNSET_IDS or len(page_rows) != 18:
        raise SystemExit(f"unexpected p.207 statement inventory: unset delta={sorted(actual_unset ^ UNSET_IDS)}, total={len(page_rows)}")
    continuation = by_id.get(CONTINUATION_ID)
    if not continuation or continuation.get("segment_id") != "chp-8:08_CHP-8_sec_i:l53-60":
        raise SystemExit("the linked p.208 completion of the rhetorical question is missing")
    if "relation_candidate" in (continuation.get("qualifiers") or {}):
        raise SystemExit("the linked p.208 completion was already classified; inspect before applying")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")
    if {row[0] for row in CANDIDATE_SPECS} & set(candidate_by_id) or {row[0] for row in MENTION_SPECS} & set(mention_by_id):
        raise SystemExit("a planned candidate or mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12031:
        raise SystemExit("candidate sequence changed since the p.207 review")

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

    rome_mention = mention_by_id.get("m-chp8-p207-006")
    if not rome_mention or rome_mention["candidate_id"] != "cand-4490" or rome_mention["surface_form"] != "Pome":
        raise SystemExit("the p.207 Rome OCR mention no longer matches its expected prestate")
    rome_mention["note"] = "The S0 surface is Pome; the print reads Rome (CHP-8.pdf physical page 5). Preserve the literal OCR span and record the correction here without changing S0."

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
        "st-chp8-p207-de-dominici-praised-preti-maniera-grande", True,
        "Haskell reports that Roomer praised Preti at their first meeting; de Dominici is the reporting source, not the person giving the praise.",
        subject="cand-2223", object_id="cand-2056",
        predicate="roomer_praised_preti_at_first_meeting_as_reported_by_de_dominici",
        claim="Haskell reports from de Dominici, the only source for Roomer's advice, that Roomer praised Mattia Preti at their first meeting for a maniera grande based on drawing, nature and chiaroscuro.",
        qualification="The pronoun 'him' refers to Roomer, the subject whose advice is under discussion. De Dominici is the source of Haskell's report; the cited text is not independently consulted here.",
        mentioned=["cand-2223", "cand-0942", "cand-4835", "cand-2056", "cand-7453"],
        extra={"reported_by_candidate_id": "cand-0942", "speaker": "Haskell reporting de Dominici"},
    )
    update(
        "st-chp8-p207-giordano-pictures-for-roomer-unknown-two-styles-proposed", False,
        "Haskell says the pictures Giordano painted for Roomer cannot be identified and poses two stylistic alternatives as questions; neither style is asserted as fact.",
        predicate="haskell_could_not_identify_roomer_pictures_or_determine_style",
        object_id=None,
        claim="Haskell says the pictures Giordano painted for Roomer cannot be identified and asks whether they followed a new light Venetian manner or continued a tradition of violence.",
        qualification="The alternatives are rhetorical questions, not established descriptions of the unidentified works. The separate statement below records the asserted Giordano-to-Roomer work relationship.",
        mentioned=["cand-1172", "cand-2223", "cand-7451", "cand-7452"],
    )
    update(
        "st-chp8-p207-haskell-questioned-roomer-reaction-to-preti-venetian-picture-open", True,
        "Haskell explicitly asks whether the Venetian Preti painting disappointed Roomer and led to no further commissions, but immediately says evidence is insufficient; this remains a hypothesis, not a factual edge.",
        claim="Haskell asks whether Roomer was disappointed in Preti's Venetian picture and therefore commissioned nothing further from the artist, then says there is too little evidence to answer.",
        qualification="The question is an explicit relation hypothesis about Roomer and the specific Preti picture; the continuation on p.208 states that it is unanswered for lack of evidence.",
        extra={"hypothesis_status": "unanswered; insufficient evidence", "continuation_source_segment_id": "chp-8:08_CHP-8_sec_i:l53-60"},
    )
    update(
        "st-chp8-p207-preti-cana-picture-recalls-veronese", True,
        "Haskell explicitly says the Marriage Feast at Cana deliberately looked back to Veronese; retain this as an attributed stylistic relation.",
        subject="cand-7448", object_id="cand-2755",
        predicate="marriage_feast_at_cana_deliberately_looked_back_to_veronese",
        mentioned=["cand-7448", "cand-2755"],
    )
    update(
        "st-chp8-p207-roomer-held-richest-and-largest-collection-permanent", False,
        "This preserves Haskell's comparative profile of Roomer's wealth and collection; the distinct rivalry with Spanish viceroys is recorded separately as a relation candidate.",
        predicate="haskell_reported_roomer_as_richest_and_his_collection_as_largest_and_permanent",
        claim="Haskell says Roomer was held to be the richest man in Naples and describes his picture collection as the city's largest and permanent.",
        qualification="These are source-attributed comparative descriptions, not formal relations. The rivalry with Spanish viceroys in claims on painters is split out separately.",
        quote_text=excerpt(49, 50, "He was held to be the richest man in Naples", "Above all it was permanent"),
        start_line=49, end_line=50,
        mentioned=["cand-2223", "cand-7407", "cand-1722"],
    )
    update(
        "st-chp8-p207-roomer-patronage-scantily-known-but-important", False,
        "This is Haskell's historiographical assessment of the available evidence and Roomer's cultural importance, not a relation between entities.",
        predicate="haskell_assessed_roomer_patronage_as_scarcely_known_but_important",
        object_id=None,
        extra={"ocr_corrections": [{"source_line": 49, "ocr": "Use", "print": "life", "basis": "CHP-8.pdf physical page 5."}]},
    )
    update(
        "st-chp8-p207-rubens-feast-may-have-shifted-roomer-taste", True,
        "The source proposes that this specific Rubens picture may have stimulated or coincided with Roomer's taste; preserve both alternatives and do not assert causation.",
        extra={"hypothesis_status": "may have stimulated or coincided; unresolved"},
    )

    continuation = by_id[CONTINUATION_ID]
    continuation_q = dict(continuation.get("qualifiers") or {})
    continuation_q["relation_candidate"] = True
    continuation_q["relation_candidate_note"] = "This continuation completes the explicit but unanswered hypothesis about Roomer's reaction to the Preti picture and possible later commissions; Haskell says evidence is insufficient."
    continuation_q["hypothesis_status"] = "unanswered; insufficient evidence"
    continuation["qualifiers"] = continuation_q

    new_statements = [
        {
            "statement_id": "st-chp8-p207-giordano-painted-unidentified-pictures-for-roomer",
            "subject_candidate_id": "cand-12032", "object_candidate_id": "cand-1172",
            "predicate": "unidentified_roomer_pictures_created_by_giordano_for_patron",
            "claim": "Haskell says Luca Giordano painted unidentified pictures for Roomer.",
            "qualification": "The source asserts that such works existed but says their identities cannot be determined. The work group is separate from the forged old masters in cand-7450.",
            "quote": excerpt(48, 48, "it is impossible to tell what pictures Giordano painted for him", "it is impossible to tell what pictures Giordano painted for him"),
            "line": 48, "relation": True,
            "note": "The source asserts an artist-work-patron relation while withholding the works' identities; do not conflate these works with the old masters Giordano apparently forged.",
            "mentioned": ["cand-12032", "cand-1172", "cand-2223"],
            "extra": {"creator_candidate_id": "cand-1172", "patron_candidate_id": "cand-2223", "work_group_candidate_id": "cand-12032"},
        },
        {
            "statement_id": "st-chp8-p207-roomer-rivalled-spanish-viceroys-for-patronage",
            "subject_candidate_id": "cand-2223", "object_candidate_id": "cand-6624",
            "predicate": "roomer_rivalled_spanish_viceroys_for_claims_on_painters",
            "claim": "Haskell describes the Spanish viceroys as Roomer's only rivals in claims on painters and says the officeholders were always changing.",
            "qualification": "The viceroys are an unnamed succession, not a single individual; the source describes rivalry for claims on painters without naming particular commissions.",
            "quote": excerpt(50, 50, "for the Spanish viceroys", "were always changing."),
            "line": 50, "relation": True,
            "note": "The source explicitly identifies Roomer and the Spanish viceroys as rivals in claims on painters; the group and succession remain unnamed.",
            "mentioned": ["cand-2223", "cand-6624"],
            "extra": {"competing_group_candidate_id": "cand-6624", "role": "rival patrons claiming painters"},
        },
    ]
    for spec in new_statements:
        line = spec["line"]
        if normalize(spec["quote"]) not in normalize(source_lines[line - 1]):
            raise SystemExit(f"new statement quote does not match source: {spec['statement_id']}")
        q = {
            "source_line_start": line, "source_line_end": line,
            "printed_page": 207, "pdf_physical_page": 5,
            "claim": spec["claim"], "speaker": "Haskell", "text_layer": "body",
            "qualification": spec["qualification"], "mentioned_candidate_ids": spec["mentioned"],
            "relation_candidate": spec["relation"], "relation_candidate_note": spec["note"],
        }
        if spec.get("extra"):
            q.update(spec["extra"])
        by_id[spec["statement_id"]] = {
            "statement_id": spec["statement_id"], "segment_id": SEGMENT_ID,
            "subject_candidate_id": spec["subject_candidate_id"],
            "object_candidate_id": spec["object_candidate_id"],
            "predicate": spec["predicate"], "qualifiers": q,
            "original_quote": spec["quote"], "origin": "book", "source_file": SOURCE_REL,
        }
    statements = list(by_id.values())

    for row in statements:
        if row.get("segment_id") not in {SEGMENT_ID, "chp-8:08_CHP-8_sec_i:l53-60"}:
            continue
        q = row.get("qualifiers") or {}
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])):
            if candidate_id and candidate_id not in candidate_by_id:
                raise SystemExit(f"p.207/p.208 statement has unresolved candidate: {row['statement_id']} -> {candidate_id}")
        if q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"true p.207 relation candidate has an unexplained open endpoint: {row['statement_id']}")
    final_p207 = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(final_p207) != 20 or sum(row["qualifiers"].get("relation_candidate") is True for row in final_p207) != 17 or sum(row["qualifiers"].get("relation_candidate") is False for row in final_p207) != 3:
        raise SystemExit("unexpected p.207 final classification counts")

    expected_counts = {"statements": 14231, "candidates": 12010, "mentions": 28073, "true": 8921, "false": 3467, "unset": 1843}
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
        "linked_p208_continuation_classified": CONTINUATION_ID,
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [row[0] for row in MENTION_SPECS],
        "corrected_author": {"de Dominici praised Preti": "Roomer praised Preti; de Dominici is the reporter"},
        "ocr_corrections": {"m-chp8-p207-006": "Pome -> Rome", "st-chp8-p207-roomer-patronage-scantily-known-but-important": "Use -> life"},
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
