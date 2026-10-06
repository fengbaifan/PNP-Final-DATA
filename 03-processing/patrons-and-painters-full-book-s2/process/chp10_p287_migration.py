"""Controlled S2 migration for printed p.287; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l190-204"
SEG = "chp-10:10_CHP-10_intro:l206-216"
NEXT = "chp-10:10_CHP-10_intro:l218-227"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "cb2f0e7d80f4c70cbb83c83eac8ed51a71f918a608f83a328fb8a8934b8d0d33"
BACKUP = ".bak-s2-chp10-p287-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[205:216])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != SEG_SHA or src[205].strip() != "[Page 287]":
    raise SystemExit("p.287 source segment hash/page mismatch")

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
if maximum != 9004:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "amigoni": "cand-0094", "sleter": "cand-2439", "mcswiny": "cand-1466",
    "nazari": "cand-1727", "fielding": "cand-1035", "richmond": "cand-2193",
    "jupiter": "cand-4178", "io": "cand-4179", "van_dyck": "cand-8909",
    "europe": "cand-3462", "england": "cand-8983", "history_painting": "cand-4630",
    "venetian_artists": "cand-8104", "vertue_notebooks": "cand-7255",
    "moor_park_decoration": "cand-9004",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("joseph_andrews", "Henry Fielding's Joseph Andrews", "archive",
     "Novel invoked by Haskell and quoted in note 2; the passage uses a satirical list of mock painter names.", 209),
    ("van_dyck_portrait_plan", "McSwiny's unrealized plan for engraved Van Dyck portraits in English country houses", "work",
     "A proposed series of engravings that came to nothing; the passage says McSwiny later returned to a similar plan.", 212),
    ("mcswiny_tomb_scheme", "McSwiny's proposed allegorical tomb series for England's recent great men", "work",
     "A proposed commission on behalf of Lord March; the passage does not say that the paintings were executed.", 213),
    ("glorious_revolution", "Glorious Revolution of 1688", "event",
     "Named as a point from which Haskell measures England's progress; retain the author's interpretation.", 214),
    ("mcswiny_italian_artists", "Leading Italian artists proposed for McSwiny's allegorical tomb scheme (unnamed group)", "term",
     "Collective group in a proposal; no individual artists or completed commissions are identified.", 213),
    ("woodward_amigoni_article", "J. Woodward, ‘Amigoni as portrait painter in England’ (1957)", "archive",
     "Bibliography identifies the article; note 2 cites pp. 21–23, not independently read here.", 215),
    ("haskell_1960_note2_source", "Unidentified Haskell 1960 source cited in note 2 (pp. 71–73)", "archive",
     "The note supplies author, year and pages; the exact bibliographic work is unresolved and is not inferred from nearby bibliography entries.", 215),
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
                 "candidate_source_ref": f"{SEG}#L{line}"})

moor_work = next(row for row in candidates if row["candidate_id"] == E["moor_park_decoration"])
if moor_work["canonical_name"] != "Unidentified decoration commission for Styles's Moor Park house":
    raise SystemExit("unexpected Moor Park work candidate")
if moor_work["detail"] != "The job intended for Thornhill and later assigned elsewhere; the next page identifies the recipients and canvases.":
    raise SystemExit("Moor Park work candidate detail changed")
moor_work["detail"] = "The job intended for Thornhill and assigned to Amigoni and Francesco Sleter; p.287 identifies four untitled Jupiter and Io canvases associated with the commission."

offsets, offset = {}, 0
for line in range(206, 217):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p287-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    positions, at = [], 0
    while True:
        at = src[line - 1].find(surface, at)
        if at < 0:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}")
    start = offsets[line] + positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("amigoni_closure",207,"Amigoni",E["amigoni"],"Closes p.286's open assignment sentence."),
    ("sleter_closure",207,"Francesco Sleter",E["sleter"],"Recipient of the Moor Park job alongside Amigoni."),
    ("amigoni_canvases",208,"Amigoni’s",E["amigoni"],"Painter of the four canvases."),
    ("four_canvases",208,"four canvases",E["moor_park_decoration"],"The p.287 continuation identifies the canvases associated with the Moor Park commission; no individual titles are supplied."),
    ("jupiter",208,"Jupiter",E["jupiter"],"Mythological subject, not a historical event."),
    ("io",208,"Io",E["io"],"Mythological subject; candidate already occurs in the book's plate list."),
    ("amigoni_career",209,"Amigoni’s",E["amigoni"],"Subject of the career account."),
    ("england_departure",209,"England",E["england"],"Place Amigoni left."),
    ("fielding",209,"Fielding’s",E["fielding"],"Author named in connection with Joseph Andrews."),
    ("joseph_main",209,"Joseph Andrews",C["joseph_andrews"],"Literary work invoked in Haskell's summary of Amigoni's reputation."),
    ("english",210,"The English",E["england"],"Generalized patrons in Haskell's account; not an assertion about the state."),
    ("venetian_painters",210,"Venetian painters",E["venetian_artists"],"Collective category; the passage does not name the exceptions."),
    ("nazari_first",210,"Bartolommeo",E["nazari"],"First part of a name split across the source line break."),
    ("nazari_second",211,"Nazari",E["nazari"],"Continuation of Bartolommeo across the source line break."),
    ("mcswiny_full",211,"Owen McSwiny",E["mcswiny"],"Subject of the biography and patronage account."),
    ("mcswiny_art",212,"McSwiny",E["mcswiny"],"Subject of the proposed engraving project."),
    ("van_dyck",212,"Van Dyck",E["van_dyck"],"Artist invoked through the proposed portrait engravings."),
    ("mcswiny_departure",212,"he",E["mcswiny"],"Pronoun refers to McSwiny."),
    ("continent",212,"the Continent",E["europe"],"Broad geographic expression; no destination country is inferred."),
    ("march",212,"Lord March",E["richmond"],"Title/name used for the patron; same in-text referent as the Duke of Richmond named next."),
    ("richmond_title",213,"Duke of Richmond",E["richmond"],"The text explicitly says Lord March became Duke of Richmond in 1723."),
    ("leading_italians",213,"leading Italian artists",C["mcswiny_italian_artists"],"Unnamed proposed group; do not infer individual membership."),
    ("england_tombs",213,"England’s",E["england"],"Country whose recent great men were to be commemorated."),
    ("england_progress",214,"England",E["england"],"Subject of Haskell's periodizing account."),
    ("europe_forefront",214,"Europe",E["europe"],"Geographic comparison in Haskell's interpretation."),
    ("glorious_revolution",214,"Glorious Revolution of 1688",C["glorious_revolution"],"Historical event named by Haskell."),
    ("vertue_ocr",215,"Verrue",E["vertue_notebooks"],"OCR form; printed footnote reads Vertue, vol. III, p.94."),
    ("woodward",215,"Woodward",C["woodward_amigoni_article"],"Named bibliographic citation; title identified from the book bibliography."),
    ("haskell_source",215,"Haskell",C["haskell_1960_note2_source"],"Note 2 citation, distinct from Haskell as narrator; exact work unresolved."),
    ("joseph_note",215,"Joseph Andrews",C["joseph_andrews"],"Book named in the note's direct citation to Book III, Chapter 6."),
]
for item in MENTIONS:
    add_m(*item)

new_s = []


def quote(start, end):
    first = body.find(start)
    if first < 0:
        raise SystemExit(f"quote start absent: {start!r}")
    last = body.find(end, first)
    if last < 0:
        raise SystemExit(f"quote end absent: {end!r}")
    return body[first:last + len(end)]


def add_s(sid, lo, hi, subject, obj, predicate, start, end, claim, qualification,
          mentioned, speaker="Haskell", layer="authorial narrative", relation=False,
          footnote=None, cross=None):
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 287,
                  "pdf_physical_page": 16, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = footnote != 2
    if cross:
        qualifiers["cross_reference_segments"] = cross
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


open_st = next((row for row in statements if row["statement_id"] == "st-chp10-p286-moor-park-decoration-open"), None)
if not open_st or open_st["segment_id"] != PREV:
    raise SystemExit("expected p.286 Moor Park continuation statement missing")
open_st["qualifiers"]["claim"] = "Haskell says Styles intended to entrust Thornhill with the Moor Park decoration, but after they quarrelled Styles assigned the job to Amigoni and Francesco Sleter instead."
open_st["qualifiers"]["qualification"] = "The assignment outcome is now closed by p.287 L207; the next sentence praises Amigoni's four canvases but does not individually title them."
open_st["qualifiers"]["continuation_quote"] = "Amigoni and Francesco Sleter instead."
open_st["qualifiers"]["cross_reference_segments"] = [{"segment_id": SEG, "source_line_start": 207, "source_line_end": 207}]
open_st["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(open_st["qualifiers"].get("mentioned_candidate_ids", []) + [E["amigoni"], E["sleter"]]))

add_s("st-chp10-p287-amigoni-canvases",207,208,E["amigoni"],E["moor_park_decoration"],
      "amigoni_moor_park_canvases_depicted_jupiter_and_io_and_were_his_most_beautiful_english_works",
      "We can be grateful for the dispute", "painted in England (Plate 49b).",
      "Haskell praises Amigoni's four canvases depicting Jupiter and Io as the most beautiful works he painted in England.",
      "This is Haskell's aesthetic judgment. The canvases are not individually titled; note 1 remains pending in the consolidated notes source.",
      [E["amigoni"],E["moor_park_decoration"],E["jupiter"],E["io"]],layer="authorial aesthetic evaluation",footnote=1)
add_s("st-chp10-p287-amigoni-career-shift",209,209,E["amigoni"],None,
      "amigoni_last_major_commission_accidental_and_shifted_toward_portraiture",
      "Thus, Amigoni’s last big commission", "turn more and more to portraiture.",
      "Haskell says Amigoni's last major commission resulted primarily from an accident, after which he struggled to obtain history-painting employment and increasingly turned to portraiture.",
      "Preserve Haskell's causal wording and distinguish the broad career account from a specific named commission.",
      [E["amigoni"],E["history_painting"]],footnote=2)
add_s("st-chp10-p287-amigoni-income",209,209,E["amigoni"],None,
      "amigoni_supposedly_left_england_with_4000_to_5000_some_from_court_work",
      "In this field his success", "derived from his work for the court.",
      "Haskell says Amigoni was very successful in portraiture and was supposed to have taken £4,000–£5,000 when he left England about ten years after arriving, some of the money deriving from court work.",
      "Both the departure interval and the reported sum are qualified as approximate or supposed; the court and work are not identified. Printed amount restores OCR-omitted currency symbol and comma.",
      [E["amigoni"],E["england"]],footnote=2,relation=True)
add_s("st-chp10-p287-amigoni-reputation",209,209,E["amigoni"],C["joseph_andrews"],
      "amigoni_reputation_reached_fieldings_joseph_andrews",
      "He also left a reputation", "Fielding’s Joseph Andrews.",
      "Haskell says Amigoni left a reputation that extended to Fielding's Joseph Andrews.",
      "The body text does not itself specify the novel's passage; note 2 identifies Book III, Chapter 6 and quotes a satirical list of mock painter names.",
      [E["amigoni"],E["fielding"],C["joseph_andrews"]],footnote=2,relation=True)
add_s("st-chp10-p287-venetian-patronage",210,211,E["england"],E["venetian_artists"],
      "english_patronage_mostly_limited_venetian_painters_to_views_landscapes_and_portraits",
      "The English went on employing Venetian painters", "how quickly English taste had hardened into a conventional pattern.",
      "Haskell says English patrons continued to employ Venetian painters but, with rare exceptions, confined their work to views, landscapes and portraits, usually by Bartolommeo Nazari; he presents McSwiny's isolation as evidence of quickly hardened English taste.",
      "This is a generalization in Haskell's narrative with an explicit rare-exceptions qualification; the split printed name Bartolommeo Nazari spans L210–211.",
      [E["england"],E["venetian_artists"],E["nazari"],E["mcswiny"]],footnote=3,relation=True)
add_s("st-chp10-p287-mcswiny-stage-career",211,212,E["mcswiny"],None,
      "mcswiny_irish_actor_dramatist_impresario_without_lasting_success",
      "Owen McSwiny", "a lasting success",
      "Haskell identifies McSwiny as Irish and says his early life was closely connected with the stage as actor, dramatist and eventually impresario; he says none of those careers was a lasting success.",
      "This summarizes Haskell's biographical narrative and evaluation; note 4's supporting references remain pending.",
      [E["mcswiny"]],footnote=4)
add_s("st-chp10-p287-van-dyck-engraving-plan",212,212,E["mcswiny"],C["van_dyck_portrait_plan"],
      "mcswiny_first_art_venture_was_plan_for_engraved_van_dyck_portraits",
      "his first venture into the world of art", "English country house-s.",
      "Haskell says McSwiny's first art venture was a plan to have a series of Van Dyck portraits engraved for English country houses.",
      "The plan is distinct from the portraits and the engravings are not said to have been made; note 5 remains pending.",
      [E["mcswiny"],E["van_dyck"],C["van_dyck_portrait_plan"]],footnote=5,relation=True)
add_s("st-chp10-p287-van-dyck-plan-failed",212,212,E["mcswiny"],C["van_dyck_portrait_plan"],
      "engraving_project_failed_but_mcswiny_returned_to_similar_plan",
      "This project too came to nothing", "returned to a similar plan in later years.",
      "Haskell says the engraving project came to nothing but fascinated McSwiny, who returned to a similar plan in later years.",
      "A later similar plan is reported but not specified or assumed to be the same executed project.",
      [E["mcswiny"],C["van_dyck_portrait_plan"]],footnote=5,relation=True)
add_s("st-chp10-p287-mcswiny-departure",212,212,E["mcswiny"],None,
      "mcswiny_left_for_continent_about_1711_due_to_debts_and_later_reemerged",
      "Meanwhile his debts were pressing", "it was with a scheme of great originality.",
      "Haskell says McSwiny's debts were pressing and he left for the Continent about 1711, disappeared for a few years, then re-emerged with an original scheme.",
      "The date is approximate and the destination is not narrowed to a particular country; 'disappeared from sight' describes the narrative record.",
      [E["mcswiny"],E["europe"]])
add_s("st-chp10-p287-mcswiny-tomb-scheme",212,213,E["mcswiny"],C["mcswiny_tomb_scheme"],
      "mcswiny_on_behalf_of_lord_march_proposed_tombs_painted_by_leading_italian_artists",
      "Acting on behalf of Lord March", "England’s recent history.",
      "Haskell says McSwiny, acting for Lord March (later Duke of Richmond), proposed that leading Italian artists paint a series of allegorical tombs commemorating England's recently great men.",
      "This is a proposal, not evidence that the series was executed. The unnamed artist group remains collective; the in-text Lord March to Duke of Richmond succession is explicit, while global identity matching remains for S3.",
      [E["mcswiny"],E["richmond"],C["mcswiny_italian_artists"],C["mcswiny_tomb_scheme"],E["england"]],footnote=6,relation=True)
add_s("st-chp10-p287-english-optimism",214,214,E["england"],E["europe"],
      "haskell_links_english_optimism_to_military_political_and_intellectual_triumphs",
      "McSwiny had judged his moment well", "the very forefront of Europe.",
      "Haskell attributes a generation of English optimism to military, political and intellectual triumphs and says they carried England to the forefront of Europe.",
      "This is Haskell's interpretive periodization, not a quantified measure of national position.",
      [E["england"],E["europe"]])
add_s("st-chp10-p287-glorious-revolution-progress",214,214,E["england"],C["glorious_revolution"],
      "haskell_says_english_progress_since_glorious_revolution_was_immense",
      "Everyone recognised", "since the Glorious Revolution of 1688 had been immense,",
      "Haskell says England's progress since the Glorious Revolution of 1688 had been immense.",
      "The statement records Haskell's characterization and does not independently validate it.",
      [E["england"],C["glorious_revolution"]])
add_s("st-chp10-p287-celebration-timing",214,214,None,None,
      "time_to_celebrate_recent_english_exploits_as_protagonists_grew_old_or_died",
      "but now the protagonists were old", "celebrate their exploits.",
      "Haskell says that because the protagonists were old or already dead, the time had come to celebrate their exploits.",
      "The people are not individually named in this passage; this is the author's explanation for the commemorative moment.",
      [E["england"]])
add_s("st-chp10-p287-wealth-peace-open",214,214,E["england"],E["europe"],
      "wealth_at_home_and_peace_in_europe_encouraged_english_noblemen_open",
      "Meanwhile wealth at home and peace in Europe were encouraging", "Meanwhile wealth at home and peace in Europe were encouraging",
      "Haskell begins a statement that domestic wealth and European peace were encouraging English actors; the sentence continues on p.288.",
      "Partial sentence: do not complete the object or infer the action until the next source segment is read.",
      [E["england"],E["europe"]],cross=[{"segment_id":NEXT,"source_line_start":219,"source_line_end":219}])
add_s("st-chp10-p287-footnote-2",215,216,None,C["joseph_andrews"],
      "note_2_cites_sources_on_amigoni_and_quotes_joseph_andrews_satirical_painter_names",
      "Verrue, III, p. 94", "I suppose were the names of the painters’",
      "Note 2 cites Vertue, Woodward's 1957 article and a Haskell 1960 source, then quotes Joseph Andrews, Book III, Chapter 6, satirically listing mock painter names.",
      "Printed note marker is 2 although OCR shows '?'. The mock names are part of Fielding's joke, not evidence for real artists; the cited works have not been independently read. The exact Haskell 1960 bibliographic work remains unresolved.",
      [E["vertue_notebooks"],C["woodward_amigoni_article"],C["haskell_1960_note2_source"],E["fielding"],C["joseph_andrews"]],
      speaker="Haskell's footnote citing Vertue, Woodward and Haskell; then Fielding",layer="footnote with nested literary quotation")

open_note = cov[PREV]["note"]
if "p.287" not in open_note:
    raise SystemExit("p.286 coverage note does not identify the p.287 continuation")
cov[PREV].update({"migration_status":"complete","source_line_ranges":"L191-204; p.287 L207",
                  "note":"Printed p.286 was read against CHP-10.pdf physical page 15. Its final Moor Park assignment sentence closes at p.287 L207, naming Amigoni and Francesco Sleter; continuation is cross-linked. Notes 1-3 remain pending in the consolidated notes segment."})
cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L207-216",
                 "note":"Printed p.287 was read against CHP-10.pdf physical page 16. Closed p.286's Moor Park assignment; recorded Amigoni's four Jupiter and Io canvases, career shift and qualified reported income, Fielding reference, English patronage generalization, and McSwiny's biography, unrealized Van Dyck engraving plan, departure and proposed allegorical tomb scheme for Lord March. Haskell's optimism/Glorious Revolution interpretation is preserved as authorial judgment; p.214's final sentence continues at p.288 L219. Scan-only corrections: L208 'story\'of' -> 'story of'; L209 printed sum £4,000–£5,000; L215 OCR note marker '?' -> printed 2 and 'Verrue' -> 'Vertue'. S0 unchanged. Notes 1,3,4,5,6 remain pending in the consolidated notes segment; note 2 is migrated here, but its cited sources were not independently read."})
cov[NEXT]["note"] = "Next source-order segment is printed p.288 at L218-227; close p.287 L214's unfinished sentence beginning 'Meanwhile wealth at home and peace in Europe were encouraging'."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"new_candidates":len(newc),"new_mentions":len(newm),
                  "new_statements":len(new_s),"new_candidate_ids":[row["candidate_id"] for row in newc],
                  "coverage":{"p286":cov[PREV]["migration_status"],"p287":cov[SEG]["migration_status"],"p288":cov[NEXT]["migration_status"]}},ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.287 S2 migration; p.286 is complete, p.287 remains partial, backups retained.")
