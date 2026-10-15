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
TABLES = ROOT / "04-knowledge/tables"
SOURCE_PDF = ROOT / "02-sources/01-book/CHP-8.pdf"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"

P211_SEGMENT = "chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4"
P214_SEGMENT = "chp-8:08_CHP-8_sec_i_notes_p214_visual-transcription:l1-4"
P211_SEGMENT_SHA256 = "55e7ef0c7f6fcfae4d11c6a1e6420bd409d0091b8f88961687d9905f06b3ddff"
P214_SEGMENT_SHA256 = "6251d0350afb065bc2eef799260b7fb2501befb9dab467b6f67aac08656497ef"
P211_SOURCE_SHA256 = "2a50e65bd1add38adc02bce184d6e58d286424588ef617411bd5e5c9e22877a4"
P214_SOURCE_SHA256 = "7ab316ce528ffc7cdf49c1304339ed6337ac5b29b7839df3160ac281ee2e15dd"
PDF_SHA256 = "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3"

SOURCE_STATEMENT_ID = "st-chp8-p211-principal-sources-for-del-rosso-collection"
GENEALOGY_STATEMENT_ID = "st-chp8-p211-passerini-and-poligrafo-gargano-genealogical-sources"
DECREE_STATEMENT_ID = "st-chp8-p211-flour-decree-citation"
DOLCI_STATEMENT_ID = "st-chp8-p211-dolci-picture-burghley-exhibition-reference"
ADMIRERS_STATEMENT_ID = "st-chp8-p214-n4-venetian-admirers"

PROCEDURE_CANDIDATE_ID = "cand-12414"
EXHIBITION_CANDIDATE_ID = "cand-12415"
NEW_STATEMENT_IDS = {
    "st-chp8-p211-andrea-inventory-principal-source",
    "st-chp8-p211-poligrafo-gargano-family-references",
    "st-chp8-p211-flour-decree-preserved-at-archive",
    "st-chp8-p211-dolci-picture-at-burghley",
    "st-chp8-p211-dolci-exhibition-held-in-london",
    "st-chp8-p214-solimena-admirers-in-venice",
}
NEW_MENTION_IDS = {
    "m-chp8-p211-cinelli-account-document",
    "m-chp8-p211-andrea-inventory-document",
    "m-chp8-p211-flour-decree-document",
    "m-chp8-p211-dolci-london-exhibition-event",
}
REASSIGN_MENTION_ID = "m-chp8-p211-070"
REASSIGN_SURFACE = "Appalto Generale della rendita della Farine della Città, e Dominio di Firenze"

EXPECTED_INPUT_HASHES = {
    "statements": "1e5b75fdb0a3c5297074bdea24ac31704196216a9282c5f71c0a3b53713b9a32",
    "mentions": "affe280d57b88bcad997ef98d1b09fdbe363747c7a457c9a9334f24eabba3fb5",
    "candidates": "7b331dafe53d3f99e9c22e1aa9ad976bcb6a4fa454529740ecc703a346f78a33",
}
BACKUP_SUFFIX = ".bak-s2-chp8-p211-p214-endpoints-20261015"
TEMP_SUFFIX = ".tmp-s2-chp8-p211-p214-endpoints-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def source_segment(segment_id: str, expected_hash: str, expected_asset: str) -> str:
    rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    matches = [row for row in rows if row.get("segment_id") == segment_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one source segment record: {segment_id}")
    row = matches[0]
    if row.get("sha256") != expected_hash or row.get("asset_sha256") != expected_asset:
        raise ValueError(f"Source segment metadata changed: {segment_id}")
    path = ROOT / row["source_file"]
    lines = path.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines[int(row["line_start"]) - 1 : int(row["line_end"])])
    if sha(text.encode("utf-8")) != expected_hash:
        raise ValueError(f"Source segment text changed: {segment_id}")
    return text


def csv_data(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    stream = io.StringIO(raw.decode("utf-8-sig"), newline="")
    reader = csv.DictReader(stream)
    return has_bom, list(reader.fieldnames or []), list(reader)


def encode_csv_row(row: dict[str, str], fields: list[str], newline: str) -> str:
    stream = io.StringIO(newline="")
    csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(row)
    return stream.getvalue()


def patch_csv(
    raw: bytes,
    key_field: str,
    updates: dict[str, dict[str, str]],
    additions: list[dict[str, str]],
) -> bytes:
    has_bom, fields, parsed = csv_data(raw)
    if not fields:
        raise ValueError("CSV has no header.")
    if any(set(row) != set(fields) for row in additions):
        raise ValueError("New CSV row does not match the current schema.")
    ids = [row.get(key_field, "") for row in parsed]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate {key_field} values in input.")
    for new_id in (row[key_field] for row in additions):
        if new_id in set(ids):
            raise ValueError(f"New {key_field} already exists: {new_id}")
    if not set(updates).issubset(set(ids)):
        raise ValueError(f"Update target missing from {key_field}: {set(updates)-set(ids)}")

    text = raw.decode("utf-8-sig")
    physical_lines = text.splitlines(keepends=True)
    if not physical_lines:
        raise ValueError("CSV is empty.")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = [physical_lines[0]]
    seen: set[str] = set()
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != fields or reader.line_num != 1:
        raise ValueError("CSV header is not a single unchanged physical record.")
    previous_line = reader.line_num
    for row in reader:
        end_line = reader.line_num
        original_chunk = "".join(physical_lines[previous_line:end_line])
        if not original_chunk:
            raise ValueError("CSV parser could not map a logical record to source lines.")
        row_id = row.get(key_field, "")
        if row_id in updates:
            row.update(updates[row_id])
            output.append(encode_csv_row(row, fields, newline))
            seen.add(row_id)
        else:
            output.append(original_chunk)
        previous_line = end_line
    if seen != set(updates):
        raise ValueError(f"Not all requested {key_field} updates were applied.")
    for row in additions:
        output.append(encode_csv_row(row, fields, newline))
    return (("\ufeff" if has_bom else "") + "".join(output)).encode("utf-8")


def statement_counts(rows: list[dict]) -> tuple[int, int, int, int, int]:
    opened = []
    true_count = false_count = unset_count = 0
    for row in rows:
        q = row.get("qualifiers") or {}
        flag = q.get("relation_candidate")
        if flag is True:
            true_count += 1
            if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
                opened.append(row)
        elif flag is False:
            false_count += 1
        else:
            unset_count += 1
    no_reason = sum(
        not (row.get("qualifiers") or {}).get("open_endpoint_reason")
        for row in opened
    )
    return len(opened), no_reason, true_count, false_count, unset_count


def clone_statement(
    base: dict,
    statement_id: str,
    subject: str,
    object_: str,
    predicate: str,
    claim: str,
    quote: str,
    qualification: str,
    relation_note: str,
    mentioned: list[str],
    *,
    citations: list[dict] | None = None,
    extra_qualifiers: dict | None = None,
) -> dict:
    row = json.loads(json.dumps(base, ensure_ascii=False))
    q = row.setdefault("qualifiers", {})
    row["statement_id"] = statement_id
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q["claim"] = claim
    q["qualification"] = qualification
    q["relation_candidate"] = True
    q["relation_candidate_note"] = relation_note
    q["mentioned_candidate_ids"] = list(dict.fromkeys(mentioned))
    q.pop("open_endpoint_reason", None)
    if citations is not None:
        q["citations"] = citations
    if extra_qualifiers:
        q.update(extra_qualifiers)
    return row


def rewrite_jsonl(raw: bytes, updates: dict[str, dict], additions: list[dict]) -> bytes:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    seen: set[str] = set()
    all_ids = set()
    for line in lines:
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        statement_id = row.get("statement_id")
        all_ids.add(statement_id)
        if statement_id in updates:
            output.append(
                json.dumps(updates[statement_id], ensure_ascii=False, separators=(",", ":")) + ending
            )
            seen.add(statement_id)
        else:
            output.append(line)
    if seen != set(updates):
        raise ValueError(f"Not all requested statement updates were applied: {set(updates)-seen}")
    if len(all_ids) != len(lines):
        raise ValueError("Duplicate statement IDs in input.")
    for row in additions:
        if row["statement_id"] in all_ids:
            raise ValueError(f"New statement ID already exists: {row['statement_id']}")
        output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        all_ids.add(row["statement_id"])
    return (("\ufeff" if has_bom else "") + "".join(output)).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve reviewed source-document, repository, exhibition, and city endpoints in Chapter 8 notes."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha(SOURCE_PDF.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-8.pdf changed.")
    p211 = source_segment(P211_SEGMENT, P211_SEGMENT_SHA256, P211_SOURCE_SHA256)
    p214 = source_segment(P214_SEGMENT, P214_SEGMENT_SHA256, P214_SOURCE_SHA256)
    required_phrases = (
        "the account given of it in 1677 by Cinelli",
        "the complete inventory drawn up twelve years later by Andrea del Rosso himself",
        "the decree conferring the Appalto Generale",
        "This picture, which is still at Burghley",
        "was exhibited in London in 1960",
    )
    if any(p211.count(phrase) != 1 for phrase in required_phrases):
        raise ValueError("One or more reviewed p.211 phrases changed.")
    admirer_quote = "Both Luca Giordano and Solimena had a number of admirers in Venice"
    if p214.count(admirer_quote) != 1:
        raise ValueError("Reviewed p.214 generalization changed.")
    spans = {}
    for phrase in (
        "the account given of it in 1677 by Cinelli",
        "the complete inventory drawn up twelve years later by Andrea del Rosso himself",
        "the decree conferring the Appalto Generale della rendita della Farine della Città, e Dominio di Firenze for nine years as from 1 June 1676",
        REASSIGN_SURFACE,
        "was exhibited in London in 1960",
    ):
        start = p211.index(phrase)
        spans[phrase] = (start, start + len(phrase))

    raw = {
        "statements": STATEMENTS.read_bytes(),
        "mentions": MENTIONS.read_bytes(),
        "candidates": CANDIDATES.read_bytes(),
    }
    actual_hashes = {name: sha(data) for name, data in raw.items()}
    if actual_hashes != EXPECTED_INPUT_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual_hashes}")

    statements = read_jsonl(raw["statements"])
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or len(statements) != 15151:
        raise ValueError("Unexpected statement inventory.")
    targets = {
        SOURCE_STATEMENT_ID: ("cand-7520", None, P211_SEGMENT),
        GENEALOGY_STATEMENT_ID: ("cand-7489", None, P211_SEGMENT),
        DECREE_STATEMENT_ID: ("cand-7517", None, P211_SEGMENT),
        DOLCI_STATEMENT_ID: ("cand-7495", None, P211_SEGMENT),
        ADMIRERS_STATEMENT_ID: (None, None, P214_SEGMENT),
    }
    for statement_id, (subject, object_, segment_id) in targets.items():
        row = by_id.get(statement_id)
        if not row or (
            row.get("segment_id") != segment_id
            or row.get("subject_candidate_id") != subject
            or row.get("object_candidate_id") != object_
            or (row.get("qualifiers") or {}).get("relation_candidate") is not True
            or (row.get("qualifiers") or {}).get("open_endpoint_reason")
        ):
            raise ValueError(f"Reviewed statement precondition changed: {statement_id}")
    if statement_counts(statements) != (368, 46, 10395, 4756, 0):
        raise ValueError(f"Unexpected relation-endpoint state: {statement_counts(statements)}")

    mention_bom, mention_fields, mention_rows = csv_data(raw["mentions"])
    candidate_bom, candidate_fields, candidate_rows = csv_data(raw["candidates"])
    if mention_bom != candidate_bom:
        raise ValueError("CSV BOM state differs.")
    if len(mention_rows) != 26601 or len(candidate_rows) != 12391:
        raise ValueError("Unexpected mention or candidate inventory.")
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if any(cid in candidate_by_id for cid in (PROCEDURE_CANDIDATE_ID, EXHIBITION_CANDIDATE_ID)):
        raise ValueError("A planned candidate ID already exists.")
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows) or NEW_MENTION_IDS & set(mention_by_id):
        raise ValueError("Duplicate or pre-existing planned mention ID.")
    old_procedure_mention = mention_by_id.get(REASSIGN_MENTION_ID)
    if not old_procedure_mention or (
        old_procedure_mention.get("candidate_id") != "cand-7517"
        or old_procedure_mention.get("surface_form") != REASSIGN_SURFACE
        or (old_procedure_mention.get("start_char"), old_procedure_mention.get("end_char")) != ("991", "1068")
    ):
        raise ValueError("The existing Appalto mention changed from its reviewed precondition.")
    if NEW_STATEMENT_IDS & set(by_id):
        raise ValueError("A planned statement ID already exists.")

    # Separate the two principal source documents for the Del Rosso collection.
    principal = by_id[SOURCE_STATEMENT_ID]
    principal_original_quote = principal["original_quote"]
    account_phrase = "the account given of it in 1677 by Cinelli"
    inventory_phrase = (
        "the complete inventory drawn up twelve years later by Andrea del Rosso himself "
        "published in Gualandi, II, pp. 113-28"
    )
    if account_phrase not in principal_original_quote or inventory_phrase not in principal_original_quote:
        raise ValueError("The source-document statement no longer contains both reviewed sources.")
    common_source_text = "The main sources for the collection of the del Rosso brothers are "
    account = clone_statement(
        principal,
        SOURCE_STATEMENT_ID,
        "cand-7520",
        "cand-7499",
        "collection_documented_by_cinelli_account",
        "Haskell identifies Cinelli's 1677 account as one of the principal sources for the Del Rosso brothers' collection.",
        common_source_text + account_phrase,
        "Haskell names the account as a principal source; the account and its contents were not independently consulted.",
        "This records the source-level link from the brothers' picture collection to Cinelli's specifically dated account.",
        ["cand-7520", "cand-7489", "cand-7499", "cand-0765"],
        citations=[],
    )
    account_q = account["qualifiers"]
    account_q.pop("ocr_corrections", None)

    inventory = clone_statement(
        principal,
        "st-chp8-p211-andrea-inventory-principal-source",
        "cand-7520",
        "cand-7500",
        "collection_documented_by_andrea_del_rosso_inventory",
        "Haskell identifies Andrea del Rosso's complete inventory, drawn up twelve years after the 1677 account, as a principal source for the family collection.",
        common_source_text + account_phrase + " and " + inventory_phrase,
        "Haskell dates the inventory by its twelve-year interval after 1677 and cites Gualandi, volume II, pages 115-128; neither the inventory nor the cited pages were independently consulted.",
        "This records the collection's source-level link to the distinct Andrea del Rosso inventory; Gualandi is retained as its publication locator.",
        ["cand-7520", "cand-7489", "cand-7500", "cand-2275", "cand-7501"],
        citations=[{"source_candidate_id": "cand-7501", "volume": "II", "page_start": "115", "page_end": "128"}],
    )
    inventory["qualifiers"]["ocr_corrections"] = [
        item
        for item in principal.get("qualifiers", {}).get("ocr_corrections", [])
        if item.get("ocr") == "pp. 113-28"
    ]
    if len(inventory["qualifiers"]["ocr_corrections"]) != 2:
        raise ValueError("The p.211 page-image correction for Gualandi's locator changed.")

    # Separate the two cited manuscript locations for family information.
    genealogy = by_id[GENEALOGY_STATEMENT_ID]
    genealogy_quote = genealogy["original_quote"]
    marker = " There are also a number of references"
    if marker not in genealogy_quote:
        raise ValueError("The p.211 genealogy note no longer has its reviewed clause boundary.")
    first_genealogy_quote, second_genealogy_tail = genealogy_quote.split(marker, 1)
    second_genealogy_quote = "There are also a number of references" + second_genealogy_tail
    genealogy_primary = clone_statement(
        genealogy,
        GENEALOGY_STATEMENT_ID,
        "cand-7489",
        "cand-7502",
        "del_rosso_genealogical_information_in_passerini_manuscript",
        "Haskell locates general information and genealogies about the Del Rosso family in Passerini's manuscript collection, especially manuscript 19(25), at the Biblioteca Nazionale.",
        first_genealogy_quote,
        "This is Haskell's bibliographic report; Passerini 19(25) and the cited manuscript were not independently consulted, and the library branch remains unspecified.",
        "The source explicitly links family genealogical material to the identified Passerini manuscript; it does not establish details beyond the cited locator.",
        ["cand-7489", "cand-7502", "cand-7503", "cand-7518", "cand-7519"],
    )
    poligrafo = clone_statement(
        genealogy,
        "st-chp8-p211-poligrafo-gargano-family-references",
        "cand-7489",
        "cand-7504",
        "additional_del_rosso_references_in_poligrafo_gargano",
        "Haskell says further references about the Del Rosso family occur in the Poligrafo Gargano at the same library.",
        second_genealogy_quote,
        "The manuscript collection is a citation locator in Haskell's note, not independently consulted; the exact library branch is not specified.",
        "This records the separate manuscript-collection locator without identifying the individual references it contains.",
        ["cand-7489", "cand-7503", "cand-7504"],
    )

    # Distinguish the named revenue concession from its decree and archival copy.
    decree = by_id[DECREE_STATEMENT_ID]
    decree_quote = decree["original_quote"]
    archive_phrase = "is preserved in the Archivio di Stato—Miscellanea Medicea 533, Uffizio delle Farine"
    if archive_phrase not in decree_quote:
        raise ValueError("The p.211 decree's archival holding statement changed.")
    decree_grant_quote = decree_quote[: decree_quote.index(" is preserved in the Archivio di Stato")]
    decree_archive_quote = archive_phrase
    decree_grant = clone_statement(
        decree,
        DECREE_STATEMENT_ID,
        "cand-7517",
        PROCEDURE_CANDIDATE_ID,
        "decree_conferred_florentine_flour_revenue_concession",
        "Haskell says the decree granted the Appalto Generale of flour revenues for the City and Domain of Florence for nine years from 1 June 1676.",
        decree_grant_quote,
        "The grant is described in Haskell's footnote; the decree and concession were not independently consulted.",
        "This links the named decree to the separately represented revenue-concession procedure it confers.",
        ["cand-7517", PROCEDURE_CANDIDATE_ID, "cand-1041"],
    )
    decree_archive = clone_statement(
        decree,
        "st-chp8-p211-flour-decree-preserved-at-archive",
        "cand-7517",
        "cand-7509",
        "decree_copy_preserved_at_archivio_di_stato",
        "Haskell says a copy of the decree is preserved in Archivio di Stato, Miscellanea Medicea 533, Uffizio delle Farine.",
        decree_archive_quote,
        "The archive locator is transcribed from Haskell's note; the repository copy and file were not independently consulted.",
        "This records the stated repository for a copy of the specific decree; it does not claim independent archival verification.",
        ["cand-7517", "cand-7509"],
    )

    procedure_candidate = {
        "candidate_id": PROCEDURE_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Florentine flour-revenue concession (Appalto Generale; from 1 June 1676 for nine years)",
        "index_page_range": "",
        "suggested_type": "procedure",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell says the decree conferred the Appalto Generale of flour revenues for the City "
            "and Domain of Florence for nine years from 1 June 1676. This is the concession, distinct "
            "from the decree and its archival copy; the holder or contractor is not named in this note."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P211_SEGMENT}#L3",
    }
    decree_mention_phrase = (
        "the decree conferring the Appalto Generale della rendita della Farine della Città, "
        "e Dominio di Firenze for nine years as from 1 June 1676"
    )
    decree_mention_start, decree_mention_end = spans[decree_mention_phrase]
    decree_mention = {
        "mention_id": "m-chp8-p211-flour-decree-document",
        "segment_id": P211_SEGMENT,
        "candidate_id": "cand-7517",
        "surface_form": decree_mention_phrase,
        "start_char": str(decree_mention_start),
        "end_char": str(decree_mention_end),
        "note": "The decree is the archival document; the Appalto Generale it grants is mapped as a separate procedure.",
    }

    # Split the painting's reported location from its distinct 1960 exhibition event.
    dolci = by_id[DOLCI_STATEMENT_ID]
    dolci_quote = dolci["original_quote"]
    location_quote = "This picture, which is still at Burghley"
    exhibition_quote = "was exhibited in London in 1960"
    if location_quote not in dolci_quote or exhibition_quote not in dolci_quote:
        raise ValueError("The p.211 Dolci note no longer contains both reviewed claims.")
    dolci_exhibition = clone_statement(
        dolci,
        DOLCI_STATEMENT_ID,
        "cand-7495",
        EXHIBITION_CANDIDATE_ID,
        "dolci_picture_exhibited_at_london_event",
        "Haskell says the Carlo Dolci picture identified as Flight into Egypt was exhibited in London in 1960.",
        exhibition_quote,
        "The note names London and 1960 but gives no exhibition title in this sentence. Italian Art and Britain, page 24, is cited but was not independently consulted.",
        "This links the identified picture to a source-described exhibition event; its title and duration remain unspecified.",
        ["cand-7495", EXHIBITION_CANDIDATE_ID, "cand-1422", "cand-7256"],
        citations=[{"source_candidate_id": "cand-7256", "pages": ["24"]}],
        extra_qualifiers={"date": "1960"},
    )
    location = clone_statement(
        dolci,
        "st-chp8-p211-dolci-picture-at-burghley",
        "cand-7495",
        "cand-7237",
        "dolci_picture_reported_still_at_burghley",
        "Haskell reports that the Carlo Dolci Flight into Egypt picture was still at Burghley.",
        location_quote,
        "The word 'still' is relative to Haskell's report; the date represented by it is not specified. Baldinucci, volume VI (1728), page 500, is cited but was not independently consulted.",
        "This records the reported location of the picture without treating it as a verified present-day location.",
        ["cand-7495", "cand-7237", "cand-4846"],
        citations=[{"source_candidate_id": "cand-4846", "volume": "VI", "year": "1728", "pages": ["500"]}],
    )
    exhibition_event = {
        "candidate_id": EXHIBITION_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "London exhibition of Carlo Dolci's Flight into Egypt (1960; title not specified in p.211 note 3)",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Haskell reports this picture exhibited in London in 1960. The note does not give the "
            "event title or duration; it cites Italian Art and Britain, page 24, which was not "
            "independently consulted."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P211_SEGMENT}#L4",
    }
    exhibition_mention_phrase = "was exhibited in London in 1960"
    exhibition_start, exhibition_end = spans[exhibition_mention_phrase]
    exhibition_mention = {
        "mention_id": "m-chp8-p211-dolci-london-exhibition-event",
        "segment_id": P211_SEGMENT,
        "candidate_id": EXHIBITION_CANDIDATE_ID,
        "surface_form": exhibition_mention_phrase,
        "start_char": str(exhibition_start),
        "end_char": str(exhibition_end),
        "note": "The one-off exhibition occurrence described by Haskell; the note gives its city and year but no title.",
    }
    location_q = location["qualifiers"]
    location_q["ocr_corrections"] = [
        item
        for item in dolci.get("qualifiers", {}).get("ocr_corrections", [])
        if item.get("print") == "3 Baldinucci"
    ]

    exhibition_location = clone_statement(
        dolci,
        "st-chp8-p211-dolci-exhibition-held-in-london",
        EXHIBITION_CANDIDATE_ID,
        "cand-1422",
        "exhibition_held_in_london",
        "Haskell places the 1960 exhibition of the picture in London.",
        exhibition_quote,
        "The location and year are stated in Haskell's note; the cited exhibition catalogue was not independently consulted.",
        "This supplies the city endpoint for the source-described 1960 exhibition without equating the catalogue title with the event title.",
        [EXHIBITION_CANDIDATE_ID, "cand-1422", "cand-7495", "cand-7256"],
        citations=[{"source_candidate_id": "cand-7256", "pages": ["24"]}],
        extra_qualifiers={"date": "1960"},
    )

    # Split the two artists in the source's collective reception statement.
    admirers = by_id[ADMIRERS_STATEMENT_ID]
    admirers_quote = admirers["original_quote"]
    luca_admirers = clone_statement(
        admirers,
        ADMIRERS_STATEMENT_ID,
        "cand-1172",
        "cand-2719",
        "artist_had_admirers_in_city",
        "Haskell says Luca Giordano had a number of admirers in Venice.",
        admirers_quote,
        "This is Haskell's generalization. The following list names picture-owning families and officials but says they owned works by 'one or other' artist, so individual owners are not assigned to Giordano.",
        "This records the source-level claim about Giordano's reception in Venice; it does not assign any named owner to him.",
        ["cand-1172", "cand-2484", "cand-2719"],
    )
    solimena_admirers = clone_statement(
        admirers,
        "st-chp8-p214-solimena-admirers-in-venice",
        "cand-2484",
        "cand-2719",
        "artist_had_admirers_in_city",
        "Haskell says Francesco Solimena had a number of admirers in Venice.",
        admirers_quote,
        "This is Haskell's generalization. The following list names picture-owning families and officials but says they owned works by 'one or other' artist, so individual owners are not assigned to Solimena.",
        "This records the source-level claim about Solimena's reception in Venice; it does not assign any named owner to him.",
        ["cand-1172", "cand-2484", "cand-2719"],
    )

    updates = {
        SOURCE_STATEMENT_ID: account,
        GENEALOGY_STATEMENT_ID: genealogy_primary,
        DECREE_STATEMENT_ID: decree_grant,
        DOLCI_STATEMENT_ID: dolci_exhibition,
        ADMIRERS_STATEMENT_ID: luca_admirers,
    }
    additions = [inventory, poligrafo, decree_archive, location, exhibition_location, solimena_admirers]

    account_start, account_end = spans[account_phrase]
    inventory_start, inventory_end = spans[inventory_phrase.split(" published in Gualandi", 1)[0]]
    account_mention = {
        "mention_id": "m-chp8-p211-cinelli-account-document",
        "segment_id": P211_SEGMENT,
        "candidate_id": "cand-7499",
        "surface_form": account_phrase,
        "start_char": str(account_start),
        "end_char": str(account_end),
        "note": "The 1677 source document identified by Haskell as a principal source for the brothers' collection.",
    }
    inventory_mention = {
        "mention_id": "m-chp8-p211-andrea-inventory-document",
        "segment_id": P211_SEGMENT,
        "candidate_id": "cand-7500",
        "surface_form": inventory_phrase.split(" published in Gualandi", 1)[0],
        "start_char": str(inventory_start),
        "end_char": str(inventory_end),
        "note": "The complete inventory identified by Haskell as a principal source; Andrea del Rosso remains a nested author mention.",
    }

    mention_updates = {
        REASSIGN_MENTION_ID: {
            "candidate_id": PROCEDURE_CANDIDATE_ID,
            "note": "The named flour-revenue concession conferred by the separately recorded decree.",
        }
    }
    new_candidates = [procedure_candidate, exhibition_event]
    new_mentions = [
        account_mention,
        inventory_mention,
        decree_mention,
        exhibition_mention,
    ]
    statements_output = rewrite_jsonl(raw["statements"], updates, additions)
    mentions_output = patch_csv(raw["mentions"], "mention_id", mention_updates, new_mentions)
    candidates_output = patch_csv(raw["candidates"], "candidate_id", {}, new_candidates)

    after_statements = read_jsonl(statements_output)
    after_mentions = csv_data(mentions_output)[2]
    after_candidates = csv_data(candidates_output)[2]
    if len(after_statements) != 15157 or statement_counts(after_statements) != (363, 41, 10401, 4756, 0):
        raise ValueError(
            f"Unexpected post-edit statement state: rows={len(after_statements)}, counts={statement_counts(after_statements)}"
        )
    if len(after_mentions) != 26605 or len(after_candidates) != 12393:
        raise ValueError(
            f"Unexpected post-edit inventories: mentions={len(after_mentions)}, candidates={len(after_candidates)}"
        )
    mention_index = {row["mention_id"]: row for row in after_mentions}
    for mid in NEW_MENTION_IDS:
        if mid not in mention_index:
            raise ValueError(f"Expected new mention missing: {mid}")
    for row in new_mentions:
        if p211[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
            raise ValueError(f"New mention does not match its source span: {row['mention_id']}")
    if p211[int(old_procedure_mention["start_char"]):int(old_procedure_mention["end_char"])] != REASSIGN_SURFACE:
        raise ValueError("Reassigned concession mention no longer matches its source.")

    outputs = {
        STATEMENTS: statements_output,
        MENTIONS: mentions_output,
        CANDIDATES: candidates_output,
    }
    print("reviewed=CHP-8 p.211 notes 1-3 and p.214 note 4 against physical pages 9 and 12")
    print("change=split source documents, family manuscript locations, decree/concession/repository, picture location/exhibition, and artist reception")
    print("new_candidates=2 (revenue-concession procedure; 1960 London exhibition event)")
    print("new_mentions=4; reassigned_mentions=1; new_statements=6")
    print("open_endpoints=368->363; no_reason_open=46->41")
    for path, data in outputs.items():
        print(f"{path.name} sha256 {sha(path.read_bytes())}->{sha(data)}")
    if args.preview:
        return 0

    if {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    } != actual_hashes:
        raise ValueError("Apply requires the three input hashes printed by this preview.")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    temps = {path: path.with_name(path.name + TEMP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A recovery copy already exists; refusing to overwrite it.")
    if any(path.exists() for path in temps.values()):
        raise FileExistsError("A temporary table already exists; refusing to overwrite it.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in outputs.items():
            temps[path].write_bytes(data)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    print("applied=yes")
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.name}:{sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
