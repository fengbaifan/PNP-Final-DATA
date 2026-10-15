"""Guarded S2 semantic review for printed p.224, body lines 152-161."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l152-161"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE = ROOT / SOURCE_REL
PAGE_IMAGE = ROOT / "scripts" / ".tmp_s2_chp8_p224_review.png"
BACKUP_SUFFIX = ".bak-s2-chp8-p224-l152-161-semantic-review-20261014"
EXPECTED = {
    STATEMENTS: "2c176e2fab781cd73d873c9cf3a9e6216496df021c3f18892e9763bc35a9c8c9",
    CANDIDATES: "f1707c6bcd6f1384a9f32b2c4acfef6b8aced45995322263c5a55e50e04b0cbe",
    MENTIONS: "69c0537105dc2af3269daf2bbd88b3488929f7465db90e2cb34435a674adaf95",
    SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    PAGE_IMAGE: "e76689b8c84770ae166e473c87fee2cd5505bc38a738acb574cd4d663ae21c2b",
}

CLASSIFICATIONS = {
    "st-chp8-p224-aeneid-cycle-and-style": (True,
        "The source explicitly says each canvas represents an episode from the Aeneid; the aesthetic assessment is separated below."),
    "st-chp8-p224-dido-enthusiasm-open": (False,
        "This reports Haskell's evaluative/reception claim and its continuation; it is not a relation between entities."),
    "st-chp8-p224-dido-picture-narrative": (True,
        "The source explicitly describes the narrative scene represented in the painting; mythological events are not asserted as historical."),
    "st-chp8-p224-gallery-window-material-description": (False,
        "This is a descriptive account of the room's openings, light, and materials; it supplies no independently identified window or courtyard endpoint."),
    "st-chp8-p224-regional-focus": (False,
        "This is a composite summary over three cities; individual city relations are recorded separately below."),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_jsonl(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def csv_bytes(path: Path, rows):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        headers = next(csv.reader(f))
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        f.write(data)
    temp.replace(path)


def verify_inputs():
    for path, expected in EXPECTED.items():
        actual = sha(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for line, quote in [
        (155, "Yet it soon becomes clear that each represents an episode taken from a single story—the Aeneid."),
        (155, "It is such iconographie unity combined with extreme stylistic diversity, rather than any intrinsic merit in the canvases, which makes this decoration so exceptional in the Italy of its day."),
        (157, "For the rest his attention was firmly concentrated on"),
        (159, "Dark clouds lower over the landscape"),
    ]:
        if quote not in source_lines[line - 1]:
            raise SystemExit(f"source excerpt mismatch at L{line}: {quote}")


def plan():
    statements = read_jsonl(STATEMENTS)
    candidates = read_csv(CANDIDATES)
    mentions = read_csv(MENTIONS)
    by_id = {r["statement_id"]: r for r in statements}
    seg_rows = [r for r in statements if r.get("segment_id") == SEGMENT]
    unset = {r["statement_id"] for r in seg_rows
             if "relation_candidate" not in r.get("qualifiers", {})}
    if len(seg_rows) != 15 or unset != set(CLASSIFICATIONS):
        raise SystemExit(f"unexpected p224 state: rows={len(seg_rows)} unset={sorted(unset)}")
    if "cand-12083" in {r["candidate_id"] for r in candidates}:
        raise SystemExit("candidate cand-12083 already exists")
    if "m-chp8-p224-aeneid-canvases" in {r["mention_id"] for r in mentions}:
        raise SystemExit("canvas group mention already exists")
    if any(sid in by_id for sid in [
        "st-chp8-p224-haskell-aeneid-style-judgment",
        "st-chp8-p224-regional-focus-naples",
        "st-chp8-p224-regional-focus-bologna",
        "st-chp8-p224-regional-focus-venice",
    ]):
        raise SystemExit("one or more planned p224 statement IDs already exist")

    for sid, (is_relation, note) in CLASSIFICATIONS.items():
        q = by_id[sid]["qualifiers"]
        q["relation_candidate"] = is_relation
        q["relation_candidate_note"] = note

    canvas_candidate = {
        "candidate_id": "cand-12083", "index_entry_id": "",
        "canonical_name": "Unidentified large canvases depicting episodes from the Aeneid in Buonaccorsi's gallery",
        "index_page_range": "", "suggested_type": "work", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Haskell describes large canvases filling the walls of Raimondo Buonaccorsi's gallery; individual titles and makers are not supplied in this passage.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L155",
    }
    candidates.append(canvas_candidate)

    canvas_source = "\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[151:161])
    if canvas_source[944:952] != "canvases":
        raise SystemExit("canvas group mention span no longer matches source")
    mentions.append({
        "mention_id": "m-chp8-p224-aeneid-canvases", "segment_id": SEGMENT,
        "candidate_id": "cand-12083", "surface_form": "canvases",
        "start_char": "944", "end_char": "952",
        "note": "Unidentified large canvases in the gallery; Haskell says each represents an Aeneid episode.",
    })

    canvases = by_id["st-chp8-p224-aeneid-cycle-and-style"]
    canvases["subject_candidate_id"] = "cand-12083"
    canvases["predicate"] = "depicts_episodes_from"
    canvases["qualifiers"]["claim"] = "Haskell says each of the gallery's large canvases represents an episode from the Aeneid."
    canvases["qualifiers"]["qualification"] = "The canvases are not individually titled or identified; the represented literary source is kept distinct as an archive candidate."
    canvases["qualifiers"]["mentioned_candidate_ids"] = ["cand-12083", "cand-7763"]
    canvases["qualifiers"].pop("speaker_judgment", None)
    canvases["original_quote"] = "Yet it soon becomes clear that each represents an episode taken from a single story—the Aeneid."

    style_statement = {
        "statement_id": "st-chp8-p224-haskell-aeneid-style-judgment",
        "segment_id": SEGMENT, "subject_candidate_id": "cand-12083",
        "object_candidate_id": None,
        "predicate": "haskell_assessed_iconographic_unity_and_stylistic_diversity",
        "qualifiers": {
            "source_line_start": 155, "source_line_end": 155, "printed_page": 224,
            "pdf_physical_page": 26,
            "claim": "Haskell attributes the gallery decoration's exceptional effect in Italy to iconographic unity combined with stylistic diversity rather than intrinsic merit in the canvases.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "This preserves the author's aesthetic judgment and does not assert an independent quality assessment.",
            "mentioned_candidate_ids": ["cand-12083", "cand-3461"],
            "speaker_judgment": True, "relation_candidate": False,
            "relation_candidate_note": "This is an authorial aesthetic assessment, not a relation candidate.",
            "ocr_corrections": [{
                "source_file": SOURCE_REL, "source_line": 155, "ocr": "iconographie",
                "print": "iconographic", "basis": "CHP-8.pdf physical page 26."
            }],
        },
        "original_quote": "It is such iconographie unity combined with extreme stylistic diversity, rather than any intrinsic merit in the canvases, which makes this decoration so exceptional in the Italy of its day.",
        "origin": "book", "source_file": SOURCE_REL,
    }
    statements.append(style_statement)

    regional = by_id["st-chp8-p224-regional-focus"]
    regional["qualifiers"]["source_line_start"] = 157
    regional["qualifiers"]["source_line_end"] = 158
    regional["qualifiers"]["claim"] = "Haskell summarizes Raimondo's attention as concentrated on Naples, Bologna, and Venice."
    regional["qualifiers"]["mentioned_candidate_ids"] = ["cand-0467", "cand-3534", "cand-3398", "cand-3401"]
    regional["qualifiers"]["relation_candidate_note"] = CLASSIFICATIONS["st-chp8-p224-regional-focus"][1]
    regional["original_quote"] = "For the rest his attention was firmly concentrated on\nNaples, Bologna and Venice."
    place_rows = [
        ("naples", "cand-3534", "Naples"),
        ("bologna", "cand-3398", "Bologna"),
        ("venice", "cand-3401", "Venice"),
    ]
    for slug, place_id, place_name in place_rows:
        statements.append({
            "statement_id": f"st-chp8-p224-regional-focus-{slug}",
            "segment_id": SEGMENT, "subject_candidate_id": "cand-0467",
            "object_candidate_id": place_id, "predicate": "collecting_attention_concentrated_on",
            "qualifiers": {
                "source_line_start": 157, "source_line_end": 158, "printed_page": 224,
                "pdf_physical_page": 26,
                "claim": f"Haskell says Raimondo's attention was firmly concentrated on {place_name}.",
                "speaker": "Haskell", "text_layer": "body",
                "qualification": "One element of Haskell's three-city summary; do not treat the list as an exhaustive itinerary.",
                "mentioned_candidate_ids": ["cand-0467", place_id],
                "relation_candidate": True,
                "relation_candidate_note": "The text explicitly names this city as a focus of Raimondo's attention.",
                "place_list_context": ["Naples", "Bologna", "Venice"],
            },
            "original_quote": "For the rest his attention was firmly concentrated on\nNaples, Bologna and Venice.",
            "origin": "book", "source_file": SOURCE_REL,
        })

    artwork = next(r for r in candidates if r["candidate_id"] == "cand-2486")
    artwork["canonical_name"] = "Dido welcoming Aeneas to the Royal Hunt (painting by Francesco Solimena)"
    artwork["detail"] = "Work-specific index candidate for the painting Haskell calls the masterpiece of the Buonaccorsi gallery series; keep distinct from its reported replica cand-7760."

    for sid in ["st-chp8-p224-aeneid-cycle-and-style", "st-chp8-p224-haskell-aeneid-style-judgment",
                "st-chp8-p224-regional-focus"]:
        checked = style_statement if sid == "st-chp8-p224-haskell-aeneid-style-judgment" else by_id[sid]
        q = checked["qualifiers"]
        excerpt = "\n".join(SOURCE.read_text(encoding="utf-8-sig").splitlines()[q["source_line_start"] - 1:q["source_line_end"]])
        if checked["original_quote"] not in excerpt:
            raise SystemExit(f"source quote mismatch: {sid}")
    quote = "Dark clouds lower over the landscape and, on the instructions of Juno, the winds prepare to pound the earth with driving rain as the young Trojan hero, oblivious of Cupid’s arrow aimed at his breast, hurries forward to accept the guiding hand of Dido, who looks back at him with eyes full of tender passion."
    if quote not in SOURCE.read_text(encoding="utf-8-sig").splitlines()[158]:
        raise SystemExit("Dido narrative quote is not an exact source excerpt")

    final = [r for r in statements if r.get("segment_id") == SEGMENT]
    summary = {
        "p224_original_rows": len(seg_rows), "new_statements": 4,
        "new_candidates": 1, "new_mentions": 1,
        "classified_previously_unset": len(CLASSIFICATIONS),
        "candidate_name_corrected": 1,
        "p224_final_statements": len(final),
        "p224_final_true": sum(r["qualifiers"].get("relation_candidate") is True for r in final),
        "p224_final_false": sum(r["qualifiers"].get("relation_candidate") is False for r in final),
        "p224_final_unset": sum("relation_candidate" not in r.get("qualifiers", {}) for r in final),
    }
    if (summary["p224_final_statements"], summary["p224_final_true"],
            summary["p224_final_false"], summary["p224_final_unset"]) != (19, 14, 5, 0):
        raise SystemExit(f"unexpected p224 plan totals: {summary}")
    return write_jsonl(statements), csv_bytes(CANDIDATES, candidates), csv_bytes(MENTIONS, mentions), summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write guarded plan; default dry-run")
    args = parser.parse_args()
    verify_inputs()
    statement_bytes, candidate_bytes, mention_bytes, summary = plan()
    print(json.dumps({"mode": "apply" if args.apply else "dry-run", **summary}, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    verify_inputs()
    outputs = {STATEMENTS: statement_bytes, CANDIDATES: candidate_bytes, MENTIONS: mention_bytes}
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if backup.read_bytes() != path.read_bytes():
                raise SystemExit(f"existing backup differs: {backup.name}")
        else:
            shutil.copy2(path, backup)
        if sha(backup.read_bytes()) != EXPECTED[path]:
            raise SystemExit(f"backup hash mismatch: {backup.name}")
    for path, data in outputs.items():
        atomic_write(path, data)
    print("written_sha256=" + json.dumps({p.name: sha(p.read_bytes()) for p in outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
