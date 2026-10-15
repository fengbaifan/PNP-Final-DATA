#!/usr/bin/env python3
"""Review the p.106 S2 relation candidates and repair their endpoints."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l91-99"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "fc37671caac8205d1d3e4273243bb67d7d1a8e93ecbec4f5c1f9c30c3dbe6230"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "78b3483fdc48e22732f5e5089d27e8696010fc6871178f1b8d279a22e212c4fe",
    "entity-candidates.csv": "7ea09293bda6e942ba6ebd19085126df10be4ab853341851d6078ad031aa607f",
    "mentions.csv": "e7f79d6ff4407b4801de724c2e1a7f92230f74ad3a99e02c6c72d5eba4f7921b",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l91-99-relations-20261011"

UNCLASSIFIED_DUAL_IDS = {
    "st-chp4-sec-ii-l91-99-cassiano-commissioned-conventional-style",
    "st-chp4-sec-ii-l91-99-cassiano-copied-trattato",
    "st-chp4-sec-ii-l91-99-cassiano-deepened-poussins-culture",
    "st-chp4-sec-ii-l91-99-cassiano-gave-set-to-chantelou",
    "st-chp4-sec-ii-l91-99-cassiano-kept-original-drawings-and-copied-set",
    "st-chp4-sec-ii-l91-99-cassiano-owned-leonardo-attributed-portraits",
    "st-chp4-sec-ii-l91-99-cassiano-prepared-publication-and-chose-poussin",
    "st-chp4-sec-ii-l91-99-cassiano-saw-leonardo-paintings-fontainebleau",
    "st-chp4-sec-ii-l91-99-errard-embellished-drawings-and-poussin-objected",
    "st-chp4-sec-ii-l91-99-leonardo-treatise-in-barberini-library",
    "st-chp4-sec-ii-l91-99-mazenta-collection-reconstructed",
    "st-chp4-sec-ii-l91-99-poussin-acknowledged-paper-museum-debt",
    "st-chp4-sec-ii-l91-99-poussin-demands-rare-and-simple",
    "st-chp4-sec-ii-l91-99-poussin-drawings-compared-with-leonardo-sketches",
    "st-chp4-sec-ii-l91-99-poussin-drawings-fine-but-not-enthusiastic",
    "st-chp4-sec-ii-l91-99-poussin-later-tribute-to-leonardo",
    "st-chp4-sec-ii-l91-99-poussin-mixed-feelings-about-leonardo",
    "st-chp4-sec-ii-l91-99-poussin-not-isolated-before-paris-visit",
    "st-chp4-sec-ii-l91-99-poussin-proposes-marriage-of-peleus",
    "st-chp4-sec-ii-l91-99-publication-irritated-poussin",
    "st-chp4-sec-ii-l91-99-seven-sacraments-series-begun-fragment",
}

RELATION_NOTES = {
    "st-chp4-sec-ii-l91-99-cassiano-commissioned-conventional-style": "Haskell reports Cassiano commissioning Poussin for a more conventional kind of picture; no specific work is named.",
    "st-chp4-sec-ii-l91-99-cassiano-copied-trattato": "Haskell reports that Cassiano copied his version of the Trattato around 1635; distinguish this copy from Leonardo's source manuscript and the later publication.",
    "st-chp4-sec-ii-l91-99-cassiano-deepened-poussins-culture": "This is Haskell's interpretation of Cassiano's intellectual influence on Poussin, not an independently verified causal finding.",
    "st-chp4-sec-ii-l91-99-cassiano-gave-set-to-chantelou": "The recipient endpoint is Paul Fréart de Chantelou; the set's mixed manuscript-and-drawing contents remain in the evidence context.",
    "st-chp4-sec-ii-l91-99-cassiano-kept-original-drawings-and-copied-set": "The narrowed claim records Cassiano retaining Poussin's original drawings; the act of copying is recorded separately.",
    "st-chp4-sec-ii-l91-99-cassiano-owned-leonardo-attributed-portraits": "Haskell reports a group of two portraits owned by Cassiano and attributed to Leonardo; one portrait's copy status remains qualified.",
    "st-chp4-sec-ii-l91-99-cassiano-saw-leonardo-paintings-fontainebleau": "This row records the Leda only; the St John the Baptist is a separate work endpoint. Fontainebleau is not narrowed to a particular building or collection.",
    "st-chp4-sec-ii-l91-99-errard-embellished-drawings-and-poussin-objected": "Haskell says Errard added backgrounds to the drawings before engraving; Poussin's angry description is reported speech, not an objective assessment.",
    "st-chp4-sec-ii-l91-99-leonardo-treatise-in-barberini-library": "This is Haskell's report of a manuscript in the Barberini library; the cited footnote is a lead, not independent manuscript examination.",
    "st-chp4-sec-ii-l91-99-mazenta-collection-reconstructed": "The narrowed claim records the collection's dispersal before Mazenta's death; reconstruction by Arconato is recorded separately.",
    "st-chp4-sec-ii-l91-99-poussin-acknowledged-paper-museum-debt": "Haskell attributes the acknowledgment to Poussin and describes him as a 'pupil' of Cassiano's paper museum; no separate Poussin letter is identified here.",
    "st-chp4-sec-ii-l91-99-poussin-demands-rare-and-simple": "This remains Haskell's meta-claim about scarce evidence for Poussin's demands on Cassiano; no particular demand is asserted to be simple beyond the author's qualification.",
    "st-chp4-sec-ii-l91-99-poussin-drawings-compared-with-leonardo-sketches": "The endpoints are the two compared work groups: Poussin's drawings and Leonardo's sketches, not Poussin and his own drawings.",
    "st-chp4-sec-ii-l91-99-poussin-drawings-fine-but-not-enthusiastic": "The narrowed claim records Poussin's qualified response to the illustration task; the separate scalar quality assessment is not an entity relation.",
    "st-chp4-sec-ii-l91-99-poussin-later-tribute-to-leonardo": "Haskell describes a later tribute by Poussin to Leonardo but does not identify its form in this segment.",
    "st-chp4-sec-ii-l91-99-poussin-mixed-feelings-about-leonardo": "This is Haskell's report of Poussin's mixed attitude, including a nested quotation; the quotation is not independently sourced here.",
    "st-chp4-sec-ii-l91-99-poussin-proposes-marriage-of-peleus": "The letter expresses Poussin's willingness to undertake the proposed subject; it does not establish that a painting was completed.",
    "st-chp4-sec-ii-l91-99-publication-irritated-poussin": "Haskell attributes Poussin's irritation to the actual publication; the identified publication remains a source-bounded candidate.",
    "st-chp4-sec-ii-l91-99-seven-sacraments-series-begun-fragment": "Haskell says Poussin began the series in the second half of the 1630s; the unfinished 'Both the' comparison continues in the next segment.",
}

FALSE_NOTES = {
    "st-chp4-sec-ii-l91-99-cassiano-prepared-publication-and-chose-poussin": "The narrowed claim is about the manuscript copy's intended publication purpose; it is a scalar property, not a relation between Cassiano and Poussin. The selection of Poussin is recorded separately.",
    "st-chp4-sec-ii-l91-99-poussin-not-isolated-before-paris-visit": "This is Haskell's assessment of Poussin's social position before a visit; Paris is a temporal locator, not the object of a relation.",
}

NEW_STATEMENTS = (
    "st-chp4-sec-ii-l91-99-cassiano-selected-poussin-as-illustrator",
    "st-chp4-sec-ii-l91-99-cassiano-proposed-peleus-subject-to-poussin",
    "st-chp4-sec-ii-l91-99-cassiano-had-poussin-drawings-copied",
    "st-chp4-sec-ii-l91-99-arconato-reconstructed-mazenta-collection",
    "st-chp4-sec-ii-l91-99-st-john-seen-at-fontainebleau",
    "st-chp4-sec-ii-l91-99-poussin-friend-of-chantelou",
    "st-chp4-sec-ii-l91-99-chantelou-took-set-to-paris",
    "st-chp4-sec-ii-l91-99-treatise-published-at-paris",
    "st-chp4-sec-ii-l91-99-cassiano-acquaintance-of-arconato",
    "st-chp4-sec-ii-l91-99-poussin-worked-for-cassiano-on-seven-sacraments",
    "st-chp4-sec-ii-l91-99-poussin-wrote-to-cassiano-from-paris",
    "st-chp4-sec-ii-l91-99-resulting-drawings-described-as-fine",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="",
    )


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_quote(body: str, phrase: str) -> str:
    start = body.find(phrase)
    if start < 0:
        raise SystemExit("preflight failed: source phrase absent: " + phrase)
    return body[start:start + len(phrase)]


def make_statement(statement_id: str, subject: str, predicate: str, obj: str | None,
                   phrase: str, line_start: int, line_end: int, claim: str, note: str,
                   mentioned: list[str], body: str, *, relation: bool = True,
                   text_layer: str = "authorial narrative", extra: dict | None = None) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": 17,
        "printed_page_locator": "p.106",
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": note,
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": source_quote(body, phrase),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }


def set_classification(row: dict, decision: bool, note: str) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = decision
    qualifiers["relation_candidate_note"] = note


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed plan after all preflight checks")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    if sha(source_bytes) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source hash changed")
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    if source_lines[90] != "[Page 106]":
        raise SystemExit("preflight failed: printed-page marker changed")
    body = "\n".join(source_lines[90:99])
    if sha(body.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("preflight failed: exact p.106 segment body changed")

    segments = read_jsonl(SEGMENTS)
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if segment is None or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("preflight failed: segment manifest changed")

    paths = {name: TABLES / name for name in EXPECTED_SHA256}
    before_hashes = {}
    for name, path in paths.items():
        before_hashes[name] = sha(path.read_bytes())
        if before_hashes[name] != EXPECTED_SHA256[name]:
            raise SystemExit(f"preflight failed: {name} hash {before_hashes[name]} != expected {EXPECTED_SHA256[name]}")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates, candidate_fields = read_csv(paths["entity-candidates.csv"])
    mentions, mention_fields = read_csv(paths["mentions.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    segment_statements = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_pending = {
        row["statement_id"] for row in segment_statements
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
        and "relation_candidate" not in row.get("qualifiers", {})
    }
    if actual_pending != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit("preflight failed: unclassified dual-statement set changed")
    if set(RELATION_NOTES) | set(FALSE_NOTES) != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit("preflight failed: decisions do not cover exactly the pending dual statements")

    segment_mentions = [row for row in mentions if row.get("segment_id") == SEGMENT_ID]
    bad_spans = [row["mention_id"] for row in segment_mentions
                 if body[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]]
    if len(segment_mentions) != 50 or bad_spans:
        raise SystemExit(f"preflight failed: p.106 mention spans changed: count={len(segment_mentions)}, bad={bad_spans[:5]}")
    subject_mention = mention_by_id.get("m-s2-chp4-surface-f93a5e50eadd7a24")
    if subject_mention is None or subject_mention.get("candidate_id") != "cand-0840" or subject_mention.get("surface_form") != "subject":
        raise SystemExit("preflight failed: generic 'subject' mention mapping changed")

    required_candidates = {
        "cand-0115": "person", "cand-0648": "person", "cand-0979": "person",
        "cand-1390": "person", "cand-1601": "person", "cand-1984": "person",
        "cand-2036": "person", "cand-2045": "archive", "cand-4653": "place",
        "cand-4777": "place", "cand-5777": "work", "cand-5778": "archive",
        "cand-5779": "work", "cand-5780": "work", "cand-5781": "work",
        "cand-5784": "work", "cand-5785": "work", "cand-5786": "archive",
        "cand-5787": "archive", "cand-5788": "archive", "cand-5789": "work",
    }
    for cid, expected_type in required_candidates.items():
        if cid not in candidate_by_id or candidate_by_id[cid].get("suggested_type", "") != expected_type:
            raise SystemExit(f"preflight failed: candidate boundary/type changed for {cid}")
    if any(sid in statement_by_id for sid in NEW_STATEMENTS):
        raise SystemExit("preflight failed: a planned statement ID already exists")

    def stmt(suffix: str) -> dict:
        key = "st-chp4-sec-ii-l91-99-" + suffix
        if key not in statement_by_id:
            raise SystemExit("preflight failed: expected statement missing: " + key)
        return statement_by_id[key]

    # Split compound claims and correct endpoints before recording the decisions.
    correspondence = stmt("cassiano-corresponded-with-leonardo-manuscript-owners")
    correspondence["object_candidate_id"] = "cand-1601"
    correspondence["predicate"] = "corresponded_with"
    correspondence["qualifiers"]["claim"] = "Haskell says Cassiano began corresponding with scholars and manuscript owners, notably the Barnabite monk Ambrogio Mazenta."
    correspondence["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-1601", "cand-1390", "cand-5778"]

    gave_set = stmt("cassiano-gave-set-to-chantelou")
    gave_set["object_candidate_id"] = "cand-0648"
    gave_set["predicate"] = "gave_copy_set_to"
    gave_set["original_quote"] = source_quote(body, "This set he gave to Poussin")
    gave_set["qualifiers"]["claim"] = "Haskell says Cassiano gave the set containing his manuscript version and copied drawings to Paul Fréart de Chantelou."
    gave_set["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-1984", "cand-5786", "cand-0648", "cand-2045", "cand-5784"]

    retained = stmt("cassiano-kept-original-drawings-and-copied-set")
    retained["predicate"] = "retained_original_drawings"
    retained["original_quote"] = source_quote(body, "Cassiano kept the original drawings for himself")
    retained["qualifiers"]["claim"] = "Haskell says Cassiano retained Poussin's original drawings."
    retained["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-1984", "cand-5784"]

    planned_copy = stmt("cassiano-prepared-publication-and-chose-poussin")
    planned_copy["subject_candidate_id"] = "cand-2045"
    planned_copy["object_candidate_id"] = None
    planned_copy["predicate"] = "designed_for_publication"
    planned_copy["original_quote"] = source_quote(body, "His copy of the Treatise was designed for publication")
    planned_copy["qualifiers"]["claim"] = "Haskell says Cassiano's copy of the Treatise was designed for publication."
    planned_copy["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-2045", "cand-1390"]

    saw_leda = stmt("cassiano-saw-leonardo-paintings-fontainebleau")
    saw_leda["object_candidate_id"] = "cand-5779"
    saw_leda["predicate"] = "saw_work_at_fontainebleau"
    saw_leda["qualifiers"]["claim"] = "Haskell says Cassiano had seen Leonardo's Leda at Fontainebleau."
    saw_leda["qualifiers"]["mentioned_candidate_ids"] = ["cand-2036", "cand-5779", "cand-4595"]

    collection_dispersed = stmt("mazenta-collection-reconstructed")
    collection_dispersed["subject_candidate_id"] = "cand-5788"
    collection_dispersed["object_candidate_id"] = "cand-1601"
    collection_dispersed["predicate"] = "dispersed_before_owner_death"
    collection_dispersed["qualifiers"]["claim"] = "Haskell says Mazenta's important Leonardo manuscript collection had been dispersed before his death."
    collection_dispersed["qualifiers"]["mentioned_candidate_ids"] = ["cand-1601", "cand-5788"]

    comparison = stmt("poussin-drawings-compared-with-leonardo-sketches")
    comparison["subject_candidate_id"] = "cand-5784"
    comparison["object_candidate_id"] = "cand-5785"
    comparison["predicate"] = "more_finished_than"
    comparison["qualifiers"]["claim"] = "Haskell compares Poussin's vigorous drawings as more finished than Leonardo's shorthand sketches, while noting that they were not considered elegant enough for the occasion."
    comparison["qualifiers"]["mentioned_candidate_ids"] = ["cand-1984", "cand-5784", "cand-1390", "cand-5785"]

    drawing_response = stmt("poussin-drawings-fine-but-not-enthusiastic")
    drawing_response["predicate"] = "not_enthusiastic_about_drawing_task"
    drawing_response["original_quote"] = source_quote(body, "Poussin does not seem to have been enthusiastic about the task.")
    drawing_response["qualifiers"]["claim"] = "Haskell says Poussin does not seem to have been enthusiastic about the illustration task."
    drawing_response["qualifiers"]["mentioned_candidate_ids"] = ["cand-1984", "cand-5784"]
    drawing_response["qualifiers"].pop("ocr_corrections", None)

    not_isolated = stmt("poussin-not-isolated-before-paris-visit")
    not_isolated["object_candidate_id"] = None

    proposal = stmt("poussin-proposes-marriage-of-peleus")
    proposal["predicate"] = "expressed_willingness_to_undertake_proposed_subject"
    proposal["qualifiers"]["claim"] = "In a letter cited by Haskell, Poussin says he would like to undertake the Marriage of Peleus subject proposed by Cassiano; this does not establish a completed painting."
    proposal["qualifiers"]["mentioned_candidate_ids"] = ["cand-1984", "cand-2036", "cand-5777"]

    # The generic index subentry 'Contracts: subject' is not the referent here.
    subject_mention["candidate_id"] = "cand-5777"
    subject_mention["note"] = "Generic anaphoric reference to the proposed Marriage of Peleus subject; it does not refer to the index subentry 'Contracts: subject'."

    additions = [
        make_statement(NEW_STATEMENTS[0], "cand-2036", "selected_poussin_to_illustrate_leonardos_notes", "cand-1984",
                       "he chose Poussin to illustrate Leonardo", 96, 96,
                       "Haskell says Cassiano chose Poussin to illustrate Leonardo's notes.",
                       "This records the selection relation separately from the copy's publication purpose; the referenced notes are not a separate manuscript object here.",
                       ["cand-2036", "cand-1984", "cand-2045", "cand-5778"], body),
        make_statement(NEW_STATEMENTS[1], "cand-2036", "proposed_painting_subject_to_artist", "cand-1984",
                       "the subject you propose of the Marriage of Peleus", 93, 93,
                       "Poussin's quoted letter identifies Cassiano as the person who proposed the Marriage of Peleus subject to him.",
                       "The proposal is reported through Haskell's quotation of Poussin; no commission or completed painting is established.",
                       ["cand-2036", "cand-1984", "cand-5777"], body, text_layer="quoted letter in authorial narrative"),
        make_statement(NEW_STATEMENTS[2], "cand-2036", "had_drawings_copied_with_manuscript_version", "cand-5784",
                       "had them copied together with the version he had made of the manuscript", 96, 96,
                       "Haskell says Cassiano had copies made of Poussin's original drawings alongside his manuscript version.",
                       "This separates copying from Cassiano's retention of the originals; the copies are not individually identified.",
                       ["cand-2036", "cand-1984", "cand-5784", "cand-2045"], body),
        make_statement(NEW_STATEMENTS[3], "cand-5788", "largely_reconstructed_by", "cand-0115",
                       "had then been largely reconstructed by Galeazzo Arconato", 96, 96,
                       "Haskell says Galeazzo Arconato largely reconstructed Mazenta's dispersed Leonardo manuscript collection.",
                       "The source says 'largely'; it does not provide an item list or claim full reconstruction.",
                       ["cand-5788", "cand-0115", "cand-1601"], body),
        make_statement(NEW_STATEMENTS[4], "cand-2036", "saw_work_at_fontainebleau", "cand-5780",
                       "St John the Baptist at Fontainebleau", 95, 96,
                       "Haskell says Cassiano had seen Leonardo's St John the Baptist at Fontainebleau.",
                       "This is the second named painting and is kept separate from the Leda; no specific building or collection at Fontainebleau is identified.",
                       ["cand-2036", "cand-5780", "cand-4595"], body),
        make_statement(NEW_STATEMENTS[5], "cand-1984", "friend_of", "cand-0648",
                       "friend, Paul Freart de Chantelou", 96, 96,
                       "Haskell identifies Paul Fréart de Chantelou as Poussin's friend.",
                       "The friendship is stated in the narrative; no date or further particulars are supplied.",
                       ["cand-1984", "cand-0648"], body),
        make_statement(NEW_STATEMENTS[6], "cand-0648", "took_copy_set_to", "cand-4653",
                       "who took it to Paris", 96, 96,
                       "Haskell says Chantelou took the copied manuscript-and-drawing set to Paris.",
                       "The set is identified in context as the mixed manuscript-and-drawing copy; no destination building is specified.",
                       ["cand-0648", "cand-5786", "cand-4653"], body),
        make_statement(NEW_STATEMENTS[7], "cand-5787", "published_at", "cand-4653",
                       "where the Treatise was published in 1651", 96, 96,
                       "Haskell reports that the Treatise publication with Poussin drawings appeared in Paris in 1651.",
                       "The publication's full edition metadata are not supplied; the footnote remains a source lead rather than an independently checked edition.",
                       ["cand-5787", "cand-4653", "cand-0648", "cand-5786"], body),
        make_statement(NEW_STATEMENTS[8], "cand-2036", "acquaintance_of", "cand-0115",
                       "another acquaintance of Cassiano", 96, 96,
                       "Haskell identifies Galeazzo Arconato as another acquaintance of Cassiano.",
                       "This is the author's stated social connection; no duration or further context is given.",
                       ["cand-2036", "cand-0115"], body),
        make_statement(NEW_STATEMENTS[9], "cand-1984", "worked_for_patron_on_series", "cand-2036",
                       "work for Cassiano consisted in the series of the Seven Sacraments", 99, 99,
                       "Haskell identifies the Seven Sacraments series as part of Poussin's work for Cassiano.",
                       "This records the patron-artist relation expressed in the sentence; the next segment continues Haskell's interpretation of the series.",
                       ["cand-1984", "cand-2036", "cand-5789"], body),
        make_statement(NEW_STATEMENTS[10], "cand-1984", "wrote_from_paris_to", "cand-2036",
                       "Poussin writing to him from Paris", 93, 93,
                       "Haskell says Poussin wrote to Cassiano from Paris before quoting the letter cited in footnote 1.",
                       "The footnote dates the cited letter to 4 April 1642; the correspondence edition is not independently collated.",
                       ["cand-1984", "cand-2036", "cand-4653"], body),
        make_statement(NEW_STATEMENTS[11], "cand-5784", "described_as_very_fine", None,
                       "the resulting drawings are very sine", 96, 96,
                       "Haskell describes the resulting Poussin drawings as very fine.",
                       "This is a scalar assessment of the drawings; the scan reads 'fine' where the OCR has 'sine'.",
                       ["cand-5784", "cand-1984"], body, relation=False,
                       text_layer="authorial assessment", extra={"ocr_corrections": [{"source_line": 96, "source_form": "sine", "print_form": "fine"}]}),
    ]

    for statement_id, note in RELATION_NOTES.items():
        set_classification(statement_by_id[statement_id], True, note)
    set_classification(correspondence, True,
                       "Haskell names Ambrogio Mazenta as a notable correspondent; other scholars and manuscript owners remain unnamed.")
    for statement_id, note in FALSE_NOTES.items():
        set_classification(statement_by_id[statement_id], False, note)

    statements.extend(additions)
    for row in additions:
        q = row["qualifiers"]
        source_span = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
        if row["original_quote"] not in source_span:
            raise SystemExit(f"preflight failed: added quote outside source lines for {row['statement_id']}")

    statement_ids = [row["statement_id"] for row in statements]
    if len(set(statement_ids)) != len(statement_ids):
        raise SystemExit("preflight failed: duplicate statement ID")
    candidate_id_set = set(candidate_by_id)
    for row in statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_id_set:
                raise SystemExit(f"preflight failed: missing endpoint candidate {endpoint}")

    segment_after = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    dual_after = [row for row in segment_after if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    segment_status = {
        "statements": len(segment_after),
        "dual": len(dual_after),
        "true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in dual_after),
        "false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in dual_after),
        "unclassified": sum("relation_candidate" not in row.get("qualifiers", {}) for row in dual_after),
    }
    totals_after = {"statements": len(statements), "candidates": len(candidates), "mentions": len(mentions)}
    expected_status = {"statements": 36, "dual": 31, "true": 31, "false": 0, "unclassified": 0}
    if totals_after != {"statements": 12983, "candidates": 11625, "mentions": 27563} or segment_status != expected_status:
        raise SystemExit(f"preflight failed: unexpected totals/state: {totals_after}, {segment_status}")

    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "table_sha256_before": before_hashes,
        "pending_dual_statements": len(actual_pending),
        "pending_ids": sorted(actual_pending),
        "decision": {"relation_candidates_true": 31, "single_endpoint_or_scalar_nonrelations": 3},
        "endpoint_and_atomicity_repairs": [
            "correspondence endpoint -> Mazenta",
            "copy purpose split from Cassiano's selection of Poussin",
            "Fontainebleau sighting split into two paintings",
            "Mazenta collection dispersal split from Arconato reconstruction",
            "original drawings retained split from copies made",
            "Poussin/Leonardo drawing comparison endpoints corrected",
            "Paris visit removed as endpoint of isolation assessment",
            "generic Contracts: subject mention remapped to proposed Marriage of Peleus subject",
            "gift recipient, Chantelou friendship, travel, and 1651 publication recorded separately",
        ],
        "new_statement_ids": list(NEW_STATEMENTS),
        "segment_after": segment_status,
        "totals_after": totals_after,
        "backups": [f"{name}.{BACKUP_SUFFIX}" for name in ("book-statements.jsonl", "mentions.csv")],
    }
    print(json.dumps(plan, ensure_ascii=False, indent=2))

    if not args.apply:
        return

    statements_path = paths["book-statements.jsonl"]
    mentions_path = paths["mentions.csv"]
    backups = [statements_path.with_name(statements_path.name + "." + BACKUP_SUFFIX),
               mentions_path.with_name(mentions_path.name + "." + BACKUP_SUFFIX)]
    if any(path.exists() for path in backups):
        raise SystemExit("apply refused: a recovery backup with this suffix already exists")
    shutil.copy2(statements_path, backups[0])
    shutil.copy2(mentions_path, backups[1])

    write_jsonl(statements_path, statements)
    write_csv(mentions_path, mentions, mention_fields)

    written_statements = read_jsonl(statements_path)
    written_mentions, _ = read_csv(mentions_path)
    written_segment = [row for row in written_statements if row.get("segment_id") == SEGMENT_ID]
    written_dual = [row for row in written_segment if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    if len(written_segment) != 36 or len(written_dual) != 31 or any("relation_candidate" not in row.get("qualifiers", {}) for row in written_dual):
        raise SystemExit("post-write verification failed: p.106 segment state mismatch; recovery backups retained")
    written_subject = next(row for row in written_mentions if row["mention_id"] == "m-s2-chp4-surface-f93a5e50eadd7a24")
    if written_subject.get("candidate_id") != "cand-5777":
        raise SystemExit("post-write verification failed: proposed-subject mention did not remap; recovery backups retained")
    print("apply complete")
    print("statement_sha256=" + sha(statements_path.read_bytes()))
    print("mention_sha256=" + sha(mentions_path.read_bytes()))
    print("backups=" + ",".join(str(path.name) for path in backups))


if __name__ == "__main__":
    main()
