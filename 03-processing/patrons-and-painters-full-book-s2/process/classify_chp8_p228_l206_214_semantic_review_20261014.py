"""Guarded S2 semantic review for printed p.228, body lines 206-214."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p228_review.png"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l206-214"
BACKUP_SUFFIX = ".bak-s2-chp8-p228-l206-214-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "65bd69a24c399bbdfefeee7857a942d3f360a3d1d03ae3f80e16fe1e58034cf3",
    CANDIDATES: "85628ba39c988df335ef8db6cab45c24238e3a384a73c5aab8e43c640f23387a",
    MENTIONS: "491de5911a85a90fad52a176977b37f14eb81ae3a77073fffd0b9a1ca8313198",
    COVERAGE: "6207ec3734deacfe3e02ec341c3a558440f7273ad4f9c2c964ad94ab2710fc34",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "b91dfa0aa43fecb0eb6fbfe8b29b2c39156b7e2d50c3e3b434757d6624f92c1d",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def jsonl_bytes(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    temporary.replace(path)


def require_fragment(line: str, start: str, end: str | None = None) -> str:
    a = line.find(start)
    if a < 0:
        raise SystemExit(f"source fragment not found: {start!r}")
    b = line.find(end, a + len(start)) if end else a + len(start)
    if end and b < 0:
        raise SystemExit(f"source end fragment not found after {start!r}: {end!r}")
    return line[a:b].rstrip()


def new_statement(statement_id, subject, object_, predicate, lines, claim, quote, *,
                  relation, note, mentioned, speaker="Haskell", text_layer="body", extra=None):
    qualifiers = {
        "source_line_start": lines[0], "source_line_end": lines[1],
        "printed_page": 228, "pdf_physical_page": 30,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": note, "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation, "relation_candidate_note": note,
    }
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": SEGMENT,
            "subject_candidate_id": subject, "object_candidate_id": object_,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote, "origin": "book", "source_file": SOURCE_REL}


def plan():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

    segments = read_jsonl(SEGMENTS)
    segment_meta = {row["segment_id"]: row for row in segments}.get(SEGMENT)
    if not segment_meta or (segment_meta["line_start"], segment_meta["line_end"]) != (206, 214):
        raise SystemExit("unexpected p.228 S0 segment metadata")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_segment = "\n".join(source_lines[205:214])
    if sha(source_segment.encode("utf-8")) != segment_meta["sha256"]:
        raise SystemExit("p.228 source segment hash mismatch")

    candidate_fields, candidates = read_csv(CANDIDATES)
    mention_fields, mentions = read_csv(MENTIONS)
    statements = read_jsonl(STATEMENTS)
    coverage_fields, coverage = read_csv(COVERAGE)
    by_id = {row["statement_id"]: row for row in statements}
    segment_rows = [row for row in statements if row.get("segment_id") == SEGMENT]
    if len(segment_rows) != 16:
        raise SystemExit(f"expected 16 migrated p.228 statements; got {len(segment_rows)}")
    expected_ids = {
        "st-chp8-p228-canale-landscape-praise",
        "st-chp8-p228-carlevarijs-bassi-age",
        "st-chp8-p228-conti-taste-accredited-works",
        "st-chp8-p228-crespi-contract-comparators",
        "st-chp8-p228-four-artists-style-isolation",
        "st-chp8-p228-marco-ricci-landscape-praise",
        "st-chp8-p228-marco-ricci-five-landscapes",
        "st-chp8-p228-medici-exception",
        "st-chp8-p228-provincial-artists-isolated",
        "st-chp8-p228-provincial-collection-limitation",
    }
    if not expected_ids <= set(by_id):
        raise SystemExit(f"missing expected statement IDs: {sorted(expected_ids - set(by_id))}")
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) != ("reviewed", "complete", "L206-214"):
        raise SystemExit(f"unexpected p.228 coverage state: {coverage_row}")

    source_by_line = {i + 1: line for i, line in enumerate(source_lines)}
    line207, line208, line209 = source_by_line[207], source_by_line[208], source_by_line[209]
    line212, line213, line214 = source_by_line[212], source_by_line[213], source_by_line[214]
    quote_canale = require_fragment(line207, "Sigr. Antonio Canale", "and also").rstrip(" ,")
    quote_ricci = require_fragment(line207, "a remarkable landscape painter", "And so,").rstrip(" ")
    quote_bassi = require_fragment(line207, "il Cremonese was blind")
    quote_carlevarijs = "old"
    quote_conti_did_not_expand = require_fragment(line212, "he did nothing to increase their number", "His taste")
    quote_conti_taste = require_fragment(line212, "His taste was never very adventurous", "Like many")
    quote_group_isolation = require_fragment(line212, "This little group of pictures", "and he did nothing")
    quote_provincial_limitation = (
        line212[line212.index("Like many of the other patrons"):].rstrip() + "\n" +
        require_fragment(line213, "Lucca.", "Pictures from Bologna")
    )
    quote_provincial_artists = require_fragment(line213, "Pictures from Bologna", "There was, however")
    quote_medici_membership = require_fragment(line214, "a Medici")
    quote_medici_importance = require_fragment(line214, "The most important figure", "a Medici")
    quote_marco_landscapes = require_fragment(line207, "eventually five little landscapes", "Marco’s uncle")
    quote_sebastiano_insertion = require_fragment(line207, "Marco’s uncle, Sebastiano", "but when")
    quote_contract_ferdinand = require_fragment(line209, "from His Highness the late Grand Prince Ferdinand")
    quote_contract_pope = require_fragment(line209, "from the late Pope")
    quote_contract_eugene = require_fragment(line209, "from Prince Eugene of Savoy in whose service I now am")

    classifications = {
        "st-chp8-p228-canale-landscape-praise": (True, "Attributed praise by Marchesini connects the named painter to a specific assessment of his views."),
        "st-chp8-p228-carlevarijs-bassi-age": (True, "The p.227 continuation reports Marchesini's description of Carlevarijs as old; its separate statement about Bassi is recorded below."),
        "st-chp8-p228-conti-taste-accredited-works": (False, "This is Haskell's evaluative characterization of Conti's taste and collecting preference, not a formal relationship."),
        "st-chp8-p228-four-artists-style-isolation": (False, "Haskell's claim that the group must have looked isolated is an aesthetic interpretation, not a formal relationship."),
        "st-chp8-p228-marco-ricci-landscape-praise": (True, "Attributed praise by Marchesini connects Marco Ricci to specific assessments of his landscape work."),
        "st-chp8-p228-medici-exception": (False, "Haskell's claim that Ferdinand was the period's most important figure is an interpretive judgment; dynastic membership is recorded separately."),
        "st-chp8-p228-provincial-artists-isolated": (False, "This is Haskell's general interpretation of provincial artistic isolation, not a formal entity relationship."),
        "st-chp8-p228-provincial-collection-limitation": (False, "This is Haskell's generalization about provincial patrons and collections, not a formal entity relationship."),
    }
    for statement_id, (value, note) in classifications.items():
        row = by_id[statement_id]
        q = row["qualifiers"]
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"expected unset classification for {statement_id}: {q.get('relation_candidate')}")
        q["relation_candidate"] = value
        q["relation_candidate_note"] = note

    canale = by_id["st-chp8-p228-canale-landscape-praise"]
    canale["predicate"] = "marchesini_praises_canales_sunlit_views"
    canale["original_quote"] = quote_canale
    canale["qualifiers"].update({
        "claim": "Haskell reports Marchesini praising Antonio Canale's views as like Carlevarijs's but distinguished by their sunlit quality.",
        "speaker": "Marchesini (reported by Haskell)",
        "text_layer": "reported direct speech",
        "qualification": "The praise is attributed to Marchesini; 'this city' is resolved as Venice from the surrounding passage.",
        "mentioned_candidate_ids": ["cand-1540", "cand-0498", "cand-0554", "cand-3401"],
    })

    carlevarijs = by_id["st-chp8-p228-carlevarijs-bassi-age"]
    carlevarijs["predicate"] = "marchesini_describes_carlevarijs_as_old"
    carlevarijs["original_quote"] = quote_carlevarijs
    carlevarijs["qualifiers"].update({
        "claim": "Haskell reports Marchesini describing Carlevarijs as old.",
        "speaker": "Marchesini (reported by Haskell)",
        "text_layer": "reported direct speech",
        "qualification": "This phrase completes the p.227 sentence; the adjacent claim about Francesco Bassi is atomized into a separate statement.",
        "mentioned_candidate_ids": ["cand-1540", "cand-0554"],
        "continuation_status": "closed",
    })

    ricci_praise = by_id["st-chp8-p228-marco-ricci-landscape-praise"]
    ricci_praise["predicate"] = "marchesini_praises_marco_riccis_landscape_work"
    ricci_praise["original_quote"] = quote_ricci
    ricci_praise["qualifiers"].update({
        "claim": "Haskell reports Marchesini praising Marco Ricci's landscapes as distinctive, in demand in Venice and London, and notable for views, Poussin-like buildings and vivid colour.",
        "speaker": "Marchesini (reported by Haskell)",
        "text_layer": "reported direct speech",
        "qualification": "The unidentified landscape-painter reference is locally resolved to Marco Ricci by the following sentence naming his five landscapes; this attribution remains Haskell's report of Marchesini.",
        "mentioned_candidate_ids": ["cand-1540", "cand-2149", "cand-1422", "cand-1984"],
    })

    conti_taste = by_id["st-chp8-p228-conti-taste-accredited-works"]
    conti_taste["predicate"] = "haskell_characterizes_contis_taste_and_gallery_interest"
    conti_taste["original_quote"] = quote_conti_taste
    conti_taste["qualifiers"].update({
        "claim": "Haskell calls Conti's taste unadventurous and says his greatest interest was apparently to fill his gallery with accredited works.",
        "qualification": "This is Haskell's attributed interpretation; 'apparently' is retained.",
        "mentioned_candidate_ids": ["cand-0833", "cand-7785"],
    })

    style = by_id["st-chp8-p228-four-artists-style-isolation"]
    style["object_candidate_id"] = "cand-12091"
    style["original_quote"] = quote_group_isolation
    style["qualifiers"].update({
        "claim": "Haskell says this group of pictures by Crespi, Canaletto, Marco Ricci and Sebastiano Ricci must have looked isolated among Conti's essentially old-fashioned paintings.",
        "qualification": "The aesthetic and isolation judgments are Haskell's interpretation; the object is the four-artist picture group, not Crespi's individual commission.",
        "mentioned_candidate_ids": ["cand-0833", "cand-12091", "cand-0871", "cand-0498", "cand-2149", "cand-2154"],
    })

    provincial = by_id["st-chp8-p228-provincial-collection-limitation"]
    provincial["original_quote"] = quote_provincial_limitation
    provincial["qualifiers"].update({
        "claim": "Haskell generalizes that patrons in small towns who ordered pictures from elsewhere could not see them before arrival, and calls this a limitation of most provincial collections.",
        "qualification": "This is a qualified generalization, not a claim about every patron or every work.",
    })
    artists = by_id["st-chp8-p228-provincial-artists-isolated"]
    artists["original_quote"] = quote_provincial_artists
    artists["qualifiers"].update({
        "claim": "Haskell says paintings from several Italian cities could enrich local taste while artists remained isolated from one another and from a cultivated patron's guidance.",
        "qualification": "This is Haskell's generalization about provincial collections and artistic contact.",
    })

    medici = by_id["st-chp8-p228-medici-exception"]
    medici["predicate"] = "haskell_identifies_ferdinand_as_key_figure_in_interregnum"
    medici["original_quote"] = quote_medici_importance
    medici["qualifiers"].update({
        "claim": "Haskell presents Grand Prince Ferdinand as the most important figure in an interregnum in which an overriding sense of artistic direction seemed to have been lost.",
        "qualification": "The identity is resolved from the immediate p.229 continuation; this row preserves Haskell's historical interpretation, while dynastic membership is a separate statement.",
        "mentioned_candidate_ids": ["cand-1609"],
    })

    marco_work = by_id["st-chp8-p228-marco-ricci-five-landscapes"]
    marco_work["predicate"] = "conti_commissions_five_landscapes_from_marco_ricci"
    marco_work["original_quote"] = quote_marco_landscapes
    marco_work["qualifiers"].update({
        "claim": "Conti eventually commissioned five small landscapes with ruins and figures from Marco Ricci.",
        "qualification": "The reported five-picture group is kept distinct from Sebastiano Ricci's separately described addition of figures.",
        "mentioned_candidate_ids": ["cand-0833", "cand-2149", "cand-7825"],
        "quantity": 5,
    })

    contract = by_id["st-chp8-p228-crespi-contract-comparators"]
    contract["predicate"] = "crespi_cites_prior_contract_from_grand_prince_ferdinand"
    contract["original_quote"] = quote_contract_ferdinand
    contract["qualifiers"].update({
        "claim": "Crespi says he had previously received a correct written contract from the late Grand Prince Ferdinand.",
        "qualification": "This is Crespi's reported statement; the prior contract is not independently examined.",
        "mentioned_candidate_ids": ["cand-0871", "cand-1609"],
        "reported_speaker": "Giuseppe Maria Crespi",
        "text_layer": "reported direct speech",
    })

    candidate_ids = {row["candidate_id"] for row in candidates}
    if "cand-12091" in candidate_ids:
        raise SystemExit("candidate ID cand-12091 already exists")
    if any(row.get("canonical_name") == "Conti's group of pictures by Crespi, Canaletto, Marco Ricci and Sebastiano Ricci"
           and row.get("suggested_type") == "work" for row in candidates):
        raise SystemExit("picture-group natural key already exists")
    candidates.append({
        "candidate_id": "cand-12091", "index_entry_id": "", "canonical_name": "Conti's group of pictures by Crespi, Canaletto, Marco Ricci and Sebastiano Ricci",
        "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": "A collective group of pictures in Conti's collection, described by Haskell as including works by four artists; no common title or complete item list is supplied.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L212",
    })

    statement_ids = {row["statement_id"] for row in statements}
    additions = [
        new_statement(
            "st-chp8-p228-bassi-blindness", "cand-1540", "cand-0259",
            "marchesini_reports_bassi_as_blind", (207, 207),
            "Haskell reports Marchesini saying Francesco Bassi, called il Cremonese, was blind.",
            quote_bassi, relation=True,
            note="This is separately attributed from the preceding statement about Carlevarijs being old.",
            mentioned=["cand-1540", "cand-0259"], speaker="Marchesini (reported by Haskell)",
            text_layer="reported direct speech"),
        new_statement(
            "st-chp8-p228-conti-did-not-expand-picture-group", "cand-0833", "cand-12091",
            "haskell_says_conti_did_not_add_to_picture_group", (212, 212),
            "Haskell says Conti did nothing to increase the number of pictures in this four-artist group.",
            quote_conti_did_not_expand, relation=False,
            note="The claim is a reported absence of later additions; it is not converted into a formal relationship.",
            mentioned=["cand-0833", "cand-12091"]),
        new_statement(
            "st-chp8-p228-sebastiano-inserts-landscape-figures", "cand-2154", "cand-7825",
            "sebastiano_ricci_inserts_figures_into_marco_ricci_landscapes", (207, 207),
            "Sebastiano Ricci inserted the figures into the five landscapes by his nephew Marco Ricci.",
            quote_sebastiano_insertion, relation=True,
            note="The source distinguishes Marco as the landscape painter and Sebastiano as the figure painter.",
            mentioned=["cand-2154", "cand-2149", "cand-7825"],
            extra={"family_context": "Sebastiano is identified as Marco's uncle."}),
        new_statement(
            "st-chp8-p228-crespi-contract-comparator-pope", "cand-0871", "cand-7829",
            "crespi_cites_prior_contract_from_unidentified_pope", (209, 209),
            "Crespi says he had previously received a correct written contract from an unnamed late Pope.",
            quote_contract_pope, relation=True,
            note="The Pope is explicitly unnamed; no pontiff is inferred.",
            mentioned=["cand-0871", "cand-7829"], speaker="Giuseppe Maria Crespi (reported direct speech)",
            text_layer="reported direct speech"),
        new_statement(
            "st-chp8-p228-crespi-contract-comparator-eugene", "cand-0871", "cand-2384",
            "crespi_cites_prior_contract_from_prince_eugene", (209, 209),
            "Crespi says he had previously received a correct written contract from Prince Eugene of Savoy and was then in his service.",
            quote_contract_eugene, relation=True,
            note="The quote supplies both the contract precedent and Crespi's reported current service to Eugene.",
            mentioned=["cand-0871", "cand-2384"], speaker="Giuseppe Maria Crespi (reported direct speech)",
            text_layer="reported direct speech"),
        new_statement(
            "st-chp8-p228-ferdinand-member-of-medici-family", "cand-1609", "cand-5179",
            "member_of", (214, 214),
            "The continuation identifies Grand Prince Ferdinand as a Medici, a member of the Medici family.",
            quote_medici_membership, relation=True,
            note="The person is identified by the immediate p.229 continuation; the family membership is expressed on p.228.",
            mentioned=["cand-1609", "cand-5179"],
            extra={"continued_context_segment_id": "chp-8:08_CHP-8_sec_ii:l216-225", "continued_context_source_line": 217}),
    ]
    for row in additions:
        if row["statement_id"] in statement_ids:
            raise SystemExit(f"statement ID already exists: {row['statement_id']}")
        statement_ids.add(row["statement_id"])

    mention_ids = {row["mention_id"] for row in mentions}
    spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
    segment_start = segment_meta["line_start"]
    offsets = {}
    offset = 0
    for line_no, line in zip(range(segment_start, segment_meta["line_end"] + 1), source_lines[segment_start - 1:segment_meta["line_end"]]):
        offsets[line_no] = offset
        offset += len(line) + 1

    new_mentions = []
    def add_mention(mention_id, line_no, candidate_id, surface, note):
        if mention_id in mention_ids:
            raise SystemExit(f"mention ID already exists: {mention_id}")
        line = source_by_line[line_no]
        start_local = line.find(surface)
        if start_local < 0:
            raise SystemExit(f"mention surface missing at L{line_no}: {surface!r}")
        start = offsets[line_no] + start_local
        end = start + len(surface)
        span = (SEGMENT, str(start), str(end))
        if span in spans:
            raise SystemExit(f"duplicate mention span: {span}")
        new_mentions.append({"mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
                             "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})
        mention_ids.add(mention_id)
        spans.add(span)

    add_mention("m-chp8-p228-four-artists-picture-group", 212, "cand-12091", "This little group of pictures",
                "Collective reference to the pictures by Crespi, Canaletto, Marco Ricci and Sebastiano Ricci.")
    add_mention("m-chp8-p228-medici-family", 214, "cand-5179", "Medici",
                "Dynastic endpoint for the linked member_of statement; the full phrase also identifies Grand Prince Ferdinand.")

    all_ids = {row["statement_id"] for row in statements}
    for row in additions:
        row["qualifiers"]["relation_candidate_note"] = row["qualifiers"]["qualification"]

    patched_statements = statements + additions
    totals = {"true": 0, "false": 0, "unset": 0}
    for row in patched_statements:
        if row.get("segment_id") != SEGMENT:
            continue
        value = row.get("qualifiers", {}).get("relation_candidate")
        totals["true" if value is True else "false" if value is False else "unset"] += 1
    if totals["unset"]:
        raise SystemExit(f"p.228 still has unset statement classifications: {totals}")

    preview = {
        "mode": "dry-run", "segment": SEGMENT, "page_image": PAGE_IMAGE.relative_to(ROOT).as_posix(),
        "existing_statements_reviewed": len(segment_rows), "new_statements": [row["statement_id"] for row in additions],
        "new_candidate": "cand-12091", "new_mentions": [row["mention_id"] for row in new_mentions],
        "p228_final_statement_counts": totals,
        "semantic_fixes": [
            "separate Carlevarijs age from Bassi blindness",
            "separate Conti's five-picture commission from Sebastiano's figure insertion",
            "separate Crespi's three cited contract precedents",
            "separate dynastic membership from Haskell's periodization judgment",
            "anchor the four-artist picture group and correct the isolation statement endpoint",
            "narrow quotation spans to the claims they support",
        ],
    }
    payload = {
        STATEMENTS: jsonl_bytes(patched_statements),
        CANDIDATES: csv_bytes(candidate_fields, candidates),
        MENTIONS: csv_bytes(mention_fields, mentions + new_mentions),
        COVERAGE: csv_bytes(coverage_fields, coverage),
    }
    return preview, payload


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.228 S2 review")
args = parser.parse_args()
preview, payload = plan()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (STATEMENTS, CANDIDATES, MENTIONS, COVERAGE):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
for path, data in payload.items():
    atomic_write(path, data)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
