from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch16-p374-residual-20261015")
EXPECTED_SHA256 = "918deecfb881417a44e04b959423b7d5d2d13315276d6ebfca64c2c13bb07409"
SEGMENT = "chp-16:16_CHP-16_intro:l16-22"


DECISIONS = {
    "st-chp16-p374-dealer-trade-secrecy-transport-customs": (
        False,
        "This summarizes general transaction logistics and conditional customs evasion; no identified collection, shipment, agent, or transaction is connected.",
        None,
    ),
    "st-chp16-p374-strange-modern-art-commissions": (
        True,
        "Haskell directly reports Strange commissioning a modern work for himself or a client; preserve the commission claim with its alternatives and unnamed work/client.",
        "The modern work and possible client are not identified; the source does not say which alternative applied to any specific commission.",
    ),
    "st-chp16-p374-strange-view-of-guardi-truth": (
        False,
        "This records Haskell's evaluation of Guardi's painted views; the antecedent of 'this' is not resolved into a separate historical relation.",
        None,
    ),
    "st-chp16-p374-armanni-quote-on-poore": (
        False,
        "This is Armanni's attributed rhetorical question about Mr Poore's taste, not evidence of a direct historical relation between the speaker and visitor.",
        None,
    ),
    "st-chp16-p374-venetian-dealers-retain-painting-heritage": (
        True,
        "Haskell directly links the source-defined agents, dealers, minor clerics, and doctors in Venice with continued acceptance of recent Venetian painting; preserve this group-level cultural relation.",
        "The social group is described by roles rather than named or enumerated members; the art tradition is the existing source-level candidate cand-11543.",
    ),
    "st-chp16-p374-canova-tiepolo-modello-rumour": (
        False,
        "Haskell explicitly says the reported purchase was not true; preserve the rumor and correction as claims without asserting a Sasso-to-modello relation.",
        None,
    ),
    "st-chp16-p374-sasso-posthumous-collection-partial": (
        True,
        "The statement links Sasso's source-level collection cand-10598 to contents listed in the auction account; retain the partial inventory scope and continuation onto p.375.",
        "The list names categories and makers but does not identify every work or establish a complete inventory.",
    ),
    "st-chp16-p374-refine-picture-storage": (
        True,
        "Haskell reports temporary storage of the pictures at Strange's Treviso country house or London apartments; preserve the stated alternatives and temporary status.",
        "The picture group is the unenumerated set purchased through Sasso, and the two residences are alternatives; no individual work or single storage location is specified.",
    ),
    "st-chp16-p374-refine-picture-sale-qualification": (
        True,
        "The source reports sales to rich amateurs while explicitly qualifying that some sales might not have occurred because buyers preferred modern pictures.",
        "No individual picture, amateur, or completed transaction is identified; retain the conditional alternative in the claim.",
    ),
    "st-chp16-p374-refine-transport-cost": (
        False,
        "This is a general cost assessment for transport, with no shipment or responsible party identified.",
        None,
    ),
    "st-chp16-p374-refine-customs-evasion": (
        False,
        "This describes general customs difficulty and conditional evasion, not a named shipment or established act by a specific person.",
        None,
    ),
    "st-chp16-p374-refine-haskell-guardi-truth-judgement": (
        False,
        "This is Haskell's aesthetic judgment of Guardi's views, not an inter-entity relation; retain it as an attributed claim.",
        None,
    ),
    "st-chp16-p374-refine-strange-admires-guardi": (
        True,
        "The source explicitly states Strange's admiration for Francesco Guardi; both person endpoints are identified.",
        None,
    ),
    "st-chp16-p374-refine-strange-venetian-colour-preference": (
        True,
        "The source explicitly attributes Strange's preference for the brio and rich colour of Venetian painting; preserve the preference as Haskell's report.",
        None,
    ),
    "st-chp16-p374-refine-strange-dislikes-neoclassical-works": (
        True,
        "The source explicitly says Strange was out of sympathy with the then-fashionable dry neo-classical works; preserve the place and period qualifiers.",
        None,
    ),
    "st-chp16-p374-refine-not-all-clients": (
        False,
        "This is a broad comparison of unnamed clients' enthusiasm, not a relation to identified clients or a particular transaction.",
        None,
    ),
    "st-chp16-p374-refine-armanni-occupation": (
        False,
        "Painter and dealer are biographical roles assigned to Armanni, not a relation candidate in this statement.",
        None,
    ),
    "st-chp16-p374-refine-armanni-travel": (
        True,
        "Haskell directly reports Armanni's travel between Bologna and Rome; preserve both named places without inferring residence or itinerary dates.",
        "The statement describes travel between two places in one clause; it does not identify a single journey, route, date, or current residence.",
    ),
    "st-chp16-p374-refine-armanni-new-fashions": (
        False,
        "This is a general characterization of Armanni's awareness of unspecified fashions, not a relation to an identified concept or work.",
        None,
    ),
    "st-chp16-p374-refine-sasso-earlier-painter-virtuosity": (
        True,
        "Haskell tentatively links Sasso's taste to an earlier generation's admiration for the virtuosity of eighteenth-century painters; retain the inference and attribution.",
        "The admired painters and particular works are not enumerated, and Haskell marks this as an inference with 'seems'.",
    ),
    "st-chp16-p374-refine-haskell-rejects-modello-rumour": (
        False,
        "This is Haskell's correction of a reported purchase rumor, not a separate relation between Sasso and all Tiepolo modelli.",
        None,
    ),
    "st-chp16-p374-refine-haskell-interprets-modello-rumour": (
        True,
        "Haskell says the false rumor probably reflects Sasso's known preference for this kind of painting; preserve the explicitly tentative interpretation.",
        None,
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate() -> tuple[list[str], str]:
    current_hash = sha256(TABLE)
    if current_hash != EXPECTED_SHA256:
        raise SystemExit(f"table hash mismatch: expected {EXPECTED_SHA256}, got {current_hash}")
    lines = TABLE.read_text(encoding="utf-8").splitlines(keepends=True)
    selected = {}
    for line in lines:
        row = json.loads(line)
        if row["statement_id"] in DECISIONS:
            selected[row["statement_id"]] = row
    if set(selected) != set(DECISIONS):
        raise SystemExit(f"statement set mismatch: missing={sorted(set(DECISIONS)-set(selected))}")
    for statement_id, row in selected.items():
        if row["segment_id"] != SEGMENT:
            raise SystemExit(f"wrong segment for {statement_id}: {row['segment_id']}")
        if row["qualifiers"].get("relation_candidate") is not None:
            raise SystemExit(f"statement is no longer unset: {statement_id}")
    return lines, current_hash


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    lines, before_hash = validate()
    counts = Counter(value for value, _, _ in DECISIONS.values())
    print(f"segment={SEGMENT} pending={len(DECISIONS)} classify_true={counts[True]} classify_false={counts[False]}")
    for statement_id, (value, note, open_reason) in DECISIONS.items():
        print(f"{statement_id}: {str(value).lower()} | {note}")
        if open_reason:
            print(f"  open_endpoint_reason: {open_reason}")
    print(f"before_sha256={before_hash}")
    if args.preview:
        print("preview only; no table or backup written")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    changed_lines: list[str] = []
    seen: set[str] = set()
    for line in lines:
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id not in DECISIONS:
            changed_lines.append(line)
            continue
        value, note, open_reason = DECISIONS[statement_id]
        qualifiers = row["qualifiers"]
        qualifiers["relation_candidate"] = value
        qualifiers["relation_candidate_note"] = note
        if open_reason:
            qualifiers["open_endpoint_reason"] = open_reason
        elif qualifiers.get("open_endpoint_reason"):
            qualifiers.pop("open_endpoint_reason")
        changed_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        seen.add(statement_id)
    if seen != set(DECISIONS):
        raise SystemExit(f"write set mismatch: {sorted(set(DECISIONS)-seen)}")
    if sha256(TABLE) != before_hash:
        raise SystemExit("table changed after validation")

    shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        stream.writelines(changed_lines)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp_path, TABLE)
    print(f"backup={BACKUP}")
    print(f"after_sha256={sha256(TABLE)}")
    print("applied 22 classifications; unrelated statement lines preserved byte-for-byte")


if __name__ == "__main__":
    main()
