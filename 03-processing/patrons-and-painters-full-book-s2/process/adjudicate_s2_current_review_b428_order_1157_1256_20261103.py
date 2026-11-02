#!/usr/bin/env python3
"""Apply the reviewed S2 batch B428 after a plan-hash preflight."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ROSTER_PATH = PROCESS / "s2-current-review-roster.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
HISTORY_PATH = PROCESS / "s2-history-9622-review-events.csv"
BASE_HEAD = "9251ea02e2aefefaa0fa786f4cfcf3e8cfcfb515"
HISTORY_SHA256 = "75ab12df478a816035929353565b0301d55959c6bb13d9b511af072c4c931c89"
BATCH_ID = "S2-B428-CH1-CH2-1157-1256"
STAGE_ID = "2026-11-03-s2-current-review-b428-order-1157-1256"
EVIDENCE_REF = "stages.md#" + STAGE_ID
SOURCE_HASHES = {
    "02-sources/01-book/CHP-1.pdf": "0b9a3ca88e6f09209bd20185948e18a68f527d0628e893940a7e3f07f6d22c86",
    "02-sources/01-book/CHP-2.pdf": "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e",
    "02-sources/02-Markdown/01_CHP-1_sec_ii.md": "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}
CH1_SEGMENT = "chp-1:01_CHP-1_sec_ii:l168-239"
CH2_SEGMENT = "chp-2:02_CHP-2_sec_i:l71-80"
NEW_LUTI_ID = "st-chp1-secii-l974-980-07b"
NEW_STPETERS_ID = "st-chp2-seci-l71-80-st-peters-transformation"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: object) -> str:
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_jsonl(path: Path) -> tuple[list[dict], list[str], bytes, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    rows = [json.loads(line) for line in lines if line.strip()]
    newline = "\r\n" if "\r\n" in text else "\n"
    return rows, lines, raw, newline


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str], bytes, str]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = list(reader.fieldnames or [])
    rows = list(reader)
    first_lf = raw.find(b"\n")
    newline = "\r\n" if first_lf > 0 and raw[first_lf - 1:first_lf] == b"\r" else "\n"
    if path == MENTIONS_PATH:
        for row in rows:
            row["surface_form"] = row["surface_form"].replace("\r\n", "\n")
    return rows, fields, raw, newline


def write_csv(rows: list[dict[str, str]], fields: list[str], newline: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline,
                            extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")


def source_mentions_at(revision: str, segment_id: str) -> dict[str, dict[str, str]]:
    raw = subprocess.check_output(
        ["git", "show", f"{revision}:04-knowledge/tables/mentions.csv"], cwd=ROOT
    ).decode("utf-8-sig")
    return {
        row["mention_id"]: row
        for row in csv.DictReader(io.StringIO(raw, newline=""))
        if row["segment_id"] == segment_id
    }


def make_statement_child(parent: dict, statement_id: str, subject: str | None,
                         object_: str | None, predicate: str, claim: str,
                         qualification: str, quote: str, line_start: int,
                         line_end: int, speaker: str, relation_note: str,
                         body_links: list[str], printed_page: int,
                         physical_page: int) -> dict:
    child = deepcopy(parent)
    child["statement_id"] = statement_id
    child["subject_candidate_id"] = subject
    child["object_candidate_id"] = object_
    child["predicate"] = predicate
    child["original_quote"] = quote
    page_fields = (
        {"printed_page": printed_page, "pdf_physical_page": physical_page}
        if "printed_page" in parent["qualifiers"]
        else {"print_page": printed_page, "pdf_page": physical_page}
    )
    child["qualifiers"] = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": speaker,
        "text_layer": "bibliographic note" if printed_page == 23 else "authorial narrative",
        "qualification": qualification,
        **page_fields,
        "relation_candidate": False,
        "relation_candidate_note": relation_note,
        "related_body_statement_ids": body_links,
        "linked_body_statement_ids": body_links,
    }
    return child


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expect-plan", default="")
    args = parser.parse_args()

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True).strip()
    require(head == BASE_HEAD, f"Expected base HEAD {BASE_HEAD}; found {head}")
    for relative, expected in SOURCE_HASHES.items():
        require(digest((ROOT / relative).read_bytes()) == expected,
                f"Source fingerprint changed: {relative}")
    history_raw = HISTORY_PATH.read_bytes()
    require(digest(history_raw) == HISTORY_SHA256,
            "The immutable H9622 event ledger changed; stop and reconcile before apply")

    statements, statement_lines, statement_raw, statement_eol = read_jsonl(STATEMENTS_PATH)
    roster, roster_fields, roster_raw, roster_eol = read_csv(ROSTER_PATH)
    mentions, mention_fields, mentions_raw, mentions_eol = read_csv(MENTIONS_PATH)
    candidates, candidate_fields, candidates_raw, candidates_eol = read_csv(CANDIDATES_PATH)
    alignments, alignment_fields, alignments_raw, alignments_eol = read_csv(ALIGNMENT_PATH)

    statement_by_id = {row["statement_id"]: row for row in statements}
    roster_by_id = {row["statement_id"]: row for row in roster}
    require(len(statements) == 15510 and len(roster) == 15510,
            "Unexpected base S2 table size")
    require(len(statement_by_id) == len(statements) == len(roster_by_id) == len(roster),
            "Duplicate S2 statement or roster ID")
    require(set(statement_by_id) == set(roster_by_id),
            "Statement IDs and current-version roster IDs differ")
    require(not any(row["review_batch_id"] == BATCH_ID for row in roster),
            "B428 is already applied to the current roster")
    require(NEW_LUTI_ID not in statement_by_id and NEW_STPETERS_ID not in statement_by_id,
            "A planned child statement ID already exists")

    selected = [row for row in roster if 1157 <= int(row["current_order"]) <= 1256]
    require(len(selected) == 100, f"Expected 100 base IDs, found {len(selected)}")
    pending_ids = {row["statement_id"] for row in selected
                   if row["current_review_status"] == "reviewed_current_pending"}
    expected_pending = {
        "st-chp1-secii-l971-973-06",
        "st-chp1-secii-l974-980-07",
        "st-chp2-seci-l71-80-resources-st-peters",
        "st-chp2-seci-l71-80-smm-family-chapel-comparison",
        "st-chp2-seci-l71-80-scipione-art-change",
    }
    require(pending_ids == expected_pending, f"Pending set changed: {sorted(pending_ids)}")
    require(sum(row["current_review_status"] == "reviewed_current_pass" for row in selected) == 95,
            "Expected 95 current PASS rows eligible for reuse")
    require(sum(int(row["history_9622_event_count"] or "0") for row in selected) == 100,
            "The interval no longer maps to 100 historical events")
    for row in roster:
        require(row["current_statement_sha256"] ==
                canonical_hash(statement_by_id[row["statement_id"]]),
                f"Current statement hash mismatch before apply: {row['statement_id']}")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["alignment_id"]: row for row in alignments}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    require(candidate_by_id["cand-4276"]["canonical_name"] ==
            "Barberini family chapel at S. Maria Maggiore",
            "Candidate cand-4276 changed since the source review")
    require(candidate_by_id["cand-4277"]["detail"] ==
            "The chapel used as a comparison for the Barberini family chapel; its relative richness and colour are Haskell’s assessment.",
            "Candidate cand-4277 changed since the source review")
    require(alignment_by_id["aln-4460"]["candidate_id"] == "cand-4276"
            and alignment_by_id["aln-4460"]["decision"] == "new"
            and "group=sg3-place-cand-4276" in alignment_by_id["aln-4460"]["resolution_note"],
            "S3 identity decision for cand-4276 changed")
    require(alignment_by_id["aln-4461"]["candidate_id"] == "cand-4277"
            and alignment_by_id["aln-4461"]["decision"] == "new"
            and "group=sg3-place-cand-4277" in alignment_by_id["aln-4461"]["resolution_note"],
            "S3 identity decision for cand-4277 changed")
    require(mention_by_id["m-chp2-seci-l71-80-0016"]["note"] ==
            "Barberini family chapel at S. Maria Maggiore; not the chapel at S. Andrea della Valle.",
            "The p.27 chapel mention changed since the source review")
    require(mention_by_id["m-chp1-secii-0447"]["note"] ==
            "Painter receiving an advance for an altarpiece in Cortona.",
            "The Ferri mention note changed since the source review")
    require(mention_by_id["m-chp1-secii-0403"]["note"] ==
            "Painter named in the chapter cross-reference.",
            "The Luti mention note changed since the source review")

    citation = statement_by_id["st-chp1-secii-l971-n1-cites-ruffo-correspondence-p172"]
    s1157 = statement_by_id["st-chp1-secii-l971-973-06"]
    s1162 = statement_by_id["st-chp1-secii-l974-980-07"]
    s1251 = statement_by_id["st-chp2-seci-l71-80-resources-st-peters"]
    s1252 = statement_by_id["st-chp2-seci-l71-80-smm-family-chapel-comparison"]
    s1254 = statement_by_id["st-chp2-seci-l71-80-scipione-art-change"]
    require(s1157["original_quote"].count("Baldinucci") == 1
            and s1157["qualifiers"]["source_line_end"] == 973,
            "Unexpected p.23 composite citation statement")
    require("And of Benedetto Luti" in s1162["original_quote"],
            "The Ferri/Luti source span has changed")
    require(s1251["subject_candidate_id"] == "cand-0393"
            and s1251["object_candidate_id"] == "cand-3135",
            "The Paul V/St Peter's endpoint pair changed")
    require(s1252["subject_candidate_id"] == "cand-4276"
            and s1252["object_candidate_id"] == "cand-4277",
            "The two chapel endpoints changed")
    require(s1254["subject_candidate_id"] == "cand-0394"
            and s1254["object_candidate_id"] == "cand-0393",
            "The Scipione/Paul V endpoint pair changed")

    changed_statement_ids: set[str] = set()
    insertions: dict[str, list[dict]] = defaultdict(list)

    q1157 = s1157["qualifiers"]
    q1157.update({
        "source_line_start": citation["qualifiers"]["source_line_start"],
        "source_line_end": citation["qualifiers"]["source_line_end"],
        "claim": "Haskell attaches footnote 1, which cites Giuseppe de Rosis's dated letter to Antonio Ruffo, to the preceding anonymous agent's appraisal of Rosa.",
        "speaker": "Haskell's footnote 1",
        "text_layer": "bibliographic note",
        "qualification": "The main text calls the speaker only 'an agent'. The footnote supplies a citation pointer; it does not explicitly name the agent or prove that the agent and letter author are the same person. The cited publication was not independently consulted.",
        "footnote_marker": 1,
        "relation_candidate": False,
        "relation_candidate_note": "This records the footnote-to-quotation source pointer only. The letter's author, addressee and publication are recorded separately; do not infer an ongoing corresponded_with relation.",
        "related_body_statement_ids": ["st-chp1-secii-l952-958-04d"],
        "linked_body_statement_ids": ["st-chp1-secii-l952-958-04d"],
        "printed_page": 23,
        "pdf_physical_page": 22,
    })
    s1157["subject_candidate_id"] = None
    s1157["object_candidate_id"] = None
    s1157["predicate"] = "footnote_attached_to_preceding_agent_appraisal"
    s1157["original_quote"] = citation["original_quote"]
    changed_statement_ids.add(s1157["statement_id"])

    ferri_quote = s1162["original_quote"]
    luti_start = ferri_quote.find("And of Benedetto Luti")
    require(luti_start > 0, "Could not locate the Luti clause in footnote 3")
    luti_quote = ferri_quote[luti_start:]
    ferri_quote = ferri_quote[:luti_start].rstrip()
    ferri_body_links = ["st-chp1-secii-l959-970-05e", "st-chp1-secii-l959-970-05f"]
    q1162 = s1162["qualifiers"]
    q1162.update({
        "source_line_start": 974,
        "source_line_end": 978,
        "claim": "Haskell presents Ciro Ferri as one of two artists showing signs of resistance to prevailing patronage: Ferri says he customarily avoided advance money to remain free, while the letter immediately qualifies this with the many affairs he handled.",
        "speaker": "Haskell quoting Ciro Ferri",
        "text_layer": "bibliographic note",
        "qualification": "Haskell frames this as limited resistance. Ferri's own quoted qualification is retained; the passage does not establish him as Rosa's follower or as sharing Rosa's full strategy.",
        "relation_candidate": False,
        "relation_candidate_note": "The note's comparison is contextual to Rosa's claim that he stood alone, not an ongoing person relation. The Ferri letter's author, addressee and cited publication are represented separately.",
        "related_body_statement_ids": ferri_body_links,
        "linked_body_statement_ids": ferri_body_links,
        "printed_page": 23,
        "pdf_physical_page": 22,
    })
    s1162["subject_candidate_id"] = "cand-3021"
    s1162["object_candidate_id"] = "cand-3099"
    s1162["predicate"] = "ferri_partial_patronage_resistance_reported_by_haskell"
    s1162["original_quote"] = ferri_quote
    changed_statement_ids.add(s1162["statement_id"])
    luti_child = make_statement_child(
        s1162, NEW_LUTI_ID, "cand-3004", "cand-3099",
        "luti_patronage_avoidance_reported_by_pascoli",
        "Haskell cites Pascoli as reporting that Benedetto Luti did not seek the protection of great patrons, rarely went to them, and said a good man's only protection should be good conduct.",
        "This is Pascoli's report as quoted by Haskell, not an independently consulted passage. Haskell places Luti among the two artists showing limited resistance to prevailing patronage; the comparison does not establish Luti as Rosa's follower or as sharing Rosa's full strategy.",
        luti_quote, 978, 980, "Haskell quoting Pascoli on Benedetto Luti",
        "The note gives a qualified contextual comparison with Rosa, not a formal relation. The Pascoli citation is recorded separately in st-chp1-secii-l978-980-n3-cites-pascoli-vol1-p233.",
        ferri_body_links, 23, 22,
    )
    insertions[s1162["statement_id"]].append(luti_child)

    q1251 = s1251["qualifiers"]
    q1251.update({
        "source_line_start": 75,
        "source_line_end": 76,
        "claim": "Haskell says the main resources of Pope Paul V and his nephew Cardinal Scipione Borghese were devoted to St Peter's.",
        "qualification": "On the printed page, 'their' follows both named patrons and is collective. The claim cannot be allocated to Paul V alone. No same-scope collective endpoint is registered, so retain this statement as pending and do not form a person-to-person or individual patronage edge.",
        "relation_candidate_note": "The source attributes resources collectively to Paul V and Scipione. The current table has no endpoint for this source-defined joint actor; the claim remains pending rather than assigning it to one person.",
        "other_candidates": ["cand-0393", "cand-0394"],
    })
    for key in ("footnote_refs", "footnote_segment", "footnote_marker"):
        q1251.pop(key, None)
    s1251["subject_candidate_id"] = None
    s1251["object_candidate_id"] = "cand-3135"
    s1251["predicate"] = "resources_devoted_to_basilica"
    s1251["original_quote"] = "Pope Paul V and his nephew Cardinal\nScipione Borghese were spending spectacular sums on palaces, churches, chapels, fountains and picture collections, and their example was being followed by a host of courtiers. Their main resources were devoted to St Peter’s"
    changed_statement_ids.add(s1251["statement_id"])
    peters_child = make_statement_child(
        s1251, NEW_STPETERS_ID, "cand-3135", None,
        "basilica_transformed_by_completion_of_nave_and_facade",
        "Haskell says St Peter's had been radically transformed through completion of its nave and façade.",
        "This is Haskell's description of the basilica's condition. The relative clause does not name a maker, commissioner or patron for the completed nave and façade.",
        "St Peter’s, which had been radically transformed by the completion of the nave and façade",
        76, 76, "Haskell",
        "Descriptive claim about the basilica only; do not infer a commission or creator from the completion clause.",
        [], 27, 8,
    )
    insertions[s1251["statement_id"]].append(peters_child)

    q1252 = s1252["qualifiers"]
    q1252.update({
        "claim": "Haskell says the family chapel at S. Maria Maggiore outdid the chapel of Sixtus V in richness and colour.",
        "qualification": "The source names only 'the family chapel' and does not identify the family. Preserve that unspecified attribution. The comparison is Haskell's aesthetic assessment, not a measurement or external assessment.",
    })
    for key in ("footnote_refs", "footnote_segment", "footnote_marker"):
        q1252.pop(key, None)
    s1252["original_quote"] = "S. Maria Maggiore where the family chapel outdid that of Sixtus V in richness and colour"
    changed_statement_ids.add(s1252["statement_id"])

    q1254 = s1254["qualifiers"]
    q1254.update({
        "qualification": "Authorial comparative assessment. On printed p.27, 'these changes' refers to Haskell's preceding list of changes in architecture, painting and sculpture; Paul V marks the period, not the object of Scipione's role. No single source-defined aggregate term endpoint is represented, so keep the endpoint pending.",
        "relation_candidate_note": "Paul V is not the object of Scipione's encouragement. The demonstrative 'these changes' refers to the preceding list; with no matching aggregate term endpoint, do not create a formal relation.",
    })
    s1254["object_candidate_id"] = None
    changed_statement_ids.add(s1254["statement_id"])

    child_ids = {luti_child["statement_id"], peters_child["statement_id"]}
    require(len(child_ids) == 2 and not (child_ids & set(statement_by_id)),
            "Child statement ID collision")
    statement_by_id[NEW_LUTI_ID] = luti_child
    statement_by_id[NEW_STPETERS_ID] = peters_child

    changed_mention_ids = {
        "m-chp1-secii-0447": "Painter whose 1672 letter is cited by Haskell as a qualified example concerning advance payments.",
        "m-chp1-secii-0403": "Painter whom Pascoli reports did not seek the protection of great patrons.",
        "m-chp2-seci-l71-80-0016": "The printed page names only 'the family chapel' at S. Maria Maggiore; family attribution is unspecified. Distinct from the chapel of Sixtus V at the same basilica.",
    }
    for mid, note in changed_mention_ids.items():
        mention_by_id[mid]["note"] = note

    candidate_by_id["cand-4276"]["canonical_name"] = (
        "Family chapel at S. Maria Maggiore (family attribution unspecified)"
    )
    candidate_by_id["cand-4276"]["detail"] = (
        "The printed page identifies only 'the family chapel' at S. Maria Maggiore; "
        "it does not name the family. Keep distinct from Maffeo Barberini's chapel at "
        "S. Andrea della Valle and from the chapel of Sixtus V at the same basilica."
    )
    alignment_by_id["aln-4460"]["resolution_note"] = (
        "group=sg3-place-cand-4276; source_ref=chp-2:02_CHP-2_sec_i:l71-80#L76; "
        "the source-supported object is the family chapel named at S. Maria Maggiore, "
        "but the family attribution is unspecified. Retain this distinct new place group; "
        "do not merge it with Maffeo Barberini's chapel at S. Andrea della Valle or the "
        "chapel of Sixtus V at S. Maria Maggiore. No KU is registered."
    )
    candidate_by_id["cand-4277"]["detail"] = (
        "The Sixtus V chapel at S. Maria Maggiore is named as the comparison target for "
        "a family chapel whose family is unspecified. Relative richness and colour are "
        "Haskell’s assessment."
    )
    alignment_by_id["aln-4461"]["resolution_note"] = (
        "group=sg3-place-cand-4277; source_ref=chp-2:02_CHP-2_sec_i:l71-80#L76; "
        "S2 identifies the Chapel of Sixtus V at S. Maria Maggiore as the comparison "
        "target for a family chapel whose family attribution is unspecified. Retain this "
        "distinct new place group; no KU is registered. Relative richness and colour are "
        "Haskell’s assessment."
    )

    segment_rows = defaultdict(list)
    for mention in mentions:
        segment_rows[mention["segment_id"]].append(mention)
    changed_segments = {CH1_SEGMENT, CH2_SEGMENT}
    new_statement_lines: list[str] = []
    rewritten_statement_lines: list[str] = []
    for line in statement_lines:
        if not line.strip():
            rewritten_statement_lines.append(line)
            continue
        row = json.loads(line)
        sid = row["statement_id"]
        if sid in changed_statement_ids:
            rewritten_statement_lines.append(
                json.dumps(statement_by_id[sid], ensure_ascii=False, separators=(",", ":")) + statement_eol
            )
        else:
            rewritten_statement_lines.append(line)
        for child in insertions.get(sid, []):
            rewritten_statement_lines.append(
                json.dumps(child, ensure_ascii=False, separators=(",", ":")) + statement_eol
            )
    statement_output = (
        (b"\xef\xbb\xbf" if statement_raw.startswith(b"\xef\xbb\xbf") else b"")
        + "".join(rewritten_statement_lines).encode("utf-8")
    )

    roster_by_id = {row["statement_id"]: row for row in roster}
    selected_ids = {row["statement_id"] for row in selected}
    for sid in selected_ids:
        row = roster_by_id[sid]
        row["review_batch_id"] = BATCH_ID
        row["review_evidence_ref"] = EVIDENCE_REF
        if row["current_review_status"] == "reviewed_current_pass":
            row["review_outcome"] = "reused_exact_current_pass_after_targeted_stage_review"

    outcomes = {
        "st-chp1-secii-l971-973-06": (
            "reviewed_current_pass",
            "current_pending_finding_resolved_after_original_page_review",
            "Printed p.23 note 1 is attached to the preceding agent appraisal; note 2 remains the separate Baldinucci citation. The main text does not name the agent. Prior finding: ",
        ),
        "st-chp1-secii-l974-980-07": (
            "reviewed_current_pass",
            "current_pending_finding_resolved_after_original_page_review",
            "Printed p.23 note 3 has been split into Ferri and Luti claims; this parent now covers Ferri alone, while letter roles/publication remain separate. Prior finding: ",
        ),
        "st-chp2-seci-l71-80-resources-st-peters": (
            "reviewed_current_pending",
            "current_open_finding_retained_after_original_page_review",
            "Printed p.27 'their' follows Pope Paul V and Scipione together; the erroneous Paul V-only endpoint was removed. No same-scope group endpoint is registered. The transformation clause is split into a PASS child. Prior finding: ",
        ),
        "st-chp2-seci-l71-80-smm-family-chapel-comparison": (
            "reviewed_current_pass",
            "current_pending_finding_resolved_after_original_page_review",
            "Printed p.27 says only 'the family chapel'; cand-4276 was renamed without assigning a family. Its S3 new group is retained. Prior finding: ",
        ),
        "st-chp2-seci-l71-80-scipione-art-change": (
            "reviewed_current_pending",
            "current_open_finding_retained_after_original_page_review",
            "Printed p.27 'these changes' refers to the preceding list, not Paul V; the incorrect Paul V object endpoint was removed. The aggregate term endpoint remains unrepresented. Prior finding: ",
        ),
    }
    for sid, (status, outcome, explanation) in outcomes.items():
        row = roster_by_id[sid]
        row["current_review_status"] = status
        row["review_batch_id"] = BATCH_ID
        row["review_outcome"] = outcome
        row["review_evidence_ref"] = EVIDENCE_REF
        row["follow_up_note"] = explanation + row.get("follow_up_note", "")

    segment_by_id = {}
    for row in roster:
        segment_by_id[row["segment_id"]] = row
    segment_rows_current = defaultdict(list)
    for mention in mentions:
        segment_rows_current[mention["segment_id"]].append(mention)

    insert_roster_after = {
        "st-chp1-secii-l974-980-07": [luti_child],
        "st-chp2-seci-l71-80-resources-st-peters": [peters_child],
    }
    for parent_id, children in insert_roster_after.items():
        parent = roster_by_id[parent_id]
        for statement in children:
            segid = statement["segment_id"]
            seg_rows = segment_rows_current[segid]
            row = dict(parent)
            row.update({
                "current_order": "",
                "statement_id": statement["statement_id"],
                "source_line_start": str(statement["qualifiers"]["source_line_start"]),
                "source_line_end": str(statement["qualifiers"]["source_line_end"]),
                "snapshot_statement_sha256": "",
                "current_statement_sha256": canonical_hash(statement),
                "history_9622_membership": "not_in_reconstructed_count",
                "prior_review_match": "no_exact_review_mapping",
                "prior_review_ref": "",
                "current_review_status": "reviewed_current_pass",
                "review_batch_id": BATCH_ID,
                "review_outcome": "current_statement_semantic_pass_source_claim_and_printed_page_verified",
                "review_evidence_ref": EVIDENCE_REF,
                "follow_up_note": (
                    "Atomic source statement split from " + parent_id +
                    "; its evidence and endpoint boundary are recorded in B428."
                ),
                "history_9622_event_count": "0",
                "history_9622_latest_review_commit": "",
                "history_9622_latest_statement_sha256": "",
                "history_9622_current_statement_match": "",
                "history_9622_source_match": "",
                "history_9622_mention_delta": "",
                "history_9622_evidence_ref": "",
                "segment_sha256": parent["segment_sha256"],
                "source_asset_sha256": parent["source_asset_sha256"],
                "current_segment_mention_count": str(len(seg_rows)),
                "current_segment_mentions_sha256": canonical_hash(
                    sorted(seg_rows, key=lambda mention: mention["mention_id"])
                ),
            })
            roster_by_id[statement["statement_id"]] = row

    for sid in changed_statement_ids:
        row = roster_by_id[sid]
        row["current_statement_sha256"] = canonical_hash(statement_by_id[sid])
        if int(row["history_9622_event_count"] or "0") > 0:
            match = ("exact" if row["history_9622_latest_statement_sha256"]
                     == row["current_statement_sha256"] else "changed")
            row["history_9622_current_statement_match"] = match
            row["prior_review_match"] = (
                "exact_object_and_source_segment"
                if match == "exact" and row["history_9622_source_match"] == "true"
                else "historical_object_or_source_differs"
            )

    roster_after: list[dict[str, str]] = []
    for row in roster:
        roster_after.append(row)
        for child in insert_roster_after.get(row["statement_id"], []):
            roster_after.append(roster_by_id[child["statement_id"]])
    require(len(roster_after) == 15512,
            f"Unexpected roster size after two source-adjacent splits: {len(roster_after)}")
    for order, row in enumerate(roster_after, 1):
        row["current_order"] = str(order)

    mention_delta_cache: dict[tuple[str, str], dict[str, str]] = {}
    for row in roster_after:
        segment_id = row["segment_id"]
        if segment_id not in changed_segments:
            continue
        current_mentions = segment_rows_current[segment_id]
        row["current_segment_mention_count"] = str(len(current_mentions))
        row["current_segment_mentions_sha256"] = canonical_hash(
            sorted(current_mentions, key=lambda mention: mention["mention_id"])
        )
        if int(row["history_9622_event_count"] or "0") <= 0:
            continue
        revision = row["history_9622_latest_review_commit"]
        key = (revision, segment_id)
        if key not in mention_delta_cache:
            old_mentions = source_mentions_at(revision, segment_id)
            new_mentions = {mention["mention_id"]: mention for mention in current_mentions}
            mention_delta_cache[key] = {
                "changed": sorted(mid for mid in old_mentions.keys() & new_mentions.keys()
                                  if old_mentions[mid] != new_mentions[mid]),
                "removed": sorted(old_mentions.keys() - new_mentions.keys()),
                "added": sorted(new_mentions.keys() - old_mentions.keys()),
            }
        row["history_9622_mention_delta"] = json.dumps(
            mention_delta_cache[key], ensure_ascii=False, separators=(",", ":")
        )

    new_statement_hashes = {sid: canonical_hash(row) for sid, row in statement_by_id.items()}
    for row in roster_after:
        sid = row["statement_id"]
        require(row["current_statement_sha256"] == new_statement_hashes[sid],
                f"Roster statement fingerprint mismatch after plan: {sid}")
    require(sum(row["current_review_status"] == "reviewed_current_pass"
                for row in roster_after) == 8674,
            "Unexpected post-stage PASS count")
    require(sum(row["current_review_status"] == "reviewed_current_pending"
                for row in roster_after) == 6838,
            "Unexpected post-stage pending count")
    require(len(mentions) == 27331, "The reviewed stage should not add or remove mentions")

    changed_paths: dict[Path, bytes] = {
        STATEMENTS_PATH: statement_output,
        ROSTER_PATH: write_csv(roster_after, roster_fields, roster_eol),
        MENTIONS_PATH: write_csv(mentions, mention_fields, mentions_eol),
        CANDIDATES_PATH: write_csv(candidates, candidate_fields, candidates_eol),
        ALIGNMENT_PATH: write_csv(alignments, alignment_fields, alignments_eol),
    }
    original_raw = {
        STATEMENTS_PATH: statement_raw,
        ROSTER_PATH: roster_raw,
        MENTIONS_PATH: mentions_raw,
        CANDIDATES_PATH: candidates_raw,
        ALIGNMENT_PATH: alignments_raw,
    }
    summary = {
        "base_head": head,
        "batch_id": BATCH_ID,
        "base_range": [1157, 1256],
        "base_ids": len(selected),
        "reused_current_pass": 95,
        "reviewed_findings_resolved": [
            "st-chp1-secii-l971-973-06",
            "st-chp1-secii-l974-980-07",
            "st-chp2-seci-l71-80-smm-family-chapel-comparison",
        ],
        "reviewed_findings_retained_pending": [
            "st-chp2-seci-l71-80-resources-st-peters",
            "st-chp2-seci-l71-80-scipione-art-change",
        ],
        "new_atomic_statements": sorted(child_ids),
        "post_stage_batch_rows": 102,
        "post_stage_batch_pass": 100,
        "post_stage_batch_pending": 2,
        "post_stage_statement_count": len(statements) + 2,
        "post_stage_mention_count": len(mentions),
        "post_stage_status_counts": dict(Counter(r["current_review_status"] for r in roster_after)),
        "history_event_ledger_sha256": digest(history_raw),
        "history_event_ledger_rewritten": False,
        "changed_segment_mention_rows": {
            segment: [mid for mid in changed_mention_ids
                      if mention_by_id[mid]["segment_id"] == segment]
            for segment in sorted(changed_segments)
        },
        "files": {
            path.relative_to(ROOT).as_posix(): {
                "before": digest(original_raw[path]),
                "after": digest(data),
            }
            for path, data in changed_paths.items()
        },
    }
    plan_hash = digest(json.dumps(summary, ensure_ascii=False, sort_keys=True,
                                  separators=(",", ":")).encode("utf-8"))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("plan_sha256=" + plan_hash)

    if not args.apply:
        return
    if args.expect_plan != plan_hash:
        raise SystemExit("Apply requires --expect-plan matching this exact inspected plan")
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "The immutable H9622 ledger changed before apply")
    for path, data in changed_paths.items():
        temp = path.with_name(path.name + ".b428.tmp")
        require(not temp.exists(), f"Refusing to overwrite recovery temp: {temp}")
        temp.write_bytes(data)
        temp.replace(path)
    require(digest(HISTORY_PATH.read_bytes()) == HISTORY_SHA256,
            "The immutable H9622 ledger changed during apply")
    print("applied B428 structured tables; H9622 event ledger unchanged")


if __name__ == "__main__":
    main()
