from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE_CH8 = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
STATEMENTS_BACKUP = STATEMENTS.with_name(
    STATEMENTS.name + ".bak-s2-independent-review-batch1-20261019"
)
MENTIONS_BACKUP = MENTIONS.with_name(
    MENTIONS.name + ".bak-s2-independent-review-batch1-20261019"
)


FIXES = {
    "st-chp1-secii-l28-38-04": {
        "expected": {
            "object_candidate_id": "cand-1677",
            "claim": "Prince Camillo Pamfili commissioned Pier Francesco Mola to paint the Four Elements at Valmontone. Mola borrowed a genealogy of the gods and a Virgil with commentary, then selected myths and the Milky Way to represent Air.",
        },
        "updates": {},
        "qualifier_updates": {
            "claim": "Prince Camillo Pamfili commissioned Pier Francesco Mola to paint the Four Elements at Valmontone. Mola asked a local lawyer to lend him a genealogy of the gods and a Virgil with commentary, then selected myths and the Milky Way to represent Air.",
            "relation_candidate_note": "Haskell reports the commission and says Mola asked a local lawyer to lend him reference books; the passage does not say the books were lent. The mapped endpoints remain Mola and the indexed Four Elements work.",
        },
    },
    "st-chp1-secii-l79-84-10": {
        "expected": {"object_candidate_id": "cand-11840"},
        "updates": {"object_candidate_id": "cand-11839"},
        "qualifier_updates": {
            "relation_candidate_note": "Arragona advises the Duke, addressed as 'His Highness', to send a deposit; the ducal chancellor is the letter's addressee, not the advice's recipient. The proposed payment is not recorded as completed.",
        },
    },
    "st-chp1-secii-l79-84-04": {
        "expected": {
            "claim": "Haskell quotes an agent’s 1662 report that Claude Lorrain charged clients generously and set a price only for people of “mediocre condition.”",
        },
        "updates": {},
        "qualifier_updates": {
            "claim": "Haskell quotes an agent writing in 1662 that a prospective buyer of a Claude picture would have to pay generously and that Claude fixed a price only for people of 'mediocre condition'.",
            "qualification": "This is the agent's report about a possible purchase and Claude's pricing; it does not establish that the purchase occurred or describe every commission.",
        },
    },
    "st-chp8-p219-giordano-crossing-assigned": {
        "expected": {
            "subject_candidate_id": "cand-7641",
            "object_candidate_id": "cand-1172",
        },
        "updates": {"subject_candidate_id": "cand-7668"},
        "qualifier_updates": {
            "claim": "Haskell says that in 1682 the third large oil painting, The Crossing of the Red Sea, was entrusted to Luca Giordano; the subject had earlier fascinated Ciro Ferri.",
            "relation_candidate_note": "The reported painting commission links the Crossing of the Red Sea work candidate to Luca Giordano in 1682. The committee remains commissioning context, and Ciro Ferri remains earlier subject context.",
        },
    },
    "st-chp8-p224-contini-architect": {
        "expected": {"subject_candidate_id": "cand-0836"},
        "updates": {"subject_candidate_id": "cand-0835"},
        "qualifier_updates": {
            "mentioned_candidate_ids": ["cand-0835", "cand-7731"],
        },
    },
    "st-chp8-p224-commissioned-aeneid-episodes": {
        "expected": {
            "object_candidate_id": "cand-7763",
            "predicate": "commissioned_pictures_of_episodes_from",
        },
        "updates": {
            "object_candidate_id": "cand-12083",
            "predicate": "commissioned_pictures",
        },
        "qualifier_updates": {
            "relation_candidate_note": "Haskell says Raimondo began commissioning gallery pictures of individual Aeneid episodes. The commissioned object is the unidentified canvas group cand-12083; the Aeneid is the narrative source, separately linked by st-chp8-p224-aeneid-cycle-and-style.",
            "mentioned_candidate_ids": ["cand-0467", "cand-12083", "cand-7763", "cand-7749"],
        },
    },
    "st-chp15-p363-contemporary-praised-villa": {
        "expected": {
            "speaker": "Haskell",
            "text_layer": "authorial report",
        },
        "updates": {},
        "qualifier_updates": {
            "speaker": "One of Farsetti's contemporaries, quoted by Haskell",
            "text_layer": "quotation from an unnamed contemporary as reported by Haskell",
        },
    },
    "st-chp15-p368-querini-private-art-public-interest": {
        "expected": {
            "predicate": "confined_art_interest_to_private_use",
            "claim": "Haskell says Querini confined his love of art strictly to private use.",
            "original_quote": "but he confmed his love of art strictly to his private\nUse",
        },
        "updates": {
            "predicate": "confined_art_interest_to_private_life",
        },
        "qualifier_updates": {
            "claim": "Haskell says Querini confined his love of art strictly to his private life.",
            "qualification": "The printed page reads 'private life'; S0 OCR split and misread the word as 'private Use'. The following accusation of advancing private interests at public expense remains in its separate statement.",
        },
    },
    "st-chp15-p367-note2-apologhi-authored-by-lodoli": {
        "expected": {
            "original_quote": "dal Fu Carlo de’ Conti Lodoli",
        },
        "updates": {
            "original_quote": "Apologhi immaginati, e sol estemporaneamente in voce esposti agli amici suoi dal Fu Carlo de’ Conti Lodoli Min. Osservante di S. Francesco, facilmente utili all’onesta Gioventù, ed ora per la prima volta pubblicati nell'occasione del Solenne Ingresso che fa alla Procurala di S. Marco l’eccellentissimo Signor Andrea Memmo, Cavaliere della Stola d’Oro. Bassano [Remondini], 1787.",
        },
        "qualifier_updates": {
            "qualification": "The full title wording is transcribed from Haskell’s p.367 note; the cited edition has not been independently consulted.",
        },
    },
    "st-chp15-p371-relief-depicts-ignorance": {
        "expected": {
            "source_line_start": 72,
            "source_line_end": 73,
            "original_quote": "Hence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
        },
        "updates": {
            "original_quote": "The same aspect of Querini’s temperament was emphasised in the Altar dedicated to\nIgnorance, Envy and Calumny; for, as Mme Rosenberg pointed out, his soul was ‘somewhat pagan or at least Manichean’, and he believed that, the world being what it was, one should sacrifice to evil as well as to good spirits if one was to hope for happiness.\nHence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
        },
        "qualifier_updates": {
            "source_line_start": 70,
            "source_line_end": 73,
        },
    },
    "st-chp15-p371-relief-depicts-envy": {
        "expected": {
            "source_line_start": 72,
            "source_line_end": 73,
            "original_quote": "Hence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
        },
        "updates": {
            "original_quote": "The same aspect of Querini’s temperament was emphasised in the Altar dedicated to\nIgnorance, Envy and Calumny; for, as Mme Rosenberg pointed out, his soul was ‘somewhat pagan or at least Manichean’, and he believed that, the world being what it was, one should sacrifice to evil as well as to good spirits if one was to hope for happiness.\nHence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
        },
        "qualifier_updates": {
            "source_line_start": 70,
            "source_line_end": 73,
        },
    },
    "st-chp15-p371-relief-depicts-calumny": {
        "expected": {
            "source_line_start": 72,
            "source_line_end": 73,
            "original_quote": "Hence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
        },
        "updates": {
            "original_quote": "The same aspect of Querini’s temperament was emphasised in the Altar dedicated to\nIgnorance, Envy and Calumny; for, as Mme Rosenberg pointed out, his soul was ‘somewhat pagan or at least Manichean’, and he believed that, the world being what it was, one should sacrifice to evil as well as to good spirits if one was to hope for happiness.\nHence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
        },
        "qualifier_updates": {
            "source_line_start": 70,
            "source_line_end": 73,
        },
    },
    "st-chp15-p371-de-non-later-director-of-napoleon-museums": {
        "expected": {
            "object_candidate_id": "cand-1701",
            "mentioned_candidate_ids": ["cand-1752", "cand-10591"],
        },
        "updates": {"object_candidate_id": None},
        "qualifier_updates": {
            "open_endpoint_reason": "Haskell reports De Non as Napoleon's director of museums. cand-1701 is Morelli and is unrelated; cand-10591 is Napoleon, not the museum institution or office. The office endpoint remains open pending a source-grounded institution or role candidate.",
            "relation_candidate_note": "This records Haskell's report of De Non's later museum office; Napoleon is context, not the institutional office endpoint.",
        },
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def prepare_statements(before: bytes) -> tuple[bytes, list[dict[str, object]]]:
    bom = b"\xef\xbb\xbf" if before.startswith(b"\xef\xbb\xbf") else b""
    raw_lines = before[len(bom) :].splitlines(keepends=True)
    rows: dict[str, dict[str, object]] = {}
    line_by_id: dict[str, int] = {}
    for index, raw_line in enumerate(raw_lines):
        body = raw_line.rstrip(b"\r\n")
        if not body.strip():
            continue
        row = json.loads(body.decode("utf-8"))
        statement_id = row["statement_id"]
        if statement_id in rows:
            raise SystemExit(f"duplicate statement ID: {statement_id}")
        rows[statement_id] = row
        line_by_id[statement_id] = index

    replacements: dict[int, bytes] = {}
    changed: list[dict[str, object]] = []
    for statement_id, fix in FIXES.items():
        if statement_id not in rows:
            raise SystemExit(f"missing statement: {statement_id}")
        row = rows[statement_id]
        qualifiers = dict(row.get("qualifiers") or {})
        expected = dict(fix["expected"])
        for key, value in expected.items():
            actual = qualifiers.get(key) if key in {"claim", "speaker", "text_layer", "mentioned_candidate_ids", "source_line_start", "source_line_end"} else row.get(key)
            if actual != value:
                raise SystemExit(f"evidence guard failed: {statement_id}.{key}: {actual!r}")

        for key, value in fix["updates"].items():
            row[key] = value
        qualifiers.update(fix["qualifier_updates"])
        row["qualifiers"] = qualifiers
        index = line_by_id[statement_id]
        ending = b"\r\n" if raw_lines[index].endswith(b"\r\n") else b"\n"
        replacements[index] = json.dumps(row, ensure_ascii=False).encode("utf-8") + ending
        changed.append({"statement_id": statement_id, "updated_fields": sorted([*fix["updates"], *fix["qualifier_updates"]])})

    output = bom + b"".join(replacements.get(i, line) for i, line in enumerate(raw_lines))
    return output, changed


def prepare_mentions(before: bytes) -> tuple[bytes, list[dict[str, object]]]:
    text = before.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fieldnames = list(reader.fieldnames or [])
    rows = list(reader)
    rows_by_id = {row["mention_id"]: row for row in rows}
    if len(rows_by_id) != len(rows):
        raise SystemExit("mention IDs are not unique")

    contini = rows_by_id.get("m-chp8-p224-contini")
    if contini is None or contini.get("candidate_id") != "cand-0836":
        raise SystemExit("evidence guard failed: m-chp8-p224-contini candidate")
    contini["candidate_id"] = "cand-0835"
    contini["note"] = "Person Giovanni Battista Contini; use the person index entry, not the Buonaccorsi-palace place subentry."
    changed: list[dict[str, object]] = [{"mention_id": "m-chp8-p224-contini", "candidate_id": "cand-0835"}]

    source_lines = SOURCE_CH8.read_text(encoding="utf-8-sig").splitlines()
    segment_text = " ".join(source_lines[151:161])
    expected_existing = segment_text.find("the Aeneid")
    if expected_existing != 1337:
        raise SystemExit(f"source offset guard failed for chapter 8 segment: {expected_existing}")

    additions = [
        {
            "mention_id": "m-chp8-p224-large-canvases",
            "segment_id": "chp-8:08_CHP-8_sec_ii:l152-161",
            "candidate_id": "cand-12083",
            "surface_form": "huge square and rectangular canvases",
            "start_char": str(segment_text.index("huge square and rectangular canvases")),
            "end_char": str(segment_text.index("huge square and rectangular canvases") + len("huge square and rectangular canvases")),
            "note": "Unidentified large-canvas group decorating the Buonaccorsi gallery; individual titles are not supplied here.",
        },
        {
            "mention_id": "m-chp8-p224-episode-pictures",
            "segment_id": "chp-8:08_CHP-8_sec_ii:l152-161",
            "candidate_id": "cand-12083",
            "surface_form": "the pictures of single episodes",
            "start_char": str(segment_text.index("the pictures of single episodes")),
            "end_char": str(segment_text.index("the pictures of single episodes") + len("the pictures of single episodes")),
            "note": "Raimondo's reported gallery-picture commission; the Aeneid is the narrative source, not the commissioned object.",
        },
    ]
    for row in additions:
        if row["mention_id"] in rows_by_id:
            raise SystemExit(f"mention already exists: {row['mention_id']}")
        rows.append(row)
        changed.append({"mention_id": row["mention_id"], "candidate_id": row["candidate_id"], "start_char": row["start_char"], "end_char": row["end_char"]})

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    encoded = output.getvalue().encode("utf-8")
    if before.startswith(b"\xef\xbb\xbf"):
        encoded = b"\xef\xbb\xbf" + encoded
    return encoded, changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Integrate independently reported S2 corrections with guarded dry-run/apply.")
    parser.add_argument("--apply", action="store_true", help="apply changes and retain exact recovery backups")
    args = parser.parse_args()

    before_statements = STATEMENTS.read_bytes()
    before_mentions = MENTIONS.read_bytes()
    after_statements, changed_statements = prepare_statements(before_statements)
    after_mentions, changed_mentions = prepare_mentions(before_mentions)
    report = {
        "mode": "apply" if args.apply else "dry_run",
        "statements_changed": changed_statements,
        "mentions_changed_or_added": changed_mentions,
        "statement_sha256_before": digest(before_statements),
        "statement_sha256_after": digest(after_statements),
        "mention_sha256_before": digest(before_mentions),
        "mention_sha256_after": digest(after_mentions),
        "statement_backup": str(STATEMENTS_BACKUP.relative_to(ROOT)),
        "mention_backup": str(MENTIONS_BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return

    if STATEMENTS.read_bytes() != before_statements or MENTIONS.read_bytes() != before_mentions:
        raise SystemExit("source tables changed after preflight; rerun dry-run")
    for backup, before in ((STATEMENTS_BACKUP, before_statements), (MENTIONS_BACKUP, before_mentions)):
        if backup.exists() and backup.read_bytes() != before:
            raise SystemExit(f"refusing to overwrite a different recovery backup: {backup.name}")
        if not backup.exists():
            shutil.copy2(STATEMENTS if backup == STATEMENTS_BACKUP else MENTIONS, backup)
    atomic_write(STATEMENTS, after_statements)
    atomic_write(MENTIONS, after_mentions)
    if digest(STATEMENTS.read_bytes()) != report["statement_sha256_after"] or digest(MENTIONS.read_bytes()) != report["mention_sha256_after"]:
        atomic_write(STATEMENTS, before_statements)
        atomic_write(MENTIONS, before_mentions)
        raise SystemExit("post-write hash mismatch; original tables restored")
    print("applied; recovery backups retained; output hashes verified")


if __name__ == "__main__":
    main()
