"""Controlled, source-locked semantic re-audit of printed p.369 and notes 1-4."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BODY = "chp-15:15_CHP-15_sec_ii:l49-59"
NOTES = "chp-15:15_CHP-15_sec_ii:l90-113"
INPUT_SHA = {
    "entity-candidates.csv": "9507b95c16d83f7a48158967135a899114163ffb6dfac35daa3686f60f7098c8",
    "mentions.csv": "8c240970e0c96e2c6c956103e7a0e4843de47daede960ae9ead2b843288ee4d0",
    "book-statements.jsonl": "c1d20146c899d7095a6d92a1a096fb0ebb318f662cf6632ddc98d8c80c8845d9",
}
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
BACKUP_SUFFIX = ".bak-s2-chp15-p369-semantic-reaudit-20261009"
NEW_CANDIDATE = "cand-11535"
NEW_MENTIONS = ("m-chp15-p369-querini-0054", "m-chp15-p369-querini-0055")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed p.369 S2 changes")
args = parser.parse_args()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if sha256(SOURCE) != SOURCE_SHA or sha256(PDF) != PDF_SHA:
    raise SystemExit("p.369 S0 source or registered PDF changed")
paths = {name: TABLES / name for name in INPUT_SHA}
for name, expected in INPUT_SHA.items():
    if sha256(paths[name]) != expected:
        raise SystemExit(f"table changed since this re-audit was prepared: {name}")
for path in paths.values():
    if path.with_name(path.name + BACKUP_SUFFIX).exists():
        raise SystemExit(f"recovery copy already exists for {path.name}{BACKUP_SUFFIX}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
required = {
    50: ["It is doubtful how far", "the reforms he advocated", "the victory of the"],
    51: ["conservatives", "accouple of years", "After his release"],
    52: ["More and more he became involved", "dette pene", "visited Voltaire", "a medal he had had specially coined"],
    53: ["Girolamo Festari", "Most of his life was thereafter devoted", "a mile or two from Padua"],
    54: ["Giustiniana Wynne", "flirting with Consul Smith"],
    55: ["married the Austrian Ambassador", "company of the learned", "know most of Alticchiero"],
    56: ["philosophers, she explains", "hide themselves in modest retreats"],
    57: ["building is not sumptuous", "furniture lavish or choice", "arrangement is as simple", "busts of ancient and modern philosophers", "no dogs roam the grounds", "Alticchiero"],
    58: ["unique in Italy", "edifying even in Switzerland"],
    59: ["plans of the great European cities"],
    105: ["different pays", "2II"],
    108: ["Brunelh", "Heraclitus", "Democritus"],
}
for number, fragments in required.items():
    for fragment in fragments:
        if fragment.casefold() not in source_lines[number - 1].casefold():
            raise SystemExit(f"required source text changed at L{number}: {fragment}")

candidate_path = paths["entity-candidates.csv"]
mention_path = paths["mentions.csv"]
statement_path = paths["book-statements.jsonl"]
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
if NEW_CANDIDATE in candidate_by_id:
    raise SystemExit(f"candidate ID collision: {NEW_CANDIDATE}")
if any(mid in mention_by_id for mid in NEW_MENTIONS):
    raise SystemExit("mention ID collision")
if sum(row.get("segment_id") == BODY for row in statements) != 26:
    raise SystemExit("p.369 body statement count changed")
if sum(row.get("segment_id") == BODY for row in mentions) != 34:
    raise SystemExit("p.369 body mention count changed")
new_ids = {
    "st-chp15-p369-haskell-doubts-progressive-interpretation",
    "st-chp15-p369-reforms-not-fundamental-change",
    "st-chp15-p369-querini-intellectual-cultural-pursuits-after-release",
    "st-chp15-p369-querini-had-medal-coined",
    "st-chp15-p369-medal-depiction-and-lucretius-text",
    "st-chp15-p369-querini-festari-trip-observations",
    "st-chp15-p369-alticchiero-near-padua",
    "st-chp15-p369-houdon-bust-group-creator",
    "st-chp15-p369-furniture-not-lavish",
    "st-chp15-p369-arrangement-simple-convenient",
    "st-chp15-p369-alticchiero-no-dogs",
    "st-chp15-p369-wynne-trust-human-nature-alticchiero",
    "st-chp15-p369-alticchiero-edifying-in-switzerland",
}
if new_ids & set(statement_by_id):
    raise SystemExit("one or more planned statement IDs already exist")


def span_quote(line, start, end):
    text = source_lines[line - 1]
    left = text.index(start)
    right = text.index(end, left) + len(end)
    return text[left:right]


def lines_quote(first_line, start, last_line, end):
    first = source_lines[first_line - 1]
    last = source_lines[last_line - 1]
    left = first.index(start)
    right = last.index(end) + len(end)
    if first_line == last_line:
        return first[left:right]
    return "\n".join([first[left:], *source_lines[first_line:last_line - 1], last[:right]])


def ocr(line, original, printed):
    return {"source_file": SOURCE_FILE, "source_line": line, "ocr": original,
            "print": printed, "basis": "CHP-15.pdf physical page 9."}


def revise(sid, *, quote, start, end, claim, predicate=None, subject=None, object_id=None,
           mentioned=None, relation=None, relation_note=None, qualification=None, corrections=None,
           remove_keys=()):
    row = statement_by_id[sid]
    row["original_quote"] = quote
    if predicate is not None:
        row["predicate"] = predicate
    if subject is not None:
        row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_id
    q = row.setdefault("qualifiers", {})
    q.update({
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 369,
        "pdf_physical_page": 9,
        "claim": claim,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned or [])),
    })
    if qualification is not None:
        q["qualification"] = qualification
    if relation is True:
        q["relation_candidate"] = True
        q["relation_candidate_note"] = relation_note or "Source-bound S2 relation candidate; no S6 formal edge is created here."
    elif relation is False:
        q.pop("relation_candidate", None)
        q.pop("relation_candidate_note", None)
    if corrections is not None:
        if corrections:
            q["ocr_corrections"] = corrections
        else:
            q.pop("ocr_corrections", None)
    for key in remove_keys:
        q.pop(key, None)
    return row


def add_statement(sid, *, subject, predicate, object_id, quote, start, end, claim, mentioned,
                  relation=False, relation_note=None, qualification="", corrections=None):
    if sid in statement_by_id:
        raise SystemExit(f"statement ID collision: {sid}")
    q = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 369,
        "pdf_physical_page": 9,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "authorial report",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if relation:
        q["relation_candidate"] = True
        q["relation_candidate_note"] = relation_note or "Source-bound S2 relation candidate; no S6 formal edge is created here."
    if corrections:
        q["ocr_corrections"] = corrections
    row = {
        "statement_id": sid,
        "segment_id": BODY,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[sid] = row
    return row


def add_mention(mid, surface, cid, line, note_text):
    segment_lines = source_lines[48:59]
    segment_text = "\n".join(segment_lines)
    prefix = "\n".join(source_lines[48:line - 1])
    line_offset = len(prefix) + (1 if prefix else 0)
    start = segment_text.index(surface) if "\n" in surface else line_offset + source_lines[line - 1].index(surface)
    mentions.append({
        "mention_id": mid,
        "segment_id": BODY,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note_text,
    })


def add_candidate(cid, label, kind, detail, line_range):
    candidates.append({
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": label,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#{line_range}",
    })


# Split the interpretation of Querini's reforms from the prior-page continuation
# about reducing the State Inquisition's powers.
reform = revise(
    "st-chp15-p369-querini-reform-within-ruling-class",
    subject="cand-2075", object_id=None,
    predicate="haskell_describes_querini_reform_as_factional_balance_shift",
    quote=span_quote(50, "In fact, the reforms he advocated", "the substitution of one faction by another"),
    start=50, end=50,
    claim="Haskell interprets Querini's proposed reforms as shifting the balance of power within the ruling class from one faction to another.",
    mentioned=["cand-2075"],
    qualification="This does not identify the factions or imply a change in the ruling class as a whole.",
)
reform["qualifiers"]["cross_reference_segments"] = ["chp-15:15_CHP-15_sec_ii:l38-47"]
reform["qualifiers"]["cross_reference_text"] = "The preceding p.368 sentence says Querini wished to reduce the State Inquisition's powers; this p.369 sentence interprets those proposed reforms."
reform["qualifiers"]["cross_reference_text_pending"] = False
add_statement(
    "st-chp15-p369-haskell-doubts-progressive-interpretation",
    subject="cand-2075", predicate="haskell_doubts_reform_was_progressive", object_id=None,
    quote=span_quote(50, "It is doubtful how far", "progressive’ move."),
    start=50, end=50,
    claim="Haskell doubts that Querini's reform can be interpreted as progressive.",
    mentioned=["cand-2075"],
    qualification="This is Haskell's historiographical qualification, not a claim that Querini used this label.",
)
add_statement(
    "st-chp15-p369-reforms-not-fundamental-change",
    subject="cand-2075", predicate="proposed_reforms_did_not_involve_fundamental_change", object_id=None,
    quote=span_quote(50, "and in no way involved", "fundamental change."),
    start=50, end=50,
    claim="Haskell says the proposed reforms did not involve fundamental change.",
    mentioned=["cand-2075"],
)
revise(
    "st-chp15-p369-foscarini-victory-querini-arrest",
    subject=NEW_CANDIDATE, object_id="cand-2079",
    predicate="followed_by",
    quote=lines_quote(50, "the victory of the", 51, "for accouple of years."),
    start=50, end=51,
    claim="Haskell says the victory of the conservatives led by Marco Foscarini was followed by Querini's arrest and detention for a couple of years.",
    mentioned=[NEW_CANDIDATE, "cand-1053", "cand-2075", "cand-2079"],
    relation=True,
    relation_note="The source gives a sequence: the conservatives' victory was followed by Querini's arrest and detention. It does not say Foscarini personally ordered the arrest or that the victory caused it.",
    corrections=[ocr(51, "accouple", "a couple")],
)
revise(
    "st-chp15-p369-querini-withdrawal-from-active-politics",
    subject="cand-2075", object_id=None,
    predicate="after_release_left_active_politics",
    quote=span_quote(51, "After his release", "active politics"),
    start=51, end=51,
    claim="Haskell says Querini took no further part in active politics after his release.",
    mentioned=["cand-2075"],
)
add_statement(
    "st-chp15-p369-querini-intellectual-cultural-pursuits-after-release",
    subject="cand-2075", predicate="after_release_devoted_himself_to_intellectual_and_cultural_pursuits", object_id=None,
    quote=span_quote(51, "but devoted himself", "cultural pursuits."),
    start=51, end=51,
    claim="Haskell says that after his release Querini devoted himself to intellectual and cultural pursuits.",
    mentioned=["cand-2075"],
)
revise(
    "st-chp15-p369-querini-enlightenment-involvement",
    subject="cand-2075", object_id="cand-8107",
    quote=span_quote(52, "More and more", "Enlightenment."),
    start=52, end=52,
    claim="Haskell says Querini became increasingly involved with the forces of the Enlightenment.",
    mentioned=["cand-2075", "cand-8107"],
    qualification="This is Haskell's description of Querini's intellectual commitments.",
)
revise(
    "st-chp15-p369-querini-beccaria-authorship-rumour",
    subject="cand-2075", object_id="cand-9707",
    quote=span_quote(52, "In 1764 rumour credited him", "dette pene.1"),
    start=52, end=52,
    claim="Haskell reports a 1764 rumour crediting Querini with authorship of Beccaria's anonymously published Dei delitti e delle pene.",
    mentioned=["cand-2075", "cand-0265", "cand-9707"],
    relation=True,
    relation_note="This is explicitly a rumour, not an authorship finding.",
    corrections=[ocr(52, "dette pene", "delle pene")],
)
revise(
    "st-chp15-p369-querini-1777-switzerland-voltaire-visit",
    subject="cand-2075", object_id="cand-2791",
    quote=span_quote(52, "In 1777", "visited Voltaire.2"),
    start=52, end=52,
    claim="Haskell says Querini went to Switzerland and visited Voltaire in 1777.",
    mentioned=["cand-2075", "cand-10529", "cand-2791"],
    relation=True,
    relation_note="The source dates the visit to 1777; the separately described medal is not treated as part of the visit endpoint.",
)
revise(
    "st-chp15-p369-querini-medal-gift-to-voltaire",
    subject="cand-2075", object_id="cand-2791",
    quote=span_quote(52, "He presented the philosopher with a medal", "specially coined"),
    start=52, end=52,
    claim="Haskell says Querini presented Voltaire with a specially coined medal.",
    mentioned=["cand-2075", "cand-2791", "cand-10530"],
    relation=True,
    relation_note="The source directly reports presentation of the medal; no maker or mint is named.",
)
add_statement(
    "st-chp15-p369-querini-had-medal-coined",
    subject="cand-2075", predicate="had_specially_coined", object_id="cand-10530",
    quote=span_quote(52, "a medal he had had specially coined", "specially coined"),
    start=52, end=52,
    claim="Haskell says Querini had the medal specially coined.",
    mentioned=["cand-2075", "cand-10530"],
    relation=True,
    relation_note="The source supports Querini's commissioning role but names no medallist or mint.",
)
add_statement(
    "st-chp15-p369-medal-depiction-and-lucretius-text",
    subject="cand-10530", predicate="depicts_philosophy_destroying_superstition_with_text_attributed_to_lucretius",
    object_id="cand-10531",
    quote=span_quote(52, "depicting Philosophy", "exaequat victoria coelo."),
    start=52, end=52,
    claim="Haskell describes the medal as depicting Philosophy destroying Superstition and bearing a text attributed to Lucretius.",
    mentioned=["cand-10530", "cand-10531"],
    relation=True,
    relation_note="The source attributes the inscription to Lucretius but does not identify the specific work containing the text.",
)
revise(
    "st-chp15-p369-querini-festari-companion-trip",
    subject="cand-2075", object_id="cand-1032",
    quote=span_quote(53, "During the trip", "places they visited."),
    start=53, end=53,
    claim="Haskell identifies Girolamo Festari as Querini's companion during the trip.",
    mentioned=["cand-2075", "cand-1032"],
    relation=True,
    relation_note="This is companionship on the specific trip, not a broader or continuing relationship.",
)
add_statement(
    "st-chp15-p369-querini-festari-trip-observations",
    subject="cand-2075", predicate="during_trip_admired_art_and_architecture_and_commented_on_trade_and_industry",
    object_id="cand-1032",
    quote=span_quote(53, "stopped everywhere", "places they visited."),
    start=53, end=53,
    claim="Haskell says Querini and Festari repeatedly admired pictures and architecture and commented on local trade and industry during the trip.",
    mentioned=["cand-2075", "cand-1032"],
    qualification="The source says 'everywhere' but does not identify the places or individual works.",
)
revise(
    "st-chp15-p369-querini-alticchiero-building-decoration",
    subject="cand-2075", object_id="cand-0086",
    quote=span_quote(53, "Most of his life was thereafter devoted", "at Alticchiero"),
    start=53, end=53,
    claim="Haskell says Querini devoted most of his remaining life to building and decorating his country house at Alticchiero.",
    mentioned=["cand-2075", "cand-0086"],
    relation=True,
    relation_note="This is a source-bound claim about Querini's activity at the named house; no architect or exact construction date is inferred.",
)
add_statement(
    "st-chp15-p369-alticchiero-near-padua",
    subject="cand-0086", predicate="located_approximately_one_or_two_miles_from", object_id="cand-1803",
    quote=span_quote(53, "Alticchiero, a mile or two from Padua", "Padua."),
    start=53, end=53,
    claim="Haskell locates Alticchiero approximately one or two miles from Padua.",
    mentioned=["cand-0086", "cand-1803"],
    relation=True,
    relation_note="The distance is approximate as stated in the source.",
)
revise(
    "st-chp15-p369-querini-wynne-close-friendship",
    subject="cand-2075", object_id="cand-2824",
    quote=span_quote(54, "Among his closest friends", "Giustiniana Wynne"),
    start=54, end=54,
    claim="Haskell describes Giustiniana Wynne as one of Querini's closest friends.",
    mentioned=["cand-2075", "cand-2824"],
    relation=True,
    relation_note="This is Haskell's explicit description of friendship.",
)
revise(
    "st-chp15-p369-wynne-earlier-flirtation-smith",
    subject="cand-2824", object_id="cand-2440",
    quote=span_quote(54, "flirting with Consul Smith", "Consul Smith"),
    start=54, end=54,
    claim="Haskell recalls Wynne flirting with Consul Smith.",
    mentioned=["cand-2824", "cand-2440"],
    relation=True,
    relation_note="The wording reports flirtation only; it does not establish marriage or a sustained affair.",
)
revise(
    "st-chp15-p369-wynne-earlier-flirtation-memmo",
    subject="cand-2824", object_id="cand-1642",
    quote=lines_quote(54, "and the young", 55, "Andrea Memmo"),
    start=54, end=55,
    claim="Haskell recalls Wynne flirting with the young Andrea Memmo.",
    mentioned=["cand-2824", "cand-1642"],
    relation=True,
    relation_note="The wording reports flirtation only; it does not establish marriage or a sustained affair.",
)
revise(
    "st-chp15-p369-wynne-links-three-patrons",
    subject="cand-2824", object_id="cand-2075",
    quote=span_quote(55, "This strange woman", "significant patrons,"),
    start=55, end=55,
    claim="Haskell says Wynne links Querini, Consul Smith, and Andrea Memmo as three significant patrons.",
    mentioned=["cand-2824", "cand-2075", "cand-2440", "cand-1642"],
    qualification="This is Haskell's interpretive grouping and does not imply that all three had the same relationship with Wynne.",
)
revise(
    "st-chp15-p369-wynne-marriage-rosenberg-1762",
    subject="cand-2824", object_id="cand-2259",
    quote=span_quote(55, "had in 1762 married", "Count Rosenberg"),
    start=55, end=55,
    claim="Haskell says Giustiniana Wynne married Count Rosenberg, the Austrian Ambassador, in 1762.",
    mentioned=["cand-2824", "cand-2259"],
    relation=True,
    relation_note="The title and identity are reported by Haskell; note 3 preserves a separate quoted comparison by de Bernis.",
)
revise(
    "st-chp15-p369-wynne-interest-in-learned-company",
    subject="cand-2824", object_id=None,
    quote=span_quote(55, "but her main interest in life", "company of the learned"),
    start=55, end=55,
    claim="Haskell says Wynne's main interest remained the company of learned people.",
    mentioned=["cand-2824"],
)
revise(
    "st-chp15-p369-haskell-rosenberg-hardly-aspired-to-learned-company",
    subject="cand-2259", object_id=None,
    quote=span_quote(55, "a condition to which her husband", "hardly aspired.3"),
    start=55, end=55,
    claim="Haskell says Count Rosenberg hardly aspired to the company of learned people.",
    mentioned=["cand-2259"],
    qualification="This is Haskell's characterization, not a self-description by Rosenberg.",
)
revise(
    "st-chp15-p369-wynne-account-source-for-alticchiero",
    subject="cand-2824", object_id="cand-0086",
    quote=span_quote(55, "It is from her rapturous account", "razed to the ground.4"),
    start=55, end=55,
    claim="Haskell says Wynne's account is the main source for his description of Alticchiero, which had already been razed.",
    mentioned=["cand-2824", "cand-0086"],
    qualification="This is a statement about Haskell's source base; Wynne's 1787 publication was not independently consulted here.",
)
revise(
    "st-chp15-p369-wynne-philosophers-modest-retreats",
    subject="cand-2824", object_id="cand-0086",
    quote=span_quote(56, "The aim of the house", "modest retreats."),
    start=56, end=56,
    claim="Haskell says Wynne's opening remarks contrast philosophers' modest retreats with grand palaces and pleasurable retreats.",
    mentioned=["cand-2824", "cand-0086"],
)
revise(
    "st-chp15-p369-alticchiero-simple-convenient-furnishings",
    subject="cand-0086", object_id=None,
    predicate="building_described_as_not_sumptuous",
    quote=span_quote(57, "the building is not sumptuous", "sumptuous,"),
    start=57, end=57,
    claim="In Wynne's quoted description, the building is not sumptuous.",
    mentioned=["cand-0086", "cand-2824"],
)
add_statement(
    "st-chp15-p369-furniture-not-lavish",
    subject="cand-0086", predicate="furniture_described_as_not_lavish_or_choice", object_id=None,
    quote=span_quote(57, "nor is the furniture", "choice;"),
    start=57, end=57,
    claim="In Wynne's quoted description, the furniture is neither lavish nor choice.",
    mentioned=["cand-0086", "cand-2824"],
)
add_statement(
    "st-chp15-p369-arrangement-simple-convenient",
    subject="cand-0086", predicate="arrangement_described_as_simple_and_convenient", object_id=None,
    quote=span_quote(57, "the arrangement is as simple", "possible’"),
    start=57, end=57,
    claim="In Wynne's quoted description, the arrangement is as simple and convenient as possible.",
    mentioned=["cand-0086", "cand-2824"],
)
revise(
    "st-chp15-p369-alticchiero-houdon-philosopher-busts",
    subject="cand-10541", object_id="cand-0086",
    predicate="located_on_tables_at",
    quote=span_quote(57, "On the tables are busts", "Voltaire and Rousseau"),
    start=57, end=57,
    claim="Haskell says busts of ancient and modern philosophers, including Voltaire and Rousseau, stood on tables at Alticchiero.",
    mentioned=["cand-0086", "cand-10541", "cand-2791", "cand-2289"],
    relation=True,
    relation_note="This records the reported placement of the described bust group; it does not identify each bust as a separately catalogued work.",
)
add_statement(
    "st-chp15-p369-houdon-bust-group-creator",
    subject="cand-10541", predicate="attributed_to", object_id="cand-1305",
    quote=span_quote(57, "Voltaire and Rousseau by Houdon", "Houdon"),
    start=57, end=57,
    claim="Haskell attributes the Voltaire and Rousseau busts to Houdon.",
    mentioned=["cand-10541", "cand-2791", "cand-2289", "cand-1305"],
    relation=True,
    relation_note="The source attributes the group of busts to Houdon; individual object identities are not supplied.",
)
revise(
    "st-chp15-p369-voltaire-influence-alticchiero",
    subject="cand-2791", object_id="cand-0086",
    quote=span_quote(57, "the influence of both men", "villa and gardens."),
    start=57, end=57,
    claim="Haskell says Voltaire's influence was felt throughout Alticchiero's villa and gardens.",
    mentioned=["cand-2791", "cand-0086"],
    relation=True,
    relation_note="This is Haskell's reported intellectual influence, not a claim that Voltaire designed or visited the villa.",
)
revise(
    "st-chp15-p369-rousseau-influence-alticchiero",
    subject="cand-2289", object_id="cand-0086",
    quote=span_quote(57, "the influence of both men", "villa and gardens."),
    start=57, end=57,
    claim="Haskell says Rousseau's influence was felt throughout Alticchiero's villa and gardens.",
    mentioned=["cand-2289", "cand-0086"],
    relation=True,
    relation_note="This is Haskell's reported intellectual influence, not a claim that Rousseau designed or visited the villa.",
)
revise(
    "st-chp15-p369-alticchiero-no-theft-precautions",
    subject="cand-0086", object_id=None,
    predicate="no_locks_reported_at_alticchiero",
    quote=span_quote(57, "nothing is locked up", "locked up"),
    start=57, end=57,
    claim="Haskell reports that nothing was locked up at Alticchiero.",
    mentioned=["cand-0086"],
)
add_statement(
    "st-chp15-p369-alticchiero-no-dogs",
    subject="cand-0086", predicate="no_guard_dogs_reported_at_alticchiero", object_id=None,
    quote=span_quote(57, "no dogs roam the grounds", "grounds"),
    start=57, end=57,
    claim="Haskell reports that no dogs roamed the grounds at Alticchiero.",
    mentioned=["cand-0086"],
)
revise(
    "st-chp15-p369-wynne-trust-human-nature-tahiti-alticchiero",
    subject="cand-2824", object_id="cand-10543",
    predicate="wynne_reported_trust_in_human_nature_at_tahiti",
    quote=span_quote(57, "Only at Tahiti", "found."),
    start=57, end=57,
    claim="Haskell reports Mme Rosenberg's exclamation that trust in human nature could be found at Tahiti.",
    mentioned=["cand-2824", "cand-10543", "cand-0086"],
    qualification="The source names both Tahiti and Alticchiero; a separate claim below records Alticchiero. This is reported speech, not an independently verified comparison.",
)
add_statement(
    "st-chp15-p369-wynne-trust-human-nature-alticchiero",
    subject="cand-2824", predicate="wynne_reported_trust_in_human_nature_at_alticchiero", object_id="cand-0086",
    quote=span_quote(57, "Only at Tahiti", "found."),
    start=57, end=57,
    claim="Haskell reports Mme Rosenberg's exclamation that trust in human nature could also be found at Alticchiero.",
    mentioned=["cand-2824", "cand-10543", "cand-0086"],
    qualification="This is reported speech, not an independently verified comparison.",
)
revise(
    "st-chp15-p369-haskell-alticchiero-unique-and-edifying",
    subject="cand-0086", object_id=None,
    predicate="haskell_calls_alticchiero_unique_in_italy",
    quote=span_quote(58, "Certainly it is unique", "Italy,"),
    start=58, end=58,
    claim="Haskell calls Alticchiero unique in Italy.",
    mentioned=["cand-0086", "cand-3461"],
)
add_statement(
    "st-chp15-p369-alticchiero-edifying-in-switzerland",
    subject="cand-0086", predicate="haskell_says_alticchiero_would_be_edifying_even_in_switzerland", object_id=None,
    quote=span_quote(58, "would be edifying", "Switzerland."),
    start=58, end=58,
    claim="Haskell says Alticchiero would be edifying even in Switzerland.",
    mentioned=["cand-0086", "cand-10529"],
)
revise(
    "st-chp15-p369-alticchiero-european-city-plans-partial",
    subject="cand-10542", object_id="cand-0086",
    predicate="displayed_on_walls_in_rooms_of",
    quote=span_quote(59, "On the walls of the various rooms", "cities"),
    start=59, end=59,
    claim="Haskell reports that plans of major European cities were displayed on the walls of rooms at Alticchiero.",
    mentioned=["cand-10542", "cand-0086"],
    relation=True,
    relation_note="This statement records the p.369 placement of the city plans. The separate p.370 statement records the bathroom's Piranesi prints.",
    remove_keys=("cross_reference_segments", "cross_reference_text", "cross_reference_text_pending", "predicate_status"),
)

# Keep OCR readings on the statements that actually contain those source lines.
note1 = statement_by_id["st-chp15-p369-note1-anonymous-voyages-rumour-source"]
note1["qualifiers"]["ocr_corrections"] = [ocr(105, "different", "differens"), ocr(105, "2II", "211")]
note4 = statement_by_id["st-chp15-p369-note4-brunelli-article"]
note4["qualifiers"]["ocr_corrections"] = [ocr(108, "Brunelh", "Brunelli")]

add_candidate(
    NEW_CANDIDATE,
    "Conservative faction victory in the Venetian constitutional crisis of 1761",
    "event",
    "Haskell says the conservatives led by Marco Foscarini won the political contest, followed by Querini's arrest and detention. The event is distinct from Foscarini as a person; the source does not say he personally ordered the arrest or caused it.",
    "L50",
)
add_mention(
    NEW_MENTIONS[0], "victory of the\n‘conservatives’", NEW_CANDIDATE, 50,
    "Event mention. Marco Foscarini is separately named as leader; no individual sole responsibility for the arrest is inferred."
)
add_mention(
    NEW_MENTIONS[1], "Alticchiero", "cand-0086", 57,
    "Second mention of the house in Mme Rosenberg's reported comparison of Tahiti and Alticchiero."
)

candidate_ids = {row["candidate_id"] for row in candidates}
statement_ids = {row["statement_id"] for row in statements}
mention_ids = {row["mention_id"] for row in mentions}
if len(candidate_ids) != len(candidates) or len(statement_ids) != len(statements) or len(mention_ids) != len(mentions):
    raise SystemExit("duplicate IDs found after planned transformations")
for row in statements:
    if row.get("segment_id") not in (BODY, NOTES):
        continue
    q = row.get("qualifiers") or {}
    start, end = q.get("source_line_start"), q.get("source_line_end")
    if not start or not end:
        raise SystemExit(f"missing source line anchor: {row['statement_id']}")
    cited = "\n".join(source_lines[int(start) - 1:int(end)])
    if " ".join((row.get("original_quote") or "").split()) not in " ".join(cited.split()):
        raise SystemExit(f"quote does not match source lines: {row['statement_id']}")
    for cid in [row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])]:
        if cid and cid not in candidate_ids:
            raise SystemExit(f"dangling candidate reference: {row['statement_id']} -> {cid}")
for row in mentions:
    if row.get("segment_id") != BODY:
        continue
    segment_text = "\n".join(source_lines[48:59])
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
for row in mentions:
    if row.get("candidate_id") and row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"dangling mention candidate: {row['mention_id']} -> {row['candidate_id']}")

page_rows = [row for row in statements if row.get("segment_id") == BODY]
page_mentions = [row for row in mentions if row.get("segment_id") == BODY]
page_relations = [row for row in page_rows if (row.get("qualifiers") or {}).get("relation_candidate") is True]
open_relations = [row for row in page_relations if not row.get("subject_candidate_id") or not row.get("object_candidate_id")]
print(f"p369 body statements: {len(page_rows)}; body mentions: {len(page_mentions)}")
print(f"new candidates: 1; new statements: {len(statement_ids) - len(read_jsonl(statement_path))}; new mentions: 2")
print(f"p369 relation candidates: {len(page_relations)} (open endpoints {len(open_relations)})")
print("source quotes, mention spans, candidate references and p369 page-scan corrections: preflight passed")
print("changes: atomize and correct p369 claims; keep distinct events/persons, route OCR corrections to their own statements, separate p370 bathroom-print claim")

if args.apply:
    for path in paths.values():
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    for name, path in paths.items():
        print(f"{name} sha256={sha256(path)}")
    print("applied; recovery copies saved with", BACKUP_SUFFIX)
else:
    print("dry-run only; no table was written")
