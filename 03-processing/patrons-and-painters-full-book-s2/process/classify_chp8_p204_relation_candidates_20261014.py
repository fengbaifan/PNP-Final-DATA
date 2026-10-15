"""Classify and refine S2 statements for p.204, preserving the OCR source."""
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
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l14-21"
BACKUP_SUFFIX = ".bak-s2-chp8-p204-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "6f63472b4c3cf71f5293c03b76ae71bc2bfc2165b438d67e40adec4f6688ad0c",
    CANDIDATES: "dc9dd0a9b118005b1593e1f8387bcd50c90d88f8fa1e7577678bc0e886e033c8",
    MENTIONS: "afd1f0187e3d3d317f99bbc67657993938e983fb11929d8a0f875b57d3de7282",
    SOURCE: "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf",
}
EXPECTED_SEGMENT_SHA = "5cd6b281b486fa731569479441cc2a31e7ee373c60180eb5cde46840e4a602bc"
UNSET_IDS = {
    "st-chp8-p204-crespi-biographer-evaluates-ricci-treatment",
    "st-chp8-p204-crespi-paintings-reflect-travel-influences",
    "st-chp8-p204-cross-regional-pictures-and-patrons",
    "st-chp8-p204-early-eighteenth-century-revival",
    "st-chp8-p204-italian-cities-remained-provincial",
    "st-chp8-p204-local-traditions-and-taste-stagnation",
    "st-chp8-p204-naples-lawyers-supported-arts",
    "st-chp8-p204-provincial-patrons-could-not-recreate-rome",
    "st-chp8-p204-ricci-admired-contemporary-artists",
    "st-chp8-p204-ricci-dealer-terms",
    "st-chp8-p204-ricci-leading-patron",
    "st-chp8-p204-ricci-sent-crespi-to-absorb-influences",
    "st-chp8-p204-roman-collections-broadened-appreciation",
    "st-chp8-p204-rome-only-competing-italian-capital",
    "st-chp8-p204-valletta-friend-of-shaftesbury",
    "st-chp8-p204-valletta-patron-of-giordano",
    "st-chp8-p204-valletta-patron-of-solimena",
    "st-chp8-p204-valletta-professions",
}
RENAMED_IDS = {
    "st-chp8-p204-cross-regional-pictures-and-patrons": "st-chp8-p204-neapolitan-picture-rare-in-bologna",
}
NEW_STATEMENT_IDS = {
    "st-chp8-p204-venetian-picture-rare-in-genoa",
    "st-chp8-p204-translocal-patrons-collected-foreign-works",
    "st-chp8-p204-foreign-intervention-averted-stagnation",
    "st-chp8-p204-local-traditions-stagnated-taste",
}
CANDIDATE_SPECS = [
    ("cand-12014", "Widely differing influences absorbed by Crespi during Ricci's visits", "term", "The passage says Crespi absorbed varied influences on long visits to Venice and Central Italy but does not identify the influences individually.", 15),
    ("cand-12015", "Unidentified contemporary Neapolitan picture in Haskell's Bologna comparison", "work", "A source-defined picture category used in the comparison; no painter, title, date, or individual work is identified.", 21),
    ("cand-12016", "Works by foreign artists collected by translocal Italian patrons (group)", "work", "The passage says a few expatriate or citizen patrons included works by foreign artists in their collections; no works are individually identified.", 21),
    ("cand-12017", "Italian nobility and professional classes sustaining local painting schools (group)", "term", "Source-defined social groups credited with keeping valuable local schools alive during most of the seventeenth century; members are not enumerated.", 21),
    ("cand-12018", "Lawyers prominent in Naples cultural and artistic life (group)", "term", "The passage describes Naples lawyers collectively; no individual lawyers are named in this sentence.", 17),
    ("cand-12019", "Contemporary artists appreciated by Giovanni Ricci (group)", "term", "A source-defined group of contemporary artists Ricci appreciated, with Burrini and the young Crespi given as examples rather than an exhaustive list.", 15),
    ("cand-12020", "Main towns in European nation-states in Haskell's prestige comparison (group)", "", "The passage compares Rome's prestige with the principal towns of European nation-states; it does not enumerate them.", 20),
    ("cand-12021", "Unidentified Venetian picture in Haskell's Genoa comparison", "work", "A source-defined example of a Venetian picture rarely found in Genoa; no painter, title, date, or individual work is identified.", 21),
    ("cand-12022", "Wide artistic appreciation and new combinations stimulated by Roman collections", "term", "Haskell identifies broad appreciation and new combinations of artistic sensibility as the outcome; the classical-Venetian synthesis is one example.", 21),
]
MENTION_SPECS = [
    ("m-s2-chp8-p204-influence-group", "cand-12014", "a number of widely differing influences", "Unspecified influences Crespi was sent to absorb during visits to Venice and Central Italy."),
    ("m-s2-chp8-p204-neapolitan-picture-in-bologna", "cand-12015", "a picture by a contemporary Neapolitan painter", "Unidentified contemporary Neapolitan picture in the Bologna rarity comparison."),
    ("m-s2-chp8-p204-foreign-artworks-group", "cand-12016", "works by foreign artists", "Unidentified works included in translocal patrons' collections."),
    ("m-s2-chp8-p204-local-patrons-group", "cand-12017", "extravagant but somewhat unimaginative nobility and professional classes", "The two social classes credited with sustaining local painting schools."),
    ("m-s2-chp8-p204-naples-lawyers-group", "cand-12018", "the lawyers", "The unnamed professional group described as prominent in Naples arts support."),
    ("m-s2-chp8-p204-ricci-artists-group", "cand-12019", "many contemporary artists", "Artists appreciated by Ricci; Burrini and Crespi are examples in the following phrase."),
    ("m-s2-chp8-p204-european-towns-group", "cand-12020", "the main towns in the nation states of Europe", "The non-enumerated group used in Haskell's comparison of prestige."),
    ("m-s2-chp8-p204-venetian-picture-in-genoa", "cand-12021", "one by a Venetian", "Unidentified Venetian picture in the Genoa rarity comparison."),
    ("m-s2-chp8-p204-collections-artistic-outcome", "cand-12022", "a wide range of appreciation and new combinations of artistic sensibility", "The broader outcome Haskell attributes to the Roman collections; the Cassiano dal Pozzo synthesis is an example."),
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
    segment_rows = read_jsonl(SEGMENTS)
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (segment["line_start"], segment["line_end"]) != (14, 21):
        raise SystemExit("p.204 source segment metadata changed")
    if segment.get("asset_sha256") != EXPECTED_HASHES[SOURCE]:
        raise SystemExit("p.204 source asset fingerprint does not match the segment registry")
    segment_text = "\n".join(source_lines[13:21])
    if segment.get("sha256") != EXPECTED_SEGMENT_SHA or sha(segment_text.encode("utf-8")) != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.204 segment text changed since review")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("statement IDs are not unique")
    segment_rows_now = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    actual_unset = {
        row["statement_id"] for row in segment_rows_now
        if "relation_candidate" not in (row.get("qualifiers") or {})
    }
    if actual_unset != UNSET_IDS or len(segment_rows_now) != 18:
        raise SystemExit(f"unexpected p.204 statement inventory: unset delta={sorted(actual_unset ^ UNSET_IDS)}, total={len(segment_rows_now)}")
    if NEW_STATEMENT_IDS & set(by_id):
        raise SystemExit("a planned statement ID already exists")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise SystemExit("candidate or mention IDs are not unique")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 12013:
        raise SystemExit("candidate sequence changed since the p.204 review")
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
    planned_keys = [(row["canonical_name"].casefold(), row["suggested_type"].casefold()) for row in new_candidates]
    if len(planned_keys) != len(set(planned_keys)):
        raise SystemExit("planned candidates duplicate each other by canonical name/type")
    old_keys = {(row["canonical_name"].casefold(), row["suggested_type"].casefold()) for row in candidates}
    if old_keys.intersection(planned_keys):
        raise SystemExit("a planned candidate duplicates an existing canonical-name/type pair")
    candidates.extend(new_candidates)
    candidate_by_id.update({row["candidate_id"]: row for row in new_candidates})

    new_mentions = []
    for mention_id, candidate_id, surface, note in MENTION_SPECS:
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"planned mention has no candidate: {mention_id}")
        starts = [i for i in range(len(segment_text)) if segment_text.startswith(surface, i)]
        if len(starts) != 1:
            raise SystemExit(f"mention surface is not unique in p.204 source text: {mention_id}: {surface!r}")
        start = starts[0]
        new_mentions.append({
            "mention_id": mention_id, "segment_id": SEGMENT_ID, "candidate_id": candidate_id,
            "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
        })
    mentions.extend(new_mentions)
    mention_by_id.update({row["mention_id"]: row for row in new_mentions})

    def excerpt(start_line: int, end_line: int, first: str, last: str) -> str:
        source = "\n".join(source_lines[start_line - 1:end_line])
        start = source.find(first)
        end = source.rfind(last)
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
            "printed_page": 204, "pdf_physical_page": 2,
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
        row.update({
            "subject_candidate_id": subject, "object_candidate_id": object_id,
            "predicate": predicate, "qualifiers": q, "original_quote": quote_text,
        })
        return row

    def new_statement(statement_id: str, *, subject: str | None, object_id: str | None,
                      predicate: str, claim: str, qualification: str, quote_text: str,
                      start_line: int, end_line: int, mentioned: list[str],
                      relation: bool, relation_note: str, open_reason: str | None = None,
                      extra: dict | None = None, text_layer: str = "body") -> dict:
        source = "\n".join(source_lines[start_line - 1:end_line])
        if normalize(quote_text) not in normalize(source):
            raise SystemExit(f"new statement quote does not match source: {statement_id}")
        q = {
            "source_line_start": start_line, "source_line_end": end_line,
            "printed_page": 204, "pdf_physical_page": 2,
            "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
            "qualification": qualification, "mentioned_candidate_ids": mentioned,
            "relation_candidate": relation, "relation_candidate_note": relation_note,
        }
        if open_reason:
            q["open_endpoint_reason"] = open_reason
        if extra:
            q.update(extra)
        return {
            "statement_id": statement_id, "segment_id": SEGMENT_ID,
            "subject_candidate_id": subject, "object_candidate_id": object_id,
            "predicate": predicate, "qualifiers": q, "original_quote": quote_text,
            "origin": "book", "source_file": SOURCE_REL,
        }

    revise(
        "st-chp8-p204-crespi-biographer-evaluates-ricci-treatment",
        predicate="ricci_provided_generous_patronage_benefiting_crespi",
        subject="cand-2148", object_id="cand-0872",
        claim="The unnamed biographer, quoted by Haskell, describes Ricci's treatment of Crespi as unusually noble and generous and of enormous advantage to the artist.",
        qualification="The evaluation is attributed to Crespi's unnamed biographer as relayed by Haskell; it is not an independently verified assessment.",
        quote_text=excerpt(16, 16, "and it is certain", "advantage to Crespi"), start_line=16, end_line=16,
        mentioned=["cand-2148", "cand-0872"], relation=True,
        relation_note="The reported evaluation concerns Ricci's treatment of Crespi; the biographer is the nested speaker, not either relation endpoint.",
        extra={"nested_speaker": "Crespi's unnamed biographer, quoted by Haskell"},
    )
    revise(
        "st-chp8-p204-crespi-paintings-reflect-travel-influences",
        predicate="pictures_reflected_influences_absorbed_by_crespi",
        subject="cand-7391", object_id="cand-12014",
        claim="Haskell says the varied influences Crespi absorbed during his visits soon appeared in the pictures he painted for Ricci.",
        qualification="The pictures are a source-defined group rather than individually identified works; the influences themselves are not enumerated.",
        quote_text=excerpt(15, 15, "influences which soon made themselves felt", "painted for him"), start_line=15, end_line=15,
        mentioned=["cand-7391", "cand-0872", "cand-2148", "cand-3401", "cand-7392", "cand-12014"],
        relation=True, relation_note="The work group and the influences absorbed on the named visits are distinct endpoints; Ricci remains the patron in the surrounding sentence.",
    )
    revise(
        "st-chp8-p204-cross-regional-pictures-and-patrons",
        predicate="contemporary_neapolitan_picture_rarely_found_in_bologna",
        subject="cand-12015", object_id="cand-0381",
        claim="Haskell says it was rare, though not impossible, to find a contemporary Neapolitan picture in Bologna.",
        qualification="This is a qualitative statement about rarity, not a positive placement or ownership relation suitable for a formal graph edge.",
        quote_text=excerpt(21, 21, "it was rare in Bologna", "contemporary Neapolitan painter"), start_line=21, end_line=21,
        mentioned=["cand-12015", "cand-1722", "cand-0381"], relation=False,
        relation_note="A source-attributed rarity comparison is retained as a claim but is not a positive entity-to-entity relation.",
        remove_qualifiers=("ocr_corrections",),
    )
    revise(
        "st-chp8-p204-early-eighteenth-century-revival",
        predicate="historical_factors_revived_city_state_cosmopolitanism",
        subject=None, object_id=None,
        claim="Haskell says early eighteenth-century wars, increased foreign travel, Spain's decline, and reforms by enlightened despots helped revive the cosmopolitan importance of some Italian city-states.",
        qualification="This is a broad historical causal interpretation; the states, wars, reforms, and rulers are not specified as discrete relation endpoints in this passage.",
        quote_text=excerpt(20, 21, "At the beginning of the eighteenth century", "Italian city states."), start_line=20, end_line=21,
        mentioned=["cand-3461", "cand-4591", "cand-7395", "cand-7396"], relation=False,
        relation_note="The source gives a broad multi-factor historical explanation rather than a discrete graph relation.",
    )
    revise(
        "st-chp8-p204-italian-cities-remained-provincial",
        predicate="italian_cities_described_as_provincial",
        subject=None, object_id=None,
        claim="Haskell says the Italian cities remained essentially provincial after foreign domination and the subsequent peace, with Venice as a possible exception.",
        qualification="This is a broad historical characterization; the city set and the meaning of provincial are not defined as a discrete relation here.",
        quote_text=excerpt(20, 20, "With the general collapse of Italy", "remained essentially provincial."), start_line=20, end_line=20,
        mentioned=["cand-3461", "cand-3401"], relation=False,
        relation_note="The authorial generalization is preserved as a claim rather than represented as one edge from Italy to an unenumerated city set.",
        remove_qualifiers=("ocr_corrections",),
    )
    revise(
        "st-chp8-p204-local-traditions-and-taste-stagnation",
        predicate="social_classes_kept_local_painting_schools_alive",
        subject="cand-12017", object_id="cand-7380",
        claim="Haskell says the Italian nobility and professional classes kept valuable local painting schools alive during most of the seventeenth century.",
        qualification="The source describes the two social classes collectively and does not identify particular schools or patrons.",
        quote_text=excerpt(21, 21, "During most of the seventeenth century", "local schools of painting of great value"), start_line=21, end_line=21,
        mentioned=["cand-12017", "cand-7380", "cand-3461"], relation=True,
        relation_note="The source explicitly links the two social classes to sustaining local painting schools; the following statement separately records Haskell's interpretation of stagnation.",
        remove_qualifiers=("ocr_corrections",),
    )
    revise(
        "st-chp8-p204-naples-lawyers-supported-arts",
        predicate="lawyers_supported_arts_in_naples",
        subject="cand-12018", object_id=None,
        claim="Haskell says lawyers were especially prominent in supporting the arts in Naples and played a vital role in the city's cultural life.",
        qualification="The lawyers are an unnamed collective; the passage identifies no specific artwork, institution, or arts program.",
        quote_text=excerpt(17, 17, "In Naples the lawyers", "support of the arts."), start_line=17, end_line=17,
        mentioned=["cand-1722", "cand-12018", "cand-2686"], relation=True,
        relation_note="The actor group and its support of the arts are explicit, but no specific supported object is identified.",
        open_reason="The sentence refers generally to support of the arts and names no work, institution, or program as the object.",
    )
    revise(
        "st-chp8-p204-provincial-patrons-could-not-recreate-rome",
        predicate="local_patrons_could_not_recreate_roman_patronage_climate",
        subject="cand-2065", object_id=None,
        claim="Haskell argues that local patrons were crucial to painting's survival in Italy but could not create a climate like that established by families such as the Barberini and their Roman circle.",
        qualification="This is a broad comparative judgment; ‘all these men’ refers to professional-class patrons in the preceding discussion, not to the Barberini family.",
        quote_text=excerpt(19, 19, "However, all these men", "their circle in Rome."), start_line=19, end_line=19,
        mentioned=["cand-2065", "cand-3461", "cand-3464", "cand-4969", "cand-4490"], relation=False,
        relation_note="The sentence is a source-attributed comparative limit on artistic climate, not a positive relation between local patrons and the Barberini circle.",
    )
    revise(
        "st-chp8-p204-ricci-admired-contemporary-artists",
        predicate="ricci_appreciated_contemporary_artists",
        subject="cand-2148", object_id="cand-12019",
        claim="Haskell says Ricci appreciated many contemporary artists, especially Burrini and the young Crespi.",
        qualification="Burrini and Crespi are examples, not an exhaustive membership list for the artist group.",
        quote_text=excerpt(15, 15, "He was a rich and discriminating patron", "the young Crespi."), start_line=15, end_line=15,
        mentioned=["cand-2148", "cand-0473", "cand-0871", "cand-12019"], relation=True,
        relation_note="Ricci's appreciation is explicitly directed toward a source-defined group of contemporary artists; the named examples remain linked separately.",
    )
    revise(
        "st-chp8-p204-ricci-dealer-terms",
        predicate="ricci_bought_crespi_work_and_passed_resale_profits_to_artist",
        subject="cand-2148", object_id="cand-0872",
        claim="Haskell says Ricci acted as Crespi's dealer on unusual terms: he agreed to buy any available work by Crespi and passed the resale profits to him.",
        qualification="The arrangement is reported by Haskell through an unnamed artist biographer; no particular work or transaction is identified.",
        quote_text=excerpt(16, 16, "Ricci also acted as a dealer", "of enormous advantage to Crespi’"), start_line=16, end_line=16,
        mentioned=["cand-2148", "cand-0872"], relation=True,
        relation_note="The sentence explicitly links Ricci's dealing arrangement to Crespi; the purchase and profit terms qualify the same relationship.",
    )
    revise(
        "st-chp8-p204-ricci-leading-patron",
        predicate="described_as_most_cultivated_and_interesting_merchant",
        subject="cand-2148", object_id=None,
        claim="Haskell calls Giovanni Ricci the most cultivated and interesting member of the small group of enlightened merchants.",
        qualification="This is Haskell's evaluative description; the source does not enumerate the merchant group or define a formal membership relation.",
        quote_text=excerpt(15, 15, "group of enlightened merchants", "Giovanni Ricci."), start_line=15, end_line=15,
        mentioned=["cand-2148"], relation=False,
        relation_note="The statement is an authorial superlative and characterization, not a separate graph relation.",
    )
    revise(
        "st-chp8-p204-ricci-sent-crespi-to-absorb-influences",
        predicate="ricci_sent_crespi_on_study_visits",
        subject="cand-2148", object_id="cand-0872",
        claim="Haskell says Ricci judged Bologna's provincial atmosphere likely to stifle Crespi's imaginative gifts and sent him on long visits to Venice and Central Italy to absorb varied influences.",
        qualification="No dates, route, or financing details are supplied; the influence group is recorded in the linked statement about the resulting pictures.",
        quote_text=excerpt(15, 15, "He soon realised", "long visits to Venice and Central Italy"), start_line=15, end_line=15,
        mentioned=["cand-2148", "cand-0872", "cand-0381", "cand-3401", "cand-7392"], relation=True,
        relation_note="The source directly says Ricci sent Crespi on visits; Venice and Central Italy are destinations, not the recipient endpoint.",
        extra={"destination_candidate_ids": ["cand-3401", "cand-7392"]},
    )
    revise(
        "st-chp8-p204-roman-collections-broadened-appreciation",
        predicate="roman_collections_stimulated_broad_artistic_appreciation",
        subject="cand-7394", object_id="cand-12022",
        claim="Haskell says Roman collections of works from Italy and Europe stimulated wide appreciation and new combinations of artistic sensibility, exemplified by the classical-Venetian synthesis associated with Cassiano dal Pozzo and his circle.",
        qualification="The classical-Venetian synthesis is an example of the broader combinations, not the sole outcome; the collections are not individually named.",
        quote_text=excerpt(21, 21, "Whereas the great Roman collections", "Cassiano dal Pozzo and his circle"), start_line=21, end_line=21,
        mentioned=["cand-7394", "cand-4490", "cand-3461", "cand-3462", "cand-12022", "cand-7397", "cand-2036", "cand-7398"], relation=True,
        relation_note="The source explicitly links the collective Roman collections to broad artistic appreciation; the named synthesis is retained as an example of the outcome.",
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 21, "ocr": "sensibility— such", "print": "sensibility—such", "basis": "CHP-8.pdf physical page 2."}]},
    )
    revise(
        "st-chp8-p204-rome-only-competing-italian-capital",
        predicate="rome_competed_in_prestige_with_main_european_nation_state_towns",
        subject="cand-4490", object_id="cand-12020",
        claim="Haskell says that from about 1600 to 1670 Rome was the only Italian capital able to compete in prestige with the principal towns of Europe's nation-states.",
        qualification="This is a time-bounded comparison of prestige; the European towns are an unenumerated group.",
        quote_text=excerpt(20, 20, "Between about 1600 and 1670 Rome", "nation states of Europe."), start_line=20, end_line=20,
        mentioned=["cand-4490", "cand-3461", "cand-3462", "cand-12020"], relation=True,
        relation_note="Rome and the comparison group of principal towns are distinct endpoints; the date range and prestige dimension are preserved.",
        extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 20, "ocr": "only ‘capital’", "print": "only 'capital'", "basis": "CHP-8.pdf physical page 2."}]},
    )
    revise(
        "st-chp8-p204-valletta-friend-of-shaftesbury",
        predicate="friendship_with_person",
        subject="cand-2686", object_id="cand-7393",
        claim="Haskell says Giuseppe Valletta was a friend of Shaftesbury.",
        qualification="The passage supplies only the surname Shaftesbury; identity relative to indexed candidates remains for S3.",
        quote_text=excerpt(18, 18, "friend of Shaftesbury", "friend of Shaftesbury"), start_line=18, end_line=18,
        mentioned=["cand-2686", "cand-7393"], relation=True,
        relation_note="The source explicitly states a friendship; the second person's identity remains unresolved.",
    )
    revise(
        "st-chp8-p204-valletta-patron-of-giordano",
        predicate="patron_of_artist",
        subject="cand-2686", object_id="cand-1172",
        claim="Haskell identifies Giuseppe Valletta as a patron of Luca Giordano.",
        qualification="No particular commission or work is specified in this sentence.",
        quote_text=excerpt(18, 18, "the patron of Luca Giordano", "the patron of Luca Giordano"), start_line=18, end_line=18,
        mentioned=["cand-2686", "cand-1172"], relation=True,
        relation_note="The patron and artist are explicitly named; the source gives no specific commission in this statement.",
    )
    revise(
        "st-chp8-p204-valletta-patron-of-solimena",
        predicate="patron_of_artist",
        subject="cand-2686", object_id="cand-2484",
        claim="Haskell identifies Giuseppe Valletta as a patron of Francesco Solimena.",
        qualification="No particular commission or work is specified in this sentence.",
        quote_text=excerpt(18, 18, "and Solimena.", "and Solimena."), start_line=18, end_line=18,
        mentioned=["cand-2686", "cand-2484"], relation=True,
        relation_note="The patron and artist are explicitly named; the source gives no specific commission in this statement.",
    )
    revise(
        "st-chp8-p204-valletta-professions",
        predicate="identified_as_poet_and_arbiter_of_taste",
        subject="cand-2686", object_id=None,
        claim="Haskell describes Giuseppe Valletta as a poet and arbiter of taste.",
        qualification="This is descriptive biographical information, not a relation to another entity.",
        quote_text=excerpt(18, 18, "Valletta, poet and arbiter of taste", "Valletta, poet and arbiter of taste"), start_line=18, end_line=18,
        mentioned=["cand-2686"], relation=False,
        relation_note="The sentence assigns two descriptive roles to one person; it does not state an entity-to-entity relation.",
    )

    new_rows = [
        new_statement(
            "st-chp8-p204-venetian-picture-rare-in-genoa", subject="cand-12021", object_id="cand-1131",
            predicate="venetian_picture_rarely_found_in_genoa",
            claim="Haskell says a Venetian picture was rare, though not impossible, to find in Genoa.",
            qualification="This is a qualitative rarity statement, not a positive placement or ownership relation suitable for a formal graph edge.",
            quote_text=excerpt(21, 21, "or in Genoa", "Rare—but not impossible;"), start_line=21, end_line=21,
            mentioned=["cand-12021", "cand-1131", "cand-3401", "cand-7400"], relation=False,
            relation_note="A source-attributed rarity comparison is retained as a claim but is not a positive entity-to-entity relation.",
        ),
        new_statement(
            "st-chp8-p204-translocal-patrons-collected-foreign-works", subject="cand-7399", object_id="cand-12016",
            predicate="translocal_italian_patrons_collected_foreign_artworks",
            claim="Haskell says a few Italian expatriate or citizen patrons looked beyond their native towns and included works by foreign artists in their collections.",
            qualification="The patrons are an unnamed collective and the works are not individually identified; the source attributes a contribution to avoiding stagnation in the surrounding sentence.",
            quote_text=excerpt(21, 21, "by a few patrons within Italy itself", "works by foreign artists."), start_line=21, end_line=21,
            mentioned=["cand-7399", "cand-3461", "cand-12016"], relation=True,
            relation_note="The source explicitly links the translocal patron group to collecting foreign artists' works; the earlier foreign intervention is not attributed to this group.",
            extra={"ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 21, "ocr": "who-looked", "print": "who looked", "basis": "CHP-8.pdf physical page 2."}]},
        ),
        new_statement(
            "st-chp8-p204-foreign-intervention-averted-stagnation", subject=None, object_id=None,
            predicate="authorial_causal_interpretation_of_stagnation_avoidance",
            claim="Haskell attributes the avoidance of stagnation in Italian painting partly to foreign intervention and partly to a few patrons who collected works beyond their native towns.",
            qualification="The prior foreign intervention is only cross-referenced, not specified; this is a broad causal interpretation rather than a single entity relation.",
            quote_text=excerpt(21, 21, "stagnation was averted", "works by foreign artists."), start_line=21, end_line=21,
            mentioned=["cand-3461", "cand-7399", "cand-12016"], relation=False,
            relation_note="The full causal comparison is preserved as authorial interpretation; the specific collection action is separately represented as a relation candidate.",
            extra={"ocr_corrections": [
                {"source_file": SOURCE_REL, "source_line": 21, "ocr": "hot only", "print": "not only", "basis": "CHP-8.pdf physical page 2."},
                {"source_file": SOURCE_REL, "source_line": 21, "ocr": "who-looked", "print": "who looked", "basis": "CHP-8.pdf physical page 2."},
            ]},
        ),
        new_statement(
            "st-chp8-p204-local-traditions-stagnated-taste", subject=None, object_id=None,
            predicate="local_isolation_and_traditions_led_to_stagnation_of_taste",
            claim="Haskell says the isolation of local painting schools and the vigour of individual traditions inevitably led to stagnation of taste.",
            qualification="This is Haskell's broad historical interpretation; no specific school, local tradition, or measurable outcome is identified.",
            quote_text=excerpt(21, 21, "but their isolation", "stagnation of taste."), start_line=21, end_line=21,
            mentioned=["cand-12017", "cand-7380"], relation=False,
            relation_note="This general causal interpretation is kept separate from the preceding claim that social classes sustained the schools.",
        ),
    ]

    old_id, new_id = next(iter(RENAMED_IDS.items()))
    if new_id in by_id:
        raise SystemExit(f"renamed statement ID collision: {new_id}")
    row = by_id.pop(old_id)
    row["statement_id"] = new_id
    by_id[new_id] = row

    def replace_nested(value):
        if isinstance(value, dict):
            for key, item in list(value.items()):
                if item == old_id:
                    value[key] = new_id
                else:
                    replace_nested(item)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if item == old_id:
                    value[index] = new_id
                else:
                    replace_nested(item)

    for statement in statements:
        replace_nested(statement.get("qualifiers", {}))
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
                raise SystemExit(f"p.204 statement has unresolved candidate: {row['statement_id']} -> {candidate_id}")
        if q.get("relation_candidate") is True and (not row.get("subject_candidate_id") or not row.get("object_candidate_id")) and not q.get("open_endpoint_reason"):
            raise SystemExit(f"true p.204 relation candidate has an unexplained open endpoint: {row['statement_id']}")
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("post-plan statement IDs are not unique")

    expected_counts = {"statements": 14216, "candidates": 12000, "mentions": 28064, "true": 8884, "false": 3452, "unset": 1880}
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
        "new_statements": sorted(NEW_STATEMENT_IDS),
        "renamed_statement": RENAMED_IDS,
        "new_candidates": [row["candidate_id"] for row in new_candidates],
        "new_mentions": [row["mention_id"] for row in new_mentions],
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
