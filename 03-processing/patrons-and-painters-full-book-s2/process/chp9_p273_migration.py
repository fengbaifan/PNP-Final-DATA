"""Controlled S2 migration for printed p.273 body; defaults to dry-run."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
PREVIOUS = "chp-9:09_CHP-9_sec_ii:l53-60"
SEGMENT = "chp-9:09_CHP-9_sec_ii:l62-68"
NEXT = "chp-9:09_CHP-9_sec_ii:l70-78"
ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
SEGMENT_SHA = "28948f51a1b46a06efca67df6597c58b2d22369b628a0d2396491eeff5a3d7bc"
MAX_CANDIDATE = 8732
BACKUP_SUFFIX = ".bak-s2-chp9-p273-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def read_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


raw = SOURCE.read_bytes()
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(raw).hexdigest() != ASSET_SHA:
    raise SystemExit("section-II source asset has changed")
segments = {x["segment_id"]: x for x in read_jsonl(TABLES / "segments.jsonl")}
if segments.get(SEGMENT, {}).get("sha256") != SEGMENT_SHA or segments[SEGMENT].get("asset_sha256") != ASSET_SHA:
    raise SystemExit("p.273 source segment missing or changed")
if NEXT not in segments or not lines[62].startswith("but although he was paid") or not lines[67].endswith("drawn,"):
    raise SystemExit("expected p.273 text/continuation has changed")
if not lines[70].startswith("so he claimed"):
    raise SystemExit("expected p.274 continuation has changed")

segment_text = "\n".join(lines[61:68])
offsets, offset = {}, 0
for n in range(62, 69):
    offsets[n] = offset
    offset += len(lines[n - 1]) + 1

cp = TABLES / "entity-candidates.csv"
mp = TABLES / "mentions.csv"
sp = TABLES / "book-statements.jsonl"
vp = TABLES / "s2-coverage.csv"
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
statements = read_jsonl(sp)
vf, coverage = read_csv(vp)
candidate_ids = {x["candidate_id"] for x in candidates}
mention_ids = {x["mention_id"] for x in mentions}
statement_ids = {x["statement_id"] for x in statements}
cov = {x["segment_id"]: x for x in coverage}
maximum = max(int(re.search(r"\d+", x["candidate_id"]).group()) for x in candidates)
if maximum != MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {MAX_CANDIDATE}, found {maximum}")
if (cov.get(PREVIOUS, {}).get("disposition"), cov.get(PREVIOUS, {}).get("migration_status")) != ("reviewed", "partial"):
    raise SystemExit("p.272 is not in expected reviewed/partial state")
if (cov.get(SEGMENT, {}).get("disposition"), cov.get(SEGMENT, {}).get("migration_status")) != ("queued", "pending"):
    raise SystemExit("p.273 is not queued/pending")

E = {
    "pieta_church": "cand-8551", "pieta_governors": "cand-8730", "pieta_triumph": "cand-8732",
    "tiepolo": "cand-2575", "piazzetta": "cand-1901", "dominicans": "cand-0941",
    "carmelites": "cand-0563", "religious_orders": "cand-8675", "oratorians": "cand-1783",
    "education": "cand-2588", "madonna": "cand-2596", "ricci": "cand-2154",
    "tassis": "cand-2543", "bergamo": "cand-8574", "piazzetta_work": "cand-1922",
    "scuola": "cand-8706", "virgin": "cand-3427", "ripa": "cand-2203", "zompini": "cand-2874",
    "tiepolo_fresco_group": "cand-8705",
}
for key, cid in E.items():
    if cid not in candidate_ids:
        raise SystemExit(f"required candidate missing: {key}={cid}")

SPECS = [
    ("altar_pictures", "Five unidentified altar pictures at the Pietà paid for by private donations", "work", "A group of five altar pictures at the Pietà; neither individual titles nor artists are supplied.", 63),
    ("piazzetta_school", "Piazzetta's school as an artistic circle", "term", "Haskell's collective attribution; not a formally named institution and not a claim that Piazzetta painted any of the five pictures.", 63),
    ("private_donations", "Private donations funding the Pietà altar pictures", "term", "Unspecified private gifts; no donor is identified in this passage.", 63),
    ("mystical_ecstasy", "Mystical ecstasy as an effect of Oratorian church paintings", "term", "A quality Haskell says the Oratorians seem to have encouraged.", 64),
    ("roman_comparison", "Roman paintings of the early seventeenth century in Haskell's comparison", "term", "A comparative group named by Haskell; no individual paintings are identified here.", 64),
    ("purgatorial_fires", "Purgatorial fires as an iconographic motif", "term", "The motif Tiepolo and Ricci are said not to show in the cited paintings.", 65),
    ("ricci_picture", "Unidentified Sebastiano Ricci picture of the same subject as the Madonna del Carmelo", "work", "The subject is linked by Haskell to Tiepolo's Madonna del Carmelo; no title, date, or location is given.", 65),
    ("central_canvas", "Proposed central ceiling canvas of the Virgin giving the scapular to St Simeon Stock", "work", "The same central subject appears in both alternatives; the source does not name a completed individual canvas.", 67),
    ("first_scheme", "First proposed Scuola del Carmine ceiling scheme of confraternity privileges", "work", "A rejected-alternative status is not asserted; this proposal comprised the central canvas and eight surrounding doctrinal canvases.", 67),
    ("second_scheme", "Second proposed Scuola del Carmine ceiling scheme of virtues", "work", "The alternative Haskell says was chosen and executed with modifications.", 67),
    ("scapular", "Scapular as a Carmelite devotional object", "term", "Named as the object handed to St Simeon Stock in the proposed central image.", 67),
    ("angels", "Angels as figures in the Scuola del Carmine ceiling proposals", "term", "A collective iconographic group, not individually named figures.", 67),
    ("elijah", "Elijah the prophet in the proposed Scuola del Carmine ceiling scene", "person", "Figure named in the proposed central composition; align identity globally in S3.", 67),
    ("elisha", "Elisha the prophet in the proposed Scuola del Carmine ceiling scene", "person", "Figure named in the proposed central composition; align identity globally in S3.", 67),
    ("simeon_stock", "St Simeon Stock in the proposed Scuola del Carmine ceiling scene", "person", "Figure named in the proposed central composition; align identity globally in S3.", 67),
    ("faith", "Faith as a theological virtue in the Scuola del Carmine scheme", "term", "One of the virtues named in the second iconographic proposal, distinct from its pictorial personification.", 67),
    ("hope", "Hope as a theological virtue in the Scuola del Carmine scheme", "term", "One of the virtues named in the second iconographic proposal, distinct from its pictorial personification.", 67),
    ("charity", "Charity as a theological virtue in the Scuola del Carmine scheme", "term", "One of the virtues named in the second iconographic proposal, distinct from its pictorial personification.", 67),
    ("purgatory_rescue", "Rescue of souls in purgatory by angels as an iconographic subject", "term", "An example of a doctrinal subject Haskell says the first scheme's canvases would represent.", 67),
    ("scuola_governors", "Governors of the Scuola del Carmine", "institution", "Unnamed governing body which organized the later competition; distinct from the Pietà governors on p.272–273.", 68),
    ("competition", "Competition for further decoration of the Scuola del Carmine", "event", "Haskell says the governors invited artists to submit schemes; no date is supplied in this passage.", 68),
    ("zompini_proposal", "Gaetano Zompini's iconographic proposal for the Scuola del Carmine competition", "work", "Its description continues on p.274; keep the proposal distinct from Tiepolo's two alternatives.", 68),
]
new_candidates, C = [], {}
for i, (key, name, kind, detail, line_no) in enumerate(SPECS, 1):
    cid = f"cand-{MAX_CANDIDATE+i:04d}"
    if cid in candidate_ids or any(x["canonical_name"] == name and x["suggested_type"] == kind for x in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {cid} {name}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{line_no}",
    })
candidate_ids |= {x["candidate_id"] for x in new_candidates}


def c(key):
    return C[key]


def e(key):
    return E[key]


new_mentions = []


def mention(mid, line_no, cid, surface, note="", occurrence=0):
    if mid in mention_ids or any(x["mention_id"] == mid for x in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    line = lines[line_no - 1]
    found, pos = [], 0
    while True:
        at = line.find(surface, pos)
        if at < 0:
            break
        found.append(at)
        pos = at + 1
    if occurrence >= len(found):
        raise SystemExit(f"surface absent on L{line_no}: {surface!r}")
    start = offsets[line_no] + found[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface or cid not in candidate_ids:
        raise SystemExit(f"bad mention span/ref: {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": SEGMENT, "candidate_id": cid, "surface_form": surface,
        "start_char": str(start), "end_char": str(end), "note": note,
    })


def piece(line_no, start, end):
    source_line = lines[line_no - 1]
    a = source_line.index(start)
    return source_line[a:source_line.index(end, a) + len(end)]


mention_specs = [
    ("tiepolo_he", 63, "tiepolo", "he", "Antecedent is Tiepolo at p.272 L58.", 0),
    ("payment_this", 63, "pieta_triumph", "this", "Refers to the Triumph of the Faith named at p.272 L58.", 0),
    ("pieta_governors", 63, "pieta_governors", "the Governors of the church", "Governors of the Pietà; not the later Scuola del Carmine governors.", 0),
    ("pieta_church", 63, "pieta_church", "the church", "Nested location within 'Governors of the church'.", 0),
    ("five_pictures", 63, "altar_pictures", "Five altar pictures", "Unidentified group of five works.", 0),
    ("piazzetta_school", 63, "piazzetta_school", "Piazzetta’s school", "Collective artistic circle; individual painters are not named.", 0),
    ("piazzetta_school_person", 63, "piazzetta", "Piazzetta’s", "Person named as the head of the artistic school.", 0),
    ("private_donations", 63, "private_donations", "private donations", "Funding source is collective and unnamed.", 0),
    ("dominicans", 64, "dominicans", "the Dominicans", "Order in Haskell's comparison.", 0),
    ("carmelites", 64, "carmelites", "Carmelites", "Order in Haskell's comparison.", 0),
    ("orders", 64, "religious_orders", "their Orders", "Plural reference to the Dominicans and Carmelites.", 0),
    ("oratorians", 64, "oratorians", "the Oratorians", "Order in Haskell's comparison.", 0),
    ("ecstasy", 64, "mystical_ecstasy", "a mystical ecstasy", "Authorial characterization, not an independently verified property.", 0),
    ("tiepolo_education", 64, "tiepolo", "Tiepolo’s", "Artist named in possessive form.", 0),
    ("education", 64, "education", "Education os the Virgin", "Index sub-entry identifies the work; OCR 'os' is read 'of' against the scan.", 0),
    ("roman_paintings", 64, "roman_comparison", "certain Roman paintings of the early seventeenth century", "Unspecified comparative group; no titles are supplied.", 0),
    ("tiepolo_madonna", 65, "tiepolo", "Tiepolo’s", "Artist named in possessive form.", 0),
    ("madonna", 65, "madonna", "Madonna del Carmelo", "Index sub-entry identifies the work.", 0),
    ("fires_tiepolo", 65, "purgatorial_fires", "the purgatorial fires", "Iconographic motif said to be absent from this work.", 0),
    ("ricci", 65, "ricci", "Sebastiano Ricci", "Artist named by Haskell.", 0),
    ("ricci_patron", 65, "tassis", "his patron", "Coreference to the following Count Tassis.", 0),
    ("tassis", 65, "tassis", "Conte Tassis", "Index candidate; individual identity awaits S3 alignment.", 0),
    ("bergamo", 65, "bergamo", "Bergamo", "Reuse the chapter-level city candidate; global identity remains for S3.", 0),
    ("ricci_same_subject_picture", 65, "ricci_picture", "a picture of the same subject", "Unidentified Ricci work compared with the Madonna del Carmelo.", 0),
    ("fires_ricci", 65, "purgatorial_fires", "them", "Pronoun refers to purgatorial fires.", 0),
    ("piazzetta_skull_person", 65, "piazzetta", "Piazzetta", "Artist named by Haskell.", 0),
    ("st_philip_work", 65, "piazzetta_work", "St Philip Neri and the Virgin", "Index sub-entry identifies the work, distinct from Piazzetta as artist.", 0),
    ("scuola", 67, "scuola", "The Scuola del Carmine", "Institution whose governors exerted patronage; building/entity boundary remains for S3.", 0),
    ("tiepolo_scuola", 67, "tiepolo", "Tiepolo", "Index candidate for the page-specific person mention.", 0),
    ("they_pressure", 67, "scuola", "they", "Pronoun refers to the Scuola del Carmine as patronal institution.", 0),
    ("tiepolo_him", 67, "tiepolo", "him", "Pronoun refers to Tiepolo.", 0),
    ("they_advice", 67, "scuola", "They", "Pronoun refers to the Scuola del Carmine governors/institution.", 0),
    ("tiepolo_advice", 67, "tiepolo", "his", "Possessive refers to Tiepolo.", 0),
    ("tiepolo_proposed", 67, "tiepolo", "Tiepolo", "Artist proposing the alternative schemes.", 1),
    ("central_panel", 67, "central_canvas", "the central panel in the ceiling", "Shared central subject in both alternatives.", 0),
    ("virgin", 67, "virgin", "the Virgin", "Religious figure represented in the proposed scene.", 0),
    ("elijah", 67, "elijah", "Elijah", "Prophet named as a figure in the scene.", 0),
    ("elisha", 67, "elisha", "Elisha", "Prophet named as a figure in the scene.", 0),
    ("angels", 67, "angels", "angels", "Collective figures surrounding the central scene.", 0),
    ("scapular", 67, "scapular", "the scapular", "Devotional object in the proposed scene.", 0),
    ("simeon_stock", 67, "simeon_stock", "St Simeon Stock", "Religious figure named in the proposed scene.", 0),
    ("this_canvas", 67, "central_canvas", "this canvas", "Anaphoric reference to the proposed central panel.", 0),
    ("first_scheme", 67, "first_scheme", "the first scheme", "First of Tiepolo's two alternatives.", 0),
    ("eight_canvases", 67, "first_scheme", "eight others", "Eight canvases surrounding the shared central canvas in the first alternative.", 0),
    ("confraternity", 67, "scuola", "the Confraternity", "Source's collective reference to the patronal association.", 0),
    ("brethren", 67, "scuola", "the Brethren", "Members of the confraternity; individuals are unnamed.", 0),
    ("virgin_intercession", 67, "virgin", "the Virgin", "Nested mention in the quoted hope of salvation through intercession.", 1),
    ("these_canvases", 67, "first_scheme", "These canvases", "Anaphoric reference to the eight canvases in the first scheme.", 0),
    ("angels_rescue", 67, "angels", "angels", "Collective agents in an illustrative doctrinal subject.", 1),
    ("souls_purgatory", 67, "purgatory_rescue", "souls in purgatory", "Example of a doctrinal subject; no individual souls are named.", 0),
    ("second_scheme", 67, "second_scheme", "the second scheme", "Second alternative, later chosen with modifications.", 0),
    ("surrounding_canvases", 67, "second_scheme", "the surrounding canvases", "Canvases of the second alternative.", 0),
    ("brethren_second", 67, "scuola", "the Brethren", "Members of the confraternity, as the intended audience of the virtues.", 1),
    ("faith", 67, "faith", "Faith", "Theological virtue named in the quoted second scheme.", 0),
    ("hope", 67, "hope", "Hope", "Theological virtue named in the quoted second scheme.", 0),
    ("charity", 67, "charity", "Charity", "Theological virtue named in the quoted second scheme.", 0),
    ("ripa", 67, "ripa", "Ripa’s", "Person credited with the standard iconographic manual.", 0),
    ("ripa_manual", 67, "ripa", "standard iconographic Manual", "Index sub-entry 'Iconologia' is the likely reference; bibliographic identity remains unverified.", 0),
    ("second_plan", 67, "second_scheme", "this second plan", "Anaphoric reference to the second scheme.", 0),
    ("scuola_competition", 68, "scuola", "the Scuola", "The Scuola del Carmine; p.274 continues its programme account.", 0),
    ("carmine_governors", 68, "scuola_governors", "the governors", "Governing body of the Scuola del Carmine, distinct from Pietà governors.", 0),
    ("competition", 68, "competition", "a competition", "Event organized for the further decoration.", 0),
    ("zompini", 68, "zompini", "Gaetano Zompini", "Painter named by Haskell.", 0),
    ("zompini_idea", 68, "zompini_proposal", "whose idea", "Possessive relative pronoun refers to Zompini's proposal.", 0),
    ("zompini_proposal", 68, "zompini_proposal", "an iconographical proposal", "Proposal description continues on p.274 L71.", 0),
]
for mid, n, key, surface, note, occurrence in mention_specs:
    mention(f"m-chp9-p273-{mid}", n, c(key) if key in C else e(key), surface, note, occurrence)

new_statements = []


def statement(sid, a, b, sub, obj, pred, quote, claim, qualification, refs=(), rel=False, fn=None, cross=()):
    if sid in statement_ids or any(x["statement_id"] == sid for x in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored: {sid}")
    refs = set(refs) | {x for x in (sub, obj) if x}
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(refs - candidate_ids)}")
    q = {
        "source_line_start": a, "source_line_end": b, "printed_page": 273, "pdf_physical_page": 39,
        "claim": claim, "speaker": "Haskell", "text_layer": "authorial narrative",
        "qualification": qualification, "mentioned_candidate_ids": sorted(refs),
    }
    if rel:
        q["relation_candidate"] = True
    if fn is not None:
        q["footnote_marker"] = fn
        q["footnote_text_pending"] = True
    if cross:
        q["cross_reference_segments"] = list(cross)
    new_statements.append({
        "statement_id": sid, "segment_id": SEGMENT, "subject_candidate_id": sub,
        "object_candidate_id": obj, "predicate": pred, "qualifiers": q,
        "original_quote": quote, "source_file": SOURCE.relative_to(ROOT).as_posix(), "origin": "book",
    })


q_payment = piece(63, "but although", "for this,")
q_loan = piece(63, "two years later", "further decoration.")
q_altarpieces = piece(63, "Five altar pictures", "private donations.2")
q_dom_carm = piece(64, "the Dominicans", "their Orders,")
q_oratorian = piece(64, "the Oratorians", "encouraged a mystical ecstasy")
q_education = piece(64, "in Tiepolo’s Education", "early seventeenth century.")
q_tone = piece(65, "But these are matters of emphasis", "morbidity.")
q_madonna = piece(65, "Tiepolo’s Madonna del Carmelo", "the purgatorial fires,")
q_ricci = piece(65, "in much the same way", "the same subject;")
q_piazzetta = piece(65, "Piazzetta even removes", "the Virgin.3")
q_control = lines[65]
q_pressure = piece(67, "The Scuola del Carmine", "secular commissions.4")
q_advice = piece(67, "They then asked his advice", "subject to him.")
q_alternatives = piece(67, "Tiepolo proposed two alternatives", "St Simeon Stock.")
q_first_scheme = piece(67, "According to the first scheme", "intercession of the Virgin.’")
q_purgatory = piece(67, "These canvases would therefore", "souls in purgatory.")
q_second_scheme = piece(67, "According to the second scheme", "and a host of others.")
q_ripa = piece(67, "Tiepolo took his descriptions", "known by heart)")
q_chosen = piece(67, "and this second plan was chosen", "few modifications.")
q_competition = piece(68, "For the further decoration", "submit schemes.5")
q_zompini = piece(68, "The painter Gaetano Zompini", "proposal of some complexity drawn,")

statement("st-chp9-p273-tiepolo-paid-for-dome-work", 63, 63, e("tiepolo"), e("pieta_triumph"),
          "tiepolo_paid_500_zecchini_for_pieta_triumph_of_faith", q_payment,
          "Haskell says Tiepolo was paid 500 zecchini for the work identified on p.272 as the Triumph of the Faith.",
          "The pronoun 'this' refers to the dome work in the previous segment; the payment is not independently verified.",
          [e("pieta_church")], True, 1, [{"segment_id": PREVIOUS, "source_line_start": 58, "source_line_end": 58}])
statement("st-chp9-p273-tiepolo-loaned-funds-to-pieta-governors", 63, 63, e("tiepolo"), e("pieta_governors"),
          "tiepolo_lent_6000_ducats_to_pieta_governors_two_years_later", q_loan,
          "Haskell says Tiepolo lent the Pietà's Governors 6000 ducats two years later to help with further decoration.",
          "Retain the relative interval and Haskell's comparison of about three times the earlier payment; do not infer a loan date.",
          [e("pieta_church"), e("pieta_triumph")], True, 1)
statement("st-chp9-p273-pieta-five-altar-pictures", 63, 63, c("altar_pictures"), e("pieta_church"),
          "five_pieta_altar_pictures_painted_by_piazzetta_school_and_paid_by_private_donations", q_altarpieces,
          "Haskell says five altar pictures were painted by leading artists of Piazzetta's school and paid for by private donations.",
          "No individual work titles, artist names, or donors are given; do not infer Piazzetta himself painted one.",
          [c("piazzetta_school"), c("private_donations"), e("piazzetta")], True, 2)
statement("st-chp9-p273-dominicans-carmelites-order-emphasis", 64, 64, None, None,
          "dominican_and_carmelite_paintings_emphasize_their_orders", q_dom_carm,
          "Haskell says Dominicans and Carmelites concentrate more on exaltation of their Orders.",
          "Comparative authorial characterization, not an exhaustive account of all works by either Order.",
          [e("dominicans"), e("carmelites"), e("religious_orders")])
statement("st-chp9-p273-oratorian-mystical-ecstasy", 64, 64, e("oratorians"), c("mystical_ecstasy"),
          "oratorian_church_paintings_seem_to_encourage_mystical_ecstasy", q_oratorian,
          "Haskell says Oratorian paintings seem to have encouraged mystical ecstasy.",
          "Preserve 'seem to have'; this is Haskell's interpretation of emphasis.", [e("oratorians")])
statement("st-chp9-p273-education-virgin-tenderness", 64, 64, e("education"), c("roman_comparison"),
          "education_of_virgin_has_unusual_tenderness_compared_with_early_roman_paintings", q_education,
          "Haskell characterizes the Education of the Virgin as unusually tender and says this quality, alongside mystical ecstasy, is more familiar in certain Roman paintings of the early seventeenth century.",
          "OCR 'os' is read 'of' against the scan; the comparison is limited to 'certain' paintings and both qualities.",
          [e("tiepolo"), c("mystical_ecstasy")])
statement("st-chp9-p273-church-paintings-triumphant-tone", 65, 65, None, None,
          "haskell_says_venetian_church_paintings_have_a_triumphant_non_morbid_tone", q_tone,
          "Haskell says the paintings are matters of emphasis rather than rigorous consistency, with a dominant note of triumph and avoidance of cruelty or morbidity.",
          "This is the author's synthesis of the preceding church examples, not a verified universal property.",
          [e("dominicans"), e("carmelites"), e("oratorians"), e("education")])
statement("st-chp9-p273-tiepolo-madonna-omits-purgatorial-fires", 65, 65, e("madonna"), c("purgatorial_fires"),
          "tiepolo_madonna_del_carmelo_does_not_show_purgatorial_fires", q_madonna,
          "Haskell says Tiepolo's Madonna del Carmelo does not show purgatorial fires.",
          "Preserve as a source claim about the image; do not infer a censorship order from this sentence.",
          [e("tiepolo")])
statement("st-chp9-p273-tassis-requested-ricci-omit-fires", 65, 65, e("tassis"), c("ricci_picture"),
          "count_tassis_asked_ricci_not_to_show_purgatorial_fires_in_same_subject_picture", q_ricci,
          "Haskell says Sebastiano Ricci was asked by his patron Count Tassis of Bergamo not to show purgatorial fires in a picture of the same subject.",
          "The painting is unnamed; the patron relation and request are reported by Haskell, not independently checked.",
          [e("ricci"), e("bergamo"), c("purgatorial_fires"), e("madonna")], True)
statement("st-chp9-p273-piazzetta-removed-skull-from-preliminary-version", 65, 65, e("piazzetta_work"), None,
          "piazzetta_removed_skull_from_preliminary_version_of_st_philip_neri_and_virgin", q_piazzetta,
          "Haskell says Piazzetta removed a skull that he had included in a preliminary version of St Philip Neri and the Virgin.",
          "The index sub-entry identifies the work; this statement does not assert that a surviving preliminary version is located.",
          [e("piazzetta"), c("purgatorial_fires")], True, 3)
statement("st-chp9-p273-control-over-artist-uncertain", 66, 66, None, None,
          "haskell_says_extent_of_control_over_artist_is_difficult_to_determine", q_control,
          "Haskell says it is difficult to say how much control was exerted over the artist in such matters.",
          "Explicit uncertainty; 'such matters' refers to the preceding examples of religious imagery and patronal direction.",
          [e("piazzetta"), e("ricci"), e("tiepolo"), e("madonna"), c("ricci_picture"), e("piazzetta_work")])
statement("st-chp9-p273-scuola-pressured-tiepolo-to-prioritize-religious-commissions", 67, 67, e("scuola"), e("tiepolo"),
          "scuola_del_carmine_pressured_tiepolo_to_prioritize_religious_commissions", q_pressure,
          "Haskell says the Scuola del Carmine determinedly secured Tiepolo and suggested he give religious commissions precedence over secular ones.",
          "The moral pressure is Haskell's description; the note 4 text remains pending in the consolidated notes segment.",
          [e("scuola"), e("tiepolo")], True, 4)
statement("st-chp9-p273-scuola-asked-tiepolo-for-decoration-advice", 67, 67, e("scuola"), e("tiepolo"),
          "scuola_del_carmine_sought_tiepolo_advice_and_left_subject_choice_to_him", q_advice,
          "Haskell says the Scuola asked Tiepolo's advice on decorating the main room and left the subject choice to him.",
          "The passage gives no exact date or formal contract.", [e("scuola")], True)
statement("st-chp9-p273-tiepolo-proposed-two-schemes", 67, 67, e("tiepolo"), None,
          "tiepolo_proposed_two_alternatives_for_scuola_ceiling", q_alternatives,
          "Haskell says Tiepolo proposed two alternatives, each with the same central scene of the Virgin giving the scapular to St Simeon Stock with Elijah, Elisha, and angels.",
          "The central subject is common to both alternatives; the passage does not name a completed individual canvas.",
          [c("central_canvas"), e("virgin"), c("elijah"), c("elisha"), c("angels"), c("scapular"), c("simeon_stock")], True)
statement("st-chp9-p273-first-scheme-confraternity-privileges", 67, 67, c("first_scheme"), e("scuola"),
          "first_scheme_surrounded_central_canvas_with_eight_canvases_of_confraternity_privileges", q_first_scheme,
          "Haskell says the first plan surrounded the central canvas with eight canvases illustrating confraternity privileges and hope of salvation through the Virgin's intercession.",
          "This records the proposed programme as described; it does not assert the scheme was built or wholly rejected.",
          [c("central_canvas"), e("scuola"), e("virgin")], True)
statement("st-chp9-p273-first-scheme-doctrinal-subjects", 67, 67, c("first_scheme"), c("purgatory_rescue"),
          "first_scheme_canvases_would_show_doctrinal_subjects_including_rescue_from_purgatory", q_purgatory,
          "Haskell says the first scheme's canvases would represent doctrinal points such as angels rescuing souls in purgatory.",
          "The example is illustrative, not an exhaustive list of the eight canvases.", [c("angels")])
statement("st-chp9-p273-second-scheme-virtues", 67, 67, c("second_scheme"), None,
          "second_scheme_surrounding_canvases_depicted_virtues_inspiring_brethren", q_second_scheme,
          "Haskell says the second scheme's surrounding canvases were to depict virtues inspiring the Brethren, including Faith, Hope, and Charity.",
          "Retain the quoted general phrasing; further virtues are unnamed.",
          [e("scuola"), c("faith"), c("hope"), c("charity")])
statement("st-chp9-p273-tiepolo-drew-virtues-from-ripa", 67, 67, e("tiepolo"), e("ripa"),
          "tiepolo_descriptions_of_virtues_drawn_from_ripas_iconographic_manual", q_ripa,
          "Haskell says Tiepolo took descriptions of the virtues from illustrations in Ripa's standard iconographic Manual and must have known it by heart.",
          "The source's 'must have' is an authorial inference; bibliographic identity of the manual remains to be confirmed from the index/bibliography.",
          [c("second_scheme"), e("ripa")], True)
statement("st-chp9-p273-second-scheme-chosen-and-executed", 67, 67, c("second_scheme"), e("tiepolo_fresco_group"),
          "second_scuola_scheme_chosen_and_carried_out_with_modifications", q_chosen,
          "Haskell says the second plan was chosen and carried out with a few modifications.",
          "Do not infer the exact finished iconographic programme or map each planned canvas to a surviving work.",
          [e("scuola")], True)
statement("st-chp9-p273-scuola-governors-organized-competition", 68, 68, c("scuola_governors"), c("competition"),
          "scuola_del_carmine_governors_organized_competition_for_further_decoration", q_competition,
          "Haskell says the Scuola governors organized a competition and invited artists to submit schemes.",
          "The date and identities of other competitors are not supplied.", [e("scuola")], True, 5)
statement("st-chp9-p273-zompini-proposal-accepted-partial", 68, 68, e("zompini"), c("zompini_proposal"),
          "zompini_iconographic_proposal_accepted_and_description_continues", q_zompini,
          "Haskell says Gaetano Zompini's idea was accepted and introduces an iconographic proposal of some complexity.",
          "The sentence breaks at the page end and continues at p.274 L71; retain partial until that source segment is processed. Note 5 remains pending.",
          [c("competition")], True, 5,
          [{"segment_id": NEXT, "source_line_start": 71, "source_line_end": 71}])

# The preceding cross-page statement from p.272 now closes at p.273 L63.
cov[PREVIOUS].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L54-58",
    "note": "Printed p.272 body L54-58 read against scan. Its Tiepolo sentence closes at p.273 L63; the cross-page payment/loan continuation is recorded in the linked p.273 statement. L59-60 duplicates printed note 3 and is routed to the consolidated notes segment; page marker L53 carries no semantic content.",
})
cov[SEGMENT].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L63-68",
    "note": "Printed p.273 (PDF physical p.39) body L63-68 read against scan. Closes p.272 L58's Tiepolo sentence at L63; L68's Zompini proposal continues at p.274 L71. Printed notes 1-5 remain for the consolidated notes segment. OCR readings corrected only in S2: L64 'seem to.have'→'seem to have', 'Education os'→'Education of'; L65 'alhthere'→'all there'; L68 'inwhichartists'→'in which artists'.",
})

if len({x["mention_id"] for x in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID")
if len({x["statement_id"] for x in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID")

summary = {
    "segment": SEGMENT, "completed_previous": PREVIOUS, "next": NEXT, "status": "reviewed/partial",
    "new_candidates": len(new_candidates), "candidate_ids": [x["candidate_id"] for x in new_candidates],
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "ocr_corrections": [
        {"line": 64, "ocr": "seem to.have / Education os", "print": "seem to have / Education of"},
        {"line": 65, "ocr": "alhthere", "print": "all there"},
        {"line": 68, "ocr": "inwhichartists", "print": "in which artists"},
    ],
    "counts_after": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements), "coverage_rows": len(coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [cp, mp, sp, vp]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for src, dst in zip(paths, backups):
        shutil.copy2(src, dst)
    try:
        write_csv(cp, cf, candidates + new_candidates)
        write_csv(mp, mf, mentions + new_mentions)
        write_jsonl(sp, statements + new_statements)
        write_csv(vp, vf, list(cov.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
