from __future__ import annotations

import argparse
import codecs
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path.cwd()
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "05_CHP-5_sec_iii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-5.pdf"
PAGE_IMAGE = PROCESS / "p133_page_review_20261012.png"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
SEGMENT = "chp-5:05_CHP-5_sec_iii:l12-18"
NOTE_STATEMENT_ID = "st-chp5-notes-l129-gigli-citation"

EXPECTED = {
    "book-statements.jsonl": "817794cfddab7e9e02d0f1531584d2b437e795588e1995304e2ca9bdd53ee5da",
    "entity-candidates.csv": "012efa6759909bc8a1e9b7c16929f331b0b0c065279090c488810b00b25c8df4",
    "mentions.csv": "665ebc1635b2af8282feba756bffe34d609786bea45c3f2f937f90a3b235681a",
}
SOURCE_SHA = "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a"
PDF_SHA = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
IMAGE_SHA = "2da80de80eb9491e2bd70eb6d9c36ea19dee0cf15ba255766ac547b5efed356c"
SEGMENT_SHA = "7665aa1fe5c68405644c7ebc5bfbe3fd99be5daef5a8b35e8e62fabf46e35882"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_csv(path: Path) -> tuple[list[dict], list[str], bool]:
    raw = path.read_bytes()
    bom = raw.startswith(codecs.BOM_UTF8)
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader), list(reader.fieldnames or []), bom


def render_csv(rows: list[dict], fields: list[str], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="raise", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    return codecs.BOM_UTF8 + data if bom else data


def exact(text: str, quote: str) -> str:
    need(quote in text, f"source quote not found: {quote!r}")
    return quote


def source_qualifier(line_start: int, line_end: int, claim: str, qualification: str,
                     mentioned: list[str], relation: bool, **extra) -> dict:
    q = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 133,
        "pdf_physical_page": 14,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial narration",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "relation_candidate_note": (
            "Source-grounded S2 relation candidate only; no formal S6 edge is created."
            if relation else
            "Source claim retained in S2; no formal entity relation is proposed."
        ),
    }
    q.update(extra)
    return q


BODY_LINES = {
    "st-chp5-p133-1648-grain-pardon-offer": {
        "subject": "cand-6102", "object": "cand-6103", "predicate": "pardon_offered_for_grain_delivery",
        "quote": "In 1648 free pardons were offered to the bandits who ravaged the campagna if only they would bring corn into Rome.",
        "line": (15, 15), "relation": True,
        "claim": "Haskell reports a 1648 offer of free pardons to bandits ravaging the campagna on condition that they bring corn into Rome.",
        "qualification": "The passage reports an offer; it does not say whether the bandits accepted or delivered grain.",
        "mentioned": ["cand-6102", "cand-6103", "cand-4243", "cand-4490"],
    },
    "st-chp5-p133-conclave-soldiers-join-riots": {
        "subject": "cand-6109", "object": "cand-6111", "predicate": "joined_riots_and_fought_with_police",
        "quote": "the soldiers themselves who came in large numbers to protect the princes and cardinals as they assembled for the conclave took part in the riots and fought with the regular police appointed to keep order.",
        "line": (15, 15), "relation": True,
        "claim": "Haskell says the soldiers who accompanied conclave participants joined the riots and fought the regular police appointed to keep order.",
        "qualification": "The source does not identify the conclave, soldiers or officers; the separate protection assignment is recorded independently.",
        "mentioned": ["cand-6109", "cand-6110", "cand-6111"],
    },
    "st-chp5-p133-cultivated-society-distaste-and-arcadian-ideal": {
        "subject": "cand-11803", "object": "cand-6118", "predicate": "regarded_with_extreme_distaste",
        "quote": "cultivated society and all who aped it looked upon the poor with extreme distaste",
        "line": (17, 17), "relation": True,
        "claim": "Haskell says cultivated society and its imitators in seventeenth-century Rome regarded the poor with extreme distaste.",
        "qualification": "This is Haskell's general characterization of social attitudes; the group is unnamed and not a formal institution.",
        "mentioned": ["cand-4490", "cand-11803", "cand-6118"],
    },
    "st-chp5-p133-diaries-and-serene-paintings": {
        "subject": "cand-0173", "object": None, "predicate": "surviving_paintings_show_little_of_recorded_misery",
        "quote": "All this violence and misery was recorded with monotonous regularity by contemporary diarists: yet wesind only the barest hint of it in those works of the bamboccianti which have come down to us and which tend to convey a picture of untroubled serenity.",
        "line": (16, 16), "relation": False,
        "claim": "Haskell contrasts contemporary diaries' regular recording of violence and misery with the limited trace and untroubled serenity he sees in surviving Bamboccianti works.",
        "qualification": "This is Haskell's interpretive comparison. The scan reads 'we find'; S0 OCR 'wesind' remains unchanged.",
        "mentioned": ["cand-0173"],
    },
    "st-chp5-p133-doni-operatic-shepherds-quotation": {
        "subject": "cand-0943", "object": None, "predicate": "quoted_comment_on_stage_shepherds",
        "quote": "that the shepherds who are brought on to the stage are the sordid and",
        "line": (18, 18), "relation": False,
        "claim": "Haskell begins quoting Giovanni Battista Doni on contemporary opera: readers should not imagine that stage shepherds are the sordid people who tend flocks in the present day.",
        "qualification": "Nested quotation attributed to Doni; the sentence continues at p.134 L21 and is not complete in this segment.",
        "mentioned": ["cand-0943"],
        "speaker": "Giovanni Battista Doni",
        "text_layer": "quoted commentary reported by Haskell",
    },
    "st-chp5-p133-embassy-tension-and-riots": {
        "subject": "cand-6112", "object": "cand-6113", "predicate": "lived_in_permanent_tension",
        "quote": "The French and the Spaniards attached to their respective embassies lived in a state of permanent tension",
        "line": (15, 15), "relation": True,
        "claim": "Haskell says the French and Spanish communities attached to their respective Rome embassies lived in permanent tension.",
        "qualification": "The account concerns unnamed embassy communities; recurring riots and the distinct papal armed police are recorded separately. The footnote cites Gigli.",
        "mentioned": ["cand-6112", "cand-6113", "cand-4490"],
    },
    "st-chp5-p133-epidemics-and-overcrowded-housing": {
        "subject": None, "object": "cand-4490", "predicate": "epidemics_threatened_overcrowded_population",
        "quote": "Epidemics threatened the population herded together in overcrowded hovels.",
        "line": (15, 15), "relation": False,
        "claim": "Haskell says epidemics threatened a population crowded into overcrowded hovels in Rome.",
        "qualification": "No disease, date, count or particular housing site is named.",
        "mentioned": ["cand-4490"],
    },
    "st-chp5-p133-mob-and-papal-statue": {
        "subject": "cand-6108", "object": "cand-6106", "predicate": "stationed_to_protect_statue_from_mob",
        "quote": "soldiers were stationed at strategic points to prevent the mob destroying the statue",
        "line": (15, 15), "relation": True,
        "claim": "Haskell says soldiers were stationed strategically to protect the unnamed papal memorial statue from a potential attempt by a mob to destroy it.",
        "qualification": "The passage reports preventive deployment, not a completed attack; the mob is an unnamed group and is recorded as a separate candidate.",
        "mentioned": ["cand-6108", "cand-6106", "cand-11801"],
    },
    "st-chp5-p133-not-social-protest": {
        "subject": "cand-0173", "object": None, "predicate": "not_interpreted_as_social_protest",
        "quote": "Certainly not as social protest.",
        "line": (17, 17), "relation": False,
        "claim": "Haskell rejects interpreting the Bamboccianti as social protest.",
        "qualification": "This is Haskell's interpretation, not an independent conclusion.",
        "mentioned": ["cand-0173"],
    },
    "st-chp5-p133-organised-beggar-bands": {
        "subject": "cand-6104", "object": "cand-4490", "predicate": "roamed_rome_in_organised_bands",
        "quote": "Beggars roamed the streets often in organised bands held together by strange rituals.",
        "line": (15, 15), "relation": True,
        "claim": "Haskell says beggars roamed Rome in organised bands held together by unusual rituals.",
        "qualification": "The groups and rituals are not individually named or described.",
        "mentioned": ["cand-6104", "cand-4490"],
    },
    "st-chp5-p133-papal-vacancy-and-discontent": {
        "subject": "cand-6105", "object": "cand-6107", "predicate": "vacancy_context_crystallised_discontent",
        "quote": "Unrest was always present; when the Pope died and Rome was only partially governed by authorities with temporary powers this permanent discontent would become crystallised.",
        "line": (15, 15), "relation": False,
        "claim": "Haskell describes unrest as persistent and says permanent discontent crystallised when a pope died while Rome was only partly governed by temporary authorities.",
        "qualification": "The pope and vacancy are unidentified; the explicit Rome-to-authorities governance claim is atomized separately.",
        "mentioned": ["cand-6105", "cand-6107", "cand-4490"],
    },
    "st-chp5-p133-restricted-window-and-contrasts": {
        "subject": "cand-0173", "object": None, "predicate": "restricted_pictorial_view_contrasted_with_other_artists",
        "quote": "The view from their window was evidently a somewhat restricted one. We do not find in their works the distortions of Georges de la Tour or the brutality of Jacques\nCallot;",
        "line": (16, 17), "relation": False,
        "claim": "Haskell calls the Bamboccianti's pictorial view restricted and contrasts their works with what he describes as distortions by Georges de la Tour and brutality by Jacques Callot.",
        "qualification": "'Distortions' and 'brutality' are Haskell's comparative judgments, not neutral factual labels.",
        "mentioned": ["cand-0173", "cand-1346", "cand-0482"],
    },
    "st-chp5-p133-rome-streets-and-urban-proletariat": {
        "subject": None, "object": None, "predicate": "street_commerce_and_indifference_to_monuments",
        "quote": "and side-streets and no one bothers to look at the soaring obelisks or fountains dimly visible in the distance.",
        "line": (13, 13), "relation": False,
        "claim": "Continuing the p.132 Rome scene, Haskell says commerce extended into side streets while passers-by ignored obelisks and fountains visible in the distance.",
        "qualification": "The following description of peasantry blending into the urban proletariat is recorded in its own statement; this is not a demographic claim about Rome.",
        "mentioned": ["cand-4490"],
    },
    "st-chp5-p133-rural-poverty-and-starvation": {
        "subject": "cand-6116", "object": None, "predicate": "extreme_poverty_and_recurring_starvation",
        "quote": "The most regular condition of the Italian peasant’s life in the seventeenth century was one of extreme poverty punctuated by periods of real starvation. Grain shortages were endemic. Desperate and extraordinary measures totally failed to cope with them.",
        "line": (14, 14), "relation": False,
        "claim": "Haskell characterizes ordinary seventeenth-century Italian peasant life as extreme poverty interrupted by starvation, with endemic grain shortages and failed extraordinary measures.",
        "qualification": "This is a general characterization; it does not claim every individual had the same experience.",
        "mentioned": ["cand-6116"],
    },
    "st-chp5-p133-surviving-works-and-hostile-criticism": {
        "subject": "cand-6099", "object": None, "predicate": "surviving_works_seldom_match_opponents_claims",
        "quote": "It is certain that many bambocciate have not survived; yet few of those that have, or that are recorded in inventories, have that aggressively offensive character that their very vocal opponents claimed.",
        "line": (17, 17), "relation": False,
        "claim": "Haskell says many bambocciate are lost, while few surviving or inventory-recorded examples display the aggressively offensive character their vocal opponents claimed.",
        "qualification": "Distinguish Haskell's certainty about loss from his qualified observation about surviving and inventoried works.",
        "mentioned": ["cand-6099"],
    },
    "st-chp5-p133-sweerts-le-nain-velasquez-peasants": {
        "subject": "cand-2536", "object": "cand-6116", "predicate": "visualizes",
        "quote": "Only Michael Sweerts gives his peasants the dignity and monumentality that is almost polemically asserted by their contemporaries in the paintings of Le Nain or Velasquez.",
        "line": (17, 17), "relation": True,
        "claim": "Haskell says Michael Sweerts represents peasants with dignity and monumentality, comparing the effect to paintings attributed collectively to Le Nain and to Velasquez.",
        "qualification": "No individual works are named; preserve the collective Le Nain attribution and Haskell's comparison.",
        "mentioned": ["cand-2536", "cand-6116", "cand-6114", "cand-2709"],
    },
    "st-chp5-p133-tiber-floods": {
        "subject": "cand-4453", "object": "cand-4490", "predicate": "flooded_low_lying_parts_of",
        "quote": "At frequent intervals the Tiber burst its banks and devastating floods swept through the low-lying parts of the city.",
        "line": (15, 15), "relation": True,
        "claim": "Haskell reports frequent Tiber floods that devastated low-lying parts of Rome.",
        "qualification": "No individual flood date is specified.",
        "mentioned": ["cand-4453", "cand-4490"],
    },
}


NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11801", "index_entry_id": "", "canonical_name": "Unidentified Roman mob threatening the papal memorial statue (Haskell account)",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Unnamed crowd that the stationed soldiers were placed to prevent from destroying a statue to a deceased pope. The source reports a preventive threat, not a completed attack.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L15",
    },
    {
        "candidate_id": "cand-11802", "index_entry_id": "", "canonical_name": "Unnamed administration that erected a papal memorial statue (Haskell account)",
        "index_page_range": "", "suggested_type": "institution", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Unidentified administration said to have erected the statue. 'Sycophantic' is Haskell's characterization, not an institutional name or identity.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L15",
    },
    {
        "candidate_id": "cand-11803", "index_entry_id": "", "canonical_name": "Cultivated society and its imitators in seventeenth-century Rome (Haskell account)",
        "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Source-defined social group said to regard the poor with extreme distaste; not treated as a formal institution, and individual members are not named.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L17",
    },
    {
        "candidate_id": "cand-11804", "index_entry_id": "", "canonical_name": "Armed police of the popes in Rome (unnamed unit)",
        "index_page_range": "", "suggested_type": "institution", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Unidentified papal armed police said to have difficulty repressing the embassy riots. Keep distinct from the regular police, cand-6111.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L15",
    },
    {
        "candidate_id": "cand-11805", "index_entry_id": "", "canonical_name": "Recurring bloody riots arising from French-Spanish embassy tensions in Rome (undated)",
        "index_page_range": "", "suggested_type": "event", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says embassy tension often erupted into bloody riots. No individual riot, date, or named participant is identified; retain as a recurring source-defined event group.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L15",
    },
]


NEW_MENTION_SPECS = [
    ("cand-6107", "authorities with temporary powers", "Unnamed temporary governing authority; do not infer its institutional identity."),
    ("cand-11801", "the mob", "Unnamed crowd; the passage reports a preventive threat, not a completed attack."),
    ("cand-11802", "a sycophantic administration", "Unidentified administration; 'sycophantic' is Haskell's judgment."),
    ("cand-6105", "the Pope’s", "Same unidentified pope referenced earlier in the sentence; no identity inferred."),
    ("cand-11803", "cultivated society and all who aped it", "Source-defined social group and imitators; no individual members named."),
    ("cand-11804", "the armed police of the popes", "Unidentified armed papal police; distinct from the regular police, cand-6111."),
    ("cand-11805", "bloody riots", "Recurring, undated riots; no individual event is identified."),
]


def new_statement(statement_id: str, subject: str | None, obj: str | None, predicate: str,
                  quote: str, line: int, claim: str, qualification: str,
                  mentioned: list[str], relation: bool, **extra) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": source_qualifier(line, line, claim, qualification, mentioned, relation, **extra),
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


NEW_STATEMENTS = [
    new_statement(
        "st-chp5-p133-conclave-soldiers-protected-princes-cardinals", "cand-6109", "cand-6110", "protected_at_conclave",
        "the soldiers themselves who came in large numbers to protect the princes and cardinals as they assembled for the conclave", 15,
        "Haskell says the soldiers came in large numbers to protect the princes and cardinals as they assembled for a conclave.",
        "The participants, soldiers, and conclave are not individually identified.", ["cand-6109", "cand-6110"], True,
        temporal_context="during an unnamed conclave; no date supplied",
    ),
    new_statement(
        "st-chp5-p133-mob-threatened-statue", "cand-11801", "cand-6106", "threatened_to_destroy",
        "to prevent the mob destroying the statue", 15,
        "The account identifies the mob as a potential threat to the statue, prompting soldiers to be stationed to prevent its destruction.",
        "This is a preventive deployment; the source does not report a completed attack or a specific attempt.", ["cand-11801", "cand-6106", "cand-6108"], True,
    ),
    new_statement(
        "st-chp5-p133-administration-erected-statue", "cand-11802", "cand-6106", "erected",
        "a sycophantic administration had erected", 15,
        "Haskell says an unnamed administration erected the statue a few years earlier.",
        "The administration is not identified; 'sycophantic' is Haskell's evaluative description.", ["cand-11802", "cand-6106"], True,
        temporal_context="a few years before the described unrest; exact date unknown",
    ),
    new_statement(
        "st-chp5-p133-statue-commemorated-pope", "cand-6106", "cand-6105", "dedicated_to",
        "the statue which only a few years earlier a sycophantic administration had erected to the Pope’s eternal memory", 15,
        "The unnamed statue was erected to commemorate the unidentified deceased pope.",
        "The pope's identity and the statue's identity remain unresolved.", ["cand-6106", "cand-6105"], True,
    ),
    new_statement(
        "st-chp5-p133-rome-partially-governed-by-temporary-authorities", "cand-4490", "cand-6107", "partially_governed_by",
        "Rome was only partially governed by authorities with temporary powers", 15,
        "Haskell says Rome was only partially governed by authorities holding temporary powers during the unnamed papal vacancy.",
        "The authorities and vacancy episode are unidentified; do not infer a particular administration or pope.", ["cand-4490", "cand-6107", "cand-6105"], True,
        temporal_context="during an unnamed papal vacancy",
    ),
    new_statement(
        "st-chp5-p133-peasantry-merges-into-urban-proletariat", "cand-6116", "cand-6117", "merged_into",
        "The characters are a satisfied and lively peasantry, hard working and sober, merging almost imperceptibly into an urban proletariat of reasonable prosperity.", 13,
        "In Haskell's account of the represented characters, a lively and sober peasantry merges almost imperceptibly into a modestly prosperous urban proletariat.",
        "This describes the represented social continuum, not a documented demographic transition; 'reasonable prosperity' is retained.", ["cand-0173", "cand-6116", "cand-6117"], True,
        representation_scope="character types in the described Bamboccianti world; not a demographic claim",
    ),
    new_statement(
        "st-chp5-p133-arcadian-sentiment-literary-only", "cand-6115", None, "literary_ideal_without_behavioural_repercussion",
        "Arcadian sentiment was a purely literary phenomenon with no repercussions as yet on actual social behaviour or inclinations.", 17,
        "Haskell characterizes Arcadian sentiment as a literary phenomenon that had not yet affected actual social behaviour or inclinations.",
        "This is Haskell's broad interpretation of seventeenth-century Roman culture.", ["cand-6115", "cand-4490"], False,
    ),
    new_statement(
        "st-chp5-p133-embassy-riots-occurred-in-rome", "cand-11805", "cand-4490", "occurred_at",
        "often this exploded into bloody riots", 15,
        "Haskell says the tension between the French and Spanish embassy communities often erupted into bloody riots in Rome.",
        "The riots are recurring and undated; no individual episode is identified.", ["cand-11805", "cand-6112", "cand-6113", "cand-4490"], True,
    ),
    new_statement(
        "st-chp5-p133-papal-armed-police-struggled-to-repress-riots", "cand-11805", "cand-11804", "difficult_to_repress_by",
        "which the armed police of the popes found exceedingly difficult to repress", 15,
        "Haskell says the armed police of the popes found the embassy riots exceedingly difficult to repress.",
        "This papal armed police is distinct from the regular police, cand-6111; the source identifies no particular unit or riot date.", ["cand-11805", "cand-11804"], True,
    ),
    new_statement(
        "st-chp5-p133-vacancy-added-to-existing-violence", None, None, "vacancy_was_not_the_only_stimulus_for_violence",
        "But such violence was prevalent enough without the occasion of a vacant papacy to provide further stimulus.", 15,
        "Haskell says violence was already prevalent, so a vacant papacy supplied additional stimulus rather than being its sole cause.",
        "This is an authorial qualification on causality; it does not identify a particular vacancy or riot.", [], False,
    ),
    new_statement(
        "st-chp5-p133-crime-libels-and-riots-public", None, None, "public_disorder_in_rome",
        "Crime assumed terrible proportions, libels and riots came out into the open;", 15,
        "Haskell describes crime as reaching terrible proportions and libels and riots as becoming public.",
        "These are general claims without named incidents, dates, or actors.", ["cand-4490"], False,
    ),
    new_statement(
        "st-chp5-p133-contemporaries-accused-bamboccianti-of-buffoons", "cand-0173", None, "accused_of_depicting_vulgar_buffoons",
        "nor yet the vulgar buffoons that so many of their contemporaries accused them of putting into their pictures.", 17,
        "Haskell reports that many contemporaries accused the Bamboccianti of putting vulgar buffoons into their pictures.",
        "This records a reported criticism, not Haskell's endorsement of the accusation; individual critics are unnamed.", ["cand-0173"], False,
    ),
]


def atomic_write(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def build_plan() -> dict:
    need(ROOT.name == "PNP-Final-DATA", f"unexpected working directory: {ROOT}")
    need(sha256(SOURCE) == SOURCE_SHA, "source markdown changed")
    need(sha256(PDF) == PDF_SHA, "source PDF changed")
    need(sha256(PAGE_IMAGE) == IMAGE_SHA, "p.133 page image changed or missing")
    for name, expected in EXPECTED.items():
        need(sha256(TABLES / name) == expected, f"unexpected pre-write hash: {name}")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    body_text = "\n".join(lines[11:18])
    need(sha256_bytes(body_text.encode("utf-8")) == SEGMENT_SHA, "p.133 segment text changed")
    segment_rows = [json.loads(x) for x in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    seg = next((x for x in segment_rows if x.get("segment_id") == SEGMENT), None)
    need(seg is not None and seg.get("sha256") == SEGMENT_SHA, "segment registry hash does not match source lines")

    statement_path = TABLES / "book-statements.jsonl"
    raw_statement_lines = statement_path.read_text(encoding="utf-8").splitlines(keepends=True)
    statements = [json.loads(x) for x in raw_statement_lines if x.strip()]
    by_id = {x.get("statement_id"): x for x in statements}
    need(len(by_id) == len(statements), "duplicate statement ids in input")
    need(set(BODY_LINES).issubset(by_id), "one or more p.133 target statements are missing")
    p133_existing = [x for x in statements if x.get("segment_id") == SEGMENT]
    need(len(p133_existing) == 17, f"expected 17 p.133 existing statements, found {len(p133_existing)}")
    for sid in BODY_LINES:
        need(by_id[sid].get("qualifiers", {}).get("relation_candidate") is None,
             f"target statement already classified or has an unexpected state: {sid}")
        need(BODY_LINES[sid]["quote"] in body_text, f"target quote is not exact source text: {sid}")

    candidates, candidate_fields, candidate_bom = read_csv(TABLES / "entity-candidates.csv")
    mentions, mention_fields, mention_bom = read_csv(TABLES / "mentions.csv")
    existing_candidate_ids = {x["candidate_id"] for x in candidates}
    new_candidate_ids = {x["candidate_id"] for x in NEW_CANDIDATES}
    need(not (existing_candidate_ids & new_candidate_ids), "new candidate id already exists")
    numeric_ids = [int(x.split("-")[1]) for x in existing_candidate_ids if x.startswith("cand-") and x.split("-")[1].isdigit()]
    need(max(numeric_ids) == 11800, f"unexpected candidate sequence; max is {max(numeric_ids)}")
    mention_ids = {x["mention_id"] for x in mentions}
    statement_ids = {x["statement_id"] for x in statements}
    need(not (mention_ids & {f"m-chp5-sec-iii-l12-18-{i:03d}" for i in range(30, 30 + len(NEW_MENTION_SPECS))}),
         "one or more new mention ids already exist")
    need(not (statement_ids & {x["statement_id"] for x in NEW_STATEMENTS}), "one or more new statement ids already exist")
    need({"candidate_id", "canonical_name", "suggested_type", "status", "detail", "candidate_source_ref"}.issubset(candidate_fields),
         "candidate table schema is missing required fields")

    p133_mentions = [x for x in mentions if x.get("segment_id") == SEGMENT]
    need(len(p133_mentions) == 29, f"expected 29 existing p.133 mentions, found {len(p133_mentions)}")
    for m in p133_mentions:
        start, end = int(m["start_char"]), int(m["end_char"])
        need(body_text[start:end] == m["surface_form"], f"existing mention span mismatch: {m['mention_id']}")

    updated = []
    for sid, spec in BODY_LINES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        line_start, line_end = spec["line"]
        q.update({
            "source_line_start": line_start,
            "source_line_end": line_end,
            "claim": spec["claim"],
            "speaker": spec.get("speaker", "Haskell"),
            "text_layer": spec.get("text_layer", "authorial narration"),
            "qualification": spec["qualification"],
            "mentioned_candidate_ids": spec["mentioned"],
            "relation_candidate": spec["relation"],
            "relation_candidate_note": (
                "Source-grounded S2 relation candidate only; no formal S6 edge is created."
                if spec["relation"] else
                "Source claim retained in S2; no formal entity relation is proposed."
            ),
        })
        updated.append((sid, {
            "subject_candidate_id": spec["subject"],
            "object_candidate_id": spec["object"],
            "predicate": spec["predicate"],
            "original_quote": exact(body_text, spec["quote"]),
            "qualifiers": q,
        }))

    new_mentions = []
    for i, (candidate_id, surface, note) in enumerate(NEW_MENTION_SPECS, start=30):
        start = body_text.find(surface)
        need(start >= 0 and body_text.find(surface, start + 1) < 0,
             f"mention surface missing or ambiguous: {surface!r}")
        end = start + len(surface)
        need(body_text[start:end] == surface, f"new mention span mismatch: {surface!r}")
        new_mentions.append({
            "mention_id": f"m-chp5-sec-iii-l12-18-{i:03d}",
            "segment_id": SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    note = by_id.get(NOTE_STATEMENT_ID)
    need(note is not None and note.get("qualifiers", {}).get("relation_candidate") is True,
         "p.133 footnote citation statement is missing or not classified as a relation candidate")
    note_q = dict(note["qualifiers"])
    need(note_q.get("related_segment") == SEGMENT and note_q.get("related_source_lines") == [15],
         "p.133 note no longer points to the embassy passage")
    linked = [
        "st-chp5-p133-embassy-tension-and-riots",
        "st-chp5-p133-embassy-riots-occurred-in-rome",
        "st-chp5-p133-papal-armed-police-struggled-to-repress-riots",
    ]
    note_q["linked_body_statement_ids"] = linked
    note_q["citation_body_statement_ids"] = linked
    note_update = {"qualifiers": note_q}

    updates = dict(updated)
    updates[NOTE_STATEMENT_ID] = note_update
    new_statements = []
    for s in NEW_STATEMENTS:
        new_statements.append({
            **s,
            "original_quote": exact(body_text, s["original_quote"]),
        })

    new_candidate_ids = set(new_candidate_ids)
    need(all(m["candidate_id"] in existing_candidate_ids | new_candidate_ids for m in new_mentions),
         "new mention points to an unregistered candidate")
    for s in new_statements:
        need(s["original_quote"] in body_text, f"new statement quote is not exact: {s['statement_id']}")
        need(s.get("subject_candidate_id") is None or s["subject_candidate_id"] in existing_candidate_ids | new_candidate_ids,
             f"unknown new statement subject: {s['statement_id']}")
        need(s.get("object_candidate_id") is None or s["object_candidate_id"] in existing_candidate_ids | new_candidate_ids,
             f"unknown new statement object: {s['statement_id']}")

    return {
        "raw_statement_lines": raw_statement_lines,
        "updates": updates,
        "new_statements": new_statements,
        "candidates": candidates,
        "candidate_fields": candidate_fields,
        "candidate_bom": candidate_bom,
        "mentions": mentions,
        "mention_fields": mention_fields,
        "mention_bom": mention_bom,
        "new_candidates": NEW_CANDIDATES,
        "new_mentions": new_mentions,
        "body_text": body_text,
    }


def render_jsonl(plan: dict) -> bytes:
    out = []
    for raw in plan["raw_statement_lines"]:
        if not raw.strip():
            out.append(raw)
            continue
        row = json.loads(raw)
        update = plan["updates"].get(row.get("statement_id"))
        if update:
            row.update(update)
            ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else "\n"
            out.append(json.dumps(row, ensure_ascii=False) + ending)
        else:
            out.append(raw)
    out.extend(json.dumps(row, ensure_ascii=False) + "\n" for row in plan["new_statements"])
    return "".join(out).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled S2 p.133 writeback; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed exact change set")
    args = parser.parse_args()
    plan = build_plan()
    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    outputs = {
        statement_path: render_jsonl(plan),
        candidate_path: render_csv(plan["candidates"] + plan["new_candidates"], plan["candidate_fields"], plan["candidate_bom"]),
        mention_path: render_csv(plan["mentions"] + plan["new_mentions"], plan["mention_fields"], plan["mention_bom"]),
    }
    relation_count = sum(1 for sid, row in plan["updates"].items() if sid in BODY_LINES
                         and row.get("qualifiers", {}).get("relation_candidate") is True)
    relation_count += sum(1 for row in plan["new_statements"] if row["qualifiers"]["relation_candidate"])
    total = len(BODY_LINES) + len(plan["new_statements"])
    print("S2 p.133 dry-run / exact plan")
    print(f"source sha256: {sha256(SOURCE)}")
    print(f"page image sha256: {sha256(PAGE_IMAGE)}")
    print(f"existing p.133 statements classified: {len(BODY_LINES)}; new atomic statements: {len(plan['new_statements'])}")
    print(f"final p.133 statements: {total} ({relation_count} relation candidates, {total - relation_count} non-relational)")
    print(f"new candidates: {len(plan['new_candidates'])}; new mentions: {len(plan['new_mentions'])}; verified existing p.133 mentions: {len([m for m in plan['mentions'] if m.get('segment_id') == SEGMENT])}")
    print(f"p.133 note statement link targets: {plan['updates'][NOTE_STATEMENT_ID]['qualifiers']['linked_body_statement_ids']}")
    for path, data in outputs.items():
        print(f"{path.relative_to(ROOT)}: {sha256(path)} -> {sha256_bytes(data)} ({len(data)} bytes)")
    if not args.apply:
        print("dry-run only; no tables written")
        return

    backups = {}
    suffix = ".bak-s2-chp5-p133-20261012"
    for path in outputs:
        backup = path.with_name(path.name + suffix)
        need(not backup.exists(), f"recovery copy already exists: {backup.name}")
        shutil.copy2(path, backup)
        need(sha256(backup) == EXPECTED[path.name], f"recovery copy hash mismatch: {backup.name}")
        backups[path] = backup
    for path, data in outputs.items():
        atomic_write(path, data)
    for path in outputs:
        print(f"applied {path.relative_to(ROOT)} sha256={sha256(path)} backup={backups[path].name}")
    print("apply complete")


if __name__ == "__main__":
    main()
