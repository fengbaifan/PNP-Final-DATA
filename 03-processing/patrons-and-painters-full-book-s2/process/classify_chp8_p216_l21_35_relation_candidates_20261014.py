"""Classify p.216 S2 relation statements and repair two mention mappings."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p216_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l21-35"
SEGMENT_SHA = "4f5d502c755d5a791200895b453b3a196db68632297a0864a37c4995a91c1039"
BACKUP_SUFFIX = ".bak-s2-chp8-p216-l21-35-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "5effd453dc8611b6568c7e938c48ff3f8a6082250fcf23f3c3c15e247b5a2703",
    CANDIDATES: "d8ede03c3fd08cd9fc3ee1516f91906a72ea0ed4e95ae112e85477362f3e3258",
    MENTIONS: "6801ec1660540dd45f045a7b243fc4fc1d012c2eb0b134cf14a99578641a1415",
    COVERAGE: "dbaf87441a346d2456540e01f3b43160e6b8a0adf5c2eba8e04a6217f30e7ec8",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "a9870da64e24685c4803c81ec2806fafdff11d4386a89542425be7f672dfbea9",
}

FALSE_NOTES = {
    "st-chp8-p216-negotiations-outcome":
        "This is Haskell's evaluative summary of the cross-page negotiations and their historical interest, not a discrete relation between identified entities.",
    "st-chp8-p216-storer-selection-and-background":
        "This combines the committee's choice, Storer's training, his regional descriptor, and unnamed Bergamo family contacts. Keep the source statement and use the separate atomic claims below.",
    "st-chp8-p216-storer-delay-and-assessment-visit":
        "This combines the delay and fresco alternative with a later assessment visit to an unnamed aristocrat's house. The distinct claims are recorded below without inventing the unnamed people or works.",
    "st-chp8-p216-massimo-response-and-no-further-work":
        "This combines the governors' reception, Haskell's comparison with Veronese, and an unsuccessful request for Massimo's leave. Preserve the source statement and record each relation separately below.",
    "st-chp8-p216-milan-pictures-first-stage-complete":
        "This combines four commissions with a 1659 milestone. Preserve the source wording and record each painting and the stage completion in separate statements below.",
}

TRUE_NOTES = {
    "st-chp8-p216-storer-the-levites-commission":
        "This is the specific artist-to-work commission for The Levites. Keep the thirteen-picture scheme, southern-transept location, February 1654 date, and reported eventual production as qualifiers; Storer maps to the person entry cand-2512.",
    "st-chp8-p216-magni-experimental-commission":
        "The committee commissioned one experimental picture from Magni in 1656, with a larger commission conditional on its reception. Haskell says the trial evidently did not satisfy the committee and does not name an evaluator.",
    "st-chp8-p216-cocchi-five-pictures":
        "The committee accepted Cocchi's offer for one picture in January 1657 and later requested four more. The five-picture group remains unidentified by title; the source's general assessment of minor artists is not a status assigned by this project.",
    "st-chp8-p216-guercino-proposed-door-canvas":
        "This is one unsuccessful attempt for a projected door canvas: the committee selected Guercino and sent a messenger to Bologna, revised the proposed subject, and Haskell says the overloaded artist seems not to have been interested. The work is not treated as executed.",
    "st-chp8-p216-padre-massimo-massacre-commission":
        "The committee commissioned the specific Massacre of the Innocents from Padre Massimo after the Guercino approach failed. The career descriptors are also captured in separate source-anchored statements below.",
    "st-chp8-p216-next-north-transept-phase-open":
        "This records the committee's move to the northern transept vault. The sentence is incomplete at 'thirteen' and continues at p.217 L70; retain that cross-page boundary.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[str], list[dict]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    return lines, [json.loads(line) for line in lines if line.strip()]


def csv_read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(fields: list[str], rows: list[dict[str, str]], had_bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = output.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if had_bom else data


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False, suffix=".tmp") as stream:
        stream.write(data)
        temporary = Path(stream.name)
    temporary.replace(path)


def make_statement(row: dict) -> dict:
    qualifiers = {
        "source_line_start": row["line_start"],
        "source_line_end": row["line_end"],
        "printed_page": 216,
        "pdf_physical_page": 14,
        "claim": row["claim"],
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": row["qualification"],
        "mentioned_candidate_ids": row["mentioned"],
        "relation_candidate": True,
        "relation_candidate_note": row["note"],
    }
    if row.get("linked_statement_ids"):
        qualifiers["linked_statement_ids"] = row["linked_statement_ids"]
    return {
        "statement_id": row["statement_id"],
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": row.get("subject"),
        "object_candidate_id": row.get("object"),
        "predicate": row["predicate"],
        "qualifiers": qualifiers,
        "original_quote": row["quote"],
        "origin": "book",
        "source_file": SOURCE_REL,
    }


NEW_ROWS = [
    {
        "statement_id": "st-chp8-p216-storer-first-choice",
        "subject": "cand-7641", "object": "cand-2512", "predicate": "committee_first_choice_of_storer",
        "line_start": 23, "line_end": 23,
        "claim": "Haskell says the committee's first choice for the commission was Cristoforo Storer.",
        "quote": "Their first choice fell on a Swiss artist, Cristoforo Storer",
        "qualification": "The following clauses describe Storer's training and contacts and are represented separately.",
        "mentioned": ["cand-7641", "cand-2512"],
        "linked_statement_ids": ["st-chp8-p215-committee-orders-oil-paintings"],
        "note": "The source identifies Storer as the committee's first choice; this does not mean the later work was completed at this point.",
    },
    {
        "statement_id": "st-chp8-p216-storer-pupil-proccaccini",
        "subject": "cand-2512", "object": "cand-2064", "predicate": "pupil_of",
        "line_start": 23, "line_end": 24,
        "claim": "Haskell describes Cristoforo Storer as a pupil of Ercole Proccaccini of Milan.",
        "quote": "Cristoforo Storer, a pupil of the Milanese\nErcole Proccaccini",
        "qualification": "Retain the printed surname form Proccaccini in the evidence and map it to the existing Procaccini candidate; Milanese is a regional descriptor.",
        "mentioned": ["cand-2512", "cand-2064", "cand-3418"],
        "note": "The statement records the source's teacher-pupil claim and does not use the index spelling to alter the quotation.",
    },
    {
        "statement_id": "st-chp8-p216-storer-close-contacts-bergamo-families",
        "subject": "cand-2512", "object": None, "predicate": "close_contacts_with_unnamed_leading_bergamo_families",
        "line_start": 24, "line_end": 24,
        "claim": "Haskell says Storer had already had close contacts with leading families in Bergamo.",
        "quote": "who had already had close contacts with leading families in Bergamo",
        "qualification": "The families are not named; Bergamo is a geographic qualifier, not the relationship endpoint.",
        "mentioned": ["cand-2512", "cand-6208"],
        "note": "The source asserts a relation to an unnamed family group; leave the second endpoint unresolved rather than assigning the city as the object.",
    },
    {
        "statement_id": "st-chp8-p216-storer-described-as-swiss",
        "subject": "cand-2512", "object": "cand-12057", "predicate": "described_as_swiss",
        "line_start": 23, "line_end": 23,
        "claim": "Haskell describes Cristoforo Storer as a Swiss artist.",
        "quote": "Swiss artist",
        "qualification": "The adjective is linked to Switzerland as a source-defined geographic descriptor; it does not independently establish birthplace, residence, or citizenship.",
        "mentioned": ["cand-2512", "cand-12057"],
        "note": "This preserves the explicit regional descriptor without upgrading it to a verified biographical fact.",
    },
    {
        "statement_id": "st-chp8-p216-storer-delay-led-fresco-alternative",
        "subject": "cand-2512", "object": "cand-7641", "predicate": "storer_delay_led_committee_to_consider_fresco_alternative",
        "line_start": 25, "line_end": 25,
        "claim": "Haskell says Storer's delay led the committee, by April 1655, to consider a quicker fresco alternative for the vault.",
        "quote": "the artist’s dilatoriness caused the first of the many long delays which the committee had to suffer, so that by April 1655 they were considering changing their original scheme and having the vault frescoed as a quicker alternative",
        "qualification": "The prior sentence locates the thirteen-picture scheme in the southern transept; the alternative remained under consideration and is not a completed fresco commission.",
        "mentioned": ["cand-2512", "cand-7641", "cand-7643", "cand-7627"],
        "note": "The source connects Storer's delay with the committee's consideration of an alternative; no change of plan is asserted as completed.",
    },
    {
        "statement_id": "st-chp8-p216-committee-assessment-visit",
        "subject": "cand-7641", "object": "cand-7627", "predicate": "assessed_unnamed_fresco_artist_for_church",
        "line_start": 25, "line_end": 25,
        "claim": "A few months later, two committee members visited an unnamed local aristocrat's country house to assess whether an unnamed artist's frescoes made that artist suitable for the church.",
        "quote": "Indeed a few months later they sent two of their members to die country house of a local aristocrat to look at some frescoes he had had painted there and to decide whether or not the artist concerned would prove suitable for the church",
        "qualification": "The visit was an assessment, not a commission. The two members, aristocrat, artist, and country house are not identified.",
        "mentioned": ["cand-7641", "cand-7627"],
        "note": "The source gives a committee-to-church assessment context but leaves the visit participants and the artist unnamed.",
    },
    {
        "statement_id": "st-chp8-p216-magni-working-for-marquis-mantua",
        "subject": "cand-1493", "object": "cand-1525", "predicate": "working_for_marquis_of_mantua_in_1656",
        "line_start": 25, "line_end": 25,
        "claim": "Haskell says Pietro Magni was then working for the Marquis of Mantua.",
        "quote": "Pietro Magni, who was then working for the Marquis of Mantua",
        "qualification": "This is the context Haskell gives for Magni's 1656 experimental commission; no particular job or terms are specified.",
        "mentioned": ["cand-1493", "cand-1525"],
        "linked_statement_ids": ["st-chp8-p216-magni-experimental-commission"],
        "note": "The statement isolates Magni's reported work for the Marquis from the separate commission for the church.",
    },
    {
        "statement_id": "st-chp8-p216-massimo-capuchin-member",
        "subject": "cand-1576", "object": "cand-3405", "predicate": "described_as_capuchin_member",
        "line_start": 30, "line_end": 30,
        "claim": "Haskell describes Padre Massimo as a Capuchin.",
        "quote": "a Capuchin",
        "qualification": "The source uses the order adjective as a description of Padre Massimo.",
        "mentioned": ["cand-1576", "cand-3405"],
        "note": "The source identifies Massimo with the Capuchin order; it does not name a monastery or office.",
    },
    {
        "statement_id": "st-chp8-p216-massimo-pupil-of-brusasorci",
        "subject": "cand-1576", "object": "cand-0460", "predicate": "pupil_of",
        "line_start": 30, "line_end": 31,
        "claim": "Haskell describes Padre Massimo as a pupil of Brusasorci.",
        "quote": "a Capuchin pupil of the\nVeronese Brusasorci, Padre Massimo",
        "qualification": "The source's teacher-pupil description is retained as attributed; it does not establish a date or place of training.",
        "mentioned": ["cand-1576", "cand-0460"],
        "note": "The source explicitly identifies Brusasorci as Massimo's teacher.",
    },
    {
        "statement_id": "st-chp8-p216-brusasorci-described-as-veronese",
        "subject": "cand-0460", "object": "cand-7661", "predicate": "described_as_veronese",
        "line_start": 31, "line_end": 31,
        "claim": "Haskell describes Brusasorci as Veronese.",
        "quote": "Veronese Brusasorci",
        "qualification": "This records the regional adjective only; it does not infer birthplace or residence.",
        "mentioned": ["cand-0460", "cand-7661"],
        "note": "Keep the source's regional descriptor distinct from a verified biographical origin claim.",
    },
    {
        "statement_id": "st-chp8-p216-massimo-prior-altar-paintings-veneto",
        "subject": "cand-1576", "object": "cand-4207", "predicate": "previously_painted_altar_pictures_in_veneto",
        "line_start": 31, "line_end": 31,
        "claim": "Haskell says Padre Massimo had already painted a number of altar pictures in the Veneto.",
        "quote": "a man who had already painted a number of altar pictures in the Veneto",
        "qualification": "The paintings are not named or counted individually.",
        "mentioned": ["cand-1576", "cand-4207"],
        "note": "The source gives a prior-work regional context but no titles, dates, or specific locations.",
    },
    {
        "statement_id": "st-chp8-p216-governors-pleased-with-massacre",
        "subject": None, "object": "cand-7653", "predicate": "source_says_governors_pleased_with_work",
        "line_start": 31, "line_end": 31,
        "claim": "Haskell says the relevant governors and city were pleased with the Massacre of the Innocents.",
        "quote": "So pleased were they with the work",
        "qualification": "The antecedent 'they' follows the reference to the Consorzio and the whole city; keep the precise actor boundary open.",
        "mentioned": ["cand-7640", "cand-7653"],
        "note": "The reception claim is explicit, but the pronoun does not isolate one institutional actor from the broader group.",
        "linked_statement_ids": ["st-chp8-p216-padre-massimo-massacre-commission"],
    },
    {
        "statement_id": "st-chp8-p216-massacre-rehash-of-paolo-veronese",
        "subject": "cand-7653", "object": "cand-2755", "predicate": "described_as_rehash_of_paolo_veronese",
        "line_start": 31, "line_end": 31,
        "claim": "Haskell characterizes the Massacre as a vigorous and efficient reworking of Paolo Veronese.",
        "quote": "a vigorous and efficient rehash of Paolo Veronese",
        "qualification": "This is Haskell's stylistic assessment; it is not an authorship claim.",
        "mentioned": ["cand-7653", "cand-2755"],
        "note": "The source compares the painting with Veronese's work but does not attribute its execution to Veronese.",
        "linked_statement_ids": ["st-chp8-p216-padre-massimo-massacre-commission"],
    },
    {
        "statement_id": "st-chp8-p216-governors-request-massimo-leave",
        "subject": "cand-7640", "object": "cand-3405", "predicate": "requested_temporary_leave_for_massimo",
        "line_start": 31, "line_end": 33,
        "claim": "Haskell says the governors implored the Capuchins to grant Padre Massimo temporary leave to settle in Bergamo for further painting; the request came to nothing.",
        "quote": "with the promise-of lavish alms, they implored the\nCapuchins to give temporary leave to Padre Massimo and allow him to settle in\nBergamo to paint further pictures. But this too came to nothing.",
        "qualification": "The request is not a completed leave, relocation, or further commission. The printed hyphen in 'promise-of' is retained.",
        "mentioned": ["cand-7640", "cand-3405", "cand-1576", "cand-6208"],
        "note": "The source explicitly describes an unsuccessful request to the order concerning Massimo's temporary leave.",
        "linked_statement_ids": ["st-chp8-p216-padre-massimo-massacre-commission"],
    },
    {
        "statement_id": "st-chp8-p216-milan-artists-commissioned-killing-of-sisera",
        "subject": None, "object": "cand-7649", "predicate": "commissioned_from_unnamed_milan_area_artist",
        "line_start": 33, "line_end": 33,
        "claim": "Haskell says an unnamed artist from Milan or its surroundings was commissioned to paint The Killing of Sisera.",
        "quote": "Instead, other artists from Milan and its surroundings were commissioned to paint The Killing of Sisera, The\nSacrifice of Isaac, facob’s Ladder and the Murder of Cain.",
        "qualification": "The painter is unnamed; do not assign the work to a particular person.",
        "mentioned": ["cand-3418", "cand-7649"],
        "note": "This isolates one named work from the four-work commission group without inventing its painter.",
    },
    {
        "statement_id": "st-chp8-p216-milan-artists-commissioned-sacrifice-of-isaac",
        "subject": None, "object": "cand-7650", "predicate": "commissioned_from_unnamed_milan_area_artist",
        "line_start": 33, "line_end": 34,
        "claim": "Haskell says an unnamed artist from Milan or its surroundings was commissioned to paint The Sacrifice of Isaac.",
        "quote": "Instead, other artists from Milan and its surroundings were commissioned to paint The Killing of Sisera, The\nSacrifice of Isaac, facob’s Ladder and the Murder of Cain.",
        "qualification": "The painter is unnamed; do not assign the work to a particular person.",
        "mentioned": ["cand-3418", "cand-7650"],
        "note": "This isolates one named work from the four-work commission group without inventing its painter.",
    },
    {
        "statement_id": "st-chp8-p216-milan-artists-commissioned-jacobs-ladder",
        "subject": None, "object": "cand-7651", "predicate": "commissioned_from_unnamed_milan_area_artist",
        "line_start": 33, "line_end": 34,
        "claim": "Haskell says an unnamed artist from Milan or its surroundings was commissioned to paint Jacob's Ladder.",
        "quote": "Instead, other artists from Milan and its surroundings were commissioned to paint The Killing of Sisera, The\nSacrifice of Isaac, facob’s Ladder and the Murder of Cain.",
        "qualification": "The painter is unnamed. The original quote preserves S0's OCR spelling; the S2 correction is recorded on the source statement.",
        "mentioned": ["cand-3418", "cand-7651"],
        "note": "This isolates one named work from the four-work commission group without inventing its painter.",
    },
    {
        "statement_id": "st-chp8-p216-milan-artists-commissioned-murder-of-cain",
        "subject": None, "object": "cand-7652", "predicate": "commissioned_from_unnamed_milan_area_artist",
        "line_start": 33, "line_end": 34,
        "claim": "Haskell says an unnamed artist from Milan or its surroundings was commissioned to paint The Murder of Cain.",
        "quote": "Instead, other artists from Milan and its surroundings were commissioned to paint The Killing of Sisera, The\nSacrifice of Isaac, facob’s Ladder and the Murder of Cain.",
        "qualification": "The painter is unnamed; do not assign the work to a particular person.",
        "mentioned": ["cand-3418", "cand-7652"],
        "note": "This isolates one named work from the four-work commission group without inventing its painter.",
    },
    {
        "statement_id": "st-chp8-p216-first-decoration-stage-complete-1659",
        "subject": "cand-7639", "object": None, "predicate": "first_decoration_stage_complete_by_1659",
        "line_start": 34, "line_end": 34,
        "claim": "Haskell says the first stage of the decoration was complete by 1659.",
        "quote": "By 1659 the first stage in the decoration was complete.",
        "qualification": "The passage does not identify which artists or committee members completed this stage.",
        "mentioned": ["cand-7639"],
        "linked_statement_ids": [
            "st-chp8-p216-milan-artists-commissioned-killing-of-sisera",
            "st-chp8-p216-milan-artists-commissioned-sacrifice-of-isaac",
            "st-chp8-p216-milan-artists-commissioned-jacobs-ladder",
            "st-chp8-p216-milan-artists-commissioned-murder-of-cain",
        ],
        "note": "This records the dated milestone for the existing decoration programme; no completing agent is inferred.",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write only after guarded preflight succeeds")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a reviewed table, source, PDF, or page image changed; re-review before applying")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[20:35])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("the p.216 S2 source segment changed since review")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl")[1]
                    if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 21, 35, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("the p.216 S0 manifest does not match the reviewed source")

    statement_lines, statements = read_jsonl(STATEMENTS)
    original_statement_count = len(statements)
    by_statement = {row["statement_id"]: row for row in statements}
    if len(by_statement) != len(statements):
        raise SystemExit("statement identifiers are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {row["statement_id"] for row in page_rows
             if "relation_candidate" not in (row.get("qualifiers") or {})}
    expected_unset = set(FALSE_NOTES) | set(TRUE_NOTES)
    if len(page_rows) != 11 or unset != expected_unset:
        raise SystemExit(f"unexpected p.216 inventory: rows={len(page_rows)}, unset={len(unset)}")

    candidate_fields, candidates = csv_read(CANDIDATES)
    by_candidate = {row["candidate_id"]: row for row in candidates}
    if len(by_candidate) != len(candidates):
        raise SystemExit("candidate identifiers are not unique")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12056:
        raise SystemExit("candidate sequence changed since review")
    if (by_candidate.get("cand-2512", {}).get("suggested_type") != "person"
            or by_candidate.get("cand-2513", {}).get("suggested_type") != "work"
            or by_candidate.get("cand-2513", {}).get("sub_entry") != "The Levites"
            or by_candidate.get("cand-0381", {}).get("canonical_name") != "Bologna"
            or by_candidate.get("cand-1131", {}).get("canonical_name") != "Genoa"):
        raise SystemExit("the reviewed Storer/Bologna candidate mappings changed")
    by_candidate["cand-2513"]["detail"] = (
        "The The Levites work sub-entry under the Cristoforo Storer index heading; this candidate denotes the work, "
        "not Storer the painter. Keep it available for later S4 alignment with the separate p.216 body candidate."
    )
    if "cand-12057" in by_candidate:
        raise SystemExit("planned Switzerland candidate ID already exists")

    mention_fields, mentions = csv_read(MENTIONS)
    by_mention = {row["mention_id"]: row for row in mentions}
    if len(by_mention) != len(mentions):
        raise SystemExit("mention identifiers are not unique")
    if (by_mention.get("m-chp8-s2-p215-216-032", {}).get("candidate_id") != "cand-2513"
            or by_mention.get("m-chp8-s2-p215-216-048", {}).get("candidate_id") != "cand-1131"):
        raise SystemExit("the reviewed Storer/Bologna mention mappings changed")
    swiss_start = segment_text.find("Swiss")
    if swiss_start != 228 or segment_text[swiss_start:swiss_start + 5] != "Swiss":
        raise SystemExit("the reviewed Swiss source span moved")

    coverage_fields, coverage_rows = csv_read(COVERAGE)
    coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
    coverage = coverage_by_id.get(SEGMENT_ID)
    expected_old_note = (
        "The p.216 sentence ending at 'thirteen' is closed by p.217 L70; see the linked continuation statement. "
        "The remainder of the p.216 passage and its existing mentions/statements are unchanged."
    )
    if (not coverage or coverage.get("disposition") != "reviewed"
            or coverage.get("migration_status") != "complete"
            or coverage.get("source_line_ranges") != "L22-35"
            or coverage.get("note") != expected_old_note):
        raise SystemExit("p.216 source coverage changed since review")

    new_ids = {row["statement_id"] for row in NEW_ROWS}
    if len(new_ids) != len(NEW_ROWS) or new_ids & set(by_statement):
        raise SystemExit("a planned p.216 statement ID already exists")
    all_statement_ids = set(by_statement) | new_ids
    for row in NEW_ROWS:
        for linked_id in row.get("linked_statement_ids", []):
            if linked_id not in all_statement_ids:
                raise SystemExit(f"unknown linked statement in {row['statement_id']}: {linked_id}")
    if "st-chp8-p215-negotiations-follow-relative-failure" not in by_statement:
        raise SystemExit("the p.215 negotiations statement used by the cross-page link is missing")
    if {"m-chp8-s2-p215-216-076", "m-chp8-s2-p215-216-077"} & set(by_mention):
        raise SystemExit("planned Switzerland mention ID already exists")
    new_candidate_ids = {"cand-12057"}
    for row in NEW_ROWS:
        if row["quote"] not in segment_text:
            raise SystemExit(f"new quote is not an exact p.216 S0 span: {row['statement_id']}")
        for endpoint in (row.get("subject"), row.get("object")):
            if endpoint and endpoint not in (set(by_candidate) | {"cand-12057"}):
                raise SystemExit(f"unknown endpoint in {row['statement_id']}: {endpoint}")
        for candidate_id in row["mentioned"]:
            if candidate_id not in (set(by_candidate) | new_candidate_ids):
                raise SystemExit(f"unknown mention candidate in {row['statement_id']}: {candidate_id}")

    # Correct the two candidate links without altering the source forms.
    for mention_id, candidate_id in (
        ("m-chp8-s2-p215-216-032", "cand-2512"),
        ("m-chp8-s2-p215-216-048", "cand-0381"),
    ):
        by_mention[mention_id]["candidate_id"] = candidate_id
    by_mention["m-chp8-s2-p215-216-032"]["note"] = "Swiss painter selected first by the committee; person candidate is Storer, Cristoforo."
    by_mention["m-chp8-s2-p215-216-048"]["note"] = "City to which the messenger was sent for Guercino."
    mentions.append({
        "mention_id": "m-chp8-s2-p215-216-076", "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12057", "surface_form": "Swiss",
        "start_char": str(swiss_start), "end_char": str(swiss_start + 5),
        "note": "Regional descriptor for Cristoforo Storer; do not infer birthplace or citizenship.",
    })
    decoration_start = segment_text.index("the decoration was complete")
    mentions.append({
        "mention_id": "m-chp8-s2-p215-216-077", "segment_id": SEGMENT_ID,
        "candidate_id": "cand-7639", "surface_form": "the decoration",
        "start_char": str(decoration_start), "end_char": str(decoration_start + len("the decoration")),
        "note": "The decoration programme whose first stage was complete by 1659; no completing agent is identified.",
    })

    candidates.append({
        "candidate_id": "cand-12057", "index_entry_id": "", "canonical_name": "Switzerland",
        "index_page_range": "", "suggested_type": "place", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Geographic referent of the source adjective Swiss applied to Cristoforo Storer on p.216; this does not establish birthplace or citizenship.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L23",
    })

    changed_statement_ids: set[str] = set()
    for statement_id, note in FALSE_NOTES.items():
        row = by_statement[statement_id]
        qualifiers = dict(row.get("qualifiers") or {})
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = note
        mentioned = list(qualifiers.get("mentioned_candidate_ids") or [])
        qualifiers["mentioned_candidate_ids"] = [
            "cand-2512" if value == "cand-2513" else value for value in mentioned
        ]
        if statement_id == "st-chp8-p216-storer-selection-and-background" and "cand-12057" not in qualifiers["mentioned_candidate_ids"]:
            qualifiers["mentioned_candidate_ids"].append("cand-12057")
        row["qualifiers"] = qualifiers
        row["subject_candidate_id"] = None
        row["object_candidate_id"] = None
        changed_statement_ids.add(statement_id)

    for statement_id, note in TRUE_NOTES.items():
        row = by_statement[statement_id]
        qualifiers = dict(row.get("qualifiers") or {})
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        mentioned = list(qualifiers.get("mentioned_candidate_ids") or [])
        mentioned = ["cand-2512" if value == "cand-2513" else value for value in mentioned]
        mentioned = ["cand-0381" if value == "cand-1131" else value for value in mentioned]
        if statement_id == "st-chp8-p216-storer-the-levites-commission":
            row["subject_candidate_id"] = "cand-2512"
            qualifiers["mentioned_candidate_ids"] = mentioned
        elif statement_id == "st-chp8-p216-cocchi-five-pictures":
            row["subject_candidate_id"] = "cand-7641"
            row["object_candidate_id"] = "cand-7647"
            row["predicate"] = "committee_accepted_cocchi_offer_and_requested_four_more"
            qualifiers["mentioned_candidate_ids"] = mentioned
        elif statement_id == "st-chp8-p216-guercino-proposed-door-canvas":
            qualifiers["mentioned_candidate_ids"] = mentioned
        elif statement_id == "st-chp8-p216-next-north-transept-phase-open":
            row["subject_candidate_id"] = "cand-7641"
            row["object_candidate_id"] = "cand-7644"
            row["predicate"] = "committee_turned_to_north_transept_vault"
        row["qualifiers"] = qualifiers
        changed_statement_ids.add(statement_id)

    # The negotiations sentence continues across the page boundary from p.215 L19.
    negotiation = by_statement["st-chp8-p216-negotiations-outcome"]
    negotiation["qualifiers"]["linked_statement_ids"] = ["st-chp8-p215-negotiations-follow-relative-failure"]
    changed_statement_ids.add("st-chp8-p216-negotiations-outcome")

    # Preserve the exact S0 quotes; record the page-image correction already present for Jacob's Ladder.
    ocr_checks = {
        "st-chp8-p216-storer-delay-and-assessment-visit": (25, "die country house", "the country house"),
        "st-chp8-p216-guercino-proposed-door-canvas": (27, "cominittee", "committee"),
        "st-chp8-p216-padre-massimo-massacre-commission": (30, "t\u00f3 the", "to the"),
        "st-chp8-p216-milan-pictures-first-stage-complete": (34, "facob\u2019s Ladder", "Jacob\u2019s Ladder"),
    }
    for statement_id, (line, bad, good) in ocr_checks.items():
        corrections = by_statement[statement_id].get("qualifiers", {}).get("ocr_corrections", [])
        if not any(c.get("source_line") == line and c.get("ocr") == bad and c.get("print") == good for c in corrections):
            raise SystemExit(f"expected page-image OCR correction is missing: {statement_id}")

    # The print itself contains the hyphen in promise-of; don't report it as an OCR repair.
    coverage["note"] = (
        "L21 is the printed-page marker; prose L22-35 was reviewed against CHP-8.pdf physical p.14. "
        "L22 completes the negotiations clause begun at p.215 L19; L35 ends at 'thirteen' and continues at p.217 L70. "
        "Four compound statements were kept as non-relational source records with atomic claims added for their separable relations. "
        "Storer and Bologna mentions now map to the person/place candidates. Page-image OCR corrections: "
        "die/the (L25), cominittee/committee (L27), tó/to (L30), and facob/Jacob (L34). "
        "The printed hyphen in promise-of (L31) is preserved; S0 remains unchanged."
    )

    for row in NEW_ROWS:
        statement = make_statement(row)
        statements.append(statement)
        by_statement[statement["statement_id"]] = statement
        changed_statement_ids.add(statement["statement_id"])

    # Link newly split statements to their source bundles where that aids interpretation.
    expected_original_count = 11
    final_page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    counts = {True: 0, False: 0, None: 0}
    for row in final_page_rows:
        value = (row.get("qualifiers") or {}).get("relation_candidate")
        counts[value] = counts.get(value, 0) + 1
    if len(final_page_rows) != expected_original_count + len(NEW_ROWS) or counts != {True: 25, False: 5, None: 0}:
        raise SystemExit(f"unexpected final p.216 relation counts: rows={len(final_page_rows)}, counts={counts}")

    for row in final_page_rows:
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in by_candidate and candidate_id != "cand-12057":
                raise SystemExit(f"unknown candidate mention after update: {row['statement_id']} {candidate_id}")
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in by_candidate and endpoint != "cand-12057":
                raise SystemExit(f"unknown endpoint after update: {row['statement_id']} {endpoint}")

    # Preserve untouched JSONL source lines byte-for-byte; serialize only changed rows and additions.
    statement_output = []
    original_rows = statements[:original_statement_count]
    if len(original_rows) != len(statement_lines):
        raise SystemExit("statement source inventory changed during preparation")
    for raw_line, row in zip(statement_lines, original_rows, strict=True):
        statement_output.append(
            json.dumps(row, ensure_ascii=False) if row["statement_id"] in changed_statement_ids else raw_line
        )
    statement_output.extend(
        json.dumps(row, ensure_ascii=False) for row in statements[original_statement_count:]
    )
    serialized_rows = [json.loads(line) for line in statement_output]
    serialized_page = [row for row in serialized_rows if row.get("segment_id") == SEGMENT_ID]
    serialized_counts = {True: 0, False: 0, None: 0}
    for row in serialized_page:
        value = (row.get("qualifiers") or {}).get("relation_candidate")
        serialized_counts[value] = serialized_counts.get(value, 0) + 1
    if len(serialized_page) != expected_original_count + len(NEW_ROWS) or serialized_counts != {True: 25, False: 5, None: 0}:
        raise SystemExit(f"serialized output failed p.216 status check: rows={len(serialized_page)}, counts={serialized_counts}")
    new_statement_bytes = ("\n".join(statement_output) + "\n").encode("utf-8")

    candidates_bytes = csv_bytes(candidate_fields, candidates, raw[CANDIDATES].startswith(b"\xef\xbb\xbf"))
    mentions_bytes = csv_bytes(mention_fields, mentions, raw[MENTIONS].startswith(b"\xef\xbb\xbf"))
    updated_coverage_rows = [coverage_by_id.get(row["segment_id"], row) for row in coverage_rows]
    coverage_bytes = csv_bytes(coverage_fields, updated_coverage_rows, raw[COVERAGE].startswith(b"\xef\xbb\xbf"))

    print("DRY RUN p.216 S2 segment")
    print(f"segment={SEGMENT_ID} original_statements=11 classified=11 added_atomic_statements={len(NEW_ROWS)}")
    print(f"final statements={len(final_page_rows)} relation_candidates={counts[True]} non_relation={counts[False]} unset={counts[None]}")
    print("repairs: Storer person cand-2512; Bologna cand-0381; Switzerland candidate cand-12057; four compound bundles split")
    for path, data in (
        (STATEMENTS, new_statement_bytes), (CANDIDATES, candidates_bytes),
        (MENTIONS, mentions_bytes), (COVERAGE, coverage_bytes),
    ):
        print(f"{path.relative_to(ROOT)} before={sha(raw[path])} after={sha(data)}")
    if not args.apply:
        print("No files written. Use --apply after reviewing the summary.")
        return

    paths = [STATEMENTS, CANDIDATES, MENTIONS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        if not all(path.exists() for path in backups):
            raise SystemExit("only some recovery backups exist; inspect before applying")
        if any(backup.read_bytes() != raw[path] for path, backup in zip(paths, backups, strict=True)):
            raise SystemExit("an existing recovery backup differs from the exact prestate")
        print("Reusing byte-identical recovery copies from the guarded first apply.")
    else:
        for path, backup in zip(paths, backups, strict=True):
            shutil.copy2(path, backup)
    atomic_write(STATEMENTS, new_statement_bytes)
    atomic_write(CANDIDATES, candidates_bytes)
    atomic_write(MENTIONS, mentions_bytes)
    atomic_write(COVERAGE, coverage_bytes)
    print("APPLIED; recovery copies:")
    for backup in backups:
        print(f"  {backup.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
