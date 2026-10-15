from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
PDF = "02-sources/01-book/CHP-4.pdf"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
PAGE_IMAGE = (
    "03-processing/patrons-and-painters-full-book-s2/process/"
    "p114_body_notes_page_review_20261011.png"
)
PAGE_IMAGE_SHA256 = "02486c67f70b3af3ec8662cdb0ae74638e50fc5b9bdc1018b76d7293d0feb0f6"
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
}
EXPECTED_TABLE_SHA256 = {
    "statements": "ce9f99372f4b941a3e9771ed186f09d545ddede681e0e8e9af9517c4213be936",
    "candidates": "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    "mentions": "01b0dbe6ab585430923576913ca45d81185ef5f8cad8c744e979d67a0c87fb4e",
}
BACKUP_SUFFIX = ".bak-s2-chp4-p114-notes-20261011"

OLD_STATEMENTS = {
    "st-chp4-sec-ii-notes-p114-fn1": ("cand-0107", "cites_references_to_angeloni", "cand-4634"),
    "st-chp4-sec-ii-notes-p114-fn2-confusion": (
        "cand-5938",
        "possibly_confused_with_original",
        "cand-5939",
    ),
    "st-chp4-sec-ii-notes-p114-fn2-killed": (
        "cand-5792",
        "possible_version_at_national_gallery",
        "cand-5938",
    ),
    "st-chp4-sec-ii-notes-p114-fn2-phocion": (
        "cand-5792",
        "version_in_lord_plymouth_collection",
        "cand-5937",
    ),
    "st-chp4-sec-ii-notes-p114-fn2-woman": (
        "cand-5792",
        "version_associated_with_ottawa",
        "cand-5936",
    ),
}
NOTE1 = (
    "1 There are frequent references to Angeloni by Cassiano himself "
    "(Lumbroso, p. 200), Poussin (Correspondance—passim) and other contemporaries. "
    "See Mahon, 1947, pp. 144 if., and also later Chapter 6."
)
NOTE2 = (
    "2 See Sheila Rinehart in Actes, 1961, pp. 19-30. The pictures are versions of the "
    "Landscape with Woman washing her Feet (Ottawa), Funeral ofPhocion "
    "(collection of Lord Plymouth), and possibly of the Landscape with Man killed by "
    "Serpent (National Gallery, London), though this has perhaps been confused with "
    "the (original) Landscape with Man fleeing from Serpent (Montreal)."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    return raw, bom, text, rows


def write_csv_bytes(headers, rows, bom: bool, text: str) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=headers,
        lineterminator="\r\n" if "\r\n" in text else "\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(rows)
    encoded = output.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + encoded


def statement(
    statement_id: str,
    subject: str | None,
    predicate: str,
    object_: str | None,
    *,
    line: int,
    marker: int,
    claim: str,
    quote: str,
    mentioned: list[str],
    relation: bool,
    relation_note: str,
    qualification: str | None = None,
    extra: dict | None = None,
) -> dict:
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "pdf_physical_page": 25,
        "printed_page_locator": f"p.114 footnote {marker}",
        "claim": claim,
        "speaker": "Haskell’s footnote",
        "text_layer": "reported historical claim" if relation else "internal cross-reference",
        "footnote_marker": marker,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": relation_note,
    }
    if qualification:
        qualifiers["qualification"] = qualification
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE,
    }


def preflight() -> tuple[list[dict], list[dict], list[dict], dict[str, bytes]]:
    checks = {
        SOURCE: SOURCE_SHA256,
        PDF: PDF_SHA256,
        PAGE_IMAGE: PAGE_IMAGE_SHA256,
    }
    for rel, expected in checks.items():
        actual = sha256((ROOT / rel).read_bytes())
        if actual != expected:
            raise SystemExit(f"STOP: {rel} SHA-256 changed: {actual}")

    source_lines = (ROOT / SOURCE).read_text(encoding="utf-8").splitlines()
    segment = "\n".join(source_lines[231:308])
    if sha256(segment.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("STOP: canonical source segment hash changed")
    if source_lines[290] != NOTE1 or source_lines[291] != NOTE2:
        raise SystemExit("STOP: printed p.114 footnote transcript changed")
    offsets = {
        "other contemporaries": (9783, 9803),
        "The pictures": (9910, 9922),
        "Actes, 1961, pp. 19-30": (9886, 9908),
    }
    for surface, (start, end) in offsets.items():
        if segment[start:end] != surface:
            raise SystemExit(f"STOP: source offset mismatch for {surface!r}")

    raw: dict[str, bytes] = {}
    for name, path in TABLES.items():
        raw[name] = path.read_bytes()
        actual = sha256(raw[name])
        if actual != EXPECTED_TABLE_SHA256[name]:
            raise SystemExit(f"STOP: {name} table SHA-256 changed: {actual}")

    statements = [json.loads(line) for line in raw["statements"].decode("utf-8").splitlines()]
    by_statement = {row["statement_id"]: row for row in statements}
    if len(by_statement) != len(statements):
        raise SystemExit("STOP: duplicate statement_id in source table")
    for statement_id, expected in OLD_STATEMENTS.items():
        row = by_statement.get(statement_id)
        if row is None:
            raise SystemExit(f"STOP: missing expected statement {statement_id}")
        actual = (
            row.get("subject_candidate_id"),
            row.get("predicate"),
            row.get("object_candidate_id"),
        )
        if actual != expected or "relation_candidate" in row.get("qualifiers", {}):
            raise SystemExit(f"STOP: old statement changed before review: {statement_id}: {actual}")
        if row.get("segment_id") != SEGMENT_ID:
            raise SystemExit(f"STOP: wrong source segment for {statement_id}")

    _, candidate_bom, candidate_text, candidates = read_csv(TABLES["candidates"])
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(candidate_by_id) != len(candidates):
        raise SystemExit("STOP: duplicate candidate_id in candidate table")
    expected_candidates = {
        "cand-2962": "archive",
        "cand-0107": "person",
        "cand-2036": "person",
        "cand-1984": "person",
        "cand-5626": "person",
        "cand-5683": "archive",
        "cand-4634": "archive",
        "cand-4371": "archive",
        "cand-1494": "person",
        "cand-5792": "archive",
        "cand-5793": "person",
        "cand-5935": "work",
        "cand-5936": "work",
        "cand-5937": "work",
        "cand-5938": "work",
        "cand-5939": "work",
        "cand-5940": "place",
        "cand-5941": "person",
        "cand-5942": "",
        "cand-5943": "institution",
        "cand-5944": "place",
        "cand-11428": "archive",
    }
    for candidate_id, candidate_type in expected_candidates.items():
        row = candidate_by_id.get(candidate_id)
        if row is None or row["suggested_type"] != candidate_type:
            raise SystemExit(f"STOP: candidate/type mismatch: {candidate_id}")
    if "Italian Studies" not in candidate_by_id["cand-5792"]["canonical_name"]:
        raise SystemExit("STOP: cand-5792 is no longer the separate Italian Studies item")
    if "Actes du Colloque Poussin" not in candidate_by_id["cand-11428"]["canonical_name"]:
        raise SystemExit("STOP: cand-11428 is no longer the Actes publication")
    if candidate_by_id["cand-11428"]["candidate_source_ref"] != (
        "chp-21:21_CHP-21Bibliography:l1022-1057#L1046"
    ):
        raise SystemExit("STOP: cand-11428 bibliography provenance changed")

    _, mention_bom, mention_text, mentions = read_csv(TABLES["mentions"])
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(mention_by_id) != len(mentions):
        raise SystemExit("STOP: duplicate mention_id in mention table")
    p114_mentions = {
        row["mention_id"]: row
        for row in mentions
        if row["segment_id"] == SEGMENT_ID
        and row["mention_id"].startswith("m-chp4-sec-ii-notes-p114-")
    }
    if len(p114_mentions) != 19:
        raise SystemExit(f"STOP: expected 19 existing p.114 note mentions, got {len(p114_mentions)}")
    expected_existing_mentions = {
        "m-chp4-sec-ii-notes-p114-0054": ("cand-5793", "Sheila Rinehart", 9867, 9882),
        "m-chp4-sec-ii-notes-p114-0055": ("cand-5792", "Actes, 1961, pp. 19-30", 9886, 9908),
        "m-chp4-sec-ii-notes-p114-0056": ("cand-0107", "Angeloni", 9698, 9706),
        "m-chp4-sec-ii-notes-p114-0057": ("cand-2036", "Cassiano", 9710, 9718),
        "m-chp4-sec-ii-notes-p114-0058": ("cand-5626", "Lumbroso", 9728, 9736),
        "m-chp4-sec-ii-notes-p114-0059": ("cand-5683", "p. 200", 9738, 9744),
        "m-chp4-sec-ii-notes-p114-0060": ("cand-1984", "Poussin", 9747, 9754),
        "m-chp4-sec-ii-notes-p114-0061": ("cand-4634", "Correspondance—passim", 9756, 9777),
        "m-chp4-sec-ii-notes-p114-0062": ("cand-4371", "Mahon, 1947, pp. 144 if.", 9809, 9833),
        "m-chp4-sec-ii-notes-p114-0044": ("cand-5936", "Landscape with Woman washing her Feet", 9943, 9980),
        "m-chp4-sec-ii-notes-p114-0045": ("cand-5940", "Ottawa", 9982, 9988),
        "m-chp4-sec-ii-notes-p114-0046": ("cand-5937", "Funeral ofPhocion", 9991, 10008),
        "m-chp4-sec-ii-notes-p114-0047": ("cand-5941", "Lord Plymouth", 10024, 10037),
        "m-chp4-sec-ii-notes-p114-0048": ("cand-5942", "collection of Lord Plymouth", 10010, 10037),
        "m-chp4-sec-ii-notes-p114-0049": ("cand-5938", "Landscape with Man killed by Serpent", 10060, 10096),
        "m-chp4-sec-ii-notes-p114-0050": ("cand-5943", "National Gallery, London", 10098, 10122),
        "m-chp4-sec-ii-notes-p114-0051": ("cand-1422", "London", 10116, 10122),
        "m-chp4-sec-ii-notes-p114-0052": ("cand-5939", "Landscape with Man fleeing from Serpent", 10183, 10222),
        "m-chp4-sec-ii-notes-p114-0053": ("cand-5944", "Montreal", 10224, 10232),
    }
    for mention_id, expected in expected_existing_mentions.items():
        row = p114_mentions.get(mention_id)
        if row is None:
            raise SystemExit(f"STOP: missing mention {mention_id}")
        actual = (
            row["candidate_id"],
            row["surface_form"],
            int(row["start_char"]),
            int(row["end_char"]),
        )
        if actual != expected or segment[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
            raise SystemExit(f"STOP: mention span or mapping changed: {mention_id}: {actual}")

    new_statement_ids = {
        "st-chp4-sec-ii-notes-p114-fn1-poussin",
        "st-chp4-sec-ii-notes-p114-fn1-contemporaries",
        "st-chp4-sec-ii-notes-p114-fn1-cite-lumbroso",
        "st-chp4-sec-ii-notes-p114-fn1-cite-correspondance",
        "st-chp4-sec-ii-notes-p114-fn1-cite-mahon",
        "st-chp4-sec-ii-notes-p114-fn1-chapter6",
        "st-chp4-sec-ii-notes-p114-fn2-cite-rinehart-actes",
    }
    if new_statement_ids & by_statement.keys():
        raise SystemExit("STOP: one or more planned statement IDs already exist")
    if "cand-11681" in candidate_by_id:
        raise SystemExit("STOP: planned candidate cand-11681 already exists")
    planned_mention_ids = {
        "m-chp4-sec-ii-notes-p114-0063",
        "m-chp4-sec-ii-notes-p114-0064",
    }
    if planned_mention_ids & mention_by_id.keys():
        raise SystemExit("STOP: one or more planned mention IDs already exist")

    candidate_headers = list(candidates[0])
    candidates.append(
        {
            "candidate_id": "cand-11681",
            "index_entry_id": "",
            "canonical_name": "Other contemporaries reported to have referred to Angeloni (members unspecified)",
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": (
                "Haskell reports references to Angeloni by other contemporaries without naming "
                "them; member identities and group size are unspecified."
            ),
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L291",
        }
    )
    if list(candidates[0]) != candidate_headers:
        raise SystemExit("STOP: candidate schema changed unexpectedly")

    for row in statements:
        if row["statement_id"] == "st-chp4-sec-ii-notes-p114-fn1":
            row.update(
                subject_candidate_id="cand-2036",
                object_candidate_id="cand-0107",
                predicate="referred_to",
                qualifiers={
                    "source_line_start": 291,
                    "source_line_end": 291,
                    "pdf_physical_page": 25,
                    "printed_page_locator": "p.114 footnote 1",
                    "claim": "Haskell reports frequent references to Angeloni by Cassiano himself.",
                    "speaker": "Haskell’s footnote",
                    "text_layer": "reported historical claim",
                    "footnote_marker": 1,
                    "mentioned_candidate_ids": ["cand-2036", "cand-0107", "cand-5683"],
                    "citation_source_candidate_id": "cand-5683",
                    "citation_locator": "Lumbroso, p. 200",
                    "supporting_citation_statement_id": "st-chp4-sec-ii-notes-p114-fn1-cite-lumbroso",
                    "relation_candidate": True,
                    "relation_candidate_note": (
                        "Explicitly reported reference by Cassiano to Angeloni; retained as an S2 "
                        "candidate, without creating a formal S6 relation."
                    ),
                    "qualification": "Haskell’s report is source-attributed; Lumbroso p. 200 is a locator, not an independently consulted source.",
                },
                original_quote=NOTE1,
            )
        elif row["statement_id"] == "st-chp4-sec-ii-notes-p114-fn2-confusion":
            row["qualifiers"].update(
                {
                    "source_line_start": 292,
                    "source_line_end": 292,
                    "pdf_physical_page": 25,
                    "printed_page_locator": "p.114 footnote 2",
                    "claim": (
                        "Haskell says the possible Landscape with Man killed by Serpent identification "
                        "may have been confused with the original Landscape with Man fleeing from Serpent, "
                        "associated with Montreal."
                    ),
                    "speaker": "Haskell’s footnote",
                    "text_layer": "reported historical claim",
                    "footnote_marker": 2,
                    "mentioned_candidate_ids": ["cand-5938", "cand-5939", "cand-5944", "cand-11428"],
                    "citation_publication_candidate_id": "cand-11428",
                    "citation_locator": "Rinehart, in Actes, 1961, pp. 19-30",
                    "relation_candidate": True,
                    "relation_candidate_note": (
                        "The reported possible confusion is preserved as an S2 candidate; the two works are not merged."
                    ),
                    "qualification": (
                        "‘Perhaps’ retained. The footnote gives 1961, while the bibliography gives 1960, I, pp. 19-30; "
                        "the year conflict remains unresolved and the cited work was not independently consulted."
                    ),
                    "ocr_corrections": [],
                }
            )
        elif row["statement_id"] in {
            "st-chp4-sec-ii-notes-p114-fn2-killed",
            "st-chp4-sec-ii-notes-p114-fn2-phocion",
            "st-chp4-sec-ii-notes-p114-fn2-woman",
        }:
            row["subject_candidate_id"] = "cand-5935"
            row["qualifiers"].update(
                {
                    "source_line_start": 292,
                    "source_line_end": 292,
                    "pdf_physical_page": 25,
                    "printed_page_locator": "p.114 footnote 2",
                    "speaker": "Haskell’s footnote",
                    "text_layer": "reported historical claim",
                    "footnote_marker": 2,
                    "citation_publication_candidate_id": "cand-11428",
                    "citation_locator": "Rinehart, in Actes, 1961, pp. 19-30",
                    "version_group_candidate_id": "cand-5935",
                    "version_count_mapping_unsettled": True,
                    "relation_candidate": True,
                    "relation_candidate_note": (
                        "The footnote associates the p.114 body’s unresolved Cassiano copy group with the named composition; "
                        "the third identification remains qualified as possible. No individual-copy mapping is inferred."
                    ),
                    "qualification": (
                        "Haskell’s reported identification is not independently checked. The footnote says 1961, while the "
                        "bibliography lists the page-matched Actes contribution as 1960, I, pp. 19-30; preserve the discrepancy."
                    ),
                }
            )
            if row["statement_id"].endswith("-woman"):
                row.update(
                    predicate="versions_of",
                    original_quote="The pictures are versions of the Landscape with Woman washing her Feet (Ottawa)",
                )
                row["qualifiers"].update(
                    claim=(
                        "Haskell reports that the unresolved group of Cassiano’s Poussin landscape copies includes "
                        "a version of Landscape with Woman washing her Feet, associated with Ottawa."
                    ),
                    mentioned_candidate_ids=["cand-5935", "cand-5936", "cand-5940", "cand-11428"],
                    location_candidate_id="cand-5940",
                )
            elif row["statement_id"].endswith("-phocion"):
                row.update(
                    predicate="versions_of",
                    original_quote="Funeral ofPhocion (collection of Lord Plymouth)",
                )
                row["qualifiers"].update(
                    claim=(
                        "Haskell reports that the unresolved group of Cassiano’s Poussin landscape copies includes "
                        "a version of Funeral of Phocion in the collection of Lord Plymouth."
                    ),
                    mentioned_candidate_ids=["cand-5935", "cand-5937", "cand-5941", "cand-5942", "cand-11428"],
                    location_or_collection_candidate_id="cand-5942",
                    collection_holder_candidate_id="cand-5941",
                    ocr_corrections=[
                        {
                            "source_line": 292,
                            "source_form": "Funeral ofPhocion",
                            "print_form": "Funeral of Phocion",
                        }
                    ],
                )
            else:
                row.update(
                    predicate="possibly_versions_of",
                    original_quote=(
                        "and possibly of the Landscape with Man killed by Serpent "
                        "(National Gallery, London)"
                    ),
                )
                row["qualifiers"].update(
                    claim=(
                        "Haskell says the unresolved Cassiano copy group may include a version of Landscape with Man "
                        "killed by Serpent, associated with the National Gallery, London."
                    ),
                    mentioned_candidate_ids=["cand-5935", "cand-5938", "cand-5943", "cand-1422", "cand-11428"],
                    location_candidate_id="cand-5943",
                    place_candidate_id="cand-1422",
                    possibility_word="possibly",
                )

    citation_note = (
        "This records Haskell’s bibliographic pointer only; the cited publication was not independently consulted, "
        "and the citation does not validate the historical claim. No formal S6 relation is created."
    )
    added = [
        statement(
            "st-chp4-sec-ii-notes-p114-fn1-poussin",
            "cand-1984",
            "referred_to",
            "cand-0107",
            line=291,
            marker=1,
            claim="Haskell reports frequent references to Angeloni by Poussin.",
            quote=NOTE1,
            mentioned=["cand-1984", "cand-0107", "cand-4634"],
            relation=True,
            relation_note="Explicitly reported reference by Poussin to Angeloni; retained as an S2 candidate, without creating a formal S6 relation.",
            qualification="Haskell’s report is source-attributed; Correspondance—passim is a locator, not an independently consulted source.",
            extra={
                "citation_source_candidate_id": "cand-4634",
                "citation_locator": "Correspondance—passim",
                "supporting_citation_statement_id": "st-chp4-sec-ii-notes-p114-fn1-cite-correspondance",
            },
        ),
        statement(
            "st-chp4-sec-ii-notes-p114-fn1-contemporaries",
            "cand-11681",
            "referred_to",
            "cand-0107",
            line=291,
            marker=1,
            claim="Haskell reports frequent references to Angeloni by other contemporaries, without naming them.",
            quote=NOTE1,
            mentioned=["cand-11681", "cand-0107", "cand-4371"],
            relation=True,
            relation_note="An unnamed group endpoint is kept open; no member identities or group size are inferred.",
            qualification=(
                "Mahon 1947 is cited in the same footnote, but the note does not specify which cited source supports "
                "this subclaim; no individual contemporaries or group size are inferred."
            ),
        ),
        statement(
            "st-chp4-sec-ii-notes-p114-fn1-cite-lumbroso",
            "cand-2962",
            "cites",
            "cand-5683",
            line=291,
            marker=1,
            claim="Haskell’s book cites Lumbroso, p. 200, in connection with references to Angeloni by Cassiano.",
            quote=NOTE1,
            mentioned=["cand-2036", "cand-0107", "cand-5626", "cand-5683"],
            relation=True,
            relation_note=citation_note,
            qualification="Citation locator only; the cited page was not independently consulted.",
            extra={
                "citation_author_candidate_ids": ["cand-5626"],
                "citation_publication_candidate_id": "cand-5683",
                "citation_locator": "Lumbroso, p. 200",
                "cited_material_not_independently_consulted": True,
            },
        ),
        statement(
            "st-chp4-sec-ii-notes-p114-fn1-cite-correspondance",
            "cand-2962",
            "cites",
            "cand-4634",
            line=291,
            marker=1,
            claim="Haskell’s book cites Poussin’s Correspondance—passim in connection with references to Angeloni by Poussin.",
            quote=NOTE1,
            mentioned=["cand-1984", "cand-0107", "cand-4634"],
            relation=True,
            relation_note=citation_note,
            qualification="‘Passim’ is retained as printed; the cited edition was not independently consulted.",
            extra={
                "citation_author_candidate_ids": ["cand-1984"],
                "citation_publication_candidate_id": "cand-4634",
                "citation_locator": "Correspondance—passim",
                "cited_material_not_independently_consulted": True,
            },
        ),
        statement(
            "st-chp4-sec-ii-notes-p114-fn1-cite-mahon",
            "cand-2962",
            "cites",
            "cand-4371",
            line=291,
            marker=1,
            claim="Haskell’s book cites Mahon, Studies in Seicento art and theory (1947), pp. 144 ff.",
            quote=NOTE1,
            mentioned=["cand-1494", "cand-4371"],
            relation=True,
            relation_note=citation_note,
            qualification="The print scan reads pp. 144 ff.; the OCR has ‘if.’. Citation locator only; cited pages were not independently consulted.",
            extra={
                "citation_author_candidate_ids": ["cand-1494"],
                "citation_publication_candidate_id": "cand-4371",
                "citation_locator": "Mahon, 1947, pp. 144 ff.",
                "cited_material_not_independently_consulted": True,
                "ocr_corrections": [
                    {"source_line": 291, "source_form": "pp. 144 if.", "print_form": "pp. 144 ff."}
                ],
            },
        ),
        statement(
            "st-chp4-sec-ii-notes-p114-fn1-chapter6",
            None,
            "internal_chapter_cross_reference",
            None,
            line=291,
            marker=1,
            claim="Footnote 1 points the reader to a later discussion in Chapter 6.",
            quote="and also later Chapter 6.",
            mentioned=[],
            relation=False,
            relation_note="Internal navigation only; it is not an external source citation or a historical relation.",
            qualification="No page or footnote is specified; no target claim is imported from Chapter 6.",
            extra={"referenced_chapter": 6},
        ),
        statement(
            "st-chp4-sec-ii-notes-p114-fn2-cite-rinehart-actes",
            "cand-2962",
            "cites",
            "cand-11428",
            line=292,
            marker=2,
            claim="Haskell’s book cites Sheila Rinehart in Actes, 1961, pp. 19-30, for the reported landscape identifications.",
            quote=NOTE2,
            mentioned=["cand-5793", "cand-11428"],
            relation=True,
            relation_note=citation_note,
            qualification=(
                "The cited page range matches the bibliography entry for Rinehart, ‘Poussin et la famille dal Pozzo’, "
                "listed as Actes du Colloque Poussin, 1960, I, pp. 19-30. The note says 1961; retain this unresolved "
                "year discrepancy and keep it distinct from Rinehart’s 1961 Italian Studies article (cand-5792)."
            ),
            extra={
                "citation_author_candidate_ids": ["cand-5793"],
                "citation_publication_candidate_id": "cand-11428",
                "citation_locator": "Rinehart, in Actes, 1961, pp. 19-30",
                "cited_material_not_independently_consulted": True,
                "bibliography_year": 1960,
                "footnote_year": 1961,
            },
        ),
    ]
    statements.extend(added)

    # The Actes locator is the page-matched publication; cand-5792 remains the separate
    # Italian Studies paper. Keep the source surface and record the unresolved year.
    mention_by_id["m-chp4-sec-ii-notes-p114-0055"]["candidate_id"] = "cand-11428"
    mention_by_id["m-chp4-sec-ii-notes-p114-0055"]["note"] = (
        "The page range matches the Actes contribution candidate; the footnote says 1961 while the bibliography says 1960, vol. I."
    )
    new_mentions = [
        {
            "mention_id": "m-chp4-sec-ii-notes-p114-0063",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11681",
            "surface_form": "other contemporaries",
            "start_char": "9783",
            "end_char": "9803",
            "note": "Unnamed and uncounted contemporaries reported as having referred to Angeloni; group membership remains unspecified.",
        },
        {
            "mention_id": "m-chp4-sec-ii-notes-p114-0064",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-5935",
            "surface_form": "The pictures",
            "start_char": "9910",
            "end_char": "9922",
            "note": "Anaphor for Cassiano’s unresolved group of two or three Poussin heroic landscape copies described in the p.114 body.",
        },
    ]
    mentions.extend(new_mentions)

    # Validate all emitted source spans and candidate references before any write.
    candidate_ids = {row["candidate_id"] for row in candidates}
    for row in statements:
        if row["statement_id"].startswith("st-chp4-sec-ii-notes-p114-"):
            for candidate_id in row["qualifiers"].get("mentioned_candidate_ids", []):
                if candidate_id not in candidate_ids:
                    raise SystemExit(f"STOP: dangling mentioned candidate {candidate_id}")
            for field in ("subject_candidate_id", "object_candidate_id"):
                if row[field] is not None and row[field] not in candidate_ids:
                    raise SystemExit(f"STOP: dangling {field} in {row['statement_id']}")
    for row in new_mentions:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment[start:end] != row["surface_form"]:
            raise SystemExit(f"STOP: planned mention span mismatch: {row['mention_id']}")

    candidate_bytes = write_csv_bytes(list(candidates[0]), candidates, candidate_bom, candidate_text)
    mention_headers = list(mentions[0])
    mention_bytes = write_csv_bytes(mention_headers, mentions, mention_bom, mention_text)
    statement_bytes = "\n".join(json.dumps(row, ensure_ascii=False) for row in statements).encode("utf-8") + b"\n"
    planned = {
        "statements": statement_bytes,
        "candidates": candidate_bytes,
        "mentions": mention_bytes,
    }
    return statements, candidates, mentions, planned


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize p.114 footnotes under guarded S2 writeback.")
    parser.add_argument("--apply", action="store_true", help="write after all source and table guards pass")
    args = parser.parse_args()

    statements, candidates, mentions, planned = preflight()
    print("P.114 notes review plan")
    print("  old statements: 5; new total in note block: 12")
    print("  new candidates: cand-11681 (open unnamed contemporaries group)")
    print("  corrected mention: Actes locator cand-5792 -> cand-11428; preserve 1961/1960 discrepancy")
    print("  new mentions: other contemporaries [9783,9803), The pictures [9910,9922)")
    print("  relation_candidate: true=11, false=1; no S0 or S6 edits")
    for name, data in planned.items():
        print(f"  planned {name} sha256={sha256(data)} bytes={len(data)}")
    if not args.apply:
        print("DRY-RUN: no files written")
        return

    backups: dict[str, Path] = {}
    temp_paths: dict[str, Path] = {}
    original_bytes = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, path in TABLES.items():
        expected = EXPECTED_TABLE_SHA256[name]
        if sha256(original_bytes[name]) != expected:
            raise SystemExit(f"STOP: {name} table changed between preflight and apply")
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"STOP: recovery backup already exists: {backup.name}")
        backups[name] = backup

    for name, path in TABLES.items():
        shutil.copy2(path, backups[name])
    try:
        for name, path in TABLES.items():
            temp_path = path.with_name(path.name + ".tmp-s2-chp4-p114-notes-20261011")
            if temp_path.exists():
                raise SystemExit(f"STOP: temporary write path already exists: {temp_path.name}")
            temp_path.write_bytes(planned[name])
            temp_paths[name] = temp_path
        for name, path in TABLES.items():
            temp_paths[name].replace(path)
    except Exception:
        for name, path in TABLES.items():
            if name in backups and backups[name].exists() and sha256(path.read_bytes()) != sha256(original_bytes[name]):
                shutil.copy2(backups[name], path)
        raise
    finally:
        for path in temp_paths.values():
            if path.exists():
                path.unlink()

    print("APPLIED")
    for name, path in TABLES.items():
        print(f"  {name}: sha256={sha256(path.read_bytes())} backup={backups[name].name}")
    print(f"  rows: candidates={len(candidates)} mentions={len(mentions)} statements={len(statements)}")


if __name__ == "__main__":
    main()
