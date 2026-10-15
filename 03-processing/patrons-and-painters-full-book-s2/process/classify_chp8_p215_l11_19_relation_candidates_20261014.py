"""Review p.215 S2 claims, split compound relationships, and correct the campanile type."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p215_review.png"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l11-19"
SEGMENT_SHA = "131cfa5f062c6baf0c97e31844b950a27f45817e5442687f1935a2e38b153a00"
BACKUP_SUFFIX = ".bak-s2-chp8-p215-l11-19-relation-review-20261014"
EXPECTED_HASHES = {
    STATEMENTS: "9d76ef56545130280e20134b9144d30daa57e181272b0c3d63434bc6e0d214b0",
    CANDIDATES: "89dc99de57441ce001923caf56381e433fd80ee7477812e688cfaf091f5d609e",
    MENTIONS: "6801ec1660540dd45f045a7b243fc4fc1d012c2eb0b134cf14a99578641a1415",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
    PAGE_IMAGE: "ab9b94393a72c3e98fc80fd921332b90ecd4d0de84f5b8f99906e466d11f9952",
}

TRUE_NOTES = {
    "st-chp8-p215-1653-decoration-programme":
        "This is a dated institutional decision with a stated purpose and a specific church space; Haskell reports the event, and the committee's quoted wording remains part of the linked statement.",
    "st-chp8-p215-cavagna-dome-frescoes-1614":
        "This records a dated completion of a single dome-decoration group by Cavagna with two unnamed local assistants; no identities are inferred for the assistants.",
    "st-chp8-p215-church-work-began-1137":
        "This records the reported start and long, intermittent course of work on an identified church; no separate construction event entity is asserted in this row.",
    "st-chp8-p215-classicising-institutions-outside-rome":
        "Haskell links classicising institutions and doctrines with constraints on painters in Rome, and contrasts their absence in out-of-the-way cities with the growth of different canons; preserve this attributed synthesis without inventing a named institution.",
    "st-chp8-p215-committee-orders-oil-paintings":
        "This records the appointment of a committee to order oil paintings for the 1653 programme, with the decision standard preserved from the quotation.",
    "st-chp8-p215-local-capacity-and-foreign-commission":
        "This preserves Haskell's assessment that local capacity was insufficient and a foreign commission would be needed; it does not claim that a foreign artist was actually commissioned.",
    "st-chp8-p215-negotiations-follow-relative-failure":
        "The source links the committee's relative failure with subsequent negotiations across Italian towns; the towns and negotiation participants are not individually identified.",
    "st-chp8-p215-one-collection-influential":
        "Haskell says at least one of the collections was highly influential; the particular collection is not identified at this point in the text.",
    "st-chp8-p215-patronage-mechanism-and-roman-values":
        "This is Haskell's interpretive claim linking the collections' development to an unusual patronage mechanism and the demolition of Roman values; retain it as an attributed conceptual relation.",
    "st-chp8-p215-provincial-collections-neglect-roman-painting":
        "Haskell identifies neglect of Roman painting as a defining relation in the provincial-collection account; the source does not name each collection in this summary.",
}
FALSE_NOTES = {
    "st-chp8-p215-bergamo-venice-milan-context":
        "The compound source sentence combines Venice's rule of Bergamo, Bergamo's distance from Milan, and artistic-cultural reflections involving two cities. Keep the source wording here and use the four atomic relation rows added below.",
    "st-chp8-p215-campione-portico-and-south-entrance":
        "The source sentence describes two distinct architectural works and construction dates. The portico and south entrance are represented in separate relation rows below.",
    "st-chp8-p215-collections-estimated-frequency":
        "This is Haskell's qualified estimate of how many collections existed and a caveat about incomplete recording, not a discrete entity relation.",
    "st-chp8-p215-interior-decoration-and-ricchini-dome":
        "This statement combines church-wide changes, surviving frescoes, altar paintings, dome stucco, and Ricchini's dome plan. Its former endpoints did not represent the full compound; preserve the quote and use the separate rows below.",
    "st-chp8-p215-interior-mid-century-spectacle":
        "This is Haskell's attributed visual assessment of the church interior, not a discrete relation candidate between identified entities.",
    "st-chp8-p215-renaissance-campanile-sacristy":
        "This combines separate additions with different dates and object types. The campanile and sacristy are represented in separate relation rows below.",
}

NEW_ROWS = [
    {
        "statement_id": "st-chp8-p215-bergamo-ruled-by-venice-from-1430",
        "subject": "cand-6255", "object": "cand-6208", "predicate": "venice_ruled_bergamo_from_1430",
        "line_start": 19, "line_end": 19,
        "claim": "Haskell says Venice had ruled Bergamo since 1430.",
        "quote": "Bergamo had been ruled by Venice since 1430",
        "qualification": "Venice is mapped to the political entity candidate for this governing action; this is not a claim about the city of Venice as a place.",
        "mentioned": ["cand-6255", "cand-6208"],
        "note": "The sentence states a political relation from the Venetian polity to Bergamo and gives its start year.",
    },
    {
        "statement_id": "st-chp8-p215-bergamo-distance-from-milan",
        "subject": "cand-6208", "object": "cand-3418", "predicate": "bergamo_lies_thirty_miles_from_milan",
        "line_start": 19, "line_end": 19,
        "claim": "Haskell says Bergamo lies thirty miles from Milan.",
        "quote": "it lies only thirty miles from Milan",
        "qualification": "The pronoun 'it' refers to Bergamo in the immediately preceding clause; preserve Haskell's approximate distance wording.",
        "mentioned": ["cand-6208", "cand-3418"],
        "note": "This is the separate geographic-distance claim in the compound source sentence.",
    },
    {
        "statement_id": "st-chp8-p215-bergamo-artistic-culture-reflects-venice",
        "subject": "cand-6208", "object": "cand-2719", "predicate": "bergamo_artistic_culture_reflected_venetian_city_traditions",
        "line_start": 19, "line_end": 19,
        "claim": "Haskell says Bergamo's artistic culture reflected that of Venice, one of the two cities with which it was closely associated.",
        "quote": "Its artistic culture reflected those of the two cities with which it was so closely associated",
        "qualification": "The source groups Venice and Milan in the comparison; this row records only its Venice endpoint and does not assign particular cultural features.",
        "mentioned": ["cand-6208", "cand-2719"],
        "note": "This isolates the Venice side of Haskell's two-city cultural comparison.",
    },
    {
        "statement_id": "st-chp8-p215-bergamo-artistic-culture-reflects-milan",
        "subject": "cand-6208", "object": "cand-3418", "predicate": "bergamo_artistic_culture_reflected_milanese_city_traditions",
        "line_start": 19, "line_end": 19,
        "claim": "Haskell says Bergamo's artistic culture reflected that of Milan, one of the two cities with which it was closely associated.",
        "quote": "Its artistic culture reflected those of the two cities with which it was so closely associated",
        "qualification": "The source groups Milan and Venice in the comparison; this row records only its Milan endpoint and does not assign particular cultural features.",
        "mentioned": ["cand-6208", "cand-3418"],
        "note": "This isolates the Milan side of Haskell's two-city cultural comparison.",
    },
    {
        "statement_id": "st-chp8-p215-campione-erected-gothic-portico-1355",
        "subject": "cand-0494", "object": "cand-7629", "predicate": "erected_gothic_portico_in_1355",
        "line_start": 13, "line_end": 13,
        "claim": "Haskell says Giovanni da Campione erected the Gothic portico of Santa Maria Maggiore in 1355.",
        "quote": "In 1355 Giovanni da Campione erected the delicate but richly ornamented Gothic portico supported on two stone lions which faces the Palazzo della Ragione",
        "qualification": "The two stone supports and facing Palazzo della Ragione remain contextual details; no authorship of the lions is inferred.",
        "mentioned": ["cand-0494", "cand-7629", "cand-7630", "cand-7628", "cand-7627", "cand-6208"],
        "note": "This isolates the dated portico construction from the later south entrance.",
    },
    {
        "statement_id": "st-chp8-p215-campione-built-south-entrance",
        "subject": "cand-0494", "object": "cand-7631", "predicate": "built_south_entrance_a_few_years_after_1355",
        "line_start": 13, "line_end": 13,
        "claim": "Haskell says Giovanni da Campione built the more restrained south entrance a few years after the portico.",
        "quote": "and a few years later he also built the rather more restrained entrance to the south",
        "qualification": "The date remains relative; the source gives no exact year.",
        "mentioned": ["cand-0494", "cand-7631", "cand-7627", "cand-6208"],
        "note": "The antecedent 'he' is Giovanni da Campione; this is a distinct work and later date from the portico.",
    },
    {
        "statement_id": "st-chp8-p215-gothic-fresco-traces-remain",
        "subject": "cand-7627", "object": "cand-7634", "predicate": "church_retained_traces_of_gothic_frescoes",
        "line_start": 14, "line_end": 14,
        "claim": "Haskell says traces of Gothic frescoes remained in Santa Maria Maggiore.",
        "quote": "Traces of Gothic frescoes still remain",
        "qualification": "The source reports traces only; it does not say the original decoration survived intact.",
        "mentioned": ["cand-7627", "cand-7634"],
        "note": "The church and surviving fresco group are separate architectural and artistic objects.",
    },
    {
        "statement_id": "st-chp8-p215-decoration-changed-and-altar-paintings-appeared",
        "subject": "cand-7627", "object": "cand-7635", "predicate": "church_decoration_changed_and_altar_paintings_appeared_from_mid_16c",
        "line_start": 14, "line_end": 14,
        "claim": "Haskell says the church's decoration changed from the mid-sixteenth century, when altar paintings by local and Venetian artists began to appear.",
        "quote": "from the middle of the sixteenth century the whole decoration was changed. Altar paintings by local and Venetian artists began to appear",
        "qualification": "This is the transition described by Haskell; the individual paintings and artists are not identified.",
        "mentioned": ["cand-7627", "cand-7635", "cand-2719", "cand-6208"],
        "note": "This isolates the church decoration transition and its source-described altar-painting group.",
    },
    {
        "statement_id": "st-chp8-p215-stucco-ornament-covers-dome-interior",
        "subject": "cand-7637", "object": "cand-7636", "predicate": "stucco_ornamentation_covered_dome_interior",
        "line_start": 14, "line_end": 14,
        "claim": "Haskell says rich stucco ornamentation covered the interior of the dome at Santa Maria Maggiore.",
        "quote": "rich and heavy stucco ornamentation crept over the interior of the dome",
        "qualification": "The stucco group is distinct from the dome structure and from the later fresco decoration.",
        "mentioned": ["cand-7637", "cand-7636", "cand-7627"],
        "note": "The statement records an architectural-decoration relation with the ornament as subject and dome interior as location.",
    },
    {
        "statement_id": "st-chp8-p215-ricchini-planned-dome-1612",
        "subject": "cand-2146", "object": "cand-7636", "predicate": "planned_dome_in_1612",
        "line_start": 14, "line_end": 15,
        "claim": "Haskell says Francesco Maria Ricchini planned the dome in 1612.",
        "quote": "the dome which was planned by the Milanese architect\nFrancesco Maria Ricchini in 1612",
        "qualification": "Planning is distinct from the stucco covering and later fresco decoration of the dome.",
        "mentioned": ["cand-2146", "cand-7636", "cand-7627"],
        "note": "This extracts the architect-to-dome design relation without merging it with later decoration.",
    },
    {
        "statement_id": "st-chp8-p215-campanile-completed-1425",
        "subject": "cand-7627", "object": "cand-7632", "predicate": "campanile_completed_in_1425",
        "line_start": 13, "line_end": 13,
        "claim": "Haskell says the campanile of Santa Maria Maggiore was completed in 1425.",
        "quote": "In 1425, after nearly three centuries, the campanile was completed",
        "qualification": "The separate architectural component is typed as a work; the surrounding church remains a place.",
        "mentioned": ["cand-7627", "cand-7632", "cand-6208"],
        "note": "The source gives a completion date for the church's campanile.",
    },
    {
        "statement_id": "st-chp8-p215-sacristy-added-late-15c",
        "subject": "cand-7627", "object": "cand-7633", "predicate": "sacristy_added_toward_end_of_15c_obscuring_original_plan",
        "line_start": 13, "line_end": 13,
        "claim": "Haskell says a new Bramantesque sacristy was added toward the end of the fifteenth century and made the original plan harder to appreciate.",
        "quote": "towards the end of the century a sacristy in the new Bramantesque style made it still harder to appreciate the original plan",
        "qualification": "The sacristy is an interior space of the church; the source gives only an approximate late-century date.",
        "mentioned": ["cand-7627", "cand-7633", "cand-3578", "cand-6208"],
        "note": "This separates the sacristy addition from the campanile completion and preserves its spatial character.",
    },
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(fields: list[str], rows: list[dict[str, str]]) -> bytes:
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


def make_statement(row: dict) -> dict:
    q = {
        "source_line_start": row["line_start"], "source_line_end": row["line_end"],
        "printed_page": 215, "pdf_physical_page": 13, "claim": row["claim"],
        "speaker": "Haskell", "text_layer": "body", "qualification": row["qualification"],
        "mentioned_candidate_ids": row["mentioned"], "relation_candidate": True,
        "relation_candidate_note": row["note"],
    }
    return {
        "statement_id": row["statement_id"], "segment_id": SEGMENT_ID,
        "subject_candidate_id": row["subject"], "object_candidate_id": row["object"],
        "predicate": row["predicate"], "qualifiers": q, "original_quote": row["quote"],
        "origin": "book", "source_file": SOURCE_REL,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded dry-run checks pass")
    args = parser.parse_args()
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    if {path: sha(data) for path, data in raw.items()} != EXPECTED_HASHES:
        raise SystemExit("a reviewed table, source, PDF, or page image changed; re-review before applying")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[10:19])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("the p.215 S2 segment changed since review")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or (
        segment.get("source_file"), segment.get("line_start"), segment.get("line_end"),
        segment.get("sha256"), segment.get("asset_sha256"),
    ) != (SOURCE_REL, 11, 19, SEGMENT_SHA, EXPECTED_HASHES[SOURCE]):
        raise SystemExit("the S0 segment manifest does not match the reviewed source")

    statements = read_jsonl(STATEMENTS)
    by_statement = {row["statement_id"]: row for row in statements}
    if len(by_statement) != len(statements):
        raise SystemExit("statement identifiers are not unique")
    page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    unset = {
        row["statement_id"] for row in page_rows
        if "relation_candidate" not in (row.get("qualifiers") or {})
    }
    expected_unset = set(TRUE_NOTES) | set(FALSE_NOTES)
    if len(page_rows) != 16 or unset != expected_unset:
        raise SystemExit(f"unexpected p.215 segment inventory: rows={len(page_rows)}, unset={len(unset)}")
    if any(row["statement_id"] in by_statement for row in NEW_ROWS):
        raise SystemExit("a planned atomic p.215 statement identifier already exists")

    candidate_fields, candidates = read_csv(CANDIDATES)
    by_candidate = {row["candidate_id"]: row for row in candidates}
    if len(by_candidate) != len(candidates):
        raise SystemExit("candidate identifiers are not unique")
    campanile = by_candidate.get("cand-7632")
    if not campanile or campanile.get("suggested_type") != "place":
        raise SystemExit("cand-7632 no longer has the reviewed campanile type prestate")
    for row in NEW_ROWS:
        if row["subject"] and row["subject"] not in by_candidate:
            raise SystemExit(f"new statement has unknown subject candidate {row['subject']}")
        if row["object"] and row["object"] not in by_candidate:
            raise SystemExit(f"new statement has unknown object candidate {row['object']}")
        if row["quote"] not in segment_text:
            raise SystemExit(f"new statement quote is not an exact S0 span: {row['statement_id']}")

    # Keep the original compound quotes, but clear their misleading pairwise endpoints.
    for statement_id, note in FALSE_NOTES.items():
        row = by_statement[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note
        row["qualifiers"] = q
        if statement_id in {
            "st-chp8-p215-bergamo-venice-milan-context",
            "st-chp8-p215-campione-portico-and-south-entrance",
            "st-chp8-p215-interior-decoration-and-ricchini-dome",
        }:
            row["subject_candidate_id"] = None
            row["object_candidate_id"] = None

    for statement_id, note in TRUE_NOTES.items():
        row = by_statement[statement_id]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        row["qualifiers"] = q

    corrections = {
        "st-chp8-p215-classicising-institutions-outside-rome": {
            "source_file": SOURCE_REL, "source_line": 12, "ocr": "growup", "print": "grow up",
            "basis": "CHP-8.pdf physical page 13.",
        },
        "st-chp8-p215-cavagna-dome-frescoes-1614": {
            "source_file": SOURCE_REL, "source_line": 14, "ocr": "Bcrgamasque", "print": "Bergamasque",
            "basis": "CHP-8.pdf physical page 13.",
        },
    }
    for statement_id, correction in corrections.items():
        q = dict(by_statement[statement_id].get("qualifiers") or {})
        ocr_corrections = list(q.get("ocr_corrections") or [])
        if correction not in ocr_corrections:
            ocr_corrections.append(correction)
        q["ocr_corrections"] = ocr_corrections
        by_statement[statement_id]["qualifiers"] = q

    campanile["suggested_type"] = "work"
    campanile["detail"] = (
        "The campanile is a separately described architectural component of Santa Maria Maggiore, completed in 1425. "
        "Under the project taxonomy, architectural components are works; the church and sacristy remain places."
    )

    for row in NEW_ROWS:
        statements.append(make_statement(row))
    final_page_rows = [row for row in statements if row.get("segment_id") == SEGMENT_ID]
    counts = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in final_page_rows)
    new_statements = jsonl_bytes(statements)
    new_candidates = csv_bytes(candidate_fields, candidates)
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, CANDIDATES)]
    print("DRY RUN p.215 S2 segment")
    print(f"segment={SEGMENT_ID} original_statements=16 unset_classified=16 added_atomic_statements={len(NEW_ROWS)}")
    print(f"final segment statements={len(final_page_rows)} true={counts[True]} false={counts[False]} unset={counts[None]}")
    print("refinements: 4 compound claims split; campanile candidate cand-7632 corrected from place to work; 2 page-image OCR corrections recorded")
    for path, data in [(STATEMENTS, new_statements), (CANDIDATES, new_candidates)]:
        print(f"{path.relative_to(ROOT)} before={EXPECTED_HASHES[path]} after={sha(data)}")
    if not args.apply:
        print("No files written. Use --apply to write after reviewing this summary.")
        return
    if any(path.exists() for path in backups):
        raise SystemExit("a recovery backup already exists")
    for path, backup in zip((STATEMENTS, CANDIDATES), backups, strict=True):
        shutil.copy2(path, backup)
    atomic_write(STATEMENTS, new_statements)
    atomic_write(CANDIDATES, new_candidates)
    print("APPLIED; recovery copies:")
    for backup in backups:
        print(f"  {backup.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
