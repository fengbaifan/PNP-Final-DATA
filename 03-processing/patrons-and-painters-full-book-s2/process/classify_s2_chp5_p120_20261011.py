from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_INTRO = ROOT / "02-sources/02-Markdown/05_CHP-5_intro.md"
SOURCE_BODY = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources/01-book/CHP-5.pdf"
PAGE_IMAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p120_notes_page_review_20261011.png"
SEG_INTRO = "chp-5:05_CHP-5_intro:l7-9"
SEG_BODY = "chp-5:05_CHP-5_sec_i:l3-7"
SEG_P121 = "chp-5:05_CHP-5_sec_i:l9-15"
SEGMENT_SHA256 = {
    SEG_INTRO: "484938c722baca7ad9f5c6915b2257f626ab5c0bfb8cf5e3a9e3ef68d7ffd575",
    SEG_BODY: "0f71e323b2e8f05ec983bcd2b59dee0c45246e9e6ace15d99bbc2fedb56b539d",
    SEG_P121: "d038ae7e4e778a83837f2cc9532e73b7cf65f14dd69ef72ec7f9269435a50144",
}
SOURCE_SHA256 = {
    SOURCE_INTRO: "fe8a452c80f8ae012b224084037696b0f5459544e1919685e92dd2ef932b7265",
    SOURCE_BODY: "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
    PDF: "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a",
    PAGE_IMAGE: "1435897f02715318823fcc5e095957e295172481990a75092d96bf0fd58f546a",
}
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
    "coverage": ROOT / "04-knowledge/tables/s2-coverage.csv",
}
EXPECTED_TABLE_SHA256 = {
    "statements": "1f333d5ef30e82f1f22530b8f6b97442714917b1991c3702fc891b2e7bcd64cf",
    "candidates": "adc8b7ddf5c576bd2749b977033db51f322d5fe18c785e392acc0658ebc22413",
    "mentions": "0577f5b7fe1b41dc51b8570ce7560432cbf8217b4c3aa0edb40c5ee4e22cb4c9",
    "coverage": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = ".bak-s2-chp5-p120-20261011"

ORIGINALS = {
    "st-chp5-p120-annunciation-provenance": (SEG_BODY, "cand-1991", "footnote-claim", "cand-4491"),
    "st-chp5-p120-caravaggio-valentin-del-monte": (SEG_BODY, "cand-0544", "met_via_dealer_reported", "cand-1691"),
    "st-chp5-p120-dealer-growth": (SEG_BODY, "cand-0125", "historical_interpretation", ""),
    "st-chp5-p120-dealer-reputation-rosa": (SEG_BODY, "cand-0125", "dealer_pressure_reported", "cand-2236"),
    "st-chp5-p120-newcomers": (SEG_BODY, "cand-0125", "historical_interpretation", ""),
    "st-chp5-p120-note1-modello-ottawa": (SEG_INTRO, "cand-6013", "reported_location", "cand-5940"),
    "st-chp5-p120-note1-poussin-st-peters": (SEG_INTRO, "cand-2015", "was_painted_for", "cand-0714"),
    "st-chp5-p120-note1-preparatory-modello": (SEG_INTRO, "cand-1984", "made_preparatory_modello_for", "cand-6013"),
    "st-chp5-p120-note1-vatican-gallery": (SEG_INTRO, "cand-2015", "current_repository_reported", "cand-6012"),
    "st-chp5-p120-note2-friedlaender-locator": (SEG_INTRO, None, "bibliographic_locator_cited", "cand-4375"),
    "st-chp5-p120-note3-mancini-locator": (SEG_INTRO, None, "bibliographic_locator_cited", "cand-5726"),
    "st-chp5-p120-patronage-development": (SEG_BODY, "cand-1984", "historical_interpretation", "cand-3578"),
    "st-chp5-p120-poussin-position": (SEG_BODY, "cand-1984", "authorial_characterization", ""),
    "st-chp5-p120-ribera-daily-work": (SEG_BODY, "cand-2140", "daily_work_for_dealers_reported", "cand-0125"),
    "st-chp5-p120-rome-cultural-climate": (SEG_BODY, "cand-4490", "historical_context", "cand-4266"),
    "st-chp5-p121-rosa-continuation": (SEG_P121, "cand-0125", "dealer_pressure_reported", "cand-2236"),
}

CANDIDATES = [
    {
        "candidate_id": "cand-11682",
        "canonical_name": "Unidentified pope in Haskell’s p.120 statement about Poussin’s employment",
        "suggested_type": "person",
        "detail": "Haskell says Poussin was hardly ever employed by “the Pope” but does not identify which pope. Keep identity open and distinct from Urban VIII and Alexander VII.",
        "candidate_source_ref": f"{SEG_BODY}#L4",
    },
    {
        "candidate_id": "cand-11683",
        "canonical_name": "Poussin’s restricted circle of scholars and humanists (members unidentified)",
        "suggested_type": "",
        "detail": "The source says Poussin deliberately confined himself to this circle but names no members. Do not merge it with other scholarly or Roman circles.",
        "candidate_source_ref": f"{SEG_BODY}#L4",
    },
    {
        "candidate_id": "cand-11684",
        "canonical_name": "Intellectually minded connoisseurs described on p.120 (unnamed circle)",
        "suggested_type": "",
        "detail": "Haskell describes a circle interested in science and aesthetics and ready to encourage complex and restrained artistic expression. Membership and institutional status are not supplied; do not equate it with other Roman connoisseur groups.",
        "candidate_source_ref": f"{SEG_BODY}#L4",
    },
    {
        "candidate_id": "cand-11685",
        "canonical_name": "Living painters in Rome in Haskell’s account (unnamed group)",
        "suggested_type": "",
        "detail": "The group of living painters with whom professional dealers were in direct contact; individual members are not identified here.",
        "candidate_source_ref": f"{SEG_BODY}#L4",
    },
    {
        "candidate_id": "cand-11686",
        "canonical_name": "Young and unknown artists newly arrived in Rome in Haskell’s account",
        "suggested_type": "",
        "detail": "A source-defined group whose members had not entered the established system. Caravaggio and Ribera are examples in the following sentences, not an exhaustive membership list.",
        "candidate_source_ref": f"{SEG_BODY}#L5",
    },
    {
        "candidate_id": "cand-11687",
        "canonical_name": "Artists who had established their reputation in Haskell’s p.120 generalization",
        "suggested_type": "",
        "detail": "A generic group described by Haskell in contrast with young newcomers; no individual membership is supplied.",
        "candidate_source_ref": f"{SEG_BODY}#L6",
    },
    {
        "candidate_id": "cand-11688",
        "canonical_name": "Pope Alexander VII’s chapel at Castel Gandolfo (specific chapel unidentified)",
        "suggested_type": "place",
        "detail": "The chapel from which Haskell says the Annunciation traditionally came. The text does not name the chapel; keep it distinct from Castel Gandolfo as a town and preserve the provenance as inconclusive.",
        "candidate_source_ref": f"{SEG_BODY}#L7",
    },
    {
        "candidate_id": "cand-11689",
        "canonical_name": "Independent patrons in Haskell’s early seventeenth-century Rome account",
        "suggested_type": "",
        "detail": "A source-defined actor category credited with shaping artists’ reputations and development and helping loosen the Church/aristocracy monopoly. No individuals or formal body are identified.",
        "candidate_source_ref": f"{SEG_BODY}#L4",
    },
    {
        "candidate_id": "cand-11690",
        "canonical_name": "Complex imagery and aristocratically restrained artistic expression in Haskell’s p.120 account",
        "suggested_type": "term",
        "detail": "A source-bounded description of artistic expression that Roman connoisseurs were ready to encourage; it is not treated as a named school or verified movement.",
        "candidate_source_ref": f"{SEG_BODY}#L4",
    },
]

NEW_STATEMENT_IDS = {
    "st-chp5-p120-poussin-no-fresco",
    "st-chp5-p120-poussin-papal-employment",
    "st-chp5-p120-poussin-altarpiece-frequency",
    "st-chp5-p120-independent-patronage-power",
    "st-chp5-p120-poussin-restricted-circle",
    "st-chp5-p120-rome-connoisseur-circle",
    "st-chp5-p120-patronage-loosening-context",
    "st-chp5-p120-caravaggio-sale-to-valentin",
    "st-chp5-p120-established-artists-avoid-dealers",
    "st-chp5-p120-dealer-reputation",
    "st-chp5-p120-annunciation-inscription",
    "st-chp5-p120-cites-blunt-article",
}

NEW_MENTION_IDS = {
    "m-chp5-p120-s2-pope",
    "m-chp5-p120-s2-independent-patron",
    "m-chp5-p120-s2-independent-patrons",
    "m-chp5-p120-s2-poussin-circle",
    "m-chp5-p120-s2-connoisseur-circle",
    "m-chp5-p120-s2-artistic-expression",
    "m-chp5-p120-s2-living-painters",
    "m-chp5-p120-s2-young-unknown-artists",
    "m-chp5-p120-s2-newly-arrived-painter",
    "m-chp5-p120-s2-established-artist",
    "m-chp5-p120-s2-dealer",
    "m-chp5-p120-s2-alexander-chapel",
    "m-chp5-p120-s2-alexander-pronoun",
    "m-chp5-p120-s2-blunt-article",
}

RELATION_TRUE_NOTE = (
    "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    return raw, bom, text, rows


def emit_csv(headers, rows, bom: bool, original_text: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=headers,
        lineterminator="\r\n" if "\r\n" in original_text else "\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(rows)
    raw = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + raw


def read_segment(path: Path, first_line: int, last_line: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[first_line - 1 : last_line])


def require_quote(segment: str, quote: str) -> str:
    if quote not in segment:
        raise SystemExit(f"STOP: planned source quote not found: {quote!r}")
    return quote


def add_relation_classification(row: dict, value: bool, note: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    if "relation_candidate" in qualifiers:
        raise SystemExit(f"STOP: already classified: {row['statement_id']}")
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note


def new_statement(
    statement_id: str,
    segment_id: str,
    source_file: str,
    subject: str | None,
    predicate: str,
    object_: str | None,
    *,
    line_start: int,
    line_end: int,
    quote: str,
    claim: str,
    qualification: str,
    mentioned: list[str],
    relation_candidate: bool,
    relation_note: str,
    text_layer: str = "authorial narration",
    extra: dict | None = None,
) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": 1 if segment_id != SEG_P121 else 2,
        "printed_page_locator": "p.120" if segment_id != SEG_P121 else "p.121",
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
        "relation_candidate_note": relation_note,
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": source_file,
    }


def set_statement(
    rows: dict[str, dict],
    statement_id: str,
    *,
    subject=...,
    predicate: str,
    object_=...,
    segment_id: str,
    quote: str,
    claim: str,
    qualification: str,
    mentioned: list[str],
    relation_candidate: bool,
    relation_note: str,
    line_start: int,
    line_end: int,
    text_layer: str | None = None,
    extra: dict | None = None,
) -> None:
    row = rows[statement_id]
    row["segment_id"] = segment_id
    if subject is not ...:
        row["subject_candidate_id"] = subject
    if object_ is not ...:
        row["object_candidate_id"] = object_
    row["predicate"] = predicate
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update(
        {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "printed_page_locator": "p.120" if segment_id != SEG_P121 else "p.121",
            "claim": claim,
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation_candidate,
            "relation_candidate_note": relation_note,
        }
    )
    if text_layer:
        q["text_layer"] = text_layer
    if extra:
        q.update(extra)


def prepare(args):
    for path, expected in SOURCE_SHA256.items():
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"STOP: source evidence changed: {path}")
    segments = {
        SEG_INTRO: read_segment(SOURCE_INTRO, 7, 9),
        SEG_BODY: read_segment(SOURCE_BODY, 3, 7),
        SEG_P121: read_segment(SOURCE_BODY, 9, 15),
    }
    for segment_id, expected in SEGMENT_SHA256.items():
        if digest(segments[segment_id].encode("utf-8")) != expected:
            raise SystemExit(f"STOP: canonical segment hash changed: {segment_id}")
    if digest(PDF.read_bytes()) != SOURCE_SHA256[PDF] or digest(PAGE_IMAGE.read_bytes()) != SOURCE_SHA256[PAGE_IMAGE]:
        raise SystemExit("STOP: PDF or reviewed page image changed")

    intro, body, p121 = segments[SEG_INTRO], segments[SEG_BODY], segments[SEG_P121]
    for quote in (
        "The Martyrdom of St Erasmus, now in the Vatican Gallery",
        "only altarpiece that Poussin painted for anltalianchurch—St Peter’s in 1628-9",
        "preparatory modello (Ottawa)",
        "2 Friedlaender, p. 101.",
        "3 Mancini, I, p. 249.",
    ):
        require_quote(intro, quote)
    for quote in (
        "OUSSIN became one of the leading painters in Rome.",
        "Yet he never worked in\nPfresco",
        "was hardly ever employed by the Pope",
        "only once or twice painted an altarpiece",
        "Such was now the power of the independent patron to make the reputation of an artist and to guide his development.",
        "Deliberately confining himself to a restricted circle of scholars and humanists",
        "he soon moved from the generalised battle pictures",
        "Florentine Renaissance produced in somewhat similar circumstances nearly two hundred years earlier.",
        "Never was Rome so closely aligned to French policy and culture as during the twenty-odd years of Urban VIII’s pontificate.",
        "Not for many generations had there been such a circle of intellectually minded connoisseurs",
        "ready to encourage complex imagery and a more aristocratically restrained form of artistic expression",
        "Yet independent patrons of this kind were not the only ones who broke down the monopoly of Church and aristocracy",
        "With the increasing attraction of the city to tourists and growing economic uncertainties conditions of patronage gradually loosened",
        "professional art dealers in direct contact with living painters.",
        "Dealers at first played an important part only in the careers of young and unknown artists.",
        "some painter newly arrived in Rome, unable to fit at once into the established system.",
        "who sold some of his early works to a French dealer called Valentin",
        "through him met the Cardinal del Monte",
        "the Spaniard Giuseppe Ribera",
        "those who deal in pictures",
        "once an artist had made his reputation",
        "For they had a bad reputation both with painters and with the public.",
        "We hear that they tried to keep the young Salvator Rosa away from",
        "There is a tradition that the Annunciation (National Gallery, London) comes from Pope Alexander Vil’s chapel at Castel Gandolfo.",
        "As it is inscribed with his name this may well be correct, though the evidence is not conclusive",
        "see Blunt in Société Poussin, 1947, pp. 18-25",
    ):
        require_quote(body, quote)
    require_quote(p121, "direct contact with possible clients so that he would be forced to work exclusively for them")

    raw_tables = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, raw in raw_tables.items():
        if digest(raw) != EXPECTED_TABLE_SHA256[name]:
            raise SystemExit(f"STOP: {name} table SHA-256 changed: {digest(raw)}")

    original_rows = [json.loads(line) for line in raw_tables["statements"].decode("utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in original_rows}
    if len(statement_by_id) != len(original_rows):
        raise SystemExit("STOP: duplicate statement IDs")
    for statement_id, expected in ORIGINALS.items():
        row = statement_by_id.get(statement_id)
        if row is None:
            raise SystemExit(f"STOP: missing expected statement {statement_id}")
        actual = (
            row.get("segment_id"),
            row.get("subject_candidate_id"),
            row.get("predicate"),
            row.get("object_candidate_id"),
        )
        if actual != expected or "relation_candidate" in (row.get("qualifiers") or {}):
            raise SystemExit(f"STOP: pre-review statement changed: {statement_id}: {actual}")
    if NEW_STATEMENT_IDS & statement_by_id.keys():
        raise SystemExit("STOP: a planned new statement ID already exists")

    candidate_raw, candidate_bom, candidate_text, candidates = read_csv(TABLES["candidates"])
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(candidate_ids) != len(candidates):
        raise SystemExit("STOP: duplicate candidate IDs")
    if max(int(cid.removeprefix("cand-")) for cid in candidate_ids) != 11681:
        raise SystemExit("STOP: candidate ID counter changed")
    if candidate_ids & {row["candidate_id"] for row in CANDIDATES}:
        raise SystemExit("STOP: a planned candidate ID already exists")
    canonical_names = {row["canonical_name"].casefold() for row in candidates}
    if canonical_names & {row["canonical_name"].casefold() for row in CANDIDATES}:
        raise SystemExit("STOP: a planned candidate duplicates an existing canonical name")

    mention_raw, mention_bom, mention_text, mentions = read_csv(TABLES["mentions"])
    mention_ids = {row["mention_id"] for row in mentions}
    if len(mention_ids) != len(mentions):
        raise SystemExit("STOP: duplicate mention IDs")
    if mention_ids & NEW_MENTION_IDS:
        raise SystemExit("STOP: a planned mention ID already exists")
    mention_by_id = {row["mention_id"]: row for row in mentions}

    # Check every existing mention on the two edited p.120 segments before touching them.
    for mention in mentions:
        if mention["segment_id"] in (SEG_INTRO, SEG_BODY):
            segment = segments[mention["segment_id"]]
            start, end = int(mention["start_char"]), int(mention["end_char"])
            if segment[start:end] != mention["surface_form"]:
                raise SystemExit(f"STOP: existing mention span mismatch: {mention['mention_id']}")

    coverage_raw, _, _, coverage = read_csv(TABLES["coverage"])
    for segment_id in (SEG_INTRO, SEG_BODY, SEG_P121):
        rows = [row for row in coverage if row["segment_id"] == segment_id]
        if len(rows) != 1 or rows[0]["disposition"] != "reviewed" or rows[0]["migration_status"] != "complete":
            raise SystemExit(f"STOP: expected reviewed/complete coverage for {segment_id}")

    # Correct the church rather than the index’s separate altarpiece heading.
    peter_mention = mention_by_id["m-chp5-p120-note-0005"]
    peter_mention["candidate_id"] = "cand-0713"
    peter_mention["note"] = "The church for which Haskell says the altarpiece was painted; use the church/place candidate, not the separate altarpiece index heading."
    mancini_mention = mention_by_id["m-chp5-p120-note-0011"]
    mancini_mention["candidate_id"] = "cand-1508"
    mancini_mention["note"] = "Citation to Giulio Mancini’s Considerazioni sulla Pittura, volume I, page 249; edition given in the bibliography, cited page not independently consulted."
    french_policy = mention_by_id["m-chp5-p120-0008"]
    french_policy.update(
        {
            "candidate_id": "cand-4221",
            "surface_form": "French policy and culture",
            "start_char": "757",
            "end_char": "782",
            "note": "French political and cultural alignment; map to the France political/cultural candidate, not the geographic France place mention.",
        }
    )

    new_mentions = []

    def add_mention(mention_id: str, candidate_id: str, segment_id: str, phrase: str, note: str, *, after: int = 0):
        segment = segments[segment_id]
        start = segment.find(phrase, after)
        if start < 0:
            raise SystemExit(f"STOP: mention phrase missing: {phrase!r}")
        if segment.find(phrase, start + 1) >= 0:
            raise SystemExit(f"STOP: mention phrase is ambiguous; add an exact start: {phrase!r}")
        new_mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": segment_id,
                "candidate_id": candidate_id,
                "surface_form": phrase,
                "start_char": str(start),
                "end_char": str(start + len(phrase)),
                "note": note,
            }
        )

    add_mention("m-chp5-p120-s2-pope", "cand-11682", SEG_BODY, "the Pope", "Unidentified office-holder in Haskell’s employment statement; not equated with Urban VIII or Alexander VII.")
    add_mention("m-chp5-p120-s2-independent-patron", "cand-11689", SEG_BODY, "the independent patron", "Generic patron category in Haskell’s historical interpretation.")
    add_mention("m-chp5-p120-s2-independent-patrons", "cand-11689", SEG_BODY, "independent patrons of this kind", "Continuation of the source-defined independent-patron category.")
    add_mention("m-chp5-p120-s2-poussin-circle", "cand-11683", SEG_BODY, "restricted circle of scholars and humanists", "Unnamed circle to which Haskell says Poussin deliberately confined himself.")
    add_mention("m-chp5-p120-s2-connoisseur-circle", "cand-11684", SEG_BODY, "circle of intellectually minded connoisseurs", "Unnamed circle described by Haskell; membership and institutional status are unspecified.")
    add_mention("m-chp5-p120-s2-artistic-expression", "cand-11690", SEG_BODY, "complex imagery and a more aristocratically restrained form of artistic expression", "Source-described artistic expression the connoisseurs were ready to encourage.")
    add_mention("m-chp5-p120-s2-living-painters", "cand-11685", SEG_BODY, "living painters", "Unnamed group in direct contact with professional dealers.")
    add_mention("m-chp5-p120-s2-young-unknown-artists", "cand-11686", SEG_BODY, "young and unknown artists", "General group said to benefit from dealers at first.")
    add_mention("m-chp5-p120-s2-newly-arrived-painter", "cand-11686", SEG_BODY, "some painter newly arrived in Rome", "Generic member/example of the young newcomer group; no individual is identified.")
    add_mention("m-chp5-p120-s2-established-artist", "cand-11687", SEG_BODY, "an artist had made his reputation", "Generic established artist in Haskell’s contrast with newcomers.")
    add_mention("m-chp5-p120-s2-dealer", "cand-0125", SEG_BODY, "a dealer", "Generic dealer in Haskell’s qualified statement about established artists.", after=2100)
    add_mention("m-chp5-p120-s2-alexander-chapel", "cand-11688", SEG_BODY, "Pope Alexander Vil’s chapel at Castel Gandolfo", "Specific but unnamed chapel in the reported provenance tradition; the printed page reads VII where OCR has Vil.")
    pronoun_start = body.find("his name")
    if pronoun_start < 0:
        raise SystemExit("STOP: Alexander VII pronoun evidence missing")
    new_mentions.append(
        {
            "mention_id": "m-chp5-p120-s2-alexander-pronoun",
            "segment_id": SEG_BODY,
            "candidate_id": "cand-0665",
            "surface_form": "his",
            "start_char": str(pronoun_start),
            "end_char": str(pronoun_start + 3),
            "note": "Pronoun refers to Pope Alexander VII, the immediately preceding named person; Haskell treats the inscription as suggestive, not conclusive.",
        }
    )
    add_mention("m-chp5-p120-s2-blunt-article", "cand-11251", SEG_BODY, "Blunt in Société Poussin, 1947, pp. 18-25", "Bibliography identifies Blunt’s article; its contents were not independently consulted.")

    # Apply the source-grounded atomization and classifications to the existing rows.
    set_statement(
        statement_by_id,
        "st-chp5-p120-poussin-position",
        predicate="became_leading_painter_in",
        object_="cand-4490",
        segment_id=SEG_BODY,
        quote=require_quote(body, "OUSSIN became one of the leading painters in Rome."),
        claim="Haskell says Poussin became one of the leading painters in Rome.",
        qualification="The OCR omits the initial P in OUSSIN; the page image confirms POUSSIN. This is Haskell’s characterization.",
        mentioned=["cand-1984", "cand-4490"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=3,
        line_end=3,
        extra={"ocr_corrections": ["L3 OUSSIN → POUSSIN"]},
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-patronage-development",
        predicate="historical_interpretation",
        object_="cand-3578",
        segment_id=SEG_BODY,
        quote=require_quote(
            body,
            "he soon moved from the generalised battle pictures with which he had been forced to begin his career to a more and more complex interpretation of religion and mythology, often as difficult to understand as the great paintings of the Florentine Renaissance produced in somewhat similar circumstances nearly two hundred years earlier.",
        ),
        claim="Haskell describes Poussin’s movement from generalized battle pictures to complex religious and mythological interpretation and compares its difficulty with Florentine Renaissance painting.",
        qualification="Authorial art-historical interpretation and comparison; no specific painting or binary relation with the Renaissance is identified.",
        mentioned=["cand-1984", "cand-3578"],
        relation_candidate=False,
        relation_note="Authorial comparison and stylistic interpretation, not a relation between the person and the Renaissance candidate.",
        line_start=4,
        line_end=4,
        extra={"text_layer": "authorial art-historical interpretation"},
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-rome-cultural-climate",
        predicate="closely_aligned_to",
        object_="cand-4221",
        segment_id=SEG_BODY,
        quote=require_quote(body, "Never was Rome so closely aligned to French policy and culture as during the twenty-odd years of Urban VIII’s pontificate."),
        claim="Haskell describes Rome as closely aligned with French policy and culture during Urban VIII’s pontificate.",
        qualification="“Never” and “twenty-odd years” are Haskell’s framing; Urban VIII’s pontificate supplies the time context. The French policy/culture referent is mapped to France as a political/cultural power, not to geographic France.",
        mentioned=["cand-0209", "cand-4221", "cand-4490"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=4,
        line_end=4,
        extra={"time_context": "during the twenty-odd years of Urban VIII’s pontificate"},
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-dealer-growth",
        predicate="in_direct_contact_with",
        object_="cand-11685",
        segment_id=SEG_BODY,
        quote=require_quote(body, "we come across an ever larger number of professional art dealers in direct contact with living painters."),
        claim="Haskell says professional art dealers were increasingly in direct contact with living painters.",
        qualification="“An ever larger number” is Haskell’s unquantified historical characterization; no individual dealers or painters are named.",
        mentioned=["cand-0125", "cand-11685", "cand-4490"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=4,
        line_end=4,
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-newcomers",
        predicate="played_role_in_careers_of",
        object_="cand-11686",
        segment_id=SEG_BODY,
        quote=require_quote(body, "Dealers at first played an important part only in the careers of young and unknown artists. Every time we hear of them it is in connection with some painter newly arrived in Rome, unable to fit at once into the established system."),
        claim="Haskell says dealers initially played an important part in the careers of young, unknown artists newly arrived in Rome who could not immediately enter the established system.",
        qualification="“At first”, “only”, and “Every time we hear” are the author’s generalization; the group has no identified individual membership.",
        mentioned=["cand-0125", "cand-11686", "cand-4490"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=5,
        line_end=5,
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-caravaggio-valentin-del-monte",
        predicate="met_via_dealer_reported",
        object_="cand-1691",
        segment_id=SEG_BODY,
        quote=require_quote(body, "and through him met the Cardinal del Monte"),
        claim="Haskell says Caravaggio met Cardinal del Monte through the dealer Valentin.",
        qualification="The intermediary is Valentin; this is a source-reported relation candidate, not independent confirmation.",
        mentioned=["cand-0544", "cand-1691", "cand-2676"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=5,
        line_end=5,
        extra={"intermediary_candidate_id": "cand-2676", "footnote_numbers": [2]},
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-ribera-daily-work",
        predicate="daily_work_for_dealers_reported",
        object_="cand-0125",
        segment_id=SEG_BODY,
        quote=require_quote(body, "or of the Spaniard Giuseppe Ribera, who on his arrival in Rome ‘took to painting by the day for those who deal in pictures\n- - with all the trials such work involves for young men’.3"),
        claim="Haskell reports that Ribera took daily painting work from picture dealers on arriving in Rome, quoting a remark about the hardship for young men.",
        qualification="Underlying cited source was not consulted; “Spaniard” is the book’s descriptor, not a birthplace claim.",
        mentioned=["cand-0125", "cand-2140"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=5,
        line_end=6,
        extra={"footnote_numbers": [3]},
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-dealer-reputation-rosa",
        predicate="dealer_pressure_reported",
        object_="cand-2236",
        segment_id=SEG_BODY,
        quote=require_quote(body, "We hear that they tried to keep the young Salvator Rosa away from"),
        claim="Haskell reports that dealers tried to keep young Salvator Rosa away from possible clients so that he would be forced to work exclusively for them.",
        qualification="Reported allegation (“We hear”); the sentence continues in the p.121 segment. Do not present the allegation as independently established.",
        mentioned=["cand-0125", "cand-2236"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=6,
        line_end=6,
        extra={"quote_continues_at": f"{SEG_P121}#L10"},
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-annunciation-provenance",
        predicate="provenance_from_reported",
        object_="cand-11688",
        segment_id=SEG_BODY,
        quote=require_quote(body, "There is a tradition that the Annunciation (National Gallery, London) comes from Pope Alexander Vil’s chapel at Castel Gandolfo."),
        claim="Haskell reports the tradition that the Annunciation at the National Gallery, London came from Pope Alexander VII’s chapel at Castel Gandolfo.",
        qualification="This remains a tradition, not a verified provenance; Haskell explicitly says the evidence is inconclusive. The page image reads Alexander VII where OCR has Vil.",
        mentioned=["cand-0665", "cand-11688", "cand-1991", "cand-4491", "cand-5943"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=7,
        line_end=7,
        extra={
            "citation_statement_ids": ["st-chp5-p120-cites-blunt-article"],
            "ocr_corrections": ["L7 Vil → VII"],
        },
    )

    new_rows = []

    def add_statement(*args, **kwargs):
        row = new_statement(*args, **kwargs)
        if row["statement_id"] not in NEW_STATEMENT_IDS:
            raise SystemExit(f"STOP: unplanned new statement ID: {row['statement_id']}")
        if row["statement_id"] in statement_by_id or any(existing["statement_id"] == row["statement_id"] for existing in new_rows):
            raise SystemExit(f"STOP: duplicate new statement ID: {row['statement_id']}")
        segment = segments[row["segment_id"]]
        if row["original_quote"] not in segment:
            raise SystemExit(f"STOP: new statement quote missing from source: {row['statement_id']}")
        new_rows.append(row)

    body_file = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
    add_statement(
        "st-chp5-p120-poussin-no-fresco", SEG_BODY, body_file, "cand-1984", "did_not_work_in_fresco", None,
        line_start=3, line_end=4, quote=require_quote(body, "Yet he never worked in\nPfresco"),
        claim="Haskell says Poussin never worked in fresco.",
        qualification="The S0 OCR has “Pfresco”; the page image confirms “fresco”. This is a source claim about practice.",
        mentioned=["cand-1984"], relation_candidate=False,
        relation_note="A scalar negative statement about artistic practice; no second entity endpoint is asserted.",
        extra={"ocr_corrections": ["L4 Pfresco → fresco"]},
    )
    add_statement(
        "st-chp5-p120-poussin-papal-employment", SEG_BODY, body_file, "cand-1984", "hardly_ever_employed_by", "cand-11682",
        line_start=3, line_end=4, quote=require_quote(body, "was hardly ever employed by the Pope"),
        claim="Haskell says Poussin was hardly ever employed by an unidentified pope.",
        qualification="Preserve “hardly ever”; the source does not identify the pope, and this is not equated with Urban VIII or Alexander VII.",
        mentioned=["cand-1984", "cand-11682"], relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
    )
    add_statement(
        "st-chp5-p120-poussin-altarpiece-frequency", SEG_BODY, body_file, "cand-1984", "painted_altarpieces_only_once_or_twice", None,
        line_start=3, line_end=4, quote=require_quote(body, "only once or twice painted an altarpiece"),
        claim="Haskell says Poussin painted an altarpiece only once or twice.",
        qualification="Preserve the author’s approximate frequency; the statement does not identify an additional work.",
        mentioned=["cand-1984"], relation_candidate=False,
        relation_note="Scalar frequency claim with no identified second endpoint.",
        extra={"footnote_numbers": [1], "citation_statement_ids": ["st-chp5-p120-note1-poussin-st-peters"]},
    )
    add_statement(
        "st-chp5-p120-independent-patronage-power", SEG_BODY, body_file, "cand-11689", "historical_interpretation", None,
        line_start=4, line_end=4,
        quote=require_quote(body, "Such was now the power of the independent patron to make the reputation of an artist and to guide his development."),
        claim="Haskell argues that independent patrons could shape artists’ reputations and development.",
        qualification="Broad authorial account of a patron category; it names no patron or bounded artist group.",
        mentioned=["cand-11689"], relation_candidate=False,
        relation_note="General historical interpretation without a bounded pair of entity endpoints.",
    )
    add_statement(
        "st-chp5-p120-poussin-restricted-circle", SEG_BODY, body_file, "cand-1984", "confined_himself_to", "cand-11683",
        line_start=4, line_end=4,
        quote=require_quote(body, "Deliberately confining himself to a restricted circle of scholars and humanists"),
        claim="Haskell says Poussin deliberately confined himself to a restricted circle of scholars and humanists.",
        qualification="The group is unnamed; no member list or institutional identity is supplied.",
        mentioned=["cand-1984", "cand-11683"], relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
    )
    add_statement(
        "st-chp5-p120-rome-connoisseur-circle", SEG_BODY, body_file, "cand-11684", "ready_to_encourage", "cand-11690",
        line_start=4, line_end=4,
        quote=require_quote(body, "Not for many generations had there been such a circle of intellectually minded connoisseurs, interested in all the latest developments in science and aesthetics, ready to encourage complex imagery and a more aristocratically restrained form of artistic expression than that which filled the churches and palaces of the great."),
        claim="Haskell describes an unnamed circle of intellectually minded connoisseurs as interested in science and aesthetics and ready to encourage complex imagery and restrained artistic expression.",
        qualification="“Ready to encourage” records disposition, not proof that the group caused adoption of a style; the group’s members are unknown.",
        mentioned=["cand-11684", "cand-11690"], relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        extra={"modality": "ready to encourage; not a claim of completed effect"},
    )
    add_statement(
        "st-chp5-p120-patronage-loosening-context", SEG_BODY, body_file, None, "historical_interpretation", None,
        line_start=4, line_end=4,
        quote=require_quote(body, "Yet independent patrons of this kind were not the only ones who broke down the monopoly of Church and aristocracy in early seventeenth-century Rome. With the increasing attraction of the city to tourists and growing economic uncertainties conditions of patronage gradually loosened"),
        claim="Haskell attributes the loosening of patronage conditions in early seventeenth-century Rome to tourism and economic uncertainty, while describing independent patrons as one force weakening the Church and aristocracy’s monopoly.",
        qualification="Broad authorial causal interpretation; no individual tourist, patron, church body, or economic event is identified.",
        mentioned=["cand-11689", "cand-4490"], relation_candidate=False,
        relation_note="General causal interpretation rather than a relation between bounded entity candidates.",
    )
    add_statement(
        "st-chp5-p120-caravaggio-sale-to-valentin", SEG_BODY, body_file, "cand-0544", "sold_early_works_to", "cand-2676",
        line_start=5, line_end=5,
        quote=require_quote(body, "who sold some of his early works to a French dealer called Valentin"),
        claim="Haskell says Caravaggio sold some early works to the French dealer Valentin.",
        qualification="The works are unnamed; the sentence does not identify their titles, number, or later locations.",
        mentioned=["cand-0544", "cand-2676"], relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        extra={"footnote_numbers": [2]},
    )
    add_statement(
        "st-chp5-p120-established-artists-avoid-dealers", SEG_BODY, body_file, "cand-11687", "rarely_worked_for", "cand-0125",
        line_start=6, line_end=6,
        quote=require_quote(body, "once an artist had made his reputation there would be no question of his ever working again for a dealer unless driven by the most acute distress."),
        claim="Haskell generalizes that an artist who had established a reputation would not work again for a dealer except under acute distress.",
        qualification="This is a qualified authorial generalization about an unnamed artist group; preserve the explicit exception.",
        mentioned=["cand-11687", "cand-0125"], relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
    )
    add_statement(
        "st-chp5-p120-dealer-reputation", SEG_BODY, body_file, "cand-0125", "authorial_characterization", None,
        line_start=6, line_end=6,
        quote=require_quote(body, "For they had a bad reputation both with painters and with the public."),
        claim="Haskell says art dealers had a bad reputation among painters and the public.",
        qualification="Authorial characterization; the phrase does not identify a particular painter, member of the public, or dealer.",
        mentioned=["cand-0125"], relation_candidate=False,
        relation_note="Scalar characterization without a bounded second endpoint.",
    )
    add_statement(
        "st-chp5-p120-annunciation-inscription", SEG_BODY, body_file, "cand-1991", "inscribed_with_name_of", "cand-0665",
        line_start=7, line_end=7,
        quote=require_quote(body, "As it is inscribed with his name this may well be correct, though the evidence is not conclusive"),
        claim="Haskell says the Annunciation bears Pope Alexander VII’s name and treats the inscription as support for the provenance tradition.",
        qualification="The inscription is presented as suggestive only; Haskell explicitly says the evidence is not conclusive.",
        mentioned=["cand-0665", "cand-1991"], relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        extra={"citation_statement_ids": ["st-chp5-p120-cites-blunt-article"]},
    )
    add_statement(
        "st-chp5-p120-cites-blunt-article", SEG_BODY, body_file, "cand-2962", "cites", "cand-11251",
        line_start=7, line_end=7,
        quote=require_quote(body, "see Blunt in Société Poussin, 1947, pp. 18-25"),
        claim="Haskell’s book cites Anthony Blunt’s 1947 article on Poussin’s Annunciation, pages 18–25.",
        qualification="The bibliography identifies the article; its contents and cited pages were not independently consulted.",
        mentioned=["cand-2962", "cand-11251", "cand-5902"], relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        text_layer="bibliographic citation",
        extra={"citation_locator": "Société Poussin, 1947, pp. 18–25"},
    )

    # Convert the short footnotes to explicit citations and classify all four factual note-1 statements.
    for sid, note in (
        ("st-chp5-p120-note1-vatican-gallery", "Haskell reports The Martyrdom of St Erasmus in the Vatican Gallery at the time of writing; this is an S2 source claim, not a current-location verification."),
        ("st-chp5-p120-note1-poussin-st-peters", RELATION_TRUE_NOTE),
        ("st-chp5-p120-note1-preparatory-modello", RELATION_TRUE_NOTE),
        ("st-chp5-p120-note1-modello-ottawa", RELATION_TRUE_NOTE),
    ):
        row = statement_by_id[sid]
        add_relation_classification(row, True, note)
    statement_by_id["st-chp5-p120-note1-poussin-st-peters"]["object_candidate_id"] = "cand-0713"
    statement_by_id["st-chp5-p120-note1-poussin-st-peters"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-2015", "cand-1984", "cand-0713"]

    set_statement(
        statement_by_id,
        "st-chp5-p120-note2-friedlaender-locator",
        subject="cand-2962",
        predicate="cites",
        object_="cand-4375",
        segment_id=SEG_INTRO,
        quote=require_quote(intro, "2 Friedlaender, p. 101."),
        claim="Haskell’s book cites Walter Friedlaender, Caravaggio Studies, page 101.",
        qualification="The bibliography identifies the cited book and publication; page 101 was not independently consulted.",
        mentioned=["cand-2962", "cand-3506", "cand-4375"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=9,
        line_end=9,
        text_layer="bibliographic citation",
        extra={
            "citation_locator": "p. 101",
            "citation_for_statement_ids": ["st-chp5-p120-caravaggio-sale-to-valentin", "st-chp5-p120-caravaggio-valentin-del-monte"],
            "footnote_numbers": [2],
        },
    )
    set_statement(
        statement_by_id,
        "st-chp5-p120-note3-mancini-locator",
        subject="cand-2962",
        predicate="cites",
        object_="cand-1508",
        segment_id=SEG_INTRO,
        quote=require_quote(intro, "3 Mancini, I, p. 249."),
        claim="Haskell’s book cites Giulio Mancini’s Considerazioni sulla Pittura, volume I, page 249.",
        qualification="The bibliography identifies the work and its 1956 edition; the cited page was not independently consulted.",
        mentioned=["cand-2962", "cand-1507", "cand-1508"],
        relation_candidate=True,
        relation_note=RELATION_TRUE_NOTE,
        line_start=9,
        line_end=9,
        text_layer="bibliographic citation",
        extra={"citation_locator": "volume I, p. 249", "footnote_numbers": [3], "citation_for_statement_ids": ["st-chp5-p120-ribera-daily-work"]},
    )
    continuation = statement_by_id["st-chp5-p121-rosa-continuation"]
    continuation["original_quote"] = require_quote(
        p121,
        "direct contact with possible clients so that he would be forced to work exclusively for them",
    )
    continuation["qualifiers"]["claim"] = (
        "Continuation of Haskell’s report that dealers tried to isolate young Salvator Rosa from possible clients so they could force him to work exclusively for them."
    )
    continuation["qualifiers"]["qualification"] = (
        "Completes the p.120 sentence and carries the same reported allegation; it is not a second independent event."
    )
    continuation["qualifiers"]["source_line_start"] = 10
    continuation["qualifiers"]["source_line_end"] = 10
    continuation["qualifiers"].pop("footnote_numbers", None)
    add_relation_classification(
        continuation,
        True,
        "Continuation of the p.120 reported dealer-pressure relation candidate; it completes the same sentence and does not create a second independent event.",
    )

    if {row["statement_id"] for row in new_rows} != NEW_STATEMENT_IDS:
        raise SystemExit(f"STOP: planned new statement set mismatch: {sorted(NEW_STATEMENT_IDS - {r['statement_id'] for r in new_rows})}")
    if {row["mention_id"] for row in new_mentions} != NEW_MENTION_IDS:
        raise SystemExit(f"STOP: planned new mention set mismatch: {sorted(NEW_MENTION_IDS - {r['mention_id'] for r in new_mentions})}")

    candidate_rows = []
    for candidate in CANDIDATES:
        row = {
            "candidate_id": candidate["candidate_id"],
            "index_entry_id": "",
            "canonical_name": candidate["canonical_name"],
            "index_page_range": "",
            "suggested_type": candidate["suggested_type"],
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": candidate["detail"],
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": candidate["candidate_source_ref"],
        }
        candidate_rows.append(row)
    candidates.extend(candidate_rows)
    mentions.extend(new_mentions)

    # Confirm all statement endpoint and mention mappings exist and all new spans point to source text.
    all_candidate_ids = candidate_ids | {row["candidate_id"] for row in candidate_rows}
    all_statement_rows = list(statement_by_id.values()) + new_rows
    for row in all_statement_rows:
        if row["statement_id"] not in ORIGINALS and row["statement_id"] not in NEW_STATEMENT_IDS:
            continue
        q = row.get("qualifiers") or {}
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint is not None and endpoint != "" and endpoint not in all_candidate_ids:
                raise SystemExit(f"STOP: unknown endpoint candidate on {row['statement_id']}: {endpoint}")
        if q.get("relation_candidate") and not (row.get("subject_candidate_id") and row.get("object_candidate_id")):
            raise SystemExit(f"STOP: relation candidate lacks two endpoints: {row['statement_id']}")
        if row["statement_id"] in NEW_STATEMENT_IDS and row.get("segment_id") not in segments:
            raise SystemExit(f"STOP: unknown source segment for {row['statement_id']}")
    for mention in mentions:
        if mention["mention_id"] in NEW_MENTION_IDS:
            segment = segments[mention["segment_id"]]
            start, end = int(mention["start_char"]), int(mention["end_char"])
            if segment[start:end] != mention["surface_form"]:
                raise SystemExit(f"STOP: new mention span mismatch: {mention['mention_id']}")
        if mention["mention_id"] in NEW_MENTION_IDS or mention["mention_id"] in (
            "m-chp5-p120-note-0005", "m-chp5-p120-note-0011", "m-chp5-p120-0008"
        ):
            if mention["candidate_id"] not in all_candidate_ids:
                raise SystemExit(f"STOP: mention points to unknown candidate: {mention['mention_id']}")

    # Keep original JSONL and CSV encodings/newline conventions and avoid touching coverage.
    statement_text = raw_tables["statements"].decode("utf-8-sig")
    statement_bom = raw_tables["statements"].startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if "\r\n" in statement_text else "\n"
    output_lines = []
    for raw_line in statement_text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not line.strip():
            output_lines.append(raw_line)
            continue
        row = json.loads(line)
        if row["statement_id"] in statement_by_id:
            row = statement_by_id[row["statement_id"]]
            line = json.dumps(row, ensure_ascii=False)
            ending = ending or newline
        output_lines.append(line + ending)
    if output_lines and not output_lines[-1].endswith(("\n", "\r")):
        output_lines[-1] += newline
    for row in new_rows:
        output_lines.append(json.dumps(row, ensure_ascii=False) + newline)
    statement_updated = (b"\xef\xbb\xbf" if statement_bom else b"") + "".join(output_lines).encode("utf-8")

    candidate_headers = list(candidates[0].keys())
    mention_headers = list(mentions[0].keys())
    candidate_updated = emit_csv(candidate_headers, candidates, candidate_bom, candidate_text)
    mention_updated = emit_csv(mention_headers, mentions, mention_bom, mention_text)

    output = {
        "statements": statement_updated,
        "candidates": candidate_updated,
        "mentions": mention_updated,
    }
    target_true = sum(1 for row in all_statement_rows if row["statement_id"] in ORIGINALS or row["statement_id"] in NEW_STATEMENT_IDS if row.get("qualifiers", {}).get("relation_candidate") is True)
    target_false = sum(1 for row in all_statement_rows if row["statement_id"] in ORIGINALS or row["statement_id"] in NEW_STATEMENT_IDS if row.get("qualifiers", {}).get("relation_candidate") is False)
    print(f"p.120/p.121 rows classified: {len(ORIGINALS)} existing; {len(new_rows)} new statements")
    print(f"new candidates: {len(candidate_rows)}; new mentions: {len(new_mentions)}")
    print(f"target classification: {target_true} relation candidates; {target_false} non-relational claims")
    print("target edits:")
    for sid in sorted(set(ORIGINALS) | NEW_STATEMENT_IDS):
        row = statement_by_id.get(sid) or next(item for item in new_rows if item["statement_id"] == sid)
        q = row.get("qualifiers") or {}
        print(f"  {sid}: relation_candidate={q.get('relation_candidate')}; {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')}; {row.get('predicate')}")
    print("dry-run prepared; no files written" if not args.apply else "apply requested")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify p.120 S2 claims and citations with guarded source/table checks.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed update and preserve backups")
    args = parser.parse_args()
    output = prepare(args)
    if not args.apply:
        return 0

    paths = {name: TABLES[name] for name in output}
    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in paths.items()}
    for name, backup in backups.items():
        if backup.exists():
            raise SystemExit(f"STOP: recovery copy already exists: {backup.name}")
        shutil.copy2(paths[name], backup)
    written = []
    try:
        for name, data in output.items():
            temp = paths[name].with_name(paths[name].name + ".tmp-s2-chp5-p120")
            temp.write_bytes(data)
            temp.replace(paths[name])
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
