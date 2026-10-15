from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SEGMENT = "chp-2:02_CHP-2_sec_ii:l20-28"
EXPECTED_SHA = "6120db88ad9cbb35777d02c9afef22ac65df1cdf3ee705d8ec82dd34c0ed8f44"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l20-28-20261010")
TRUE_NOTES = {
    "st-chp2-sec-ii-l20-28-architecture-decoration-and-persuasion":
        "Haskell links Urban VIII's support for ecclesiastical art to an intended persuasive effect, while limiting the motive to 'at least partly'. Preserve the author's interpretation.",
    "st-chp2-sec-ii-l20-28-counter-reformation-and-spiritual-crisis":
        "The source directly contrasts the Counter Reformation's severity with the spiritual crisis revealed when it was relaxed; evaluative language remains Haskell's.",
    "st-chp2-sec-ii-l20-28-intellectual-changes-affect-papacy":
        "Haskell says the listed intellectual and spiritual currents emerged and affected the papacy. The spiritual-crisis candidate is the source-framed aggregate, not a claim that any one named person caused the change.",
    "st-chp2-sec-ii-l20-28-naude-french-quotation":
        "This records Naudé's mediated quotation about Rome and the Roman Court, with Rome and Italy retained as additional referents. The quotation's population descriptions are not independently verified.",
    "st-chp2-sec-ii-l20-28-papacy-status-threats":
        "Haskell frames Urban VIII's leadership as facing threats that eventually undermined the institution's status; do not attribute the institutional change to Urban's own conduct.",
    "st-chp2-sec-ii-l20-28-richelieu-exploited-alliance":
        "The source says Richelieu turned Urban VIII's forced reliance on France to advantage. Preserve the political situation as context and Haskell's evaluative characterization.",
    "st-chp2-sec-ii-l20-28-urban-alliance-with-france":
        "The source directly states that Urban tried to remain neutral but was compelled to rely heavily on France; retain the source's account and qualification.",
    "st-chp2-sec-ii-l20-28-urban-fortification-impact":
        "Haskell links Urban VIII's attention to fortifications in and around Rome with contemporary effect and artistic recording. Preserve this as an authorial historical interpretation; the note-linked works remain the supporting examples.",
}
SOURCE_CHECKS = {
    22: ("Urban VIII was faced with a situation", "undermine the whole status of the papacy"),
    24: ("attention paid by Urban",),
    25: ("VIII to fortifications both in and out of Rome", "turned to advantage by the unscrupulous Richelieu"),
    27: ("severity of the Counter Reformation", "affecting the papacy itself"),
    28: ("stimulus to ecclesiastical architecture and decoration", "at least partly aimed at stifling doubts"),
}
EXPECTED_ENDPOINTS = {
    "st-chp2-sec-ii-l20-28-architecture-decoration-and-persuasion": ("cand-3104", "cand-4227"),
    "st-chp2-sec-ii-l20-28-counter-reformation-and-spiritual-crisis": ("cand-3396", "cand-4226"),
    "st-chp2-sec-ii-l20-28-intellectual-changes-affect-papacy": ("cand-4226", "cand-4223"),
    "st-chp2-sec-ii-l20-28-naude-french-quotation": ("cand-1726", "cand-4224"),
    "st-chp2-sec-ii-l20-28-papacy-status-threats": ("cand-3104", "cand-4223"),
    "st-chp2-sec-ii-l20-28-richelieu-exploited-alliance": ("cand-2189", "cand-3104"),
    "st-chp2-sec-ii-l20-28-urban-alliance-with-france": ("cand-3104", "cand-4221"),
    "st-chp2-sec-ii-l20-28-urban-fortification-impact": ("cand-3104", "cand-3126"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed relation classifications")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    require(actual_sha == EXPECTED_SHA, f"statement table changed since review: {actual_sha}")
    require(not BACKUP.exists(), f"recovery backup already exists: {BACKUP.name}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for line_no, phrases in SOURCE_CHECKS.items():
        require(line_no <= len(source_lines), f"source line {line_no} is missing")
        for phrase in phrases:
            require(phrase in source_lines[line_no - 1], f"source line {line_no} changed: {phrase!r}")

    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    require(set(TRUE_NOTES) <= set(by_id), "one or more reviewed statement IDs are absent")
    with (ROOT / "04-knowledge/tables/entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in __import__("csv").DictReader(handle)}
    pending = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == SEGMENT
        and row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(pending == set(TRUE_NOTES), f"pending bilateral statement set changed: {sorted(pending ^ set(TRUE_NOTES))}")
    for statement_id, note in TRUE_NOTES.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        require(row.get("segment_id") == SEGMENT, f"{statement_id} is outside the reviewed segment")
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == EXPECTED_ENDPOINTS[statement_id],
                f"{statement_id} endpoints changed")
        require(row.get("subject_candidate_id") in candidate_ids and row.get("object_candidate_id") in candidate_ids,
                f"{statement_id} has a missing endpoint")
        require(qualifiers.get("relation_candidate") is None, f"{statement_id} is already classified")
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and 20 <= start <= end <= 28,
                f"{statement_id} has an invalid source anchor")
        anchor = "\n".join(source_lines[start - 1:end])
        require(row.get("original_quote") in anchor, f"{statement_id} quote no longer matches source")
        qualifiers = dict(qualifiers)
        qualifiers["relation_candidate"] = True
        qualifiers["relation_candidate_note"] = note
        row["qualifiers"] = qualifiers

    naude = by_id["st-chp2-sec-ii-l20-28-naude-french-quotation"]
    naude_q = dict(naude["qualifiers"])
    naude_q["other_candidate_ids"] = ["cand-3126", "cand-3114"]
    naude_q["mentioned_candidate_ids"] = ["cand-1726", "cand-3126", "cand-4224", "cand-3114"]
    naude["qualifiers"] = naude_q
    intellectual = by_id["st-chp2-sec-ii-l20-28-intellectual-changes-affect-papacy"]
    intellectual_q = dict(intellectual["qualifiers"])
    intellectual_q["mentioned_candidate_ids"] = ["cand-0003", "cand-1105", "cand-3578", "cand-4226", "cand-4223"]
    intellectual["qualifiers"] = intellectual_q

    true_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                         and (row.get("qualifiers") or {}).get("relation_candidate") is True)
    false_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                          and (row.get("qualifiers") or {}).get("relation_candidate") is False)
    pending_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                            and (row.get("qualifiers") or {}).get("relation_candidate") is None)
    require((true_bilateral, false_bilateral, pending_bilateral) == (3996, 451, 4050),
            f"unexpected projected counts: {(true_bilateral, false_bilateral, pending_bilateral)}")
    output = []
    for index, row in enumerate(rows):
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            line = b"\xef\xbb\xbf" + line
        output.append(line + newline)
    payload = b"".join(output)
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_true": list(TRUE_NOTES),
        "classified_false": [],
        "after": {
            "relation_true_bilateral": true_bilateral,
            "relation_false_bilateral": false_bilateral,
            "unclassified_bilateral": pending_bilateral,
        },
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry run only. Pass --apply to write.")
        return

    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".s2tmp-", delete=False) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        os.replace(temp_path, TABLE)
        written = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        written_by_id = {row["statement_id"]: row for row in written}
        require(all((written_by_id[key].get("qualifiers") or {}).get("relation_candidate") is True for key in TRUE_NOTES),
                "one or more classifications were not persisted")
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(json.dumps({
        "result": "applied",
        "statement_count": len(written),
        "sha256": hashlib.sha256(TABLE.read_bytes()).hexdigest(),
        "backup": BACKUP.name,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
