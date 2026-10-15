#!/usr/bin/env python3
"""Restore exact entity mention spans for the Chapter 13 merged notes segment."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
SEGMENT = "chp-13:13_CHP-13_intro:l179-251"
BACKUP_SUFFIX = ".bak-s2-ch13-notes-entity-mention-backfill-20261014"
EXPECTED = {
    STATEMENTS: "f1c506986ccf97a39a5ee78050faea5ad15e87b5bdcec8f0c0bc0eb16aaae2ac",
    MENTIONS: "f81cbedd136c14b810133b89c019cf84e5e44fba7ca54e3ba9d1be1c130d6365",
    SOURCE: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validation; default is dry-run")
    args = parser.parse_args()
    for path, expected in EXPECTED.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} sha256={actual}, expected={expected}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_rows = [__import__("json").loads(s) for s in (ROOT / "04-knowledge" / "tables" / "segments.jsonl").read_text(encoding="utf-8").splitlines() if s.strip()]
    bounds = {r["segment_id"]: (int(r["line_start"]), int(r["line_end"])) for r in segment_rows}
    if SEGMENT not in bounds or bounds[SEGMENT] != (179, 251):
        raise SystemExit("Chapter 13 note segment bounds changed")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        mention_rows = list(reader)
    has_bom = MENTIONS.read_bytes().startswith(b"\xef\xbb\xbf")
    if any(row["segment_id"] == SEGMENT for row in mention_rows):
        raise SystemExit("Chapter 13 note segment already has mention rows; inspect before reapplying")

    # (source line, exact source substring, candidate id, review note, occurrence index)
    specs = [
        (180, "Horatio Brown", "cand-10127", "", 0),
        (180, "a general survey of the whole field", "cand-10133", "The note supplies no survey title.", 0),
        (181, "M. Berengo", "cand-8291", "", 0),
        (181, "M. Berengo, 1957, p. 1322", "cand-10134", "Citation locator as printed.", 0),
        (182, "J. G. Goethe", "cand-10128", "", 0),
        (182, "J. G. Goethe, I, p. 38", "cand-10135", "Citation locator as printed.", 0),
        (183, "Berengo", "cand-8291", "", 0),
        (183, "Berengo, 1957", "cand-10136", "Citation locator as printed.", 0),
        (183, "Morazzoni", "cand-10129", "", 0),
        (183, "Morazzoni", "cand-10137", "The cited work is not titled in this note.", 0),
        (183, "Gallo", "cand-8514", "", 0),
        (183, "Gallo, 1948, pp. 153-214", "cand-10138", "Citation locator as printed.", 0),
        (183, "Marin", "cand-10130", "", 0),
        (183, "Marin, Vin, p. 234", "cand-10139", "Preserve the S0 spelling; do not normalize its printed citation here.", 0),
        (183, "Venice", "cand-2719", "", 0),
        (184, "Morazzoni", "cand-10129", "", 0),
        (184, "Morazzoni, p. 70", "cand-10140", "Citation locator as printed.", 0),
        (185, "Roberti", "cand-10131", "", 0),
        (185, "Roberti, 1900, pp. 3 26-3 5", "cand-10141", "Preserve the S0 OCR spacing in this span.", 0),
        (186, "Bettinelli", "cand-0369", "", 0),
        (186, "Lettere inglesi", "cand-10142", "Title fragment as printed.", 0),
        (187, "Morazzoni", "cand-10129", "", 0),
        (187, "Morazzoni, p. 131", "cand-10143", "Citation locator as printed.", 0),
        (188, "the eighth volume of the Bossuet", "cand-9987", "The cited volume is not individually identified.", 0),
        (189, "Battagia", "cand-10132", "", 0),
        (189, "Battagia, p. 76", "cand-10144", "Citation locator as printed.", 0),
        (190, "Novelle della Repubblica delle Lettere", "cand-9988", "", 0),
        (191, "Hazard", "cand-9919", "Author identity remains unresolved.", 0),
        (191, "Hazard, 1946,1, pp. 105-7 and note", "cand-10145", "Citation locator as printed.", 0),
        (192, "the Novelle", "cand-9988", "", 0),
        (192, "St Augustine", "cand-10146", "", 0),
        (192, "a proposed edition of the works of St Augustine", "cand-10147", "The edition was only proposed in the advertisement.", 0),
        (193, "Padre Antonio da Venezia", "cand-10148", "Author form as printed in the book title.", 0),
        (193, "La Chiesa di Gesù Cristo vendicata", "cand-9993", "Title fragment; the cited book was not independently consulted.", 0),
        (193, "Piazzetta", "cand-1907", "", 0),
        (193, "Religion trampling on Heresy", "cand-10149", "", 0),
        (193, "Pitteri", "cand-1948", "", 0),
        (194, "The drawings", "cand-9991", "The drawings are described as an approximate group in the preceding text.", 0),
        (194, "Albrizzi", "cand-0025", "", 0),
        (194, "England", "cand-10151", "", 0),
        (194, "the Royal Library", "cand-10152", "Repository name as printed.", 0),
        (194, "Turin", "cand-2662", "", 0),
        (195, "Hofer", "cand-10153", "Surname-only citation.", 0),
        (195, "Hofer, p. 37", "cand-10154", "The cited work title is not supplied in this note.", 0),
        (196, "These paintings", "cand-9998", "Reference to the Guardi canvases in the preceding text.", 0),
        (196, "Washington", "cand-5523", "City named without a museum identity.", 0),
        (196, "Copenhagen", "cand-9287", "City named without a museum identity.", 0),
        (196, "Hull", "cand-10155", "City named without a museum identity.", 0),
        (196, "London", "cand-1422", "", 0),
        (197, "Morazzoni", "cand-10129", "", 0),
        (197, "Morazzoni", "cand-10137", "The cited work is not titled in this note.", 0),
        (198, "G. A. Moschini", "cand-1709", "", 0),
        (198, "G. A. Moschini, 1809, p. 5", "cand-10156", "Citation locator as printed.", 0),
        (198, "Gradenigo", "cand-8507", "", 0),
        (198, "Gradenigo, p. 71", "cand-10157", "Citation locator as printed.", 0),
        (199, "G. B. Albrizzi", "cand-0025", "", 0),
        (199, "Memorie", "cand-10158", "Title fragment as printed.", 0),
        (200, "G. A. Moschini", "cand-1709", "", 0),
        (200, "G. A. Moschini, 1815,1, p. xv", "cand-10159", "Citation locator as printed.", 0),
        (200, "1806, HI, p. 49", "cand-8511", "Preserve the S0 volume transcription.", 0),
        (200, "1924, p. 82", "cand-9561", "Citation locator; publication identity remains unresolved here.", 0),
        (200, "Albrizzi’s vast collection of prints", "cand-10163", "Collection scope as described by Haskell.", 0),
        (200, "Albrizzi", "cand-0025", "", 0),
        (200, "the catalogue of these", "cand-10161", "The catalogue is reported as untraced.", 0),
        (200, "Pietro Brandolese", "cand-10160", "", 0),
        (201, "Morazzoni", "cand-10129", "", 0),
        (201, "Morazzoni, p. 117", "cand-10162", "Citation locator as printed.", 0),
        (202, "P. E. Gherardi", "cand-1155", "", 0),
        (202, "L. A. Muratori", "cand-1717", "", 0),
        (202, "Letter from P. E. Gherardi to L. A. Muratori of 12 July 1749", "cand-10008", "Letter identified by the note; manuscript not independently consulted.", 0),
        (202, "Biblioteca Estense", "cand-8539", "Repository named in the citation.", 0),
        (202, "Pasquali", "cand-1844", "", 0),
        (202, "Albrizzi", "cand-0025", "", 0),
        (203, "Andrea Memmo", "cand-1643", "", 0),
        (203, "[Andrea Memmo], 1786, p. 45", "cand-10166", "Citation locator as printed.", 0),
        (203, "Lodoli", "cand-1411", "", 0),
        (203, "Conti’s letter to Vico of 1728", "cand-10165", "Letter reference as printed.", 0),
        (203, "Conti", "cand-10164", "Surname-only author reference.", 0),
        (203, "Vico", "cand-2770", "", 0),
        (203, "Fisch", "cand-9953", "Author named in the publication credit.", 0),
        (203, "Bergin", "cand-9954", "Author named in the publication credit.", 0),
        (203, "Fisch and Bergin, p. 184", "cand-9955", "Publication locator as printed.", 0),
        (203, "Pasquali", "cand-1844", "", 0),
        (204, "his letter of 7 January 1785/6 to the Prato bookseller Niccola Mazzoni", "cand-10167", "Letter identified by date and addressee; manuscript not independently consulted.", 0),
        (204, "Prato", "cand-10170", "Place named in the description of Mazzoni.", 0),
        (204, "Niccola Mazzoni", "cand-1603", "", 0),
        (204, "Nuti", "cand-10168", "Surname-only publication credit.", 0),
        (204, "Nuti, 1941, p. 199", "cand-10169", "Citation locator as printed.", 0),
        (204, "La Toscana", "cand-10171", "Region named in the quoted letter.", 0),
        (205, "Archivio di Stato", "cand-10172", "Repository name as printed.", 0),
        (205, "Venice", "cand-2719", "", 0),
        (205, "Inquisitori di Stato", "cand-9739", "", 0),
        (205, "Inquisitori di Stato, 537, p. Z2v, 27 Agosto 1764", "cand-10173", "Archival locator as printed; folio transcription remains as in S0.", 0),
        (206, "Novelle della Repubblica delle Lettere", "cand-9988", "", 0),
        (206, "Novelle della Repubblica delle Lettere, 8 Settembre 1736", "cand-10174", "Issue locator as printed.", 0),
        (207, "Morazzoni", "cand-10129", "", 0),
        (207, "Morazzoni, p. 116", "cand-10175", "Citation locator as printed.", 0),
        (208, "Delle Commedie di Carlo Goldoni avvocato veneto", "cand-10176", "Title as printed; edition details remain source-limited.", 0),
        (208, "Carlo Goldoni", "cand-1205", "", 0),
        (209, "Delle Commedie di Carlo Goldoni avvocato veneto", "cand-10177", "Title as printed; volume II is stated in the note.", 0),
        (209, "Carlo Goldoni", "cand-1205", "", 0),
        (210, "Lettera del Magnifico Signor Antonio Zatta", "cand-10178", "Title fragment as printed.", 0),
        (210, "Antonio Zatta", "cand-2865", "", 0),
        (210, "Fiorenza", "cand-3397", "Printed place form; the note itself corrects the imprint to Venice.", 0),
        (210, "Venice", "cand-3401", "Place supplied by the note's bracketed correction.", 0),
        (210, "Lettera Giustificativa di Antonio Zatta", "cand-10179", "Title as printed.", 0),
        (210, "Antonio Zatta", "cand-2865", "Second occurrence in the title of the 1761 letter.", 1),
        (210, "Venezia", "cand-3401", "Printed Italian place form for Venice.", 0),
        (210, "Jesuits", "cand-1321", "", 0),
        (211, "Archi vio di Stato, Venice", "cand-10180", "Preserve the S0 OCR spacing in the repository name.", 0),
        (211, "Inquisitori di Stato, 535", "cand-10180", "First archival register locator.", 0),
        (211, "Archi vio di Stato, Venice", "cand-10181", "Preserve the S0 OCR spacing in the repository name.", 0),
        (211, "Inquisitori di Stato", "cand-9739", "", 0),
        (211, "536, p. 4IV", "cand-10181", "Second archival register locator; preserve the S0 transcription.", 0),
        (211, "Venice", "cand-3401", "", 0),
        (213, "terziario, a quel die pare, dei Gesuiti", "cand-1321", "Quoted Jesuit affiliation; the quote remains qualified.", 0),
        (213, "Giovanni de Cattaneo", "cand-0610", "", 0),
        (213, "Zatta", "cand-2865", "", 0),
        (213, "le fameux Zatta", "cand-2865", "Quoted characterization in French.", 0),
        (213, "Nouvelles Ecclésiastiques", "cand-10182", "Periodical title as printed.", 0),
        (213, "Neri, 1899, pp. 109 and 114", "cand-10183", "Citation locator as printed.", 0),
        (214, "Lettera del Magnifico Signor Antonio Zatta", "cand-10178", "Cross-reference to the cited title.", 0),
        (214, "Antonio Zatta", "cand-2865", "", 0),
        (215, "Catalogo di Libri latini c italiani", "cand-10184", "Title begins with the S0 OCR reading; preserve it.", 0),
        (215, "Antonio Zatta", "cand-2865", "", 0),
        (215, "Venezia", "cand-3401", "Printed Italian place form for Venice.", 0),
        (215, "G. da Venezia, 1934, pp. 25-34", "cand-10185", "Citation locator as printed.", 0),
        (216, "Catalogo di quadri raccolti dal fu Signor Maffeo Pinelli", "cand-10186", "Title fragment as printed.", 0),
        (216, "Maffeo Pinelli", "cand-1932", "", 0),
        (216, "Venezia", "cand-3401", "Printed Italian place form for Venice.", 0),
        (216, "G. A. Moschini, 1806, II, p. 64", "cand-10187", "Citation locator as printed.", 0),
        (217, "Morelli, V, p. 348", "cand-10188", "Citation locator as printed.", 0),
        (218, "Bercngo, 1957", "cand-10136", "Preserve the S0 spelling; the citation's author identity remains subject to source-image review.", 0),
        (218, "Mostra dei Remondini, 1958", "cand-10189", "Exhibition catalogue citation as printed.", 0),
        (218, "Remondini", "cand-2123", "", 0),
        (219, "seven letters from Pietro Longhi to Remondini between 1748 and 1752", "cand-10190", "Letter group described in the note; publication reference is truncated after 'A.'.", 0),
        (219, "Pietro Longhi", "cand-1429", "", 0),
        (219, "Remondini", "cand-2123", "", 0),
        (220, "G. A. Moschini", "cand-1709", "", 0),
        (220, "G. A. Moschini, 1924, p. 132", "cand-10191", "Citation locator as printed.", 0),
        (221, "Gallo", "cand-8514", "", 0),
        (221, "Gallo, 1948, p. 184", "cand-10138", "Citation locator as printed.", 0),
        (221, "G. A. Moschini", "cand-1709", "", 0),
        (221, "G. A. Moschini, 1924, p. 132", "cand-10191", "Citation locator as printed.", 0),
        (222, "Gallo", "cand-8514", "", 0),
        (222, "Gallo, 1948, pp. 158 and 186", "cand-10138", "Citation locator as printed.", 0),
        (223, "G. Lorenzetti", "cand-9947", "", 0),
        (223, "G. Lorenzetti, 1917", "cand-10192", "Citation locator as printed.", 0),
        (223, "F. Borroni", "cand-10193", "Short-form reference; title and date are not supplied.", 0),
        (224, "Marco Ricci", "cand-2149", "", 0),
        (224, "six pictures for Zanetti", "cand-10194", "Source-defined group of works.", 0),
        (224, "Zanetti", "cand-2838", "", 0),
        (224, "Bottari, II, pp. 128-30", "cand-7516", "Publication locator as printed.", 0),
        (224, "Bottari", "cand-0417", "", 0),
        (224, "Federico Correr", "cand-10195", "", 0),
        (224, "Lorenzetti, 1917, p. 138", "cand-10192", "Citation locator as printed.", 0),
        (225, "Mariette", "cand-1547", "", 0),
        (225, "Ahecedario", "cand-10196", "Preserve the S0 title spelling.", 0),
        (225, "Zanetti", "cand-2838", "", 0),
        (225, "Zanetti", "cand-2838", "Second mention in this note line.", 1),
        (225, "a pastel by Rosalba", "cand-10197", "Work is not further identified in the note.", 0),
        (225, "Rosalba", "cand-0581", "", 0),
        (225, "Lorenzetti, 1917, p. 145", "cand-10192", "Citation locator as printed.", 0),
        (225, "Lorenzetti, 1917, p. 145", "cand-9947", "Author reference in the citation.", 0),
        (225, "his will", "cand-10198", "Document identified contextually by the note.", 0),
        (226, "Biblioteca Marciana", "cand-9448", "Repository named in the archival locator.", 0),
        (226, "MSS. Italiani—Cl. XI, Cod. CXVI, 7356", "cand-10199", "Manuscript shelfmark as printed.", 0),
        (226, "Venice", "cand-2719", "", 0),
        (226, "A. M. Zanetti", "cand-2838", "", 0),
        (226, "Prince of Liechtenstein", "cand-10202", "Correspondent named in the note.", 0),
        (226, "Count Tessin", "cand-2554", "", 0),
        (226, "Marshal Schulenburg", "cand-2401", "", 0),
        (226, "receipt, dated 10 August 1736 in Vienna", "cand-10200", "Receipt as described by Haskell; document not consulted.", 0),
        (226, "Anne Marie de Savoye", "cand-2381", "", 0),
        (226, "Vienna", "cand-2772", "", 0),
        (226, "un Poussin", "cand-10069", "Unidentified Poussin picture described in the receipt.", 0),
        (226, "Castiglione Benedetto", "cand-10070", "Work attributed in the quoted receipt; no title supplied.", 0),
        (226, "fifteen gems and cameos", "cand-10204", "Group of objects recorded in the receipt.", 0),
        (226, "Memorie de gl’acquisti fatti da me Antonio Mra Zanetti", "cand-10201", "Title fragment follows S0 transcription; the manuscript was not consulted.", 0),
        (226, "lo Spagnolo di Bologna", "cand-10203", "Painter designation as quoted; identity not inferred here.", 0),
        (226, "Bologna", "cand-3398", "", 0),
        (227, "Biblioteca Marciana", "cand-9448", "Repository repeated in the note.", 0),
        (227, "MSS. Italiani—Cl. XI, Cod. CXVI, 7356", "cand-10199", "Manuscript shelfmark repeated in the note.", 0),
        (227, "seven letters from Tessin", "cand-10205", "Letter group described by Haskell; manuscripts not consulted.", 0),
        (227, "Tessin", "cand-2554", "", 0),
        (227, "Vienna", "cand-2772", "", 0),
        (227, "Strahlsund", "cand-10213", "Preserve the place spelling as printed.", 0),
        (228, "Stockholm", "cand-4790", "Continuation of the letter-date list.", 0),
        (228, "Copenhagen", "cand-9287", "Continuation of the letter-date list; retain the printed date discrepancy.", 0),
        (229, "first and third letters", "cand-10205", "Cross-reference within the cited letter group.", 0),
        (229, "the painter", "cand-10077", "Unidentified painter; the note explicitly says the identity is unknown.", 0),
        (230, "third letter", "cand-10205", "Cross-reference within the cited letter group.", 0),
        (230, "Tiepolo", "cand-2569", "", 0),
        (232, "Lorenzetti, 1917, p. 75", "cand-10192", "Citation locator as printed.", 0),
        (232, "Lorenzetti", "cand-9947", "", 0),
        (232, "Bottari", "cand-0417", "", 0),
        (232, "Bottari, II, pp. 129 and 179 ff.", "cand-7516", "Publication locator as printed.", 0),
        (232, "Zanetti’s", "cand-2838", "Possessive reference to the elder Zanetti.", 0),
        (232, "Sebastiano Riccis", "cand-2154", "Plural reference to the paintings by Ricci.", 0),
        (232, "Esther and Ahasuerus", "cand-2163", "Painting title; keep distinct from Monaco's engraving candidate.", 0),
        (232, "Esther and Ahasuerus", "cand-10207", "Work and engraving are distinguished in separate candidates.", 0),
        (232, "The Presentation in the Temple", "cand-2175", "Painting title; keep distinct from Monaco's engraving candidate.", 0),
        (232, "The Presentation in the Temple", "cand-10208", "Work and engraving are distinguished in separate candidates.", 0),
        (232, "Pietro Monaco", "cand-1682", "", 0),
        (232, "Raccolta di Opere scelte", "cand-10206", "Publication title as printed; edition not independently consulted.", 0),
        (232, "Rosalba Carriera", "cand-0581", "", 0),
        (232, "portrait of Zanetti by Rosalba Carriera", "cand-10209", "Portrait not further identified in the note.", 0),
        (232, "Dactyliotheca", "cand-10012", "Title as printed.", 0),
        (233, "Biblioteca Marucelliana", "cand-9493", "Repository named in the archival locator.", 0),
        (233, "Florence", "cand-3397", "", 0),
        (233, "Letter to A. F. Gori of 22 December 1752", "cand-10210", "Letter identified by date and addressee; manuscript not consulted.", 0),
        (233, "A. F. Gori", "cand-1214", "", 0),
        (234, "tazza d’Annibale", "cand-10090", "Source-language object phrase; its ownership is not stated by this note.", 0),
        (234, "Annibale", "cand-0576", "", 0),
        (234, "Baccanale", "cand-10090", "Subject named in the quoted Italian phrase.", 0),
        (234, "Kurz", "cand-10211", "Full author identity remains unresolved here.", 0),
        (234, "Kurz, 1955, pp. 282-7", "cand-10212", "Article locator as printed.", 0),
        (235, "Lorenzetti", "cand-9947", "", 0),
        (235, "Lorenzetti, 1917, p. 122", "cand-10192", "Citation locator as printed.", 0),
        (236, "Varie Pitture a Fresco de'Principali Maestri Veneziani", "cand-10117", "Title as transcribed in S0; do not normalize the spacing here.", 0),
        (237, "Mariette", "cand-1547", "", 0),
        (237, "Crozat", "cand-0894", "", 0),
        (237, "Vleughels", "cand-2789", "", 0),
        (237, "Duke of Devonshire", "cand-0918", "", 0),
        (237, "Sir Andrew Fountaine", "cand-1060", "", 0),
        (237, "Dr Richard Mead", "cand-10214", "Identity remains pending.", 0),
        (237, "Joseph Smith", "cand-2442", "", 0),
        (237, "Rosalba Carriera", "cand-0581", "", 0),
        (237, "Zaccaria Sagredo", "cand-2329", "", 0),
        (238, "Lorenzetti, 1917, p. 55", "cand-10192", "Citation locator as printed.", 0),
        (238, "Lorenzetti", "cand-9947", "", 0),
        (239, "Borroni, p. 28", "cand-10193", "Citation locator as printed; title and date unspecified.", 0),
        (240, "P. Clement, p. 124", "cand-10217", "Citation locator as printed; cited title is not supplied.", 0),
        (240, "P. Clement", "cand-0789", "", 0),
        (240, "John Northall", "cand-10215", "", 0),
        (240, "John Northall wrote (p. 43 8)", "cand-10216", "The note supplies author and page only; title is not given.", 0),
        (240, "Signor Lanetti’s [sic]", "cand-2838", "Printed misidentification as transcribed; contextual identity remains source-limited.", 0),
        (240, "fine collection of pictures and drawings", "cand-11495", "Collection described by the quoted source; scope remains unresolved.", 0),
        (241, "Bottari", "cand-0417", "", 0),
        (241, "Bottari, II, pp. 129-30", "cand-6200", "Publication locator as printed.", 0),
        (242, "Blunt", "cand-0379", "", 0),
        (242, "Croft-Murray", "cand-9339", "Identity remains unresolved in this citation.", 0),
        (242, "Blunt and Croft-Murray, p. 146", "cand-9340", "Citation locator as printed.", 0),
        (243, "Rosalba’s diary", "cand-0581", "", 0),
        (243, "Vianello", "cand-2764", "", 0),
        (243, "Lorenzetti, 1917, p. 12", "cand-10192", "Citation locator as printed.", 0),
        (243, "Lorenzetti", "cand-9947", "", 0),
        (244, "G. A. Moschini", "cand-1709", "", 0),
        (244, "G. A. Moschini, 1806, III, p. 92", "cand-8511", "Citation locator as printed.", 0),
        (245, "Battistella", "cand-8815", "", 0),
        (245, "Battistella, 1930, pp. 60 ff.", "cand-8815", "Citation locator as printed; the cited work title is not supplied here.", 0),
        (246, "Biblioteca Marucelliana", "cand-9493", "Repository named in the archival locator.", 0),
        (246, "Florence", "cand-3397", "", 0),
        (246, "Letter of 26 August 1752 to A. F. Gori", "cand-10218", "Letter identified by date and addressee; manuscript not independently consulted.", 0),
        (246, "A. F. Gori", "cand-1214", "", 0),
        (249, "Raccolta Ji centododici stampe", "cand-10219", "Preserve the S0 title reading; edition alignment remains unresolved.", 0),
        (249, "Pietro Monaco", "cand-1682", "", 0),
        (250, "Letter of 4 February 1763/4", "cand-10119", "Letter locator as printed; author not stated in this line.", 0),
        (250, "British Museum", "cand-5986", "Repository named in the citation.", 0),
        (251, "Toni", "cand-2640", "", 0),
        (251, "G. A. Moschini", "cand-1709", "", 0),
        (251, "G. A. Moschini, 1924, p. 167", "cand-10220", "Citation locator as printed.", 0),
        (251, "manuscript life by the artist P. A. Novelli", "cand-10221", "Manuscript described by Haskell; not independently consulted.", 0),
        (251, "P. A. Novelli", "cand-1760", "", 0),
        (251, "Seminario Patriarcale", "cand-6589", "Repository named in the citation.", 0),
        (251, "Venice", "cand-2719", "", 0),
    ]

    statement_rows = [line for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    import json
    note_statements = [json.loads(line) for line in statement_rows if json.loads(line).get("segment_id") == SEGMENT]
    if len(note_statements) != 102:
        raise SystemExit(f"expected 102 note statements, found {len(note_statements)}")
    candidate_rows = {row["candidate_id"] for row in csv.DictReader((ROOT / "04-knowledge" / "tables" / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))}

    start_line, end_line = bounds[SEGMENT]
    segment_text = "\n".join(source_lines[start_line - 1:end_line])
    new_rows: list[dict] = []
    for number, (line_number, phrase, candidate_id, note, occurrence) in enumerate(specs, start=1):
        if candidate_id not in candidate_rows:
            raise SystemExit(f"candidate not in registry: {candidate_id} for {phrase!r}")
        if not start_line <= line_number <= end_line:
            raise SystemExit(f"line outside segment: L{line_number}")
        source_line = source_lines[line_number - 1]
        positions: list[int] = []
        pos = 0
        while True:
            found = source_line.find(phrase, pos)
            if found < 0:
                break
            positions.append(found)
            pos = found + 1
        if occurrence >= len(positions):
            raise SystemExit(f"phrase missing at L{line_number}: {phrase!r}; found={len(positions)}")
        offset = sum(len(source_lines[i - 1]) + 1 for i in range(start_line, line_number))
        start_char = offset + positions[occurrence]
        new_rows.append({
            "mention_id": f"m-s2-ch13-notes-20261014-{number:03d}",
            "segment_id": SEGMENT,
            "candidate_id": candidate_id,
            "surface_form": phrase,
            "start_char": str(start_char),
            "end_char": str(start_char + len(phrase)),
            "note": note,
        })

    ids = {row["mention_id"] for row in mention_rows}
    proposed_ids = [row["mention_id"] for row in new_rows]
    if len(set(proposed_ids)) != len(proposed_ids) or ids.intersection(proposed_ids):
        raise SystemExit("mention IDs collide")
    for row in new_rows:
        a, b = int(row["start_char"]), int(row["end_char"])
        if segment_text[a:b] != row["surface_form"]:
            raise SystemExit(f"offset check failed: {row['mention_id']}")

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(mention_rows + new_rows)
    payload = output.getvalue().encode("utf-8")
    if has_bom:
        payload = b"\xef\xbb\xbf" + payload
    print(f"mode={'APPLY' if args.apply else 'DRY-RUN'}; note statements={len(note_statements)}; exact mentions to add={len(new_rows)}")
    print(f"projected mentions hash={hashlib.sha256(payload).hexdigest()}; all offsets match S0")
    if not args.apply:
        return

    backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(MENTIONS, backup)
    try:
        MENTIONS.write_bytes(payload)
    except Exception:
        shutil.copy2(backup, MENTIONS)
        raise
    print(f"backup={backup.name}; written hash={sha(MENTIONS)}")


if __name__ == "__main__":
    main()
