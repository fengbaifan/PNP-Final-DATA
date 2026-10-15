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
SEGMENT = "chp-7:07_CHP-7_sec_i:l61-74"
STATEMENT_BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp7-seci-p175-l61-74-relation-classification-20261013"
MENTION_BACKUP = TABLES / "mentions.csv.bak-s2-chp7-seci-p175-l61-74-relation-classification-20261013"
EXPECTED = {
    STATEMENTS: "252e54de64162b6a5c828bbf2a15ea03ed4e837d6c14d73d32d0110f10422d1f",
    MENTIONS: "1a4854217cd821631b52f976a88f81c2bcb983f7f886dfb16bcbc6bbf211266d",
    CANDIDATES: "ef7893ab6f854a074a592eac8d904774cc8ec31bf0115366f23cb0e35c5e3baa",
    SOURCE: "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3",
}

TRUE_NOTES = {
    "st-chp7-p175-i01": "This records Gentileschi's short Paris stay and Haskell's explicitly inferential explanation that Rubens's welcome discouraged him.",
    "st-chp7-p175-i05": "This records the one commission from Marie de Medici that Haskell regards as certain, tied to the indexed Public Felicity painting; 'only one certain' limits the evidence rather than excluding other commissions.",
    "st-chp7-p175-i07": "This preserves Haskell's interpretation that the painting reflects Marie's interests; it remains an attributed reading of the work.",
    "st-chp7-p175-i08": "This records Haskell's account of Rubens using his artistic gifts to promote Marie's personal prestige, without inferring a separate commission in this clause.",
    "st-chp7-p175-i09": "This records Haskell's account of Gentileschi using his artistic gifts to promote Marie's prestige; it does not add an unnamed commission.",
    "st-chp7-p175-i10": "This records Haskell's comparison between Ferdinando's concerns and Marie's concern with personal prestige; it does not infer a specific shared political motive.",
    "st-chp7-p175-i11": "This records Ferdinando's wish for the French court to address him as Altesse; the source does not say the court complied.",
    "st-chp7-p175-i12": "This records Ferdinando writing to his unnamed ambassador in Paris for advice; the cited locators are not treated as independent verification.",
    "st-chp7-p175-i13": "This records the advice that pictures for Marie's new palace would be a suitable gift; the adviser is unnamed and the later proposal is not treated as accepted or delivered.",
    "st-chp7-p175-i14": "This records the source-stated father relationship between Ferdinando and Duke Vincenzo; the duke's regnal identity remains unresolved.",
    "st-chp7-p175-i16": "This records Ferdinando employing a broad unnamed group of leading Italian artists and specifically highlights Domenico Fetti; Haskell's praise of Fetti remains evaluative.",
    "st-chp7-p175-i17": "This records Ferdinando's proposal to send the ten Baglione pictures; the proposal does not establish that they were sent, received, or accepted.",
    "st-chp7-p175-i18": "This records Marie's request about the Muses' depiction in the proposed pictures and preserves Haskell's statement that her other reactions are unknown.",
    "st-chp7-p175-i19": "This preserves Haskell's claim that the proposed Baglione pictures indirectly turned Richelieu's attention toward Mantua; it does not claim he acquired those pictures.",
    "st-chp7-p175-i20": "This records Haskell's account that Richelieu and other unnamed people would obtain treasures from Mantua; the recipients and works remain unspecified and the comparison is the author's evaluation.",
    "st-chp7-p175-i22": "This records an unidentified cited source's characterization of Richelieu as a minister of France and art lover; it is a quoted evaluation, not Haskell's independent assessment.",
    "st-chp7-p175-i24": "This records Haskell's account of Richelieu using agents in Italy to acquire masterpieces, with the Isabella d'Este studiolo pictures as examples; it does not identify individual works or prove acquisition of a particular surviving picture.",
    "st-chp7-p175-i26": "This records Haskell's claim that Richelieu's dealings with living artists were mostly confined to French and Flemish artists, retaining the duration qualifier and named examples.",
    "st-chp7-p175-i27": "This records Richelieu's first turn toward Italy through commissioning works from Nicolas Poussin, whom Haskell identifies as French.",
    "st-chp7-p175-i28": "This records Richelieu ordering three Bacchanals from Nicolas Poussin; the artist is the commission endpoint and the work group remains separately mentioned without identifying individual paintings.",
    "st-chp7-p175-i29": "This records Haskell's account of Richelieu's policy of trying to bring leading Italian artists to Paris; it does not claim the artists actually came.",
    "st-chp7-p175-i30": "This preserves Haskell's inferential account of Richelieu's envy of the Barberini and his assessment of Parisian talent; the mental states and evaluations remain attributed.",
    "st-chp7-p175-i31": "This records Mazzarini as Richelieu's Italian protégé and Haskell's claim about his emerging role in French politics; the source has not yet described him as a cardinal here.",
    "st-chp7-p175-i32": "This records Richelieu's pressure to have Mazzarini made a cardinal and his persuasion for Mazzarini to settle in France, preserving the p.176 continuation and the source's time span.",
}

FALSE_NOTES = {
    "st-chp7-p175-i06": "This describes the painting's depicted content and visual composition; it does not assert a relation between independently represented entity candidates.",
    "st-chp7-p175-i15": "This is Haskell's broad characterization of Ferdinando as a collector and patron; the specific employment of artists is stated separately.",
    "st-chp7-p175-i21": "This is editorial framing about Richelieu's part in the chapter's story, not a historical relation claim.",
    "st-chp7-p175-i23": "This is editorial framing about Richelieu's role in the chapter narrative, not a historical relation claim.",
    "st-chp7-p175-i25": "This is a broad chronological characterization that four artists were long dead by the period under discussion, without a discrete relation endpoint.",
}

ENDPOINT_FIXES = {
    "st-chp7-p175-i28": {"subject": ("cand-2189", "cand-2189"), "object": ("cand-1998", "cand-1984")},
    "st-chp7-p175-i32": {"subject": ("cand-2190", "cand-2189"), "object": ("cand-1588", "cand-1588")},
}
MENTION_OLD = (
    b"m-chp7-p175-b-083,chp-7:07_CHP-7_sec_i:l61-74,cand-2190,Richelieu,3232,3241,"
    b"Topical candidate for the policy of attracting Italian artists to Paris.\r\n"
)
MENTION_NEW = MENTION_OLD.replace(b",cand-2190,Richelieu,", b",cand-2189,Richelieu,")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify p.175 body S2 relation candidates")
    parser.add_argument("--apply", action="store_true", help="write guarded classification changes")
    args = parser.parse_args()

    raw = {path: path.read_bytes() for path in EXPECTED}
    for path, expected in EXPECTED.items():
        actual = digest(raw[path])
        if actual != expected:
            raise SystemExit(f"input SHA mismatch for {path.relative_to(ROOT)}: {actual}")

    source_lines = raw[SOURCE].decode("utf-8-sig").splitlines()
    required_source = (
        (60, "[Page 175]"),
        (62, "influence of which has been traced"),
        (62, "Only one certain commission from Marie de Medici survives"),
        (68, "he ordered three Bacchanals"),
        (73, "Throughout 1639 Richelieu was using all his pressure"),
    )
    if any(text not in source_lines[index] for index, text in required_source):
        raise SystemExit("p.175 source-line guards failed")

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
    if unset != expected_targets or len(unset) != 29:
        raise SystemExit(f"p.175 target set changed: {sorted(unset ^ expected_targets)}")

    candidate_rows = list(csv.DictReader(io.StringIO(raw[CANDIDATES].decode("utf-8-sig"), newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    for sid in sorted(unset):
        row = by_id[sid]
        q = row.get("qualifiers") or {}
        start, end = q.get("source_line_start"), q.get("source_line_end")
        if not isinstance(start, int) or not isinstance(end, int) or start < 61 or end > 74 or start > end:
            raise SystemExit(f"invalid p.175 source anchor: {sid} {start}-{end}")
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
    target_mentions = [row for row in mention_rows if row.get("mention_id") == "m-chp7-p175-b-083"]
    if len(target_mentions) != 1 or target_mentions[0].get("candidate_id") != "cand-2190" or target_mentions[0].get("surface_form") != "Richelieu":
        raise SystemExit("unexpected target mention state for m-chp7-p175-b-083")
    if raw[MENTIONS].count(MENTION_OLD) != 1:
        raise SystemExit("exact mention-row byte guard failed")
    mention_result = raw[MENTIONS].replace(MENTION_OLD, MENTION_NEW, 1)

    for sid, changes in ENDPOINT_FIXES.items():
        row = by_id[sid]
        for field, (_, new) in changes.items():
            row[f"{field}_candidate_id"] = new
        q = row.setdefault("qualifiers", {})
        mentioned = q.get("mentioned_candidate_ids", [])
        if sid == "st-chp7-p175-i32":
            if mentioned.count("cand-2190") != 1:
                raise SystemExit("unexpected statement mention list for Richelieu's p.175 L74 claim")
            q["mentioned_candidate_ids"] = ["cand-2189" if cid == "cand-2190" else cid for cid in mentioned]
    for mapping in (TRUE_NOTES, FALSE_NOTES):
        for sid, note in mapping.items():
            q = by_id[sid].setdefault("qualifiers", {})
            q["relation_candidate"] = sid in TRUE_NOTES
            q["relation_candidate_note"] = note

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
        "mention_correction": "m-chp7-p175-b-083 candidate_id cand-2190 -> cand-2189",
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
