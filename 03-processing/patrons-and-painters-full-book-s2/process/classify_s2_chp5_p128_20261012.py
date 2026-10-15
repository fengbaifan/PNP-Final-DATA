from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


BASE = Path(__file__).resolve().parents[3]
TABLES = BASE / "04-knowledge" / "tables"
PROCESS = BASE / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = BASE / "02-sources" / "02-Markdown" / "05_CHP-5_sec_i.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l85-97"
EXPECTED = {
    STATEMENTS.name: "6f4042b9b027e6edea62a4e1ba58b9be112ca726eb2b177ecbc6a6651f1ee3a0",
    CANDIDATES.name: "714c522c6c846612167ef934d16bba0eb2bdd9aadcd091322228cc778b154bba",
    MENTIONS.name: "6daa57037f79fb3eca85207b04091c710928d183f68dfc63afd4fb3fefd4b899",
    SOURCE.name: "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def load_segment() -> tuple[str, dict]:
    source_hash = sha(SOURCE)
    if source_hash != EXPECTED[SOURCE.name]:
        raise SystemExit(f"source hash changed: {source_hash}")
    segment = next(row for row in jsonl_rows(SEGMENTS) if row["segment_id"] == SEGMENT_ID)
    if segment["asset_sha256"] != source_hash:
        raise SystemExit("segment source asset hash does not match the Markdown source")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != segment["sha256"]:
        raise SystemExit("segment slice hash mismatch")
    return text, segment


def quote(text: str, exact: str) -> str:
    if exact not in text:
        raise SystemExit(f"quote not found in source segment: {exact!r}")
    return exact


def make_qualifiers(
    *,
    start: int,
    end: int,
    claim: str,
    candidates: list[str],
    relation: bool,
    qualification: str,
    speaker: str = "Haskell",
    text_layer: str = "authorial narrative",
) -> dict:
    return {
        "source_line_start": start,
        "source_line_end": end,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidates,
        "pdf_physical_page": 9,
        "printed_page_locator": "p.128",
        "relation_candidate": relation,
        "relation_candidate_note": (
            "Source-grounded S2 relation candidate only; no S6 formal edge is created."
            if relation
            else "Retained as a source claim, but not a candidate for a formal entity relation."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write tables after all preflight checks pass")
    args = parser.parse_args()

    for path in (STATEMENTS, CANDIDATES, MENTIONS):
        actual = sha(path)
        if actual != EXPECTED[path.name]:
            raise SystemExit(f"{path.name} hash changed: {actual}")

    text, segment = load_segment()
    statements = jsonl_rows(STATEMENTS)
    candidates = list(csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline="")))
    mentions = list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))
    p128 = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    if len(p128) != 26:
        raise SystemExit(f"expected 26 existing p.128 statements, found {len(p128)}")
    if sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in p128) != 24:
        raise SystemExit("p.128 classification state changed")

    candidate_ids = {row["candidate_id"] for row in candidates}
    if max(int(value[5:]) for value in candidate_ids if value.startswith("cand-") and value[5:].isdigit()) != 11767:
        raise SystemExit("candidate sequence changed; review IDs before applying")
    if any(f"cand-{number:04d}" in candidate_ids for number in range(11768, 11781)):
        raise SystemExit("one or more planned candidate IDs already exist")

    candidate_specs = [
        ("cand-11768", "S. Giovanni Decollato exhibition held in the Holy Year 1675 (Medici display)", "event", "L88", "Specific 1675 occurrence in the S. Giovanni Decollato series cand-6039; distinct from the 1662 and 1668 instances cand-11766 and cand-11767."),
        ("cand-11769", "S. Giovanni Decollato exhibition of 1736", "event", "L90", "Specific exhibition in the S. Giovanni Decollato series cand-6039; 212 pictures and an issued catalogue are reported, while a papal bid is only hoped for."),
        ("cand-11770", "S. Salvatore in Lauro exhibition in the Holy Year 1675", "event", "L94", "Specific occurrence of the recurring S. Salvatore exhibition cand-6051; the reported comparison with other Roman exhibitions is evaluative."),
        ("cand-11771", "S. Salvatore in Lauro exhibition in 1697", "event", "L97", "Specific 1697 occurrence of the recurring S. Salvatore exhibition cand-6051; Pio's loan and other lenders' display are described here."),
        ("cand-11772", "Pictures shown at the S. Giovanni Decollato exhibition in 1675 (unnamed group)", "work", "L88", "The source reports over two hundred pictures and names artists whose works were included; no individual works are identified."),
        ("cand-11773", "Tapestries and damasks hung outside S. Giovanni Decollato in 1675 (unnamed group)", "work", "L88", "Textiles used as stage scenery outside the church; individual objects and makers are not identified."),
        ("cand-11774", "Room opening onto the cloisters of S. Giovanni Decollato (unnamed room)", "place", "L88", "The source identifies one room opening onto the cloisters but supplies no architectural name."),
        ("cand-11775", "Pictures lent by Prince Pio for the 1697 S. Salvatore exhibition (unnamed group)", "work", "L97", "The source says Pio lent his pictures and that they included Venetian old masters; titles and makers are not identified."),
        ("cand-11776", "Further pictures displayed for other collectors in 1697 (unnamed group)", "work", "L97", "Additional unnamed pictures hung separately in the upper gallery; the source does not identify individual works or collectors."),
        ("cand-11777", "Families from the Marche who lent for S. Salvatore exhibitions (unnamed group)", "term", "L94", "The source says lenders were often families from the Marche; no family or member is identified."),
        ("cand-11778", "Other collectors seeking to display at the 1697 S. Salvatore exhibition (unnamed group)", "term", "L97", "The source refers to unnamed other collectors who wanted to display their pictures; no individual collector is identified."),
        ("cand-11779", "Preacher from St Peter's at the 1697 S. Salvatore ceremony (unnamed person)", "person", "L97", "The sermon is attributed to an unnamed preacher associated with St Peter's; the source supplies no personal identity."),
        ("cand-11780", "Cardinals assembled at the 1697 S. Salvatore ceremony (unnamed group)", "term", "L97", "The source reports an assembly of cardinals but names no attendees."),
    ]
    new_candidates = [
        {
            "candidate_id": candidate_id,
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
            "candidate_source_ref": f"{SEGMENT_ID}#{line}",
        }
        for candidate_id, name, kind, line, detail in candidate_specs
    ]

    mention_updates = {
        "m-chp5-p128-0011": ("cand-11768", "Specific 1675 S. Giovanni Decollato occurrence; series cand-6039 remains separate."),
        "m-chp5-p128-0019": ("cand-11769", "Specific 1736 S. Giovanni Decollato occurrence, distinct from the recurring series."),
        "m-chp5-p128-0033": ("cand-11770", "Specific Holy Year 1675 occurrence, distinct from the recurring series cand-6051."),
        "m-chp5-p128-0048": ("cand-11771", "Specific 1697 S. Salvatore in Lauro occurrence, distinct from the recurring series cand-6051."),
    }
    mention_specs = [
        ("m-chp5-p128-0054", "cand-11772", "over two hundred pictures", "L88", "Count-bearing mention of the unnamed works shown at this exhibition."),
        ("m-chp5-p128-0055", "cand-11773", "tapestries and damasks", "L88", "Unnamed textile works hung outside the church."),
        ("m-chp5-p128-0056", "cand-11774", "one of the rooms opening on to them", "L88", "Unnamed room opening onto the cloisters; 'them' refers to the cloisters."),
        ("m-chp5-p128-0057", "cand-11772", "works by living and dead artists", "L88", "The source's description of the unnamed exhibition works; artists are examples, not identified work titles."),
        ("m-chp5-p128-0058", "cand-11775", "his pictures", "L97", "Anaphoric reference to the pictures Prince Pio agreed to lend."),
        ("m-chp5-p128-0059", "cand-11776", "further pictures", "L97", "Additional works displayed for other collectors, distinct from Pio's pictures."),
        ("m-chp5-p128-0060", "cand-11777", "families from the Marche", "L94", "Unnamed lender families; the source does not provide individual family identities."),
        ("m-chp5-p128-0061", "cand-11778", "other collectors", "L97", "Unnamed collectors who wanted to display their treasures in 1697."),
        ("m-chp5-p128-0062", "cand-11779", "the preacher of St Peter’s", "L97", "Unnamed preacher associated with St Peter's; St Peter's is not the exhibition venue."),
        ("m-chp5-p128-0063", "cand-11780", "a great assembly of cardinals", "L97", "Collective reference to unnamed cardinals gathered at the ceremony."),
    ]
    existing_mention_ids = {row["mention_id"] for row in mentions}
    if any(spec[0] in existing_mention_ids for spec in mention_specs):
        raise SystemExit("one or more planned mention IDs already exist")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    for mention_id, (candidate_id, note) in mention_updates.items():
        if mention_id not in mention_by_id:
            raise SystemExit(f"expected mention missing: {mention_id}")
        mention_by_id[mention_id]["candidate_id"] = candidate_id
        mention_by_id[mention_id]["note"] = note
    new_mentions = []
    for mention_id, candidate_id, surface, line, note in mention_specs:
        start = text.find(surface)
        if start < 0 or text.find(surface, start + 1) >= 0:
            raise SystemExit(f"mention surface is missing or ambiguous: {surface!r}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })

    statement_by_id = {row["statement_id"]: row for row in statements}
    updates = {
        "st-chp5-p128-1675-salvatore-reputation": {
            "subject": "cand-11770", "object": None, "predicate": "reported_comparison_with_roman_exhibitions", "relation": False,
            "claim": "The 1675 S. Salvatore exhibition was said to equal any exhibition held in Rome.", "lines": (93, 94),
            "qualification": "Reported comparison with an unnamed source of the judgment; not an objective equivalence claim.", "candidates": ["cand-11770", "cand-4490"],
            "quote": "the one at S. Salvatore in Lauro was said to equal any held in Rome.",
        },
        "st-chp5-p128-1697-social-ceremony": {
            "subject": "cand-11771", "object": None, "predicate": "social_ceremony_with_sermon_and_cardinal_assembly", "relation": False,
            "claim": "The 1697 occasion became a social ceremony with a sermon from a preacher of St Peter's and an assembly of cardinals.", "lines": (97, 97),
            "qualification": "Contextual description. St Peter's identifies the preacher's association, not the exhibition venue; the cardinals are an unnamed group.", "candidates": ["cand-11771", "cand-5696"],
            "quote": "The occasion turned into a brilliant social ceremony",
        },
        "st-chp5-p128-1708-ruspoli-opening": {
            "subject": "cand-2311", "object": None, "predicate": "incomplete_transition_to_1708_exhibition_account", "relation": False,
            "claim": "The author introduces a similar situation in 1708 involving Marchese Ruspoli, but the clause is incomplete at the page break.", "lines": (97, 97),
            "qualification": "Narrative bridge only. The account continues in p.129 L100 and is represented by st-chp5-p129-1708-ruspoli-condition-and-concession; do not treat this fragment as a second complete relation.", "candidates": ["cand-2311", "cand-6051"],
            "quote": "We find a similar situation in 1708 when the Marchese Ruspoli at first",
        },
        "st-chp5-p128-1736-catalogue": {
            "subject": "cand-11769", "object": "cand-6062", "predicate": "catalogue_issued_for_exhibition", "relation": True,
            "claim": "A catalogue was issued for the 1736 S. Giovanni Decollato exhibition.", "lines": (90, 90),
            "qualification": "The source says a catalogue was issued but does not identify its title or author.", "candidates": ["cand-11769", "cand-6062"],
            "quote": "a catalogue was issued",
        },
        "st-chp5-p128-1736-exhibition-count": {
            "subject": "cand-11769", "object": None, "predicate": "212_old_and_modern_pictures_exhibited", "relation": False,
            "claim": "The 1736 exhibition included 212 pictures described as old and modern.", "lines": (90, 90),
            "qualification": "Count and category are scalar properties; the individual works are not identified.", "candidates": ["cand-11769", "cand-6039"],
            "quote": "Thus 212 pictures, old and modern, were exhibited in 1736",
        },
        "st-chp5-p128-1736-pope-bid-hope": {
            "subject": "cand-11769", "object": None, "predicate": "reported_hope_of_papal_bid", "relation": False,
            "claim": "There were hopes that the Pope would make a bid at the 1736 exhibition.", "lines": (90, 90),
            "qualification": "Prospective hope only; the source does not say that the Pope made or placed a bid and does not identify him personally.", "candidates": ["cand-11769"],
            "quote": "there were hopes that the Pope would make a bid.",
        },
        "st-chp5-p128-additional-loans-upper-gallery": {
            "subject": "cand-11776", "object": "cand-6061", "predicate": "displayed_separately_in_upper_gallery", "relation": True,
            "claim": "Further pictures for other collectors were hung separately in the upper gallery of the cloisters in 1697.", "lines": (97, 97),
            "qualification": "The picture group and collectors remain unnamed; this display is separate from Prince Pio's pictures in the loggia.", "candidates": ["cand-11776", "cand-6061", "cand-6053", "cand-11771"],
            "quote": "further pictures were hung separately in the upper gallery of the cloisters.",
        },
        "st-chp5-p128-anniversary-celebrations": {
            "subject": "cand-6054", "object": "cand-6055", "predicate": "celebrated_anniversary_of_arrival", "relation": True,
            "claim": "Members of the Marchigian colony celebrated the anniversary of the reported arrival of the Holy House in Loreto on 10 December.", "lines": (93, 93),
            "qualification": "The source describes the devotional tradition and celebrations; concerts and a picture exhibition are listed as components, not independently identified events.", "candidates": ["cand-6054", "cand-6055", "cand-6056", "cand-6057", "cand-6051"],
            "quote": "Soon afterwards the members of this group began to celebrate the anniversary of the arrival of the Holy House in Loreto on 10 December with elaborate celebrations which included concerts and a picture exhibition.",
        },
        "st-chp5-p128-azzolini-purchased-church": {
            "subject": "cand-0153", "object": "cand-6052", "predicate": "bought_church_for_marchigian_colony", "relation": True,
            "claim": "Cardinal Azzolini bought the church of S. Salvatore in Lauro for the Marchigian colony in Rome in 1669.", "lines": (92, 93),
            "qualification": "The source gives the purchase purpose and year; this claim does not identify the colony's members.", "candidates": ["cand-0153", "cand-6052", "cand-6054"],
            "quote": "a church that was bought for the Marchigian colony in Rome by Cardinal\nAzzolini in 1669.",
        },
        "st-chp5-p128-display-conditions": {
            "subject": "cand-6051", "object": None, "predicate": "lighting_and_public_criticism_considered", "relation": False,
            "claim": "Adequate lighting was arranged and public criticism was taken into account while paintings remained on view on 10 and 11 December.", "lines": (95, 95),
            "qualification": "Operational and display conditions for the recurring exhibition; no individual lighting system or critic is identified.", "candidates": ["cand-6051"],
            "quote": "during which days the paintings remained on view; adequate lighting had to be arranged and criticisms of the public taken into account.",
        },
        "st-chp5-p128-exhibitions-commercial": {
            "subject": "cand-6039", "object": None, "predicate": "reported_later_commercial_tendency", "relation": False,
            "claim": "Haskell says later exhibitions seem to have become more commercial as patrician families became more interested in selling than displaying their pictures.", "lines": (89, 89),
            "qualification": "Authorial trend assessment, explicitly qualified by 'seem'; the families are unnamed and no individual sale is specified.", "candidates": ["cand-6039"],
            "quote": "In later years when the great patrician families were more interested in selling than in displaying their pictures, the exhibitions seem to have become far more commercial.",
        },
        "st-chp5-p128-ghezzi-appointment": {
            "subject": "cand-1157", "object": "cand-6051", "predicate": "managed_exhibition_arrangements_from_1682", "relation": True,
            "claim": "Giuseppe Ghezzi was in charge of arrangements for the S. Salvatore exhibition from 1682.", "lines": (94, 95),
            "qualification": "The source describes the recurring exhibition series. Ghezzi's secretary role and origin are recorded separately; his full identity remains for S3 alignment.", "candidates": ["cand-1157", "cand-6051"],
            "quote": "As from 1682 the painter Giuseppe\nGhezzi, life secretary of the Accademia di S. Luca and himself from Ascoli Piceno, was in charge of the arrangements",
        },
        "st-chp5-p128-ghezzi-recommended-scale": {
            "subject": "cand-1157", "object": "cand-6051", "predicate": "recommended_ideal_exhibition_scale_with_yearly_variation", "relation": False,
            "claim": "Ghezzi recommended five or six large canvases and about 200 smaller pictures as an ideal, while actual numbers varied by year.", "lines": (95, 95),
            "qualification": "A recommendation and scalar annual variation, not a relation between independently identified entities.", "candidates": ["cand-1157", "cand-6051"],
            "quote": "Ghezzi recommended five or six large canvases and about 200 smaller ones as the ideal to be aimed at, but numbers obviously varied from year to year.",
        },
        "st-chp5-p128-lending-and-security": {
            "subject": "cand-6051", "object": None, "predicate": "lending_transport_and_security_procedures", "relation": False,
            "claim": "Lenders were approached in advance, porters were hired for transport, and soldiers guarded the paintings for 24 hours on 10 and 11 December.", "lines": (95, 95),
            "qualification": "A set of operating procedures; the source names no individual lenders, porters, or soldiers and does not identify the paintings.", "candidates": ["cand-6051", "cand-6054", "cand-6058"],
            "quote": "Families prepared to lend had to be approached in good time; reliable porters had to be hired for the transport and soldiers employed on 24-hour guard duty over the 10 and 11 December",
        },
        "st-chp5-p128-madonna-pride-and-variety": {
            "subject": "cand-6051", "object": None, "predicate": "madonna_representation_given_pride_of_place_and_varied_paintings_included", "relation": False,
            "claim": "A representation of the Madonna was always given pride of place, and the exhibition included every kind of painting.", "lines": (95, 95),
            "qualification": "Display convention and category breadth. The source names no specific Madonna painting; cand-3427 is the represented subject, not an exhibited person or identified work.", "candidates": ["cand-6051", "cand-3427"],
            "quote": "Pride of place was always given to a representation of the Madonna, but every kind of painting was included in the exhibition.",
        },
        "st-chp5-p128-medici-1675-exhibition": {
            "subject": "cand-5179", "object": "cand-11768", "predicate": "showed_pictures_at_exhibition", "relation": True,
            "claim": "The Medici showed pictures at the S. Giovanni Decollato exhibition arranged for the Holy Year of 1675.", "lines": (88, 88),
            "qualification": "The source reports over two hundred pictures; that count is recorded separately. 'The Medici' is a collective family reference and no individual lender is named.", "candidates": ["cand-5179", "cand-11768", "cand-6039", "cand-11772", "cand-11481"],
            "quote": "Another lavish exhibition was arranged for the Holy Year of 1675 when over two hundred pictures were shown by the Medici.",
        },
        "st-chp5-p128-medici-interior-display": {
            "subject": "cand-11772", "object": "cand-6041", "predicate": "displayed_in_cloisters", "relation": True,
            "claim": "Works by living and dead artists, including Raphael, Titian, and the Carracci, were displayed in the cloisters at the 1675 S. Giovanni Decollato exhibition.", "lines": (88, 88),
            "qualification": "The works are unidentified. Artist names are metonymic examples; the Carracci reference remains unresolved and is not narrowed to Annibale.", "candidates": ["cand-11772", "cand-11768", "cand-6041", "cand-2098", "cand-2630", "cand-0576"],
            "quote": "while inside the cloisters and in one of the rooms opening on to them were works by living and dead artists including Raphael, Titian and the Carracci.",
        },
        "st-chp5-p128-medici-outdoor-stage-setting": {
            "subject": "cand-11773", "object": "cand-6040", "predicate": "hung_outside_church", "relation": True,
            "claim": "Tapestries and damasks were hung outside the church for the 1675 exhibition.", "lines": (88, 88),
            "qualification": "The source says the textiles created the illusion of stage scenery as the public walked among them; their makers and identities are unknown.", "candidates": ["cand-11773", "cand-11768", "cand-6040"],
            "quote": "Outside the church were hung tapestries and damasks giving the illusion of stage scenery as the public walked among them;",
        },
        "st-chp5-p128-pio-exclusive-loan": {
            "subject": "cand-11775", "object": "cand-1934", "predicate": "lent_by_under_exclusive_display_condition", "relation": True,
            "claim": "Prince Pio lent his pictures for the 1697 exhibition at his own expense on condition that only his pictures were shown.", "lines": (97, 97),
            "qualification": "The pictures are an unnamed group; the index lead does not establish Prince Pio's full identity. Preserve the exclusive display condition and expense stated in the source.", "candidates": ["cand-11775", "cand-1934", "cand-11771", "cand-6051"],
            "quote": "Thus in 1697 Prince Pio agreed to lend his pictures entirely at his own expense—on condition that his alone were shown.",
        },
        "st-chp5-p128-pio-works-loggia": {
            "subject": "cand-11775", "object": "cand-6060", "predicate": "displayed_together_under_loggia_arcades", "relation": True,
            "claim": "Prince Pio's loaned pictures, including a number of Venetian old masters, were hung together under the loggia arcades in 1697.", "lines": (97, 97),
            "qualification": "The pictures remain an unnamed group; 'Venetian old masters' is not treated as a named work or a resolved maker list.", "candidates": ["cand-11775", "cand-6060", "cand-4288", "cand-11771"],
            "quote": "They included a number of Venetian old masters and were all hung together under the arcades of the loggia.",
        },
        "st-chp5-p128-prestige-rivalries": {
            "subject": "cand-6051", "object": None, "predicate": "reported_prestige_and_rivalries_among_owners", "relation": False,
            "claim": "Haskell describes prestige attached to creating a striking effect and rivalries among owners as a broader Roman tendency.", "lines": (96, 96),
            "qualification": "Authorial social interpretation; the owners are not individually identified and no particular act of rivalry is stated.", "candidates": ["cand-6051", "cand-4490"],
            "quote": "Quite soon considerable prestige attached to creating a striking effect, and—as so often in Rome—rivalries between the various owners came powerfully to the fore.",
        },
        "st-chp5-p128-salvatore-exhibition-purpose": {
            "subject": "cand-11770", "object": "cand-6052", "predicate": "intended_to_decorate_church", "relation": True,
            "claim": "The purpose of the 1675 S. Salvatore exhibition included decorating the church.", "lines": (94, 94),
            "qualification": "Haskell contrasts this purpose with publicity for painters and says lenders, often families from the Marche, were to be glorified; this is not a claim that the purpose was exclusive.", "candidates": ["cand-11770", "cand-6052", "cand-6058", "cand-6051"],
            "quote": "the intention was to decorate the church",
        },
        "st-chp5-p128-salvatore-professional-organization": {
            "subject": "cand-6051", "object": None, "predicate": "comparatively_professional_organization", "relation": False,
            "claim": "Haskell assesses the S. Salvatore exhibitions as more professionally organized than the others.", "lines": (94, 94),
            "qualification": "Comparative evaluation of organization, not an entity relation.", "candidates": ["cand-6051"],
            "quote": "Despite this, the exhibitions in S. Salvatore in Lauro were organised far more professionally than any of the others.",
        },
        "st-chp5-p128-salvatore-series-venue": {
            "subject": "cand-6051", "object": "cand-6053", "predicate": "held_in_cloisters", "relation": True,
            "claim": "The regular S. Salvatore in Lauro exhibition was held in the church's cloisters.", "lines": (91, 92),
            "qualification": "The source says the series began later than exhibitions considered earlier; that relative start is contextual rather than a separate event date.", "candidates": ["cand-6051", "cand-6053", "cand-6052"],
            "quote": "This was held in the beautiful cloisters of S. Salvatore in\nLauro",
        },
    }

    updated_ids = set(updates)
    if updated_ids - set(statement_by_id):
        raise SystemExit(f"statement IDs missing: {sorted(updated_ids - set(statement_by_id))}")
    for statement_id, spec in updates.items():
        row = statement_by_id[statement_id]
        row["subject_candidate_id"] = spec["subject"]
        row["object_candidate_id"] = spec["object"]
        row["predicate"] = spec["predicate"]
        row["original_quote"] = quote(text, spec["quote"])
        row["qualifiers"].update(make_qualifiers(
            start=spec["lines"][0], end=spec["lines"][1], claim=spec["claim"],
            candidates=spec["candidates"], relation=spec["relation"], qualification=spec["qualification"],
            text_layer="authorial narrative with reported speech" if "said" in spec["claim"] or "hopes" in spec["claim"] else "authorial narrative",
        ))

    added_specs = [
        ("st-chp5-p128-sgj-1675-instance-of-series", "cand-11768", "cand-6039", "instance_of_annual_exhibition_series", 88, "Another lavish exhibition was arranged for the Holy Year of 1675", "This specific 1675 occurrence belongs to the S. Giovanni Decollato annual series discussed on p.127; the link is contextual and the named series remains distinct from the event instance.", ["cand-11768", "cand-6039"]),
        ("st-chp5-p128-sgj-1736-instance-of-series", "cand-11769", "cand-6039", "instance_of_annual_exhibition_series", 90, "Thus 212 pictures, old and modern, were exhibited in 1736", "The preceding sentence continues the same S. Giovanni Decollato exhibition account; this event instance is distinct from the series.", ["cand-11769", "cand-6039"]),
        ("st-chp5-p128-salvatore-1675-instance-of-series", "cand-11770", "cand-6051", "instance_of_regular_exhibition_series", 94, "the one at S. Salvatore in Lauro", "The phrase identifies the specific Holy Year 1675 occurrence within the regular S. Salvatore exhibition series.", ["cand-11770", "cand-6051", "cand-11481"]),
        ("st-chp5-p128-salvatore-1697-instance-of-series", "cand-11771", "cand-6051", "instance_of_regular_exhibition_series", 97, "Thus in 1697 Prince Pio agreed to lend his pictures", "The 1697 episode is narrated within the account of the recurring S. Salvatore exhibition series.", ["cand-11771", "cand-6051", "cand-1934"]),
        ("st-chp5-p128-medici-pictures-displayed", "cand-11772", "cand-11768", "displayed_at", 88, "over two hundred pictures were shown by the Medici", "The pictured works are an unnamed group. Artist references in the next clause are metonymic and do not identify individual works.", ["cand-11772", "cand-11768", "cand-5179"]),
        ("st-chp5-p128-medici-1675-picture-count", "cand-11772", None, "count_over_200_pictures", 88, "over two hundred pictures", "A scalar count only; the source does not list the individual works.", ["cand-11772", "cand-11768"]),
        ("st-chp5-p128-medici-room-display", "cand-11772", "cand-11774", "displayed_in_room_opening_onto_cloisters", 88, "in one of the rooms opening on to them were works by living and dead artists", "The room is unnamed and distinct from the cloisters themselves; the works are not individually identified.", ["cand-11772", "cand-11774", "cand-6041", "cand-11768"]),
        ("st-chp5-p128-medici-textiles-displayed", "cand-11773", "cand-6040", "hung_outside_church", 88, "Outside the church were hung tapestries and damasks", "The textiles are an unnamed work group; the source says they created a stage-like setting for visitors.", ["cand-11773", "cand-6040", "cand-11768"]),
        ("st-chp5-p128-ghezzi-life-secretary", "cand-1157", "cand-0007", "life_secretary_of", 95, "Ghezzi, life secretary of the Accademia di S. Luca", "The source states this office. cand-0007 is the index lead; duplicate index candidates cand-0008 and cand-0009 remain for S3 identity alignment.", ["cand-1157", "cand-0007"]),
        ("st-chp5-p128-ghezzi-origin", "cand-1157", "cand-6059", "originated_from", 95, "and himself from Ascoli Piceno", "Source-stated origin only; no birth date or additional biography is inferred.", ["cand-1157", "cand-6059"]),
        ("st-chp5-p128-ghezzi-perfect-arrangements", "cand-1157", None, "author_assesses_effort_to_perfect_arrangements", 95, "he went to great trouble to perfect them", "Authorial assessment of effort; 'them' refers to the exhibition arrangements and does not name an independent entity.", ["cand-1157", "cand-6051"]),
        ("st-chp5-p128-salvatore-lenders-glorified", "cand-11770", "cand-11777", "intended_to_glorify_lenders", 94, "glorify the lenders—often families from the Marche", "Haskell identifies the lenders as often coming from the Marche but supplies no family names; preserve the source's qualification 'often'.", ["cand-11770", "cand-11777", "cand-6058", "cand-6051"]),
        ("st-chp5-p128-other-collectors-display-intent", "cand-11778", "cand-11771", "wanted_to_display_treasures_at_exhibition", 97, "other collectors who also wanted to display their treasures", "Unnamed collectors are represented as a group; the next clause reports that further pictures were hung to satisfy them.", ["cand-11778", "cand-11771", "cand-11776"]),
        ("st-chp5-p128-preacher-sermon", "cand-11779", "cand-11771", "preached_sermon_at_ceremony", 97, "a sermon from the preacher of St Peter’s", "The preacher is unnamed; St Peter's identifies association, not the event's location.", ["cand-11779", "cand-11771", "cand-5696"]),
        ("st-chp5-p128-cardinals-assembly", "cand-11780", "cand-11771", "assembled_at_ceremony", 97, "a great assembly of cardinals", "The source reports a group gathering but names no individual cardinal.", ["cand-11780", "cand-11771"]),
    ]
    new_statements = []
    for statement_id, subject, obj, predicate, line, exact_quote, qualification, ids in added_specs:
        if statement_id in statement_by_id:
            raise SystemExit(f"new statement already exists: {statement_id}")
        new_statements.append({
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": make_qualifiers(
                start=line, end=line, claim=exact_quote.rstrip("."), candidates=ids,
                relation=obj is not None, qualification=qualification,
            ),
            "original_quote": quote(text, exact_quote),
            "origin": "book",
            "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        })

    existing_ids = set(statement_by_id)
    if any(row["statement_id"] in existing_ids for row in new_statements):
        raise SystemExit("new statement ID collision")
    existing_candidate_ids = {row["candidate_id"] for row in candidates}
    if any(row["candidate_id"] in existing_candidate_ids for row in new_candidates):
        raise SystemExit("new candidate ID collision")

    # Keep all existing quote spans exact and verify the new mention anchors against the source slice.
    for mention in new_mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if text[start:end] != mention["surface_form"]:
            raise SystemExit(f"mention offset mismatch: {mention['mention_id']}")

    # Build a minimal preview from the target segment before any file is written.
    classifications = {row["statement_id"]: row["qualifiers"].get("relation_candidate") for row in p128}
    for statement_id, spec in updates.items():
        classifications[statement_id] = spec["relation"]
    for row in new_statements:
        classifications[row["statement_id"]] = row["qualifiers"]["relation_candidate"]
    counts = {"true": sum(value is True for value in classifications.values()), "false": sum(value is False for value in classifications.values()), "unset": sum(value is None for value in classifications.values())}
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "segment_sha256": segment["sha256"],
        "existing_statements": len(p128),
        "statement_updates": len(updates),
        "new_statements": len(new_statements),
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [{"id": row["mention_id"], "surface": row["surface_form"], "span": [row["start_char"], row["end_char"]]} for row in new_mentions],
        "p128_classification_after": counts,
        "table_sha256_before": {path.name: sha(path) for path in (STATEMENTS, CANDIDATES, MENTIONS)},
    }, ensure_ascii=False, indent=2))

    if not args.apply:
        return

    backup_paths = [path.with_name(path.name + ".bak-s2-chp5-p128-20261012") for path in (STATEMENTS, CANDIDATES, MENTIONS)]
    if any(path.exists() for path in backup_paths):
        raise SystemExit("a p.128 recovery copy already exists; refusing to overwrite")
    for original, backup in zip((STATEMENTS, CANDIDATES, MENTIONS), backup_paths):
        shutil.copy2(original, backup)

    changed = set(updates)
    raw_lines = STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
    statement_lines = []
    for raw in raw_lines:
        row = json.loads(raw)
        if row["statement_id"] in changed:
            statement_lines.append(json.dumps(statement_by_id[row["statement_id"]], ensure_ascii=False))
        else:
            statement_lines.append(raw)
    statement_lines.extend(json.dumps(row, ensure_ascii=False) for row in new_statements)
    STATEMENTS.write_text("\n".join(statement_lines) + "\n", encoding="utf-8", newline="")

    def write_csv(path: Path, rows: list[dict], additions: list[dict]) -> None:
        bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
        raw = path.read_bytes()
        line_ending = "\r\n" if raw.count(b"\r\n") > raw.count(b"\n") / 2 else "\n"
        fieldnames = list(rows[0])
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=line_ending, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        writer.writerows(additions)
        path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8"))

    write_csv(CANDIDATES, candidates, new_candidates)
    write_csv(MENTIONS, mentions, new_mentions)
    print(json.dumps({"mode": "applied", "backups": [str(path.relative_to(BASE)) for path in backup_paths], "table_sha256_after": {path.name: sha(path) for path in (STATEMENTS, CANDIDATES, MENTIONS)}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
