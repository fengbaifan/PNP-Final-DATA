from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_i.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-3.pdf"
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l16-24"
BACKUP_STATEMENTS = TABLES / "book-statements.jsonl.bak-s2-chp3-sec-i-l16-24-20261010"
BACKUP_MENTIONS = TABLES / "mentions.csv.bak-s2-chp3-sec-i-l16-24-20261010"
EXPECTED_HASHES = {
    "table": "5bca89bad9f43a91ca253a9bb495d06399ec7d1da50e421370ccaea18d14e89f",
    "candidates": "1de62da6b601a36870a3c59f6f892d11fcd67eff0adcaf732d3eed4470b61a92",
    "mentions": "a2b3f66e5387732c6cdc66a7c9f3d36ac6737db6c76b40a7c3a5a7864477e800",
    "coverage": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "source": "a18f48c7b8bf5b161fa13a7ce26ed2935e72d9a14d555f82dfc1d85f84314255",
    "pdf": "362e08518334ae5cda65cc1758f92ef4de6874b5982bfb6600187d889dc6785d",
}
TARGET_IDS = {
    "st-chp3-seci-l16-24-antonio-benefactor",
    "st-chp3-seci-l16-24-antonio-had-occasion-recorded",
    "st-chp3-seci-l16-24-barberini-family-sympathies",
    "st-chp3-seci-l16-24-bentivoglio-advised",
    "st-chp3-seci-l16-24-canonisation-occasion-paintings",
    "st-chp3-seci-l16-24-church-building-dependent-on-families",
    "st-chp3-seci-l16-24-gregory-nephew-educated",
    "st-chp3-seci-l16-24-haskell-disputes-rubens-attribution",
    "st-chp3-seci-l16-24-jesuits-delayed-church-decoration",
    "st-chp3-seci-l16-24-jesuits-published-imago",
    "st-chp3-seci-l16-24-ludovico-educated",
    "st-chp3-seci-l16-24-oliva-friend-bernini",
    "st-chp3-seci-l16-24-orat-caravaggio",
    "st-chp3-seci-l16-24-orders-social-integration",
    "st-chp3-seci-l16-24-ottonelli-advocated-cortona-claims",
    "st-chp3-seci-l16-24-ottonelli-coauthored-treatise",
    "st-chp3-seci-l16-24-paintings-main-text-vandyck",
    "st-chp3-seci-l16-24-paulv-friendly-jesuits",
    "st-chp3-seci-l16-24-philip-neri-founder-oratorians",
    "st-chp3-seci-l16-24-puyvelde-rubens-attribution",
    "st-chp3-seci-l16-24-sacchi-picture-maker",
    "st-chp3-seci-l16-24-urban-published-bull",
    "st-chp3-seci-l16-24-urban-similar-policy",
    "st-chp3-seci-l16-24-urban-sympathies-orders",
    "st-chp3-seci-l16-24-urban-visits-gesu",
    "st-chp3-seci-l16-24-vandyck-in-rome",
}
EXPECTED_ENDPOINTS = {
    "st-chp3-seci-l16-24-orders-social-integration": ("cand-1321", "cand-2114"),
    "st-chp3-seci-l16-24-church-building-dependent-on-families": ("cand-1321", "cand-4984"),
    "st-chp3-seci-l16-24-paintings-main-text-vandyck": ("cand-4977", "cand-0960"),
    "st-chp3-seci-l16-24-puyvelde-rubens-attribution": ("cand-4976", "cand-2293"),
    "st-chp3-seci-l16-24-vandyck-in-rome": ("cand-0960", "cand-4490"),
}
ENDPOINT_OVERRIDES = {
    "st-chp3-seci-l16-24-orders-social-integration": ("cand-2114", None),
    "st-chp3-seci-l16-24-church-building-dependent-on-families": ("cand-2114", "cand-4984"),
    "st-chp3-seci-l16-24-paintings-main-text-vandyck": ("cand-4977", "cand-0958"),
    "st-chp3-seci-l16-24-puyvelde-rubens-attribution": ("cand-4977", "cand-2293"),
    "st-chp3-seci-l16-24-vandyck-in-rome": ("cand-0958", "cand-4490"),
}
NOTES = {
    "st-chp3-seci-l16-24-antonio-benefactor": (
        "Haskell explicitly calls Antonio Barberini a special benefactor of the Society of Jesus. "
        "Keep this source-attributed role; do not infer a particular donation or commission."
    ),
    "st-chp3-seci-l16-24-antonio-had-occasion-recorded": (
        "The source says Antonio had one of Urban VIII's visits recorded in a picture. "
        "Record the pictorial commemoration without inferring a contract or changing the separate painter attribution."
    ),
    "st-chp3-seci-l16-24-barberini-family-sympathies": (
        "Haskell attributes strong sympathies with the Orders, especially the Jesuits, to Urban VIII's family collectively. "
        "Do not assign the claim to unnamed individual family members."
    ),
    "st-chp3-seci-l16-24-bentivoglio-advised": (
        "This records a reported recommendation that Bentivoglio contact the Oratorians. "
        "The adviser is unnamed; the source does not say Bentivoglio followed the advice or met them."
    ),
    "st-chp3-seci-l16-24-canonisation-occasion-paintings": (
        "The source says ceremonies and commissions of paintings of the two Jesuit saints followed the canonisation occasion. "
        "Do not infer that the paintings depicted Philip Neri or identify a commissioner here."
    ),
    "st-chp3-seci-l16-24-church-building-dependent-on-families": (
        "The antecedent is the Jesuits and other religious Orders collectively; use the group-level Orders candidate, "
        "not Jesuits alone. Haskell says church building depended on powerful Roman families; their members and any contracts remain unspecified."
    ),
    "st-chp3-seci-l16-24-gregory-nephew-educated": (
        "Haskell says Gregory XV had been educated by the Jesuits. Preserve this as the book's historical claim without adding dates or institutions."
    ),
    "st-chp3-seci-l16-24-haskell-disputes-rubens-attribution": (
        "Haskell disputes van Puyvelde's attribution by citing the absence of documentary evidence and reasons for doubt. "
        "This records Haskell's assessment; it does not establish the Van Dyck attribution."
    ),
    "st-chp3-seci-l16-24-jesuits-delayed-church-decoration": (
        "Haskell says the Jesuits waited decades before progress on decorating their own churches. "
        "Retain the group and duration; do not identify a specific church from nearby examples."
    ),
    "st-chp3-seci-l16-24-jesuits-published-imago": (
        "The source identifies the Antwerp Jesuits as publishers of Imago primi saeculi for the centenary. "
        "Haskell's judgment about its self-satisfaction remains a separate evaluation."
    ),
    "st-chp3-seci-l16-24-ludovico-educated": (
        "The pronoun refers to Gregory XV's nephew, identified in the existing candidate as Ludovico Ludovisi. "
        "Keep the identification source-bound and preserve the education claim as reported."
    ),
    "st-chp3-seci-l16-24-oliva-friend-bernini": (
        "Haskell describes Oliva as one of Bernini's closest and most influential friends. "
        "Preserve the superlative as the author's characterization, not a quantified ranking."
    ),
    "st-chp3-seci-l16-24-orat-caravaggio": (
        "The claim is explicitly reported as a suggestion and says the Oratorians may have encouraged Caravaggio's religious painting. "
        "Retain the hedge; do not recast this as a confirmed commission."
    ),
    "st-chp3-seci-l16-24-orders-social-integration": (
        "The passage treats the Jesuits and other religious Orders collectively as integrated into the fabric of society. "
        "Keep the subject group-level and the society object open because no bounded society candidate is present; "
        "preserve the counterfactual 'even had that been their intention' and do not substitute the Papal court or a narrower art-and-society term."
    ),
    "st-chp3-seci-l16-24-ottonelli-advocated-cortona-claims": (
        "The source says Ottonelli pressed Cortona's claims on the Barberini during palace decoration. "
        "This is advocacy in a patronage context, not proof that the family accepted a specific contract."
    ),
    "st-chp3-seci-l16-24-ottonelli-coauthored-treatise": (
        "The source says Ottonelli wrote the treatise in collaboration with Pietro da Cortona, whose candidate remains in coauthor_candidate_id. "
        "Preserve the note linkage and do not infer further editions or independent authorship verification."
    ),
    "st-chp3-seci-l16-24-paintings-main-text-vandyck": (
        "The main text identifies the two paintings as by the person Anthony van Dyck; the footnote records a competing Rubens attribution. "
        "Use the person candidate rather than a same-name work candidate and retain both claims as source-specific."
    ),
    "st-chp3-seci-l16-24-paulv-friendly-jesuits": (
        "Haskell explicitly says Paul V was friendly with the Jesuits. "
        "Do not extend the statement to a specific policy or date."
    ),
    "st-chp3-seci-l16-24-philip-neri-founder-oratorians": (
        "The passage identifies Philip Neri as founder of the Oratorians in the canonisation context. "
        "Preserve the source's identification without adding institutional history."
    ),
    "st-chp3-seci-l16-24-puyvelde-rubens-attribution": (
        "Van Puyvelde's reported claim concerns the two Vatican paintings as subject and Rubens as proposed painter; "
        "Van Puyvelde is the speaker/source, not the attributed object. Haskell immediately disputes the claim. "
        "Retain the proposed 1608 date and source attribution without asserting either as fact."
    ),
    "st-chp3-seci-l16-24-sacchi-picture-maker": (
        "Haskell attributes the picture recording one of the Gesù visits to Andrea Sacchi. "
        "The title and exact version remain unspecified."
    ),
    "st-chp3-seci-l16-24-urban-published-bull": (
        "The source says Urban VIII published a bull of canonisation. "
        "The clause does not restate which persons were canonised; preserve that local scope."
    ),
    "st-chp3-seci-l16-24-urban-similar-policy": (
        "Haskell compares Urban VIII's policy with Gregory XV's as 'much the same'. "
        "This is a source-level comparison; do not infer identical acts or a formal relation between the popes."
    ),
    "st-chp3-seci-l16-24-urban-sympathies-orders": (
        "Haskell attributes sympathies with the Orders, especially the Jesuits, to Urban VIII and his family. "
        "Preserve the collective and authorial scope."
    ),
    "st-chp3-seci-l16-24-urban-visits-gesu": (
        "The source dates Urban VIII's two visits to the Gesù to 1639 and 1640 during the statutes' centenary celebrations. "
        "Retain both dates and the stated context."
    ),
    "st-chp3-seci-l16-24-vandyck-in-rome": (
        "The source says Anthony van Dyck was in Rome at the time of the occasion, without an exact date. "
        "Map the person mention to the person candidate, not the same-name work candidate."
    ),
}
MENTION_ID = "m-chp3-seci-l16-24-0022"
OLD_MENTION = (
    b"m-chp3-seci-l16-24-0022,chp-3:03_CHP-3_sec_i:l16-24,cand-0960,Van Dyck,843,851,"
    b"Artist named as the painter in the main text; footnote 3 records a disputed attribution."
)
NEW_MENTION = OLD_MENTION.replace(b",cand-0960,", b",cand-0958,")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def read_jsonl(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    decoded = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in decoded else "\n"
    rows = [json.loads(line) for line in decoded.splitlines() if line.strip()]
    return rows, bom, newline


def serialize_jsonl(rows, bom: bool, newline: str) -> bytes:
    text = newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows
    ) + newline
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def relation_counts(rows):
    bilateral = [
        row for row in rows
        if row.get("subject_candidate_id") and row.get("object_candidate_id")
    ]
    true_bilateral = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        for row in bilateral
    )
    false_bilateral = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is False
        for row in bilateral
    )
    pending = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is None
        for row in bilateral
    )
    true_total = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        for row in rows
    )
    open_true = sum(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and not (row.get("subject_candidate_id") and row.get("object_candidate_id"))
        for row in rows
    )
    return {
        "bilateral": len(bilateral),
        "classified_relation": true_bilateral,
        "classified_nonrelation": false_bilateral,
        "pending": pending,
        "relation_candidates_total": true_total,
        "relation_candidates_open": open_true,
    }


def preflight():
    paths = {
        "table": STATEMENTS,
        "candidates": CANDIDATES,
        "mentions": MENTIONS,
        "coverage": COVERAGE,
        "source": SOURCE,
        "pdf": PDF,
    }
    actual = {name: sha256(path) for name, path in paths.items()}
    if actual != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: expected={EXPECTED_HASHES}; actual={actual}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as handle:
        coverage = [
            row for row in csv.DictReader(handle)
            if row.get("segment_id") == SEGMENT_ID
        ]
    if (
        len(coverage) != 1
        or coverage[0].get("disposition") != "reviewed"
        or coverage[0].get("migration_status") != "complete"
    ):
        raise SystemExit(f"coverage preflight failed: {coverage}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidates = {row["candidate_id"]: row for row in csv.DictReader(handle)}
    type_expectations = {
        "cand-0958": "person",
        "cand-0960": "work",
        "cand-2114": "term",
        "cand-2293": "person",
        "cand-4976": "person",
        "cand-4977": "work",
        "cand-4984": "term",
    }
    for candidate_id, expected_type in type_expectations.items():
        candidate = candidates.get(candidate_id)
        if not candidate or candidate.get("suggested_type") != expected_type:
            raise SystemExit(f"candidate type preflight failed: {candidate_id}")
    if candidates["cand-0958"]["canonical_name"] != "Dyck, Sir Anthony Van":
        raise SystemExit("Van Dyck person candidate identity changed")
    if candidates["cand-4977"]["canonical_name"] != (
        "Two paintings of St Ignatius and St Francis Xavier in the Vatican (attribution disputed)"
    ):
        raise SystemExit("Vatican painting-pair candidate identity changed")

    raw_mentions = MENTIONS.read_bytes()
    if raw_mentions.count(OLD_MENTION) != 1:
        raise SystemExit("Van Dyck mention row changed or is not unique")
    if BACKUP_STATEMENTS.exists() or BACKUP_MENTIONS.exists():
        raise SystemExit("a recovery backup path already exists")

    rows, bom, newline = read_jsonl(STATEMENTS)
    selected = [row for row in rows if row.get("segment_id") == SEGMENT_ID]
    by_id = {row.get("statement_id"): row for row in selected}
    pending = {
        row["statement_id"]
        for row in selected
        if row.get("subject_candidate_id")
        and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if pending != TARGET_IDS:
        raise SystemExit(
            f"pending statement scope changed: missing={TARGET_IDS-pending}; unexpected={pending-TARGET_IDS}"
        )
    for statement_id, endpoints in EXPECTED_ENDPOINTS.items():
        row = by_id[statement_id]
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise SystemExit(f"expected endpoint state changed: {statement_id}")
    for statement_id in TARGET_IDS:
        row = by_id[statement_id]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
            raise SystemExit(f"invalid source line anchor: {statement_id}")
        anchor = normalize("\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[start - 1:end]))
        if normalize(row.get("original_quote", "")) not in anchor:
            raise SystemExit(f"source quote does not match line anchor: {statement_id}")

    before_counts = relation_counts(rows)
    expected_before = {
        "bilateral": 8500,
        "classified_relation": 4491,
        "classified_nonrelation": 459,
        "pending": 3550,
        "relation_candidates_total": 4521,
        "relation_candidates_open": 30,
    }
    if before_counts != expected_before:
        raise SystemExit(f"unexpected relation counts before write: {before_counts}")

    projected = []
    for current in rows:
        if current.get("statement_id") not in TARGET_IDS:
            projected.append(current)
            continue
        updated = dict(current)
        if current["statement_id"] in ENDPOINT_OVERRIDES:
            updated["subject_candidate_id"], updated["object_candidate_id"] = ENDPOINT_OVERRIDES[current["statement_id"]]
        q = dict(updated.get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = NOTES[current["statement_id"]]
        if current["statement_id"] == "st-chp3-seci-l16-24-orders-social-integration":
            q["mentioned_candidate_ids"] = ["cand-1321", "cand-2114"]
        elif current["statement_id"] == "st-chp3-seci-l16-24-church-building-dependent-on-families":
            q["mentioned_candidate_ids"] = ["cand-2114", "cand-4984"]
        elif current["statement_id"] == "st-chp3-seci-l16-24-puyvelde-rubens-attribution":
            q["mentioned_candidate_ids"] = ["cand-4977", "cand-2293", "cand-4976"]
        elif current["statement_id"] == "st-chp3-seci-l16-24-paintings-main-text-vandyck":
            q["mentioned_candidate_ids"] = ["cand-4977", "cand-0958"]
        updated["qualifiers"] = q
        projected.append(updated)

    after_counts = relation_counts(projected)
    expected_after = {
        "bilateral": 8499,
        "classified_relation": 4516,
        "classified_nonrelation": 459,
        "pending": 3524,
        "relation_candidates_total": 4547,
        "relation_candidates_open": 31,
    }
    if after_counts != expected_after:
        raise SystemExit(f"unexpected projected relation counts: {after_counts}")
    return rows, projected, bom, newline, raw_mentions, actual, before_counts, after_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows, projected, bom, newline, raw_mentions, hashes, before, after = preflight()
    preview = []
    for statement_id in sorted(TARGET_IDS):
        current = next(row for row in rows if row.get("statement_id") == statement_id)
        new = next(row for row in projected if row.get("statement_id") == statement_id)
        preview.append({
            "statement_id": statement_id,
            "predicate": current.get("predicate"),
            "old_endpoints": [current.get("subject_candidate_id"), current.get("object_candidate_id")],
            "new_endpoints": [new.get("subject_candidate_id"), new.get("object_candidate_id")],
            "relation_candidate": True,
            "relation_candidate_note": NOTES[statement_id],
        })
    if args.dry_run:
        print(json.dumps({
            "preflight": "passed",
            "hashes": hashes,
            "mention_change": {
                "mention_id": MENTION_ID,
                "old_candidate_id": "cand-0960",
                "new_candidate_id": "cand-0958",
            },
            "changes": preview,
            "counts_before": before,
            "counts_after": after,
        }, ensure_ascii=False, indent=2))
        return

    statement_temp = STATEMENTS.with_suffix(STATEMENTS.suffix + ".s2tmp")
    mention_temp = MENTIONS.with_suffix(MENTIONS.suffix + ".s2tmp")
    if statement_temp.exists() or mention_temp.exists():
        raise SystemExit("temporary output path already exists")
    projected_mentions = raw_mentions.replace(OLD_MENTION, NEW_MENTION)
    if projected_mentions == raw_mentions:
        raise SystemExit("mention mapping replacement produced no change")
    shutil.copy2(STATEMENTS, BACKUP_STATEMENTS)
    shutil.copy2(MENTIONS, BACKUP_MENTIONS)
    statement_temp.write_bytes(serialize_jsonl(projected, bom, newline))
    mention_temp.write_bytes(projected_mentions)
    statement_temp.replace(STATEMENTS)
    mention_temp.replace(MENTIONS)

    written_rows, _, _ = read_jsonl(STATEMENTS)
    verified_counts = relation_counts(written_rows)
    written_target = {
        row["statement_id"]: row
        for row in written_rows
        if row.get("statement_id") in TARGET_IDS
    }
    if len(written_target) != len(TARGET_IDS):
        raise SystemExit("post-write target count verification failed; backups preserved")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not True for row in written_target.values()):
        raise SystemExit("post-write relation flag verification failed; backups preserved")
    if verified_counts != after:
        raise SystemExit(f"post-write relation counts differ: {verified_counts}; backups preserved")
    verified_mentions = MENTIONS.read_bytes()
    if verified_mentions.count(NEW_MENTION) != 1 or verified_mentions.count(OLD_MENTION) != 0:
        raise SystemExit("post-write Van Dyck mention verification failed; backups preserved")
    print(json.dumps({
        "applied": len(TARGET_IDS),
        "backups": [str(BACKUP_STATEMENTS.relative_to(ROOT)), str(BACKUP_MENTIONS.relative_to(ROOT))],
        "before_sha256": hashes,
        "after_sha256": {"table": sha256(STATEMENTS), "mentions": sha256(MENTIONS)},
        "verified_counts": verified_counts,
        "verified_mention": MENTION_ID,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
