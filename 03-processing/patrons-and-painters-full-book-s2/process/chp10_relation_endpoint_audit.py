"""Controlled Chapter 10 S2 relation-candidate and footnote audit.

Defaults to dry-run. The script checks the current source/segment hashes and
the exact open-endpoint set before planning a table write.
"""
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
SOURCE_PATHS = {
    "02-sources/02-Markdown/10_CHP-10_intro.md": ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md",
}
EXPECTED_MAX_CANDIDATE = 11473
EXPECTED_OPEN_ENDPOINT_IDS = {
    "st-chp10-notes-p280n5-presentation-dated-1713",
    "st-chp10-notes-p280n5-susanna-dated-1713",
    "st-chp10-p276-similar-regimes-and-tiepolo",
    "st-chp10-p277-northern-visitors-wanted-records",
    "st-chp10-p282-italian-collection-commissions",
    "st-chp10-p282-wilhelm-love-of-art",
    "st-chp10-p283-wilhelm-dutch-collecting",
    "st-chp10-p284-crozat-patronage-aristocratic-contact",
    "st-chp10-p284-crozat-weekly-meetings",
    "st-chp10-p285-carriera-met-artists",
    "st-chp10-p286-burlington-architecture",
    "st-chp10-p287-amigoni-income",
    "st-chp10-p293-note4-franz-schoenborn-letter",
    "st-chp10-p293-note4-travel-dates",
    "st-chp10-p301-smith-artists-business-arrangements",
    "st-chp10-p312-employed-artists-recorded-dropsical-features",
    "st-chp10-p312-gonzaga-employed-romano-and-castiglione",
    "st-chp10-p312-portrait-sculpture-engraving-artists",
    "st-chp10-p312-royal-generosity-to-artists",
    "st-chp10-p312-simonini-battles-and-campaigns",
    "st-chp10-p313-schulenburg-collection-history-and-genre-paintings",
    "st-chp10-p315-both-collections-held-marco-ricci-and-zuccarelli-works",
    "st-chp10-p315-neither-collection-had-tiepolo-paintings",
    "st-chp10-p315-piazzetta-pittoni-guardi-not-particularly-favoured-by-smith",
    "st-chp10-p317-italian-intellectuals-travelled-abroad",
    "st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled",
    "st-chp10-p51-caption-date",
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
    parser.add_argument("--show-diff", action="store_true", help="print the planned unified diffs during dry-run")
    args = parser.parse_args()

    candidate_path = TABLES / "entity-candidates.csv"
    statement_path = TABLES / "book-statements.jsonl"
    segment_path = TABLES / "segments.jsonl"
    paths = [candidate_path, statement_path]

    segments = {row["segment_id"]: row for row in read_jsonl(segment_path)}
    source_lines = {}
    for source_name, path in SOURCE_PATHS.items():
        raw = path.read_bytes()
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        source_lines[source_name] = lines
        actual = hashlib.sha256(raw).hexdigest()
        applicable = [row for row in segments.values() if row.get("source_file") == source_name and row["segment_id"].startswith("chp-10:")]
        if not applicable:
            raise SystemExit(f"no Chapter 10 segments found for {source_name}")
        if any(row.get("asset_sha256") != actual for row in applicable):
            raise SystemExit(f"source asset changed: {source_name}")
        for meta in applicable:
            text = "\n".join(lines[int(meta["line_start"]) - 1 : int(meta["line_end"])])
            if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
                raise SystemExit(f"source segment changed: {meta['segment_id']}")

    candidate_fields, candidates = read_csv(candidate_path)
    statements = read_jsonl(statement_path)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    statement_by_id = {row["statement_id"]: row for row in statements}
    original_candidate_types = {row["candidate_id"]: row["suggested_type"] for row in candidates}
    original_statement_by_id = copy.deepcopy(statement_by_id)
    if len(candidate_by_id) != len(candidates) or len(statement_by_id) != len(statements):
        raise SystemExit("duplicate identifiers in candidate or statement table")
    maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
    if maximum != EXPECTED_MAX_CANDIDATE:
        raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {maximum}")

    open_ids = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp10-")
        and row.get("qualifiers", {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if open_ids != EXPECTED_OPEN_ENDPOINT_IDS:
        raise SystemExit(f"Chapter 10 open endpoint set changed: {sorted(open_ids)}")

    expected_endpoints = {
        "st-chp10-p282-unsuccessful-invitations": ("cand-1325", "cand-0168"),
        "st-chp10-notes-p282n3-cignani-john-the-baptist": ("cand-0748", "cand-9323"),
        "st-chp10-notes-p282n3-cignani-jupiter-giving-suck": ("cand-0748", "cand-9324"),
        "st-chp10-notes-p282n3-franceschini-venus-graces": ("cand-1069", "cand-9325"),
        "st-chp10-notes-p282n3-dal-sole-st-teresa": ("cand-2480", "cand-9326"),
        "st-chp10-notes-p282n3-dal-sole-rape-sabines": ("cand-2480", "cand-9327"),
        "st-chp10-p282-balestra-refused-regular-employment": ("cand-0168", "cand-1325"),
        "st-chp10-p282-trevisani-refused-regular-employment": ("cand-2650", "cand-1325"),
        "st-chp10-p312-gonzaga-employed-romano-and-castiglione": ("cand-6669", None),
        "st-chp10-p312-portrait-sculpture-engraving-artists": ("cand-2401", None),
        "st-chp10-p312-simonini-battles-and-campaigns": ("cand-2401", None),
        "st-chp10-p293-note4-franz-schoenborn-letter": (None, "cand-9451"),
        "st-chp10-p293-note4-travel-dates": (None, "cand-2772"),
    }
    for sid, expected in expected_endpoints.items():
        row = statement_by_id.get(sid)
        if not row or (row.get("subject_candidate_id"), row.get("object_candidate_id")) != expected:
            raise SystemExit(f"statement precondition changed: {sid}")
    expected_types = {
        "cand-1918": "work", "cand-1953": "work", "cand-8841": "term", "cand-8843": "work",
        "cand-9585": "work", "cand-9625": "work", "cand-9628": "work", "cand-9629": "work",
        "cand-9630": "work", "cand-9631": "work", "cand-9632": "work", "cand-9633": "work",
        "cand-9634": "work", "cand-9635": "work", "cand-9645": "work",
    }
    for cid, expected in expected_types.items():
        if cid not in candidate_by_id or candidate_by_id[cid]["suggested_type"] != expected:
            raise SystemExit(f"candidate type precondition changed: {cid}")
    if candidate_by_id.get("cand-9328", {}).get("suggested_type") != "place":
        raise SystemExit("Augsburg must remain a place candidate")
    if candidate_by_id.get("cand-9636", {}).get("suggested_type") != "work":
        raise SystemExit("the identified Amigoni portrait must remain a work candidate")

    new_statements = []
    new_ids = set(statement_by_id)

    def set_statement(row, subject, obj, predicate, claim, qualification, mentioned, relation=True, negation=None):
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = obj
        row["predicate"] = predicate
        q = row.setdefault("qualifiers", {})
        q["claim"] = claim
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = list(dict.fromkeys(mentioned))
        q["relation_candidate"] = relation
        if negation is not None:
            q["negation"] = negation
        return row

    def clone_statement(parent_id, new_id, **kwargs):
        if new_id in new_ids:
            raise SystemExit(f"statement ID already exists: {new_id}")
        row = copy.deepcopy(statement_by_id[parent_id])
        row["statement_id"] = new_id
        set_statement(row, **kwargs)
        new_ids.add(new_id)
        statement_by_id[new_id] = row
        new_statements.append(row)
        return row

    def mark_nonrelation(sid, claim=None, qualification=None, predicate=None):
        row = statement_by_id[sid]
        q = row["qualifiers"]
        q["relation_candidate"] = False
        if claim is not None:
            q["claim"] = claim
        if qualification is not None:
            q["qualification"] = qualification
        if predicate is not None:
            row["predicate"] = predicate

    def append_unique(values, value):
        if value not in values:
            values.append(value)

    def link_note_body(note_id, body_id):
        q = statement_by_id[note_id]["qualifiers"]
        append_unique(q.setdefault("related_body_statement_ids", []), body_id)
        append_unique(q.setdefault("linked_body_statement_ids", []), body_id)

    def link_body_note(body_id, note_id):
        q = statement_by_id[body_id]["qualifiers"]
        append_unique(q.setdefault("footnote_note_statement_ids", []), note_id)

    def clear_footnote_link(row):
        q = row["qualifiers"]
        for key in list(q):
            if key.startswith("footnote") or key == "pending_note_source_line":
                q.pop(key, None)

    # Dates and broad contextual statements are source claims, not entity relations.
    for sid in [
        "st-chp10-notes-p280n5-presentation-dated-1713",
        "st-chp10-notes-p280n5-susanna-dated-1713",
        "st-chp10-p276-similar-regimes-and-tiepolo",
        "st-chp10-p277-northern-visitors-wanted-records",
        "st-chp10-p282-wilhelm-love-of-art",
        "st-chp10-p284-crozat-weekly-meetings",
        "st-chp10-p286-burlington-architecture",
        "st-chp10-p301-smith-artists-business-arrangements",
        "st-chp10-p312-employed-artists-recorded-dropsical-features",
        "st-chp10-p312-royal-generosity-to-artists",
        "st-chp10-p317-italian-intellectuals-travelled-abroad",
        "st-chp10-p51-caption-date",
    ]:
        q = statement_by_id[sid]["qualifiers"]
        q["relation_candidate"] = False
        q["qualification"] = (q.get("qualification", "").rstrip() + " This is retained as a source assertion or property, not a formal relation candidate.").strip()

    # p.282: retain the collection profile and extract four explicit commissioned artists.
    parent_id = "st-chp10-p282-italian-collection-commissions"
    parent = statement_by_id[parent_id]
    parent["predicate"] = "wilhelm_collected_italian_works_especially_giordano"
    parent["qualifiers"]["claim"] = "Haskell says Johann Wilhelm amassed Italian works, especially works by Luca Giordano."
    parent["qualifiers"]["qualification"] = "No individual Giordano work is identified in this passage; the note marker after Italy is retained with this collection statement."
    parent["qualifiers"]["relation_candidate"] = False
    commission_specs = [
        ("cignani", "cand-0748", "Carlo Cignani"),
        ("franceschini", "cand-1069", "Marcantonio Franceschini"),
        ("dal-sole", "cand-2480", "Giovan Gioseffo dal Sole"),
        ("trevisani", "cand-2650", "Francesco Trevisani"),
    ]
    commission_body_ids = {}
    for slug, artist_id, label in commission_specs:
        sid = f"st-chp10-p282-wilhelm-commissioned-{slug}"
        row = clone_statement(
            parent_id, sid, subject="cand-1325", obj=artist_id,
            predicate=f"wilhelm_commissioned_{slug}_to_work_for_him",
            claim=f"Haskell says Johann Wilhelm commissioned {label} to work for him in Bologna and Rome.",
            qualification="The source identifies the artist and the broad locations, but no individual job dates or surviving commissioned work in the body sentence.",
            mentioned=["cand-1325", artist_id, "cand-4490", "cand-3398"],
        )
        clear_footnote_link(row)
        commission_body_ids[slug] = sid

    # The failed invitations name two artists; the third note carries work details and a cross-page continuation.
    invitations_id = "st-chp10-p282-unsuccessful-invitations"
    invitations = statement_by_id[invitations_id]
    set_statement(
        invitations, "cand-1325", "cand-0168", "wilhelm_unsuccessfully_invited_balestra_to_dusseldorf",
        "Haskell says Johann Wilhelm tried unsuccessfully to persuade Antonio Balestra to come to Düsseldorf.",
        "An unsuccessful invitation does not establish that Balestra visited Düsseldorf.",
        ["cand-1325", "cand-0168", "cand-0955"],
    )
    clone_statement(
        invitations_id, "st-chp10-p282-wilhelm-unsuccessfully-invited-carriera",
        subject="cand-1325", obj="cand-0581", predicate="wilhelm_unsuccessfully_invited_carriera_to_dusseldorf",
        claim="Haskell says Johann Wilhelm tried unsuccessfully to persuade Rosalba Carriera to come to Düsseldorf.",
        qualification="An unsuccessful invitation does not establish that Carriera visited Düsseldorf; her separate picture-acquisition role is stated in the source but not expanded here.",
        mentioned=["cand-1325", "cand-0581", "cand-0955"],
    )
    p282_note_work_ids = {
        "st-chp10-notes-p282n3-cignani-john-the-baptist": ("cand-9323", "cand-0748", "St John the Baptist", "Cignani"),
        "st-chp10-notes-p282n3-cignani-jupiter-giving-suck": ("cand-9324", "cand-0748", "Jupiter Giving Suck", "Cignani"),
        "st-chp10-notes-p282n3-franceschini-venus-graces": ("cand-9325", "cand-1069", "Venus and The Three Graces", "Franceschini"),
        "st-chp10-notes-p282n3-dal-sole-st-teresa": ("cand-9326", "cand-2480", "St Teresa Wounded by Christ", "dal Sole"),
        "st-chp10-notes-p282n3-dal-sole-rape-sabines": ("cand-9327", "cand-2480", "The Rape of the Sabines", "dal Sole"),
    }
    note_to_commission = {
        "Cignani": commission_body_ids["cignani"],
        "Franceschini": commission_body_ids["franceschini"],
        "dal Sole": commission_body_ids["dal-sole"],
    }
    for note_id, (work_id, artist_id, title, artist_label) in p282_note_work_ids.items():
        row = statement_by_id[note_id]
        creator_claim = f"Haskell's note says {title} was painted by {artist_label}."
        commissioner_claim = f"Haskell's note says {title} was painted for Johann Wilhelm."
        if note_id == "st-chp10-notes-p282n3-franceschini-venus-graces":
            creator_claim = "Haskell's note says Marcantonio Franceschini painted Venus and The Three Graces."
            commissioner_claim = "Haskell's note says Marcantonio Franceschini painted Venus and The Three Graces for Johann Wilhelm."
        set_statement(
            row, work_id, artist_id, "created_by",
            creator_claim,
            row["qualifiers"].get("qualification", ""),
            [work_id, artist_id, "cand-1325"],
        )
        commissioner_id = note_id + "-commissioner"
        clone_statement(
            note_id, commissioner_id,
            subject=work_id, obj="cand-1325", predicate="commissioned_by",
            claim=commissioner_claim,
            qualification=row["qualifiers"].get("qualification", ""),
            mentioned=[work_id, artist_id, "cand-1325"],
        )
        body_id = note_to_commission[artist_label]
        link_note_body(note_id, body_id)
        link_note_body(commissioner_id, body_id)
        link_body_note(invitations_id, commissioner_id)

    locations_id = "st-chp10-notes-p282n3-cignani-locations"
    mark_nonrelation(
        locations_id,
        qualification="The two cities are reported for the pair without mapping a city to either painting; this is a location assertion, not an artwork-to-place relation.",
    )
    link_note_body(locations_id, commission_body_ids["cignani"])

    note3_crosspage = {
        "st-chp10-p282-balestra-refused-regular-employment": invitations_id,
        "st-chp10-p282-trevisani-refused-regular-employment": commission_body_ids["trevisani"],
    }
    for note_id, body_id in note3_crosspage.items():
        q = statement_by_id[note_id]["qualifiers"]
        q.pop("footnote_marker_status", None)
        q["footnote_number"] = 3
        subject_name = "Antonio Balestra" if "balestra" in note_id else "Francesco Trevisani"
        q["claim"] = f"Haskell's note 3 says {subject_name} refused regular employment under Johann Wilhelm and points to a manuscript life."
        q["qualification"] = "The p.282 note 3 text continues at p.283 L163–164; its continuation identifies manuscript lives in Biblioteca Augusta, Perugia, MSS. 1383. This cited manuscript was not consulted."
        link_note_body(note_id, body_id)
        link_body_note(invitations_id, note_id)

    # p.283: split the dated visit to Holland from the unspecified collection profile.
    sid = "st-chp10-p283-wilhelm-dutch-collecting"
    row = statement_by_id[sid]
    row["predicate"] = "wilhelm_collected_works_by_dutch_artists"
    row["qualifiers"]["claim"] = "Haskell says Johann Wilhelm avidly collected works by Jan Weenix, Adrian van der Werff, and many other Dutch artists."
    row["qualifiers"]["qualification"] = "No individual works or titles are supplied; the unnamed 'many others' are not expanded."
    row["qualifiers"]["relation_candidate"] = False
    clone_statement(
        sid, "st-chp10-p283-wilhelm-visited-holland-1696",
        subject="cand-1325", obj="cand-6084", predicate="visited",
        claim="Haskell says Johann Wilhelm visited Holland in 1696.",
        qualification="The year is reported in Haskell's narrative; no further itinerary is stated.",
        mentioned=["cand-1325", "cand-6084"],
    )

    # p.284: Crozat's patronage explicitly connects three named artists to aristocratic society.
    sid = "st-chp10-p284-crozat-patronage-aristocratic-contact"
    patronage = statement_by_id[sid]
    artist_specs = [
        ("pellegrini", "cand-1862", "Pellegrini"),
        ("carriera", "cand-0581", "Carriera"),
        ("zanetti", "cand-2838", "Zanetti"),
    ]
    for i, (slug, artist_id, label) in enumerate(artist_specs):
        target = sid if i == 0 else f"st-chp10-p284-crozat-patronage-{slug}-contact"
        set_statement(
            patronage, "cand-0894", artist_id, "crozat_patronage_connected_artist_to_aristocratic_society",
            f"Haskell says Crozat's patronage brought {label} into contact with aristocratic society.",
            "This is Haskell's account of social contact through patronage; it does not identify a particular commission or work.",
            ["cand-0894", artist_id, "cand-1447"],
        ) if i == 0 else clone_statement(
            sid, target, subject="cand-0894", obj=artist_id,
            predicate="crozat_patronage_connected_artist_to_aristocratic_society",
            claim=f"Haskell says Crozat's patronage brought {label} into contact with aristocratic society.",
            qualification="This is Haskell's account of social contact through patronage; it does not identify a particular commission or work.",
            mentioned=["cand-0894", artist_id, "cand-1447"],
        )

    # p.285: split Carriera's contacts into seven individually supported candidates.
    sid = "st-chp10-p285-carriera-met-artists"
    contacts = [
        ("rigaud", "cand-2198", "Rigaud", True),
        ("watteau", "cand-2804", "Watteau", True),
        ("coypel", "cand-0866", "Coypel", False),
        ("vleughels", "cand-2789", "Vleughels", False),
        ("oppenord", "cand-1781", "Oppenord", False),
        ("de-troy", "cand-2656", "de Troy", False),
        ("mariette", "cand-1547", "Mariette", False),
    ]
    for i, (slug, person_id, label, admired) in enumerate(contacts):
        claim = (
            f"Haskell says Carriera met {label}, who expressed deep admiration for her."
            if admired else f"Haskell lists {label} among the artists and connoisseurs Carriera met."
        )
        qual = (
            "The source explicitly reports deep admiration by Rigaud."
            if slug == "rigaud" else
            "The source explicitly reports deep admiration by Watteau."
            if slug == "watteau" else
            "The source gives the name in a collective list without individual encounter details."
        )
        kwargs = dict(
            subject="cand-0581", obj=person_id, predicate="met",
            claim=claim, qualification=qual, mentioned=["cand-0581", person_id],
        )
        if i == 0:
            set_statement(statement_by_id[sid], **kwargs)
        else:
            clone_statement(sid, f"st-chp10-p285-carriera-met-{slug}", **kwargs)

    # p.287 retains the qualified report and its explicit England endpoint.
    set_statement(
        statement_by_id["st-chp10-p287-amigoni-income"], "cand-0094", "cand-8983",
        "left_england_with_supposed_savings_partly_from_court_work",
        "Haskell says Amigoni was supposed to have taken £4,000–£5,000 when he left England about ten years after arriving, some from court work.",
        "Preserve the source's 'supposed' and approximate interval; the court, work, and arrival/departure dates are not identified more precisely.",
        ["cand-0094", "cand-8983"],
    )

    # p.293 note 4: identify the letter's author, addressee, and person introduced.
    sid = "st-chp10-p293-note4-franz-schoenborn-letter"
    set_statement(
        statement_by_id[sid], "cand-9451", "cand-1868", "introduces",
        "Haskell cites Johann Philip Franz's 12 July 1723 letter to Friedrich Karl Schönborn as introducing Pellegrini.",
        "The letter was not consulted; the statement reports Haskell's note and the cited Von Freeden locator.",
        ["cand-9451", "cand-2398", "cand-2397", "cand-1868"],
    )
    clone_statement(
        sid, "st-chp10-p293-note4-franz-letter-authored-by",
        subject="cand-9451", obj="cand-2398", predicate="authored_by",
        claim="Haskell identifies Johann Philip Franz as the author of the letter dated 12 July 1723.",
        qualification="The letter was not consulted; this is the attribution stated in Haskell's note.",
        mentioned=["cand-9451", "cand-2398"],
    )
    clone_statement(
        sid, "st-chp10-p293-note4-franz-letter-addressed-to",
        subject="cand-9451", obj="cand-2397", predicate="addressed_to",
        claim="Haskell identifies Friedrich Karl Schönborn as the addressee of the letter dated 12 July 1723.",
        qualification="The letter was not consulted; this is the addressee stated in Haskell's note.",
        mentioned=["cand-9451", "cand-2397"],
    )
    sid = "st-chp10-p293-note4-travel-dates"
    set_statement(
        statement_by_id[sid], "cand-1868", "cand-2772", "travelled_to",
        "Haskell's note says Pellegrini went to Vienna in 1725–1727.",
        "This is the itinerary stated in Haskell's note, not an independently checked travel record.",
        ["cand-1868", "cand-2772", "cand-0581"],
    )
    clone_statement(
        sid, "st-chp10-p293-note4-carriera-travelled-to-vienna",
        subject="cand-0581", obj="cand-2772", predicate="travelled_to",
        claim="Haskell's note says Rosalba Carriera went to Vienna in 1730.",
        qualification="This reads the note's abbreviated second clause as Carriera going to Vienna; it is Haskell's statement, not an independently checked itinerary.",
        mentioned=["cand-0581", "cand-2772", "cand-1868"],
    )

    # p.312: split the Gonzaga employment and portrait activity by named person.
    sid = "st-chp10-p312-gonzaga-employed-romano-and-castiglione"
    set_statement(
        statement_by_id[sid], "cand-1194", "cand-6669", "employed_by",
        "Haskell says Giulio Romano had been much employed by the Gonzaga in earlier, more prosperous times.",
        "Retain the family/group scope of 'the Gonzaga'; individual patron identity and employment dates are not supplied.",
        ["cand-1194", "cand-6669", "cand-0602"],
    )
    clone_statement(
        sid, "st-chp10-p312-castiglione-employed-by-gonzaga",
        subject="cand-0602", obj="cand-6669", predicate="employed_by",
        claim="Haskell says Castiglione had been much employed by the Gonzaga in earlier, more prosperous times.",
        qualification="Retain the family/group scope of 'the Gonzaga'; individual patron identity and employment dates are not supplied.",
        mentioned=["cand-0602", "cand-6669", "cand-1194"],
    )
    sid = "st-chp10-p312-portrait-sculpture-engraving-artists"
    set_statement(
        statement_by_id[sid], "cand-2401", None, "schulenburg_portrait_artists_collective_list",
        "Haskell lists artists who drew, painted, sculpted, or engraved Schulenburg's features, with further unnamed artists.",
        "The original collective summary is retained as context; each named artist's activity is recorded in a separate statement, while specific portraits remain unidentified.",
        ["cand-2401", "cand-1901", "cand-1918", "cand-1727", "cand-1743", "cand-0637", "cand-1245", "cand-2435", "cand-0849", "cand-1703", "cand-1948"],
        relation=False,
    )
    portrait_specs = [
        ("piazzetta", "cand-1901", "Piazzetta", "drew_portraits_of", "drew portraits of Schulenburg several times"),
        ("nazari", "cand-1727", "Nazari", "painted_portraits_of", "painted portraits of Schulenburg"),
        ("nogari", "cand-1743", "Nogari", "painted_portraits_of", "painted portraits of Schulenburg"),
        ("ceruti", "cand-0637", "Ceruti", "painted_portraits_of", "painted portraits of Schulenburg"),
        ("guardi", "cand-1245", "Guardi", "painted_portraits_of", "painted portraits of Schulenburg"),
        ("simonini", "cand-2435", "Simonini", "painted_portraits_of", "painted portraits of Schulenburg"),
        ("corradini", "cand-0849", "Corradini", "sculpted_portraits_of", "sculpted portraits of Schulenburg"),
        ("morlaiter", "cand-1703", "Morlaiter", "sculpted_portraits_of", "sculpted portraits of Schulenburg"),
        ("pitteri", "cand-1948", "Pitteri", "engraved_portraits_of", "engraved portraits of Schulenburg"),
    ]
    for slug, artist_id, label, predicate, activity in portrait_specs:
        clone_statement(
            sid, f"st-chp10-p312-{slug}-{predicate.replace('_', '-')}",
            subject=artist_id, obj="cand-2401", predicate=predicate,
            claim=f"Haskell says {label} {activity}.",
            qualification="No individual portrait or other object is titled in this list.",
            mentioned=["cand-2401", artist_id] + (["cand-1918"] if slug == "piazzetta" else []),
        )
    sid = "st-chp10-p312-simonini-battles-and-campaigns"
    set_statement(
        statement_by_id[sid], "cand-2435", "cand-2401", "apparently_accompanied_on_campaigns",
        "Haskell says Francesco Simonini apparently accompanied Schulenburg on his campaigns.",
        "Preserve 'apparently'; Haskell does not state that accompaniment as certain.",
        ["cand-2435", "cand-2401", "cand-9585"],
    )
    clone_statement(
        sid, "st-chp10-p312-schulenburg-battle-paintings-created-by-simonini",
        subject="cand-9585", obj="cand-2435", predicate="created_by",
        claim="Haskell says Simonini painted a group of Schulenburg's principal battles.",
        qualification="The source identifies these paintings only as a group; no titles or locations are supplied.",
        mentioned=["cand-9585", "cand-2435", "cand-2401"],
    )

    # p.313 and p.315 collection profiles do not identify individual objects.
    mark_nonrelation(
        "st-chp10-p313-schulenburg-collection-history-and-genre-paintings",
        qualification="This is a collection profile naming genres and makers; no individual paintings are identified.",
    )
    mark_nonrelation(
        "st-chp10-p315-schulenburg-collection-rich-in-three-painters",
        qualification="The individual works and their number are not specified; retain this as a collection profile.",
    )
    mark_nonrelation(
        "st-chp10-p315-smith-collection-based-on-three-painters",
        qualification="The artists are named but individual works and counts are not supplied; retain this as a collection profile.",
    )
    mark_nonrelation(
        "st-chp10-p315-schulenburg-owned-ricci-portrait-and-paintings",
        qualification="Retain the ambiguity in 'of Ricci'; the plural/group reference is not an individually identified artwork.",
    )
    mark_nonrelation(
        "st-chp10-p315-both-collections-held-marco-ricci-and-zuccarelli-works",
        predicate="haskell_profiles_two_collections_with_works_by_ricci_and_zuccarelli",
        qualification="The statement describes two collections and unspecified works; it does not identify common physical objects or a single work-group endpoint.",
    )
    both_collections = statement_by_id["st-chp10-p315-both-collections-held-marco-ricci-and-zuccarelli-works"]
    both_collections["subject_candidate_id"] = None
    both_collections["object_candidate_id"] = None
    sid = "st-chp10-p315-neither-collection-had-tiepolo-paintings"
    set_statement(
        statement_by_id[sid], "cand-9626", "cand-2569", "collection_did_not_contain_painting_by",
        "Haskell says Joseph Smith's collection contained no painting by Tiepolo.",
        "Negative collection evidence is retained as an assertion; it does not create a positive ownership relation.",
        ["cand-9626", "cand-2569", "cand-2440", "cand-2401", "cand-9622"],
        relation=False, negation=True,
    )
    clone_statement(
        sid, "st-chp10-p315-schulenburg-collection-had-no-tiepolo-painting",
        subject="cand-9622", obj="cand-2569", predicate="collection_did_not_contain_painting_by",
        claim="Haskell says Schulenburg's collection contained no painting by Tiepolo.",
        qualification="Negative collection evidence is retained as an assertion; it does not create a positive ownership relation.",
        mentioned=["cand-9622", "cand-2569", "cand-2401", "cand-2440", "cand-9626"],
        relation=False, negation=True,
    )
    sid = "st-chp10-p315-piazzetta-pittoni-guardi-not-particularly-favoured-by-smith"
    preferences = [
        ("piazzetta", "cand-3862", "Piazzetta"),
        ("pittoni", "cand-3870", "Pittoni"),
        ("guardi", "cand-1245", "Gian Antonio Guardi"),
    ]
    for i, (slug, artist_id, label) in enumerate(preferences):
        kwargs = dict(
            subject=artist_id, obj="cand-2440", predicate="not_particularly_favoured_by",
            claim=f"Haskell says {label} was not particularly favoured by Smith.",
            qualification="This is a qualified preference comparison; it does not establish that Smith never acquired the artist's work.",
            mentioned=["cand-2440", artist_id],
            relation=False, negation=True,
        )
        if i == 0:
            set_statement(statement_by_id[sid], **kwargs)
        else:
            clone_statement(sid, f"st-chp10-p315-{slug}-not-particularly-favoured-by-smith", **kwargs)

    # p.318 explicitly names three people and an additional unnamed group.
    sid = "st-chp10-p318-giannone-pilati-baretti-and-other-thinkers-expelled"
    expellees = [
        ("giannone", "cand-1164", "Pietro Giannone", "was"),
        ("pilati", "cand-1930", "Carlo Antonio Pilati", "was"),
        ("baretti", "cand-0245", "Giuseppe Baretti", "was"),
        ("other-unnamed-thinkers", "cand-9712", "other unnamed unorthodox thinkers", "were"),
    ]
    for i, (slug, person_id, label, verb) in enumerate(expellees):
        kwargs = dict(
            subject=person_id, obj="cand-8838", predicate="expelled_from_territory",
            claim=f"Haskell says {label} {verb} expelled from Venetian territory.",
            qualification="The source gives no individual dates or separate expulsion details; 'her territory' refers to the Republic of Venice.",
            mentioned=["cand-8838", person_id],
        )
        if i == 0:
            set_statement(statement_by_id[sid], **kwargs)
        else:
            clone_statement(sid, f"st-chp10-p318-{slug}-expelled-from-venetian-territory", **kwargs)

    # Candidate types reflect the lack of individually identifiable works or collective type.
    for cid in expected_types:
        candidate_by_id[cid]["suggested_type"] = ""

    # Keep the existing p.315 shipment relation, whose repeated transfer and date are explicit.
    # These are source-derived candidate statements only; no S6 formal relations are added.

    statements.extend(new_statements)
    all_candidate_ids = set(candidate_by_id)
    all_statement_ids = [row["statement_id"] for row in statements]
    if len(set(all_statement_ids)) != len(all_statement_ids):
        raise SystemExit("duplicate statement identifier introduced by plan")
    for row in statements:
        for cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if cid and cid not in all_candidate_ids:
                raise SystemExit(f"statement endpoint missing candidate: {row['statement_id']} -> {cid}")
        for cid in row.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if cid not in all_candidate_ids:
                raise SystemExit(f"statement mention list has missing candidate: {row['statement_id']} -> {cid}")

    remaining = {
        row["statement_id"]
        for row in statements
        if row["statement_id"].startswith("st-chp10-")
        and row.get("qualifiers", {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    }
    if remaining:
        raise SystemExit(f"planned Chapter 10 relation candidates still lack endpoints: {sorted(remaining)}")
    missing_segments = {row["segment_id"] for row in statements if row["statement_id"] in {r["statement_id"] for r in new_statements} and row["segment_id"] not in segments}
    if missing_segments:
        raise SystemExit(f"new statement source segment missing: {sorted(missing_segments)}")

    encoded = {
        candidate_path: encode_csv(candidate_fields, candidates),
        statement_path: encode_jsonl(statements),
    }
    print("Chapter 10 S2 relation and footnote audit plan")
    print(f"open relation candidates before: {len(open_ids)}")
    print(f"new statements: {len(new_statements)}; new candidates/mentions: 0/0")
    print(f"candidate type corrections: {len(expected_types)} unidentified groups changed to no KU type")
    print("p.282 note 3: five artwork creator/commissioner pairs linked to the body; p.283 continuation linked to note 3")
    print("collection profiles, dates, negative claims, and generalized assertions retained as non-relations")
    print(f"Chapter 10 open relation candidates after plan: {len(remaining)}")
    if not args.apply:
        for path, content in encoded.items():
            old = path.read_text(encoding="utf-8-sig")
            diff = list(difflib.unified_diff(
                old.splitlines(), content.splitlines(),
                fromfile=str(path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)) + " (planned)",
                lineterm="",
            ))
            print(f"{path.name}: {len(diff)} diff lines")
            if args.show_diff:
                if path == candidate_path:
                    for cid in expected_types:
                        before = original_candidate_types[cid]
                        after = candidate_by_id[cid]["suggested_type"]
                        print(f"candidate {cid}: {before!r} -> {after!r}")
                else:
                    for row in statements:
                        sid = row["statement_id"]
                        if sid not in original_statement_by_id or row != original_statement_by_id[sid]:
                            q = row.get("qualifiers", {})
                            endpoints = f"{row.get('subject_candidate_id') or '∅'} → {row.get('object_candidate_id') or '∅'}"
                            extra = ""
                            if q.get("footnote_number"):
                                extra = f"; note={q['footnote_number']}"
                            if q.get("negation"):
                                extra += "; negated"
                            print(f"{sid}: {endpoints}; {row.get('predicate')}; relation={q.get('relation_candidate')}{extra}; {q.get('claim')}")
        print("DRY-RUN only; review the plan, then pass --apply to write.")
        return

    backup_dir = Path(tempfile.mkdtemp(prefix="pnp-chp10-s2-relation-audit-"))
    for path in paths:
        shutil.copy2(path, backup_dir / path.name)
    for path, content in encoded.items():
        atomic_write(path, content)
    print(f"applied; recovery copies: {backup_dir}")


if __name__ == "__main__":
    main()
