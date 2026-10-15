from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/16_CHP-16_intro.md"
PDF = ROOT / "02-sources/01-book/CHP-16.pdf"
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
BACKUP_SUFFIX = ".bak-s2-chp16-p376-semantic-refine-20261009"

EXPECTED_SHA256 = {
    SOURCE: "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff",
    PDF: "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f",
    STATEMENTS: "4ef3547e3a0c226085aceb72343ff467793661886ec73060a02535daa5df12dd",
    MENTIONS: "d7c0b23117309ffcc8a69824d518e9c1fdcd7e01032d703f388e61197823964d",
    CANDIDATES: "b13f93e673abcbdd80e88e10cb45d993549d0aba97fbe703213091f9e4603f3c",
}

BODY_SEGMENT = "chp-16:16_CHP-16_intro:l38-46"
NOTE_SEGMENT = "chp-16:16_CHP-16_intro:l69-89"
SOURCE_FILE = "02-sources/02-Markdown/16_CHP-16_intro.md"
PAGE_BASIS = "CHP-16.pdf physical page 4."


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[bytes, list[dict[str, Any]], list[bytes]]:
    raw = path.read_bytes()
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line.decode("utf-8")) for line in lines if line.strip()]
    return raw, rows, lines


def csv_replace_row(raw: bytes, key: str, value: str, replacement: dict[str, str]) -> bytes:
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw.decode("utf-8-sig")
    physical = text.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader)
    if key not in header:
        raise ValueError(f"CSV key field {key!r} is missing")
    key_index = header.index(key)
    previous_line = reader.line_num
    hits = 0
    for cells in reader:
        end_line = reader.line_num
        if len(cells) != len(header):
            raise ValueError(f"Malformed CSV row ending at physical line {end_line}")
        if cells[key_index] == value:
            hits += 1
            cells[header.index("detail")] = replacement["detail"]
            ending = "\r\n" if physical[end_line - 1].endswith("\r\n") else "\n" if physical[end_line - 1].endswith("\n") else ""
            buffer = io.StringIO(newline="")
            csv.writer(buffer, lineterminator="").writerow(cells)
            physical[previous_line:end_line] = [buffer.getvalue() + ending]
            break
        previous_line = end_line
    if hits != 1:
        raise ValueError(f"Expected one {key}={value!r} row, found {hits}")
    return bom + "".join(physical).encode("utf-8")


def csv_append_row(raw: bytes, row: dict[str, str]) -> bytes:
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw.decode("utf-8-sig")
    header_reader = csv.reader(io.StringIO(text, newline=""))
    header = next(header_reader)
    if set(row) != set(header):
        raise ValueError("New mention fields do not match the CSV header")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator=newline).writerow([row[field] for field in header])
    if text and not text.endswith(("\n", "\r")):
        text += newline
    return bom + (text + buffer.getvalue()).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Refine p.376 S2 statements; default is a hash-guarded dry-run.")
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes after creating verified backups")
    args = parser.parse_args()

    for path, expected in EXPECTED_SHA256.items():
        actual = sha256(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"Refusing to run: SHA-256 changed for {path.relative_to(ROOT)}: {actual}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    _, statement_rows, statement_lines = read_jsonl(STATEMENTS)
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    if len(statement_by_id) != len(statement_rows):
        raise SystemExit("Duplicate statement IDs detected")

    original_ids = [
        "st-chp16-p376-vianello-circle-membership",
        "st-chp16-p376-vianello-canon-of-chioggia-cathedral",
        "st-chp16-p376-vianello-scholarship-and-rosalba-journal-edition",
        "st-chp16-p376-vianello-dealer-and-picture-catalogue",
        "st-chp16-p376-vianello-large-venetian-collection",
        "st-chp16-p376-vianello-vecchia-pictures",
        "st-chp16-p376-vianello-artists-and-preferred-works",
        "st-chp16-p376-vianello-guardi-works",
        "st-chp16-p376-vianello-defends-guardi",
        "st-chp16-p376-vianello-guardi-aesthetic-qualities",
        "st-chp16-p376-toninotto-introduction",
        "st-chp16-p376-toninotto-showed-tourists-around-frari",
        "st-chp16-p376-toninotto-disgrace-with-state-inquisition",
        "st-chp16-p376-toninotto-recording-venetian-art",
        "st-chp16-p376-toninotto-del-pian-prints-after-carpaccio",
        "st-chp16-p376-toninotto-collection-similar-taste",
        "st-chp16-p376-del-pian-maker-of-print-series",
        "st-chp16-p376-del-pian-prints-of-carpaccio-cycle",
        "st-chp16-p376-toninotto-attributed-old-masters",
        "st-chp16-p376-toninotto-mixed-collection",
        "st-chp16-p376-toninotto-vecchia-works",
        "st-chp16-p376-toninotto-zais-works",
        "st-chp16-p376-toninotto-guardi-works",
        "st-chp16-p376-toninotto-guardi-capricci",
        "st-chp16-p376-toninotto-unnamed-venetian-views",
        "st-chp16-p376-swajer-biography-and-manuscripts",
        "st-chp16-p376-swajer-secret-manuscripts-partial",
        "st-chp16-p376-note1-vianello-catalogue",
        "st-chp16-p376-note2-haskell-journal",
        "st-chp16-p376-note3-swajer-correspondence-partial",
    ]
    if any(identifier not in statement_by_id for identifier in original_ids):
        raise SystemExit("A required p.376 statement ID is missing")
    if sum(identifier.startswith("st-chp16-p376-") for identifier in statement_by_id) != 30:
        raise SystemExit("Unexpected p.376 statement inventory")

    def update(
        identifier: str,
        quote: str,
        start: int,
        end: int,
        claim: str,
        qualification: str,
        mentioned: list[str],
        relation: bool,
        *,
        predicate: str | None = None,
        subject: str | None = None,
        object_id: str | None | object = ...,
        speaker: str | None = None,
        text_layer: str | None = None,
        ocr: list[dict[str, Any]] | None = None,
        remove_prefixes: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        row = copy.deepcopy(statement_by_id[identifier])
        q = row["qualifiers"]
        q["source_line_start"] = start
        q["source_line_end"] = end
        q["printed_page"] = 376
        q["pdf_physical_page"] = 4
        q["claim"] = claim
        q["qualification"] = qualification
        q["mentioned_candidate_ids"] = mentioned
        q["relation_candidate"] = relation
        if speaker:
            q["speaker"] = speaker
        if text_layer:
            q["text_layer"] = text_layer
        if ocr:
            q["ocr_corrections"] = ocr
        else:
            q.pop("ocr_corrections", None)
        for key in list(q):
            if any(key.startswith(prefix) for prefix in remove_prefixes):
                q.pop(key, None)
        row["original_quote"] = quote
        if predicate is not None:
            row["predicate"] = predicate
        if subject is not None:
            row["subject_candidate_id"] = subject
        if object_id is not ...:
            row["object_candidate_id"] = object_id
        return row

    def new_statement(
        identifier: str,
        template_id: str,
        subject: str | None,
        object_id: str | None,
        predicate: str,
        quote: str,
        start: int,
        end: int,
        claim: str,
        qualification: str,
        mentioned: list[str],
        relation: bool,
        text_layer: str,
        ocr: list[dict[str, Any]] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if identifier in statement_by_id:
            raise SystemExit(f"New statement ID already exists: {identifier}")
        row = copy.deepcopy(statement_by_id[template_id])
        row.update(
            {
                "statement_id": identifier,
                "segment_id": BODY_SEGMENT,
                "subject_candidate_id": subject,
                "object_candidate_id": object_id,
                "predicate": predicate,
                "original_quote": quote,
                "origin": "book",
                "source_file": SOURCE_FILE,
                "qualifiers": {
                    "source_line_start": start,
                    "source_line_end": end,
                    "printed_page": 376,
                    "pdf_physical_page": 4,
                    "claim": claim,
                    "speaker": "Haskell",
                    "text_layer": text_layer,
                    "qualification": qualification,
                    "mentioned_candidate_ids": mentioned,
                    "relation_candidate": relation,
                },
            }
        )
        if ocr:
            row["qualifiers"]["ocr_corrections"] = ocr
        if extra:
            row["qualifiers"].update(extra)
        return row

    def correction(line: int, ocr: str, printed: str) -> dict[str, Any]:
        return {"source_file": SOURCE_FILE, "source_line": line, "ocr": ocr, "print": printed, "basis": PAGE_BASIS}

    c_vianello_name = [correction(39, "ofChioggia", "of Chioggia"), correction(39, "GiovanniVianello", "Giovanni Vianello")]
    c_pietro = [correction(41, "Pietrp", "Pietro")]
    c_alla = [correction(41, "‘alia Giorgionesca’", "‘alla Giorgionesca’")]
    c_pittori_punctuation = [correction(42, "Pittori’. .", "Pittori’.")]
    c_modelli = [correction(44, "tnodelli", "modelli")]
    c_mostly = [correction(84, "mosdy", "mostly")]

    updates: dict[str, dict[str, Any]] = {}
    updates["st-chp16-p376-vianello-circle-membership"] = update(
        "st-chp16-p376-vianello-circle-membership",
        "who may well have belonged to the circle of Sasso and della Lena",
        39,
        39,
        "Haskell says Dr Giovanni Vianello may well have belonged to the circle of Sasso and della Lena.",
        "The hedge and the circle's membership remain unresolved; this does not assert separate membership relations with either person.",
        ["cand-2764", "cand-2364", "cand-1387"],
        False,
    )
    updates["st-chp16-p376-vianello-canon-of-chioggia-cathedral"] = update(
        "st-chp16-p376-vianello-canon-of-chioggia-cathedral",
        "a canon ofChioggia Cathedral, Dr GiovanniVianello.",
        39,
        39,
        "Haskell identifies Dr Giovanni Vianello as a canon of Chioggia Cathedral.",
        "The candidate's institutional or building referent is unresolved.",
        ["cand-2764", "cand-10641"],
        True,
        ocr=c_vianello_name,
    )
    updates["st-chp16-p376-vianello-scholarship-and-rosalba-journal-edition"] = update(
        "st-chp16-p376-vianello-scholarship-and-rosalba-journal-edition",
        "in the edition he brought out in 1793 of Rosalba’s journal.",
        41,
        41,
        "Haskell reports that Vianello brought out an edition of Rosalba's journal in 1793.",
        "The journal and edition are not titled or independently consulted.",
        ["cand-2764", "cand-10631", "cand-0581"],
        True,
    )
    updates["st-chp16-p376-vianello-dealer-and-picture-catalogue"] = update(
        "st-chp16-p376-vianello-dealer-and-picture-catalogue",
        "It is not certain whether or not he was a dealer",
        41,
        41,
        "Haskell says it is uncertain whether Vianello was a dealer.",
        "The source leaves his dealer status unresolved.",
        ["cand-2764"],
        False,
        predicate="dealer_status_uncertain",
        remove_prefixes=("footnote_",),
    )
    updates["st-chp16-p376-vianello-large-venetian-collection"] = update(
        "st-chp16-p376-vianello-large-venetian-collection",
        "He owned over 200 pictures",
        41,
        41,
        "Haskell says Vianello owned more than 200 pictures.",
        "The passage gives no inventory or individual titles.",
        ["cand-2764"],
        False,
        predicate="owned_over_two_hundred_pictures",
    )
    updates["st-chp16-p376-vianello-vecchia-pictures"] = update(
        "st-chp16-p376-vianello-vecchia-pictures",
        "by whom he owned twenty-five pictures",
        41,
        41,
        "Haskell says Vianello owned twenty-five pictures by Pietro della Vecchia.",
        "The antecedent is Pietro della Vecchia, whom Haskell has just called Vianello's special favourite; individual pictures are unidentified.",
        ["cand-2764", "cand-2707", "cand-10633"],
        True,
    )
    updates["st-chp16-p376-vianello-artists-and-preferred-works"] = update(
        "st-chp16-p376-vianello-artists-and-preferred-works",
        "Most of the great artists of his century were well represented with many drawings and paintings by Rosalba, Ricci, Piazzetta and Tiepolo.",
        42,
        42,
        "Haskell says Vianello's collection included many drawings and paintings by Rosalba, Ricci, Piazzetta, and Tiepolo.",
        "Ricci is given by surname only; the index lists both Marco and Sebastiano Ricci at p.376, so identity remains unresolved.",
        ["cand-2764", "cand-0581", "cand-10645", "cand-1901", "cand-2569"],
        False,
    )
    updates["st-chp16-p376-vianello-guardi-works"] = update(
        "st-chp16-p376-vianello-guardi-works",
        "Vianello also owned three works by Francesco Guardi—two paintings and a drawing",
        42,
        42,
        "Haskell says Vianello owned three works by Francesco Guardi: two paintings and one drawing.",
        "No individual Guardi work is titled or located.",
        ["cand-2764", "cand-10634", "cand-1239"],
        True,
    )
    updates["st-chp16-p376-vianello-defends-guardi"] = update(
        "st-chp16-p376-vianello-defends-guardi",
        "He deplored Guardi’s absence from the standard reference books.",
        42,
        42,
        "Haskell says Vianello deplored Guardi's absence from standard reference books.",
        "No particular reference book is named.",
        ["cand-2764", "cand-1239"],
        False,
        predicate="deplored_guardis_absence_from_standard_reference_books",
    )
    updates["st-chp16-p376-vianello-guardi-aesthetic-qualities"] = update(
        "st-chp16-p376-vianello-guardi-aesthetic-qualities",
        "Above all he specially admired him for those qualities that were peculiarly his own—the movement, the colour, the vivacity, the sparkling lights, the macchiette ‘secondo si dice dalli Pittori’. .",
        42,
        42,
        "Haskell says Vianello especially admired Guardi's movement, colour, vivacity, sparkling lights, and macchiette, using the phrase 'secondo si dice dalli Pittori'.",
        "This is Haskell's account of Vianello's aesthetic judgment; S0 contains an extra terminal period, corrected only in S2.",
        ["cand-2764", "cand-1239"],
        True,
        ocr=c_pittori_punctuation,
    )
    updates["st-chp16-p376-toninotto-introduction"] = update(
        "st-chp16-p376-toninotto-introduction",
        "More modest than any of these but with similar tastes was the Dominican Padre\nGiuseppe Toninotto.2",
        43,
        44,
        "Haskell introduces Dominican Padre Giuseppe Toninotto as more modest than the preceding collectors but similar in taste.",
        "'More modest' is Haskell's comparison, not an independent social ranking.",
        ["cand-2643", "cand-0941"],
        False,
    )
    updates["st-chp16-p376-toninotto-showed-tourists-around-frari"] = update(
        "st-chp16-p376-toninotto-showed-tourists-around-frari",
        "as he shows them round the Frari",
        44,
        44,
        "Haskell says Toninotto showed foreign tourists around the Frari.",
        "The passage does not specify a paid guide role; 'them' refers to the foreign tourists in the preceding clause.",
        ["cand-2643", "cand-10642"],
        True,
        predicate="showed_foreign_tourists_around",
    )
    updates["st-chp16-p376-toninotto-disgrace-with-state-inquisition"] = update(
        "st-chp16-p376-toninotto-disgrace-with-state-inquisition",
        "or in disgrace with the State Inquisition for selling improper prints",
        44,
        44,
        "Haskell says Toninotto was in disgrace with the State Inquisition for selling improper prints.",
        "The source does not specify a formal proceeding or outcome.",
        ["cand-2643", "cand-10524"],
        True,
    )
    updates["st-chp16-p376-toninotto-recording-venetian-art"] = update(
        "st-chp16-p376-toninotto-recording-venetian-art",
        "Yet he too played his part in helping to record—and to collect— some of the glories of Venetian art before the Republic finally collapsed.",
        44,
        44,
        "Haskell says Toninotto helped record and collect some of the glories of Venetian art before the Venetian Republic finally collapsed.",
        "The Republic is the Venetian political entity, not the city; no exact collapse date is added.",
        ["cand-2643", "cand-8838"],
        False,
    )
    updates["st-chp16-p376-toninotto-del-pian-prints-after-carpaccio"] = update(
        "st-chp16-p376-toninotto-del-pian-prints-after-carpaccio",
        "In 1785 he was responsible for publishing a series of nine large prints by Giovanni del Pian of Carpaccio’s famous scenes of the Life of St Ursula.",
        44,
        44,
        "Haskell says Toninotto was responsible in 1785 for publishing nine large prints by Giovanni del Pian of Carpaccio's Life of St Ursula scenes.",
        "The print series is distinct from Carpaccio's source cycle; individual print titles and the publication imprint are not given.",
        ["cand-2643", "cand-1899", "cand-10636", "cand-10635", "cand-0566"],
        True,
    )
    updates["st-chp16-p376-toninotto-collection-similar-taste"] = update(
        "st-chp16-p376-toninotto-collection-similar-taste",
        "And his collection shows a similar taste to those that have already been investigated.",
        44,
        44,
        "Haskell says Toninotto's collection showed a similar taste to those previously discussed.",
        "This is Haskell's broad comparison; the sentence does not identify a complete inventory or particular works.",
        ["cand-11502", "cand-2643"],
        False,
    )
    updates["st-chp16-p376-del-pian-maker-of-print-series"] = update(
        "st-chp16-p376-del-pian-maker-of-print-series",
        "prints by Giovanni del Pian",
        44,
        44,
        "Haskell identifies Giovanni del Pian as the maker of the nine-print series.",
        "The work group is not individually titled.",
        ["cand-10636", "cand-1899"],
        True,
    )
    updates["st-chp16-p376-del-pian-prints-of-carpaccio-cycle"] = update(
        "st-chp16-p376-del-pian-prints-of-carpaccio-cycle",
        "Carpaccio’s famous scenes of the Life of St Ursula",
        44,
        44,
        "Haskell identifies Carpaccio's Life of St Ursula scenes as the subject of the nine-print series.",
        "The print series is distinct from the source cycle; no individual print titles are supplied.",
        ["cand-10636", "cand-10635"],
        True,
    )
    updates["st-chp16-p376-toninotto-attributed-old-masters"] = update(
        "st-chp16-p376-toninotto-attributed-old-masters",
        "There were, of course, some old masters with ambitious attributions to Titian, Bassano and others.",
        44,
        44,
        "Haskell says Toninotto's collection included old masters with ambitious attributions to Titian, Bassano, and others.",
        "No individual picture or attribution is specified or independently assessed.",
        ["cand-2643", "cand-2630", "cand-0257", "cand-4288", "cand-11502"],
        False,
    )
    updates["st-chp16-p376-toninotto-mixed-collection"] = update(
        "st-chp16-p376-toninotto-mixed-collection",
        "and many Flemish paintings, as well as a selection of eighteenth-century pictures, mainly small views and landscapes by Carlevarijs, Marco Ricci and Marieschi.",
        44,
        44,
        "Haskell lists Flemish paintings and eighteenth-century pictures in Toninotto's collection, mainly small views and landscapes by Carlevarijs, Marco Ricci, and Marieschi.",
        "The individual Flemish paintings and views are not titled; the source names the makers of the views.",
        ["cand-2643", "cand-0554", "cand-2149", "cand-1546", "cand-11502"],
        False,
    )
    updates["st-chp16-p376-toninotto-vecchia-works"] = update(
        "st-chp16-p376-toninotto-vecchia-works",
        "a couple of Pietro della Vecchias ‘sulla maniera di Zorzone’",
        44,
        44,
        "Haskell says Toninotto had a couple of works by Pietro della Vecchia described as 'sulla maniera di Zorzone'.",
        "The two works are unnamed and their medium is not specified; the identity behind 'Zorzone' remains unresolved.",
        ["cand-2643", "cand-2707", "cand-10646"],
        True,
    )
    updates["st-chp16-p376-toninotto-zais-works"] = update(
        "st-chp16-p376-toninotto-zais-works",
        "twelve paintings and four drawings by the former",
        44,
        44,
        "Haskell says Toninotto owned twelve paintings and four drawings by Giuseppe Zais.",
        "The individual works are not titled or located; 'the former' refers to Giuseppe Zais.",
        ["cand-2643", "cand-2830", "cand-10637"],
        True,
    )
    updates["st-chp16-p376-toninotto-guardi-works"] = update(
        "st-chp16-p376-toninotto-guardi-works",
        "eight paintings by the latter",
        44,
        44,
        "Haskell says Toninotto owned eight paintings by Francesco Guardi.",
        "'The latter' refers to Francesco Guardi; the following sentences describe two subsets of the eight paintings.",
        ["cand-2643", "cand-1239", "cand-10638"],
        True,
    )
    updates["st-chp16-p376-toninotto-guardi-capricci"] = update(
        "st-chp16-p376-toninotto-guardi-capricci",
        "'caprizi copiosi di figure’",
        45,
        45,
        "Haskell describes four of Toninotto's Guardi paintings as 'caprizi copiosi di figure'.",
        "The Italian phrase is retained as printed; the individual paintings are unnamed.",
        ["cand-2643", "cand-1239", "cand-10639"],
        True,
    )
    updates["st-chp16-p376-toninotto-unnamed-venetian-views"] = update(
        "st-chp16-p376-toninotto-unnamed-venetian-views",
        "and four were unnamed Venetian views.",
        45,
        45,
        "Haskell says four of Toninotto's Guardi paintings were unnamed Venetian views.",
        "The views remain unidentified, as Haskell states.",
        ["cand-2643", "cand-1239", "cand-10640"],
        True,
    )
    updates["st-chp16-p376-swajer-biography-and-manuscripts"] = update(
        "st-chp16-p376-swajer-biography-and-manuscripts",
        "Another figure in this group was the rich German business man Amadeo Swajer (Plate 59a) who lived most of his life in Venice and died there in 1792.",
        46,
        46,
        "Haskell describes Amadeo Swajer as a wealthy German businessman who lived most of his life in Venice and died there in 1792.",
        "The source supplies no further biography.",
        ["cand-2534", "cand-2719"],
        False,
        predicate="rich_german_businessman_lived_most_of_life_in_venice_died_1792",
        object_id=None,
    )
    updates["st-chp16-p376-swajer-secret-manuscripts-partial"] = update(
        "st-chp16-p376-swajer-secret-manuscripts-partial",
        "and after his death the possible dispersal of the secret",
        46,
        46,
        "Haskell says the possible posthumous dispersal of Swajer's 'secret' manuscripts raised concern; the sentence continues on p.377.",
        "P.377 L49 completes the sentence: the possible dispersal caused anxiety to the Inquisitors of State, who acquired all the manuscripts.",
        ["cand-2534", "cand-10643"],
        True,
    )
    updates["st-chp16-p376-note1-vianello-catalogue"] = update(
        "st-chp16-p376-note1-vianello-catalogue",
        "1 See the catalogue of his pictures published in. 1790.",
        82,
        82,
        "Haskell's note points to the catalogue of Vianello's pictures published in 1790.",
        "The catalogue was not independently consulted; OCR punctuation is corrected only in S2.",
        ["cand-10630", "cand-2764"],
        False,
    )
    updates["st-chp16-p376-note2-haskell-journal"] = update(
        "st-chp16-p376-note2-haskell-journal",
        "2 Haskell, in Journal os Warburg Institute, i960, pp. 263-4, for all references.",
        83,
        83,
        "Haskell's note cites his Journal of Warburg Institute article, 1960, pages 263-4, for references.",
        "The article title and full publication details are not supplied; the cited pages were not consulted.",
        ["cand-10629", "cand-6004", "cand-3770"],
        False,
    )
    updates["st-chp16-p376-note3-swajer-correspondence-partial"] = update(
        "st-chp16-p376-note3-swajer-correspondence-partial",
        "3 A good deal of Swajer’s correspondence is in the Seminario Patriarcale in Venice—above all a volume of letters dating from the 1750s and 1760s, mosdy concerned with literature, addressed to him",
        84,
        84,
        "Haskell's note locates much of Swajer's correspondence at Seminario Patriarcale and highlights a volume of letters from the 1750s and 1760s, mostly concerned with literature and addressed to him.",
        "The cited letters were not independently consulted; p.377 continues the note with other correspondence and archive details.",
        ["cand-10644", "cand-2534", "cand-6589", "cand-2719"],
        False,
        ocr=c_mostly,
    )

    note1_qualifiers = statement_by_id["st-chp16-p376-vianello-dealer-and-picture-catalogue"]["qualifiers"]
    catalogue_footnote = {key: copy.deepcopy(value) for key, value in note1_qualifiers.items() if key.startswith("footnote_")}

    additions = [
        new_statement(
            "st-chp16-p376-vianello-scholarship-assessment",
            "st-chp16-p376-vianello-scholarship-and-rosalba-journal-edition",
            "cand-2764",
            None,
            "had_pretensions_to_scholarship_as_assessed_by_haskell",
            "Like them he had pretensions to scholarship which he showed—though hardly justified",
            40,
            40,
            "Haskell says Vianello displayed pretensions to scholarship and judges them hardly justified.",
            "This is Haskell's evaluation, not an independent assessment of the edition.",
            ["cand-2764"],
            False,
            "authorial evaluation",
        ),
        new_statement(
            "st-chp16-p376-vianello-catalogue-published-1790",
            "st-chp16-p376-vianello-dealer-and-picture-catalogue",
            "cand-2764",
            "cand-10630",
            "his_picture_catalogue_published_in_1790",
            "but the publication of a catalogue of his paintings in 1790",
            41,
            41,
            "Haskell reports publication in 1790 of a catalogue of Vianello's paintings.",
            "The catalogue's title, author, and contents are not supplied; it was not consulted.",
            ["cand-2764", "cand-10630"],
            True,
            "authorial report",
            extra=catalogue_footnote,
        ),
        new_statement(
            "st-chp16-p376-vianello-disposal-inference",
            "st-chp16-p376-vianello-dealer-and-picture-catalogue",
            "cand-2764",
            None,
            "willing_to_dispose_of_pictures_in_1790_as_inferred_by_haskell",
            "strongly suggests that he was by then willing to dispose of them.",
            41,
            41,
            "Haskell infers from the catalogue's publication that Vianello was then willing to dispose of his pictures.",
            "This is a strong suggestion, not confirmation that he was a dealer or that a sale occurred.",
            ["cand-2764", "cand-10630"],
            False,
            "qualified authorial inference",
        ),
        new_statement(
            "st-chp16-p376-vianello-collection-period-majority",
            "st-chp16-p376-vianello-large-venetian-collection",
            "cand-2764",
            None,
            "collection_mostly_venetian_seventeenth_and_eighteenth_century",
            "the vast majority of which were Venetian of the seventeenth and eighteenth centuries.",
            41,
            41,
            "Haskell says the vast majority of Vianello's pictures were Venetian works of the seventeenth and eighteenth centuries.",
            "No individual pictures are identified.",
            ["cand-2764"],
            False,
            "authorial report",
        ),
        new_statement(
            "st-chp16-p376-vianello-vecchia-favourite",
            "st-chp16-p376-vianello-vecchia-pictures",
            "cand-2764",
            "cand-2707",
            "had_as_special_favourite_artist",
            "His special favourite was Pietrp della Vecchia",
            41,
            41,
            "Haskell identifies Pietro della Vecchia as Vianello's special favourite.",
            "The artist's surname is corrected from S0 OCR only in S2.",
            ["cand-2764", "cand-2707"],
            True,
            "authorial report",
            ocr=c_pietro,
        ),
        new_statement(
            "st-chp16-p376-vianello-vecchia-fantasy-heads",
            "st-chp16-p376-vianello-vecchia-pictures",
            "cand-10633",
            "cand-10632",
            "many_were_fantasy_heads_in_alla_giorgionesca_manner",
            "many of them fantasy heads ‘alia Giorgionesca’.",
            41,
            41,
            "Haskell says many of the twenty-five pictures were fantasy heads described as 'alla Giorgionesca'.",
            "The phrase is corrected from S0 OCR only in S2; individual pictures remain unidentified.",
            ["cand-10633", "cand-10632"],
            False,
            "authorial report",
            ocr=c_alla,
        ),
        new_statement(
            "st-chp16-p376-vianello-sketch-and-bust-preference",
            "st-chp16-p376-vianello-artists-and-preferred-works",
            "cand-2764",
            None,
            "seems_to_have_preferred_sketches_and_capricious_bust_portraits",
            "Of these artists he seems to have preferred the sketches, and above all the capricious bust portraits that were so popular at the time.",
            42,
            42,
            "Haskell says Vianello seems to have preferred sketches and, above all, capricious bust portraits.",
            "The source says 'seems'; it does not identify individual sketches or portraits.",
            ["cand-2764", "cand-0581", "cand-10645", "cand-1901", "cand-2569"],
            False,
            "qualified authorial report",
        ),
        new_statement(
            "st-chp16-p376-vianello-guardi-appreciation",
            "st-chp16-p376-vianello-guardi-works",
            "cand-2764",
            "cand-1239",
            "appreciation_of_guardi_exceeded_the_work_count_suggested",
            "but his appreciation of this artist was greater than such a small number would suggest.",
            42,
            42,
            "Haskell says Vianello's appreciation of Guardi exceeded what the small number of owned works would suggest.",
            "This is Haskell's interpretation of Vianello's appreciation; no additional works are implied.",
            ["cand-2764", "cand-1239"],
            True,
            "authorial interpretation",
        ),
        new_statement(
            "st-chp16-p376-vianello-canaletto-comparison-omitted",
            "st-chp16-p376-vianello-defends-guardi",
            "cand-2764",
            "cand-0498",
            "did_not_make_unfavourable_comparison_with_canaletto",
            "Alone among those who wrote about him, he did not drag in Canaletto and make the inevitably unfavourable comparison.",
            42,
            42,
            "Haskell says Vianello did not introduce Canaletto to make the unfavourable comparison used by other writers.",
            "This describes Haskell's comparison of writers; no specific writer or publication is identified.",
            ["cand-2764", "cand-1239", "cand-0498"],
            False,
            "authorial report and comparison",
        ),
        new_statement(
            "st-chp16-p376-vianello-implied-defense-of-guardi",
            "st-chp16-p376-vianello-defends-guardi",
            "cand-2764",
            "cand-1239",
            "by_implication_defended_guardi_from_perspective_attacks",
            "By implication, indeed, he defended Guardi from the attacks that were made on his deficiencies in perspective.",
            42,
            42,
            "Haskell infers that Vianello defended Guardi against attacks on his perspective.",
            "The defense is explicitly Haskell's implication; the critics are not identified.",
            ["cand-2764", "cand-1239"],
            False,
            "authorial interpretation",
        ),
        new_statement(
            "st-chp16-p376-toninotto-begged-from-tourists",
            "st-chp16-p376-toninotto-showed-tourists-around-frari",
            "cand-2643",
            None,
            "begged_from_foreign_tourists",
            "We come across him rather pathetically begging from foreign tourists",
            44,
            44,
            "Haskell says Toninotto begged from foreign tourists.",
            "'Rather pathetically' is Haskell's evaluative tone; the tourists are not individually identified.",
            ["cand-2643"],
            False,
            "authorial report with evaluative wording",
        ),
        new_statement(
            "st-chp16-p376-toninotto-collection-included-modelli",
            "st-chp16-p376-toninotto-mixed-collection",
            "cand-11502",
            None,
            "collection_included_modelli",
            "There were a number of tnodelli",
            44,
            44,
            "Haskell says Toninotto's collection included a number of modelli.",
            "The source term is corrected from 'tnodelli' to 'modelli' by comparison with the page image; no individual model is identified.",
            ["cand-11502", "cand-1674"],
            False,
            "authorial report",
            ocr=c_modelli,
        ),
        new_statement(
            "st-chp16-p376-swajer-principal-manuscript-collector",
            "st-chp16-p376-swajer-biography-and-manuscripts",
            "cand-2534",
            None,
            "was_principally_a_collector_of_manuscripts",
            "He was principally a collector of manuscripts",
            46,
            46,
            "Haskell says Swajer was principally a collector of manuscripts.",
            "The source does not identify the manuscripts in this general description; keep it distinct from the unidentified 'secret' manuscripts in the following clause.",
            ["cand-2534"],
            False,
            "authorial report",
        ),
    ]

    # The catalogue's note link moves with the catalogue fact, not the separate dealer-status or disposal-inference statements.
    catalog_row = next(row for row in additions if row["statement_id"] == "st-chp16-p376-vianello-catalogue-published-1790")
    catalog_row["qualifiers"].update(catalogue_footnote)

    source_text = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for row in list(updates.values()) + additions:
        q = row["qualifiers"]
        start, end = q["source_line_start"], q["source_line_end"]
        evidence = "\n".join(source_text[start - 1 : end])
        if row["original_quote"] not in evidence:
            raise SystemExit(f"Quote is not an exact source substring: {row['statement_id']}")
    for identifier, row in updates.items():
        updates[identifier] = row

    statement_id_new = {row["statement_id"] for row in additions}
    if len(statement_id_new) != len(additions):
        raise SystemExit("Duplicate IDs among new statements")
    if statement_id_new.intersection(statement_by_id):
        raise SystemExit("A new statement ID already exists")

    new_mention = {
        "mention_id": "m-chp16-p376-modelli-candidate-surface",
        "segment_id": BODY_SEGMENT,
        "candidate_id": "cand-1674",
        "surface_form": "tnodelli",
        "start_char": "2481",
        "end_char": "2489",
        "note": "The mention preserves the exact S0 OCR span; CHP-16.pdf physical page 4 reads 'modelli'.",
    }
    page_segment = "\n".join([source_text[37]] + source_text[38:46])
    if page_segment[2481:2489] != "tnodelli":
        raise SystemExit("The new mention offsets do not match the p.376 source segment")

    candidates_text = CANDIDATES.read_text(encoding="utf-8-sig")
    candidate_reader = csv.DictReader(io.StringIO(candidates_text, newline=""))
    candidate_rows = list(candidate_reader)
    candidate_matches = [row for row in candidate_rows if row["candidate_id"] == "cand-10630"]
    if len(candidate_matches) != 1:
        raise SystemExit("Expected exactly one cand-10630 row")
    old_candidate_detail = candidate_matches[0]["detail"]
    expected_old_detail = "Haskell says its publication in 1790 strongly suggests Vianello was willing to dispose of his pictures; the catalogue was not consulted."
    if old_candidate_detail != expected_old_detail:
        raise SystemExit("cand-10630 detail changed from the reviewed baseline")
    new_candidate_detail = "Haskell identifies this as a catalogue of Vianello's pictures published in 1790; its title and author are not supplied here, and the catalogue was not consulted."
    candidate_new = csv_replace_row(
        CANDIDATES.read_bytes(),
        "candidate_id",
        "cand-10630",
        {"detail": new_candidate_detail},
    )

    mention_text = MENTIONS.read_bytes()
    mention_csv = list(csv.DictReader(io.StringIO(mention_text.decode("utf-8-sig"), newline="")))
    if any(row["mention_id"] == new_mention["mention_id"] for row in mention_csv):
        raise SystemExit("The new modelli mention ID already exists")
    if not any(row["candidate_id"] == new_mention["candidate_id"] for row in candidate_rows):
        raise SystemExit("The modelli candidate does not exist")
    mentions_new = csv_append_row(mention_text, new_mention)

    replacements: dict[str, bytes] = {}
    statement_new_lines = []
    inserted = False
    for line in statement_lines:
        ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
        payload = line[: -len(ending)] if ending else line
        row = json.loads(payload.decode("utf-8")) if payload.strip() else None
        if row is not None and row["statement_id"] in updates:
            row = updates[row["statement_id"]]
            statement_new_lines.append(
                json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending
            )
        else:
            if row is not None and row["statement_id"] == "st-chp16-p377-swajer-inquisitors-conclusion":
                for addition in additions:
                    statement_new_lines.append(json.dumps(addition, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
                inserted = True
            statement_new_lines.append(line)
    if not inserted:
        raise SystemExit("Could not find the p.377 insertion boundary")
    replacements[STATEMENTS] = b"".join(statement_new_lines)
    replacements[MENTIONS] = mentions_new
    replacements[CANDIDATES] = candidate_new

    changed_quote_count = len(updates) + len(additions)
    print(f"p.376 statements checked: {len(updates)} existing rows refined; {len(additions)} new statements")
    print(f"New mention: {new_mention['mention_id']} → {new_mention['candidate_id']} at {new_mention['start_char']}:{new_mention['end_char']}")
    print("Candidate detail refined: cand-10630 now describes the catalogue itself; the disposal inference remains only in the statement.")
    print(f"Exact source quote checks passed: {changed_quote_count}")
    print("Footnote 1/2/3 links, p.376→p.377 statement IDs, and p.377 continuation fields are preserved.")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")

    if not args.apply:
        for identifier, row in updates.items():
            old = statement_by_id[identifier]["original_quote"].replace("\n", " ")
            new = row["original_quote"].replace("\n", " ")
            print(f"UPDATE {identifier}: {old[:90]!r} -> {new[:110]!r}")
        for row in additions:
            print(f"ADD {row['statement_id']}: {row['original_quote'][:120]!r}")
        return 0

    backups: dict[Path, Path] = {}
    for path in replacements:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        original_hash = EXPECTED_SHA256[path]
        if backup.exists():
            if sha256(backup.read_bytes()) != original_hash:
                raise SystemExit(f"Existing backup does not match the baseline: {backup.name}")
        else:
            shutil.copy2(path, backup)
            if sha256(backup.read_bytes()) != original_hash:
                raise SystemExit(f"Backup verification failed: {backup.name}")
        backups[path] = backup

    try:
        for path, data in replacements.items():
            atomic_write(path, data)
    except Exception:
        for path, backup in backups.items():
            atomic_write(path, backup.read_bytes())
        raise

    for path in replacements:
        print(f"WROTE {path.relative_to(ROOT)} sha256={sha256(path.read_bytes())}")
        print(f"BACKUP {backups[path].relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
