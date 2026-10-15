from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l147-193"
SEGMENT_SHA = "eecca3166cf5e2c76b830b696b314e5c2b6f3cec09b463643578f0b0d44d1c4a"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l147-193-classification-20261013"
EXPECTED = {
    "book-statements.jsonl": "829a0c80a6865ba88a64e2e5c75ffa67cb6be581c9192d941eecab210f285a1f",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "80f08cbdfb94b733bb556b8b7d078e93392e2e4a38a6daf9db837d2a6aff710d",
}
UNSET_SPECIAL = {
    "st-chp2-secii-l147-193-astrology-surveillance-inference",
    "st-chp2-secii-l147-193-barozzi-francesco-cross-section",
    "st-chp2-secii-l147-193-chapter1-crossref",
    "st-chp2-secii-l147-193-epigram-origin-pointer",
    "st-chp2-secii-l147-193-haskell-ginnasi-critique",
    "st-chp2-secii-l147-193-internal-crossref-to-astrology-note",
    "st-chp2-secii-l147-193-passeri-version-caveat",
}
SPECIAL_NOTES = {
    "st-chp2-secii-l147-193-astrology-surveillance-inference": (
        "This preserves Haskell's explicit inference that Campanella's surveillance was connected with Urban VIII's "
        "astrological activities. The two underlying person relations are recorded separately; this broad link between "
        "activities has no independently identified event endpoints and is not normalized as a formal entity relation."
    ),
    "st-chp2-secii-l147-193-barozzi-francesco-cross-section": (
        "This is a bibliographic locator for the following section's description of Francesco Barberini, not a substantive relation claim."
    ),
    "st-chp2-secii-l147-193-chapter1-crossref": (
        "This is an internal navigation pointer to Chapter 1, p. 11, note 1; it does not assert an entity relation."
    ),
    "st-chp2-secii-l147-193-epigram-origin-pointer": (
        "This identifies an epigram and points readers to sources discussing its origins; it does not itself assert an origin attribution."
    ),
    "st-chp2-secii-l147-193-haskell-ginnasi-critique": (
        "This is Haskell's historiographical critique of Pastor's claim, based on a published document and Venetian-envoy reports; "
        "the source argument is retained, while its evidence references and the separate Ginnasi claims remain linked."
    ),
    "st-chp2-secii-l147-193-internal-crossref-to-astrology-note": (
        "This is a footnote navigation pointer to p. 40, note 3, not an entity relation; the substantive claims in that note are recorded separately."
    ),
    "st-chp2-secii-l147-193-passeri-version-caveat": (
        "This is a source-version caveat: Haskell identifies Passeri's account as one version and notes that others exist; it is not an entity relation."
    ),
}
GENERIC_CITATION_NOTE = (
    "This row records a bibliographic or documentary locator. The cited source remains attached as provenance, "
    "but the locator itself does not assert a substantive relation between entities."
)
ASTROLOGY_ID = "st-chp2-secii-l147-193-astrology-surveillance-inference"
SURVEILLANCE_ID = "st-chp2-secii-l147-193-campanella-surveillance"
RESEARCH_ID = "st-chp2-secii-l147-193-campanella-urban-research"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def append_unique(items: list[str], value: str) -> list[str]:
    return items if value in items else [*items, value]


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify footnote citations and refine p.40 note evidence in CHP-2 L147-193.")
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected notes segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset_rows = [
        row for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    unset_ids = {row["statement_id"] for row in unset_rows}
    citation_ids = {row["statement_id"] for row in unset_rows if row.get("predicate") == "footnote_citation"}
    noncitation_ids = unset_ids - citation_ids
    if len(unset_ids) != 67 or len(citation_ids) != 60 or noncitation_ids != UNSET_SPECIAL:
        raise SystemExit(
            f"unexpected p.40 notes unset set: count={len(unset_ids)}, citations={len(citation_ids)}, noncitations={sorted(noncitation_ids)}"
        )
    for row_id in (ASTROLOGY_ID, SURVEILLANCE_ID, RESEARCH_ID):
        if row_id not in statement_by_id:
            raise SystemExit(f"expected substantive p.40 note statement is missing: {row_id}")
    if statement_by_id[SURVEILLANCE_ID].get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("the existing Barberini-Campanella surveillance relation is no longer classified")
    if statement_by_id[RESEARCH_ID].get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("the existing Campanella-Urban research relation is no longer classified")
    required_candidates = {"cand-0198", "cand-0209", "cand-0491", "cand-3464", "cand-4572"}
    if not required_candidates.issubset(candidate_by_id):
        raise SystemExit("a required Barberini, Urban VIII, Campanella, or Paris candidate is missing")
    expected_mentions = {
        "m-chp2-secii-l147-193-0066": ("cand-0209", "Urban VIII"),
        "m-chp2-secii-l147-193-0067": ("cand-0491", "Campanella"),
        "m-chp2-secii-l147-193-0068": ("cand-0491", "Campanella"),
        "m-chp2-secii-l147-193-0069": ("cand-3464", "the Barberini"),
        "m-chp2-secii-l147-193-0070": ("cand-4572", "Paris"),
    }
    for mention_id, expected in expected_mentions.items():
        mention = mention_by_id.get(mention_id)
        if not mention or (mention["candidate_id"], mention["surface_form"]) != expected:
            raise SystemExit(f"required p.40 note mention changed or is missing: {mention_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[146:193])
    line182 = source_lines[181]
    research_quote = "which shows that Campanella helped him in his researches."
    surveillance_quote = line182[line182.index("The rather sinister"):line182.index(" must certainly")]
    inference_quote = "must certainly be connected with these activities."
    if any(quote not in line182 for quote in (research_quote, surveillance_quote, inference_quote)):
        raise SystemExit("the p.40 note sentence boundaries no longer match the protected source")
    for mention in mentions:
        if mention.get("segment_id") != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"protected notes mention span is invalid: {mention['mention_id']}")
    if len([row for row in coverage if row.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one notes-segment coverage row")

    for row in unset_rows:
        qualifiers = row.setdefault("qualifiers", {})
        if row["statement_id"] == ASTROLOGY_ID:
            note = SPECIAL_NOTES[ASTROLOGY_ID]
        elif row["statement_id"] in SPECIAL_NOTES:
            note = SPECIAL_NOTES[row["statement_id"]]
        else:
            note = GENERIC_CITATION_NOTE
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = note
        mentioned = list(qualifiers.get("mentioned_candidate_ids", []))
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if candidate_id and candidate_id not in mentioned:
                mentioned.append(candidate_id)
        qualifiers["mentioned_candidate_ids"] = mentioned
        qualifiers.pop("open_endpoint_reason", None)

    inference = statement_by_id[ASTROLOGY_ID]
    inference["original_quote"] = inference_quote
    inference["qualifiers"]["claim"] = (
        "Haskell infers that the reported surveillance of Campanella in Paris was connected with Urban VIII's astrological activities."
    )
    inference["qualifiers"]["qualification"] = (
        "This is explicitly Haskell's inference, not a direct statement by Walker or Bazzoni. "
        "The assistance and surveillance relations are recorded separately; this connection between activities has no independent event endpoints."
    )
    inference["qualifiers"]["ocr_note"] = (
        "Printed p.40 (PDF page 21) reads 'in Paris' and 'pp. 205 ff.'; S0 OCR reads 'hi Paris' and 'if.'. S0 remains unchanged."
    )
    inference["qualifiers"]["linked_statement_ids"] = append_unique(
        inference["qualifiers"].get("linked_statement_ids", []), RESEARCH_ID
    )
    inference["qualifiers"]["linked_statement_ids"] = append_unique(
        inference["qualifiers"]["linked_statement_ids"], SURVEILLANCE_ID
    )

    research = statement_by_id[RESEARCH_ID]
    research["original_quote"] = research_quote
    research["qualifiers"]["ocr_note"] = (
        "Printed p.40 (PDF page 21) confirms pp. 205 ff.; S0 OCR reads 'if.'. S0 remains unchanged."
    )
    research["qualifiers"]["linked_statement_ids"] = append_unique(
        research["qualifiers"].get("linked_statement_ids", []), "st-chp2-secii-l147-193-cite-walker-p205ff"
    )
    research["qualifiers"]["linked_note_statement_ids"] = append_unique(
        research["qualifiers"].get("linked_note_statement_ids", []), "st-chp2-secii-l147-193-cite-walker-p205ff"
    )

    surveillance = statement_by_id[SURVEILLANCE_ID]
    surveillance["original_quote"] = surveillance_quote
    surveillance["qualifiers"]["ocr_note"] = (
        "Printed p.40 (PDF page 21) reads 'in Paris'; S0 OCR reads 'hi Paris'. The named family, Campanella, and Paris mentions are reused. S0 remains unchanged."
    )
    for citation_id in ("st-chp2-secii-l147-193-cite-bazzoni-surveillance", "st-chp2-secii-l147-193-cite-bertolotti1878"):
        surveillance["qualifiers"]["linked_statement_ids"] = append_unique(
            surveillance["qualifiers"].get("linked_statement_ids", []), citation_id
        )
        surveillance["qualifiers"]["linked_note_statement_ids"] = append_unique(
            surveillance["qualifiers"].get("linked_note_statement_ids", []), citation_id
        )
    for citation_id, statement_ids in {
        "st-chp2-secii-l147-193-cite-walker-p205ff": [RESEARCH_ID, ASTROLOGY_ID],
        "st-chp2-secii-l147-193-cite-bazzoni-surveillance": [SURVEILLANCE_ID, ASTROLOGY_ID],
        "st-chp2-secii-l147-193-cite-bertolotti1878": [SURVEILLANCE_ID, ASTROLOGY_ID],
    }.items():
        citation = statement_by_id[citation_id]
        for statement_id in statement_ids:
            citation["qualifiers"]["linked_statement_ids"] = append_unique(
                citation["qualifiers"].get("linked_statement_ids", []), statement_id
            )

    if any(
        row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
        for row in statements
    ):
        raise SystemExit("notes segment still has unset relation_candidate values")
    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " S2 follow-up classifies all 60 bibliographic citations and seven other unset footnote/navigation/interpretation rows; "
        "citation locators, cross-references, Haskell's Ginnasi critique, the epigram origin pointer, and Passeri version caveat remain "
        "non-relational. The already-recorded Campanella-to-Urban research-assistance and Barberini-family surveillance relations remain "
        "separate and true; Haskell's inferred connection between the activities is retained as a non-relational, attributed interpretation. "
        "Their statement quotes are narrowed to exact clauses and the Walker/Bazzoni/Bertolotti citation links are aligned. Printed p.40 "
        "(PDF page 21) confirms 'pp. 205 ff.' and 'in Paris'; S0 remains unchanged."
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    print(json.dumps({
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "classified_unset_count": len(unset_ids),
        "bibliographic_locators_classified_nonrelational": len(citation_ids),
        "special_rows_classified_nonrelational": sorted(UNSET_SPECIAL),
        "research_and_surveillance_relations": "retained as separate existing true candidates",
        "inferred_association": "retained as a source-attributed claim, non-relational",
        "new_statements": 0,
        "new_candidates": 0,
        "new_mentions": 0,
        "existing_p40_mention_spans": len([m for m in mentions if m.get("segment_id") == SEGMENT_ID]),
        "remaining_unset_in_segment": [],
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any(written_by_id[row_id]["qualifiers"].get("relation_candidate") is not False for row_id in unset_ids):
            raise SystemExit("a footnote classification was not persisted")
        if any(written_by_id[row_id]["qualifiers"].get("relation_candidate") is not True for row_id in (SURVEILLANCE_ID, RESEARCH_ID)):
            raise SystemExit("an existing explicit relation was changed during write")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
        "statement_count": len(written),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
