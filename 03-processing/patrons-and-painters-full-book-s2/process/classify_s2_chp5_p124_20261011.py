from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
PDF = ROOT / "02-sources/01-book/CHP-5.pdf"
PAGE_IMAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p124_page_review_20261011.png"
BODY_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l35-49"
NOTES_SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l125-147"
SOURCE_SHA256 = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
PDF_SHA256 = "f63dca79808fde73ba10aa9414fef89bc8ca5e77ed829b2d5c86f23719e0674a"
PAGE_IMAGE_SHA256 = "f2c6cbc1ac4c334af4e37528b44c6582e94d6545e35ebfaab99a998058caeb30"
BODY_SEGMENT_SHA256 = "fe94061e20be7e9eaead12d90c3d54f6867f09503a7b2a8ea93e0e3e1cfff711"
NOTE_SEGMENT_SHA256 = "5fdb179fd5637ce1d0a0b6b3da66e4e871452e25debcd265e4749060845324e8"
TABLES = {
    "statements": ROOT / "04-knowledge/tables/book-statements.jsonl",
    "candidates": ROOT / "04-knowledge/tables/entity-candidates.csv",
    "mentions": ROOT / "04-knowledge/tables/mentions.csv",
    "coverage": ROOT / "04-knowledge/tables/s2-coverage.csv",
}
EXPECTED_TABLE_SHA256 = {
    "statements": "06e56489ae0136e1a00512c3f34f58762eef6a1834566d840d006f6b65cbc777",
    "candidates": "846dcd41f560846c52057da29e0f94cb9fe9e83a1c6763c8316699fc2daf1a1d",
    "mentions": "61103eb1409046d9d6409f0b3953b68f7dd0a99ee0073e7157dffd7e0b7b6426",
    "coverage": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = ".bak-s2-chp5-p124-20261011"
RELATION_NOTE = "S2 source-attributed relation candidate only; this classification does not create a formal S6 edge."
NONRELATION_NOTE = "This is a source-attributed biographical, contextual, negative, evidentiary, or interpretive assertion; it does not assert a specific binary relation."

NOTE_START_IDS = [
    "st-chp5-note-p124-n1-monconys-1664",
    "st-chp5-note-p124-n1-bellori-drawings",
    "st-chp5-note-p124-n1-bellori-other-items",
]
NOTE_CONTINUATION_IDS = [
    "st-chp5-p124-passeri-simonelli-connoisseur",
    "st-chp5-note-p124-n1-passeri-relations-rosa",
    "st-chp5-note-p124-n1-passeri-rosa-letters",
    "st-chp5-p124-scaramuccia-print-dedication",
    "st-chp5-note-p124-n1-scaramuccia-dedicated-by",
    "st-chp5-note-p124-n1-scaramuccia-inscription",
    "st-chp5-p124-testa-letter-debt-indication",
    "st-chp5-p124-chigi-archive-career-reference",
    "st-chp5-p124-castiglione-dedication-interpretation",
    "st-chp5-note-p124-n1-castiglione-publisher-identification",
]

CANDIDATES = [
    {
        "candidate_id": "cand-11709",
        "canonical_name": "Unnamed distinguished and fashionable patients visited by Giulio Mancini (p.124)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell refers collectively to Mancini's distinguished and fashionable patients; no patients are individually named.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L36",
    },
    {
        "candidate_id": "cand-11710",
        "canonical_name": "Various unnamed cardinals under whom Niccolò Simonelli served (p.124)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell says Simonelli served under various cardinals but identifies none in this passage.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L37",
    },
    {
        "candidate_id": "cand-11711",
        "canonical_name": "Other visitors for whom Simonelli probably repeated his assistance (p.124)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell infers that Simonelli probably did the same for other visitors; no visitors or additional episodes are identified.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L40",
    },
    {
        "candidate_id": "cand-11712",
        "canonical_name": "Carlo, Mancini, and Simonelli as the three figures compared by Haskell (p.124)",
        "suggested_type": "term",
        "status": "open",
        "detail": "A source-defined grouping of Ferrante Carlo, Giulio Mancini, and Niccolò Simonelli for Haskell's comparison; not a formal organization.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L41",
    },
    {
        "candidate_id": "cand-11713",
        "canonical_name": "Many leading artists of Carlo, Mancini, and Simonelli's day (p.124)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell says the three men were friends and patrons of many leading artists but does not name the members of this group here.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L42",
    },
    {
        "candidate_id": "cand-11714",
        "canonical_name": "Artists Simonelli kept in close touch with: Salvator Rosa, Pietro Testa, and Castiglione (p.124)",
        "suggested_type": "term",
        "status": "open",
        "detail": "Haskell groups Rosa, Testa, and Castiglione as interesting artists outside the main stream of fashion with whom Simonelli was in close touch; retain the source-defined grouping.",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT_ID}#L38",
    },
]


def S(statement_id, segment, subject, object_, predicate, line_start, line_end,
      quote, claim, qualification, mentioned, relation, *, layer=None,
      note_ids=None, note_continuation=False, linked_body=None, extra=None):
    return {
        "statement_id": statement_id,
        "segment": segment,
        "segment_id": BODY_SEGMENT_ID if segment == "body" else NOTES_SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "line_start": line_start,
        "line_end": line_end,
        "quote": quote,
        "claim": claim,
        "qualification": qualification,
        "mentioned": list(dict.fromkeys(mentioned)),
        "relation": relation,
        "layer": layer or ("authorial narration" if segment == "body" else "authorial footnote"),
        "note_ids": list(note_ids or []),
        "note_continuation": note_continuation,
        "linked_body": list(linked_body or []),
        "extra": dict(extra or {}),
    }


REVISIONS = [
    S("st-chp5-p124-mancini-medical-dealing", "body", "cand-1507", "cand-11709", "solicited_picture_gifts_from_patients", 36, 36,
      "he would suggest at the critical moment that some of their pictures would make an acceptable gift",
      "Haskell says Mancini used his medical visits to suggest that pictures from his distinguished and fashionable patients would make acceptable gifts.",
      "The source describes a suggestion that pictures would make acceptable gifts; it does not say that the patients transferred them.", ["cand-1507", "cand-11709"], True),
    S("st-chp5-p124-monconys-other-visitors-inference", "body", "cand-2434", "cand-11711", "repeat_visitor_assistance_inferred", 40, 40,
      "No doubt he did the same for other visitors.",
      "Haskell infers that Simonelli probably repeated his assistance for other visitors.",
      "This is explicitly the author's inference; no additional visit, visitor, or particular service is documented.", ["cand-2434", "cand-11711"], True),
    S("st-chp5-p124-monconys-rome-visit", "body", "cand-2434", "cand-1685", "guided_visitor_around_studios", 40, 40,
      "it was Simonelli who took him round the studios",
      "Haskell says Simonelli took Monconys around artists' studios during the latter's 1664 visit to Rome.",
      "The report is attributed to Haskell; the studios are not individually identified.", ["cand-2434", "cand-1685"], True,
      note_ids=NOTE_START_IDS[:1]),
    S("st-chp5-p124-passeri-simonelli-connoisseur", "body", "cand-2434", None, "reputation_as_connoisseur_cited", 43, 43,
      "Simonelli ‘stava in credito d’intendente’",
      "Haskell cites Passeri's description of Simonelli as enjoying a reputation as a connoisseur.",
      "The Italian phrase and Passeri citation are reported by Haskell; the cited source was not independently consulted.", ["cand-2434", "cand-1856"], False,
      layer="authorial footnote", note_continuation=True),
    S("st-chp5-p124-scaramuccia-print-dedication", "body", "cand-6018", "cand-2434", "dedicated_to", 44, 44,
      "Luigi Scaramuccia dedicated a print to him of Venus and Adonis",
      "Haskell says Luigi Scaramuccia dedicated a Venus and Adonis print to Simonelli.",
      "The print is represented by the body-derived work candidate cand-6018. The index subentry cand-2391 remains a separate unresolved S3 alignment candidate.", ["cand-2390", "cand-2391", "cand-6018", "cand-2434"], True,
      layer="authorial footnote", note_continuation=True),
    S("st-chp5-p124-simonelli-administration", "body", "cand-2434", "cand-6017", "was_in_charge_of", 37, 37,
      "ending up in charge of the Chigi household during the papacy of Alexander VII",
      "Haskell says Simonelli ended up in charge of the Chigi household during Alexander VII's papacy.",
      "The Chigi household is treated as an organization, not as a building or a family relationship; the period is bounded by the papacy named in the source.", ["cand-2434", "cand-6017", "cand-0665"], True,
      note_ids=["st-chp5-p124-chigi-archive-career-reference"]),
    S("st-chp5-p124-simonelli-castiglione-print", "body", "cand-6022", "cand-2434", "dedicated_to", 38, 39,
      "Castiglione whose publisher dedicated to him a fine print of\nDiogenes searching in vain for one honest man.",
      "Haskell says the publisher of Castiglione's Diogenes print dedicated it to Simonelli.",
      "The work is cand-6022. The publisher's identification as Gian Domenico Rossi comes from the signed dedication and Haskell's bracketed name at L49.", ["cand-0602", "cand-6022", "cand-6023", "cand-2434"], True,
      note_ids=["st-chp5-p124-castiglione-dedication-interpretation", "st-chp5-note-p124-n1-castiglione-publisher-identification"]),
    S("st-chp5-p124-simonelli-collection", "body", "cand-2434", "cand-11480", "assembled_collection", 37, 38,
      "He assembled a notable collection",
      "Haskell says Simonelli assembled a notable art collection.",
      "The collection candidate remains untyped and open; individual works are not identified in this statement.", ["cand-2434", "cand-11480"], True,
      note_ids=["st-chp5-note-p124-n1-bellori-drawings", "st-chp5-note-p124-n1-bellori-other-items"]),
    S("st-chp5-p124-simonelli-rosa-assistance", "body", "cand-2434", "cand-2236", "helped_launch_career_of", 38, 38,
      "Salvator Rosa whom he helped to launch",
      "Haskell says Simonelli helped launch Salvator Rosa's career.",
      "The account is attributed to Haskell; no more specific form of assistance is supplied in this sentence.", ["cand-2434", "cand-2236"], True,
      note_ids=["st-chp5-note-p124-n1-passeri-relations-rosa", "st-chp5-p124-passeri-simonelli-connoisseur"]),
    S("st-chp5-p124-simonelli-taste", "body", "cand-2434", None, "independent_cultivated_taste_assessed", 38, 38,
      "clearly a man of independent and cultivated taste",
      "Haskell characterizes Simonelli as a man of independent and cultivated taste.",
      "This is Haskell's evaluation, not an independently verified trait.", ["cand-2434"], False),
    S("st-chp5-p124-simonelli-testa-loan", "body", "cand-2434", "cand-2556", "loaned_money_to", 38, 38,
      "Pietro Testa to whom he lent money",
      "Haskell says Simonelli lent money to Pietro Testa.",
      "This body-text report is retained separately from the footnote's qualified inference about a letter that seems to show a debt.", ["cand-2434", "cand-2556"], True,
      note_ids=["st-chp5-p124-testa-letter-debt-indication"]),
    S("st-chp5-p124-simonelli-unofficial-dealing", "body", "cand-2434", None, "unofficial_picture_dealing_reported", 37, 37,
      "A third and almost equally influential figure who indulged in a certain amount of unofficial dealing was Niccolò Simonelli.",
      "Haskell presents Niccolò Simonelli as an influential figure who engaged in some unofficial dealing.",
      "This is a source-attributed description of activity; no transaction or counterparty is identified here.", ["cand-2434"], False,
      note_ids=NOTE_START_IDS),
    S("st-chp5-p124-simonelli-uses-contacts", "body", "cand-2434", "cand-11714", "used_artist_contacts_for_dealing", 39, 39,
      "Simonelli too took advantage of these contacts",
      "Haskell says Simonelli used his contacts among artists in the course of dealing.",
      "The contacts are the source-defined group of Rosa, Testa, and Castiglione; no particular transaction is identified.", ["cand-2434", "cand-11714", "cand-2236", "cand-2556", "cand-0602"], True,
      note_ids=NOTE_START_IDS[:1]),
    S("st-chp5-p124-testa-letter-debt-indication", "body", "cand-2556", "cand-2434", "possible_debt_indicated_by_letter", 44, 45,
      "a letter from the artist to Simonelli which seems to show that he owed him money",
      "Haskell says a letter from Pietro Testa to Simonelli seems to show that Testa owed him money.",
      "The source says ‘seems to show’; the drawing and letter are represented separately, and neither it nor the cited Blunt and Cooke publication was independently consulted.", ["cand-2556", "cand-2434", "cand-6019", "cand-6020", "cand-4627"], True,
      layer="authorial footnote", note_continuation=True,
      linked_body=["st-chp5-p124-simonelli-testa-loan"]),
    S("st-chp5-p124-three_figures-careers", "body", "cand-11712", None, "distinguished_clerical_bureaucratic_careers_reported", 42, 42,
      "All enjoyed distinguished careers in the clerical bureaucracy of the mid-seventeenth century",
      "Haskell says Carlo, Mancini, and Simonelli had distinguished careers in the mid-seventeenth-century clerical bureaucracy.",
      "The source-defined group refers to the three named men; this claim is separate from their non-membership in the Church and their friendships or patronage.", ["cand-11712", "cand-0560", "cand-1507", "cand-2434"], False),
    S("st-chp5-p124-three_figures-common", "body", "cand-11712", None, "shared_profile_assessed", 41, 41,
      "All three figures, Carlo, Mancini and Simonelli, thus had many features in common.",
      "Haskell says Carlo, Mancini, and Simonelli had many features in common.",
      "This is the author's comparative grouping, not a newly named organization.", ["cand-11712", "cand-0560", "cand-1507", "cand-2434"], False),
    S("st-chp5-note-p124-n1-bellori-drawings", "notes", "cand-2434", None, "drawings_by_named_artists_in_collection_reported", 142, 142,
      "Some information about his own collecting is given in Bellori’s Nota dei Musei, which says that he owned a ‘Studio di disegni li più eccellenti di Giulio Romano, di Polidoro, di Annibaie Carracci",
      "Haskell says Bellori's Nota dei Musei records Simonelli as owning drawings by Giulio Romano, Polidoro, and Annibale Carracci, among the finest artists.",
      "The statement reports Haskell's quotation of Bellori's inventory; the inventory was not independently consulted. OCR reads ‘Annibaie’; the printed reading is ‘Annibale’.", ["cand-2434", "cand-0272", "cand-4805", "cand-1194", "cand-0553", "cand-0576", "cand-11480"], False,
      layer="authorial footnote reporting Bellori's inventory", linked_body=["st-chp5-p124-simonelli-collection", "st-chp5-p124-simonelli-collection-contents", "st-chp5-p124-simonelli-favorite-annibale"]),
    S("st-chp5-note-p124-n1-bellori-other-items", "notes", "cand-2434", None, "other_collection_contents_reported", 142, 142,
      "con vario museo d’intagli, gemme, antichità, e cose peregrine, siccome anche di varie pitture eccellenti",
      "Haskell's Bellori quotation also lists prints, gems, antiquities, curiosities, and excellent paintings in Simonelli's collection.",
      "Individual objects and paintings are not identified; the inventory itself was not independently consulted.", ["cand-2434", "cand-0272", "cand-4805", "cand-11480"], False,
      layer="authorial footnote reporting Bellori's inventory", linked_body=["st-chp5-p124-simonelli-collection", "st-chp5-p124-simonelli-collection-contents"]),
    S("st-chp5-note-p124-n1-monconys-1664", "notes", "cand-2434", None, "artist_contacts_in_1664_reported", 142, 142,
      "See Monconys’ Journal des Voyages, 2eme partie, p. 439, for Simonelli’s contacts with artists in 1664.",
      "Haskell cites Monconys's Journal des Voyages, part 2, page 439, for Simonelli's contacts with artists in 1664.",
      "This is a citation locator, not a Simonelli–Monconys social relation; the cited page was not independently consulted.", ["cand-1685", "cand-11403", "cand-2434"], False,
      layer="authorial footnote citing a travel account", linked_body=["st-chp5-p124-simonelli-close-artist-contacts", "st-chp5-p124-monconys-rome-visit", "st-chp5-p124-monconys-introduced-poussin", "st-chp5-p124-monconys-introduced-claude", "st-chp5-p124-monconys-picture-sale"]),
    S("st-chp5-p124-castiglione-dedication-interpretation", "body", "cand-2434", None, "outlook_not_wholly_conformist_interpreted", 47, 49,
      "The suggestion that his outlook on the world was not wholly conformist comes from Castiglione’s print of Diogenes with its strange dedication from the publisher",
      "Haskell interprets the dedication on Castiglione's Diogenes print as suggesting that Simonelli's outlook was not wholly conformist.",
      "This is Haskell's interpretation of the print and its dedication, not an independently established description of Simonelli's beliefs. The quoted dedication is the publisher's voice, not Haskell's.", ["cand-2434", "cand-6022", "cand-0602", "cand-6023"], False,
      layer="authorial footnote", note_continuation=True,
      linked_body=["st-chp5-p124-simonelli-castiglione-print"]),
    S("st-chp5-p124-chigi-archive-career-reference", "body", "cand-2434", None, "career_source_location_cited", 46, 47,
      "The occasional fact about his career in the Chigi household can be traced in that family’s archives",
      "Haskell says occasional information about Simonelli's career in the Chigi household can be traced in the family's archives and cites Golzio (1939, page 155).",
      "This reports Haskell's source location and citation; no Chigi archival record or Golzio publication was independently consulted.", ["cand-2434", "cand-6017", "cand-6021", "cand-3501"], False,
      layer="authorial footnote citing archival records", note_continuation=True,
      linked_body=["st-chp5-p124-simonelli-administration"]),
]

NEW = [
    S("st-chp5-p124-mancini-patient-refusal", "body", "cand-11709", None, "patients_felt_unable_to_refuse_reported", 36, 36,
      "Few felt like refusing just then",
      "Haskell says few of Mancini's patients felt able to refuse his suggestion at the critical moment.",
      "The source's wording is retained and does not say that any particular patient accepted the suggestion.", ["cand-11709", "cand-1507"], False),
    S("st-chp5-p124-mancini-dealer-advantage", "body", "cand-1507", "cand-0125", "gained_advantages_over_rival_dealers", 36, 36,
      "from such opportunities he derived decisive advantages over all rival dealers",
      "Haskell says Mancini derived decisive advantages over rival art dealers from these opportunities.",
      "This is Haskell's comparative account; no rival dealer or individual transaction is named.", ["cand-1507", "cand-0125"], True),
    S("st-chp5-p124-mancini-treatise-knowledge", "body", "cand-1507", None, "knowledge_for_art_treatise_reported", 36, 36,
      "the knowledge needed to write a learned and most valuable artistic Treatise",
      "Haskell says Mancini gained knowledge for writing an art treatise.",
      "The body passage does not name the treatise; the existing index-derived cand-1508 mapping to Considerazioni sulla Pittura remains tentative for S3.", ["cand-1507", "cand-1508"], False),
    S("st-chp5-p124-simonelli-served-cardinals", "body", "cand-2434", "cand-11710", "served_under_cardinals", 37, 37,
      "he served under various cardinals",
      "Haskell says Simonelli served under various cardinals.",
      "The cardinals are unnamed in this passage and remain an open group candidate.", ["cand-2434", "cand-11710"], True),
    S("st-chp5-p124-simonelli-administrator-assessment", "body", "cand-2434", None, "efficient_administrator_assessed", 37, 37,
      "An obviously efficient administrator",
      "Haskell characterizes Simonelli as an obviously efficient administrator.",
      "This is the author's evaluation, distinct from the offices and responsibilities that follow.", ["cand-2434"], False),
    S("st-chp5-p124-simonelli-connoisseur-reputation", "body", "cand-2434", None, "reputation_as_connoisseur_reported", 37, 37,
      "He had some reputation as a connoisseur",
      "Haskell says Simonelli had some reputation as a connoisseur.",
      "The phrase ‘some reputation’ is preserved as a qualified source-attributed statement.", ["cand-2434"], False),
    S("st-chp5-p124-simonelli-advice-on-art", "body", "cand-2434", None, "gave_advice_on_art_reported", 37, 37,
      "liked to give advice on artistic matters",
      "Haskell says Simonelli liked to give advice on artistic matters.",
      "No recipient or particular advisory episode is named; this remains a scalar statement about his reported activity.", ["cand-2434"], False),
    S("st-chp5-p124-simonelli-favorite-annibale", "body", "cand-2434", "cand-0576", "favored_artist", 37, 38,
      "Annibale Carracci, his special favourite",
      "Haskell identifies Annibale Carracci as Simonelli's special favorite among the artists named in connection with the drawings.",
      "This preserves Haskell's wording and does not infer ownership of any individually identified Carracci work.", ["cand-2434", "cand-0576"], True),
    S("st-chp5-p124-simonelli-collection-contents", "body", "cand-11480", None, "collection_contents_reported", 37, 38,
      "a notable collection of drawings by Giulio\nRomano, Polidoro da Caravaggio and Annibale Carracci, his special favourite, as well as paintings, antiquities and cameos",
      "Haskell says Simonelli's collection included drawings by Giulio Romano, Polidoro da Caravaggio, and Annibale Carracci, as well as paintings, antiquities, and cameos.",
      "No individual drawing, painting, antiquity, or cameo is identified; the collection is represented by the existing open candidate cand-11480.", ["cand-11480", "cand-1194", "cand-0553", "cand-0576"], False),
    S("st-chp5-p124-simonelli-close-artist-contacts", "body", "cand-2434", "cand-11714", "kept_in_close_touch_with_artists", 38, 38,
      "he was in very close touch with a number of interesting artists outside the main stream of fashion",
      "Haskell says Simonelli was in very close touch with the source-defined group of artists that includes Rosa, Testa, and Castiglione.",
      "The group is represented collectively as the passage does; the named examples remain separate candidates and are not merged into it.", ["cand-2434", "cand-11714", "cand-2236", "cand-2556", "cand-0602"], True,
      note_ids=NOTE_START_IDS[:1]),
    S("st-chp5-p124-simonelli-testa-contact", "body", "cand-2434", "cand-2556", "was_in_close_contact_with", 38, 38,
      "Pietro Testa to whom he lent money",
      "Haskell names Pietro Testa among the artists with whom Simonelli was in close touch.",
      "This contact statement is distinct from the reported loan and the later letter-based inference about debt.", ["cand-2434", "cand-2556"], True),
    S("st-chp5-p124-simonelli-castiglione-contact", "body", "cand-2434", "cand-0602", "was_in_close_contact_with", 38, 39,
      "Castiglione whose publisher dedicated to him a fine print",
      "Haskell names Castiglione among the artists with whom Simonelli was in close touch.",
      "This contact statement is separate from the publisher's dedication of the print; Castiglione is not equated with the publisher.", ["cand-2434", "cand-0602"], True),
    S("st-chp5-p124-simonelli-more-respectable-than-mancini", "body", "cand-2434", None, "more_respectable_than_mancini_assessed", 39, 39,
      "he was obviously a much more respectable figure than Mancini",
      "Haskell describes Simonelli as much more respectable than Mancini.",
      "This is the author's comparative evaluation, not a formal relation or an independently verified moral judgment.", ["cand-2434", "cand-1507"], False),
    S("st-chp5-p124-monconys-visited-rome", "body", "cand-1685", "cand-4490", "visited_place", 40, 40,
      "Monsieur de Monconys visited Rome in 1664",
      "Haskell says Balthasar de Monconys visited Rome in 1664.",
      "The visit date and place are attributed to Haskell; this is separate from Simonelli's actions during the visit.", ["cand-1685", "cand-4490"], True,
      note_ids=NOTE_START_IDS[:1]),
    S("st-chp5-p124-monconys-introduced-poussin", "body", "cand-2434", "cand-1984", "introduced_visitor_to_artist", 40, 40,
      "introduced him to Poussin",
      "Haskell says Simonelli introduced Monconys to Nicolas Poussin.",
      "The reported introduction took place during Monconys's Rome visit in 1664.", ["cand-2434", "cand-1685", "cand-1984"], True,
      note_ids=NOTE_START_IDS[:1]),
    S("st-chp5-p124-monconys-introduced-claude", "body", "cand-2434", "cand-0767", "introduced_visitor_to_artist", 40, 40,
      "and Claude",
      "Haskell says Simonelli introduced Monconys to Claude Lorrain.",
      "The reported introduction took place during Monconys's Rome visit in 1664.", ["cand-2434", "cand-1685", "cand-0767"], True,
      note_ids=NOTE_START_IDS[:1]),
    S("st-chp5-p124-monconys-picture-sale", "body", "cand-2434", "cand-1685", "sold_unidentified_picture_to", 40, 40,
      "and sold him the odd picture",
      "Haskell says Simonelli sold Monconys an unidentified picture.",
      "The picture is not identified; this statement does not create a specific work candidate.", ["cand-2434", "cand-1685"], True,
      note_ids=NOTE_START_IDS[:1]),
    S("st-chp5-note-p124-n1-passeri-relations-rosa", "body", "cand-2434", "cand-2236", "relations_with_artist_reported_by_passeri", 43, 43,
      "who refers to his relations with Salvator Rosa",
      "Haskell says Passeri refers to Simonelli's relations with Salvator Rosa.",
      "The specific nature of the relationship is not specified by this passage; it is retained as a source-attributed relation candidate.", ["cand-2434", "cand-2236", "cand-1856"], True,
      layer="authorial footnote", note_continuation=True,
      linked_body=["st-chp5-p124-simonelli-rosa-assistance", "st-chp5-p124-simonelli-close-artist-contacts"]),
    S("st-chp5-note-p124-n1-passeri-rosa-letters", "body", "cand-2434", None, "references_in_rosa_letters_reported", 43, 43,
      "there are many references to him in Rosa’s letters",
      "Haskell says many references to Simonelli occur in Salvator Rosa's letters.",
      "This is a report about letter contents, not a direct social relation; the letters were not independently consulted.", ["cand-2434", "cand-2236"], False,
      layer="authorial footnote", note_continuation=True,
      linked_body=["st-chp5-p124-simonelli-rosa-assistance", "st-chp5-p124-simonelli-close-artist-contacts"]),
    S("st-chp5-note-p124-n1-scaramuccia-dedicated-by", "body", "cand-6018", "cand-2390", "dedicated_by", 44, 44,
      "Luigi Scaramuccia dedicated a print to him",
      "Haskell identifies Luigi Scaramuccia as the person who dedicated the Venus and Adonis print to Simonelli.",
      "The person candidate cand-2390 is distinct from the index-derived work candidate cand-2391; the print is cand-6018.", ["cand-6018", "cand-2390", "cand-2434", "cand-2391"], True,
      layer="authorial footnote", note_continuation=True),
    S("st-chp5-note-p124-n1-scaramuccia-inscription", "body", "cand-2434", None, "love_of_carracci_works_reported_in_inscription", 44, 44,
      "Simonelli was ‘inamorato dell’Opere dei Carracci’",
      "Haskell says the inscription on Scaramuccia's print describes Simonelli as enamoured of works by the Carracci.",
      "This is the inscription's characterization as quoted by Haskell; it does not identify an individual Carracci work.", ["cand-2434", "cand-2390", "cand-6018", "cand-0576"], False,
      layer="authorial footnote", note_continuation=True),
    S("st-chp5-note-p124-n1-castiglione-publisher-identification", "body", "cand-6023", None, "publisher_initials_identified_by_haskell", 49, 49,
      "G.D.R. [Gian Domenico Rossi] D.D.D.",
      "Haskell's bracket identifies the initials G.D.R. at the end of the dedication as Gian Domenico Rossi.",
      "The identification is reported from Haskell's bracketed note; no independent source check is claimed.", ["cand-6023", "cand-6022"], False,
      layer="authorial footnote", note_continuation=True,
      linked_body=["st-chp5-p124-simonelli-castiglione-print", "st-chp5-note-p124-castiglione-dedication-interpretation"]),
    S("st-chp5-p124-three_figures-not-church", "body", "cand-11712", None, "not_members_of_church_reported", 42, 42,
      "without themselves being in the Church",
      "Haskell says Carlo, Mancini, and Simonelli were not themselves in the Church.",
      "The source applies this qualification to all three named men; it is separate from their clerical-bureaucratic careers.", ["cand-11712", "cand-0560", "cand-1507", "cand-2434"], False),
    S("st-chp5-p124-carlo-friends-leading-artists", "body", "cand-0560", "cand-11713", "was_friend_of_leading_artists", 42, 42,
      "all were friends and patrons of many of the leading artists of their day",
      "Haskell says Ferrante Carlo was among the three men who were friends of many leading artists of their day.",
      "The word ‘all’ applies distributively to Carlo, Mancini, and Simonelli; the artists remain an unnamed group in this passage.", ["cand-0560", "cand-11713", "cand-1507", "cand-2434"], True),
    S("st-chp5-p124-mancini-friends-leading-artists", "body", "cand-1507", "cand-11713", "was_friend_of_leading_artists", 42, 42,
      "all were friends and patrons of many of the leading artists of their day",
      "Haskell says Giulio Mancini was among the three men who were friends of many leading artists of their day.",
      "The word ‘all’ applies distributively to Carlo, Mancini, and Simonelli; the artists remain an unnamed group in this passage.", ["cand-1507", "cand-11713", "cand-0560", "cand-2434"], True),
    S("st-chp5-p124-simonelli-friends-leading-artists", "body", "cand-2434", "cand-11713", "was_friend_of_leading_artists", 42, 42,
      "all were friends and patrons of many of the leading artists of their day",
      "Haskell says Niccolò Simonelli was among the three men who were friends of many leading artists of their day.",
      "The word ‘all’ applies distributively to Carlo, Mancini, and Simonelli; the artists remain an unnamed group in this passage.", ["cand-2434", "cand-11713", "cand-0560", "cand-1507"], True),
    S("st-chp5-p124-carlo-patrons-leading-artists", "body", "cand-0560", "cand-11713", "was_patron_of_leading_artists", 42, 42,
      "all were friends and patrons of many of the leading artists of their day",
      "Haskell says Ferrante Carlo was among the three men who were patrons of many leading artists of their day.",
      "The word ‘all’ applies distributively to Carlo, Mancini, and Simonelli; the artists remain an unnamed group in this passage.", ["cand-0560", "cand-11713", "cand-1507", "cand-2434"], True),
    S("st-chp5-p124-mancini-patrons-leading-artists", "body", "cand-1507", "cand-11713", "was_patron_of_leading_artists", 42, 42,
      "all were friends and patrons of many of the leading artists of their day",
      "Haskell says Giulio Mancini was among the three men who were patrons of many leading artists of their day.",
      "The word ‘all’ applies distributively to Carlo, Mancini, and Simonelli; the artists remain an unnamed group in this passage.", ["cand-1507", "cand-11713", "cand-0560", "cand-2434"], True),
    S("st-chp5-p124-simonelli-patrons-leading-artists", "body", "cand-2434", "cand-11713", "was_patron_of_leading_artists", 42, 42,
      "all were friends and patrons of many of the leading artists of their day",
      "Haskell says Niccolò Simonelli was among the three men who were patrons of many leading artists of their day.",
      "The word ‘all’ applies distributively to Carlo, Mancini, and Simonelli; the artists remain an unnamed group in this passage.", ["cand-2434", "cand-11713", "cand-0560", "cand-1507"], True),
]

NEW_MENTIONS = [
    ("m-chp5-p124-s2-patients", "cand-11709", "distinguished and fashionable patients", "Unspecified patient group in Haskell's account of Mancini's medical visits.", BODY_SEGMENT_ID),
    ("m-chp5-p124-s2-rival-dealers", "cand-0125", "all rival dealers", "Collective reference to Mancini's unnamed rivals in art dealing.", BODY_SEGMENT_ID),
    ("m-chp5-p124-s2-cardinals", "cand-11710", "various cardinals", "Unnamed cardinals under whom Simonelli reportedly served.", BODY_SEGMENT_ID),
    ("m-chp5-p124-s2-interesting-artists", "cand-11714", "a number of interesting artists outside the main stream of fashion", "Source-defined group exemplified by Rosa, Testa, and Castiglione.", BODY_SEGMENT_ID),
    ("m-chp5-p124-s2-other-visitors", "cand-11711", "other visitors", "Unnamed group in Haskell's explicit inference about repeated assistance.", BODY_SEGMENT_ID),
    ("m-chp5-p124-s2-three-figures", "cand-11712", "All three figures, Carlo, Mancini and Simonelli", "Source-defined grouping of the three men compared in the passage.", BODY_SEGMENT_ID),
    ("m-chp5-p124-s2-leading-artists", "cand-11713", "many of the leading artists of their day", "Unnamed group said to have been friends with and patronized by all three men.", BODY_SEGMENT_ID),
    ("m-chp5-note-p124-s2-journal", "cand-11403", "Journal des Voyages", "Bibliography candidate for Monconys's cited travel journal; the cited page was not independently consulted.", NOTES_SEGMENT_ID),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_hash(path: Path, expected: str, label: str) -> None:
    actual = digest(path.read_bytes())
    if actual != expected:
        raise SystemExit(f"STOP: {label} changed: {path} ({actual})")


def read_csv(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return raw, bom, text, reader.fieldnames, list(reader)


def emit_csv(headers, rows, bom: bool, source_text: str) -> bytes:
    newline = "\r\n" if "\r\n" in source_text else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=newline, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in headers})
    return (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")


def build_row(spec, body_text, note_text):
    text = body_text if spec["segment"] == "body" else note_text
    if spec["quote"] not in text:
        raise SystemExit(f"STOP: source quote not found for {spec['statement_id']}: {spec['quote']!r}")
    relation = spec["relation"]
    q = {
        "source_line_start": spec["line_start"],
        "source_line_end": spec["line_end"],
        "pdf_physical_page": 5,
        "printed_page_locator": "p.124n1" if spec["note_continuation"] or spec["segment"] == "notes" else "p.124",
        "claim": spec["claim"],
        "speaker": "Haskell",
        "text_layer": spec["layer"],
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "relation_candidate": relation,
        "relation_candidate_note": RELATION_NOTE if relation else NONRELATION_NOTE,
    }
    if spec["note_continuation"]:
        q.update({
            "footnote_marker": 1,
            "footnote_target_line": 142,
            "footnote_segment": NOTES_SEGMENT_ID,
        })
    if spec["note_ids"]:
        q.update({
            "footnote_numbers": [1],
            "footnote_links": [{
                "marker": 1,
                "note_line": 142,
                "note_segment": NOTES_SEGMENT_ID,
                "note_statement_ids": spec["note_ids"],
                "status": "linked",
            }],
            "footnote_link_status": "linked",
        })
    if spec["linked_body"]:
        q["linked_body_statement_ids"] = spec["linked_body"]
    q.update(spec["extra"])
    return {
        "statement_id": spec["statement_id"],
        "segment_id": spec["segment_id"],
        "subject_candidate_id": spec["subject_candidate_id"],
        "object_candidate_id": spec["object_candidate_id"],
        "predicate": spec["predicate"],
        "qualifiers": q,
        "original_quote": spec["quote"],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
    }


def prepare_spec(spec):
    spec = dict(spec)
    spec["extra"] = dict(spec["extra"])
    return spec


def mention_row(text, item):
    mention_id, candidate_id, surface, note, segment_id = item
    start = text.find(surface)
    if start < 0:
        raise SystemExit(f"STOP: mention surface not found for {mention_id}: {surface!r}")
    return {
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and atomize p.124 S2 statements; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the validated table changes")
    args = parser.parse_args()

    require_hash(SOURCE, SOURCE_SHA256, "canonical source")
    require_hash(PDF, PDF_SHA256, "chapter PDF")
    require_hash(PAGE_IMAGE, PAGE_IMAGE_SHA256, "p.124 page review image")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    body_text = "\n".join(lines[34:49])
    note_text = "\n".join(lines[124:147])
    if digest(body_text.encode("utf-8")) != BODY_SEGMENT_SHA256:
        raise SystemExit("STOP: p.124 body segment changed")
    if digest(note_text.encode("utf-8")) != NOTE_SEGMENT_SHA256:
        raise SystemExit("STOP: p.124 note segment changed")
    if not body_text.startswith("[Page 124]\n"):
        raise SystemExit("STOP: p.124 body boundary changed")

    raw = {name: path.read_bytes() for name, path in TABLES.items()}
    for name, expected in EXPECTED_TABLE_SHA256.items():
        if digest(raw[name]) != expected:
            raise SystemExit(f"STOP: {name} table changed since p.123 review")

    statement_text = raw["statements"].decode("utf-8-sig")
    statement_bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    statement_rows = [json.loads(line) for line in statement_text.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in statement_rows}
    if len(by_id) != len(statement_rows):
        raise SystemExit("STOP: duplicate statement_id before p.124 update")
    revision_ids = {spec["statement_id"] for spec in REVISIONS}
    if len(revision_ids) != len(REVISIONS) or revision_ids - set(by_id):
        raise SystemExit("STOP: p.124 revision IDs are missing or duplicated")
    for statement_id in revision_ids:
        q = by_id[statement_id].get("qualifiers", {})
        if q.get("relation_candidate") not in (None, ""):
            raise SystemExit(f"STOP: p.124 target already classified: {statement_id}")

    candidate_raw, candidate_bom, candidate_text, candidate_headers, candidates = read_csv(TABLES["candidates"])
    mention_raw, mention_bom, mention_text, mention_headers, mentions = read_csv(TABLES["mentions"])
    coverage_raw, coverage_bom, coverage_text, coverage_headers, coverage = read_csv(TABLES["coverage"])
    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    planned_candidate_ids = {row["candidate_id"] for row in CANDIDATES}
    if candidate_ids & planned_candidate_ids:
        raise SystemExit("STOP: a planned p.124 candidate ID already exists")
    if not {"cand-11403", "cand-11480", "cand-0125"}.issubset(candidate_ids):
        raise SystemExit("STOP: an expected existing p.124 endpoint is missing")

    new_specs = [prepare_spec(spec) for spec in NEW]
    revised_specs = [prepare_spec(spec) for spec in REVISIONS]
    new_ids = {spec["statement_id"] for spec in new_specs}
    if len(new_ids) != len(new_specs) or new_ids & set(by_id):
        raise SystemExit("STOP: planned p.124 statement IDs are duplicated or already present")
    candidate_universe = candidate_ids | planned_candidate_ids
    built_rows = [build_row(spec, body_text, note_text) for spec in revised_specs + new_specs]
    for row in built_rows:
        q = row["qualifiers"]
        if q["relation_candidate"] is True:
            endpoints = {row.get("subject_candidate_id"), row.get("object_candidate_id")}
            if None in endpoints or not endpoints.issubset(candidate_universe):
                raise SystemExit(f"STOP: relation endpoint missing/unknown: {row['statement_id']}")
            if not endpoints.issubset(set(q["mentioned_candidate_ids"])):
                raise SystemExit(f"STOP: relation endpoint absent from mention list: {row['statement_id']}")
    rows_by_id = {row["statement_id"]: row for row in built_rows}
    if len(rows_by_id) != len(built_rows):
        raise SystemExit("STOP: duplicate built p.124 statements")

    planned_mentions = [
        mention_row(body_text if item[4] == BODY_SEGMENT_ID else note_text, item)
        for item in NEW_MENTIONS
    ]
    planned_mention_ids = {row["mention_id"] for row in planned_mentions}
    if len(planned_mention_ids) != len(planned_mentions) or planned_mention_ids & mention_ids:
        raise SystemExit("STOP: a planned p.124 mention ID is duplicated or already present")
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if "m-chp5-p124-0027" not in mention_by_id:
        raise SystemExit("STOP: Scaramuccia person mention is missing")
    mention_by_id["m-chp5-p124-0027"]["candidate_id"] = "cand-2390"
    mention_by_id["m-chp5-p124-0027"]["note"] = "Person mention maps to cand-2390; print cand-6018 and index work candidate cand-2391 remain distinct pending S3 alignment."

    for row in CANDIDATES:
        for field in candidate_headers:
            row.setdefault(field, "")
    candidate_ids |= planned_candidate_ids

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    coverage_notes = {
        BODY_SEGMENT_ID: "已核对印刷p.124正文L36–49；页内只有Simonelli姓名后的注1。p.124注1续文位于本段L43–49，不能拆作注2–6；p.125 L52续完本段L42句子。",
        NOTES_SEGMENT_ID: "已读并迁移L126–147。p.124唯一印刷注1起于L142，续文在正文源段L43–49；续文包含Passeri、Scaramuccia、Testa、Chigi档案与Castiglione资料，均归注1。",
    }
    for segment_id, note in coverage_notes.items():
        if segment_id not in coverage_by_id:
            raise SystemExit(f"STOP: missing p.124 coverage row: {segment_id}")
        coverage_by_id[segment_id]["note"] = note

    statement_newline = "\r\n" if "\r\n" in statement_text else "\n"
    out_lines = []
    for raw_line in statement_text.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        ending = raw_line[len(line):]
        if not line.strip():
            out_lines.append(raw_line)
            continue
        row = json.loads(line)
        if row["statement_id"] in revision_ids:
            old_q = row.setdefault("qualifiers", {})
            for key in ("footnote_numbers", "footnote_links", "footnote_link_status", "footnote_marker", "footnote_target_line", "footnote_segment", "linked_body_statement_ids"):
                old_q.pop(key, None)
            row.clear()
            row.update(rows_by_id[json.loads(line)["statement_id"]])
            line = json.dumps(row, ensure_ascii=False)
            ending = ending or statement_newline
        out_lines.append(line + ending)
    if out_lines and not out_lines[-1].endswith(("\n", "\r")):
        out_lines[-1] += statement_newline
    out_lines.extend(json.dumps(rows_by_id[sid], ensure_ascii=False) + statement_newline for sid in [spec["statement_id"] for spec in new_specs])
    statement_bytes = (b"\xef\xbb\xbf" if statement_bom else b"") + "".join(out_lines).encode("utf-8")
    candidate_bytes = emit_csv(candidate_headers, candidates + CANDIDATES, candidate_bom, candidate_text)
    mention_bytes = emit_csv(mention_headers, mentions + planned_mentions, mention_bom, mention_text)
    coverage_bytes = emit_csv(coverage_headers, coverage, coverage_bom, coverage_text)
    outputs = {"statements": statement_bytes, "candidates": candidate_bytes, "mentions": mention_bytes, "coverage": coverage_bytes}

    relation_count = sum(1 for row in built_rows if row["qualifiers"]["relation_candidate"] is True)
    scalar_count = len(built_rows) - relation_count
    print("p.124 canonical source, chapter PDF physical page 5, page image, body/note segment hashes, and four table hashes verified")
    print(f"existing statements revised: {len(REVISIONS)}")
    print(f"new atomic statements: {len(new_specs)} ({sum(row['qualifiers']['relation_candidate'] is True for row in [rows_by_id[sid] for sid in new_ids])} relation candidates; {len(new_specs) - sum(rows_by_id[sid]['qualifiers']['relation_candidate'] is True for sid in new_ids)} non-relational claims)")
    print(f"new open group candidates: {len(CANDIDATES)}; new mentions: {len(planned_mentions)}; corrected person mention: m-chp5-p124-0027")
    print("printed footnote audit: one note 1 at L142, continued at L43-L49; no p.124 notes 2-6")
    print(f"all revised/new statements classified: {len(built_rows)}; relation candidates={relation_count}; non-relational claims={scalar_count}")
    print("planned table outputs:")
    for name, data in outputs.items():
        print(f"  {name}: {len(raw[name])} -> {len(data)} bytes; sha256={digest(data)}")
    if not args.apply:
        print("dry-run only; no table files written")
        return 0

    paths = {name: TABLES[name] for name in outputs}
    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in paths.items()}
    for backup in backups.values():
        if backup.exists():
            raise SystemExit(f"STOP: recovery copy already exists: {backup.name}")
    for name, backup in backups.items():
        shutil.copy2(paths[name], backup)
    written = []
    try:
        for name, data in outputs.items():
            path = paths[name]
            temp = path.with_name(path.name + ".tmp-s2-chp5-p124")
            temp.write_bytes(data)
            temp.replace(path)
            written.append(name)
    except Exception:
        for name in written:
            shutil.copy2(backups[name], paths[name])
        raise
    for name, path in paths.items():
        print(f"written {name}: sha256={digest(path.read_bytes())}; recovery copy={backups[name].name}")
    print("p.124 tables written successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
