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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-i-l26-33-relations-20261010"
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l26-33"

EXPECTED_HASHES = {
    STATEMENTS: "4184ffe5eaa5af23a51d81ecb7c01c0274b62506a07aeca3bfd5f5e219dc2435",
    CANDIDATES: "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    COVERAGE: "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    SOURCE: "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255",
    PDF: "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}

DECISIONS = {
    "st-chp3-seci-l26-33-aristocracy-expropriation-right": (
        True,
        "Haskell reports that the rich aristocracy was given this right to encourage Rome's reconstruction. The granting authority, statute, and individual neighbours are not identified; preserve the source attribution and do not treat the cited legal account as independently verified.",
    ),
    "st-chp3-seci-l26-33-bernini-jesuit-association": (
        True,
        "The source says both Bernini and Pietro da Cortona were closely associated with the Jesuits; this scalar statement records Bernini. Association does not imply a Gesu commission, and the following sentence separately says he produced nothing significant for that church during Urban VIII's reign.",
    ),
    "st-chp3-seci-l26-33-bernini-no-significant-gesu-work": (
        True,
        "Retain Haskell's period limitation to Urban VIII's reign and the qualified phrase 'nothing significant'; this does not claim Bernini did no work of any kind for the Gesu.",
    ),
    "st-chp3-seci-l26-33-churches-dialectic-spiritual-moneyed-patrons": (
        True,
        "This is Haskell's interpretive relation between religious-order church decoration and two general patron types: saint-founded spiritual authority and money. The moneyed-family candidate represents only one pole; do not infer a named patron, ownership, or a specific commission.",
    ),
    "st-chp3-seci-l26-33-cortona-jesuit-association": (
        True,
        "The source says both Bernini and Pietro da Cortona were closely associated with the Jesuits; this scalar statement records Cortona. Association does not imply a Gesu commission, and the following sentence separately says he produced nothing significant for that church during Urban VIII's reign.",
    ),
    "st-chp3-seci-l26-33-cortona-no-significant-gesu-work": (
        True,
        "Retain Haskell's period limitation to Urban VIII's reign and the qualified phrase 'nothing significant'; this does not claim Cortona did no work of any kind for the Gesu.",
    ),
    "st-chp3-seci-l26-33-dispossess-religious-institutions": (
        True,
        "Haskell says the aristocracy was allowed to dispossess unnamed, uncooperative religious institutions. Keep the collective endpoint and source attribution; do not identify a particular order or infer an independently verified legal instrument.",
    ),
    "st-chp3-seci-l26-33-duchess-turin-not-prevented": (
        True,
        "This records the Duchess of Savoy's reported belief that Ferri's existing engagements would not prevent him coming to Turin. It does not say that Ferri travelled, accepted the job, or completed work there.",
    ),
    "st-chp3-seci-l26-33-duchess-wanted-ciro-ferri": (
        True,
        "Haskell reports the Duchess's desire to employ Ferri for an unspecified job. Preserve this as intention, not a completed commission or work; her personal identity is not supplied here.",
    ),
    "st-chp3-seci-l26-33-families-superiority-legal-financial": (
        True,
        "This continues p.64's statement that the ruling families' superiority was assured by legal and financial forces. Those forces are generic and not identified as a single entity; leave the object open rather than reducing the claim to the expropriation right alone.",
    ),
    "st-chp3-seci-l26-33-ferri-engagements-with-nuns": (
        True,
        "This is the Duchess's quoted characterization of Ferri's engagements. The nun communities and work are unnamed; do not infer formal commissions, Ferri's departure, or completed employment.",
    ),
    "st-chp3-seci-l26-33-first-class-artists-scarcity": (
        False,
        "This is Haskell's explanatory premise about the limited number of first-class artists, not a relation between two identifiable entities. Retain the statement without inventing endpoints.",
    ),
    "st-chp3-seci-l26-33-intense-patronage-opportunity-venues": (
        True,
        "Haskell generalizes that intense papal and court patronage limited many great artists' opportunities outside a small set of venues. Preserve 'few', 'as long as', and the generic family-palace/titular-church wording; the Churches candidate captures only the church part of the venue list, and no specific commission is asserted.",
    ),
    "st-chp3-seci-l26-33-method-study-periods": (
        False,
        "This is Haskell's methodological recommendation to study the churches before, during, and after Urban VIII's reign; it does not assert a historical relation between the church group and the Pope.",
    ),
    "st-chp3-seci-l26-33-order-patronage-affected-by-tendency": (
        True,
        "Haskell links religious-order patronage to the preceding aristocratic legal and financial tendency. The expropriation-right candidate captures the described legal aspect; preserve the broader source scope and do not infer a named statute or a particular order.",
    ),
    "st-chp3-seci-l26-33-orders-call-great-artists-after-source-dries": (
        True,
        "This is a conditional capacity claim, not a report of specific commissions: Haskell says orders, especially the Jesuits, could call on great artists only when the dominant papal/court patronage source temporarily dried up.",
    ),
    "st-chp3-seci-l26-33-papal-court-patronage-personal-channels": (
        True,
        "This records Haskell's broad comparison between papal/court patronage through personal channels and religious-order churches. Preserve 'on the whole', 'mainly', and the authorial characterization; it does not identify a specific patron, employment, or ownership relation.",
    ),
    "st-chp3-seci-l26-33-church-decoration-synthesis": (
        True,
        "Haskell says the decoration depended on a synthesis of conflicting forces, but the object is expressed as an unspecified combination, not a single identified entity. Keep the relation candidate open and do not select one patron or church from the preceding examples.",
    ),
    "st-chp3-seci-l26-33-secular-princes-claims-first": (
        True,
        "Haskell says secular princes' claims took precedence, but this sentence does not identify the competing claims or artists. Keep the object open; the Duchess's following example does not make her the exhaustive target of the generalization.",
    ),
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
        r for r in rows
        if has_endpoint(r.get("subject_candidate_id")) and has_endpoint(r.get("object_candidate_id"))
    ]
    relation_true = [r for r in rows if qualifiers(r).get("relation_candidate") is True]
    categories = Counter(
        "true" if qualifiers(r).get("relation_candidate") is True
        else "false" if qualifiers(r).get("relation_candidate") is False
        else "pending"
        for r in bilateral
    )
    open_true = sum(
        not (has_endpoint(r.get("subject_candidate_id")) and has_endpoint(r.get("object_candidate_id")))
        for r in relation_true
    )
    return {
        "bilateral": len(bilateral),
        "bilateral_true": categories["true"],
        "bilateral_false": categories["false"],
        "bilateral_pending": categories["pending"],
        "relation_candidates_total": len(relation_true),
        "relation_candidates_open": open_true,
    }


def read_jsonl_lines(raw: bytes) -> list[tuple[dict, bytes, bytes]]:
    result = []
    for line in raw.splitlines(keepends=True):
        body = line.rstrip(b"\r\n")
        ending = line[len(body):]
        row = json.loads(body.decode("utf-8-sig"))
        result.append((row, ending, body))
    return result


def projected_bytes(raw: bytes, rows: list[tuple[dict, bytes]]) -> tuple[bytes, dict[str, dict]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    out = bytearray()
    changed = {}
    for index, (row, ending, original_body) in enumerate(rows):
        if row.get("statement_id") in DECISIONS:
            q = qualifiers(row)
            flag, note = DECISIONS[row["statement_id"]]
            if "relation_candidate" in q:
                raise SystemExit(f"target already classified: {row['statement_id']}")
            q["relation_candidate"] = flag
            q["relation_candidate_note"] = note
            row["qualifiers"] = q
            changed[row["statement_id"]] = q
            encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            out.extend(encoded)
            out.extend(ending)
        else:
            out.extend(original_body)
            out.extend(ending)
    return bytes(out), changed


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
        cover = [r for r in csv.DictReader(handle) if r["segment_id"] == SEGMENT_ID]
    if len(cover) != 1 or cover[0]["disposition"] != "reviewed" or cover[0]["migration_status"] != "complete":
        raise SystemExit(f"unexpected S2 coverage row: {cover}")
    if cover[0]["source_line_ranges"] != "L27-33":
        raise SystemExit(f"unexpected source range: {cover[0]['source_line_ranges']}")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidates = {r["candidate_id"] for r in csv.DictReader(handle)}
    raw = STATEMENTS.read_bytes()
    lines = read_jsonl_lines(raw)
    table_rows = [r for r, _, _ in lines]
    segment_rows = [r for r in table_rows if r.get("segment_id") == SEGMENT_ID]
    target_rows = {r["statement_id"]: r for r in segment_rows if r.get("statement_id") in DECISIONS}
    if set(target_rows) != set(DECISIONS):
        raise SystemExit(f"target ID mismatch: found={sorted(target_rows)}")
    if len(segment_rows) != 19:
        raise SystemExit(f"unexpected statement count in segment: {len(segment_rows)}")
    for row in target_rows.values():
        if "relation_candidate" in qualifiers(row):
            raise SystemExit(f"target already classified: {row['statement_id']}")
        for endpoint in (row.get("subject_candidate_id"), row.get("object_candidate_id")):
            if has_endpoint(endpoint) and endpoint not in candidates:
                raise SystemExit(f"unresolved candidate endpoint {endpoint} in {row['statement_id']}")

    before = stats(table_rows)
    expected_before = {
        "bilateral": 8499,
        "bilateral_true": 4516,
        "bilateral_false": 459,
        "bilateral_pending": 3524,
        "relation_candidates_total": 4547,
        "relation_candidates_open": 31,
    }
    if before != expected_before:
        raise SystemExit(f"unexpected pre-write counts: {before}")

    projected, changed = projected_bytes(raw, lines)
    projected_rows = [r for r, _, _ in read_jsonl_lines(projected)]
    after = stats(projected_rows)
    expected_after = {
        "bilateral": 8499,
        "bilateral_true": 4530,
        "bilateral_false": 460,
        "bilateral_pending": 3509,
        "relation_candidates_total": 4564,
        "relation_candidates_open": 34,
    }
    if len(changed) != len(DECISIONS) or after != expected_after:
        raise SystemExit(f"unexpected projected result: changed={len(changed)} counts={after}")

    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "segment_id": SEGMENT_ID,
        "statement_classifications": {
            "relation_candidates": sum(flag for flag, _ in DECISIONS.values()),
            "nonrelations": sum(not flag for flag, _ in DECISIONS.values()),
            "with_open_endpoint": sum(
                flag and not (has_endpoint(target_rows[sid].get("subject_candidate_id")) and has_endpoint(target_rows[sid].get("object_candidate_id")))
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
    fd, temp_name = tempfile.mkstemp(prefix="book-statements.s2-l26-33.", suffix=".tmp", dir=TABLES)
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

    written_rows = [r for r, _, _ in read_jsonl_lines(STATEMENTS.read_bytes())]
    written_targets = {r["statement_id"]: r for r in written_rows if r.get("statement_id") in DECISIONS}
    if set(written_targets) != set(DECISIONS):
        raise SystemExit("post-write target set changed; recovery backup retained")
    for sid, (flag, note) in DECISIONS.items():
        q = qualifiers(written_targets[sid])
        if q.get("relation_candidate") is not flag or q.get("relation_candidate_note") != note:
            raise SystemExit(f"post-write classification mismatch: {sid}; recovery backup retained")
    verified = stats(written_rows)
    if verified != expected_after:
        raise SystemExit(f"post-write counts mismatch: {verified}; recovery backup retained")
    print(f"post_write_sha256={sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
