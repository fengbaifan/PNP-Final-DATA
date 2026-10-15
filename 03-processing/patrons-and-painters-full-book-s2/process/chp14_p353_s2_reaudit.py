"""Controlled semantic re-audit of p.353 S2 rows; dry-run by default."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
BODY = "chp-14:14_CHP-14_intro:l63-71"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
EXPECTED_HASHES = {
    "book-statements.jsonl": "2e9d8e2331c8476560f959801d70857b951cff45d54ba9f8bf5e18a37822f63e",
    "mentions.csv": "e567ae6e336b7520060eb8eeecb6fbc6cb50b762ee6770af9fc1ea5c4aad8477",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.353 re-audit")
ARGS = parser.parse_args()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


if sha(SOURCE.read_bytes()) != SOURCE_SHA or sha(PDF.read_bytes()) != PDF_SHA:
    raise SystemExit("canonical chapter-14 Markdown/PDF source changed; refusing to write")

statement_path = TABLES / "book-statements.jsonl"
mention_path = TABLES / "mentions.csv"
for path in (statement_path, mention_path):
    current_hash = sha(path.read_bytes())
    if current_hash != EXPECTED_HASHES[path.name]:
        raise SystemExit(f"table baseline changed: {path.name} ({current_hash})")

statements = read_jsonl(statement_path)
mention_fields, mentions = read_csv(mention_path)
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_lines = source_lines[62:71]
note_lines = source_lines[167:220]
segment_texts = {BODY: "\n".join(body_lines), NOTES: "\n".join(note_lines)}
statement_by_id = {row["statement_id"]: row for row in statements}
mention_by_id = {row["mention_id"]: row for row in mentions}
baseline_statement_ids = set(statement_by_id)
baseline_statement_json = {sid: json.dumps(row, ensure_ascii=False, sort_keys=True) for sid, row in statement_by_id.items()}
baseline_mention_ids = set(mention_by_id)
baseline_mention_candidates = {mid: row["candidate_id"] for mid, row in mention_by_id.items()}
candidate_ids = {row["candidate_id"] for row in read_csv(TABLES / "entity-candidates.csv")[1]}
statement_ids = set(statement_by_id)
p353_rows = [row for row in statements if row["statement_id"].startswith("st-chp14-p353-")]
p353_mentions = [row for row in mentions if row["mention_id"].startswith("m-chp14-p353-")]
if len(p353_rows) != 24 or len(p353_mentions) != 73:
    raise SystemExit(f"unexpected p.353 baseline: {len(p353_rows)} statements, {len(p353_mentions)} mentions")

required_ids = {
    "st-chp14-p352-cleopatra-description-continuation",
    "st-chp14-p353-cleopatra-comparison-closed",
    "st-chp14-p353-tiepolo-compared-with-poussin",
    "st-chp14-p353-classical-claim-and-period-comparison",
    "st-chp14-p353-algarotti-letter-and-engraving-plan",
    "st-chp14-p353-algarotti-promotes-classical-aspect-to-augustus",
    "st-chp14-p353-framing-tiepolo-in-italian-tradition",
    "st-chp14-p353-commissioned-maecenas-picture-for-bruhl",
    "st-chp14-p353-commissioned-flora-picture-for-bruhl",
    "st-chp14-p353-two-pictures-sent-to-bruhl",
    "st-chp14-p353-subjects-chosen-to-flatter-bruhl",
    "st-chp14-p353-bruhl-possessions-in-the-pictures",
    "st-chp14-p353-note1-picture-locations-and-source",
    "st-chp14-p353-note1-leonardis-engraving",
    "st-chp14-p354-banquet-classicism-and-accuracy",
    "st-chp21-bib-l658-699-entry-14",
    "st-fm-pl-p68b-engraver",
    "st-fm-pl-p68b-maecenas",
}
missing = required_ids - statement_ids
if missing:
    raise SystemExit(f"required linked statements missing: {sorted(missing)}")


def exact_quote(start: int, end: int, quote: str) -> str:
    excerpt = "\n".join(source_lines[start - 1 : end])
    if quote not in excerpt:
        raise SystemExit(f"quote does not match source L{start}-L{end}: {quote[:100]!r}")
    return quote


def add_identity_question(row: dict, candidate_id: str, question: str) -> None:
    items = row.setdefault("qualifiers", {}).setdefault("candidate_identity_questions", [])
    if isinstance(items, dict):
        items = [items]
        row["qualifiers"]["candidate_identity_questions"] = items
    if not any(item.get("candidate_id") == candidate_id and item.get("question") == question for item in items):
        items.append({"candidate_id": candidate_id, "question": question})


def add_ref(row: dict, key: str, value: str) -> None:
    values = row.setdefault("qualifiers", {}).setdefault(key, [])
    if value not in values:
        values.append(value)


def add_statement(
    statement_id: str,
    segment_id: str,
    subject: str,
    obj: str,
    predicate: str,
    qualifiers: dict,
    quote: str,
) -> dict:
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    row = {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row
    return row


def qualifiers(start: int, end: int, claim: str, qualification: str, mentioned: list[str], **extra) -> dict:
    row = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 353,
        "pdf_physical_page": 7,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial report",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    row.update(extra)
    return row


def add_mention(mention_id: str, candidate_id: str, needle: str, note: str) -> None:
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    text = segment_texts[BODY]
    if text.count(needle) != 1:
        raise SystemExit(f"expected one p.353 source occurrence for {mention_id}: {needle!r}")
    start = text.index(needle)
    mention = {
        "mention_id": mention_id,
        "segment_id": BODY,
        "candidate_id": candidate_id,
        "surface_form": needle,
        "start_char": str(start),
        "end_char": str(start + len(needle)),
        "note": note,
    }
    mentions.append(mention)
    mention_by_id[mention_id] = mention


# Re-anchor painter references to the page-specific person index candidate T.csv#35.
for mention_id in (
    "m-chp14-p353-0016",
    "m-chp14-p353-0017",
    "m-chp14-p353-0018",
    "m-chp14-p353-0031",
    "m-chp14-p353-0054",
    "m-chp14-p353-0058",
):
    if mention_id not in mention_by_id:
        raise SystemExit(f"expected Tiepolo mention missing: {mention_id}")
    mention_by_id[mention_id]["candidate_id"] = "cand-2572"
mention_by_id["m-chp14-p353-0067"]["candidate_id"] = "cand-4101"
mention_by_id["m-chp14-p353-0069"]["candidate_id"] = "cand-0045"
add_mention(
    "m-chp14-p353-0075",
    "cand-2572",
    "the author",
    "The quoted letter identifies the picture author in Haskell’s immediate context as Tiepolo; map to the person index candidate, not the Banquet work subentry.",
)

# Correct the two same-name index seeds by their page-specific subentry context.
for statement_id in (
    "st-chp14-p353-commissioned-maecenas-picture-for-bruhl",
    "st-chp14-p353-commissioned-flora-picture-for-bruhl",
    "st-chp14-p353-two-pictures-sent-to-bruhl",
    "st-chp14-p353-subjects-chosen-to-flatter-bruhl",
):
    statement_by_id[statement_id]["subject_candidate_id"] = "cand-0045"

# Replace work/person cross-wiring throughout p.353 statements.
for row in p353_rows:
    if row.get("subject_candidate_id") in {"cand-2577", "cand-3781"}:
        row["subject_candidate_id"] = "cand-2572"
    if row.get("object_candidate_id") in {"cand-2577", "cand-3781"}:
        row["object_candidate_id"] = "cand-2572"
    mentioned = row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    row["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-2572" if candidate_id in {"cand-2577", "cand-3781"} else candidate_id
        for candidate_id in mentioned
    ]

comparison = statement_by_id["st-chp14-p353-tiepolo-compared-with-poussin"]
comparison["original_quote"] = exact_quote(
    68,
    68,
    "The idea of Tiepolo as an ‘accurate’ painter comparable to Poussin (as Algarotti claimed) may ell surprise us:",
)
comparison["qualifiers"]["claim"] = (
    "Haskell says Algarotti claimed that Tiepolo was an ‘accurate’ painter comparable to Poussin, "
    "and adds that the characterization may surprise the reader."
)
comparison["qualifiers"]["qualification"] = (
    "The comparison is attributed to Algarotti through Haskell. The printed page reads ‘may well’; "
    "the source OCR misspelling is retained in original_quote and corrected here only as an S2 reading note."
)
comparison["qualifiers"]["ocr_corrections"] = [{
    "source_line": 68,
    "ocr": "may ell",
    "print": "may well",
    "basis": "CHP-14.pdf physical page 7.",
}]
classical = statement_by_id["st-chp14-p353-classical-claim-and-period-comparison"]
classical["original_quote"] = exact_quote(
    68,
    68,
    "and yet this was certainly a more classical picture than any that he had hitherto painted, or, indeed, that had been painted by anyone in Venice since the end of the Renaissance.",
)
classical["qualifiers"]["claim"] = (
    "Haskell judges the completed picture more classical than any picture Tiepolo had previously painted "
    "and than any Venetian painting since the Renaissance ended."
)
classical["qualifiers"]["qualification"] = "The superlative is Haskell’s assessment; it is not generalized into an independently verified history of Venetian painting."

letter_statement = statement_by_id["st-chp14-p353-algarotti-letter-and-engraving-plan"]
letter_statement["subject_candidate_id"] = "cand-10292"
letter_statement["object_candidate_id"] = "cand-10291"
letter_statement["predicate"] = "letter_reports_intention_to_bring_engraving"
letter_statement["qualifiers"]["claim"] = (
    "Haskell quotes an undated letter attributed to Algarotti as saying he was bringing an engraving of the original modello "
    "so that Augustus III could see how its author had enriched and improved the composition."
)
letter_statement["qualifiers"]["qualification"] = (
    "This is Haskell’s report of the quoted letter, which was not independently consulted. The passage gives no date or repository; "
    "the stated intention does not establish delivery. Haskell’s context identifies ‘the author’ as Tiepolo and ‘His Majesty’ as Augustus III."
)
letter_statement["qualifiers"].pop("relation_candidate", None)
letter_statement["qualifiers"]["mentioned_candidate_ids"] = [
    "cand-10292", "cand-0045", "cand-0052", "cand-0458", "cand-10291", "cand-0149", "cand-2572"
]
add_identity_question(
    letter_statement,
    "cand-4100",
    "The quoted letter calls the depicted object the original modello; compare it with the small Cognacq-Jay Banquet candidate cand-4100 in S3, but do not treat the identity as established in S2.",
)

comparison["qualifiers"]["mentioned_candidate_ids"] = [
    "cand-2572" if x == "cand-2577" else x
    for x in comparison["qualifiers"].get("mentioned_candidate_ids", [])
]
add_identity_question(
    comparison,
    "cand-3781",
    "Compare the page-specific index person candidate cand-2572 (T.csv#35) with accepted-KU candidate cand-3781 for Giambattista Tiepolo in S3; keep them separate until alignment.",
)

for statement_id in (
    "st-chp14-p353-commissioned-maecenas-picture-for-bruhl",
    "st-chp14-p353-commissioned-flora-picture-for-bruhl",
    "st-chp14-p353-two-pictures-sent-to-bruhl",
    "st-chp14-p353-subjects-chosen-to-flatter-bruhl",
):
    row = statement_by_id[statement_id]
    row["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-2572" if x == "cand-3781" else x
        for x in row["qualifiers"].get("mentioned_candidate_ids", [])
    ]
add_identity_question(
    statement_by_id["st-chp14-p353-commissioned-maecenas-picture-for-bruhl"],
    "cand-0052",
    "Compare this Brühl-specific Algarotti index candidate cand-0045 (A.csv#46) with the broader Algarotti–Tiepolo index candidate cand-0052 in S3; do not merge in S2.",
)

open_motif = statement_by_id["st-chp14-p353-bruhl-possessions-in-the-pictures"]
open_motif["subject_candidate_id"] = "cand-2572"
open_motif["qualifiers"]["mentioned_candidate_ids"] = [
    cid for cid in open_motif["qualifiers"].get("mentioned_candidate_ids", []) if cid != "cand-4174"
]
add_identity_question(
    statement_by_id["st-chp14-p353-king-prefers-old-masters"],
    "cand-9091",
    "The newly mentioned old-master collection cand-11498 may or may not be the Dresden royal gallery cand-9091; preserve the distinction for S3.",
)

# Make the p.352/p.353 continuation, p.353/p.354 continuation, footnote, plate, and bibliography links bidirectional.
add_ref(statement_by_id["st-chp14-p352-cleopatra-description-continuation"], "cross_reference_statement_ids", "st-chp14-p353-cleopatra-comparison-closed")
add_ref(statement_by_id["st-chp14-p353-cleopatra-comparison-closed"], "cross_reference_statement_ids", "st-chp14-p352-cleopatra-description-continuation")
add_ref(statement_by_id["st-chp14-p354-banquet-classicism-and-accuracy"], "cross_reference_statement_ids", "st-chp14-p353-bruhl-possessions-in-the-pictures")
add_ref(open_motif, "cross_reference_statement_ids", "st-chp14-p354-banquet-classicism-and-accuracy")
note_locations = statement_by_id["st-chp14-p353-note1-picture-locations-and-source"]
note_locations["qualifiers"]["qualification"] = (
    "The Hermitage and De Young locations are reported in Haskell’s note and are not verified current custody. "
    "The matching internal bibliography entry repeats the article title, year and pages; neither the article nor cited pages were independently consulted. "
    "The surname-only author candidate remains unaligned for S3."
)
for ref in (
    "st-chp21-bib-l658-699-entry-14",
    "st-chp14-p353-commissioned-maecenas-picture-for-bruhl",
    "st-chp14-p353-commissioned-flora-picture-for-bruhl",
):
    add_ref(note_locations, "cross_reference_statement_ids", ref)
    add_ref(note_locations, "linked_bibliography_statement_ids" if ref.startswith("st-chp21") else "linked_body_statement_ids", ref)
add_ref(statement_by_id["st-chp21-bib-l658-699-entry-14"], "cross_reference_statement_ids", "st-chp14-p353-note1-picture-locations-and-source")
for ref in ("st-fm-pl-p68b-engraver", "st-fm-pl-p68b-maecenas"):
    add_ref(statement_by_id["st-chp14-p353-note1-leonardis-engraving"], "cross_reference_statement_ids", ref)
    add_ref(statement_by_id[ref], "cross_reference_statement_ids", "st-chp14-p353-note1-leonardis-engraving")

body_quote_commission = exact_quote(69, 69, "Algarotti commissioned two other pictures from Tiepolo at this time")
body_quote_sent = exact_quote(69, 69, "both of whichdie sent to Augustus’s all-powerful minister, Count Briihl.1")
body_quote_letter = letter_statement["original_quote"]
note_quote = statement_by_id["st-chp14-p353-note1-picture-locations-and-source"]["original_quote"]
motif_quote = exact_quote(
    70,
    71,
    "making Tiepolo insert into the picture two of Bruhl’s most treasured possessions: the hanging gardens and the\nNeptune fountain by Lorenzo Mattielli from his town and country houses.",
)

def qrel(start: int, end: int, claim: str, qualification: str, mentioned: list[str], **extra) -> dict:
    return qualifiers(start, end, claim, qualification, mentioned, relation_candidate=True, **extra)


def add_pairwise_work_relations(work: str, name: str, location: str, loc_name: str) -> None:
    created = add_statement(
        f"st-chp14-p353-{name}-created-by-tiepolo",
        BODY, work, "cand-2572", "created_by",
        qrel(69, 69,
             f"Haskell identifies the {name} picture as one of the two pictures commissioned from Tiepolo.",
             "‘From Tiepolo’ is Haskell’s attribution in the commission account; note 1 identifies this picture by its Maecenas/Flora subject. No independent authorship verification is claimed.",
             [work, "cand-2572"], cross_reference_statement_ids=[
                 f"st-chp14-p353-commissioned-{name}-picture-for-bruhl",
                 "st-chp14-p353-note1-picture-locations-and-source",
             ]),
        body_quote_commission,
    )
    add_statement(
        f"st-chp14-p353-{name}-sent-to-bruhl",
        BODY, work, "cand-0458", "sent_to",
        qrel(69, 69,
             f"Haskell reports that the {name} picture was among the two works sent to Count Brühl.",
             "The sentence says both commissioned pictures were sent; note 1 identifies the pair as Maecenas and Flora. It does not establish receipt or installation.",
             [work, "cand-0458", "cand-0045"], cross_reference_statement_ids=[
                 "st-chp14-p353-two-pictures-sent-to-bruhl",
                 "st-chp14-p353-note1-picture-locations-and-source",
             ]),
        body_quote_sent,
    )
    add_statement(
        f"st-chp14-p353-{name}-located-at-{loc_name}",
        NOTES, work, location, "located_at",
        qrel(185, 185,
             f"Haskell’s note reports the {name} picture at {loc_name}.",
             "This is the location reported in the cited note, not verified current custody; the exact date of the reported location is not specified.",
             [work, location], cross_reference_statement_ids=[
                 "st-chp14-p353-note1-picture-locations-and-source",
                 "st-chp21-bib-l658-699-entry-14",
             ], citation_statement_ids=["st-chp21-bib-l658-699-entry-14"]),
        note_quote,
    )


add_pairwise_work_relations("cand-2597", "maecenas", "cand-5795", "hermitage")
add_pairwise_work_relations("cand-2590", "flora", "cand-10295", "de-young-museum")

for motif_id, motif_name in (("cand-10293", "hanging gardens"), ("cand-10294", "Neptune fountain")):
    add_statement(
        f"st-chp14-p353-{motif_name.lower().replace(' ', '-')}-reported-bruhl-possession",
        BODY, motif_id, "cand-0458", "reported_possession_by",
        qrel(70, 71,
             f"Haskell describes the {motif_name} as one of Count Brühl’s most treasured possessions.",
             "This records Haskell’s possession wording; it does not identify a particular town/country house or establish a legal title record.",
             [motif_id, "cand-0458", "cand-1584"], cross_reference_statement_ids=[
                 "st-chp14-p353-bruhl-possessions-in-the-pictures"
             ]),
        motif_quote,
    )

letter_ref_quote = exact_quote(68, 68, "he wrote to Bruhl")
letter_author = add_statement(
    "st-chp14-p353-letter-authored-by-algarotti",
    BODY, "cand-10292", "cand-0045", "authored_by",
    qrel(68, 68,
         "Haskell attributes the quoted, undated letter to Algarotti.",
         "The source says ‘he wrote to Bruhl’; the letter’s date and repository are not given, and the original was not consulted.",
         ["cand-10292", "cand-0045", "cand-0458"], cross_reference_statement_ids=[
             "st-chp14-p353-algarotti-letter-and-engraving-plan"
         ]),
    letter_ref_quote,
)
letter_address = add_statement(
    "st-chp14-p353-letter-addressed-to-bruhl",
    BODY, "cand-10292", "cand-0458", "addressed_to",
    qrel(68, 68,
         "Haskell says the undated Algarotti letter was written to Count Brühl.",
         "The addressee is explicit in Haskell’s narrative; no date, repository, or independently consulted original is supplied.",
         ["cand-10292", "cand-0045", "cand-0458"], cross_reference_statement_ids=[
             "st-chp14-p353-algarotti-letter-and-engraving-plan"
         ]),
    letter_ref_quote,
)
intent_quote = exact_quote(
    68,
    68,
    "‘I am bringing with me an engraving of the original modello so that His Majesty can see how greatly the imagination of the author has enriched and improved the composition’",
)
intent = add_statement(
    "st-chp14-p353-algarotti-intends-to-bring-engraving",
    BODY, "cand-0045", "cand-10291", "intends_to_bring",
    qrel(68, 68,
         "In the letter quoted by Haskell, Algarotti says he is bringing the engraving of the original modello so Augustus III can see it.",
         "This is a reported intention; it does not establish that the engraving was delivered or seen. The original modello’s identity remains open for S3.",
         ["cand-0045", "cand-0052", "cand-10291", "cand-0149", "cand-2572"], cross_reference_statement_ids=[
             "st-chp14-p353-algarotti-letter-and-engraving-plan"
         ]),
    intent_quote,
)
add_identity_question(
    letter_author,
    "cand-0052",
    "Compare Brühl-specific Algarotti candidate cand-0045 with broader Algarotti–Tiepolo candidate cand-0052 in S3; do not merge in S2.",
)

# Preserve the multi-picture motif attribution as open: the source does not assign
# either feature to Maecenas versus Flora.

for row in statements:
    if row["statement_id"].startswith("st-chp14-p353-"):
        q = row.get("qualifiers", {})
        for key in ("subject_candidate_id", "object_candidate_id"):
            cid = row.get(key)
            if cid and cid not in candidate_ids:
                raise SystemExit(f"missing candidate on {row['statement_id']}: {cid}")
        for cid in q.get("mentioned_candidate_ids", []):
            if cid not in candidate_ids:
                raise SystemExit(f"missing mentioned candidate on {row['statement_id']}: {cid}")
        for key in ("cross_reference_statement_ids", "linked_body_statement_ids", "linked_note_statement_ids",
                    "footnote_note_statement_ids", "linked_bibliography_statement_ids", "citation_statement_ids"):
            for ref in q.get(key, []):
                if ref not in statement_by_id:
                    raise SystemExit(f"missing statement reference on {row['statement_id']}: {ref}")
        if q.get("relation_candidate") is True and row["statement_id"] != "st-chp14-p353-bruhl-possessions-in-the-pictures" and not (row.get("subject_candidate_id") and row.get("object_candidate_id")):
            raise SystemExit(f"relation candidate lacks scalar endpoint: {row['statement_id']}")
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p353-"):
        text = segment_texts.get(row["segment_id"])
        start, end = int(row["start_char"]), int(row["end_char"])
        if not text or text[start:end] != row["surface_form"]:
            raise SystemExit(f"p.353 mention span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in candidate_ids:
            raise SystemExit(f"p.353 mention has missing candidate: {row['mention_id']}")

new_p353 = [row for row in statements if row["statement_id"].startswith("st-chp14-p353-")]
new_mentions = [row for row in mentions if row["mention_id"].startswith("m-chp14-p353-")]
relations = [row for row in new_p353 if row.get("qualifiers", {}).get("relation_candidate") is True]
changed_existing_statements = [
    sid for sid, row in statement_by_id.items()
    if sid in baseline_statement_ids and json.dumps(row, ensure_ascii=False, sort_keys=True) != baseline_statement_json[sid]
]
changed_mentions = [
    {"mention_id": mid, "from": baseline_mention_candidates[mid], "to": row["candidate_id"]}
    for mid, row in mention_by_id.items()
    if mid in baseline_mention_ids and row["candidate_id"] != baseline_mention_candidates[mid]
]
statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
buf = StringIO(newline="")
writer = csv.DictWriter(buf, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
writer.writeheader()
writer.writerows(mentions)
mention_bytes = buf.getvalue().encode("utf-8")

print(json.dumps({
    "mode": "apply" if ARGS.apply else "dry-run",
    "p353_statements_before": 24,
    "p353_statements_after": len(new_p353),
    "statements_added": len(new_p353) - 24,
    "p353_mentions_before": 73,
    "p353_mentions_after": len(new_mentions),
    "mentions_added": len(new_mentions) - 73,
    "p353_relation_candidates_after": len(relations),
    "complete_endpoint_relation_candidates": sum(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")) for row in relations),
    "open_relation_candidate_ids": [row["statement_id"] for row in relations if not (row.get("subject_candidate_id") and row.get("object_candidate_id"))],
    "candidate_reanchors": ["Tiepolo person mentions/statements -> cand-2572", "Brühl-specific Algarotti statements/pronouns -> cand-0045"],
    "changed_existing_statement_ids": changed_existing_statements,
    "new_statement_ids": [row["statement_id"] for row in new_p353 if row["statement_id"] not in baseline_statement_ids],
    "changed_mention_candidates": changed_mentions,
    "new_mention_ids": [row["mention_id"] for row in new_mentions if row["mention_id"] not in baseline_mention_ids],
    "statement_sha256_before": EXPECTED_HASHES["book-statements.jsonl"],
    "statement_sha256_after": sha(statement_bytes),
    "mention_sha256_before": EXPECTED_HASHES["mentions.csv"],
    "mention_sha256_after": sha(mention_bytes),
}, ensure_ascii=False, indent=2))

if ARGS.apply:
    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp14-p353-reaudit-"))
    originals = {statement_path: statement_path.read_bytes(), mention_path: mention_path.read_bytes()}
    (backup_dir / "book-statements.jsonl.before").write_bytes(originals[statement_path])
    (backup_dir / "mentions.csv.before").write_bytes(originals[mention_path])
    temp_paths = []
    try:
        for path, data in ((statement_path, statement_bytes), (mention_path, mention_bytes)):
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as f:
                f.write(data)
                temp_paths.append((Path(f.name), path))
        for temp, target in temp_paths:
            temp.replace(target)
    except Exception:
        for path, data in originals.items():
            path.write_bytes(data)
        for temp, _ in temp_paths:
            if temp.exists():
                temp.unlink()
        raise
    print(json.dumps({"recovery_backup_dir": str(backup_dir)}, ensure_ascii=False))
