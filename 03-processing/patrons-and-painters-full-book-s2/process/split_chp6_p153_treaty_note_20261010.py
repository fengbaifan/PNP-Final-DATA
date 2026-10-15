from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/06_CHP-6_sec_i.md"
EXPECTED_TABLE_SHA = "2f469a14d1fe794c09265ed1923b546ddd80b1ec5ce51abc0d9936bb89f7e31b"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp6-p153-treaty-note-20261010")
SEGMENT = "chp-6:06_CHP-6_sec_i:l120-157"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
OLD_ID = "st-chp6-notes-l145-p153-n1-5"
CITATION_ID = "st-chp6-notes-l145-p153-n1-5-baldinucci-citation"
COUNTER_ID = "st-chp6-notes-l145-p153-n1-5-haskell-counterstatement"
BODY_ID = "st-chp6-p153-bernini-leave-and-oliva-pressure"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def complete(row: dict) -> bool:
    return bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))


def counts(rows: list[dict]) -> dict[str, int]:
    flag = lambda row: (row.get("qualifiers") or {}).get("relation_candidate")
    true_rows = [row for row in rows if flag(row) is True]
    false_rows = [row for row in rows if flag(row) is False]
    return {
        "statements": len(rows),
        "relation_true": len(true_rows),
        "relation_true_with_two_endpoints": sum(complete(row) for row in true_rows),
        "relation_true_open": sum(not complete(row) for row in true_rows),
        "relation_false": len(false_rows),
        "double_endpoint_unclassified": sum(complete(row) and flag(row) not in (True, False) for row in rows),
        "unclassified_footnote_claim": sum(
            row.get("predicate") == "footnote_claim" and flag(row) not in (True, False) for row in rows
        ),
    }


def build_counterstatement(old: dict, quote: str) -> dict:
    q = dict(old.get("qualifiers") or {})
    q.update({
        "claim": "Haskell states that the reported clause does not occur in published versions of the Treaty of Pisa.",
        "speaker": "Haskell",
        "text_layer": "authorial counterstatement in footnote",
        "qualification": "The published versions are not identified and were not independently examined; this records Haskell's source-critical assertion.",
        "mentioned_candidate_ids": ["cand-6372", "cand-4548", "cand-6371"],
        "relation_candidate": False,
        "relation_candidate_note": "This is a source-critical absence claim with no named version as object, not a relation candidate. Do not convert it into an assertion about every treaty copy.",
        "source_layers": ["Haskell's counterstatement to the reported clause"],
    })
    q.pop("ocr_correction", None)
    return {
        "statement_id": COUNTER_ID,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-6372",
        "object_candidate_id": None,
        "predicate": "footnote_claim",
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def build_citation(quote: str) -> dict:
    return {
        "statement_id": CITATION_ID,
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-4548",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 145,
            "source_line_end": 145,
            "claim": "Haskell's book cites the 1948 Baldinucci edition; print p.153 reads pp.111 ff. and locates note 107 at p.249 in that edition.",
            "speaker": "Haskell",
            "text_layer": "bibliographic citation in authorial footnote",
            "qualification": "The printed locator has been checked against p.153; the cited edition and its note were not independently examined.",
            "citation_locator": "pp.111 ff.",
            "nested_locator": "note 107, p.249 in the cited edition",
            "printed_page": "153",
            "pdf_physical_page": 8,
            "printed_page_locator": "p.153 n.1",
            "footnote_marker": 1,
            "footnote_segment": SEGMENT,
            "related_segment": "chp-6:06_CHP-6_sec_i:l78-89",
            "related_source_lines": [85],
            "linked_body_statement_ids": [BODY_ID],
            "citation_body_statement_ids": [BODY_ID],
            "mentioned_candidate_ids": ["cand-0166", "cand-4548"],
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly cites this archive from Haskell's book. This records a bibliographic link and does not validate the cited claim.",
            "ocr_correction": "S0 reads 'pp. in ff.'; print p.153 reads 'pp. 111 ff.'. S0 is unchanged.",
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply reviewed S2 statement split; default is dry-run")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    require(sha256(TABLE) == EXPECTED_TABLE_SHA, "book-statements.jsonl changed since review")
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(OLD_ID in by_id, "composite p.153 statement missing")
    require(CITATION_ID not in by_id and COUNTER_ID not in by_id, "split statement ID already exists")

    old = by_id[OLD_ID]
    old_q = old.get("qualifiers") or {}
    require(old.get("predicate") == "footnote_claim", "p.153 row predicate changed")
    require(old.get("segment_id") == SEGMENT, "p.153 statement segment changed")
    require((old.get("subject_candidate_id"), old.get("object_candidate_id")) == ("cand-6371", "cand-6372"),
            "p.153 statement endpoints changed")
    require(old_q.get("relation_candidate") not in (True, False), "p.153 statement already classified")
    require(old_q.get("source_line_start") == 145 and old_q.get("source_line_end") == 145,
            "p.153 source anchor changed")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    require(len(source_lines) >= 145, "source file ends before p.153 note")
    source_quote = source_lines[144]
    require(source_quote.startswith("1 Baldinucci, 1948, pp. in ff. In a note (107 on page 249)"),
            "p.153 source line changed")
    citation_quote = source_quote[:source_quote.index(" In a note")]
    report_start = source_quote.index("In a note (107 on page 249)")
    counter_start = source_quote.index("This clause certainly does not occur")
    report_quote = source_quote[report_start:counter_start].rstrip()
    counter_quote = source_quote[counter_start:]
    require(citation_quote == "1 Baldinucci, 1948, pp. in ff.", "citation quote span changed")
    require("Treaty of Pisa" in report_quote and "French King" in report_quote and "Pope" in report_quote and "artists" in report_quote,
            "reported clause quote span changed")
    require(counter_quote.endswith("published versions of the Treaty."), "counterstatement quote span changed")
    require(old.get("original_quote") == source_quote, "original composite quote changed")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidates = {row["candidate_id"]: row for row in csv.DictReader(handle)}
    required_candidates = {"cand-0166", "cand-2962", "cand-4548", "cand-6371", "cand-6372", "cand-6373", "cand-6374"}
    require(required_candidates <= set(candidates), "one or more cited candidates are missing")
    require(candidates["cand-2962"]["suggested_type"] == "archive", "Haskell book candidate type changed")
    require(candidates["cand-4548"]["suggested_type"] == "archive", "Baldinucci edition candidate type changed")

    coverage_text = COVERAGE.read_text(encoding="utf-8-sig")
    require(SEGMENT in coverage_text, "reviewed segment missing from S2 coverage")

    before = counts(rows)
    require(before == {
        "statements": 12684,
        "relation_true": 3776,
        "relation_true_with_two_endpoints": 3760,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4315,
        "unclassified_footnote_claim": 1,
    }, f"unexpected statement counts: {before}")

    # Recast the existing ID as the disputed, source-attributed employment-right claim.
    old["subject_candidate_id"] = "cand-6373"
    old["object_candidate_id"] = "cand-6374"
    old["predicate"] = "right_to_employ_reported"
    q = dict(old_q)
    q.update({
        "claim": "Samek Ludovici's note 107 in the 1948 edition reports that a Treaty of Pisa clause granted the unnamed French king the right to employ the Pope's artists.",
        "speaker": "Samek Ludovici, as reported by Haskell",
        "text_layer": "secondhand relation claim in authorial footnote",
        "qualification": "This is a secondhand and disputed report: Haskell immediately states that the clause is absent from published treaty versions. It does not establish actual employment or an operative right; neither text was independently examined.",
        "mentioned_candidate_ids": ["cand-4548", "cand-6371", "cand-6372", "cand-6373", "cand-6374"],
        "relation_candidate": True,
        "relation_candidate_note": "Preserve only the attributed right-to-employ claim between the unnamed French king and the Pope's artists. Haskell disputes its presence in published treaty versions; this is a contested S2 candidate, not a verified fact or S6 edge.",
        "source_layers": ["Samek Ludovici's claim as reported by Haskell"],
        "ocr_correction": "S0 reads 'Satnek Ludovici'; print p.153 reads 'Samek Ludovici'. S0 is unchanged.",
    })
    old["qualifiers"] = q
    old["original_quote"] = report_quote

    counterstatement = build_counterstatement(old, counter_quote)
    citation = build_citation(citation_quote)
    rows.extend([citation, counterstatement])

    after = counts(rows)
    require(after == {
        "statements": 12686,
        "relation_true": 3778,
        "relation_true_with_two_endpoints": 3762,
        "relation_true_open": 16,
        "relation_false": 1761,
        "double_endpoint_unclassified": 4314,
        "unclassified_footnote_claim": 0,
    }, f"unexpected projected counts: {after}")

    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    payload = b"".join(output)

    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "split_statement_ids": [OLD_ID, CITATION_ID, COUNTER_ID],
        "before": before,
        "after": after,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    require(not BACKUP.exists(), "recovery backup already exists")
    shutil.copy2(TABLE, BACKUP)
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".tmp-", delete=False) as handle:
            handle.write(payload)
            temporary = Path(handle.name)
        os.replace(temporary, TABLE)
        written = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        require(counts(written) == after, "post-write counts differ from preview")
        written_by_id = {row["statement_id"]: row for row in written}
        require((written_by_id[OLD_ID]["subject_candidate_id"], written_by_id[OLD_ID]["object_candidate_id"]) ==
                ("cand-6373", "cand-6374"), "reported claim endpoints were not persisted")
        require(written_by_id[CITATION_ID]["predicate"] == "cites" and
                written_by_id[CITATION_ID]["subject_candidate_id"] == "cand-2962" and
                written_by_id[CITATION_ID]["object_candidate_id"] == "cand-4548", "citation was not persisted")
        require(written_by_id[COUNTER_ID]["object_candidate_id"] is None and
                (written_by_id[COUNTER_ID].get("qualifiers") or {}).get("relation_candidate") is False,
                "counterstatement classification was not persisted")
        print(json.dumps({"result": "applied", "counts": counts(written), "sha256": sha256(TABLE),
                          "backup": str(BACKUP.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise


if __name__ == "__main__":
    main()
