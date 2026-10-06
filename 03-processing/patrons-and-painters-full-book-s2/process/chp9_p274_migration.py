"""Controlled S2 migration for printed p.274 body; defaults to dry-run."""
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
PREVIOUS = "chp-9:09_CHP-9_sec_ii:l62-68"
SEGMENT = "chp-9:09_CHP-9_sec_ii:l70-78"
NEXT = "chp-9:09_CHP-9_sec_ii:l80-83"
PREVIOUS_STATEMENT = "st-chp9-p273-zompini-proposal-accepted-partial"
ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
SEGMENT_SHA = "83927497827eff20a3eb9dfc87075c96affdf5b18f53022088980960c4c868ad"
MAX_CANDIDATE = 8754
BACKUP_SUFFIX = ".bak-s2-chp9-p274-20261001"


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
    raise SystemExit("p.274 source segment missing or changed")
if not lines[69].strip() == "[Page 274]" or not lines[70].startswith("so he claimed") or not lines[77].endswith("various saints."):
    raise SystemExit("expected p.274 text/continuation has changed")
if not lines[67].endswith("drawn,") or not lines[79].strip() == "[Page 275]":
    raise SystemExit("expected p.273/p.275 page boundary has changed")

segment_text = "\n".join(lines[69:78])
offsets, offset = {}, 0
for n in range(70, 79):
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
    raise SystemExit("p.273 is not in expected reviewed/partial state")
if (cov.get(SEGMENT, {}).get("disposition"), cov.get(SEGMENT, {}).get("migration_status")) != ("queued", "pending"):
    raise SystemExit("p.274 is not queued/pending")

E = {
    "corner": "cand-0844", "corner_family": "cand-0847", "angeli": "cand-0106",
    "tiepolo": "cand-2575",
    "casanova": "cand-0591", "jesuits": "cand-3403", "piazzetta": "cand-1901",
    "venice": "cand-2719", "rome": "cand-4490", "virgin": "cand-3427",
    "pieta_church": "cand-8551", "pieta_governors": "cand-8730",
    "zompini": "cand-2874", "zompini_proposal": "cand-8754",
    "corner_portrait": "cand-4053", "sanciano": "cand-0731", "sbasile": "cand-0730",
}
for key, cid in E.items():
    if cid not in candidate_ids:
        raise SystemExit(f"required candidate missing: {key}={cid}")

SPECS = [
    ("rebecca", "Rebecca (biblical figure in Zompini's Virgin programme)", "person", "Biblical figure named as a type of the Virgin in Zompini's proposed iconographic programme; identity alignment remains S3 work.", 72),
    ("abigail", "Abigail (biblical figure in Zompini's Virgin programme)", "person", "Biblical figure named as a type of the Virgin in Zompini's proposed iconographic programme; identity alignment remains S3 work.", 72),
    ("esther", "Esther (biblical figure in Zompini's Virgin programme)", "person", "Biblical figure named both in Zompini's proposed Virgin programme and in the 1743 sermon comparison; do not conflate the two source contexts before S3.", 72),
    ("judith", "Judith (biblical figure in Zompini's Virgin programme)", "person", "Biblical figure named as a type of the Virgin in Zompini's proposed iconographic programme; identity alignment remains S3 work.", 72),
    ("mother_maccabees", "Mother of the Maccabees (unnamed biblical figure in Zompini's Virgin programme)", "person", "Unnamed biblical mother named as a type of the Virgin; retain the source's non-personal proper-name form.", 72),
    ("panegyric", "Jesuit panegyric of the Blessed Virgin comparing her to Esther (1743)", "work", "An unnamed Jesuit sermon reported as preached in 1743; no preacher or independent title is supplied.", 72),
    ("corner_palace", "Unidentified palace associated with Flaminio Corner in Venice", "place", "The source calls this only Corner's palace and does not provide a street or building name; identity remains unresolved.", 75),
    ("corner_relics", "Relic collection associated with Flaminio Corner", "", "Explicitly described as a large collection of relics. Current taxonomy has no collection type; preserve as type-undecided rather than forcing a category.", 75),
    ("sanciano_altarpieces", "Unidentified altarpieces by Giuseppe Angeli at S. Canciano under Flaminio Corner's patronage", "work", "A group of altarpieces is specified by artist, site, and patronal context; individual titles are not supplied.", 77),
    ("sbasile_altarpieces", "Unidentified altarpieces by Giuseppe Angeli at S. Basilio under Flaminio Corner's patronage", "work", "A group of altarpieces is specified by artist, site, and patronal context; individual titles are not supplied.", 77),
    ("pieta_altarpieces", "Unidentified altarpieces by Giuseppe Angeli at the Pietà in Flaminio Corner's patronage context", "work", "A group of altarpieces is specified by artist and site, but the sentence does not name individual works or explain Corner's exact role at the Pietà.", 77),
    ("evangelists_paintings", "Paintings of the Four Evangelists commissioned by Flaminio Corner from Giuseppe Angeli", "work", "Private devotional commission described as plural paintings; no titles, dates, or locations are supplied.", 78),
    ("apostles_series", "Series of the Apostles commissioned by Flaminio Corner from Giuseppe Angeli", "work", "Private devotional series; no title, date, medium, or location is supplied.", 78),
    ("saints_paintings", "Unidentified paintings of various saints commissioned by Flaminio Corner from Giuseppe Angeli", "work", "Private devotional paintings named collectively; individual saints and titles are not supplied.", 78),
    ("aconato", "Beato Pietro Aconato", "person", "Named as the subject of a cult propagated by a group of nobles associated with S. Basilio; further identity work belongs to S3.", 77),
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


mention_specs = [
    ("zompini_he", 71, "zompini", "he", "Continuation of Gaetano Zompini's proposal sentence from p.273 L68.", 0),
    ("virgin", 71, "virgin", "the Virgin", "The Virgin in Zompini's proposed programme.", 0),
    ("rebecca", 71, "rebecca", "Rebecca", "Biblical figure in the proposed typology.", 0),
    ("abigail", 72, "abigail", "Abigail", "Biblical figure in the proposed typology.", 0),
    ("esther_typology", 72, "esther", "Esther", "First occurrence: biblical figure in the proposed typology.", 0),
    ("judith", 72, "judith", "Judith", "Biblical figure in the proposed typology.", 0),
    ("mother_maccabees", 72, "mother_maccabees", "the Mother of the Maccabees", "Unnamed biblical figure in the proposed typology.", 0),
    ("tiepolo", 72, "tiepolo", "Tiepolo", "Comparison artist in the proposal discussion.", 0),
    ("zompini", 72, "zompini", "Zompini", "Artist whose proposal is being described.", 0),
    ("jesuit", 72, "jesuits", "a Jesuit", "The preacher is unnamed; this mention identifies only his religious order.", 0),
    ("panegyric", 72, "panegyric", "a fine panegyric of the Blessed Virgin", "Unnamed sermon reported in the cited 1743 source.", 0),
    ("blessed_virgin", 72, "virgin", "the Blessed Virgin", "Mary as the subject of the reported sermon.", 0),
    ("esther_sermon", 72, "esther", "Esther", "Second occurrence: the sermon reportedly compared the Virgin to Esther.", 1),
    ("pieta", 72, "pieta_church", "the Pietà", "Church named as the setting for a similar plan-selection practice.", 0),
    ("pieta_governors", 72, "pieta_governors", "the governors", "Governors of the Pietà; not the Scuola del Carmine governors from p.273.", 0),
    ("venice_patron", 73, "venice", "Venice", "City context for Corner's patronage.", 0),
    ("corner_intro", 73, "corner", "he", "Pronoun in the introductory phrase refers to Flaminio Corner, named on the following source line.", 0),
    ("flaminio", 73, "corner", "Flaminio", "Start of the name Flaminio Corner, which continues on the following source line.", 0),
    ("corner_name_continuation", 74, "corner", "Corner", "Continuation of the name Flaminio Corner from the preceding source line.", 0),
    ("portrait", 74, "corner_portrait", "Plate 48a", "Cross-reference to the existing Flaminio Corner portrait candidate; the image itself is handled in the plates segment.", 0),
    ("corner_rigid", 74, "corner", "he", "Refers to Flaminio Corner.", 0),
    ("casanova", 74, "casanova", "Casanova", "Casanova de Seingalt as the speaker quoted by Haskell.", 0),
    ("corner_reputation", 74, "corner", "sa reputation était sans tache", "Quoted description of Corner's reputation; nested speech attributed to Casanova. Scan reads French accent in 'réputation'; original OCR is retained in S0.", 0),
    ("corner_educated", 74, "corner", "He", "Refers to Flaminio Corner.", 0),
    ("jesuits_education", 74, "jesuits", "the Jesuits", "Religious order that educated Corner.", 0),
    ("corner_family", 75, "corner_family", "his family", "The Corner family; keep family distinct from Flaminio Corner as an individual.", 0),
    ("venice_family", 75, "venice", "Venice", "City in the source's description of the family's antiquity.", 0),
    ("corner_palace", 75, "corner_palace", "his palace", "Unidentified palace associated with Corner; do not infer its proper name.", 0),
    ("corner_relics", 75, "corner_relics", "a prodigious quantity of relics", "Collection has no current taxonomy type; candidate remains type-undecided.", 0),
    ("corner_patronage", 75, "corner", "his patronage", "Refers to Corner's patronage.", 0),
    ("artist_especially", 75, "angeli", "one artist especially", "Coreference to Giuseppe Angeli named later in the same sentence.", 0),
    ("angeli_named", 75, "angeli", "Giuseppe Angeli", "Index candidate A.csv#107; identity alignment remains S3 work.", 0),
    ("angeli_pupil", 75, "angeli", "Angeli", "Artist evaluated as Piazzetta's pupil.", 0),
    ("piazzetta_pupils", 75, "piazzetta", "Piazzetta’s pupils", "Piazzetta named as Angeli's master.", 0),
    ("piazzetta_master", 75, "piazzetta", "his master", "Possessive reference identifies Piazzetta as Angeli's master.", 0),
    ("piazzetta_latter", 75, "piazzetta", "the latter’s", "Refers to Piazzetta in the phrase about his death in 1754.", 0),
    ("angeli_process", 75, "angeli", "he", "Refers to Angeli in the account of stylistic transformation.", 0),
    ("rome", 76, "rome", "Rome", "City used in Haskell's comparison with Venetian painters.", 0),
    ("venetian_painters", 76, "venice", "Venetian painters", "Regional adjective refers to painters of Venice.", 0),
    ("corner_employ", 76, "corner", "Flaminio Corner", "Patron named as employing Angeli on altarpieces.", 0),
    ("angeli_employ", 76, "angeli", "him", "Angeli is the object of Corner's employment claim.", 0),
    ("sanciano_altarpieces", 76, "sanciano_altarpieces", "altarpieces", "Unidentified Angeli altarpieces at S. Canciano.", 0),
    ("sanciano", 76, "sanciano", "S. Canciano", "Corner's parish church.", 0),
    ("sbasile_altarpieces", 76, "sbasile_altarpieces", "S. Basilio", "Site of further Angeli altarpieces in Corner's patronage context.", 0),
    ("corner_nobles", 76, "corner", "he", "The relative clause's antecedent is ambiguous; do not assert Corner's membership in the group as settled.", 0),
    ("aconato", 76, "aconato", "Beato Pietro Aconato", "Named object of the cult promoted by an unnamed group of nobles.", 0),
    ("pieta_altarpieces", 77, "pieta_altarpieces", "Pietà", "Location of further Angeli altarpieces; exact works are unidentified.", 0),
    ("corner_private", 77, "corner", "his own private devotions", "Corner's private devotional context.", 0),
    ("angeli_private", 77, "angeli", "Angeli", "Artist named as recipient of Corner's devotional commissions.", 0),
    ("evangelists", 78, "evangelists_paintings", "Four Evangelists", "Subject of a group of paintings commissioned from Angeli; the preceding line ends with the article 'the'.", 0),
    ("apostles", 78, "apostles_series", "a series of the Apostles", "Unidentified series commissioned from Angeli.", 0),
    ("saints", 78, "saints_paintings", "various saints", "Collective description of devotional paintings; individual figures are not identified.", 0),
]
for mid, n, key, surface, note, occurrence in mention_specs:
    mention(f"m-chp9-p274-{mid}", n, c(key) if key in C else e(key), surface, note, occurrence)

new_statements = []


def excerpt(a, b, start, end):
    chunks = lines[a - 1:b]
    left = chunks[0].index(start)
    right = chunks[-1].index(end) + len(end)
    if a == b:
        return chunks[0][left:right]
    chunks[0] = chunks[0][left:]
    chunks[-1] = chunks[-1][:right]
    return "\n".join(chunks)


def statement(sid, a, b, sub, obj, pred, quote, claim, qualification, refs=(), rel=False, fn=None, cross=(), quoted_speaker=None):
    if sid in statement_ids or any(x["statement_id"] == sid for x in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored: {sid}")
    refs = set(refs) | {x for x in (sub, obj) if x}
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(refs - candidate_ids)}")
    q = {
        "source_line_start": a, "source_line_end": b, "printed_page": 274, "pdf_physical_page": 40,
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
    if quoted_speaker:
        q["quoted_speaker"] = quoted_speaker
    new_statements.append({
        "statement_id": sid, "segment_id": SEGMENT, "subject_candidate_id": sub,
        "object_candidate_id": obj, "predicate": pred, "qualifiers": q,
        "original_quote": quote, "source_file": SOURCE.relative_to(ROOT).as_posix(), "origin": "book",
    })


statement("st-chp9-p274-zompini-fathers-reading", 71, 71, e("zompini"), e("zompini_proposal"),
          "zompini_proposal_claimed_to_draw_on_church_fathers", excerpt(71, 71, "so he claimed", "Church fathers."),
          "Haskell says Zompini claimed that his proposal was drawn from a reading of the Church Fathers.",
          "Closes the proposal sentence begun at p.273 L68; retain the attribution to Zompini rather than asserting direct access to the Fathers.",
          [e("tiepolo")], True, None, [{"segment_id": PREVIOUS, "source_line_start": 68, "source_line_end": 68}])
statement("st-chp9-p274-zompini-virgin-typology", 71, 72, e("zompini"), e("virgin"),
          "zompini_proposed_virgin_glorification_using_old_testament_figures", excerpt(71, 72, "This was to be a glorification", "Mother of the Maccabees."),
          "Haskell describes Zompini's proposal as a glorification of the Virgin prefigured by Rebecca, Abigail, Esther, Judith, and the Mother of the Maccabees.",
          "These are typological figures named by the source; the Mother of the Maccabees is unnamed. Preserve the proposal as a plan, not a completed artwork.",
          [c("rebecca"), c("abigail"), c("esther"), c("judith"), c("mother_maccabees")], True)
statement("st-chp9-p274-1743-jesuit-panegyric", 72, 72, None, c("panegyric"),
          "jesuit_preached_virgin_panegyric_comparing_her_to_esther_in_1743", excerpt(72, 72, "we know that", "her to Esther’.1"),
          "Haskell reports that in 1743 an unnamed Jesuit preached a panegyric of the Blessed Virgin comparing her to Esther.",
          "The preacher is not identified. The footnote's cited source is still pending transcription and review in the consolidated notes segment.",
          [e("jesuits"), e("virgin"), c("esther")], True, 1)
statement("st-chp9-p274-programmes-followed-artist-initiative", 72, 72, None, None,
          "eighteenth_century_iconographic_programmes_adhered_to_but_left_artist_initiative", excerpt(72, 72, "In any case", "left to the artist."),
          "Haskell argues that the long plans show iconographic programmes remained rigorous in the eighteenth century while leaving initiative to artists.",
          "This is Haskell's generalizing interpretation of the submitted plans, not a claim about every eighteenth-century commission.",
          [e("tiepolo"), e("zompini"), e("zompini_proposal")])
statement("st-chp9-p274-pieta-governors-sought-plans", 72, 72, e("pieta_governors"), None,
          "pieta_governors_required_to_seek_and_choose_painter_plans", excerpt(72, 72, "A similar practice", "choose the best’.2"),
          "Haskell says a similar plan-selection practice appears to have been followed at the Pietà: its governors were required to seek plans from highly regarded painters with suitable ideas and choose the best.",
          "The passage says 'seems'; preserve that qualification. Footnote 2 remains pending in the consolidated notes segment.",
          [e("pieta_church")], True, 2)
statement("st-chp9-p274-corner-religious-patron", 73, 73, e("corner"), None,
          "flaminio_corner_patron_of_religious_art_with_decided_views", excerpt(73, 73, "We know of one patron", "through no fault of his own."),
          "Haskell presents Flaminio Corner as a Venetian patron of religious art with decided views, noting that he was not himself a priest.",
          "The ironic phrase 'through no fault of his own' is retained without inventing a reason for his not becoming a priest.",
          [e("venice")], False, 3)
statement("st-chp9-p274-corner-born-1693", 74, 74, e("corner"), None,
          "flaminio_corner_born_1693", excerpt(74, 74, "was born in 1693", "1693.3"),
          "Haskell gives Flaminio Corner's birth year as 1693.",
          "Reported by Haskell; biographical footnote 3 remains pending in the consolidated notes segment.", fn=3)
statement("st-chp9-p274-casanova-corner-reputation", 74, 74, e("casanova"), e("corner"),
          "casanova_described_corner_reputation_as_untarnished", excerpt(74, 74, "So rigid was he", "sa reputation était sans tache’.4"),
          "Haskell says Corner was so rigid and unbending that Casanova admitted his reputation was spotless.",
          "Casanova's French phrase is nested quotation; retain Haskell's characterization and the cited attribution. Footnote 4 remains pending.",
          [], True, 4, quoted_speaker="Casanova")
statement("st-chp9-p274-corner-jesuit-education", 74, 74, e("corner"), e("jesuits"),
          "corner_educated_by_jesuits", excerpt(74, 74, "He had been educated", "educated by the Jesuits"),
          "Haskell says Corner was educated by the Jesuits.",
          "Biographical statement; note 3's source scope remains pending.", [e("venice")], True, 3)
statement("st-chp9-p274-corner-monastery-intention", 74, 74, e("corner"), None,
          "corner_as_young_man_wanted_to_enter_monastery", excerpt(74, 74, "as a young man", "wanted to enter a monastery."),
          "Haskell says Corner wanted to enter a monastery when he was young.",
          "Intention only; the source does not say that he entered a monastery.", fn=3)
statement("st-chp9-p274-corner-marriage-family", 75, 75, e("corner"), e("corner_family"),
          "corner_reluctantly_married_after_family_deaths_to_prevent_extinction", excerpt(75, 75, "But after the death", "oldest in Venice."),
          "Haskell says that after his parents and elder brother died, Corner reluctantly agreed to marry to prevent the extinction of his family, described as one of Venice's oldest.",
          "The parents and brother are unnamed; do not infer marriage date or descendants. Biographical source note 3 remains pending.", [e("venice")], True, 3)
statement("st-chp9-p274-corner-latin-books", 75, 75, e("corner"), None,
          "corner_wrote_scholarly_latin_books_on_early_venetian_church_history", excerpt(75, 75, "Most of his life", "churches;"),
          "Haskell says much of Corner's life was devoted to writing scholarly books in Latin about the early history of Venetian churches.",
          "No book titles are supplied; do not create separate works from an unnamed plural corpus. Note 3 remains pending.", [e("venice")], False, 3)
statement("st-chp9-p274-corner-palace-relics", 75, 75, e("corner"), c("corner_relics"),
          "corner_collected_relics_at_his_palace_frequented_by_clergy_and_learned", excerpt(75, 75, "his palace", "the learned."),
          "Haskell says Corner's palace contained a very large quantity of relics and was frequented especially by clergy and learned visitors.",
          "The palace name and relic collection's formal type are not supplied. Note 5, which gives a Correr manuscript quotation, remains pending in the consolidated notes segment.",
          [c("corner_palace"), e("venice")], False, 5)
statement("st-chp9-p274-corner-employed-angeli", 75, 75, e("corner"), e("angeli"),
          "corner_seems_to_patronize_religious_painting_and_sculpture_and_employ_angeli", excerpt(75, 75, "He seems to have extended", "Giuseppe Angeli."),
          "Haskell says Corner seems to have patronized religious paintings and sculpture exclusively and employed Giuseppe Angeli especially for them.",
          "Retain 'seems' and the author's scope; no individual works are named in this sentence.", [], True, 3)
statement("st-chp9-p274-angeli-best-pupil", 75, 75, e("angeli"), e("piazzetta"),
          "angeli_considered_best_of_piazzettas_pupils", excerpt(75, 75, "Angeli was considered", "Piazzetta’s pupils,"),
          "Haskell says Angeli was considered the best of Piazzetta's pupils.",
          "A reported evaluative judgement; 'considered' does not identify who held the view.", [e("corner")], True, 3)
statement("st-chp9-p274-angeli-imitated-piazzetta", 75, 75, e("angeli"), e("piazzetta"),
          "angeli_imitated_piazzettas_style_after_1754_and_focused_on_religious_painting", excerpt(75, 75, "and he imitated", "religious painting."),
          "Haskell says Angeli imitated Piazzetta's style long after Piazzetta's death in 1754 and confined himself almost entirely to religious painting.",
          "The temporal phrase is relative, not a date for any specific work. Note 3 remains pending.", [e("corner")], True, 3)
statement("st-chp9-p274-angeli-style-softened", 75, 75, e("angeli"), e("piazzetta"),
          "haskell_characterized_angeli_style_as_softened_intimate_and_sentimental", excerpt(75, 75, "In the process", "early paintings."),
          "Haskell describes Angeli as softening Piazzetta's style, making it more intimate and sentimental, and developing this into 'pietestic mawkishness' far from the pride and grandeur of Piazzetta's early paintings.",
          "Explicitly an authorial aesthetic judgement, not a neutral fact. Footnote 6 remains pending in the consolidated notes segment.", [e("corner")], False, 6)
statement("st-chp9-p274-angeli-compared-to-roman-counterreformation", 75, 76, e("angeli"), None,
          "angeli_compared_to_seventeenth_century_roman_counter_reformation_artists", excerpt(75, 76, "In many ways", "painters of his time."),
          "Haskell says Angeli is in many ways closer to seventeenth-century Roman Counter-Reformation artists than to contemporary Venetian painters.",
          "Comparative judgement by Haskell; the unnamed group is not made into a separate formal organization.", [e("rome"), e("venice"), e("piazzetta")])
statement("st-chp9-p274-corner-angeli-sanciano", 76, 76, e("corner"), c("sanciano_altarpieces"),
          "corner_employed_angeli_on_altarpieces_at_s_canciano", excerpt(76, 76, "Flaminio Corner thought very highly", "S. Canciano"),
          "Haskell says Corner highly valued Angeli and employed him on altarpieces in his parish church of S. Canciano.",
          "Individual altarpiece titles and dates are not supplied; footnote 3 remains pending.", [e("angeli"), e("sanciano")], True, 3)
statement("st-chp9-p274-corner-angeli-sbasile", 76, 76, e("corner"), c("sbasile_altarpieces"),
          "corner_employed_angeli_on_altarpieces_at_s_basilio", excerpt(76, 76, "as well as in S. Basilio", "S. Basilio"),
          "Haskell includes altarpieces by Angeli at S. Basilio among works for which Corner employed him.",
          "The adjacent relative clause about a group of nobles is kept separate because its pronoun antecedent is not fully clear.", [e("angeli"), e("sbasile")], True, 3)
statement("st-chp9-p274-sbasile-nobles-aconato-cult", 76, 76, None, c("aconato"),
          "unnamed_nobles_at_s_basilio_devoted_to_propagating_aconato_cult", excerpt(76, 76, "where he was one of a group of nobles", "Beato Pietro Aconato,"),
          "Haskell says a group of nobles associated with S. Basilio was devoted to propagating the cult of Beato Pietro Aconato.",
          "The pronoun 'he' may refer to Flaminio Corner in the relative clause; preserve the ambiguity and do not assert Angeli was one of the nobles.",
          [e("corner"), e("angeli"), e("sbasile")], True, 3)
statement("st-chp9-p274-corner-angeli-pieta", 76, 77, e("corner"), c("pieta_altarpieces"),
          "corner_employed_angeli_on_altarpieces_at_the_pieta", excerpt(76, 77, "and in the", "Pietà."),
          "Haskell also places Angeli altarpieces in the Pietà in the list of works Corner employed him on.",
          "The source does not specify individual works or Corner's precise role at the Pietà; retain this as a book relation candidate only.", [e("angeli"), e("pieta_church")], True, 3)
statement("st-chp9-p274-corner-angeli-evangelists", 77, 78, e("corner"), c("evangelists_paintings"),
          "corner_commissioned_angeli_paintings_of_four_evangelists_for_private_devotion", excerpt(77, 78, "For his own private devotions", "Four Evangelists,"),
          "Haskell says Corner commissioned paintings of the Four Evangelists from Angeli for private devotion.",
          "No titles, dates, or locations are supplied. The source's sentence begins on L77 and continues on L78.", [e("angeli")], True, 3)
statement("st-chp9-p274-corner-angeli-apostles", 78, 78, e("corner"), c("apostles_series"),
          "corner_commissioned_angeli_apostles_series_for_private_devotion", excerpt(78, 78, "a series of the Apostles", "Apostles"),
          "Haskell says Corner commissioned a series of the Apostles from Angeli for private devotion.",
          "The series title and location are not supplied.", [e("angeli")], True, 3)
statement("st-chp9-p274-corner-angeli-saints", 78, 78, e("corner"), c("saints_paintings"),
          "corner_commissioned_angeli_paintings_of_various_saints_for_private_devotion", excerpt(78, 78, "various saints", "various saints."),
          "Haskell says Corner also commissioned paintings of various saints from Angeli for private devotion.",
          "Individual saints and work titles are not named.", [e("angeli")], True, 3)

# Close p.273's Zompini sentence using the continuation at p.274 L71.
prev_statement = next((x for x in statements if x["statement_id"] == PREVIOUS_STATEMENT), None)
if prev_statement is None:
    raise SystemExit("p.273 Zompini continuation statement is missing")
prev_statement["predicate"] = "zompini_iconographic_proposal_accepted_and_program_introduced"
prev_statement["qualifiers"]["claim"] = "Haskell says Gaetano Zompini's idea was accepted and introduces his iconographic proposal, whose sentence concludes at p.274 L71."
prev_statement["qualifiers"]["qualification"] = "The proposal's description continues on p.274 L71; the cited footnote 5 remains pending in the consolidated notes segment."
prev_refs = set(prev_statement["qualifiers"].get("mentioned_candidate_ids", []))
prev_refs.add(e("zompini"))
prev_refs.add(e("zompini_proposal"))
prev_statement["qualifiers"]["mentioned_candidate_ids"] = sorted(prev_refs)
prev_cross = prev_statement["qualifiers"].setdefault("cross_reference_segments", [])
if not any(x.get("segment_id") == SEGMENT for x in prev_cross):
    prev_cross.append({"segment_id": SEGMENT, "source_line_start": 71, "source_line_end": 71})

cov[PREVIOUS].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L63-68",
    "note": "Printed p.273 body L63-68 read against scan. Closes p.272 L58's Tiepolo sentence at L63 and the Zompini proposal sentence at p.274 L71; printed notes 1-5 remain for the consolidated notes segment. OCR readings corrected only in S2: L64 'seem to.have'→'seem to have', 'Education os'→'Education of'; L65 'alhthere'→'all there'; L68 'inwhichartists'→'in which artists'.",
})
cov[SEGMENT].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L71-78",
    "note": "Printed p.274 body (PDF physical p.40) read against scan. L71 closes p.273 L68's Zompini proposal sentence. Records Virgin typology, the 1743 Jesuit sermon, Pietà plan selection, Flaminio Corner's patronage and biography, Giuseppe Angeli's style and commissions. Notes 1-6 are in the consolidated notes segment and remain pending; note markers are linked to the applicable statements. The S. Basilio relative clause does not settle whether 'he' refers to Corner or Angeli; membership in the nobles' group is not asserted for either individual.",
})

if len({x["mention_id"] for x in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID")
if len({x["statement_id"] for x in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID")

summary = {
    "segment": SEGMENT, "completed_previous": PREVIOUS, "next": NEXT, "status": "reviewed/complete",
    "new_candidates": len(new_candidates), "candidate_ids": [x["candidate_id"] for x in new_candidates],
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "closed_statement": PREVIOUS_STATEMENT,
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
