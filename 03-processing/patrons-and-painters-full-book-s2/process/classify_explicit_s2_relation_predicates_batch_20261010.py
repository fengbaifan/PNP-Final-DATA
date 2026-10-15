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
SOURCES = ROOT / "02-sources/02-Markdown"
EXPECTED_SHA = "bd7535f1ab371aa63a19ac9b040a9c9cfdf16738273028a939be8b63abc3e3e7"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-explicit-relation-predicates-20261010")

# Each entry is a source-line phrase independently checked before writeback.
SPECS = {
    "st-chp3-seci-l16-24-gregory-canonisation-ignatius": (
        "decree the canonisation of the two great Jesuits, Ignatius",
        "Haskell explicitly attributes Ignatius's canonisation decree to the Pope identified in the preceding sentence as Gregory XV; the claim remains source-attributed.",
    ),
    "st-chp3-seci-l16-24-gregory-canonisation-philip-neri": (
        "the founder of the Oratorians Philip Neri",
        "Haskell explicitly includes Philip Neri in Gregory XV's canonisation decree; the separate endpoint is retained and the claim remains source-attributed.",
    ),
    "st-chp3-seci-l16-24-gregory-canonisation-xavier": (
        "Ignatius and Francis Xavier",
        "Haskell explicitly includes Francis Xavier in Gregory XV's canonisation decree; the separate endpoint is retained and the claim remains source-attributed.",
    ),
    "st-chp3-seciv-l35-46-considers-brandi": (
        "Giacinto Brandi",
        "The passage explicitly says Oliva considered Brandi among three possible painters. Consideration is not treated as a commission.",
    ),
    "st-chp3-seciv-l35-46-considers-ferri": (
        "Ciro Ferri",
        "The passage explicitly says Oliva considered Ferri among three possible painters. Consideration is not treated as a commission.",
    ),
    "st-chp3-seciv-l35-46-considers-maratta": (
        "Maratta, Ciro Ferri",
        "The passage explicitly says Oliva considered Maratta among three possible painters; the line break in the source is preserved and consideration is not treated as a commission.",
    ),
    "st-chp4-sec-ii-p118-king-france-purchase": (
        "the King of France, the Spanish Viceroy of Naples and an English gentleman, Dr Richard Mead",
        "Haskell names the King of France among purchasers from the Massimi estate. The exact items bought are unspecified; no object-level ownership is inferred.",
    ),
    "st-chp4-sec-ii-p118-mead-purchase": (
        "Dr Richard Mead",
        "Haskell names Dr Richard Mead among purchasers from the Massimi estate. The exact items bought are unspecified; no object-level ownership is inferred.",
    ),
    "st-chp4-sec-ii-p118-viceroy-naples-purchase": (
        "the Spanish Viceroy of Naples",
        "Haskell names the Spanish Viceroy of Naples among purchasers from the Massimi estate. The exact items bought are unspecified; no object-level ownership is inferred.",
    ),
    "st-chp5-p144-de-rossi-displayed-la-fortuna": (
        "La Fortuna",
        "Haskell says De' Rossi displayed La Fortuna in his private museum. Display is not upgraded to legal ownership or present-day custody.",
    ),
    "st-chp5-p144-de-rossi-displayed-prometheus": (
        "Prometheus",
        "Haskell says De' Rossi displayed Rosa's Prometheus in his private museum. Display is not upgraded to legal ownership or present-day custody.",
    ),
    "st-chp5-p144-de-rossi-displayed-regulus": (
        "Regulus killed by the Carthaginians",
        "Haskell says De' Rossi displayed Regulus killed by the Carthaginians. 'Masterpiece' remains Haskell's evaluation; display is not upgraded to legal ownership or present-day custody.",
    ),
    "st-chp6-p155-lorenzo-commissions-claude": (
        "and Claude",
        "The sentence includes Claude among landscape specialists from whom Lorenzo commissioned pictures. No individual work is identified.",
    ),
    "st-chp6-p155-lorenzo-commissions-dughet": (
        "above all, Gaspard Dughet",
        "The sentence explicitly names Dughet among landscape specialists commissioned by Lorenzo. The adjacent Maratta figure attribution remains separate; no individual work is identified.",
    ),
    "st-chp6-p155-lorenzo-commissions-rosa": (
        "commissioned innumerable pictures by specialists in the subject such as Salvator Rosa",
        "The sentence explicitly names Rosa among landscape specialists commissioned by Lorenzo. No individual work or version is inferred.",
    ),
    "st-chp7-p175-i02": (
        "Louis Le Nain, Laurent de la Hyre and Philippe de Champaigne",
        "Haskell reports that influence from Gentileschi's pictures has been traced on Le Nain's style. This remains an attributed art-historical claim, not a teacher-pupil relation.",
    ),
    "st-chp7-p175-i03": (
        "Laurent de la Hyre",
        "Haskell reports that influence from Gentileschi's pictures has been traced on de la Hyre's style. This remains an attributed art-historical claim, not a teacher-pupil relation.",
    ),
    "st-chp7-p175-i04": (
        "Philippe de Champaigne",
        "Haskell reports that influence from Gentileschi's pictures has been traced on de Champaigne's style. This remains an attributed art-historical claim, not a teacher-pupil relation.",
    ),
    "st-chp7-p177-n4-letter-addressed-to": (
        "Gabriele Balestrieri wrote to the Duke of Modena",
        "Haskell's footnote, citing Lumbroso, reports the 1645 letter's addressee. The letter was not independently consulted.",
    ),
    "st-chp7-p181-n4-letter-addressed-to": (
        "Letter from Romanelli to Francesco Barberini of 6 July 1646",
        "Haskell's note identifies Francesco Barberini as the addressee of Romanelli's reported letter. The cited publication and letter were not independently consulted.",
    ),
    "st-chp7-p183-n3-letter-1650-to-maccarani": (
        "letter of 3 June 1650 to Maccarani",
        "Haskell identifies a 3 June 1650 letter to Maccarani and quotes it through a cited publication. The quotation's precise referent remains contextual and unverified here.",
    ),
    "st-chp2-sec-ii-l30-40-bernini-baldacchino-start": (
        "Bernini began work on a gigantic baldacchino",
        "The text explicitly reports Bernini beginning the baldacchino in July 1624. The source's 'supposed tomb' qualification is retained.",
    ),
    "st-chp3-secii-l125-135-oratorio-start": (
        "Borromini began work on the Oratorio in 1637",
        "The text explicitly reports Borromini beginning work on the Oratorio in 1637; no additional commission or appointment is inferred.",
    ),
    "st-chp2-seci-l124-157-darpino-copy-andrians": (
        "the Cavaliere d’Arpino copied them",
        "Haskell's note reports d'Arpino copying The Andrians, with 'them' resolved to the preceding Titian pictures. The manuscript note is not independently examined.",
    ),
    "st-chp2-seci-l124-157-darpino-copy-worship": (
        "the Cavaliere d’Arpino copied them",
        "Haskell's note reports d'Arpino copying The Worship of Venus, with 'them' resolved to the preceding Titian pictures. The manuscript note is not independently examined.",
    ),
    "st-chp2-seci-l124-157-rubens-version-andrians": (
        "His versions of these pictures, now in Stockholm",
        "Haskell reports a later Rubens version of The Andrians in Stockholm; the proposed date and derivation remain qualified, and no collection identity beyond the source is inferred.",
    ),
    "st-chp2-seci-l124-157-rubens-version-worship": (
        "His versions of these pictures, now in Stockholm",
        "Haskell reports a later Rubens version of The Worship of Venus in Stockholm; the proposed date and derivation remain qualified, and no collection identity beyond the source is inferred.",
    ),
}

CONTEXT_CHECKS = {
    "st-chp3-seci-l16-24-gregory-canonisation-ignatius": {17: "Gregory XV and his"},
    "st-chp3-seci-l16-24-gregory-canonisation-philip-neri": {17: "Gregory XV and his"},
    "st-chp3-seci-l16-24-gregory-canonisation-xavier": {17: "Gregory XV and his"},
    "st-chp3-seciv-l35-46-considers-brandi": {36: "Oliva had been looking"},
    "st-chp3-seciv-l35-46-considers-ferri": {36: "Oliva had been looking"},
    "st-chp3-seciv-l35-46-considers-maratta": {36: "Oliva had been looking"},
    "st-chp5-p144-de-rossi-displayed-la-fortuna": {24: "De’ Rossi had assembled"},
    "st-chp5-p144-de-rossi-displayed-prometheus": {24: "De’ Rossi had assembled"},
    "st-chp5-p144-de-rossi-displayed-regulus": {24: "De’ Rossi had assembled"},
    "st-chp7-p175-i02": {59: "Gentileschi"},
    "st-chp7-p175-i03": {59: "Gentileschi"},
    "st-chp7-p175-i04": {59: "Gentileschi"},
    "st-chp2-seci-l124-157-darpino-copy-andrians": {50: "Titian’s Worship", 129: "copied them"},
    "st-chp2-seci-l124-157-darpino-copy-worship": {50: "Titian’s Worship", 129: "copied them"},
    "st-chp2-seci-l124-157-rubens-version-andrians": {50: "The Andrians"},
    "st-chp2-seci-l124-157-rubens-version-worship": {50: "Worship os Venus"},
}


def require(ok: bool, message: str) -> None:
    if not ok:
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
        "relation_true": 3692,
        "relation_true_with_two_endpoints": 3676,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4397,
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
        "relation_true": 3719,
        "relation_true_with_two_endpoints": 3703,
        "relation_true_open": 16,
        "relation_false": 1760,
        "double_endpoint_unclassified": 4370,
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
