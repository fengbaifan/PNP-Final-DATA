from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources/01-book/CHP-5.pdf"
PAGE_IMAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p122_page_review_20261011.png"
SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l17-26"
SOURCE_SHA256 = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA256 = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
PAGE_IMAGE_SHA256 = "0b4c590a52fa27700b4d62a3cb707fde866b4f204e53986e8dccc75c3bc2968a"
SEGMENT_SHA256 = "d80b8cf98fa4d69b02d5c60d394770bc1b9b1ba65087d4bbf241f42f3454c6a3"
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
    "coverage": ROOT / "04-knowledge/tables/s2-coverage.csv",
}
EXPECTED_TABLE_SHA256 = {
    "statements": "f8205102e15a3777acecbe77b9a4623c014c61ac04740d651e9a3d6af9f0e260",
    "candidates": "e4472ddd7eafbcabff40ccb188b9bce487633ebf18bc2d334fa2c5ec60cff253",
    "mentions": "1088db158296f2d1792fa661f1c7e3d2bbab58cdf1c20d9ba38bfe230b84f8a5",
    "coverage": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = ".bak-s2-chp5-p122-20261011"
RELATION_NOTE = (
    "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
)

ORIGINALS = {
    "st-chp5-p122-carlone-debt": ("cand-0562", "cand-1878"),
    "st-chp5-p122-flemish-dealers": ("cand-0125", None),
    "st-chp5-p122-market-painters": ("cand-0125", None),
    "st-chp5-p122-market-shift": ("cand-0125", "cand-1822"),
    "st-chp5-p122-ottini-brandi": ("cand-1792", "cand-0446"),
    "st-chp5-p122-peri-gaulli": ("cand-1878", "cand-1117"),
    "st-chp5-p122-picture-export": ("cand-0125", None),
    "st-chp5-p122-rossi-preti": ("cand-2273", "cand-2056"),
    "st-chp5-p122-stael-preference": ("cand-2504", "cand-0125"),
    "st-chp5-p122-wael-clients": ("cand-2794", None),
    "st-chp5-p122-wael-stock": ("cand-2794", "cand-1117"),
    "st-chp5-p122-wael-trade": ("cand-2794", "cand-1131"),
}

CANDIDATES = [
    {
        "candidate_id": "cand-11692",
        "canonical_name": "Flemish dealers referred to on p.122 (group unspecified)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell describes the Flemish collectively as prominent dealers. No individual members or complete membership are supplied.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L18",
    },
    {
        "candidate_id": "cand-11693",
        "canonical_name": "Cornelius de Wael's unnamed compatriot artists and clients",
        "suggested_type": "term",
        "status": "open",
        "detail": "The source says de Wael dealt principally with compatriots as artists and clients; it does not identify their names or establish a full membership list. Keep this group distinct from the Flemish dealer group.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L18",
    },
    {
        "candidate_id": "cand-11694",
        "canonical_name": "Smaller pictures by Italian genre, flower, and battle painters in de Wael's collection",
        "suggested_type": "work",
        "status": "open",
        "detail": "A source-defined group of unnamed pictures; the painters and individual works are not identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L19",
    },
    {
        "candidate_id": "cand-11695",
        "canonical_name": "More important artists contrasted with de Wael on p.122 (unnamed group)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell says de Wael played little part in these artists' lives. The comparative category is the author's and its membership is unspecified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L19",
    },
    {
        "candidate_id": "cand-11696",
        "canonical_name": "Financial turmoil following Urban VIII's pontificate in Haskell's p.122 account",
        "suggested_type": "event",
        "status": "open",
        "detail": "Source-bounded event description credited with creating dealers' first large-scale opportunities; it is not attributed to Urban VIII as a personal action.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L20",
    },
    {
        "candidate_id": "cand-11697",
        "canonical_name": "Artists and painters affected by economic pressure in Haskell's p.122 account (membership unspecified)",
        "suggested_type": "term",
        "status": "open",
        "detail": "The nearby passage describes artists left helpless by retrenchment, painters working for dealers, and pressure on artists after the market crash. It names no individuals; the group records this source-defined occupational population without asserting that every statement concerns identical members.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L20",
    },
    {
        "candidate_id": "cand-11698",
        "canonical_name": "Italian pictures sent to European countries in Haskell's p.122 account",
        "suggested_type": "work",
        "status": "open",
        "detail": "An unnamed group of pictures in a general export trend; no individual title, maker, or complete list of destinations is supplied.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L23",
    },
    {
        "candidate_id": "cand-11699",
        "canonical_name": "Foreign visitors who came to Rome for short periods in Haskell's p.122 account",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell's general, qualified statement concerns temporary foreign visitors; no individuals or membership list are identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L23",
    },
    {
        "candidate_id": "cand-11700",
        "canonical_name": "Painters whom temporary visitors might approach directly on p.122 (unnamed group)",
        "suggested_type": "term",
        "status": "open",
        "detail": "The painter is a generic comparator in Haskell's statement about access to dealers; no individual painter is named.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L23",
    },
    {
        "candidate_id": "cand-11701",
        "canonical_name": "Works of art that dealers sometimes took the initiative to export in Haskell's p.122 account",
        "suggested_type": "work",
        "status": "open",
        "detail": "Haskell identifies no individual work or destination for this general dealer-initiated export practice.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L23",
    },
    {
        "candidate_id": "cand-11702",
        "canonical_name": "Painters referred to as 'these gentlemen' in Cornelius de Stael's 1663 quotation",
        "suggested_type": "term",
        "status": "open",
        "detail": "The page's bracketed word [painters] clarifies the unnamed plural group in the attributed quotation; no individual painters are identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L25",
    },
    {
        "candidate_id": "cand-11703",
        "canonical_name": "Already-painted pictures contrasted with new commissions in de Stael's 1663 quotation",
        "suggested_type": "work",
        "status": "open",
        "detail": "A source-defined class of pictures in de Stael's attributed preference; no individual works are identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L26",
    },
]

NEW_MENTIONS = [
    ("m-chp5-p122-s2-flemish-dealers", "cand-11692", "The Flemish", "The unnamed collective described as prominent dealers."),
    ("m-chp5-p122-s2-wael-compatriots", "cand-11693", "his own compatriots", "Unnamed compatriot artists and clients in Haskell's general account of de Wael."),
    ("m-chp5-p122-s2-wael-small-pictures", "cand-11694", "smaller pictures by\nItalian genre, flower and battle painters", "Unnamed pictures in de Wael's collection; individual works and painters are not identified."),
    ("m-chp5-p122-s2-wael-important-artists", "cand-11695", "more important artists", "Haskell's unnamed comparative group in the statement about de Wael's limited social involvement."),
    ("m-chp5-p122-s2-financial-turmoil", "cand-11696", "financial turmoil that followed the pontificate of Urban VIII", "Source-described event; not an action by Urban VIII."),
    ("m-chp5-p122-s2-economic-pressure-artists", "cand-11697", "Artists", "Generic artist population described as affected by Innocent X's retrenchment policy."),
    ("m-chp5-p122-s2-market-painters", "cand-11697", "more and more painters", "Generic painters described as working for dealers amid market pressure."),
    ("m-chp5-p122-s2-exported-italian-pictures", "cand-11698", "increasing number of Italian pictures which were being sent to France, Spain, England and other European countries", "Unnamed works in Haskell's general export trend."),
    ("m-chp5-p122-s2-temporary-foreign-visitors", "cand-11699", "Foreigners who came to Rome for a short time", "Unnamed visitor group in Haskell's qualified generalization."),
    ("m-chp5-p122-s2-visiting-painters", "cand-11700", "the painter", "Generic artist contrasted with dealers as an access point for temporary visitors."),
    ("m-chp5-p122-s2-dealer-exported-works", "cand-11701", "works of art", "Unnamed works in the general statement about dealers initiating exports."),
    ("m-chp5-p122-s2-stael-painters", "cand-11702", "[painters]", "Editorial bracket in the quotation clarifies the unnamed plural referent."),
    ("m-chp5-p122-s2-prepainted-pictures", "cand-11703", "already painted", "The class of pictures de Stael says he preferred buying to commissioning new works."),
]

NEW_STATEMENT_IDS = [
    "st-chp5-p122-peri-residence-near-pasquino",
    "st-chp5-p122-wael-commercial-gallery",
    "st-chp5-p122-wael-gaulli-acquaintance",
    "st-chp5-p122-wael-small-pictures",
    "st-chp5-p122-wael-important-artists",
    "st-chp5-p122-policy-artists",
    "st-chp5-p122-market-painters-work-for-dealers",
    "st-chp5-p122-market-dealers-exploit-distress",
    "st-chp5-p122-market-dealers-generous-terms",
    "st-chp5-p122-market-biography-context",
    "st-chp5-p122-visitors-dealers",
    "st-chp5-p122-visitors-painters",
    "st-chp5-p122-dealer-export-initiative",
    "st-chp5-p122-ottini-conditional-plan",
    "st-chp5-p122-ottini-commissioned-works",
    "st-chp5-p122-ottini-exported-to-france",
    "st-chp5-p122-stael-business-with-painters",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_hash(path: Path, expected: str, label: str) -> None:
    if digest(path.read_bytes()) != expected:
        raise SystemExit(f"STOP: {label} changed: {path}")


def quote_between(text: str, start: str, end: str) -> str:
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"STOP: source phrase not found: {start!r}")
    b = text.find(end, a)
    if b < 0:
        raise SystemExit(f"STOP: source ending phrase not found after {start!r}: {end!r}")
    return text[a : b + len(end)]


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return raw, bom, text, reader.fieldnames, list(reader)


def emit_csv(headers, rows, bom: bool, source_text: str) -> bytes:
    newline = "\r\n" if "\r\n" in source_text else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=newline, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in headers})
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def mention_row(text: str, item):
    mention_id, candidate_id, surface, note = item
    start = text.find(surface)
    if start < 0:
        raise SystemExit(f"STOP: mention surface not found: {mention_id}: {surface!r}")
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


def note_link(marker: int, note_statement_ids):
    return {
        "marker": marker,
        "note_line": {1: 132, 2: 133, 3: 134, 4: 135, 5: 136, 6: 137}[marker],
        "note_segment": "chp-5:05_CHP-5_sec_i:l125-147",
        "note_statement_ids": list(note_statement_ids),
        "status": "linked",
    }


NOTE_STATEMENTS = {
    1: ["st-chp5-note-p122-n1-citation", "st-chp5-note-p122-n1-carlone-attack", "st-chp5-note-p122-n1-carlone-loan", "st-chp5-note-p122-n1-peri-theft"],
    2: ["st-chp5-note-p122-n2-citation"],
    3: ["st-chp5-note-p122-n3-citation"],
    4: ["st-chp5-note-p122-n4-citation"],
    5: ["st-chp5-note-p122-n5-citation"],
    6: ["st-chp5-note-p122-n6-letter-source"],
}


def make_statement(text: str, *, statement_id: str, subject, object_, predicate: str,
                   start_line: int, end_line: int, quote_start: str, quote_end: str,
                   claim: str, qualification: str, mentioned, relation: bool,
                   relation_reason: str, marker: int | None = None):
    original_quote = quote_between(text, quote_start, quote_end)
    qualifiers = {
        "source_line_start": start_line,
        "source_line_end": end_line,
        "pdf_physical_page": 3,
        "printed_page_locator": "p.122",
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narration",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation,
        "relation_candidate_note": relation_reason,
    }
    if marker is not None:
        qualifiers["footnote_numbers"] = [marker]
        qualifiers["footnote_links"] = [note_link(marker, NOTE_STATEMENTS[marker])]
        qualifiers["footnote_link_status"] = "linked"
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": original_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
    }


def update_row(by_id, statement_id, *, subject=..., object_=..., predicate=None,
               quote=None, qpatch=None, drop=()):
    row = by_id[statement_id]
    if subject is not ...:
        row["subject_candidate_id"] = subject
    if object_ is not ...:
        row["object_candidate_id"] = object_
    if predicate is not None:
        row["predicate"] = predicate
    if quote is not None:
        row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    for key in drop:
        q.pop(key, None)
    if qpatch:
        q.update(qpatch)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and refine p.122 S2 statements; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the validated table changes")
    args = parser.parse_args()

    require_hash(SOURCE, SOURCE_SHA256, "canonical source")
    require_hash(PDF, PDF_SHA256, "chapter PDF")
    require_hash(PAGE_IMAGE, PAGE_IMAGE_SHA256, "p.122 page review image")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment = "\n".join(source_lines[16:26])
    if digest(segment.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("STOP: p.122 canonical segment changed")
    if not segment.startswith("[Page 122]\n"):
        raise SystemExit("STOP: p.122 segment boundary changed")
    segment_text = segment

    raw = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, expected in EXPECTED_TABLE_SHA256.items():
        if digest(raw[name]) != expected:
            raise SystemExit(f"STOP: {name} table changed since p.121 review")

    statement_text = raw["statements"].decode("utf-8-sig")
    statement_bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    statement_rows = [json.loads(line) for line in statement_text.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("STOP: duplicate statement_id before p.122 update")
    if set(ORIGINALS) - set(by_id):
        raise SystemExit(f"STOP: missing p.122 target statements: {sorted(set(ORIGINALS)-set(by_id))}")
    for statement_id, endpoints in ORIGINALS.items():
        row = by_id[statement_id]
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise SystemExit(f"STOP: p.122 target endpoints changed: {statement_id}")
        if row.get("qualifiers", {}).get("relation_candidate") not in (None, ""):
            raise SystemExit(f"STOP: p.122 target already classified: {statement_id}")

    cand_raw, cand_bom, cand_text, cand_headers, candidates = read_csv(TABLES["candidates"])
    mention_raw, mention_bom, mention_text, mention_headers, mentions = read_csv(TABLES["mentions"])
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    planned_candidate_ids = {row["candidate_id"] for row in CANDIDATES}
    if len(planned_candidate_ids) != len(CANDIDATES) or candidate_ids & planned_candidate_ids:
        raise SystemExit("STOP: planned candidate IDs are duplicated or already present")
    if len(set(NEW_STATEMENT_IDS)) != len(NEW_STATEMENT_IDS) or set(NEW_STATEMENT_IDS) & set(by_id):
        raise SystemExit("STOP: planned statement IDs are duplicated or already present")
    new_mentions = [mention_row(segment_text, item) for item in NEW_MENTIONS]
    new_mention_ids = {row["mention_id"] for row in new_mentions}
    if len(new_mention_ids) != len(new_mentions) or mention_ids & new_mention_ids:
        raise SystemExit("STOP: planned mention IDs are duplicated or already present")
    for row in CANDIDATES:
        for field in cand_headers:
            row.setdefault(field, "")
    all_candidate_ids = candidate_ids | planned_candidate_ids

    # Existing statements retain their stable IDs; compound claims are narrowed and split below.
    true_patch = {"relation_candidate": True, "relation_candidate_note": RELATION_NOTE}
    update_row(by_id, "st-chp5-p122-carlone-debt", qpatch=true_patch)
    update_row(
        by_id, "st-chp5-p122-flemish-dealers", subject="cand-11692", object_="cand-0125",
        predicate="prominent_as_art_dealers",
        quote=quote_between(segment_text, "The Flemish were also prominent dealers", "dealers"),
        qpatch={**true_patch, "claim": "Haskell describes the Flemish collectively as prominent dealers.",
                "qualification": "The collective's membership is unspecified; no named dealer is identified here.",
                "mentioned_candidate_ids": ["cand-11692", "cand-0125"],
                "source_line_start": 18, "source_line_end": 18},
        drop=("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment"),
    )
    update_row(
        by_id, "st-chp5-p122-market-painters", subject=None, object_=None,
        predicate="dealer_market_context_and_crash_reported",
        quote=quote_between(segment_text, "Large numbers had been attracted to Rome", "Now suddenly the market seemed to crash"),
        qpatch={"relation_candidate": False,
                "relation_candidate_note": "The antecedent of 'large numbers' is not explicit enough to assign a person-group endpoint; retain the passage as contextual narrative.",
                "claim": "Haskell describes a Rome-based clientele formed during Urban VIII's prosperous reign and says the market then seemed to crash; the antecedent of 'large numbers' is not made explicit.",
                "qualification": "The source's plural referent is left unresolved; do not assign it to dealers or artists by inference.",
                "mentioned_candidate_ids": ["cand-4490", "cand-0209", "cand-0125"],
                "referent_status": "unresolved", "source_line_start": 21, "source_line_end": 21},
        drop=("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment"),
    )
    update_row(
        by_id, "st-chp5-p122-market-shift", subject="cand-11696", object_="cand-0125",
        predicate="created_first_large_scale_opportunities_for",
        quote=quote_between(segment_text, "It was the financial turmoil", "large-scale opportunities"),
        qpatch={**true_patch, "claim": "Haskell attributes dealers' first large-scale opportunities to financial turmoil following Urban VIII's pontificate.",
                "qualification": "The source attributes the change to subsequent financial turmoil, not to a personal action by Urban VIII.",
                "mentioned_candidate_ids": ["cand-11696", "cand-0209", "cand-0125"],
                "source_line_start": 20, "source_line_end": 20},
        drop=("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment"),
    )
    update_row(
        by_id, "st-chp5-p122-ottini-brandi", predicate="received_pictures_from_to_settle_debts",
        quote=quote_between(segment_text, "Giacinto Brandi to settle his debts in pictures", "pictures"),
        qpatch={**true_patch, "claim": "Haskell says Andrea Ottini obtained pictures from Giacinto Brandi against debts.",
                "qualification": "The particular pictures and the debt amount are not identified.",
                "mentioned_candidate_ids": ["cand-1792", "cand-0446"],
                "source_line_start": 24, "source_line_end": 24,
                "footnote_numbers": [5], "footnote_links": [note_link(5, NOTE_STATEMENTS[5])], "footnote_link_status": "linked"},
    )
    update_row(
        by_id, "st-chp5-p122-peri-gaulli", predicate="employed_on_arrival",
        quote=quote_between(segment_text, "who employed the young Gaulli", "arrival in Rome"),
        qpatch={**true_patch, "claim": "Haskell says Pellegrino Peri employed the young Gaulli on his arrival in Rome.",
                "qualification": "The report is attributed to Haskell; it does not establish a formal employment contract.",
                "mentioned_candidate_ids": ["cand-1878", "cand-1117", "cand-4490"],
                "source_line_start": 18, "source_line_end": 18,
                "footnote_numbers": [1], "footnote_links": [note_link(1, ["st-chp5-note-p122-n1-citation", "st-chp5-note-p122-n1-peri-theft"])], "footnote_link_status": "linked"},
    )
    update_row(
        by_id, "st-chp5-p122-picture-export", subject="cand-11698", object_="cand-0125",
        predicate="increased_picture_exports_encouraged_rise_of_dealers",
        quote=quote_between(segment_text, "the increasing number of Italian pictures which were being sent", "during the second half of the century"),
        qpatch={**true_patch, "claim": "Haskell identifies increasing exports of Italian pictures as one factor encouraging the rise of dealers.",
                "qualification": "The source names France, Spain, England, and other European countries as destinations but does not identify individual works or exporters.",
                "mentioned_candidate_ids": ["cand-11698", "cand-0125", "cand-4266", "cand-5120", "cand-4439"],
                "source_line_start": 23, "source_line_end": 23},
        drop=("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment"),
    )
    update_row(by_id, "st-chp5-p122-rossi-preti", qpatch=true_patch)
    update_row(
        by_id, "st-chp5-p122-stael-preference", subject="cand-2504", object_="cand-11703",
        predicate="preferred_buying_already_painted_pictures_to_new_commissions",
        quote=quote_between(segment_text, "I find it much better to buy pictures", "new ones"),
        qpatch={**true_patch, "claim": "Haskell quotes Cornelius de Stael saying he preferred buying already-painted pictures to commissioning new ones.",
                "qualification": "Attributed through Haskell to a 1663 letter; the letter itself was not independently consulted.",
                "mentioned_candidate_ids": ["cand-2504", "cand-11703"],
                "source_line_start": 25, "source_line_end": 26,
                "footnote_numbers": [6], "footnote_links": [note_link(6, NOTE_STATEMENTS[6])], "footnote_link_status": "linked"},
    )
    update_row(
        by_id, "st-chp5-p122-wael-clients", subject="cand-2794", object_="cand-11693",
        predicate="dealt_principally_with_compatriot_artists_and_clients",
        quote=quote_between(segment_text, "He dealt principally with his own compatriots", "artists and clients"),
        qpatch={**true_patch, "claim": "Haskell says Cornelius de Wael dealt principally with compatriots as artists and clients.",
                "qualification": "The compatriots are unnamed; do not infer their nationality or equate them with the separate Flemish dealer group.",
                "mentioned_candidate_ids": ["cand-2794", "cand-11693"],
                "source_line_start": 18, "source_line_end": 18},
        drop=("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment"),
    )
    update_row(
        by_id, "st-chp5-p122-wael-stock", predicate="owned_early_works_by",
        quote=quote_between(segment_text, "Though he also owned early works by Gaulli", "early works by Gaulli"),
        qpatch={**true_patch, "claim": "Haskell says de Wael owned early works by Gaulli.",
                "qualification": "The works are not individually titled; this statement does not turn the ownership claim into proof that de Wael knew Gaulli.",
                "mentioned_candidate_ids": ["cand-2794", "cand-1117"],
                "source_line_start": 18, "source_line_end": 19,
                "footnote_numbers": [2], "footnote_links": [note_link(2, NOTE_STATEMENTS[2])], "footnote_link_status": "linked"},
    )
    update_row(
        by_id, "st-chp5-p122-wael-trade", predicate="left_place_in_year",
        quote=quote_between(segment_text, "who left Genoa in 1657", "1657"),
        qpatch={**true_patch, "claim": "Haskell says Cornelius de Wael left Genoa in 1657.",
                "qualification": "The move is reported by Haskell; the following commercial activity and gallery description are recorded separately.",
                "mentioned_candidate_ids": ["cand-2794", "cand-1131"],
                "source_line_start": 18, "source_line_end": 18},
        drop=("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment"),
    )

    # New statements atomize the remaining explicit relations and retain scalar context.
    statements = [
        make_statement(segment_text, statement_id="st-chp5-p122-peri-residence-near-pasquino", subject="cand-1878", object_="cand-6016", predicate="lived_near_landmark_reported", start_line=18, end_line=18, quote_start="who lived near the statue of Pasquino", quote_end="seventeenth century", claim="Haskell says Pellegrino Peri lived near the statue of Pasquino during the second half of the seventeenth century.", qualification="The statue is retained as the named landmark; no further identity or residence address is supplied.", mentioned=["cand-1878", "cand-6016"], relation=True, relation_reason=RELATION_NOTE, marker=1),
        make_statement(segment_text, statement_id="st-chp5-p122-wael-commercial-gallery", subject="cand-2794", object_=None, predicate="commercial_activity_and_gallery_reported", start_line=18, end_line=18, quote_start="engaged in extensive commercial activities", quote_end="evidently for sale", claim="Haskell says de Wael engaged in extensive commercial activity and had a large gallery of pictures apparently for sale.", qualification="Evidently qualifies the sale status; the gallery is not treated as a separate institution.", mentioned=["cand-2794"], relation=False, relation_reason="A scalar account of de Wael's activity and gallery; it does not assert a second identified entity endpoint.", marker=2),
        make_statement(segment_text, statement_id="st-chp5-p122-wael-gaulli-acquaintance", subject="cand-2794", object_="cand-1117", predicate="probable_acquaintance_reported", start_line=18, end_line=19, quote_start="Gaulli whom he must have known in Genoa", quote_end="Genoa", claim="Haskell infers that de Wael must have known Gaulli in Genoa.", qualification="Must have known is Haskell's inference, not direct evidence of a meeting.", mentioned=["cand-2794", "cand-1117", "cand-1131"], relation=True, relation_reason=RELATION_NOTE, marker=2),
        make_statement(segment_text, statement_id="st-chp5-p122-wael-small-pictures", subject="cand-2794", object_="cand-11694", predicate="owned_smaller_pictures_reported", start_line=18, end_line=19, quote_start="smaller pictures by", quote_end="battle painters", claim="Haskell says de Wael also owned smaller pictures by Italian genre, flower, and battle painters.", qualification="The painters and individual pictures are unnamed; no maker is inferred.", mentioned=["cand-2794", "cand-11694"], relation=True, relation_reason=RELATION_NOTE, marker=2),
        make_statement(segment_text, statement_id="st-chp5-p122-wael-important-artists", subject="cand-2794", object_="cand-11695", predicate="had_little_part_in_lives_of_reported", start_line=19, end_line=19, quote_start="he played little part in the lives of the more important artists", quote_end="more important artists", claim="Haskell says de Wael played little part in the lives of more important artists.", qualification="More important is Haskell's comparative category; the individuals and membership are unspecified.", mentioned=["cand-2794", "cand-11695"], relation=True, relation_reason=RELATION_NOTE, marker=2),
        make_statement(segment_text, statement_id="st-chp5-p122-policy-artists", subject="cand-11697", object_="cand-1822", predicate="left_helpless_under_retrenchment_policy_reported", start_line=20, end_line=20, quote_start="Artists were left helpless", quote_end="Innocent X", claim="Haskell says artists were left helpless by the economic-retrenchment policy pursued by Innocent X.", qualification="This is Haskell's account of the policy's effect; no individual artist or policy instrument is identified.", mentioned=["cand-11697", "cand-1822"], relation=True, relation_reason=RELATION_NOTE),
        make_statement(segment_text, statement_id="st-chp5-p122-market-painters-work-for-dealers", subject="cand-11697", object_="cand-0125", predicate="worked_for_dealers_under_market_pressure_reported", start_line=21, end_line=21, quote_start="more and more painters had to work for dealers", quote_end="dealers", claim="Haskell says more and more painters had to work for dealers after the market crash.", qualification="The painters and dealers are unnamed groups; no individual employment is inferred.", mentioned=["cand-11697", "cand-0125"], relation=True, relation_reason=RELATION_NOTE),
        make_statement(segment_text, statement_id="st-chp5-p122-market-dealers-exploit-distress", subject="cand-0125", object_="cand-11697", predicate="exploited_painters_distress_reported", start_line=21, end_line=21, quote_start="many of whom exploited their distress", quote_end="to the full", claim="Haskell says many dealers exploited the distress of painters who had to work for them.", qualification="Many preserves the source's quantifier; the individual dealers and painters are not named.", mentioned=["cand-0125", "cand-11697"], relation=True, relation_reason=RELATION_NOTE),
        make_statement(segment_text, statement_id="st-chp5-p122-market-dealers-generous-terms", subject="cand-0125", object_="cand-11697", predicate="offered_generous_terms_to_painters_reported", start_line=21, end_line=21, quote_start="Others apparently offered generous terms", quote_end="terms", claim="Haskell says other dealers apparently offered generous terms to painters.", qualification="Apparently and others preserve the author's uncertainty and distinction from dealers said to exploit artists.", mentioned=["cand-0125", "cand-11697"], relation=True, relation_reason=RELATION_NOTE),
        make_statement(segment_text, statement_id="st-chp5-p122-market-biography-context", subject="cand-11697", object_=None, predicate="contemporary_biographies_reported", start_line=21, end_line=21, quote_start="We get vivid accounts in contemporary biographies", quote_end="at the time", claim="Haskell says contemporary biographies give vivid accounts of the market crisis's effects on artists.", qualification="The cited works are not independently read here; footnote 3 points to Passeri and the book's Chapter 6 discussion.", mentioned=["cand-11697"], relation=False, relation_reason="This records Haskell's source-attribution about accounts of artists' experience, not a relation between two entities.", marker=3),
        make_statement(segment_text, statement_id="st-chp5-p122-visitors-dealers", subject="cand-11699", object_="cand-0125", predicate="found_dealers_easier_to_approach_reported", start_line=23, end_line=23, quote_start="Foreigners who came to Rome for a short time", quote_end="go to dealers", claim="Haskell says temporary foreign visitors must certainly have found dealers easier to approach.", qualification="Must certainly have found is Haskell's inference, not a reported statement by identified visitors.", mentioned=["cand-11699", "cand-0125", "cand-4490"], relation=True, relation_reason=RELATION_NOTE),
        make_statement(segment_text, statement_id="st-chp5-p122-visitors-painters", subject="cand-11699", object_="cand-11700", predicate="found_direct_approach_to_painters_less_easy_reported", start_line=23, end_line=23, quote_start="Foreigners who came to Rome for a short time", quote_end="direct to the painter", claim="Haskell contrasts visitors' easier access to dealers with direct access to painters.", qualification="The comparison is a source-attributed generalization about temporary visitors and unnamed painters.", mentioned=["cand-11699", "cand-11700", "cand-0125", "cand-4490"], relation=True, relation_reason=RELATION_NOTE),
        make_statement(segment_text, statement_id="st-chp5-p122-dealer-export-initiative", subject="cand-0125", object_="cand-11701", predicate="sometimes_initiated_export_of_works_reported", start_line=23, end_line=23, quote_start="dealers themselves sometimes took the initiative", quote_end="works of art", claim="Haskell says dealers sometimes took the initiative in exporting works of art.", qualification="No individual dealer, work, or destination is named.", mentioned=["cand-0125", "cand-11701"], relation=True, relation_reason=RELATION_NOTE),
        make_statement(segment_text, statement_id="st-chp5-p122-ottini-conditional-plan", subject="cand-1792", object_="cand-0446", predicate="considered_regular_work_arrangement_conditionally", start_line=24, end_line=24, quote_start="He did so well out of this that he said that if Brandi", quote_end="take to the art trade", claim="Haskell says Ottini stated conditionally that if Brandi could be induced to work regularly for him, he would close his inn and enter the art trade.", qualification="This is a conditional intention, not evidence that Brandi entered regular employment or that Ottini closed the inn.", mentioned=["cand-1792", "cand-0446"], relation=True, relation_reason=RELATION_NOTE, marker=5),
        make_statement(segment_text, statement_id="st-chp5-p122-ottini-commissioned-works", subject="cand-1792", object_="cand-0446", predicate="commissioned_works_from_reported", start_line=24, end_line=24, quote_start="he still commissioned several works from him", quote_end="works from him", claim="Haskell says Ottini commissioned several works from Brandi.", qualification="The works are unnamed; this is reported through Haskell and Pascoli.", mentioned=["cand-1792", "cand-0446"], relation=True, relation_reason=RELATION_NOTE, marker=5),
        make_statement(segment_text, statement_id="st-chp5-p122-ottini-exported-to-france", subject="cand-1792", object_="cand-4266", predicate="sent_commissioned_works_to_reported", start_line=24, end_line=24, quote_start="sent them to France", quote_end="France", claim="Haskell says Ottini sent the works he commissioned from Brandi to France.", qualification="Them refers to the unnamed commissioned works; France is the geographic destination.", mentioned=["cand-1792", "cand-0446", "cand-4266"], relation=True, relation_reason=RELATION_NOTE, marker=5),
        make_statement(segment_text, statement_id="st-chp5-p122-stael-business-with-painters", subject="cand-2504", object_="cand-11702", predicate="described_business_with_painters_as_troublesome", start_line=25, end_line=26, quote_start="very troublesome to do business with these gentlemen [painters]", quote_end="[painters]", claim="Haskell quotes de Stael describing business with painters as very troublesome.", qualification="The quotation is attributed through Haskell to a 1663 letter; [painters] is an editorial clarification, and the letter was not independently consulted.", mentioned=["cand-2504", "cand-11702"], relation=True, relation_reason=RELATION_NOTE, marker=6),
    ]
    if [row["statement_id"] for row in statements] != NEW_STATEMENT_IDS:
        raise SystemExit("STOP: constructed p.122 statement IDs differ from the declared plan")
    for row in statements:
        if row["original_quote"] not in segment_text:
            raise SystemExit(f"STOP: planned quote is not an exact source substring: {row['statement_id']}")

    # Refine the existing statements; each now has a deliberate relation decision.
    update_row(by_id, "st-chp5-p122-carlone-debt", qpatch={"relation_candidate": True, "relation_candidate_note": RELATION_NOTE})
    update_row(by_id, "st-chp5-p122-rossi-preti", qpatch={"relation_candidate": True, "relation_candidate_note": RELATION_NOTE})
    for row in statements:
        if row["statement_id"] in by_id:
            raise SystemExit(f"STOP: planned new statement already exists: {row['statement_id']}")
        if row["qualifiers"]["relation_candidate"]:
            if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
                raise SystemExit(f"STOP: relation candidate lacks an endpoint: {row['statement_id']}")
            if not {row["subject_candidate_id"], row["object_candidate_id"]}.issubset(set(row["qualifiers"]["mentioned_candidate_ids"])):
                raise SystemExit(f"STOP: endpoint absent from mention candidates: {row['statement_id']}")
            if not {row["subject_candidate_id"], row["object_candidate_id"]}.issubset(all_candidate_ids):
                raise SystemExit(f"STOP: unknown relation endpoint: {row['statement_id']}")

    all_body = {**by_id, **{row["statement_id"]: row for row in statements}}
    note_body_links = {
        "st-chp5-note-p122-n1-citation": ["st-chp5-p122-peri-residence-near-pasquino"],
        "st-chp5-note-p122-n2-citation": ["st-chp5-p122-wael-stock", "st-chp5-p122-wael-gaulli-acquaintance", "st-chp5-p122-wael-small-pictures", "st-chp5-p122-wael-important-artists"],
        "st-chp5-note-p122-n3-citation": ["st-chp5-p122-market-biography-context"],
        "st-chp5-note-p122-n5-citation": ["st-chp5-p122-ottini-conditional-plan", "st-chp5-p122-ottini-commissioned-works", "st-chp5-p122-ottini-exported-to-france"],
        "st-chp5-note-p122-n6-letter-source": ["st-chp5-p122-stael-business-with-painters"],
    }
    for note_id, body_ids in note_body_links.items():
        if note_id not in by_id:
            raise SystemExit(f"STOP: expected p.122 footnote statement missing: {note_id}")
        q = by_id[note_id].setdefault("qualifiers", {})
        q["linked_body_statement_ids"] = list(dict.fromkeys(q.get("linked_body_statement_ids", []) + body_ids))

    all_mentions = mentions + new_mentions
    candidates_out = candidates + CANDIDATES
    known_candidates = candidate_ids | planned_candidate_ids
    for row in all_body.values():
        if row.get("segment_id") != SEGMENT_ID:
            continue
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is True:
            if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
                raise SystemExit(f"STOP: p.122 true relation candidate lacks endpoint: {row['statement_id']}")
            if not {row["subject_candidate_id"], row["object_candidate_id"]}.issubset(known_candidates):
                raise SystemExit(f"STOP: p.122 statement references an unknown candidate: {row['statement_id']}")
            if not {row["subject_candidate_id"], row["object_candidate_id"]}.issubset(set(q.get("mentioned_candidate_ids", []))):
                raise SystemExit(f"STOP: p.122 relation endpoint absent from mentioned_candidate_ids: {row['statement_id']}")

    has_statement_bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    old_statement_text = raw["statements"].decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in old_statement_text else "\n"
    out_lines = []
    for raw_line in old_statement_text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not line.strip():
            out_lines.append(raw_line)
            continue
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id in by_id:
            row = by_id[statement_id]
            line = json.dumps(row, ensure_ascii=False)
            ending = ending or newline
        out_lines.append(line + ending)
    if out_lines and not out_lines[-1].endswith(("\n", "\r")):
        out_lines[-1] += newline
    for row in statements:
        out_lines.append(json.dumps(row, ensure_ascii=False) + newline)
    statement_bytes = (b"\xef\xbb\xbf" if has_statement_bom else b"") + "".join(out_lines).encode("utf-8")
    candidate_bytes = emit_csv(cand_headers, candidates_out, cand_bom, cand_text)
    mention_bytes = emit_csv(mention_headers, all_mentions, mention_bom, mention_text)
    output = {"statements": statement_bytes, "candidates": candidate_bytes, "mentions": mention_bytes}

    print("p.122 source segment, PDF page 3, and review-image hashes: verified")
    print(f"existing p.122 body statements reviewed: {len(ORIGINALS)}")
    print(f"new atomic statements: {len(statements)}; new candidates: {len(CANDIDATES)}; new mentions: {len(new_mentions)}")
    print("new candidate scope:")
    for row in CANDIDATES:
        print(f"  {row['candidate_id']} [{row['suggested_type'] or 'type open'}] {row['canonical_name']}")
    print("new statements:")
    for row in statements:
        q = row["qualifiers"]
        print(f"  {row['statement_id']}: {row['subject_candidate_id']} -> {row['object_candidate_id']}; {row['predicate']}; relation_candidate={q['relation_candidate']}; {q['claim']}")
    for statement_id in ORIGINALS:
        row = by_id[statement_id]
        print(f"  {statement_id}: {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')}; {row['predicate']}; relation_candidate={row['qualifiers'].get('relation_candidate')}")
    if not args.apply:
        print("dry-run only; no table files written")
        return 0

    paths = {name: TABLES[name] for name in output}
    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in paths.items()}
    for name, backup in backups.items():
        if backup.exists():
            raise SystemExit(f"STOP: recovery copy already exists: {backup.name}")
    for name, backup in backups.items():
        shutil.copy2(paths[name], backup)
    written = []
    try:
        for name, data in output.items():
            path = paths[name]
            temp = path.with_name(path.name + ".tmp-s2-chp5-p122")
            temp.write_bytes(data)
            temp.replace(path)
            written.append(name)
    except Exception:
        for name in written:
            shutil.copy2(backups[name], paths[name])
        raise
    for name, path in paths.items():
        print(f"{name}: {digest(path.read_bytes())}; recovery copy {backups[name].name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
