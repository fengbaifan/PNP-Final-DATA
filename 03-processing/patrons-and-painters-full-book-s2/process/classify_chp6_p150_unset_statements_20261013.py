from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_i.md"
SEGMENT = "chp-6:06_CHP-6_sec_i:l48-57"
NEXT_SEGMENT = "chp-6:06_CHP-6_sec_i:l59-67"
TARGETS = {
    "st-chp6-p150-foreign-tributes",
    "st-chp6-p150-local-trade-industry",
    "st-chp6-p150-ambassador-benefice-policy",
    "st-chp6-p150-rome-tolerates-revenue-loss",
    "st-chp6-p150-navona-protest-rhymes",
    "st-chp6-p150-taxes-and-resentment",
    "st-chp6-p150-rhyme-demands-bread",
    "st-chp6-p150-academy-director-proposals",
    "st-chp6-p150-accademia-financial-difficulties",
    "st-chp6-p150-monumental-ambition-persists",
    "st-chp6-p150-papal-response-unlikely",
    "st-chp6-p150-small-enterprises-suffer",
    "st-chp6-p150-artists-begin-to-suffer",
    "st-chp6-p150-dealers-and-bamboccianti",
    "st-chp6-p150-preti-finds-artists-unemployed",
    "st-chp6-p150-burial-cost-dispute",
    "st-chp6-p150-coffin-refusal",
    "st-chp6-p150-agostino-raphael-friendship",
    "st-chp6-p150-alexander-accession-patronage",
    "st-chp6-p150-alexander-friendship-partial",
    "st-chp6-p150-alexander-legate-in-cologne",
    "st-chp6-p150-alexander-wrote-agostino-life",
    "st-chp6-p150-camillo-holiness-quote",
    "st-chp6-p150-fabio-descended-from-agostino",
    "st-chp6-p150-olimpia-heiress-quote",
}
CANDIDATE_IDS = [f"cand-{n}" for n in range(11971, 11977)]
MENTION_IDS = [
    "m-chp6-p150-external-tributes",
    "m-chp6-p150-ambassador-rulers",
    "m-chp6-p150-benefice-incomes",
    "m-chp6-p150-roman-public",
    "m-chp6-p150-building-expenditure",
]
NEW_STATEMENT_IDS = [
    "st-chp6-p150-mercantilist-doctrines-intensified-tribute-decline",
    "st-chp6-p150-accademia-faces-difficulties-1648",
    "st-chp6-p150-bamboccianti-complaints",
    "st-chp6-p150-camillo-refused-coffin-payment",
]
EXPECTED_HASHES = {
    STATEMENTS: "18b82cbed37b6c20abc756c04335ff68ce4d0171bd04c6c8676627f5b502f086",
    CANDIDATES: "f3df912a4b5392cf9afba29caa92601ce146d86423397fc0aca35182d2c6bd4c",
    MENTIONS: "b94702d6c96f0054cc1833f78e71c28e30ee2b5cab8b8e181b998ab5be35462b",
    COVERAGE: "147cbf2bfc7a3ec8810fae33aea146f900ade288e3c27498264789deee44d15a",
}
SOURCE_SHA256 = "e1bf27cf13961032d4587a1787a1b89f00a9076cf7a8c9dd4434000e84add42d"
SEGMENT_SHA256 = "b47108f683c59b6cc10648bf827d6e3c3430d4ef54b77460c84adb3232138682"
BACKUP_SUFFIX = ".bak-s2-chp6-p150-unset-classification-20261013"
FALSE_NOTE = "This is a source-attributed descriptive, biographical, or evaluative claim, not a relation between represented entities."
TRUE_NOTE = "This is an explicit source-attributed relation candidate retained at S2; it does not create a formal S6 edge."


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.split())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    os.replace(temp, path)


def quote_between(text: str, first: str, last: str) -> str:
    start = text.find(first)
    if start < 0:
        raise SystemExit(f"quote start not found: {first!r}")
    if first == last:
        return text[start:start + len(first)]
    end = text.find(last, start + len(first))
    if end < 0:
        raise SystemExit(f"quote end not found: {last!r}")
    return text[start:end + len(last)]


def make_candidate(cid: str, name: str, detail: str, line: int) -> dict[str, str]:
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": "term", "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line}",
    }


def add_mention(mid: str, cid: str, surface: str, note: str, text: str) -> dict[str, str]:
    positions = [i for i in range(len(text)) if text.startswith(surface, i)]
    if len(positions) != 1:
        raise SystemExit(f"expected one mention surface, got {len(positions)}: {mid} / {surface!r}")
    start = positions[0]
    return {"mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid,
            "surface_form": surface, "start_char": str(start),
            "end_char": str(start + len(surface)), "note": note}


def new_statement(sid: str, subject: str | None, object_: str | None, predicate: str,
                  claim: str, quote: str, start: int, end: int, mentioned: list[str],
                  relation: bool, qualification: str, note: str, *, extra: dict | None = None) -> dict:
    qualifiers = {
        "source_line_start": start, "source_line_end": end,
        "printed_page": "150", "pdf_physical_page": 5,
        "claim": claim, "speaker": "Haskell", "text_layer": "authorial historical narrative",
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
    }
    if extra:
        qualifiers.update(extra)
    return {"statement_id": sid, "segment_id": SEGMENT,
            "subject_candidate_id": subject, "object_candidate_id": object_,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote, "origin": "book",
            "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md"}


def build_outputs() -> tuple[dict[Path, bytes], dict[str, object]]:
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[47:57])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256 or source_lines[47].strip() != "[Page 150]":
        raise SystemExit("p.150 source segment hash/page mismatch")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs in source table")
    unset = {sid for sid, row in by_id.items()
             if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if unset != TARGETS:
        raise SystemExit(f"p.150 unset target set changed: {sorted(unset)}")
    for sid in NEW_STATEMENT_IDS:
        if sid in by_id:
            raise SystemExit(f"new statement ID already exists: {sid}")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    vfields, coverage, vbom = read_csv(COVERAGE)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if any(cid in candidate_ids for cid in CANDIDATE_IDS) or any(mid in mention_ids for mid in MENTION_IDS):
        raise SystemExit("planned candidate or mention ID already exists")
    numeric_candidate_ids = [int(row["candidate_id"].split("-")[1]) for row in candidates
                             if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()]
    if max(numeric_candidate_ids) != 11970:
        raise SystemExit(f"candidate sequence changed: max={max(numeric_candidate_ids)}")
    cov_by_id = {row["segment_id"]: row for row in coverage}
    cov = cov_by_id.get(SEGMENT)
    if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.150 coverage state: {cov}")

    p151 = by_id.get("st-chp6-p151-alexander-circle-friendship")
    if not p151 or p151.get("subject_candidate_id") != "cand-0665" or p151.get("object_candidate_id") != "cand-6301":
        raise SystemExit("p.151 continuation statement changed")

    quote_specs = {
        "st-chp6-p150-foreign-tributes": (49, 49, "Gradually, however, the tributes from abroad", "mercantilist doctrines made headway."),
        "st-chp6-p150-local-trade-industry": (49, 49, "trade and industry were negligible", "effects were only indirect."),
        "st-chp6-p150-ambassador-benefice-policy": (50, 50, "there is no ruler who does not look", "being enjoyed by foreigners."),
        "st-chp6-p150-rome-tolerates-revenue-loss": (50, 50, "At Rome they put up with their disappointment", "But these troubles came none the less."),
        "st-chp6-p150-navona-protest-rhymes": (51, 51, "As the magnificent reconstruction", "attached to the stones2:"),
        "st-chp6-p150-taxes-and-resentment": (51, 51, "Meanwhile sudden and improvised taxes", "papal palaces and squares."),
        "st-chp6-p150-rhyme-demands-bread": (52, 53, "Noi volemo altro che Guglie, et Fontane,", "Pane volemo, pane, pane, pane."),
        "st-chp6-p150-academy-director-proposals": (54, 54, "The director", "only a few of them were carried out"),
        "st-chp6-p150-accademia-financial-difficulties": (54, 54, "In 1648 the Accademia di S. Luca", "faced great difficulties."),
        "st-chp6-p150-monumental-ambition-persists": (54, 54, "for the grandiose adornment of Rome", "a starving population."),
        "st-chp6-p150-papal-response-unlikely": (54, 54, "This was not a hint", "likely to take,"),
        "st-chp6-p150-small-enterprises-suffer": (54, 54, "it was smaller scale enterprises", "vast showy undertakings."),
        "st-chp6-p150-artists-begin-to-suffer": (55, 55, "At first minor", "artists began to suffer."),
        "st-chp6-p150-dealers-and-bamboccianti": (55, 55, "It was now that dealers", "important role"),
        "st-chp6-p150-preti-finds-artists-unemployed": (55, 55, "Mattia Preti found many of them unemployed", "middle ’forties.4"),
        "st-chp6-p150-burial-cost-dispute": (56, 56, "While the corpse lay rotting in a cellar", "charged for the burial."),
        "st-chp6-p150-coffin-refusal": (56, 56, "Donna Olimpia and Prince Camillo Pamfili refused", "January 1655."),
        "st-chp6-p150-agostino-raphael-friendship": (57, 57, "whose friendship with Raphael", "was legendary"),
        "st-chp6-p150-alexander-accession-patronage": (57, 57, "The accession of Fabio Chigi", "enlightened patronage."),
        "st-chp6-p150-alexander-friendship-partial": (57, 57, "Before spending thirteen years", "intimate friend of"),
        "st-chp6-p150-alexander-legate-in-cologne": (57, 57, "Before spending thirteen years", "Papal Legate in Cologne"),
        "st-chp6-p150-alexander-wrote-agostino-life": (57, 57, "whose fife he himself had written.", "whose fife he himself had written."),
        "st-chp6-p150-camillo-holiness-quote": (57, 57, "He says that he has never received anything", "from His Holiness..."),
        "st-chp6-p150-fabio-descended-from-agostino": (57, 57, "He was a direct descendant", "Agostino ‘il Magnifico’"),
        "st-chp6-p150-olimpia-heiress-quote": (57, 57, "She replies that she is not the heiress", "She replies that she is not the heiress"),
    }
    quotes: dict[str, str] = {}
    for sid, (first_line, last_line, first, last) in quote_specs.items():
        text = "\n".join(source_lines[first_line - 1:last_line])
        quote = quote_between(text, first, last)
        if norm(quote) not in norm(by_id[sid].get("original_quote", "")):
            raise SystemExit(f"p.150 source quote does not match the existing statement: {sid}")
        quotes[sid] = quote

    new_candidates = [
        make_candidate("cand-11971", "External tribute revenues on which Rome relied (p.150 account)",
            "Tributes from abroad that Haskell says Rome had long relied on and that began to dry up. No individual payer, territory, or amount is identified.", 49),
        make_candidate("cand-11972", "Rulers in the Venetian ambassador’s 1660 generalization (unnamed group)",
            "The quoted ambassador describes rulers generally as protecting their subjects by preventing ecclesiastical-benefice income from leaving their territories. No rulers or territories are named.", 50),
        make_candidate("cand-11973", "Income from ecclesiastical benefices described as leaving territories",
            "The quoted category is revenue from benefices, especially the richest ones; no specific benefice, amount, or receiving foreigner is identified.", 50),
        make_candidate("cand-11974", "Public affected by taxes and papal building expenditure in Rome (unnamed group)",
            "Haskell's unnamed public in the account of sudden taxes, hardship, and resentment toward spending on papal palaces and squares. No individual members or exact boundary are supplied.", 51),
        make_candidate("cand-11975", "Building and decoration expenditure on papal palaces and squares in Rome",
            "Aggregate expenditure that Haskell says the public resented amid hardship. The passage names no individual palace, square, project, or amount; this is not a candidate for the buildings themselves.", 51),
        make_candidate("cand-11976", "Artists in Rome who began to suffer in Haskell’s mid-1640s account (unnamed group)",
            "The passage-defined artists who began to suffer and of whom Mattia Preti found many unemployed on arriving in Rome. Membership is not listed and this group is not equated with cand-3540 or later artist groups.", 55),
    ]
    if any(row["candidate_id"] in candidate_ids for row in new_candidates):
        raise SystemExit("planned candidate already exists")
    new_mentions = [
        add_mention(MENTION_IDS[0], "cand-11971", "the tributes from abroad",
                    "External tribute flow on which Rome is said to have relied.", segment_text),
        add_mention(MENTION_IDS[1], "cand-11972", "no ruler",
                    "Generic rulers in the unnamed ambassador’s attributed generalization.", segment_text),
        add_mention(MENTION_IDS[2], "cand-11973", "the incomes from ecclesiastical benefices",
                    "Revenue from benefices, distinguished from the benefice institutions themselves.", segment_text),
        add_mention(MENTION_IDS[3], "cand-11974", "the public",
                    "Unnamed collective said to resent expenditure after sudden taxes and hardship.", segment_text),
        add_mention(MENTION_IDS[4], "cand-11975", "building and decorating the papal palaces and squares",
                    "Aggregate expenditure description; no individual building or square is named.", segment_text),
    ]

    # The existing generic Roman-artists candidate comes from a distinct passage.
    artist_mentions = {"m-chp6-p150-090", "m-chp6-p150-092"}
    changed_mentions = [row for row in mentions if row["mention_id"] in artist_mentions]
    if {row["mention_id"] for row in changed_mentions} != artist_mentions:
        raise SystemExit("expected p.150 artist-group mentions changed")
    for row in changed_mentions:
        if row["candidate_id"] != "cand-3540":
            raise SystemExit(f"artist mention mapping changed: {row}")
        row["candidate_id"] = "cand-11976"
        row["note"] = "Maps the artists and their pronoun to the distinct source-defined Rome group at p.150; do not merge with cand-3540."

    candidates_by_id = candidate_ids | set(CANDIDATE_IDS)
    mention_candidates = {
        "st-chp6-p150-foreign-tributes": ("cand-4490", "cand-11971"),
        "st-chp6-p150-local-trade-industry": ("cand-4490",),
        "st-chp6-p150-ambassador-benefice-policy": ("cand-11972", "cand-11973"),
        "st-chp6-p150-rome-tolerates-revenue-loss": ("cand-4490", "cand-6292", "cand-6294"),
        "st-chp6-p150-navona-protest-rhymes": ("cand-6295", "cand-3455"),
        "st-chp6-p150-taxes-and-resentment": ("cand-11974", "cand-11975"),
        "st-chp6-p150-rhyme-demands-bread": ("cand-6295",),
        "st-chp6-p150-academy-director-proposals": ("cand-6296", "cand-0007"),
        "st-chp6-p150-accademia-financial-difficulties": ("cand-0007", "cand-3464"),
        "st-chp6-p150-monumental-ambition-persists": ("cand-4490",),
        "st-chp6-p150-papal-response-unlikely": ("cand-1819", "cand-5964", "cand-6295"),
        "st-chp6-p150-small-enterprises-suffer": ("cand-4490",),
        "st-chp6-p150-artists-begin-to-suffer": ("cand-11976",),
        "st-chp6-p150-dealers-and-bamboccianti": ("cand-0125",),
        "st-chp6-p150-preti-finds-artists-unemployed": ("cand-2056", "cand-11976", "cand-4490"),
        "st-chp6-p150-burial-cost-dispute": ("cand-1496", "cand-1814", "cand-1819", "cand-6297"),
        "st-chp6-p150-coffin-refusal": ("cand-1496", "cand-1814", "cand-1819", "cand-6297"),
        "st-chp6-p150-agostino-raphael-friendship": ("cand-0663", "cand-2098"),
        "st-chp6-p150-alexander-accession-patronage": ("cand-6298", "cand-0665"),
        "st-chp6-p150-alexander-friendship-partial": ("cand-0665", "cand-6301", "cand-4730", "cand-0209"),
        "st-chp6-p150-alexander-legate-in-cologne": ("cand-0665", "cand-6300"),
        "st-chp6-p150-alexander-wrote-agostino-life": ("cand-0665", "cand-0663", "cand-6299"),
        "st-chp6-p150-camillo-holiness-quote": ("cand-1814", "cand-1819"),
        "st-chp6-p150-fabio-descended-from-agostino": ("cand-0665", "cand-0663"),
        "st-chp6-p150-olimpia-heiress-quote": ("cand-1496",),
    }
    if any(not set(ids) <= candidates_by_id for ids in mention_candidates.values()):
        raise SystemExit("a planned statement refers to a missing candidate")

    def decide(sid: str, subject: str | None, object_: str | None, predicate: str,
               claim: str, relation: bool, qualification: str, note: str,
               mentioned: tuple[str, ...] | None = None) -> None:
        row = by_id[sid]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_
        row["predicate"] = predicate
        row["original_quote"] = quotes[sid]
        q = row["qualifiers"]
        q.update({"claim": claim, "relation_candidate": relation,
                  "relation_candidate_note": note, "qualification": qualification,
                  "mentioned_candidate_ids": list(mentioned or mention_candidates[sid])})

    decide("st-chp6-p150-foreign-tributes", "cand-4490", "cand-11971",
        "rome_relied_on_external_tributes_that_began_to_dry_up",
        "Haskell says Rome had long relied on tributes from abroad and that these began to dry up.", True,
        "The payers, territories, and sums are not identified; the effect of mercantilist doctrines is recorded in a separate statement.",
        "Explicit source-attributed economic relation between Rome and an unspecified external tribute flow.")
    decide("st-chp6-p150-local-trade-industry", "cand-4490", None,
        "rome_trade_and_industry_negligible_with_indirect_effects_of_italian_collapse",
        "Haskell says trade and industry in Rome were negligible, so the wider Italian economic collapse affected the city only indirectly.", False,
        "This is an authorial scalar characterization; the cross-page sentence begins at p.149 L43.",
        FALSE_NOTE)
    decide("st-chp6-p150-ambassador-benefice-policy", "cand-11972", "cand-11973",
        "rulers_prevent_benefice_income_from_leaving_their_territories",
        "The unnamed Venetian ambassador, writing in 1660 as quoted by Haskell, says rulers prevent income from ecclesiastical benefices from leaving their territories for foreigners.", True,
        "This universalized policy claim remains attributed to the ambassador; no specific rulers, territories, or revenues are identified. Haskell cites Barozzi e Berchet, II, p. 214, not independently read.",
        "The quotation explicitly attributes this policy relation to rulers, while retaining the speaker and secondhand evidence status.")
    decide("st-chp6-p150-rome-tolerates-revenue-loss", None, None,
        "unnamed_people_at_rome_patiently_endured_revenue_loss",
        "The ambassador’s quotation says unnamed people at Rome endured their disappointment patiently to avoid worse troubles; Haskell adds that the troubles came nonetheless.", False,
        "The pronoun 'they' has no secure individual or group referent in the passage; do not use Rome, the ambassador, or benefices as actor endpoints.",
        FALSE_NOTE, ("cand-4490", "cand-6292", "cand-6294"))
    decide("st-chp6-p150-navona-protest-rhymes", "cand-6295", "cand-3455",
        "anonymous_rhymes_found_on_stones_during_piazza_navona_reconstruction",
        "Haskell says that during the reconstruction of Piazza Navona, poignant and bitter rhymes were found attached to stones.", True,
        "The author, exact stones, and independent source wording remain unidentified; footnote 2 cites Gigli, p. 233, not independently read.",
        "The text-to-place association is explicit in Haskell's account; the relation remains source-attributed.")
    decide("st-chp6-p150-taxes-and-resentment", "cand-11974", "cand-11975",
        "roman_public_resented_papal_palace_and_square_spending_amid_tax_hardship",
        "Haskell says sudden taxes and resulting hardship led the public to resent sums spent on building and decorating papal palaces and squares.", True,
        "The public is unnamed; no individual building, square, expenditure amount, or taxpayer is identified.",
        "The source explicitly links a source-defined public group to the named category of papal building expenditure.")
    decide("st-chp6-p150-rhyme-demands-bread", "cand-6295", None,
        "anonymous_verse_demands_bread_over_obelisks_and_fountains",
        "The anonymous verse rejects obelisks and fountains as priorities and repeats a demand for bread.", False,
        "This records the quoted text's content; the verse does not name a person or institution it addresses.",
        FALSE_NOTE)
    decide("st-chp6-p150-academy-director-proposals", "cand-6296", "cand-0007",
        "unidentified_accademia_director_proposed_reforms_and_only_a_few_were_implemented",
        "The unidentified director tried to restore the Accademia di S. Luca’s fortunes and proposed arrangements, but Haskell says only a few were implemented.", True,
        "The director is unnamed; Haskell cites the quotation to Missirini, p. 116, not independently read.",
        "The quoted account explicitly connects the director's proposals with the Accademia.")
    decide("st-chp6-p150-accademia-financial-difficulties", "cand-3464", "cand-0007",
        "barberini_endowed_accademia_di_s_luca_before_1648",
        "Haskell says the Barberini had well endowed the Accademia di S. Luca a few years before its serious difficulties in 1648.", True,
        "The family reference is collective and the amount and date of the endowment are not given; the Academy's 1648 difficulties are recorded separately.",
        "The sentence explicitly attributes the Academy's earlier endowment to the Barberini family.")
    decide("st-chp6-p150-monumental-ambition-persists", "cand-4490", None,
        "haskell_characterizes_rome_grand_adornment_as_too_deep_rooted_to_be_deterred",
        "Haskell argues that Rome’s grand adornment was too deep-rooted an ambition to be deterred by a starving population.", False,
        "This is the author's interpretive generalization; the population and individual undertakings are not bounded here.",
        FALSE_NOTE)
    decide("st-chp6-p150-papal-response-unlikely", "cand-1819", None,
        "haskell_says_pope_and_courtiers_unlikely_to_take_bread_protest_as_a_hint",
        "Haskell says the Pope and his courtiers were unlikely to take the bread protest as a hint or warning.", False,
        "This is Haskell's interpretive prediction, not a documented response; the court is mentioned but is not the Pope's relational object.",
        FALSE_NOTE)
    decide("st-chp6-p150-small-enterprises-suffer", "cand-4490", None,
        "haskell_generalizes_that_smaller_enterprises_suffered_while_large_undertakings_continued",
        "Haskell generalizes that smaller enterprises suffered while large, showy undertakings continued.", False,
        "No particular small enterprise beyond the Academy example is identified in this generalization.",
        FALSE_NOTE)
    decide("st-chp6-p150-artists-begin-to-suffer", "cand-11976", None,
        "unnamed_artists_in_rome_began_to_suffer_during_economic_hardship",
        "Haskell says artists in Rome, first minor and later more established, began to suffer.", False,
        "This is a group-level condition, not a relation to Rome as an actor; the source-defined group is kept distinct from cand-3540.",
        FALSE_NOTE)
    decide("st-chp6-p150-dealers-and-bamboccianti", "cand-0125", None,
        "art_dealers_began_to_play_an_important_role_in_rome",
        "Haskell says art dealers began to play an important role.", False,
        "The adjacent statement about complaints concerning the bamboccianti is split out; the passage does not say dealers made those complaints.",
        FALSE_NOTE)
    decide("st-chp6-p150-preti-finds-artists-unemployed", "cand-2056", "cand-11976",
        "preti_found_many_unnamed_rome_artists_unemployed_on_arrival",
        "Haskell reports that Mattia Preti found many of the artists unemployed when he came to Rome in the mid-1640s.", True,
        "The artists are not individually identified; footnote 4 cites De Dominici, IV, p. 19, not independently read. The OCR form of the period is preserved.",
        "The source explicitly relates Preti's observation to the unnamed artist group and its unemployment state.")
    decide("st-chp6-p150-burial-cost-dispute", "cand-1496", "cand-1814",
        "donna_olimpia_and_camillo_quarreled_over_innocent_x_burial_costs",
        "Haskell says Donna Olimpia and Prince Camillo quarreled over who should be charged for Innocent X’s burial.", True,
        "This remains Haskell's account; the charged description of the corpse and dispute is not independently verified here.",
        "The source explicitly identifies the mother and son as the two parties to the burial-cost dispute.")
    decide("st-chp6-p150-coffin-refusal", "cand-1496", "cand-1819",
        "donna_olimpia_refused_to_pay_for_innocent_x_coffin_in_1655",
        "Haskell says Donna Olimpia refused to pay for a coffin for Innocent X when he died in January 1655.", True,
        "The same sentence attributes refusal to Camillo, recorded separately; footnote 5 cites Pastor, XIV, p. 37, not independently read.",
        "The source explicitly attributes a refusal to Donna Olimpia and identifies Innocent X as the intended recipient of the coffin.",
        ("cand-1496", "cand-1819", "cand-1814", "cand-6297"))
    decide("st-chp6-p150-agostino-raphael-friendship", "cand-0663", "cand-2098",
        "agostino_chigi_was_a_friend_of_raphael",
        "Haskell says Agostino Chigi’s friendship with Raphael was legendary.", True,
        "The source's 'legendary' characterization is retained; no particular encounter is documented here.",
        "The text explicitly identifies both people and their friendship.")
    decide("st-chp6-p150-alexander-accession-patronage", "cand-6298", "cand-0665",
        "fabio_chigi_accession_removed_personal_obstacles_to_enlightened_patronage",
        "Haskell says Fabio Chigi’s accession as Pope Alexander VII removed personal obstacles to enlightened patronage.", True,
        "The obstacles and beneficiaries are not identified; 'enlightened patronage' is Haskell's evaluative wording.",
        "The event is explicitly linked to its attributed effect on Fabio Chigi's patronage context.")
    decide("st-chp6-p150-alexander-friendship-partial", "cand-0665", "cand-6301",
        "fabio_chigi_was_intimate_friend_of_urban_viii_court_circle_before_legation",
        "Haskell’s sentence, completed at p.151 L60–61, says Fabio Chigi had been an intimate friend of the circle around Urban VIII’s court before his legation in Cologne.", True,
        "The p.150 fragment is completed by the exact continuation in the next segment; the circle is unnamed and distinct from the court institution.",
        "This is the cross-page relation already completed by the linked p.151 statement; preserve both source anchors without merging the segments.",
        ("cand-0665", "cand-6301", "cand-4730", "cand-0209"))
    friendship_q = by_id["st-chp6-p150-alexander-friendship-partial"]["qualifiers"]
    friendship_q.update({
        "continuation_quote": "the circle of poets, intellectuals and artists which gravitated round the court of Urban\nVIII",
        "continuation_source_segment_id": NEXT_SEGMENT,
        "continuation_source_line_start": 60,
        "continuation_source_line_end": 61,
        "cross_reference_segments": [{"segment_id": NEXT_SEGMENT, "source_line_start": 60, "source_line_end": 61}],
        "continuation_resolved_by_statement_id": "st-chp6-p151-alexander-circle-friendship",
    })
    decide("st-chp6-p150-alexander-legate-in-cologne", "cand-0665", "cand-6300",
        "fabio_chigi_served_as_papal_legate_in_cologne_for_thirteen_years",
        "Haskell says Fabio Chigi spent thirteen years as Papal Legate in Cologne before his period of intimacy with the Urban VIII court circle.", True,
        "The sentence continues across the page break; exact start and end dates are not supplied.",
        "The office-holder, office, place, and stated duration are explicit in the source.")
    decide("st-chp6-p150-alexander-wrote-agostino-life", "cand-0665", "cand-6299",
        "fabio_chigi_authored_an_untitled_life_of_agostino_chigi",
        "Haskell says Fabio Chigi himself wrote a life of Agostino Chigi.", True,
        "No title, form, location, or publication history is supplied; footnote 6 cites Cugnoni, 1879–81, not independently read. The S0 OCR reads 'fife'; the print reads 'life'.",
        "The source explicitly attributes authorship of Agostino Chigi's life to Fabio Chigi.",
        ("cand-0665", "cand-0663", "cand-6299"))
    life_q = by_id["st-chp6-p150-alexander-wrote-agostino-life"]["qualifiers"]
    life_q["ocr_corrections"] = [{"source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md", "source_line": 57,
                                  "ocr": "fife", "print": "life", "basis": "CHP-6.pdf physical page 5."}]
    decide("st-chp6-p150-camillo-holiness-quote", "cand-1814", "cand-1819",
        "camillo_said_he_had_received_nothing_from_innocent_x",
        "Haskell quotes Camillo as saying that he had received nothing from Innocent X.", True,
        "This is Camillo's attributed denial, not independent confirmation that no transfers occurred; Haskell cites Pastor, XIV, p. 37, not independently read.",
        "The quoted statement explicitly concerns a claimed non-receipt between Camillo and Innocent X.")
    decide("st-chp6-p150-fabio-descended-from-agostino", "cand-0665", "cand-0663",
        "fabio_chigi_was_a_direct_descendant_of_agostino_chigi",
        "Haskell describes Fabio Chigi as a direct descendant of Agostino Chigi, called 'il Magnifico', and as a fabulously rich Sienese banker.", True,
        "The genealogy and wealth description are not independently verified here; the OCR misreads 'fabulously' and is retained in original_quote.",
        "The source explicitly asserts a direct genealogical relation between Fabio and Agostino Chigi.",
        ("cand-0665", "cand-0663", "cand-5203"))
    decide("st-chp6-p150-olimpia-heiress-quote", "cand-1496", None,
        "olimpia_denied_being_the_heiress_without_identifying_the_estate",
        "Haskell quotes Donna Olimpia replying that she was not the heiress, without identifying the estate or succession at issue.", False,
        "The missing referent prevents a supported heirship endpoint; do not infer one from the burial-cost context.",
        FALSE_NOTE)

    # Rebuild the two composite statements as separate source claims while preserving their original IDs.
    new_quote = quote_between(segment_text, "the process was intensified", "mercantilist doctrines made headway.")
    if norm(new_quote) not in norm(by_id["st-chp6-p150-foreign-tributes"]["original_quote"]):
        raise SystemExit("mercantilist statement quote no longer appears in the original source row")
    new_statements = [
        new_statement(NEW_STATEMENT_IDS[0], "cand-6293", "cand-11971",
            "mercantilist_doctrines_intensified_decline_of_rome_external_tributes",
            "Haskell says the drying up of Rome’s external tributes intensified as mercantilist doctrines made headway.",
            new_quote, 49, 49, ["cand-6293", "cand-11971"], True,
            "The causal explanation is Haskell's framing and is not independently established in this segment.",
            "Explicit source-attributed causal relation between the spread of a doctrine and decline of Rome's tribute flow."),
        new_statement(NEW_STATEMENT_IDS[1], "cand-0007", None,
            "accademia_di_s_luca_faced_great_difficulties_in_1648",
            "Haskell says the Accademia di S. Luca faced great difficulties in 1648.",
            quotes["st-chp6-p150-accademia-financial-difficulties"], 54, 54, ["cand-0007", "cand-3464"], False,
            "The Barberini endowment is captured by the separate relation statement; the amount and date are not given.", FALSE_NOTE),
        new_statement(NEW_STATEMENT_IDS[2], "cand-0174", None,
            "complaints_began_about_comparative_success_of_bamboccianti",
            "Haskell says serious complaints began to be made about the comparative success of the bamboccianti.",
            quote_between(segment_text, "the first serious complaints", "comparative success of the bamboccianti."),
            55, 55, ["cand-0174"], False,
            "The complainants are not named; adjacency to the dealer statement does not make dealers the complainants.", FALSE_NOTE),
        new_statement(NEW_STATEMENT_IDS[3], "cand-1814", "cand-1819",
            "camillo_refused_to_pay_for_innocent_x_coffin_in_1655",
            "Haskell says Prince Camillo Pamfili refused to pay for a coffin for Innocent X when he died in January 1655.",
            quotes["st-chp6-p150-coffin-refusal"], 56, 56,
            ["cand-1814", "cand-1819", "cand-1496", "cand-6297"], True,
            "The same sentence attributes refusal to Donna Olimpia, recorded separately; footnote 5 cites Pastor, XIV, p. 37, not independently read.",
            "The source explicitly attributes a refusal to Camillo and identifies Innocent X as the intended recipient of the coffin."),
    ]
    for row in new_statements:
        if row["statement_id"] in by_id or row["subject_candidate_id"] not in candidates_by_id:
            raise SystemExit(f"invalid new statement: {row['statement_id']}")
        if row["object_candidate_id"] and row["object_candidate_id"] not in candidates_by_id:
            raise SystemExit(f"invalid new statement endpoint: {row['statement_id']}")
        if not set(row["qualifiers"]["mentioned_candidate_ids"]) <= candidates_by_id:
            raise SystemExit(f"invalid new statement mention list: {row['statement_id']}")

    # Ensure all assigned endpoints and mentions exist after the planned candidate additions.
    for sid in TARGETS:
        row = by_id[sid]
        q = row["qualifiers"]
        if row.get("subject_candidate_id") and row["subject_candidate_id"] not in candidates_by_id:
            raise SystemExit(f"missing subject for {sid}")
        if row.get("object_candidate_id") and row["object_candidate_id"] not in candidates_by_id:
            raise SystemExit(f"missing object for {sid}")
        if not set(q.get("mentioned_candidate_ids", [])) <= candidates_by_id:
            raise SystemExit(f"missing mentioned candidate for {sid}")

    by_id.update({row["statement_id"]: row for row in new_statements})
    statements = [by_id[row["statement_id"]] for row in statements]
    statements.extend(new_statements)
    cov["note"] += (
        " p.150 physical page 5 was reviewed against CHP-6.pdf. The 25 previously unset statements are classified; "
        "the Rome tribute flow and mercantilist explanation, the ambassador’s attributed benefice-income policy, "
        "public resentment of papal building expenditure, the Accademia’s Barberini endowment, Preti’s observation, "
        "the burial dispute and two separate coffin refusals, and the Alexander VII cross-page relation are recorded. "
        "Four composite rows were atomized into four additional statements; six source-bounded term candidates and "
        "five mentions were added, and two artist mentions were remapped from cand-3540 to the p.150 group. "
        "The OCR reading 'fife' is retained in S0 and corrected only in S2."
    )

    outputs = {
        STATEMENTS: ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8"),
        CANDIDATES: csv_bytes(cfields, candidates + new_candidates, cbom),
        MENTIONS: csv_bytes(mfields, mentions + new_mentions, mbom),
        COVERAGE: csv_bytes(vfields, coverage, vbom),
    }
    totals = {
        "true": sum(row.get("qualifiers", {}).get("relation_candidate") is True for row in statements),
        "false": sum(row.get("qualifiers", {}).get("relation_candidate") is False for row in statements),
        "unset": sum(row.get("qualifiers", {}).get("relation_candidate") is None for row in statements),
    }
    summary = {
        "segment": SEGMENT, "statements_classified": len(TARGETS),
        "new_atomic_statements": len(new_statements),
        "relation_candidates_in_segment": sum(by_id[sid]["qualifiers"].get("relation_candidate") is True for sid in TARGETS)
            + sum(row["qualifiers"]["relation_candidate"] is True for row in new_statements),
        "non_relational_in_segment": sum(by_id[sid]["qualifiers"].get("relation_candidate") is False for sid in TARGETS)
            + sum(row["qualifiers"]["relation_candidate"] is False for row in new_statements),
        "candidates_added": CANDIDATE_IDS, "mentions_added": MENTION_IDS,
        "artist_mentions_remapped": sorted(artist_mentions), "totals_after": totals,
        "mode": "dry-run",
    }
    return outputs, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize p.150 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up affected tables, then atomically write reviewed results.")
    args = parser.parse_args()
    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
