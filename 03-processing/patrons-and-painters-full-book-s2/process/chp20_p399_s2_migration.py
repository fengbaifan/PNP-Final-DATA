#!/usr/bin/env python3
"""Controlled S2 migration for printed p.399 and closure of p.398's open assessment."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
EXPECTED_SOURCE = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
EXPECTED_PDF = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P398 = "chp-20:20_CHP-20Postscript:l26-36"
P399 = "chp-20:20_CHP-20Postscript:l38-44"
P400 = "chp-20:20_CHP-20Postscript:l46-57"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
CHP3_LANCKORONSKA = "chp-3:03_CHP-3_sec_iv:l189-243"
OPEN_398 = "st-chp20-p398-haskell-farnese-evaluation-open"
CLOSE_399 = "st-chp20-p399-hibbard-jesuit-control"
BACKUP_SUFFIX = ".bak-s2-chp20-p399-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


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


for path, expected in ((SOURCE, EXPECTED_SOURCE), (PDF, EXPECTED_PDF)):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)} ({actual})")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(x) for x in statement_path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
coverage_fields, coverage = read_csv(coverage_path)
segments = [json.loads(x) for x in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if x.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
statement_by_id = {row["statement_id"]: row for row in statements}

for sid in (P398, P399, P400, NOTES, CHP3_LANCKORONSKA):
    if sid not in segment_by_id:
        raise SystemExit(f"missing registered segment: {sid}")
if (coverage_by_id[P398]["disposition"], coverage_by_id[P398]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.398 must be reviewed/partial before closure")
if (coverage_by_id[P399]["disposition"], coverage_by_id[P399]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.399 should be queued/pending: {coverage_by_id[P399]}")
if segment_by_id[P399]["sha256"] != "38b28c432e7d2451ab366543fb1f16f675b2e391192879bc0f160b4f9662b1d7":
    raise SystemExit("registered p.399 S0 hash changed")
if segment_by_id[P399]["asset_sha256"] != EXPECTED_SOURCE:
    raise SystemExit("p.399 source asset hash is inconsistent")
if coverage_by_id[P400]["disposition"] != "queued" or coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("next body or footnote segment is not queued")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text399 = "\n".join(source_lines[segment_by_id[P399]["line_start"] - 1 : segment_by_id[P399]["line_end"]])
if hashlib.sha256(text399.encode("utf-8")).hexdigest() != segment_by_id[P399]["sha256"]:
    raise SystemExit("p.399 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment_by_id[P399]["line_start"], segment_by_id[P399]["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    ("cand-10920", "Thomas Buser", "person", 40,
     "Named as the author of a 1976 article on Jesuit art; identity is left for S3 alignment."),
    ("cand-10921", "Thomas Buser’s 1976 article on Jesuit art and the Nadal engravings (title unspecified)", "archive", 40,
     "Footnote 1 cites Buser without a title or page locator; the article was not independently consulted."),
    ("cand-10922", "Book of gospel meditations by Jerome Nadal (title and edition unspecified)", "archive", 40,
     "Haskell says its engravings were commissioned by St Ignatius; no title, edition, or publication details are supplied here."),
    ("cand-10923", "Engravings in Jerome Nadal’s book of gospel meditations (set unspecified)", "work", 40,
     "Buser is reported to discuss their didactic intent and format; exact compositions and count are not supplied."),
    ("cand-10924", "Church of S. Stefano Rotondo (Rome)", "place", 41,
     "Named as the Jesuit church containing Circignani’s martyrdom frescoes."),
    ("cand-10925", "Church of S. Vitale (Rome; distinct from the Venetian church)", "place", 42,
     "The context places the church among Roman Jesuit art sites; keep distinct from the S. Vitale in Venice candidate."),
    ("cand-10926", "Powerful patrons in Haskell’s account of Jesuit church decoration (individuals unspecified)", "term", 42,
     "A role-based group in Haskell’s retrospective account; no individual patron is named here."),
    ("cand-10927", "Howard Hibbard’s paper on Jesuit control of Gesù chapel programmes (title unspecified)", "archive", 39,
     "Haskell calls it a persuasive paper; its title and publication details are not supplied on this page."),
    ("cand-10928", "Robert Enggass", "person", 43,
     "Named as author of a monograph on Gaulli; identity is left for S3 alignment."),
    ("cand-10929", "Robert Enggass’s monograph on Giovanni Battista Gaulli (1964; title unspecified)", "archive", 43,
     "Footnote 2 cites Enggass 1964; the monograph is not independently consulted in this S2 passage."),
    ("cand-10930", "Church Triumphant as an interpretive context for the Gesù frescoes", "term", 43,
     "Haskell reports Enggass’s framing of the fresco iconography within this general theological context."),
    ("cand-10931", "Irving Lavin’s 1972 article on Bernini and the Jesuits (title unspecified)", "archive", 43,
     "Footnote 3 cites Lavin, 1972, pages 169–171; the article is not independently consulted here."),
    ("cand-10932", "Lanckorońska (historian cited for an interpretation of the Gesù frescoes; identity unresolved)", "person", 43,
     "Named by surname in the passage; reuse the prior cited-publication candidate separately and leave identity alignment to S3."),
    ("cand-10933", "Jesuit art as a disputed historical category in Haskell’s account", "term", 40,
     "Buser is said to challenge Haskell’s earlier scepticism about the reality of Jesuit art; this is a historiographical issue, not a settled taxonomy."),
]

existing_keys = {(row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()) for row in candidates}
for cid, name, kind, line_number, detail in candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P399}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-3806", "Howard Hibbard", 39, 39, "Reuse the existing person candidate; closes the p.398 Haskell transition.", 0),
    ("cand-10927", "paper", 39, 39, "The p.398 phrase ‘a persuasive’ continues with this word on p.399; the paper’s title and publication are not identified.", 0),
    ("cand-3403", "the Jesuits", 39, 39, "Reuse the typed Jesuit institution candidate.", 0),
    ("cand-5200", "the Gesù", 39, 39, "Reuse the Church of the Gesù place candidate.", 0),
    ("cand-5002", "the chapels", 39, 39, "Reuse the side-chapels place group at the Gesù.", 0),
    ("cand-3403", "Jesuit decorators", 39, 39, "Collective decorators acting in the Jesuit church context.", 0),
    ("cand-3403", "Jesuit intermediaries", 39, 39, "Collective intermediaries in payments to artists.", 0),
    ("cand-10926", "private-patrons", 39, 39, "OCR preserves the printed hyphen; private patrons funded chapel painting in Hibbard’s quoted account.", 0),
    ("cand-10926", "The patrons", 39, 39, "Role-based patrons with limited say over programme and artist choice.", 0),
    ("cand-10920", "Thomas Buser", 40, 40, "New person candidate named on p.399.", 0),
    ("cand-10921", "an interesting article by Thomas Buser", 40, 40, "Footnote 1 supplies Buser as the cited author; title unspecified.", 0),
    ("cand-10933", "the reality of ‘Jesuit art’", 40, 40, "Historiographical category whose reality Buser is said to affirm against Haskell’s prior scepticism.", 0),
    ("cand-10923", "the engravings", 40, 40, "Engravings in Nadal’s gospel-meditation book.", 0),
    ("cand-10922", "a book of gospel meditations by the Jesuit Jerome Nadal", 40, 40, "Book identified by genre and author; title and edition are unspecified.", 0),
    ("cand-1721", "Jerome Nadal", 40, 40, "Reuse the indexed person candidate.", 0),
    ("cand-1309", "St Ignatius himself", 40, 40, "Reuse the indexed St Ignatius candidate; Haskell reports a commissioning role.", 0),
    ("cand-5002", "one of the chapels of the Gesù", 40, 40, "Reuse the Gesù side-chapels group; the specific chapel is unnamed.", 0),
    ("cand-3806", "Hibbard", 40, 40, "Reuse Howard Hibbard; Haskell says he had already noted the chapel influence.", 0),
    ("cand-5019", "the horrific scenes of martyrdom", 40, 41, "Reuse the S. Stefano Rotondo martyrdom fresco-cycle candidate.", 0),
    ("cand-1970", "Circignani", 40, 41, "Reuse Niccolò Circignani dalle Pomarance candidate.", 0),
    ("cand-10924", "the Jesuit church of S. Stefano Rotondo", 41, 41, "New place candidate for the Roman church.", 0),
    ("cand-10918", "and elsewhere", 41, 41, "Other Jesuit churches are not identified; reuse only as a collective spatial reference.", 0),
    ("cand-10920", "Buser has some valuable comments", 41, 41, "Coreference to Thomas Buser.", 0),
    ("cand-5019", "these frescoes", 41, 41, "Coreference to Circignani’s S. Stefano Rotondo martyrdom cycle.", 0),
    ("cand-10925", "the church of S. Vitale", 42, 42, "New place candidate for the Roman church; distinguish from Venice.", 0),
    ("cand-5022", "‘pastoral’ episodes of torture depicted in the church of S. Vitale", 42, 42, "Reuse the existing S. Vitale fresco-cycle candidate; retain Haskell’s unusual ‘pastoral’ characterization.", 0),
    ("cand-10920", "he suggests", 42, 42, "Coreference to Buser; the proposed style choice is explicitly tentative.", 0),
    ("cand-10926", "powerful patrons", 42, 42, "Role-based patrons in Haskell’s earlier account; no individuals are identified.", 0),
    ("cand-9423", "I have always emphasised", 42, 42, "Reuse the Francis Haskell person candidate as the speaker of his earlier position.", 0),
    ("cand-10933", "a truly Jesuit style", 42, 42, "Haskell’s historiographical formulation, not an independently established category.", 0),
    ("cand-10920", "Buser referring", 42, 42, "Coreference to Thomas Buser in Haskell’s statement of puzzlement.", 0),
    ("cand-1117", "Gaulli’s frescoes in the Gesù", 43, 43, "Reuse the indexed Giovanni Battista Gaulli candidate and the existing Gesù fresco group below.", 0),
    ("cand-6445", "the content of the frescoes", 43, 43, "Reuse the broader Gaulli Gesù frescoes candidate; no exact cycle is identified.", 0),
    ("cand-10928", "Robert Enggass", 43, 43, "New person candidate; his identity will be aligned globally at S3.", 0),
    ("cand-10929", "important monograph on the artist", 43, 43, "Footnote 2 identifies Enggass, 1964; title unspecified.", 0),
    ("cand-10930", "the general context of the ‘church triumphant’", 43, 43, "Interpretive framework attributed to Enggass by Haskell.", 0),
    ("cand-10932", "Lanckoronska", 43, 43, "New person candidate for the named scholar; reuse her prior publication separately.", 0),
    ("cand-5473", "Lanckoronska’s theory", 43, 43, "Reuse the previously registered 1935 cited-publication candidate.", 0),
    ("cand-9423", "I infer from his silence", 43, 43, "Haskell explicitly marks the claim about Enggass’s view as his inference.", 0),
    ("cand-10931", "an important article partly concerned with Bernini’s relationship to the Jesuits", 43, 43, "Footnote 3 identifies Lavin’s 1972 article; title unspecified.", 0),
    ("cand-10859", "Lavin", 43, 43, "Reuse Irving Lavin from p.396; the specific 1972 article is distinct from his 1968 publication.", 0),
    ("cand-0295", "Bernini", 43, 43, "Reuse the existing Bernini person candidate.", 0),
    ("cand-5478", "the drawings by Gaulli", 43, 43, "Reuse the earlier drawing-group candidate discussed in chapter 3 notes.", 0),
    ("cand-5476", "Berlin", 43, 43, "Reuse the location candidate for one cited Blood of Christ drawing.", 0),
    ("cand-5477", "Dusseldorf", 43, 43, "Reuse the location candidate for the other cited Blood of Christ drawing; printed form has ü.", 0),
    ("cand-5256", "Bernini’s composition of the Sangue dt Cristo", 43, 43, "Reuse the existing Bernini drawing candidate; preserve the OCR surface and record the print correction to ‘di’ on the statement.", 0),
    ("cand-5254", "the Sangue dt Cristo", 43, 43, "Reuse the iconographic-theme candidate; preserve the OCR surface and record the print correction to ‘di’ on the statement.", 0),
    ("cand-5258", "an alternative—and rejected— design for the dome of the Gesù", 43, 43, "Reuse Gaulli’s earlier proposed Gesù dome-theme drawings; preserve the OCR spacing and retain the rejection as stated.", 0),
    ("cand-5265", "Quietism", 44, 44, "Reuse the Quietism concept while marking Haskell’s earlier causal suggestion as withdrawn.", 0),
]

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first, last, note, occurrence) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p399-{ordinal:03d}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention target missing or not open: {cid}")
    lower = line_offset[first]
    upper = line_offset[last] + len(source_lines[last - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text399.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(f"surface not found on p.399 lines {first}-{last}: {surface!r}")
        cursor = found + 1
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P399, "candidate_id": cid,
        "surface_form": surface, "start_char": str(found),
        "end_char": str(found + len(surface)), "note": note,
    })
    existing_mention_ids.add(mention_id)

intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
                   for row in [*mentions, *new_mentions] if row["segment_id"] == P399)
for index, left in enumerate(intervals):
    for right in intervals[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing p.399 mention spans: {left[2]} / {right[2]}")


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer,
                   qualification, candidate_ids, relation=False, footnote_marker=None, extra=None):
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": 399, "pdf_physical_page": 4,
        "claim": claim, "speaker": speaker, "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation,
    }
    if footnote_marker is not None:
        note_line = 225
        qualifiers.update({
            "footnote_marker": footnote_marker,
            "footnote_text_pending": True,
            "footnote_segment": NOTES,
            "footnote_refs": [{"marker": footnote_marker, "segment_id": NOTES, "source_line": note_line}],
            "footnote_statement_ids": [],
            "footnote_body_link_status": "pending",
        })
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id, "segment_id": P399,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[first - 1:last]),
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement(CLOSE_399, 39, 39, "cand-9423", "cand-10927",
        "haskell_reported_hibbards_correction_on_jesuit_control_of_church_programme",
        "Haskell introduces a persuasive paper by Howard Hibbard, who argued that Jesuits controlled the Gesù’s ornamental and iconographic programme more than Haskell had allowed for: chapel dedications were set at transfer, Jesuit decorators remained in charge, and payments passed through Jesuit intermediaries, while patrons retained some limited say over programme and artist choice.",
        "Haskell reporting Hibbard", "source-attributed historical interpretation",
        "This closes Haskell’s p.398 open assessment. Hibbard’s paper and underlying documents are not independently consulted; the passage distinguishes patron funding and artist choice from Jesuit control of chapel dedication and iconographic coherence.",
        ["cand-9423", "cand-3806", "cand-10927", "cand-3403", "cand-5200", "cand-5002", "cand-10926"],
        relation=True, extra={"cross_reference_segments": [{"segment_id": P398, "source_line_start": 36, "source_line_end": 36}],
            "closes_statement_ids": [OPEN_398], "cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p399-buser-challenges-jesuit-art-scepticism", 40, 40, "cand-10920", "cand-10921",
        "buser_article_challenged_haskells_scepticism_about_jesuit_art",
        "Haskell says Thomas Buser’s 1976 article challenged his scepticism about the reality of Jesuit art.",
        "Haskell reporting Buser", "historiographical revision",
        "The article is cited but not independently consulted; ‘Jesuit art’ is recorded as the debate’s category, not an endorsed fixed style.",
        ["cand-10920", "cand-10921", "cand-10933"], relation=False, footnote_marker=1,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p399-nadal-engravings-commission-and-influence", 40, 41, "cand-1309", "cand-10922",
        "st_ignatius_commissioned_nadal_meditation_book_whose_engravings_influenced_jesuit_art",
        "Haskell says the gospel-meditation book by Jerome Nadal was commissioned by St Ignatius. Buser discussed the engravings’ influence on a Gesù chapel and, in didactic intent and format but not actual compositions, on Circignani’s martyrdom scenes at S. Stefano Rotondo and elsewhere.",
        "Haskell reporting Buser and Hibbard", "source-reported commission and qualified visual influence",
        "The book’s title and edition are not supplied. Preserve the explicit limit: influence concerns didactic intent and format, not the engravings’ actual compositions. The book and article were not independently consulted.",
        ["cand-1309", "cand-1721", "cand-10922", "cand-10923", "cand-3403", "cand-5002", "cand-3806", "cand-1970", "cand-5019", "cand-10924", "cand-10918"],
        relation=True, footnote_marker=1,
        extra={"cited_material_not_independently_consulted": True,
            "cross_reference_segments": [{"segment_id": CHP3_LANCKORONSKA, "source_line_start": 189, "source_line_end": 243}]}),
    make_statement("st-chp20-p399-buser-s-vitale-frescoes", 41, 42, "cand-10920", "cand-5022",
        "buser_discussed_s_vitale_torture_frescoes_and_suggested_an_antique_style_choice",
        "Haskell says Buser commented on Circignani’s martyrdom frescoes and on ‘pastoral’ torture episodes in S. Vitale. Buser suggested that the latter’s style may have been chosen, under the influence of Roman wall painting, to give the early Christian victims’ suffering an antique feeling.",
        "Haskell reporting Buser", "attributed interpretation with explicit uncertainty",
        "The style explanation is Buser’s suggestion as reported by Haskell, not a settled commission fact; distinguish this Roman S. Vitale from the Venetian church. The cited article was not consulted.",
        ["cand-10920", "cand-10921", "cand-5022", "cand-10925", "cand-5019", "cand-1970"],
        relation=True, footnote_marker=1,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p399-haskell-jesuit-art-and-patron-tension", 42, 42, "cand-9423", "cand-10926",
        "haskell_contrasted_his_jesuit_martyrdom_style_claim_with_patron_constraints",
        "Haskell recalls his view that martyrdom scenes first brought a truly Jesuit style into being, then says he was puzzled that Buser cited his separate argument that Jesuits elsewhere were often forced by political or economic weakness to accept what powerful patrons provided.",
        "Haskell reflecting on his earlier argument and Buser’s reading", "authorial comparison and unresolved historiographical tension",
        "This records a tension between two claims and does not resolve whether it is contradiction, different contexts, or a difference in the art discussed.",
        ["cand-9423", "cand-10920", "cand-10921", "cand-10933", "cand-3403", "cand-5019", "cand-10926"], relation=True,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p399-enggass-monograph-and-fresco-content", 43, 43, "cand-10928", "cand-10929",
        "enggass_monograph_provided_a_fuller_account_of_gaullis_gesu_frescoes",
        "Haskell says Robert Enggass’s monograph on Gaulli supplemented and sometimes corrected his account; Enggass’s study of the frescoes’ content was more complete and treated their iconography within the Church Triumphant context rather than Haskell’s specific theological issues.",
        "Haskell reporting and evaluating Enggass", "authorial comparison of scholarship",
        "Footnote 2 cites Enggass 1964; the monograph is not independently consulted. ‘Church Triumphant’ is Enggass’s reported interpretive frame, not a full account of the fresco programme.",
        ["cand-10928", "cand-10929", "cand-1117", "cand-6445", "cand-10930"], relation=True, footnote_marker=2,
        extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p399-haskell-concedes-enggass-theological-relevance", 43, 43, "cand-9423", "cand-10928",
        "haskell_inferred_enggass_considered_specific_theological_issues_irrelevant_and_conceded_this_was_right",
        "Haskell infers from Enggass’s silence that he considered the specific theological issues largely irrelevant, and explicitly says Enggass was right in this attitude.",
        "Haskell", "authorial inference and revision",
        "The claim about Enggass’s view is explicitly an inference from silence, not a direct statement by Enggass. Haskell’s concession is preserved as his own later judgment.",
        ["cand-9423", "cand-10928", "cand-10929", "cand-6445"], relation=False, footnote_marker=2),
    make_statement("st-chp20-p399-lavin-rejects-lanckoronska-dome-drawing-theory", 43, 43, "cand-10859", "cand-5478",
        "lavin_confirmed_rejection_of_lanckoronskas_gaulli_drawing_alternative_gesu_dome_theory",
        "Haskell says Irving Lavin’s article partly on Bernini and the Jesuits confirmed recent historians’ rejection of Lanckoronska’s theory that Gaulli’s Blood of Christ drawings in Berlin and Düsseldorf were for an alternative, rejected design for the Gesù dome.",
        "Haskell reporting Lavin and recent historians", "source-attributed correction of an earlier iconographic attribution",
        "The drawings, publication, and relevant collections were not independently consulted in this passage. Reuse the previously registered drawings, locations, Bernini composition, and proposed dome-design candidates; do not conflate them with Gaulli’s final Duplex Intercessio scheme.",
        ["cand-10859", "cand-10931", "cand-10932", "cand-5473", "cand-1117", "cand-5478", "cand-5476", "cand-5477", "cand-5254", "cand-5256", "cand-5258", "cand-5218"],
        relation=True, footnote_marker=3,
        extra={"cited_material_not_independently_consulted": True,
            "cross_reference_segments": [{"segment_id": CHP3_LANCKORONSKA, "source_line_start": 189, "source_line_end": 243}],
            "ocr_corrections": [
                {"source_line": 43, "ocr": "osan important", "print": "of an important", "basis": "CHP-20Postscript.pdf physical page 4"},
                {"source_line": 43, "ocr": "Dusseldorf", "print": "Düsseldorf", "basis": "CHP-20Postscript.pdf physical page 4"},
                {"source_line": 43, "ocr": "Sangue dt Cristo", "print": "Sangue di Cristo", "basis": "CHP-20Postscript.pdf physical page 4"},
            ]}),
    make_statement("st-chp20-p399-haskell-retracts-quietism-explanation", 43, 44, "cand-9423", "cand-5265",
        "haskell_withdrew_his_suggestion_jesuits_rejected_the_blood_of_christ_theme_due_to_quietism",
        "Haskell says he had been wrong to propose that the Jesuits might have rejected the Blood of Christ theme because of its possible association with Quietism.",
        "Haskell", "explicit authorial correction of an earlier hypothesis",
        "This is a retraction of a tentative causal explanation, not a claim that the theme was in fact rejected for another known reason.",
        ["cand-9423", "cand-5254", "cand-5265", "cand-3403"], relation=False,
        extra={"cross_reference_segments": [{"segment_id": CHP3_LANCKORONSKA, "source_line_start": 189, "source_line_end": 243}],
            "cross_reference_statement_ids": ["st-chp3-seciv-notes-l189-204-p82-n3-drawings-held-in-berlin-and-dusseldorf", "st-chp3-seciv-notes-l189-204-p82-n3-lanckoronska", "st-chp3-seciv-notes-l205-243-p83-n2-lanckoronska", "st-chp3-seciv-notes-l205-243-p84-n1-lanckoronska"]}),
]

if OPEN_398 not in statement_by_id:
    raise SystemExit(f"missing open p.398 statement: {OPEN_398}")
open_statement = statement_by_id[OPEN_398]
open_qualifiers = open_statement.get("qualifiers", {})
if not open_qualifiers.get("open_across_segment"):
    raise SystemExit("p.398 Haskell assessment is not marked open")
if CLOSE_399 in statement_by_id:
    raise SystemExit(f"closure statement already exists: {CLOSE_399}")

statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    sid = row["statement_id"]
    if sid in statement_ids:
        raise SystemExit(f"statement ID already exists: {sid}")
    statement_ids.add(sid)
    if row["original_quote"] not in text399:
        raise SystemExit(f"statement quote not contained in p.399 segment: {sid}")
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {cid}")
    for ref in row["qualifiers"].get("cross_reference_segments", []):
        ref_id = ref if isinstance(ref, str) else ref.get("segment_id")
        if ref_id not in segment_by_id:
            raise SystemExit(f"statement references missing segment {ref_id}")

open_qualifiers["open_across_segment"] = False
open_qualifiers["closed_by_segment"] = P399
open_qualifiers["closed_by_statement_id"] = CLOSE_399
open_qualifiers["cross_page_quote_continuation"] = (
    "paper, Howard Hibbard pointed out that though the Jesuits were not interested in stylistic uniformity they did, even at an early stage in the history of the Gesù, control the ornamental and iconographic programme far more than I had allowed for"
)
open_qualifiers["qualification"] = (
    "The p.398 opening is completed on p.399 with Haskell’s account of Hibbard’s argument that Jesuits controlled chapel dedication, decoration, and iconographic coherence more than Haskell had allowed, "
    "while patrons retained some limited choice. Hibbard’s paper and underlying documents were not independently consulted."
)
open_statement["predicate"] = "haskell_hibbard_intervention_on_jesuit_control_closed"
mentions.extend(new_mentions)
statements.extend(new_statements)

coverage_by_id[P398]["migration_status"] = "complete"
coverage_by_id[P398]["note"] = coverage_by_id[P398]["note"] + " Haskell’s open assessment was closed against p.399 statement `" + CLOSE_399 + "`."
coverage_by_id[P399]["disposition"] = "reviewed"
coverage_by_id[P399]["migration_status"] = "complete"
coverage_by_id[P399]["source_line_ranges"] = "L39-44"
coverage_by_id[P399]["note"] = (
    "Printed p.399 (PDF physical page 4) read against the page image. Closes p.398’s Hibbard transition; processes Hibbard, Buser/Nadal, "
    "Circignani, S. Vitale, Enggass, and Lavin’s correction of the earlier Gaulli-drawing theory. The text explicitly retracts the Quietism explanation. "
    "Cited works remain unconsulted; footnotes are linked to the queued notes segment. Page-image OCR corrections are recorded on statements."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.399 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print(f"closed p.398 statement {OPEN_398} using {CLOSE_399}")
    print("p.399 segment is complete; its footnote block remains queued as a separate segment")
