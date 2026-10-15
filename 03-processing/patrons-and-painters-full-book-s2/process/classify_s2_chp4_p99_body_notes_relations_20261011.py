#!/usr/bin/env python3
"""Classify the 24 p.99 S2 statements with a guarded, recoverable table write."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_REL = Path("02-sources/02-Markdown/04_CHP-4_sec_ii.md")
STATEMENTS_REL = Path("04-knowledge/tables/book-statements.jsonl")
CANDIDATES_REL = Path("04-knowledge/tables/entity-candidates.csv")
MENTIONS_REL = Path("04-knowledge/tables/mentions.csv")
BACKUP_TAG = "s2-chp4-p99-relations-20261011"

EXPECTED_SHA256 = {
    SOURCE_REL: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    STATEMENTS_REL: "867049839e018852e4ddec60fced23bee71aef65150ea26b0b30c4e17b261913",
    CANDIDATES_REL: "c1498faa3e0149760d9f0bd8612570657166fefbd4577656af595dc1d4a964f4",
    MENTIONS_REL: "d2ccd39af72a45317214ba936a1c43fbc8c91c0140b1765c6b6fd6db154617fb",
}

TARGET_IDS = {
    "st-chp4-sec-ii-l232-308-cassiano-admitted-to-lincei",
    "st-chp4-sec-ii-l232-308-cassiano-bought-cesi-books",
    "st-chp4-sec-ii-l232-308-cassiano-collected-natural-history-material",
    "st-chp4-sec-ii-l232-308-cassiano-scholar-reputation",
    "st-chp4-sec-ii-l232-308-cassiano-sponsored-scientific-publications",
    "st-chp4-sec-ii-l232-308-cesi-died-1630",
    "st-chp4-sec-ii-l232-308-cesi-identified-as-founder",
    "st-chp4-sec-ii-l232-308-clerical-patronage-and-church-conflict",
    "st-chp4-sec-ii-l232-308-fn99-carutti",
    "st-chp4-sec-ii-l232-308-fn99-gabrieli",
    "st-chp4-sec-ii-l232-308-fn99-lumbroso",
    "st-chp4-sec-ii-l232-308-fn99-lumbroso-letter-1617",
    "st-chp4-sec-ii-l232-308-fn99-naudaeana-citation",
    "st-chp4-sec-ii-l232-308-heresy-charges-and-attacks-left-lincei-firm",
    "st-chp4-sec-ii-l232-308-lincei-described-as-scientific-ancestor",
    "st-chp4-sec-ii-l232-308-lincei-disintegrated-after-cesi-death",
    "st-chp4-sec-ii-l232-308-lincei-membership-proposed-1621",
    "st-chp4-sec-ii-l232-308-lincei-membership-rule",
    "st-chp4-sec-ii-l232-308-lynx-metaphor-and-suppression",
    "st-chp4-sec-ii-l232-308-naudaeana-income",
    "st-chp4-sec-ii-l232-308-naudaeana-kinship-and-marital-status",
    "st-chp4-sec-ii-l232-308-naudaeana-natural-interests-and-scholars",
    "st-chp4-sec-ii-l232-308-naudaeana-place-and-age",
    "st-chp4-sec-ii-l232-308-new-scientific-method-and-participants",
}

TRUE_NOTES = {
    "st-chp4-sec-ii-l232-308-cassiano-admitted-to-lincei":
        "Haskell explicitly reports Cassiano's admission to the Accademia and his subsequent devotion of time to it; the relative date remains as stated.",
    "st-chp4-sec-ii-l232-308-cassiano-bought-cesi-books":
        "Haskell explicitly says Cassiano bought books and instruments belonging to Cesi; the possessive identifies prior ownership, not the object endpoint.",
    "st-chp4-sec-ii-l232-308-cassiano-collected-natural-history-material":
        "The source says Cassiano collected material relating to natural history; the endpoint is the stated field, not a specific collection or specimen.",
    "st-chp4-sec-ii-l232-308-cassiano-sponsored-scientific-publications":
        "Haskell explicitly attributes sponsorship of the listed scientific publications to Cassiano; titles and authors remain unspecified.",
    "st-chp4-sec-ii-l232-308-cesi-died-1630":
        "The source reports Cesi's death in 1630 and the statement points to the corresponding event candidate.",
    "st-chp4-sec-ii-l232-308-cesi-identified-as-founder":
        "The appositive explicitly identifies Federico Cesi as founder of the Accademia dei Lincei.",
    "st-chp4-sec-ii-l232-308-clerical-patronage-and-church-conflict":
        "This is Haskell's explicitly causal historical interpretation: the Lincei's stated research objective inevitably led to trouble with the Church; retain the author's qualification and do not treat it as independently verified.",
    "st-chp4-sec-ii-l232-308-fn99-carutti":
        "The footnote explicitly cites this bibliographic source from Haskell's book; the citation does not verify the cited content.",
    "st-chp4-sec-ii-l232-308-fn99-gabrieli":
        "The footnote explicitly cites this bibliographic source from Haskell's book; the cited page was not independently consulted.",
    "st-chp4-sec-ii-l232-308-fn99-lumbroso":
        "The footnote explicitly cites Lumbroso as a source from Haskell's book; the shorthand locator does not identify a title or page.",
    "st-chp4-sec-ii-l232-308-fn99-lumbroso-letter-1617":
        "The footnote explicitly cites the 27 August 1617 letter through the supplied Lumbroso locator; the cited material was not independently consulted.",
    "st-chp4-sec-ii-l232-308-fn99-naudaeana-citation":
        "The footnote explicitly cites Naudaeana et Patiniana from Haskell's book; this records the bibliographic link and does not verify the quoted comment.",
    "st-chp4-sec-ii-l232-308-heresy-charges-and-attacks-left-lincei-firm":
        "Haskell says the heresy charges and attacks on Galileo left the Lincei exposed but still firm; the unnamed actors and source attribution remain unresolved.",
    "st-chp4-sec-ii-l232-308-lincei-described-as-scientific-ancestor":
        "This records Haskell's comparison of the Lincei with the collective of European scientific societies; it does not establish formal institutional descent.",
    "st-chp4-sec-ii-l232-308-lincei-disintegrated-after-cesi-death":
        "The source places the Lincei's disintegration after Cesi's death; preserve temporal sequence without inferring that the death caused it.",
    "st-chp4-sec-ii-l232-308-lincei-membership-proposed-1621":
        "Haskell reports that the unnamed organisers proposed Cassiano for membership; the source's OCR reading and 1621 context are retained as qualifications.",
    "st-chp4-sec-ii-l232-308-lincei-membership-rule":
        "The passage explicitly attributes this membership eligibility rule to the Accademia; preserve its source and period scope.",
    "st-chp4-sec-ii-l232-308-lynx-metaphor-and-suppression":
        "This is Haskell's source-bounded account of the Lincei's scientific outlook in seventeenth-century Rome; retain the lynx metaphor and do not infer named suppressors.",
    "st-chp4-sec-ii-l232-308-naudaeana-kinship-and-marital-status":
        "The quoted comment explicitly calls Cassiano a nephew of an Archbishop of Pisa; the Archbishop's identity and the phrase 'bore this name' remain unresolved.",
    "st-chp4-sec-ii-l232-308-naudaeana-natural-interests-and-scholars":
        "The French comment says Cassiano maintained dealings with several learned people; here commerce means contact, not proven trade, and the people remain unnamed.",
    "st-chp4-sec-ii-l232-308-naudaeana-place-and-age":
        "The quoted comment says Cassiano lived in Rome; the claim remains attributed to that comment and is not independently verified.",
    "st-chp4-sec-ii-l232-308-new-scientific-method-and-participants":
        "Haskell says the new organisation of scientific thought and experiment left a deep mark on the unnamed young participants; the group remains open.",
}

FALSE_NOTES = {
    "st-chp4-sec-ii-l232-308-cassiano-scholar-reputation":
        "This is a scalar claim about Cassiano's reputation and writing, not a relation between two entities.",
    "st-chp4-sec-ii-l232-308-naudaeana-income":
        "This is a scalar income estimate attributed to the quoted comment, not a relation between two entities; it is not independent verification.",
}

CITATIONS = {
    "st-chp4-sec-ii-l232-308-fn99-gabrieli": (1, "Giuseppe Gabrieli, 1941, Parte seconda, sezione seconda, p. 736"),
    "st-chp4-sec-ii-l232-308-fn99-lumbroso": (2, "Lumbroso: passim"),
    "st-chp4-sec-ii-l232-308-fn99-carutti": (3, "Carutti, 1883"),
    "st-chp4-sec-ii-l232-308-fn99-lumbroso-letter-1617": (4, "Lumbroso, p. 137—Letter of 27 August 1617"),
    # The OCR label is 6, while the scan shows printed marker 5; the existing note preserves that distinction.
    "st-chp4-sec-ii-l232-308-fn99-naudaeana-citation": (5, "Naudaeana et Patiniana, Amsterdam 1703, p. 29"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, newline


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    if not rows:
        raise ValueError(f"CSV has no data rows: {path}")
    fieldnames = list(rows[0].keys())
    return rows, fieldnames, newline, has_bom


def csv_bytes(rows: list[dict[str, str]], fieldnames: list[str], newline: str, has_bom: bool) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fieldnames, extrasaction="raise", lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    data = out.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if has_bom else data


def jsonl_bytes(rows: list[dict], newline: str) -> bytes:
    return (newline.join(json.dumps(row, ensure_ascii=False) for row in rows) + newline).encode("utf-8")


def append_unique(values: list[str], value: str) -> list[str]:
    result = list(values)
    if value not in result:
        result.append(value)
    return result


def set_flags(record: dict, is_relation: bool, note: str) -> None:
    qualifiers = record.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = is_relation
    qualifiers["relation_candidate_note"] = note


def new_scalar(statement_id: str, predicate: str, quote: str, claim: str, qualification: str) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-2036",
        "object_candidate_id": None,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": 238,
            "source_line_end": 238,
            "claim": claim,
            "speaker": "Unidentified comment quoted in Naudaeana et Patiniana as cited by Haskell",
            "text_layer": "French quotation in substantive footnote",
            "pdf_physical_page": 6,
            "printed_page_locator": "p.99",
            "mentioned_candidate_ids": ["cand-2036", "cand-5650"],
            "qualification": qualification,
            "relation_candidate": False,
            "relation_candidate_note": "This is a scalar description of Cassiano attributed to the quoted comment, not a relation between two entities.",
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL.as_posix(),
    }


def new_candidate(candidate_id: str, canonical_name: str, detail: str, line: int) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": canonical_name,
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


def new_mention(mention_id: str, candidate_id: str, surface: str, start: int, end: int, note: str) -> dict[str, str]:
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    }


def insert_after(rows: list[dict], anchor_id: str, additions: list[dict], id_key: str) -> list[dict]:
    out = []
    found = False
    for row in rows:
        out.append(row)
        if row[id_key] == anchor_id:
            out.extend(additions)
            found = True
    if not found:
        raise ValueError(f"Insertion anchor not found: {anchor_id}")
    return out


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the prevalidated S2 edits; default is dry-run")
    args = parser.parse_args()

    if not (ROOT / ".agents" / "pipeline.md").exists():
        raise SystemExit(f"Run from the repository checkout; resolved root={ROOT}")
    paths = {rel: ROOT / rel for rel in EXPECTED_SHA256}
    for rel, expected in EXPECTED_SHA256.items():
        actual = sha256(paths[rel].read_bytes())
        if actual != expected:
            raise SystemExit(f"Precondition hash mismatch for {rel}: expected {expected}, found {actual}")

    source_bytes = paths[SOURCE_REL].read_bytes()
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    if len(source_lines) < 308:
        raise SystemExit("Source does not contain the expected lines through L308")
    segment_text = "\n".join(source_lines[231:308])
    segments = [json.loads(line) for line in (ROOT / "04-knowledge/tables/segments.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    segment = next((x for x in segments if x.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e":
        raise SystemExit("The target S0 segment hash changed")

    statements, statements_newline = read_jsonl(paths[STATEMENTS_REL])
    candidates, candidate_fields, candidate_newline, candidate_bom = read_csv(paths[CANDIDATES_REL])
    mentions, mention_fields, mention_newline, mention_bom = read_csv(paths[MENTIONS_REL])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}

    p99 = {
        row["statement_id"]
        for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("printed_page_locator") == "p.99"
    }
    if p99 != TARGET_IDS:
        raise SystemExit(f"The p.99 target set changed: expected {len(TARGET_IDS)}, found {len(p99)}")
    for statement_id in TARGET_IDS:
        if statement_by_id[statement_id].get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"Target is no longer unclassified: {statement_id}")

    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11677:
        raise SystemExit("Candidate sequence changed; review IDs before applying")
    for candidate_id in ("cand-11678", "cand-11679", "cand-11680"):
        if candidate_id in candidate_by_id:
            raise SystemExit(f"New candidate ID already exists: {candidate_id}")

    additions = [
        new_scalar(
            "st-chp4-sec-ii-l232-308-naudaeana-piedmontese-gentleman",
            "described_as_piedmontese_gentleman",
            "Chevalier Piemontois",
            "The quoted comment describes Cassiano as a Piedmontese gentleman.",
            "This is the comment's description of Cassiano; it does not establish a separate relationship with a Piedmontese entity.",
        ),
        new_scalar(
            "st-chp4-sec-ii-l232-308-naudaeana-natural-knowledge",
            "described_as_well_versed_in_natural_things",
            "est fort versé aux choses naturelles",
            "The quoted comment says Cassiano was well versed in natural things.",
            "Keep the French wording broad; do not infer a specific scientific discipline.",
        ),
        new_scalar(
            "st-chp4-sec-ii-l232-308-naudaeana-foreign-animals",
            "kept_many_foreign_animals",
            "il nourrit quantité d’animaux étrangers",
            "The quoted comment says Cassiano kept many foreign animals.",
            "The source does not identify species or individual animals; no animal-group candidate is created.",
        ),
        new_scalar(
            "st-chp4-sec-ii-l232-308-naudaeana-unmarried",
            "reported_unmarried",
            "il n’est point marie",
            "The quoted comment says Cassiano was unmarried at the time of its description.",
            "This remains a time-bounded statement from an unidentified comment; no broader marital history is inferred.",
        ),
        new_scalar(
            "st-chp4-sec-ii-l232-308-naudaeana-age-1636",
            "age_48_in_1636",
            "age de quarante huit ans [in 1636]",
            "The quoted description gives Cassiano's age as forty-eight in 1636.",
            "The bracketed year is retained as supplied in the source transcription; no birth year is calculated.",
        ),
    ]
    for row in additions:
        if row["statement_id"] in statement_by_id:
            raise SystemExit(f"New statement ID already exists: {row['statement_id']}")
        if row["original_quote"] not in segment_text:
            raise SystemExit(f"New quote is not an exact source substring: {row['statement_id']}")

    new_candidates = [
        new_candidate(
            "cand-11678",
            "European scientific societies collectively compared with the Accademia dei Lincei by Haskell",
            "Haskell calls the Lincei an ancestor of all European scientific societies. This group candidate records his comparison only; no members are listed and formal institutional genealogy is not independently established.",
            233,
        ),
        new_candidate(
            "cand-11679",
            "Unspecified books and scientific instruments from Federico Cesi's collection acquired by Cassiano",
            "Haskell says Cassiano bought a large number of Cesi's books and scientific instruments after Cesi's death. The titles, individual instruments, exact quantity, and transfer details are not supplied.",
            233,
        ),
        new_candidate(
            "cand-11680",
            "Several unnamed learned people mentioned in the quoted comment on Cassiano",
            "The French comment says Cassiano maintained commerce or contact with several savants. Their identities and exact number are not supplied; the phrase is not treated as evidence of commercial trade.",
            238,
        ),
    ]

    new_mentions = [
        new_mention(
            "m-chp4-sec-ii-p99body-0035", "cand-0003", "the recently created ancestor", 58, 87,
            "Appositive description of the Accademia dei Lincei in Haskell's comparison.",
        ),
        new_mention(
            "m-chp4-sec-ii-p99body-0036", "cand-11678", "all European scientific societies", 91, 124,
            "Collective comparison target; no constituent societies are identified.",
        ),
        new_mention(
            "m-chp4-sec-ii-p99body-0037", "cand-11679", "books and scientific instruments", 354, 386,
            "Unspecified mixed group of items that Haskell says Cassiano bought from Cesi's collection.",
        ),
        new_mention(
            "m-chp4-sec-ii-p99note-0012", "cand-11680", "plusieurs Savans", 2007, 2023,
            "Several unnamed learned people in the French comment; identities and exact number are not supplied.",
        ),
    ]
    for row in new_mentions:
        if row["mention_id"] in mention_by_id:
            raise SystemExit(f"New mention ID already exists: {row['mention_id']}")
        if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
            raise SystemExit(f"Mention span does not match source: {row['mention_id']}")

    # Classify all 24 original statements, then correct the endpoints and atomize composite claims.
    for statement_id, note in TRUE_NOTES.items():
        record = statement_by_id[statement_id]
        set_flags(record, True, note)
    for statement_id, note in FALSE_NOTES.items():
        set_flags(statement_by_id[statement_id], False, note)

    income = statement_by_id["st-chp4-sec-ii-l232-308-naudaeana-income"]
    income["subject_candidate_id"] = "cand-2036"
    income["object_candidate_id"] = None

    book_candidate_id = "cand-2962"
    for statement_id, (marker, locator) in CITATIONS.items():
        record = statement_by_id[statement_id]
        target_id = record.get("object_candidate_id")
        if not target_id or target_id not in candidate_by_id:
            raise SystemExit(f"Citation target missing for {statement_id}")
        record["subject_candidate_id"] = book_candidate_id
        record["predicate"] = "cites"
        q = record["qualifiers"]
        q["claim"] = f"Haskell's book cites {candidate_by_id[target_id]['canonical_name']} in this footnote."
        q["speaker"] = "Haskell footnote"
        q["text_layer"] = "bibliographic citation"
        q["qualification"] = "This records a bibliographic reference only. The cited material was not independently consulted and the citation is not treated as verification of adjacent claims."
        q["mentioned_candidate_ids"] = append_unique(q.get("mentioned_candidate_ids", []), book_candidate_id)
        q["mentioned_candidate_ids"] = append_unique(q["mentioned_candidate_ids"], target_id)
        q["footnote_marker"] = marker
        q["citation_locator"] = locator
        q["cited_material_not_independently_consulted"] = True

    # Correct object boundaries and split the source's composite French descriptions.
    books = statement_by_id["st-chp4-sec-ii-l232-308-cassiano-bought-cesi-books"]
    books["object_candidate_id"] = "cand-11679"
    books["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-0641", "cand-11679", "cand-5641"]

    ancestor = statement_by_id["st-chp4-sec-ii-l232-308-lincei-described-as-scientific-ancestor"]
    ancestor["object_candidate_id"] = "cand-11678"
    ancestor["qualifiers"]["mentioned_candidate_ids"] = ["cand-0003", "cand-11678"]

    kinship = statement_by_id["st-chp4-sec-ii-l232-308-naudaeana-kinship-and-marital-status"]
    kinship["subject_candidate_id"] = "cand-2036"
    kinship["object_candidate_id"] = "cand-5651"
    kinship["predicate"] = "nephew_of"
    kinship["original_quote"] = "est neveu d’un Àrcheveque de Pise"
    kinship["qualifiers"]["claim"] = "The unidentified quoted comment calls Cassiano a nephew of an Archbishop of Pisa who 'bore this name'."
    kinship["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-5651", "cand-5650"]
    kinship["qualifiers"]["qualification"] = "The antecedent of 'ce nom' is unclear; the Archbishop remains distinct from the p.98 candidate, and this quoted claim is not independently verified. Marital status is recorded separately."

    contacts = statement_by_id["st-chp4-sec-ii-l232-308-naudaeana-natural-interests-and-scholars"]
    contacts["subject_candidate_id"] = "cand-2036"
    contacts["object_candidate_id"] = "cand-11680"
    contacts["predicate"] = "contacts_with_unnamed_scholars_reported"
    contacts["original_quote"] = "entretient commerce avec plusieurs Savans."
    contacts["qualifiers"]["claim"] = "The quoted comment says Cassiano maintained contact with several learned people."
    contacts["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-11680", "cand-5650"]
    contacts["qualifiers"]["qualification"] = "In this context the French 'commerce' is retained as contact or dealings, not inferred commercial trade. The individual scholars and exact number are unknown; the statement belongs to an unidentified comment quoted by Haskell."

    residence = statement_by_id["st-chp4-sec-ii-l232-308-naudaeana-place-and-age"]
    residence["subject_candidate_id"] = "cand-2036"
    residence["object_candidate_id"] = "cand-4490"
    residence["predicate"] = "resided_in"
    residence["original_quote"] = "qui demeure à Rome"
    residence["qualifiers"]["claim"] = "The unidentified quoted comment says Cassiano lived in Rome."
    residence["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-4490", "cand-5650"]
    residence["qualifiers"]["qualification"] = "The residence is attributed to the quoted comment; no dates beyond the source context are inferred."

    # Separate the possessive from the acquired objects; preserve both source-grounded mentions.
    possessive = mention_by_id["m-chp4-sec-ii-p99body-0011"]
    possessive.update({
        "candidate_id": "cand-0641",
        "surface_form": "his",
        "start_char": "350",
        "end_char": "353",
        "note": "Possessive pronoun refers to Federico Cesi; the following nouns are separately mapped as the objects of Cassiano's purchase.",
    })

    # Insert five scalar statements beside their source clauses in the JSONL order.
    scalar_by_id = {row["statement_id"]: row for row in additions}
    before = {
        "st-chp4-sec-ii-l232-308-naudaeana-natural-interests-and-scholars": [
            scalar_by_id["st-chp4-sec-ii-l232-308-naudaeana-natural-knowledge"],
            scalar_by_id["st-chp4-sec-ii-l232-308-naudaeana-foreign-animals"],
        ],
        "st-chp4-sec-ii-l232-308-naudaeana-place-and-age": [
            scalar_by_id["st-chp4-sec-ii-l232-308-naudaeana-piedmontese-gentleman"],
        ],
    }
    after = {
        "st-chp4-sec-ii-l232-308-naudaeana-kinship-and-marital-status": [
            scalar_by_id["st-chp4-sec-ii-l232-308-naudaeana-unmarried"],
        ],
        "st-chp4-sec-ii-l232-308-naudaeana-place-and-age": [
            scalar_by_id["st-chp4-sec-ii-l232-308-naudaeana-age-1636"],
        ],
    }
    out_statements = []
    for row in statements:
        out_statements.extend(before.get(row["statement_id"], []))
        out_statements.append(row)
        out_statements.extend(after.get(row["statement_id"], []))
    if len(out_statements) != len(statements) + 5:
        raise SystemExit("Unexpected statement output count")

    out_candidates = candidates + new_candidates
    out_mentions = mentions
    out_mentions = insert_after(out_mentions, "m-chp4-sec-ii-p99body-0034", new_mentions[:3], "mention_id")
    out_mentions = insert_after(out_mentions, "m-chp4-sec-ii-p99note-0011", new_mentions[3:], "mention_id")

    # Validate all external IDs and statement classification totals before touching disk.
    valid_candidate_ids = {row["candidate_id"] for row in out_candidates}
    for row in out_statements:
        if row.get("segment_id") == SEGMENT_ID:
            for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
                if endpoint and endpoint not in valid_candidate_ids:
                    raise SystemExit(f"Unknown candidate endpoint in {row['statement_id']}: {endpoint}")
    out_p99 = [row for row in out_statements if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("printed_page_locator") == "p.99"]
    if len(out_p99) != 29 or any(row.get("qualifiers", {}).get("relation_candidate") is None for row in out_p99):
        raise SystemExit(f"Post-plan p.99 state invalid: rows={len(out_p99)}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in out_p99) != 22:
        raise SystemExit("Post-plan p.99 relation-candidate total is not 22")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in out_p99) != 7:
        raise SystemExit("Post-plan p.99 non-relation total is not 7")
    for row in out_p99:
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is True:
            endpoints = (row.get("subject_candidate_id"), row.get("object_candidate_id"))
            if not all(endpoints):
                raise SystemExit(f"p.99 relation candidate has an open endpoint: {row['statement_id']}")
            if not set(endpoints).issubset(set(q.get("mentioned_candidate_ids", []))):
                raise SystemExit(f"p.99 relation endpoint is absent from mentioned_candidate_ids: {row['statement_id']}")

    proposed = {
        STATEMENTS_REL: jsonl_bytes(out_statements, statements_newline),
        CANDIDATES_REL: csv_bytes(out_candidates, candidate_fields, candidate_newline, candidate_bom),
        MENTIONS_REL: csv_bytes(out_mentions, mention_fields, mention_newline, mention_bom),
    }
    print("PREVIEW: p99 output statements=29; relation candidates=22; non-relations=7 (24 existing plus 5 new scalar statements)")
    print("PREVIEW: new candidates=3; new mentions=4; source/S0 unchanged; formal S6 relations=0")
    for row in out_p99:
        q = row.get("qualifiers", {})
        print(
            "REVIEW: "
            + row["statement_id"]
            + f" | relation_candidate={q.get('relation_candidate')}"
            + f" | {row.get('predicate')} | {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')}"
            + f" | {row.get('original_quote', '')[:100]}"
        )
    for rel, data in proposed.items():
        print(f"PREVIEW: {rel.as_posix()} {sha256(paths[rel].read_bytes())} -> {sha256(data)} bytes={len(data)}")
    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply to write the prevalidated changes.")
        return 0

    backups = []
    for rel in (STATEMENTS_REL, CANDIDATES_REL, MENTIONS_REL):
        path = paths[rel]
        backup = path.with_name(path.name + ".bak-" + BACKUP_TAG)
        if backup.exists():
            raise SystemExit(f"Backup already exists; refusing to overwrite: {backup}")
        with backup.open("xb") as stream:
            stream.write(path.read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
        backups.append(backup)
    for rel, data in proposed.items():
        atomic_write(paths[rel], data)
    for rel, backup in zip((STATEMENTS_REL, CANDIDATES_REL, MENTIONS_REL), backups):
        print(f"BACKUP: {backup.relative_to(ROOT).as_posix()} sha256={sha256(backup.read_bytes())}")
        print(f"WRITTEN: {rel.as_posix()} sha256={sha256(paths[rel].read_bytes())}")
    print("APPLY COMPLETE. Source file was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
