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
SEGMENT = "chp-2:02_CHP-2_sec_ii:l62-69"
EXPECTED_SHA = "acb8aca92118219687d89b8653315aa725f39e36600ce4fbf75c1a8d361055d2"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l62-69-20261010")
TRUE_NOTES = {
    "st-chp2-secii-l62-69-berninicommission-scope-and-papal-motive":
        "Haskell says Bernini undertook almost no important work other than Barberini commissions in 1623–1644, then gives time pressure and papal project scale and adds a 'no doubt' inference about Urban's motives. Preserve the period, 'almost,' 'largely,' and the inference.",
    "st-chp2-secii-l62-69-berninicompleted-bibiana-work":
        "Haskell says Bernini completed the S. Bibiana reconstruction and decoration within a couple of years; no exact start or completion year is supplied.",
    "st-chp2-secii-l62-69-berninimade-bibiana-statue":
        "The source says Bernini made a statue of Saint Bibiana for placement behind the High Altar; retain intended placement without asserting it remained there.",
    "st-chp2-secii-l62-69-berniniposition-and-papal-exclusivity":
        "Haskell describes Bernini's position as impregnable while Urban VIII lived and says the Pope wanted him to work exclusively for him. Preserve these as narrative characterizations, not formal office or independently verified motives.",
    "st-chp2-secii-l62-69-bibiana-body-discovered":
        "Haskell reports that the saint's body was discovered during routine restoration at S. Bibiana and presents this as the accident behind the church's Baroque importance. The remains' identity and type remain unresolved.",
    "st-chp2-secii-l62-69-bibiana-statue-aesthetic-interpretation":
        "This preserves Haskell's aesthetic interpretation that the statue translated a sensual and mystical combination from Counter Reformation paintings into sculpture; the priority claim is not independently verified.",
    "st-chp2-secii-l62-69-diplomatic-portrait-permission":
        "Haskell reports that Charles I and Cardinal Richelieu had to seek Barberini permission for Bernini to make portraits, granted as an exceptional favour for useful privileges. Individual execution and diplomatic terms remain unverified.",
    "st-chp2-secii-l62-69-nicholas-stone-baker-bust-account":
        "This records Haskell's report of Nicholas Stone's account about Bernini carving Thomas Baker's bust and the Pope's intervention. Preserve the nested quotation and the unresolved identity of Cardinal Barberine.",
    "st-chp2-secii-l62-69-passeri-quote-continuation":
        "This continues Passeri's satirical quotation about Bernini from L60; retain the metaphor and cross-segment link without reading it literally.",
    "st-chp2-secii-l62-69-pope-restricted-berninipatrons":
        "Haskell says Urban VIII took steps to prevent Bernini working for others without papal authorization, framing the restriction in relation to the portrait occasions. Do not infer a complete list of rulings.",
    "st-chp2-secii-l62-69-scipione-two-busts-authorized":
        "Haskell reports two busts recording Scipione Borghese's features shortly before his death, made only with special papal authorization. The individual bust versions remain unresolved.",
    "st-chp2-secii-l62-69-urban-commissioned-bibiana-work":
        "Haskell says Urban VIII entrusted Bernini with reconstruction and decoration of S. Bibiana around the time of the baldacchino commission. 'First purely architectural work' is the author's characterization.",
    "st-chp2-secii-l62-69-urban-rebuilt-bibiana":
        "Haskell says Urban VIII took the opportunity of the reported body discovery to have S. Bibiana completely rebuilt; keep the church as place distinct from the reconstruction work candidate.",
}
EXPECTED_ENDPOINTS = {
    "st-chp2-secii-l62-69-berninicommission-scope-and-papal-motive": ("cand-0295", "cand-0198"),
    "st-chp2-secii-l62-69-berninicompleted-bibiana-work": ("cand-0295", "cand-4442"),
    "st-chp2-secii-l62-69-berninimade-bibiana-statue": ("cand-0295", "cand-4445"),
    "st-chp2-secii-l62-69-berniniposition-and-papal-exclusivity": ("cand-0209", "cand-0295"),
    "st-chp2-secii-l62-69-bibiana-body-discovered": ("cand-4441", "cand-4443"),
    "st-chp2-secii-l62-69-bibiana-statue-aesthetic-interpretation": ("cand-4445", "cand-3396"),
    "st-chp2-secii-l62-69-diplomatic-portrait-permission": ("cand-0209", "cand-4435"),
    "st-chp2-secii-l62-69-nicholas-stone-baker-bust-account": ("cand-2511", "cand-4436"),
    "st-chp2-secii-l62-69-passeri-quote-continuation": ("cand-1856", "cand-0295"),
    "st-chp2-secii-l62-69-pope-restricted-berninipatrons": ("cand-0209", "cand-0295"),
    "st-chp2-secii-l62-69-scipione-two-busts-authorized": ("cand-0209", "cand-4434"),
    "st-chp2-secii-l62-69-urban-commissioned-bibiana-work": ("cand-0209", "cand-4442"),
    "st-chp2-secii-l62-69-urban-rebuilt-bibiana": ("cand-0209", "cand-4441"),
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
    for line_no, phrase in {
        63: "as long as Urban VIII lived his position was impregnable",
        64: "Between 1623 and 1644 Bernini undertook almost no work",
        65: "two splendid busts (Plate 5)",
        66: "Bernini to make portraits of them",
        67: "his patrone the Pope",
        68: "Urban VIII had commissioned the baldacchino",
        69: "the reconstruction and decoration of the little church of S. Bibiana",
    }.items():
        require(line_no <= len(source_lines) and phrase in source_lines[line_no - 1],
                f"source line {line_no} changed: {phrase!r}")

    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [json.loads(line.decode("utf-8-sig")) for line in raw.splitlines() if line.strip()]
    require(len({row["statement_id"] for row in rows}) == len(rows), "duplicate statement_id")
    by_id = {row["statement_id"]: row for row in rows}
    pending = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == SEGMENT
        and row.get("subject_candidate_id") and row.get("object_candidate_id")
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    require(pending == set(TRUE_NOTES), f"pending bilateral statement set changed: {sorted(pending ^ set(TRUE_NOTES))}")
    for statement_id, note in TRUE_NOTES.items():
        row = by_id[statement_id]
        require((row.get("subject_candidate_id"), row.get("object_candidate_id")) == EXPECTED_ENDPOINTS[statement_id],
                f"{statement_id} endpoints changed")
        qualifiers = row.get("qualifiers") or {}
        require(qualifiers.get("relation_candidate") is None, f"{statement_id} is already classified")
        start, end = qualifiers.get("source_line_start"), qualifiers.get("source_line_end")
        require(isinstance(start, int) and isinstance(end, int) and 62 <= start <= end <= 69,
                f"{statement_id} has an invalid source anchor")
        anchor = "\n".join(source_lines[start - 1:end])
        require(row.get("original_quote") in anchor, f"{statement_id} quote no longer matches source")
        q = dict(qualifiers)
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        row["qualifiers"] = q

    true_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                         and (row.get("qualifiers") or {}).get("relation_candidate") is True)
    false_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                          and (row.get("qualifiers") or {}).get("relation_candidate") is False)
    pending_bilateral = sum(1 for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")
                            and (row.get("qualifiers") or {}).get("relation_candidate") is None)
    require((true_bilateral, false_bilateral, pending_bilateral) == (4070, 451, 3976),
            f"unexpected projected bilateral counts: {(true_bilateral, false_bilateral, pending_bilateral)}")

    output = []
    for index, row in enumerate(rows):
        encoded = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if index == 0 and bom:
            encoded = b"\xef\xbb\xbf" + encoded
        output.append(encoded + newline)
    payload = b"".join(output)
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "classified_true": list(TRUE_NOTES),
        "classified_false": [],
        "after_bilateral": {"relation_true": true_bilateral, "relation_false": false_bilateral,
                            "unclassified": pending_bilateral},
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
        "sha256_after": hashlib.sha256(TABLE.read_bytes()).hexdigest(),
        "backup": BACKUP.name,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
