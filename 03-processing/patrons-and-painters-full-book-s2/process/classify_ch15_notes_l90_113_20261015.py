from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BIBLIOGRAPHY = ROOT / "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SEGMENT_ID = "chp-15:15_CHP-15_sec_ii:l90-113"
SEGMENT_LINE_START = 90
SEGMENT_LINE_END = 113

EXPECTED_HASHES = {
    "statements": "669fa95034c249b447226bab9147003e4687952117c4baba49343b232f05573e",
    "candidates": "abc0b39d010ebfd4b2c74d040112b1c261e9595d4482d3ce958d968d4c2c933b",
    "mentions": "edb8725525b32df523f6b536bc5a297de986d725e96fcb32c9170d4f1e66cff7",
    "source": "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f",
    "bibliography": "f69ccf85eda80949e835db205addb5e89c8521a60e3632db1d7bf7c62e4d38b3",
}

UNSET_IDS = {
    "st-chp15-p365-note1-brunelli-1923",
    "st-chp15-p365-note2-radicchio-1786",
    "st-chp15-p365-note2-neu-mayr-1807",
    "st-chp15-p367-note1-della-valle-quotation",
    "st-chp15-p367-note1-elementi-first-volume-1786",
    "st-chp15-p367-note1-elementi-completion-1834",
    "st-chp15-p367-note4-memmo-friends-citations",
    "st-chp15-p368-note1-memmo-zaguri-reference",
    "st-chp15-p368-note2-gallery-destruction",
    "st-chp15-p368-note3-inventory-record",
    "st-chp15-p368-note3-mengs-drawing-and-prints",
    "st-chp15-p368-note4-open-house-reference",
    "st-chp15-p368-note5-brenta-obstruction-reference",
    "st-chp15-p368-note6-elementi-reference",
    "st-chp15-p368-note7-1761-crisis-reference",
    "st-chp15-p369-note1-anonymous-voyages-rumour-source",
    "st-chp15-p369-note2-festari-reference",
    "st-chp15-p369-note3-bernis-rosenberg-quotation",
    "st-chp15-p369-note4-alticchiero-wynne-publication",
    "st-chp15-p369-note4-brunelli-article",
    "st-chp15-p369-note4-heraclitus-democritus-busts",
    "st-chp15-p370-note1-querini-alticchiero-inventory",
    "st-chp15-p370-note2-moschini-citation",
    "st-chp15-p371-note1-antiquarians-dedicated-books-to-querini",
    "st-chp15-p371-note2-de-non-citation-chain",
    "st-chp15-p372-note1-cites-brunelli-bonetti-1951",
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12251",
        "canonical_name": "Several hundred unidentified prints owned by Andrea Memmo",
        "suggested_type": "work",
        "status": "open",
        "detail": "Haskell says Memmo owned several hundred prints and that the artist is rarely indicated. No individual prints or artists are identified; keep this as a source-bounded group, not a list of distinct works.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L100",
    },
    {
        "candidate_id": "cand-12252",
        "canonical_name": "Unnamed plans to stop flooding of the Brenta",
        "suggested_type": "procedure",
        "status": "open",
        "detail": "Haskell reports that Querini was accused of obstructing plans for stopping the Brenta flooding because they threatened his garden. No specific plan, project, or implementing authority is identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L102",
    },
]

NEW_MENTIONS = [
    (
        "m-chp15-p368-querini-0055",
        "cand-12251",
        "several hundred prints",
        "Source-bounded group; Haskell says the artist is rarely indicated and names no individual print.",
    ),
    (
        "m-chp15-p368-querini-0056",
        "cand-12252",
        "plans for stopping the flooding",
        "Unnamed flood-prevention plans; Haskell reports an accusation against Querini but identifies no specific project.",
    ),
    (
        "m-chp15-p370-alticchiero-0053",
        "cand-8533",
        "II, p. 255",
        "Locator for the same Levi volume II cited at p.368 note 3; this note gives p.255. The publication itself was not consulted.",
    ),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_hashes() -> None:
    for label, path in {
        "statements": STATEMENTS,
        "candidates": CANDIDATES,
        "mentions": MENTIONS,
        "source": SOURCE,
        "bibliography": BIBLIOGRAPHY,
    }.items():
        if not path.exists():
            raise SystemExit(f"Required input is missing: {path}")
        actual = sha256(path)
        if actual != EXPECTED_HASHES[label]:
            raise SystemExit(f"Precondition hash changed for {label}: {actual}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encode_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def load_csv(path: Path) -> tuple[list[str], list[dict], bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), has_bom


def encode_csv(fields: list[str], rows: list[dict], has_bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + data if has_bom else data


def phrase_span(text: str, phrase: str) -> tuple[int, int]:
    positions = [i for i in range(len(text)) if text.startswith(phrase, i)]
    if len(positions) != 1:
        raise SystemExit(f"Expected one source occurrence of {phrase!r}, found {len(positions)}")
    return positions[0], positions[0] + len(phrase)


def write_atomic(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile(prefix=path.name + ".", suffix=".tmp", dir=path.parent, delete=False) as temp:
        temp.write(data)
        temp_path = Path(temp.name)
    temp_path.replace(path)


def add_ids(row: dict, ids: list[str]) -> None:
    values = row.setdefault("qualifiers", {}).setdefault("mentioned_candidate_ids", [])
    for candidate_id in ids:
        if candidate_id not in values:
            values.append(candidate_id)


def classify(row: dict, is_relation: bool, note: str, open_reason: str | None = None) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = is_relation
    qualifiers["relation_candidate_note"] = note
    if open_reason:
        qualifiers["open_endpoint_reason"] = open_reason
    else:
        qualifiers.pop("open_endpoint_reason", None)


def set_endpoints(row: dict, subject: str | None, predicate: str, obj: str | None) -> None:
    row["subject_candidate_id"] = subject
    row["predicate"] = predicate
    row["object_candidate_id"] = obj


def clone_relation(
    parent: dict,
    statement_id: str,
    subject: str | None,
    predicate: str,
    obj: str | None,
    claim: str,
    mentioned_ids: list[str],
    note: str,
    *,
    speaker: str | None = None,
    text_layer: str | None = None,
) -> dict:
    row = copy.deepcopy(parent)
    row["statement_id"] = statement_id
    set_endpoints(row, subject, predicate, obj)
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["claim"] = claim
    qualifiers["mentioned_candidate_ids"] = mentioned_ids
    qualifiers["relation_candidate"] = True
    qualifiers["relation_candidate_note"] = note
    if speaker is not None:
        qualifiers["speaker"] = speaker
    if text_layer is not None:
        qualifiers["text_layer"] = text_layer
    if predicate == "cites":
        qualifiers["cited_source_independently_consulted"] = False
    return row


def synchronize_note_links(rows: list[dict], segment_rows: list[dict]) -> None:
    groups: dict[tuple[object, object, object], list[str]] = {}
    prior_ids: dict[tuple[object, object, object], set[str]] = {}
    for row in segment_rows:
        q = row.get("qualifiers") or {}
        marker = q.get("footnote_marker")
        body_line = q.get("footnote_body_line_range")
        if marker is None or body_line is None:
            continue
        key = (q.get("printed_page"), marker, body_line)
        groups.setdefault(key, []).append(row["statement_id"])
        prior_ids.setdefault(key, set()).update(q.get("footnote_note_statement_ids") or [])

    for key, statement_ids in groups.items():
        ids = list(dict.fromkeys(statement_ids))
        old_ids = prior_ids.get(key, set())
        for row in rows:
            q = row.get("qualifiers") or {}
            linked = q.get("footnote_note_statement_ids")
            if linked is None:
                continue
            same_group = (q.get("printed_page"), q.get("footnote_marker"), q.get("footnote_body_line_range")) == key
            if same_group or old_ids.intersection(linked):
                q["footnote_note_statement_ids"] = ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize chapter 15 consolidated footnotes, lines 90-113.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="Validate and display planned edits without writing (default).")
    mode.add_argument("--apply", action="store_true", help="Apply after all source and table preconditions pass.")
    args = parser.parse_args()

    require_hashes()
    statement_rows = load_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_bom = load_csv(CANDIDATES)
    mention_fields, mention_rows, mention_bom = load_csv(MENTIONS)

    segment_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    by_id = {row["statement_id"]: row for row in segment_rows}
    if len(segment_rows) != 35:
        raise SystemExit(f"Expected 35 existing statements in the footnote segment, found {len(segment_rows)}")
    unset_ids = {row["statement_id"] for row in segment_rows if (row.get("qualifiers") or {}).get("relation_candidate") is None}
    if unset_ids != UNSET_IDS:
        raise SystemExit(f"Unset statement set changed: {sorted(unset_ids ^ UNSET_IDS)}")
    if sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in segment_rows) != 9:
        raise SystemExit("Expected 9 already-classified true statements")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is False for row in segment_rows):
        raise SystemExit("Unexpected pre-existing false classification in the segment")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row.get("candidate_id", "").startswith("cand-"))
    if max_candidate != 12250:
        raise SystemExit(f"Expected candidate ID ceiling 12250, found {max_candidate}")
    if any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
        raise SystemExit("A proposed candidate ID already exists")

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if any(spec[0] in mention_by_id for spec in NEW_MENTIONS):
        raise SystemExit("A proposed mention ID already exists")
    de_tipaldo_mention = mention_by_id.get("m-chp15-p371-querini-0050")
    if not de_tipaldo_mention or de_tipaldo_mention.get("candidate_id") != "cand-10451":
        raise SystemExit("The expected p.371 De Tipaldo mention mapping changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if len(source_lines) < SEGMENT_LINE_END or source_lines[89] != "**Footnotes:**":
        raise SystemExit("The consolidated footnote segment boundary changed")
    segment_text = "\n".join(source_lines[SEGMENT_LINE_START - 1:SEGMENT_LINE_END])
    mention_spans = [phrase_span(segment_text, spec[2]) for spec in NEW_MENTIONS]

    # Convert citation locators to explicit book -> source edges and preserve the citation context.
    citation_updates = {
        "st-chp15-p365-note1-brunelli-1923": ("cand-2962", "cites", "cand-9501", "Haskell's p.365 note 1 cites Brunelli (1923) for the preceding discussion; the cited work and cited passage were not independently consulted."),
        "st-chp15-p365-note2-radicchio-1786": ("cand-2962", "cites", "cand-10478", "Haskell directs readers to Radicchio (1786) for the history of the Prà della Valle; the short citation is not independently verified."),
        "st-chp15-p365-note2-neu-mayr-1807": ("cand-2962", "cites", "cand-10479", "The printed continuation of note 2 directs readers to Neu-Mayr (1807) for figures and inscriptions associated with the Prà della Valle; the work was not consulted."),
        "st-chp15-p367-note1-della-valle-quotation": ("cand-2962", "cites", "cand-10503", "Haskell reproduces and cites Della Valle, volume III, page 459; the cited work and the identity behind the locator remain unresolved."),
        "st-chp15-p368-note1-memmo-zaguri-reference": ("cand-2962", "cites", "cand-10475", "Haskell cites Molmenti's Un nobil huomo, pages 137 onward, for the p.368 discussion; the cited pages were not consulted."),
        "st-chp15-p368-note3-inventory-record": ("cand-2962", "cites", "cand-10514", "Haskell points to the 1792 Memmo-effects inventory in the Archivio di Stato, Venice, Petizion 488, and identifies its two dates; the archival record was not consulted."),
        "st-chp15-p368-note4-open-house-reference": ("cand-2962", "cites", "cand-10513", "Haskell cites Lorenzo da Ponte, page 52, for the p.368 account of Memmo's open house; the cited page was not consulted."),
        "st-chp15-p368-note6-elementi-reference": ("cand-2962", "cites", "cand-1647", "Haskell cites Memmo's 1786 Elementi, page 29 note 1, for the p.368 information about Lodoli's earlier years; the cited page was not consulted."),
        "st-chp15-p368-note7-1761-crisis-reference": ("cand-2962", "cites", "cand-10516", "Haskell cites Bozzola (1948), pages 93-116, for the p.368 account of the 1761 crisis; the article was not consulted."),
        "st-chp15-p369-note4-alticchiero-wynne-publication": ("cand-2962", "cites", "cand-10534", "Haskell cites Giustiniana Wynne-Rosenberg's Alticchiero, printed in Venice in 1787; a separate bibliography locator gives a conflicting place form, retained for S3."),
        "st-chp15-p370-note2-moschini-citation": ("cand-2962", "cites", "cand-10568", "Haskell cites G. A. Moschini (1806), volume II, page 116; the print reads II although the OCR reads H, and the cited page was not consulted."),
        "st-chp15-p372-note1-cites-brunelli-bonetti-1951": ("cand-2962", "cites", "cand-10515", "Haskell's p.372 note 1 cites Brunelli Bonetti (1951) for the immediately preceding account of Querini and the Renier bust; the article was not consulted."),
    }
    for statement_id, (subject, predicate, obj, claim) in citation_updates.items():
        row = by_id[statement_id]
        set_endpoints(row, subject, predicate, obj)
        row["qualifiers"]["claim"] = claim
        row["qualifiers"]["text_layer"] = "bibliographic citation"
        row["qualifiers"]["cited_source_independently_consulted"] = False
        add_ids(row, [obj])
        classify(row, True, "A bibliographic citation is an explicit source-to-work relation; preserve the page locator and do not imply independent consultation.")

    # Publication history and source-attributed claims in p.367.
    classify(by_id["st-chp15-p367-note1-elementi-first-volume-1786"], True, "Haskell explicitly says Memmo published only the first volume in 1786; this is a source-attributed publication-history claim.")
    classify(by_id["st-chp15-p367-note1-elementi-completion-1834"], True, "Haskell explicitly says Memmo completed the work before his death and the full two-volume edition appeared in 1834; keep the attribution to Haskell.")
    by_id["st-chp15-p367-note4-memmo-friends-citations"].update({"subject_candidate_id": "cand-2962", "predicate": "cites", "object_candidate_id": "cand-10475"})
    by_id["st-chp15-p367-note4-memmo-friends-citations"]["qualifiers"]["claim"] = "Haskell cites Molmenti's Un nobil huomo, pages 143-144, and separately directs readers to Torcellan (1963) for other examples of Memmo writing to friends."
    by_id["st-chp15-p367-note4-memmo-friends-citations"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-1642", "cand-10474", "cand-10475"]
    classify(by_id["st-chp15-p367-note4-memmo-friends-citations"], True, "The Molmenti citation is a distinct source relation; the Torcellan citation is recorded separately below.")

    # p.368 note 2 has an explicit but cautious referent; keep the destruction claim open.
    destruction = by_id["st-chp15-p368-note2-gallery-destruction"]
    destruction["qualifiers"]["claim"] = "The note says 'These' were destroyed about 1960. It follows the frescoed-gallery sentence, so the referent is linked cautiously to that decorative program rather than to the palace as a whole."
    classify(
        destruction,
        True,
        "The printed note follows the frescoed-gallery claim and makes a destruction assertion, but its plural 'These' does not identify a precise object boundary.",
        "The plural referent may be the frescoed decorations; the note does not say whether it means the frescoes, figures, or another part of the program.",
    )

    # The inventory note is split into the archive citation, its provenance, repository, and publication.
    inventory_row = by_id["st-chp15-p368-note3-inventory-record"]
    inventory_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-10514", "cand-10525", "cand-2773", "cand-8592", "cand-8532", "cand-8533"]
    classify(inventory_row, True, "Haskell explicitly points to this archival inventory; compiler, repository, dates, and partial publication are represented in separate atomic statements.")

    drawing_row = by_id["st-chp15-p368-note3-mengs-drawing-and-prints"]
    set_endpoints(drawing_row, "cand-10514", "lists_holy_family_drawing_by_mengs", "cand-10519")
    drawing_row["qualifiers"]["claim"] = "Haskell says the inventory includes a drawing of the Holy Family by Mengs."
    drawing_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-10514", "cand-10519", "cand-1652"]
    classify(drawing_row, True, "The note identifies one inventory-listed drawing; the separate claim about several hundred prints is atomized below.")

    # p.368 note 5: the object is the unnamed plan, not the Brenta River itself.
    flood_row = by_id["st-chp15-p368-note5-brenta-obstruction-reference"]
    set_endpoints(flood_row, "cand-2075", "accused_of_obstructing_flood_control_plans", "cand-12252")
    flood_row["qualifiers"]["claim"] = "Haskell reports that Querini was accused of obstructing plans to stop Brenta flooding because the plans threatened his garden."
    add_ids(flood_row, ["cand-12252"])
    classify(flood_row, True, "The source states an accusation, not an independently established act; the unnamed plans are represented as a source-bounded procedure candidate.")

    # The anonymous publication is both the reported source of the rumour and a citation target.
    voyages = by_id["st-chp15-p369-note1-anonymous-voyages-rumour-source"]
    set_endpoints(voyages, "cand-10527", "reports_authorship_rumour_in", "cand-10528")
    voyages["qualifiers"]["claim"] = "Haskell attributes the report of the 1764 authorship rumour to the anonymous author of Voyages, volume I, page 211."
    voyages["qualifiers"]["speaker"] = "Anonymous author of Voyages, as reported by Haskell"
    add_ids(voyages, ["cand-10527", "cand-10528"])
    classify(voyages, True, "The note explicitly attributes the report to the anonymous source; preserve the reported status of the authorship rumour.")

    # A bare surname in p.369 note 2 repeats the body locator and contributes no separate relation.
    classify(by_id["st-chp15-p369-note2-festari-reference"], False, "The note contains only 'Festari.'; the body already records Querini's 1777 journey with Girolamo Festari, so this locator adds no distinct relation.")

    # Correct the endpoints in Bernis's quotation and keep the ambassadorial succession separate.
    bernis = by_id["st-chp15-p369-note3-bernis-rosenberg-quotation"]
    set_endpoints(bernis, "cand-2259", "bernis_compares_rosenberg_with_prie_and_says_little_more_merit", "cand-10537")
    bernis["qualifiers"]["claim"] = "As quoted by Haskell, Cardinal de Bernis says Count Rosenberg had more birth, wit, and intrigue than the Marquis de Prié but scarcely more merit; Bernis calls Prié mediocre."
    bernis["qualifiers"]["speaker"] = "Cardinal de Bernis, as quoted by Haskell"
    add_ids(bernis, ["cand-10537", "cand-10536"])
    classify(bernis, True, "The quoted comparison is attributed to Bernis by Haskell; retain the source attribution and the unresolved historical identity of the Marquis de Prié.")

    # p.369 note 4: distinguish the article's subject from its author and from Haskell's citation.
    article = by_id["st-chp15-p369-note4-brunelli-article"]
    set_endpoints(article, "cand-10535", "discusses_and_illustrates_remains_of", "cand-0086")
    article["qualifiers"]["claim"] = "Haskell says the remains of Alticchiero are discussed and illustrated in Bruno Brunelli's 1931 article, pages 4-11."
    article["qualifiers"]["speaker"] = "Haskell's note"
    classify(article, True, "This statement is about what the cited article discusses and illustrates; the article's author is recorded separately.")
    classify(
        by_id["st-chp15-p369-note4-heraclitus-democritus-busts"],
        True,
        "Haskell reports that the busts were at Casa Soster at the time of Brunelli's 1931 article; this is not a claim about their present location.",
    )

    # p.370 inventory is a cited archival object; fix direction and retain owner/location separately.
    inventory_querini = by_id["st-chp15-p370-note1-querini-alticchiero-inventory"]
    set_endpoints(inventory_querini, "cand-2962", "cites", "cand-10567")
    inventory_querini["qualifiers"]["claim"] = "Haskell cites an unclassified inventory of Angelo Querini's effects at Alticchiero, published by C. A. Levi in volume II, page 255."
    add_ids(inventory_querini, ["cand-2075", "cand-0086", "cand-8532", "cand-8533"])
    classify(inventory_querini, True, "Haskell explicitly cites the inventory; its subject, location, and publication are represented as separate relationships.")

    # p.371 note 1: model contact with the three named individuals and keep their dedications separate.
    contact = by_id["st-chp15-p371-note1-antiquarians-dedicated-books-to-querini"]
    set_endpoints(contact, "cand-2075", "was_in_contact_with", "cand-0372")
    contact["qualifiers"]["claim"] = "Haskell says Querini was in touch with antiquarians and neo-classicists including Isidoro Bianchi, Francesco Milizia, and Jacopo Morelli; the three dedication claims are recorded separately."
    classify(contact, True, "The note explicitly reports contact with the named examples; the group is not treated as a formal organization.")

    # De Tipaldo in p.371 note 2 refers to the 10-volume Biografia, not the unrelated 1833 villa book.
    de_non = by_id["st-chp15-p371-note2-de-non-citation-chain"]
    set_endpoints(de_non, "cand-2962", "cites", "cand-11439")
    de_non["qualifiers"]["claim"] = "Haskell directs readers to De Tipaldo's Biografia for De Non's relationship with Querini; the note gives no volume or page, and the work was not consulted."
    de_non["qualifiers"]["mentioned_candidate_ids"] = ["cand-1752", "cand-11439"]
    classify(de_non, True, "The p.371 note concerns De Non and maps to the multi-volume Biografia bibliography entry; keep it separate from De Tipaldo's unrelated 1833 villa publication.")
    de_tipaldo_mention["candidate_id"] = "cand-11439"
    de_tipaldo_mention["note"] = "The p.371 De Tipaldo citation for De Non maps to the Biografia degli Italiani illustri bibliography entry, not the unrelated 1833 Descrizione della villa di Sala cited on p.363; no volume or page is supplied here."

    # Add exact-span candidates and mentions.
    for candidate in NEW_CANDIDATES:
        candidate_rows.append({field: candidate.get(field, "") for field in candidate_fields})
    for spec, span in zip(NEW_MENTIONS, mention_spans):
        mention_id, candidate_id, surface_form, note = spec
        mention_rows.append(
            {
                "mention_id": mention_id,
                "segment_id": SEGMENT_ID,
                "candidate_id": candidate_id,
                "surface_form": surface_form,
                "start_char": str(span[0]),
                "end_char": str(span[1]),
                "note": note,
            }
        )

    # Add new source, ownership, location, publication, and contact relationships.
    extras = [
        ("st-chp15-p367-note2-cites-apologhi-1787", "st-chp15-p367-note2-apologhi-publication-1787", "cand-2962", "cites", "cand-1413", "Haskell's p.367 note 2 gives the full title and Bassano [Remondini], 1787 imprint of the Apologhi.", ["cand-1413", "cand-1411", "cand-1642"], "The note identifies the publication as a cited source; its printed title and imprint are not independently verified.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p367-note3-cites-memmo-oration-1787", "st-chp15-p367-note3-memmo-panegyric-1787", "cand-2962", "cites", "cand-10505", "Haskell's p.367 note 3 identifies the 1787 oration for Memmo's solemn entry as Procurator di San Marco.", ["cand-10505", "cand-1642", "cand-8449", "cand-2719", "cand-2865"], "This is the book-to-document citation; the oration's relation to Memmo's entry is recorded separately.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p367-note4-cites-torcellan-1963", "st-chp15-p367-note4-memmo-friends-citations", "cand-2962", "cites", "cand-10476", "Haskell directs readers to Torcellan (1963) for other examples of Memmo writing to friends.", ["cand-1642", "cand-10476"], "The Torcellan reference is a separate citation from the Molmenti pages 143-144 citation.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p368-note2-cites-fontana-p142", "st-chp15-p368-note2-gallery-destruction", "cand-2962", "cites", "cand-10512", "Haskell cites Fontana, page 142, after the p.368 frescoed-gallery passage.", ["cand-10512", "cand-10518"], "The short-form citation is retained as a source locator; the cited work and page were not consulted.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p368-note3-cites-levi-volume-ii-p254", "st-chp15-p368-note3-inventory-record", "cand-2962", "cites", "cand-8533", "Haskell says part of the Petizion 488 inventory is published by Levi, volume II, page 254.", ["cand-10514", "cand-8532", "cand-8533"], "The Levi volume is a separate publication from the underlying archival inventory; neither was consulted.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p368-note3-inventory-drawn-up-by-sasso", "st-chp15-p368-note3-inventory-record", "cand-10514", "drawn_up_by", "cand-10525", "Haskell identifies Sasso as one of the persons who drew up the 1792 Memmo-effects inventory.", ["cand-10514", "cand-10525"], "This is a source-reported compiler attribution; Sasso is identified only by surname and the inventory was not consulted.", "Haskell's note", "archive attribution"),
        ("st-chp15-p368-note3-inventory-drawn-up-by-viero", "st-chp15-p368-note3-inventory-record", "cand-10514", "drawn_up_by", "cand-2773", "Haskell identifies Viero as one of the persons who drew up the 1792 Memmo-effects inventory.", ["cand-10514", "cand-2773"], "This is a source-reported compiler attribution; the inventory was not consulted.", "Haskell's note", "archive attribution"),
        ("st-chp15-p368-note3-inventory-held-by-state-archive", "st-chp15-p368-note3-inventory-record", "cand-10514", "held_by", "cand-8592", "Haskell locates the Petizion 488 inventory in the Archivio di Stato, Venice.", ["cand-10514", "cand-8592"], "The repository is reported by Haskell; the archival record was not consulted.", "Haskell's note", "archive attribution"),
        ("st-chp15-p368-note3-inventory-partly-published-in-levi", "st-chp15-p368-note3-inventory-record", "cand-10514", "partially_published_in", "cand-8533", "Haskell says part of the Petizion 488 inventory was published in Levi, volume II, page 254.", ["cand-10514", "cand-8533"], "The relation is limited to the portion Haskell says was published; the archival inventory and Levi volume were not consulted.", "Haskell's note", "publication relation"),
        ("st-chp15-p368-note3-memmo-owned-several-hundred-prints", "st-chp15-p368-note3-mengs-drawing-and-prints", "cand-12251", "owned_by", "cand-1642", "Haskell says Andrea Memmo also owned several hundred prints, with the artist rarely indicated.", ["cand-12251", "cand-1642"], "The prints are kept as one source-bounded group because no individual print or artist is identified.", "Haskell's note", "collection report"),
        ("st-chp15-p368-note5-cites-brunelli-bonetti-1951", "st-chp15-p368-note5-brenta-obstruction-reference", "cand-2962", "cites", "cand-10515", "Haskell cites Brunelli Bonetti (1951), pages 185-200, for the report that Querini was accused of obstructing Brenta flood-control plans.", ["cand-2075", "cand-10520", "cand-10515"], "The cited article is a source locator; its contents were not independently checked.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p369-note1-cites-voyages-1777", "st-chp15-p369-note1-anonymous-voyages-rumour-source", "cand-2962", "cites", "cand-10528", "Haskell cites Voyages, volume I, page 211, as the source reporting the 1764 authorship rumour.", ["cand-10527", "cand-10528"], "The edition and cited passage were not independently consulted; the author remains anonymous.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p369-note1-voyages-authored-anonymously", "st-chp15-p369-note1-anonymous-voyages-rumour-source", "cand-10528", "authored_by", "cand-10527", "Haskell identifies the author of the 1777 Voyages as anonymous.", ["cand-10527", "cand-10528"], "This preserves only the anonymous author role attributed by Haskell; no identity is inferred.", "Haskell's note", "source attribution"),
        ("st-chp15-p369-note3-rosenberg-succeeded-prie", "st-chp15-p369-note3-bernis-rosenberg-quotation", "cand-2259", "succeeded_as_imperial_ambassador", "cand-10537", "Haskell's bracketed gloss identifies the Marquis de Prié as the Imperial Ambassador whom Count Rosenberg succeeded.", ["cand-2259", "cand-10537", "cand-8801", "cand-10536"], "The succession is stated through Haskell's bracketed clarification of the pronoun in Bernis's quotation.", "Haskell's note quoting Bernis", "quoted succession"),
        ("st-chp15-p369-note3-cites-memoires-et-lettres", "st-chp15-p369-note3-bernis-rosenberg-quotation", "cand-2962", "cites", "cand-10536", "Haskell cites Mémoires et Lettres, volume I, page 166, for the passage attributed to Cardinal de Bernis.", ["cand-8801", "cand-10536", "cand-2259", "cand-10537"], "The quoted source and page were not independently consulted.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p369-note3-memoires-passage-attributed-to-bernis", "st-chp15-p369-note3-bernis-rosenberg-quotation", "cand-10536", "contains_passage_attributed_to", "cand-8801", "Haskell attributes the passage cited to Mémoires et Lettres, volume I, page 166, to Cardinal de Bernis.", ["cand-10536", "cand-8801"], "This records Haskell's attribution of the cited passage; it does not independently verify the source text.", "Haskell's note", "source attribution"),
        ("st-chp15-p369-note4-cites-alticchiero-1787", "st-chp15-p369-note4-alticchiero-wynne-publication", "cand-2962", "cites", "cand-10534", "Haskell cites Giustiniana Wynne-Rosenberg's Alticchiero, Venice, 1787.", ["cand-2824", "cand-10534"], "Haskell's place form is retained; the bibliography has a conflicting place form, and the work was not consulted.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p369-note4-cites-brunelli-article", "st-chp15-p369-note4-brunelli-article", "cand-2962", "cites", "cand-10535", "Haskell cites Bruno Brunelli's 1931 article, pages 4-11, on the remains of Alticchiero.", ["cand-9502", "cand-10535", "cand-0086"], "The article is not independently consulted; its stated subject and author are recorded separately.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p369-note4-brunelli-article-authored-by-brunelli", "st-chp15-p369-note4-brunelli-article", "cand-10535", "authored_by", "cand-9502", "Haskell identifies the 1931 article on Alticchiero as by Bruno Brunelli.", ["cand-10535", "cand-9502"], "The author is reported by Haskell; the article itself was not consulted.", "Haskell's note", "source attribution"),
        ("st-chp15-p369-note4-alticchiero-authored-by-wynne", "st-chp15-p369-note4-alticchiero-wynne-publication", "cand-10534", "authored_by", "cand-2824", "Haskell's citation names Giustiniana Wynne-Rosenberg as the author of Alticchiero.", ["cand-10534", "cand-2824"], "The author and title are transcribed from Haskell's note; the edition was not independently consulted.", "Haskell's note", "source attribution"),
        ("st-chp15-p370-note1-cites-levi-volume-ii-p255", "st-chp15-p370-note1-querini-alticchiero-inventory", "cand-2962", "cites", "cand-8533", "Haskell cites Levi, volume II, page 255, for the inventory of Querini's effects at Alticchiero.", ["cand-8532", "cand-8533", "cand-10567"], "The locator matches the Levi volume cited at p.368 note 3, page 254; the volume was not consulted.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p370-note1-inventory-of-querini-effects", "st-chp15-p370-note1-querini-alticchiero-inventory", "cand-10567", "inventory_of_effects_of", "cand-2075", "Haskell describes the cited inventory as an inventory of Angelo Querini's effects.", ["cand-10567", "cand-2075"], "This is the archive-to-person relation stated by Haskell; the inventory was not consulted.", "Haskell's note", "archive content"),
        ("st-chp15-p370-note1-inventory-records-alticchiero", "st-chp15-p370-note1-querini-alticchiero-inventory", "cand-10567", "records_effects_at", "cand-0086", "Haskell identifies the inventory as concerning Querini's effects at Alticchiero.", ["cand-10567", "cand-0086"], "This is limited to the location stated in Haskell's citation; the inventory was not consulted.", "Haskell's note", "archive content"),
        ("st-chp15-p370-note1-inventory-published-in-levi", "st-chp15-p370-note1-querini-alticchiero-inventory", "cand-10567", "published_in", "cand-8533", "Haskell says the inventory was published by Levi, volume II, page 255.", ["cand-10567", "cand-8532", "cand-8533"], "The cited publication is the Levi volume identified from the adjacent p.254 reference; it was not consulted.", "Haskell's note", "publication relation"),
        ("st-chp15-p371-note1-querini-contact-with-milizia", "st-chp15-p371-note1-antiquarians-dedicated-books-to-querini", "cand-2075", "was_in_contact_with", "cand-10589", "Haskell names Francesco Milizia among the antiquarians and neo-classicists with whom Querini was in touch.", ["cand-2075", "cand-10589"], "The contact is source-reported; the specific books or monographs attributed to Milizia are not identified.", "Haskell's note", "relation report"),
        ("st-chp15-p371-note1-querini-contact-with-morelli", "st-chp15-p371-note1-antiquarians-dedicated-books-to-querini", "cand-2075", "was_in_contact_with", "cand-10590", "Haskell names Jacopo Morelli among the antiquarians and neo-classicists with whom Querini was in touch.", ["cand-2075", "cand-10590"], "The contact is source-reported; the specific books or monographs attributed to Morelli are not identified.", "Haskell's note", "relation report"),
        ("st-chp15-p371-note2-cites-moschini-1924", "st-chp15-p371-note2-de-non-citation-chain", "cand-2962", "cites", "cand-10587", "Haskell cites G. A. Moschini (1924) for De Non; the cited title is not supplied in the note.", ["cand-1752", "cand-1709", "cand-10587"], "Citation locator only; the work and cited passage were not independently checked.", "Haskell's note", "bibliographic citation"),
        ("st-chp15-p371-note2-cites-pallucchini-1941", "st-chp15-p371-note2-de-non-citation-chain", "cand-2962", "cites", "cand-10588", "Haskell cites Pallucchini's Mostra degli Incisori Veneti del Settecento (1941), page 112, for De Non.", ["cand-1752", "cand-10319", "cand-10588"], "The catalogue and cited page were not independently consulted.", "Haskell's note", "bibliographic citation"),
    ]

    new_statement_ids = [spec[0] for spec in extras]
    existing_statement_ids = {row["statement_id"] for row in statement_rows}
    if existing_statement_ids.intersection(new_statement_ids):
        raise SystemExit("A proposed statement ID already exists")
    for spec in extras:
        statement_id, parent_id, subject, predicate, obj, claim, mentioned_ids, note, speaker, text_layer = spec
        if parent_id not in by_id:
            raise SystemExit(f"Missing parent statement for {statement_id}: {parent_id}")
        row = clone_relation(by_id[parent_id], statement_id, subject, predicate, obj, claim, mentioned_ids, note, speaker=speaker, text_layer=text_layer)
        statement_rows.append(row)
        by_id[statement_id] = row

    # Add the Torcellan citation as a separate source edge and keep the original Molmenti citation atomic.
    # The De Tipaldo mention and statement were corrected above using the bibliography's distinct 10-volume work.

    # Synchronize each split note with its body statements so note-marker links remain complete.
    segment_after = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    synchronize_note_links(statement_rows, segment_after)

    # Rebuild lookup sets and validate all newly introduced foreign keys and exact spans.
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    for row in statement_rows:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        q = row.get("qualifiers") or {}
        for candidate_id in q.get("mentioned_candidate_ids") or []:
            if candidate_id not in candidate_by_id:
                raise SystemExit(f"Unknown mentioned candidate {candidate_id} in {row['statement_id']}")
        for field in ("subject_candidate_id", "object_candidate_id"):
            candidate_id = row.get(field)
            if candidate_id is not None and candidate_id not in candidate_by_id:
                raise SystemExit(f"Unknown {field} {candidate_id} in {row['statement_id']}")
    for spec, span in zip(NEW_MENTIONS, mention_spans):
        mention_id, candidate_id, phrase, _ = spec
        row = mention_by_id[mention_id]
        if row["candidate_id"] != candidate_id or int(row["start_char"]) != span[0] or int(row["end_char"]) != span[1]:
            raise SystemExit(f"New mention validation failed: {mention_id}")

    segment_after = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    true_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in segment_after)
    false_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in segment_after)
    unset_count = sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in segment_after)
    if (len(segment_after), true_count, false_count, unset_count) != (63, 62, 1, 0):
        raise SystemExit(f"Unexpected segment result: {len(segment_after)} statements, {true_count} true, {false_count} false, {unset_count} unset")

    print(f"Segment: {SEGMENT_ID}")
    print(f"Classified the {len(UNSET_IDS)} remaining original statements; atomized source relations and added {len(extras)} statements.")
    print(f"After: {len(segment_after)} statements ({true_count} true, {false_count} false, {unset_count} unset).")
    print("New candidates:")
    for row in NEW_CANDIDATES:
        print(f"  {row['candidate_id']} [{row['suggested_type']}]: {row['canonical_name']}")
    print("New exact-span mentions:")
    for spec, span in zip(NEW_MENTIONS, mention_spans):
        print(f"  {spec[0]} -> {spec[1]}: {spec[2]!r} [{span[0]},{span[1]})")
    print("Correction: p.371 note 2 De Tipaldo mention now maps to cand-11439, the bibliography's 10-volume Biografia, not p.363's 1833 villa publication cand-10451.")

    if not args.apply:
        print("PREVIEW ONLY; no files written.")
        return

    backup_suffix = ".bak-s2-ch15-notes-classification-20261015"
    targets = [STATEMENTS, CANDIDATES, MENTIONS]
    backups = [path.with_name(path.name + backup_suffix) for path in targets]
    if any(path.exists() for path in backups):
        raise SystemExit("A recovery backup already exists; inspect it before applying")
    payloads = {
        STATEMENTS: encode_jsonl(statement_rows),
        CANDIDATES: encode_csv(candidate_fields, candidate_rows, candidate_bom),
        MENTIONS: encode_csv(mention_fields, mention_rows, mention_bom),
    }
    try:
        for source, backup in zip(targets, backups):
            shutil.copy2(source, backup)
        for path, data in payloads.items():
            write_atomic(path, data)
    except Exception:
        for source, backup in zip(targets, backups):
            if backup.exists():
                shutil.copy2(backup, source)
        raise
    print("APPLIED. Recovery copies:")
    for path in backups:
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
