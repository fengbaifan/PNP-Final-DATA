"""Review p.209 S2 statements, split conflated claims, and repair mappings."""
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
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l62-70"
BACKUP_SUFFIX = ".bak-s2-chp8-p209-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "14b5170151258cfa3cae1800d0c2e24bf63541ccf685266e66da594cef5bd890",
    CANDIDATES: "19cec2dbd76133ba4080b1cf864f9413b4f5cfe147207c24cc5a2c4eddc07571",
    MENTIONS: "eac1c1989a9c51829a0ebc0ea3b70749c76f32a04b244f730d851a92cd02a80d",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "debb8b7e6e0c50ccf2766215496ca21c7eec55f0be432b91448eb40408f7118a"

UNSET_IDS = {
    "st-chp8-p209-ruffo-agents-reported-market-and-contemporary-artists",
    "st-chp8-p209-ruffo-aimed-for-representative-collection-open",
    "st-chp8-p209-ruffo-born-messina-aristocratic-family",
    "st-chp8-p209-ruffo-collected-almost-uninterrupted-for-thirty-years",
    "st-chp8-p209-ruffo-guided-by-size-and-expense",
    "st-chp8-p209-ruffo-symmetry-and-pairs-shaped-composition",
    "st-chp8-p209-ruffo-trade-and-tax-revenue",
}
PAGE_STATEMENT_IDS = {
    "st-chp8-p209-first-picture-guided-further-orders-open",
    "st-chp8-p209-gallery-works-as-clues-to-taste",
    "st-chp8-p209-guercino-picture-required-to-match-rembrandt-aristotle",
    "st-chp8-p209-guercino-rate-and-ruffo-offer-in-scudi",
    "st-chp8-p209-ruffo-agents-reported-market-and-contemporary-artists",
    "st-chp8-p209-ruffo-aimed-for-representative-collection-open",
    "st-chp8-p209-ruffo-began-collecting-about-1646-palace-built-by-mother",
    "st-chp8-p209-ruffo-born-messina-aristocratic-family",
    "st-chp8-p209-ruffo-collected-almost-uninterrupted-for-thirty-years",
    "st-chp8-p209-ruffo-collection-over-350-at-death",
    "st-chp8-p209-ruffo-guided-by-size-and-expense",
    "st-chp8-p209-ruffo-ordered-directly-or-through-agents-with-varying-briefs",
    "st-chp8-p209-ruffo-outlawed-for-supporting-messina-privileges",
    "st-chp8-p209-ruffo-patronage-palace-cultural-centre-until-death",
    "st-chp8-p209-ruffo-personal-interest-and-limited-acquaintance",
    "st-chp8-p209-ruffo-knew-few-other-paintings",
    "st-chp8-p209-ruffo-pressed-network-into-agency",
    "st-chp8-p209-ruffo-raised-price-guercino-promised-proportionate-picture",
    "st-chp8-p209-ruffo-seems-to-set-picture-price-in-advance",
    "st-chp8-p209-ruffo-symmetry-and-pairs-shaped-composition",
    "st-chp8-p209-ruffo-trade-and-tax-revenue",
    "st-chp8-p209-ruffo-travelled-seemingly-only-within-calabria",
}
NEW_STATEMENT_IDS = {
    "st-chp8-p209-ruffo-born-into-unidentified-aristocratic-family",
    "st-chp8-p209-ruffo-moved-into-palace-before-collecting",
    "st-chp8-p209-ruffo-mother-built-palace",
    "st-chp8-p209-ruffo-income-from-tax-revenues",
    "st-chp8-p209-ruffo-limited-political-participation",
    "st-chp8-p209-ruffo-life-devoted-to-arts",
}
CANDIDATE_SPECS = [
    (
        "cand-12038",
        "Unidentified aristocratic family into which Antonio Ruffo was born",
        "family",
        "Haskell says Ruffo was born into one of the great aristocratic families but names no lineage; retain the family as unidentified.",
        63,
    ),
    (
        "cand-12039",
        "Unspecified painter contemporaries of Antonio Ruffo",
        "term",
        "Haskell says Ruffo was primarily interested in his contemporaries; no artist in this group is identified by the passage.",
        68,
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
    segment_text = "\n".join(source_lines[61:70])
    segments = read_jsonl(SEGMENTS)
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (segment["line_start"], segment["line_end"]) != (62, 70):
        raise SystemExit("p.209 segment metadata changed")
    if segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE] or segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.209 source asset or segment fingerprint changed")
    if sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.209 source segment text changed since review")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(by_id) != len(statements) or len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("statement, candidate, or mention IDs are not unique")

    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_ids = {row["statement_id"] for row in page_rows}
    actual_unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if actual_ids != PAGE_STATEMENT_IDS or actual_unset != UNSET_IDS:
        raise SystemExit(
            f"unexpected p.209 statement inventory: ids_delta={sorted(actual_ids ^ PAGE_STATEMENT_IDS)}, "
            f"unset_delta={sorted(actual_unset ^ UNSET_IDS)}"
        )
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")
    if {row[0] for row in CANDIDATE_SPECS} & set(candidate_by_id):
        raise SystemExit("a planned candidate ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12037:
        raise SystemExit("candidate sequence changed since the p.209 review")

    def require_mention(mention_id: str, candidate_id: str, surface: str) -> dict:
        row = mention_by_id.get(mention_id)
        if not row or row["candidate_id"] != candidate_id or row["surface_form"] != surface:
            raise SystemExit(f"mention {mention_id} no longer matches expected prestate")
        return row

    family_mention = require_mention(
        "m-chp8-p209-004", "cand-2297", "one of the great aristocratic families"
    )
    contemporaries_mention = require_mention("m-chp8-p209-025", "cand-2301", "his contemporaries")
    count_mention = require_mention("m-chp8-p209-010", "cand-7468", "more than 350 pictures")
    criteria_mention = require_mention("m-chp8-p209-026", "cand-2302", "size and expense")

    new_candidates = []
    for candidate_id, name, kind, detail, line in CANDIDATE_SPECS:
        new_candidates.append({
            "candidate_id": candidate_id,
            "index_entry_id": "",
            "canonical_name": name,
            "index_page_range": "",
            "suggested_type": kind,
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": detail,
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    family_mention["candidate_id"] = "cand-12038"
    family_mention["note"] = "Unidentified family into which Haskell says Ruffo was born; do not infer its name or lineage."
    contemporaries_mention["candidate_id"] = "cand-12039"
    contemporaries_mention["note"] = "Unspecified painter contemporaries; no members are named in the passage."
    mentions = [row for row in mentions if row["mention_id"] not in {count_mention["mention_id"], criteria_mention["mention_id"]}]

    def excerpt(start_line: int, end_line: int, first: str, last: str) -> str:
        source = "\n".join(source_lines[start_line - 1:end_line])
        start, end = source.find(first), source.rfind(last)
        if start < 0 or end < start:
            raise SystemExit(f"expected source phrase missing at L{start_line}-L{end_line}: {first!r} ... {last!r}")
        return source[start:end + len(last)]

    def update(
        statement_id: str,
        relation: bool,
        note: str,
        *,
        predicate: str | None = None,
        subject=UNCHANGED,
        object_id=UNCHANGED,
        claim: str | None = None,
        qualification: str | None = None,
        quote_text: str | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
        mentioned: list[str] | None = None,
        add_corrections: list[dict] | None = None,
        remove_qualifiers: list[str] | None = None,
    ) -> None:
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
        if add_corrections:
            corrections = list(q.get("ocr_corrections") or [])
            for correction in add_corrections:
                if correction not in corrections:
                    corrections.append(correction)
            q["ocr_corrections"] = corrections
        for key in remove_qualifiers or []:
            q.pop(key, None)
        if predicate is not None:
            row["predicate"] = predicate
        if subject is not UNCHANGED:
            row["subject_candidate_id"] = subject
        if object_id is not UNCHANGED:
            row["object_candidate_id"] = object_id
        if quote_text is not None:
            row["original_quote"] = quote_text
        row["qualifiers"] = q

    update(
        "st-chp8-p209-first-picture-guided-further-orders-open", True,
        "The passage describes Ruffo receiving an artist's first picture in Messina and deciding whether to seek more; the decision is conditional, not a claim that he always commissioned further work.",
    )
    update(
        "st-chp8-p209-gallery-works-as-clues-to-taste", False,
        "This is Haskell's inference from the number of works in the gallery to Ruffo's taste, not a historical relation between two independently identified entities.",
        predicate="haskell_inferred_gallery_artist_counts_as_clues_to_ruffos_taste",
        claim="Haskell says that, without Ruffo's letters and instructions, the number of works by each painter in his gallery helps provide clues to his taste.",
        qualification="This is an author's inference from collection contents; the counts are not direct statements by Ruffo.",
        mentioned=["cand-2297", "cand-7468"],
    )
    update(
        "st-chp8-p209-guercino-picture-required-to-match-rembrandt-aristotle", True,
        "Haskell reports that Guercino asked for a drawing of Rembrandt's identified Aristotle painting because Guercino's own unidentified picture was to match it.",
        add_corrections=[{"source_line": 68, "ocr": "Rembrandt��s", "print": "Rembrandt's", "basis": "CHP-8.pdf physical page 7."}],
    )
    update(
        "st-chp8-p209-guercino-rate-and-ruffo-offer-in-scudi", True,
        "Haskell reports a negotiation between Ruffo and Guercino tied to the artist's per-figure rate; currency units and quoted terms remain as printed.",
        add_corrections=[
            {"source_line": 69, "ocr": "halfa figure", "print": "half a figure", "basis": "CHP-8.pdf physical page 7."},
            {"source_line": 69, "ocr": "��", "print": "curly single quotation marks", "basis": "CHP-8.pdf physical page 7."},
        ],
    )
    update(
        "st-chp8-p209-ruffo-agents-reported-market-and-contemporary-artists", True,
        "The source says Ruffo's unnamed intermediaries informed him about artists and the market; the reporting direction runs from intermediaries to Ruffo.",
        subject="cand-7470", object_id="cand-2297",
        predicate="intermediaries_informed_ruffo_about_artists_and_market",
        claim="Haskell says Ruffo's intermediaries informed him which artists were more talented and working, and about the state of the market.",
        qualification="No informant or artist is named. Haskell says Ruffo was primarily interested in contemporary artists.",
        mentioned=["cand-7470", "cand-2297", "cand-12039"],
        add_corrections=[{"source_line": 68, "ocr": "��", "print": "em dash", "basis": "CHP-8.pdf physical page 7."}],
    )
    update(
        "st-chp8-p209-ruffo-aimed-for-representative-collection-open", True,
        "Haskell attributes to Ruffo an aim to assemble a representative collection; p.210 completes the phrase as works by all the leading contemporaries.",
        predicate="ruffo_aimed_to_assemble_representative_collection_of_leading_contemporaries",
        qualification="This is Haskell's account of Ruffo's aim, not a quotation of Ruffo's own statement. The linked p.210 continuation closes the sentence.",
        mentioned=["cand-2297", "cand-7468", "cand-2301"],
    )
    update(
        "st-chp8-p209-ruffo-born-messina-aristocratic-family", True,
        "This statement is narrowed to the reported birthplace and year; family membership is recorded separately with an unidentified family endpoint.",
        predicate="antonio_ruffo_born_in_messina_in_1610",
        claim="Haskell says Don Antonio Ruffo was born in Messina in 1610.",
        qualification="This is Haskell's report; it is not independently verified here.",
        object_id="cand-1655",
        quote_text=excerpt(63, 63, "Don Antonio Ruffo was born", "1610"),
        mentioned=["cand-2297", "cand-1655"],
    )
    update(
        "st-chp8-p209-ruffo-collected-almost-uninterrupted-for-thirty-years", True,
        "The duration describes Ruffo's continuing collecting activity and is linked to his unidentified collection.",
        subject="cand-2297", object_id="cand-7468",
        claim="Haskell says Ruffo continued collecting almost without interruption for the next thirty years.",
        qualification="The duration is relative to the approximate start date; do not calculate a precise end year.",
        mentioned=["cand-2297", "cand-7468"],
    )
    update(
        "st-chp8-p209-ruffo-collection-over-350-at-death", True,
        "The sentence's subject is Ruffo's palace, which Haskell says contained the picture collection at his death; endpoints are corrected to palace and collection.",
        subject="cand-7467", object_id="cand-7468",
        predicate="ruffo_palace_contained_over_350_pictures_at_his_death",
        claim="Haskell says the palace contained more than 350 pictures at Ruffo's death, painted by artists across Italy and elsewhere.",
        mentioned=["cand-7467", "cand-7468", "cand-3461"],
    )
    update(
        "st-chp8-p209-ruffo-guided-by-size-and-expense", False,
        "Size and expense are generic considerations in Haskell's description, not a separately identified entity; the index subentry for Ruffo must not be used as an endpoint.",
        predicate="haskell_described_size_and_expense_as_ruffos_considerations",
        subject="cand-2297", object_id=None,
        mentioned=["cand-2297"],
    )
    update(
        "st-chp8-p209-ruffo-outlawed-for-supporting-messina-privileges", True,
        "This statement is narrowed to the reported 1661 outlawing and its stated cause; Ruffo's limited political activity is recorded separately.",
        predicate="ruffo_temporarily_outlawed_in_1661_for_supporting_messina_privileges",
        claim="Haskell says Ruffo was outlawed for a short time in 1661 for supporting Messina's privileges against the Viceroy's authority.",
        qualification="The source does not name the Viceroy or specify the legal process; this remains Haskell's report.",
        quote_text=excerpt(65, 65, "in 1661 he was outlawed", "Viceroy."),
        start_line=65, end_line=65,
        mentioned=["cand-2297", "cand-1655", "cand-7465"],
    )
    update(
        "st-chp8-p209-ruffo-patronage-palace-cultural-centre-until-death", True,
        "This statement is narrowed to the palace's reported cultural role in Messina; Ruffo's devotion to arts patronage is recorded separately.",
        subject="cand-7467", object_id="cand-1655",
        predicate="ruffo_palace_became_cultural_centre_of_messina_until_1678",
        claim="Haskell says Ruffo's palace in Messina became the centre of cultural life there until his death in 1678.",
        qualification="The palace is unnamed; this is Haskell's characterization of its cultural role.",
        quote_text=excerpt(65, 65, "and his palace in Messina became", "1678."),
        start_line=65, end_line=65,
        mentioned=["cand-7467", "cand-1655", "cand-2297"],
        remove_qualifiers=["ocr_corrections"],
    )
    update(
        "st-chp8-p209-ruffo-personal-interest-and-limited-acquaintance", False,
        "This statement records Ruffo's personal interest in works he ordered; the following clause about his limited acquaintance with other paintings remains in its separate statement.",
        quote_text=excerpt(67, 67, "A good deal of evidence makes it clear beyond doubt", "ordered,"),
        remove_qualifiers=["modality"],
    )
    update(
        "st-chp8-p209-ruffo-knew-few-other-paintings", False,
        "This is Haskell's qualified inference about Ruffo's familiarity with paintings outside his own collection, not a relation to an identified painting.",
        claim="Haskell infers that Ruffo's acquaintance with paintings other than his own must have been negligible.",
        qualification="'Must have been' marks Haskell's inference; no other painting is identified.",
    )
    update(
        "st-chp8-p209-ruffo-pressed-network-into-agency", True,
        "Haskell explicitly says Ruffo pressed family, friends, employed artists and dealers into intermediary work; the unnamed group remains open.",
    )
    update(
        "st-chp8-p209-ruffo-raised-price-guercino-promised-proportionate-picture", True,
        "The statement records Ruffo's later offer and Guercino's reported response; the source attribution and printed currency are retained.",
        add_corrections=[{"source_line": 69, "ocr": "��", "print": "curly single quotation marks", "basis": "CHP-8.pdf physical page 7."}],
    )
    update(
        "st-chp8-p209-ruffo-seems-to-set-picture-price-in-advance", False,
        "This is Haskell's qualified general interpretation of Ruffo's pricing practice and its effect on picture structure; no particular work is identified.",
    )
    update(
        "st-chp8-p209-ruffo-symmetry-and-pairs-shaped-composition", True,
        "Haskell describes Ruffo's symmetrical arrangement and preference for pairs as affecting picture composition; the source-local practice is retained as the endpoint.",
        add_corrections=[{"source_line": 68, "ocr": "pairs��either", "print": "pairs—either", "basis": "CHP-8.pdf physical page 7."}],
    )
    update(
        "st-chp8-p209-ruffo-trade-and-tax-revenue", False,
        "This statement is narrowed to Ruffo's engagement in trade; his reported income from tax revenues is recorded separately.",
        predicate="ruffo_engaged_in_trade",
        claim="Haskell says Ruffo engaged in trade.",
        qualification="The statement reports trade as part of Ruffo's biography; no particular business or transaction is identified.",
        quote_text=excerpt(63, 63, "This did not prevent him engaging in trade", "trade"),
        start_line=63, end_line=63,
        mentioned=["cand-2297"],
    )
    update(
        "st-chp8-p209-ruffo-travelled-seemingly-only-within-calabria", True,
        "This statement is narrowed to Haskell's qualified travel claim; the following agent-mediated information is captured in the separate intermediary statements.",
        claim="Haskell says Ruffo seems never to have travelled beyond Calabria.",
        qualification="The source says 'seems'; it does not establish a complete itinerary.",
        quote_text=excerpt(67, 68, "He seems never to have travelled beyond", "Calabria,"),
        mentioned=["cand-2297", "cand-7469"],
    )

    new_statements = [
        {
            "statement_id": "st-chp8-p209-ruffo-born-into-unidentified-aristocratic-family",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2297",
            "object_candidate_id": "cand-12038",
            "predicate": "antonio_ruffo_belonged_to_an_unidentified_aristocratic_family",
            "qualifiers": {
                "source_line_start": 63, "source_line_end": 63, "printed_page": 209, "pdf_physical_page": 7,
                "claim": "Haskell says Antonio Ruffo was born into one of the great aristocratic families.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The family is not named; no lineage or branch is inferred.",
                "mentioned_candidate_ids": ["cand-2297", "cand-12038"],
                "relation_candidate": True,
                "relation_candidate_note": "The source explicitly identifies an aristocratic family connection but leaves the family unnamed.",
            },
            "original_quote": excerpt(63, 63, "of one of the great aristocratic families", "families"),
            "origin": "book", "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp8-p209-ruffo-moved-into-palace-before-collecting",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2297",
            "object_candidate_id": "cand-7467",
            "predicate": "ruffo_moved_into_messina_palace_shortly_before_beginning_to_collect",
            "qualifiers": {
                "source_line_start": 66, "source_line_end": 67, "printed_page": 209, "pdf_physical_page": 7,
                "claim": "Haskell says Ruffo moved into the palace on Strada Emmanuela shortly before he began collecting in about 1646.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The palace is unidentified; 'shortly after' and the collecting date remain approximate source language.",
                "mentioned_candidate_ids": ["cand-2297", "cand-7467", "cand-7466"],
                "relation_candidate": True,
                "relation_candidate_note": "The text explicitly links Ruffo's move to the identified-in-context but unnamed palace before collecting began.",
                "ocr_corrections": [{"source_line": 67, "ocr": "Strada Emnianuela", "print": "Strada Emmanuela", "basis": "CHP-8.pdf physical page 7."}],
            },
            "original_quote": excerpt(66, 67, "shortly after moving into the palace in the", "Strada Emnianuela"),
            "origin": "book", "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp8-p209-ruffo-mother-built-palace",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-0160",
            "object_candidate_id": "cand-7467",
            "predicate": "duchess_of_bagnara_built_ruffos_palace_for_him",
            "qualifiers": {
                "source_line_start": 67, "source_line_end": 67, "printed_page": 209, "pdf_physical_page": 7,
                "claim": "Haskell says Ruffo's mother, the Duchess of Bagnara, built the palace for him.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The palace is unnamed; the builder is identified by her relationship and title in the source.",
                "mentioned_candidate_ids": ["cand-2297", "cand-0160", "cand-7467"],
                "relation_candidate": True,
                "relation_candidate_note": "The source explicitly says Ruffo's mother built the palace for him.",
            },
            "original_quote": excerpt(67, 67, "which his mother, the Duchess of Bagnara, had built for him", "him."),
            "origin": "book", "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp8-p209-ruffo-income-from-tax-revenues",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2297",
            "object_candidate_id": None,
            "predicate": "haskell_reported_ruffos_income_from_taxes_on_essential_goods",
            "qualifiers": {
                "source_line_start": 63, "source_line_end": 63, "printed_page": 209, "pdf_physical_page": 7,
                "claim": "Haskell says Ruffo's income was further increased by revenues he drew from taxes on grain, silk and other vital goods.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "The passage does not specify Ruffo's office or the mechanism by which he drew these revenues.",
                "mentioned_candidate_ids": ["cand-2297"],
                "relation_candidate": False,
                "relation_candidate_note": "This is an economic and biographical description; the passage identifies no distinct tax authority or revenue instrument as an endpoint.",
            },
            "original_quote": excerpt(63, 63, "and his income was still further increased", "goods."),
            "origin": "book", "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp8-p209-ruffo-limited-political-participation",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2297",
            "object_candidate_id": None,
            "predicate": "haskell_described_ruffos_limited_political_participation_under_spanish_rule",
            "qualifiers": {
                "source_line_start": 64, "source_line_end": 65, "printed_page": 209, "pdf_physical_page": 7,
                "claim": "Haskell says Ruffo played a limited part in the little political activity permitted to the nobility under Spanish rule.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "This general description is separate from the specific 1661 outlawing described in the following clause.",
                "mentioned_candidate_ids": ["cand-2297", "cand-4591"],
                "relation_candidate": False,
                "relation_candidate_note": "This is a broad biographical characterization without a distinct event or identified relationship endpoint.",
            },
            "original_quote": excerpt(64, 65, "He played a limited part", "Spanish rule"),
            "origin": "book", "source_file": SOURCE_REL,
        },
        {
            "statement_id": "st-chp8-p209-ruffo-life-devoted-to-arts",
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-2297",
            "object_candidate_id": None,
            "predicate": "haskell_described_most_of_ruffos_life_as_devoted_to_arts_patronage",
            "qualifiers": {
                "source_line_start": 65, "source_line_end": 65, "printed_page": 209, "pdf_physical_page": 7,
                "claim": "Haskell says most of Ruffo's life was devoted to patronage of the arts.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "This is Haskell's general characterization; no specific artwork or patronage event is identified.",
                "mentioned_candidate_ids": ["cand-2297"],
                "relation_candidate": False,
                "relation_candidate_note": "This is a general biographical characterization without a separately identified endpoint.",
                "ocr_corrections": [{"source_line": 65, "ocr": "Use", "print": "life", "basis": "CHP-8.pdf physical page 7."}],
            },
            "original_quote": excerpt(65, 65, "But most of his Use was devoted", "arts"),
            "origin": "book", "source_file": SOURCE_REL,
        },
    ]
    for row in new_statements:
        if row["statement_id"] in by_id:
            raise SystemExit(f"planned statement ID already exists: {row['statement_id']}")
        if row["segment_id"] != SEGMENT_ID:
            raise SystemExit(f"new statement points outside p.209: {row['statement_id']}")
    statements.extend(new_statements)
    by_id.update({row["statement_id"]: row for row in new_statements})

    # Keep the p.209/p.210 fragments of one collecting-aim sentence semantically aligned.
    continuation = by_id.get("st-chp8-p210-ruffo-collection-of-leading-contemporaries")
    if not continuation or continuation.get("original_quote") != "of works by all the leading contemporaries":
        raise SystemExit("p.210 continuation no longer matches the reviewed sentence")
    continuation_q = dict(continuation.get("qualifiers") or {})
    continuation_q["relation_candidate"] = True
    continuation_q["relation_candidate_note"] = "This p.210 fragment completes the p.209 claim that Ruffo aimed to assemble a representative collection of leading contemporaries."
    continuation_q["mentioned_candidate_ids"] = list(dict.fromkeys(["cand-2297", "cand-7468", "cand-2301"]))
    continuation["qualifiers"] = continuation_q

    final_page = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(final_page) != 28 or any("relation_candidate" not in (row.get("qualifiers") or {}) for row in final_page):
        raise SystemExit("p.209 rows are not fully classified after the planned edits")
    if len(statements) != 14238 or len(candidates) != 12017 or len(mentions) != 28073:
        raise SystemExit(
            f"unexpected post-write counts: statements={len(statements)}, candidates={len(candidates)}, mentions={len(mentions)}"
        )

    outputs = {
        STATEMENTS: jsonl_bytes(statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
    }
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("p.209 statements:", len(final_page), "true:", sum(r["qualifiers"]["relation_candidate"] is True for r in final_page),
          "false:", sum(r["qualifiers"]["relation_candidate"] is False for r in final_page))
    print("new statements:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    print("new candidates:", ", ".join(row["candidate_id"] for row in new_candidates))
    print("removed nonentity mentions:", count_mention["mention_id"], criteria_mention["mention_id"])
    print("p.210 linked continuation:", continuation["qualifiers"]["relation_candidate"])
    for path, data in outputs.items():
        print(f"{path.relative_to(ROOT)} sha256={sha(data)} bytes={len(data)}")
    if args.apply:
        for path, backup in backups.items():
            backup.write_bytes(raw[path])
        for path, data in outputs.items():
            atomic_write(path, data)
        print("recovery copies:", ", ".join(str(path.relative_to(ROOT)) for path in backups.values()))


if __name__ == "__main__":
    main()
