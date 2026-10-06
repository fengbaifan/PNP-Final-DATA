"""S2 migration of the deferred p.193-199 footnotes, in source order.

The source OCR is retained as the quote anchor. Print-scan corrections and
links back to the page statements are recorded as structured qualifiers.
Run without --apply for preflight.
"""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[3]
base = root / "04-knowledge" / "tables"
source_rel = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
source_path = root / source_rel
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_id = "chp-7:07_CHP-7_sec_iv:l97-119"
segment_start, segment_end = 97, 119
segment_text = "\n".join(source_lines[segment_start - 1 : segment_end])

new_candidates = [
    {"candidate_id": "cand-7250", "canonical_name": "Niels von Holst, ‘La pittura veneziana tra il Reno e la Neva’ (1951)", "suggested_type": "archive", "detail": "The book bibliography identifies the 1951 article in Arte Veneta, pages 131-140; p.193 note 1 cites p.132 only. Article not independently read.", "candidate_source_ref": f"{segment_id}#L98"},
    {"candidate_id": "cand-7251", "canonical_name": "E. Lavagnino, Gli artisti italiani in Germania, vol. III (1943)", "suggested_type": "archive", "detail": "The book bibliography identifies volume III, I pittori e gl’incisori, Rome 1943; p.193 note 3 and p.194 note 1 cite pages only. Work not independently read.", "candidate_source_ref": f"{segment_id}#L99"},
    {"candidate_id": "cand-7252", "canonical_name": "P. Heilbronner, ‘Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera’ (1936)", "suggested_type": "archive", "detail": "The book bibliography identifies the article in Le Vie d’Italia e del Mondo, 1936, pages 887-904; cited pages not independently read.", "candidate_source_ref": f"{segment_id}#L99"},
    {"candidate_id": "cand-7253", "canonical_name": "Max H. von Freeden, Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn, I. Teil, zweiter Halbband (1955)", "suggested_type": "archive", "detail": "Publication title and edition follow the book bibliography; p.194 note 3 cites it without page numbers. Work not independently read.", "candidate_source_ref": f"{segment_id}#L101"},
    {"candidate_id": "cand-7254", "canonical_name": "R. L. Brett, The Third Earl of Shaftesbury (1951)", "suggested_type": "archive", "detail": "The book bibliography identifies the London 1951 publication; p.198 note 3 cites page 38. Work not independently read.", "candidate_source_ref": f"{segment_id}#L115"},
    {"candidate_id": "cand-7255", "canonical_name": "George Vertue, Notebooks (six volumes, Walpole Society, 1930–1955)", "suggested_type": "archive", "detail": "The book bibliography lists Vertue’s Notebooks; notes cite volume I, page 114, and volume II, page 132. Cited pages not independently read.", "candidate_source_ref": f"{segment_id}#L109"},
    {"candidate_id": "cand-7256", "canonical_name": "Italian Art and Britain (publication cited at pp. 19–20; full details unspecified)", "suggested_type": "archive", "detail": "Named in p.197 note 2 without full publication details in the note or book bibliography; title is retained without expansion. Cited pages not independently read.", "candidate_source_ref": f"{segment_id}#L109"},
    {"candidate_id": "cand-7257", "canonical_name": "Gerald Burden, ‘Sir Thomas Isham, an English collector in Rome in 1677–8’ (1960)", "suggested_type": "archive", "detail": "The book bibliography supplies the article title and pages 1-25; its date is OCRed there as ‘i960’ and is read as 1960 against p.197 note 4. Article not independently read.", "candidate_source_ref": f"{segment_id}#L110"},
    {"candidate_id": "cand-7258", "canonical_name": "Lamport Hall", "suggested_type": "place", "detail": "Named in p.197 note 4 as the location of Sir Thomas Isham’s pictures; no individual picture is identified by this note.", "candidate_source_ref": f"{segment_id}#L110"},
    {"candidate_id": "cand-7259", "canonical_name": "E. K. Waterhouse, ‘A note on British collecting of Italian pictures in the later seventeenth century’ (1960)", "suggested_type": "archive", "detail": "The book bibliography identifies the article in Burlington Magazine, 1960, pages 54-58; p.197 note 5 cites page 57. Article not independently read.", "candidate_source_ref": f"{segment_id}#L111"},
    {"candidate_id": "cand-7260", "canonical_name": "H. Honour, ‘English patrons and Italian sculptors in the first half of the eighteenth century’ (1958)", "suggested_type": "archive", "detail": "The book bibliography identifies the Connoisseur article, vol. 141, 1958, pages 220-226; p.197 note 6 cites page 220 ff. Article not independently read.", "candidate_source_ref": f"{segment_id}#L112"},
    {"candidate_id": "cand-7261", "canonical_name": "J. Agnelli, Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara (1734)", "suggested_type": "archive", "detail": "The book bibliography identifies the Ferrara 1734 publication; p.197 note 1 says it is printed after the book’s imprimatur. Its contents were not independently read.", "candidate_source_ref": f"{segment_id}#L108"},
    {"candidate_id": "cand-7262", "canonical_name": "Raccolta di Memorie di Benedetto Gennari, MS B.344", "suggested_type": "archive", "detail": "P.196 note 1 names this manuscript and gives Archiginnasio, Bologna, as the holding institution; it notes a photocopy at the Warburg Institute. The manuscript was not independently consulted.", "candidate_source_ref": f"{segment_id}#L107"},
    {"candidate_id": "cand-7263", "canonical_name": "Archiginnasio, Bologna", "suggested_type": "institution", "detail": "Named in p.196 note 1 as the repository of MS B.344; repository identity is recorded as stated in Haskell’s note.", "candidate_source_ref": f"{segment_id}#L107"},
    {"candidate_id": "cand-7264", "canonical_name": "Wind, 1938 publication cited at pages 185–188 (title unspecified)", "suggested_type": "archive", "detail": "The note gives author surname, year and pages but does not name the work; no title or edition is inferred.", "candidate_source_ref": f"{segment_id}#L117"},
    {"candidate_id": "cand-7265", "canonical_name": "Benedetto Croce, ‘Shaftesbury in Italia’ (1927)", "suggested_type": "archive", "detail": "The book bibliography identifies the reprint in Uomini e cose della vecchia Italia, 1927, pages 272-309; cited pages not independently read.", "candidate_source_ref": f"{segment_id}#L118"},
    {"candidate_id": "cand-7266", "canonical_name": "Shaftesbury, cited work at pages 30–61 (title and edition unspecified)", "suggested_type": "archive", "detail": "P.198 note 6 gives only the author name and pages; the publication is not expanded or conflated with Brett’s biography.", "candidate_source_ref": f"{segment_id}#L118"},
    {"candidate_id": "cand-7267", "canonical_name": "W. Wells, ‘Shaftesbury and Paolo de Matteis’ (1950)", "suggested_type": "archive", "detail": "The book bibliography identifies the Leeds Art Quarterly article, Spring 1950, pages 23-28; cited pages not independently read.", "candidate_source_ref": f"{segment_id}#L118"},
    {"candidate_id": "cand-7268", "canonical_name": "J. E. Sweetman, ‘Shaftesbury’s last commission’ (1956)", "suggested_type": "archive", "detail": "The book bibliography identifies the Journal of the Warburg and Courtauld Institutes article, 1956, pages 110-116; p.199 note 1 cites these pages. Article not independently read.", "candidate_source_ref": f"{segment_id}#L119"},
    {"candidate_id": "cand-7269", "canonical_name": "Portrait of Thomas Killigrew by Giovanni Angelo Canini (1651)", "suggested_type": "work", "detail": "P.197 note 2 attributes the portrait to Canini and dates it to 1651, citing Vertue, vol. I, p.114; neither title nor location is specified. Attribution is recorded as Haskell’s citation, not independently verified.", "candidate_source_ref": f"{segment_id}#L109"},
    {"candidate_id": "cand-7270", "canonical_name": "James Altham as a hermit, by Salvator Rosa (1665)", "suggested_type": "work", "detail": "P.197 note 2 gives the subject, artist and date and says it was in the Bankes Collection; no title or present location is independently established.", "candidate_source_ref": f"{segment_id}#L109"},
    {"candidate_id": "cand-7271", "canonical_name": "Bankes Collection (as named for the James Altham portrait)", "suggested_type": "", "detail": "The p.197 note names this collection in parentheses; it is not normalized to a repository or a specific Bankes household.", "candidate_source_ref": f"{segment_id}#L109"},
]

# surface, candidate, note, line filter, optional occurrence indexes
mention_specs = [
    ("von Holst", "cand-7250", "Surname in p.193 note 1; publication identity follows the book bibliography.", [98]),
    ("Lavagnino", "cand-7251", "Cited at p.193 note 3 and p.194 note 1.", [99, 100]),
    ("Heilbronner", "cand-7252", "Article identified from the book bibliography; cited pages not read.", [99]),
    ("Hantsch und Schers", "cand-6576", "OCR has Schers; print reads Scherf. Reuse the 1931 source candidate.", [101]),
    ("von Freeden", "cand-7253", "The cited 1955 source is distinguished from Hantsch and Scherf’s 1931 volume.", [101]),
    ("Wilhelm", "cand-7185", "Reuse the F. Wilhelm article candidate cited on p.194.", [102]),
    ("ibid.", "cand-7185", "Contextually refers to the immediately preceding p.194 note 4 citation to Wilhelm; retain this resolution as a contextual reference.", [103]),
    ("Hantsch und Schers", "cand-6576", "OCR has Schers; print reads Scherf.", [104]),
    ("Da Canal", "cand-6593", "Reuse the publication candidate for Vita di Gregorio Lazzarini.", [105]),
    ("Zanotti", "cand-7115", "Reuse Storia dell’Accademia Clementina.", [106, 107, 114]),
    ("Whinney and Millar", "cand-7066", "Reuse English Art, 1625–1714.", [106, 107]),
    ("Raccolta di Memorie di Benedetto Gennari", "cand-7262", "Manuscript named as an additional source in p.196 note 1.", [107]),
    ("Archiginnasio, Bologna", "cand-7263", "Repository named for MS B.344; not independently checked.", [107]),
    ("Warburg Institute", "cand-5950", "Named as holding a photocopy of the manuscript.", [107]),
    ("Agnelli", "cand-7261", "Reference to the 1734 publication identified from the book bibliography.", [108]),
    ("Soprani/Ratti", "cand-5160", "Reuse the two-volume Soprani/Ratti edition cited for Cassana.", [108]),
    ("Killigrew by Canini in 1651", "cand-7269", "Portrait attribution and date as stated in Haskell’s footnote.", [109]),
    ("Killigrew", "cand-1342", "Thomas Killigrew; person candidate reused from the p.197 body.", [109]),
    ("Canini", "cand-0530", "Giovanni Angelo Canini candidate reused from the index.", [109]),
    ("Vertue", "cand-7255", "Vertue Notebooks, volume I, page 114.", [109]),
    ("James Altham as a hermit by Salvator Rosa in 1665", "cand-7270", "Portrait attribution and date as stated in Haskell’s footnote.", [109]),
    ("James Altham", "cand-0085", "Person candidate reused from the p.197 body.", [109]),
    ("Salvator Rosa", "cand-2236", "Reuse an index-seeded person candidate; identity remains for S3.", [109]),
    ("Bankes Collection", "cand-7271", "Collection label is kept unresolved; it is not assigned to a named estate.", [109]),
    ("Italian Art and Britain", "cand-7256", "Publication title as cited; full details remain unresolved.", [109]),
    ("ibid.", "cand-7256", "Contextually points to Italian Art and Britain, p. 19, after its citation at p. 20.", [109]),
    ("Sir Thomas Baines by Carlo Dolci between 1665 and 1670", "cand-4024", "Reuse the plate-list work candidate; attribution and date are supplied by the p.197 note.", [109]),
    ("Sir Thomas Baines", "cand-0162", "Person candidate reused from the p.197 body.", [109]),
    ("Carlo Dolci", "cand-0923", "Artist candidate reused from the p.197 body.", [109]),
    ("Fitzwilliam Museum, Cambridge", "cand-4893", "Museum named as the location of the Baines portrait.", [109]),
    ("Baldinucci", "cand-4846", "Reuse the volume VI (1728) source candidate.", [109, 114]),
    ("Burden", "cand-7257", "Article identified from the book bibliography; the bibliography OCR year is corrected to 1960.", [110]),
    ("Lamport Hall", "cand-7258", "Named as the place where the Isham pictures are held.", [110]),
    ("Northants", "cand-7236", "Printed abbreviation for Northamptonshire; reuse the unresolved place candidate from p.197.", [110]),
    ("Waterhouse", "cand-7259", "Article identified from the bibliography; cited page 57.", [111]),
    ("Bellori", "cand-4831", "Reuse Le Vite inedite (1942), cited p.98.", [111]),
    ("Burghley", "cand-7237", "Reuse Burghley, Lord Exeter’s country house, from p.198.", [111]),
    ("Pascoli", "cand-4552", "Reuse volume II of Vite de’ Pittori, Scultori ed Architetti moderni.", [112]),
    ("Honour", "cand-7260", "Article identified from the book bibliography; cited pages not read.", [112]),
    ("Vertue", "cand-7255", "Vertue Notebooks, volume II, page 132.", [113]),
    ("Pascoli", "cand-4834", "Reuse volume I of Pascoli’s Vite.", [114]),
    ("de Dominici", "cand-4835", "Reuse volume IV of Vite dei pittori scultori ed architetti napoletani.", [114, 118]),
    ("Brett", "cand-7254", "Biography identified from the book bibliography; cited page 38.", [115]),
    ("Wind", "cand-7230", "Reuse E. Wind’s 1939–40 Hampton Court article, cited at pp.134–135.", [116]),
    ("Wind", "cand-7264", "Only author surname, year and pages are supplied; title remains unspecified.", [117]),
    ("Croce", "cand-7265", "‘Shaftesbury in Italia’, as identified in the book bibliography.", [118]),
    ("Shaftesbury", "cand-7266", "Cited work at pp.30–61; title and edition are not specified here.", [118]),
    ("Wells", "cand-7267", "‘Shaftesbury and Paolo de Matteis’, as identified in the book bibliography.", [118]),
    ("Sweetman", "cand-7268", "‘Shaftesbury’s last commission’, as identified in the book bibliography.", [119]),
]

statements = []

def add_note(sid, subj, obj, lo, hi, quote, claim, mentioned, marker, linked, *, predicate="footnote_citation", qualification=None, extra=None, speaker="book footnote", text_layer="authorial footnote citation"):
    page = 193 if lo <= 99 else 194 if lo <= 102 else 195 if lo <= 106 else 196 if lo == 107 else 197 if lo <= 112 else 198 if lo <= 118 else 199
    physical = page - 162
    q = {
        "source_line_start": lo,
        "source_line_end": hi,
        "printed_page": page,
        "pdf_physical_page": physical,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification or "Citation locator and any accompanying claim are recorded as printed; cited pages or works were not independently read.",
        "footnote_marker": marker,
        "linked_body_statement_ids": linked,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        q.update(extra)
    statements.append({
        "statement_id": sid,
        "segment_id": segment_id,
        "subject_candidate_id": subj,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": source_rel,
    })

add_note("st-chp7-p193-n1-von-holst", "cand-1399", "cand-7250", 98, 98, "1 von Holst, p. 132.", "P.193 note 1 cites von Holst, page 132, alongside Haskell’s account of Leopold Wilhelm’s patronage.", ["cand-1399", "cand-7250"], 1, ["st-chp7-p193-leopold-patronizes-vecchia"], extra={"page": "132"})
add_note("st-chp7-p193-n3-lavagnino-heilbronner", "cand-7154", None, 99, 99, "3 Lavagnino, p. 69, and Heilbronner, pp. 887-904.", "P.193 note 3 cites Lavagnino and Heilbronner in connection with the Wittelsbach account.", ["cand-7154", "cand-7251", "cand-7252"], 3, ["st-chp7-p193-wittelsbach-alliance"], extra={"page": "Lavagnino p. 69; Heilbronner pp. 887-904"})
add_note("st-chp7-p194-n1-lavagnino", "cand-7154", "cand-7251", 100, 100, "1 Lavagnino, p. 66.", "P.194 note 1 cites Lavagnino, page 66, for the Cadani account.", ["cand-7154", "cand-7251"], 1, ["st-chp7-p194-cadani-employed-dresden"], extra={"page": "66"})
add_note("st-chp7-p194-n3-hantsch-freeden", "cand-2400", None, 101, 101, "8 Hantsch und Schers and von Freeden, 1955.", "P.194 note 3 cites Hantsch and Scherf and Max H. von Freeden’s 1955 source in connection with the Schönborn patronage account.", ["cand-2400", "cand-6576", "cand-7253"], 3, ["st-chp7-p194-schoenborn-commission-group"], extra={"ocr_corrections": [{"source_line": 101, "ocr": "8 Hantsch und Schers", "reading": "3 Hantsch und Scherf", "basis": "PDF physical page 32."}], "source_citation": "Hantsch und Scherf; von Freeden (1955)"})
add_note("st-chp7-p194-n4-wilhelm", "cand-1405", "cand-7185", 102, 102, "4 Wilhelm, p. 136.", "P.194 note 4 cites F. Wilhelm, page 136, alongside the Prince of Liechtenstein’s subject instructions.", ["cand-1405", "cand-7184", "cand-7185"], 4, ["st-chp7-p194-liechtenstein-letter-subject-discretion"], extra={"page": "136", "author_candidate_id": "cand-7184"})
add_note("st-chp7-p195-n1-prince-taste-comment", "cand-1405", "cand-7185", 103, 103, "1 ibid., pp. 89 and 92. ‘Mondane’ seems a curious way to describe some of these subjects, but it gives us an indication of what the Prince was looking for even in. sacred pictures.", "Haskell comments that ‘Mondane’ is a curious description but indicates what the Prince wanted even in sacred pictures.", ["cand-1405", "cand-7185"], 1, ["st-chp7-p195-liechtenstein-gallery-worldly"], predicate="interpreted_worldly_term_as_princely_taste", qualification="‘Ibid.’ is resolved contextually to the immediately preceding p.194 note 4 citation to Wilhelm; this does not independently verify the cited pages. The sentence is Haskell’s interpretation, not a fact about every picture.", extra={"page": "89, 92", "author_candidate_id": "cand-7184", "ocr_corrections": [{"source_line": 103, "ocr": "in. sacred pictures", "reading": "in sacred pictures", "basis": "PDF physical page 33."}]}, speaker="Haskell", text_layer="authorial comment in footnote")
add_note("st-chp7-p195-n2-schoenborn-letter", "cand-2399", "cand-6576", 104, 104, "2 Letter of 10 October 1708—Hantsch und Schers, p. 164.", "P.195 note 2 cites the letter of 10 October 1708 in Hantsch and Scherf, page 164, for the von Schönborn quotation.", ["cand-2399", "cand-6576"], 2, ["st-chp7-p195-lothar-schonborn-letter"], extra={"page": "164", "ocr_corrections": [{"source_line": 104, "ocr": "Schers", "reading": "Scherf", "basis": "PDF physical page 33."}]})
add_note("st-chp7-p195-n3-da-canal", "cand-1368", "cand-6593", 105, 105, "3 Da Canal, especially pp. 71-3.", "P.195 note 3 cites Da Canal, especially pages 71–73, alongside Haskell’s account of Gregorio Lazzarini.", ["cand-1368", "cand-6593"], 3, ["st-chp7-p195-lazzarini-testimony", "st-chp7-p195-lazzarini-output-germany"], extra={"page": "71-73"})
add_note("st-chp7-p195-n4-zanotti", "cand-0748", "cand-7115", 106, 106, "4 Zanotti, I, p. 154.", "P.195 note 4 cites Zanotti, volume I, page 154, for the Cignani testimony.", ["cand-0748", "cand-7115"], 4, ["st-chp7-p195-cignani-testimony"], extra={"page": "vol. I, p. 154"})
add_note("st-chp7-p195-n5-whinney-millar", "cand-2759", "cand-7066", 106, 106, "5 Whinney and Millar, pp. 296-302.", "P.195 note 5 cites Whinney and Millar, pages 296–302, for Haskell’s account of Verrio’s English career.", ["cand-2759", "cand-7066"], 5, ["st-chp7-p195-verrio-employed-by-charlesii", "st-chp7-p195-arlington-introduced-verrio"], extra={"page": "296-302"})
add_note("st-chp7-p196-n1-gennari-evidence", "cand-1127", "cand-7262", 107, 107, "1 Whinney and Millar, p. 182, and Zanotti, I, pp. 170-1. See also Raccolta di Memorie di Benedetto Gennari—MS. B.344 in Archiginnasio, Bologna (photocopy in Warburg Institute).", "P.196 note 1 cites Whinney and Millar and Zanotti, and names a Gennari manuscript, MS B.344 at the Archiginnasio in Bologna, with a photocopy at the Warburg Institute.", ["cand-1127", "cand-7066", "cand-7115", "cand-7262", "cand-7263", "cand-3398", "cand-5950"], 1, ["st-chp7-p196-gennari_salary_and_commissions"], extra={"page": "Whinney and Millar p. 182; Zanotti vol. I pp. 170-171; MS B.344", "repository_candidate_id": "cand-7263", "photocopy_holder_candidate_id": "cand-5950"}, qualification="Citation locator and manuscript repository as stated in Haskell’s note; the manuscript, photocopy and cited pages were not independently consulted.")
add_note("st-chp7-p197-n1-cassana-date-conflict", "cand-0593", "cand-5160", 108, 108, "1 Agnelli, printed at end ofbook after imprimatur. Ratti (Soprani/Ratti, II, p. 15) says that he died in 1713 after refusing an official post as the Queen’s Painter. It is not known just when he came to England or whether he died in this country.", "The footnote cites Agnelli and reports that Ratti says Cassana died in 1713 after refusing an official post as the Queen’s Painter; it also says his arrival date and place of death are unknown.", ["cand-0593", "cand-7261", "cand-5160"], 1, ["st-chp7-p197-queen-anne-employs-cassana"], predicate="footnote_reports_conflicting_death_date_and_unknown_itinerary", qualification="The body gives 1714 while Ratti is reported here as giving 1713. Preserve both source claims without choosing a date. The citation pages were not independently read.", extra={"page": "Soprani/Ratti vol. II, p. 15", "author_candidate_id": "cand-5160", "ocr_corrections": [{"source_line": 108, "ocr": "ofbook", "reading": "of book", "basis": "PDF physical page 35."}]}, speaker="Haskell", text_layer="authorial footnote")
add_note("st-chp7-p197-n2-portrait-attributions", "cand-0162", "cand-4024", 109, 109, "2 Killigrew by Canini in 1651—Vertue, I, p. 114; James Altham as a hermit by Salvator Rosa in 1665 (Bankes Collection)—Italian Art and Britain, p. 20; Sir Thomas Baines by Carlo Dolci between 1665 and 1670 (Fitzwilliam Museum, Cambridge)—ibid., p. 19.", "P.197 note 2 attributes a 1651 portrait of Killigrew to Canini, a 1665 hermit portrait of James Altham to Salvator Rosa (then in the Bankes Collection), and a portrait of Baines to Carlo Dolci between 1665 and 1670, at the Fitzwilliam Museum, Cambridge.", ["cand-1342", "cand-0530", "cand-7269", "cand-0085", "cand-2236", "cand-7270", "cand-7271", "cand-7255", "cand-7256", "cand-0162", "cand-0923", "cand-4024", "cand-4893"], 2, ["st-chp7-p197-tourist-portrait-examples"], predicate="footnote_identifies_portrait_attributions_dates_and_locations", qualification="These are Haskell’s footnote attributions and dates; the cited pages and the collection/museum records were not independently checked. No one-to-one mapping is inferred between the three visitors and body Plate references 30a, 30b and 31a.", extra={"citations": [{"source_candidate_id": "cand-7255", "page": "vol. I, p. 114"}, {"source_candidate_id": "cand-7256", "page": "pp. 19-20"}], "ocr_corrections": [{"source_line": 109, "ocr": "Sir Thomas Baines by Carlo Dolci between 1665 and 1670", "reading": "Sir Thomas Baines by Carlo Dolci between 1665 and 1670", "basis": "PDF physical page 35 confirms the attribution and date."}]}, speaker="Haskell", text_layer="authorial footnote")
add_note("st-chp7-p197-n3-baldinucci", "cand-1037", "cand-4846", 109, 109, "3 Baldinucci, VI, 1728, p. 503.", "P.197 note 3 cites Baldinucci, volume VI (1728), page 503, for the Finch and Dolci account.", ["cand-1037", "cand-0923", "cand-4846"], 3, ["st-chp7-p197-finch-commissioned-dolci"], extra={"page": "vol. VI (1728), p. 503"})
add_note("st-chp7-p197-n4-isham-pictures-lamport", "cand-1315", "cand-7258", 110, 110, "4 Burden, pp. 1-25. The pictures are all at Lamport Hall, Northants.", "P.197 note 4 cites Burden, pages 1–25, and says the pictures discussed for Isham are all at Lamport Hall, Northamptonshire.", ["cand-1315", "cand-7257", "cand-7258", "cand-7236"], 4, ["st-chp7-p197-isham-acquired-paintings-with-advice", "st-chp7-p197-isham-commissions-in-rome", "st-chp7-p197-isham-mythological-pictures", "st-chp7-p197-isham-portrait-maratta"], predicate="reports_isham_pictures_all_at_lamport_hall", qualification="This is the footnote’s statement about the pictured group; individual works and current object records are not identified or independently checked.", extra={"page": "1-25"}, speaker="Haskell", text_layer="authorial footnote")
add_note("st-chp7-p197-n5-exeter-pictures-burghley", "cand-0984", "cand-7237", 111, 111, "5 Waterhouse, i960, p. 57; Bellori, 1942, p. 98. The pictures are mostly still at Burghley.", "P.197 note 5 cites Waterhouse and Bellori and says the pictures associated with Exeter are mostly still at Burghley.", ["cand-0984", "cand-7259", "cand-4831", "cand-7237"], 5, ["st-chp7-p197-exeter-ordered-nine-dolci", "st-chp7-p197-exeter-ordered-fifteen-giordano", "st-chp7-p197-exeter-collected-maratta-rome"], predicate="reports_exeter_pictures_mostly_at_burghley", qualification="The note says ‘mostly’; it does not identify each picture or establish a current inventory. The sources were not independently read.", extra={"citations": [{"source_candidate_id": "cand-7259", "page": "57"}, {"source_candidate_id": "cand-4831", "page": "98"}], "ocr_corrections": [{"source_line": 111, "ocr": "i960", "reading": "1960", "basis": "PDF physical page 35."}]}, speaker="Haskell", text_layer="authorial footnote")
add_note("st-chp7-p197-n6-monnot-tomb-citations", "cand-0984", "cand-7260", 112, 112, "6 Pascoli, II, p. 491; Honour, pp. 220 ff.", "P.197 note 6 cites Pascoli, volume II, page 491, and Honour, pages 220 ff., for the Monnot tomb account.", ["cand-0984", "cand-1686", "cand-4552", "cand-7260"], 6, ["st-chp7-p197-monnot-tomb"], extra={"citations": [{"source_candidate_id": "cand-4552", "page": "vol. II, p. 491"}, {"source_candidate_id": "cand-7260", "page": "220 ff."}]})
add_note("st-chp7-p198-n1-vertue", "cand-0984", "cand-7255", 113, 113, "1 Vertue, II, p. 132.", "P.198 note 1 cites Vertue, volume II, page 132, alongside the Exeter and Verrio account.", ["cand-0984", "cand-2759", "cand-7255"], 1, ["st-chp7-p198-exeter-employs-verrio-burghley"], extra={"page": "vol. II, p. 132"})
add_note("st-chp7-p198-n2-biographical-citations", "cand-0984", None, 114, 114, "2 See, for instance, Pascoli, l, pp. 140,215,226; Baldinucci, VI, 1728, p. 503; de Dominici, IV, p. 292.", "P.198 note 2 cites Pascoli, Baldinucci and de Dominici as examples connected with Exeter’s collecting and the Italian biographical accounts.", ["cand-0984", "cand-4834", "cand-4846", "cand-4835"], 2, ["st-chp7-p198-exeter-introduced-maratta", "st-chp7-p198-english-tourist-collecting"], extra={"citations": [{"source_candidate_id": "cand-4834", "page": "vol. I, pp. 140, 215, 226"}, {"source_candidate_id": "cand-4846", "page": "vol. VI (1728), p. 503"}, {"source_candidate_id": "cand-4835", "page": "vol. IV, p. 292"}], "ocr_corrections": [{"source_line": 114, "ocr": "Pascoli, l", "reading": "Pascoli, I", "basis": "PDF physical page 36."}]})
add_note("st-chp7-p198-n3-brett", "cand-2426", "cand-7254", 115, 115, "8 Brett, p. 38.", "P.198 note 3 cites Brett, page 38, alongside Haskell’s account of Shaftesbury’s Italian visit.", ["cand-2426", "cand-7254"], 3, ["st-chp7-p198-shaftesbury-italy-visit"], extra={"page": "38", "ocr_corrections": [{"source_line": 115, "ocr": "8 Brett", "reading": "3 Brett", "basis": "PDF physical page 36."}]})
add_note("st-chp7-p198-n4-wind-1939", "cand-2426", "cand-7230", 116, 116, "4 Wind, 1939-40, pp. 134-5.", "P.198 note 4 cites E. Wind’s 1939–40 Hampton Court article, pages 134–135, alongside the proposed link between Shaftesbury and Verrio’s programme.", ["cand-2426", "cand-7230", "cand-7213"], 4, ["st-chp7-p198-shaftesbury-verrio-programme"], extra={"page": "134-135"})
add_note("st-chp7-p198-n5-wind-1938", "cand-2426", "cand-7264", 117, 117, "8 Wind, 1938, pp. 185-8.", "P.198 note 5 cites an unspecified Wind publication from 1938, pages 185–188, alongside Closterman and Shaftesbury’s instructions.", ["cand-2426", "cand-7264", "cand-0791"], 5, ["st-chp7-p198-closterman-instructions-advice"], extra={"page": "185-188", "ocr_corrections": [{"source_line": 117, "ocr": "8 Wind", "reading": "5 Wind", "basis": "PDF physical page 36."}]})
add_note("st-chp7-p198-n6-shaftesbury-citations", "cand-2426", "cand-7265", 118, 118, "8 Croce, 1927, pp. 272-309; Shaftesbury, pp. 30-61; Wells, pp. 23-8; and de Dominici, IV, p. 329.", "P.198 note 6 cites Croce, a Shaftesbury text, Wells and de Dominici alongside the account of Shaftesbury’s aesthetic ideas and practice.", ["cand-2426", "cand-7265", "cand-7266", "cand-7267", "cand-4835"], 6, ["st-chp7-p198-shaftesbury-buys-pictures-for-friends", "st-chp7-p198-shaftesbury-de-matteis-choice-hercules", "st-chp7-p198-shaftesbury-quoted-aesthetic-instruction"], extra={"citations": [{"source_candidate_id": "cand-7265", "page": "272-309"}, {"source_candidate_id": "cand-7266", "page": "30-61"}, {"source_candidate_id": "cand-7267", "page": "23-28"}, {"source_candidate_id": "cand-4835", "page": "vol. IV, p. 329"}], "ocr_corrections": [{"source_line": 118, "ocr": "8 Croce", "reading": "6 Croce", "basis": "PDF physical page 36."}]})
add_note("st-chp7-p199-n1-sweetman", "cand-2426", "cand-7268", 119, 119, "1 Sweetman, pp. no-16.", "P.199 note 1 cites Sweetman’s ‘Shaftesbury’s last commission’, pages 110–116, alongside the 1713 picture and order account.", ["cand-2426", "cand-7268", "cand-7246"], 1, ["st-chp7-p199-shaftesbury-1713-picture", "st-chp7-p199-picture-as-history-instructions", "st-chp7-p199-shaftesbury-died-before-order"], extra={"page": "110-116", "ocr_corrections": [{"source_line": 119, "ocr": "no-16", "reading": "110-116", "basis": "PDF physical page 37."}]})

candidate_path = base / "entity-candidates.csv"
mention_path = base / "mentions.csv"
statement_path = base / "book-statements.jsonl"
coverage_path = base / "s2-coverage.csv"

with candidate_path.open(encoding="utf-8-sig", newline="") as f:
    candidate_rows = list(csv.DictReader(f))
    candidate_fields = list(candidate_rows[0].keys())
existing_candidate_ids = {r["candidate_id"] for r in candidate_rows}
if any(c["candidate_id"] in existing_candidate_ids for c in new_candidates):
    raise SystemExit("new candidate id collision")
if [c["candidate_id"] for c in new_candidates] != [f"cand-{i}" for i in range(7250, 7272)]:
    raise SystemExit("unexpected candidate sequence")
for c in new_candidates:
    row = {field: "" for field in candidate_fields}
    row.update(c)
    row.update({"status": "open", "candidate_origin": "body-mention"})
    c.clear()
    c.update(row)
all_candidate_ids = existing_candidate_ids | {c["candidate_id"] for c in new_candidates}

with mention_path.open(encoding="utf-8-sig", newline="") as f:
    mention_rows = list(csv.DictReader(f))
    mention_fields = list(mention_rows[0].keys())
existing_mention_ids = {r["mention_id"] for r in mention_rows}
with statement_path.open(encoding="utf-8-sig") as f:
    statement_rows = [json.loads(x) for x in f if x.strip()]
existing_statement_ids = {s["statement_id"] for s in statement_rows}
if any(s["statement_id"] in existing_statement_ids for s in statements):
    raise SystemExit("statement id collision")
if any((s["subject_candidate_id"] and s["subject_candidate_id"] not in all_candidate_ids) or (s["object_candidate_id"] and s["object_candidate_id"] not in all_candidate_ids) for s in statements):
    raise SystemExit("statement endpoint FK missing")
if any(cid not in all_candidate_ids for s in statements for cid in s["qualifiers"]["mentioned_candidate_ids"]):
    raise SystemExit("statement mention FK missing")

found_mentions = {}
for spec in mention_specs:
    surface, cid, note, lines = spec
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate FK missing: {cid}")
    start = 0
    matches = []
    while True:
        pos = segment_text.find(surface, start)
        if pos < 0:
            break
        line = segment_start + segment_text[:pos].count("\n")
        if line in lines:
            matches.append((pos, pos + len(surface), line))
        start = pos + 1
    if not matches:
        raise SystemExit(f"unmatched mention {surface!r} on lines {lines}")
    for lo, hi, line in matches:
        key = (lo, hi, cid)
        row = found_mentions.get(key)
        if row:
            row["note"] = (row["note"] + "; " + note).strip("; ")
        else:
            found_mentions[key] = {"mention_id": "", "segment_id": segment_id, "candidate_id": cid, "surface_form": surface, "start_char": str(lo), "end_char": str(hi), "note": note}
new_mentions = sorted(found_mentions.values(), key=lambda r: (int(r["start_char"]), int(r["end_char"]), r["candidate_id"]))
for i, row in enumerate(new_mentions, 1):
    row["mention_id"] = f"m-chp7-footnotes-b{i:03d}"
    if row["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention id collision: {row['mention_id']}")
    if segment_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"bad mention offset: {row}")

for s in statements:
    q = s["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1 : q["source_line_end"]])
    if s["original_quote"] not in excerpt or s["segment_id"] != segment_id or s["source_file"] != source_rel or s["origin"] != "book":
        raise SystemExit(f"quote/source mismatch: {s['statement_id']}")

by_id = {s["statement_id"]: s for s in statement_rows}
updates = {
    "st-chp7-p197-queen-anne-employs-cassana": {"qualification": "The body gives Haskell’s 1714 date, while p.197 note 1 reports that Ratti gives 1713 and leaves Cassana’s arrival date and place of death unknown. Keep the conflict unresolved.", "footnote_marker": 1, "linked_footnote_statement_ids": ["st-chp7-p197-n1-cassana-date-conflict"]},
    "st-chp7-p197-tourist-portrait-examples": {"qualification": "The body does not map each named visitor to a city or one plate. P.197 note 2 does attribute Killigrew’s portrait to Canini (1651), Altham’s hermit portrait to Salvator Rosa (1665, then Bankes Collection), and Baines’s portrait to Carlo Dolci (1665–1670, Fitzwilliam Museum). The plate-list references 30a, 30b and 31a identify different captions, so they are not a one-to-one key for the three named sitters.", "linked_footnote_statement_ids": ["st-chp7-p197-n2-portrait-attributions"], "mentioned_candidate_ids": ["cand-0973", "cand-1342", "cand-0085", "cand-0162", "cand-4490", "cand-1722", "cand-3397", "cand-4057", "cand-4024", "cand-4026", "cand-7269", "cand-7270"]},
    "st-chp7-p194-cadani-employed-dresden": {"footnote_marker": 1, "linked_footnote_statement_ids": ["st-chp7-p194-n1-lavagnino"]},
    "st-chp7-p194-liechtenstein-letter-subject-discretion": {"footnote_marker": 4, "linked_footnote_statement_ids": ["st-chp7-p194-n4-wilhelm"]},
    "st-chp7-p198-exeter-employs-verrio-burghley": {"footnote_marker": 1, "linked_footnote_statement_ids": ["st-chp7-p198-n1-vertue"]},
}
updated_statement_rows = []
for s in statement_rows:
    if s["statement_id"] in updates:
        s = json.loads(json.dumps(s))
        s["qualifiers"].update(updates[s["statement_id"]])
    updated_statement_rows.append(s)

coverage_rows = list(csv.DictReader(coverage_path.open(encoding="utf-8-sig", newline="")))
coverage_fields = list(coverage_rows[0].keys())
complete_segments = {
    "chp-7:07_CHP-7_sec_iv:l6-21": "p.193 body and all printed-page footnotes 1-3 migrated; note 2 was embedded at source L21 and notes 1 and 3 were migrated from the composite note block.",
    "chp-7:07_CHP-7_sec_iv:l23-36": "p.194 body and all printed-page footnotes 1-4 migrated; note 2 was embedded at source L36 and notes 1, 3, and 4 were migrated from the composite note block.",
    "chp-7:07_CHP-7_sec_iv:l38-46": "p.195 body and notes 1-5 migrated, including Haskell’s ‘Mondane’ comment and cited-source locators.",
    "chp-7:07_CHP-7_sec_iv:l48-61": "p.196 body and notes 1-2 migrated; note 2 was embedded at source L61 and note 1 was migrated from the composite note block.",
    "chp-7:07_CHP-7_sec_iv:l63-75": "p.197 body and notes 1-6 migrated; Ratti’s 1713 date remains in conflict with the body’s 1714 date. The ending clause continues to p.198.",
    "chp-7:07_CHP-7_sec_iv:l77-87": "p.198 body and notes 1-6 migrated; the 1713 choice-of-Hercules cross-reference was checked against the List of Plates.",
    "chp-7:07_CHP-7_sec_iv:l89-95": "p.199 body and note 1 migrated; French OCR corrections were checked against PDF physical page 37.",
}
updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] in complete_segments:
        row.update({"disposition": "reviewed", "migration_status": "complete", "note": complete_segments[row["segment_id"]]})
    if row["segment_id"] == segment_id:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L98-119", "note": "p.193-199 deferred footnotes migrated and cross-linked to body statements; OCR footnote-number and text corrections checked against PDF physical pages 31-37. Quoted works and citation pages are locators, not independent verification."})
    updated_coverage.append(row)

if any(r["segment_id"] in complete_segments and r["migration_status"] != "complete" for r in updated_coverage):
    raise SystemExit("a page segment did not reach complete")
if next(r for r in updated_coverage if r["segment_id"] == segment_id)["migration_status"] != "complete":
    raise SystemExit("composite footnote segment did not reach complete")
for s in statements:
    for linked in s["qualifiers"].get("linked_body_statement_ids", []):
        if linked not in by_id:
            raise SystemExit(f"missing body statement link {linked}")
for sid in updates:
    if sid not in by_id:
        raise SystemExit(f"missing target statement for update {sid}")

backup_suffix = ".bak-s2-chp7-footnotes-20260930"
backups = []
for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + backup_suffix)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    backups.append((path, backup))

preview = {"mode": "dry-run", "segment": segment_id, "new_candidates": len(new_candidates), "new_mentions": len(new_mentions), "new_footnote_statements": len(statements), "updated_body_statements": len(updates), "completed_body_segments": len(complete_segments), "coverage": "footnotes and p.193-199 complete"}
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False))
    raise SystemExit(0)

for path, backup in backups:
    shutil.copy2(path, backup)

def atomic_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    Path(f.name).replace(path)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
updated_statement_rows.extend(statements)
atomic_csv(candidate_path, candidate_fields, candidate_rows)
atomic_csv(mention_path, mention_fields, mention_rows)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statement_path.parent, delete=False, suffix=".tmp") as f:
    for row in updated_statement_rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
Path(f.name).replace(statement_path)
atomic_csv(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
preview["mention_ids"] = [new_mentions[0]["mention_id"], new_mentions[-1]["mention_id"]]
print(json.dumps(preview, ensure_ascii=False))
