"""Controlled S2 migration for printed p.291; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l240-251"
SEG = "chp-10:10_CHP-10_intro:l253-266"
NEXT = "chp-10:10_CHP-10_intro:l268-277"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "d51d364d093f8f89a4d92df6693b5bde7a552daf931d9f67b7a376778400315e"
BACKUP = ".bak-s2-chp10-p291-reapply-20261002"


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
body = "\n".join(src[252:266])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != SEG_SHA or src[252].strip() != "[Page 291]":
    raise SystemExit("p.291 source segment hash/page mismatch")
if "appeared in 1741" not in body or "Twenty pieces I see of him" not in body:
    raise SystemExit("p.291 scan-checked text no longer matches source")

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
if maximum != 9031:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "complete")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "mcswiny": "cand-1466", "scheme": "cand-9007", "planned_volume": "cand-9031",
    "british_worthies": "cand-9013", "richmond": "cand-2194", "boucher": "cand-0423",
    "cochin": "cand-0793", "cars": "cand-0590", "william_iii": "cand-2814",
    "anne": "cand-0110", "george_i": "cand-1140", "newton": "cand-1739",
    "smith": "cand-2443", "carriera": "cand-0581", "canaletto": "cand-0501",
    "england": "cand-8983",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (("richmond", E["richmond"], "289, 290, 291", "and McSwiny's British Worthies"),
                            ("smith", E["smith"], "291", "and McSwiny"),
                            ("canaletto", E["canaletto"], "291, 292", "and McSwiny")):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected page-specific index candidate {key}={cid}")

NEW_SPECS = [
    ("published_volume", "Tombeaux des Princes grands capitaines et autres hommes illustres, qui ont fleuri dans la Grande-Bretagne vers la fin du XVII et le commencement du XVIII siècle (1741 edition)", "archive",
     "The 1741 published volume that Haskell presents after the subscription proposal. It has eighteen plates, including nine allegorical tombs, rather than the proposed fifty; retain the printed French title and keep it distinct from the proposed-volume record.", 258),
    ("lord_dorset", "Lord Dorset (hero named in McSwiny's Tombeaux des Princes; identity pending)", "person",
     "Named as one of two heroes given a Character in the 1741 volume. The title alone is insufficient to identify the individual; defer identity resolution to S3.", 259),
    ("canaletto_letter", "McSwiny letter assessing Canaletto pictures (body dates it 1727; note 3 cites a 1730 letter)", "archive",
     "A quoted letter to a client in which McSwiny assesses Canaletto pictures. The body dates it to 1727, while printed note 3 cites a letter to John Conduitt dated 27 September 1730; preserve this discrepancy pending migration of the consolidated notes segment.", 264),
    ("queen_mary", "Queen Mary (named in McSwiny's proposed account of royal reigns; identity pending)", "person",
     "Named in the projected account of memorable transactions. The passage does not specify a regnal number; defer identity resolution to S3.", 256),
    ("king_george", "King George (named in McSwiny's proposed account; precise ruler not specified)", "person",
     "Named without a regnal number in the projected account. Do not silently align with George I or another ruler before S3.", 256),
    ("british_nation", "British Nation (collective polity as phrased in the proposed volume)", "",
     "The pamphlet's collective political wording for the reputation and credit advanced by the projected volume. Preserve this wording pending type and identity alignment; do not collapse it into England.", 256),
    ("french_artists", "French artists who engraved the actual tombs in the 1741 volume (unnamed group)", "",
     "Haskell refers collectively to French artists who engraved the actual tombs. No individuals are named in this passage; preserve the group as type-undecided rather than inventing members.", 262),
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

plan = next(row for row in candidates if row["candidate_id"] == E["planned_volume"])
old_plan_detail = "A publication project described in the subscription pamphlet: 24 sepulchral pieces, 24 inscription plates, a frontispiece, and a title plate. The passage gives proposed dimensions, not evidence that the volume was completed."
if plan["detail"] != old_plan_detail:
    raise SystemExit("planned-volume candidate detail changed")
plan["detail"] = "A publication project described in the subscription pamphlet: 24 sepulchral pieces, 24 inscription plates, a frontispiece, and a title plate. P.291 presents the 1741 Tombeaux des Princes as the volume that followed this proposal, while reporting eighteen rather than fifty plates; preserve the author's account and do not treat the planned specification as the final book's contents."

offsets, offset = {}, 0
for line in range(253, 267):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p291-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    positions, at = [], offsets[line]
    line_end = at + len(src[line - 1])
    while True:
        at = body.find(surface, at)
        if at < 0 or at >= line_end:
            break
        positions.append(at - offsets[line])
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = offsets[line] + positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("worthies",254,"deceased Worthies",E["british_worthies"],"References the previously described commemorative subject group."),
    ("contemporaries",254,"Contemporaries",E["british_worthies"],"Projected additional sitters/subjects; do not infer individual identities."),
    ("king-william",256,"King William",E["william_iii"],"Source's proposed reign list; identity alignment remains S3."),
    ("queen-mary",256,"Queen Mary",C["queen_mary"],"No regnal number is given in this projected list."),
    ("queen-anne",256,"Queen Anne",E["anne"],"Source's proposed reign list."),
    ("king-george",256,"King George",C["king_george"],"No regnal number is given; retain an unresolved candidate."),
    ("british-nation",256,"British Nation",C["british_nation"],"Collective political wording retained; not collapsed into England."),
    ("published-volume-title",258,"Tombeaux des Princes grands capitaines et autres hommes illustres, qui ont fleuri dans la Grande-Bretagne vers la fin du XVII et le commencement du XVIII siecle",C["published_volume"],"S0 OCR lacks the printed accent in 'siècle'; the scan confirms it. Keep the 1741 book distinct from the proposed volume."),
    ("mcswiny-return",259,"McSwiny",E["mcswiny"],"Subject of Haskell's approximate return date."),
    ("richmond-collection",259,"Duke of Richmond",E["richmond"],"Mapped to the page-specific index entry for McSwiny's British Worthies."),
    ("dorset",259,"Lord Dorset",C["lord_dorset"],"Hero named in the published book; identity pending S3."),
    ("newton",259,"Sir\nIsaac Newton",E["newton"],"Name spans a source line break."),
    ("william-iii",260,"William III",E["william_iii"],"Named in the list of reigns omitted from the published account."),
    ("anne-reign",260,"Anne",E["anne"],"Named in the list of reigns omitted from the published account."),
    ("george-i",260,"George I",E["george_i"],"The published book's omitted-reigns list specifies George I."),
    ("boucher-design",261,"Boucher",E["boucher"],"The page-specific index sub-entry is for designs for Tombeaux des Princes."),
    ("cochin",261,"C. N. Cochin",E["cochin"],"Named as an engraver of the inscription plates."),
    ("cars",261,"Laurence Cars",E["cars"],"Named as an engraver of the inscription plates."),
    ("french-artists",262,"French artists",C["french_artists"],"Collective phrase attached to engraving the actual tombs; no individual artists are identified."),
    ("boucher-evaluation",262,"Boucher",E["boucher"],"Haskell compares the plates' vitality with Boucher's work."),
    ("mcswiny-reluctance",263,"McSwiny",E["mcswiny"],"Subject of Haskell's interpretation of the subscriber shortage."),
    ("smith",264,"Joseph Smith",E["smith"],"Mapped to the page-specific index candidate for Smith and McSwiny."),
    ("carriera",264,"Rosalba Garriera",E["carriera"],"S0 OCR spelling retained in the mention span; the scan reads Carriera."),
    ("canaletto-views",264,"Canaletto",E["canaletto"],"Mapped to the page-specific index candidate for Canaletto and McSwiny."),
    ("canaletto-first-foreign",264,"this artist",E["canaletto"],"Corefers to Canaletto in the same paragraph."),
    ("canaletto-letter",264,"Canaletto",E["canaletto"],"Artist assessed in the quoted client letter.",1),
    ("mcswiny-letter",264,"he wrote",E["mcswiny"],"Refers to McSwiny as the letter's reported author."),
    ("client-letter",264,"a client in 1727",C["canaletto_letter"],"The body gives 1727; note 3's 1730 John Conduitt citation remains to be migrated and reconciled."),
    ("canaletto-letter-subject",264,"some pictures by Canaletto",E["canaletto"],"Object of the reported letter's evaluation."),
    ("canaletto-letter-evaluation",265,"him",E["canaletto"],"Pronoun corefers to Canaletto in McSwiny's quoted assessment."),
    ("mcswiny-commission-open",266,"McSwiny",E["mcswiny"],"The sentence opens a commission claim that continues in the next segment."),
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
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 291,
                  "pdf_physical_page": 20, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
    if cross:
        qualifiers["cross_reference_segments"] = cross
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


add_s("st-chp10-p291-proposed-volume-content",254,256,E["planned_volume"],None,
      "pamphlet_proposes_additional_contemporary_worthies_and_reign_history_if_subscriptions_allow",
      "‘To which will be added", "King George.",
      "The pamphlet proposes conditionally adding accounts of deceased worthies and contemporaries across court, military, church, state and learning, plus notable events in the reigns named in the text.",
      "The additions depend on the encouragement of subscribers; 'King George' and 'Queen Mary' retain the source wording without regnal identification.",
      [E["planned_volume"],E["british_worthies"],E["william_iii"],C["queen_mary"],E["anne"],C["king_george"],C["british_nation"]],
      speaker="McSwiny's pamphlet quoted by Haskell",layer="reported conditional publication proposal",footnote=None)
add_s("st-chp10-p291-proposed-volume-embellishments",257,257,E["planned_volume"],None,
      "pamphlet_proposes_vignettes_busts_medallions_and_other_embellishments",
      "‘The Whole to be adorn’d", "Masters in Europe.’",
      "The pamphlet proposes vignettes, busts, medallions, cul-de-lampes and other embellishments designed and engraved by celebrated European masters.",
      "This describes the proposed publication, not the contents of the 1741 volume.",
      [E["planned_volume"]],speaker="McSwiny's pamphlet quoted by Haskell",layer="reported publication proposal")
add_s("st-chp10-p291-volume-publication-and-disappointment",258,259,C["published_volume"],E["mcswiny"],
      "haskell_says_1741_volume_must_have_disappointed_mcswiny_who_had_returned_to_england_about_ten_years_earlier",
      "The volume—", "some ten years earlier.",
      "Haskell says the French-titled volume appeared in 1741, was magnificent, and must have disappointed McSwiny, who had returned to England about ten years earlier.",
      "The volume is presented as the publication following the prior subscription proposal; 'must have disappointed' is Haskell's inference, and the return date is approximate.",
      [C["published_volume"],E["planned_volume"],E["mcswiny"]],layer="authorial report and inference")
add_s("st-chp10-p291-volume-plate-and-tomb-count",259,259,C["published_volume"],E["richmond"],
      "published_volume_had_eighteen_plates_including_nine_allegorical_tombs_all_from_richmond_collection",
      "There were eighteen instead of fifty plates", "the Duke of Richmond’s collection.",
      "Haskell reports that the published volume had eighteen rather than the proposed fifty plates, and that its nine engraved allegorical tombs all came from the Duke of Richmond's collection.",
      "This distinguishes the realized publication from the earlier proposal; the exact nine works are not listed in this body passage and note 2 remains pending.",
      [C["published_volume"],E["planned_volume"],E["richmond"]],relation=True)
add_s("st-chp10-p291-volume-characters-and-reign-history",259,260,C["published_volume"],None,
      "only_dorset_and_newton_received_characters_and_no_account_of_three_reigns_was_included",
      "Only two of the heroes", "George I.",
      "Haskell says only Lord Dorset and Sir Isaac Newton were given Characters, and the volume contained no account of notable transactions in the reigns of William III, Anne and George I.",
      "'Characters' retains the source's term for the included biographical accounts; this statement describes omissions from the realized book.",
      [C["published_volume"],C["lord_dorset"],E["newton"],E["william_iii"],E["anne"],E["george_i"]])
add_s("st-chp10-p291-volume-tribute",260,260,C["published_volume"],E["mcswiny"],
      "haskell_calls_volume_a_fine_tribute_to_mcswinys_enterprise_and_taste",
      "It is none the less a fine tribute", "taste.",
      "Haskell calls the volume a fine tribute to McSwiny's enterprise and taste.",
      "This is the author's evaluation.",
      [C["published_volume"],E["mcswiny"]],layer="authorial evaluation")
add_s("st-chp10-p291-inscription-plate-production",260,262,C["published_volume"],E["boucher"],
      "each_painting_preceded_by_inscription_plate_with_frieze_designed_by_boucher_and_engraved_by_cochin_cars_and_others",
      "Each painting is preceded", "French artists.",
      "Haskell says each painting was preceded by an inscription plate naming its hero within a decorative frieze designed by Boucher and engraved by C. N. Cochin, Laurence Cars and others; engravings of the actual tombs were also made by French artists.",
      "The page attributes different production roles to the named artists; unnamed collaborators remain unspecified.",
      [C["published_volume"],E["boucher"],E["cochin"],E["cars"],C["french_artists"]],speaker="Haskell",layer="authorial report",relation=True,footnote=1)
add_s("st-chp10-p291-inscription-plate-evaluation",262,262,C["published_volume"],None,
      "haskell_says_inscription_plates_allude_to_heroes_achievements_and_have_rare_vitality_in_bouchers_work",
      "They contain allegorical allusions", "Boucher’s work.",
      "Haskell says the inscription plates allude to the heroes' achievements and have a tense, virile vitality rarely found in Boucher's work.",
      "This is an aesthetic judgment about the plates, not an independently verified property.",
      [C["published_volume"],E["boucher"]],layer="authorial evaluation")
add_s("st-chp10-p291-subscriber-failure-interpretation",263,263,E["scheme"],None,
      "haskell_interprets_painting_criticism_and_subscription_failure_as_english_reluctance_toward_contemporary_italian_history_painting",
      "The criticisms of the paintings", "even when heavily disguised.",
      "Haskell argues that criticism of the paintings and failure to attract enough subscribers show English reluctance to welcome contemporary Italian history painting, even when heavily disguised.",
      "This is Haskell's broad interpretation of cultural taste, not a count or survey of English opinion.",
      [E["scheme"],E["mcswiny"]],layer="authorial interpretation")
add_s("st-chp10-p291-mcswiny-smith-trade",264,264,E["mcswiny"],E["smith"],
      "mcswiny_and_close_friend_joseph_smith_dealt_in_carriera_pastels_and_canaletto_views",
      "With his close friend", "views by Canaletto.",
      "Haskell says McSwiny dealt with his close friend Joseph Smith, an English businessman, in pastels by Rosalba Carriera and views by Canaletto.",
      "The source's OCR gives 'Garriera'; the scan reads Carriera. Footnote 2's Malamani citation remains to be migrated.",
      [E["mcswiny"],E["smith"],E["carriera"],E["canaletto"]],layer="authorial report",relation=True,footnote=2)
add_s("st-chp10-p291-canaletto-early-patronage",264,264,E["mcswiny"],E["canaletto"],
      "mcswiny_was_among_canalettos_first_foreign_patrons_but_doubted_his_merits",
      "Indeed he was among this artist’s first foreign patrons", "about his merits.",
      "Haskell says McSwiny was among Canaletto's first foreign patrons, although he had strong doubts about Canaletto's merits.",
      "Both the priority claim and the evaluation are attributed to Haskell.",
      [E["mcswiny"],E["canaletto"]],layer="authorial report and evaluation",relation=True)
add_s("st-chp10-p291-canaletto-letter-assessment",264,265,C["canaletto_letter"],E["canaletto"],
      "mcswiny_letter_reports_disliking_eighteen_of_twenty_canaletto_pictures_and_criticizes_artist",
      "he wrote to a client in 1727", "his own price",
      "In a letter that Haskell dates to 1727, McSwiny tells a client he dislikes eighteen of twenty Canaletto pictures he has seen, would not give some London-bound examples house room or two pistols each, and calls the artist covetous and greedy.",
      "These are McSwiny's reported opinions, not established facts about Canaletto. Printed note 3 cites a letter to John Conduitt dated 27 September 1730, conflicting with the body's 1727 date; preserve both pending consolidated-note review.",
      [C["canaletto_letter"],E["mcswiny"],E["canaletto"]],speaker="McSwiny quoted by Haskell",
      layer="reported correspondence and opinion",footnote=3)

cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L254-266",
                 "note":"Printed p.291 was checked against CHP-10.pdf physical page 20. Captured the conditional additions and embellishments proposed for the subscription volume; the 1741 Tombeaux des Princes as Haskell's account of its realization, with eighteen rather than fifty plates, nine Richmond-collection tombs, two Characters, and missing reign histories; the inscription-plate production and Haskell's assessments; McSwiny/Smith trade in Carriera pastels and Canaletto views; and McSwiny's reported criticism of Canaletto. The body dates the quoted client letter to 1727 while note 3 cites a 27 September 1730 letter to John Conduitt; preserve this discrepancy until the consolidated note segment is migrated. Correct OCR 'Garriera' to printed 'Carriera' only in S2 notes. The final clause at L266 ('he commissioned a number of') remains open to p.292 L268; footnotes 1-3 remain pending in consolidated notes."})
cov[NEXT]["note"] = "Next source-order segment is printed p.292 at L268-277; p.291 L266 ends in an incomplete commission sentence. Footnotes 1-3 printed on p.291 remain in the consolidated notes segment."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"new_candidates":len(newc),"new_candidate_ids":[row["candidate_id"] for row in newc],
                  "updated_candidates":[E["planned_volume"]],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p290":cov[PREV]["migration_status"],
                  "p291":cov[SEG]["migration_status"],"p292":cov[NEXT]["migration_status"]}},ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.291 S2 migration; p.291 remains partial pending p.292 continuation and consolidated notes.")
