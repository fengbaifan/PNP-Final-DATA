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
PDF = ROOT / "02-sources/01-book/CHP-2.pdf"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p61-notes1-3-4-20261010"

STATEMENTS_SHA = "ee57596eeafea9a5050ed5790a132d87882568b073b524d8ab0b542b4f2e6d60"
MENTIONS_SHA = "ad57d10340723ec589285d0ad37a1ea0e5963a96360896febbe6e07abf5e31a9"
CANDIDATES_SHA = "b4ac5c42748249c553bf133ab9267acb9fbb85422d1198208b19b7e8b8c250de"
SOURCE_SHA = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
PDF_SHA = "317531003e6aeba7d0a956d660eb7552e846fe35b6c7e8e1a4a0a5aa97e8ac5e"

SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l38-54"
N1_ID = "st-chp2-secvii-l38-54-fn-p61-1-vatican-manuscript-reference"
N1_HOLDER_ID = "st-chp2-secvii-l38-54-fn-p61-1-vatican-manuscript-holder"
N3_ID = "st-chp2-secvii-l38-54-fn-p61-3-survey-scope-and-references"
N3_BAGLIONE_ID = "st-chp2-secvii-l38-54-fn-p61-3-baglione-citation"
N3_PASTOR_ID = "st-chp2-secvii-l38-54-fn-p61-3-pastor-citation"
N4_ID = "st-chp2-secvii-l38-54-fn-p61-4-francesco-and-san-carlo-reference"
N4_POLLAK_ID = "st-chp2-secvii-l38-54-fn-p61-4-pollak-citation"
NEW_IDS = [N1_HOLDER_ID, N3_BAGLIONE_ID, N3_PASTOR_ID, N4_POLLAK_ID]

BODY_N1 = "st-chp2-secvii-l32-36-francesco-library-correspondence"
BODY_N3 = "st-chp2-secvii-l32-36-barberini-contribution-assessment-period"
BODY_N4 = "st-chp2-sec-viii-l3-7-barberini-admired-borromini-talents"

BOOK = "cand-2962"
FRANCESCO = "cand-0199"
BARBERINI_FAMILY = "cand-0198"
VATICAN_MS = "cand-4962"
VATICAN_LIBRARY = "cand-4380"
BAGLIONE = "cand-4546"
PASTOR_XIII = "cand-4237"
PASTOR_BIBLIOGRAPHY = "cand-11414"
POLLAK = "cand-4855"
SAN_CARLO = "cand-4963"

EXPECTED_OLD_BODY_REFS = {
    1: [N1_ID],
    3: [N3_ID],
    4: [N4_ID],
}
NEW_BODY_REFS = {
    1: [N1_ID, N1_HOLDER_ID],
    3: [N3_ID, N3_BAGLIONE_ID, N3_PASTOR_ID],
    4: [N4_ID, N4_POLLAK_ID],
}


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
        "cites": sum(s.get("predicate") == "cites"
                     and (s.get("qualifiers") or {}).get("relation_candidate") is True for s in rows),
    }


def body_ref(statement: dict, marker: int) -> dict:
    refs = statement.get("qualifiers", {}).get("footnote_refs", [])
    found = [r for r in refs if isinstance(r, dict) and r.get("marker") == marker
             and r.get("segment_id") == SEGMENT_ID]
    require(len(found) == 1, f"expected one body footnote reference for marker {marker}")
    return found[0]


def preflight():
    for path, expected in (
        (STATEMENTS, STATEMENTS_SHA),
        (MENTIONS, MENTIONS_SHA),
        (CANDIDATES, CANDIDATES_SHA),
        (SOURCE, SOURCE_SHA),
        (PDF, PDF_SHA),
    ):
        require(sha(path) == expected, f"unexpected SHA-256 for {path.relative_to(ROOT)}")

    statements, statement_lines, statement_bom = read_statements()
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mentions = list(csv.DictReader(f))
    by_id = {s["statement_id"]: s for s in statements}
    require(len(by_id) == len(statements), "duplicate statement_id")
    for sid in (N1_ID, N3_ID, N4_ID, BODY_N1, BODY_N3, BODY_N4):
        require(sid in by_id, f"missing statement {sid}")
    for sid in NEW_IDS:
        require(sid not in by_id, f"new statement ID already exists: {sid}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    originals = {
        N1_ID: "1 Bibliotcca Vaticana, MSS. Barb. , and many other collections.",
        N3_ID: "3 It will be obvious that in such a general survey I have omitted a great many important examples of Barberini patronage. Very useful accounts are given in Baglione, pp. 177-83, and Pastor, XIII, pp. 9031000.",
        N4_ID: "4 See, for example. Cardinal Francesco Barberini’s part in the building of S. Carlo aile Quattro Fontane—Pollak, 1927,1, p. 45.",
    }
    for sid, expected_quote in originals.items():
        s = by_id[sid]
        q = s.get("qualifiers", {})
        line_number = {N1_ID: 51, N3_ID: 53, N4_ID: 54}[sid]
        marker = {N1_ID: 1, N3_ID: 3, N4_ID: 4}[sid]
        require(s["segment_id"] == SEGMENT_ID and s["source_file"] == "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
                f"source anchor changed: {sid}")
        require(s["predicate"] == "footnote-claim" and s["original_quote"] == expected_quote
                and source_lines[line_number - 1] == expected_quote, f"source line changed: {sid}")
        require(q.get("source_line_start") == line_number and q.get("source_line_end") == line_number
                and q.get("print_page") == 61 and q.get("pdf_physical_page") == 50
                and q.get("footnote_marker") == marker, f"locator changed: {sid}")
    print_text = " ".join(__import__("fitz").open(PDF)[49].get_text().split())
    require("MSS. Barb. Lat. 6463" in print_text,
            "print p.61 does not verify the manuscript locator")
    require("Baglione, pp. 177-83" in print_text,
            "print p.61 does not verify the Baglione locator")
    require("Pastor, XIII, pp. 903" in " ".join(__import__("fitz").open(PDF)[49].get_text().split()),
            "print p.61 does not verify the Pastor locator")
    require("Pollak, 1927" in " ".join(__import__("fitz").open(PDF)[49].get_text().split()),
            "print p.61 does not verify the Pollak citation")

    candidate_by_id = {c["candidate_id"]: c for c in candidates}
    expected_kinds = {
        BOOK: "archive", FRANCESCO: "person", BARBERINI_FAMILY: "family",
        VATICAN_MS: "archive", VATICAN_LIBRARY: "institution",
        BAGLIONE: "archive", PASTOR_XIII: "archive", PASTOR_BIBLIOGRAPHY: "archive",
        POLLAK: "archive", SAN_CARLO: "place",
    }
    for cid, kind in expected_kinds.items():
        c = candidate_by_id.get(cid)
        require(c is not None and c["suggested_type"] == kind and c["status"] == "open",
                f"candidate {cid} changed")

    segment = "\n".join(source_lines[37:54])
    mention_by_id = {m["mention_id"]: m for m in mentions}
    expected_mentions = {
        "m-chp2-secvii-l38-54-0045": (VATICAN_LIBRARY, "Bibliotcca Vaticana", 1433, 1452),
        "m-chp2-secvii-l38-54-0046": (VATICAN_MS, "MSS. Barb.", 1454, 1464),
        "m-chp2-secvii-l38-54-0048": (BAGLIONE, "Baglione", 1675, 1683),
        "m-chp2-secvii-l38-54-0049": (PASTOR_XIII, "Pastor, XIII", 1701, 1713),
        "m-chp2-secvii-l38-54-0051": (SAN_CARLO, "S. Carlo aile Quattro Fontane", 1803, 1832),
        "m-chp2-secvii-l38-54-0052": (POLLAK, "Pollak, 1927", 1833, 1845),
    }
    for mid, (cid, surface, start, end) in expected_mentions.items():
        m = mention_by_id.get(mid)
        require(m is not None and m["segment_id"] == SEGMENT_ID and m["candidate_id"] == cid
                and m["surface_form"] == surface and m["start_char"] == str(start)
                and m["end_char"] == str(end) and segment[start:end] == surface,
                f"mention anchor changed: {mid}")

    body_expectations = {
        (BODY_N1, 1, 51): N1_ID,
        (BODY_N3, 3, 53): N3_ID,
        (BODY_N4, 4, 54): N4_ID,
    }
    for (body_id, marker, line_number), old_id in body_expectations.items():
        ref = body_ref(by_id[body_id], marker)
        require(ref.get("source_line") == line_number and ref.get("statement_ids") == [old_id],
                f"body marker {marker} reference changed")
    n4_body_ref = by_id[N4_ID].get("qualifiers", {}).get("body_marker_ref", {})
    require(n4_body_ref.get("segment_id") == "chp-2:02_CHP-2_sec_viii:l3-7"
            and n4_body_ref.get("marker") == 4
            and n4_body_ref.get("body_statement_ids") == [BODY_N4],
            "note 4 body marker reference changed")

    duplicate_specs = [
        (VATICAN_MS, 1, None, None),
        (BAGLIONE, 3, 177, 183),
        (PASTOR_XIII, 3, 903, 1000),
        (POLLAK, 4, 45, 45),
    ]
    for target, marker, page_start, page_end in duplicate_specs:
        for s in statements:
            q = s.get("qualifiers", {})
            if s["predicate"] == "cites" and s.get("object_candidate_id") == target and q.get("footnote_marker") == marker:
                require(not (q.get("page_start") == page_start and q.get("page_end") == page_end),
                        f"duplicate note citation already exists for {target}")

    before = counts(statements)
    expected_before = {
        "statements": 12676, "relations": 3653, "complete_relations": 3638,
        "open_relations": 15, "dual_unclassified": 4429, "footnote_claims": 4, "cites": 114,
    }
    require(before == expected_before, f"current ledger counts differ: {before}")
    return statements, statement_lines, statement_bom, mentions, candidates


def make_citation(statement_id: str, target: str, quote: str, claim: str, year: int | None,
                  context_ids: list[str], related_statement_ids: list[str],
                  page: int | None = None, page_end: int | None = None,
                  volume: str | None = None, print_correction: str | None = None,
                  repository_id: str | None = None, shelfmark: str | None = None) -> dict:
    locator = (
        (1, 51) if statement_id in (N1_ID, N1_HOLDER_ID)
        else (3, 53) if statement_id in (N3_ID, N3_BAGLIONE_ID, N3_PASTOR_ID)
        else (4, 54)
    )
    marker, source_line = locator
    q = {
        "source_line_start": source_line,
        "source_line_end": source_line,
        "claim": claim,
        "speaker": "Haskell, authorial footnote",
        "text_layer": "archival locator" if shelfmark else "bibliographic citation",
        "qualification": "This records the source pointer in the book only; the cited manuscript or publication was not independently consulted.",
        "footnote_marker": marker,
        "print_page": 61,
        "pdf_physical_page": 50,
        "citation_publication_candidate_id": target,
        "citation_context_candidate_ids": context_ids,
        "related_statement_ids": related_statement_ids,
        "relation_candidate": True,
        "relation_candidate_note": "S2 source pointer only; it does not independently verify the historical claim or create a formal S6 edge.",
    }
    if year is not None:
        q["year"] = year
    if page is not None:
        q["page_start"] = page
        q["page_end"] = page if page_end is None else page_end
    if volume is not None:
        q["volume"] = volume
    if print_correction is not None:
        q["print_ocr_correction"] = print_correction
    if repository_id is not None:
        q["repository_candidate_id"] = repository_id
    if shelfmark is not None:
        q["shelfmark"] = shelfmark
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


def make_changes(statements: list[dict]) -> list[dict]:
    rows = copy.deepcopy(statements)
    by_id = {s["statement_id"]: s for s in rows}
    n1, n3, n4 = by_id[N1_ID], by_id[N3_ID], by_id[N4_ID]
    bodies = {sid: by_id[sid] for sid in (BODY_N1, BODY_N3, BODY_N4)}
    q1, q3, q4 = (s["qualifiers"] for s in (n1, n3, n4))

    n1["subject_candidate_id"] = BOOK
    n1["object_candidate_id"] = VATICAN_MS
    n1["predicate"] = "cites"
    n1["qualifiers"] = {
        "source_line_start": 51, "source_line_end": 51,
        "claim": "Haskell points readers to MSS. Barb. Lat. 6463 in Biblioteca Vaticana, along with other collections, for Francesco's correspondence.",
        "speaker": "Haskell, authorial footnote",
        "text_layer": "archival source pointer",
        "print_page": 61, "pdf_physical_page": 50, "footnote_marker": 1,
        "shelfmark": "MSS. Barb. Lat. 6463",
        "repository_candidate_id": VATICAN_LIBRARY,
        "citation_publication_candidate_id": VATICAN_MS,
        "citation_context_candidate_ids": [FRANCESCO],
        "other_collections_unspecified": True,
        "qualification": "The named manuscript locator comes from the print page. Other collections are not named; the manuscript was not independently consulted.",
        "print_ocr_correction": "Print p.61 reads 'Biblioteca Vaticana, MSS. Barb. Lat. 6463'; S0 OCR omits 'Lat. 6463' and misreads 'Biblioteca'. S0 remains unchanged.",
        "relation_candidate": True,
        "relation_candidate_note": "The book explicitly cites the manuscript locator for Francesco's correspondence; no manuscript contents are inferred.",
        "related_body_statement_ids": [BODY_N1],
    }
    holder = {
        "statement_id": N1_HOLDER_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": VATICAN_MS,
        "object_candidate_id": VATICAN_LIBRARY,
        "predicate": "held_by",
        "qualifiers": {
            "source_line_start": 51, "source_line_end": 51,
            "claim": "The printed locator places MSS. Barb. Lat. 6463 in Biblioteca Vaticana.",
            "speaker": "Haskell, authorial footnote",
            "text_layer": "repository locator",
            "print_page": 61, "pdf_physical_page": 50, "footnote_marker": 1,
            "shelfmark": "MSS. Barb. Lat. 6463",
            "qualification": "This records the repository named in the 1962 book; present custody is not independently verified.",
            "relation_candidate": True,
            "relation_candidate_note": "Source-qualified archive holding candidate, not a present-day custody claim or formal S6 edge.",
            "related_body_statement_ids": [BODY_N1],
        },
        "original_quote": n1["original_quote"],
        "origin": n1["origin"],
        "source_file": n1["source_file"],
    }

    n3["subject_candidate_id"] = BOOK
    n3["object_candidate_id"] = BARBERINI_FAMILY
    n3["predicate"] = "survey_scope_omits_examples_of"
    n3["qualifiers"] = {
        "source_line_start": 53, "source_line_end": 53,
        "claim": "Haskell says the general survey omits many important examples of Barberini patronage.",
        "speaker": "Haskell",
        "text_layer": "authorial scope note",
        "print_page": 61, "pdf_physical_page": 50, "footnote_marker": 3,
        "qualification": "This is a statement about the book's coverage; the omitted examples are not identified here.",
        "related_body_statement_ids": [BODY_N3],
        "related_citation_statement_ids": [N3_BAGLIONE_ID, N3_PASTOR_ID],
        "relation_candidate": False,
    }

    n4["subject_candidate_id"] = FRANCESCO
    n4["object_candidate_id"] = SAN_CARLO
    n4["predicate"] = "reported_participation_in_building"
    n4["qualifiers"] = {
        "source_line_start": 54, "source_line_end": 54,
        "claim": "Haskell points to Cardinal Francesco Barberini's part in the building of S. Carlo alle Quattro Fontane.",
        "speaker": "Haskell",
        "text_layer": "authorial footnote role claim",
        "print_page": 61, "pdf_physical_page": 50, "footnote_marker": 4,
        "qualification": "The note does not specify the nature of Francesco's role; do not infer commissioner, patron, architect, builder, or owner.",
        "nature_of_role": "unspecified",
        "print_ocr_correction": "Print p.61 reads 'alle Quattro Fontane'; S0 OCR reads 'aile Quattro Fontane'. S0 remains unchanged.",
        "citation_statement_id": N4_POLLAK_ID,
        "relation_candidate": True,
        "relation_candidate_note": "The source explicitly reports a part in the building but leaves the role unspecified; retain as an S2 candidate for later pending/formal review.",
        "body_marker_ref": {
            "segment_id": "chp-2:02_CHP-2_sec_viii:l3-7",
            "source_line": 6,
            "marker": 4,
            "status": "linked",
            "body_statement_ids": [BODY_N4],
        },
        "related_body_statement_ids": [BODY_N4],
    }

    quotes = {N1_ID: n1["original_quote"], N3_ID: n3["original_quote"], N4_ID: n4["original_quote"]}
    citations = [
        make_citation(
            N1_ID, VATICAN_MS, quotes[N1_ID],
            "The book cites MSS. Barb. Lat. 6463 in Biblioteca Vaticana as a source for Francesco's correspondence.",
            None, [FRANCESCO], [N1_ID], repository_id=VATICAN_LIBRARY,
            shelfmark="MSS. Barb. Lat. 6463",
            print_correction="Print p.61 supplies 'Biblioteca' and 'Lat. 6463', which are not fully present in S0 OCR.",
        ),
        make_citation(
            N3_BAGLIONE_ID, BAGLIONE, quotes[N3_ID],
            "Haskell recommends Baglione, pp. 177-83, as a useful account of Barberini patronage.",
            None, [BARBERINI_FAMILY], [N3_ID], page=177, page_end=183,
        ),
        make_citation(
            N3_PASTOR_ID, PASTOR_XIII, quotes[N3_ID],
            "Haskell recommends Pastor, volume XIII, pp. 903-1000, as a useful account of Barberini patronage.",
            None, [BARBERINI_FAMILY], [N3_ID], page=903, page_end=1000, volume="XIII",
            print_correction="Print p.61 gives pp. 903-1000; S0 OCR omits the range dash. The cited volume's edition remains unresolved.",
        ),
        make_citation(
            N4_POLLAK_ID, POLLAK, quotes[N4_ID],
            "Haskell cites Pollak (1927), volume I, p. 45, as an example concerning Francesco's part in the building of S. Carlo alle Quattro Fontane.",
            1927, [FRANCESCO, SAN_CARLO], [N4_ID], page=45, volume="I",
            print_correction="Print p.61 reads 'alle Quattro Fontane'; S0 OCR reads 'aile Quattro Fontane'.",
        ),
    ]
    pastor_note3 = next(s for s in citations if s["statement_id"] == N3_PASTOR_ID)
    pastor_note3["qualifiers"]["possible_version_candidate_id"] = PASTOR_BIBLIOGRAPHY
    pastor_note3["qualifiers"]["version_qualification"] = (
        "The bibliography identifies a 1943 Italian edition of the Pastor series but gives no volume; "
        "do not assign that year to this volume XIII citation."
    )

    refs = {
        1: (bodies[BODY_N1], NEW_BODY_REFS[1]),
        3: (bodies[BODY_N3], NEW_BODY_REFS[3]),
        4: (bodies[BODY_N4], NEW_BODY_REFS[4]),
    }
    for marker, (body, ids) in refs.items():
        ref = body_ref(body, marker)
        require(ref["statement_ids"] == EXPECTED_OLD_BODY_REFS[marker],
                f"body note {marker} references changed during edit")
        ref["statement_ids"] = ids

    citation_by_id = {s["statement_id"]: s for s in citations}
    output = []
    for row in rows:
        output.append(row)
        sid = row["statement_id"]
        if sid == N1_ID:
            output.append(holder)
        elif sid == N3_ID:
            output.extend([citation_by_id[N3_BAGLIONE_ID], citation_by_id[N3_PASTOR_ID]])
        elif sid == N4_ID:
            output.append(citation_by_id[N4_POLLAK_ID])
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
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    statements, statement_lines, statement_bom, mentions, candidates = preflight()
    updated = make_changes(statements)
    after = counts(updated)
    expected_after = {
        "statements": 12680, "relations": 3659, "complete_relations": 3644,
        "open_relations": 15, "dual_unclassified": 4427, "footnote_claims": 1, "cites": 118,
    }
    require(after == expected_after, f"projected counts differ: {after}")
    preview = {
        "action": "apply" if args.apply else "dry-run",
        "before": counts(statements),
        "after": after,
        "candidate_rows": len(candidates),
        "mention_rows": len(mentions),
        "updated_statements": [N1_ID, N3_ID, N4_ID, BODY_N1, BODY_N3, BODY_N4],
        "new_statements": NEW_IDS,
        "relation_candidates": [
            {"id": N1_ID, "predicate": "cites", "subject": BOOK, "object": VATICAN_MS},
            {"id": N1_HOLDER_ID, "predicate": "held_by", "subject": VATICAN_MS, "object": VATICAN_LIBRARY},
            {"id": N3_BAGLIONE_ID, "predicate": "cites", "subject": BOOK, "object": BAGLIONE,
             "pages": "177-183"},
            {"id": N3_PASTOR_ID, "predicate": "cites", "subject": BOOK, "object": PASTOR_XIII,
             "volume": "XIII", "pages": "903-1000", "year": None,
             "possible_version_candidate": PASTOR_BIBLIOGRAPHY},
            {"id": N4_ID, "predicate": "reported_participation_in_building",
             "subject": FRANCESCO, "object": SAN_CARLO, "role": "unspecified"},
            {"id": N4_POLLAK_ID, "predicate": "cites", "subject": BOOK, "object": POLLAK,
             "volume": "I", "page": 45},
        ],
        "non_relation_scope_note": {
            "id": N3_ID, "predicate": "survey_scope_omits_examples_of",
            "subject": BOOK, "object": BARBERINI_FAMILY, "relation_candidate": False,
        },
        "body_marker_links": {str(k): v for k, v in NEW_BODY_REFS.items()},
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
        for sid in NEW_IDS:
            require(sid in by_id, f"post-write statement missing: {sid}")
        for marker, (body_id, expected_ids) in {
            1: (BODY_N1, NEW_BODY_REFS[1]),
            3: (BODY_N3, NEW_BODY_REFS[3]),
            4: (BODY_N4, NEW_BODY_REFS[4]),
        }.items():
            require(body_ref(by_id[body_id], marker)["statement_ids"] == expected_ids,
                    f"post-write body marker {marker} references failed")
        require("year" not in by_id[N3_PASTOR_ID]["qualifiers"],
                "post-write Pastor note 3 year/version qualification failed")
        print(json.dumps({"result": "applied", "statements_sha256": sha(STATEMENTS),
                          "backup": str(backup.relative_to(ROOT))}, ensure_ascii=True, indent=2))
    except Exception:
        shutil.copy2(backup, STATEMENTS)
        raise
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


if __name__ == "__main__":
    main()
