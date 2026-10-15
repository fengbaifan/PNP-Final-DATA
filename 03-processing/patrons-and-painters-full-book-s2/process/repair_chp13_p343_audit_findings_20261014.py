from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge/tables/book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md"
EXPECTED = {
    STATEMENTS: "4ce8c53899cdc50a33ce3341559b124afdca09329b818d4fcff928a6861f770a",
    MENTIONS: "65596a446ce8f6700b4bc34cf585603e4eb081adb1085994430e617695094050",
}
BACKUP_SUFFIX = ".bak-s2-ch13-p343-audit-repair-20261014"

RAW_QUOTES = {
    "st-chp13-p343-zanetti_bought_rembrandt_callot_prints_abroad": "Rembrandtand Callot whomhe bought on his foreign travels;",
    "st-chp13-p343-zanetti_never_seen_giulio_romano_prints": "prints of Giulio Romano engraved by Marc’Antonio with Aretino’s.sonnets. I have never seen these in all my life—either in Italy, or in Holland, France or England.",
    "st-chp13-p343-zanetti_revived_technique_and_made_about_fifty_cuts": "He - revived this technique, which had been familiar to sixteenth-century artists, during his \" stay in London, and he produced about fifty cuts in all, mostly copied or adapted from his Parmigianino drawings.",
    "st-chp13-p343-zanetti_never_seen_annibale_bacchanal_dish": "prints of Giulio Romano engraved by Marc’Antonio with Aretino’s.sonnets. I have never seen these in all my life—either in Italy, or in Holland, France or England.",
    "st-chp13-p343-zanetti_had_passion_for_antiquity": "Zanetti, had a passion for antiquity",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    for path, expected in EXPECTED.items():
        if digest(path) != expected:
            raise SystemExit(f"precheck failed: {path.name} changed")

    statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines()]
    by_id = {row["statement_id"]: row for row in statements}
    if set(RAW_QUOTES) - by_id.keys():
        raise SystemExit("precheck failed: expected statement missing")
    for statement_id, quote in RAW_QUOTES.items():
        by_id[statement_id]["original_quote"] = quote
    # The OCR defect precedes the enthusiasm clause and is recorded with the unary passion statement only.
    by_id["st-chp13-p343-zanetti_passion_for_antiquity_and_tiepolo_etchings"]["qualifiers"]["ocr_corrections"] = []

    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        mentions = list(reader)
    matches = [row for row in mentions if row.get("mention_id") == "m-s2-ch13-p343-060"]
    if len(matches) != 1 or matches[0].get("candidate_id") != "cand-10090" or matches[0].get("surface_form") != "these":
        raise SystemExit("precheck failed: expected duplicate anaphoric mention missing or altered")
    mentions = [row for row in mentions if row.get("mention_id") != "m-s2-ch13-p343-060"]

    print("repairing 5 source quotes to preserve exact S0 OCR and removing duplicate overlapping 'these' mention")
    if not args.apply:
        print("dry-run: no files changed")
        return

    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in (STATEMENTS, MENTIONS)]
    if any(path.exists() for path in backups):
        raise SystemExit("refusing to overwrite an existing recovery copy")
    for original, backup in zip((STATEMENTS, MENTIONS), backups):
        shutil.copy2(original, backup)

    statements_data = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in statements) + "\n").encode("utf-8")
    atomic_write(STATEMENTS, statements_data)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(mentions)
    atomic_write(MENTIONS, ("\ufeff" + stream.getvalue()).encode("utf-8"))

    print(f"statements_sha256={digest(STATEMENTS)}")
    print(f"mentions_sha256={digest(MENTIONS)}")
    print("APPLIED; backups saved")


if __name__ == "__main__":
    main()
