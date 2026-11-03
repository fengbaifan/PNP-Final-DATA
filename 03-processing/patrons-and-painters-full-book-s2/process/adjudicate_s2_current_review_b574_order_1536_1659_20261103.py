#!/usr/bin/env python3
"""Apply the B574 current-version S2 repairs for Chapter 2, printed pp. 34–38."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import tempfile
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
RESULTS = ROOT / "03-processing/patrons-and-painters-full-book-s2/results"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
SEGMENTS_PATH = TABLES / "segments.jsonl"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
STAGES_PATH = PROCESS / "stages.md"
RESULT_STAGES_PATH = RESULTS / "stages.md"
CURRENT_RESULT_PATH = ROOT / "04-knowledge/results/patrons-and-painters-full-book-s2.md"

BASE_HEAD = "af3f3ba7084b0066febe9d388b5c4a8b1b1eb634"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
SOURCE_HASHES = {
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
BATCH_ID = "S2-B574-CH2-1536-1659"
STAGE_ID = "2026-11-03-s2-current-review-b574-order-1536-1659"
EVIDENCE_REF = f"stages.md#{STAGE_ID}"
WINDOW_START = 1536
WINDOW_END = 1659

PASS_IDS = {
    # p.34: source attribution, temporal scope, and exact local mention repairs.
    "st-chp2-sec-ii-l30-40-passeri-bolognese-and-urban",
    "st-chp2-sec-ii-l30-40-bernini-birthplace-and-mother",
    "st-chp2-sec-ii-l30-40-bernini-father-origin",
    "st-chp2-sec-ii-l30-40-appeal-attributed-to-origin",
    "st-chp2-sec-ii-l30-40-urban-favored-tuscan-artists",
    "st-chp2-sec-ii-l30-40-urban-reported-praise",
    "st-chp2-sec-ii-l30-40-bernini-first-monumental-works",
    "st-chp2-sec-ii-l30-40-bernini-prior-work-and-first-post",
    "st-chp2-sec-ii-l30-40-observers-on-facade-inscription",
    "st-chp2-sec-ii-l30-40-bernini-baldacchino-start",
    "st-chp2-sec-ii-l30-40-bronze-from-pantheon",
    # p.35: line-specific endpoint mappings and the construction sequence.
    "st-chp2-secii-l42-50-iconography_simple",
    "st-chp2-secii-l42-50-planned_risen_christ_statue",
    "st-chp2-secii-l42-50-cross_replaced_risen_christ",
    "st-chp2-secii-l42-50-references_to_peter_and_papacy",
    "st-chp2-secii-l42-50-column_preserved_at_st_peters",
    "st-chp2-secii-l42-50-solomon_temple_precedent",
    "st-chp2-secii-l42-50-twisted_column_basilica_screens",
    "st-chp2-secii-l42-50-urban_role_in_scheme",
    "st-chp2-secii-l42-50-urban_ensured_identification",
    "st-chp2-secii-l42-50-barberini_bees_decoration",
    "st-chp2-secii-l42-50-barberini_history_linked_to_church",
    "st-chp2-secii-l42-50-barberini_sun_decoration",
    "st-chp2-secii-l42-50-cost_reported",
    "st-chp2-secii-l42-50-epigram_followed_removal",
    "st-chp2-secii-l42-50-laurel_instead_of_vine",
    "st-chp2-secii-l42-50-pantheon_bronze_removed",
    "st-chp2-secii-l42-50-pope_influence_decisive",
    "st-chp2-secii-l42-50-committee_decided_altars",
    "st-chp2-secii-l42-50-pope_deferred_choice_to_committee",
    # p.36: exact statement-to-mention mapping; authorship, scope, and qualifiers retained.
    "st-chp2-secii-l52-60-berninischeme-accepted-plan-revised",
    "st-chp2-secii-l52-60-four-most-venerated-saints",
    "st-chp2-secii-l52-60-two-further-direct-commissions",
    "st-chp2-secii-l52-60-matilda-tomb-designed",
    "st-chp2-secii-l52-60-completed-scheme-new-meaning",
    "st-chp2-secii-l52-60-papacy-and-house-reminder",
    "st-chp2-secii-l52-60-religious-elements-hymn",
    "st-chp2-secii-l52-60-barberini-patronage-complaint",
    "st-chp2-secii-l52-60-berninipayment",
    "st-chp2-secii-l52-60-passeri-quote-poison-fragment",
    "st-chp2-secii-l52-60-passeri-satirical-parody",
    # p.37: nested quotation and endpoint mappings; existing formal edges are unchanged.
    "st-chp2-secii-l62-69-passeri-quote-continuation",
    "st-chp2-secii-l62-69-scipione-two-busts-authorized",
    "st-chp2-secii-l62-69-diplomatic-portrait-permission",
    "st-chp2-secii-l62-69-pope-restricted-berninipatrons",
    "st-chp2-secii-l62-69-urban-commissioned-bibiana-work",
    "st-chp2-secii-l62-69-berninicompleted-bibiana-work",
    # p.38: exact Marino/Paris/Italy source-local mapping.
    "st-chp2-secii-l71-78-marino-return-from-paris",
}

ADDED_MENTIONS = [
    ("m-chp2-secii-l30-40-0044", "chp-2:02_CHP-2_sec_ii:l30-40", "cand-11881",
     "decorative sculpture and small-scale busts",
     "Source phrase anchoring Bernini's prior-work group; not an individually titled sculpture."),
    ("m-chp2-secii-l30-40-0045", "chp-2:02_CHP-2_sec_ii:l30-40", "cand-11882",
     "his first monumental works",
     "Source phrase anchoring Bernini's first monumental-work group; individual works remain unnamed here."),
    ("m-chp2-secii-l30-40-0046", "chp-2:02_CHP-2_sec_ii:l30-40", "cand-11584",
     "early Christian tombs",
     "Source-defined plural tomb group at risk from the baldacchino foundations; distinct from the supposed tomb of St Peter."),
    ("m-chp2-secii-l42-50-0070", "chp-2:02_CHP-2_sec_ii:l42-50", "cand-4397",
     "Iconographically",
     "The adverb introduces the baldacchino's source-defined iconographic scheme; it does not identify a separate work."),
    ("m-chp2-secii-l42-50-0071", "chp-2:02_CHP-2_sec_ii:l42-50", "cand-11585",
     "a form",
     "Anaphoric mention of the twisted-column architectural form, not Bernini's physical columns."),
    ("m-chp2-secii-l42-50-0072", "chp-2:02_CHP-2_sec_ii:l42-50", "cand-3104",
     "his enterprises",
     "The possessive refers to Urban VIII, the Pope named in the preceding source line; exact anchor for this relation candidate."),
    ("m-chp2-secii-l52-60-0090", "chp-2:02_CHP-2_sec_ii:l52-60", "cand-11587",
     "the relics associated with the saints concerned",
     "Source-defined unspecified relic group available for feast-day display and stone reproductions; members remain unidentified."),
]

STATEMENT_REPAIRS = {
    "st-chp2-sec-ii-l30-40-urban-reported-praise": {
        "claim": "Haskell reports Urban VIII's words praising Maffeo Barberini's accession and Bernini's presence during the pontificate; he adds that subsequent action soon showed the sentiment to be genuine even if the words themselves were apocryphal.",
        "qualification": "The reported dialogue remains hearsay and may be apocryphal. The claim distinguishes Urban's attributed words from Haskell's interpretation of subsequent action; footnote 3 cites Baldinucci.",
        "extend_quote_to_apocryphal": True,
    },
    "st-chp2-sec-ii-l30-40-bernini-first-monumental-works": {
        "claim": "Haskell says that within a few months Bernini received his first official post and began his first monumental works; the sentence does not say that work began a few months after the appointment.",
        "qualification": "The temporal phrase covers the two coordinated developments in the source; no interval between appointment and the beginning of the works is stated. The source names no individual work in this sentence.",
    },
    "st-chp2-sec-ii-l30-40-observers-on-facade-inscription": {
        "claim": "Haskell reports that unnamed malicious observers said the façade gave more prominence to Paul V's name than to St Peter and sarcastically claimed that the Church had been built for Paul, the Apostle's Vicar, rather than for the Prince of the Apostles.",
        "qualification": "Both the comparison and the nested sarcastic quotation are attributed to unnamed observers and cited via P. Romano in footnote 4; neither establishes the builders' intention.",
    },
    "st-chp2-secii-l42-50-cross_replaced_risen_christ": {
        "claim": "Haskell says the original Risen Christ design was changed to a Cross at a later stage, after work had already begun, shifting the monument's effect toward Christ's Passion rather than his triumph.",
        "qualification": "The source reports a later design change after work had begun; it gives no exact date and does not say the Cross statue was completed.",
    },
    "st-chp2-secii-l52-60-papacy-and-house-reminder": {
        "claim": "Haskell interprets the programme as a passionate reminder of the overwhelming glories of the papacy and Urban VIII's own house, fused into and essential to the church's whole structure.",
        "qualification": "This is Haskell's interpretation of the ensemble. The 'own house' refers to the Barberini family; the claim does not independently assess the church's structure.",
    },
    "st-chp2-secii-l52-60-religious-elements-hymn": {
        "claim": "Haskell says the ensemble's elements echo one another in style and theme, forming a hymn of praise to Christ's martyrdom, his Saints and Apostles, unequalled in emotional force anywhere in the world.",
        "qualification": "The hymn and its emotional force are Haskell's metaphorical evaluation, not an objective measurement. The OCR-fused phrase is read against printed p.36.",
    },
    "st-chp2-secii-l52-60-passeri-quote-poison-fragment": {
        "quoted_speaker": "Giambattista Passeri",
    },
    "st-chp2-secii-l62-69-passeri-quote-continuation": {
        "quoted_speaker": "Giambattista Passeri",
    },
    "st-chp2-secii-l62-69-bibiana-body-discovered": {
        "claim": "During routine restoration, the body of Saint Bibiana was discovered; Haskell says this was largely due to an accident.",
        "qualification": "Haskell attributes the discovery largely, not exclusively, to accident. The identity and type of the source-described remains remain unresolved.",
    },
    "st-chp2-secii-l62-69-bibiana-statue-aesthetic-interpretation": {
        "claim": "Haskell describes the statue as restrained yet emotional and says that, for the first time, a combination of sensuality and mysticism found in many Counter-Reformation paintings was translated into sculpture.",
        "qualification": "This is Haskell's aesthetic interpretation. 'For the first time' and the source's comparison to many paintings are retained; the paintings are not identified as a specific work group.",
    },
}

OPEN_ENDPOINT_REPAIRS = {
    "st-chp2-sec-ii-l30-40-uncertain-overall-plan": {
        "object_candidate_id": None,
        "open_endpoint_reason": "The source's 'whole area' refers to the central area under Michelangelo's dome, not the entire Basilica; no source-defined candidate for that bounded space is registered.",
    },
    "st-chp2-secii-l52-60-matilda-body-transferred": {
        "object_candidate_id": None,
        "open_endpoint_reason": "The source says Matilda's body was transferred, while cand-4419 identifies Matilda as a person. No distinct remains/body endpoint is registered; destination and date are also unstated.",
        "claim": "Haskell says the Pope had Matilda's body transferred from the province of Mantua; this sentence does not state the destination or date.",
        "qualification": "The transferred object is Matilda's body, not Matilda as a person. The province of Mantua is named as the source; the destination and date are not supplied.",
    },
}

PENDING_TARGETED_REPAIRS = {
    "st-chp2-sec-ii-l30-40-uncertain-overall-plan": "Removed the entire-Basilica endpoint; the central-area antecedent remains an unregistered bounded space.",
    "st-chp2-sec-ii-l30-40-maderno-facade": "Retained the source-to-candidate mention but kept pending: cand-1478 is typed as work while the passage names Carlo Maderno as a person, and aln-1813 remains a conflicting S3 decision.",
    "st-chp2-sec-ii-l30-40-archaeological-investigation": "Added the exact 'early Christian tombs' mention; the open tomb-group type and OCR/print punctuation note remain for targeted follow-up.",
    "st-chp2-sec-ii-l30-40-baldacchino-obstacles": "Added the exact early-Christian-tomb group anchor; the two-obstacle composite still needs separation or a bounded obstacle group.",
    "st-chp2-secii-l52-60-matilda-body-transferred": "Removed the person-as-body endpoint; the source-described remains need a distinct endpoint before this relation can pass.",
    "st-chp2-secii-l71-78-urban-taste-as-explanation-conjectured": "Removed the narrower popular-poems candidate; the conjecture remains pending because 'much of his verse' is an unbounded corpus.",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_jsonl(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return ([json.loads(line) for line in text.splitlines() if line.strip()], raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def read_csv(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return (list(reader), list(reader.fieldnames or []), raw,
            "\r\n" if "\r\n" in text else "\n", raw.startswith(b"\xef\xbb\xbf"))


def write_csv(rows, fields, eol, bom):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator=eol,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + out.getvalue().encode("utf-8")


def git_file(revision: str, relative_path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{relative_path}"], cwd=ROOT)


def source_mentions_at(revision: str, segment_id: str):
    raw = git_file(revision, "04-knowledge/tables/mentions.csv").decode("utf-8-sig")
    return {
        row["mention_id"]: row
        for row in csv.DictReader(io.StringIO(raw, newline=""))
        if row["segment_id"] == segment_id
    }


def atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def source_span(segment, qualifiers, source_lines):
    start_line = int(segment["line_start"])
    end_line = int(segment["line_end"])
    text = "\n".join(source_lines[start_line - 1:end_line])
    pieces = text.splitlines(keepends=True)
    offsets = []
    offset = 0
    for piece in pieces:
        offsets.append((offset, offset + len(piece)))
        offset += len(piece)
    if len(offsets) < end_line - start_line + 1:
        offsets.append((offset, len(text)))
    local_start = int(qualifiers["source_line_start"]) - start_line
    local_end = int(qualifiers.get("source_line_end", qualifiers["source_line_start"])) - start_line
    require(0 <= local_start <= local_end < len(offsets),
            f"invalid source line span: {segment['segment_id']} {qualifiers}")
    return text, offsets[local_start][0], offsets[local_end][1]


def append_once(path: Path, text: str) -> bytes:
    raw = path.read_bytes()
    existing = raw.decode("utf-8-sig")
    require(STAGE_ID not in existing, f"stage already recorded in {path}")
    sep = "" if not existing or existing.endswith("\n") else "\n"
    return raw + (sep + text).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expect-plan", default="")
    args = parser.parse_args()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require(head == BASE_HEAD, f"Expected base HEAD {BASE_HEAD}; found {head}")
    require(subprocess.run(["git", "diff", "--quiet"], cwd=ROOT).returncode == 0,
            "Tracked worktree changes exist; rebase the stage plan against them first")
    for relative, expected in SOURCE_HASHES.items():
        require(sha256((ROOT / relative).read_bytes()) == expected,
                f"Source asset changed: {relative}")
    require(sha256(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 event ledger changed")

    statements, statements_raw, statements_eol, statements_bom = read_jsonl(STATEMENTS_PATH)
    mentions, mention_fields, _, mentions_eol, mentions_bom = read_csv(MENTIONS_PATH)
    roster, roster_fields, _, roster_eol, roster_bom = read_csv(ROSTER_PATH)
    coverage, coverage_fields, _, coverage_eol, coverage_bom = read_csv(COVERAGE_PATH)
    segments, _, _, _ = read_jsonl(SEGMENTS_PATH)
    candidates, _, _, _, _ = read_csv(TABLES / "entity-candidates.csv")

    statements_by_id = {row["statement_id"]: deepcopy(row) for row in statements}
    roster_by_id = {row["statement_id"]: dict(row) for row in roster}
    segments_by_id = {row["segment_id"]: row for row in segments}
    candidate_ids = {row["candidate_id"] for row in candidates}
    require(len(statements_by_id) == len(statements) == 15518,
            "Unexpected current statement size or duplicate IDs")
    require(len(roster_by_id) == len(roster) == len(statements),
            "Unexpected current roster size or duplicate IDs")
    require(set(statements_by_id) == set(roster_by_id), "Statement and roster IDs differ")
    ordered_before = sorted(roster, key=lambda row: int(row["current_order"]))
    require([int(row["current_order"]) for row in ordered_before] == list(range(1, len(roster) + 1)),
            "Roster source order is not continuous")
    require(all(row["current_statement_sha256"] == canonical_hash(statements_by_id[row["statement_id"]])
                for row in roster), "Pre-stage current statement hashes are stale")

    selected = [row for row in ordered_before
                if WINDOW_START <= int(row["current_order"]) <= WINDOW_END]
    require(len(selected) == WINDOW_END - WINDOW_START + 1 == 124,
            "Unexpected B574 source-order window")
    before_counts = Counter(row["current_review_status"] for row in selected)
    require(before_counts == Counter({"reviewed_current_pending": 91,
                                     "reviewed_current_pass": 33}),
            f"Unexpected B574 initial statuses: {before_counts}")
    selected_ids = {row["statement_id"] for row in selected}
    require(PASS_IDS <= selected_ids, "One or more B574 pass decisions are outside the window")
    require(all(roster_by_id[sid]["current_review_status"] == "reviewed_current_pending"
                for sid in PASS_IDS), "B574 would overwrite a non-pending decision")
    require(all(sid in statements_by_id for sid in STATEMENT_REPAIRS | OPEN_ENDPOINT_REPAIRS),
            "A targeted statement repair ID is missing")
    require(set(PENDING_TARGETED_REPAIRS) <= selected_ids,
            "A documented pending repair is outside the B574 window")

    source_lines = (ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md").read_text(
        encoding="utf-8-sig").splitlines()
    source_text_by_segment = {}
    for segment_id in {statements_by_id[sid]["segment_id"] for sid in selected_ids}:
        segment = segments_by_id[segment_id]
        text, _, _ = source_span(segment,
                                 {"source_line_start": segment["line_start"],
                                  "source_line_end": segment["line_end"]}, source_lines)
        source_text_by_segment[segment_id] = text

    mentions_by_segment = defaultdict(list)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(len(mention_by_id) == len(mentions), "Duplicate existing mention IDs")
    for mention in mentions:
        mentions_by_segment[mention["segment_id"]].append(dict(mention))
    for segment_id in source_text_by_segment:
        source_text = source_text_by_segment[segment_id]
        for mention in mentions_by_segment[segment_id]:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            require(source_text[start:end] == mention["surface_form"],
                    f"Existing mention span mismatch: {mention['mention_id']}")

    planned_mentions = []
    for mention_id, segment_id, candidate_id, surface, note in ADDED_MENTIONS:
        require(mention_id not in mention_by_id, f"Mention ID already exists: {mention_id}")
        require(candidate_id in candidate_ids, f"Unknown mention candidate: {candidate_id}")
        text = source_text_by_segment[segment_id]
        positions = []
        start = 0
        while (index := text.find(surface, start)) >= 0:
            positions.append(index)
            start = index + 1
        require(len(positions) == 1, f"Expected one exact occurrence of {surface!r}; found {positions}")
        index = positions[0]
        planned_mentions.append({
            "mention_id": mention_id,
            "segment_id": segment_id,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(index),
            "end_char": str(index + len(surface)),
            "note": note,
        })

    for mention in planned_mentions:
        mentions_by_segment[mention["segment_id"]].append(mention)
        mention_by_id[mention["mention_id"]] = mention

    changed_statement_ids = set()
    statement_by_id_after = {sid: deepcopy(row) for sid, row in statements_by_id.items()}

    # Apply explicit current-version claim and endpoint repairs.
    quote_source = source_text_by_segment["chp-2:02_CHP-2_sec_ii:l30-40"]
    quote_start = quote_source.find("‘It is your great good luck")
    quote_end_token = "even if the words themselves are apocryphal."
    quote_end = quote_source.find(quote_end_token, quote_start)
    require(quote_start >= 0 and quote_end >= 0, "p.34 reported-speech continuation changed")
    quote_end += len(quote_end_token)
    statement_by_id_after["st-chp2-sec-ii-l30-40-urban-reported-praise"]["original_quote"] = quote_source[quote_start:quote_end]

    for sid, changes in STATEMENT_REPAIRS.items():
        row = statement_by_id_after[sid]
        qualifiers = row.setdefault("qualifiers", {})
        for key, value in changes.items():
            if key == "extend_quote_to_apocryphal":
                continue
            qualifiers[key] = deepcopy(value)
        changed_statement_ids.add(sid)
    changed_statement_ids.add("st-chp2-sec-ii-l30-40-urban-reported-praise")

    for sid, changes in OPEN_ENDPOINT_REPAIRS.items():
        row = statement_by_id_after[sid]
        for key, value in changes.items():
            if key == "claim" or key == "qualification":
                row.setdefault("qualifiers", {})[key] = value
            else:
                row[key] = value
        changed_statement_ids.add(sid)

    # The poem set cited by the p.38 conjecture is narrower than "much of his verse".
    taste_id = "st-chp2-secii-l71-78-urban-taste-as-explanation-conjectured"
    taste = statement_by_id_after[taste_id]
    taste_q = taste.setdefault("qualifiers", {})
    taste_q.pop("cited_work_candidate_id", None)
    taste_q["mentioned_candidate_ids"] = ["cand-0209", "cand-1548"]
    taste_q["open_endpoint_reason"] = "Haskell refers to 'much of his verse', an unbounded poetry corpus; the specific popular-poems candidate later in the segment is not established as its identity."
    taste_q["relation_candidate_note"] = "Preserve Haskell's explicitly conjectural explanation of Marino's disappointment. Do not equate the broad verse corpus with the later, narrower popular-poems group."
    changed_statement_ids.add(taste_id)

    # Map source-line mentions to the statement that records that line; include named endpoints
    # only when their candidate has an exact anchor somewhere in the same source segment.
    source_candidate_ids_by_segment = {
        segment_id: {m["candidate_id"] for m in rows}
        for segment_id, rows in mentions_by_segment.items()
    }
    for roster_row in selected:
        sid = roster_row["statement_id"]
        row = statement_by_id_after[sid]
        qualifiers = row.get("qualifiers") or {}
        if qualifiers.get("relation_candidate") is not True:
            continue
        segment = segments_by_id[row["segment_id"]]
        text, span_start, span_end = source_span(segment, qualifiers, source_lines)
        local_mentions = sorted(
            (m for m in mentions_by_segment[row["segment_id"]]
             if span_start <= int(m["start_char"]) and int(m["end_char"]) <= span_end),
            key=lambda m: (int(m["start_char"]), int(m["end_char"]), m["mention_id"]),
        )
        mapped = list(qualifiers.get("mentioned_candidate_ids") or [])
        for mention in local_mentions:
            if mention["candidate_id"] not in mapped:
                mapped.append(mention["candidate_id"])
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint in source_candidate_ids_by_segment.get(row["segment_id"], set()) and endpoint not in mapped:
                mapped.append(endpoint)
        if sid == taste_id:
            mapped = ["cand-0209", "cand-1548"]
        if mapped != qualifiers.get("mentioned_candidate_ids"):
            qualifiers["mentioned_candidate_ids"] = mapped
            changed_statement_ids.add(sid)

    # Keep the historical Maderno candidate visible but do not resolve its type conflict here.
    maderno_id = "st-chp2-sec-ii-l30-40-maderno-facade"
    maderno_q = statement_by_id_after[maderno_id].setdefault("qualifiers", {})
    maderno_q["mentioned_candidate_ids"] = ["cand-4232", "cand-1478"]
    maderno_q["open_endpoint_reason"] = "The source names Carlo Maderno, but cand-1478 is typed as work and alignment aln-1813 remains conflicting. Preserve the source mention while leaving the endpoint pending for S3; do not convert it to a formal relation."
    changed_statement_ids.add(maderno_id)

    # The two p.34/p.35/p.36 exact anchors also close previously unanchored endpoint mentions.
    tomb_ids = {
        "st-chp2-sec-ii-l30-40-archaeological-investigation",
        "st-chp2-sec-ii-l30-40-baldacchino-obstacles",
    }
    for sid in tomb_ids:
        q = statement_by_id_after[sid].setdefault("qualifiers", {})
        mapped = list(q.get("mentioned_candidate_ids") or [])
        for cid in ("cand-4234", "cand-11584"):
            if cid not in mapped:
                mapped.append(cid)
        q["mentioned_candidate_ids"] = mapped
        changed_statement_ids.add(sid)

    # Retain the earlier B433 review of p.38, but remove its false narrow-work mapping.
    # It stays pending because the referenced corpus has no bounded source-defined endpoint.

    # Any new or repaired mention mapping must resolve to a registered candidate and an exact
    # current-source mention span in this segment.
    for sid in changed_statement_ids:
        row = statement_by_id_after[sid]
        q = row.get("qualifiers") or {}
        for cid in q.get("mentioned_candidate_ids", []):
            require(cid in candidate_ids, f"Unknown mentioned_candidate_id {cid} in {sid}")
            require(cid in source_candidate_ids_by_segment.get(row["segment_id"], set()),
                    f"mentioned_candidate_id lacks a source-local mention: {sid} -> {cid}")

    # Recheck repaired quotations against their exact current source segment.
    require(statement_by_id_after["st-chp2-sec-ii-l30-40-urban-reported-praise"]["original_quote"]
            in quote_source, "Expanded p.34 quotation is not a contiguous source substring")

    statements_after = []
    statement_order_ids = [row["statement_id"] for row in statements]
    for sid in statement_order_ids:
        statements_after.append(statement_by_id_after[sid])

    # Insert exact source mentions after the last row of their segment, preserving all other order.
    mentions_after = [dict(row) for row in mentions]
    for segment_id in sorted({row["segment_id"] for row in planned_mentions}):
        new_rows = [row for row in planned_mentions if row["segment_id"] == segment_id]
        last_index = max(i for i, row in enumerate(mentions_after) if row["segment_id"] == segment_id)
        mentions_after[last_index + 1:last_index + 1] = new_rows
    mentions_after_by_segment = defaultdict(list)
    for mention in mentions_after:
        mentions_after_by_segment[mention["segment_id"]].append(mention)

    # Validate only the claim fixes that can be closed; all other problems remain pending.
    for sid in PASS_IDS:
        row = statement_by_id_after[sid]
        q = row.get("qualifiers") or {}
        require(q.get("relation_candidate") is True, f"Expected relation candidate for PASS row {sid}")
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint:
                require(endpoint in q.get("mentioned_candidate_ids", []),
                        f"PASS row endpoint omitted from mentioned_candidate_ids: {sid} -> {endpoint}")
    require(statement_by_id_after["st-chp2-sec-ii-l30-40-uncertain-overall-plan"].get("object_candidate_id") is None,
            "The p.34 bounded-space endpoint was not removed")
    require(statement_by_id_after["st-chp2-secii-l52-60-matilda-body-transferred"].get("object_candidate_id") is None,
            "The p.36 person-as-body endpoint was not removed")
    require("cited_work_candidate_id" not in statement_by_id_after[taste_id]["qualifiers"],
            "The p.38 over-narrow poetry candidate remains")
    for sid in {"st-chp2-secii-l52-60-passeri-quote-poison-fragment",
                "st-chp2-secii-l62-69-passeri-quote-continuation"}:
        require(statement_by_id_after[sid]["qualifiers"].get("quoted_speaker") == "Giambattista Passeri",
                f"Nested Passeri attribution missing on {sid}")

    # Update the current roster while keeping the H9622 event ledger byte-for-byte immutable.
    roster_after_by_id = {row["statement_id"]: dict(row) for row in roster}
    selected_old_refs = {row["statement_id"]: row.get("review_evidence_ref", "") for row in selected}
    for sid in selected_ids:
        row = roster_after_by_id[sid]
        row["review_batch_id"] = BATCH_ID
        row["review_evidence_ref"] = EVIDENCE_REF
        old_ref = selected_old_refs[sid]
        if sid in PASS_IDS:
            row["current_review_status"] = "reviewed_current_pass"
            row["review_outcome"] = "current_semantic_pass_after_targeted_source_and_mention_repair"
            detail = "B574 applied the documented p.34–38 claim, attribution, temporal-scope, or exact endpoint-mention correction; no unresolved issue remains for this statement."
        elif roster_by_id[sid]["current_review_status"] == "reviewed_current_pass":
            row["current_review_status"] = "reviewed_current_pass"
            row["review_outcome"] = "reused_current_pass_after_B574_full_window_fingerprint_check"
            detail = "Existing current PASS reused after current ID, statement, source, segment, and mention fingerprint verification; prior page evidence remains valid."
        else:
            row["current_review_status"] = "reviewed_current_pending"
            row["review_outcome"] = "current_pending_retained_after_targeted_claim_and_endpoint_review"
            detail = PENDING_TARGETED_REPAIRS.get(
                sid,
                "The current source claim was checked and source-local endpoint mentions were recorded where available; the existing open finding remains pending and is preserved below."
            )
        previous = row.get("follow_up_note", "").strip()
        row["follow_up_note"] = f"B574: {detail} Prior current evidence: {old_ref}.\n{previous}".strip()

    for sid in changed_statement_ids:
        roster_after_by_id[sid]["current_statement_sha256"] = canonical_hash(statement_by_id_after[sid])
        if int(roster_after_by_id[sid].get("history_9622_event_count") or "0") > 0:
            roster_after_by_id[sid]["history_9622_current_statement_match"] = (
                "exact" if roster_after_by_id[sid]["history_9622_latest_statement_sha256"]
                == roster_after_by_id[sid]["current_statement_sha256"] else "changed"
            )
            roster_after_by_id[sid]["prior_review_match"] = (
                "exact_object_and_source_segment"
                if roster_after_by_id[sid]["history_9622_current_statement_match"] == "exact"
                and roster_after_by_id[sid]["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )

    changed_segments = {row["segment_id"] for row in planned_mentions}
    mention_hashes = {
        seg_id: canonical_hash(sorted(rows, key=lambda m: m["mention_id"]))
        for seg_id, rows in mentions_after_by_segment.items() if seg_id in changed_segments
    }
    mention_delta_cache = {}
    for row in roster_after_by_id.values():
        seg_id = row["segment_id"]
        if seg_id not in changed_segments:
            continue
        seg_mentions = mentions_after_by_segment[seg_id]
        row["current_segment_mention_count"] = str(len(seg_mentions))
        row["current_segment_mentions_sha256"] = mention_hashes[seg_id]
        if int(row.get("history_9622_event_count") or "0") <= 0:
            continue
        revision = row.get("history_9622_latest_review_commit") or ""
        cache_key = (revision, seg_id)
        if cache_key not in mention_delta_cache:
            old_mentions = source_mentions_at(revision, seg_id)
            now_mentions = {m["mention_id"]: m for m in seg_mentions}
            mention_delta_cache[cache_key] = {
                "changed": sorted(mid for mid in old_mentions.keys() & now_mentions.keys()
                                  if old_mentions[mid] != now_mentions[mid]),
                "removed": sorted(old_mentions.keys() - now_mentions.keys()),
                "added": sorted(now_mentions.keys() - old_mentions.keys()),
            }
        row["history_9622_mention_delta"] = json.dumps(
            mention_delta_cache[cache_key], ensure_ascii=False, separators=(",", ":")
        )

    roster_after = [roster_after_by_id[row["statement_id"]] for row in roster]
    require([int(row["current_order"]) for row in roster_after] == list(range(1, len(roster_after) + 1)),
            "B574 changed the stable current order")
    after_counts = Counter(row["current_review_status"] for row in roster_after)
    require(after_counts["reviewed_current_pass"] == 8791 and
            after_counts["reviewed_current_pending"] == 6727,
            f"Unexpected post-stage status counts: {after_counts}")
    selected_after = [r for r in roster_after if WINDOW_START <= int(r["current_order"]) <= WINDOW_END]
    require(len(selected_after) == 124 and
            sum(r["current_review_status"] == "reviewed_current_pass" for r in selected_after) == 81 and
            sum(r["current_review_status"] == "reviewed_current_pending" for r in selected_after) == 43,
            "B574 post-window disposition counts are unexpected")

    # Full roster checks use the final statement and mention versions.
    statement_hashes = {sid: canonical_hash(row) for sid, row in statement_by_id_after.items()}
    require(all(row["current_statement_sha256"] == statement_hashes[row["statement_id"]]
                for row in roster_after), "A current statement hash is stale after B574")
    for seg_id, seg_rows in mentions_after_by_segment.items():
        if seg_id not in changed_segments:
            continue
        for mention in seg_rows:
            start, end = int(mention["start_char"]), int(mention["end_char"])
            require(source_text_by_segment[seg_id][start:end] == mention["surface_form"],
                    f"Post-stage mention span mismatch: {mention['mention_id']}")
        digest = canonical_hash(sorted(seg_rows, key=lambda m: m["mention_id"]))
        require(all(r["current_segment_mention_count"] == str(len(seg_rows)) and
                    r["current_segment_mentions_sha256"] == digest
                    for r in roster_after if r["segment_id"] == seg_id),
                f"Post-stage roster segment mention fingerprint mismatch: {seg_id}")

    # Exact unaffected-table checks.
    protected_paths = [TABLES / "alignment.csv", TABLES / "entity-candidates.csv",
                       TABLES / "relations.csv", HISTORY_PATH]
    protected_hashes = {path: sha256(path.read_bytes()) for path in protected_paths}
    require(protected_hashes[HISTORY_PATH] == HISTORY_SHA256,
            "H9622 ledger changed before stage application")
    linked_relations = []
    relation_rows, _, _, _, _ = read_csv(TABLES / "relations.csv")
    for relation in relation_rows:
        span = "|".join(str(value) for value in relation.values())
        if any(sid in span for sid in selected_ids):
            linked_relations.append(relation)
    relation_counts = Counter(row["status"] for row in linked_relations)
    linked_relation_ids = [row["relation_id"] for row in linked_relations]

    # Keep the existing coverage protocol and append only a concise process pointer.
    coverage_after = [dict(row) for row in coverage]
    coverage_notes = {
        "chp-2:02_CHP-2_sec_ii:l30-40": "B574: p.34 exact work-group and tomb-group mention anchors, source attribution, and the bounded central-area endpoint were corrected; Maderno/aln-1813 and open space/type findings remain pending.",
        "chp-2:02_CHP-2_sec_ii:l42-50": "B574: p.35 line-scoped candidate mappings, iconographic-form anchors, and the post-construction Cross timing were checked; composite reception/feature and Ginnasi-chair findings remain pending.",
        "chp-2:02_CHP-2_sec_ii:l52-60": "B574: p.36 exact relic-group anchor and statement mappings were added; the Matilda remains endpoint is detached from the person and remains pending.",
    }
    for seg_id, note in coverage_notes.items():
        matches = [row for row in coverage_after if row["segment_id"] == seg_id]
        require(len(matches) == 1, f"Expected one coverage row for {seg_id}")
        matches[0]["note"] = (matches[0]["note"].rstrip() + " " + note).strip()

    pass_outcomes = Counter(roster_after_by_id[sid]["review_outcome"] for sid in PASS_IDS)
    h9622_matches = Counter(r["history_9622_current_statement_match"] for r in roster_after
                            if int(r.get("history_9622_event_count") or "0") > 0)
    mention_total = len(mentions_after)
    statement_total = len(statements_after)
    changed_hashes = len(changed_statement_ids)
    pass_percent = 100 * after_counts["reviewed_current_pass"] / statement_total
    pending_percent = 100 * after_counts["reviewed_current_pending"] / statement_total
    source_hash = SOURCE_HASHES["02-sources/02-Markdown/02_CHP-2_sec_ii.md"]
    pdf_hash = SOURCE_HASHES["02-sources/01-book/CHP-2.pdf"]

    process_record = f"""

<a id=\"{STAGE_ID}\"></a>
### 2026-11-03 S2 当前版语义修复阶段 B574（当前顺序1536–1659）

**阶段范围与复用。** 连续覆盖124条当前statement，源序1536–1659，对应第二章第二节印刷p.34–38。33条原有PASS在statement、来源、segment及mention指纹核平后复用；91条pending逐项对照现行statement与原页finding处理，其中48条在本阶段修订/补齐后转为当前PASS，43条保留pending。B433已复核的1659项只处理其已记录的过窄诗作候选映射，不重复宣称重审原页。

**原文和当前版本依据。** 权威 `CHP-2.pdf` SHA-256=`{pdf_hash}`；第二节Markdown SHA-256=`{source_hash}`。核读来源行L30–78及印刷p.34–38（PDF物理页15–19）；此前逐页视觉核读记录见`s2-independent-review-chp1-2-4-20261020.md` Chapter 2 batches 10–14，B430–B432核平当前ID 1536–1658的指纹，B433记录1659–1660。原页finding只在当前ID、source、segment及mention版本一致处复用；本阶段的claim/mention修订不冒充对修订版的独立验收。

**本阶段裁决。** 补入{len(planned_mentions)}条精确mention：Bernini既有雕塑/半身像组、首批纪念性作品组、早期基督教墓群、扭柱形式/图像方案、四圣遗物组，以及以“his enterprises”锚定Urban VIII的代词指涉。修正Bernini首次纪念作品的时间范围、Urban/Bernini引语及Haskell后续评价、匿名观察者对立面铭文的嵌套讽刺、Cross改案发生在开工后的时序；恢复completed programme的整体结构评价和Passeri引语者。将“中央区域”从整座St Peter’s端点分离，将Matilda遗体从Matilda人物端点分离。针对Marino诗歌的推测移除不相同一的特定诗组映射，开放范围继续pending。

**同段指纹维护。** p.34新mention改变了整段mention集合；顺序1535的既有PASS与本批共享该段，只同步其段内mention数量/hash及历史mention差异，statement和裁决未变。

仍pending的43项包括：未名任职者、Maderno候选类型/`aln-1813`冲突、未登记的中央空间、双重障碍与复合叙述、Matilda遗体端点、未名受众或社会群体、作品/地点类型与版本、关系角色拆分、未界定诗歌总体及其它原findings。相关候选、S3 alignment、KU和S6关系没有被强行更改。

| 阶段量 | 数量 | 结果 |
|---|---:|---|
| 当前连续statement | 124 | 1536–1659 |
| 原有PASS复用 | 33 | 当前指纹一致 |
| pending转当前PASS | 48 | 修订后逐项按原页定位核对 |
| 保留pending | 43 | 原因和后续去向保留 |
| 新增精确mention | {len(planned_mentions)} | 当前S0 segment偏移逐一核实 |
| statement当前hash更新 | {changed_hashes} | 历史review hash不改写 |

**下游关系与历史裁决。** 逐条对照`relations.csv`中链接本窗口statement的{len(linked_relations)}条关系（`{", ".join(linked_relation_ids)}`；状态`{json.dumps(dict(relation_counts), ensure_ascii=False)}`）及原文范围；formal端点、谓词和状态均仍受修订后当前claim支持。未改正式边、端点、谓词或状态；缺少遗体端点的转移关系继续pending。`alignment.csv`、`entity-candidates.csv`及H9622不可变事件账本均未改。H9622当前statement/mention指纹重算为exact/changed，历史裁决及事件数量不回写。本阶段不构成全书S2独立语义接收。

**批后状态与复核。** 当前statement {statement_total}条、mention {mention_total}条；PASS {after_counts['reviewed_current_pass']}（{pass_percent:.2f}%），pending {after_counts['reviewed_current_pending']}（{pending_percent:.2f}%）。H9622当前映射hash匹配计数：`{json.dumps(dict(h9622_matches), ensure_ascii=False)}`。新增mention及statement mappings逐项以当前源行、精确span和同segment候选存在性断言；全roster statement hash、连续序、受影响segment mention计数/hash重算通过。脚本`{Path(__file__).name}`，基线HEAD `{BASE_HEAD}`，计划哈希由dry-run输出记录。后续按B574保留的原页finding继续处理，不重复已PASS条目。
""".strip()

    result_index = (
        f"\n\n### 2026-11-03 S2 current semantic repair stage B574 (1536–1659)\n\n"
        f"Reviewed 124 continuous current statements: reused 33 current PASS, promoted 48 pending to PASS, retained 43 pending, and added {len(planned_mentions)} exact mentions. "
        f"Current full-book totals: {statement_total} statements, {mention_total} mentions, {after_counts['reviewed_current_pass']} PASS, {after_counts['reviewed_current_pending']} pending. "
        f"S3 alignment, candidate registry, formal relations, and immutable H9622 outcomes were not changed. See [B574 process record](../process/stages.md#{STAGE_ID}).\n"
    )

    current_result_raw = CURRENT_RESULT_PATH.read_bytes()
    current_result_text = current_result_raw.decode("utf-8-sig")
    old_latest = "当前源序范围1432–1535共104条（96 PASS、8 pending），下一窗口1536–1635。"
    new_latest = (f"B574当前版范围1536–1659共124条（81 PASS、43 pending）；48条pending在本阶段转为PASS。"
                 f"全局当前PASS {after_counts['reviewed_current_pass']}、pending {after_counts['reviewed_current_pending']}。")
    require(old_latest in current_result_text, "Current result summary no longer has the expected B573 handoff text")
    current_result_text = current_result_text.replace(old_latest, new_latest, 1)
    current_result_text = current_result_text.replace(
        "15,518条statement、27,350条mention；逐ID清单15,518/15,518均有当前决定：PASS 8,743（56.34%）、pending 6,775（43.66%）",
        f"{statement_total:,}条statement、{mention_total:,}条mention；逐ID清单{statement_total:,}/{statement_total:,}均有当前决定：PASS {after_counts['reviewed_current_pass']:,}（{pass_percent:.2f}%）、pending {after_counts['reviewed_current_pending']:,}（{pending_percent:.2f}%）",
        1)
    current_result_output = (b"\xef\xbb\xbf" if current_result_raw.startswith(b"\xef\xbb\xbf") else b"") + current_result_text.encode("utf-8")

    # Preserve all untouched JSONL lines exactly; only changed records are re-serialized.
    raw_lines = statements_raw.decode("utf-8-sig").splitlines()
    rendered = []
    for line in raw_lines:
        if not line.strip():
            rendered.append(line)
            continue
        sid = json.loads(line)["statement_id"]
        if sid in changed_statement_ids:
            rendered.append(json.dumps(statement_by_id_after[sid], ensure_ascii=False, separators=(",", ":")))
        else:
            rendered.append(line)
    statements_output = ((b"\xef\xbb\xbf" if statements_bom else b"") +
                         (statements_eol.join(rendered) + statements_eol).encode("utf-8"))
    mentions_output = write_csv(mentions_after, mention_fields, mentions_eol, mentions_bom)
    roster_output = write_csv(roster_after, roster_fields, roster_eol, roster_bom)
    coverage_output = write_csv(coverage_after, coverage_fields, coverage_eol, coverage_bom)
    stage_output = append_once(STAGES_PATH, process_record + "\n")
    result_index_output = append_once(RESULT_STAGES_PATH, result_index)

    outputs = {
        STATEMENTS_PATH: statements_output,
        MENTIONS_PATH: mentions_output,
        ROSTER_PATH: roster_output,
        COVERAGE_PATH: coverage_output,
        STAGES_PATH: stage_output,
        RESULT_STAGES_PATH: result_index_output,
        CURRENT_RESULT_PATH: current_result_output,
    }
    plan = {
        "batch_id": BATCH_ID,
        "base_head": BASE_HEAD,
        "window": [WINDOW_START, WINDOW_END],
        "initial_status": dict(before_counts),
        "pass_ids": sorted(PASS_IDS),
        "pending_repairs": sorted(PENDING_TARGETED_REPAIRS),
        "changed_statement_count": changed_hashes,
        "new_mentions": [{k: m[k] for k in ("mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char")} for m in planned_mentions],
        "post_status": dict(after_counts),
        "post_pending_hash": dict(h9622_matches),
        "post_totals": {"statements": statement_total, "mentions": mention_total,
                        "pass": after_counts["reviewed_current_pass"],
                        "pending": after_counts["reviewed_current_pending"]},
        "linked_relations": len(linked_relations),
        "linked_relation_status": dict(relation_counts),
        "output_sha256": {str(path.relative_to(ROOT)): sha256(data) for path, data in outputs.items()},
    }
    plan_sha = sha256(json.dumps(plan, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":")).encode("utf-8"))
    require(not args.expect_plan or args.expect_plan == plan_sha,
            f"Plan hash mismatch: expected {args.expect_plan}; found {plan_sha}")
    plan["plan_sha256"] = plan_sha
    plan["mode"] = "apply" if args.apply else "preview"
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {}
    try:
        for path in outputs:
            backup = path.with_name(path.name + ".bak-b574-20261103")
            require(not backup.exists(), f"Recovery copy already exists; refusing overwrite: {backup}")
            backup.write_bytes(path.read_bytes())
            backups[path] = backup
        for path, data in outputs.items():
            atomic_write(path, data)
        require(sha256(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
                "Immutable H9622 event ledger changed during apply")
        for path in protected_paths:
            require(sha256(path.read_bytes()) == protected_hashes[path],
                    f"Protected downstream table changed during apply: {path.name}")
        final_rows, _, _, _ = read_jsonl(STATEMENTS_PATH)
        final_roster, _, _, _, _ = read_csv(ROSTER_PATH)
        require(len(final_rows) == 15518 and len(final_roster) == 15518,
                "Statement or roster row count changed during apply")
        require(all(row["current_statement_sha256"] == canonical_hash(
                    {s["statement_id"]: s for s in final_rows}[row["statement_id"]])
                    for row in final_roster), "Persisted B574 roster hashes failed")
    except Exception:
        for path, backup in backups.items():
            if backup.exists():
                atomic_write(path, backup.read_bytes())
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {str(path.relative_to(ROOT)): str(backup.relative_to(ROOT)) for path, backup in backups.items()},
        "written_hashes": {str(path.relative_to(ROOT)): sha256(path.read_bytes()) for path in outputs},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
