from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/stages.md"
EXPECTED = {
    "book-statements.jsonl": "a69b6b68e50288d139844de16779c4724efa2b0a2c397864d4fe68b1610888ca",
    "entity-candidates.csv": "efcd5a91784101b9f50594f545ae6b1c6d26a416941632a16085614b3b27d57e",
    "mentions.csv": "2f63171eabe966cec2f78afe54cdbf77e42f22152fc97fb398a1d50e957a8372",
}
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_HASHES = {
    "chp-4:04_CHP-4_sec_ii:l101-107": "1a388b01323331b59dfef89a1df6f3545745e1fbf178394b49219c84d2f3bba7",
    "chp-4:04_CHP-4_sec_ii:l121-128": "0b07b284662fa705b1b4e46e7eb35db51c5d358d231c7fa4019efcc6572bca46",
}
GROUPS = [
    {
        "candidate_id": "cand-12394",
        "canonical_name": "Unidentified artists and scholars in Cassiano's contact network",
        "detail": "Haskell says Cassiano was in touch with artists and scholars of all kinds. This records the broad source-defined contact group; the individuals and membership are not listed, and it is not equated with the immediate Barberini entourage or the separate broader Barberini circle candidate.",
        "candidate_source_ref": "chp-4:04_CHP-4_sec_ii:l101-107#L105",
        "mention_id": "m-chp4-sec-ii-l101-107-cassiano-artist-scholar-group",
        "segment_id": "chp-4:04_CHP-4_sec_ii:l101-107",
        "surface_form": "artists and scholars of all kinds",
        "start_char": 1005,
        "end_char": 1038,
        "note": "Haskell's broad, unenumerated group of contacts for Cassiano; individual members and any formal organization are not supplied.",
        "statement_id": "st-chp4-sec-ii-l101-107-cassiano-contact-and-possible-echoes",
        "reason": "The wording defines a broad, unenumerated contact group but no named people or organization. The new open candidate records this source-defined endpoint only; it is not identified with the Barberini immediate entourage or cand-4969's wider Barberini circle.",
        "qualification": "The individuals and membership are unenumerated; the endpoint is represented only as the broad source-defined contact group, not as a formal institution or the separate Barberini circles.",
    },
    {
        "candidate_id": "cand-12395",
        "canonical_name": "Unidentified local ecclesiastics displeased by Gaudenzi's history",
        "detail": "Haskell reports that conclusions in Gaudenzi's History of the early church displeased 'Ecclesiastiques de ce pays'. No individual, number, institution, or precise locality is named; retain this source-defined group without assigning a type or identifying it with the Jesuits mentioned nearby.",
        "candidate_source_ref": "chp-4:04_CHP-4_sec_ii:l121-128#L123",
        "mention_id": "m-chp4-sec-ii-p109-local-ecclesiastics",
        "segment_id": "chp-4:04_CHP-4_sec_ii:l121-128",
        "surface_form": "Ecclesiastiques de ce pays",
        "start_char": 1026,
        "end_char": 1052,
        "note": "French phrase for local ecclesiastics whose response Haskell reports; members, number, and precise locality remain unspecified.",
        "statement_id": "st-chp4-sec-ii-p109-gaudenzi-history-conclusions",
        "reason": "The source identifies an affected class as ecclesiastics of this country but names no members, count, institution, or precise locality. The open candidate preserves the source-defined group without equating it with the Jesuits mentioned elsewhere.",
        "qualification": "The affected group is unnamed and unenumerated; no member, number, specific institution, or precise locality is inferred.",
    },
]
REASON_ONLY = {
    "st-chp4-sec-ii-l101-107-possible-schismatic-sect": "Haskell poses an unspecified schismatic sect only as a possible interpretation of Poussin's religious views. The passage names no sect and asserts no affiliation; the existing S2 review explicitly leaves this as a hypothesis and does not create an unnamed sect candidate.",
    "st-chp4-sec-ii-l101-107-possible-echoes-in-other-works": "Haskell tentatively suggests that echoes of Cassiano's ideas may appear in other works, but names no target work or bounded work group. Preserve this as an authorial hypothesis with its target open; do not invent a generic work endpoint.",
}
BACKUPS = {
    STATEMENTS: STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-p107-p109-open-groups-20261015"),
    CANDIDATES: CANDIDATES.with_name("entity-candidates.csv.bak-s2-chp4-p107-p109-open-groups-20261015"),
    MENTIONS: MENTIONS.with_name("mentions.csv.bak-s2-chp4-p107-p109-open-groups-20261015"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def open_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    opened = [
        row for row in rows
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    ]
    obj_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opened)
    subj_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opened)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opened)
    return len(opened), obj_only, subj_only, both


def no_reason_count(rows: list[dict]) -> int:
    return sum(
        1 for row in rows
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
        and not (row.get("qualifiers") or {}).get("open_endpoint_reason")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    paths = {path.name: path for path in (STATEMENTS, CANDIDATES, MENTIONS)}
    raw = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED.items():
        if digest(raw[name]) != expected:
            raise ValueError(f"protected table changed: {name}: {digest(raw[name])}")
    if digest(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("chapter 4 source asset changed")
    segments = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    for segment_id, expected in SEGMENT_HASHES.items():
        seg = segments.get(segment_id)
        if not seg or seg.get("sha256") != expected or seg.get("asset_sha256") != SOURCE_SHA256:
            raise ValueError(f"reviewed segment changed: {segment_id}")

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    for evidence in (
        "Jansenism? Some schismatic sect? Possibly.",
        "Cassiano was in touch with artists and scholars of all kinds",
        "had come to conclusions in his History of the early church",
    ):
        if evidence not in process_text and evidence not in SOURCE.read_text(encoding="utf-8-sig"):
            raise ValueError(f"required source/process evidence missing: {evidence}")

    statements = [json.loads(line) for line in raw[STATEMENTS.name].decode("utf-8-sig").splitlines() if line.strip()]
    candidates = read_csv(CANDIDATES)
    mentions = read_csv(MENTIONS)
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(statement_by_id) != len(statements) or len(candidate_by_id) != len(candidates) or len(mention_by_id) != len(mentions):
        raise ValueError("duplicate primary IDs in protected tables")
    if open_counts(statements) != (390, 244, 46, 100) or no_reason_count(statements) != 75:
        raise ValueError(f"unexpected open-endpoint baseline: counts={open_counts(statements)}, no_reason={no_reason_count(statements)}")
    if any(group["candidate_id"] in candidate_by_id for group in GROUPS):
        raise ValueError("a planned candidate ID already exists")
    if any(group["mention_id"] in mention_by_id for group in GROUPS):
        raise ValueError("a planned mention ID already exists")
    for group in GROUPS:
        row = statement_by_id.get(group["statement_id"])
        if not row or row.get("object_candidate_id") is not None or not row.get("subject_candidate_id"):
            raise ValueError(f"expected open endpoint changed: {group['statement_id']}")
        if (row.get("qualifiers") or {}).get("open_endpoint_reason"):
            raise ValueError(f"expected row without endpoint reason changed: {group['statement_id']}")
    for statement_id in REASON_ONLY:
        row = statement_by_id.get(statement_id)
        if not row or not row.get("subject_candidate_id") or row.get("object_candidate_id") or (row.get("qualifiers") or {}).get("open_endpoint_reason"):
            raise ValueError(f"expected open hypothesis changed: {statement_id}")

    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_texts = {
        "chp-4:04_CHP-4_sec_ii:l101-107": "\n".join(lines[100:107]),
        "chp-4:04_CHP-4_sec_ii:l121-128": "\n".join(lines[120:128]),
    }
    for group in GROUPS:
        text = source_texts[group["segment_id"]]
        start, end, surface = group["start_char"], group["end_char"], group["surface_form"]
        if text[start:end] != surface:
            raise ValueError(f"new evidence span does not match S0: {group['mention_id']}")
        if any(
            m["segment_id"] == group["segment_id"]
            and int(m["start_char"]) < end and start < int(m["end_char"])
            for m in mentions
        ):
            raise ValueError(f"new evidence span overlaps an existing mention: {group['mention_id']}")

        candidate = {
            "candidate_id": group["candidate_id"],
            "index_entry_id": "",
            "canonical_name": group["canonical_name"],
            "index_page_range": "",
            "suggested_type": "",
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": group["detail"],
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": group["candidate_source_ref"],
        }
        mention = {
            "mention_id": group["mention_id"],
            "segment_id": group["segment_id"],
            "candidate_id": group["candidate_id"],
            "surface_form": group["surface_form"],
            "start_char": str(group["start_char"]),
            "end_char": str(group["end_char"]),
            "note": group["note"],
        }
        candidates.append(candidate)
        mentions.append(mention)
        statement = statement_by_id[group["statement_id"]]
        statement["object_candidate_id"] = group["candidate_id"]
        q = statement["qualifiers"]
        q["qualification"] = group["qualification"]
        q["mentioned_candidate_ids"] = list(dict.fromkeys((q.get("mentioned_candidate_ids") or []) + [group["candidate_id"]]))
        q["relation_candidate_note"] = group["reason"]
        q.pop("open_endpoint_reason", None)

    for statement_id, reason in REASON_ONLY.items():
        statement_by_id[statement_id]["qualifiers"]["open_endpoint_reason"] = reason

    if len({row["candidate_id"] for row in candidates}) != len(candidates):
        raise ValueError("candidate IDs are not unique after preparation")
    if len({row["mention_id"] for row in mentions}) != len(mentions):
        raise ValueError("mention IDs are not unique after preparation")
    if open_counts(statements) != (388, 242, 46, 100) or no_reason_count(statements) != 71:
        raise ValueError(f"unexpected post-reconciliation counts: {open_counts(statements)}, no_reason={no_reason_count(statements)}")

    output = {
        STATEMENTS: "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in statements).encode("utf-8"),
        CANDIDATES: write_csv(candidates),
        MENTIONS: write_csv(mentions),
    }
    print("resolved=two source-defined unnamed groups: Cassiano's artists/scholars contacts and the local ecclesiastics affected by Gaudenzi's history")
    print("preserved_open=the speculative schismatic-sect interpretation and unidentified works in Haskell's possible-echoes hypothesis")
    print("added=2 untyped open candidates, 2 exact mentions; statements unchanged")
    print(f"open_endpoints=(390,244,46,100)->{open_counts(statements)}; no_reason_open=75->71")
    for path, data in output.items():
        print(f"{path.name} sha256 {digest(raw[path.name])}->{digest(data)}")
    if args.preview:
        return 0
    if any(backup.exists() for backup in BACKUPS.values()):
        raise FileExistsError("one or more recovery copies already exist")
    temps = {path: path.with_name(path.name + ".tmp-s2-chp4-p107-p109-open-groups-20261015") for path in output}
    if any(temp.exists() for temp in temps.values()):
        raise FileExistsError("one or more temporary table files already exist")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    try:
        for path, data in output.items():
            temps[path].write_bytes(data)
        for path, temp in temps.items():
            temp.replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in BACKUPS.items():
            shutil.copy2(backup, path)
        raise
    print("backups=" + ",".join(backup.relative_to(ROOT).as_posix() for backup in BACKUPS.values()))
    for path in output:
        print(f"applied_{path.name}_sha256={digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
