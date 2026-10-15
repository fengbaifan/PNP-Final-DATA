from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCES = ROOT
BODY_SEGMENT = "chp-8:08_CHP-8_sec_ii:l11-19"
NOTES_SEGMENT = "chp-8:08_CHP-8_sec_ii:l372-461"
CONTINUATION_SEGMENT = "chp-8:08_CHP-8_sec_ii:l21-35"
CHURCH_ID = "st-chp8-p215-church-work-began-1137"
CLASSICISING_ID = "st-chp8-p215-classicising-institutions-outside-rome"
NEGOTIATIONS_ID = "st-chp8-p215-negotiations-follow-relative-failure"
INFLUENCE_ID = "st-chp8-p215-one-collection-influential"
MECHANISM_ID = "st-chp8-p215-patronage-mechanism-and-roman-values"
NEGLECT_ID = "st-chp8-p215-provincial-collections-neglect-roman-painting"
ACK_ID = "st-chp8-p215-dora-coggiola-acknowledgment"
CONTINUATION_ID = "st-chp8-p216-negotiations-outcome"
BACKUP_SUFFIX = "bak-s2-chp8-p215-structural-endpoints-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "04f6e3ff158bd9353575063c08d1654a4730d6eab0f84d995473365d0fcb45ff",
    "mentions.csv": "4b43f599b09bfd9a9abdbb6f8377618ec24fc3aee5d01111711d634fb234b8e2",
    "book-statements.jsonl": "06a3a6819530b1fcd4298cd31bcd177779061d775500d3da81d8efd3a8baad9f",
}
EXPECTED_SEGMENT_HASHES = {
    BODY_SEGMENT: "131cfa5f062c6baf0c97e31844b950a27f45817e5442687f1935a2e38b153a00",
    NOTES_SEGMENT: "62a4611253d2bf05494ef55b0511b53861b0947a05aee1c7a9fdbab976ecbc3f",
    CONTINUATION_SEGMENT: "4f5d502c755d5a791200895b453b3a196db68632297a0864a37c4995a91c1039",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=fields, lineterminator=newline.decode("ascii"), extrasaction="raise"
    )
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open_relation(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def endpoint_counts(rows: list[dict[str, object]]) -> tuple[int, int, int, int]:
    opens = [row for row in rows if is_open_relation(row)]
    object_only = sum(bool(row.get("subject_candidate_id")) and not row.get("object_candidate_id") for row in opens)
    subject_only = sum(not row.get("subject_candidate_id") and bool(row.get("object_candidate_id")) for row in opens)
    both = sum(not row.get("subject_candidate_id") and not row.get("object_candidate_id") for row in opens)
    return len(opens), object_only, subject_only, both


def source_segment_text(segment: dict[str, object]) -> str:
    source = SOURCES / str(segment["source_file"])
    lines = source.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    actual = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(actual[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    segment_index = {row["segment_id"]: row for row in segment_rows}
    texts: dict[str, str] = {}
    for segment_id, expected_hash in EXPECTED_SEGMENT_HASHES.items():
        if segment_id not in segment_index or segment_index[segment_id].get("sha256") != expected_hash:
            raise ValueError(f"Source segment changed: {segment_id}")
        texts[segment_id] = source_segment_text(segment_index[segment_id])

    candidate_specs = [
        (
            "cand-12359",
            "Construction work on Santa Maria Maggiore in Bergamo (begun 1137)",
            "event",
            "Haskell dates the beginning of work to 1137 and says it continued fitfully for several centuries. This is an extended construction process, not a claim that all later additions formed one campaign.",
            BODY_SEGMENT,
            "Work on the church of Santa Maria Maggiore in Bergamo",
        ),
        (
            "cand-12360",
            "Relative failure of the Bergamo decoration search in Venice and Milan (Haskell's p.215 account)",
            "event",
            "Haskell says the renewed search in Venice and Milan met with relative failure before negotiations spread to towns across Italy. The exact agent, measure, and date of this failure are not specified.",
            BODY_SEGMENT,
            "Their relative failure",
        ),
        (
            "cand-12361",
            "Negotiations across Italian towns following the Bergamo decoration search",
            "event",
            "Haskell reports a complicated series of negotiations in towns all over Italy after the relative failure of the search in Venice and Milan. Participants, individual negotiations, and dates are not supplied; p.216 refers back to this series as 'these'.",
            BODY_SEGMENT,
            "a complicated series of negotiations in towns all over Italy",
        ),
        (
            "cand-12362",
            "Roman painting in Haskell's p.215 account of provincial collections",
            "term",
            "Roman painting as the artistic field Haskell says was neglected in the provincial collections discussed immediately before this passage; this term does not identify particular paintings.",
            BODY_SEGMENT,
            "Roman painting",
        ),
        (
            "cand-12363",
            "Classicising doctrines and institutions said to constrain Rome-going painters",
            "",
            "Haskell refers collectively to classicising doctrines and institutions that paralysed or boycotted many painters who went to Rome. No doctrine or institution is named; type remains unset because this combines concepts and organizations.",
            BODY_SEGMENT,
            "classicising doctrines and institutions",
        ),
        (
            "cand-12364",
            "Development of provincial art collections in Haskell's p.215 account",
            "event",
            "The historical development of the collections discussed in the Chapter 8 overview, treated by Haskell as evidence for a patronage mechanism. This is a broad source-described process, not a single dated event.",
            BODY_SEGMENT,
            "history of their development",
        ),
        (
            "cand-12365",
            "Unusual type of patronage in Haskell's account of provincial collections",
            "term",
            "The source-named patronage mechanism whose significance Haskell connects to his argument about the demolition of Roman values; retain that framing as his interpretation.",
            BODY_SEGMENT,
            "mechanism of an unusual type of patronage",
        ),
    ]
    candidate_index = {row["candidate_id"]: row for row in candidates}
    candidate_names = {row["canonical_name"] for row in candidates}
    new_candidates: list[dict[str, str]] = []
    new_mentions: list[dict[str, str]] = []
    def add_mention(
        mention_id: str,
        segment_id: str,
        candidate_id: str,
        surface: str,
        note: str,
        occurrence: int | None = None,
    ) -> None:
        text = texts[segment_id]
        matches = list(re.finditer(re.escape(surface), text))
        if not matches or (occurrence is None and len(matches) != 1):
            raise ValueError(f"Source phrase missing or repeated: {surface} in {segment_id}")
        index = 0 if occurrence is None else occurrence
        if index < 0 or index >= len(matches):
            raise ValueError(f"Occurrence {index} unavailable for {surface} in {segment_id}")
        start = matches[index].start()
        new_mentions.append(
            {
                "mention_id": mention_id,
                "segment_id": segment_id,
                "candidate_id": candidate_id,
                "surface_form": surface,
                "start_char": str(start),
                "end_char": str(start + len(surface)),
                "note": note,
            }
        )

    for cid, name, suggested_type, detail, segment_id, surface in candidate_specs:
        if cid in candidate_index or name in candidate_names:
            raise ValueError(f"Candidate ID or name already exists: {cid} / {name}")
        line = int(segment_index[segment_id]["line_start"]) + (
            texts[segment_id].count("\n", 0, texts[segment_id].find(surface))
        )
        new_candidates.append(
            {
                "candidate_id": cid,
                "index_entry_id": "",
                "canonical_name": name,
                "index_page_range": "",
                "suggested_type": suggested_type,
                "status": "open",
                "index_source_file": "",
                "sub_entry": "",
                "detail": detail,
                "exclude_reason": "",
                "candidate_origin": "body-mention",
                "candidate_source_ref": f"{segment_id}#L{line}",
            }
        )
        add_mention(
            f"m-chp8-{cid}-source-mention",
            segment_id,
            cid,
            surface,
            detail,
        )
        candidate_index[cid] = new_candidates[-1]
        candidate_names.add(name)

    add_mention(
        "m-chp8-p215-remote-places",
        BODY_SEGMENT,
        "cand-12353",
        "these out-of-the-way places",
        "Anaphoric reference to the source-defined group of provincial cities discussed on p.214.",
    )
    add_mention(
        "m-chp8-p215-collections-group",
        BODY_SEGMENT,
        "cand-12352",
        "these collections",
        "Anaphoric reference to the group of Italian art collections introduced on p.214.",
        occurrence=0,
    )
    add_mention(
        "m-chp8-p215-collections-influence-group",
        BODY_SEGMENT,
        "cand-12352",
        "these collections",
        "Second reference to the p.214 collection group, in the statement about their number and influence.",
        occurrence=1,
    )
    add_mention(
        "m-chp8-p215-collections-pronoun",
        BODY_SEGMENT,
        "cand-12352",
        "their",
        "Anaphoric reference to the collections in the phrase 'history of their development'.",
        occurrence=1,
    )
    add_mention(
        "m-chp8-p215-author-first-person",
        NOTES_SEGMENT,
        "cand-9423",
        "I",
        "First-person authorial voice in the acknowledgment; the title page identifies Francis Haskell as the book's author.",
        occurrence=1,
    )
    add_mention(
        "m-chp8-p216-negotiations-anaphora",
        CONTINUATION_SEGMENT,
        "cand-12361",
        "these",
        "Anaphoric reference to the negotiation series named at p.215 L19.",
    )

    existing_mention_ids = {row["mention_id"] for row in mentions}
    if existing_mention_ids & {row["mention_id"] for row in new_mentions}:
        raise ValueError("A planned mention ID already exists")
    if "cand-12352" not in candidate_index or "cand-12353" not in candidate_index:
        raise ValueError("The p.214 collection and city groups are missing")
    if candidate_index["cand-9423"].get("canonical_name") != "Francis Haskell (author named in p.290 note 1)":
        raise ValueError("Expected Francis Haskell candidate is missing")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: row for row in rows}
    ids = [
        CHURCH_ID,
        CLASSICISING_ID,
        NEGOTIATIONS_ID,
        INFLUENCE_ID,
        MECHANISM_ID,
        NEGLECT_ID,
        ACK_ID,
        CONTINUATION_ID,
    ]
    if any(statement_id not in statement_index for statement_id in ids):
        raise ValueError("One or more target statements are missing")
    church = statement_index[CHURCH_ID]
    classicising = statement_index[CLASSICISING_ID]
    negotiations = statement_index[NEGOTIATIONS_ID]
    influence = statement_index[INFLUENCE_ID]
    mechanism = statement_index[MECHANISM_ID]
    neglect = statement_index[NEGLECT_ID]
    acknowledgment = statement_index[ACK_ID]
    continuation = statement_index[CONTINUATION_ID]
    expected_open = {
        CHURCH_ID: ("cand-7627", None),
        CLASSICISING_ID: (None, None),
        NEGOTIATIONS_ID: (None, None),
        INFLUENCE_ID: (None, None),
        MECHANISM_ID: (None, None),
        NEGLECT_ID: (None, None),
        ACK_ID: (None, "cand-7658"),
    }
    for statement_id, expected in expected_open.items():
        row = statement_index[statement_id]
        if (
            row.get("subject_candidate_id"), row.get("object_candidate_id")
        ) != expected or not is_open_relation(row):
            raise ValueError(f"Target statement state changed: {statement_id}")
    if continuation.get("segment_id") != CONTINUATION_SEGMENT:
        raise ValueError("p.216 continuation statement changed")
    if endpoint_counts(rows) != (449, 278, 63, 108):
        raise ValueError(f"Unexpected pre-update endpoint counts: {endpoint_counts(rows)}")
    if sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in rows) != 10389:
        raise ValueError("Unexpected relation-candidate total")

    new_candidates_raw = append_csv(candidate_raw, candidate_fields, new_candidates)
    mention_after = append_csv(mention_raw, mention_fields, new_mentions)

    def set_endpoint(
        row: dict[str, object],
        subject: str | None,
        object_id: str | None,
        note: str,
        extra_ids: list[str],
    ) -> None:
        row["subject_candidate_id"] = subject
        row["object_candidate_id"] = object_id
        q = row.get("qualifiers") or {}
        q["mentioned_candidate_ids"] = list(
            dict.fromkeys((q.get("mentioned_candidate_ids") or []) + extra_ids)
        )
        q["relation_candidate_note"] = note
        q.pop("open_endpoint_reason", None)
        row["qualifiers"] = q

    set_endpoint(
        church,
        "cand-7627",
        "cand-12359",
        "The object is the extended construction process Haskell dates from 1137; later additions remain separate statements and works.",
        ["cand-12359"],
    )
    set_endpoint(
        classicising,
        "cand-12363",
        "cand-12353",
        "The endpoints are Haskell's unnamed group of classicising doctrines and institutions and the source-defined group of out-of-the-way provincial cities. No specific institution or doctrine is inferred.",
        ["cand-12363", "cand-12353"],
    )
    set_endpoint(
        negotiations,
        "cand-12360",
        "cand-12361",
        "The source links the relative failure of the search in Venice and Milan to subsequent negotiations across Italian towns. The exact agent and measure of failure remain unspecified; p.216's 'these' refers to the negotiation series.",
        ["cand-12360", "cand-12361"],
    )
    set_endpoint(
        mechanism,
        "cand-12364",
        "cand-12365",
        "Haskell interprets the development of the provincial collections as evidence for an unusual patronage mechanism. His phrase about the demolition of Roman values remains attributed interpretation.",
        ["cand-12352", "cand-12364", "cand-12365"],
    )
    set_endpoint(
        neglect,
        "cand-12352",
        "cand-12362",
        "Haskell describes neglect of Roman painting as a feature of the source-defined provincial collection group; no individual collection or painting is identified.",
        ["cand-12352", "cand-12362"],
    )
    set_endpoint(
        acknowledgment,
        "cand-9423",
        "cand-7658",
        "The first-person speaker is Francis Haskell, identified on the book's title page; the statement records his acknowledgment of Dora Coggiola without inferring her occupation.",
        ["cand-9423"],
    )
    for row in (church, classicising, negotiations, mechanism, neglect, acknowledgment):
        row.pop("qualification", None)
        row.pop("mentioned_candidate_ids", None)

    # The prior paragraph's collection-frequency claim and this statement refer to the
    # p.214 source-defined collection group; retain its lower-bound qualification.
    influence_q = influence.get("qualifiers") or {}
    influence_q["mentioned_candidate_ids"] = list(
        dict.fromkeys((influence_q.get("mentioned_candidate_ids") or []) + ["cand-12352"])
    )
    influence["qualifiers"] = influence_q

    continuation_q = continuation.get("qualifiers") or {}
    continuation_q["mentioned_candidate_ids"] = list(
        dict.fromkeys((continuation_q.get("mentioned_candidate_ids") or []) + ["cand-12361"])
    )
    resolution = continuation_q.get("anaphora_resolution") or {}
    resolution["candidate_id"] = "cand-12361"
    resolution["mention_id"] = "m-chp8-p216-negotiations-anaphora"
    continuation_q["anaphora_resolution"] = resolution
    continuation["qualifiers"] = continuation_q

    statement_after = (
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    ).encode("utf-8")
    after_rows = [
        json.loads(line) for line in statement_after.decode("utf-8").splitlines() if line.strip()
    ]
    after_counts = endpoint_counts(after_rows)
    p215_open = [
        row["statement_id"]
        for row in after_rows
        if row.get("segment_id") == BODY_SEGMENT and is_open_relation(row)
    ]
    expected_p215_open = [INFLUENCE_ID, "st-chp8-p215-local-capacity-and-foreign-commission"]
    if after_counts != (443, 277, 62, 104) or set(p215_open) != set(expected_p215_open):
        raise ValueError(f"Unexpected post-update endpoint state: {after_counts}, {p215_open}")

    print(f"candidate_rows={len(candidates)}->{len(candidates) + len(new_candidates)}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + len(new_mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    for row in new_candidates:
        print(f"planned_candidate={row['candidate_id']}|{row['suggested_type'] or 'type unresolved'}|{row['canonical_name']}")
    print(f"resolved_statements={CHURCH_ID},{CLASSICISING_ID},{NEGOTIATIONS_ID},{MECHANISM_ID},{NEGLECT_ID},{ACK_ID}")
    print(f"continued_anaphora={CONTINUATION_ID}|these->{ 'cand-12361' }")
    print(f"retained_open_statements={p215_open}")
    print(f"open_endpoints={(449, 278, 63, 108)}->{after_counts}")
    for name, before, after in (
        ("entity-candidates.csv", candidate_raw, new_candidates_raw),
        ("mentions.csv", mention_raw, mention_after),
        ("book-statements.jsonl", statement_raw, statement_after),
    ):
        print(f"{name} {digest(before)}->{digest(after)}")
    if args.preview:
        return 0

    paths = (
        (CANDIDATES, new_candidates_raw),
        (MENTIONS, mention_after),
        (STATEMENTS, statement_after),
    )
    pairs: list[tuple[Path, Path, Path, bytes]] = []
    for path, data in paths:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((path, backup, temp, data))
    for path, backup, _, _ in pairs:
        shutil.copy2(path, backup)
    replaced: list[tuple[Path, Path]] = []
    try:
        for _, _, temp, data in pairs:
            temp.write_bytes(data)
        for path, backup, temp, _ in pairs:
            temp.replace(path)
            replaced.append((path, backup))
    except Exception:
        for _, _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
        for path, backup in replaced:
            shutil.copy2(backup, path)
        raise
    for path, backup, _, _ in pairs:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
