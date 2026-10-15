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
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-ii-l19-31-relations-20261010"
SEGMENT = "chp-3:03_CHP-3_sec_ii:l19-31"

HASHES = {
    STATEMENTS: "0367676e97510e751dd8e0c1466c53a078850dcc2affb214ecf911d9bbe77b70",
    CANDIDATES: "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "cb17a400fc5a79d895e31fe4a112c83e010f5e5b859883852b3985b7010eb1e6",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

# flag, note, source start, source end, subject, object, quotation anchor
TARGETS = {
    "st-chp3-secii-l19-31-andrea-decoration-delayed": (True, "Haskell says lack of funds repeatedly delayed decoration of S. Andrea al Quirinale; no completion date is stated.", 28, 29, "cand-1321", "cand-0694", "S. Andrea al Quirinale,5"),
    "st-chp3-secii-l19-31-aquaviva-controlled-and-shaped-scheme": (True, "Haskell says Aquaviva exercised immediate control, took a strong personal interest, and made suggestions; the suggestions are not itemized.", 26, 26, "cand-0113", "cand-5022", "took a strong personal interest in the scheme"),
    "st-chp3-secii-l19-31-aquaviva-correspondence-raising-funds": (True, "Haskell says Aquaviva's correspondence often addresses fundraising; the letters and particular fundraising matter remain unspecified.", 29, 30, "cand-0113", "", "the correspondence of General"),
    "st-chp3-secii-l19-31-austerity-could-be-turned-to-account": (False, "This is Haskell's conditional evaluation of Jesuit austerity, not a specific relation between identified entities.", 30, 30, "cand-1321", "", "the very austerity which they were compelled to adopt"),
    "st-chp3-secii-l19-31-fiammeri-directed-vitale-decoration": (True, "Haskell says Giovanni Battista Fiammeri directed the S. Vitale decoration under Aquaviva's control; individual frescoes are not titled.", 25, 26, "cand-1034", "cand-5022", "The decoration was directed by a Jesuit painter"),
    "st-chp3-secii-l19-31-jesuit-patronage-limited": (False, "This is Haskell's qualitative assessment of the scale of Jesuit patronage, without a distinct object endpoint.", 28, 28, "cand-1321", "", "the contribution to patronage made by the Jesuits had been exceedingly limited"),
    "st-chp3-secii-l19-31-jesuit-style-first-brought-into-being": (True, "Haskell characterizes a Jesuit style as first emerging at S. Stefano Rotondo; its features remain unspecified.", 20, 20, "cand-5021", "cand-0722", "a truly Jesuit style was brought into being"),
    "st-chp3-secii-l19-31-jesuits-pride-in-innovation": (True, "Haskell says the Jesuits took a certain pride in the cycle's innovations of subject matter and treatment; retain the qualified wording.", 22, 22, "cand-1321", "cand-5019", "a certain pride in these innovations"),
    "st-chp3-secii-l19-31-planned-adoption-at-vitale": (True, "Haskell reports a Jesuit plan to adopt the S. Stefano approach at S. Vitale; a plan does not prove full implementation.", 23, 23, "cand-1321", "cand-0724", "they planned to adopt them in the third church"),
    "st-chp3-secii-l19-31-rector-commissioned-stefano-cycle": (True, "Haskell says the unidentified German College rector commissioned Circignani's fresco cycle for S. Stefano Rotondo; the rector's identity remains open.", 21, 22, "cand-5018", "cand-5019", "the rector commissioned from"),
    "st-chp3-secii-l19-31-richeome-dedicated-book-to-aquaviva": (True, "Haskell says Richeome dedicated the 1611 book to Aquaviva; this records the book's dedication, not a broader patronage relation.", 31, 31, "cand-5024", "cand-0113", "he dedicated to Aquaviva"),
    "st-chp3-secii-l19-31-richeome-wrote-book-1611": (True, "Haskell identifies Louis Richeome as author of the book written in 1611; retain the source's spelling and date.", 30, 31, "cand-2192", "cand-5024", "In 1611 a French"),
    "st-chp3-secii-l19-31-shortage-funds-explains-limited-patronage": (True, "Haskell explains the Jesuits' limited patronage by their severe shortage of funds; preserve this authorial causal claim and leave its effect endpoint open.", 28, 28, "cand-1321", "", "This was largely due to their desperate shortage of funds"),
    "st-chp3-secii-l19-31-stefano-allotted-to-jesuits": (True, "Haskell reports Gregory XIII allotted S. Stefano Rotondo to the Jesuits; no legal terms or date are added.", 20, 20, "cand-1321", "cand-0722", "allotted by Gregory XIII"),
    "st-chp3-secii-l19-31-stefano-cycle-detail-and-explanations": (True, "Haskell describes detailed painting and explanations attached to each fresco; retain the attachment claim with its explanatory-text endpoint open.", 22, 22, "cand-5019", "", "the explanation of the torture was attached to each fresco"),
    "st-chp3-secii-l19-31-stefano-cycle-martyrdoms-setting": (True, "Haskell says the cycle depicts martyrdoms mostly enacted under the late Roman Empire; retain mostly as a scope qualifier.", 22, 22, "cand-5019", "cand-5020", "mostly enacted under the late Roman empire"),
    "st-chp3-secii-l19-31-stefano-given-to-german-college": (True, "Haskell says S. Stefano Rotondo was given to the German College; keep this distinct from the rector's fresco commission.", 21, 21, "cand-0722", "cand-5017", "The church was given to the German college"),
    "st-chp3-secii-l19-31-venetian-tradition-in-subjects": (True, "This preserves Haskell's interpretive link between the cycle's subjects and the Venetian High Renaissance; it is not an authorship attribution.", 22, 22, "cand-5019", "cand-4319", "a last feeble glimmer of the Venetian High Renaissance"),
    "st-chp3-secii-l19-31-vitale-choir-unrestrained-torture": (True, "Haskell says the S. Vitale choir display reveals torture without restraint; the choir is the stated location.", 27, 27, "cand-5022", "cand-5023", "Only in the choir were the painters encouraged"),
    "st-chp3-secii-l19-31-vitale-decoration-delayed": (True, "Haskell says financial shortage repeatedly held up S. Vitale decoration; do not infer when work resumed or finished.", 28, 29, "cand-1321", "cand-0724", "S. Vitale was constantly being held up for this reason"),
    "st-chp3-secii-l19-31-vitale-generation-atmosphere-relaxed": (True, "Haskell compares the later S. Vitale generation with S. Stefano Rotondo and says its atmosphere had relaxed; retain the comparative interpretation.", 26, 26, "cand-5022", "cand-0722", "the generation that had passed since the decoration of S. Stefano Rotondo"),
    "st-chp3-secii-l19-31-vitale-given-to-society-by-clement": (True, "Haskell says S. Vitale was given to the Jesuit Society by Clement VIII; retain the source's wording and named donor.", 24, 25, "cand-0724", "cand-1321", "which was given to the Society by"),
    "st-chp3-secii-l19-31-vitale-idyllic-first-impression": (False, "This records Haskell's visual characterization of the frescoes' first impression, not a distinct entity relation.", 26, 27, "cand-5022", "", "give the impression of idyllic pastoral landscapes"),
    "st-chp3-secii-l19-31-vitale-images-martyr-and-soldier": (True, "Haskell describes the fresco cycle as depicting an unnamed martyr and soldier undergoing torture; keep the depicted figures as an open object group.", 27, 27, "cand-5022", "", "nailed to one tree is a martyr"),
    "st-chp3-secii-l19-31-vitale-poussin-attribution": (True, "Haskell reports a nineteenth-century attribution of the S. Vitale frescoes to Gaspard Poussin; this is historical attribution, not accepted authorship.", 26, 27, "cand-5022", "cand-0949", "they were attributed to"),
    "st-chp3-secii-l19-31-vitale-subjects-mostly-torture": (True, "Haskell says torture predominates among the S. Vitale fresco subjects; preserve mostly/almost exclusively and leave the subject-term endpoint open.", 26, 26, "cand-5022", "", "the subjects were almost exclusively concerned with torture"),
}

EXPECTED_BEFORE = {
    "bilateral": 8499,
    "bilateral_true": 4557,
    "bilateral_false": 460,
    "bilateral_pending": 3482,
    "relation_candidates_total": 4594,
    "relation_candidates_open": 37,
}
EXPECTED_AFTER = {
    "bilateral": 8499,
    "bilateral_true": 4575,
    "bilateral_false": 460,
    "bilateral_pending": 3464,
    "relation_candidates_total": 4617,
    "relation_candidates_open": 42,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(raw: bytes):
    result = []
    offset = 0
    for line in raw.splitlines(keepends=True):
        if line.strip():
            result.append((json.loads(line), offset, offset + len(line)))
        offset += len(line)
    return result


def has_endpoint(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def stats(rows):
    bilateral = [r for r in rows if has_endpoint(r.get("subject_candidate_id")) and has_endpoint(r.get("object_candidate_id"))]
    def flag(row):
        q = row.get("qualifiers", {})
        return q.get("relation_candidate") if isinstance(q, dict) else None
    return {
        "bilateral": len(bilateral),
        "bilateral_true": sum(flag(r) is True for r in bilateral),
        "bilateral_false": sum(flag(r) is False for r in bilateral),
        "bilateral_pending": sum(flag(r) is None for r in bilateral),
        "relation_candidates_total": sum(flag(r) is True for r in rows),
        "relation_candidates_open": sum(
            flag(r) is True and not (has_endpoint(r.get("subject_candidate_id")) and has_endpoint(r.get("object_candidate_id")))
            for r in rows
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for path, expected in HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"SHA mismatch for {path.relative_to(ROOT)}: {actual}")
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = [r for r in csv.DictReader(handle) if r["segment_id"] == SEGMENT]
    if len(coverage) != 1 or (
        coverage[0]["disposition"],
        coverage[0]["migration_status"],
        coverage[0]["source_line_ranges"],
    ) != ("reviewed", "complete", "L20-31"):
        raise SystemExit(f"unexpected coverage row: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {r["candidate_id"] for r in csv.DictReader(handle)}
    raw = STATEMENTS.read_bytes()
    parsed = read_jsonl(raw)
    rows = [r for r, _, _ in parsed]
    segment_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    targets = {r["statement_id"]: r for r in segment_rows if r.get("statement_id") in TARGETS}
    if len(segment_rows) != 26 or set(targets) != set(TARGETS):
        raise SystemExit(f"unexpected segment records: rows={len(segment_rows)}, targets={len(targets)}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for statement_id, (flag, note, start, end, subject, obj, anchor) in TARGETS.items():
        row = targets[statement_id]
        qualifiers = row.get("qualifiers", {})
        if "relation_candidate" in qualifiers:
            raise SystemExit(f"target already classified: {statement_id}")
        if (qualifiers.get("source_line_start"), qualifiers.get("source_line_end")) != (start, end):
            raise SystemExit(f"source locator changed for {statement_id}: {qualifiers}")
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != (subject, obj):
            raise SystemExit(f"endpoint changed for {statement_id}: {row}")
        if anchor not in " ".join(row.get("original_quote", "").split()):
            raise SystemExit(f"quotation anchor changed for {statement_id}")
        if anchor not in " ".join(source_lines[start - 1:end]):
            raise SystemExit(f"source text no longer contains {anchor!r} for {statement_id}")
        if (subject and subject not in candidate_ids) or (obj and obj not in candidate_ids):
            raise SystemExit(f"unresolved candidate endpoint in {statement_id}")

    before = stats(rows)
    if before != EXPECTED_BEFORE:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    replacements = {}
    for row, start, end in parsed:
        statement_id = row.get("statement_id")
        if statement_id not in TARGETS:
            continue
        flag, note, *_ = TARGETS[statement_id]
        updated = dict(row)
        qualifiers = dict(row.get("qualifiers", {}))
        qualifiers["relation_candidate"] = flag
        qualifiers["relation_candidate_note"] = note
        updated["qualifiers"] = qualifiers
        replacements[statement_id] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if set(replacements) != set(TARGETS):
        raise SystemExit("replacement target set mismatch")

    pieces = []
    for row, start, end in parsed:
        data = replacements.get(row.get("statement_id"))
        if data is None:
            pieces.append(raw[start:end])
        else:
            newline = b"\r\n" if raw[start:end].endswith(b"\r\n") else b"\n"
            pieces.append(data + newline)
    projected = b"".join(pieces)
    projected_rows = [r for r, _, _ in read_jsonl(projected)]
    after = stats(projected_rows)
    if after != EXPECTED_AFTER:
        raise SystemExit(f"unexpected projected counts: {after}")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT,
        "printed_page": 67,
        "segment_statements": len(segment_rows),
        "new_relation_candidates": sum(spec[0] for spec in TARGETS.values()),
        "new_nonrelations": sum(not spec[0] for spec in TARGETS.values()),
        "new_open_endpoint_candidates": sum(
            spec[0] and not (has_endpoint(spec[4]) and has_endpoint(spec[5]))
            for spec in TARGETS.values()
        ),
        "before": before,
        "after": after,
        "changed_ids": sorted(TARGETS),
        "backup": str(BACKUP.relative_to(ROOT)) if args.apply else None,
    }, ensure_ascii=False, indent=2))
    if args.dry_run:
        return

    shutil.copy2(STATEMENTS, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix="book-statements.s2-chp3-secii-l19-31.", suffix=".tmp", dir=TABLES)
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

    written_rows = [r for r, _, _ in read_jsonl(STATEMENTS.read_bytes())]
    verified = stats(written_rows)
    if verified != EXPECTED_AFTER:
        raise SystemExit(f"post-write count mismatch: {verified}; recovery backup retained")
    for row in written_rows:
        if row.get("statement_id") not in TARGETS:
            continue
        flag, note, *_ = TARGETS[row["statement_id"]]
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is not flag or q.get("relation_candidate_note") != note:
            raise SystemExit(f"post-write classification mismatch: {row['statement_id']}; recovery backup retained")
    print(f"post_write_sha256={sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
