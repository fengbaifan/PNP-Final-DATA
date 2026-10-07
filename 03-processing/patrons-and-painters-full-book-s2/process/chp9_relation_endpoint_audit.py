"""Controlled S2 endpoint and relation audit for Chapter 9; defaults to dry-run."""
from __future__ import annotations

import argparse
import copy
import csv
import difflib
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENTS_PATH = TABLES / "segments.jsonl"
SOURCE_PATHS = {
    "02-sources/02-Markdown/09_CHP-9_intro.md": ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md",
    "02-sources/02-Markdown/09_CHP-9_sec_ii.md": ROOT / "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
}
EXPECTED_MAX_CANDIDATE = 11464
NEW_CANDIDATE_START = 11465
EXPECTED_OPEN_ENDPOINT_IDS = {
    "st-chp9-p254-four-family-apotheosis-report",
    "st-chp9-p258-marco-education-travel-and-ambassadorship",
    "st-chp9-p258-marco-held-procuratore-and-doge-offices",
    "st-chp9-p259-pietro-left-picture-group-with-palace",
    "st-chp9-p263264-purchases-from-artists",
    "st-chp9-p263264-sagredo-inventory-makers",
    "st-chp9-p265-zucchi-dedication-to-sagredo",
    "st-chp9-p266-probable-artist-contacts",
    "st-chp9-p266-sagredo-heirs-sold-volumes",
    "st-chp9-p267-lorraine-claim",
    "st-chp9-p267-tentative-mantuan-origin-of-sagredo-drawings",
    "st-chp9-p268-church-and-orders-wealth",
    "st-chp9-p269-orders-churches-filled-with-art",
    "st-chp9-p270-rich-families-employed-painters",
    "st-chp9-p273-piazzetta-removed-skull-from-preliminary-version",
    "st-chp9-p273-tiepolo-proposed-two-schemes",
    "st-chp9-p274-1743-jesuit-panegyric",
    "st-chp9-p274-pieta-governors-sought-plans",
    "st-chp9-p274-sbasile-nobles-aconato-cult",
}


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def encode_csv(fields, rows):
    import io

    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def encode_jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def atomic_write(path: Path, text: str):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        f.write(text)
        temporary = Path(f.name)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes; default is dry-run")
    args = parser.parse_args()

    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    statement_path = TABLES / "book-statements.jsonl"
    paths = [candidate_path, mention_path, statement_path]

    segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS_PATH)}
    source_lines = {}
    segment_texts = {}
    for source_name, path in SOURCE_PATHS.items():
        raw = path.read_bytes()
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        source_lines[source_name] = lines
        for segment_id, meta in segments.items():
            if meta.get("source_file") != source_name or not segment_id.startswith("chp-9:"):
                continue
            text = "\n".join(lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
            if hashlib.sha256(raw).hexdigest() != meta["asset_sha256"]:
                raise SystemExit(f"source asset changed: {source_name}")
            if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
                raise SystemExit(f"source segment changed: {segment_id}")
            segment_texts[segment_id] = text

    candidate_fields, candidates = read_csv(candidate_path)
    mention_fields, mentions = read_csv(mention_path)
    statements = read_jsonl(statement_path)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions) or len(statement_by_id) != len(statements):
        raise SystemExit("duplicate table identifiers in input")

    maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
    if maximum != EXPECTED_MAX_CANDIDATE:
        raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {maximum}")

    missing = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp9-")
        and row.get("qualifiers", {}).get("relation_candidate")
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if missing != EXPECTED_OPEN_ENDPOINT_IDS:
        raise SystemExit(f"Chapter 9 open endpoint set changed: {sorted(missing)}")

    for cid, expected in {
        "cand-2468": ("Smith, Joseph", "event"),
        "cand-8639": ("Print 428 in volume 3 of Raccolta Gherro (Biblioteca Correr)", "archive"),
    }.items():
        row = candidate_by_id.get(cid)
        if not row or (row["canonical_name"], row["suggested_type"]) != expected:
            raise SystemExit(f"candidate precondition changed: {cid}")
    for sid, expected in {
        "st-chp9-p273-piazzetta-removed-skull-from-preliminary-version": ("cand-1922", None),
        "st-chp9-p265-zucchi-dedication-to-sagredo": (None, "cand-2339"),
    }.items():
        row = statement_by_id[sid]
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != expected:
            raise SystemExit(f"statement precondition changed: {sid}")

    new_candidates = []
    new_mentions = []
    new_statements = []

    candidate_specs = [
        (11465, "Unidentified 1762 inventory of Pietro Longhi for the Sagredo collection", "archive",
         "Haskell says Longhi drew up an inventory in 1762 and later corrects Brunetti: the inventory survives among the Sagredo papers at Biblioteca Correr, MSS. P.D. C2193/I. Keep distinct from the 1762 Udney picture list and the unidentified 1743 inventory.",
         "chp-9:09_CHP-9_intro:l240-249", 243),
        (11466, "Unnamed heirs of Zaccaria Sagredo", "",
         "Haskell refers collectively to Zaccaria Sagredo's unnamed heirs as the later sellers of pictures and drawing volumes. Do not equate this group with the whole Sagredo family or assign identities here.",
         "chp-9:09_CHP-9_intro:l240-249", 241),
        (11467, "Unidentified Gonzaga effects (property or estate)", "",
         "The phrase 'Gonzaga effects' denotes property or an estate to which the Duke of Lorraine claimed heirship, not the Gonzaga family.",
         "chp-9:09_CHP-9_intro:l313-321", 319),
        (11468, "Unidentified member of Ferdinando Carlo's immediate entourage", "person",
         "Haskell offers an unnamed member of the Duke's immediate entourage as an alternative possible owner of drawings later assembled by Sagredo. The individual is not identified.",
         "chp-9:09_CHP-9_intro:l313-321", 321),
        (11469, "Unidentified Castiglione pictures painted at Mantua", "work",
         "Unidentified pictures by Castiglione at Mantua to which Haskell says some of the Sagredo drawings relate; do not conflate these paintings with the more than 900 ducal pictures sent to Ferdinando Carlo.",
         "chp-9:09_CHP-9_intro:l313-321", 321),
        (11470, "Unnamed Jesuit preacher of the 1743 panegyric to the Blessed Virgin", "person",
         "An unnamed Jesuit whom Haskell reports preached the 1743 panegyric comparing the Blessed Virgin to Esther.",
         "chp-9:09_CHP-9_sec_ii:l70-78", 72),
        (11471, "Pietà governors' plan-selection procedure", "procedure",
         "Procedure described as seeking plans from highly regarded painters with suitable ideas and choosing the best. Haskell says a similar practice 'seems' to have been followed at the Pietà.",
         "chp-9:09_CHP-9_sec_ii:l70-78", 72),
        (11472, "Unnamed group of nobles associated with S. Basilio", "",
         "Source-defined group of nobles associated with S. Basilio and devoted to propagating a cult. The pronoun referring to an individual member is ambiguous; no membership is assigned to Corner or Angeli.",
         "chp-9:09_CHP-9_sec_ii:l70-78", 76),
        (11473, "Cult of Beato Pietro Aconato at S. Basilio", "term",
         "The cult of Beato Pietro Aconato named as the object of propagation by an unnamed group of nobles associated with S. Basilio; keep distinct from Beato Pietro Aconato as a person.",
         "chp-9:09_CHP-9_sec_ii:l70-78", 76),
    ]
    for number, name, kind, detail, segment_id, line_no in candidate_specs:
        cid = f"cand-{number:04d}"
        if cid in candidate_by_id or any(c["canonical_name"] == name and c["suggested_type"] == kind for c in candidates):
            raise SystemExit(f"candidate ID or natural key already exists: {cid}")
        new_candidates.append({
            "candidate_id": cid,
            "index_entry_id": "",
            "canonical_name": name,
            "index_page_range": "",
            "suggested_type": kind,
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": detail,
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{segment_id}#L{line_no}",
        })
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    def add_mention(mid, segment_id, line_no, cid, surface, note, occurrence=0):
        if mid in mention_by_id or any(row["mention_id"] == mid for row in new_mentions):
            raise SystemExit(f"mention ID already exists: {mid}")
        meta = segments[segment_id]
        source_name = meta["source_file"]
        line = source_lines[source_name][line_no - 1]
        starts, pos = [], 0
        while True:
            at = line.find(surface, pos)
            if at < 0:
                break
            starts.append(at)
            pos = at + 1
        if occurrence >= len(starts):
            raise SystemExit(f"source surface absent on L{line_no}: {surface!r}")
        offset = sum(len(source_lines[source_name][n - 1]) + 1 for n in range(int(meta["line_start"]), line_no))
        start = offset + starts[occurrence]
        end = start + len(surface)
        if segment_texts[segment_id][start:end] != surface:
            raise SystemExit(f"mention span failed source check: {mid}")
        new_mentions.append({
            "mention_id": mid,
            "segment_id": segment_id,
            "candidate_id": cid,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    # Correct a family-to-heirs overreach and add the heirs' second occurrence.
    if mention_by_id["m-chp9-p263264-sagredo-heirs"]["candidate_id"] != "cand-8571":
        raise SystemExit("heirs mention precondition changed")
    mention_by_id["m-chp9-p263264-sagredo-heirs"]["candidate_id"] = "cand-11466"
    mention_by_id["m-chp9-p263264-sagredo-heirs"]["note"] = "Unnamed heirs are a distinct legal successor group, not the entire Sagredo family."
    add_mention(
        "m-chp9-p266-sagredo-heirs-group", "chp-9:09_CHP-9_intro:l303-311", 307, "cand-11466",
        "Zaccaria’s heirs", "Unnamed heirs of Zaccaria Sagredo, distinct from the Sagredo family and from Zaccaria himself."
    )
    # Map the footnote's archival object rather than its maker.
    if mention_by_id["m-chp9-p263264-longhi-inventory-source"]["candidate_id"] != "cand-1429":
        raise SystemExit("Longhi inventory mention precondition changed")
    mention_by_id["m-chp9-p263264-longhi-inventory-source"]["candidate_id"] = "cand-11465"
    mention_by_id["m-chp9-p263264-longhi-inventory-source"]["note"] = "The note's phrase names the archive record; Pietro Longhi as maker is separately mentioned in the body."
    # Property, not family, is the referent of 'Gonzaga effects'.
    if mention_by_id["m-chp9-p267-gonzaga"]["candidate_id"] != "cand-6669":
        raise SystemExit("Gonzaga-effects mention precondition changed")
    mention_by_id["m-chp9-p267-gonzaga"]["candidate_id"] = "cand-11467"
    mention_by_id["m-chp9-p267-gonzaga"]["note"] = "Here 'Gonzaga effects' means property or an estate, not the Gonzaga family."

    add_mention(
        "m-chp9-p263264-inventory-1743", "chp-9:09_CHP-9_intro:l240-249", 243, "cand-8618",
        "draw up inventories", "The inventory record set dated 1743; keep distinct from the 1738 inventory and the 1762 Udney picture list."
    )
    add_mention(
        "m-chp9-p265-dedication-print-reference", "chp-9:09_CHP-9_intro:l291-301", 294, "cand-8639",
        "this was dedicated", "Anaphoric dedication reference resolved by note 3 to print 428 in Raccolta Gherro, vol. 3."
    )
    add_mention(
        "m-chp9-p267-entourage-member", "chp-9:09_CHP-9_intro:l313-321", 321, "cand-11468",
        "someone in his immediate entourage", "One unnamed alternative possible owner in Haskell's tentative provenance hypothesis."
    )
    add_mention(
        "m-chp9-p267-castiglione-pictures", "chp-9:09_CHP-9_intro:l313-321", 321, "cand-11469",
        "pictures that Castiglione painted at Mantua", "Unidentified paintings to which only some of the Sagredo drawings are said to relate."
    )
    if mention_by_id["m-chp9-p274-jesuit"]["candidate_id"] != "cand-3403":
        raise SystemExit("anonymous Jesuit mention precondition changed")
    mention_by_id["m-chp9-p274-jesuit"]["candidate_id"] = "cand-11470"
    mention_by_id["m-chp9-p274-jesuit"]["note"] = "Unnamed individual preacher, identified by membership in the Jesuit order; do not map this person to the order itself."
    add_mention(
        "m-chp9-p274-plan-selection-procedure", "chp-9:09_CHP-9_sec_ii:l70-78", 72, "cand-11471",
        "plans from the most highly thought of painters with suitable ideas and choose the best",
        "Source wording for the Pietà plan-selection procedure; retain Haskell's 'seems' qualification."
    )
    add_mention(
        "m-chp9-p274-sbasile-noble-group", "chp-9:09_CHP-9_sec_ii:l70-78", 76, "cand-11472",
        "a group of nobles", "Source-defined unnamed collective; the individual's pronoun antecedent remains ambiguous."
    )
    add_mention(
        "m-chp9-p274-aconato-cult", "chp-9:09_CHP-9_sec_ii:l70-78", 76, "cand-11473",
        "the cult of Beato Pietro Aconato", "Cult as a concept, distinct from Beato Pietro Aconato as a person."
    )

    def set_statement(row, subject, obj, predicate, claim, qualification, mentioned, relation=True):
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = obj
        row["predicate"] = predicate
        q = row.setdefault("qualifiers", {})
        q["claim"] = claim
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = list(dict.fromkeys(mentioned))
        q["relation_candidate"] = relation
        return row

    def clone_statement(parent_id, new_id, **kwargs):
        if new_id in statement_by_id or any(row["statement_id"] == new_id for row in new_statements):
            raise SystemExit(f"statement ID already exists: {new_id}")
        row = copy.deepcopy(statement_by_id[parent_id])
        row["statement_id"] = new_id
        set_statement(row, **kwargs)
        new_statements.append(row)
        return row

    def clear_note_link(row):
        q = row["qualifiers"]
        for key in ("footnote_marker", "footnote_refs", "footnote_statement_ids", "footnote_body_link_status", "footnote_segment"):
            q.pop(key, None)

    def link_body_to_note(row, marker, note_id, note_segment, note_line):
        q = row["qualifiers"]
        q["footnote_marker"] = marker
        q["footnote_text_pending"] = False
        q["footnote_segment"] = note_segment
        q["footnote_refs"] = [{"marker": marker, "segment_id": note_segment, "source_line": note_line}]
        q["footnote_statement_ids"] = [note_id]
        q["footnote_body_link_status"] = "linked"

    def link_note_to_body(note_id, body_id):
        q = statement_by_id[note_id]["qualifiers"]
        linked = q.setdefault("linked_body_statement_ids", [])
        if body_id not in linked:
            linked.append(body_id)
        q["footnote_body_link_status"] = "linked"

    # p.254: preserve the four-family overview as context and add four family-specific edges.
    sid = "st-chp9-p254-four-family-apotheosis-report"
    parent = statement_by_id[sid]
    parent["qualifiers"]["relation_candidate"] = False
    family_specs = [
        ("grassi", "cand-1228", "cand-8311", "family_apotheosis_fresco_painted_in_palace_or_country_house", "st-chp9-p254-grassi-apotheosis", 2,
         "Haskell reports that the Grassi family had an apotheosis of the family painted in its palace or country house.",
         "The body supplies no named location or painter. Note 2 reports Molmenti's separate Fabio Canal attribution; it is not independently verified."),
        ("widmann", "cand-2812", "cand-8310", "family_apotheosis_reported_within_aggregate_work_group", "st-chp9-p254-widmann-apotheosis", None,
         "Haskell names the Widmann among the families whose apotheoses were painted in their palaces or country houses.",
         "The source gives only the aggregate group mention; no individual work, title, location, or painter can be separated for this family. Do not attribute it to Tiepolo."),
        ("giustiniani", "cand-1197", "cand-8310", "family_apotheosis_reported_within_aggregate_work_group", "st-chp9-p254-giustiniani-apotheosis", 3,
         "Haskell names the Giustiniani among the families whose apotheoses were painted in their palaces or country houses.",
         "The source gives only the aggregate group mention; note 3 is a citation locator, not an attribution, and no individual work or painter can be separated."),
        ("soderini", "cand-2478", "cand-8310", "family_apotheosis_reported_within_aggregate_work_group", "st-chp9-p254-soderini-apotheosis", None,
         "Haskell names the Soderini among the families whose apotheoses were painted in their palaces or country houses.",
         "The source gives only the aggregate group mention; no individual work, title, location, or painter can be separated for this family. Do not attribute it to Tiepolo."),
    ]
    for key, family, work, predicate, new_id, marker, claim, qualification in family_specs:
        row = clone_statement(
            sid, new_id,
            subject=family, obj=work,
            predicate=predicate,
            claim=claim, qualification=qualification,
            mentioned=[family, work, "cand-8310"],
        )
        clear_note_link(row)
        row["qualifiers"].pop("cross_reference_segments", None)
        if marker == 2:
            link_body_to_note(row, 2, "st-chp9-p254-note2-molmenti-fabio-canal-attribution",
                              "chp-9:09_CHP-9_intro:l134-146", 146)
            link_note_to_body("st-chp9-p254-note2-molmenti-fabio-canal-attribution", new_id)
        elif marker == 3:
            link_body_to_note(row, 3, "st-chp9-p254-note3-brunelli-callegari-reference",
                              "chp-9:09_CHP-9_intro:l323-445", 365)
            link_note_to_body("st-chp9-p254-note3-brunelli-callegari-reference", new_id)

    # p.258: separate education, travel destinations, and diplomatic service.
    sid = "st-chp9-p258-marco-education-travel-and-ambassadorship"
    parent = statement_by_id[sid]
    set_statement(parent, "cand-1053", "cand-3398", "marco_foscarini_educated_in_bologna",
                  "Haskell says Marco Foscarini was educated in Bologna.",
                  "This is the source's biographical account; no date or educational institution is supplied.",
                  ["cand-1053", "cand-3398"])
    travel = [
        ("paris", "cand-4653", "Paris"),
        ("vienna", "cand-2772", "Vienna"),
        ("rome", "cand-4490", "Rome"),
    ]
    for place_key, place_id, place_name in travel:
        clone_statement(
            sid, f"st-chp9-p258-marco-travelled-to-{place_key}",
            subject="cand-1053", obj=place_id, predicate=f"marco_foscarini_travelled_to_{place_key}",
            claim=f"Haskell says Marco Foscarini travelled to {place_name} in his younger days.",
            qualification="The source gives no date or itinerary details.",
            mentioned=["cand-1053", place_id],
        )
    for place_key, place_id, place_name in [("vienna", "cand-2772", "Vienna"), ("rome", "cand-4490", "Rome")]:
        clone_statement(
            sid, f"st-chp9-p258-marco-ambassador-in-{place_key}",
            subject="cand-1053", obj=place_id, predicate=f"marco_foscarini_served_as_ambassador_in_{place_key}",
            claim=f"Haskell says Foscarini served as ambassador in {place_name}.",
            qualification="The phrase 'the two latter cities' refers to Vienna and Rome; dates and missions are not supplied.",
            mentioned=["cand-1053", place_id],
        )

    sid = "st-chp9-p258-marco-held-procuratore-and-doge-offices"
    parent = statement_by_id[sid]
    set_statement(parent, "cand-1053", "cand-8449", "marco_foscarini_held_procuratore_di_san_marco_from_1741",
                  "Haskell says Marco Foscarini served as Procuratore di San Marco from 1741.",
                  "Preserve the source's office title and start date.",
                  ["cand-1053", "cand-8449"])
    clone_statement(
        sid, "st-chp9-p258-marco-held-doge-office",
        subject="cand-1053", obj="cand-8450", predicate="marco_foscarini_later_held_doge_office_for_few_months",
        claim="Haskell says Foscarini later served as Doge for a few months before his death in 1763.",
        qualification="Preserve the source's relative chronology and short tenure; no exact Doge dates are supplied.",
        mentioned=["cand-1053", "cand-8450"],
    )

    # p.259: Pietro Foscarini is the previous owner; the palace is contextual, not the work endpoint.
    sid = "st-chp9-p259-pietro-left-picture-group-with-palace"
    parent = statement_by_id[sid]
    set_statement(parent, "cand-1056", "cand-8461", "pietro_foscarini_left_seven_tintoretto_pictures_with_palace",
                  "Haskell says seven Tintoretto pictures had been left with the Foscarini palace by its former owner Pietro Foscarini.",
                  "The source reports this transfer without specifying how or when it occurred; note 4 locates Pietro's will and picture inventory but was not independently checked.",
                  ["cand-1056", "cand-8461", "cand-1059", "cand-1057"])
    link_body_to_note(parent, 4, "st-chp9-p259-note4-pietro-picture-inventory-location",
                      "chp-9:09_CHP-9_intro:l323-445", 392)
    link_note_to_body("st-chp9-p259-note4-pietro-picture-inventory-location", sid)
    clone_statement(
        sid, "st-chp9-p259-pietro-left-other-venetian-classics",
        subject="cand-1056", obj="cand-8490", predicate="pietro_foscarini_left_other_venetian_classics_with_palace",
        claim="Haskell says other Venetian classics had been left with the Foscarini palace by its former owner Pietro Foscarini.",
        qualification="The works are not individually identified; note 4 locates Pietro's will and picture inventory but does not independently establish the transfer.",
        mentioned=["cand-1056", "cand-8490", "cand-1059", "cand-1057"],
    )
    link_body_to_note(new_statements[-1], 4, "st-chp9-p259-note4-pietro-picture-inventory-location",
                      "chp-9:09_CHP-9_intro:l323-445", 392)
    link_note_to_body("st-chp9-p259-note4-pietro-picture-inventory-location", new_statements[-1]["statement_id"])

    # p.263 note 5: one transaction per work group.
    sid = "st-chp9-p263264-purchases-from-artists"
    parent = statement_by_id[sid]
    parent["qualifiers"]["relation_candidate"] = False
    purchase_specs = [
        ("st-chp9-p263264-sagredo-bought-carracci-drawings", "cand-2329", "cand-8590",
         "sagredo_bought_carracci_drawings_from_bonfiglioli_family",
         "Haskell's note says Zaccaria Sagredo bought unidentified Carracci drawings from the Bonfiglioli family in Bologna.",
         "Bottari II, p.186 is cited but was not independently consulted; individual drawings are not identified.",
         ["cand-2329", "cand-0576", "cand-8589", "cand-8590", "cand-8584"]),
        ("st-chp9-p263264-sagredo-commissioned-crespi-pictures", "cand-2329", "cand-8591",
         "sagredo_commissioned_unidentified_pictures_from_crespi",
         "Haskell's note says Zaccaria Sagredo commissioned unidentified pictures from Giuseppe Maria Crespi.",
         "Zanotti II, p.62 is cited but was not independently consulted; the pictures are not individually titled.",
         ["cand-2329", "cand-0871", "cand-8591", "cand-8585"]),
        ("st-chp9-p263264-sagredo-bought-angelo-custode", "cand-2329", "cand-8569",
         "sagredo_bought_piazzetta_angelo_custode_at_s_rocco_exhibition",
         "Haskell's note says Zaccaria Sagredo bought Piazzetta's Angelo Custode at the S. Rocco exhibition.",
         "d'Argenville I, p.319 is cited but was not independently consulted; reuse the existing Angelo Custode work candidate.",
         ["cand-2329", "cand-1901", "cand-8569", "cand-8587", "cand-8588", "cand-8586"]),
    ]
    for new_id, subject, obj, predicate, claim, qualification, mentioned in purchase_specs:
        row = clone_statement(
            sid, new_id, subject=subject, obj=obj, predicate=predicate, claim=claim,
            qualification=qualification, mentioned=mentioned,
        )
        row["qualifiers"]["footnote_marker"] = 5

    # p.264 inventory makers: distinguish the 1743 record set, Longhi's 1762 record, and the Udney list.
    sid = "st-chp9-p263264-sagredo-inventory-makers"
    parent = statement_by_id[sid]
    parent["qualifiers"]["relation_candidate"] = False
    parent["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-2329", "cand-2569", "cand-1901", "cand-1429", "cand-8618", "cand-11465"
    ]
    clear_note_link(parent)
    parent["qualifiers"].pop("cross_reference_segments", None)
    inventory_specs = [
        ("st-chp9-p263264-tiepolo-drew-1743-inventory", "cand-2569", "cand-8618",
         "tiepolo_required_to_draw_up_sagredo_inventory_in_1743",
         "Haskell says Tiepolo was required to draw up an inventory of the Sagredo collection in 1743.",
         "The exact archival record is unidentified; do not conflate it with the separate 1738 inventory.",
         ["cand-2569", "cand-8618", "cand-2329"]),
        ("st-chp9-p263264-piazzetta-drew-1743-inventory", "cand-1901", "cand-8618",
         "piazzetta_required_to_draw_up_sagredo_inventory_in_1743",
         "Haskell says Piazzetta was required to draw up an inventory of the Sagredo collection in 1743.",
         "The source scan corrects S0's 'Tiazzetta' to Piazzetta; the exact archival record is unidentified.",
         ["cand-1901", "cand-8618", "cand-2329"]),
        ("st-chp9-p263264-longhi-drew-1762-inventory", "cand-1429", "cand-11465",
         "pietro_longhi_drew_up_sagredo_inventory_in_1762",
         "Haskell says Pietro Longhi drew up a Sagredo inventory in 1762.",
         "Keep this record distinct from the 1762 Udney picture list; note 6 says the Longhi inventory survives at Biblioteca Correr.",
         ["cand-1429", "cand-11465", "cand-2329"]),
    ]
    for new_id, subject, obj, predicate, claim, qualification, mentioned in inventory_specs:
        row = clone_statement(
            sid, new_id, subject=subject, obj=obj, predicate=predicate, claim=claim,
            qualification=qualification, mentioned=mentioned,
        )
        clear_note_link(row)
        row["qualifiers"].pop("cross_reference_segments", None)
        if "longhi" in new_id:
            link_body_to_note(row, 6, "st-chp9-p263264-longhi-inventory-survival",
                              "chp-9:09_CHP-9_intro:l323-445", 425)
            row["qualifiers"]["cross_reference_segments"] = [
                {"segment_id": "chp-9:09_CHP-9_intro:l323-445", "source_line_start": 425, "source_line_end": 425}
            ]
            link_note_to_body("st-chp9-p263264-longhi-inventory-survival", new_id)

    # Correct the note-level relation: the inventory survives at Correr; Brunetti is only the cited author.
    longhi_note = statement_by_id["st-chp9-p263264-longhi-inventory-survival"]
    set_statement(
        longhi_note, "cand-11465", "cand-8262", "longhi_inventory_survives_among_sagredo_papers_at_biblioteca_correr",
        "Haskell corrects Brunetti: the 1762 Longhi inventory survives among the Sagredo papers at Biblioteca Correr, MSS. P.D. C2193/I.",
        "Haskell's correction and the shelfmark are reported through the note; neither the inventory nor Brunetti's publication was independently examined.",
        ["cand-11465", "cand-1429", "cand-8600", "cand-8262", "cand-2329"],
    )

    # p.264 disposal: preserve the broad account as context; split the two named buyers.
    sid = "st-chp9-p263264-sale-heirs-and-consuls"
    parent = statement_by_id[sid]
    parent["qualifiers"]["relation_candidate"] = False
    parent["subject_candidate_id"] = None
    parent["object_candidate_id"] = None
    parent["predicate"] = "sagredo_collection_dispersed_piecemeal_and_heirs_contacted_foreign_buyers"
    parent["qualifiers"]["claim"] = "Haskell says the collection was broken up piecemeal over time and that Zaccaria Sagredo's heirs contacted interested foreign buyers."
    parent["qualifiers"]["qualification"] = "This is a broad contextual summary; the source names Joseph Smith and John Udney separately as buyers, with distinct note evidence."
    parent["qualifiers"]["mentioned_candidate_ids"] = [
        "cand-11466", "cand-2468", "cand-2668", "cand-8598", "cand-8599"
    ]
    smith_id = "st-chp9-p263264-heirs-sold-pictures-to-smith"
    smith = clone_statement(
        sid, smith_id, subject="cand-11466", obj="cand-2468",
        predicate="sagredo_heirs_sold_pictures_and_drawings_to_joseph_smith",
        claim="Haskell reports that the unnamed heirs of Zaccaria Sagredo sold pictures and drawings to Joseph Smith in 1751–52.",
        qualification="The body places Smith among buyers; note 4 cites a published archival document showing the purchases. The document itself was not independently consulted.",
        mentioned=["cand-11466", "cand-2468", "cand-8598"],
    )
    link_body_to_note(smith, 4, "st-chp9-p263264-smith-purchases-document",
                      "chp-9:09_CHP-9_intro:l323-445", 423)
    link_note_to_body("st-chp9-p263264-smith-purchases-document", smith_id)
    udney_id = "st-chp9-p263264-heirs-sold-to-udney-report"
    udney = clone_statement(
        sid, udney_id, subject="cand-11466", obj="cand-2668",
        predicate="sagredo_heirs_reportedly_sold_collection_items_to_john_udney",
        claim="Haskell includes John Udney among the buyers who came to the Sagredo heirs.",
        qualification="Note 5 identifies a 1762 list of pictures sought by Udney; that list alone does not establish a completed purchase.",
        mentioned=["cand-11466", "cand-2668", "cand-8599"],
    )
    link_body_to_note(udney, 5, "st-chp9-p263264-udney-1762-list",
                      "chp-9:09_CHP-9_intro:l323-445", 424)
    link_note_to_body("st-chp9-p263264-udney-1762-list", udney_id)

    # p.265: the note resolves the body's anaphoric dedication reference to print 428.
    sid = "st-chp9-p265-zucchi-dedication-to-sagredo"
    dedication = statement_by_id[sid]
    set_statement(
        dedication, "cand-8639", "cand-2339", "print_428_dedicated_to_zaccaria_sagredo",
        "Haskell says the image dedicated to Zaccaria Sagredo is print 428 in volume 3 of Raccolta Gherro.",
        "The body's 'this' is resolved by note 3 to the print; do not attach the dedication to Corradini's sculpture or Tiepolo's preparatory drawing. The print was not independently examined.",
        ["cand-8639", "cand-2339", "cand-2569", "cand-2886", "cand-8608", "cand-8609"],
    )
    link_body_to_note(dedication, 3, "st-chp9-p265-note3-correr-print-dedication",
                      "chp-9:09_CHP-9_intro:l323-445", 430)
    link_note_to_body("st-chp9-p265-note3-correr-print-dedication", sid)

    # p.266: keep the four contacts probable and endpoint-specific; map the unnamed heirs separately.
    sid = "st-chp9-p266-probable-artist-contacts"
    parent = statement_by_id[sid]
    set_statement(parent, "cand-2329", "cand-2569", "zaccaria_sagredo_probably_had_contact_with_tiepolo",
                  "Haskell says Zaccaria Sagredo probably had contact with Tiepolo early in the artist's career and late in Sagredo's life.",
                  "Preserve 'probable' and the relative chronology; no meeting, correspondence, or date is named.",
                  ["cand-2329", "cand-2569"])
    for artist, artist_id, label in [("piazzetta", "cand-1901", "Piazzetta"), ("canaletto", "cand-0522", "Canaletto"), ("longhi", "cand-1429", "Longhi")]:
        clone_statement(
            sid, f"st-chp9-p266-sagredo-probable-contact-{artist}",
            subject="cand-2329", obj=artist_id, predicate=f"zaccaria_sagredo_probably_had_contact_with_{artist}",
            claim=f"Haskell says Zaccaria Sagredo probably had contact with {label} early in the artist's career and late in Sagredo's life.",
            qualification="Preserve 'probable' and the relative chronology; no meeting, correspondence, or date is named.",
            mentioned=["cand-2329", artist_id],
        )

    sid = "st-chp9-p266-sagredo-heirs-sold-volumes"
    set_statement(
        statement_by_id[sid], "cand-11466", "cand-8635", "unnamed_sagredo_heirs_later_sold_drawing_volumes",
        "Haskell says the unnamed heirs of Zaccaria Sagredo sold the drawing volumes in later years.",
        "The heirs, sale date, terms, and individual volumes are not identified.",
        ["cand-11466", "cand-2329", "cand-8635"],
    )

    # p.267: correct the property referent and separate alternatives from the 'some drawings' qualification.
    sid = "st-chp9-p267-lorraine-claim"
    set_statement(
        statement_by_id[sid], "cand-1441", "cand-11467", "duke_of_lorraine_claimed_heirship_to_gonzaga_effects",
        "Haskell says the unnamed Duke of Lorraine successfully established a claim to be heir to the Gonzaga effects.",
        "'Gonzaga effects' means property or an estate, not a family relationship; the Duke is not named.",
        ["cand-1441", "cand-11467"],
    )

    sid = "st-chp9-p267-tentative-mantuan-origin-of-sagredo-drawings"
    parent = statement_by_id[sid]
    set_statement(
        parent, "cand-1524", "cand-8636", "ferdinando_carlo_may_have_owned_drawings_later_assembled_by_sagredo",
        "Haskell says Ferdinando Carlo may well have owned the large quantity of drawings from which Sagredo assembled his volumes.",
        "This is one explicitly tentative alternative. Haskell says there is no specific reference to drawings among the works sent to the Duke; it does not establish a sale or prove all volumes came from the ducal collections.",
        ["cand-1524", "cand-8636", "cand-8631", "cand-6672"],
    )
    parent["qualifiers"].pop("footnote_marker", None)
    parent["qualifiers"].pop("cross_reference_segments", None)
    clone_statement(
        sid, "st-chp9-p267-entourage-member-may-have-owned-sagredo-drawings",
        subject="cand-11468", obj="cand-8636",
        predicate="unnamed_entourage_member_may_have_owned_drawings_later_assembled_by_sagredo",
        claim="Haskell says an unnamed member of Ferdinando Carlo's immediate entourage may well have owned the drawings from which Sagredo assembled his volumes.",
        qualification="This is the second explicitly tentative alternative; the person is unnamed and no direct reference to drawings among the works sent to the Duke is supplied.",
        mentioned=["cand-11468", "cand-1524", "cand-8636", "cand-8631", "cand-6672"],
    )
    castiglione_id = "st-chp9-p267-sagredo-drawings-relate-to-mantuan-pictures"
    castiglione_row = clone_statement(
        sid, castiglione_id,
        subject="cand-8636", obj="cand-11469",
        predicate="some_sagredo_drawings_relate_to_castiglione_pictures_painted_at_mantua",
        claim="Haskell says some of the drawings in Sagredo's volumes relate to pictures Castiglione painted at Mantua.",
        qualification="The quantifier is 'some'; no individual drawing or painting is identified. This relation does not prove the drawings' provenance.",
        mentioned=["cand-8636", "cand-11469", "cand-0602", "cand-6672"],
    )
    link_body_to_note(castiglione_row, 5, "st-chp9-p267-note5-blunt-citation",
                      "chp-9:09_CHP-9_intro:l323-445", 445)
    link_note_to_body("st-chp9-p267-note5-blunt-citation", castiglione_id)

    # p.268–270: broad contextual assertions do not identify relation endpoints.
    for sid in [
        "st-chp9-p268-church-and-orders-wealth",
        "st-chp9-p269-orders-churches-filled-with-art",
        "st-chp9-p270-rich-families-employed-painters",
    ]:
        statement_by_id[sid]["qualifiers"]["relation_candidate"] = False

    # p.273: repair painter-to-work direction; note 3 identifies only the modello's location.
    sid = "st-chp9-p273-piazzetta-removed-skull-from-preliminary-version"
    skull = statement_by_id[sid]
    set_statement(
        skull, "cand-1901", "cand-1922", "piazzetta_removed_skull_from_preliminary_version_of_st_philip_neri_and_virgin",
        "Haskell says Piazzetta removed a skull he had included in a preliminary version of St Philip Neri and the Virgin.",
        "Note 3 locates a modello at the Pennsylvania Museum; do not identify that model with the full-size painting or infer any broader object identity.",
        ["cand-1901", "cand-1922", "cand-8813", "cand-8814", "cand-8738"],
    )

    sid = "st-chp9-p273-tiepolo-proposed-two-schemes"
    first_scheme = statement_by_id[sid]
    set_statement(
        first_scheme, "cand-2575", "cand-8741", "tiepolo_proposed_first_scuola_del_carmine_ceiling_scheme",
        "Haskell says Tiepolo proposed a first ceiling scheme with the shared central scene and eight surrounding canvases illustrating the confraternity's privileges and doctrinal points.",
        "The first scheme is a proposal; the text does not explicitly say it was rejected. The central scene is shared with the second scheme.",
        ["cand-2575", "cand-8740", "cand-8741", "cand-8743", "cand-8744", "cand-8745", "cand-8746", "cand-8747"],
    )
    # Extend the source excerpt to the full two-scheme passage for both extracted claims.
    p273_line = source_lines["02-sources/02-Markdown/09_CHP-9_sec_ii.md"][66]
    first_scheme["original_quote"] = p273_line
    clone_statement(
        sid, "st-chp9-p273-tiepolo-proposed-second-scuola-scheme",
        subject="cand-2575", obj="cand-8742", predicate="tiepolo_proposed_second_scuola_del_carmine_ceiling_scheme",
        claim="Haskell says Tiepolo proposed a second ceiling scheme with surrounding canvases depicting virtues; this second plan was chosen and carried out with a few modifications.",
        qualification="The central scene was shared with the first alternative; preserve the reported chosen and modified status.",
        mentioned=["cand-2575", "cand-8740", "cand-8742", "cand-8743", "cand-8744", "cand-8745", "cand-8746", "cand-8747"],
    )
    new_statements[-1]["original_quote"] = p273_line

    # p.274: register the unnamed preacher, a procedure, and the unnamed S. Basilio group/cult.
    sid = "st-chp9-p274-1743-jesuit-panegyric"
    preacher = statement_by_id[sid]
    set_statement(
        preacher, "cand-11470", "cand-8760", "unnamed_jesuit_preached_virgin_panegyric_comparing_her_to_esther_in_1743",
        "Haskell reports that an unnamed Jesuit preached a 1743 panegyric of the Blessed Virgin comparing her to Esther.",
        "The preacher is not identified; note 1 cites a dated Zanetti report but its source is not independently consulted.",
        ["cand-11470", "cand-3403", "cand-8760", "cand-3427", "cand-8757"],
    )
    sid = "st-chp9-p274-pieta-governors-sought-plans"
    procedure = statement_by_id[sid]
    set_statement(
        procedure, "cand-8730", "cand-11471", "pieta_governors_followed_plan_selection_procedure",
        "Haskell says a similar plan-selection procedure seems to have been followed at the Pietà: its governors were required to seek suitable plans from highly regarded painters and choose the best.",
        "Preserve 'seems'; note 2 cites Urbani de Ghelthof, p.123, not independently consulted.",
        ["cand-8730", "cand-11471", "cand-8551"],
    )
    sid = "st-chp9-p274-sbasile-nobles-aconato-cult"
    nobles = statement_by_id[sid]
    set_statement(
        nobles, "cand-11472", "cand-11473", "unnamed_s_basilio_nobles_propagated_cult_of_aconato",
        "Haskell says a group of nobles associated with S. Basilio was devoted to propagating the cult of Beato Pietro Aconato.",
        "The individual's pronoun antecedent in the surrounding sentence remains ambiguous; do not attribute group membership to Corner or Angeli. Note 3 gives a source-scope citation, not independent verification.",
        ["cand-11472", "cand-11473", "cand-0730", "cand-0844", "cand-0106", "cand-8769"],
    )

    # Note-to-body backlinks for changed and split statements.
    for note_id, body_id in [
        ("st-chp9-p254-note2-molmenti-fabio-canal-attribution", "st-chp9-p254-grassi-apotheosis"),
        ("st-chp9-p254-note3-brunelli-callegari-reference", "st-chp9-p254-giustiniani-apotheosis"),
        ("st-chp9-p259-note4-pietro-picture-inventory-location", "st-chp9-p259-pietro-left-other-venetian-classics"),
        ("st-chp9-p263264-smith-purchases-document", "st-chp9-p263264-heirs-sold-pictures-to-smith"),
        ("st-chp9-p263264-udney-1762-list", "st-chp9-p263264-heirs-sold-to-udney-report"),
    ]:
        link_note_to_body(note_id, body_id)

    # Type corrections from the source-described object, not the index label alone.
    candidate_by_id["cand-2468"]["suggested_type"] = "person"
    candidate_by_id["cand-8639"]["suggested_type"] = "work"

    candidates.extend(new_candidates)
    mentions.extend(new_mentions)
    statements.extend(new_statements)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    statement_ids = {row["statement_id"] for row in statements}
    if len(candidate_ids) != len(candidates) or len(mention_ids) != len(mentions) or len(statement_ids) != len(statements):
        raise SystemExit("duplicate identifier introduced by plan")
    for row in statements:
        for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if cid and cid not in candidate_ids:
                raise SystemExit(f"statement endpoint missing candidate: {row['statement_id']} -> {cid}")
        for cid in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if cid not in candidate_ids:
                raise SystemExit(f"statement mention list has missing candidate: {row['statement_id']} -> {cid}")
    for row in mentions:
        if row["candidate_id"] not in candidate_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")

    remaining = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp9-")
        and row.get("qualifiers", {}).get("relation_candidate")
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if remaining:
        raise SystemExit(f"planned Chapter 9 relation candidates still lack endpoints: {sorted(remaining)}")

    encoded = {
        candidate_path: encode_csv(candidate_fields, candidates),
        mention_path: encode_csv(mention_fields, mentions),
        statement_path: encode_jsonl(statements),
    }
    print("Chapter 9 S2 endpoint audit plan")
    print(f"new candidates: {len(new_candidates)} (cand-11465–cand-11473)")
    print(f"new mentions: {len(new_mentions)}; existing mention remaps: 4")
    print(f"new statements: {len(new_statements)}")
    print("type corrections: cand-2468 event→person; cand-8639 archive→work")
    print("relation dispositions: all 19 prior missing-endpoint rows resolved; 3 broad claims and 4 composite summaries retained as non-relations")
    print(f"remaining Chapter 9 relation candidates without endpoints: {len(remaining)}")
    if not args.apply:
        for path, content in encoded.items():
            old = path.read_text(encoding="utf-8-sig")
            diff = list(difflib.unified_diff(
                old.splitlines(), content.splitlines(),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (planned)",
                lineterm="",
            ))
            print(f"{path.name}: {len(diff)} diff lines")
        print("DRY-RUN only; pass --apply after reviewing this plan.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp9-s2-endpoint-audit-"))
    for path in paths:
        shutil.copy2(path, backup_dir / path.name)
    for path, content in encoded.items():
        atomic_write(path, content)
    print(f"applied; recovery copies: {backup_dir}")


if __name__ == "__main__":
    main()
