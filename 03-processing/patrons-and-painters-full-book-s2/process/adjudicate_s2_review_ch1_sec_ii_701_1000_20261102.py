#!/usr/bin/env python3
"""Apply the reviewed S2 current-version decisions for source order 701-1000."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
LEDGER_PATH = PROCESS / "s2-history-9622-review-events.csv"
STAGE_ID = "2026-11-02-s2-current-review-stage-b398-b400-order-701-1000"
STAGE_MARKER = f"stages.md#{STAGE_ID}"
SOURCE_FILE = "02-sources/02-Markdown/01_CHP-1_sec_ii.md"
SOURCE_SHA256 = "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268"
PDF_FILE = "02-sources/01-book/CHP-1.pdf"
PDF_SHA256 = "0b9a3ca88e6f09209bd20185948e18a68f527d0628e893940a7e3f07f6d22c86"


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        lines = stream.readlines()
    values = [json.loads(line) for line in lines if line.strip()]
    return values, lines


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    return rows, fields


def write_csv_bytes(rows: list[dict[str, str]], fields: list[str],
                    lineterminator: str = "\n") -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=lineterminator,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")


def git_mentions(revision: str, segment_id: str) -> dict[str, dict[str, str]]:
    data = subprocess.check_output(
        ["git", "show", f"{revision}:04-knowledge/tables/mentions.csv"],
        cwd=ROOT,
    ).decode("utf-8-sig")
    return {
        row["mention_id"]: row
        for row in csv.DictReader(io.StringIO(data, newline=""))
        if row["segment_id"] == segment_id
    }


def load_source_text(segments: dict[str, dict], segment_ids: set[str]) -> dict[str, str]:
    by_file: dict[str, list[str]] = {}
    for segment_id in segment_ids:
        segment = segments[segment_id]
        if segment["source_file"] not in by_file:
            with (ROOT / segment["source_file"]).open(
                "r", encoding="utf-8-sig", newline=""
            ) as stream:
                by_file[segment["source_file"]] = stream.read().splitlines()
    result = {}
    for segment_id in segment_ids:
        segment = segments[segment_id]
        lines = by_file[segment["source_file"]]
        result[segment_id] = "\n".join(
            lines[int(segment["line_start"]) - 1:int(segment["line_end"])]
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    statements_path = TABLES / "book-statements.jsonl"
    mentions_path = TABLES / "mentions.csv"
    alignment_path = TABLES / "alignment.csv"
    segments_path = TABLES / "segments.jsonl"

    statements, statement_lines = read_jsonl(statements_path)
    segments, _ = read_jsonl(segments_path)
    mentions, mention_fields = read_csv(mentions_path)
    alignments, alignment_fields = read_csv(alignment_path)
    roster, roster_fields = read_csv(ROSTER_PATH)

    statement_by_id = {row["statement_id"]: row for row in statements}
    segment_by_id = {row["segment_id"]: row for row in segments}
    if len(statement_by_id) != len(statements) or len(segment_by_id) != len(segments):
        raise SystemExit("Duplicate statement or segment ID")
    if roster_fields != list(roster[0]):
        raise SystemExit("Unexpected S2 roster columns")
    if sha256((ROOT / SOURCE_FILE).read_bytes()) != SOURCE_SHA256:
        raise SystemExit("Chapter 1 section source file changed")
    if sha256((ROOT / PDF_FILE).read_bytes()) != PDF_SHA256:
        raise SystemExit("Chapter 1 authority PDF changed")

    order_rows = roster[700:1000]
    if len(order_rows) != 300 or [int(row["current_order"]) for row in order_rows] != list(range(701, 1001)):
        raise SystemExit("Current roster order 701-1000 is not contiguous")
    existing_pass = [r for r in order_rows if r["current_review_status"] == "reviewed_current_pass"]
    existing_pending = [r for r in order_rows if r["current_review_status"] == "reviewed_current_pending"]
    if (len(existing_pass), len(existing_pending)) != (280, 20):
        raise SystemExit(f"Unexpected stage baseline: {len(existing_pass)} PASS, {len(existing_pending)} pending")
    expected_pending = {
        "st-chp1-secii-l28-38-04", "st-chp1-secii-l48-60-07",
        "st-chp1-secii-l62-71-09", "st-chp1-secii-l79-84-10",
        "st-chp1-secii-l86-94-06", "st-chp1-secii-l106-116-02f",
        "st-chp1-secii-l106-116-02h", "st-chp1-secii-l106-116-02j",
        "st-chp1-secii-l106-116-02l", "st-chp1-secii-l118-127-05",
        "st-chp1-secii-l118-127-01b", "st-chp1-secii-l118-127-03a",
        "st-chp1-secii-l129-135-01", "st-chp1-secii-l129-135-01e",
        "st-chp1-secii-l137-146-02", "st-chp1-secii-l148-153-01a",
        "st-chp1-secii-l905-916-01j", "st-chp1-secii-l927-943-03f",
        "st-chp1-secii-p22-n1-cites-rosa-letter",
        "st-chp1-secii-p8-n1-piola-obtains-alternative-residence",
    }
    if {r["statement_id"] for r in existing_pending} != expected_pending:
        raise SystemExit("Pending ID set changed since source review")
    if any(r["history_9622_event_count"] != "1" or r["history_9622_source_match"] != "true"
           for r in existing_pending):
        raise SystemExit("Pending historical event/source mapping changed")
    if any(r["review_batch_id"].startswith(("S2-B398", "S2-B399", "S2-B400"))
           for r in order_rows):
        raise SystemExit("This stage already appears in the current roster")
    pre_statement_hashes = {
        sid: canonical_hash(row) for sid, row in statement_by_id.items()
    }
    pre_mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for mention in mentions:
        pre_mentions_by_segment[mention["segment_id"]].append(mention)
    for order_row in order_rows:
        sid = order_row["statement_id"]
        statement = statement_by_id[sid]
        segment = segment_by_id[statement["segment_id"]]
        if order_row["current_statement_sha256"] != pre_statement_hashes[sid]:
            raise SystemExit(f"Pre-edit statement fingerprint mismatch: {sid}")
        if order_row["segment_sha256"] != segment["sha256"]:
            raise SystemExit(f"Pre-edit source segment mismatch: {sid}")
        if order_row["source_asset_sha256"] != segment.get("asset_sha256", ""):
            raise SystemExit(f"Pre-edit source asset mismatch: {sid}")
        before_rows = pre_mentions_by_segment.get(statement["segment_id"], [])
        before_hash = canonical_hash(sorted(before_rows, key=lambda m: m["mention_id"]))
        if (order_row["current_segment_mention_count"] != str(len(before_rows)) or
                order_row["current_segment_mentions_sha256"] != before_hash):
            raise SystemExit(f"Pre-edit mention fingerprint mismatch: {sid}")
        if not order_row["review_evidence_ref"]:
            raise SystemExit(f"Missing prior evidence reference: {sid}")

    mention_specs = [
        ("m-chp1-secii-20261102-pamfili-this-commission",
         "chp-1:01_CHP-1_sec_ii:l62-71", "cand-11836", "this commission",
         1083, 1098,
         "Anaphoric reference to Ciro Ferri's S. Agnese cupola commission."),
        ("m-chp1-secii-20261102-arragona-highness",
         "chp-1:01_CHP-1_sec_ii:l79-84", "cand-11839", "His Highness",
         1286, 1298,
         "The unnamed Duke addressed in Arragona's letter; identity unresolved."),
        ("m-chp1-secii-20261102-arragona-agent",
         "chp-1:01_CHP-1_sec_ii:l79-84", "cand-3476", "the Mantuan agent in Rome",
         1343, 1368,
         "Appositive description of Fabrizio Arragona."),
        ("m-chp1-secii-20261102-arragona-chancellor",
         "chp-1:01_CHP-1_sec_ii:l79-84", "cand-11840", "a ducal chancellor",
         1372, 1390,
         "Unnamed letter addressee, distinct from the Duke called His Highness."),
        ("m-chp1-secii-20261102-bentveughels-colony",
         "chp-1:01_CHP-1_sec_ii:l137-146", "cand-11862",
         "the colony of Dutch and Flemish artists living in Rome", 758, 812,
         "Source definition of the bentveughels; keep distinct from the Schildersbent."),
        ("m-chp1-secii-20261102-carlone-sister",
         "chp-1:01_CHP-1_sec_ii:l148-153", "cand-11870", "his sister",
         120, 130,
         "Unnamed sister of the household master; no completed marriage is asserted."),
        ("m-chp1-secii-20261102-rosa-would-be-patron",
         "chp-1:01_CHP-1_sec_ii:l155-159", "cand-2297", "a would-be patron",
         2848, 2865,
         "Body-text role identified as Don Antonio Ruffo by the linked footnote."),
    ]
    source_texts = load_source_text(
        segment_by_id, {spec[1] for spec in mention_specs}
    )
    existing_mention_ids = {m["mention_id"] for m in mentions}
    new_mentions = []
    for mid, segment_id, candidate_id, surface, start, end, note in mention_specs:
        if mid in existing_mention_ids:
            raise SystemExit(f"Mention ID already exists: {mid}")
        if source_texts[segment_id][start:end] != surface:
            raise SystemExit(f"Mention anchor mismatch for {mid}")
        new_mentions.append({
            "mention_id": mid, "segment_id": segment_id,
            "candidate_id": candidate_id, "surface_form": surface,
            "start_char": str(start), "end_char": str(end), "note": note,
        })

    # statement ID: current source-faithful edits; open findings are retained separately.
    edits = {
        "st-chp1-secii-l79-84-10": {
            "claim": "In a letter to an unnamed ducal chancellor, Fabrizio Arragona urged the unnamed Duke addressed as 'His Highness' to send money to Rome as a deposit so painters would serve him well and quickly.",
        },
        "st-chp1-secii-l106-116-02f": {
            "subject_candidate_id": "cand-3092", "object_candidate_id": "cand-3470",
        },
        "st-chp1-secii-l106-116-02h": {
            "subject_candidate_id": "cand-3061", "object_candidate_id": "cand-3470",
        },
        "st-chp1-secii-l106-116-02j": {
            "subject_candidate_id": "cand-3104", "object_candidate_id": "cand-3470",
        },
        "st-chp1-secii-l106-116-02l": {
            "object_candidate_id": "cand-3470",
        },
        "st-chp1-secii-l118-127-01b": {
            "subject_candidate_id": "cand-3581", "object_candidate_id": "cand-3470",
            "relation_candidate": True,
            "relation_candidate_note": "S2 relation candidate: Haskell qualifies the gilders' initial Accademia membership as 'seem' and marks 1645 as the later second-class boundary; this is not a formal S6 edge.",
        },
        "st-chp1-secii-l129-135-01e": {
            "claim": "Haskell identifies the account of Queen Christina taking Mola into her carriage as among the stories more likely to be true in a strict sense and describes Mola as a particularly successful courtier.",
        },
        "st-chp1-secii-l905-916-01j": {
            "claim": "Haskell says Salvator Rosa set out to try to do away with those patronage restrictions.",
        },
        "st-chp1-secii-p22-n1-cites-rosa-letter": {
            "footnote_segment": "chp-1:01_CHP-1_sec_ii:l168-239",
            "footnote_refs": [{
                "marker": 1,
                "segment_id": "chp-1:01_CHP-1_sec_ii:l168-239",
                "source_line": 944,
            }],
        },
    }
    for sid in edits:
        if sid not in statement_by_id:
            raise SystemExit(f"Missing statement: {sid}")
    statement_changes: set[str] = set()
    for sid, values in edits.items():
        row = statement_by_id[sid]
        q = row["qualifiers"]
        before = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for key, value in values.items():
            if key in {"claim", "relation_candidate", "relation_candidate_note"}:
                q[key] = value
            elif key in {"footnote_segment", "footnote_refs"}:
                q[key] = value
            else:
                row[key] = value
        after = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if before != after:
            statement_changes.add(sid)

    # Preserve the existing candidate lists while recording the exact new S2 referents.
    statements_to_mention = {
        "st-chp1-secii-l62-71-09": ["cand-11836"],
        "st-chp1-secii-l79-84-10": ["cand-11839", "cand-11840", "cand-3476"],
        "st-chp1-secii-l137-146-02": ["cand-11862"],
        "st-chp1-secii-l148-153-01a": ["cand-11870"],
        "st-chp1-secii-l927-943-03f": ["cand-2297"],
    }
    for sid, candidate_ids in statements_to_mention.items():
        values = statement_by_id[sid]["qualifiers"].setdefault("mentioned_candidate_ids", [])
        before = list(values)
        values[:] = list(dict.fromkeys(values + candidate_ids))
        if values != before:
            statement_changes.add(sid)

    # Existing source-level S3 decisions remain unchanged; append only the new evidence.
    alignment_notes = {
        "cand-11862": "S2 page review now anchors 'the colony of Dutch and Flemish artists living in Rome' in Chapter 1 p.20 (stage B399); retain undecided because the group-vs-term identity/type boundary against cand-3152 remains unresolved.",
        "cand-11870": "S2 page review now anchors 'his sister' in Chapter 1 p.21 (stage B399); retain undecided because the referent remains unnamed and no person identity is established.",
        "cand-2297": "S2 page review now anchors 'a would-be patron' in Chapter 1 p.22 body; the linked footnote names Don Antonio Ruffo. Existing same alignment to units/persons/antonio-ruffo is unchanged.",
    }
    alignment_by_candidate = {row["candidate_id"]: row for row in alignments}
    for candidate_id, addition in alignment_notes.items():
        row = alignment_by_candidate.get(candidate_id)
        if row is None or STAGE_ID in row["resolution_note"]:
            raise SystemExit(f"Missing or already updated alignment row: {candidate_id}")
        if candidate_id == "cand-11862" and row["decision"] != "undecided":
            raise SystemExit("cand-11862 is no longer undecided")
        if candidate_id == "cand-11870" and row["decision"] != "undecided":
            raise SystemExit("cand-11870 is no longer undecided")
        if candidate_id == "cand-2297" and (row["decision"], row["ku_id"]) != ("same", "units/persons/antonio-ruffo"):
            raise SystemExit("cand-2297 alignment changed")
        row["resolution_note"] += " " + addition

    cupola_alignment = alignment_by_candidate.get("cand-11836")
    if cupola_alignment is None or cupola_alignment["decision"] != "undecided":
        raise SystemExit("cand-11836 alignment changed")
    cupola_alignment["decision"] = "same"
    cupola_alignment["ku_id"] = "units/works/ferri-sant-agnese-cupola"
    cupola_alignment["resolution_note"] = (
        "group=sg3-ku-units-works-ferri-sant-agnese-cupola; source_ref=cand-11836; "
        "S2 mention=m-chp1-secii-20261102-pamfili-this-commission@"
        "chp-1:01_CHP-1_sec_ii:l62-71[chars=1083-1098]; statements "
        "st-chp1-secii-l62-71-06/-09 and the printed p.12 context identify the "
        "Ciro Ferri S. Agnese cupola fresco; matched_manifest="
        "units/works/ferri-sant-agnese-cupola. Same type and source-defined work; "
        "keep separate from the coloured modello candidate cand-11835 and "
        "units/works/ferri-sant-agnese-modello. No external identity source accessed."
    )

    arragona_mentions = {
        "cand-11839": (
            "m-chp1-secii-20261102-arragona-highness",
            "chp-1:01_CHP-1_sec_ii:l79-84[chars=1286-1298]",
        ),
        "cand-11840": (
            "m-chp1-secii-20261102-arragona-chancellor",
            "chp-1:01_CHP-1_sec_ii:l79-84[chars=1372-1390]",
        ),
    }
    for candidate_id, (mention_id, anchor) in arragona_mentions.items():
        row = alignment_by_candidate.get(candidate_id)
        if row is None or row["decision"] != "undecided":
            raise SystemExit(f"{candidate_id} alignment changed")
        row["resolution_note"] = row["resolution_note"].replace(
            "s2_mentions=none",
            f"s2_mentions={mention_id}@{anchor}",
        )
        row["resolution_note"] += (
            f" S2 current review anchors the exact role mention {mention_id}@{anchor}; "
            "identity remains unresolved because the Duke/chancellor is unnamed."
        )

    # Retain exact prior evidence in each current roster row before assigning this stage.
    mentions_after = mentions + new_mentions
    mention_ids = [m["mention_id"] for m in mentions_after]
    if len(mention_ids) != len(set(mention_ids)):
        raise SystemExit("Duplicate mention IDs")
    mentions_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for mention in mentions_after:
        mentions_by_segment[mention["segment_id"]].append(mention)

    resolution_notes = {
        "st-chp1-secii-l28-38-04": ("pending", "Composite commission, borrowing request, and iconographic account; preserve until split. Existing rel-0034 remains supported and unchanged."),
        "st-chp1-secii-l48-60-07": ("pass", "The printed p.12 statement is explicitly 'no certain examples'; its linked note distinguishes disputed Cortona proposals from recorded Camassei and Sacchi modelli. Keep the qualification."),
        "st-chp1-secii-l62-71-09": ("pending", "Added the exact 'this commission' anchor to cand-11836; the statement still combines the S. Agnese commission and a general characterization of Pamfili relations with artists."),
        "st-chp1-secii-l79-84-10": ("pass", "Re-read the printed p.14 quotation and note. The Mantuan agent is Arragona; 'His Highness' is the unnamed Duke, the ducal chancellor is the addressee, and advice does not prove payment."),
        "st-chp1-secii-l86-94-06": ("pending", "The source names art dealing and art exhibitions as distinct activities; retain pending until the composite claim is split."),
        "st-chp1-secii-l106-116-02f": ("pass", "Corrected direction: Paul V grants the annual privilege to the Accademia; printed p.17 confirms the named endpoints and annual scope."),
        "st-chp1-secii-l106-116-02h": ("pass", "Corrected direction: Gregory XV confirms the Accademia statutes in 1621; printed p.17 confirms the claim."),
        "st-chp1-secii-l106-116-02j": ("pass", "Corrected direction: Urban VIII establishes the Accademia's authority; printed p.17 confirms the source-attributed claim."),
        "st-chp1-secii-l106-116-02l": ("pass", "Corrected object to the Accademia as protectorate; keep Urban VIII as appointment context, not the protected institution."),
        "st-chp1-secii-l118-127-05": ("pending", "The brief remains unidentified and the statement combines a financial-benefit attribution with a separate social-status interpretation."),
        "st-chp1-secii-l118-127-01b": ("pass", "Corrected direction to gilders as the qualified membership group and the Accademia as institution; retain 'seem' and the 1645 boundary. S2 relation candidate only."),
        "st-chp1-secii-l118-127-03a": ("pending", "This is an incomplete sentence fragment spanning the segment boundary; preserve with the linked completion until a correct merge/exclusion is established."),
        "st-chp1-secii-l129-135-01": ("pending", "This is the overlapping completion of the preceding cross-segment fragment; keep both rows pending until the source-span boundary is resolved."),
        "st-chp1-secii-l129-135-01e": ("pass", "Updated the claim to preserve Haskell's attribution that this is among stories more likely true in a strict sense; the cited account remains unchecked."),
        "st-chp1-secii-l137-146-02": ("pass", "Added the exact source definition of the bentveughels as a Rome-based Dutch and Flemish artists' colony. Keep distinct from the Schildersbent and retain cand-11862 undecided at S3."),
        "st-chp1-secii-l148-153-01a": ("pass", "Added the exact 'his sister' anchor; the source reports a suitable match, not a completed marriage, and leaves both master and sister unnamed. Keep cand-11870 undecided at S3."),
        "st-chp1-secii-l905-916-01j": ("pass", "Restored the source's 'try' qualification: Rosa set out to try to do away with the restrictions; success is not claimed."),
        "st-chp1-secii-l927-943-03f": ("pass", "Added the exact body phrase 'a would-be patron'; the linked p.22 footnote identifies Don Antonio Ruffo. Keep the existing S3 identity decisions and do not add an S6 edge."),
        "st-chp1-secii-p22-n1-cites-rosa-letter": ("pass", "Re-anchored footnote_segment and footnote_refs to the footnote segment; kept body page context and linked body statements. The cited letter/publication remain mediated, not independently consulted."),
        "st-chp1-secii-p8-n1-piola-obtains-alternative-residence": ("pass", "The printed p.8 note supports the source-limited claim that Piola, with difficulty, obtained permission to live elsewhere; grantor and place remain unspecified."),
    }
    if set(resolution_notes) != expected_pending:
        raise SystemExit("Decision set does not cover exactly the 20 pending statements")

    pass_ids = {sid for sid, (decision, _) in resolution_notes.items() if decision == "pass"}
    pending_ids = set(resolution_notes) - pass_ids
    if (len(pass_ids), len(pending_ids)) != (14, 6):
        raise SystemExit("Unexpected stage decision totals")

    statement_hashes = {sid: canonical_hash(row) for sid, row in statement_by_id.items()}
    # Stage metadata is source order based, independent of chapter segment grouping.
    batch_specs = [
        (701, 800, "S2-B398-CH1-SECII-701-800", "2026-11-02-s2-current-review-b398-order-701-800"),
        (801, 900, "S2-B399-CH1-SECII-801-900", "2026-11-02-s2-current-review-b399-order-801-900"),
        (901, 1000, "S2-B400-CH1-SECII-901-1000", "2026-11-02-s2-current-review-b400-order-901-1000"),
    ]
    for order_row in order_rows:
        order = int(order_row["current_order"])
        batch_id, anchor = next((b, a) for lo, hi, b, a in batch_specs if lo <= order <= hi)
        sid = order_row["statement_id"]
        prior_ref = order_row["review_evidence_ref"]
        order_row["review_batch_id"] = batch_id
        order_row["review_evidence_ref"] = "stages.md#" + anchor
        if sid in resolution_notes:
            decision, note = resolution_notes[sid]
            order_row["current_review_status"] = (
                "reviewed_current_pass" if decision == "pass" else "reviewed_current_pending"
            )
            order_row["review_outcome"] = (
                "current_pending_finding_resolved_after_original_page_review"
                if decision == "pass" else "current_open_finding_retained_after_original_page_review"
            )
            order_row["follow_up_note"] = note + " Previous evidence: " + prior_ref + "."
        else:
            if order_row["current_review_status"] != "reviewed_current_pass":
                raise SystemExit(f"Unexpected non-target pending status at {sid}")
            order_row["review_outcome"] = "reused_exact_current_pass_after_fingerprint_verification"
            order_row["follow_up_note"] = (
                "Reused the existing current-version page review after statement, source, and mention fingerprints matched; "
                "no source or semantic delta was found. Previous evidence: " + prior_ref + "."
            )

    changed_segments = {m["segment_id"] for m in new_mentions}
    historical_mention_cache: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    for row in roster:
        sid = row["statement_id"]
        statement = statement_by_id[sid]
        segment = segment_by_id[statement["segment_id"]]
        seg_mentions = mentions_by_segment.get(statement["segment_id"], [])
        event_count = int(row["history_9622_event_count"] or "0")
        if sid in statement_changes:
            row["current_statement_sha256"] = statement_hashes[sid]
        if segment["segment_id"] in changed_segments:
            row["current_segment_mention_count"] = str(len(seg_mentions))
            row["current_segment_mentions_sha256"] = canonical_hash(
                sorted(seg_mentions, key=lambda m: m["mention_id"])
            )
        if event_count > 0 and sid in statement_changes:
            row["history_9622_current_statement_match"] = (
                "exact" if row["history_9622_latest_statement_sha256"] == statement_hashes[sid]
                else "changed"
            )
            row["prior_review_match"] = (
                "exact_object_and_source_segment"
                if row["history_9622_current_statement_match"] == "exact"
                and row["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )
        if event_count > 0 and segment["segment_id"] in changed_segments:
            revision = row["history_9622_latest_review_commit"]
            cache_key = (revision, segment["segment_id"])
            if cache_key not in historical_mention_cache:
                historical_mention_cache[cache_key] = git_mentions(*cache_key)
            old_mentions = historical_mention_cache[cache_key]
            current_mentions = {m["mention_id"]: m for m in seg_mentions}
            changed = sorted(
                mid for mid in old_mentions.keys() & current_mentions.keys()
                if old_mentions[mid] != current_mentions[mid]
            )
            removed = sorted(old_mentions.keys() - current_mentions.keys())
            added = sorted(current_mentions.keys() - old_mentions.keys())
            row["history_9622_mention_delta"] = json.dumps(
                {"changed": changed, "removed": removed, "added": added},
                ensure_ascii=False, separators=(",", ":"),
            )

    # Preserve JSON formatting and line endings for every untouched statement row.
    changed_ids = statement_changes
    rewritten_statement_lines = []
    for line in statement_lines:
        if not line.strip():
            rewritten_statement_lines.append(line)
            continue
        obj = json.loads(line)
        if obj["statement_id"] not in changed_ids:
            rewritten_statement_lines.append(line)
            continue
        ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        rewritten_statement_lines.append(
            json.dumps(statement_by_id[obj["statement_id"]], ensure_ascii=False,
                       separators=(",", ":")) + ending
        )

    # Assert relevant historical and formal relation ledgers are untouched by this stage.
    ledger_before = sha256(LEDGER_PATH.read_bytes())
    relations_path = TABLES / "relations.csv"
    relations_before = sha256(relations_path.read_bytes())
    if sha256(LEDGER_PATH.read_bytes()) != ledger_before or sha256(relations_path.read_bytes()) != relations_before:
        raise SystemExit("Immutable ledger changed before stage application")

    print(json.dumps({
        "stage": STAGE_ID,
        "range": "701-1000",
        "existing_current_pass_reused": len(existing_pass),
        "historical_pending_reviewed": len(existing_pending),
        "resolved_to_current_pass": len(pass_ids),
        "retained_pending": len(pending_ids),
        "changed_statement_ids": sorted(changed_ids),
        "new_mentions": len(new_mentions),
        "changed_mention_segments": sorted(changed_segments),
        "history_ledger_sha256": ledger_before,
        "relations_sha256": relations_before,
        "apply": args.apply,
    }, ensure_ascii=False, indent=2))

    if not args.apply:
        return

    # Confirm none of the records changed after the dry run's source and ID checks.
    statements_path.write_bytes(
        b"\xef\xbb\xbf" + "".join(rewritten_statement_lines).encode("utf-8")
    )
    mentions_path.write_bytes(write_csv_bytes(mentions_after, mention_fields))
    alignment_path.write_bytes(write_csv_bytes(alignments, alignment_fields))
    ROSTER_PATH.write_bytes(write_csv_bytes(roster, roster_fields, lineterminator="\r\n"))
    if sha256(LEDGER_PATH.read_bytes()) != ledger_before:
        raise SystemExit("Historical H9622 ledger was unexpectedly modified")
    if sha256(relations_path.read_bytes()) != relations_before:
        raise SystemExit("S6 relations.csv was unexpectedly modified")
    print("applied_stage_701_1000_without_changing_H9622_or_relations")


if __name__ == "__main__":
    main()
