from __future__ import annotations

import argparse
import copy
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l30-40"
SEGMENT_SHA = "572d6f8146f8914c683d85e9f68fff62f7c775b8951b151740f6c8e5efc1bfd8"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l30-40-20261012"
EXPECTED = {
    "book-statements.jsonl": "b3fca2f7fba0519c1a57cbc3faff79e3668ef6f84d12f28988dbbbb245ab48e6",
    "entity-candidates.csv": "192c32537280780659436def68e48fceef96c90535bac5a7443104c70c4384b3",
    "mentions.csv": "ddd8cd36f60270b832767851d31747f2961c2c24963f08b13db86d1251f0bdc2",
    "s2-coverage.csv": "469676eb5b0ad5477f38872dd5136ced732d9aca756dbcc13c5735143c407d83",
}
UNSET = {
    "st-chp2-sec-ii-l30-40-baldacchino-completion",
    "st-chp2-sec-ii-l30-40-bernini-prior-work-and-first-post",
    "st-chp2-sec-ii-l30-40-bernini-work-quality",
    "st-chp2-sec-ii-l30-40-st-peters-exterior-complete",
}
NEW_CANDIDATES = {
    "cand-11881": {
        "candidate_id": "cand-11881",
        "index_entry_id": "",
        "canonical_name": "Bernini’s decorative sculpture and small-scale bust work under the previous pontificate (unnamed group)",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Bernini had worked on decorative sculpture and small-scale busts throughout the previous reign. No individual works, titles, or complete membership are supplied.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L34",
    },
    "cand-11882": {
        "candidate_id": "cand-11882",
        "index_entry_id": "",
        "canonical_name": "Bernini’s first monumental works (unnamed group)",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Bernini began his first monumental works within months of receiving his first official post. The sentence names no work; do not treat the later baldacchino as the entire group without evidence.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L34",
    },
}
NEW_MENTIONS = {
    "m-chp2-secii-l30-40-0044": ("cand-11881", "decorative sculpture and small-scale busts"),
    "m-chp2-secii-l30-40-0045": ("cand-11882", "his first monumental works"),
}
NEW_STATEMENTS = {
    "st-chp2-sec-ii-l30-40-bernini-first-official-post",
    "st-chp2-sec-ii-l30-40-bernini-first-monumental-works",
}


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


def set_relation(row: dict, value: bool, note: str, *, mentioned: list[str] | None = None, open_endpoint_reason: str | None = None) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = value
    qualifiers["relation_candidate_note"] = note
    if mentioned is not None:
        qualifiers["mentioned_candidate_ids"] = mentioned
    if open_endpoint_reason:
        qualifiers["open_endpoint_reason"] = open_endpoint_reason
    else:
        qualifiers.pop("open_endpoint_reason", None)


def make_mention(mention_id: str, candidate_id: str, surface: str, source_text: str, note: str) -> dict[str, str]:
    starts = [index for index in range(len(source_text)) if source_text.startswith(surface, index)]
    if len(starts) != 1:
        raise SystemExit(f"expected one exact source anchor for {surface!r}, found {starts}")
    start = starts[0]
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.34 source segment fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[29:40])
    if "lais pontificate" not in source_text or "his first official post" not in source_text:
        raise SystemExit("expected p.34 OCR and career clauses changed; re-review before applying")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET:
        raise SystemExit(f"unexpected p.34 unset statement set: {sorted(unset)}")
    if set(NEW_CANDIDATES) & set(candidate_by_id) or set(NEW_MENTIONS) & set(mention_by_id) or NEW_STATEMENTS & set(statement_by_id):
        raise SystemExit("a planned candidate, mention, or statement ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11880:
        raise SystemExit("candidate ID sequence changed; refusing to allocate cand-11881/11882")
    if "work" not in {row["suggested_type"] for row in candidates}:
        raise SystemExit("candidate taxonomy no longer contains work type")

    for mention in mentions:
        if mention["segment_id"] != SEGMENT_ID:
            continue
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"existing p.34 mention span changed or is invalid: {mention['mention_id']}")

    candidates.extend(NEW_CANDIDATES.values())
    mentions.extend([
        make_mention(
            "m-chp2-secii-l30-40-0044", "cand-11881", "decorative sculpture and small-scale busts", source_text,
            "Source-described group of Bernini’s earlier work; no individual titles are supplied.",
        ),
        make_mention(
            "m-chp2-secii-l30-40-0045", "cand-11882", "his first monumental works", source_text,
            "Unnamed group Bernini began within months of receiving his first official post; titles are not supplied here.",
        ),
    ])

    false_decisions = {
        "st-chp2-sec-ii-l30-40-baldacchino-completion": "This is a completion-duration attribute of the identified baldacchino project. The source gives nine years but no explicit completion year; it does not assert a relation to a distinct entity.",
        "st-chp2-sec-ii-l30-40-bernini-work-quality": "This is Haskell’s comparative assessment of Bernini’s work and birth circumstances, not a relation between entities.",
        "st-chp2-sec-ii-l30-40-st-peters-exterior-complete": "This is a construction-status assertion about St Peter’s exterior, not a relation to a distinct identified entity.",
    }
    for statement_id, note in false_decisions.items():
        row = statement_by_id[statement_id]
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = note
        row["qualifiers"].pop("open_endpoint_reason", None)

    combined_id = "st-chp2-sec-ii-l30-40-bernini-prior-work-and-first-post"
    combined = statement_by_id[combined_id]
    first_post = copy.deepcopy(combined)
    first_works = copy.deepcopy(combined)
    combined["object_candidate_id"] = "cand-11881"
    combined["predicate"] = "worked_on"
    combined["original_quote"] = "Bernini, who throughout the previous reign had been working on decorative sculpture and small-scale busts"
    combined["qualifiers"]["claim"] = "Haskell says Bernini worked on decorative sculpture and small-scale busts throughout the previous reign."
    combined["qualifiers"]["qualification"] = "The previous reign is understood from the surrounding account as Paul V’s pontificate. The source names no individual sculptures or busts. The printed page reads ‘his pontificate’ elsewhere where the OCR source has ‘lais’."
    set_relation(
        combined,
        True,
        "The source explicitly says Bernini worked on decorative sculpture and small-scale busts throughout the previous reign; the source-defined unnamed work group preserves the activity without inventing titles.",
        mentioned=["cand-3046", "cand-11881"],
    )

    first_post.update({
        "statement_id": "st-chp2-sec-ii-l30-40-bernini-first-official-post",
        "subject_candidate_id": "cand-3046",
        "object_candidate_id": None,
        "predicate": "received_first_official_post_reported",
        "original_quote": "Within a few months Bernini, who throughout the previous reign had been working on decorative sculpture and small-scale busts, was given his first official post and began his first monumental works.",
        "qualifiers": copy.deepcopy(combined["qualifiers"]),
    })
    first_post["qualifiers"].update({
        "claim": "Haskell says Bernini received his first official post within a few months.",
        "qualification": "The source does not name the post or explicitly identify the appointing authority in this sentence.",
    })
    set_relation(
        first_post,
        True,
        "The source explicitly reports Bernini’s receipt of his first official post, but supplies neither the post’s name nor the appointing authority.",
        mentioned=["cand-3046"],
        open_endpoint_reason="The official post and the person or body that granted it are unnamed in this sentence.",
    )

    first_works.update({
        "statement_id": "st-chp2-sec-ii-l30-40-bernini-first-monumental-works",
        "subject_candidate_id": "cand-3046",
        "object_candidate_id": "cand-11882",
        "predicate": "began_work_on",
        "original_quote": "Within a few months Bernini, who throughout the previous reign had been working on decorative sculpture and small-scale busts, was given his first official post and began his first monumental works.",
        "qualifiers": copy.deepcopy(combined["qualifiers"]),
    })
    first_works["qualifiers"].update({
        "claim": "Haskell says Bernini began his first monumental works within a few months of receiving his first official post.",
        "qualification": "The source identifies these as a group of first monumental works but names no individual work in this sentence.",
    })
    set_relation(
        first_works,
        True,
        "The source explicitly says Bernini began his first monumental works; preserve the unnamed group as an open work candidate and do not assume it consists only of the later baldacchino.",
        mentioned=["cand-3046", "cand-11882"],
    )
    insert_at = statements.index(combined)
    statements[insert_at + 1:insert_at + 1] = [first_post, first_works]

    for statement_id, corrected in {
        "st-chp2-sec-ii-l30-40-urban-favored-tuscan-artists": ("lais pontificate", "his pontificate"),
        "st-chp2-sec-ii-l30-40-uncertain-overall-plan": ("nature of lais ideas", "nature of his ideas"),
    }.items():
        row = statement_by_id[statement_id]
        note = f"The printed p.34 scan reads ‘{corrected[1]}’; the OCR source asset has ‘{corrected[0]}’."
        qualification = row["qualifiers"].get("qualification", "").rstrip()
        if note not in qualification:
            row["qualifiers"]["qualification"] = (qualification + " " + note).strip()

    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("split created duplicate statement IDs")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.34 segment still has unset values: {remaining}")
    candidate_ids = {row["candidate_id"] for row in candidates}
    referenced = set()
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row.get("qualifiers", {}).get("mentioned_candidate_ids", []))
    if referenced - candidate_ids:
        raise SystemExit(f"missing p.34 candidate foreign keys: {sorted(referenced - candidate_ids)}")
    if any(source_text[int(m["start_char"]):int(m["end_char"])] != m["surface_form"] for m in mentions if m["segment_id"] == SEGMENT_ID):
        raise SystemExit("p.34 mention span audit failed")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.34 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up closed four previously unset statements. Bernini’s combined career sentence was separated into prior decorative work, receipt of an unnamed first official post, and beginning an unnamed group of first monumental works. "
        "The printed p.34 scan confirms ‘his pontificate’ and ‘his ideas’ where the OCR source has ‘lais’; the source asset remains unchanged."
    )

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2 printed p.34 / normalized S0 L30-40",
        "classified_unset_ids": sorted(UNSET),
        "split_statements": sorted(NEW_STATEMENTS),
        "new_candidates": sorted(NEW_CANDIDATES),
        "new_mentions": sorted(NEW_MENTIONS),
        "remaining_unset": remaining,
        "counts_delta": {"statements": 2, "candidates": 2, "mentions": 2},
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(serialize(name, rows)).hexdigest() for name, rows in updated.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, path in paths.items():
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
        for name, rows in updated.items():
            path = paths[name]
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(serialize(name, rows))
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_by_id = {row["statement_id"]: row for row in written}
        if any((written_by_id[sid].get("qualifiers") or {}).get("relation_candidate") is None for sid in UNSET | NEW_STATEMENTS):
            raise SystemExit("a p.34 relation_candidate value was not persisted")
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
        "statement_count": len(written),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
