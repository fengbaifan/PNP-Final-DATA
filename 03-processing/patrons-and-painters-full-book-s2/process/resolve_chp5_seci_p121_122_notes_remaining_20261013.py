from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l125-147"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
EXPECTED_HASHES = {
    STATEMENTS: "46156c50a6895034964411d7a205fd8190737d0cbf4154b670c65fde7bcdc09b",
    CANDIDATES: "15d2f3c9356b71d67635be95f32ff26542741c4a7891f3e59211b2d27f49d274",
    MENTIONS: "ceb802eb1e3b5397c7e1e05159ecee0445970f197053dbee1eeeccfd72ac4aa9",
}
EXPECTED_SEGMENT_SHA = "5fdb179fd5637ce1d0a0b6b3da66e4e871452e25debcd265e4749060845324e8"
NEW_CANDIDATES = {
    "cand-11909": {
        "canonical_name": "Picture dealers listed in the Accademia di S. Luca's 1636 tax record",
        "suggested_type": "term",
        "detail": "A source-defined group of picture dealers named in Haskell's account of the 1636 Accademia tax list. Individual sellers and any exact mapping between people and locations are not supplied.",
        "candidate_source_ref": f"{SEGMENT_ID}#L129",
    },
    "cand-11910": {
        "canonical_name": "Eleven unidentified pictures in the theft denounced by Antonio Maria Visconti (1699)",
        "suggested_type": "work",
        "detail": "Haskell reports that Visconti denounced the theft of eleven pictures in 1699. No titles, owners, theft location, or recovery are stated in this note.",
        "candidate_source_ref": f"{SEGMENT_ID}#L131",
    },
    "cand-11911": {
        "canonical_name": "Two unidentified pictures by Filippo Lauri and Giovanni Perusini stolen from Pellegrino Peri's shop (1681)",
        "suggested_type": "work",
        "detail": "Haskell reports the 1681 theft from Peri's shop of two pictures associated with Lauri and Perusini. No titles or one-to-one mapping between the artists and the two pictures is given.",
        "candidate_source_ref": f"{SEGMENT_ID}#L132",
    },
    "cand-11912": {
        "canonical_name": "Church of S. Luca named as recipient in the 1636 dealer tax list (identity unresolved)",
        "suggested_type": "",
        "detail": "The cited list says picture dealers owed payment to the Church of S. Luca. This passage does not determine whether the named recipient is the physical church, the Accademia, or another institutional body; keep it separate from both the Accademia candidate and the existing building candidate.",
        "candidate_source_ref": f"{SEGMENT_ID}#L129",
    },
    "cand-11913": {
        "canonical_name": "V. Russo cited as publisher of Cornelius de Stael's 1663 letter (identity unresolved)",
        "suggested_type": "person",
        "detail": "Haskell says V. Russo published the cited letter at p.170. The initials and publication title are not expanded here; do not merge with the separate V. Russo candidate cand-3530 before S3 identity review.",
        "candidate_source_ref": f"{SEGMENT_ID}#L137",
    },
}
NEW_STATEMENT_IDS = {
    "st-chp5-note-p121-n2-print-created-by",
    "st-chp5-note-p121-n2-print-after-marriage",
    "st-chp5-note-p121-n2-print-inscription-interest",
    "st-chp5-note-p121-n5-tax-recipient",
    "st-chp5-note-p121-n5-dealers-piazza-navona",
    "st-chp5-note-p121-n5-dealers-campo-marzio",
    "st-chp5-note-p121-n5-dealers-trastevere",
    "st-chp5-note-p121-n7-roccatagliata-genoese",
    "st-chp5-note-p122-n6-letter-addressed-to",
    "st-chp5-note-p122-n6-letter-published-by",
}
NEW_MENTION_IDS = {
    "m-chp5-note-L127-s2-mercati-print",
    "m-chp5-note-L129-s2-dealer-group",
    "m-chp5-note-L131-s2-visconti-stolen-pictures",
    "m-chp5-note-L132-s2-peri-stolen-pictures",
}
FALSE_NOTES = {
    "st-chp5-note-p121-n1-citation": "Bibliographic locator only; the cited books are not independently consulted in this S2 statement.",
    "st-chp5-note-p121-n2-citation": "Bibliographic locator only; the cited work is not independently consulted in this S2 statement.",
    "st-chp5-note-p121-n3-citation": "Bibliographic locator only; it adds no entity-to-entity claim.",
    "st-chp5-note-p122-n1-citation": "Bibliographic references within the footnote; these locators are not domain relations.",
    "st-chp5-note-p122-n2-citation": "Bibliographic locator for the preceding de Wael account; cited material is not independently consulted.",
    "st-chp5-note-p122-n3-citation": "Bibliographic locator plus an internal chapter pointer; neither creates a domain relation.",
    "st-chp5-note-p122-n4-citation": "Bibliographic locator only; cited material is not independently consulted.",
    "st-chp5-note-p122-n5-citation": "Bibliographic locator only; cited material is not independently consulted.",
    "st-chp5-note-p130-n1-citation": "Bibliographic locator only; cited material is not independently consulted.",
    "st-chp5-note-p130-n2-citation": "Bibliographic locator only; cited material is not independently consulted.",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp5-p121-122-notes-20261013"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp5-p121-122-notes-20261013"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp5-p121-122-notes-20261013"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_csv(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def render_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    rendered = output.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + rendered if raw.startswith(b"\xef\xbb\xbf") else rendered


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve the remaining p.121–122 footnote claims in chapter 5 section I.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha(raw[path]) != expected:
            raise SystemExit(f"protected table changed: {path.name}")
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more protected backups already exist")

    segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("protected S0 segment metadata changed")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(lines[segment["line_start"] - 1:segment["line_end"]])
    if sha(source_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("protected S0 source segment changed")
    spans = {
        "a print by Giovanni Battista Mercati": (116, 152),
        "Marriage o f St Catherine": (171, 196),
        "dedicated to Lelio Guidiccioni": (197, 227),
        "inscription recording his love of painting": (236, 278),
        "dealers in the Piazza Navona": (505, 533),
        "eleven pictures": (None, None),
        "two pictures by Filippo Lauri and Giovanni Perusini": (1480, 1531),
    }
    for text, (start, end) in spans.items():
        actual = source_text.find(text)
        if actual < 0 or (start is not None and (actual, actual + len(text)) != (start, end)):
            raise SystemExit(f"protected source span changed: {text}")
    eleven_start = source_text.index("eleven pictures")
    eleven_end = eleven_start + len("eleven pictures")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or NEW_STATEMENT_IDS.intersection(by_id):
        raise SystemExit("duplicate or unexpected statement IDs")
    expected_unset = set(FALSE_NOTES) | {
        "st-chp5-note-p121-n2-mercati-print",
        "st-chp5-note-p121-n5-archive-list",
        "st-chp5-note-p121-n6-evelyn-market",
        "st-chp5-note-p121-n7-roccatagliata-contact",
        "st-chp5-note-p121-n7-roccatagliata-sales",
        "st-chp5-note-p121-n7-visconti-shop",
        "st-chp5-note-p121-n7-visconti-theft",
        "st-chp5-note-p122-n1-carlone-attack",
        "st-chp5-note-p122-n1-carlone-loan",
        "st-chp5-note-p122-n1-peri-theft",
        "st-chp5-note-p122-n6-letter-source",
    }
    actual_unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and "relation_candidate" not in (row.get("qualifiers") or {})
    }
    if actual_unset != expected_unset:
        raise SystemExit(f"protected unset statement set changed: {sorted(actual_unset)}")

    for sid, note in FALSE_NOTES.items():
        row = by_id[sid]
        q = row.setdefault("qualifiers", {})
        if row.get("predicate") != "footnote_citation":
            raise SystemExit(f"citation predicate changed: {sid}")
        row["subject_candidate_id"] = None
        row["object_candidate_id"] = None
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    def set_relation(sid: str, subject: str, obj: str | None, predicate: str, claim: str, note: str) -> dict:
        row = by_id[sid]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = obj
        row["predicate"] = predicate
        q = row.setdefault("qualifiers", {})
        q["claim"] = claim
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        return q

    # Mercati print: correct the endpoints and keep the print, its model, maker and dedication distinct.
    print_id = "st-chp5-note-p121-n2-mercati-print"
    print_parent_q = set_relation(
        print_id, "cand-6092", "cand-1281", "dedicated_to",
        "Haskell says the print is dedicated to Lelio Guidiccioni.",
        "The dedicatee is explicit; the print remains distinct from the Correggio painting it reproduces.",
    )
    print_parent_q["mentioned_candidate_ids"] = ["cand-6092", "cand-1281"]
    print_parent_q["related_statement_ids"] = sorted(NEW_STATEMENT_IDS & {
        "st-chp5-note-p121-n2-print-created-by",
        "st-chp5-note-p121-n2-print-after-marriage",
        "st-chp5-note-p121-n2-print-inscription-interest",
    })
    print_parent = by_id[print_id]
    print_parent["original_quote"] = source_text[197:227]
    print_parent["subject_candidate_id"] = "cand-6092"

    # The existing title mention identifies Correggio's underlying painting, not Mercati's print.
    candidate_fields, candidates = load_csv(raw[CANDIDATES])
    mention_fields, mentions = load_csv(raw[MENTIONS])
    candidate_rows = {row["candidate_id"]: row for row in candidates}
    mention_rows = {row["mention_id"]: row for row in mentions}
    if set(NEW_CANDIDATES).intersection(candidate_rows) or NEW_MENTION_IDS.intersection(mention_rows):
        raise SystemExit("new candidate or mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11908:
        raise SystemExit("candidate sequence changed")
    title_mention = mention_rows.get("m-chp5-note-L127-003")
    if not title_mention or title_mention["candidate_id"] != "cand-6092" or title_mention["surface_form"] != "Marriage o f St Catherine":
        raise SystemExit("protected print/painting mention mapping changed")
    title_mention["candidate_id"] = "cand-0855"
    title_mention["note"] = "This surface names Correggio's underlying Marriage of St Catherine; it is distinct from the Mercati print."
    russo_mention = mention_rows.get("m-s2-surface-5539866d956c8bd5")
    if not russo_mention or russo_mention["surface_form"] != "V. Russo":
        raise SystemExit("protected V. Russo mention changed")
    russo_mention["candidate_id"] = "cand-11913"
    russo_mention["note"] = "Publisher cited for the de Stael letter; keep separate from cand-3530 until identity review."

    # Resolve all remaining relation statements in this segment without treating source descriptions as verified facts.
    archive_id = "st-chp5-note-p121-n5-archive-list"
    archive_q = set_relation(
        archive_id, "cand-6077", "cand-11909", "lists_tax_liable_picture_dealers",
        "Haskell reports that the 1636 Accademia di S. Luca archival list names a source-defined group of picture dealers liable to pay the Church of S. Luca.",
        "The cited archive item was not independently inspected; the dealer group is unnamed and the tax recipient's identity remains open.",
    )
    archive_q["mentioned_candidate_ids"] = list(dict.fromkeys(
        [candidate_id for candidate_id in archive_q.get("mentioned_candidate_ids", []) if candidate_id != "cand-4735"]
        + ["cand-6077", "cand-11909", "cand-0007", "cand-11912", "cand-3455", "cand-6078", "cand-6079", "cand-4490"]
    ))
    archive_children = [
        "st-chp5-note-p121-n5-tax-recipient",
        "st-chp5-note-p121-n5-dealers-piazza-navona",
        "st-chp5-note-p121-n5-dealers-campo-marzio",
        "st-chp5-note-p121-n5-dealers-trastevere",
    ]
    archive_q["related_statement_ids"] = archive_children
    church_mention = mention_rows.get("m-chp5-note-L129-007")
    if not church_mention or church_mention["candidate_id"] != "cand-4735":
        raise SystemExit("protected Church of S. Luca mention changed")
    church_mention["candidate_id"] = "cand-11912"
    church_mention["note"] = "Source wording identifies the tax recipient as the Church of S. Luca; building, Academy, or institutional identity is unresolved."

    evelyn_q = set_relation(
        "st-chp5-note-p121-n6-evelyn-market", "cand-5686", "cand-3455", "market_observation_reported",
        "John Evelyn reports spending an afternoon in Piazza Navona in 1645 to see what antiquities he might purchase and to hear mountebanks; the market also offered medals, pictures and curiosities.",
        "This is Evelyn's reported visit and market description; the passage does not say that he completed a purchase.",
    )

    rocca_contact_id = "st-chp5-note-p121-n7-roccatagliata-contact"
    rocca_q = set_relation(
        rocca_contact_id, "cand-2205", "cand-1984", "close_contact_with",
        "Haskell says Giovanni Stefano Roccatagliata was in close touch with Poussin.",
        "Source-attributed contact; this does not independently verify the relationship.",
    )
    rocca_q["related_statement_ids"] = ["st-chp5-note-p121-n7-roccatagliata-genoese"]
    by_id[rocca_contact_id]["original_quote"] = source_text[980:1011]

    rocca_sales_q = set_relation(
        "st-chp5-note-p121-n7-roccatagliata-sales", "cand-2205", "cand-2684", "sold_pictures_to",
        "Haskell's printed footnote appears to say Roccatagliata sold pictures to Valguarnera.",
        "The S0 OCR reads 'old pictures; the scan appears to read 'sold pictures'. Preserve the OCR text and register this as Haskell's reported claim.",
    )
    by_id["st-chp5-note-p121-n7-roccatagliata-sales"]["original_quote"] = source_text[1016:1048]
    rocca_sales_q["print_ocr_correction"] = "2026-10-13：对照CHP-5.pdf物理第2页（印刷p.121）注7，OCR“'old pictures”在印本中疑似为“sold pictures”；保留S0转写，不改原始文本。"

    visconti_shop_q = set_relation(
        "st-chp5-note-p121-n7-visconti-shop", "cand-2781", "cand-6080", "shop_near_landmark_reported",
        "Haskell says Antonio Maria Visconti's shop was near the Albergo del Moretto.",
        "The landmark is named, but no street address or expanded identification is supplied.",
    )
    visconti_theft_q = set_relation(
        "st-chp5-note-p121-n7-visconti-theft", "cand-2781", "cand-11910", "denounced_theft_of",
        "Haskell reports that Visconti denounced the theft of eleven pictures in 1699.",
        "The eleven pictures are an unidentified work group; the source does not name the thief, location, or outcome.",
    )
    visconti_theft_q["mentioned_candidate_ids"] = list(dict.fromkeys((visconti_theft_q.get("mentioned_candidate_ids") or []) + ["cand-11910"]))
    visconti_theft_q["related_statement_ids"] = ["st-chp5-note-p121-n7-visconti-shop"]

    attack_q = set_relation(
        "st-chp5-note-p122-n1-carlone-attack", "cand-0562", "cand-6081", "attacked",
        "Haskell reports that Giovanni Andrea Carlone attacked Pellegrino Peri in 1666.",
        "The source states that Carlone attacked Peri; the relation direction follows the named actor and target.",
    )
    by_id["st-chp5-note-p122-n1-carlone-attack"]["original_quote"] = source_text[source_text.index("In 1666 he was attacked"):source_text.index("In 1666 he was attacked") + len("In 1666 he was attacked by Giovanni Andrea Carlone")]

    loan_q = set_relation(
        "st-chp5-note-p122-n1-carlone-loan", "cand-0562", "cand-6081", "refused_to_repay_loan_to",
        "Haskell says Giovanni Andrea Carlone refused to repay a loan owed to Pellegrino Peri.",
        "The footnote reports the debt and refusal; no amount, contract, or independent record is supplied.",
    )
    peri_theft_q = set_relation(
        "st-chp5-note-p122-n1-peri-theft", "cand-6081", "cand-11911", "denounced_theft_of",
        "Haskell says Peri denounced the 1681 theft from his shop of two pictures associated with Filippo Lauri and Giovanni Perusini.",
        "The two pictures have no titles; the source does not map each named artist to a particular picture.",
    )
    peri_theft_q["mentioned_candidate_ids"] = list(dict.fromkeys((peri_theft_q.get("mentioned_candidate_ids") or []) + ["cand-11911"]))

    letter_id = "st-chp5-note-p122-n6-letter-source"
    letter_q = set_relation(
        letter_id, "cand-6083", "cand-6082", "authored_by",
        "Haskell cites a letter dated 9 June 1663 as written by Cornelius de Stael.",
        "The letter is cited through V. Russo at p.170; neither the letter nor the publication was independently consulted, and the publication title is not supplied here.",
    )
    letter_q["reported_date"] = "1663-06-09"
    letter_q["cited_material_not_independently_consulted"] = True
    letter_q["related_statement_ids"] = [
        "st-chp5-note-p122-n6-letter-addressed-to",
        "st-chp5-note-p122-n6-letter-published-by",
    ]
    letter_candidate = candidate_rows.get("cand-6083")
    if not letter_candidate:
        raise SystemExit("letter candidate missing")
    letter_candidate["detail"] = "Letter cited as the source of a preference for already painted pictures; Haskell reports its date, sender, addressee, and publication by V. Russo at p.170. The original letter and publication were not independently consulted; the publication title and V. Russo's identity remain unresolved."

    genoese_statement = {
        "statement_id": "st-chp5-note-p121-n7-roccatagliata-genoese",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2205",
        "object_candidate_id": None,
        "predicate": "origin_described_as_genoese",
        "qualifiers": {
            "source_line_start": 131,
            "source_line_end": 131,
            "claim": "Haskell describes Roccatagliata as Genoese.",
            "speaker": "Haskell's footnote",
            "text_layer": "authorial footnote",
            "qualification": "This is a scalar origin description, separated from the contact relation with Poussin.",
            "mentioned_candidate_ids": ["cand-2205"],
            "pdf_physical_page": 2,
            "printed_page_locator": "p.121n7",
            "relation_candidate": False,
            "relation_candidate_note": "Single-person origin description; no relation endpoint is asserted.",
            "related_statement_ids": ["st-chp5-note-p121-n7-roccatagliata-contact"],
        },
        "original_quote": source_text[1050:1063],
        "origin": "book",
        "source_file": SOURCE_FILE,
    }

    def related_statement(statement_id: str, subject: str, obj: str | None, predicate: str, claim: str, quote: str, line: int, locator: str, mentioned: list[str], note: str, **extra) -> dict:
        q = {
            "source_line_start": line,
            "source_line_end": line,
            "claim": claim,
            "speaker": "Haskell's footnote",
            "text_layer": "substantive footnote",
            "qualification": "Source-attributed S2 candidate only; cited archival or documentary materials were not independently consulted.",
            "mentioned_candidate_ids": mentioned,
            "pdf_physical_page": 2,
            "printed_page_locator": locator,
            "relation_candidate": True,
            "relation_candidate_note": note,
        }
        q.update(extra)
        return {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": q,
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_FILE,
        }

    new_statements = [
        related_statement(
            "st-chp5-note-p121-n2-print-created-by", "cand-6092", "cand-1654", "created_by",
            "Haskell says Giovanni Battista Mercati made the print.", source_text[116:152], 127, "p.121n2",
            ["cand-6092", "cand-1654"], "The print is the subject and Mercati the maker; no date is supplied.",
            footnote_marker=2, footnote_segment=SEGMENT_ID, linked_body_statement_ids=["st-chp5-p121-guidiccioni-attributions"],
            related_statement_ids=[print_id],
        ),
        related_statement(
            "st-chp5-note-p121-n2-print-after-marriage", "cand-6092", "cand-0855", "after",
            "Haskell says Mercati's print was made after Correggio's Marriage of St Catherine.", source_text[source_text.index("after Correggio"):source_text.index("dedicated to Lelio Guidiccioni")], 127, "p.121n2",
            ["cand-6092", "cand-0855", "cand-1654"], "The print and the underlying work are distinct candidates; the index sub-entry identifies the referenced work title.",
            footnote_marker=2, footnote_segment=SEGMENT_ID, linked_body_statement_ids=["st-chp5-p121-guidiccioni-attributions"],
            related_statement_ids=[print_id],
        ),
        related_statement(
            "st-chp5-note-p121-n2-print-inscription-interest", "cand-6092", "cand-1281", "inscription_records_interest_of",
            "Haskell says the print bears an inscription recording Guidiccioni's love of painting.", source_text[236:278], 127, "p.121n2",
            ["cand-6092", "cand-1281"], "The relation is limited to Haskell's report of the inscription; its text is not independently examined.",
            footnote_marker=2, footnote_segment=SEGMENT_ID, linked_body_statement_ids=["st-chp5-p121-guidiccioni-attributions"],
            related_statement_ids=[print_id],
        ),
        related_statement(
            "st-chp5-note-p121-n5-tax-recipient", "cand-11909", "cand-11912", "liable_to_pay_tax_to",
            "Haskell reports that the picture dealers in the 1636 list were required to pay the Church of S. Luca.",
            source_text[source_text.index("Rivenditori di quadri"):source_text.index(" This includes dealers")], 129, "p.121n5",
            ["cand-11909", "cand-11912", "cand-0007"],
            "The quoted recipient is preserved as an open candidate; the passage does not resolve building versus institutional identity.",
            footnote_marker=5, footnote_segment=SEGMENT_ID,
            open_endpoint_reason="The source says Church of S. Luca; its precise identity as building, Academy, or corporate recipient is unresolved.",
            related_statement_ids=[archive_id],
        ),
        related_statement(
            "st-chp5-note-p121-n5-dealers-piazza-navona", "cand-11909", "cand-3455", "dealers_listed_in",
            "The 1636 list includes picture dealers in Piazza Navona.", source_text[505:533], 129, "p.121n5",
            ["cand-11909", "cand-3455"], "The list gives a group-level location; individual dealers are not mapped to a specific district.",
            footnote_marker=5, footnote_segment=SEGMENT_ID, related_statement_ids=[archive_id],
        ),
        related_statement(
            "st-chp5-note-p121-n5-dealers-campo-marzio", "cand-11909", "cand-6078", "dealers_listed_in",
            "The 1636 list includes picture dealers in Campo Marzio.", source_text[source_text.index("Campo Marzio"):source_text.index("Campo Marzio") + len("Campo Marzio")], 129, "p.121n5",
            ["cand-11909", "cand-6078"], "The list gives a group-level location; individual dealers are not mapped to a specific district.",
            footnote_marker=5, footnote_segment=SEGMENT_ID, related_statement_ids=[archive_id],
        ),
        related_statement(
            "st-chp5-note-p121-n5-dealers-trastevere", "cand-11909", "cand-6079", "dealers_listed_in",
            "The 1636 list includes picture dealers in Trastevere.", source_text[source_text.index("Trastevere"):source_text.index("Trastevere") + len("Trastevere")], 129, "p.121n5",
            ["cand-11909", "cand-6079"], "The list gives a group-level location; individual dealers are not mapped to a specific district.",
            footnote_marker=5, footnote_segment=SEGMENT_ID, related_statement_ids=[archive_id],
        ),
        related_statement(
            "st-chp5-note-p122-n6-letter-addressed-to", "cand-6083", "cand-2297", "addressed_to",
            "Haskell identifies Don Antonio Ruffo as the addressee of Cornelius de Stael's letter dated 9 June 1663.",
            source_text[source_text.index("Letter from Cornelius"):source_text.index(" published by V. Russo")], 137, "p.122n6",
            ["cand-6083", "cand-6082", "cand-2297"], "The named addressee is explicit; the letter itself was not independently consulted.",
            footnote_marker=6, footnote_segment=SEGMENT_ID, reported_date="1663-06-09",
            cited_material_not_independently_consulted=True, related_statement_ids=["st-chp5-note-p122-n6-letter-source"],
        ),
        related_statement(
            "st-chp5-note-p122-n6-letter-published-by", "cand-6083", "cand-11913", "published_by",
            "Haskell says V. Russo published the cited de Stael letter at p.170.",
            source_text[source_text.index("published by V. Russo"):source_text.index("published by V. Russo") + len("published by V. Russo")], 137, "p.122n6",
            ["cand-6083", "cand-11913"], "V. Russo's initials and the publication title are not supplied; keep this publisher candidate distinct from the separate V. Russo candidate cand-3530.",
            footnote_marker=6, footnote_segment=SEGMENT_ID, reported_date="1663-06-09",
            cited_material_not_independently_consulted=True, related_statement_ids=["st-chp5-note-p122-n6-letter-source"],
        ),
    ]
    new_statements.append(genoese_statement)
    for statement in new_statements:
        if statement["statement_id"] in by_id:
            raise SystemExit(f"new statement already exists: {statement['statement_id']}")
        statements.append(statement)

    for sid in ("st-chp5-note-p121-n7-visconti-theft", "st-chp5-note-p122-n1-peri-theft"):
        by_id[sid]["object_candidate_id"] = "cand-11910" if "visconti" in sid else "cand-11911"
    by_id["st-chp5-note-p121-n7-visconti-theft"]["predicate"] = "denounced_theft_of"
    by_id["st-chp5-note-p122-n1-peri-theft"]["predicate"] = "denounced_theft_of"
    by_id["st-chp5-note-p122-n1-carlone-attack"]["subject_candidate_id"] = "cand-0562"
    by_id["st-chp5-note-p122-n1-carlone-attack"]["object_candidate_id"] = "cand-6081"

    # Link the print and publisher as direct mentions; preserve separate object mappings.
    new_mentions = [
        {"mention_id": "m-chp5-note-L127-s2-mercati-print", "segment_id": SEGMENT_ID, "candidate_id": "cand-6092", "surface_form": source_text[116:152], "start_char": "116", "end_char": "152", "note": "The print candidate; the following title phrase is separately mapped to Correggio's underlying painting."},
        {"mention_id": "m-chp5-note-L129-s2-dealer-group", "segment_id": SEGMENT_ID, "candidate_id": "cand-11909", "surface_form": source_text[505:533], "start_char": "505", "end_char": "533", "note": "Source-defined dealer group listed across several areas; individuals and exact district mapping are unknown."},
        {"mention_id": "m-chp5-note-L131-s2-visconti-stolen-pictures", "segment_id": SEGMENT_ID, "candidate_id": "cand-11910", "surface_form": source_text[eleven_start:eleven_end], "start_char": str(eleven_start), "end_char": str(eleven_end), "note": "Eleven pictures reported stolen; titles, owner and location are not supplied."},
        {"mention_id": "m-chp5-note-L132-s2-peri-stolen-pictures", "segment_id": SEGMENT_ID, "candidate_id": "cand-11911", "surface_form": source_text[1480:1531], "start_char": "1480", "end_char": "1531", "note": "The two stolen pictures are unnamed; the passage does not map each named artist to a particular picture."},
    ]
    if NEW_MENTION_IDS != {row["mention_id"] for row in new_mentions}:
        raise SystemExit("new mention ID set changed")
    for mention in new_mentions:
        if source_text[int(mention["start_char"]):int(mention["end_char"])] != mention["surface_form"]:
            raise SystemExit(f"mention span mismatch: {mention['mention_id']}")
    mentions.extend(new_mentions)

    for candidate_id, spec in NEW_CANDIDATES.items():
        candidates.append({
            "candidate_id": candidate_id,
            "index_entry_id": "",
            "canonical_name": spec["canonical_name"],
            "index_page_range": "",
            "suggested_type": spec["suggested_type"],
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": spec["detail"],
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": spec["candidate_source_ref"],
        })

    statement_output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in statements) + "\n").encode("utf-8")
    candidate_output = render_csv(raw[CANDIDATES], candidate_fields, candidates)
    mention_output = render_csv(raw[MENTIONS], mention_fields, mentions)
    rendered = {STATEMENTS: statement_output, CANDIDATES: candidate_output, MENTIONS: mention_output}
    print("Chapter 5 section I pp.121–122 notes preview:")
    print(f"classified false: {len(FALSE_NOTES)} bibliographic/internal-reference rows plus Roccatagliata's scalar origin statement")
    print("retained and corrected: print authorship/model/dedication/inscription; archive list and dealer locations; theft reports; letter sender/recipient/publisher")
    for candidate_id, spec in NEW_CANDIDATES.items():
        print(f"candidate: {candidate_id} [{spec['suggested_type'] or 'type unresolved'}, open] {spec['canonical_name']}")
    for mention in new_mentions:
        print(f"mention: {mention['mention_id']} [{mention['start_char']},{mention['end_char']}) {mention['surface_form']!r}")
    for path, output in rendered.items():
        print(f"{path.relative_to(ROOT)}: {sha(raw[path])} -> {sha(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return

    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    for path, output in rendered.items():
        temporary = path.with_name(path.name + ".tmp-s2-chp5-p121-122-notes")
        temporary.write_bytes(output)
        temporary.replace(path)
    print("mode=apply; backups=" + ", ".join(path.name for path in BACKUPS.values()))


if __name__ == "__main__":
    main()
