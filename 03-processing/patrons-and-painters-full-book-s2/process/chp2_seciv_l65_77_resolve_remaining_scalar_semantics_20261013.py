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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l65-77"
SEGMENT_SHA = "69490f9d868a34da1b43ef70ed866733a906d4a10d1935155fa65fb8dd57a811"
NOTES_SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l190-245"
NOTES_SEGMENT_SHA = "5dd2839d3e713ca4795b2bfd4de98120305a38026d0d41ffcc7c84e19fbcfd2a"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l65-77-scalar-semantics-20261013"
EXPECTED = {
    "book-statements.jsonl": "71cc3a77383c31502b78399f346c9fbc7bc0a625dd90bd043bfd46edbd204824",
    "s2-coverage.csv": "2b4213c849cf4ae8095a70232eed0c06610e22552d22ecd2202335b7779bf9a9",
}
UNSET_IDS = {
    "st-chp2-seciv-l65-77-bentivoglio-family-papal-art-patronage",
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-artists",
    "st-chp2-seciv-l65-77-claude-romantic-treatment-reported",
}
NEW_IDS = {
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-tassi",
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-gentileschi",
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-unnamed-artists",
}
FAMILY_QUOTE = (
    "Ever since the beginning of the century the BentivogUo brothers had been helping succeeding popes with the "
    "purchase of the finest old masters and the employment of contemporary artists."
)
RENI_QUOTE = "decorated by Guido Reni"
OTHERS_QUOTE = "decorated by Guido Reni, Tassi, Gentileschi and others"
TASSI_QUOTE = OTHERS_QUOTE
GENTILESCHI_QUOTE = OTHERS_QUOTE
CLAUDE_QUOTE = (
    "Santa Marinella and his country house at Castel Gandolfo—themes which the artist treated in a romantically "
    "vague manner rather than literally as Urban had perhaps hoped."
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def add_unique(values: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*values, *additions]))


def classify(row: dict, note: str) -> dict:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = True
    qualifiers["relation_candidate_note"] = note
    return qualifiers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve remaining scalar claims and split artist endpoints in CHP-2 section IV L65-77."
    )
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")

    segment_by_id = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
    segment = segment_by_id.get(SEGMENT_ID)
    notes_segment = segment_by_id.get(NOTES_SEGMENT_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected print-p.49 source segment fingerprint changed")
    if not notes_segment or notes_segment.get("sha256") != NOTES_SEGMENT_SHA or notes_segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected section IV notes segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected L65-77 unset statement set: {sorted(unset)}")
    if NEW_IDS & statement_by_id.keys():
        raise SystemExit(f"planned statement IDs already exist: {sorted(NEW_IDS & statement_by_id.keys())}")
    required = {
        "st-chp2-seciv-l65-77-urban-commissions-two-location-views",
        "st-chp2-seciv-l190-245-palace-transfer-and-earlier-frescoes",
    }
    if required - statement_by_id.keys():
        raise SystemExit(f"required body or note statements missing: {sorted(required - statement_by_id.keys())}")
    candidate_ids = {"cand-4651", "cand-0398", "cand-2124", "cand-2542", "cand-1135", "cand-0767", "cand-0209", "cand-4657", "cand-4492", "cand-4491"}
    candidate_rows = {row["candidate_id"] for row in read_csv(TABLES / "entity-candidates.csv")}
    if candidate_ids - candidate_rows:
        raise SystemExit(f"required candidate IDs missing: {sorted(candidate_ids - candidate_rows)}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for quote in (FAMILY_QUOTE, RENI_QUOTE, TASSI_QUOTE, GENTILESCHI_QUOTE, OTHERS_QUOTE, CLAUDE_QUOTE):
        if quote not in "\n".join(source_lines):
            raise SystemExit(f"protected S0 quote no longer matches the source: {quote}")
    coverage_rows = [row for row in coverage if row.get("segment_id") == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected exactly one L65-77 coverage row")

    family = statement_by_id["st-chp2-seciv-l65-77-bentivoglio-family-papal-art-patronage"]
    family["original_quote"] = FAMILY_QUOTE
    fq = classify(
        family,
        "Haskell explicitly describes Bentivoglio family assistance to succeeding popes' art acquisitions and employment of contemporary artists; keep the unnamed popes and transactions open.",
    )
    fq["claim"] = "Haskell says the Bentivoglio brothers had, since the beginning of the century, helped succeeding popes acquire old masters and employ contemporary artists."
    fq["qualification"] = "No specific pope, purchase, or employment is identified; preserve the source's collective and continuing wording."
    fq["time_relation"] = "Since the beginning of the century, as stated by Haskell; no exact year is supplied."
    fq["open_endpoint_reason"] = "The source refers collectively to 'succeeding popes' and does not identify individual patrons or transactions. Do not infer the Pope from adjacent claims."
    fq["mentioned_candidate_ids"] = ["cand-4651"]
    corrections = fq.setdefault("page_image_ocr_corrections", [])
    correction = {"source_line": 73, "ocr": "BentivogUo", "print": "Bentivoglio"}
    if correction not in corrections:
        corrections.append(correction)

    decorators = statement_by_id["st-chp2-seciv-l65-77-borghese-palace-decoration-by-artists"]
    decorators["object_candidate_id"] = "cand-2124"
    decorators["predicate"] = "palace_decoration_attributed_to_artist"
    decorators["original_quote"] = RENI_QUOTE
    dq = classify(decorators, "The source explicitly names Guido Reni among the artists who decorated the Borghese palace; retain a separate palace-to-artist endpoint.")
    dq["claim"] = "Haskell says Guido Reni decorated the Borghese palace on the Quirinal."
    dq["artist_candidate_ids"] = ["cand-2124"]
    dq["mentioned_candidate_ids"] = ["cand-0398", "cand-2124"]
    dq["qualification"] = "Haskell also says 'and others', but does not name those additional artists; no work or room is assigned to Reni here."
    dq["footnote_marker"] = 1
    dq["footnote_refs"] = [{"marker": 1, "segment_id": NOTES_SEGMENT_ID, "source_line": 214}]

    tassi_id = "st-chp2-seciv-l65-77-borghese-palace-decoration-by-tassi"
    gentileschi_id = "st-chp2-seciv-l65-77-borghese-palace-decoration-by-gentileschi"
    unnamed_id = "st-chp2-seciv-l65-77-borghese-palace-decoration-by-unnamed-artists"
    link_ids = [tassi_id, gentileschi_id, unnamed_id]
    dq["related_statement_ids"] = add_unique(dq.get("related_statement_ids", []), link_ids)

    def artist_row(statement_id: str, candidate_id: str, artist: str, quote: str) -> dict:
        note = "Haskell explicitly names this artist among those who decorated the Borghese palace."
        q = {
            "source_line_start": 67, "source_line_end": 67,
            "claim": f"Haskell says {artist} decorated the Borghese palace on the Quirinal.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 49, "pdf_physical_page": 34,
            "qualification": "The body does not assign an individual room or work. Footnote 1 dates the Tassi and Gentileschi frescoes to 1611 and 1612, when Scipione Borghese owned the palace, and rejects Passeri's attribution of those works to Bentivoglio.",
            "footnote_marker": 1,
            "footnote_refs": [{"marker": 1, "segment_id": NOTES_SEGMENT_ID, "source_line": 214}],
            "relation_candidate": True,
            "relation_candidate_note": note,
            "mentioned_candidate_ids": ["cand-0398", candidate_id],
            "related_statement_ids": [decorators["statement_id"], "st-chp2-seciv-l190-245-palace-transfer-and-earlier-frescoes"],
        }
        return {
            "statement_id": statement_id,
            "segment_id": SEGMENT_ID,
            "subject_candidate_id": "cand-0398",
            "object_candidate_id": candidate_id,
            "predicate": "palace_decoration_attributed_to_artist",
            "qualifiers": q,
            "original_quote": quote,
            "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
        }

    tassi = artist_row(tassi_id, "cand-2542", "Agostino Tassi", TASSI_QUOTE)
    gentileschi = artist_row(gentileschi_id, "cand-1135", "Orazio Gentileschi", GENTILESCHI_QUOTE)
    unnamed = {
        "statement_id": unnamed_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0398", "object_candidate_id": None,
        "predicate": "palace_decoration_by_unnamed_artists_reported",
        "qualifiers": {
            "source_line_start": 67, "source_line_end": 67,
            "claim": "Haskell says additional unnamed artists also decorated the Borghese palace.",
            "speaker": "Haskell", "text_layer": "authorial narrative",
            "print_page": 49, "pdf_physical_page": 34,
            "qualification": "The source says 'and others' after naming Guido Reni, Agostino Tassi, and Orazio Gentileschi, but does not identify the additional artists.",
            "footnote_marker": 1,
            "footnote_refs": [{"marker": 1, "segment_id": NOTES_SEGMENT_ID, "source_line": 214}],
            "relation_candidate": True,
            "relation_candidate_note": "The source explicitly reports additional decorators but leaves their identities unnamed; preserve the open endpoint without creating a group entity.",
            "open_endpoint_reason": "The additional artists are described only as 'others' and are not individually identifiable in this passage.",
            "mentioned_candidate_ids": ["cand-0398"],
            "related_statement_ids": [decorators["statement_id"]],
        },
        "original_quote": OTHERS_QUOTE,
        "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    for row in (tassi, gentileschi):
        row["qualifiers"]["related_statement_ids"] = add_unique(row["qualifiers"]["related_statement_ids"], [gentileschi_id if row is tassi else tassi_id, unnamed_id])
    unnamed["qualifiers"]["related_statement_ids"] = add_unique(unnamed["qualifiers"]["related_statement_ids"], [tassi_id, gentileschi_id])
    note_statement = statement_by_id["st-chp2-seciv-l190-245-palace-transfer-and-earlier-frescoes"]
    note_q = note_statement.setdefault("qualifiers", {})
    note_q["linked_body_statement_ids"] = add_unique(note_q.get("linked_body_statement_ids", []), [tassi_id, gentileschi_id])
    note_q["related_statement_ids"] = add_unique(note_q.get("related_statement_ids", []), [tassi_id, gentileschi_id])

    claude = statement_by_id["st-chp2-seciv-l65-77-claude-romantic-treatment-reported"]
    claude["object_candidate_id"] = "cand-0209"
    claude["predicate"] = "artist_treatment_contrasted_with_patron_expectation_reported"
    claude["original_quote"] = CLAUDE_QUOTE
    cq = classify(claude, "Haskell directly contrasts Claude's treatment of Urban's themes with what Urban had perhaps hoped; preserve the tentative expectation as the author's inference.")
    cq["claim"] = "Haskell characterizes Claude's treatment of Urban's fortifications and country house themes as romantically vague rather than literal, while tentatively suggesting that Urban may have hoped for literal records."
    cq["qualification"] = "The word 'perhaps' qualifies Haskell's account of Urban's expectation; it is not a documented statement by Urban. The source identifies the two locations but not the commissioned pictures by title."
    cq["mentioned_candidate_ids"] = ["cand-0767", "cand-0209", "cand-4657", "cand-4492", "cand-4491"]
    cq["related_statement_ids"] = add_unique(cq.get("related_statement_ids", []), ["st-chp2-seciv-l65-77-urban-commissions-two-location-views"])

    statements.extend([tassi, gentileschi, unnamed])
    remaining = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if remaining:
        raise SystemExit(f"section IV L65-77 still has unset relation_candidate values: {sorted(remaining)}")

    coverage_row = coverage_rows[0]
    note = (
        " 本轮闭合3条旧unset：Bentivoglio家族协助继任教皇采购古代名作和雇用当代画家保留为开放端点关系；Borghese宫 decorator 拆为Reni、Tassi、Gentileschi三条具名边，并保留未名其他画家为开放端点；Claude对Urban主题的处理与Urban可能偏好的写实记录相连，保留perhaps限定。"
        "p.49注1回链至Tassi/Gentileschi边：注释称两人壁画作于1611/1612年、宫殿当时属Scipione Borghese，并纠正Passeri的Bentivoglio归属；不把该归属移给Reni。页图确认BentivogUo→Bentivoglio；原S0及original_quote保留。"
    )
    if note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "closed_unset_ids": sorted(UNSET_IDS),
        "classification_counts": {"true": 6, "false": 0},
        "new_statements": sorted(NEW_IDS),
        "new_candidates": 0, "new_mentions": 0,
        "open_endpoint_statements": [family["statement_id"], unnamed_id],
        "note_backlinks_added": [tassi_id, gentileschi_id],
        "source_asset_unchanged": True,
        "remaining_unset_in_segment": [],
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if written_by_id[tassi_id].get("object_candidate_id") != "cand-2542":
            raise SystemExit("the Tassi-palace relation was not persisted")
        if written_by_id[gentileschi_id].get("object_candidate_id") != "cand-1135":
            raise SystemExit("the Gentileschi-palace relation was not persisted")
        if written_by_id[claude["statement_id"]].get("object_candidate_id") != "cand-0209":
            raise SystemExit("the Claude-Urban treatment relation was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
