"""Controlled S2 semantic re-audit for printed page 370 and its notes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
BODY = "chp-15:15_CHP-15_sec_ii:l61-67"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BACKUP_SUFFIX = ".bak-s2-chp15-p370-semantic-reaudit-20261009-retry"

EXPECTED_HASHES = {
    "entity-candidates.csv": "348091428b9607eace154c52f1c2ac7dc59c31529d205ece39c14d6d45454559",
    "mentions.csv": "c337eb1d046e151c73d52894b36349b04ed5659ee5cac88aadb549d0686bfde2",
    "book-statements.jsonl": "dd12122579b211c1cc2a06f5d41e35677f139dee5fcebf4121e4f755e1f8ca52",
    "s2-coverage.csv": "f37a3e8d0b3207108bded979915a43f2716106cd39cae7c775b7e555eae6a50f",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "pdf": "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.370 S2 corrections")
args = parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def atomic_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def atomic_jsonl(path: Path, rows: list[dict]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


for filename, expected in EXPECTED_HASHES.items():
    path = SOURCE if filename == "source" else PDF if filename == "pdf" else TABLES / filename
    if sha256(path) != expected:
        raise SystemExit(f"precondition changed: {path.relative_to(ROOT)}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
source_slices = {
    (61, 67): "\n".join(source_lines[60:67]),
    (90, 113): "\n".join(source_lines[89:113]),
}
body_text = source_slices[(61, 67)]

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)

candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

if BODY not in coverage_by_id or NOTES not in coverage_by_id:
    raise SystemExit("required p.370 coverage rows are absent")
if coverage_by_id[BODY]["disposition"] != "reviewed" or coverage_by_id[BODY]["migration_status"] != "complete":
    raise SystemExit("p.370 body is no longer reviewed/complete")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "complete":
    raise SystemExit("consolidated notes are no longer reviewed/complete")
if sum(row.get("segment_id") == BODY for row in mentions) != 45:
    raise SystemExit("p.370 mention inventory changed; review the new state before applying")
if sum(row.get("segment_id") == BODY for row in statements) != 22:
    raise SystemExit("p.370 body statement inventory changed; review the new state before applying")
if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11535:
    raise SystemExit("candidate ID sequence changed; do not allocate from the stale next ID")


def new_candidate(candidate_id: str, name: str, suggested_type: str, line: int, detail: str) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": suggested_type,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L{line}",
    }


candidate_updates = {
    "cand-10547": {
        "canonical_name": "Book collection in the library at Alticchiero: classics and books on agriculture, philosophy, and theology",
        "suggested_type": "archive",
        "detail": "A broad collection of books described as held by the library; individual titles, catalogue, and collection boundaries are not supplied.",
    },
    "cand-10551": {
        "canonical_name": "Night Thoughts",
        "suggested_type": "work",
        "detail": "The poem is named in Haskell's account of Young's Wood; no edition or external catalogue identity is supplied here.",
    },
    "cand-10559": {
        "canonical_name": "Tranquillity as an ideal represented by the Alticchiero garden altars",
        "suggested_type": "term",
        "detail": "Kept separate from Country Life; the passage does not identify a specific altar or surviving object for this ideal.",
    },
}
for candidate_id, changes in candidate_updates.items():
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"expected candidate missing: {candidate_id}")
    candidate_by_id[candidate_id].update(changes)

new_candidates = [
    new_candidate("cand-11536", "Library room at Alticchiero", "place", 62,
                  "The physical library space in the villa; kept distinct from the book collection it held."),
    new_candidate("cand-11537", "Bathroom at Alticchiero", "place", 62,
                  "The bathroom is identified as an interior room by Haskell; no finer location is supplied."),
    new_candidate("cand-11538", "Angelo Querini's study at Alticchiero", "place", 62,
                  "The room referred to as Querini's own study; the text gives no more precise location within the villa."),
    new_candidate("cand-11539", "Country Life as an ideal represented by the Alticchiero garden altars", "term", 65,
                  "Listed separately from Tranquillity; the passage does not map it to an individual altar."),
    new_candidate("cand-11540", "Fortune as an ideal represented by the Alticchiero garden altars", "term", 66,
                  "The local passage lists Fortune among the garden's ideals; it is not the separate indexed work under Salvator Rosa."),
]
if any(row["candidate_id"] in candidate_by_id for row in new_candidates):
    raise SystemExit("a planned candidate ID is already in use")
candidates.extend(new_candidates)
candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})


def find_span(surface: str, occurrence: int | None = None) -> tuple[int, int]:
    starts: list[int] = []
    start = body_text.find(surface)
    while start >= 0:
        starts.append(start)
        start = body_text.find(surface, start + 1)
    if not starts:
        raise SystemExit(f"mention surface not found in S0 segment: {surface!r}")
    if occurrence is None and len(starts) > 1:
        raise SystemExit(f"mention surface is ambiguous; supply a reviewed occurrence: {surface!r}")
    if occurrence is not None and not 0 <= occurrence < len(starts):
        raise SystemExit(f"mention occurrence is out of range: {surface!r} #{occurrence}")
    start = starts[occurrence or 0]
    return start, start + len(surface)


def update_mention(mention_id: str, **changes: str) -> None:
    if mention_id not in mention_by_id:
        raise SystemExit(f"expected mention missing: {mention_id}")
    mention_by_id[mention_id].update(changes)


# Correct the split toponym, the incomplete Philippe d'Orleans span, and two semantic mappings.
update_mention(
    "m-chp15-p370-alticchiero-0015",
    candidate_id="cand-10550",
    surface_form="Young’s Wood",
    start_char=str(find_span("Young’s Wood")[0]),
    end_char=str(find_span("Young’s Wood")[1]),
    note="The complete toponym names the garden area; the poet is separately mentioned as 'the poet'.",
)
mentions = [row for row in mentions if row["mention_id"] != "m-chp15-p370-alticchiero-0016"]
mention_by_id.pop("m-chp15-p370-alticchiero-0016", None)
update_mention(
    "m-chp15-p370-alticchiero-0011",
    surface_form="Philippe d’Orléans",
    start_char=str(find_span("Philippe d’Orléans")[0]),
    end_char=str(find_span("Philippe d’Orléans")[1]),
    note="The full printed name is present in S0 and matches the p.370 scan.",
)
update_mention("m-s2-chp15-surface-830230fc30c2a5cd", candidate_id="cand-10547",
               note="This is the book collection, distinct from the physical library room.")
update_mention("m-s2-surface-9154efa380b55add", candidate_id="cand-11540",
               note="In this passage Fortune is an ideal in the Alticchiero altar programme, not the indexed Salvator Rosa work.")
update_mention("m-chp15-p370-alticchiero-0031", candidate_id="cand-11539",
               note="Country Life is a separate ideal from Tranquillity.")
update_mention("m-chp15-p370-alticchiero-0004", candidate_id="cand-11536",
               note="Here 'library' denotes the physical room; the books are recorded separately as a collection.")

new_mentions: list[dict[str, str]] = []


def add_mention(
    mention_id: str,
    candidate_id: str,
    surface: str,
    note: str = "",
    occurrence: int | None = None,
) -> None:
    if mention_id in mention_by_id or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    start, end = find_span(surface, occurrence)
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": BODY,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


add_mention("m-chp15-p370-piranesi-print-group", "cand-10545", "prints by Piranesi")
add_mention("m-chp15-p370-bathroom-room", "cand-11537", "bathroom")
add_mention("m-chp15-p370-bacon-bust", "cand-10548", "a bust of Bacon")
add_mention("m-chp15-p370-querini-study-room", "cand-11538", "study")
add_mention("m-chp15-p370-edward-young-poet", "cand-2827", "the poet",
            "The book index identifies Edward Young with the Night Thoughts sub-entry; S3 retains the identity alignment decision.")
add_mention("m-chp15-p370-altar-bust-pair", "cand-10557", "colossal busts")
add_mention("m-chp15-p370-other-altars", "cand-10554", "Other altars")
add_mention("m-chp15-p370-altar-remention", "cand-10555", "the Altar", occurrence=1)
add_mention("m-chp15-p370-huber-print", "cand-10566", "one by Huber")
mentions.extend(new_mentions)
mention_by_id.update({row["mention_id"]: row for row in new_mentions})


def quote(fragment: str, start: int, end: int) -> str:
    cited = "\n".join(source_lines[start - 1:end])
    normalize = lambda value: " ".join(value.split())
    if normalize(fragment) not in normalize(cited):
        raise SystemExit(f"planned quote is outside source lines L{start}-L{end}: {fragment!r}")
    return fragment


def q(
    claim: str,
    start: int,
    end: int,
    mentioned: list[str],
    *,
    qualification: str = "",
    relation_candidate: bool = False,
    relation_note: str = "",
    speaker: str = "Haskell",
    text_layer: str = "authorial report",
    footnote_marker: str = "",
    footnote_line: str = "",
    ocr_corrections: list[dict] | None = None,
) -> dict:
    value = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 370,
        "pdf_physical_page": 10,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if relation_candidate:
        value["relation_candidate"] = True
        if relation_note:
            value["relation_candidate_note"] = relation_note
    if footnote_marker:
        value.update({
            "footnote_marker": footnote_marker,
            "footnote_segment": NOTES,
            "footnote_line_range": footnote_line,
            "footnote_text_pending": False,
            "footnote_body_link_status": "linked",
            "footnote_body_line_range": f"L{start}",
        })
    if ocr_corrections:
        value["ocr_corrections"] = ocr_corrections
    return value


def set_statement(
    statement_id: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    claim: str,
    original_quote: str,
    start: int,
    end: int,
    mentioned: list[str],
    *,
    qualification: str = "",
    relation_candidate: bool = False,
    relation_note: str = "",
    footnote_marker: str = "",
    footnote_line: str = "",
    ocr_corrections: list[dict] | None = None,
    speaker: str = "Haskell",
    text_layer: str = "authorial report",
) -> dict:
    if statement_id not in statement_by_id:
        raise SystemExit(f"expected statement missing: {statement_id}")
    row = statement_by_id[statement_id]
    row.update({
        "segment_id": BODY,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q(
            claim, start, end, mentioned,
            qualification=qualification,
            relation_candidate=relation_candidate,
            relation_note=relation_note,
            speaker=speaker,
            text_layer=text_layer,
            footnote_marker=footnote_marker,
            footnote_line=footnote_line,
            ocr_corrections=ocr_corrections,
        ),
        "original_quote": quote(original_quote, start, end),
        "origin": "book",
        "source_file": SOURCE_FILE,
    })
    return row


def add_statement(
    statement_id: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    claim: str,
    original_quote: str,
    start: int,
    end: int,
    mentioned: list[str],
    **kwargs,
) -> dict:
    if statement_id in statement_by_id:
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    row = {
        "statement_id": statement_id,
        "segment_id": BODY,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": q(claim, start, end, mentioned, **kwargs),
        "original_quote": quote(original_quote, start, end),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row
    return row


def rename_statement(old_id: str, new_id: str) -> None:
    if old_id not in statement_by_id or new_id in statement_by_id:
        raise SystemExit(f"cannot safely rename statement {old_id} -> {new_id}")
    row = statement_by_id.pop(old_id)
    row["statement_id"] = new_id
    statement_by_id[new_id] = row


# Give two formerly composite claims IDs that describe their now-separated content.
rename_statement(
    "st-chp15-p370-bacon-as-enlightenment-and-lodoli-hero",
    "st-chp15-p370-bacon-as-enlightenment-founder",
)
rename_statement(
    "st-chp15-p370-other-altars-friendships-and-ideals",
    "st-chp15-p370-other-altars-material",
)
rename_statement(
    "st-chp15-p370-wynne-reflection-on-madness-and-prophets",
    "st-chp15-p370-wynne-eastern-veneration-reflection",
)

ocr_wildarea = [{
    "source_file": SOURCE_FILE,
    "source_line": 63,
    "ocr": "wildarea",
    "print": "wild area",
    "basis": "CHP-15.pdf physical page 10.",
}]
ocr_phocion_quote = [{
    "source_file": SOURCE_FILE,
    "source_line": 65,
    "ocr": 'who "was Querini',
    "print": "who was Querini",
    "basis": "CHP-15.pdf physical page 10.",
}]
ocr_montaigne = [{
    "source_file": SOURCE_FILE,
    "source_line": 67,
    "ocr": "Montaigne's",
    "print": "Montaigne’s",
    "basis": "CHP-15.pdf physical page 10.",
}]
ocr_moschini = [{
    "source_file": SOURCE_FILE,
    "source_line": 110,
    "ocr": "1806, H, p. 116",
    "print": "1806, II, p. 116",
    "basis": "CHP-15.pdf physical page 10.",
}]

# Tighten the 20 existing body records and preserve their IDs except where the former claim was composite.
set_statement(
    "st-chp15-p370-alticchiero-piranesi-bathroom-prints", "cand-10545", "cand-11537",
    "located_at", "Haskell says the Piranesi prints lined the bathroom at Alticchiero.",
    "bathroom is lined with prints by Piranesi.", 62, 62,
    ["cand-10545", "cand-11537", "cand-1938"],
    qualification="The individual prints, editions, and present locations are not identified.",
    relation_candidate=True,
    relation_note="Work group to the named interior room; the source says the bathroom was lined with the prints.",
)
set_statement(
    "st-chp15-p370-alticchiero-decoration-combined-with-utility", "cand-0086", None,
    "decoration_combined_with_utility_throughout_villa",
    "Haskell summarizes the villa's design as combining decoration with utility throughout.",
    "Thus everywhere decoration is combined with utility.", 62, 62, ["cand-0086"],
    qualification="This is Haskell's summary of the villa, not a general architectural rule.",
)
set_statement(
    "st-chp15-p370-alticchiero-picart-oriental-engraving", "cand-10546", "cand-0086",
    "located_at_other_walls_of_alticchiero",
    "Haskell says Picart engravings of oriental customs lined other walls at Alticchiero and quotes their French description.",
    "Other walls are lined with engravings by Picart of oriental customs ‘qui amusent les passants, et arrêtent ceux qui aiment à réfléchir sur les folies de tant de prétendus sages’. ",
    62, 62, ["cand-10546", "cand-1925", "cand-0086"],
    qualification="The particular room, print titles, editions, and accuracy of the French wording against the prints are not independently checked.",
    relation_candidate=True,
    relation_note="The text locates the group on other villa walls but does not identify the room.",
)
set_statement(
    "st-chp15-p370-alticchiero-library-contents", "cand-10547", "cand-11536",
    "located_at",
    "Haskell says the Alticchiero library held the classics and a large collection of books on agriculture, philosophy, and theology.",
    "The library contains all the great classics as well as a large collection of books on agriculture, philosophy ‘and even theology’.",
    62, 62, ["cand-10547", "cand-11536"],
    qualification="The library room and its book collection are separate objects; the text provides no itemized catalogue or count.",
    relation_candidate=True,
    relation_note="Archive-like book collection to its physical library room.",
)
set_statement(
    "st-chp15-p370-bacon-bust-at-alticchiero", "cand-10548", "cand-11536",
    "located_at",
    "Haskell identifies a bust of Bacon in the library and calls it the 'idol of the temple'.",
    "The ‘idol of the temple’ is a bust of Bacon—", 62, 62,
    ["cand-10548", "cand-11536", "cand-0155"],
    qualification="'Idol of the temple' is Haskell's metaphor, not a documented object title.",
    relation_candidate=True,
    relation_note="The bust is located in the library by the local context.",
)
set_statement(
    "st-chp15-p370-bacon-as-enlightenment-founder", "cand-0155", "cand-8107",
    "described_as_founder_of_enlightenment",
    "Haskell characterizes Francis Bacon as a founding father of the Enlightenment.",
    "the founding father of the Enlightenment", 62, 62, ["cand-0155", "cand-8107"],
    qualification="This is Haskell's characterization, not an independently verified intellectual-history conclusion.",
)
set_statement(
    "st-chp15-p370-querini-study-daphnis-chloe-print-series", "cand-10549", "cand-11538",
    "located_at",
    "Haskell says the Daphnis and Chloe print series was kept in Querini's study and was intended to lighten his overburdened mind.",
    "Querini’s own study contained a series of prints designed to lighten his overburdened mind.",
    62, 62, ["cand-2075", "cand-10549", "cand-11538"],
    qualification="The print series is not individually titled or dated.",
    relation_candidate=True,
    relation_note="The series is located in the named study room.",
    footnote_marker="1",
    footnote_line="L109-L109",
)
set_statement(
    "st-chp15-p370-querini-garden-as-expression-of-taste", "cand-2075", "cand-2081",
    "garden_more_important_than_house_as_expression_of_querini_taste",
    "Haskell says the garden mattered more than the house as an expression of Querini's taste.",
    "The garden was even more important than the house as an expression of Querini’s taste.",
    63, 63, ["cand-2075", "cand-2081"],
    qualification="This is Haskell's evaluative comparison.",
)
set_statement(
    "st-chp15-p370-alticchiero-garden-formal-and-agreeable-confusion", "cand-2081", None,
    "regular_outline_combined_with_agreeable_confusion_of_plants",
    "Haskell describes the garden's main outline as severely regular, with an 'agreeable confusion' of bushes and plants within it.",
    "The main outlines were severely regular, but within this framework could be found an ‘agreeable confusion’ of bushes and plants.",
    63, 63, ["cand-2081"],
)
set_statement(
    "st-chp15-p370-youngs-wood-landscape-arrangement", "cand-10552", "cand-10550",
    "located_at",
    "Haskell describes columns and burial urns artfully arranged among carefully sited trees in Young's Wood.",
    "At some distance from the house was a wildarea thick with cunningly sited trees through whose branches could just be seen columns and burial urns strewn on the ground with artful casualness.",
    63, 63, ["cand-10550", "cand-10552"],
    qualification="The precise plan and identity of the grouped objects are not supplied.",
    relation_candidate=True,
    relation_note="The described columns and urns are located in the garden area; no individual object is identified.",
    ocr_corrections=ocr_wildarea,
)
set_statement(
    "st-chp15-p370-youngs-night-thoughts-romantic-influence", "cand-10551", "cand-3462",
    "caught_romantic_imagination_in_europe",
    "Haskell says Night Thoughts had caught the romantic imagination of Europe.",
    "whose Night Thoughts had caught the romantic imagination of Europe.",
    63, 63, ["cand-10551", "cand-3462"],
    qualification="This is Haskell's broad account of literary reception; the text names no readers or edition.",
)
set_statement(
    "st-chp15-p370-garden-allegory-philosophers-way-of-life", "cand-2081", "cand-10553",
    "designed_as_allegory_of_philosophers_way_of_life",
    "Haskell says the main part of the garden was designed as a complete allegory of the philosopher's way of life.",
    "The main part of the garden was designed as a complete allegory of the philosopher’s way of life",
    64, 64, ["cand-2081", "cand-10553"],
    qualification="This is Haskell's interpretation of the design.",
)
set_statement(
    "st-chp15-p370-friendship-altar-epicurus-phocion-busts", "cand-10557", "cand-10555",
    "part_of",
    "Haskell says the Altar of Friendship had a paired group of colossal busts of Epicurus and Phocion.",
    "the Altar of Friendship with its colossal busts of Epicurus ‘le Philosophe de la sage volupté’, so much misunderstood by vulgar minds, and of Phocion ‘le\nPhilosophe Citoyen’",
    64, 65, ["cand-10555", "cand-10557", "cand-0977", "cand-10556"],
    qualification="The paired busts are not individually attributed, dated, or located today.",
    relation_candidate=True,
    relation_note="The bust group is associated with and forms part of the named altar in Haskell's account.",
)
set_statement(
    "st-chp15-p370-phocion-described-as-querini-hero", "cand-2075", "cand-10556",
    "admired_as_querinis_particular_hero",
    "Haskell says Phocion was Querini's particular hero.",
    'who "was Querini’s particular hero.', 65, 65, ["cand-2075", "cand-10556"],
    qualification="The statement records Haskell's account of Querini's admiration; it does not infer direct influence.",
    relation_candidate=True,
    relation_note="The text explicitly calls Phocion Querini's particular hero; the formal relation type remains for S6 review.",
    ocr_corrections=ocr_phocion_quote,
)
set_statement(
    "st-chp15-p370-querini-aristocratic-cast-and-1761-downfall", "cand-2075", "cand-10556",
    "choice_of_phocion_read_as_querini_aristocratic_cast",
    "Haskell interprets the choice of Phocion as showing Querini's aristocratic cast of mind.",
    "The choice clearly shows his aristocratic cast of mind", 65, 65, ["cand-2075", "cand-10556"],
    qualification="This is Haskell's interpretation of the choice, not an independent psychological diagnosis.",
)
set_statement(
    "st-chp15-p370-altar-inscription-dedicated-to-giustiniani", "cand-10558", "cand-1198",
    "dedicated_to",
    "Haskell says the inscription below the Altar of Friendship was dedicated to Girolamo Ascanio Giustiniani.",
    "an inscription dedicated to his closest friend, Girolamo Ascanio Giustiniani.",
    65, 65, ["cand-10555", "cand-10558", "cand-2075", "cand-1198"],
    qualification="The inscription's wording is not transcribed; its dedication is reported by Haskell.",
    relation_candidate=True,
    relation_note="Inscription work to named dedicatee.",
)
set_statement(
    "st-chp15-p370-other-altars-material", "cand-10554", None,
    "other_altars_formed_from_antique_sculpture_or_modern_imitations",
    "Haskell says other garden altars were formed from genuine antique sculpture or modern imitations.",
    "Other altars, formed of real antique sculpture or of modern imitations",
    65, 65, ["cand-2081", "cand-10554"],
    qualification="The individual altars and source sculptures are not identified.",
)
set_statement(
    "st-chp15-p370-apollo-sculpture-by-unidentified-living-artist", "cand-10560", "cand-10561",
    "created_by",
    "Haskell describes Apollo in noble repose and youthful beauty as rendered by a modern sculptor who was still living.",
    "Apollo, rendered ‘in noble repose in the full beauty of his youth’ by a modern and still living sculptor.",
    66, 66, ["cand-10560", "cand-10561"],
    qualification="The sculptor is unnamed. The syntax follows the list 'Fortune and Apollo' and uses 'his'; whether the phrase covers a distinct Fortune object is not established.",
    relation_candidate=True,
    relation_note="Artist identity is unresolved; the claim is limited to Haskell's description of Apollo.",
)
set_statement(
    "st-chp15-p370-cabane-de-la-folie-and-montaigne-inscription", "cand-10563", "cand-10562",
    "located_at",
    "Haskell says Montaigne's dictum was fixed to the door of the thatched cabane de la folie.",
    "on the door of which was fixed Montaigne’s dictum ‘De la plus grande sagesse à la folie il n’y a qu’un demi-tour de cheville’",
    67, 67, ["cand-10562", "cand-1689", "cand-10563"],
    qualification="The underlying textual edition is not cited here.",
    relation_candidate=True,
    relation_note="Textual object to the place where Haskell says it was fixed.",
    ocr_corrections=ocr_montaigne,
)
set_statement(
    "st-chp15-p370-antique-bust-resembling-venetian-woman", "cand-10564", "cand-10565",
    "resembled",
    "Haskell says the antique bust in the hut resembled an unnamed old woman who used to roam Venice's streets.",
    "Inside was an antique bust which resembled an old mad woman who used to roam the streets of Venice",
    67, 67, ["cand-10562", "cand-10564", "cand-10565", "cand-2719"],
    qualification="The woman and bust remain unidentified; the resemblance is Haskell's report.",
    relation_candidate=True,
    relation_note="A reported resemblance, not an identity claim.",
)
rename_statement(
    "st-chp15-p370-wynne-eastern-veneration-reflection",
    "st-chp15-p370-wynne-reflects-on-eastern-veneration",
)
set_statement(
    "st-chp15-p370-wynne-reflects-on-eastern-veneration", "cand-2824", None,
    "reflected_on_eastern_veneration_of_the_mad",
    "Haskell says the bust's resemblance prompted Mme Rosenberg to think about reported veneration of the mad in the East.",
    "and the sight of this stimulated Mme Rosenberg to think of the veneration felt in the East for the mad",
    67, 67, ["cand-2824", "cand-10564", "cand-10565"],
    qualification="This is Haskell's report of Wynne's thought; 'the East' is broad, and the reported belief is not independently verified.",
)
set_statement(
    "st-chp15-p370-huber-voltaire-angle-engraving", "cand-10566", "cand-10562",
    "located_at",
    "Haskell says a Huber engraving of Voltaire's head was among the prints hung on the hut's walls to bring home the point.",
    "Engravings designed to bring home the point hung round the walls, among them one by Huber of the head of Voltaire taken from a number of different angles.",
    67, 67, ["cand-10562", "cand-10566", "cand-1306", "cand-2791"],
    qualification="No title, date, or surviving print is identified.",
    relation_candidate=True,
    relation_note="The source locates the identified Huber print on the hut walls.",
)

# Split claims and explicit relationships that were previously folded into the broad rows.
add_statement(
    "st-chp15-p370-piranesi-prints-created-by-piranesi", "cand-10545", "cand-1938",
    "created_by", "Haskell attributes the bathroom prints to Giovanni Battista Piranesi.",
    "prints by Piranesi", 62, 62, ["cand-10545", "cand-1938"],
    qualification="No individual print is identified.", relation_candidate=True,
    relation_note="The wording 'prints by Piranesi' gives the creator role.",
)
add_statement(
    "st-chp15-p370-picart-engravings-created-by-picart", "cand-10546", "cand-1925",
    "created_by", "Haskell attributes the oriental-custom engravings to Bernard Picart.",
    "engravings by Picart", 62, 62, ["cand-10546", "cand-1925"],
    qualification="Individual print titles and editions are not supplied.", relation_candidate=True,
    relation_note="The wording 'engravings by Picart' gives the creator role.",
)
add_statement(
    "st-chp15-p370-bacon-bust-depicts-francis-bacon", "cand-10548", "cand-0155",
    "depicts", "The bust is described as a bust of Francis Bacon.",
    "a bust of Bacon", 62, 62, ["cand-10548", "cand-0155"],
    qualification="The bust's maker, object identity, and present location are not supplied.",
    relation_candidate=True, relation_note="The work is explicitly identified as a bust of Bacon.",
)
add_statement(
    "st-chp15-p370-bacon-as-lodoli-particular-hero", "cand-0155", "cand-1411",
    "particular_hero_of", "Haskell calls Bacon the particular hero of Lodoli.",
    "the particular hero of Lodoli", 62, 62, ["cand-0155", "cand-1411"],
    qualification="The statement records an intellectual admiration, not a documented personal relationship or direct influence.",
    relation_candidate=True,
    relation_note="The precise formal relation type remains for later S6 review.",
)
add_statement(
    "st-chp15-p370-daphnis-chloe-prints-illustrate-text", "cand-10549", "cand-0901",
    "illustrates", "Haskell identifies the print series as illustrations to Daphnis and Chloe.",
    "They were illustrations to Daphnis and Chloe", 62, 62, ["cand-10549", "cand-0901"],
    qualification="The text does not identify an edition or individual impressions.",
    relation_candidate=True, relation_note="The print group is explicitly described as illustrations to the textual work.",
)
add_statement(
    "st-chp15-p370-daphnis-chloe-prints-drawn-by-regent", "cand-10549", "cand-1786",
    "created_by", "Haskell says the Daphnis and Chloe prints were drawn by Philippe d'Orléans, the Regent.",
    "drawn by the Régent Philippe d’Orléans", 62, 62, ["cand-10549", "cand-1786"],
    qualification="The printed name matches S0; no separate edition or drawing is identified.",
    relation_candidate=True, relation_note="Role recorded as designer/draughtsman, not engraver.",
)
add_statement(
    "st-chp15-p370-daphnis-chloe-prints-engraved-by-audran", "cand-10549", "cand-0145",
    "created_by", "Haskell says Audran engraved the Daphnis and Chloe illustrations.",
    "engraved-by Audran", 62, 62, ["cand-10549", "cand-0145"],
    qualification="No edition or individual impressions are identified.",
    relation_candidate=True, relation_note="Role recorded as engraver, distinct from the Regent's drawing role.",
)
add_statement(
    "st-chp15-p370-youngs-wood-part-of-garden", "cand-10550", "cand-2081",
    "part_of", "Haskell places the wild area later called Young's Wood at some distance from the house within the garden.",
    "At some distance from the house was a wildarea", 63, 63, ["cand-10550", "cand-2081", "cand-0086"],
    qualification="The source gives only a relative distance from the house, not a measured location.",
    relation_candidate=True, relation_note="Named garden area to the larger garden place.",
)
add_statement(
    "st-chp15-p370-youngs-wood-named-in-honour-of-young", "cand-10550", "cand-2827",
    "named_in_honour_of", "Haskell says Young's Wood was named in honour of the poet Edward Young.",
    "This was called ‘Young’s Wood’ in honour of the poet", 63, 63, ["cand-10550", "cand-2827"],
    qualification="The book index identifies Edward Young with the Night Thoughts sub-entry; final identity alignment remains for S3.",
    relation_candidate=True, relation_note="The passage explicitly says the place name honours the poet.",
)
add_statement(
    "st-chp15-p370-night-thoughts-authored-by-edward-young", "cand-10551", "cand-2827",
    "authored_by", "Haskell refers to Night Thoughts as the poem of the poet honoured by Young's Wood; the book index identifies that poet as Edward Young.",
    "the poet whose Night Thoughts", 63, 63, ["cand-10551", "cand-2827"],
    qualification="The author name is supplied through the book's own index seed, not an external verification; identity alignment remains for S3.",
    relation_candidate=True, relation_note="The source's possessive construction and index sub-entry identify the poet/work pairing.",
)
add_statement(
    "st-chp15-p370-garden-sculpture-programme-located-in-grounds", "cand-10554", "cand-2081",
    "located_at", "Haskell says shrines and carefully chosen antique and modern sculpture were distributed through the garden grounds.",
    "his various ideals were expressed in a number of shrines and carefully chosen pieces of antique and modern sculpture distributed in the grounds.",
    64, 64, ["cand-10554", "cand-2081"],
    qualification="The individual unnamed shrines and sculptures are not enumerated.",
    relation_candidate=True, relation_note="Collective garden works to the grounds where Haskell places them.",
)
add_statement(
    "st-chp15-p370-altar-bust-pair-depicts-epicurus", "cand-10557", "cand-0977",
    "depicts", "One of the Altar of Friendship's busts is identified as Epicurus.",
    "busts of Epicurus", 64, 64, ["cand-10557", "cand-0977", "cand-10555"],
    qualification="The bust is not individually attributed, dated, or located today.",
    relation_candidate=True, relation_note="The text explicitly names Epicurus as one of the figures represented.",
)
add_statement(
    "st-chp15-p370-altar-bust-pair-depicts-phocion", "cand-10557", "cand-10556",
    "depicts", "One of the Altar of Friendship's busts is identified as Phocion.",
    "and of Phocion", 64, 65, ["cand-10557", "cand-10556", "cand-10555"],
    qualification="The bust is not individually attributed, dated, or located today.",
    relation_candidate=True, relation_note="The text explicitly names Phocion as one of the figures represented.",
)
add_statement(
    "st-chp15-p370-epicurus-epithet-and-reception", "cand-0977", None,
    "described_as_wise_pleasure_philosopher_misunderstood_by_vulgar_minds",
    "Haskell gives Epicurus the epithet 'philosopher of wise pleasure' and says vulgar minds misunderstood him.",
    "Epicurus ‘le Philosophe de la sage volupté’, so much misunderstood by vulgar minds", 64, 64,
    ["cand-0977"], qualification="The French epithet is reproduced as printed; Haskell's characterization is not independently checked.",
)
add_statement(
    "st-chp15-p370-phocion-epithet-and-stance", "cand-10556", None,
    "described_as_citizen_philosopher_who_stood_against_mob",
    "Haskell calls Phocion 'the citizen philosopher' and describes him as having stood out against the ignorant mob.",
    "Philosophe Citoyen’—the man who had dared to stand out against the ignorant mob", 65, 65,
    ["cand-10556"], qualification="This is Haskell's characterization of Phocion.",
)
add_statement(
    "st-chp15-p370-populace-recognized-reform-harm", "cand-2075", None,
    "haskell_says_populace_saw_proposed_reforms_as_against_their_interests",
    "Haskell says the populace had long recognized that Querini's proposed reforms would not benefit them.",
    "long since apparent to the populace which, realising that his proposed ‘reforms’ certainly augured them no good",
    65, 65, ["cand-2075"],
    qualification="This records Haskell's interpretation of popular perception, not independently verified public opinion.",
)
add_statement(
    "st-chp15-p370-populace-rejoiced-at-querini-downfall", "cand-2075", None,
    "haskell_says_populace_rejoiced_at_1761_downfall",
    "Haskell says the populace rejoiced at Querini's downfall in 1761.",
    "had rejoiced at his downfall in 1761.", 65, 65, ["cand-2075"],
    qualification="'Downfall' is retained as Haskell's wording and is not equated here with a specific arrest or political event.",
)
add_statement(
    "st-chp15-p370-altar-inscription-located-below-altar", "cand-10558", "cand-10555",
    "located_at", "Haskell places the inscription below the Altar of Friendship.",
    "Below the Altar was an inscription", 65, 65, ["cand-10558", "cand-10555"],
    relation_candidate=True, relation_note="The text gives a specific location below the altar.",
)
add_statement(
    "st-chp15-p370-giustiniani-querinis-closest-friend", "cand-2075", "cand-1198",
    "friend_of", "Haskell identifies Girolamo Ascanio Giustiniani as Querini's closest friend.",
    "his closest friend, Girolamo Ascanio Giustiniani.", 65, 65, ["cand-2075", "cand-1198"],
    qualification="This is Haskell's explicit description of the friendship.",
    relation_candidate=True, relation_note="The text explicitly names Giustiniani as Querini's closest friend.",
)
add_statement(
    "st-chp15-p370-querini-swiss-friendships-open", "cand-2075", None,
    "friendships_formed_in_switzerland_with_people_not_named",
    "Haskell says some of the other friendships commemorated by the garden altars had been formed in Switzerland, but names no people.",
    "celebrated other friendships—those formed in Switzerland, for example", 65, 65, ["cand-2081", "cand-2075", "cand-10529"],
    qualification="The people are not named; no individual or collective person endpoint is guessed.",
    relation_candidate=True, relation_note="Open object endpoint because the text leaves the Swiss friends unnamed.",
)
add_statement(
    "st-chp15-p370-querini-friendship-with-mme-rosenberg", "cand-2075", "cand-2824",
    "friend_of",
    "Haskell says an Alticchiero garden altar commemorated Querini's friendship with Mme Rosenberg after her death in 1791.",
    "and after her death in 1791 that of Mme Rosenberg herself", 65, 65, ["cand-2081", "cand-2075", "cand-2824"],
    qualification="The sentence says the friendship was commemorated after her death; the cited Moschini page was not independently consulted.",
    relation_candidate=True,
    relation_note="The text explicitly names Mme Rosenberg as the friend commemorated.",
    footnote_marker="2",
    footnote_line="L110-L110",
)
for statement_id, concept_id, concept_name, source_quote, line in [
    ("st-chp15-p370-altar-ideal-tranquillity", "cand-10559", "Tranquillity", "Tranquillity", 65),
    ("st-chp15-p370-altar-ideal-country-life", "cand-11539", "Country Life", "Country Life", 65),
    ("st-chp15-p370-altar-ideal-fortune", "cand-11540", "Fortune", "Fortune", 66),
]:
    add_statement(
        statement_id, concept_id, "cand-10554", "represented_in_garden_altar_programme",
        f"Haskell lists {concept_name} among the ideals represented by the other garden altars.",
        source_quote, line, line, [concept_id, "cand-10554", "cand-2081"],
        qualification="The passage does not assign the ideal to a particular altar or surviving object.",
        relation_candidate=True, relation_note="Symbolic relation to the collective altar programme; individual altar mapping remains unspecified.",
    )
add_statement(
    "st-chp15-p370-altar-ideal-apollo", "cand-10560", "cand-10554",
    "included_in_garden_altar_programme",
    "Haskell lists Apollo among the ideals associated with the other garden altars.",
    "Apollo", 66, 66, ["cand-10560", "cand-10554", "cand-2081"],
    qualification="The text does not identify a specific altar or distinguish a separate ideal from its sculptural representation.",
    relation_candidate=True, relation_note="The Apollo work is included in the described altar programme; exact object-to-altar mapping is not given.",
)
add_statement(
    "st-chp15-p370-montaigne-dictum-text-authored-by-montaigne", "cand-10563", "cand-1689",
    "text_authored_by", "Haskell attributes the dictum fixed to the hut door to Montaigne.",
    "Montaigne’s dictum", 67, 67, ["cand-10563", "cand-1689"],
    qualification="The textual edition or exact source is not cited on this page.",
    relation_candidate=True, relation_note="The possessive explicitly attributes the dictum to Montaigne.",
)
add_statement(
    "st-chp15-p370-wynne-recalled-proverbial-link", "cand-2824", None,
    "recalled_proverbial_relationship_of_mad_with_prophets_and_poets",
    "Haskell says Mme Rosenberg recalled a proverbial relationship between mad people and prophets and poets.",
    "and to recall their proverbial relationship with prophets and poets.", 67, 67, ["cand-2824"],
    qualification="This records Haskell's report of Wynne's thought, not a general fact about all Eastern societies.",
)
add_statement(
    "st-chp15-p370-cabane-as-romantic-expression", "cand-10562", None,
    "most_explicit_expression_of_romantic_conception",
    "Haskell says the romantic nature of the garden conception came to the fore most explicitly in the cabane de la folie.",
    "The romantic nature of the whole conception came to the fore most explicitly in the ‘cabane de la folie’",
    67, 67, ["cand-10562", "cand-2081"],
    qualification="This is Haskell's interpretation of the design.",
)
add_statement(
    "st-chp15-p370-huber-engraving-created-by-huber", "cand-10566", "cand-1306",
    "created_by", "Haskell attributes the identified Voltaire-head engraving to Jean Huber.",
    "one by Huber", 67, 67, ["cand-10566", "cand-1306"],
    qualification="No title, date, or surviving impression is supplied.",
    relation_candidate=True, relation_note="The wording 'one by Huber' supplies the creator attribution.",
)
add_statement(
    "st-chp15-p370-huber-engraving-depicts-voltaire", "cand-10566", "cand-2791",
    "depicts", "Haskell says the Huber engraving showed Voltaire's head from multiple angles.",
    "of the head of Voltaire taken from a number of different angles.", 67, 67, ["cand-10566", "cand-2791"],
    qualification="No print title or surviving impression is identified.",
    relation_candidate=True, relation_note="The source explicitly names Voltaire's head as the engraving's subject.",
)

# The p.370 body note markers are on the Daphnis print paragraph and the Mme Rosenberg friendship clause.
statement_by_id["st-chp15-p370-querini-study-daphnis-chloe-print-series"]["qualifiers"]["footnote_note_statement_ids"] = [
    "st-chp15-p370-note1-querini-alticchiero-inventory"
]
statement_by_id["st-chp15-p370-querini-friendship-with-mme-rosenberg"]["qualifiers"]["footnote_note_statement_ids"] = [
    "st-chp15-p370-note2-moschini-citation"
]
for note_id, body_id, body_line in [
    ("st-chp15-p370-note1-querini-alticchiero-inventory", "st-chp15-p370-querini-study-daphnis-chloe-print-series", "L62"),
    ("st-chp15-p370-note2-moschini-citation", "st-chp15-p370-querini-friendship-with-mme-rosenberg", "L65"),
]:
    note = statement_by_id[note_id]
    note["qualifiers"]["footnote_body_link_status"] = "linked"
    note["qualifiers"]["footnote_body_line_range"] = body_line
    note["qualifiers"]["footnote_note_statement_ids"] = [body_id]

# Keep the remaining visual corrections attached only to the claims they affect.
statement_by_id["st-chp15-p370-bacon-as-enlightenment-founder"]["qualifiers"].pop("ocr_corrections", None)
statement_by_id["st-chp15-p370-querini-study-daphnis-chloe-print-series"]["qualifiers"].pop("ocr_corrections", None)
statement_by_id["st-chp15-p370-note2-moschini-citation"]["qualifiers"]["ocr_corrections"] = ocr_moschini

coverage_by_id[BODY]["note"] = (
    "Printed p.370 checked against CHP-15.pdf physical p.10 in a semantic re-audit. "
    "Separates the library, book collection, bathroom, study, named garden area, works, authorship, "
    "friendships, and altar ideals; corrects the Fortune-to-Rosa mislink, the Young/Night Thoughts "
    "candidate conflation, and the p.370 note-2 attachment. S0 remains unchanged."
)

candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = [row["mention_id"] for row in mentions]
statement_ids = [row["statement_id"] for row in statements]
if len(mention_ids) != len(set(mention_ids)):
    raise SystemExit("duplicate mention IDs in planned state")
if len(statement_ids) != len(set(statement_ids)):
    raise SystemExit("duplicate statement IDs in planned state")
if len(candidate_ids) != len(candidates):
    raise SystemExit("duplicate candidate IDs in planned state")

for row in mentions:
    if row["segment_id"] != BODY:
        continue
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']}")
    start, end = int(row["start_char"]), int(row["end_char"])
    if body_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
for row in statements:
    if row.get("segment_id") not in {BODY, NOTES}:
        continue
    for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
        if endpoint and endpoint not in candidate_by_id:
            raise SystemExit(f"statement has unknown endpoint: {row['statement_id']} -> {endpoint}")
    for endpoint in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
        if endpoint not in candidate_by_id:
            raise SystemExit(f"statement has unknown mentioned candidate: {row['statement_id']} -> {endpoint}")
    start = int(row.get("qualifiers", {}).get("source_line_start", 0))
    end = int(row.get("qualifiers", {}).get("source_line_end", 0))
    cited = "\n".join(source_lines[start - 1:end])
    normalize = lambda value: " ".join(value.split())
    if normalize(row.get("original_quote", "")) not in normalize(cited):
        raise SystemExit(f"statement quote mismatch: {row['statement_id']}")

relation_candidates = [
    row for row in statements
    if row.get("origin") == "book" and row.get("qualifiers", {}).get("relation_candidate") is True
]
open_relation_candidates = [
    row for row in relation_candidates
    if not row.get("subject_candidate_id") or not row.get("object_candidate_id")
]

plan = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": EXPECTED_HASHES["source"],
    "pdf_sha256": EXPECTED_HASHES["pdf"],
    "added_candidates": [row["candidate_id"] for row in new_candidates],
    "added_mentions": [row["mention_id"] for row in new_mentions],
    "removed_mentions": ["m-chp15-p370-alticchiero-0016"],
    "p370_mentions_after": sum(row.get("segment_id") == BODY for row in mentions),
    "p370_body_statements_after": sum(row.get("segment_id") == BODY for row in statements),
    "relation_candidates_after": len(relation_candidates),
    "open_relation_candidates_after": [row["statement_id"] for row in open_relation_candidates],
    "next_cursor": "chp-15:15_CHP-15_sec_ii:l69-83",
}

if args.apply:
    touched = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [(path, path.with_name(path.name + BACKUP_SUFFIX)) for path in touched]
    collision = next((backup for _, backup in backups if backup.exists()), None)
    if collision:
        raise SystemExit(f"backup already exists: {collision.name}")
    for path, backup in backups:
        shutil.copy2(path, backup)
    atomic_csv(candidate_path, candidate_fields, candidates)
    atomic_csv(mention_path, mention_fields, mentions)
    atomic_jsonl(statement_path, statements)
    atomic_csv(coverage_path, coverage_fields, coverage)

print(json.dumps(plan, ensure_ascii=False, indent=2))
