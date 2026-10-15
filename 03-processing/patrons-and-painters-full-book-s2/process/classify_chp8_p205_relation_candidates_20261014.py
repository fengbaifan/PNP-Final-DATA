"""Classify and refine S2 statements for the p.205 Roomer passage."""
from __future__ import annotations

import argparse
import csv
import hashlib
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
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l23-28"
BACKUP_SUFFIX = ".bak-s2-chp8-p205-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "3572bb7ebcd894759cd4157a41585b2a96d758735cee0517c079a7250d15adf3",
    CANDIDATES: "cb12616c0975adb5a265db05570289418d6ca24a2be122eb8b2d3f07021689da",
    MENTIONS: "54dbd233e8d40b305c85c8ce59edb2d1bf1c6a2a11cd950954a5ff629629b7ae",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "927016e646ad420bf9f667b350e5937ba0fecf83bbcab992b7b5733703719db2"
UNSET_IDS = {
    "st-chp8-p205-roomer-daughter-entered-convent",
    "st-chp8-p205-roomer-devoted-to-carmelites",
    "st-chp8-p205-roomer-estate-and-collection-dispersal",
    "st-chp8-p205-roomer-favoured-caravaggists",
    "st-chp8-p205-roomer-hosted-neapolitan-nobility",
    "st-chp8-p205-roomer-lent-to-king-of-spain",
    "st-chp8-p205-roomer-lent-to-viceroys",
    "st-chp8-p205-roomer-lifespan-recovery-death",
    "st-chp8-p205-roomer-most-influential-patron",
    "st-chp8-p205-roomer-origin-residence-gallery",
    "st-chp8-p205-roomer-proverb",
    "st-chp8-p205-roomer-shipping-trade",
    "st-chp8-p205-roomer-survived-masaniello-revolt",
    "st-chp8-p205-roomer-taste-for-grotesque-subjects",
    "st-chp8-p205-sandrart-recalled-cato",
}
NEW_STATEMENT_IDS = {
    "st-chp8-p205-roomer-collection-dispersed",
    "st-chp8-p205-roomer-naples-social-context",
    "st-chp8-p205-roomer-died-in-1674",
    "st-chp8-p205-roomer-settled-in-naples",
    "st-chp8-p205-roomer-owned-outstanding-gallery",
    "st-chp8-p205-roomer-ships-reached-scandinavia",
    "st-chp8-p205-roomer-ships-reached-egypt",
    "st-chp8-p205-roomer-business-in-low-countries",
}
CANDIDATE_SPECS = [
    ("cand-12023", "Charitable recipients of most of Roomer's fortune (unnamed group)", "term", "Haskell says Roomer bequeathed most of his fortune to charity but identifies no recipient, institution, or charitable purpose.", 25),
    ("cand-12024", "Seven unidentified paintings by Ribera in Gaspar Roomer's collection", "work", "Source-defined group counted by Haskell; the titles and membership are not enumerated, and the Drunken Silenus and Flaying of Marsyas are not assigned as members here.", 28),
    ("cand-12025", "Three unidentified paintings by Caracciolo in Gaspar Roomer's collection", "work", "Source-defined group of three paintings; no titles, dates, or locations are given in this passage.", 28),
    ("cand-12026", "Three unidentified paintings by Massimo Stanzione in Gaspar Roomer's collection", "work", "Source-defined group of three paintings; no titles, dates, or locations are given in this passage.", 28),
    ("cand-12027", "Three unidentified paintings by Carlo Saraceni in Gaspar Roomer's collection", "work", "The artist's surname completes as Saraceni on p.206; no titles, dates, or locations are given here.", 28),
    ("cand-12028", "Neapolitan nobility entertained by Gaspar Roomer (source-estimated half)", "term", "Haskell estimates that Roomer entertained half the nobility; the individuals and basis for the estimate are not supplied.", 25),
]
MENTION_SPECS = [
    ("m-s2-chp8-p205-charity-recipients", "cand-12023", "charity", "Unspecified charitable recipients of most of Roomer's fortune."),
    ("m-s2-chp8-p205-seven-ribera-works", "cand-12024", "his seven Riberas", "Seven-work group attributed to Ribera; individual works are not identified here."),
    ("m-s2-chp8-p205-three-caracciolo-works", "cand-12025", "three paintings each by Caracciolo", "Three-work group attributed to Caracciolo."),
    ("m-s2-chp8-p205-three-stanzione-works", "cand-12026", "the young Massimo Stanzione", "The sentence says three paintings each by the artists in this list."),
    ("m-s2-chp8-p205-three-saraceni-works", "cand-12027", "Carlo", "Name fragment at the p.205 page break; the artist's surname completes as Saraceni on p.206."),
    ("m-s2-chp8-p205-roomer-hosted-nobility-group", "cand-12028", "half the nobility", "Source-estimated group entertained by Roomer at his residences."),
]


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
    import io
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
    segment_text = "\n".join(source_lines[22:28])
    if not segment or (segment["line_start"], segment["line_end"]) != (23, 28):
        raise SystemExit("p.205 segment metadata changed")
    if segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE] or segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.205 source asset or segment fingerprint changed")
    if sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.205 segment text changed since review")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("statement IDs are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_unset = {row["statement_id"] for row in page_rows if "relation_candidate" not in (row.get("qualifiers") or {})}
    if actual_unset != UNSET_IDS or len(page_rows) != 21:
        raise SystemExit(f"unexpected p.205 statement inventory: unset delta={sorted(actual_unset ^ UNSET_IDS)}, total={len(page_rows)}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("candidate or mention IDs are not unique")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12022:
        raise SystemExit("candidate sequence changed since the p.205 review")
    if {row[0] for row in CANDIDATE_SPECS} & set(candidate_by_id) or {row[0] for row in MENTION_SPECS} & set(mention_by_id):
        raise SystemExit("a planned candidate or mention ID already exists")

    new_candidates = []
    for candidate_id, name, kind, detail, line in CANDIDATE_SPECS:
        new_candidates.append({
            "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
            "index_page_range": "", "suggested_type": kind, "status": "open",
            "index_source_file": "", "sub_entry": "", "detail": detail,
            "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
        })
    new_keys = [(r["canonical_name"].casefold(), r["suggested_type"].casefold()) for r in new_candidates]
    old_keys = {(r["canonical_name"].casefold(), r["suggested_type"].casefold()) for r in candidates}
    if len(new_keys) != len(set(new_keys)) or old_keys.intersection(new_keys):
        raise SystemExit("planned candidate duplicates another candidate by canonical name/type")
    candidates.extend(new_candidates)
    candidate_by_id.update({r["candidate_id"]: r for r in new_candidates})

    new_mentions = []
    for mention_id, candidate_id, surface, note in MENTION_SPECS:
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"planned mention has no candidate: {mention_id}")
        starts = [i for i in range(len(segment_text)) if segment_text.startswith(surface, i)]
        if len(starts) != 1:
            raise SystemExit(f"mention surface is not unique in p.205 source text: {mention_id}: {surface!r}")
        start = starts[0]
        new_mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
        })
    mentions.extend(new_mentions)
    mention_by_id.update({r["mention_id"]: r for r in new_mentions})

    def excerpt(start_line: int, end_line: int, first: str, last: str) -> str:
        source = "\n".join(source_lines[start_line - 1:end_line])
        start, end = source.find(first), source.rfind(last)
        if start < 0 or end < start:
            raise SystemExit(f"expected source phrase missing at L{start_line}-L{end_line}: {first!r} ... {last!r}")
        return source[start:end + len(last)]

    def revise(statement_id: str, *, predicate: str, subject: str | None, object_id: str | None,
               claim: str, qualification: str, quote_text: str, start_line: int, end_line: int,
               mentioned: list[str], relation: bool, relation_note: str,
               open_reason: str | None = None, extra: dict | None = None,
               remove_qualifiers: tuple[str, ...] = ()) -> dict:
        row = by_id[statement_id]
        q = dict(row.get("qualifiers") or {})
        for key in remove_qualifiers:
            q.pop(key, None)
        source = "\n".join(source_lines[start_line - 1:end_line])
        if normalize(quote_text) not in normalize(source):
            raise SystemExit(f"statement quote does not match source: {statement_id}")
        q.update({
            "source_line_start": start_line, "source_line_end": end_line,
            "printed_page": 205, "pdf_physical_page": 3,
            "claim": claim, "speaker": q.get("speaker", "Haskell"),
            "text_layer": q.get("text_layer", "body"), "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation, "relation_candidate_note": relation_note,
        })
        if open_reason:
            q["open_endpoint_reason"] = open_reason
        else:
            q.pop("open_endpoint_reason", None)
        if extra:
            q.update(extra)
        row.update({"subject_candidate_id": subject, "object_candidate_id": object_id,
                    "predicate": predicate, "qualifiers": q, "original_quote": quote_text})
        return row

    def new_statement(statement_id: str, *, subject: str | None, object_id: str | None,
                      predicate: str, claim: str, qualification: str, quote_text: str,
                      start_line: int, end_line: int, mentioned: list[str],
                      relation: bool, relation_note: str, extra: dict | None = None) -> dict:
        source = "\n".join(source_lines[start_line - 1:end_line])
        if normalize(quote_text) not in normalize(source):
            raise SystemExit(f"new statement quote does not match source: {statement_id}")
        q = {
            "source_line_start": start_line, "source_line_end": end_line,
            "printed_page": 205, "pdf_physical_page": 3,
            "claim": claim, "speaker": "Haskell", "text_layer": "body",
            "qualification": qualification, "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation, "relation_candidate_note": relation_note,
        }
        if extra:
            q.update(extra)
        return {"statement_id": statement_id, "segment_id": SEGMENT_ID,
                "subject_candidate_id": subject, "object_candidate_id": object_id,
                "predicate": predicate, "qualifiers": q, "original_quote": quote_text,
                "origin": "book", "source_file": SOURCE_REL}

    revise(
        "st-chp8-p205-roomer-daughter-entered-convent", predicate="roomers_daughter_entered_carmelite_convent",
        subject="cand-7404", object_id="cand-7405",
        claim="Haskell reports that Roomer's only daughter entered one of the Carmelites' convents.",
        qualification="The daughter and convent are unnamed; the passage does not specify the convent's location.",
        quote_text=excerpt(25, 25, "the entry of his only daughter", "one of their convents."), start_line=25, end_line=25,
        mentioned=["cand-7404", "cand-7405", "cand-0563"], relation=True,
        relation_note="The source states a direct entry relation between Roomer's unnamed daughter and an unnamed Carmelite convent.",
    )
    revise(
        "st-chp8-p205-roomer-devoted-to-carmelites", predicate="roomer_donated_to_carmelite_churches",
        subject="cand-2223", object_id="cand-7411",
        claim="Haskell cites spectacular donations to Carmelite churches as evidence of Roomer's religious convictions and particular devotion to the Carmelites.",
        qualification="The churches are unnamed and are not identified as one institution; the devotional interpretation is Haskell's.",
        quote_text=excerpt(25, 25, "The strength ofliis religious convictions", "donations to their churches"), start_line=25, end_line=25,
        mentioned=["cand-2223", "cand-0563", "cand-7411"], relation=True,
        relation_note="Roomer's donations to the order's churches are explicit; the buildings are preserved as an unnamed group.",
    )
    revise(
        "st-chp8-p205-roomer-estate-and-collection-dispersal", predicate="roomer_bequeathed_most_fortune_to_charity",
        subject="cand-2223", object_id="cand-12023",
        claim="Haskell says Roomer left a vast fortune and bequeathed most of it to charity.",
        qualification="The recipient, amount, and charitable purposes are not specified beyond ‘most’ and the general term charity.",
        quote_text=excerpt(25, 25, "He left behind a vast fortune", "most of which he bequeathed to charity"), start_line=25, end_line=25,
        mentioned=["cand-2223", "cand-12023"], relation=True,
        relation_note="The bequest from Roomer to unspecified charitable recipients is explicit; no named institution is inferred.",
    )
    revise(
        "st-chp8-p205-roomer-favoured-caravaggists", predicate="roomer_was_fond_of_caravaggist_painters",
        subject="cand-2230", object_id="cand-7416",
        claim="Haskell says Roomer was especially fond of Caravaggist painters.",
        qualification="The painter group is not enumerated in this sentence.",
        quote_text=excerpt(28, 28, "Roomer was especially fond", "the Caravaggists:"), start_line=28, end_line=28,
        mentioned=["cand-2230", "cand-7416"], relation=True,
        relation_note="The source explicitly states Roomer's preference for the Caravaggists as a group.",
    )
    revise(
        "st-chp8-p205-roomer-hosted-neapolitan-nobility", predicate="roomer_entertained_neapolitan_nobility_at_residences",
        subject="cand-2223", object_id="cand-12028",
        claim="Haskell says Roomer entertained what he estimates as half the Neapolitan nobility, first at his palace on Via Monteoliveto, later at Palazzo della Stella or at one of his country houses.",
        qualification="‘Half’ is Haskell's estimate; the people and country houses are not named, and no exact guest list is supplied.",
        quote_text=excerpt(25, 25, "this rich foreign upstart entertained half the nobility", "one of his many country houses."), start_line=25, end_line=25,
        mentioned=["cand-2223", "cand-1722", "cand-3461", "cand-12028", "cand-7402", "cand-7403", "cand-11489"], relation=True,
        relation_note="The host and source-estimated guest group are explicit; the residences remain location qualifiers.",
        extra={"location_candidate_ids": ["cand-7402", "cand-7403", "cand-11489"]},
    )
    revise(
        "st-chp8-p205-roomer-lent-to-king-of-spain", predicate="roomer_lent_money_to_king_of_spain",
        subject="cand-2223", object_id="cand-7401",
        claim="Haskell says Roomer lent money even to the King of Spain.",
        qualification="The king is not identified by name or reign.",
        quote_text=excerpt(25, 25, "even to the King of Spain", "even to the King of Spain"), start_line=25, end_line=25,
        mentioned=["cand-2223", "cand-7401", "cand-4591"], relation=True,
        relation_note="The source directly names Roomer as lender and the unnamed King of Spain as borrower.",
    )
    revise(
        "st-chp8-p205-roomer-lent-to-viceroys", predicate="roomer_lent_money_to_viceroys",
        subject="cand-2223", object_id="cand-7408",
        claim="Haskell says Roomer lent money to unnamed viceroys.",
        qualification="The viceroys are a collective reference; neither their names nor offices are specified.",
        quote_text=excerpt(25, 25, "He lent money to the viceroys", "He lent money to the viceroys"), start_line=25, end_line=25,
        mentioned=["cand-2223", "cand-7408"], relation=True,
        relation_note="The lending relation is explicit, with the collective officeholders retained as an open group.",
    )
    revise(
        "st-chp8-p205-roomer-lifespan-recovery-death", predicate="roomer_recovered_from_plague",
        subject="cand-2223", object_id="cand-7406",
        claim="Haskell reports that Roomer recovered from the plague in 1656 and lived on for another twenty-six years.",
        qualification="The source reports recovery but gives no location or independent medical evidence; his death in 1674 is recorded separately.",
        quote_text=excerpt(25, 25, "He lived on, respected and successful", "recovering from the plague in 1656"), start_line=25, end_line=25,
        mentioned=["cand-2223", "cand-7406"], relation=True,
        relation_note="The statement connects Roomer to the specific 1656 plague episode by recovery; the later death date is a separate biographical claim.",
    )
    revise(
        "st-chp8-p205-roomer-most-influential-patron", predicate="ranked_as_most_influential_patron",
        subject="cand-2223", object_id=None,
        claim="Haskell ranks Roomer as by far the most important and influential of the patrons discussed on the preceding page.",
        qualification="This is a comparative authorial ranking, not a discrete relation; ‘all such patrons’ refers to the source-defined translocal patron group.",
        quote_text=excerpt(24, 24, "By far the most important", "Gaspar Roomer.1"), start_line=24, end_line=24,
        mentioned=["cand-2223", "cand-7399"], relation=False,
        relation_note="A comparative judgment is retained as a claim, not encoded as an entity-to-entity edge.",
    )
    revise(
        "st-chp8-p205-roomer-origin-residence-gallery", predicate="roomer_born_in_antwerp",
        subject="cand-2223", object_id="cand-4983",
        claim="Haskell says Roomer was born of a good family in Antwerp toward the end of the sixteenth century.",
        qualification="The family is not named, and the date remains approximate.",
        quote_text=excerpt(24, 24, "He was born of a good family in Antwerp", "end of the sixteenth century"), start_line=24, end_line=24,
        mentioned=["cand-2223", "cand-4983"], relation=True,
        relation_note="The source directly states Roomer's birth place; the family description and approximate date remain qualifications.",
    )
    revise(
        "st-chp8-p205-roomer-proverb", predicate="reported_proverb_used_against_persistent_borrowers",
        subject=None, object_id=None,
        claim="Haskell reports the proverb ‘Do you take me for a Roomer?’ as a phrase used to counter persistent borrowers.",
        qualification="The passage reports the saying but does not establish its origin or a formal relation to Roomer.",
        quote_text=excerpt(25, 25, "the proverb ‘Do you take me for a Roomer?’", "persistent borrowers."), start_line=25, end_line=25,
        mentioned=["cand-7418", "cand-2223"], relation=False,
        relation_note="The proverb's reported wording and pragmatic use are preserved as a cultural-linguistic claim, not an entity relation.",
    )
    revise(
        "st-chp8-p205-roomer-shipping-trade", predicate="roomer_shipowner_trader_and_wealthy_businessman",
        subject="cand-2223", object_id=None,
        claim="Haskell reports that Roomer's shipowning and trading activities brought him a fortune valued at five million ducats.",
        qualification="The valuation is Haskell's report; the route to Scandinavia and Egypt and the Low Countries business connection are recorded separately.",
        quote_text=excerpt(24, 24, "Some years later his activities", "five million ducats."), start_line=24, end_line=24,
        mentioned=["cand-2223"], relation=False,
        relation_note="Occupation and estimated wealth are retained as biographical information; the explicitly named route and business relations are separated below.",
    )
    revise(
        "st-chp8-p205-roomer-survived-masaniello-revolt", predicate="roomer_survived_danger_during_masaniello_revolt",
        subject="cand-2229", object_id="cand-1559",
        claim="Haskell says Roomer faced danger during the 1647 revolt of Masaniello but was spared after the public remembered his earlier generosity to nearby working men and he was ready to bribe their present leaders.",
        qualification="The source does not name the workers or leaders and gives no independent evidence for the causal account.",
        quote_text=excerpt(25, 25, "During the revolt of Masaniello", "less cautious or less benevolent."), start_line=25, end_line=25,
        mentioned=["cand-2229", "cand-1559", "cand-4150", "cand-7409", "cand-7410"], relation=True,
        relation_note="The person and revolt event are explicit; the reported generosity and readiness to bribe leaders remain Haskell's explanation for his survival.",
    )
    revise(
        "st-chp8-p205-roomer-taste-for-grotesque-subjects", predicate="authorial_characterization_of_roomer_artistic_taste",
        subject="cand-2231", object_id=None,
        claim="Haskell characterizes Roomer as having a taste for grotesque, dark, and cruel subjects that Neapolitan painters could satisfy.",
        qualification="This is an authorial characterization, framed by comparison with Flemings and Naples painters; no specific subject or work is identified.",
        quote_text=excerpt(26, 26, "Like many a Fleming", "the painters of Naples were well able to satisfy."), start_line=26, end_line=26,
        mentioned=["cand-2231", "cand-1722"], relation=False,
        relation_note="The broad characterization of artistic taste is preserved as a claim, not a specific relation to an identified work or painter.",
    )
    revise(
        "st-chp8-p205-sandrart-recalled-cato", predicate="sandrart_recalled_seeing_cato_painting",
        subject="cand-2353", object_id="cand-7414",
        claim="Haskell reports that Sandrart recalled seeing a painting of a Cato shown in the act of suicide.",
        qualification="The painting's maker, title, medium, and version are unspecified; Cato's identity is not resolved.",
        quote_text=excerpt(27, 27, "Sandrart recalled seeing a Cato", "with his hands’.4"), start_line=27, end_line=27,
        mentioned=["cand-2353", "cand-7414", "cand-7415"], relation=True,
        relation_note="Sandrart's recollection and the unidentified painting are distinct endpoints; Haskell is the reporting source.",
        extra={"nested_speaker": "Joachim von Sandrart, as recalled by Haskell"},
    )

    # Correct the index subentry's object type: this entry identifies Roomer as a person, not an event.
    candidate_by_id["cand-2229"]["suggested_type"] = "person"
    candidate_by_id["cand-2229"]["detail"] = "Index subentry for Gaspar Roomer's escape during the 1647 Masaniello revolt; the subject is the person Gaspar Roomer."

    # Collection endpoints are work groups; artists are creator qualifiers, not objects of ownership.
    ownership_specs = [
        ("st-chp8-p205-roomer-owned-seven-ribera-paintings", "cand-12024", "cand-2140", 7, "seven paintings by Ribera"),
        ("st-chp8-p205-roomer-owned-three-caracciolo-paintings", "cand-12025", "cand-0541", 3, "three paintings by Caracciolo"),
        ("st-chp8-p205-roomer-owned-three-stanzione-paintings", "cand-12026", "cand-2506", 3, "three paintings by Massimo Stanzione"),
        ("st-chp8-p205-roomer-owned-three-saraceni-paintings-open", "cand-12027", "cand-2358", 3, "three paintings by Carlo Saraceni"),
    ]
    for statement_id, work_group, artist, quantity, label in ownership_specs:
        row = by_id[statement_id]
        row["object_candidate_id"] = work_group
        q = row.setdefault("qualifiers", {})
        q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), work_group, artist]))
        q["creator_candidate_id"] = artist
        q["work_quantity"] = quantity
        q["relation_candidate_note"] = f"The source attributes {label} to Roomer's collection; the artist is a creator qualifier and the owned works are a separate source-defined group."
        if "saraceni" in statement_id:
            q["continuation_status"] = "completed_on_next_page"
            q["continuation_completed_in_segment_id"] = "chp-8:08_CHP-8_sec_i:l30-41"
            q["continuation_source_lines"] = [31]

    new_rows = [
        new_statement(
            "st-chp8-p205-roomer-collection-dispersed", subject="cand-2223", object_id="cand-7407",
            predicate="roomers_painting_collection_was_quickly_dispersed",
            claim="Haskell says Roomer left more than 1,500 paintings, which were quickly dispersed.",
            qualification="The works are not individually identified; the passage does not say when or by whom they were dispersed.",
            quote_text=excerpt(25, 25, "over 1500 paintings", "quickly dispersed,"), start_line=25, end_line=25,
            mentioned=["cand-2223", "cand-7407"], relation=True,
            relation_note="The source identifies Roomer's collection and reports its later dispersal; no individual works or dispersal agent are inferred.",
        ),
        new_statement(
            "st-chp8-p205-roomer-naples-social-context", subject=None, object_id=None,
            predicate="authorial_characterization_of_neapolitan_social_values",
            claim="Haskell characterizes Naples as a city where titles and feudal virtues counted more than elsewhere in Italy.",
            qualification="This is a broad authorial comparison and not a measurable claim about every Neapolitan or Italian social setting.",
            quote_text=excerpt(25, 25, "in a city where titles", "more than anywhere else in Italy"), start_line=25, end_line=25,
            mentioned=["cand-1722", "cand-3461"], relation=False,
            relation_note="The statement is an authorial social characterization, not an entity-to-entity relation.",
        ),
        new_statement(
            "st-chp8-p205-roomer-died-in-1674", subject="cand-2223", object_id=None,
            predicate="roomer_died_in_1674",
            claim="Haskell says Roomer died in 1674 at a very old age.",
            qualification="The age is qualitative and no exact age is supplied.",
            quote_text=excerpt(25, 25, "and died, a very old man", "in 1674."), start_line=25, end_line=25,
            mentioned=["cand-2223"], relation=False,
            relation_note="This is a biographical date and characterization rather than an entity-to-entity relation.",
        ),
        new_statement(
            "st-chp8-p205-roomer-settled-in-naples", subject="cand-2223", object_id="cand-1722",
            predicate="roomer_settled_in_naples_by_1634",
            claim="Haskell says Roomer had long been settled in Naples by 1634.",
            qualification="The passage gives an approximate duration but no exact arrival date.",
            quote_text=excerpt(24, 24, "by 1634 he had already been long settled in Naples", "Naples"), start_line=24, end_line=24,
            mentioned=["cand-2223", "cand-1722"], relation=True,
            relation_note="The source explicitly places Roomer in Naples by 1634; no earlier arrival date is inferred.",
        ),
        new_statement(
            "st-chp8-p205-roomer-owned-outstanding-gallery", subject="cand-2223", object_id="cand-7407",
            predicate="roomer_owned_outstanding_picture_gallery",
            claim="Haskell says Roomer owned an outstanding picture gallery in Naples by 1634.",
            qualification="The gallery is not named or inventoried; Naples is the clause's residence context, not an explicitly separate gallery address.",
            quote_text=excerpt(24, 24, "was the owner of an outstanding picture gallery", "picture gallery"), start_line=24, end_line=24,
            mentioned=["cand-2223", "cand-1722", "cand-7407"], relation=True,
            relation_note="The source explicitly identifies Roomer as owner of the gallery; it is kept distinct from its later reported 1,500 paintings.",
        ),
        new_statement(
            "st-chp8-p205-roomer-ships-reached-scandinavia", subject="cand-2223", object_id="cand-5521",
            predicate="roomers_ships_ranged_to_scandinavia",
            claim="Haskell says Roomer's ships ranged as far as Scandinavia.",
            qualification="No port, voyage, or individual vessel is identified.",
            quote_text=excerpt(24, 24, "His ships ranged as far afield as Scandinavia", "Scandinavia"), start_line=24, end_line=24,
            mentioned=["cand-2223", "cand-5521"], relation=True,
            relation_note="The source names Scandinavia as the farthest extent of the ships' range; it does not provide a route.",
        ),
        new_statement(
            "st-chp8-p205-roomer-ships-reached-egypt", subject="cand-2223", object_id="cand-7420",
            predicate="roomers_ships_ranged_to_egypt",
            claim="Haskell says Roomer's ships ranged as far as Egypt.",
            qualification="No port, voyage, or individual vessel is identified.",
            quote_text=excerpt(24, 24, "and Egypt", "Egypt"), start_line=24, end_line=24,
            mentioned=["cand-2223", "cand-7420"], relation=True,
            relation_note="The source names Egypt as one extent of the ships' range; it does not provide a route.",
        ),
        new_statement(
            "st-chp8-p205-roomer-business-in-low-countries", subject="cand-2223", object_id="cand-4342",
            predicate="roomer_carried_most_business_with_low_countries",
            claim="Haskell says most of Roomer's business was carried on with his native Low Countries.",
            qualification="The source gives no business partners, ports, or trade volume.",
            quote_text=excerpt(24, 25, "most of his business was carried on with his native", "Low Countries."), start_line=24, end_line=25,
            mentioned=["cand-2223", "cand-4342"], relation=True,
            relation_note="The geographic business connection is explicit; ‘most’ and ‘native’ are preserved as source qualifications.",
        ),
    ]
    for row in new_rows:
        if row["statement_id"] in by_id:
            raise SystemExit(f"new statement ID collision: {row['statement_id']}")
        by_id[row["statement_id"]] = row
    statements = list(by_id.values())

    for row in statements:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        q = row.get("qualifiers") or {}
        for candidate_id in (row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])):
            if candidate_id and candidate_id not in candidate_by_id:
                raise SystemExit(f"p.205 statement has unresolved candidate: {row['statement_id']} -> {candidate_id}")
        if q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"true p.205 relation candidate has an unexplained open endpoint: {row['statement_id']}")
    expected_counts = {"statements": 14224, "candidates": 12006, "mentions": 28070, "true": 8901, "false": 3458, "unset": 1865}
    actual_counts = {
        "statements": len(statements), "candidates": len(candidates), "mentions": len(mentions),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in statements),
        "unset": sum("relation_candidate" not in (row.get("qualifiers") or {}) for row in statements),
    }
    if actual_counts != expected_counts:
        raise SystemExit(f"unexpected post-write counts: {actual_counts}")

    outputs = {STATEMENTS: jsonl_bytes(statements), CANDIDATES: csv_bytes(candidate_fields, candidates), MENTIONS: csv_bytes(mention_fields, mentions)}
    result = {
        "mode": "apply" if args.apply else "dry_run", "segment_id": SEGMENT_ID,
        "unclassified_statement_rows_reviewed": len(UNSET_IDS),
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [row["mention_id"] for row in new_mentions],
        "corrected_candidate_type": {"cand-2229": "event -> person"},
        "work_group_endpoints_corrected": {row[0]: row[1] for row in ownership_specs},
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
