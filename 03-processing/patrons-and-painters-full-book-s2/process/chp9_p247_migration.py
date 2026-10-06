"""Controlled S2 migration for printed page 247.

Default invocation is a read-only dry run. It leaves the source OCR untouched.
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
P247 = "chp-9:09_CHP-9_intro:l27-36"
P248 = "chp-9:09_CHP-9_intro:l38-46"
P246 = "chp-9:09_CHP-9_intro:l18-25"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
BACKUP_SUFFIX = ".bak-s2-chp9-p247-20261001"
EXPECTED_SEGMENT_HASH = "7b7c85bfda0e96fa9e2d3d69aee031457433796ae97125cba42ae80f5f3db2ee"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"


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
for required in (P247, P248, P246, NOTES):
    if required not in segment_by_id:
        raise SystemExit(f"missing segment metadata: {required}")
page_meta = segment_by_id[P247]
if page_meta["sha256"] != EXPECTED_SEGMENT_HASH or page_meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.247 source hashes changed; inspect before migration")
asset = ROOT / page_meta["source_file"]
if hashlib.sha256(asset.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
if not PDF.is_file() or not (PROCESS / "p247_page_review_hi.png").is_file() or not (PROCESS / "p248_page_review.png").is_file():
    raise SystemExit("chapter PDF or reviewed page images are missing")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
selected = source_lines[page_meta["line_start"] - 1:page_meta["line_end"]]
if hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_HASH:
    raise SystemExit("p.247 segment content hash changed")
line_offsets = {}
offset = 0
for line_no, line in zip(range(page_meta["line_start"], page_meta["line_end"] + 1), selected):
    line_offsets[line_no] = offset
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
current = coverage_by_id.get(P247)
if not current or (current["disposition"], current["migration_status"], current["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"unexpected p.247 coverage: {current}")

new_candidates = [
    ("cand-8129", "Senate of Venice in Haskell's account", "institution", 28,
     "The Senate is presented as compelled to admit new families during fiscal pressure; the source does not name an individual senator or a formal act title."),
    ("cand-8130", "Venetian Church under noble governance", "institution", 29,
     "The Church is described as an institution governed by the nobility and submitted to the State; no individual church body is specified."),
    ("cand-8131", "Rich Venetian bourgeoisie", "term", 29,
     "A social group described as emerging from nobles' withdrawal from trade but lacking political power and autonomous culture; no members are listed."),
    ("cand-8132", "Wealthier Venetian noble families", "term", 28,
     "Unnamed richer families and nobles associated with control of administrative posts; retain as a collective, not as named families."),
    ("cand-8133", "Poorer Venetian patrician families", "term", 28,
     "Unnamed poorer patrician families described as dependent on and plotting against wealthier relations while opposing broader political participation."),
    ("cand-8134", "New families admitted into Venetian nobility", "term", 28,
     "Families admitted during fiscal pressure and allowed to purchase noble status; keep distinct from the older aristocracy."),
    ("cand-8135", "Purchase of admission into Venetian nobility", "procedure", 28,
     "The source says new families were allowed to buy themselves into the nobility; it supplies no formal procedure name or detailed rules."),
    ("cand-8136", "Seventeenth-century Venetian wars against the Turks", "event", 28,
     "Wars are cited as draining State resources; the passage gives no campaign names or dates beyond the century."),
    ("cand-8137", "Older Venetian aristocracy", "term", 28,
     "Unnamed older aristocratic group said to hold newer nobles in contempt and exclude them from important administrative spheres."),
    ("cand-8138", "Antichiesetta in Palazzo Ducale", "place", 32,
     "Named interior location for allegorical frescoes; retain the source's Italian name and do not conflate it with the entire palace."),
    ("cand-8139", "Allegorical frescoes in the Antichiesetta alluding to virtuous government", "work", 32,
     "Collective work description in the continuation of note 4; no individual fresco title or artist is supplied."),
    ("cand-8140", "Scattered frescoes elsewhere in Palazzo Ducale by artists including Bambini", "work", 32,
     "A collective reference to scattered palace frescoes; only Bambini is named and no individual work is identified."),
    ("cand-8141", "Four paintings by Francesco Guardi recording the Pope's 1782 visit", "work", 33,
     "The source reports an order for four paintings to record a papal visit; titles and present identities are not supplied."),
    ("cand-8142", "Unidentified Pope visiting Venice in 1782", "person", 33,
     "The Pope is unnamed in the passage; do not infer the pontiff's identity from the date alone."),
    ("cand-8143", "Papal visit to Venice recorded by Guardi in 1782", "event", 33,
     "The source dates the visit to 1782 but does not name the Pope or provide further itinerary details."),
    ("cand-8144", "Unnamed Venetian Academy established by the State", "institution", 33,
     "The Academy is not named on this page; Haskell points forward to Chapter 12."),
    ("cand-8145", "Paolo Renier's 1767 statement on avoiding novelty in public bodies", "archive", 36,
     "A statement attributed to Renier and quoted in the page note; the source identifies it through Marcellino, p. 30, note 78."),
    ("cand-8146", "Marcellino reference for Paolo Renier, p. 30, note 78", "archive", 36,
     "Bibliographic pointer printed after the Renier quotation; full title and edition details are not supplied in this passage."),
    ("cand-8147", "Noble families' trade-dependent fortunes and land-derived income", "term", 28,
     "Haskell says noble families' histories and fortunes depended on trade while they had long since drawn their incomes from land; no individual family is named."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
if len(candidate_ids) != len(candidate_rows):
    raise SystemExit("duplicate candidate IDs already exist")
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 8128:
    raise SystemExit("candidate inventory changed since p.245-246; inspect before allocating IDs")
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, line_no, detail in new_candidates:
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
        "candidate_source_ref": f"{P247}#L{line_no}",
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []


def mention(line_no, suffix, candidate_id, surface, note="", occurrence=0):
    mention_id = f"m-chp9-p247-{suffix}"
    if mention_id in existing_mention_ids:
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    position = -1
    search_at = 0
    for _ in range(occurrence + 1):
        position = line.find(surface, search_at)
        if position < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r} occurrence={occurrence}")
        search_at = position + len(surface)
    start = line_offsets[line_no] + position
    end = start + len(surface)
    span = (P247, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mention_id} {surface!r}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": P247, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


MENTION_SPECS = [
    (28, "state-first", "cand-8105", "the State", "Venetian political authority.", 0),
    (28, "nobility-first", "cand-8108", "nobility", "The social estate holding government.", 0),
    (28, "constitution-first", "cand-2726", "Venetian constitution", "Index candidate for criticism of the eighteenth-century constitution."),
    (28, "europe", "cand-3462", "Europe", "Comparative political frame."),
    (28, "noble-families", "cand-8108", "Noble families", "Collective social estate."),
    (28, "trade", "cand-8147", "trade", "Economic activity from which noble families had withdrawn."),
    (28, "land", "cand-8147", "the land", "Land-derived income in the account of noble fortunes."),
    (28, "rich-families", "cand-8132", "rich", "Wealthier side of the family division."),
    (28, "poor-families", "cand-8133", "poor families", "Poorer side of the family division."),
    (28, "government-stability", "cand-8105", "stability of government", "Political stability endangered by social divisions."),
    (28, "constitution-resistance", "cand-2726", "constitution", "Object of resistance to change.", 1),
    (28, "wealthier-nobles", "cand-8132", "wealthier nobles", "Unnamed wealthy noble collective."),
    (28, "leading-positions", "cand-8105", "leading positions", "Administrative positions monopolized by wealthier nobles."),
    (28, "administration-first", "cand-8105", "administration", "State administration."),
    (28, "poorer-patricians", "cand-8133", "poorer patrician families", "Unnamed poorer patrician collective."),
    (28, "fortunate-relations", "cand-8132", "their more fortunate relations", "Coreference to richer family members."),
    (28, "basis-government", "cand-8105", "basis of government", "Political participation."),
    (28, "state-second", "cand-8105", "the State", "Venetian political authority.", 1),
    (28, "turkish-wars", "cand-8136", "seventeenth-century wars against the Turks", "Wars said to drain State resources."),
    (28, "senate", "cand-8129", "the Senate", "Venetian governing institution."),
    (28, "new-families", "cand-8134", "new families", "Families admitted during fiscal pressure."),
    (28, "purchase-nobility", "cand-8135", "buy themselves into the nobility", "Purchase of noble status; footnote marker 2."),
    (28, "recent-nobles", "cand-8134", "more recent nobles", "Newly admitted noble families."),
    (28, "older-aristocracy", "cand-8137", "older aristocracy", "Established Venetian aristocratic group."),
    (28, "administration-exclusion", "cand-8105", "administration", "Important administrative spheres from which newer nobles were excluded.", 1),
    (28, "mercantile-origins", "cand-8134", "mercantile origins", "Commercial background the newer nobles sought to disguise."),
    (28, "venetian-life", "cand-2738", "Venetian life", "Conservative social tone described by Haskell."),
    (28, "old-custom-proverb", "cand-2738", "à Venise il suffit qu’une coutume soit ancienne pour être toujours suivie . . .", "French proverb quoted by Haskell; footnote marker 3."),
    (29, "church", "cand-8130", "The Church", "Institution described as governed by the nobility."),
    (29, "nobility", "cand-8108", "nobility", "Venetian noble estate."),
    (29, "state", "cand-8105", "the State", "Venetian political authority."),
    (29, "rich-bourgeoisie", "cand-8131", "rich bourgeoisie", "Emerging social group."),
    (29, "nobles-withdraw-trade", "cand-8108", "nobles’ withdrawal from trade", "Economic withdrawal described as the cause of bourgeois formation."),
    (29, "political-power", "cand-8131", "political power", "Power the bourgeoisie is said not to have acquired."),
    (29, "autonomous-culture", "cand-2736", "autonomous culture", "Index candidate on the lack of autonomous bourgeois culture."),
    (29, "venice", "cand-2719", "Venice", "City from which Goldoni left."),
    (29, "goldoni", "cand-1205", "Goldoni", "Carlo Goldoni."),
    (29, "gasparo-gozzi", "cand-1220", "Gasparo Gozzi", "Named as Goldoni's admirer."),
    (29, "aristocracy", "cand-8108", "aristocracy", "The social group to which Gasparo Gozzi was attached."),
    (29, "art-patronage", "cand-2720", "Venetian art patronage", "Index topic concerning aristocratic patronage."),
    (29, "aristocratic-tastes", "cand-2720", "aristocratic tastes", "Tastes shaping choices of artists, subjects and styles."),
    (30, "decline-state-patronage", "cand-2728", "decline of State patronage of the arts", "Index topic on declining State patronage."),
    (30, "financial-families", "cand-8124", "families", "The limited number of financially powerful families; compare the p.246 collective."),
    (31, "aristocratic-status", "cand-8108", "aristocratic status", "Status motive for patronage; sentence continues onto p.248."),
    (32, "venice-in-note", "cand-2719", "Venice", "Completion of the p.246 note 4 reference to Tiepolo's painting."),
    (32, "palazzo-ducale", "cand-1806", "Palazzo Ducale", "Location of the Tiepolo painting and other works."),
    (32, "allegorical-frescoes", "cand-8139", "allegorical frescoes", "Collective fresco reference in the Antichiesetta."),
    (32, "virtuous-government", "cand-8105", "its virtuous government", "Venetian political virtue represented allegorically."),
    (32, "antichiesetta", "cand-8138", "Antichiesetta", "Named interior location."),
    (32, "scattered-frescoes", "cand-8140", "a few scattered frescoes by other artists", "Collective work reference; Bambini is named separately."),
    (32, "bambini", "cand-0171", "Bambini", "Niccolò Bambini."),
    (32, "palace", "cand-1806", "the palace", "Coreference to Palazzo Ducale."),
    (33, "state-ordered-paintings", "cand-8105", "it", "Coreference to the Venetian State.", 0),
    (33, "four-paintings", "cand-8141", "four paintings", "Unidentified group ordered to record the visit."),
    (33, "guardi", "cand-1239", "Francesco Guardi", "Named painter."),
    (33, "pope", "cand-8142", "Pope", "Unidentified pontiff; do not infer identity."),
    (33, "visit-event", "cand-8143", "visit", "The 1782 papal visit to Venice."),
    (34, "academy-second", "cand-8144", "Academy", "Coreference to the Academy mentioned on p.247 L33."),
    (35, "open-minded-nobles", "cand-8108", "nobles", "Noble group described as opposing constitutional change."),
    (35, "constitutional-change", "cand-2726", "changes in the constitution", "Changes opposed by the nobles."),
    (36, "paolo-renier", "cand-2133", "Paolo Renier", "Named writer of the 1767 statement."),
    (36, "marcellino", "cand-8146", "Marcellino", "Citation printed after the quotation."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(first, last):
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, first, last, subject, obj, predicate, claim, qualification,
                   mentioned, marker=None, extras=None):
    if first < page_meta["line_start"] or last > page_meta["line_end"]:
        raise SystemExit(f"statement lines outside target segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 247,
        "pdf_physical_page": 5, "claim": claim, "speaker": "Haskell",
        "text_layer": "body" if first <= 31 else "footnote continuation or unnumbered page note",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if marker is not None:
        qualifiers["footnote_marker"] = marker
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": P247,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(first, last), "origin": "book",
            "source_file": page_meta["source_file"]}


new_statements = [
    make_statement("st-chp9-p247-state-administration", 28, 28, "cand-8105", "cand-8108",
        "government_and_higher_administration_held_by_nobility",
        "Haskell says the State's government and higher administration were in the hands of the nobility.",
        "A general description of political control; no named officeholder is identified.",
        ["cand-8105", "cand-8108"], extras={"relation_candidate": True}),
    make_statement("st-chp9-p247-constitution-criticism", 28, 28, "cand-2726", None,
        "constitution_under_foreign_criticism_by_early_18th_century",
        "Haskell says the Venetian constitution, once admired in Europe, faced heavy criticism from abroad by the beginning of the eighteenth century.",
        "The passage does not name individual critics or specific constitutional proposals.",
        ["cand-2726", "cand-3462"], marker=1),
    make_statement("st-chp9-p247-noble-fortunes-and-division", 28, 28, "cand-8108", "cand-8105",
        "trade_dependent_history_and_fortunes_with_land_derived_income_and_rich_poor_division_endangered_government",
        "Haskell says noble families' histories and fortunes depended on trade while they had long since drawn their incomes from the land, and that divisions between rich and poor families endangered government stability.",
        "This is Haskell's account of social and economic change; no family is named.",
        ["cand-8108", "cand-8132", "cand-8133", "cand-8105", "cand-8147"]),
    make_statement("st-chp9-p247-rich-poor-patrician-politics", 28, 28, "cand-8132", "cand-8133",
        "wealthier_nobles_monopolized_office_while_poorer_patricians_opposed_widening_government",
        "Haskell says wealthier nobles increasingly monopolized leading administrative posts, while poorer patrician families depended on and plotted against wealthier relations but agreed that the basis of government must not be widened.",
        "Collective groups only; retain the source's contrast and do not infer individual family alignments.",
        ["cand-8132", "cand-8133", "cand-8105", "cand-2726"]),
    make_statement("st-chp9-p247-senate-admission", 28, 28, "cand-8129", "cand-8134",
        "admitted_new_families_during_resource_depletion_and_allowed_purchase_of_nobility",
        "Haskell says the Senate was compelled to admit more families as State resources drained during seventeenth-century wars against the Turks, and that the new families were allowed to purchase noble status.",
        "The war is not broken into named campaigns; the source does not provide the purchase procedure's formal title.",
        ["cand-8129", "cand-8105", "cand-8136", "cand-8134", "cand-8135", "cand-8108"],
        marker=2, extras={"relation_candidate": True}),
    make_statement("st-chp9-p247-new-nobles-exclusion", 28, 28, "cand-8134", "cand-8137",
        "new_nobles_treated_with_contempt_and_excluded_from_administration",
        "Haskell says newer nobles were often held in contempt by the older aristocracy and excluded from important administrative spheres.",
        "Neither the newer families nor the older aristocratic families are individually named.",
        ["cand-8134", "cand-8137", "cand-8105"]),
    make_statement("st-chp9-p247-new-nobles-integration", 28, 28, "cand-8134", "cand-2738",
        "concealed_mercantile_origins_and_adopted_conservative_social_order",
        "Haskell says newer nobles sought to disguise their mercantile origins and integrate into the existing order, making radical social ideas unlikely; he characterizes Venetian life through a proverb about following ancient customs.",
        "The French proverb is quoted as a general characterization; it is not attributed here to a named speaker.",
        ["cand-8134", "cand-2738"], marker=3),
    make_statement("st-chp9-p247-church-submission", 29, 29, "cand-8130", "cand-8105",
        "governed_by_nobility_and_maintained_through_submission_to_state",
        "Haskell says the Church was governed entirely by the nobility and maintained in splendour only through absolute submission to the State.",
        "The author signals that the account of the Church will be developed later; no named church body is specified.",
        ["cand-8130", "cand-8108", "cand-8105"], extras={"relation_candidate": True,
        "ocr_corrections": [{"source_line": 29, "ocr": "price pf absolute", "print": "price of absolute", "basis": "CHP-9.pdf physical page 5"}]}),
    make_statement("st-chp9-p247-bourgeois-culture", 29, 29, "cand-8131", "cand-2736",
        "emerged_after_noble_trade_withdrawal_but_lacked_political_power_and_autonomous_culture",
        "Haskell says a rich bourgeoisie formed as nobles withdrew from trade but acquired neither political power nor an autonomous culture.",
        "The group is collective and unnamed; the claim is Haskell's social interpretation.",
        ["cand-8131", "cand-8108", "cand-2736"]),
    make_statement("st-chp9-p247-goldoni-left", 29, 29, "cand-1205", "cand-2719",
        "left_venice_as_a_spokesman_for_the_bourgeoisie",
        "Haskell presents Goldoni as a natural spokesman for the bourgeoisie who left Venice.",
        "The passage does not specify a date or destination.",
        ["cand-1205", "cand-2719", "cand-8131"], extras={"relation_candidate": True}),
    make_statement("st-chp9-p247-gozzi-attached", 29, 29, "cand-1220", "cand-8108",
        "became_attached_to_more_intelligent_aristocrats",
        "Haskell says Gasparo Gozzi, Goldoni's keen admirer, became no more than a hanger-on of the more intelligent members of the aristocracy.",
        "This is Haskell's characterization; it is not a formal employment relation.",
        ["cand-1220", "cand-1205", "cand-8108"], extras={"relation_candidate": True}),
    make_statement("st-chp9-p247-patronage-tastes", 29, 29, "cand-2720", "cand-8108",
        "history_reflected_forces_shaping_aristocratic_tastes_and_choices",
        "Haskell frames eighteenth-century Venetian art patronage as the history of forces shaping aristocratic tastes, reflected in choices of artists, subjects and styles.",
        "This is an authorial synthesis, not a claim about one specific commission.",
        ["cand-2720", "cand-8108"]),
    make_statement("st-chp9-p247-state-patronage-decline", 30, 30, "cand-2728", "cand-8124",
        "decline_of_state_patronage_taken_up_by_financially_powerful_families",
        "Haskell says the decline of State art patronage meant that a limited number of financially powerful families assumed the function.",
        "The families are not named in this sentence; the statement is a broad change in patronage.",
        ["cand-2728", "cand-8105", "cand-8124"], extras={"relation_candidate": True}),
    make_statement("st-chp9-p247-patronage-status", 31, 31, "cand-8124", "cand-8108",
        "patronage_regarded_as_necessary_appurtenance_of_aristocratic_status",
        "Haskell says patronage was looked upon as a necessary appurtenance of aristocratic status.",
        "The sentence ends with 'and may' and continues at p.248 L39; only the completed status claim is asserted here.",
        ["cand-8124", "cand-8108"],
        extras={"continuation_to_segment_id": P248, "continuation_to_source_line": 39}),
    make_statement("st-chp9-p247-tiepolo-palazzo", 32, 32, "cand-2600", "cand-1806",
        "located_in_palazzo_ducale",
        "The continuation of note 4 identifies the Palazzo Ducale as the location of Tiepolo's Neptune paying Homage to Venice.",
        "The work title and commission context begin in the consolidated note at L331; this page supplies the continuation 'Venice in the Palazzo Ducale'.",
        ["cand-2600", "cand-2719", "cand-1806"],
        extras={"relation_candidate": True, "text_layer": "footnote continuation", "continued_from_segment_id": NOTES,
                "continued_from_source_line": 331,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 331, "source_line_end": 331}]}),
    make_statement("st-chp9-p247-antichiesetta-frescoes", 32, 32, "cand-8139", "cand-8105",
        "allegorical_frescoes_alluded_to_virtuous_government",
        "The continuation of note 4 describes allegorical frescoes in the Antichiesetta as alluding to Venice's virtuous government.",
        "No individual fresco title or artist is given.",
        ["cand-8139", "cand-8138", "cand-8105"],
        extras={"relation_candidate": True, "text_layer": "footnote continuation", "continued_from_segment_id": NOTES,
                "continued_from_source_line": 331,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 331, "source_line_end": 331}]}),
    make_statement("st-chp9-p247-bambini-frescoes", 32, 32, "cand-0171", "cand-8140",
        "associated_with_scattered_frescoes_elsewhere_in_palazzo_ducale",
        "The note continuation mentions a few scattered frescoes elsewhere in the palace by other artists such as Bambini.",
        "No specific fresco is identified and the collective reference does not establish a commission.",
        ["cand-0171", "cand-8140", "cand-1806"],
        extras={"relation_candidate": True, "text_layer": "footnote continuation", "continued_from_segment_id": NOTES,
                "continued_from_source_line": 331,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 331, "source_line_end": 331}]}),
    make_statement("st-chp9-p247-guardi-visit", 33, 34, "cand-8105", "cand-8141",
        "ordered_four_paintings_to_record_papal_visit_in_1782",
        "The note continuation says the State ordered four paintings by Francesco Guardi in 1782 to record the Pope's visit.",
        "The Pope and four paintings are unidentified; do not infer a papal identity or individual work titles.",
        ["cand-8105", "cand-8141", "cand-1239", "cand-8142", "cand-8143"],
        extras={"relation_candidate": True, "text_layer": "footnote continuation",
                "continued_from_segment_id": NOTES, "continued_from_source_line": 331,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 331, "source_line_end": 331}]}),
    make_statement("st-chp9-p247-academy-established", 33, 34, "cand-8105", "cand-8144",
        "established_unnamed_academy",
        "The note continuation says the State also established an Academy discussed in Chapter 12.",
        "The Academy's name and establishment date are not given in this passage.",
        ["cand-8105", "cand-8144"],
        extras={"relation_candidate": True, "text_layer": "footnote continuation",
                "continued_from_segment_id": NOTES, "continued_from_source_line": 331,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 331, "source_line_end": 331}]}),
    make_statement("st-chp9-p247-nobles-resist-change", 35, 36, "cand-8108", "cand-2726",
        "even_open_minded_nobles_opposed_constitutional_change",
        "The page's unnumbered note-like passage says even intelligent and open-minded nobles opposed constitutional change and quotes Paolo Renier in 1767 warning against novelty in civil and military bodies.",
        "No footnote number is visible in the scan. Preserve the marker as unresolved; the quotation is cited to Marcellino, p. 30, note 78.",
        ["cand-8108", "cand-2726", "cand-2133", "cand-8145", "cand-8146"],
        extras={"text_layer": "unnumbered page note", "footnote_marker_unresolved": True,
                "quoted_speaker": "Paolo Renier, as cited by Haskell",
                "relation_candidate": True,
                "ocr_corrections": [
                    {"source_line": 36, "ocr": "alia pace", "print": "alla pace", "basis": "CHP-9.pdf physical page 5"},
                    {"source_line": 36, "ocr": "tranquillité", "print": "tranquillità", "basis": "CHP-9.pdf physical page 5"},
                    {"source_line": 36, "ocr": "di fiiori", "print": "di fuori", "basis": "CHP-9.pdf physical page 5"},
                    {"source_line": 36, "ocr": "Fordinario", "print": "l'ordinario", "basis": "CHP-9.pdf physical page 5"},
                ]}),
]
statement_ids = {row["statement_id"] for row in statement_rows}
new_statement_ids = {row["statement_id"] for row in new_statements}
if len(statement_ids) != len(statement_rows) or len(new_statement_ids) != len(new_statements) or statement_ids & new_statement_ids:
    raise SystemExit("duplicate statement ID")

coverage_by_id[P247].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L27-36",
    "note": "Printed p.247 (CHP-9.pdf physical p.5) reviewed against the page image. The main text at L31 ends 'and may' and continues at p.248 L39, so this segment remains partial pending that continuation. L32-34 are the page-end continuation of p.246 note 4, linked to consolidated notes L331; L35-36 are an unnumbered note-like passage quoting Paolo Renier, with its missing marker preserved as unresolved. Numbered notes 1-3 are represented in the separate notes segment L332-334 and remain queued for that segment's review."
})

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
print(json.dumps({
    "segment": P247, "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage": [coverage_by_id[P247]["disposition"], coverage_by_id[P247]["migration_status"]],
    "cross_page_continuation": f"{P247} L31 -> {P248} L39",
    "footnote_continuation": f"{P247} L32-34 -> {NOTES} L331",
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
