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
PAGE_IMAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p123_page_review_20261011.png"
BODY_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l28-33"
NOTES_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l125-147"
SOURCE_SHA256 = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA256 = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
PAGE_IMAGE_SHA256 = "deaa254326d15fdec82d736f09a33163ea80b95a943dce2ea0eca8cdf41a4da0"
BODY_SEGMENT_SHA256 = "9ed81bc933510570643cdb32ce1d6745a7a48454dbc0fe08b57adea4d74d0883"
NOTE_SEGMENT_SHA256 = "5fdb179fd5637ce1d0a0b6b3da66e4e871452e25debcd265e4749060845324e8"
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
    "coverage": ROOT / "04-knowledge/tables/s2-coverage.csv",
}
EXPECTED_TABLE_SHA256 = {
    "statements": "f0eaa8dcce97bba95e6628d869a7dfa86717f5721c45bcebe898bf8a59a7963a",
    "candidates": "1e0af85224683d0dcae917f66e04927cdce37476202ca0427d7ed9e7b36cf7ac",
    "mentions": "618b80458b7b4b48b07c45451bf179a62475cf6819daf4c5b466ef4ecbbd0eba",
    "coverage": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = ".bak-s2-chp5-p123-20261011"
RELATION_NOTE = "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
NONRELATION_NOTE = "This is a source-attributed biographical, contextual, negative, or interpretive assertion; it does not assert a specific binary relation."

NOTE_IDS = {
    1: ["st-chp5-note-p123-n1-dealer-generalization"],
    2: [
        "st-chp5-note-p123-n2-carlo-cassiano-letters",
        "st-chp5-note-p123-n2-carlo-historiography",
        "st-chp5-note-p123-n2-ludovico-letters",
        "st-chp5-note-p123-n2-dumesnil-bottari",
        "st-chp5-note-p123-n2-cassiano-letters-location",
        "st-chp5-note-p123-n2-nicodemi-career-sources",
        "st-chp5-note-p123-n2-cites-dumesnil",
        "st-chp5-note-p123-n2-cites-borzelli",
    ],
    3: ["st-chp5-note-p123-n3-avviso-bernini", "st-chp5-note-p123-n3-cites-fraschetti"],
    4: [
        "st-chp5-note-p123-n4-citation",
        "st-chp5-note-p123-n4-critical-edition",
    ],
}

CANDIDATES = [
    {
        "candidate_id": "cand-11704",
        "canonical_name": "Unnamed leading artists in contact with Ferrante Carlo (p.123)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell says Carlo was in touch with many leading artists but names no members of this group in the passage.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L31",
    },
    {
        "candidate_id": "cand-11705",
        "canonical_name": "Friends whom Giulio Mancini encouraged to eat meat during Lent (unnamed group, p.123)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell describes Mancini encouraging his friends to eat meat during Lent; no individual friend is identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L33",
    },
    {
        "candidate_id": "cand-11706",
        "canonical_name": "Unidentified married woman in Giulio Mancini's p.123 account",
        "suggested_type": "person",
        "status": "open",
        "detail": "Haskell refers to a married woman with whom Mancini had an affair but does not identify her.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L33",
    },
    {
        "candidate_id": "cand-11707",
        "canonical_name": "Unidentified criminal sons of the married woman in Giulio Mancini's p.123 account",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell says the woman's criminal sons were saved from justice by Mancini; no individual son is identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L33",
    },
    {
        "candidate_id": "cand-11708",
        "canonical_name": "Jan Niceo Eritreo, volume II cited for Giulio Mancini's life (work title unresolved)",
        "suggested_type": "archive",
        "status": "open",
        "detail": "Haskell gives author form, volume and page range but no work title in this footnote; the referenced edition has not been independently identified or consulted.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES_SEGMENT_ID}#L141",
    },
]

NEW_MENTIONS = [
    ("m-chp5-p123-s2-leading-artists", "cand-11704", "many leading artists", "Unnamed group used as the object of Carlo's reported contacts.", "many leading artists", BODY_SEGMENT_ID, BODY_SEGMENT_ID),
    ("m-chp5-p123-s2-mancini-friends", "cand-11705", "his friends", "Unnamed friends whom Mancini reportedly encouraged to eat meat during Lent.", "encouraged his friends", BODY_SEGMENT_ID, BODY_SEGMENT_ID),
    ("m-chp5-p123-s2-mancini-woman", "cand-11706", "a married woman", "Unidentified woman in Haskell's account of Mancini.", "a married woman", BODY_SEGMENT_ID, BODY_SEGMENT_ID),
    ("m-chp5-p123-s2-mancini-sons", "cand-11707", "criminal sons", "Unidentified plural group whose members Haskell says Mancini saved from justice.", "criminal sons", BODY_SEGMENT_ID, BODY_SEGMENT_ID),
    ("m-chp5-note-p123-s2-eritreo-volume", "cand-11708", "Jan Niceo Eritreo, II", "Source reference for Mancini's life; work title remains unresolved.", "Jan Niceo Eritreo", NOTES_SEGMENT_ID, NOTES_SEGMENT_ID),
    ("m-chp5-note-p123-s2-dumesnil-work", "cand-11319", "Dumesnil in 1853", "Bibliography candidate matching the named author and year in Haskell's note.", "Dumesnil in 1853", NOTES_SEGMENT_ID, NOTES_SEGMENT_ID),
    ("m-chp5-note-p123-s2-borzelli-work", "cand-11259", "Borzelli, 1910", "Bibliography candidate matching the named author and year in Haskell's note.", "Borzelli, 1910", NOTES_SEGMENT_ID, NOTES_SEGMENT_ID),
    ("m-chp5-note-p123-s2-fraschetti-work", "cand-4553", "Fraschetti, p. 71", "Bibliography candidate for the cited Fraschetti volume; the locator is preserved from Haskell's footnote.", "Fraschetti, p. 71", NOTES_SEGMENT_ID, NOTES_SEGMENT_ID),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_hash(path: Path, expected: str, label: str) -> None:
    actual = digest(path.read_bytes())
    if actual != expected:
        raise SystemExit(f"STOP: {label} changed: {path} ({actual})")


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


def note_link(marker: int):
    return {
        "marker": marker,
        "note_line": {1: 138, 2: 139, 3: 140, 4: 141}[marker],
        "note_segment": NOTES_SEGMENT_ID,
        "note_statement_ids": list(NOTE_IDS[marker]),
        "status": "linked",
    }


def make_statement(*, statement_id, region, subject, object_, predicate,
                   line_start, line_end, quote_start, quote_end, claim,
                   qualification, mentioned, relation, relation_note,
                   marker=None, text_layer=None):
    text = BODY_TEXT if region == "body" else NOTE_TEXT
    segment_id = BODY_SEGMENT_ID if region == "body" else NOTES_SEGMENT_ID
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "pdf_physical_page": 4,
            "printed_page_locator": "p.123",
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": text_layer or ("authorial narration" if region == "body" else "authorial footnote"),
            "qualification": qualification,
            "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
            "relation_candidate": relation,
            "relation_candidate_note": relation_note,
        },
        "original_quote": quote_between(text, quote_start, quote_end),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
    }


def revise(by_id, *, statement_id, region, subject, object_, predicate,
           line_start, line_end, quote_start, quote_end, claim,
           qualification, mentioned, relation, relation_note, marker=None,
           text_layer=None):
    row = by_id[statement_id]
    fresh = make_statement(
        statement_id=statement_id, region=region, subject=subject, object_=object_,
        predicate=predicate, line_start=line_start, line_end=line_end,
        quote_start=quote_start, quote_end=quote_end, claim=claim,
        qualification=qualification, mentioned=mentioned, relation=relation,
        relation_note=relation_note, marker=marker, text_layer=text_layer,
    )
    row.update({key: value for key, value in fresh.items() if key != "qualifiers"})
    q = row.setdefault("qualifiers", {})
    for key in ("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment"):
        q.pop(key, None)
    q.update(fresh["qualifiers"])
    if marker is not None:
        q["footnote_numbers"] = [marker]
        q["footnote_links"] = [note_link(marker)]
        q["footnote_link_status"] = "linked"


NEW_SPECS = []


def add(statement_id, region, subject, object_, predicate, line_start, line_end,
        quote_start, quote_end, claim, qualification, mentioned, relation,
        marker=None, text_layer=None):
    NEW_SPECS.append({
        "statement_id": statement_id, "region": region, "subject": subject,
        "object_": object_, "predicate": predicate, "line_start": line_start,
        "line_end": line_end, "quote_start": quote_start, "quote_end": quote_end,
        "claim": claim, "qualification": qualification, "mentioned": mentioned,
        "relation": relation, "relation_note": RELATION_NOTE if relation else NONRELATION_NOTE,
        "marker": marker, "text_layer": text_layer,
    })


# The page's opening line completes the sentence begun on p.122; each claim keeps its own source limitation.
add("st-chp5-p123-dealer-frequency", "body", "cand-0125", None, "dealer_mentions_increase_over_time_reported", 29, 29,
    "we hear more and more of them", "as the years go by",
    "Haskell says dealers are mentioned increasingly as the years pass.",
    "This is Haskell's qualitative observation about frequency, not a quantified trend.", ["cand-0125"], False, marker=1)
add("st-chp5-p123-dealer-limited-reach", "body", "cand-0125", None, "seventeenth_century_dealer_reach_uncertain", 29, 29,
    "it is very doubtful whether", "relatively unknown painter.",
    "Haskell doubts whether seventeenth-century dealers generally ventured much beyond relatively unknown painters.",
    "The phrase 'very doubtful' preserves the author's uncertainty; no individual painter or transaction is identified.", ["cand-0125"], False, marker=1)
add("st-chp5-p123-marchands-history", "body", "cand-1537", None, "recurs_in_histories_of_patronage", 30, 30,
    "who turn up again and again", "any history of patronage.",
    "Haskell says marchand-amateurs recur in histories of patronage.",
    "This describes the historiographic appearance of a category, not a formal organization.", ["cand-1537"], False)
add("st-chp5-p123-marchands-overlooked", "body", "cand-1537", None, "cautious_emergence_long_unnoticed_reported", 30, 30,
    "This type of dealer makes his first appearance cautiously", "for a long time we fail to notice him.",
    "Haskell says the marchand-amateur type emerges cautiously and was long overlooked.",
    "This is the author's characterization of the category's visibility in the record.", ["cand-1537"], False)
add("st-chp5-p123-carlo-birthplace", "body", "cand-0560", "cand-3417", "born_in", 31, 31,
    "Ferrante Carlo, born in Parma in 1578", "1578",
    "Haskell places Ferrante Carlo's birth in Parma in 1578.",
    "Source-attributed biographical statement.", ["cand-0560", "cand-3417"], True, marker=2)
add("st-chp5-p123-carlo-lawyer", "body", "cand-0560", None, "described_as_cultivated_lawyer", 31, 31,
    "a most cultivated lawyer", "lawyer",
    "Haskell describes Ferrante Carlo as a cultivated lawyer.",
    "Source-attributed biographical description.", ["cand-0560"], False, marker=2)
add("st-chp5-p123-carlo-poet", "body", "cand-0560", None, "described_as_poet", 31, 31,
    "and poet", "poet",
    "Haskell describes Ferrante Carlo as a poet.",
    "Source-attributed biographical description.", ["cand-0560"], False, marker=2)
add("st-chp5-p123-carlo-secretary-borghese", "body", "cand-0560", "cand-0394", "served_as_secretary_to", 31, 31,
    "then by Cardinal Borghese", "Borghese",
    "Haskell says Carlo was later employed as secretary by Cardinal Borghese.",
    "The index-derived Borghese candidate is not globally reconciled here; retain the source's title and sequence.", ["cand-0560", "cand-0394"], True, marker=2)
add("st-chp5-p123-carlo-residence", "body", "cand-0560", "cand-0394", "resided_in_palace_of", 31, 31,
    "in whose palace he lived", "in whose palace he lived",
    "Haskell says Carlo lived in Cardinal Borghese's palace.",
    "The palace is not separately identified; the relation is recorded through the explicitly named associated patron.", ["cand-0560", "cand-0394"], True, marker=2)
add("st-chp5-p123-carlo-combative", "body", "cand-0560", None, "described_as_combative", 31, 31,
    "Of a rather combative temperament", "temperament",
    "Haskell describes Carlo as having a rather combative temperament.",
    "This is the author's characterization, not an independently verified personality assessment.", ["cand-0560"], False, marker=2)
add("st-chp5-p123-carlo-general-quarrels", "body", "cand-0560", None, "participated_in_many_literary_and_artistic_quarrels", 31, 31,
    "he took part in many of the literary and artistic quarrels of the day", "quarrels of the day",
    "Haskell says Carlo took part in many literary and artistic quarrels of his day.",
    "The general statement does not identify the other participants; named disputes are recorded separately.", ["cand-0560"], False, marker=2)
add("st-chp5-p123-carlo-marino", "body", "cand-0560", "cand-1548", "became_embroiled_in_quarrel_with", 31, 31,
    "first the poet Marino", "Marino",
    "Haskell says Carlo became embroiled with the poet Marino.",
    "The source places this among Carlo's literary and artistic quarrels.", ["cand-0560", "cand-1548"], True, marker=2)
add("st-chp5-p123-bernini-st-peters-alterations", "body", "cand-0295", "cand-5696", "made_precarious_alterations_to", 31, 31,
    "some precarious alterations the architect had made", "structure of St Peter’s",
    "Haskell says Bernini made alterations to the structure of St Peter's that Carlo considered precarious.",
    "The judgment 'precarious' is carried by Haskell's narration; the building is St Peter's Basilica, not a city or political entity.", ["cand-0295", "cand-5696"], True, marker=3)
add("st-chp5-p123-carlo-wished-bernini", "body", "cand-0560", "cand-0295", "wished_to_see_exterminated_reported", 31, 31,
    "whom he ‘wished to see exterminated’", "exterminated’",
    "Haskell reports that Carlo wished to see Bernini exterminated.",
    "This is reported wording, corroborated in Haskell's footnote through a 1637 avviso; it does not establish an action or threat carried out.", ["cand-0560", "cand-0295"], True, marker=3)
add("st-chp5-p123-carlo-picture-passion", "body", "cand-0560", None, "had_passion_for_pictures", 31, 31,
    "His real passion was for pictures", "pictures",
    "Haskell says Carlo's real passion was for pictures.",
    "Source-attributed characterization.", ["cand-0560"], False, marker=2)
add("st-chp5-p123-carlo-taste", "body", "cand-0560", None, "contemporaries_doubted_taste_reported", 31, 31,
    "contemporaries were doubtful about his taste", "taste",
    "Haskell says Carlo's contemporaries doubted his taste.",
    "The doubt is attributed to unnamed contemporaries.", ["cand-0560"], False, marker=2)
add("st-chp5-p123-carlo-understanding", "body", "cand-0560", None, "contemporaries_doubted_understanding_reported", 31, 31,
    "and understanding", "understanding",
    "Haskell says Carlo's contemporaries doubted his understanding of pictures.",
    "The doubt is attributed to unnamed contemporaries.", ["cand-0560"], False, marker=2)
add("st-chp5-p123-carlo-cassiano", "body", "cand-0560", "cand-2036", "was_in_contact_with", 31, 31,
    "he was in touch with Cassiano dal Pozzo", "Cassiano dal Pozzo",
    "Haskell says Carlo was in touch with Cassiano dal Pozzo.",
    "The corresponding evidence is later attributed to letters reported by Borzelli; those letters were not independently consulted.", ["cand-0560", "cand-2036"], True, marker=2)
add("st-chp5-p123-carlo-leading-artists", "body", "cand-0560", "cand-11704", "was_in_contact_with", 31, 31,
    "and many leading artists", "leading artists",
    "Haskell says Carlo was in touch with many leading artists.",
    "The group is unnamed and open; no individual artist is inferred.", ["cand-0560", "cand-11704"], True, marker=2)
add("st-chp5-p123-carlo-favorite-bolognese", "body", "cand-0560", "cand-4229", "favored_artists", 31, 31,
    "His special favourites were the Bolognese", "Bolognese",
    "Haskell says Carlo especially favored Bolognese artists.",
    "The existing collective candidate remains open as to membership and whether it denotes a school or regional group.", ["cand-0560", "cand-4229"], True, marker=2)
add("st-chp5-p123-carlo-favorite-lanfranco", "body", "cand-0560", "cand-1359", "favored_artist", 31, 31,
    "and Giovanni Lanfranco", "Lanfranco",
    "Haskell says Giovanni Lanfranco was among Carlo's special favorites.",
    "Source-attributed preference; 'from his native Parma' is not used to infer a birthplace for Lanfranco.", ["cand-0560", "cand-1359"], True, marker=2)
add("st-chp5-p123-lanfranco-parma", "body", "cand-1359", "cand-3417", "came_from_place", 31, 31,
    "Giovanni Lanfranco from his native Parma", "Parma",
    "Haskell describes Giovanni Lanfranco as from Parma, Carlo's native city.",
    "The source says 'from' but does not specify whether it means birthplace, residence, or another association.", ["cand-1359", "cand-3417"], True, marker=2)
add("st-chp5-p123-carlo-befriended-bolognese", "body", "cand-0560", "cand-4229", "befriended_artists", 31, 31,
    "He befriended and commissioned works from all of these", "all of these",
    "Haskell says Carlo befriended Bolognese artists.",
    "'All of these' refers to the Bolognese artists and Lanfranco named immediately before; group membership remains unspecified.", ["cand-0560", "cand-4229"], True, marker=2)
add("st-chp5-p123-carlo-commissioned-bolognese", "body", "cand-0560", "cand-4229", "commissioned_works_from_artists", 31, 31,
    "He befriended and commissioned works from all of these", "all of these",
    "Haskell says Carlo commissioned works from Bolognese artists.",
    "The commissioned works and individual artists are not identified.", ["cand-0560", "cand-4229"], True, marker=2)
add("st-chp5-p123-carlo-befriended-lanfranco", "body", "cand-0560", "cand-1359", "befriended_artist", 31, 31,
    "He befriended and commissioned works from all of these", "all of these",
    "Haskell says Carlo befriended Giovanni Lanfranco.",
    "'All of these' refers to the Bolognese artists and Lanfranco named immediately before.", ["cand-0560", "cand-1359"], True, marker=2)
add("st-chp5-p123-carlo-commissioned-lanfranco", "body", "cand-0560", "cand-1359", "commissioned_works_from_artist", 31, 31,
    "He befriended and commissioned works from all of these", "all of these",
    "Haskell says Carlo commissioned works from Giovanni Lanfranco.",
    "The commissioned work is not identified.", ["cand-0560", "cand-1359"], True, marker=2)
add("st-chp5-p123-carlo-marchand-amateur", "body", "cand-0560", "cand-1537", "recognized_as_example_of_dealer_type", 31, 31,
    "We recognise the type", "We recognise the type",
    "Haskell presents Carlo as an example of the marchand-amateur type.",
    "This is Haskell's interpretation of the preceding account, not an independently verified social classification.", ["cand-0560", "cand-1537"], True, marker=2)
add("st-chp5-p123-valguarnera-visit", "body", "cand-2684", "cand-0560", "visited", 31, 31,
    "when the Sicilian adventurer Don Fabrizio Valguarnera called on Ferrante Carlo", "Ferrante Carlo",
    "Haskell recounts that Don Fabrizio Valguarnera visited Ferrante Carlo in 1631 with a few friends.",
    "The companions are unnamed; no identities or separate actions are assigned to them.", ["cand-2684", "cand-0560"], True)
add("st-chp5-p123-valguarnera-discussion", "body", "cand-2684", None, "discussion_of_painters_at_carlo_collection_reported", 31, 31,
    "For a time they talked in generalities about the qualities of the various painters represented on his walls", "on his walls",
    "Haskell says Valguarnera's visit included a general discussion of painters represented on Carlo's walls.",
    "The companions and painters are unnamed; the passage does not attribute particular opinions to any individual.", ["cand-2684", "cand-0560"], False)
add("st-chp5-p123-carlo-not-wholly-disinterested", "body", "cand-0560", None, "passion_not_wholly_disinterested_inferred", 31, 31,
    "But his passion was not wholly disinterested", "episode in 1631",
    "Haskell infers from the 1631 Valguarnera episode that Carlo's passion for pictures was not wholly disinterested.",
    "This is the author's interpretation of the episode, not an independently established motive.", ["cand-0560", "cand-2684"], False)
add("st-chp5-p123-carlo-agreed-sale", "body", "cand-0560", "cand-2684", "agreed_to_part_with_pictures_conditionally", 31, 31,
    "The answer was immediate: T agreed,’ said Carlo when describing the incident later, ‘as long as I received an honourable deal.’", "honourable deal.’",
    "Carlo later said he agreed to part with some pictures only if he received an honourable deal.",
    "The OCR transcription reads 'T agreed'; the p.123 scan reads 'I agreed'. The source transcription remains unchanged, and the statement is attributed to Carlo's later account.", ["cand-0560", "cand-2684"], True)
add("st-chp5-p123-mancini-dealer-role", "body", "cand-1507", None, "dealer_role_and_access_reported", 33, 33,
    "Another strange sort of dealer, even better placed for taking advantage of his connections", "connections",
    "Haskell characterizes Mancini as an unusual dealer whose position gave him access to useful connections.",
    "This is Haskell's social interpretation; the connections and their beneficiaries are not specified.", ["cand-1507", "cand-0125"], False, marker=4)
add("st-chp5-p123-mancini-reputation-freedom", "body", "cand-1507", None, "healer_reputation_enabled_unusual_freedom_reported", 33, 33,
    "his inflated reputation as a great healer allowed him a degree of freedom unimaginable to ordinary citizens", "ordinary citizens",
    "Haskell says Mancini's inflated reputation as a healer allowed him unusual freedom compared with ordinary citizens.",
    "This is Haskell's characterization and causal interpretation, not an independently verified medical or legal finding.", ["cand-1507"], False, marker=4)
add("st-chp5-p123-mancini-atheism", "body", "cand-1507", None, "described_as_virtually_self_confessed_atheist", 33, 33,
    "A virtually self-confessed atheist", "atheist",
    "Haskell describes Mancini as a virtually self-confessed atheist.",
    "The author preserves a qualified characterization; it is not stated as an independently verified belief record.", ["cand-1507"], False, marker=4)
add("st-chp5-p123-mancini-encouraged-friends", "body", "cand-1507", "cand-11705", "encouraged_friends_to_eat_meat_during_lent", 33, 33,
    "he deliberately encouraged his friends to eat meat during Lent", "during Lent",
    "Haskell says Mancini deliberately encouraged his friends to eat meat during Lent.",
    "The friends are an unnamed group and the statement is attributed to Haskell.", ["cand-1507", "cand-11705"], True, marker=4)
add("st-chp5-p123-mancini-affair", "body", "cand-1507", "cand-11706", "had_affair_with", 33, 33,
    "carried on a notorious affair with a married woman", "married woman",
    "Haskell says Mancini had a notorious affair with an unidentified married woman.",
    "The woman's identity is not supplied; the claim remains attributed to Haskell.", ["cand-1507", "cand-11706"], True, marker=4)
add("st-chp5-p123-mancini-saved-sons", "body", "cand-1507", "cand-11707", "saved_womans_sons_from_justice_reported", 33, 33,
    "whose criminal sons he successfully saved from justice", "saved from justice",
    "Haskell says Mancini successfully saved the woman's criminal sons from justice.",
    "The sons are unnamed; 'criminal' and the intervention are Haskell's report, not independent legal findings.", ["cand-1507", "cand-11706", "cand-11707"], True, marker=4)

# Footnotes are treated as source-attributed evidence. Their references do not silently become S6 edges.
add("st-chp5-note-p123-n2-dumesnil-bottari", "notes", "cand-6085", None, "chapter_and_letter_publication_context_reported", 139, 139,
    "Dumesnil in 1853 devoted a chapter to Carlo", "published by Bottari, I.",
    "Haskell says Dumesnil devoted a chapter to Carlo in 1853 and that it largely summarized letters to Carlo published by Bottari, volume I.",
    "This is Haskell's account of the earlier literature; neither the chapter nor the letters were independently consulted here.", ["cand-6085", "cand-0560", "cand-0417"], False)
add("st-chp5-note-p123-n2-cassiano-letters-location", "notes", "cand-0560", None, "contacts_documented_in_letters_held_at", 139, 139,
    "which are documented in letters now in the Montpellier Library", "Montpellier Library",
    "Haskell says letters documenting Carlo's contacts with Cassiano were then held at the Montpellier Library.",
    "The letters were not independently consulted; 'now' is relative to Haskell's account. This is a source-location statement, not a direct person-institution relationship.", ["cand-0560", "cand-2036", "cand-6086"], False)
add("st-chp5-note-p123-n2-nicodemi-career-sources", "notes", "cand-6087", None, "referred_to_other_sources_for_carlo_career", 139, 139,
    "who also refers to other sources for his career", "career",
    "Haskell says Giorgio Nicodemi also referred to other sources for Carlo's career.",
    "The other sources are not identified in this sentence.", ["cand-6087", "cand-0560"], False)
add("st-chp5-note-p123-n2-cites-dumesnil", "notes", "cand-2962", "cand-11319", "cites", 139, 139,
    "Dumesnil in 1853", "Dumesnil in 1853",
    "Haskell refers to Dumesnil's 1853 chapter on Ferrante Carlo; the bibliography supplies a matching Dumesnil 1853 publication candidate.",
    "The mapping follows the cited author and year and the bibliography record; the publication was not independently consulted.", ["cand-2962", "cand-11319"], True)
add("st-chp5-note-p123-n2-cites-borzelli", "notes", "cand-2962", "cand-11259", "cites", 139, 139,
    "Borzelli, 1910", "Borzelli, 1910",
    "Haskell cites Borzelli's 1910 publication for further information on Carlo's contacts with Cassiano.",
    "The bibliography candidate matches the author and year; the cited publication was not independently consulted.", ["cand-2962", "cand-11259"], True)
add("st-chp5-note-p123-n4-critical-edition", "notes", "cand-2962", "cand-6089", "cites", 141, 141,
    "See also the critical edition of his works, 1956.", "1956.",
    "Haskell also points readers to a 1956 critical edition of Mancini's works.",
    "The edition candidate preserves the source's incomplete citation; the edition was not independently consulted.", ["cand-2962", "cand-1507", "cand-6089"], True, text_layer="authorial footnote")
add("st-chp5-note-p123-n3-cites-fraschetti", "notes", "cand-2962", "cand-4553", "cites", 140, 140,
    "Fraschetti, p. 71", "p. 71",
    "Haskell cites Fraschetti's Il Bernini at page 71 for the 1637 avviso.",
    "The bibliography candidate matches the cited author and work; the publication was not independently consulted.", ["cand-2962", "cand-4553", "cand-6088"], True, text_layer="authorial footnote")


def mention_row(text, item):
    mention_id, candidate_id, surface, note, anchor, segment_id, region = item
    anchor_at = text.find(anchor)
    if anchor_at < 0:
        raise SystemExit(f"STOP: mention anchor not found: {mention_id}: {anchor!r}")
    start = text.find(surface, anchor_at)
    if start < 0:
        raise SystemExit(f"STOP: mention surface not found after anchor: {mention_id}: {surface!r}")
    return {
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and refine p.123 S2 statements; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the validated table changes")
    args = parser.parse_args()

    require_hash(SOURCE, SOURCE_SHA256, "canonical source")
    require_hash(PDF, PDF_SHA256, "chapter PDF")
    require_hash(PAGE_IMAGE, PAGE_IMAGE_SHA256, "p.123 page review image")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    BODY_TEXT = "\n".join(lines[27:33])
    NOTE_TEXT = "\n".join(lines[124:147])
    if digest(BODY_TEXT.encode("utf-8")) != BODY_SEGMENT_SHA256:
        raise SystemExit("STOP: p.123 body segment changed")
    if digest(NOTE_TEXT.encode("utf-8")) != NOTE_SEGMENT_SHA256:
        raise SystemExit("STOP: p.123 note segment changed")
    if not BODY_TEXT.startswith("[Page 123]\n"):
        raise SystemExit("STOP: p.123 body boundary changed")
    globals()["BODY_TEXT"] = BODY_TEXT
    globals()["NOTE_TEXT"] = NOTE_TEXT

    raw = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, expected in EXPECTED_TABLE_SHA256.items():
        if digest(raw[name]) != expected:
            raise SystemExit(f"STOP: {name} table changed since p.122 review")

    statement_text = raw["statements"].decode("utf-8-sig")
    statement_bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    statement_rows = [json.loads(line) for line in statement_text.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("STOP: duplicate statement_id before p.123 update")
    targets = {
        "st-chp5-p123-dealer-role", "st-chp5-p123-marchands-category",
        "st-chp5-p123-carlo-bargaining-inference", "st-chp5-p123-carlo-collecting",
        "st-chp5-p123-carlo-offices", "st-chp5-p123-carlo-quarrels",
        "st-chp5-p123-mancini", "st-chp5-p123-valguarnera-purchase",
        "st-chp5-note-p123-n1-dealer-generalization",
        "st-chp5-note-p123-n2-carlo-cassiano-letters",
        "st-chp5-note-p123-n2-carlo-historiography",
        "st-chp5-note-p123-n2-ludovico-letters",
        "st-chp5-note-p123-n3-avviso-bernini",
        "st-chp5-note-p123-n4-citation",
    }
    if targets - set(by_id):
        raise SystemExit(f"STOP: missing p.123 targets: {sorted(targets-set(by_id))}")
    for statement_id in targets:
        q = by_id[statement_id].get("qualifiers", {})
        if q.get("relation_candidate") not in (None, ""):
            raise SystemExit(f"STOP: p.123 target already classified: {statement_id}")

    cand_raw, cand_bom, cand_text, cand_headers, candidates = read_csv(TABLES["candidates"])
    mention_raw, mention_bom, mention_text, mention_headers, mentions = read_csv(TABLES["mentions"])
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    planned_candidate_ids = {row["candidate_id"] for row in CANDIDATES}
    if candidate_ids & planned_candidate_ids:
        raise SystemExit("STOP: a planned candidate ID already exists")
    new_ids = {row["statement_id"] for row in NEW_SPECS}
    if len(new_ids) != len(NEW_SPECS) or new_ids & set(by_id):
        raise SystemExit("STOP: planned statement IDs are duplicated or already present")
    planned_mentions = [
        mention_row(BODY_TEXT if item[5] == BODY_SEGMENT_ID else NOTE_TEXT, item)
        for item in NEW_MENTIONS
    ]
    planned_mention_ids = {row["mention_id"] for row in planned_mentions}
    if len(planned_mention_ids) != len(planned_mentions) or planned_mention_ids & mention_ids:
        raise SystemExit("STOP: a planned mention ID is duplicated or already present")

    for row in CANDIDATES:
        for field in cand_headers:
            row.setdefault(field, "")
    all_candidate_ids = candidate_ids | planned_candidate_ids

    def revise_existing(statement_id, region, subject, object_, predicate, line_start, line_end,
                        quote_start, quote_end, claim, qualification, mentioned, relation,
                        marker=None, text_layer=None):
        revise(
            by_id, statement_id=statement_id, region=region, subject=subject, object_=object_,
            predicate=predicate, line_start=line_start, line_end=line_end,
            quote_start=quote_start, quote_end=quote_end, claim=claim,
            qualification=qualification, mentioned=mentioned, relation=relation,
            relation_note=RELATION_NOTE if relation else NONRELATION_NOTE,
            marker=marker, text_layer=text_layer,
        )

    revise_existing("st-chp5-p123-dealer-role", "body", "cand-0125", None,
        "dealer_role_in_artist_patron_change_reported", 29, 29,
        "part in breaking down the tight relationship", "artist and patron",
        "Haskell says dealer activity contributed to weakening the close relationship between artist and patron.",
        "This is a structural interpretation; the sentence does not identify a particular artist, patron, or transaction.", ["cand-0125"], False, marker=1)
    revise_existing("st-chp5-p123-marchands-category", "body", "cand-1537", None,
        "activities_difficult_to_determine", 30, 30,
        "those marchands-amateurs whose activities", "not easily determined",
        "Haskell says the activities of marchand-amateurs were often difficult to determine.",
        "A source-defined social category, not a formally organized institution.", ["cand-1537"], False)
    revise_existing("st-chp5-p123-carlo-offices", "body", "cand-0560", "cand-2424",
        "served_as_secretary_to", 31, 31,
        "employed as secretary first by Cardinal Sfondrato", "Sfondrato",
        "Haskell says Carlo was first employed as secretary by Cardinal Sfondrato.",
        "Source-attributed office; the source gives no term dates.", ["cand-0560", "cand-2424"], True)
    revise_existing("st-chp5-p123-carlo-quarrels", "body", "cand-0560", "cand-0295",
        "became_embroiled_in_quarrel_with", 31, 31,
        "managed to become embroiled with the two greatest favourites", "structure of St Peter’s",
        "Haskell says Carlo became embroiled with Bernini over the architect's alterations to St Peter's.",
        "The source reports Carlo's hostile response; the wish to see Bernini exterminated is separately recorded and does not establish an action carried out.", ["cand-0560", "cand-1548", "cand-0295", "cand-5696"], True, marker=3)
    revise_existing("st-chp5-p123-carlo-collecting", "body", "cand-0560", None,
        "owned_notable_picture_collection", 31, 31,
        "and owned a notable collection", "notable collection",
        "Haskell says Carlo owned a notable collection of pictures.",
        "The collection and its individual works are not enumerated in this sentence.", ["cand-0560"], False, marker=2)
    revise_existing("st-chp5-p123-carlo-bargaining-inference", "body", "cand-0560", None,
        "shrewd_bargaining_inferred", 32, 32,
        "Beneath the Oriental courtesies", "shrewd bargaining.",
        "Haskell infers that Carlo's courteous manner concealed shrewd bargaining.",
        "This is the author's interpretation of the episode, not an independently established fact.", ["cand-0560"], False)
    revise_existing("st-chp5-p123-valguarnera-purchase", "body", "cand-2684", "cand-0560",
        "requested_to_buy_pictures_from", 31, 31,
        "Valguarnera asked if Carlo was prepared", "some of his pictures’",
        "Haskell says Valguarnera asked whether Carlo would part with some pictures.",
        "The pictures are not individually identified; the request is recorded separately from Carlo's conditional response.", ["cand-2684", "cand-0560"], True)
    revise_existing("st-chp5-p123-mancini", "body", "cand-1507", None,
        "identified_as_popes_doctor", 33, 33,
        "was the Pope’s doctor Giulio Mancini", "Mancini",
        "Haskell identifies Giulio Mancini as the Pope's doctor.",
        "The Pope is unnamed in this passage; no pontificate or appointment date is inferred.", ["cand-1507"], False, marker=4)

    revise_existing("st-chp5-note-p123-n1-dealer-generalization", "notes", None, None,
        "distinguished_artist_dealer_work_generalization", 138, 138,
        "Certainly there are no cases", "Martin, 1907.",
        "Haskell says he knows no further cases beyond those already cited of distinguished artists working systematically for dealers and compares the situation with contemporary Holland.",
        "This is a qualified negative generalization, not an asserted positive artist-dealer relation; Martin (1907) is not independently consulted here.", ["cand-0125", "cand-6084"], False, text_layer="authorial footnote")
    revise_existing("st-chp5-note-p123-n2-carlo-cassiano-letters", "notes", "cand-0560", "cand-4945",
        "had_contacts_with", 139, 139,
        "There is further information in Borzelli, 1910", "Montpellier Library.",
        "Haskell says Borzelli (1910) provides further information on Carlo's contacts with Cassiano dal Pozzo.",
        "This is Haskell's reference to Borzelli; the cited work and underlying letters were not independently consulted.", ["cand-0560", "cand-4945", "cand-6086", "cand-11259"], True, text_layer="authorial footnote")
    revise_existing("st-chp5-note-p123-n2-carlo-historiography", "notes", "cand-0560", None,
        "earlier_writers_treated_carlo_only_as_patron_reported", 139, 139,
        "For Ferrante Carlo see above all the evidence quoted by Miss Jane Costello", "purely as a patron.",
        "Haskell points to Jane Costello's evidence and says earlier writers, including Dumesnil, did not recognize Carlo's dealer activity and treated him only as a patron.",
        "This is Haskell's characterization of earlier scholarship; it is not an independent assessment of those authors.", ["cand-0560", "cand-7016", "cand-6085"], False, text_layer="authorial footnote")
    revise_existing("st-chp5-note-p123-n2-ludovico-letters", "notes", "cand-0580", "cand-6095",
        "letters_published_in", 139, 139,
        "Some most interesting letters from Ludovico Carracci to Carlo have been published by Giorgio Nicodemi, 1935", "1935",
        "Haskell says Giorgio Nicodemi published letters from Ludovico Carracci to Carlo in 1935.",
        "The referenced publication was not independently consulted; the relation describes the cited publication record.", ["cand-0580", "cand-0560", "cand-6087", "cand-6095"], True, text_layer="authorial footnote")
    revise_existing("st-chp5-note-p123-n3-avviso-bernini", "notes", "cand-0560", "cand-0295",
        "hostility_reported_in_avviso", 140, 140,
        "which refers to Carlo as a ‘nemico’ of Bernini", "esterminato’."
        ,"Haskell reports that a 1637 avviso described Carlo as Bernini's enemy and reported Carlo's wish to see Bernini exterminated.",
        "Haskell cites Fraschetti's publication of the notice; neither the original notice nor Fraschetti was independently consulted.", ["cand-0560", "cand-0295", "cand-6088", "cand-4553"], True, text_layer="authorial footnote")
    revise_existing("st-chp5-note-p123-n4-citation", "notes", "cand-2962", "cand-11708",
        "cites", 141, 141,
        "The main and most vivid source for Mancini’s life is Jan Niceo Eritreo, II, pp. 79-82.", "79-82.",
        "Haskell cites Jan Niceo Eritreo, volume II, pages 79–82, as a source on Mancini's life.",
        "The cited work's title and edition remain unresolved; it has not been independently consulted.", ["cand-2962", "cand-1507", "cand-11708", "cand-4560"], True, text_layer="authorial footnote")

    # Resolve the exact p.123 Jane Costello mention to the already registered full-name candidate.
    mention_by_id = {row["mention_id"]: row for row in mentions}
    for mention_id in ("m-chp5-note-L139-029", "m-s2-surface-93a43ab71d5c9f67"):
        if mention_id not in mention_by_id or mention_by_id[mention_id].get("candidate_id") != "cand-3509":
            raise SystemExit(f"STOP: expected Jane Costello mention mapping changed: {mention_id}")
        mention_by_id[mention_id]["candidate_id"] = "cand-7016"
    new_rows = [make_statement(**spec) for spec in NEW_SPECS]
    for row in CANDIDATES:
        for field in cand_headers:
            row.setdefault(field, "")
    for row in new_rows:
        if row["statement_id"] in by_id:
            raise SystemExit(f"STOP: new statement already exists: {row['statement_id']}")
        q = row["qualifiers"]
        if q["relation_candidate"]:
            if not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
                raise SystemExit(f"STOP: relation candidate lacks an endpoint: {row['statement_id']}")
            if not {row["subject_candidate_id"], row["object_candidate_id"]}.issubset(set(q["mentioned_candidate_ids"])):
                raise SystemExit(f"STOP: relation endpoint absent from mention list: {row['statement_id']}")
            if not {row["subject_candidate_id"], row["object_candidate_id"]}.issubset(all_candidate_ids):
                raise SystemExit(f"STOP: unknown relation endpoint: {row['statement_id']}")

    all_rows = {**by_id, **{row["statement_id"]: row for row in new_rows}}
    # Keep the forward and reverse footnote links synchronized after splitting statements.
    body_links = {
        1: ["st-chp5-p123-dealer-role", "st-chp5-p123-dealer-frequency", "st-chp5-p123-dealer-limited-reach"],
        2: ["st-chp5-p123-carlo-offices", "st-chp5-p123-carlo-residence", "st-chp5-p123-carlo-birthplace", "st-chp5-p123-carlo-lawyer", "st-chp5-p123-carlo-poet", "st-chp5-p123-carlo-combative", "st-chp5-p123-carlo-general-quarrels", "st-chp5-p123-carlo-marino", "st-chp5-p123-carlo-collecting", "st-chp5-p123-carlo-picture-passion", "st-chp5-p123-carlo-taste", "st-chp5-p123-carlo-understanding", "st-chp5-p123-carlo-cassiano", "st-chp5-p123-carlo-leading-artists", "st-chp5-p123-carlo-favorite-bolognese", "st-chp5-p123-carlo-favorite-lanfranco", "st-chp5-p123-lanfranco-parma", "st-chp5-p123-carlo-befriended-bolognese", "st-chp5-p123-carlo-commissioned-bolognese", "st-chp5-p123-carlo-befriended-lanfranco", "st-chp5-p123-carlo-commissioned-lanfranco", "st-chp5-p123-carlo-marchand-amateur", "st-chp5-p123-carlo-not-wholly-disinterested"],
        3: ["st-chp5-p123-carlo-quarrels", "st-chp5-p123-bernini-st-peters-alterations", "st-chp5-p123-carlo-wished-bernini"],
        4: ["st-chp5-p123-mancini", "st-chp5-p123-mancini-dealer-role", "st-chp5-p123-mancini-reputation-freedom", "st-chp5-p123-mancini-atheism", "st-chp5-p123-mancini-encouraged-friends", "st-chp5-p123-mancini-affair", "st-chp5-p123-mancini-saved-sons"],
    }
    note_body_links = {
        "st-chp5-note-p123-n1-dealer-generalization": body_links[1],
        "st-chp5-note-p123-n2-carlo-cassiano-letters": ["st-chp5-p123-carlo-cassiano"],
        "st-chp5-note-p123-n2-carlo-historiography": ["st-chp5-p123-carlo-offices", "st-chp5-p123-carlo-collecting", "st-chp5-p123-valguarnera-purchase"],
        "st-chp5-note-p123-n2-ludovico-letters": ["st-chp5-p123-carlo-collecting", "st-chp5-p123-carlo-leading-artists"],
        "st-chp5-note-p123-n2-dumesnil-bottari": ["st-chp5-p123-carlo-offices", "st-chp5-p123-carlo-collecting"],
        "st-chp5-note-p123-n2-cassiano-letters-location": ["st-chp5-p123-carlo-cassiano"],
        "st-chp5-note-p123-n2-nicodemi-career-sources": ["st-chp5-p123-carlo-offices"],
        "st-chp5-note-p123-n2-cites-dumesnil": ["st-chp5-p123-carlo-offices", "st-chp5-p123-carlo-collecting"],
        "st-chp5-note-p123-n2-cites-borzelli": ["st-chp5-p123-carlo-cassiano"],
        "st-chp5-note-p123-n3-avviso-bernini": body_links[3],
        "st-chp5-note-p123-n3-cites-fraschetti": body_links[3],
        "st-chp5-note-p123-n4-citation": body_links[4],
        "st-chp5-note-p123-n4-critical-edition": body_links[4],
    }
    for note_id, body_ids in note_body_links.items():
        q = all_rows[note_id].setdefault("qualifiers", {})
        q["linked_body_statement_ids"] = list(dict.fromkeys(q.get("linked_body_statement_ids", []) + body_ids))

    # Validate all p.123 relation endpoints, including the original statements after their revisions.
    for row in all_rows.values():
        if row.get("segment_id") not in (BODY_SEGMENT_ID, NOTES_SEGMENT_ID):
            continue
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is True:
            endpoints = {row.get("subject_candidate_id"), row.get("object_candidate_id")}
            if None in endpoints or not endpoints.issubset(all_candidate_ids):
                raise SystemExit(f"STOP: p.123 relation has missing/unknown endpoint: {row['statement_id']}")
            if not endpoints.issubset(set(q.get("mentioned_candidate_ids", []))):
                raise SystemExit(f"STOP: p.123 relation endpoint absent from mention list: {row['statement_id']}")

    # Build the output while preserving JSONL order, CSV columns, BOM, and newline style.
    statement_newline = "\r\n" if "\r\n" in statement_text else "\n"
    out_lines = []
    revised_ids = set(targets)
    for raw_line in statement_text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not line.strip():
            out_lines.append(raw_line)
            continue
        row = json.loads(line)
        if row["statement_id"] in revised_ids:
            row = by_id[row["statement_id"]]
            line = json.dumps(row, ensure_ascii=False)
            ending = ending or statement_newline
        out_lines.append(line + ending)
    if out_lines and not out_lines[-1].endswith(("\n", "\r")):
        out_lines[-1] += statement_newline
    out_lines.extend(json.dumps(row, ensure_ascii=False) + statement_newline for row in new_rows)
    statement_bytes = (b"\xef\xbb\xbf" if statement_bom else b"") + "".join(out_lines).encode("utf-8")
    candidate_bytes = emit_csv(cand_headers, candidates + CANDIDATES, cand_bom, cand_text)
    mention_bytes = emit_csv(mention_headers, mentions + planned_mentions, mention_bom, mention_text)
    outputs = {"statements": statement_bytes, "candidates": candidate_bytes, "mentions": mention_bytes}

    relation_count = sum(1 for row in new_rows if row["qualifiers"]["relation_candidate"])
    scalar_count = len(new_rows) - relation_count
    print("p.123 source file, PDF physical page 4, page image, and body/note segment hashes verified")
    print(f"existing body/note statements revised: {len(targets)}")
    print(f"new atomic statements: {len(new_rows)} ({relation_count} relation candidates; {scalar_count} non-relational claims)")
    print(f"new candidates: {len(CANDIDATES)}; new mentions: {len(planned_mentions)}")
    print("unclassified dual-endpoint p.123 statements now classified: carlo-quarrels, Cassiano letters, Ludovico letters, avviso, and citations")
    print("candidate additions:")
    for row in CANDIDATES:
        print(f"  {row['candidate_id']} [{row['suggested_type']}] {row['canonical_name']}")
    print("existing statements revised:")
    for statement_id in sorted(targets):
        row = by_id[statement_id]
        q = row.get("qualifiers", {})
        print(f"  {statement_id}: {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')}; relation={q.get('relation_candidate')}; {q.get('claim', '')[:170]}")
    print("new statements:")
    for row in new_rows:
        q = row["qualifiers"]
        print(f"  {row['statement_id']}: {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')}; relation={q.get('relation_candidate')}; {q.get('claim', '')[:170]}")
    if not args.apply:
        print("dry-run only; no table files written")
        return 0

    paths = {name: TABLES[name] for name in outputs}
    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in paths.items()}
    for backup in backups.values():
        if backup.exists():
            raise SystemExit(f"STOP: recovery copy already exists: {backup.name}")
    for name, backup in backups.items():
        shutil.copy2(paths[name], backup)
    written = []
    try:
        for name, data in outputs.items():
            path = paths[name]
            temp = path.with_name(path.name + ".tmp-s2-chp5-p123")
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
