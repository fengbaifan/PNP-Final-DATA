from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p60-note7-citations-20261010"

STATEMENTS_SHA = "f1947acaa6610e3a9a3d37be4b6556a95a208e82d5d84b9c7a81c6eefd2f04dd"
MENTIONS_SHA = "ad57d10340723ec589285d0ad37a1ea0e5963a96360896febbe6e07abf5e31a9"
CANDIDATES_SHA = "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de"
SOURCE_SHA = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"

SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l38-54"
BODY_IDS = [
    "st-chp2-secvii-l21-30-baldi-ferri-tapestry-design-commission",
    "st-chp2-secvii-l21-30-tapestry-set-urban-subject",
]
STATUS_ID = "st-chp2-secvii-l38-54-fn-p60-7a-tapestry-and-cartoon-status"
ATTRIBUTION_ID = "st-chp2-secvii-l38-54-fn-p60-7b-ferri-attribution-suggested"
PLAN_ID = "st-chp2-secvii-l38-54-fn-p60-7c-earlier-salone-fresco-plan"
LOCATION_ID = "st-chp2-secvii-l38-54-fn-p60-7a-tapestry-cartoon-location"
CAVALLO_CITE_ID = "st-chp2-secvii-l38-54-fn-p60-7a-cavallo-citation"
CALBERG_CITE_ID = "st-chp2-secvii-l38-54-fn-p60-7a-calberg-citation"
BLUNT_CITE_ID = "st-chp2-secvii-l38-54-fn-p60-7b-blunt-cooke-citation"
PASTOR_CITE_ID = "st-chp2-secvii-l38-54-fn-p60-7c-pastor-citation"
NEW_IDS = [LOCATION_ID, CAVALLO_CITE_ID, CALBERG_CITE_ID, BLUNT_CITE_ID, PASTOR_CITE_ID]
OLD_IDS = [STATUS_ID, ATTRIBUTION_ID, PLAN_ID]

BOOK = "cand-2962"
TAPESTRY_SET = "cand-4935"
CARTOONS = "cand-4936"
PALAZZO = "cand-4957"
CAVALLO = "cand-4958"
CALBERG = "cand-4959"
BLUNT_COOKE = "cand-4960"
FERRI = "cand-1027"
FRESCO_PLAN = "cand-4961"
SALONE = "cand-3556"
PASTOR_XIII = "cand-4237"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_statements():
    raw = STATEMENTS.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line.decode("utf-8-sig")) for line in lines if line.strip()]
    return rows, lines, bom


def counts(rows: list[dict]) -> dict:
    marked = [s for s in rows if (s.get("qualifiers") or {}).get("relation_candidate") is True]
    complete = sum(bool(s.get("subject_candidate_id") and s.get("object_candidate_id")) for s in marked)
    dual_unclassified = sum(
        bool(s.get("subject_candidate_id") and s.get("object_candidate_id"))
        and (s.get("qualifiers") or {}).get("relation_candidate") not in (True, False)
        for s in rows
    )
    return {
        "statements": len(rows),
        "relations": len(marked),
        "complete_relations": complete,
        "open_relations": len(marked) - complete,
        "dual_unclassified": dual_unclassified,
        "footnote_claims": sum(s.get("predicate") == "footnote-claim" for s in rows),
        "cites": sum(
            s.get("predicate") == "cites"
            and (s.get("qualifiers") or {}).get("relation_candidate") is True
            for s in rows
        ),
    }


def preflight():
    for path, expected in (
        (STATEMENTS, STATEMENTS_SHA),
        (MENTIONS, MENTIONS_SHA),
        (CANDIDATES, CANDIDATES_SHA),
        (SOURCE, SOURCE_SHA),
    ):
        require(sha(path) == expected, f"unexpected SHA-256 for {path.relative_to(ROOT)}")

    statements, statement_lines, statement_bom = read_statements()
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mentions = list(csv.DictReader(f))
    by_id = {s["statement_id"]: s for s in statements}
    require(len(by_id) == len(statements), "duplicate statement_id")
    for statement_id in OLD_IDS + BODY_IDS:
        require(statement_id in by_id, f"missing statement {statement_id}")
    for statement_id in NEW_IDS:
        require(statement_id not in by_id, f"new statement ID already exists: {statement_id}")

    quote = by_id[STATUS_ID]["original_quote"]
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    require(source_lines[49] == quote, "source line 50 and note 7 statement quote differ")
    require("Blunt and Cooke, i960, p. 36" in quote, "expected OCR year form changed")
    require("Pastor, XIII, p. 969" in quote, "expected Pastor locator changed")

    for statement_id in OLD_IDS:
        s = by_id[statement_id]
        q = s.get("qualifiers", {})
        require(s["segment_id"] == SEGMENT_ID and s["source_file"] == "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
                f"source anchor changed: {statement_id}")
        require(s["predicate"] == "footnote-claim" and s["original_quote"] == quote,
                f"statement source changed: {statement_id}")
        require(q.get("source_line_start") == 50 and q.get("source_line_end") == 50
                and q.get("print_page") == 60 and q.get("pdf_physical_page") == 49
                and q.get("footnote_marker") == 7, f"statement locator changed: {statement_id}")

    candidate_by_id = {c["candidate_id"]: c for c in candidates}
    expected_kinds = {
        BOOK: "archive",
        TAPESTRY_SET: "work",
        CARTOONS: "work",
        PALAZZO: "place",
        CAVALLO: "archive",
        CALBERG: "archive",
        BLUNT_COOKE: "archive",
        FERRI: "person",
        FRESCO_PLAN: "work",
        SALONE: "place",
        PASTOR_XIII: "archive",
    }
    for candidate_id, kind in expected_kinds.items():
        c = candidate_by_id.get(candidate_id)
        require(c is not None and c["suggested_type"] == kind and c["status"] == "open",
                f"candidate {candidate_id} changed")

    segment = "\n".join(source_lines[37:54])
    mention_by_id = {m["mention_id"]: m for m in mentions}
    expected_mentions = {
        "m-chp2-secvii-l38-54-0035": (TAPESTRY_SET, "The tapestries", 1082, 1096),
        "m-chp2-secvii-l38-54-0036": (CARTOONS, "the cartoons", 1116, 1128),
        "m-chp2-secvii-l38-54-0037": (PALAZZO, "the Palazzo Barberini", 1136, 1157),
        "m-chp2-secvii-l38-54-0038": (CAVALLO, "Adolf S. Cavallo", 1181, 1197),
        "m-chp2-secvii-l38-54-0039": (CALBERG, "M. Calberg", 1205, 1215),
        "m-chp2-secvii-l38-54-0040": (BLUNT_COOKE, "Blunt and Cooke", 1227, 1242),
        "m-chp2-secvii-l38-54-0041": (FERRI, "Ciro Ferri", 1269, 1279),
        "m-chp2-secvii-l38-54-0042": (SALONE, "the Salone", 1347, 1357),
        "m-chp2-secvii-l38-54-0043": (FRESCO_PLAN, "frescoes representing rather similar subjects", 1363, 1408),
        "m-chp2-secvii-l38-54-0044": (PASTOR_XIII, "Pastor, XIII", 1409, 1421),
    }
    for mention_id, (candidate_id, surface, start, end) in expected_mentions.items():
        m = mention_by_id.get(mention_id)
        require(m is not None and m["segment_id"] == SEGMENT_ID and m["candidate_id"] == candidate_id
                and m["surface_form"] == surface and m["start_char"] == str(start) and m["end_char"] == str(end)
                and segment[start:end] == surface, f"mention anchor changed: {mention_id}")

    for body_id in BODY_IDS:
        refs = by_id[body_id].get("qualifiers", {}).get("footnote_refs", [])
        ref = next((r for r in refs if isinstance(r, dict) and r.get("marker") == 7
                    and r.get("segment_id") == SEGMENT_ID and r.get("source_line") == 50), None)
        require(ref is not None and ref.get("statement_ids") == OLD_IDS,
                f"body marker 7 references changed: {body_id}")

    for cited_candidate in (CAVALLO, CALBERG, BLUNT_COOKE):
        require(not any(s["predicate"] == "cites" and s.get("object_candidate_id") == cited_candidate
                        and (s.get("qualifiers") or {}).get("footnote_marker") == 7 for s in statements),
                f"duplicate note 7 citation already exists for {cited_candidate}")
    require(not any(s["predicate"] == "cites" and s.get("object_candidate_id") == PASTOR_XIII
                    and (s.get("qualifiers") or {}).get("footnote_marker") == 7
                    and (s.get("qualifiers") or {}).get("page") == 969 for s in statements),
            "duplicate note 7 Pastor citation already exists")

    before = counts(statements)
    expected_before = {
        "statements": 12671, "relations": 3646, "complete_relations": 3632,
        "open_relations": 14, "dual_unclassified": 4432, "footnote_claims": 7, "cites": 110,
    }
    require(before == expected_before, f"current ledger counts differ: {before}")
    return statements, statement_lines, statement_bom, mentions, candidates, quote


def make_citation(statement_id: str, target: str, quote: str, claim: str, context_ids: list[str],
                  related_statement_ids: list[str], year: int | None, page: int | None = None,
                  volume: str | None = None, print_correction: str | None = None) -> dict:
    q = {
        "source_line_start": 50,
        "source_line_end": 50,
        "claim": claim,
        "speaker": "Haskell, authorial footnote",
        "text_layer": "bibliographic citation",
        "qualification": "This records the citation in the book only; the cited publication was not independently consulted.",
        "footnote_marker": 7,
        "print_page": 60,
        "pdf_physical_page": 49,
        "citation_publication_candidate_id": target,
        "citation_context_candidate_ids": context_ids,
        "related_statement_ids": related_statement_ids,
        "relation_candidate": True,
        "relation_candidate_note": "S2 bibliographic pointer only; it does not verify the cited historical claim and is not a formal S6 edge.",
    }
    if year is not None:
        q["year"] = year
    if page is not None:
        q["page"] = page
    if volume is not None:
        q["volume"] = volume
    if print_correction is not None:
        q["print_ocr_correction"] = print_correction
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": BOOK,
        "object_candidate_id": target,
        "predicate": "cites",
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
    }


def make_changes(statements: list[dict], quote: str) -> list[dict]:
    rows = copy.deepcopy(statements)
    by_id = {s["statement_id"]: s for s in rows}
    status, attribution, plan = (by_id[x] for x in OLD_IDS)
    bodies = [by_id[x] for x in BODY_IDS]

    status["object_candidate_id"] = None
    status["predicate"] = "reported_dispersed_by_book_publication"
    status["qualifiers"] = {
        "source_line_start": 50,
        "source_line_end": 50,
        "claim": "Haskell reports that the twelve-tapestry set was dispersed by the time of the book's publication.",
        "speaker": "Haskell",
        "text_layer": "authorial footnote status report",
        "print_page": 60,
        "pdf_physical_page": 49,
        "footnote_marker": 7,
        "qualification": "The note's 'now' is relative to Haskell's 1962 publication; it does not establish present-day locations for individual tapestries.",
        "relation_candidate": False,
        "related_body_statement_ids": BODY_IDS,
    }

    location = {
        "statement_id": LOCATION_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": CARTOONS,
        "object_candidate_id": PALAZZO,
        "predicate": "book_note_reports_work_location_at_publication",
        "qualifiers": {
            "source_line_start": 50,
            "source_line_end": 50,
            "claim": "Haskell's note reports that the cartoons were in Palazzo Barberini at the time of publication.",
            "speaker": "Haskell",
            "text_layer": "authorial footnote location report",
            "print_page": 60,
            "pdf_physical_page": 49,
            "footnote_marker": 7,
            "qualification": "This is a publication-time location report only; present custody is not established.",
            "relation_candidate": True,
            "relation_candidate_note": "Source-qualified location candidate, not a verified present location or formal S6 relation.",
            "related_body_statement_ids": BODY_IDS,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
    }

    attribution["subject_candidate_id"] = None
    attribution["object_candidate_id"] = FERRI
    attribution["predicate"] = "attributed_to"
    attribution["qualifiers"] = {
        "source_line_start": 50,
        "source_line_end": 50,
        "claim": "Haskell reports that Blunt and Cooke suggest Ciro Ferri as the artist, but the note does not resolve whether the attribution concerns the tapestry set or its cartoons/designs.",
        "speaker": "Blunt and Cooke, as cited by Haskell",
        "text_layer": "tentative attribution reported in authorial footnote",
        "print_page": 60,
        "pdf_physical_page": 49,
        "footnote_marker": 7,
        "qualification": "The attribution is tentative and transmitted through Haskell. Keep the work endpoint open between the tapestry set and preparatory cartoons; no authorship is confirmed.",
        "possible_subject_candidate_ids": [TAPESTRY_SET, CARTOONS],
        "citation_statement_id": BLUNT_CITE_ID,
        "attribution_status": "suggested",
        "relation_candidate": True,
        "relation_candidate_note": "The artist is named, but the work scope is ambiguous in the note; preserve as an open S2 candidate, not a formal S6 edge.",
        "related_body_statement_ids": BODY_IDS,
    }

    plan["subject_candidate_id"] = FRESCO_PLAN
    plan["object_candidate_id"] = SALONE
    plan["predicate"] = "planned_decoration_for"
    plan["qualifiers"] = {
        "source_line_start": 50,
        "source_line_end": 50,
        "claim": "Haskell notes an earlier plan to cover the Salone walls with frescoes on subjects rather similar to those of the tapestry set.",
        "speaker": "Haskell",
        "text_layer": "authorial footnote about a prior plan",
        "print_page": 60,
        "pdf_physical_page": 49,
        "footnote_marker": 7,
        "qualification": "The note reports a plan only and does not say the frescoes were executed.",
        "similar_subjects_work_candidate_id": TAPESTRY_SET,
        "citation_statement_id": PASTOR_CITE_ID,
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly identifies a planned decoration for this space; it is an S2 candidate only.",
        "related_body_statement_ids": BODY_IDS,
    }

    citation_rows = [
        make_citation(
            CAVALLO_CITE_ID, CAVALLO, quote,
            "Haskell cites Adolf S. Cavallo (1957) for the history of the Barberini tapestry set.",
            [TAPESTRY_SET], [STATUS_ID], 1957,
        ),
        make_citation(
            CALBERG_CITE_ID, CALBERG, quote,
            "Haskell cites M. Calberg (1959) for the history of the Barberini tapestry set.",
            [TAPESTRY_SET], [STATUS_ID], 1959,
        ),
        make_citation(
            BLUNT_CITE_ID, BLUNT_COOKE, quote,
            "Haskell cites Blunt and Cooke (1960), p. 36, for tapestry history and their suggested Ciro Ferri attribution.",
            [TAPESTRY_SET, CARTOONS], [STATUS_ID, ATTRIBUTION_ID], 1960, page=36,
            print_correction="The S0 OCR reads 'i960'; print p.60 reads '1960'.",
        ),
        make_citation(
            PASTOR_CITE_ID, PASTOR_XIII, quote,
            "Haskell cites Pastor, volume XIII, p. 969, for the earlier Salone fresco plan.",
            [FRESCO_PLAN, SALONE], [PLAN_ID], None, page=969, volume="XIII",
        ),
    ]
    pastor_citation = next(s for s in citation_rows if s["statement_id"] == PASTOR_CITE_ID)
    pastor_citation["qualifiers"]["possible_version_candidate_id"] = "cand-11414"
    pastor_citation["qualifiers"]["version_qualification"] = (
        "The book bibliography identifies a 1943 Italian edition of the Pastor series but gives no volume; "
        "do not assign that year to this volume XIII citation."
    )

    old_refs = OLD_IDS
    new_refs = [STATUS_ID, LOCATION_ID, CAVALLO_CITE_ID, CALBERG_CITE_ID,
                BLUNT_CITE_ID, ATTRIBUTION_ID, PLAN_ID, PASTOR_CITE_ID]
    for body in bodies:
        ref = next(r for r in body["qualifiers"]["footnote_refs"]
                   if isinstance(r, dict) and r.get("marker") == 7
                   and r.get("segment_id") == SEGMENT_ID and r.get("source_line") == 50)
        require(ref.get("statement_ids") == old_refs, "body note 7 references changed during edit")
        ref["statement_ids"] = new_refs

    cite_by_id = {s["statement_id"]: s for s in citation_rows}
    output = []
    for row in rows:
        output.append(row)
        sid = row["statement_id"]
        if sid == STATUS_ID:
            output.extend([location, cite_by_id[CAVALLO_CITE_ID], cite_by_id[CALBERG_CITE_ID]])
        elif sid == ATTRIBUTION_ID:
            output.append(cite_by_id[BLUNT_CITE_ID])
        elif sid == PLAN_ID:
            output.append(cite_by_id[PASTOR_CITE_ID])
    return output


def serialize_statements(rows: list[dict], original_lines: list[bytes], bom: bool) -> bytes:
    newline = b"\r\n" if any(line.endswith(b"\r\n") for line in original_lines) else b"\n"
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    return b"".join(output)


def write_atomic(path: Path, content: bytes) -> Path:
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".tmp-", delete=False) as tmp:
        tmp.write(content)
        return Path(tmp.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the audited statement changes")
    args = parser.parse_args()
    statements, statement_lines, statement_bom, mentions, candidates, quote = preflight()
    updated = make_changes(statements, quote)
    after = counts(updated)
    expected_after = {
        "statements": 12676, "relations": 3653, "complete_relations": 3638,
        "open_relations": 15, "dual_unclassified": 4429, "footnote_claims": 4, "cites": 114,
    }
    require(after == expected_after, f"projected counts differ: {after}")
    preview = {
        "action": "apply" if args.apply else "dry-run",
        "before": counts(statements),
        "after": after,
        "candidate_rows": len(candidates),
        "mention_rows": len(mentions),
        "updated_statements": OLD_IDS + BODY_IDS,
        "new_statements": NEW_IDS,
        "relation_candidates": [
            {"id": LOCATION_ID, "predicate": "book_note_reports_work_location_at_publication",
             "subject": CARTOONS, "object": PALAZZO},
            {"id": ATTRIBUTION_ID, "predicate": "attributed_to", "subject": None, "object": FERRI,
             "possible_subjects": [TAPESTRY_SET, CARTOONS], "status": "open due to ambiguous scope"},
            {"id": PLAN_ID, "predicate": "planned_decoration_for", "subject": FRESCO_PLAN, "object": SALONE},
            {"id": CAVALLO_CITE_ID, "predicate": "cites", "subject": BOOK, "object": CAVALLO},
            {"id": CALBERG_CITE_ID, "predicate": "cites", "subject": BOOK, "object": CALBERG},
            {"id": BLUNT_CITE_ID, "predicate": "cites", "subject": BOOK, "object": BLUNT_COOKE, "page": 36},
            {"id": PASTOR_CITE_ID, "predicate": "cites", "subject": BOOK, "object": PASTOR_XIII,
             "volume": "XIII", "page": 969},
        ],
        "status_claim": {"id": STATUS_ID, "predicate": "reported_dispersed_by_book_publication",
                         "subject": TAPESTRY_SET, "object": None, "relation_candidate": False},
        "body_marker_7_links": [STATUS_ID, LOCATION_ID, CAVALLO_CITE_ID, CALBERG_CITE_ID,
                                BLUNT_CITE_ID, ATTRIBUTION_ID, PLAN_ID, PASTOR_CITE_ID],
    }
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    if not args.apply:
        return

    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    require(not backup.exists(), "recovery backup already exists")
    shutil.copy2(STATEMENTS, backup)
    temp = None
    try:
        temp = write_atomic(STATEMENTS, serialize_statements(updated, statement_lines, statement_bom))
        os.replace(temp, STATEMENTS)
        result, _, _ = read_statements()
        require(counts(result) == expected_after, "post-write statement counts mismatch")
        by_id = {s["statement_id"]: s for s in result}
        for statement_id in NEW_IDS:
            require(statement_id in by_id, f"post-write statement missing: {statement_id}")
        for body_id in BODY_IDS:
            refs = by_id[body_id]["qualifiers"]["footnote_refs"]
            ref = next(r for r in refs if isinstance(r, dict) and r.get("marker") == 7
                       and r.get("segment_id") == SEGMENT_ID and r.get("source_line") == 50)
            require(ref["statement_ids"] == preview["body_marker_7_links"],
                    f"post-write reciprocal footnote links failed: {body_id}")
        print(json.dumps({"result": "applied", "statements_sha256": sha(STATEMENTS),
                          "backup": str(backup.relative_to(ROOT))}, indent=2))
    except Exception:
        shutil.copy2(backup, STATEMENTS)
        raise
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


if __name__ == "__main__":
    main()
