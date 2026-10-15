"""Controlled semantic re-audit of printed p.371, with source and table hash locks."""
import argparse, copy, csv, hashlib, json, shutil, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-15.pdf"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
BODY = "chp-15:15_CHP-15_sec_ii:l69-83"
SOURCE_SHA = "eea847f75c7876dc5b8ea38ef4b64ad30cdd6c629df6a064125ac5f63917d31f"
PDF_SHA = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
EXPECTED = {
    "entity-candidates.csv": "45d0ef9d662b65feb2fcd1a5254d3562221d217251f50d040be8611a002d67f9",
    "mentions.csv": "197d3361782e14af6d95119d515326f0d68387a0a5b324d89b4be484c2283390",
    "book-statements.jsonl": "f0b43a7b75d105d77346e1acf60243e701f76c893cf2a2ebff668078ce24398a",
}
BACKUP_SUFFIX = ".bak-s2-chp15-p371-semantics-reaudit-20261009"
ap = argparse.ArgumentParser()
ap.add_argument("--apply", action="store_true")
ARGS = ap.parse_args()

def rcsv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)
def rjson(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
def wcsv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader(); w.writerows(rows); tmp = Path(f.name)
    tmp.replace(path)
def wjson(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)

cp, mp, sp = (TABLES / x for x in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl"))
cf, candidates = rcsv(cp); mf, mentions = rcsv(mp); statements = rjson(sp)
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA: raise SystemExit("Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA: raise SystemExit("registered PDF changed")
for name, expected in EXPECTED.items():
    actual = hashlib.sha256((TABLES / name).read_bytes()).hexdigest()
    if actual != expected: raise SystemExit(f"{name} changed since review snapshot: {actual}")
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text = "\n".join(lines[68:83])
cby = {r["candidate_id"]: r for r in candidates}
mby = {r["mention_id"]: r for r in mentions}
sby = {r["statement_id"]: r for r in statements}
body = [r for r in statements if r.get("segment_id") == BODY and r.get("statement_id", "").startswith("st-chp15-p371-")]
if len(body) != 23: raise SystemExit(f"expected 23 first-pass body statements; found {len(body)}")
if sum(bool(r.get("qualifiers", {}).get("relation_candidate")) for r in body) != 12: raise SystemExit("relation candidate precondition changed")
if "cand-10575" not in cby or "cand-11541" in cby or "cand-11542" in cby: raise SystemExit("candidate ID precondition changed")
if not {"cand-0086", "cand-2825", "cand-9945", "cand-10571"} <= set(cby): raise SystemExit("required candidates missing")
if "m-chp15-p371-querini-0056" in mby or "st-chp15-p371-altar-highlights-querini-temperament" in sby: raise SystemExit("reaudit IDs already exist")
bad_mentions = {r["mention_id"] for r in mentions if r.get("candidate_id") == "cand-10575"}
if bad_mentions != {"m-chp15-p371-querini-0015", "m-chp15-p371-querini-0017", "m-chp15-p371-querini-0019"}:
    raise SystemExit(f"unexpected references to pseudo-entity: {sorted(bad_mentions)}")

def pos(surface):
    a = text.find(surface)
    if a < 0 or text.find(surface, a + 1) >= 0: raise SystemExit(f"surface not unique in source: {surface}")
    return a, a + len(surface)
def revise(sid, subject, obj, pred, quote, claim, qualification, mentioned, ln, rel=False,
           speaker="Haskell", layer="authorial report"):
    if quote not in text: raise SystemExit(f"quote not exact in source: {sid}")
    r = sby[sid]; r["subject_candidate_id"] = subject; r["object_candidate_id"] = obj
    r["predicate"] = pred; r["original_quote"] = quote
    q = r.setdefault("qualifiers", {})
    q.update({"source_line_start": ln[0], "source_line_end": ln[1], "printed_page": 371,
              "pdf_physical_page": 11, "claim": claim, "speaker": speaker,
              "text_layer": layer, "qualification": qualification,
              "mentioned_candidate_ids": list(dict.fromkeys(mentioned))})
    if rel: q["relation_candidate"] = True
    else: q.pop("relation_candidate", None)
def add(sid, subject, obj, pred, quote, claim, qualification, mentioned, ln, rel=False,
        speaker="Haskell", layer="authorial report"):
    if quote not in text: raise SystemExit(f"quote not exact in source: {sid}")
    q = {"source_line_start": ln[0], "source_line_end": ln[1], "printed_page": 371,
         "pdf_physical_page": 11, "claim": claim, "speaker": speaker, "text_layer": layer,
         "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if rel: q["relation_candidate"] = True
    return {"statement_id": sid, "segment_id": BODY, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": pred, "qualifiers": q,
            "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE}

def cand(cid, name, typ, detail, line):
    return {"candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
            "suggested_type": typ, "status": "open", "index_source_file": "", "sub_entry": "",
            "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
            "candidate_source_ref": f"{BODY}#L{line}"}

new_candidates = [
    cand("cand-11541", "Apollo as the mythological figure invoked in the Alticchiero monument allegory",
         "person", "Haskell says the monument allegorized the unnamed Grand Duke as Apollo; keep this distinct from other Apollo candidates pending S3.", 74),
    cand("cand-11542", "Allegory as a representational mode discussed in the p.371 account",
         "term", "Haskell summarizes Mme Rosenberg's difficulty with allegorical paintings and her ease with Querini's garden allegories; this is the mode, not a specific work.", 74),
]
# Repair candidate mapping and remove the non-entity used for a methodological limitation.
mby["m-chp15-p371-querini-0015"]["candidate_id"] = "cand-11542"
mby["m-chp15-p371-querini-0017"]["candidate_id"] = "cand-11542"
mby["m-chp15-p371-querini-0020"]["candidate_id"] = "cand-2825"
mentions = [r for r in mentions if r["mention_id"] != "m-chp15-p371-querini-0019"]
for mid, cid, surface in [
    ("m-chp15-p371-querini-0056", "cand-0086", "Querini’s villa"),
    ("m-chp15-p371-querini-0057", "cand-11541", "Apollo"),
    ("m-chp15-p371-querini-0058", "cand-11542", "allegorised"),
]:
    a, b = pos(surface)
    mentions.append({"mention_id": mid, "segment_id": BODY, "candidate_id": cid,
                     "surface_form": surface, "start_char": str(a), "end_char": str(b), "note": ""})
candidates = [r for r in candidates if r["candidate_id"] != "cand-10575"] + new_candidates
cby = {r["candidate_id"]: r for r in candidates}
new = []

# Reported characterization, Querini's reported belief, altar and relief relationships.
revise("st-chp15-p371-querini-alter-spirits-and-mme-characterization",
       "cand-2075", "cand-10572", "mme_rosenberg_characterized_querini_soul_as_somewhat_pagan_or_manichean",
       "as Mme Rosenberg pointed out, his soul was ‘somewhat pagan or at least Manichean’",
       "Haskell reports Mme Rosenberg's characterization of Querini's soul as somewhat pagan or at least Manichean.",
       "This is a characterization reported by Haskell from Mme Rosenberg, not an independently established statement of Querini's beliefs.",
       ["cand-2075", "cand-2824", "cand-10572"], (71, 71), speaker="Haskell, reporting Mme Rosenberg", layer="reported account")
new.append(add("st-chp15-p371-querini-sacrifice-evil-and-good-spirits", "cand-2075", None,
       "believed_sacrifice_to_good_and_evil_spirits_was_needed_for_happiness",
       "he believed that, the world being what it was, one should sacrifice to evil as well as to good spirits if one was to hope for happiness.",
       "Haskell reports that Querini believed one should sacrifice to both evil and good spirits to hope for happiness.",
       "The belief is attributed to Querini through Haskell's report of Mme Rosenberg; it is not independently established here.",
       ["cand-2075"], (71, 71), speaker="Haskell, reporting Mme Rosenberg", layer="reported account"))
new.append(add("st-chp15-p371-altar-highlights-querini-temperament", "cand-10569", "cand-2075",
       "altar_emphasized_aspect_of_querini_temperament",
       "The same aspect of Querini’s temperament was emphasised in the Altar dedicated to\nIgnorance, Envy and Calumny",
       "Haskell says an aspect of Querini's temperament was emphasized in the altar dedicated to Ignorance, Envy, and Calumny.",
       "The referent of 'the same aspect' is the characterization discussed immediately afterward; no independent account of the altar is consulted.",
       ["cand-10569", "cand-2075", "cand-10592", "cand-10593", "cand-10594"], (70, 71), True))
for slug, cid, vice in [("ignorance", "cand-10592", "Ignorance"), ("envy", "cand-10593", "Envy"), ("calumny", "cand-10594", "Calumny")]:
    new.append(add(f"st-chp15-p371-altar-dedicated-to-{slug}", "cand-10569", cid, "altar_dedicated_to_personified_vice",
        "Altar dedicated to\nIgnorance, Envy and Calumny", f"Haskell identifies the Alticchiero altar as dedicated to {vice}.",
        "This follows the printed dedication wording; no separate dedication text is supplied.",
        ["cand-10569", cid], (70, 71), True))
revise("st-chp15-p371-vices-depicted-after-apelles-pliny", "cand-10570", None,
       "bas_relief_depicted_three_personified_vices",
       "Hence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
       "Haskell says the bas-relief depicted the three personified vices and links it to a composition by Apelles recorded by Pliny.",
       "The source does not identify or independently examine either the relief or the ancient composition.",
       ["cand-10570", "cand-10592", "cand-10593", "cand-10594", "cand-9945", "cand-10571"], (72, 73))
for slug, cid, vice in [("ignorance", "cand-10592", "Ignorance"), ("envy", "cand-10593", "Envy"), ("calumny", "cand-10594", "Calumny")]:
    new.append(add(f"st-chp15-p371-relief-depicts-{slug}", "cand-10570", cid, "bas_relief_depicts_personified_vice",
        "Hence these vices were depicted in a bas-relief based on the famous composition of\nApelles as recorded by Pliny.",
        f"Haskell says the bas-relief depicted {vice}.",
        "The description is Haskell's report; the physical relief is not independently examined.",
        ["cand-10570", cid], (72, 73), True))
new.append(add("st-chp15-p371-relief-based-on-apelles-composition", "cand-10570", "cand-9945",
       "bas_relief_based_on_composition_by_apelles", "a bas-relief based on the famous composition of\nApelles",
       "Haskell says the bas-relief was based on a famous composition by Apelles.",
       "The composition's exact title, surviving form, and transmission to the relief are not identified.",
       ["cand-10570", "cand-9945"], (72, 73), True))
new.append(add("st-chp15-p371-pliny-recorded-apelles-composition", "cand-10571", "cand-9945",
       "recorded_composition_by_apelles", "composition of\nApelles as recorded by Pliny",
       "Haskell identifies Pliny as the recorder of the composition attributed to Apelles.",
       "Pliny is named only by surname here; identity alignment is deferred to S3.",
       ["cand-10571", "cand-9945"], (73, 73), True))

# Villa visit and monument, including previously absent villa and Apollo mentions.
revise("st-chp15-p371-grand-duke-visit-and-monument", "cand-4302", "cand-10573", "grand_duke_visited_querini_villa",
       "Among the visitors who came to see it was the Grand Duke of Tuscany",
       "Haskell says the unnamed Grand Duke of Tuscany was among visitors to Querini's villa.",
       "The Grand Duke's individual identity is not supplied; the villa is Alticchiero as indexed in the book.",
       ["cand-4302", "cand-10573", "cand-0086"], (74, 74), True)
new.append(add("st-chp15-p371-villa-attracted-enormous-attention", "cand-0086", None, "attracted_enormous_attention",
       "Querini’s villa attracted enormous attention.", "Haskell says Querini's villa attracted enormous attention.",
       "This is Haskell's qualitative description; no visitor count is provided.", ["cand-0086"], (74, 74)))
new.append(add("st-chp15-p371-querini-erected-monument-for-visit", "cand-2075", "cand-10574",
       "erected_monument_to_record_grand_duke_visit", "Querini recorded the occasion by erecting a monument",
       "Haskell says Querini erected a monument to record the Grand Duke's visit.",
       "The date and survival of the monument are not supplied.",
       ["cand-2075", "cand-10574", "cand-10573", "cand-4302"], (74, 74), True))
revise("st-chp15-p371-grand-duke-monument-sphinx-apollo-relief", "cand-10574", "cand-4302",
       "monument_allegorized_reforming_prince_as_apollo",
       "monument, crowned with a sphinx, containing a flattering inscription and a bas-relief in which the reforming prince was allegorised as Apollo",
       "Haskell describes the monument as crowned with a sphinx and bearing a flattering inscription; its bas-relief allegorized the unnamed reforming prince as Apollo.",
       "The inscription's wording and the monument's survival are not supplied; 'reforming prince' refers to the unnamed Grand Duke of Tuscany.",
       ["cand-10574", "cand-4302", "cand-11541", "cand-11542"], (74, 74), True)
revise("st-chp15-p371-mme-rosenberg-distrust-of-allegory", "cand-2824", None,
       "found_painted_ceilings_hard_to_understand_and_sculptural_allegory_easier",
       "Mme Rosenberg distrusted allegory—she found painted ceilings hard to understand, but in sculpture the whole problem was much easier, for so few figures were involved.",
       "Haskell says Mme Rosenberg distrusted allegory, found painted ceilings difficult to understand, and found sculptural allegory easier because fewer figures were involved.",
       "This is Haskell's summary of Rosenberg's response, not a direct quotation from her.",
       ["cand-2824", "cand-11542"], (74, 74))
revise("st-chp15-p371-querini-garden-allegories-straightforward", "cand-2824", "cand-2081",
       "mme_rosenberg_found_querini_garden_allegories_straightforward",
       "And above ail she found that the allegories in\nQuerini’s garden were absolutely straightforward.",
       "Haskell says Mme Rosenberg found the allegories in Querini's garden absolutely straightforward.",
       "The source's 'above ail' is an OCR error for printed 'above all'; this remains Haskell's report of Rosenberg's view.",
       ["cand-2824", "cand-2081", "cand-11542"], (74, 75))
# Keep the evidence limitation as a statement, not an entity; correct the cited illustrated book.
revise("st-chp15-p371-sculpture-collection-assessment-limit", "cand-2075", None,
       "haskell_cannot_assess_quality_or_type_of_querini_sculpture_collection",
       "Despite the illustrations in Mme Rosenberg’s book it is difficult to assess the quality or even the type of sculpture that Querini collected and put to such strange use.",
       "Haskell says Mme Rosenberg's illustrations do not allow him to assess the quality or even the type of sculpture Querini collected.",
       "This is an explicit limitation in Haskell's evidence; it does not itself identify a separate entity.",
       ["cand-2075", "cand-2825"], (76, 76))

# Sculptural taste, collection and attribution statements.
revise("st-chp15-p371-querini-antique-taste-winckelmann", "cand-2075", "cand-2816",
       "querini_antique_taste_inspired_by_winckelmann",
       "His taste for the antique was clearly inspired by the ‘digne et malheureux’ Winckelmann;",
       "Haskell says Querini's taste for antiquity was clearly inspired by Winckelmann.",
       "This is Haskell's interpretation; the note points to other antiquarian contacts and dedications.",
       ["cand-2075", "cand-2816"], (76, 76), True)
new.append(add("st-chp15-p371-querini-antique-restraint", "cand-2075", None,
       "saw_restraint_and_lack_of_excess_as_antiquitys_main_character",
       "in it he saw a restraint and lack of excess which constituted its main character.",
       "Haskell says Querini saw restraint and lack of excess as the main character of antiquity.",
       "This is Haskell's report of Querini's interpretation, not an independently established general property of antiquity.",
       ["cand-2075"], (76, 76)))
revise("st-chp15-p371-querini-algardi-hercules", "cand-2075", "cand-10576",
       "querini_collection_included_hercules_by_algardi", "His more modern work included a Hercules by Algardi",
       "Haskell says Querini's more modern collection included a Hercules sculpture by Algardi.",
       "The work's title, date, and location are not supplied.",
       ["cand-2075", "cand-10576", "cand-0034"], (76, 76), True)
new.append(add("st-chp15-p371-hercules-attributed-to-algardi", "cand-10576", "cand-0034",
       "hercules_sculpture_by_algardi", "a Hercules by Algardi",
       "Haskell attributes the Hercules sculpture in Querini's collection to Algardi.",
       "No title, date, or current location is supplied.", ["cand-10576", "cand-0034"], (76, 76), True))
revise("st-chp15-p371-querini-young-canova-sculpture", "cand-2075", "cand-10577",
       "querini_collection_included_sculpture_by_young_canova", "and sculpture by the young Canova.",
       "Haskell says Querini's more modern collection included sculpture by the young Canova.",
       "The subject, title, date, and location of the sculpture are not supplied.",
       ["cand-2075", "cand-10577", "cand-0532"], (76, 76), True)
new.append(add("st-chp15-p371-unidentified-sculpture-by-young-canova", "cand-10577", "cand-0532",
       "unidentified_sculpture_by_young_canova", "sculpture by the young Canova",
       "Haskell attributes an unidentified sculpture in Querini's collection to the young Canova.",
       "The subject, date, and current location are not supplied.", ["cand-10577", "cand-0532"], (76, 76), True))
revise("st-chp15-p371-querini-etruacan-and-egyptian-objects", "cand-2075", "cand-10578",
       "owned_ancient_etruscan_phallic_symbols", "He owned ancient Etruscan phallic symbols",
       "Haskell says Querini owned ancient Etruscan phallic symbols.",
       "The source gives no count, catalogue, or present location.",
       ["cand-2075", "cand-10578"], (76, 76), True)
new.append(add("st-chp15-p371-rosenberg-difficulty-explaining-etruscan-symbols", "cand-2824", "cand-10578",
       "mme_rosenberg_found_etruscan_symbols_difficult_to_explain",
       "which caused Mme Rosenberg a certain amount of difficulty in explaining",
       "Haskell says the Etruscan phallic symbols caused Mme Rosenberg difficulty in explaining them.",
       "This is Haskell's account of Rosenberg's response; the source gives no further detail.",
       ["cand-2824", "cand-10578"], (76, 76), True))
new.append(add("st-chp15-p371-querini-owned-egyptian-figures", "cand-2075", "cand-10579",
       "owned_large_number_of_egyptian_figures", "and a large number of Egyptian figures.",
       "Haskell says Querini owned a large number of Egyptian figures.",
       "The number, identities, and current locations of the figures are not supplied.",
       ["cand-2075", "cand-10579"], (76, 76), True))

# Separate De Non's close contact, residence, roles, two influence recipients, and portraits.
revise("st-chp15-p371-de-non-close-contact-and-venice-period", "cand-2075", "cand-1752",
       "querini_had_close_contact_with_de_non_excepting_sculptors",
       "Apart from sculptors the only artist with whom he had close contacts'was Dominique De Non",
       "Haskell identifies Dominique De Non as the only artist, apart from sculptors, with whom Querini had close contacts.",
       "The scope explicitly excludes sculptors; the printed page reads 'contacts was', while S0 OCR joins the words.",
       ["cand-2075", "cand-1752"], (77, 77), True)
new.append(add("st-chp15-p371-de-non-settled-in-venice", "cand-1752", "cand-2719",
       "settled_in_venice_for_about_five_years_in_early_1790s",
       "De Non settled in Venice for about five years in the early ’nineties",
       "Haskell says De Non settled in Venice for about five years in the early 1790s.",
       "Both the duration and date are approximate as stated by Haskell.",
       ["cand-1752", "cand-2719"], (77, 77), True))
revise("st-chp15-p371-de-non-engraver-and-collector", "cand-1752", None,
       "described_as_controversial_but_admired_engraver_and_collector",
       "and led a busy life as a controversial but highly admired engraver and also as a collector.",
       "Haskell describes De Non as a controversial but highly admired engraver and collector.",
       "This is Haskell's characterization; no independent appraisal is supplied.",
       ["cand-1752"], (77, 77))
revise("st-chp15-p371-rembrandt-prints-influenced-de-non-and-novelli", "cand-10580", "cand-1752",
       "rembrandt_prints_profoundly_influenced_de_non_style",
       "the Rembrandts, which had a profound effect on his own style and that of his principal pupil Francesco Novelli.",
       "Haskell says the Rembrandt prints profoundly affected De Non's own style.",
       "This is Haskell's account of artistic influence; it is not independently assessed here.",
       ["cand-10580", "cand-1752"], (78, 78), True)
new.append(add("st-chp15-p371-rembrandt-prints-influenced-novelli", "cand-10580", "cand-1756",
       "rembrandt_prints_profoundly_influenced_novelli_style",
       "the Rembrandts, which had a profound effect on his own style and that of his principal pupil Francesco Novelli.",
       "Haskell says the Rembrandt prints profoundly affected Francesco Novelli's style.",
       "This is Haskell's account of artistic influence; it is not independently assessed here.",
       ["cand-10580", "cand-1756"], (78, 78), True))
revise("st-chp15-p371-de-non-voltaire-engraving-ferney", "cand-1752", "cand-10582",
       "de_non_engraved_portrait_of_voltaire", "At Ferney he had engraved a portrait of Voltaire",
       "Haskell says De Non engraved a portrait of Voltaire.",
       "No date, title, or surviving impression is specified.",
       ["cand-1752", "cand-10582", "cand-2791", "cand-10581"], (79, 79), True)
new.append(add("st-chp15-p371-voltaire-portrait-depicts-voltaire", "cand-10582", "cand-2791",
       "portrait_depicts_voltaire", "a portrait of Voltaire",
       "Haskell identifies the engraved portrait as a portrait of Voltaire.",
       "No title, date, or surviving impression is specified.",
       ["cand-10582", "cand-2791"], (79, 79), True))
new.append(add("st-chp15-p371-de-non-engraved-voltaire-portrait-at-ferney", "cand-10582", "cand-10581",
       "engraving_made_at_ferney", "At Ferney he had engraved a portrait of Voltaire",
       "Haskell locates De Non's engraving of the Voltaire portrait at Ferney.",
       "The precise site at Ferney is not identified.",
       ["cand-10582", "cand-10581"], (79, 79), True))
revise("st-chp15-p371-de-non-in-querini-circle-and-signed-portrait", "cand-1752", "cand-2075",
       "moved_in_querini_circle", "He moved a great deal in his circle",
       "Haskell says De Non moved a great deal in Querini's circle.",
       "The antecedent of 'his' is Querini in the surrounding account.",
       ["cand-1752", "cand-2075"], (80, 80), True)
new.append(add("st-chp15-p371-de-non-drew-signed-unidentified-sitter-portrait", "cand-1752", "cand-10584",
       "drew_portrait_signed_amico_suavissimo", "drew his portrait (which he signed ‘amico suavissimo’)",
       "Haskell says De Non drew a portrait signed 'amico suavissimo'; the male sitter is not securely identified.",
       "The possessive sitter referent is ambiguous in the source and remains unresolved; date and present location are also absent.",
       ["cand-1752", "cand-10584", "cand-2075"], (80, 80), True))
new.append(add("st-chp15-p371-rosenberg-portrait-depicts-rosenberg", "cand-10585", "cand-2824",
       "portrait_depicts_mme_rosenberg", "also that of Mme Rosenberg among her friends.",
       "Haskell identifies the second portrait as one of Mme Rosenberg.",
       "No date, title, or present location is supplied.",
       ["cand-10585", "cand-2824"], (81, 81), True))

# Separate association, commission, maker, and sitter in the Renier bust passage.
revise("st-chp15-p371-querini-renier-canova-bust-commission-partial", "cand-2075", "cand-10586",
       "querini_commissioned_bust_of_paolo_renier_from_canova",
       "and he had commissioned Canova to make him a bust of this friend after his successful (but exceedingly corrupt) campaign",
       "Haskell says Querini commissioned Canova to make a bust of his friend Paolo Renier after Renier's successful, though in Haskell's description exceedingly corrupt, campaign.",
       "P.372 completes the sentence by specifying the campaign was to become Doge in 1779; Haskell's moral characterization is not independently established.",
       ["cand-2075", "cand-0532", "cand-2133", "cand-10586"], (83, 83), True)
new.append(add("st-chp15-p371-querini-associated-with-paolo-renier", "cand-2075", "cand-2133",
       "closely_associated_with_paolo_renier_in_younger_days",
       "In his younger days he had been closely associated with another potential reformer, Paolo Renier",
       "Haskell says Querini was closely associated in his younger days with the potential reformer Paolo Renier.",
       "This is Haskell's account; it does not specify dates or the nature of the association.",
       ["cand-2075", "cand-2133"], (83, 83), True))
new.append(add("st-chp15-p371-renier-bust-commissioned-from-canova", "cand-10586", "cand-0532",
       "querini_commissioned_canova_to_make_bust",
       "commissioned Canova to make him a bust",
       "Haskell says Canova was commissioned to make the bust of Paolo Renier.",
       "The sentence records a commission; the date and production history are not supplied on this page.",
       ["cand-10586", "cand-0532", "cand-2075", "cand-2133"], (83, 83), True))
new.append(add("st-chp15-p371-renier-bust-portrayed-paolo-renier", "cand-10586", "cand-2133",
       "bust_portrayed_paolo_renier", "a bust of this friend",
       "Haskell identifies the commissioned bust as a bust of Paolo Renier.",
       "No title, date, or present location is supplied in this sentence.",
       ["cand-10586", "cand-2133"], (83, 83), True))

# Strip stale references to the removed pseudo-entity, then validate every touched endpoint and quote.
for row in statements:
    q = row.get("qualifiers", {})
    if "mentioned_candidate_ids" in q:
        q["mentioned_candidate_ids"] = [x for x in q["mentioned_candidate_ids"] if x != "cand-10575"]
updated = statements + new
cids = {r["candidate_id"] for r in candidates}
all_sids = [r["statement_id"] for r in updated]
if len(all_sids) != len(set(all_sids)): raise SystemExit("duplicate statement IDs")
for r in updated:
    if r.get("segment_id") == BODY:
        for cid in (r.get("subject_candidate_id"), r.get("object_candidate_id")):
            if cid and cid not in cids: raise SystemExit(f"unknown endpoint {cid}: {r['statement_id']}")
        for cid in r.get("qualifiers", {}).get("mentioned_candidate_ids", []):
            if cid not in cids: raise SystemExit(f"unknown mentioned candidate {cid}: {r['statement_id']}")
        if r.get("statement_id", "").startswith("st-chp15-p371-") and r.get("original_quote") not in text:
            raise SystemExit(f"non-exact p.371 quote: {r['statement_id']}")
for r in mentions:
    if r.get("segment_id") == BODY and r.get("candidate_id") not in cids:
        raise SystemExit(f"unknown mention endpoint: {r['mention_id']}")
if any("cand-10575" in json.dumps(r, ensure_ascii=False) for r in updated + mentions):
    raise SystemExit("removed pseudo-entity still referenced")
new_body = [r for r in updated if r.get("segment_id") == BODY and r.get("statement_id", "").startswith("st-chp15-p371-")]
plan = {
    "mode": "apply" if ARGS.apply else "dry-run",
    "body_segment": BODY,
    "existing_body_statements": len(body),
    "added_body_statements": len(new),
    "result_body_statements": len(new_body),
    "result_body_relation_candidates": sum(bool(r.get("qualifiers", {}).get("relation_candidate")) for r in new_body),
    "candidate_count_before": len(rcsv(cp)[1]), "candidate_count_after": len(candidates),
    "mention_count_before": len(rcsv(mp)[1]), "mention_count_after": len(mentions),
    "statement_count_before": len(rjson(sp)), "statement_count_after": len(updated),
    "removed_candidate": "cand-10575",
    "new_candidates": [r["candidate_id"] for r in new_candidates],
    "new_mentions": ["m-chp15-p371-querini-0056", "m-chp15-p371-querini-0057", "m-chp15-p371-querini-0058"],
    "added_statement_ids": [r["statement_id"] for r in new],
}
print(json.dumps(plan, ensure_ascii=False, indent=2))
if not ARGS.apply: raise SystemExit(0)
for path in (cp, mp, sp):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
wcsv(cp, cf, candidates); wcsv(mp, mf, mentions); wjson(sp, updated)
print("applied p.371 semantic re-audit; recovery copies created for all changed tables")
