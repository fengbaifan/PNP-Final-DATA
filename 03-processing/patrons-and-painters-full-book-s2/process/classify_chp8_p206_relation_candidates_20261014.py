"""Classify and refine S2 statements for the p.206 Roomer passage."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l30-41"
BACKUP_SUFFIX = ".bak-s2-chp8-p206-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "9509f349fb60ccda6b45a7760f0709ec9c110682677564c78c76aa568bdf8900",
    CANDIDATES: "8a1e87101b9be8146d7817bba0cf35db0c7d48b9acb3d74731325735796d7d53",
    MENTIONS: "356ade738f8a81ba391f2b61472a303c557422f815e9fb740a783860f5539882",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "5b3d569aa1ba988b5d8d012525571e678226dbbc1031c9cc0e50db0e4d4f1bd0"

UNSET_IDS = {
    "st-chp8-p206-bassano-animal-pieces-qualified-authorial-inference",
    "st-chp8-p206-feast-of-herod-depicts-daughter-of-herodias",
    "st-chp8-p206-feast-of-herod-depicts-girl-holding-john-baptist-head",
    "st-chp8-p206-feast-of-herod-depicts-luxury-crowded-room-and-attendants",
    "st-chp8-p206-feast-of-herod-made-impact-in-naples",
    "st-chp8-p206-flemish-painters-settled-temporarily-in-rome",
    "st-chp8-p206-haskell-compared-roman-painting-and-venetian-colour",
    "st-chp8-p206-herod-depicted-as-aware-of-injustice",
    "st-chp8-p206-later-roomer-collection-less-documented",
    "st-chp8-p206-roomer-acquired-pictures-by-three-painters",
    "st-chp8-p206-roomer-collection-bridged-flemish-and-neapolitan-cultures",
    "st-chp8-p206-roomer-liked-flemish-subject-categories",
    "st-chp8-p206-roomer-quoted-inventory-request",
    "st-chp8-p206-rubens-feast-of-herod-maturity-and-approximate-date",
}
PRECLASSIFIED_IDS = {
    "st-chp8-p206-falcone-painted-battle-scenes-for-roomer",
    "st-chp8-p206-feast-of-herod-arrived-roomers-palace-c1640",
    "st-chp8-p206-haskell-suggested-depicted-cruelty-appealed-to-roomer",
    "st-chp8-p206-roomer-owned-hundreds-by-flemish-artists",
    "st-chp8-p206-roomer-preferred-war-as-safe-picturesque-subject",
    "st-chp8-p206-roomer-presumably-received-flemish-pictures-in-exchange",
    "st-chp8-p206-roomer-sent-neapolitan-paintings-to-low-countries",
    "st-chp8-p206-saraceni-closes-three-paintings-continuation",
    "st-chp8-p206-van-dyck-pictures-probably-acquired-locally",
    "st-chp8-p206-roomer-probably-acquired-st-sebastian-locally",
}
NEW_STATEMENT_IDS = {
    "st-chp8-p206-classical-discipline-imposed-clarity-on-venetian-colour",
    "st-chp8-p206-haskell-inferred-roomers-lack-of-intellectual-interests-from-bassano-pieces",
    "st-chp8-p206-roomer-continued-buying-hundreds-of-pictures",
    "st-chp8-p206-roomer-pictures-by-foreign-artists",
    "st-chp8-p206-foreign-artists-unfamiliar-to-neapolitan-painters",
}
CANDIDATE_SPECS = [
    (
        "cand-12029",
        "Unspecified pictures by Valentin, Simon Vouet and David de Haen acquired by Gaspar Roomer",
        "work",
        "Haskell says Roomer acquired pictures by these three named painters but gives no individual titles, quantities, dates, or transactions.",
        31,
    ),
    (
        "cand-12030",
        "Several hundred works by named Flemish painters in Gaspar Roomer's collection",
        "work",
        "Haskell reports several hundreds by the named painters and others; individual works are not listed, and the quantity remains approximate.",
        35,
    ),
    (
        "cand-12031",
        "Hundreds of pictures bought by Gaspar Roomer after his early Naples gallery",
        "work",
        "Haskell says Roomer continued buying hundreds of pictures after the early gallery; their nature is less documented and individual works are not identified.",
        38,
    ),
]
MENTION_SPECS = [
    (
        "m-s2-chp8-p206-acquired-pictures-by-three-painters",
        "cand-12029",
        "pictures by the Frenchmen Valentin and Simon Vouet and the Dutch David de Haen",
        "Unspecified source-defined group of works acquired by Roomer; the named painters are separately mapped as creators.",
    ),
    (
        "m-s2-chp8-p206-several-hundred-flemish-works",
        "cand-12030",
        "several hundreds by Paul Brill,\nPeter de Witte, Velvet Breughel, Leonard Bramer, Jacques Duyvelant, Cornelius\nPoelenburgh, Corneille Schut, Gioffredo Wals, Gerard van dor Bos and many others",
        "Approximate source-defined group; the listed artists are separately mapped as creators.",
    ),
]
UNCHANGED = object()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after every guard passes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    hashes = {path: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit("one or more tables or source files changed since this reviewed baseline")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES, MENTIONS)}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("a recovery copy already exists; inspect it before applying this script")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segments = read_jsonl(SEGMENTS)
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    segment_text = "\n".join(source_lines[29:41])
    if not segment or (segment["line_start"], segment["line_end"]) != (30, 41):
        raise SystemExit("p.206 segment metadata changed")
    if segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE] or segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.206 source asset or segment fingerprint changed")
    if sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.206 segment text changed since review")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(by_id) != len(statements) or len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("statement, candidate, or mention IDs are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if actual_unset != UNSET_IDS or len(page_rows) != 24:
        raise SystemExit(f"unexpected p.206 statement inventory: unset delta={sorted(actual_unset ^ UNSET_IDS)}, total={len(page_rows)}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")
    if {row[0] for row in CANDIDATE_SPECS} & set(candidate_by_id) or {row[0] for row in MENTION_SPECS} & set(mention_by_id):
        raise SystemExit("a planned candidate or mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12028:
        raise SystemExit("candidate sequence changed since the p.206 review")

    new_candidates = []
    for candidate_id, name, kind, detail, line in CANDIDATE_SPECS:
        new_candidates.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": kind, "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": detail, "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    for mention_id, candidate_id, surface, note in MENTION_SPECS:
        starts = [i for i in range(len(segment_text)) if segment_text.startswith(surface, i)]
        if len(starts) != 1:
            raise SystemExit(f"expected one exact surface for {mention_id}, got {len(starts)}")
        start = starts[0]
        mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)),
            "note": note,
        })
    target_mention = mention_by_id.get("m-chp8-p206-037")
    if not target_mention or target_mention["candidate_id"] != "cand-7407" or target_mention["surface_form"] != "hundreds of pictures":
        raise SystemExit("the later 'hundreds of pictures' mention no longer matches its expected prestate")
    target_mention["candidate_id"] = "cand-12031"
    target_mention["note"] = "Here the phrase refers to the hundreds of pictures Roomer continued buying after the early Naples gallery, not to the collection object itself."

    def excerpt(start_line: int, end_line: int, first: str, last: str) -> str:
        source = "\n".join(source_lines[start_line - 1:end_line])
        start, end = source.find(first), source.rfind(last)
        if start < 0 or end < start:
            raise SystemExit(f"expected source phrase missing at L{start_line}-L{end_line}: {first!r} ... {last!r}")
        return source[start:end + len(last)]

    def update(statement_id: str, relation: bool, note: str, *,
               predicate: str | None = None, subject=UNCHANGED,
               object_id=UNCHANGED, claim: str | None = None,
               qualification: str | None = None, extra: dict | None = None) -> None:
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = relation
        q["relation_candidate_note"] = note
        if claim is not None:
            q["claim"] = claim
        if qualification is not None:
            q["qualification"] = qualification
        if predicate is not None:
            row["predicate"] = predicate
        if subject is not UNCHANGED:
            row["subject_candidate_id"] = subject
        if object_id is not UNCHANGED:
            row["object_candidate_id"] = object_id
        if extra:
            q.update(extra)
            related = []
            for key in ("work_group_candidate_id", "destination_candidate_id", "requested_painter_group_candidate_id"):
                if key in extra:
                    related.append(extra[key])
            related.extend(extra.get("creator_candidate_ids", []))
            for key in ("creator_candidate_id", "notable_artist_candidate_id", "owner_candidate_id", "location_candidate_id"):
                if key in extra and extra[key]:
                    related.append(extra[key])
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), *related]))
        row["qualifiers"] = q

    decisions = {
        "st-chp8-p206-falcone-painted-battle-scenes-for-roomer": (True, "Haskell directly says Falcone painted a number of battle scenes for Roomer; the group is retained as source-specific and untitled."),
        "st-chp8-p206-roomer-acquired-pictures-by-three-painters": (True, "Roomer's acquisition of an unidentified work group by the three named painters is explicit; the painters are creator qualifiers, not the acquired objects."),
        "st-chp8-p206-roomer-preferred-war-as-safe-picturesque-subject": (True, "The source says war as a picturesque subject appealed to Roomer and immediately identifies battle scenes painted for him by Falcone; his non-participation remains a separate qualification."),
        "st-chp8-p206-saraceni-closes-three-paintings-continuation": (True, "The p.206 surname completes the p.205 statement that Roomer owned three paintings by Carlo Saraceni."),
        "st-chp8-p206-flemish-painters-settled-temporarily-in-rome": (True, "The source explicitly says many Flemish painters settled temporarily in Rome; their membership remains unspecified."),
        "st-chp8-p206-roomer-liked-flemish-subject-categories": (False, "This is a broad preference for subject categories, not a relation to a distinct identified work or artist."),
        "st-chp8-p206-roomer-quoted-inventory-request": (True, "Roomer explicitly wanted foreign painters summoned to prepare the inventory; the unidentified quoted writing is source context, not the relation target."),
        "st-chp8-p206-roomer-owned-hundreds-by-flemish-artists": (True, "Haskell directly attributes several hundreds of pictures to Roomer's collection; the works form a separate open group and the named painters are creators."),
        "st-chp8-p206-roomer-collection-bridged-flemish-and-neapolitan-cultures": (False, "This is Haskell's cultural interpretation of the collection, not an entity-to-entity historical relation."),
        "st-chp8-p206-haskell-compared-roman-painting-and-venetian-colour": (False, "The first clause describes qualities missing from Roman painting; the distinct causal relation to Venetian colour is split into its own statement."),
        "st-chp8-p206-later-roomer-collection-less-documented": (False, "This records Haskell's evidence limitation for the later collection; the separate claim that Roomer continued buying hundreds of pictures is captured in a new statement."),
        "st-chp8-p206-roomer-presumably-received-flemish-pictures-in-exchange": (True, "Haskell explicitly presents receipt of an unidentified work group in exchange as probable; the uncertainty remains in the claim."),
        "st-chp8-p206-roomer-probably-acquired-st-sebastian-locally": (True, "The source says the identified subject painting was probably acquired locally; attribution and probability remain qualified."),
        "st-chp8-p206-roomer-sent-neapolitan-paintings-to-low-countries": (True, "The source states that Roomer sent Neapolitan pictures to the Low Countries; the destination is the object endpoint and the picture group is recorded as a qualifier."),
        "st-chp8-p206-van-dyck-pictures-probably-acquired-locally": (True, "The source says the identified subject painting was probably acquired locally; attribution and probability remain qualified."),
        "st-chp8-p206-feast-of-herod-arrived-roomers-palace-c1640": (True, "The source reports that the Feast of Herod reached Roomer's possession around 1640; the unidentified palace remains a location qualifier."),
        "st-chp8-p206-feast-of-herod-depicts-daughter-of-herodias": (True, "The painting depicts an unnamed figure identified in the text as Herodias's daughter; this is image content, not a claim about a historical person's action."),
        "st-chp8-p206-feast-of-herod-depicts-girl-holding-john-baptist-head": (True, "The painting depicts an unnamed girl holding the severed head; she remains separate from the daughter of Herodias because the text does not equate them."),
        "st-chp8-p206-feast-of-herod-depicts-luxury-crowded-room-and-attendants": (False, "This is a visual description of the composition; the unnamed scene elements do not form a distinct typed entity endpoint."),
        "st-chp8-p206-feast-of-herod-made-impact-in-naples": (True, "Haskell explicitly reports the painting's impact in Naples, while leaving the viewers and reception evidence unspecified."),
        "st-chp8-p206-haskell-suggested-depicted-cruelty-appealed-to-roomer": (True, "This is Haskell's qualified inference that a feature of this specific painting appealed to Roomer, not a direct statement by the collector."),
        "st-chp8-p206-rubens-feast-of-herod-maturity-and-approximate-date": (True, "The painting is attributed to Rubens and dated approximately six years before its arrival; the attribution, maturity assessment, and date remain source-qualified."),
        "st-chp8-p206-herod-depicted-as-aware-of-injustice": (True, "Haskell interprets the depicted Herod as aware of injustice; the statement concerns a figure in the painting, not the historical person's mental state."),
        "st-chp8-p206-bassano-animal-pieces-qualified-authorial-inference": (True, "The source says the collection's almost-only old masters included eight animal pieces attributed to Bassano; the separate inference about Roomer's intellectual interests is recorded independently."),
    }
    if set(decisions) != UNSET_IDS | PRECLASSIFIED_IDS:
        raise SystemExit("review plan does not cover exactly the p.206 statement inventory")
    for statement_id, (relation, note) in decisions.items():
        update(statement_id, relation, note)

    # Correct endpoints and atomic predicates where the initial candidate pass conflated roles.
    update(
        "st-chp8-p206-roomer-acquired-pictures-by-three-painters", True,
        decisions["st-chp8-p206-roomer-acquired-pictures-by-three-painters"][1],
        object_id="cand-12029", predicate="collector_acquired_unidentified_pictures_by_three_named_painters",
        extra={"creator_candidate_ids": ["cand-7421", "cand-2792", "cand-1285"], "work_group_candidate_id": "cand-12029"},
    )
    update(
        "st-chp8-p206-roomer-quoted-inventory-request", True,
        decisions["st-chp8-p206-roomer-quoted-inventory-request"][1],
        object_id="cand-7426",
        claim="Roomer requested that foreign painters be summoned to draw up an inventory, especially Jan Vandeneynde of Brussels and others of his choice.",
        qualification="The speaker is Roomer as quoted by Haskell. The underlying document is unidentified and the requested inventory is not shown as completed.",
        extra={"source_document_candidate_id": "cand-7425", "requested_painter_group_candidate_id": "cand-7426", "speaker": "Gaspar Roomer, quoted by Haskell"},
    )
    update(
        "st-chp8-p206-roomer-owned-hundreds-by-flemish-artists", True,
        decisions["st-chp8-p206-roomer-owned-hundreds-by-flemish-artists"][1],
        object_id="cand-12030",
        predicate="roomer_owned_several_hundred_pictures_by_named_flemish_artists",
        extra={
            "work_group_candidate_id": "cand-12030",
            "creator_candidate_ids": ["cand-0453", "cand-2817", "cand-0449", "cand-0444", "cand-0957", "cand-1965", "cand-2415", "cand-2800", "cand-0917"],
            "work_quantity": "several hundred (approximate)",
        },
    )
    update(
        "st-chp8-p206-bassano-animal-pieces-qualified-authorial-inference", True,
        decisions["st-chp8-p206-bassano-animal-pieces-qualified-authorial-inference"][1],
        predicate="roomer_owned_eight_animal_pictures_attributed_to_bassano",
        claim="Haskell says almost the only old masters in Roomer's collection were eight animal pictures attributed to Bassano.",
        qualification="The source's separate inference that this may characterize Roomer's lack of intellectual interests is captured in a distinct non-relation statement. No titles are given, and which Bassano is meant remains unresolved.",
        extra={"creator_candidate_id": "cand-7428", "work_quantity": 8, "work_group_candidate_id": "cand-7436"},
    )
    update(
        "st-chp8-p206-haskell-compared-roman-painting-and-venetian-colour", False,
        decisions["st-chp8-p206-haskell-compared-roman-painting-and-venetian-colour"][1],
        predicate="haskell_described_clarity_and_serenity_as_missing_from_roman_painting",
        claim="Haskell says clarity and serenity were missing from what he describes as characteristic Roman painting of the time.",
        qualification="This is an authorial aesthetic characterization. The separate clause about classical discipline and Venetian colour is represented in a distinct statement.",
        object_id=None,
    )
    update(
        "st-chp8-p206-later-roomer-collection-less-documented", False,
        decisions["st-chp8-p206-later-roomer-collection-less-documented"][1],
        predicate="haskell_reported_less_information_about_later_collection",
        claim="Haskell says he had much less information about the nature of Roomer's later collection and had to rely on indirect sources.",
        qualification="This records Haskell's stated evidence limitation; it does not treat the indirect sources as inspected in this passage.",
        object_id="cand-7407",
    )
    update(
        "st-chp8-p206-roomer-sent-neapolitan-paintings-to-low-countries", True,
        decisions["st-chp8-p206-roomer-sent-neapolitan-paintings-to-low-countries"][1],
        object_id="cand-4342",
        extra={"destination_candidate_id": "cand-4342", "work_group_candidate_id": "cand-7432", "notable_artist_candidate_id": "cand-1854"},
    )
    update(
        "st-chp8-p206-feast-of-herod-arrived-roomers-palace-c1640", True,
        decisions["st-chp8-p206-feast-of-herod-arrived-roomers-palace-c1640"][1],
        predicate="feast_of_herod_reached_roomer_around_1640",
        claim="Haskell says Rubens's Feast of Herod, one of Roomer's most important pictures, reached his palace in about 1640.",
        extra={"owner_candidate_id": "cand-2223", "location_candidate_id": "cand-1816"},
    )
    update(
        "st-chp8-p206-feast-of-herod-depicts-daughter-of-herodias", True,
        decisions["st-chp8-p206-feast-of-herod-depicts-daughter-of-herodias"][1],
        subject="cand-4092", object_id="cand-7437",
        predicate="painting_depicts_daughter_of_herodias_preparing_to_stab_tongue",
    )
    update(
        "st-chp8-p206-feast-of-herod-depicts-girl-holding-john-baptist-head", True,
        decisions["st-chp8-p206-feast-of-herod-depicts-girl-holding-john-baptist-head"][1],
        subject="cand-4092", object_id="cand-7439",
        predicate="painting_depicts_girl_holding_john_baptist_head",
    )
    update(
        "st-chp8-p206-herod-depicted-as-aware-of-injustice", True,
        decisions["st-chp8-p206-herod-depicted-as-aware-of-injustice"][1],
        subject="cand-4092", object_id="cand-4165",
        predicate="painting_depicts_herod_as_anxiously_aware_of_injustice",
    )
    update(
        "st-chp8-p206-rubens-feast-of-herod-maturity-and-approximate-date", True,
        decisions["st-chp8-p206-rubens-feast-of-herod-maturity-and-approximate-date"][1],
        predicate="rubens_created_feast_of_herod_approximately_six_years_before_1640",
        subject="cand-4092", object_id="cand-2295",
        extra={"creator_candidate_id": "cand-2295", "approximate_creation_year": "c.1634"},
    )
    candidate_by_id["cand-2295"]["suggested_type"] = "person"
    candidate_by_id["cand-2295"]["detail"] = "The index subentry identifies Peter Paul Rubens as the painter of Feast of Herod; the work itself is cand-4092."

    added_statements = [
        {
            "statement_id": "st-chp8-p206-classical-discipline-imposed-clarity-on-venetian-colour",
            "subject_candidate_id": "cand-7431", "object_candidate_id": "cand-7430",
            "predicate": "classical_discipline_imposed_clarity_and_serenity_on_venetian_colour",
            "claim": "Haskell says classical discipline had imposed clarity and serenity on Venetian colour.",
            "qualification": "This is Haskell's art-historical interpretation; the concepts remain source-local candidates pending S3.",
            "quote": excerpt(37, 37, "which classical discipline", "Venetian colour."),
            "start_line": 37, "end_line": 37, "relation": True,
            "note": "The sentence's causal clause is distinct from the preceding description of qualities missing from Roman painting.",
            "mentioned": ["cand-7431", "cand-7430"],
        },
        {
            "statement_id": "st-chp8-p206-haskell-inferred-roomers-lack-of-intellectual-interests-from-bassano-pieces",
            "subject_candidate_id": "cand-2223", "object_candidate_id": None,
            "predicate": "haskell_qualified_roomers_collection_as_evidence_of_limited_intellectual_interests",
            "claim": "Haskell tentatively suggests that the limited range of old masters in Roomer's collection may characterize his lack of intellectual interests.",
            "qualification": "The source explicitly says 'perhaps'; this is an authorial interpretation, not an independently established psychological fact.",
            "quote": excerpt(37, 37, "It is perhaps characteristic", "lack of intellectual interests"),
            "start_line": 37, "end_line": 37, "relation": False,
            "note": "This qualified authorial inference is preserved as a claim, not as an entity-to-entity relation.",
            "mentioned": ["cand-2223", "cand-7436"],
        },
        {
            "statement_id": "st-chp8-p206-roomer-continued-buying-hundreds-of-pictures",
            "subject_candidate_id": "cand-2223", "object_candidate_id": "cand-12031",
            "predicate": "roomer_continued_buying_hundreds_of_pictures_after_early_gallery",
            "claim": "Haskell says Roomer continued buying hundreds of pictures after his early Naples gallery.",
            "qualification": "The number is approximate and the individual pictures and their nature are not identified.",
            "quote": excerpt(38, 38, "he went on buying hundreds of pictures", "he went on buying hundreds of pictures"),
            "start_line": 38, "end_line": 38, "relation": True,
            "note": "The ongoing purchase is a distinct claim from Haskell's statement that the later collection is less documented.",
            "mentioned": ["cand-2223", "cand-12031"],
        },
        {
            "statement_id": "st-chp8-p206-roomer-pictures-by-foreign-artists",
            "subject_candidate_id": "cand-7427", "object_candidate_id": "cand-7426",
            "predicate": "roomer_said_most_preferred_pictures_were_by_foreign_artists",
            "claim": "Roomer said most of the pictures he particularly praised were by foreign artists.",
            "qualification": "The referent of 'these' is the subject-category pictures just described; no individual works or complete artist list is given.",
            "quote": excerpt(33, 34, "as all the pictures are very sine", "most of them are by foreign artists"),
            "start_line": 33, "end_line": 34, "relation": True,
            "note": "The quoted statement connects the source-defined picture group to an open group of foreign makers.",
            "mentioned": ["cand-7427", "cand-7426"],
            "extra": {"speaker": "Gaspar Roomer, quoted by Haskell"},
        },
        {
            "statement_id": "st-chp8-p206-foreign-artists-unfamiliar-to-neapolitan-painters",
            "subject_candidate_id": "cand-7426", "object_candidate_id": "cand-7424",
            "predicate": "foreign_artists_unfamiliar_to_neapolitan_painters",
            "claim": "Roomer's quoted statement describes the foreign artists as unfamiliar to Neapolitan painters.",
            "qualification": "The grammatical referent is the foreign artists; the painter groups are unenumerated and their exact membership remains open.",
            "quote": excerpt(33, 34, "unfamiliar to Neapolitan painters", "unfamiliar to Neapolitan painters"),
            "start_line": 33, "end_line": 34, "relation": True,
            "note": "The source explicitly describes a knowledge relation between two broad, unnamed painter groups.",
            "mentioned": ["cand-7426", "cand-7424"],
            "extra": {"speaker": "Gaspar Roomer, quoted by Haskell"},
        },
    ]
    for spec in added_statements:
        line_start, line_end = spec["start_line"], spec["end_line"]
        if normalize(spec["quote"]) not in normalize("\n".join(source_lines[line_start - 1:line_end])):
            raise SystemExit(f"new statement quote does not match source: {spec['statement_id']}")
        q = {
            "source_line_start": line_start, "source_line_end": line_end,
            "printed_page": 206, "pdf_physical_page": 4,
            "claim": spec["claim"], "speaker": "Haskell", "text_layer": "body",
            "qualification": spec["qualification"],
            "mentioned_candidate_ids": spec["mentioned"],
            "relation_candidate": spec["relation"],
            "relation_candidate_note": spec["note"],
        }
        if spec.get("extra"):
            q.update(spec["extra"])
        row = {
            "statement_id": spec["statement_id"], "segment_id": SEGMENT_ID,
            "subject_candidate_id": spec["subject_candidate_id"],
            "object_candidate_id": spec["object_candidate_id"],
            "predicate": spec["predicate"], "qualifiers": q,
            "original_quote": spec["quote"], "origin": "book", "source_file": SOURCE_REL,
        }
        by_id[row["statement_id"]] = row
    statements = list(by_id.values())

    for row in statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        q = row.get("qualifiers") or {}
        if "relation_candidate" not in q:
            raise SystemExit(f"p.206 statement remains unset: {row['statement_id']}")
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])):
            if candidate_id and candidate_id not in candidate_by_id:
                raise SystemExit(f"p.206 statement has unresolved candidate: {row['statement_id']} -> {candidate_id}")
        if q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"true p.206 relation candidate has an unexplained open endpoint: {row['statement_id']}")

    expected_counts = {"statements": 14229, "candidates": 12009, "mentions": 28072, "true": 8914, "false": 3464, "unset": 1851}
    actual_counts = {
        "statements": len(statements), "candidates": len(candidates), "mentions": len(mentions),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements),
        "unset": sum("relation_candidate" not in (row.get("qualifiers") or {}) for row in statements),
    }
    if actual_counts != expected_counts:
        raise SystemExit(f"unexpected post-write counts: {actual_counts}")

    outputs = {
        STATEMENTS: jsonl_bytes(statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions),
    }
    result = {
        "mode": "apply" if args.apply else "dry_run",
        "segment_id": SEGMENT_ID,
        "unclassified_statement_rows_reviewed": len(UNSET_IDS),
        "preclassified_statement_rows_rechecked": len(PRECLASSIFIED_IDS),
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [row[0] for row in MENTION_SPECS],
        "corrected_candidate_type": {"cand-2295": "work -> person"},
        "corrected_existing_mention": {"m-chp8-p206-037": "cand-7407 -> cand-12031"},
        "post_counts": actual_counts,
        "input_sha256": {path.name: hashes[path] for path in EXPECTED_HASHES},
        "output_sha256": {path.name: sha(data) for path, data in outputs.items()},
        "recovery_copies": [path.name + BACKUP_SUFFIX for path in (STATEMENTS, CANDIDATES, MENTIONS)],
    }
    if args.apply:
        for path in (STATEMENTS, CANDIDATES, MENTIONS):
            backups[path].write_bytes(raw[path])
        for path, data in outputs.items():
            atomic_write(path, data)
        actual_hashes = {path: sha(path.read_bytes()) for path in outputs}
        expected_hashes = {path: sha(data) for path, data in outputs.items()}
        if actual_hashes != expected_hashes:
            raise SystemExit("post-write hash verification failed")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("applied; recovery copies written and post-write hashes verified" if args.apply else "dry-run only; no files changed")


if __name__ == "__main__":
    main()
