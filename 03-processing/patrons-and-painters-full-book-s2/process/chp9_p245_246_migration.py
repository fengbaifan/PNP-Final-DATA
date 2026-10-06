"""Controlled S2 migration for Chapter 9, printed pages 245-246.

Default invocation is a read-only dry run. It does not edit OCR source files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-9.pdf"
P245 = "chp-9:09_CHP-9_intro:l7-16"
P246 = "chp-9:09_CHP-9_intro:l18-25"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
TARGETS = {P245, P246}
BACKUP_SUFFIX = ".bak-s2-chp9-p245-246-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGETS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
if segment_by_id[P245]["source_file"] != segment_by_id[P246]["source_file"]:
    raise SystemExit("page segments no longer share one source file")
for segment_id in TARGETS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")
if not SOURCE.is_file() or not PDF.is_file() or not (PROCESS / "p245_page_review.png").is_file() or not (PROCESS / "p246_page_review.png").is_file():
    raise SystemExit("source OCR, chapter PDF, or page-review image is missing")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line_offsets = {}
for segment_id in TARGETS:
    meta = segment_by_id[segment_id]
    selected = source_lines[meta["line_start"] - 1 : meta["line_end"]]
    if hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), selected):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
expected = {
    P245: ("queued", "pending", ""),
    P246: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-8105", "Venetian government and State in Haskell's eighteenth-century account", "institution", P245, 13,
     "The governing political entity acting in the passage; keep distinct from the city of Venice and defer alignment with other Republic of Venice candidates to S3."),
    ("cand-8106", "International tourism to Venice in the eighteenth century", "term", P245, 13,
     "Tourism is described as a major cosmopolitan activity encouraged by the Venetian government; no specific institution or tour is named."),
    ("cand-8107", "Enlightenment as a general intellectual force named in the Venetian account", "term", P245, 13,
     "Haskell uses the general term Enlightenment for forces changing ideas; do not infer a local organization or specific intellectual circle."),
    ("cand-8108", "Venetian nobility as a social estate", "term", P245, 13,
     "Collective social estate named by Haskell; individual nobles are not enumerated in this passage."),
    ("cand-8109", "Venetian patricians subject to restrictions on foreign travel", "term", P245, 14,
     "Legal/social class named as the subject of the travel restriction; keep distinct from the broader nobility until semantic alignment is reviewed."),
    ("cand-8110", "Council of Ten", "institution", P245, 14,
     "Venetian governing body named as the authority whose special permission was required for patricians to travel abroad."),
    ("cand-8111", "Venetian law restricting patrician travel abroad (passed 1709; revived 1783)", "procedure", P245, 14,
     "Legal restriction described by Haskell; this record preserves the passage's dates and scope without adding an independently verified law title."),
    ("cand-8112", "Political unorthodoxy in eighteenth-century Venice", "term", P245, 13,
     "Concept named as a basis for prosecutions; no individual case is identified in the body passage."),
    ("cand-8113", "Prosecutions for political unorthodoxy in Venice", "procedure", P245, 13,
     "Threat of prosecution described by Haskell; no case or accused person is named in the body passage."),
    ("cand-8114", "Sciences as a field of study in the Venetian political debate", "term", P245, 14,
     "Haskell reports an allegation that the government discouraged the sciences; the passage explicitly says there is no direct evidence."),
    ("cand-8115", "French travellers commenting on Venetian policy (unnamed collective)", "term", P245, 14,
     "Collective group whose suggestion about government policy is reported; no travellers are named here."),
    ("cand-8116", "Molmenti 1919 publication cited for the origins of the Venetian travel law", "archive", P245, 15,
     "Bibliographic reference as transcribed in Haskell's footnote continuation; title and cited pages were not independently consulted."),
    ("cand-8117", "Peloponnese", "place", P246, 22,
     "Geographic region named in the account of Francesco Morosini's seventeenth-century triumphs."),
    ("cand-8118", "Corfu", "place", P246, 22,
     "Island named as the site of the 1716 siege withstood by Venice."),
    ("cand-8119", "Siege of Corfu withstood by Venice in 1716", "event", P246, 22,
     "Military event named by Haskell; no additional campaign details are supplied in this passage."),
    ("cand-8120", "Neutrality as Venice's policy under declining political power", "term", P246, 22,
     "Political stance described as Venice's only hope; preserve Haskell's interpretation and do not treat it as a formal treaty."),
    ("cand-8121", "Great powers in Haskell's account of Venice's survival", "term", P246, 22,
     "Collective category of unnamed powers whose forbearance is said to matter to Venice's survival."),
    ("cand-8122", "Betrothal of the Sea ceremony", "procedure", P246, 22,
     "Recurring Venetian ceremony discussed as a tourist attraction and political tradition; individual ceremonial occasions are not itemized."),
    ("cand-8123", "Spain as a political entity in the account of Tiepolo's Madrid mission", "institution", P246, 24,
     "Political entity named as the object of a gesture of appeasement; the passage does not identify a particular Spanish official or negotiation."),
    ("cand-8124", "Leading Venetian patrician families as an unnamed collective", "term", P246, 24,
     "Collective social group said to have supplied important artistic opportunities after State commissions declined; no family is named on this page."),
    ("cand-8125", "Thoughtful Venetians as a civic collective in the ceremony debate", "term", P246, 22,
     "Unnamed Venetians described as beginning to question the ceremony; not an organized group."),
    ("cand-8126", "Unresolved M. S[ilhouette] reference cited at p.246 note 1, vol. I, p.157", "archive", P246, 25,
     "Citation fragment transcribed from the page-end continuation; author spelling, work identity, and full bibliographic data remain unresolved."),
    ("cand-8127", "Foreign influences affecting Venetian ideas in the eighteenth century", "term", P245, 13,
     "Concept described as something the Venetian government sought to limit; distinct from the foreign visitors mentioned later in the paragraph."),
    ("cand-8128", "Venice's declining trade in the eighteenth century", "term", P246, 22,
     "Economic condition named by Haskell in the account of Venice's wealth and the approximate date of Tiepolo's painting."),
]

candidate_ids = {row["candidate_id"] for row in candidate_rows}
if len(candidate_ids) != len(candidate_rows) or max(int(cid.split("-")[1]) for cid in candidate_ids) != 8104:
    raise SystemExit("candidate inventory changed since p.240-241; inspect before allocating IDs")
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, anchor_segment, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []


def mention(segment_id, line_no, suffix, candidate_id, surface, note="", occurrence=0):
    mention_id = f"m-chp9-p245-246-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    position = -1
    search_at = 0
    for _ in range(occurrence + 1):
        position = line.find(surface, search_at)
        if position < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r} #{occurrence}")
        search_at = position + 1
    start = line_offsets[(segment_id, line_no)] + position
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans:
        prior = next(row for row in mention_rows if (row["segment_id"], row["start_char"], row["end_char"]) == span)
        raise SystemExit(f"duplicate existing mention span {span}: {prior['mention_id']} {prior['surface_form']!r}")
    if any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate new mention span: {mention_id} {surface!r}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


MENTION_SPECS = [
    (P245, 12, "city", "cand-2719", "The city", "Coreference to Venice."),
    (P245, 13, "europe", "cand-3462", "Europe", "Geographic frame of the cosmopolitan comparison."),
    (P245, 13, "tourism", "cand-8106", "international tourism", "Concept described as promoted by the government."),
    (P245, 13, "government-first", "cand-8105", "government", "Venetian political authority.", 0),
    (P245, 13, "government-second", "cand-8105", "government", "Coreference to the Venetian government.", 1),
    (P245, 13, "venice-isolation", "cand-2719", "Venice", "City the government sought to isolate."),
    (P245, 13, "foreign-influences", "cand-8127", "foreign influences", "Concept distinct from foreign travellers."),
    (P245, 13, "enlightenment", "cand-8107", "Enlightenment", "General intellectual term used by Haskell."),
    (P245, 13, "foreign-ambassadors", "cand-3562", "Foreign ambassadors", "Unnamed collective; access is described as restricted."),
    (P245, 13, "ordinary-travellers", "cand-3562", "ordinary travellers", "Unnamed visitors, sometimes subject to the same restrictions."),
    (P245, 13, "nobility-first", "cand-8108", "nobility", "Venetian noble estate.", 0),
    (P245, 13, "censorship", "cand-2723", "censorship", "Use the Venice index subentry on censorship."),
    (P245, 13, "political-unorthodoxy", "cand-8112", "political unorthodoxy", "Ground for threatened prosecutions."),
    (P245, 13, "prosecutions", "cand-8113", "prosecutions", "Threatened response to political unorthodoxy."),
    (P245, 13, "travel-law", "cand-8111", "a law", "Travel restriction passed in 1709 and revived in 1783."),
    (P245, 14, "patricians", "cand-8109", "patricians", "Social/legal class subject to the stated travel restriction."),
    (P245, 14, "council-ten", "cand-8110", "Council of Ten", "Authority whose permission was required."),
    (P245, 14, "second-nobility", "cand-8108", "nobility", "Collective social estate described as provincially informed."),
    (P245, 14, "french-travellers", "cand-8115", "French travellers", "Unnamed collective whose suggestion Haskell reports."),
    (P245, 14, "government-sciences", "cand-8105", "the government", "Venetian political authority.", 0),
    (P245, 14, "sciences", "cand-8114", "the sciences", "Field of study in the reported allegation."),
    (P245, 15, "measures", "cand-8111", "The measures", "Coreference to the travel restriction's enforcement."),
    (P245, 15, "de-brosses", "cand-0455", "de Brosses", "Haskell's cited observer, not independently checked here."),
    (P245, 15, "nobles-note", "cand-8108", "nobles", "Venetian noble estate.", 0),
    (P245, 15, "foreigners-note", "cand-3562", "foreigners", "Visitors in the report attributed to de Brosses."),
    (P245, 15, "law-origin", "cand-8111", "the law", "Travel restriction whose origins are cited.", 0),
    (P245, 15, "molmenti", "cand-8116", "Molmenti", "Cited author/reference; title not supplied."),
    (P245, 16, "molmenti-year-page", "cand-8116", "1919. P-27", "Continuation of the Molmenti bibliographic citation; OCR punctuation is noisy."),
    (P246, 19, "europe-reforms", "cand-3462", "Europe", "Comparative geographic scope."),
    (P246, 20, "venice-restore", "cand-2719", "Venice", "City/polity named as the site of reform."),
    (P246, 21, "status-quo", "cand-2730", "status quo", "Use the Venice index subentry on preserving the status quo."),
    (P246, 21, "venice-losing-ground", "cand-8105", "Venice", "Political actor in the international sphere.", 0),
    (P246, 22, "morosini", "cand-1705", "Francesco Morosini", "Named Venetian military leader."),
    (P246, 22, "peloponnese", "cand-8117", "Peloponnese", "Region named as the location of Morosini's triumphs."),
    (P246, 22, "corfu-venice", "cand-8105", "Venice", "Political actor in the 1716 defence.", 0),
    (P246, 22, "siege-corfu", "cand-8119", "the siege of Corfu", "Event at Corfu in 1716."),
    (P246, 22, "corfu", "cand-8118", "Corfu", "Place nested within the event phrase."),
    (P246, 22, "passarowitz", "cand-1855", "the peace of Passarowitz", "Peace treaty named as the point at which Venice surrendered earlier conquests."),
    (P246, 22, "europe-conflicts", "cand-3462", "Europe", "Geographic and political frame of the conflicts."),
    (P246, 22, "neutrality", "cand-8120", "Neutrality", "Described as Venice's only hope."),
    (P246, 22, "great-powers", "cand-8121", "the great powers", "Unnamed collective powers."),
    (P246, 22, "state-weakness", "cand-8105", "the State", "Venetian political authority.", 0),
    (P246, 22, "tourist-trade", "cand-8106", "the tourist trade", "Tourism as one motive for maintaining ceremonies."),
    (P246, 22, "old-customs", "cand-2738", "old traditions and customs", "Use the Venice index subentry on the maintenance of old customs."),
    (P246, 22, "tourists", "cand-3562", "the tourists", "Visitors who are reported to find the ceremony ridiculous."),
    (P246, 22, "betrothal", "cand-8122", "The Betrothal of the Sea", "Recurring Venetian ceremony."),
    (P246, 22, "thoughtful-venetians", "cand-8125", "thoughtful Venetians", "Unnamed civic collective described as beginning to have doubts."),
    (P246, 22, "venice-great-power-fiction", "cand-8105", "Venice", "Political entity in the fiction of continuing great-power status.", 1),
    (P246, 22, "state-fiction", "cand-8105", "the State", "Venetian political authority and its public representation.", 1),
    (P246, 22, "tiepolo", "cand-2569", "Tiepolo", "Artist identified in the index."),
    (P246, 22, "neptune-picture", "cand-2600", "Neptune paying Homage to Venice", "Painting index subentry under Giambattista Tiepolo."),
    (P246, 22, "venetian-trade", "cand-8128", "Venetian trade", "Venice's trade situation in about 1745."),
    (P246, 22, "veronese", "cand-2755", "Veronese", "Paolo Veronese."),
    (P246, 23, "triumphant-venice", "cand-2719", "Venice", "City/state personified in Veronese's legacy."),
    (P246, 23, "tiepolo-painting-confidence", "cand-2600", "the picture", "Coreference to Neptune paying Homage to Venice."),
    (P246, 24, "tiepolo-belief", "cand-2569", "Tiepolo", "Artist named as an adherent of the Venetian ancien régime."),
    (P246, 24, "ancien-regime", "cand-2581", "Venetian ancien regime", "Use the Tiepolo index subentry on belief in the ancien régime."),
    (P246, 24, "state-failed", "cand-8105", "the State", "Venetian political authority.", 0),
    (P246, 24, "tiepolo-him", "cand-2569", "him", "Coreference to Tiepolo."),
    (P246, 24, "madrid", "cand-1481", "Madrid", "Destination of Tiepolo's mission."),
    (P246, 24, "spain", "cand-8123", "Spain", "Polity named as the object of appeasement."),
    (P246, 24, "state-commissions", "cand-2747", "State commissions to the arts", "Use the Venice index subentry on State art patronage."),
    (P246, 24, "patrician-families", "cand-8124", "the leading patrician families", "Unnamed collective social group."),
    (P246, 25, "silhouette-reference", "cand-8126", "S silhouette]", "Unresolved tail of the p.246 note 1 citation; do not normalize the source name."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, printed_page, pdf_physical_page,
                   text_layer="body", marker=None, extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": printed_page, "pdf_physical_page": pdf_physical_page,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if marker is not None:
        qualifiers["footnote_marker"] = marker
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(segment_id, first, last), "origin": "book",
            "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp9-p245-cosmopolitan-tourism", P245, 11, 13,
        "cand-2719", "cand-8106", "cosmopolitan_centre_and_international_tourism_promoted",
        "Haskell describes Venice as one of Europe's great cosmopolitan centres and an acknowledged resort of international tourism that the government actively promoted.",
        "Broad authorial characterization of eighteenth-century Venice; tourism is a concept rather than a named organization.",
        ["cand-2719", "cand-3462", "cand-8106", "cand-8105"], 245, 3,
        extras={"ocr_corrections": [{"source_line": 12, "ocr": "Aeighteenth", "print": "eighteenth", "basis": "CHP-9.pdf physical page 3; initial drop-cap A belongs to the opening sentence"}]}),
    make_statement("st-chp9-p245-isolation-policy", P245, 13, 13,
        "cand-8105", "cand-2719", "sought_to_isolate_venice_from_foreign_influences_and_enlightenment",
        "Haskell says the same government systematically sought to isolate Venice from foreign influences and forces summarized as the Enlightenment.",
        "The policy was not altogether successful, although Haskell says it was enforced with extreme rigour; the city and political authority remain separate candidates.",
        ["cand-8105", "cand-2719", "cand-8127", "cand-8107", "cand-2732"], 245, 3,
        extras={"ocr_corrections": [{"source_line": 13, "ocr": "against’", "print": "against", "basis": "CHP-9.pdf physical page 3"}]}),
    make_statement("st-chp9-p245-visitor-access", P245, 13, 13,
        "cand-3562", "cand-8108", "foreign_visitors_refused_contact_with_the_nobility",
        "Haskell says foreign ambassadors and sometimes ordinary travellers were kept to themselves and refused contact with the nobility.",
        "Collective categories only; the passage does not identify individual visitors or nobles. Footnote 1 contains qualifications and contrasting reports and remains separately anchored in the notes segment.",
        ["cand-3562", "cand-8108", "cand-8105"], 245, 3, marker=1),
    make_statement("st-chp9-p245-censorship-and-prosecution", P245, 13, 13,
        "cand-2723", "cand-8112", "censorship_and_prosecutions_enforced_political_restrictions",
        "Haskell characterizes censorship as strict but fitful and says prosecutions for political unorthodoxy threatened even highly placed people.",
        "The text describes risk and practice generally; it does not name a prosecution in this sentence. The footnote marker points to a separate example to be processed from the notes segment.",
        ["cand-2723", "cand-8112", "cand-8113"], 245, 3, marker=2),
    make_statement("st-chp9-p245-travel-law", P245, 13, 14,
        "cand-8111", "cand-8109", "restricted_patricians_travel_abroad_without_council_permission",
        "Haskell says a law passed in 1709 and revived in 1783 forbade patricians to travel abroad without special permission of the Council of Ten.",
        "Dates and scope follow the source. The note on the law's origins is cited but not independently consulted; patricians and the broader nobility remain distinct candidates.",
        ["cand-8111", "cand-8109", "cand-8110"], 245, 3, marker=3,
        extras={"relation_candidate": True}),
    make_statement("st-chp9-p245-unresolved-tension", P245, 14, 14,
        "cand-8105", "cand-2719", "contradiction_affected_politics_and_culture_without_resolution",
        "Haskell says the contradiction affected Venetian politics and culture and produced a tension that was never resolved.",
        "Authorial synthesis, not a dated event or a claim attributed to a named witness.",
        ["cand-8105", "cand-2719"], 245, 3),
    make_statement("st-chp9-p245-nobility-and-reform", P245, 14, 14,
        "cand-8108", None, "criticized_as_provincial_and_ignorant_while_remedies_were_obstructed",
        "Haskell reports complaints about the nobility's provincialism and ignorance, while saying that those who sought to remedy the situation faced hindrances.",
        "The complaints are reported without a named speaker; the passage does not identify a particular reformer or measure. Footnote 4 is a separate cited report.",
        ["cand-8108"], 245, 3, marker=4),
    make_statement("st-chp9-p245-sciences-allegation", P245, 14, 14,
        "cand-8115", "cand-8114", "suggested_government_discouraged_sciences_for_political_reasons",
        "Haskell reports that some French travellers suggested the government deliberately discouraged the sciences for political reasons.",
        "This sentence continues at p.246 L19, which explicitly says there is no direct evidence for the suggestion; keep the allegation and its qualification linked.",
        ["cand-8115", "cand-8105", "cand-8114"], 245, 3,
        extras={"continuation_to_segment_id": P246, "continuation_to_source_line": 19}),
    make_statement("st-chp9-p245-footnote1-measures-and-brosses", P245, 15, 16,
        "cand-0455", "cand-8108", "reported_variation_and_rare_foreign_contact",
        "In the page-end continuation of note 1, Haskell says the measures probably varied in severity and treats de Brosses's report that nobles very rarely received foreigners as plausible.",
        "Footnote quotation continuation from the consolidated notes segment L324. De Brosses is a cited witness; his work was not independently checked. The noisy OCR citation for Molmenti is recorded in a separate bibliographic statement.",
        ["cand-0455", "cand-8108", "cand-3562", "cand-8111"], 245, 3,
        text_layer="footnote quotation continuation", marker=1,
        extras={"quoted_speaker": "Charles de Brosses, as cited by Haskell",
                "continued_from_segment_id": NOTES, "continued_from_source_line": 324,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 324, "source_line_end": 324}]}),
    make_statement("st-chp9-p245-footnote1-molmenti-reference", P245, 15, 16,
        "cand-8111", "cand-8116", "cites_molmenti_1919_page_27_for_origins_of_law",
        "Haskell cites Molmenti (1919, p.27) for the origins of the law restricting travel.",
        "This is a bibliographic pointer in the continuation of note 1, not independent confirmation of the law's origin; the OCR punctuation is noisy and the work title is not supplied.",
        ["cand-8111", "cand-8116"], 245, 3,
        text_layer="footnote quotation continuation", marker=1,
        extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 324,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 324, "source_line_end": 324}],
                "ocr_corrections": [{"source_line": 16, "ocr": "1919. P-27- -, ,", "print": "1919, p. 27", "basis": "CHP-9.pdf physical page 3"}]}),
    make_statement("st-chp9-p246-sciences-qualification", P246, 19, 19,
        "cand-8115", "cand-8114", "allegation_not_supported_by_direct_evidence",
        "Haskell completes the preceding sentence by saying there is no direct evidence that the government deliberately discouraged the sciences for political reasons.",
        "This line closes the p.245 statement; it explicitly limits the preceding suggestion and must not be detached from it.",
        ["cand-8115", "cand-8105", "cand-8114"], 246, 4, marker=1,
        extras={"continued_from_segment_id": P245, "continued_from_source_line": 14,
                "cross_reference_segments": [{"segment_id": P245, "source_line_start": 14, "source_line_end": 14}]}),
    make_statement("st-chp9-p246-reforms", P246, 19, 20,
        "cand-8105", "cand-2719", "reforms_aimed_to_restore_an_earlier_situation",
        "Haskell says reforms were in the air throughout Europe, but in Venice they were designed to restore an earlier situation.",
        "The comparison is Haskell's generalization; the specific reforms are not identified in this sentence.",
        ["cand-8105", "cand-2719", "cand-3462"], 246, 4),
    make_statement("st-chp9-p246-status-quo", P246, 21, 21,
        "cand-8105", "cand-2730", "sought_to_preserve_status_quo_or_move_backwards",
        "Haskell identifies a century-long preoccupation with preserving the status quo or moving backwards if change was unavoidable.",
        "Authorial interpretation of a recurring political tendency; not a single policy decree.",
        ["cand-8105", "cand-2730"], 246, 4),
    make_statement("st-chp9-p246-morosini-triumphs", P246, 21, 22,
        "cand-1705", "cand-8117", "triumphs_in_peloponnese_celebrated_in_1686_were_short_lived",
        "Haskell says Venice had been losing ground through much of the seventeenth century and that Francesco Morosini's triumphs in the Peloponnese, celebrated in 1686, were short-lived.",
        "The source names no specific battle or campaign in this passage; 1686 is the celebration date stated by Haskell.",
        ["cand-8105", "cand-2719", "cand-1705", "cand-8117"], 246, 4),
    make_statement("st-chp9-p246-corfu-and-passarowitz", P246, 22, 22,
        "cand-8105", "cand-1855", "withstood_corfu_siege_then_surrendered_earlier_conquests",
        "Haskell says Venice just withstood the siege of Corfu in 1716, then at the 1718 peace of Passarowitz had to surrender all conquests from thirty years earlier.",
        "The passage does not specify the individual territories surrendered; the 1716 siege and peace are distinct events.",
        ["cand-8105", "cand-2719", "cand-8118", "cand-8119", "cand-1855"], 246, 4,
        extras={"relation_candidate": True}),
    make_statement("st-chp9-p246-decline-neutrality", P246, 22, 22,
        "cand-8105", "cand-8120", "declining_trade_and_strength_made_neutrality_the_only_hope",
        "Haskell says Venice remained wealthy despite declining trade but was too weak to take further part in European struggles; neutrality was the only hope, and survival depended more on the great powers' forbearance than on Venice's ability to resist.",
        "This is Haskell's political interpretation. The great powers are unnamed and the passage does not identify a specific treaty or guarantee.",
        ["cand-8105", "cand-2719", "cand-3462", "cand-8120", "cand-8121", "cand-8128"], 246, 4),
    make_statement("st-chp9-p246-customs-and-tourism", P246, 22, 22,
        "cand-8105", "cand-2738", "state_preserved_old_customs_amid_weakness_and_tourism",
        "Haskell says the State turned to dreams of the past to compensate for weakness and immobility, and that old traditions and customs were maintained partly for tourist trade and partly for other reasons.",
        "Haskell says this was fully as much as, not exclusively, for tourism; do not reduce the explanation to tourism alone.",
        ["cand-8105", "cand-2738", "cand-8106"], 246, 4),
    make_statement("st-chp9-p246-betrothal-judgment", P246, 22, 22,
        "cand-3562", "cand-8122", "tourists_found_betrothal_ceremony_ridiculous",
        "Haskell says tourists mainly found the Betrothal of the Sea ceremony ridiculous, while more thoughtful Venetians were also beginning to doubt it.",
        "This is a reported generalization; note 2 attributes a related report to Abbé Coyer and is still pending in the consolidated notes segment.",
        ["cand-3562", "cand-8122", "cand-8125"], 246, 4, marker=2),
    make_statement("st-chp9-p246-great-power-fiction", P246, 22, 23,
        "cand-8105", "cand-2719", "maintained_fiction_of_venice_as_a_great_power_in_state_commissions",
        "Haskell says the fiction that Venice remained a great power was maintained through every artifice available to the State and naturally affected the painting it commissioned.",
        "The claim concerns political self-presentation and state patronage, not an independent assessment of Venice's legal rank among powers.",
        ["cand-8105", "cand-2719", "cand-2747", "cand-2600"], 246, 4,
        extras={"relation_candidate": True}),
    make_statement("st-chp9-p246-tiepolo-confidence", P246, 22, 23,
        "cand-2600", "cand-8105", "painted_about_1745_as_an_expression_of_state_confidence",
        "Haskell calls Tiepolo's Neptune paying Homage to Venice the clearest illustration of this frame of mind: painted about 1745, it expresses self-confidence despite concern about Venetian trade.",
        "Approximate date and Haskell's interpretation are retained; the painting remains linked to its artist candidate and is not assigned a new object identity here.",
        ["cand-2569", "cand-2600", "cand-2719", "cand-8105", "cand-8128"], 246, 4,
        extras={"relation_candidate": True, "footnote_marker": 3,
                "ocr_corrections": [{"source_line": 22, "ocr": "Uve", "print": "live", "basis": "CHP-9.pdf physical page 4"}]}),
    make_statement("st-chp9-p246-veronese-inspiration", P246, 22, 23,
        "cand-2755", "cand-2600", "provided_inspiration_for_tiepolo_painting",
        "Haskell says Veronese, as a personification of triumphant Venice, provided inspiration for Tiepolo's painting and much eighteenth-century Venetian painting; the painting is not nostalgic despite its appeal to past glories.",
        "Art-historical interpretation by Haskell; the passage does not assert a direct quotation or copied composition.",
        ["cand-2755", "cand-2600", "cand-2569", "cand-2719"], 246, 4,
        extras={"relation_candidate": True}),
    make_statement("st-chp9-p246-tiepolo-belief", P246, 24, 24,
        "cand-2569", "cand-2581", "believed_in_venetian_ancien_regime",
        "Haskell says Tiepolo was almost alone in wholeheartedly believing in the Venetian ancien régime.",
        "This is Haskell's interpretive characterization, not a quotation from Tiepolo.",
        ["cand-2569", "cand-2581"], 246, 4),
    make_statement("st-chp9-p246-tiepolo-madrid-mission", P246, 24, 24,
        "cand-8105", "cand-2614", "sent_tiepolo_to_madrid_against_his_will_to_appease_spain",
        "Haskell says the State made little further use of Tiepolo and drove him against his will to Madrid as a gesture of appeasement towards Spain.",
        "Haskell's wording presents coercion and diplomatic purpose; no specific Spanish negotiation or official is named.",
        ["cand-8105", "cand-2569", "cand-2614", "cand-1481", "cand-8123"], 246, 4,
        extras={"relation_candidate": True}),
    make_statement("st-chp9-p246-end-state-commissions", P246, 24, 24,
        "cand-8105", "cand-2747", "state_art_commissions_nearly_ended_and_families_supplied_opportunities",
        "Haskell says State commissions to the arts were virtually at an end and that leading patrician families gave the greatest artists their most rewarding opportunities.",
        "The sentence describes a broad change in patronage; the unnamed families are not individually identified and the continuation begins a new paragraph on p.247.",
        ["cand-8105", "cand-2747", "cand-8124"], 246, 4, marker=4,
        extras={"relation_candidate": True}),
    make_statement("st-chp9-p246-footnote1-citation-tail", P246, 25, 25,
        "cand-8126", None, "continues_unresolved_reference_in_footnote_1",
        "The page-end fragment continues the citation attached to p.246 note 1, transcribed as M. S[ilhouette], vol. I, p.157.",
        "The OCR and page image do not establish the author's identity or full work title; no normalization or external identification is made.",
        ["cand-8126"], 246, 4, text_layer="footnote quotation continuation", marker=1,
        extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 328,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 328, "source_line_end": 328}]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")

coverage_by_id[P245].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L7-16",
    "note": "Printed p.245 (CHP-9.pdf physical p.3) reviewed against the page image. The main-text sentence ending at L14 continues and is closed by p.246 L19; the note 1 tail at L15-16 is recorded as a footnote quotation continuation linked to the notes segment L324. Heading/page markers are retained only as source structure. OCR corrections are recorded in statement qualifiers; source OCR is unchanged.",
})
coverage_by_id[P246].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L18-25",
    "note": "Printed p.246 (CHP-9.pdf physical p.4) reviewed against the page image. L19 closes the p.245 sciences sentence; body claims, approximate dates, reported interpretations and the p.246 note 1 citation tail at L25 are separately anchored. The final body sentence is complete on this page; note 1 tail links to consolidated notes L328. Notes 2-4 remain separate in the queued notes segment.",
})

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
print(json.dumps({
    "segments": sorted(TARGETS), "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage": {P245: [coverage_by_id[P245]["disposition"], coverage_by_id[P245]["migration_status"]],
                 P246: [coverage_by_id[P246]["disposition"], coverage_by_id[P246]["migration_status"]]},
}, ensure_ascii=False))
if not args.apply:
    print("DRY RUN: no files changed")
else:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
    write_csv_atomic(mention_path, mention_fields, mention_rows + new_mentions)
    write_jsonl_atomic(statement_path, statement_rows + new_statements)
    write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
    print("applied; backups=" + ", ".join(backup.name for _, backup in backups))
