from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/00_01_Title_Copyright.md"
EXPECTED_SHA256 = "c4b77ef59f53b5c729614d99192805731678fa294ef79ece043d74c180d337e7"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-front-matter-title-page-relations-20261010")
SEGMENT_1 = "front-matter:00_01_Title_Copyright:l3-12"
SEGMENT_2 = "front-matter:00_01_Title_Copyright:l14-29"

ROWS = {
    "st-fm-title-published-by": {
        "segment": SEGMENT_1, "line": 10, "predicate": "published_by",
        "subject": "cand-2962", "object": "cand-3703", "anchor": "YALE UNIVERSITY PRESS",
        "note": "The printed title-page imprint names Yale University Press as publisher. This is a source-stated imprint relation, not an external edition verification.",
    },
    "st-fm-title-published-london": {
        "segment": SEGMENT_1, "line": 11, "predicate": "publication_place",
        "subject": "cand-2962", "object": "cand-1422", "anchor": "NEW HAVEN AND LONDON",
        "note": "The title-page imprint lists London as one publication place. The statement remains limited to this printed edition imprint.",
    },
    "st-fm-title-published-new-haven": {
        "segment": SEGMENT_1, "line": 11, "predicate": "publication_place",
        "subject": "cand-2962", "object": "cand-3941", "anchor": "NEW HAVEN AND LONDON",
        "note": "The title-page imprint lists New Haven as one publication place. The statement remains limited to this printed edition imprint.",
    },
    "st-fm-title-copyright-holder": {
        "segment": SEGMENT_2, "line": 16, "predicate": "copyright_notice_holder",
        "subject": "cand-2962", "object": "cand-3704", "anchor": "Copyright © 1980 by Yale University.",
        "note": "The printed copyright notice assigns copyright in 1980 to Yale University. Keep this rights holder distinct from Yale University Press, the publisher.",
    },
    "st-fm-title-reproduction-notice": {
        "segment": SEGMENT_2, "line": 18, "predicate": "reproduction_notice_cites_law",
        "subject": "cand-2962", "object": "cand-3611", "anchor": "Sections 107 and 108 of the U.S. Copyright Law",
        "note": "The reproduction notice explicitly cites Sections 107 and 108 of U.S. Copyright Law. This records the notice's cited legal basis, not an independent legal interpretation.",
    },
    "st-fm-title-printed-in": {
        "segment": SEGMENT_2, "line": 19, "predicate": "printed_in",
        "subject": "cand-2962", "object": "cand-3915", "anchor": "Printed in China",
        "note": "The printed edition identifies China as its place of printing; this is not treated as its publication place.",
    },
    "st-fm-title-cataloged-by": {
        "segment": SEGMENT_2, "line": 20, "predicate": "cataloged_by",
        "subject": "cand-2962", "object": "cand-3655", "anchor": "Library of Congress Cataloging in Publication Data",
        "note": "The printed CIP block identifies Library of Congress cataloging data. This records the source of the printed catalog metadata and does not assert an independently checked cataloging workflow.",
    },
    "st-fm-title-catalog-author-entry": {
        "segment": SEGMENT_2, "line": 21, "predicate": "catalog_author_entry",
        "subject": "cand-2962", "object": "cand-3770", "anchor": "Haskell, Francis, 1928-2000",
        "note": "The printed CIP block includes the Francis Haskell author entry. This preserves its catalog-record role and is not an independent identity verification.",
    },
    "st-fm-title-catalog-subject-baroque-italy": {
        "segment": SEGMENT_2, "line": 25, "predicate": "catalog_subject_heading",
        "subject": "cand-2962", "object": "cand-4132", "anchor": "Art, Baroque—Italy.",
        "note": "The printed CIP block lists 'Art, Baroque—Italy' as a catalog subject heading. This is catalog metadata, not a claim that the heading exhaustively describes the book.",
    },
    "st-fm-title-catalog-subject-italian-art": {
        "segment": SEGMENT_2, "line": 25, "predicate": "catalog_subject_heading",
        "subject": "cand-2962", "object": "cand-4131", "anchor": "I. Art, Italian.",
        "note": "The printed CIP block lists 'Art, Italian' as a catalog subject heading. This is catalog metadata, not a claim that the heading exhaustively describes the book.",
    },
    "st-fm-title-catalog-subject-art-patrons": {
        "segment": SEGMENT_2, "line": 26, "predicate": "catalog_subject_heading",
        "subject": "cand-2962", "object": "cand-4129", "anchor": "3. Art patrons.",
        "note": "The printed CIP block lists 'Art patrons' as a catalog subject heading. This is catalog metadata, not a claim that the heading exhaustively describes the book.",
    },
    "st-fm-title-catalog-subject-art-society": {
        "segment": SEGMENT_2, "line": 26, "predicate": "catalog_subject_heading",
        "subject": "cand-2962", "object": "cand-4130", "anchor": "4. Art and society.",
        "note": "The printed CIP block lists 'Art and society' as a catalog subject heading. This is catalog metadata, not a claim that the heading exhaustively describes the book.",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    actual_sha = sha256(raw)
    if actual_sha != EXPECTED_SHA256:
        raise SystemExit(f"input SHA mismatch: expected {EXPECTED_SHA256}, got {actual_sha}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(f)}
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mention_pairs = {(row["segment_id"], row["candidate_id"]) for row in csv.DictReader(f)}
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")

    for sid, spec in ROWS.items():
        if sid not in by_id:
            raise SystemExit(f"missing statement: {sid}")
        if spec["line"] > len(source_lines) or spec["anchor"] not in source_lines[spec["line"] - 1]:
            raise SystemExit(f"source anchor mismatch: {sid} L{spec['line']}")
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        if (row.get("segment_id") != spec["segment"] or row.get("source_file") != "02-sources/02-Markdown/00_01_Title_Copyright.md"
                or row.get("origin") != "book" or row.get("predicate") != spec["predicate"]
                or row.get("subject_candidate_id") != spec["subject"] or row.get("object_candidate_id") != spec["object"]
                or q.get("source_line_start") != spec["line"] or q.get("source_line_end") != spec["line"]
                or q.get("relation_candidate") is not None):
            raise SystemExit(f"statement preflight mismatch: {sid}")
        for endpoint in (spec["subject"], spec["object"]):
            if endpoint not in candidate_ids or (spec["segment"], endpoint) not in mention_pairs:
                raise SystemExit(f"candidate/mention preflight failed: {endpoint} in {spec['segment']}")

    updated = {}
    for sid, spec in ROWS.items():
        row = deepcopy(by_id[sid])
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = spec["note"]
        updated[sid] = row

    output = []
    seen = set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        sid = row["statement_id"]
        if sid in updated:
            output.append(json.dumps(updated[sid], ensure_ascii=False, separators=(",", ":")))
            seen.add(sid)
        else:
            output.append(line)
    if seen != set(ROWS):
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output) + "\n").encode("utf-8")

    print(f"preflight passed: {len(seen)}/{len(ROWS)} statements; source, endpoints, mentions and anchors verified; input_sha256={actual_sha}")
    print("records relation_candidate only; no candidates, mentions, statements or S6 relations added")
    if not args.apply:
        print("dry-run only; table unchanged")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(result)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={sha256(result)}")


if __name__ == "__main__":
    main()
