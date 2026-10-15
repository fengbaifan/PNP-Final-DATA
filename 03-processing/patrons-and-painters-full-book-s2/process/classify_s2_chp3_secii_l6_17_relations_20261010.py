from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-ii-l6-17-relations-20261010"
SEGMENT_ID = "chp-3:03_CHP-3_sec_ii:l6-17"

EXPECTED_HASHES = {
    STATEMENTS: "9ae75084843f045fbf7ac9c73cb27326eda6840128618cd5d943c3aa4aa003fa",
    CANDIDATES: "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

DECISIONS = {
    "st-chp3-secii-l6-17-apse-mosaic-plan": (
        True,
        "Haskell says plans were made to cover the Gesu apse with mosaics. The plan-maker is not named; leave the subject open and do not infer that the Jesuits commissioned or executed it.",
    ),
    "st-chp3-secii-l6-17-baglione-complained-to-pope-about-unpaid-fee": (
        True,
        "Haskell reports Baglione's complaint that the Jesuit fathers had not fully paid him for The Resurrection. Keep the Pope as addressee, the Jesuit fathers as the reported non-payers, and 'five years' relative to the picture.",
    ),
    "st-chp3-secii-l6-17-baglione-reported-repeated-delay-and-no-funds": (
        True,
        "This is Baglione's reported explanation of repeated payment delay by the Jesuit fathers. Preserve the quoted speaker and do not treat the debt or the Jesuits' finances as independently verified.",
    ),
    "st-chp3-secii-l6-17-decoration-effect-described-as-disastrous": (
        False,
        "'Disastrous' is Haskell's evaluation of the effect of Farnese's death while decoration was incomplete; the one-ended statement is an assessment, not a relation between entities.",
    ),
    "st-chp3-secii-l6-17-decoration-stop-and-family-reservation": (
        True,
        "Haskell links the immediate stoppage of work to Farnese's reservation of the tribune and High Altar decoration for his family and the need for heirs' permission. Preserve the two spaces, unnamed heirs, and source scope; do not infer legal title.",
    ),
    "st-chp3-secii-l6-17-early-decoration-haphazard-not-concerted": (
        True,
        "Haskell contrasts the Gesu's early decoration with a concerted Jesuit plan and describes its execution as haphazard and difficult. Retain this as the author's interpretation of the church-decoration process.",
    ),
    "st-chp3-secii-l6-17-external-painter-exposed-jesuit-financial-weakness": (
        True,
        "Haskell links the Jesuits' commissioning of an established painter from outside their own ranks to the visible financial weakness. The painter is unnamed in this general claim; keep the object open and do not substitute Baglione from the next sentence as its exhaustive referent.",
    ),
    "st-chp3-secii-l6-17-farnese-death-with-decoration-unbegun": (
        True,
        "Haskell dates Farnese's death to 1589 and says Gesu decoration had scarcely begun by then. Preserve the approximate completion state and the author's account.",
    ),
    "st-chp3-secii-l6-17-gesu-designed-for-public-worship": (
        False,
        "This describes the Gesu's intended public-worship function as a site attribute; 'public worship' is not a separately identified entity endpoint in this claim.",
    ),
    "st-chp3-secii-l6-17-gesu-general-effect-bleak": (
        False,
        "The 'little bleak' general effect is Haskell's qualified aesthetic assessment, not a relation between the church and another entity.",
    ),
    "st-chp3-secii-l6-17-heirs-disinterest-and-jesuit-delay": (
        True,
        "Haskell says Farnese's unnamed heirs lacked interest in the decoration and the Jesuits could not resume it for generations despite repeated efforts. Keep the heirs unnamed and preserve the source's broad chronology.",
    ),
    "st-chp3-secii-l6-17-hypothetical-visitor-old-fashioned-decoration": (
        False,
        "The informed visitor is hypothetical and the dates are alternatives; this is Haskell's imagined assessment of the church's decor, not a documented visitor relation.",
    ),
    "st-chp3-secii-l6-17-jesuit-private-novice-training-and-missions": (
        True,
        "Haskell says the Jesuits trained their novices for overseas missions. Preserve the unnamed collective, destinations, and Haskell's 'horribly dangerous' characterization without inventing a specific mission.",
    ),
    "st-chp3-secii-l6-17-jesuits-concentrated-on-side-chapels": (
        True,
        "Haskell says the Jesuits were compelled to concentrate on the Gesu side chapels after the principal decoration stalled. Keep the venue group-level.",
    ),
    "st-chp3-secii-l6-17-jesuits-employed-valeriano-to-cut-costs": (
        True,
        "Haskell says the Jesuits reduced costs by employing their own member Padre Valeriano as principal painter. Preserve the stated cost motive and source attribution.",
    ),
    "st-chp3-secii-l6-17-muziano-circumcision-commission": (
        True,
        "Haskell says Farnese commissioned Girolamo Muziano to paint The Circumcision for the Gesu High Altar. Keep the named work and altar as distinct scope; do not infer completion from the commission.",
    ),
    "st-chp3-secii-l6-17-no-bolognese-artists-represented": (
        True,
        "Haskell explicitly says no Bolognese artist who had helped transform church decoration at the century's beginning was represented at the Gesu. Preserve the negative claim and its defined artist group.",
    ),
    "st-chp3-secii-l6-17-older-families-submerged-by-new-rich": (
        True,
        "Haskell contrasts older Roman aristocratic families with the newly rich papal entourage, saying the former were being overtaken in wealth and political importance. Keep both as source-defined groups; the named families are examples, not an exhaustive roster.",
    ),
    "st-chp3-secii-l6-17-pious-ladies-paid-chapel-structure": (
        True,
        "Haskell says some unnamed pious ladies paid for chapel structures while leaving essential decoration to the Jesuits. Preserve the unnamed women and chapels; do not infer particular commissions.",
    ),
    "st-chp3-secii-l6-17-schemes-grandiose-while-alive": (
        True,
        "Haskell characterizes Farnese's schemes during his lifetime as grandiose. The plans are not bounded to a named work here; leave the object open and preserve the continuation from the preceding segment.",
    ),
    "st-chp3-secii-l6-17-side-chapels-attracted-pious-ladies": (
        True,
        "Haskell says the Gesu side chapels attracted pious ladies from older Roman aristocratic families. Keep the women and family branches as collective examples, not individually identified patrons.",
    ),
    "st-chp3-secii-l6-17-valeriano-style-authorial-reading": (
        False,
        "This is Haskell's interpretive evaluation of Valeriano's style as mystery and power, not a relation between two entities. Retain the attribution and footnote linkage.",
    ),
    "st-chp3-secii-l6-17-vecchi-frescoes-begun": (
        True,
        "Haskell says Giovanni de' Vecchi began frescoes on the Gesu pendentives and dome. Preserve the attributed description of adornments and putti without naming an individual fresco or treating work as complete.",
    ),
}

EXPECTED_TARGETS = {
    "st-chp3-secii-l6-17-apse-mosaic-plan": (8, 8, "", "cand-5005", "plans were made for the apse"),
    "st-chp3-secii-l6-17-baglione-complained-to-pope-about-unpaid-fee": (11, 13, "cand-0158", "cand-1321", "Baglione was forced to complain"),
    "st-chp3-secii-l6-17-baglione-reported-repeated-delay-and-no-funds": (13, 13, "cand-0158", "cand-1321", "constantly being put off"),
    "st-chp3-secii-l6-17-decoration-effect-described-as-disastrous": (8, 8, "cand-3112", "", "the effect was disastrous"),
    "st-chp3-secii-l6-17-decoration-stop-and-family-reservation": (8, 9, "cand-0995", "cand-3112", "reserved the adornment of the tribune"),
    "st-chp3-secii-l6-17-early-decoration-haphazard-not-concerted": (14, 14, "cand-3112", "cand-1321", "far from reflecting any concerted Jesuit plan"),
    "st-chp3-secii-l6-17-external-painter-exposed-jesuit-financial-weakness": (11, 11, "cand-1321", "", "commissioned an estabEshed painter"),
    "st-chp3-secii-l6-17-farnese-death-with-decoration-unbegun": (8, 8, "cand-0995", "cand-3112", "when he died in 1589"),
    "st-chp3-secii-l6-17-gesu-designed-for-public-worship": (15, 15, "cand-3112", "", "designed for public worship"),
    "st-chp3-secii-l6-17-gesu-general-effect-bleak": (14, 14, "cand-3112", "", "the general effect must have been a little bleak"),
    "st-chp3-secii-l6-17-heirs-disinterest-and-jesuit-delay": (9, 9, "cand-3112", "cand-1321", "total lack of interest in the whole matter"),
    "st-chp3-secii-l6-17-hypothetical-visitor-old-fashioned-decoration": (14, 14, "cand-3112", "", "An informed visitor inspecting the church"),
    "st-chp3-secii-l6-17-jesuit-private-novice-training-and-missions": (15, 15, "cand-1321", "cand-5016", "private training of their own novices"),
    "st-chp3-secii-l6-17-jesuits-concentrated-on-side-chapels": (9, 9, "cand-1321", "cand-5002", "concentrate on the side-chapels"),
    "st-chp3-secii-l6-17-jesuits-employed-valeriano-to-cut-costs": (11, 11, "cand-1321", "cand-2683", "employing as principal painter one of their own members"),
    "st-chp3-secii-l6-17-muziano-circumcision-commission": (7, 8, "cand-0995", "cand-5003", "commissioned Girolamo Muziano"),
    "st-chp3-secii-l6-17-no-bolognese-artists-represented": (14, 14, "cand-3112", "cand-5015", "Not a single one of the Bolognese artists"),
    "st-chp3-secii-l6-17-older-families-submerged-by-new-rich": (10, 10, "cand-5009", "cand-5010", "submerged in wealth and political importance"),
    "st-chp3-secii-l6-17-pious-ladies-paid-chapel-structure": (11, 11, "cand-5008", "cand-5002", "paid for the main structure of the chapel"),
    "st-chp3-secii-l6-17-schemes-grandiose-while-alive": (7, 7, "cand-0995", "", "his schemes were as grandiose"),
    "st-chp3-secii-l6-17-side-chapels-attracted-pious-ladies": (10, 10, "cand-5002", "cand-5008", "great attraction for pious ladies"),
    "st-chp3-secii-l6-17-valeriano-style-authorial-reading": (11, 11, "cand-2683", "", "interpreted as mystery and power"),
    "st-chp3-secii-l6-17-vecchi-frescoes-begun": (8, 8, "cand-2706", "cand-5004", "began frescoes on the pendentives"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qualifiers(row: dict) -> dict:
    value = row.get("qualifiers") or {}
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise SystemExit(f"invalid qualifiers for {row.get('statement_id')}")
    return value


def has_endpoint(value: object) -> bool:
    return value is not None and str(value).strip() != ""


def stats(rows: list[dict]) -> dict:
    bilateral = [
        row for row in rows
        if has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id"))
    ]
    candidates = [row for row in rows if qualifiers(row).get("relation_candidate") is True]
    categories = Counter(
        "true" if qualifiers(row).get("relation_candidate") is True
        else "false" if qualifiers(row).get("relation_candidate") is False
        else "pending"
        for row in bilateral
    )
    open_candidates = sum(
        not (has_endpoint(row.get("subject_candidate_id")) and has_endpoint(row.get("object_candidate_id")))
        for row in candidates
    )
    return {
        "bilateral": len(bilateral),
        "bilateral_true": categories["true"],
        "bilateral_false": categories["false"],
        "bilateral_pending": categories["pending"],
        "relation_candidates_total": len(candidates),
        "relation_candidates_open": open_candidates,
    }


def read_jsonl_lines(raw: bytes) -> list[tuple[dict, bytes, bytes]]:
    result = []
    for line in raw.splitlines(keepends=True):
        body = line.rstrip(b"\r\n")
        ending = line[len(body):]
        row = json.loads(body.decode("utf-8-sig"))
        result.append((row, ending, body))
    return result


def project(raw: bytes, lines: list[tuple[dict, bytes, bytes]]) -> tuple[bytes, dict[str, dict]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    output = bytearray()
    changed = {}
    for index, (row, ending, original_body) in enumerate(lines):
        statement_id = row.get("statement_id")
        if statement_id in DECISIONS:
            q = qualifiers(row)
            flag, note = DECISIONS[statement_id]
            if "relation_candidate" in q:
                raise SystemExit(f"target already classified: {statement_id}")
            q["relation_candidate"] = flag
            q["relation_candidate_note"] = note
            row["qualifiers"] = q
            changed[statement_id] = q
            encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            output.extend(encoded)
        else:
            output.extend(original_body)
        output.extend(ending)
    return bytes(output), changed


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"SHA mismatch for {path.relative_to(ROOT)}: {actual}")
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage_rows = [row for row in csv.DictReader(handle) if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit(f"unexpected coverage matches: {len(coverage_rows)}")
    coverage = coverage_rows[0]
    if (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"]) != (
        "reviewed", "complete", "L7-17"
    ):
        raise SystemExit(f"unexpected S2 coverage row: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
    raw = STATEMENTS.read_bytes()
    lines = read_jsonl_lines(raw)
    all_rows = [row for row, _, _ in lines]
    segment_rows = [row for row in all_rows if row.get("segment_id") == SEGMENT_ID]
    targets = {row["statement_id"]: row for row in segment_rows if row.get("statement_id") in DECISIONS}
    if set(targets) != set(DECISIONS) or len(segment_rows) != 26:
        raise SystemExit(f"unexpected segment targets/size: targets={sorted(targets)} rows={len(segment_rows)}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for statement_id, (line_start, line_end, subject, obj, quote_part) in EXPECTED_TARGETS.items():
        row = targets[statement_id]
        q = qualifiers(row)
        if "relation_candidate" in q:
            raise SystemExit(f"target already classified: {statement_id}")
        if (q.get("source_line_start"), q.get("source_line_end")) != (line_start, line_end):
            raise SystemExit(f"source locator changed for {statement_id}: {q}")
        if row.get("subject_candidate_id") != subject or row.get("object_candidate_id") != obj:
            raise SystemExit(f"endpoint changed for {statement_id}: {row}")
        normalized_quote = " ".join(row.get("original_quote", "").split())
        if quote_part not in normalized_quote:
            raise SystemExit(f"quotation anchor changed for {statement_id}")
        if quote_part not in " ".join(source_lines[line_start - 1:line_end]):
            raise SystemExit(f"source lines no longer contain {quote_part!r} for {statement_id}")
        if (subject and subject not in candidate_ids) or (obj and obj not in candidate_ids):
            raise SystemExit(f"unresolved candidate endpoint in {statement_id}")

    before = stats(all_rows)
    expected_before = {
        "bilateral": 8499,
        "bilateral_true": 4542,
        "bilateral_false": 460,
        "bilateral_pending": 3497,
        "relation_candidates_total": 4576,
        "relation_candidates_open": 34,
    }
    if before != expected_before:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    projected, changed = project(raw, lines)
    projected_rows = [row for row, _, _ in read_jsonl_lines(projected)]
    after = stats(projected_rows)
    expected_after = {
        "bilateral": 8499,
        "bilateral_true": 4557,
        "bilateral_false": 460,
        "bilateral_pending": 3482,
        "relation_candidates_total": 4594,
        "relation_candidates_open": 37,
    }
    if len(changed) != len(DECISIONS) or after != expected_after:
        raise SystemExit(f"unexpected projected result: changed={len(changed)} counts={after}")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT_ID,
        "printed_page": 66,
        "segment_statements": len(segment_rows),
        "new_decisions": {
            "relation_candidates": sum(flag for flag, _ in DECISIONS.values()),
            "nonrelations": sum(not flag for flag, _ in DECISIONS.values()),
            "open_endpoint_candidates": sum(
                flag and not (has_endpoint(targets[sid].get("subject_candidate_id")) and has_endpoint(targets[sid].get("object_candidate_id")))
                for sid, (flag, _) in DECISIONS.items()
            ),
        },
        "before": before,
        "after": after,
        "changed_ids": sorted(changed),
        "backup": str(BACKUP.relative_to(ROOT)) if args.apply else None,
    }, ensure_ascii=False, indent=2))
    if args.dry_run:
        return

    shutil.copy2(STATEMENTS, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix="book-statements.s2-chp3-secii-l6-17.", suffix=".tmp", dir=TABLES)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(projected)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, STATEMENTS)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

    written_rows = [row for row, _, _ in read_jsonl_lines(STATEMENTS.read_bytes())]
    written_targets = {row["statement_id"]: row for row in written_rows if row.get("statement_id") in DECISIONS}
    if set(written_targets) != set(DECISIONS):
        raise SystemExit("post-write target set changed; recovery backup retained")
    for statement_id, (flag, note) in DECISIONS.items():
        q = qualifiers(written_targets[statement_id])
        if q.get("relation_candidate") is not flag or q.get("relation_candidate_note") != note:
            raise SystemExit(f"post-write classification mismatch: {statement_id}; recovery backup retained")
    verified = stats(written_rows)
    if verified != expected_after:
        raise SystemExit(f"post-write counts mismatch: {verified}; recovery backup retained")
    print(f"post_write_sha256={sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
