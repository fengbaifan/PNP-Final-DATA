#!/usr/bin/env python3
"""Classify p.116 S2 statements and add source-bounded entity groups."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l191-205"
NOTE_SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "10e57b2801d3d0c7e6187820e069899b9bfbaee94a6222ef770f6a523123fff6",
    "entity-candidates.csv": "b8041804a7ec4e15b3d6ed802b6ed2541308ffc39af29e377d699e32c50c949a",
    "mentions.csv": "a7b67d1dd402ceb4633f6f23115513c2801770a3163b456fdfe0853225f0b782",
}
BACKUP_SUFFIX = "bak-s2-chp4-p116-relations-20261011"

P116_IDS = {
    "st-chp4-sec-ii-p116-antiquities-visits",
    "st-chp4-sec-ii-p116-artist-offer",
    "st-chp4-sec-ii-p116-claude-demand",
    "st-chp4-sec-ii-p116-correspondence",
    "st-chp4-sec-ii-p116-court-meeting-1655",
    "st-chp4-sec-ii-p116-court-refusal",
    "st-chp4-sec-ii-p116-donna-olimpia-characterization",
    "st-chp4-sec-ii-p116-donna-olimpia-kinship",
    "st-chp4-sec-ii-p116-donna-olimpia-newswriter-reaction",
    "st-chp4-sec-ii-p116-donna-olimpia-portrait",
    "st-chp4-sec-ii-p116-four-pictures-continuation",
    "st-chp4-sec-ii-p116-inscription-interest",
    "st-chp4-sec-ii-p116-landscapes-social-metaphor",
    "st-chp4-sec-ii-p116-massimi-1653-patriarch",
    "st-chp4-sec-ii-p116-massimi-1654-nuncio",
    "st-chp4-sec-ii-p116-massimi-age-and-collection",
    "st-chp4-sec-ii-p116-massimi-claude-client-list",
    "st-chp4-sec-ii-p116-massimi-portrait-reading",
    "st-chp4-sec-ii-p116-massimi-reported-characterization",
    "st-chp4-sec-ii-p116-massimi-taste",
    "st-chp4-sec-ii-p116-massimi-velasquez-friendship",
    "st-chp4-sec-ii-p116-patron-records-social-fortunes",
    "st-chp4-sec-ii-p116-scholarship-standards",
    "st-chp4-sec-ii-p116-town-residence",
    "st-chp4-sec-ii-p116-two-claude-pictures-subjects",
    "st-chp4-sec-ii-p116-two-pictures-circumstances",
    "st-chp4-sec-ii-p116-velasquez-arrival",
    "st-chp4-sec-ii-p116-velasquez-greeted-by-barberini",
    "st-chp4-sec-ii-p116-velasquez-greeted-by-cassiano",
    "st-chp4-sec-ii-p116-velasquez-portrait-innocent",
    "st-chp4-sec-ii-p116-velasquez-portrait-massimi",
}
NOTE_IDS = {
    "st-chp4-sec-ii-p116note-fn1-collections",
    "st-chp4-sec-ii-p116note-fn2-harris-1958",
    "st-chp4-sec-ii-p116note-fn3-antonazzi",
    "st-chp4-sec-ii-p116note-fn3-giustiniani-volume",
    "st-chp4-sec-ii-p116note-fn3-inventory-locator",
    "st-chp4-sec-ii-p116note-fn4-harris-1960",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.split())


def excerpt(text: str, start: str, end: str) -> str:
    left = text.find(start)
    if left < 0 or text.find(start, left + 1) >= 0:
        raise SystemExit(f"source excerpt start is absent or ambiguous: {start!r}")
    right = text.find(end, left + len(start))
    if right < 0:
        raise SystemExit(f"source excerpt end is absent: {end!r}")
    return text[left:right + len(end)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write validated p.116 changes")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    if digest(source_bytes) != SOURCE_SHA256:
        raise SystemExit("source SHA-256 changed; stop and review the source")
    source_lines = source_bytes.decode("utf-8").splitlines()
    segment_text = "\n".join(source_lines[190:205])
    if not segment_text.startswith("[Page 116]\n"):
        raise SystemExit("p.116 segment boundary differs from the audited source")
    line = {n: source_lines[n - 1] for n in range(191, 217)}

    paths = {name: TABLES / name for name in EXPECTED_SHA256}
    originals = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED_SHA256.items():
        actual = digest(originals[name])
        if actual != expected:
            raise SystemExit(f"{name} changed since p.115; expected {expected}, got {actual}")

    rows: list[dict] = []
    raw_statement_lines: list[bytes] = []
    for raw in originals["book-statements.jsonl"].splitlines(keepends=True):
        data = raw.rstrip(b"\r\n")
        if data:
            rows.append(json.loads(data.decode("utf-8")))
        raw_statement_lines.append(raw)
    p116 = [r for r in rows if r.get("segment_id") == SEGMENT_ID]
    p116_notes = [
        r for r in rows
        if r.get("segment_id") == NOTE_SEGMENT_ID
        and r.get("statement_id") in NOTE_IDS
    ]
    if {r["statement_id"] for r in p116} != P116_IDS or len(p116) != 31:
        raise SystemExit(f"expected exactly 31 original p.116 statements; found {len(p116)}")
    if {r["statement_id"] for r in p116_notes} != NOTE_IDS:
        raise SystemExit(f"expected exactly six p.116 footnote statements; found {len(p116_notes)}")
    for row in p116 + p116_notes:
        if row.get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified; review before overwriting: {row['statement_id']}")
    for row in p116:
        if norm(row.get("original_quote", "")) not in norm(segment_text):
            raise SystemExit(f"original quote does not match p.116 source: {row['statement_id']}")

    mention_rows = list(csv.DictReader(io.StringIO(
        originals["mentions.csv"].decode("utf-8"), newline=""
    )))
    p116_mentions = [r for r in mention_rows if r.get("segment_id") == SEGMENT_ID]
    if len(p116_mentions) != 44:
        raise SystemExit(f"expected 44 pre-existing p.116 mentions; found {len(p116_mentions)}")
    for mention in p116_mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing mention span mismatch: {mention['mention_id']}")
    target_mention = next(
        (r for r in mention_rows if r["mention_id"] == "m-chp4-sec-ii-p116-0030"),
        None,
    )
    if not target_mention or target_mention["candidate_id"] != "cand-1498":
        raise SystemExit("Donna Olimpia mention no longer has the expected pre-review mapping")

    source_index = {n: source_lines[n - 1] for n in range(191, 217)}
    q = lambda n, start, end: excerpt(source_index[n], start, end)
    updates = {
        "st-chp4-sec-ii-p116-antiquities-visits": {
            "relation": True, "subject": "cand-1564", "object": "cand-11663",
            "predicate": "visited_local_antiquities",
            "note": "Haskell explicitly says Massimi visited this source-bounded set while seeking relaxation. The set mixes a theatre, statue fragments, and ruins; do not assign individual identities or force one type.",
            "mentioned": ["cand-1564", "cand-11663"],
        },
        "st-chp4-sec-ii-p116-artist-offer": {
            "relation": True, "subject": "cand-2709", "object": "cand-1564",
            "predicate": "offered_assistance_to",
            "claim": "Haskell says Velasquez offered to be of service to Massimi in any way he could.",
            "quote": q(203, "With some courage", "could"),
            "note": "This row records the offer of assistance only; the anticipated court meeting is a separate claim.",
            "mentioned": ["cand-2709", "cand-1564"],
            "source_start": 203, "source_end": 203,
        },
        "st-chp4-sec-ii-p116-claude-demand": {
            "relation": True, "subject": "cand-11656", "object": "cand-0767",
            "predicate": "demanded_the_work_of",
            "note": "The source explicitly says Claude was in overwhelming demand from an unnamed plural of highly placed and powerful people; no individuals are identified.",
            "mentioned": ["cand-11656", "cand-0767"],
        },
        "st-chp4-sec-ii-p116-correspondence": {
            "relation": True, "subject": "cand-1564", "object": "cand-2709",
            "predicate": "wrote_to_while_awaiting_madrid_reception",
            "claim": "While waiting to be received in Madrid, Massimi wrote to Velasquez.",
            "quote": q(203, "While still waiting", "Velasquez"),
            "note": "This records Massimi's outgoing letter only; Velasquez's friendly reply is a distinct claim.",
            "mentioned": ["cand-1564", "cand-2709"],
            "source_start": 203, "source_end": 203,
        },
        "st-chp4-sec-ii-p116-court-meeting-1655": {
            "relation": True, "subject": "cand-2709", "object": "cand-1564",
            "predicate": "anticipated_court_meeting_became_possible_after_accession",
            "note": "The passage says the anticipated meeting became possible after Alexander VII's accession in 1655; it does not say that the meeting actually occurred.",
            "mentioned": ["cand-2709", "cand-1564", "cand-0665"],
            "qualifiers": {"time": "1655, after Alexander VII's accession",
                           "qualification": "Possibility of a meeting, not evidence that it took place."},
        },
        "st-chp4-sec-ii-p116-court-refusal": {
            "relation": True, "subject": "cand-1896", "object": "cand-1564",
            "predicate": "refused_to_receive_at_court",
            "claim": "Haskell says Philip IV refused to receive Massimi at court, citing alleged friendliness with the French.",
            "quote": q(200, "Philip IV refusing", "French."),
            "note": "The refusal and its stated rationale are kept distinct from the Spanish ambassador's intrigue; the reason is reported by Haskell, not independently verified.",
            "mentioned": ["cand-1896", "cand-1564", "cand-5968"],
            "source_start": 200, "source_end": 200,
            "qualifiers": {"qualification": "Reported rationale attributed to Philip IV; not independently verified."},
        },
        "st-chp4-sec-ii-p116-donna-olimpia-characterization": {
            "relation": False, "subject": "cand-1496",
            "note": "This is Haskell's evaluative characterization of Donna Olimpia, not a relation claim.",
            "mentioned": ["cand-1496", "cand-1819"],
        },
        "st-chp4-sec-ii-p116-donna-olimpia-kinship": {
            "relation": True, "subject": "cand-1496", "object": "cand-1819",
            "predicate": "sister_in_law_of",
            "note": "The source explicitly identifies Donna Olimpia as Innocent X's sister-in-law.",
            "mentioned": ["cand-1496", "cand-1819"],
        },
        "st-chp4-sec-ii-p116-donna-olimpia-newswriter-reaction": {
            "relation": True, "subject": "cand-1496", "object": "cand-11658",
            "predicate": "influence_entertained_and_outraged_newswriters",
            "note": "Haskell attributes both reactions to her court influence and names only an unspecified plural group of Roman newswriters.",
            "mentioned": ["cand-1496", "cand-11658"],
        },
        "st-chp4-sec-ii-p116-donna-olimpia-portrait": {
            "relation": True, "subject": "cand-5970", "object": "cand-1564",
            "predicate": "acquired_by",
            "claim": "Massimi acquired the portrait of Donna Olimpia from Velasquez.",
            "note": "The work is the object acquired by Massimi. The source identifies Velasquez as the person from whom it was acquired but does not say here that he created this particular portrait.",
            "mentioned": ["cand-5970", "cand-1564", "cand-2709", "cand-1496"],
        },
        "st-chp4-sec-ii-p116-four-pictures-continuation": {
            "relation": True, "subject": "cand-5976", "object": "cand-2709",
            "predicate": "created_by",
            "claim": "Haskell says Velasquez painted four more pictures in the next few years; p.117 continues that these were portraits for Massimi.",
            "note": "The p.116 sentence establishes the four-picture group and its maker. The p.117 continuation supplies Massimi and the sitters; the cross-page context does not establish a court meeting.",
            "mentioned": ["cand-5976", "cand-2709"],
        },
        "st-chp4-sec-ii-p116-inscription-interest": {
            "relation": True, "subject": "cand-1564", "object": "cand-11659",
            "predicate": "deciphered_inscriptions_for_research_of",
            "note": "Haskell says Massimi deciphered Hebrew and other inscriptions for the researches of unnamed learned friends in Italy; no friends are individually identified.",
            "mentioned": ["cand-1564", "cand-11659"],
        },
        "st-chp4-sec-ii-p116-landscapes-social-metaphor": {
            "relation": False,
            "note": "This is a counterfactual rhetorical contrast about the comfort Claude landscapes might offer to successful or disgraced people; it does not assert an entity-to-entity relation.",
            "qualifiers": {"ocr_corrections": [
                {"source_line": 192, "source_form": "Use", "print_form": "life"},
            ]},
        },
        "st-chp4-sec-ii-p116-massimi-1653-patriarch": {
            "relation": False, "object": None,
            "predicate": "was_made_patriarch_of_jerusalem",
            "note": "This records an office held by Massimi as a scalar biographical claim. Jerusalem is mentioned as part of the title, but the place candidate is not the office; no office entity is created under the current taxonomy.",
            "mentioned": ["cand-1564", "cand-4396"],
            "qualifiers": {"time": "1653"},
        },
        "st-chp4-sec-ii-p116-massimi-1654-nuncio": {
            "relation": True, "subject": "cand-1564", "object": "cand-5667",
            "predicate": "sent_as_nuncio_to",
            "note": "The source says Massimi was sent as nuncio to Spain in 1654; the sending authority is not named.",
            "mentioned": ["cand-1564", "cand-5667"],
            "qualifiers": {"time": "1654"},
        },
        "st-chp4-sec-ii-p116-massimi-age-and-collection": {
            "relation": False, "object": None,
            "predicate": "aged_33_in_1653",
            "claim": "Haskell says Massimi was 33 in 1653.",
            "quote": q(198, "In 1653 Massimi", "at the age of 33"),
            "note": "Age is a scalar biographical claim. The collection and its unnamed makers are recorded separately.",
            "mentioned": ["cand-1564"],
            "source_start": 198, "source_end": 198,
            "qualifiers": {"time": "1653"},
        },
        "st-chp4-sec-ii-p116-massimi-claude-client-list": {
            "relation": True, "subject": "cand-1564", "object": "cand-0767",
            "predicate": "listed_as_client_of",
            "claim": "Haskell says Massimi appeared among Claude's clients in the late 1640s, alongside Camillo Pamfili and unnamed new clients.",
            "quote": q(193, "we find lais name", "Claude’s clients."),
            "note": "The source includes Massimi in Claude's client list; Camillo Pamfili and the unnamed new clients are split into separate group-level claims.",
            "mentioned": ["cand-1564", "cand-0767", "cand-1814", "cand-11657"],
            "source_start": 193, "source_end": 193,
            "qualifiers": {"time": "late 1640s",
                           "ocr_corrections": [{"source_line": 193, "source_form": "lais", "print_form": "his"}]},
        },
        "st-chp4-sec-ii-p116-massimi-portrait-reading": {
            "relation": False, "subject": "cand-4110", "object": None,
            "predicate": "portrait_features_suggest_surly_coarse_character",
            "claim": "Haskell interprets the portrait's features as suggesting a surly and coarse character.",
            "note": "This is Haskell's visual interpretation of the portrait, not a verified statement about Massimi's personality.",
            "mentioned": ["cand-4110", "cand-1564"],
        },
        "st-chp4-sec-ii-p116-massimi-reported-characterization": {
            "relation": False,
            "note": "This is an attributed summary of reports about Massimi's cultivation and appearance, not an entity relation.",
            "mentioned": ["cand-1564"],
        },
        "st-chp4-sec-ii-p116-massimi-taste": {
            "relation": True, "subject": "cand-1564", "object": "cand-0767",
            "predicate": "appreciated_pictures_by",
            "claim": "Haskell says Massimi appreciated Claude's pictures.",
            "quote": q(192, "Camillo Massimi", "pictures of Claude"),
            "note": "This row records appreciation of Claude's pictures only; Poussin is a separate artist endpoint.",
            "mentioned": ["cand-1564", "cand-0767"],
            "source_start": 192, "source_end": 192,
        },
        "st-chp4-sec-ii-p116-massimi-velasquez-friendship": {
            "relation": True,
            "note": "Haskell explicitly describes a close friendship between Massimi and Velasquez; the later artistic consequences are not specified here.",
            "mentioned": ["cand-1564", "cand-2709"],
        },
        "st-chp4-sec-ii-p116-patron-records-social-fortunes": {
            "relation": False,
            "note": "This is Haskell's interpretive metaphor about Claude's patron records and broad social change, not a typed relation between bounded entities.",
            "qualifiers": {"ocr_corrections": [
                {"source_line": 192, "source_form": "Use", "print_form": "life"},
            ]},
            "qualifiers": {"ocr_corrections": [
                {"source_line": 192, "source_form": "Use", "print_form": "life"},
            ]},
        },
        "st-chp4-sec-ii-p116-scholarship-standards": {
            "relation": False,
            "note": "This is an authorial evaluation of Massimi's attitude to prevailing scholarship standards, not an entity relation.",
            "mentioned": ["cand-1564"],
        },
        "st-chp4-sec-ii-p116-town-residence": {
            "relation": True, "subject": "cand-1564", "object": "cand-5967",
            "predicate": "resided_in_unnamed_town",
            "note": "Haskell says Massimi was forced to live in this unnamed town for a year; do not infer its identity from Valencia or Madrid.",
            "mentioned": ["cand-1564", "cand-5967", "cand-5966", "cand-3936"],
            "qualifiers": {"time": "one year, between the 1654 mission and the later Madrid reception"},
        },
        "st-chp4-sec-ii-p116-two-claude-pictures-subjects": {
            "relation": False,
            "note": "The two named works are presented as evidence for Haskell's claim about Massimi's unusual literary taste; the passage does not state ownership or another direct relation.",
            "mentioned": ["cand-1564", "cand-0772", "cand-0775", "cand-4179", "cand-5972", "cand-5973"],
            "qualifiers": {"ocr_corrections": [
                {"source_line": 193, "source_form": "large'pictures", "print_form": "large pictures"},
            ]},
        },
        "st-chp4-sec-ii-p116-two-pictures-circumstances": {
            "relation": True, "subject": "cand-11662", "object": "cand-1564",
            "predicate": "may_allude_to_massimi_circumstances",
            "note": "The plural pronoun applies to the two named Claude pictures as a pair. Haskell's possible allusion is preserved at group level; the source does not distinguish a separate allusion by each painting.",
            "mentioned": ["cand-11662", "cand-1564", "cand-1984", "cand-4144"],
            "qualifiers": {
                "qualification": "Haskell says the works may well conceal an allusion; this is an interpretive possibility, not a verified historical fact.",
                "ocr_corrections": [{"source_line": 193, "source_form": "Use of Moses", "print_form": "Life of Moses"}],
            },
        },
        "st-chp4-sec-ii-p116-velasquez-arrival": {
            "relation": True, "subject": "cand-2709", "object": "cand-4490",
            "predicate": "arrived_in",
            "note": "The source explicitly dates Velasquez's arrival in Rome to 1649.",
            "mentioned": ["cand-2709", "cand-4490"],
            "qualifiers": {"time": "1649"},
        },
        "st-chp4-sec-ii-p116-velasquez-greeted-by-barberini": {
            "relation": True,
            "note": "Haskell says Francesco Barberini greeted Velasquez on his arrival; this is separate from Cassiano's greeting.",
            "mentioned": ["cand-2709", "cand-0199"],
        },
        "st-chp4-sec-ii-p116-velasquez-greeted-by-cassiano": {
            "relation": True,
            "note": "Haskell says Cassiano dal Pozzo greeted Velasquez on his arrival; the paired wording is separated from Francesco Barberini's role.",
            "mentioned": ["cand-2709", "cand-2036"],
        },
        "st-chp4-sec-ii-p116-velasquez-portrait-innocent": {
            "relation": True, "subject": "cand-2715", "object": "cand-1819",
            "predicate": "has_subject",
            "claim": "Haskell identifies Innocent X as the subject of the Velasquez portrait listed in the index.",
            "note": "The work candidate is the index entry for Velasquez's portrait of Pope Innocent X; the source names the sitter but gives no separate title.",
            "mentioned": ["cand-2715", "cand-1819", "cand-2709"],
        },
        "st-chp4-sec-ii-p116-velasquez-portrait-massimi": {
            "relation": True, "subject": "cand-4110", "object": "cand-1564",
            "predicate": "has_subject",
            "claim": "Haskell identifies Camillo Massimi (Plate 20) as the sitter in the Velasquez portrait.",
            "note": "The existing work candidate is the accepted KU for the Portrait of Camillo Massimi; the named sitter is its subject.",
            "mentioned": ["cand-4110", "cand-1564", "cand-2709"],
        },
        "st-chp4-sec-ii-p116note-fn1-collections": {
            "relation": False,
            "note": "The footnote gives collection and bibliographic locators but does not map either painting to a specific collection; it is not independent verification.",
        },
        "st-chp4-sec-ii-p116note-fn2-harris-1958": {
            "relation": False,
            "note": "This footnote is a bibliographic locator only; it does not state a relation between Harris and the people or works discussed in the body.",
        },
        "st-chp4-sec-ii-p116note-fn3-antonazzi": {
            "relation": True, "subject": "cand-1564", "object": "cand-0112",
            "predicate": "took_along_with",
            "claim": "Haskell's note says Massimi had taken the miniaturist Antonio Maria Antonazzi with him.",
            "note": "The note's 'He' is resolved from its attachment and immediate context to Massimi. Preserve this as Haskell's reported claim, not an independently verified journey.",
            "mentioned": ["cand-1564", "cand-0112"],
            "qualifiers": {"qualification": "Pronoun resolved contextually to Massimi; no destination or date is stated."},
        },
        "st-chp4-sec-ii-p116note-fn3-giustiniani-volume": {
            "relation": False,
            "note": "This is a bibliographic locator for Giustiniani, not a relation claim about the volume's author, owner, or contents.",
        },
        "st-chp4-sec-ii-p116note-fn3-inventory-locator": {
            "relation": False,
            "note": "The note identifies a manuscript inventory as a citation locator; it does not state the inventory's authorship, ownership, or repository.",
        },
        "st-chp4-sec-ii-p116note-fn4-harris-1960": {
            "relation": False,
            "note": "This is a bibliographic locator only; the OCR year correction is retained in the footnote qualifier.",
        },
    }

    existing_by_id = {r["statement_id"]: r for r in p116 + p116_notes}
    if set(updates) != P116_IDS | NOTE_IDS:
        raise SystemExit("classification manifest does not cover all p.116 body and footnote statements")
    for sid, item in updates.items():
        row = existing_by_id[sid]
        qv = row["qualifiers"]
        qv["relation_candidate"] = item["relation"]
        qv["relation_candidate_note"] = item["note"]
        for key in ("subject", "object", "predicate", "claim", "quote"):
            if key not in item:
                continue
            if key == "subject":
                row["subject_candidate_id"] = item[key]
            elif key == "object":
                row["object_candidate_id"] = item[key]
            elif key == "predicate":
                row["predicate"] = item[key]
            elif key == "claim":
                qv["claim"] = item[key]
            elif key == "quote":
                row["original_quote"] = item[key]
        if "mentioned" in item:
            qv["mentioned_candidate_ids"] = item["mentioned"]
        for key, value in item.get("qualifiers", {}).items():
            qv[key] = value
        if "source_start" in item:
            qv["source_line_start"] = item["source_start"]
            qv["source_line_end"] = item["source_end"]

    def new_statement(statement_id: str, subject: str | None, object_: str | None, predicate: str,
                      claim: str, source_start: int, source_end: int, quote: str,
                      relation_note: str, mentioned: list[str],
                      qualification: str | None = None,
                      time: str | None = None) -> dict:
        qualifiers = {
            "source_line_start": source_start,
            "source_line_end": source_end,
            "pdf_physical_page": 27,
            "printed_page_locator": "p.116",
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": True,
            "relation_candidate_note": relation_note,
        }
        if qualification:
            qualifiers["qualification"] = qualification
        if time:
            qualifiers["time"] = time
        return {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": object_,
            "predicate": predicate,
            "qualifiers": qualifiers,
            "original_quote": quote,
            "origin": "book",
            "source_file": SOURCE_REL,
        }

    additions = [
        new_statement(
            "st-chp4-sec-ii-p116-artist-court-meeting-interest", "cand-2709", "cand-1564",
            "looked_forward_to_meeting_at_court",
            "Velasquez looked forward to seeing his former patron Massimi at court.",
            203, 203, q(203, "looked forward", "court."),
            "This records Velasquez's stated expectation only; the source does not say the meeting occurred.",
            ["cand-2709", "cand-1564"],
            qualification="Anticipated meeting; later passage says it became possible after 1655, not that it happened.",
        ),
        new_statement(
            "st-chp4-sec-ii-p116-massimi-velasquez-reply", "cand-2709", "cand-1564",
            "replied_to_letter",
            "Velasquez sent Massimi a most friendly reply to his letter.",
            203, 203, q(203, "he wrote to Velasquez", "reply."),
            "The source says Massimi wrote to Velasquez and received a friendly reply; the reply is attributed to Velasquez by the immediate correspondence context.",
            ["cand-2709", "cand-1564"],
        ),
        new_statement(
            "st-chp4-sec-ii-p116-ambassador-intrigue-caused-refusal", "cand-5969", "cand-1896",
            "intrigues_led_to_refusal_of_massimi",
            "Haskell attributes Philip IV's refusal to receive Massimi to intrigues by the unidentified Spanish ambassador in Rome.",
            199, 200, excerpt(segment_text, "Intrigues by the Spanish ambassador", "at court"),
            "The source expressly connects the ambassador's intrigue to Philip IV's refusal; the ambassador's identity remains unknown and the reported causal account is not independently checked.",
            ["cand-5969", "cand-1896", "cand-1564"],
        ),
        new_statement(
            "st-chp4-sec-ii-p116-donna-portrait-supplied-by-velasquez", "cand-5970", "cand-2709",
            "supplied_by",
            "Massimi acquired the portrait from Velasquez, who is identified as its supplier in this transaction.",
            197, 197, q(197, "He also acquired", "Donna Olimpia"),
            "The source says the portrait was acquired from the painter; this records the supplier role and does not infer that Velasquez created this particular portrait.",
            ["cand-5970", "cand-2709", "cand-1564", "cand-1496"],
        ),
        new_statement(
            "st-chp4-sec-ii-p116-donna-portrait-has-subject", "cand-5970", "cand-1496",
            "has_subject",
            "The acquired portrait depicts Donna Olimpia.",
            197, 197, q(197, "a portrait of", "Donna Olimpia"),
            "The source explicitly identifies Donna Olimpia as the portrait's subject.",
            ["cand-5970", "cand-1496"],
        ),
        new_statement(
            "st-chp4-sec-ii-p116-masterpieces-owned-by-massimi", "cand-11660", "cand-1564",
            "owned_by",
            "Haskell says Massimi owned approximately six masterpieces in 1653.",
            198, 198, q(198, "owned some half-dozen", "masterpieces"),
            "The source gives an approximate group count, not six individually identified works; the group is kept distinct from the unnamed makers.",
            ["cand-11660", "cand-1564"],
            qualification="Approximate count: 'some half-dozen'.",
            time="1653",
        ),
        new_statement(
            "st-chp4-sec-ii-p116-masterpieces-by-three-painters", "cand-11660", "cand-11661",
            "created_by",
            "Haskell attributes the approximately six masterpieces to three unnamed painters.",
            198, 198, q(198, "masterpieces by three", "painters"),
            "The source gives the number three but does not name these painters; do not infer that they are Claude, Poussin, and Velasquez.",
            ["cand-11660", "cand-11661"],
            qualification="Group-level authorship only; individual works and painters are not mapped.",
        ),
        new_statement(
            "st-chp4-sec-ii-p116-camillo-pamfili-claude-client", "cand-1814", "cand-0767",
            "listed_as_client_of",
            "Haskell includes Camillo Pamfili among the new names in Claude's client lists in the late 1640s.",
            193, 193, q(193, "Camillo Pamfili", "Claude’s clients."),
            "Camillo Pamfili is explicitly named in the client list; the wording does not identify a particular commission or painting.",
            ["cand-1814", "cand-0767"],
            time="late 1640s",
        ),
        new_statement(
            "st-chp4-sec-ii-p116-other-new-claude-clients", "cand-11657", "cand-0767",
            "listed_as_client_of",
            "Haskell says other unnamed new clients appeared in Claude's lists in the late 1640s.",
            193, 193, q(193, "other new ones", "Claude’s clients."),
            "The phrase defines an unnamed plural group of clients but supplies no names or membership list.",
            ["cand-11657", "cand-0767"],
            time="late 1640s",
        ),
        new_statement(
            "st-chp4-sec-ii-p116-massimi-appreciated-poussin", "cand-1564", "cand-1984",
            "appreciated_pictures_by",
            "Haskell says Massimi appreciated Poussin's pictures.",
            192, 192, q(192, "those of ", "Poussin"),
            "This separates Massimi's appreciation of Poussin from the parallel claim about Claude.",
            ["cand-1564", "cand-1984"],
        ),
        new_statement(
            "st-chp4-sec-ii-p116-innocent-x-portrait-created-by-velasquez", "cand-2715", "cand-2709",
            "created_by",
            "Haskell identifies Velasquez as the maker of the portrait of Innocent X listed in the index.",
            195, 195, excerpt(segment_text, "his principal portraits", "Innocent X"),
            "The artist is identified by the immediately preceding clause; the index entry supplies the work candidate for the portrait of Innocent X.",
            ["cand-2715", "cand-2709", "cand-1819"],
        ),
        new_statement(
            "st-chp4-sec-ii-p116-massimi-portrait-created-by-velasquez", "cand-4110", "cand-2709",
            "created_by",
            "Haskell identifies Velasquez as the maker of the portrait of Camillo Massimi (Plate 20).",
            195, 196, excerpt(segment_text, "his principal portraits", "Massimi (Plate 20)"),
            "The source connects Velasquez's principal portraits with the named sitter; the existing work candidate identifies the Massimi portrait.",
            ["cand-4110", "cand-2709", "cand-1564"],
        ),
        new_statement(
            "st-chp4-sec-ii-p116-massimi-memorial-success-evaluation", "cand-1564", None,
            "authorial_evaluation_of_success_and_perspicacity",
            "Haskell calls the work discussed next a wonderful memorial to Massimi's success and perspicacity.",
            194, 194, q(194, "There is another wonderful memorial", "these years."),
            "This is Haskell's evaluative framing of Massimi's success and perspicacity, not a separate relation claim.",
            ["cand-1564"],
        ),
    ]
    additions[-1]["qualifiers"]["relation_candidate"] = False

    candidates = [
        {
            "candidate_id": "cand-11656", "index_entry_id": "",
            "canonical_name": "Unnamed highly placed and powerful people demanding Claude's work",
            "index_page_range": "", "suggested_type": "", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Haskell identifies only an unnamed plural group as the source of demand for Claude's pictures; no people or bounded membership are supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L192",
        },
        {
            "candidate_id": "cand-11657", "index_entry_id": "",
            "canonical_name": "Other unnamed new clients in Claude's late-1640s lists",
            "index_page_range": "", "suggested_type": "", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "The source says 'other new ones' alongside Massimi and Camillo Pamfili but does not name or enumerate the clients.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L193",
        },
        {
            "candidate_id": "cand-11658", "index_entry_id": "",
            "canonical_name": "Unnamed Roman newswriters reacting to Donna Olimpia's court influence",
            "index_page_range": "", "suggested_type": "", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Haskell names an unspecified plural group of Roman newswriters; no individual writers or bounded membership are identified.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L197",
        },
        {
            "candidate_id": "cand-11659", "index_entry_id": "",
            "canonical_name": "Unnamed learned friends in Italy for whom Massimi deciphered inscriptions",
            "index_page_range": "", "suggested_type": "", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "Haskell identifies only an unnamed plural group of learned friends in Italy; no individuals or precise research affiliations are stated.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L202",
        },
        {
            "candidate_id": "cand-11660", "index_entry_id": "",
            "canonical_name": "Approximately six masterpieces owned by Camillo Massimi in 1653",
            "index_page_range": "", "suggested_type": "work", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "A source-bounded group described as 'some half-dozen masterpieces'; individual works and their present identities are not supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L198",
        },
        {
            "candidate_id": "cand-11661", "index_entry_id": "",
            "canonical_name": "Three unnamed painters of Massimi's 1653 masterpieces",
            "index_page_range": "", "suggested_type": "", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "The source supplies a group size of three but no names; do not infer Claude, Poussin, Velasquez, or any other painters as members.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L198",
        },
        {
            "candidate_id": "cand-11662", "index_entry_id": "",
            "canonical_name": "Pair of two Claude paintings named on p.116",
            "index_page_range": "", "suggested_type": "work", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "A group-level referent for Argus guarding Io (cand-0772) and A Coast View with Apollo and the Cumaean Sibyl (cand-0775), used only for Haskell's plural possible-allusion claim; not a composite work.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L193",
        },
        {
            "candidate_id": "cand-11663", "index_entry_id": "",
            "canonical_name": "Unspecified local antiquities visited by Massimi",
            "index_page_range": "", "suggested_type": "", "status": "open",
            "index_source_file": "", "sub_entry": "",
            "detail": "The source groups a Roman theatre, statue fragments, and other ruins as local antiquities visited by Massimi; object identities and a single shared type are not supplied.",
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L201",
        },
    ]

    def mention(mention_id: str, candidate_id: str, surface: str, note: str) -> dict:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"mention surface is absent or ambiguous in p.116: {surface!r}")
        return {
            "mention_id": mention_id, "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id, "surface_form": surface,
            "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
        }

    mentions = [
        mention("m-chp4-sec-ii-p116-0045", "cand-11656", "the highly placed and powerful",
                "Unspecified plural group; no individual patrons are named."),
        mention("m-chp4-sec-ii-p116-0046", "cand-11657", "other new ones",
                "Unnamed clients in Claude's late-1640s lists; membership is unknown."),
        mention("m-chp4-sec-ii-p116-0047", "cand-11658", "the Roman newswriters",
                "Unspecified plural group reacting to Donna Olimpia's influence."),
        mention("m-chp4-sec-ii-p116-0048", "cand-11659", "his learned friends in Italy",
                "Unnamed plural group for whom Massimi deciphered inscriptions."),
        mention("m-chp4-sec-ii-p116-0049", "cand-11660", "some half-dozen masterpieces",
                "Approximate group of works; no individual titles are given."),
        mention("m-chp4-sec-ii-p116-0050", "cand-11661", "three of the greatest painters",
                "The source gives a group size but does not name its members."),
        mention("m-chp4-sec-ii-p116-0051", "cand-11662",
                "pictures of Argus guarding Io and A Coast View with Apollo and the Cumaean Sibyl",
                "Group-level referent for two separately indexed paintings; not a composite work."),
        mention("m-chp4-sec-ii-p116-0052", "cand-11663",
                "the local antiquities, a Roman theatre, fragments of statues and other ruins",
                "Source-bounded mixed group of visited sites and objects; individual identities remain unresolved."),
    ]

    current_candidate_rows = list(csv.DictReader(io.StringIO(
        originals["entity-candidates.csv"].decode("utf-8"), newline=""
    )))
    current_candidate_ids = {r["candidate_id"] for r in current_candidate_rows}
    numeric_ids = [int(x[5:]) for x in current_candidate_ids if x.startswith("cand-") and x[5:].isdigit()]
    if max(numeric_ids) != 11655 or any(c["candidate_id"] in current_candidate_ids for c in candidates):
        raise SystemExit("candidate ID range changed; review before assigning p.116 IDs")
    if any(m["mention_id"] in {r["mention_id"] for r in mention_rows} for m in mentions):
        raise SystemExit("a new p.116 mention ID already exists")
    if any(r["statement_id"] in {x["statement_id"] for x in rows} for r in additions):
        raise SystemExit("a new p.116 statement ID already exists")

    all_candidate_ids = current_candidate_ids | {c["candidate_id"] for c in candidates}
    for sid, item in updates.items():
        row = existing_by_id[sid]
        for field in ("subject", "object"):
            value = item.get(field, row["subject_candidate_id"] if field == "subject" else row["object_candidate_id"])
            if value and value not in all_candidate_ids:
                raise SystemExit(f"unknown {field} candidate in update {sid}: {value}")
    for row in additions:
        if ((row["subject_candidate_id"] and row["subject_candidate_id"] not in all_candidate_ids)
                or (row["object_candidate_id"] and row["object_candidate_id"] not in all_candidate_ids)):
            raise SystemExit(f"unknown candidate endpoint in addition {row['statement_id']}")
        if norm(row["original_quote"]) not in norm(segment_text):
            raise SystemExit(f"new statement quote does not match p.116: {row['statement_id']}")
    for row in p116 + p116_notes + additions:
        for candidate_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if candidate_id not in all_candidate_ids:
                raise SystemExit(f"unknown mentioned candidate in {row['statement_id']}: {candidate_id}")

    def append_csv(data: bytes, new_rows: list[dict]) -> bytes:
        fields = next(csv.reader([data.splitlines()[0].decode("utf-8")]))
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(
            stream, fieldnames=fields, lineterminator="\n", extrasaction="raise"
        )
        writer.writerows(new_rows)
        prefix = data if data.endswith((b"\n", b"\r")) else data + b"\n"
        return prefix + stream.getvalue().encode("utf-8")

    def patch_csv_cell(data: bytes, row_id: str, column: str, old: str, new: str) -> bytes:
        raw_lines = data.splitlines(keepends=True)
        header = next(csv.reader([raw_lines[0].decode("utf-8").rstrip("\r\n")]))
        index = header.index(column)
        matches = 0
        for i in range(1, len(raw_lines)):
            raw = raw_lines[i]
            cells = next(csv.reader([raw.decode("utf-8").rstrip("\r\n")]))
            if cells[0] != row_id:
                continue
            matches += 1
            if cells[index] != old:
                raise SystemExit(f"unexpected {column} for {row_id}: {cells[index]!r}")
            token = b"," + old.encode("utf-8") + b","
            if raw.count(token) != 1:
                raise SystemExit(f"cannot safely patch {row_id} without changing CSV formatting")
            raw_lines[i] = raw.replace(token, b"," + new.encode("utf-8") + b",", 1)
        if matches != 1:
            raise SystemExit(f"expected one CSV row for {row_id}, found {matches}")
        return b"".join(raw_lines)

    by_id = {r["statement_id"]: r for r in p116}
    if len(additions) != 13 or len(candidates) != 8 or len(mentions) != 8:
        raise SystemExit("p.116 write manifest counts changed")
    new_statement_bytes = [
        (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        for row in additions
    ]
    statement_output: list[bytes] = []
    inserted = False
    after_id = "st-chp4-sec-ii-p116-velasquez-portrait-massimi"
    for raw in raw_statement_lines:
        data = raw.rstrip(b"\r\n")
        row = json.loads(data.decode("utf-8")) if data else None
        if row and row["statement_id"] in existing_by_id:
            row = existing_by_id[row["statement_id"]]
            raw = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        statement_output.append(raw)
        if row and row.get("statement_id") == after_id:
            statement_output.extend(new_statement_bytes)
            inserted = True
    if not inserted:
        raise SystemExit("could not locate the final p.116 body statement for insertion")
    statement_bytes = b"".join(statement_output)

    candidate_bytes = append_csv(originals["entity-candidates.csv"], candidates)
    mention_bytes = patch_csv_cell(
        originals["mentions.csv"], "m-chp4-sec-ii-p116-0030", "candidate_id", "cand-1498", "cand-1496"
    )
    mention_bytes = append_csv(mention_bytes, mentions)
    outputs = {
        "book-statements.jsonl": statement_bytes,
        "entity-candidates.csv": candidate_bytes,
        "mentions.csv": mention_bytes,
    }

    rc = sum(bool(r["qualifiers"]["relation_candidate"]) for r in p116 + p116_notes)
    false = len(updates) - rc
    print(f"p.116 body and linked footnotes: {len(updates)} statements; classified relation={rc}, non-relation={false}, unclassified=0")
    print(f"new statements: {len(additions)}; new relation candidates={sum(r['qualifiers']['relation_candidate'] for r in additions)}; new non-relations={sum(not r['qualifiers']['relation_candidate'] for r in additions)}")
    print(f"new candidates={len(candidates)}; new mentions={len(mentions)}")
    print("classification preview:")
    for sid in sorted(updates):
        row = existing_by_id[sid]
        item = updates[sid]
        subject = item.get("subject", row["subject_candidate_id"])
        object_ = item.get("object", row["object_candidate_id"])
        predicate = item.get("predicate", row["predicate"])
        print(f"  {sid}: relation={item['relation']} {subject} --{predicate}--> {object_}")
    print("new statement preview:")
    for row in additions:
        print(f"  {row['statement_id']}: relation={row['qualifiers']['relation_candidate']} "
              f"{row['subject_candidate_id']} --{row['predicate']}--> {row['object_candidate_id']}")
    print("new mention spans:", [(m["mention_id"], m["surface_form"], m["start_char"], m["end_char"]) for m in mentions])
    print("Donna Olimpia mention m-chp4-sec-ii-p116-0030: cand-1498 -> cand-1496")
    print("no S0 source text or S6 formal relation is modified")
    if not args.apply:
        print("dry-run only; no files written")
        return

    backups = {name: paths[name].with_name(f"{paths[name].name}.{BACKUP_SUFFIX}") for name in paths}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("recovery backup already exists; stop and inspect")
    for name, path in backups.items():
        shutil.copy2(paths[name], path)
    temp_paths = {name: paths[name].with_name(paths[name].name + ".p116-tmp") for name in paths}
    try:
        for name, data in outputs.items():
            temp_paths[name].write_bytes(data)
        for name in paths:
            os.replace(temp_paths[name], paths[name])
    except Exception:
        for name, path in paths.items():
            shutil.copy2(backups[name], path)
        for temp in temp_paths.values():
            temp.unlink(missing_ok=True)
        raise
    for name, path in paths.items():
        print(f"wrote {name}: {digest(path.read_bytes())}")
    print("recovery copies:", ", ".join(str(p.relative_to(ROOT)) for p in backups.values()))


if __name__ == "__main__":
    main()
