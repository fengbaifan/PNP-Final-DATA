from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l48-60"
SEGMENT_SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
QUOTE_SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "317360dc58a1ff7ff952b209733ff093818c1c90a73d9de212406f2ef081bf18",
    MENTIONS: "c3ac6a7f170a0107e2daa7abc1dd71d0df50cdb98a9cc3686de8d31ba61daed1",
    STATEMENTS: "27f125ef906618187c7e837f9de17fffbd39ea4fa922af716d99be79f6c0fcf6",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SEGMENT_SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp1-secii-l48-60-20261015")
    for path in (MENTIONS, STATEMENTS)
}
BODY_IDS = {
    "general": "st-chp1-secii-l48-60-01",
    "caravaggio": "st-chp1-secii-l48-60-04",
    "rubens": "st-chp1-secii-l48-60-05",
    "footnote": "st-chp1-secii-p11-n4-cites-friedlaender-p302",
}
NEW_STATEMENT_ID = "st-chp1-secii-l48-60-04-martyrdom-design"
NEW_MENTION_ID = "m-chp1-secii-rubens-chiesa-nuova-altarpiece-1606"
WORK_IDS = {
    "conversion": "cand-3185",
    "martyrdom": "cand-3187",
    "rubens": "cand-3206",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def write_csv(data: bytes, headers: list[str], rows: list[dict[str, str]]) -> bytes:
    line_ending = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    return (b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b"") + buffer.getvalue().encode("utf-8")


def serialize_json_line(row: dict, ending: bytes) -> bytes:
    return json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending


def build() -> tuple[dict[Path, bytes], dict[str, int]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, digest in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_headers, candidate_rows = read_csv(CANDIDATES.read_bytes())
    _, mention_rows = read_csv(MENTIONS.read_bytes())
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_by_id = {row["mention_id"]: row for row in mention_rows}
    for candidate_id in WORK_IDS.values():
        candidate = candidate_by_id.get(candidate_id)
        if not candidate or candidate.get("candidate_origin") != "accepted-ku":
            raise SystemExit(f"accepted work candidate changed: {candidate_id}")
        card = ROOT / candidate["candidate_source_ref"]
        if not card.is_file():
            raise SystemExit(f"accepted work card missing: {candidate_id}")

    segment_rows = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SEGMENT_SOURCE.read_bytes()):
        raise SystemExit("S0 asset/segment mismatch")
    segment_lines = SEGMENT_SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(segment_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(segment_text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    surface = "an altarpiece"
    if segment_text.count(surface) != 1:
        raise SystemExit("expected one exact Rubens commission mention in the S0 segment")
    start = segment_text.index(surface)
    end = start + len(surface)
    if any(
        row["segment_id"] == SEGMENT_ID
        and start < int(row["end_char"])
        and end > int(row["start_char"])
        for row in mention_rows
    ):
        raise SystemExit("new work mention overlaps an existing mention")
    if NEW_MENTION_ID in mention_by_id:
        raise SystemExit("new mention ID already exists")

    statements_bytes = STATEMENTS.read_bytes()
    statement_lines = statements_bytes.splitlines(keepends=True)
    statement_by_id: dict[str, dict] = {}
    for line in statement_lines:
        if line.strip():
            row = json.loads(line)
            statement_by_id[row["statement_id"]] = row
    if NEW_STATEMENT_ID in statement_by_id:
        raise SystemExit("new statement ID already exists")
    for statement_id in BODY_IDS.values():
        if statement_id not in statement_by_id:
            raise SystemExit(f"target statement missing: {statement_id}")
    general = statement_by_id[BODY_IDS["general"]]
    caravaggio = statement_by_id[BODY_IDS["caravaggio"]]
    rubens = statement_by_id[BODY_IDS["rubens"]]
    footnote = statement_by_id[BODY_IDS["footnote"]]
    if any(statement_by_id[key].get("segment_id") != SEGMENT_ID for key in (BODY_IDS["general"], BODY_IDS["caravaggio"], BODY_IDS["rubens"])):
        raise SystemExit("body statement/source mapping changed")
    if general.get("predicate") != "artist_reputation_and_temperament" or general.get("qualifiers", {}).get("source_line_end") != 392:
        raise SystemExit("general artist-reputation statement changed")
    if caravaggio.get("subject_candidate_id") != "cand-0544" or caravaggio.get("object_candidate_id") not in (None, ""):
        raise SystemExit("Caravaggio statement endpoint state changed")
    if rubens.get("subject_candidate_id") != "cand-2293" or rubens.get("object_candidate_id") not in (None, ""):
        raise SystemExit("Rubens statement endpoint state changed")
    if mention_by_id.get("m-chp1-secii-0076", {}).get("candidate_id") != "cand-0546" or mention_by_id.get("m-chp1-secii-0077", {}).get("candidate_id") != "cand-0550":
        raise SystemExit("Caravaggio title mention mapping changed")
    if footnote.get("qualifiers", {}).get("related_body_statement_ids") != [BODY_IDS["caravaggio"]]:
        raise SystemExit("Caravaggio footnote backlink changed")

    quote_lines = QUOTE_SOURCE.read_text(encoding="utf-8-sig").splitlines()
    general_quote = "\n".join(quote_lines[381:388])
    boundary = "friends for suggestions.2"
    if boundary not in general_quote:
        raise SystemExit("expected exact paragraph boundary not found in source quote")
    general_quote = general_quote[:general_quote.index(boundary) + len(boundary)]
    if "Valentin" in general_quote or not general_quote.endswith(boundary):
        raise SystemExit("general statement quote did not stop before the Valentin example")

    new_mentions = [row for row in mention_rows if row["mention_id"] in {"m-chp1-secii-0076", "m-chp1-secii-0077"}]
    if len(new_mentions) != 2:
        raise SystemExit("expected the two Caravaggio title mentions")
    mention_updates = {
        "m-chp1-secii-0076": (WORK_IDS["conversion"], "Named subject of the 1600 Conversion commission; the mention denotes the commission object, not a selected surviving version."),
        "m-chp1-secii-0077": (WORK_IDS["martyrdom"], "Named subject of the 1600 Martyrdom commission; the mention denotes the commission object, not a selected surviving version."),
    }
    for mention in mention_rows:
        if mention["mention_id"] in mention_updates:
            mention["candidate_id"], mention["note"] = mention_updates[mention["mention_id"]]
    rubens_mention = {
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": WORK_IDS["rubens"],
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Haskell names only an altarpiece at Chiesa Nuova; this mention maps it to the accepted Rubens commission KU, whose evidence includes this passage and independent identification. The passage itself supplies no formal title or version.",
    }
    mention_rows.append(rubens_mention)
    mention_bytes = write_csv(MENTIONS.read_bytes(), list(read_csv(MENTIONS.read_bytes())[0]), mention_rows)

    general = dict(general)
    general_q = dict(general.get("qualifiers", {}))
    general_q["source_line_end"] = 388
    general_q["mentioned_candidate_ids"] = [candidate_id for candidate_id in general_q.get("mentioned_candidate_ids", []) if candidate_id not in {"cand-3446", "cand-3568", "cand-3447"}]
    general["qualifiers"] = general_q
    general["original_quote"] = general_quote

    work_ids = [WORK_IDS["conversion"], WORK_IDS["martyrdom"]]
    caravaggio_qual = dict(caravaggio.get("qualifiers", {}))
    caravaggio_qual.pop("open_endpoint_reason", None)
    caravaggio_qual["claim"] = "In 1600 Caravaggio agreed with his unnamed patron to submit figure and object designs before executing the altarpiece commission of The Conversion of St Paul. Haskell presents the arrangement as exceptional and notes Caravaggio’s reputation as difficult."
    caravaggio_qual["qualification"] = "The contract clause is mediated through Haskell’s footnote. The source names the commission but does not identify which surviving version belongs to it; the patron remains unnamed. The parallel St Peter commission is a separate statement with the same source quote."
    caravaggio_qual["relation_candidate_note"] = "Records Caravaggio’s 1600 design-submission requirement for the Conversion commission. Haskell calls the case exceptional; neither the patron’s identity nor a surviving version is identified here."
    caravaggio_qual["mentioned_candidate_ids"] = ["cand-0544", *work_ids]
    caravaggio_qual["source_line_start"] = 397
    caravaggio_qual["source_line_end"] = 401
    first_caravaggio = dict(caravaggio)
    first_caravaggio["object_candidate_id"] = WORK_IDS["conversion"]
    first_caravaggio["qualifiers"] = caravaggio_qual

    second_caravaggio = dict(first_caravaggio)
    second_caravaggio["statement_id"] = NEW_STATEMENT_ID
    second_caravaggio["object_candidate_id"] = WORK_IDS["martyrdom"]
    second_qual = dict(caravaggio_qual)
    second_qual["claim"] = "In 1600 Caravaggio agreed with his unnamed patron to submit figure and object designs before executing the altarpiece commission of The Martyrdom of St Peter. Haskell presents the arrangement as exceptional and notes Caravaggio’s reputation as difficult."
    second_qual["relation_candidate_note"] = "Records Caravaggio’s 1600 design-submission requirement for the Martyrdom commission. Haskell calls the case exceptional; neither the patron’s identity nor a surviving version is identified here."
    second_caravaggio["qualifiers"] = second_qual

    rubens = dict(rubens)
    rubens["object_candidate_id"] = WORK_IDS["rubens"]
    rubens_q = dict(rubens.get("qualifiers", {}))
    rubens_q.pop("open_endpoint_reason", None)
    rubens_q["mentioned_candidate_ids"] = list(dict.fromkeys([*rubens_q.get("mentioned_candidate_ids", []), WORK_IDS["rubens"]]))
    rubens_q["relation_candidate_note"] = "Rubens was asked in 1606 to show painting examples before undertaking the Chiesa Nuova altarpiece. The object endpoint is the accepted commission/work unit; Haskell’s passage itself does not supply its formal title or version."
    rubens["qualifiers"] = rubens_q

    footnote = dict(footnote)
    footnote_q = dict(footnote.get("qualifiers", {}))
    footnote_q["mentioned_candidate_ids"] = [candidate_id for candidate_id in footnote_q.get("mentioned_candidate_ids", []) if candidate_id not in {"cand-0546", "cand-0550"}]
    for candidate_id in work_ids:
        if candidate_id not in footnote_q["mentioned_candidate_ids"]:
            footnote_q["mentioned_candidate_ids"].append(candidate_id)
    for key in ("related_body_statement_ids", "linked_body_statement_ids"):
        links = list(footnote_q.get(key, []))
        if NEW_STATEMENT_ID not in links:
            links.append(NEW_STATEMENT_ID)
        footnote_q[key] = links
    footnote["qualifiers"] = footnote_q

    replacements = {
        BODY_IDS["general"]: general,
        BODY_IDS["caravaggio"]: first_caravaggio,
        BODY_IDS["rubens"]: rubens,
        BODY_IDS["footnote"]: footnote,
    }
    statement_out: list[bytes] = []
    seen: set[str] = set()
    for line in statement_lines:
        if not line.strip():
            statement_out.append(line)
            continue
        row = json.loads(line)
        statement_id = row["statement_id"]
        ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
        if statement_id in replacements:
            statement_out.append(serialize_json_line(replacements[statement_id], ending))
            seen.add(statement_id)
            if statement_id == BODY_IDS["caravaggio"]:
                statement_out.append(serialize_json_line(second_caravaggio, ending))
        else:
            statement_out.append(line)
    if seen != set(replacements):
        raise SystemExit(f"statement replacement mismatch: {seen}")
    statement_bytes = b"".join(statement_out)
    new_candidate_count = len(candidate_rows)
    new_statement_count = sum(1 for line in statement_bytes.splitlines() if line.strip())
    new_mention_count = len(mention_rows)
    if (new_candidate_count, new_mention_count, new_statement_count) != (12256, 26445, 15113):
        raise SystemExit(f"projected counts mismatch: {(new_candidate_count, new_mention_count, new_statement_count)}")
    return {MENTIONS: mention_bytes, STATEMENTS: statement_bytes}, {
        "candidates": new_candidate_count,
        "mentions": new_mention_count,
        "statements": new_statement_count,
    }


def apply(updates: dict[Path, bytes]) -> None:
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("recovery backup already exists")
    for path, digest in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise SystemExit(f"file changed after preview: {path.relative_to(ROOT)}")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    temporary: dict[Path, Path] = {}
    written: list[Path] = []
    try:
        for path, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                temp_path = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            temporary[path] = temp_path
        for path, temp_path in temporary.items():
            os.replace(temp_path, path)
            written.append(path)
    except Exception:
        for path in reversed(written):
            shutil.copy2(BACKUPS[path], path)
        raise
    finally:
        for temp_path in temporary.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updates, counts = build()
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {EXPECTED_HASHES[path]} -> {sha(data)}")
    print("changes: trim l48-60-01 before Valentin example; split Caravaggio's two commissions; correct their work mentions/backlinks; resolve Rubens altarpiece to accepted KU")
    print(f"projected counts: {counts}; open endpoints 541 -> 539; relation candidates true 10376 -> 10377")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply(updates)
    print("applied with recovery backups")


if __name__ == "__main__":
    main()
