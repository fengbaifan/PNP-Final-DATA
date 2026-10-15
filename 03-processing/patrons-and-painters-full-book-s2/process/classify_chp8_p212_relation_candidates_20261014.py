"""Classify p.212 S2 statements, split mixed claims, and repair mappings."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l98-106"
SEGMENT_SHA = "948fd4e29bdb94c2c371da037d8350d05d3ea8d98e8757acb228d43700d6cd99"
BACKUP_SUFFIX = ".bak-s2-chp8-p212-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "353aa2fc422652e787e7b607ba2cb6d4fee09d89d38bfbe66649ca2365a6e19a",
    CANDIDATES: "73fbc688e68fc74b01b8ac3f91f6233a0edec61b91d3564104e1c778c04ae4e8",
    MENTIONS: "184eef6a7b96e41701dcab0d432eec20b9bdad466e7525773e428b298ef1b603",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
}
NEW_CANDIDATE = (
    "cand-12051",
    "Unidentified Del Rosso pictures acquired through Luca Giordano",
    "work",
    "Haskell says many pictures belonging to the Del Rosso family were acquired through Giordano. The individual works and count are not supplied; this group is distinct from works painted by Giordano.",
    105,
)
NEW_MENTION_ID = "m-chp8-p212-090"
NEW_STATEMENT_IDS = {
    "st-chp8-p212-lorenzo-may-have-started-career-naples",
    "st-chp8-p212-four-scenes-considered-vanninis-finest-works",
    "st-chp8-p212-one-section-florentine-painting-provincial-backwater",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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
    parser.add_argument("--apply", action="store_true", help="write after all preconditions and dry-run checks pass")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a table, source, or page image changed since the p.212 review baseline")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[97:106])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("p.212 S0 segment changed since review")
    segment_rows = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segment_rows.get(SEGMENT_ID)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 98, 106, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("p.212 segment manifest does not match the reviewed source")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_statement = {row["statement_id"]: row for row in statements}
    by_candidate = {row["candidate_id"]: row for row in candidates}
    by_mention = {row["mention_id"]: row for row in mentions}
    if len(by_statement) != len(statements) or len(by_candidate) != len(candidates) or len(by_mention) != len(mentions):
        raise SystemExit("statement, candidate, or mention identifiers are not unique")

    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if len(page_rows) != 24 or unset != {row["statement_id"] for row in page_rows}:
        raise SystemExit(f"unexpected p.212 inventory: rows={len(page_rows)}, unset={len(unset)}")
    if NEW_STATEMENT_IDS & set(by_statement) or NEW_MENTION_ID in by_mention:
        raise SystemExit("a planned p.212 identifier already exists")
    if NEW_CANDIDATE[0] in by_candidate or max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12050:
        raise SystemExit("candidate sequence changed since the reviewed p.212 baseline")

    target = by_mention.get("m-chp8-p212-061")
    if not target or (target["candidate_id"], target["surface_form"]) != ("cand-7489", "their"):
        raise SystemExit("the p.212 family-pronoun mention changed since review")
    letter = by_statement["st-chp8-p212-1613-grand-duke-letter-about-antonio-sons"]
    expected_bad_correction = {
        "source_line": 103,
        "ocr": "heirs ' of",
        "print": "heirs of",
        "basis": "CHP-8.pdf physical page 10; the quotation continues across the source line.",
    }
    if expected_bad_correction not in (letter.get("qualifiers", {}).get("ocr_corrections") or []):
        raise SystemExit("the p.212 quoted punctuation correction differs from the reviewed prestate")

    candidates.append({
        "candidate_id": NEW_CANDIDATE[0], "index_entry_id": "", "canonical_name": NEW_CANDIDATE[1],
        "index_page_range": "", "suggested_type": NEW_CANDIDATE[2], "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": NEW_CANDIDATE[3], "exclude_reason": "",
        "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT_ID}#L{NEW_CANDIDATE[4]}",
    })

    phrase = "their pictures"
    start = segment_text.find(phrase)
    if start < 0 or segment_text.find(phrase, start + 1) >= 0:
        raise SystemExit("the p.212 'their pictures' mention is missing or repeated")
    end = start + len(phrase)
    if segment_text[start:end] != phrase:
        raise SystemExit("new p.212 work-group mention does not match its source offsets")
    for row in mentions:
        if row["segment_id"] != SEGMENT_ID:
            continue
        other_start, other_end = int(row["start_char"]), int(row["end_char"])
        overlaps = start < other_end and end > other_start
        if overlaps and row["mention_id"] != "m-chp8-p212-061":
            contained = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not contained:
                raise SystemExit(f"new work-group mention overlaps {row['mention_id']} without nesting")
    mentions.append({
        "mention_id": NEW_MENTION_ID, "segment_id": SEGMENT_ID, "candidate_id": NEW_CANDIDATE[0],
        "surface_form": phrase, "start_char": str(start), "end_char": str(end),
        "note": "Unidentified family pictures described as acquired through Giordano; distinct from works painted by him.",
    })

    def excerpt(first: str, last: str) -> str:
        start_at, end_at = segment_text.find(first), segment_text.rfind(last)
        if start_at < 0 or end_at < start_at:
            raise SystemExit(f"expected p.212 source excerpt missing: {first!r} ... {last!r}")
        return segment_text[start_at:end_at + len(last)]

    def update(statement_id: str, relation: bool, note: str, **changes) -> None:
        row = by_statement[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        for key, value in changes.pop("qualifier_changes", {}).items():
            if value is None:
                q.pop(key, None)
            else:
                q[key] = value
        q.update(changes.pop("qualifiers", {}))
        row["qualifiers"] = q
        row.update(changes)

    # The apostrophe after "heirs" closes the source's quotation; it is not an OCR error.
    letter_q = dict(letter["qualifiers"])
    letter_q["ocr_corrections"] = [
        item for item in letter_q.get("ocr_corrections", []) if item != expected_bad_correction
    ]
    if not letter_q["ocr_corrections"]:
        letter_q.pop("ocr_corrections")
    letter["qualifiers"] = letter_q

    update(
        "st-chp8-p212-1613-grand-duke-letter-about-antonio-sons", True,
        "Haskell reports a 1613 letter from the Grand Duke to the Spanish Viceroy and quotes its reference to Antonio del Rosso's unnamed sons and heirs; the note gives a Florence archive locator, not an independent document reading.",
        predicate="grand_duke_wrote_viceroy_in_1613_about_antonio_del_rosso_sons_and_heirs",
        claim="Haskell reports that in 1613 the Grand Duke of Tuscany wrote to the Spanish Viceroy about some subjects, quoting the sons and heirs of Antonio del Rosso as Florentines living and trading in Naples.",
        qualification="The Viceroy is identified only by office. The plural sons and heirs remain unnamed and are not equated with Andrea and Lorenzo; the archival document has not been independently consulted.",
        original_quote=excerpt("In 1613, for instance", "living and trading in Naples"),
        mentioned_candidate_ids=["cand-7538", "cand-6232", "cand-7539", "cand-7541", "cand-7540", "cand-1041", "cand-3534"],
    )
    update(
        "st-chp8-p212-altar-picture-left-for-pupil-completion", True,
        "Haskell reports that Vannini left the chapel altar picture for a pupil to complete; the pupil is unnamed.",
        predicate="vannini_left_altar_picture_for_pupil_to_complete",
    )
    update(
        "st-chp8-p212-andrea-and-lorenzo-may-have-started-careers-in-naples", True,
        "This is Haskell's explicitly modal possibility, split by named person; it is not a confirmed career history.",
        predicate="andrea_may_have_started_career_in_naples",
        subject_candidate_id="cand-2275", object_candidate_id="cand-3534",
        claim="Haskell says it is perfectly possible that Andrea del Rosso may have started his career in Naples.",
        original_quote=excerpt("it is perfectly possible that Andrea and Lorenzo", "that city"),
        qualification="The source presents this as a possibility. The 1613 report about Antonio's unnamed sons and heirs is not used to identify Andrea.",
        mentioned_candidate_ids=["cand-2275", "cand-2282", "cand-7489", "cand-3534"],
    )
    update(
        "st-chp8-p212-business-connections-probably-outweighed-taste", False,
        "This is Haskell's qualified causal interpretation of a collecting shift; it names no particular business partner or transaction.",
        object_candidate_id=None,
        qualification="Haskell says taste alone is unlikely to explain the shift and business connections were probably more important; this remains an attributed interpretation.",
    )
    update(
        "st-chp8-p212-carlo-dolci-painted-for-del-rosso-family", True,
        "Haskell explicitly reports that Carlo Dolci painted for the Del Rosso family.",
        predicate="carlo_dolci_painted_for_del_rosso_family",
    )
    update(
        "st-chp8-p212-chapel-decorated-with-vannini-frescoes", True,
        "Haskell identifies Ottavio Vannini as the painter of frescoes decorating the family chapel.",
        predicate="vannini_painted_frescoes_for_del_rosso_family_chapel",
    )
    update(
        "st-chp8-p212-corsini-commission-in-turn-led-to-palazzo-riccardi-frescoes", True,
        "Haskell states that the Corsini chapel commission led in turn to Giordano's frescoes in Palazzo Riccardi; retain this reported causal sequence.",
    )
    update(
        "st-chp8-p212-family-already-owned-several-giordano-works", True,
        "Haskell says the family already owned a number of Giordano's works before his 1679 visit; the statement does not assign the later total of more than sixty to the earlier date.",
        predicate="del_rosso_family_owned_giordano_works_before_1679_visit",
        qualification="The number owned before the visit is unspecified; the passage separately says more than sixty Giordano pictures were among the holdings overall.",
    )
    update(
        "st-chp8-p212-family-may-have-arranged-corsini-chapel-commission", True,
        "Haskell says it may well have been the brothers who arranged the commission; preserve this uncertainty and do not treat them as established commissioners.",
        qualification="This is a qualified attribution by Haskell, not a confirmed commission record.",
    )
    update(
        "st-chp8-p212-family-owned-original-bozzetto-for-chapel-pendentive", True,
        "Haskell says the brothers certainly owned the original bozzetto for one chapel pendentive; the maker and corresponding finished image are not identified here.",
    )
    update(
        "st-chp8-p212-four-scenes-made-for-house-and-considered-finest", True,
        "Haskell identifies four Old Testament scenes as works Vannini produced for the Del Rosso house; the separate ranking of them as his finest works is retained in its own attributed statement.",
        predicate="vannini_produced_four_named_old_testament_scenes_for_del_rosso_house",
        claim="Haskell says Vannini produced four large Old Testament scenes for the Del Rosso house: The Sacrifice of Isaac, The Fall of Manna, Moses striking the Rock, and Susanna and the Elders.",
        original_quote=excerpt("the four large scenes from the Old Testament", "which he produced for the house"),
        qualification="The four titles are represented as individual work candidates within one unidentified group; the source does not give their later location.",
        mentioned_candidate_ids=["cand-2694", "cand-7527", "cand-7528", "cand-7529", "cand-7530", "cand-7531", "cand-7543"],
    )
    update(
        "st-chp8-p212-giordano-pictures-included-many-erotic-works-open", True,
        "This p.212 sentence continues on p.213; the cross-page link identifies the example and further subjects without treating the unfinished phrase as complete on p.212.",
    )
    update(
        "st-chp8-p212-giordano-visited-florence-and-stayed-at-family-house-1679", True,
        "Haskell reports Giordano's 1679 visit to Florence and stay at the family's house; the house is not explicitly identified here with the Via Chiara residence mentioned earlier.",
        predicate="giordano_visited_florence_and_stayed_at_del_rosso_family_house_in_1679",
    )
    update(
        "st-chp8-p212-grandfather-andrea-built-chapel", True,
        "This clause completes the p.211 sentence about the brothers' grandfather; it identifies Andrea and the chapel built for his name-saint.",
        predicate="grandfather_andrea_had_family_chapel_built_for_his_name_saint",
        qualifier_changes={"continues_statement_id": "st-chp8-p211-forebears-grandfather-open"},
    )
    update(
        "st-chp8-p212-links-with-naples-in-family-history", False,
        "This is Haskell's broad transition that links with Naples recur in the family history; the specific actors and relations are stated separately where the text identifies them.",
    )
    update(
        "st-chp8-p212-luca-giordano-family-relationship-close", True,
        "Haskell explicitly characterizes the relationship between Giordano and the Del Rosso family as particularly close.",
    )
    update(
        "st-chp8-p212-luca-giordano-principal-agent-in-naples", True,
        "Haskell identifies Giordano as the family's principal artistic agent in Naples.",
        predicate="luca_giordano_was_del_rosso_familys_principal_artistic_agent_in_naples",
    )
    update(
        "st-chp8-p212-many-family-pictures-acquired-through-giordano", True,
        "Haskell says many pictures belonging to the Del Rosso family were acquired through Giordano; the individual works are not named and are distinct from the Giordano-authored works counted separately.",
        predicate="many_del_rosso_family_pictures_acquired_through_giordano",
        subject_candidate_id="cand-7489", object_candidate_id=NEW_CANDIDATE[0],
        claim="Haskell says many of the Del Rosso family's pictures were acquired through Luca Giordano.",
        qualification="The pictures are unidentified; 'through Giordano' describes the acquisition route and does not establish that he painted every work.",
        original_quote=excerpt("Many of their pictures", "acquired through him"),
        mentioned_candidate_ids=["cand-7489", NEW_CANDIDATE[0], "cand-1172"],
    )
    update(
        "st-chp8-p212-more-than-sixty-by-luca-giordano", True,
        "Haskell says more than sixty of the over one hundred Neapolitan pictures were by Luca Giordano; the lower-bound count applies to the represented group overall, not to the pre-1679 subset.",
    )
    update(
        "st-chp8-p212-other-vannini-pictures-owned-by-family", True,
        "Haskell reports that the family owned many other pictures by Vannini, mainly of saints; no individual titles are supplied.",
    )
    update(
        "st-chp8-p212-over-hundred-neapolitan-pictures-introduced", True,
        "Haskell reports that the new generation introduced over one hundred Neapolitan pictures into the household; do not infer that all were acquired through one route.",
    )
    update(
        "st-chp8-p212-some-pictures-came-from-roomer-collection", True,
        "Haskell says an unspecified subset came from the Roomer collection after its dispersal in 1674; neither count nor individual works are given.",
    )
    update(
        "st-chp8-p212-vannini-died-a-year-later", False,
        "This is an isolated relative-date biographical detail, not a relation needed for the current S2 knowledge claims; preserve Haskell's wording without inferring an exact death year.",
        qualification="The source says 'a year later' after the chapel account but gives no absolute date in this passage.",
    )
    update(
        "st-chp8-p212-vannini-style-and-florentine-disegno-assessment", True,
        "The statement is narrowed to Haskell's description of Vannini as a methodical, correct, academic artist in the Florentine disegno tradition; the provincial-backwater judgment about one section of city painting is split out.",
        predicate="haskell_characterizes_vannini_as_methodical_academic_artist_in_florentine_disegno_tradition",
        claim="Haskell characterizes Vannini as a methodical, correct and academic artist in the Florentine disegno tradition.",
        original_quote=excerpt("He was a methodical", "Florentine \u2018disegno\u2019"),
        qualification="This is Haskell's description of Vannini's artistic manner; the passage's separate judgment about one section of Florentine painting is not generalized to all Florentine art.",
        mentioned_candidate_ids=["cand-2694", "cand-7533", "cand-1041"],
    )

    def make_statement(statement_id: str, predicate: str, subject: str | None, obj: str | None,
                       claim: str, quote: str, start_line: int, end_line: int, mentioned: list[str],
                       relation: bool, note: str, qualification: str) -> dict:
        return {
            "statement_id": statement_id, "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
            "qualifiers": {
                "source_line_start": start_line, "source_line_end": end_line,
                "printed_page": 212, "pdf_physical_page": 10, "claim": claim,
                "speaker": "Haskell", "text_layer": "body", "qualification": qualification,
                "mentioned_candidate_ids": mentioned, "relation_candidate": relation,
                "relation_candidate_note": note,
            },
            "original_quote": quote, "origin": "book", "source_file": SOURCE_REL,
        }

    statements.extend([
        make_statement(
            "st-chp8-p212-lorenzo-may-have-started-career-naples",
            "lorenzo_may_have_started_career_in_naples", "cand-2282", "cand-3534",
            "Haskell says it is perfectly possible that Lorenzo del Rosso may have started his career in Naples.",
            excerpt("it is perfectly possible that Andrea and Lorenzo", "that city"), 103, 103,
            ["cand-2282", "cand-2275", "cand-7489", "cand-3534"], True,
            "This is Haskell's explicitly modal possibility, split by named person; it is not a confirmed career history.",
            "The source presents this as a possibility. The 1613 report about Antonio's unnamed sons and heirs is not used to identify Lorenzo.",
        ),
        make_statement(
            "st-chp8-p212-four-scenes-considered-vanninis-finest-works",
            "haskell_reports_four_vannini_scenes_were_considered_his_finest_works", "cand-2694", "cand-7527",
            "Haskell says the four named Old Testament scenes were considered Vannini's finest works.",
            excerpt("which he produced for the house were considered his finest works", "were considered his finest works"),
            101, 101, ["cand-2694", "cand-7527"], False,
            "This is an attributed quality ranking with no evaluator identified in the passive wording; preserve it as Haskell's report rather than a formal relation.",
            "The statement refers to the four scenes named in the adjacent p.212 statement; it does not independently establish a comparative assessment.",
        ),
        make_statement(
            "st-chp8-p212-one-section-florentine-painting-provincial-backwater",
            "haskell_describes_one_section_of_florentine_painting_as_provincial_backwater", None, None,
            "Haskell describes one section of Florentine painting as a provincial backwater in the first half of the seventeenth century.",
            excerpt("characteristic in every way of the provincial backwater", "first half of the seventeenth century"),
            101, 101, ["cand-1041", "cand-7533"], False,
            "This is Haskell's evaluative characterization of one section of Florentine painting, not a discrete relation or a judgment about all Florentine art.",
            "The temporal scope is the first half of the seventeenth century; 'one section' limits the claim.",
        ),
    ])

    changed_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(changed_rows) != 27 or any("relation_candidate" not in row.get("qualifiers", {}) for row in changed_rows):
        raise SystemExit("the updated p.212 statement inventory is incomplete")
    if by_statement["st-chp8-p212-giordano-pictures-included-many-erotic-works-open"]["qualifiers"].get("continuation_statement_id") != "st-chp8-p213-giordano-erotic-subjects-and-ignudo":
        raise SystemExit("the p.212-p.213 erotic-works continuation link changed")

    outputs = {
        STATEMENTS: jsonl_bytes(statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
    }
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("p.212 statements:", len(page_rows), "->", len(changed_rows), "relation candidates:", sum(bool(row["qualifiers"]["relation_candidate"]) for row in changed_rows))
    print("added candidate:", NEW_CANDIDATE[0], NEW_CANDIDATE[1])
    print("added mention:", NEW_MENTION_ID, repr(phrase), "offsets", start, end)
    print("added statements:", ", ".join(sorted(NEW_STATEMENT_IDS)))
    for path, data in outputs.items():
        print(path.name, "sha256:", sha(data))
    if args.apply:
        backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
        if any(path.exists() for path in backups.values()):
            raise SystemExit("a p.212 recovery copy already exists; inspect it before applying")
        for path, backup in backups.items():
            shutil.copy2(path, backup)
        for path, data in outputs.items():
            atomic_write(path, data)
        print("recovery copies:", ", ".join(path.name for path in backups.values()))


if __name__ == "__main__":
    main()
