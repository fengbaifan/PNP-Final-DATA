#!/usr/bin/env python3
"""Adjudicate S2 current-review rows 1659-1758 against printed pp. 39-40."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
MENTIONS_PATH = TABLES / "mentions.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
RELATIONS_PATH = TABLES / "relations.csv"
SEGMENTS_PATH = TABLES / "segments.jsonl"

BASE_HEAD = "098a1940f5a46543c9468859b91c08a70b2c23f9"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
SOURCE_HASHES = {
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
BATCH_ID = "S2-B433-CH2-P39-P40-1659-1758"
STAGE_ID = "2026-11-03-s2-current-review-stage-b433-order-1659-1758"
EVIDENCE_REF = f"stages.md#{STAGE_ID}"

# Rows whose pending findings can be closed after the page, source, and current
# mention mappings are checked. Two findings remain open below.
PASS_IDS = {
    "st-chp2-secii-l80-89-marcello-welcomes-pietro",
    "st-chp2-secii-l80-89-pietro-aesthetic-capacity-and-domenichino-contrast",
    "st-chp2-secii-l80-89-pietro-requested-subjects",
    "st-chp2-secii-l80-89-pietro-welcome-to-marcello",
    "st-chp2-secii-l80-89-annibale-comparison",
    "st-chp2-secii-l80-89-pietro-painted-polyxena",
    "st-chp2-secii-l80-89-pietro-painted-rape-of-sabines",
    "st-chp2-secii-l80-89-pietro-painted-triumph-of-bacchus",
    "st-chp2-secii-l80-89-processional-style-development",
    "st-chp2-secii-l80-89-marcello-chose-gallery-subjects",
    "st-chp2-secii-l80-89-giulio-made-cardinal",
    "st-chp2-secii-l80-89-marcello-papal-treasurer",
    "st-chp2-secii-l80-89-brothers-promoted-pietro",
    "st-chp2-secii-l80-89-chronicler-quote-on-sacchetti-protection",
    "st-chp2-secii-l80-89-marcello-pope-friend-confidant",
    "st-chp2-secii-l80-89-sacchetti-influence-on-taste",
    "st-chp2-secii-l80-89-pietro-grand-manner-in-bibiana-frescoes",
    "st-chp2-secii-l91-104-pietro-fresco-classical-detail-continuation",
    "st-chp2-secii-l91-104-pietro-success-assured",
    "st-chp2-secii-l91-104-urban-company-of-poets",
    "st-chp2-secii-l91-104-urban-lifelong-love-of-poetry",
    "st-chp2-secii-l91-104-urban-poems-nature-and-country-life",
    "st-chp2-secii-l91-104-urban-writes-verses-and-guides-content",
    "st-chp2-secii-l91-104-urban-delegates-business-audiences-to-nephew",
    "st-chp2-secii-l91-104-1631-volume-illustrated-by-bernini",
    "st-chp2-secii-l91-104-1631-volume-produced-by-jesuits",
    "st-chp2-secii-l91-104-urban-poetry-editions-after-accession",
    "st-chp2-secii-l91-104-bernini-makes-urban-portrait-busts",
    "st-chp2-secii-l91-104-urban-busts-as-self-image",
    "st-chp2-secii-l91-104-urban-busts-contrast-with-royal-portraits",
    "st-chp2-secii-l91-104-urban-portrait-image-changes-over-rule",
    "st-chp2-secii-l91-104-urban-portrait-hieratic-dignity",
}
PENDING_NOTES = {
    "st-chp2-secii-l91-104-baroque-flattery-interpretation": (
        "原文分作两个完整判断：flattery是Baroque的重要成分；Urban VIII给予其充分表达机会。"
        "本statement仍把文化判断与人物语境合在一起，需另行拆分或确认准确的原子化表示；保留pending。"
    ),
    "st-chp2-secii-l91-104-urban-portrait-appearance-continues-at-l119": (
        "p.40底部句子在“his long moustaches and beard”处截断，后续在p.41继续；"
        "待逐页核对并链接续句，不把未审读的后文并入本claim。"
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12471", "canonical_name": "The Sacrifice of Polyxena (Pietro da Cortona; large canvas for Marcello Sacchetti)",
        "suggested_type": "work", "detail": "Haskell names this as one of three large canvases painted by Pietro for Sacchetti. The candidate is bounded by this source title; date, surviving version, and present location are not stated.",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l80-89#L83",
    },
    {
        "candidate_id": "cand-12472", "canonical_name": "The Triumph of Bacchus (Pietro da Cortona; large canvas for Marcello Sacchetti)",
        "suggested_type": "work", "detail": "Haskell names this as one of three large canvases painted by Pietro for Sacchetti. The candidate is bounded by this source title; date, surviving version, and present location are not stated.",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l80-89#L83",
    },
    {
        "candidate_id": "cand-12473", "canonical_name": "Giulio and Marcello Sacchetti as the brothers named on printed p. 39",
        "suggested_type": "family", "detail": "Source-bounded pair: Giulio and Marcello, named immediately before “the brothers”. Do not merge this bounded pair with the broader Sacchetti-family candidate cand-4452 without identity and membership evidence.",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l80-89#L87",
    },
    {
        "candidate_id": "cand-12474", "canonical_name": "Poetry as a literary practice valued by Urban VIII (Haskell)",
        "suggested_type": "term", "detail": "The abstract literary practice of poetry, distinct from the work group of poems by Urban VIII (cand-4494).",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l91-104#L96",
    },
    {
        "candidate_id": "cand-12475", "canonical_name": "Nature and simple country life as subjects of Urban VIII's poems (Haskell)",
        "suggested_type": "term", "detail": "A source-defined subject theme in poems by Urban VIII; distinct from the poem corpus cand-4494 and from the villa as a place.",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l91-104#L97",
    },
    {
        "candidate_id": "cand-12476", "canonical_name": "Unnamed foreign diplomats directed to Urban VIII's nephew (Haskell)",
        "suggested_type": "", "detail": "The source names an unnamed class of foreign diplomats but gives no members or bounded delegation. Keep candidate type and identity undecided.",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l91-104#L98",
    },
    {
        "candidate_id": "cand-12477", "canonical_name": "Bernini's unnamed royal patrons compared with Urban VIII portraits (Haskell)",
        "suggested_type": "", "detail": "The source uses a plural comparison class and names no patrons or bounded membership. Keep candidate type and identity undecided.",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l91-104#L102",
    },
    {
        "candidate_id": "cand-12478", "canonical_name": "First fine editions of Urban VIII's poems before the 1631 volume (titles unspecified)",
        "suggested_type": "archive", "detail": "Haskell reports plural fine editions issuing from Rome within months of Urban VIII's accession and says the sequence culminated in a splendid 1631 volume. Individual titles and dates are not supplied; keep the group distinct from volume cand-4498.",
        "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l91-104#L100",
    },
]

ALIGNMENT_NOTES = {
    "cand-12471": "Title-level source work; no cross-chapter identity comparison, date, version, or location has been made. Keep S3 undecided and do not register a KU or formal relation.",
    "cand-12472": "Title-level source work; no cross-chapter identity comparison, date, version, or location has been made. Keep S3 undecided and do not register a KU or formal relation.",
    "cand-12473": "Only Giulio and Marcello are supported as the referent of ‘the brothers’ here. Keep this pair distinct from broader family group cand-4452 pending cross-chapter identity review.",
    "cand-12474": "This is the abstract concept poetry, not Urban VIII’s poems (work group cand-4494). No broader identity comparison has been made; keep S3 undecided.",
    "cand-12475": "This is the subject theme named for Urban VIII’s poems, not the poem corpus or Castel Gandolfo villa. No broader identity comparison has been made; keep S3 undecided.",
    "cand-12476": "The text identifies only an unnamed plural class. Both identity and taxonomy remain unresolved; keep the audience endpoint open and do not formalize a relation.",
    "cand-12477": "The text identifies only Bernini’s unnamed royal-patron comparison class. Membership and taxonomy remain unresolved; keep the comparison endpoint open.",
    "cand-12478": "The source reports a group of earlier print editions but supplies no titles or dates. Keep this source-defined archive group separate from the 1631 volume cand-4498 pending S3 identity review.",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")
    return digest(data)


def read_jsonl(path: Path) -> tuple[list[dict], list[str], bytes, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    newline = "\r\n" if "\r\n" in text else "\n"
    return rows, lines, raw, newline


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes, str, bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    first_lf = raw.find(b"\n")
    newline = "\r\n" if first_lf > 0 and raw[first_lf - 1:first_lf] == b"\r" else "\n"
    return rows, fields, raw, newline, raw.startswith(b"\xef\xbb\xbf")


def write_csv(rows: list[dict[str, str]], fields: list[str], newline: str,
              bom: bool) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    temp = path.with_name(path.name + ".b433.tmp")
    temp.write_bytes(data)
    temp.replace(path)


def source_segment_text(segment_id: str, source_file: str) -> str:
    suffix = segment_id.rsplit(":l", 1)[1]
    start_text, end_text = suffix.split("-", 1)
    start, end = int(start_text), int(end_text)
    lines = (ROOT / source_file).read_text(encoding="utf-8-sig").splitlines()
    return "\n".join(lines[start - 1:end])


def unique_span(text: str, surface: str) -> tuple[int, int]:
    first = text.find(surface)
    require(first >= 0 and text.find(surface, first + 1) < 0,
            f"Expected one source occurrence for mention: {surface!r}")
    return first, first + len(surface)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="write the reviewed batch; default is a guarded dry run")
    args = parser.parse_args()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True).strip()
    require(head == BASE_HEAD, f"Unexpected base commit: {head}")
    for relative, expected in SOURCE_HASHES.items():
        require(digest((ROOT / relative).read_bytes()) == expected,
                f"Source file hash changed: {relative}")
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 event ledger differs from the reviewed baseline")

    statements, statement_lines, statement_raw, statement_eol = read_jsonl(STATEMENTS_PATH)
    roster, roster_fields, _, roster_eol, roster_bom = read_csv(ROSTER_PATH)
    mentions, mention_fields, _, mention_eol, mention_bom = read_csv(MENTIONS_PATH)
    candidates, candidate_fields, _, candidate_eol, candidate_bom = read_csv(CANDIDATES_PATH)
    alignments, alignment_fields, _, alignment_eol, alignment_bom = read_csv(ALIGNMENT_PATH)
    relations, _, relation_raw, _, _ = read_csv(RELATIONS_PATH)
    segments, _, _, _ = read_jsonl(SEGMENTS_PATH)

    statement_by_id = {row["statement_id"]: row for row in statements}
    roster_by_id = {row["statement_id"]: row for row in roster}
    segment_by_id = {row["segment_id"]: row for row in segments}
    require(len(statements) == len(roster) == 15512,
            f"Unexpected statement/roster sizes: {len(statements)}/{len(roster)}")
    require(len(statement_by_id) == len(statements) and len(roster_by_id) == len(roster),
            "Duplicate statement or roster identifier")
    require(set(statement_by_id) == set(roster_by_id),
            "Statement and roster ID sets differ")
    for row in roster:
        require(row["current_statement_sha256"] ==
                canonical_hash(statement_by_id[row["statement_id"]]),
                f"Current statement fingerprint mismatch: {row['statement_id']}")

    selected = sorted((row for row in roster
                       if 1659 <= int(row["current_order"]) <= 1758),
                      key=lambda row: int(row["current_order"]))
    require([int(row["current_order"]) for row in selected] == list(range(1659, 1759)),
            "Selected current-order interval is not exactly 1659-1758")
    pending_ids = {row["statement_id"] for row in selected
                   if row["current_review_status"] == "reviewed_current_pending"}
    require(len(selected) == 100 and len(pending_ids) == 34,
            f"Expected 100 rows and 34 pending findings; got {len(selected)}/{len(pending_ids)}")
    require(pending_ids == PASS_IDS | set(PENDING_NOTES),
            f"The current pending set changed: {sorted(pending_ids ^ (PASS_IDS | set(PENDING_NOTES)))}")
    require(sum(row["current_review_status"] == "reviewed_current_pass"
                for row in selected) == 66,
            "Expected 66 pre-existing current PASS rows to reuse")
    require(all(row["history_9622_source_match"] == "true" for row in selected
                if int(row["history_9622_event_count"] or "0") > 0),
            "A selected historical row has a source-version mismatch")

    mention_by_id = {row["mention_id"]: row for row in mentions}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    require(len(mention_by_id) == len(mentions), "Duplicate mention ID")
    require(len(candidate_by_id) == len(candidates), "Duplicate candidate ID")
    alignment_candidate_ids = {row["candidate_id"] for row in alignments if row["candidate_id"]}
    require(max(int(row["candidate_id"].split("-")[1]) for row in candidates) == 12470,
            "Candidate allocation point changed")
    require(max(int(row["alignment_id"].split("-")[1]) for row in alignments
                if row["alignment_id"].startswith("aln-")) == 12799,
            "Alignment allocation point changed")
    require(all(row["candidate_id"] not in candidate_by_id for row in NEW_CANDIDATES),
            "A planned candidate ID already exists")
    require(not any(candidate_id in alignment_candidate_ids
                    for candidate_id in {c["candidate_id"] for c in NEW_CANDIDATES}),
            "A planned candidate already has an alignment row")
    require(not any(c["canonical_name"] == row["canonical_name"] and
                    c["suggested_type"] == row["suggested_type"]
                    for c in NEW_CANDIDATES for row in candidates),
            "A planned candidate duplicates an existing canonical-name/type pair")

    reviewed_range_segment_ids = {row["segment_id"] for row in selected}
    expected_range_segment_ids = {
        "chp-2:02_CHP-2_sec_ii:l80-89",
        "chp-2:02_CHP-2_sec_ii:l91-104",
        "chp-2:02_CHP-2_sec_ii:l106-107",
        "chp-2:02_CHP-2_sec_ii:l109-113",
        "chp-2:02_CHP-2_sec_ii:l115-116",
        "chp-2:02_CHP-2_sec_ii:l118-125",
    }
    require(reviewed_range_segment_ids == expected_range_segment_ids,
            f"Unexpected source segments in batch: {sorted(reviewed_range_segment_ids)}")
    mention_update_segments = {
        "chp-2:02_CHP-2_sec_ii:l80-89",
        "chp-2:02_CHP-2_sec_ii:l91-104",
    }
    for row in selected:
        segment = segment_by_id[row["segment_id"]]
        require(segment["sha256"] == row["segment_sha256"],
                f"Source segment hash changed: {row['segment_id']}")
        require(segment.get("asset_sha256", "") == row["source_asset_sha256"],
                f"Source asset hash changed: {row['segment_id']}")
    require(all(row["current_review_status"] == "reviewed_current_pass" or
                row["current_review_status"] == "reviewed_current_pending"
                for row in selected), "Unexpected review status in selected rows")

    # Confirm the source-sized page spans and exact phrase locations before writing.
    p39_segment = "chp-2:02_CHP-2_sec_ii:l80-89"
    p40_segment = "chp-2:02_CHP-2_sec_ii:l91-104"
    p39_text = source_segment_text(p39_segment, segment_by_id[p39_segment]["source_file"])
    p40_text = source_segment_text(p40_segment, segment_by_id[p40_segment]["source_file"])
    require("The Sacrifice of Polyxena" in p39_text and "The Triumph of Bacchus" in p39_text,
            "Printed p. 39 work titles are not present in the source segment")
    require("warmth and.breadth" in p39_text,
            "The p. 39 punctuation anomaly is absent or changed")
    require("A triumphant career lay ahead." in p40_text and "even Greek" in p40_text,
            "Printed p. 40 continuation text is not present")

    # Build candidate additions and retain six source-only references as undecided.
    after_candidates = [dict(row) for row in candidates]
    for spec in NEW_CANDIDATES:
        row = {field: "" for field in candidate_fields}
        row.update({
            "candidate_id": spec["candidate_id"],
            "canonical_name": spec["canonical_name"],
            "suggested_type": spec["suggested_type"],
            "status": "open",
            "detail": spec["detail"],
            "candidate_origin": "body-mention",
            "candidate_source_ref": spec["candidate_source_ref"],
        })
        after_candidates.append(row)
    for candidate_id in ("cand-11886", "cand-11887"):
        require(candidate_id in candidate_by_id, f"Missing source group: {candidate_id}")
    for row in after_candidates:
        if row["candidate_id"] == "cand-11886":
            row["suggested_type"] = ""
            row["detail"] = (
                "Unnamed human audience described as connoisseurs; candidate identity and type "
                "remain open. Do not force this group into term or merge it with other connoisseur groups."
            )
        elif row["candidate_id"] == "cand-11887":
            row["suggested_type"] = ""
            row["detail"] = (
                "Unnamed human company of poets; no members or formal institution are identified. "
                "Keep the human-group type and identity open and distinct from Urban VIII's poem corpus."
            )

    after_alignments = [dict(row) for row in alignments]
    first_alignment_id = 12800
    for offset, spec in enumerate(NEW_CANDIDATES):
        candidate_id = spec["candidate_id"]
        row = {field: "" for field in alignment_fields}
        row.update({
            "alignment_id": f"aln-{first_alignment_id + offset:05d}",
            "candidate_id": candidate_id,
            "decision": "undecided",
            "process_ref": f"03-processing/patrons-and-painters-full-book-s2/process/{EVIDENCE_REF}",
            "resolution_note": (
                f"source_ref={spec['candidate_source_ref']}; {ALIGNMENT_NOTES[candidate_id]}"
            ),
        })
        after_alignments.append(row)

    # Copy and patch statements by stable ID. The source's two-page sentence and
    # evaluation layers are preserved; source-bounded identity work remains S3-open.
    after_statements = json.loads(json.dumps(statements, ensure_ascii=False))
    after_by_id = {row["statement_id"]: row for row in after_statements}

    def patch(sid: str, *, subject=..., object_id=..., predicate=..., quote=...,
              qualifiers: dict | None = None) -> None:
        row = after_by_id[sid]
        if subject is not ...:
            row["subject_candidate_id"] = subject
        if object_id is not ...:
            row["object_candidate_id"] = object_id
        if predicate is not ...:
            row["predicate"] = predicate
        if quote is not ...:
            row["original_quote"] = quote
        if qualifiers:
            row["qualifiers"].update(qualifiers)

    patch("st-chp2-secii-l80-89-marcello-welcomes-pietro", qualifiers={
        "claim": "Haskell says the eager young Pietro was especially welcome to Marcello Sacchetti.",
        "qualification": "The separate phrase calling Marcello a new type of patron is recorded as a profile statement; this sentence does not name a specific commission.",
        "mentioned_candidate_ids": ["cand-2316", "cand-0342"],
    })
    patch("st-chp2-secii-l80-89-pietro-aesthetic-capacity-and-domenichino-contrast", qualifiers={
        "claim": "Haskell says Pietro could give warm and vivid life to Marcello's dreams of the past, recreate the trappings of antiquity, and avoid the coldness he attributes to a classical artist such as Domenichino.",
        "qualification": "This is Haskell's aesthetic comparison. The source frames the dreams as Marcello's; the comparison does not establish a formal artistic opposition or influence relation.",
        "mentioned_candidate_ids": ["cand-0342", "cand-2314", "cand-0932"],
    })
    patch("st-chp2-secii-l80-89-pietro-requested-subjects", qualifiers={
        "claim": "Haskell characterizes Pietro as docile and says that even in later fame he would always ask his patrons to choose subjects.",
        "qualification": "‘Docile’ is Haskell's characterization of the practice described; the patrons are an unnamed plural group and no individual subject is specified.",
        "mentioned_candidate_ids": ["cand-0356", "cand-12295"],
    })
    patch("st-chp2-secii-l80-89-pietro-welcome-to-marcello", subject="cand-2314",
          object_id=None, predicate="authorial_personal_characterization",
          qualifiers={
              "claim": "Haskell describes Marcello as learned, steeped in classical culture, and a poet; he calls him a ‘new type of patron.’",
              "qualification": "This is Haskell's profile and typological interpretation of Marcello. Pietro's separate welcome relation is recorded in st-chp2-secii-l80-89-marcello-welcomes-pietro.",
              "relation_candidate": False,
              "relation_candidate_note": "Authorial profile statement, not a relation between Marcello and Pietro.",
              "mentioned_candidate_ids": ["cand-2314"],
          })
    patch("st-chp2-secii-l80-89-annibale-comparison", qualifiers={
        "claim": "Haskell says Annibale Carracci had the same artistic gift; since Annibale's death, he says, no painter had matched Pietro's freshness, grandeur, and seriousness in evoking the fables of ancient Rome and Greece.",
        "qualification": "The comparison and evaluation are Haskell's. The printed page reads ‘fables’; this does not assert influence or artistic descent.",
        "mentioned_candidate_ids": ["cand-0342", "cand-0576", "cand-3126", "cand-4474"],
    })
    patch("st-chp2-secii-l80-89-pietro-painted-polyxena", object_id="cand-12471",
          qualifiers={
              "claim": "Haskell says Pietro painted a large canvas of The Sacrifice of Polyxena for Sacchetti.",
              "qualification": "The work endpoint is a source-title candidate, not the Pietro person index sub-entry cand-0357. No date, surviving version, or present location is supplied.",
              "mentioned_candidate_ids": ["cand-0342", "cand-12471", "cand-2316"],
          })
    patch("st-chp2-secii-l80-89-pietro-painted-rape-of-sabines", qualifiers={
        "claim": "Shortly afterwards Pietro painted a large canvas of The Rape of the Sabines for Sacchetti.",
        "qualification": "The source gives no exact date. Plate 10a is a locating reference, not evidence of a present location or a particular surviving version.",
        "mentioned_candidate_ids": ["cand-0342", "cand-4477", "cand-2316"],
    })
    patch("st-chp2-secii-l80-89-pietro-painted-triumph-of-bacchus", object_id="cand-12472",
          qualifiers={
              "claim": "Haskell says Pietro painted a large canvas of The Triumph of Bacchus for Sacchetti.",
              "qualification": "The work endpoint is a source-title candidate, not the Pietro person index sub-entry cand-0362. No date, surviving version, or present location is supplied.",
              "mentioned_candidate_ids": ["cand-0342", "cand-12472", "cand-2316"],
          })
    patch("st-chp2-secii-l80-89-processional-style-development", qualifiers={
        "claim": "Haskell describes Pietro's movement from dark and even crude beginnings toward a rich, warm, sun-soaked style of stately processional figures.",
        "qualification": "The following claim that other artists soon adopted the figures in the Sacchetti orbit is recorded separately in st-chp2-secii-l80-89-processional-style-adopted-in-sacchetti-orbit.",
        "mentioned_candidate_ids": ["cand-0342", "cand-4479"],
    })
    patch("st-chp2-secii-l80-89-marcello-chose-gallery-subjects", qualifiers={
        "claim": "In the Castel Fusano country-house decoration, Marcello chose tales from ancient Roman history for the gallery walls and ceiling.",
        "qualification": "The local passage places this gallery within the country-house decoration. Keep it distinct from any other Sacchetti villa or gallery until S3 establishes identity.",
        "mentioned_candidate_ids": ["cand-2317", "cand-4484", "cand-4460"],
    })
    patch("st-chp2-secii-l80-89-giulio-made-cardinal", qualifiers={
        "claim": "Haskell says Giulio Sacchetti was made a cardinal in 1626 and thereafter enjoyed a successful career in the Church.",
        "qualification": "The passage supplies the year but not the appointing authority or exact date. Keep the appointment relation pending rather than infer Urban VIII as appointer.",
        "mentioned_candidate_ids": ["cand-2313", "cand-4244"],
    })
    patch("st-chp2-secii-l80-89-marcello-papal-treasurer", qualifiers={
        "claim": "Haskell says Marcello became papal treasurer.",
        "qualification": "The passage gives no exact date, term, or appointing authority. The role is retained as stated; no appointing person or separate office entity is invented.",
        "mentioned_candidate_ids": ["cand-2314"],
    })
    patch("st-chp2-secii-l80-89-brothers-promoted-pietro", subject="cand-12473",
          qualifiers={
              "claim": "Haskell reports, citing Passeri, that Giulio and Marcello Sacchetti—the brothers named in the preceding context—took pleasure in Pietro da Cortona's success and never tired of promoting his chances.",
              "qualification": "The source explicitly names the two brothers in the preceding line. Keep this bounded pair distinct from the broader Sacchetti family candidate cand-4452. Passeri, p. 378, is cited but was not independently consulted.",
              "mentioned_candidate_ids": ["cand-12473", "cand-0342"],
          })
    patch("st-chp2-secii-l80-89-chronicler-quote-on-sacchetti-protection", object_id="cand-4565",
          qualifiers={
              "claim": "Haskell describes the Sacchettis' influence in matters of taste as decisive and quotes an unidentified chronicler: their ‘shadow was enough to protect any artist.’ Note 3 cites Vita di G. M. Bottalla in Soprani, volume I, p. 303.",
              "speaker": "An unidentified chronicler as quoted by Haskell; Soprani is the cited publication author, not a confirmed speaker.",
              "qualification": "The printed footnote identifies a cited passage in Soprani, volume I, p. 303; that page has not been independently consulted. Do not identify Soprani as the quoted chronicler.",
              "supporting_source_refs": [{
                  "segment_id": "chp-2:02_CHP-2_sec_ii:l147-193",
                  "source_line_start": 178,
                  "source_line_end": 178,
                  "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                  "quote": "3 Vita Ji C. Ai. Battalia—Soprani, I, p. 303.",
              }],
              "mentioned_candidate_ids": ["cand-4452", "cand-4565"],
          })
    patch("st-chp2-secii-l80-89-marcello-pope-friend-confidant", qualifiers={
        "claim": "Haskell says Marcello became the Pope's closest friend and confidant of his most intimate secrets until ill-health compelled him to retire to Naples.",
        "qualification": "The source supplies the illness-related end boundary but no start date or examples of confidences. Preserve this as Haskell's characterization.",
        "mentioned_candidate_ids": ["cand-2314", "cand-0209", "cand-3534"],
    })
    patch("st-chp2-secii-l80-89-sacchetti-influence-on-taste", qualifiers={
        "claim": "Haskell describes the Sacchettis' influence in matters of taste as decisive.",
        "qualification": "The source does not define the family's full membership or specify a single target of influence. Keep candidate identity and any formal relation open.",
        "open_endpoint_reason": "The source makes a broad statement about influence in matters of taste without naming a specific target; no formal relation endpoint is supplied.",
        "mentioned_candidate_ids": ["cand-4452"],
    })
    patch("st-chp2-secii-l80-89-pietro-grand-manner-in-bibiana-frescoes", qualifiers={
        "claim": "Haskell says Pietro brought the ‘warmth and.breadth’ of his ‘grand manner’ to the S. Bibiana frescoes; the scan shows a dot-like mark after ‘and’, so the wording is retained without silently normalizing the punctuation.",
        "qualification": "Printed p. 39 ends this sentence at ‘grand manner’; it continues on p. 40 with the attention to classical detail. Preserve the visible punctuation anomaly rather than assert a clean ‘and breadth’ reading.",
        "linked_statement_ids": ["st-chp2-secii-l91-104-pietro-fresco-classical-detail-continuation"],
        "mentioned_candidate_ids": ["cand-4448", "cand-4489"],
    })
    patch("st-chp2-secii-l91-104-pietro-fresco-classical-detail-continuation", qualifiers={
        "claim": "The sentence continues by saying that the frescoes combined Pietro's ‘grand manner’ with attention to classical detail, which delighted unnamed connoisseurs.",
        "qualification": "This completes st-chp2-secii-l80-89-pietro-grand-manner-in-bibiana-frescoes. The connoisseurs are an unnamed human audience; their candidate type and identity remain open.",
        "linked_statement_ids": ["st-chp2-secii-l80-89-pietro-grand-manner-in-bibiana-frescoes"],
        "mentioned_candidate_ids": ["cand-4448", "cand-11886"],
    })
    patch("st-chp2-secii-l91-104-pietro-success-assured", qualifiers={
        "claim": "Haskell says Pietro's success was assured and adds that a triumphant career lay ahead.",
        "qualification": "This is Haskell's forecast, not an independently verified career outcome. The adjacent claim that Pietro joined Bernini as the Pope's special artist remains separately recorded.",
        "source_line_end": 94,
        "linked_statement_ids": ["st-chp2-secii-l91-104-pietro-joins-bernini-as-pope-special-artist"],
        "relation_candidate": False,
        "relation_candidate_note": "Authorial career forecast, not a relationship to a named endpoint.",
        "mentioned_candidate_ids": ["cand-0342"],
    })
    patch("st-chp2-secii-l91-104-urban-company-of-poets", qualifiers={
        "qualification": "The source-defined group is an unnamed human company, not a formal institution and not the separate group of friends in the next sentence. Candidate type remains undecided.",
        "mentioned_candidate_ids": ["cand-0230", "cand-11887"],
    })
    patch("st-chp2-secii-l91-104-urban-lifelong-love-of-poetry", object_id="cand-12474",
          qualifiers={
              "claim": "Haskell says Urban VIII retained throughout his life a deep love of poetry.",
              "qualification": "Poetry here is the abstract literary practice, distinct from Urban VIII's poem corpus cand-4494.",
              "mentioned_candidate_ids": ["cand-0230", "cand-12474"],
          })
    patch("st-chp2-secii-l91-104-urban-poems-nature-and-country-life", qualifiers={
        "claim": "Haskell says Urban VIII devoted many poems to celebrating nature and simple country life, particularly as lived at his villa at Castel Gandolfo.",
        "qualification": "The villa is the stated setting of the country life, not evidence that every poem was composed there. The source-defined theme remains distinct from the poem corpus.",
        "mentioned_candidate_ids": ["cand-0230", "cand-4494", "cand-12475", "cand-4492", "cand-4491"],
    })
    patch("st-chp2-secii-l91-104-urban-writes-verses-and-guides-content", qualifiers={
        "claim": "Haskell says Urban VIII himself wrote verses in Italian, Latin, and even Greek.",
        "qualification": "No individual poem or title is identified; preserve the source's emphasis on ‘even Greek’.",
        "mentioned_candidate_ids": ["cand-0230", "cand-4494"],
    })
    patch("st-chp2-secii-l91-104-urban-delegates-business-audiences-to-nephew", qualifiers={
        "claim": "On some occasions Urban VIII directed foreign diplomats to conduct business with his nephew so that he could reserve audiences for literary discussions nearer his heart.",
        "qualification": "The nephew, diplomats, and occasions are not identified. Keep the nephew placeholder and the source-defined diplomat group open; no formal relation until endpoints are resolved.",
        "mentioned_candidate_ids": ["cand-0220", "cand-12476", "cand-4497"],
    })
    patch("st-chp2-secii-l91-104-1631-volume-illustrated-by-bernini", qualifiers={
        "claim": "Haskell says Gian Lorenzo Bernini illustrated the splendid 1631 volume of Urban VIII's poems.",
        "qualification": "This is an illustration credit for the specific volume, not authorship of the poems or a general relation to all Urban VIII writings.",
        "mentioned_candidate_ids": ["cand-4498", "cand-0295"],
    })
    patch("st-chp2-secii-l91-104-1631-volume-produced-by-jesuits", qualifiers={
        "claim": "Haskell says the Jesuits produced the splendid 1631 volume of Urban VIII's poems.",
        "qualification": "The volume title is not supplied. Reuse the existing source-derived Jesuit-order candidate; its S3 identity remains open.",
        "mentioned_candidate_ids": ["cand-4498", "cand-3403"],
    })
    patch("st-chp2-secii-l91-104-urban-poetry-editions-after-accession", qualifiers={
        "claim": "Haskell says the first fine editions of Urban VIII's poems began to pour from the presses of Rome within months of his accession, culminating in a splendid 1631 volume.",
        "qualification": "‘Within months’ is relative; the source gives no initial edition dates or titles. The 1631 volume is distinguished from the broader poem corpus.",
        "mentioned_candidate_ids": ["cand-0222", "cand-12478", "cand-4490", "cand-4498", "cand-4494"],
    })
    patch("st-chp2-secii-l91-104-bernini-makes-urban-portrait-busts", qualifiers={
              "claim": "Haskell says Bernini made many bronze and marble busts of Urban VIII throughout Bernini's career.",
              "qualification": "The S0 segment surface reads ‘his.career’; the print scan shows a dot-like mark between ‘his’ and ‘career’. The claim normalizes this as ‘his career’ while retaining the transcription distinction here. Individual busts and dates are not identified. Note 5 cites Wittkower (1955), p. 184; that page was not independently consulted.",
              "mentioned_candidate_ids": ["cand-0307", "cand-4499", "cand-0232"],
          })
    patch("st-chp2-secii-l91-104-urban-busts-as-self-image", qualifiers={
        "claim": "Haskell says nothing gives a better impression of how Urban VIII saw himself than Bernini's busts.",
        "qualification": "This is Haskell's reading of the portrait group, not a statement made by Urban VIII.",
        "mentioned_candidate_ids": ["cand-4499", "cand-0232"],
    })
    patch("st-chp2-secii-l91-104-urban-busts-contrast-with-royal-portraits", qualifiers={
        "claim": "Haskell contrasts the restraint of Bernini's Urban VIII portraits with the ‘swagger’ and almost exaggerated elegance of his royal-patron portraits, both at that period and in later years; he says such display was unsuitable for the Vicar of Christ.",
        "qualification": "This is an authorial comparison of portrait representation. The royal patrons are unnamed and unbounded; keep that comparison group type and identity undecided.",
        "mentioned_candidate_ids": ["cand-4499", "cand-0232", "cand-12477"],
    })
    patch("st-chp2-secii-l91-104-urban-portrait-image-changes-over-rule", qualifiers={
        "claim": "Haskell says that after a few years of Urban VIII's rule, his early sparkle gives way in the portraits to a grave, authoritarian, and somewhat withdrawn image.",
        "qualification": "This describes how the portraits represent Urban VIII, not an independently verified change in his personality.",
        "mentioned_candidate_ids": ["cand-4499", "cand-0232"],
    })
    patch("st-chp2-secii-l91-104-urban-portrait-hieratic-dignity", qualifiers={
        "claim": "Haskell describes the portraits as images of hieratic dignity designed to portray Urban VIII as a man who need not stress his right to rule.",
        "qualification": "This is an interpretation of the images, not a claim about Urban VIII's actual political authority. The leading OCR dash before ‘portray’ is not present in the scan.",
        "mentioned_candidate_ids": ["cand-4499", "cand-0232"],
    })

    # Existing index mentions for the two titles pointed at Pietro person entries.
    mention_patch = {
        "m-chp2-secii-l80-89-0019": ("cand-12471", "Work title in Haskell's p. 39 list; distinct from the Pietro da Cortona person index sub-entry cand-0357."),
        "m-chp2-secii-l80-89-0020": ("cand-12472", "Work title in Haskell's p. 39 list; distinct from the Pietro da Cortona person index sub-entry cand-0362."),
        "m-chp2-secii-l80-89-0056": ("cand-12473", "The two brothers identified by the immediately preceding Giulio and Marcello references; keep distinct from broad family candidate cand-4452."),
        "m-chp2-secii-l91-104-0051": ("cand-0232", "S0 surface ‘his.career’ retained for exact segment alignment; p. 40 scan shows a dot-like mark, and the claim records the normalized reading ‘his career’."),
    }
    for mention_id, (candidate_id, note) in mention_patch.items():
        require(mention_id in mention_by_id, f"Missing expected mention: {mention_id}")
        mention_by_id[mention_id]["candidate_id"] = candidate_id
        mention_by_id[mention_id]["note"] = note

    new_mentions = [
        ("m-chp2-secii-l80-89-0085", p39_segment, "him", "cand-2314", "Anaphoric reference to Marcello Sacchetti in ‘re-create for him’; endpoint retained as an index candidate for S3."),
        ("m-chp2-secii-l80-89-0086", p39_segment, "his", "cand-2314", "Anaphoric reference to Marcello's dreams of the past in the aesthetic comparison; identity alignment remains for S3."),
        ("m-chp2-secii-l91-104-0092", p40_segment, "poetry", "cand-12474", "Abstract literary practice, distinct from the Urban VIII poem corpus cand-4494."),
        ("m-chp2-secii-l91-104-0093", p40_segment, "beauties of nature", "cand-12475", "Poetic subject theme in the source's account of Urban VIII's poems."),
        ("m-chp2-secii-l91-104-0094", p40_segment, "simple country life", "cand-12475", "Poetic subject theme; the nearby Castel Gandolfo villa is setting, not proof of composition."),
        ("m-chp2-secii-l91-104-0095", p40_segment, "foreign diplomats", "cand-12476", "Unnamed plural group in Urban VIII's audience arrangement; candidate type remains undecided."),
        ("m-chp2-secii-l91-104-0096", p40_segment, "royal patrons", "cand-12477", "Unnamed comparison group in Haskell's discussion of Bernini's portraits; type remains undecided."),
        ("m-chp2-secii-l91-104-0097", p40_segment, "first fine editions", "cand-12478", "Unnamed plural editions reported before the culminating 1631 volume; publication titles and dates are not supplied."),
    ]
    mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in mentions:
        mentions_by_segment[row["segment_id"]].append(dict(row))
    after_mentions = [dict(row) for row in mentions]
    for mention_id, segment_id, surface, candidate_id, note in new_mentions:
        require(mention_id not in mention_by_id, f"New mention ID already exists: {mention_id}")
        source_file = segment_by_id[segment_id]["source_file"]
        text = source_segment_text(segment_id, source_file)
        if mention_id == "m-chp2-secii-l80-89-0085":
            context_start, _ = unique_span(text, "re-create for him all the trappings")
            start = context_start + len("re-create for ")
            end = start + len(surface)
            require(text[start:end] == surface, "Anaphoric mention surface does not match source")
        elif mention_id == "m-chp2-secii-l80-89-0086":
            start, end = unique_span(text, "his dreams of the past")
            end = start + len(surface)
        else:
            start, end = unique_span(text, surface)
        for old in mentions_by_segment[segment_id]:
            a, b = int(old["start_char"]), int(old["end_char"])
            require(end <= a or start >= b,
                    f"New mention {mention_id} overlaps {old['mention_id']}")
        row = {field: "" for field in mention_fields}
        row.update({"mention_id": mention_id, "segment_id": segment_id,
                    "candidate_id": candidate_id, "surface_form": surface,
                    "start_char": str(start), "end_char": str(end), "note": note})
        after_mentions.append(row)
        mentions_by_segment[segment_id].append(row)

    # The two unnamed human groups were previously misfiled as terms. Leave their
    # taxonomy open rather than converting a category of people into a concept.
    after_by_id = {row["statement_id"]: row for row in after_statements}
    for row in after_statements:
        require(row["statement_id"] in after_by_id, "Statement ID set changed")
    require(set(PASS_IDS) == pending_ids - set(PENDING_NOTES),
            "Stage pass/pending decision sets no longer partition the open findings")

    # Build the current roster result and refresh the two source-segment fingerprints.
    changed_statement_ids = {sid for sid in statement_by_id
                             if canonical_hash(statement_by_id[sid]) != canonical_hash(after_by_id[sid])}
    after_roster = [dict(row) for row in roster]
    after_roster_by_id = {row["statement_id"]: row for row in after_roster}
    selected_ids = {row["statement_id"] for row in selected}
    pass_review_ids = pending_ids - set(PENDING_NOTES)
    for row in selected:
        target = after_roster_by_id[row["statement_id"]]
        prior_evidence = row["review_evidence_ref"]
        target["review_batch_id"] = BATCH_ID
        target["review_evidence_ref"] = EVIDENCE_REF
        if row["statement_id"] in pass_review_ids:
            target["current_review_status"] = "reviewed_current_pass"
            target["review_outcome"] = "current_semantic_pass_after_printed_page_review"
            detail = "按p.39-40扫描修订claim、端点映射或mention，并复核原文跨度。"
        elif row["statement_id"] in PENDING_NOTES:
            target["current_review_status"] = "reviewed_current_pending"
            target["review_outcome"] = "current_open_finding_retained_after_printed_page_review"
            detail = PENDING_NOTES[row["statement_id"]]
        else:
            target["current_review_status"] = "reviewed_current_pass"
            target["review_outcome"] = "current_pass_reused_after_current_fingerprint_and_printed_page_check"
            detail = "复用已完成审读并核对当前statement、来源资产、segment及mention指纹。"
        target["follow_up_note"] = (
            f"B433：{detail} 前次依据：{prior_evidence}。\n"
            + target.get("follow_up_note", "")
        ).strip()

    # A source segment fingerprint is shared by every statement in that segment.
    segment_mentions: dict[str, list[dict[str, str]]] = defaultdict(list)
    for mention in after_mentions:
        segment_mentions[mention["segment_id"]].append(mention)
    for row in after_roster:
        if row["segment_id"] in mention_update_segments:
            ordered = sorted(segment_mentions[row["segment_id"]], key=lambda m: m["mention_id"])
            row["current_segment_mention_count"] = str(len(ordered))
            row["current_segment_mentions_sha256"] = canonical_hash(ordered)
        if row["statement_id"] in changed_statement_ids:
            target_statement = after_by_id[row["statement_id"]]
            target = after_roster_by_id[row["statement_id"]]
            target["current_statement_sha256"] = canonical_hash(target_statement)
            target["source_line_start"] = str(target_statement["qualifiers"].get(
                "source_line_start", target["source_line_start"]))
            target["source_line_end"] = str(target_statement["qualifiers"].get(
                "source_line_end", target["source_line_end"]))
            if int(target["history_9622_event_count"] or "0") > 0:
                target["history_9622_current_statement_match"] = (
                    "exact" if target["history_9622_latest_statement_sha256"] ==
                    target["current_statement_sha256"] else "changed"
                )
                target["prior_review_match"] = (
                    "exact_object_and_source_segment"
                    if target["history_9622_current_statement_match"] == "exact"
                    and target["history_9622_source_match"] == "true"
                    else "historical_object_or_source_differs"
                )
    require(changed_statement_ids <= selected_ids,
            f"Unexpected out-of-batch statement modifications: {sorted(changed_statement_ids-selected_ids)}")

    # Preserve every untouched JSONL record byte-for-byte.
    rewritten_statement_lines = []
    changed_left = set(changed_statement_ids)
    for line in statement_lines:
        if not line.strip():
            rewritten_statement_lines.append(line)
            continue
        old = json.loads(line)
        sid = old["statement_id"]
        if sid in changed_left:
            rewritten_statement_lines.append(json.dumps(after_by_id[sid], ensure_ascii=False,
                                                         separators=(",", ":")) + statement_eol)
            changed_left.remove(sid)
        else:
            rewritten_statement_lines.append(line)
    require(not changed_left, f"Changed JSONL IDs missing from source: {sorted(changed_left)}")
    statement_output = ((b"\xef\xbb\xbf" if statement_raw.startswith(b"\xef\xbb\xbf") else b"")
                        + "".join(rewritten_statement_lines).encode("utf-8"))

    mentions_output = write_csv(after_mentions, mention_fields, mention_eol, mention_bom)
    candidates_output = write_csv(after_candidates, candidate_fields, candidate_eol, candidate_bom)
    alignment_output = write_csv(after_alignments, alignment_fields, alignment_eol, alignment_bom)
    roster_output = write_csv(after_roster, roster_fields, roster_eol, roster_bom)

    status_counts = Counter(row["current_review_status"] for row in after_roster)
    history_counts = Counter(row["history_9622_current_statement_match"]
                             for row in after_roster if row["history_9622_event_count"])
    source_matches = Counter(row["history_9622_source_match"]
                             for row in after_roster if row["history_9622_event_count"])
    require(status_counts["reviewed_current_pass"] == 8709 and
            status_counts["reviewed_current_pending"] == 6803,
            f"Unexpected stage status totals: {status_counts}")
    require(len(after_mentions) == len(mentions) + 8,
            f"Unexpected mention count change: {len(mentions)} -> {len(after_mentions)}")
    require(len(after_candidates) == len(candidates) + 8 and
            len(after_alignments) == len(alignments) + 8,
            "Candidate/alignment addition count mismatch")
    require(relation_raw == RELATIONS_PATH.read_bytes(), "relations.csv changed during planning")
    related_statement_rows = [row["relation_id"] for row in relations
                              if any(sid in row.get("source_span", "") for sid in changed_statement_ids)]
    require(not related_statement_rows,
            f"Changed statements have adjudicated relation rows to reassess: {related_statement_rows}")
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 ledger changed during planning")

    print(f"batch={BATCH_ID} rows=100 reused_PASS=66 new_PASS=32 retained_pending=2")
    print(f"modified_statements={len(changed_statement_ids)} new_mentions=8 new_candidates=8 undecided_alignments=8")
    print(f"global_current_PASS={status_counts['reviewed_current_pass']} pending={status_counts['reviewed_current_pending']}")
    print(f"H9622_current_hash_matches={dict(history_counts)} source_matches={dict(source_matches)}")
    print("new_candidate_ids=" + ",".join(spec["candidate_id"] for spec in NEW_CANDIDATES))
    print("affected_formal_relation_rows=0; relations.csv remains unchanged")
    if not args.apply:
        print("dry-run only; rerun with --apply after reviewing this plan")
        return

    outputs = [
        (STATEMENTS_PATH, statement_output),
        (MENTIONS_PATH, mentions_output),
        (CANDIDATES_PATH, candidates_output),
        (ALIGNMENT_PATH, alignment_output),
        (ROSTER_PATH, roster_output),
    ]
    for path, data in outputs:
        atomic_write(path, data)
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "Immutable H9622 ledger changed during apply")
    require(RELATIONS_PATH.read_bytes() == relation_raw,
            "relations.csv changed during apply")
    print("applied B433; H9622 ledger and relations.csv unchanged")


if __name__ == "__main__":
    main()
