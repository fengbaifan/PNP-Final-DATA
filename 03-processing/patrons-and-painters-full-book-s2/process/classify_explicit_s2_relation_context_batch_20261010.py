from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
EXPECTED_SHA = "1570c12b24fe6eb9bbec5c19dce369728cd330083b1898b445fc31932d110c47"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-explicit-relation-context-20261010")

SPECS = {
    "st-chp2-seci-l44-53-andrians-transfer": (
        "The Andrians",
        "Haskell explicitly includes The Andrians among Titian paintings Cardinal Aldobrandini brought to Rome. This remains a source report; footnote 3 is a source lead.",
    ),
    "st-chp2-seci-l44-53-bacchus-transfer": (
        "Bacchus and Ariadne",
        "Haskell explicitly includes Bacchus and Ariadne among Titian paintings Cardinal Aldobrandini brought to Rome. This remains a source report; footnote 3 is a source lead.",
    ),
    "st-chp2-seci-l44-53-worship-transfer": (
        "Worship os Venus",
        "Haskell explicitly includes The Worship of Venus among Titian paintings Cardinal Aldobrandini brought to Rome. Preserve the documented print correction of OCR 'os' to 'of'; footnote 3 is a source lead.",
    ),
    "st-chp2-seciv-l171-179-poussin-painted-dance-of-human-life": (
        "The Dance of Human Life",
        "Haskell explicitly names The Dance of Human Life among Poussin's three paintings of the moral poems. The possible Rospigliosi commission remains uncertain.",
    ),
    "st-chp2-seciv-l171-179-poussin-painted-happiness-subject-to-death": (
        "Happiness subject to Death",
        "Haskell explicitly names Happiness subject to Death, parenthetically The Arcadian Shepherds, among Poussin's three paintings. The possible Rospigliosi commission remains uncertain.",
    ),
    "st-chp2-seciv-l171-179-poussin-painted-truth-uncovered-by-time": (
        "Truth uncovered by Time",
        "Haskell explicitly names Truth uncovered by Time among Poussin's three paintings of the moral poems. The possible Rospigliosi commission remains uncertain.",
    ),
    "st-chp13-p336-pasquali-friend-of-albergati-capacelli": (
        "Francesco Albergati-Capacelli",
        "Haskell names Albergati-Capacelli as one of Pasquali's non-conforming friends. The source does not specify duration or context.",
    ),
    "st-chp13-p336-pasquali-friend-of-pilati": (
        "Carlo Antonio",
        "Haskell names Pilati as one of Pasquali's non-conforming friends. The source does not specify duration or context.",
    ),
    "st-chp13-p336-pasquali-friend-of-querini": (
        "Angelo Querini",
        "Haskell names Querini as one of Pasquali's non-conforming friends. The source does not specify duration or context.",
    ),
    "st-fm-c-preface-calvocoressi-reading": (
        "Peter Calvocoressi",
        "Haskell explicitly thanks Calvocoressi for reading and greatly improving the typescript; this is an acknowledgment claim, not an employment or formal affiliation.",
    ),
    "st-fm-c-preface-mahon-reading": (
        "Denis Mahon",
        "Haskell explicitly thanks Mahon for reading and greatly improving the typescript; this is an acknowledgment claim, not an employment or formal affiliation.",
    ),
    "st-fm-c-preface-waterhouse-reading": (
        "Ellis Waterhouse",
        "Haskell explicitly thanks Waterhouse for reading and greatly improving the typescript; this is an acknowledgment claim, not an employment or formal affiliation.",
    ),
    "st-fm-b2-blunt": (
        "Anthony Blunt",
        "Haskell explicitly credits Blunt with pointing out mistakes and emphasizes his contribution; no broader role is inferred.",
    ),
    "st-fm-b2-enggass": (
        "Robert Enggass",
        "Haskell explicitly credits Enggass with pointing out mistakes; no broader role is inferred.",
    ),
    "st-fm-b2-hibbard": (
        "Howard Hibbard",
        "Haskell explicitly credits Hibbard with pointing out mistakes; no broader role is inferred.",
    ),
    "st-chp7-p194-bologna-affected-by-patronage": (
        "Bologna",
        "Haskell explicitly names Bologna as one of three cities principally affected by the new German source of patronage; the source's 'principally' and comparative scope are retained.",
    ),
    "st-chp7-p194-rome-affected-by-patronage": (
        "Rome",
        "Haskell explicitly names Rome as one of three cities principally affected by the new German source of patronage; the source's 'principally' and comparative scope are retained.",
    ),
    "st-chp7-p194-venice-affected-by-patronage": (
        "Venice",
        "Haskell explicitly names Venice as one of three cities principally affected by the new German source of patronage; the source's 'principally' and comparative scope are retained.",
    ),
    "st-chp3-seci-l35-43-bentivoglio-citation": (
        "Bentivoglio, 1807, p. 48",
        "The footnote explicitly cites Bentivoglio (1807, p. 48) in connection with the preceding account; the cited source was not independently consulted.",
    ),
    "st-chp3-seci-l35-43-canonization-volume-citation": (
        "La Canonizazzione dei Santi",
        "The footnote explicitly cites the 1923 canonisation-centenary volume in connection with the account and paintings; bibliographic identification remains provisional.",
    ),
    "st-chp3-seci-l35-43-delumeau-citation": (
        "Delumeau, pp. 238-41",
        "The footnote explicitly cites Delumeau for the preceding expropriation passage; title and edition remain unspecified, and the note does not resolve the historical claim.",
    ),
    "st-chp3-seci-l35-43-pastor-citation": (
        "Pastor, XIII, pp. 610-11",
        "The footnote explicitly cites Pastor for the picture recording Urban VIII's visit; the cited edition remains unspecified.",
    ),
    "st-chp10-p329-n03-bassi-academy-study": (
        "E. Bassi, 1941",
        "Haskell's note explicitly cites Bassi (1941) in the Venetian Academy discussion; the publication was not independently consulted.",
    ),
    "st-chp10-p329-n03-fogolari-academy-study": (
        "Fogolari, 1913",
        "Haskell's note explicitly cites Fogolari (1913) in the Venetian Academy discussion; the publication was not independently consulted.",
    ),
    "st-fm-b2-boucher": (
        "Bruce Boucher",
        "Haskell thanks Boucher for bibliography and illustration suggestions and other help; the unspecified additional help is not elaborated.",
    ),
    "st-fm-b2-chiarini": (
        "Chiarini",
        "Haskell thanks Chiarini for bibliography and illustration suggestions and other help; his name crosses the source line break.",
    ),
    "st-fm-b2-harris": (
        "Aim Sutherland Harris",
        "Haskell thanks the person represented as 'Aim Sutherland Harris' in OCR; earlier scan review supports candidate Ann Sutherland Harris. The scope of other help is unspecified.",
    ),
    "st-fm-b2-rolandmichel": (
        "Marianne Roland-Michel",
        "Haskell thanks Roland-Michel for bibliography and illustration suggestions and other help; the unspecified additional help is not elaborated.",
    ),
    "st-fm-b2-rosenberg": (
        "Pierre Rosenberg",
        "Haskell thanks Rosenberg for bibliography and illustration suggestions and other help; the unspecified additional help is not elaborated.",
    ),
}

CONTEXT_CHECKS = {
    "st-chp2-seci-l44-53-andrians-transfer": {49: "Cardinal Aldobrandini", 50: "Rome were Titian’s"},
    "st-chp2-seci-l44-53-bacchus-transfer": {49: "Cardinal Aldobrandini", 50: "Rome were Titian’s"},
    "st-chp2-seci-l44-53-worship-transfer": {49: "Cardinal Aldobrandini", 50: "Rome were Titian’s"},
    "st-chp13-p336-pasquali-friend-of-albergati-capacelli": {49: "the friend of non-conforming spirits"},
    "st-chp13-p336-pasquali-friend-of-pilati": {49: "the friend of non-conforming spirits"},
    "st-chp13-p336-pasquali-friend-of-querini": {49: "the friend of non-conforming spirits"},
    "st-fm-b2-chiarini": {12: "Marco", 13: "Chiarini"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows():
    raw = TABLE.read_bytes()
    require(sha256(TABLE) == EXPECTED_SHA, "book-statements.jsonl changed since review")
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({r["statement_id"] for r in rows}) == len(rows), "duplicate statement_id")
    by_id = {r["statement_id"]: r for r in rows}
    require(set(SPECS) <= set(by_id), "one or more reviewed statement IDs are absent")
    with (ROOT / "04-knowledge/tables/entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {r["candidate_id"] for r in csv.DictReader(handle)}
    with (ROOT / "04-knowledge/tables/s2-coverage.csv").open(encoding="utf-8-sig", newline="") as handle:
        segment_ids = {r["segment_id"] for r in csv.DictReader(handle)}

    for statement_id, (expected_text, _) in SPECS.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        require(qualifiers.get("relation_candidate") not in (True, False),
                f"{statement_id} already classified")
        require(row.get("subject_candidate_id") in candidate_ids and
                row.get("object_candidate_id") in candidate_ids,
                f"{statement_id} has a missing candidate endpoint")
        require(row.get("segment_id") in segment_ids, f"{statement_id} has no S2 coverage segment")
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and start <= end,
                f"{statement_id} has no valid source line anchor")
        source = ROOT / row["source_file"]
        require(source.is_file(), f"{statement_id} source file does not exist")
        lines = source.read_text(encoding="utf-8").splitlines()
        require(end <= len(lines) and any(expected_text in lines[n - 1] for n in range(start, end + 1)),
                f"{statement_id} anchor text does not match the reviewed source")
        for context_line, context_text in CONTEXT_CHECKS.get(statement_id, {}).items():
            require(context_line <= len(lines) and context_text in lines[context_line - 1],
                    f"{statement_id} context line {context_line} no longer matches")
    return rows, bom, newline


def counts(rows: list[dict]) -> dict[str, int]:
    flag = lambda r: (r.get("qualifiers") or {}).get("relation_candidate")
    true_rows = [r for r in rows if flag(r) is True]
    false_rows = [r for r in rows if flag(r) is False]
    complete = lambda r: bool(r.get("subject_candidate_id") and r.get("object_candidate_id"))
    return {
        "statements": len(rows),
        "relation_true": len(true_rows),
        "relation_true_with_two_endpoints": sum(complete(r) for r in true_rows),
        "relation_true_open": sum(not complete(r) for r in true_rows),
        "relation_false": len(false_rows),
        "double_endpoint_unclassified": sum(
            complete(r) and flag(r) not in (True, False) for r in rows
        ),
    }


def serialize(rows: list[dict], bom: bool, newline: bytes) -> bytes:
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    return b"".join(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write reviewed S2 classifications; default is dry-run")
    args = parser.parse_args()
    rows, bom, newline = read_rows()
    before = counts(rows)
    require(before == {
        "statements": 12682,
        "relation_true": 3719,
        "relation_true_with_two_endpoints": 3703,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4370,
    }, f"unexpected before counts: {before}")
    by_id = {r["statement_id"]: r for r in rows}
    for statement_id, (_, note) in SPECS.items():
        qualifiers = dict(by_id[statement_id].get("qualifiers") or {})
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        by_id[statement_id]["qualifiers"] = qualifiers
    after = counts(rows)
    require(after == {
        "statements": 12682,
        "relation_true": 3748,
        "relation_true_with_two_endpoints": 3732,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4341,
    }, f"unexpected projected counts: {after}")
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "reviewed_statement_count": len(SPECS),
        "statement_ids": list(SPECS),
        "source_anchors_and_context_checked": len(SPECS),
        "before": before,
        "after": after,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    require(not BACKUP.exists(), f"recovery backup already exists: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".tmp-", delete=False) as handle:
            handle.write(serialize(rows, bom, newline))
            temp_path = Path(handle.name)
        os.replace(temp_path, TABLE)
        written = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        require(counts(written) == after, "post-write counts do not match preview")
        by_written_id = {r["statement_id"]: r for r in written}
        require(all((by_written_id[sid].get("qualifiers") or {}).get("relation_candidate") is True
                    for sid in SPECS), "one or more classifications were not persisted")
        print(json.dumps({
            "result": "applied",
            "counts": counts(written),
            "sha256": sha256(TABLE),
            "backup": str(BACKUP.relative_to(ROOT)),
        }, ensure_ascii=False, indent=2))
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    main()
