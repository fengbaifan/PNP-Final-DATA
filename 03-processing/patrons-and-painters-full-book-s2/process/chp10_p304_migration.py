"""Controlled S2 migration for printed p.304; dry-run unless --apply."""
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
P303 = "chp-10:10_CHP-10_intro:l402-409"
P304 = "chp-10:10_CHP-10_intro:l411-421"
P305 = "chp-10:10_CHP-10_intro:l423-433"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "b5de1a06fe3c99db95c9cc9769167c842113032386060f53857acd55ef64b7e5"
BACKUP = ".bak-s2-chp10-p304-20261002"


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
first, last, PAGE, PHYSICAL = 411, 421, 304, 33
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[410].strip() != "[Page 304]" or "settled on arrival" not in body:
    raise SystemExit(f"p.304 source segment mismatch: {digest}")
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
if maximum != 9206:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P303, ("reviewed", "partial")), (P304, ("queued", "pending")),
                      (P305, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P304 for row in mentions) or any(row["segment_id"] == P304 for row in statements):
    raise SystemExit("p.304 already has mention or statement rows")

E = {
    "smith": "cand-2440", "gerolamo_canal": "cand-0496", "procuratore": "cand-8449",
    "canaletto": "cand-0514", "carriera": "cand-0581", "cignani": "cand-0748",
    "piazzetta": "cand-1901", "marco_ricci": "cand-2149", "sebastiano_ricci": "cand-2154",
    "tessin": "cand-2552", "royal_collection": "cand-2292", "venice": "cand-3401",
    "palazzo_balbi": "cand-2464", "england": "cand-8983",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("smith_country_house", "Country house at Mogliano acquired by Joseph Smith in 1731", "place",
     "Smith leased the house from Gerolamo Canal around 1727 and bought it in 1731; the exact building identity is not supplied.", 412),
    ("mogliano", "Mogliano near Treviso", "place",
     "Named location of Smith’s country house; the passage gives Treviso as a nearby locator.", 412),
    ("treviso", "Treviso", "place",
     "Geographic locator for Mogliano in the p.304 account.", 412),
    ("smith_venice_collection", "Joseph Smith’s Venetian collection of modern art and old masters (collection type unresolved)", "",
     "A body of paintings and drawings displayed in Smith’s Palazzo Balbi and country house; do not force the collection into a work/archive type.", 413),
    ("smith_taste_shift", "Joseph Smith’s shift from large-scale history pictures toward views and landscapes", "term",
     "Haskell relates Smith’s change in collecting direction to a concurrent English shift while qualifying that the parallel may have been conscious or not; portraiture is explicitly excluded for Smith.", 413),
    ("smith_canaletto_holdings", "Canaletto pictures obtained by Joseph Smith for his own collection", "work",
     "A group of Canaletto works kept by Smith; the passage distinguishes these from pictures he obtained for other customers.", 417),
    ("smith_1729_letter", "Unidentified letter by Joseph Smith quoting a 1729 quarrel with a painter", "archive",
     "The p.304 passage quotes Smith after a brush with a painter in 1729; footnote 5, still pending in the consolidated notes segment, will clarify the letter’s date and recipient.", 418),
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
                 "candidate_source_ref": f"{P304}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p304-{local}"
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
    newm.append({"mention_id": mid, "segment_id": P304, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("smith-settled", 412, "settled on arrival", E["smith"], "Closes p.303’s sentence about Smith’s residence at the Palazzo Balbi."),
    ("smith-bought-house", 412, "he bought", E["smith"]),
    ("country-house", 412, "country house", C["smith_country_house"]),
    ("mogliano", 412, "Mogliano", C["mogliano"]),
    ("treviso", 412, "Treviso", C["treviso"]),
    ("smith-leased-house", 412, "he had leased", E["smith"]),
    ("procuratore-office", 412, "Procuratore di San Marco", E["procuratore"], "Formal office held by Gerolamo Canal in this account."),
    ("gerolamo", 412, "Gerolamo", E["gerolamo_canal"], "Personal name continues as Canal at the start of p.304 L413."),
    ("canal", 413, "Canal", E["gerolamo_canal"], "Continuation of the line-break name Gerolamo Canal."),
    ("sebastiano", 413, "Sebastiano", E["sebastiano_ricci"]),
    ("marco", 413, "Marco Ricci", E["marco_ricci"]),
    ("cignani", 413, "Carlo Cignani", E["cignani"]),
    ("carriera", 413, "Rosalba Carriera", E["carriera"]),
    ("piazzetta", 413, "Piazzetta", E["piazzetta"], "Haskell says probably also; Smith was in touch with him."),
    ("smith-contact-piazzetta", 413, "he was in touch", E["smith"], "Corefers to Smith."),
    ("venice", 413, "Venice", E["venice"]),
    ("modern-art-collection", 413, "collection of modern art", C["smith_venice_collection"]),
    ("old-masters", 413, "old masters", C["smith_venice_collection"], "Part of the same growing collection; the line distinguishes these from modern works."),
    ("smith-palace", 413, "his palace", E["palazzo_balbi"], "Index cue points to Palazzo Balbi; alignment remains for S3."),
    ("smith-started-collecting", 413, "Smith began to accumulate", E["smith"]),
    ("individual-taste", 413, "individual taste", C["smith_taste_shift"]),
    ("taste-shift", 413, "a move away from large-scale history pictures towards views and landscapes", C["smith_taste_shift"]),
    ("england", 413, "England", E["england"]),
    ("smith-portraits-artists", 413, "he was anxious to have portraits", E["smith"]),
    ("canaletto", 415, "Canaletto", E["canaletto"]),
    ("smith-patronage", 414, "his patronage", E["smith"], "The possessive refers to Smith."),
    ("smith-canaletto-relations", 415, "the relations between the two men", E["canaletto"], "The two men are Smith and Canaletto; the relation candidate is explicitly described as central to both careers."),
    ("canaletto-contact", 416, "Canaletto", E["canaletto"]),
    ("smith-contact-date", 416, "Smith", E["smith"]),
    ("canaletto-output", 417, "his whole output", E["canaletto"], "Corefers to Canaletto’s output."),
    ("english-channels", 417, "English channels", E["england"], "Destination/context for Canaletto’s commissions; retain that Haskell says almost entirely."),
    ("smith-own-holdings", 417, "his own collection", C["smith_canaletto_holdings"], "Smith’s personal holdings of Canaletto pictures."),
    ("smith-control", 417, "Smith’s control", E["smith"]),
    ("canaletto-artist", 417, "the artist", E["canaletto"]),
    ("canaletto-works", 417, "his works", C["smith_canaletto_holdings"], "Canaletto works obtained through Smith; the statement distinguishes agented commissions from personal ownership."),
    ("artist-character", 418, "artist", E["canaletto"]),
    ("businessman-character", 418, "business man", E["smith"]),
    ("smith-letter-author", 418, "Smith wrote angrily", E["smith"]),
    ("smith-brush-letter", 418, "after a brush in 1729", C["smith_1729_letter"], "The footnoted letter’s exact date and addressee remain pending."),
    ("painter-impertinence", 419, "a painter’s impertinence", E["canaletto"], "Context points to Canaletto; preserve the wording as Smith’s quoted complaint."),
    ("smith-agent-role", 419, "his self-appointed role as the agent", E["smith"]),
    ("canaletto-purchases", 419, "Canalettos were purchased", C["smith_canaletto_holdings"], "Plural refers to Canaletto pictures; the passage describes Smith’s purchasing agency."),
    ("tessin", 420, "Count Tessin", E["tessin"]),
    ("canaletto-engagement", 420, "Canaletto", E["canaletto"]),
    ("smith-engagement", 420, "Smith", E["smith"]),
    ("tessin-exclusivity", 420, "work exclusively for him", E["canaletto"], "Reported by Haskell as Tessin’s 1736 statement about a four-year engagement."),
    ("royal-collection-first-half", 420, "Royal", E["royal_collection"], "The institution name is line-broken as Royal / Collection in the source."),
    ("royal-collection-second-half", 421, "Collection", E["royal_collection"], "Completes the line-broken name Royal Collection."),
    ("smith-more-pictures", 420, "Smith obtained for others", E["smith"]),
    ("smith-private-pictures", 420, "for himself", E["smith"]),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p304-{local}"
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
        page_map = {P303: 303, P305: 305}
        pages = [page_map[item] for item in cross if item in page_map]
        if pages:
            qualifiers["cross_reference_printed_pages"] = pages
    new_s.append({"statement_id": sid, "segment_id": P304, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("smith-settled-palazzo", 412, 412, E["smith"], E["palazzo_balbi"], "settled_at_palazzo_balbi_on_arrival",
      "The p.303 sentence closes: Smith had settled at the Palazzo Balbi on arrival.",
      "The source does not give an arrival date here; building identity remains for S3.", relation=True, cross=[P303])
add_s("smith-country-house-lease-purchase", 412, 413, E["smith"], C["smith_country_house"],
      "leased_from_gerolamo_canal_then_bought_in_1731",
      "Smith bought the country house at Mogliano in 1731 after leasing it four years earlier from Gerolamo Canal, then Procuratore di San Marco.",
      "The lease date is calculated from Haskell’s ‘four years earlier’; retain the office as a role and do not infer a separate institution.", relation=True, footnote=1)
add_s("smith-displayed-works", 413, 413, C["smith_venice_collection"], C["smith_country_house"],
      "displayed_paintings_and_drawings_in_two_properties",
      "Smith displayed paintings and drawings by Sebastiano Ricci, Marco Ricci, Carlo Cignani and Rosalba Carriera in the Palazzo Balbi and country house.",
      "The phrase ‘these two properties’ refers to the Palazzo Balbi and the country house. The passage does not identify each work individually.", relation=True, footnote=2)
add_s("smith-piazzetta-contact", 413, 413, E["smith"], E["piazzetta"],
      "probably_displayed_piazzetta_work_and_was_in_touch_with_him",
      "Haskell says Smith probably also displayed works by Piazzetta, with whom he was in touch during those years.",
      "Both the display attribution and the inclusion of Piazzetta are qualified by ‘probably’.", relation=True, footnote=2)
add_s("smith-collection-standing", 413, 413, E["smith"], C["smith_venice_collection"],
      "collection_was_venices_most_important_modern_art_collection_with_growing_old_masters",
      "Haskell describes Smith’s collection as already Venice’s most important collection of modern art, with a growing number of old masters, but says it reflected no particular originality of outlook.",
      "Comparative assessment is Haskell’s; it does not mean the collection contained only modern art.", layer="authorial interpretation")
add_s("smith-taste-shift", 413, 413, E["smith"], C["smith_taste_shift"],
      "shifted_from_history_pictures_to_views_and_landscapes",
      "Haskell says Smith began accumulating pictures that made his palace distinctive in individual taste, reflecting a concurrent English move away from large-scale history pictures toward views and landscapes.",
      "Haskell says the parallel may have been conscious or not and explicitly says the shift was not toward portraits in Smith’s case.", layer="authorial interpretation")
add_s("smith-artist-portraits", 413, 413, E["smith"], None, "wanted_portraits_of_employed_artists_but_not_of_himself",
      "Smith was anxious to have portraits of all the artists who worked for him, but never seems to have commissioned a portrait of himself.",
      "The negative is qualified by ‘never seems’; do not infer that no portrait of Smith existed.", layer="authorial interpretation")
add_s("canaletto-employment-centrality", 414, 415, E["smith"], E["canaletto"],
      "employed_canaletto_as_central_change_in_patronage",
      "Haskell identifies Smith’s employment of Canaletto as the principal marker of a new direction in Smith’s patronage and says their relations were central to both careers.",
      "This describes Haskell’s assessment of the relationship’s significance.", relation=True, cross=[P305])
add_s("canaletto-work-start-date", 416, 416, E["canaletto"], E["smith"], "likely_began_working_for_smith_circa_1727_or_1728",
      "Although there is no conclusive record that Smith and Canaletto were in touch before 1729, Haskell thinks Canaletto likely began working for Smith a year or two earlier, when he was already known to a European clientele.",
      "The start date and early contact are explicitly uncertain; do not state a documented meeting.", relation=True, footnote=3, layer="authorial hypothesis")
add_s("smith-directed-output", 417, 417, E["smith"], C["smith_canaletto_holdings"],
      "directed_canaletto_output_almost_entirely_to_english_channels_and_own_collection",
      "Smith directed nearly all of Canaletto’s output into English channels and conspicuously into his own collection.",
      "‘Almost entirely’ is retained; Haskell says the exact nature of their relations remains uncertain.", relation=True, footnote=3)
add_s("smith-controlled-commissions", 417, 417, E["smith"], E["canaletto"],
      "controlled_commissions_for_canaletto_works_through_smith",
      "Haskell says Smith’s control over Canaletto was such that, from an early period, commissions for Canaletto’s works were very frequently, if not exclusively, made through Smith.",
      "The passage preserves ‘very frequently, if not exclusively’; footnote 4 remains pending.", relation=True, footnote=4)
add_s("smith-canaletto-character", 418, 418, E["smith"], E["canaletto"], "both_described_as_notoriously_mean",
      "Haskell characterizes both Canaletto and the businessman Smith as notoriously mean.",
      "This is Haskell’s evaluative characterization, not an independently established personality fact.", relation=True, layer="authorial interpretation")
add_s("smith-1729-complaint", 418, 419, E["smith"], C["smith_1729_letter"],
      "complained_after_1729_brush_with_painter",
      "After a brush with a painter in 1729, Smith wrote angrily that he had previously submitted to a painter’s impertinence to serve himself and his friends.",
      "The original letter is only cited through Haskell here; footnote 5 remains pending, and the object of the quarrel is contextual rather than named in the quotation.", relation=True,
      footnote=5, layer="nested correspondence quotation", speaker="Joseph Smith as quoted by Haskell")
add_s("smith-purchase-agent", 419, 419, E["smith"], C["smith_canaletto_holdings"],
      "retained_self_appointed_agent_role_for_canaletto_purchases",
      "Despite difficulties, Smith retained his self-appointed role as the agent through whom Canaletto pictures were purchased.",
      "This is Haskell’s description of Smith’s role; the passage does not identify all buyers.", relation=True)
add_s("tessin-four-year-engagement", 420, 420, E["tessin"], E["canaletto"],
      "reported_four_year_exclusive_engagement_by_smith",
      "Haskell thinks Count Tessin’s 1736 statement meant that Canaletto had been engaged by Smith for four years to work exclusively for him.",
      "This is Haskell’s interpretation of Tessin’s report, not an independently verified contract; the cited source remains pending in footnote 6.",
      relation=True, footnote=6, layer="reported observation", speaker="Count Tessin as reported by Haskell")
add_s("smith-held-canalettos-versus-royal", 420, 421, E["smith"], E["royal_collection"],
      "kept_far_more_canaletto_pictures_than_fifty_three_in_royal_collection",
      "Haskell says that, besides the pictures Smith obtained for others, he kept far more for himself than the fifty-three Canaletto pictures then in the Royal Collection.",
      "The sentence continues on p.305 and the comparison’s implications are not complete until that continuation; footnote 7 remains pending.", relation=True,
      footnote=7, cross=[P305], layer="authorial comparison")

all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.304: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if not q["mentioned_candidate_ids"]:
        raise SystemExit(f"statement has no anchored mention: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

cov[P303]["note"] = cov[P303]["note"].replace(
    "the last body sentence continues on p.304, so p.303 remains partial.",
    "p.304 closes the residence sentence; p.303’s L409 and footnotes 1–6 remain pending in the consolidated notes segment, so p.303 remains partial.")
cov[P304].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L412-421",
    "note": "Printed p.304 body checked against CHP-10.pdf physical page 33. Closed p.303’s Palazzo Balbi sentence; recorded Smith’s 1731 purchase of the Mogliano country house after a four-year lease from Gerolamo Canal, then Procuratore di San Marco; the artists whose works were displayed in both properties; the collection’s standing and Smith’s qualified shift from history pictures toward views/landscapes; the English/portraiture qualification; Smith’s employment and control of Canaletto commissions; uncertain pre-1729 contact and likely earlier work; the 1729 quarrel quotation; Smith’s agent role; Tessin’s reported four-year exclusive engagement; and the comparison with 53 Canaletto works in the Royal Collection. Reused indexed candidates for Smith, Canal, Canaletto, Carriera, Cignani, Piazzetta, both Riccis, Tessin, Royal Collection, Palazzo Balbi, Venice, England and the Procuratore office; added separate candidates for the country house, Mogliano/Treviso locations, unresolved Venetian collection, taste-shift term, Smith’s Canaletto holdings and quoted letter. The p.304 image confirms the OCR’s line-breaks and wording; original spelling ‘submitt’ is retained. Footnotes 1–7 remain pending in the consolidated notes source. L421’s sentence continues on p.305, so p.304 remains partial."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P304, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "coverage": {"p303": cov[P303]["migration_status"], "p304": cov[P304]["migration_status"],
                        "p305": cov[P305]["migration_status"]}}
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
    print("Applied p.304 S2 body migration; p.304 footnotes remain in the consolidated notes segment.")
