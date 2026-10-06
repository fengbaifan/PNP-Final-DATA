"""Controlled S2 migration for printed p.306; dry-run unless --apply."""
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
P305 = "chp-10:10_CHP-10_intro:l423-433"
P306 = "chp-10:10_CHP-10_intro:l435-443"
P307 = "chp-10:10_CHP-10_intro:l445-454"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "bcb35c916a114107fcee2fc774eb7c946773e3202b6f2265207b1fd083471a8a"
BACKUP = ".bak-s2-chp10-p306-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
first, last, PAGE, PHYSICAL = 435, 443, 306, 35
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[434].strip() != "[Page 306]" or "Aesculapio" not in body:
    raise SystemExit(f"p.306 source segment mismatch: {digest}")
line_offsets, offset = {}, 0
for line_no in range(first, last + 1):
    line_offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9222:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P305, ("reviewed", "partial")), (P306, ("queued", "pending")),
                      (P307, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P306 for row in mentions) or any(row["segment_id"] == P306 for row in statements):
    raise SystemExit("p.306 already has mention or statement rows")

E = {
    "smith": "cand-2440", "canaletto": "cand-0514", "ricci": "cand-2154",
    "gori": "cand-1214", "pasquali": "cand-1844", "visentini": "cand-2783",
    "girolamo_zanetti": "cand-2861", "antonio_zanetti": "cand-2838",
    "breval": "cand-0451",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("smith_old_masters", "Old-master works Joseph Smith was buying during this period", "work",
     "Haskell says Smith was probably buying old masters extensively; individual paintings are not identified in this passage.", 437),
    ("smith_drawings", "Joseph Smith’s large collection of drawings (collection type unresolved)", "",
     "Haskell says Smith was forming and adding to a large drawing collection; much of Sebastiano Ricci’s studio contents may have entered it around 1734.", 437),
    ("ricci_studio_contents", "Much of Sebastiano Ricci’s studio contents probably acquired by Joseph Smith", "",
     "Haskell says Smith probably acquired much of the studio contents after Ricci’s death in 1734; this is a qualified acquisition claim, not an inventory.", 437),
    ("pasquali_illustrated_editions", "Unidentified illustrated book editions published by Giambattista Pasquali during Smith’s collecting years", "archive",
     "The editions are unnamed here; Smith retained original drawings, most attributed by Haskell to Visentini.", 437),
    ("visentini_original_drawings", "Original drawings retained by Joseph Smith for illustrated books, mostly by Antonio Visentini", "work",
     "A group of drawings associated with Pasquali’s illustrated editions; individual books and drawings are not identified in this passage.", 437),
    ("smith_gems_cameos", "Gems and cameos collected by Joseph Smith", "work",
     "A body of carved stones and cameos discussed through Smith’s correspondence and reported judgments; individual pieces remain unidentified here.", 438),
    ("smith_gori_correspondence", "Joseph Smith’s 1737–1738 correspondence with A. F. Gori about gems and cameos", "archive",
     "Haskell says these letters provide the only explicit indication of Smith’s artistic tastes; exact letter records and quotations are pending in the consolidated notes.", 438),
    ("breval_statuette", "Unidentified statuette shown to John Breval in Joseph Smith’s collection", "work",
     "The p.306–307 continuation describes it as seemingly an Aesculapius/Priapus figure; preserve the unresolved identification and proportions until the next page is processed.", 441),
]
newc, C = [], {}
for i, (key, name, kind, detail, line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{i:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                 "index_page_range": "", "suggested_type": kind, "status": "open",
                 "index_source_file": "", "sub_entry": "", "detail": detail,
                 "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{P306}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p306-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start = line_offsets[line]
    line_end = line_start + len(src[line - 1])
    positions, at = [], line_start
    while True:
        at = body.find(surface, at)
        if at < 0 or at + len(surface) > line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": P306, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("canaletto-style-close", 436, "whom the English have spoilt", E["canaletto"], "Closes p.305’s style evaluation of Canaletto."),
    ("smith-buying-old-masters", 437, "Smith", E["smith"]),
    ("old-masters", 437, "old masters", C["smith_old_masters"], "Describes Smith’s purchases during this period."),
    ("smith-drawing-collection", 437, "great collection of drawings", C["smith_drawings"]),
    ("ricci-death", 437, "Sebastiano Ricci", E["ricci"]),
    ("ricci-studio", 437, "his studio", C["ricci_studio_contents"], "Corefers to Sebastiano Ricci."),
    ("pasquali", 437, "Pasquali", E["pasquali"]),
    ("illustrated-editions", 437, "Many illustrated editions of books", C["pasquali_illustrated_editions"]),
    ("smith-retained-drawings", 437, "Smith retained", E["smith"]),
    ("original-drawings", 437, "original drawings", C["visentini_original_drawings"]),
    ("visentini", 437, "Visentini", E["visentini"]),
    ("smith-gems-cameos", 438, "gems and cameos", C["smith_gems_cameos"]),
    ("gori", 438, "A. F. Gori", E["gori"]),
    ("smith-gori-letters", 438, "many letters that he wrote about these", C["smith_gori_correspondence"], "Corefers to Smith’s letters about the gems and cameos."),
    ("smith-artistic-tastes", 438, "his artistic tastes", E["smith"]),
    ("smith-collector", 438, "He emerges as an enthusiastic and apparently discriminating collector", E["smith"], "Haskell’s qualified characterization of Smith."),
    ("smith-quote-speaker", 438, "he writes", E["smith"]),
    ("smith-quote-stones", 439, "I do like modern things", C["smith_gems_cameos"], "Direct quotation attributed by Haskell to Smith; concerns his stated preferences."),
    ("smith-gems-praise", 439, "Smith’s choice of stones", E["smith"]),
    ("dealers", 439, "dealers of the time", C["smith_gems_cameos"], "Unnamed group said to praise Smith’s selection."),
    ("girolamo-zanetti", 439, "Girolamo", E["girolamo_zanetti"], "Name continues as Zanetti at the start of p.306 L440."),
    ("zanetti", 440, "Zanetti", E["girolamo_zanetti"], "Girolamo Zanetti is the speaker of the reported criticism."),
    ("antonio-maria", 440, "Antonio Maria", E["antonio_zanetti"], "Girolamo Zanetti’s brother."),
    ("smith-gems-copied", 440, "Smith’s gems", C["smith_gems_cameos"]),
    ("consul-antiques", 440, "the Consul’s ‘antiques’", E["smith"], "The term is quoted and the quality/authenticity is disputed in the reported account."),
    ("smith-distinguishing", 440, "Smith always showed himself careful", E["smith"]),
    ("john-breval", 441, "John Breval", E["breval"]),
    ("breval-collection", 441, "Smith’s collection", E["smith"]),
    ("statuette", 441, "a little statuette", C["breval_statuette"]),
    ("aesculapio-description", 441, "Aesculapio", C["breval_statuette"], "The identification continues on p.307 with a Priapus description; do not resolve it on this page."),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p306-{local}"
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    mentioned = []
    for mention in newm:
        start = int(mention["start_char"])
        line_no = max((n for n, off in line_offsets.items() if off <= start), default=first)
        if lo <= line_no <= hi and mention["candidate_id"] not in mentioned:
            mentioned.append(mention["candidate_id"])
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": PAGE,
                  "pdf_physical_page": PHYSICAL, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        page_map = {P305: 305, P307: 307}
        pages = [page_map[item] for item in cross if item in page_map]
        if pages:
            qualifiers["cross_reference_printed_pages"] = pages
    new_s.append({"statement_id": sid, "segment_id": P306, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("canaletto-spoilt-style", 436, 436, E["canaletto"], None, "later_style_deterioration",
      "Haskell completes his description of mannerisms, harshness and studio assistance as a deterioration characteristic of a painter ‘whom the English have spoilt’.",
      "This is Haskell’s evaluative formulation and the completion of p.305 L433.", cross=[P305], layer="authorial interpretation")
add_s("smith-bought-old-masters", 437, 437, E["smith"], C["smith_old_masters"],
      "probably_bought_old_masters_extensively",
      "Haskell says Smith was probably buying old masters extensively during this period.",
      "Explicitly probable; the individual paintings are not identified.", relation=True, footnote=1, layer="authorial inference")
add_s("smith-formed-drawing-collection", 437, 437, E["smith"], C["smith_drawings"],
      "formed_and_added_to_large_drawing_collection",
      "Haskell says Smith must also have been forming and adding to his large collection of drawings.",
      "Haskell’s inference; no inventory is supplied.", relation=True, footnote=1, layer="authorial inference")
add_s("smith-acquired-ricci-studio", 437, 437, E["smith"], C["ricci_studio_contents"],
      "probably_acquired_much_of_ricci_studio_after_1734_death",
      "After Sebastiano Ricci died in 1734, Smith probably acquired much of the contents of Ricci’s studio.",
      "Explicitly probable and not an inventory; compare the earlier p.302–303 acquisition hypothesis without assuming identical scope.", relation=True, footnote=1, layer="authorial hypothesis")
add_s("pasquali-visentini-drawings", 437, 437, E["smith"], C["visentini_original_drawings"],
      "retained_original_drawings_mostly_by_visentini_for_pasquali_illustrated_editions",
      "Pasquali published many illustrated book editions during these years; Smith retained the original drawings, most of which were by Visentini.",
      "The books and drawings are not individually identified; footnote 1 remains pending.", relation=True, footnote=1)
add_s("smith-gems-correspondence", 438, 438, E["smith"], C["smith_gems_cameos"],
      "bought_gems_and_cameos_and_corresponded_with_gori_in_1737_1738",
      "Smith bought gems and cameos; letters he wrote about them to the Florentine antiquary A. F. Gori in 1737 and 1738 provide Haskell’s only explicit indication of Smith’s artistic tastes.",
      "The exact letters and their textual context remain pending in the consolidated notes; Haskell calls Smith an apparently discriminating collector.", relation=True, footnote=2)
add_s("smith-stated-artistic-preferences", 438, 439, E["smith"], C["smith_gems_cameos"],
      "preferred_excellent_workmanship_and_gave_preference_to_antique",
      "In a quotation attributed to Smith, he says workmanship matters more than the stone’s material or relief format, prefers the antique while allowing for exceptionally beautiful modern works, and is willing to pay what beautiful objects are worth.",
      "This is Smith’s self-description as quoted through Haskell; source and translation remain pending in footnote 3.", relation=True, footnote=3,
      layer="nested correspondence quotation", speaker="Joseph Smith as quoted by Haskell")
add_s("praise-and-contested-taste", 439, 439, E["smith"], C["smith_gems_cameos"],
      "dealers_praised_stones_but_generosity_and_taste_were_not_universally_acknowledged",
      "Many people, including dealers, praised Smith’s choice of stones, but not everyone accepted his claims of generosity or taste.",
      "Haskell reports disagreement; do not resolve it into a single objective judgment.", footnote=4, layer="authorial interpretation")
add_s("zanetti-criticism-of-gems", 439, 440, E["girolamo_zanetti"], E["antonio_zanetti"],
      "reported_brother_copied_smith_gems_badly_paid_and_criticized_antique_quality",
      "Girolamo Zanetti said his brother Antonio Maria copied Smith’s gems for publication and was badly paid; Girolamo also criticized the quality and authenticity of many of the Consul’s antiques.",
      "This is a reported criticism, not an independent finding; the letter and note 5 are pending.", relation=True, footnote=5, layer="reported criticism")
add_s("smith-distinguished-antique-art", 440, 440, E["smith"], C["smith_gems_cameos"],
      "distinguished_excellent_sixteenth_century_works_from_recent_production",
      "Haskell says Smith carefully distinguished excellent works made in the sixteenth century, when fine masters were alive, from more recent production.",
      "The source passage presents this as Smith’s careful distinction; the corresponding letter is pending in footnote 6.", relation=True, footnote=6,
      layer="authorial narrative")
add_s("breval-statuette", 441, 441, E["breval"], C["breval_statuette"],
      "visited_smith_collection_and_saw_statuette_described_as_seemingly_aesculapius",
      "John Breval visited Smith’s collection and was shown a small statuette described as seemingly an Aesculapius figure.",
      "The quotation and description continue on p.307, where Priapus is named; keep the identification unresolved until that page is read.", relation=True,
      footnote=1, cross=[P307], layer="reported observation")

all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.306: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if not q["mentioned_candidate_ids"]:
        raise SystemExit(f"statement has no anchored mention: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

cov[P305]["note"] = cov[P305]["note"].replace(
    "L433 continues on p.306, so p.305 remains partial.",
    "p.306 closes L433’s style-evaluation sentence; p.305 footnote markers remain to reconcile in the consolidated notes segment, so p.305 remains partial.")
cov[P306].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L436-441",
    "note": "Printed p.306 body checked against CHP-10.pdf physical page 35. Closed p.305’s Canaletto style sentence; recorded Smith’s uncertain activity, old-master purchases, drawing collection, likely acquisition of much of Sebastiano Ricci’s studio after 1734, Pasquali’s illustrated editions and Visentini originals; Smith’s gems/cameos and 1737–38 letters to A. F. Gori; Smith’s qualified collector self-description and quoted preferences; praise and contrary dealer/antiquary judgments; and John Breval’s visit and statuette description. The statuette’s identity continues as Priapus on p.307 and remains unresolved. Page-body footnote excerpts at L442–443 duplicate the consolidated notes source and are deferred; footnotes 1–6 remain pending. OCR source quote “charactèristic” is visibly printed as “characteristic”; S2 records the correction without changing S0. L441’s quoted statue description continues on p.307, so p.306 remains partial."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P306, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "coverage": {"p305": cov[P305]["migration_status"], "p306": cov[P306]["migration_status"],
                        "p307": cov[P307]["migration_status"]}}
print(json.dumps(summary, ensure_ascii=False, indent=2))
if sys.argv[-1:] == ["--apply"]:
    for path in (cp, mp, sp, vp):
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + newc)
    write_csv(mp, mf, mentions + newm)
    write_jsonl(sp, statements + new_s)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied p.306 S2 body migration; page-note excerpts remain with the consolidated notes segment.")
