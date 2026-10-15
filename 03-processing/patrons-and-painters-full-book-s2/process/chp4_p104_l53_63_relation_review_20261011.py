#!/usr/bin/env python3
"""Classify and refine the p.104 S2 relation-review segment."""
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
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l53-63"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_SHA256 = "b4a5ba97f08464b967ccca06b55a628e8a56e6188fb15d92d4ded8319c50a04a"
EXPECTED_SHA256 = {
    "book-statements.jsonl": "5183dbe48e226ee9882b9febd4f7bdeb6bbdd0bce81704ca609c84c26e5d30e1",
    "entity-candidates.csv": "f1eaec7d61e6a695e4e5b94cc29b2cae16430e77a43fba0bffe80aae268fa3f5",
    "mentions.csv": "fd1be487b2214828a67ae6126df0821cfa1830791c60e7e78423cc96bf248f4b",
}
BACKUP_SUFFIX = "bak-s2-chp4-sec-ii-l53-63-relations-20261011"
NEW_IDS = ("cand-11643", "cand-11644", "cand-11645")

UNCLASSIFIED_DUAL_IDS = {
    "st-chp4-sec-ii-l53-63-barberini-high-baroque-opposed-classical",
    "st-chp4-sec-ii-l53-63-barberini-team-first-appeared-st-peters",
    "st-chp4-sec-ii-l53-63-cardinal-antonio-employed-sacchi",
    "st-chp4-sec-ii-l53-63-carlo-antonio-interested-in-poussin-bird-pictures",
    "st-chp4-sec-ii-l53-63-cassiano-admired-sacchi",
    "st-chp4-sec-ii-l53-63-cassiano-collected-duquesnoy-models",
    "st-chp4-sec-ii-l53-63-cassiano-employed-poussin-archaeology",
    "st-chp4-sec-ii-l53-63-cassiano-employed-poussin-natural-sciences",
    "st-chp4-sec-ii-l53-63-cassiano-enthusiastic-four-rivers",
    "st-chp4-sec-ii-l53-63-cassiano-interest-in-poussin-after-return",
    "st-chp4-sec-ii-l53-63-cassiano-obtained-sacchi-modello",
    "st-chp4-sec-ii-l53-63-cassiano-returned-to-rome-1626",
    "st-chp4-sec-ii-l53-63-cassiano-travel-interrupted-poussin-relationship",
    "st-chp4-sec-ii-l53-63-cassiano-urban-tomb-report",
    "st-chp4-sec-ii-l53-63-cassiano-views-bernini-changeable",
    "st-chp4-sec-ii-l53-63-duquesnoy-appealed-cassiano-taste",
    "st-chp4-sec-ii-l53-63-duquesnoy-greek-style-saying",
    "st-chp4-sec-ii-l53-63-marino-introduced-poussin-to-sacchetti",
    "st-chp4-sec-ii-l53-63-poussin-associated-with-drawing-group",
    "st-chp4-sec-ii-l53-63-poussin-classical-spirit-fragment",
    "st-chp4-sec-ii-l53-63-poussin-closest-protege",
    "st-chp4-sec-ii-l53-63-poussin-immersed-in-classical-studies",
    "st-chp4-sec-ii-l53-63-poussin-probably-met-cassiano-via-sacchetti",
    "st-chp4-sec-ii-l53-63-poussin-younger-than-cassiano",
    "st-chp4-sec-ii-l53-63-sacchi-and-poussin-kept-classical-path",
    "st-chp4-sec-ii-l53-63-susanna-judged-equal-to-ancients",
}

RELATION_NOTES = {
    "barberini-high-baroque-opposed-classical": "Haskell explicitly compares the 1630s Baroque style with the classical path; keep the comparison as authorial interpretation.",
    "barberini-team-first-appeared-st-peters": "The passage explicitly locates the unnamed team's first appearance at St Peter's; its Barberini auspices are recorded separately.",
    "cardinal-antonio-employed-sacchi": "Haskell reports employment by Cardinal Antonio; the person's identity remains unresolved in this passage.",
    "carlo-antonio-interested-in-poussin-bird-pictures": "The source says the unidentified bird paintings were of special interest to Carlo Antonio; footnote 3 does not establish that Skippon's collection paintings were by Poussin.",
    "cassiano-admired-sacchi": "Haskell's explicit characterization of Cassiano's view; it is not independent external verification.",
    "cassiano-collected-duquesnoy-models": "The source states that Cassiano collected plural wax and terracotta models by Duquesnoy; no individual model is identified.",
    "cassiano-employed-poussin-archaeology": "The source explicitly connects Cassiano's employment of Poussin with archaeological interests.",
    "cassiano-employed-poussin-natural-sciences": "The source explicitly names natural sciences as the second field; retain the source's employment language.",
    "cassiano-enthusiastic-four-rivers": "Haskell reports enthusiasm seven years after the 1647 tomb report; do not turn this relative interval into an independently verified date.",
    "cassiano-interest-in-poussin-after-return": "The source says Cassiano could begin to take a serious interest after his return; preserve this sequence and modal wording.",
    "cassiano-obtained-sacchi-modello": "The source reports Cassiano obtaining a modello for Sacchi's named altarpiece; the modello and altarpiece remain distinct works.",
    "cassiano-returned-to-rome-1626": "The return is located only as towards the end of 1626.",
    "cassiano-travel-interrupted-poussin-relationship": "The source says the relationship was interrupted, not ended, by Cassiano's travel.",
    "cassiano-urban-tomb-report": "Cassiano's reported comparison concerns the Urban VIII and Paul III tombs; preserve its quoted source attribution and do not independently rank their reputations.",
    "cassiano-views-bernini-changeable": "This is Haskell's characterization of Cassiano's views, which does not state a stable position.",
    "duquesnoy-appealed-cassiano-taste": "Haskell identifies Duquesnoy as the sculptor who particularly appealed to Cassiano's taste.",
    "duquesnoy-greek-style-saying": "The claim is attributed to Duquesnoy through Haskell; no individual Greek work is specified.",
    "marino-introduced-poussin-to-sacchetti": "Haskell says Poussin was introduced to Marcello Sacchetti by the poet Marino; the intermediary remains in the statement context.",
    "poussin-associated-with-drawing-group": "Poussin is associated with an unnamed artist collective; keep that collective separate from the corpus of drawings it produced.",
    "poussin-classical-spirit-fragment": "Haskell attributes absorption of the classical-art tradition to Poussin; the sentence continues after the plate captions and remains explicitly fragmentary.",
    "poussin-closest-protege": "This preserves Haskell's characterization of Poussin as Cassiano's closest protege, not a formally verified status.",
    "poussin-immersed-in-classical-studies": "Haskell describes Poussin's immersion in classical studies and attributes their direction to a connoisseur; retain the authorial wording.",
    "poussin-probably-met-cassiano-via-sacchetti": "Retain 'probably' and 'very soon'; no exact arrival or meeting date is supplied.",
    "poussin-younger-than-cassiano": "Preserve the approximate relative age of about six years; do not infer birth dates.",
    "sacchi-and-poussin-kept-classical-path": "This statement is narrowed to Sacchi; Poussin's parallel claim is recorded separately. 'Only' remains bounded by the unnamed Barberini team.",
    "susanna-judged-equal-to-ancients": "The comparison is reported as the judgment of unnamed contemporaries; no individual comparator work is identified.",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows, fields) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    if sha256_bytes(source_bytes) != SOURCE_SHA256:
        raise SystemExit("preflight failed: source hash changed")
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    if source_lines[52] != "[Page 104]":
        raise SystemExit("preflight failed: printed page marker changed")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if segment is None or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("preflight failed: segment manifest changed")
    body = "\n".join(source_lines[52:63])

    statements_path = TABLES / "book-statements.jsonl"
    candidates_path = TABLES / "entity-candidates.csv"
    mentions_path = TABLES / "mentions.csv"
    paths = [statements_path, candidates_path, mentions_path]
    for path in paths:
        expected = EXPECTED_SHA256[path.name]
        if sha256_bytes(path.read_bytes()) != expected:
            raise SystemExit(f"preflight failed: {path.name} hash changed")

    statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    candidates, candidate_fields = read_csv(candidates_path)
    mentions, mention_fields = read_csv(mentions_path)
    statement_by_id = {row["statement_id"]: row for row in statements}
    segment_statements = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_unclassified = {
        row["statement_id"] for row in segment_statements
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
        and "relation_candidate" not in row.get("qualifiers", {})
    }
    if actual_unclassified != UNCLASSIFIED_DUAL_IDS:
        raise SystemExit("preflight failed: the set of unclassified dual statements changed")
    if len(RELATION_NOTES) != len(UNCLASSIFIED_DUAL_IDS):
        raise SystemExit("preflight failed: decision notes do not cover all unclassified dual statements")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if any(candidate_id in candidate_by_id for candidate_id in NEW_IDS):
        raise SystemExit("preflight failed: a planned candidate ID already exists")
    if candidate_by_id["cand-5740"].get("suggested_type") != "term":
        raise SystemExit("preflight failed: artist-team candidate type changed")
    if candidate_by_id["cand-5754"].get("canonical_name") != "Modello by Andrea Sacchi for the St Romualdo altarpiece":
        raise SystemExit("preflight failed: modello candidate changed")

    def quote(text: str) -> str:
        start = body.find(text)
        if start < 0:
            raise SystemExit("preflight failed: requested evidence text is absent: " + text.encode("ascii", "backslashreplace").decode("ascii"))
        return body[start : start + len(text)]

    source_row = statement_by_id["st-chp4-sec-ii-l53-63-barberini-high-baroque-opposed-classical"]
    susanna_row = statement_by_id["st-chp4-sec-ii-l53-63-susanna-judged-equal-to-ancients"]
    models_row = statement_by_id["st-chp4-sec-ii-l53-63-duquesnoy-appealed-cassiano-taste"]
    bird_row = statement_by_id["st-chp4-sec-ii-l53-63-carlo-antonio-interested-in-poussin-bird-pictures"]
    drawing_row = statement_by_id["st-chp4-sec-ii-l53-63-poussin-associated-with-drawing-group"]
    modello_row = statement_by_id["st-chp4-sec-ii-l53-63-cassiano-obtained-sacchi-modello"]
    tomb_row = statement_by_id["st-chp4-sec-ii-l53-63-cassiano-urban-tomb-report"]

    # Classify every existing dual-endpoint claim and preserve its source scope.
    for statement_id in UNCLASSIFIED_DUAL_IDS:
        row = statement_by_id[statement_id]
        qualifier = row.setdefault("qualifiers", {})
        qualifier["relation_candidate"] = True
        note_key = statement_id.removeprefix("st-chp4-sec-ii-l53-63-")
        qualifier["relation_candidate_note"] = RELATION_NOTES[note_key]

    # Add passage-defined terms/groups and correct unsupported endpoint mappings.
    classical = {
        "candidate_id": "cand-11643", "index_entry_id": "", "canonical_name": "Classical painting as the stylistic path in Haskell's comparison",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "The classical painting path opposed to the 1630s Baroque style and followed by Sacchi and Poussin in Haskell's account; keep distinct from the broader periodizing candidate for the classical reaction in the early 1620s.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L60",
    }
    drawing_artists = {
        "candidate_id": "cand-11644", "index_entry_id": "", "canonical_name": "Unnamed artists recording ancient Rome in drawings",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Passage-defined collective associated with Poussin in the Roman remains documentation project; membership is unspecified and this group is not assumed identical to the artists who first appeared at St Peter's under Barberini auspices.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L63",
    }
    classical_art = {
        "candidate_id": "cand-11645", "index_entry_id": "", "canonical_name": "Classical art as the tradition Poussin absorbed",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell's account of the essential spirit of classical art absorbed by Poussin; keep this broader aesthetic tradition distinct from the classical painting path in the preceding comparison.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": SEGMENT_ID + "#L63",
    }
    candidates.extend([classical, drawing_artists, classical_art])
    valid_candidate_ids = {row["candidate_id"] for row in candidates}

    candidate_by_id["cand-5740"]["suggested_type"] = ""
    candidate_by_id["cand-5754"]["canonical_name"] = "Modello for Andrea Sacchi's St Romualdo altarpiece"
    candidate_by_id["cand-5754"]["detail"] = "A modello Cassiano obtained for Sacchi's named altarpiece; the passage does not explicitly identify the modello's maker, so no creator is assigned here."

    mention_by_id = {row["mention_id"]: row for row in mentions}
    wrong_guglielmo_mention = mention_by_id["m-chp4-sec-ii-l53-63-0009"]
    if wrong_guglielmo_mention["candidate_id"] != "cand-1978":
        raise SystemExit("preflight failed: Guglielmo mention mapping changed")
    wrong_guglielmo_mention["candidate_id"] = "cand-1977"
    wrong_guglielmo_mention["note"] = "The passage names Guglielmo della Porta as maker of Paul III's opposite tomb; map to the existing person candidate, not the duplicate index candidate typed as a work."
    classical_path_mention = mention_by_id["m-chp4-sec-ii-l53-63-0026"]
    if classical_path_mention["candidate_id"] != "cand-4301":
        raise SystemExit("preflight failed: classical-path mention mapping changed")
    classical_path_mention["candidate_id"] = "cand-11643"
    classical_path_mention["note"] = "Classical painting as the path in this comparison; keep separate from the early-1620s periodizing phrase cand-4301."

    def mention(mention_id: str, surface: str, candidate_id: str, note: str) -> dict[str, str]:
        start = body.find(surface)
        if start < 0 or body[start : start + len(surface)] != surface:
            raise SystemExit("preflight failed: mention surface absent")
        if mention_id in mention_by_id:
            raise SystemExit("preflight failed: planned mention ID already exists")
        return {"mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
                "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note}

    new_mentions = [
        mention("m-chp4-sec-ii-l53-63-0063", "essential spirit of classical art", "cand-11645", "The phrase refers to the broader classical-art tradition Poussin absorbed, distinct from the specific classical painting path candidate."),
        mention("m-chp4-sec-ii-l53-63-0064", "that group of artists", "cand-11644", "Anaphoric reference to the unnamed collective recording ancient Roman remains; not the earlier St Peter's team."),
    ]
    mentions.extend(new_mentions)

    # Use the bounded classical-art concept consistently in this segment.
    source_row["object_candidate_id"] = "cand-11643"
    source_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-11643" if value == "cand-4301" else value for value in source_row["qualifiers"].get("mentioned_candidate_ids", [])]
    path_row = statement_by_id["st-chp4-sec-ii-l53-63-sacchi-and-poussin-kept-classical-path"]
    path_row["subject_candidate_id"] = "cand-2318"
    path_row["object_candidate_id"] = "cand-11643"
    path_row["predicate"] = "kept_to_classical_path"
    path_row["qualifiers"]["claim"] = "Of the unnamed team, Haskell says Andrea Sacchi kept to the classical path."
    path_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-11643" if value == "cand-4301" else value for value in path_row["qualifiers"].get("mentioned_candidate_ids", [])]

    spirit_row = statement_by_id["st-chp4-sec-ii-l53-63-poussin-classical-spirit-fragment"]
    spirit_row["object_candidate_id"] = "cand-11645"
    spirit_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-11645" if value == "cand-4301" else value for value in spirit_row["qualifiers"].get("mentioned_candidate_ids", [])]

    drawing_row["object_candidate_id"] = "cand-11644"
    drawing_row["predicate"] = "associated_with_artist_group"
    drawing_row["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(drawing_row["qualifiers"].get("mentioned_candidate_ids", []) + ["cand-11644", "cand-5744"]))
    decisive_row = statement_by_id["st-chp4-sec-ii-l53-63-archaeology-more-decisive"]
    decisive_row["object_candidate_id"] = "cand-5744"
    decisive_row["qualifiers"]["relation_candidate"] = True
    decisive_row["qualifiers"]["relation_candidate_note"] = "The first experience is Poussin's participation in recording ancient Rome through the grouped drawings; Haskell compares its formative importance with the bird-painting experience."

    team_row = statement_by_id["st-chp4-sec-ii-l53-63-barberini-team-first-appeared-st-peters"]
    team_row["predicate"] = "made_first_appearance_at"
    tomb_row["subject_candidate_id"] = "cand-4512"
    tomb_row["object_candidate_id"] = "cand-4516"
    tomb_row["predicate"] = "reported_relative_reputation"
    tomb_row["qualifiers"]["claim"] = "Cassiano reported in 1647 that praise for Urban VIII's tomb had not diminished the reputation of Paul III's opposite tomb."
    tomb_row["qualifiers"]["mentioned_candidate_ids"] = ["cand-1977" if value == "cand-1978" else value for value in tomb_row["qualifiers"].get("mentioned_candidate_ids", [])]
    tomb_row["qualifiers"].pop("footnote_refs", None)  # printed note 1 follows the later Fountain of the Four Rivers clause

    def new_statement(statement_id: str, subject: str, obj: str, predicate: str, claim: str, quote_text: str,
                      line_start: int, line_end: int, mentioned: list[str], qualification: str,
                      speaker: str = "Haskell", text_layer: str = "authorial narrative",
                      relation_note: str = "The source explicitly states the scoped relationship; this remains an S2 candidate, not an externally verified S6 edge.",
                      footnote_refs=None) -> dict:
        original_quote = quote(quote_text)
        if subject not in valid_candidate_ids or obj not in valid_candidate_ids or any(x not in valid_candidate_ids for x in mentioned):
            raise SystemExit("preflight failed: new statement references an unknown candidate")
        qualifier = {
            "source_line_start": line_start, "source_line_end": line_end, "claim": claim,
            "speaker": speaker, "text_layer": text_layer, "pdf_physical_page": 11,
            "printed_page_locator": "p.104", "mentioned_candidate_ids": mentioned,
            "qualification": qualification, "relation_candidate": True,
            "relation_candidate_note": relation_note,
        }
        if footnote_refs:
            qualifier["footnote_refs"] = footnote_refs
        return {"statement_id": statement_id, "segment_id": SEGMENT_ID,
                "subject_candidate_id": subject, "object_candidate_id": obj,
                "predicate": predicate, "qualifiers": qualifier,
                "original_quote": original_quote, "origin": "book",
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md"}

    existing_ids = set(statement_by_id)
    new_statements = [
        new_statement("st-chp4-sec-ii-l53-63-mannerism-opposed-classical-path", "cand-1516", "cand-11643", "opposed_to_classical_painting",
            "Haskell compares the opposition of earlier Mannerism to classical painting with that of the 1630s Baroque style.", source_row["original_quote"], 60, 60,
            ["cand-1516", "cand-11643", "cand-4937"], "This is the explicit historical comparison in Haskell's sentence, not an independently verified periodization."),
        new_statement("st-chp4-sec-ii-l53-63-naturalism-opposed-classical-path", "cand-5739", "cand-11643", "opposed_to_classical_painting",
            "Haskell compares the opposition of earlier Naturalism to classical painting with that of the 1630s Baroque style.", source_row["original_quote"], 60, 60,
            ["cand-5739", "cand-11643", "cand-4937"], "This is the explicit historical comparison in Haskell's sentence, not an independently verified periodization."),
        new_statement("st-chp4-sec-ii-l53-63-poussin-kept-classical-path", "cand-1984", "cand-11643", "kept_to_classical_path",
            "Of the unnamed team, Haskell says Nicolas Poussin kept to the classical path.", quote("Poussin had kept to that path"), 60, 60,
            ["cand-1984", "cand-2318", "cand-5740", "cand-11643"], "'Only' limits the claim to the unnamed Barberini team; Sacchi is represented in a separate statement."),
        new_statement("st-chp4-sec-ii-l53-63-team-under-barberini-auspices", "cand-5740", "cand-0198", "under_auspices_of",
            "The unnamed artists' team made its first appearance under the auspices of the Barberini.", quote("under the auspices of the Barberini"), 60, 60,
            ["cand-5740", "cand-0198", "cand-5696"], "'Under the auspices' is retained as the source's wording and is not silently strengthened to a specific commission."),
        new_statement("st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb", "cand-1977", "cand-4516", "creator_of",
            "Haskell attributes the opposite tomb of Paul III to Guglielmo della Porta.", tomb_row["original_quote"], 54, 55,
            ["cand-1977", "cand-4515", "cand-4516", "cand-4512"], "The creator attribution appears in Haskell's bracketed identification; the printed/OCR form is retained in the source quote."),
        new_statement("st-chp4-sec-ii-l53-63-duquesnoy-created-modelli", "cand-0952", "cand-5735", "creator_of",
            "Haskell identifies François Duquesnoy as the sculptor whose collected wax and terracotta models are described.", models_row["original_quote"], 57, 58,
            ["cand-0952", "cand-5735", "cand-2036"], "The plural models remain an unidentified group; no individual model or subject is inferred."),
        new_statement("st-chp4-sec-ii-l53-63-duquesnoy-created-st-susanna", "cand-0952", "cand-5736", "creator_of",
            "Haskell identifies St Susanna as Duquesnoy's sculpture.", susanna_row["original_quote"], 58, 58,
            ["cand-0952", "cand-5736", "cand-5737"], "The work attribution is taken from Haskell's wording and has not been independently authenticated."),
        new_statement("st-chp4-sec-ii-l53-63-st-susanna-located-at-loreto", "cand-5736", "cand-5737", "located_at",
            "Haskell locates Duquesnoy's St Susanna in the church of S. Maria di Loreto.", susanna_row["original_quote"], 58, 58,
            ["cand-5736", "cand-5737", "cand-0952"], "The source gives a church location; no further site or present-location claim is made."),
        new_statement("st-chp4-sec-ii-l53-63-poussin-painted-bird-pictures", "cand-1984", "cand-5743", "creator_of",
            "Haskell attributes unidentified large bird paintings to Poussin.", bird_row["original_quote"], 63, 63,
            ["cand-1984", "cand-5743", "cand-2035"], "The paintings are unidentified; footnote 3 reports Skippon's collection note but says he did not record whether they were by Poussin.",
            footnote_refs=bird_row["qualifiers"].get("footnote_refs")),
        new_statement("st-chp4-sec-ii-l53-63-drawing-group-recorded-roman-remains", "cand-11644", "cand-5744", "recorded_ancient_roman_remains_in_drawings",
            "The unnamed artist collective recorded the vestiges of ancient Rome in approximately fifteen hundred subject-organized drawings.", drawing_row["original_quote"], 63, 63,
            ["cand-11644", "cand-5744", "cand-4490", "cand-1984"], "The number is approximate and the group, sheets, and volumes are not individually identified."),
        new_statement("st-chp4-sec-ii-l53-63-modello-for-st-romualdo", "cand-5754", "cand-5741", "model_for",
            "Cassiano obtained a modello for Sacchi's St Romualdo altarpiece of 1638.", modello_row["original_quote"], 61, 61,
            ["cand-5754", "cand-5741", "cand-2318", "cand-2036"], "The modello is distinct from the altarpiece; its maker is not explicitly stated in this passage."),
    ]
    if any(row["statement_id"] in existing_ids for row in new_statements):
        raise SystemExit("preflight failed: a planned statement ID already exists")
    statements.extend(new_statements)

    # Update explicit endpoint mentions after correcting relation subject/object roles.
    for row in segment_statements:
        qualifier = row.get("qualifiers", {})
        ids = qualifier.get("mentioned_candidate_ids", [])
        if "cand-1978" in ids and row["statement_id"] == "st-chp4-sec-ii-l53-63-cassiano-urban-tomb-report":
            qualifier["mentioned_candidate_ids"] = ["cand-1977" if value == "cand-1978" else value for value in ids]

    # Prevent silent collision and ensure all changed endpoints exist.
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("preflight failed: duplicate statement IDs")
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(candidate_ids) != len(candidates):
        raise SystemExit("preflight failed: duplicate candidate IDs")
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        if row.get("subject_candidate_id") and row["subject_candidate_id"] not in candidate_ids:
            raise SystemExit("preflight failed: unknown subject endpoint")
        if row.get("object_candidate_id") and row["object_candidate_id"] not in candidate_ids:
            raise SystemExit("preflight failed: unknown object endpoint")

    expected_counts = {"candidates": 11623, "mentions": 27562, "statements": 12967}
    actual_counts = {"candidates": len(candidates), "mentions": len(mentions), "statements": len(statements)}
    if actual_counts != expected_counts:
        raise SystemExit(f"preflight failed: unexpected totals {actual_counts}")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "source_sha256": SOURCE_SHA256,
        "segment_sha256": SEGMENT_SHA256,
        "unclassified_dual_classified_true": len(UNCLASSIFIED_DUAL_IDS),
        "new_candidates": [row["candidate_id"] for row in [classical, drawing_artists, classical_art]],
        "new_mentions": [row["mention_id"] for row in new_mentions],
        "new_statements": [row["statement_id"] for row in new_statements],
        "corrected_endpoint_roles": {
            "artist_team": "open collective; no term type",
            "Poussin_artist_group": "cand-11644, distinct from drawing corpus cand-5744",
            "classical_painting_path": "cand-11643, distinct from broader classical-art tradition cand-11645 and early-1620s reaction cand-4301",
            "Guglielmo_della_Porta": "cand-1977 person, not duplicate cand-1978 work candidate",
            "tomb_comparison": "Urban VIII tomb cand-4512 -> Paul III tomb cand-4516",
        },
        "totals_after": actual_counts,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = [path.with_name(path.name + "." + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("apply failed: a recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    try:
        write_jsonl(statements_path, statements)
        write_csv(candidates_path, candidates, candidate_fields)
        write_csv(mentions_path, mentions, mention_fields)
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("APPLY_OK")
    for path in paths:
        print("SHA256", path.name, sha256_bytes(path.read_bytes()))
    print("BACKUPS", ",".join(path.name for path in backups))


if __name__ == "__main__":
    main()
