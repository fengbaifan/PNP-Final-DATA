"""Controlled S2 migration for printed p.298; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l332-343"
SEG = "chp-10:10_CHP-10_intro:l345-352"
NEXT = "chp-10:10_CHP-10_intro:l354-366"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEG_SHA = "1eb737b59f2af24ef4cca5e7814c6e3ba5d0dd521276689c9f690ae94ff54d3f"
BACKUP = ".bak-s2-chp10-p298-20261002"


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
body = "\n".join(src[344:352])
SEG_SHA = hashlib.sha256(body.encode("utf-8")).hexdigest()
if SEG_SHA != EXPECTED_SEG_SHA or src[344].strip() != "[Page 298]" or "Pietro Antonio Novelli" not in body or "the city’s treasures" not in body:
    raise SystemExit("p.298 source segment/page mismatch")

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
if maximum != 9154:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "catherine": "cand-0609", "bellotto": "cand-0281", "augustus_iii": "cand-0148",
    "augustus_iii_algarotti_index": "cand-0149", "stanislas": "cand-2505",
    "novelli": "cand-1758", "novelli_work_index": "cand-1759", "batoni": "cand-0260",
    "tiepolo": "cand-2577", "algarotti": "cand-0073", "st_petersburg": "cand-2343",
    "france": "cand-5317", "venetian_art": "cand-8101", "venetian_artists": "cand-8104",
    "venice_city": "cand-2719", "republic": "cand-8838", "london": "cand-1422",
    "paris": "cand-4653", "dusseldorf": "cand-9072", "madrid": "cand-1481",
    "dresden_city": "cand-0947", "wurzburg_city": "cand-9117", "poland": "cand-7492",
    "europe": "cand-3462", "aeneas": "cand-4164", "anchises": "cand-7626",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (
    ("catherine", E["catherine"], "298", ""),
    ("bellotto", E["bellotto"], "298", "work in Warsaw"),
    ("stanislas", E["stanislas"], "298, 366", ""),
    ("novelli", E["novelli"], "254, 255n, 260, 298, 336", ""),
    ("novelli_work_index", E["novelli_work_index"], "298", "Creusa imploring Aeneas to rescue his father Anchises"),
    ("batoni", E["batoni"], "xvii, 259, 298", ""),
    ("tiepolo", E["tiepolo"], "256, 257, 298, 352, 353", "Banquet of Cleopatra"),
    ("algarotti", E["algarotti"], "294, 295, 298, 349, 356", "purchases of pictures for Augustus III"),
    ("augustus_iii", E["augustus_iii"], "277, 294, 295, 298, 307, 344, 349, 350, 351", ""),
    ("augustus_iii_algarotti_index", E["augustus_iii_algarotti_index"], "294, 295, 298, 349, 350, 351, 353, 355", "F. Algarotti and"),
):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected candidate {key}={cid}: {row}")

NEW_SPECS = [
    ("warsaw", "Warsaw as Bellotto's destination and the capital represented in his views", "place",
     "The city where Bellotto stopped at Stanislas Poniatowski's persuasion and produced views; no specific buildings or views are named here.", 348),
    ("bellotto_warsaw_views", "Unidentified views of Warsaw produced by Bernardo Bellotto for Stanislas Poniatowski", "work",
     "A large, unnamed group of city views made over the period Haskell describes as twelve years until Bellotto's death in 1780; individual titles and dates are not supplied.", 348),
    ("creusa", "Creusa, named in Pietro Antonio Novelli's painting subject", "person",
     "Mythological figure named in the source's description of Novelli's 1772 picture; no identity beyond the subject is inferred.", 348),
    ("troy", "Troy as the mythological setting named in Novelli's picture subject", "place",
     "The mythological city named in the account of the fire from which Aeneas rescues Anchises; distinguish it from the named painting subject.", 349),
    ("novelli_creusa_picture", "Pietro Antonio Novelli's 1772 picture of Creusa imploring Aeneas to rescue Anchises", "work",
     "A picture painted for the Empress in 1772, identified by its narrative subject; the source does not establish a formal catalogue title.", 348),
    ("batoni_opposing_painting", "Unidentified Pompeo Batoni painting intended to hang opposite Novelli's Creusa picture", "work",
     "A painting by Pompeo Batoni used as the competing work in Haskell's account; its subject, date and location are not given here.", 349),
    ("russia_destination", "Russia as the destination of Novelli's declined invitation", "place",
     "The broad destination named for an invitation Novelli declined because of the climate; the inviter and intended city are not identified.", 349),
    ("tiepolo_banquet_cleopatra", "Giambattista Tiepolo's Banquet of Cleopatra purchased by Catherine the Great", "work",
     "A Tiepolo painting named as Catherine's purchase and said to have been acquired earlier for Augustus III by Francesco Algarotti, then transferred to St Petersburg in the 1760s. Do not merge it with the separately indexed Labia Palace Banquet of Antony and Cleopatra without S3 evidence.", 349),
    ("dominant_foreigner", "Dominant foreigner in Haskell's p.298 comparison with Venetian native genius", "term",
     "One side of Haskell's explicit contrast about the relationship between foreign presence and native artistic ability; retained as the author's wording, not an external classification.", 352),
    ("native_genius", "Native genius in Haskell's p.298 comparison with the dominant foreigner", "term",
     "One side of Haskell's explicit contrast about the relationship between foreign presence and local artistic ability; retained as the author's wording, not an external classification.", 352),
    ("foreign_residents", "Unidentified foreign residents able to settle within the Venetian Republic", "term",
     "A collective category implied by the closing sentence and announced by the next chapter heading; no individual resident is inferred from this passage.", 352),
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

offsets, offset = {}, 0
for line in range(345, 353):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p298-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start, line_end = offsets[line], offsets[line] + len(src[line - 1])
    positions, at = [], line_start
    while True:
        at = body.find(surface, at)
        if at < 0 or at >= line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("catherine-full-name",346,"Catherine the\nGreat",E["catherine"],"Printed name crosses the OCR line break."),
    ("catherine-second",347,"Catherine",E["catherine"],"Explicit repeat after the line-break completion of her full name."),
    ("catherine-her-culture",347,"her culture",E["catherine"],"Corefers to Catherine the Great."),
    ("catherine-her-artistic",347,"her artistic",E["catherine"],"Corefers to Catherine's artistic tastes."),
    ("catherine-her-other",347,"her other",E["catherine"],"Corefers to Catherine's other tastes."),
    ("catherine-herself",347,"herself",E["catherine"],"Reflexive coreference to Catherine."),
    ("catherine-she",347,"she did what she could",E["catherine"],"Corefers to Catherine as the subject of the policy claim."),
    ("catherine-her-predecessor",347,"her predecessor",E["catherine"],"Possessive coreference; the predecessor is not named."),
    ("venetian-pictures",347,"Venetian pictures",E["venetian_art"],"Objects of the importation impulse described by Haskell."),
    ("france",347,"France",E["france"],"Country toward which Haskell says Catherine's culture was inclined."),
    ("bellotto",348,"Bernardo Bellotto",E["bellotto"],"Named artist planning the journey from Dresden toward St Petersburg."),
    ("st-petersburg-plan",348,"S t Petersburg",E["st_petersburg"],"OCR inserts a space; the scan reads 'St Petersburg'."),
    ("dresden-court",348,"the Dresden court", "cand-9109", "Court whose collapse is given as context."),
    ("augustus-death",348,"Augustus III",E["augustus_iii"],"His death is one of the stated contexts for Bellotto's plan."),
    ("bellotto-he-persuaded",348,"he was persuaded",E["bellotto"],"Corefers to Bellotto in the changed-travel account."),
    ("stanislas",348,"the new King of Poland Stanislas Poniatowski",E["stanislas"],"Named ruler who persuaded Bellotto to stop in Warsaw."),
    ("warsaw",348,"Warsaw",C["warsaw"],"Destination where Bellotto was persuaded to stop."),
    ("bellotto-his-death",348,"his death",E["bellotto"],"Corefers to Bellotto; the source dates his death to 1780."),
    ("bellotto-views",348,"a large number of views",C["bellotto_warsaw_views"],"Unidentified city-view group produced for the Polish monarch."),
    ("bellotto-monarch",348,"that art-loving and reforming monarch",E["stanislas"],"Corefers to Stanislas Poniatowski; the evaluation is Haskell's."),
    ("warsaw-capital",348,"his capital",C["warsaw"],"Corefers to Warsaw."),
    ("novelli",348,"Pietro Antonio Novelli",E["novelli"],"Named painter of the 1772 picture."),
    ("empress",348,"the Empress",E["catherine"],"Context identifies her as Catherine; no separate ruler is inferred."),
    ("novelli-picture",348,"a picture",C["novelli_creusa_picture"],"Work mention; the following subject figures are separately anchored."),
    ("creusa",348,"Creusa",C["creusa"],"Named mythological figure in the picture subject."),
    ("aeneas",349,"Aeneas",E["aeneas"],"Named mythological figure in the picture subject."),
    ("anchises",349,"Anchises",E["anchises"],"Named as Aeneas's father in the picture subject."),
    ("troy",349,"Troy",C["troy"],"Mythological place named as the setting of the fire."),
    ("novelli-he",349,"he had gone",E["novelli"],"Corefers to Novelli in the subject-choice account."),
    ("novelli-him",349,"him refuse",E["novelli"],"Corefers to Novelli, who declined the invitation."),
    ("learned-subject",349,"a ‘learned’ subject",C["novelli_creusa_picture"],"Description of Novelli's chosen painting subject."),
    ("batoni-picture",349,"the painting",C["batoni_opposing_painting"],"Unidentified Batoni painting said to hang opposite the Novelli picture."),
    ("batoni",349,"Pompeo Batoni",E["batoni"],"Artist named for the opposing painting."),
    ("batoni-rival",349,"his Roman rival",E["batoni"],"Corefers to Pompeo Batoni."),
    ("russia-invitation",349,"Russia",C["russia_destination"],"Broad invitation destination; inviter and intended city are unnamed."),
    ("catherine-purchase",349,"Catherine",E["catherine"],"Purchaser named in the evidence for her taste."),
    ("venetian-art-catherine",349,"Venetian art",E["venetian_art"],"Artistic category whose reception Haskell discusses."),
    ("venetian-artists",349,"artists",E["venetian_artists"],"Collective artists Haskell calls relatively minor in this context."),
    ("tiepolo",349,"Tiepolo",E["tiepolo"],"Artist named as creator of the purchased painting."),
    ("banquet-cleopatra",349,"Banquet of Cleopatra",C["tiepolo_banquet_cleopatra"],"Title as printed in italics; keep distinct from the separately indexed Labia Palace banquet unless S3 establishes identity."),
    ("masterpiece",349,"This masterpiece",C["tiepolo_banquet_cleopatra"],"Corefers to Tiepolo's Banquet of Cleopatra."),
    ("augustus-acquisition",349,"Augustus III",E["augustus_iii_algarotti_index"],"Index entry with the 'F. Algarotti and' subentry; distinct S1 candidate from the broader Augustus III entry."),
    ("algarotti",349,"Francesco Algarotti",E["algarotti"],"Named as the intermediary in the earlier acquisition."),
    ("st-petersburg-transfer",350,"St Petersburg",E["st_petersburg"],"Destination of the painting's transfer in the 1760s."),
    ("europe-power",350,"Europe",E["europe"],"Geographic frame of Haskell's changing-balance interpretation."),
    ("venetian-art-diffusion",351,"Venetian art",E["venetian_art"],"Subject of the diffusion account."),
    ("venice-city",351,"Venice",E["venice_city"],"City described as a passive onlooker; distinct from the Republic as a political actor."),
    ("venice-city-possessive",351,"the city",E["venice_city"],"Corefers to Venice in 'the city's best artists'."),
    ("london",351,"London",E["london"],"Destination in Haskell's list of cities attracting Venetian artists and pictures."),
    ("paris",352,"Paris",E["paris"],"Destination in Haskell's list of cities attracting Venetian artists and pictures."),
    ("dusseldorf",352,"Diisseldorf",E["dusseldorf"],"OCR spelling; the scan reads 'Düsseldorf'."),
    ("madrid",352,"Madrid",E["madrid"],"Destination in Haskell's list of cities attracting Venetian artists and pictures."),
    ("dresden-city",352,"Dresden",E["dresden_city"],"City destination; distinct from the Dresden court."),
    ("wurzburg",352,"Würzburg",E["wurzburg_city"],"City destination in the scan and OCR."),
    ("dominant-foreigner",352,"dominant foreigner",C["dominant_foreigner"],"Haskell's conceptual wording, not a named individual."),
    ("native-genius",352,"native genius",C["native_genius"],"Haskell's conceptual wording, not a named individual."),
    ("republic",352,"the Republic",E["republic"],"Political entity, distinguished from Venice as a city."),
    ("republic-frontiers",352,"her frontiers",E["republic"],"Pronoun and boundary phrase refer to the Venetian Republic."),
    ("foreign-residents",352,"others",C["foreign_residents"],"Unspecified people who could settle in Venice; the following chapter heading names the collective subject."),
    ("venice-city-treasures",352,"the city",E["venice_city"],"Corefers to Venice in 'the city's treasures'."),
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
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 298,
                  "pdf_physical_page": 27, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        qualifiers["cross_reference_printed_pages"] = [299 if NEXT in cross else 298]
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


add_s("st-chp10-p298-catherine-accession",346,347,E["catherine"],E["venetian_art"],
      "in_june_1762_catherines_accession_gave_a_new_but_not_very_fruitful_impulse_to_importing_venetian_pictures",
      "The dramatic accession to the throne in June 1762", "the importation of Venetian pictures.",
      "Haskell says Catherine's accession in June 1762 gave a new but, as it turned out, not very fruitful impulse to the importation of Venetian pictures.",
      "'Dramatic' and 'not very fruitful' are Haskell's framing and evaluation; the source does not quantify imports.",
      [E["catherine"],E["venetian_art"]],layer="authorial interpretation")
add_s("st-chp10-p298-catherine-taste-policy",347,347,E["catherine"],E["france"],
      "catherines_culture_was_mainly_inclined_towards_france_but_she_resisted_one_style_and_tried_to_continue_her_predecessors_policy",
      "Though her culture was mainly inclined towards France", "policy of her predecessor.",
      "Haskell says Catherine's culture was mainly inclined toward France, while her artistic and other tastes resisted confinement to a single style and she tried to continue her predecessor's policy.",
      "The predecessor is unnamed; this is Haskell's account of Catherine's tastes and policy, not an independently verified motive.",
      [E["catherine"],E["france"]],layer="authorial interpretation")
add_s("st-chp10-p298-bellotto-planned-st-petersburg",348,348,E["bellotto"],E["st_petersburg"],
      "bellotto_was_planning_to_go_to_st_petersburg_after_the_dresden_court_collapsed_and_augustus_iii_died",
      "Bernardo Bellotto was planning", "death of Augustus III.",
      "After the Dresden court's collapse and Augustus III's death, Bernardo Bellotto was planning to go to St Petersburg.",
      "The statement records the plan reported by Haskell, not a completed journey; the source does not specify the timing of the plan.",
      [E["bellotto"],E["st_petersburg"],E["augustus_iii"],"cand-9109"],relation=True)
add_s("st-chp10-p298-bellotto-persuaded-to-warsaw",348,348,E["bellotto"],C["warsaw"],
      "stanislas_poniatowski_persuaded_bellotto_to_stop_in_warsaw_while_he_was_already_travelling",
      "But while already on the journey", "Stanislas Poniatowski",
      "While already on the journey, Bellotto was persuaded by the new King of Poland, Stanislas Poniatowski, to stop in Warsaw.",
      "The source identifies the persuader and destination but does not state that Bellotto had reached St Petersburg or that Warsaw was his original destination.",
      [E["bellotto"],E["stanislas"],C["warsaw"]],relation=True)
add_s("st-chp10-p298-bellotto-warsaw-views",348,348,E["bellotto"],C["bellotto_warsaw_views"],
      "bellotto_produced_many_views_of_warsaw_for_stanislas_until_his_death_in_1780",
      "and, for twelve years", "aspects of his capital.1",
      "Haskell says Bellotto produced a large number of views recording the changing aspects of Warsaw for the art-loving and reforming Stanislas Poniatowski, for twelve years until Bellotto's death in 1780.",
      "The source gives a duration and terminal year but no individual view titles; footnote 1 remains to be processed in the consolidated notes segment.",
      [E["bellotto"],C["bellotto_warsaw_views"],C["warsaw"],E["stanislas"]],relation=True,footnote=1)
add_s("st-chp10-p298-novelli-creusa-picture",348,349,E["novelli"],C["novelli_creusa_picture"],
      "in_1772_novelli_painted_for_the_empress_a_picture_of_creusa_asking_aeneas_to_rescue_anchises_from_the_fire_of_troy",
      "Meanwhile in 1772 Pietro Antonio Novelli painted", "from the fire of Troy.",
      "In 1772 Pietro Antonio Novelli painted for the Empress a picture of Creusa imploring Aeneas to rescue his father Anchises from the fire of Troy.",
      "The source names the subject and patronal recipient but supplies no formal title, exact location, or independent verification.",
      [E["novelli"],E["catherine"],C["novelli_creusa_picture"],C["creusa"],E["aeneas"],E["anchises"],C["troy"]],relation=True)
add_s("st-chp10-p298-novelli-batoni-competition",349,349,E["novelli"],C["batoni_opposing_painting"],
      "novelli_chose_a_learned_subject_to_compete_with_a_batoni_painting_intended_to_hang_opposite",
      "Though he had gone out of his way", "which it was to hang,",
      "Haskell says Novelli went out of his way to choose a 'learned' subject to compete with a Pompeo Batoni painting that was to hang opposite it.",
      "The source does not identify Batoni's painting by title or establish that either work was ultimately hung as planned.",
      [E["novelli"],C["novelli_creusa_picture"],E["batoni"],C["batoni_opposing_painting"]],relation=True,
      layer="authorial interpretation")
add_s("st-chp10-p298-novelli-declined-russia-invitation",349,349,E["novelli"],C["russia_destination"],
      "novelli_declined_an_invitation_to_russia_because_of_the_climate",
      "the thought of the climate made him refuse", "an invitation to Russia.2",
      "Haskell says the thought of the climate made Novelli refuse an invitation to Russia.",
      "The inviter and intended city are not named; footnote 2 remains pending in the consolidated notes segment.",
      [E["novelli"],C["russia_destination"]],relation=True,footnote=2)
add_s("st-chp10-p298-catherine-tiepolo-purchase",349,349,E["catherine"],C["tiepolo_banquet_cleopatra"],
      "catherines_purchase_of_tiepolos_banquet_of_cleopatra_is_presented_as_evidence_of_her_admiration_for_venetian_art",
      "In any case Catherine", "her purchase of Tiepolo’s Banquet of Cleopatra.",
      "Haskell presents Catherine's purchase of Tiepolo's Banquet of Cleopatra as stronger evidence of her admiration for Venetian art than the relatively minor artists and works she attracted to her distant court.",
      "'Rather minor' is Haskell's comparative judgement; the passage does not list all artists or works attracted to the court.",
      [E["catherine"],E["venetian_art"],E["venetian_artists"],E["tiepolo"],C["tiepolo_banquet_cleopatra"]],
      relation=True,layer="authorial interpretation")
add_s("st-chp10-p298-algarotti-acquired-banquet-for-augustus",349,349,C["tiepolo_banquet_cleopatra"],E["augustus_iii_algarotti_index"],
      "algarotti_had_earlier_acquired_tiepolos_banquet_of_cleopatra_for_augustus_iii",
      "This masterpiece had been among those acquired", "many years earlier3",
      "Haskell says the painting had been among those Francesco Algarotti acquired for Augustus III many years earlier.",
      "This is the source's patronage and acquisition account; footnote 3's Chapter 14 cross-reference remains pending in the consolidated notes segment.",
      [C["tiepolo_banquet_cleopatra"],E["algarotti"],E["augustus_iii_algarotti_index"]],relation=True,footnote=3)
add_s("st-chp10-p298-banquet-transferred-and-power-balance",349,351,C["tiepolo_banquet_cleopatra"],E["st_petersburg"],
      "the_banquet_was_transferred_to_st_petersburg_in_the_1760s_which_haskell_reads_as_a_reflection_of_european_power_change_and_venetian_art_diffusion",
      "and its transference to", "Venetian art.",
      "The Banquet of Cleopatra was transferred to St Petersburg in the 1760s; Haskell interprets this movement as a striking reflection of Europe's changing balance of power, which had long influenced the diffusion of Venetian art.",
      "The transfer is reported by Haskell; the balance-of-power statement is his interpretation and does not by itself establish a causal account of this individual transfer.",
      [C["tiepolo_banquet_cleopatra"],E["st_petersburg"],E["europe"],E["venetian_art"]],
      relation=True,layer="authorial interpretation")
add_s("st-chp10-p298-venetian-artists-drawn-to-foreign-cities",351,352,E["venetian_artists"],E["london"],
      "venice_was_a_passive_onlooker_as_many_of_its_best_artists_and_pictures_were_drawn_to_named_foreign_cities",
      "But though it is true that Venice itself", "Dresden and Würzburg,",
      "Haskell says Venice had to remain a passive onlooker while many of its best artists and pictures were drawn to London, Paris, Düsseldorf, Madrid, Dresden and Würzburg.",
      "The passage names destinations collectively but does not identify the individual artists, pictures, patrons, or routes.",
      [E["venice_city"],E["venetian_artists"],E["london"],E["paris"],E["dusseldorf"],E["madrid"],E["dresden_city"],E["wurzburg_city"]],
      relation=True,layer="authorial interpretation")
add_s("st-chp10-p298-foreigner-native-genius",352,352,C["dominant_foreigner"],C["native_genius"],
      "haskell_foreshadows_a_subtler_relationship_between_the_dominant_foreigner_and_native_genius_than_one_based_on_military_and_commercial_power",
      "it will become apparent in the next chapter", "military strength and commercial wealth.",
      "Haskell foreshadows a more subtle relationship between the dominant foreigner and native genius than one built essentially on military strength and commercial wealth.",
      "This is an authorial framing of the following chapter, not a claim about a named foreigner or artist; the next-chapter source segment is linked for context.",
      [C["dominant_foreigner"],C["native_genius"]],layer="authorial interpretation",cross=[NEXT])
add_s("st-chp10-p298-republic-attractions-and-settlement",352,352,C["foreign_residents"],E["republic"],
      "the_republic_retained_attractions_for_visitors_and_people_free_to_settle_within_its_frontiers",
      "For the Republic still retained many attractions", "the city’s treasures.",
      "Haskell says the Republic retained many attractions: kings and landowners could glimpse them on brief holidays, while others were free to settle within its frontiers and gain deeper awareness of the city's treasures.",
      "The visitors and settlers are unnamed collective groups; 'the city' refers to Venice, while 'the Republic' is the political entity.",
      [C["foreign_residents"],E["republic"],E["venice_city"]],relation=True,layer="authorial interpretation",cross=[NEXT])

new_ids = {row["candidate_id"] for row in newc}
all_ids = cids | new_ids
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < 346 or q["source_line_end"] > 352:
        raise SystemExit(f"statement range outside p.298 body: {row['statement_id']}")
    if row["subject_candidate_id"] not in all_ids or row["object_candidate_id"] not in all_ids:
        raise SystemExit(f"statement foreign key missing: {row['statement_id']}")
    if not all(cid in all_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"mentioned candidate missing: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping new mentions: {left[2]} / {right[2]}")

cov[SEG].update({"disposition":"reviewed", "migration_status":"complete", "source_line_ranges":"L346-352",
                 "note":"Printed p.298 body L346-352 checked against CHP-10.pdf physical page 27. Recorded Catherine the Great's 1762 accession, taste and policy; Bellotto's planned St Petersburg journey, redirection to Warsaw and Warsaw view group; Novelli's 1772 Creusa picture, Batoni comparison and declined Russian invitation; Catherine's purchase of Tiepolo's Banquet of Cleopatra, its earlier acquisition for Augustus III by Algarotti and transfer to St Petersburg; and Haskell's account of Venetian artistic movement, foreign settlement and the dominant foreigner/native genius contrast. Reused page-indexed candidates for Catherine, Bellotto, Stanislas Poniatowski, Novelli, Batoni, Tiepolo, Algarotti, Augustus III and named cities; added distinct candidates for Warsaw, Russia, named work groups, mythological referents and conceptual categories without resolving cross-chapter identity. Scan-only S2 corrections: OCR 'S t Petersburg' reads 'St Petersburg'; 'Diisseldorf' reads 'Düsseldorf'; 'landowners-could' reads 'landowners could'. Footnotes 1-3 are not in this body segment and remain pending in the consolidated notes segment."})
cov[NEXT]["note"] = "Next source-order segment is printed p.299 at L354-366; inspect chapter heading, body, and the footnote 4 excerpt against the scan before migration."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"segment_sha256":SEG_SHA,"new_candidates":len(newc),
                  "candidate_ids":[row["candidate_id"] for row in newc],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p297":cov[PREV]["migration_status"],
                  "p298":cov[SEG]["migration_status"],"p299":cov[NEXT]["migration_status"]}},
                 ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.298 S2 body migration; footnotes remain in the consolidated notes segment.")
