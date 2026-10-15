from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l152-163"
PREFIX = "st-chp3-seciv-l152-163-"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "ddbd6a94727311c0ad9be879ae7f437db41b52f7ae0a6174cd7b418b223257fb"
PRE_HASHES = {
    STATEMENTS.name: "8264433909a2205d9f146f497c64b2921171fbb8efed091cd632770765a39259",
    CANDIDATES.name: "8561ba26c7cd1136abf1e48c49ceac67152bddd05defae78194d2bed0c8b8851",
    MENTIONS.name: "2af4b0abf1dec49f83b4f51f53bec337f339c7a2f6c04a2f2b789c5f256a4843",
    COVERAGE.name: "5e3a6fe18aab19b79a00e9a592750764fba9b53cf01e351c3b807581c13f82d7",
}
BACKUP_SUFFIX = ".bak-s2-chp3-seciv-l152-163-relations-20261011"


RELATION_NOTES = {
    "altar-expense-presumed-jesuit": "Haskell marks the Jesuits' payment for Cortona's replacement altar as presumptive; the earlier Della Porta altar is a separate work.",
    "chapel-belonged-to-savelli-heirs": "The source states that the left-transept chapel belonged to the unnamed heirs of Cardinal Savelli; it does not identify individual heirs.",
    "chapel-conceived-for-founder": "The passage identifies the chapel as dedicated to the founder, St Ignatius; its superlative description remains Haskell's evaluation.",
    "chapel-reverted-to-jesuits": "Haskell says the heirs seem to have taken no interest in the chapel for over a century; this row records only that qualified lack of interest.",
    "congregation-agreed-monument": "The 1646 Eighth General Congregation agreed that a more ambitious monument should be established; this is a decision to establish a project, not evidence it was completed.",
    "crucifixion-dedication-altar-unfinished": "The chapel's original dedication to the Crucifixion is distinct from the uncompleted altar; the latter is recorded in separate work statements.",
    "duke-delay-made-plan-impossible": "Haskell reports an unnamed assessment that the Duke of Parma's parsimony and delay made Oliva's plan impossible; the duke's identity is unresolved.",
    "funds-arrived-from-europe": "The source says large sums arrived from across Europe for the chapel; it does not identify contributors, amounts, or a transfer record.",
    "gonzalez-resumed-undertaking": "Haskell says the monument undertaking resumed in the transept chapel after Gonzalez took office in 1687; the sentence continues on p.92.",
    "legacy-and-college-plan": "The source reports a legacy left to the Jesuits in Peru; the donor, amount, and exact date are not stated.",
    "memorandum-argued-ignatius-deserved-memorial": "This records the memorandum's reported argument, not independent verification of its comparative claim about founders buried in Rome.",
    "memorandum-cites-other-founders": "The statement records the memorandum's comparison as reported by Haskell; the passage does not identify the cited monuments individually.",
    "nickel-proposed-redirecting-legacy": "Haskell reports Nickel's proposal to use the Peru legacy for decorating a Gesu chapel; proposal is not evidence that funds were redirected or work executed.",
    "oliva-preferred-high-altar-monument": "The scan reads 'not in the transept'; S0 OCR reads 'hot'. This is Oliva's proposed location under the High Altar, not an executed placement.",
    "pozzo-follows-jesuit-decoration-feature": "This is Haskell's interpretation of Pozzo's account of a recurring Jesuit decorative motif, not independently verified evidence of the artist's intent.",
    "remains-and-picture-placed-in-chapel": "Haskell says the Jesuits moved Ignatius's physical remains into the chapel after his 1622 canonisation; the remains are distinct from Ignatius as a person.",
    "spaniards-rejected-proposal-and-rumour": "The source says the Spaniards 'evidently' did not welcome Nickel's proposal; this row records the qualified reaction only.",
    "three-churches-spectacular": "The claim that the three principal Jesuit churches were Rome's most spectacular is Haskell's evaluative account and attribution to the Jesuits, not an independent ranking.",
    "urn-offered-and-new-altar-built": "Haskell says the Jesuits were offered Algardi's urn fifteen years after the remains were moved; the urn's date and present location are not supplied.",
}

NONRELATION_NOTES = {
    "further-works-continued": "This is Haskell's qualified causal interpretation and a report of unspecified new works; the passage does not identify a second entity or their makers.",
    "legacy-redirection-dropped": "This records the status of Nickel's proposal. The passage does not identify who dropped it or establish the rumour as the cause.",
    "monument-work-paused": "This records the reported status of the project under the Society's stated poverty and adverse times, not a relation between two entities.",
    "noyelle-generalship-too-short": "This is a one-person biographical assessment of the duration of Noyelle's generalship, not an entity-to-entity relation.",
    "oliva-died-disappointed": "This is a one-person biographical state reported by Haskell, not an entity-to-entity relation.",
}

QUOTE_SPECS = {
    "altar-expense-presumed-jesuit": (158, 158, "the expense of which was presumably borne by the Jesuits themselves"),
    "chapel-belonged-to-savelli-heirs": (155, 155, "The chapel in the left transept of the Gesù belonged to the heirs of Cardinal Savelli.2"),
    "chapel-conceived-for-founder": (154, 154, "Among them was the most elaborate chapel ever conceived, dedicated to the founder of the movement which had so signally triumphed."),
    "chapel-reverted-to-jesuits": (156, 156, "After the death of the Cardinal, his heirs seem to have taken no interest in the chapel for over a century"),
    "congregation-agreed-monument": (158, 158, "In 1646, the Eighth General Congregation of the Society agreed that a more ambitious monument should be established."),
    "crucifixion-dedication-altar-unfinished": (156, 156, "Dedicated originally to the Crucifixion"),
    "duke-delay-made-plan-impossible": (162, 162, "It has been pointed out that the parsimony and delay of the Duke of Parma made this impossible"),
    "funds-arrived-from-europe": (161, 161, "Meanwhile, vast sums began to pour in from all over Europe for the building of the chapel."),
    "further-works-continued": (154, 154, "But even after they had been completed, the very energy that had been employed seemed to encourage further efforts, and in the last few years of the century many new works were undertaken."),
    "gonzalez-resumed-undertaking": (162, 163, "under the Spaniard,\nTirso Gonzalez, who took over in 1687, the undertaking was again resumed in the transept chapel"),
    "legacy-and-college-plan": (159, 159, "Four years after this a vast legacy was left to the Jesuits in Peru"),
    "legacy-redirection-dropped": (160, 160, "Again, the matter was dropped."),
    "memorandum-argued-ignatius-deserved-memorial": (159, 159, "surely St Ignatius, who alone of all the saintly founders of Orders was buried in Rome, should also have a fine memorial."),
    "memorandum-cites-other-founders": (158, 159, "They drew up a memorandum which pointed out that St Dominic in Bologna, St Francis in Assisi and St Benedict in\nMontecassino were all suitably commemorated"),
    "monument-work-paused": (159, 159, "In view, however, of the Society’s ‘extreme poverty and the disastrous times’, nothing further was done."),
    "nickel-proposed-redirecting-legacy": (160, 160, "The General of the Society, Padre Nickel, suggested that the money would be better employed in decorating a chapel in the Gesù in Rome."),
    "noyelle-generalship-too-short": (162, 162, "The four-year Generalship of his Belgian successor, Charles de Noy elle, was too short for much to be done"),
    "oliva-died-disappointed": (162, 162, "Oliva died, disappointed, in 1681."),
    "oliva-preferred-high-altar-monument": (161, 162, "the monument to\nIgnatius \"hot in the transept but under the High Altar, as the most spectacular feature of the tribune"),
    "pozzo-follows-jesuit-decoration-feature": (153, 153, "This short extract from Pozzo’s description makes it clear that he too was following one of the constant features of Jesuit decoration"),
    "remains-and-picture-placed-in-chapel": (156, 156, "When Ignatius was canonised in 1622, they moved his remains to this chapel"),
    "spaniards-rejected-proposal-and-rumour": (160, 160, "But the Spaniards evidently did not welcome this idea"),
    "three-churches-spectacular": (154, 154, "All this lavish decoration turned the three principal Jesuit churches into the most spectacular in Rome, as they were the first to point out."),
    "urn-offered-and-new-altar-built": (157, 157, "Fifteen years later, the Jesuits were offered a superb urn, modelled by Algardi, in which to place the saint’s bones"),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11624",
        "index_entry_id": "",
        "canonical_name": "Uncompleted Della Porta altar for the Chapel of St Ignatius in the Gesù",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The earlier altar was designed by Giacomo della Porta but never completed. Haskell says Pietro da Cortona later built a replacement; keep this predecessor distinct from the left-transept altar above which Gaulli painted in 1685 (cand-5246).",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L156",
    },
    {
        "candidate_id": "cand-11625",
        "index_entry_id": "",
        "canonical_name": "Padre Nickel's proposal to use the Peru legacy for a Gesù chapel",
        "index_page_range": "",
        "suggested_type": "event",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Source-bounded proposal event: Haskell says Padre Nickel suggested using the legacy left to the Jesuits in Peru to decorate a chapel in the Gesu. The Spaniards evidently did not welcome the idea, and the matter was later dropped. The passage does not identify who ended it or report any transfer of funds or executed decoration.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L160",
    },
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], bytes]:
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, raw


def read_csv(path: Path) -> tuple[list[str], list[dict], str, bool, bytes]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    fields = list(csv.DictReader(io.StringIO(text, newline="")).fieldnames or [])
    return fields, rows, eol, bom, raw


def encode_csv(fields: list[str], rows: list[dict], eol: str, bom: bool) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="raise", lineterminator=eol)
    writer.writeheader()
    writer.writerows(rows)
    return (("\ufeff" if bom else "") + output.getvalue()).encode("utf-8")


def encode_jsonl_preserving_unchanged(rows: list[dict], raw: bytes) -> bytes:
    lines = raw.splitlines(keepends=True)
    current = {row["statement_id"]: row for row in rows}
    if len(current) != len(rows):
        raise SystemExit("duplicate statement IDs in prepared JSONL")
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[bytes] = []
    old_ids: set[str] = set()
    for index, line in enumerate(lines):
        if not line.strip():
            output.append(line)
            continue
        old = json.loads(line.decode("utf-8-sig"))
        sid = old["statement_id"]
        if sid in old_ids or sid not in current:
            raise SystemExit(f"duplicate or removed statement in prepared table: {sid}")
        old_ids.add(sid)
        if old == current[sid]:
            output.append(line)
        else:
            encoded = (json.dumps(current[sid], ensure_ascii=False, separators=(",", ":")) + eol.decode("ascii")).encode("utf-8")
            if index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            output.append(encoded)
    new_ids = set(current) - old_ids
    if new_ids and output and not output[-1].endswith((b"\n", b"\r")):
        output.append(eol)
    for row in rows:
        if row["statement_id"] in new_ids:
            output.append((json.dumps(row, ensure_ascii=False, separators=(",", ":")) + eol.decode("ascii")).encode("utf-8"))
    return b"".join(output)


def exact_quote(source_lines: list[str], start: int, end: int, quote: str) -> str:
    excerpt = "\n".join(source_lines[start - 1 : end])
    if quote not in excerpt:
        raise SystemExit(f"quote is not present in S0 L{start}-{end}: {quote!r}")
    return quote


def make_statement(
    suffix: str,
    subject: str | None,
    object_: str | None,
    predicate: str,
    quote: str,
    line_start: int,
    line_end: int,
    claim: str,
    qualification: str,
    relation_candidate: bool,
    relation_note: str,
    *,
    mentioned_candidate_ids: list[str] | None = None,
    speaker: str = "Haskell",
    text_layer: str = "authorial narrative",
) -> dict:
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "print_page": 91,
        "pdf_physical_page": 33,
        "qualification": qualification,
        "relation_candidate": relation_candidate,
        "relation_candidate_note": relation_note,
    }
    if mentioned_candidate_ids:
        qualifiers["mentioned_candidate_ids"] = mentioned_candidate_ids
    return {
        "statement_id": PREFIX + suffix,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and atomize CHP-3 printed p.91 S2 statements.")
    parser.add_argument("--apply", action="store_true", help="write after all preconditions, scope checks, and recovery copies pass")
    args = parser.parse_args()

    source_raw = SOURCE.read_bytes()
    if sha(source_raw) != SOURCE_SHA:
        raise SystemExit("source hash changed; re-review before applying")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_rows, _ = read_jsonl(SEGMENTS)
    segment_meta = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(segment_meta) != 1 or segment_meta[0].get("sha256") != SEGMENT_SHA:
        raise SystemExit("normalized segment hash changed; re-review before applying")

    statement_rows, statement_raw = read_jsonl(STATEMENTS)
    candidate_fields, candidate_rows, candidate_eol, candidate_bom, candidate_raw = read_csv(CANDIDATES)
    mention_fields, mention_rows, mention_eol, mention_bom, mention_raw = read_csv(MENTIONS)
    coverage_fields, coverage_rows, coverage_eol, coverage_bom, coverage_raw = read_csv(COVERAGE)
    raw_by_name = {
        STATEMENTS.name: statement_raw,
        CANDIDATES.name: candidate_raw,
        MENTIONS.name: mention_raw,
        COVERAGE.name: coverage_raw,
    }
    for name, expected in PRE_HASHES.items():
        if sha(raw_by_name[name]) != expected:
            raise SystemExit(f"{name} changed since review; do not reapply")

    segment_statements = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    expected_suffixes = set(QUOTE_SPECS)
    found_suffixes = {
        row["statement_id"][len(PREFIX) :]
        for row in segment_statements
        if row["statement_id"].startswith(PREFIX)
    }
    if len(segment_statements) != 24 or found_suffixes != expected_suffixes:
        raise SystemExit(f"unexpected p.91 statement scope: count={len(segment_statements)}, missing={sorted(expected_suffixes-found_suffixes)}, extra={sorted(found_suffixes-expected_suffixes)}")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in segment_statements):
        raise SystemExit("p.91 statements already classified; re-review before applying")
    coverage = [row for row in coverage_rows if row.get("segment_id") == SEGMENT_ID]
    if len(coverage) != 1 or (coverage[0].get("disposition"), coverage[0].get("migration_status")) != ("reviewed", "complete"):
        raise SystemExit("p.91 coverage changed; re-review before applying")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs")
    if any(candidate["candidate_id"] in candidate_by_id for candidate in NEW_CANDIDATES):
        raise SystemExit("one or more new candidate IDs already exist")
    numeric_ids = [int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-")]
    if max(numeric_ids) != 11623:
        raise SystemExit(f"unexpected candidate sequence maximum: {max(numeric_ids)}")
    natural_keys = {(row.get("canonical_name", ""), row.get("suggested_type", "")) for row in candidate_rows}
    for candidate in NEW_CANDIDATES:
        key = (candidate["canonical_name"], candidate["suggested_type"])
        if key in natural_keys:
            raise SystemExit(f"new candidate duplicates an existing natural key: {key}")
    if "cand-0960" not in candidate_by_id or "cand-5246" not in candidate_by_id:
        raise SystemExit("expected cross-page artist/altar candidates are missing")
    if candidate_by_id["cand-0960"].get("suggested_type") != "work":
        raise SystemExit("Van Dyck index candidate type differs from the reviewed pre-state")
    if candidate_by_id["cand-5246"].get("canonical_name") != "Altar of St Ignatius in the Gesù left transept":
        raise SystemExit("left-transept altar candidate changed; re-review object identity")
    for candidate_id in ("cand-5399", "cand-5413"):
        if candidate_by_id[candidate_id].get("suggested_type") != "term":
            raise SystemExit(f"collective candidate type changed: {candidate_id}")

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("duplicate mention IDs")
    new_mention_ids = {"m-chp3-seciv-l152-163-0070", "m-chp3-seciv-l152-163-0071"}
    if new_mention_ids & mention_by_id.keys():
        raise SystemExit("one or more new mention IDs already exist")
    if not {"m-chp3-seciv-l152-163-0015", "m-chp3-seciv-l152-163-0016", "m-chp3-seciv-l152-163-0031"} <= mention_by_id.keys():
        raise SystemExit("expected altar and Van Dyck mentions are missing")

    all_statement_ids = {row["statement_id"] for row in statement_rows}
    if len(all_statement_ids) != len(statement_rows):
        raise SystemExit("duplicate statement IDs in source table")
    row_by_suffix = {row["statement_id"][len(PREFIX) :]: row for row in segment_statements}

    for suffix, (line_start, line_end, quote) in QUOTE_SPECS.items():
        row = row_by_suffix[suffix]
        row["original_quote"] = exact_quote(source_lines, line_start, line_end, quote)
        qualifiers = row.setdefault("qualifiers", {})
        qualifiers["source_line_start"] = line_start
        qualifiers["source_line_end"] = line_end
        if suffix in RELATION_NOTES:
            qualifiers["relation_candidate"] = True
            qualifiers["relation_candidate_note"] = RELATION_NOTES[suffix]
        elif suffix in NONRELATION_NOTES:
            qualifiers["relation_candidate"] = False
            qualifiers["relation_candidate_note"] = NONRELATION_NOTES[suffix]
        else:
            raise SystemExit(f"missing classification for {suffix}")

    # Correct the cross-page altar mapping: the earlier Della Porta altar was not completed;
    # cand-5246 is the later left-transept altar above which Gaulli painted in 1685.
    candidate_by_id["cand-5246"]["detail"] = (
        "The later left-transept altar of St Ignatius above which Gaulli painted in 1685. "
        "P.91 reports that Pietro da Cortona built a new altar to replace Della Porta's uncompleted predecessor; "
        "the passage contextually links this candidate to Cortona's altar. Distinct from the Gesù High Altar."
    )
    candidate_by_id["cand-0960"]["suggested_type"] = "person"
    candidate_by_id["cand-0960"]["detail"] = (
        "Person named by the D.csv index heading; its subentry points to paintings of St Ignatius and St Francis Xavier. "
        "Keep this index candidate separate from person candidate cand-8909 pending S3 identity alignment."
    )
    candidate_by_id["cand-5399"]["suggested_type"] = ""
    candidate_by_id["cand-5399"]["detail"] = (
        "Collective heirs named by Haskell; the passage identifies neither individuals nor a family, and the current taxonomy "
        "has no generic person-group type. Keep type unresolved pending S3."
    )
    candidate_by_id["cand-5413"]["suggested_type"] = ""
    candidate_by_id["cand-5413"]["detail"] = (
        "Unspecified people referred to as 'the Spaniards'; membership and institutional identity are unknown, and the current "
        "taxonomy has no generic people-group type. Keep type unresolved pending S3."
    )
    mention_by_id["m-chp3-seciv-l152-163-0015"]["candidate_id"] = "cand-11624"
    mention_by_id["m-chp3-seciv-l152-163-0015"]["note"] = (
        "The earlier Della Porta altar, never completed; distinct from Cortona's replacement altar."
    )
    mention_by_id["m-chp3-seciv-l152-163-0016"]["candidate_id"] = "cand-5246"
    mention_by_id["m-chp3-seciv-l152-163-0016"]["note"] = (
        "The new left-transept altar built by Pietro da Cortona to replace Della Porta's uncompleted predecessor; "
        "contextually matched to the later altar above which Gaulli painted in 1685."
    )
    mention_by_id["m-chp3-seciv-l152-163-0031"]["note"] = (
        "Haskell names Van Dyck as the picture's painter. The index candidate is typed as a person; its identity "
        "alignment with the separate Van Dyck person candidate cand-8909 is deferred to S3."
    )

    # Reuse existing rows for the first atomic claim and add rows for distinct claims.
    altar_expense = row_by_suffix["altar-expense-presumed-jesuit"]
    altar_expense["object_candidate_id"] = "cand-5246"
    altar_expense["predicate"] = "presumably_bore_expense_of_cortona_replacement_altar"
    altar_expense["qualifiers"]["claim"] = "Haskell says the Jesuits presumably bore the expense of Pietro da Cortona's replacement altar."
    altar_expense["qualifiers"]["qualification"] = "The source explicitly marks the attribution as presumptive; the predecessor altar is cand-11624."

    heirs = row_by_suffix["chapel-reverted-to-jesuits"]
    heirs["subject_candidate_id"] = "cand-5399"
    heirs["object_candidate_id"] = "cand-5236"
    heirs["predicate"] = "seemingly_took_no_interest_in_chapel_for_over_a_century"
    heirs["qualifiers"]["claim"] = "Haskell says the heirs seem to have taken no interest in the chapel for over a century after the Cardinal's death."
    heirs["qualifiers"]["qualification"] = "Preserve 'seem'; the heirs are unnamed and the duration is approximate. The chapel's unofficial reversion is recorded separately."

    crucifixion = row_by_suffix["crucifixion-dedication-altar-unfinished"]
    crucifixion["subject_candidate_id"] = "cand-5236"
    crucifixion["object_candidate_id"] = "cand-5398"
    crucifixion["predicate"] = "dedicated_originally_to_crucifixion"
    crucifixion["qualifiers"]["claim"] = "Haskell says the chapel was originally dedicated to the Crucifixion."
    crucifixion["qualifiers"]["qualification"] = "The dedication is not a claim about a specific Crucifixion artwork; the altar is a distinct work."

    remains = row_by_suffix["remains-and-picture-placed-in-chapel"]
    remains["predicate"] = "moved_ignatius_remains_to_chapel_after_1622_canonisation"
    remains["qualifiers"]["claim"] = "Haskell says the Jesuits moved Ignatius's remains to the chapel after his 1622 canonisation."
    remains["qualifiers"]["qualification"] = "This records the movement of physical remains to the chapel; placement and authorship of Van Dyck's picture are separate claims."
    remains["qualifiers"]["mentioned_candidate_ids"] = ["cand-5220"]

    legacy = row_by_suffix["legacy-and-college-plan"]
    legacy["subject_candidate_id"] = "cand-5409"
    legacy["object_candidate_id"] = "cand-3403"
    legacy["predicate"] = "legacy_left_to_jesuits_in_peru"
    legacy["qualifiers"]["claim"] = "Haskell says a vast legacy was left to the Jesuits in Peru four years after the memorandum."
    legacy["qualifiers"]["qualification"] = "The donor, amount, and exact date are not supplied; the source does not say that the legacy was later redirected."
    legacy["qualifiers"]["mentioned_candidate_ids"] = ["cand-5279"]

    dropped = row_by_suffix["legacy-redirection-dropped"]
    dropped["subject_candidate_id"] = "cand-11625"
    dropped["object_candidate_id"] = None
    dropped["predicate"] = "nickel_proposal_was_dropped"
    dropped["qualifiers"]["claim"] = "Haskell says the proposal concerning the Peru legacy was later dropped."
    dropped["qualifiers"]["qualification"] = "The passage does not identify a decision-maker or establish that the rumour alone caused the outcome."
    dropped["qualifiers"]["mentioned_candidate_ids"] = ["cand-5413", "cand-1740", "cand-5409", "cand-5236"]

    pause = row_by_suffix["monument-work-paused"]
    pause["subject_candidate_id"] = "cand-5402"
    pause["object_candidate_id"] = None
    pause["predicate"] = "no_further_work_was_done_on_monument_project"
    pause["qualifiers"]["claim"] = "Haskell says nothing further was done on the monument project in view of the Society's stated poverty and adverse times."
    pause["qualifiers"]["qualification"] = "This is Haskell's reported project status and causal explanation; no completed monument is inferred."
    pause["qualifiers"]["mentioned_candidate_ids"] = ["cand-3403"]

    proposal = row_by_suffix["nickel-proposed-redirecting-legacy"]
    proposal["object_candidate_id"] = "cand-11625"
    proposal["predicate"] = "proposed_use_of_peru_legacy_for_gesu_chapel"
    proposal["qualifiers"]["claim"] = "Haskell says Padre Nickel proposed using the Peru legacy to decorate a chapel in the Gesù."
    proposal["qualifiers"]["qualification"] = "This records a proposal only; the text does not say funds were redirected or that the chapel was decorated with them. Nickel's identity remains for S3."
    proposal["qualifiers"]["mentioned_candidate_ids"] = ["cand-5409", "cand-5279", "cand-5236"]

    spaniards = row_by_suffix["spaniards-rejected-proposal-and-rumour"]
    spaniards["object_candidate_id"] = "cand-11625"
    spaniards["predicate"] = "evidently_did_not_welcome_nickel_proposal"
    spaniards["qualifiers"]["claim"] = "Haskell says the Spaniards evidently did not welcome Nickel's proposal."
    spaniards["qualifiers"]["speaker"] = "Haskell reporting an unspecified Spanish collective"
    spaniards["qualifiers"]["text_layer"] = "authorial narrative"
    spaniards["qualifiers"]["qualification"] = "Preserve 'evidently'; the collective's members and decision-making role are not identified. The rumour is recorded separately."

    oliva = row_by_suffix["oliva-preferred-high-altar-monument"]
    oliva["predicate"] = "planned_ignatius_monument_under_high_altar_not_in_transept"
    oliva["qualifiers"]["claim"] = "Haskell says Oliva wanted Ignatius's monument under the Gesù High Altar as a feature of the tribune, not in the transept."
    oliva["qualifiers"]["qualification"] = "The scan reads 'not in the transept'; S0 OCR reads 'hot'. This was a plan, not an executed location. Borgognone's proposed decoration is a separate claim."
    oliva["qualifiers"]["mentioned_candidate_ids"] = ["cand-4999", "cand-5000"]

    urn = row_by_suffix["urn-offered-and-new-altar-built"]
    urn["predicate"] = "jesuits_were_offered_algardi_urn_for_ignatius_remains"
    urn["qualifiers"]["claim"] = "Haskell says that fifteen years after the remains were moved, the Jesuits were offered an urn modelled by Algardi for Ignatius's bones."
    urn["qualifiers"]["qualification"] = "Preserve the relative date; the actor who offered the urn and its present location are not stated. The new Cortona altar is recorded separately."
    urn["qualifiers"]["mentioned_candidate_ids"] = ["cand-0034", "cand-5220"]

    row_by_suffix["chapel-conceived-for-founder"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-1309"]
    row_by_suffix["gonzalez-resumed-undertaking"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-5236"]
    row_by_suffix["memorandum-cites-other-founders"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-5415"]
    row_by_suffix["memorandum-argued-ignatius-deserved-memorial"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-1309"]
    row_by_suffix["further-works-continued"]["subject_candidate_id"] = None
    row_by_suffix["further-works-continued"]["object_candidate_id"] = None
    row_by_suffix["further-works-continued"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-3403", "cand-5414"]

    candidate_by_id.update({row["candidate_id"]: row for row in NEW_CANDIDATES})
    candidate_rows.extend(NEW_CANDIDATES)
    candidate_by_id["cand-11624"]["canonical_name"] = "Uncompleted Della Porta altar for the Chapel of St Ignatius in the Gesù"

    # Existing page references show the two altar mentions are distinct. The segment text includes the 10-character page marker.
    segment_text = source_lines[151] + "\n" + "\n".join(source_lines[152:163])
    if segment_text[913:918] != "altar" or segment_text[1471:1476] != "altar":
        raise SystemExit("p.91 altar mention offsets do not match the page-marker-prefixed segment")
    new_mentions = []
    for mention_id, surface, note in [
        ("m-chp3-seciv-l152-163-0070", "this idea", "Deictic reference to Padre Nickel's proposal event cand-11625."),
        ("m-chp3-seciv-l152-163-0071", "the matter", "Refers to Nickel's proposal event cand-11625; the source does not identify who dropped it."),
    ]:
        start = segment_text.find(surface)
        if start < 0 or segment_text.find(surface, start + 1) >= 0:
            raise SystemExit(f"expected one exact span for {surface!r}")
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-11625",
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(start + len(surface)),
            "note": note,
        })
    mention_rows.extend(new_mentions)

    new_rows = [
        make_statement(
            "chapel-reverted-unofficially-to-jesuits", "cand-5236", "cand-3403",
            "unofficially_reverted_to_jesuits",
            exact_quote(source_lines, 156, 156, "and it thus reverted unofficially into the hands of the Jesuits"),
            156, 156,
            "Haskell says the chapel unofficially reverted into the hands of the Jesuits after its Savelli heirs ceased taking an interest.",
            "Preserve 'unofficially'; this does not establish a formal transfer or exact date.",
            True,
            "The source explicitly links the chapel's unofficial reversion to the Jesuits; the preceding lack of interest is recorded separately.",
        ),
        make_statement(
            "della-porta-designed-uncompleted-altar", "cand-1976", "cand-11624",
            "designed_altar_for_left_transept_chapel",
            exact_quote(source_lines, 156, 156, "the altar had been designed but never completed by Giacomo della Porta"),
            156, 156,
            "Haskell says Giacomo della Porta designed the earlier altar for the chapel.",
            "The designed altar was never completed; its status is recorded separately from the designer relationship.",
            True,
            "The passage explicitly identifies Della Porta as designer of the earlier altar.",
        ),
        make_statement(
            "della-porta-altar-never-completed", "cand-11624", None,
            "was_never_completed",
            exact_quote(source_lines, 156, 156, "the altar had been designed but never completed"),
            156, 156,
            "Haskell says the Della Porta altar was never completed.",
            "This is the state of the earlier altar, not the later Cortona altar which replaced it.",
            False,
            "One-work completion status; no second entity endpoint is required.",
        ),
        make_statement(
            "van-dyck-painted-canonisation-picture", "cand-0960", "cand-5400",
            "painted_picture_for_1622_canonisation_occasion",
            exact_quote(source_lines, 156, 156, "the picture painted for the occasion by Van Dyck"),
            156, 156,
            "Haskell identifies Van Dyck as the painter of the picture associated with Ignatius's canonisation.",
            "The picture's title, version, and present location are not supplied; the artist candidate remains separate from cand-8909 pending S3.",
            True,
            "The source explicitly names Van Dyck as painter; artist identity alignment is deferred to S3.",
            speaker="Haskell",
            text_layer="authorial narrative",
        ),
        make_statement(
            "jesuits-placed-canonisation-picture-above-remains", "cand-3403", "cand-5400",
            "placed_picture_above_ignatius_remains_in_chapel",
            exact_quote(source_lines, 156, 156, "above them placed the picture painted for the occasion by Van Dyck"),
            156, 156,
            "Haskell says the Jesuits placed Van Dyck's canonisation picture above Ignatius's remains in the chapel.",
            "The antecedent of 'them' is Ignatius's physical remains; the painting's identity is source-bounded.",
            True,
            "The text attributes placement of the identified picture to the Jesuits and locates it above the remains.",
            mentioned_candidate_ids=["cand-5220"],
        ),
        make_statement(
            "jesuits-planned-college-at-birthplace", "cand-3403", "cand-5410",
            "planned_to_build_college_at_ignatius_birthplace",
            exact_quote(source_lines, 159, 159, "who thereupon planned to build a college in Ignatius’ birthplace in the province of Vizcaya"),
            159, 159,
            "Haskell says the Jesuits in Peru planned to build a college at Ignatius's birthplace after receiving the legacy.",
            "Planning is not evidence the college was built; the passage names no town or formal college name.",
            True,
            "The source explicitly attributes the college plan to the Jesuits; planned institution and birthplace are separately mapped.",
            mentioned_candidate_ids=["cand-1309", "cand-5279"],
        ),
        make_statement(
            "planned-college-site-is-ignatius-birthplace", "cand-5410", "cand-5411",
            "planned_site_at_ignatius_birthplace",
            exact_quote(source_lines, 159, 159, "a college in Ignatius’ birthplace in the province of Vizcaya"),
            159, 159,
            "Haskell locates the planned college at Ignatius's birthplace in Vizcaya.",
            "This is a proposed site only; the town and evidence of construction are absent.",
            True,
            "The source directly links the planned college to the named birthplace; Vizcaya remains its locator.",
            mentioned_candidate_ids=["cand-1309", "cand-5412"],
        ),
        make_statement(
            "spaniards-spread-rumour-about-nickel", "cand-5413", "cand-1740",
            "spread_rumour_that_nickel_wanted_legacy_for_private_use",
            exact_quote(source_lines, 160, 160, "and soon began to spread rumours that the General wanted the money ‘for his own private use’"),
            160, 160,
            "Haskell says the unspecified Spaniards spread a rumour that Nickel wanted the money for his private use.",
            "This is a reported rumour, not a factual finding about Nickel; the speakers and group membership are not identified.",
            True,
            "The passage attributes the spread of a rumour to an unspecified Spanish collective and identifies Nickel as its subject.",
            speaker="Haskell reporting an unspecified Spanish collective",
            text_layer="reported rumour",
        ),
        make_statement(
            "borgognone-was-to-decorate-tribune", "cand-0399", "cand-5000",
            "was_to_lavishly_decorate_tribune",
            exact_quote(source_lines, 162, 162, "which was to be lavishly decorated by Giacomo Borgognone"),
            161, 162,
            "Haskell says the Gesu tribune was to be lavishly decorated by Giacomo Borgognone.",
            "This records the planned decoration, not an executed commission; the scan and OCR agree on the name's printed form, but the Jacques Courtois identity question remains for S3.",
            True,
            "The source explicitly names Borgognone as the planned decorator of the tribune.",
        ),
        make_statement(
            "algardi-modelled-ignatius-urn", "cand-0034", "cand-5401",
            "modelled_urn_for_ignatius_remains",
            exact_quote(source_lines, 157, 157, "a superb urn, modelled by Algardi"),
            157, 157,
            "Haskell says Algardi modelled the urn offered to the Jesuits for Ignatius's remains.",
            "This is the source's attribution; the urn's version and present location are not supplied.",
            True,
            "The passage explicitly identifies Algardi as the modeler of the specific urn.",
        ),
        make_statement(
            "urn-intended-to-hold-ignatius-remains", "cand-5401", "cand-5220",
            "intended_to_hold_ignatius_bones",
            exact_quote(source_lines, 157, 157, "in which to place the saint’s bones"),
            157, 157,
            "Haskell says the urn was intended to hold Ignatius's bones.",
            "This records intended use, not the urn's actual use or current contents.",
            True,
            "The text explicitly links the urn to the saint's bones as its intended contents.",
        ),
        make_statement(
            "cortona-built-replacement-altar", "cand-0345", "cand-5246",
            "built_new_left_transept_altar",
            exact_quote(source_lines, 157, 157, "at the same time Pietro da Cortona built a new altar"),
            157, 157,
            "Haskell says Pietro da Cortona built the new altar in the chapel at the time the urn was offered.",
            "The new altar replaced Della Porta's uncompleted predecessor; no exact calendar year is asserted here.",
            True,
            "The source explicitly identifies Cortona as builder of the replacement altar.",
        ),
        make_statement(
            "cortona-altar-replaced-della-porta-altar", "cand-5246", "cand-11624",
            "replaced_della_porta_uncompleted_predecessor",
            exact_quote(source_lines, 157, 158, "built a new altar to\n' replace della Porta’s uncompleted one"),
            157, 158,
            "Haskell says Cortona's new altar replaced Della Porta's uncompleted predecessor.",
            "The OCR has a stray opening quote at the beginning of L158; preserve S0 and use the printed page to read the line as a continuation.",
            True,
            "The source explicitly states that the new Cortona altar replaced the earlier Della Porta altar.",
        ),
    ]

    if len(new_rows) != 13:
        raise SystemExit(f"expected 13 new atomic statements, got {len(new_rows)}")
    new_ids = {row["statement_id"] for row in new_rows}
    if len(new_ids) != len(new_rows) or new_ids & all_statement_ids:
        raise SystemExit("new statement IDs collide or are not unique")
    statement_rows.extend(new_rows)

    for mention in new_mentions:
        start = int(mention["start_char"])
        end = int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"invalid mention span: {mention['mention_id']}")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    if len(candidate_by_id) != len(candidate_rows):
        raise SystemExit("duplicate candidate IDs after candidate insertion")
    for row in statement_rows:
        if row.get("segment_id") != SEGMENT_ID:
            continue
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if endpoint and endpoint not in candidate_by_id:
                raise SystemExit(f"missing endpoint {endpoint} in {row['statement_id']}")
        for mentioned in (row.get("qualifiers") or {}).get("mentioned_candidate_ids", []):
            if mentioned not in candidate_by_id:
                raise SystemExit(f"missing mentioned candidate {mentioned} in {row['statement_id']}")

    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    if len(mention_by_id) != len(mention_rows):
        raise SystemExit("duplicate mention IDs after mention insertion")
    for mention_id in ["m-chp3-seciv-l152-163-0015", "m-chp3-seciv-l152-163-0016", *sorted(new_mention_ids)]:
        mention = mention_by_id[mention_id]
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"] or mention["candidate_id"] not in candidate_by_id:
            raise SystemExit(f"invalid p.91 mention span or endpoint: {mention_id}")

    segment_after = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
    classified = [row for row in segment_after if (row.get("qualifiers") or {}).get("relation_candidate") in (True, False)]
    if len(segment_after) != 37 or len(classified) != 37:
        raise SystemExit(f"unexpected segment statement/classification count: {len(segment_after)}/{len(classified)}")
    segment_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in segment_after)
    segment_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in segment_after)
    if (segment_relations, segment_nonrelations) != (31, 6):
        raise SystemExit(f"unexpected p.91 classification totals: {segment_relations}/{segment_nonrelations}")

    coverage[0]["note"] += (
        " Printed p.91 scan checked against S0: 'not in the transept' corrects OCR 'hot', and 'Noyelle' corrects OCR spacing; "
        "S0 remains unchanged. Classified 24 existing statements, atomized compound claims into 37 statements, "
        "separated Della Porta's uncompleted altar from Cortona's later altar, and preserved the 1622 remains/picture distinction."
    )

    bilateral = [row for row in statement_rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    bilateral_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    bilateral_nonrelations = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    bilateral_unclassified = len(bilateral) - bilateral_relations - bilateral_nonrelations
    total_relations = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statement_rows)
    open_relations = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in statement_rows
    )
    if (len(statement_rows), len(candidate_rows), len(mention_rows)) != (12841, 11603, 27538):
        raise SystemExit("unexpected post-write global row counts")
    if (len(bilateral), bilateral_relations, bilateral_nonrelations, bilateral_unclassified, total_relations, open_relations) != (8628, 5197, 490, 2941, 5249, 52):
        raise SystemExit("unexpected post-write global relation-classification totals")

    prepared = {
        STATEMENTS: encode_jsonl_preserving_unchanged(statement_rows, statement_raw),
        CANDIDATES: encode_csv(candidate_fields, candidate_rows, candidate_eol, candidate_bom),
        MENTIONS: encode_csv(mention_fields, mention_rows, mention_eol, mention_bom),
        COVERAGE: encode_csv(coverage_fields, coverage_rows, coverage_eol, coverage_bom),
    }
    print("source and normalized p.91 segment hashes match the reviewed passage")
    print("classified all 24 existing p.91 statements; split compound claims and added 13 atomic statements")
    print("added two source-bounded candidates and two exact mentions; corrected the old/new altar mapping and Van Dyck candidate type")
    print(f"p.91 statements={len(segment_after)} relation_candidates={segment_relations} nonrelations={segment_nonrelations}")
    print(f"post totals: statements={len(statement_rows)} candidates={len(candidate_rows)} mentions={len(mention_rows)}")
    print(f"bilateral statements={len(bilateral)} relation={bilateral_relations} nonrelation={bilateral_nonrelations} unclassified={bilateral_unclassified}")
    print(f"relation candidates total={total_relations} open endpoints={open_relations}")
    print("unchanged JSONL rows and table formatting are preserved")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return

    prepared_paths = list(prepared)
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in prepared_paths}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("a recovery copy already exists; refusing to overwrite")
    temp_paths = {path: path.with_name(path.name + ".tmp-write") for path in prepared_paths}
    if any(path.exists() for path in temp_paths.values()):
        raise SystemExit("a temporary output exists; inspect it before applying")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in prepared.items():
            temp_paths[path].write_bytes(data)
        for path in prepared_paths:
            os.replace(temp_paths[path], path)
        for path, data in prepared.items():
            if path.read_bytes() != data:
                raise SystemExit(f"post-write verification failed: {path.name}")
    except Exception:
        for path, backup in backups.items():
            shutil.copy2(backup, path)
        for temp in temp_paths.values():
            if temp.exists():
                temp.unlink()
        raise
    for path, data in prepared.items():
        print(f"post_sha256 {path.name} {sha(data)}")
    for backup in backups.values():
        print(f"recovery_copy {backup.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
