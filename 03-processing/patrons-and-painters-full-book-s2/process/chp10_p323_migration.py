"""Controlled S2 migration for printed p.323; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l186-192"
NOTE_SEGMENT = "chp-10:10_CHP-10_sec_ii:l273-349"
EXPECTED_MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
EXPECTED_SEGMENT_SHA = "caba0a273883e9e3976c43c07c3dabf09911993c64e1461e55158cb98f394373"
BACKUP_SUFFIX = ".bak-s2-chp10-p323-20261003"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed p.323 rows after creating recovery copies")
parser.add_argument("--repair-coverage-range", action="store_true", help="repair the reviewed p.323 line-range syntax after an applied migration")
parser.add_argument("--repair-tiepolo-link", action="store_true", help="correct the p.323 comparison referent using the book index")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_MARKDOWN_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != EXPECTED_PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[185:192]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.323 S2 source segment changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
existing_mention_ids = {row["mention_id"] for row in mentions}
existing_statement_ids = {row["statement_id"] for row in statements}
table_state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if SEGMENT not in coverage_by_id:
    raise SystemExit("p.323 coverage row is missing")
coverage_row = coverage_by_id[SEGMENT]
if args.repair_tiepolo_link:
    if table_state != (9763, 9776, 20656, 9164):
        raise SystemExit(f"unexpected post-migration table state for Tiepolo-link repair: {table_state}")
    if (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) != ("reviewed", "partial", "L186-192"):
        raise SystemExit("p.323 coverage is not in the expected state for Tiepolo-link repair")
    selected_mentions = {
        row["mention_id"]: row for row in mentions
        if row["mention_id"] in {"m-s2-ch10-p323-0029", "m-s2-ch10-p323-0031"}
    }
    if set(selected_mentions) != {"m-s2-ch10-p323-0029", "m-s2-ch10-p323-0031"}:
        raise SystemExit("comparison Tiepolo mentions are missing")
    if any(row["candidate_id"] != "cand-2626" for row in selected_mentions.values()):
        raise SystemExit("comparison Tiepolo mentions are not in the expected pre-repair state")
    comparison = next((row for row in statements if row["statement_id"] == "st-chp10-p323-gozzi-compares-longhi-and-tiepolo"), None)
    if comparison is None or comparison["object_candidate_id"] != "cand-2626":
        raise SystemExit("comparison statement is not in the expected pre-repair state")
    backup_mentions = mention_path.with_name(mention_path.name + ".bak-s2-chp10-p323-tiepolo-identity-20261003")
    backup_statements = statement_path.with_name(statement_path.name + ".bak-s2-chp10-p323-tiepolo-identity-20261003")
    if backup_mentions.exists() or backup_statements.exists():
        raise SystemExit("Tiepolo identity recovery copy already exists")
    print("p.323 comparison-link repair preview: cand-2626 (Gian Domenico) -> cand-2569 (Giambattista); Via Crucis remains cand-2626")
    if args.apply:
        shutil.copy2(mention_path, backup_mentions)
        shutil.copy2(statement_path, backup_statements)
        for row in selected_mentions.values():
            row["candidate_id"] = "cand-2569"
            row["note"] = "The comparison is linked to the general Giambattista Tiepolo index entry (T.csv#32, p.323); keep distinct from Gian Domenico Tiepolo's S. Polo Via Crucis entry (T.csv#89)."
        comparison["object_candidate_id"] = "cand-2569"
        comparison["qualifiers"]["mentioned_candidate_ids"] = [
            "cand-2569" if cid == "cand-2626" else cid
            for cid in comparison["qualifiers"]["mentioned_candidate_ids"]
        ]
        comparison["qualifiers"]["qualification"] = (
            "The prose gives only the surname Tiepolo. The book index places Giambattista Tiepolo in its general entry T.csv#32 at p.323, while T.csv#89 specifically identifies Gian Domenico's S. Polo Via Crucis at p.323; the artistic comparison is mapped to Giambattista and kept distinct from that Via Crucis claim. 'No less perfect' is a comparison of artistic merit, not an identity or influence claim."
        )
        write_csv(mention_path, mention_fields, mentions)
        write_jsonl(statement_path, statements)
        print(f"applied; recovery copies created: {backup_mentions.name}, {backup_statements.name}")
    else:
        print("dry-run only; no files written")
    raise SystemExit(0)

if args.repair_coverage_range:
    if table_state != (9763, 9776, 20656, 9164):
        raise SystemExit(f"unexpected post-migration table state for range repair: {table_state}")
    if (coverage_row["disposition"], coverage_row["migration_status"], coverage_row["source_line_ranges"]) != ("reviewed", "partial", "186-192"):
        raise SystemExit("p.323 coverage is not in the expected pre-repair state")
    backup = coverage_path.with_name(coverage_path.name + ".bak-s2-chp10-p323-rangefix-20261003")
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    print("p.323 coverage-range repair preview: 186-192 -> L186-192")
    if args.apply:
        shutil.copy2(coverage_path, backup)
        coverage_row["source_line_ranges"] = "L186-192"
        write_csv(coverage_path, coverage_fields, coverage)
        print(f"applied; recovery copy created: {backup.name}")
    else:
        print("dry-run only; no files written")
    raise SystemExit(0)

if table_state != (9757, 9770, 20624, 9144):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
if (coverage_row["disposition"], coverage_row["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.323 coverage is not queued/pending")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("p.323 has existing mention or statement rows")

new_candidates = []


def add_candidate(candidate_id, canonical_name, suggested_type, detail, source_line):
    if candidate_id in candidate_ids or any(row["candidate_id"] == candidate_id for row in new_candidates):
        raise SystemExit(f"candidate id already exists: {candidate_id}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": canonical_name,
        "suggested_type": suggested_type,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })
    new_candidates.append(row)


add_candidate(
    "cand-9771",
    "Pietro Longhi's genre scenes and conversational pictures described on p.323",
    "work",
    "An unnamed body of genre scenes and pictures representing conversations, meetings, love, and jealousy. The passage supplies no individual titles or locations.",
    188,
)
add_candidate(
    "cand-9772",
    "Gian Domenico Tiepolo's Via Crucis painting series at S. Polo",
    "work",
    "A series of paintings representing the Via Crucis, reported as being at S. Polo in 1749. Individual stations and present location are not specified here.",
    190,
)
add_candidate(
    "cand-9773",
    "S. Polo, place named as the location of Tiepolo's Via Crucis series",
    "place",
    "Retain the source form S. Polo; this passage does not itself resolve whether it denotes a church, parish, or other local designation.",
    190,
)
add_candidate(
    "cand-9774",
    "Unidentified early-nineteenth-century Venetian historian cited for a Longhi claim",
    "person",
    "Haskell reports an unnamed historian's claim that Longhi was punished for depicting truth. The historian is not named in the prose; note 5 cites Paoletti and qualifies the report, pending full note migration.",
    189,
)
add_candidate(
    "cand-9775",
    "Unnamed opponents who accused Carlo Goldoni of corrupting poetry and decorum",
    "",
    "The opponents are not named. Preserve the accusation as an attributed claim, not as a fact about Goldoni's conduct.",
    188,
)
add_candidate(
    "cand-9776",
    "Patrician families who admired and collected Pietro Longhi (unnamed group)",
    "",
    "Haskell describes a great number of families not associated with advanced ideas; no individual family or direct political motive is named.",
    190,
)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
source_by_line = {number: source_lines[number - 1] for number in range(186, 193)}
new_mentions = []


def add_mention(line_no, surface, candidate_id, note="", occurrence=0):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"missing candidate for mention {surface!r}: {candidate_id}")
    line = source_by_line[line_no]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r} occurrence {occurrence}")
    offset = sum(len(source_lines[index]) + 1 for index in range(185, line_no - 1))
    start = offset + starts[occurrence]
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch on L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p323-{len(new_mentions) + 1:04d}",
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


add_mention(187, "Pietro Longhi", "cand-1429", "Index candidate whose page range includes p.323.")
add_mention(188, "Goldoni", "cand-1206", "Index candidate for Carlo Goldoni, p.323.", 0)
add_mention(188, "the painter", "cand-1429", "Anaphoric reference to Pietro Longhi.")
add_mention(188, "the poet", "cand-1206", "Anaphoric reference to Carlo Goldoni.")
add_mention(188, "Longhi", "cand-1429", "", 0)
add_mention(188, "Goldoni", "cand-1206", "", 1)
add_mention(188, "Longhi", "cand-1429", "", 1)
add_mention(188, "Goldoni", "cand-1206", "", 2)
add_mention(188, "Goldoni’s", "cand-1206", "", 0)
add_mention(188, "his opponents", "cand-9775", "The antecedent is Goldoni; the accusation remains attributed.")
add_mention(188, "Longhi’s pictures", "cand-9771", "The unnamed picture group is described through conversational and playful scenes.")
add_mention(189, "Venetian historian", "cand-9774", "Unnamed in the prose; note 5 is linked for later note migration.")
add_mention(189, "his work", "cand-1429", "Anaphoric reference to Pietro Longhi.")
add_mention(190, "Pietro Longhi", "cand-1429", "")
add_mention(190, "patrician families", "cand-9776", "Unspecified collective, not individually identified.")
add_mention(190, "his break with fantasy", "cand-1429", "The possessive and break refer to Longhi.")
add_mention(190, "Lodoli", "cand-1411", "Index candidate for Padre Carlo Lodoli.")
add_mention(190, "Gian Domenico Tiepolo", "cand-2626", "Index candidate for Gian Domenico Tiepolo, p.323.")
add_mention(190, "S. Polo", "cand-9773", "Source wording retained; exact local referent remains unresolved.")
add_mention(190, "Via Crucis", "cand-9772", "Names the subject of the painting series.")
add_mention(190, "Longhi’s admirers", "cand-1220", "The next clause identifies at least one admirer as Gasparo Gozzi.")
add_mention(190, "Gasparo Gozzi", "cand-1220", "Index candidate for Gasparo Gozzi, p.323.")
add_mention(190, "Goldoni", "cand-1206", "")
add_mention(190, "his brother Carlo", "cand-1219", "Refers to Carlo Gozzi; do not infer the target of the attacks from this syntax alone.")
add_mention(190, "Longhi", "cand-1429", "", 2)
add_mention(190, "Gazzetta Veneta", "cand-8729", "Reuse the existing periodical candidate.")
add_mention(190, "Osservatore Veneto", "cand-1791", "Index candidate for the periodical, p.323.")
add_mention(190, "The Spectator", "cand-2503", "Index candidate for the English journal, p.323.")
add_mention(191, "Tiepolo", "cand-2569", "The comparison is linked to the general Giambattista Tiepolo index entry (T.csv#32, p.323); keep distinct from Gian Domenico's specific Via Crucis entry.", 0)
add_mention(191, "Longhi’s ‘imitations’", "cand-9771", "Refers to Longhi's genre pictures; OCR of the following phrase is corrected in the page-image note.")
add_mention(191, "Tiepolo’s", "cand-2569", "Index distinguishes this artistic comparison from the S. Polo Via Crucis by Gian Domenico Tiepolo.", 0)
add_mention(192, "‘Antonio’ Longhi", "cand-1429", "Footnote 5's continuation records Paoletti's misnaming of the artist; it is not treated as a second person.")

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["candidate_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")
if any(row["mention_id"] in existing_mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")

new_statements = []


def add_statement(statement_id, subject, object_id, predicate, line_start, line_end,
                  claim, quote, qualification, mentioned, speaker="Haskell",
                  text_layer="authorial claim", relation_candidate=False, extra=None):
    if statement_id in existing_statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"statement id already exists: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in p.323: {statement_id}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {statement_id}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate in {statement_id}: {subject}")
    if object_id and object_id not in all_candidate_ids:
        raise SystemExit(f"missing object candidate in {statement_id}: {object_id}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 323,
        "pdf_physical_page": 56,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


NOTE_REF = lambda start, end: [{"segment_id": NOTE_SEGMENT, "source_line_start": start, "source_line_end": end}]
add_statement(
    "st-chp10-p323-goldoni-hails-longhi-seeker-of-truth-1750", "cand-1206", "cand-1429", "hailed-as-seeking-truth",
    188, 188,
    "Haskell reports that in 1750 Goldoni hailed Pietro Longhi as a man looking for truth.",
    "it was in 1750 that Goldoni first hailed him as a ‘man who is looking for the truth’",
    "This is Haskell's account of Goldoni's praise; footnote 1 supplies the cited text and remains to be migrated from the consolidated notes segment.",
    ["cand-1206", "cand-1429"], speaker="Haskell reporting Goldoni", text_layer="reported praise",
    relation_candidate=True, extra={"cross_reference_segments": NOTE_REF(318, 318)},
)
add_statement(
    "st-chp10-p323-goldoni-theatre-reform-return-to-nature", "cand-1206", "", "sought-theatrical-reform-by-return-to-nature",
    188, 188,
    "Haskell places Goldoni's break with old masked comedies and attempt to reform theatre through a return to nature in the same period as his praise of Longhi.",
    "This was the very period when Goldoni was making his deliberate and decisive break with the old masked comedies and was trying to reform the theatre by a return to nature.",
    "The passage describes a period and an artistic program; it gives no titles for the old comedies or the reforming plays.",
    ["cand-1206"],
)
add_statement(
    "st-chp10-p323-longhi-may-have-inspired-goldoni", "cand-1429", "cand-1206", "may-have-inspired",
    188, 188,
    "Haskell suggests that the painter may have inspired Goldoni's turn toward naturalistic theatre, rather than Goldoni inspiring the painter.",
    "So it may well have been the painter who inspired the poet—Longhi had already been painting genre scenes for many years—rather than, as is usually assumed, the other way round.",
    "Both 'may well have' and the comparison with what is 'usually assumed' remain the author's qualified hypothesis, not an established influence.",
    ["cand-1429", "cand-1206", "cand-9771"], relation_candidate=True,
)
add_statement(
    "st-chp10-p323-longhi-highly-thought-of-in-advanced-circles", "cand-1429", "", "highly-regarded-in-advanced-venetian-circles",
    187, 188,
    "Haskell says Longhi was highly thought of in other advanced circles of Venetian society.",
    "For we know that Pietro Longhi was highly thought of in other advanced circles of\nVenetian society.",
    "The description concerns a social circle rather than all Venetian society; the named membership is not supplied.",
    ["cand-1429"],
)
add_statement(
    "st-chp10-p323-goldoni-praises-longhi-representation-1757", "cand-1206", "cand-1429", "praised-representation-of-human-character-and-passion",
    188, 188,
    "Haskell says Goldoni returned to the subject seven years later and praised Longhi's representation of human character and passions.",
    "Seven years later Goldoni returned to the subject and again praised Longhi for his ‘manner of representing on canvas the characters and passions of men’.2",
    "The source's relative date is retained as seven years later; footnote 2 identifies the cited dedication and remains pending in the notes segment.",
    ["cand-1206", "cand-1429"], speaker="Haskell reporting Goldoni", text_layer="reported praise",
    relation_candidate=True, extra={"cross_reference_segments": NOTE_REF(319, 319)},
)
add_statement(
    "st-chp10-p323-goldoni-sympathies-advanced-by-implication", "cand-1206", "", "sympathies-described-as-advanced",
    188, 188,
    "Haskell infers Goldoni's sympathies were advanced, at least by implication.",
    "Goldoni’s sympathies were ‘advanced’, at least by implication",
    "The phrase 'at least by implication' is essential; this is Haskell's inference rather than a direct self-description by Goldoni.",
    ["cand-1206"], speaker="Haskell", text_layer="authorial inference",
    extra={"cross_reference_segments": NOTE_REF(320, 320)},
)
add_statement(
    "st-chp10-p323-opponents-accuse-goldoni", "cand-9775", "cand-1206", "accused-of-corrupting-poetry-and-decent-behaviour",
    188, 188,
    "Haskell reports that unnamed opponents accused Goldoni of corrupting poetry and decent behaviour.",
    "he was accused by his opponents of being ‘a corrupter no less of poetry than of decent behaviour (buon costume)’.",
    "This records the opponents' accusation, not a fact about Goldoni. Footnote 4 gives a letter locator and remains pending in the consolidated notes segment.",
    ["cand-9775", "cand-1206"], speaker="Haskell reporting unnamed opponents", text_layer="reported accusation",
    relation_candidate=True, extra={"cross_reference_segments": NOTE_REF(321, 321)},
)
add_statement(
    "st-chp10-p323-longhi-pictures-interpretation-rejected", "cand-1429", "cand-9771", "pictures-could-be-read-as-socially-subversive-but-author-rejects-reading",
    188, 188,
    "Haskell asks whether Longhi's conversational pictures could be read as sharing Goldoni's implied advanced sympathies, then calls that interpretation absurd.",
    "Could Longhi’s pictures—those httle ‘conversations, meetings, playful scenes of love and jealousy’—have been interpreted in the same sense? The very idea seems absurd",
    "The question is immediately answered as absurd by Haskell. The scan reads 'little'; OCR 'htt le' is a transcription error, not a change to the source asset.",
    ["cand-1429", "cand-9771", "cand-1206"], text_layer="authorial question and evaluation",
    extra={"ocr_corrections": [{"source_line": 188, "ocr": "httle", "print": "little"}]},
)
add_statement(
    "st-chp10-p323-historian-claim-longhi-punished-for-depicting-truth", "cand-9774", "cand-1429", "claimed-punished-by-laws-for-depicting-truth",
    188, 189,
    "Haskell reports an early nineteenth-century Venetian historian's claim that Longhi was repeatedly punished for depicting truth, while explicitly noting the historian offered no supporting evidence.",
    "despite the fact that early in the nineteenth century a\nVenetian historian claimed (with no supporting evidence) that he ‘went so far in depicting the truth that he was several times punished by the laws’.5",
    "This is a reported claim expressly marked as unsupported. Footnote 5 identifies a cited source as Paoletti, says there is no evidence in the Archives of the Inquisitors, and calls the source not wholly reliable; the note is linked but its full migration remains pending.",
    ["cand-9774", "cand-1429"], speaker="Haskell reporting a historian", text_layer="reported claim",
    extra={"cross_reference_segments": NOTE_REF(322, 322)},
)
add_statement(
    "st-chp10-p323-haskell-links-longhi-praise-to-venetian-life", "cand-1429", "", "received-strongest-praise-from-observers-of-venetian-life",
    189, 189,
    "Haskell says the strongest praise of Longhi's work came from men who sought a steadier view of actual Venetian life.",
    "the most enthusiastic praise of his work should have come from men who were anxious to look more steadily at the actual circumstances of Venetian Use than was usual at the time.",
    "The OCR reads 'Use'; the scan reads 'life'. Haskell's comparative assessment is retained as authorial interpretation.",
    ["cand-1429"], extra={"ocr_corrections": [{"source_line": 189, "ocr": "Use", "print": "life"}]},
)
add_statement(
    "st-chp10-p323-longhi-admired-and-collected-by-patrician-families", "cand-1429", "cand-9776", "admired-and-collected-by",
    190, 190,
    "Haskell says a great number of patrician families not associated with advanced ideas admired and collected Pietro Longhi.",
    "Pietro Longhi was certainly admired and collected by a great number of patrician families in no way associated with advanced ideas",
    "'A great number' is not quantified; no family names are supplied. Preserve Haskell's contrast with the advanced circles discussed earlier.",
    ["cand-1429", "cand-9776"], relation_candidate=True,
)
add_statement(
    "st-chp10-p323-longhi-break-with-fantasy-mostly-not-political", "cand-1429", "", "break-with-fantasy-not-seen-as-directly-political",
    190, 190,
    "Haskell says most people would not have connected Longhi's break with fantasy to direct political motives.",
    "in most people’s eyes his break with fantasy can have had no connection with directly political motives.",
    "The wording 'in most people's eyes' and modal 'can have had' are retained; this is not stated as Longhi's own motive.",
    ["cand-1429"],
)
add_statement(
    "st-chp10-p323-lodoli-ideas-indirect-impact-on-arts", "cand-1411", "", "ideas-made-at-least-indirect-impact",
    190, 190,
    "Haskell places Lodoli's ideas within a mid-eighteenth-century attack on the irrational in the arts and says their impact was at least indirect.",
    "By the middle of the eighteenth century the irrational in all the arts was coming under attack, and the ideas of men like Lodoli were making at least an indirect impact.",
    "The date is approximate and 'at least an indirect impact' is not upgraded to direct influence on a named person or work.",
    ["cand-1411"],
)
add_statement(
    "st-chp10-p323-tiepolo-via-crucis-criticized-for-costumes", "cand-9772", "", "met-with-strong-criticism-for-costumes",
    190, 190,
    "Haskell reports that Gian Domenico Tiepolo's Via Crucis series at S. Polo met with criticism in 1749 because its figures wore varying costumes and were said to look caricatural or out of period.",
    "Thus we hear that in 1749 Gian Domenico Tiepolo’s series of paintings in S. Polo representing the Via Crucis met with strong criticism-because ‘all the figures were wearing different costume—some Spanish, some Slav and some are just caricatures. And people say that in those days that sort of person was not found and that he has painted them in that way only out of personal whim.’6",
    "'Thus we hear' frames this as a report, and the costume criticism is quoted speech, not an independently verified assessment. The printed page has 'criticism because'; the OCR hyphen is removed only in this reading note.",
    ["cand-9772", "cand-2626", "cand-9773"], speaker="Haskell reporting contemporary criticism", text_layer="reported criticism",
    extra={"ocr_corrections": [{"source_line": 190, "ocr": "criticism-because", "print": "criticism because"}], "cross_reference_segments": NOTE_REF(323, 323)},
)
add_statement(
    "st-chp10-p323-gozzi-admires-longhi-rejection-of-fantasy", "cand-1220", "cand-1429", "admired-for-rejecting-fantasy",
    190, 190,
    "Haskell identifies Gasparo Gozzi as at least one admirer who valued Longhi for rejecting the kind of historical or imaginary costume just criticized.",
    "One at least of Longhi’s admirers made it quite clear that he liked him just because of his rejection of this sort of thing.",
    "The next sentence identifies the admirer as Gasparo Gozzi; the source does not say all admirers shared this view.",
    ["cand-1220", "cand-1429", "cand-9772"], relation_candidate=True,
)
add_statement(
    "st-chp10-p323-gozzi-defender-of-goldoni", "cand-1220", "cand-1206", "strong-defender-of",
    190, 190,
    "Haskell describes Gasparo Gozzi as a strong defender of Carlo Goldoni.",
    "Gasparo Gozzi, who was also a strong defender of Goldoni, despite the attacks of his brother Carlo",
    "The quoted syntax does not make clear whether Carlo Gozzi's attacks targeted Goldoni or Gasparo; no attack edge is asserted here.",
    ["cand-1220", "cand-1206", "cand-1219"], relation_candidate=True,
)
add_statement(
    "st-chp10-p323-gozzi-writes-about-longhi-in-periodicals", "cand-1220", "cand-1429", "wrote-about-in-periodicals",
    190, 190,
    "Haskell says Gasparo Gozzi wrote about Longhi twice in Gazzetta Veneta and Osservatore Veneto.",
    "twice wrote about Longhi in the Gazzetta Veneta and the Osservatore Veneto",
    "The periodicals are named, but this sentence does not date both pieces individually; the August 1760 reference follows on the next line.",
    ["cand-1220", "cand-1429", "cand-8729", "cand-1791"], relation_candidate=True,
)
add_statement(
    "st-chp10-p323-gozzi-edits-osservatore-along-spectator-lines", "cand-1220", "cand-1791", "edited-on-lines-of",
    190, 190,
    "The relative clause says Gozzi edited Osservatore Veneto on the lines of English journals such as The Spectator.",
    "the Osservatore Veneto which he edited on the lines of English journals such as The Spectator",
    "Grammatically 'which he edited' directly follows Osservatore Veneto; do not extend the editorial claim to Gazzetta Veneta from this sentence alone.",
    ["cand-1220", "cand-1791", "cand-2503"], relation_candidate=True,
)
add_statement(
    "st-chp10-p323-gozzi-compares-longhi-and-tiepolo", "cand-1220", "cand-2569", "compared-longhi-with-tiepolo",
    190, 191,
    "Haskell says Gozzi compared Longhi with Giambattista Tiepolo on both occasions and, in August 1760, judged Longhi's imitations of observed life no less perfect than Tiepolo's imaginative scenes.",
    "On both occasions he compared him to\nTiepolo. In August 1760 he reaches the conclusion that Longhi’s ‘imitations’ of the Efe he see around him are ‘no less perfect’ than Tiepolo’s great scenes of the imagination.7",
    "The prose gives only the surname Tiepolo. The book index places Giambattista Tiepolo in its general entry T.csv#32 at p.323, while T.csv#89 specifically identifies Gian Domenico's S. Polo Via Crucis at p.323; the artistic comparison is mapped to Giambattista and kept distinct from that Via Crucis claim. The OCR phrase 'Efe he see' is 'life he sees' on the scan; 'no less perfect' is a comparison of artistic merit, not an influence claim.",
    ["cand-1220", "cand-1429", "cand-2569", "cand-9771"], speaker="Haskell reporting Gasparo Gozzi", text_layer="reported critical comparison",
    relation_candidate=True, extra={"ocr_corrections": [{"source_line": 191, "ocr": "Efe he see", "print": "life he sees"}], "cross_reference_segments": NOTE_REF(324, 324)},
)
add_statement(
    "st-chp10-p323-note5-paoletti-misnaming-and-reliability", "cand-9774", "cand-1429", "cited-source-misnames-artist-and-is-qualified-as-unreliable",
    192, 192,
    "In the continuation of note 5, Haskell says the cited account calls the artist 'Antonio' Longhi and does not seem wholly reliable.",
    "who calls the artist ‘Antonio’ Longhi, does not seem wholly reliable.",
    "This is a note fragment whose antecedent and citation begin at consolidated note line 322. The page image confirms the printed note number is 5; the OCR note block labels it 6. Do not create a separate Antonio Longhi identity.",
    ["cand-9774", "cand-1429"], speaker="Haskell", text_layer="footnote reliability qualification",
    extra={"cross_reference_segments": NOTE_REF(322, 322), "ocr_corrections": [{"note_source_line": 322, "ocr_note_number": 6, "print_note_number": 5}]},
)

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate id")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")
all_ids = {row["candidate_id"] for row in candidate_rows}
if any(row["candidate_id"] not in all_ids for row in new_mentions):
    raise SystemExit("missing mention candidate foreign key")
if any(cid not in all_ids for row in new_statements for cid in row["qualifiers"]["mentioned_candidate_ids"]):
    raise SystemExit("missing statement candidate reference")
for row in new_statements:
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in all_ids:
        raise SystemExit(f"missing statement subject: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in all_ids:
        raise SystemExit(f"missing statement object: {row['statement_id']}")

coverage_row.update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L186-192",
    "note": "Printed p.323 body reviewed against CHP-10.pdf physical page 56. Body claims, comparison, report attribution, and page-specific OCR corrections are migrated. L192 is the closing fragment of footnote 5 and is captured with a cross-reference to canonical note L322; full footnotes 1-7 at L318-324 remain pending, so coverage stays partial.",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
print(f"p.323 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: reviewed/partial; footnotes 1-7 remain pending in the canonical notes segment")
print(f"totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = []
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
    backups.append(backup)
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
