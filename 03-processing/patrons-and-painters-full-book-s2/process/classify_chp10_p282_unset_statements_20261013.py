from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SEGMENT = "chp-10:10_CHP-10_intro:l141-149"
TARGETS = {
    "st-chp10-p282-wilhelm-love-of-glory",
    "st-chp10-p282-wilhelm-political-influence",
    "st-chp10-p282-rapparini-aesthetic-theory",
    "st-chp10-p282-rapparini-eclectic-taste",
}
NEW_CANDIDATE = "cand-11970"
NEW_MENTION = "m-chp10-p282-artists-adulation-group"
EXPECTED_HASHES = {
    STATEMENTS: "712125fe8dd1bee3630c14fd284af78cafb8e9b9a42c4731744fd607d4d60342",
    CANDIDATES: "e9309ec1f73a0d2e2c264cc779b2631bcd10674eb0485a7e0f5a6e1199685031",
    MENTIONS: "b886c50229ba5b5749ef17ae6b42dddd0688ca671c6ac1cb5ce7448b2ec9d695",
    COVERAGE: "97df8627c8f2f4ca6a51f6d4782b476bc5ff71bbadb3f9ec13a523d12ee90496",
}
SOURCE_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEGMENT_SHA256 = "813500dc1bffa25162b5ff929a4545f93048788e5a6a3cd4bad430c8428b7450"
BACKUP_SUFFIX = ".bak-s2-chp10-p282-unset-classification-20261013"
FALSE_NOTE = "This is a source-attributed biographical, theoretical, or evaluative statement, not a relation between distinct represented entities."
TRUE_NOTE = (
    "Haskell explicitly describes adulation by this unnamed artist group toward Johann Wilhelm. "
    "His interpretation that the adulation reflected Wilhelm's love of glory remains part of the claim; "
    "the group is not equated with the artists attracted to German courts at p.278."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized(text: str) -> str:
    return " ".join(text.split())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader), raw.startswith(b"\xef\xbb\xbf")


def csv_bytes(fields: list[str], rows: list[dict[str, str]], bom: bool) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    os.replace(temp, path)


def build_outputs() -> tuple[dict[Path, bytes], dict[str, object]]:
    raw = {path: path.read_bytes() for path in EXPECTED_HASHES}
    for path, expected in EXPECTED_HASHES.items():
        if sha256(raw[path]) != expected:
            raise SystemExit(f"input SHA mismatch: {path.relative_to(ROOT)}")
    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")

    lines = source_bytes.decode("utf-8-sig").splitlines()
    segment_text = "\n".join(lines[140:149])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("p.282 segment SHA mismatch")

    statements = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements):
        raise SystemExit("duplicate statement IDs in input")
    target_rows = {sid for sid, row in by_id.items()
                   if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("relation_candidate") is None}
    if target_rows != TARGETS:
        raise SystemExit(f"p.282 unset target set changed: {sorted(target_rows)}")

    cfields, candidates, cbom = read_csv(CANDIDATES)
    mfields, mentions, mbom = read_csv(MENTIONS)
    covfields, coverage, covbom = read_csv(COVERAGE)
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if NEW_CANDIDATE in candidate_ids or NEW_MENTION in mention_ids:
        raise SystemExit("planned candidate or mention ID already exists")
    numeric_ids = [int(row["candidate_id"].split("-")[1]) for row in candidates
                   if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()]
    if max(numeric_ids) != 11969:
        raise SystemExit(f"candidate sequence changed: max={max(numeric_ids)}")
    coverage_by_id = {row["segment_id"]: row for row in coverage}
    segment_coverage = coverage_by_id.get(SEGMENT)
    if not segment_coverage or (segment_coverage["disposition"], segment_coverage["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"unexpected p.282 coverage state: {segment_coverage}")

    quotes = {
        "st-chp10-p282-wilhelm-love-of-glory": "His love of glory-was reflected in the adulation of the artists who surrounded him.",
        "st-chp10-p282-wilhelm-political-influence": "For some years between 1708 and 1714 he achieved unparalleled influence in German politics",
        "st-chp10-p282-rapparini-aesthetic-theory": "Une austère régularité de l’Art rebutte les Amateurs memes de l’Art.\nSi le Peintre ne montre point au dehors quelque agrément de facilité, qui attire au plaisir d’imiter en cachant le dificile, on en décourage le Sectateur qui s’en va ailleurs.\nLa Science vraiment de plaire à l’oeil materiel, consiste surtout dans le cromatique, c’est à dire dans le coloris. Sans ce charme mignon la Peinture perd trop de sa force, et n’a plus cette magie d’enchanter. Il faut égayer parci, parla son Tableau par une manière riante, qui régné d’un bout à l’autre de la Pièce.’",
        "st-chp10-p282-rapparini-eclectic-taste": "In his writings Rapparini shows himself so anxious to give unqualified praise to everyone that his taste can only be described as eclectic.",
    }
    for sid, quote in quotes.items():
        row = by_id[sid]
        q = row.get("qualifiers", {})
        if row.get("source_file") != "02-sources/02-Markdown/10_CHP-10_intro.md" or row.get("segment_id") != SEGMENT:
            raise SystemExit(f"unexpected source mapping: {sid}")
        span = " ".join(lines[q["source_line_start"] - 1:q["source_line_end"]])
        if normalized(quote) not in normalized(span) or normalized(quote) != normalized(row.get("original_quote", "")):
            raise SystemExit(f"source/original quote mismatch: {sid}")

    surface = "artists who surrounded him"
    occurrences = [at for at in range(len(segment_text)) if segment_text.startswith(surface, at)]
    if len(occurrences) != 1:
        raise SystemExit(f"unexpected artist-group surface count: {len(occurrences)}")
    start = occurrences[0]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit("mention span mismatch")

    new_candidate = {
        "candidate_id": NEW_CANDIDATE,
        "index_entry_id": "",
        "canonical_name": "Artists surrounding Johann Wilhelm in Haskell’s p.282 account (unnamed group)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": (
            "Unnamed artists whom Haskell says surrounded Johann Wilhelm and whose adulation reflected his love of glory. "
            "Members, number, and individual identities are not supplied. This group is kept distinct from cand-8854, "
            "the artists attracted to German courts in the p.278 account."
        ),
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L142",
    }
    new_mention = {
        "mention_id": NEW_MENTION,
        "segment_id": SEGMENT,
        "candidate_id": NEW_CANDIDATE,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": "Source-defined unnamed group; membership is not specified and it is not merged with the p.278 artist group.",
    }

    decisions = {
        "st-chp10-p282-wilhelm-love-of-glory": (True, "artists_adulated_johann_wilhelm_in_haskell_account",
            "Haskell says the artists surrounding Johann Wilhelm adulated him and interprets this as reflecting Wilhelm’s love of glory.",
            NEW_CANDIDATE, "cand-1325", [NEW_CANDIDATE, "cand-1325"], TRUE_NOTE),
        "st-chp10-p282-wilhelm-political-influence": (False, "johann_wilhelm_gained_german_political_influence_1708_1714",
            "Haskell says Johann Wilhelm achieved unparalleled influence in German politics for some years between 1708 and 1714.",
            "cand-1325", None, ["cand-1325"], FALSE_NOTE + " German politics is the domain of the influence claim, not a distinct bounded entity in this sentence."),
        "st-chp10-p282-rapparini-aesthetic-theory": (False, "rapparini_writings_advocated_chromatic_pleasure_facility_and_variety",
            "Haskell quotes Rapparini’s writing that strict regularity repels amateurs, painting should attract through apparent ease, colour pleases the eye, and a cheerful manner should animate the picture.",
            "cand-2107", None, ["cand-2107"], FALSE_NOTE + " The passage presents aesthetic propositions; it names no separate work or relational endpoint for those propositions."),
        "st-chp10-p282-rapparini-eclectic-taste": (False, "haskell_judged_rapparinis_praise_to_produce_eclectic_taste",
            "Haskell says Rapparini’s unqualified praise made his taste describable only as eclectic.",
            "cand-2107", None, ["cand-2107"], FALSE_NOTE + " This is Haskell’s critical evaluation of Rapparini’s writings."),
    }
    for sid, (is_relation, predicate, claim, subject, object_, mentioned, note) in decisions.items():
        row = by_id[sid]
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_
        row["predicate"] = predicate
        q = row["qualifiers"]
        q.update({"claim": claim, "relation_candidate": is_relation,
                  "relation_candidate_note": note, "mentioned_candidate_ids": mentioned})

    segment_coverage["note"] += (
        " The four previously unset statements are now classified: artist adulation is a source-bounded relation "
        "between an unnamed artist group and Johann Wilhelm; political influence, Rapparini’s quoted aesthetic "
        "propositions, and Haskell’s eclectic-taste evaluation are non-relational claims."
    )

    statement_bytes = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
    outputs = {
        STATEMENTS: statement_bytes,
        CANDIDATES: csv_bytes(cfields, candidates + [new_candidate], cbom),
        MENTIONS: csv_bytes(mfields, mentions + [new_mention], mbom),
        COVERAGE: csv_bytes(covfields, coverage, covbom),
    }
    summary = {
        "segment": SEGMENT,
        "mode": "dry-run",
        "statements_classified": 4,
        "relation_candidates": 1,
        "non_relational": 3,
        "candidate_added": NEW_CANDIDATE,
        "mention_added": NEW_MENTION,
        "mention_span": [start, start + len(surface)],
        "statement_counts_after": {
            "true": sum(r.get("qualifiers", {}).get("relation_candidate") is True for r in statements),
            "false": sum(r.get("qualifiers", {}).get("relation_candidate") is False for r in statements),
            "unset": sum(r.get("qualifiers", {}).get("relation_candidate") is None for r in statements),
        },
    }
    return outputs, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify the four remaining p.282 S2 statements with protected writes.")
    parser.add_argument("--apply", action="store_true", help="Back up affected tables, then atomically write the reviewed classification.")
    args = parser.parse_args()

    outputs, summary = build_outputs()
    summary["mode"] = "apply" if args.apply else "dry-run"
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("backup already exists; refusing to overwrite")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    for path, data in outputs.items():
        atomic_write(path, data)
    print("APPLIED; backups:")
    for backup in backups.values():
        print(backup.relative_to(ROOT))


if __name__ == "__main__":
    main()
