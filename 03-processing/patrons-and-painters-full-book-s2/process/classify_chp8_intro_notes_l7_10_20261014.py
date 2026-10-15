from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
SEGMENT = "chp-8:08_CHP-8_intro:l7-10"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp8-intro-notes-l7-10-20261014")

EXPECTED_HASHES = {
    STATEMENTS.name: "79ba5a084f723a5ceec02bbd88d8f6c17f7880da25ec527c6b43645b15b93837",
    CANDIDATES.name: "ed1a698cad783887d9f511972c329cd1a649b1d1ab924255ad996893675020c3",
    MENTIONS.name: "8976f979a97de735298020f8438d40eeba2e37b02e54901d308322393a21ccea",
    SEGMENTS.name: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE.name: "29f190c6512fa5512cc31f73ae1f9cc68f5943139e49cedf88303f88660a0c10",
    PDF.name: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
}
EXPECTED_SEGMENT_SHA = "6288828c4cd4e618176f4802cadf1ca1c0e454e2561dcf97585170fa20856328"

CITATIONS = {
    "st-chp8-p203-n1-soprani": {
        "publication": "cand-5160", "locator": "passim",
        "claim": "Haskell's p.203 footnote 1 cites Soprani, passim, as a general reference for the Genoa account.",
        "qualification": "The note gives no specific page; the cited work was not independently consulted.",
    },
    "st-chp8-p203-n2-naples-citations": {
        "publication": "cand-4835", "locator": "passim",
        "claim": "Haskell's p.203 footnote 2 cites de Dominici, passim, in connection with the Naples account.",
        "qualification": "This is a general bibliographic pointer; the cited work was not independently consulted.",
    },
    "st-chp8-p203-n2-cite-maresca": {
        "publication": "cand-7388", "locator": "p. 49",
        "claim": "Haskell's p.203 footnote 2 cites Maresca di Serracapriola, p.49, in connection with the Naples account.",
        "qualification": "The article identity is taken from the bibliography candidate; that bibliography segment remains pending S2 review, and the cited page was not independently read.",
    },
    "st-chp8-p203-n3-bologna-citations": {
        "publication": "cand-6933", "locator": "passim",
        "claim": "Haskell's p.203 footnote 3 cites Malvasia, passim, as a general reference for the Bologna family collections.",
        "qualification": "The note gives no specific page; the cited work was not independently consulted. The full source phrase names Zanotti as a separate reference.",
    },
    "st-chp8-p203-n3-cite-zanotti": {
        "publication": "cand-7115", "locator": "passim",
        "claim": "Haskell's p.203 footnote 3 also cites Zanotti, passim, as a general reference for the Bologna family collections.",
        "qualification": "The note gives no specific page; the cited work was not independently consulted. The full source phrase also names Malvasia.",
    },
    "st-chp8-p203-n4-ruffo-citation": {
        "publication": "cand-7261", "locator": "pp. 122–123",
        "claim": "Haskell's p.203 footnote 4 cites Ruffo, pp.122–123, for the Malpighi and Reni passage.",
        "qualification": "The short citation is resolved through the current bibliography candidate to Agnelli's Galleria di pitture del Card. Tomm. Ruffo; the bibliography's S2 review and the cited pages remain pending.",
    },
}

EXPECTED_IDS = {
    "st-chp8-p203-n1-soprani",
    "st-chp8-p203-n2-naples-citations",
    "st-chp8-p203-n3-bologna-citations",
    "st-chp8-p203-n4-ruffo-citation",
}
NEW_ROWS = {
    "st-chp8-p203-n2-cite-maresca": ("st-chp8-p203-n2-naples-citations", "cand-7388", "Maresca di Serracapriola, p. 49"),
    "st-chp8-p203-n3-cite-zanotti": ("st-chp8-p203-n3-bologna-citations", "cand-7115", "Malvasia and Zanotti, passim."),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after all guards pass")
    args = parser.parse_args()

    paths = [STATEMENTS, CANDIDATES, MENTIONS, SEGMENTS, SOURCE, PDF]
    raw = {path: path.read_bytes() for path in paths}
    hashes = {path.name: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: {hashes}")
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")

    with SEGMENTS.open("r", encoding="utf-8") as stream:
        segment_rows = [json.loads(line) for line in stream]
    segment = next(row for row in segment_rows if row["segment_id"] == SEGMENT)
    if segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("p.203 footnote segment hash changed")
    source_text = raw[SOURCE].decode("utf-8")
    for excerpt in (
        "See Soprani, passim.",
        "See de Dominici, passim, and Maresca di Serracapriola, p. 49.",
        "See Malvasia and Zanotti, passim.",
        "Ruffo, pp. 122-3.",
    ):
        if excerpt not in source_text:
            raise SystemExit(f"source excerpt not found: {excerpt!r}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8").splitlines()]
    by_id = {row["statement_id"]: row for row in rows}
    current = [row for row in rows if row.get("segment_id") == SEGMENT]
    if len(current) != 4 or {row["statement_id"] for row in current} != EXPECTED_IDS:
        raise SystemExit("p.203 footnote statement set changed")
    if any((row.get("qualifiers") or {}).get("relation_candidate") is not None for row in current):
        raise SystemExit("expected all four p.203 note rows to be unset")
    if not set(CITATIONS) == EXPECTED_IDS | set(NEW_ROWS):
        raise SystemExit("citation map does not cover split p.203 notes")
    if any(sid in by_id for sid in NEW_ROWS):
        raise SystemExit("new p.203 citation statement id already exists")

    with CANDIDATES.open("r", encoding="utf-8-sig", newline="") as stream:
        candidate_ids = {row["candidate_id"] for row in __import__("csv").DictReader(stream)}
    required = {"cand-2962", "cand-5160", "cand-4835", "cand-7388", "cand-7389", "cand-6933", "cand-7115", "cand-7261"}
    if not required <= candidate_ids:
        raise SystemExit(f"missing citation candidate ids: {sorted(required - candidate_ids)}")

    with MENTIONS.open("r", encoding="utf-8", newline="") as stream:
        mention_rows = list(__import__("csv").DictReader(stream))
    segment_mentions = {(row["candidate_id"], row["surface_form"]) for row in mention_rows if row["segment_id"] == SEGMENT}
    required_mentions = {
        ("cand-5160", "Soprani"), ("cand-4835", "de Dominici"),
        ("cand-7389", "Maresca di Serracapriola"), ("cand-6933", "Malvasia"),
        ("cand-7115", "Zanotti"), ("cand-7261", "Ruffo"),
    }
    if not required_mentions <= segment_mentions:
        raise SystemExit(f"missing citation surface mentions: {sorted(required_mentions - segment_mentions)}")

    # Separate the two-publication note 2 and note 3 into one source-to-publication claim each.
    by_id["st-chp8-p203-n2-naples-citations"]["original_quote"] = "de Dominici, passim"
    nq = dict(by_id["st-chp8-p203-n2-naples-citations"].get("qualifiers") or {})
    nq["mentioned_candidate_ids"] = ["cand-4835"]
    by_id["st-chp8-p203-n2-naples-citations"]["qualifiers"] = nq

    bologna = by_id["st-chp8-p203-n3-bologna-citations"]
    bologna["original_quote"] = "Malvasia and Zanotti, passim."

    for sid, (base_id, publication, quote) in NEW_ROWS.items():
        base = by_id[base_id]
        q = dict(base.get("qualifiers") or {})
        q["mentioned_candidate_ids"] = [publication, "cand-2962"]
        if publication == "cand-7388":
            q["mentioned_candidate_ids"].append("cand-7389")
        new_row = {
            "statement_id": sid, "segment_id": SEGMENT,
            "subject_candidate_id": None, "object_candidate_id": publication,
            "predicate": "footnote_citation", "qualifiers": q,
            "original_quote": quote, "origin": "book", "source_file": SOURCE.relative_to(ROOT).as_posix(),
        }
        rows.append(new_row)
        by_id[sid] = new_row

    body_id_by_citation = {}
    for sid, info in CITATIONS.items():
        if sid in NEW_ROWS:
            base_id = NEW_ROWS[sid][0]
            body_ids = list((by_id[base_id].get("qualifiers") or {}).get("linked_body_statement_ids") or [])
        else:
            body_ids = list((by_id[sid].get("qualifiers") or {}).get("linked_body_statement_ids") or [])
        if not body_ids:
            raise SystemExit(f"missing body link for {sid}")
        body_rows = [by_id[body_id] for body_id in body_ids]
        body_segments = {body["segment_id"] for body in body_rows}
        body_lines = sorted({body["qualifiers"]["source_line_start"] for body in body_rows})
        if len(body_segments) != 1:
            raise SystemExit(f"citation points across body segments unexpectedly: {sid}")

        row = by_id[sid]
        publication = info["publication"]
        q = dict(row.get("qualifiers") or {})
        mentions = list(dict.fromkeys([publication, "cand-2962", *(q.get("mentioned_candidate_ids") or [])]))
        q.update({
            "claim": info["claim"], "speaker": "Haskell footnote",
            "text_layer": "bibliographic citation to publication",
            "qualification": info["qualification"], "mentioned_candidate_ids": mentions,
            "citations": [{"source_candidate_id": "cand-2962", "publication_candidate_id": publication, "locator": info["locator"]}],
            "citation_publication_candidate_id": publication, "citation_locator": info["locator"],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": info["claim"] + " The cited material was not independently consulted.",
            "footnote_number": q.get("footnote_marker"), "footnote_segment": SEGMENT,
            "related_segment": next(iter(body_segments)), "related_source_lines": body_lines,
            "related_body_statement_ids": body_ids,
            "footnote_refs": [{
                "marker": q.get("footnote_marker"), "segment_id": next(iter(body_segments)),
                "source_line": line, "statement_ids": body_ids,
            } for line in body_lines],
            "footnote_link_status": "linked", "footnote_body_link_status": "linked", "footnote_text_pending": False,
        })
        row["subject_candidate_id"] = "cand-2962"
        row["object_candidate_id"] = publication
        row["predicate"] = "cites"
        row["qualifiers"] = q
        body_id_by_citation[sid] = body_ids

    counts = {
        "statements": len(rows),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in rows),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in rows),
        "unset": sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in rows),
    }
    if counts != {"statements": 14204, "true": 8850, "false": 3439, "unset": 1915}:
        raise SystemExit(f"unexpected post-counts: {counts}")

    for sid, info in CITATIONS.items():
        row = by_id[sid]
        if (row["subject_candidate_id"], row["object_candidate_id"], row["predicate"]) != ("cand-2962", info["publication"], "cites"):
            raise SystemExit(f"citation endpoints not normalized: {sid}")
        q = row["qualifiers"]
        if q.get("citation_locator") != info["locator"] or not q.get("cited_material_not_independently_consulted"):
            raise SystemExit(f"citation locator/status error: {sid}")

    after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
    report = {
        "mode": "apply" if args.apply else "dry_run", "segment": SEGMENT,
        "normalized_citation_rows": len(CITATIONS), "new_atomic_citations": len(NEW_ROWS),
        "split_sources": {"note_2": ["de Dominici", "Maresca di Serracapriola"], "note_3": ["Malvasia", "Zanotti"]},
        "post_counts": counts, "input_sha256": hashes,
        "after_statement_sha256": sha(after), "backup": str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return

    BACKUP.write_bytes(raw[STATEMENTS])
    atomic_write(STATEMENTS, after)
    if sha(STATEMENTS.read_bytes()) != report["after_statement_sha256"]:
        raise SystemExit("post-write statement hash mismatch")
    print("applied; recovery copy written; statement hash verified")


if __name__ == "__main__":
    main()
