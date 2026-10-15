from __future__ import annotations

import argparse
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
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
SEGMENT = "chp-7:07_CHP-7_sec_i:l76-89"
STATEMENT_BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p176-l76-89-relation-classification-20261013"
MENTION_BACKUP = TABLES / "mentions.csv.bak-s2-chp7-seci-p176-l76-89-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "5e9b8b203a25aefb4aed250e333d7a243f3c5bc92f85637820dea6b47395f6fe",
    MENTIONS: "89964c642f56e7c062af14f6d869990ee4f9c17ad8adb77bf8b99b0a7d747af9",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p176-i01": "This records Haskell's claim that Richelieu's pressure led to Mazzarini's elevation to cardinal; the appointing authority is not identified in this passage.",
    "st-chp7-p176-i02": "This records Richelieu persuading Mazzarini to settle in France at the end of 1639; it does not imply a formal appointment.",
    "st-chp7-p176-i03": "This records Mazarin's appointment as French representative at the Congress of Cologne; the appointing authority remains unnamed.",
    "st-chp7-p176-i04": "This records Mazarin acting for the French court after Cologne; the source supplies no narrower office title.",
    "st-chp7-p176-i05": "This preserves Haskell's qualified inference that Mazarin's nationality, artistic interest and later role support crediting him with initiating Richelieu's recruitment policy; it is not direct evidence of origin.",
    "st-chp7-p176-i06": "This records Poussin writing to Jean Lemaire in early 1639 about concern over French recruitment developments; Haskell reports the letter rather than quoting it directly.",
    "st-chp7-p176-i07": "This preserves Poussin's reported assessment that the best Italian painters were well treated in Rome and unlikely to accept French offers; it is not generalized to every painter.",
    "st-chp7-p176-i08": "This preserves Poussin's attributed judgment about which painters might accept the offers and his quoted criticism of French overestimation; it is not the project's own evaluation.",
    "st-chp7-p176-i09": "This records Haskell's retrospective claim that events bore out Poussin's forecast; the specific outcomes are described in the following sentences and are not quantified here.",
    "st-chp7-p176-i10": "This records pressure being applied to Poussin and Duquesnoy to come to France; the recruiting actor is not identified.",
    "st-chp7-p176-i11": "This records both named artists resisting the pressure to come to France; the source gives no individual reason for either response.",
    "st-chp7-p176-i12": "This records Poussin setting demanding conditions and those conditions being accepted; the accepting person or authority is not named.",
    "st-chp7-p176-i13": "This records the unnamed Surintendant des Bâtiments sending Chantelou to Rome in May 1640; the officeholder's identity is not inferred.",
    "st-chp7-p176-i14": "This records Chantelou's mission to bring Poussin back and recruit a broader unnamed group of artists and artisans; no full membership list is supplied.",
    "st-chp7-p176-i15": "This records appeals made collectively by Mazarin and unnamed friends to the artists; the sentence expresses a hope for response, not universal acceptance.",
    "st-chp7-p176-i16": "This records Pietro da Cortona as one artist Mazarin's circle wished to attract; it does not claim he accepted.",
    "st-chp7-p176-i16b": "This records Guercino as another artist the circle wished to attract; it does not claim he accepted.",
    "st-chp7-p176-i18": "This records a series of refusals by those approached; Haskell does not assign individual refusals to Cortona or Guercino.",
    "st-chp7-p176-i19": "This records Chantelou escorting Poussin and a few unnamed secondary painters by October; the other painters remain unidentified.",
    "st-chp7-p176-i20": "This preserves Haskell's account that the limited recruitment success depended on pressure ranging from threats to bribery; actors and recipients are not identified.",
    "st-chp7-p176-i21": "This records Stefano della Bella coming to Paris in the service of an unnamed Florentine ambassador; no year or ambassador identity is supplied.",
    "st-chp7-p176-i22": "This records della Bella settling and working in Paris for ten years according to Haskell; exact start and end dates are not given.",
    "st-chp7-p176-i23": "This records the Barberini allowing Bernini to make Richelieu's bust, with unnamed pupils also participating; the person endpoint is Bernini and the bust remains a separate work mention.",
    "st-chp7-p176-i24": "This preserves Haskell's rhetorical characterization of Richelieu as the Barberini's formidable and dangerous so-called ally; it does not establish a formal alliance.",
    "st-chp7-p176-i25": "This preserves Haskell's inference that Bernini's Richelieu bust was almost certainly derived from an unidentified triple portrait by Philippe de Champaigne.",
    "st-chp7-p176-i26": "This records the Richelieu bust arriving in Paris in August 1641; the cold, aloof and elegant description is Haskell's evaluation.",
    "st-chp7-p176-i27": "This records Haskell's account that Richelieu's death did not interrupt French artist-recruitment plans; it does not claim every plan was carried out.",
    "st-chp7-p176-i28": "This records the unnamed Surintendant informing a group of artists that French plans continued after Richelieu's death; the quoted collective label does not establish a formal organization.",
    "st-chp7-p176-i29": "This records Poussin's return to Rome after two years in Paris and preserves Haskell's characterization of his stated reason as a pretext; the wife's identity and actual motive remain unverified.",
    "st-chp7-p176-i30": "This records Duquesnoy agreeing to go to Paris and dying before he could sail from Livorno; it does not claim he reached Paris.",
    "st-chp7-p176-i31": "This records Mazarin replacing Richelieu and Haskell's causal interpretation that Duquesnoy's death spurred more ambitious recruitment; the death is the stated stimulus.",
    "st-chp7-p176-i32": "This records Mazarin's 1644 effort to persuade Bernini to settle in France by offering a large but unspecified salary; acceptance is not stated.",
    "st-chp7-p176-i33": "This records Haskell's warning that Mazarin was reckoning without Urban VIII; the p.177 continuation specifies the Pope's continuing authority over Bernini.",
}

FALSE_NOTES = {
    "st-chp7-p176-i17": "This sentence is Haskell's evaluative judgment that the recruitment aims were too ambitious; it does not state a distinct relation fact beyond that assessment.",
}

OPEN_ENDPOINTS = {
    "st-chp7-p176-i01": "The source identifies Mazarin as the person made cardinal and Richelieu's pressure, but names no appointing authority.",
    "st-chp7-p176-i09": "The sentence refers collectively to events that proved the forecast but does not identify one event as the validating endpoint.",
    "st-chp7-p176-i10": "The source names Poussin and Duquesnoy as targets but does not identify who applied the pressure.",
    "st-chp7-p176-i11": "The source has two artist subjects and no named single destination decision-maker; retain both artists in mentions rather than selecting one scalar endpoint.",
    "st-chp7-p176-i12": "The source says the conditions were accepted but does not identify the accepting person or authority.",
    "st-chp7-p176-i15": "The appeal was made by Mazarin together with unnamed friends; the scalar Mazarin endpoint does not represent the full recruiting group.",
    "st-chp7-p176-i16": "The attraction effort is attributed to Mazarin's circle, including unnamed friends; Mazarin is not treated as the sole actor.",
    "st-chp7-p176-i16b": "The attraction effort is attributed to Mazarin's circle, including unnamed friends; Mazarin is not treated as the sole actor.",
    "st-chp7-p176-i18": "The source names no complete set of people who refused and does not assign individual refusals to the named artists.",
    "st-chp7-p176-i20": "The source does not identify the actors who used the pressure tactics or the people subjected to each tactic.",
    "st-chp7-p176-i23": "The source includes Bernini and unnamed pupils as makers; the pupil group remains an additional open endpoint beyond the named artist.",
    "st-chp7-p176-i31": "The statement's causal stimulus is Duquesnoy's death, while the scalar endpoints represent Mazarin and Richelieu; retain the causal event in the claim and mentions.",
}

ENDPOINT_FIXES = {
    "st-chp7-p176-i23": {"subject": ("cand-0198", "cand-0198"), "object": ("cand-0306", "cand-0295")},
    "st-chp7-p176-i25": {"subject": ("cand-6715", "cand-6715"), "object": ("cand-0306", "cand-2191")},
    "st-chp7-p176-i26": {"subject": ("cand-0306", "cand-2191"), "object": ("cand-4653", "cand-4653")},
}

MENTION_REWRITES = {
    b"m-chp7-p176-b-060,chp-7:07_CHP-7_sec_i:l76-89,cand-0306,": b"m-chp7-p176-b-060,chp-7:07_CHP-7_sec_i:l76-89,cand-2191,",
    b"m-chp7-p176-b-065,chp-7:07_CHP-7_sec_i:l76-89,cand-0306,": b"m-chp7-p176-b-065,chp-7:07_CHP-7_sec_i:l76-89,cand-2191,",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.176 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (75, "[Page 176]"),
        (76, "a cardinal and at the very end of that year"),
        (80, "Early in 1639 Poussin wrote to his friend Jean Lemaire"),
        (82, "Some months earker pressure had been put on him"),
        (83, "Bâtiments sent his agent"),
        (88, "Early in 1644 he made a determined effort"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.176 source-line guards failed")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"]
        for row in rows
        if row.get("segment_id") == SEGMENT and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    expected_targets = set(TRUE_NOTES) | set(FALSE_NOTES)
    if unset != expected_targets or len(unset) != 34:
        raise SystemExit(f"p.176 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 76 or end > 89 or start > end:
            raise SystemExit(f"invalid p.176 source anchor: {sid} {start}-{end}")
        refs = [row.get("subject_candidate_id"), row.get("object_candidate_id")] + q.get("mentioned_candidate_ids", [])
        missing_refs = sorted({cid for cid in refs if cid and cid not in candidate_ids})
        if missing_refs:
            raise SystemExit(f"candidate reference missing for {sid}: {missing_refs}")
    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (old, new) in changes.items():
            if row.get(f"{field}_candidate_id") != old:
                raise SystemExit(f"unexpected {field} endpoint for {sid}; review before applying")
            if new not in candidate_ids:
                raise SystemExit(f"replacement candidate missing for {sid}: {new}")

    mention_rows = list(csv.DictReader(io.StringIO(raw[MENTIONS].decode("utf-8-sig"), newline="")))
    expected_mentions = {
        "m-chp7-p176-b-060": ("cand-0306", "make a bust of the\nCardinal"),
        "m-chp7-p176-b-065": ("cand-0306", "it"),
    }
    for mid, (candidate_id, surface) in expected_mentions.items():
        matches = [row for row in mention_rows if row.get("mention_id") == mid]
        if len(matches) != 1 or matches[0].get("candidate_id") != candidate_id or matches[0].get("surface_form") != surface:
            raise SystemExit(f"unexpected mention state for {mid}")
    mention_result = raw[MENTIONS]
    for old, new in MENTION_REWRITES.items():
        if mention_result.count(old) != 1:
            raise SystemExit(f"mention byte guard failed: {old!r}")
        mention_result = mention_result.replace(old, new, 1)

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
        q = row.setdefault("qualifiers", {})
        refs = q.get("mentioned_candidate_ids", [])
        q["mentioned_candidate_ids"] = list(dict.fromkeys("cand-2191" if cid == "cand-0306" else cid for cid in refs))
    for mapping in (TRUE_NOTES, FALSE_NOTES):
        for sid, note in mapping.items():
            q = by_id[sid].setdefault("qualifiers", {})
            q["relation_candidate"] = sid in TRUE_NOTES
            q["relation_candidate_note"] = note
            if sid in OPEN_ENDPOINTS:
                q["open_endpoint_reason"] = OPEN_ENDPOINTS[sid]

    statement_result = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
    print(json.dumps({
        "mode": "apply" if args.apply else "dry_run",
        "segment": SEGMENT,
        "classified": len(unset),
        "relation_candidate_true": len(TRUE_NOTES),
        "relation_candidate_false": len(FALSE_NOTES),
        "unset_in_segment": 0,
        "statement_endpoint_corrections": [
            f"{sid} {field}_candidate_id {old!r} -> {new!r}"
            for sid, changes in ENDPOINT_FIXES.items()
            for field, (old, new) in changes.items()
            if old != new
        ],
        "mention_corrections": ["m-chp7-p176-b-060: cand-0306 -> cand-2191", "m-chp7-p176-b-065: cand-0306 -> cand-2191"],
        "statement_before_sha256": digest(raw[STATEMENTS]),
        "statement_after_sha256": digest(statement_result),
        "mentions_before_sha256": digest(raw[MENTIONS]),
        "mentions_after_sha256": digest(mention_result),
    }, ensure_ascii=True))
    if not args.apply:
        return
    if STATEMENT_BACKUP.exists() or MENTION_BACKUP.exists():
        raise SystemExit("a backup already exists; refusing to overwrite")
    shutil.copy2(STATEMENTS, STATEMENT_BACKUP)
    shutil.copy2(MENTIONS, MENTION_BACKUP)
    atomic_write(STATEMENTS, statement_result)
    atomic_write(MENTIONS, mention_result)
    print(f"statement_backup={STATEMENT_BACKUP.relative_to(ROOT)}")
    print(f"mention_backup={MENTION_BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
